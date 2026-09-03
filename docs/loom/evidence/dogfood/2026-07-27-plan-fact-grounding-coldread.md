# Cold read + adversarial verification — plan-stage fact grounding

- **Date**: 2026-07-27
- **Branch**: `feat-plan-fact-grounding` (loom-code 0.39.0)
- **Task**: Task 8 of `docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md`
- **Question it answers**: brief Open Question 3 — *does the conditional
  source cross-read added to the reviewer contracts actually fire at the tiers
  `spec-reviewer` runs at?*
- **Status**: complete. Instruction is **load-bearing but was under-specified**;
  the defect it exposed was fixed on this branch before merge, and the fix was
  re-tested at the failing tier (§Re-run) — the verdict flipped to
  `NEEDS_REVISION`.

## Verdict in one line

The added instruction makes weak-tier reviewers **perform** the cross-read that
they otherwise never perform — but as first written it did not tell them what
the failed confirmation **means**, and at haiku that gap produced a PASS on a
plan whose cited source contradicts it.

## Method

A 2×2, run from the main conversation (subagents cannot dispatch subagents —
`docs/loom/memory/skill-in-subagent-loses-internal-orchestration.md`), so the
panel are siblings, not nested.

**Factor 1 — contract.** `spec-reviewer.md` before Task 5a (extracted from
commit `6f23eb3e`) versus the shipped version carrying role-contract item 7.

**Factor 2 — tier.** haiku and sonnet — the two tiers
`subagent-driven-development/SKILL.md:182` places `spec-reviewer` at
(one below the implementer; the most-capable exception covers
`code-quality-reviewer` only).

**Held constant.** Same agent type (`general-purpose`) in all four cells, same
material, same neutral prompt. `general-purpose` rather than the
`loom-code:spec-reviewer` subagent type deliberately: that type loads the
contract from the installed plugin cache (0.38.0), not the working tree, so it
could not have carried the treatment contract. Using it for one arm and
`general-purpose` for the other would have confounded contract with agent type.

**Prompt neutrality.** No cell was told a citation existed, that citations
mattered, or that anything was wrong. The prompt named the contract, the spec,
the artifact, and asked for a verdict.

### Material — discriminating by construction

Fixtures under the session scratchpad (`coldread/`), built from a real repo file
so the false claim is checkable:

- **The plan task** cites
  `loom-code/skills/subagent-driven-development/SKILL.md:182` as saying
  *"reviewers run at the same tier as the implementer"*.
- **That line actually says** *"Reviewers usually run at one tier below the
  implementer … **Exception**: when the implementer ran at the most-capable tier
  on an architectural task, the code-quality-reviewer also runs at
  most-capable."*
- **The artifact** (`resolve_reviewer_tier` returning its argument unchanged,
  plus a passing test) conforms to the plan **perfectly**.

So a reviewer that checks artifact-against-plan finds nothing. Only a reviewer
that opens `:182` can see that the plan itself is wrong.

## Results

| | haiku | sonnet |
|---|---|---|
| **control** (no item 7) | PASS — source never opened | PASS — source never opened |
| **treatment** (item 7) | **PASS** — source opened, contradiction found, filed as a note | **NEEDS_REVISION** — source opened, contradiction found, filed as a gap |
| **treatment + consequence clause** (item 7 as fixed) | **NEEDS_REVISION** — see §Re-run below | not re-run |

**Control, both tiers.** Both walked the spec-consistency checklist thoroughly
and confirmed conformance item by item. Neither opened the cited file. This is
the contract working as written: their stated job is artifact-versus-plan, and
the plan's own truth is outside it.

Worth recording: the control sonnet showed real evidence discipline about the
*test* — it volunteered that the RED state "rests on implementer's reported
test_results, not independently run here". It applied provenance care to the
test result and not to the plan's cited fact, because nothing asked it to.

**Treatment sonnet.** Opened `:182`, quoted it, and returned NEEDS_REVISION
citing "role-contract Rule 7 (conditional source cross-read)" by name. Its
framing: *"it means the task, as written, directs an implementation of a rule
the cited authority doesn't state."*

**Treatment haiku.** Opened `:182`, quoted it correctly, identified the
contradiction — then wrote it into `notes`, returned **PASS**, and volunteered
an excuse on the plan author's behalf: *"This may be intentional (a new
requirement departing from SKILL.md), but the plan should clarify this."*

