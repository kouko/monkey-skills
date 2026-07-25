"""Regenerate `us_statement_shapes_probe_2026-07-26.json` — the live
grounding capture behind the §Probe evidence numbers in
`docs/loom/specs/2026-07-26-us-as-reported-statement-lane.md`.

WHAT IT ANSWERS. That brief's case for an as-reported statement lane rests
on five claims about the SHAPE of real filers' `companyfacts` — none
settleable from in-repo fixtures because they are claims about what SEC
XBRL tagging actually looks like across a broad filer sample:
(1) does `ticker -> CIK` resolution ever land on a decoy entity carrying
zero us-gaap concepts (measured: XOM); (2) for the 14-field spine, which
candidate concept each filer actually tags, and whether the NAIVE
per-company first-present winner is silently stale versus the best concept
available anywhere in the filer's history (M2/M3 below) — the specific
instance this fixture pins is `total_liabilities`, which 13 filers never
tag at all under ANY chain concept; (3) did the PRE-Task-2 shipped
`build_top_line_backfill` (Lane A, `sec_edgar_client.py:2788`, baseline
commit `3ee2fcd3` — see "M4 BASELINE" below) truncate a filer's revenue
series short of what the chain-wide best concept can serve, and for how
many filers (M4); (4) does the balance identity
`A = L + mezzanine + E` reconcile once the mezzanine (temporary-equity) term
is included; (5) how many usable fiscal years (>=10/14 spine fields, 10-K-
carried) does the corpus actually have (M5) — the floor the plan's Task 10
must document as a capability limit. Only shapes/counts are captured here;
this fixture never stores per-fact financial values beyond the specific
identity/staleness aggregates each measurement needs.

Selection logic is a straight vendored copy of this session's discovery
probe (drafts, not committed) — `_rows_of`/`_newest_end`/`_latest_instant`/
`_instant_at` mirror the scratchpad `probe47.py`; `_usable_years` mirrors
the scratchpad `history_depth.py`. These measure against `sec_edgar_client`
functions already shipped (`resolve_cik`, `fetch_facts`) — no new
production code is exercised by this script, it only reads what those
functions already return, EXCEPT M4 (`_shipped_lane_truncation`), which is
scored against a frozen vendored copy rather than a live function — see
"M4 BASELINE" below.

M4 BASELINE. `_shipped_lane_truncation` (M4) is scored against a FROZEN
vendored copy of `build_top_line_backfill`'s pre-Task-2 concept selector
(`_legacy_top_line_winner`, below), pinned to this branch's base commit
`3ee2fcd3` — NEVER the live `sec.build_top_line_backfill` import. Task 2
of this same arc rewrites that live function's selection from per-company
first-hit to per-period resolution specifically because the per-company
rule truncates switched-tag filers (see `_legacy_top_line_winner`'s
docstring); a "current" M4 that called the live function would silently
stop reproducing the committed 10-filers-truncated number the moment
Task 2 lands, with nothing surfacing the drift. The captured
`n_filers_shipped_lane_truncated_1y_or_more` is therefore a POINT-IN-TIME
baseline against commit `3ee2fcd3`, deliberately invalidated for the LIVE
function by this arc's own Task 2 — re-verify by diffing
`_legacy_top_line_winner` against `git show 3ee2fcd3:investing-toolkit/
skills/data-markets/scripts/sec_edgar_client.py`'s `build_top_line_backfill`
if this number is ever questioned.

NETWORK. Hits `data.sec.gov` live via `sec_edgar_client.fetch_facts` /
`resolve_cik`; NOT part of the offline suite (it is not a `test_*` module
and pytest never collects it). Each filer's companyfacts response is
cached by `sec_edgar_client`'s own `cache_util`-backed `TTL_FACTS` cache,
so a re-run against a warm cache is almost entirely cache hits — same
fair-access posture as the sibling probe scripts. Re-run by hand when the
probe evidence is questioned:

    PYTHONDONTWRITEBYTECODE=1 python3 investing-toolkit/tests/data/fixtures/\\
      capture_us_statement_shapes_probe.py > \\
      investing-toolkit/tests/data/fixtures/\\
      us_statement_shapes_probe_2026-07-26.json

FILER SAMPLE. The SAME 47 US filers as the kpi_id arc's probe — imported
verbatim from `capture_kpi_id_identity_probe.TICKERS`, never re-authored
here, so this fixture and that one are provably grounded in one corpus. See
that module's docstring FILER SAMPLE section for the per-sector rationale
(energy majors, money-center banks, tech/consumer megacaps, retail, staples/
healthcare, industrials/autos/telecom).
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

_HERE = Path(__file__).resolve()
_FIXTURES_DIR = _HERE.parent
_REPO_ROOT = _HERE.parents[4]
_DATA_MARKETS_SCRIPTS = _REPO_ROOT / "investing-toolkit" / "skills" / "data-markets" / "scripts"
sys.path.insert(0, str(_DATA_MARKETS_SCRIPTS))
sys.path.insert(0, str(_FIXTURES_DIR))
import sec_edgar_client as sec  # noqa: E402
from capture_kpi_id_identity_probe import TICKERS  # noqa: E402 — reused verbatim, see module docstring

sec._QUIET = True

# --- spine field chains ------------------------------------------------
# Verbatim transcription of the plan's ## Notes "PIN — spine field chains"
# (docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md). Order is
# the same-period tiebreak this probe measures staleness against, never a
# per-company winner.
SPINE: dict[str, tuple[str, ...]] = {
    "revenue": (
        "Revenues", "RevenuesNetOfInterestExpense",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueNet",
    ),
    "gross_profit": ("GrossProfit",),
    "operating_income": ("OperatingIncomeLoss",),
    "pretax_income": (
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments",
        "IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic",
    ),
    "net_income": ("NetIncomeLoss", "ProfitLoss"),
    "eps_basic": ("EarningsPerShareBasic", "IncomeLossFromContinuingOperationsPerBasicShare"),
    "total_assets": ("Assets",),
    "total_liabilities": ("Liabilities",),
    "total_equity": (
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ),
    "cash": (
        "CashAndCashEquivalentsAtCarryingValue",
        "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "Cash",
    ),
    "operating_cash_flow": (
        "NetCashProvidedByUsedInOperatingActivities",
        "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
    ),
    "investing_cash_flow": (
        "NetCashProvidedByUsedInInvestingActivities",
        "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations",
    ),
    "financing_cash_flow": (
        "NetCashProvidedByUsedInFinancingActivities",
        "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations",
    ),
    "capex": (
        "PaymentsToAcquirePropertyPlantAndEquipment",
        "PaymentsToAcquireProductiveAssets",
        "PaymentsToAcquirePropertyPlantAndEquipmentAndIntangibleAssets",
    ),
}

# Identity components used only by the balance-identity measurement
# (fetched alongside the spine, not themselves spine fields).
_MEZZANINE_CONCEPTS = (
    "TemporaryEquityCarryingAmountIncludingPortionAttributableToNoncontrollingInterests",
    "RedeemableNoncontrollingInterestEquityCarryingAmount",
)

_USABLE_YEAR_FIELD_FLOOR = 10  # of 14 spine fields present (10-K-carried) in one fiscal year
_USABLE_HISTORY_YEARS_FLOOR = 20


def _rows_of(facts: dict, tag: str, form: str | None = "10-K") -> list[dict]:
    """All `us-gaap:{tag}` rows across every unit, optionally filtered to
    one carrier `form` (None = every form)."""
    obj = (facts.get("us-gaap") or {}).get(tag)
    if not obj:
        return []
    out = []
    for unit, rows in (obj.get("units") or {}).items():
        for row in rows:
            if form is None or row.get("form") == form:
                out.append({**row, "_unit": unit})
    return out


def _newest_end(facts: dict, tag: str) -> str | None:
    ends = [r["end"] for r in _rows_of(facts, tag) if r.get("end")]
    return max(ends) if ends else None


def _latest_instant(facts: dict, tag: str) -> dict | None:
    rows = [r for r in _rows_of(facts, tag) if r.get("start") is None and r.get("end")]
    return max(rows, key=lambda r: (r["end"], r.get("filed", ""))) if rows else None


def _instant_at(facts: dict, tag: str, end: str) -> dict | None:
    rows = [r for r in _rows_of(facts, tag) if r.get("start") is None and r.get("end") == end]
    return max(rows, key=lambda r: r.get("filed", "")) if rows else None


def _field_coverage(facts: dict) -> dict[str, dict]:
    """M2/M3 per spine field: the NAIVE per-company first-present winner
    (10-K rows, any form initially considered across the whole chain) vs
    the chain-wide BEST concept's newest 10-K end — the gap is the naive
    rule's staleness in years."""
    out = {}
    for field, chain in SPINE.items():
        winner = None
        for tag in chain:
            if _rows_of(facts, tag, form=None):
                winner = tag
                break
        naive_end = _newest_end(facts, winner) if winner else None
        best_tag, best_end = None, None
        for tag in chain:
            end = _newest_end(facts, tag)
            if end and (best_end is None or end > best_end):
                best_tag, best_end = tag, end
        out[field] = {
            "winner": winner,
            "winner_newest_10k_end": naive_end,
            "best_tag": best_tag,
            "best_newest_10k_end": best_end,
            "stale_years": (
                int(best_end[:4]) - int(naive_end[:4])
                if (naive_end and best_end) else None
            ),
        }
    return out


