# checker 四條接縫一次修 — 我試了什麼、發生了什麼

2026-09-04 在一份乾淨的專案副本上試的（對應 commit a8a13524）。

## 你要的東西，一條一條來

### 1. 只改樣板文件的改動不再被逼成 product；改真的介面程式碼還是會被擋
- **怎麼試的**：在一個乾淨的臨時倉庫裡，先改 `loom-code/contract/templates/intent.md`（樣板文件，屬於 docs 型別）一行，intent 標成 `kind: engineering`，跑「檢查 intent」與「開始寫計畫」兩個指令；再另開一個分支改 `src/cli/x.py`（真的程式碼），一樣標 `kind: engineering`，再跑一次「檢查 intent」。
- **發生了什麼**：改樣板文件那次，兩個指令都通過（exit 0）；改 `src/cli/x.py` 那次照樣被擋下，訊息說「diff 碰到了使用者介面（interface surface）」，並且明講「KICKOFF 的 interface-surfaces 只能加不能減」。
- **證據**：兩次指令的原始輸出（我自己在臨時倉庫跑的，不是讀報告）；擋下訊息裡看得到規則名 `intent.kind-recompute`。
- **判定**：works。

### 2. 舊腳本 `check_open_questions.py` 已經拿掉，命令面（AGENTS.md）也不再列它
- **怎麼試的**：直接找那兩個檔案還在不在；搜尋整個專案裡還有沒有人提到這支腳本的名字，排除掉「開發歷史紀錄」與「CHANGELOG」。
- **發生了什麼**：兩個檔案都已經不存在。搜尋結果裡，除了開發歷史紀錄與 CHANGELOG，**還多了一個地方**：這次改動自己新寫的一支測試 `test_no_stale_open_questions_script.py`，裡面提到這支腳本的名字——但那是「斷言它已經不存在」的測試本身，功能上等同於在幫這條 Acceptance 把關，不是遺留的引用。`AGENTS.md` 的命令面清單裡已經完全找不到它了。
- **證據**：`ls` 兩個路徑都回「No such file or directory」；`grep -rn check_open_questions` 的完整清單（見上）。
- **判定**：works——但字面意義上「grep 只剩 CHANGELOG 與歷史紀錄」這句不是 100% 精確，多出來的那一筆是這條驗收本身要求存在的守門測試，不是漏刪的舊引用。算不算「乾淨」是文字定義問題，不是功能缺陷。

### 3. 乾淨環境對主幹已合併的 intent 跑檢查會過；分支上漏帶那一行照樣被擋
- **怎麼試的**：在乾淨環境對 `docs/loom/intent/2026-09-02-simple-loom-flow.md`（一個從 squash 合併方式進主幹的舊 intent）跑「檢查 intent」；另外，在一個模擬的分支上把 needs-design 從「no」改成「yes」，但 commit 訊息裡故意不帶那行文字，再跑一次。
- **發生了什麼**：對主幹上的舊 intent，指令通過（exit 0），並且印出一行說明：「這個 commit 長得像 GitHub squash（在 origin/main 的第一父系鏈上、單一 parent、標題是 PR 合併格式），但 PR 來源沒辦法離線驗證，所以視為未確認的 squash——這行文字假設它曾經被分支上的 push 閘檢查過」。對假造的分支 commit（沒有 squash 外觀、就是普通改動漏了那行），照樣被擋下，訊息點名是哪個 commit 漏了哪一行。
- **證據**：兩次指令的原始輸出；另外我也直接跑了這次改動自己寫的 5 個對抗測試（`test_abuse_squash_needs_design.py`），全部通過，涵蓋「squash 形狀的分支 commit 過」「手寫冒充 `(#1)` 但不在主幹上的分支 commit 仍被擋」「普通 commit 沒有那行仍被擋」等情境。
- **判定**：works。

