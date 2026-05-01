"""Tests for report-stock-snapshot/scripts/snapshot_format.py.

Pure-formatter contract. The script consumes a snapshot pack JSON and emits
a single-page Markdown card. No network, no subprocess, no env access.

Coverage:
  - Smoke (--help, valid AAPL fixture)
  - Pure-formatter discipline (AST-based forbidden import scan)
  - Markdown structure (header / 52W / Valuation / Returns)
  - Country routing: --country us explicit + --country auto shape-sniff
  - 3 languages (en / zh-TW / ja) with localized headers
  - Forward P/E rendering when present, omitted when null
  - Empty pack {} all-N/A graceful rendering
  - KR pack with primary_source_note → footer + warnings de-duplicated
  - divYield assumed already-percent (0.38 → 0.38%, NOT 38%)
"""
from __future__ import annotations

import json


def test_help_runs(scripts, run_script):
    cp = run_script(scripts["snapshot"], ["--help"])
    assert cp.returncode == 0
    assert "snapshot pack" in cp.stdout.lower() or "input" in cp.stdout.lower()


def test_aapl_smoke(scripts, fixtures_dir, run_script):
    cp = run_script(
        scripts["snapshot"],
        ["--input", str(fixtures_dir / "aapl_pack.json"), "--country", "us", "--lang", "en"],
    )
    assert cp.returncode == 0, cp.stderr
    out = cp.stdout
    assert out.lstrip().startswith("## "), f"expected '## ' header, got: {out[:60]!r}"
    assert "AAPL" in out and "Snapshot" in out
    assert "Apple Inc." in out
    assert "52W" in out
    assert "Valuation" in out
    assert "Returns" in out


def test_pure_formatter_imports(scripts, collect_imports, forbidden_imports):
    """No HTTP / subprocess / yfinance imports allowed in the format script."""
    imports = collect_imports(scripts["snapshot"])
    leaked = imports & forbidden_imports
    assert not leaked, f"snapshot_format.py imports forbidden modules: {leaked}"


def test_country_explicit_us(scripts, fixtures_dir, run_script):
    cp = run_script(
        scripts["snapshot"],
        ["--input", str(fixtures_dir / "aapl_pack.json"), "--country", "us"],
    )
    assert cp.returncode == 0
    assert "SEC EDGAR" in cp.stdout


def test_country_auto_sniffs_us(scripts, fixtures_dir, run_script):
    """data-us pack has no 'country' key — auto routing must shape-sniff to US."""
    cp = run_script(
        scripts["snapshot"],
        ["--input", str(fixtures_dir / "aapl_pack.json")],
    )
    assert cp.returncode == 0
    assert "SEC EDGAR" in cp.stdout


def test_country_auto_sniffs_tw(scripts, fixtures_dir, run_script):
    """data-tw pack uses _pack/_ticker — auto routes to TW + zh-TW labels."""
    cp = run_script(
        scripts["snapshot"],
        ["--input", str(fixtures_dir / "tsmc_pack.json")],
    )
    assert cp.returncode == 0
    assert "估值" in cp.stdout
    assert "三大法人" in cp.stdout


def test_lang_zh_tw_headers(scripts, fixtures_dir, run_script):
    cp = run_script(
        scripts["snapshot"],
        ["--input", str(fixtures_dir / "aapl_pack.json"), "--country", "us", "--lang", "zh-TW"],
    )
    assert cp.returncode == 0
    assert "估值" in cp.stdout
    assert "報酬" in cp.stdout


def test_lang_ja_headers(scripts, fixtures_dir, run_script):
    cp = run_script(
        scripts["snapshot"],
        ["--input", str(fixtures_dir / "aapl_pack.json"), "--country", "us", "--lang", "ja"],
    )
    assert cp.returncode == 0
    assert "バリュエーション" in cp.stdout
    assert "リターン" in cp.stdout


def test_forward_pe_rendered_when_present(scripts, fixtures_dir, run_script):
    """AAPL fixture has forwardPE=26.0 — must show 'Forward P/E 26.00'."""
    cp = run_script(
        scripts["snapshot"],
        ["--input", str(fixtures_dir / "aapl_pack.json"), "--country", "us", "--lang", "en"],
    )
    assert cp.returncode == 0
    assert "Forward P/E" in cp.stdout
    assert "26.00" in cp.stdout


def test_forward_pe_omitted_when_null(scripts, fixtures_dir, tmp_path, run_script):
    """When forwardPE is missing, the 'Forward P/E' segment must NOT appear."""
    pack = json.loads((fixtures_dir / "aapl_pack.json").read_text())
    pack["company_info"].pop("forwardPE", None)
    p = tmp_path / "aapl_no_fwd.json"
    p.write_text(json.dumps(pack))
    cp = run_script(scripts["snapshot"], ["--input", str(p), "--country", "us", "--lang", "en"])
    assert cp.returncode == 0
    assert "Forward P/E" not in cp.stdout


def test_empty_pack_all_na(scripts, fixtures_dir, run_script):
    """Empty pack {} → script must not crash; renders N/A placeholders."""
    cp = run_script(
        scripts["snapshot"],
        ["--input", str(fixtures_dir / "empty_pack.json"), "--country", "us"],
    )
    assert cp.returncode == 0, cp.stderr
    assert "N/A" in cp.stdout
    assert cp.stdout.lstrip().startswith("## ")


def test_kr_primary_source_note_dedup(scripts, fixtures_dir, run_script):
    """KR pack with _provenance.primary_source_note → note shown ONCE in
    warnings, NOT also duplicated in footer 'DART deferred' line."""
    cp = run_script(
        scripts["snapshot"],
        ["--input", str(fixtures_dir / "kr_pack_with_note.json")],
    )
    assert cp.returncode == 0
    out = cp.stdout
    note_count = out.count("DART")
    assert note_count == 1, (
        f"DART mentioned {note_count} times — expected exactly 1 (warnings only)."
    )
    assert "yfinance Tier 2 (.KS/.KQ price + valuation)." in out


def test_divyield_already_percent(scripts, fixtures_dir, run_script):
    """AAPL fixture has dividendYield=0.38 (already percent for 0.38%).
    Must render as '0.38%', NOT '38.00%' (legacy fraction interpretation)."""
    cp = run_script(
        scripts["snapshot"],
        ["--input", str(fixtures_dir / "aapl_pack.json"), "--country", "us", "--lang", "en"],
    )
    assert cp.returncode == 0
    assert "0.38%" in cp.stdout, "divYield 0.38 must render as 0.38%"
    assert "38.00%" not in cp.stdout, "divYield 0.38 must NOT render as 38.00%"
