# 記憶步驟提前到分支結束前、散文釘規則 — 我試了什麼、結果如何

2026-09-05 在乾淨副本（短 sha `de38277a`）上試的。

## 你要的東西，逐條核對

### 1. 一個新 change 走完流程後，`git log <branch-end reviewed_sha>..HEAD` 只有 review-only commit 與關閉 intent 的 commit
- **我怎麼試的**：這個 change 本身就是它自己的第一個樣本（計畫裡寫明），所以我直接對這條分支跑
  `git log e895fbb3..HEAD --format='%h %s'`，看現在的樹長什麼樣。
- **結果**：印出 20 筆 commit，從「intent confirmed」一路到「chore(loom): dispatch review wave-end:1」，
  裡面還有正常的 feature／test／docs commit，不是只有兩筆。
- **證據**：指令輸出（20 行 log，含 `de38277a`、`b2f4e56f`、`08904fd1` 等）。
- **判定**：**尚未（not-yet）**——這是預期中的，因為第二個 wave（release plumbing 1.3.1 版號＋這個
  change 自己的記憶步驟 W2-02）還沒做。要驗證這條，得等分支真正結束（branch-end）那次才跑
  `git log <branch-end reviewed_sha>..HEAD`，屆時才應該只剩下 review-only 與關閉 intent 兩種 commit。
  現在看到的 log 形狀不是失敗，是「還沒到那一步」。

### 2. build 站與 ship 站各有一句寫明記憶步驟位置的話，且有站文字測試釘住
- **我怎麼試的**：在 build 的說明文件裡找「記憶」相關段落，在 ship 的說明文件裡也找；然後跑對應的
  自動測試。
- **結果**：build 文件裡新增了一段「6.5 記憶步驟——在計畫的最後一次檢查點之前」，寫明畢業探針與
  記憶庫條目要在最後一個 wave 整合完、下一次審查前完成；ship 文件裡的「記憶」章節則說清楚這件事
  已經在 build 做完了，ship 只留尾標與問題。跑
  `pytest loom-code/scripts/test_build_station_text.py loom-code/scripts/test_ship_station_text.py`
  → **16 個測試全過**。
- **證據**：16 passed（測試名見證據欄：`test_build_station_text.py`、`test_ship_station_text.py`）。
- **判定**：**做到了（works）**。

### 3. adversary.md 與 engineering-baseline.md 各有一句散文釘規則（肯定動詞、無否定詞、正反自測），有測試釘住
- **我怎麼試的**：分別在兩份文件裡搜規則句子，再跑對應測試，並數了字數。
- **結果**：兩份文件都各有一句寫明「釘住一句散文的測試必須在被釘字句前有肯定動詞、同句不可有否定
  詞、且要有一個肯定範例與一個被拒絕的否定範例的正反自測」。跑
  `pytest loom-code/scripts/test_prose_pin_rule_text.py loom-code/scripts/test_reviewer_agent_single_contract.py loom-code/scripts/test_engineering_baseline_reference.py`
  → **73 個測試全過**。字數：adversary.md 內文 593 字（帽 600）、engineering-baseline.md 內文 1322 字
  （帽 1500），都在既有字數帽內。
- **證據**：73 passed；字數計算用 Python `split()`（測試名見證據欄：
  `test_adversarymd_prosepinsentence_present`、`test_engineeringbaselinemd_prosepinsentence_present`、
  `test_sentencepinsproserule_negatedsynthetic_rejected`）。
- **判定**：**做到了（works）**。

### 4. build 站 §4 與 §5 有可複製的尾標檢查命令；用故意漏尾標的測試 commit 在沙盒證明能抓到
- **我怎麼試的**：把 build 文件裡 §4 的單筆檢查指令、§5 的迴圈指令原封不動抄出來，另外開一個全新的
  沙盒 git 倉庫，造兩筆 commit——一筆帶 `Task: T1` 尾標，一筆不帶——分別套用兩條指令。
- **結果**：§4 指令對帶尾標的 commit 印出「trailer OK」，對沒帶的印出「MISSING Task trailer」；
  §5 迴圈對整段範圍跑一次，準確印出「no Task trailer: <沒帶尾標的 commit>」，帶尾標那筆沒被列出。
- **證據**：沙盒倉庫的指令輸出（兩筆 commit：`56f98fd6…`帶尾標、`00bbc79f…`不帶尾標，指令抓到了後者）。
- **判定**：**做到了（works）**。

### 5. `loom_checker.py --list-rules` 規則數不變（27）
- **我怎麼試的**：跑 `python3 loom-code/scripts/loom_checker.py --list-rules | wc -l`。
- **結果**：27。
- **證據**：指令輸出 `27`。
- **判定**：**做到了（works）**。

