# 對抗探針在 ship 時畢業成永久測試
originator: kouko
kind: engineering
needs-design: no — 只加 ship 站 memory 步驟的一個動作與一條 repo 慣例；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-03-loom-post-merge-seams/evidence/probes/]
status: open

## Problem
對抗者寫的探針（可執行的攻擊案例）住在 `docs/loom/<change-id>/evidence/probes/`，是該 change 的證據，不在 repo 的整包測試命令裡；merge 後沒有東西會再跑它們。PRINCIPLES 第 2 條說每個事故要變永久 eval，但目前探針 merge 後就只是歷史。首個真實 change 有 21 個探針（W0-04 十個、W0-05 十一個，約 25 秒），約一半與實作者自己的測試重疊。

## Proposed outcome
ship 站的 memory 步驟多一個動作：把本 change 探針裡**與既有測試不重疊**的案例搬進永久測試目錄（本 repo：`loom-code/scripts/test_*.py`），帶 `Task:` trailer；evidence 裡留原檔不刪。只有 gate／code 型 task 的探針是 pytest，docs／skill 型的對抗產物是冷讀報告，不畢業。

## Acceptance
1. 一個 change 走到 ship，其 `evidence/probes/` 裡有 pytest 檔：ship 之後永久測試目錄多出對應案例，整包命令跑得到它們，evidence 原檔仍在。
2. 與既有測試重複的案例不被搬（以測試名與斷言的目標行為判斷，寫在 ship 站的一句話裡）。
3. 整包測試時間不因此成長超過探針本身的執行時間（畢業不重寫成更慢的 fixture）。

## Constraints
- 不加機制、不加規則：ship 站 memory 步驟加一句，SKILL.md 字數帽內。
- 套件變慢的問題另立 intent（共用 fixture、少開子程序），不用「不畢業」來省。

## Out of scope
- 舊 change 的探針回溯畢業（2026-09-03-loom-post-merge-seams 的 21 個由該 change 自己在 W1-04 順手做）。

## Open questions
- 「不重疊」要不要機械判：先用人判＋一句慣例，量幾個 change 後再說。
