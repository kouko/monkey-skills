# Brief — dbt-wiki：把蒸餾知識封裝成「可攜知識 skill」，搭配連倉工具供 agent 分析（架構修正）

- **Date**: 2026-06-03
- **Topic**: dbt-wiki-knowledge-skill-pack（取代先前 part-2-B packager brief + 修正 A 的定位）
- **Stage**: brainstorming（discovery 已大量經由本 session 的 dogfood + 業界研究 + user 架構修正完成）→ checkpoint → writing-plans
- **取代/修正**：`2026-06-02-dbt-wiki-nl2sql-skill.md`（A+B 願景）、`2026-06-02-dbt-wiki-nl2sql-packager-part2-B.md`（舊 B）、`2026-06-02-dbt-wiki-to-sql-semantic-guardrails.md`（A 的護欄）。**A（永不連倉的獨立 to-sql skill）退場**，好東西併入本案。

---

## Problem（Axis 1 — JTBD）

**When** 一個分析師/agent 要對**這個 dbt 專案的資料倉庫**回答商業邏輯問題，**I want** agent 手上有這個專案**蒸餾好的業務語意**（entity/metric 意義、join grain、value domain、正確聚合形式、陷阱 caveat），**so I can** 讓一個**連倉的 agent** 高效率**且正確**地生 SQL→執行→分析——而不是冷啟動亂猜、產出合法但算錯的 SQL（dogfood 實證：聚合 3x、fan-out 84x、value-grounding 0 列）。

**核心修正**：dbt-wiki 不做 NL2SQL 引擎、不負責執行。它是**知識/脈絡層**；執行交給**連倉工具**（redshift MCP / DBHub / dbt show…）。最終交付物 = **把蒸餾知識封裝成一個可攜 Agent Skill**，agent 載入它做 grounding，再用連倉工具執行。

## Users（Axis 2）

- **主要消費者**：一個 **Skills-相容、且已接了連倉工具的 agent**（Claude Code 等），由分析師驅動。agent 載入「知識 skill」當脈絡。
- **知識 skill 的接收者**：可能是**沒有 dbt 專案、只有自己倉連線**的人（可攜性 = B 的原始前提）——拿到 bundle + 自己的連倉工具就能用。
- **生產者**：wiki owner，在**連倉環境**跑蒸餾（init），所以蒸餾可用真實資料把知識做厚。
- **約束**：消費端 agent 必須自備連倉工具（執行不在本案）；知識 skill 本身只提供脈絡/指引，不執行。

## Smallest End State（Axis 3）

**交付物 = 一個 packager**：把 `.dbt-wiki/` 蒸餾知識 → 自包含**「知識 skill」bundle**（Agent Skill / SKILL.md 形式），設計成**搭配連倉工具被 agent 消費**。

Bundle 內容：
1. **凍結的蒸餾知識**：entities/metrics/concepts + 欄位卡 + 關係圖（含**複合 join key**）+ **value_domain**（連倉蒸餾時用真實 DISTINCT 充實）。
2. **生成指引（不是執行器）**：把先前 A 的語意護欄（聚合 SUM/SUM、fan-out 防護、value-grounding、source 消歧、時間 grounding）改寫成「**給連倉 agent 的 SQL 生成指引**」——agent 照著生 SQL，**用自己的連倉工具執行 + 迭代**。
3. **gold examples（few-shot 脈絡）**：少量 in-domain 問題→正確SQL，連倉蒸餾時可**實際執行驗證**（不再只靠靜態）。
4. **SKILL.md（消費契約）**：指示 agent「① 讀此知識 grounding ② 生 SQL（遵生成指引）③ **用你的連倉工具執行** ④ 看結果迭代」。**工具無關**（不綁特定 MCP）。
5. 快照註記（來源 manifest_sha + build 日期 + rebuild 指引）。

