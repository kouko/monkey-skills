# Protocol — cite

FINAL synthesis step of the 4-protocol pipeline (plan → iterative-search →
triangulate → **cite**). Reads `state.json` + the optional ⚠️ block
prep file emitted by `protocols/triangulate.md`, then synthesizes the
two user-facing outputs (`research-memo.md` for 法務 / `executive-summary.md`
for 業務), each carrying inline citations to a Harvey doc-level
`## §Citations` manifest and ending with the canonical §6.3 Disclaimer
footer. Also conditionally emits the §6.4 Escalation banner on
`executive-summary.md` when `forced_stop` OR the query domain involves
刑事 / 訴訟 / 跨境 / 重大金額.

## Purpose

This is the SYNTHESIS + DISCLAIM + ESCALATE step. Earlier protocols
plan / fetch / triangulate; this protocol assembles the final memo
+ summary and **owns the canonical §Disclaimer text** for this skill
(mirroring the v0.5.0 pattern where `legal-issue-spot/protocols/risk-grade.md`
owns its disclaimer SoT). The LLM does NOT re-run searches here — it
reads `state.sources` + the (optional) ⚠️ block prep file produced by
triangulate, and writes the two output files.

## Inputs

Read from disk:

- `state.json` — the deterministic checkpoint produced by the loop
  (rounds / fetches / sources[] / types_covered{} / early_stop /
  forced_stop / timestamps + triangulate.md additions:
  `triangulation_assessment` + `final_types_covered_count`); MUST be
  present and well-formed. **state.json is the single SoT** — there is
  no separate `triangulate-prep.md` file; the ⚠️ block is reconstructed
  here at prepend-time from state.json fields.
- The original `--query=...` string (re-read from `plan.md` §問題)

**Halt + ask fallback** — if any required input is missing or
corrupt, halt and report:

```
⚠️ cite halt — 缺少必要前置輸入：
  - missing: <list — e.g. state.json / plan.md §問題>
  - 必須先重跑：<該檔對應的 protocol — plan.md / triangulate.md / re-run from --query>
請補齊後再執行 cite.md。
```

Do NOT fabricate missing inputs. Specifically:

- `state.json` missing → halt + ask user to re-run plan-first
- `state.json.triangulation_assessment` missing → halt + ask user to re-run from triangulate.md
- `state.sources` empty → halt (defensive; this should have been caught
  by triangulate emitting a coverage failure earlier)

## Outputs

This protocol writes to **two files** under
`<cwd>/legal-outputs/<YYYY-MM-DD-HHmm>-research-<topic>/`:

| File | Audience | Sections (in order) |
|---|---|---|
| `research-memo.md` | 法務 / GC / 內部簽核 | [⚠️ block, if forced_stop] / §問題 / §搜尋摘要 / §法源分析 / §結論 / §Citations / §Disclaimer |
| `executive-summary.md` | 非法務 (CEO / BD / 業務 / PM) | §問題 / §結論 / §依據 / §風險提示 / [§Escalation, conditional] / §Disclaimer |

Both files end with the canonical §Disclaimer block (verbatim — see
§Disclaimer canonical text below).

## Procedure

Step-by-step. Do NOT skip steps; do NOT re-order.

1. **Read `state.json`** — validate schema (rounds / fetches / sources / types_covered / early_stop / forced_stop / timestamps + triangulate additions `triangulation_assessment` + `final_types_covered_count`); halt on missing or corrupt.
2. **Reconstruct ⚠️ block** (only when `state.triangulation_assessment ∈ {"forced_stop", "coverage degraded"}`) — build the block from state.json fields directly:
   - `rounds` / `fetches` / `len(sources)` / `final_types_covered_count` (all from state.json)
   - Template (zh-TW; PREPEND above §問題 in research-memo.md):
     ```
     > ⚠️ **覆蓋未達 triangulation** (forced_stop)
     >
     > 本研究於 cap 達到時退出 (rounds=<rounds>/5 或 fetches=<fetches>/30)，未達 early_stop 條件 (≥ 8 sources + ≥ 2 法源類型)。
     >
     > 實際覆蓋：<len(sources)> sources / <final_types_covered_count> 法源類型。
     >
     > 建議：擴大關鍵字 + 重跑 `/legal-research --query="..."`，或諮詢執業律師補充覆蓋。
     ```
