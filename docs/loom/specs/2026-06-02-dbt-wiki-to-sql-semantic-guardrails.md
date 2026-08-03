# Brief — dbt-wiki to-sql：語意護欄（semantic correctness guardrails）

- **Date**: 2026-06-02
- **Topic**: dbt-wiki-to-sql-semantic-guardrails
- **Stage**: brief (discovery done empirically via 5 dogfood rounds) → writing-plans → SDD
- **Branch**: `feat/dbt-wiki-nl2sql-to-sql`（接續 A 的 dogfood 強化；distill 變更先前已在此 branch 有 f0a7d861 date-caveat 前例）
- **Discovery 來源**：真實客戶 dogfood（見 [[project_dbt_wiki_nl2sql]] / memory `feedback_static_validation_necessary_not_sufficient_nl2sql`）

---

## Problem

（Axis 1 — JTBD，經驗性發現）

dogfood 證實：to-sql 的靜態驗證（sqlglot parse + manifest 存在性）只攔得到語法錯 + 幻覺 ref；**真正危險的是「合法 SQL 但算錯數字」**，靜態驗證結構上抓不到、非-SQL 使用者也看不出來。實測 5 個 valid-SQL-wrong-answer class：聚合形式（AOV 3x）、fan-out join-grain（84x）、時間語意（MAX(date)→2051，已修）、value-grounding（台灣≠TW → 0 列）、source-ambiguity（同詞兩源差 4%）。

**When** 使用者問一個商業問題、to-sql 生成語法合法的 SQL，**I want** 那段 SQL 的**語意**也對（正確的聚合形式 / join grain / 值對映 / 來源），**so I can** 信任答案而不需自己會寫 SQL 驗算。

## Users

（Axis 2）

- to-sql 的使用者（有 wiki 的 repo 內）；以及未來 B packager 的外部使用者（**沒有 warehouse 可驗算** → 語意錯 = 直接拿到錯答案，無從察覺）。這正是 B 必須等語意護欄到位的原因。

## Smallest End State

（Axis 3 — 兩層：prompt 護欄〔便宜、即時防〕+ distill 知識捕捉〔治本〕）

**A. prompt-assembly.md 加 4 條護欄**（與既有 §4 時間 / §4d NULL 同形狀，APPEND/子節、不 renumber）：
1. **聚合語意**：ratio/average 預設 **aggregate-level（`SUM(num)/SUM(denom)`）**，非 `AVG(row-ratio)`；若 metric 頁 `## Calculation` 已定義則用之；聲明所用形式。
2. **fan-out / grain**：join 必須用 relationship `note` 記的**完整 grain key（複合）**；偵測到兩表 grain 不同（如 customer vs customer×month）時警告 + 不可對 fan-out 後的列直接 SUM。
3. **value-grounding**：分類值等值過濾，優先用知識層記錄的 value-domain/enum；無則聲明「stored-format 假設」或用 ILIKE；**絕不假設使用者詞 = DB 存值**（台灣≠TW、台北≠台北市）。
4. **source-disambiguation**：同一業務詞有 ≥2 候選來源（如 operational SRR vs financial-close report）時，**surface 兩者 + 各自 basis** 讓使用者選，不靜默挑一個。

**B. distill 知識層捕捉 3 項**（治本——讓護欄有資料可用）：
5. **relationship edge `note` 記複合 join key**：所有 key 欄（如 `customer_no + rr_month`），非單一欄。（SCHEMA Relationships spec + distill-entities/metrics 產出。）
6. **metric 頁 `## Calculation` 定義 derived-ratio 聚合形式**：如 AOV = `SUM(sales)/SUM(invoices)`（aggregate-level）。（distill-metrics §5。）
7. **分類欄記 value-domain/enum + stored format**：小基數分類欄（如 region ∈ {TW,HK,SG}）記進 entity `## Fields` 或 caveat。（distill-entities + SCHEMA。）
   （第 8 項 date forward-dating caveat 已於 round 2 完成 = `f0a7d861` distill-metrics §6，本 brief 不重做。）

**驗收**：給定合成 fixture + 上述每個 trap 形狀，prompt-assembly 規則明確指示正確處理；distill 規格明確要求捕捉複合 key / ratio 定義 / value-domain。（純 spec/markdown，無 runtime 執行；驗證 = grep + reviewer + 對照 dogfood 案例。）

## Current State Evidence

（強，經驗性 + 檔案 refs）

