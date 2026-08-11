# Were the 🟡 findings behind past 2+🟡 NEEDS_REVISION docs verdicts load-bearing?

**Date**: 2026-08-11
**Subject**: the 2+🟡→NEEDS_REVISION aggregation rule (`requesting-docs-review`
and its shared `rubrics/quality-gate.md` aggregation), sampled BEFORE the
`2026-08-10-yellow-findings-should-default-to-debt-not-revision-loops.md`
backlog proposal relaxes it.
**Denominator, stated plainly**: 6 verdicts, 14 classified 🟡 findings, drawn
from merged PRs' own review-trail narration. This is a thin, non-random
sample — see §Limits before citing a rate from it.

## Method

1. Enumerated merged PRs since `requesting-docs-review` shipped:
   `gh pr list --state merged --search "merged:>=2026-07-30" --json
   number,body,title,mergedAt --limit 100` → 55 PRs (#628–#685).
2. `git log --grep "review" --since 2026-07-30 --oneline` returned the same
   55 merge commits already covered by step 1 — no separate gate-marker or
   review-ledger commits exist in git history distinct from the squash-merge
   commits. Gate markers (`origin-ledger.json`, verdict JSON) are branch-local
   working-tree state under `<git-common-dir>/loom/`; they are not committed
   and do not survive past the branch's squash-merge. **The only reachable
   record of a historical verdict's finding content is the PR body's own
   review-trail prose** (most PRs in this repo narrate the review trail in
   detail as a close-out convention — see CLAUDE.md's git-memory / finishing
   norms). This is a real ceiling on what "reachable" means here, stated
   before the sample, not after.
3. Grepped every PR body for `NEEDS_REVISION`, `🟡`, `🔴`, `docs-review` /
   `docs arm` / `docs-reviewer` co-occurrence (33 of 55 PRs matched at least
   one).
4. Read the matching PR bodies in full. Kept only rounds that satisfy ALL
   of: (a) the round's own verdict was NEEDS_REVISION (explicit, or implied
   by a stated 2-round-cap firing / an authorized extra round), (b) the
   round's docs-arm findings are described as 🟡 only — no 🔴 attributed to
   the same round's docs arm, (c) the PR body's prose names each 🟡 finding
   specifically enough to classify it (not just a bare count).
