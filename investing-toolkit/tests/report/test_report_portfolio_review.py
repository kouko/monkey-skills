"""Tests for report-portfolio-review/scripts/review_format.py.

Pure-formatter contract. Input: analysis-portfolio JSON (+ optional regime-card
JSON). Output: Markdown — summary / positions table / concentration / optional
regime overlay / provenance footer. No network, no subprocess.

Coverage:
  - Smoke (--help + 3-position fixture)
  - Pure-formatter discipline (AST forbidden imports)
  - Markdown sections (header / summary / positions / concentration / provenance)
  - pnl_ratio fractional (0.4) → '+40.00%' rendering
  - Positions rendered in source order (formatter does NOT re-sort —
    upstream analysis-portfolio orders by descending weight)
  - Optional --regime: section appears when provided, absent when omitted
  - 3 languages with localized IC quadrant labels
  - top3_weight uses totals.top3_weight (formatter does not recompute)
"""
from __future__ import annotations

import json


def test_help_runs(scripts, run_script):
    cp = run_script(scripts["review"], ["--help"])
    assert cp.returncode == 0
    assert "portfolio" in cp.stdout.lower()


def test_pure_formatter_imports(scripts, collect_imports, forbidden_imports):
    imports = collect_imports(scripts["review"])
    leaked = imports & forbidden_imports
    assert not leaked, f"review_format.py imports forbidden modules: {leaked}"


def test_3positions_smoke(scripts, fixtures_dir, run_script):
    cp = run_script(
        scripts["review"],
        ["--portfolio", str(fixtures_dir / "portfolio_3positions.json"), "--lang", "en"],
    )
    assert cp.returncode == 0, cp.stderr
    out = cp.stdout
    assert out.lstrip().startswith("# "), f"expected '# ' header, got: {out[:40]!r}"
    assert "Portfolio Review" in out
    assert "## Summary" in out
    assert "## Positions" in out
    assert "## Concentration" in out
    assert "## Data Sources" in out
    assert "MSFT" in out and "AAPL" in out and "GOOGL" in out


def test_pnl_ratio_fractional_to_percent(scripts, fixtures_dir, run_script):
    """pnl_ratio=0.4 must render as '+40.00%', not '0.40%'."""
    cp = run_script(
        scripts["review"],
        ["--portfolio", str(fixtures_dir / "portfolio_3positions.json"), "--lang", "en"],
    )
    assert cp.returncode == 0
    assert "+40.00%" in cp.stdout, "pnl_ratio 0.4 must render as +40.00%"
    assert "0.40%" not in cp.stdout, "pnl_ratio 0.4 must NOT render as 0.40%"


def test_positions_order_preserved(scripts, fixtures_dir, run_script):
    """Formatter renders positions in source order (upstream sorts by
    descending weight; MSFT 50% > AAPL 30% > GOOGL 20% in fixture)."""
    cp = run_script(
        scripts["review"],
        ["--portfolio", str(fixtures_dir / "portfolio_3positions.json"), "--lang", "en"],
    )
    assert cp.returncode == 0
    out = cp.stdout
    msft_idx = out.index("| MSFT")
    aapl_idx = out.index("| AAPL")
    googl_idx = out.index("| GOOGL")
    assert msft_idx < aapl_idx < googl_idx, (
        f"positions must render in descending-weight source order: "
        f"got MSFT@{msft_idx} AAPL@{aapl_idx} GOOGL@{googl_idx}"
    )


def test_regime_section_present_when_provided(scripts, fixtures_dir, run_script):
    cp = run_script(
        scripts["review"],
        [
            "--portfolio", str(fixtures_dir / "portfolio_with_regime.json"),
            "--regime", str(fixtures_dir / "regime_5country.json"),
            "--lang", "en",
        ],
    )
    assert cp.returncode == 0, cp.stderr
    assert "Macro Regime Overlay" in cp.stdout
    assert "Cross-country" in cp.stdout


def test_regime_section_absent_when_omitted(scripts, fixtures_dir, run_script):
    cp = run_script(
        scripts["review"],
        ["--portfolio", str(fixtures_dir / "portfolio_3positions.json"), "--lang", "en"],
    )
    assert cp.returncode == 0
    assert "Macro Regime Overlay" not in cp.stdout
    assert "Regime Overlay" not in cp.stdout


def test_lang_zh_tw(scripts, fixtures_dir, run_script):
    cp = run_script(
        scripts["review"],
        [
            "--portfolio", str(fixtures_dir / "portfolio_with_regime.json"),
            "--regime", str(fixtures_dir / "regime_5country.json"),
            "--lang", "zh-TW",
        ],
    )
    assert cp.returncode == 0
    assert "投資組合回顧" in cp.stdout
    assert "持倉明細" in cp.stdout
    assert "階段一 — 復甦" in cp.stdout


def test_lang_ja(scripts, fixtures_dir, run_script):
    cp = run_script(
        scripts["review"],
        [
            "--portfolio", str(fixtures_dir / "portfolio_with_regime.json"),
            "--regime", str(fixtures_dir / "regime_5country.json"),
            "--lang", "ja",
        ],
    )
    assert cp.returncode == 0
    assert "ポートフォリオレビュー" in cp.stdout
    assert "局面1 — 回復" in cp.stdout


def test_top3_weight_from_totals(scripts, fixtures_dir, run_script):
    """Formatter must use totals.top3_weight when present (no recompute).
    Fixture sets top3_weight=0.99 even though sum-of-top-3-weights == 1.00.
    The rendered value must be 99.00%, proving it pulled from totals."""
    cp = run_script(
        scripts["review"],
        ["--portfolio", str(fixtures_dir / "portfolio_3positions.json"), "--lang", "en"],
    )
    assert cp.returncode == 0
    assert "Top-3 weight" in cp.stdout
    assert "99.00%" in cp.stdout, (
        "totals.top3_weight=0.99 must render as 99.00% (formatter pulls from totals)"
    )


def test_top3_fallback_recompute_when_missing(scripts, fixtures_dir, tmp_path, run_script):
    """Backward-compat: when totals.top3_weight is missing, formatter
    falls back to summing the first 3 positions' weights."""
    data = json.loads((fixtures_dir / "portfolio_3positions.json").read_text())
    data["totals"].pop("top3_weight", None)
    p = tmp_path / "no_top3.json"
    p.write_text(json.dumps(data))
    cp = run_script(scripts["review"], ["--portfolio", str(p), "--lang", "en"])
    assert cp.returncode == 0
    # 0.50 + 0.30 + 0.20 = 1.00 → 100.00%
    assert "100.00%" in cp.stdout
