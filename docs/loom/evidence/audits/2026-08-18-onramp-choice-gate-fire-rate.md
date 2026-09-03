# On-ramp explicit-choice gate — fire-rate baseline

**Date**: 2026-08-18
**Subject**: `loom-code/scripts/check_onramp_choice.py` (as of `4260a489`) run
over every historical spec and plan→brief pair, as a pre-ship ceremony
baseline for BI-7 of `docs/loom/specs/2026-08-18-onramp-explicit-choice-gate.md`.
**Scope note, stated up front**: the commit-time gate this arc ships
(Task 8, `git-guard.py`) only fires on `git commit` for a **newly added**
`docs/loom/plans/*.md` (`--diff-filter=A`). None of the historical
files scanned below were added today — **none of them is, or will be,
blocked by the shipped gate**. This audit answers a different question:
if the checker's strict grammar were applied to the existing corpus,
how often would it call something unresolved — i.e. how loud would the
gate be once it starts firing on *new* plans going forward.

## Method

1. Ran `check_onramp_choice.py <file> --repo-root .` over every file
   under `docs/loom/specs/*.md` (207 files) directly — each spec file
   itself carries (or lacks) a `## Design-side on-ramp` / inline
   `Design-side on-ramp:` line, so the spec file *is* the "brief" the
   checker parses.
2. For every file under `docs/loom/plans/*.md` (220 files), located the
   `**Source brief**:` / `Source brief:` header line (bold and
   non-bold forms both occur in the corpus), extracted its path
   (handling three observed spellings: bare path, backtick-wrapped
   path, and `[text](path)` markdown-link form), resolved it against
   the repo root, and ran the same checker against that resolved path.
   A bash `for`-loop with `sed`'s `\s` class could not reliably strip
   the three header spellings (`\s` is not honored by macOS/BSD `sed`
   in extended mode), so this half of the run used a small Python
   script instead of a one-line shell loop — its source is reproduced
   under §Commands below, next to the specs' shell loop.
3. Bucketed by exit code (0/1/2) and, for exit 0, by the checker's own
   stdout wording (`resolved (not_fired)` vs `resolved (resolved)`) —
   the checker's `print()` at `check_onramp_choice.py` `main()` always
   includes the literal string `not_fired` or `resolved` from
   `Result.status`, so a substring match on stdout distinguishes them
   without re-implementing the grammar.
4. Read `docs/loom/DIRECTION.md` at run time for the
   `## On-ramp standing choices` section state (§DIRECTION.md state
   below).

## Counts — specs (`docs/loom/specs/*.md`, 207 files)

| Outcome | Count |
|---|---|
| exit 0, not-fired | 1 |
| exit 0, resolved (fired + explicit choice) | 0 |
| exit 2, unresolved | 206 |
| exit 1, brief file missing | 0 |
| **Total** | **207** |

The single exit-0/not-fired file is this arc's own brief
(`docs/loom/specs/2026-08-18-onramp-explicit-choice-gate.md`), whose
inline line — `> Design-side on-ramp: not fired — ...` — was authored
against the canonical grammar this arc is introducing. Every other
spec (206 of 207) is unresolved under the strict checker, including
the 87 specs that *do* carry some form of a `Design-side on-ramp`
line (`grep -l "Design-side on-ramp" docs/loom/specs/*.md | wc -l` →
87) — none of their existing wording (`N/A — ...`, `not offered — ...`,
`not applicable — ...`, etc.) matches the checker's literal
`^not fired — <reason>$` form, so all 87 fall into the same
`unresolved` bucket as specs with no line at all. This is expected and
by design (`section-gate-must-flag-entry-lookalikes-not-just-matches.md`
— lookalike wording never resolves the gate); it also means the
checker's `unresolved` count is not a proxy for "the on-ramp actually
fired" on this historical corpus — see §Disagreement with the brief's
pre-measurement below.

## Counts — plans → brief (`docs/loom/plans/*.md`, 220 files)

| Outcome | Count |
|---|---|
| no `Source brief` line at all | 8 |
| exit 0, not-fired | 1 |
| exit 0, resolved (fired + explicit choice) | 0 |
| exit 2, unresolved | 200 |
| exit 1, brief file missing | 11 |
| **Total** | **220** |

The exit-1 "brief file missing" plans are pre-existing path drift, not
a gate defect — mostly old `code-toolkit`/`spec-toolkit` paths from
before the loom- rename, two paths that never existed under
`docs/loom/plans/*.md` naming (`implicit`, see below), one path
pointing outside the repo (an Obsidian vault path), and one
change-folder-style spec path. Full list under §Blocked pairs.

The 8 "no `Source brief` line" plans are older plans predating the
`**Source brief**:` header convention (`plan-format.md:31`); the
checker was never run against them because there is no path to
resolve.

## Combined total

207 (specs) + 220 (plans) = **427** files scanned, matching the sum of
the two counts tables above.

## Plan→brief pairs that would be blocked if newly added today

**211 pairs** (200 exit-2 unresolved + 11 exit-1 brief-missing) would
be blocked by the checker if the corresponding plan were *newly added*
today and staged in `git commit` — restated: **none of them actually
is**, per the scope note at the top of this file. The full list (plan
path → resolved brief path → reason) is reproducible via the commands
in §Commands; a representative sample of the exit-1 (brief-missing)
subset — the more actionable half, since exit-2 is expected corpus-wide
per the grammar-mismatch finding above — is:

| Plan | Resolved brief path | Reason |
|---|---|---|
| `docs/loom/plans/2026-05-25-distill-sessions-v2.6.1-known-bugs-hotfix.md` | `implicit` | exit 1: not a real path (header reads literally "implicit") |
| `docs/loom/plans/2026-05-25-distill-sessions-v2.7.1-propose-target-filter.md` | `implicit` | exit 1: same |
| `docs/loom/plans/2026-06-02-dbt-wiki-nl2sql-skill-part1-A.md` | `docs/code-toolkit/specs/2026-06-02-dbt-wiki-nl2sql-skill.md` | exit 1: pre-rename `code-toolkit` path |
| `docs/loom/plans/2026-06-12-completeness-critic-diverse-panel.md` | `docs/spec-toolkit/specs/2026-06-12-completeness-critic-diverse-panel.md` | exit 1: pre-rename `spec-toolkit` path |
| `docs/loom/plans/2026-06-12-deep-deep-research-vs-angle-selector.md` | `~/kouko-obsidian-vault/projects/...` | exit 1: brief lives outside this repo |
| `docs/loom/plans/2026-07-16-operational-kpi-quarterly.md` | `docs/loom/2026-07-16-operational-kpi-quarterly/specs/operational-kpi-quarterly/spec.md` | exit 1: loom-spec change-folder path, not under `docs/loom/specs/` |
| `docs/loom/plans/2026-08-16-loom-design-merge-plan.md` | `docs/loom/research/2026-08-15-loom-plugin-consolidation.md` | exit 1: research doc, not a spec |

The remaining 200 exit-2 pairs are the historical specs/plans whose
on-ramp wording predates the canonical grammar (see previous section) —
listing all 200 individually adds no new information beyond "the
grammar is new and stricter than prior ad hoc wording"; they are all
reproducible via the loop in §Commands.

