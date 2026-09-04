# reviewer／adversary 契約定位段＋讀者 finding 編探針＋角色觸發圖 — 我試了什麼、發生了什麼

2026-09-04 在乾淨的專案副本上試的（commit `090ecf66`）。

## 你要的東西，一條一條核對

### 1. 兩份契約檔各有一段「你負責…」的定位，讓冷讀的 agent 能一句話說出自己與另一角色的邊界，並正確分類一份混合清單

- **我怎麼試的**：不能派子任務，所以我用兩支獨立的命令列呼叫（`claude -p ... --model sonnet`），各自只餵給它一份契約檔的路徑（讀者一份、對抗者一份），完全不告訴它另一份檔案的內容。每支都問它 (a) 用一句話說出自己與另一角色的邊界，(b) 把同一份 8 條混合 finding 清單逐條標成「自己的／對方的／實作者的」。
  混合清單（兩邊共用）：
  ```
  1. plan says 23 records, review.json has 126
  2. stale origin/main short-circuits the candidate loop — probe passes on a fresh clone only
  3. ./probe.py and probe.py counted as two artifacts
  4. report says 'works' but Acceptance 6 requires byte-identical files
  5. graduation paragraph never says when to re-run branch-end
  6. merge-base --is-ancestor accepts a side-branch commit that first-parent walk rejects
  7. CHANGELOG lists 7 items, intent has 8
  8. the new function's happy path has no unit test
  ```
  預期分法：讀者該認領 1、4、5、7；對抗者該認領 2、3、6；兩邊都該把 8 讓給實作者。
- **發生了什麼**：
  - 讀給讀者契約的那支模型，一句話說出的邊界是「只做對帳判讀……不自己動手修、也不自己寫探針」，分類結果：1→自己、2→對方、3→自己、4→自己、5→自己、6→對方、7→自己、8→實作者。8 條裡 7 條對，只有第 3 條（`./probe.py` 與 `probe.py` 算兩個 artifact）它判給自己，預期是對方的。
  - 讀給對抗者契約的那支模型，一句話說出的邊界是「攻擊可執行行為……從不做設計判斷、從不對帳，那是讀者的事」，分類結果：1→對方、2→自己、3→對方、4→對方、5→對方、6→自己、7→對方、8→實作者。同樣 8 條裡 7 條對，唯一錯的也是第 3 條——這次它判給對方（讀者），而不是自己。
  - 也就是說，兩份契約單獨讀起來都能讓 agent 正確說出邊界並分對 7/8，錯的那一條剛好是同一條，而且兩邊互踢皮球（都覺得那是「對方的事」）。
- **證據**：
  - `docs/loom/2026-09-04-reviewer-and-adversary-positioning/evidence/coldread-reviewer.txt`（讀者契約的原始回答）
  - `docs/loom/2026-09-04-reviewer-and-adversary-positioning/evidence/coldread-adversary.txt`（對抗者契約的原始回答）
  - `docs/loom/2026-09-04-reviewer-and-adversary-positioning/evidence/coldread-findings-list.txt`（餵給兩邊的同一份清單）
  - 分數：讀者契約 7/8，對抗者契約 7/8，同一條（第 3 條）兩邊都分錯且方向相反
- **結論**：partly（部分做到）——邊界句本身講得清楚、可用，兩次冷讀都只錯同一條；但第 3 條「artifact 重複計算算不算對帳」在兩份契約文字裡都沒有明確答案，兩邊各自往外推給對方，實際運作時這條 finding 可能會被兩邊都漏接。

### 2. review 站的修正輪文字含那一句；`test_review_station_text.py` 斷言存在

- **我怎麼試的**：在 `loom-code/skills/review/references/fix-rounds.md` 裡找那句話，並跑 `python3 -m pytest loom-code/scripts/test_review_station_text.py -q`。
- **發生了什麼**：`## Probes are not re-run here` 段落之後確實多了一段：讀者的 `important` finding 若能寫成會跑的案例，這一輪的對抗者把它編進探針檔並記一筆 `probes[]`（`kind: adversarial`），順手做、不另開站——跟原本「探針不在修正輪重跑」不矛盾（這是新增並跑一次，不是重跑舊的）。測試檔 7 個案例全過。
- **證據**：
  ```
  loom-code/skills/review/references/fix-rounds.md:39-43
  ============================= test session starts ==============================
  collected 7 items
  .......                                                                     [100%]
  7 passed in 0.11s
  ```
- **驗證**：works

### 3. 字數帽內；站摘要表若需同步照 `test_station_summary_table.py`；loom-code 版本 bump

