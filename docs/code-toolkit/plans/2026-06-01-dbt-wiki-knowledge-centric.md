# Plan: dbt-wiki 知識主體化 v2.0（MVP）

**Source brief**: docs/code-toolkit/specs/2026-06-01-dbt-wiki-knowledge-centric.md
**Total tasks**: 12（width 不設限；depth 才是天花板）
**Critical-path depth**: 4（≤5 ✓） — 最長鏈 T1 → T2 → T3/T4/T5 → T8a–e（文件層全在 L4 平行）
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-06-01, R2 14/14；R1 NEEDS_REVISION → T8 拆 8a–e 後通過)

> MVP 性質：本計畫幾乎全為 markdown 編排（SCHEMA.md spec + 3 SKILL.md 程序 prose）+ 版本檔，**無新增 deterministic Python**（現有 sqlglot 萃取器不動，僅輸出路徑改 `_evidence/`，屬 prose 層）。多數任務 RED 為 grep/結構診斷而非 pytest——skill-prose 重設計的固有形態，plan-format 明文允許 "RED: failing test OR diagnostic"。知識蒸餾本體在 runtime 由 LLM 依程序執行；任務交付物是「程序 prose」，邊界明確。

---

## Task 1 — SCHEMA.md 升 v2.0：知識頁型 + 證據層 + 定位重寫

- **Description**: 在 `skills/init/assets/SCHEMA.md` 定義 v2.0：① 三個知識頁型 `knowledge-entity` / `knowledge-metric` / `knowledge-concept` 的 frontmatter（含 `derived_from: [evidence uids]`、`relationships:`、`last_changed_by:`、`status` 生命週期、`summary`）＋知識頁 body 結構（含 `## Relationships` typed-edges 段、entity 頁的欄位字典段、caveats 段）；② 證據層目錄佈局 `_evidence/{models,sources,macros,seeds,snapshots,tests,exposures}/` + `lineage.md` + `syntheses/`；③ 定位語句改寫（`= STRUCTURE + COLUMN LINEAGE` → `= 資料的語意知識，由結構證據支撐`）+ repo-wiki coexistence 段更新（WHY vs WHAT-the-data-means）+ v2.0 freeze 標記。
- **Module**: `skills/init/assets/SCHEMA.md`
- **Files touched**: `dbt-wiki/skills/init/assets/SCHEMA.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/assets/SCHEMA.md
  - /Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-06-01-dbt-wiki-knowledge-centric.md
- **Acceptance**:
  - **RED**: `grep -E 'knowledge-entity|knowledge-metric|knowledge-concept|_evidence/|derived_from' SCHEMA.md` 全部 0 命中（v1.x 現況）
  - **GREEN**: 三個知識頁型 frontmatter + `_evidence/` 佈局 + `derived_from`/`relationships`/`last_changed_by` 欄位 + 改寫後的定位語句皆在檔內；舊「= STRUCTURE + COLUMN LINEAGE」定位語句已移除/改寫
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: 「SCHEMA v2.0 — 定義知識層頁型 + 證據層 + migration note」（Smallest End State 1）

## Task 2 — init SKILL.md：證據層搬遷 + Phase B 蒸餾骨架 + v1.x 護欄

- **Description**: 改 `skills/init/SKILL.md`：① Phase A 把 model/source/macro 等頁的生成輸出路徑全部改到 `_evidence/<type>/`（Step 5）；② index.md 改成知識優先（by entity/metric/domain），結構分組降級進證據層索引（Step 6）；③ 新增 Phase B 蒸餾骨架：一段程序 prose，說明蒸餾在證據層建好後執行，並 **指向** `references/distill-entities.md` / `distill-metrics.md` / `distill-concepts.md` 三個規格檔；④ 加 v1.x 護欄：偵測到既有 `.dbt-wiki/`（有 `models/` 無 `_evidence/`）且含 `## User Notes` 時印一次警告（不保留、建議先備份），非遷移邏輯。
- **Module**: `skills/init/SKILL.md`
- **Files touched**: `dbt-wiki/skills/init/SKILL.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/SKILL.md
  - /Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/assets/SCHEMA.md
- **Acceptance**:
  - **RED**: `grep -E '_evidence/|Phase B|distill-entities' SKILL.md` 0 命中；且 Step 5 仍寫 `.dbt-wiki/models/`
  - **GREEN**: Step 5 輸出路徑為 `_evidence/<type>/`；Phase B 骨架段存在且引用三個 distill 規格檔；index 改知識優先；v1.x User-Notes 警告分支存在
- **Dependencies**: Task 1 completes first
- **Independent**: true  # L2 波：與 T6(query)/T7(refresh) 檔案不相交可平行；被 L3 依賴以 Dependencies 表達，不影響平行性
- **Brief item covered**: 「init 兩階段：Phase A 機械建證據層（搬到 `_evidence/`）→ Phase B 新增 LLM 蒸餾知識層」（Smallest End State 2）

## Task 3 — distill-entities.md：實體維度蒸餾規格

- **Description**: 新建 `skills/init/references/distill-entities.md`：規範 LLM 如何從證據層（`_evidence/` model 頁 + manifest 命名族 + 血緣 + schema.yml description）蒸餾出 `entities/` 頁——識別業務物件（跨 stg→int→mart 聚類）、grain、欄位字典段（白話欄位意義，glossary 併此）、`## Relationships` 的 entity↔entity（join key / depends_on）與 →`_evidence/` 引用、`derived_from` frontmatter。含 1 個 worked example（Customer/Order）。
- **Module**: `skills/init/references/distill-entities.md`（new）
- **Files touched**: `dbt-wiki/skills/init/references/distill-entities.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/assets/SCHEMA.md
  - /Users/kouko/GitHub/monkey-skills/obsidian/skills/wiki-ingest/references/category-routing.md
- **Acceptance**:
  - **RED**: `test -f references/distill-entities.md` 失敗（檔不存在）
  - **GREEN**: 檔存在，含實體識別程序 + 欄位字典段規範 + `## Relationships` typed-edge 規範 + `derived_from` + 1 worked example；產出頁型對齊 SCHEMA `knowledge-entity`
