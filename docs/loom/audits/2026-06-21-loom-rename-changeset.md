# loom- suite rename — dry-run changeset (read-only audit)

> Status: **PLANNED, not executed.** This is the grounded blast-radius
> inventory + plan for renaming the 4 "design→code pipeline" plugins to the
> `loom-` prefix. Decision origin: PR #421 (`ddef05eb`, 2026-06-19) shipped the
> `loom-pipeline` keyword tag and deferred the full rename to "its own scoped,
> test-gated PR". This doc is that PR's pre-flight.

## Locked decisions (2026-06-21)

| # | Decision | Value |
|---|---|---|
| Naming | Option C — `loom-` prefix, drop redundant `-toolkit` | mapping below |
| env var | rename | `CODE_TOOLKIT_MODE` → `LOOM_CODE_MODE` |
| Phasing | one atomic PR (git worktree) | avoids half-renamed cross-refs |
| Back-compat | hard-cut, no alias | CHANGELOG marks **BREAKING** |
| Router skills | rename for consistency | `using-code-toolkit`→`using-loom-code`, `using-interface-design-toolkit`→`using-loom-interface-design` |

### Name mapping
```
product-principles-toolkit  -> loom-product-principles
interface-design-toolkit    -> loom-interface-design
spec-toolkit                -> loom-spec
code-toolkit                -> loom-code
```

