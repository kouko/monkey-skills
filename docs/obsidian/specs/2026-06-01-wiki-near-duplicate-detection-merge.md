# Brief — obsidian wiki near-duplicate detection + guided merge (L15 + wiki-merge)

> Status: brainstorming complete, awaiting writing-plans.
> Date: 2026-06-01 · Target plugin: `obsidian` (wiki-* skills) · dbt-wiki NOT in scope.

## Problem
(Axis 1 — JTBD)

obsidian wiki 的 fan-out 架構靠「一個實體一頁 canonical」成立。但去重**只在 ingest 當下 slug 字串完全相等時觸發**(wiki-ingest STEP 4c)。一旦 LLM 兩次 ingest 把同一實體算出不同 slug(`Thompson-Sampling` vs `Thompson-Sampling-MAB`),三層防線(ingest STEP 4c / cross-linker / wiki-lint 14 項)**全部漏掉**,且 L06 會把重複頁當「孤兒」→ 建議 cross-linker 連起來 → **坐實重複**。

Job story: **當**我長期 ingest 同主題的多個來源,**我想要**系統在實體被建成第二頁(不同命名)時抓得到並協助我合併,**這樣**知識圖譜不會碎裂成「同一個東西散在兩頁、各被連一半」。

研究確認:這不是 obsidian 獨有缺陷——LightRAG / MS GraphRAG / HippoRAG 的 production merge 也只靠 string-match,2025 學界視為**未解開放問題**。所以目標是務實補強,不是追一個不存在的「LLM-wiki 標準」。

## Users
(Axis 2)

- 主使用者:kouko,單人 Obsidian vault(**非企業 MDM 規模**——不搬 source-ranking / unmerge UI / 欄位級 SOP 那套儀式)。
- 執行者:ingest/lint 的 LLM agent。
- 維護節奏:wiki-lint 週期健檢(weekly / 大 batch 後)——**batch 時機**,與 GraphRAG「dedup 在 index build 做、不逐筆增量」一致。

## Current State Evidence
(各 file:line;recon 自實際讀檔)

- **Forward(資料流入口 / 去重觸發點)**:`obsidian/skills/wiki-ingest/SKILL.md:165-179` — STEP 4c「Filename uniqueness check」只在 `wiki/{6folders}/<slug>.md` **完全同名**時判同主體→UPDATE;不同 slug 直接放行建新頁。
- **Reverse(SSOT 歸屬)**:page 格式 SSOT = `obsidian/skills/wiki-ingest/references/page-format.md`(skill 描述明載「owns page format spec」)。**無 distribute/sync 腳本**;wiki-lint 無 scripts/,14 項檢查全是 LLM 讀 `lint-checks.md` 照做的 prose 指令(連 L07 的 Levenshtein≤2 也是**指令非函式**)。
- **Error(現有漏洞 / 反向作用)**:`obsidian/skills/wiki-lint/references/lint-checks.md:51-54`(L06 orphan 把重複頁誤標孤兒)+ `wiki-lint/SKILL.md:75`(建議跑 cross-linker → 坐實重複);`lint-checks.md:60`(L07「2+ matches」只抓**完全同檔名碰撞**,近重複不觸發)。
- **Data(可複用結構)**:`obsidian/skills/wiki-ingest/references/page-format.md:19,37`(`aliases:` frontmatter — redirect 類比,可當 blocking 的比對欄位 + merge 後保留舊 slug 的容器);`wiki-ingest/references/delta-tracking.md`(`.manifest.json` `wiki_pages[]` + 「source 刪除→manifest 留 audit trail」的非破壞精神)。
- **Boundary(現況邊界)**:`grep -ri merge obsidian/skills` 確認**無任何 page-merge 工具 / 無 wiki-merge skill**;發現重複後現況只能純手工(搬內容→刪頁→修 wikilink,否則 L07 報 broken)。

## Decision (REVISED 2026-06-01 — 收斂 v2)
(一段:做什麼 / 不做什麼 / 為何)

**偵測雙家 + LLM 自動合併(人 gate 觸發)**,只動 obsidian。三個元件:

1. **偵測（共用一套 prose method,兩個家）** — method:對 normalized `title`+`aliases`+slug 做 string/alias **blocking** 算候選 → **LLM-as-judge** 判是否同一實體 + **自報信賴度 HIGH/MID/LOW**(非 embedding、非評分引擎——obsidian 無此 infra)。兩個觸發點:
   - **wiki-ingest STEP 4c 擴充(防新)** — 整理時的「擺放決策」:新實體 vs 既有頁的不同命名。**只在 HIGH 信賴度才提示**(沿用 STEP 4c 只在 multi/no-match 才問的克制),提示「近重複,要 `/wiki-merge` 合併嗎?」→ **人決定是否觸發**。
   - **wiki-lint L15(掃舊)** — 唯讀稽核,all-pairs 掃既有頁,severity=warning,補 ingest 碰不到的既存重複盲區。