- **Dependencies**: Tasks 1, 2 complete first
- **Independent**: true
- **Brief item covered**: 「`entities/` 業務物件；欄位段含白話欄位字典；typed-link Relationships」（Decision 知識維度表）

## Task 4 — distill-metrics.md：指標維度蒸餾規格

- **Description**: 新建 `skills/init/references/distill-metrics.md`：規範如何蒸餾 `metrics/` 頁——從聚合 SQL（GROUP BY grain）、mart 欄位、**若專案有 MetricFlow `semantic_models`/`metrics`（manifest）則 ingest 當權威輸入、不重推**，產出：定義、算法白話、caveats、來源 model、`## Relationships` 的 metric→entity（衡量對象/grain）與 metric→concept（算法依賴）、`derived_from`。含 1 worked example（churn/MRR）。
- **Module**: `skills/init/references/distill-metrics.md`（new）
- **Files touched**: `dbt-wiki/skills/init/references/distill-metrics.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/assets/SCHEMA.md
  - /Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/SKILL.md
- **Acceptance**:
  - **RED**: `test -f references/distill-metrics.md` 失敗
  - **GREEN**: 檔存在，含指標蒸餾程序 + MetricFlow-ingest-if-present 分支 + metric→entity/concept typed-edge 規範 + `derived_from` + 1 worked example；對齊 SCHEMA `knowledge-metric`
- **Dependencies**: Tasks 1, 2 complete first
- **Independent**: true
- **Brief item covered**: 「`metrics/` 業務指標：定義＋算法白話＋caveats＋來源；MetricFlow 若有則 ingest」（Decision + Out of Scope）

## Task 5 — distill-concepts.md：概念維度蒸餾規格

- **Description**: 新建 `skills/init/references/distill-concepts.md`：規範如何蒸餾 `concepts/` 頁——從 SQL 的 CASE/WHERE 語意 + schema.yml description，抽出**不屬單一實體的橫切業務規則**（「活躍客戶＝近90天有單」、財年、狀態列舉），產出：規則白話定義、適用範圍、`## Relationships` 的 concept→entity/metric（規則套用對象）、`derived_from`。含 1 worked example（活躍客戶定義）。附「concept vs entity 邊界判準」小節（沿用 Obsidian category-routing 的 80% 規則精神）。
- **Module**: `skills/init/references/distill-concepts.md`（new）
- **Files touched**: `dbt-wiki/skills/init/references/distill-concepts.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/assets/SCHEMA.md
  - /Users/kouko/GitHub/monkey-skills/obsidian/skills/wiki-ingest/references/category-routing.md
- **Acceptance**:
  - **RED**: `test -f references/distill-concepts.md` 失敗
  - **GREEN**: 檔存在，含概念蒸餾程序 + concept↔entity/metric typed-edge 規範 + 邊界判準小節 + `derived_from` + 1 worked example；對齊 SCHEMA `knowledge-concept`
- **Dependencies**: Tasks 1, 2 complete first
- **Independent**: true
- **Brief item covered**: 「`concepts/` SQL 裡編碼、不屬單一實體的橫切業務規則」（Decision 知識維度表）

## Task 6 — query SKILL.md：語意問句類別

- **Description**: 改 `skills/query/SKILL.md`：在現有結構類 C1–C11 之上，新增**語意問句類別**（如 K1「X 是什麼意思 / 解釋這個指標」、K2「哪些實體/指標跟 Y 有關」→ 走 `## Relationships`、K3「這份資料的領域全貌」），優先讀知識層、引用證據層佐證；結構類 C1–C11 改讀 `_evidence/`。更新 Step 1 讀知識優先 index、Step 2 分類表、citation 路徑。
- **Module**: `skills/query/SKILL.md`
- **Files touched**: `dbt-wiki/skills/query/SKILL.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/query/SKILL.md
  - /Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/assets/SCHEMA.md
- **Acceptance**:
  - **RED**: `grep -E 'K1|K2|語意|knowledge|_evidence/' query/SKILL.md` 0 命中語意類別
  - **GREEN**: 新增 ≥3 語意問句類別、優先讀知識層、結構類 citation 改 `_evidence/`；現有 C1–C11 仍在（不刪結構能力）
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: 「query 加語意問句（『churn 是什麼意思』『哪些實體跟營收有關』），結構類改讀證據層」（Smallest End State 3）

## Task 7 — refresh SKILL.md：thin（證據刷新 + 標 stale）

- **Description**: 改 `skills/refresh/SKILL.md`（**thin，不做自動重蒸——auto-redistill 是 fast-follow**）：① 證據刷新輸出路徑改 `_evidence/`（Step 3/4/6）；② 擴充 Step 6.5：除既有 syntheses，**亦對知識頁做 stale 偵測**——用既有 manifest-diff 算出的 modified model uids，與知識頁 frontmatter `derived_from` 取交集，重疊則貼 stale banner + `stale: true`（複用同一 mark_stale 機制）。明確標註：MVP 只標 stale 不自動重蒸，re-distill 由使用者觸發 / fast-follow。
- **Module**: `skills/refresh/SKILL.md`
- **Files touched**: `dbt-wiki/skills/refresh/SKILL.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/refresh/SKILL.md
  - /Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/assets/SCHEMA.md
