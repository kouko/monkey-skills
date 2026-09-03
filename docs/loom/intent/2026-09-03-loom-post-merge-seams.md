# loom 1.0 merge 後的接縫：關 intent 推得出去、契約認得 closed、scaffold 副本不算 gate、checkpoint 成本量出來
originator: kouko
kind: engineering
needs-design: yes — (a) 會改 loom-code/contract/templates/**（本 repo 宣告的 interface surface：intent 模板的 status 註解要加 closed）；engineering，決策點②不跑
status: confirmed 2026-09-03

## Problem
loom 1.0 合併後第一次在真 session 用它，馬上撞到三條它自己的接縫，還有一項當初留到 merge 後量的成本：
- ship 站第 6 步規定「merge 後把 intent 改成 `closed`、commit」，但 push 閘要求每次 push 的 HEAD 必須是只動 review.json 的 review-only commit、主幹又 fail-closed，所以那個收尾 commit 在自己的閘下推不出去（PR #781 的 push 被 `push.review-only-head` 擋下，只能由使用者 `!` 親推）。
- 契約的 intent `status` 文法只認 `open | confirmed <date> | withdrawn`，沒有 ship 站會寫的 `closed <date> — PR #N`；把 intent 改 closed 後，repo 自檢的測試（對自己的 change 跑 intake）紅了（PR #781 CI）。
- `push.dispatch-covers-tasks` 把 scaffold 寫進 `.codex/hooks/contract/` 的副本算成 gate，純刷新副本的 commit 也要 `Task:` trailer；`changed_paths` 已對同一組檔豁免，兩處規則不一致（上一個 change 為此改寫過一次歷史）。
- 每個 checkpoint 固定三個 commit（派工記錄／checkpoint 工件／review-only），#771 replay 因此 34 對 31；當初裁定 merge 後用真實 change 量了再決定。這個 change 就是第一個真實樣本。

## Proposed outcome
- 「關 intent」改在 merge 之前做（kouko 的設計，2026-09-03）：ship 站 push、開 PR 拿到號碼後，在分支上 commit `status: closed <date> — PR #<N>`，再補一個只動審查記錄的 commit 讓 push 閘照舊規則放行，closed 隨 merge 落到主幹；PR 沒 merge 則 closed 只留在分支上。intake 對 `closed` 的 intent 要明確擋（那個 change 已完成，不可再進 write-plan）。
- 契約文法加 `closed <date> — PR #<N>`，模板註解與 checker 同步；repo 自檢測試改成對「已 closed 的 change」預期正確的擋法。
- `push.dispatch-covers-tasks` 的豁免集合與 `changed_paths` 共用同一個來源（scaffold 自己寫的那組檔）。
- 本 change 自己跑完後，把 checkpoint 的實際 commit 數、派工數、輪數記進 evidence，寫成**建議**（不是決議）；係數要不要改，kouko 決定留到看過第二、三個真實 change 再說。

## Acceptance
1. 在一個乾淨的 clone 裡，照 ship 站寫的順序（PR 號碼已知 → commit intent `closed <date> — PR #<N>` → 關 intent 的 commit 也照常由兩個 fresh reviewer 機器審過、我不看 diff → 只動審查記錄的收尾 commit）做完後 `git push` 這個分支：push 閘放行（不需要任何人用 `!` 繞過、不需要新規則）；反例：跳過那輪審查、直接把審查記錄指到關 intent 的 commit 再推，push 閘擋；關 intent 的 commit 多改任何一個字再推，push 閘也擋（kouko 決定 A，2026-09-03），而對那個 intent 跑 write-plan 的 intake 會被擋並說明「這個 change 已關閉」。上一個 change（2026-09-02-simple-loom-flow，已合併但仍 confirmed）由本 change 的 diff 順手改成 closed。
2. `loom_checker.py --list-rules` 印出的 intent status 文法含 `closed`；`loom-code/scripts/` 與 `scripts/` 的整包測試在本機與 CI 都綠（含對 repo 自己 change 的自檢測試）。
3. 在一個乾淨的 clone 裡（Claude Code 這一側，也就是有 plugin 正本可比的情況）只重跑 `codex_scaffold.py --repo .`（刷新 `.codex/hooks/` 副本）並 commit，不帶 `Task:` trailer：`loom_checker.py push` 不再因 `push.dispatch-covers-tasks` 擋這個 commit；而把副本裡任一檔改一個字、多放一個檔、刪掉一個檔、或只改檔案權限再 commit，同一條規則照樣擋。（反例由 round 2 審查者要求補上、round 3 補刪檔與權限兩種，2026-09-03）
4. 本 change 的 evidence 裡有一張表：本 change 每個 checkpoint 實際產生的 commit 數、派工數、審查輪數，以及 `git rev-list --count` 的總 commit 數，對照 #771 replay 的 34／31，一行**建議**「係數看起來要不要改、改哪一種」——決定留到第二、三個真實 change 之後（kouko 2026-09-03）。
5. 三個 plugin 的版本號各 bump 一次（loom-code 1.0.1 起），裝置端 `claude plugin update` 後 `loom_checker.py --list-rules` 是新版。
6. 上一輪留下的五個測試小瑕疵（R24-O2、R28-O2、R30-O1、R30-O2、R30-O3）各自有一個改過的測試或註解可以指出來，整包測試仍綠；其中 R28-O2 的目標程式已在上一輪 round 30 改寫時消失，記為「不需修」即可（round 4 冷讀發現，2026-09-03）。（由 Constraints 升為 Acceptance，round 2 審查者要求，2026-09-03）

## Constraints
- 不加新規則、不放寬任何規則、push 閘不加 waiver 機制（設計原則：閘門重算、不信宣稱）；文法與豁免集合的來源可改。（2026-09-03 kouko 改設計：closed 在 PR 開出、號碼已知後就在分支上寫，隨 merge 一起落主幹。）**2026-09-03 kouko 決定 A**：允許把兩條既有規則**加嚴**——審查裁定要記「審的是哪個 commit」且必須對到被推的那個 commit；關 intent 的 commit 由 checker 重算「只改那一行」——原本「不改 27 條規則語意」的寫法改成上面這句。
- 不動 `.codex/hooks/loom-checker` 的 command 字串（Codex 的 trust 綁 hook 定義）。
- PR 的 merge 動作留給 kouko 親按（kouko 2026-09-03）；agent 只做到 push 與開 PR。
- 五個測試 nit（R24-O2、R28-O2、R30-O1、R30-O2、R30-O3）順手一起清；不做別的重構。（原寫「六個」，數錯）

## Out of scope
- checkpoint 係數本身的修改（這次只量，不改）。
- Codex `/hooks` 授權畫面的真人實測、`~/.codex/requirements.toml` 免授信。
- 多人 repo 的作弊防護；loom-design 單獨安裝。
- self-test／reviewer 重跑整包測試的耗時優化。

## Open questions
- none（原本的「關 intent 推得出去怎麼做」已由 kouko 2026-09-03 決定：merge 前在分支上寫）
