# Loom family skill compaction summary

Date: 2026-08-26

## Result

All 33 targeted loom skills were compacted. Counting the three pilot
references back in, total text fell from **85,975 to 66,381 words**:
**19,594 fewer words (22.8%)**. This is the extraction-adjusted result; it does
not claim moved prose as savings.

| Family | Skills | Net words, baseline → candidate | Net bytes, baseline → candidate |
|---|---:|---:|---:|
| loom-workflow | 9 | 23,433 → 18,086 (-5,347; 22.8%) | 159,577 → 122,225 (-37,352; 23.4%) |
| loom-design | 10 | 24,629 → 18,390 (-6,239; 25.3%) | 173,869 → 133,910 (-39,959; 23.0%) |
| loom-code | 14 | 37,913 → 29,905 (-8,008; 21.1%) | 271,757 → 220,771 (-50,986; 18.8%) |
| **Total** | **33** | **85,975 → 66,381 (-19,594; 22.8%)** | **605,203 → 476,906 (-128,297; 21.2%)** |

For comparison, the gross `SKILL.md`-only result is 85,975 → 64,494
(-21,481; 25.0%). The 1,887-word difference is exactly the content extracted
by the three pilots: distill-sessions 709, spec-expansion 366, and
subagent-driven-development 812 words.

## Method

Each skill used an immutable baseline, a RED-first static behavior oracle,
surgical `SKILL.md` compaction, package verification, and weak-model A/B on
both Claude Code `haiku` and Codex `gpt-5.6-luna`. Stronger models adjudicated
raw outputs only when deterministic comparison was inconclusive. Candidate
regressions were repaired and retested; host errors or missing skill activation
were excluded rather than counted as passes.

The compaction moves were deduplication, closed-list rules, shorter workflow
wording, consolidated tables, and removal of repeated rationale. References
did not change in the 30-skill family batches. The three pilots did extract
content, so their reference growth is explicitly included in the net result.

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