3. **Re-read `plan.md` §問題** — to lift the original user query string verbatim for both files' §問題 sections.
4. **Assemble `research-memo.md` body** in this order:
   1. If `state.triangulation_assessment ∈ {"forced_stop", "coverage degraded"}`: PREPEND the reconstructed ⚠️ block (from Step 2) above §問題.
   2. `§問題` — restate the user query in 1-2 sentences (lift from `plan.md`).
   3. `§搜尋摘要` — brief recap: keywords used / sites visited / 法源類型 plan vs actual coverage (1 short paragraph + optional bullet list).
   4. `§法源分析` — the analytical body. Inline citations use `[<bracketed cite>]` form (e.g. `[§Citations #2]` or `[最高法院 109 台上 1234]`), each tied to an entry in the `§Citations` manifest below. zh-TW user-facing prose; preserve 條文/判決/函釋 字號 verbatim.
   5. `§結論` — direct answer to the user's query, citing specific §Citations entries by number or by full reference.
5. **Emit `§Citations` manifest** — for EVERY source in `state.sources` that was actually used in §法源分析 / §結論, emit one numbered entry following the Harvey doc-level template (see §Citations format below). Each entry MUST carry: 法源類型 / full reference (官方來源 + 識別字號 + 引用日期) + 1-line relevance to the conclusion.
6. **Assemble `executive-summary.md` body** in this order:
   1. `§問題` — same query restatement (1-2 sentences; 業務 tone).
   2. `§結論` — exactly one of `✅` / `⚠️` / `❌` marker + 1-sentence plain-language conclusion. Choice rule:
      - `✅` — research answers the query with ≥ 2 法源類型 coverage AND no `forced_stop` AND no 反對 學說 / 矛盾 判決 trend
      - `⚠️` — answers conditionally (carve-outs / trend uncertainty / `forced_stop` with partial coverage / 函釋 vs 判決 conflict)
      - `❌` — research could NOT answer (insufficient sources OR query is mis-routed)
   3. `§依據` — bullet list of TOP 3 citations supporting the conclusion (link by number to the `§Citations` manifest in `research-memo.md`).
   4. `§風險提示` — bullet list of caveats / open questions / coverage gaps (1-3 bullets; surface what user should know even when conclusion is ✅).
7. **Evaluate §Escalation trigger** (hard-wired, NOT LLM judgement; see §6.4 trigger table below). If any trigger fires, append `## §Escalation` to `executive-summary.md` BEFORE `## §Disclaimer` (Escalation comes second-to-last; Disclaimer is always the final block).
8. **Append §Disclaimer** to BOTH files — copy verbatim from the canonical text below (do NOT paraphrase; grader greps for sentinel substrings). The leading `---` separator IS part of the block.
9. **Write both files** to the session output directory. Filenames: `research-memo.md` + `executive-summary.md` (no timestamp suffix; directory already carries it).

## §Citations format (Harvey doc-level)

Manifest section in `research-memo.md`. Numbered list; each entry
covers ONE source; format below MUST be followed so grader's
`citation_has_relevance` check passes (each citation must carry a
1-line relevance pinpoint).

Template (numbered list):

```markdown
## §Citations

1. **<法源類型>**: <full reference — 法典名/判決字號/函釋字號 + 官方來源 + 引用日期>
   → <1-line relevance to the conclusion — why this source matters here>

2. **<法源類型>**: ...
   → ...
```

Worked examples across the 4 法源類型 (cover all four in your manifest
when coverage permits):

