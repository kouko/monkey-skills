# legal-issue-spot

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

![version](https://img.shields.io/badge/version-0.1.0-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![phase](https://img.shields.io/badge/phase-3_SP3--a-orange)

> ⚠️ **Not legal advice.** Free open-source utility, not a law firm. Output is 法律意見 (legal opinion) for in-house 法務 internal reference only — escalate to a licensed lawyer for any matter with criminal exposure, regulator-facing risk, or material business impact. Every output ships with the §6.3 Mandatory Disclaimer footer (see below).

IRAC issue-spotting skill for Taiwan in-house 法務. Takes a business-language fact pattern (e.g. 「我們想做 X，能不能做？」) and produces an issue 矩陣 (issue matrix) + per-element 構成要件 涵攝 (statutory-element subsumption) + 反事實 (counterfactual) + 風險分級 (🔴/🟡/🟢) + escalation recommendation. Pure-LLM workflow; no external fetches; no `legal-playbook/profile.yml` dependency.

## When to use

- Business asks 「我們想做 X，能不能做？」 — legal pre-check before product launch / new feature / new vendor / new SOP
- Multi-statute fact pattern spanning 民法 / 勞基法 (Labor Standards Act) / 個資法 (Personal Data Protection Act) — one fact triggers multiple statutory issues at once
- Need structured 構成要件 涵攝 with risk grade + 律師 (lawyer) escalation recommendation, not just a binary yes/no answer

## When NOT to use

- **Literal law-text lookup** (「§227 條文是什麼？」) → use `legal-research` (Phase 3 SP3-b v0.5.2)
- **Contract review** (existing contract file or pasted clause text) → use `legal-contract-review`
- **Document drafting** (通知函 / 警示函 / 終止合約信) → use `legal-document-draft`
- **Incident response** (already-happened breach / received 主管機關 letter / counterparty already in breach) → use `legal-incident-response`

## Input format

- **Required at session**: free-text fact pattern (1-3 paragraphs of business-language description, e.g. 「我們想送一份員工生日禮物給客戶聯絡人，能不能做？」)
- **No structured schema** — `protocols/parse-facts.md` extracts 當事人 / 行為 / 時間 / 金額 / 標的 in Step 1
- **No `profile.yml` dependency** — analysis is fact-pattern-driven, not company-identity-driven (router Q4-fact bypasses the profile prerequisite check used by other v0.4.x skills)

## Output format

Per session, writes to `<cwd>/legal-outputs/<YYYY-MM-DD-HHmm>-issue-spot/`:

| File | Audience | Sections |
|---|---|---|
| `issues.md` | 法務 / GC / internal sign-off | §事實摘要 / §時間軸 / §Issue 矩陣 / §構成要件涵攝 / §反事實 / §風險分級 / §Disclaimer |
| `business.md` | non-法務 (CEO / BD / 業務 / PM) | §TL;DR / §可以做的部分 / §不能做的部分 / §注意點 / §風險分級 / §Disclaimer (+ §建議下一步 conditional + §Escalation conditional) |

Schema validation: both files have JSON Schema contracts in `assets/output-schema-issues.json` + `assets/output-schema-business.json`, consumed by `scripts/grade_issue_spot.py`.

## Cross-skill handoff

When the subsumption table contains **≥ 1 ⚠️** (any low-confidence element), `business.md` ends with a `§建議下一步` block listing concrete `/legal-research` queries:

```markdown
## 建議下一步

⚠️ 以下構成要件信心不足，建議跑 research 釐清：

- §227 不完全給付的 carve-out 認定
  → `/legal-research --query="不完全給付 §227 carve-out 民國 110 年後判決趨勢"`
```

This is a **soft handoff** — the user copies the command and invokes `/legal-research` themselves; no auto-dispatch (Q8 locked: user controls token budget). Reverse handoff (research → issue-spot) is intentionally NOT implemented; router Q4 catches misrouted queries.

## §6.3 Disclaimer footer

Every output file MUST end with the §6.3 Disclaimer footer (canonical text in `protocols/risk-grade.md`). Body covers: AI-tool attribution / not formal legal opinion / current TW in-force law scope / recommendation to consult 律師 for litigation, contract signing, criminal liability, cross-border, or high-stakes decisions. The grader greps for the canonical sentinel substring; missing footer → exit 1 (FAIL). This skill produces 法律意見 — disclaimer is mandatory, not optional.

When 風險分級 = 🔴 OR ≥ 2 ⚠️ in §構成要件涵攝, `business.md §Escalation` is also hard-wired (§6.4 Escalation Override) — the LLM does not get to soften or skip the 律師 recommendation.

## References

- Full skill instructions: [`SKILL.md`](SKILL.md)
- Design spec: [`docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md`](../../../docs/superpowers/specs/2026-05-15-legal-toolkit-phase3-irac-cluster-design.md) §5
- Plugin spec: [`legal-toolkit/PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) + [`legal-toolkit/TECH-SPEC.md`](../../TECH-SPEC.md)
- ROADMAP: [`legal-toolkit/ROADMAP.md`](../../ROADMAP.md)
