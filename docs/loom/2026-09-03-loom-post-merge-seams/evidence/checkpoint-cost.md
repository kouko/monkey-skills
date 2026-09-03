# Checkpoint cost — recomputed at branch end

Written by the blind-runner (not the orchestrator who took the notes below),
2026-09-03, at HEAD `664159a8`, from `git log 160658c2..664159a8` and
`docs/loom/2026-09-03-loom-post-merge-seams/review.json`. Every number here
is recomputed from those two sources, not copied from
`evidence/checkpoint-cost-orchestrator-notes.md`. No coefficient is changed
by this table — the recommendation at the bottom is a recommendation, not a
decision (kouko, 2026-09-03: wait for the second and third real change).

## 1. Whole-branch totals

| measure | value | command |
|---|---|---|
| total commits on the branch | 82 | `git rev-list --count 160658c2..664159a8` |
| review-only commits (= checkpoints, one per completed round) | 30 | `git show --name-only --format=` on every commit; a checkpoint touches exactly `docs/loom/2026-09-03-loom-post-merge-seams/review.json` |
| verdicts recorded | 37, across 18 numbered rounds | `review.json["verdicts"]`, grouped by `round` |
| probes recorded | 44 (adversarial 31, blind-run 10, package-tests 3) | `review.json["probes"]`, grouped by `kind` |
| dispatch entries | 82 (reviewer 39, implementer 18, adversary 14, blind-runner 11) | `review.json["dispatch"]`, grouped by `role` |
| open findings, all-time | 75, of which 4 are dismissed (not fixed) | `review.json["open_findings"]` |

## 2. Commit breakdown by kind (82 total)

| kind | count | how identified |
|---|---|---|
| code / test with a `Task:` trailer | 18 | commit body contains `Task:` and is not itself a review-only/spec/evidence-only commit |
| review-only (checkpoints) | 30 | touches only `review.json` |
| combined round-record + next dispatch | 12 | subject starts `chore(loom): after-task …` / `chore(loom): spec round …` and records one round's outcome while dispatching the next; these did not get their own review-only commit because they are folded into the same commit as the dispatch |
| dispatch records | 8 | subject `chore(loom): dispatch …`, no round outcome attached |
| evidence-only | 11 | touches only files under `evidence/` |
| spec-version-only | 3 | touches only `spec.md` |
| new intent / plan-only | 8 | touches only `docs/loom/intent/*.md` or this change's `plan.md` |
| new intent (`2026-09-02-simple-loom-flow`) closed inside this branch's diff | (counted in the 18 code commits above, commit `996c69f0`) | `git show 664159a8:docs/loom/intent/2026-09-02-simple-loom-flow.md` reads `status: closed 2026-09-03 — PR #780` |

18+30+12+8+11+3+8 = 82. ✓

Twelve commits mix a round's outcome and the next dispatch in one commit —
the orchestrator's earlier notes counted these as three separate record
commits per round ("dispatch, evidence, review-only" — 3 → 24 of 46 commits
at an early snapshot); at branch end the actual shape leans more on
combined commits than that snapshot suggested, which is itself evidence for
recommendation candidate 3 below (it is already happening, informally).

## 3. Review rounds by scope (from `review.json["verdicts"]`, grouped by round)

| scope | rounds | round numbers | outcome pattern |
|---|---|---|---|
| spec | 11 | 1,2,3,4,5,6,7,8,11,12,13 | NEEDS_REVISION ×5 (rounds 1,2,3,5,7), PASS/PASS_WITH_NOTES ×6 (4,6,8,11,12,13) |
| after-task:W0-04 | 4 | 9,10,14,15 | NEEDS_REVISION ×3 (9,10,14 partial), PASS_WITH_NOTES/PASS ×1 (15) |
| after-task:W0-05 | 3 | 16,17,18 | NEEDS_REVISION ×2 (16,17), PASS_WITH_NOTES/PASS ×1 (18) |
| branch-end | this report | — | in progress (this dispatch) |

