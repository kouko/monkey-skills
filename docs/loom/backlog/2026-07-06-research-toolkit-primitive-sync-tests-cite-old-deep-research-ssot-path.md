---
name: 2026-07-06-research-toolkit-primitive-sync-tests-cite-old-deep-research-ssot-path
description: research-toolkit primitive-sync tests cite old deep-research SSOT path
status: open
origin: whole-branch review of research-skill-r2 (2026-07-06, docs/loom/dogfood/2026-07-06-research-toolkit-firing-ab.md branch)
start: next research-toolkit scripts/primitives touch, or as a tiny surgical PR
---

- Start: next research-toolkit scripts/primitives touch, or as a tiny
  surgical PR
- Origin: whole-branch review of research-skill-r2 (2026-07-06,
  docs/loom/dogfood/2026-07-06-research-toolkit-firing-ab.md branch)
- What: per-skill `test_primitives_present.py` files + sync headers still
  cite the SSOT path `research-toolkit/skills/deep-research/scripts/`,
  but the folder is now `deep-deep-research/` (pre-existing residue of
  the earlier rename; functional copies still verify byte-identity, only
  the cited path string is stale). Sweep the path strings, keep
  `scripts/sync-primitives.sh` + check-script-sync.yml semantics intact.
  ALSO sweep member SKILL.md body prose (fact-check ~L12-21, deep-read
  ~L11-18 and siblings) where bare "deep-research" still means the
  sibling deep-deep-research — since the using-research-toolkit router
  now reserves "deep-research" for the host BUILT-IN skill, the bare
  term is newly ambiguous to readers (2026-07-06 review-panel nit).
