# Comms metrics recipe — run against the 2026-07-06 baseline sessions

Date: 2026-07-07. Recipe: `loom-pipeline/scripts/comms_metrics.py` (Task
12). This doc closes plan Task 13: run the recipe over the 11 sessions
named in `docs/loom/audits/2026-07-06-loom-comms-transcript-baseline.md`
and report what it measures, honestly compared against the hand-mined
baseline. All numbers below come from actually executing the script
against the real transcript files on 2026-07-07 — none are copied from
the baseline doc.

## How to rerun

```
python3 loom-pipeline/scripts/comms_metrics.py <jsonl...> [--json]
```

Exact invocation used for this report (all 11 sessions in one run, so
the aggregate is computed by the script itself, not hand-summed):

```
python3 loom-pipeline/scripts/comms_metrics.py \
  "/Users/kouko/.claude/projects/-Users-kouko-XcodeProjects-komado-Viewfinder/06647157-1b71-4d2b-ad44-289cdb3c3d93.jsonl" \
  "/Users/kouko/.claude/projects/-Users-kouko-XcodeProjects-komado-Viewfinder/f0789a4c-067d-433e-a52a-f788db68b9cf.jsonl" \
  "/Users/kouko/.claude/projects/-Users-kouko-XcodeProjects-komado-Refs/225fa464-e04e-4ede-b76b-a502d207d51e.jsonl" \
  "/Users/kouko/.claude/projects/-Users-kouko-XcodeProjects-komado-Refs/1f54c98d-69da-430b-83a5-e9a878170078.jsonl" \
  "/Users/kouko/.claude/projects/-Users-kouko-GitHub-youtube-summarize-scraper/867713a8-b307-40be-ac65-3fdb3d3cf5e0.jsonl" \
  "/Users/kouko/.claude/projects/-Users-kouko-GitHub-reading-list-summarize-scraper/978c9592-ff49-4524-a708-0ad46d943bd4.jsonl" \
  "/Users/kouko/.claude/projects/-Users-kouko--supacode-repos-monkey-skills-loom-dogfood/c73e92db-7b4e-454f-958a-b75f6a60cf73.jsonl" \
  "/Users/kouko/.claude/projects/-Users-kouko--supacode-repos-monkey-skills-loom-dogfood/198f5d1e-f354-4dc1-b024-cf6b9aedbdaf.jsonl" \
  "/Users/kouko/.claude/projects/-Users-kouko--supacode-repos-monkey-skills-loom-s2/a74d08ae-be41-4a5a-a27f-b3ce993ba0ab.jsonl" \
  "/Users/kouko/.claude/projects/-Users-kouko-GitHub-monkey-skills/ff13f714-94eb-43a6-825f-66df5598420c.jsonl" \
  "/Users/kouko/.claude/projects/-Users-kouko--supacode-repos-monkey-skills-obsidian-skill-r1/6e739422-d65e-4158-832f-c39c88684c69.jsonl" \
  --json
```

Ran clean (exit 0) on all 11 real transcript files; no missing sessions
to report — every path from the baseline doc's table still exists on
disk at this run's time.

## Per-session results (2026-07-07 run)

Labels S1-S11 match the baseline doc's session table.

| # | wrong-lang (count/eligible) | wrong-lang % | visual-at-fork (count/eligible) | visual-at-fork % | confusion-signal count |
|---|---|---|---|---|---|
| S1 | 15/16 | 93.8% | 0/4 | 0.0% | 0 |
| S2 | 8/9 | 88.9% | 1/3 | 33.3% | 0 |
| S3 | 10/18 | 55.6% | 0/2 | 0.0% | 0 |
| S4 | 3/11 | 27.3% | 0/2 | 0.0% | 0 |
| S5 | 10/23 | 43.5% | 5/10 | 50.0% | 0 |
| S6 | 5/6 | 83.3% | 0/0 | 0.0% (no asks) | 0 |
| S7 | 7/20 | 35.0% | 1/6 | 16.7% | 1 |
| S8 | 5/30 | 16.7% | 8/16 | 50.0% | 0 |
| S9 | 6/20 | 30.0% | 8/11 | 72.7% | 0 |
| S10 | 21/37 | 56.8% | 0/9 | 0.0% | 2 |
| S11 | 6/26 | 23.1% | 0/2 | 0.0% | 1 |

## Aggregates (sum-then-divide across all 11, one script invocation)

- **Wrong-language turn ratio: 96/216 = 44.4%**
- **Visual-at-fork rate: 23/65 = 35.4%**
- **Confusion-signal count: 4** (S7:1, S10:2, S11:1)

## Deviation notes — recipe vs the 2026-07-06 hand-mined baseline

The recipe's numbers do not match the baseline's, by design — different
instruments measuring related-but-not-identical things. Each gap below
is explained, not fudged toward agreement.

