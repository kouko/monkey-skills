# Phase 4 seed contract — verdict-layer defenses

> Toolkit-owned. Phase 4's delegation packet MUST carry the six elements
> below, and the orchestrator MUST verify the returned memo against them
> before accepting the Phase 4 artifact. Elements 1-4 origin: 2026-07-12
> strong-vs-weak model comparison on identical pipeline data (plan:
> `docs/loom/plans/2026-07-12-verdict-layer-defenses.md`) — the weak run
> deviated from the DCF verdict rule with an unsourced uplift, claimed
> present data was unavailable, dropped upstream warnings, and stamped the
> memo with the fetch's UTC date. Element 5 origin: 2026-07-13 whole-branch
> review 🟡 F2 — the US SEC narrative fetch shipped with no memo-side
> instruction to read it. Element 6 origin: 2026-07-13 US SEC financial-
> table cross-validation wiring (plan: `docs/loom/plans/2026-07-13-us-sec-
> financial-table-xval.md`) — the xval compute layer surfaces doc-vs-XBRL
> divergences and doc-only findings, but nothing told the memo writer to
> read them before citing a number. Each element closes one observed hole.

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

## 6. `xval` — read before you cite a financial number

`analysis-xval`'s report (US tickers with a filed statement, only) carries
`comparisons` (every matched doc-vs-XBRL cell pair), `high_alerts` (the
subset of `comparisons` with `alert == "high"`, surfaced a second time,
verbatim), and `single_source` (doc-only cells with no XBRL counterpart,
plus `decimal-disagreement (DQC 2.4.1)` and `restatement-signal`
findings). Each entry's `source_mode` is `"two-source"` (independently
matched to XBRL) or `"single-source"` (no independent cross-check
happened).

- **Iron rule**: before citing a statement-table number in the memo,
  check whether that `(concept, period, dimension)` appears in
  `high_alerts`. If it does, the memo MUST surface the divergence — show
  BOTH `doc_value` and `xbrl_value` — and weight or challenge the number
  accordingly, rather than citing the doc figure alone as if it were
  uncontested.
- **Respect `source_mode`**: a `"two-source"` figure was independently
  cross-validated (doc-table cell vs an independent companyfacts fact). A
  `"single-source"` finding was NOT — it is either a structural check on
  one filing's own tags (doc-only, `decimal-disagreement (DQC 2.4.1)`) or a
  cross-FILING XBRL comparison (`restatement-signal`, which cites
  `earlier_accn`/`later_accn` and `earlier_value`/`later_value`, not a
  `doc_value`/`xbrl_value` pair). Do not present a single-source finding
  with the same confidence as a two-source one.
- **A doc-only cell is un-cross-validated, not confirmed**: a
  `single_source` entry with `status: "doc-only, no XBRL counterpart"`
  means the cell could not be matched to a companyfacts fact at all —
  state that plainly ("not independently verified against XBRL"), don't
  imply XBRL agreement was checked and passed.
- **Failure signal is depth-1 only** (mirrors §5): trust `high_alerts`
  and `single_source` as already-computed — never re-derive alert
  levels by walking `comparisons` and re-checking thresholds yourself.
  `analysis-xval` has no partial-report mode (a bad `--source-a`/`-b`
  path exits 2 with no report emitted at all — SKILL.md `## CLI`), so
  an empty `high_alerts` means no high-divergence pairs were found, not
  a truncated run.

## Optional input: kpi quarterly memo feed (Phase 3.5, US tickers only)

Not a seventh defense element — an OPTIONAL Resource Paths entry the six
elements' disciplines already cover. When Phase 3.5 ran, the packet's
`### Resource Paths` includes `/tmp/${TICKER_SAFE}-kpi-quarterly-feed.json`
— the `kpi_memo_feed.py build-quarterly` output (memo-feed envelope 1.1,
`status: "TRUSTED"`, fail-closed: the CLI exits 1 instead of emitting a
degraded feed). The memo's Operating-KPI section consumes ONLY this feed
— never recomputed raw facts (investing-team protocol owns the rendering
rules).

**Skip-note contract (non-US, or a loud Phase 3.5 failure)**: the feed
path is omitted and the seed context carries an explicit skip note (e.g.
"kpi-quarterly-feed skipped: non-US ticker, dimensional-XBRL lane is
US-only") — absence is never silent, mirroring the Phase 2.6 xval skip
discipline. §4's verbatim-transcription bar applies to the skip note's
reason text.

## Orchestrator acceptance check (before Phase 4 artifact gate)

On receiving the memo: (a) grep the Verdict section for `rule_verdict` —
absent, or deviating without a Deviation Block → send back, do not accept;
(b) spot-check any "data unavailable" sentence against the inventory;
(c) confirm the memo date matches the issuer-timezone execution date;
(d) if the run carried an xval report, spot-check any statement-table
number cited in the memo against `high_alerts` — a `high`-alert number
cited without surfacing both values → send back, do not accept;
(e) if the run carried a kpi quarterly feed, confirm the memo's
Operating-KPI content cites the feed's values (derived-Q4 cells tagged,
coverage gaps footnoted) rather than recomputing from raw facts; if
Phase 3.5 was skipped, grep the memo's Limitations section for the skip
note — a silent absence → send back, do not accept.
These are orchestrator-side cheap greps, not a re-run of the gates.
