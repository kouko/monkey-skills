---
name: data-markets
description: |
  Layer-1 unified data fetch across US/JP/TW/KR/CN equities + macro — one
  pack.py facade, market auto-detected from ticker suffix, 9 pack types
  (snapshot / memo-fetch / comps-multiples / screener-batch / regime-pack /
  kpi-quarterly / kpi-topline-backfill / statement-backfill / reconstruct).
  Emits a raw data pack（原始資料包，非渲染卡片）from SEC EDGAR, EDINET, TWSE, FRED and
  14 more sources through a shared cache layer. Use for 資料層 health checks,
  cache (快取) verification, or fetch-by-source-name. Pure I/O, no analysis —
  regime 判斷 → analysis-macro-regime.
---

# data-markets

**Layer 1 — Data** in the investing-toolkit three-layer architecture
(Data → Analysis → Report). Pure fetch across 5 markets — 18 client
scripts (yfinance, SEC EDGAR, FRED, EDINET, TDnet, BOJ, e-Stat, ECB, MOPS,
TWSE/TPEx OpenAPI, FinMind, CBC, DGBAS, NDC, stat.gov.tw, NBS, akshare,
FinanceDataReader) behind one CLI. Does not analyze, score, or compose
narrative — output is structured JSON for a Layer 2 `analysis-*` skill or
a Layer 3 `report-*` orchestrator.

## THE invocation

One command shape covers every market and pack type:

```
uv run ${CLAUDE_SKILL_DIR}/scripts/pack.py --ticker 2330.TW --pack snapshot
```

No plugin-data env var is needed or should be passed here — that class
of variable is hook-context-only and is not set in a normal tool
invocation (an unset/misexpanded one used to silently collapse to a
bogus literal path in the pre-migration clients). Cache location is
resolved internally by `cache_util.py` via an XDG-style ladder, highest
precedence first:

```
INVESTING_TOOLKIT_CACHE env var  >  $XDG_CACHE_HOME/investing-toolkit  >  ~/.cache/investing-toolkit
```

The resolved directory is probed with a real write; if unwritable, a loud
`WARNING:` line prints to stderr and resolution falls back to a tempdir —
it never fails silently and never raises unless even the tempdir fallback
is unwritable.

## Pack types

| Pack | Ticker mode | Worked example |
|---|---|---|
| `snapshot` | single | `pack.py --ticker AAPL --pack snapshot` |
| `memo-fetch` | single (heavy) | `pack.py --ticker 7203 --pack memo-fetch` |
| `comps-multiples` | single or batch | `pack.py --tickers 005930.KS,000660.KS --pack comps-multiples` |
| `screener-batch` | batch (≥2) | `pack.py --tickers 600519.SS,000858.SZ,300750.SZ --pack screener-batch` |
| `regime-pack` | none — **requires `--market`** | `pack.py --pack regime-pack --market tw` |
| `kpi-quarterly` | single, **US-only** | `pack.py --ticker AAPL --pack kpi-quarterly` |
| `kpi-topline-backfill` | single, **US-only** | `pack.py --ticker AAPL --pack kpi-topline-backfill` |
| `statement-backfill` | single, **US-only** | `pack.py --ticker AAPL --pack statement-backfill` |
| `reconstruct` | single, **US-only**, needs client deps | `uv run --with edgartools --with requests pack.py --ticker KO --pack reconstruct` |

`regime-pack` has no ticker dimension; omitting `--market` is a usage
error (exit 64). `kpi-quarterly`, `kpi-topline-backfill`,
`statement-backfill` and `reconstruct` are refused (exit 64) for any
market but `us` — the facade's `US_ONLY_PACKS` guard names this as a
market-availability problem, not a pack-name typo.

## Client dependencies are supplied on the invocation

`pack.py` is a **zero-dependency facade**: it imports only the stdlib, and
each market client's dependencies (`edgartools`, `requests`) are passed on
the `uv run` line rather than bundled. Every SEC-backed pack therefore
needs them:

