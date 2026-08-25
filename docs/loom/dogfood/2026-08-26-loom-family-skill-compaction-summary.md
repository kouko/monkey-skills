# Loom family skill compaction summary

Date: 2026-08-26

## Result

All 33 targeted loom skills were compacted without moving removed prose into
references. Across loom-workflow, loom-design, and loom-code, `SKILL.md` text
fell from **85,975 to 64,536 words**: **21,439 fewer words (24.9%)**.

| Family | Skills | Words, baseline → candidate | Bytes, baseline → candidate |
|---|---:|---:|---:|
| loom-workflow | 9 | 23,433 → 17,377 (-6,056; 25.8%) | 159,577 → 116,857 (-42,720; 26.8%) |
| loom-design | 10 | 24,629 → 18,024 (-6,605; 26.8%) | 173,869 → 131,308 (-42,561; 24.5%) |
| loom-code | 14 | 37,913 → 29,135 (-8,778; 23.2%) | 271,757 → 215,006 (-56,751; 20.9%) |
| **Total** | **33** | **85,975 → 64,536 (-21,439; 24.9%)** | **605,203 → 463,171 (-142,032; 23.5%)** |

## Method

Each skill used an immutable baseline, a RED-first static behavior oracle,
surgical `SKILL.md` compaction, package verification, and weak-model A/B on
both Claude Code `haiku` and Codex `gpt-5.6-luna`. Stronger models adjudicated
raw outputs only when deterministic comparison was inconclusive. Candidate
regressions were repaired and retested; host errors or missing skill activation
were excluded rather than counted as passes.

The compaction moves were deduplication, closed-list rules, shorter workflow
wording, consolidated tables, and removal of repeated rationale. References
were not used as a hidden destination for removed text.

## Family evidence

- `docs/loom/dogfood/2026-08-25-loom-workflow-skill-compaction-dual-host-ab.md`
- `docs/loom/dogfood/2026-08-26-loom-design-skill-compaction-dual-host-ab.md`
- `docs/loom/dogfood/2026-08-26-loom-code-skill-compaction-dual-host-ab.md`
- Pilot evidence for one skill per family:
  `docs/loom/dogfood/2026-08-25-loom-skill-compaction-dual-host-ab.md`

## Final classification

**CLEAN after repairs.** Every targeted skill satisfies its static invariant
and size gate, every family package suite passes, and the accepted grounded
dual-host evidence shows no remaining candidate-only behavioral regression.
