# Faster required-check observation — spec
intent: 2026-09-10-wait-for-ci-registration@a5d0847d04fff8a4e470456fcea805b4a9483f24
confirmed-behavior: 2026-09-10 @eae4aa9
pre-build-review: required — changes the public Ship timing and error-classification contract at the GitHub CLI boundary

## Requirements

REQ-1 — Registration delay
  WHEN GitHub reports that a newly published branch has no checks, the publisher shall retry every 10 seconds for up to 60 seconds without requiring another publish invocation → Acceptance #1

REQ-2 — Other observation failures
  IF GitHub returns an authorization, network, malformed-response, or other error that is not its no-checks response THEN the publisher shall stop immediately and preserve the concrete reason → Acceptance #2

REQ-3 — Registration grace expiry
  WHILE no required checks appear during the 60-second registration grace, the publisher shall report that no required checks are registered and finish successfully after the final observation → Acceptance #3

REQ-4 — Pending observation cadence
  WHILE required checks remain pending, the publisher shall recheck every 10 seconds for up to 60 minutes without emitting unchanged pending snapshots → Acceptance #4

## Design decision

- agent-decided — Treat only exit code 1 with blank stdout and GitHub CLI's explicit `no checks reported on the ... branch` stderr as an empty registration snapshot; keeping all other non-0/8 exits blocking avoids hiding authorization or transport failures.
- agent-decided — Express the limits as elapsed polling budgets: six 10-second registration waits followed by one final observation, and 360 10-second pending waits; this preserves the confirmed 60-second and 60-minute bounds instead of retaining obsolete attempt counts.
- agent-decided — Keep registration and pending counters separate because checks that appear near the end of registration still receive the full pending-monitoring budget.

## Alternatives considered

- Keep the existing two-snapshot rule with a 10-second interval — rejected because a slowly registered workflow would still be missed after only 10 seconds.
- Treat every exit code 1 as an empty snapshot — rejected because authentication and repository errors also use non-zero exits and must remain fail-closed.
- Query branch-protection configuration before polling — rejected because it adds another GitHub API surface without removing the registration race.

## Current state evidence

- Forward: `loom-code/scripts/loom_checker.py:3129` begins task-local required-CI observation after publication.
- Reverse: `loom-code/scripts/loom_checker.py:3137` invokes `gh pr checks --required` for every observation.
- Error: `loom-code/scripts/loom_checker.py:3147` rejects exit code 1 before the empty-snapshot retry at line 3159 can run.
- Data: `loom-code/scripts/test_loom_publish.py:939` reproduces blank stdout, exit code 1, and `no checks reported on the 'feature' branch` stderr.
- Boundary: `loom-code/skills/ship/SKILL.md:116` owns task-local CI observation; GitHub workflow configuration, branch protection, and persistent monitoring remain unchanged.

## UI flows

Publish opens or reuses a ready pull request and GitHub initially reports no checks → Loom stays quiet, checks again every 10 seconds, and requires no second publish command.

Required checks appear and remain pending → Loom stays quiet while rechecking every 10 seconds; pass prints `Required CI passed` and exits 0, while failure, cancellation, or required user action prints the concrete blocker and exits 1.

GitHub returns an observation error other than its explicit no-checks response → Loom immediately prints the concrete observation blocker and exits 1.

No required checks appear for the full 60-second registration grace → Loom prints `No required checks registered` and exits 0 after the final observation.
