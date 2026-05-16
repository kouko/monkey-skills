# legal-research

Read this in: [English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

![version](https://img.shields.io/badge/version-0.1.0-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![phase](https://img.shields.io/badge/phase-3_SP3--b-orange)

> ⚠️ **法的助言ではありません。** 本ツールは無料 open-source utility であり、法律事務所でも執業弁護士でもない。出力は 法律意見 (legal opinion) として in-house 法務 の内部参考のみ — 刑事 exposure / 訴訟 / 跨境 / 重大金額 が絡む案件は必ず執業弁護士にエスカレーションすること。全ての出力は §6.3 Mandatory Disclaimer footer 付き（後述）。
>
> **対象**：台湾 in-house 法務 向け（zh-TW jurisdiction 専用）。日本法務には適用不可。

台湾 in-house 法務 向け IRAC legal-research skill。法律問題 / 條文號 / 判例編號 の query を受け取り、plan-first 半互動 Agent loop（LLM が search plan を立てる → user が Y/n で確認 → autonomous WebFetch + triangulation + Harvey doc-level citation）で執行し、4-file artifact set（`plan.md` / `state.json` / `research-memo.md` / `executive-summary.md`）を出力する。Loop は hard cap（≤ 5 rounds または ≤ 30 fetches）で bounded、early-stop（≥ 8 sources + ≥ 2 法源類型）で打ち切り、cap 到達時は forced_stop で ⚠️ marker を必ず付ける。`legal-playbook/profile.yml` 依存なし。

## こんな時に使う

- 法条文 lookup（例：「§227 不完全給付的條文是什麼？」「個資法 §27 的安全維護義務具體要做什麼？」）— literal な 條文 / 判決 / 函釋 / 学説 の triangulation 結果が必要
- 判決動向の調査（例：「民國 110 年後 §227 carve-out 的判決趨勢」）— 単一 source ではなく ≥ 2 法源類型 を跨ぐ structured iterative search
- `legal-issue-spot` の 構成要件 涵攝 で ⚠️ 信頼度不足要素が出た — そこから来る pinpoint query で research-memo を作る（inbound handoff、後述）

## こんな時には使わない

- **Fact pattern analysis**（「我們想做 X，能不能做？」business 相談）→ `legal-issue-spot`
- **契約 review**（既存契約 file または貼付け clause text）→ `legal-contract-review`
- **書面 drafting**（通知函 / 警示函 / 終止合約信）→ `legal-document-draft`
- **Incident response**（既発生の breach / 主管機関 来文受領済 / 取引相手側既違約）→ `legal-incident-response`

## Input format

- **Required at session**：`--query="..."` 引数（具体的な法律問題 / 條文號 / 判例編號 を含む zh-TW 文字列、例：`--query="§227 不完全給付 carve-out 民國 110 年後判決趨勢"`）
- **`profile.yml` 依存なし** — query は fact-pattern-driven ではなく law-text-driven であり、company-identity を必要としない
- **Query が 10 字未満 / 非法律内容** の場合、`protocols/plan.md` が halt + ask user fallback で停止する

## Output format

session 毎に `<cwd>/legal-outputs/<YYYY-MM-DD-HHmm>-research-<topic>/` へ出力：

| File | Audience | Sections |
|---|---|---|
| `plan.md` | 法務 + 業務（reproducibility checkpoint）| §問題 / §關鍵字 / §目標 site / §法源類型 plan / §Budget / §Disclaimer |
| `state.json` | 機器（grader + LLM loop）| rounds / fetches / sources[] / types_covered{} / early_stop / forced_stop / timestamps |
| `research-memo.md` | 法務 / GC / 内部稟議 | §問題 / §搜尋摘要 / §法源分析 / §結論 / §Citations / §Disclaimer（+ conditional ⚠️ block prepended）|
| `executive-summary.md` | 非法務（CEO / BD / 業務 / PM）| §問題 / §結論 (✅/⚠️/❌) / §依據 / §風險提示 / §Disclaimer（+ conditional §Escalation）|

Schema validation：4 file 全てが JSON Schema contract を `assets/plan-schema.json` / `assets/state-schema.json` / `assets/output-schema-memo.json` / `assets/output-schema-summary.json` に持ち、`scripts/grade_research.py` で消費される。

## Plan-first 半互動

Fetch budget が燃え始める前に、skill は `plan.md` を必ず emit し user に確認を求める。これは **mandatory、skip 不可** であり、v0.4.2 SP3b `classify-path` の Y/n precedent を踏襲している。

具体的には（`protocols/plan.md` 参照）：

1. LLM が `--query=...` を parse
2. LLM が `plan.md` を disk に emit + 全内容を stdout に print
3. LLM が 「Plan OK 嗎? (Y/n)」 と prompt（exact zh-TW 文字列、router log がこの surface form を match）
4. **Y** → `protocols/iterative-search.md` Step 1 が開始
5. **n**（または任意の非 Y）→ skill は `plan.md` を disk に残して exit；user は query を revise して再 invoke

Rationale：`plan.md` は 30-fetch budget を commit する前の cheap reproducibility checkpoint。User が token cost を制御する（auto-dispatch は意図的に未実装）。

## Agent loop cap

Loop は LLM-driven、state は `state.json` で deterministic に track される。Python は state 永続化のみ、loop logic 自体は LLM 側。

| Parameter | Value | Meaning |
|---|---|---|
| `max_rounds` | **5** | forced_stop までの最大 loop iteration 数 |
| `max_fetches` | **30** | forced_stop までの最大 WebFetch tool call 数 |
| `early_stop_min_sources` | **8** | early_stop dispatch の `len(sources)` 下限 |
| `early_stop_min_types` | **2** | early_stop の `len(types_covered)` 下限（4-type ∩ は new-domain query には strict すぎ、2-type が realistic）|

- **early_stop**：sources ≥ 8 + types_covered ≥ 2 を満たせば、cap に達する前に triangulate へ抜ける（成功 path）
- **forced_stop**：sources / types が早期収束基準に届かないまま cap に到達した場合、`state.forced_stop = true` を立てて triangulate へ break。**Forced stop は failure ではなく safety net** — memo は出るが ⚠️ `覆蓋未達 triangulation` block が §問題 の上に prepend される
- **grader**：forced_stop + ⚠️ marker は exit 2 (`PASS_WITH_NOTES`)、exit 1 (`FAIL`) ではない

Cap 値は `assets/triangulation-config.json` に centralize されており、v0.5.3 patch で tuning 余地を残してある。

## Cross-skill handoff（inbound only）

`legal-issue-spot` の 構成要件 涵攝 で **≥ 1 ⚠️**（信頼度不足要素）が出た場合、その `business.md §建議下一步` block に `/legal-research` の query string が具体的に列挙されている：

```markdown
## §建議下一步

⚠️ 以下構成要件信心不足，建議跑 research 釐清：

- §227 不完全給付的 carve-out 認定
  → `/legal-research --query="不完全給付 §227 carve-out 民國 110 年後判決趨勢"`
```

User がその command を copy して本 skill を起動する — **soft handoff、auto-dispatch なし**（Q8 lock：user が token budget を制御）。

逆方向（research → issue-spot）は **意図的に未実装**；router Q4 が誤 routing を catch する。`legal-research` は law-text query 専用、business fact pattern が来たら router 側で `legal-issue-spot` へ振り直される。

## §6.3 Disclaimer footer

全ての出力 file（`plan.md` / `research-memo.md` / `executive-summary.md` の 3 つ；`state.json` は機械可読のため除く）は §6.3 Disclaimer footer を必ず末尾に付ける（canonical text は `protocols/cite.md` が SoT、v0.5.0 `legal-issue-spot/protocols/risk-grade.md` の ownership pattern を踏襲）。Body は：AI tool 帰属 / 正式な法律意見ではない旨 / 現行台湾法 scope / litigation・契約締結・刑事責任・cross-border・high-stakes 判断は 律師 相談推奨。Grader は canonical sentinel substring を grep；footer 欠落 → exit 1（FAIL）。本 skill は 法律意見 を出力する — disclaimer は mandatory であり optional ではない。

## §6.4 Escalation Override

`state.json.forced_stop == true` または query domain が **刑事 / 訴訟 / 跨境 / 重大金額** に該当する場合、`executive-summary.md` は `## §Escalation` section を必ず含む（hard-wired、LLM judgement 不可）。`protocols/cite.md` Step 3 が fixed-format banner を emit し、LLM は softening / skip できない。Rationale は v0.4.x SoT §6.4 から継承：low confidence × 非法務 audience、または high-stakes domain では disclaimer 単独では不十分。

## 参考

- 完全 skill 説明：[`SKILL.md`](SKILL.md)
- Design spec：[`docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md`](../../../docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md) §6
- Plugin spec：[`legal-toolkit/PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) + [`legal-toolkit/TECH-SPEC.md`](../../TECH-SPEC.md)
- ROADMAP：[`legal-toolkit/ROADMAP.md`](../../ROADMAP.md)
