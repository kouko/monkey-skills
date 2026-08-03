# Brief — dbt-wiki NL2SQL part-2 = B (portable packager `dbt-wiki:pack-sql-skill`)

- **Date**: 2026-06-02
- **Topic**: dbt-wiki-nl2sql-packager (part-2 of the NL2SQL work; part-1 = A `to-sql`, shipped on branch `feat/dbt-wiki-nl2sql-to-sql`)
- **Stage**: brainstorming → (next) writing-plans → SDD
- **Parent brief**: `docs/code-toolkit/specs/2026-06-02-dbt-wiki-nl2sql-skill.md` (the A+B vision)
- **User goal (locked)**: final product must be **portable — usable by people who have neither dbt-wiki nor the dbt project**. A gives the in-repo runtime + early testing; **B is the portable deliverable**.

---

## Problem

（Axis 1 — JTBD）

**When** the wiki owner wants to give a non-dbt-wiki user (a business team, a different repo, someone with no dbt project) the ability to ask business questions and get correct SQL, **I want** to **compile** the distilled knowledge + the NL→SQL pipeline into a **single self-contained skill bundle** they can drop into any Agent-Skills-compatible tool (Claude Code / Cursor / Copilot / Gemini / Codex), **so I can** hand off "ask→SQL for this data domain" as a portable artifact without shipping the dbt project, the manifest, or the dbt-wiki plugin.

The job is **packaging/portability**, not a new NL→SQL algorithm — B reuses A's pipeline, frozen into a standalone bundle.

研究（本次 Axis-4, EN+JA 一致）：Agent Skills 是**開放可攜標準**（Anthropic，Cursor/Copilot/Gemini/Codex 皆採用）——SKILL.md bundle「跨產品攜帶、不綁單一 app」。且**同梱知識實質無上限**，因為脈絡是「按需 file-read」而非預載入。→ B 的產物天生就是這個格式；且**不需壓縮**（凍結整個知識庫當 reference 檔，bundle 自己用分層檢索只讀需要的頁）。

## Users

（Axis 2）

- **B 產物的使用者**：**沒有 dbt-wiki plugin、沒有 dbt 專案、可能不會寫 SQL** 的人（業務/PM/別團隊/別 repo）。他們拿到一個 skill bundle，貼進自己的 Agent-Skills 相容工具，問白話→得 SQL。
- **B 的操作者**：擁有 wiki 的工程師，跑 `pack-sql-skill` 產出 bundle、定期 rebuild 交付。
- **約束**：產物環境**沒有 live manifest、沒有 dbt-wiki**。所以 (a) 知識必須**凍結進 bundle**；(b) A 的靜態驗證在產物端退化為「sqlglot parse + 對 **bundle 內凍結 schema** 的存在性檢查」（無 live manifest 可查）；(c) 仍**永不執行 SQL / 永不連 warehouse**（繼承 dbt-wiki 硬邊界）。

## Smallest End State

（Axis 3）

**B = 一個 compiler skill `dbt-wiki:pack-sql-skill`**（暫名），讀 `.dbt-wiki/` + A 的 skill 檔，輸出一個**自包含 Agent Skill bundle**到使用者指定路徑。**v1 = full-freeze（不壓縮）**：

Bundle 內容（一個扁平 skill 資料夾）：
1. `SKILL.md` — 由 A 的 `to-sql/SKILL.md` 改寫：相同 pipeline，但 (a) 從 bundle 內凍結知識讀取（非 `.dbt-wiki/`），(b) 驗證對凍結 schema（非 live manifest），(c) 不做 drift check（快照，無 live manifest 可比）。
2. `knowledge/` — 凍結的知識層（entities/metrics/concepts + 欄位卡 + relationships）+ 必要的 evidence schema（欄位名/型別），從 `.dbt-wiki/` 拷入。
3. `assets/validate_sql.py` — A 的 validator，改成對「凍結 schema JSON」而非 manifest.json 做存在性檢查（沿用同函式，換 schema 來源）。
4. `references/` — A 的 retrieval.md + prompt-assembly.md，改寫掉「live `.dbt-wiki/` / manifest / drift」的引用。
5. bundle frontmatter / manifest 註記：來源 `manifest_sha` + build 日期 + 「snapshot；rebuild 以更新」+ 來源 dbt-wiki 版本。

