# Changelog

All notable changes to investing-toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v2.27.0] — 2026-07-19

Taiwan iXBRL financial-statement ingestion — TW equity memos now source
their canonical three statements + DCF fields + curated notes from the real
inline-XBRL filing (MOPS `t164sb01`, a gate-free Big5 GET), replacing the
deferred yfinance-only canonical stub, and degrade back to the yfinance stub
when a filing isn't available. Plan:
`docs/loom/plans/2026-07-19-tw-ixbrl-ingestion.md`.

### Added

- **TW iXBRL fetch/parse pipeline** (`data-markets`): `twse_ixbrl_fetch.py`
  (t164sb01 fetch — Big5 decode, season fallback for 興櫃 semiannual cadence,
  502 retry; one URL covers 上市/上櫃/興櫃/KY), `twse_ixbrl_parser.py` (generic
  fact extraction via regex/iterparse over `ix:` tags — NOT DOM, which silently
  drops ~85% of nested facts; `scale`-attribute-driven scaling),
  `twse_ixbrl_canonical.py` (canonical three-statement mapping for industrial
  `-ci` filers, incl. the DCF-required `total_debt`/`cash`/`ebit`/`capex`/`fcf`
  fields verified against 2330 + 1301 fixtures; financial `-fh` → unsupported
  marker), `twse_ixbrl_notes.py` (4 curated note categories: financial-instruments
  by measurement category, Mainland-China investment + MOEA ceiling, related-party
  balances + flows, employee-benefit expense), and `twse_ixbrl.py` (the
  `run_client`-invokable CLI assembling the pipeline into JSON).

### Changed

- **`pack_tw.py` memo-fetch** now sources the TW canonical from the iXBRL client
  (provenance-wrapped Tier-A `twse_ixbrl` group), filling the previously-deferred
  `_build_canonical_from_yf_financials_tw` stub; on iXBRL fetch failure it degrades
  to the retained yfinance stub rather than an empty canonical (no regression).

### Notes

- Scope is statements + generic fact layer + curated note fields, NOT a full
  note-table reconstruction engine — annual-filing verification showed TW iXBRL's
  forensic notes (inventory write-downs, tax bridge, aging buckets, PP&E
  rollforward) are absent at any period; value concentrates in the ~4 curated
  concept families. Endorsement/guarantee, parent-only (個體) statements, and
  `-fh` canonical are deferred (see plan Decision Log).

## [v2.26.0] — 2026-07-19

Route B 8-K earnings-release semi-auto KPI intake lane — a mechanical
producer + LLM-semantic + human-confirm three-layer path that turns an
earnings 8-K press-release exhibit into confirmed operational-KPI points
in the EXISTING tier-① store, without the value or its coordinates ever
passing through an LLM. Plan:
`docs/loom/plans/2026-07-19-8k-earnings-kpi-intake.md`.

### Added

- **Exhibit acquisition via attachments** (`data-markets` /
  `sec_edgar_client.py`): `fetch_exhibit_documents(ticker, accession=None)`
  resolves the latest earnings 8-K (Item 2.02) — or the given accession —
  and enumerates ALL EX-99.* attachments off `filing.attachments`,
  returning each document's RAW HTML (`attachment.content`) plus metadata
  (accession / document / exhibit_type / filingDate). This sidesteps
  `_segment_8k`'s ≥2-exhibit-item LOOM-SIMPLIFY ceiling (attachments
  enumerate every EX-99.x directly). Each document is cached under the NEW
  key family `exhibit_raw_{accession}_{document}` — never the legacy
  `narrative_sections_{accession}` slot (incompatible payload shapes share
  the immutable TTL; the distinct prefix makes the two caches un-aliasable
  so a pre-warmed machine can't get a schema-passing HIT of the wrong
  shape). A failed resolution/acquisition is a loud `{"error": ...}` slot,
  surfaced not cached.
- **Generic HTML table walker** (`data-markets` / `exhibit_tables.py`):
  stdlib `html.parser` extractor — raw exhibit HTML → JSON list of tables,
  each cell `{table_index, row, col, text}` after rowspan/colspan
  resolution + empty-separator-cell cleanup, plus a per-row leading-label
  path. No pandas/lxml (coordinate fidelity across the Workiva
  colspan/duplicate-cell artifact needs a custom walker). MECHANICAL only:
  values are the exact printed strings (nbsp/whitespace normalized, never
  parsed to float). CLI: `exhibit_tables.py --html <path> --out <json>`.
