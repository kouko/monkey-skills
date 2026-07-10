"""Tests for check_seed_traceability.py — the oracle parser (Task 1) and the
artifact checks + CLI (Task 2) for the Level-2 mechanical traceability gate
(brief §Level 2, docs/loom/specs/2026-07-10-principles-replay-loop.md).

Synthetic content only. Fixtures built INLINE (flat-folder rule: no
fixtures/ subdir, no conftest.py — same convention as
test_validate_principles_output.py).
"""

import subprocess
import sys
from pathlib import Path

import pytest

from check_seed_traceability import check, parse_oracle


def test_parse_oracle_extracts_three_token_lists():
    text = (
        "named_anchors: HEART; MoSCoW; Nielsen's 10 Usability Heuristics\n"
        "deferred_items: upgrade appetite unclear (single deferred item)\n"
        "negative: \"forced login\" as accepted behavior\n"
    )
    result = parse_oracle(text)
    assert result == {
        "named_anchors": ["HEART", "MoSCoW", "Nielsen's 10 Usability Heuristics"],
        "deferred_items": ["upgrade appetite unclear (single deferred item)"],
        "negative": ['"forced login" as accepted behavior'],
    }


def test_none_in_this_seed_sentinel_parses_to_empty_list():
    # Sentinel may carry trailing parenthetical commentary (seed1-oracle.md
    # shape: "none in this seed (2-deferred trap lives in seed 2)").
    text = (
        "named_anchors: HEART\n"
        "deferred_items: none in this seed (2-deferred trap lives in seed 2)\n"
        "negative: none in this seed\n"
    )
    result = parse_oracle(text)
    assert result["deferred_items"] == []
    assert result["negative"] == []


def test_absent_key_parses_to_empty_list():
    text = "named_anchors: HEART; MoSCoW\n"
    result = parse_oracle(text)
    assert result["deferred_items"] == []
    assert result["negative"] == []


def test_ignores_stances_and_out_of_jurisdiction_bait_keys():
    # Out of checker scope by design (brief §Level 2) — must not leak into
    # the returned dict, and must not be mistaken for one of the three keys.
    text = (
        "named_anchors: HEART\n"
        "out_of_jurisdiction_bait: some timeline text; another bait\n"
        "stances: task=x; user=y\n"
    )
    result = parse_oracle(text)
    assert set(result.keys()) == {"named_anchors", "deferred_items", "negative"}
    assert result["named_anchors"] == ["HEART"]


def test_missing_all_three_keys_raises_value_error_naming_them():
    text = "stances: task=x\nout_of_jurisdiction_bait: y\n"
    with pytest.raises(ValueError) as exc_info:
        parse_oracle(text)
    message = str(exc_info.value)
    assert "named_anchors" in message
    assert "deferred_items" in message
    assert "negative" in message


def test_multi_token_values_are_stripped_of_surrounding_whitespace():
    text = "named_anchors:   HEART ;  MoSCoW  ;IBM Carbon\n"
    result = parse_oracle(text)
    assert result["named_anchors"] == ["HEART", "MoSCoW", "IBM Carbon"]


# --- Task 2: artifact checks + CLI ------------------------------------------

SCRIPT = Path(__file__).with_name("check_seed_traceability.py")


def _artifact(
    anchor_row: str | None = "| HEART | HEART framework, 2010 |",
    open_question: str | None = "1. Whether X — re-trigger: revisit when Y ships\n",
    extra_negative: str = "",
) -> str:
    """A minimal PRINCIPLES.md-shaped artifact. `anchor_row=None` omits the
    `## Anchors` section entirely; `open_question=None` omits `## Open
    Questions` entirely. `extra_negative` is appended as trailing prose."""
    parts = ["# PRINCIPLES\n\n## North Star\n\nGoal.\n\n"]
    if anchor_row is not None:
        parts.append(
            "## Anchors\n\n"
            "| Canon | Pinned version/edition |\n"
            "| --- | --- |\n"
            f"{anchor_row}\n\n"
        )
    if open_question is not None:
        parts.append(f"## Open Questions\n\n{open_question}\n")
    if extra_negative:
        parts.append(f"{extra_negative}\n")
    return "".join(parts)


