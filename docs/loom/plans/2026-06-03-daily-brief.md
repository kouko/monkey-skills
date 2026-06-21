# Plan: briefing-toolkit:daily-brief v0.1

Source brief: docs/loom/specs/2026-06-03-daily-brief-v0.1-brief.md
Total tasks: 10   (width OK — 5 parallel leaves at level 1)
Critical-path depth: 4 (≤5)   ← longest chain: Task 1→2→8→10 / Task 3→7→8→10
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-03 · 14/14 · domain-teams:evaluator)

## Notes

- **Authoring-task adaptation**: this plan builds a new **skill (markdown authoring)**, not runtime code. Each task's acceptance is adapted: **RED** = required file/section absent OR `validate-skill-folder-structure.sh` failing; **GREEN** = file present with the brief-specified sections AND the PostToolUse structure hook exits 0. Criterion 3 (one cohesive acceptance per task) governs over the strict ≤5-min smell threshold — each file is one cohesive authoring unit; splitting a single reference file into sub-tasks would be artificial over-decomposition.
- **Parallelism rationale (level 1)**: Tasks 1, 3, 4, 5, 6 all derive from the **brief as shared SSOT**. Filenames + section scope are fixed by the brief, so SKILL.md (Task 3) can be authored without reading the reference files' content (its `## 參考檔` summaries are determined by the brief). No doc-mirrors-doc *ordering* needed → all marked `Independent: true`. Cross-file consistency (SKILL.md links resolve, scope matches) is verified by the Task 8 integration gate.
- **Memory constraint honored**: Task 2 edits `.claude-plugin/marketplace.json` description to **match** Task 1's `plugin.json` description (Required CI check — plugin/marketplace description sync). Hence Task 2 depends on Task 1.
- **Structure rule honored**: skill is flat — `references/` is single-layer, no nested subfolders (repo CLAUDE.md §Skill Structure, enforced by `.claude/hooks/validate-skill-folder-structure.sh`).
- **skill-creator-advance standards (quality bar for Tasks 3–6, per /goal directive)**: author to the **skill-judge 8-dimension rubric** — **D1 Knowledge Delta** (every section = expert knowledge Claude lacks: the readiness-Gate discipline, per-platform 雷區 [Asana 100/no-page, Notion author-trap, Slack recency-bias, GitHub same-source dedup], continuity live-reverify, PDB ruthless-selection + BLUF; NO basics like "what is Slack"); **D3 Anti-Patterns with WHY** (extend source skill's 反模式); **D5 Progressive Disclosure** (SKILL.md routes + MANDATORY load-triggers embedded in workflow steps + "Do NOT load" guidance; body ≤ ~6k tokens); **D6 Freedom Calibration** (read-only/draft-only = hard constraint/low freedom; fan-out search = medium; focus curation = higher). Description per `dev-workflow/skills/skill-creator-advance/references/description-design.md` (WHAT+WHEN, third-person, about-to-violate trigger, natural keywords, negative trigger, multilingual belt). Adds Task 9 (slash command — skill-creator-advance plugin convention) + Task 10 (skill-judge review gate, target ≥ B).
- **plugin.json has NO `mcpServers` block**: briefing-toolkit *consumes* whatever MCP the user already connected (collab-toolkit / gws-toolkit / a GitHub MCP / their own) and degrades gracefully per the 0-A Gate. Hard-registering 7 servers would duplicate collab/gws-toolkit and break graceful degradation; the skill loads tools at runtime via ToolSearch.
- **Out of scope v0.1** (no tasks): 排程(harness 層,SKILL.md 僅註明)、推送/多格式輸出、self-eval、寫回官方系統、獨立 state 檔。
- **Post-PASS amendment (2026-06-03, re-review skipped)**: tightened Task 6 RED/GREEN to assert the 晨報-output length-ceiling rule (brief Smallest End State §字數上限), per plan-document-reviewer advisory note. Additive + schema-safe (no field removed, DAG/acceptance structure unchanged) → re-review skipped per writing-plans §"Amending a PASS plan".
- **Post-PASS amendment 2 (2026-06-03, re-review skipped)**: per /goal directive「參考 skill-creator-advance 的標準」, added Task 9 (commands/ slash command — skill-creator-advance plugin convention) + Task 10 (skill-judge review gate) + the skill-creator-advance quality-bar note (Tasks 3–6) + the plugin.json no-mcpServers note. Additive (2 new tasks: one leaf + one terminal gate; DAG still acyclic; depth 3→4, ≤5) + schema-safe → re-review skipped per writing-plans §"Amending a PASS plan".

---

## Task 1 — plugin.json scaffolding
- Description: Create `briefing-toolkit/.claude-plugin/plugin.json` for the new toolkit (name `briefing-toolkit`, version `0.1.0`, description naming the daily-brief cross-platform aggregation purpose). Mirror an existing toolkit's manifest shape.
- Module: briefing-toolkit/.claude-plugin
- Files touched: briefing-toolkit/.claude-plugin/plugin.json
- Context paths:
  - collab-toolkit/.claude-plugin/plugin.json (manifest shape to mirror)
  - gws-toolkit/.claude-plugin/plugin.json (second reference)
- Acceptance:
  - RED: `briefing-toolkit/.claude-plugin/plugin.json` does not exist
  - GREEN: valid JSON; `name: "briefing-toolkit"`, `version: "0.1.0"`, `description` present; parses with `python3 -m json.tool`
- Dependencies: none
- Independent: true
- Brief item covered: Decision §"位置:新 toolkit `briefing-toolkit`,單一 skill `daily-brief` 起步"

## Task 2 — marketplace.json registration
- Description: Add a `briefing-toolkit` entry to the root `.claude-plugin/marketplace.json` `plugins` array (`name`, `description`, `source: "./briefing-toolkit/"`). The `description` MUST be byte-identical to Task 1's `plugin.json` description.
- Module: .claude-plugin (root marketplace)
- Files touched: .claude-plugin/marketplace.json
- Context paths:
  - .claude-plugin/marketplace.json (existing entries to append to)
  - briefing-toolkit/.claude-plugin/plugin.json (description source — must match)
- Acceptance:
  - RED: no `briefing-toolkit` object in `marketplace.json` `plugins`
  - GREEN: entry present; `description` string-equals `plugin.json` description; file still valid JSON
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: Decision §"位置:新 toolkit `briefing-toolkit`"(+ repo Required CI check: plugin/marketplace description sync)

## Task 3 — SKILL.md (entry + principles + workflow)
- Description: Author `briefing-toolkit/skills/daily-brief/SKILL.md` — frontmatter (`name: daily-brief`, multilingual `description` with triggers 每日簡報/daily brief/morning brief/今日まとめ/朝のブリーフ, `tags`, `related_skills`) + body: 何時用 / skill 分層(read-only + draft-only)/ 核心原則 / 工作流骨架(0-A Gate → 0-B Intake → continuity-load → fan-out → triage → continuity-diff → 雙產物)/ 反模式 / 參考檔(link the 3 references). Note scheduling is a harness layer (`/schedule` / cron / Cowork), not built-in. Keep body ≤ ~6k tokens.
- Module: briefing-toolkit/skills/daily-brief (SKILL.md)
- Files touched: briefing-toolkit/skills/daily-brief/SKILL.md
- Context paths:
  - ~/Downloads/performance-evidence-audit/SKILL.md (mechanism母體 — workflow shape to mirror)
  - docs/loom/specs/2026-06-03-daily-brief-v0.1-brief.md (the brief — SSOT)
  - four-dx-coach/skills/4dx-audit/SKILL.md (repo aggregator-skill house style)
- Acceptance:
  - RED: `SKILL.md` absent OR missing any of {何時用, skill 分層, 核心原則, 工作流, 反模式, 參考檔}; OR `validate-skill-folder-structure.sh` fails
  - GREEN: all sections present; workflow lists the 7-step chain incl continuity-load + continuity-diff; frontmatter valid YAML; body ≤ ~6k tokens; PostToolUse structure hook exits 0
- Dependencies: none
- Independent: true
- Brief item covered: Decision §"Skill 結構: SKILL.md + references/..." + Smallest End State §"工作流"

## Task 4 — references/platform-search-playbook.md
- Description: Author the 7-platform fan-out playbook: pre-flight 就緒 Gate (連線/身份/讀取煙霧測試 per platform), the common ToolSearch 雷區 (deferred tools, `select:` vs keyword fallback, server-prefix drift), one sub-agent prompt template per platform (Gmail / Slack / Notion / Asana / Drive / Calendar / **GitHub** — GitHub core: `author:@me`, `reviewed-by:@me`, assigned issues, PRs awaiting review; distinguish 本人作者 vs reviewer), and the canonical deep-link form table per platform.
- Module: briefing-toolkit/skills/daily-brief/references (platform-search-playbook.md)
- Files touched: briefing-toolkit/skills/daily-brief/references/platform-search-playbook.md
- Context paths:
  - ~/Downloads/performance-evidence-audit/references/platform-search-playbook.md (6-platform template to mirror + extend)
  - docs/loom/specs/2026-06-03-daily-brief-v0.1-brief.md §"每個平台的 canonical 深連結形式"
- External surfaces: documents the 7 MCP server tool surfaces (Gmail / Slack / Notion / Asana / Drive / Calendar / GitHub) — names/loading via ToolSearch; doc-only, no live calls at author-time.
- Acceptance:
  - RED: file absent OR fewer than 7 platform templates OR GitHub still "選配第七路" OR no link-form table
  - GREEN: 7 core platform templates incl GitHub-as-core; ToolSearch 雷區 section; 就緒 Gate pre-flight; canonical deep-link table covering all 7; structure hook exits 0
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State §"7 平台 raw MCP 平行 fan-out … GitHub" + Users §"工程角色 ⇒ GitHub 是核心"

## Task 5 — references/prioritization-framework.md
- Description: Author the triage + continuity logic: 緊急度 × 相關性 scoring; 動態焦點門檻 (納入條件 / 下限 0「無關鍵焦點」/ 軟上限 ~5 高負載橫幅不截斷); 「需回覆」啟發式 (對我提問的 @mention、等我回的 email、指派給我快到期的 task — mark confidence, never claim certainty); 信心模型 (✅ 2+ 平台 / ⚠️ 單一 / 推論); **延續性 diff** (ID-join against prior CSV → 🆕新增 / ⏳仍在等你(已 N 天)/ ✅已結 / 🔄狀態變化; **硬原則:以 ID 去 live 平台重驗,不信昨日文字**; 首次跑/跳天降級).
- Module: briefing-toolkit/skills/daily-brief/references (prioritization-framework.md)
- Files touched: briefing-toolkit/skills/daily-brief/references/prioritization-framework.md
- Context paths:
  - ~/Downloads/performance-evidence-audit/references/analysis-framework.md (信心模型 + 量化陷阱 to mirror)
  - docs/loom/specs/2026-06-03-daily-brief-v0.1-brief.md §"動態焦點規則" + §"文件累積 + 延續性模型"
- Acceptance:
  - RED: file absent OR missing any of {triage scoring, 動態焦點門檻 with 下限0/軟上限~5, 需回覆 heuristic, 信心模型, 延續性 diff with 4 狀態 + live 重驗 硬原則}
  - GREEN: all five blocks present; dynamic-focus rule states no-silent-truncation; continuity-diff states live-reverify principle; structure hook exits 0
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State §"triage 框架 + 動態焦點" + §"跨日延續性" + Decision §continuity

## Task 6 — references/brief-templates.md
- Description: Author the output templates: 晨報 6-段版型 (涵蓋聲明 / 自上次以來(延續性)/ 今日焦點(動態)/ 當日行程 / 要回覆·要處理 / 進行中專案現況 / 未來 N 天) with emoji-zoning that can be toggled off; 完整事項表版型 (零省略 markdown table: # | 重要度 | 分類 | 平台 | 標題 | 🔗連結 | 日期/期限 | 動作 | 一句話 | 信心; 硬規則 無直連標⚠️不省略); CSV schema (`編號,重要度,分類,平台,標題,唯一識別碼,連結,日期,動作,一句話,信心` — 唯一識別碼 = join key); 資料源涵蓋聲明 block; 日期前綴命名 + 扁平累積規則 (`<date>_晨報.md` etc).
- Module: briefing-toolkit/skills/daily-brief/references (brief-templates.md)
- Files touched: briefing-toolkit/skills/daily-brief/references/brief-templates.md
- Context paths:
  - ~/Downloads/performance-evidence-audit/references/output-templates.md (版型 to mirror)
  - docs/loom/specs/2026-06-03-daily-brief-v0.1-brief.md §"Output Artifact Specs"
- Acceptance:
  - RED: file absent OR 晨報 not 6-section OR full-table not zero-omission OR CSV schema missing 唯一識別碼 join-key OR no naming/accumulation rule OR no 晨報 length-ceiling rule
  - GREEN: 晨報 6-段 template (emoji-toggle noted) **with an explicit per-section / total length-ceiling rule** (避免「AI 回一面牆」, brief Smallest End State §字數上限); 完整事項表 zero-omission table w/ link column + 無直連 rule; CSV schema w/ 唯一識別碼; 涵蓋聲明; 日期前綴扁平命名; structure hook exits 0
- Dependencies: none
- Independent: true
- Brief item covered: Output Artifact Specs §"01_晨報.md" + §"02_完整事項.md/.csv" + §"文件累積 + 延續性模型"

## Task 7 — toolkit meta docs (READMEs + CHANGELOG)
- Description: Author toolkit-level meta files mirroring the existing toolkit convention: `briefing-toolkit/README.md` + `README.ja.md` + `README.zh-TW.md` (tri-language, describing the daily-brief skill) + `briefing-toolkit/CHANGELOG.md` (v0.1.0 initial entry). Content mirrors SKILL.md's purpose + the brief.
- Module: briefing-toolkit (top-level meta docs)
- Files touched: briefing-toolkit/README.md, briefing-toolkit/README.ja.md, briefing-toolkit/README.zh-TW.md, briefing-toolkit/CHANGELOG.md
- Context paths:
  - collab-toolkit/README.md, collab-toolkit/README.ja.md, collab-toolkit/README.zh-TW.md, collab-toolkit/CHANGELOG.md (convention to mirror)
  - briefing-toolkit/skills/daily-brief/SKILL.md (content source — doc-mirrors-doc)
- Acceptance:
  - RED: any of the 4 files absent
  - GREEN: 3 READMEs present in EN/JA/zh-TW describing daily-brief; CHANGELOG.md has v0.1.0 entry; consistent with SKILL.md description
- Dependencies: Task 3 completes first
- Independent: true
- Brief item covered: Handoff §task 7 "多語 README — 比照 repo 新 skill 慣例" (位置決策 = 新 toolkit)

## Task 8 — integration gate (structure + consistency)
- Description: Verify the assembled toolkit: (a) run `.claude/hooks/validate-skill-folder-structure.sh` against `briefing-toolkit/skills/daily-brief/` — confirm flat single-layer structure; (b) confirm SKILL.md body ≤ ~6k tokens; (c) confirm `plugin.json` description string-equals the `marketplace.json` briefing-toolkit description; (d) confirm every `references/…` link in SKILL.md resolves to an existing file; (e) confirm all three reference files + SKILL.md exist.
- Module: (verification — no authoring)
- Files touched: (none — read + validate only)
- Context paths:
  - .claude/hooks/validate-skill-folder-structure.sh
  - briefing-toolkit/skills/daily-brief/SKILL.md
  - .claude-plugin/marketplace.json
  - briefing-toolkit/.claude-plugin/plugin.json
- Acceptance:
  - RED: structure hook non-zero OR description mismatch OR a SKILL.md reference link 404s OR a required file missing
  - GREEN: hook exits 0; descriptions match; all SKILL.md reference links resolve; SKILL.md + 3 references + plugin.json + marketplace entry all present; token budget within ~6k
- Dependencies: Tasks 1, 2, 3, 4, 5, 6, 7 complete first
- Independent: false
- Brief item covered: brief §"skill 結構(扁平單層,符合 repo CLAUDE.md skill 規範)" + Success criteria (誠實涵蓋 / 零省略 verified structurally)

## Task 9 — commands/daily-brief.md slash command
- Description: Create `briefing-toolkit/commands/daily-brief.md` — slash-command entry point per skill-creator-advance plugin convention. Frontmatter `description` one-liner (distinct from the skill description); body delegates: "Use the briefing-toolkit:daily-brief skill to handle this request." (optionally a 2-3 line what-it-does).
- Module: briefing-toolkit/commands (daily-brief.md)
- Files touched: briefing-toolkit/commands/daily-brief.md
- Context paths:
  - collab-toolkit/commands/collab-setup.md (command format to mirror)
  - dev-workflow/skills/skill-creator-advance/references/plugin-conventions.md §Slash Commands
- Acceptance:
  - RED: `briefing-toolkit/commands/daily-brief.md` absent
  - GREEN: file present; frontmatter `description` one-liner; body delegates to `briefing-toolkit:daily-brief`
- Dependencies: Task 3 completes first
- Independent: true
- Brief item covered: skill-creator-advance §"Each skill should have a corresponding slash command entry point in the plugin's commands/ directory"

## Task 10 — skill-judge quality review gate
- Description: Evaluate the assembled `daily-brief` skill against the **skill-judge 8-dimension rubric** (`dev-workflow:skill-judge`). Produce 0-120 score + letter grade + per-dimension scores + critical issues + E:A:R knowledge ratio. Target **≥ B (96+/120, ≥80%)**. If any dimension is critical (esp D1 Knowledge Delta <11, D4 structure auto-cap, D5 Dump), fix the skill and re-evaluate before declaring done.
- Module: (review — no authoring)
- Files touched: (none — evaluation only)
- Context paths:
  - dev-workflow/skills/skill-judge/SKILL.md (the 8-dimension rubric)
  - briefing-toolkit/skills/daily-brief/SKILL.md + references/*
- Acceptance:
  - RED: skill not yet evaluated OR score < B (below 96/120) OR D4 structure auto-cap (nested subfolder)
  - GREEN: skill-judge score ≥ B; no auto-cap; critical issues addressed (or explicitly accepted with rationale)
- Dependencies: Tasks 1, 2, 3, 4, 5, 6, 7, 8, 9 complete first
- Independent: false
- Brief item covered: /goal directive "參考 skill-creator-advance 的標準" (skill-judge rubric = the quality bar)
