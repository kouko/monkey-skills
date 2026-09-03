# gate 型 task 的對抗探針在實作之前寫
originator: kouko
kind: engineering
needs-design: no — 只改 build 站派工順序的一句與 review 站對抗段的一句；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-03-loom-post-merge-seams/evidence/probes/]
status: withdrawn — superseded by 2026-09-03-small-change-lane

## Problem
現在對抗者在 checkpoint 時才上場：實作已完成、盲跑已做，對抗者才找洞。首個真實 change 的 W0-04（關閉 commit 形狀規則）走這個順序：實作一輪，之後審 5 輪、修 6 次、換 3 個設計，每輪對抗者都找到一個新的解析邊界。W0-05（副本豁免）改成對抗者先寫 11 個可執行探針（10 個今天就要擋、1 個刻意紅＝實作目標）、實作者再做：實作一輪、審查抓到 1 fatal＋形狀問題、修一輪就過。同一個 change、同一批 agent，順序不同差五輪。

## Proposed outcome
plan 標了 `review: after-task` 或改到 gate／checker 的 task，build 站派實作者之前先派對抗者：讀 spec 該條 REQ，寫一個 pytest 探針檔進 `evidence/probes/`（攻擊案例今天就該擋的要綠、實作目標刻意紅並標記），commit；實作者的派工包指名該檔：紅的變綠、其他不能變綠。checkpoint 時對抗者只需重跑探針並補新攻擊，不從零開始。

## Acceptance
1. 一個 gate 型 task 的派工記錄裡，`adversary` 的 `started` 早於同 task 的 `implementer`。
2. 實作者的 commit 之後探針檔全綠，且探針檔本身在實作 commit 之前就存在（`git log -- evidence/probes/<file>` 的第一個 commit 早於 `Task:` 那個 commit）。
3. docs／skill 型 task 不受影響（對抗產物仍是冷讀報告）。

## Constraints
- 不加機制：對抗者角色、探針格式、`push.probes-adversarial` 都已存在，只改派工順序的文字。
- build 站 SKILL.md 字數帽內。

## Out of scope
- 探針畢業成永久測試（另一條 intent）。
- 修正輪上限（另一條 intent）。

## Open questions
- 只限 gate／checker 型，還是所有 `review: after-task` 的 task 都先派對抗者？這次證據只有 checker 型兩例。