5. Excluded, by reason:
   - Rounds whose NEEDS_REVISION was driven by an explicit 🔴 (e.g. #644 R1,
     #645 R1, #655 R1, #658 R1, #663 R1/R2 — "fatal" findings) — different
     rule, out of scope for this sample.
   - Rounds where the PR body reports a finding *count* with no per-finding
     detail (e.g. #647 R1's single docs finding — also below the 2+
     threshold; #639's round-2 findings are named but not tagged 🟡 vs 🔴 in
     the text, so classification would be guesswork).
   - Rounds already at PASS_WITH_NOTES with only 1 gating 🟡 (does not meet
     the 2+ rule at all — e.g. #681, #662, #669 R1 as narrated).
   - PR #629 itself (the ship point) and #628 (its precedent, pre-dates
     shipment) — excluded as before-the-fact, not reachable post-shipment
     instances.

## Sample table — 6 verdicts

| PR | Round | Arm | 🟡 | 🔴 in same round | Verdict |
|---|---|---|---|---|---|
| #644 | 2 | docs (2 arms) | 2 | 0 | NEEDS_REVISION |
| #648 | 1 | docs (2 arms) | 3 | 0 (the round's 1🔴 was the code arm's) | NEEDS_REVISION |
| #649 | 1 | docs (2 arms) | 2 (both explicitly "instruction-class") | 0 | NEEDS_REVISION |
| #656 | 2 | docs (2 arms) | 2 | 0 | NEEDS_REVISION (2-round cap fired) |
| #658 | 2 | docs (2 arms) | 2 (explicit "2 NEW placement 🟡") | 0 (round 2; the branch's 1🔴 was round 1) | NEEDS_REVISION (2-round cap fired) |
| #659 | 1 | docs (2 arms) | 3 | 0 | NEEDS_REVISION |

## Per-🟡 classification

**Test applied** (from the backlog seed and this arc's dispatch): load-bearing
= an instruction a weak model would execute wrongly, or a fact that misleads
a reader who trusts it. Conventional = label/format/style, no executable or
factual consequence.

| # | PR | Finding (paraphrased from the PR body) | Class | Reason |
|---|---|---|---|---|
| 1 | #644 | A remediation instruction told the orchestrator to "fold" an unscored finding block into a severity-keyed aggregation — no orchestrator can execute a fold into a schema that has no slot for it | **Load-bearing** | Literally unexecutable instruction; a weak model would either fabricate a resolution or silently drop the finding |
| 2 | #644 | A non-conformance roster claimed a population ("all N non-conforming entries") the author had never actually swept for | **Load-bearing** | A completeness claim a reader would trust and act on; false |
| 3 | #648 | Backlog reconciliation gap (doc's backlog state claim did not match the actual store) | **Load-bearing** | A reader trusting the doc's backlog-state claim would act on stale information |
| 4 | #648 | A heading positioned so a reader stops reading before reaching required content ("stop-early reading") | **Load-bearing** | Structural, but the stated consequence is missed instructions downstream of the heading |
| 5 | #648 | A verification step ("E-3 probe") the doc implied was run, but was missing | **Load-bearing** | Misleads about what was actually verified |
| 6 | #649 | A fail-closed clause's tail still read "either check" after the clause was tightened to require both | **Load-bearing** | Explicitly tagged instruction-class by the reviewer; a weak model reading "either" would take the looser, wrong branch |
| 7 | #649 | A reference file's preamble was falsified by a new normative section added elsewhere in the same file | **Load-bearing** | Explicitly instruction-class; the preamble now asserts something the file's own body contradicts |
| 8 | #656 | A round-1 fix's correction text was placed inside a block the file's own guard tells readers to skip | **Load-bearing** | The fix is invisible to a reader following the doc's own stated reading path |
| 9 | #656 | A gate condition's main clause contradicted its own parenthetical | **Load-bearing** | Direct self-contradiction in executable gate logic; ambiguous which half a weak model follows |
| 10 | #658 | A `--detail` clause, spliced into an existing pinned sentence, now read as carrying Stage/next fields it does not | **Load-bearing** | Changes what a template-copier would believe the contract requires |
| 11 | #658 | A placement rule was written where template-copiers would fold it into the Goal value | **Load-bearing** | Would produce malformed output when the template is actually copied |
| 12 | #659 | An evidence quote claimed "byte-preserved" text that the branch's own rewrite had in fact changed | **Load-bearing** | Misleading provenance claim a reader would trust |
| 13 | #659 | A second evidence quote, same defect | **Load-bearing** | Same reason as #12 |
| 14 | #659 | A two-word swap in prose directly contradicted the branch's own stated condition (c) | **Load-bearing** | A weak model reading condition (c) would apply the contradicted (wrong) reading |

**Load-bearing: 14 / 14 (100%)**

No finding in this sample classified as conventional (label/format/style with
no executable or factual consequence). Findings #3 and #4 are the closest to
borderline — thinner PR-body description than the rest — and are kept
load-bearing on the stated reasoning rather than dropped, per the "state the
denominator plainly, don't discard thin evidence silently" instruction.

## Verdict

**STOP — surface to user.**

Fraction (100%) is far above the 20% threshold the backlog seed set for
"proceed with the relaxation." Every 🟡 finding this sample could classify
in detail turned out load-bearing under the stated test — none were pure
label/format/style nits. This directly confirms, rather than refutes, the
backlog seed's own stated worry: *"the falsified-neighbor carriers were
🟡-tagged."*

## Limits — stated, not buried

- **N=6 verdicts, 14 findings**, out of 55 merged PRs and ~33 that mentioned
  review/NEEDS_REVISION/🟡/🔴 at all. No rate here generalizes past this
  corpus; a different repo, a different reviewer prompt, or a different
  session's narration style could shift it substantially.
- **Selection bias, in one direction only.** The sample is PR-body prose
  that *authors chose to narrate in enough detail to classify*. Findings
  narrated in detail are more likely to be the interesting, consequential
  ones — a genuinely trivial 🟡 ("period vs colon", "extra blank line") is
  more likely to be summarized as a bare count or folded into an
  undifferentiated "🟢 debt" list than spelled out. This sample therefore
  cannot rule out that many additional, purely conventional 🟡s exist in the
  same verdicts but were never narrated specifically enough to classify —
  it can only speak to the 🟡s that *were* narrated. The true load-bearing
  fraction over ALL 🟡s ever raised is very likely lower than 100%, but this
  sample has no way to measure how much lower.
- **No independent re-verification.** Unlike the 2026-08-04 docs-review
  convergence experiment (which re-read cited passages against source text),
  this sample took each PR body's own characterization of its findings at
  face value — it did not re-open the historical branch state to confirm the
  described defect was real. The PR bodies are close-out records written by
  the same session that fixed the findings, not adversarial re-checks.
- **Denominator collapse is itself informative.** Of the ~15+ NEEDS_REVISION
  docs-adjacent mentions found across the 55 PRs, most were disqualified for
  reasons OTHER than "the findings were conventional" — usually because a
  🔴 was present in the same round (a different rule), or the PR body didn't
  narrate individual findings precisely enough to classify. Very few rounds
  in this corpus were cleanly "2+🟡, no 🔴, fully narrated" — which is
  itself evidence that this repo's docs-review practice rarely produces a
  NEEDS_REVISION verdict built from throwaway 🟡s; the rounds that hit 2+
  tend to be rounds the reviewers thought worth explaining.

## Consumers

This audit is cited by the review-cost-reduction arc plan
(`docs/loom/plans/2026-08-11-review-cost-reduction.md`) as the sampling
step required before relaxing 2+🟡→NEEDS_REVISION to always-ships-as-debt.
The verdict above (STOP) means that relaxation cannot proceed on this
sample alone without the user weighing the trade-off explicitly: either the
relaxation is narrowed (e.g. only demote 🟡s a reviewer marks as
label/format at the time it raises them), or the user accepts the residual
risk this sample surfaces with eyes open.
