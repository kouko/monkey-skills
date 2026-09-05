# 使用者宣告車道（full／express／gate-only）——我試了什麼、發生了什麼

在 2026-09-05 試的，用的是一份乾淨複製的專案，版本 `d31484fa`。

**先說範圍**：這次試的是這個改動的「wave 1」——car 車道宣告、切換規則、
車道重算、review／build／ship 三站的文字。改動計畫裡還排了「wave 2」
（版本號更新到 1.6.0、記憶步驟），但那部分還沒做出來，這次不試也不評論。

## 你要的東西，一條一條試

### 1. intent 範本要有 `lane:` 說明；KICKOFF 範本要有 `default-lane:` 說明；切換 commit 沒帶那一行就要擋
- **怎麼試的**：打開兩份範本檔看說明文字；接著自己動手做兩個小實驗——寫
  一個帶 `lane: express` 的 intent，commit 訊息裡「不寫」那一行，跑一次
  checker 的 `intent` 檢查；再寫一個 commit 訊息裡「有寫」那一行，再跑一次。
- **發生了什麼**：intent 範本裡真的有一行說明 `lane:` 欄位（可選、值只能
  是 `express` 或 `gate-only`、切換要帶日期與人名）；KICKOFF 範本裡也有
  `default-lane:` 的說明。commit 訊息漏寫那一行時，工具擋下來並印出訊息
  「commit ... 沒有帶著 `lane: express` 這一行」；補上那一行後，同一個檢查
  順利通過。
- **證據**：範本檔 `loom-code/contract/templates/intent.md` 第 8 行、
  `loom-code/contract/templates/KICKOFF-DEFAULTS.md` 第 17 行；手動實驗在
  `/Users/kouko/.claude/jobs/f14c84f2/tmp/manual-switch-missing-line`，指令
  `python3 loom_checker.py intent <路徑>`，前者印出
  `BLOCK intent.needs-design-reason: the commit message ... does not carry
  the line lane: express`（結束碼 1），後者結束碼 0。
- **結論**：符合。

### 2. 沙盒：宣告 `express` 的 docs／skill 類改動，只有一位讀者，過閘要成功；同一份改動再動 checker 一行，要變回擋下
- **怎麼試的**：自己搭一個小的假專案，寫一份 `lane: express` 的 intent，
  改一份 docs 檔和一份 skill 檔，只記一位讀者的審查結果，跑「過閘」指令；
  接著在同一份改動再多改一行 checker 本身的程式碼，重跑一次過閘指令。
- **發生了什麼**：第一次過閘指令回傳成功（結束碼 0）；加了 checker 那一行
  之後回傳失敗（結束碼 1），並印出「因為改到了 `loom_checker.py`（非測試
  程式碼），車道被強制拉回 full，需要 2 位讀者，現在只有 1 位」。
- **證據**：手動實驗在
  `/Users/kouko/.claude/jobs/f14c84f2/tmp/manual-express-repo`；也用專案自
  帶的對抗測試檔 `test_abuse_lane_declaration.py` 裡對應的兩個測項重跑過，
  全部通過（`pytest ... -q` → `11 passed`）。
- **結論**：符合。

### 3. 沙盒：宣告 `gate-only` 的純 docs 改動，零讀者也能過閘（但要有 ≥3 個對抗測試和一次整包測試紀錄）；同一份改動加一個 SKILL.md 檔要擋下
- **怎麼試的**：搭另一個假專案，寫一份 `lane: gate-only` 的 intent，只改
  一份 docs 檔，記零讀者、3 個對抗測試紀錄和 1 個整包測試紀錄，跑過閘；
  再加一份 skill 說明檔（SKILL.md），重跑過閘。
- **發生了什麼**：第一次過閘成功（結束碼 0）；加了 SKILL.md 之後失敗
  （結束碼 1），訊息說「因為改到了一份 skill／agent 契約檔，車道被強制拉
  回 full，需要 2 位讀者，現在 0 位」。
- **證據**：手動實驗在
  `/Users/kouko/.claude/jobs/f14c84f2/tmp/manual-gateonly-repo`；同一份
  對抗測試檔裡的對應測項也全部通過。
- **結論**：符合。

