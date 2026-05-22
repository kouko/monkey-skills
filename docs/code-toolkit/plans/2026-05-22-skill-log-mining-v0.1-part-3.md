# Plan: skill-log-mining v0.1 — Part 3 (SKILL.md body + READMEs + plugin metadata + test-prompts)

**Source brief**: docs/code-toolkit/specs/2026-05-22-skill-log-mining-v0.1-brief.md
**Total tasks**: 4 (≤5 ✓)
**Execution order**: parallel-where-possible (T11 ∥ T12 ∥ T13 ∥ T14 all after Part 2 ships)
**Plan-document-reviewer verdict**: PASS (2026-05-22, round 2 — round 1 NEEDS_REVISION on check 11, fixed by routing cross-Part edge into plan-meta notes)

## Plan-time decisions (inherited from Parts 1 + 2)

See `2026-05-22-skill-log-mining-v0.1-part-1.md` §"Plan-time decisions locked". Relevant carry-overs:
- **Description triggers**: SKILL.md body description (T11) must include EN + JA + ZH-TW trigger lines per repo convention (memory feedback_skill_readme_i18n_required.md). Tri-lang READMEs (T12) follow PR #150 rule.
- **dev-workflow plugin version bump**: 2.3.0 → 2.4.0 (minor, new skill added). CHANGELOG entry required.
- **Marketplace description sync**: monkey-skills root `marketplace.json` entry for `dev-workflow` plugin description MUST match `dev-workflow/.claude-plugin/plugin.json` description verbatim (memory feedback_plugin_json_location_and_description_sync.md). CI enforces via `scripts/check-marketplace-description-sync.py`.

## Cross-cutting plan notes

