---
name: 2026-08-31-mutation-and-property-testing-for-loom
description: Evaluate mutmut mutation testing and hypothesis property-based testing for loom's checker scripts; no evidence yet either pays for a prose-contract repo
status: open
origin: 2026-08-31 — adversarial-audit-station arc (docs/loom/specs/2026-08-31-adversarial-audit-station.md `## Out of Scope`), deferred from BI-11's scope
start: event — a checker script (backlog_index.py, check_loom_memory_integrity.py, or a similar loom-code validator) ships a bug that a mutation- or property-testing run would have caught but the existing test suite did not, giving concrete evidence the technique pays here
---

`loom-code` and this repo's `scripts/` directory are mostly prose-contract
enforcement: Python scripts that validate Markdown frontmatter grammars,
regenerate indexes, and check cross-file agreement (`backlog_index.py`,
`check_loom_memory_integrity.py`, `check_contract_citations.py`, and
siblings). Two testing techniques were named but not evaluated for this
codebase during the adversarial-audit-station arc:

- **Mutation testing** (e.g. `mutmut`) — systematically mutates the
  checker's own source and confirms the test suite kills each mutant;
  would catch checker logic that "looks tested" but has an
  under-constrained assertion (the exact class of gap the
  batch-cost-numbers-are-declared-not-observed finding named for a
  different script — declared numbers nothing observed).
- **Property-based / fuzz testing** (e.g. `hypothesis`) — generates
  many frontmatter/body combinations against the grammar these checkers
  enforce, rather than relying only on hand-written fixture files.

Neither was adopted in the station arc: hand-written fixtures plus the
audit's reproduce-or-hold discipline were judged sufficient for BI-11's
scope, and there is no measured evidence either technique would have
caught something the current suite missed. This entry exists to hold the
question open rather than lose it, and its `start:` condition is
evidence-gated on purpose — don't pick this up speculatively; pick it up
when a real missed bug in a checker script makes the case.
