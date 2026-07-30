# Description-diet firing A/B — third band (493 chars), measured revert

- Date: 2026-07-30
- Repo state: branch `chore-description-diet`, `loom-discovery:user-insights`
  frontmatter description at 493 rendered chars (candidate, HEAD commit
  `cdd3cee1` before this revert) vs the deployed pin at 899 rendered chars
  (`main`, commit `4cf04014` lineage — the same pin-literal text restored
  by the 2026-07-14 remedy).
- Method: **pinned method re-used, identical to 2026-07-14**
  (`docs/skill-dogfood/2026-07-14-description-token-economy/ab-results.md`)
  — harness `run` mode, `--max-turns 4` (floor), `filter_contaminated`
  before grading, `grade` mode EXACT/FAMILY/MISS/OVER. Both legs run
  **same-day, in the CURRENT environment** (newer Claude CLI than
  2026-07-14, current deployed sibling descriptions, post-diet listing
  state on this branch) — not a re-use of old numbers.
- 7-record committed probe subset = the same guard-pair as 2026-07-14's
  remedy experiment: 3 `loom-discovery:user-insights` records (zh/en/ja)
  + 4 `loom-pipeline:loom-memory` records (the guard: a user-insights
  description edit must not steal loom-memory's 4/4 EXACT). Raw records:
  `probe-7.jsonl` (this directory).
- **Cache-experiment disclosure** (same pattern as 2026-07-14): Leg A ran
  against the deployed 899-char pin as installed. Leg B overlaid the
  493-char candidate onto the deployed cache copy for the probe run only,
  after backing up both the plugin-cache and marketplace copies
  (`backup-cache.md` / `backup-marketplace.md`, verified byte-identical to
  each other pre-experiment — kept in the working scratchpad, not
  committed here since they are pre-experiment deployed-pin backups, not
  new evidence). After the run the deployed copy was restored byte-exact
  from backup; `cmp` exit 0 on both copies.
- Raw run JSONL: `legA-899.jsonl` (leg A, 899-char pin) and
  `legB-493.jsonl` (leg B, 493-char candidate) — both committed here.

## Contamination filter

Both legs: 0 discarded (contaminated), 0 unparsed_lines. Several records
per leg ended `result_subtype: error_max_turns` — per the harness's trap
#3 rule these are graded normally (the `--max-turns 4` floor governs
turns available for research/delegation, not routing correctness).

## Results

| Leg | n | EXACT | FAMILY | MISS | OVER | combined |
|---|---|---|---|---|---|---|
| A (899-char pin) | 7 | 4 | 3 | 0 | 0 | **7/7** |
| B (493-char candidate) | 7 | 4 | 2 | **1** | 0 | **6/7** |

Per-skill split:

| skill | Leg A | Leg B |
|---|---|---|
| `loom-discovery:user-insights` (zh/en/ja, n=3) | 3 FAMILY (via `using-loom-discovery` router), 0 MISS | 2 FAMILY (zh, en) + **1 MISS (ja)** |
| `loom-pipeline:loom-memory` (n=4) | 4 EXACT, 0 MISS — guard held | 4 EXACT, 0 MISS — guard held |

## The regression — record + mechanism

| # | lang | expected | Leg A fired | Leg B fired | Leg B verdict |
|---|---|---|---|---|---|
| 3 | ja | user-insights | `using-loom-discovery` (FAMILY) | **`loom-pipeline:loom-memory`** | MISS |

Query (ja, record #3): "設計に入る前にユーザーインサイトをまとめたい。個人投資家が
ポートフォリオ管理で本当に必要としていることを、証拠付きで調査して整理して。"

This is the same cross-family absorption mechanism documented on
2026-07-14: the query opens with a "before we design" clause
(「設計に入る前に」), which ties into `loom-pipeline:loom-memory`'s
standing description clause "check prior experience **before loom
work**". At 493 chars the zh and en records (#1, #2) survived — unlike
the 170-char leg on 2026-07-14 where two of the three records died (zh,
en; the ja record #8 survived via the router at 170), and unlike the
217-char remedy candidate where zh and ja both died. At 493 chars a
**different** record (ja) dies instead. No band tested so far (170, 217,
493) has cleared zero-MISS; each band loses a different member of the
3-record set to the same attractor.

## Verdict

**FAIL** — bar (pin, unchanged since 2026-07-14: "no swept skill's
EXACT+FAMILY combined rate drops below its 899-char baseline," i.e. zero
MISS and zero OVER) not met. Leg A re-established the 899-char baseline
same-day (7/7, matching the 2026-07-14 baseline shape for this
guard-pair), so the Leg A vs Leg B comparison is internally valid despite
the environment delta (newer Claude CLI, current deployed sibling
descriptions, post-diet listing state) — the baseline was re-measured
now, not carried over from six weeks ago.

## Conclusion

The 899-char `user-insights` description is now measured to survive at
**three separate diet bands** where it has been tried against this
guard-pair — 170 (2026-07-14 sweep), 217 (2026-07-14 remedy), 493
(this run) — and fails all three. The failure mode is not a fixable
wording defect at any one band; it is that `loom-pipeline:loom-memory`'s
before-loom-work clause is a standing cross-family attractor for any
"before we design" phrasing, and shrinking `user-insights`'s own
description changes *which* record loses the tie-break without
clearing the miss. Mid-band lexical tuning near this attractor remains
unstable.

**Remedy: pin-literal revert** (this commit) — the full 899-char
description is restored verbatim on `loom-discovery`, matching the
2026-07-14 post-remedy state exactly (frontmatter byte-identical,
plugin.json version and CHANGELOG reverted to `main`). Any future
attempt to diet this one description needs this same same-day two-leg
A/B against the loom-memory guard pair, not static judgment about
wording — three independent bands have now falsified the "shorter is
safe if worded carefully" assumption.
