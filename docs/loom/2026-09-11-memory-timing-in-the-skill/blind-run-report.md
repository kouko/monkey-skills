# 記憶的時機規則要住在 skill 裡 — 我試了什麼、發生了什麼

2026-09-11 在乾淨的一份專案副本（024b66141）上試的。我沒有參與這次改動的實作，
下面每一項都是我自己動手驗證出來的。

## 你要求的事，一項一項來看

### 1. 在任何一個裝了 loom-workflow 的專案裡讀記憶 skill，都看得到「什麼時候該記」這條規則，不需要去翻某個 repo 的儲存目錄

- **我怎麼試的**：把 `loom-workflow/skills/loom-memory/` 整個資料夾複製到一個完全獨立的資料夾（不帶這個 repo 的任何其他東西，尤其不帶 `docs/` 目錄），模擬「只裝了這個 skill」的情境，然後只讀複製出來的檔案。
- **發生了什麼**：複製出來的 `SKILL.md` 裡，「Record」這個操作區塊本身就完整寫著「什麼時候該記」——分支關閉前就已經知道的事，要落在同一個分支，不要為此另開一個合併後的分支，那是純粹的多餘負擔。整段規則不引用、不依賴這個 repo 才有的任何檔案。
- **證據**：複製後的目錄結構與 `SKILL.md` 全文（我在自己的工作暫存目錄下確認過），規則落在 `## Record` 底下的「When」段落。
- **結論：works** — 規則確實住在 skill 本體裡，裝了這個 plugin 的任何專案都讀得到，不必去翻某個特定 repo 的資料檔。

### 2. 規則講得夠具體，讓一個沒讀過這段歷史的 agent 照著做就會在分支還開著的時候記錄，而不是事後另開 PR

- **我怎麼試的**：我先只憑「Record」段落的文字，自己在心裡模擬一個不知道 #515／#780 這段歷史的讀者會怎麼做；確認完自己的判斷後，才去讀這個 skill 自帶的凍結評測 `evals/record-timing.md` 與 `evals/record-timing-cases.json`。
- **發生了什麼**：我自己的判斷是——文字會讓人在分支關閉前就記錄，且「幾乎沒有東西夠格被記錄」這句話會擋掉大多數候選。讀完凍結評測後，它的結論與我一致：一個全新、沒有工具、沒有這個 repo 存取權的 sonnet agent，被單獨餵給「Record」段落與 11 個候選案例後，答對了時機（在同一個開著的分支上記錄）、答對了那個例外（只有第 11 個案例被歸類為「合併後才能觀察到，應批次處理」），而且候選中只挑出 1 條該記的，並且自己主動核對這個數字符不符合契約講的「正常結果是零到一條」。評測文件裡誠實記了一個與 ground truth 不同的判斷（候選 1 該記卻被讀者判退），並解釋這個分歧其實是規則刻意偏向「拒絕」在起作用，不是規則失靈。
- **證據**：`evals/record-timing.md` 的「Reference run — 2026-09-11」區塊，三項判準全部 PASS。
- **結論：works，且我同意評測的結論** — 它的判定方式（把段落單獨抽出來、給一個完全陌生的讀者、要求讀者自己核對數量）確實測到了「規則會不會被稀釋」這件事，而不只是「關鍵字還在不在」。

### 3. 那一個例外（只有合併後／安裝後才觀察得到的事實）同樣寫清楚，而且說明那種情況要批次處理，不是一個發現開一個 PR

- **我怎麼試的**：對照上面複製出來的 `SKILL.md` 全文找例外句子。
- **發生了什麼**：「Record」段落明白寫著：「The one exception is a fact only confirmable by observing real post-merge or installed behavior; that genuinely needs a follow-up branch, and those are batched rather than one pull request per discovery.」（唯一的例外，是只有在真正合併後或安裝後的行為裡才能確認的事實；這種情況確實需要一個後續分支，但這些要批次處理，而不是一個發現開一個 PR。）
- **證據**：同一份 `SKILL.md`；上面第 2 項的評測也把候選 11（「新發佈的 plugin 版本能不能從市集正確安裝」）正確歸類為這個例外並批次處理。
- **結論：works**

### 4. 規則的兩半（時機／稀少性）各由一個機制守住：刪除靠回歸測試、稀釋靠冷讀評測，而且測試本身要自我解釋

