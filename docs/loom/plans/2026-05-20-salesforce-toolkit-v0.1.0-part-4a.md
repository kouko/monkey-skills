# Plan: salesforce-toolkit v0.1.0 — part 4a (English authoritative READMEs)

**Source brief**: docs/loom/specs/2026-05-20-salesforce-toolkit-v0.1.0.md
**Total tasks**: 3 (≤5 ✓)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-05-20 round 1, 14/14 checks)
**Prerequisites**: part-1 + part-2 + part-3 merged (plugin scaffold + setup automation + skill SKILL.md 已存在)

Part 4a scope：3 個 English authoritative README（plugin-level + 2 skill-level）。Translation 部分（ja + zh-TW）由 part-4b 處理。

每個 README 採 collab-toolkit / gws-toolkit 既有 EN 寫作 pattern 為 template。三個 task 全 `Independent: true`，Files touched 兩兩 disjoint，可一條 message 內 3 個 Agent calls 並行 dispatch。

## Execution wave 圖

```
Wave 1:  T1 (plugin-level en) ∥ T2 (sf-query en) ∥ T3 (sf-report en)
```

---

## Task 1 — `salesforce-toolkit/README.md` plugin-level 英文 authoritative

- **Description**: 建立 plugin-level English README — 簡介、Cowork-incompatible warning（⚠️ `sf` CLI + brew 沙箱外才有效，per memory feedback_plugin_metadata_conventions）、Installation（`/plugin install salesforce-toolkit` + `/salesforce-toolkit:sf-setup` quickstart）、Skills 入口（sf-query / sf-report 各一句說明）、Tooling（sf CLI / salesforce-mcp / Node 26 brew 依賴）、Troubleshooting pointer 到 `commands/sf-setup.md`
- **Module**: `salesforce-toolkit/`
- **Files touched**: `salesforce-toolkit/README.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/collab-toolkit/README.md
  - /Users/kouko/GitHub/monkey-skills/gws-toolkit/README.md
  - /Users/kouko/GitHub/monkey-skills/salesforce-toolkit/commands/sf-setup.md
- **Acceptance**:
  - **RED**: `test -f salesforce-toolkit/README.md` exits non-zero
  - **GREEN**: 檔案存在；`grep -ci 'sf-setup' salesforce-toolkit/README.md` ≥ 1；`grep -c 'Cowork\|⚠️' salesforce-toolkit/README.md` ≥ 1；`grep -c 'sf-query\|sf-report' salesforce-toolkit/README.md` ≥ 2
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Smallest End State plugin top-level `README.md`；Current State Evidence「Tri-language README」en authoritative 部分；Cowork-incompatible marker convention

---

## Task 2 — `skills/sf-query/README.md` skill-level 英文 authoritative

- **Description**: 建立 sf-query skill-level English README — quickstart（一句話 skill 用途）+ 3 example prompt（自然語言問題 → 預期 SOQL 結構）+ Troubleshooting pointer。≤80 lines
- **Module**: `salesforce-toolkit/skills/sf-query/`
- **Files touched**: `salesforce-toolkit/skills/sf-query/README.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/collab-toolkit/skills/slack-automate/README.md
  - /Users/kouko/GitHub/monkey-skills/salesforce-toolkit/skills/sf-query/SKILL.md
- **Acceptance**:
  - **RED**: `test -f salesforce-toolkit/skills/sf-query/README.md` exits non-zero
  - **GREEN**: 檔案存在；`grep -c 'SOQL' salesforce-toolkit/skills/sf-query/README.md` ≥ 1；至少 3 個 `### ` 開頭的 example heading；行數 `wc -l` ≤ 80
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Smallest End State `skills/sf-query/README.md`；PR #150 規定 skill-level tri-language README 的 en authoritative 部分

---

## Task 3 — `skills/sf-report/README.md` skill-level 英文 authoritative

- **Description**: 建立 sf-report skill-level English README — quickstart + 3 example prompt（Report run / Dashboard snapshot / pipeline funnel）+ Troubleshooting pointer。≤80 lines
- **Module**: `salesforce-toolkit/skills/sf-report/`
- **Files touched**: `salesforce-toolkit/skills/sf-report/README.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/collab-toolkit/skills/notion-automate/README.md
  - /Users/kouko/GitHub/monkey-skills/salesforce-toolkit/skills/sf-report/SKILL.md
- **Acceptance**:
  - **RED**: `test -f salesforce-toolkit/skills/sf-report/README.md` exits non-zero
  - **GREEN**: 檔案存在；`grep -ci 'Report\|Dashboard' salesforce-toolkit/skills/sf-report/README.md` ≥ 2；至少 3 個 `### ` 開頭的 example heading；行數 `wc -l` ≤ 80
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Smallest End State `skills/sf-report/README.md`；PR #150 規定 skill-level tri-language README 的 en authoritative 部分

---

## Notes

- 全 3 tasks `Independent: true`，Files touched disjoint：plugin root `README.md` / `skills/sf-query/README.md` / `skills/sf-report/README.md`。SDD 可一條 message 3 個 Agent calls 並行 dispatch。
- Translation tasks (ja + zh-TW) 全在 part-4b，每個 task 為 (1 skill ja + 1 skill zh-TW) 對，分別依賴本 plan 的 en 主檔。
