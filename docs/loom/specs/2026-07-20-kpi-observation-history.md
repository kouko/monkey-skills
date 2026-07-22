# Brief: KPI observation history — what I hold, and whether it still holds

Date: 2026-07-20 (revised 2026-07-21 — scope narrowed to the US lane after a
layer-contract recon; open question 1 closed by research)
Arc: narrative-evidence (investing-toolkit). Follows Slice A Part 1 (#593, 2.28.0)
and Part 2 (#594, 2.29.0). Supersedes the BACKLOG's "Slice C" framing.
Design-side on-ramp: offered — the deliverable is CLI/query machinery in a repo
that has never used DESIGN.md/ui-flows.md for its report skills; user chose to
proceed direct.

## Problem

The user's job, as first stated: *"avoid having to fetch from scratch every time
I want to use it"* — the measurements below reframed that job into a different
and better one.

Fetching is not the problem. A cold `companyfacts` fetch is **~0.9 s and
~262 KiB on the wire** (measured, n=1 per filer; 3.75 MB uncompressed, but the
client already requests gzip — `sec_edgar_client.py:104`).

The real problem the measurements exposed: **a figure the user recorded can stop
being what the company says, silently.** J&J's FY2021 revenue was 93,775,000,000
in the FY2021 10-K, repeated unchanged in the FY2022 10-K, and re-presented as
**78,740,000,000** in the FY2023 10-K — a −16% revision to a two-year-old annual
figure, in an ordinary 10-K, no amendment, no reason code. Measured true-positive
rate across 4 filers: **2.43% of period groups** (51,631 groups, 1,252 genuine
changes; weakest filer 1.56%; rounding artifacts are only 11.7% of raw conflicts).

Two facts make this tractable rather than hopeless:

- **Filings are immutable.** Verified: 11/11 sampled fact rows match the bytes of
  the filing they are attributed to. A restatement does not rewrite the old
  filing — it appends a new observation under a new accession. Both coexist, and
  **SEC's own API returns all of them**. Collapsing them to one scalar is a choice
  this tool would be making, not one the source forces.
- **So what changes is not a document, it is the ANSWER to a question.**
  "What was FY2021 revenue?" has three observations, each true of its own filing.

Job story: *When I look at a figure I collected months or years ago, I want to
know what I hold and whether it is still what the company says, so I can trust my
own history instead of silently carrying a stale number.*

## Users

The repo owner, working alone, long-horizon fundamental research on a few dozen
names. Conditions that shape the design:

- Runs locally, per-machine store under XDG data dir; no team, no server.
- Accumulates prose-derived operational KPIs that each cost a **human
  confirmation** — unreproducible, therefore irreplaceable.
- Also consumes XBRL financial facts, which are machine-reproducible and
  empirically stable (0 value changes across 849,541 fact keys over ~2.5 months).
- Today cannot answer "what do I have for AMZN?" at all: the store is not
  enumerable and `period` is not sortable.

## Smallest End State

Four capabilities, **all scoped to the US lane** (see §Scope decision).

1. **The store can be enumerated.** Given a company (and optionally a KPI), list
   the observations held, without already knowing the query key.
2. **A stored point's period IDENTITY is the raw `(start, end)` context pair**,
   while its `fiscal_period` / `fiscal_year` LABELS remain first-class fields the
   analysis layer computes on unchanged. The store keys, sorts, and same-period-
   matches on the date pair; analysis keeps reading `FY2021-Q4` labels exactly as
   today. See §Period model — this is NOT "labels are display-only".
3. **Every newly written point carries an integrity stamp**: a hash of the
   anchored span, plus the flattener/surface version. Write-time only.
4. **`history` answers "what has been said about period P, and when"** — reading
   observations across filings and flagging when they disagree. Coverage ("which
   periods do I have / lack") falls out of (1)+(2) as a read-side query.

NOT in the smallest end state: any rendered tearsheet, any retention policy, any
new storage of XBRL facts, any read-time drift re-verification.

## Period model — identity vs coordinate (the crux, evidence-backed)

A fiscal period plays two roles, and conflating them is the bug this arc keeps
hitting (a clean-looking label that lies). Keep them separate:

| Role | Field | Who uses it | Rule |
|---|---|---|---|
| **Identity / sort / same-period match** | raw `(start, end)` (instant → `end`) | the store, `history` | key on the date pair; sort by `end`; match exact `(start,end)`, fallback = `end` snapped to month-end + `qtrs` |
| **Analysis coordinate** | `fiscal_period` (Q1–Q4/FY) + `fiscal_year` | the analysis layer, unchanged | derived in Layer 1 from the filing's own declared fiscal-year-end, NEVER `end[:4]` and NEVER the companyfacts `fy` tag |

**Both are produced in Layer 1, and the derivation ALREADY EXISTS** — do not
build it: `sec_edgar_client._derive_fiscal_label` (`:2658`) classifies each fact
from its filing's own dei fiscal-year-end + a `FISCAL_BOUNDARY_TOLERANCE_DAYS=10`
guard (`:2495`), and the `kpi-quarterly` pack already emits per fact
`fiscal_period_focus` / `fiscal_year_focus` / `period_end` (`sec_edgar_client.py`
~`:3404`). This slice REUSES that; it does not re-derive fiscal geometry (the
`kpi_xbrl.py:46-64` "never re-derive" discipline holds).

**The analysis layer does not touch dates.** It receives `FY2021-Q4` as before
and computes quarters/years on it. The date pair is a below-the-analysis identity
key: it exists so that when one `FY2021` label carries two values across filings
(J&J 93,775 vs 78,740), the store can confirm both describe the same real period
and order them by filing. Answering the user's question directly: **classification
happens in the data layer, not the analysis layer** — analysis still works in
quarters/years, exactly as it does today.

**Evidence this is the industry split, not a local invention:**
- 14-filer / 64,044-group measurement: raw `(start,end)` byte-identical 98.99%;
  the `fy` tag disagrees across filings 98.3%; `end[:4]` mis-keys 6.7% for Dec
  filers but 55–64% for Jun/May fiscal-year-ends (a Dec-only sample hides it).
- `edgartools` keys internally on the raw range and fixed exactly this as Issue
  #816 (regression tests name JNJ/PFE/AAPL/WMT/TGT/MSFT).
- Vendor APIs agree unanimously: Alpha Vantage keys on `fiscalDateEnding` (no
  label field at all); Polygon on `start_date`+`end_date` with separate
  `fiscal_period`/`fiscal_year`; FMP `date` + `calendarYear` + `period`.
- Japan's EDINET `jpdei` taxonomy carries absolute 当会計期間開始日/終了日 as
  first-class fields plus a separate coarse 会計期間の種類 enum whose **Q5** value
  is a purpose-built irregular-period (変則決算) accommodation — the exact split.
- No counter-example found (a serious system keying on a fiscal label and
  thriving); the only candidates are login-walled terminals.
- Honest limits: 14 US large-caps, fiscal-year-end months Feb/Mar/Apr/Nov absent,
  no 10-K/A tested; TW/TEJ period-key convention not reached. Sufficient for a
  US-only slice, not a universal proof.

## Scope decision — US lane only, deliberately

A layer-contract recon (2026-07-21) found that period canonicalization **belongs
in Layer 1** — the repo's own `docs/normalization-contract.md:255-262` forbids
computation in Layer 2's input and defines staging as "mapping + cast + rename
only"; only Layer 1 holds the fiscal-calendar context needed to do it correctly
(`sec_edgar_client.py:2659-2682` warns explicitly against deriving fiscal year
from a bare date); and Anti-pattern E (`:277-285`) names "adapter inside Layer 2"
as grounds for PR rejection.

But Layer 1 is **five separate per-market scripts**, not one:

| module | lines | canonical path |
|---|---|---|
| `pack_us.py` | 1238 | mature: concept-mapping chains, cross-concept merge, filed-date dedup |
| `pack_jp.py` | 801 | **empty stub on the EDINET (better) path**; yfinance label-match fallback only |
| `pack_tw.py` | 769 | real TIFRS mapping, but emits `periods` structs under a different key |
| `pack_cn.py` | 730 | yfinance label-match |
| `pack_kr.py` | 673 | yfinance label-match |

JP/KR/CN/TW carry **four near-identical copies** of one
`_build_canonical_from_yf_financials` + label map (parallel line numbers
`pack_jp:190/220/260`, `pack_tw:191/221/261`, `pack_cn:201/229/269`), which is why
one alignment bug reproduces at `pack_jp:274`, `pack_tw:275`, `pack_kr:325`.

Unifying period across all five would mean editing four copies (guaranteed to
miss one) or de-duplicating first — a separate slice. The prose lane and the
restatement problem are both US-only today, so **this slice touches `pack_us.py`
alone**, which is also the healthiest module. Recorded as a deliberate limit, not
an oversight.

## Current State Evidence

- **Forward** — `kpi_store.append` stores a point dict verbatim with no field
  whitelist (`kpi_store.py:189-213`); enforces only provenance completeness
  (`:113`, `:116-125`) and a non-wallclock `as_of` (`:128-148`). Dedup key is the
  5-tuple `(company, kpi_id, period, as_of, source_accession)` (`:151-155`) — it
  ALREADY models multiple observations of one period from different filings,
  exactly what capability (4) needs. Adding a field costs the store nothing; it
  must be added at each producer (`kpi_prose_candidates.py:649-668`,
  `kpi_8k_candidates.py:265`).
- **Reverse** — `kpi_memo_feed` does NOT read the store (`kpi_memo_feed.py:12-14`,
  no `import kpi_store`). The XBRL series builder reads a fact pack from disk,
  never the store (`kpi_xbrl.py:1626`, `:1674`, `:1677`). This brief does NOT
  couple the lanes by storage — only by a shared period vocabulary.
- **Error** — a duplicate dedup key is a silent no-op, first-record-wins, even
  when `value` differs (`kpi_store.py:207-210`). Re-appending an existing point
  under a new integrity stamp would be silently dropped, so capability (3) applies
  to NEW writes only; backfill is unavailable without changing the dedup key.
- **Data** — the Layer1→Layer2 contract is **implicit exactly at period**. Field
  names are conventionally agreed and documented; period semantics are not agreed,
  not schema'd, not tested. Five representations coexist: US/JP/KR
  `_meta.<field>.fiscal_year_ends` (ISO strings, `pack_us.py:453`); TW
  `_meta.<field>.periods` (structs, `twse_ixbrl_canonical.py:278`); `kpi-quarterly`
  `fiscal_calendars` + per-fact `fiscal_year`/`period_end` (`pack_us.py:1013-1016`);
  EDINET raw `relative_year: "CurrentYear"` (`edinet_client.py:511`). The canonical
  value arrays are **bare positional lists** — period lives only in `_meta`, matched
  by array index. On the store side, `period` is an opaque string: an LLM proposal
  on prose points (`kpi_prose_candidates.py:652`), `str(fact["fiscal_year"])` on
  XBRL points (`kpi_xbrl.py:452-476`).
- **Boundary** — the store cannot be enumerated: series files are keyed
  `<company>__<kpi_id>__<sha1[:12]>.json` (`kpi_store.py:68-93`), the digest is
  one-way, and there is no `glob`/`iterdir` in `analysis-kpi/scripts/`. Every read
  path requires the caller to already know `(company, kpi_id, period)`.
  `review_queue.py:54-57`/`:76`/`:107` is the closest precedent for a per-store
  aggregate. The 31 JSON Schemas are toothless here — canonical blocks are
  `{"type":"object","additionalProperties":true}` with no inner properties.

Evidence paths: `investing-toolkit/skills/analysis-kpi/scripts/*.py`,
`investing-toolkit/skills/data-markets/scripts/{pack*,sec_edgar_client,cache_util}.py`,
`investing-toolkit/docs/normalization-contract.md`, `investing-toolkit/docs/adr/`.
Measurements: `scratchpad/{xbrl-refetch-measurements,restatement-classification,
xbrl-api-mutability,conflict-resolution-practice}.md`.

## Constraints the design must satisfy (from industry research, 2026-07-21)

These are findings, not preferences — each rules out a cheaper design.

1. **Vintages are an unbounded list, not a pair.** ネットワンシステムズ (7518) has
   three vintages of one filing (2018-04-26 → 訂正 2020-03-12 → 再訂正 2020-12-16).
   An `original` + `restated` two-slot schema is insufficient.
2. **Track vintage per line item, not per filing.** 田中精密工業 (7218) had its
   cash-flow statement corrected across 9 filings while the P&L was untouched. A
   filing-level `is_restated` flag is the wrong granularity.
3. **Detection must be a value diff across vintages, never an event
   subscription.** TW 證交法施行細則 §6 permits sub-threshold corrections to skip
   restatement entirely (「得不重編」) — figures may change with **no restatement
   event to detect**. Any design listening for announcements misses these
   structurally.
4. **Normalize unit and precision before comparing, or manufacture false
   conflicts.** The same figure appears as「12,345（百万円）」and「12,345,678
   （千円）」across JA document types; our own measurement found 11.7% of raw
   conflicts were rounding artifacts.
5. **A superseded value is not "wrong".** J&J (spinoff), IFRS 17 retroactive
   application (寶成 9904), and 東芝 (error correction) are three different causes
   with one shape. Presenting the old value as an error is a category mistake.

## Decision

Build the four capabilities, US lane only. Do NOT build a cache, a retention
policy, a stored coverage file, or a tearsheet.

**Conflict resolution — open question 1 is now closed by research:**

- **(B) different source types, same period** (press release vs tagged filing):
  **source precedence, audited wins, loser retained.** EN and JA agree without
  qualification; Japanese practice is explicit — 有報 (statutory, audited) over
  短信 (preliminary, no audit obligation): 「精度が求められる場面では、有報の数字を
  優先するのが原則」. A system may apply this automatically and be right ~always.
- **(A) same source type, different filing dates** (the J&J shape): **do not
  auto-decide — expose the choice.** No vendor resolves this, because the correct
  answer flips by purpose: replaying a past decision needs as-first-reported
  (93,775, avoiding look-ahead bias); comparing FY2021 against FY2023 needs the
  latest re-presentation (78,740, which is the *point* of a discontinued-ops
  restatement). Store every vintage keyed by when it became knowable; let the
  caller pick.

**Why no cache** — measured ~0.9 s / ~262 KiB. Per-accession slicing would save
83–91% of parse and storage but **~0 network bytes**: `companyfacts` is one
indivisible URL with **no conditional-request support** (probed: `cache-control:
no-cache, no-store`, no ETag, no Last-Modified; `If-Modified-Since` → 200 full
body). The bulk `companyfacts.zip` is 1.39 GB — it only pays off above ~5,200
companies.

**Why no retention policy** — the "≥10yr industry norm" at BACKLOG:167 is **not
evidenced**. CFA Institute's financial-analysis material specifies no lookback
window; practitioner guidance clusters at 3–5 years; 会社四季報 prints 5 periods by
default; vendors sell depth as product tiers. No consensus exists to conform to.

**Why no stored coverage file** — a materialized coverage artifact is a second
source of truth that will drift. dbt-expectations / Great Expectations precedent
is on-read gap detection; our store is local JSON, scannable in milliseconds.

**Why not copy XBRL facts into the store** — machine-reproducible and measured
stable; the store exists for values whose human confirmation is unreproducible.

## Alternatives Considered

- **Store the long-term series as a durable cache** (the user's original idea).
  Rejected on measurement: no fetch cost worth avoiding, no conditional-request
  path to make refresh cheap. Would add a second source of truth for zero gain.
- **Do Part 3's full hash+version anchor first.** Partially adopted: the WRITE
  half is pulled in (capability 3) because recording cannot be added
  retroactively — the dedup key makes backfill a silent no-op — while the
  expensive READ-time re-verifier stays in Part 3. A sequencing judgment.
- **Canonicalize period across all five markets** (what the layer recon
  recommends on correctness grounds). Rejected on scope: four copy-pasted
  fallbacks and a JP stub stand in the way; see §Scope decision.
- **Render a tearsheet now.** Rejected: the prose lane is not user-invocable
  (`kpi_prose_candidates.py` has no CLI, appears in no SKILL.md) so there is
  nothing to render; and EN/JA/ZH research found **no shipped public format** for
  "one company, many operating KPIs, many years".

Grounding for capability (3): shipped annotation systems hash the **anchored text
itself** (STAM per-span checksum, verified at parse time, fail-closed;
standoff-mode whole-document MD5). Nobody uses a normalizer version as the primary
trust anchor — the hash is load-bearing, the version supplementary.

## What Becomes Obsolete

- `docs/loom/BACKLOG.md:167` — the "≥10yr, industry norm" claim. **Delete it**;
  unevidenced and currently reads as fact.
- The BACKLOG's "Slice C = coverage file + retention + tearsheet" framing.
- Honest flag: **no code becomes obsolete.** Almost purely additive, which Axis 5
  calls a YAGNI smell. Mitigation: each capability traces to a measured finding,
  and two (enumerate, canonical period) are prerequisites deferred across three
  slices. If a reviewer disagrees, cut capability (4); (1)-(3) are load-bearing.

## Pre-existing defects found during recon — log, do not fix here

Surgical-edit discipline: these are not ours and not in scope. To BACKLOG.

- `comps_compute._concept_fy_end` (`comps_compute.py:206-207`) hardcodes
  `fiscal_year_ends`, so a TW pack (which emits `periods`) returns `None` every
  time — provenance column silently blank, no error.
- Values/periods can pair **wrongly**: `_extract` skips missing labels rather than
  appending `None`, then `_meta` slices `periods[: len(revenue)]` — a mid-series
  gap truncates periods from the END (`pack_jp.py:232-236`/`:274`, `pack_tw.py:275`,
  `pack_kr.py:325`).
- JP EDINET Tier A canonical is an empty stub (`pack_jp.py:463-478`) — the better
  source produces the emptier canonical.
- TW's canonical blocks are absent from `tw-schema-memo-fetch.json` entirely.
- ADR-0001 sanctions duplication with a CI MD5 drift check, but the four
  `_YF_LABEL_MAP*` copies differ in content, so no drift check covers them.

## Out of Scope

- Period canonicalization for JP / KR / CN / TW, and the four-copy duplication.
- Read-time anchor-drift re-verification (Part 3).
- Any rendered per-company view / tearsheet.
- Retention or pruning of the store.
- Backfilling integrity stamps onto already-stored points (blocked by dedup key).
- SKILL wiring to make the prose lane user-invocable — related and arguably needed
  before accumulation is real, but separable.
- The two remaining Part-2 known limits (non-adjacent qualifier; same-clause PII).

## Open Questions

1. ~~Canonical US period format.~~ **DECIDED** (see §Period model): identity is
   the raw `(start, end)` pair; `fiscal_period`/`fiscal_year` labels stay as
   analysis coordinates, derived in Layer 1 via the existing
   `_derive_fiscal_label`, never `end[:4]`/`fy`. Backed by a 14-filer / 64k-group
   measurement + edgartools #816 + four vendor schemas + EDINET's Q5 accommodation;
   no counter-example found.
2. **Whether SEC rewrites an old accession's rows after an AMENDMENT is filed.**
   The measured window held 3,855 new accessions and **zero** `/A` filings, so the
   likeliest rewrite trigger was never exercised. `frame` is the one field verified
   mutable (removed from superseded rows) and must be excluded from any integrity
   stamp.
3. **How much of `history` is a query vs a stored view** — deferred until (1) and
   (2) land; on-read is the default per the coverage reasoning above.
