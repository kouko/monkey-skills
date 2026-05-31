# Plan: `## Asking the user` three-gate redesign

Source brief: docs/code-toolkit/specs/2026-05-31-asking-the-user-three-gate-redesign.md
Total tasks: 3 (≤5)
Execution order: parallel-where-possible (Task 1 ∥ Task 2; Task 3 after both)
Plan-document-reviewer verdict: PASS (2026-05-31, 14/14)

## Task 1 — SDD `## Asking the user` three-gate rewrite
- Description: Rewrite the `## Asking the user` section in subagent-driven-development's
  SKILL.md from the flat 7-rule list into three gates — **① Whether to ask** (tier by
  reversibility × cost: reversible+inferable → do it, mention after, no per-step
  re-confirm under standing authorization; irreversible/outward/costly → always confirm;
  genuine taste/scope/un-inferable → ask per ②), **② What to bring** (a researched
  `(Recommended)` option, never an open-ended punt; less-familiar domain → more research),
  **③ How to phrase** (the existing phrasing rules MINUS old rule #5, now 6, verbatim, +
  the ✅❌ worked example + "calibration target" line, verbatim). Cite Horvitz CHI 1999 as
  the rationale anchor. Operative rule body uses plain language only — NO 確連報/察する/
  忖度/JA term in the rules themselves. Delete the standalone old rule #5 (absorbed into ②).
- Module: code-toolkit/skills/subagent-driven-development/SKILL.md
- Files touched: code-toolkit/skills/subagent-driven-development/SKILL.md
- Context paths:
  - docs/code-toolkit/specs/2026-05-31-asking-the-user-three-gate-redesign.md
  - code-toolkit/skills/subagent-driven-development/SKILL.md
- Acceptance:
  - RED: `grep -c "### ① Whether to ask" SKILL.md` returns 0; the standalone
    "5. **Research industry practice first**" rule still present in the flat list.
  - GREEN: three gate headers (`### ① Whether to ask`, `### ② What to bring`,
    `### ③ How to phrase`) present; gate ② names "(Recommended)" + "research" + cites
    Horvitz; gate ③ retains 6 phrasing rules + the ✅/❌ worked example + the "calibration
    target" closing line verbatim; old standalone rule #5 removed; `grep -E "確連報|察する|
    忖度|空気を読む" SKILL.md` returns 0 matches in the rule body; SKILL.md body still within
    the ~6,000-token (~4,500-word) budget (`wc -w`); validate-skill-folder hook passes.
- Dependencies: none
- Independent: true
- Brief item covered: Decision §"Restructure `## Asking the user` (both skills) … into
  three gates"; Smallest End State (Axis 3).

## Task 2 — requesting-code-review `## Asking the user` parallel update
- Description: Apply the same three-gate structure to requesting-code-review's
  `## Asking the user`: gate ① (same reversibility × cost tiering; the push-as-trigger
  confirm is the "always confirm" case), gate ② **lighter** (its asks are "fix now /
  defer / merge anyway" → lead with a `(Recommended)` option, not an open punt), gate ③
  (its existing 6 phrasing rules minus old #5, verbatim). MUST keep the existing boundary
  note that the `code-reviewer` agent's structured verdict stays machine-precise (do not
  loosen its R2 evidence-citation contract). Cite Horvitz CHI 1999. Plain-language rule
  body only — no JA term.
- Module: code-toolkit/skills/requesting-code-review/SKILL.md
- Files touched: code-toolkit/skills/requesting-code-review/SKILL.md
- Context paths:
  - docs/code-toolkit/specs/2026-05-31-asking-the-user-three-gate-redesign.md
  - code-toolkit/skills/requesting-code-review/SKILL.md
- Acceptance:
  - RED: `grep -c "### ① Whether to ask" SKILL.md` returns 0.
  - GREEN: three gate headers present; gate ② names "(Recommended)"; the verdict-structure
    boundary note ("these rules govern the relay TO the user ONLY … reviewer agent's output
    stays exact") is still present verbatim; gate ③ retains the phrasing rules + ✅/❌
    example; `grep -E "確連報|察する|忖度|空気を読む" SKILL.md` returns 0 in the rule body;
    token budget intact; validate-skill-folder hook passes.
- Dependencies: none
- Independent: true
- Brief item covered: Decision §"both skills"; Open Question 2 (code-review gets gate ① +
  lighter gate ②; verdict boundary preserved).

## Task 3 — Version bump + CHANGELOG entry with provenance line
- Description: Bump code-toolkit 0.12.0 → 0.13.0 (minor — additive behavioral guidance) in
  the plugin manifest, and add a CHANGELOG [0.13.0] entry describing the three-gate
  `## Asking the user` redesign across SDD + requesting-code-review, grounded in Horvitz
  (CHI 1999). The CHANGELOG entry MUST include a one-line provenance pointer to the brief's
  §Terminology Provenance (察する / 確連報 / 忖度 / Horvitz / confirmation-fatigue) so future
  edits can trace the original terms — per user directive that spec + commit/changelog both
  name the source terminology.
- Module: release metadata (plugin manifest + changelog — moves as one unit; no
  marketplace.json sync needed, it carries no per-plugin code-toolkit version)
- Files touched: code-toolkit/.claude-plugin/plugin.json, code-toolkit/CHANGELOG.md
- Context paths:
  - code-toolkit/.claude-plugin/plugin.json
  - code-toolkit/CHANGELOG.md
  - docs/code-toolkit/specs/2026-05-31-asking-the-user-three-gate-redesign.md
- Acceptance:
  - RED: `grep '"version": "0.12.0"' plugin.json` matches; no `[0.13.0]` heading in CHANGELOG.
  - GREEN: plugin.json version is `0.13.0`; CHANGELOG has a `[0.13.0]` entry naming the
    three-gate redesign + Horvitz grounding + a provenance line pointing to the brief's
    terminology table.
- Dependencies: Tasks 1, 2 complete first (the version + changelog name what changed).
- Independent: false
- Brief item covered: Decision (the shipped change); §Terminology Provenance (commit/
  changelog must name original terms).

## Notes
- Task 1 ∥ Task 2: both `Independent: true` with disjoint `Files touched` (two different
  SKILL.md files, no shared symbol) → genuine fan-out; SDD MAY dispatch both implementers
  in one parallel message (dogfoods [[project_code_toolkit_parallelism_well_tuned]]).
- Doc-only skills: code-toolkit has no pytest for SKILL.md, so acceptance is grep-diagnostic
  + validate-skill-folder hook + token-budget (`wc -w`), not a unit test. This is the
  intended RED/GREEN form for prose tasks here.
- Behavioral validation + exemption-polarity-flip guard ([[feedback_compressing_exemption_section_flips_polarity]])
  is a REVIEW-stage gate (SDD spec-/quality-reviewer + finishing review check that the 6
  phrasing rules still fire after being demoted under gate ③), not a separate shipped task —
  keeps the plan within scope. Brief Open Question 1.
- Task 3 touches 2 manifest/doc files as one logical release-metadata unit (repo convention
  for version-bump tasks); not a multi-module scope violation.
