# Plan: salesforce-toolkit v0.1.0 — part 3 (skill SKILLs + specs + CI)

**Source brief**: docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md
**Total tasks**: 4 (≤5 ✓)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PENDING
**Prerequisites**: part-1 + part-2 merged (plugin scaffold + setup automation 已存在；skill 文中 reference `/salesforce-toolkit:sf-setup` 與 `.mcp.json` salesforce server)

Part 3 scope：兩個 read-only skill 的 SKILL.md 本體（不含 tri-language READMEs，那是 part-4）+ PRODUCT/TECH spec + CI workflow。

## Execution wave 圖

```
Wave 1:  T1 (sf-query SKILL.md) ∥ T2 (sf-report SKILL.md) ∥ T3 (PRODUCT + TECH spec) ∥ T4 (CI)
```

四個 task 全 `Independent: true`，Files touched 兩兩 disjoint，可一條 message 內 4 個 Agent calls 並行 dispatch implementer。

---

## Task 1 — `skills/sf-query/SKILL.md` SOQL/SOSL 自然語言查詢

- **Description**: 建立 `skills/sf-query/SKILL.md`（YAML frontmatter `name: sf-query`, `description ≤200 chars` 含 SOQL / SOSL / query / 查詢 / クエリ 三語觸發詞）+ body：教 LLM 根據自然語言問題、檢視 MCP server 提供的 SOQL/SOSL tool、組合 query、解讀結果。Prerequisite check（`/salesforce-toolkit:sf-setup` 已跑、`sf` CLI 與 MCP server alive）；5 個 worked example（物件 list / record fetch / 條件過濾 / aggregate / cross-object）；常見錯誤處置（field permission 不足、relationship name 拼錯、SOQL syntax error）
- **Module**: `salesforce-toolkit/skills/sf-query/`
- **Files touched**: `salesforce-toolkit/skills/sf-query/SKILL.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/collab-toolkit/skills/slack-automate/SKILL.md
  - /Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md
- **Acceptance**:
  - **RED**: `test -f salesforce-toolkit/skills/sf-query/SKILL.md` fail
  - **GREEN**: 檔案存在；YAML frontmatter 含 `name: sf-query` + `description`；description 含 SOQL / 查詢 / クエリ 三語觸發詞；`grep -c 'SOQL\|SOSL' salesforce-toolkit/skills/sf-query/SKILL.md` ≥ 3；至少 5 個 `### ` 開頭的 worked example heading
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Smallest End State `skills/sf-query/SKILL.md`；Decision Q5 sf-query (SOQL/SOSL)

---

## Task 2 — `skills/sf-report/SKILL.md` Dashboard/Report 拉取分析

- **Description**: 建立 `skills/sf-report/SKILL.md`（YAML frontmatter `name: sf-report`, `description` 含 Salesforce report / dashboard / KPI / 報表 / ダッシュボード 三語觸發詞）+ body：教 LLM 透過 MCP server 列 Report folder、抓 Report metadata、執行 Report、取 row data、做 trend/aggregate 分析、與 Dashboard widget 對話。Prerequisite check 同 sf-query；5 個 worked example（Report run by name / filter by date range / Dashboard snapshot / pipeline funnel / Top-N by metric）；錯誤處置（Report 不在可見 folder、Report Type 限制、row limit）
- **Module**: `salesforce-toolkit/skills/sf-report/`
- **Files touched**: `salesforce-toolkit/skills/sf-report/SKILL.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/collab-toolkit/skills/notion-automate/SKILL.md
  - /Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md
- **Acceptance**:
  - **RED**: `test -f salesforce-toolkit/skills/sf-report/SKILL.md` fail
  - **GREEN**: 檔案存在；YAML frontmatter 含 `name: sf-report` + `description`；description 含 Report / 報表 / ダッシュボード 三語觸發詞；`grep -ci 'Report\|Dashboard' salesforce-toolkit/skills/sf-report/SKILL.md` ≥ 5；至少 5 個 `### ` 開頭的 worked example heading
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Smallest End State `skills/sf-report/SKILL.md`；Decision Q5 sf-report (Dashboard/Report)

