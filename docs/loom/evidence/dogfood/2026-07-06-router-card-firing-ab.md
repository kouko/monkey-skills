# Router-card slim — firing A/B acceptance (2026-07-06)

**Verdict: PASS — candidate (router card) is non-inferior on every
criterion and strictly better on 3 records.** The user-mandated gate
(「firing 風險要驗證過才准剪」) is satisfied.

- Plan: `docs/loom/plans/2026-07-06-loom-code-router-card-slim.md`
- Branch under test: `feat/loom-code-router-card-slim`
- Method: `loom-code/scripts/loom_firing_harness.py` `run_corpus()` via a
  driver using the `claude_bin` seam; wrapper scripts pass
  `--model sonnet` (weak-tier gate — the audience the card must keep
  working for) + `--plugin-dir` ×5. Arm A = main @ 03d8312c (full
  SKILL.md embed) via a git worktree; Arm B = branch (2.1 KB router
  card). Neutral empty cwd (2026-07-04 method note 2). 56 runs total,
  0 harness errors. Injection provenance probed before the run:
  arm B context contains the card pull-pointer and no full-body
  markers; no double-injection from installed plugins.
- Corpora: `docs/loom/firing-corpus/{direct-ask,goal-oriented,near-miss}.jsonl`
  (10/8/10). Adjudication per the 2026-07-04 baseline report:
  `error_max_turns` records keep their valid `fired` field.

## Per-criterion comparison

| Criterion | Arm A (full embed) | Arm B (router card) |
|---|---|---|
| Near-miss over-fires (4× expected=NONE) | 0 | **0** |
| Coding-mandate fire on the bug-fix line | **MISS** (no fire) | ✅ `using-loom-code` |
| Direct asks routed (10 records) | 9/10 (completeness-critic ask missed) | **10/10** (hit the exact member) |
| Goal-oriented upstream routing (8) | 6× principles-first + 2× principles | 6× principles-first + 2× `using-loom-code` (= corpus `expected`; both patterns adjudicated correct in the 2026-07-04 baseline) |
| Refactor / test-covered-increment negative guards | no design-entry fire ✅ | no design-entry fire ✅ |

Diff rows (3 of 28): all three favor B —
1. direct-ask「spec 草稿 adversarial completeness critique」: A=None,
   B=`loom-spec:completeness-critic` (exact member fire).
2. near-miss「登入功能 bug…500 錯誤」: A=None, B=`loom-code:using-loom-code`
   (the coding mandate working).
3. goal-oriented habit-tracker / 報名網站: A=principles, B=`using-loom-code`
   (matches corpus `expected`; upstream recommendation still reachable via
   brainstorming Axis 0 — same adjudication as baseline record #4).

## Why B ≥ A (mechanism, not luck)

Current Claude Code truncates oversized hook additionalContext to a ~2 KB
preview + persisted file. Arm A's 11 KB embed therefore delivered only
the first ~2 KB of the router (mandate + rules 1-2) — rules 4-5 and the
member map never reached the model at session start. The 2.1 KB card
arrives whole. The slim is not a trade-off against firing quality; it
removes an unreliable, truncation-shaped delivery. (Wire cost also drops
34 KB → ~6.5 KB ×3 keys; consumed context 11 KB → 2.1 KB per
startup/clear/compact in every project — ~1.9M input tokens/30d saved,
`docs/harness-audit/2026-07-06-a-harness-diagnosis.md` #1.)

## Method notes / limits

- Both arms sonnet: isolates the card effect from model drift vs the
  2026-07-04 baseline (which ran the then-default model).
- Single run per record (no repeats); the 3 diff rows are consistent in
  direction with the truncation mechanism, so treated as signal, not noise.
- Raw outputs: `/private/tmp/loom-firing-ab/out/{A,B}-*.jsonl` (session-local;
  this table is the durable record).
