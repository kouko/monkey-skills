# 小改動車道：一個旗標的 change 二十分鐘內結束 — 我試了什麼、發生了什麼

於 2026-09-04 在乾淨的專案副本（短 sha `e8d99de4`）上試跑，範圍是整個分支（branch-end）。

## 你要的東西，一條一條試

### 1. 落在預授權類別的 change 走完流程，只需一位讀者、免盲跑；跨出類別即擋
- **我怎麼試的**：借用這個 repo 自己的測試工具（`test_loom_checker_push.py` 裡搭臨時假 repo 的函式），造一個只碰「docs + 一個測試檔」的分支，review 記錄裡只放一位讀者的 PASS、沒有盲跑探針，跑 `loom_checker.py push`；接著在同一個分支再加一個非測試的 `.py` 檔，重跑一次。
- **發生了什麼**：第一次 exit code 0（通過）；加了非測試檔之後 exit code 1，並且明確印出「full lane」與差幾位讀者、是哪個檔逼出全車道。
- **證據**：
  - 小車道：`returncode: 0`
  - 全車道：`returncode: 1`，`stderr: BLOCK push.verdicts-ge-2: full lane: review round 1 carries 1 distinct reviewer(s) with a readable verdict; 2 required (loom-code/scripts/lane_acc1_helper.py is non-test code).`
- **判定**：works — 兩邊行為都對，訊息也點名是哪個檔把它推出小車道。

### 2. 修正輪只讀「這輪修正」，不重跑整個 checkpoint；不得跳出修正範圍提新意見
- **我怎麼試的**：只讀 `loom-code/skills/review/SKILL.md` 與 `references/fix-rounds.md`，把自己當成第一次看到這套流程的人回答。
- **發生了什麼**：
  - 修正輪的差異範圍＝「上一輪被讀過的那個 commit」到現在新增的修正 commit（不是回到最早那次通過的版本）；讀的人是同一位讀者被叫回來（不是換新人）。
  - 讀者不可以對修正範圍外的句子提新意見，除非那個修正把範圍外的東西弄壞了。
  - 探針（測試／對抗案例）不重跑；真正把關的是最後 push 時重跑一次。
- **證據**：`fix-rounds.md`「Delta: fix commits only」「Resume, do not replace, the reader」「Probes are not re-run here」三段原文。
- **判定**：works — 文字清楚，不用猜。

### 3. 只是措辭修正的意見記成 nit，不因它多開一輪；ship 前批次修完、不算新輪
- **我怎麼試的**：同樣只讀上述兩份文件的嚴重度定義段落。
- **發生了什麼**：判準是「後果」不是「位置」——會讓人照做出錯、或 checker／CI 依賴的事實錯了才算 important；用語、單位、同一件事兩種說法、讀起來不順，就算字面上不對，一律 nit。nit 永遠不會變成要處理的「未結事項」，也永遠不會多開一輪；ship 前把所有 nit 收成一個 commit，原本提意見的讀者一句話確認就算數。第三輪起（同一個 checkpoint）要先停下來，找更高階的人看設計是不是本身就錯了，而不是繼續修字句。
- **證據**：`SKILL.md`「Severity is by consequence, not by wording」整段；`fix-rounds.md`「Third round: stop fixing, look at the design」整段。
- **判定**：works — 兩份文件都不用猜。

### 4. 下一個小改動車道的 change，從確認到送出 PR ≤ 20 分鐘
- **我怎麼試的**：沒有下一個小改動 change 可試——這一條量的是「這個機制上線之後，未來某個小 change」的表現，這次跑的正是打造機制本身的那個大 change。
- **發生了什麼**：無法觀測。
- **證據**：無。
- **判定**：not yet — 要等下一個真的走小車道的 change 出現才能量。

### 5. gate 類型的 task，對抗者先於實作者派工、探針 commit 先於實作 commit
- **我怎麼試的**：只讀 `loom-code/skills/build/SKILL.md` 關於「檔案落在 `hooks/**` 或 `scripts/check_*`」該先派誰；再去看這次 change 自己的派工紀錄與 git 歷史。
- **發生了什麼**：文件說這類 task 要先派對抗者，讓其中一個攻擊案例當作實作者的 RED（先讓測試紅，再讓它變綠）。這次 change 的紀錄確實照做：對抗者（W0-01）派工時間 `2026-09-04T00:12:24+08:00`，早於實作者（W0-02）的 `2026-09-04T00:20:26+08:00`；探針 commit（`74a353d` test(loom): W0-01…，00:19:55）也早於實作 commit（`4c1ac02` feat(loom-code): W0-02…，00:38:14）。
- **證據**：`build/SKILL.md` 第 102-104 行原文；`review.json` 的 `dispatch[]`；`git log --format='%H %ci %s'` 兩筆 commit 時間戳。
- **判定**：works。

