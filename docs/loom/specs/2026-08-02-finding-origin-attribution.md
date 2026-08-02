# Brief: reviewer findings carry a quote-gated origin, so planning-origin defects become countable

- **Date**: 2026-08-02
- **Origin**: this session's feasibility probe over the transcript corpus
  (`~/.claude/projects`, 6,524 files / 2.0 GB). The probe established that
  docs-side A-class defects are extractable from shipped verdict blocks, and
  code-side ones are not — the plan-origin attribution is lost at the point of
  recording.
- **Status**: brief, awaiting user ratification.

## Design-side on-ramp

Axis 0 evaluated, not skipped: this is an increment to internal review
machinery in a repo with no `docs/loom/PRINCIPLES.md`, no user-facing surface,
and no multi-state object behaviour. No on-ramp row fires. Proceeding direct.

## Problem

When I ship a change to the review machinery, I want to know whether it
actually reduced the expensive defect class — so that I stop choosing the next
mechanism by argument and start choosing it by measurement.

Today every candidate ships unmeasured. The repo has already paid for this
once in the right direction: the declared-vs-actual comparator was **measured
at 0 of 9** against the catalogued A-class defects, and that measurement is the
only reason it was not wired in. Nothing else on the candidate list has a
comparable number.

The blocker is specific and small. `docs/loom/backlog/2026-07-27-phase-
containment-effectiveness-*.md` already defines the success metric — the share
of planning-origin defects caught before close-out — and its baseline is
uncomputable. Not because the corpus is missing: because **the corpus records
where a defect lives, never where it came from.**

Worked example, from this session. A plan enumerated seven hard-coded call
sites with `file:line` for each. There were eight. The implementer changed all
seven correctly, every test passed, and the eighth was a silent
data-corruption bug found two review rounds later. The reviewer that found it
recorded `where:` pointing at the `.py` file. **The plan's role in causing it
was never written down anywhere.**

## Users

The three reviewer agents (`code-reviewer`, `code-quality-reviewer`,
`docs-reviewer`), which already emit structured findings; the orchestrator,
which unions and aggregates them; and — the actual beneficiary — the human
choosing what to build next, who currently has n=9 hand-curated cases and no
way to grow that number except by hand.

Job story: *when a review finds a defect that an upstream document caused, I
want that causal link recorded at the moment it is visible, so that six months
of accumulated reviews answer "which gate is worth building" without anyone
re-reading transcripts.*

## Current State Evidence

- **Forward** — the finding schema is defined in three agent contracts and
  mirrored in two skills: `loom-code/agents/code-reviewer.md:346-350`,
  `loom-code/agents/code-quality-reviewer.md:339-343`,
  `loom-code/agents/docs-reviewer.md:364-369`, plus §Verdict structure in
  `loom-code/skills/requesting-code-review/SKILL.md` and
  `loom-code/skills/requesting-docs-review/SKILL.md`. `spec-reviewer` is a
  different shape (binary verdict + `gaps:`) and is out of scope.
- **Reverse** — `loom-code/scripts/loom_gate_markers.py` is the enforcement
  point, not the agent prose: `_FINDING_RE` (`:78`) splits the verdict text
  into per-finding blocks and `_WHERE_RE` (`:79`) requires a path-like `where:`
  in each, refusing to mint the review-pass marker otherwise. **A field is
  enforced here or it is not enforced.**
- **Error** — a finding missing `where:` does not warn; it flips the whole
  verdict to `NEEDS_REVISION` and the marker refuses to mint (exit 3/4). That
  is the fail-closed precedent this change should match.
- **Data** — `docs-reviewer` already ships a fourth per-finding field with
  exactly the shape needed: `class: instruction | evidence`, with the rule
  "unclear → instruction (fail closed)" (`:366`). A per-finding classification
  field with a fail-closed default is therefore an **established pattern in
  this codebase**, not a novel one.
- **Boundary** — the docs arm's dimensions (`incorrect-fact`, `inconsistency`)
  already act as a de-facto A-class tag and the probe extracts them cleanly.
  The code arm's dimensions (`correctness`, `cross-task-coherence`) mix
  A-class and non-A-class findings and cannot be separated post-hoc. **The gap
  is code-arm-only.**

Evidence paths: `loom-code/agents/{code-reviewer,code-quality-reviewer,docs-reviewer}.md`,
`loom-code/scripts/loom_gate_markers.py`, `loom-code/skills/requesting-{code,docs}-review/SKILL.md`.

## Alternatives Considered (Axis 4 — researched, EN + JA)