**Correction against the orchestrator's notes**: the addendum at W0 close
states "after-task W0-04 ... 5 rounds, 6 fix dispatches". `review.json`
carries only 4 verdict-rounds under the `after-task:W0-04` scope label
(9, 10, 14, 15) — rounds 11–13 that sit between them are labeled `spec`
(the opus design review triggered three narrow spec rounds mid-checkpoint,
because the after-task fix changed the spec's own design decision). If the
three nested spec rounds are counted as part of the W0-04 checkpoint's true
cost (they existed only because of findings raised against W0-04's design),
the orchestrator's "5" underclaims it — the honest count is 4 formal
after-task rounds **plus** 3 spec rounds interleaved, 7 total review
passes before W0-04 closed. This report keeps the two scopes visibly
separate above rather than picking one number, because collapsing them
would hide exactly the kind of cost recommendation candidate 5
(cross-scope churn from a content-reading rule) is about.

## 4. Side by side with the #771 replay

| | #771 replay (recomputed elsewhere) | this change |
|---|---|---|
| commits | 34 | 82 |
| review-only checkpoints | 31 | 30 |
| notable difference | single-purpose script-helper extraction, no spec-review stage | full `needs-design: yes` spec stage (11 rounds) dominates; the checker-rule work itself (W0) is comparable in shape to #771's |

The #771 number (34/31) was for a change with no spec stage. This change's
82 commits are not evidence the per-checkpoint coefficient grew — REQ-4's
own framing (§0) — they are evidence that a `needs-design: yes` engineering
change with real design churn (content-parsing rule → regenerate-and-compare
redesign) costs far more than three record-commits-per-round, because the
churn itself re-triggers rounds. Stripping the 11 spec rounds' commits
(spec-version 3 + a share of the 12 combined + a share of dispatch/evidence)
leaves the W0/W1 checker-and-cleanup work at roughly the same shape as
#771's per-checkpoint average.

## 5. Recommendation candidates — kept, dropped, reordered against the recomputed numbers

Source: `evidence/checkpoint-cost-orchestrator-notes.md`. Each candidate
below is re-examined against §1–§3's real numbers, not accepted on the
orchestrator's word.

1. **Kept, strengthened by the data**: *fix rounds re-dispatch only the arm
   that said NEEDS_REVISION.* Confirmed by §3: every spec round after
   round 4 still ran the same two-to-three-arm shape regardless of what the
   previous round found (round 7 — one stale sentence — still ran four
   arms per the orchestrator's note, and this report's round table shows
   no round narrowed itself on its own).
2. **Kept, but the recomputed number is smaller than claimed**: *red team
   on a spec, at most two rounds.* The orchestrator's rationale ("7 of 8
   rounds NEEDS_REVISION") does not fully hold against the branch-end
   count — spec had 11 rounds total, not 8, because three more (11–13)
   were needed after the redesign; the red team's actual unresolved-finding
   count across all 11 rounds is not separately recorded in `review.json`
   in a form this table can recompute without re-opening every round's
   evidence file, so this candidate is kept on the original rationale but
   flagged: it needs a per-arm verdict count, not a per-round one, to be
   sized correctly next time.
3. **Kept**: *dispatch record + evidence in one commit.* §2 shows this
   already happening informally (12 of 82 commits already combine a round
   record with the next dispatch) — formalizing it removes little further
   cost since the branch already converged there under time pressure.
4. **Kept**: *Codex as second vendor earned its place on the read arm.*
   Not independently re-verified here (would need reading every round's
   evidence file for which vendor raised which finding) — carried forward
   on the orchestrator's original citation (round 5 fatal, round 6
   contradiction, both Codex-only).
5. **New, from this recomputation**: *a content-reading gate rule is the
   single biggest cost driver on this branch.* §3's correction shows the
   close-commit-shape rule (`push.review-only-head`'s tightening) pulled in
   3 extra spec rounds (11–13) on top of its own 4 after-task rounds — 7
   rounds for one rule, out of 18 total. This is the same lesson the
   orchestrator's addendum already named ("content-reading rules are a
   category to avoid") but the recomputed round count makes the size of it
   visible: roughly 40% of every review round on this branch traces back to
   one rule design.
6. **Dropped as stated, folded into 5**: *"redesign trigger: a second
   NEEDS_REVISION on the same checkpoint sends the finding history to a
   fresh higher-tier agent."* The branch's own history shows this already
   happened once, informally, by user request (the opus design review at
   round 10/11) and it closed six rounds' worth of churn in one dispatch.
   Kept as a candidate, but reworded: this is not a new mechanism to add,
   it is a pattern that already worked once and should be looked for
   sooner next time.
7. **Not recommended, confirmed**: relaxing "two-plus-arm PASS" for code
   deltas. The two real gate defects this branch found (round 6's spec
   contradiction; the after-task rounds' six content-parsing edge cases)
   came from full-strength review, not a spot check.

## Recommendation (one line, not a decision)

The checkpoint coefficient itself looks about right for ordinary engineering
work (the W0/W1 rule-and-cleanup commits track #771's shape); what drove
this branch's cost past #771 was one content-reading rule design pulling in
7 of 18 rounds — so the coefficient to watch on the next two real changes is
not "commits per checkpoint" but "rounds per rule that reads file content",
and the fix that already worked once (escalate to a stronger model after
one repeated NEEDS_REVISION on the same design, not after N fix attempts)
is worth trying on purpose rather than by request.
