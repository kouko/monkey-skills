# loom-code tests

Two prompt clusters cover the Phase 1 acceptance criteria from [`../ROADMAP.md`](../ROADMAP.md) §Phase 1:

| Cluster | What it verifies | ROADMAP goal |
|---|---|---|
| [`skill-triggering/prompts/`](skill-triggering/prompts/) | SessionStart hook injects router; router auto-routes coding tasks (and **does not** over-trigger on read-only questions); legitimate user override (`explicit-skip.txt`) is honored after explicit re-confirmation. | G2, G4, plus router negative case (§When NOT to use). |
| [`tdd-iron-law-pressure/prompts/`](tdd-iron-law-pressure/prompts/) | Iron Law refuses 5 distinct rationalizations for skipping TDD, citing Beck (2002) Preface (or Martin Clean Code Ch.9 / 和田訳 2017) on each refusal. | G3 ("5 / 5 induction prompts rejected with Beck 2002 citation"). |

## Running (Phase 1 — manual)

Each `.txt` file is **a single user prompt**, copy-pastable into a fresh session. Run mode:

```
1. Install loom-code in your host (Claude Code or Codex CLI).
2. Open a fresh session — important: SessionStart hook fires at session start,
   and earlier prompts in the same session can poison subsequent ones (a
   prior "skip TDD" framing can prime the agent to skip again).
3. Paste the .txt content as the first user message.
4. Eyeball the agent's first reply against the table in the cluster's
   prompts/index.md.
5. PASS if all MUST rules in the table are satisfied.
```

## Phase 1 acceptance threshold

| Cluster | PASS threshold |
|---|---|
| `skill-triggering/` | 5 / 5 PASS |
| `tdd-iron-law-pressure/` | 5 / 5 PASS (every refusal cites a primary source) |

## Future automation (Phase 1.5+)

Phase 1 verification is manual. Phase 1.5 may add an automated harness — likely mirroring Superpowers' `tests/skill-triggering/run-all.sh` — that:

- Spawns a fresh CLI session per prompt (host-dependent: Claude Code uses `claude --no-history`-style flag; Codex uses its own).
- Captures the first agent reply.
- Greps the reply against the `MUST` rules in each cluster's `index.md`.
- Emits a tabular pass / fail report.

Until then, treat the `index.md` tables as the human-runnable test harness. If a prompt fails, file the failure mode under [`../research/`](../research/) as a dogfood note — the rationalization that broke through is the next iteration's pressure test.

## Adding new prompts

When adding a new prompt to either cluster:

1. Create the `.txt` (pure prompt body, one user message).
2. Add a row to the cluster's `prompts/index.md` with the assertion table.
3. Note the ROADMAP goal it covers (G1-G6 in PRODUCT-SPEC §3.1).

When a real-world session reveals a rationalization the current prompts do not cover, that is the cue to add a new prompt — see CLAUDE.md `feedback` memory type for the broader pattern.

## See also

- [`../PRODUCT-SPEC.md`](../PRODUCT-SPEC.md) §3.1 — Goals.
- [`../ROADMAP.md`](../ROADMAP.md) §Phase 1 — Acceptance test list.
- [`../TECH-SPEC.md`](../TECH-SPEC.md) §6 — Testing strategy.
- [`../skills/tdd-iron-law/SKILL.md`](../skills/tdd-iron-law/SKILL.md) §When NOT to Use + §Red Flags — the rules these prompts pressure.
- [`../skills/using-loom-code/SKILL.md`](../skills/using-loom-code/SKILL.md) §Skill priority + §Red Flags — the routing the prompts test.
