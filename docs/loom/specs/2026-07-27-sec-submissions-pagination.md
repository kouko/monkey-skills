# SEC submissions pagination — the filing history stops where the recent block does

Brief (loom-code `brainstorming`, 2026-07-27). Branch
`feat-sec-submissions-pagination`, based on `50c8d65c` (investing-toolkit
2.39.0).

## Problem

`sec_edgar_client.fetch_submissions` (`sec_edgar_client.py:404-422`) reads
exactly one URL — `https://data.sec.gov/submissions/CIK##########.json` — and
returns it. SEC packs **at most one year, or the most recent 1,000 filings
(whichever is more)** into that document's `filings.recent` block; everything
older lives in the archive files enumerated by `filings.files[]`, which this
client never requests. `list_filings` (`:460-464`) then reads `recent` only, so
every caller's view of a company's history ends wherever that block happens to
end.

The truncation point is a function of the filer's **total** filing volume, not
of its 10-K count. A company that files many 8-Ks and 424Bs pushes its own
10-Ks out of the window. The result is the opposite of what the pipeline is
for: **the larger and more actively-filing the company, the less history it
returns** — and it returns it as a healthy-looking success, with no truncation
signal of any kind.

**Pre-fix baseline**, measured live 2026-07-27 over the full 71-filer roster in
`docs/loom/references/xbrl-verification-universe.md` (`reconstruct` pack asking
for 8 annual filings; 71/71 completed, zero crashes). Raw rows:
`sweep.jsonl` / `truth.json`, regenerable from §Verification.

The true 10-K count per filer was computed by merging `filings.files[]`
**outside the client under test** — a denominator taken from the client would
inherit the client's own truncation.

| verdict | filers | meaning |
|---|---|---|
| already complete | 38 | 8 of 8 returned |
| **truncated by this defect** | **29** | returned strictly fewer than the filer has |
| legitimately short | 2 | DOW (7 total, 2019 spin-off), PLTR (6 total, 2021 IPO) |
| entity/CIK defect (out of scope) | 2 | XOM (0), BLK (2, oldest 2025-02) |

**Post-fix expectation: 67 of 71 reach 8 filings, against 38 today.** The
remaining 4 are the two legitimately-short filers and the two entity-defect
filers — neither category is this change's to fix.

Worst cases, returned vs actually held:

| filer | returned | actually held | oldest 10-K | annual periods reachable (N+2) |
|---|---|---|---|---|
| JPM | **1** | 27 | 1994-03 | 3 |
| BAC | **1** | 32 | 1994-03 | 3 |
| C | **1** | 27 | 1994-03 | 3 |
| WFC | 2 | 32 | 1994-03 | 4 |
| META | 2 | 14 | 2013-02 | 4 |
| GOOGL | 3 | 11 | 2016-02 | 5 |
| WMT | 3 | 32 | 1995-04 | 5 |
| PG | 4 | 32 | 1994-09 | 6 |

Only **37 of 71** filers currently reach 10 distinct annual income-statement
periods — the user's stated floor.

Direct confirmation against SEC for three filers:

| CIK | filer | 10-Ks inside `recent` | filings in unread `files[]` archives |
|---|---|---|---|
| 1326801 | Meta Platforms | 2 | 2,004 (2017-02→2024-05) + 1,138 (2005→2017) |
| 1652044 | Alphabet | 3 | 1,659 (2015-10→2023-05) |
| 21344 | Coca-Cola | 8 | 2,007 + 273 (unaffected — 8 fit) |

This is the **same defect shape** `list_filings`'s own docstring
(`:431-458`) says it fixed on 2026-07-13: "a `limit`-only (row-count) window is
capped ACROSS ALL forms combined, so a company's own 8-K/10-Q filing volume can
crowd a once-a-year 10-K out of the returned rows entirely". That fix corrected
the window this code applies to the rows it holds. It did not correct **which
rows it holds** — the same crowding-out, one layer up, in the transport.

