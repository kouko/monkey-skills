# Brief — F4: executable both-carrier verify gate at branch close-out

Date: 2026-06-23 · Stage: brainstorming output → `writing-plans`
Target: `loom-code:finishing-a-development-branch` (the close-out orchestration) + a cross-ref touch in `dev-workflow:git-memory`
Source: `docs/skill-mining/2026-06-22-git-memory-findings.md` F4 + the #445 post-merge dogfood (`project_git_memory_p1p2_merge_gate_verified_survival.md`)
Carrier policy (user decision, 2026-06-23): **both carriers required** — commit-carrier (`git log --grep` on main) AND PR `## Memory`. Consistent with the P2 choice.

## Problem (Axis 1 — JTBD)

A memory-worthy branch can reach `gh pr merge` with its **commit carrier empty** — the decision recorded only in the PR `## Memory` (GitHub), not retrievable via `git log --grep` on `main`. Live proof: #445's own squash commit `fb62c234` → `memory-grep.sh --verify` exit 4. The job: **make "memory-worthy branch ⇒ memory is retrievable from BOTH carriers" an enforced, executable gate at close-out — not advisory prose the agent can skip.**

The generative half already exists and is NOT the gap: `finishing-a-development-branch` Phase 3/4 has git-memory return a trailer set and commits it, and `compose-commit.md` produces literal `Decision:`/`Learning:`/`Gotcha:` trailer lines (which concatenate into the squash body under `COMMIT_MESSAGES`, where `git log --grep` finds them). #445 failed only because the close-out flow was **skipped** (manual SDD→review→PR) and **nothing verified** the commit carrier landed.

## Users (Axis 2)

- The orchestrating agent at branch close (`finishing-a-development-branch`) — today can commit, push, and open a PR for a memory-worthy branch without ever confirming the memory is retrievable; there is no executable check, only the P2 prose in `compose-pr.md`/SKILL.md.
- A future dev/agent running `git log --grep='^Decision:'` on `main` to recall "why did we X?" — gets nothing when the commit carrier was silently empty.

## Smallest End State (Axis 3)

Wire an **executable both-carrier verify gate** into `finishing-a-development-branch`'s Default flow:

1. **Commit-carrier gate (post-commit, pre-push).** After the close-out commit (Step 9), run `dev-workflow/skills/git-memory/scripts/memory-grep.sh --verify HEAD`. If git-memory's Phase-3 trailer set was **non-empty** (the branch is memory-worthy) and `--verify` exits **4**, STOP and surface: "the close-out commit did not capture the memory trailers — fix before push." If Phase 3 returned empty (routine branch), exit 4 is expected → proceed.
2. **PR-carrier check (at PR creation, Step 11).** When opening the PR for a memory-worthy branch, confirm the PR body carries a `## Memory` section before declaring the PR ready (per the user's both-carrier policy). Absent → flag.
3. **Make the existing P2 prose point at this enforced gate** — `compose-pr.md` Step 7 and SKILL.md Pillar 2 currently *describe* the verify; cross-ref them to the now-executable gate in `finishing-a-development-branch` so the prose and the enforcement agree.
4. A **grep-style test** (mirroring `loom-code/tests/integration/test-git-memory-delegation.sh`) asserting `finishing-a-development-branch`'s flow contains the `--verify` commit-carrier gate + the PR `## Memory` check.
5. **loom-code** version bump + CHANGELOG (the gate lives in the loom-code `finishing-a-development-branch` skill, NOT dev-workflow).

This is **verification-class** scaffolding (Bitter-Lesson keep): it runs a check and surfaces a hard exit-4 signal, rather than adding a new generative mechanism (which already exists).

## Current State Evidence

- **Forward (flow today)**: `loom-code/skills/finishing-a-development-branch/SKILL.md` Default flow Steps 6–11 — Step 6 invokes git-memory (returns trailer set), Step 9 commits with trailers, Step 10 pushes, Step 11 opens PR. **No `--verify` step anywhere** — the close-out never confirms the commit carrier actually landed.
- **Reverse (SSOT/ownership)**: `finishing-a-development-branch` is a loom-code orchestration skill (prose contract, no synced SSOT). git-memory (incl. `--verify`) is dev-workflow; finishing already references `dev-workflow:git-memory` (Phase 3 P3-D), so calling its `--verify` script is consistent cross-plugin use, not new coupling. Neither skill is under a distribute/drift gate.
- **Error**: `memory-grep.sh --verify` exit codes 0 retrievable / 4 empty / 1 no-ref / 2 unresolvable (shipped #445, `dev-workflow/skills/git-memory/scripts/memory-grep.sh`). The gate keys on 0-vs-4.
- **Data (the generative half exists)**: `dev-workflow/skills/git-memory/protocols/compose-commit.md:33-77` produces literal `Decision:`/`Learning:`/`Gotcha:` trailer lines; finishing Phase 4 commits them → squash mid-body → `git log --grep` retrieves on main.
- **Boundary**: #445 squash commit `fb62c234` → `--verify` exit 4 (commit carrier empty), PR `## Memory` present (PR carrier ok). Repo squash setting `COMMIT_MESSAGES`. The gate would have flagged this branch at close-out **had finishing been run** — and the P1 merge-trigger (shipped #445) is the backstop for when it is skipped.
- **P2 prose already present (to cross-ref, not duplicate)**: `compose-pr.md` Step 7 + SKILL.md Pillar 2 describe the verify; F4 turns description into an executed step.

## Decision

Ship F4 as an **executable both-carrier verify gate in `finishing-a-development-branch`**: a post-commit `--verify HEAD` commit-carrier check (STOP on memory-worthy + exit 4) + a PR `## Memory` presence check at PR creation, with a grep-test and cross-refs from the P2 prose. **No new generative mechanism** (Phase 3/4 already authors trailers); **no repo-setting change**; the value is making P2's "verification required" actually execute and surface a hard exit-4 signal. loom-code version bump.

## Alternatives Considered (Axis 4)

- **(a) Executable verify gate in finishing-a-development-branch [CHOSEN]** — verification-class; reuses the shipped `--verify`; minimal; directly closes the #445 hole. Bitter-Lesson keep (checks ON the work, doesn't think FOR it).
- **(b) Generative: make git-memory auto-author trailers into a commit** — REJECTED. The machinery already exists (finishing Phase 3/4 + compose-commit.md). Adding auto-generation would be a crutch (Bitter-Lesson fragile) and duplicate working logic.
- **(c) Full native↔git reconciliation (cross-check Claude `MEMORY.md` ↔ PR `## Memory` ↔ commit carrier, flag any divergence)** — DEFER. Broader than the #445 hole; the executable carrier-gate (a) covers the concrete failure. Revisit if drift between the three stores recurs.
- No EN/JA industry search run: this is internal-to-our-toolkit orchestration policy (no external "shipped option" exists to research); the Bitter-Lesson framing is the relevant prior art and is already cited.

## What Becomes Obsolete (Axis 5)

Nothing removed. `compose-pr.md` Step 7 + SKILL.md Pillar 2's verify *prose* (shipped P2) stop being advisory-only — they become the documentation of an enforced gate, cross-referenced to the executable step in `finishing-a-development-branch`. A tightening, not a deletion.

## Out of Scope

- Auto-merge (finishing keeps user agency on the final merge — unchanged).
- Repo `squash_merge_commit_message` change (stays opt-in, prior spec's "user's call").
- Full native↔git reconciliation against Claude `MEMORY.md` (Axis-4 option c — deferred).
- Re-running / amending #445 itself (already merged; its decision lives in PR #445 `## Memory`; main-history rewrite is not worth it).
- Any change to the `--verify` script (shipped #445, sufficient as-is for the commit-carrier check).

## Open Questions

1. **Gate hardness**: STOP (block push) vs loud warning the agent must acknowledge, when a memory-worthy branch shows `--verify` exit 4. Lean **STOP** (consistent with finishing's other gates: 🔴 review / test-failure both STOP), surfaced per §Asking-the-user.
2. **loom-code version**: minor (new enforced gate step) vs patch. Lean **minor**.
3. **Does the PR-carrier check need tooling** or is "agent confirms `## Memory` is in the PR body it just composed" enough? Lean enough-as-prose (the agent authored the body; a grep on the body it's about to submit is trivial) — no new script.
