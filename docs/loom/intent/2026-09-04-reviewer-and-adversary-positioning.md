# reviewer／adversary 契約各加一段定位；讀者的可執行 finding 由對抗者編成探針
originator: kouko
kind: engineering
needs-design: no — 只改兩份 agent 契約檔各一段與 review 站一句；沒有使用者讀或輸入的介面
evidence: [docs/loom/2026-09-04-checker-seams/review.json, docs/loom/2026-09-04-checker-seams/evidence/probes/test_abuse_branch_end.py, docs/loom/2026-09-04-reviewer-and-adversary-positioning/evidence/research-reviewer-adversary-roles.md, docs/loom/2026-09-04-reviewer-and-adversary-positioning/evidence/research-role-separation-ablations.md]
status: closed 2026-09-04 — PR #787

## Problem
`loom-code/agents/reviewer.md` 與 `agents/adversary.md` 都有角色開頭句（judge／attacker）與機制（維度表、探針格式），但沒有一句說「你負責哪一種真相」，兩個角色的邊界只能從維度名自己歸納。2026-09-04-checker-seams 的實測：對抗者抓的 4 條全是可執行的邊界（stale trunk、路徑正規化、第一父系鏈），讀者抓的 6 條裡 4 條寫不成測試（文字誇大、流程遺漏、報告與 Acceptance 不一致）——分工明確存在，契約沒寫。另一個缺口是單向流動：讀者抓到的可執行 finding（`--is-ancestor` ≠ 第一父系鏈）只變成修正 commit＋單元測試，直到 branch-end 才由對抗者順手編成探針，那是臨時決定不是站規則。

## Proposed outcome
1. `adversary.md` 加一段定位：負責**負向**——禁止的行為；證據必須可執行、可在乾淨樹重跑；不評設計、不對帳。
2. `reviewer.md` 加一段定位：負責**對帳**——做出來的與 intent／plan／文字自身的承諾對不對得上，雙向：該有的沒有（遺漏）、說了沒做的（誇大）、兩份文件互相矛盾；產出是主張，靠修正輪確認。對帳優先，不是禁止執行：讀者可以引用對抗者已產出的執行證據（探針、套件結果），但不自己寫探針；正向可執行的部分屬實作者的 RED，不是讀者的。
3. review 站修正輪加一句：讀者的 `important` finding 若可寫成會跑的案例，修正輪的對抗者把它編進本 change 的探針檔（`probes[]` 一筆），讓它從「有人讀到過」變「push 時重跑、merge 後可畢業」。這是修正輪順手做的一步，不另開站、不加交接文件（業界實測：按工種切角色的交接有協調成本）。
4. 兩段定位的措辭寫成「本流程的分工」，不寫成「業界共識」：文獻支持讀者獨立於實作者、對抗者獨立於實作者、讀與跑抓不同缺陷類別；「讀者與對抗者彼此拆成兩個 agent」沒有任何直接比較，是本流程的設計假設，靠之後各 change 的 finding 來源分布驗證。
5. `docs/loom/README.md` 加一節：checkpoint 的三個驗證角色（blind-runner／reviewer／adversary，附中文名）什麼時候被誰觸發、哪些同時派、哪些必須先後——一張寬 ≤72 欄的序列圖（ascii-graph 生成）加一張步驟表，讓之後的 session 不用重推（kouko 2026-09-04 決策點①後加入）。

## Acceptance
1. 兩份契約檔各有一段以「你負責…」開頭的定位段，冷讀 agent 拿到任一檔能一句話說出自己與另一角色的邊界（冷讀盲跑：給 agent 一個混合 finding 清單，它能正確分出哪些歸自己）。
2. review 站的修正輪文字含那一句；`test_review_station_text.py` 斷言存在。
3. 字數帽內；站摘要表若需同步照 `test_station_summary_table.py`；loom-code 版本 bump。
4. `docs/loom/README.md` 有那一節：序列圖每行顯示寬度 ≤72、三個角色的英文契約檔名都出現、步驟表列出並行與先後；圖旁記下生成用的 payload 或命令，重生得到同一張圖。

## Constraints
- 不加規則、不動 checker；純契約文字。
- 每段 ≤80 字（英文），不重述維度表。
- 契約文字不引用本 repo `docs/` 下的研究檔（可攜性規則）；研究結論只進 plan 的 Current State Evidence。

## Out of scope
- 對抗者的攻擊目錄本身；讀者維度的增刪。

## Open questions
- none
