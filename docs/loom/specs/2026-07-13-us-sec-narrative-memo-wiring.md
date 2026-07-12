# Brief — Wire US SEC narrative into the memo data pack

Status: brainstorming output, awaiting user sign-off → `writing-plans`
Arc: US SEC primary-source layer, capability 1 of 3 (narrative) — the
consumer-side half deferred from PR #552 (scope option A).
Change-folder: `docs/loom/2026-07-12-us-sec-primary-source-layer/`
Closes the folder's open concern **C6 — "Memo-feed contract undefined"**
(`proposal.md:179`).

## Design-side on-ramp

Axis 0: offered — none fired. A change-folder already covers this arc
(reception row 3 requires *no* spec/change-folder to exist), and the work
is a brownfield increment to an existing, test-covered data pack. Proceed
direct to loom-code.

## Problem

**Job:** *When I write an equity memo on a US company, I want to read what
management themselves said about the business — in their own filed words —
so my verdict rests on primary sources instead of my inference from the
numbers alone.*

Today the memo data pack carries only quantitative surfaces: yfinance
`info`/history, SEC XBRL `facts`, and the DCF-normalized statements. The
narrative capability that PR #552 shipped (`fetch_narrative_sections`,
segmenting every item of a 10-K/10-Q and every reported item of an 8-K)
is reachable **only** from the CLI (`--action narrative --accession X`).
No pack calls it, so the memo writer has never seen a single sentence of
management's own text.

The gap is not "a key is missing from a dict" — it is that the memo's
qualitative claims currently have no primary-source anchor to cite, which
is exactly the failure class the #548 defense lines were built to stop
(a weak model padding a verdict with unsourced assertions).

## Users

**Job story:** *When I run `report-equity-memo` on a US ticker and reach
the qualitative sections (business description, risk, management's own
framing of the quarter), I want the seed bundle to already contain
management's filed text with reconstructable provenance, so I can quote
and cite it verbatim rather than paraphrase from memory or invent.*

Concretely: `investing-toolkit:report-equity-memo` (the orchestrator) →
`domain-teams:investing-team` (the analyst that writes and is gated). The
analyst runs under gates that already demand verbatim transcription and
primary-source citation (CHK-CIT-007), so it needs *text it can cite*, not
a summary.

## Smallest End State

`pack_us.pack_memo_fetch(ticker)` returns one additional top-level key,
`sec_narrative`, containing management's filed text for the latest 10-K,
the latest 10-Q, and the **earnings 8-K of each of the last N quarters**
(N=4 by default) — with:

- section bodies on disk (`text_path`, paths-not-content — the existing
  producer contract; the pack stays small),
- full provenance per section (accession / CIK / item id / filingDate /
  reconstructable Archives URL) — already emitted by the producer,
- a **structurally visible** failure surface (see Decision) so a partial
  or failed narrative can never read as complete.

Nothing else changes. No new analysis, no filtering of items, no memo
prose changes beyond what the existing disclosure gate already forces.

## Current State Evidence

- **Forward (producer → what exists):** `fetch_narrative_sections(accession)`
  — `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py:1204`.
  Takes **an accession only** (no ticker, no form). Returns
  `{accession, cik, form, filingDate, sections[], section_count,
  narrative_status, failed_items[], _cache}` (`sec_edgar_client.py:1283-1301`);
  `narrative_status` ∈ ok/partial/failed computed at `:1276-1282`. Success
  sections are `{item, text_path, disclosure_status, **provenance}`
  (`_build_section`, `:1081`); failure slots carry an `"error"` key
  (`:922`, `:936`, `:956`, `:977`). Cache key
  `sec_edgar/narrative_sections_{accession}`, **immutable TTL** (`:69`, `:1249`).

