# Plan: P2 — principles-conformance lens in the existing critics

Source brief: docs/loom/specs/2026-06-17-principles-conformance-lens.md
Total tasks: 3
Critical-path depth: 2 (T1 independent; T2 → T3 chain)
Execution order: parallel-where-possible (T1 ∥ T2; T3 after T2)
Plan-document-reviewer verdict: PASS (2026-06-17, 14/14 — doc/agent-prose grep+drift oracles judged specific; T1∥T2 disjoint, T3 after T2)

Notes:
- Doc/agent-prose change (markdown only — agent + skill prose). No Python, no unit
  tests → `Acceptance` uses grep diagnostics + one automated drift check
  (`verify-drift.py` must stay green for T2) + a final dogfood behavior run.
- T1 (spec side) and T2 (code agent) touch disjoint files in different plugins,
  no shared symbol → `Independent: true`.
- T3 (requesting-code-review SKILL) depends on T2: its dispatch-prompt addition
  references the `principles-conformance` dimension name that T2 defines in the
  agent, and the discovered PRINCIPLES.md path is the input that dimension consumes
  (doc-mirrors-code coupling). Sequential after T2; NOT marked Independent.
- Final verification (post-merge of all 3): dogfood against
  ~/pipeline-dogfood/invoice-tracker/ — confirm the code-side dimension + spec-side
  lens both fire with PRINCIPLES.md present, and degrade to N/A when it is removed.
  Recorded as an orchestrator-run gate, not a task-level oracle.

## Task 1 — completeness-critic: add 6th omission-framed principles lens
- Description: In completeness-critic/SKILL.md, add a 6th lens to "### The five
  lenses" (rename heading to "### The lenses" or "### The six lenses") framed as an
  OMISSION question — *"what PRINCIPLES.md-entailed behavior did the spec OMIT?"*
  (e.g. a principle "must work offline" → hunt where the spec drops offline
  handling). The lens reads `docs/loom/PRINCIPLES.md` as an
  extra input view; if absent, the lens is an announced N/A no-op. Must respect the
  skill's absence-not-inconsistency boundary (SKILL.md:143) — frame as missing
  principle-entailed behavior, NOT "the spec violates a principle".
- Module: spec-toolkit/skills/completeness-critic
- Files touched: spec-toolkit/skills/completeness-critic/SKILL.md
- Context paths:
  - spec-toolkit/skills/completeness-critic/SKILL.md (lenses block :187-218; panel
    mechanics :105-141; absence-not-inconsistency boundary :143)
  - docs/loom/specs/2026-06-17-principles-conformance-lens.md (brief)
- Acceptance:
  - RED: `grep -ci 'PRINCIPLES' spec-toolkit/skills/completeness-critic/SKILL.md` = 0.
  - GREEN: a 6th lens exists naming PRINCIPLES.md, framed as omission ("entailed …
    omit/missing", not "violate"); the panel-count references are updated
    (five→six where the literal count is stated); N/A-when-absent stated; flat-skill
    + ≤6k-token body intact.
- Dependencies: none
- Independent: true
- Brief item covered: "Add a 6th lens to the panel framed as omission, not
  violation: 'what principle-ENTAILED behavior did the spec OMIT?'"

## Task 2 — code-reviewer agent: add 9th principles-conformance dimension
- Description: In code-toolkit/agents/code-reviewer.md add a 9th dimension
  `principles-conformance` to the `dimension_scores` block (:296-304) and a row to
  the dimension→source mapping table (:339-346). It asks the CONFORMANCE question —
  *does the branch diff VIOLATE any PRINCIPLES.md `— check:` clause?* — mapped to the
  **consumer's `docs/loom/PRINCIPLES.md`** (NOT a code-team
  standard). Severity: violation of a falsifiable check = 🟡 (🔴 if the principle is
  safety/security-bearing); ambiguous = 🟢. Graceful N/A when PRINCIPLES.md absent.
  The edit MUST land OUTSIDE the injected baseline / rule-sheet block so drift stays
  green.
- Module: code-toolkit/agents/code-reviewer.md
- Files touched: code-toolkit/agents/code-reviewer.md
- Context paths:
  - code-toolkit/agents/code-reviewer.md (dimension_scores :296-304; mapping :339-346;
    locate the synced baseline/rule-sheet block boundary and edit outside it)
  - docs/loom/specs/2026-06-17-principles-conformance-lens.md (brief)
- Acceptance:
  - RED: `grep -ci 'principles-conformance' code-toolkit/agents/code-reviewer.md` = 0.
  - GREEN: `principles-conformance` appears in both the `dimension_scores` block and
    the mapping table, maps to the consumer PRINCIPLES.md (not a code-team standard),
    states N/A-when-absent + the 🟡/🔴 severity rule; AND
    `python code-toolkit/scripts/verify-drift.py` still exits 0 ("all … functional
    copies match") — proving the edit did not disturb the synced baseline block.
- Dependencies: none
- Independent: true
- Brief item covered: "code-reviewer agent: add a 9th dimension
  `principles-conformance` to the dimension_scores block + the dimension→source
  mapping … mapped to the consumer's PRINCIPLES.md artifact."

## Task 3 — requesting-code-review SKILL: discover + pass PRINCIPLES.md path
- Description: In requesting-code-review/SKILL.md §Process (the dispatch step that
  passes "diff range, paths to rubrics + checklists, branch context"), add: discover
  `docs/loom/PRINCIPLES.md` in the consumer repo and pass its
  path to the code-reviewer with the conformance instruction; if absent, pass
  nothing and the dimension is N/A. Reference the `principles-conformance` dimension
  by the exact name T2 defines.
- Module: code-toolkit/skills/requesting-code-review
- Files touched: code-toolkit/skills/requesting-code-review/SKILL.md
- Context paths:
  - code-toolkit/skills/requesting-code-review/SKILL.md (§Process, the Agent-dispatch
    step that lists what the orchestrator passes)
  - code-toolkit/agents/code-reviewer.md (the dimension name added in T2 — cite it
    exactly)
  - docs/loom/specs/2026-06-17-principles-conformance-lens.md (brief)
- Acceptance:
  - RED: `grep -ci 'PRINCIPLES' code-toolkit/skills/requesting-code-review/SKILL.md` = 0.
  - GREEN: the Process dispatch step names `docs/loom/PRINCIPLES.md`
    discovery + path pass-through + N/A-when-absent, and references the
    `principles-conformance` dimension by the name T2 uses; flat-skill + token budget
    intact.
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: "requesting-code-review SKILL.md: in the dispatch step,
  discover docs/loom/PRINCIPLES.md … and pass its path to the
  reviewer with the conformance instruction."
