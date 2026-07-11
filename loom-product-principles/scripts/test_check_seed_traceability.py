"""Tests for check_seed_traceability.py — the oracle parser (Task 1) and the
artifact checks + CLI (Task 2) for the Level-2 mechanical traceability gate
(brief §Level 2, docs/loom/specs/2026-07-10-principles-replay-loop.md).

Synthetic content only. Fixtures built INLINE (flat-folder rule: no
fixtures/ subdir, no conftest.py — same convention as
test_validate_principles_output.py).
"""

import re
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


@pytest.mark.parametrize("bad_token", ["a||b", "|b", "a|", "a|  |b", "|"])
def test_malformed_pipe_alternative_raises_value_error(bad_token):
    # Empty alternatives (leading/trailing `|`, or `||`) are a parse error —
    # contract precision, not a matching edge case.
    text = f"named_anchors: {bad_token}\n"
    with pytest.raises(ValueError):
        parse_oracle(text)


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


def test_missing_artifact_file_exits_2_with_clean_error(tmp_path):
    missing_artifact = tmp_path / "does-not-exist.md"
    oracle = tmp_path / "oracle.md"
    oracle.write_text(_oracle(), encoding="utf-8")
    proc = _run_cli(missing_artifact, oracle)
    assert proc.returncode == 2
    assert "Traceback" not in proc.stderr
    assert f"error: file not found: {missing_artifact}" in proc.stderr


def test_missing_oracle_file_exits_2_with_clean_error(tmp_path):
    artifact = tmp_path / "PRINCIPLES.md"
    artifact.write_text(_artifact(), encoding="utf-8")
    missing_oracle = tmp_path / "does-not-exist-oracle.md"
    proc = _run_cli(artifact, missing_oracle)
    assert proc.returncode == 2
    assert "Traceback" not in proc.stderr
    assert f"error: file not found: {missing_oracle}" in proc.stderr


def test_check_public_api_returns_miss_lines_without_subprocess():
    # Public API (brief: "so tests and future consumers can call without
    # subprocess").
    artifact = _artifact(anchor_row=None)
    oracle = _oracle()
    misses = check(artifact, oracle)
    assert misses == ["named_anchors: HEART"]


# --- Task 1 (plan 2026-07-11): `|` OR-alternatives ---------------------------


def test_pipe_alternatives_match_any_form():
    # RED: a `JTBD|Jobs-to-be-Done` anchor item must pass when the artifact's
    # Anchors row carries only the long form.
    artifact = _artifact(anchor_row="| Jobs-to-be-Done | usability framework |")
    oracle = _oracle(named="JTBD|Jobs-to-be-Done")
    assert check(artifact, oracle) == []


def test_pipe_alternatives_match_any_form_deferred_items():
    artifact = _artifact(
        open_question="1. Reversibility posture unclear — re-trigger: revisit later\n"
    )
    oracle = _oracle(deferred="可逆性|Reversibility posture")
    assert check(artifact, oracle) == []


def test_pipe_alternatives_negative_violated_by_any_alternative():
    # A negative item is violated if ANY alternative is present, even if the
    # oracle's first-listed alternative is absent.
    artifact = _artifact(extra_negative="We considered an API gateway here.")
    oracle = _oracle(negative="mock server|API gateway")
    assert check(artifact, oracle) == ["negative: mock server|API gateway"]


def test_pipe_alternatives_miss_line_echoes_full_item_when_no_alternative_matches():
    artifact = _artifact(anchor_row=None)
    oracle = _oracle(named="JTBD|Jobs-to-be-Done")
    assert check(artifact, oracle) == ["named_anchors: JTBD|Jobs-to-be-Done"]


# --- Calibration round-2: negation-superstring characterization -------------


def test_negative_token_fires_on_its_own_rejection_sentence_characterization():
    # CHARACTERIZATION (not a bug): `check_negative` cannot distinguish a
    # bait item being ACCEPTED from the artifact correctly REJECTING it — a
    # negative token is a substring of its own natural-language rejection
    # ("不支援企業版多店管理" contains "支援企業版"). This is WHY the three
    # bait-leak tokens (mock server support / API gateway support / 支援企業版)
    # were demoted out of `negative:` to grader-side `# note:` prose in the
    # oracle calibration round-2 fix — no acceptance-phrase choice escapes
    # this under substring semantics.
    artifact = _artifact(
        extra_negative="不支援企業版多店管理，功能優化針對單一店家。"
    )
    oracle = _oracle(negative="支援企業版")
    assert check(artifact, oracle) == ["negative: 支援企業版"]


