# Monkey Skills

## Skill Development Conventions

### File Paths
- SKILL.md 內引用 bundled files 時使用相對路徑（相對於 skill 目錄）
- Good: `checklists/security-checklist.md`, `protocols/code-brainstorming.md`
- Bad: `domain-teams/skills/code-team/checklists/security-checklist.md`
- 原因：Claude Code 提供 Base Path，bundled files 從 skill 目錄相對解析

### Two-Layer Spec
- PRODUCT-SPEC.md（planning-team 擁有）— 跨域：商業 + 設計 + 技術方向
- TECH-SPEC.md（code-team 擁有）— 技術：模組設計 + 資料流 + 介面定義
- TECH-SPEC.md 應 reference PRODUCT-SPEC.md 的內容

### Skill Structure（CRITICAL — Anthropic 規範，違規會被 hook 擋）

**MUST：skill 資料夾扁平 — subfolder 內不可再嵌 subfolder。**

```
✅ OK（subfolder 是單層）:
skills/init/SKILL.md
skills/init/assets/SCHEMA.md
skills/init/assets/extract_lineage.py
skills/init/scripts/build.py
skills/init/agents/worker.md
skills/init/references/spec.md
skills/init/protocols/code-review.md
skills/init/checklists/security.md

❌ NOT OK（subfolder 內又開 subfolder）:
skills/init/assets/scripts/foo.py     ← assets/ 下開 scripts/
skills/init/agents/sub/worker.md      ← agents/ 下開 sub/
skills/init/references/v1/spec.md     ← references/ 下開 v1/
```

- 每個 skill 是自包含目錄：SKILL.md + 任意數量的**單層** subfolder（assets/、protocols/、agents/、scripts/、references/、checklists/、rubrics/、standards/ 等）
- 任一 subfolder 內**不可再開 subfolder**（這是 Anthropic 官方 skill convention）
- SKILL.md body 控制在 ~6,000 tokens 以內（約 4,500 words）；Anthropic 官方建議 <500 lines，本 repo 改用 token 計量因為行數密度差異大
- Domain knowledge 用目錄慣例 + 描述性檔名路由，不用靜態清單
- Reference files 從 SKILL.md 直接引用，路徑都是 `<subfolder>/<file>` 一層 deep
- **違規會被 `.claude/hooks/validate-skill-folder-structure.sh` 擋下**（PostToolUse on Write|Edit）

### Quality Gates
- 四級系統：SELF / MUST / SHOULD / MAY
- Gate 定義明確指定檔案路徑（相對路徑）
- Verdict 約束內嵌於 PASS_WITH_NOTES 定義，不另開段落

### Agent Behavioral Rules
- worker：produces artifacts, does NOT produce gate verdicts
- evaluator：produces verdicts, does NOT modify artifacts
- **明文豁免**：GENERATE 站的 critic（`loom-interface-design:design-critic`、`loom-spec:completeness-critic`）是 sanctioned co-writer——可對草稿做 provenance-tagged **增補**（`critic-found` 標記），永不覆寫 writer 內容，且仍必須產出兩值 verdict（`PASS_WITH_NOTES` / `NEEDS_REVISION`，無 bare `PASS`——無條件通過即變相 complete 宣稱）。writer≠judge 由 fresh-context panel 保證，不靠「不改檔案」保證
- Knowledge access is open（行為限制，非閱讀限制）

### Agent Launch Convention
- 傳遞 **檔案路徑** 給 agent（不是檔案內容）
- Agent 用 Read 工具自行讀取資源
- 路徑在 SKILL.md 中用相對路徑定義，launch 時解析為絕對路徑
- Worker Input Contract: Resource Paths → Task → Input
- Evaluator Input Contract: Resource Paths → Artifact → Requirements

### Cross-Plugin Delegation Contract

首例：`investing-toolkit:investment-memo-writer` → `domain-teams:investing-team`

**規則**：
1. **Delegation = pass paths + structured seed context** — 不傳遞 file content，不內嵌分析結果
2. **Delegation target receives full authority** — 被委派的 skill 自行載入 standards、執行 gates、產生 verdict；委派方不干涉
3. **Data layer stays in toolkit, analysis layer stays in domain-teams** — investing-toolkit 只負責 data fetch + pipeline orchestration；investing-team 負責分析、primary-source anchoring、gate enforcement
4. **Gate verdicts flow back** — delegation target 的 gate 結果（PASS / NEEDS_REVISION）回傳給 orchestrating skill，不被 swallowed
5. **Cross-plugin path resolution** — 委派時使用 plugin name + skill path（e.g. `domain-teams:investing-team`），不使用檔案系統絕對路徑

**Pattern（investing-toolkit → domain-teams）**：
```
investing-toolkit skill
  → data-fetcher agent (I/O only)
  → domain-teams:{team} skill (analysis + gates)
  → domain-teams:docs-team (formatting, optional)
```

**禁止**：
- 不可在 toolkit skill 內自行執行 investing-team 的 gate logic（避免 gate bypass）
- 不可把 domain-teams standards 複製到 toolkit skill（避免 drift）
- data-fetcher agent 不可做分析（I/O only）