## Cost / value note
Large, mostly-cosmetic. The `loom-pipeline` *keyword* (#421) already groups the
4 in the marketplace; this rename only buys a visible "one suite" identity in
the plugin **names**. Cost is dominated by `loom-code`. Worth keeping the slice
tight; the keyword tag is the functional grouping that already shipped.

---

## P1 — Dirs + manifests (~11 edits)
- `git mv` ×4 per the mapping above.
- 4× `<plugin>/.claude-plugin/plugin.json` — `name` field.
- `.claude-plugin/marketplace.json` — 4 entries: `name` + `source` (`./loom-code/`, `./loom-spec/`, `./loom-interface-design/`, `./loom-product-principles/`).
- `code-toolkit/.codex-plugin/plugin.json` — `name`, then `scripts/sync_codex_manifest.py` + `--check`.
- Descriptions UNCHANGED → `check-marketplace-description-sync.py` stays green.

## P2 — loom-code internals (operative)

### `code-toolkit:` colon-IDs (20 files)
```
10  code-toolkit/TECH-SPEC.md
 6  code-toolkit/skills/using-code-toolkit/references/claude-code-tools.md
 5  code-toolkit/skills/subagent-driven-development/SKILL.md
 5  code-toolkit/skills/dispatching-parallel-agents/SKILL.md
 5  code-toolkit/ROADMAP.md
 4  code-toolkit/PRODUCT-SPEC.md
 2  code-toolkit/skills/requesting-code-review/SKILL.md
 1  code-toolkit/skills/using-code-toolkit/references/engineering-baselines.md
 1  code-toolkit/skills/using-code-toolkit/references/codex-tools.md
 1  code-toolkit/README.md / README.ja.md / README.zh-TW.md
 1  code-toolkit/agents/{implementer,spec-reviewer,code-quality-reviewer,code-reviewer}.md
 1  code-toolkit/tests/integration/test-{superpowers-mode-on,git-memory-delegation,complexity-critique-delegation,code-team-coexistence}.sh
```

### `CODE_TOOLKIT_MODE` → `LOOM_CODE_MODE` (15 files, ~50 occ)
```
16  code-toolkit/tests/integration/test-superpowers-mode-off.sh
10  code-toolkit/tests/integration/test-superpowers-mode-on.sh
 5  code-toolkit/tests/integration/README.md
 3  code-toolkit/TECH-SPEC.md
 3  code-toolkit/ROADMAP.md
 2  code-toolkit/skills/using-code-toolkit/README.{md,ja,zh-TW}
 2  code-toolkit/hooks/session-start
 1  code-toolkit/skills/using-code-toolkit/SKILL.md
 1  code-toolkit/README.{md,ja,zh-TW}
 1  code-toolkit/docs/announcement/v1.0.0-announcement.md
 1  code-toolkit/.codex-plugin/plugin.json
```

### Special surfaces
- Router skill folder: `code-toolkit/skills/using-code-toolkit` → `using-loom-code` (dir + `name`).
- Hooks: `code-toolkit/hooks/{hooks.json, session-start}` — plugin name + env var.
- CI: `.github/workflows/code-toolkit-ci.yml` → `loom-code-ci.yml` (12 path refs + `paths:` trigger filter + job names).
- subagent_type: the 4 agents are addressed `loom-code:<agent>` post-rename — every dispatch site (TECH-SPEC, ROADMAP, the 4 agents/*.md, dispatching-parallel-agents, using-* refs, requesting-code-review, SDD) must update.

## P3 — cross-plugin consumers

### dev-workflow `distill-sessions` (19 files — stays in dev-workflow, repoint refs)
Bulk is test fixtures/assertions:
```
37  scripts/test_aggregate.py      26  scripts/test_main.py    10  scripts/test_main_e2e.py
 8  SKILL.md     6  README.{md,ja,zh-TW}    4  scripts/main.py    3  scripts/aggregate.py
 2  scripts/test_friction_signals.py   2  agents/prompt-failure-analysis.md
 1× test-prompts.json, test_propose.py, test_prompts_parseable.py, test_ingest.py,
    friction_signals.py, fixture_sample.jsonl, fixture_report_merged.json,
    agents/prompt-success-analysis.md
```

### research-toolkit (4 files → `loom-code:`)
`skills/{deep-deep-research, fact-check, deep-read, cite-check}/SKILL.md`

### loom-spec (was spec-toolkit, 7 files — own `spec-toolkit:` + `code-toolkit:`)
```
3  skills/spec-expansion/SKILL.md     2  examples/subscription-pause/proposal.md
2  examples/AB-SUMMARY.md             1  skills/completeness-critic/SKILL.md
1  README.md   1  examples/stock-reservation/proposal.md   1  examples/password-reset/A-B-delta.md
```

### loom-product-principles
`README.md` (1)

### loom-interface-design
- Router rename `using-interface-design-toolkit` → `using-loom-interface-design`.
- **OPEN VERIFY**: operative grep returned 0 but 7 `interface-design-toolkit:` refs exist repo-wide — locate at execution time (likely the router SKILL.md + frozen docs). Does not change the magnitude.

## P4 — Frozen (keep old IDs — do NOT touch)
**46 files** under `docs/**/{plans,specs,audits,dogfood}`, CHANGELOGs, `/adr/`, `research/`.
⚠️ Lesson from the skill-dev-toolkit extraction: operative `*-SPEC.md` / `ROADMAP.md` / `README*` / `ATTRIBUTION.md` are NOT frozen — they DO get repointed.

## P5 — Live-load smoke test (#421's explicit gate)
Install/enable the renamed plugins, then verify:
1. skills load under the new names;
2. SessionStart hook still injects the loom-code router banner;
3. `LOOM_CODE_MODE=off` disables injection;
4. a dispatch resolves: `loom-code:tdd-iron-law` + `subagent_type: loom-code:code-reviewer`.

## P6 — Gates + review
- `check-marketplace-description-sync.py` · `check-plugin-description-skill-coherence.py` · `sync_codex_manifest.py --check` · `check-skill-structure.py` · conventional commits.
- **Grep-guard:** `0` operative `code-toolkit:|spec-toolkit:|interface-design-toolkit:|product-principles-toolkit:` outside the 46 frozen files; `0` `CODE_TOOLKIT_MODE` operative.
- Fresh dispatched whole-branch review — focus cross-task-coherence (no half-renamed refs).
- CHANGELOGs for all 4 + dev-workflow, marked **BREAKING**.

## Magnitude
| Block | operative files |
|---|---|
| P1 dirs+manifest | ~11 |
| P2 loom-code (incl env var / CI / hook / agents / router) | ~38 |
| P3 distill-sessions | 19 |
| P3 research + loom-spec + principles + interface | ~13 |
| **operative total** | **~80** |
| P4 frozen (untouched) | 46 |

Heaviest: `loom-code` itself + distill-sessions test files (`test_aggregate.py`/`test_main.py` ≈ 63 occ, mostly fixture strings).

## Execution notes
- Do it in a **git worktree** (big mechanical diff; isolate).
- Scripted, operative/frozen-aware sed (like the 2026-06-21 tagline sweep), `git mv` for dirs.
- The Bash hook blocks `git push` + `--base main` in one command — run push and `gh pr create` as separate calls.