## Appendix — full blocked-pairs list (211)

<details>
<summary>211 pairs (plan path → resolved brief path → outcome: unresolved | brief_file_missing)</summary>

| Plan | Resolved brief path | Outcome |
|---|---|---|
| `docs/loom/plans/2026-05-18-inline-rule-sheet.md` | `docs/loom/specs/2026-05-18-inline-rule-sheet.md` | unresolved |
| `docs/loom/plans/2026-05-19-wiki-query-path2-frontmatter-script.md` | `docs/loom/specs/2026-05-19-wiki-query-path2-frontmatter-script.md` | unresolved |
| `docs/loom/plans/2026-05-20-salesforce-toolkit-v0.1.0-part-1.md` | `docs/loom/specs/2026-05-20-salesforce-toolkit-v0.1.0.md` | unresolved |
| `docs/loom/plans/2026-05-20-salesforce-toolkit-v0.1.0-part-2.md` | `docs/loom/specs/2026-05-20-salesforce-toolkit-v0.1.0.md` | unresolved |
| `docs/loom/plans/2026-05-20-salesforce-toolkit-v0.1.0-part-3.md` | `docs/loom/specs/2026-05-20-salesforce-toolkit-v0.1.0.md` | unresolved |
| `docs/loom/plans/2026-05-20-salesforce-toolkit-v0.1.0-part-4a.md` | `docs/loom/specs/2026-05-20-salesforce-toolkit-v0.1.0.md` | unresolved |
| `docs/loom/plans/2026-05-20-salesforce-toolkit-v0.1.0-part-4b.md` | `docs/loom/specs/2026-05-20-salesforce-toolkit-v0.1.0.md` | unresolved |
| `docs/loom/plans/2026-05-22-external-surface-grounding-discipline.md` | `../specs/2026-05-22-external-surface-grounding-discipline.md` | unresolved |
| `docs/loom/plans/2026-05-22-skill-log-mining-v0.1-part-1.md` | `docs/loom/specs/2026-05-22-skill-log-mining-v0.1-brief.md` | unresolved |
| `docs/loom/plans/2026-05-22-skill-log-mining-v0.1-part-2.md` | `docs/loom/specs/2026-05-22-skill-log-mining-v0.1-brief.md` | unresolved |
| `docs/loom/plans/2026-05-22-skill-log-mining-v0.1-part-3.md` | `docs/loom/specs/2026-05-22-skill-log-mining-v0.1-brief.md` | unresolved |
| `docs/loom/plans/2026-05-25-distill-sessions-v0.3-part-1.md` | `docs/loom/specs/2026-05-25-distill-sessions-v0.3-brief.md` | unresolved |
| `docs/loom/plans/2026-05-25-distill-sessions-v0.3-part-2.md` | `docs/loom/specs/2026-05-25-distill-sessions-v0.3-brief.md` | unresolved |
| `docs/loom/plans/2026-05-25-distill-sessions-v2.6.1-known-bugs-hotfix.md` | `implicit` | brief_file_missing |
| `docs/loom/plans/2026-05-25-distill-sessions-v2.7.1-propose-target-filter.md` | `implicit` | brief_file_missing |
| `docs/loom/plans/2026-05-26-distill-sessions-v0.4.md` | `docs/loom/specs/2026-05-26-distill-sessions-v0.4-brief.md` | unresolved |
| `docs/loom/plans/2026-05-26-recap-v0.1.md` | `docs/loom/specs/2026-05-26-recap-v0.1-brief.md` | unresolved |
| `docs/loom/plans/2026-05-27-distill-sessions-v0.4.1.md` | `docs/loom/specs/2026-05-27-distill-sessions-v0.4.1-brief.md` | unresolved |
| `docs/loom/plans/2026-05-27-distill-sessions-v0.5.md` | `docs/loom/specs/2026-05-27-distill-sessions-v0.5-brief.md` | unresolved |
| `docs/loom/plans/2026-05-28-handoff-v0.1.md` | `docs/loom/specs/2026-05-28-handoff-v0.1-brief.md` | unresolved |
| `docs/loom/plans/2026-05-30-plain-language-user-questions.md` | `docs/loom/specs/2026-05-30-plain-language-user-questions-brief.md` | unresolved |
| `docs/loom/plans/2026-05-31-asking-the-user-rollout-brainstorming-router.md` | `docs/loom/specs/2026-05-31-asking-the-user-rollout-brainstorming-router.md` | unresolved |
| `docs/loom/plans/2026-05-31-asking-the-user-three-gate-redesign.md` | `docs/loom/specs/2026-05-31-asking-the-user-three-gate-redesign.md` | unresolved |
| `docs/loom/plans/2026-05-31-git-memory-readability-guardrails.md` | `docs/loom/specs/2026-05-31-git-memory-readability-guardrails.md` | unresolved |
| `docs/loom/plans/2026-05-31-git-memory-squash-retrieval-caveat.md` | `docs/loom/specs/2026-05-31-git-memory-squash-retrieval-caveat.md` | unresolved |
| `docs/loom/plans/2026-05-31-writing-plans-parallelism-aware-ceiling.md` | `docs/loom/specs/2026-05-31-writing-plans-parallelism-aware-ceiling.md` | unresolved |
| `docs/loom/plans/2026-06-01-dbt-wiki-knowledge-centric.md` | `docs/loom/specs/2026-06-01-dbt-wiki-knowledge-centric.md` | unresolved |
| `docs/loom/plans/2026-06-02-dbt-wiki-metric-column-cards.md` | `docs/loom/specs/2026-06-02-dbt-wiki-metric-column-cards.md` | unresolved |
| `docs/loom/plans/2026-06-02-dbt-wiki-nl2sql-skill-part1-A.md` | `docs/code-toolkit/specs/2026-06-02-dbt-wiki-nl2sql-skill.md` | brief_file_missing |
| `docs/loom/plans/2026-06-02-dbt-wiki-to-sql-semantic-guardrails.md` | `docs/code-toolkit/specs/2026-06-02-dbt-wiki-to-sql-semantic-guardrails.md` | brief_file_missing |
| `docs/loom/plans/2026-06-02-deep-research-portable-python.md` | `docs/loom/specs/2026-06-02-deep-research-portable-python.md` | unresolved |
| `docs/loom/plans/2026-06-02-deep-research-skill.md` | `docs/loom/specs/2026-06-02-deep-research-skill.md` | unresolved |
| `docs/loom/plans/2026-06-03-daily-brief.md` | `docs/loom/specs/2026-06-03-daily-brief-v0.1-brief.md` | unresolved |
| `docs/loom/plans/2026-06-03-dbt-wiki-knowledge-skill-pack.md` | `docs/code-toolkit/specs/2026-06-03-dbt-wiki-knowledge-skill-pack.md` | brief_file_missing |
| `docs/loom/plans/2026-06-03-dogfood-skill-testing.md` | `docs/loom/specs/2026-06-03-dogfood-skill-testing.md` | unresolved |
| `docs/loom/plans/2026-06-03-research-toolkit-cite-check.md` | `docs/loom/specs/2026-06-03-research-toolkit-cite-check.md` | unresolved |
| `docs/loom/plans/2026-06-03-research-toolkit-deep-read.md` | `docs/loom/specs/2026-06-03-research-toolkit-deep-read.md` | unresolved |
| `docs/loom/plans/2026-06-03-research-toolkit-fact-check.md` | `docs/loom/specs/2026-06-03-research-toolkit-fact-check.md` | unresolved |
| `docs/loom/plans/2026-06-04-obsidian-dangling-wikilink-prevention.md` | `docs/loom/specs/2026-06-04-obsidian-dangling-wikilink-prevention.md` | unresolved |
| `docs/loom/plans/2026-06-11-brainstorming-greenfield-ui-coverage-nudge.md` | `docs/loom/specs/2026-06-11-brainstorming-greenfield-ui-coverage-nudge.md` | unresolved |
| `docs/loom/plans/2026-06-11-spec-toolkit-mvp-critic-first.md` | `docs/loom/specs/2026-06-11-spec-toolkit-mvp-critic-first.md` | unresolved |
| `docs/loom/plans/2026-06-12-completeness-critic-diverse-panel.md` | `docs/spec-toolkit/specs/2026-06-12-completeness-critic-diverse-panel.md` | brief_file_missing |
| `docs/loom/plans/2026-06-12-completeness-critic-v0.2.1-panel-hardening.md` | `docs/spec-toolkit/specs/2026-06-12-completeness-critic-v0.2.1-panel-hardening.md` | brief_file_missing |
| `docs/loom/plans/2026-06-12-deep-deep-research-vs-angle-selector.md` | `~/kouko-obsidian-vault/projects/2026-06-12 deep-research 角度選擇器（Verbalized Sampling）實作 brief.md` | brief_file_missing |
| `docs/loom/plans/2026-06-12-spec-expansion-v0.2-l2-l3.md` | `docs/loom/specs/2026-06-12-spec-expansion-v0.2-l2-l3.md` | unresolved |
| `docs/loom/plans/2026-06-12-spec-expansion-v0.2.1-dogfood-hardening.md` | `docs/loom/specs/2026-06-12-spec-expansion-v0.2.1-dogfood-hardening.md` | unresolved |
| `docs/loom/plans/2026-06-13-deep-deep-research-framework-audit-meta-mode.md` | `docs/loom/specs/2026-06-13-deep-deep-research-framework-audit-meta-mode.md` | unresolved |
| `docs/loom/plans/2026-06-13-framework-audit-backfill-check.md` | `docs/loom/specs/2026-06-13-framework-audit-backfill-check.md` | unresolved |
| `docs/loom/plans/2026-06-13-framework-audit-blindspots-canon-rewrite.md` | `docs/loom/specs/2026-06-13-framework-audit-blindspots-canon-rewrite.md` | unresolved |
| `docs/loom/plans/2026-06-13-framework-audit-library-english-only.md` | `docs/loom/specs/2026-06-13-framework-audit-library-english-only.md` | unresolved |
| `docs/loom/plans/2026-06-13-purpose-fit-relevance-floor-lever.md` | `docs/loom/specs/2026-06-13-purpose-fit-relevance-floor-lever.md` | unresolved |
| `docs/loom/plans/2026-06-14-codex-compat-completion.md` | `docs/loom/specs/2026-06-14-codex-compat-completion.md` | unresolved |
| `docs/loom/plans/2026-06-14-interface-design-toolkit-mvp.md` | `docs/loom/specs/2026-06-14-interface-design-toolkit-mvp.md` | unresolved |
| `docs/loom/plans/2026-06-14-product-principles-toolkit-mvp.md` | `docs/loom/specs/2026-06-14-product-principles-toolkit-mvp.md` | unresolved |
| `docs/loom/plans/2026-06-15-synthesis-calibration-prepend.md` | `docs/loom/specs/2026-06-15-synthesis-calibration-prepend.md` | unresolved |
| `docs/loom/plans/2026-06-16-design-spec-seam.md` | `docs/loom/specs/2026-06-16-design-spec-seam.md` | unresolved |
| `docs/loom/plans/2026-06-16-progress-ledger.md` | `docs/loom/specs/2026-06-16-progress-ledger.md` | unresolved |
| `docs/loom/plans/2026-06-17-ascii-graph-skill.md` | `docs/loom/specs/2026-06-17-ascii-graph-skill.md` | unresolved |
| `docs/loom/plans/2026-06-17-ascii-graph-v2a-layered-arch.md` | `docs/loom/specs/2026-06-17-ascii-graph-v2a-layered-arch.md` | unresolved |
| `docs/loom/plans/2026-06-17-continuous-mode-auto-advance.md` | `docs/loom/specs/2026-06-17-continuous-mode-auto-advance.md` | unresolved |
| `docs/loom/plans/2026-06-17-design-critic.md` | `docs/loom/specs/2026-06-17-design-critic.md` | unresolved |
| `docs/loom/plans/2026-06-17-principles-conformance-lens.md` | `docs/loom/specs/2026-06-17-principles-conformance-lens.md` | unresolved |
| `docs/loom/plans/2026-06-18-ascii-graph-v2c-sequence.md` | `docs/loom/specs/2026-06-18-ascii-graph-v2c-sequence.md` | unresolved |
| `docs/loom/plans/2026-06-19-ascii-graph-multiline-labels.md` | `docs/loom/specs/2026-06-19-ascii-graph-multiline-labels.md` | unresolved |
| `docs/loom/plans/2026-06-20-skill-dev-toolkit-extraction.md` | `docs/code-toolkit/specs/2026-06-20-skill-dev-toolkit-extraction.md` | brief_file_missing |
| `docs/loom/plans/2026-06-21-spec-to-code-wiring.md` | `docs/loom/specs/2026-06-21-spec-to-code-wiring.md` | unresolved |
| `docs/loom/plans/2026-06-22-deliberate-simplification-ledger.md` | `docs/loom/specs/2026-06-22-deliberate-simplification-ledger.md` | unresolved |
| `docs/loom/plans/2026-06-22-git-memory-merge-gate-and-verified-survival.md` | `docs/loom/specs/2026-06-22-git-memory-merge-gate-and-verified-survival.md` | unresolved |
| `docs/loom/plans/2026-06-22-loom-code-mining-fixes.md` | `docs/loom/specs/2026-06-22-loom-code-mining-fixes.md` | unresolved |
| `docs/loom/plans/2026-06-23-git-memory-f4-close-out-verify-gate.md` | `docs/loom/specs/2026-06-23-git-memory-f4-close-out-verify-gate.md` | unresolved |
| `docs/loom/plans/2026-06-23-loom-living-spec-index-slice1.md` | `docs/loom/specs/2026-06-22-loom-living-spec-index-design-brief.md` | unresolved |
| `docs/loom/plans/2026-06-23-loom-living-spec-slice2-gitref-warn.md` | `docs/loom/specs/2026-06-23-loom-living-spec-slice2-gitref-warn.md` | unresolved |
| `docs/loom/plans/2026-06-23-loom-living-spec-slice3-intent-layer.md` | `docs/loom/specs/2026-06-23-loom-living-spec-slice3-intent-layer.md` | unresolved |
| `docs/loom/plans/2026-06-24-dbt-wiki-materiality-triage.md` | `docs/loom/specs/2026-06-24-dbt-wiki-materiality-triage.md` | unresolved |
| `docs/loom/plans/2026-06-24-loom-living-spec-capstone-g-pr1.md` | `docs/loom/specs/2026-06-24-loom-living-spec-capstone-g.md` | unresolved |
| `docs/loom/plans/2026-06-24-loom-living-spec-capstone-g-pr2.md` | `docs/loom/specs/2026-06-24-loom-living-spec-capstone-g-pr2.md` | unresolved |
| `docs/loom/plans/2026-06-24-loom-living-spec-slice4-closed-loop.md` | `docs/loom/specs/2026-06-24-loom-living-spec-slice4-closed-loop.md` | unresolved |
| `docs/loom/plans/2026-06-30-codex-compat-all-plugins.md` | `docs/loom/specs/2026-06-30-codex-compat-all-plugins.md` | unresolved |
| `docs/loom/plans/2026-07-03-loom-pipeline-conductor.md` | `docs/loom/specs/2026-07-03-loom-pipeline-conductor.md` | unresolved |
| `docs/loom/plans/2026-07-03-loom-pipeline-v1-1-batch-mode.md` | `docs/loom/specs/2026-07-03-loom-pipeline-v1-1-batch-mode.md` | unresolved |
| `docs/loom/plans/2026-07-03-principles-three-jurisdiction-sections.md` | `docs/loom/specs/2026-07-03-principles-three-jurisdiction-sections.md` | unresolved |
| `docs/loom/plans/2026-07-04-loom-family-connective-tissue.md` | `docs/loom/specs/2026-07-04-loom-family-connective-tissue.md` | unresolved |
| `docs/loom/plans/2026-07-06-loom-memory-skill.md` | `docs/loom/specs/2026-07-06-loom-memory-skill.md` | unresolved |
| `docs/loom/plans/2026-07-06-loom-memory-store.md` | `docs/loom/specs/2026-07-06-loom-memory-store.md` | unresolved |
| `docs/loom/plans/2026-07-06-research-toolkit-triggering.md` | `docs/loom/specs/2026-07-06-research-toolkit-triggering.md` | unresolved |
| `docs/loom/plans/2026-07-07-deep-deep-research-file-carrier.md` | `docs/loom/specs/2026-07-07-deep-deep-research-file-carrier.md` | unresolved |
| `docs/loom/plans/2026-07-07-loom-user-communication-overhaul-tasks.md` | `docs/loom/plans/2026-07-07-loom-user-communication-overhaul.md` | unresolved |
| `docs/loom/plans/2026-07-08-daily-news-digest-multiview-synthesis.md` | `docs/loom/specs/2026-07-08-daily-news-digest-multiview-synthesis.md` | unresolved |
| `docs/loom/plans/2026-07-08-deep-deep-research-bakeoff2-bugfixes.md` | `docs/loom/specs/2026-07-08-deep-deep-research-bakeoff2-bugfixes.md` | unresolved |
| `docs/loom/plans/2026-07-08-deep-deep-research-fact-opinion-classification.md` | `docs/loom/specs/2026-07-08-deep-deep-research-fact-opinion-classification.md` | unresolved |
| `docs/loom/plans/2026-07-08-sdd-mechanical-review-weight-tasks.md` | `docs/loom/specs/2026-07-08-sdd-mechanical-review-weight.md` | unresolved |
| `docs/loom/plans/2026-07-08-w1-l2-e2e-harness.md` | `docs/loom/specs/2026-07-08-w1-l2-e2e-harness.md` | unresolved |
| `docs/loom/plans/2026-07-10-ascii-graph-trigger-fix.md` | `docs/loom/specs/2026-07-10-ascii-graph-trigger-fix.md` | unresolved |
| `docs/loom/plans/2026-07-10-designer-pm-loop-implementation.md` | `docs/loom/specs/2026-07-10-designer-pm-loop-implementation.md` | unresolved |
| `docs/loom/plans/2026-07-10-g1-sparse-comment-fixture.md` | `docs/loom/specs/2026-07-10-g1-sparse-comment-fixture.md` | unresolved |
| `docs/loom/plans/2026-07-10-loom-discovery-station.md` | `docs/loom/specs/2026-07-09-loom-discovery-station.md` | unresolved |
| `docs/loom/plans/2026-07-10-principles-replay-loop.md` | `docs/loom/specs/2026-07-10-principles-replay-loop.md` | unresolved |
| `docs/loom/plans/2026-07-11-escalation-interface-contracts.md` | `docs/loom/specs/2026-07-11-escalation-interface-contracts.md` | unresolved |
| `docs/loom/plans/2026-07-11-investing-dogfood-fixes.md` | `docs/skill-dogfood/2026-07-11-data-markets/report.md` | unresolved |
| `docs/loom/plans/2026-07-11-investing-obsidian-memory-layer.md` | `docs/loom/specs/2026-07-11-investing-obsidian-memory-layer.md` | unresolved |
| `docs/loom/plans/2026-07-11-investing-toolkit-data-consolidation.md` | `docs/loom/specs/2026-07-11-investing-toolkit-data-consolidation.md` | unresolved |
| `docs/loom/plans/2026-07-11-principles-replay-l3-loop.md` | `docs/loom/specs/2026-07-11-principles-replay-l3-loop.md` | unresolved |
| `docs/loom/plans/2026-07-11-replay-oracle-calibration.md` | `docs/loom/specs/2026-07-11-replay-oracle-calibration.md` | unresolved |
| `docs/loom/plans/2026-07-12-principles-mechanical-seed-gate.md` | `docs/loom/specs/2026-07-12-principles-mechanical-seed-gate.md` | unresolved |
| `docs/loom/plans/2026-07-12-us-sec-narrative-all-items.md` | `docs/loom/2026-07-12-us-sec-primary-source-layer/specs/narrative/spec.md` | unresolved |
| `docs/loom/plans/2026-07-12-us-sec-narrative.md` | `docs/loom/2026-07-12-us-sec-primary-source-layer/specs/narrative/spec.md` | unresolved |
| `docs/loom/plans/2026-07-12-visual-anchor-realignment-tone-and-manner.md` | `docs/loom/specs/2026-07-12-visual-anchor-realignment-tone-and-manner.md` | unresolved |
| `docs/loom/plans/2026-07-12-visual-style-movement-anchor-and-quality-separation.md` | `docs/loom/specs/2026-07-12-visual-style-movement-anchor-and-quality-separation.md` | unresolved |
| `docs/loom/plans/2026-07-13-axis-b-relocation-and-tone-manner-seam.md` | `docs/loom/specs/2026-07-13-axis-b-relocation-and-tone-manner-seam.md` | unresolved |
| `docs/loom/plans/2026-07-13-pocock-compression-philosophy-port.md` | `docs/loom/specs/2026-07-13-pocock-compression-philosophy-port.md` | unresolved |
| `docs/loom/plans/2026-07-13-us-sec-financial-table-xval.md` | `docs/loom/specs/2026-07-13-us-sec-financial-table-xval.md` | unresolved |
| `docs/loom/plans/2026-07-13-us-sec-narrative-memo-wiring.md` | `docs/loom/specs/2026-07-13-us-sec-narrative-memo-wiring.md` | unresolved |
| `docs/loom/plans/2026-07-13-us-sec-xval-memo-wiring.md` | `docs/loom/specs/2026-07-13-us-sec-xval-memo-wiring.md` | unresolved |
| `docs/loom/plans/2026-07-14-afk-research-lane.md` | `docs/loom/specs/2026-07-14-afk-research-lane.md` | unresolved |
| `docs/loom/plans/2026-07-14-description-token-economy.md` | `docs/loom/specs/2026-07-14-description-token-economy.md` | unresolved |
| `docs/loom/plans/2026-07-14-mid-task-ask-layered-defense.md` | `docs/loom/specs/2026-07-13-mid-task-ask-layered-defense.md` | unresolved |
| `docs/loom/plans/2026-07-14-operational-kpi-bitemporal-store.md` | `docs/loom/specs/2026-07-14-operational-kpi-bitemporal-store.md` | unresolved |
| `docs/loom/plans/2026-07-14-operational-kpi-break-events.md` | `docs/loom/specs/2026-07-14-operational-kpi-break-events.md` | unresolved |
| `docs/loom/plans/2026-07-14-operational-kpi-cell-parser.md` | `docs/loom/specs/2026-07-14-operational-kpi-cell-parser.md` | unresolved |
| `docs/loom/plans/2026-07-14-operational-kpi-companyfacts-pilot.md` | `docs/loom/specs/2026-07-14-operational-kpi-companyfacts-pilot.md` | unresolved |
| `docs/loom/plans/2026-07-14-operational-kpi-dual-series.md` | `docs/loom/specs/2026-07-14-operational-kpi-dual-series.md` | unresolved |
| `docs/loom/plans/2026-07-14-operational-kpi-memo-feed.md` | `docs/loom/specs/2026-07-14-operational-kpi-memo-feed.md` | unresolved |
| `docs/loom/plans/2026-07-14-operational-kpi-reliability-gate.md` | `docs/loom/specs/2026-07-14-operational-kpi-reliability-gate.md` | unresolved |
| `docs/loom/plans/2026-07-14-operational-kpi-review-queue.md` | `docs/loom/specs/2026-07-14-operational-kpi-review-queue.md` | unresolved |
| `docs/loom/plans/2026-07-14-operational-kpi-schema-lifecycle.md` | `docs/loom/specs/2026-07-14-operational-kpi-schema-lifecycle.md` | unresolved |
| `docs/loom/plans/2026-07-14-operational-kpi-value-validation.md` | `docs/loom/specs/2026-07-14-operational-kpi-value-validation.md` | unresolved |
| `docs/loom/plans/2026-07-15-multi-filing-historical-fetch.md` | `docs/loom/specs/2026-07-15-multi-filing-historical-fetch.md` | unresolved |
| `docs/loom/plans/2026-07-15-operational-kpi-full-dimensional-signature.md` | `docs/loom/specs/2026-07-15-operational-kpi-full-dimensional-signature.md` | unresolved |
| `docs/loom/plans/2026-07-16-operational-kpi-quarterly.md` | `docs/loom/2026-07-16-operational-kpi-quarterly/specs/operational-kpi-quarterly/spec.md` | brief_file_missing |
| `docs/loom/plans/2026-07-17-loom-memory-hardening-o4-o2-o3-o5-o6.md` | `docs/loom/specs/2026-07-17-loom-memory-hardening-o4-o2-o3-o5-o6.md` | unresolved |
| `docs/loom/plans/2026-07-17-token-budget-two-tier-calibration.md` | `docs/loom/specs/2026-07-15-token-budget-two-tier-calibration.md` | unresolved |
| `docs/loom/plans/2026-07-18-52-53-week-filer-support.md` | `docs/loom/specs/2026-07-18-52-53-week-filer-support.md` | unresolved |
| `docs/loom/plans/2026-07-18-loop-convergence-fixes.md` | `docs/loom/specs/2026-07-18-loop-convergence-tier1-fixes.md` | unresolved |
| `docs/loom/plans/2026-07-18-memo-quarterly-kpi-wiring.md` | `docs/loom/specs/2026-07-18-memo-quarterly-kpi-wiring.md` | unresolved |
| `docs/loom/plans/2026-07-19-8k-earnings-kpi-intake.md` | `docs/loom/specs/2026-07-19-8k-earnings-kpi-intake.md` | unresolved |
| `docs/loom/plans/2026-07-19-closeout-privacy-gate.md` | `docs/loom/specs/2026-07-19-closeout-privacy-gate.md` | unresolved |
| `docs/loom/plans/2026-07-19-jnj-restatement-axis-signature.md` | `docs/loom/specs/2026-07-19-jnj-restatement-axis-signature.md` | unresolved |
| `docs/loom/plans/2026-07-19-tw-ixbrl-ingestion.md` | `docs/loom/specs/2026-07-19-tw-ixbrl-ingestion.md` | unresolved |
| `docs/loom/plans/2026-07-20-loom-gate-hardening-mechanical.md` | `docs/loom/specs/2026-07-20-loom-gate-hardening-mechanical.md` | unresolved |
| `docs/loom/plans/2026-07-22-kpi-observation-history.md` | `docs/loom/specs/2026-07-20-kpi-observation-history.md` | unresolved |
| `docs/loom/plans/2026-07-22-loom-memory-integrity.md` | `docs/loom/specs/2026-07-22-loom-memory-integrity.md` | unresolved |
| `docs/loom/plans/2026-07-22-tw-ixbrl-fh-ingestion.md` | `docs/loom/specs/2026-07-22-tw-ixbrl-fh-ingestion.md` | unresolved |
| `docs/loom/plans/2026-07-23-goal-loop-harness.md` | `docs/loom/specs/2026-07-23-goal-loop-harness.md` | unresolved |
| `docs/loom/plans/2026-07-23-kpi-tearsheet.md` | `docs/loom/specs/2026-07-23-kpi-tearsheet.md` | unresolved |
| `docs/loom/plans/2026-07-23-wiki-update-loop.md` | `docs/loom/specs/2026-07-23-wiki-update-maintenance-loop.md` | unresolved |
| `docs/loom/plans/2026-07-24-dbt-wiki-skill-surface-simplification.md` | `docs/loom/specs/2026-07-24-dbt-wiki-skill-surface-simplification.md` | unresolved |
| `docs/loom/plans/2026-07-24-kpi-xbrl-store-producer.md` | `docs/loom/specs/2026-07-24-kpi-xbrl-store-producer.md` | unresolved |
| `docs/loom/plans/2026-07-24-tw-financial-ixbrl-followups.md` | `docs/loom/specs/2026-07-24-tw-financial-ixbrl-followups.md` | unresolved |
| `docs/loom/plans/2026-07-24-tw-ixbrl-endorsement.md` | `docs/loom/specs/2026-07-24-tw-ixbrl-endorsement.md` | unresolved |
| `docs/loom/plans/2026-07-25-bba-proactive-trigger-hardening.md` | `docs/loom/specs/2026-07-25-bba-proactive-trigger-hardening.md` | unresolved |
| `docs/loom/plans/2026-07-25-company-total-revenue.md` | `docs/loom/specs/2026-07-25-company-total-revenue.md` | unresolved |
| `docs/loom/plans/2026-07-25-kpi-id-injective-identity.md` | `docs/loom/specs/2026-07-25-kpi-id-injective-identity.md` | unresolved |
| `docs/loom/plans/2026-07-25-tw-kpi-store-producer.md` | `docs/loom/specs/2026-07-25-tw-kpi-store-producer.md` | unresolved |
| `docs/loom/plans/2026-07-26-as-filed-statement-reconstruction.md` | `docs/loom/specs/2026-07-26-as-filed-statement-reconstruction.md` | unresolved |
| `docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md` | `docs/loom/specs/2026-07-26-us-as-reported-statement-lane.md` | unresolved |
| `docs/loom/plans/2026-07-27-plan-stage-fact-grounding.md` | `docs/loom/specs/2026-07-27-plan-stage-fact-grounding.md` | unresolved |
| `docs/loom/plans/2026-07-28-docs-citation-check-and-review-mode.md` | `docs/loom/specs/2026-07-28-docs-citation-check-and-review-mode.md` | unresolved |
| `docs/loom/plans/2026-07-28-phase2-loop-execution-only.md` | `docs/loom/specs/2026-07-28-phase2-loop-execution-only.md` | unresolved |
| `docs/loom/plans/2026-07-28-us-quarterly-statement-series.md` | `docs/loom/specs/2026-07-28-us-quarterly-statement-series.md` | unresolved |
| `docs/loom/plans/2026-07-30-copywriting-convergence-modernization.md` | `docs/loom/specs/2026-07-30-copywriting-convergence-modernization.md` | unresolved |
| `docs/loom/plans/2026-07-30-docs-review-blocking-class.md` | `docs/loom/specs/2026-07-30-docs-review-blocking-class.md` | unresolved |
| `docs/loom/plans/2026-07-30-requesting-docs-review-standalone-skill.md` | `docs/loom/specs/2026-07-30-requesting-docs-review-standalone-skill.md` | unresolved |
| `docs/loom/plans/2026-07-30-review-round-ledger-and-bad-fix-recheck.md` | `docs/loom/specs/2026-07-29-review-round-ledger-and-bad-fix-recheck.md` | unresolved |
| `docs/loom/plans/2026-07-31-reuse-adequacy-declaration-hardening.md` | `docs/loom/specs/2026-07-31-reuse-adequacy-declaration-hardening.md` | unresolved |
| `docs/loom/plans/2026-08-01-backlog-one-entry-per-file.md` | `docs/loom/specs/2026-08-01-backlog-one-entry-per-file.md` | unresolved |
| `docs/loom/plans/2026-08-01-declared-vs-actual-files-touched-check.md` | `docs/loom/specs/2026-08-01-declared-vs-actual-files-touched-check.md` | unresolved |
| `docs/loom/plans/2026-08-02-finding-origin-attribution.md` | `docs/loom/specs/2026-08-02-finding-origin-attribution.md` | unresolved |
| `docs/loom/plans/2026-08-03-review-scope-resolver.md` | `docs/loom/specs/2026-08-03-review-scope-resolver.md` | unresolved |
| `docs/loom/plans/2026-08-04-docs-review-0490-defect-fixes.md` | `docs/loom/specs/2026-08-04-docs-review-0490-defect-fixes.md` | unresolved |
| `docs/loom/plans/2026-08-04-loom-mechanism-defect-fixes.md` | `docs/loom/specs/2026-08-04-loom-mechanism-defect-fixes.md` | unresolved |
| `docs/loom/plans/2026-08-04-mechanical-lane-suite-gate.md` | `docs/loom/specs/2026-08-04-mechanical-lane-suite-gate.md` | unresolved |
| `docs/loom/plans/2026-08-05-loom-skill-extraction-batch.md` | `docs/loom/specs/2026-08-05-loom-skill-extraction-batch.md` | unresolved |
| `docs/loom/plans/2026-08-05-orchestrator-tree-detach-hardening.md` | `docs/loom/specs/2026-08-05-orchestrator-tree-detach-hardening.md` | unresolved |
| `docs/loom/plans/2026-08-05-rcr-skill-extraction-pilot.md` | `docs/loom/specs/2026-08-05-rcr-skill-extraction-pilot.md` | unresolved |
| `docs/loom/plans/2026-08-05-request-derived-authorization.md` | `docs/loom/specs/2026-08-05-request-derived-authorization.md` | unresolved |
| `docs/loom/plans/2026-08-05-reviewer-evidence-grade-contract.md` | `docs/loom/specs/2026-08-05-reviewer-evidence-grade-contract.md` | unresolved |
| `docs/loom/plans/2026-08-06-backlog-ready-verb-and-close-loop.md` | `docs/loom/specs/2026-08-06-backlog-ready-verb-and-close-loop.md` | unresolved |
| `docs/loom/plans/2026-08-06-bounded-auto-third-round-and-dispatch-hardening.md` | `docs/loom/specs/2026-08-06-bounded-auto-third-round-and-dispatch-hardening.md` | unresolved |
| `docs/loom/plans/2026-08-06-dispatch-efficiency-trio.md` | `docs/loom/specs/2026-08-06-dispatch-efficiency-trio.md` | unresolved |
| `docs/loom/plans/2026-08-06-ledger-writer-and-plan-tooling-hardening.md` | `docs/loom/specs/2026-08-06-ledger-writer-and-plan-tooling-hardening.md` | unresolved |
| `docs/loom/plans/2026-08-06-progress-card-roadmap-view.md` | `docs/loom/specs/2026-08-06-progress-card-roadmap-view.md` | unresolved |
| `docs/loom/plans/2026-08-06-progress-cards-and-plan-ledger.md` | `docs/loom/specs/2026-08-06-progress-cards-and-plan-ledger.md` | unresolved |
| `docs/loom/plans/2026-08-07-loom-arc2-deletion-first-dimension.md` | `docs/loom/specs/2026-08-07-loom-arc2-deletion-first-dimension.md` | unresolved |
| `docs/loom/plans/2026-08-07-loom-arc3-memory-index-generation.md` | `docs/loom/specs/2026-08-07-loom-arc3-memory-index-generation.md` | unresolved |
| `docs/loom/plans/2026-08-07-loom-arc4a-prose-slim.md` | `docs/loom/specs/2026-08-07-loom-arc4-prose-slim.md` | unresolved |
| `docs/loom/plans/2026-08-07-loom-arc4b-finishing-collapse.md` | `docs/loom/specs/2026-08-07-loom-arc4-prose-slim.md` | unresolved |
| `docs/loom/plans/2026-08-07-loom-direction-layer.md` | `docs/loom/specs/2026-08-07-loom-direction-layer-and-commit-loop.md` | unresolved |
| `docs/loom/plans/2026-08-07-loom-mechanical-dedup-arc1.md` | `docs/loom/specs/2026-08-07-loom-mechanical-dedup-arc1.md` | unresolved |
| `docs/loom/plans/2026-08-07-stage-owner-and-blocked-enum.md` | `docs/loom/specs/2026-08-07-stage-owner-and-blocked-enum.md` | unresolved |
| `docs/loom/plans/2026-08-08-progress-display-hardening.md` | `docs/loom/specs/2026-08-08-progress-display-hardening.md` | unresolved |
| `docs/loom/plans/2026-08-10-cheap-hardening-batch.md` | `docs/loom/specs/2026-08-10-cheap-hardening-batch.md` | unresolved |
| `docs/loom/plans/2026-08-10-design-md-spec-conformance.md` | `docs/loom/specs/2026-08-08-design-md-spec-conformance.md` | unresolved |
| `docs/loom/plans/2026-08-10-loom-init-scaffold.md` | `docs/loom/specs/2026-08-10-loom-init-scaffold.md` | unresolved |
| `docs/loom/plans/2026-08-10-ship-progress-tooling.md` | `docs/loom/specs/2026-08-10-ship-progress-tooling.md` | unresolved |
| `docs/loom/plans/2026-08-10-task-mgmt-doc-currency.md` | `docs/loom/specs/2026-08-10-task-mgmt-doc-currency.md` | unresolved |
| `docs/loom/plans/2026-08-10-terminal-state-gates.md` | `docs/loom/specs/2026-08-10-terminal-state-gates.md` | unresolved |
| `docs/loom/plans/2026-08-11-review-cost-reduction.md` | `docs/loom/specs/2026-08-11-review-cost-reduction.md` | unresolved |
| `docs/loom/plans/2026-08-11-visualization-trigger-layer.md` | `docs/loom/specs/2026-08-11-visualization-trigger-layer.md` | unresolved |
| `docs/loom/plans/2026-08-12-adjudication-view-japanese.md` | `docs/loom/specs/2026-08-12-adjudication-view-japanese.md` | unresolved |
| `docs/loom/plans/2026-08-12-adjudication-view.md` | `docs/loom/specs/2026-08-12-adjudication-digest.md` | unresolved |
| `docs/loom/plans/2026-08-12-ascii-graph-generative-trigger.md` | `docs/loom/specs/2026-08-12-ascii-graph-generative-trigger.md` | unresolved |
| `docs/loom/plans/2026-08-13-brief-item-addressability.md` | `docs/loom/specs/2026-08-13-brief-item-addressability.md` | unresolved |
| `docs/loom/plans/2026-08-13-open-question-dispatch-gate.md` | `docs/loom/specs/2026-08-13-open-question-dispatch-gate.md` | unresolved |
| `docs/loom/plans/2026-08-14-loom-doc-language-layering.md` | `docs/loom/specs/2026-08-14-loom-doc-language-layering.md` | unresolved |
| `docs/loom/plans/2026-08-15-plain-relay-contract.md` | `docs/loom/specs/2026-08-15-plain-relay-contract.md` | unresolved |
| `docs/loom/plans/2026-08-16-loom-design-merge-part-1.md` | `docs/loom/plans/2026-08-16-loom-design-merge-plan.md` | unresolved |
| `docs/loom/plans/2026-08-16-loom-design-merge-part-2.md` | `docs/loom/plans/2026-08-16-loom-design-merge-plan.md` | unresolved |
| `docs/loom/plans/2026-08-16-loom-design-merge-part-3.md` | `docs/loom/plans/2026-08-16-loom-design-merge-plan.md` | unresolved |
| `docs/loom/plans/2026-08-16-loom-design-merge-plan.md` | `docs/loom/research/2026-08-15-loom-plugin-consolidation.md` | brief_file_missing |
| `docs/loom/plans/2026-08-17-artifact-table-routing.md` | `docs/loom/specs/2026-08-17-artifact-table-routing.md` | unresolved |
| `docs/loom/plans/2026-08-18-requirement-identity-hybrid.md` | `docs/loom/specs/2026-08-18-requirement-identity-hybrid.md` | unresolved |

