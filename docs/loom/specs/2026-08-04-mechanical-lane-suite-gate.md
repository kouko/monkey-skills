# Brief: mechanical-lane suite gate + worktree-reviewer dispatch guidance

Date: 2026-08-04
Source: live observations from the 0.51.0 fix arc (PR #648), reported to
the user at close-out and approved for immediate fix（「可以現在直接做修改嗎」→ 開工）.
Status: FROZEN.

## Problem (both observed live, same session)

1. **Mechanical-lane tasks have no "suite still green" condition.**
   `Review-weight: mechanical` skips both reviewers and its deterministic
   self-check verifies only content match + scope match; nothing between
   the task commit and the whole-branch review runs the package suite.
   Live case: the 0.51.0 bump task passed its self-check and
   `check_version_bump.py` while the branch tip was RED — the
   shipping-version pin test (`test_docs_review_blocking_class.py`) lived
   in a file no task touched. Caught only by the whole-branch panel (the
   most expensive layer) and, post-push, CI.
2. **Worktree-isolated reviewer dispatches land on a checkout that is not
   the branch tip.** The orchestrator's working tree holds the branch, so
   `isolation: worktree` detaches the reviewer at the default-branch tip.
   Live costs on the 0.51.0 arc: every reviewer independently
   rediscovered the mismatch; flat-extraction test runs produced spurious
   failures (13 path-artifact failures in one spec review; two
   codex-git-guard-shim environmental failures re-proven in at least
   three separate reviews); docs arms stamped `standards_version` from
   the worktree manifest (0.50.0) instead of the reviewed branch's
   (0.51.0).

## Decisions

1. The mechanical self-check gains a third required part: run the
   resolved package test command after the task's commit; any failure
   fails the self-check (falls back to the full triad like the other two
   parts). Wording must fit SDD SKILL.md's remaining CHK-SKL-010 budget
   (4435/4500 at branch base).
2. Worktree-reviewer guidance lives in SDD's
   `references/dispatch-hygiene-notes.md` as a new section (references
   are not word-capped; both requesting-code-review's panel step and
   SDD's reviewer dispatches route through this file's neighborhood).
   Content: worktree may be detached at the default-branch tip — address
   the artifact via `git show <branch>:<path>` / `git show <sha>`; name
   known environmental test failures in the dispatch packet instead of
   letting each arm re-prove them; stamp `standards_version` from the
   REVIEWED BRANCH's manifest, not the worktree's.
3. Plugin bump 0.51.0 → 0.52.0 with all FOUR deliverables (manifest,
   codex sync, CHANGELOG entry, shipping-version pin test rewrite — the
   variant recorded in
   `docs/loom/memory/version-bump-packets-must-name-changelog-entry.md`),
   and the bump task itself runs the full suite after its commit,
   practicing Decision 1.
4. No backlog entries: the fix ships now; the durable lesson is already
   in the repo memory store.

## Smallest End State

1. SDD SKILL.md §Mechanical review-weight exemption lists three required
   self-check parts; "both/either" wording updated; file ≤ 4500 words;
   prose-pin pytest in `loom-code/scripts/`.
2. `dispatch-hygiene-notes.md` carries a §Worktree-isolated reviewer
   dispatch section with the three guidance points; prose-pin pytest.
3. loom-code at 0.52.0 with CHANGELOG entry and pin test at 0.52.0;
   `check_version_bump.py` and full suite green at tip.

## Out of scope

- Pre-dispatch capacity/quota checks (no reliable CLI surface — reported
  honestly as unmechanizable; recovery protocol stands).
- claim_copy_sweep live-tree count caveat and the T9-style
  pinned-replacement-scope lesson (next-touch / plan-author practice).
- Changing the Agent tool's worktree checkout behavior (harness-owned).
- Any edit to the two word-capped review SKILL.md files.
