# A/B results — round 2: silent sweep vs verbalized checklist

Date: 2026-09-01 · Second A/B, prompted by the question "should the self-check
be a written checklist instead of silent?" Single variable: rule 14's output
framing (silent, emit nothing — the shipped form — vs written, work through the
five actions as visible working lines). Contract otherwise byte-identical; the
five actions (a)-(e) unchanged. 8 draft generations (2 cases × 2 arms × 2 reps)
+ 8 blind judgings. Confounds fixed from round 1: tasks name ONLY the primary
change (restatements must be *discovered*, not spoon-fed); literal `Files
touched:` framing so the trigger fires in every run (it did — 8/8); judges told
to review content regardless of file class (no record-class N/A).

## Headline

**No measurable benefit from the written form; if anything it scored slightly
worse, driven by one draft within n=2 noise.**

| metric | Arm S (silent — shipped) | Arm V (written checklist) |
|---|---|---|
| runs | 4 | 4 |
| first-round gating findings (instruction-class) | 1 | 4 |
| — all cause A (stale-neighbour) | 1 | 4 |
| clean runs (0 findings) | 3/4 | 2/4 |
| draft tokens (mean) | 25518 | 25465 |
| hedge marks | 0 | 0 |

By case: case1 tied (S=1, V=1); case2 S=0, V=3 — but all three V findings are
ONE draft (r03) that missed restatements. The other three V drafts were as
clean as the silent ones.

## What actually decides it (both rounds agree)

**Draft-to-draft variance, not the form.** Both silent and written produced
drafts that swept thoroughly — catching the *un-named* paraphrase restatements
(`蓋滿正交視野`, `icon 保持正交俯視`, and case 1's `替代方案`/`單向門`/`出典`
dependents) — and drafts that missed them. Whether a given draft catches the
paraphrase restatements turns on whether that agent reasoned *semantically*
about where the changed claim is depended on, versus running action (a)'s
literal `grep exact key phrases` and concluding "none found". The written form
did not force the semantic reading: r03 (written) still grepped-and-missed;
r02 and r08 (one silent, one written) both swept thoroughly.

## The deeper finding this surfaced

Action (a) as worded — "grep the exact key phrases/strings of each changed
claim" — is the wrong instrument for the dominant defect class. The stale
neighbours are **semantic dependents** (a bullet that reasons *from* the false
cause without repeating its words), which no literal grep finds. Agents that
succeeded did so by ignoring the literal-grep wording and reasoning about
dependency; agents that failed followed it literally. This is a content defect
in action (a), independent of silent-vs-written, and is the change most likely
to actually move the metric — untested here.

## Verdict on the form question

The written-checklist variant the user proposed is a reasonable idea
(chain-of-verification: verbalizing forces the look) but is **not supported by
this test** — n=2 per cell, one draft swings the arm, and both forms show the
same variance. Combined with round 1 (silent vs none, also null), the honest
position across two A/B rounds is: **a prose self-check instruction shows no
measurable benefit on the registered metrics in any form tried (none / silent /
written).** The lever, if there is one, is rewording action (a) to target
semantic dependents — or a standing mechanism — not the output framing.

## Isolation

No sibling-baseline-corpus cases. Reviewer prompts unmodified in both arms.
Only rule 14's output framing varied. Raw drafts / blind copies / judge
verdicts / tally input in this session's scratchpad (`.../scratchpad/ab/`),
session-local, not committed.

## Dogfood of the reworded action (a) — n=1, blind, artifact-checked

After rewording action (a) (commit c31f1553), one implementer was run under the
current contract on the case-1 discovery task (task names only the primary
cause fix; the 替代方案/單向門判定/出典 dependents must be discovered). A blind
docs-reviewer then checked the artifact — not the implementer's self-report —
per dependent statement:

| dependent | reconciled? |
|---|---|
| 替代方案 | yes (minor ditto ambiguity) |
| 出典 | yes |
| 單向門判定 | **no — left stale** |

Reading: the reworded action (a) is a real behavioral improvement — the agent
quoted the new "restated OR depended on" wording and caught 2 of 3 semantic
dependents that the earlier literal-grep-and-stop behaviour missed — but n=1
and incomplete (one dependent still stale; verdict PASS_WITH_NOTES). The
dogfood also re-confirmed [[a-weak-model-reporting-it-ran-a-silent-self-check-is-not-evidence-the-check-worked]]:
the implementer's note claimed it "touched the alternatives and 出典 and reasoned
about dependents" but never mentioned 單向門判定, which the blind artifact check
found stale — the self-report was more thorough than the output. Not a
statistical result; a "does the change fire as intended" behavioral check.

## Confirmation A/B: does the action-(a) reword actually help? (n=4/arm, single variable)

Prompted by "confirm the last change has an effect." Clean single-variable
comparison: OLD (literal-grep action a) vs NEW (semantic-dependent action a),
built by swapping ONLY action (a) on the current HEAD contract (everything else
byte-identical). Same case-1 discovery task, 4 reps each, blind judge scores
each draft's dependents-reconciled out of 3 (替代方案 / 單向門判定 / 出典).

| arm | per-draft scores /3 | mean |
|---|---|---|
| OLD (grep exact phrases) | 0, 1, 2, 3 | 1.50 |
| NEW (restated OR depended on) | 1, 2, 3, 3 | 2.25 |

**Δ mean = +0.75/3, in the intended direction.** This is the first change in
the whole arc to show a measurable positive effect — the two earlier A/B rounds
varied the OUTPUT FORM (none/silent/written) and were null, while this varies
the ACTION (a) CONTENT and moves the needle. It confirms the lever is the
action's wording (literal-grep → semantic-dependent), not the output framing.

Honest limits: n=4/arm, distributions overlap (OLD has a 3, NEW has a 1), so
this is a directional shift in the distribution, not a firm effect size and not
a fix — NEW's worst draft still reconciled only 1/3. Single case, single task
shape; generalization untested. The reworded action (a) makes a weak model MORE
LIKELY to catch semantic dependents, not reliably catch all of them.

## Refinement A/B: does an added "reconcile in place" clause help? — NULL, not shipped

The confirmation above showed 出典 (citations) is the most-often-missed dependent,
and the miss shape is systematic: agents append a new correction elsewhere while
leaving the original stale citation standing. A candidate refinement added a clause
to action (a): "Fix each where it sits ... a correction added elsewhere while the
original still stands does not count." Tested BEFORE committing (control = current
semantic action a; treatment = + the clause), single variable, 4 reps each, blind
per-dependent scoring:

| arm | scores /3 | mean | 出典 reconciled |
|---|---|---|---|
| control (semantic action a) | 1,2,2,3 | 2.00 | 2/4 |
| + in-place clause | 1,2,2,3 | 2.00 | 1/4 |

**Δ = 0.00; on its own target (出典) the clause did slightly worse (1/4 vs 2/4,
n=4 noise).** The clause was NOT committed — tested first, no effect, dropped.

Two conclusions, both load-bearing:
1. **Diminishing returns confirmed.** The big content change (literal-grep →
   semantic-dependent) moved the metric +0.75/3; this small refinement moves it
   0.00. The lever was the action's core content, not further wording.
2. **The n=4 noise floor is ≈ the refinement effect size.** This same semantic
   contract scored 2.25 in the first confirmation and 2.00 here — a 0.25 swing
   from variance alone across two n=4 runs. A refinement whose true effect is
   ≤0.25 cannot be detected at n=4; detecting it needs far more reps than it is
   worth. This is why the wording-tuning loop stops here.