- **Reverse (consumer → what is missing):** `pack_us.pack_memo_fetch`
  — `pack_us.py:552-597`. Already fetches the filings list
  (`--action filings --forms 10-K,10-Q,8-K --limit 8`, `pack_us.py:561-565`),
  **so the accessions are already in hand** — no new lookup is needed, only
  a selection policy. `pack_us.py` and `pack.py` contain **zero** occurrences
  of "accession"; ticker→accession resolution is **ABSENT** package-wide.
  Each sub-fetch is a `uv run` subprocess (`run_client`, `pack_us.py:187`,
  300s timeout) — so each extra filing narrated = one extra subprocess of
  memo latency.

- **Error (the classifier's blind spot — the CRITICAL TRAP):**
  `pack.py:_classify_result` (`pack.py:253-310`) walks **exactly one level**
  and, per `_dict_section_status` (`:197-216`), inspects only a section's
  **non-empty dict-valued sub-fields**. The narrative wrapper's per-section
  errors live inside `sections`, which is a **list** → structurally
  invisible. Its own docstring names this ceiling (`pack.py:264-278`).
  Compounding it, `pack_inventory._classify`
  (`skills/report-equity-memo/scripts/pack_inventory.py:41-49`) marks any
  dict with ≥1 key as `present: true` → an **error-only narrative wrapper
  would be inventoried as data-present** (false presence — the very thing
  `pack_inventory.py` exists to prevent, inverted).

- **Data (what the downstream contract already guarantees):** the memo seed
  bundle schema (`skills/report-equity-memo/references/schema-phase4-input-bundle.json`)
  puts the pack under `fetch` and does **not** set `additionalProperties:
  false` → a new top-level pack key flows through without a schema change.
  And `references/phase4-seed-contract.md:50-57` already mandates:
  *"transcribe upstream `_status`/`warnings` content at verbatim grade —
  no silent dropping, softening, or relabeling"*, enforced by CHK-CIT-007.
  **Therefore: if the narrative's degradation reaches the pack's `_status`,
  the memo's disclosure obligation is already automatic** — no new
  disclosure channel needs building.

- **Boundary (live-probed, 2026-07-13, real SEC API):** `data.sec.gov`
  `submissions` `recent` carries an **`items`** array (and `reportDate`)
  alongside form/date/accession — verified live against CIK 0000320193.
  8-K earnings releases are identifiable by item **`2.02`** with **zero
  extra fetches**. But `list_filings` (`sec_edgar_client.py:320-347`)
  **drops both fields**. Critically, AAPL's *most recent* 8-K at probe time
  was `items='5.02'` (an executive-change filing), while the earnings 8-K
  was the one before it (`items='2.02,9.01'`) — **"take the latest 8-K"
  would select the wrong filing.** Selection MUST be by item code, not by
  recency.

**Evidence paths:** `sec_edgar_client.py`, `pack_us.py`, `pack.py`,
`report-equity-memo/scripts/pack_inventory.py`,
`report-equity-memo/references/{schema-phase4-input-bundle.json,phase4-seed-contract.md}`,
`tests/data/test_sec_narrative.py`, `tests/data/fixtures/data-us-memo-fetch-sample.json`
(confirmed: carries **no** narrative key today — clean additive surface).

## Decision

We wire the narrative into `pack_us.pack_memo_fetch` under a new top-level
key `sec_narrative`, covering **the latest 10-K, the latest 10-Q, and the
earnings 8-K (submissions `items` ⊇ `2.02`) of each of the last N quarters,
N=4 by default**. **User decision, 2026-07-13**, overriding the researched
recommendation of 10-K-only: the user wants the fullest primary-source set,
consistent with this arc's standing principle that the data layer performs
pure acquisition and defers the read/relevance decision downstream.

To make that selectable, `list_filings` is extended to preserve the
submissions API's `items` and `reportDate` fields (live-verified to exist).
Selection is **by item code, never by recency** — the live probe proved the
latest 8-K is often not the earnings one.

**The selection window is anchored in TIME (quarters), never in filing
count.** *User correction, 2026-07-13*, and it is the stronger design: 8-K
volume is unpredictable (it is the "any material event" form — the live
probe found AAPL filing 4 8-Ks in ~3 months, mixing earnings 2.02 with
5.02 executive changes and 5.07 shareholder votes), so a count-based window
("last 8 rows") silently drifts with a company's filing frequency, while a
period-based window does not. N=4 quarters is chosen to align with **TTM**
(trailing twelve months) — the repo has a recorded failure where a weak
model mislabeled FY figures as TTM, so four consecutive earnings releases
give the memo a genuine rolling year of management commentary rather than
an arbitrary count. N is an overridable parameter (the user framed it as a
variable; this is a real policy knob, not speculative config).

Four earnings releases also give the memo something one release cannot:
**cross-quarter drift in management's own framing** (softening tone,
guidance walked down) — a signal that only exists across a series.

