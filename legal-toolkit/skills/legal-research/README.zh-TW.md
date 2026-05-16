# legal-research

Read this in: [English](README.md) | [日本語](README.ja.md) | **繁體中文**

![version](https://img.shields.io/badge/version-0.1.0-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![phase](https://img.shields.io/badge/phase-3_SP3--b-orange)

> ⚠️ **本工具不是律師意見。** 本工具為免費 open-source utility，非律師事務所、亦非執業律師。輸出為 法律意見，僅供 in-house 法務 內部參考；涉及刑事 exposure / 主管機關 應對 / 重大經營判斷的案件，請務必交由執業律師處理。每份輸出皆會附上 §6.3 Mandatory Disclaimer footer（詳下）。

台灣 in-house 法務 IRAC legal-research skill。讀取 法律問題 / 條文號 / 判決字號 query，跑 plan-first 半互動 Agent loop（LLM 規劃搜尋 → user Y/n 確認 → 自主 WebFetch + triangulation + Harvey doc-level citation），產出 4 個檔案：`plan.md` + `state.json` + `research-memo.md` + `executive-summary.md`。Pure-LLM + WebFetch workflow；不外取資料；不依賴 `legal-playbook/profile.yml`。

## 什麼時候用

- 法條原文 lookup —「§227 是什麼？」/「民法 §184 構成要件」
- 判例 / 判決 趨勢 search —「民國 110 年後 不完全給付 carve-out 判決」
- 函釋 lookup —「個資法 §27 適當安全措施 PDPC 函釋」/ 學說 reference 查找
- 從 `legal-issue-spot` ⚠️ 信心不足要件 handoff 過來的 specific query

## 什麼時候不用

- **事實情境分析**（「我們想做 X，能不能做？」）→ 改用 `legal-issue-spot`（v0.5.0+，IRAC 議題盤點 + 構成要件 涵攝 + 風險分級）
- **合約 review**（既有合約檔案或貼上的條文）→ 改用 `legal-contract-review`
- **書面起草**（通知函 / 警示函 / 終止合約信）→ 改用 `legal-document-draft`
- **事後 incident response**（已發生外洩 / 已收到 主管機關 來文 / 對方已違約）→ 改用 `legal-incident-response`

## Input format

- **Required at session**：`--query="<自由文 query>"` — 1-3 行的法律查詢字串（例：`--query="不完全給付 §227 carve-out 民國 110 年後判決趨勢"`）
- **Opaque input** — query string 對本 skill 是 opaque；`protocols/plan.md` Step 1 抽出 ≥ 3 關鍵字 + ≥ 2 target site + 法源類型 plan，不對 caller-side 詞彙做 schema 驗證
- **不依賴 `profile.yml`** — 分析是 query-driven，不是 company-identity-driven（router Q4-law-lookup 跳過 profile prerequisite check）

## Output format

每次 session 寫入 `<cwd>/legal-outputs/<YYYY-MM-DD-HHmm>-research-<topic>/`：

| File | Audience | Sections |
|---|---|---|
| `plan.md` | 法務 + 業務（reproducibility checkpoint）| §問題 / §關鍵字 / §目標 site / §法源類型 plan / §Budget |
| `state.json` | 機器（grader + LLM loop）| rounds / fetches / sources[] / types_covered{} / early_stop / forced_stop / timestamps |
| `research-memo.md` | 法務 / GC / 內部簽核 | §問題 / §搜尋摘要 / §法源分析 / §結論 / §Citations（Harvey doc-level）/ §Disclaimer（+ conditional ⚠️ block prepended）|
| `executive-summary.md` | 非法務（CEO / BD / 業務 / PM）| §問題 / §結論（✅/⚠️/❌）/ §依據 / §風險提示 / §Disclaimer（+ conditional §Escalation）|

Schema validation：4 個檔都有 JSON Schema contract（`assets/plan-schema.json` / `assets/state-schema.json` / `assets/output-schema-memo.json` / `assets/output-schema-summary.json`），由 `scripts/grade_research.py` 消費。

## Plan-first 半互動 contract

在燒任何 fetch budget 之前，skill 會先寫出 `plan.md` 並要 user 確認。這是 **mandatory + 不可略過**，pattern 沿用 v0.4.2 SP3b `classify-path` Y/n precedent：

1. LLM 解析 `--query=...`
2. LLM 把 `plan.md` 寫到 disk 並把完整內容 print 到 stdout
3. LLM 詢問：`Plan OK 嗎? (Y/n)` — 固定 zh-TW 字串，不能變體（router log match 這個 surface form）
4. **Y** → 進入 `protocols/iterative-search.md` Step 1
5. **n**（或非 Y）→ skill 退出，`plan.md` 留在 disk；user 改 query 後重跑

Rationale（Q5 lock）：`plan.md` 是便宜的 reproducibility checkpoint，在 30-fetch 預算還沒燒之前先讓 user 把關 token 成本；auto-dispatch 會 silently burn budget。

## Agent loop spec

LLM-driven loop with deterministic state tracking via `state.json`。Python 只負責 state 持久化；LLM 在每個 iteration 開頭 re-read `state.json` + `protocols/iterative-search.md`，自行決定 continue / early-stop / forced-stop。

**Cap parameters**（集中於 `assets/triangulation-config.json`，v0.5.3 patch room 保留）：

| Parameter | Value | Meaning |
|---|---|---|
| `max_rounds` | **5** | 觸發 forced_stop 的 loop iteration 上限 |
| `max_fetches` | **30** | 觸發 forced_stop 的 WebFetch tool call 上限 |
| `early_stop_min_sources` | **8** | early_stop 的 `len(sources)` 下限 |
| `early_stop_min_types` | **2** | early_stop 的 `len(types_covered)` 下限（4-type ∩ 對新領域 query 太嚴；2-type 較實際）|

**forced_stop 不是失敗模式** — 它是 safety net。cap 觸發而 early_stop 未達時，memo 仍會產出，但會在 §問題 上方 prepend ⚠️ `覆蓋未達 triangulation` block，明示 coverage 不足 + 結論信心降級。Grader 把 forced_stop + ⚠️ marker 判為 exit 2（`PASS_WITH_NOTES`），不是 exit 1（`FAIL`）。

## Cross-skill handoff（INBOUND only）

`legal-issue-spot/business.md` 當 構成要件 涵攝 表出現 **≥ 1 ⚠️**（信心不足要件）時，會在 `## §建議下一步` block 列出 `/legal-research` 用的 specific query string：

```markdown
- §227 不完全給付的 carve-out 認定
  → `/legal-research --query="不完全給付 §227 carve-out 民國 110 年後判決趨勢"`
```

這是 **soft handoff** — user 自己 copy command 來跑；不會 auto-dispatch（Q8 lock：user 控管 token budget）。本 skill 把 `--query=...` 當 opaque input 收（Q6 + Q8 lock：不跟 issue-spot 詞彙做 brittle alignment）。**反向 handoff（research → issue-spot）刻意不做** — research input 不是 fact pattern，沒有可靠 signal；router Q4 dispatch 會接住誤 routing 的 query。

## §6.3 Disclaimer footer

每份輸出檔末尾都必須附上 §6.3 Disclaimer footer（canonical 文字 SoT 在 `protocols/cite.md`，鏡像 v0.5.0 `legal-issue-spot/protocols/risk-grade.md` ownership）。內容涵蓋：AI 工具 attribution / 非正式法律意見 / 現行台灣法 scope / 訴訟、簽約、刑責、cross-border、高風險決策請洽 律師。Grader 會 grep canonical sentinel substring；缺 footer → exit 1（FAIL）。本 skill 產出 法律意見 — disclaimer 是 mandatory，不是 optional。

## §6.4 Escalation Override

當 `state.json.forced_stop == true` 或 query 涉及 **刑事 / 訴訟 / 跨境 / 重大金額** 時，`executive-summary.md §Escalation` 同樣 hard-wired — LLM 不能 soften 也不能 skip 律師 建議。觸發條件 + §Escalation template 詳見 `protocols/cite.md` §6.4 trigger table；grader 會驗證 forced_stop ↔ §Escalation 對齊。

## 參考

- 完整 skill 說明：[`SKILL.md`](SKILL.md)
- Design spec：[`docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md`](../../../docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md) §6
- Plugin spec：[`legal-toolkit/PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) + [`legal-toolkit/TECH-SPEC.md`](../../TECH-SPEC.md)
- ROADMAP：[`legal-toolkit/ROADMAP.md`](../../ROADMAP.md)
- Sibling skill（handoff source）：[`legal-issue-spot/SKILL.md`](../legal-issue-spot/SKILL.md)