def _balance_identity(facts: dict) -> dict:
    """A = L + mezzanine + E at the latest Assets instant, mezzanine
    (temporary equity) term included per the plan's Decision."""
    assets = _latest_instant(facts, "Assets")
    if assets is None:
        return {"checkable": False, "reason": "no Assets 10-K instant"}
    end = assets["end"]
    liabilities = _instant_at(facts, "Liabilities", end)
    if liabilities is None:
        return {"checkable": False, "period_end": end,
                "reason": "filer never tags total 'Liabilities'"}
    equity_incl = _instant_at(
        facts, "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", end,
    )
    equity_parent = _instant_at(facts, "StockholdersEquity", end)
    equity, equity_kind = (
        (equity_incl, "incl_NCI") if equity_incl else (equity_parent, "parent_only")
    )
    if equity is None:
        return {"checkable": False, "period_end": end, "reason": "no equity total at that instant"}
    equity_val = equity["val"]
    minority = _instant_at(facts, "MinorityInterest", end)
    if equity_kind == "parent_only" and minority is not None:
        equity_val += minority["val"]
        equity_kind = "parent_plus_MI"
    mezzanine = None
    for concept in _MEZZANINE_CONCEPTS:
        mezzanine = _instant_at(facts, concept, end)
        if mezzanine is not None:
            break
    mezzanine_val = mezzanine["val"] if mezzanine else 0.0
    residual = assets["val"] - (liabilities["val"] + equity_val + mezzanine_val)
    return {
        "checkable": True,
        "period_end": end,
        "equity_kind": equity_kind,
        "mezzanine_used": bool(mezzanine),
        "assets": assets["val"],
        "residual": residual,
        "residual_rel": abs(residual) / assets["val"] if assets["val"] else None,
    }