</details>

## DIRECTION.md standing-choice state at run time

`docs/loom/DIRECTION.md`'s `## On-ramp standing choices` section is
**present**. When first observed for this audit (2026-08-18, base commit
`6186d710`), it existed only as an uncommitted working-tree diff of `+7`
lines on this branch — this arc's own Task 5, in flight while this task
first ran. As of this revision it is committed: `76a3faf9` ("record
repo-level on-ramp standing choice for row 1") + `cb39c5ce` ("DIRECTION
standing-choices comment — state entries change only by editing this
file"). Both facts are recorded because the section's *content* (the
row-1 entry below) is unchanged across the two observations — only its
commit status changed:

```
## On-ramp standing choices

<!-- Repo-level on-ramp decisions read by check_onramp_choice.py; grammar
owned by loom-code/hooks/family-reception.md §On-ramp standing choices. -->

- row 1 (product-principles): standing direct — monkey-skills deliberately keeps no docs/loom/PRINCIPLES.md; loom-family arcs go direct to a brief (2026-08-18)
```

`load_standing(repo_root)` therefore resolves `{1: "direct"}` at run
time. This state does not change any count above — none of the 427
scanned files used the `fired: rows <n> — standing <detour|direct>
(DIRECTION.md)` form (that form did not exist in the corpus before
this arc), so `load_standing`'s output was consulted but never matched
during this run.

