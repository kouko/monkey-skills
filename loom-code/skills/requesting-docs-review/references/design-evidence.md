Source: `requesting-docs-review/SKILL.md` — maintainer-facing evidence extracted from the convergence contract (Directives 1-2), Step 3, Red Flags row 1, and the Aggregation rule — serves `requesting-docs-review`.

# Design evidence — author-facing, do NOT load at runtime

This file is author-facing: it exists for maintainers reviewing or redesigning this skill's convergence-contract decisions. Runtime agents executing `requesting-docs-review` do NOT load this file at runtime — the rule sentences these fragments qualify already stay inline in SKILL.md, byte-preserved; only citation tails, worked-example asides, and measurement archaeology live here (see the dated correction below for which hosts changed on 2026-08-07). SAFE-TIER extraction only (per `docs/loom/specs/2026-08-05-loom-skill-extraction-batch.md` §Partition C) — this file carries none of the operative rules themselves.

**Correction (2026-08-07, arc 4a):** of the 14 pointers below, 8 moved host — their rule sentences relocated from SKILL.md to `references/convergence-contract.md` on 2026-08-07 (arc 4a): "Directive 1 — beyond-cap authorization precedent", "Directive 1 — delta-size evidence (criterion paragraph)", "Directive 1 — 'why a cap' measurement", "Directive 2 — read-context / out-of-scope worked examples", "Directive 2 — session-boundary backlog citation", "Directive 2 — 'Why.' round-2 measurement", "Directive 2 — mint-scope-conflict aside", and "Directive 2 — round-1 sampling-weakness measurement". For those 8, read their "stays inline in SKILL.md" below as "stays inline in convergence-contract.md." The remaining 6 pointers — "What this skill does — intro audit citation", "Directive 1 (a) — pre-scoping historical note", "Directive 1 (b) — fix-round risk citation", "Process Step 3 — recorded-miss citation", "Red Flags row 1 — evidence tail", and "Aggregation rule — revisit-if clause" — are unchanged: their rule sentences still stay inline in SKILL.md as originally written. Per Directive 4, this is an appended correction — the 14 pointers themselves are left as originally written.

