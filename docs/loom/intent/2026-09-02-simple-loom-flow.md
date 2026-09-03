# loom 重設計：讓只有基本軟體知識的使用者也能得到高品質實作
originator: kouko
kind: product
needs-design: yes — 多站、多 artifact、多 plugin 的狀態與互動要重定義，現有 spec 不存在（條件 b）
evidence: [docs/loom/2026-09-02-simple-loom-flow/evidence/]
status: confirmed 2026-09-02   # 重確認×3：跨 vendor 改選配、Acceptance #6 對象改站文件、Acceptance #2 切換日重授信除外（kouko 2026-09-02）

## Problem
loom 現在太重：三個 plugin 共 36 個 skill、約 38 種文件形狀、113 個專有名詞，每個 session 開頭要塞進五千多字的說明。重量集中在「治理」——拆計畫、批次審查、閘門標記——而不是在幫使用者把東西做好。每次出事故就長一個新機制，沒有准入規則，砍了也會長回來。

受影響的是 loom 的使用者：他們被要求在 spec、plan、審查批次、豁免這些自己看不懂的地方做決定，而真正該由他們決定的「我要什麼」「做到了嗎」反而沒有固定的位置。維護者（也是使用者）每次改動要面對五個表面的版本同步與一堆互相引用的散文契約。

## Proposed outcome
loom 的目標重新定為：假定使用者只具備基本軟體工程知識，盡量自動化判斷並維持高品質的實作，避免讓使用者做過多的決策。

做法：每個 change 從一份人寫的 intent 開始，視需要經 spec、plan、實作、機器審查到 PR；使用者只在「要什麼」「可見的操作與反應」「做到了嗎」三處回答，其餘決定由 agent 做並記錄理由。品質來自機器：寫的 agent 和審的 agent 分開（至少兩個 fresh-context reviewer；用不用第二家模型由使用者選，機制在同一個 change 裡至多建議一次，答案記住後不再問）、沒寫過的 agent 照 Acceptance 盲跑、另一個 agent 試著弄壞它、每個事故變永久 eval。新機制必須同時有回歸 eval 且淨數不增。舊的 plan、spec、brief 原地封存，硬切換。

完整設計見同名資料夾的 concept-model.md（v10，經六輪冷讀、兩輪 Codex、一輪 opus 邏輯審、一輪紅隊與一次儀式成本量測）。

## Acceptance
1. 一個只有基本軟體知識的人，能用白話描述想要的功能，在不讀 spec、plan 或 diff 的情況下，只回答「這是我要的嗎」「這個操作會這樣反應對嗎」「做到了嗎」三種問題，就拿到一個測試通過、經兩個獨立 reviewer 審過、有盲跑報告的 PR。
2. 同一個任務在 Claude Code 和 Codex CLI 上走出來的檔案、決策點、閘門一致；Codex 只多一次每 repo 一次的 `/hooks` 授信（切換日既有 Codex repo 因 hook 定義改變的一次性重授信除外）。
3. 一個 engineering 的 change（例如抽共用 helper）從頭到 PR，流程停下來等使用者的**決策點** ≤ 2；product 的 change ≤ 3。每個決策點內問幾個問題不限（訪談可以問到清楚為止）；限制的是「不問使用者看不懂的問題」（spec 品質、plan 拆法、審查裁定），不是問得少。
4. 拿三個 2026-08-20 之後真實合併的 change 重走一遍，commit 數、審查派工數、人類決策點都不多於今天的實際數字。
5. skill 數從 36 降到 18 以內，session-start 注入字數減半以上，每個 change 產生的文件形狀 ≤ 5 種。
6. 一個沒看過 loom 的 agent，只拿該站的 SKILL.md（落地後），能在 15 分鐘內對一個給定任務說出會產生哪些檔、誰決定什麼、哪個 checker 在何時擋、審查何時跑，且沒有需要猜的規則。零猜測優先於 15 分鐘。concept-model.md 本身只記錄冷讀結果（v10：25 分鐘、零猜測），不作驗收。
7. 新增任何機制的 PR 若沒有回歸 eval 或沒有刪／併既有機制且沒有 budget 例外行，CI 會紅。

