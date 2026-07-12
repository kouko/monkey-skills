# Plan: visual-style movement anchor — Phase 1 (canon split + Axis-B seed + 3-5/divergent flow)

Source brief: docs/loom/specs/2026-07-12-visual-style-movement-anchor-and-quality-separation.md
Total tasks: 7
Critical-path depth: 4 (≤5)   ← T1 → T2 → T4a → T5a (and T1 → T2 → T4b → T5b); T3 is a parallel leaf off T2
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-12, round-2 fix applied — see Notes)

## Notes

- **Review history**: round 1 → NEEDS_REVISION (Check 4, multi-module T4/T5) →
  split by file into T4a/T4b + T5a/T5b. Round 2 → NEEDS_REVISION (Check 14: T5a
  and T5b were marked `Independent: true` while sharing files with their
  `Independent: true` predecessors T4a/T4b). Fix applied = the reviewer's exact
  prescribed remedy: flip T5a/T5b to `Independent: false`. Round-3 re-review
  SKIPPED: the change is strictly parallelism-removing (Independent:true→false
  only drops a parallel-eligibility claim and adds a sequential floor — it cannot
  introduce a cycle, change critical-path depth, or drop coverage), and the round-2
  reviewer pre-confirmed the post-fix state carries only an advisory Check-15
  under-marking (never a failure). Wave-3 parallel set (T3, T4a, T4b) unchanged.

- Scope = Phase 1 only (mechanism + runnable seed) per brief §Phasing. Phase 2
  catalog expansion is a separate additive BACKLOG item, not planned here.
- **Key testing constraint (from `scripts/test_canon_references.py`)**: that suite
  enforces **≥14 entries** on every file in its `CANON_FILES` list. The new Axis-B
  surface file is intentionally a **small seed (~6)** — so it MUST NOT be added to
  `CANON_FILES`; it gets its own `test_surface_canon.py` (≥5 rows, `Currency`
  column, risk-flag note, cites research doc). `canon-design-visual.md` stays in
  `CANON_FILES`; after removing the one surface-cycle row it retains ~19 rows,
  still ≥14 (safe).
- **Module split (round-2 fix)**: the Design-flow change spans two SSOT files that
  are edited independently — `SKILL.md` (Step-3 audit list + carve-out) and
  `question-sets.md` (Design lane). Per one-module-per-task, the flow work is
  T4a/T4b (two-round + audit list) and T5a/T5b (3-5 + divergent), split by file.