---

## Task 3 — `PRODUCT-SPEC.md` + `TECH-SPEC.md`

- **Description**: 建立 `PRODUCT-SPEC.md`（受眾 / JTBD / Phase 1 vs Phase 2+ scope / 商業價值 / non-goals / 競品定位 — DX MCP vs Hosted MCP vs 第三方）+ `TECH-SPEC.md`（模組圖：plugin.json → .mcp.json → bin/sf-mcp-launcher.sh → salesforce-mcp/npx；setup 流程：command → auto-setup.sh → 6 steps → sf CLI + brew；資料流：Claude → MCP server (stdio) → sf CLI keychain → SF instance；介面定義：每個 script 的 input/output/exit codes）；TECH-SPEC `grep` 須引用 PRODUCT-SPEC（CLAUDE.md §Two-Layer Spec 規定）
- **Module**: `salesforce-toolkit/`
- **Files touched**: `salesforce-toolkit/PRODUCT-SPEC.md`, `salesforce-toolkit/TECH-SPEC.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/gws-toolkit/PRODUCT-SPEC.md
  - /Users/kouko/GitHub/monkey-skills/gws-toolkit/TECH-SPEC.md
  - /Users/kouko/GitHub/monkey-skills/CLAUDE.md
- **Acceptance**:
  - **RED**: `test -f salesforce-toolkit/PRODUCT-SPEC.md` 兩檔皆不存在
  - **GREEN**: 兩檔皆存在；PRODUCT-SPEC 含 `## Users` + `## Scope` + `## Non-goals` 三個 heading；TECH-SPEC 含 `## Modules` + `## Data Flow` + `## Interfaces` 三個 heading；`grep -c 'PRODUCT-SPEC.md' salesforce-toolkit/TECH-SPEC.md` ≥ 1
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Smallest End State `PRODUCT-SPEC.md + TECH-SPEC.md`；CLAUDE.md §Two-Layer Spec 規定

---

## Task 4 — `.github/workflows/salesforce-toolkit-ci.yml` shellcheck + bats CI

- **Description**: 建立 `.github/workflows/salesforce-toolkit-ci.yml` — triggers on PR / push 改到 `salesforce-toolkit/**` 或本 workflow；jobs：(a) `shellcheck` — `find salesforce-toolkit -name '*.sh' -print0 | xargs -0 shellcheck`；(b) `bats` — `brew install bats-core` + `bats salesforce-toolkit/tests/`；(c) `marketplace-sync` — `python3 scripts/check-marketplace-description-sync.py`。Runner `macos-latest`
- **Module**: `.github/workflows/`
- **Files touched**: `.github/workflows/salesforce-toolkit-ci.yml`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/.github/workflows/
  - /Users/kouko/GitHub/monkey-skills/scripts/check-marketplace-description-sync.py
- **Acceptance**:
  - **RED**: `test -f .github/workflows/salesforce-toolkit-ci.yml` fail
  - **GREEN**: 檔案存在且 YAML valid（`python3 -c "import yaml; yaml.safe_load(open('.github/workflows/salesforce-toolkit-ci.yml'))"` exit 0）；含 `shellcheck` job；含 `bats` job；含 `marketplace-sync` job；trigger paths 含 `salesforce-toolkit/**`；runs-on 含 `macos`
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Smallest End State `.github/workflows/salesforce-toolkit-ci.yml`

---

## Notes

- 全 4 tasks `Independent: true`，Files touched 兩兩 disjoint：(skills/sf-query/) / (skills/sf-report/) / (salesforce-toolkit root spec files) / (.github/workflows/)。SDD 可一條 message 4 個 Agent calls 並行 dispatch。
- Part-3 在 plan 內完全無 inter-task dependency（Wave 1 收尾即結）。Prerequisites 移至 plan header 表達跨 part 依賴。
- Skill READMEs（sf-query / sf-report 各 4 files）與 plugin-level READMEs（3 files）全部移到 part-4 處理。
