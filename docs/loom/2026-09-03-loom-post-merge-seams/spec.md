# loom 1.0 merge 後的接縫 — spec
intent: 2026-09-03-loom-post-merge-seams@90aedebf

## Requirements
REQ-1 — Intent close commit passes the push gate
  A commit whose only change is one intent file's `status:` line moving from `confirmed <date>` to `closed <date> — PR #<N>` passes `loom_checker.py push` on its branch with no other artifact required, and `intake write-plan` on that intent blocks with a message naming the closed status → Acceptance #1
REQ-2 — Contract grammar knows `closed`
  The manifest's `status` grammar and the intent template's status comment both list `closed <date> — PR #<N>`; `--list-rules` shows it; the repo's self-check test expects a closed intent to block intake on `intake.confirmed` (not on `intake.spec-pass`), and the full package command is green locally and on CI → Acceptance #2
REQ-3 — Scaffold copy is host plumbing for the trailer rule too
  `push.dispatch-covers-tasks` ignores the same path set `changed_paths` ignores (`HOST_PLUMBING_FILES` and `HOST_PLUMBING_DIR_PREFIX`), so a commit that only refreshes `.codex/hooks/` scaffold output carries no trailer duty → Acceptance #3
REQ-4 — Checkpoint cost measured on this change
  `docs/loom/2026-09-03-loom-post-merge-seams/evidence/checkpoint-cost.md` holds one table — per checkpoint: commits, dispatches, review rounds — plus the branch's `git rev-list --count`, side by side with the #771 replay (34 / 31), and one line of recommendation; no coefficient is changed → Acceptance #4
REQ-5 — Plugins versioned
  loom-code, loom-design and loom-workflow each carry a new patch version with a CHANGELOG entry naming this change, so `claude plugin update` picks them up → Acceptance #5
REQ-6 — Six carried test nits closed
  R24-O2 (`changed_paths` docstring "below"→"above"), R28-O2 (`check=True` on the skip-guard probe), R30-O1 (literal 5 pinned), R30-O2 (no-`wc`-subprocess guard replaces the moot locale test), R30-O3 (`_run` decodes UTF-8 explicitly) are fixed with the package suite green → Acceptance #2 (part of "the full package command is green")

## Design decision
- **Intent close path (agent-decided).** `push.review-only-head` gains a second accepted shape: HEAD touches exactly one file under `docs/loom/intent/`, and the diff of that file is exactly one line — the `status:` line — whose new value matches `closed <YYYY-MM-DD> — PR #<N>`. Everything else about the push gate is unchanged (the other push rules still run; a closing commit that also edits another file is still blocked). Reason: the ship station already prescribes this commit and it is the only post-merge write the flow needs; a one-line, grammar-checked docs edit is the narrowest possible exemption, and it is recomputed from the diff, not declared. Rejected: folding `closed` into the next change's review-only commit (the next change may be weeks away, and the intent would look unfinished meanwhile — the ship station's own warning).
- **`intake.confirmed` on a closed intent (agent-decided).** Keeps blocking, with the message "this change is closed (PR #N); a new change starts from a new intent" — the rule's existing shape, one more branch; `closed` is not a pass state anywhere.
- **Trailer-rule exemption (agent-decided).** `check_dispatch_covers_tasks` filters `commit_paths()` through the existing `is_host_plumbing()` predicate (loom_checker.py:401) before classifying — one call site, no new constant, so the two rules cannot drift again.
- **Contract version (agent-decided).** The manifest's contract version stays 1.0: adding an accepted value to a frontmatter grammar is backward compatible for every consumer that requires `>=1.0`. Plugin versions: loom-code 1.0.1 (checker + template), loom-design 1.0.1 (its stations' prose lists the status values), loom-workflow 4.0.1 (decision-map reads the intent status to show delivery state).
- **Checkpoint-cost table (agent-decided).** Written by the blind-runner at branch end from `git log` and `review.json`, not by an implementer, so the numbers are recomputed by someone who did not produce them. Recommendation only — the user deferred the decision (user-decided 2026-09-03).
- **Merge (user-decided 2026-09-03).** The user presses merge; the ship station's text for this repo is not changed by this spec — the agent stops after `gh pr create`.
- **Test nits (agent-decided).** Fixed in the same task as REQ-3 where they share a file (`test_check_mechanisms.py`, `test_session_start_words.py`), otherwise as one small task; the R30-O2 replacement asserts `"wc"` is not a subprocess argument anywhere in `check_mechanisms.py` (inspect the module source), which fails for both a pinned and an unpinned reintroduction.

## Alternatives considered
- A `push` flag or waiver for docs-only commits — rejected: reintroduces a declared bypass; the design has no waivers (concept-model §7).
- Writing `closed` before the merge, inside the last review-only commit — rejected: false until the merge happens, and the review-only commit may touch only `review.json`.
- Making the trailer rule read `changed_paths()` directly — rejected: that function returns the branch delta, while the rule walks commits one by one; sharing the predicate is the smallest common piece.
- Bumping only loom-code — rejected by Acceptance #5 (user-confirmed) and because both sibling plugins describe the status values in prose.

## Current state evidence
- Forward：`loom-code/skills/ship/SKILL.md:326-336` prescribes the close commit (`status: closed <YYYY-MM-DD> — PR #<N>`) after the merge; `loom-code/scripts/loom_checker.py:1557` (`check_review_only_head`) rejects any HEAD that touches a file other than `review.json`.
- Reverse：`loom-code/scripts/loom_checker.py:825-835` (`intake.confirmed`) accepts only `confirmed <date>`; `loom-code/scripts/test_loom_checker_intake.py:385` (`test_the_repos_own_change_matches_its_own_review_json`) expects the repo's own change to block on `intake.spec-pass` only — red on CI since the intent was closed (PR #781 run).
- Error：PR #781 — push blocked by `push.review-only-head`; CI red on `intake.confirmed` with "status is closed 2026-09-03 — PR #780".
- Data：`loom-code/contract/manifest.yaml:85` grammar `open | confirmed <date> | withdrawn — <reason>`; `loom-code/contract/templates/intent.md:7` comment mirrors it; `loom_checker.py:389-401` `HOST_PLUMBING_FILES` / `HOST_PLUMBING_DIR_PREFIX` / `is_host_plumbing`; `loom_checker.py:2085` `commit_paths` (no plumbing filter); `:2095` `check_dispatch_covers_tasks`.
- Boundary：no rule semantics beyond the two named change; `.codex/hooks/loom-checker` command string untouched; the checkpoint coefficient (three commits per checkpoint) is measured, not changed; six nits at `test_check_mechanisms.py:664/670/672`, `test_session_start_words.py:49`, `loom_checker.py:455`.

## UI flows
N/A — no surface a user reads or types into changes; the touched template is a file agents fill in, and the `closed` value is written by the ship station, never typed by the user.
