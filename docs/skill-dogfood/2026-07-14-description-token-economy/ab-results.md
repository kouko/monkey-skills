# Description token economy — post-sweep A/B results (Task 8, post-merge leg)

- Date: 2026-07-14
- Repo state: branch `main`, HEAD `47bc1316` (merged PR #566)
- Deployed plugin versions in the device cache (probes see these):
  loom-discovery 0.1.1 / loom-pipeline 0.7.1 / loom-code 0.30.2 /
  loom-product-principles 0.9.1 — verified in
  `~/.claude/plugins/marketplaces/monkey-skills/*/.claude-plugin/plugin.json`
  before the run; deployed frontmatter descriptions spot-checked as the NEW
  swept text (499/478/495/332 chars for the four rewritten skills below).
- Method (plan Notes "Kickoff decision: A/B method" pin — IDENTICAL to
  baseline.md): harness `run` mode over the committed
  `baseline-subset.jsonl` (18 records, reused verbatim, `validate_corpus`
  re-run = 0 warnings), `--max-turns 4` (floor, trap #1),
  `filter_contaminated` before grading, `grade` mode EXACT/FAMILY.
  Claude CLI 2.1.208 (same as baseline). Each record run ONCE (no
  replicates; the pin's bar is comparative — same method both legs).
- Grading: aggregate via harness `grade` CLI; per-skill split computed by
  importing the harness's own `filter_contaminated` + `grade_record`
  (no grading logic re-implemented). Per-skill sums cross-check against
  the CLI aggregate: 11 EXACT / 5 FAMILY / 2 MISS / 0 OVER. ✓
- Raw run JSONL: `ab-run-raw.jsonl` (this directory — committed evidence,
  per the T6 lesson that scratchpad evidence dies).

## Contamination filter (trap #3)

| records run | discarded (contaminated) | unparsed_lines |
|---|---|---|
| 18 | **0** | 0 |

4 of the 18 kept records ended `error_max_turns` (baseline: 8) — per the
harness's trap #3 rule these are NOT contamination and are graded
normally.

## Per-skill A-leg vs B-leg

Baseline (A-leg) numbers transcribed from `baseline.md` (HEAD 4378c0d0);
B-leg from this run. Desc chars = deployed frontmatter description
collapsed to single-line text, same counting rule as baseline.

| Sweep target | n | A EXACT | A FAMILY | A MISS/OVER | B EXACT | B FAMILY | B MISS | B OVER | A→B combined | desc chars A→B |
|---|---|---|---|---|---|---|---|---|---|---|
| loom-discovery:using-loom-discovery | 3 | 3 | 0 | 0/0 | 3 | 0 | 0 | 0 | 100% → 100% | 1,065 → 499 |
| loom-discovery:user-insights | 3 | 0 | 3 | 0/0 | 0 | 1 | **2** | 0 | **100% → 33%** ⚠️ | 899 → 170 |
| loom-discovery:business-value | 3 | 0 | 3 | 0/0 | 0 | 3 | 0 | 0 | 100% → 100% | 616 → 230 |
| loom-pipeline:using-loom-pipeline | 4 | 4 | 0 | 0/0 | 4 | 0 | 0 | 0 | 100% → 100% | 1,019 → 478 |
| loom-pipeline:loom-memory | 4 | 4 | 0 | 0/0 | 4 | 0 | 0 | 0 | 100% → 100% | 974 → 495 |
| loom-product-principles:product-principles | 1 | 0 | 1 | 0/0 | 0 | 1 | 0 | 0 | 100% → 100% | 569 → 332 |
| **Total** | **18** | **11** | **7** | **0/0** | **11** | **5** | **2** | **0** | 18/18 → 16/18 | — |

**Acceptance bar (pin, verbatim): "no swept skill's EXACT+FAMILY combined
rate drops below its baseline."** Baseline combined = 100% everywhere, so
the bar = zero MISS and zero OVER. **The bar is NOT met: 2 MISS, both on
`loom-discovery:user-insights`.**

Secondary signal (EXACT/FAMILY shift, not bar-gated): no shift anywhere
except the two user-insights misses; every other skill reproduced its
baseline split exactly, including all three router-absorption patterns.

## The regression — records + mechanism

| # | expected | A-leg fired | B-leg fired | B verdict | query (truncated) |
|---|---|---|---|---|---|
| 6 | user-insights | using-loom-discovery | **loom-pipeline:loom-memory** | MISS | 在動手設計之前，幫我做一輪使用者需求研究：自由工作者記帳時真正的痛點… |
| 7 | user-insights | using-loom-discovery | **loom-pipeline:loom-memory** | MISS | Before we design anything, I want an evidence-backed map of what remote-team managers… |
| 8 | user-insights | using-loom-discovery | using-loom-discovery | FAMILY | 設計に入る前にユーザーインサイトをまとめたい。個人投資家がポートフォリオ… |

Mechanism (evidence-grounded reading, for the revert decision):

- The thief is **cross-family**: both misses first-fired
  `loom-pipeline:loom-memory`, whose deployed description carries
  "check prior experience **before loom work**" — the two lost probes
  both open with a "before we design / 在動手設計之前" clause. The
  harness grades the chronologically FIRST Skill call as the routing
  decision, so a "check memory first, then route" opening move counts
  as a MISS even if discovery work follows. (Probe sessions run with
  cwd inside this repo, which HAS `docs/loom/memory/README.md`, so
  loom-memory's CONDITIONAL gate is satisfied for the probes.)
- loom-memory's OLD description carried the same before-loom-work
  clause at baseline and did NOT absorb these records — what changed is
  the relative pull: the loom-discovery family's descriptions shrank
  (router 1,065→499; user-insights 899→170) and the baseline
  router-absorption of user-insights probes weakened. Record 8 (ja,
  contains the router's own ユーザーインサイト keyword) still routed to
  the family router; records 6/7 (zh/en paraphrases without a verbatim
  belt keyword) lost the tie-break to loom-memory.
- Implication for the pin's "revert that one description" rule: the
  regressed skill is `user-insights`, but its own 170-char description
  is not obviously the culpable edit — the failure is a two-body
  problem (discovery-side pull loss vs loom-memory's standing
  before-clause). Candidate remedies, cheapest first: (a) revert
  `user-insights` description to the pre-sweep text (the pin's literal
  rule), (b) restore the lost "使用者需求研究 / user research" belt
  keywords to `user-insights` or the router within band, (c) qualify
  loom-memory's before-clause. Any remedy needs a re-run of the same
  3 user-insights records to confirm. This file records the
  measurement; the revert rides the follow-up PR per the T8 post-merge
  amendment.

## Verdict

**FAIL (bar not met) — regressed skill: `loom-discovery:user-insights`**,
records #6 (zh) and #7 (en) of the 18-record subset (both baseline
FAMILY → B-leg MISS, absorbed cross-family by `loom-pipeline:loom-memory`).
All five other swept skills: combined rate preserved at 100%, zero OVER.
Per the pin: revert/fix is scoped to that ONE description — the other
five sweeps ship as-is.

## §remedy-experiment (post-merge, branch `fix/user-insights-description-recall`)

- Date: 2026-07-14. Remedy (b) tried first — targeted lexical restore
  within band — then measured via the pinned method before deciding.
- **Candidate text (217 rendered chars), verbatim**:
  `Map user needs with recorded evidence — an evidence-backed
  opportunity map made before we design anything. Use for: research
  user needs / needs research / 使用者需求研究 / 使用者洞察 /
  ユーザーインサイト. Worth-it checks → business-value.`
  (restores 使用者需求研究 = record #6's verbatim phrase, "research
  user needs", "evidence-backed" + "before we design anything" =
  record #7's opener, and 使用者洞察; keeps the business-value
  redirect.)
- **Cache-experiment disclosure**: the candidate was NOT deployed via a
  plugin release. It was temporarily copied over BOTH installed copies
  (`~/.claude/plugins/cache/monkey-skills/loom-discovery/0.1.1/skills/user-insights/SKILL.md`
  and `~/.claude/plugins/marketplaces/monkey-skills/loom-discovery/skills/user-insights/SKILL.md`
  — verified byte-identical to each other pre-experiment) for the
  probe run only, after backing both up. Probes therefore read the
  candidate; every other description was the deployed swept text.
- Method: identical pin (harness `run` `--max-turns 4` →
  `filter_contaminated` → `grade`; per-skill via the harness's own
  `grade_record`). 7-record probe = the committed subset's 3
  user-insights + 4 loom-memory records (guard: the fix must not steal
  loom-memory's 4/4 EXACT). Raw run JSONL: `remedy-run-raw.jsonl`
  (this directory). Contamination: 0 discarded, 0 unparsed; 5
  `error_max_turns` (graded normally per trap #3).
- **Result — candidate leg**:

  | skill | n | EXACT | FAMILY | MISS | OVER | combined |
  |---|---|---|---|---|---|---|
  | loom-discovery:user-insights | 3 | 0 | 1 | **2** | 0 | **1/3** |
  | loom-pipeline:loom-memory | 4 | 4 | 0 | 0 | 0 | 4/4 ✓ guard held |

  Per-record: #6 zh → loom-memory MISS (unchanged); #7 en →
  using-loom-discovery FAMILY (recovered); #8 ja → loom-memory MISS
  (**newly lost** — was FAMILY on the swept B-leg). Net 1/3 vs bar 3/3.
- **Verdict: FAIL** (bar = user-insights 3/3 combined AND loom-memory
  4/4 with 0 MISS/OVER; only the guard held). The 217-char thickness
  moved which records lose the tie-break to loom-memory's standing
  before-clause but did not clear it — evidence that mid-band tuning
  is unstable against the cross-family attractor.
- **Cache restored** byte-exact from backups regardless of outcome:
  `cmp` exit 0 on both the cache 0.1.1 copy and the marketplaces copy
  (deployed surface back to the swept 170-char text).
- **Remedy taken: pin-literal (step 6).** Candidate frontmatter edit
  reverted on the branch; the FULL pre-sweep 899-char description
  restored verbatim (frontmatter byte-identical to pre-sweep commit
  `4cf04014`; rendered length re-verified = 899). No second cache run —
  pin-literal is the guaranteed-baseline state (baseline leg: 3/3
  FAMILY via router absorption, loom-memory 4/4 EXACT).
