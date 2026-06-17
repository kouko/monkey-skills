# Plan: design-critic — writer≠judge omission critic for the design surface

Source brief: docs/interface-design-toolkit/specs/2026-06-17-design-critic.md
Total tasks: 5
Critical-path depth: 4 (T1→T3→T4→T5; T2 parallel with T1)
Execution order: parallel-where-possible (T1 ∥ T2; then T3; then T4; then T5)
Plan-document-reviewer verdict: PASS (2026-06-17, 14/14 — TDD test-first ordering sound; DAG depth 4; oracles specific)

Notes:
- New skill, mirrors `spec-toolkit:completeness-critic` (SKILL.md prose panel). TDD applies:
  the skill IS testable via a structural grep-test (template:
  `spec-toolkit/scripts/test_completeness_critic_skill.py`) — so the RED test (T1) is written
  BEFORE the SKILL.md (T3), per tdd-iron-law.
- The plugin-coherence CI gate only flags STALE slugs → a NEW skill needs NO plugin.json /
  marketplace description edit (confirmed via scripts/check-plugin-description-skill-coherence.py).
  So no marketplace task; T5 just confirms the existing manifest/marketplace tests still pass.
- Lenses grounded in Nielsen's 10 heuristics × the 7 UX dims — cited in a references file (T2),
  summarized in the SKILL (T3). Do NOT invent a fresh checklist.
- Final verification: package suite green (T5) + a dogfood + the brief's redundancy comparison
  against completeness-critic (orchestrator-run after the suite passes; recorded in the brief's
  Open Questions, not a task-level oracle).

## Task 1 — RED: structural grep-test for design-critic SKILL.md
- Description: Create `interface-design-toolkit/scripts/test_design_critic_skill.py` mirroring
  `spec-toolkit/scripts/test_completeness_critic_skill.py`. Assert design-critic's load-bearing
  phrases: YAML frontmatter `name: design-critic` + a description that triggers on design
  review / blind-spot / omission / heuristic; the writer≠judge panel + loop-until-dry + re-seed;
  the multi-lens panel with the 5 design lenses' keywords (render-state empty/loading/error/success;
  dead-end + exit + undo; navigation reachability + entry; error prevention/recovery; modality +
  a11y); grounding in Nielsen heuristics; the surface-not-behavioral boundary; the mandatory
  non-empty blind-spots rail; the conditional PRINCIPLES.md omission lens. This test FAILS now
  (no SKILL.md yet) — that is the RED state.
- Module: interface-design-toolkit/scripts
- Files touched: interface-design-toolkit/scripts/test_design_critic_skill.py
- Context paths:
  - spec-toolkit/scripts/test_completeness_critic_skill.py (the template to mirror)
  - docs/interface-design-toolkit/specs/2026-06-17-design-critic.md (brief — the lens set)
- Acceptance:
  - RED: `PYTHONDONTWRITEBYTECODE=1 python -m pytest interface-design-toolkit/scripts/test_design_critic_skill.py -q`
    fails (collection error / assertion fail — SKILL.md absent).
  - GREEN (of THIS task): the test file exists, is collected, and its failures are
    SKILL.md-absent assertions (not syntax errors) — i.e. it's a valid failing test ready for T3.
- Dependencies: none
- Independent: true
- Brief item covered: "reuses completeness-critic's proven panel pattern … design-surface lenses
  grounded in canon … mandatory non-empty blind-spots honesty rail."

## Task 2 — references/design-heuristics.md (Nielsen × 7-dim canon grounding)
- Description: Create `interface-design-toolkit/skills/design-critic/references/design-heuristics.md`
  mapping **Nielsen's 10 usability heuristics** to the **7 UX dimensions**
  (`interaction-flows/references/ux-flow-checklist.md`) and to the 5 load-bearing design lenses,
  with citations (Nielsen & Molich heuristic evaluation; cite the canon, do not invent). This is
  the lens-critic's reference (loaded on demand), keeping SKILL.md lean.
- Module: interface-design-toolkit/skills/design-critic
- Files touched: interface-design-toolkit/skills/design-critic/references/design-heuristics.md
- Context paths:
  - interface-design-toolkit/skills/interaction-flows/references/ux-flow-checklist.md (the 7 dims)
  - docs/interface-design-toolkit/specs/2026-06-17-design-critic.md (brief — the 5 lenses)
- Acceptance:
  - RED: `test -f interface-design-toolkit/skills/design-critic/references/design-heuristics.md` → absent.
  - GREEN: the file exists, names all 10 Nielsen heuristics, maps them to the 5 lenses + 7 dims,
    cites the canon (Nielsen/Molich), and is single-level under references/ (flat-skill).