## Constraints
- 維持三個 plugin：loom-design（要什麼、為什麼）、loom-code（怎麼做）、loom-workflow（工具）；loom-code 必須能獨立安裝使用。
- 不要求使用者跑任何 init；站在第一次碰到 repo 時自己建需要的東西。
- 不做 git hook；決定性層靠 host hooks（Claude Code plugin hooks、Codex repo 級 hooks.json）與可選的 CI。
- 決定性層擋的是漏步驟，不宣稱擋有目標的 agent。
- 對 Codex 的行為以真機實測為準，不以文件為準。
- 硬切換：不維護新舊格式並行。

## Value case
GO。理由：現況的重量已經讓維護者自己都覺得 heavy；儀式成本量測顯示三個真實 change 合計 126 個 commit、94 次審查派工、40 個文件；batch 審查機制 11k 行程式碼在 8 天內出了 5 個修正版、真實採用 6/268、找不到任何真實的淨節省。這不是優化，是止血。

## Out of scope
- 遷移計畫的細節（哪個 skill 先改、舊測試怎麼處理）——屬於這個 change 的 plan。
- 多人 repo 的作弊防護（branch protection、CODEOWNERS、bot 身分）——另立 intent。
- loom-design 缺哪些具體設計能力——另立 intent。
- `~/.codex/requirements.toml` 能否讓 hook 免授信——未驗證，另立 research。
- decision-map 的 grilling／research／prototype 三型 ticket 的重設計。

## Open questions
- checkpoint 門檻（8 檔或 400 行）與 plan 深度 ≤ 5 都是實驗預設，要用歷史分支 replay 量過才固定。
- 名詞計數規則下的基線是 36（Codex 數的），原目標 ≤ 40；規則本身可能還要調。**2026-09-03 user-decided：目標改為 ≤ 60（實測 61 → 已達；40 是設計前的估計值，未經量測）。合併後第一次真跑時記錄哪些名詞讓使用者卡住，作為下一輪裁剪的證據。**
- 跨 vendor reviewer 每次約 5 分鐘、11 萬 token，成本是否可接受要用幾個真實 change 量。
- 問題三型判準（要什麼／可見行為／做到了嗎＋單向門後果形）的邊界以實際使用回饋調整；量測面＝每 change 記錄的決策點數與岔路提問數（concept-model §11），判定住在 review 的 user-judgment-leak 鏡頭與 write-plan 的 one-way-door reference，改文字不改程式（kouko 2026-09-02）。
- 對抗 artifact 的內容無機械約束（空殼檔也算合格）；可能的便宜硬化＝要求 artifact 在刻意弄壞的樹上必須失敗（mutation 式自證）。W1 對抗第四輪記錄，待實際使用後決定。
- checkpoint 的固定成本＝每次三個 commit（派工記錄、checkpoint 工件、review-only）；#771 真 replay 因此 34 commit 對今天 31（Acceptance #4 該格不合格，派工與決策點合格）。可能的便宜硬化＝派工記錄與 checkpoint 工件併進同一 commit、或以 wave 為單位記錄一次。W4-03 記錄，落地後用真實 change 量再決定。**2026-09-03 user-decided：本 change 不動，Acceptance #4 該格如實記為未達；merge 後以真實改動量過再調。首跑安排（user-decided 2026-09-03）：merge 後第一個 change 就是這條「checkpoint commit 係數」，同時作為 v10 在真實 Claude Code session（plugin 1.0.0 已裝）內的首次完整實走；本 change 內的實走全在臨時 repo 由 subagent 執行，未在真 session 走過。**
- `push.dispatch-covers-tasks` 把 scaffold 寫進 `.codex/hooks/contract/` 的副本算成 gate（`changed_paths` 已豁免 scaffold 自己的檔，這條規則沒有），所以純刷新副本的 commit 也要 `Task:` trailer；ship 前撞到一次（2026-09-03）。merge 後第一個 change 順手對齊兩處的豁免集合。
