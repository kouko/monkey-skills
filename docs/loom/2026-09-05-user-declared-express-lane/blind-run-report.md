# 使用者宣告車道（full／express／gate-only）——我試了什麼、發生了什麼

在 2026-09-05 試的，用的是一份乾淨複製的專案。第 5、6、7 條驗收在版本
`d31484fa` 上試的；第 1-4 條經過兩輪對抗修正，最後一次在版本 `19b8c4e8`
上重新試過（同樣是乾淨複製）——這一版把 gate-only 的定義改窄了：它現在
是「small 車道拿掉讀者下限」，不是另一種獨立、範圍較窄的東西；而且宣告
車道那一行現在強制要帶日期（`lane: <名> — declared <日期> by <人名>`），
沒帶日期的一行會被拒絕。

**先說範圍**：這次試的是這個改動的「wave 1」——car 車道宣告、切換規則、
車道重算、review／build／ship 三站的文字。改動計畫裡還排了「wave 2」
（版本號更新到 1.6.0、記憶步驟），但那部分還沒做出來，這次不試也不評論。

## 你要的東西，一條一條試

### 1. intent 範本要有 `lane:` 說明；KICKOFF 範本要有 `default-lane:` 說明；切換 commit 沒帶那一行就要擋（本輪改為：宣告一定要帶日期）
- **怎麼試的**：打開兩份範本檔看說明文字，確認宣告的寫法已經改成「一定
  要帶日期與人名」；接著自己動手做三個小實驗——（a）寫一個帶
  `lane: express — declared 2026-09-05 by kouko`（帶日期）的 intent，
  commit 訊息裡「有寫」那一行，跑一次 checker 的 `intent` 檢查；（b）寫一
  個只寫 `lane: express`（沒有日期、沒有人名）的 intent，跑同一個檢查，
  期待被拒絕；（c）重跑一次「切換 commit 沒帶那一行」的舊實驗，確認換了
  日期格式後這條規則還在。
- **發生了什麼**：intent 範本裡的說明已經改成「宣告一定要帶日期與人名，
  沒有日期的寫法不合法」；KICKOFF 範本裡的 `default-lane:` 說明沒變。
  （a）帶日期的宣告，通過（結束碼 0）。（b）只寫 `lane: express`（沒日
  期）被兩條規則同時擋下：一條說「這個寫法不合語法，沒有日期的車道名稱
  不是合法值」，另一條說「commit 訊息沒有帶著這一行」（結束碼 1）——也就
  是說，現在光靠寫日期還不夠，寫法本身也要合語法，改動的 commit 訊息也
  要照樣抄一次。（c）帶日期的切換 commit，如果訊息漏寫那一行，一樣被擋
  （結束碼 1），跟以前的規則邏輯一致，只是引號裡的原文換成了帶日期版本。
- **證據**：範本檔 `loom-code/contract/templates/intent.md` 第 8 行、
  `loom-code/contract/templates/KICKOFF-DEFAULTS.md` 第 17 行；三個手動實
  驗分別在
  `/Users/kouko/.claude/jobs/f14c84f2/tmp/rerun3-templates`（帶日期通過，
  結束碼 0）、
  `/Users/kouko/.claude/jobs/f14c84f2/tmp/rerun3-bare-lane`（無日期被擋，
  印出「`lane: express` does not match the declared grammar ... a bare
  lane name with no dated attribution is not a legal value」以及「commit
  ... 沒有帶著 `lane: express` 這一行」，結束碼 1）、
  `/Users/kouko/.claude/jobs/f14c84f2/tmp/rerun3-switch-missing-line`
  （帶日期的切換 commit 漏寫那一行被擋，印出「commit ... 沒有帶著
  `lane: express — declared 2026-09-05 by kouko` 這一行」，結束碼 1）。
- **結論**：符合（規則升級為「一定要帶日期」，行為一致重新驗過）。

### 2. 沙盒：宣告 `express` 的 docs／skill 類改動，只有一位讀者，過閘要成功；同一份改動再動 checker 一行，要變回擋下
- **怎麼試的**：自己搭一個小的假專案，寫一份帶日期的
  `lane: express — declared 2026-09-05 by kouko` 的 intent，改一份 docs
  檔和一份 skill 檔，只記一位讀者的審查結果，跑「過閘」指令；接著在同一份
  改動再多改一行 checker 本身的程式碼，重跑一次過閘指令。這是第三次驗這
  一條——前兩輪對抗修正之後，這次改用新的「一定要帶日期」寫法，在最新版本
  `19b8c4e8` 上把兩步整個重搭一次沙盒重跑。
