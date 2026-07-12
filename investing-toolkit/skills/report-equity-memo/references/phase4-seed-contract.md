# Phase 4 seed contract — verdict-layer defenses

> Toolkit-owned. Phase 4's delegation packet MUST carry the five elements
> below, and the orchestrator MUST verify the returned memo against them
> before accepting the Phase 4 artifact. Elements 1-4 origin: 2026-07-12
> strong-vs-weak model comparison on identical pipeline data (plan:
> `docs/loom/plans/2026-07-12-verdict-layer-defenses.md`) — the weak run
> deviated from the DCF verdict rule with an unsourced uplift, claimed
> present data was unavailable, dropped upstream warnings, and stamped the
> memo with the fetch's UTC date. Element 5 origin: 2026-07-13 whole-branch
> review 🟡 F2 — the US SEC narrative fetch shipped with no memo-side
> instruction to read it. Each element closes one observed hole.

## 1. `rule_verdict` — adopt or file a Deviation Block

`analysis-dcf` output (`dcf.json` → `verdict_thresholds.rule_verdict` +
`rule_verdict_basis`) carries the machine-computed application of the DCF
verdict rule to the current price. The packet MUST quote it in the seed
context, marked **binding-or-gated**:

- The memo adopts `rule_verdict`, or files a **Deviation Block** per the
  investing-team protocol (`protocols/deep-equity-research-memo.md`
  §Verdict). A deviation whose recomputed thresholds still trigger the
  original `rule_verdict` is arithmetically void; the thesis-soundness
  gate (CHK-THX-007) enforces this by recomputation.
- If `rule_verdict` is null (no current price), say so in the packet —
  the memo then derives its verdict per the protocol as before.

## 2. Pack-section inventory — unavailability claims are checkable

Before dispatch, generate the inventory and include its JSON in the packet:

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/report-equity-memo/scripts/pack_inventory.py \
    --input /tmp/${TICKER_SAFE}-fetch.json > /tmp/${TICKER_SAFE}-inventory.json
```

Packet clause: "Any claim that a data section is unavailable/missing MUST be
consistent with this inventory; the citation-compliance gate (CHK-CIT-007)
cross-checks against it." A `_status: partial` with named `failed_sections`
does not license writing off sections the inventory shows present.

## 3. Date anchoring — issuer timezone, reference periods

- Memo date = the **execution date in the issuer's market timezone** (e.g.
  Asia/Taipei for `.TW`) — never a `fetched_at`/`computed_at` UTC stamp
  from the data files (same clock-mismatch class as PR #543).
- Every price/figure cites its **reference period** (e.g. "TWSE close
  2026-07-09"), never the fetch timestamp. yfinance delay wording does not
  substitute for the authoritative close date.

## 4. Mandatory disclosures — verbatim transcription is the pass bar

The packet lists the run's mandatory disclosures (fetch `_status`, DCF
parameter caveats, comps `warnings[]`, scope exclusions, Phase 0 recall
outcome). Pass criterion, stated in the packet: **transcribe upstream
`_status`/`warnings` content at verbatim grade** — no silent dropping,
softening, or relabeling (FY→"TTM" relabeling is the canonical fail).
Enforced by CHK-CIT-007.

## 5. `sec_narrative` — read before you cite

`fetch.sec_narrative.filings[]` (US tickers only) is where management's
own filed words live: each filing carries `role` (`10-K`/`10-Q`/`8-K`,
plus `quarter` for 8-Ks) and `sections[]`; each section carries `item`,
a `text_path`, `disclosure_status`, and provenance (`accession`, `cik`,
`filingDate`, a reconstructable SEC Archives `url`). **`text_path` is a
path, not text — the section body sits on disk at that path; the pack
does not carry it.**

- **Iron rule**: read the file at `text_path` before quoting or citing
  that item. Citing an item's provenance/`url` without having opened its
  `text_path` is fabrication — the exact class CHK-CIT-007 exists to
  catch.
- **`disclosure_status` matters**: `"filed"` (10-K/10-Q sections) vs
  `"furnished"` (8-K Exhibit 99.x — a different §18 liability standard).
  Weight or label a claim resting on furnished material accordingly;
  this is a shipped producer field, not new policy.
- **Failure signal is depth-1 only**: check the wrapper's own `_status`
  and `failed_items` — never infer completeness by walking `sections`.
  Also: `succeeded` counts filings obtained, not sections extracted — a
  filing fetched with its own `narrative_status: "partial"` still counts
  as succeeded, so `succeeded + failed == requested` can reconcile clean
  while some section text is missing. §4's verbatim-transcription rule
  already covers transcribing that gap.

## Orchestrator acceptance check (before Phase 4 artifact gate)

On receiving the memo: (a) grep the Verdict section for `rule_verdict` —
absent, or deviating without a Deviation Block → send back, do not accept;
(b) spot-check any "data unavailable" sentence against the inventory;
(c) confirm the memo date matches the issuer-timezone execution date.
These are orchestrator-side cheap greps, not a re-run of the gates.
