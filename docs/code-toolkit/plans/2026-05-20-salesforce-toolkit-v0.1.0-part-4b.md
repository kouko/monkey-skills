# Plan: salesforce-toolkit v0.1.0 — part 4b (Japanese + Traditional Chinese translation READMEs)

**Source brief**: docs/code-toolkit/specs/2026-05-20-salesforce-toolkit-v0.1.0.md
**Total tasks**: 3 (≤5 ✓)
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-05-20 round 1, 14/14 checks)
**Prerequisites**: part-4a merged (3 個 en authoritative README 已存在；ja + zh-TW 從各自的 en 主檔翻譯)

Part 4b scope：3 個 translation pair（plugin-level + 2 skill-level），每 task 翻譯 1 個 en 主檔成 ja + zh-TW 兩語言（同主檔的雙語翻譯為 logical unit；2 檔 ≤ 100 行各，glossary lint 同步通過）。

Translation 規範：
- 日文：technical nouns 保留英文（per `docs/i18n/glossary-ja.md`，不可 katakana 替換 SOQL / SOSL / MCP / brew / OAuth / Report / Dashboard 等）
- 繁中：不可 Mainland calques（per `docs/i18n/glossary-zh-TW.md`，繁中地區慣用語）
- 結構與長度與 en 主檔對齊

## Execution wave 圖

```
Wave 1:  T1 (plugin-level ja+zh-TW) ∥ T2 (sf-query ja+zh-TW) ∥ T3 (sf-report ja+zh-TW)
```

三 task 全 `Independent: true`，Files touched 兩兩 disjoint（plugin root vs sf-query/ vs sf-report/）。Cross-part dependency（各自的 en 主檔）已在 Prerequisites header 處理。

---

## Task 1 — Plugin-level translation pair (`README.ja.md` + `README.zh-TW.md`)

- **Description**: 從 part-4a T1 的 `salesforce-toolkit/README.md` 翻譯成日文 + 繁中。保留 `sf-setup` / `SOQL` / `SOSL` / `Cowork` / `brew` 等英文 noun；ja 不 katakana 替換；zh-TW 不 Mainland calques。Heading 結構與 en 主檔對齊
- **Module**: `salesforce-toolkit/`
- **Files touched**: `salesforce-toolkit/README.ja.md`, `salesforce-toolkit/README.zh-TW.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/salesforce-toolkit/README.md
  - /Users/kouko/GitHub/monkey-skills/collab-toolkit/README.ja.md
  - /Users/kouko/GitHub/monkey-skills/collab-toolkit/README.zh-TW.md
  - /Users/kouko/GitHub/monkey-skills/docs/i18n/glossary-ja.md
  - /Users/kouko/GitHub/monkey-skills/docs/i18n/glossary-zh-TW.md
- **Acceptance**:
  - **RED**: `test -f salesforce-toolkit/README.ja.md && test -f salesforce-toolkit/README.zh-TW.md` exits non-zero（兩檔皆不存在）
  - **GREEN**: 兩檔皆存在；ja 含 `sf-setup` + `SOQL` 英文不變；zh-TW 含 `sf-setup` 不變；ja 不含 Mainland calques；zh-TW 不含 katakana hybrid；二者 heading 數量分別等於 en 主檔 heading 數量（`grep -c '^#' README.md` == `grep -c '^#' README.ja.md` == `grep -c '^#' README.zh-TW.md`）
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Smallest End State plugin top-level `README.ja.md` + `README.zh-TW.md`；Tri-language README 規定 translation 部分

---

## Task 2 — sf-query skill-level translation pair (`README.ja.md` + `README.zh-TW.md`)

- **Description**: 從 part-4a T2 的 `skills/sf-query/README.md` 翻譯成 ja + zh-TW。同 T1 翻譯規範（保留 SOQL / SOSL 英文；ja 不 katakana；zh-TW 不 Mainland calques）
- **Module**: `salesforce-toolkit/skills/sf-query/`
- **Files touched**: `salesforce-toolkit/skills/sf-query/README.ja.md`, `salesforce-toolkit/skills/sf-query/README.zh-TW.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/salesforce-toolkit/skills/sf-query/README.md
  - /Users/kouko/GitHub/monkey-skills/collab-toolkit/skills/slack-automate/README.ja.md
  - /Users/kouko/GitHub/monkey-skills/collab-toolkit/skills/slack-automate/README.zh-TW.md
  - /Users/kouko/GitHub/monkey-skills/docs/i18n/glossary-ja.md
  - /Users/kouko/GitHub/monkey-skills/docs/i18n/glossary-zh-TW.md
- **Acceptance**:
  - **RED**: `test -f salesforce-toolkit/skills/sf-query/README.ja.md && test -f salesforce-toolkit/skills/sf-query/README.zh-TW.md` exits non-zero
  - **GREEN**: 兩檔皆存在；ja 含 `SOQL` 英文不變；zh-TW 含 `SOQL` 不變；ja 不含 Mainland calques；zh-TW 不含 katakana hybrid；每檔行數 ≤ 100；heading 數量分別等於 en 主檔
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Smallest End State `skills/sf-query/README.ja.md` + `README.zh-TW.md`；PR #150 規定 skill-level tri-language

---

## Task 3 — sf-report skill-level translation pair (`README.ja.md` + `README.zh-TW.md`)

- **Description**: 從 part-4a T3 的 `skills/sf-report/README.md` 翻譯成 ja + zh-TW。同 T1 翻譯規範（保留 Report / Dashboard 英文；ja 不 katakana；zh-TW 不 Mainland calques）
- **Module**: `salesforce-toolkit/skills/sf-report/`
- **Files touched**: `salesforce-toolkit/skills/sf-report/README.ja.md`, `salesforce-toolkit/skills/sf-report/README.zh-TW.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/salesforce-toolkit/skills/sf-report/README.md
  - /Users/kouko/GitHub/monkey-skills/collab-toolkit/skills/notion-automate/README.ja.md
  - /Users/kouko/GitHub/monkey-skills/collab-toolkit/skills/notion-automate/README.zh-TW.md
  - /Users/kouko/GitHub/monkey-skills/docs/i18n/glossary-ja.md
  - /Users/kouko/GitHub/monkey-skills/docs/i18n/glossary-zh-TW.md
- **Acceptance**:
  - **RED**: `test -f salesforce-toolkit/skills/sf-report/README.ja.md && test -f salesforce-toolkit/skills/sf-report/README.zh-TW.md` exits non-zero
  - **GREEN**: 兩檔皆存在；ja 含 `Report` + `Dashboard` 英文不變；zh-TW 含 `Report` + `Dashboard` 不變；ja 不含 Mainland calques；zh-TW 不含 katakana hybrid；每檔行數 ≤ 100；heading 數量等於 en 主檔
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: Smallest End State `skills/sf-report/README.ja.md` + `README.zh-TW.md`；PR #150 規定 skill-level tri-language

---

## Notes

- 全 3 tasks `Independent: true`，Files touched 兩兩 disjoint：(salesforce-toolkit/) / (skills/sf-query/) / (skills/sf-report/)。可一條 message 內 3 個 Agent calls 並行 dispatch。
- RED 採 compound diagnostic（`test -f A && test -f B`）：若任一 file 不存在則 exit non-zero — 比單檔 RED 更精準地對應 task 產出 2 個檔的 binary contract。
- 每 task 翻譯一個 en 主檔成兩語言為自然 unit（同源、同結構、glossary lint 同步）；不混 2 個不同 source 主檔的翻譯，避免上輪 part-4 T5 4 檔過大問題。