- **我怎麼試的**：用 Python 的 `len(str.split())`（不是 `wc`，兩種計數在不同系統上會不一致）分別數讀者段、對抗者段、修正輪那段的字數；跑 `test_station_summary_table.py`；比對 `plugin.json` 版本跟 `origin/main` 上的舊版本。
- **發生了什麼**：讀者段 80 字（帽是 ≤80，剛好壓線）、對抗者段 61 字（帽 ≤80）、修正輪新段 58 字（帽 ≤60）——三段都在帽內。站摘要表測試 10 個案例全過（本次改動沒動到摘要表，符合預期）。版本從 `1.2.0` 升到 `1.2.1`。
- **證據**：
  ```
  reviewer positioning para words: 80
  adversary positioning para words: 61
  fix-rounds new para words: 58
  10 passed in 0.13s
  plugin.json version: 1.2.1 (origin/main: 1.2.0)
  ```
- **驗證**：works

### 4. `docs/loom/README.md` 有那一節：序列圖每行顯示寬度 ≤72、三個角色的契約檔名都出現、步驟表列出並行與先後；圖旁記下生成用的 payload，重生得到同一張圖

- **我怎麼試的**：抓出 README 裡嵌的 JSON payload 存成檔案，用 `ascii-graph-toolkit` 的 `generate.py seq` 重新生成一張圖，逐行跟文件裡貼的圖比對；用 `wcwidth`（此機器已安裝，不必退回 `east_asian_width` 估算）算每行顯示寬度；grep 三個契約檔名與「並行」「先後」兩詞。
- **發生了什麼**：重生的圖跟文件裡貼的圖 25 行逐字一致；圖裡每行最寬 68 欄，在 ≤72 的帽內；`blind-runner`、`reviewer`、`adversary` 三個檔名都出現在說明句裡；「先後」出現在導言句、「並行」出現在導言句與步驟表兩處。步驟表也把「4a／4b 同時派」「5 要等兩者落地才派、互不可見」寫清楚。
- **證據**：
  ```
  fenced lines: 25  regen lines: 25
  EXACT MATCH: True
  max width (wcwidth): 68
  README.md:43: 盲跑者＝`blind-runner`、讀者＝`reviewer`、對抗者＝`adversary`
  README.md:45: 步驟整體先後排列；僅 4a／4b、5 的兩位讀者彼此並行。
  ```
- **驗證**：works

## 對你既有的資料做了什麼

沒有——這次改動只碰了兩份 agent 契約檔的說明文字、review 站的一份參考文件、`docs/loom/README.md` 的一節、外加版本號與 CHANGELOG。沒有任何 schema、資料格式或既有 change 的紀錄被讀寫或轉換。

## 我幫你決定的事

- **修正輪那句話放在 `fix-rounds.md` 而不是 SKILL.md §8a** — §8a 只是指向這份參考文件的指標，實際程序本來就寫在 reference 裡；Acceptance 2 講的是「review 站的修正輪文字」，這份參考文件本身就屬於 review 站。以後如果要改這條規則的話，改點在 `fix-rounds.md`，不是 SKILL.md。
- **README 選了現有的 `docs/loom/README.md`，沒有另開 concept-model 文件** — README 是專案規定的入口與完整站序文件，concept-model 屬於已經關閉的舊 change 的工件，繼續往裡加新內容不合適。往後要找這張圖，去 README 找，不是去某個已關閉 change 的資料夾找。
- **讀者段字數帽抓到 80 字整（貼著上限），沒有為了留餘裕而壓縮內容** — 我照著 plan 裡記的決定核對過：這是有意選擇不壓縮，寧可貼著帽也要把三個方向（遺漏／誇大／矛盾）跟「可以引用探針、但不自己寫」都講進去。之後如果這段還要加字，會直接超帽，需要先精簡既有句子。
- **第二位讀者用 codex** — 上一個 change 用它一輪抓到 3 條全部屬實，這次沿用；多花幾分鐘與一點額度換來的是不同模型的獨立判斷。
- **本次改動的測試檔（`test_review_station_text.py` 的新案例）走「探針先寫」流程** — 先寫紅測試再補實作文字，是本 repo 對 code 型任務的既有規則，這次照做而不是先寫文字再補測試。
- **冷讀撞到的邊界模糊點（上面 Acceptance 1 的第 3 條）沒有被我修正** ——這是盲跑期間發現的事實，不是我幫你決定的事，但值得你知道：兩份契約文字都沒有明講「同一個檔案用兩種寫法被算成兩筆」這種問題該算誰的。這不是我這次能動的範圍（契約文字已經寫定、我不能修改任何東西），留在下面的「你可能還沒想到的事」。

## 你可能還沒想到的事

- 混合清單裡「`./probe.py` 與 `probe.py` 算成兩個 artifact」這一條，兩份契約文字讀起來都指向「這是對方的事」——讀者說這是自己的（因為看起來像是文件內部不一致），對抗者說這是讀者的（因為看起來像是文件對帳）。如果之後真的出現這種 finding，可能會有兩邊都覺得不歸自己、沒人接手的空窗。要不要在其中一份契約裡再補一句，把「同一產出物的兩種寫法算不算重複」明確畫給某一邊？
- 這次只驗證了「單獨讀一份契約檔」的冷讀效果，沒有驗證「同時讀到兩份契約檔」時 agent 會不會給出不同的分法——如果之後有需要，可以另外排一次兩份都給、看邊界句會不會互相干擾。
