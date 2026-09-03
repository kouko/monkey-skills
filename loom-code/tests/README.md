# loom-code tests

| Directory | What it holds |
|---|---|
| [`integration/`](integration/) | Cross-plugin behaviour scripts — loom-code beside `domain-teams:code-team`, `loom-workflow:git-memory`, and obra/superpowers. Each skips gracefully when its other plugin is absent. |

The pre-1.0 prompt clusters (`skill-triggering/`, the `*-pressure/`
directories, `codex-cli/`) were manual eyeball rituals over skills that no
longer exist. Their successor is the cold-read dogfood registered in
`docs/loom/evidence/mechanisms.yaml`: a fresh agent is handed one station's
SKILL.md and one real task, and the result is recorded as an eval rather
than read once and thrown away.

## Running

```bash
bash loom-code/tests/integration/test-code-team-coexistence.sh
```

All of them are local-only: they read the installed CLI's plugin state, so
a runner without `claude` reports SKIP rather than PASS.