def _usable_years(facts: dict) -> dict:
    """M5: fiscal years where >=_USABLE_YEAR_FIELD_FLOOR of the 14 spine
    fields have a 10-K-carried observation ending that year."""
    fields_by_year: dict[str, set] = defaultdict(set)
    ends: list[str] = []
    for field, chain in SPINE.items():
        for tag in chain:
            for row in _rows_of(facts, tag, form="10-K"):
                end = row.get("end")
                if end:
                    ends.append(end)
                    fields_by_year[end[:4]].add(field)
    usable = sorted(year for year, present in fields_by_year.items()
                     if len(present) >= _USABLE_YEAR_FIELD_FLOOR)
    return {
        "earliest_fact_end": min(ends) if ends else None,
        "latest_fact_end": max(ends) if ends else None,
        "usable_years": len(usable),
        "first_usable_year": usable[0] if usable else None,
        "last_usable_year": usable[-1] if usable else None,
    }


# --- FROZEN legacy top-line concept selector (pre-Task-2 baseline,
# commit `3ee2fcd3`) ---------------------------------------------------
# This block is a HISTORICAL RECORD of what `build_top_line_backfill`'s
# concept SELECTION did across the corpus before Task 2 of THIS SAME arc
# (docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md) rewrote it
# from per-company first-hit to per-period resolution
# (`_resolve_concept_per_period`, sec_edgar_client.py). It must never be
# pointed at the live function, and never "kept in sync" with it — see
# `_legacy_top_line_winner`'s docstring for why syncing would silently
# break this script's own regenerate command. Mirrors
# `capture_kpi_id_identity_probe._legacy_kpi_id`'s frozen-copy shape and
# rationale — that arc hit the identical hazard (a sibling task in the
# same wave rewriting the exact function a probe measures).