## Disagreement with the brief's 2026-08-18 pre-measurement

The brief's §Problem states a pre-measurement over the 86 specs that
carry a `## Design-side on-ramp` line, classified by wording family:
**71 not-fired, 8 fired-and-agent-defaulted-direct, 3
fired-with-an-explicit-user-choice, 4 other** (86 total).

This run's checker-based count over the same corpus (87 specs contain
some form of the line — one more than the brief's 86, see note below):
**0 not-fired, 0 resolved, 87 unresolved** (of the 207 specs scanned;
the other 120 specs carry no on-ramp line at all and are also
`unresolved`).

**These disagree, and the disagreement is expected, not a bug**: the
brief's 71/8/3/4 was a human/LLM classification by *wording family*
(loose, semantic — "N/A", "not offered", "not applicable" all read as
"not fired" to a human) done *before* BI-1's canonical grammar existed.
The checker implements BI-1's strict grammar literally: exactly
`not fired — <reason>` or `fired: rows <n> — user chose <detour|direct>`
or `fired: rows <n> — standing <detour|direct> (DIRECTION.md)` — every
other spelling, including "N/A — ..." and "not offered — ...", is
`unresolved` by design (the lookalike-wording rule the checker's own
docstring cites). So the pre-measurement's "71 not-fired" bucket is
real *evidence that the on-ramp mostly does not fire*, but none of
those 71 specs would pass the checker unmodified — they would all need
their wording rewritten to the canonical `not fired — <reason>` form to
resolve. The 8 fired-agent-defaulted and 3 explicit-choice specs are
likewise 0-for-0 against the checker for the same reason: none of the
historical corpus was ever written in the new canonical grammar (this
arc's own brief, `2026-08-18-onramp-explicit-choice-gate.md`, is the
first).

