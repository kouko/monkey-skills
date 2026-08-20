---
name: 2026-08-04-review-scope-stale-base-remedy-wrong-old-base
description: review_scope.py's stale-base refusal prints a rebase remedy whose old-base argument is not the branch's fork point, so following the printed command verbatim replays main's own commits and wedges in conflicts
status: closed
origin: 0.50.0 fix arc close-out (2026-08-04) — defect observed live on branch fix-docs-review-0490-adjudicated-defects
---

When `loom-code/scripts/review_scope.py` refuses a stale-base branch, its
stderr remedy suggests a `git rebase --onto <new-base> <old-base> HEAD`
command. Observed live: on a branch forked from `f61837ed` (then-main tip)
with origin/main advanced to `4c2937d5`, the printed remedy was

```
git rebase --onto 4c2937d5ed6e6b38e070cfc1efdefe4a1781f4e8 099af0c92fdf96b4c3e145eeb6b82d159abb8b46 HEAD
```

`099af0c9` is a commit in main's own history (PR #645), NOT the branch's
fork point. Running the command verbatim replayed main's own commits onto
main's tip and hit conflicts ("Could not apply f422f494..."); recovery
required `git rebase --abort`. The old-base that worked was `f61837ed` —
the branch's creation point (the recording session mislabeled it as the
merge-base; the verified root cause below corrects that): rebasing with
it succeeded 18/18 cleanly. A weak-model orchestrator following the
printed remedy verbatim wedges in conflicts it cannot diagnose.

Root cause (verified 2026-08-04 by git-history reconstruction —
OVERTURNS the original hypothesis, kept here honestly): the script
already computes `git merge-base HEAD <ref>` at refusal time and the
printed `099af0c9` WAS the true merge-base. The branch had been cut
from `f61837ed` — the tip of the previous arc's merged-but-squashed
local branch `docs-loom-close-out-backlog-and-memory` — so
merge-base..HEAD contained 7 foreign commits whose content was already
squash-merged into main; squash changes patch-ids, so rebase cannot
skip them and their replay is what conflicted. The remedy is unsafe
precisely in the stale-cut state it exists to heal (second occurrence
of that state; see
`docs/loom/memory/new-arc-branch-bases-on-origin-main-not-merged-tip.md`).

Fix shipped this arc (user-approved Option A): the remedy prefers the
branch's reflog creation sha as the printed old-base when it is a
descendant-or-equal of the merge-base and an ancestor of HEAD;
otherwise it falls back to the merge-base and prints a
verifiable-action caveat line. RED coverage:
`loom-code/scripts/test_review_scope.py` (creation-sha selection,
fallback caveat, detached-HEAD None).

Swept 2026-08-06: shipped in loom-code 0.51.0 / PR #648 (squash 0366f993)
— `loom-code/scripts/review_scope.py:236-259` reflog-based
`branch_creation_sha` + `:288-325` dual-ancestry-gated remedy with
merge-base fallback caveat.
