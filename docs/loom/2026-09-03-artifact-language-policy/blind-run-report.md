# 產物語言政策 — 我試了什麼、結果如何

2026-09-05 在一份乾淨的 worktree 副本上試（HEAD `9aa9555`，detached）。

這次是 wave-end:1（第一波結束的檢查點），第二波（每站 SKILL.md 各加一句語言規定、
changelog／版本號）依計畫**還沒做**，以下逐條照實回報，不用「應該還沒做」猜測。

## 你要的東西，一條一條試

### 1. 一個新 change 走完流程，其 spec／plan／review.json／evidence／探針 docstring／commit 訊息全為英文，intent、盲跑報告與 PR 內文為使用者語言——由 blind-run 報告逐項列出檢查結果
- **怎麼試的**：這個 change 自己就是驗收樣本（plan 裡寫明）。我讀了
  `plan.md`（全英文）、`evidence/` 下兩份研究筆記（全英文）、
  `evidence/probes/test_abuse_language_policy.py` 的 8 個測試函式與其
  docstring（全英文），並用 `git log 4e459ed0..HEAD --format='%B' | grep -cP '[中日文字]'`
  掃全部 commit 訊息。
- **結果**：spec 這次沒有（engineering、needs-design: no，intent 裡寫明不需要
  spec）。plan、兩份 evidence、探針檔全英文，沒有中文字。commit 訊息掃到
  2 處中文字元，但都不是新寫的中文散文：一處是 61dc0af5 的 commit body
  引用被替換掉的**舊**標籤「檔/測/風」（說明「這三個字被換成 Files/Test/Risk」，
  引用而非使用）；另一處是 2a45a57a 的 commit body 直接貼了 intent 檔裡
  `needs-design:` 那一行的原文（intent 本身就該是使用者語言，這個 commit
  是「確認 intent」那一步，貼的是使用者原話）。intent 全文是中文（正確——
  這是使用者面產物）。盲跑報告（這份文件）與 PR 內文（尚未開 PR，之後由
  ship 站產生）也是使用者語言。
- **證據**：`plan.md`、`evidence/research-se-*.md`、
  `evidence/probes/test_abuse_language_policy.py` 全篇肉眼確認；
  `git log 4e459ed0..HEAD --format='%B' | grep -cP '[\x{4e00}-\x{9fff}]'` → 2，
  逐一核對來源如上。
- **判定**：大致做到 — 兩處中文都是「引用舊字」而非新寫的中文內容，
  不算違反政策，但字面上確實不是純英文，值得記一筆。

### 2. `loom-code/contract/templates/` 內每個檔案的註解與說明文字為英文，`intent.md` 模板的欄位語意不變
- **怎麼試的**：對該目錄下全部 8 個檔案跑
  `grep -cP '[\x{4e00}-\x{9fff}]'`；另外讀了 `intent.md` 模板確認欄位名稱
  （Problem／Proposed outcome／Acceptance／Constraints／Out of scope／
  Open questions）沒有被拿掉或改名。
- **結果**：8 個檔案（`intent.md`、`KICKOFF-DEFAULTS.md`、
  `memory-README.md`、`plan.md`、`PRINCIPLES-interview.md`、`PURPOSE.md`、
  `review.json`、`spec-minimal.md`）中文字元數全部是 0。`intent.md` 的欄位
  仍是那六個，順序與名稱未變。
- **證據**：8 行 grep 輸出全 0（見上方指令）。
- **判定**：做到。

### 3. capture-intent／write-spec／write-plan／build／review／ship 六站的 SKILL.md 各有一句語言規定，reviewer 契約有「非英文內部產物 → nit」一條；`loom_checker.py --list-rules` 規則數不變
- **怎麼試的**：對六個 SKILL.md 各跑 `grep -in "english"`；另外跑
  `python3 loom-code/scripts/loom_checker.py --list-rules | wc -l`。