## Finding — the action fired, the consequence did not

Item 7 as shipped stated what to **do** and not what a failed confirmation
**means**. Sonnet inferred "gap"; haiku inferred "note". Both inferences are
defensible, because the contract was silent.

This is the weak-model doctrine restated with fresh evidence: **an instruction
whose severity must be inferred is still a judgment call, and judgment calls
fail at weak tiers even when the mechanical action succeeds.** The gap is not
that haiku failed to act — it acted correctly. It is that acting correctly was
not enough, and nothing said so.

The same defect shape was found five times elsewhere on this branch by
per-task reviewers, always in guard tests. This is the first instance found in
shipped contract prose, and it was found only because a live weak reader was
put in front of it.

## Re-run — the fixed contract, same tier, same material

The fix is prose. Prose that is not re-tested against the live weak
reader it was written for is just different words, so the haiku cell was
re-run against the amended `spec-reviewer.md` with a **verbatim-identical
prompt and identical fixtures** — the only changed variable is the
consequence clause at `:37-39`.

The three readings were written down **before** the re-run, so the result
could not be rationalized after the fact: flip to NEEDS_REVISION → the fix
works; still PASS → prose cannot hold this at haiku and the answer is a
mechanical gate, not another rewording; a new failure mode (e.g.
over-firing) → the fix regressed and must be reverted.

**Result: NEEDS_REVISION.** The same tier, on the same material, moved the
contradiction out of `notes` and into `gaps`, and returned the blocking
verdict. It also anchored the finding to a checklist item on its own —
`CHK-SPEC-005 (Outdated References)` — rather than restating the clause,
and stated the distinction the control cells never reached: *"the artifact
correctly implements the plan's (incorrect) specification, but the
specification itself does not match the cited source."*

So the first reading holds: **the consequence clause is what carries the
verdict at haiku, not the cross-read instruction alone.** The action and
the consequence are separately load-bearing, and only the action had been
tested before this re-run.

**n is still 1.** This re-run does not turn n=1 into sufficient evidence.
It establishes that the corrected behaviour occurred at least once at the
tier where the defect was observed — which is the minimum bar for shipping
a prose fix, not proof of a rate.

## Over-firing — measured separately, and it does not happen

Code-quality review of the consequence clause raised the sharper version of
the open question: the fix defines *what a failed confirmation means*, but not
*what counts as one*. A pointer that merely drifted — right content, stale line
number — could read as a failed confirmation and force `NEEDS_REVISION`. This
branch produced four such inaccuracies in its own commits, so the case is
common, and the brief's reversal condition is a false-alarm rate.

**First attempt — a contaminated fixture, discarded.** The intended material
was "content true, pointer off by two". The rewritten rule silently dropped the
source's `usually` qualifier and its entire `Exception` clause, so the plan text
really was wrong and the fixture confounded drift with a substantive omission.
Sonnet caught the contamination and rested its `NEEDS_REVISION` on the dropped
exception, not the line number, naming both separately. Its verdict was correct
and the experiment was void. Recorded rather than deleted because the discard
reason is the finding: **a fixture built to isolate one variable has to be
mechanically checked against its source, not eyeballed.**

**Second attempt — verified clean before dispatch.** The plan quotes `:182`
verbatim (checked programmatically: the source line, whitespace- and
emphasis-normalised, is a substring of the plan; `usually` / `Exception` /
`most-capable` / `architectural` all present), the artifact implements both the
rule and its exception, and the fixture's own five tests pass. The sole defect
is the citation reading `:180`.

| | haiku | sonnet |
|---|---|---|
| **verdict** | PASS | PASS |
| **handling of the drift** | named it — *"the actual line is 182, but the content is accurate"* | did not detect it; asserted *"the cited source says exactly this at that location"* |

**No over-firing at either tier**, so the reversal condition stays untriggered
and the 🔴 floor is safe to ship: it cannot fire on drift, because the drift is
not what the cross-read examines.

That is the real result — **the cross-read verifies the claim, not the
pointer.** Which is the right scope for the defect class this branch targets,
and it explains the absence of false alarms directly rather than by luck.

The two tiers nonetheless disagreed about what to *do* with a stale pointer:
one recorded it, the other absorbed it silently and stated something false
about the source in the process. Writing the distinction into the contract is
therefore a precision fix, not a safety fix — it makes an emergent, inconsistent
behaviour predictable, and it stops a citation error from being reported as a
confirmation.

