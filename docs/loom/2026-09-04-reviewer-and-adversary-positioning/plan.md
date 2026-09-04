# reviewer／adversary 契約定位段＋讀者 finding 編探針＋角色觸發圖 — plan
intent: 2026-09-04-reviewer-and-adversary-positioning@20658a36

## Current State Evidence
- Forward（契約）：`loom-code/agents/reviewer.md:6-11` 開頭是 `> **Role**: judge…do not modify`（1255 字），`loom-code/agents/adversary.md:6-10` 是 `> **Role**: attacker…`（446 字）；兩檔都沒有一句說「你負責哪一種真相」，邊界只能從 reviewer 的維度表（`:29-60`）與 adversary 的 per-type 配方（`:18-34`）歸納。
- Forward（修正輪）：review 站 SKILL.md `§8a`（`loom-code/skills/review/SKILL.md:414-421`）只指向 `loom-code/skills/review/references/fix-rounds.md`（434 字）；該檔 `## Probes are not re-run here`（`:33-37`）說修正輪不重跑探針、push 會重跑——沒有一句說讀者的可執行 finding 該由誰、在哪一輪變成探針。2026-09-04-checker-seams 的 wave-end finding 05（`--is-ancestor` ≠ first-parent）是臨時在 branch-end 由對抗者編成 `test_abuse_branch_end.py` case (1) 的，`review.json` 裡沒有規則依據。
- Reverse：讀 reviewer.md 的是 review 站 §2 派工（`loom-code/skills/review/SKILL.md:150-180`）與 fix-rounds 的 resumed reader；讀 adversary.md 的是 review 站 §4 與 build 站 §2 的探針先寫段（`loom-code/skills/build/SKILL.md:101-118`）。文字測試：`loom-code/scripts/test_review_station_text.py`（`:15-40`，已讀 reviewer.md 一處：docs-lint 段）、`test_station_summary_table.py`（九處站摘要表同步；本 change 不改站摘要行）。
- Data（研究）：`evidence/research-reviewer-adversary-roles.md`——讀與跑抓不同缺陷類別有量測（Mäntylä & Lassenius 2009：review 找到的缺陷 75% 不影響功能）；finding→回歸測試是既有慣例（Google／SQLite／detection-as-code）。`evidence/research-role-separation-ablations.md`——「讀者與對抗者拆成兩個 agent」沒有任何直接比較；最近的 ablation 是 AgentCoder（寫碼者≠寫測試者：HumanEval 71.3%→79.9%）與 Olausson 2023（自我批判 vs 獨立批判）。所以定位段措辭是「本流程的分工」，不是「業界共識」（intent Proposed outcome 4）。
- Data（README）：`docs/loom/README.md` 553 字、三節（Live layout／Frozen stores／Where a new change starts），是 CLAUDE.md 指定的「入口與完整站序」文件，繁中；docs-lint 為 none。角色觸發圖今天在對話裡用 `ascii-graph` 的 `seq` 生成器畫過（68 欄，payload 見 W1-02）。
- Boundary：不動 checker、不加規則、不動角色數與站摘要表；不動 `references/lenses.md`、`attack-catalogue.md`；不動 blind-runner 契約（它的邊界——使用者視角、Acceptance 逐條——已由自身文字給定）。契約文字不引用 `docs/` 下的研究檔（可攜性規則）。

## Task DAG

**W0-01 對抗者先寫探針**　after: —
- 檔：新增 `docs/loom/2026-09-04-reviewer-and-adversary-positioning/evidence/probes/test_abuse_positioning.py`（≥5 案例）。攻擊面：(1) reviewer.md／adversary.md 各有一段以 `You own` 開頭、≤80 英文字、不含 `docs/` 路徑引用；(2) reviewer 段含 reconciliation 三向（omission／overclaim／contradiction）且明說可引用 adversary 的執行證據、不自寫探針；adversary 段含 negative＋re-runnable＋不對帳；(3) fix-rounds.md 有一句把讀者 `important` finding 交給修正輪對抗者編成探針、且與 `Probes are not re-run here` 不矛盾（新探針是「寫並跑一次」，不是「重跑既有」）；(4) README 新節：每行 wcwidth ≤72、`blind-runner`／`reviewer`／`adversary` 三字都在、含「並行」與「先後」兩詞、payload 可重生同圖；(5) 兩段不含「industry consensus／業界共識」類措辭；(6) plugin.json 版本 > 1.2.0 且 CHANGELOG 有該版。實作前全紅、docstring 標 `RED until W1-0x`。
- 測：探針檔本身；記紅綠各幾條。
- 風：agent-decided——文字探針用 `re`＋`len(str.split())` 算字數（不可用 wc）、寬度用 `wcwidth`（repo 的 `ascii-graph-toolkit` 已依賴）；README 圖重生檢查以 `subprocess` 跑 `ascii-graph-toolkit/skills/ascii-graph/scripts/generate.py seq` 對 payload，比對輸出與檔中圖塊逐行相等。