```markdown
## §Citations

1. **條文**: 民法 §184 第一項前段 (中華民國民法; 全國法規資料庫 pcode B0000001;
   引用日期 2026-05-15; url: https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=B0000001)
   → 本案請求權基礎核心；構成「不法侵害他人權利」之主要構成要件依據。

2. **判決**: 最高法院 109 年度台上字第 1234 號民事判決
   (司法院判決系統; 引用日期 2026-05-15;
   url: https://judgment.judicial.gov.tw/FJUD/data.aspx?id=...)
   → 判決採人格權說，明確界定「不法性」涵攝範圍；可作為本結論之 leading 案例援引。

3. **函釋**: 法務部 法律字第 11012345 號函 (2026-04-15 發布;
   法務部主管法規查詢系統; 引用日期 2026-05-15)
   → 闡釋 §27 「適當安全措施」之 主管機關 操作判準；補強條文文義之模糊地帶。

4. **學說**: 王澤鑑《債法原論》第一冊 §3-2-1 不完全給付之構成 (新學林出版, 2022 修訂版, 頁 184-187;
   引用日期 2026-05-15)
   → 通說採二元說（瑕疵給付 / 加害給付）；本結論之分類框架依據。
```

Each entry MUST have:

- **法源類型** in bold — one of 條文 / 判決 / 函釋 / 學說 (zh-TW; do NOT translate)
- **full reference** — 識別字號 + 官方來源 + 引用日期; include url if from WebFetch
- **`→ <1-line relevance>`** — the trailing arrow + relevance text is **mandatory**; grader checks each citation has it (`citation_has_relevance`)

If a source was fetched but NOT used in the analysis, do NOT include
it in §Citations (citations are for sources that support the
conclusion; unused fetches stay in `state.sources` only).

Detailed worked examples for each 法源類型 live in
[`references/citation-format.md`](../references/citation-format.md)
(Task 3 forward-reference); consult that file if a 法源類型 needs
disambiguation (e.g. 函釋 vs 行政函令 vs 解釋令).

## §Disclaimer canonical text (THIS PROTOCOL OWNS IT)

Verbatim boilerplate appended to BOTH `research-memo.md` and
`executive-summary.md`. **This protocol is the Single Source of Truth
for this disclaimer text** within `legal-research` (mirroring how
`legal-issue-spot/protocols/risk-grade.md` owns issue-spot's
disclaimer). Do NOT paraphrase when emitting; copy verbatim so the
grader's `disclaimer_footer` check passes:

```markdown
---

## §Disclaimer

本研究由 AI 工具（legal-toolkit / legal-research）產出，**不構成正式法律意見**。本工具：

- 僅就現行有效之中華民國法律進行法源檢索與分析；
- 不能取代具有律師資格之專業諮詢；
- WebFetch 取得之 判決 / 函釋 / 條文 內容可能因主管機關更新或網頁改版而失準；
- 對特定案件之適用性、最新主管機關函釋、未公開判決未必涵蓋；
- 不保證內容無誤、完整或最新。

具體案件如涉及訴訟、契約簽訂、刑事責任、跨境議題、或重大金額決策，請諮詢專業律師。
```

The leading `---` separator IS part of the boilerplate. The §Disclaimer
heading uses the § sigil per plugin convention (grader checks
`## §Disclaimer` literal).

## §Escalation template

When a trigger fires (see §6.4 trigger table below), append this
block to `executive-summary.md` immediately before `## §Disclaimer`:

```markdown
## §Escalation

⚠️ 本研究達成 §6.4 升級門檻，**強烈建議於採取任何行動前諮詢執業律師**。

升級觸發原因：
- <which trigger fired: forced_stop / 刑事元素 / 訴訟元素 / 跨境 / 重大金額>
- <1-line elaborate, e.g. "loop cap 達 30 fetches 仍僅取得 5 sources / 1 法源類型，覆蓋不足">

律師可協助：
- 補充本研究因 cap 退出未涵蓋之 leading 判決或函釋
- 評估特定案件之 判決趨勢與主管機關函釋走向
- 規劃具體行動 (書面意見 / 訴訟策略 / 合約條款設計)
```

zh-TW user-facing strings; do NOT translate domain terms.

## §6.4 Escalation triggers

Hard-wired logic — NOT LLM judgement. The LLM does not get to
"soften" or skip this when triggered.

