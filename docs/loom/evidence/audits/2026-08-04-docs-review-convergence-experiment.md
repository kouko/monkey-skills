# Why a docs-review round never returns empty — a controlled measurement

**Date**: 2026-08-04
**Subject**: `loom-code:requesting-docs-review`'s convergence contract
**Method**: four fresh `docs-reviewer` dispatches over one already-passed branch

## What prompted it

PR #643 closed with the docs arm converging at round 4 — two independent
arms returning PASS and PASS_WITH_NOTES, zero instruction-class findings.
Hours later the question was whether the arm had converged because the
artifacts were clean, or because the round cap had run out.

A proposal was on the table at the time: add a **harm gate** to the
docs-reviewer contract, requiring a finding to name the concrete harm a
reader would suffer before it could gate. The stated theory was that the
loop is driven by findings that are technically true but consequence-free.

## Design

Twelve merged `.md` artifacts from PR #643 — the exact tree that had
passed round 4 — were handed to four fresh `docs-reviewer` dispatches
with no knowledge of each other or of the prior rounds.

| Arm | Contract |
|---|---|
| Control A, Control B | the shipped contract, unchanged |
| Treatment A, Treatment B | the shipped contract plus the harm gate |

Predictions were registered before dispatch. The one that mattered:
**if the treatment arms return the same gating-finding count as the
controls, the harm gate does not address the mechanism and the proposal
is dropped.**

## Result

| Arm | Gating findings (`class: instruction`) | Verdict |
|---|---|---|
| Control A | 1 | PASS_WITH_NOTES |
| Control B | 2 | NEEDS_REVISION |
| Treatment A | 2 | NEEDS_REVISION |
| Treatment B | 2 | NEEDS_REVISION |

**The harm gate did not reduce gating findings.** The criterion actually
applied was the weaker, one-sided form: *no reduction* — the treatment
counts (2, 2) sit at the top of the controls' range (1, 2), so the gate
removed nothing. The registered wording said "the same count", which the
literal reading (1 vs 2) does not satisfy; the one-sided form is what was
used and what the conclusion rests on. Either way the proposal was
dropped, unbuilt.

The result that was not predicted is the load-bearing one:

> **The four arms' gating findings did not overlap at all.** Seven
> distinct findings; no two reviewers raised the same one.

## Were they real?

All seven were checked, but not to the same depth, and the difference
matters to what this audit may be cited for. Each of the seven was read
against the text it cited and found to describe that text accurately —
no finding pointed at a passage that did not say what it claimed. **One**
was additionally settled by running a command that decides it. The other
was settled by reading the two passages against each other; the command
run there answers a different question — whether the store's gate catches
it — not whether the contradiction exists. Both artifacts had passed
round 4 that same day:

