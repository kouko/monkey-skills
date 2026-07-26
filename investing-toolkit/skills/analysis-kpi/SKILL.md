---
name: analysis-kpi
description: >-
  Append-only bitemporal store for validated operational-KPI series-points
  (US SEC primary-source layer). Persists file-per-series JSON keyed by
  company+kpi_id under a durable DATA dir, keeping full history so a
  restatement appends a superseding record and a point-in-time query sees
  only what was known then. 営業 KPI 二時制追加専用ストア。營運 KPI 雙時態
  唯附加儲存層。
---

# analysis-kpi

Layer 2 (Analysis) internal-persistence skill for the **operational-kpi**
capability of the US SEC primary-source layer. This capability is built
**INCREMENTALLY as a sequence of thin slices** (validated spec:
`docs/loom/2026-07-12-us-sec-primary-source-layer/specs/operational-kpi/spec.md`).

**This slice = the append-only bitemporal store** — the keystone every later
slice writes to. Later slices (HTML table extraction, KPI schema, locate/
parse, rule validation, XBRL cross-check, review queue, break-events,
reliability-gate, memo-feed) are NOT part of this slice.

## What it does

`scripts/kpi_store.py` persists a validated KPI series-point to a
**file-per-series JSON** (one file per `company`+`kpi_id`, holding a list of
point records) under a **durable DATA dir** — resolved as `KPI_STORE_DIR`
env override → `$XDG_DATA_HOME/investing-toolkit/kpi-store` →
`~/.local/share/investing-toolkit/kpi-store`. It is durable (NOT the
evictable cache dir): a bitemporal series is irreplaceable history.

A point is a dict:
`{company, kpi_id, period, as_of, value, source_accession, source_table_id,
source_cell_ref}` (+ optional `lineage`, `restates` — persisted verbatim,
not interpreted this slice). Records are wrapped in a versioned
`_kpi_store_meta` envelope so a future record-shape change is a detectable
migration, not a silent misread.

**Append-only:** an existing record is never mutated or deleted; a
restatement/re-extraction appends a superseding record instead.

## Persistence pattern (mirrored, not imported)

The store MIRRORS `data-markets/scripts/cache_util.py`'s key-sanitization
regex + atomic tmp+rename write **pattern**, but does NOT `import cache_util`
(cross-skill import would breach the analysis↔data-markets layer boundary —
analysis skills reach data-markets by subprocess, never by importing its
modules) and does NOT reuse its TTL envelope (a bitemporal series is
immutable append-only, no expiry). Stdlib only.

## CLI reference

Per-subcommand CLI detail (flags, exit codes, worked examples) lives in
[`references/cli-reference.md`](references/cli-reference.md) for thirteen
of the fifteen persistence/compute scripts indexed below. The two
exceptions: `kpi_tw_ingest` (shipped 2.35.0) has no section there yet, so
for that one the index entry and the TW workflow step are currently the
whole documented surface; and `kpi_us_statements` is a pure LIBRARY with
no CLI at all — it is reached only through `kpi_us_statements_ingest`.
Index:

- **`kpi_store`** — append-only bitemporal store: `append` a point / `query`
  `--latest` or `--as-of` (point-in-time).
- **`review_queue`** — review-item queue + human-confirm seam: `enqueue` /
  `list` / `adjudicate`.
- **`kpi_schema`** — KPI schema propose-then-confirm lifecycle: `propose` /
  `confirm` / `status`.
- **`kpi_validate`** — pure-compute rule-based value validation: `validate`
  (sign/unit/subtotal/gaap).
- **`kpi_parse`** — deterministic fail-loud cell parser: `parse` (raises on
  an unparseable cell, never coerces to 0).
- **`kpi_gate`** — reliability gate (accuracy -> TRUSTED/WITHHELD):
  `add-labels` / `evaluate` / `verdict`.
- **`kpi_break`** — break-event detection + adjudication: `detect` / `flag` /
  `confirm` / `dismiss` / `list`.
- **`kpi_series`** — dual as-reported/recast split + basis-required view:
  `apply` / `view`.
- **`kpi_memo_feed`** — memo-feed contract assembly (trust-gated): `build`.
- **`kpi_xbrl`** — XBRL fact -> kpi_store point adapter: `build`.
- **`kpi_xbrl_ingest`** — XBRL fact-pack -> kpi_store driver (no collapse):
  `ingest`.
- **`kpi_tw_ingest`** — TW filing envelope (canonical + facts + coordinates)
  -> kpi_store driver (idempotent, append-only): `ingest`.