```
uv run --with edgartools --with requests ${CLAUDE_SKILL_DIR}/scripts/pack.py \
  --ticker KO --pack reconstruct
```

Omitting them exits `1` with an `_status.message` naming the missing
module **and the whole set to pass** — pass the whole set, since supplying
only the module named in the error moves the failure to the next import.
The raw traceback rides along in `_status.traceback`; the message adds
guidance, it never replaces the cause.

## As-filed statement reconstruction (US SEC)

`--pack reconstruct` (**US-only**, single ticker) emits one company's
three financial statements **as the filer declared them**, for its most
recent 8 annual filings, under a single `reconstruction` section:

```
{pack, ticker, cik, company, fetched_at,
 reconstruction: {
   filings: [{accession, form, filingDate,
              statements: {income|balance_sheet|cash_flow: [
                 {label, concept, level, weight, calculation_parent,
                  values, decimals, balance}, ...]},
              roles: {kind: [role_uri, ...]},
              unrecognised_dimension_keys: [...]}, ...],
   verification: {
     by_era: [{era, resolved, unresolved, reasons: [{reason, count}]}],
     statements: [{filing_date, era, kind, resolved,
                   reasons: [{reason, detail}],
                   groups_checked, groups_incomplete}],
     sum_checks: {
       by_status: {agrees, within_rounding, disagrees, incomplete},
       disagreements: [{kind, period, parent, status,
                        reported, computed, difference, tolerance}]}},
   failed_items: [...], requested, succeeded, failed, _status}}
```

Each line carries the **filer's own label** and **own concept** — including
custom ones no fixed concept list could contain — in the filing's own
presentation order, with segment slices and placeholder rows excluded.
Reads the presentation linkbase for which lines exist and their order, and
the calculation linkbase for `weight` / `calculation_parent`; nothing infers
a line's meaning from its position. `decimals` is the precision the filer
declared per period (KO states −6 on its revenue line and 2 on its EPS line
in the same statement, so it is per-period, never one scalar); `balance` is
the **taxonomy's** own debit/credit classification, and `null` — the common
case — means the taxonomy says nothing, never "not revenue".

### Reading the verification

`by_era` splits the resolved/unresolved counts by **filing** era, because the
structural rule's 63-of-65 was measured on filings filed 2016-2018 only and a
10-year run spans years nobody sampled. An era with no filings is absent
rather than zeroed.

`sum_checks.by_status` always carries all four keys, and the four are three
different answers plus a non-answer — keep them apart:

| status | what it means |
|---|---|
| `agrees` | Σ(child × weight) equals the filer's own reported figure exactly |
| `within_rounding` | it differs, but by less than the filer's **own declared** precision permits — **not** a defect (24 of 27 such differences in the committed capture are this) |
| `disagrees` | it differs beyond that interval |
| `incomplete` | no comparison was made — a child carries no value for that period |

`disagrees` does **not** mean the filer is wrong. The check sees *presented*
lines only, so a calculation child the filer never puts on the face of the
statement leaves the sum short and reads the same way; all 3 remaining
disagreements in the capture are that shape. `disagreements` carries the
`tolerance` alongside the figures so the interval can be argued with, not
just the verdict. Money is emitted as **exact decimal text** (`"18000000000"`),
never a float.

Every figure is **recomputed per run** — a verification refusal (the check
refuses to guess on a concept presented twice with disagreeing figures, or a
filing date with no readable year) degrades `verification` to an `error`
entry and the section to `partial`; the statements still ship.

**No per-cell typing here, deliberately.** There is no `cell_state` in this
envelope. Against the filer's own line set the four states collapse: every
line present *is* presented; "the line exists but that period is untagged" is
already visible as a period missing from that line's `values`; and a
`derived` value would mean adding a line the filer never filed, which breaks
the one fidelity promise this pack makes. The four-way taxonomy earns its
keep against the fixed 14-field grid — `analysis-kpi`'s
`kpi_spine_view.derive_spine_as_filed`, a read-side view over this payload.

