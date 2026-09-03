# Cold read round 2 — spec.md v3, 2026-09-03-loom-post-merge-seams

## Acceptance 1 — close-before-merge, push gate unchanged
Try: clean clone; after PR number known, commit exactly
`docs(loom): close intent <change-id>` changing `status:` to
`closed <date> — PR #<N>`; then a review-only commit (only review.json,
reviewed_sha = close commit); push. Then run `intake write-plan` on the
closed intent.
Expect: push passes on existing rules, no override; intake blocks with
`intake.confirmed: … this change is closed (PR #<N>); a new change starts
from a new intent`. Diff also closes 2026-09-02-simple-loom-flow.
Enough? Yes — commit message, file scope, and the intake block message are
now given verbatim (all were guesses in round 1).

## Acceptance 2 — grammar + tests green
Try: `loom_checker.py --list-rules` shows `closed <YYYY-MM-DD> — PR #<N>`
under `intake.confirmed`; run `python3 -m pytest loom-code/scripts/
scripts/ .claude/hooks/ -q` locally; check CI job
`pytest + knowledge-drift + codex-manifest-drift` green.
Enough? Yes — the literal package command is now spelled out (was a guess
in round 1).

## Acceptance 3 — scaffold refresh carries no trailer duty
Try: clean clone, run `codex_scaffold.py --repo .`, commit with no `Task:`
trailer, run `loom_checker.py push`.
Expect: `push.dispatch-covers-tasks` does not fire (content-bound
comparison against the running checker's own files, per Design decision).
Enough? Yes, unchanged from round 1 — command and rule id both named.

## Acceptance 4 — checkpoint cost table
Try: open `docs/loom/2026-09-03-loom-post-merge-seams/evidence/
checkpoint-cost.md`; check per-checkpoint commits/dispatches/review-rounds,
`git rev-list --count`, side-by-side with #771's 34/31, one recommendation
line, no coefficient changed.
Enough? Yes, path and columns explicit.

## Acceptance 5 — plugin versions bumped and observable
Try: after `claude plugin update <plugin>@monkey-skills`, check
`~/.claude/plugins/cache/monkey-skills/loom-code/1.0.1/` exists and run
`python3 .../1.0.1/scripts/loom_checker.py --list-rules` for the `closed`
grammar.
Enough? Yes — the exact directory and command to observe the version are
now given (was a guess in round 1: "where do I see the bumped version").

## Round-1 guesses — status in v3
1. Close-commit message text — ANSWERED (REQ-1 states
   `docs(loom): close intent <change-id>` verbatim).
2. "the full package command" — ANSWERED (REQ-2 gives the literal
   `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q`).
3. Where to observe the bumped version after `claude plugin update` —
   ANSWERED (REQ-5 names the cache directory path and the exact command).

Anchor mismatch flagged in r1 (`is_host_plumbing` vs `_is_host_plumbing`)
is also fixed: v3 Design decision now cites `_is_host_plumbing()
(loom_checker.py:400)`, matching the real symbol and line.

## New guesses (round 2)
None found that fork the deliverable. One non-blocking note: REQ-1's
"already-merged intent 2026-09-02-simple-loom-flow is closed the same way"
does not state that intent's own PR number — but it is a discoverable fact
(`gh pr list --state merged`), not a design ambiguity, so not counted as a
guess.

## Anchors checked (all resolved)
ship/SKILL.md:326-336 (still pre-change text, as expected for Current
state evidence), loom_checker.py:1557 (check_review_only_head), :791/
825-840 (CONFIRMED, intake.confirmed), :385-400 (HOST_PLUMBING_*,
_is_host_plumbing), :2082-2100 (commit_paths, check_dispatch_covers_tasks),
:455 (changed_paths docstring), manifest.yaml:85, templates/intent.md:7,
codex_scaffold.py (SHIM_TEMPLATE/_checker_copy_content/CONTRACT_COPY),
test_loom_checker_intake.py:385-449 (spec cites 385-447, function body
actually runs to 449 — 2-line drift, same function, not a resolution
failure), test_check_mechanisms.py:660-675, test_session_start_words.py:
45-55 — all match spec's descriptions.

## Verdict
Zero guesses.
