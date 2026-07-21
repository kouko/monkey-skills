# Brief — 8-K earnings-release semi-auto KPI intake (non-monetary double-arc, Route B first)

Date: 2026-07-19
Origin: docs/loom/BACKLOG.md §「investing-toolkit 非金錢營運 KPI 自動化 — 雙路線」(USER-COMMITTED 2026-07-19)
Design-side on-ramp: offered N/A — data-pipeline increment, no UI surface, no multi-state spec gap (consistent with prior quarterly arcs); user chose direct.

## Problem

Operational KPIs that are non-monetary (streaming memberships, store counts,
vehicle deliveries, headcount) never reach the KPI layer. The Route A census
— extended to the FULL committed verification universe (71 US filers, 142
filings; docs/loom/references/xbrl-verification-universe.md) — proved this is
a data-class gap, not a parsing gap: the headline operational metrics
investors track (NFLX memberships, PYPL active accounts, UNH enrollment,
ISRG procedures, BA total deliveries, oil&gas production volumes) have ZERO
XBRL facts across the universe — those numbers live only in 8-K
press-release / prose disclosures. The only genuine XBRL-side survivors are
a narrow physical-footprint/capacity cluster (~8-10 filers: store/restaurant/
property counts, utility MW capacity) — Route A's reduced territory. Job story: when an earnings release drops, the
user wants every disclosed operational KPI to enter the trusted KPI layer
with provenance, not just currency revenue (user: 「我不想要漏掉任何資訊」).

## Users

kouko, operating investing-toolkit's memo/KPI pipelines on US tickers;
tier-① store is the existing trust lane (human-confirmed, append-only
bitemporal, provenance-required).

## Smallest End State

A semi-auto intake producer: given a ticker's earnings 8-K, machine-parse the
press-release exhibit's HTML tables → candidate KPI points
`{kpi_id, label, value, unit, period, source_accession, source_table_id,
source_cell_ref}` → present candidates to the human → confirmed points append
via the EXISTING `kpi_store.append()` (schema untouched, confirm-all gate
untouched). v1 ships the generic table walker + one filer exercised
end-to-end (NFLX), with the label-proposal step honest about being
filer-vocabulary work.

## Current State Evidence

- **Forward**: 8-K acquisition exists — `fetch_narrative_sections` /
  `_segment_8k` (sec_edgar_client.py ~:1060–1190). LOOM-SIMPLIFY ≥2-exhibit
  ceiling confirmed tripping on a REAL NFLX 8-K (acc 0001065280-25-000033,
  items 2.02+8.01) — but the spike bypassed `_segment_8k` entirely via
  `filing.attachments` / `obj.press_releases`, the natural route for a
  table parser (wants whole exhibit, not per-item text).
- **Reverse**: tier-① intake = `kpi_store.append(point)` keyed
  `(company, kpi_id, period, as_of)`; REQUIRES `value`, `unit`,
  `source_accession`, `source_table_id`, `source_cell_ref` (rejects if
  absent); dedup on the 5-tuple; append-only bitemporal
  (analysis-kpi/scripts/kpi_store.py). `kpi_schema.py`'s `propose()`
  contract already expects `{kpi_id, label, unit, locate_hint}` produced
  upstream — Route B is a new producer for an existing socket.
- **Error**: missing-provenance rejection already enforced (kpi_validate);
  ≥2-exhibit narrative gap is loud, not silent.
- **Data**: spike extracted 5 exact candidates from NFLX Q4'24 EX-99.1
  (Global Streaming Paid Memberships 301.63; Net Additions 18.91; Revenue
  $10,247; Diluted EPS $4.27; UCAN 89.63) with table/row/col coordinates —
  scratchpad `route-b-inventory-spike.md` (volatile).
- **Boundary**: any Route B cache mints a NEW key (e.g.
  `exhibit_tables_{accession}_{document}`) — never reuse
  `narrative_sections_{accession}` (immutable-TTL collision class,
  docs/loom/memory/cache-key-collision-across-migration.md).

Evidence paths: scratchpad `route-a-census.md` / `route-a-census.json` /
`route-b-inventory-spike.md` / `route_b_spike*.py` (all volatile,
regenerable); repo reads cited above.

## Decision