- **Acceptance**:
  - **RED**: `grep -E '_evidence/|derived_from' refresh/SKILL.md` 0 命中；Step 6.5 僅處理 syntheses
  - **GREEN**: 證據刷新路徑為 `_evidence/`；Step 6.5 含知識頁 `derived_from`∩modified-uids 的 stale 標記；明文「不自動重蒸（fast-follow）」
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: 「thin refresh（證據刷新 + 標 stale，先不自動重蒸）」（Smallest End State / OQ4 LOCKED）

## Task 8a — 版本機械收尾：plugin.json 2.0.0 + CHANGELOG

- **Description**: `dbt-wiki/.claude-plugin/plugin.json` version `1.3.0` → `2.0.0`；`dbt-wiki/CHANGELOG.md` 新增 2.0.0 breaking 條目（知識主體化雙層架構 + clean-break 無 migration + 證據層搬 `_evidence/` + 三知識維度 entities/metrics/concepts + thin refresh）。純機械 release metadata，不碰敘事散文。
- **Module**: `dbt-wiki release metadata`（plugin.json + CHANGELOG.md）
- **Files touched**: `dbt-wiki/.claude-plugin/plugin.json`, `dbt-wiki/CHANGELOG.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/dbt-wiki/.claude-plugin/plugin.json
  - /Users/kouko/GitHub/monkey-skills/dbt-wiki/CHANGELOG.md
- **Acceptance**:
  - **RED**: `grep '"version": "2.0.0"' plugin.json` 失敗（現為 1.3.0）；CHANGELOG 無 2.0.0 條目
  - **GREEN**: version 為 2.0.0；CHANGELOG 有 2.0.0 breaking 條目列出上述變更
- **Dependencies**: Tasks 2, 3, 4, 5, 6, 7 complete first
- **Independent**: true  # 與 T8b–e 敘事檔不相交；doc-mirrors-code 但屬機械版本，依賴用 Dependencies 表達
- **Brief item covered**: 「v2.0 breaking + migration（本次為 v2.0）」（Brief 標頭 + What Becomes Obsolete）

## Task 8b — README.md（en）雙層敘事改寫

- **Description**: 改 `dbt-wiki/README.md` 定位敘事：從「純機械結構快照 / = STRUCTURE + COLUMN LINEAGE」改為「證據層機械萃取 + 知識層 AI 蒸餾」雙層；補三知識維度與語意 query 一句話定位。依 brief「What Becomes Obsolete」指引，單檔聚焦改寫。
- **Module**: `dbt-wiki/README.md`
- **Files touched**: `dbt-wiki/README.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/dbt-wiki/README.md
  - /Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-06-01-dbt-wiki-knowledge-centric.md
