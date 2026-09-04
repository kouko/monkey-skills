# 內部產物一律英文，只有給使用者讀的東西用使用者的語言
originator: kouko
kind: engineering
needs-design: no — engineering；會改的 loom-code/contract/templates/** 全是 .md 模板，checker 的 interface-surface 重算把 templates/ 下的非程式檔排除，使用者讀或輸入的介面沒有改變
evidence: [docs/loom/2026-09-03-package-tests-run-in-parallel/review.json]
status: confirmed 2026-09-05

## Problem
loom 1.0 只規定「盲跑報告用使用者的語言」和「intent 是使用者自己的話」；spec、plan、review.json 的 finding 與 notes、evidence、探針 docstring、commit 訊息、站文字、模板註解都沒有語言規定。結果本 repo 的 1.0 設計文件與模板註解是中文，之後兩個真實 change 的 plan、evidence、cost 筆記也跟著寫成中文，而讀這些的是 reviewer、implementer、adversary——模型在英文開發語料上最強、讀中文規格的誤讀率較高，docs linter（Vale／textlint 的英文規則集）也接不上。kouko 原本的設計邏輯：內部文件與規格用英文，只在要給使用者看的時候才有使用者語言的版本。

前提（2026-09-05 決策點①補記）：模型的程式開發語料絕大多數是英文；而且軟體工程有既有的標準用詞與技術文件寫作規範（先前研究過），可以拿來統一內部文件的敘述方式——reviewer 讀到的措辭一致，審查結果比較不會飄。

## Proposed outcome
把語言政策寫進契約與站文字：

| 產物 | 語言 |
|---|---|
| intent（使用者親口確認的原話） | 使用者的語言 |
| 決策點①②③的對話、盲跑報告、PR 內文 | 使用者的語言 |
| spec、plan、review.json 的 finding／notes／dispatch note、evidence 與 cost 筆記、探針檔的 docstring、commit 訊息、SKILL.md／agents 契約、contract/templates 的註解 | 英文 |

硬切換：從落地後的新 change 起適用；既有的中文 plan／evidence 不回頭翻。站文字各加一句；reviewer 契約加一條：內部產物不是英文時記 nit（不擋）。模板註解改英文。

## Acceptance
1. 一個新 change 走完流程，其 spec／plan／review.json／evidence／探針 docstring／commit 訊息全為英文，intent、盲跑報告與 PR 內文為使用者語言——由 blind-run 報告逐項列出檢查結果。
2. `loom-code/contract/templates/` 內每個檔案的註解與說明文字為英文（`grep -P '[\x{4e00}-\x{9fff}]'` 為空），`intent.md` 模板的欄位語意不變。
3. capture-intent／write-spec／write-plan／build／review／ship 六站的 SKILL.md 各有一句語言規定，reviewer 契約有「非英文內部產物 → nit」一條；`loom_checker.py --list-rules` 規則數不變。
4. 本 repo 既有中文文件不動：`git diff` 不碰 `docs/loom/2026-09-0*/` 與 `docs/loom/intent/` 既有檔案。

## Constraints
- 不加規則、不加 waiver；語言是 reviewer 的 nit 維度，不是閘。
- 使用者面（intent、決策點對話、盲跑報告、PR 內文）語言不變。
- 硬切換，不維護雙語版本。

## Out of scope
- 回頭翻譯既有的中文設計文件與 plan。
- docs linter 的採用（在 2026-09-03-small-change-lane 以「可宣告、不阻擋」方式處理）。
- 三語 README 慣例（skill README 的 i18n 是另一條既有規定，不動）。

## Open questions
- none