**Job to be done** (committed reading, per the user's standing goal stated
2026-07-26): *read one company's 10+ year financial trend, without the tool
silently deciding how far back "10 years" reaches.* The 2.39.0 as-filed
reconstruction made the per-filing view honest; this makes the set of filings
honest.

## Users

The single-company longitudinal analyst — the user of this repo — running
`pack.py --pack reconstruct` or `--pack statement-backfill` for one ticker and
reading the resulting trend. Job story: *when I ask for a decade of one
company's statements, I want the pipeline to return the decade or tell me it
cannot, so I can tell a short history apart from a short answer.*

The failure is worst exactly where the user's interest is highest: mega-cap and
financial-sector filers, whose filing volume is the reason the window overflows.

## Smallest End State

`fetch_submissions` returns the filer's **complete** filing history — the
`recent` block with every `filings.files[]` archive merged into it — so
`list_filings` and every other reader sees one full-length set of parallel
arrays and needs no change at all.

Three properties make that merge safe rather than merely longer:

1. **Merged in place, into `recent`.** The archive files carry the same
   parallel-array shape as `recent`. Appending them into those arrays keeps the
   payload's schema byte-compatible with every existing reader
   (`list_filings:460-464`, `_foreign_private_issuer_no_quarterly_reason:2225`),
   so this is a transport fix with no consumer edits.
2. **A distinct cache key for the merged payload.** The payload's SHAPE is
   unchanged but its SEMANTICS are not — a cached entry written by the old code
   is a truncated history that a reader cannot distinguish from a complete one.
   Reusing `submissions_{cik:010d}` (`:405`) would let a warm 24 h cache serve
   truncated history from the fixed code, per-company and unpredictably, which
   is precisely the condition that makes a verification run lie. Per
   `docs/loom/memory/cache-key-collision-across-migration.md`, the new
   semantics get their own key.
3. **Each archive page is cached under its own key**, so the per-company merge
   amortizes instead of being re-paid in full every TTL. See §Cost — this is
   the difference between a fixed constant and a 68-request bank.
4. **A failed archive fetch is an error, never a short answer.** If any
   `files[]` page fails, `fetch_submissions` returns the client's existing
   `{"error": ...}` shape rather than a silently-partial merge. A partial merge
   is the defect being fixed, wearing a different hat.

### Cost — measured, and it refutes this brief's first estimate

This brief originally asserted "most filers have 0-2 archives … this is
noise". Measured 2026-07-27 across the 33 filers the sweep flagged, that is
true for 28 of them and **false where it matters most**:

| archive pages | filers |
|---|---|
| 0-3 | 28 |
| 5 / 8 | CRM / WFC |
| 20 | BAC |
| 39 | C |
| **68** | **JPM** |