- **Forward**：`to-sql/references/prompt-assembly.md` 現有 §1 schema-link / §2 column-card / §3 join-path / §4 temporal / §4d NULL / §5-8。**缺**：聚合形式、grain/fan-out、value-grounding、source 多選 的規則。
- **Reverse（SSOT）**：dbt-wiki 無 distribute.py。prompt-assembly.md 是 to-sql 自有；distill specs（`init/references/distill-{metrics,entities,concepts}.md` + `init/assets/SCHEMA.md` Relationships/頁型）是 init 的知識層 SSOT。to-sql 消費 distill 產出的知識頁。本 branch 已有 distill 變更前例（f0a7d861）。
- **Error/一致性**：護欄是 prompt 指示（LLM 行為），非確定性碼 → 無單元測試；靠 grep + reviewer + dogfood 案例對照。distill 變更須跨 init/query 泛型相容（query 泛型載入，已驗無 allowlist）。
- **Data**：fan-out 的真實證據 = monthly 表複合鍵 (customer_no, rr_month)；value-domain = cd__region ∈ {TW,HK,SG,null}、cd__city 帶「市」；ratio 分歧 = AOV 582 vs 1656；source 分歧 = SRR 22.53M vs 財報 21.63M。（真實數字僅 dogfood 佐證，**不入 repo**。）
- **Boundary（硬護欄）**：純 spec；零 warehouse/執行；真實 SQL/客戶名/數字**絕不進 public repo**，worked example 一律合成；§-renumber 禁止（用子節，避免再炸跨檔 ref，見 [[feedback_cross_file_section_refs_shotgun_surgery]]）。

**Evidence paths**：`dbt-wiki/skills/to-sql/references/prompt-assembly.md`(§1-8) · `dbt-wiki/skills/init/references/distill-metrics.md`(§5 Calculation, §6 Caveats) · `dbt-wiki/skills/init/references/distill-entities.md`(Fields) · `dbt-wiki/skills/init/assets/SCHEMA.md`(Relationships spec, knowledge-entity/metric 頁型)

## Decision

**做**：A. prompt-assembly 加 4 條語意護欄（aggregate-semantics / fan-out-grain / value-grounding / source-disambiguation），APPEND 或子節、不 renumber。B. distill 規格加 3 項知識捕捉（複合 join key / derived-ratio 聚合定義 / 分類 value-domain）。全為 spec 精修、零執行、合成範例。

**不做（本次）**：gold examples 生成（獨立增量，這次 dogfood 證實其必要性但仍是大工程）；execution 驗證；B packager（必須等語意護欄到位後）；retrieval 演算法重構（source-disambiguation 用「surface 多源」處理，不重建檢索）。

**為何 prompt + distill 雙層**：prompt 護欄是即時防護（即使知識層沒記，也有保守預設 + 聲明假設）；distill 捕捉是治本（讓護欄有權威資料）。兩者互補，研究的「知識結構是主槓桿」對應 distill 層。

## Out of Scope

- gold examples（獨立 brief，已存在 `2026-06-02-dbt-wiki-gold-example-bank.md`）。
- B packager（part-2，等語意護欄）。
- execution-based 驗證 / warehouse 連線。
- 真實資料進 repo。

## Alternatives Considered

（Axis 4 — 經驗性）

1. **加更多靜態驗證** — 直覺反應。否決：dogfood 證實這些 class 結構上靜態抓不到（合法 SQL）。
2. **只加 prompt 護欄、不改 distill** — 較小。部分可行（即時防護），但治標：value-domain/複合-key/ratio-定義 沒記進知識層，護欄只能用保守預設 + 猜，命中率受限。故 prompt + distill 並進。
3. **直接上 gold examples（最大槓桿）** — 研究 +44.9pp。延後：gold-example 生成是獨立大工程（已有 brief）；護欄是更便宜的即時防護，且 examples 也需正確的知識層基礎。先護欄 + distill，examples 隨後。

**My take**：prompt 護欄 + distill 捕捉雙層（選項 2 的完整版）。Why：即時防護 + 治本，便宜、不需 examples 工程。Conditional reversal：若護欄+distill 後 dogfood 顯示準確度仍不足 → 提前做 gold examples。

## What Becomes Obsolete

（Axis 5）

- 純新增規則 + 規格強化，無碼過時。
- 概念上：到位後，「靜態驗證 PASS 就當 SQL 對」的隱含假設過時——輸出契約應明確區分「語法/schema 已驗」vs「語意假設（已聲明）」。§8 輸出契約已有 validation + temporal/NULL 假設區，本次擴充涵蓋 aggregation/grain/value/source 假設。

## Open Questions

- **OQ1**：distill 變更（複合 key / value-domain / ratio 定義）放本 branch（dogfood 驅動、已有前例 f0a7d861）還是獨立 init PR？傾向本 branch（coherent dogfood 故事），writing-plans 時確認。
- **OQ2**：value-domain 捕捉的基數上限（小 enum 記、大基數不記，避免 SCHEMA 膨脹）——writing-plans 定一個門檻（如 ≤ N distinct）。
- **OQ3**：source-disambiguation 規則要不要也需 distill 記「canonical source per intent」，或 prompt「surface 兩源」就夠？v1 傾向後者（prompt surface），distill 記 canonical 為後續。
