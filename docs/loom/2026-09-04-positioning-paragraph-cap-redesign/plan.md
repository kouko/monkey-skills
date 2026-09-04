# 定位段字數帽改成句數帽＋對抗者段三方歸屬 — plan
intent: 2026-09-04-positioning-paragraph-cap-redesign@4ab5224d

## Current State Evidence
- Forward（契約）：`loom-code/agents/reviewer.md:13` 起的 `You own` 段 79 詞、3 句（21／31／27 詞）；`loom-code/agents/adversary.md:12` 起的 `You own` 段 80 詞、4 句（12／25／14／29 詞）。對抗者段沒有一句說「不是我的那些，誰的是讀者的、誰的是實作者的」。
- Forward（帽子）：`loom-code/scripts/test_review_station_text.py:50-63` 兩測斷言 `len(para.split()) <= 80`；同檔 `:66-87` 另外兩測（claim-fix-round、artifact-bookkeeping）各自也重複斷言 `<= 80`。畢業探針 `loom-code/scripts/test_probes_positioning.py:98`（`WORD_CAP = 80`，`:222-231` 用它）與 `test_probes_positioning_branch_end_r2.py:100`（`WORD_CAP = 80`；`:209` 上限、`:286-299` 斷言對抗者段 `== 80`「剛好在帽上」、`:424-450` 合成段 at-80／at-81 邊界）。`test_probes_positioning_branch_end.py` 不含 80 詞斷言（只提 reviewer.md 本體帽）。
- Forward（本體帽，不動）：`loom-code/scripts/test_reviewer_agent_single_contract.py:34` `AGENT_CAPS = {reviewer 1300, blind-runner 600, adversary 600}`，量 `body_of()`。現況 reviewer 本體 **1300/1300**、adversary 本體 502/600、blind-runner 503/600。→ 對抗者段加一句（約 20 詞）仍在 600 內；讀者段本次不加字。
- Reverse：讀這兩段的是 review 站 §2／§4 派工與 build §2 的探針先寫段；`fix-rounds.md` 那段（≤60 詞，`test_review_station_text.py:90`）與四契約的工具偏好句（≤40 詞，`:163-176`）是別的帽，本次不碰（intent Constraints）。
- Data（研究，本 change）：`evidence/research-paragraph-cap-unit.md`——GOV.UK 內容設計指南原文：一段 **≤5 句**、一句 >25 詞就拆［standard］；ASD-STE100「一段約 6 句」只有二手摘要、無編號原文；「一段幾個詞」沒有任何標準；IFScale（arXiv 2507.11538，2025）量到遵循度隨**指令數**下降且前段偏重［measured］；Levy 2024／Context Rot 2025 量到隨 token 長度下降［measured］；「段落佔全檔比例」零證據；句子切分用 regex（`. ` `? ` `! ` 之後、反引號外）＋縮寫例外可確定性測試，已知坑＝縮寫、小數、破折號子句。
- Data（冷讀歷史）：`docs/loom/2026-09-04-reviewer-and-adversary-positioning/blind-run-report.md:9,40-41`——方法＝兩支獨立 `claude -p --model sonnet`，各只給一份契約路徑，問 (a) 一句話邊界 (b) 把 `evidence/coldread-findings-list.txt` 的 8 條標成自己的／對方的／實作者的；三輪三方歸屬 7/8、7/8、6/8，own/not-own 第三輪 8/8。
- Boundary：不加 checker 規則、不動角色數、不動站摘要表；契約段不引用 `docs/` 路徑；詞數一律 Python `len(str.split())`，句數用測試明寫的 regex 規則，不用 wc。

