# Post-PR CI loop — implementation plan

Source brief: docs/loom/specs/2026-08-23-post-pr-ci-loop.md
Goal: Make `finishing-a-development-branch` wait for and repair CI after opening a PR.
Stage: review:round-2
Critical-path depth: 3 (≤5)
Total tasks: 4
Execution order: sequential
Plan-document-reviewer verdict: PASS (2026-08-23, round 3)

## Task 1 — Deterministic PR-check waiter

- Status: done(89b0aebd)

- **Brief item covered**: BI-1, BI-3
- **Module**: `loom-code/scripts/post_pr_ci.py`
- **Context paths**: `loom-code/skills/finishing-a-development-branch/SKILL.md`, `loom-code/scripts/loom_gate_markers.py`
- **Files touched**: `loom-code/scripts/post_pr_ci.py`, `loom-code/scripts/test_post_pr_ci.py`
- **Description**: Add a stdlib-only CLI that resolves the current PR and expected head, polls `gh pr checks` JSON, normalizes pass/fail/pending/cancel states, enforces head stability, no-check grace, and timeout, then emits a stable JSON result and exit code.
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_post_pr_ci.py::test_wait_pending_then_passes` and its sibling terminal/error cases fail at import because `post_pr_ci.py` does not exist.
  - **GREEN**: `python3 -m pytest loom-code/scripts/test_post_pr_ci.py -q` passes with pass, pending-to-pass, fail, timeout, no-check, operational-error, and head-drift cases; `python3 loom-code/scripts/post_pr_ci.py --help` exits 0.
- **Dependencies**: none
- **Independent**: false
- **Review-weight**: full

## Task 2 — Finishing workflow wiring

- Status: done(89b0aebd)

- **Brief item covered**: BI-2, BI-4, BI-5
- **Module**: `loom-code/skills/finishing-a-development-branch/SKILL.md`
- **Context paths**: `loom-code/skills/systematic-debugging/SKILL.md`, `loom-code/skills/requesting-code-review/SKILL.md`, `loom-code/skills/verification-before-completion/SKILL.md`, `loom-code/skills/using-loom-code/references/continuous-mode.md`
- **Files touched**: `loom-code/skills/finishing-a-development-branch/SKILL.md`, `loom-code/scripts/test_finishing_post_pr_ci.py`
- **Description**: Move the terminal beyond PR creation, invoke the helper against the created PR and current head, route failures through the existing bounded debug/review/verify/commit/push sequence, wait on the new head, and preserve all stop boundaries including never-auto-merge.
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_finishing_post_pr_ci.py::test_finishing_waits_repairs_and_rechecks_current_head` fails because Step 11 has no post-PR CI phase.
  - **GREEN**: `python3 -m pytest loom-code/scripts/test_finishing_post_pr_ci.py loom-code/scripts/test_continuous_mode_router.py -q` passes and pins the overview, delegation, bounded repair, new-head wait, stop states, and never-auto-merge terminal.
- **Reuse-adequacy**:
  - **Observed**: systematic debugging requires REPRODUCE before ISOLATE, HYPOTHESIZE, and VERIFY, and explicitly covers CI failures — `read loom-code/skills/systematic-debugging/SKILL.md:4`
  - **Observed**: finishing already routes a local verification failure to `tdd-iron-law` or `systematic-debugging` and stops before push — `read loom-code/skills/finishing-a-development-branch/SKILL.md:139`
  - **Intended**: reuse the debugging phases for remote CI evidence and the existing review/verification/commit/push gates after a fix; do not reuse the current STOP-at-local-failure control flow, because this new path has explicit bounded repair authorization.
- **Dependencies**: Task 1 completes first
- **Independent**: false
- **Review-weight**: full

## Task 3 — Shipping metadata and package verification

- Status: done(89b0aebd)

- **Brief item covered**: BI-4
- **Module**: `loom-code/.claude-plugin/plugin.json`
- **Context paths**: `scripts/sync_codex_manifests.py`, `loom-code/CHANGELOG.md`, `AGENTS.md`
- **Files touched**: `loom-code/.claude-plugin/plugin.json`, `loom-code/.codex-plugin/plugin.json`, `loom-code/CHANGELOG.md`, `docs/loom/INDEX.md`
- **Description**: Bump the plugin patch version, sync the Codex manifest, document the behavior, regenerate the living-spec index, and run the package-level suite and structural gates required by the repository.
- **Acceptance**:
  - **RED**: `loom-code/scripts/test_finishing_post_pr_ci.py::test_plugin_version_and_changelog_ship_the_ci_loop` fails while both manifests remain `0.97.6` and the changelog has no post-PR CI entry.
  - **GREEN**: `python3 scripts/sync_codex_manifests.py --check loom-code`, living-spec checks, targeted tests, and `python3 -m pytest loom-code/scripts/ -q` pass with a non-zero test count after the patch bump and changelog entry.
- **Dependencies**: Task 2 completes first
- **Independent**: false
- **Review-weight**: full

## Task 4 — Close-out ordering and autonomous entry corrections

- Status: done(uncommitted)

- **Brief item covered**: BI-6, BI-7
- **Module**: `loom-code/skills/finishing-a-development-branch/SKILL.md`
- **Context paths**: `loom-code/skills/subagent-driven-development/SKILL.md`, `loom-code/scripts/post_pr_ci.py`
- **Files touched**: `loom-code/scripts/post_pr_ci.py`, `loom-code/scripts/test_post_pr_ci.py`, `loom-code/skills/finishing-a-development-branch/SKILL.md`, `loom-code/skills/subagent-driven-development/SKILL.md`, `loom-code/scripts/test_finishing_post_pr_ci.py`, `loom-code/.claude-plugin/plugin.json`, `loom-code/.codex-plugin/plugin.json`, `loom-code/CHANGELOG.md`
- **Description**: Correct the CLI argument-error category, place PR-carrier validation before creation, require a repair commit before markers and push, and start finishing automatically after an approved autonomous plan completes.
- **Acceptance**:
  - **RED**: The targeted tests reject exit 4 for `nan`, PR-carrier validation after creation, missing repair commit ordering, and an SDD final-summary pause in autonomous mode.
  - **GREEN**: `python3 -m pytest loom-code/scripts/test_post_pr_ci.py loom-code/scripts/test_finishing_post_pr_ci.py -q` passes with the corrected ordering and `0.97.8` release metadata.
- **Dependencies**: Task 3 completes first
- **Independent**: false
- **Review-weight**: full

## Open Questions

N/A — no unresolved question: the approved brief fixes the helper boundary and repair policy.

## Decision Log

- 2026-08-23 — Use PR-wide checks rather than one workflow run because PR readiness can include multiple workflows and external checks.
- 2026-08-23 — Bound automated repair to two attempts and waiting to 30 minutes by default; both remain explicit helper/orchestrator constants rather than hidden indefinite loops.