- Dependencies: none
- Independent: true
- Brief item covered: "Lenses = Nielsen's 10 usability heuristics intersected with the existing 7
  UX dimensions … NOT a freshly invented checklist."

## Task 3 — design-critic SKILL.md (panel skill; makes T1 GREEN)
- Description: Create `interface-design-toolkit/skills/design-critic/SKILL.md` — the writer≠judge
  panel skill mirroring completeness-critic: YAML frontmatter (name + trilingual-ish description
  triggering on design review/blind-spots/heuristic-evaluation); executor model; honesty rails;
  the multi-lens fresh-context panel (the 5 design lenses, each with a persona + input view, citing
  references/design-heuristics.md); loop-until-dry (K=2); union+dedup+rank consolidation; mandatory
  non-empty blind-spots section; the surface-not-behavioral boundary (flag here, fan-out there);
  the conditional PRINCIPLES.md omission lens (N/A no-op when absent); the Bitter-Lesson
  deletable-lens note. ≤~6k tokens, flat-skill.
- Module: interface-design-toolkit/skills/design-critic
- Files touched: interface-design-toolkit/skills/design-critic/SKILL.md
- Context paths:
  - spec-toolkit/skills/completeness-critic/SKILL.md (pattern to mirror — panel/loop/blind-spots)
  - interface-design-toolkit/skills/design-critic/references/design-heuristics.md (T2 — cite it)
  - interface-design-toolkit/scripts/test_design_critic_skill.py (T1 — the contract to satisfy)
  - docs/interface-design-toolkit/specs/2026-06-17-design-critic.md (brief)
- Acceptance:
  - RED: T1's test is failing on SKILL.md-absent assertions.
  - GREEN: `PYTHONDONTWRITEBYTECODE=1 python -m pytest interface-design-toolkit/scripts/test_design_critic_skill.py -q`
    PASSES; SKILL.md is ≤~6k tokens; flat-skill (only references/ single-level); frontmatter
    description ≤1024 chars (Codex limit).
- Dependencies: Tasks 1, 2 complete first
- Independent: false
- Brief item covered: "A new skill interface-design-toolkit:design-critic that reuses
  completeness-critic's proven panel pattern … with design-surface lenses grounded in canon."

## Task 4 — router wiring: using-interface-design-toolkit adds the review step
- Description: Edit `interface-design-toolkit/skills/using-interface-design-toolkit/SKILL.md` to add
  a review step that routes to `design-critic` AFTER `design-system` + `interaction-flows` have
  emitted their artifacts (the router currently has no critic/review step). Reference the skill by
  name; note it is the design station's writer≠judge gate before handing ui-flows.md to
  spec-expansion.
- Module: interface-design-toolkit/skills/using-interface-design-toolkit
- Files touched: interface-design-toolkit/skills/using-interface-design-toolkit/SKILL.md
- Context paths:
  - interface-design-toolkit/skills/using-interface-design-toolkit/SKILL.md (router; insertion point)
  - interface-design-toolkit/skills/design-critic/SKILL.md (T3 — the skill name to cite)
- Acceptance:
  - RED: `grep -ci 'design-critic' interface-design-toolkit/skills/using-interface-design-toolkit/SKILL.md` = 0.
  - GREEN: the router names `design-critic` as the post-emit review step; flat-skill + token budget intact.
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "Router wiring: using-interface-design-toolkit routes to design-critic AFTER
  design-system + interaction-flows emit."

## Task 5 — verify package suite green (manifest/marketplace tolerate the new skill)
- Description: Run the full `interface-design-toolkit/scripts/` pytest suite. Confirm the new skill
  does not break `test_plugin_manifest.py` / `test_marketplace_entry.py` (if either hardcodes a
  skill count/list rather than globbing, update it to include design-critic — minimal, only if it
  fails). Confirm `python scripts/check-plugin-description-skill-coherence.py`-equivalent stays
  clean (no stale slug introduced).
- Module: interface-design-toolkit/scripts
- Files touched: interface-design-toolkit/scripts/test_plugin_manifest.py OR test_marketplace_entry.py (ONLY if a count/list assertion fails; otherwise none)
- Context paths:
  - interface-design-toolkit/scripts/test_plugin_manifest.py
  - interface-design-toolkit/scripts/test_marketplace_entry.py
- Acceptance:
  - RED: full suite may fail IF a manifest test hardcodes the skill set (3 → 4).
  - GREEN: `PYTHONDONTWRITEBYTECODE=1 python -m pytest interface-design-toolkit/scripts/ -q`
    is fully green (all prior tests + the new test_design_critic_skill.py).
- Dependencies: Tasks 3, 4 complete first
- Independent: false
- Brief item covered: "Build interface-design-toolkit:design-critic as a new skill" (the skill must
  ship green within the existing package suite + CI gates).
