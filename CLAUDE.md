# Monkey Skills

## Skill Development Conventions

### File Paths
- SKILL.md 內引用 bundled files 時使用相對路徑（相對於 skill 目錄）
- Good: `checklists/security-checklist.md`, `protocols/code-brainstorming.md`
- Bad: `skills/code-team/checklists/security-checklist.md`
- 原因：Claude Code 提供 Base Path，bundled files 從 skill 目錄相對解析

### Two-Layer Spec
- PRODUCT-SPEC.md（planning-team 擁有）— 跨域：商業 + 設計 + 技術方向
- TECH-SPEC.md（code-team 擁有）— 技術：模組設計 + 資料流 + 介面定義
- TECH-SPEC.md 應 reference PRODUCT-SPEC.md 的內容

### Skill Structure
- 每個 team skill 是自包含目錄（SKILL.md + protocols/ + checklists/ + rubrics/ + standards/）
- SKILL.md body 控制在 500 行以內
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
