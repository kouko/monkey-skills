# reviewer／adversary 契約定位段＋讀者 finding 編探針＋角色觸發圖 — 我試了什麼、發生了什麼

2026-09-04 在乾淨的專案副本上試的：第一輪 commit `090ecf66`，第一次修正輪落地後重試 commit `6351711d`，第二次修正輪落地後再重試 commit `571f24f2`。

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
- **發生了什麼（第一輪，`090ecf66`）**：
  - 讀給讀者契約的那支模型，一句話說出的邊界是「只做對帳判讀……不自己動手修、也不自己寫探針」，分類結果：1→自己、2→對方、3→自己、4→自己、5→自己、6→對方、7→自己、8→實作者。8 條裡 7 條對，只有第 3 條（`./probe.py` 與 `probe.py` 算兩個 artifact）它判給自己，預期是對方的。
  - 讀給對抗者契約的那支模型，一句話說出的邊界是「攻擊可執行行為……從不做設計判斷、從不對帳，那是讀者的事」，分類結果：1→對方、2→自己、3→對方、4→對方、5→對方、6→自己、7→對方、8→實作者。同樣 8 條裡 7 條對，唯一錯的也是第 3 條——這次它判給對方（讀者），而不是自己。
  - 也就是說，兩份契約單獨讀起來都能讓 agent 正確說出邊界並分對 7/8，錯的那一條剛好是同一條，而且兩邊互踢皮球（都覺得那是「對方的事」）。
- **修正輪做了什麼**：對抗者段補上「empty, hostile or unnormalised input, forgotten state」這幾個具體的邊界類別；讀者段改成「anything provable by running a case belongs to the adversary or the implementer, not you」。這兩句都是針對第一輪冷讀漏接的第 3 條而補的。
- **第二輪重試（`6351711d`，同一份 8 條清單、同樣的呼叫方式）**：
  - 讀給讀者契約的模型這次分類：1→自己、2→對方、3→**對方**、4→自己、5→自己、6→對方、7→自己、8→實作者——**8 條全對**。它把第 3 條的理由寫成「探針如何被記錄與跑，是對抗者的地盤，不是我能光靠引用就判定的」。
  - 讀給對抗者契約的模型這次分類：1→對方、2→自己、3→**對方（讀者）**、4→對方、5→對方、6→自己、7→對方、8→實作者——仍是 7/8，第 3 條依然判給讀者而不是自己，理由是「怎麼算 artifact 是跨文件的帳務問題，不是可執行的攻擊」。
  - 也就是說：讀者契約補的那句話生效了，冷讀 8/8；對抗者契約補的「forgotten state」類別沒有把第 3 條的判斷拉過去，它仍然把「artifact 重複計算」讀成對帳而不是可執行案例。
- **第二次修正輪做了什麼**：對抗者段再補一句，把「probe 自己的 artifact 路徑（拼法或計數）」明講成對抗者自己的，「跨文件的計數」明講成讀者的——直接針對第 3 條那個兩邊互踢的模糊點。讀者段這次沒有再改分類相關的文字，只是把「產出是主張，靠修正輪確認」這句放回去（見下方「我幫你決定的事」）。
- **第三輪重試（`571f24f2`，同一份 8 條清單、同樣的呼叫方式）**：
  - 讀給讀者契約的模型這次分類：1→自己、2→對方、3→**對方**、4→自己、5→自己、6→對方、7→自己、8→實作者——**8 條全對**，維持第二輪的水準。
  - 讀給對抗者契約的模型這次分類：1→對方、2→自己、3→**自己**、4→**實作者**、5→**實作者**、6→自己、7→對方、8→實作者——**6/8**。第 3 條這次真的判給自己了，理由直接引用契約文字「a probe's own artifact path (its spelling or count) is yours」；但第 4、5 條（先前兩輪都正確判給「對方（讀者）」）這次改判成「實作者的」，理由是「這是驗收條件沒被滿足/文件遺漏的落差，是被建造出來的東西本身有落差」——把本來屬於讀者的「overclaim」「omission」判讀成了建置缺口。
  - 也就是說：第二次修正輪解決了第 3 條的模糊點（兩邊現在都正確認領它，不再互踢），但同一段新增的文字似乎讓對抗者這次的模型對「什麼算對抗案例、什麼算讀者的對帳」邊界判斷更模糊了，多錯了兩條原本答對的（4、5）。
- **證據**：
  - `docs/loom/2026-09-04-reviewer-and-adversary-positioning/evidence/coldread-reviewer.txt`（三輪原始回答都在，標了 TRIAL 1 / TRIAL 2 / TRIAL 3）
  - `docs/loom/2026-09-04-reviewer-and-adversary-positioning/evidence/coldread-adversary.txt`（同上）
  - `docs/loom/2026-09-04-reviewer-and-adversary-positioning/evidence/coldread-findings-list.txt`（三輪共用的同一份清單）
  - 分數：第一輪讀者 7/8、對抗者 7/8；第二輪讀者 **8/8**、對抗者 **7/8**（同一條第 3 條）；第三輪讀者 **8/8**、對抗者 **6/8**（第 3 條修好，第 4、5 條新錯）