## 額外驗證（超出五條 Acceptance，但屬於這次 wave 的證據要求）
- W0-01 對抗探針檔案（`test_abuse_memory_step.py`）單獨跑：10 個測試全過。
- 全套套件 `pytest loom-code/scripts/ scripts/ .claude/hooks/ -q -n auto`：**1376 個測試全過，2 個跳過，
  1 個預期失敗（xfailed）**。那 2 個跳過，就是第 4 個 wave 任務（W1-04）新加的兩個「已畢業」探針——
  它們原本會對這次改動自己的文件誤判成別的 change 的檔案；修好之後，只要 2026-09-03 那個 change
  被標記「已關閉」，這兩個探針就會自動跳過不跑，不影響你能不能用這個改動；等分支真正結束、
  intent 被關閉，它們會恢復跑但已經沒有東西可測。
- `pytest loom-design/scripts/`：182 個測試全過、1 個跳過。

## 對你既有的資料做了什麼

沒有——這次改動只碰了 loom-code 這套流程本身的說明文件、測試檔案，跟這個 change 自己的計畫／
證據文件。沒有動到你專案裡任何既有的原始資料或程式碼。

## 我決定了什麼（幫你做的選擇）

- **這個 change 拿自己當第一個樣本**——計畫寫明由 agent 決定：因為 Acceptance 第 1 條要求「一個
  新 change」的分支結束 log 長什麼樣，最直接的證明方式就是讓這次改動自己走一遍新流程；代價是
  第 1 條現在只能報告「還沒到那一步」，要等第二個 wave 做完才能真的驗證。
- **W1-04 是事後補上的任務，不在原計畫裡**——做 W1-03 時發現既有的兩個「畢業探針」（graduated
  probes）會把這次改動自己的文件誤判成別人的檔案而報紅；agent 決定加開一個任務，讓這兩個探針
  在對應的舊 change 標記「已關閉」時自動跳過，而不是刪掉它們。代價是：如果那個舊 change 之後被
  重新打開，這兩個探針會自動恢復檢查。
- **W1-02 的標題文字和計畫寫的不完全一樣**——計畫任務名稱寫「build：分支結束檢查點之前的記憶步驟」，
  實際寫進文件的標題是「6.5 記憶步驟——在計畫的最後一次檢查點之前」，字面不是逐字對應（用「計畫
  的最後一次檢查點」取代「分支結束檢查點」），但意思一致；沒有測試會因為這個字面差異而失敗，只是
  提醒你：如果你之後要搜這段文字，關鍵字要對得上實際標題，不是計畫裡的任務名稱。
- **散文釘規則放進 adversary.md 既有段落旁邊**——計畫寫明由 agent 決定：因為原本「You own」那段
  已經頂到六句上限，新規則被放到「三段式命名」那句旁邊，而不是塞進滿格的那段。
- **這次審查（review.json）目前還沒有任何被駁回（dismissed）的重大以上發現**——`open_findings` 與
  `verdicts` 都是空的，代表目前為止沒有審查者提出過嚴重度 important 或以上、又被駁回的問題可以
  在這裡列給你看；如果之後這次 wave-end 的對抗或審查跑出這類發現並被駁回，這份報告目前這一版
  不包含它。

## 你可能沒注意到、但該問一下的事

- 這個改動的「完工」定義本身要等第二個 wave（版號 1.3.1 與這個改動自己的記憶步驟 W2-02）做完
  才算數；現在你看到的只是 wave 1 結束後的中途快照，Acceptance 第 1 條要等分支真正結束時才能
  真的打勾。
- 兩個「已畢業」探針目前用「跳過」而不是「刪除」來繞開這次改動撞到舊 change 的問題；如果你以後
  重新打開 2026-09-03 那個舊 change，這兩個探針會自動恢復檢查——這是設計好的行為，但值得你知道。

---
**各文件的語言規則是否有守住**（僅供追蹤，識別碼只放在各自的證據欄）：
- 計畫（plan.md）：英文段落與中文對話段落分開放，符合規則。
- 意圖（intent.md）：中文書寫，符合規則（此文件本就用使用者語言）。
- 審查紀錄（review.json）發現文字：目前為空，尚無 Conventional Comments 標籤可核對。
- 證據（沙盒指令輸出、pytest 摘要行）：全部英文。
- 探針／測試檔案的說明字串（docstring）：抽查 `test_abuse_memory_step.py`、
  `test_prose_pin_rule_text.py` 皆為英文。
- 測試名稱：抽查皆符合 `test_<單元>_<狀態>_<預期>` 形狀（見上方各段證據欄的具體函式名）。
- Commit 訊息：抽查 `08904fd1` 為英文。
