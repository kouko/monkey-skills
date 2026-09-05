# 使用者宣告的快速車道：① 時宣告或實作途中切換，只影響之後的輪次，gate 類 delta 不接受
originator: kouko
kind: engineering
needs-design: no — 只改 intent 模板一行、checker 的車道重算多讀一個宣告（規則數不變）、review／build／ship 站文字各一句、PR 內文一行；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-03-artifact-language-policy/review.json, docs/loom/2026-09-05-memory-step-before-branch-end-and-prose-pin-rule/review.json, docs/loom/2026-09-05-checker-fix-rounds-and-tree-bound-probes/review.json]
status: open

## Problem
loom 的車道由 checker 從 diff 重算（small／full），不能宣告——這防的是 agent 自己選輕的。但「這個 change 我願意花多少驗證成本」跟「要不要第二讀者」一樣，是使用者的決定，而且通常做到一半才看得出這個 change 有多重。現在沒有任何方法讓使用者說「這次一位讀者、不用盲跑就好」；唯一的快路是不走 loom（沒審查紀錄、沒記憶尾標）。這幾週的 change 全是 skill／契約／checker，每個都 full 且花 6–10 小時；其中有些（例如一句站文字）明明可以更輕。

## Proposed outcome
1. **intent 多一個可選欄位 `lane: express`**：在決策點①宣告，或實作途中由使用者指示切換——切換是一個 commit（intent 加一行 `lane: express — switched <日期> by <name>, from <wave 或 round>`，commit 訊息帶同一行，checker 比對），對話覆述後果並記進 `questions[]`（type consequence）。切回 full 隨時可以，同樣一行。
2. **checker 的車道重算多讀這個宣告**：宣告的 express 只在 delta 不含 gate 類檔案（checker、hooks）時生效；gate 類永遠 full。express 的效果：讀者下限 1；`push.verdicts-ge-2` 的 floor 隨之；不加規則、不刪規則。
3. **站文字**：review 站——express 時一位讀者、盲跑只在驗收條非機械可查時跑一次、adversary 只在 branch-end 一次（仍 ≥3 探針）；build 站——express 時沒有中途 wave-end checkpoint，只有 branch-end；切換只影響切換 commit 之後的輪次，進行中的那一輪照原車道跑完。ship 站——PR 內文一行「lane: express（第 N 輪起）」，merge 的人看得到。
4. **不變的**：writer≠verifier、push 閘重跑測試與探針、③、記憶步驟。

## Acceptance
1. intent 模板有 `lane:` 欄位說明（可選；值 `express`；宣告或切換都帶日期與人）；checker 的 `intent` 子命令接受它，且切換 commit 的訊息不含同一行時擋（與 `needs-design:` 同一招）。
2. 在沙盒：一個 `lane: express` 的 docs／skill 類 change，`loom_checker.py push` 對只有一位讀者的 branch-end 輪 exit 0；同一個沙盒把 delta 加進 `loom-code/scripts/loom_checker.py` 一行，變回 full、一位讀者被擋——各一個測試。
3. 在沙盒：實作途中切換（切換 commit 落在 round 2 之後），round 2 的兩位讀者照舊、round 3 起一位讀者被接受；切換 commit 訊息缺那一行時擋——各一個測試。
4. review／build／ship 三站各有一句 express 的行為（讀者數、盲跑條件、無中途 checkpoint、PR 內文標示），有釘測試（肯定句、無否定詞、反例自測）。
5. `--list-rules` 規則數不變（27）；既有 full／small 的所有測試不動。

## Constraints
- 宣告的人只能是使用者：agent 不得在 intent 或 plan 裡自行寫 `lane: express`；站文字明寫，且 user-judgment-leak 鏡頭把「agent 自己切」列為 finding。
- gate 類 delta 永遠 full——checker 守著其他所有東西，它自己不走快車道。
- express 不省 push 閘：探針 ≥3、整包測試、writer≠verifier 照舊。

## Out of scope
- 把 small 車道的自動判定範圍加寬（另一個問題：那是 agent 端的重算）。
- express 的品質追蹤（哪些 express change 事後出包）——用複雜度那份 intent 的 cost 欄位累積後再看。

## Open questions
- none
