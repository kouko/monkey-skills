# 將 Loom 系列抽成獨立 repository
originator: kouko
kind: engineering
needs-design: no — repository ownership and history migration change without a new runtime interface
evidence: [docs/loom/specs/2026-08-22-independent-composable-loom-plugins.md]
status: confirmed 2026-09-13
publication: automatic — authorized 2026-09-13 by kouko

## Problem
Loom 三個 plugin 的原始碼、測試、發布設定與開發記錄目前位於 monkey-skills monorepo。要獨立維護 Loom 時，直接複製目前檔案會失去逐檔歷史與變更脈絡，而直接搬走又可能漏掉共用測試、CI、文件和混合 commit 中屬於 Loom 的部分。

## Proposed outcome
產生一個可獨立維護三個 Loom plugin 的候選 repository，保留可用的 Git 開發歷史、原始 commit 對照與現有 plugin 邊界，並以可重現的遷移程序證明沒有遺漏必要內容。

## Acceptance
1. 從固定的最新 `origin/main` 來源可重現地產生候選 repository，三個 Loom plugin 的現行 tracked files 與必要的 repository-level 測試、CI、manifest 和文件均有明確歸屬。
2. 候選 repository 保留 Loom 檔案的作者、日期、commit message、逐檔演進與可用的 blame，並提供原始 SHA 到重寫 SHA 的完整對照。
3. 原本同時修改 Loom 與非 Loom 路徑的 commit，在候選 repository 中保留其 Loom 內容，且抽樣與機械檢查都能驗證。
4. 三個 Loom plugin 維持目前的獨立安裝與組合邊界，現有相關 package、boundary、manifest、cross-reference 與 isolated-install 測試在候選 repository 通過。
5. 遷移驗證不修改遠端 repository、不推送、不刪除 monkey-skills 的 Loom 內容，也不改寫 monkey-skills 的既有歷史。

## Constraints
- 來源固定為驗證時最新的已取得 `origin/main` commit；不從目前混有其他未合併 commit 的 worktree HEAD 抽取。
- 使用 fresh clone 執行歷史過濾，不在現有 monkey-skills repository 內重寫歷史。
- 保留 `loom-code`、`loom-design`、`loom-workflow` 三個 plugin 目錄與版本邊界；搬遷期間不順便合併或重新設計 plugin。
- `docs/loom/` 是整個 monkey-skills 的工作記錄，不整批誤搬；Loom 自身的開發證據依可重現規則選取，其他專案記錄留在原 repository。
- 原始 commit SHA 因路徑過濾必然改變；以固定來源、commit map 與永久來源連結保留追溯性。

## Out of scope
- 建立、設定或推送 GitHub repository。
- 決定新 repository 的公開性、正式名稱、權限或維護者。
- 從 monkey-skills 刪除 Loom、改寫其歷史或切換 marketplace 安裝來源。
- Antigravity 相容、plugin 合併或新的 host 支援。
- 修改 Loom station、decision point、review 或 publication 行為。

## Open questions
- none