**W1-01 兩段定位＋修正輪一句＋文字測試**　after: W0-01
- 檔：`loom-code/agents/reviewer.md` 在 `> **Role**: judge` 引言後加一段（≤80 字）：You own reconciliation——delivered vs what intent／plan／the text itself promised，雙向：omission、overclaim、contradiction；產出是 claim，由修正輪確認；reconciliation-first, not execution-free：可以引用對抗者已產出的探針與套件結果，但不自己寫探針；正向可執行的 RED 屬實作者。`loom-code/agents/adversary.md` 在 `> **Role**: attacker` 引言後加一段（≤80 字）：You own the negative——forbidden behaviour；證據可執行、可在乾淨樹重跑；不評設計、不對帳。兩段都寫 "in this flow"，不寫 industry。`loom-code/skills/review/references/fix-rounds.md` 在 `## Probes are not re-run here` 之後加一小段（≤60 字）：讀者的 `important` finding 若可寫成會跑的案例，本修正輪的對抗者把它編進本 change 的探針檔並記一筆 `probes[]`（`kind: adversarial`，本輪 scope），順手做、不另開站；這是新增一筆並跑一次，不是重跑既有探針。`loom-code/scripts/test_review_station_text.py` 加三測（兩段存在＋字數帽、修正輪句存在）。
- 測：W0-01 探針 (1)(2)(3)(5) 轉綠；新三測先紅。
- 風：agent-decided——句子放 fix-rounds.md 而非 SKILL.md §8a，因為 §8a 只是指標、程序在 reference（Acceptance 2 說「review 站的修正輪文字」，reference 屬 review 站）。reviewer.md／adversary.md 是 `skill` 型→checkpoint 帶 skill lens＋冷讀。

**W1-02 README 角色觸發一節**　after: W0-01
- 檔：`docs/loom/README.md` 在 `## Where a new change starts` 之前加一節「checkpoint 的三個驗證角色什麼時候被觸發」：一句說明三角色英文契約檔名（blind-runner／reviewer／adversary，另 implementer）與圖中縮寫；序列圖（`ascii-graph` `seq` 生成，participants `build`／`adv`／`impl`／`review`／`blind`／`rev x2`，九步：1 探針先寫、2 實作、3 checkpoint、4a 補攻、4b 盲跑、5 並行讀、6 verdict、7 修正、8 編探針、9 PASS）；步驟表（誰派誰、內容、同步性：4a∥4b 同時派且同樹並行要路徑限定 commit、禁 amend；5 等 4a／4b 落地才派、兩位互不可見；8 為 intent 1 新增）；一行小車道差異（跳 1、4b、5 只一位；4a 不省）；圖下方以摺疊或註記放生成 payload（JSON）與命令，供重生。
- 測：W0-01 探針 (4) 轉綠。
- 風：agent-decided——放 README 不放 concept-model：README 是 CLAUDE.md 指定的入口文件，concept-model 是已關閉 change 的工件。README 用繁中（docs-lint none、既有語言），英文名稱照契約檔名。

**W1-03 版本與 CHANGELOG**　after: W1-01, W1-02
- 檔：`loom-code/.claude-plugin/plugin.json` 1.2.0→1.2.1、`loom-code/CHANGELOG.md` 一則（三件事）；marketplace／README 版本表照既有測試同步（`test_sync_codex_manifest.py`、plugin version bump CI）。純文字改動 patch 版。
- 測：W0-01 探針 (6) 轉綠；整包 `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q -n auto` 綠。
- 風：改 skill 內容必 bump（marketplace 按版本發佈）；不動 loom-design。

## Questions asked
1 — what — 你要的是兩個驗證角色各自知道「自己負責哪一種真相」（對抗者＝不准發生的事、證據可重跑；讀者＝做的跟說的對不對得上，對帳為主可看執行證據）；讀者的重要可執行 finding 修正時由對抗者順手寫進探針；做完後冷讀 agent 能一句話說出邊界、修正輪文字有那句且有測試釘著、字數帽內、版本 bump；不動 checker、不加規則、不改角色數。對嗎？（答：對）
1 — consequence — 第二審查者用 codex？多花幾分鐘與額度；上一 change 它一輪抓 3 條全真（答：用）
1 — what — 事後追加：把對話裡畫的角色觸發序列圖寫進文件，未來 session 可回頭看（答：要；agent 選 `docs/loom/README.md`）

## Risks
1. 只有一個 wave 產出（W1），三個 task 檔案互斥：W1-01 與 W1-02 可平行（各自 worktree、`--no-ff` 合回）；W1-03 最後。W0-01 一個對抗者、工作樹直接做。
2. checkpoint：只有 branch-end 一次（delta 遠低於 8 檔／400 行，最後一波必審）。型別聯集：skill（agents/*.md）＋docs（README、fix-rounds.md）＋code（測試、plugin.json）＋evidence（探針）→ 讀者一位 codex＋一位 sonnet 各帶 skill＋docs＋code 三鏡；盲跑者對 skill 型做冷讀真任務（Acceptance 1：拿混合 finding 清單分邊界）＋ Acceptance 2–4 逐條；對抗者六類攻擊目錄冷讀兩段＋補攻探針。
3. 本 change 的 code 型 task（W1-01 的測試檔、W1-03 的 json）走探針先寫（W0-01），符合 build §2 新規則——上一 change 自己違規過，這次別再。
4. 同樹並行坑：branch-end 對抗者與盲跑者同時 commit——派工包寫「只路徑限定 commit、禁 amend」。
5. 定位段是散文規則，弱模型讀者會不會照做只能靠冷讀盲跑證明；措辭要「指向可查動作」（引用哪一筆 probes[]）不要「需判斷」。