- **結論**：partly（仍未完全做到）——讀者這邊自第二輪起穩定 8/8。對抗者這邊：原本卡住的第 3 條這次真的修好了，兩邊不再互踢；但補的那句話換來了新的模糊——這次的冷讀把「report 沒達到驗收條件」「文件遺漏說明」這兩條原本很清楚屬於讀者對帳工作的 finding，錯判成「實作者的建置缺口」。同一份契約冷讀三輪，還沒有一輪讓對抗者這邊 8/8。

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
- **發生了什麼（第一輪，`090ecf66`）**：讀者段 80 字（帽是 ≤80，剛好壓線）、對抗者段 61 字（帽 ≤80）、修正輪新段 58 字（帽 ≤60）——三段都在帽內。站摘要表測試 10 個案例全過（本次改動沒動到摘要表，符合預期）。版本從 `1.2.0` 升到 `1.2.1`。
- **修正輪之後重量（`6351711d`）**：修正輪為了補上 Acceptance 1 的邊界句，重寫了讀者段與對抗者段的文字。重新用 `len(str.split())` 數了一次：讀者段 **79 字**、對抗者段 **74 字**，都還在 ≤80 字帽內；修正輪那段文字沒有再改動。
- **第二次修正輪之後再重量（`571f24f2`）**：對抗者段補上「probe 自己的路徑歸自己、跨文件計數歸讀者」這句，讀者段把「產出是主張，靠修正輪確認」放回去。重新用 `len(str.split())` 數了一次：讀者段 **79 字**、對抗者段 **80 字**（貼著上限），都還在帽內。
- **證據**：
  ```
  # 090ecf66
  reviewer positioning para words: 80
  adversary positioning para words: 61
  fix-rounds new para words: 58
  10 passed in 0.13s
  plugin.json version: 1.2.1 (origin/main: 1.2.0)

  # 6351711d（重量）
  reviewer positioning para words: 79
  adversary positioning para words: 74

  # 571f24f2（再重量）
  reviewer positioning para words: 79
  adversary positioning para words: 80
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
- **冷讀撞到的邊界模糊點（上面 Acceptance 1 的第 3 條）在第二次修正輪修好了，但同一次修正換來了新的模糊點（第 4、5 條）** ——這是盲跑期間發現的事實，不是我幫你決定的事，但值得你知道：對抗者段補的「probe 自己的 artifact 路徑歸自己」這句，讓第三輪冷讀的對抗者正確認領了第 3 條，但同一輪它把原本兩輪都答對的「report 沒達到驗收條件」「文件遺漏說明」錯判成「實作者的建置缺口」，而不是它自己該讓給讀者的對帳工作。這不是我這次能動的範圍（契約文字已經寫定、我不能修改任何東西），留在下面的「你可能還沒想到的事」。
- **「your output is a claim the fix round confirms」這句原本在守 80 字帽時被拿掉，第二次修正輪已經放回讀者段** ——這句是 intent 的 Proposed outcome 2 裡明講要放進讀者定位段的內容之一（「產出是主張，靠修正輪確認」）。上一輪報告記過這句被拿掉；這次盲跑確認第二次修正輪的 commit `9c47fb58` 把它壓縮其他句子後放回去了，讀者段目前仍是 79 字，在帽內。這條記錄已經是過去式，寫在這裡是為了讓你知道之前的擔心已經處理。
- **不相關的開放 intent `docs/loom/intent/2026-09-04-prefer-harness-native-file-tools.md` 留在這條分支上** ——這是這次盲跑期間發現、但由你在這次 checkpoint 親自決定的事，不是我或任何 agent 幫你決定的：這份 intent 講的是另一件事（偏好 harness 原生檔案工具），目前狀態是 open、還沒實作，對這次 reviewer／adversary 定位改動的行為完全沒有影響。你的決定是先把它放在這條分支上，留到之後另開一個 change 再處理。如果你改變主意，之後隨時可以把它移到別的分支或直接處理掉，不影響這次已經完成的東西。

## 你可能還沒想到的事

- 「`./probe.py` 與 `probe.py` 算成兩個 artifact」這一條，在第二次修正輪之後已經修好——兩邊冷讀都正確認領它，不再互踢。但第三輪冷讀的對抗者出現了一個新的錯判：「report 沒達到驗收條件」「文件遺漏說明」這兩條原本兩輪都答對，這次被誤判成「實作者的建置缺口」而不是讓給讀者。也就是說補上「probe 自己的路徑歸自己」這句話，可能連帶讓對抗者模型對「什麼時候該讓給讀者」變得更謹慎、卻矯枉過正到不該讓給讀者的地方也讓了。如果要讓對抗者也穩定 8/8，這個新的模糊點還需要再看一次。
- 這次只驗證了「單獨讀一份契約檔」的冷讀效果，沒有驗證「同時讀到兩份契約檔」時 agent 會不會給出不同的分法——如果之後有需要，可以另外排一次兩份都給、看邊界句會不會互相干擾。