## 單位決定（agent-decided，intent Open question 的答案）
- **句數帽：一段 ≤6 句；句長守衛：一句 ≤40 詞。** 舊的 ≤80 詞斷言移除，不並存。
- 為什麼是句數：intent 要的是「量這段講幾件事」——一句一個主張，句數是最近的代理；跨檔一致（不隨全檔長度變）；切分規則可寫死在測試裡。詞數量的是長度不是件數（這次的起因）；佔全檔比例零證據、且對 1355 詞 vs 564 詞兩檔天生不一致——皆不採。
- 為什麼 6 不是 GOV.UK 的 5：對抗者段補三方歸屬那句後是 5 句，設 5 又是「剛好裝得下」（intent Constraints：帽子要明顯高於需求）；6 是 ASD-STE100 二手摘要的數字，改完後兩段 3/6、5/6，各留 ≥1 句餘裕。
- 為什麼 40 不是 GOV.UK 的 25：現有最長句 31 詞（讀者段 2 句、對抗者段 1 句超過 25），25 會逼兩段重寫，違反 intent「讀者段不必改」；句長守衛的目的只是擋「用破折號把三件事塞進一句」的繞法（研究 Q5 的已知坑），40 ＝ 31 加三成餘裕。**這個 40 是拍的，沒有出處**，可逆；承重的是句數帽。
- 切句規則（測試 docstring 照抄；branch-end 修正輪追加）：先把反引號區段換成佔位符、把 `e.g.`／`i.e.`／`etc.`／`vs.` 的句點視為非終止；whitespace 正規化後以「終止符 `.!?…`（含 Unicode 刪節號）後面可選一個收尾引號／括號字元（直／彎雙引號、直／彎單引號、`)`、`]`），再接空白」切分（收尾字元留在被關閉的那句裡，不被切分吃掉）；非空片段數＝句數；每片段 `len(split())`＝句長（含佔位符，反引號內容算一個詞）。修正前的舊規則只切 `(?<=[.!?])\s+`，終止符後緊接收尾引號／括號或遇到刪節號時會漏切，讓句數帽低估。

## Task DAG

**W0-01 對抗者先寫探針**　after: —
- 檔：新增 `docs/loom/2026-09-04-positioning-paragraph-cap-redesign/evidence/probes/test_abuse_sentence_cap.py`（≥6 案例）。攻擊面：(1) 切句規則 oracle——合成段含反引號內句點、`e.g.`、小數、破折號子句、`?`／`!` 終止，各給預期句數；(2) 兩契約 `You own` 段各 ≤6 句、每句 ≤40 詞，且 `test_review_station_text.py` 不再含任何 `<= 80` 斷言；(3) 對抗者段有一句同時把「不是我的」分給讀者（含 omission／overclaim／contradiction 至少兩詞）與實作者（含 RED 或 implementer）；(4) 兩段不含 `docs/` 路徑；(5) 三個畢業探針檔不再有 `WORD_CAP = 80`／`== 80` 斷言，且合成邊界案例改成句數 6 過／7 紅、句長 40 過／41 紅；(6) plugin.json 版本 > 1.2.2 且 CHANGELOG 有該版；(7) 本體帽不變：adversary 本體 ≤600、reviewer 本體 ≤1300。實作前全紅、docstring 標 `RED until W1-0x`。
- 測：探針檔本身；記紅綠各幾條。
- 風：agent-decided——探針自帶一份切句規則實作（與 W1-01 的 helper 不共用），故意獨立，兩份對同一組合成案例得同答案才算 oracle 成立。

**W1-01 句數帽＋對抗者段三方歸屬＋站文字測試**　after: W0-01
- 檔：`loom-code/scripts/test_review_station_text.py`——加 `_sentences(para) -> list[str]` helper（規則照上節）、常數 `SENTENCE_CAP = 6`／`SENTENCE_WORD_CAP = 40`；`:50-63` 兩測改成句數＋句長斷言，docstring 寫明計算規則與依據（GOV.UK ≤5 句／>25 詞拆；6 與 40 的餘裕理由）；`:66-87` 兩測的 `<= 80` 改用同一對常數；新增一測斷言對抗者段含三方歸屬句（同 W0-01 (3) 的判準）。`loom-code/agents/adversary.md:12` 段末加一句（約 20 詞）：not yours 的分法——對帳類（omission、overclaim、contradiction）是 reviewer 的、正向可執行的 RED 是 implementer 的；不引用 `docs/`。讀者段不動。
- 測：W0-01 探針 (1)(2)(3)(4)(7) 轉綠；新增測試先紅（三方歸屬句不存在時）。
- 風：agent-decided——helper 放 `test_review_station_text.py` 而非新模組：規則只在這裡與探針用，開模組是投機抽象。對抗者段加句後 5/6 句、約 100 詞、本體約 524/600。

