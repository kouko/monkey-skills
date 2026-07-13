# skill-creator-advance token refactor — skill-refactor gate evidence (2026-07-13)

Target: `skill-dev-toolkit/skills/skill-creator-advance/SKILL.md`
6,069 → 4,497 words (−25.9%), back under the 4,500 CHK-SKL-010 cap.
Gate: `skill-dev-toolkit:skill-refactor` Q1/Q2/Q3. First real-world run of the
0.2.0 machinery (taxonomy-guided pre-pass + enriched moves catalog).

## Pre-pass (0.2.0 first run — validation data)

Analyst executed `ablation-mode.md §Taxonomy-guided candidate pre-pass`:
section inventory (36 sections), taxonomy scan (NO-OP/SED/NEG/PCC/DUP-ref
hits with quoted evidence), 16 ranked moves totaling est. ~1,750w vs 1,569
needed, keep-list of 9 protected anchors. Implementer actuals landed within
±20% of estimates on 14/16 ranks; two deviations were the plan's own
sanctioned fallbacks (rank 12: plan counted 3 snapshot dups, only 2 existed;
rank 11: took the §4 "give"). No Leading-Word Substitution candidate fired
(no in-body derivation of a nameable pre-trained concept found).
Full plan preserved at the PR; ordering proved sound — ranks 1-3 alone
delivered ~830w.

## Test prompts

`test-prompts.json` (pre-existing, 2026-04-29) + P4 added PRE-BASELINE
(description-optimization coverage — the documented use case whose section
was a likely extraction target; both gate sides ran identical 4 prompts).

## Q1 — runs and verdicts

Baseline ×4 and candidate ×4 (sonnet runners, dry-run cold-reads), 3-judge
opus ensemble (utility / content / boundary framings, randomized A/B labels,
with an explicit simulation-depth caveat in the judge prompts — the lesson
from the writing-plans round's false non-equivalence):

| Pair | J1 utility | J2 content | J3 boundary |
|---|---|---|---|
| P1 create-from-scratch | equivalent | equivalent | equivalent |
| P2 structural split | equivalent | equivalent | **uncertain** |
| P3 vague router | equivalent | equivalent | equivalent |
| P4 description opt | equivalent | equivalent | equivalent |

P2 consensus rule: 2 equivalent + 1 uncertain → **PASS, moderate confidence**
(no not_equivalent anywhere; the gate escalates on substantive dissent, not
on uncertainty). J3's uncertainty is a BIDIRECTIONAL gate-machinery
divergence (candidate ran the Gate-3 AskUserQuestion but informal Gate 1/2;
baseline the reverse) rooted in a PRE-EXISTING doc ambiguity both versions
carry — all four independent runners flagged "Case (c) doesn't inherit
Pre-Creation Gates 1/2" unprompted. BACKLOG'd as a behavior-change item
(out of refactor scope).

## Q2 / Q3

- Q2: −25.9% ✓ (≥10%).
- Q3: frontmatter name+description byte-identical; 9 reference files, none
  removed, none added (extractions absorbed into existing
  description-design.md +479w and asking-user-questions.md +328w;
  plugin-conventions.md +0 — its claimed duplicates verified already
  present). Keep-list spot-greps 10/10 hit (router table, House standard,
  eval mechanics incl. one-shot timing warning + grading fields +
  aggregate_benchmark, flat-folder hook warning, /skill-test guard, Lack of
  Surprise, blind-comparison boundary, catalog-quoted ALWAYS/NEVER line).

## Verdict: PROCEED

User-approved confirm items (2026-07-13, both approved): §Description Best
Practices → ~70w pointer (removed the items-6/7 contradiction with §House
standard); "make descriptions a little 'pushy'" sentence deleted
(contradicted the anti-over-trigger MUST).

## Durable observations

1. The taxonomy pre-pass paid for itself on first use: ranked ordering meant
   the three biggest cuts were validated extraction targets, and the ±20%
   estimate band held — future rounds can budget cuts from the plan without
   re-measuring everything.
2. Judge-prompt simulation-depth caveat prevented a repeat of the
   writing-plans false non-equivalence on P2 — the uncertainty that remained
   was genuine (pre-existing ambiguity), not artifact.
3. Every independent cold-read (4/4) surfacing the same doc gap is a strong
   discovery signal — equivalence infrastructure doubles as a skill-design
   fuzzer.
