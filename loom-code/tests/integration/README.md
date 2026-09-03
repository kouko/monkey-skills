# Integration tests — cross-plugin behaviors

> **Phase**: v0.4.0-draft Phase 4 build. Tests verify loom-code's cross-plugin contracts hold when other plugins (loom-workflow, domain-teams:code-team, obra/superpowers) are installed alongside.

## Test surface

| Script | What it tests | Prereqs (auto-detected) |
|---|---|---|
| `test-git-memory-delegation.sh` | `ship` SKILL.md invokes `loom-workflow:git-memory` and names both memory carriers (commit trailer + PR body footer) | loom-workflow plugin installed |
| `test-code-team-coexistence.sh` | loom-code + domain-teams:code-team coexist — both installable, no skill-name collision with the five stations | domain-teams plugin installed |
| `test-superpowers-mode-on.sh` | Default mode (LOOM_CODE_MODE unset or =on) → both plugins fire | obra/superpowers (optional; some checks offline-only) |
| `test-superpowers-mode-off.sh` | LOOM_CODE_MODE=off escape hatch → loom-code hook silenced; superpowers fires alone | obra/superpowers (optional) |

## How to run

All scripts gracefully skip when their prerequisites are missing — safe to run in CI without pre-installing every plugin.

```bash
cd /path/to/monkey-skills/.worktrees/loom-code-design

# Run individual test:
bash loom-code/tests/integration/test-git-memory-delegation.sh

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
| git-memory delegation | ship/SKILL.md names git-memory, `memory-grep.sh --verify`, and both PR carriers; loom-workflow installed | Live: "ship it" → the memory step dispatches git-memory before push |
| code-team coexistence | No skill-name collisions; both plugins discoverable | Live: hybrid prompt invoking both plugins in same session without conflict |
| superpowers ON | Hook emits >1000 char context when var unset or =on; superpowers installation check | Live: both plugins' SessionStart hooks fire; skill lists discoverable |
| superpowers OFF | Hook emits valid JSON with EMPTY context when LOOM_CODE_MODE=off; hookEventName + 3 portable keys still present; sanity check unset mode | Live: LOOM_CODE_MODE=off → only superpowers active; unset → both active |

## Scope note (loom-code 1.0)

These four are the cross-plugin contracts that survived the station
redesign. `test-complexity-critique-delegation.sh`,
`test-command-surface-*.sh` and `test-rule-sheet-drift.sh` were deleted with
their subjects (the brainstorming skill, the command surface, the reviewer
rule sheet). They are local-only: none of them runs in CI, because each
reads the installed CLI's plugin state.