- **8-K candidate three-layer intake** (`analysis-kpi` /
  `kpi_8k_candidates.py`): `propose` subprocesses the table walker and
  emits RAW candidate points (verbatim label path + exact-printed value +
  `period_hint` + source coordinates + `confirmed: false`), leaving
  `kpi_id`/`unit`/`period` explicit `null` with a `needs_semantic` list —
  the mechanical layer NEVER invents a slug, a unit, or a normalized
  period. The LLM layer (analysis-kpi SKILL.md prose workflow) proposes
  those semantic slots by reading the verbatim labels; the human
  confirm-all gate ratifies and flips `confirmed: true`. `commit
  --company <T>` then appends ONLY confirmed-and-complete candidates into
  the tier-① store via the EXISTING `kpi_store.append` — unconfirmed
  entries are skipped, and a null semantic slot or missing provenance is
  refused loud (the store's own confirm-all trust gate is un-weakened).

## [v2.25.0] — 2026-07-19

JNJ restatement-axis fix — vintage-axis exclusion accounting and
per-signature refusal granularity join the dimensional-revenue producer
and the quarterly-KPI consumer chain. Plan:
`docs/loom/plans/2026-07-19-jnj-restatement-axis-signature.md`.

### Added

- **Vintage/unknown-axis exclusion accounting** (`data-markets` /
  `sec_edgar_client.py`): `_dimension_signature` now excludes, rather than
  silently collapsing, any fact carrying a `dim_` axis that is neither a
  whitelisted breakdown axis nor the ConsolidationItems qualifier —
  `srt:RestatementAxis` (any member, namespace-agnostic, via
  `_VINTAGE_AXIS_LOCAL_NAME`) is the named `"vintage"` exclusion category,
  every other disallowed axis is `"unknown"` (fail-closed). Each exclusion
  is counted in the pack's `coverage.axis_exclusions` channel
  (`{category, axis, member, concept, accession, period_end}`) via
  `_dimensional_axis_exclusions`; the 3-key signature shape
  (`concept`/`dimensions`/`consolidation`) is unchanged.
  `srt:ConsolidatedEntitiesAxis` — a sibling-axis spelling of the
  consolidation qualifier live-observed on INTC's 2021-2023 filings
  (member `OperatingSegmentsMember`) — is recognized as a second
  consolidation-qualifier axis (`_CONSOLIDATION_AXIS_LOCAL_NAMES`), folded
  into the same `consolidation` slot; a fact carrying both qualifier axes
  with DIFFERING members is excluded under the self-describing
  `"consolidation_conflict"` category.
- **`period_recast` coverage flag** (`analysis-kpi` / `kpi_xbrl.py`):
  `build_quarterly_series` aggregates the pack's `"vintage"`-category
  `axis_exclusions` — read from BOTH the quarterly and annual coverage
  arms — into at most one pack-wide `period_recast` coverage_flag,
  carrying the affected accession(s) and the raw exclusion entries
  verbatim under `exclusions`. Unknown-category exclusions stay
  pack-level accounting only; zero vintage exclusions emit no flag.
- **`signature_refused` per-signature refusal** (`analysis-kpi` /
  `kpi_xbrl.py`): a genuine intra-filing ambiguity
  (`_IntraFilingAmbiguityError`, raised by `resolve_binding`'s per-group
  call) is now caught per signature group instead of aborting the whole
  build — the poisoned group is skipped, a `signature_refused`
  coverage_flag records its accession(s), verbatim exception reason, and
  offending signature, and every other signature group's series still
  emits. Any other exception type still propagates.

## [v2.24.0] — 2026-07-18

Week-based duration lane — 52/53-week fiscal calendars (COST-class filers)
join the month lane across the quarterly-KPI chain, producer primitive
through the memo feed. Plan:
`docs/loom/plans/2026-07-18-52-53-week-filer-support.md`.

### Added

- **Shared week-band primitive** (`data-markets` / `sec_edgar_client.py`):
  a positive-allowlist day-span → week-count/week-lane-band mapping
  (`_WEEK_BANDS`), colocated with the existing month-lane primitive; every
  dimensional-revenue fact now emits `duration_weeks` alongside
  `duration_months`, plus a producer-decided `week_lane_band` — the
  producer classifies once, the consumer transcribes (no second band
  table).
- **Week-aware Gate P boundaries**: `_derive_fiscal_label`'s sub-annual
  path gains week-offset quarter boundaries computed per filer from
  `_WEEK_QUARTER_STRUCTURES`, matched within a tight
  `_WEEK_BOUNDARY_TOLERANCE_DAYS = 2` — the month lane's own ±10d
  tolerance is unchanged.
- **Week-lane Gate C classes** (`analysis-kpi` / `kpi_xbrl.py`):
  `classify_fact_period` transcribes each fact's `week_lane_band` into a
  `duration_class` string (e.g. `16wk`/`17wk`, `36wk-YTD`, `52wk-FY`/
  `53wk-FY`); facts with neither a month- nor week-lane match still
  raise (fail-closed unchanged).
- **Week-lane Q4 derivation**: `derive_q4_points` mints a derived Q4 from
  a week-lane FY point minus its `36wk-YTD` sibling, with
  `duration_weeks = FY_weeks − YTD_weeks` (16 or 17); a group carrying
  BOTH a month-lane 9mo-YTD candidate AND a week-lane `36wk-YTD`
  candidate refuses as `q4_basis_ambiguous` rather than guessing a
  basis; a missing YTD anchor still yields the existing
  `q4_source_missing` refusal.
- **Feed carries week counts + supplementary normalized YoY**: the 1.1
  quarterly feed passes through each point's `duration_weeks`, and a
  point whose same-signature prior-year comparator carries a DIFFERENT
  week count gets a supplementary `week_normalized_yoy` field
  ((value/weeks) vs. (prior value/prior weeks) − 1), skipped on any
  zero-denominator side; the as-reported value/YoY stay primary and
  `MEMO_FEED_QUARTERLY_SCHEMA_VERSION` stays "1.1" (additive fields,
  passthrough — no envelope bump).

## [v2.23.0] — 2026-07-18

Memo quarterly-KPI wiring — the honest fiscal-calendar quarterly chain shipped
in v2.22.0 now reaches the rendered memo. A new `kpi-quarterly` data pack, a
`quarterly-series` CLI, and a quarterly/XBRL memo-feed arm (schema 1.1) join
the fact-pack → series → memo-feed chain end-to-end, and `report-equity-memo`
gains a Phase 3.5 step that runs the chain for US tickers and hands the feed
to `investing-team`'s Operating-KPI block. Plan:
`docs/loom/plans/2026-07-18-memo-quarterly-kpi-wiring.md`.

### Added

- **`data-markets` `kpi-quarterly` pack** (US-only): calls
  `extract_dimensional_revenue` and emits the dimensional-revenue fact-pack
  JSON (facts[] + per-accession fiscal_calendars + `_status` envelope); a
  non-US ticker returns `_status.status == "usage_error"` (no silent skip).
- **`analysis-kpi` `quarterly-series` CLI** on `kpi_xbrl.py`: takes a
  fact-pack JSON path, classifies + builds a break-aware series per
  full-dimensional-signature group (`granularity="quarterly"`), derives Q4
  points, and emits one series JSON with parallel calendar/fiscal labels
  intact on every point.
- **`analysis-kpi` memo-feed quarterly/XBRL arm** (`kpi_memo_feed.py`,
  envelope `_memo_feed_schema_version` 1.0 → 1.1): `build_quarterly_memo_feed`
  + CLI subcommand `build-quarterly`. Fail-closed on per-point XBRL
  provenance completeness (reported points: `source_accession` + `concept`;
  derived points: `derived: True` + non-empty plural `source_accessions`/
  `source_forms`) and `assert_dqc_schema` on every coverage flag; this lane
  does not call the tier-① store gate (`kpi_gate.is_trusted`) — its trust is
  machine-verified provenance, not a store confirmation.
- **`report-equity-memo` Phase 3.5**: for a US ticker, runs
  kpi-quarterly pack → `quarterly-series` → `build-quarterly` and adds the
  resulting memo-feed JSON as an OPTIONAL `### Resource Paths` entry;
  non-US tickers get an explicit skip note in the seed (never silent).
- **Offline end-to-end chain test**: fact-pack fixture → `quarterly-series` →
  `build-quarterly`, asserting derived points keep plural accessions and the
  calendar/fiscal pair, `coverage_flags` survive verbatim, and a poisoned
  payload (derived point stripped of `source_accessions`) exits 1.

## [v2.22.0] — 2026-07-18

Quarterly (10-Q) operational-KPI support, rebuilt on an honest fiscal-calendar
foundation. The root defect — a primitive returning the CALENDAR year under a
"fiscal year" docstring, which mislabeled every non-December-FYE filer's
quarters — is replaced end-to-end: every dimensional fact now carries BOTH a
calendar label and a fiscal label in parallel (mirroring Compustat
DATADATE/DATACQTR/DATAFQTR), never one collapsed into the other. Spec:
`docs/loom/2026-07-16-operational-kpi-quarterly/specs/operational-kpi-quarterly/spec.md`;
plan: `docs/loom/plans/2026-07-16-operational-kpi-quarterly.md`; decision record:
`docs/loom/2026-07-16-operational-kpi-quarterly/rebuild-findings.md`.

### Added

- **Parallel period labels per fact** (`data-markets` / `sec_edgar_client.py`):
  `calendar_year`/`calendar_quarter` (calendar quarter containing period_end) +
  `fiscal_year`/`fiscal_quarter` (per-fact, own period_end vs that filing's dei
  calendar; comparatives from their OWN period, never the filing focus stamped;
  fail-loud on an unreadable calendar — never a calendar fallback) +
  `derivation_basis` (dei-declared | projected).
- **Declared-fiscal-year selection**: a 10-Q range request selects filings by
  their DECLARED fiscal year (index-window guess pre-fetch, reconciled against
  `dei:DocumentFiscalYearFocus` post-fetch — out-of-range declarations excluded
  and surfaced, unreadable declarations flagged, never calendar-bucketed).
- **Coverage honesty rebuilt**: comparison universe = the full filings index;
  absence states not_yet_filed / out_of_requested_range / unclassified +
  observed states attempted-fetch-failed / filed-but-unlabelable (one bad
  filing quarantines, never aborts the run) + index-visible-but-not-selected
  selection gaps. All flags on ONE DQC schema (type/old/new/accessions/reason).
- **Quarterly analysis chain** (`analysis-kpi` / `kpi_xbrl.py`): period
  classification consumes the emitted labels (analysis never re-derives fiscal
  years); series key on the FISCAL basis; duration-qualified identity key
  de-conflates 3mo single-quarter from YTD cumulatives; derived Q4 =
  FY − 9mo-YTD (guarded, segregated `derived: True` lane, dual-accession
  provenance, three label groups); single-granularity series with fiscal-range
  output filtering; structured point provenance (accession + source form +
  duration_class).
- **Live shape-anchor** (network-marked) pinning dual-duration facts + all
  three dei cover tags against real SEC EDGAR.

### Changed

- `_filing_period_year` (calendar-as-fiscal lie) removed; call sites route
  through honest primitives (`_filing_period_end_calendar_year`,
  `_quarterly_fiscal_year_guesses`, `_derive_fiscal_label`).
- Revenue-concept gate: deny list names the real
  `RevenueFromCollaborativeArrangement*` family + REIT pro-forma/ladder class;
  synthetic $-unit backstop regression added.

## [v2.6.0] — 2026-07-12

US SEC primary-source narrative layer — the memo pipeline can now read what
management actually wrote, not just XBRL numbers. Segmentation is pure data
acquisition: every item the filing's primary document enumerates is emitted,
never a curated analysis-selected subset (the downstream consumer decides what
to read). Ships the narrative capability of the US SEC primary-source spec
(`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/narrative/spec.md`);
plans: `docs/loom/plans/2026-07-12-us-sec-narrative.md` +
`docs/loom/plans/2026-07-12-us-sec-narrative-all-items.md`.

### Added

- **`data-markets` / `sec_edgar_client.py` narrative via edgartools**: a 10-K
  or 10-Q is segmented into one section per item in the filing's item list
  (a real AAPL 10-K yields all 23 items — Business, Risk Factors, MD&A,
  Financial Statements + notes, Controls, Governance…); an 8-K is segmented by
  every reported item, with exhibit-bearing items (2.02 / 7.01 / 8.01) followed
  to their **Exhibit 99.x** (where an 8-K's substance lives) and tagged
  `disclosure_status: furnished` — other reported items carry their body text,
  tagged `filed`. No non-99.x attachment is fetched.
- **Section provenance**: every section carries accession, CIK, item id, filing
  date, period of report, and a reconstructable SEC Archives URL pointing at
  *that section's own* source document (an 8-K section's URL points at the
  exhibit, not the body).
- **Paths-not-content**: section text is written to files under the toolkit
  cache and returned as `text_path`, never inlined into the JSON result. Both
  path segments are allowlist-sanitized and the write is containment-checked.
- **Per-section fail-loud** feeding `pack.py`'s `_status`: five distinct error
  classes (`absent_item`, `missing_exhibit`, `extraction_error`, `timeout`
  (retryable), `version_drift`) — a section is never silently empty or
  fabricated. The result wrapper carries `narrative_status` (ok / partial /
  failed) + `failed_items` so the failure state is visible without unwrapping
  `sections`.
- **SEC fair-access**: a non-compliant `<name> <email>` identity is rejected
  *before* any request is sent (edgartools does not fail fast); its built-in
  jittered backoff is preserved; filings are cached per accession under a
  dedicated key.

### Changed

- **`--action narrative` internals**: the legacy regex parser
  (`parse_item_sections` / `_ITEM_HEADER_RE` / `_TextExtractor` / the old
  `fetch_narrative`) is **retired**; segmentation now runs through edgartools'
  typed section API. The CLI contract (action name, `--accession`, result keys,
  exit-1-iff-error) is unchanged.

## [v2.5.0] — 2026-07-12

Verdict-layer defenses — hardening the memo pipeline against weak-model
failure at the judgment layer (a controlled strong-vs-weak comparison on
identical 2330.TW data surfaced rule-deviation, false data-unavailability
claims, dropped disclosures, and UTC date leakage after #539's artifact
gates already closed fake-completion). Plan:
`docs/loom/plans/2026-07-12-verdict-layer-defenses.md`. Pairs with
domain-teams v5.7.0 (the gate-side enforcement).

### Added

- **`analysis-dcf` `rule_verdict`**: `verdict_thresholds` now carries a
  deterministic `rule_verdict` (SELL / HOLD / BUY-string / null when no
  price) + `rule_verdict_basis` (price + thresholds compared) — the
  mechanical verdict-rule application moves into code so the memo LLM
  adopts it or files a gated Deviation Block rather than re-deriving it.
- **`report-equity-memo/scripts/pack_inventory.py`**: pure-stdlib CLI
  turning a data pack into a machine-readable section inventory
  (present/kind/rows|keys + `_status` echo), so a memo's "data unavailable"
  claims are checkable against ground truth.
- **`report-equity-memo/references/phase4-seed-contract.md`**: the four
  verdict-layer defense elements the Phase 4 packet must carry
  (`rule_verdict` binding-or-gated, pack inventory, issuer-timezone date
  anchoring, verbatim-disclosure pass bar) + the orchestrator's acceptance
  greps; SKILL.md Phase 4 gains a pointer (step 2b).

## [v2.4.1] — 2026-07-12

### Added

- **Vault filename & folder convention** (`vault-frontmatter.md` new section,
  referenced from Phase 5b): all-English `YYYY-MM-DD {identifier} Equity Memo.md`
  under `investing/memos/`; equity identifier = Yahoo/RIC ticker as-is (dot
  suffix included, e.g. `2330.TW`); future non-equity descriptors (`FX Memo`,
  `Commodity Memo`) use clean identifiers (ISO 4217 `USDTWD`, `XAUUSD`, house
  energy codes, caret-stripped indices) — raw vendor sigils (`=X`/`=F`/`^`) are
  Obsidian-link-hostile and stay in frontmatter, never filenames. Same-day
  re-analysis updates the existing note. (RESOLVED 2026-07-12 with the user;
  grounded in an Obsidian-constraints + multi-asset-symbology survey.)

## [v2.4.0] — 2026-07-11

Investing analysis memory layer (Obsidian-carried), pilot on
`report-equity-memo`. Brief: `docs/loom/specs/2026-07-11-investing-obsidian-memory-layer.md`.

### Added

- **`skills/report-equity-memo/references/vault-frontmatter.md`** — toolkit-owned
  frontmatter schema SSOT (8 fields: type/ticker/market/date/verdict/confidence/
  price_at_analysis/intrinsic_mid), Obsidian Bases date-typing note, sample
  track-record `.base` snippet.
- **Phase 0 — Recall Prior Verdicts**: before any data fetch, grep prior memos'
  frontmatter for the same ticker; surface last verdict/date/price + delta;
  three-way disclosure (hit / no-hits / no-vault) in the memo's Limitations.
- **Phase 4 always-on frontmatter**: the memo file begins with the schema block
  regardless of destination; artifact gate additionally verifies `head -1` is `---`.

### Changed

- **Phase 5b field ownership**: `obsidian:obsidian-markdown` must respect the
  toolkit frontmatter fields (placement/wikilinks/vault conventions only; never
  re-invent or overwrite); default vault folder `investing/memos/`
  (default-unless-user-says-otherwise).

## [v2.3.1] — 2026-07-11

Dogfood fix package (PR #539) — version bump so the fixes deploy via
`plugin update`; full findings in `docs/skill-dogfood/2026-07-11-data-markets/report.md`.

### Fixed

- **`analysis-dcf`** — per-share intrinsic value was exactly 1,000,000×
  too large on every market (script assumed $M inputs; all data-markets
  packs emit absolute currency). Fixtures reshaped to real producer shape.
- **`analysis-comps`** — multi-ticker batch peer packs now expand to N
  peer entries; unresolvable tickers fail loud via `_provenance.warnings`
  instead of silent all-null.
- **`data-markets`** — TWSE cache hits re-attach the declared
  `_cache_age_seconds`/`_cache_ttl_seconds` pair; description gains
  data-layer vocabulary, source names, and a regime-routing clause;
  cache-metadata docs clarify per-section injection.
- **`analysis-screener` / `analysis-macro-regime`** — stale
  `data-{country}` paths replaced; regime description now leads with the
  classification job.
- **`report-equity-memo`** — every phase requires an ls-verified on-disk
  artifact before it counts as complete (anti fake-completion gates;
  Phase 4 gains a defined artifact).

## [v2.3.0] — 2026-07-11

`data-markets` consolidation: 5 per-country data skills merged into one,
a live-reproduced silent-cache-crash bug closed, and a fail-loud exit
contract added to the data layer. See
[ADR-0009](docs/adr/0009-data-markets-consolidation-and-cache-util.md)
for the full design record.

### Added

- **`skills/data-markets/`** — replaces `skills/data-{us,jp,tw,kr,cn}/`.
  Thin `SKILL.md` (routing + shared contract + worked examples) +
  `references/market-{us,jp,tw,kr,cn}.md` (per-market sources, tiers,
  key requirements, caveats). 18 unique clients (deduplicated from 23:
  yfinance ×5 → 1, fred ×2 → 1) + one per-market `pack_{market}.py`
  module each, behind a single `pack.py` facade with ticker-suffix
  market auto-detection (`--market` required for `regime-pack`).
- **`skills/data-markets/scripts/cache_util.py`** — single cache module
  for all clients: XDG/uv-style path precedence (explicit arg >
  `INVESTING_TOOLKIT_CACHE` > `$XDG_CACHE_HOME/investing-toolkit` >
  `~/.cache/investing-toolkit`), empty-string-safe env parsing,
  post-resolution writability check with loud stderr warning + tempdir
  fallback, cadence-aware `compute_ttl()` (generalizes `dgbas_client.py`'s
  `_compute_ttl` to all 18 clients), schema-versioned roundtrip helpers.
- **Fail-loud `pack.py` exit contract**: `0` = all sections ok, `2` =
  partial (was silently exit `0` in 4 of 5 old `pack.py`s), `1` = all
  failed / unexpected exception, `64` = usage error (bad args/pack name,
  mixed-market ticker list, missing `--market` for `regime-pack`). A
  top-level `_status` block (`status`, `market`, `pack`,
  `failed_sections`, `warnings`) is injected into every response.
- `agents/data-fetcher.md` rewritten against the merged skill (`pack.py`
  invocations, exit-contract table, `cache_util` cache section) —
  replaces v1.x content referencing pre-v2.0.0 per-client scripts and
  flat `1h`/`6h`/`24h` TTLs.

### Fixed

- **Silent cache-directory crash (live-reproduced)**: the old canonical
  invocation set `INVESTING_TOOLKIT_CACHE` from a hook-only variable that
  is empty inside a Bash tool call, collapsing to the literal path
  `/cache`. Every client's unguarded cache-dir `mkdir()` then crashed,
  and 4 of 5 `pack.py` implementations swallowed the crash into an error
  slot while still exiting `0` — reports silently received `None` prices
  with no failure signal. `cache_util.resolve_cache_dir()` now strips +
  empty-checks the override, probes writability, and falls back loudly
  instead of crashing.

### Changed — BREAKING

- **`data-{us,jp,tw,kr,cn}` skill names removed.** All invocations
  (slash commands, agent dispatch, downstream `SKILL.md` references)
  migrate to `data-markets` — see `agents/data-fetcher.md` and
  `skills/data-markets/SKILL.md` for the new invocation form.
- **`INVESTING_TOOLKIT_CACHE` is now fully optional.** Previously
  required by the (silently broken) canonical invocation; omit it
  entirely for the default `~/.cache/investing-toolkit` path, or set it
  deliberately to override.
- **`sync-clients.sh` and its MD5-sync CI discipline removed** — a
  single-copy skill has no cross-copy drift to guard against.

### Removed

- `skills/data-{us,jp,tw,kr,cn}/` (5 skills, ~4-5k net LOC reduction
  including 4 duplicate `yfinance_client.py` copies + 1 duplicate
  `fred_client.py` + ~1,077 LOC of per-client cache boilerplate
  collapsing into one `cache_util.py`).
- `scripts/sync-clients.sh`, `tests/test_sync_clients.py`.

## [v2.1.1] — 2026-07-05

### Fixed — `report-equity-memo` Codex dispatch-portability

Phase 2.5's peer-discovery step named `general-purpose` (a real
Claude-Code built-in agent-type name) directly in `SKILL.md`, with no
literal `Agent(...)` syntax but also no per-host reference file (Codex
dispatch-portability survey finding, `docs/skill-mining/2026-07-05-
codex-dispatch-portability-survey.md` — classed borderline (A)/(B)).
Reworded to "dispatch a general-reasoning subagent" and added
`references/{claude-code-tools.md,codex-tools.md}` mapping
`general-purpose` onto Codex's `default`/`worker`/`explorer` built-ins.

### Fixed — description self-contradiction

Caught by whole-branch review: `plugin.json` + `.codex-plugin/plugin.json`
+ the root marketplace entry all said "Claude Code CLI only" while
shipping a full Codex manifest — same class of bug already fixed for
`briefing-toolkit` on this branch. Dropped the false host-restriction
claim from all three copies.

### Fixed — awkward dispatch sentence (behavioral dogfood follow-up)

A blind cold-reader flagged the peer-discovery dispatch sentence as
splitting subject from verb with a 30-word parenthetical, and naming
only Claude Code's agent-type inline. Restructured into two sentences
naming both hosts' agent-type symmetrically (`general-purpose` /
`default`).