**Second correction (2026-08-11, 0.75.0 review-cost-reduction arc):** the bounded-cap contract itself — 2 rounds plus at most one mechanically-conditioned auto-delta round, with a fourth round gated on explicit user authorization — was the prior design; it was retired in 0.75.0 on the pool-arithmetic evidence (Directive 3's rationale below, which held under both designs) and replaced by the single-round + delta-confirmation contract now inline in SKILL.md's Process section (Directives 1-4) and in `references/convergence-contract.md`. Several of the 14 pointers below quote rule sentences that no longer appear verbatim in either file — each such pointer is now marked **RETIRED** (no live successor) or **RENUMBERED** (the rationale survived under a new Directive) in place of its old "stays inline" claim; the pinned evidence tail (measurement, citation, worked example) under each pointer is kept unedited for provenance. Two pointers — "Process Step 3 — recorded-miss citation" and "Aggregation rule — revisit-if clause" — needed no correction: both quotes still match SKILL.md's current text verbatim.

## What this skill does — intro audit citation

**RETIRED quote.** SKILL.md's current intro sentence reads: "this skill therefore also carries what the code arm never needed: a convergence contract — round 1 whole-artifact is the only full review; a gating verdict is fixed, then confirmed by the SAME reviewer via a delta-scoped check, never a fresh whole-corpus re-sample" (the bounded-cap wording quoted here previously — "2 rounds plus at most one mechanically-conditioned auto-delta round" — was retired 0.75.0). Its evidence tail is unchanged and still applies to the current contract: the recorded pathology this contract exists to end is a 9-round non-converging docs-review loop in which 6 of 9 rounds shipped a defect injected by the previous round's own remediation (`docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md`).

## Directive 1 (a) — pre-scoping historical note

**RETIRED — no live successor.** The current contract has no "third round" or "default recommendation" concept; this pointer described the bounded-cap contract only. Supporting narrative, kept for provenance: before scoping existed, a third round meant re-reviewing everything, and "don't authorize lightly" was the right posture.

## Directive 1 — beyond-cap authorization precedent

**RETIRED — no live successor.** The current contract has no round-count cap and no "fourth round" concept: `STILL_BLOCKING` now STOPs and hands the decision to the user directly, without a round-numbered ladder. Precedent it drew on, kept for provenance: the critics' user-authorized breach precedent.

## Directive 1 (b) — fix-round risk citation

**RENUMBERED.** The underlying risk survives into the current contract's Directive 2 (Delta confirmation): "the fix introduced a new gating problem" is one of the two `STILL_BLOCKING` triggers `convergence-contract.md` now names. The older phrasing quoted here previously ("a fix round is where defects get written") was retired with the bounded-cap contract. Evidence, kept for provenance: on the measured branch, round 1's fixes contained gating defects that only later review caught (`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`).

## Directive 1 — delta-size evidence (criterion paragraph)

**RETIRED quote, surviving rationale.** The specific round-1-vs-round-2 delta-size comparison quoted here previously was retired 0.75.0 with the bounded-cap contract — no round 2 exists anymore to compare against. What survived: this is the measurement that justified making the current contract's Directive 2 confirmation delta-scoped rather than a whole-corpus re-sample. Its sourcing and supporting evidence, kept for provenance: the audit's own round labels (`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md` §Does delta-scoping converge faster) — a delta-scoped round verifying round 1's fixes re-found every gating defect an unbounded round also found, while a delta-scoped round verifying round 2's fixes found none.

## Directive 1 — "why a cap" measurement

**RENUMBERED, not retired.** This rule now lives as the current contract's Directive 3 ("Terminal state is 'no gating findings,' never 'clean.'") and stays inline, verbatim, in both SKILL.md and `references/convergence-contract.md`: "for an artifact carrying many small real defects, a clean round is not a reachable state." Measurement, unchanged: measured on one branch's twelve already-passed `.md` artifacts: four fresh arms, seven gating findings, zero overlap, each traced to its cited text and one settled by running the command that decides it; the audit's §Limits states it does not generalize a rate (`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`).

## Directive 2 — read-context / out-of-scope worked examples

**RETIRED quote, simplified successor.** The specific "contradiction between two unchanged passages, neither touched by the delta" wording was retired 0.75.0 with the old round-scope model. `read-context` and `out_of_scope` both survive into the current contract under simplified semantics: `read-context` is still Step 3's non-`.md` verification material, and `out_of_scope` now populates only during Directive 2's delta confirmation (SKILL.md §Verdict structure). Two instances, kept for provenance, both named so the claim is checkable: a docs arm's `read-context` gap let a spec claiming stdin ship against a script with no stdin path, and this contract's own `read_context_findings` rule was contradicted by an unchanged §Aggregation rule that had no exclusion for it.

## Directive 2 — session-boundary backlog citation

**RENUMBERED.** The session-boundary problem this backlog entry raised is now handled by the current contract's Directive 4 ("Session death before confirmation → one fresh single round"); the specific quoted round-scope wording ("this round is `unbounded`…") was retired 0.75.0 along with the old round-scope model. Backlog citation, kept for provenance: `docs/loom/backlog/2026-08-04-a-delta-scoped-round-cannot-resume-across-a-session.md`.

## Directive 2 — "Why." round-2 measurement

**RETIRED — no live successor.** "Round 2" as a numbered concept was retired 0.75.0 — the current contract has round 1 plus one delta-confirmation cycle, not a numbered round 2 — so the quoted rule text no longer appears in SKILL.md or `convergence-contract.md`. Measurement, kept for provenance: measured at round 2, two delta-scoped arms re-found BOTH gating findings that two unbounded arms found, and additionally listed 13 observations as out-of-scope (`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md` §Does delta-scoping converge faster).

## Directive 2 — mint-scope-conflict aside

**RENUMBERED.** The "pre-existing defect pool" framing now supports the current contract's Directive 3 rationale (see the "why a cap" pointer above); the exact phrase quoted here previously was retired 0.75.0. Worked example, kept for provenance: a mint-scope conflict in this very skill survived two unbounded rounds before a third surfaced it — illustrating why "no gating findings" was chosen as the terminal state instead of an unreachable "clean."

## Directive 2 — round-1 sampling-weakness measurement

**RETIRED — no live successor.** This pointer compared round 1's sampling against a round 2 that no longer exists; retired 0.75.0 with the bounded-cap contract. Measurement, kept for provenance: on the measured branch, 1 of its 14 findings was pre-existing-and-unrelated.

## Process Step 3 — recorded-miss citation

The rule stays inline (the whole-artifact scope instruction and the unchanged-claim question) — unchanged by the 0.75.0 retirement. The recorded miss this closes: a spec stating its shipped tool accepts input via `--claim` or stdin, on a branch whose script has no stdin path, reached merge unflagged — the docs arm that reviewed the spec was never given the script to open (`docs/loom/specs/2026-08-03-claim-copy-sweep.md:82`; `docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`).

## Red Flags row 1 — evidence tail (measurement duplication)

**RENUMBERED/reworded.** SKILL.md's Red Flags row 1 now reads "The single-round-plus-confirmation contract IS the design" (the "cap" framing quoted here previously — "The cap IS the design" — was retired 0.75.0). This row's evidence duplicates the "why a cap" measurement above (now the current Directive 3, same content); consolidated here rather than kept twice: two mechanisms, both measured — the source audit's remediation-injected defects (6 of 9 rounds), and a large pool of genuine small defects sampled disjointly by each pass. Do NOT read this row as "extra findings are manufactured": on one branch's twelve already-passed artifacts, four fresh arms returned seven gating findings with zero overlap, none manufactured (`docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md` — read its §Limits before reusing the numbers).

## Aggregation rule — revisit-if clause

The rule stays inline ("these thresholds are inherited unexamined from `requesting-code-review`... no docs-specific evidence sets them") — unchanged by the 0.75.0 retirement; these thresholds were never part of the bounded-cap contract. Maintainer note: revisit if the docs arm's false-positive economics prove different.