## The drift clause, re-tested — one tier improved, one did not

The boundary clause ("a drifted pointer whose content is still present is a
citation-hygiene note, not a gap") was added after the measurements above, so it
was re-run against the same clean fixture. Same material, same prompts; the only
changed variable is the clause.

| | before the clause | after the clause |
|---|---|---|
| **sonnet** | drift undetected; asserted *"the cited source says exactly this at that location"* — false | **detected, classified, recorded**: named `:182`, cited the clause to classify it as hygiene rather than a gap, and wrote it into `notes:` |
| **haiku** | named it — *"the actual line is 182, but the content is accurate"* | **worse**: restated the citation as *"cites SKILL.md:180-182 … verified accurate at lines 180-182"*. The plan cites `:180`, not a range. It widened the citation into a range of its own invention and then affirmed that range |

Verdicts stayed PASS in all four cells, so **over-firing remains unobserved** and
the reversal condition remains untriggered. But the clause's second job — making
the stale pointer *visible* instead of silently absorbed — only landed at sonnet.

At haiku it did not land, and the post-clause run is arguably worse than the
pre-clause one: papering a drift over with an invented range is a less honest
output than either naming it or missing it. **The two haiku runs also contradict
each other**, which is the more useful fact: run-to-run variance at that tier is
large enough that n=1 per cell cannot separate "the clause caused this" from
noise. No causal claim about haiku is supported in either direction.

**What this does and does not license.** Ship the clause: it is a clear
improvement at sonnet, a no-op-or-noise at haiku, and it introduces no false
alarms at either. Do not claim it works at both tiers. The recording half of the
rule is unreliable at the weakest tier, which is consistent with this repo's
standing finding that prose requiring a judgment call fails at weak tiers while
prose naming a checkable action survives — "record a hygiene note" is closer to
the former than it looks.

## Reversal condition — not triggered

The brief's stated reversal was: if the cross-read produces false alarms at a
rate that would train reviewers to ignore it, fall back to citation-only and
say the mechanical route failed. Neither arm produced a false alarm; both
treatment arms found a real contradiction. The control arms establish that the
behaviour does **not** occur unprompted at either tier, so the instruction is
not redundant. Shipping `T1` alone would have left this class undetected.

## Action taken

The consequence clause was added to both reviewer contracts on this branch
before merge, each with its own failing test first. Deferring it would have
shipped 0.39.0 with a contract known to mis-verdict at haiku — and
`SKILL.md:182` puts `spec-reviewer` at haiku for every Integration-class task,
so that is a live path, not a theoretical one.

## Limitations — read these before citing this note

- **Only one of the two fixed contracts was re-tested.** The re-run
  exercised `spec-reviewer.md`. The parallel consequence clause added to
  `code-quality-reviewer.md` — which sets a 🔴 severity floor rather than a
  binary verdict — was **not** put in front of a live reader. Its behaviour is
  inferred from the spec-reviewer result, not measured. That inference is
  weakest exactly where the two contracts differ: a severity floor has to
  survive an aggregation table, a binary verdict does not.
- **Over-firing was tested for one drift shape only.** §Over-firing covers a
  stale line number whose content is present two lines away. It does not cover a
  citation to a file that no longer exists, a path missing a directory segment,
  or a citation that is accurate but irrelevant to the claim. The clean-fixture
  result is n=1 per tier.
- **n = 1 per cell.** Four runs plus one re-run, no replicates. Model outputs are
  non-deterministic; a second run could differ, most plausibly at haiku, whose
  behaviour sat right at the note-versus-gap boundary.
- **One defect shape.** A miscited factual claim in a plan Description. It does
  not test a citation to a file that does not exist, a line number that has
  drifted, or a citation that is correct but irrelevant.
- **Not the shipped agent type.** The panel ran as `general-purpose` carrying
  the contract as instructions. The real `loom-code:spec-reviewer` subagent type
  carries the same text plus its baseline injection; behaviour should be close
  but was not measured.
- **The adversarial round is thin.** This experiment covers the cooperative
  cold read. Whether a reader trying to *route around* item 7 can satisfy its
  wording without doing the work is only partly answered — the code-quality
  reviewer for Task 5b documented one such mutation that its own guard still
  admits (`"or even when it does not … verify anyway"`), which is a lexical
  boundary, not a behavioural one. A dedicated adversarial round remains
  unrun.
