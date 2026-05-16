# Changelog

All notable changes to the `code-toolkit` plugin will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

## [0.1.0] — 2026-05-16

First ship — Phase 1 MVP shell. Three skills + SessionStart hook + cross-plugin SSOT pipeline.

### Added — process layer (3 skills)

- **`using-code-toolkit`** — router skill, auto-injected by SessionStart hook. ~1853 tokens (under the 2000-token P1-A budget). Sections: `<SUBAGENT-STOP>` escape hatch, `<EXTREMELY-IMPORTANT>` 3-rule charter (brainstorm-before-implement, TDD iron law, SDD for >1-hour or >1-module work), Instruction Priority, How to Access Skills (Claude Code `Skill` tool / Codex CLI `skill` tool), Skill Priority decision table (8 stages mapped to v0.1.0 / Phase 2 / Phase 3 status), Red Flags rationalization table (en + ja + zh-TW localized triggers), Skill Types (Rigid / Flexible), Coexistence contract.
- **`tdd-iron-law`** — discipline skill. **"NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST."** Verbatim Beck (2002, ISBN 978-0321146533) Preface citation; full Three Laws of TDD from Martin (2008, ISBN 978-0132350884) Ch.9; Japanese anchor 和田卓人 訳 (2017, ISBN 978-4274217883). Iron Law remediation = *"Delete the code. Write the test. Start over."* (Superpowers measure preserved per Q-lock Q7). §When NOT to Use: 4 enumerated exemption rows (throwaway / generated / trivial-delegation / pure-config) + explicit-override row with confirmation requirement. §Red Flags: 8 rationalizations (en + ja + zh-TW) with primary-source rebuttals. §False-green diagnostic: comment-out / re-run drill. Ships with `references/testing-anti-patterns.md` indexing 8 anti-patterns to primary-source rebuttals.
- **`subagent-driven-development`** — workflow orchestrator. Triggers when task >1 hour OR >1 module. Per-task triad: implementer (worker, under TDD iron law) + spec-reviewer (evaluator, binary `PASS` / `NEEDS_REVISION`) + code-quality-reviewer (evaluator, three-valued `PASS` / `PASS_WITH_NOTES` / `NEEDS_REVISION`). Verdict resolution rule + 3-round retry cap. Model-selection table (mechanical → cheap / integration → standard / architecture → most capable). Continuous execution rule. Three subagent prompts under `agents/` with explicit input + output contracts (paths-not-content delegation per CLAUDE.md).

### Added — knowledge layer (12 functional copies)

Byte-identical copies of `domain-teams:code-team` standards / rubrics / checklists, each prefixed by a 5-line HTML comment SSOT header (P1-D). Pinned to **code-team SHA `916a165` (2026-04-29)** at v0.1.0 ship.

- `tdd-iron-law/standards/tdd-standard.md`
- `subagent-driven-development/standards/{tdd-standard, naming-and-functions, pragmatic-principles, solid-principles, refactoring-standard, app-security-standard, character-encoding-security}.md`
- `subagent-driven-development/rubrics/{quality-gate, arch-gate}.md`
- `subagent-driven-development/checklists/{security-checklist, spec-consistency}.md`

### Added — hooks

- `hooks/hooks.json` — registers SessionStart on `startup | clear | compact` matchers.
- `hooks/session-start` — bash; reads `using-code-toolkit/SKILL.md`, JSON-escapes via parameter substitution, emits **three** keys for portability across Claude Code (`hookSpecificOutput.additionalContext`), Codex CLI (`additional_context`), and any mixed-shape host (`additionalContext`). Fail-open if SKILL.md missing. Escape hatch wired up: `export CODE_TOOLKIT_MODE=off` returns empty-context JSON for users who already have `obra/superpowers` installed.

### Added — SSOT-and-functional-copy pipeline