The off-by-one (87 vs 86 specs carrying the line) is not investigated
further here — it is a one-file discrepancy against a pre-measurement
whose own method (§Problem, brief) is not reproduced in this repo, and
does not change any conclusion above.

## Fired-rate implication for future arcs

Going forward, only *newly written* briefs are graded against the
canonical grammar (this run's 0/0/87 bucket is a snapshot of the old,
pre-canonical corpus — it says nothing about how often future briefs
will resolve cleanly). The brief's own pre-measurement is still the
best available estimate of the underlying fire rate: **on the order of
8–11% of briefs (8 agent-defaulted + 3 explicit, of 86) have the
on-ramp actually fire**, i.e. roughly 1 in 10 arcs. Under BI-5's new
rule (recommend as a standalone ask, write `pending` until answered),
that is the rate at which a future arc will see the standalone
on-ramp ask at all — the other ~90% ("not fired") pay no added
ceremony, since `not_fired` and `resolved` both exit 0 and the
`writing-plans`/`git-guard.py` gates only block on `unresolved`
(`pending`, malformed, or fired-with-no-recorded-choice). The
ceremony this arc adds is therefore bounded to roughly 1 extra
standalone question per 10 arcs, not a per-arc tax.

## Commands

Specs loop (bash; exact commands run):

