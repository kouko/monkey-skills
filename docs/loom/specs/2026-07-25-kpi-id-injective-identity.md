# Brief — injective kpi_id identity (consolidation axis + concept-case drift)

Date: 2026-07-25
Arc: investing-toolkit, successor to the top-line revenue lane
(`2026-07-25-company-total-revenue.md`); resolves the COMMITTED-NEXT BACKLOG
entry filed by that arc's live run
Status: brief (brainstorming output) — awaiting user sign-off before `writing-plans`

## Design-side on-ramp

Axis 0 negative guard fired: this is a correctness fix to an existing,
test-covered producer (no new product surface, no UI). No design-side detour
offered.

## Problem

`derive_kpi_id` mints the durable series identity for every dimensional KPI
point. It derives that identity by a **lossy** transform of the fact's full
XBRL signature, and the loss makes it **non-injective**: two genuinely
different series can mint the same `kpi_id`. The producer's collision guard
catches that and — correctly — refuses to write, but the refusal aborts the
whole pack.

The job: **"when I run the producer for any US filer, I want every genuinely
distinct series to get its own durable identity, so one filer's tagging
quirk cannot silently merge two series NOR blank out the filer's entire
breakdown."**

Live cost: **2 of 7 filers** lost their dimensional lane on the arc's original
end-to-end run (measured at the predecessor arc's close-out, 2026-07-26; no
entry in the backlog store records the per-filer breakdown — the original
`BACKLOG.md:204-222` anchor pointed at the follow-up section header, not at
this figure, so there is no source to repoint), and **23 of 47** on the wider
probe run for this brief (§Probe evidence).

- **XOM** — `us-gaap:Revenues` + `(StatementBusinessSegments=Upstream,
  StatementGeographical=US)` under `OperatingSegmentsMember` and under
  `IntersegmentEliminationMember` both derive
  `revenues__statementbusinesssegments-upstream__statementgeographical-us`,
  because `derive_kpi_id` **drops the `ConsolidationItemsAxis` entirely**.
  Those are different amounts (a segment's operating view vs its intersegment
  eliminations), not one series with a note.
- **Case drift** (JPM `jpm:…ChangesinFairValueof…` vs `…ChangesInFairValueOf…`;
  AMD `DataCenterMember` vs `DatacenterMember`; DIS, JNJ, 21 instances measured)
  — one name spelled two ways, so two selectors derive one lowercased slug and
  the guard aborts. Here the SHARED id is the right answer and the REFUSAL is
  the defect: the probe shows the two spellings are one series, split along the
  10-Q/10-K boundary.

The two failures live in the same function but pull in opposite directions —
one identity is too coarse, the other too fine. Getting either backwards is a
one-way door: `kpi_id` is the append-only store's series identity.

## Users

The toolkit operator (the repo owner) running the XBRL→`kpi_store` producer
for a US filer and reading the resulting one-page tearsheet. Conditions:
append-only durable history where a wrong identity is unrecoverable; `kpi_id`
is a **human surface** — it is the tearsheet's row label
(`tearsheet_format.py:175,208`) and a required hand-typed CLI argument
(`kpi_store.py:853`).

## Smallest End State

1. `derive_kpi_id` becomes **injective over the consumer's own identity tuple,
   up to case**: two signatures the consumer treats as distinct always mint
   distinct `kpi_id`s; two the consumer treats as the same — including two that
   differ only in spelling case — always mint the same one.
2. XOM's two consolidation views ingest as **two** series; a filer's 10-Q and
   10-K spellings of one segment ingest as **one** series carrying both its
   quarterly and its annual history. No pack aborts on either.
   Measured target: the 23 of 47 filers that abort today all ingest, with 0
   unintended merges (§Probe evidence).
3. The already-shipped fold stays intact: an **absent** consolidation tag and
   an explicit `OperatingSegmentsMember` remain **one** series (the 2.36.0
   INTC fix — `kpi_xbrl.py:405-413`, `_signature_key` docstring).
4. The fixed canonical top-line series `total_revenue` is **untouched** — it
   is a curated literal, not a derived identity.

### Chosen mechanism (user decision 2026-07-25 "走 C", amended same day to C′
after the 47-filer probe — see §Probe evidence)

`kpi_id` = **readable prefix + a 12-hex digest of the CASE-FOLDED identity
tuple**, mirroring the repo's own `kpi_store._series_key` pattern
(`kpi_store.py:71-92`, which appends a 12-hex sha1 of the exact raw pair to a
sanitized readable stem for exactly this reason).

