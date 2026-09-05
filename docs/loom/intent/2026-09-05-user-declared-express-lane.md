# 使用者宣告的車道：full／express／gate-only——① 時宣告或實作途中切換、切換時給三格後果選項、repo 有預設車道、gate 類 delta 永遠 full
originator: kouko
kind: engineering
needs-design: no — 只改 intent 模板一行、KICKOFF 一行、checker 的車道重算多讀一個宣告（規則數不變）、review／build／ship 站文字各一句加一份參考檔、PR 內文一行；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-03-artifact-language-policy/review.json, docs/loom/2026-09-05-checker-fix-rounds-and-tree-bound-probes/review.json, docs/loom/2026-09-05-review-sees-complexity-and-process-cost/review.json]
status: confirmed 2026-09-05

## Problem
loom 的車道由 checker 從 diff 重算（small／full），不能宣告——這防的是 agent 自己選輕的。但「這個 change 我願意花多少驗證成本」跟「要不要第二讀者」一樣，是使用者的決定，而且常常做到一半才看得出這個 change 有多重。現在沒有任何方法讓使用者說「這次一位讀者就好」或「這次只過閘、不用審」；唯一的快路是不走 loom。

不走 loom 已經是常態：`~/DataspellProjects/iCHEF-dbt-pipeline` 從 2026-07-01 起 main 上 63 個 PR，只有 1 個全走 loom（#540），44 個只留 plan 文件或記憶尾標、跳過 intent／review／盲跑，18 個什麼都沒留；72 則 commit 訊息沒有一則說明為什麼跳過，repo 也沒有任何規則說 loom 何時適用（AGENTS.md 417 行零提及）。也就是說真實世界的「快速模式」＝「零驗證、零紀錄」。本 repo 的三個 change（#791、#793、#794）都是 skill／契約／checker，每個 full 且花 2.6–10 小時；其中有些明明可以更輕。

## Proposed outcome
1. **三格車道，宣告的人只能是使用者**：`full`（現行）、`express`、`gate-only`。intent 多一個可選欄位 `lane: express | gate-only`；在決策點①宣告，或實作途中由使用者指示切換——切換是一個 commit（intent 加一行 `lane: <名> — switched <日期> by <name>, from <wave 或 round>`，commit 訊息帶同一行，checker 比對），對話覆述後果並記進 `questions[]`（type consequence）。切回 full 隨時可以，同樣一行。名字不用 minimal／small／lite：`small` 是 checker 算出來的既有車道。
2. **express 的內容**：讀者下限 1（使用者在 ① 指定 Codex 或 Claude）；盲跑只在驗收條非機械可查時跑一次；adversary 只在 branch-end 一次（仍 ≥3 探針）；沒有中途 wave-end checkpoint。
3. **gate-only 的內容**：沒有讀者、沒有盲跑、沒有修正輪；仍有 ≥3 探針（adversary 一次）、整包測試、push 閘一條不少、記憶尾標、review-only commit＋關閉行、③——③ 讀的是探針與整包測試結果的一頁，不是盲跑報告。plan 可省：單 task 直接一個 commit 帶 `Task: T1`。禁用範圍比 express 寬：delta 含 checker／hooks／agent 契約／SKILL.md 就不能選。
4. **切換時給三格後果選項**：使用者說「快速模式」「切換模式」「不用審」時，站以固定格式列出三格——每格寫「失去什麼、還剩什麼、估計還要多久」，標出目前所在，**不能選的格照列並說原因**（delta 類型），估時來自 cost 欄位與上一個同車道 change、沒資料寫「無估計」；口頭對應寫死：「快速模式」→ express、「只過閘」「不用審」→ gate-only。這段住在 review 站的參考檔 `references/lane-switch.md`，build／review／ship 三站各一句指向它。
5. **checker 的車道重算多讀這個宣告**：宣告只在 delta 不含該車道禁用的檔案類型時生效；gate 類永遠 full。效果：讀者下限（full 2／express 1／gate-only 0）；`push.verdicts-ge-2` 的 floor 隨之；不加規則、不刪規則。
6. **repo 預設車道**：KICKOFF 多一行 `default-lane: full | express | gate-only`；沒宣告就用它；① 覆述時說「這次照 repo 預設走 X，要升就說」。本 repo 填 full。
7. **看得見**：PR 內文一行 `lane: <名>（第 N 輪起）`；cost 欄位照記，讓「gate-only 事後出包率」可回頭看。
8. **不變的**：writer≠verifier、push 閘重跑測試與探針、③、記憶步驟；agent 不得自行寫 `lane:`（站文字明寫，user-judgment-leak 鏡頭把「agent 自己切」列為 finding）。

## Acceptance
1. intent 模板有 `lane:` 欄位說明（可選；值 `express` 或 `gate-only`；宣告或切換都帶日期與人）；KICKOFF 模板有 `default-lane:` 說明；checker 的 `intent` 子命令接受兩者，且切換 commit 的訊息不含同一行時擋（與 `needs-design:` 同一招）。
2. 在沙盒：一個 `lane: express` 的 docs／skill 類 change，`loom_checker.py push` 對只有一位讀者的 branch-end 輪 exit 0；同一沙盒把 delta 加進 `loom-code/scripts/loom_checker.py` 一行，變回 full、一位讀者被擋——各一個測試。
3. 在沙盒：一個 `lane: gate-only` 的純 docs change，零讀者、有 ≥3 探針與整包測試紀錄，`push` exit 0；同一沙盒 delta 加進任一 SKILL.md 或 `agents/*.md`，零讀者被擋——各一個測試。
4. 在沙盒：實作途中切換（切換 commit 落在 round 2 之後），round 2 的兩位讀者照舊、round 3 起一位讀者被接受；切換 commit 訊息缺那一行時擋——各一個測試。
5. `references/lane-switch.md` 存在，含三格固定格式（失去什麼／還剩什麼／估時）、「不能選的格照列並說原因」、口頭對應表；build／review／ship 各一句指向它，有釘測試（肯定句、無否定詞、反例自測）。冷讀：一個 cold agent 只讀 review 站文字＋這份參考檔，面對「delta 含 SKILL.md、使用者說快速模式」的合成情境，要列出三格且把 gate-only 標成不能選並說出原因——由盲跑報告記錄。
6. review 站文字：express／gate-only 各一段行為（讀者數、盲跑條件、adversary 一次、無中途 checkpoint、gate-only 的 ③ 讀什麼）；ship 站：PR 內文一行；有釘。
7. `--list-rules` 規則數不變（27）；既有 full／small 的所有測試不動；本 repo 的 KICKOFF 填 `default-lane: full`。

## Constraints
- 宣告的人只能是使用者：agent 不得在 intent 或 plan 裡自行寫 `lane:`；站文字明寫。
- gate 類 delta 永遠 full——checker 守著其他所有東西，它自己不走快車道；gate-only 另加禁用 agent 契約與 SKILL.md。
- express 與 gate-only 都不省 push 閘：探針 ≥3、整包測試、writer≠verifier 照舊。
- 不加 checker 規則、不刪規則。
- 本 change 自己改 checker，走 full。

## Out of scope
- 把 small 車道的自動判定範圍加寬（那是 agent 端的重算）。
- 各車道的品質追蹤（哪些 express／gate-only change 事後出包）——用 cost 欄位累積後再看。
- iCHEF-dbt-pipeline 的 AGENTS.md 何時適用 loom 的規則——另一個 repo 的事，這裡只提供 `default-lane`。

## Open questions
- none
