"""Tests for report-screener-list/scripts/screener_format.py.

Pure-formatter contract. Input: analysis-screener ranked JSON. Output:
Markdown — preset header + 14-column ranked table + filtered-out section
+ optional warnings <details> block + footer. No network, no subprocess.

Coverage:
  - Smoke (--help, 5-ranked fixture)
  - Pure-formatter discipline (AST forbidden imports)
  - 14-column table header (Rank / Ticker / Score / Valuation / Momentum /
    Trend / Quality / P/E / P/B / Div / RSI / vs SMA200 / MACD / Price)
  - Empty ranked → 'No tickers passed' message, no orphan section header
  - Tickers with warnings → ⚠️ marker + collapsible <details> block
  - No warnings → no orphan 'Per-ticker warnings' heading (M-4 fix)
  - filtered_out: first 3 + 'and N more' truncation
  - 3 languages
"""
from __future__ import annotations


def test_help_runs(scripts, run_script):
    cp = run_script(scripts["screener"], ["--help"])
    assert cp.returncode == 0
    assert "screener" in cp.stdout.lower() or "input" in cp.stdout.lower()


def test_pure_formatter_imports(scripts, collect_imports, forbidden_imports):
    imports = collect_imports(scripts["screener"])
    leaked = imports & forbidden_imports
    assert not leaked, f"screener_format.py imports forbidden modules: {leaked}"


def test_smoke_5_ranked(scripts, fixtures_dir, run_script):
    cp = run_script(
        scripts["screener"],
        ["--input", str(fixtures_dir / "screener_ranked_5.json"), "--lang", "en"],
    )
    assert cp.returncode == 0, cp.stderr
    out = cp.stdout
    assert out.lstrip().startswith("# "), f"expected '# ' header, got: {out[:40]!r}"
    assert "Stock Screener" in out
    assert "Preset" in out
    for t in ("MSFT", "AAPL", "GOOGL", "MIDQ", "MIDQ2"):
        assert t in out, f"missing ticker {t} in output"


def test_14_column_header(scripts, fixtures_dir, run_script):
    """Verify all 14 columns of the ranked table header are present."""
    cp = run_script(
        scripts["screener"],
        ["--input", str(fixtures_dir / "screener_ranked_5.json"), "--lang", "en"],
    )
    assert cp.returncode == 0
    out = cp.stdout
    expected_cols = [
        "Rank", "Ticker", "Score",
        "Valuation", "Momentum", "Trend", "Quality",
        "P/E", "P/B", "Div %", "RSI",
        "vs SMA200", "MACD", "Price",
    ]
    header_line = next(
        (line for line in out.splitlines() if line.startswith("| Rank |")),
        None,
    )
    assert header_line is not None, "ranked table header row not found"
    for col in expected_cols:
        assert f"| {col} " in header_line or f"| {col} |" in header_line, (
            f"column {col!r} missing from header line: {header_line}"
        )


def test_empty_ranked_message(scripts, fixtures_dir, run_script):
    """Empty ranked array → 'No tickers passed' message; no orphan table."""
    cp = run_script(
        scripts["screener"],
        ["--input", str(fixtures_dir / "screener_empty_ranked.json"), "--lang", "en"],
    )
    assert cp.returncode == 0, cp.stderr
    out = cp.stdout
    assert "No tickers passed" in out
    assert "| Rank |" not in out


def test_warning_marker_and_details_block(scripts, fixtures_dir, run_script):
    """Tickers with warnings → ⚠️ marker on row + <details> block at bottom."""
    cp = run_script(
        scripts["screener"],
        ["--input", str(fixtures_dir / "screener_ranked_5.json"), "--lang", "en"],
    )
    assert cp.returncode == 0
    out = cp.stdout
    assert "`AAPL` ⚠️" in out
    assert "`MSFT` ⚠️" not in out
    assert "<details>" in out
    assert "Per-ticker warnings" in out
    assert "</details>" in out


def test_no_orphan_warnings_header_when_empty(scripts, fixtures_dir, run_script):
    """M-4 fix: when zero ranked records carry warnings, the entire
    'Per-ticker warnings' section must be suppressed (no orphan heading)."""
    cp = run_script(
        scripts["screener"],
        ["--input", str(fixtures_dir / "screener_no_warnings.json"), "--lang", "en"],
    )
    assert cp.returncode == 0
    out = cp.stdout
    assert "Per-ticker warnings" not in out, (
        "no_warnings fixture should NOT emit the 'Per-ticker warnings' heading"
    )
    assert "<details>" not in out
    assert "⚠️" not in out


def test_filtered_out_truncation(scripts, fixtures_dir, run_script):
    """5 filtered_out tickers → first 3 shown + 'and 2 more' row."""
    cp = run_script(
        scripts["screener"],
        ["--input", str(fixtures_dir / "screener_ranked_5.json"), "--lang", "en"],
    )
    assert cp.returncode == 0
    out = cp.stdout
    assert "Filtered Out" in out
    for t in ("BADP", "LOWV", "NULLY"):
        assert f"`{t}`" in out, f"filtered ticker {t} missing"
    assert "and 2 more" in out
    assert "EXTRA1" not in out
    assert "EXTRA2" not in out


def test_lang_zh_tw(scripts, fixtures_dir, run_script):
    cp = run_script(
        scripts["screener"],
        ["--input", str(fixtures_dir / "screener_ranked_5.json"), "--lang", "zh-TW"],
    )
    assert cp.returncode == 0
    assert "個股篩選" in cp.stdout
    assert "排名" in cp.stdout
    assert "估值" in cp.stdout


def test_lang_ja(scripts, fixtures_dir, run_script):
    cp = run_script(
        scripts["screener"],
        ["--input", str(fixtures_dir / "screener_ranked_5.json"), "--lang", "ja"],
    )
    assert cp.returncode == 0
    assert "スクリーナー" in cp.stdout
    assert "順位" in cp.stdout
    assert "バリュエーション" in cp.stdout