- **發生了什麼**：跟前兩次試的結果一樣：第一次過閘指令回傳成功（結束碼
  0）；加了 checker 那一行之後回傳失敗（結束碼 1），並印出「因為改到了
  `loom_checker.py`（非測試程式碼），車道被強制拉回 full，需要 2 位讀
  者，現在只有 1 位」——這條規則從頭到尾沒有被任何一輪修法動到，只是宣告
  的寫法換成了帶日期版本。
- **證據**：第一輪手動實驗在
  `/Users/kouko/.claude/jobs/f14c84f2/tmp/manual-express-repo`；第二輪重
  新驗證在 `/Users/kouko/.claude/jobs/f14c84f2/tmp/rerun2-express-repo`；
  這次（帶日期寫法）重新驗證在
  `/Users/kouko/.claude/jobs/f14c84f2/tmp/rerun3-express-repo`；也用專案
  自帶的對抗測試檔 `test_abuse_lane_declaration.py` 整份重跑過，全部通過
  （`pytest ... -q` → `11 passed`）。
- **結論**：符合。

### 3. 沙盒：宣告 `gate-only` 的純 docs 改動，零讀者也能過閘（但要有 ≥3 個對抗測試和一次整包測試紀錄）；同一份改動加一個 SKILL.md 檔要擋下（本輪改為：gate-only 現在等於「small 車道、拿掉讀者下限」）
- **這一條的規則變了，先說清楚**：gate-only 現在不是一種獨立的、有自己一
  套准入名單的車道，而是「這份改動本來（不管有沒有宣告）就會被算成 small
  車道時，讀者下限額外歸零」。換句話說：只要這份改動的內容讓 checker 自
  己重算出來就已經是 small（純測試、純文件、CI／設定、版本同步、乾淨
  revert 這幾類），宣告 gate-only 才會生效；只要delta 裡有任何一樣東西讓
  checker 自己算出來是 full——不管是一份像 `KICKOFF-DEFAULTS.md` 這樣的
  「常設文件」、第二個外掛目錄、一般程式碼、gate／skill／agent 契約檔，
  還是 interface-surface 路徑——gate-only 這個宣告就直接被忽略，車道退回
  full，讀者下限變回 2。
- **怎麼試的**：搭三個獨立的假專案，跑三種情境——（a）一份原本就會被算成
  small 的純 docs 改動，宣告帶日期的 `lane: gate-only`，零讀者、3 個對抗
  測試紀錄、1 個整包測試紀錄，跑過閘，期待成功；（b）同一種改動，但這次
  多加一份一般用途的 `.py` 程式檔（非測試），跑過閘，期待被擋，而且擋的
  理由要點名是哪一個檔案；（c）同一種改動，但這次改動的內容本身包含了
  `KICKOFF-DEFAULTS.md`（常設文件）的編輯，跑過閘，期待被擋。
- **發生了什麼**：（a）成功（結束碼 0）。（b）失敗（結束碼 1），工具印出
  這一行（原文）：「BLOCK push.verdicts-ge-2: full lane: review round 0
  carries 0 distinct reviewer(s) with a readable verdict; 2 required
  (gate-only needs a small-lane delta: src/module.py is non-test code).」
  ——點名了確切是哪一個檔案讓 gate-only 失效。（c）也失敗（結束碼 1），
  工具印出：「... (gate-only needs a small-lane delta:
  docs/loom/KICKOFF-DEFAULTS.md is a standing document.)」——同一句話的
  結構，換成點名 KICKOFF 這份常設文件。三種情境都跟這一輪改動想要達成的
  行為一致。
- **證據**：三個手動實驗分別在
  `/Users/kouko/.claude/jobs/f14c84f2/tmp/rerun3-gateonly-repo2`（情境 a、
  b，兩者疊在同一個分支上，先驗 a 成功，再加程式檔驗 b 失敗）、
  `/Users/kouko/.claude/jobs/f14c84f2/tmp/rerun3-gateonly-repo3`（情境
  c，KICKOFF-DEFAULTS.md 的編輯本身就在被驗的改動範圍內）；另外
  `pytest docs/loom/2026-09-05-user-declared-express-lane/evidence/probes/
  test_abuse_lanes_wave_end.py -k
  "gateonly_dated_declaration_nontest_code_in_delta_blocked or
  gateonly_dated_declaration_standing_doc_touch_now_blocked"` 也各自通
  過，跟手動重跑的結果一致。
