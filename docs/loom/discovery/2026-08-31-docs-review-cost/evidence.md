# Evidence — 2026-08-31-docs-review-cost

> Claims-to-evidence registry for this discovery. Evidence is separated from
> recommendations so later review changes can update the conclusion without
> rewriting the historical observations.

| Claim id | Claim | Evidence (link / quote) | Source | Source type | Date | Confidence |
|---|---|---|---|---|---|---|
| C1 | One docs-only branch ran nine review rounds without passing; six rounds found at least one defect introduced by the preceding remediation. | [`docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md`](../../audits/2026-07-28-doc-branch-review-loop-audit.md) §1, §4.2 | Monkey Skills audit (EN) | project-local | 2026-07-28 | high |
| C2 | On that branch, diff-scoped review missed a pre-existing incorrect instruction for six rounds; whole-artifact review found it in its first round. | [`docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md`](../../audits/2026-07-28-doc-branch-review-loop-audit.md) §2, §6b | Monkey Skills audit (EN) | project-local | 2026-07-28 | high |
| C3 | Four fresh reviewers over one previously passed corpus produced seven distinct gating findings with zero overlap. | [`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`](../../audits/2026-08-04-docs-review-convergence-experiment.md) §Result | Monkey Skills controlled measurement (EN) | project-local | 2026-08-04 | high |
| C4 | All seven findings in that experiment referred to text that existed and said what the finding claimed; only a subset received deeper instance verification. | [`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`](../../audits/2026-08-04-docs-review-convergence-experiment.md) §Were they real? | Monkey Skills controlled measurement (EN) | project-local | 2026-08-04 | high |
| C5 | In one 2x2 experiment, delta-scoped review passed on a small round-3 fix while the unbounded control found two pre-existing defects; the audit explicitly limits this to one branch and two arms per cell. | [`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`](../../audits/2026-08-04-docs-review-convergence-experiment.md) §Does delta-scoping converge faster? | Monkey Skills controlled measurement (EN) | project-local | 2026-08-04 | high |
| C6 | A historical sample classified 14 of 14 narrated yellow findings as load-bearing, but the sample was thin, non-random, narration-selected, and not independently reverified. | [`docs/loom/audits/2026-08-11-yellow-finding-load-bearing-sample.md`](../../audits/2026-08-11-yellow-finding-load-bearing-sample.md) §Verdict, §Limits | Monkey Skills audit (EN) | project-local | 2026-08-11 | high |
| C7 | The current docs-review contract permits one whole-artifact review and at most one post-fix confirmation before stopping. | [`loom-code/skills/requesting-docs-review/references/convergence-contract.md`](../../../../loom-code/skills/requesting-docs-review/references/convergence-contract.md) Directives 1–2 | Current project contract (EN) | project-local | 2026-08-31 | high |
| C8 | The core docs-review skill and reviewer paths have been touched by 27 commits since the standalone skill shipped; their current main contracts total 979 lines. | [`research/current-system-and-history.md`](research/current-system-and-history.md) §Maintenance surface | Git and `wc -l` observation (EN) | project-local | 2026-08-31 | high |
| C9 | The repository has no durable historical verdict store: a prior audit could reconstruct finding content only from PR-body prose because branch-local gate state does not survive squash merge. | [`docs/loom/audits/2026-08-11-yellow-finding-load-bearing-sample.md`](../../audits/2026-08-11-yellow-finding-load-bearing-sample.md) §Method item 2 | Monkey Skills audit (EN) | project-local | 2026-08-11 | high |
| C10 | Research over 12 LLM judges and more than 100,000 evaluation instances found position bias and material variation by judge and task. | [Judging the Judges](https://arxiv.org/abs/2406.07791) | Shi et al. (EN) | craft | 2024-06-12 | high |
| C11 | Independent research reports low inter-sample agreement and sensitivity to prompt differences in LLM evaluators. | [Large Language Models are Inconsistent and Biased Evaluators](https://arxiv.org/abs/2405.01724) | Stureborg et al. (EN) | craft | 2024-05-02 | high |
| C12 | Japanese-language research found likelihood bias can reduce LLM evaluator performance and that targeted few-shot examples can mitigate it. | [大規模言語モデルにおける評価バイアスの尤度に基づく緩和](https://www.jstage.jst.go.jp/article/jnlp/32/2/32_480/_article/-char/ja) | 言語処理学会論文誌 (JA) | craft | 2025 | high |
| C13 | Current engineering guidance recommends moving automatable checks earlier while retaining assurance throughout the lifecycle. | [Catch defects early](https://engineering.homeoffice.gov.uk/patterns/catch-defects-early/) and [Google Cloud's approach to change](https://docs.cloud.google.com/docs/cloud-approach-to-change) | UK Home Office and Google Cloud (EN) | craft | 2023–2026 | high |
| C14 | Japanese SI-document research describes ambiguity and reviewer dependence as obstacles to automation and evaluates LLM-based guideline-conformance checking as review support. | [SI文書レビュー支援のための生成AI駆動ガイドライン適合性チェックツール](https://www.ieice.org/publications/ken/summary.php?contribution_id=142157&expandable=3&ken_id=KBSE&lang=jp&presen_date=2026-03-20&schedule_id=8898&society_cd=ISS&year=2026) | IEICE / NEC (JA) | craft | 2026-03-20 | med |
| C15 | Existing technical-document production already belongs to `domain-teams:docs-team`, while strategy formation and proposal critique already have separate owners. | [`domain-teams/skills/docs-team/SKILL.md`](../../../../domain-teams/skills/docs-team/SKILL.md), [`systems-thinking-toolkit/skills/strategy-lever-and-cascade/SKILL.md`](../../../../systems-thinking-toolkit/skills/strategy-lever-and-cascade/SKILL.md), [`loom-workflow/skills/proposal-critique/SKILL.md`](../../../../loom-workflow/skills/proposal-critique/SKILL.md) | Current project contracts (EN) | project-local | 2026-08-31 | high |

## Source type legend

- **craft** — engineering or evaluation practice that is not specific to this repository.
- **project-local** — a directly observed fact of Monkey Skills.

## Notes

- EN and JA sources both support treating LLM review as a fallible aid rather
  than an exhaustive oracle. The Japanese search did not surface a comparable
  public study of repeated agentic Markdown-review loops; that gap limits direct
  external comparison with Loom's exact workflow.
- No claim here measures the current flow's token or elapsed-time cost. The
  repository does not retain the required denominator (C9).
