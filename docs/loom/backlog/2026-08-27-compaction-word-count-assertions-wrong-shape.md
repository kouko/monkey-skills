---
name: 2026-08-27-compaction-word-count-assertions-wrong-shape
description: Compaction word-count assertions are the wrong shape — drop the floor, move the ceiling to family level
status: closed
origin: 2026-08-27 #740 follow-up. Restoring the accidentally-deleted "Deletable lenses (Bitter Lesson)" section to loom-design/skills/completeness-critic/SKILL.md was blocked by loom-design/scripts/spec/test_completeness_critic_compaction.py's assert 2_803 <= words <= 3_203. That ceiling was calibrated on the premise that the #740 compaction was lossless — the premise the restore disproved. A guard whose calibration assumes the absence of the defect it is now blocking the fix for is the wrong shape. The ceiling was raised to 3_300 in that follow-up as a local unblock, not as the answer.
start: the next arc that touches more than two compaction tests at once — the reference-prose compaction arc (docs/loom/specs/2026-08-26-loom-reference-prose-compaction.md) is the likely carrier, since its BI-8 already replaces SKILL.md-only accounting with package-aware measurement.
---

- Start: the next arc that touches more than two compaction tests at once — the
  reference-prose compaction arc
  (docs/loom/specs/2026-08-26-loom-reference-prose-compaction.md) is the
  likely carrier, since its BI-8 already replaces SKILL.md-only accounting
  with package-aware measurement.
- Origin: 2026-08-27 #740 follow-up. Restoring the accidentally-deleted "Deletable
  lenses (Bitter Lesson)" section to
  loom-design/skills/completeness-critic/SKILL.md was blocked by
  loom-design/scripts/spec/test_completeness_critic_compaction.py's assert
  2_803 <= words <= 3_203. That ceiling was calibrated on the premise that the
  #740 compaction was lossless — the premise the restore disproved. A guard
  whose calibration assumes the absence of the defect it is now blocking the
  fix for is the wrong shape. The ceiling was raised to 3_300 in that
  follow-up as a local unblock, not as the answer.
- What: 32 of the 33 `test_*_compaction.py` files carry a two-sided word-count
  assertion. The two halves do not earn their place equally.
  - **Floor (drop it).** Each of these tests already carries ~20 presence
    assertions pinning load-bearing phrases by name. A word floor is a
    blunt proxy for "don't delete the important parts" that the presence
    assertions already do precisely, and it actively blocks legitimate
    later compaction.
  - **Ceiling (keep the job, change the level).** The ceiling is the only
    mechanical guard against regrowth — presence assertions cannot detect
    additions by construction, so without it the #740 savings decay
    silently across a few PRs. But per-file bands of roughly ±14%
    over-constrain individual files while missing what context economy
    actually cares about: the aggregate that loads on a path. Candidate
    shape — one family-level aggregate ceiling plus a repo-wide hard cap,
    with per-file bounds removed.
  - Whatever replaces it must state its calibration premise, so the next
    person who finds a defect underneath it knows the bound is
    re-openable rather than load-bearing.

- **2026-08-27: CLOSED by `fix/740-compaction-followups`.** The user's call was
  that a bound set as one refactor's implementation artifact should never have
  become a persistent test rule — a sharper reason than the raise-count test
  this entry originally proposed. All per-file word bounds are removed from all
  33 `test_*_compaction.py` files, floor and ceiling together, rather than the
  floor-drop-plus-family-ceiling this entry sketched. No family-level aggregate
  replaced them. For a `SKILL.md` the 4,500-word cap in
  `check-skill-structure.py` is the ceiling, and across the three loom plugins
  the tightest remaining headroom is 880 words at
  `finishing-a-development-branch/SKILL.md`. Two limits on that sentence, both
  measured: the cap is not repo-wide — the script takes one plugin directory
  per invocation and CI runs it on six, leaving most of the repo's `SKILL.md`
  files unchecked, and within those six the tightest is 404 words at
  `domain-teams/skills/copywriting-team/SKILL.md`. It is also not a ceiling for
  reference files at all: the script reads `skill_dir / "SKILL.md"` and
  measures nothing else, so
  `subagent-driven-development/references/conditional-operations.md` (812
  words) now has no size guard anywhere — the removed package-total bound was
  its only one. Content is carried instead by the presence and absence
  assertions this branch added, each mutation-checked against its rule's
  deletion or re-addition; those are content guards, not size guards. A
  family-level aggregate remains available if regrowth is ever measured;
  nothing in this branch forecloses it.
