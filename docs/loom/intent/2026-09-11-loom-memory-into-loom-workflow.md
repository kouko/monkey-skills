# loom-memory 搬進 loom-workflow 工具箱
originator: kouko
kind: engineering
needs-design: no — 記憶的行為、儲存格式與四個操作已由 2026-09-10-okf-compatible-loom-memory 的 spec 定義並上線，這次只改變它住在哪個 plugin，不新增任何多狀態行為
status: confirmed 2026-09-11
publication: automatic — authorized 2026-09-11 by kouko

## Problem
上一個 change（#821，已合併）把 loom-memory 做成第四個可獨立安裝的 plugin。但 kouko 要的一直是「記憶是 loom-workflow 工具箱裡的一把工具」——跟 git-memory、handoff、decision-map 並排的那種工具，而不是一個要單獨安裝的東西。

那份 spec 把「獨立 plugin」標成 user-decided，但這個岔路從來沒有被當成問題問過 kouko；他確認的 intent 裡只有「independently installable」這句描述，不是一個「A 還是 B」的選擇。所以出貨的形狀不是他決定的，是上一輪推導出來又蓋上使用者印章的。

## Proposed outcome
記憶能力搬進 `loom-workflow`，成為它的一把工具；`loom-memory` 這個獨立 plugin 連同它的 marketplace 條目一起退掉。儲存格式、驗證器、四個操作、已經遷移好的 293 條 lesson 全部原樣保留，只換住址。

## Acceptance
1. 我在只裝了 loom-workflow 的環境裡，可以呼叫記憶能力，做 recall、record、reconcile、retire 四件事，不需要再裝任何別的 plugin。
2. `loom-memory` 這個獨立 plugin 不存在了：marketplace 清單裡沒有它，plugin 目錄也沒有它。
3. 已經遷移好的 293 條 lesson 與那份索引，內容一個位元組都沒變。
4. 驗證儲存庫記憶格式的指令仍然可用，指向 loom-workflow 裡的新位置；舊位置沒有留下任何還能跑的殘骸。
5. 這次改動沒有讓「沒裝 loom-workflow」這件事變得更糟：loom-design 在沒有 loom-workflow 時測試全綠；loom-code 的測試套件在改動前後以完全相同的方式失敗（同一組既有的跨 plugin 讀檔），而且沒有新增任何 loom-code 或 loom-design 對 loom-workflow 的依賴。

## Constraints
- 記憶的儲存格式（OKF v0.2 相容 profile）、四個操作的行為、以及 293 條 lesson 的內容都不重新設計，這次只搬家。
- `git-memory` 維持原狀，它管 commit 與 PR 的 trailer，跟這件事無關。
- 憲章 `PRINCIPLES.md` 的 Fixed choices 要改回「三個 loom 家族 plugin」，並記下修訂日期。
- 實作、資料遷移、發布到「PR 開完且 CI 全綠」為止都已授權；合併仍是另外的決定。
- 第二廠商（Codex）這次不用——kouko 於 2026-09-11 決定，只管這個 change。

## Out of scope
- 重新設計儲存格式或四個操作的行為。
- 對已遷移的 293 條 lesson 做任何內容修改。
- 動 `git-memory` 的職責。
- 把上一個 change 整個還原——loom-code 拆掉 memory 所有權、hook 改指向新驗證器、store 已完成遷移，這些都留著。

## Open questions
- none

## Amendments
- 2026-09-11：Acceptance 5 原寫「loom-code 與 loom-design 在完全沒裝 loom-workflow 時測試全綠」。盲跑發現 loom-code 有 4 處既有的跨 plugin 讀檔（git-memory 的 PR 協定、decision-map 的 SKILL.md、機制重算與契約引用檢查的掃描根），在 origin/main 上以相同方式失敗，亦即這條性質這個 repo 從未滿足過，是撰寫時未先驗基準線的錯誤。kouko 於同日選擇把該條收斂為可證的真話（見上），並將「每個 plugin 可獨立測試」留給另一個 intent。