The research materially changed the recommendation. The design this brief
started from — a required, judgment-based origin field, mechanically enforced —
is the one the evidence rejects.

| # | Approach | Evidence | Verdict |
|---|---|---|---|
| A | Required field, reviewer judges the cause | Attribution reliability tracks whether the rater holds upstream context. Raters classifying from report text alone reached **kappa 0.26–0.33, fair-to-poor** (Hernández-González et al., via Shape of Code 2026). El Emam & Wieczorek (ISSRE 1998) found it repeatable **only** for trained inspectors with first-hand context. Our reviewer is the downstream case. | **REJECT** |
| B | Optional field with an explicit `unknown` (the Azure DevOps CMMI "Root Cause" pattern, which ships `Unknown` as a value) | Research-endorsed, and mandatory fields are measured to produce junk — practitioners enter "N/A" or nonsense rather than leave blank (arXiv 2408.01621, 2024). But this repo's own recorded lesson `prose-only-enforcement-dies-on-weak-executors` says a duty carried only by prose is dropped by weak executors. Optional here means always-`unknown`. | REJECT as primary |
| C | **Required, but quote-gated**: the field is fillable only by quoting the upstream statement verbatim; no quote ⇒ the literal value `none`. The validator greps the quote against the named file. | Converts the field from a judgment ("what caused this?") to a checkable action ("can you quote a wrong upstream statement? "). Sidesteps the kappa problem — the reviewer is no longer estimating causation, only reporting a quotation it either has or does not. And a quote the validator greps cannot be faked, which is what defeats the mandatory-field-junk failure mode. | **RECOMMEND** |
| D | Skip the field; compute **DRE** instead of PCE | DRE = internal / (internal + external) needs only *where found*, never origin — which the research names as the structural reason DRE is more common than PCE in practice. Costs nothing; the corpus already carries it. But DRE answers "what escaped", not "which gate catches the expensive class" — it cannot settle the A/B table. | Adopt as a **companion**, not a substitute |

Note the EN/JA agreement, which strengthens the finding: Japanese practice has
a standing vocabulary for exactly this failure (`属人化` / `ばらつき` in ODC
classification), and JaSST Tokyo 2015 carried a talk whose title is
"…属人化を排除していく試み" — a countermeasure write-up exists because the
problem is real. Neither language's sources treat classification repeatability
as self-evident.

**My take**: recommend **C**, with **D** run alongside because it is free.
Conditional reversal: if a first real arc shows reviewers returning `none` on
findings that plainly did have a document origin, then C has degenerated into
B and the honest move is to stop collecting the field rather than to tighten
the prose demanding it.

## Smallest End State

> **Re-cut 2026-08-02, after the plan-document-reviewer falsified this
> section's premise.** The first version said "ship on `code-quality-reviewer`
> first", on the belief that the per-task reviewer's output was what the gate
> marker validates. **It is not.** Per-task review mints no marker at all —
> minting happens only in `requesting-code-review` Step 3 and
> `requesting-docs-review` Step 4, i.e. at whole-branch scope. The chosen
> enforcement point and the chosen first agent did not intersect. The original
> wording is not preserved verbatim here because it was a factual error, not a
> decision that changed; this note is the record.
>
> Worth naming: that is a plan-fact defect — wrong, actionable, and silent —
> caught one stage earlier than usual, by the reviewer of the plan rather than
> by a code review two rounds in. It is the exact class this change exists to
> make countable.

One new per-finding field on the code arm, enforced where the existing
`where:` check already lives, scoped so it cannot break the arms it does not
govern.

- **Grammar** — `origin:` accepts either `none` or
  `<path> :: "<verbatim quote>"`.
