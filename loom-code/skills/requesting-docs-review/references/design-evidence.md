Source: `requesting-docs-review/SKILL.md` — maintainer-facing evidence extracted from the convergence contract (Directives 1-2), Step 3, Red Flags row 1, and the Aggregation rule — serves `requesting-docs-review`.

# Design evidence — author-facing, do NOT load at runtime

This file is author-facing: it exists for maintainers reviewing or redesigning this skill's convergence-contract decisions. Runtime agents executing `requesting-docs-review` do NOT load this file at runtime — the rule sentences these fragments qualify already stay inline in SKILL.md, byte-preserved; only citation tails, worked-example asides, and measurement archaeology live here (see the dated correction below for which hosts changed on 2026-08-07). SAFE-TIER extraction only (per `docs/loom/specs/2026-08-05-loom-skill-extraction-batch.md` §Partition C) — this file carries none of the operative rules themselves.

**Correction (2026-08-07, arc 4a):** of the 14 pointers below, 8 moved host — their rule sentences relocated from SKILL.md to `references/convergence-contract.md` on 2026-08-07 (arc 4a): "Directive 1 — beyond-cap authorization precedent", "Directive 1 — delta-size evidence (criterion paragraph)", "Directive 1 — 'why a cap' measurement", "Directive 2 — read-context / out-of-scope worked examples", "Directive 2 — session-boundary backlog citation", "Directive 2 — 'Why.' round-2 measurement", "Directive 2 — mint-scope-conflict aside", and "Directive 2 — round-1 sampling-weakness measurement". For those 8, read their "stays inline in SKILL.md" below as "stays inline in convergence-contract.md." The remaining 6 pointers — "What this skill does — intro audit citation", "Directive 1 (a) — pre-scoping historical note", "Directive 1 (b) — fix-round risk citation", "Process Step 3 — recorded-miss citation", "Red Flags row 1 — evidence tail", and "Aggregation rule — revisit-if clause" — are unchanged: their rule sentences still stay inline in SKILL.md as originally written. Per Directive 4, this is an appended correction — the 14 pointers themselves are left as originally written.

## What this skill does — intro audit citation

The rule stays inline in SKILL.md ("this skill therefore also carries what the code arm never needed: a convergence contract with a bounded cap — 2 rounds plus at most one mechanically-conditioned auto-delta round"). Its evidence tail: the recorded pathology this contract exists to end is a 9-round non-converging docs-review loop in which 6 of 9 rounds shipped a defect injected by the previous round's own remediation (`docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md`).

## Directive 1 (a) — pre-scoping historical note

The rule stays inline ("the default recommendation... That cost drop is what makes it the default."). Supporting narrative: before scoping existed, a third round meant re-reviewing everything, and "don't authorize lightly" was the right posture.

## Directive 1 — beyond-cap authorization precedent

The rule stays inline ("A fourth round runs ONLY on explicit user authorization — never silently."). Precedent it draws on: the critics' user-authorized breach precedent.

## Directive 1 (b) — fix-round risk citation

The rule stays inline ("a fix round is where defects get written"). Evidence: on the measured branch, round 1's fixes contained gating defects that only later review caught (`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`).

## Directive 1 — delta-size evidence (criterion paragraph)

The rule stays inline ("on the measured branch […] round 1's fixes were the larger delta and round 2's were the smaller delta" — the ellipsis marks the provenance parenthetical a later review fix inserted). Its sourcing and supporting evidence: the audit's own round labels (`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md` §Does delta-scoping converge faster) — a delta-scoped round verifying round 1's fixes re-found every gating defect an unbounded round also found, while a delta-scoped round verifying round 2's fixes found none.

## Directive 1 — "why a cap" measurement

The rule stays inline ("for an artifact carrying many small real defects, a clean round is not a reachable state"). Measurement: measured on one branch's twelve already-passed `.md` artifacts: four fresh arms, seven gating findings, zero overlap, each traced to its cited text and one settled by running the command that decides it; the audit's §Limits states it does not generalize a rate (`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`).

## Directive 2 — read-context / out-of-scope worked examples

The rule stays inline ("what is out of scope is a contradiction between two unchanged passages, neither touched by the delta"). Two instances, both named so the claim is checkable: a docs arm's `read-context` gap let a spec claiming stdin ship against a script with no stdin path, and this contract's own `read_context_findings` rule was contradicted by an unchanged §Aggregation rule that had no exclusion for it.

## Directive 2 — session-boundary backlog citation

The rule stays inline ("this round is `unbounded` — never a guessed range, and never a range built from the literal string `unresolved`"). Backlog citation: `docs/loom/backlog/2026-08-04-a-delta-scoped-round-cannot-resume-across-a-session.md`.

## Directive 2 — "Why." round-2 measurement

The rule stays inline ("Round 1 does the first; every later round does the second. Conflating them is the non-convergence."). Measurement: measured at round 2, two delta-scoped arms re-found BOTH gating findings that two unbounded arms found, and additionally listed 13 observations as out-of-scope (`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md` §Does delta-scoping converge faster).

## Directive 2 — mint-scope-conflict aside

The rule stays inline ("sampling the artifact's pre-existing defect pool (unbounded, inexhaustible)"). Worked example: a mint-scope conflict in this very skill survived two unbounded rounds before a third surfaced it.

## Directive 2 — round-1 sampling-weakness measurement

The rule stays inline ("It is the only pass positioned to sample the pre-existing pool, and it samples weakly."). Measurement: on the measured branch, 1 of its 14 findings was pre-existing-and-unrelated.

## Process Step 3 — recorded-miss citation

The rule stays inline (the whole-artifact scope instruction and the unchanged-claim question). The recorded miss this closes: a spec stating its shipped tool accepts input via `--claim` or stdin, on a branch whose script has no stdin path, reached merge unflagged — the docs arm that reviewed the spec was never given the script to open (`docs/loom/specs/2026-08-03-claim-copy-sweep.md:82`; `docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`).

## Red Flags row 1 — evidence tail (measurement duplication)

The rule stays inline ("The cap IS the design... what it still cannot do is certify the artifact clean."). This row's evidence duplicated Directive 1's "why a cap" measurement above; consolidated here rather than kept twice: two mechanisms, both measured — the source audit's remediation-injected defects (6 of 9 rounds), and a large pool of genuine small defects sampled disjointly by each pass. Do NOT read this row as "extra findings are manufactured": on one branch's twelve already-passed artifacts, four fresh arms returned seven gating findings with zero overlap, none manufactured (`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md` — read its §Limits before reusing the numbers).

## Aggregation rule — revisit-if clause

The rule stays inline ("these thresholds are inherited unexamined from `requesting-code-review`... no docs-specific evidence sets them"). Maintainer note: revisit if the docs arm's false-positive economics prove different.
