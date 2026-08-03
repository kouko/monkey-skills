# deep-deep-research: classify fact vs opinion at extraction, route opinions around adversarial refutation

## Design-side on-ramp

Axis 0 negative guard applies silently — this is an enhancement to an
existing, already-shipped skill's internal pipeline (extract/verify/
synthesize stages), not new product-shaped or user-facing-UI work. No
`using-loom-product-principles` / `using-loom-interface-design` /
`using-loom-spec` detour offered.

## Problem

`research-toolkit:deep-deep-research`'s extract → rank → verify →
synthesize pipeline treats every extracted claim as a fact-checkable
proposition with a determinable truth value. `EXTRACT_SCHEMA` has no
fact/opinion distinction (`schemas.py:71-91`), the Stage-3 extraction
prompt explicitly instructs extracting only "FALSIFIABLE claims"
(`prompts.py:87`), and the Stage-5 adversarial-verify checklist is
built entirely around refutability — "Be SKEPTICAL. Try to REFUTE this
claim." (`prompts.py:110-135`).

This causes a demonstrated, concrete harm: a claim representing one
side of a genuine, evidence-backed disagreement (e.g. two credible
economists reaching opposite conclusions from the same data, or one
analyst's contrarian-but-substantiated call) gets voted on by 3
adversarial "refuters" (`VOTES_PER_CLAIM = 3`, `schemas.py:18`) exactly
like a factual error would be. If ≥2/3 voters find "a credible source
disputes this" (`REFUTATIONS_REQUIRED = 2`, `schemas.py:19`), the claim
is killed (`SKILL.md:414-419`, `rank.py quorum`) — permanently dropped
before Stage 6 ever sees it as a first-class finding (`SKILL.md:423-424`).
The mechanism cannot distinguish "this is factually wrong" from "this
is one side of a real disagreement" — both look identical to a
refutation-quorum voter, because finding *any* credible opposing source
is suficient to vote refuted=true (`prompts.py:126,131`).

The three existing opt-in levers that touch this space —
`mode_route.py` (settled/unsettled synthesis stance), `calibrate.py`
(no-false-consensus rule), `purpose_fit.py` (relevance floor) — all
operate at **Stage 6 (synthesis) only**. A legitimate opinion killed at
Stage 5 never reaches Stage 6, so none of these levers can rescue it —
they can only shape how *survivors* get written up. The fix has to
happen upstream of verify, not just at synthesis.

## Users

Whoever runs `deep-deep-research` on a question where genuine,
evidence-backed disagreement is normal rather than exceptional —
social-science / political / investing questions (expert disagreement
is the domain norm; this session's research found Wikipedia NPOV,
ProCon.org, and financial-analyst-consensus dispersion all treat named
attribution + preserved disagreement as first-class, not a fallback),
or any question surfacing a named individual's assessment that the
pipeline currently has no way to preserve as "attributed opinion"
rather than "checkable claim."

## Smallest End State

Two schema/prompt changes plus one routing change, nothing else:

1. **`EXTRACT_SCHEMA` gains a `claimType` field** (`schemas.py:71-91`):
   enum `fact` / `opinion` — **two values, not three.** An earlier draft
   of this brief used a `mixed` third value routed identically to
   `opinion`; whole-branch-adjacent review caught that this lets a
   false factual claim smuggled inside an opinion wrapper (e.g. "Analyst
   X believes [a fabricated revenue figure] caused the crash") skip
   refutation entirely, since the whole statement would skip straight to
   attribution-only checking. Fixed by **decomposing at extraction
   instead of tagging a middle state**: when a source statement mixes a
   factual component with an opinion component, the extraction
   instruction requires emitting **two separate claim objects** — one
   `fact`-tagged (the fabricated revenue figure, which now correctly
   flows into refutation) and one `opinion`-tagged (the analyst's causal
   belief, which flows into attribution-checking) — rather than one
   claim tagged `mixed`. `claims` is already an array
   (`schemas.py:77-89`), so this needs no schema change beyond dropping
   `mixed` from the enum — only an extraction-instruction change.
   **Fail-safe**: if a statement genuinely cannot be cleanly decomposed,
   default the whole claim to `fact` (subject to the full refutation
   quorum) — never default an undecomposable statement to `opinion`,
   which would wrongly exempt it from fact-checking. This mirrors the
   existing verify_prompt's own "default to refuted=true if uncertain"
   philosophy (`prompts.py:133`) — uncertainty always resolves toward
   the stricter check.

   **`heldBy` is a global optional field, not conditional on
   `claimType`.** An earlier draft captured it only for opinion/mixed
   claims; on review this created needless downstream coupling (code
   reading a claim would need to check `claimType` before knowing
   whether `heldBy` might be populated) for zero schema cost (it was
   already an optional string either way). Extraction now captures
   `heldBy` whenever a claim has a natural attributable source — "GDP
   grew 3% per the Federal Reserve" (`fact`, `heldBy: "Federal
   Reserve"`) is exactly as legitimate as "Analyst X believes stock Y is
   undervalued" (`opinion`, `heldBy: "Analyst X"`). This still applies
   CheckThat! 2025's finding that *reporting* a view is itself an
   objective, checkable fact ("X said Y") separate from the view's
   substance (Y) — it just no longer restricts that insight to
   opinion-tagged claims only.

2. **`fetch_prompt` (Stage 3) stops filtering to falsifiable-only**
   (`prompts.py:66-95`): extraction instructs the model to classify
   each extracted claim's `claimType` (decomposing mixed statements per
   above) rather than pre-filtering to only "FALSIFIABLE claims" — this
   is the Axis-5 obsolescence this brief commits to fixing in the same
   change (see below).

3. **Stage 5 routes by `claimType`** (`SKILL.md:377-425`,
   `prompts.py:98-135`): `fact`-tagged claims go through the
   **existing, unmodified** adversarial-refutation quorum — that
   mechanism is correctly designed for factual claims and stays as-is.
   `opinion`-tagged claims skip refutation voting entirely and get a
   narrower **attribution-confirmation check** instead — does the cited
   source actually hold/express this view, per the quote? (A much
   smaller question than "is this view correct.") An
   attribution-confirmed opinion always survives to Stage 6, tagged so
   synthesis knows to preserve rather than adjudicate it. Because
   decomposition already split any mixed statement's factual kernel
   into its own `fact`-tagged claim (step 1 above), no claim reaching
   Stage 5 ever needs to skip refutation on content that also carries an
   unchecked factual assertion.

Nothing else changes: `rank.py`'s ordering, the three existing Stage-6
opt-in levers, `REPORT_SCHEMA`, the fan-out/file-carrier conventions.
This is the minimal schema+routing fix that stops the demonstrated harm
(legitimate opinions killed by a refutation mechanism built for facts,
AND the newly-caught inverse risk of a factual error smuggled past
refutation inside an opinion wrapper) and lays the `claimType`/`heldBy`
foundation that later, larger work (claim↔counter-claim linkage,
dispersion-as-metric, belief-clustering, domain-specific folklore/KOL
handling — see Out of Scope) can build on without a second schema
migration.

## Current State Evidence

- **Forward**: `schemas.py:71-91` (`EXTRACT_SCHEMA`), `schemas.py:93-102`
  (`VERDICT_SCHEMA`, unchanged by this brief), `prompts.py:66-95`
  (`fetch_prompt`, falsifiable-only instruction at line 87),
  `prompts.py:98-135` (`verify_prompt`, refutation checklist),
  `SKILL.md:314-354` (Stage 3 extract flow), `SKILL.md:377-425` (Stage 5
  verify flow, quorum decision at 414-419).
- **Reverse**: `research-toolkit/skills/deep-deep-research/scripts/` is
  the SSOT for `schemas.py` / `rank.py` / `prompts.py` / `dedup.py`
  (confirmed via `sync-primitives.sh` header comment) — synced OUT to
  `fact-check` / `cite-check` / `deep-read` via
  `bash research-toolkit/scripts/sync-primitives.sh <skill...>`. Both
  files this brief touches (`schemas.py`, `prompts.py`) are synced
  primitives — any edit here MUST be followed by re-running that sync
  script for the sibling skills, and CI has an MD5 drift gate on this
  (hit and fixed once already this session, PR #519).
- **Error**: today, `refuted=true` from ≥2/3 adversarial voters on a
  claim that is actually a legitimate opinion produces silent,
  permanent information loss — the claim is dropped before Stage 6 ever
  sees it as a finding candidate (only surfaces in the `killed_block`
  context string, not as first-class synthesis input).
- **Data/Boundary**: `claimType` needs a safe backward-compat default —
  an extraction response that omits the field (e.g. a stale cached
  prompt, or a voter emitting a partial object) must default-behave as
  `fact` (today's only behavior — routes through the existing
  refutation quorum unchanged), never silently default to `opinion`
  (which would too-aggressively exempt claims from refutation and
  weaken the pipeline's existing fact-checking guarantee). The same
  fail-safe applies to decomposition: a statement the model cannot
  cleanly split into fact/opinion parts stays a single `fact`-tagged
  claim (full refutation), never an undecomposed `opinion`-tagged claim
  that would wrongly skip it.

## Alternatives Considered

This session ran extensive prior research (industry survey of
opinion-disagreement presentation + fact/opinion classification
criteria — Wikipedia NPOV, ProCon.org, Argument Mining/IBIS, financial-
analyst-consensus dispersion, ClaimBuster, CheckThat! 2025 SUBJ/OBJ,
Ollman v. Evans, JFC's mixed-category warning, software-engineering
folklore research, finfluencer/reflexivity research) — not re-run here.//
Summarizing the two live alternatives for THIS specific schema decision:

1. **A `mixed` third enum value, routed like `opinion`** — this brief's
   own first draft. Rejected on review: routing a `mixed`-tagged claim
   entirely through attribution-checking lets a factual error smuggled
   inside an opinion wrapper skip refutation ("Analyst X believes [a
   fabricated figure] caused the crash" would only get "did Analyst X
   say this" checked, never "is the figure real"). JFC's fact-checking
   methodology independently warns that forcing mixed content into
   either pure bucket loses information (their own worked example:
   "この暑さは異常だ。地球温暖化のせいだ！" mixes an observable claim
   with a causal/theoretical opinion) — **decomposition at extraction
   satisfies JFC's concern more completely than a `mixed` tag would**:
   splitting into a `fact` claim and an `opinion` claim preserves BOTH
   parts with their correct routing, rather than tagging the whole
   statement "mixed" and still having to decide which check to run.
2. **Binary subjective/objective (CheckThat! 2025's SUBJ/OBJ) with no
   decomposition** — simpler on paper, but this is what a bare binary
   without decomposition amounts to: mixed content forced into
   whichever bucket the model leans toward, same information loss JFC
   warns against. Superseded by decompose-into-two-claims, which keeps
   the schema binary (`fact`/`opinion`) while not forcing any single
   statement into the wrong bucket.
3. **Ollman v. Evans' context/field-based signal** (does the claim
   appear in a field institutionally marked as opinion, e.g. an
   "Outlook" section) — deferred. The current pipeline has no per-claim
   "field/section" concept (extraction reads whole-page content, not
   structured sections) — adding this would need a bigger restructuring
   of the fetch/extract contract than this brief's smallest-end-state
   scope. Flagged as a natural Phase-2 enhancement to `claimType`
   classification accuracy, not required for the routing fix itself.

**My take**: a binary `fact`/`opinion` `claimType` with extraction-time
decomposition of mixed statements, plus a global (not conditional)
`heldBy` attribution field, is the right minimal schema. It is cheap
(one 2-value enum + one always-optional string, no new schema shape
beyond dropping a third enum value), backward-compatible (safe
fact-default), and directly fixes both the original demonstrated harm
(legitimate opinions killed by refutation) and the inverse risk caught
on review (factual errors smuggled past refutation inside an opinion
wrapper) — without the bigger structural changes (per-claim
field/section tagging, argument-graph linkage) the richer alternatives
would need.

## Decision

Add `claimType` (`fact`/`opinion`, default `fact`) and a global
optional `heldBy` (attribution string, captured whenever a claim has a
natural attributable source, regardless of `claimType`) to
`EXTRACT_SCHEMA`. Rewrite `fetch_prompt`'s claim-extraction instruction
to (a) classify `claimType` per claim instead of pre-filtering to
falsifiable-only, and (b) decompose any source statement that mixes a
factual component with an opinion component into two separate claim
objects rather than emitting one ambiguously-typed claim — with a
fail-safe default to `fact` when a statement cannot be cleanly
decomposed. Add a Stage-5 routing split: `fact` claims → existing
unmodified refutation quorum; `opinion` claims → new, narrower
attribution-confirmation check (new prompt-builder function, new
lightweight verdict shape — details for `writing-plans` to atomize).
Re-run `sync-primitives.sh` for `fact-check cite-check deep-read` after
the schema/prompts changes land.

We will NOT build claim↔counter-claim linkage, dispersion metrics,
belief-level clustering, domain-specific (engineering-folklore /
financial-KOL) handling, or sync-primitives.sh automation in this
change — see Out of Scope.

## Out of Scope

- **Claim↔counter-claim explicit linkage** (Argument Mining / IBIS
  pattern — support/attack graph between claims). Real value, bigger
  schema surface; natural Phase 2 once `claimType` ships and is
  validated in practice.
- **Dispersion/spread as a first-class synthesis metric** (financial-
  analyst-consensus pattern — report *how split* the confirmed opinions
  are, not just a confidence tag). Needs claim-linkage (above) to know
  which opinions are "the same debate" before dispersion is
  measurable.
- **Belief-level clustering at synthesis** (the 2026 "Faithful
  Summarisation under Disagreement" paper's approach). Likely overlaps
  significantly with the EXISTING `mode_route.py` / `calibrate.py`
  opt-in levers — worth a dedicated follow-up brief evaluating whether
  to extend those levers rather than build new machinery, once
  `claimType`-tagged opinions are actually reaching Stage 6 to observe
  real overlap.
- **Engineering-domain folklore detection** (confidently-stated,
  community-repeated but empirically-ungrounded claims — e.g. "10x
  developers", per this session's software-engineering-folklore
  research). A distinct problem from opinion-routing — folklore is
  *fact-shaped in tone* but *unverified in substance*, so it needs its
  own verify-stage check, not the opinion path this brief builds.
- **Financial-domain KOL / reflexivity handling** (reach +
  conflict-of-interest tracking instead of refutation, per this
  session's finfluencer/Soros-reflexivity research). Distinct from
  plain opinion routing — a KOL's opinion isn't just "skip refutation,"
  its causal structure differs (the opinion can make itself true by
  being acted on), so adversarial-refutation is not just inapplicable
  but the wrong *kind* of wrong for it. Natural Phase-2/3 extension
  once `claimType` has a place to grow a domain-specific sub-tag.
- **Version-scoping for engineering facts** (a separate, narrower gap
  in the *fact* path's verify checklist — staleness handling for
  version-bound technical claims). Unrelated to opinion handling;
  independent follow-up if pursued.
- **Automating `sync-primitives.sh`** (pre-commit hook or build-pipeline
  dependency, instead of manual run + CI-only MD5 drift gate). Raised on
  review as a valid hardening idea — but it targets a repo-wide,
  pre-existing convention shared by every SSOT-synced primitive in
  `research-toolkit`, not something this brief's `claimType` change
  introduces. Parked in `docs/loom/BACKLOG.md` as an independent
  infra item rather than folded into this feature's scope.

## What Becomes Obsolete

`fetch_prompt`'s current instruction to extract only "FALSIFIABLE
claims" (`prompts.py:87`) is replaced in this same change by a
claimType-classifying instruction — the old falsifiable-only framing is
not left alongside the new field (Axis 5 discipline: don't ship a field
whose instruction still contradicts it).

## Open Questions

- Exact shape of the new attribution-confirmation verdict for
  `opinion`/`mixed` claims (fields, pass/fail criteria) — left for
  `writing-plans` to atomize as part of task-splitting, not decided
  here since it's implementation-level, not a design fork.