- **`kpi_us_statements`** — US as-reported statement-pack -> store-point
  mapper. PURE LIBRARY, no CLI (`us_statement_pack_to_points`); `kpi_id` is
  the filer's own qname verbatim.
- **`kpi_us_statements_ingest`** — US as-reported statement pack ->
  kpi_store driver (idempotent, append-only): `ingest`.
- **`kpi_spine_view`** — READ-side pure view: as-reported concept series ->
  the 14 canonical spine fields, resolved per period: `derive`.

The Route-B `kpi_8k_candidates` intake CLI is documented in full below (it
stays here because its 3-layer contract is load-bearing).

## Workflow: US XBRL -> tearsheet

The end-to-end path from a bare US ticker to a rendered KPI tearsheet is
three steps, in order:

1. **Fetch** the dimensional fact-pack from `data-markets`:
   `pack.py --pack kpi-quarterly --ticker <T> --market us` (US-only pack;
   SEC EDGAR dimensional XBRL, single ticker only — rate-limited 10 req/s).
   This pack now also carries the filing's flat top-line revenue fact
   (Lane B) alongside the dimensional facts.
2. **Ingest** the fact-pack into this skill's store:
   `kpi_xbrl_ingest.py ingest --pack <pack.json>` — derives a `kpi_id` per
   dimensional signature (a non-default `ConsolidationItemsAxis` member,
   e.g. intersegment eliminations, splits off its own series; spelling
   case never does) and appends every vintage to `kpi_store`, and
   routes any flat fact into the ONE fixed canonical `total_revenue`
   series (honors `KPI_STORE_DIR`; see
   [`references/cli-reference.md`](references/cli-reference.md) for
   flags/exit codes and the two-lane provenance/dedup-guard detail).
3. **Render** the tearsheet via `report-kpi-tearsheet`, which reads the
   now-populated store directly.

### Two-lane `total_revenue` coverage

`total_revenue` is filled by TWO independently-fetched packs, both
ingested through the SAME `ingest` command above (no separate
subcommand):

- **Lane B — per-filing** (`--pack kpi-quarterly`, step 1 above): the
  filing's own flat top-line fact; provenance `xbrl-topline` unless the
  pack declares its own `source_kind`.
- **Lane A — annual backfill** (`--pack kpi-topline-backfill`): fills
  fiscal years older than the filings Lane B fetched, from the SEC
  `companyconcept` REST series; provenance `xbrl-companyfacts`.

Both lanes append to the SAME series, and a fiscal year both lanes cover
must agree — see [`references/cli-reference.md`](references/cli-reference.md)
for the exact dedup-key guard.

## Workflow: US as-reported statements -> spine view

The third US lane, and the only one that stores the filer's OWN concept ids
rather than a repo-canonical slug. Three steps:

1. **Fetch** the as-reported annual statement pack from `data-markets`:
   `pack.py --pack statement-backfill --ticker <T> --market us` (US-only,
   exactly one ticker — heavy). It walks SEC `companyfacts` for the source
   concepts of the 14 spine fields and keeps only **annual, 10-K-carried**
   rows; every rejected row lands in `coverage.skipped_rows` under a named
   reason. A ticker whose resolved CIK carries no statement history is a
   loud typed error slot with NO `facts` key — never an empty-but-successful
   pack — and a truncated history is surfaced in `coverage` rather than
   stitched from a predecessor CIK.
2. **Ingest** the pack: `kpi_us_statements_ingest.py ingest --filing
   <pack.json>` — maps it through the pure `kpi_us_statements` library and
   appends every point to `kpi_store` (honors `KPI_STORE_DIR`; idempotent).
   The `kpi_id` is the filer's **own qname, verbatim, namespace preserved**
   (`us-gaap:Revenues`) — no slug derivation, so it is injective by
   construction, and `us-gaap:Revenues` and
   `us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax` are **two
   series**, not one resolved series.
3. **Derive + render** — the view is a plain pipe stage, so
   `tearsheet_format.py` stays untouched:

```
uv run scripts/kpi_store.py dump --company AAPL \
  | uv run scripts/kpi_spine_view.py derive \
  | uv run ../report-kpi-tearsheet/scripts/tearsheet_format.py --as-of 2026-07-26
```

