---
name: 2026-07-13-skill-creator-advance-case-c-gate-inheritance-ambiguity
description: skill-creator-advance Case (c) gate inheritance ambiguity
status: open
origin: refactor/skill-creator-advance-token-slim equivalence runs (2026-07-13): all four independent runners (2 baseline + 2 candidate) flagged that the "Improving an Existing Skill" router's Case (c) structural-rewrite flow does not explicitly inherit Pre-Creation Gates 1/2, and there is no documented pattern for "shared library across split skills" despite the flat-folder rule making it a natural ask. Judge 3 marked the resulting gate-machinery divergence "uncertain" — pre-existing ambiguity, present in both pre- and post-refactor versions.
start: next structural redesign touching skill-dev-toolkit/skills/ skill-creator-advance/SKILL.md (behavior change → route through skill-creator-advance's own redesign path, NOT skill-refactor).
---

- Start: next structural redesign touching skill-dev-toolkit/skills/
  skill-creator-advance/SKILL.md (behavior change → route through
  skill-creator-advance's own redesign path, NOT skill-refactor).
- Origin: refactor/skill-creator-advance-token-slim equivalence runs
  (2026-07-13): all four independent runners (2 baseline + 2 candidate)
  flagged that the "Improving an Existing Skill" router's Case (c)
  structural-rewrite flow does not explicitly inherit Pre-Creation
  Gates 1/2, and there is no documented pattern for "shared library
  across split skills" despite the flat-folder rule making it a natural
  ask. Judge 3 marked the resulting gate-machinery divergence
  "uncertain" — pre-existing ambiguity, present in both pre- and
  post-refactor versions.
- What: decide whether Case (c) should explicitly run Gates 1/2
  (worth-it / smallest-end-state) before drafting a split, and add a
  documented shared-code-across-skills pattern (candidates surfaced by
  the runs: third skill via delegation contract / plugin-root module /
  duplicate-with-SSOT-note).