- **Enforcement is scoped by dimension family, not applied globally.**
  `validate_verdict_text` is shared: the docs arm mints the *same* review-pass
  marker (`requesting-docs-review/SKILL.md:56` — "a separate docs marker would
  break the `git-guard.py` push gate"). A blanket requirement would therefore
  refuse to mint on docs-only and mixed branches and block their pushes. The
  discriminator is mechanical and clean: the code-arm dimension set
  (`security`, `architecture`, `correctness`, `naming`, `tests`,
  `refactoring`, `cross-task-coherence`, `external-surface-grounding`,
  `principles-conformance`, `deliberate-simplification`) and the docs-arm set
  (`omission`, `ambiguity`, `inconsistency`, `incorrect-fact`,
  `missing-population`) are **disjoint** — verified. A finding carrying a
  code-arm dimension must carry `origin:`; one carrying a docs-arm dimension
  is untouched. This follows the existing arm-scoping precedent for `class:`
  (`requesting-code-review/SKILL.md:151`).
- **The quote check runs after the sha exists, and says so when it cannot.**
  `validate_verdict_text` runs at `_cmd_review_pass:257`, before `head_sha` is
  resolved at `:275`, and the `validate` dry-run subcommand takes no `--repo`
  at all. So quote verification cannot live inside grammar validation. It runs
  as a distinct step in `_cmd_review_pass` after the sha resolves; the
  `validate` path reports loudly that quote verification did not run rather
  than passing silently — a silent skip on the pre-flight path reviewers are
  told to use would be exactly the fail-open this change exists to prevent.
- **Contract ships on both code-arm agents, with their difference stated.**
  `code-reviewer` (whole-branch) is the agent whose output the marker
  validates. `code-quality-reviewer` (per-task) emits the same field, and is
  **not** marker-enforced — per-task verdicts never reach the marker. That
  asymmetry is written into the contract rather than left for a later reader
  to discover.

Explicitly NOT in the smallest end state: the docs arm's schema (the probe
shows it is already extractable via its own dimensions), `spec-reviewer`
(different verdict shape), any corpus-wide backfill, and PCE itself.

## Decision

Add a quote-gated `origin:` field to the code-arm finding schema, enforced by
`loom_gate_markers.py` in the same fail-closed way `where:` already is,
**scoped by dimension family** so the shared validator cannot break the docs
arm, and with the quote check placed after `_cmd_review_pass` resolves the sha
it stamps into the marker.

We will **not** ask the reviewer to judge causation, because the measured
agreement for that judgment by a downstream rater is fair-to-poor, and a field
that is confidently wrong is worse than an absent one. We will **not** make it
optional, because this repo has already recorded that prose-only duties are
dropped by weak executors. The quote gate is what makes "required" safe: it
demands an action the reviewer can either perform or truthfully decline.

> **Correction 2026-08-02, after the Tasks 7-9 re-cut.** Two claims above and
> in Alternative C's row no longer hold at their strongest reading. "Enforced
> ... in the same fail-closed way `where:` already is" is true of the field's
> **presence and grammar** — a missing or malformed `origin:` on a code-arm
> finding still refuses to mint — but no longer true of the **quote**: Task 8
> demoted quote verification from a mint refusal to a recorded fact (0 of 24
> severity-🔴 findings on this repo ever reached it, so it was refusing on
> exactly the tail it could never see — a transcript tally, not a script;
> population and method at `docs/loom/plans/2026-08-02-finding-origin-attribution.md`
> §Re-cut after Tasks 1-6). Alternative C's stated ground for
> beating option B — "a quote the validator greps cannot be faked" — is
> therefore also weaker than written: a fabricated quote that fails to verify
> now mints regardless and is merely recorded as `unverified-quote-absent` in
> the origin ledger, not refused. The field still cannot be satisfied with a
> judgment-only `origin:` value (grammar still requires `none` or a quoted
> `<path> :: "<quote>"`), so C still beats A and B on the kappa/junk grounds
> this section argues from; what changed is narrower — unfakeability is now a
> property of the ledger's record, not of the mint gate.

## Out of Scope

- PCE itself — this brief only removes its blocker.
- **DRE.** The research names it as the cheaper companion metric (it needs
  only *where found*, never origin, which is the structural reason it is more
  common in practice than PCE). It is deferred rather than folded in: it
  shares no file, no schema and no test with this change, and bundling an
  independent measurement into a schema change would make both harder to
  judge. Re-trigger: once this field has produced its first data, compute DRE
  from the same corpus pass — the extractor written for the feasibility probe
  already reads what DRE needs.
- Reconciling the three internal inconsistencies in
  `docs/loom/audits/2026-07-27-*-defect-provenance-audit.md`, which separately
  block the PCE baseline. Tracked; not this change.
- The docs arm's schema.
- `spec-reviewer`'s binary verdict shape.
- Backfilling origin onto the 777 verdicts already in the corpus — the quote
  is not recoverable after the fact, which is the whole point.

## What Becomes Obsolete

Nothing is deleted by this change, which Axis 5 flags as a smell worth stating
plainly rather than hiding: this is a **purely additive** change. The
justification for accepting that is narrow — the field's entire purpose is to
create a measurement that does not currently exist, so there is no incumbent
mechanism for it to replace. If a later arc shows the field is not being
filled with real quotes, the correct response is deletion, not reinforcement.

## Resolved Questions

All three were open when this brief was first written; each is now decided and
the reasoning is recorded here rather than in a dispatch packet.

