---
name: schema-shaped-fixtures-certify-the-rule-not-the-parser
description: A fixture corpus authored from the format spec certifies the VERDICT RULE and says nothing about the PARSER — a 10-cell frozen corpus shipped the R3 variant at 0 false alarms while the real plan corpus broke the parse layer in five shapes the schema never names (wrapped multi-line values, trailing parenthetical annotations, letter-suffixed task numbers, Status-line comment tails, nested-bullet lists); only a sweep of the entire real corpus certifies the parser, and every rate computed before that sweep is contaminated
type: practice
origin: branch docs-declared-vs-actual-measurement (2026-08-01) — declared-vs-actual Files touched measurement arc
---

The declared-vs-actual comparator was measured two ways on one branch.
The frozen 10-cell corpus (answer key frozen before the comparator
existed) certified the verdict rule: R3 at 4 hits / 0 misses / 0 false
alarms. Then a sweep of all 170 real plans broke the parse layer five
ways, none representable in the schema-shaped cells:

| real shape | schema says | failure direction |
|---|---|---|
| value wrapped across continuation lines | inline comma-separated | false UNDER (paths invisible) |
| trailing `(annotation)` after last token | — | token contaminated |
| `## Task 3a` letter-suffixed numbers | `## Task <N>` | **silent non-coverage** |
| `# comment` tails on `Status:` lines | bare vocabulary | all join keys dropped |
| nested `- <path>` sub-bullets | inline list | paths invisible |

Four of five fail loud (false alarms); the letter-suffix one is silent —
the dangerous direction survived every constructed cell.

**Why:** fixtures authored from the format doc inherit the format doc's
idealizations. The corpus is written by many hands over months; the doc
is written once. A checker validated only on doc-shaped inputs measures
the doc, not the corpus — the same failure as
[[convergence-is-not-evidence-when-the-sample-is-shared]], one layer
down: the sample was the spec's imagination.

**How to apply:** when building any checker over a house format (plans,
briefs, ledgers, frontmatter), sweep it across the ENTIRE real corpus
before trusting a single rate; diff the parse-error classes pre/post
any parser change (the class arithmetic catches wrong attributions);
treat the format doc as aspiration and the corpus as truth — where they
disagree, either the parser follows practice (bold/plain field
precedent) or the gap is recorded as silent-non-coverage debt, never
left unquantified. Frozen-key discipline stays for the RULE; the sweep
is a separate, mandatory certification for the PARSER.
