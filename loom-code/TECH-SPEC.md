# loom-code — technical spec

Superseded at 1.0.0. The module design is small enough to read directly.

- `contract/manifest.yaml` — stations, actions, artifact fields;
  `contract/README.md` says who may read and write it
- `scripts/loom_checker.py` — one entry point: `intent`, `intake`, `push`,
  `standing`, `contract`, `--list-rules`
- `scripts/codex_scaffold.py` — the repo-local checker copy for Codex CLI
- `scripts/check_mechanisms.py` — recomputes the mechanism population
- `hooks/hooks.json` — SessionStart and the PreToolUse push matchers
- `agents/*.md` — implementer, reviewer, blind-runner, adversary

The pre-1.0 tech spec described the knowledge-SSOT distribution, the
review-batch pipeline and the living-spec index — all three deleted.