**W1-02 畢業探針同步到新單位**　after: W1-01
- 檔：`loom-code/scripts/test_probes_positioning.py`（`WORD_CAP` → 句數／句長常數與斷言）、`test_probes_positioning_branch_end_r2.py`（`:209` 上限改句數；`:286-299`「剛好在帽上」測改成「低於帽且 ≥1 句餘裕」；`:424-450` 合成 at-80／at-81 改成 6/7 句與 40/41 詞兩組 parametrize；docstring 內 80 的敘述同步）；對應的 `docs/loom/2026-09-04-reviewer-and-adversary-positioning/evidence/probes/` 原檔**不動**（已關閉 change 的工件，畢業副本才是活的）。切句 helper 由 `sys.path` 匯入 `test_review_station_text._sentences`，不第三次實作。
- 測：W0-01 探針 (5) 轉綠；整包 `python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q -n auto` 綠。
- 風：agent-decided——畢業檔與 evidence 原檔從此不再逐位元相同（原檔釘的是舊帽）；這是 intent Acceptance 4 明說的同步，不是漂移。`test_probes_positioning_branch_end.py` 沒有 80 詞斷言，不動。

**W1-03 版本與 CHANGELOG**　after: W1-01, W1-02
- 檔：`loom-code/.claude-plugin/plugin.json` 1.2.2→1.2.3、`loom-code/CHANGELOG.md` 一則（句數帽＋三方歸屬句＋探針同步）；marketplace／README 版本表照既有測試同步；`.codex/hooks/*` 鏡射用 `codex_scaffold.py` 重生（若版本字串在內）。
- 測：W0-01 探針 (6) 轉綠；整包綠。
- 風：改 skill 內容必 bump。

## Questions asked
1 — what — 你要的是把兩段定位段的字數帽從「剛好裝得下」改成「防漂移」，限制方式要換、單位在實作前研究後由我決定並附依據；騰出的餘裕在對抗者段補一句「不是我的那些誰是讀者的、誰是實作者的」；冷讀重跑一次記三方歸屬但不當驗收。對嗎？（答：對）
1 — consequence — 這次要不要用 Codex 當第二位讀者？多花幾分鐘與額度（答：用）
3 — consequence — branch-end 修正輪：讀者側冷讀兩次都錯同兩條（第 3、8 條），是措辭偏差不是雜訊；intent 說讀者段不動、驗收 3 又要讀者側 8/8，兩者衝突。A＝現在在讀者段補一句對稱的三方歸屬（砍 reviewer.md 別處約 25 詞或調本體帽、重跑冷讀、多一輪）；B＝不改、驗收 3 讀者側記未達、留給下一個 intent。（答：A）

## Risks
1. 一個 wave（W1），三 task 串行（W1-02 匯入 W1-01 的 helper、W1-03 最後）；W0-01 一個對抗者、工作樹直接做。checkpoint 只有 branch-end 一次（delta 遠低於 8 檔／400 行）。型別聯集 skill（adversary.md）＋code（測試）＋evidence（探針）→ 全車道：讀者一位 codex＋一位 sonnet，帶 skill＋code 鏡；second_vendor: codex。
2. 盲跑（Acceptance 3）：blind-runner 用 #787 同方法（兩支 `claude -p --model sonnet`、各只餵一份契約、同一份 8 條清單）；報告要分開寫 own/not-own（讀者、對抗者各 8/8 為驗收）與三方歸屬（記分、附 7/8、7/8、6/8 對照，**不當驗收**）。冷讀是單樣本，三方歸屬的分佈留給 2026-09-04-adversary-three-way-attribution-measured。
3. 切句規則是本 change 的新契約面：兩份獨立實作（探針、helper）對同一組合成案例必須同答案；破折號子句不切句是**刻意的**（句長守衛負責擋它）。
4. 句長 40 無出處（上節明講）；若對抗者攻出「40 擋不住的塞法」，修法是換設計（例如改 ≤35 或加子句數），不是補 token。
5. 同樹並行坑：branch-end 對抗者與盲跑者同時 commit——派工包寫「只路徑限定 commit、禁 amend」。
6. user-decided（branch-end 修正輪）——讀者段也補一句三方歸屬（intent「讀者段不必改」的例外，理由：兩次冷讀同兩條同理由＝系統性偏差，驗收 3 讀者側 8/8 否則不可達）。reviewer.md 本體 1300/1300：優先砍別處冗詞（不改任何義務詞）；砍不出來才把 `AGENT_CAPS["reviewer.md"]` 調到剛好夠、並在 commit 說明。