`derive` resolves, **per period**, which stored concept represents each
spine field (first-present over that field's ordered chain). A field no
concept covers in a period yields no entry; a field no concept covers at
all yields no row — never 0, never a derived guess.

> **The store key is the TICKER, in every lane.** `kpi_us_statements_ingest`
> resolves it through `kpi_us_statements.store_company` — `ticker` first,
> falling back to `company` only for a bare pack that carries no ticker —
> which is the same precedence `kpi_xbrl_ingest` uses for the dimensional and
> top-line lanes. So one filer has ONE key, and a single `dump --company AAPL`
> feeds the spine view every lane's series at once. The envelope's `company`
> (the SEC `entityName`) is display metadata: it is what makes the CIK-decoy
> rejection readable by naming the entity whose facts came back empty.

**Why selection happens at read time.** Storing a canonical slug makes
concept selection a write-time, ONE-WAY decision into an append-only store.
Measured over the 47-filer probe, a per-company selection rule is stale for
24 of 46 filers (worst: HD revenue −16y, MSFT revenue −15y). Storing
as-reported keeps both candidates, so selection stays a pure function that
can be corrected and re-run.

### Capability limit: the history floor is ~2009, not 20 years

**This lane cannot return two decades of history, and no change to this repo
can make it.** US XBRL history begins with the SEC's 2009-2011 phase-in, so
`companyfacts` simply holds nothing earlier. Measured over the committed
47-ticker probe (captured 2026-07-26; committed evidence at
`investing-toolkit/tests/data/fixtures/us_statement_shapes_probe_2026-07-26.json`,
re-derivable via its sibling `capture_us_statement_shapes_probe.py`):

- **0 of 46** usable filers have **≥20 usable years**; the **median is 18**.
- The floor moves FORWARD one year per calendar year. It never deepens
  backward, so waiting does not help a request for 20+ years.
- 1 of 47 tickers resolves to an entity carrying **zero** us-gaap concepts
  (refused loudly); 2 more are truncated at the source (GOOGL from 2012,
  DIS from 2016) and surfaced, not stitched.

Pre-2009 history is reachable only via HTML/text extraction (which this repo
forbids) or a vendor-standardized source (an uninspectable model, and a
separate product decision). Expect ~18 years — plan analysis accordingly
rather than reading a short table as a bug.

### The balance-identity flag is stored but NOT rendered

Per period `derive` checks `total_assets − (total_liabilities + mezzanine +
WHOLE equity)` and attaches a `balance_identity` flag when the residual
exceeds **1e-5 relative** to total assets. It never suppresses, refuses, or
alters a value: a residual points at THIS VIEW's per-period concept
selection, not at the filer's numbers.

**`tearsheet_format` does not read the flag**, so a flagged period and a
clean one look identical on the rendered tearsheet. To see it, read
`derive`'s RAW JSON instead of piping it onward — the flag rides on the
`total_assets` series' period entry (the identity's subject and its
denominator), one per flagged period:

```
uv run scripts/kpi_store.py dump --company AAPL \
  | uv run scripts/kpi_spine_view.py derive \
  | python3 -c 'import json,sys; [print(json.dumps(p["balance_identity"])) \
      for s in json.load(sys.stdin)["series"] if s["kpi_id"] == "total_assets" \
      for p in s["periods"] if "balance_identity" in p]'
```

Each flag carries `residual`, `relative_residual`, `tolerance`,
`equity_kind` (`parent_only` vs `incl_NCI`, so a `minority_interest` of 0
is readable), the `components` used, and `checked_vintage` — the ONE filing
they were all read from (`accessions` is that same single accession).

**The identity is computed WITHIN one filing, never across.** A restatement
appends a new vintage rather than overwriting, so comparing each component's
own latest observation mixes filings and flags filers that balance perfectly.
The check uses the newest vintage carrying all three totals — what a reader
sees as current — which is why the flag's `components` can differ from the
values the tearsheet renders for that period, and why it names the vintage.
A period missing any required component, or that no single filing covers,
is **not** flagged — uncheckable is not wrong, and 13 of 46 filers never tag
a total `Liabilities` at all.

## Workflow: TW iXBRL -> tearsheet

The TW analog, producer-only (no store/tearsheet code change):

1. **Fetch** the TW iXBRL canonical from `data-markets`
   (`twse_ixbrl.py` / `pack_tw.py memo-fetch`) and assemble a filing
   envelope pairing the `canonical` with the parsed `facts` and the filing
   coordinates (`co_id`/`year`/`season`/`report_id`) — the facts carry the
   board authorisation-for-issue date `as_of` source, which the canonical
   alone does not.