```bash
cd /Users/kouko/GitHub/monkey-skills
total=0; not_fired=0; resolved=0; unresolved=0; missing=0
for f in docs/loom/specs/*.md; do
  total=$((total+1))
  out=$(python3 loom-code/scripts/check_onramp_choice.py "$f" --repo-root . 2>&1)
  code=$?
  if [ $code -eq 1 ]; then missing=$((missing+1))
  elif [ $code -eq 2 ]; then unresolved=$((unresolved+1))
  elif [ $code -eq 0 ]; then
    if echo "$out" | grep -q "not_fired"; then not_fired=$((not_fired+1))
    else resolved=$((resolved+1)); fi
  fi
done
echo "SPECS total=$total not_fired=$not_fired resolved=$resolved unresolved=$unresolved missing=$missing"
```

Output reproduced: `SPECS total=207 not_fired=1 resolved=0 unresolved=206 missing=0`

Plans loop (Python; needed because plan headers use three different
`Source brief` spellings that a portable `sed`/`grep` one-liner could
not reliably normalize — see §Method step 2):

```python
#!/usr/bin/env python3
import re, subprocess, sys
from pathlib import Path

REPO_ROOT = Path("/Users/kouko/GitHub/monkey-skills")
PLANS_DIR = REPO_ROOT / "docs" / "loom" / "plans"
LINE_RE = re.compile(r"^\**Source brief\**:\s*(?P<rest>.+)$")
MD_LINK_RE = re.compile(r"^\[[^\]]*\]\((?P<path>[^)]+)\)")
BACKTICK_RE = re.compile(r"^`(?P<path>[^`]+)`")

def extract_path(rest: str) -> str:
    rest = rest.strip()
    m = MD_LINK_RE.match(rest)
    if m: return m.group("path")
    m = BACKTICK_RE.match(rest)
    if m: return m.group("path")
    m = re.match(r"^[A-Za-z0-9._/\-]+", rest)
    return m.group(0) if m else rest

def main():
    plans = sorted(PLANS_DIR.glob("*.md"))
    total = len(plans)
    no_source_line = not_fired = resolved = unresolved = missing = 0
    for plan in plans:
        text = plan.read_text(encoding="utf-8")
        brief_rel = None
        for line in text.splitlines():
            m = LINE_RE.match(line.strip())
            if m:
                brief_rel = extract_path(m.group("rest"))
                break
        if brief_rel is None:
            no_source_line += 1
            continue
        brief_path = REPO_ROOT / brief_rel.lstrip("./")
        if not brief_path.exists() and brief_rel.startswith(".."):
            brief_path = (PLANS_DIR / brief_rel).resolve()
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "loom-code/scripts/check_onramp_choice.py"),
             str(brief_path), "--repo-root", str(REPO_ROOT)],
            capture_output=True, text=True)
        code = result.returncode
        if code == 1: missing += 1
        elif code == 2: unresolved += 1
        elif code == 0:
            if "not_fired" in result.stdout: not_fired += 1
            else: resolved += 1
    print(f"PLANS total={total} no_source_brief_line={no_source_line} "
          f"not_fired={not_fired} resolved={resolved} unresolved={unresolved} "
          f"brief_file_missing={missing}")