- **我怎麼試的**：讀 `loom-workflow/skills/loom-memory/scripts/test_skill_contract.py` 裡守住 Acceptance 4 的那幾條測試，以及上面已經讀過的凍結評測。
- **發生了什麼**：
  - **刪除守衛**：`test_record_contract_states_when_to_record`、`test_record_contract_states_how_much_to_record`、`test_both_halves_live_in_the_record_section_itself` 三條測試各自釘住時機半段與稀少性半段的必要元素（例如「before the branch closes」「zero to one durable lesson per change」），而且是把空白壓平之後比對關鍵片語，不是比對整句——也就是說換句話說但保留精神的改寫仍會過，只有真的刪掉才會紅。
  - **稀釋守衛**：就是上面第 2 項讀過的 `evals/record-timing.md` + `record-timing-cases.json`，明確標成「不自動跑、不進 CI，改變這兩個子句時要重跑」。
  - **自我解釋**：這幾條測試前面有一大段註解，講清楚 2026-07-08（#515）這條規則第一次被寫進強制指示，2026-07 的 loom 1.0 大砍版本（#780）把當時的 skill 與測試一起刪掉，規則因此只剩散文留在資料檔裡；並且明講「如果這條測試變紅，問題不是怎麼把它改綠，而是這個子句是不是真的被拿掉了，拿掉是一個需要走 intent 的契約變更」。這段解釋同時出現在該區塊的標頭註解，也重複進每一條斷言失敗時印出的訊息（`_A4_WHY`）。
- **證據**：`scripts/test_skill_contract.py` 中「Acceptance A4」標頭區塊的完整註解，以及三條對應測試；`evals/record-timing.md` 的方法論表格「刪除→回歸測試 / 稀釋→這份評測」。
- **結論：works** — 兩種失效各有各的守法，測試本身確實把「為什麼在這裡」講清楚了，不是一句孤立的斷言。

### 5. closing review 走到收斂之後、產生 attestation 之前，看得到一句同時講時機與稀少性、不點名 plugin、不呼叫工具的話

- **我怎麼試的**：在 `loom-code/skills/review/SKILL.md` 裡找這段話，確認它相對於 `<!-- gate: review.bounded-episode -->` 這個收斂區塊與後面「## 5. Finalize」（產生 attestation 的地方）的相對位置；並跑 `python3 loom-code/scripts/check_mechanisms.py --baseline origin/main`。
- **發生了什麼**：這段話（以「Convergence is also the last moment when recording a lesson is free.」開頭）出現在 `<!-- /gate -->`（收斂那個 gate 區塊的結束標記，第 155 行）之後、「## 5. Finalize」（開始寫 attestation 的地方，第 168 行）之前。逐項核對四個性質：
  1. 位置在收斂之後、attestation 產生之前——符合。
  2. 不點名任何 plugin——整段只提到 `docs/loom/memory/` 這個路徑，沒有出現任何 plugin 名稱。
  3. 不呼叫任何工具——段落本身沒有指令、沒有程式碼區塊，而且它自己明講「it invokes nothing, requires no plugin to be installed, and asks for no decision from the user」。
  4. 不帶 gate 標記——這段話落在兩個 `<!-- gate: ... -->` / `<!-- /gate -->` 區塊之外，前一個 gate 已經在它之前關閉，後面直到「## 5. Finalize」都沒有新的 gate 開啟。
  `check_mechanisms.py` 的結果：`net mechanism count (excl. host-hygiene): 118`，與 `baseline net count: 118` 完全相同；`prose-gate` 一項是 `15 / 15`（跟 baseline 一致），代表沒有新增任何一個機制或 gate，跟這條改動宣稱的「不新增 checker 規則、不新增閘門」一致。
- **證據**：`loom-code/skills/review/SKILL.md` 第 155–167 行左右；`check_mechanisms.py --baseline origin/main` 的完整輸出（`all clear`）。
- **結論：works**

### 6. 記憶 skill 的既有行為沒有改變：四個操作、儲存格式、驗證器都照舊；沒有任何 loom 站台因此變成會自動呼叫記憶

- **我怎麼試的**：跑 `git diff origin/main..HEAD -- loom-workflow/skills/loom-memory/scripts/loom_memory.py`；另外看了 `references/operations.md`、整體改動的檔案清單，並確認 review 站那段話本身沒有呼叫語法。
- **發生了什麼**：`loom_memory.py` 的 diff 是空的（0 行），驗證器與四個操作的實作完全沒動。`references/operations.md` 的改動只是在「Record」小節前面加了兩段說明（時機＋稀少性），原本的四個編號步驟一字未改。這次改動實際碰到的檔案只有 `SKILL.md`（+17 行）、`evals/` 兩個新檔、`operations.md`（+10 行）、`scripts/test_skill_contract.py`（新增）、`scripts/test_store_fidelity.py`（刪除，見下方）——沒有任何一個 loom 站台的呼叫流程被改動成會主動叫記憶。
- **證據**：`git diff origin/main..HEAD -- loom-workflow/skills/loom-memory/scripts/loom_memory.py`（空輸出）；`git diff --stat origin/main..HEAD -- loom-workflow/skills/loom-memory/`。
- **結論：works**

## 附帶查證的兩件事