- `scripts/distribute.py` — pure stdlib (P1-E). Reads from sibling-plugin `../domain-teams/skills/code-team/{standards,rubrics,checklists}/`, writes to `code-toolkit/skills/*/{standards,rubrics,checklists}/` with the SSOT header prepended. ROUTE table has 12 entries.
- `scripts/verify-drift.py` — pure stdlib. Regenerates expected payload `(SSOT header) + (canonical bytes)` and byte-diffs against the on-disk copy. On drift: md5 fingerprints + ≤50-line unified diff. Both positive (12 / 12 match) and negative (corrupted-copy detection) paths smoke-tested at v0.1.0 ship.
- `scripts/canonical/README.md` — SSOT pointer table + drift policy doc (no code in this dir; canonical lives in `domain-teams:code-team`).

### Added — manifests + 3-lang docs

- `.claude-plugin/plugin.json` — Claude Code manifest, version `0.1.0-draft` (drop the `-draft` suffix when live install is verified in a fresh session).
- `.codex-plugin/plugin.json` — Codex CLI manifest skeleton (P1-F: not shipped this phase; v0.2.5 ship target).
- `README.{md,ja.md,zh-TW.md}` — plugin-root 3-lang.
- `skills/{using-code-toolkit,tdd-iron-law,subagent-driven-development}/README.{md,ja.md,zh-TW.md}` — per-skill 3-lang × 3 skills = 9 files.

### Added — manual test harness

- `tests/skill-triggering/prompts/{new-feature,bug-fix,refactor,pure-question,explicit-skip}.txt` + `index.md` — 5 prompts that test SessionStart routing (positive + negative + legitimate-override cases). Mirrors Superpowers `tests/skill-triggering/` convention.
- `tests/tdd-iron-law-pressure/prompts/{skip-just-this-once,prototype-exception,i-already-wrote-it,tests-are-slow,small-change}.txt` + `index.md` — 5 prompts that pressure the Iron Law with 5 distinct rationalizations. Acceptance: 5 / 5 refused with primary-source citation.
- `tests/README.md` — manual-run convention for Phase 1; Phase 1.5+ may add an automated harness.

### Added — design + grounding documents

- `PRODUCT-SPEC.md` — business / target user / Q-lock × 8.
- `TECH-SPEC.md` — architecture / SSOT / hooks / interface contracts.
- `ROADMAP.md` — Phase 0–4 plan + Decision Ledger.
- `research/grounding-v0.1.0.md` — per-version grounding rationale: §1 inherits 11 primary sources from code-team v5.6.0 canon (with full ISBN / URL citations); §2 enumerates 7 process-layer authoritative claims original to this toolkit (each tagged to a Q-lock); §3 lists explicit non-claims (deferred to Phase 2 / 3); §4 drift policy summary; §5 re-runnable audit commands; §6 version-log rule.

### Added — marketplace registration

- `code-toolkit` entry added to root `.claude-plugin/marketplace.json` after `legal-toolkit`. Description byte-identical to `code-toolkit/.claude-plugin/plugin.json` per `scripts/check-marketplace-description-sync.py` gate (16 / 16 plugins in sync).

### Q-lock at v0.1.0 (PRODUCT-SPEC §8)

Eight design decisions locked at Phase 0 (2026-05-15) and **deliberately not revisited** during Phase 1 build:

1. **Q1** Harness = Claude Code + Codex CLI (Codex full ship deferred to Phase 2.5).
2. **Q2** `domain-teams:code-team` is **kept**, not deprecated — it is the passive-gate entry; `code-toolkit` is the active-construction entry.
3. **Q3** Design docs first (PRODUCT-SPEC + TECH-SPEC + ROADMAP) before any skill build.
4. **Q4** Worktree `feat/code-toolkit-design` for isolation.
5. **Q5** Knowledge-layer SSOT lives in `domain-teams:code-team/`; this plugin holds byte-identical functional copies.
6. **Q6** Skill naming follows `obra/superpowers` (`using-*`, `subagent-driven-development`, etc.).
7. **Q7** TDD measure preserves Superpowers' "Delete it. Start over." rhetoric AND adds Beck (2002) Preface ISBN-cited grounding (double anchor: behavior layer + canon layer).
8. **Q8** Subagent triad = three roles (implementer / spec-reviewer / code-quality-reviewer); spec-reviewer scope is binary, code-quality-reviewer scope is six-dimensional.