if __name__ == "__main__":
    main()
```

Output reproduced: `PLANS total=220 no_source_brief_line=8 not_fired=1 resolved=0 unresolved=200 brief_file_missing=11`

Plans loop — full-pair-emitting variant (Python; same resolution logic
as the counting variant above, but also prints every blocked pair as a
markdown table row on stdout, counts on stderr — this is exactly what
generated §Appendix's 211-row table):

```python
#!/usr/bin/env python3
import re, subprocess, sys
from pathlib import Path

REPO_ROOT = Path("/Users/kouko/GitHub/monkey-skills")
PLANS_DIR = REPO_ROOT / "docs" / "loom" / "plans"
LINE_RE = re.compile(r"^\**Source brief\**:\s*(?P<rest>.+)$")
MD_LINK_RE = re.compile(r"^\[[^\]]*\]\((?P<path>[^)]+)\)")
BACKTICK_RE = re.compile(r"^`(?P<path>[^`]+)`")

def extract_path(rest: str) -> str:
    rest = rest.strip()
    m = MD_LINK_RE.match(rest)
    if m: return m.group("path")
    m = BACKTICK_RE.match(rest)
    if m: return m.group("path")
    m = re.match(r"^[A-Za-z0-9._/\-]+", rest)
    return m.group(0) if m else rest

