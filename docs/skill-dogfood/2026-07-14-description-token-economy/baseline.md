# Description token economy — pre-sweep firing baseline (Task 6)

- Date: 2026-07-14
- Repo state: branch `feat/description-token-economy`, HEAD `4378c0d0`
  (post-Task-5 corpus, CURRENT pre-sweep descriptions)
- Method (plan Notes "Kickoff decision: A/B method" pin, followed verbatim):
  `loom-code/scripts/loom_firing_harness.py` headless — `validate_corpus`
  (0 warnings on the subset), `run` mode `--max-turns 4` (= floor, trap #1),
  `filter_contaminated` before grading, `grade` mode EXACT/FAMILY.
  Claude CLI 2.1.208. Each record run ONCE (no replicates; the pin's bar is
  comparative — same method both legs).
- Corpus: `docs/loom/firing-corpus/direct-ask.jsonl` (26 records), filtered
  to the 18 records whose `expected` is a Task 7a–7d sweep target (the
  harness `run` mode accepts any corpus path, so the 8 non-target records
  were not burned). Subset reproducible: `expected ∈` the six covered
  targets listed below; record order preserved.
- Grading: aggregate via harness `grade` CLI; per-skill split computed by
  importing the harness's own `filter_contaminated` + `grade_record`
  (no grading logic re-implemented). Per-skill sums cross-check against
  the CLI aggregate: 11 EXACT / 7 FAMILY / 0 MISS / 0 OVER. ✓

## Contamination filter (trap #3)

| records run | discarded (contaminated) | unparsed_lines |
|---|---|---|
| 18 | **0** | 0 |

8 of the 18 kept records ended `error_max_turns` — per the harness's trap #3
rule these are NOT contamination (the skill fired, the session kept working
past the turn cap) and are graded normally.

## Per-skill baseline — corpus-covered sweep targets

| Sweep target | n | EXACT | FAMILY | MISS | OVER | EXACT+FAMILY | desc chars* |
|---|---|---|---|---|---|---|---|
| loom-discovery:using-loom-discovery | 3 | 3 | 0 | 0 | 0 | 3/3 (100%) | 1,065 |
| loom-discovery:user-insights | 3 | 0 | 3 | 0 | 0 | 3/3 (100%) | 899 |
| loom-discovery:business-value | 3 | 0 | 3 | 0 | 0 | 3/3 (100%) | 616 |
| loom-pipeline:using-loom-pipeline | 4 | 4 | 0 | 0 | 0 | 4/4 (100%) | 1,019 |
| loom-pipeline:loom-memory | 4 | 4 | 0 | 0 | 0 | 4/4 (100%) | 974 |
| loom-product-principles:product-principles | 1 | 0 | 1 | 0 | 0 | 1/1 (100%) | 569 |
| **Total** | **18** | **11** | **7** | **0** | **0** | **18/18** | — |

\* CURRENT description length at HEAD 4378c0d0, frontmatter `description`
collapsed to single-line text before counting (the plan's awk counts —
1,081/927/632 etc. — count raw YAML bytes incl. indentation, hence the
small deltas; not load-bearing for grading).

### Reading the FAMILY rows

Every FAMILY verdict is the family ROUTER absorbing a member-skill query
(known router-asymmetry pattern): all 3 `user-insights` and all 3
`business-value` records fired `using-loom-discovery`; the 1
`product-principles` record fired `using-loom-product-principles`. No
cross-family leakage, no silence.

**B-leg acceptance bar (pin, verbatim): "no swept skill's EXACT+FAMILY
combined rate drops below its baseline."** Baseline combined = 100% for
every covered skill, so the post-sweep leg must produce zero MISS and zero
OVER on these 18 records. The EXACT/FAMILY split above is the secondary
signal: the pin's bar does not gate on it, but a post-sweep EXACT→FAMILY
shift (or the reverse) is worth recording in results.

## Per-record detail (evidence for the B-leg diff)

| # | expected | fired | verdict | subtype | query (truncated) |
|---|---|---|---|---|---|
| 1 | product-principles | using-loom-product-principles | FAMILY | success | 我們要幫這個新產品訂一份 PRINCIPLES.md，包含北極星跟 3 到 7 條可證偽… |
| 2 | using-loom-pipeline | using-loom-pipeline | EXACT | success | 幫我把整個 loom pipeline 從頭跑一遍… |
| 3 | using-loom-discovery | using-loom-discovery | EXACT | success | 我有一個 side project 的想法，但連要給誰用都還說不清楚… |
| 4 | using-loom-discovery | using-loom-discovery | EXACT | error_max_turns | I have a product idea but honestly can't articul… |
| 5 | using-loom-discovery | using-loom-discovery | EXACT | success | 新しいプロダクトのアイデアがあるけど、需要の調査と価値の見極め… |
| 6 | user-insights | using-loom-discovery | FAMILY | error_max_turns | 在動手設計之前，幫我做一輪使用者需求研究… |
| 7 | user-insights | using-loom-discovery | FAMILY | error_max_turns | Before we design anything, I want an evidence-ba… |
| 8 | user-insights | using-loom-discovery | FAMILY | error_max_turns | 設計に入る前にユーザーインサイトをまとめたい… |
| 9 | business-value | using-loom-discovery | FAMILY | success | 我週末能寫 code 的時間很有限，這個瀏覽器外掛的點子… |
| 10 | business-value | using-loom-discovery | FAMILY | success | Is this CLI tool idea actually worth my time to… |
| 11 | business-value | using-loom-discovery | FAMILY | success | この自動化ツールを作って公開する価値が本当にあるのか… |
| 12 | using-loom-pipeline | using-loom-pipeline | EXACT | success | Take this feature idea and drive it through the… |
| 13 | using-loom-pipeline | using-loom-pipeline | EXACT | success | 這個功能改動幫我自動實作到底：從產品原則一路推進… |
| 14 | using-loom-pipeline | using-loom-pipeline | EXACT | error_max_turns | この機能変更を、原則から設計、仕様、実装まで… |
| 15 | loom-memory | loom-memory | EXACT | error_max_turns | 這次 debug 學到的教訓很值得留下來… |
| 16 | loom-memory | loom-memory | EXACT | error_max_turns | Before I start this loom refactor, check the rep… |
| 17 | loom-memory | loom-memory | EXACT | error_max_turns | docs/loom/memory 的記憶庫好像累積了不少舊條目… |
| 18 | loom-memory | loom-memory | EXACT | success | リポジトリの loom 記憶ストアが古くなってきたので… |

(Skill ids abbreviated to member name; plugin prefixes as in the per-skill
table. Raw run JSONL lived in the session scratchpad — this table is the
durable record.)

## No corpus coverage — A/B not applicable

The following Task 7c sweep targets (loom-code member skills) have ZERO
direct-ask records (`expected == <skill>` count = 0). They route via
`loom-code:using-loom-code` and never had per-skill corpus records; no
baseline is measurable and none is fabricated here. **Task 7c is guarded
by review-side trigger-word preservation instead** (per Task 6 dispatch).

- loom-code:ui-verification
- loom-code:subagent-driven-development
- loom-code:brainstorming
- loom-code:requesting-code-review
- loom-code:dispatching-parallel-agents
- loom-code:verification-before-completion