Build Route B as the next arc: generic HTML-table extraction (pandas-style
walking + colspan/duplicate-cell cleanup on Workiva-generated exhibits) +
KPI-label candidate proposal, feeding tier-①'s EXISTING confirm-all human
gate. Trust design unchanged — confidence-gated review (Nowcast-style) is
recorded as a future calibration option, NOT v1: the committed tier-① design
is confirm-all, and industry EN-side treats per-number source anchoring as
non-negotiable (which we keep). NOT building in this arc: Route A's XBRL
allowlist (separate, now-small arc — disposition pending user), auto-confirm,
multi-filer label dictionaries, the ≥2-exhibit narrative ceiling lift
(acquisition goes via attachments; if the narrative layer IS touched, execute
the marker's recorded upgrade on the spot per
docs/loom/memory/execute-cheap-loom-simplify-upgrades-at-review.md).

## Alternatives Considered (Axis 4 — research-grounded, EN+JA)

- **Daloopa (EN)** — ML extraction + human QC on materiality/anomaly;
  auditable source-linking as core differentiator.
  https://daloopa.com/blog/analyst-best-practices/how-ai-is-transforming-earnings-report-processing-in-2025
- **Canalyst / Visible Alpha (EN)** — fully manual analyst spreading;
  click-through-to-source a named product feature on S&P Capital IQ Pro.
  https://www.spglobal.com/market-intelligence/en/solutions/visible-alpha-on-sp-capital-iq-pro
- **Nowcast / Finatext (JA)** — LLM extraction from 決算短信 with
  confidence-gated residual review (only ~2% below-threshold records get
  eyes; 95% accuracy at confidence≥90).
  https://aws.amazon.com/jp/blogs/news/gen-ai-usecase-nowcast/
- **Nikkei 決算サマリー (JA)** — fully automated summarization, no
  confirmation gate (consumer journalism, lower stakes).
  https://www.nikkei.com/promotion/collaboration/qreports-ai/
- **EN/JA split (finding)**: EN institutional vendors = human confirmation
  near-mandatory + source anchoring non-negotiable; JA (Nowcast) = human
  review as calibrated residual. Our v1 = EN-shape (confirm-all + anchors),
  JA-shape recorded as the conditional future once accuracy is measurable.
- Regulatory corroboration: EDINET/US inline-XBRL scope does not reach
  operational non-financial KPIs — the data class stays in unstructured
  release tables on both sides. https://www.fsa.go.jp/search/20241112.html

## What Becomes Obsolete

The fully-manual keying of press-release KPIs into tier-① becomes the
fallback path instead of the only path (workflow change; no code deleted —
manual entry stays as the degraded/override mode). This arc is otherwise
additive; the YAGNI flag is answered by the census: this data class is
unreachable by any existing lane.

## Out of Scope

- Route A XBRL non-monetary allowlist (own arc; full-universe census scopes
  it to the physical-footprint/capacity cluster — location counts confirmed
  at COST/MCD/CVS/O/PLD (+AMT extension-only), utility MW capacity at
  NEE/DUK/SO, BA program-unit counts; REQUIRES per-filer semantic
  verification (SBUX sub-brand trap), a value-sanity gate (MET claims-count
  corruption), and QName-keyed classification (hedge-notional trap in the
  same physical units at 7/15 energy/utility filers))
- JP 決算短信 sources; non-US filers
- Confidence-gated review / auto-confirm (future calibration, needs measured
  accuracy first)
- Multi-filer KPI label dictionaries beyond what v1's one-filer exercise needs
- ≥2-exhibit narrative ceiling lift (unless acquisition reuses that layer)

## Open Questions

1. Route A disposition after the FULL-universe census (71 filers) — the
   evidence-scoped shape is a physical-footprint/capacity allowlist
   (~8-10 filers, standard concepts, filer-aware extraction + semantic
   verification + value-sanity gate). Mini-arc after Route B vs
   park-with-evidence (user ruling pending; BACKLOG committed "both").
   Census artifacts: scratchpad route-a-census*.{md,json} (6 slices,
   volatile) — worth persisting the merged findings into
   docs/loom/references/ during the arc.
2. Per-point `currency` ISO passthrough rider — lands in whichever arc first
   touches the XBRL feed emission path (likely Route A's producer touch, not
   this arc); confirm at plan time.