**驗收**：給定一個（合成）`.dbt-wiki/`，packager 產出一個 Agent Skill bundle；該 bundle 在「只有 bundle + 一個連倉工具」的環境下，能讓 agent grounding 出正確 SQL（用連倉工具執行驗證）。

**最小化**：bundle 是**知識+指引**，不含執行器；蒸餾的「連倉充實」優先**讀 `catalog.json`（dbt docs generate 已產出真實型別/列數）+ 可選的連倉工具補 value_domain**，而非在 dbt-wiki 內建 DB driver（見 OQ-A）。

## Current State Evidence

- **Forward**：dbt-wiki 現有 init(蒸餾)/query/refresh/ingest；`to-sql` skill（A）剛建（branch `feat/dbt-wiki-nl2sql-to-sql`，已 force-push 清乾淨的 `c3faac5e`）含 SKILL.md + validate_sql.py + retrieval.md + prompt-assembly.md(§4e-§4h 護欄)。**A 的護欄 + schema-linking = 本案要併入的素材**。
- **Reverse/SSOT**：`skills/init/assets/SCHEMA.md` 擁有頁型；`catalog.json` 已被定義為「可選、真實倉型別/列數」(`SCHEMA.md` Architecture 段)；無 distribute.py（dbt-wiki 自包含）。knowledge layer 由 init 產、query 消費（泛型，無 allowlist）。
- **Error/邊界**：消費端缺連倉工具 → bundle 只能 grounding 不能執行（需在 SKILL.md 講清「需自備連倉工具」）；蒸餾若連倉 → 治理（真實資料/SQL 不進 public repo）。
- **Data**：蒸餾輸入 = manifest.json + compiled SQL（既有）+ **可選 catalog.json/連倉**（充實 value_domain/型別）；bundle 輸出 = 凍結知識 + 指引 + examples。
- **Boundary（治理硬護欄，本 session 剛踩過雷）**：真實 schema/SQL/資料**絕不進 public plugin repo**；真實 bundle 落使用者私有處；public repo 只放 packager 程式碼 + 合成（acme）示範 bundle。**永不 `git add -A`**（[[feedback_never_git_add_dash_A_in_this_repo]]）。

**Evidence paths**：`dbt-wiki/skills/to-sql/*`（A，待併入/退場）· `dbt-wiki/skills/init/assets/SCHEMA.md`（頁型 + catalog.json）· `dbt-wiki/skills/init/references/distill-*.md`（蒸餾規格，含剛加的 value_domain/複合鍵/ratio）· `docs/code-toolkit/specs/2026-06-02-dbt-wiki-gold-example-bank.md`（examples brief）

## Decision

**做**：建 **packager**，把 `.dbt-wiki/` 蒸餾知識封裝成**可攜「知識 skill」bundle**（Agent Skill 形式），設計為**搭配使用者自備的連倉工具**被 agent 消費（agent grounding→生 SQL→用連倉工具執行→迭代）。蒸餾允許用**連倉環境**充實知識（優先 catalog.json + 可選連倉補 value_domain）。把先前 A 的語意護欄 + schema-linking 改寫成 bundle 內「給連倉 agent 的生成指引」。gold examples 為 bundle 的 few-shot 脈絡，蒸餾時可執行驗證。

**不做**：
- **不自建 NL2SQL 引擎 / 執行器**（執行＝使用者的連倉工具；不跟 Vanna/Wren/dbt-text-to-SQL-expert 正面競爭）。
- **不在 dbt-wiki 內建 warehouse DB driver**（充實優先靠 catalog.json + 可選外部連倉工具；見 OQ-A）。
- **不保留 A 作為永不連倉的獨立 to-sql skill**（退場，併入 bundle 指引）。
- 真實資料進 public repo。

**為何這形狀**：(1) 解決「不連倉做 NL2SQL 很怪」——執行歸連倉工具，dbt-wiki 歸知識；(2) 蒸餾連倉讓知識厚（value_domain/型別真實）；(3) 可攜知識 skill 與執行工具**組合**，不重造引擎——差異化於「即時探索+執行」的競品（我們是事先策展的語意知識，給沒專案的人也能用）。

