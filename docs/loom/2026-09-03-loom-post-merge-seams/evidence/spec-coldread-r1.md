# Cold read — spec.md, 2026-09-03-loom-post-merge-seams

## Acceptance 1 — intent close commit passes push gate
Try: clean clone, edit prior intent's `status:` line to
`closed 2026-09-03 — PR #780`, commit exactly that one-line diff on one
file under `docs/loom/intent/`, run `loom_checker.py push`, then run
`intake write-plan` on that intent.
Expect: push gate passes with no `!` override; intake blocks with a message
naming the closed status.
Enough? Yes for the shape of the diff (REQ-1/spec Design decision spells out
"exactly one file... exactly one line... status: line"). The commit message
text itself is not prescribed by spec — I used the ship-station wording
found in the cited SKILL.md anchor (`docs(loom): close intent <change-id>`),
which is a **guess** since spec.md itself never states it.

## Acceptance 2 — grammar + tests green
Try: run `loom_checker.py --list-rules` and check the intent-status grammar
line lists `closed`; run the full `loom-code/scripts/` and `scripts/` test
suites locally and check CI is green; look for the repo self-check test's
expectation of `intake.confirmed` blocking (not `intake.spec-pass`).
Expect: grammar string includes `closed <date> — PR #<N>`; suites all pass.
Enough? Yes — the exact commands are named (`--list-rules`, "package
command"), though "the full package command" itself is not spelled out
verbatim anywhere in spec.md — a **guess** that it means the repo's
standard pytest invocation, inferred from CLAUDE.md/README convention
rather than stated in this spec.

## Acceptance 3 — scaffold-refresh commit carries no trailer duty
Try: clean clone, run `codex_scaffold.py --repo .` to refresh `.codex/hooks/`
copies only, commit with no `Task:` trailer, run `loom_checker.py push`.
Expect: `push.dispatch-covers-tasks` does not fire on this commit.
Enough? Yes — command and target rule id are both named.

## Acceptance 4 — checkpoint cost table
Try: after the change's own checkpoints finish, open
`docs/loom/2026-09-03-loom-post-merge-seams/evidence/checkpoint-cost.md`
and check it has a table of commits/dispatches/review-rounds per
checkpoint, `git rev-list --count` total, a side-by-side with #771's 34/31,
and one recommendation line (no coefficient changed).
Enough? Yes, path and required columns are explicit. Whether the
recommendation is a single sentence or something longer is not stated —
minor, not counted as a blocking guess since "one line" is explicit.

## Acceptance 5 — plugin versions bumped
Try: after merge, `claude plugin update` then `loom_checker.py --list-rules`
and check version metadata reflects new patch versions (loom-code 1.0.1,
loom-design 1.0.1, loom-workflow 4.0.1 per Design decision) with CHANGELOG
entries naming this change.
Enough? Version numbers are given in the Design decision section, so no
guess needed for target versions. **Guess**: spec doesn't say where to
literally see the "new version" after `--list-rules` (does it print a
version banner, or do I have to check `plugin.json`?) — I'd check
`.claude-plugin/plugin.json` by inference, not because spec names that
file for this check.

## Guesses
1. Exact commit message text for Acceptance #1 (spec doesn't restate it;
   I borrowed it from the cited ship SKILL.md line, not from spec.md
   itself — sentence: REQ-1's line never gives commit-message wording).
2. "the full package command" (Acceptance #2 / REQ-2) — spec never states
   the literal command string, only "the full package command is green
   locally and on CI."
3. Where to observe a plugin's bumped version after `claude plugin update`
   (Acceptance #5) — spec says "`loom_checker.py --list-rules` is new
   version" but doesn't say what output field carries the version, so I'd
   guess `plugin.json` / a printed banner.

## Anchors that did not resolve
- Design decision cites `is_host_plumbing()` at `loom_checker.py:401`; the
  actual function in the repo is named `_is_host_plumbing` (leading
  underscore) at that location — a naming mismatch, not a missing line.
  Not fatal to walking the acceptance line, but the spec's own anchor text
  doesn't match the symbol it names.
- All other cited anchors (ship SKILL.md:326-336, loom_checker.py
  check_review_only_head / intake.confirmed / commit_paths /
  check_dispatch_covers_tasks / HOST_PLUMBING_*, manifest.yaml:85,
  intent.md template, test_loom_checker_intake.py:385,
  test_check_mechanisms.py:664/670/672, test_session_start_words.py:49,
  loom_checker.py:455) resolved to real, matching lines.

## One-line verdict
3 guesses.