### 6. `docs-lint` 宣告了就不列風格意見；宣告 `none` 時風格意見最多是 nit
- **我怎麼試的**：`grep` `docs/loom/KICKOFF-DEFAULTS.md` 找 `docs-lint:` 那一行，再讀 `loom-code/agents/reviewer.md` 對應段落。
- **發生了什麼**：這個 repo 目前宣告 `docs-lint: none`（loom 文件現在是中文，還沒裝）；`reviewer.md` 寫得很清楚——有宣告 `docs-lint: <command>` 時，讀者完全不列任何風格意見（那支指令自己是風格閘、另外跑）；是 `none` 或沒寫時，風格類意見最高只能是 nit，不能是 important 或 fatal。
- **證據**：`KICKOFF-DEFAULTS.md:12`；`reviewer.md:93-99`。
- **判定**：works。

### 7. KICKOFF 寫 `second-vendor: ask` 時，決策點①要問那一句話、答案記在該次 change 的 review.json，小車道不問
- **我怎麼試的**：讀 `loom-code/skills/write-plan/SKILL.md` 與其 `references/second-vendor-ask-and-docs-lint.md`，找那句確切問句與答案該記在哪裡；再去看這次 change 自己的 `review.json`。
- **發生了什麼**：文件規定的問句是「這次要不要用 Codex 當第二位讀者？」，要記進該次 change 計畫的「Questions asked」清單，答案（`<cli>` 或 `none`）由 review 站寫進該次 `review.json` 頂層的 `second_vendor` 欄位；小車道因為只有一位讀者，這題完全不問，`second_vendor` 欄位也直接不寫（不是寫 `none`）。這次 change 本身是全車道，它的 `review.json` 確實有 `second_vendor` 欄位，值是 `"codex"`。
- **證據**：`second-vendor-ask-and-docs-lint.md`「## second-vendor: ask」整段；`review.json` 的 `second_vendor: "codex"`。
- **判定**：works。

## 對你既有的資料做了什麼

這次改動修過兩份你原本就有、正在生效中的文件：`PRINCIPLES.md` 的「不可退讓事項 2」被修改並重新蓋章——舊文字是「至少兩位讀者、一次盲跑、一次對抗」，新文字改成「全車道兩位、小車道一位，盲跑只在 Acceptance 全機械時可省略」，蓋章日期從 2026-09-03 改成 2026-09-04（這是這次 change 在 W0 checkpoint 上請你當場拍板的「option A」，commit `7f4e19e1`，舊文字仍完整保留在這次 commit 之前的版本裡，用 `git show` 隨時能對照）；另外 `docs/loom/KICKOFF-DEFAULTS.md` 的 `second-vendor` 那行從固定寫死的 `codex` 改成 `ask`（表示以後每次改動都會被問一次，不會再被自動預設），並新增一行 `docs-lint: none`。除此之外沒有動到你其他既有的資料。

## 我幫你決定的事

- **車道判準寫成純機械規則，不讓 agent 自由心證** — 我／實作者把「小車道」寫死成：改動路徑要嘛是文件／記錄／測試／CI設定，要嘛只碰一個 plugin 且不碰任何介面層，只要有一行非測試的程式碼就整條退回全車道。理由：intent 明講判準不能看行數也不能讓 agent 自己判斷。改回別的判準要重寫 `change_lane` 那段程式加一輪測試。
- **`second_vendor` 欄位命名與函式名稱由 agent 直接定案**（plan.md 風險行）——因為探針要先寫出可執行案例，這兩個名字必須先定下來才能寫測試；之後要改名字要跟著改探針與 checker 兩處。
- **W0 checkpoint 的 option A（PRINCIPLES.md 非負讓步 2 怎麼改）由你本人當場拍板**——已記在 `review.json` 對應 finding 的 `resolved` 欄位，不是我或實作者代決的。

## 我不確定你是不是要這樣

- 這次 change 自己是「全車道」，理論上該在寫計畫時就被問一次「這次要不要用 Codex 當第二位讀者？」，但計畫的 Questions asked 清單裡沒看到這句問話被記下來——review.json 卻已經有 `second_vendor: "codex"`。可能是因為 `second-vendor: ask` 這個新值就是這次 change 自己在造，寫計畫當下 KICKOFF 還沒改成 `ask`，所以走的是舊的固定流程；但這點我沒有把握，建議你確認一下這個答案是不是照你的意思來的。