- **Acceptance**:
  - **RED**: `grep -iE 'STRUCTURE \+ COLUMN LINEAGE|純機械' README.md` 仍命中舊純機械定位
  - **GREEN**: 定位段為雙層敘事；含 entities/metrics/concepts 與語意 query 提及；舊純機械定位語句已移除/改寫
- **Dependencies**: Tasks 2, 3, 4, 5, 6, 7 complete first
- **Independent**: true
- **Brief item covered**: 「定位語句 / README → 證據層機械、知識層 AI 蒸餾雙重敘事」（What Becomes Obsolete）

## Task 8c — README.ja.md 雙層敘事鏡像

- **Description**: 將 `dbt-wiki/README.ja.md` 的定位敘事同步改為雙層（証拠層＝機械、知識層＝AI 蒸留），與 README.md 同義；依 brief 直接改，不需先等 en 版。
- **Module**: `dbt-wiki/README.ja.md`
- **Files touched**: `dbt-wiki/README.ja.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/dbt-wiki/README.ja.md
  - /Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-06-01-dbt-wiki-knowledge-centric.md
- **Acceptance**:
  - **RED**: `grep -iE 'STRUCTURE \+ COLUMN LINEAGE|純機械|構造スナップショット' README.ja.md` 仍命中舊定位
  - **GREEN**: 定位段為雙層敘事（日文）；舊純機械定位已改寫
- **Dependencies**: Tasks 2, 3, 4, 5, 6, 7 complete first
- **Independent**: true
- **Brief item covered**: 「定位語句 / README（多語）→ 雙層敘事」（What Becomes Obsolete）

## Task 8d — README.zh-TW.md 雙層敘事鏡像

- **Description**: 將 `dbt-wiki/README.zh-TW.md` 的定位敘事同步改為雙層（證據層＝機械、知識層＝AI 蒸餾），與 README.md 同義；依 brief 直接改。
- **Module**: `dbt-wiki/README.zh-TW.md`
- **Files touched**: `dbt-wiki/README.zh-TW.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/dbt-wiki/README.zh-TW.md
  - /Users/kouko/GitHub/monkey-skills/docs/code-toolkit/specs/2026-06-01-dbt-wiki-knowledge-centric.md