## Out of Scope
- 執行器 / 連倉 driver（使用者自備連倉工具）。
- 完整 text-to-SQL 引擎（用現成的）。
- 消費端 agent 的檢索/embedding（v1 靜態注入；bundle 小）。
- 真實資料 / bundle 進 public repo。

## Alternatives Considered（Axis 4 — 本 session 已研究）

1. **自建 NL2SQL 引擎**（Vanna OSS / Wren AI OSS）——[Vanna](https://github.com/vanna-ai/vanna)、[WrenAI](https://github.com/Canner/WrenAI)。Pros：完整。Cons：服務型、自己連倉+執行、重；我們不做引擎。**否決（用現成）**。
2. **dbt MCP + MetricFlow**——[dbt MCP](https://github.com/dbt-labs/dbt-mcp)。Pros：官方、on-scope 100%。Cons：需 Cloud/MetricFlow。**否決為自建**（有就用，但非我們的 niche）。
3. **dbt-text-to-SQL-expert（即時探索 + `dbt show` 執行）**——[mcpmarket](https://mcpmarket.com/tools/skills/dbt-text-to-sql-expert)。Pros：本地、不需 Cloud。Cons：查詢時即時探索（非策展知識）、連倉執行、第三方來源未明。**它是「執行工具」候選之一，不是我們的知識層**。
4. **官方 dbt-agent-skills 的 NL 問答 skill**——[github](https://github.com/dbt-labs/dbt-agent-skills)。其 NL→SQL 那塊**需 MetricFlow/Cloud** → 不符無 Cloud 前提。
5. **本案：可攜「知識 skill」+ 使用者連倉工具**。Pros：差異化（策展語意、可攜給無專案者、組合非競爭）、複用現成執行工具、解決不連倉矛盾。Cons：依賴使用者有連倉工具；快照會 stale。**← 採用**。

**My take**：採 5。Why：把 dbt-wiki 定位成「讓連倉 agent 更懂這個專案、更不算錯」的可攜知識層，與執行工具組合而非重造——這是它真正差異化且不過度建造的位置。Conditional reversal：若使用者環境固定有 dbt Cloud + MetricFlow，直接用 dbt MCP，本案降為補充。

## What Becomes Obsolete（Axis 5）

- **A（`skills/to-sql/` 永不連倉獨立 to-sql skill）退場**：其 SKILL.md「自己生+靜態驗、不執行」的殼丟棄；schema-linking + §4e-§4h 護欄**改寫進 bundle 的生成指引**；validate_sql.py 降為**可選 pre-check**（真驗證＝連倉執行）。**這是本案要清理的技術債**（A 的 branch 還沒 merge，正好趁此重定位，不留半套）。
- 先前「A+B 兩件事」收斂成「**知識層 + packager（B）**」一條線。

## Open Questions

- **OQ-A — ✅ LOCKED 2026-06-03**：蒸餾的「連倉充實」= **(a) 讀 `catalog.json`（零新依賴）+ 可選外部連倉工具補 value_domain**。dbt-wiki 本體**不內建 DB driver、保持 warehouse-agnostic**；連倉是「環境提供」而非 dbt-wiki 內建。
- **OQ-B**：bundle 的 SKILL.md 對「連倉工具」要工具無關（泛指）還是綁一個（如 redshift MCP）？傾向**工具無關 + 舉例**。
- **OQ-C**：A 的 branch（`feat/dbt-wiki-nl2sql-to-sql`，未 merge）怎麼處置——直接重定位成本案、還是先關掉？傾向**重定位**（複用護欄/知識，丟棄 to-sql 殼）。
- **OQ-D**：gold examples 仍照舊 brief（合成+人工，連倉蒸餾可加執行驗證）——本案是否把它併進來一起做，還是仍獨立增量？