- **Readable prefix** — today's slug, plus the `ConsolidationItemsAxis`
  member as a token **when that member is non-default**. Default/absent adds
  no token, so the fold in item 3 is preserved by construction.
- **Digest input** — the CONSUMER's identity tuple, **case-folded**,
  NUL-separated: `(concept.casefold(), tuple(sorted((axis.casefold(),
  member.casefold()) for …)), _consumer_consolidation(consolidation).casefold())`.
  - **Namespace** survives on `concept` only. The producer already emits
    `dimensions` as `{axis LOCAL name: member LOCAL name}`
    (`sec_edgar_client.py:3537-3539`), so there is no dimension namespace left
    for this function to lose.
  - **Consolidation is normalized before folding**, so `None` and
    `OperatingSegmentsMember` produce the **same** digest — the digest must key
    on the consumer's notion of "same", never a finer raw one
    (`docs/loom/memory/derived-durable-id-slug-is-a-lossy-one-way-door.md`
    rule 2; this is the exact over-fire that aborted INTC's 473 facts).
  - **Case is folded, not preserved.** This is the C→C′ amendment. Preserving
    case would mint two ids for the 21 measured series whose 10-Q and 10-K
    spellings differ, permanently separating each series' QUARTERLY history
    from its ANNUAL history. See §Probe evidence.
- Shape: `<prefix>__<12-hex>`.

### Required companion change to the collision guard

Two selectors whose signatures differ ONLY by case now derive the SAME
`kpi_id`, so `_claim_kpi_id` (`kpi_xbrl_ingest.py:205`) must accept a second
claimant whose claim key is **case-insensitively equal** to the incumbent's,
and keep raising otherwise.

`_fact_matches` is NOT touched: each selector still exact-matches its own
spelling's facts, and both selectors append into the one shared series. That
is what makes the fold reachable without editing the pure consumer — the
concern the BACKLOG entry raised ("case-normalizing the signature key would
make the consumer's exact-concept match miss one of the two facts") applies to
folding the SIGNATURE, not to folding the ID while leaving two selectors.

## Probe evidence (47 filers, live SEC fetch, 2026-07-25)

Method: `pack.py --pack kpi-quarterly` for 47 US filers across sectors (3-year
lookback, 51,147 dimensional facts, 2,074 distinct signatures), then a replay of
`ingest_pack`'s selector+claim loop using the REAL production functions
(imported, not reimplemented) with no store write. A data probe answers "does
this shape exist", never "does the pipeline survive"
(`docs/loom/memory/a-data-probe-is-not-a-pipeline-dogfood.md`) — the pipeline
claim still needs the live dogfood at close-out.

**Today's damage**

| Measure | Result |
|---|---|
| Filers whose dimensional lane aborts entirely | **23 / 47 (49%)** — XOM CVX COP PSX JPM BAC WFC T VZ DIS F GM GE BA CAT HON JNJ MRK KO NKE QCOM UNH AMD |
| Collisions | 149 — 128 consolidation-axis, 21 case-drift |
| **Silently mislabeled ids** (no collision, so no refusal: the only claimant carries a NON-default member, and the id reads as the operating view) | **49 ids across 5 filers** |
| Distinct `ConsolidationItemsAxis` members observed | 10 |

**Consolidation axis — splitting is CORRECT**

123 of 128 collisions have both members present **in the same filing** (adjacent
columns of one segment reconciliation table), i.e. genuinely two amounts. 5 are
disjoint — see Open Questions.

**Case drift — splitting is WRONG (this reversed the C decision)**

All 21 case collisions are disjoint across filings, and the cause is not a
rename over time: the filer uses one capitalization in its **10-Q** and another
in its **10-K**, ongoing.

| Filer | 10-Q spelling | 10-K spelling | Fact durations |
|---|---|---|---|
| AMD | `DataCenterMember` | `DatacenterMember` | 3/6/9 mo ↔ **12 mo** |
| DIS | `SubscriptionFeesMember` | `SubscriptionfeesMember` | 3/6/9 ↔ **12** |
| JNJ | `ERLEADAMember` | `ErleadaMember` | 3/6/9 ↔ **12** |

Minting two ids therefore files each series' quarterly points under one identity
and its annual points under another — permanently, for 21 series in this sample
alone — which is the exact opposite of the continuous annual+quarterly history
the store exists to hold.

**C′ scored on the same corpus**

| Measure | Result |
|---|---|
| Distinct `kpi_id`s minted | 2,053 |
| Intended folds (2+ spellings reunited into one series) | 21 |
| **Unintended merges of genuinely distinct signatures** | **0** |

**Read 2,053 as the SUM of each filer's own distinct-id count**, not a global
dedup across the corpus. A global dedup returns 1,887, because many filers
independently report the same signature (e.g. `us-gaap:Revenues` by
`StatementGeographical=US`) and those ids coincide across companies. That
coincidence is harmless — `kpi_store` keys on `(company, kpi_id, …)`
(`kpi_store.py:173-177`) — but it is not what this row measures. The committed
capture (`investing-toolkit/tests/data/fixtures/kpi_id_identity_probe_2026-07-25.json`)
computes the per-filer sum; recomputing it the other way and finding 1,887 is a
different question, not a discrepancy.

## Close-out dogfood (2026-07-26) — what the probe could not tell us

The §Probe evidence above is a REPLAY of `ingest_pack`'s selector+claim loop with
no store write. Per `docs/loom/memory/a-data-probe-is-not-a-pipeline-dogfood.md`
that answers "does this shape exist", never "does the pipeline survive it" — so
close-out ran the REAL path (`ingest_pack` → `facts_to_points` →
`kpi_store.append`) over all 47 cached live packs, one isolated store per filer.

**First run: 46 of 47 ingested. JNJ aborted** —
`OSError: [Errno 63] File name too long`. Its 4-axis signatures produced a
257-byte atomic-write temp filename against a 255-byte filesystem limit. This
arc CAUSED it: without the 14-byte id digest the same name is 243 bytes. The
suite was fully green and the probe reported JNJ healthy; only a real write to
a real filesystem surfaced it. Fixed by budgeting the FILENAME stem in
`kpi_store._series_key` (the id itself is unchanged; that file's digest already
guarantees uniqueness, so the readable stem is safe to cap).

**After the fix: 47 of 47 ingested, 0 aborted** — 51,147 facts → 2,100 series →
35,415 stored points; JNJ alone 7,157 facts → 371 series → 4,870 points.

The lesson generalizes past this arc: a derived identity getting LONGER is a
change to every downstream name derived from it, and filesystem limits are the
kind of constraint no unit test models.

## Current State Evidence

- **Forward (who calls it)** — `ingest_pack` (`kpi_xbrl_ingest.py:298`) groups
  facts by `_signature_key` (`:357`), then per selector calls
  `derive_kpi_id(match["concept"], match["dimensions"])` (`:379`) and
  `_claim_kpi_id(claimed_by, kpi_id, sig_key)` (`:380`). The top-line lane
  claims the literal `_TOP_LINE_KPI_ID` under one fixed key (`:387`) and never
  routes through `derive_kpi_id`. **`derive_kpi_id` currently takes no
  consolidation argument** (`:117`) — the mechanism above requires adding it;
  `:379` is the only production call site.
- **Reverse (who owns the identity rule)** — the SSOT is the CONSUMER,
  `kpi_xbrl._fact_matches` (`kpi_xbrl.py:416-432`): concept exact, `dimensions`
  by dict equality, `consolidation` normalized on BOTH sides via
  `_normalize_consolidation` (`:405-413`, default
  `_DEFAULT_CONSOLIDATION_MEMBER = "OperatingSegmentsMember"`, `:148`). The
  driver deliberately reaches into that private name rather than restating the
  rule (`_consumer_consolidation`, `kpi_xbrl_ingest.py:144-159`). The digest
  MUST be built from that same tuple.
- **Error (current failure mode)** — `_claim_kpi_id` (`:205-222`) raises
  `ValueError` when a *different* `_signature_key` lands on an already-claimed
  `kpi_id`. Because `ingest_pack` builds every point before appending any, that
  raise aborts **both lanes of the whole pack** — the live INTC run landed 0 of
  473 facts on one collision (BACKLOG item (l), now
  `docs/loom/backlog/2026-07-25-investing-toolkit-top-line-revenue-lane-2-36-0-post-ship-follow-ups.md`).
  XOM and JPM fail this way today.
- **Data (what is stored)** — one JSON file per series under
  `resolve_store_dir()` (`_store_fs.py:43-64`): `KPI_STORE_DIR` →
  `$XDG_DATA_HOME/investing-toolkit/kpi-store` →
  `~/.local/share/investing-toolkit/kpi-store`. Write-side dedup key is
  `(company, kpi_id, period, as_of, source_accession)` (`kpi_store.py:173-177`)
  — `kpi_id` is load-bearing in it. **Verified 2026-07-25: no durable store
  exists on this machine** — `~/.local/share/investing-toolkit` is absent and
  neither env override is set, so every dogfood ran in an isolated store.
  Migration cost of an id-format change is therefore **zero right now**, and
  no back-compat path is needed. It is also the last cheap moment: a real
  ingest run makes the change orphan whatever it wrote.
- **Boundary (what else touches the id)** — the TW producer mirrors this
  derivation independently (`kpi_tw._tw_kpi_id`, `kpi_tw.py:122-137`) and
  already encodes its consolidation basis (`__basis-C|A`); the tearsheet
  renders `kpi_id` verbatim as a row label and section heading
  (`tearsheet_format.py:170-208`); `kpi_store` exposes `--kpi-id` as a required
  CLI argument (`kpi_store.py:853`).

**Evidence paths**: `investing-toolkit/skills/analysis-kpi/scripts/`
{`kpi_xbrl_ingest.py`, `kpi_xbrl.py`, `kpi_store.py`, `kpi_tw.py`,
`_store_fs.py`}; `investing-toolkit/skills/report-kpi-tearsheet/scripts/tearsheet_format.py`;
`investing-toolkit/tests/analysis/test_kpi_xbrl_ingest.py`;
`docs/loom/backlog/2026-07-26-investing-toolkit-kpi-id-identity-2-37-0-post-ship-follow-ups.md`,
`docs/loom/backlog/2026-07-25-investing-toolkit-top-line-revenue-lane-2-36-0-post-ship-follow-ups.md`.

## Decision

Make `derive_kpi_id` injective **up to case** by appending a 12-hex digest of
the consumer's case-folded identity tuple to a readable prefix that additionally
carries a **non-default** `ConsolidationItemsAxis` member. Two axes, opposite
directions, each measured rather than assumed: the consolidation member is
DISCRIMINATING (123/128 collisions have both members in one filing), spelling
case is NOT (21/21 case collisions are one series split across 10-Q vs 10-K
tagging). Keep `_claim_kpi_id` as a regression tripwire, relaxed to accept a
case-insensitively equal claimant — a guard that stops firing on the cases we
fixed is evidence the invariant holds, not dead weight to delete.
Ship no migration path, no alias map, and no back-compat id: the store is
empty (see Evidence → Data), so a clean break is both free and the only
option that works — the old id for a non-default consolidation member is
**byte-identical** to the new id for the default member, so no script could
have told them apart after the fact.

We will NOT fix the pack-wide blast radius, will NOT touch the TW producer,
and will NOT change how facts are MATCHED (`_fact_matches` stays exactly as
shipped — this arc changes identity minting only).

## Alternatives Considered

| | Approach | Why rejected |
|---|---|---|
| A | Add the non-default consolidation member to the slug, nothing else | Fixes XOM only; JPM's dimensional lane stays entirely unavailable and needs its own arc, paying the one-way-door ceremony a second time |
| B | A + stop discarding namespace and case in the tokens (faithful readable slug) | Fixes both aborts, keeps ids human-readable, but is only injective against the two *known* lossy transforms — not a guarantee. Agent recommended B; user chose C. **Also DISPROVED by the probe** for the same reason as C: preserving case splits 21 series along the 10-Q/10-K seam |
| C | A + always append a 12-hex digest of the **exact** identity tuple | Chosen by the user, then **disproved by the 47-filer probe before any code was written**: exact-case digests split 21 measured series into a quarterly half and an annual half |
| C′ | A + a 12-hex digest of the **case-folded** identity tuple, plus a case-insensitive relaxation of the collision guard | **CHOSEN (amended).** Injective up to case by construction; mirrors `_series_key`'s precedent; measured 0 unintended merges and 21 intended folds on the probe corpus |

Industry grounding (Axis 4): `srt:ConsolidationItemsAxis` members are
reconciliation components that decompose the consolidated total (operating
segments vs intersegment eliminations vs corporate non-segment) — i.e.
different amounts, not one amount with a note — per FASB's Segment Reporting
Taxonomy Implementation Guide and XBRL US DQC rules 0150 / 0243. That grounds
the SPLIT side of the decision.

On the FOLD side, the industry position and the observed data point the same
way: XBRL element names are case-sensitive NCNames, but XBRL US DQC 0215 treats
a case-insensitive name match as a *duplicate-definition defect* — i.e. two
spellings of one name are a filer error to be reconciled, not two economic
facts. The probe shows filers making exactly that error, systematically, along
the 10-Q/10-K boundary. A consumer that mints two durable identities from it
propagates the filer's error into its own history. (EN: xbrl.us/data-rule/
{dqc_0150, dqc_0243, dqc_0215}, xbrl.fasb.org/impguidance/SG1_TIG/
segmentreporting.pdf. JA: 金融庁 EDINET タクソノミ概要説明 — ディメンション軸で
「連結・個別」等の多次元構造を表現, fsa.go.jp/search/20200807/1b-1_GaiyoSetsumei.pdf.)

## What Becomes Obsolete

Removed or rewritten **in the same change**:

- `derive_kpi_id`'s docstring claim that the consolidation axis is "dropped
  from the signature" (`kpi_xbrl_ingest.py:122-129`) and the module
  docstring's matching paragraph (`:30-38`) — both become false.
- Two tests that pin the CURRENT (wrong-polarity) behaviour and must flip:
  `test_ingest_collision_guard_fires_across_consolidation_variants` (:285) and
  `test_ingest_raises_on_two_non_default_consolidation_members` (:323) — under
  this change both scenarios must ingest as two series instead of raising.
  Per `docs/loom/memory/a-test-can-pin-behaviour-with-a-false-rationale.md`,
  each existing test's stated *rationale* gets read as a claim to verify, not
  as context.
- `test_ingest_kpi_id_derivation` (:374) — the id format changes.
- `test_ingest_raises_on_kpi_id_collision` (:171) — re-read its scenario: if its
  two signatures differ only by case, its polarity flips too (they must now fold
  into one series). If they differ structurally, it stays as-is.
- The BACKLOG COMMITTED-NEXT section (now
  `docs/loom/backlog/2026-07-26-investing-toolkit-kpi-id-identity-2-37-0-post-ship-follow-ups.md`)
  — resolved, moves out at close-out.
- The probe scripts now in the session scratchpad (`fetch_packs.sh`,
  `analyze_ids.py`) — per the repo precedent set by
  `tests/data/fixtures/capture_companyconcept_form_domain.py`, the arc commits a
  regeneratable capture script plus a COUNTS-ONLY JSON so the §Probe evidence
  numbers are reproducible rather than assertions in prose.

Explicitly NOT obsolete: `test_ingest_collapses_consolidation_variants_of_one_signature`
(:219) and `_signature_key`'s normalization — those pin the 2.36.0 INTC fix and
must keep passing unchanged. They are the regression floor for this arc.

## Out of Scope

- **BACKLOG item (l)** — a collision aborting both lanes of the whole pack.
  This arc removes the two known triggers; whether to isolate the claim map
  per lane is a separate fork, decided after this ships.
- **The TW producer (`kpi_tw._tw_kpi_id`)** — agent's call, stated as an
  assumption for the user to override: its ids are derived from a
  repo-canonical field allowlist, not filer-authored qnames, so it has no
  namespace or case-drift source; no observed defect. Filed as a BACKLOG
  follow-up rather than widened into this arc.
- **Fact MATCHING semantics** — `_fact_matches` / `_normalize_consolidation`
  are untouched.
- **The `total_revenue` top-line series** — a fixed literal, no digest.
- **Any migration / alias / back-compat id.**

## Open Questions

1. Does any **other machine** hold a real `kpi-store`? Verified empty here
   only. If one exists, its old-format series become unreachable orphans
   (data is not corrupted, but it will not line up with new writes).
2. Should the readable prefix keep the `ConsolidationItemsAxis` token when
   the digest already guarantees uniqueness? Brief says yes — without it,
   XOM's two series render as two visually identical tearsheet rows. Cheap to
   revisit if the labels read badly in the live dogfood.
3. **The 5 disjoint consolidation-axis collisions** (of 128). The other 123 have
   both members inside one filing, which settles them as two series. These 5 do
   not co-occur, so the same evidence does not settle them — they may be a
   filer switching which member it tags, i.e. the consolidation analogue of the
   case-drift finding. C′ splits them. The probe did not measure whether their
   values continue each other across the seam; if a later dogfood shows a
   segment's history broken at that seam, this is where to look. Not a blocker:
   splitting is the conservative direction (a split is visible on the tearsheet;
   a wrong merge is silent).
4. Should the digest fold anything BEYOND case — e.g. whitespace, or the
   `Axis`/`Member` suffix variants? Not measured; no observed instance. Fold
   only what evidence demands (case), so each fold stays defensible.