def _oracle(named="HEART", deferred="Whether X", negative="forced login") -> str:
    return f"named_anchors: {named}\ndeferred_items: {deferred}\nnegative: {negative}\n"


def _run_cli(artifact_path: Path, oracle_path: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(artifact_path), str(oracle_path)],
        capture_output=True, text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": ""},
    )


def test_conformant_artifact_exits_0_no_output(tmp_path):
    artifact = tmp_path / "PRINCIPLES.md"
    artifact.write_text(_artifact(), encoding="utf-8")
    oracle = tmp_path / "oracle.md"
    oracle.write_text(_oracle(), encoding="utf-8")
    proc = _run_cli(artifact, oracle)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert proc.stdout == ""
    assert proc.stderr == ""


def test_missing_named_anchor_exits_1_naming_the_miss(tmp_path):
    # RED test: `main` is not implemented yet.
    artifact = tmp_path / "PRINCIPLES.md"
    artifact.write_text(_artifact(anchor_row=None), encoding="utf-8")
    oracle = tmp_path / "oracle.md"
    oracle.write_text(_oracle(), encoding="utf-8")
    proc = _run_cli(artifact, oracle)
    assert proc.returncode == 1
    assert "named_anchors: HEART" in proc.stderr


def test_named_anchor_row_with_empty_version_cell_treated_as_missing(tmp_path):
    artifact = tmp_path / "PRINCIPLES.md"
    artifact.write_text(_artifact(anchor_row="| HEART |  |"), encoding="utf-8")
    oracle = tmp_path / "oracle.md"
    oracle.write_text(_oracle(), encoding="utf-8")
    proc = _run_cli(artifact, oracle)
    assert proc.returncode == 1
    assert "named_anchors: HEART" in proc.stderr


def test_missing_open_questions_retrigger_exits_1_naming_the_miss(tmp_path):
    artifact = tmp_path / "PRINCIPLES.md"
    artifact.write_text(
        _artifact(open_question="1. Whether X, no marker at all.\n"),
        encoding="utf-8",
    )
    oracle = tmp_path / "oracle.md"
    oracle.write_text(_oracle(), encoding="utf-8")
    proc = _run_cli(artifact, oracle)
    assert proc.returncode == 1
    assert "deferred_items: Whether X" in proc.stderr


def test_negative_token_present_exits_1_naming_the_miss(tmp_path):
    artifact = tmp_path / "PRINCIPLES.md"
    artifact.write_text(
        _artifact(extra_negative="Note: forced login is accepted here."),
        encoding="utf-8",
    )
    oracle = tmp_path / "oracle.md"
    oracle.write_text(_oracle(), encoding="utf-8")
    proc = _run_cli(artifact, oracle)
    assert proc.returncode == 1
    assert "negative: forced login" in proc.stderr


def test_all_three_miss_classes_reported_together(tmp_path):
    artifact = tmp_path / "PRINCIPLES.md"
    artifact.write_text(
        _artifact(
            anchor_row=None,
            open_question="1. Whether X, no marker.\n",
            extra_negative="forced login is fine here.",
        ),
        encoding="utf-8",
    )
    oracle = tmp_path / "oracle.md"
    oracle.write_text(_oracle(), encoding="utf-8")
    proc = _run_cli(artifact, oracle)
    assert proc.returncode == 1
    lines = proc.stderr.strip().splitlines()
    assert len(lines) == 3, proc.stderr
    assert "named_anchors: HEART" in proc.stderr
    assert "deferred_items: Whether X" in proc.stderr
    assert "negative: forced login" in proc.stderr


def test_check_public_api_returns_miss_lines_without_subprocess():
    # Public API (brief: "so tests and future consumers can call without
    # subprocess").
    artifact = _artifact(anchor_row=None)
    oracle = _oracle()
    misses = check(artifact, oracle)
    assert misses == ["named_anchors: HEART"]