### 4. 沙盒：做到一半換車道——前面兩輪照舊兩位讀者，換車道之後那一輪起變一位讀者可通過；換車道那個 commit 沒帶那一行要擋
- **怎麼試的**：跑專案自帶對抗測試檔裡建好的三個情境（前兩輪兩位讀者、
  「從第 2 輪起換車道」讓第 3 輪一位讀者過關、「從第 3 輪起換車道」讓第
  3 輪本身仍要兩位讀者），另外自己動手重跑一次「換車道 commit 沒帶那一行」
  的情境。
- **發生了什麼**：三個情境都跟預期一致：從第 2 輪起換，第 3 輪一位讀者就
  過關；從第 3 輪起換，第 3 輪本身還是要兩位讀者、擋下來。手動重跑「commit
  沒帶那行」的情境，工具印出「commit ... 沒有帶著 `lane: express` 這一行」
  並擋下（結束碼 1）。
- **證據**：`pytest test_abuse_lane_declaration.py -k "mid_flight or
  switch_commit_message"` → `3 passed`；手動重跑同一份
  `/Users/kouko/.claude/jobs/f14c84f2/tmp/manual-switch-missing-line`
  沙盒。
- **結論**：符合。

### 5. `references/lane-switch.md` 存在，含三格固定格式、「不能選的格照列並說原因」、口頭對應表；冷讀考驗——只讀 review 站文字和這份參考檔，面對「改動裡有一份 SKILL.md、使用者說『快速模式』」的情境，要列出三格、把 gate-only 標成不能選並說原因
- **怎麼試的**：只讀了 `loom-code/skills/review/SKILL.md` 和
  `loom-code/skills/review/references/lane-switch.md` 這兩份文件（不看其他
  任何程式碼），然後自己扮演拿到這份文件的人，面對合成情境：「這次改動
  裡有一份 `loom-code/skills/build/SKILL.md`；使用者在第 2 輪說『快速
  模式』」，照著參考檔要求的格式寫出三格提示。
- **發生了什麼**：口頭對應表把「快速模式」對應到 `express`（無需再問）。
  三格提示如下——

  | 車道 | 失去什麼 | 還剩什麼 | 估計 |
  |---|---|---|---|
  | full（目前所在） | （不變，全部都在） | 兩位以上讀者、盲跑、branch-end 對抗 | — |
  | express | 從兩位以上讀者降成一位、中途的 wave-end 檢查點 | 一位讀者、驗收條非機械可查時仍跑盲跑、branch-end 對抗一次 | 無估計（這次沒有可比的 cost 紀錄） |
  | gate-only（不能選） | 全部讀者、盲跑 | 對抗測試、整包測試、branch-end 對抗一次 | 無估計 —— **不能選，因為這次改動裡有一份 SKILL.md（skill／agent 契約類檔案），gate-only 明文禁止這類改動宣告** |

  依「從第 2 輪起換」的文法，這次換車道只影響第 2 輪之後（第 3 輪起），
  第 2 輪本身照舊跑在原本的車道。
- **我不得不用猜的地方**：（a）「目前所在」我猜是 `full`——情境沒有明講
  換車道之前是哪個車道，我用這個改動的預設車道當猜測；（b）估計欄兩個
  車道我都寫「無估計」，因為情境沒給我可用的 cost 數字或前一次同車道改動
  的紀錄。
- **build／ship 站文字確認**：build 站有一句話說「使用者要求做到一半換
  車道時，讀 review 站的 `references/lane-switch.md` 取得三格後果提示，
  換之前先讀」；ship 站沒有再重複指向這份參考檔，只帶一行 PR 內文格式
  `lane: <名稱>（第 N 輪起）`——這是它被要求做的唯一一件事。
- **釘測試**：`test_lane_switch_reference.py`（10 項，含
  `test_three_option_block_covers_full_express_gateonly`、
  `test_forbidden_option_listed_with_its_reason`、
  `test_switch_line_grammar_present`）、
  `test_review_skill_points_at_lane_switch`、
  `test_wave_end_points_at_lane_switch_reference`（build）、
  `test_pr_body_template_carries_lane_line`（ship）全部通過。