- **Cross-part prerequisite** (schema clarification): per `plan-format.md`, the `Dependencies` field enum is within-plan only (`"none"` / `"Task N completes first"` / `"Tasks N, M parallel"`). Part 3 begins only AFTER Parts 1 + 2 have shipped (all 10 prior tasks PASS + full `pytest dev-workflow/skills/skill-log-mining/scripts/` green); this is enforced by part-ordering, NOT by per-task Dependencies. Hence T11-T14 all carry `Dependencies: none` (no in-Part-3 predecessors). The cross-Part edge is plan-meta.
- **Commit format** (memory feedback_cc_type_whitelist.md, 9 prior hits — most recent PR #321 hit was `chore:` no-scope on mid-stack commit caught by pre-push CI): `feat(skill-log-mining): T<N> <short>` for body/readme/test tasks; `feat(dev-workflow): bump to v2.4.0 — add skill-log-mining` for metadata. Aggregate Part-3 PR commit: `feat(dev-workflow): skill-log-mining v0.1 ship (closes #<issue>)`.
  - **Pre-push grep** MUST scan `git log main..HEAD`, not just `HEAD~1` (memory's 9th hit was an inherited mid-stack bad commit).
- **External surfaces (memory project_external_surface_grounding_discipline.md)**:
  - T11 references `code-toolkit:dispatching-parallel-agents` (sibling skill — verify name/path) and `code-toolkit:brainstorming` / `code-toolkit:writing-plans` / `code-toolkit:subagent-driven-development` in prose. All internal — no 3rd-party.
  - T13 touches `monkey-skills/marketplace.json` root file — verify path exists before editing.
- **Cross-skill schema-rename blind spot**: T11 SKILL.md body lists CLI invocation strings (e.g. `python -m main`, `python -m propose`, `python -m apply`). If Part 1/Part 2 implementers renamed any script module, T11 prose drifts. Code-quality-reviewer at Part 3 MUST `grep -rn "python -m " dev-workflow/skills/skill-log-mining/` and cross-check against actual `scripts/*.py` filenames.
- **Dual-SSOT audit (memory feedback_lint_checks_md_second_drift_surface.md)**: SKILL.md description + tri-lang READMEs + test-prompts.json + plugin.json `keywords` all encode the skill's identity. Audit ALL FOUR for the same trigger phrasing — phrase drift across surfaces is the failure mode. Whole-branch reviewer's `cross_task_coherence` dimension catches.

## Task 11 — SKILL.md body finalization

- **Description**: Replace the Part 1 stub body with the full SKILL.md prose. Required sections in order: (a) **frontmatter** — `name: skill-log-mining`, `description` ≥150 chars including EN/JA/ZH-TW trigger phrases (e.g. "mine skill logs / 技能ログ採掘 / 技能日誌挖掘"), `version: 0.1.0`. (b) §"When to use" — explicit triggers ("after a multi-PR cycle on code-toolkit:*", "when MEMORY.md exceeds soft limit", "before a skill-refactor session"). (c) §"When NOT to use" — claude-coach-territory (real-time coaching), crune-territory (new skill discovery), `/insights` already covers it. (d) §"Pipeline" — diagram + step-by-step: `main.py` → top-N JSON → Claude dispatches subagents via `code-toolkit:dispatching-parallel-agents` with `agents/prompt-{failure,success}-analysis.md` → collect results → `propose.py` → diff file → human approval → `apply.py --approved`. (e) §"Configuration" — JSON override schema + the 6 Q5 baked defaults documented. (f) §"Operating notes" — `cleanupPeriodDays` 30-day retention warning; "No silent writes" gate; mention `/insights` interactive-only constraint. (g) §"Future (v0.2+)" — Stage 4 SDD consolidation if merge conflicts emerge; YAML config swap; persistent cross-run fingerprint ledger; Codex CLI adapter; Layer A standalone OSS surface. Body MUST stay ≤6,000 tokens per CLAUDE.md.
- **Module**: `dev-workflow/skills/skill-log-mining/SKILL.md`
- **Files touched**: `dev-workflow/skills/skill-log-mining/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/CLAUDE.md` (6k token ceiling + skill structure rules)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/brief-before-asking/SKILL.md` (sibling reference for SKILL.md body shape + tri-lang description trigger pattern)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-judge/SKILL.md` (sibling reference)
  - `/Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-05-22-skill-log-mining-v0.1-brief.md` (locked decisions + Q5 defaults + Out of Scope list)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-log-mining/scripts/main.py` (from Part 2 T9 — CLI flags to document)
- **Acceptance**:
  - **RED**: `python -c "import sys; body=open('dev-workflow/skills/skill-log-mining/SKILL.md').read(); assert 'When to use' in body and 'Pipeline' in body and 'Configuration' in body" ` fails (placeholder stub still in place).
  - **GREEN**: same command succeeds; body has all 7 required sections; description contains all 3 language triggers; total file ≤6,000 tokens (`wc -w` + ~1.3 multiplier as proxy); `.claude/hooks/validate-skill-folder-structure.sh` still PASSes.
- **Dependencies**: none
- **Independent**: true (file-disjoint from T12, T13, T14)
- **Brief item covered**: Smallest End State §"User invokes `/skill-log-mining` ... → skill (Python script + structured subagent prompts) reads ... → orchestrator merges → human sees diff" + the entire pipeline description.

## Task 12 — Tri-language READMEs

- **Description**: Create `README.md` (English, ~150-300 lines), `README.ja.md` (Japanese translation of EN, parallel structure), `README.zh-TW.md` (Traditional Chinese translation of EN, parallel structure). Sections: Overview / Why this exists / How it works (high-level — defer detail to SKILL.md) / Installation (just `Skill(skill: "dev-workflow:skill-log-mining")` in Claude Code) / Quick start example / Configuration reference / Future roadmap / License. Per memory feedback_skill_readme_i18n_required.md + PR #150 / PR #248, all 3 are required at skill ship.
- **Module**: `dev-workflow/skills/skill-log-mining/` (READMEs at skill root)
- **Files touched**: `dev-workflow/skills/skill-log-mining/README.md`, `dev-workflow/skills/skill-log-mining/README.ja.md`, `dev-workflow/skills/skill-log-mining/README.zh-TW.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-judge/README.md` (template — section ordering, callout patterns)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-judge/README.ja.md` (JA translation reference)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-judge/README.zh-TW.md` (ZH-TW translation reference)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-log-mining/SKILL.md` (from T11 — for cross-reference quotes)
- **Acceptance**:
  - **RED**: `ls dev-workflow/skills/skill-log-mining/README.{md,ja.md,zh-TW.md} 2>&1 | grep -c 'cannot access'` returns `3` (all three missing).
  - **GREEN**: all 3 files exist; each has the same section headers in correct language; "Quick start" example identical across languages (code block + invocation); no obviously machine-translated phrasings (implementer SHOULD read sibling JA / ZH-TW README for tone).
- **Dependencies**: none
- **Independent**: true (file-disjoint from T11, T13, T14)
- **Brief item covered**: Smallest End State §"skill scaffolding (SKILL.md + tests + README × tri-language per PR #150 rule)".

## Task 13 — dev-workflow plugin metadata bump + CHANGELOG + marketplace sync

- **Description**: Three file edits with a single acceptance: (a) `dev-workflow/.claude-plugin/plugin.json` — bump `version` 2.3.0 → 2.4.0; append `skill-log-mining` to `keywords` array; description may stay or get a clause "+ skill-log mining for empirical SKILL.md iteration" appended (keep ≤200 chars). (b) `dev-workflow/CHANGELOG.md` — add `## [2.4.0] — 2026-05-22` entry with `### Added` listing `dev-workflow:skill-log-mining v0.1`. (c) `marketplace.json` at repo root — find the `dev-workflow` plugin entry; ensure `description` matches the (possibly updated) `dev-workflow/.claude-plugin/plugin.json` description verbatim. Run `python scripts/check-marketplace-description-sync.py` post-edit; CI hook enforces.
- **Module**: dev-workflow plugin metadata
- **Files touched**: `dev-workflow/.claude-plugin/plugin.json`, `dev-workflow/CHANGELOG.md`, `marketplace.json`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/.claude-plugin/plugin.json` (current state — read before edit)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/CHANGELOG.md` (current state — match formatting of prior entries)
  - `/Users/kouko/GitHub/monkey-skills/marketplace.json` (current state — find dev-workflow entry)
  - `/Users/kouko/GitHub/monkey-skills/scripts/check-marketplace-description-sync.py` (CI guard — verify what it asserts)
- **Acceptance**:
  - **RED**: `python scripts/check-marketplace-description-sync.py` exits non-zero (drift exists after just bumping plugin.json without marketplace sync). Or, if no drift was introduced: `jq -r '.version' dev-workflow/.claude-plugin/plugin.json` returns `2.3.0`.
  - **GREEN**: `python scripts/check-marketplace-description-sync.py` exits 0; `jq -r '.version' dev-workflow/.claude-plugin/plugin.json` returns `2.4.0`; `keywords` array contains `skill-log-mining`; CHANGELOG has new entry dated 2026-05-22; grep `2.4.0` returns hits in plugin.json AND CHANGELOG.
- **Dependencies**: none
- **Independent**: true (file-disjoint from T11, T12, T14)
- **Brief item covered**: Smallest End State §"`dev-workflow:skill-log-mining` (slot into existing 5-strong `skill-*` family)" — metadata bump is what makes the slot official.

## Task 14 — test-prompts.json + trigger-eval.json (description-trigger eval bundle)

- **Description**: Create `test-prompts.json` listing 5-8 should-trigger prompts (EN/JA/ZH-TW mixed; phrasings the skill description should route on, e.g. "I've burned through a lot of code-toolkit PRs lately — what can I learn?", "技能ログから知見を蒸留したい", "從 JSONL 挖掘 skill iteration 機會") + 3-5 should-NOT-trigger prompts (claude-coach territory, /insights territory). Schema matches sibling skills (`brief-before-asking/test-prompts.json` reference). Create `trigger-eval.json` if any sibling uses it for the eval harness driver config. Note per memory feedback_run_loop_iteration_ties.md: do NOT iterate description phrasing for run_loop scores if all iterations tie — that's a framework issue, not a description issue.
- **Module**: `dev-workflow/skills/skill-log-mining/` (eval bundle at skill root)
- **Files touched**: `dev-workflow/skills/skill-log-mining/test-prompts.json`, `dev-workflow/skills/skill-log-mining/trigger-eval.json`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/brief-before-asking/test-prompts.json` (schema template)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/brief-before-asking/trigger-eval.json` (config template)
  - `/Users/kouko/GitHub/monkey-skills/dev-workflow/skills/skill-log-mining/SKILL.md` (from T11 — for trigger-phrase coherence)
- **Acceptance**:
  - **RED**: `python -c "import json; data=json.load(open('dev-workflow/skills/skill-log-mining/test-prompts.json'))['should_trigger']; assert len(data) >= 5"` fails (file missing).
  - **GREEN**: same command + `should_not_trigger` has ≥3 entries; schema matches `brief-before-asking/test-prompts.json` shape (`should_trigger` / `should_not_trigger` keys); manual smoke: run `dev-workflow:skill-creator-advance` eval harness against this skill (out of plan scope to fully pass — just verify the file is parseable input).
- **Dependencies**: none
- **Independent**: true (file-disjoint from T11, T12, T13)
- **Brief item covered**: Smallest End State §"skill scaffolding (SKILL.md + tests + README × tri-language)" — test-prompts is the eval-side test artifact.

## Notes

- **Parallel-dispatch hint for SDD orchestrator**: T11 + T12 + T13 + T14 all have `Independent: true` with disjoint `Files touched`. After Part 2 ships, dispatching-parallel-agents SHOULD dispatch all 4 implementers in one assistant message. There is no T15-style sequential join in Part 3 — the cross-coherence check (descriptions / READMEs / test-prompts / plugin keyword all using the same trigger phrasing) is done by whole-branch reviewer, not by a separate task.
- **Soft-order suggestion if not running parallel**: T11 first (others reference it), then T12 / T13 / T14 in any order.
- **Part-3 ship gate (for finishing-a-development-branch to start)**: all 4 tasks PASS; full repo `pytest` green; `.claude/hooks/validate-skill-folder-structure.sh` PASSes; CI `check-marketplace-description-sync.py` PASSes; `git grep -n 'skill-log-mining' marketplace.json` returns the keyword line.
- **Whole-branch review surface (per memory project_external_surface_grounding_discipline.md)**: at requesting-code-review step, the reviewer's cross-task-coherence dimension (D7) MUST verify: SKILL.md description phrasing ↔ tri-lang README phrasing ↔ test-prompts triggers ↔ plugin.json keyword all use the same language. This is the "dual-SSOT" type pattern (memory feedback_lint_checks_md_second_drift_surface.md) — audit all 4 surfaces.
- **Dogfood validation (post-merge)**: user invokes `Skill(skill: "dev-workflow:skill-log-mining")` against real `~/.claude/projects/` tree → confirms top-N skills returned + at least 1 proposal renders + apply.py refuses without --approved. This is finishing-a-development-branch Step 2 verification, NOT a plan task.
- **Out of scope for v0.1 (deferred per brief Out of Scope §)**: Stage 4 full SDD consolidation; `references/*.md` new-file creation; persistent cross-run fingerprint ledger; Codex CLI / Gemini CLI / Cline / Cursor adapters; AGENTS.md / GEMINI.md / .cursorrules write-back; auto-trigger (cron / SessionStart hook); auto-cleanup of MEMORY.md feedback memos; headless `claude -p` shell-out; Layer A standalone OSS publication; auto-merge to main.