**Why 8 filings.** Consecutive 10-Ks overlap by their two comparative
years, so N filings yield **N+2** distinct years, not 3N. Measured live
2026-07-26 on KO: 4 filings → 6 distinct annual periods; 8 filings → 10
(2016-2025), ~24s warm. An earlier estimate of "10 years ≈ 4 filings"
multiplied where it should have overlapped.

**Nothing is persisted.** The reconstruction is recomputed per run and no
point reaches the KPI store — filings are immutable, so the correct
cache-invalidation trigger is *our own code changing*, and a stale
reconstruction served after a logic fix is exactly the failure this lane
exists to remove. The envelope therefore carries no `source_kind`.

A per-accession acquisition failure is a loud entry in `failed_items` with
its `error_class`, never a fabricated statements entry; the section's
`{requested, succeeded, failed}` triple and `_status` make degradation
visible without descending into `filings`.

## Ticker-suffix routing

| Suffix / form | Market |
|---|---|
| `.TW` / `.TWO` | `tw` |
| `.KS` / `.KQ` | `kr` |
| `.SS` / `.SZ` / `.HK` | `cn` |
| `.T` or bare 4-digit | `jp` |
| anything else | `us` (historical default — surfaced as a `_status.warnings` entry, not silent) |

`--market <us\|jp\|tw\|kr\|cn>` overrides detection entirely. **One
market per invocation**: a `--tickers` list whose members resolve to more
than one market is rejected (exit 64) rather than silently picking one —
split cross-market batches at the caller.

## Exit contract — always check `_status` first

| Exit | Meaning | `_status` fields |
|---|---|---|
| `0` | all sections ok | `status: "ok"` |
| `2` | some sections failed | `status: "partial"`, `failed_sections: [...]` |
| `1` | all sections failed, or an unexpected exception | `status: "failed"`, `traceback` (on crash) |
| `64` | usage error (bad args/pack name, mixed-market tickers, missing `--market` for regime-pack) | `status: "usage_error"`, `message` |

`_status` is injected at the top level of every emitted JSON object.
This is the fail-loud contract: **never consume a pack payload without
checking `_status.status` first**. A `partial` (exit 2) result still
emits every section it could fetch — only `_status.failed_sections`
tells you which ones to distrust.

## Cache-hit metadata

A payload served from cache carries three bookkeeping keys injected by
`cache_util.load_cache`: `_cache: "hit"`, `_cache_age_seconds`,
`_cache_ttl_seconds`. A fresh fetch has no `_cache` key (or `_cache:
"miss"` where the client sets it explicitly). Downstream skills may use
these to decide whether to force a re-fetch. These keys are injected
per fetched section (e.g. `.yfinance.info.data._cache`), never at
document top level; miss-marking varies by client.

## Route B — 8-K earnings-exhibit acquisition (US SEC)

Two mechanical verbs acquire and structure an earnings 8-K press-release
exhibit for the analysis-kpi Route B intake lane (US SEC only). Both are
PURE MECHANICAL — they carry raw bytes + grid coordinates, and perform
zero semantic interpretation (no `kpi_id`, no unit, no normalized period).

**`fetch_exhibit_documents(ticker, accession=None)`** (`sec_edgar_client.py`
library call): resolves the latest earnings 8-K (Item 2.02) when
`accession` is `None`, or fetches the given accession directly; then
enumerates ALL EX-99.* attachments off `filing.attachments` and returns
each document's RAW HTML (`attachment.content`) plus metadata. Return
shape:

```
{accession, ticker, cik, form, filingDate,
 document_count,
 documents: [{accession, document, exhibit_type, filingDate,
              raw_html, _cache: "hit"|"miss"}, ...]}
```

Acquisition goes via `filing.attachments` (NOT `_segment_8k` /
`fetch_narrative_sections`) so every EX-99.x is recovered even on a ≥2
exhibit-item 8-K. A failed resolution/acquisition is a loud
`{"error": ...}` slot — surfaced, never cached.