| Condition | Detected from | Required action |
|---|---|---|
| `state.json.forced_stop == true` | `state.json` | MUST emit §Escalation block; reasoning line = "loop 達 cap (rounds≥5 OR fetches≥30) 未達 early_stop，覆蓋不足" |
| Query mentions **刑事 / 起訴 / 偵查 / 不起訴 / 緩起訴 / 起訴狀** | scan §問題 + plan.md keywords | MUST emit §Escalation; reasoning line = "查詢涉及刑事元素" |
| Query mentions **訴訟 / 上訴 / 起訴 / 民事訴訟 / 答辯狀 / 強制執行** | scan §問題 + plan.md keywords | MUST emit §Escalation; reasoning line = "查詢涉及訴訟元素" |
| Query mentions **跨境 / 涉外 / 域外 / 香港 / 中國 / 美國 / 日本 + (法律 \| 法規 \| 適用)** | scan §問題 + plan.md keywords | MUST emit §Escalation; reasoning line = "查詢涉及跨境議題" |
| Query mentions **重大金額 / 億 / 千萬 / 上市 / 併購 / M&A / 收購** | scan §問題 + plan.md keywords | MUST emit §Escalation; reasoning line = "查詢涉及重大金額決策" |

If multiple triggers fire, list ALL fired triggers under "升級觸發
原因" (do NOT collapse to one). The §Escalation block appears EXACTLY
ONCE per `executive-summary.md`.

Grader rule (per SKILL.md §6.4): if `state.json.forced_stop == true`,
`executive-summary.md` MUST contain `§Escalation` section with a
律師 keyword. Missing → exit 1. High-stakes-domain triggers are
SHOULD-level structurally (grader cannot reliably classify domain),
so they are LLM-judgement enforced at this protocol layer; the
forced_stop trigger is MUST-level grader-enforced.

## Halt + ask fallback (summary)

- `state.json` missing or corrupt → halt + ask plan-first re-run
- `state.sources` empty (should have been caught earlier) → halt
  defensively; report likely pipeline bug
- `state.triangulation_assessment` field missing → halt + ask user to
  re-run from triangulate.md (logic bug — that field is REQUIRED for
  the ⚠️ block reconstruction decision)
- `plan.md` §問題 missing or unreadable → halt + ask for re-run from
  `--query=...`

## Worked example

Query (benign, low-stakes; §Escalation NOT triggered):

```
--query="民法 §184 第一項前段 構成要件 簡介"
```

`state.json` summary: rounds=3, fetches=12, sources=8,
types_covered={條文:2, 判決:3, 函釋:1, 學說:2}, early_stop=true,
forced_stop=false.

`state.json.triangulation_assessment`: `"early_stop met"` (no ⚠️ block reconstruction; early_stop reached).

Synthesis output skeleton:

```markdown
# Research Memo — 民法 §184 第一項前段 構成要件 簡介

## §問題

使用者查詢民法 §184 第一項前段「因故意或過失，不法侵害他人之權利者，負損害賠償責任」之構成要件如何展開。

## §搜尋摘要

關鍵字：「民法 §184」「不法侵害」「侵權行為」「構成要件」；目標 site：law.moj.gov.tw / judicial.gov.tw / mojlaw.moj.gov.tw；
法源類型：條文 / 判決 / 函釋 / 學說 四類皆涵蓋；共 12 fetches / 8 sources。

## §法源分析

民法 §184 第一項前段之構成要件，依通說分為 (1) 行為 (2) 不法性 (3) 過失或故意
(4) 損害 (5) 因果關係五要件 [§Citations #4]。其中「不法性」之認定，最高
法院判決多採人格權說 [§Citations #2]，並援引主管機關函釋對「適當安全
措施」之闡釋 [§Citations #3]。

## §結論

民法 §184 第一項前段為一般侵權行為條款，五要件採通說架構，本研究涵蓋
條文 / 判決 / 函釋 / 學說 四類法源，結論信心度 HIGH（見 §Citations #1-#4）。

## §Citations

1. **條文**: 民法 §184 第一項前段 (中華民國民法; 全國法規資料庫 pcode B0000001;
   引用日期 2026-05-15)
   → 本研究核心條文；構成要件展開之文義基礎。

2. **條文**: 民法 §184 第二項 (中華民國民法; 全國法規資料庫 pcode B0000001;
   引用日期 2026-05-15)
   → 違反保護他人法律 (推定過失 路徑)；補強構成要件適用範圍。

3. **判決**: 最高法院 109 年度台上字第 1234 號民事判決
   (司法院判決系統; 引用日期 2026-05-15)
   → 確認「不法性」採人格權說；leading 判決趨勢。

4. **判決**: 最高法院 110 年度台上字第 567 號民事判決
   (司法院判決系統; 引用日期 2026-05-15)
   → 「相當因果關係」之具體 判定標準；強化第三要件涵攝。

5. **函釋**: 法務部 法律字第 11012345 號函 (2026-04-15 發布;
   法務部主管法規查詢系統; 引用日期 2026-05-15)
   → 補強「不法性」於 個資 場景之 主管機關 操作判準。

6. **函釋**: 法務部 法律字第 11023456 號函 (2025-08-20 發布;
   法務部主管法規查詢系統; 引用日期 2026-05-15)
   → 「損害」要件之 行政解釋；釐清純粹精神損害 vs 慰撫金邊界。

7. **學說**: 王澤鑑《侵權行為法》第二章 §1 構成要件展開
   (新學林出版, 2022 修訂版, 頁 45-58; 引用日期 2026-05-15)
   → 通說之五要件分類框架；本結論之 學理 依據。

8. **學說**: 王澤鑑《侵權行為法》第二章 §3 主觀要件
   (新學林出版, 2022 修訂版, 頁 78-92; 引用日期 2026-05-15)
   → 故意過失之主觀構成要件分析；補強第一要件涵攝深度。

---

## §Disclaimer

本研究由 AI 工具（legal-toolkit / legal-research）產出，**不構成正式法律意見**。本工具：

- 僅就現行有效之中華民國法律進行法源檢索與分析；
- 不能取代具有律師資格之專業諮詢；
- WebFetch 取得之 判決 / 函釋 / 條文 內容可能因主管機關更新或網頁改版而失準；
- 對特定案件之適用性、最新主管機關函釋、未公開判決未必涵蓋；
- 不保證內容無誤、完整或最新。

具體案件如涉及訴訟、契約簽訂、刑事責任、跨境議題、或重大金額決策，請諮詢專業律師。
```

Corresponding `executive-summary.md`:

```markdown
# Executive Summary — 民法 §184 第一項前段 構成要件 簡介

## §問題

使用者想了解民法 §184 第一項前段一般侵權行為的構成要件結構。

## §結論

✅ 一般侵權行為採五要件通說（行為 / 不法性 / 過失或故意 / 損害 / 因果關係），條文 + 判決 + 函釋 + 學說 四類法源一致支持。

## §依據

- §Citations #1 — 民法 §184 第一項前段條文本身
- §Citations #2 — 最高法院 109 台上 1234（人格權說 leading 判決）
- §Citations #4 — 王澤鑑《侵權行為法》通說五要件分類

## §風險提示

- 「不法性」之認定於 個資 / 隱私 / 名譽 不同 場景 仍須個別審視
- 主管機關函釋若於 2026 後更新，本研究未涵蓋
- 本研究為 一般 構成要件 介紹，非 具體 案件 涵攝

---

## §Disclaimer

本研究由 AI 工具（legal-toolkit / legal-research）產出，**不構成正式法律意見**。本工具：

- 僅就現行有效之中華民國法律進行法源檢索與分析；
- 不能取代具有律師資格之專業諮詢；
- WebFetch 取得之 判決 / 函釋 / 條文 內容可能因主管機關更新或網頁改版而失準；
- 對特定案件之適用性、最新主管機關函釋、未公開判決未必涵蓋；
- 不保證內容無誤、完整或最新。

具體案件如涉及訴訟、契約簽訂、刑事責任、跨境議題、或重大金額決策，請諮詢專業律師。
```

§Escalation NOT triggered (query is benign: no 刑事 / 訴訟 / 跨境 /
重大金額 keyword; forced_stop=false).

End of cite protocol.