# --- Task 3: committed oracles conform to the parser contract ---------------

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SEED_CORPUS = _REPO_ROOT / "docs/loom/dogfood/2026-07-10-principles-flow-seed-corpus"
_COLD_OPERATOR_SEED = (
    _REPO_ROOT
    / "docs/loom/dogfood/2026-07-10-principles-flow-cold-operator"
    / "seed.md"
)

# (label, path, expected named_anchors count, deferred_items count, negative
# count, exemplars) — exemplars is a dict of {key: one stable token expected
# in that key's list}, one entry per NON-EMPTY key for that source. These
# pin actual extracted content (not just counts), so prose-glue regressions
# that happen to preserve counts (e.g. seed3's old pre-normalization glued
# token) still fail. See git show 0726d823^ for the pre-normalization seed3
# oracle: its glued token
# "Nielsen's 10 Usability Heuristics (MIXED-TRADITION TRAP: ...)" would trip
# the shape assertion below.
_COMMITTED_ORACLE_EXPECTATIONS = [
    ("seed1-oracle.md", _SEED_CORPUS / "seed1-oracle.md", 12, 0, 3, {
        "named_anchors": "Nielsen's 10 Usability Heuristics",
        "negative": "postmortem 撰寫",
    }),
    ("seed2-oracle.md", _SEED_CORPUS / "seed2-oracle.md", 8, 2, 5, {
        "named_anchors": "Calm Technology",
        "deferred_items": "可逆性|Reversibility posture",
        "negative": "上傳雲端",
    }),
    ("seed3-oracle.md", _SEED_CORPUS / "seed3-oracle.md", 6, 0, 0, {
        "named_anchors": "Nielsen's 10 Usability Heuristics",
    }),
    ("seed4-oracle.md", _SEED_CORPUS / "seed4-oracle.md", 10, 1, 4, {
        "named_anchors": "Norman's Design Principles",
        "deferred_items": "升級胃口|Upgrade appetite",
        "negative": "強制雲端備份",
    }),
    ("seed5-oracle.md", _SEED_CORPUS / "seed5-oracle.md", 8, 2, 0, {
        "named_anchors": "WCAG",
        "deferred_items": "預約記錄保留期",
    }),
    ("cold-operator seed.md", _COLD_OPERATOR_SEED, 9, 1, 8, {
        "named_anchors": "JTBD|Jobs-to-be-Done",
        "deferred_items": "成本|Cost posture",
        "negative": "零雲端依賴",
    }),
]

# Shape assertion: a token that still carries prose-glue TRAP-style
# annotation (e.g. "(MIXED-TRADITION TRAP: ...)"), the literal substring
# "MUST appear", or a descriptive " stack"/" format" suffix (e.g. "C++/Qt
# stack", "SVG format") is evidence the oracle text wasn't normalized into a
# clean `;`-separated token list — the parser would be pinning prose, not a
# stable token fragment. Checked per `|` alternative so a class-B pair can't
# hide a glued alternative.
_TRAP_ANNOTATION_RE = re.compile(r"\([A-Z]{2,}")
_GLUED_SUFFIXES = (" stack", " format")


def _is_prose_glued(token: str) -> bool:
    for alt in token.split("|"):
        alt = alt.strip()
        if _TRAP_ANNOTATION_RE.search(alt) or "MUST appear" in alt:
            return True
        if alt.endswith(_GLUED_SUFFIXES):
            return True
    return False


@pytest.mark.parametrize(
    "label,path,named_count,deferred_count,negative_count,exemplars",
    _COMMITTED_ORACLE_EXPECTATIONS,
)
def test_committed_oracles_conform_to_parser_contract(
    label, path, named_count, deferred_count, negative_count, exemplars
):
    text = path.read_text(encoding="utf-8")
    result = parse_oracle(text)  # raises ValueError if the source can't parse
    assert result["named_anchors"], f"{label}: named_anchors must be non-empty"
    assert len(result["named_anchors"]) == named_count, label
    assert len(result["deferred_items"]) == deferred_count, label
    assert len(result["negative"]) == negative_count, label

    for key, exemplar in exemplars.items():
        assert exemplar in result[key], (
            f"{label}: expected exemplar {exemplar!r} in {key}, got {result[key]}"
        )

    for key in ("named_anchors", "deferred_items", "negative"):
        glued = [t for t in result[key] if _is_prose_glued(t)]
        assert not glued, f"{label}: prose-glued token(s) in {key}: {glued}"