- **結果**：六個站的 SKILL.md（`write-plan`、`build`、`review`、`ship`、
  `capture-intent`、`write-spec`）目前**一句都沒有**提到「English」——這是
  wave 2 的任務（W2-01），計畫上寫明排在這一波之後，本來就還沒做。
  `loom-code/agents/reviewer.md` 這邊倒是已經有了：第 115-119 行寫明
  「內部產物不是 Conventional Comments 格式的開頭標籤 / 探針函式名不是
  三段式 → 一律 nit，不論 docs-lint 有沒有宣告，且絕不升級」。
  `--list-rules` 輸出 27 行，跟 plan 裡記的「規則數不變」一致。
- **證據**：六次 grep 全空（無輸出）；`reviewer.md:115-119`；
  `loom_checker.py --list-rules | wc -l` → 27。
- **判定**：尚未達成（符合預期）— 六站的語言規定句子還沒寫，是 wave 2 的
  工作，這次盲跑只到 wave-end:1。規則數不變這半條已驗證成立。

### 4. 本 repo 既有中文文件不動：`git diff` 不碰 `docs/loom/2026-09-0*/` 與 `docs/loom/intent/` 既有檔案
- **怎麼試的**：`git diff --name-only origin/main..HEAD -- 'docs/loom/2026-09-0*/' 'docs/loom/intent/'`
- **結果**：只列出一個檔案 —
  `docs/loom/intent/2026-09-03-artifact-language-policy.md`，那是這個
  change 自己新增的 intent 檔（本來就不存在，不是「動了既有中文檔」）。
  沒有任何既有的中文 plan、evidence 或別的 intent 檔被改到。
- **證據**：上方指令輸出僅一行，且該檔是本 change 自己新建。
- **判定**：做到。

### 5. 三個句型模板寫進契約：`spec-minimal.md` 模板的 REQ 行示例為 EARS 五式之一、reviewer 契約要求 finding text 以 Conventional Comments 的 label 開頭、adversary 與 blind-runner 契約要求探針函式名為三段式；驗收 1 的那個新 change 其 review.json 每條 finding 與每個探針函式名都符合，由 blind-run 報告逐項列出
- **怎麼試的**：讀 `spec-minimal.md` 的 REQ-1 範例行；讀
  `reviewer.md` 的 nit 段落；讀 `adversary.md`、`blind-runner.md` 有沒有
  提三段式探針名；另外檢查這個 change 自己的
  `evidence/probes/test_abuse_language_policy.py` 8 個函式名，以及
  `review.json` 目前的 `verdicts[]`／`probes[]`。
- **結果**：`spec-minimal.md:11` 寫的是
  `WHEN <trigger>, the <system> shall <verifiable obligation> → Acceptance #<n>`，
  是 EARS 的 WHEN 式。`reviewer.md:115-119` 已要求 finding text 開頭要有
  Conventional Comments 標籤。`adversary.md:53` 與
  `blind-runner.md:47-49` 都已寫明三段式探針名的要求。這個 change 自己
  的 8 個探針函式名（`test_templates_cjk_absent`、
  `test_stations_english_absent`、`test_reviewer_nitclause_absent`、
  `test_specminimal_ears_absent`、`test_agents_probename_absent`、
  `test_checker_rulecount_pinned`、`test_branchdiff_scope_clean`、
  `test_cjkdetector_hidden_caught`）都是「單元_狀態_預期」的三段式。
  但 `review.json` 目前的 `verdicts[]` 與 `probes[]` 都是空陣列——本次
  wave-end:1 的對抗與盲跑結果**還沒寫回**這份檔案，所以「review.json 每條
  finding 都符合 Conventional Comments」這件事現在**查不到東西可核對**，
  無法判定，只能等這次盲跑與對抗的結果真的寫進 `review.json` 之後再核。
- **證據**：`spec-minimal.md:11`、`reviewer.md:115-119`、
  `adversary.md:53`、`blind-runner.md:47-49`；探針檔 8 個函式名逐一核對；
  `review.json` 目前 `verdicts: []`、`probes: []`。
- **判定**：契約面（模板、reviewer、adversary、blind-runner 四份文件）做到；
  「review.json 每條 finding 都符合格式」這件事本次無法驗證——`review.json`
  裡還沒有 finding 可查。