- **Visual-lens 3-5 is a carve-out, NOT a global bump**: `SKILL.md` Step-3's
  generic "2-3 candidates" stays 2-3 for Product/Engineering; the visual lens gets
  an explicit 3-5 override (carve-out note in SKILL.md; the primary count wording
  in question-sets.md's Design lane). Guard assertions confirm Product (8-Q) and
  Engineering (2-3) wording is untouched.
- **Version bump is a close-out action, not a task** (finishing-a-development-branch):
  bump `loom-product-principles/.claude-plugin/plugin.json` + sync the Codex
  manifest at branch close. This repo has missed this before — confirm it lands.
- No change-folder input (brainstorming-brief plan) → `check_scenario_coverage.py`
  N/A; only plan-document-reviewer runs.
- Tests are stdlib + pytest, path-based, mirroring the existing structural
  grep-tests. New `test_surface_canon.py` is auto-discovered by
  `python3 -m pytest loom-product-principles/scripts/` (no declaration needed).

## Decision Log

Kickoff sweep (post-PASS): **zero one-way-door decisions** — every task is a
prose/reference-file edit, trivially reversible (two-way door), so nothing
escalates to a kickoff briefing (kickoff-briefing.md §a). No `docs/loom/PRINCIPLES.md`
in this repo → §d default would brief all one-way-door hits, but there are none.
The settled design choices (all decided WITH the user across the brainstorm; recorded
here per §e two-way-door routing):

- Two SEPARATE files (canon-design-visual.md = Axis A, canon-design-surface.md =
  Axis B) — contamination prevention that scales with Axis-B enrichment. (user)
- Axis-B ships a ~6-entry Phase-1 seed; catalog expansion is Phase 2 (additive,
  BACKLOG). (user)
- Divergent candidates: 1-2 of the 3-5, agent-labeled on-brief vs exploratory,
  deviating on expression but defensible against PRINCIPLES values. (user)
- `Excluded when` note only on Axis-A entries that cross common values (e.g.
  Memphis vs low-stimulus) — not every entry. (user)
- Axis-B grounding via a dated companion research doc, not editing the §3 doc. (user)
- Surface file kept OUT of test_canon_references.py's ≥14 CANON_FILES contract;
  own test with a ≥5 + Currency-column contract. (agent — forced by the ≥14 rule vs
  the ~6-treatment reality; two-way, reversible)
- Visual-lens 3-5 is a carve-out; generic 2-3 preserved for Product/Engineering.
  (user-scoped)
- Version bump handled at finishing-a-development-branch close-out, not a task.
  (agent — repo convention)

## Task 1 — Axis-B surface-treatment grounding research doc
- Description: Author a dated companion research doc grounding the ~6 UI
  surface-treatment paradigms (skeuomorphism, flat, material-as-surface,
  neumorphism, glassmorphism, spatial/Liquid-Glass) — each with a one-line
  characterization, a currency/era note, and a citable source URL. This is the
  grounding the surface canon file cites (mirrors how `canon-design-visual.md`
  cites `.../research/2026-07-10-principles-canon-base-lists.md §3`).
- Module: docs/loom/research (new doc)
- Files touched: docs/loom/research/2026-07-12-ui-surface-treatments-canon.md, loom-product-principles/scripts/test_surface_canon.py
- Context paths:
  - docs/loom/research/2026-07-10-principles-canon-base-lists.md
  - loom-product-principles/skills/product-principles/references/canon-design-visual.md
- Acceptance:
  - RED: loom-product-principles/scripts/test_surface_canon.py::test_surface_research_doc_grounds_seed fails (doc absent)
  - GREEN: the doc exists with ≥5 named surface-treatment sections, each carrying a source URL and an era/currency note (test asserts ≥5 `http` links and the 6 seed names present)
- Dependencies: none
- Independent: false
- Brief item covered: "Grounded to time-stamped current sources (NN/g + platform release docs) via a dated companion research doc"

## Task 2 — create canon-design-surface.md (Axis-B seed, distinct contract)
- Description: Create the new Axis-B reference `canon-design-surface.md` — same
  table shape as the visual canon (`Entry (originator, era) | Fits when… |
  Stability | Source`) PLUS a `Currency` column, seeded with the ~6 surface
  treatments, each row citing a source URL; add risk-flag notes where relevant
  (e.g. neumorphism's low-contrast WCAG risk); header frames it agent-facing
  ("never shown raw to the user"), "including but not limited to" (extensible),
  and states it is grounded in the Task-1 research doc. NOT added to `CANON_FILES`
  (small seed by design — see Notes).
- Module: loom-product-principles/skills/product-principles/references/canon-design-surface.md
- Files touched: loom-product-principles/skills/product-principles/references/canon-design-surface.md, loom-product-principles/scripts/test_surface_canon.py
- Context paths:
  - loom-product-principles/skills/product-principles/references/canon-design-visual.md
  - loom-product-principles/scripts/test_canon_references.py
  - docs/loom/research/2026-07-12-ui-surface-treatments-canon.md
- Acceptance:
  - RED: loom-product-principles/scripts/test_surface_canon.py::test_surface_canon_file_contract fails (file absent)
  - GREEN: canon-design-surface.md exists; table has a `Currency` column header; ≥5 data rows each with a source URL; contains "including but not limited to"; contains "never shown raw to the user"; cites the Task-1 research doc path; ≥1 risk-flag note present (e.g. "WCAG")
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "NEW references/canon-design-surface.md → Axis B: UI surface treatments … Phase-1 minimal seed of individual grounded entries (~5-6) … PLUS a currency stamp and risk flags"

## Task 3 — canon-design-visual.md becomes Axis-A-only (remove surface row + point to surface file)
- Description: Edit `canon-design-visual.md` to remove the single collapsed
  "Flat → skeuo → neumorphic → glassmorphic cycle" surface row (its expanded home
  is now the surface file), and add a header pointer noting this file is Axis A
  (cultural / graphic movements) and that UI surface treatments live in
  `canon-design-surface.md`. Must remain ≥14 rows so the existing
  `test_canon_references.py` parametrized contract still passes.
- Module: loom-product-principles/skills/product-principles/references/canon-design-visual.md
- Files touched: loom-product-principles/skills/product-principles/references/canon-design-visual.md, loom-product-principles/scripts/test_canon_references.py
- Context paths:
  - loom-product-principles/skills/product-principles/references/canon-design-visual.md
  - loom-product-principles/scripts/test_canon_references.py
- Acceptance:
  - RED: loom-product-principles/scripts/test_canon_references.py::test_visual_canon_is_axis_a_only fails (surface-cycle row still present / no surface-file pointer)
  - GREEN: canon-design-visual.md no longer contains the "glassmorphic cycle" surface row; contains a pointer string "canon-design-surface.md"; existing parametrized ≥14-entry + URL contract for canon-design-visual.md still passes
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "keep canon-design-visual.md as Axis A cultural/graphic movements (remove the collapsed … surface row)"

## Task 4a — SKILL.md Step-3: canon-audit list names both visual files + two axis-typed rounds
- Description: Edit `SKILL.md` Step 3's canon-audit reference list (~line 122-124)
  to name BOTH visual files (`canon-design-visual.md` for Axis A cultural +
  `canon-design-surface.md` for Axis B surface), and describe the visual lens
  running as TWO axis-typed candidate rounds, each reading ONLY its own file
  (contamination guard), each landing as its own version-pinned `## Anchors` row
  (Axis B optional-blank). SKILL.md side only; do not touch question-sets.md here.
- Module: loom-product-principles/skills/product-principles/SKILL.md
- Files touched: loom-product-principles/skills/product-principles/SKILL.md, loom-product-principles/scripts/test_product_principles_skill.py
- Context paths:
  - loom-product-principles/skills/product-principles/SKILL.md
  - loom-product-principles/scripts/test_product_principles_skill.py
- Acceptance:
  - RED: loom-product-principles/scripts/test_product_principles_skill.py::test_canon_audit_lists_surface_file fails
  - GREEN: SKILL.md Step-3 audit list names `canon-design-surface.md` alongside `canon-design-visual.md`; text states the visual lens runs as two axis-typed rounds each reading only its own file
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "Update the canon-audit reference list (SKILL.md ~122-124) to name both files" + "two separate candidate rounds … each round Reads ONLY its own file (contamination guard)"

## Task 4b — question-sets.md Design lane: two axis-typed rounds reading their own files
- Description: Edit `question-sets.md`'s Design lane (~line 49-56) so the visual
  lens is described as TWO axis-typed rounds — Axis A (cultural) reads
  `canon-design-visual.md`, Axis B (surface) reads `canon-design-surface.md` —
  each reading only its own file. question-sets.md side only.
- Module: loom-product-principles/skills/product-principles/references/question-sets.md
- Files touched: loom-product-principles/skills/product-principles/references/question-sets.md, loom-product-principles/scripts/test_question_sets.py
- Context paths:
  - loom-product-principles/skills/product-principles/references/question-sets.md
  - loom-product-principles/scripts/test_question_sets.py
- Acceptance:
  - RED: loom-product-principles/scripts/test_question_sets.py::test_design_lane_two_axis_rounds fails
  - GREEN: question-sets.md Design lane names both file names (`canon-design-visual.md` + `canon-design-surface.md`) and states the visual lens runs as two axis-typed rounds each reading only its own file (assert substrings for both file names + "cultural"/"surface" axis framing)
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "question-sets.md Design lane (line ~49-56) … the visual lens runs as TWO separate candidate rounds … each round Reads ONLY its own file"

## Task 5a — SKILL.md Step-3: visual-lens 3-5 carve-out + divergent-candidate concept
- Description: In `SKILL.md` Step 3, add an explicit carve-out that the VISUAL
  lens proposes 3-5 candidates (overriding the generic "2-3"), including 1-2
  deliberately divergent candidates that deviate from the user's stated stance but
  remain defensible against the Product Principles VALUES. Preserve the generic
  "2-3" for Product/Engineering (no global change). SKILL.md side only.
- Module: loom-product-principles/skills/product-principles/SKILL.md
- Files touched: loom-product-principles/skills/product-principles/SKILL.md, loom-product-principles/scripts/test_product_principles_skill.py
- Context paths:
  - loom-product-principles/skills/product-principles/SKILL.md
- Acceptance:
  - RED: loom-product-principles/scripts/test_product_principles_skill.py::test_visual_lens_3_5_carveout fails
  - GREEN: SKILL.md Step-3 states the visual lens uses 3-5 (carve-out over the generic 2-3) with a divergent/exploratory subset defensible against values; a guard assertion confirms the generic "2-3" wording for the non-visual sections still exists (no global bump)
- Dependencies: Task 4a completes first
- Independent: false
- Brief item covered: "Bump the visual-lens candidate count from 2-3 to 3-5 … Scope the 3-5 bump to the VISUAL lens only — do NOT touch Product/Engineering 2-3 counts"

## Task 5b — question-sets.md Design lane: 3-5 candidates + divergent-candidate detail
- Description: In `question-sets.md`'s Design lane, change "returns 2-3 candidates
  per lens" to 3-5 for the visual lens, and spell out the divergent-candidate
  concept: of the 3-5, deliberately include 1-2 that deviate from the stated
  stance (transparently labeled exploratory) yet stay defensible against the
  PRINCIPLES values (deviate on aesthetic expression, not values — a low-stimulus
  constitution still excludes Memphis). question-sets.md side only.
- Module: loom-product-principles/skills/product-principles/references/question-sets.md
- Files touched: loom-product-principles/skills/product-principles/references/question-sets.md, loom-product-principles/scripts/test_question_sets.py
- Context paths:
  - loom-product-principles/skills/product-principles/references/question-sets.md
- Acceptance:
  - RED: loom-product-principles/scripts/test_question_sets.py::test_visual_lens_offers_3_5_with_divergent fails
  - GREEN: the Design-lane text states the visual lens returns 3-5 candidates (not 2-3) and names an exploratory/divergent subset (1-2) that deviates from stance yet stays defensible against the PRINCIPLES values
- Dependencies: Task 4b completes first
- Independent: false
- Brief item covered: "Add the divergent-candidate concept: of the 3-5, deliberately include 1-2 that deviate from the user's stated stance … still defensible against the Product Principles VALUES"
