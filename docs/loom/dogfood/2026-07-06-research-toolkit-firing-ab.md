# research-toolkit triggering — firing A/B acceptance (2026-07-06)

**Verdict: PASS — candidate (branch) fires the research family on 3
records the baseline misses outright, with zero new over-fires; family
fire-rate rises 2/13 → 5/13.** Plan Task 9's GREEN condition ("B ≥ A
overall AND B fires research-toolkit on ≥3 records where A missed AND
zero new over-fires") is satisfied.

- Plan: `docs/loom/plans/2026-07-06-research-toolkit-triggering.md`
- Branch under test: `research-skill-r2` (descriptions rewrite + router,
  commits eb33b80d…0103a68c)
- Method: `loom-code/scripts/loom_firing_harness.py` `run_corpus()` via a
  driver on the `claude_bin` seam; wrappers pass `--model sonnet` +
  `--plugin-dir` (Arm A = origin/main via git worktree; Arm B = branch).
  Neutral empty cwd; branch-plugin load probed before the run
  (`docs/loom/memory/headless-branch-plugin-testing-recipe.md`). 32 runs,
  0 contaminated records (harness `_is_contaminated` filter).
- Corpus: `docs/loom/firing-corpus/research-asks.jsonl` (16 records:
  13 expected research-toolkit:*, 3 expected NONE; 中/日/英 mix;
  fairness-reviewed to be independent of both arms' description wording).
- Grader: driver-local research-family EXACT/FAMILY/OVER (the shipped
  grade mode is loom-family-specific — trap #4 discipline applied to
  `research-toolkit:*`).

## Per-criterion comparison

| Criterion | Arm A (main) | Arm B (branch) |
|---|---|---|
| EXACT fires (13 expected-fire records) | 2 | **4** |
| Family fires total (EXACT+FAMILY) | 2 | **5** |
| Over-fires on 3 expected=NONE records | 0 | **0** |
| Router-level ambiguous asks (2 records) | 0 (no router exists) | **2 EXACT** |
| Contaminated / dropped | 0 | 0 |

Diff rows (3 of 16) — all favor B:
1. 「幫我用研究工具查證這整份報告，我不確定是要…」(ambiguous, expected
   router): A=None, B=`using-research-toolkit` EXACT.
2. "I need to use the research tools to work through…" (ambiguous,
   expected router): A=None, B=`using-research-toolkit` EXACT.
3. 「多來源查證的深度研究報告…搬到 Codex 也能照跑」(expected
   deep-deep-research): A=None, B=`using-research-toolkit` (FAMILY — the
   router is the sanctioned on-ramp; its table routes onward to
   deep-deep-research).

Arm B's NONE-record fire of `loom-code:using-loom-code` on the coding ask
is correct non-research routing, not an over-fire (trap #4: expected=NONE
penalizes only research-family fires).

## Honest residual — what the branch does NOT fix

8 records still MISS in both arms identically (fact-check ×3,
deep-read ×3, cite-check 中文 ×1, deep-deep-research EN ×1). Two
non-exclusive causes, both environment-level and out of this branch's
scope:

1. **Description eviction** — with ~120 skills enabled, the host drops
   least-used skills' descriptions from the listing (official behavior;
   live-session inspection showed fact-check / deep-read / deep-deep
   evicted while cite-check survived — matching exactly which member
   skills fired here). Identical in both arms, so the A/B delta is
   attributable to the branch changes.
2. **Inline answering** — for short verification asks the model answers
   directly (observed: the 月球距離 record got a direct sourced answer),
   bypassing skill routing regardless of description quality.

Fixes for the residual live in the deferred machine-side options: shrink
the enabled-plugin surface / raise `skillListingBudgetFraction`
(SLASH_COMMAND_TOOL_CHAR_BUDGET), or invoke the router by name — the
user's global CLAUDE.md using-* routing line and `/using-research-toolkit`
both work independently of description survival, which is precisely the
mechanism the A/B shows working (router fired in B despite sibling
members staying evicted).

## Method notes / limits

- Single run per record, both arms sonnet; the 3 diff rows are consistent
  in direction with the mechanism (router presence + repositioned
  descriptions), so treated as signal — same adjudication stance as the
  2026-07-06 router-card A/B.
- `--allowedTools Skill` per the harness's run mode: WebSearch etc. are
  unavailable, which slightly inflates inline answering on verification
  asks; affects both arms equally.
- Raw outputs: `/private/tmp/research-firing-ab/out/{A,B}-research-asks.jsonl`
  (session-local; this table is the durable record).
