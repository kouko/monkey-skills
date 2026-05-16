# Worked examples — code-toolkit end-to-end flows

> Three worked examples covering the full code-toolkit flow from `using-code-toolkit` SessionStart hook injection through to `finishing-a-development-branch` close-out. Each example exercises a different combination of skills + stack, so reading all three covers the toolkit's behavioral surface.

## Index

| Example | Stack | What it shows | Skills exercised |
|---|---|---|---|
| [`python-csv-export.md`](python-csv-export.md) | Python + FastAPI + pytest | Clean 3-task flow; all-PASS execution; data-analyst persona | Full flow; no exception paths |
| [`typescript-react-toast.md`](typescript-react-toast.md) | React + TypeScript + Vitest | Multi-module case; SDD child-test fallback (Beck Part II) when Task 3 returns BLOCKED | Full flow + `writing-plans` BLOCKED re-invocation; PASS_WITH_NOTES verdict |
| [`swift-network-layer.md`](swift-network-layer.md) | Swift + URLSession + XCTest | Legacy refactor with Feathers (2004) characterization tests; `systematic-debugging` 4-phase flow on a CI race condition | Full flow + `tdd-iron-law` §Legitimate legacy-code backfill + `systematic-debugging` REPRODUCE/ISOLATE/HYPOTHESIZE/VERIFY |

## Reading order

For first-time readers:
1. **`python-csv-export.md`** first — clean baseline; shows the happy path with no exception handling
2. **`typescript-react-toast.md`** second — adds the child-test fallback mechanism + PASS_WITH_NOTES verdict shape
3. **`swift-network-layer.md`** last — adds two more exception paths: legacy backfill + systematic-debugging

For readers focused on a specific area:
- Want the flow but in your language? Pick the closest of the 3 stacks and adapt
- Want to understand BLOCKED handling? Read TypeScript example §"Task 3 implementer BLOCKED"
- Want to understand legacy vs Iron Law violation? Read Swift example §"Distinction between Feathers backfill vs Iron Law violation"
- Want to understand `systematic-debugging` end-to-end? Read Swift example §"Stage 5 — systematic-debugging"

## What's deliberately NOT in these examples

- **Real coding output** — these are *worked examples* showing the toolkit's flow, not literal copy-paste-ready implementations. The Python `render_csv` function is real Python; the Swift Concurrency wrapper is real Swift. But the specific business logic is illustrative.
- **Codex CLI commands** — examples show Claude Code's tool surface (`Skill(...)`, `Bash(...)`, etc.). The same flow works on Codex CLI via `/skill-name` slash commands per [`../../skills/using-code-toolkit/references/codex-tools.md`](../../skills/using-code-toolkit/references/codex-tools.md).
- **Full transcripts** — each Stage shows the load-bearing artifacts (the brief, the plan, the test output) without 50-page interleaved chat. The actual session has more turns; the examples extract the durable outputs.

## See also

- [`../../README.md`](../../README.md) — top-level toolkit overview
- [`../../skills/using-code-toolkit/SKILL.md`](../../skills/using-code-toolkit/SKILL.md) — router charter (Stage 0 always-on)
- [`../../PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) — design intent + Q-lock decisions
- [`../../ROADMAP.md`](../../ROADMAP.md) — phase plan + decision ledger
