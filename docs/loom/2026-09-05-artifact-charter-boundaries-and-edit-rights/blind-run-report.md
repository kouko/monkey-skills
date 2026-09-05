# loom 文件憲章：內容邊界與定稿後修改權 — 我試了什麼、發生了什麼

於 2026-09-05 在乾淨副本試跑，版本 dfb78af1e3ebf8728cb5beeaf58c276653130311（取代上一份只驗到第 0 波的報告）。

這次驗收涵蓋到第 1 波前兩個任務：文件憲章表（第 0 波）、plan 三欄字數帽（W1-01）、plan 定稿後可改哪些地方（W1-02）。review.json 的累積規則（W1-03）、站文字改寫（第 2 波）、A/B 縮寫證據與 Codex 鏡射（第 3 波）都還沒蓋，第 4、5、6 條驗收因此還不到能試的時候。

## 逐條驗收

### 1. 打開一張表，每種文件一列，四欄都不空
- **怎麼試的**：跑 checker 的 `charter` 指令
- **發生了什麼**：印出一張表，intent、spec、plan、review、blind-run-report、memory、kickoff-defaults、dispatch 共八列，每列「回答什麼／給誰讀／必須寫／不得寫且指向哪裡／定稿點／定稿後允許的變動」六欄都有內容，沒有空格；退出碼 0
- **證據**：`python3 loom-code/scripts/loom_checker.py charter`（本地執行，輸出見上）
- **判定**：works — 表存在且六欄齊全

### 2. 拿舊 dbt 專案的長 plan 給 checker，指出事後日誌與 landed task 該搬去哪
- **怎麼試的**：那份 3,945 字的真實 plan 不在這個專案裡，我在乾淨的暫存 git 倉庫裡自己搭了一份替身：建一份帶憲章戳記的 plan、用 `docs(loom): plan <id>` 這個標準訊息 commit 起來當作「定稿點」，然後在工作區裡追加一筆帶日期的「LESSON」事後日誌到 Risks 段，再追加一個帶 `landed: <sha>` 標記的新任務，跑 `plan-edits` 指令看它怎麼反應
- **發生了什麼**：擋下，印出兩行：「T2 added; goes to spec」（新追加的任務該搬去 spec）、「Risks section changed; goes to review」（事後日誌該搬去 review）；退出碼 1
- **證據**：替身倉庫的 plan.md 與 `python3 loom_checker.py plan-edits 2026-01-01-standin-change` 的輸出（本地執行，見上）
- **判定**：works — 但這是我自己搭的替身資料，不是真的那份 dbt plan，請當作示範而非原始驗收；另外我觀察到一個小落差：帶 `landed: <sha>` 的追加任務被指向「spec」，但憲章表寫「landed 的 commit sha 該住在 dispatch」，這條規則目前不分「一般追加任務」和「帶 landed 標記的追加任務」，兩種都算「spec」——是否要緊由你判斷，我已在下面的發現一併列出

### 3. 三欄都在帽內的 plan 通過、超帽被擋
- **怎麼試的**：先用這個變更自己的 plan.md（三欄都在帽內）跑 `plan` 指令；再把其中一個任務的 Test 欄改寫成 7 條情境敘述（133 字，遠超 40 字帽），同一份指令再跑一次
- **發生了什麼**：帽內版本退出碼 0（通過）；擴寫版本擋下，印出「BLOCK plan.field-caps: W0-01.Test 133 words, cap 40」，點名是哪個任務、哪一欄、超了多少
- **證據**：兩次 `python3 loom_checker.py plan <path>` 的輸出（本地執行，見上）
- **判定**：works

### 4. 冷派 implementer 給縮寫版與原版 plan 各一次，比較 NEEDS_CONTEXT 次數
- **怎麼試的**：查證據資料夾
- **發生了什麼**：`evidence/` 目錄下只有對抗測試探針（`probes/`），沒有 `ab-plan-original.md`、`ab-plan-charter.md`、`ab-implementer-runs.md` 這些第 3 波要交的檔案
- **判定**：尚未建置 — A/B 證據是第 3 波（W3-01）的工作

### 5. 假 finding「plan 少列一個測試情境」冷派 reviewer，不算 omission；REQ 重述的樣本標 inconsistency
- **怎麼試的**：查 `lenses.md` 的 omission 定義有沒有改窄
- **發生了什麼**：`lenses.md` 裡 omission 的定義還是舊的通用寫法，沒有「implementer 拿那張單無法開工」這句收窄語；這是第 2 波（W2-02）的工作
- **判定**：尚未建置

### 6. review.json 追加第二輪時，只有允許的節點能長，允許替換的節點被擋
- **怎麼試的**：找 `review.round-append-only` 一類規則
- **發生了什麼**：規則清單裡沒有，第 1 波（W1-03）尚未開工
- **判定**：尚未建置

### 7. 整包測試通過，write-plan 的 SKILL.md 仍在字數帽內
- **怎麼試的**：跑 `python3 scripts/run_package_tests.py loom-code/scripts/ scripts/ .claude/hooks/ -q -n auto --then loom-design/scripts/ -q`；另外單獨重跑 write-plan 字數帽的測試
- **發生了什麼**：主段 1673 通過、5 略過、1 預期失敗（xfail）；附加段 182 通過、1 略過；write-plan 字數帽測試 44 通過
- **證據**：上面指令的完整輸出（本地終端機）
- **判定**：works

## 對你既有的資料做了什麼

沒有 — 這次改動只碰 loom-code 自己的契約檔、checker 程式與測試檔，也沒有寫入我自己搭的替身倉庫以外的任何資料；沒有讀寫任何你既有的專案資料。

## 我決定了什麼（含被駁回的重大以上發現）

沒有 — 這個檢查點（W1-02 之後）目前還沒有被駁回的重大以上發現；每個選擇不是你的就是被逼的。第 0 波審查提出的 7 個發現（2 個 fatal、5 個 important）在那一輪的修正裡全部修掉，沒有一個保留不修。

## 我不確定你是否想要的

- 第 2 條驗收目前只用我自己搭的替身資料驗過，不是真的那份 3,945 字的 dbt plan；如果你想看真的那份跑起來什麼樣，需要把那份檔案帶進來試。
- 帶 `landed: <sha>` 標記的追加任務目前和一般追加任務一樣被指向「搬去 spec」，沒有單獨指向憲章表寫的「dispatch」；這是否需要更精細的區分，由你判斷。
- 第 2、3 波（review.json 累積、站文字改寫、A/B 縮寫證據、Codex 鏡射）都還沒做，Acceptance 4、5、6 要等這些波做完才能真的驗。