def _legacy_top_line_winner(facts: dict) -> str | None:
    """FROZEN reproduction of `build_top_line_backfill`'s concept
    SELECTION exactly as it behaved at the pre-Task-2 baseline commit
    `3ee2fcd3`: scan the top-line allowlist IN ORDER and return the FIRST
    concept that has ANY row (any form) — a per-company winner-take-all
    pick, replaced by Task 2's per-period resolution. Deliberately NOT
    wired to the live `build_top_line_backfill` import — a live call would
    silently stop reproducing this fixture's committed M4 numbers once
    Task 2 lands, exactly the drift `_legacy_kpi_id` was frozen to avoid
    on the sibling kpi_id arc.

    The concept UNIVERSE (`sec._TOP_LINE_REVENUE_CONCEPTS`) stays imported
    LIVE: Task 2 does not touch that tuple, only the algorithm that picks
    among its members — same split `capture_kpi_id_identity_probe` makes
    between live-imported selector-building and frozen id-derivation.

    Operates on the already-fetched `companyfacts` payload (`_rows_of`,
    `form=None` — "any form", matching the pre-fix loop's
    `summarize_concept` check, which does not itself filter by form)
    rather than re-fetching via `companyconcept`: both endpoints serve the
    same underlying facts, and reusing the payload this probe already
    fetched for M2/M3 avoids a second SEC round-trip per ticker.

    Verified against `git show 3ee2fcd3:investing-toolkit/skills/
    data-markets/scripts/sec_edgar_client.py`'s `build_top_line_backfill`
    (the `for concept in _TOP_LINE_REVENUE_CONCEPTS: ... if
    candidate_rows: winning_concept = concept; break` loop)."""
    for concept in sec._TOP_LINE_REVENUE_CONCEPTS:
        if _rows_of(facts, concept, form=None):
            return concept
    return None


def _shipped_lane_truncation(facts: dict, field_coverage: dict) -> dict:
    """M4: does the PRE-Task-2 per-company top-line concept selector
    (frozen `_legacy_top_line_winner`, baseline commit `3ee2fcd3`) emit a
    revenue series that ends earlier than the chain-wide best revenue
    concept could serve? This is a POINT-IN-TIME baseline against that
    commit, deliberately invalidated for the LIVE `build_top_line_backfill`
    by Task 2 of this same arc — see module docstring "M4 baseline" note."""
    winner = _legacy_top_line_winner(facts)
    if winner is None:
        return {"error": (
            "no concept in sec._TOP_LINE_REVENUE_CONCEPTS returned any "
            "companyconcept rows"
        )}
    last = _newest_end(facts, winner)
    best_end = field_coverage["revenue"]["best_newest_10k_end"]
    years_lost = (
        int(best_end[:4]) - int(last[:4]) if (best_end and last) else None
    )
    return {
        "legacy_winning_concept": winner,
        "last_period_end": last,
        "years_lost_vs_chain_best": years_lost,
    }


def _probe_one(ticker: str) -> dict:
    cik_info = sec.resolve_cik(ticker)
    if "error" in cik_info:
        return {"ticker": ticker, "error": cik_info["error"]}
    cik = cik_info["cik"]
    fetched = sec.fetch_facts(cik, None)
    if "error" in fetched:
        return {"ticker": ticker, "cik": cik, "error": fetched["error"]}
    data = fetched.get("data") or {}
    facts = data.get("facts") or {}
    us_gaap_tags = len(facts.get("us-gaap") or {})
    field_coverage = _field_coverage(facts)
    return {
        "ticker": ticker,
        "cik": cik,
        "entity_name": data.get("entityName"),
        "us_gaap_tags": us_gaap_tags,
        "fields": field_coverage,
        "identity": _balance_identity(facts) if us_gaap_tags else {
            "checkable": False, "reason": "0 us-gaap concepts",
        },
        "history": _usable_years(facts) if us_gaap_tags else {
            "usable_years": 0, "earliest_fact_end": None, "latest_fact_end": None,
            "first_usable_year": None, "last_usable_year": None,
        },
        "shipped_lane": _shipped_lane_truncation(facts, field_coverage),
    }