**Failure must be structurally visible, not merely announced.** Axis-4
research (5 shipped approaches; see below) converged on this: a status
*string* is the "merely-optional signal" every source says consumers ignore,
and both of our readers (`_classify_result`, `pack_inventory._classify`) are
**structural** readers. So `sec_narrative` carries, at its own top level:

- `failed_items` — hoisted to **depth 1** where the one-level classifier
  can see it (AWS batch shape: failures are a top-level sibling list, never
  nested inside item records);
- a **required count triple** `{requested, succeeded, failed}` — turning
  "is this complete?" into an **arithmetic reconciliation** rather than a
  string a consumer may skip (Elasticsearch `_shards` shape), and giving
  `pack_inventory` a hard predicate for presence (`present ⟺ succeeded ≥ 1`)
  that kills the false-presence bug.

A filing that fails entirely emits an explicit error-bearing slot — never a
silently absent key (repo fail-loud convention). A ticker with **no** 8-K
carrying item 2.02 within the filings window emits an explicit **gap** slot
naming the reason — not silence.

**We will NOT**: filter or rank items (the all-items pivot stands — the data
layer never bakes in an analysis judgment); summarize, score, or interpret
any text (the parser emits the text, never an LLM — the arc's load-bearing
anti-fabrication invariant); change memo prose or gates (the existing
verbatim-disclosure gate already absorbs the new `_status` content); touch
`pack_jp/tw/kr/cn`.

## Alternatives Considered (Axis 4 — WebSearch, EN + JA)