- **證據**：`pytest loom-code/scripts/test_lane_switch_reference.py
  loom-code/scripts/test_build_station_text.py
  loom-code/scripts/test_review_station_text.py
  loom-code/scripts/test_ship_station_text.py -q` → `147 passed`。
- **結論**：符合。

### 6. review 站文字要有 express／gate-only 各一段行為說明（讀者數、盲跑條件、對抗一次、無中途檢查點、gate-only 的③要讀什麼）；ship 站要有 PR 內文一行；都要有釘測試
- **怎麼試的**：讀 `loom-code/skills/review/SKILL.md` 找對應段落；讀
  `loom-code/skills/ship/SKILL.md` 找 PR 模板那一行；跑對應的釘測試。
- **發生了什麼**：review 站文字裡找到——
  - 讀者數：「Reader floors are full two, small one, express one, and
    gate-only zero」
  - 盲跑條件：「Express triggers the blind run only for an Acceptance line
    that resists a mechanical check, matching the small lane's trigger;
    every mechanical line skips it. Gate-only skips the blind run always,
    relying on probes and package tests alone as its evidence.」——這句同時
    回答了「gate-only 的③讀什麼」：不是盲跑報告，是探針與整包測試那一頁。
  - 對抗一次、無中途檢查點：「Express and gate-only run the adversary once,
    at branch-end, keeping the probe floor of three regardless of lane.」
  ship 站 PR 模板裡有一行：`lane: <name>（第 N 輪起）`。
- **釘測試**：`test_lane_paragraph_names_three_declared_lanes_and_what_
  each_drops`、`test_reader_floor_sentence_names_all_four_lanes`、
  `test_blindrun_by_lane_sentences_present`（連同它的肯定句／否定句自測
  對照組）、`test_matcher_adversary_once_sentence_negated_rejected`、
  `test_pr_body_template_carries_lane_line`——全部通過。
- **證據**：同上 147 passed 的那次 pytest 執行涵蓋了這些測項。
- **結論**：符合。

### 7. 規則數不變（27 條）；既有 full／small 車道的測試不受影響；本 repo 的 KICKOFF 要填 `default-lane: full`；跑 KICKOFF 定義的整包測試指令
- **怎麼試的**：跑 `--list-rules | wc -l`；打開
  `docs/loom/KICKOFF-DEFAULTS.md` 看有沒有 `default-lane:` 那一行；照
  KICKOFF 裡寫的指令原文跑一次整包測試（這條指令本身分兩段 session，因為
  `loom-design/scripts/` 有自己的 pytest 設定檔）；另外單獨跑一次既有的
  車道測試檔確認沒被動過。
- **發生了什麼**：`--list-rules` 印出 27 行。KICKOFF 裡有一行
  `default-lane: full — no change here has declared express or gate-only
  yet …`。整包測試第一段（`loom-code/scripts/`、`scripts/`、
  `.claude/hooks/`）跑出 `1710 passed, 5 skipped, 1 xfailed`（89 秒）；第二
  段（`loom-design/scripts/`）跑出 `182 passed, 1 skipped`（11.5 秒）。既有
  的車道測試檔 `test_probes_change_lane.py` 跑出 `26 passed`，一項沒少。
- **證據**：終端機輸出（如上）；指令原文取自
  `docs/loom/KICKOFF-DEFAULTS.md` 第 8 行的 `package-tests:` 欄位。
- **結論**：符合。

## 對你既有的資料做了什麼

沒有動到——這次改動只碰了它自己的文件（範本、checker 程式碼、幾份站文字、
一份新的參考檔、它自己的 intent／plan／review.json），沒有動到這個 repo
裡任何一份「更早的」改動的 intent 或 review.json；`lane:` 這個新欄位在
每一份既有的 intent 上都是可省略的，省略時照舊走 `full`——舊資料完全不用
改就能繼續用。

## 我幫你決定的事

- **零讀者那一輪要怎麼算「通過」** —— gate-only 車道下，一輪審查可以完全
  沒有讀者驗收結果，只留探針和整包測試紀錄；我讓「至少要有幾位讀者」這條
  規則在這種情況下自動算通過，不再另外加一條新規則去處理它。以後如果要
  改嚴，得改這條算法，不是加規則。