**B 是 compiler，不是 fork**：B 讀「當前的 A + 當前的知識庫」每次重新產出 → A 演化時 re-run B 即可，無手抄漂移。

**驗收**：給定一個合成的最小 `.dbt-wiki/` fixture（幾頁 entity/metric + 一個欄位卡），`pack-sql-skill` 產出一個 bundle 資料夾；該 bundle 在**移除 dbt-wiki plugin + dbt 專案**的環境下，對 bundle 內凍結 schema 能產出 sqlglot-parse 通過、且欄位存在於凍結 schema 的 SQL。

## Current State Evidence

（擴充既有 + 依賴 A，必填）

- **Forward（A 的 runtime，B 要凍結的對象）**：A `to-sql/SKILL.md` pipeline = 前置/drift → 檢索 `.dbt-wiki/` → 組 prompt → 生 SQL → 對 manifest 靜態驗證 → 輸出（`dbt-wiki/skills/to-sql/SKILL.md`，本 session 剛 ship 在 `feat/dbt-wiki-nl2sql-to-sql`）。B 凍結這條 pipeline，抽掉 live 依賴。
- **Reverse（SSOT / 資料流向）**：dbt-wiki **無 distribute.py**。`.dbt-wiki/` 由 init 產生。A 的檔（`skills/to-sql/{SKILL.md,references/*,assets/validate_sql.py}`）是 B 的輸入之一。B 是**第一個產出「可分發成品」的 skill**——輸出落使用者指定路徑（治理：產物若含真實 schema → 落使用者私有處，不進 public plugin repo）。
- **Error / 一致性**：A 的 validator `check_refs_against_manifest(refs, manifest_path, catalog_path=None)`（`dbt-wiki/skills/to-sql/assets/validate_sql.py`）吃 manifest.json。B 端無 manifest → 需一個 `check_refs_against_frozen_schema(refs, schema_path)` 變體（或把 manifest 載入抽象成「schema source」），對凍結的 schema JSON 查存在性。`extract_refs` 不變（純 sqlglot）。
- **Data 來源**：B 凍結 = `.dbt-wiki/` 的 entities/metrics（含 `## Materialized Columns`）/concepts/relationships + evidence 的 `columns[]`（名/型別）。凍結 schema = 從 evidence models 萃取的 {model→columns} 子集（validator 用）。
- **Boundary（硬護欄）**：產物**永不執行 SQL / 永不連 warehouse**（繼承）；驗證靜態。真實 schema/SQL 產物落使用者私有 repo，**不進 public plugin repo**（Block 8 治理；B 的 fixture/測試一律合成）。

**Evidence paths appendix**：
- `dbt-wiki/skills/to-sql/SKILL.md` + `references/{retrieval,prompt-assembly}.md` + `assets/validate_sql.py`（A — B 凍結的對象，branch `feat/dbt-wiki-nl2sql-to-sql`）
- `dbt-wiki/skills/init/assets/SCHEMA.md`（知識頁 + evidence 欄位結構 = 要凍結的形狀）
- `dbt-wiki/skills/query/SKILL.md`（分層檢索 — bundle 內保留同機制）

## Decision

**做**：B = compiler skill `dbt-wiki:pack-sql-skill`，讀 `.dbt-wiki/` + A 的檔 → 產出自包含 Agent Skill bundle（凍結知識庫為 reference 檔 + A 的 pipeline 去 live 依賴 + validator 改吃凍結 schema + 快照註記）。**v1 full-freeze，不壓縮**（研究證實 bundle 知識按需 file-read、實質無上限；分層檢索保留 → 不需壓縮，YAGNI）。B 是 compiler 非 fork（每次讀當前 A 重產，免手抄漂移）。

**不做（v1）**：
- **壓縮 / 子集挑選**（YAGNI — bundle 無上限；分層檢索已解決載入成本；除非實測 bundle 大到不實用才做）。
- **execution 驗證 / 連 warehouse**（繼承硬邊界）。
- **bundle 內重建 drift check**（產物無 live manifest 可比；改為「快照 + rebuild 以更新」註記）。
- **多 wiki 合併 / 跨專案 bundle**（單一 `.dbt-wiki/` → 單一 bundle）。

