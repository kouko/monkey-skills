# 審查要看得見複雜度：docs／skill 鏡頭加 deletion-first、字數帽調高要記理由並逼出刪減候選、每個 change 記流程成本、派工紀錄按 wave／輪合併
originator: kouko
kind: engineering
needs-design: no — 只改審查鏡頭的參考文件、reviewer 契約、review.json 與 KICKOFF 的幾行欄位、ship 的 PR 內文模板；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-03-artifact-language-policy/review.json, docs/loom/2026-09-05-memory-step-before-branch-end-and-prose-pin-rule/review.json, loom-code/skills/review/references/lenses.md]
status: open

## Problem
loom 的複雜度防線只在 **code 鏡頭**裡：`deletion-first`（新的抽象要有兩個現成使用者，提 finding 必須說出更小的做法）、`deliberate-simplification`、`architecture`、`refactoring`，加上 implementer 基線的「Simplicity first」。但最近四個 change（#789、#790、#791、記憶步驟搬家）動的全是站文字、契約與模板，走的是 **docs／skill 鏡頭**——那兩條鏡頭沒有任何一維問「這個機制有必要嗎？有沒有更小的寫法？」。結果：

- 字數帽變成唯一的代理指標，而我們一路在調高它（reviewer 契約 1300→1340→1460；write-plan 站 4291／4500），調高從來不需要理由。
- 「同一 checkpoint 第三輪→停下來重看設計」是讀者信任型規則，#791 branch-end 跑到 11 輪、同一個探針釘被收緊三次，沒有人被逼著問「這種釘該不該存在」。
- 流程本身的膨脹沒人量：每個 change 花幾輪、派幾次工、調了幾次帽，只在我的筆記裡，PR 看不到，所以「新流程有沒有比較省」永遠回答不了。

## Proposed outcome
1. **docs 與 skill 鏡頭各加一維 `deletion-first`**：站文字或契約每新增一段（或一個機制、一個預留任務、一個 fallback 路徑），delta 裡要能找到它取代了什麼、或防的是哪個已發生的失敗（引用 review.json 或 memory 條目）；找不到就是 finding，且 finding 必須附「更小的寫法」——與 code 鏡頭同一條規則、同一嚴重度規則（重要度按後果）。
2. **字數帽調高要付代價**：任何 `*_CAP` 常數調高的 commit，review.json 的 notes 要有一行理由；同一檔案連續兩個 change 都調高＝設計味道，reviewer 在該檔的 `deletion-first` 維度必須列出至少一個刪減候選（可以被駁回，但不能不列）。
3. **每個 change 固定記流程成本**：review.json 加一個 `cost` 區塊（輪數、派工數、字數帽異動、從 plan commit 到 PR 開出的時數），review 站在每個 checkpoint 更新，ship 的 PR 內文有一段列出來；模板同步。
4. **第三輪重看設計改成看得見**：review 站在同一 checkpoint 的第三輪，必須在 notes 寫一行「設計重看的結論」（繼續修／換設計／接受為 nit），沒有這行的第三輪 verdict 不算完成（站文字＋釘測試，不加 checker 規則）。
5. **順手補一個已知洞**：KICKOFF 的 package-tests 指令補上 `loom-design/scripts/`（#791 兩次 CI 紅的根因），ship 站關閉 commit 前要跑的檢查清單與 CI 的 job 對齊。
6. **派工紀錄按 wave／輪合併 commit**（2026-09-05 追加）：PR #792 的分支有 56 個 commit，實作只佔 5 個，派工紀錄佔 16 個——因為我把「紀錄要在派工前 commit、與工作分開」讀成「每筆一個 commit」。build 站與 review 站文字改為：同一個 wave 的所有 implementer 紀錄一次 append、一次 commit 再派；同一輪的 adversary／blind-runner／讀者紀錄同樣一次 commit（review 站對前兩者本來就這樣寫）。探針作者修自己探針的 bug、且尚未被任何讀者看過時，amend 進原探針 commit 而非新開一筆。

## Acceptance
1. `lenses.md` 的 docs 與 skill 鏡頭各多一維 `deletion-first`，定義含「必須附更小的寫法」；reviewer 契約的鏡頭表同步；有釘測試。用一個合成的 delta（站文字多一段、沒有任何 review.json 或 memory 條目對應）冷讀 reviewer 契約，讀者要提出 `deletion-first` finding 並附更小寫法——由盲跑報告記錄。
2. 用一個合成的 review.json（同一檔案兩個 change 連續調帽）盲跑 reviewer，讀者列出刪減候選；review 站文字寫明「調帽 commit 要在 notes 記理由」並有釘。
3. review.json 模板與本 repo 的 KICKOFF 各多 `cost` 欄位（輪數、派工數、字數帽異動、時數）；review 站每個 checkpoint 更新；ship 的 PR 內文模板多一段「流程成本」；這個 change 自己的 review.json 與 PR 內文就有這段。
4. review 站文字：同一 checkpoint 第三輪 verdict 的 notes 必有「設計重看」一行；有釘測試；本 change 若真的跑到第三輪，那一行就在。
5. `docs/loom/KICKOFF-DEFAULTS.md` 的 package-tests 指令包含 `loom-design/scripts/`；ship 站關閉 commit 前的檢查清單列出 CI 的每個 job 對應命令，有釘；`--list-rules` 規則數不變（27）。
6. build 站 §3 與 review 站 §2 各有一句「同一 wave／同一輪的派工紀錄合成一個 commit、在派工之前」，有釘測試；adversary 契約有一句「未被讀者看過的探針修正 amend 進原 commit」；用這份 intent 自己的 change 當樣本：分支上 `chore(loom): dispatch` 開頭的 commit 數 ≤ wave 數＋審查輪數，由盲跑報告數給你看。

## Constraints
- 不加 checker 規則；四項都是鏡頭定義、站文字、契約與紀錄欄位。
- `deletion-first` 的 finding 沒有附更小寫法就不成立（與 code 鏡頭同一條）。
- 既有 change 的 review.json 不回頭補 cost。

## Out of scope
- 修正輪只要提 finding 的讀者回來、探針綁樹雜湊（另一份 intent：2026-09-05-checker-fix-rounds-and-tree-bound-probes）。
- 自動量測「句型固定是否讓判決不飄」——等資料。
- 把字數帽本身改成 token 計量或拿掉。

## Open questions
- none