### 4. 同一支探針檔被引用很多次時只跑一次；出錯訊息只印一次；既有紀錄的結果不變
- **怎麼試的**：跑了這次改動自己寫的對抗測試（`test_abuse_probe_rerun_dedup.py`，直接呼叫檢查器裡負責這件事的函式，用一個「執行一次就在計數檔加一行」的機制實測次數，不是用嘴巴宣稱）；另外我自己也對這個分支目前的狀態跑了一次真正的 push 檢查（雖然因為分支還在進行中，reviewed_sha 對不上被擋，但這不影響我讀到的探針輸出行）。
- **發生了什麼**：對抗測試 5 個全過，包含「同一檔被 4 筆紀錄引用只執行一次」「失敗的檔案，所有引用它的紀錄一次性失格、錯誤訊息只印一次」「不同檔案各自算一次」「舊改動（2026-09-03-loom-post-merge-seams）那種同檔多筆的形狀，門檻結果跟以前一樣」。我自己跑的 push 輸出裡，也真的看到「referenced by 3 records」這種每個檔案只印一行、附註引用筆數的格式，跟規則說明裡的那句話（用「紀錄」當計數單位；一個檔案只跑一次）對得上。
- **證據**：對抗測試輸出（5 passed）；push 指令的原始輸出片段（`adversarial …test_abuse_templates_glob.py: … referenced by 3 records` 這種行）；`--list-rules` 印出的 `push.probes-adversarial` 說明句子。
- **判定**：works。

### 5. `second-vendor` 改成「ask」；這次改動自己的 review.json 記了答案並過了對應規則
- **怎麼試的**：直接讀 `docs/loom/KICKOFF-DEFAULTS.md` 那一行；讀這次改動的 `review.json` 裡有沒有 `second_vendor` 這個頂層欄位；核對規則清單裡有沒有一條規則在檢查這件事。
- **發生了什麼**：那一行已經是 `second-vendor: ask — kouko decides per change …`；`review.json` 裡 `second_vendor` 記的是 `codex`，跟實際的第二讀者（codex／openai）verdicts 對得上；`--list-rules` 也印出對應規則的說明。
- **證據**：檔案內容原文；`--list-rules` 輸出。
- **判定**：works。

### 6. codex 那份鏡射檔跟主要檢查器逐位元相同
- **怎麼試的**：直接用 `cmp` 比對兩個檔案；再跑這次改動新增的漂移測試 `test_codex_mirror_matches_checker.py`。
- **發生了什麼**：`cmp` 說兩個檔案在第 2 行不同——差異是鏡射檔多了一行版本戳（`# loom-checker 1.1.0`），把這一行拿掉之後，其餘內容逐位元相同（我自己用 `diff` 核對過，只有那一行）。這是設計上刻意的：測試本身就是「鏡射檔 = 原始檔 + 一行版本戳」，不是字面上「一模一樣」。這跟 Acceptance 原文寫的「逐位元相同」不完全一致——但跟這次改動的漂移測試、跟現有 CI 的 codex-manifest-drift 檢查所認定的「一致」是同一件事。
- **證據**：`cmp` 與 `diff` 的原始輸出；測試結果（1 passed）。
- **判定**：works——但要注意「逐位元相同」這句話字面上不成立（差一行版本戳），實際定義是「原始檔 + 一行固定格式的版本戳」。

### 7. ship 站的 memory 步驟加了那句話，字數在帽內，站摘要表同步測試綠
- **怎麼試的**：讀 `loom-code/skills/ship/SKILL.md` 第 3 節，找那段「把探針畢業成永久測試」的文字；算整份文件字數；跑對應的兩個測試。
- **發生了什麼**：那段文字在（見上引用）：把 `evidence/probes/` 底下跟既有測試沒有同名函式的探針，複製成永久測試、帶 `Task:` 標記，原檔不刪；docs／skill 型的冷讀報告不畢業。整份文件 3301 字，帽是 4500（軟目標 3750），在帽內。兩個測試都通過（13 passed）。
- **證據**：原文引用；字數計算；測試輸出。
- **判定**：works。