def main() -> None:
    results = [_probe_one(ticker) for ticker in TICKERS]

    # "clean" = excludes the one decoy CIK with 0 us-gaap concepts (XOM) —
    # the ONLY exclusion the brief's per-field/per-history rates apply
    # (§Probe evidence: "one filer (XOM) resolves to an entity with 0
    # us-gaap concepts and is excluded from per-field rates (n=46)").
    clean = [r for r in results if "error" not in r and r["us_gaap_tags"] > 0]

    usable_years_list = [r["history"]["usable_years"] for r in clean]
    truncated = [
        r["ticker"] for r in clean
        if isinstance(r["shipped_lane"].get("years_lost_vs_chain_best"), int)
        and r["shipped_lane"]["years_lost_vs_chain_best"] >= 1
    ]
    liabilities_missing = [
        r["ticker"] for r in clean if r["fields"]["total_liabilities"]["winner"] is None
    ]
    checkable_identity = [r for r in clean if r["identity"].get("checkable")]
    balancing_identity = [
        r for r in checkable_identity
        if r["identity"]["residual_rel"] is not None and r["identity"]["residual_rel"] < 1e-5
    ]

    summary = {
        "n_filers_probed": len(TICKERS),
        "n_filers_errored": sum(1 for r in results if "error" in r),
        "n_filers_zero_us_gaap_concepts": sum(
            1 for r in results if "error" not in r and r["us_gaap_tags"] == 0
        ),
        "n_filers_clean": len(clean),
        "n_filers_never_tagging_total_liabilities": len(liabilities_missing),
        "filers_never_tagging_total_liabilities": sorted(liabilities_missing),
        "n_filers_shipped_lane_truncated_1y_or_more": len(truncated),
        "filers_shipped_lane_truncated_1y_or_more": sorted(truncated),
        "n_filers_usable_history_ge_20y": sum(
            1 for y in usable_years_list if y >= _USABLE_HISTORY_YEARS_FLOOR
        ),
        "median_usable_years": (
            sorted(usable_years_list)[len(usable_years_list) // 2] if usable_years_list else None
        ),
        "n_identity_checkable": len(checkable_identity),
        "n_identity_balancing_within_1e-5_relative": len(balancing_identity),
    }
    doc = {
        "_capture": {
            "what": (
                "Live capture over the 47-ticker corpus grounding "
                "docs/loom/specs/2026-07-26-us-as-reported-statement-lane.md "
                "§Probe evidence: decoy-CIK detection, per-field concept "
                "coverage + naive-vs-chain-best staleness, the PRE-Task-2 "
                "shipped build_top_line_backfill selector's truncation "
                "(frozen, see m4_baseline_commit below), the balance "
                "identity with the mezzanine term, and usable-history depth."
            ),
            "endpoints": [
                "data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
            ],
            "captured_at": "2026-07-26",
            "m4_baseline_commit": (
                "3ee2fcd3 — M4 (_shipped_lane_truncation) is scored against "
                "_legacy_top_line_winner, a frozen reproduction of "
                "build_top_line_backfill's concept selector as it stood at "
                "this commit, NOT the live function. This arc's Task 2 "
                "deliberately rewrites the live selector (per-company "
                "first-hit -> per-period resolution); see this script's "
                "module docstring M4 BASELINE section."
            ),
            "filer_sample_rationale": (
                "Same 47-filer corpus as the kpi_id arc's probe, imported "
                "verbatim from capture_kpi_id_identity_probe.TICKERS; see "
                "that module's FILER SAMPLE docstring section."
            ),
            "regenerate": "investing-toolkit/tests/data/fixtures/capture_us_statement_shapes_probe.py",
            "note": (
                "Shapes/counts only. No per-fact financial values are "
                "captured beyond the specific identity/staleness aggregates "
                "each measurement needs."
            ),
        },
        "_summary": summary,
        "per_filer": results,
    }
    print(json.dumps(doc, indent=1))


if __name__ == "__main__":
    main()
