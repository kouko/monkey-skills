"""Structural tests for report-equity-memo's Phase 3.5 quarterly-KPI wiring
(Task 4, docs/loom/plans/2026-07-18-memo-quarterly-kpi-wiring.md).

Phase 3.5 (US tickers only) runs the three-step chain
`--pack kpi-quarterly` -> `quarterly-series` -> `build-quarterly` and hands
the resulting memo-feed JSON to Phase 4 as an OPTIONAL input-bundle entry;
non-US tickers record an explicit skip note in the Phase-4 seed (never a
silent absence). Prose policies are not pytest-able beyond structure (repo
memory), so these are grep-level structural pins:

  - schema-phase4-input-bundle.json declares the OPTIONAL
    `kpi_quarterly_feed` property (never in `required`), mirroring the
    memo-feed 1.1 envelope kpi_memo_feed.build_quarterly_memo_feed emits
  - SKILL.md carries a Phase 3.5 block between Phase 3 and Phase 4 with
    the three chain steps in order, and the quarterly-series invocation
    keeps `requests` importable (kpi_xbrl.py declares PEP 723
    `dependencies = []` but its coverage path lazily imports
    sec_edgar_client -> `import requests`; a bare `uv run` crashes)
  - phase4-seed-contract.md names the optional feed path + the non-US
    skip-note contract, and its orchestrator acceptance greps cover it
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_DIR = REPO_ROOT / "skills" / "report-equity-memo"
SKILL_MD = SKILL_DIR / "SKILL.md"
SEED_CONTRACT = SKILL_DIR / "references" / "phase4-seed-contract.md"
SCHEMA = SKILL_DIR / "references" / "schema-phase4-input-bundle.json"


def test_schema_declares_optional_kpi_quarterly_feed():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    # OPTIONAL: declared under properties, never promoted into required —
    # non-US runs legitimately omit the feed (with a seed skip note).
    assert "kpi_quarterly_feed" in schema["properties"]
    assert "kpi_quarterly_feed" not in schema["required"]

    entry = schema["properties"]["kpi_quarterly_feed"]
    assert entry["type"] == "object"
    # Mirrors the memo-feed 1.1 envelope (kpi_memo_feed.build_quarterly_memo_feed).
    for key in ("_memo_feed_schema_version", "company", "status", "series", "coverage_flags"):
        assert key in entry["required"], f"feed envelope key {key!r} not pinned"
    assert entry["properties"]["_memo_feed_schema_version"]["const"] == "1.1"


def test_skill_md_phase_3_5_block_present_and_ordered():
    text = SKILL_MD.read_text(encoding="utf-8")

    assert "### Phase 3.5" in text, "Phase 3.5 block missing from SKILL.md"
    # Sits between Phase 3 (DCF) and Phase 4 (delegation).
    assert text.index("### Phase 3 —") < text.index("### Phase 3.5") < text.index("### Phase 4")

    block = text[text.index("### Phase 3.5"):text.index("### Phase 4")]
    # Three-step chain referenced in pipeline order.
    i_pack = block.index("--pack kpi-quarterly")
    i_series = block.index("quarterly-series")
    i_feed = block.index("build-quarterly")
    assert i_pack < i_series < i_feed, "chain steps out of pipeline order"


def test_skill_md_quarterly_series_invocation_keeps_requests_importable():
    """kpi_xbrl.py's PEP 723 header declares `dependencies = []`, but the
    quarterly-series coverage path lazily imports sec_edgar_client, whose
    module level does `import requests` — a bare `uv run` of the script
    CRASHES. The documented command must keep `requests` importable, or the
    doc ships an invocation that fails for every user."""
    text = SKILL_MD.read_text(encoding="utf-8")
    block = text[text.index("### Phase 3.5"):text.index("### Phase 4")]
    series_cmd_lines = [
        line for line in block.splitlines()
        if "kpi_xbrl.py" in line and "uv run" in line
    ]
    assert series_cmd_lines, "no uv run kpi_xbrl.py invocation in Phase 3.5"
    for line in series_cmd_lines:
        assert "--with requests" in line, (
            f"quarterly-series invocation lacks --with requests: {line!r}"
        )


def test_skill_md_phase_3_5_non_us_skip_is_explicit():
    text = SKILL_MD.read_text(encoding="utf-8")
    block = text[text.index("### Phase 3.5"):text.index("### Phase 4")]
    assert "US tickers only" in block
    # Non-US: skip note recorded in the Phase 4 seed — never silent absence.
    assert "skip note" in block


def test_seed_contract_names_optional_feed_and_skip_note():
    text = SEED_CONTRACT.read_text(encoding="utf-8")
    # Optional feed path entry.
    assert "kpi-quarterly-feed" in text
    assert "build-quarterly" in text
    # Skip-note contract for non-US stays explicit.
    assert "skip note" in text
    # Orchestrator acceptance-grep section extended to cover the feed.
    acceptance = text[text.index("## Orchestrator acceptance check"):]
    assert "kpi" in acceptance.lower(), "acceptance greps do not cover the kpi feed"