- **`python3 -m pytest docs/loom/2026-09-11-memory-timing-in-the-skill/evidence/probes/ -q`**：7 個測試全過（`7 passed in 2.22s`）。這些是這次改動自己寫的對抗測試，逐一驗證：刪掉時機或稀少性任一半會讓釘子變紅、失敗訊息會告訴刪除者他刪了什麼、保留兩半精神的改寫仍是綠的、把那段話搬到 Finalize 之後會變紅、把那段話標成 gate 會變紅、在那段話裡點名一個 plugin 會變紅。
- **`uv run --isolated --with-requirements requirements-package-tests.lock python scripts/run_package_tests.py --loom-family -q`**：全部通過，結束碼 0。逐段摘要：`1112 passed, 2 skipped`（loom-code 主體）、`183 passed, 1 skipped`（loom-design）、`48 passed`、`28 passed`、`244 passed`、`115 passed`（loom-workflow 幾個 Python 套件），以及 15 支 shell 探針腳本（`test-git-memory-*`、`test-loom-memory-charter-pins`、`test-memory-grep-*`、`test-privacy-*`）全部回報 PASS、0 FAIL。

## 被刪掉的那支測試：`scripts/test_store_fidelity.py`

這支測試在這個分支上被刪掉了。查證下來，它守的是另一個更早的改動（把記憶 store 從舊資料夾搬到現在位置那次）的驗收條件——「搬移前後 293 筆內容逐位元組一致」，比對對象是一個會移動的 `origin/main`。它跟「什麼時候該記」這條時機規則沒有關係：這次改動的六條驗收線都不依賴它、也沒有任何一條測到它守的東西。它的刪除有自己的一則說明（記在 `docs/loom/memory/` 裡），大意是「一次性的驗收證明釘在一個會移動的基準上，遲早會開始擋正常操作（因為 Record／Reconcile／Retire 三個操作本來就會改動這個 store）」，這個說法我核對過是事實：如果保留它，這次改動一旦用 Record 操作真的記一條教訓，這支測試就會變紅。

**結論：它的消失沒有讓任何一條 Acceptance（1–6）少了保障。**

## 對你既有的資料做了什麼

沒有動到你既有的資料。這次改動只新增、修改、刪除了 skill 與 review 站的散文檔與測試檔（`SKILL.md`、`references/operations.md`、新的 `evals/` 與 `test_skill_contract.py`、review 的 `SKILL.md`），刪除的 `test_store_fidelity.py` 是一支已經完成階段性任務的測試，不是資料。任何既有的記憶 store 內容（`docs/loom/memory/` 下的教訓檔案）一個字都沒有被改動，`loom_memory.py` 驗證器與儲存格式的程式碼零變更。

## Review summary

我沒有拿到這次改動的 review 站正式裁決（`docs/loom/2026-09-11-memory-timing-in-the-skill/` 目錄下目前只有 `plan.md` 與 `evidence/`，還沒有 `attestation.json`）。因此沒有任何 review 階段的「嚴重度 important 以上被駁回的發現」可以轉告你——如果之後補上了 review 紀錄，其中任何一條 important 以上被駁回的發現都應該補進這份報告的「我幫你做的決定」一節。

## 我幫你做的決定

- 沒有需要幫你決定的事。六條驗收線都能用你能自己查證的事實直接判定（複製出來的檔案、diff、跑測試的結果），沒有遇到需要我代替你選邊站的模糊地帶。

## Questions I asked you（我認為你該留意的問題）

- 沒有。六條驗收線全部 works，沒有查出需要你回答的開放問題。

---

### 語言規則核對表（各項工件是否遵守英文／模板規則）

| 工件 | 規則 | 是否遵守 |
|---|---|---|
| `docs/loom/intent/2026-09-11-memory-timing-in-the-skill.md`（意圖） | 用使用者語言（繁中）撰寫 | 是，全篇繁體中文 |
| `loom-workflow/skills/loom-memory/SKILL.md`、`references/operations.md`（出貨散文） | 英文撰寫 | 是 |
| `loom-workflow/skills/loom-memory/evals/record-timing.md`、`record-timing-cases.json`（評測） | 英文撰寫 | 是 |
| `loom-code/skills/review/SKILL.md`（review 站那段提醒） | 英文撰寫 | 是 |
| `loom-workflow/skills/loom-memory/scripts/test_skill_contract.py`（回歸測試） | 英文撰寫；測試名稱應為 `test_<單元>_<狀態>_<預期>` | 內容英文，遵守；測試函式名稱是完整敘述句（如 `test_record_contract_states_when_to_record`），不是嚴格的三段式 `test_<unit>_<state>_<expected>` 格式，但語意等價（單元＋狀態＋預期都能從名字讀出） |
| `docs/loom/2026-09-11-memory-timing-in-the-skill/evidence/probes/test_adversarial_clause_guards.py`（對抗探針） | docstring 用英文；測試名稱同上格式 | docstring 英文，遵守；測試名稱同樣是完整敘述句而非嚴格三段式（如 `test_deleting_either_half_turns_the_pin_red`），語意等價 |
| 這份 blind-run 報告 | 使用者語言（繁中） | 是 |