Fetching every page on every TTL expiry would cost JPM ~68 extra requests
(~25-30 s at the client's 0.1 s throttle) — roughly doubling a `reconstruct`
run for exactly the sector that needs the fix most.

**Resolution (user decision 2026-07-27, applied uniformly to every filer — no
size-based special case):** fetch every page, but cache each page under its own
key, `submissions_page_{name}`. Archive pages are historical: the page covering
1994-2003 does not change. The first JPM call pays 68 requests; subsequent
calls within the page TTL pay only for the main document.

**Archive pages are long-lived, NOT immutable.** When the `recent` block
overflows, SEC re-partitions — the NEWEST archive page can gain rows, and page
boundaries can shift. So the page cache gets a long TTL (7 days, the existing
`TTL_TICKERS` constant's value, `:67`), never a permanent one:
`docs/loom/memory/cache-key-collision-across-migration.md` names the
immutable-TTL cache as the case that can never expire a poisoned entry, and a
re-partitioned page is exactly such an entry. The page name comes from the
main document's `files[]` on every call, so a re-partition that renames pages
self-corrects on the next main-document fetch regardless.

## Current State Evidence

- **Forward** (who consumes the truncated data): `list_filings`
  (`sec_edgar_client.py:460`) → `select_narrative_filings` (`:792`), the 8-K
  scan (`:1745`), and `pack_us.pack_reconstruct` (`pack_us.py:1539`, asking for
  `RECONSTRUCT_ANNUAL_FILINGS = 8`, `pack_us.py:1218`).
  `_foreign_private_issuer_no_quarterly_reason` (`:2225`) reads the same
  `recent` block as a form histogram; merging can only make that histogram more
  complete, so it moves that check toward fewer false foreign-issuer
  classifications, never more.
- **Reverse** (SSOT / direction): `sec_edgar_client` is the Layer-1 acquisition
  SSOT for SEC transport; `pack_us` composes it and `analysis-kpi` never
  imports it (subprocess boundary, `pack_us.py:1220-1239`). The fix therefore
  lands entirely in Layer 1 and needs no Layer-2 change.
- **Error**: `_sec_get` (`:100-130`) already returns `{"error": "..."}` for 404
  / non-200 / post-retry 429, and `fetch_submissions` (`:411-412`) already
  propagates it un-cached. The archive-page path reuses that contract exactly.
- **Data**: `filings.recent` is a dict of parallel arrays (`form`,
  `filingDate`, `accessionNumber`, `primaryDocument`, `primaryDocDescription`,
  `items`, `reportDate` — the keys `list_filings:464-471` reads).
  `filings.files[]` entries carry `{name, filingCount, filingFrom, filingTo}`;
  each named file holds the same parallel-array dict at its top level.
- **Boundary**: the cache is `cache_util.cache_path("sec_edgar", ...)` with
  `TTL_SUBMISSIONS = 86400` — evictable cache, not the durable KPI store, so a
  key change costs a refetch and nothing else.

Evidence paths: `investing-toolkit/skills/data-markets/scripts/sec_edgar_client.py`,
`investing-toolkit/skills/data-markets/scripts/pack_us.py`,
`docs/loom/references/xbrl-verification-universe.md`,
`docs/loom/memory/cache-key-collision-across-migration.md`,
`docs/loom/memory/a-data-probe-is-not-a-pipeline-dogfood.md`.

## Decision

**We will** make `fetch_submissions` follow `filings.files[]` and merge every
archive page into `filings.recent` before caching, under a new cache key, with
each archive page separately cached under its own 7-day key, and a failed page
returning the existing error shape instead of a partial merge. Every filer
takes the same path — the 68-page bank and the 0-page filer run identical code,
because a size threshold would be a second, untested behaviour on the money
path for no measured benefit.

**We will not** change `list_filings`, any pack, or any consumer — the whole
point of merging into `recent` is that the fix is invisible above the
transport. **We will not** add a caller-facing "how deep" knob: the callers
already express depth as `limit` / `min_filing_date`, and a second depth
control at the transport is the kind of speculative flexibility the repo's
simplicity rule refuses.

**Why merge-into-`recent` and not a new richer return shape**: the industry
wrapper for this exact endpoint, `jadchaar/sec-edgar-api`, exposes
`get_submissions(..., handle_pagination=True)` **defaulting to eager**, and
merges the archive pages by appending "to the lists in the above `recent` key
entries" — the same shape choice, shipped and defaulted on. Adopting the
shipped convention costs nothing and keeps our payload readable by anyone who
knows that library.

**Verification is a live sweep, not a fixture.** Per
`docs/loom/memory/a-data-probe-is-not-a-pipeline-dogfood.md`, the acceptance
evidence is the full 71-filer roster re-run end to end and compared against the
pre-fix sweep captured on this branch's base, plus the returned 10-K set for at
least one bank checked against `data.sec.gov` directly. A fixture built from
the old client cannot show this bug, because the old client is what truncated
it.

## Alternatives Considered

| Option | Who ships it | Why not |
|---|---|---|
| **Eager merge into `recent`, every page cached under its own key** (chosen) | merge-shape from `jadchaar/sec-edgar-api` — `handle_pagination=True` by default ([README](https://github.com/jadchaar/sec-edgar-api/blob/main/README.md)); the per-page cache is ours, added after measuring | — |
| Eager merge, single cached blob (this brief's first draft) | `jadchaar/sec-edgar-api` as shipped | Correct, and re-pays the full page fan-out every TTL expiry — 68 requests for JPM. Superseded once the page counts were measured, not on principle |
| Lazy: fetch archive pages only until the caller's `limit` / `min_filing_date` is satisfied | no popular wrapper does this for this endpoint | Cheapest, and buys it by making the cached payload's completeness depend on which caller warmed it — a cache whose contents differ by requester is a second version of the bug being fixed |
| Opt-in flag, default off | `sec-edgar-api` offers `handle_pagination=False` as the opt-OUT | Defaulting to truncation preserves today's silent wrong answer as the default answer |
| Switch to `edgartools` for filing lists | already a dependency for XBRL | Its performance doc claims one request "contains all available filings" with no mention of the 1,000-row block ([docs](https://edgartools.readthedocs.io/en/latest/resources/performance/)) — an unverified claim against the endpoint whose limit we just measured; adopting it would move the bug, not remove it |

EN and JA sources agree on the mechanism and disagree with nothing: SEC's own
API page and both wrapper communities describe `filings.files[]` as the
required second hop.

- EN: [SEC.gov — EDGAR APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces),
  [sec-edgar-api docs](https://sec-edgar-api.readthedocs.io/)
- JA-sourced: [sec-edgar-api README](https://github.com/jadchaar/sec-edgar-api/blob/main/README.md)
  ("1000 submissions … the response specifies the next set of filenames to
  request"), [edgartools performance](https://edgartools.readthedocs.io/en/latest/resources/performance/)

## What Becomes Obsolete

Nothing is deleted. Two things change status rather than existing:

- `list_filings`'s docstring (`:448-455`) cites the 2026-07-13 AAPL "phantom
  no-10-K gap" as fixed by `min_filing_date`. That remains true for its layer
  but is now half the story — a `min_filing_date` deeper than the `recent`
  block could not have been satisfied before this change. The docstring gets a
  sentence, not a rewrite.
- The pre-fix sweep results become the **before** baseline for this branch's
  acceptance, not stale data.

## Out of Scope

- **The XOM silent-empty defect** (a ticker resolving to a CIK with zero 10-Ks
  returns `requested: 0 / _status: ok`). Separate defect, separate layer
  (entity resolution, not transport), user-sequenced second.
- Quarterly (10-Q) three-statement coverage — annual-only is a design property
  of `reconstruct` and `statement-backfill`, not a consequence of this bug.
- Predecessor-CIK stitching (Exxon's history under CIK 34088 vs the ticker's
  current CIK). `statement-backfill` already states it never stitches across a
  predecessor CIK; that stays true.
- Raising `RECONSTRUCT_ANNUAL_FILINGS` above 8 to reach 20 years. XBRL's
  2009-2011 phase-in bounds that independently.

## Open Questions

The one this brief opened with — can "short" be told apart from "truncated"? —
is **answered, before implementation**: yes, by the independent true-count
denominator described in §Problem. Two filers are legitimately short (DOW 7,
PLTR 6) and are named in the acceptance table so a post-fix run that leaves
them under 8 reads as correct rather than as a partial fix.

Remaining, non-blocking:

- **BLK is a second instance of the XOM entity defect**, discovered by this
  sweep: its CIK holds 2 10-Ks, oldest 2025-02, i.e. a 2024/25 holding-company
  re-registration. Recorded here so the entity arc sizes itself on 2 known
  instances, not 1. Not this change's scope.
- Whether SEC re-partitions archive pages often enough for the 7-day page TTL
  to matter is unmeasured. The main document's `files[]` is re-read on every
  call, so a rename self-corrects; only a same-name page gaining rows can go
  stale, and it goes stale for at most 7 days.
