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
- 給「關 intent」一條在閘下推得出去的路：`closed` 由 ship 站在 merge 後寫入，且該 commit 能通過 push 閘（做法由 plan 決定：例如 push 閘對「只動 intent status 行」的 commit 放行、或把 closed 併進下一個 change 的 review-only commit）；同時 intake 對 `closed` 的 intent 要明確擋（那個 change 已經完成，不可再進 write-plan）。
- 契約文法加 `closed <date> — PR #<N>`，模板註解與 checker 同步；repo 自檢測試改成對「已 closed 的 change」預期正確的擋法。
- `push.dispatch-covers-tasks` 的豁免集合與 `changed_paths` 共用同一個來源（scaffold 自己寫的那組檔）。
- 本 change 自己跑完後，把 checkpoint 的實際 commit 數、派工數、輪數記進 evidence，寫成**建議**（不是決議）；係數要不要改，kouko 決定留到看過第二、三個真實 change 再說。

## Acceptance
1. 在一個乾淨的 clone 裡，把上一個 change 的 intent 狀態改成 `closed 2026-09-03 — PR #780` 並用 ship 站寫的方式 commit，然後 `git push` 這個分支：push 閘放行（不需要任何人用 `!` 繞過），而對那個 intent 跑 write-plan 的 intake 會被擋並說明「這個 change 已關閉」。
2. `loom_checker.py --list-rules` 印出的 intent status 文法含 `closed`；`loom-code/scripts/` 與 `scripts/` 的整包測試在本機與 CI 都綠（含對 repo 自己 change 的自檢測試）。
3. 在一個乾淨的 clone 裡只重跑 `codex_scaffold.py --repo .`（刷新 `.codex/hooks/` 副本）並 commit，不帶 `Task:` trailer：`loom_checker.py push` 不再因 `push.dispatch-covers-tasks` 擋這個 commit。
4. 本 change 的 evidence 裡有一張表：本 change 每個 checkpoint 實際產生的 commit 數、派工數、審查輪數，以及 `git rev-list --count` 的總 commit 數，對照 #771 replay 的 34／31，一行**建議**「係數看起來要不要改、改哪一種」——決定留到第二、三個真實 change 之後（kouko 2026-09-03）。
5. 三個 plugin 的版本號各 bump 一次（loom-code 1.0.1 起），裝置端 `claude plugin update` 後 `loom_checker.py --list-rules` 是新版。

## Constraints
- 不改 27 條規則的語意，只改文法與豁免集合的來源；push 閘不加 waiver 機制（設計原則：閘門重算、不信宣稱）。
- 不動 `.codex/hooks/loom-checker` 的 command 字串（Codex 的 trust 綁 hook 定義）。
- PR 的 merge 動作留給 kouko 親按（kouko 2026-09-03）；agent 只做到 push 與開 PR。
- 六個測試 nit（R24-O2、R28-O2、R30-O1..O3）順手一起清；不做別的重構。

## Out of scope
- checkpoint 係數本身的修改（這次只量，不改）。
- Codex `/hooks` 授權畫面的真人實測、`~/.codex/requirements.toml` 免授信。
- 多人 repo 的作弊防護；loom-design 單獨安裝。
- self-test／reviewer 重跑整包測試的耗時優化。

## Open questions
- 「關 intent 推得出去」的具體做法要在 plan 裡選：push 閘對 intent-status-only commit 放行，還是把 closed 併進下一個 change 的 review-only commit？（agent-decided，plan 記理由）
