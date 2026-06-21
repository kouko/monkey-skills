# Integration tests — cross-plugin behaviors

> **Phase**: v0.4.0-draft Phase 4 build. Tests verify loom-code's cross-plugin contracts hold when other plugins (dev-workflow, domain-teams:code-team, obra/superpowers) are installed alongside.

## Test surface

| Script | What it tests | Prereqs (auto-detected) |
|---|---|---|
| `test-complexity-critique-delegation.sh` | `brainstorming` SKILL.md references `dev-workflow:complexity-critique` as Axis 3 delegate; both plugins installed | dev-workflow plugin installed |
| `test-git-memory-delegation.sh` | `finishing-a-development-branch` SKILL.md invokes `dev-workflow:git-memory` at Step 3 per P3-D MANDATORY | dev-workflow plugin installed |
| `test-code-team-coexistence.sh` | loom-code + domain-teams:code-team coexist (no skill collisions; SSOT-and-functional-copy intact; coexistence framing in SKILL.md) | domain-teams plugin installed; verify-drift.py works |
| `test-superpowers-mode-on.sh` | Default mode (LOOM_CODE_MODE unset or =on) → both plugins fire | obra/superpowers (optional; some checks offline-only) |
| `test-superpowers-mode-off.sh` | LOOM_CODE_MODE=off escape hatch → loom-code hook silenced; superpowers fires alone | obra/superpowers (optional) |

## How to run

All scripts gracefully skip when their prerequisites are missing — safe to run in CI without pre-installing every plugin.

```bash
cd /path/to/monkey-skills/.worktrees/loom-code-design

# Run individual test:
bash loom-code/tests/integration/test-complexity-critique-delegation.sh

# Run all integration tests:
for t in loom-code/tests/integration/test-*.sh; do
  echo ""
  echo "=== ${t} ==="
  bash "${t}"
done
```

## Output shape

Each script prints:
1. Per-check `PASS / FAIL / SKIP` lines
2. Summary count (e.g. `5 PASS / 0 FAIL / 1 SKIP`)
3. If all offline checks PASS: manual verification handoff (copy-paste prompt + expected agent behavior)
4. If any FAIL: exits 1 (script-level) with diagnostic

The **manual verification handoff** is the actual integration test — offline checks just ensure the structural prerequisites are met before you spend session time on the live test.

## What's tested offline vs manual

| Test | Offline scope | Manual scope |
|---|---|---|
| complexity-critique delegation | SKILL.md reference; dev-workflow installed; complexity-critique exists | Live: PAGNI prompt → agent invokes complexity-critique |
| git-memory delegation | SKILL.md reference + P3-D MANDATORY framing; Step 3 names git-memory; dev-workflow installed | Live: "finish this branch" → Step 3 dispatches git-memory before commit |
| code-team coexistence | No skill-name collisions; verify-drift PASS; both plugins discoverable; coexistence framing in router | Live: hybrid prompt invoking both plugins in same session without conflict |
| superpowers ON | Hook emits >1000 char context when var unset or =on; superpowers installation check | Live: both plugins' SessionStart hooks fire; skill lists discoverable |
| superpowers OFF | Hook emits valid JSON with EMPTY context when LOOM_CODE_MODE=off; hookEventName + 3 portable keys still present; sanity check unset mode | Live: LOOM_CODE_MODE=off → only superpowers active; unset → both active |

## Where these tests fit in the Phase plan

- **Phase 4 GA acceptance** per ROADMAP §Phase 4:
  - 與 Superpowers 並存（LOOM_CODE_MODE=on）測試通過 ← `test-superpowers-mode-on.sh`
  - 與 Superpowers 並存（LOOM_CODE_MODE=off）測試通過 ← `test-superpowers-mode-off.sh`
  - 三個 cross-plugin delegation（git-memory / complexity-critique / code-team）全綠 ← `test-git-memory-delegation.sh` + `test-complexity-critique-delegation.sh` + `test-code-team-coexistence.sh`

When all 5 PASS (offline + manual), Phase 4 GA acceptance criteria are met.

## Related test surfaces

- `loom-code/tests/skill-triggering/` — per-skill auto-fire pressure prompts (Phase 1 ship)
- `loom-code/tests/tdd-iron-law-pressure/` — Iron Law refusal pressure prompts (Phase 1 ship)
- `loom-code/tests/brainstorming-pressure/` — HARD-GATE refusal pressure prompts (Phase 2 ship)
- `loom-code/tests/writing-plans-pressure/` — splitting framework + plan-doc-reviewer (Phase 2 ship)
- `loom-code/tests/systematic-debugging-pressure/` — 4-phase HARD-GATE pressure prompts (Phase 2 ship)
- `loom-code/tests/requesting-code-review-pressure/` — push-as-trigger + skip-review refusal (Phase 3 ship)
- `loom-code/tests/verification-before-completion-pressure/` — package-level-test HARD-GATE (Phase 3 ship)
- `loom-code/tests/using-git-worktrees-pressure/` — stash-and-clone alternative refusal (Phase 3 ship)
- `loom-code/tests/finishing-a-development-branch-pressure/` — orchestrator skip-step refusal (Phase 3 ship)
- `loom-code/tests/codex-cli/` — Codex CLI install + hook injection (Phase 2.5 ship)
- `loom-code/tests/integration/` — **this dir** (Phase 4 build)

## See also

- [`../../../loom-code/PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) §4.3 + §5.6 — coexistence contracts
- [`../../../loom-code/ROADMAP.md`](../../ROADMAP.md) §Phase 4 — GA acceptance criteria
- [`../../../loom-code/skills/finishing-a-development-branch/SKILL.md`](../../skills/finishing-a-development-branch/SKILL.md) — P3-D MANDATORY git-memory invocation