## 對你既有的資料做了什麼

沒有——這個 change 只碰 `loom-code`、`loom-design` 兩個 plugin 的契約檔、
模板檔，以及它自己在 `docs/loom/2026-09-03-artifact-language-policy/` 下
新建的檔案。既有的中文 plan、evidence、intent 檔案一個字都沒被動過
（驗收 4 已核對）。

## 我幫你決定的事

以下是 plan.md 的 Risks 段落列出、由執行者（agent）自行拍板的項目：

- **模板裡的中文說明改成英文，但欄位鍵、標題、標記符號一個字元都不動**——
  改變後，之後照模板寫新文件時看到的是英文說明，但既有工具（checker）解析
  用的欄位名稱不受影響。若這個決定錯了，代價是要重新逐檔比對欄位是否被
  誤動過。
- **plan 模板的三個項目標籤從中文「檔／測／風」改成英文「Files:／Test:／
  Risk:」**——因為只有一份文件（`build/SKILL.md`）用字串方式讀這三個標籤名，
  所以兩邊一起改。已經寫好的舊 plan 檔案保留舊標籤，不會被回頭改，也不會
  被任何程式碼解析到，所以不影響。
- **`PRINCIPLES-interview.md` 模板裡問使用者的問題，模板本身存英文原文，
  跑的時候才由站翻成使用者的語言**——跟「跟使用者對話那句用使用者語言」
  的既有規定一致，此變動視為驗收 2 的必然結果，不算例外。
- **這次審查本身用的 reviewer／adversary／blind-runner 是從已安裝的
  plugin（1.2.4 版）派出去的，不是從這個分支正在改的版本派出去的**——
  所以理論上這次的 reviewer 契約還沒有機會真的套用新加的 nit 規則來審這個
  change 自己。為了讓驗收 5 仍能被核對，plan 裡寫明派工時要在派工指令裡
  明講 Conventional Comments 標籤的要求。我在驗收 5 那條已經指出：由於
  `review.json` 目前還沒有任何 finding 寫入，這個補救措施本身**還沒有機會被
  驗證**——如果之後 finding 真的寫進來卻沒有標籤開頭，這裡就是漏洞會出現
  的地方。
- **intent 裡的 Acceptance 行維持使用者原話，不套 EARS 句型**——因為 EARS
  只管英文的 `REQ-<n>` 行，intent 本來就規定是使用者語言。
- **cost／效益「用詞一致會讓審查判決比較穩定」被記成待驗證的假設，不是
  已證明的結論**——目前只有引用文獻證明「換一種說法問模型會讓判決移動」，
  沒有人量過「被審的文件本身用詞受控」是否真的降低判決變異。這是誠實記錄，
  不是決定，這裡順帶列出讓你知道這個政策背後的因果假設還沒有實證支持。

沒有被 reviewer 判定為 `important` 以上又被駁回的 finding——因為這次
wave-end:1 的 `review.json` 裡 `verdicts[]` 是空的，還沒有任何審查結果寫入，
沒有東西可以列。

## 我不確定你要不要的事

- 六個站的 SKILL.md 語言規定句、changelog／版本號更新（loom-code
  1.2.4→1.3.0、loom-design 1.0.3→1.0.4）、`KICKOFF-DEFAULTS.md` 那行
  「docs-lint: none」的理由文字更新，這些都排在 wave 2，這次盲跑還看不到，
  之後還會有一次 branch-end 的盲跑把它們補上——你要不要現在就先看一次
  wave 2 完成後的結果，還是等 ship 前那次盲跑報告一次看完？
- `review.json` 這次沒有任何 finding 或 verdict 寫入，代表對抗與審查的
  結果目前不在這份檔案裡——這是本次派工記錄本來就有兩筆（adversary、
  blind-runner）尚未回填的結果，還是流程上本來就會晚一步寫入，我不確定，
  建議你留意 wave-end:1 這個檢查點的審查結果最後有沒有真的落到
  `review.json` 裡。