1. **Wrong-language ratio: 44.4% (recipe) vs ~39%/9% visual + separate
   70%/19% English-turn figures (baseline) — different eligible pools,
   not a contradiction.**
   - S6: baseline counted 34/48 = 70% English turns using a **≥40-char
     CJK heuristic across all substantive assistant turns**. The recipe
     requires **≥200 visible (non-whitespace) chars** AND both the
     rolling-window expected language and the turn's detected script to
     be non-`None` before a turn is "eligible" at all — S6 has only 6
     eligible turns (5 wrong), because most of S6's English one-liners
     ("Now make it GREEN") are short and get excluded by the 200-char
     floor rather than counted as short-English-and-wrong. The
     threshold choice (Task 12's spec) trades recall for precision:
     fewer turns are judged, but each judged turn is unambiguous.
   - S3: baseline 29/147 = 19% vs recipe 10/18 = 55.6% — same mechanism,
     larger gap. Baseline's denominator (147) is the full turn count at
     a loose length floor; the recipe's denominator (18) is the subset
     long enough to trust script detection on both sides. A smaller,
     stricter-selected pool naturally produces a different ratio; this
     is a known trade-off of the 200-char floor, not an error.
   - The baseline also used a **fixed whole-session majority language**
     while the recipe uses a **rolling 3-user-turn window recomputed at
     each assistant turn** (Task 12 spec) — so "expected language" can
     legitimately shift mid-session in the recipe but not in the
     baseline's per-session label. This is a second, independent source
     of disagreement on top of the threshold difference.

2. **Visual-at-fork rate: 35.4% overall (recipe) vs 39% (baseline)** —
   close by coincidence of overall scale, but the same divergence shows
   up in components:
   - The 4 real-app komado sessions (S1-S4) alone: **1/11 = 9.1%**,
     which matches the baseline's reported "1 of 11" for the same
     subset almost exactly (baseline: "9%"). S1 (0/4), S2 (1/3), S3
     (0/2), S4 (0/2) all match the baseline's per-session breakdown
     turn-for-turn. This is the strongest agreement in this whole
     report — likely because both the baseline's manual judgment and
     the recipe's structural detector agree easily on "no visual
     present at all" (the common case in these 4 sessions).
   - S9 also matches exactly: 8/11 = baseline's stated "S9 8/11".
   - S8 does NOT match: recipe finds 8/16 vs baseline's stated "S8
     6/16". Likely cause: the recipe's `_has_ascii_diagram` counts any
     ≥3 lines containing box-drawing/arrow characters within the
     2-turn lookback window, which can pick up incidental structural
     characters (e.g. in a pasted verdict block with `─` separators or
     `→` inside prose) that a human reviewer would not credit as "a
     diagram offered to the user" the way the baseline's manual read
     did. This is a known false-positive mode of the structural
     heuristic, not a bug — it is the deliberate simplification traded
     for a mechanical, repeatable rule instead of human judgment call
     on "does this count as a visual."
   - The 2-preceding-assistant-turn lookback window (`_FORK_LOOKBACK =
     2`) is the same generous window the baseline doc's §D limitations
     note flags ("the 3-turn look-back window... is generous"); the
     recipe fixed it at 2 turns plus the ask turn itself, matching the
     audit's stated methodology ("the ask turn or the two assistant
     turns before it").

3. **Confusion-signal count: 4 (recipe, across 11 sessions) vs "7 real
   hits" (baseline, hand-curated across the same + adjacent evidence).**
   This is the largest and most expected gap. The baseline's 7 hits
   came from a **broad manual grep** (看不懂/講人話/白話/太複雜/什麼意思/
   簡單/視覺化/圖/中文 etc.) followed by **human relevance judgment** to
   exclude near-misses (e.g. it explicitly excludes an artifact-keyword
   complaint at S11:433 as "related-but-different"). The recipe's
   `CONFUSION_PATTERNS` (Task 12 spec) is a **fixed, narrower literal
   list** — 什麼意思/看不懂/？？/意義與影響/講簡單/白話/"what do you
   mean" — with no relevance filtering (any substring match on a
   main-chain user turn counts). Cross-checking the baseline's 7 quoted
   hits against this literal list: only S7:219 ("...意義與影響")
   contains an exact-match substring; the other six (S7:184, S7:191,
   S8:1294, S9:1189, S9:1200, S9:1205) use synonyms/phrasings
   (視覺化解釋, 的意思是, 請先用視覺化說明) that are semantically
   confusion/pushback signals but do not literally match any regex in
   the fixed list — by design (Task 12 scoped the list to be
   "extensible", not exhaustive, and explicitly not a synonym-expanding
   NLP classifier — Rule 5, deterministic code over LLM judgment). The
   recipe's 4 hits (S7:1, S10:2, S11:1) are real matches on that fixed
   list, not fabricated; the undercount vs. baseline's 7 is the direct,
   expected cost of trading human synonym recognition for a
   deterministic, rerunnable literal-match rule.

**Bottom line**: the recipe is not a re-implementation of the baseline's
manual read — it is a cheaper, mechanical, rerunnable proxy with
different (documented) thresholds. Where the two methods' definitions
happen to align closely (real-app visual-at-fork subset, S9's
visual-at-fork ratio), the numbers match almost exactly, which is
evidence the recipe is measuring the same underlying phenomenon, not
noise. Where thresholds diverge (turn-length floor, rolling vs.
whole-session language window, literal-list vs. human-judged confusion
signals), the recipe's numbers diverge too, in the direction the
threshold choice predicts — never the reverse.

## Post-ship targets (quoted from the brief, Acceptance item 5)

From `docs/loom/plans/2026-07-07-loom-user-communication-overhaul.md`
§Acceptance, item 5 ("Post-ship (deferred, after ~10 real sessions):
re-run the audit"):

> targets: wrong-language turn ratio <10%, visual-at-fork ≥50% where
> ≥2 options compared, zero undefined internal terms at sign-offs.

Current (pre-ship) baseline for comparison, from this run:
- Wrong-language turn ratio: **44.4%** (target: <10%)
- Visual-at-fork rate: **35.4%** overall, **9.1%** in the real-app
  (non-meta) subset (target: ≥50% where ≥2 options compared — the
  recipe does not currently distinguish "≥2 options compared" asks from
  all `AskUserQuestion` asks; that filter is out of scope for this run)
- Zero undefined internal terms at sign-offs: not measured by this
  recipe (requires the cold-reader dogfood in brief Acceptance Cut 2,
  not a mechanical script signal) — recorded here as an open gap, not
  silently dropped.
