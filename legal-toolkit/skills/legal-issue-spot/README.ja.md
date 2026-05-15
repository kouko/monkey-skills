# legal-issue-spot

Read this in: [English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

![version](https://img.shields.io/badge/version-0.1.0-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![phase](https://img.shields.io/badge/phase-3_SP3--a-orange)

> ⚠️ **法的助言ではありません。** 本ツールは無料 open-source utility であり、法律事務所でも執業弁護士でもない。出力は 法律意見 (legal opinion) として in-house 法務 の内部参考のみ — 刑事 exposure / 主管機関 対応 risk / 重大経営判断が絡む案件は必ず執業弁護士にエスカレーションすること。全ての出力は §6.3 Mandatory Disclaimer footer 付き（後述）。
>
> **対象**：台湾 in-house 法務 向け（zh-TW jurisdiction 専用）。日本法務には適用不可。

台湾 in-house 法務 向け IRAC issue-spotting skill。business-language の fact pattern（例：「我們想做 X，能不能做？」）を受け取り、issue 矩陣 (issue matrix) + per-element 構成要件 涵攝 (subsumption) + 反事実 (counterfactual) + 風險分級 (🔴/🟡/🟢) + 律師 escalation 推奨を出力する。Pure-LLM workflow；外部 fetch なし；`legal-playbook/profile.yml` 依存なし。

## こんな時に使う

- 業務側から「我們想做 X，能不能做？」と相談を受けた — product launch / 新機能 / 新 vendor / 新 SOP の前段 legal pre-check
- 民法 / 勞基法（台湾労基法）/ 個資法（台湾個人情報保護法）を跨ぐ multi-statute fact pattern — 一つの事実が複数の statutory issue を同時に triger
- 構成要件 涵攝 を要素別に構造化した分析が必要 — risk grade + 律師 escalation 推奨付き、binary yes/no では不十分

## こんな時には使わない

- **法条文 lookup**（「§227 條文是什麼？」）→ `legal-research`（Phase 3 SP3-b v0.5.2）
- **契約 review**（既存契約 file または貼付け clause text）→ `legal-contract-review`
- **書面 drafting**（通知函 / 警示函 / 終止合約信）→ `legal-document-draft`
- **Incident response**（既発生の breach / 主管機関 来文受領済 / 取引相手側既違約）→ `legal-incident-response`

## Input format

- **Required at session**：fact pattern の自由記述（1-3 段落の business-language description、例：「我們想送一份員工生日禮物給客戶聯絡人，能不能做？」）
- **構造化 schema なし** — `protocols/parse-facts.md` が Step 1 で 當事人 / 行為 / 時間 / 金額 / 標的 を抽出
- **`profile.yml` 依存なし** — 分析は fact-pattern-driven であり company-identity-driven ではない（router Q4-fact が他 v0.4.x skill の profile prerequisite check を bypass）

## Output format

session 毎に `<cwd>/legal-outputs/<YYYY-MM-DD-HHmm>-issue-spot/` へ出力：

| File | Audience | Sections |
|---|---|---|
| `issues.md` | 法務 / GC / 内部稟議 | §事實摘要 / §時間軸 / §Issue 矩陣 / §構成要件涵攝 / §反事實 / §風險分級 / §Disclaimer |
| `business.md` | 非法務（CEO / BD / 業務 / PM）| §TL;DR / §可以做的部分 / §不能做的部分 / §注意點 / §風險分級 / §Disclaimer（+ §建議下一步 conditional + §Escalation conditional）|

Schema validation：両 file とも JSON Schema contract が `assets/output-schema-issues.json` + `assets/output-schema-business.json` にあり、`scripts/grade_issue_spot.py` で消費。

## Cross-skill handoff

subsumption 表に **≥ 1 ⚠️**（信頼度が低い要素）が現れた場合、`business.md` の末尾に `§建議下一步` block を出し、`/legal-research` 用の query string を具体的に列挙する：

```markdown
## 建議下一步

⚠️ 以下構成要件信心不足，建議跑 research 釐清：

- §227 不完全給付的 carve-out 認定
  → `/legal-research --query="不完全給付 §227 carve-out 民國 110 年後判決趨勢"`
```

これは **soft handoff** — user が command を copy して `/legal-research` を起動する；auto-dispatch なし（Q8 lock：user が token budget を制御）。逆方向（research → issue-spot）は意図的に未実装；router Q4 が誤 routing を catch。

## §6.3 Disclaimer footer

全ての出力 file は §6.3 Disclaimer footer を必ず末尾に付ける（canonical text は `protocols/risk-grade.md`）。Body は：AI tool 帰属 / 正式な法律意見ではない旨 / 現行台湾法 scope / litigation・契約締結・刑事責任・cross-border・high-stakes 判断は 律師 相談推奨。Grader は canonical sentinel substring を grep；footer 欠落 → exit 1（FAIL）。本 skill は 法律意見 を出力する — disclaimer は mandatory であり optional ではない。

風險分級 = 🔴 または §構成要件涵攝 に ≥ 2 ⚠️ がある場合、`business.md §Escalation` も hard-wired（§6.4 Escalation Override）— LLM は 律師 推奨を softening または skip できない。

## 参考

- 完全 skill 説明：[`SKILL.md`](SKILL.md)
- Design spec：[`docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md`](../../../docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md) §5
- Plugin spec：[`legal-toolkit/PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) + [`legal-toolkit/TECH-SPEC.md`](../../TECH-SPEC.md)
- ROADMAP：[`legal-toolkit/ROADMAP.md`](../../ROADMAP.md)