**1 — Verify the quote against committed content, not the working tree.**
*(user, 2026-08-02)*
Committed content is the only correct anchor: reading the working tree would let
an uncommitted edit satisfy the check, so a quote could be manufactured at
verdict-writing time and never exist in the history the marker attests. The cost
is one `git show` per quoted finding.

> **Correction 2026-08-02, after the plan-document-reviewer's round 2.** The
> question actually put to the user framed this as *"the reviewed commit vs
> HEAD"*, and the first version of this answer was written in those terms.
> **That distinction does not exist.** `_cmd_review_pass` resolves exactly one
> sha — `head_sha` from `rev-parse HEAD` — and stamps it into the marker, so
> "the committed content at that sha" and "the reviewed content" are the same
> thing; there is no second anchor to prefer over it. The decision the user made
> is unchanged and so is its force; what changed is the alternative it rejects,
> which is **reading the worktree**, never "reading HEAD". The superseded
> rationale — that a mid-branch document change would otherwise produce a false
> `none` — depended on the two-sha framing and does not survive it, so it is not
> preserved as a live reason. This note is the record.

**2 — One `none`, no second escape value.** *(agent decision)*
Rejecting the Azure DevOps `Unknown` precedent here, because the reason that
precedent exists does not apply to this design. A tracker's Root Cause field
asks for a **judgment** the rater may genuinely be unable to make, so it needs
an honest way to decline. This field asks whether the reviewer **holds a
quote** — a question that always has a definite answer. Splitting `none` into
"no document involved" versus "a document was probably involved but I cannot
quote it" would re-introduce exactly the causal judgment the quote gate was
built to remove, complete with its fair-to-poor agreement. The information that
split would carry is recoverable better elsewhere: `dimension:` already
indicates whether a finding is document-shaped, and the count of `none` on
findings whose `where:` is a code file is itself the degeneration signal
question 3 needs.

**3 — Judge on ≥40 code-arm findings, and judge truth rather than rate.**
*(agent decision, pre-registered before any data exists)*
One arc is **not** enough, and the reason is arithmetic. Measured on this
session as the calibration case: of roughly 14 code-arm findings, about **1**
had a quotable upstream-document origin — a base rate near **7%**. At that
rate a 20-finding sample returns zero non-`none` origins about 23% of the time
by chance alone, so a single-arc "it produced nothing, kill it" verdict would
be wrong roughly one time in four.

The pre-registered rule, fixed now so it cannot be rationalised after the data
lands:

- Accumulate until **≥40 code-arm findings** carry the field (≈3 arcs at the
  observed rate).
- **Degenerated — delete the field** if all 40 read `none`.
- **Working — keep** if at least one non-`none` origin survives a human check
  that the quoted statement genuinely explains the defect.
- **The rate is explicitly not the test.** A 5% hit rate is a success if those
  few are the expensive defects, which is the entire hypothesis. Recording the
  expected base rate here is what stops a low number from being misread as
  failure later.

> **Correction 2026-08-02, after the Tasks 7-9 re-cut.** The start condition
> above read, as first written, "accumulate from first mint" — implicitly
> the moment `_cmd_review_pass` first wrote `review-pass.json`. Two
> independent soundness reviews of the shipped Tasks 1-6 found that moment
> never arrives for most rounds: 0 of 24 severity-🔴 findings on this repo
> ever reached quote verification (a transcript tally, not a script;
> population and method at
> `docs/loom/plans/2026-08-02-finding-origin-attribution.md` §Re-cut after
> Tasks 1-6), because a `NEEDS_REVISION` round returned
> before minting or verifying anything, and the marker file itself was
> overwritten every run rather than accumulated. **The start condition is
> now: counting begins when the durable ledger
> (`<git-common-dir>/loom/origin-ledger.json`, Task 7) holds code-arm entries,
> not at first mint.** Only the start condition changes — the **≥40** threshold,
> the verdict (all-`none` ⇒ delete the field; ≥1 human-confirmed true origin
> ⇒ keep it), and the explicit refusal to judge on hit rate above are all
> untouched.
>
> It was legitimate to make this change now, and only now: the rule's own
> binding clause is that it "cannot be rationalised after the data lands,"
> and no data has landed under either version of the start condition — the
> branch was unpushed, `review-pass.json` is per-checkout, and nothing in
> the repo reads the field yet. Editing the finish line before the race
> starts is not the thing that clause forbids; editing it once a runner is
> partway down the track is. This correction is the record of which side of
> that line the edit falls on.
