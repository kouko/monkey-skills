# Plan: DESIGN→spec seam (P1) — doc-only point-don't-copy convention

Source brief: docs/spec-toolkit/specs/2026-06-16-design-spec-seam.md
Total tasks: 2
Critical-path depth: 1 (both tasks at the same level; uncapped width)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-16, 13/14 — Check 12 N/A; doc-task grep oracles judged specific)

Notes:
- Doc-only change (skill markdown prose). No production code, no Python, no tests
  in the code sense → `Acceptance` uses a grep diagnostic as the RED/GREEN oracle
  (convention absent = RED, present = GREEN). This is the documented doc-task
  pattern, not a TDD exemption dodge.
- Task 1 owns the SSOT mapping table (consumer side). Task 2 points to Task 1 by
  `plugin:skill` name only — a stable existing reference, NOT a content copy and
  NOT a new imported symbol — so the two are genuinely independent (no drift
  surface, no semantic ordering). Both marked `Independent: true`.
- Final verification is NOT a unit test: re-run dogfood station ⑤ against
  ~/pipeline-dogfood/invoice-tracker/ (out of repo) — recorded as a post-merge
  manual gate in the brief, run by the orchestrator after both tasks land.

## Task 1 — spec-expansion: add "Consuming a ui-flows.md seed" subsection
- Description: Add a short subsection to spec-expansion's SKILL.md (near the
  seed-adequacy pre-flight, lines 66–82, or as a standalone `##` before Phase ①)
  that (a) states when the seed is a `ui-flows.md`, treat its inventory / flows /
  entry-exit as already-specified surface — do not re-derive or re-express; (b)
  states the proposal LINKS BACK to the named ui-flows sections and fans out only
  NET-NEW behavior (state machines, guard rules, edge cases, `#### Scenario:`) —
  point-don't-copy; (c) includes the 3-row SSOT mapping table (§inventory+flags →
  Phase ② OOUX; §User flows+§Entry+§Exit → ③c `## Journey navigation`;
  interaction-dense surface → `## Cross-object combinations`).
- Module: spec-toolkit/skills/spec-expansion
- Files touched: spec-toolkit/skills/spec-expansion/SKILL.md
- Context paths:
  - spec-toolkit/skills/spec-expansion/SKILL.md (insertion point + existing phases)
  - docs/spec-toolkit/specs/2026-06-16-design-spec-seam.md (brief — the mapping)
  - interface-design-toolkit/skills/interaction-flows/SKILL.md (lines 118–124 —
    the reciprocal seam wording to stay consistent with)
- Acceptance:
  - RED: `grep -ci 'ui-flows' spec-toolkit/skills/spec-expansion/SKILL.md` = 0
    (current state); and `grep -ci "point-don't-copy\|net-new"` = 0.
  - GREEN: the subsection exists — `grep -ci 'ui-flows' …/spec-expansion/SKILL.md`
    ≥ 3 (heading + mapping rows + link-back rule), the 3-row mapping table is
    present, and the SKILL.md body stays within the ~6,000-token / flat-skill
    convention (no new subfolder).
- Dependencies: none
- Independent: true
- Brief item covered: "spec-expansion (consumer, SSOT owner) — add a short
  subsection ('Consuming a ui-flows.md seed') … link back … fan out only NET-NEW
  behavior … the mapping table (SSOT)."

## Task 2 — interaction-flows §6: reciprocal point-don't-copy + addressability note
- Description: Extend interaction-flows §6 seam paragraph (SKILL.md:118–124, which
  already half-names the mapping) with the reciprocal note: spec-expansion links
  back to these sections rather than copying them (point-don't-copy), so structure
  ui-flows sections with stable / addressable headings; add a one-line pointer to
  `spec-toolkit:spec-expansion` for the canonical mapping (do NOT copy the table —
  avoids drift). Extend the existing paragraph; do not replace it.
- Module: interface-design-toolkit/skills/interaction-flows
- Files touched: interface-design-toolkit/skills/interaction-flows/SKILL.md
- Context paths:
  - interface-design-toolkit/skills/interaction-flows/SKILL.md (§6, lines 111–139;
    "See also" pointer pattern at line 158)
  - docs/spec-toolkit/specs/2026-06-16-design-spec-seam.md (brief)
- Acceptance:
  - RED: `grep -ci "point-don't-copy\|addressable\|stable heading"`
    interaction-flows/SKILL.md = 0 (current state).
  - GREEN: §6 contains the reciprocal point-don't-copy note + the addressable-
    headings instruction + the `spec-toolkit:spec-expansion` canonical-mapping
    pointer; the original seam wording (lines 118–124) is preserved (extended, not
    replaced); flat-skill + token budget intact.
- Dependencies: none
- Independent: true
- Brief item covered: "interaction-flows §6 (producer) — extend the existing seam
  paragraph … with the reciprocal point-don't-copy note … One-line pointer to
  spec-toolkit:spec-expansion for the canonical mapping (no copied table → no drift)."
