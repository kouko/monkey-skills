"""test_report.py — tests for report.py (Stage 5c advisory dispatch-payload generator).

v0.5 architecture: report.py emits a JSON dispatch payload to stdout; the
Claude Code orchestrator dispatches the Sonnet 4.6 advisory-analyst
subagent and writes the returned markdown to ``output_path``. All
heuristic clustering + rendering moved out of report.py into the
subagent prompt (see ``agents/prompt-advisory-analyst.md``).

Tests:
- ``parse_merged_json`` structural correctness (inline + real fixture).
- ``build_dispatch_payload`` schema parity with main.py Stage 3 pattern.
- ``main`` CLI argparse contract: mandatory ``--lang``, valid choices,
  stdout payload shape.
- ``test_heuristic_functions_removed`` — v0.5 T3 refactor invariant.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from report import (
    build_dispatch_payload,
    main,
    parse_merged_json,
)

_SCRIPTS_DIR = Path(__file__).parent
_FIXTURE_PATH = _SCRIPTS_DIR / "fixture_report_merged.json"


# ---------------------------------------------------------------------------
# Helpers.
# ---------------------------------------------------------------------------


def _mk_entry(
    session_id: str,
    target_skill_path: str,
    items: list[dict],
    *,
    kind: str = "failure",
    trajectory_id: str = "traj-1",
) -> dict:
    """Build a minimal merged.json entry."""
    return {
        "session_id": session_id,
        "trajectory_id": trajectory_id,
        "kind": kind,
        "target_skill_path": target_skill_path,
        "memory_items": items,
    }


def _mk_item(title: str, *, description: str = "desc", content: str = "content") -> dict:
    """Build a minimal Memory Item dict."""
    return {
        "title": title,
        "description": description,
        "content": content,
        "kind": "failure",
        "section_anchor": "Examples",
        "requires_new_reference_file": False,
    }


# ---------------------------------------------------------------------------
# parse_merged_json — structural correctness.
# ---------------------------------------------------------------------------


def test_parse_merged_json_returns_expected_structure(tmp_path: Path) -> None:
    """parse_merged_json reads a JSON file and returns a list of dicts.

    Uses a small inline fixture to avoid dependency on the real fixture file
    existing at test time (fixture is bundled in same commit, but test must
    be runnable before it).
    """
    data = [
        _mk_entry(
            "s1",
            "/path/SKILL.md",
            [_mk_item("Title A"), _mk_item("Title B")],
        ),
        _mk_entry(
            "s2",
            "/path2/SKILL.md",
            [_mk_item("Title C")],
        ),
    ]
    fixture = tmp_path / "test_merged.json"
    fixture.write_text(json.dumps(data), encoding="utf-8")

    result = parse_merged_json(str(fixture))

    assert isinstance(result, list), "parse_merged_json must return a list"
    assert len(result) == 2, f"expected 2 entries, got {len(result)}"
    # Each entry has expected keys
    entry = result[0]
    assert "session_id" in entry
    assert "memory_items" in entry
    assert isinstance(entry["memory_items"], list)


def test_parse_merged_json_real_fixture() -> None:
    """parse_merged_json on the real bundled snapshot fixture.

    Verifies: 11 entries, ≥30 total Memory Items, 4 distinct target skills.
    The fixture is bundled alongside this test file.
    """
    if not _FIXTURE_PATH.exists():
        pytest.skip(f"real fixture not yet bundled: {_FIXTURE_PATH}")

    result = parse_merged_json(str(_FIXTURE_PATH))
    assert len(result) == 11, f"expected 11 entries from fixture, got {len(result)}"

    all_items = [item for entry in result for item in entry.get("memory_items", [])]
    assert len(all_items) >= 30, f"expected ≥30 Memory Items, got {len(all_items)}"

    targets = {entry["target_skill_path"] for entry in result}
    assert len(targets) == 4, f"expected 4 distinct target skills, got {len(targets)}"


# ---------------------------------------------------------------------------
# v0.5 T2 tests — analyst-dispatch payload + mandatory --lang flag.
# ---------------------------------------------------------------------------


def test_build_dispatch_payload_emits_correct_schema() -> None:
    """v0.5 T2 — pure function returns the orchestrator-dispatch payload shape."""
    merged = parse_merged_json(str(_FIXTURE_PATH))
    payload = build_dispatch_payload(
        merged_data=merged,
        lang="zh-TW",
        date_str="2026-05-27",
        output_path="/tmp/x.md",
    )
    assert set(payload.keys()) == {"dispatch_payload", "output_path"}
    dp = payload["dispatch_payload"]
    assert dp["prompt_path"] == "agents/prompt-advisory-analyst.md"
    assert dp["model"] == "claude-sonnet-4-6"
    assert set(dp["input"].keys()) == {"merged_data", "lang", "date_str"}
    assert dp["input"]["lang"] == "zh-TW"
    assert dp["input"]["date_str"] == "2026-05-27"
    assert payload["output_path"] == "/tmp/x.md"


def test_main_requires_lang_flag(capsys: pytest.CaptureFixture[str]) -> None:
    """v0.5 T2 — argparse rejects invocation without --lang."""
    with pytest.raises(SystemExit) as exc:
        main(["--input", str(_FIXTURE_PATH)])
    assert exc.value.code != 0
    err = capsys.readouterr().err
    assert "--lang" in err or "lang" in err.lower()


def test_main_rejects_invalid_lang(capsys: pytest.CaptureFixture[str]) -> None:
    """v0.5 T2 — argparse rejects --lang values outside zh-TW/en/ja."""
    with pytest.raises(SystemExit) as exc:
        main(["--input", str(_FIXTURE_PATH), "--lang", "fr"])
    assert exc.value.code != 0


def test_main_emits_dispatch_payload_to_stdout(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    """v0.5 T2 — main() with valid --lang prints dispatch payload JSON to stdout and returns 0."""
    out_path = tmp_path / "advisory.md"
    rc = main([
        "--input", str(_FIXTURE_PATH),
        "--output", str(out_path),
        "--date", "2026-05-27",
        "--lang", "zh-TW",
    ])
    assert rc == 0
    captured = capsys.readouterr()
    parsed = json.loads(captured.out)
    assert parsed["output_path"] == str(out_path)
    assert parsed["dispatch_payload"]["model"] == "claude-sonnet-4-6"
    assert parsed["dispatch_payload"]["prompt_path"] == "agents/prompt-advisory-analyst.md"
    assert parsed["dispatch_payload"]["input"]["lang"] == "zh-TW"
    assert parsed["dispatch_payload"]["input"]["date_str"] == "2026-05-27"
    assert "merged_data" in parsed["dispatch_payload"]["input"]


# ---------------------------------------------------------------------------
# v0.5 T3 — refactor-invariant: heuristic helpers must not exist after v0.5.
# ---------------------------------------------------------------------------


def test_heuristic_functions_removed():
    """v0.5 T3 — refactor-invariant: heuristic helpers must not exist after v0.5 architecture migration."""
    import report
    deleted_symbols = [
        "_STOP_WORDS",
        "_tokenize_title",
        "cluster_by_title_keyword",
        "extract_claude_md_candidates",
        "_render_header",
        "_render_anti_patterns_section",
        "_render_skill_breakdown_section",
        "_render_claude_md_section",
        "_render_new_skill_section",
        "_render_summary_section",
        "_render_action_steps_section",
        "render_advisory_markdown",
    ]
    for sym in deleted_symbols:
        assert getattr(report, sym, None) is None, f"{sym} should be deleted in v0.5 T3"