- **結論**：符合（gate-only 的定義已經改窄，三種情境都照新定義驗證過）。

### 4. 沙盒：做到一半換車道——前面兩輪照舊兩位讀者，換車道之後那一輪起變一位讀者可通過；換車道那個 commit 沒帶那一行要擋（本輪：換車道的計時規則改了）
- **這一條也有規則變化**：以前「從第 2 輪起換」是照「輪數編號」比大小，
  這次改成照「這個 change 到目前為止，已經記錄過哪些（範圍、輪數）的組
  合」來判斷——不然一旦審查輪重新編號（例如修正輪不算進正式輪數），舊算
  法會把後面所有輪次都誤判成「還沒輪到」，永遠卡住。另外沒有寫成切換格式
  的「單純宣告」（`lane: express — declared <日期> by <人名>`），現在的
  生效時機跟`from wave <n>`的切換是同一套算法：只套用在「宣告這個動作發
  生之後才記錄的（範圍、輪數）」，宣告當下已經存在的紀錄不受影響。
- **怎麼試的**：跑專案自帶對抗測試檔裡針對這個新算法建好的四個情境（含
  「宣告發生在檢查點關閉之後」「宣告發生在檢查點進行中」等邊界案例），
  另外自己動手重跑一次「換車道 commit 沒帶那一行」的情境（改用最新版本
  `19b8c4e8`），並把兩份對抗測試檔整份重跑一次。
- **發生了什麼**：四個情境都符合新算法的預期。手動重跑「commit 沒帶那
  行」的情境，工具印出「commit ... 沒有帶著 `lane: express — declared
  2026-09-05 by kouko` 這一行」並擋下（結束碼 1）——只是引號裡的原文換成
  了帶日期版本，行為邏輯沒變。兩份對抗測試檔分別跑出 `11 passed`（原本
  那份）和 `23 passed`（記錄這兩輪全部問題的那份，這次比上一輪多了 9
  項，因為新一輪對抗又多寫了幾個情境），一項沒有紅。
- **證據**：`pytest test_abuse_lanes_wave_end.py -k "from_wave or
  bare_lane_declaration_at_new_checkpoint"` → `4 passed`；手動重跑在
  `/Users/kouko/.claude/jobs/f14c84f2/tmp/rerun3-switch-missing-line`；
  兩份對抗測試檔整份重跑：`test_abuse_lane_declaration.py` → `11 passed`、
  `test_abuse_lanes_wave_end.py` → `23 passed`。
- **結論**：符合（計時算法已經改成不受輪數重編號影響，重新驗證過）。

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
- **gate-only 被改窄成「small 車道拿掉讀者下限」，不是它原本設計的那個
  獨立範圍** —— 一開始的設計是「gate-only 有自己一套准入名單，跟 full／
  small 的判斷分開算」；試跑到一半發現這樣會漏掉一種情況（一份改動明明
  已經被系統自己算成 full，卻因為使用者宣告了 gate-only 而被錯誤放行）
  之後，把設計改成「gate-only 只是 small 車道少了讀者這一件事」，並把這
  個決定寫進了公司規章（PRINCIPLES.md 第 2 條），要使用者親自點頭認可過
  才生效。對你的影響：以後想宣告 gate-only 的改動，範圍會比原本設計的更
  窄——只有系統本來就會判定為「small」的改動（純測試、純文件、CI／設定、
  版本同步、乾淨 revert）才能選 gate-only；連改一份像 KICKOFF-DEFAULTS.md
  這樣的「常設設定文件」都會讓 gate-only 整個失效、退回完整審查。這不是
  我一個人決定的——這條規則被正式寫進了 PRINCIPLES.md，需要你本人簽核；
  如果你還沒看過那句話，這裡先提醒你去確認一下。
- **宣告車道現在強制要帶日期，舊的「只寫車道名稱」寫法直接不合法** —— 這
  也是試跑途中發現的問題：如果宣告不用寫日期，工具沒辦法區分「這是使用
  者今天決定的」還是「這行字放了三個月都沒人管」。對你的影響：以後宣告
  車道，一定要照著 `lane: <名稱> — declared <日期> by <你的名字>` 這個
  格式寫，少了日期或名字，intent 檢查會直接擋下、不會被當成有效宣告。

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
