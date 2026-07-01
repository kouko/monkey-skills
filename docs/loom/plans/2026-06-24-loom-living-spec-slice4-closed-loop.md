# Plan: loom living-spec slice 4 (F) — closed loop (prior-state intake)

Source brief: docs/loom/specs/2026-06-24-loom-living-spec-slice4-closed-loop.md
Total tasks: 1
Critical-path depth: 1 (≤5)
Execution order: sequential
Plan-document-reviewer verdict: PASS (2026-06-24; 14/14)

Resolved open-Qs:
- **Section placement** = adjacent to §"Consuming a ui-flows.md seed" (both are *intake*
  seams; symmetric + discoverable).
- **Test granularity** = ONE behavioral test asserting all load-bearing elements (mirrors
  slice-3's `test_skill_documents_intent_layer` precedent — the doc + its test are one
  cohesive TDD unit: the test is the RED, the doc section makes it green).

This is a doc-convention slice: one cohesive deliverable (the prior-state section + its
behavioral test). The doc-mirrors-code dependency (test asserts the section's content) makes
them one TDD task, not two — the implementer writes the failing test first, then the section.

## Task 1 — prior-state intake convention + behavioral test
- Description: add a NEW section to `loom-spec/skills/spec-expansion/SKILL.md`, e.g.
  **"Consuming the persisted intent layer as prior-state"**, placed adjacent to the existing
  §"Consuming a ui-flows.md seed" (SKILL.md:53) and mirroring its style (prose + a fenced/MD
  seam-mapping table + bold lead-ins). It MUST carry: (a) **point-don't-copy + link-back** —
  spec-expansion references the persisted layers by path and links back, NEVER copies their
  content in (a copy = a 2nd SSOT that drifts); (b) a **seam-mapping table** — MID
  `<capability>/README.md` → Phase ① seed-adequacy + USM backbone; TOP `MODEL.md`
  `## Object state machines` → Phase ② OOUX object/state model; TOP `## Invariants` →
  Phase ③ matrix guard-rule lenses; TOP `## Out of scope` → Phase ③ pruning; the generated
  INDEX (capability→req→test) → the fan boundary, **fan NET-NEW only** (#406); (c) the
  **empty base case** — prior-state is additive and may be empty; absent → ignore the section
  and treat the input as a generic/net-new seed (mirror SKILL.md:78), an empty/absent layer
  is never authoritative, no cold-start deadlock; (d) the **INDEX referenced "when present"**
  (its committed location is capstone-G scope). Write the behavioral RED test FIRST, then the
  section.
- Module: loom-spec/skills/spec-expansion/SKILL.md
- Files touched: loom-spec/skills/spec-expansion/SKILL.md, loom-spec/scripts/test_spec_expansion_skill.py
- Context paths:
  - loom-spec/skills/spec-expansion/SKILL.md  (§53 ui-flows seam = template to mirror; §69 its mapping table; §90/§94/§141/§166 the three phases the table maps to; §356 the authoring section that wrote the layer this reads)
  - loom-spec/scripts/test_spec_expansion_skill.py  (existing behavioral-test style, e.g. test_skill_documents_intent_layer)
- Acceptance:
  - RED: test_spec_expansion_skill.py::test_skill_documents_prior_state_intake fails before the section exists (asserts the section + its load-bearing elements absent).
  - GREEN: SKILL.md contains the new section naming point-don't-copy/link-back (never-copy), the seam-mapping rows (MID README→Phase ①; TOP `## Object state machines`→Phase ②; TOP `## Invariants`→Phase ③; TOP `## Out of scope`→Phase ③; INDEX→fan-net-new-only), the empty base case (additive/may-be-empty/absent→treat-as-generic-seed), and the INDEX-when-present qualifier; the test passes; full loom-spec suite green.
- Dependencies: none
- Independent: false
- Brief item covered: "a new doc-convention section in spec-expansion/SKILL.md … mirroring the existing §'Consuming a ui-flows.md seed' template, carrying: point-don't-copy + link-back; a seam-mapping table; the empty base case; … plus a behavioral test"

## Notes
- Single cohesive TDD task (doc section + its behavioral test) — mirrors slice-3 T4's
  doc+test pattern. Depth 1; no parallelism (one task).
- Out of scope (from brief): active/deferred status (capstone G), repo-wide index wiring +
  pre-merge required checks (capstone G), any machine merge/parser of prior-state
  (point-don't-copy READING convention only), editing the persisted layer from the read path.
- Test command: `cd loom-spec/scripts && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -q`
  (loom-spec-ci.yml runs this in CI as of slice 3).
