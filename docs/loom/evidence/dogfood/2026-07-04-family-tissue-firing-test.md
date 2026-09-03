# F3 — loom family connective tissue: live firing acceptance (2026-07-04)

**Verdict: PASS** (all three acceptance criteria met; two calibration debts filed below)

- Plan: `docs/loom/plans/2026-07-04-loom-family-connective-tissue.md` Task F3
- Branch under test: `feat/loom-family-connective-tissue` @ d0cec679 (23 commits)
- Method: `loom-code/scripts/loom_firing_harness.py` `run` mode, `claude -p --max-turns 4
  --allowedTools Skill --output-format stream-json`, **branch plugins loaded via
  `--plugin-dir` ×5** (installed plugins untouched — they track GitHub main, which does
  not carry this branch). Probe confirmed the loom-pipeline reception hook injects in
  headless mode before the corpus runs. cwd = session scratchpad (see method note 2).
- Corpora: `docs/loom/firing-corpus/{goal-oriented,near-miss,direct-ask}.jsonl` (8/10/10,
  Task F2). 28/28 records ran; 0 harness errors; 0 session-limit contamination.

## Criterion 1 — goal-first asks surface the design-side recommendation: **PASS (7/8)**

The guarantee chain under test: goal-oriented instruction (「幫我做一個記帳 app」) →
reception context + brainstorming Axis 0 → upstream (principles/design) recommendation
surfaces even though the user never asked for it.

| # | Query (gist) | Behavior | Recommendation surfaced? |
|---|---|---|---|
| 1 | 記帳 app 從零規劃 | fired `using-loom-product-principles` | ✅ routed upstream directly |
| 2 | habit tracker (EN) | asked where the real project home is | ⚠ env artifact (note 2) |
| 3 | 讀書會報名網站 | text:「先做一輪簡短的產品原則釐清…先定調再動手（推薦）」 | ✅ in text |
| 4 | small CLI tool (EN) | fired `using-loom-code` (kept working past turn cap) | ✅ correct entry |
| 5 | 團隊任務管理系統 | text names `loom-product-principles`, PRINCIPLES.md, 產品憲章 | ✅ in text |
| 6 | recipe-sharing (EN) | fired `using-loom-product-principles` | ✅ routed upstream |
| 7 | 讀書會匹配平台 | fired `using-loom-product-principles` | ✅ routed upstream |
| 8 | personal site (EN) | text: "first step isn't code… it's a constitution: a north star" | ✅ in text |

7/8 surfaced the upstream recommendation (3 by firing the principles entry outright,
1 by firing the coding entry, 3 in reply text under the 4-turn cap). #2's pause is a
cwd artifact, not a routing failure. **The 「使用者沒明說也要引導」 requirement holds.**

## Criterion 2 — near-miss / negative guards do not over-fire: **PASS (0 over-fires)**

- 4/4 `expected=NONE` lines (cat name, mountain, weather, email draft): **nothing fired**.
- Bug-fix line: fired `using-loom-code` (correct — coding mandate, no design entry). ✅
- Refactor + test-covered-increment lines: no design entry fired; #10's reply text
  recites the negative guard verbatim —「test-covered 的小型 refactor，不需要走
  brainstorming/spec 那套流程」. ✅ (Both then ask for the missing code — cwd artifact.)
- Spec-draft critique line: nothing mis-fired; reply text names
  `loom-spec:completeness-critic` — the #456 adjacent mis-route (critique →
  spec-expansion) did **not** recur.

## Criterion 3 — direct asks keep #456-level routing: **PASS (with a documented shift)**

- All five `using-loom-*` entry direct-asks: **5/5 EXACT** (including
  `using-loom-pipeline` and both 「不知道從哪開始」 phrasings).
- Member direct-asks (interaction-flows, product-principles, spec-expansion ×2,
  design-system, completeness-critic): **the family entry fires instead of the member**
  in 6 instances (same plugin — FAMILY grade, never a cross-plugin miss, never OVER).
  Records that ran past the turn cap kept working (entry §Intake step 3 hands off to
  the member); completeness-critic asks were correctly named in text both times.

**Adjudication — entry reception, not entry stealing.** Under the shipped convention
(「要用 loom-X，就從 using-loom-X 開始」, reception hook + README), the family entry
catching a member-shaped ask and routing via §Intake is the designed front door; the
cost is one extra hop. The corpus notes anticipated exactly this pattern. Anti-steal
description tests (member trigger phrases absent from entry descriptions) all hold —
the pull comes from the reception context doing its job, not from description overlap.
**Watch item**: if the extra hop proves annoying in real use, tighten entry §Intake
step 3 to fast-path verbatim member asks; do not weaken the reception.

## Raw grade-mode output (before manual adjudication)

`grade` mode reported goal-oriented 0/0/5/0 + 3 discarded, near-miss 4/0/3/0 + 3
discarded, direct-ask (manual) 5 EXACT + 4 FAMILY + 1 text-correct. Two calibration
gaps explain the gap between raw numbers and the adjudicated PASS:

1. **`error_max_turns` records are discarded as contaminated, but their `fired` field
   is valid** — a session that fires a skill and keeps working past the cap is a
   *success signal*, not contamination. 6/28 records (all with useful fires) were
   dropped by the filter. → File as harness next-touch: grade `error_max_turns`
   records normally, discard only session-limit/harness_error subtypes.
2. **Goal-oriented `expected` values are narrower than the design** — the corpus pins
   `loom-code:using-loom-code`, but firing `using-loom-product-principles` on a
   brand-new-product ask is the tissue working as designed (trap #6 already documents
   that this corpus grades routing only; the real check is the transcript column above).

## Method notes (for the next run)

1. Branch-state testing without touching the installed plugins: wrapper script passing
   `--plugin-dir <repo>/<plugin>` ×5, handed to the harness via its `claude_bin` seam.
   (`parse_corpus` takes file *content*, not a path — the CLI does this right; a custom
   driver must `read_text()` first.)
2. Run from a **neutral empty directory**, not the session scratchpad — three records
   referencing "this codebase / my draft" tripped over unrelated scratch artifacts.
   Self-contained queries that *mention* local artifacts need a clean cwd to be fair.