def main():
    plans = sorted(PLANS_DIR.glob("*.md"))
    total = len(plans)
    no_source_line = not_fired = resolved = unresolved = missing = 0
    blocked = []
    for plan in plans:
        text = plan.read_text(encoding="utf-8")
        brief_rel = None
        for line in text.splitlines():
            m = LINE_RE.match(line.strip())
            if m:
                brief_rel = extract_path(m.group("rest"))
                break
        if brief_rel is None:
            no_source_line += 1
            continue
        brief_path = REPO_ROOT / brief_rel.lstrip("./")
        if not brief_path.exists() and brief_rel.startswith(".."):
            brief_path = (PLANS_DIR / brief_rel).resolve()
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "loom-code/scripts/check_onramp_choice.py"),
             str(brief_path), "--repo-root", str(REPO_ROOT)],
            capture_output=True, text=True)
        code = result.returncode
        rel_plan = str(plan.relative_to(REPO_ROOT))
        if code == 1:
            missing += 1
            blocked.append((rel_plan, brief_rel, "brief_file_missing"))
        elif code == 2:
            unresolved += 1
            blocked.append((rel_plan, brief_rel, "unresolved"))
        elif code == 0:
            if "not_fired" in result.stdout: not_fired += 1
            else: resolved += 1
    print(f"PLANS total={total} no_source_brief_line={no_source_line} "
          f"not_fired={not_fired} resolved={resolved} unresolved={unresolved} "
          f"brief_file_missing={missing}", file=sys.stderr)
    print(f"| Plan | Resolved brief path | Outcome |")
    print(f"|---|---|---|")
    for rel_plan, brief_rel, reason in blocked:
        print(f"| `{rel_plan}` | `{brief_rel}` | {reason} |")

if __name__ == "__main__":
    main()
```

Output reproduced (stderr): `PLANS total=220 no_source_brief_line=8 not_fired=1 resolved=0 unresolved=200 brief_file_missing=11`; stdout: 2 header lines + 211 data rows, identical to §Appendix.


Re-running both commands against the same repo state (branch
`onramp-explicit-choice-gate`, DIRECTION.md state as recorded above)
reproduces these exact numbers.
