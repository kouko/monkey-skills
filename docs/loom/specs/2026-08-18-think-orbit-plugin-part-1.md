# think-orbit plugin — Part 1（格式・機械閘・假設傳播・核心對話協定・骨架 → 真實素材檢查點）— brief

> **Phase**: brainstorming output (`brainstorming` → `writing-plans` handoff) — **Part 1 of 2**
> **Date**: 2026-08-18
> **Author**: agent (Fable 5) + kouko
> **Umbrella brief**: `docs/loom/specs/2026-08-18-think-orbit-plugin.md`（總覽：Problem／Users／
> Alternatives／Diagrams 的完整版在那裡；本 part 只重述計畫所需的最小內容，並用自己的 BI 編號。
> 括號內 `[U BI-n]` 指回總覽的條目。）
> **Sibling**: `docs/loom/specs/2026-08-18-think-orbit-plugin-part-2.md`（視圖／編提案／里程碑／發佈）。
> **Why split**: 完整 v0 一份計畫的關鍵路徑深度 6–7 > 5（writing-plans 硬上限）；使用者 2026-08-18
> 選 A＝拆兩份 brief／兩份計畫，範圍不變。Part 1 的最後一項是真實素材檢查點；Part 2 在檢查點
> 回饋後開工。
> **Design-side on-ramp**: direct（見總覽）。**Continuous mode**: not named — human-pumped.
> **Name**: `think-orbit`（使用者 2026-08-18 定案）。**Skill shape**（使用者 2026-08-18 選 B）：入口路由 `using-think-orbit`
> ＋動詞 skill `decision-session`／`break-assumption`（Part 2 再加 `render-views`／`compile-proposal`）；腳本在 plugin 層
> `think-orbit/scripts/`（三 skill 共用）；每個 SKILL.md ≤4,500 words，references 在 decision-session 下、其他 skill 以
> `${CLAUDE_PLUGIN_ROOT}` 路徑指過去。

## Problem

（同總覽 §Problem；使用者原話：）「可以讓使用者與 agent 的討論互動所產生的整個研究、假設與決策過程
都可以有一個完整的 CoT 形式的文件群記錄」。使用者 2026-08-18 再對齊核心概念（verbatim）：「將 CoT
透明化，並用 DAG 圖＋每個節點一個獨立文件 的方式提供給使用者觀看/編輯」。Part 1 解決的是這個 job 的**地基**：檔案就是圖、
每個節點邊界有靜默機械閘、前提破了知道哪裡要重看、以及一套只打斷三次的對話協定——足以讓
使用者拿自己的真實素材跑一輪。

## Users

- **kouko（唯一使用者）** — 在 Claude Code 對話；節點檔放在自己指定的專案資料夾（多半在
  Obsidian vault）；來源＝本地檔＋Notion／Drive（經 MCP，plugin 不處理存取）；會在手動編輯與
  對談之間來回；每段 2–4 句、一段一個概念。
- **未來的 agent session** — 只從 frontmatter 現算圖，不讀渲染後的視圖檔。
- **條件** — 價值只在跨階段出現；agent 只在三處打斷（定目標／開分支問假設／下決定）。

## Smallest End State

Part 1 交付後：plugin 骨架在 repo 內、有自己的 CI lane；使用者在任一資料夾說「我要決定 X」，
agent 依對話協定寫 `GOAL/FACT/CLAIM/DECISION` 節點檔與假設檔（≤3／分支、agent 起草人確認、
可證偽測試），每個節點邊界靜默跑機械閘腳本（失敗才一行），使用者宣告假設破裂時腳本沿承重鏈
標 `stale`、輸出影響範圍視圖、不重算；研究筆記以其 `claim` 一行被引用、`claim` 變了才通知下游。
整張 DAG（GOAL→…→DECISION，含分支與假設）由腳本畫成一張基本 Mermaid 全圖給人看。
成功判準：腳本 pytest 全綠＋CI lane 跑得動；**使用者用自己的真實素材跑完一輪、對著 DAG 全圖與
節點檔寫下檢查點結論**（格式要不要改）。非判準：不做主線折疊／分支逐條展開／假設逐一聚焦等
局部渲染、不編提案、不做里程碑 commit（Part 2）；不量分類正確率。

