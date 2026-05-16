# Changelog

All notable changes to the `code-toolkit` plugin will be documented in this file.

Format: [Keep a Changelog](https://keepachangelog.com/).
Versioning: [Semantic Versioning](https://semver.org/).

## [Unreleased]

Phase 2 underway — Discovery + planning + repair cluster. Skills accumulate
under [Unreleased] until all 3 ship, then bump to [0.2.0].

### Added — `systematic-debugging` skill (3 of 3 Phase 2 skills) — closes Phase 2

Repair-cluster skill — the debugging analogue of `tdd-iron-law`. HARD-GATE
measure: NO FIXING WITHOUT REPRODUCING. 4-phase discipline (REPRODUCE →
ISOLATE → HYPOTHESIZE → VERIFY) with explicit gates between phases.

- `skills/systematic-debugging/SKILL.md` — HARD-GATE measure;
  4-phase framework with per-phase gates (🟢 reliable repro / 🟡
  bounded conditions / 🔴 cannot reproduce → not actionable yet);
  §When NOT to Use with 4 enumerated exemptions; Red Flags table
  covering 8 rationalizations × ja + zh-TW variants (random-patching,
  hypothesis-without-observation, "works on my machine," fishing-
  without-hypothesis logging, try/except masking, intermittent
  dismissal, symptom-as-root-cause); primary sources: Kernighan &
  Pike (1999) *The Practice of Programming* Ch.5 Debugging (ISBN
  978-0201615869) and Hunt & Thomas (2019) *Pragmatic Programmer*
  Topic 28 (ISBN 978-0135957059).
- `skills/systematic-debugging/references/root-cause-tracing.md` —
  Phase 2 ISOLATE sub-protocols. 6 bisection axes (git / dependency /
  input / component / time / 5-Whys) with trigger conditions, tools,
  and halving cost estimates. Anti-patterns enumerated.
- `skills/systematic-debugging/references/condition-based-waiting.md` —
  Phase 1 🟡 + Phase 2 time-axis bisection. Replaces `sleep(500)`
  anti-pattern with condition-polling; library helpers per language
  (TS / Python / Go / Java / Rust / shell); heisenbug bisection
  protocol (CPU / network / disk / GC axes).
- `skills/systematic-debugging/references/defense-in-depth.md` —
  Phase 4 post-VERIFY layering. 6-layer ladder (regression test →
  input validation → invariant assertion → type-system constraint →
  monitoring → architectural refactor) with proportionality rule
  (cost ≤ expected damage of next instance). 3 worked examples
  (typo / SQLi / race condition) showing layer selection by blast
  radius. The Rule-of-Three trigger for layer 6.
- `skills/systematic-debugging/references/character-encoding-debug.md`
  — **P2-C deliverable, new to code-toolkit.** Encoding-specific
  bisection (BOM detection / UTF-8 vs UTF-16 mismatch / NFC vs NFD
  normalization / surrogate pairs / stream decoder buffer boundary).
  Hex-dump bisection protocol. Cross-links to
  `domain-teams:code-team/standards/character-encoding-security.md`
  (徳丸本 第 2 版 Ch.6, ISBN 978-4797393163) for the security-
  grounded version. Worked example mirrors `tests/skill-triggering/
  prompts/bug-fix.txt` (UTF-8 BOM in CSV first column).
- `skills/systematic-debugging/README.{md,ja.md,zh-TW.md}` — 3-lang.

### Updated — `using-code-toolkit` router for systematic-debugging

- Skill Priority table row 5: Repair `systematic-debugging` flipped
  from "Phase 2" → "✅ shipped".
- Router stays under the 2000-token P1-A budget: ~1837 tokens.
- 3-lang README tables updated in lockstep.

### Added — systematic-debugging pressure tests

`tests/systematic-debugging-pressure/prompts/`:
- `just-try-fixes.txt` — canonical random-patching rationalization
  dressed in time pressure ("ship in next hour").
- `add-more-logging.txt` — fishing-without-hypothesis (1-in-50
  intermittent order drop; user wants `console.log` at every
  function entry/exit).
- `silence-with-try-except.txt` — error-masking with operational
  justification ("years without issue"; user wants to silent-skip
  2% of CSV uploads with UnicodeDecodeError). Tests both the
  masking refusal AND the character-encoding-debug invocation.
- `index.md` — assertion table per prompt; Phase 2 ritual
  acceptance is 3/3 refused with 4-phase engagement.

### Phase 2 closeout

This commit completes the Phase 2 skill triplet:
1. ✅ `brainstorming` — Discovery (Stage 1)
2. ✅ `writing-plans` — Planning (Stage 2)
3. ✅ `systematic-debugging` — Repair (Stage 5)

Stages 3-4 (Execution / Discipline) shipped in Phase 1
(`subagent-driven-development` / `tdd-iron-law`).

The plugin version stays `0.2.0-draft` until the user runs the
Phase 2 ritual for systematic-debugging in a fresh session and
confirms PASS. The 4-step path to `0.2.0`:
1. `claude plugin validate code-toolkit` ✔ (already passing)
2. `claude plugin uninstall + install code-toolkit@monkey-skills --scope local`
3. Run one systematic-debugging-pressure prompt in fresh session
4. If PASS, drop -draft from both manifest version fields; convert
   this [Unreleased] section to `## [0.2.0] — YYYY-MM-DD`; commit.

### Added — `writing-plans` skill (2 of 3 Phase 2 skills)

Bridge between `brainstorming` (produces the brief) and `subagent-driven-
development` (dispatches subagents). Splits the brief into ≤5 atomic
≤5-minute tasks with explicit RED-GREEN acceptance criteria, self-reviews
via plan-document-reviewer before declaring DONE.

- `skills/writing-plans/SKILL.md` — splitting framework (4-criteria
  per-task: time-box ≤5 min / single module / one failing-test
  acceptance / no hidden coupling); plan size ceiling = ≤5 atomic
  tasks (forcing function for the brainstorming HARD-GATE); BLOCKED
  fallback per Kent Beck (2002) *Test-Driven Development: By Example*
  Part II §Child Test pattern, ISBN 978-0321146533 (when implementer
  returns BLOCKED with decomposition signal, orchestrator re-invokes
  writing-plans on the failing task); Red Flags table covering 7
  rationalizations including ja + zh-TW variants; §When NOT to Use
  with 4 enumerated exemptions.
- `skills/writing-plans/references/plan-format.md` — output schema for
  SDD consumption (required: Source brief / Total tasks ≤5 / Execution
  order / Plan-document-reviewer verdict / per-task: Description /
  Module / Context paths / Acceptance.RED + .GREEN / Dependencies /
  Brief item covered). Worked example: CSV export query param plan with
  3 tasks. Anti-patterns enumerated.
- `skills/writing-plans/references/plan-document-reviewer-prompt.md` —
  evaluator subagent prompt. 12 structured checks (each task ≤5 min /
  single module / failing-test acceptance / brief-to-task coverage map /
  no orphan tasks / DAG no-cycles / etc.). Returns PASS / NEEDS_REVISION
  + structured gap list with check_id / rule quote / where pointer /
  suggested_fix. Mirrors sibling evaluator patterns from SDD's spec-
  reviewer (binary verdict) and code-quality-reviewer (three-valued).
- `skills/writing-plans/README.{md,ja.md,zh-TW.md}` — 3-lang.

### Updated — `using-code-toolkit` router for writing-plans

- Skill Priority table row 2: Planning `writing-plans` flipped from
  "Phase 2 — until then, sketch a ≤5-task plan inline" → "✅ shipped".
- Router stays under the 2000-token P1-A budget: ~1836 tokens (was
  ~1848).
- 3-lang README tables updated in lockstep.

### Added — writing-plans pressure tests

`tests/writing-plans-pressure/prompts/`:
- `too-big-no-split.txt` — Stripe-integration brief that would obviously
  produce 8-12 atomic tasks; user instructs "ship them all in one plan."
  Tests the plan-size-ceiling forcing function.
- `unverifiable-task.txt` — brief with vague Problem / End State /
  Decision + "we'll know it when we see it" on acceptance. Tests
  refusal of vague tasks lacking RED-GREEN.
- `skip-the-plan.txt` — user wants to dispatch SDD directly with the
  brief. Tests the cross-skill contract: SDD's input REQUIRES a plan,
  not a brief.
- `index.md` — assertion table per prompt; Phase 2 ritual acceptance
  is 3 / 3 handled correctly.

### Added — `brainstorming` skill (1 of 3 Phase 2 skills)

Discovery skill with HARD-GATE measure preserved from Superpowers per P2-A.
Walks the user / agent through a 5-axis exploration framework (Problem /
Users / Smallest End State / Alternatives / What Becomes Obsolete) and
emits a structured brief that `writing-plans` (Phase 2, ships next)
consumes.

- `skills/brainstorming/SKILL.md` — HARD-GATE measure ("DO NOT START
  IMPLEMENTING UNTIL YOU HAVE EXPLORED INTENT"); §When NOT to Use with
  4 enumerated exemptions; 5-axis framework with primary-source citations
  (Christensen 1997 JTBD ISBN 978-0875845852; Klement 2018 job-story
  format ISBN 978-1718626751); Red Flags table with en + ja + zh-TW
  triggers; Output Contract pointing at handoff-brief-format.md; Cross-
  skill delegation to `dev-workflow:complexity-critique` (optional,
  Axis 3 smell) and `dev-workflow:proposal-critique` (optional, Axis 4
  triage).
- `skills/brainstorming/references/visual-companion.md` — when a Mermaid
  sequence / C4 / ER / flowchart diagram pays for itself vs when prose
  is enough. Includes axis-to-diagram-type mapping table + worked
  templates with color discipline (preferred green / rejected red /
  removed dashed-red).
- `skills/brainstorming/references/handoff-brief-format.md` — output
  schema for `writing-plans` consumption. Required sections (Problem /
  Users / Smallest End State / Decision / Out of Scope) + optional
  (Alternatives Considered / What Becomes Obsolete / Open Questions /
  Diagrams). Conventional file path: `docs/superpowers/specs/YYYY-MM-DD-
  <topic>.md`.
- `skills/brainstorming/README.{md,ja.md,zh-TW.md}` — 3-lang.

### Updated — `using-code-toolkit` router for brainstorming

- Skill Priority table row 1: Discovery `brainstorming` flipped from
  "Phase 2 — until then, ask 2-3 clarifying Qs" → "✅ shipped".
- `<EXTREMELY-IMPORTANT>` rule 1: dropped the "until that ships, ask
  2-3 clarifying questions" fallback; now points directly at the
  brainstorming skill's 5-axis framework.
- Skill version bumped to 0.2.0-draft.
- Router stays under the 2000-token P1-A budget: ~1848 tokens (was
  ~1853).
- 3-lang README tables updated in lockstep.

### Added — brainstorming pressure tests

`tests/brainstorming-pressure/prompts/`:
- `this-is-simple.txt` — the canonical "feature flag system" PAGNI
  smell (mirrors `dev-workflow:complexity-critique` test prompt #2).
- `i-know-what-to-build.txt` — user with a pre-formed feature list;
  agent must engage Axis 1 (problem behind the solution) + Axis 5
  (what becomes obsolete) before implementation.
- `lets-just-start.txt` — webhook receiver with hidden auth /
  idempotency / observability sub-decisions; agent must engage all
  5 axes minimally.
- `index.md` — assertion table per prompt; Phase 2 ritual acceptance
  is 3 / 3 refused with 5-axis engagement.

### Plugin version

- `.claude-plugin/plugin.json` + `.codex-plugin/plugin.json` bumped
  to `0.2.0-draft`. Drops `-draft` when full Phase 2 (writing-plans +
  systematic-debugging) ships.

### Phase 1 → Phase 2 carryover

Items deferred from Phase 1 into Phase 1.5 / Phase 2 backlog:

- **Feathers (2004) distinction in tdd-iron-law**: Phase 1 live test
  surfaced that the agent did not cite *Working Effectively with
  Legacy Code* (ISBN 978-0131177055) when distinguishing legitimate
  legacy-backfill from "I just wrote 200 lines without tests". Iron
  Law itself worked; the Feathers distinction is a SKILL.md
  sharpening — to be addressed alongside Phase 1.5 dogfood findings.

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
