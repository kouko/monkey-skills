---
name: 2026-08-04-review-scope-stale-base-remedy-wrong-old-base
description: review_scope.py's stale-base refusal prints a rebase remedy whose old-base argument is not the branch's fork point, so following the printed command verbatim replays main's own commits and wedges in conflicts
status: COMMITTED-NEXT
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
required `git rebase --abort`. The correct old-base was
`git merge-base HEAD origin/main` = `f61837ed`; rebasing with that
succeeded 18/18 cleanly. A weak-model orchestrator following the printed
remedy verbatim wedges in conflicts it cannot diagnose.

Root-cause hypothesis (verify in the source before fixing): the remedy
uses a recorded/stale base rather than computing `git merge-base HEAD
<target>` at refusal time.

Next step: RED test first (fixture: branch whose fork point ≠ the remedy's
chosen old-base; assert the printed remedy's old-base equals the
merge-base). Fix in `review_scope.py`; tests live in
`loom-code/scripts/test_review_scope*.py`. Before editing the remedy
wording, sweep for copies of the remedy shape — the gate-markers/scope
specs may quote it (`loom-code/skills/requesting-code-review/references/gate-markers-spec.md`,
`loom-code/skills/requesting-docs-review/SKILL.md` Step 1 pass-down) —
per `docs/loom/memory/enumerate-every-copy-before-editing-a-claim-and-name-the-leaks.md`.
loom-code `scripts/` is plugin content: version bump + CHANGELOG entry are
named deliverables of the fix.