2. **Ingest** the envelope into this skill's store:
   `kpi_tw_ingest.py ingest --filing <filing.json>` — derives `basis` (C/A),
   `as_of` (the non-wall-clock authorisation-for-issue date), and TW
   provenance from the coordinates, maps the canonical to points via
   `kpi_tw`, and appends each to `kpi_store` (honors `KPI_STORE_DIR`;
   idempotent — re-ingesting the same filing adds no duplicate).
3. **Render** the tearsheet via `report-kpi-tearsheet`, which reads the
   now-populated store directly (TW points share the market-agnostic schema).

## CLI (kpi_8k_candidates) — 8-K semi-auto KPI intake (Route B)

`scripts/kpi_8k_candidates.py` — the tier-① intake lane for an 8-K
earnings-release exhibit (US SEC). It is a **THREE-LAYER** workflow;
each layer has a fixed role and **the LLM never produces or alters a
`value` or a `source_*` coordinate — it only proposes semantic labels**
(the value is mechanically produced in Layer 1 and human-ratified in
Layer 3; Layer 2 fills `kpi_id`/`unit`/`period` only).

**Layer 1 — MECHANICAL (`propose`, deterministic code):** subprocesses
data-markets `exhibit_tables.py` on the exhibit HTML, then emits RAW
candidate points — each carrying the verbatim row-label path, the exact
printed `value` string (never re-parsed), a verbatim `period_hint`
(column header) and a verbatim `unit_hint` (the table's own `(in …)`
caption, or `null`) — both ADVISORY, the source coordinates
(`source_accession`, `source_table_id`, `source_cell_ref`), and
`confirmed: false`. The
semantic slots `kpi_id`/`unit`/`period` are emitted as explicit `null`
with a `needs_semantic: ["kpi_id","unit","period"]` list. **This layer
never invents a slug, a unit, or a normalized period** — the value and
its coordinates come straight from the filed bytes to the file.

```
uv run scripts/kpi_8k_candidates.py propose --html ex991.htm \
    --accession 0001065280-25-000033 --out candidates.json
```

**Layer 2 — LLM PROPOSAL (the agent running this skill; prose, not
pytest):** for each candidate, read its verbatim `label` path,
`period_hint`, and `unit_hint` and FILL the three `needs_semantic` slots
as PROPOSALS —
`kpi_id` (a stable slug, e.g. `global_streaming_paid_memberships`),
`unit` (e.g. `millions`), and a normalized `period` (e.g. `2024-Q4`).
Fill ONLY from what the verbatim label/header text says; do NOT alter
`value` or any `source_*` coordinate. These are proposals, not truth —
their consequence is gated by Layer 3 code below, so a wrong guess is
caught at commit, never silently stored. (This layer is prose-instruction,
verified by dogfood, not by a unit test.)

**Layer 3 — HUMAN confirm-all + `commit` (deterministic gate):** the human
ratifies each proposal and flips `confirmed: true`; then `commit
--company <T>` appends into the tier-① store via the EXISTING
`kpi_store.append`. The gate order per candidate: an unconfirmed
candidate is **skipped** (never written); a confirmed candidate still
carrying a null semantic slot is **refused loud** (`_missing_semantic` —
this confirm gate enforces `unit`, which the store never inspects); a
candidate the store's own provenance/`as_of` guard rejects is **refused
loud** (`kpi_store.append`, un-weakened). Only confirmed-and-complete
points land.

```
uv run scripts/kpi_8k_candidates.py commit \
    --candidates candidates.json --company NFLX
```

| Subcommand | Flag           | Required | Notes                                              |
|------------|----------------|----------|----------------------------------------------------|
| `propose`  | `--html`       | yes      | Path to the raw exhibit HTML                        |
| `propose`  | `--accession`  | yes      | Filing accession (source provenance)                |
| `propose`  | `--out`        | yes      | Path to write the candidates JSON                   |
| `commit`   | `--candidates` | yes      | Path to the candidates JSON (propose output)        |
| `commit`   | `--company`    | yes      | Company/ticker key (one filing = one company)       |

`propose` exits **0**, writing the candidate list. `commit` exits **0**
when every confirmed candidate committed, and **non-zero** when ANY
confirmed candidate was refused-incomplete — a silent partial commit
would defeat the fail-loud contract. The store's append-only bitemporal
model and the confirm-all trust gate are **unchanged**: this lane feeds
the SAME `kpi_store.append`, adding only the mechanical/LLM/human split
in front of it.