2. **wiki-merge（新 skill,寫入)** — 人觸發後 **LLM 自動執行**(非人工搬運):LLM 再確認同一實體 → 起草整合 `## Summary`(較完整)/`## Key Facts`(聯集)→ 套用。**安全閘(讓自動可行)**:`## User Notes` 永遠聯集保留、被併頁 **archive 到 `wiki/_archive/<date>/` 不 hard-delete(可逆)**、舊 slug → canonical `aliases:`、重指 inbound wikilink + 重跑 cross-linker、**self-verify(查無事實遺失,失敗則中止/降級問人)**、idempotent、寫 `wiki/log.md`。合併**只處理觸發的這一對**(single responsibility);若有第三個重複,靠既有兩偵測家(ingest 防新 / lint 掃舊)接續——**不在單次 merge 內自我連鎖**(刪去 transitive iterate,避免從 batch-KG 系統搬來的 gold-plating)。

**分工**:人 gate「哪兩頁該合」(擋 over-merge);LLM 自動「把合併做完」(免人工勞動)。

為何這形狀:EN+JP 文獻 × GraphRAG/LightRAG 實作(LLM-native auto-merge 是它們的實際做法)× MDM 紀律三方交叉,且**全部用 obsidian 原生原語**(markdown + frontmatter + LLM 判斷 + stdlib,**zero 新依賴**,不裝 vector/graph DB)。偵測在 ingest=routing(整理本職)、在 lint=audit(健檢本職),共用 method、各自框架。實作以 SKILL.md + reference prose 為主,**無 pytest**。

## Out of Scope
- **auto-merge 無條件全自動**(ingest 偵測到就自己合)——不做;人 gate「要不要合」擋 over-merge(LLM 配對會誤合不同實體,如 John Doe/Doe Corp)。LLM 只在人觸發後自動「執行」。
- **embedding / 向量 blocking**——obsidian 無 infra + determinism 破壞;本版 string+alias blocking。embedding 列未來增強。
- **MDM 重型 survivorship**(source-ranking + 欄位 SOP + unmerge UI + survivorship-rules 大表)——單人 vault overkill;只取其紀律(可逆/log/User Notes override),壓成 SKILL.md 內 inline 不變量。
- **KG denoising / 剪枝**(arXiv 2510.14271)——超出本次。
- **dbt-wiki**——字典是 manifest 衍生封閉集,無此破口,不動。
- **L06/L07 大改**——僅在 L06 加一句「先過 L15 排除近重複再 cross-linker」交叉提示,不重構判定。

## Alternatives Considered
(Axis 4 — 已 WebSearch 查證,EN+JP)

- **純 string-match merge**(LightRAG/GraphRAG/HippoRAG 現況)— rejected:正是 obsidian 現有破口,2025 survey 列未解問題。
- **純 embedding similarity** — rejected:obsidian 無 infra + determinism 破壞。
- **MDM 全套 / 人工執行合併** — rejected:overkill + 違背「LLM 自動做」需求;只取紀律。
- **偵測只放 wiki-lint(batch only)** — rejected:漏「寫入時防新」,重複會先累積 inbound link 被坐實;改雙家。
- **採用**:string/alias blocking → LLM-judge(自報信賴度)雙家偵測 + 人 gate 觸發 + LLM 自動執行合併(可逆安全閘),obsidian 原生。

## What Becomes Obsolete
(Axis 5)
- 偵測層 STEP 4c 從「完全同名才判同主體」擴成「近似也判」,舊的「只認 exact slug」邏輯被涵蓋(非刪除,是擴充)。
- L06「orphan→cross-linker」對重複頁的反向建議,被 L15 前置「先判近重複」擋掉(不刪 L06,加交叉提示)。
- merge 後被併頁的獨立存在(降級為 `_archive/` 的可逆快照)。

## Open Questions — 已鎖定(2026-06-01)
- ✅ 偵測雙家:ingest STEP 4c(防新,HIGH 才提示)+ lint L15(掃舊)。
- ✅ 合併:獨立 `wiki-merge` skill;人 gate 觸發 + LLM 自動執行。
- ✅ archive 落點:`wiki/_archive/<date>/`(沿用 dbt-wiki 慣例)。
- ⏳ 實作時定:信賴度 HIGH/MID/LOW 的具體判準描述、normalization 規則(大小寫/連字號/尾綴 qualifier 如 `-MAB`)、LLM-judge prompt 確切欄位——皆為偵測 reference 的內容,非阻擋。
- ⚠ 跨 skill 重複:偵測 method 在 ingest reference(完整)與 lint-checks.md L15(inline,all-pairs 框架)各一份。依 repo 慣例「每 skill 自包含、不可跨 skill 讀檔」→ 接受重複,標注須同步(類 L12 inline heuristic 先例)。