### 8. `--list-rules` 規則數跟主幹一樣是 27；整包測試綠
- **怎麼試的**：跑 `--list-rules` 數行數；跑套件層級的完整測試指令 `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q -n auto`。
- **發生了什麼**：規則數 27，跟 main 一致。整包測試：**1124 passed in 40.58s**，沒有失敗、沒有 skip。
- **證據**：兩次指令的原始輸出。
- **判定**：works。

### 9. build 站文字改成「完整車道中 `code` 或 `gate` 型 task 先派對抗者，小車道不先派」；字數帽內、站摘要表同步測試綠
- **怎麼試的**：讀 `loom-code/skills/build/SKILL.md` 第 2 節開頭那段；算字數；跑對應測試。
- **發生了什麼**：那段文字明確寫「In the full lane, a task whose 檔 paths map to the `code` or `gate` artifact type is adversary-first」，並且說明小車道（`change_lane` 重算出來、只碰測試／文件／CI config 的計畫）跳過這條、實作者照舊先上、對抗者改在 checkpoint 才動手；也附了一句理由（獨立對抗測試抓自測漏掉的假通過，並引用一個量測數字）。整份文件 2559 字，在帽內。對應測試 4 passed。
- **證據**：原文引用；字數計算；測試輸出。
- **判定**：works。

## 對你既有的資料做了什麼

沒有——這次改動只碰這個專案自己的規則檔、腳本、文件、測試，不讀不寫任何使用者自己的資料。乾淨環境裡跑的每一項測試也都是在臨時倉庫或這份乾淨副本裡做的，沒有動到你原本的分支或工作目錄。

## 我幫你決定的事

- **codex 鏡射檔用「原始檔 + 一行版本戳」而非逐字節相同來定義「一致」** — Acceptance 原文寫「逐位元相同」，但實際機制（也是既有的 `codex_scaffold.py` 設計）一定會在複製時插入一行版本號。這次改動選擇把「一致」的定義收斂成「拿掉那一行之後逐位元相同」，並寫成一個明確測試釘住這個定義，而不是想辦法真的消除那一行差異。如果你要的是連版本戳都不能有差異，這裡需要重新討論。
- **舊腳本存在性檢查測試本身會提到腳本名字，因而技術上不算「grep 完全乾淨」** — 這是驗收條件文字（Acceptance #2）用「grep 只剩歷史紀錄」描述一個「沒有殘留引用」的意圖，但一個負責斷言「這支腳本已經不存在」的守門測試，寫法上不可能不提到它的名字。這不是遺漏，但如果你希望這條驗收的字面意思被嚴格滿足，這裡有落差。
- **審查紀錄裡有兩則「important」等級的發現，最終都被修正而不是被駁回**（`loom-code/scripts/loom_checker.py:843` 的型別過濾範圍問題、`loom-code/scripts/loom_checker.py:736` 的 squash 來源可驗證性問題）——這兩則都在後續輪次改了程式碼並經第二位讀者確認修好，`review.json` 裡沒有被駁回、未修的 important 或更嚴重的發現。

## 你可能會想確認的事

- Acceptance #6「逐位元相同」與 Acceptance #2「只剩 CHANGELOG 與歷史紀錄」這兩句話都跟實際落地結果有一點點文字上的落差（見上「我幫你決定的事」）——功能上我認為都是對的，但如果你在意逐字對應驗收條件，這兩處值得你自己再看一眼。
- 我在乾淨副本裡跑的完整 `push` 檢查因為分支還在同時被其他 agent 動（`reviewed_sha` 與 `HEAD^` 對不上）而回報了一個「不是要推的那個 commit」的擋下訊息；這不是這次改動要修的四條接縫之一，是分支還沒收尾的正常現象，不影響上面九條的判定，但如果你自己在收尾前手動跑一次 `push`，會先看到這則訊息，屬預期。