Phase 1 sub-decisions (P1-A through P1-F, ROADMAP §Phase 1 Q-lock): all observed at v0.1.0 ship — router under 2000-token budget; Beck 2002 Preface ISBN-quoted in `tdd-iron-law/SKILL.md`; subagent prompts as `.md` not `.txt`; functional copies carry HTML comment SSOT header; scripts pure-stdlib (no PEP 723); Codex CLI manifest is skeleton-only.

### Coexistence + escape hatches

- **`domain-teams:code-team`** — coexists. No file conflict (different plugin paths). `dev-workflow:complexity-critique`'s SSOT pointer to code-team's mindset functional copy is **unchanged**.
- **`dev-workflow:{git-memory, complexity-critique, proposal-critique}`** — `code-toolkit` delegates to these at the right moments (per Phase 3 cross-plugin contract); does not duplicate their logic.
- **`obra/superpowers`** — known conflict on dual SessionStart hook + overlapping skill names (`brainstorming`, `writing-plans`, `subagent-driven-development`, `using-git-worktrees`). Resolution shipped: `export CODE_TOOLKIT_MODE=off` in shell rc disables this plugin's hook injection. Cleanly disables; tested with both positive and negative env-var cases.

### Known gaps + verification still owed

- **Live install verification still pending.** `0.1.0-draft` suffix in plugin.json + .codex-plugin/plugin.json marks this. To ship as `0.1.0` proper:
  1. Install plugin in a fresh Claude Code session.
  2. Confirm SessionStart hook fires (router auto-loads).
  3. Run at least one prompt from each of `tests/skill-triggering/` and `tests/tdd-iron-law-pressure/`; eyeball assertions per cluster `index.md`.
  4. Drop `-draft` from both manifest version fields; commit.
- **Phase 1.5 follow-ups**: `--soft-mode` flag implementation (OQ-1), 5 dogfood-session notes (`research/dogfood-2026-05-XX.md`).
- **Phase 2** (estimated 6-8 days): `brainstorming` + `writing-plans` + `systematic-debugging` skills.
- **Phase 2.5** (estimated 3-4 days): Codex CLI variant ship + integration tests.
- **Phase 3** (estimated 6-8 days): code-review cluster (`requesting-code-review`, `verification-before-completion`, `using-git-worktrees`, `finishing-a-development-branch`) for Superpowers parity.
- **Phase 4** (estimated 3-4 days): GA — cross-plugin delegation hardening + release.

### Files in v0.1.0 ship

```
code-toolkit/
├── .claude-plugin/plugin.json                  (manifest, draft)
├── .codex-plugin/plugin.json                   (manifest skeleton, draft)
├── PRODUCT-SPEC.md / TECH-SPEC.md / ROADMAP.md (Phase 0 design docs)
├── README.{md,ja.md,zh-TW.md}                  (plugin root, 3-lang)
├── CHANGELOG.md                                (this file)
├── hooks/{hooks.json,session-start}            (SessionStart injection)
├── scripts/{distribute.py,verify-drift.py,canonical/README.md}  (SSOT pipeline)
├── docs/superpowers/specs/2026-05-15-design-lock-session.md     (Phase 0 handoff)
├── research/grounding-v0.1.0.md                (per-version grounding rationale)
├── skills/using-code-toolkit/{SKILL.md, README ×3, references/{claude-code-tools.md,codex-tools.md}}
├── skills/tdd-iron-law/{SKILL.md, README ×3, standards/tdd-standard.md, references/testing-anti-patterns.md}
├── skills/subagent-driven-development/{SKILL.md, README ×3, agents/{implementer,spec-reviewer,code-quality-reviewer}-prompt.md, standards/×7, rubrics/×2, checklists/×2}
└── tests/{README.md, skill-triggering/prompts/×5+index.md, tdd-iron-law-pressure/prompts/×5+index.md}
```

Plus: 1 root `.claude-plugin/marketplace.json` entry added (16th plugin in monkey-skills marketplace).
