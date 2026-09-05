# loom 每種文件各有定位、內容邊界與定稿後修改權
originator: kouko
kind: engineering
needs-design: no — engineering；會改的是 loom-code/contract/ 下的 .md 模板與說明、站 SKILL.md、agent 契約、checker 規則與測試；checker 的 interface-surface 重算把 templates/ 下的非程式檔排除，使用者讀或輸入的介面沒有改變
evidence: [docs/loom/2026-09-05-artifact-charter-boundaries-and-edit-rights/evidence/]
status: confirmed 2026-09-05

## Problem
loom 對每種文件只規定了「格式長什麼樣」，沒有規定「這份文件裝什麼、不裝什麼」以及「定稿之後誰能在什麼時候改哪一部分」，也沒有 checker 重算這兩件事。結果同一個模板的產物長度相差 18 倍，plan 在 build／review 期間被回頭寫成施工日誌，review.json 逐輪累積不清。

2026-09-05 量測（Python `len(str.split())`）：
- monkey-skills 最近 12 份 loom 1.0 plan.md：215–1,643 字，同一模板。
- 一個採用 loom 的 dbt 專案最新一份 1.0 plan.md：3,945 字，對應 intent 188 字（21 倍）。其中結尾 Risks 段 1,624 字（41%）全是帶日期的 build／review 期日誌與「LESSON」；另有三個帶 `landed: <sha>` 的事後追加 task（約 400 字）。同目錄 review.json 161 KB。
- task 本體 1,758 字裡 Risk 欄佔 54%、Test 欄佔 37%，Test 欄把情境 a–g 逐條敘述，Risk 欄寫成三段設計理由。
- 對照組 intent.md：有六段格式、EARS Acceptance、①確認後修改權（只有 maintain 回頭開新 intent）、checker 重算，長度穩定在 188–282 字。

三個缺口，缺一個就守不住：
1. **內容種類邊界**：模板只有欄位名（Files／Test／Risk），沒說每欄只能裝哪一類內容、溢出去哪。plan 於是變成第二份 spec。
2. **定稿後修改權**：build 站說進度從 git 推導、plan 沒有進度帳，允許的變動只有 blocked 標記與 W-memory task；但沒有一句肯定句說「其他都不可以」，fix-rounds 也沒說修正輪的紀錄住哪。
3. **執行機制**：以上兩層即使補了，若只是散文，reviewer 一個 omission finding（「plan 少講一個情境」）就能把它頂回去；reviewer 契約把 plan 當 ground truth 做雙向對帳，是長度的放大器。

## Proposed outcome
在 loom-code 的 contract 裡放一張**文件憲章**（artifact charter）：loom 會寫的每一種文件一列——intent、spec、plan、review.json、blind-run-report、memory 條目、KICKOFF-DEFAULTS、dispatch 紀錄——每列寫清楚（a）回答什麼問題、給誰讀（b）**正向**：必須寫哪些內容種類，缺了就是 omission（c）**負向**：不得寫哪些內容種類，每一種都指明它該住的那份文件，出現了就是 inconsistency（d）定稿點是哪個站、定稿後允許的變動清單（肯定句、窮舉）。正負向兩欄都不可留空：只寫正向，寫手會把所有東西都塞進去；只寫負向，寫手會漏掉承重內容。這張表是唯一正本；站 SKILL.md、模板、agent 契約只引用它的路徑，不重述。

在此之上：
- plan 三欄有內容種類定義與可重算的字數帽；checker 加規則比對 plan 內容樹，confirmed 後的變動只允許落在憲章列出的節點。
- review.json 的累積規則：每輪能新增哪些節點、哪些節點只能替換不能追加，checker 重算。
- reviewer／adversary／blind-runner／implementer 契約各加一行指向憲章；docs 鏡頭對 plan 的 omission 收窄為「implementer 拿那張單無法開工」，plan 含了 spec 才該有的內容算 inconsistency。
- 規格中途變更時的路徑寫成肯定句：回 write-spec 走②，替換未 landed 的 task，已 landed 的不動，原因一行進 Questions asked 或 review.json。

## Acceptance
1. 我可以在 loom-code 的 contract 裡打開一張表，每種 loom 文件一列，每列都有「該寫什麼、不該寫什麼（及其該去哪）、定稿點、定稿後允許的變動」四欄，沒有空格；「不該寫什麼」那欄每一條都指向另一份文件。
2. 我把那個 dbt 專案 3,945 字的 plan.md 拿給 checker，它會指出 Risks 段裡的事後日誌與 `landed:` task 是 confirmed 後不允許的變動，並說明每一條該搬去哪份文件。
3. 我把一份三欄都在帽內的 plan.md 拿給 checker，它通過；把 Test 欄擴寫成情境清單後再給它，它擋下並指出超帽的欄位。
4. 我拿一份舊的長 plan（kumiko 或該 dbt 專案）依憲章縮寫，冷派一個 implementer 給縮寫版與原版各一次，縮寫版回 NEEDS_CONTEXT 的次數不多於原版；報告附兩次派工的狀態回報。
5. 我用一份含「plan 少列一個測試情境」的假 finding 冷派 reviewer，它依收窄後的 omission 定義不把這條當 omission；用一份 plan 內含 REQ 重述的樣本冷派，它標 inconsistency 並指向憲章。
6. 我在 review.json 追加第二輪紀錄時，只有憲章允許追加的節點能長；對允許替換的節點追加第二份，checker 擋下。
7. 整包測試通過，write-plan SKILL.md 仍在 4,500 字帽內。

## Constraints
- 憲章只有一份正本，其他檔案只引用路徑；違者是第二漂移面。
- 判斷型規則必須配可重算的 checker 規則與 `<!-- gate: <id> -->` 標記，散文不當閘。
- 執行期散文不得引用本 repo 的 docs/ 開發紀錄（Contract Citations）。
- SKILL.md 4,500 字 CI 硬帽；憲章不進 SKILL.md。
- 模板檔會被實例化到 adopting repo，憲章文字不能跟著複製進產物。
- 內部文件英文（artifact-language-policy）；本 intent 與決策點對話用中文。
- 新的 checker 規則只對規則上線後 confirmed 的 intent 生效；已開著的舊變更照舊，不被突襲（使用者決定 2026-09-05）。

## Out of scope
- 回頭清理任何既有 repo 裡的舊 plan／review.json；它們是歷史紀錄。
- superpowers 時代「整段程式碼貼進 task」的模板；1.0 已移除。
- 修 CLAUDE.md 裡「子資料夾不可嵌套是 Anthropic 官方 convention」的出處說法。
- 改變三個人類決策點的數量或位置。

## Open questions
- Acceptance 4 的樣本選哪一份、縮寫由誰做（agent-decided，plan 記理由）。
