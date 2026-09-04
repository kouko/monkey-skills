# reviewer／adversary 契約各加一段定位；讀者的可執行 finding 由對抗者編成探針
originator: kouko
kind: engineering
needs-design: no — 只改兩份 agent 契約檔各一段與 review 站一句；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-04-checker-seams/review.json, docs/loom/2026-09-04-checker-seams/evidence/probes/test_abuse_branch_end.py]
status: open

## Problem
`loom-code/agents/reviewer.md` 與 `agents/adversary.md` 都有角色開頭句（judge／attacker）與機制（維度表、探針格式），但沒有一句說「你負責哪一種真相」，兩個角色的邊界只能從維度名自己歸納。2026-09-04-checker-seams 的實測：對抗者抓的 4 條全是可執行的邊界（stale trunk、路徑正規化、第一父系鏈），讀者抓的 6 條裡 4 條寫不成測試（文字誇大、流程遺漏、報告與 Acceptance 不一致）——分工明確存在，契約沒寫。另一個缺口是單向流動：讀者抓到的可執行 finding（`--is-ancestor` ≠ 第一父系鏈）只變成修正 commit＋單元測試，直到 branch-end 才由對抗者順手編成探針，那是臨時決定不是站規則。

## Proposed outcome
1. `adversary.md` 加一段定位：負責**負向**——禁止的行為；證據必須可執行、可在乾淨樹重跑；不評設計、不對帳。
2. `reviewer.md` 加一段定位：負責**對帳**——做出來的與 intent／plan／文字自身的承諾對不對得上，雙向：該有的沒有（遺漏）、說了沒做的（誇大）、兩份文件互相矛盾；產出是主張，靠修正輪確認；正向可執行的部分屬實作者的 RED，不是讀者的。
3. review 站修正輪加一句：讀者的 `important` finding 若可寫成會跑的案例，修正輪的對抗者把它編進本 change 的探針檔（`probes[]` 一筆），讓它從「有人讀到過」變「push 時重跑、merge 後可畢業」。

## Acceptance
1. 兩份契約檔各有一段以「你負責…」開頭的定位段，冷讀 agent 拿到任一檔能一句話說出自己與另一角色的邊界（冷讀盲跑：給 agent 一個混合 finding 清單，它能正確分出哪些歸自己）。
2. review 站的修正輪文字含那一句；`test_review_station_text.py` 斷言存在。
3. 字數帽內；站摘要表若需同步照 `test_station_summary_table.py`；loom-code 版本 bump。

## Constraints
- 不加規則、不動 checker；純契約文字。
- 每段 ≤80 字（英文），不重述維度表。

## Out of scope
- 對抗者的攻擊目錄本身；讀者維度的增刪。

## Open questions
- none
