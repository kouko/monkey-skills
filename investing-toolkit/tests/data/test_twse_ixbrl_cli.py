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
from unittest import mock

import pytest

ROOT = Path(__file__).resolve().parents[2]
MARKETS_SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

# The CLI imports twse_ixbrl_fetch, which does `import requests`. CI's offline
# environment has no `requests` installed (the clients ship PEP 723 deps and run
# via `uv run`), so the bare import chain would ModuleNotFoundError at collection.
# Stub it here BEFORE any loader imports the CLI — setdefault keeps a real
# `requests` when present (local) and installs a stub when absent (CI). The fetch
# seam is monkeypatched per-test, so `requests` is never actually exercised.
sys.modules.setdefault("requests", mock.MagicMock(name="requests"))


def _load_modules():
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import twse_ixbrl
    import twse_ixbrl_fetch
    return twse_ixbrl, twse_ixbrl_fetch


def _load_all_modules():
    if str(MARKETS_SCRIPTS) not in sys.path:
        sys.path.insert(0, str(MARKETS_SCRIPTS))
    import twse_ixbrl
    import twse_ixbrl_canonical
    import twse_ixbrl_fetch
    import twse_ixbrl_notes
    import twse_ixbrl_parser
    return twse_ixbrl, twse_ixbrl_fetch, twse_ixbrl_parser, twse_ixbrl_canonical, twse_ixbrl_notes


def _fixture_body() -> str:
    return (FIXTURES / "twse_ixbrl_2330_2024Q3_C.html").read_text(encoding="big5")


def _smart_fixture_body(fetch_mod, filename: str) -> str:
    # Financial-family (-fh/-basi/-bd/-ins) fixtures are genuinely UTF-8
    # despite the declared big5 charset (Task 14 finding) -- decode the
    # same way the real fetch layer does (decode_ixbrl_document), since
    # these tests stub `fetch_ixbrl_body` entirely (its own decode step
    # is bypassed) and must hand run_pipeline an equivalently-decoded body.
    raw = (FIXTURES / filename).read_bytes()
    return fetch_mod.decode_ixbrl_document(raw)


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


def test_cli_parse_failure_emits_error_envelope_not_traceback(monkeypatch, capsys):
    """Fetch succeeds, but parse_ixbrl_facts raises -- the pipeline's
    parse/build/notes try-block (twse_ixbrl.py run_pipeline) must convert
    this into a JSON `_error` envelope, never a raw traceback to stdout.
    """
    twse_ixbrl, fetch_mod, parser_mod, _canonical_mod, _notes_mod = _load_all_modules()
    monkeypatch.setattr(fetch_mod, "fetch_ixbrl_body", lambda **_kw: _fixture_body())

    def _boom(*_args, **_kwargs):
        raise ValueError("boom")

    monkeypatch.setattr(parser_mod, "parse_ixbrl_facts", _boom)
    monkeypatch.setattr(
        sys, "argv",
        ["twse_ixbrl.py", "--co-id", "2330", "--year", "2024", "--season", "3",
         "--report-id", "C"],
    )

    with pytest.raises(SystemExit) as excinfo:
        twse_ixbrl.main()
    assert excinfo.value.code == 1

    out = capsys.readouterr().out
    result = json.loads(out)  # must be valid JSON, not a traceback

    assert result["_error"] == "parse_failed: boom"
    assert "canonical" not in result
    assert "notes" not in result