**為何 compiler 非 fork**：避免 B 的產物與 A 的邏輯漂移（A 改了 → re-run B）。B 機械化重產，是 build step 不是複製。

**為何現在可做（A-dogfood 依賴已解除）**：先前 part-1 brief 的 OQ2 擔心「凍結全部 vs 壓縮子集」需 A 實測指導——研究證實 v1 用 full-freeze，該問題消失；B 可用合成 fixture 測試，不硬性 gate 在 A 的真實-專案 dogfood。

## Out of Scope

- 壓縮 / 涵蓋率優化（延後，實測驅動）。
- gold examples（A 的 few-shot slot；獨立增量；B 若 A 有 examples 就一併凍結，但不在 B 範圍生成）。
- execution 驗證、warehouse 連線。
- 多專案 / 多 wiki 合併 bundle。
- 真實 schema 產物進 public repo（治理硬護欄；B 測試用合成 fixture）。

## Alternatives Considered

（Axis 4 — research-grounded）

1. **Agent Skills bundle（SKILL.md + reference 檔，full-freeze）** — [Anthropic Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)、[Claude Skills docs](https://code.claude.com/docs/en/skills)、JA [Karpathy LLM Knowledge Base パターン](https://dev.classmethod.jp/articles/karpathy-llm-knowledge-base/)
   - Pros：開放可攜標準（跨 Claude/Cursor/Copilot/Gemini/Codex）；同梱知識按需 file-read、實質無上限；保留分層檢索；就是 dbt-wiki 自己的格式（一致）。
   - Cons：快照會 stale（需 rebuild）；產物較大（但無功能上限）。
   - **採用**（v1）。
2. **壓縮成單一 prompt-context 檔（embed 精選 schema）** — 傳統 text-to-SQL 做法。
   - Pros：產物小。
   - Cons：丟失分層檢索；要挑「凍結什麼」（正是需 A dogfood 的難題）；研究說無上限故無必要。
   - 否決（v1）；若實測 bundle 過大再考慮。
3. **standalone CLI（`pipx install`）** — part-1 brief 曾提的 architecture C。
   - Pros：完全獨立可執行。
   - Cons：違背「可攜 skill」目標（要裝 Python pkg，非貼進 AI 工具）；重。
   - 否決。

**My take**：full-freeze Agent Skills bundle（選項 1）。Why：直接命中「可攜、給沒有 dbt-wiki 的人」目標，且是知識按需讀取的開放標準；不壓縮符合最小終態。Conditional reversal：若真實 wiki 大到 bundle 不實用（實測），再加壓縮（選項 2 的子集挑選）。

## What Becomes Obsolete

（Axis 5）

- 純新增 skill。無既有碼過時。
- 一旦 B 可用：「把 wiki 內容人工整理成給別人的 SQL 指南」的手動流程過時。
- A 與 B 共用 pipeline 邏輯——B 是 compiler 讀 A，故 A 不被 B 取代、也不複製（避免雙份漂移）。**需在 README/router 標明 A（in-repo runtime）vs B（產出可攜 bundle）的分工。**

## Open Questions

- **OQ1（sequencing — checkpoint 待你定）**：A 已 push 但**未 merge、未在真實專案 dogfood**。B 用合成 fixture 可現在做；但 A 若經真實 dogfood 後改了 pipeline，B 的「去 live 依賴」改寫可能要跟改（B-as-compiler 讓知識凍結部分自動跟上，但 pipeline 改寫部分需手動跟）。要 **現在就做 B**，還是 **先把 A merge + 真實 dogfood 一輪再做 B**？（見下方 checkpoint）
- **OQ2（命名）**：`pack-sql-skill` / `export-sql-skill` / `build-nl2sql-skill`。writing-plans 前定。
- **OQ3（validator 重用形狀）**：把 A 的 manifest 載入抽象成「schema source」介面（manifest source vs frozen-schema source），讓 A 與 bundle 共用一個 validator？還是 bundle 帶一個獨立的 frozen-schema validator？影響 A 是否要回頭小改。writing-plans 時定。
