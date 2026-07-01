# Plan: F4 — executable both-carrier verify gate at branch close-out

Source brief: docs/loom/specs/2026-06-23-git-memory-f4-close-out-verify-gate.md
Evidence: docs/skill-mining/2026-06-22-git-memory-findings.md F4 + project_git_memory_p1p2_merge_gate_verified_survival.md
Total tasks: 5 (width OK; 2 parallel leaves mid-level, 2 parallel leaves at final level)
Critical-path depth: 3 (≤5) — longest chain: Task 1 → Task 2 → Task 4a/4b
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-23, 14/14 checks, round 1)

## Notes

- Carrier policy (user, 2026-06-23): **both carriers required** — commit-carrier (`git log --grep`/`--verify HEAD`==0) AND PR `## Memory`.
- Open-Q resolutions (user-approved): gate hardness = **STOP** (block push, like finishing's other 🔴/test gates); loom-code version = **minor**; PR-carrier check = prose only (agent greps the PR body it just authored), no new tooling.
- **Plugin boundary**: the gate lives in **loom-code** (`finishing-a-development-branch`); it calls the **dev-workflow** `--verify` script shipped in #445. finishing already references `dev-workflow:git-memory` (Phase 3 P3-D), so this is consistent cross-plugin use, not new coupling. Version bump is **loom-code**, not dev-workflow.
- The generative half (close-out authors trailers) already exists (finishing Phase 3/4 + compose-commit.md) — F4 adds only the executable verification, no new generation.
- Task 1 is a TDD pair (Module = finishing SKILL.md; the grep-assertion test extends the existing `test-git-memory-delegation.sh`, mirroring the accepted P1+P2 plan pattern where a task owns impl + its test).
- Cross-ref tasks (2, 3) are minor prose alignments so P2's verify prose points at the now-executable gate; they depend on Task 1 (the gate they reference must exist) — doc-mirrors-code semantic dependency.

## Task 1 — executable both-carrier verify gate in finishing-a-development-branch (+ test)

- Description: Add an executable verify gate to `finishing-a-development-branch`'s Default flow. (a) After the close-out commit (Step 9) and before push (Step 10): run `dev-workflow/skills/git-memory/scripts/memory-grep.sh --verify HEAD`; if git-memory's Phase-3 trailer set was non-empty (memory-worthy branch) AND `--verify` exits 4, **STOP** and surface "close-out commit didn't capture the memory trailers — fix before push" (consistent with finishing's other STOP gates). If Phase 3 returned empty (routine branch), exit 4 is expected → proceed. (b) At PR creation (Step 11) for a memory-worthy branch: confirm the PR body carries a `## Memory` section before declaring the PR ready; absent → flag. Extend `loom-code/tests/integration/test-git-memory-delegation.sh` with grep-assertions that finishing's flow contains the `--verify HEAD` commit-carrier gate and the PR `## Memory` check.
- Module: loom-code/skills/finishing-a-development-branch/SKILL.md
- Files touched: loom-code/skills/finishing-a-development-branch/SKILL.md, loom-code/tests/integration/test-git-memory-delegation.sh
- Context paths:
  - loom-code/skills/finishing-a-development-branch/SKILL.md (Default flow Steps 6–13; Phase 3/4 overview)
  - loom-code/tests/integration/test-git-memory-delegation.sh (existing harness to extend)
  - dev-workflow/skills/git-memory/scripts/memory-grep.sh (the --verify contract: exit 0/4/1/2)
- Acceptance:
  - RED: extend the test with the new assertions FIRST — `bash loom-code/tests/integration/test-git-memory-delegation.sh` fails because finishing SKILL.md has no `--verify` gate yet (`grep -- '--verify' loom-code/skills/finishing-a-development-branch/SKILL.md` → no match).
  - GREEN: the test passes — finishing SKILL.md names the post-commit `--verify HEAD` commit-carrier STOP gate AND the PR `## Memory` presence check; `grep -c -- '--verify' loom-code/skills/finishing-a-development-branch/SKILL.md` ≥ 1.
- External surfaces: `memory-grep.sh --verify` (dev-workflow sibling script, in-repo; cross-plugin reference already established via P3-D) — no new external dependency.
- Dependencies: none
- Independent: false
- Brief item covered: "Wire an executable both-carrier verify gate into finishing-a-development-branch's Default flow … commit-carrier gate (post-commit, pre-push) … PR-carrier check (at PR creation)."

## Task 2 — compose-pr.md Step 7 cross-ref to the enforced gate

- Description: In `dev-workflow/skills/git-memory/protocols/compose-pr.md`, update the Step-7 pre-close verify prose (shipped in P2) to cross-reference the now-executable gate in `loom-code:finishing-a-development-branch` as the enforcement point — so the description and the executed step agree. One-line pointer; do not duplicate the gate logic.
- Module: dev-workflow/skills/git-memory/protocols/compose-pr.md
- Files touched: dev-workflow/skills/git-memory/protocols/compose-pr.md
- Context paths:
  - dev-workflow/skills/git-memory/protocols/compose-pr.md (Step 7, the pre-close verify section)
- Acceptance:
  - RED: `grep -i 'finishing-a-development-branch' dev-workflow/skills/git-memory/protocols/compose-pr.md` → no match (Step 7 describes the verify but does not point at the enforced gate).
  - GREEN: Step 7 references `finishing-a-development-branch` as the enforcement point for the pre-close verify; grep-present.
- Dependencies: Task 1 completes first (the gate it points to must exist — doc-mirrors-code).
- Independent: true
- Brief item covered: "Make the existing P2 prose point at this enforced gate — compose-pr.md Step 7 … cross-ref … so the prose and the enforcement agree."

## Task 3 — git-memory SKILL.md Pillar 2 cross-ref to the enforced gate

- Description: In `dev-workflow/skills/git-memory/SKILL.md` Pillar 2, add a one-line cross-reference from the verify-required prose (shipped in P2) to the executable gate in `loom-code:finishing-a-development-branch`. Pointer only; do not duplicate the gate.
- Module: dev-workflow/skills/git-memory/SKILL.md
- Files touched: dev-workflow/skills/git-memory/SKILL.md
- Context paths:
  - dev-workflow/skills/git-memory/SKILL.md (Pillar 2 verify-required region)
- Acceptance:
  - RED: `grep -i 'finishing-a-development-branch' dev-workflow/skills/git-memory/SKILL.md` → no match in Pillar 2.
  - GREEN: Pillar 2 references `finishing-a-development-branch` as where the verify is enforced; grep-present.
- Dependencies: Task 1 completes first (doc-mirrors-code).
- Independent: true
- Brief item covered: "Make the existing P2 prose point at this enforced gate — … SKILL.md Pillar 2 … cross-ref … so the prose and the enforcement agree."

## Task 4a — loom-code plugin version bump (minor)

- Description: Increment `loom-code/.claude-plugin/plugin.json` `"version"` by a minor bump (new enforced close-out verify gate). Single-field edit.
- Module: loom-code/.claude-plugin/plugin.json
- Files touched: loom-code/.claude-plugin/plugin.json
- Context paths:
  - loom-code/.claude-plugin/plugin.json (current version field — currently 0.19.0)
- Acceptance:
  - RED: the intended new minor version string does not yet appear (`grep` → no match).
  - GREEN: `version` incremented by a minor; file valid JSON (`python3 -c 'import json; json.load(open("loom-code/.claude-plugin/plugin.json"))'` exits 0); new version string grep-present.
- Dependencies: Tasks 1, 2, 3 complete first.
- Independent: true
- Brief item covered: "loom-code version bump … (the gate lives in the loom-code finishing-a-development-branch skill)."

## Task 4b — loom-code CHANGELOG entry

- Description: Add a dated `loom-code/CHANGELOG.md` entry (matching the file's existing format) for the new version, summarizing F4: an executable both-carrier verify gate in `finishing-a-development-branch` (post-commit `--verify HEAD` commit-carrier STOP gate + PR `## Memory` check), making P2's verify prose execute. Must name the same new version string as Task 4a.
- Module: loom-code/CHANGELOG.md
- Files touched: loom-code/CHANGELOG.md
- Context paths:
  - loom-code/CHANGELOG.md (existing entry format / latest heading)
- Acceptance:
  - RED: `grep '<new-version>' loom-code/CHANGELOG.md` → no match.
  - GREEN: a dated entry for the new version names the F4 verify gate; the new version string + a `--verify` mention grep-present.
- Dependencies: Tasks 1, 2, 3 complete first.
- Independent: true
- Brief item covered: "loom-code version bump + CHANGELOG."