- **Acceptance**:
  - **RED**: `grep -iE 'STRUCTURE \+ COLUMN LINEAGE|純機械|結構快照' README.zh-TW.md` 仍命中舊定位
  - **GREEN**: 定位段為雙層敘事（繁中）；舊純機械定位已改寫
- **Dependencies**: Tasks 2, 3, 4, 5, 6, 7 complete first
- **Independent**: true
- **Brief item covered**: 「定位語句 / README（多語）→ 雙層敘事」（What Becomes Obsolete）

## Task 8e — claude-md-snippet.md 雙層敘事改寫

- **Description**: 改 `dbt-wiki/skills/init/assets/claude-md-snippet.md`（init 寫進使用者 repo 的 CLAUDE.md drop-in）：把 `.dbt-wiki/` 定位描述從純機械結構快照改為雙層（證據層機械 + 知識層蒸餾），並反映 `_evidence/` 佈局與知識頁存在。
- **Module**: `dbt-wiki/skills/init/assets/claude-md-snippet.md`
- **Files touched**: `dbt-wiki/skills/init/assets/claude-md-snippet.md`
- **Context paths**:
  - /Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/assets/claude-md-snippet.md
  - /Users/kouko/GitHub/monkey-skills/dbt-wiki/skills/init/assets/SCHEMA.md
- **Acceptance**:
  - **RED**: `grep -iE '_evidence/|知識層|knowledge' claude-md-snippet.md` 0 命中（仍純結構描述）
  - **GREEN**: snippet 描述雙層 + `_evidence/` 佈局 + 知識頁存在
- **Dependencies**: Tasks 2, 3, 4, 5, 6, 7 complete first
- **Independent**: true
- **Brief item covered**: 「SKILL 描述 → 證據層機械、知識層 AI 蒸餾雙重敘事」（What Becomes Obsolete）

## Notes

- **依賴層級**：L1=T1（SCHEMA SSOT）→ L2={T2(init), T6(query), T7(refresh)} 三檔不相交可平行 → L3={T3,T4,T5} 三個新 distill 規格檔不相交可平行 → L4={T8a,T8b,T8c,T8d,T8e} 文件層五任務（各單檔、不相交）平行鏡像最終態。
- **平行波**：三波——L2={T2,T6,T7}（3-wide）、L3={T3,T4,T5}（3-wide）、L4={T8a–e}（5-wide），各波內皆 `Independent: true` 且 `Files touched` 不相交 → 適用 `dispatching-parallel-agents`。L4 諸任務雖 doc-mirrors-code，但依賴以 `Dependencies: Tasks 2–7` 表達、彼此單檔不相交，故波內可平行；跨任務敘事一致性由 whole-branch code-reviewer 的 cross-task-coherence 把關。
- **R1→R2 修正**：原 T8（6 檔/多語改寫）違反 Check 4（多模組）+ Check 5（>5min），依 reviewer 建議拆成 T8a（版本機械）+ T8b/c/d（3 語 README 各單檔）+ T8e（snippet）。depth 不變（皆 L4）。
- **depth=4**，遠低於 5，留有 BLOCKED Child-Test 再拆的餘裕。T1（SCHEMA v2.0）為最大單頁 spec，若 implementer 回 BLOCKED 則依 Child-Test 拆 frontmatter / 佈局 / 定位三子任務（同檔順序）。
- **無 External surfaces**：全為內部 skill prose + 版本檔；現有 sqlglot 不新增、不變更介面。
- **TDD 形態**：T3/T4/T5 的 RED 為 `test -f`（檔案存在）、其餘為 grep 結構診斷——prose/spec 任務的合法 acceptance（plan-format 明文允許 diagnostic）。