**New cache key family** `exhibit_raw_{accession}_{document}` under the
`sec_edgar` cache namespace — NEVER the legacy
`narrative_sections_{accession}` slot. The two payload shapes are
incompatible (raw exhibit HTML per document vs a section list) and share
the immutable TTL, so a shared key would let a pre-warmed machine get a
schema-passing HIT of the WRONG shape that never self-heals. The distinct
`exhibit_raw_` prefix makes the two caches un-aliasable. A per-document
cache HIT skips re-downloading that exhibit's bytes; the filing itself is
still resolved once to enumerate which exhibits exist.

**`exhibit_tables.py --html <path> --out <json>`** (CLI): a stdlib
`html.parser` table walker — raw exhibit HTML → a JSON list of tables,
each cell `{table_index, row, col, text}` after rowspan/colspan
resolution + empty-separator-cell cleanup, plus a per-row leading-label
path (`row_label_paths`). No pandas/lxml (coordinate fidelity across the
Workiva colspan/duplicate-cell artifact needs a custom walker). Values
are the exact printed strings (nbsp/whitespace normalized, never parsed to
float). Output shape:

```
[{table_index, n_rows,
  cells: [{table_index, row, col, text}, ...],
  row_label_paths: [["Global Streaming Paid Memberships"], ...]}, ...]
```

analysis-kpi's `kpi_8k_candidates.py` invokes this walker by SUBPROCESS
(not import) to cross the analysis↔data-markets layer boundary.

## Top-line revenue lane (US SEC)

`kpi-quarterly`'s per-filing parse (`extract_dimensional_revenue`) now
ALSO resolves and emits the company's flat top-line (total) revenue fact
for every filing it walks, at zero extra fetch cost — the candidate facts
were already inside the parse, only dropped by the dimensional gate
before. Per filing, exactly ONE concept is emitted: the first-present
entry, in this fixed order, from a closed allowlist — `Revenues` →
`RevenuesNetOfInterestExpense` →
`RevenueFromContractWithCustomerExcludingAssessedTax` →
`RevenueFromContractWithCustomerIncludingAssessedTax`. A filing with no
allowlist candidate emits nothing for that filing and is recorded under
`coverage.top_line_gaps` with a named reason — never guessed.

`--pack kpi-topline-backfill` (**US-only**, single ticker) reaches
further back via the SEC `companyconcept` REST endpoint over the same
allowlist, picking the first concept with any reported history. It is
**annual-only by design**: a `companyconcept` row carries no fiscal
calendar, so four skip classes land in `coverage.skipped_rows` with a
named reason rather than a guess — never fewer than a row's actual
disqualifier, never a fabricated one:

- `source_filing_unidentifiable` — the row carries no `form` (leaving
  the carrying filing's dei fiscal-period focus undecidable) and/or no
  `accn` (which is the `fiscal_calendars` key — a `None` key would be
  matched by any equally accession-less fact downstream);
- `carrier_form_not_allowlisted` — the row's carrying form is not one
  whose annual focus this lane can state honestly. A 12-month top-line
  row is **not** necessarily carried by a 10-K: a live capture of the
  endpoint's `form` domain (`tests/data/fixtures/companyconcept_form_
  domain_2026-07-25.json`, 8 filers, 2026-07-25) observed
  `{"10-K": 48, "20-F": 47, "20-F/A": 8}` on annual-span rows — TM and
  HMC, us-gaap-tagging foreign private issuers, carry their entire
  top-line history on 20-F/20-F/A. Labelling those `FY` would stamp
  `source_form: "10-K"` on filings that never were. (IFRS-tagging FPIs
  — TSM, SAP, SHEL, BP — 404 out of the us-gaap endpoint entirely, so
  they cannot reach this lane at all. `10-K/A` is excluded too, which
  costs value freshness: it is the canonical carrier of a *restated*
  annual figure, so an amended year keeps its original number here.)
- `non_annual_row_skipped` — duration ≠ 12 months (quarterly/YTD row);
- `new_year_boundary_ambiguous` — the period end has **crossed into
  January**, landing within `FISCAL_BOUNDARY_TOLERANCE_DAYS` *after*
  Jan 1, where the period-end-year labeling convention is unsound for a
  52/53-week filer whose fiscal year rolls past New Year, and this lane
  (unlike `kpi-quarterly`) has no dei fiscal calendar to disambiguate.
  The check is deliberately **one-sided**: a December year-end, however
  close to Jan 1, gets the SAME label from both lanes *provided the
  filer's nominal fiscal-year end is itself in December* (`kpi-quarterly`
  walks to the first fiscal-year end at-or-after the period end, which
  for a December-nominal filer is the period end's own calendar year), so
  it is backfilled normally — a symmetric check would silently drop the
  entire history of every December-fiscal-year-end filer.

  **Known residual — this lane can mislabel a January-nominal filer's
  late-December year.** The agreement above holds along the period end
  only; the divergence is two-sided along the *nominal* fiscal-year end,
  which this lane never sees. When a filer's `dei:CurrentFiscalYearEndDate`
  sits in early January but the year's actual end drifted back into late
  December (a 52/53-week filer — the nominal drifts per filing),
  `kpi-quarterly` walks *forward* to the January nominal and answers the
  NEXT fiscal year while this lane answers the period-end year. The guard
  does not fire, no coverage reason is emitted, and the row is backfilled
  under a fiscal year one lower than `kpi-quarterly` assigns it — which
  surfaces as a spurious restatement dagger where the two lanes overlap,
  not as a missing value. This lane cannot detect the case (its
  `companyconcept` rows carry no dei calendar, and their `fy`/`fp` are the
  carrying filing's focus, not the fact's), so **treat `kpi-quarterly` as
  the authority for any fiscal year both lanes cover.** Tracked in
  `docs/loom/backlog/2026-07-25-investing-toolkit-top-line-revenue-lane-2-36-0-post-ship-follow-ups.md`,
  item (j).

The filing-identity checks run first — a filer this lane cannot serve
at all (a 20-F-only foreign private issuer) reports one actionable
reason per row instead of a period-shaped one, and one unusable row's
malformed dates can no longer abort an otherwise good backfill. A row
that survives all four checks also seeds this pack's own
`fiscal_calendars` map (keyed by accession, focus always `"FY"` — the
only value this lane can state honestly, since the allowlisted annual
carrier form is the literal `10-K`), which the envelope carries
alongside `facts` and `coverage`.
Downstream, `kpi_xbrl.facts_to_points` reads that map to derive each
point's `source_form` and refuses to emit a point when it is absent —
so a backfill pack missing `fiscal_calendars` loses 100% of its facts at
ingest. The envelope also carries `"source_kind": "xbrl-companyfacts"`
so the KPI ingest layer assigns these points the correct provenance.

## API keys

| Env var | Market | Effect |
|---|---|---|
| `EDINET_API_KEY` | jp | Unlocks Tier-A EDINET (金融庁) primary-source filings for `memo-fetch`. Unset → yfinance Tier-2 fallback with `_provenance.upgrade_hint` pointing to free EDINET registration. |
| `FRED_API_KEY` | us (+ macro cross-source for kr/cn) | Optional — the CSV endpoint works keyless; the key only enables the more flexible JSON API. |
| `FINMIND_API_TOKEN` | tw | Optional — anonymous access is 300 req/hr; a free token raises this to 600 req/hr. |

Per-market source inventories, authority tiers, additional keys, rate
limits, and caveats: see `references/market-us.md`,
`references/market-jp.md`, `references/market-tw.md`,
`references/market-kr.md`, `references/market-cn.md`. External-surface
grounding for the cache-layer migration itself: `references/migration-grounding.md`.
Per-pack output JSON Schemas (market-prefixed, e.g. `tw-schema-snapshot.json`)
for validating each pack's emitted shape: `schemas/`.

---

統一 5 市場（美/日/台/韓/中）資料抓取層 · 5市場統合データ取得レイヤー