**Fork A — how partial failure is represented** (5 approaches found):
Elasticsearch `_shards` required counts (elastic.co search-api docs) · AWS
batch `Successful`/`Failed` arrays at HTTP 200 (SQS `SendMessageBatch` ref:
*"you should check for batch errors even when the call returns an HTTP
status code of 200"*; DynamoDB `UnprocessedItems`) · GraphQL `data`+`errors`
with null-propagation (graphql-js docs; Hasura) · HTTP 207 Multi-Status
(RFC 4918 §13) · JP consumer-side discipline (ZOZO, Gaudiy, coconala tech
blogs; Salesforce Bulk API JA docs).

**EN vs JA — agreement on shape, different emphasis, and the JA framing is
the one that names our bug.** EN sources argue the transport envelope
(207 vs 200) and producer-side arrays. JP sources skip that debate entirely
and go straight at the consumer failure mode we actually have —
「部分データが完全データに見える」(partial data looks like complete data) —
and their remedy is always to make failure **reconcilable per item**
(trace id / `errors[].path`), **never a status string**.

*Chosen:* AWS shape (top-level `failed_items`) + Elasticsearch shape
(required counts). *Rejected:* status-string-only (ignored by structural
readers — the documented failure mode); HTTP 207 (no transport layer here);
GraphQL null-propagation (its forcing function only pays off when consumers
read field-by-field — ours read section-wise). **Conditional reversal:** if
a future consumer iterates `sections` element-by-element, switch to the
GraphQL shape (make failed items structurally absent from `sections`, keep
`failed_items` as diagnostics only).

**Fork B — which filings the memo reads** (4 approaches found): 10-K as the
mandatory floor (fe.training; Stanford GSB library guide — only audited
filing with the full narrative set; **Q4 exists only in the 10-K**, as
companies file just three 10-Qs a year) · +10-Q (timely, unaudited, thin
marginal narrative — its MD&A is largely a delta and its risk item usually
says "no material changes") · +8-K/EX-99.1 (FinanceBench — 10,231
analyst-style questions built with 15 finance domain experts — grounds its
corpus in 10-K/10-Q/**8-K**/earnings material; the EX-99.1 carries the
quarter's actual numbers weeks before the 10-Q) · MD&A/risk-factor tone
literature (Loughran-McDonald), which argues the 10-K narrative is the
section with demonstrated marginal information.

**EN vs JA — a genuine DISAGREEMENT, surfaced rather than silently
resolved.** Japanese practice **inverts** the reading order: JP guides
(kabu.com; diamond.jp) say read the 決算短信 (the 8-K analogue) **first**,
because it lands within 45 days and carries 連結業績予想 — management's own
full-year forecast — and consult the 有価証券報告書 (10-K analogue) only to
go deeper. **This does not transfer to EDGAR:** US 8-K/EX-99.1 press
releases carry no mandated forward guidance, so the JP reason for reading
the fast filing first is absent here. Treated as evidence about JP practice,
not about our design.

*Researched recommendation was 10-K-only (start narrow; accession-keyed
immutable caching makes widening later cheap and idempotent).* **User chose
the max set (10-K + 10-Q + earnings 8-K)** — recorded as a deliberate
override, not an oversight. Trade-off accepted: 3 subprocesses of memo
latency instead of 1.

## What Becomes Obsolete

- `pack_us.py:594` — `us_specific.non_gaap_eps_note`:
  *"Out of scope for T3 v1; lives in 8-K narratives."* Once the earnings
  8-K's narrative IS in the pack, this note is a stale pointer to a gap that
  no longer exists. **Remove or rewrite it in the same PR** (leaving it is
  technical debt by design).
- Change-folder concern **C6** ("Memo-feed contract undefined",
  `proposal.md:179`) — this brief + its implementation define it; mark C6
  resolved for the narrative capability.

## Out of Scope

- `financial-table-xval` and `operational-kpi` (the arc's other two
  capabilities) — untouched.
- Non-US packs (`pack_jp/tw/kr/cn`) — the narrative producer is SEC-only.
- Any change to which *items* are segmented (all-items pivot stands).
- Memo prose / template / gate changes beyond the automatic `_status`
  disclosure the existing contract already forces.
- Non-99.x 8-K attachments (EX-10 / EX-21 / certs / XBRL) — explicitly out
  of scope per the shipped narrative spec.
- Archiving the change-folder (2 of its 3 capabilities remain unshipped).

## Open Questions

1. ~~**Filings-window depth** (count-based)~~ — **RESOLVED, and the question
   itself was wrongly framed.** The window is now anchored in **time
   (N=4 quarters)**, not filing count; see Decision. The `--limit 8` count
   window is retired for narrative selection: the selection pass requests a
   window generous enough to cover N quarters (the submissions fetch is a
   single cached call, so a larger window is nearly free) and then filters
   by period. A quarter with **no** item-2.02 8-K found emits an explicit
   gap slot naming the quarter — never silence, and never a short list
   passed off as complete (this is exactly what the required
   `{requested, succeeded, failed}` count triple makes unfakeable:
   `requested` is fixed by the policy, not by what happened to come back).
2. **`pack_inventory` second-level expansion.** Today only `mops` gets a
   hardcoded sub-inventory (`pack_inventory.py:62-66`). Whether
   `sec_narrative` warrants the same treatment (so the memo's inventory
   check can see per-filing presence) is a small, separable call — flagged,
   not pre-decided.
