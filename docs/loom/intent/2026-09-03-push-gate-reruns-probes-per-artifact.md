# push 閘重跑探針按檔案去重
originator: kouko
kind: engineering
needs-design: no — 改 checker 一條規則的重算方式與計數說明；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-03-loom-post-merge-seams/evidence/checkpoint-cost-orchestrator-notes.md]
status: open

## Problem
`push.probes-adversarial` 對每一筆對抗探針紀錄，都執行該筆的 artifact 檔案本身（不是紀錄裡的命令），逐筆串行。紀錄的粒度是「每個案例一筆」（同一個檔案 `-k` 不同案例），重跑的粒度卻是「整檔」，所以首個真實 change 的 21 筆單案探針（加 2 筆整檔探針）讓 checker 把同兩個檔案各整檔重跑十幾次，每次約十秒。門檻「至少 3 支可用探針」也因此曖昧：3 個檔案還是 3 筆紀錄？一輪 ship 因此多一輪窄審（記錄在 evidence）。

## Proposed outcome
checker 對相同 artifact 只執行一次，結果套回所有引用它的紀錄；門檻的計數單位寫清楚（建議：按可執行的 artifact 檔案數，每檔至少一個案例）；rule 的說明文字與 `--list-rules` 同步。

## Acceptance
1. review.json 裡同一個探針檔被引用 N 筆時，`loom_checker.py push` 只執行它一次（以執行時間或紀錄的執行次數證明），結論與逐筆跑相同。
2. 門檻的計數單位在 `--list-rules` 的說明裡一句講清；既有的 loom-post-merge-seams 紀錄（2 個檔案、23 筆對抗探針：21 筆單案＋2 筆整檔）在新規則下的結果與現在一致或被明確說明。
3. 探針檔失敗時，所有引用它的紀錄都被判不可用，錯誤訊息只出現一次。

## Constraints
- 規則數不增不減、不加 waiver；只改重算方式與說明。
- 探針仍在 reviewed_sha 的乾淨樹重跑，不信紀錄。
- 去重後不同檔案要不要平行跑，由 agent 在去重量過後決定，不問使用者；本 intent 只要求去重。

## Out of scope
- 整包測試的平行化（另一條 intent：2026-09-03-package-tests-run-in-parallel）。

## Open questions
- none
