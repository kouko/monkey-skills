"""test_twse_ixbrl_cli.py — OFFLINE tests for twse_ixbrl.py (Task 5,
docs/loom/plans/2026-07-19-tw-ixbrl-ingestion.md).

The CLI composes twse_ixbrl_fetch (Task 2) -> twse_ixbrl_parser (Task 1)
-> twse_ixbrl_canonical + twse_ixbrl_notes (Tasks 3/4) and emits one JSON
object to stdout. The fetch layer is stubbed at the
`twse_ixbrl_fetch.fetch_ixbrl_body` seam (module attribute, so the CLI's
module-namespace call picks up the patched function) -- no live network,
no `network` marker.

Run offline (part of the default "not network" suite):
  PYTHONDONTWRITEBYTECODE=1 python3 -m pytest investing-toolkit/tests/ -q -m "not network"
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _load_modules():
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import twse_ixbrl
    import twse_ixbrl_fetch
    return twse_ixbrl, twse_ixbrl_fetch


def _fixture_body() -> str:
    return (FIXTURES / "twse_ixbrl_2330_2024Q3_C.html").read_text(encoding="big5")


def test_cli_success_emits_canonical_and_notes(monkeypatch, capsys):
    twse_ixbrl, fetch_mod = _load_modules()
    monkeypatch.setattr(fetch_mod, "fetch_ixbrl_body", lambda **_kw: _fixture_body())
    monkeypatch.setattr(
        sys, "argv",
        ["twse_ixbrl.py", "--co-id", "2330", "--year", "2024", "--season", "3",
         "--report-id", "C"],
    )

    with pytest.raises(SystemExit) as excinfo:
        twse_ixbrl.main()
    assert excinfo.value.code == 0

    out = capsys.readouterr().out
    result = json.loads(out)  # must be valid JSON, not a traceback

    assert "_error" not in result
    canonical = result["canonical"]
    assert set(["income_statement", "balance_sheet", "cash_flow"]) <= set(canonical)
    notes = result["notes"]
    assert "financial_assets_fvoci" in notes


def test_cli_not_found_emits_error_envelope(monkeypatch, capsys):
    twse_ixbrl, fetch_mod = _load_modules()
    monkeypatch.setattr(fetch_mod, "fetch_ixbrl_body", lambda **_kw: None)
    monkeypatch.setattr(
        sys, "argv",
        ["twse_ixbrl.py", "--co-id", "9999", "--year", "2024", "--season", "1",
         "--report-id", "C"],
    )

    with pytest.raises(SystemExit) as excinfo:
        twse_ixbrl.main()
    assert excinfo.value.code == 1

    out = capsys.readouterr().out
    result = json.loads(out)  # valid JSON _error envelope, never a traceback

    assert "_error" in result
    assert "canonical" not in result
