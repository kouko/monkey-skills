# loom 文件憲章：內容邊界與定稿後修改權 — 我試了什麼、發生了什麼

於 2026-09-05 在乾淨副本試跑，版本 a4276148（本輪重跑，取代舊報告在 36a71b29 那次；上一輪誤把八種文件寫成九種，這裡已更正為八種）。

這次驗收只涵蓋第 0 波：文件憲章表本身、checker 的 `charter` 指令、以及規則 `contract.charter-complete`。第 1～3 波（欄位字數帽、定稿後修改權規則、review.json 累積規則、站文字改寫、A/B 證據、Codex 鏡射）都還沒蓋，第 2、3、6 條驗收因此還不到能試的時候。

## 逐條驗收

### 1. 打開一張表，每種文件一列，四欄都不空
- **怎麼試的**：跑 checker 的 `charter` 指令
- **發生了什麼**：印出一張表，intent、spec、plan、review、blind-run-report、memory、kickoff-defaults、dispatch 共八列，每列「回答什麼／給誰讀／必須寫／不得寫且指向哪裡／定稿點／定稿後允許的變動」六欄都有內容，沒有空格；退出碼 0
- **證據**：`python3 loom-code/scripts/loom_checker.py charter`（本地執行，輸出見上）
- **判定**：works — 表存在且六欄齊全，且原本「九種」的錯字已修成「八種」

### 2. 拿舊 dbt 專案的長 plan 給 checker，指出事後日誌與 landed task 該搬去哪
- **怎麼試的**：找對應規則（如 `plan.field-caps`、`plan.edits-after` 之類）
- **發生了什麼**：目前規則清單裡沒有這類規則；這是第 1 波的工作，還沒做
- **證據**：`loom_checker.py --list-rules` 沒有 plan 相關規則；程式碼裡也搜不到
- **判定**：尚未建置 — 判斷「plan 裡哪些內容不該留」的規則還沒寫

### 3. 三欄都在帽內的 plan 通過、超帽被擋
- **怎麼試的**：同上，找欄位字數帽規則
- **發生了什麼**：同樣沒有這條規則，第 1 波尚未開工
- **判定**：尚未建置

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
- **怎麼試的**：跑 `python3 scripts/run_package_tests.py loom-code/scripts/ scripts/ .claude/hooks/ -q -n auto --then loom-design/scripts/ -q`；另外用 Python 的 `len(open(f).read().split())` 數 write-plan 的 SKILL.md 字數
- **發生了什麼**：主段 1656 通過、5 略過、1 預期失敗（xfail）；附加段 182 通過、1 略過；SKILL.md 字數 4,308（帽是 4,500）
- **證據**：上面兩條指令的完整輸出（本地終端機）
- **判定**：works

## 對你既有的資料做了什麼

沒有 — 這次改動只碰 loom-code 自己的契約檔、checker 程式與測試檔，沒有讀寫任何你既有的專案資料。

## 我決定了什麼（含被駁回的重大以上發現）

- 沒有 — 上一輪審查提出的 7 個發現（2 個 fatal、5 個 important）在這一輪之前的修正輪裡全部修掉了，沒有一個被駁回或保留不修：
  - 空/缺 `artifacts:` 對照表原本會靜默通過，現在會擋
  - 人讀表原本漏掉「回答什麼／給誰讀」兩欄，現在補上
  - plan 的「定稿後允許變動」清單原本沒窮舉到「非規格變更的修正」這一類，現在補了第五類
  - 舊報告寫在錯的版本（36a71b29），現在這份重新在 a4276148 跑過
  - `artifacts:` 註解原本沒說清楚它同時裝「逐次變更」與「常設」兩種憲章列，現在補清楚
  - 憲章欄位裡塞 `|` 或換行會讓表格畫面跑掉且不會被擋，現在會擋
  - plan 的「定稿後允許變動」清單宣稱窮舉，但有一次修正不屬於四類中任何一類，現在補第五類

## 我不確定你是否想要的

- 第 1～3 波（欄位字數帽、修改權規則、review.json 累積規則、站文字改寫、A/B 縮寫證據、Codex 鏡射）都還沒做，Acceptance 2、3、4、5、6 要等這些波做完才能真的驗。目前只能確認第 0 波（憲章表本身）站得住。
