---
name: 2026-08-22-revert-condition-for-the-code-as-spec-no-op-bar
description: the no-op bar shipped in loom-code 0.94.0 is provisional — its benefit is 2/2 on a single run against a baseline that draws zeros 2 times in 5, and the same run drew the exercise's first control false positive, so this entry names in advance what evidence retires it rather than leaving a one-sentence rule to accumulate unexamined
status: open
origin: 2026-08-22 code-as-spec-lens-no-op-bar arc — shipped with the author's own assessment that the effect is unproven and the cost is real; recorded so the rule cannot survive on inertia
start: the second real-branch review in which a reviewer files a finding against an intent or absence sentence under deletion-first, or four real-branch reviews with no such finding — whichever comes first
---

- What shipped: one sentence in each reviewer arm's code-as-spec lens barring
  the reviewer from declaring the `deletion-first` dimension not applicable,
  a no-op, or out of scope on a diff that touches the prose it governs. It
  still permits a genuine PASS after finding nothing.

- Why it is provisional. The measured benefit is 2/2 on a single run — both
  barred arms evaluated the dimension and neither declared it a no-op. But
  the prior five samples of that dimension read `1/2, 2/2, 0/2, 0/2, 2/2`, so
  two clean draws are unsurprising from an unchanged contract. The claim that
  survives is only that the forbidden declaration did not appear, not that the
  bar caused its absence.

- The cost is not hypothetical. The same run drew the first control false
  positive in eight arms: one arm flagged "This module stays deliberately
  tolerant of a malformed header" as a mechanism the code shows. That is
  deliberate non-behaviour, and the lens's own carve-out says an absence claim
  is never deletable — so the finding contradicts the rule's own text, not
  merely the sandbox's answer key. Removing a reviewer's option to find
  nothing predictably pushes it toward finding something.

- **Retire the bar** when a second real-branch review files a `deletion-first`
  finding against an intent, goal, trade-off, or absence sentence — the
  classes the lens's second half and its carve-out protect. Two occurrences,
  per this repo's own one-occurrence-is-memory rule. Revert both arms'
  sentences and the test that pins them, and record the reversal in the
  dogfood README's results table alongside the run that motivated it.

- **Keep the bar, and say so** when four real-branch reviews pass with the
  dimension evaluated every time and no such false positive. Then the entry
  closes as evidence, not as neglect.

- Either way this entry closes with a written verdict. A one-sentence rule
  that nobody ever revisits is how a contract accretes judgment prose it
  cannot afford — which is the defect the arc that shipped this bar spent
  itself diagnosing.

- Evidence: `docs/skill-dogfood/2026-08-22-code-as-spec-reviewer-lens/README.md`
  §Results (eight arms) and `transcripts/barred-arm-1.md`, whose grading note
  records the control false positive verbatim. Reasoning for choosing this
  narrow bar over an artifact duty:
  `docs/loom/specs/2026-08-22-code-as-spec-lens-no-op-bar.md` §Decision.