- BI-1 — Node files: one markdown file per reasoning node with frontmatter `type` (GOAL|FACT|CLAIM|DECISION), `id` (author-named, never derived), `seq` (monotonic CoT order), `inputs` (list of `{ref, load_bearing: bool}`), `summary` (one line), `status` (current|stale); FACT adds `source` + `quote`; branch members add `branch` + `branch_type` (exclusive|complementary); no draft layer. [U BI-1, BI-7 data half]
- BI-2 — Assumption files: `assumptions/<id>.md` with `id`, `status` (open|broken|confirmed), `statement`, `breaks_if`, `source`, `branch`; ≤3 per branch; agent drafts, user confirms; falsifiability check ("what event breaks it") or sent back. [U BI-2]
- BI-3 — Research note as FACT: a `research/*.md` note carrying frontmatter `claim` is loaded as one FACT node whose citable content is the `claim` line; a `claim` changed since the last git revision lists its dependents (git diff, no hashing). [U BI-3]
- BI-4 — Mechanical gate script (`check`): every `inputs` entry carries `load_bearing`; every `inputs.ref` resolves to an existing node / assumption / research claim; FACT carries `source` + `quote`; paragraph form (≈2–4 sentences per body paragraph); silent + exit 0 on pass, one line per failure + exit 1 on fail; never edits files. [U BI-4]
- BI-5 — Assumption-broken propagation (`break`): on `status: broken`, transitive dependents reached through a load-bearing chain get `status: stale`; dependents reached only through non-load-bearing edges are reported as weakened, not marked; nothing is recomputed; the impact view (assumption-focused Mermaid) is rendered. [U BI-5, and the impact-view half of BI-6]
- BI-6 — Core conversation protocol (SKILL.md): intake (project dir + sources) → agent asks the goal → GOAL confirmed → branches (`exclusive|complementary`) → assumptions drafted/confirmed → silent node writes for every reasoning step (procedural/social content produces no node) → gate at every node boundary; resume opening restates last decision + open assumptions; break-assumption flow (agent raises hand, user declares, "direct dependents only" vs "full impact"); three interrupt points only; user may hand-edit files between turns; agent must not read rendered `views/` files; blind-spot checklist offered when a branch opens. [U BI-8, BI-7 semantics]
- BI-7 — Research rules in SKILL.md: project docs answer → infer; one missing external fact → verify with ≤1 arm and write result + source into the current note; topic survey or explicit request → standalone research note; any external fact entering the reasoning must be findable in the docs. [U BI-9]
- BI-8 — Plugin scaffold: `think-orbit/` with `.claude-plugin/plugin.json` (version 0.1.0) + `.codex-plugin/plugin.json` mirror, tri-language READMEs (may be short), `CHANGELOG.md`, marketplace entry, and a repo-root CI workflow `think-orbit-ci.yml` running pytest over the skill's `scripts/` and the skill-folder-structure hook; SKILL.md ≤4,500 words self-enforced. [U BI-12 scaffold half]
- BI-9 — Real-material checkpoint: after BI-1..BI-8 land, the user runs one real decision through the protocol; findings + any schema deltas are recorded in `docs/loom/dogfood/2026-08-<dd>-think-orbit-real-material.md`; Part 2 starts only after this file exists. [U BI-13]

## Current State Evidence

同總覽 §Current State Evidence（接點：marketplace 登錄、`check_version_bump.py`、
`check-plugin-description-skill-coherence.yml`、skill-structure 掃描不含新 plugin → 自帶 CI lane，
樣板 `tsundoku-ci.yml:10-17,42-52`；loom-memory 教訓清單）。本 part 不新增證據；
`Evidence paths` 見總覽。

- **Forward**: 總覽 §Forward。
- **Reverse**: 無 caller。
- **Error**: 總覽 §Error（CI 掃描缺口 → BI-8 自帶 lane）。
- **Data**: 專案資料夾在 repo 外；plugin 內只有 SKILL 文字、腳本、schema 參考、pytest。
- **Boundary**: 總覽 §Boundary（`[FRAGILE]` 衍生視圖只重生成；閘為腳本非散文；fail-closed 顯式；id 由作者命名）。
- **Evidence paths**: 見 `docs/loom/specs/2026-08-18-think-orbit-plugin.md` §Evidence paths。

## Decision

Part 1 蓋地基與檢查點：schema 參考文件＋載入器、`check`（機械閘）、`break`（傳播＋影響範圍視圖）、
研究筆記 `claim` 連結、基本 DAG 全圖（CoT 透明化的觀看面）、核心對話協定（含研究規則、三個打斷點、
禁讀視圖）、plugin 骨架與 CI lane，最後由使用者以真實素材跑一輪。**不做**（留 Part 2）：主線折疊／
分支逐條展開／假設逐一聚焦等局部渲染、編提案、里程碑
commit、SKILL 的視圖／編提案段落、正式版本發佈。三個預設值照總覽：需求驅動抽取、允許一段多重
角色、存放在使用者指定資料夾。腳本以 Python stdlib 為主（frontmatter 用簡單 YAML 子集解析或
`yaml` 若 repo 既有慣例允許——由計畫決定並註明外部表面）。

- BI-10 — Umbrella (Part 1): the scaffold + scripts (`check`, `break`, claim-diff, loader, basic DAG render) + core SKILL land in `think-orbit/`, and the real-material checkpoint file exists before Part 2 begins.
- BI-12 — Basic DAG view (`render`): one Mermaid flowchart of the whole graph written to `<root>/views/dag.md` — every node in `seq` order (shape by `type`, `stale` nodes greyed), assumptions as stadium nodes attached to their branch, edges from `inputs` (dashed when `load_bearing: false`), branch members grouped by `branch`; regenerated from frontmatter, generated-marker comment first line, human-only; no collapsing / partial rendering (Part 2). [U BI-6 basic half — the CoT made visible]

## Out of Scope

- 主線折疊、分支逐條展開、假設逐一聚焦等局部渲染，編提案、里程碑 commit（Part 2）。
- 併入 loom 家族；外部來源存取；深度研究本身；矛盾偵測；多人／權限；Obsidian 寫作規則整合；
  正確率量測；每型別 JSON Schema（同總覽）。

## Alternatives Considered

見總覽 §Alternatives Considered（EN＋JA 研究表）。本 part 額外一列：

| Alternative | Who ships it / source | Why rejected |
|---|---|---|
| 一份計畫硬塞到深度 5（檢查點降為 Notes） | agent 於 writing-plans 提出 | 視圖會蓋在未經真實素材驗證的格式上，BI-13 形同虛設；使用者選拆兩份 |

## What Becomes Obsolete

- BI-11 — Nothing in the repo (new plugin; purely additive by nature — see umbrella).

## Open Questions

（空——預設值已寫入 Decision；schema 若在檢查點被推翻，改的是 Part 2 的 brief，不回頭改此 part。）

## Diagrams

Part 1 的資料流是總覽第一張圖去掉 `views/` 主線／分支與 git commit 的子集；狀態圖同總覽第二張。
不重畫（SSOT 在總覽），此處 N/A — no flow/state/architecture-shaped content beyond the umbrella's two diagrams: this part adds no new flow.
