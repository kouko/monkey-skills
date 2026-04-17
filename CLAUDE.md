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

### Skill Structure
- 每個 team skill 是自包含目錄（SKILL.md + protocols/ + checklists/ + rubrics/ + standards/）
- SKILL.md body 控制在 ~6,000 tokens 以內（約 4,500 words）；Anthropic 官方建議 <500 lines，本 repo 改用 token 計量因為行數密度差異大
- Domain knowledge 用目錄慣例 + 描述性檔名路由，不用靜態清單
- Reference files 從 SKILL.md 直接引用（one level deep，不巢狀）

### Quality Gates
- 四級系統：SELF / MUST / SHOULD / MAY
- Gate 定義明確指定檔案路徑（相對路徑）
- Verdict 約束內嵌於 PASS_WITH_NOTES 定義，不另開段落

### Agent Behavioral Rules
- worker：produces artifacts, does NOT produce gate verdicts
- evaluator：produces verdicts, does NOT modify artifacts
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