def test_cli_quiet_propagates_to_sibling_modules(monkeypatch, capsys):
    """--quiet must silence stderr logging in the 4 composed sibling
    modules too, not just this module's own _QUIET flag."""
    twse_ixbrl, fetch_mod, parser_mod, canonical_mod, notes_mod = _load_all_modules()
    monkeypatch.setattr(fetch_mod, "fetch_ixbrl_body", lambda **_kw: _fixture_body())
    monkeypatch.setattr(
        sys, "argv",
        ["twse_ixbrl.py", "--co-id", "2330", "--year", "2024", "--season", "3",
         "--report-id", "C", "--quiet"],
    )

    orig_fetch_quiet = fetch_mod._QUIET
    orig_parser_log = parser_mod._log
    orig_canonical_log = canonical_mod._log
    orig_notes_log = notes_mod._log
    try:
        with pytest.raises(SystemExit) as excinfo:
            twse_ixbrl.main()
        assert excinfo.value.code == 0
        capsys.readouterr()  # drain stdout JSON; irrelevant here

        # fetch_mod exposes its own _QUIET gate -- propagated.
        assert fetch_mod._QUIET is True

        # parser/canonical/notes have no _QUIET gate of their own (they
        # log unconditionally) -- propagation must still silence their
        # stderr output, by neutralizing their _log at the module level.
        parser_mod._log("bad scale attribute", "scale=x, left unscaled")
        canonical_mod._log("bad period bounds", "start=None end=None")
        notes_mod._log("curated notes partial", "0/1 concepts present")
        assert capsys.readouterr().err == ""
    finally:
        fetch_mod._QUIET = orig_fetch_quiet
        parser_mod._log = orig_parser_log
        canonical_mod._log = orig_canonical_log
        notes_mod._log = orig_notes_log


def test_cli_fh_filer_composes_financial_canonical_and_fh_npl_notes(monkeypatch, capsys):
    """Task 11: an -fh (financial-holding, e.g. 2882 國泰金控) filer is
    served at report_id=C. run_pipeline must route build_canonical's
    "fh" taxonomy output to extract_fh_npl_coverage_notes -- not the
    -ci extract_curated_notes -- keyed by bank subsidiary (國泰世華銀行)."""
    twse_ixbrl, fetch_mod = _load_modules()
    body = _smart_fixture_body(fetch_mod, "twse_ixbrl_2882_2026Q1_C.html")

    # C is present for this -fh filer -- report_id fallback should not
    # even need to try A, but the stub tolerates either report_id so a
    # correct implementation isn't accidentally rewarded for guessing.
    monkeypatch.setattr(
        fetch_mod, "fetch_ixbrl_body",
        lambda co_id, year, season, report_id: body,
    )
    monkeypatch.setattr(
        sys, "argv",
        ["twse_ixbrl.py", "--co-id", "2882", "--year", "2026", "--season", "1"],
    )

    with pytest.raises(SystemExit) as excinfo:
        twse_ixbrl.main()
    assert excinfo.value.code == 0

    result = json.loads(capsys.readouterr().out)
    assert "_error" not in result

    canonical = result["canonical"]
    assert canonical["sector_class"] == "financial"
    assert canonical["taxonomy"] == "fh"

    notes = result["notes"]
    assert "國泰世華銀行" in notes
    assert "coverage_ratio" in notes["國泰世華銀行"]


def test_cli_insurer_fetches_via_report_a_fallback_no_npl_notes(monkeypatch, capsys):
    """Task 11: an insurer (e.g. 2867 三商美邦人壽) is served ONLY at
    report_id=A -- C resolves to the absence sentinel (None). run_pipeline
    must use fetch_with_report_fallback (C then A) to land the body, route
    build_canonical's "ins" taxonomy output, and NOT call any NPL/coverage
    extractor (brokers/insurers carry no such note)."""
    twse_ixbrl, fetch_mod = _load_modules()
    body = _smart_fixture_body(fetch_mod, "twse_ixbrl_2867_2026Q1_A.html")

    def _fetch(co_id, year, season, report_id):
        if report_id == "C":
            return None  # 檔案不存在 sentinel -- not filed at C
        assert report_id == "A"
        return body

    monkeypatch.setattr(fetch_mod, "fetch_ixbrl_body", _fetch)
    monkeypatch.setattr(
        sys, "argv",
        ["twse_ixbrl.py", "--co-id", "2867", "--year", "2026", "--season", "1"],
    )

    with pytest.raises(SystemExit) as excinfo:
        twse_ixbrl.main()
    assert excinfo.value.code == 0

    result = json.loads(capsys.readouterr().out)
    assert "_error" not in result

    canonical = result["canonical"]
    assert canonical["sector_class"] == "financial"
    assert canonical["taxonomy"] == "ins"

    assert result["notes"] == {}