- **誰能寫 `lane:` 這一行，工具管不到** —— 工具只檢查這一行有沒有寫「誰
  簽的名」，沒辦法分辨簽名的是使用者本人還是一個自動化的程式假裝成使用者
  簽的。真正擋著「agent 不能自己宣告車道」的是站文字上白紙黑字寫的規矩，
  和審查時人工抓出這種情況當作一個問題點來提報。以後如果站文字被拿掉，
  這道防線就沒有工具接手。
- **改範本、寫預設值這兩份工作分給不同的檔案負責** —— 一份檔案負責定義
  「車道」和「預設車道」這兩個新欄位長什麼樣子，另一份檔案負責把說明文字
  寫進範本裡，兩邊各自的測試只驗自己該管的那塊。這是為了不要兩個地方同時
  改同一件事而打架，代價是要追蹤這個功能的全貌得看兩份檔案。
- **PR 內文一行要放哪、放多少字** —— 這次只在 PR 內文加了一行寫車道名稱和
  從第幾輪起生效，沒有把換車道的三格提示整段搬進 PR 模板裡（那個提示只在
  對話裡問使用者的當下出現）。以後想在 PR 上看到完整的換車道理由，得回頭
  看對話紀錄，PR 本身不會留。
- **「要不要找第二家 AI 家做覆核」這個問題，還是照著改動看起來有多大來
  問，不是照使用者選的車道來問** —— 也就是說，就算你這次選了「快速模式」
  或「只過閘」，只要這份改動實際改的檔案數量或種類看起來仍然算「大」，
  系統還是會照舊問你要不要找第二家 AI 覆核；反過來，如果你維持在完整
  車道、但實際改動很小，也可能不會被問。換句話說，選車道只影響「要幾位
  讀者、要不要盲跑、有沒有中途檢查點」，不影響「要不要找第二家 AI」這件
  事——這兩者目前是分開算的，這次沒有把它們接起來。

沒有審查者對這份改動提出「important」以上、又被駁回的問題——review 這一
輪目前還沒有讀者留下正式的審查意見（我是這一輪被派去試跑的角色之一），
所以這裡沒有可以列的駁回紀錄。

## 這次改動裡，該用英文寫的地方有沒有守住

專案規定：計畫文件、規格文件、審查紀錄的意見、證據檔、測試裡的說明文字、
測試名稱、commit 訊息——這些工程用的文件一律要用英文寫，這樣派到別的
地方跑的工具才讀得懂；只有這份給你看的報告本身，用你的語言寫。逐項核對
如下：

| 文件 | 有沒有守住英文規則 | 備註 |
|---|---|---|
| 計畫文件（plan.md） | 守住 | 全篇英文 |
| 規格文件（spec.md） | 不適用 | 這次改動標記「不需要規格」，本來就沒有這份文件 |
| 審查紀錄的意見（findings） | 不適用 | 這一輪審查目前還沒有任何一位讀者留下正式意見可核對 |
| 證據檔（對抗測試探針） | 守住 | 探針檔 `test_abuse_lane_declaration.py` 的說明文字全英文 |
| 測試裡的說明文字（docstrings） | 守住 | 抽查的測試檔說明文字全英文 |
| 測試名稱 | 守住 | 抽查到的名稱都照著「測試對象—狀態—預期結果」這種三段式在取名，例如
  `test_push_declared_express_lane_docs_skill_delta_single_reader_passes` |
| commit 訊息 | 守住 | 抽查的幾個 commit 主旨與內文全英文 |

這次改動沒有規格文件，所以「規格文件裡每一條需求都要對得回驗收條」這條
額外規矩不適用；審查紀錄的意見用「這句話是誰對誰提的、贊成或反對」那種
固定格式寫，這次還沒有意見可以核對這一條。

## 我不確定你是否想要的地方

- 「要不要找第二家 AI 覆核」跟「選什麼車道」目前是兩條分開算的規則，會不
  會讓你以為選了快速模式就一定不會被多問一次？
- PR 內文只留一行車道名稱，換車道當下的完整理由不會留在 PR 上，只留在
  對話裡——這樣夠不夠事後回頭查？
- gate-only 車道下完全沒有讀者看過這份改動，只靠寫程式的人自己寫的對抗
  測試和整包測試把關——這對你來說，安心的門檻夠不夠？
