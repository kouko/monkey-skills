"""test_data_markets_live.py — consolidated live-API contract tests for the
merged data-markets skill's pack.py facade (Task 5c of
docs/loom/plans/2026-07-11-investing-toolkit-data-consolidation.md).

Migrates the network-marked tests that used to live in
tests/data/test_data_{us,jp,tw,kr,cn}.py (one section per market below,
preserving each original test's intent) — those 5 files are deleted in the
same task, since their skill paths (skills/data-{us,jp,tw,kr,cn}/) no longer
exist.

Coverage accounting for the deleted files' 56 tests (round-1 gap: this
docstring previously overclaimed the drop was "covered by fixture/
shape-parity assertions" without saying which tests or where; corrected in
round 2):
  - 10 pure-logic tests (ROC-quarter-math for TW, ticker auto-suffix
    normalisation for KR/CN) covered still-live functions
    (pack_tw.latest_roc_quarter, pack_kr.normalize_ticker,
    pack_cn._normalise_ticker) that merely moved into pack_{market}.py.
    These were dropped by the round-1 deletion and are now RESTORED in
    tests/data/test_data_markets_{tw,kr,cn}.py (1 TW + 3 KR + 6 CN).
  - 9 were migration-era cross-skill sync assertions (byte-identical-copy
    checks across the now-merged per-country clients) that no longer apply
    once the copies became one canonical file under data-markets/scripts/ —
    correctly retired, nothing to restore.
  - 32 (net: 40 removed / 8 added) were parametrized instances of 8 test
    functions in tests/test_skill_structure.py (test_skill_md_present,
    test_skill_frontmatter_required_keys,
    test_skill_description_length_under_1024,
    test_scripts_subdir_present_when_required) and
    tests/test_path_conventions.py
    (test_data_analysis_self_refs_no_cross_skill_drift,
    test_no_absolute_user_paths, test_no_skill_dir_parent_escape,
    test_skill_dir_not_followed_by_skills_subpath), each reparametrized
    from the 5-item DATA_SKILLS list down to ["data-markets"]. They check
    SKILL.md presence/frontmatter/description-length and path-safety —
    the same checks now run once against data-markets in those SAME two
    files; nothing to restore.
  - 5 were CN-specific legacy output-shape assertions tied to the old
    data-cn/scripts/pack.py's pre-consolidation JSON envelope, superseded by
    pack_cn.py's current shape (already covered by
    tests/data/test_data_markets_cn.py's migration-contract test).
  (10 + 9 + 32 + 5 = 56, matching the round-1 net test-count drop.)

All tests here hit real external APIs (yfinance / SEC EDGAR / FRED / TDnet /
BOJ / e-Stat / ECB / MOPS / TWSE / FinMind / CBC / DGBAS / NDC / stat.gov.tw /
FinanceDataReader / BOK ECOS / akshare / NBS) via the unified facade
`skills/data-markets/scripts/pack.py`. Marked @pytest.mark.network — skipped
in offline CI (`pytest -m "not network"`).

Cache: honors $INVESTING_TOOLKIT_CACHE.

One deliberate behavior change vs. the old per-market CLIs: the unified
facade (pack.py) dropped `--indicators` (data-kr regime-pack indicator-group
subset) and `--kosdaq` — see pack.py's module docstring "Dropped flags"
section for the grounding (zero downstream references found). The KR
regime-pack test below was adapted accordingly: it no longer restricts to
`rates,inflation` via `--indicators` (that flag no longer exists) and instead
asserts those two groups are present within the full default group set —
preserving the assertion's intent (rates + inflation populate) without the
now-removed restriction flag.

Task-2 edgartools acquisition anchor (D7 grounding): the section
"US — edgartools acquisition shape anchor" below captures the REAL edgartools
5.42.0 Filing attribute shape that the offline mocks in
tests/data/test_sec_narrative.py mirror (fixtures-mirror-producer-shape).
grounding: edgartools 5.42.0 — edgar.get_by_accession_number / Company.
get_filings; Filing.accession_no(str) / cik(int) / form(str) /
filing_date(datetime.date, NOT str) / period_of_report(str) / filing_url /
homepage_url; `primary_document` does NOT exist (filing_url's tail is the
primary-doc filename). Captured live 2026-07-12 against AAPL FY2024 10-K,
accession 0000320193-24-000123. Sources: PyPI edgartools JSON + GitHub
dgunning/edgartools.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "skills" / "data-markets" / "scripts" / "pack.py"
SCRIPTS = ROOT / "skills" / "data-markets" / "scripts"


def _run_pack(args: list[str], extra_env: dict | None = None, timeout: int = 900) -> dict:
    """Invoke the unified pack.py facade and return parsed JSON. Asserts exit 0."""
    cmd = ["uv", "run", str(PACK), *args]
    env = {**os.environ}
    if extra_env is not None:
        for k, v in extra_env.items():
            if v is None:
                env.pop(k, None)
            else:
                env[k] = v
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    assert proc.returncode == 0, (
        f"pack.py exit={proc.returncode}\nstderr (tail): {proc.stderr[-1500:]}"
    )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        pytest.fail(f"non-JSON stdout: {e}\nhead: {proc.stdout[:500]}")


# ---------------------------------------------------------------------------
# US — AAPL (yfinance + SEC EDGAR + FRED)
# ---------------------------------------------------------------------------

US_TICKER = "AAPL"
US_SCREENER_TICKERS = "AAPL,MSFT,GOOGL,META,AMZN"


@pytest.mark.network
def test_us_snapshot_aapl():
    """snapshot has company_info + price_history; yfinance provenance reachable."""
    out = _run_pack(["--ticker", US_TICKER, "--pack", "snapshot"], timeout=600)
    assert out["pack"] == "snapshot"
    assert out["ticker"] == US_TICKER
    assert "fetched_at" in out
    assert isinstance(out.get("company_info"), dict), "snapshot missing company_info"
    assert isinstance(out.get("price_history"), dict), "snapshot missing price_history"
    info = out["company_info"]
    assert info.get("ticker") or info.get("symbol") or "shortName" in info or "longName" in info, (
        f"company_info missing identifying fields: keys={list(info)[:20]}"
    )


@pytest.mark.network
def test_us_memo_fetch_aapl_has_sec_provenance():
    """memo-fetch should include sec_filings + sec_facts (SEC EDGAR Tier A)."""
    out = _run_pack(["--ticker", US_TICKER, "--pack", "memo-fetch"], timeout=600)
    assert out["pack"] == "memo-fetch"
    assert out["ticker"] == US_TICKER
    assert "fetched_at" in out
    assert isinstance(out.get("company_info"), dict)
    assert "sec_filings" in out, "memo-fetch missing sec_filings"
    assert "sec_facts" in out, "memo-fetch missing sec_facts"
    filings = out["sec_filings"]
    facts = out["sec_facts"]
    assert isinstance(filings, dict), "sec_filings should be a dict"
    assert isinstance(facts, dict), "sec_facts should be a dict"


@pytest.mark.network
def test_us_memo_fetch_aapl_has_extended_canonical_fields():
    """v2.2.0-l: memo-fetch should surface 6 new canonical fields from XBRL.

    AAPL coverage:
      - income_statement.gross_profit            (GrossProfit)
      - cash_flow.depreciation_amortization      (DepreciationDepletionAndAmortization)
      - cash_flow.stock_based_compensation       (ShareBasedCompensation)
      - balance_sheet.total_stockholders_equity  (StockholdersEquity)
      - balance_sheet.intangible_assets          (immaterial — empty array OK)
      - balance_sheet.goodwill                   (zero — empty array OK)
    """
    out = _run_pack(["--ticker", US_TICKER, "--pack", "memo-fetch"], timeout=600)

    inc = out["income_statement"]
    cf = out["cash_flow"]
    bs = out["balance_sheet"]

    assert "gross_profit" in inc, "income_statement missing gross_profit (v2.2.0-l)"
    assert isinstance(inc["gross_profit"], list) and inc["gross_profit"], (
        "AAPL gross_profit array empty — XBRL GrossProfit chain failed"
    )
    assert inc["gross_profit"][0] > 100_000_000_000, (
        f"AAPL FY[0] gross_profit suspiciously small: {inc['gross_profit'][0]}"
    )

    for field, threshold in (
        ("depreciation_amortization", 5_000_000_000),
        ("stock_based_compensation",  5_000_000_000),
    ):
        assert field in cf, f"cash_flow missing {field} (v2.2.0-l)"
        assert isinstance(cf[field], list) and cf[field], (
            f"AAPL {field} array empty — XBRL chain failed"
        )
        assert cf[field][0] > threshold, (
            f"AAPL FY[0] {field} suspiciously small: {cf[field][0]}"
        )

    assert "total_stockholders_equity" in bs, "balance_sheet missing total_stockholders_equity (v2.2.0-l)"
    assert isinstance(bs["total_stockholders_equity"], list) and bs["total_stockholders_equity"], (
        "AAPL total_stockholders_equity array empty — XBRL StockholdersEquity chain failed"
    )
    assert bs["total_stockholders_equity"][0] > 30_000_000_000, (
        f"AAPL FY[0] equity suspiciously small: {bs['total_stockholders_equity'][0]}"
    )

    assert "intangible_assets" in bs, "balance_sheet missing intangible_assets (v2.2.0-l)"
    assert "goodwill" in bs, "balance_sheet missing goodwill (v2.2.0-l)"
    assert isinstance(bs["intangible_assets"], list)
    assert isinstance(bs["goodwill"], list)

    inc_meta = inc.get("_meta", {})
    cf_meta = cf.get("_meta", {})
    bs_meta = bs.get("_meta", {})
    assert "gross_profit" in inc_meta
    assert "depreciation_amortization" in cf_meta
    assert "stock_based_compensation" in cf_meta
    assert "total_stockholders_equity" in bs_meta


@pytest.mark.network
def test_us_comps_multiples_single_aapl():
    """comps-multiples (single) returns multiples block under tickers map."""
    out = _run_pack(["--ticker", US_TICKER, "--pack", "comps-multiples"], timeout=600)
    assert out["pack"] == "comps-multiples"
    tickers = out.get("tickers")
    assert isinstance(tickers, dict)
    assert US_TICKER in tickers
    block = tickers[US_TICKER]
    multiples_keys = {"trailingPE", "forwardPE", "priceToSales", "priceToBook",
                      "enterpriseToEbitda", "enterpriseToRevenue",
                      "marketCap", "enterpriseValue"}
    assert multiples_keys.issubset(block.keys()), (
        f"comps-multiples block missing keys: "
        f"{sorted(multiples_keys - set(block.keys()))}"
    )


@pytest.mark.network
def test_us_screener_batch():
    """screener-batch returns per-ticker lightweight fields."""
    out = _run_pack(["--tickers", US_SCREENER_TICKERS, "--pack", "screener-batch"], timeout=600)
    assert out["pack"] == "screener-batch"
    tickers = out.get("tickers")
    assert isinstance(tickers, dict)
    for t in US_SCREENER_TICKERS.split(","):
        assert t in tickers, f"screener-batch missing ticker {t}"
    sample_ticker = next(iter(tickers))
    sample = tickers[sample_ticker]
    expected = {"trailingPE", "priceToBook", "marketCap", "dividendYield",
                "beta", "fiftyTwoWeekHigh", "fiftyTwoWeekLow",
                "regularMarketPrice", "sector", "industry", "shortName"}
    assert expected.issubset(sample.keys()), (
        f"screener fields missing: {sorted(expected - set(sample.keys()))}"
    )


@pytest.mark.network
def test_us_regime_pack_fred_groups():
    """regime-pack returns FRED groups with observation arrays."""
    out = _run_pack(["--pack", "regime-pack", "--market", "us"], timeout=600)
    assert out["pack"] == "regime-pack"
    assert out["country"] == "US"
    groups = out.get("groups")
    assert isinstance(groups, dict)
    expected_groups = {"rates", "inflation", "growth", "nowcast", "wei",
                       "real_rates", "swap_spreads"}
    assert expected_groups.issubset(groups.keys()), (
        f"missing FRED groups: {sorted(expected_groups - set(groups.keys()))}"
    )
    rates = groups["rates"]
    assert isinstance(rates, dict)
    assert rates, "rates group empty"


# ---------------------------------------------------------------------------
# US — edgartools acquisition shape anchor (Task 2, edgartools migration)
# ---------------------------------------------------------------------------
# fixtures-mirror-producer-shape: this live anchor captures the REAL edgartools
# 5.42.0 Filing attribute shape that the offline mocks in
# tests/data/test_sec_narrative.py mirror. `import edgar` / `import
# sec_edgar_client` are inside the test body so offline collection (edgartools
# not installed, deselected by `-m "not network"`) stays clean.


@pytest.mark.network
def test_edgartools_acquire_real_10k_shape():
    """Anchor the REAL edgartools Filing shape + acquire_filing end-to-end.

    Documents the producer shape the offline mocks mirror; a v5->v6 attribute
    churn surfaces HERE, not silently inside the mocked unit tests. Run live:
      uv run --with pytest --with edgartools==5.42.0 --with 'pyyaml>=6.0' \
        pytest investing-toolkit/tests/data/test_data_markets_live.py \
        -k edgartools_acquire -m network
    """
    import datetime
    import sys

    import edgar

    edgar.set_identity("kouko investing-toolkit noreply@anthropic.com")
    accession = "0000320193-24-000123"  # AAPL FY2024 10-K
    f = edgar.get_by_accession_number(accession)
    assert f is not None, "known AAPL 10-K accession must resolve"
    assert f.accession_no == accession
    assert f.cik == 320193
    assert f.form == "10-K"
    assert isinstance(f.filing_date, datetime.date), (
        "filing_date is a datetime.date, not a str — the client must serialize it"
    )
    assert f.period_of_report == "2024-09-28"
    assert not hasattr(f, "primary_document"), (
        "edgartools has NO primary_document attr — filing_url carries the doc"
    )
    assert f.filing_url.startswith(
        "https://www.sec.gov/Archives/edgar/data/320193/000032019324000123/"
    )
    assert f.filing_url.endswith("aapl-20240928.htm")
    assert f.homepage_url.endswith("-index.html")

    # acquire_filing mirrors that shape end-to-end (by-accession mode).
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import sec_edgar_client

    ref = sec_edgar_client.acquire_filing(accession=accession)
    assert ref["accession"] == accession
    assert ref["cik"] == 320193
    assert ref["form"] == "10-K"
    assert ref["filingDate"] == "2024-11-01"
    assert ref["period_of_report"] == "2024-09-28"
    assert ref["primaryDocument"] == "aapl-20240928.htm"
    assert ref["url"] == f.filing_url


@pytest.mark.network
def test_edgartools_segment_real_10k_shape():
    """Anchor the REAL edgartools TenK/TenQ section API + segment_filing end-to-end.

    fixtures-mirror-producer-shape (Task 3): the offline TenK/TenQ mocks in
    tests/data/test_sec_narrative.py mirror THIS captured shape. A v5->v6
    section-API churn (a renamed property, a changed subscript key) surfaces
    HERE, loud, not silently inside the mocked unit tests. Run live:
      uv run --with pytest --with edgartools==5.42.0 --with 'pyyaml>=6.0' \
        pytest investing-toolkit/tests/data/test_data_markets_live.py \
        -k edgartools_segment -m network
    """
    import sys

    import edgar

    edgar.set_identity("kouko investing-toolkit noreply@anthropic.com")

    # 10-K: management_discussion (Item 7) / risk_factors (Item 1A) are str props.
    tenk_filing = edgar.get_by_accession_number("0000320193-24-000123")  # AAPL FY2024 10-K
    tenk = tenk_filing.obj()
    assert type(tenk).__name__ == "TenK"
    assert isinstance(tenk.management_discussion, str) and tenk.management_discussion.strip(), (
        "TenK.management_discussion (Item 7) must be non-empty str"
    )
    assert isinstance(tenk.risk_factors, str) and tenk.risk_factors.strip(), (
        "TenK.risk_factors (Item 1A) must be non-empty str"
    )

    # 10-Q: NO management_discussion property; Item 2 via obj["Part I, Item 2"] subscript.
    tenq_filing = edgar.Company("AAPL").get_filings(form="10-Q").latest()
    tenq = tenq_filing.obj()
    assert type(tenq).__name__ == "TenQ"
    assert not hasattr(tenq, "management_discussion"), (
        "TenQ has NO management_discussion property — Item 2 is read via subscript"
    )
    assert isinstance(tenq["Part I, Item 2"], str) and tenq["Part I, Item 2"].strip(), (
        "TenQ Item 2 (MD&A) must be non-empty str via obj['Part I, Item 2']"
    )

    # segment_filing mirrors that shape end-to-end.
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import sec_edgar_client

    k_sections = {s["item"]: s for s in sec_edgar_client.segment_filing(tenk_filing)}
    assert set(k_sections) == {"Item 7", "Item 1A"}, "10-K segments into Item 7 + Item 1A"
    assert k_sections["Item 7"]["text"].strip()
    assert k_sections["Item 1A"]["text"].strip()

    q_sections = {s["item"]: s for s in sec_edgar_client.segment_filing(tenq_filing)}
    assert set(q_sections) == {"Item 2"}, "10-Q segments into Item 2"
    assert q_sections["Item 2"]["text"].strip()


@pytest.mark.network
def test_edgartools_segment_real_8k_shape():
    """Anchor the REAL edgartools 8-K exhibit-following shape + segment_filing (Task 4).

    fixtures-mirror-producer-shape: the offline _MockEightK / _MockPressRelease
    mocks in tests/data/test_sec_narrative.py mirror THIS captured shape. Two
    plan-grounding corrections surfaced live and are asserted here so a v5->v6
    churn (or a re-reader trusting the stale plan) fails LOUD:
      - filing.obj() on an 8-K returns type ``CurrentReport`` (NOT ``EightK``).
      - press-release exhibits (``obj.press_releases`` -> ``PressReleases`` of
        ``PressRelease``) expose ``.document`` + ``.text()`` but NO
        ``.document_type`` (that attr is on ``filing.attachments``' Attachments).
    Captured live 2026-07-12 against AAPL earnings 8-K 0000320193-26-000011
    (Item 2.02 + Exhibit 99.1). Run live:
      uv run --with pytest --with edgartools==5.42.0 --with 'pyyaml>=6.0' \
        pytest investing-toolkit/tests/data/test_data_markets_live.py \
        -k edgartools_segment_real_8k -m network
    """
    import sys

    import edgar

    edgar.set_identity("kouko investing-toolkit noreply@anthropic.com")

    # An earnings 8-K reporting Item 2.02 with an EX-99.1 press release.
    filings = edgar.Company("AAPL").get_filings(form="8-K")
    eightk_filing = None
    for f in filings:
        obj = f.obj()
        if any("2.02" in str(it) for it in getattr(obj, "items", [])):
            eightk_filing = f
            break
    assert eightk_filing is not None, "expected an AAPL 8-K reporting Item 2.02"
    obj = eightk_filing.obj()

    assert type(obj).__name__ == "CurrentReport", (
        "filing.obj() on an 8-K is a CurrentReport, not an EightK (plan correction)"
    )
    assert isinstance(obj.items, list) and any("Item 2.02" in str(it) for it in obj.items)
    prs = list(obj.press_releases)
    assert prs, "earnings 8-K must carry at least one EX-99.x press release"
    pr = prs[0]
    assert isinstance(pr.document, str) and pr.document, "PressRelease.document is the EX-99.x filename"
    assert isinstance(pr.text(), str) and pr.text().strip(), "PressRelease.text() is the exhibit body"
    assert not hasattr(pr, "document_type"), (
        "a PressRelease has NO document_type — that attr is on filing.attachments' Attachments"
    )

    # segment_filing mirrors that shape end-to-end.
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    import sec_edgar_client

    sections = {s["item"]: s for s in sec_edgar_client.segment_filing(eightk_filing)}
    assert "Item 2.02" in sections, "8-K segments into a section for reported Item 2.02"
    slot = sections["Item 2.02"]
    assert "error" not in slot
    assert slot["text"].strip(), "Item 2.02 text sourced from its EX-99.x exhibit"
    assert slot["exhibit"] == pr.document, "section provenance records the source exhibit filename"


# ---------------------------------------------------------------------------
# JP — 7203 Toyota (yfinance + TDnet + EDINET + BOJ/e-Stat/ECB)
# ---------------------------------------------------------------------------

JP_TICKER = "7203"  # 4-digit JP code, no suffix — auto-detected by pack.py
JP_SCREENER_TICKERS = "7203,6758,9984,8306,7974"


@pytest.mark.network
def test_jp_snapshot_toyota_auto_t_suffix():
    """4-digit `7203` auto-appends `.T`; snapshot returns yf_ticker + bare."""
    out = _run_pack(["--ticker", JP_TICKER, "--pack", "snapshot"], timeout=600)
    assert out["pack"] == "snapshot"
    assert out["ticker"] == "7203", "bare ticker should pass through"
    assert out["yf_ticker"] == "7203.T", "yf ticker should auto-append .T"
    assert "fetched_at" in out
    assert isinstance(out.get("info"), dict)
    assert isinstance(out.get("price_history"), dict)
    assert "timely_disclosures" in out  # TDnet — always Tier 1, no key
    prov = out.get("_provenance", {})
    assert prov.get("tier") == "tier_1"


@pytest.mark.network
def test_jp_memo_fetch_no_edinet_key_falls_back_to_tier2():
    """Without EDINET_API_KEY: memo-fetch surfaces Tier 2 fallback envelope."""
    out = _run_pack(
        ["--ticker", JP_TICKER, "--pack", "memo-fetch"],
        extra_env={"EDINET_API_KEY": None},  # explicitly unset
        timeout=600,
    )
    assert out["pack"] == "memo-fetch"
    assert out["ticker"] == "7203"
    assert out["yf_ticker"] == "7203.T"

    fundamentals = out.get("fundamentals")
    assert isinstance(fundamentals, dict)
    assert fundamentals.get("tier") == "tier_2"
    assert fundamentals.get("tier_label") == "Tier 2 fallback"
    assert "annual" in fundamentals
    assert "quarterly" in fundamentals

    prov = out.get("_provenance", {})
    assert prov.get("tier_label") == "Tier 2 fallback"
    upgrade = prov.get("upgrade_hint", "")
    assert "EDINET_API_KEY" in upgrade
    assert "edinet" in upgrade.lower()
    assert "http" in upgrade


@pytest.mark.network
def test_jp_comps_multiples_single():
    """comps-multiples returns tickers list with multiples block."""
    out = _run_pack(["--ticker", JP_TICKER, "--pack", "comps-multiples"], timeout=600)
    assert out["pack"] == "comps-multiples"
    tickers = out.get("tickers")
    assert isinstance(tickers, list) and len(tickers) >= 1
    block = tickers[0]
    assert block["ticker"] == "7203"
    assert block["yf_ticker"] == "7203.T"
    assert isinstance(block.get("multiples"), dict)


@pytest.mark.network
def test_jp_screener_batch():
    """screener-batch returns batch info + history."""
    out = _run_pack(["--tickers", JP_SCREENER_TICKERS, "--pack", "screener-batch"], timeout=600)
    assert out["pack"] == "screener-batch"
    assert "info_batch" in out
    assert "history_batch" in out
    assert set(out.get("yf_tickers", [])) == {f"{t}.T" for t in JP_SCREENER_TICKERS.split(",")}


@pytest.mark.network
def test_jp_regime_pack():
    """regime-pack returns BOJ + estat + ECB groups."""
    out = _run_pack(["--pack", "regime-pack", "--market", "jp"], timeout=600)
    assert out["pack"] == "regime-pack"
    groups = out.get("groups", {})
    assert {"rates", "inflation", "real_rates"}.issubset(groups.keys())
    prov = out.get("_provenance", {})
    assert prov.get("tier") == "tier_a"


# ---------------------------------------------------------------------------
# TW — 2330.TW TSMC (yfinance + MOPS + TWSE OpenAPI + FinMind + CBC/DGBAS/NDC/stat.gov.tw)
# ---------------------------------------------------------------------------

TW_TICKER = "2330.TW"
TW_SCREENER_TICKERS = "2330.TW,2454.TW,2317.TW,2412.TW,1303.TW"


@pytest.mark.network
def test_tw_snapshot_tsmc():
    out = _run_pack(["--ticker", TW_TICKER, "--pack", "snapshot"], timeout=900)
    assert out["pack"] == "snapshot"
    assert out["country"] == "TW"
    assert out["ticker"] == TW_TICKER
    norm = out.get("_normalized", {})
    assert norm.get("ticker_code") == "2330"
    assert norm.get("market") == "sii"
    for group in ("yfinance", "mops", "twse", "finmind"):
        assert group in out, f"snapshot missing {group} group"


@pytest.mark.network
def test_tw_memo_fetch_tsmc():
    out = _run_pack(["--ticker", TW_TICKER, "--pack", "memo-fetch"], timeout=900)
    assert out["pack"] == "memo-fetch"
    assert out["country"] == "TW"
    mops = out.get("mops", {})
    for extra in ("cash_flow", "monthly_revenue", "dividends",
                  "director_holdings", "insider_trades", "announcements"):
        assert extra in mops, f"memo-fetch missing mops.{extra}"
    twse = out.get("twse", {})
    assert "three_investor" in twse
    assert "stock_day_history" in twse, "sii memo-fetch should include TWSE OHLCV"


@pytest.mark.network
def test_tw_comps_multiples_single():
    out = _run_pack(["--ticker", TW_TICKER, "--pack", "comps-multiples"], timeout=900)
    assert out["pack"] == "comps-multiples"
    assert out["country"] == "TW"
    assert TW_TICKER in out.get("tickers", {})
    block = out["tickers"][TW_TICKER]
    assert block.get("_source") == "yfinance"
    assert block.get("_action") == "info-multiples"


@pytest.mark.network
def test_tw_screener_batch():
    out = _run_pack(["--tickers", TW_SCREENER_TICKERS, "--pack", "screener-batch"], timeout=900)
    assert out["pack"] == "screener-batch"
    assert out["country"] == "TW"
    assert isinstance(out.get("yfinance"), dict)
    assert "info_batch" in out["yfinance"]
    assert "history_batch" in out["yfinance"]
    mops = out.get("mops", {})
    for t in TW_SCREENER_TICKERS.split(","):
        assert t in mops, f"screener-batch missing mops.{t}"


@pytest.mark.network
def test_tw_regime_pack():
    out = _run_pack(["--pack", "regime-pack", "--market", "tw"], timeout=900)
    assert out["pack"] == "regime-pack"
    assert out["country"] == "TW"
    for group in ("cbc", "dgbas", "ndc", "statgov"):
        assert group in out, f"regime-pack missing {group} group"


# ---------------------------------------------------------------------------
# KR — 005930.KS Samsung (yfinance + BOK ECOS-KEYSTAT via FinanceDataReader)
# ---------------------------------------------------------------------------

KR_TICKER = "005930.KS"
KR_SCREENER_TICKERS = "005930.KS,000660.KS,005380.KS,051910.KS,068270.KS"


@pytest.mark.network
def test_kr_snapshot_samsung():
    """Snapshot returns the raw yfinance envelope under `price_history`
    (dict) AND a T1-canonical OHLCV list under `history` (list of
    `{date, open, high, low, close, volume}` records). Fixed per ROADMAP
    §v2.1.x-g.
    """
    out = _run_pack(["--ticker", KR_TICKER, "--pack", "snapshot"], timeout=600)
    assert out["pack"] == "snapshot"
    assert out["country"] == "kr"
    assert out["ticker"] == KR_TICKER
    assert isinstance(out.get("info"), dict)
    assert isinstance(out.get("price_history"), dict), (
        f"snapshot missing price_history (raw yfinance envelope); "
        f"top keys: {sorted(out.keys())}"
    )
    history = out.get("history")
    assert isinstance(history, list), (
        f"snapshot.history must be a list of OHLCV records "
        f"(cross-country symmetric T1 alias), got {type(history).__name__}"
    )
    assert history, "snapshot.history is empty"
    first = history[0]
    for field in ("date", "open", "high", "low", "close", "volume"):
        assert field in first, (
            f"history[0] missing field {field!r}; got keys {sorted(first.keys())}"
        )
    prov = out.get("_provenance", {})
    assert "Tier 2" in prov.get("tier", "")


@pytest.mark.network
def test_kr_memo_fetch_samsung_tier_2():
    """Korea memo-fetch is Tier 2 only (DART deferred)."""
    out = _run_pack(["--ticker", KR_TICKER, "--pack", "memo-fetch"], timeout=600)
    assert out["pack"] == "memo-fetch"
    assert out["tier"] == "Tier 2 only"
    assert "financials_annual" in out
    assert "financials_quarterly" in out
    prov = out.get("_provenance", {})
    assert prov.get("primary_source_status") == "deferred"


@pytest.mark.network
def test_kr_comps_multiples_single():
    out = _run_pack(["--ticker", KR_TICKER, "--pack", "comps-multiples"], timeout=600)
    assert out["pack"] == "comps-multiples"
    info = out.get("info", {})
    assert KR_TICKER in info, f"comps-multiples missing ticker {KR_TICKER}"


@pytest.mark.network
def test_kr_screener_batch():
    out = _run_pack(["--tickers", KR_SCREENER_TICKERS, "--pack", "screener-batch"], timeout=600)
    assert out["pack"] == "screener-batch"
    assert set(out["tickers"]) == set(KR_SCREENER_TICKERS.split(","))
    assert "batch" in out


@pytest.mark.network
def test_kr_regime_pack():
    """BOK ECOS-KEYSTAT via fdr_client. The old CLI's `--indicators
    rates,inflation` restriction has no facade equivalent (dropped flag, see
    module docstring) — this now fetches the full default group set and
    asserts rates + inflation are present within it, preserving the
    original assertion's intent without the removed restriction flag."""
    out = _run_pack(["--pack", "regime-pack", "--market", "kr"], timeout=600)
    assert out["pack"] == "regime-pack"
    assert out["country"] == "kr"
    assert {"rates", "inflation"}.issubset(set(out["groups_requested"]))
    data = out.get("data", {})
    assert "rates" in data
    assert "inflation" in data
    prov = out.get("_provenance", {})
    assert prov.get("primary_source_status") == "available"


# ---------------------------------------------------------------------------
# CN — 600519.SS Kweichow Moutai (yfinance + NBS + akshare + FRED USDCNY)
# ---------------------------------------------------------------------------

CN_TICKER = "600519.SS"
CN_SCREENER_TICKERS = "600519.SS,000858.SZ,601318.SS,000333.SZ,300750.SZ"


@pytest.mark.network
def test_cn_snapshot_moutai():
    out = _run_pack(["--ticker", CN_TICKER, "--pack", "snapshot"], timeout=900)
    assert out["pack"] == "snapshot"
    assert out["country"] == "CN"
    assert out["ticker"] == CN_TICKER
    assert "yfinance_info" in out
    assert "yfinance_history" in out


@pytest.mark.network
def test_cn_memo_fetch_moutai_tier_2():
    out = _run_pack(["--ticker", CN_TICKER, "--pack", "memo-fetch"], timeout=900)
    assert out["pack"] == "memo-fetch"
    prov = out.get("_provenance", {})
    assert prov.get("tier") == 2
    assert prov.get("primary_source_status") == "deferred"
    assert "yfinance_financials_annual" in out
    assert "yfinance_financials_quarterly" in out


@pytest.mark.network
def test_cn_comps_multiples_single():
    out = _run_pack(["--ticker", CN_TICKER, "--pack", "comps-multiples"], timeout=900)
    assert out["pack"] == "comps-multiples"
    tickers = out.get("tickers", [])
    assert isinstance(tickers, list) and len(tickers) >= 1
    block = tickers[0]
    assert block["ticker"] == CN_TICKER
    assert "multiples" in block


@pytest.mark.network
def test_cn_screener_batch():
    out = _run_pack(["--tickers", CN_SCREENER_TICKERS, "--pack", "screener-batch"], timeout=900)
    assert out["pack"] == "screener-batch"
    assert set(out["tickers"]) == set(CN_SCREENER_TICKERS.split(","))
    assert "yfinance_info_batch" in out
    assert "yfinance_history_batch" in out


@pytest.mark.network
def test_cn_regime_pack():
    """NBS (21) + akshare PBOC/Caixin (8) + FRED USDCNY composition."""
    out = _run_pack(["--pack", "regime-pack", "--market", "cn"], timeout=900)
    assert out["pack"] == "regime-pack"
    assert out["country"] == "CN"
    for source in ("nbs", "akshare", "fred", "markets"):
        assert source in out, f"regime-pack missing {source} source"
    prov = out.get("_provenance", {})
    assert isinstance(prov.get("nbs_indicators"), list)
    assert isinstance(prov.get("akshare_indicators"), list)
    assert isinstance(prov.get("fred_series"), list)
