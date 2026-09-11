# What was recorded, and what the bar rejected

The change wrote a scarcity clause into the Record contract. This is the
first time it was applied to real candidates, and it is applied to this
branch's own material — which is the point: a rule about scarcity that is
never seen to reject anything is indistinguishable from a rule that
permits everything.

## Scope of the backlog

Sixteen candidates, spanning three changes: the two already merged
(`2026-09-10-okf-compatible-loom-memory`,
`2026-09-11-loom-memory-into-loom-workflow`) and this one. The first two
should each have recorded in their own branch and did not — which is the
failure this change exists to stop. Recording them here is the batched
catch-up, not the normal path.

**Recorded: 5 of 16.** Across three changes that is just over one each,
above what the clause calls the normal outcome — said plainly rather than
trimmed to fit, because this is a three-change backlog being cleared at
once. Two of the five were not on any list when this document was first
written: the first Record under the new bar failed a test, and the reason
it failed was durable; then the review episode produced the same test-design
defect four times, which is what turns a defect into a lesson.

## Recorded

| Concept | Why it qualified |
|---|---|
| `a-worktree-cleanup-by-pattern-match-destroys-other-peoples-work` | A named trap with an irreversible consequence, reachable by any future contributor writing a cleanup command. Nothing in the store covered removal-by-filter. |
| `an-acceptance-line-is-measured-against-the-trunk-before-it-is-written` | A rule about how an acceptance line is written, independent of the change that taught it. The nearest existing entry covers wrongly *claimed* pre-existing breakage, not genuinely unmeasured baselines. |
| `a-prose-pin-outlives-its-prose-only-if-it-explains-itself` | The lesson this change itself is built on, with the industry verification attached. Adjacent to `a-doc-pin-makes-a-prose-defect-permanent` but the opposite hazard, and the two are cross-linked rather than merged. |
| `an-assertion-scoped-wider-than-its-clause-is-about-something-else` | Four instances in one review episode, one written inside the commit that fixed the previous one. Every instance was found by mutation and none by reading. The cold reader rejected this candidate as a bug fixed inside the change; it is recorded anyway, and the disagreement is kept in the eval — recurrence across four independent sites is what separates a lesson from an incident. |
| `a-one-shot-acceptance-proof-against-a-moving-baseline-outlives-its-change` | Found by doing the recording: the previous change's migration-fidelity proof compared the store against a moving `origin/main`, so once it merged the assertion became "the store may never change" and the first new lesson failed it. Three of the skill's four operations would each have tripped it. |

## Rejected, with the reason and where it went instead

| Candidate | Verdict | Belongs in |
|---|---|---|
| A fidelity test silently skipped in its own CI job (checkout had no fetch depth) | REJECT | evidence — a defect in this arc's own verification, fixed in the same branch |
| `git archive` copies have no `.git`, so git-dependent verification fails in them | REJECT | evidence — a limitation of one verification method, superseded by the blind runner's real-worktree approach |
| Conflict-marker files staged and committed mid-rebase | REJECT | commit message — a one-off slip, corrected by redoing the rebase |
| `_quote_scalar` renamed to `_scalar_literal` | REJECT | commit message — change narrative |
| The review needed four rounds; the second vendor found two defects four same-vendor agents missed | REJECT | evidence — a verification record about one episode. The general claim (cross-vendor review finds what same-vendor review misses) is already in the store |
| One plugin's suite assumes a sibling is present; independent testability is unscoped | REJECT | backlog — an open task, not a lesson |
| A fix round hardcoded a changelog path and version into the CI command | REJECT | commit message — commit-bound; removing it was the fix |
| The store-integrity hook's shortest-suffix path derivation picks the wrong root | REJECT | backlog — borderline. The `%` vs `%%` trap is durable, but as stated this is an unfixed defect, and an unfixed defect is an item |
| `PRINCIPLES.md` was amended twice in two days in opposite directions | REJECT | nowhere — a fact about two changes, true of neither the charter nor the process |
| Marketplace publishes by version, so an unbumped skill change is a silent no-op | REJECT | already recorded — `feedback_skill_content_pr_requires_plugin_version_bump` covers it |
| Whether the published plugin version installs correctly from the marketplace | FOLLOW-UP | only confirmable after merge and publish; batched with other post-merge checks, not a branch of its own |

## The one the cold reader and ground truth disagreed on

The eval's reader marked the acceptance-line candidate REJECT, routing it
to evidence; ground truth marks it RECORD. Both readings are defensible —
the incident is bound to one change, the rule it teaches is not. It is
recorded here, and the disagreement is kept in
`loom-workflow/skills/loom-memory/evals/record-timing.md` rather than
resolved, because the clause's bias runs toward rejection and that is the
direction it was written to push.