## [v2.1.0] — 2026-05-02

`analysis-macro-regime` Phase 1 per-country classifier refactor. Decomposed the v1.9.0 unified IC + Hedgeye GIP classifier into 5 native per-country modules (`classify_us / jp / tw / kr / cn`). See [ADR-0004](docs/adr/0004-analysis-macro-regime-phase1-per-country-classifiers.md) for design rationale + Phase 2 deferral.

### Added

- **5 per-country classifier modules** (`classify_{us,jp,tw,kr,cn}.py`) — each implements its country's native framework rather than re-labeling legacy IC:
  - **US**: IC + Hedgeye GIP + Fed FIT (post-FAIT 2025) + 4-tier real-rate decomposition (HLW / LM / SEP / NY Fed composite) + yield-curve overlay.
  - **JP**: BOJ stance + Tankan business sentiment DI (大企業/中小企業 × 製造/非製造) + ESRI 景気動向指数 CI + deflation/inflation regime detection + ECB ex-post real-yield 4-tier band.
  - **TW**: NDC 五色景氣燈號 score-led (9-45 composite) + 9 構成項目 dispersion (per 2024 revision) + TIER 製造業營業氣候測驗點 + TSMC TAIEX concentration overlay.
  - **KR**: BOK 단일 2% target alignment + KOSTAT 동행지수순환변동치 cycle phase + 가계부채 GDP overlay + KOSPI 삼성+SK 하이닉스 ~40.96% concentration overlay.
  - **CN**: PBOC reaction (7天逆回购 1.40% post-2024-07) + credit impulse (CICC TSF flow-yoy 2nd-derivative) + 4-component dispersion alarm + 房地产 GDP-share overlay (3 definitions disclosed) + CPI framing enum (`supportive_recovery_below_target` captures PBOC's "wants inflation up" stance).
- **5 calibration YAMLs** (`scripts/calibrations/{us,jp,tw,kr,cn}.yaml`) — machine-readable extracts of `references/thresholds-{country}.md` (2026-Q1/Q2 vintages). All numeric thresholds plumbed into classifier code instead of sitting as un-executed documentation.
- **5 grounding research notes** (`research/grounding-{country}-2026-05.md`) — partial-recalibration delta refreshes per `recalibration-protocol.md` template. JP captured 4 material BOJ events 2026-04-19 → 2026-05-02 (FY2026 核 CPI 1.9%→2.7-2.8% upward revision, 6-3 vote, Ueda 4/30 anchor).
- **Output schema `2.0-phase1`** with `by_country.{cc}` envelope (country / framework_used / native_verdict / indicators_used / data_quality / confidence / provenance). `cross_country` hardcoded `null` (deferred to Phase 2).
- **Per-country fetch additions**:
  - JP: `boj_client.py --tankan-business-di` (4 series codes verified vs BOJ official docs); `pack.py` wires Tankan + ESRI coincident-index / leading-index / 機械受注 e-Stat presets.
  - CN: `pack.py:_compute_credit_impulse()` (CICC TSF flow → trailing-12m-sum YoY → 12-month change); methodology doc at `references/credit-impulse-methodology.md`.

### Changed

- **Output schema migration** for direct `regime_compose.py` consumers: read `out["by_country"][cc]` instead of `out["countries"][cc]`. `out["cross_country"]` is `null` in Phase 1.
- **Per-country threshold reference docs** (`references/thresholds-{country}.md`) — partial-recalibration refresh from v1.11.0 (2026-04-19) to 2026-05-02. JP captures 4 material BOJ policy events.

### Removed

- `_legacy_ic.py` — the v1.9.0 unified `classify_country()` IC + GIP fallback path. Helpers migrated to `_helpers.py`; per-country classifiers import from there.
- `out["countries"]` and `out["cross_country_consensus"]` schema fields (replaced by `out["by_country"]`; consensus deferred to Phase 2).

### Deferred (per fresh-eyes audit + ADR-0004)

- **Cross-country comparable surface** (Phase 2 / ADR-0005). Re-trigger: Phase 1 stable ≥4 weeks, ≥5 multi-country invocations, or memo workflow surfacing concrete need. If none fire within 6 months, evaluate whether comparable surface is needed at all.
- **KR ESI explicit ECOS API integration** — current code uses fdr_client KEYSTAT 'sentiment' group as best-effort fallback; explicit ECOS key-based integration deferred to v2.2.0.
- **TW TIER preset wiring at NDC client level** + live TWSE monthly weight ingestion — deferred to v2.1.x or v2.2.0.
- **CN true stock-yoy credit impulse** — current implementation uses flow-yoy second-derivative with explicit honest methodology label; switch when PBOC publishes stock series via akshare or direct scrape.

## [v2.0.0] — 2026-05-01

Three-Layer Skill Architecture (Data / Analysis / Report). See [ADR-0001](docs/adr/0001-data-analysis-report-layers.md) for the architectural decision and [migration guide](docs/migration-v2.0.0.md) for v1.x → v2.0.0 upgrade instructions.

### Breaking changes

- Plugin version bumped 1.16.5 → 2.0.0 (skill-API breaking changes — see Removed below).
- All 14 v1.x skill **directories** deleted and replaced by 16 new skills under three layers (5 `data-{country}` + 6 `analysis-*` + 4 `report-*` + 1 router).
- Removed `investing-toolkit/scripts/sync-scripts.sh`, `investing-toolkit/scripts/sync-check.sh`, and `investing-toolkit/tests/test_skill_md_sync.py` — the v1.16.1 dual-mode sync mechanism is retired.
- Slash-command **internal routing** now points at the new skills (full mapping in [ADR-0001 §Slash-Command Rename Map](docs/adr/0001-data-analysis-report-layers.md)). User-facing slash command names (`/invest-memo`, `/invest-screen`, `/invest-portfolio`, `/invest-macro`) are preserved.

### Added

- **5 new `data-{country}` skills** (US / JP / TW / KR / CN) — Layer 1 country-bundled fetch with 5 pack types each (`equity` / `regime` / `industry` / `screener-input` / `portfolio-input`).
- **6 new `analysis-*` skills** (Layer 2, pure compute, no I/O):
  - `analysis-dcf` — Damodaran 3-stage DCF (rename of v1.x `dcf-valuation`).
  - `analysis-comps` — peer multiples comparison (5 multiples: P/E trailing + forward, EV/EBITDA, P/S, P/B); statistics + anchor delta + composite ranking. **NEW.**
  - `analysis-screener` — multi-criteria screener engine (rename of v1.x `stock-screener` compute path).
  - `analysis-technical` — RSI / MACD / Bollinger / ATR / SMA (rename of v1.x `technical-snapshot`).
  - `analysis-portfolio` — holdings P&L + regime overlay (rename of v1.x `invest-portfolio`).
  - `analysis-macro-regime` — IC + GIP regime classification across US/JP/TW/KR/CN (rename of v1.x `macro-regime-snapshot`).
- **4 new `report-*` skills** (Layer 3, orchestrators):
  - `report-equity-memo` — full equity memo pipeline (rename of v1.x `investment-memo-writer`).
  - `report-stock-snapshot` — country-aware stock snapshot (consolidates v1.x `us-stock-snapshot` / `japan-stock-snapshot` / `taiwan-stock-snapshot`).
  - `report-portfolio-review` — portfolio review report (orchestrator above `analysis-portfolio`).
  - `report-screener-list` — screener list report. **NEW.**
- **`analysis-comps`** as a first-class skill: peer multiples (P/E trailing + forward, EV/EBITDA, P/S, P/B) with median / mean / IQR statistics, anchor delta vs peer median, and composite ranking.
- **`report-equity-memo` Phase 2.5**: runtime `research-agent` peer-discovery for the Comps section (`--auto` / `--interactive` modes).
- **ADR-0001**: Three-Layer Skill Architecture decision record at `investing-toolkit/docs/adr/0001-data-analysis-report-layers.md`.
- **Migration guide**: user-facing v1.x → v2.0.0 upgrade guide at `investing-toolkit/docs/migration-v2.0.0.md`.
- **CI sync workflow**: `.github/workflows/check-script-sync.yml` enforces MD5 equality between canonical clients (`investing-toolkit/scripts/`) and `data-{country}/scripts/` copies. Advisory in v2.0.0; will become required in v2.0.1+.
- **New helper**: `investing-toolkit/scripts/sync-clients.sh` (canonical → copies sync; `--check` mode for CI).
- **New slash command**: `/invest-snapshot` → routes to `report-stock-snapshot`.
- **Test suite**: 296 non-network + 27 network automated pytest tests covering data packs, analysis compute, and report orchestration.

### Changed

- **Architecture** — three-layer separation (Data / Analysis / Report). Layer 1 is I/O-only, Layer 2 is pure compute, Layer 3 orchestrates. See ADR-0001.
- **Cross-skill data passing** — main agent + temp files (replaces v1.x intra-skill subprocess dispatch). Each layer reads/writes JSON via temp file paths passed by the main agent.
- **`fred_client.py`** — parallel multi-series fetch via `ThreadPoolExecutor` (default 8 workers; configurable via `FRED_MAX_WORKERS` env var); removed custom User-Agent header (FRED bot filter blocked it, causing intermittent fetch failures).
- **Slash commands** — internal routing updated; user-facing names preserved (`/invest-memo`, `/invest-screen`, `/invest-portfolio`, `/invest-macro`). New: `/invest-snapshot`.

### Removed

- 14 v1.x skill directories: `us-macro`, `japan-macro`, `taiwan-macro`, `korea-macro`, `china-macro`, `us-stock-snapshot`, `japan-stock-snapshot`, `taiwan-stock-snapshot`, `technical-snapshot`, `stock-screener`, `dcf-valuation`, `invest-portfolio`, `macro-regime-snapshot`, `investment-memo-writer`.
- `investing-toolkit/scripts/sync-scripts.sh` (replaced by `sync-clients.sh`).
- `investing-toolkit/scripts/sync-check.sh` (replaced by `sync-clients.sh --check`).
- `investing-toolkit/tests/test_skill_md_sync.py` (v1.16.1 dual-mode validation; obsolete in v2.0.0 main-agent + Bash architecture).

### Fixed

- **JP bare 4-digit ticker resolution** (critical): `analysis-portfolio._resolve_price()` now auto-resolves `7203` ↔ `7203.T` mismatches between holdings files and `data-jp` pack output. Pre-fix produced silent missing-price entries; post-fix logs the mapping under `_provenance.ticker_resolutions`.
- **ROC quarter filing-aware logic**: `data-tw/pack.py.latest_roc_quarter()` no longer returns unfiled quarters near the Mar 31 / May 15 / Aug 14 / Nov 14 filing-deadline boundaries.
- **`analysis-dcf`** removed a dangerous unit-normalisation heuristic that mis-scaled BRK.A-style low-share-count stocks by 1e6× (mis-classifying market cap and intrinsic value).
- ~30 Wave 4 quality findings addressed in PR #172 and ~10 in PR #173.

### Pull requests

- **#172** — three-layer refactor (15 → 15 skills; 14 v1.x deleted; 11 + 4 implementer agents across Phase 1 + Phase 2; ADR-0001; 272-test suite baseline).
- **#173** — `analysis-comps` + `report-equity-memo` peer-discovery (15 → 16 skills; 24 new tests; `fred_client` parallel fetch + UA fix).
- **#(this PR)** — documentation polish (CHANGELOG, migration guide, READMEs, design-principles update) and final v2.0.0 plugin-version bump.

### Slash-command routing map (high-level)

User-facing slash commands stay stable. Only the underlying skill they route to changes.

| Slash command | v1.x routes to | v2.0.0 routes to |
|---|---|---|
| `/invest-macro` | `us-macro` / `japan-macro` / `taiwan-macro` / `korea-macro` / `china-macro` | `data-{country}` regime-pack + `analysis-macro-regime` |
| `/invest-memo` | `investment-memo-writer` | `report-equity-memo` |
| `/invest-screen` | `stock-screener` | `report-screener-list` |
| `/invest-portfolio` | `invest-portfolio` | `report-portfolio-review` |
| `/invest-snapshot` *(new)* | (none) | `report-stock-snapshot` |

For the full v1 skill → v2 skill mapping (16 entries including internal renames), see [ADR-0001 §Slash-Command Rename Map](docs/adr/0001-data-analysis-report-layers.md).

[v2.0.0]: https://github.com/kouko/monkey-skills/releases/tag/investing-toolkit-v2.0.0