- `docs/loom/memory/enumerate-every-copy-before-editing-a-claim-and-name-the-leaks.md`
  — the frontmatter `description` presented the hard-wrap leak as open
  ("hard-wrapped so a quote split across two lines matches nothing")
  while the body stated the opposite ("The unwrapping half is now
  mechanised"). **The quoted description no longer exists**: the same
  commit that added this audit rewrote it, so a reader checking the file
  today finds the corrected text, not the contradiction.
  `scripts/check_loom_memory_integrity.py` exited 0 on it throughout:
  the checker compares the index line against the frontmatter
  byte-for-byte and never compares either against the body.
- `docs/loom/specs/2026-08-03-claim-copy-sweep.md:82` — states the tool
  accepts a claim via `--claim` **or stdin**. `grep -c stdin
  scripts/claim_copy_sweep.py` returns 0. PR #643 (`9960b202`) was a
  mixed branch: the spec is `.md` and went to the docs arm, the script
  is `.py` and went to the code arm. Under the per-file split then in
  force, the reviewer that read the claim was not given the file that
  falsifies it. What the code arm did or did not read is not recorded —
  the observable fact is the scope split, not the other arm's attention.

None was manufactured — meaning none cited a passage that did not exist
or did not say what the finding said. That is the claim this audit
supports; it is not a claim that all seven were worth fixing.

## What this means

The mechanism behind the non-converging loop is not that reviewers
invent findings. It is arithmetic:

> **A document carrying many small real defects, reviewed by a sampler,
> yields new findings on every pass. A stop rule keyed on "did the
> reviewer find anything" can never terminate.**

The hard 2-round cap is therefore correct — but not for the reason the
skill stated. It is not that extra rounds manufacture defects; it is
that, **for an artifact in the condition the blockquote names**, no round
count reaches an empty round. The cap exists because "reviewer found
nothing" is not a reachable state *there*, so it cannot be the
termination condition. The conditional is load-bearing and travels with
the claim: this was measured on one corpus (§Limits), and a genuinely
thin artifact could well return an empty round.

The two framings prescribe opposite reader behaviour, which is why the
distinction is worth the edit:

| Framing | What a reader does with round-2 findings |
|---|---|
| *extra rounds manufacture defects* | discount them — they are probably artifacts |
| *the pool is large and sampled* | treat them as real; decide on severity, not on exhaustion |

The second also yields the operative consequence: **a standing mechanism
outranks another review round.** A mechanism fires the same way every
run; a reviewer returns a different subset each time.

"Mechanism" here is deliberately wider than "detector", because **neither
of the two hand-verified findings was answerable by a standing detector**
— and saying otherwise would send a reader to build one. The distinction
that makes this compatible with §Were they real? above: a one-off command
can settle a single instance (`grep -c stdin` settled the stdin claim)
while no standing check finds the class (nothing greps every doc for
every capability it claims). Instance and class are different questions. The description-vs-body
contradiction produced a **format contract** that makes the claim
unwritable (`docs/loom/memory/README.md` §Format); a detector for it was
measured and killed
(`docs/loom/memory/measure-a-checks-fire-rate-before-building-it.md`).
The stdin claim produced a **change to what the reviewer is handed** —
the `read-context` field in `requesting-code-review` Step 1 /
`requesting-docs-review` Step 3. Three shapes, then: a checker, a format
rule, a change of inputs. The evidence that checkers specifically pay off
is separate and plentiful — `backlog_index --check`,
`check_loom_memory_integrity`, and the codex-manifest hook each caught a
mistake on this branch at the moment it was made.

## Limits — stated, not buried

- Four arms over **one** branch's artifacts. This measures that the pool
  is large and disjointly sampled on this corpus; it does not
  generalize a rate.
- Severity was not controlled. All seven findings were `🟡`-class; the
  experiment says nothing about whether `🔴` findings overlap more.
- The harm gate was refuted **as a lever on finding count**. It was not
  tested as a lever on relay quality, which is a different claim.
- **Zero overlap may characterise the tail rather than review in
  general.** The branch that shipped this audit carried a structural gap
  — a mechanism written into the skill layer but not into the agent
  contract that executes it — and its two docs arms **both** raised it,
  independently. The measurement above ran instead against an
  already-passed corpus holding only small residual defects. So the
  direction is: a panel agrees on structural defects and diverges on
  residual nits. No magnitude is stated here on purpose — a count of that
  branch's own findings, written into a file on that branch, changes
  every time the branch is reviewed again
  (`docs/loom/memory/a-passage-that-describes-itself-decays-on-every-edit.md`).
  The reviews themselves are the record; read them in PR #644.

## Does delta-scoping converge faster?

A second, separately pre-registered experiment on the branch that shipped
this audit. **The rule under test**: from some round N onward a reviewer
still reads every artifact whole, but may only raise a finding that is
(a) about text the round's delta changed or (b) a contradiction between
that delta and unchanged text. Everything else it notices is listed as
out-of-scope rather than raised.

**Design** — 2×2. Two cells were already filled by that branch's real
review rounds; two were run fresh against worktrees pinned at the same
commits, with prompts identical to the historical ones except for the
scope clause. Two arms per cell; findings unioned per cell.

| | Unbounded (control) | Delta-scoped (treatment) |
|---|---|---|
| **Round 2** (large delta — round 1's fixes) | 2 gating · NEEDS_REVISION | **3 gating** · NEEDS_REVISION |
| **Round 3** (small delta — round 2's fixes) | **2 gating** · NEEDS_REVISION | 0 gating · PASS |

**The registered falsifier held.** Delta-scoping must not hide a gating
defect living inside the delta. Both round-2 treatment arms re-found both
of the control's gating findings, and surfaced a third the control missed.
Suppression was volunteered, not inferred: the round-2 treatment arms
listed 13 out-of-scope observations between them, the round-3 treatment
arms 3. Of those 16, none has since been raised as a gating finding by
any later arm on this branch — which is the only check that was run, over
the rounds this session held, adjudicated by the author. It is not a
claim that they were unimportant, and the suppression counts are a floor
(see Limits).

**The first reading of this table was wrong, and the correction is the
finding.** The round-3 column looks like "scoping blinds a late round" —
its unbounded control surfaced two real pre-existing defects the scoped
arms never mentioned, including a gate hole in this very skill. That
invites a rule keyed on round number, with round 3 exempted. It is an
artifact. **Both of those defects were present and findable during rounds
1 and 2, which were also unbounded, and both of those rounds missed
them.** The mint-scope conflict survived two unbounded passes. So the
round-3 control did not find them by being round 3; it found them the way
the first experiment's arms found their seven — by sampling a pool that
does not run out.

Round number is therefore the wrong variable. The real trade is the same
at every round: **keep sampling an inexhaustible pool and never
terminate, or scope to the delta and converge.** Which is why the shipped
rule is monotonic from round 2 (`requesting-docs-review` Directive 2) and
why round 1 is kept unbounded only until something else sweeps that pool.

**Limits — this experiment.**

- One branch, two arms per cell. No rate generalises, and n=2 cannot
  separate a one-finding difference from arm variance — the round-2
  3-vs-2 result is suggestive at best.
- **Named confound**: treatment arms were told to list what they
  suppressed "because it is data". That instruction may itself have made
  them more careful, so treatment's higher gating count is not cleanly
  attributable to scoping. The falsifier result (treatment re-found both
  control findings) does not depend on it.
- Suppression counts rest on arms volunteering what they withheld. An arm
  that drops something silently is invisible here, so those counts are a
  floor.
- Round 1 sampled the pre-existing pool weakly on this branch — 1 of its
  14 findings was pre-existing-and-unrelated — because the branch was
  mostly new text. A branch changing three lines in a large document
  would test that differently, and was not tested.

## Errata — what was rewritten in place, and when

`requesting-docs-review` Directive 4 forbids rewriting settled narrative
in place, because doing so destroys the record the correction exists to
create. This document broke that rule against itself before this note
existed. Recorded here rather than reverted, since the corrected text is
the one downstream contracts now transcribe.

**Scope of this section**: it records in-place rewrites of text that had
already SHIPPED to `main` under an earlier release. Rewrites of prose the
same unmerged branch authored are not listed. Directive 4's operative
test is narrower than this section — it governs an evidence-class finding
against prose *the branch left unchanged* — so text a branch both wrote
and rewrote falls outside it either way. Later rounds of the 0.48.0
branch rewrote several of their own new sentences on that basis. The
0.48.0 bullet below also records one addition rather than a rewrite; it
is listed because it changed what the document asserts.

- **loom-code 0.48.0** corrected three claims first published under
  0.47.0. §Were they real? said two findings were confirmed by running
  the command that decides them; only one was. §What this means said a
  deterministic check outranks another round, on two worked examples
  neither of which a detector answers; the category is now a standing
  mechanism. The cap rationale asserted "an empty round is not a
  reachable state" without the "artifact carrying many small real
  defects" premise its own blockquote carries.
- **loom-code 0.48.0** also added §Does delta-scoping converge faster and
  withdrew the magnitude from the §Limits overlap bullet.

A reader who cited the 0.47.0-era wording will find different text above.
`loom-code/CHANGELOG.md` carries the same record release by release.

## Corrections this arc's research pass produced

The session that led here ran a deep-research pass whose first-round
output was checked against primary sources. The corrections are recorded
because each would have changed a decision. **Citation status, stated
rather than implied**: only the κ bullet carries a document identifier.
The others name an author, venue, or literature by description, and the
primary documents were not re-opened while writing this audit. Treat
every bullet below as a pointer to re-verify before reuse, not as a
citation that has been checked here:

- **The κ≈0.3 figure for LLM-as-judge agreement** was misattributed
  (arXiv 2505.12201, not the number first cited) and mis-scoped: it
  measures one judge's cross-language self-consistency, not inter-judge
  agreement. English-language benchmarks report κ spanning 0.271–0.898.
- **"Anthropic models have the worst false-positive rate on clean
  prose"** inverted the finding. Models scoring zero false positives do
  so with d′ = −0.17 and 100% orchestrated false negatives — a hit rate
  pinned to the floor, not accuracy. Acting on the inverted reading would
  have swapped in a model that detects nothing.
- **"No published practice keys a review stop rule on findings"** was a
  universal negative asserted from two examples, both of which key on
  findings.
- **"Seeded defects are easier to find than real ones"** had the
  direction and the attribution wrong. Andrews/Briand/Labiche (ICSE
  2005) find generated mutants resemble real faults, while hand-seeded
  defects are *harder*.
- **"Prose admits no cheap ground-truth generator"** is false; error
  seeding for documents dates to the Basili/NASA inspection work.

## Consumers

Every place that cites this audit, so an editor revising a claim above
knows what depends on it:

These are the passages that **cite this path**, outside this file. A
passage that draws on this audit without citing it (Directive 2's
clause-(b) instances, the 0.48.0 CHANGELOG entry) is not a site here and
will not appear when you re-run the command. The command also returns
this file's own re-run line and splits operative from frozen; neither
distinction is carried below.

- `loom-code/skills/requesting-docs-review/SKILL.md` — Directive 1's
  fix-round risk figure, its "why a cap" rationale, Directive 2's §Why,
  Step 3's `read-context` rationale (the stdin miss), and the red-flag
  row.
- `loom-code/CHANGELOG.md` — the 0.47.0 entry.
- `docs/loom/memory/README.md` §Format — the description-vs-body
  contradiction above is the recorded instance behind its rule.

Re-run the list with `python3 scripts/claim_copy_sweep.py --claim
"2026-08-04-docs-review-convergence-experiment"` rather than trusting
this enumeration after either document moves.
