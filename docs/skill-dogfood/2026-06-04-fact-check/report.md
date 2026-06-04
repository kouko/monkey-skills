# Dogfood report — `fact-check`

> Agent-actionable fix dossier. Findings are **ADVISORY** — dogfood
> discovers + points; it does NOT apply edits. The main agent decides and
> makes the change. The user is the final calibrator: read the surfaced
> raw outputs (appendix), then drive the fix.

## Metadata

| Field | Value |
|---|---|
| Skill path | `research-toolkit/skills/fact-check` |
| Skill version | `0.1.0` |
| Date | `2026-06-04` |
| Passes run | activation (real-harness) · executor+blind-auditor · cold-reader |
| Model pinned | `claude-opus-4-8[1m]` (orchestrator + subagents); activation via local `claude` CLI 2.1.162 |
| Activation fidelity | **real-harness sandbox** (`claude -p --max-turns 1`, 4-skill menu, 2 runs/query) |
| Distractor set | `deep-research`, `cite-check`, `deep-read` (3 nearest siblings) |
| Meta-dogfood bias | none — fact-check is an external target, not the dogfood skill itself |

## Severity summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 1 |
| Medium | 5 |
| Low | 3 |
| **Total** | 9 |

**Headline.** The skill *works* — all three real-input executions produced
correct, contract-shaped verdicts (`supported` / `refuted` /
`inconclusive`), and its **trigger differentiation from siblings is
excellent (over-trigger 0/6)**. The defects are concentrated in two
seams a static check cannot see: (1) the **A→B data handoff** inside the
workflow is under-specified, and (2) the skill **under-fires on claims the
router thinks it already knows** (trigger-miss). Per the skill's own
*floor-not-ceiling* rule, **no pass verdict is stamped.**

---

## Findings

### FINDING-001: A→B evidence-pool → verify-input reduction is undefined

- **Severity**: High
- **Category**: Workflow-drift
- **Pass**: informed (executor) + blind (cold-reader) — **convergent, both probes found it independently**
- **Probe prompt**: executor "run the full Stage A→B→C on claim X"; cold-reader Q3 "is Stage B executable as written?"
- **Expected**: Stage A produces an evidence **pool** (multiple `{sourceQuality, publishDate, claims}` objects from `schemas.py extract`); Stage B's `prompts.py verify` consumes **one** flat `{claim, sourceUrl, sourceQuality, quote}`. The skill should say how to collapse the pool into the per-voter object.
- **Actual**: SKILL.md never specifies the reduction. The executor had to guess ("I picked the single strongest supporting quote per claim"); the cold-reader flagged the same hole: *"Does each voter get one source, all sources, the best source? **Undefined.** This is a real execution gap."*
- **Transcript evidence**:
  - executor FRICTION: *"The verify prompt takes ONE `{claim, sourceUrl, sourceQuality, quote}`, but Stage A produces an evidence pool of multiple quotes/sources. SKILL.md never says which pooled quote to feed the voters, or whether each voter sees the whole pool."*
  - cold-reader Q3: *"My evidence pool has multiple sources. Does each voter get one source, all sources, the best source? Undefined."*
- **Root cause**: the workflow documents each *step* (extract schema, verify prompt) but not the *data transformation between them*. The extract output shape (`claims[]`) and the verify input shape (single `claim`) don't line up, and nothing bridges them.
- **Why static review missed it**: every script is documented and every stage is present, so a structural check / `skill-judge` reads the file as complete. The gap only exists in the *prose handoff* between two documented steps — invisible until an agent actually pipes Stage A's output into Stage B.
- **Location**: `SKILL.md` Stage A step 4 → Stage B step 1 (the seam between lines ~104–120 and ~134–140).
- **Suggested fix direction**: add an explicit "A→B reduction" paragraph — how to collapse the extract `claims` pool into the per-voter `{claim,...}` object, and whether each of the 3 voters sees one source or the whole pool. If "whole pool," change the verify example to take an array; if "one each," say how sources are assigned to `voter_idx`.
- **Repro**: dispatch a fresh informed executor on any claim that yields ≥2 sources; observe it must invent the reduction.

### FINDING-002: Under-fires on claims the router believes it already knows

- **Severity**: Medium
- **Category**: Trigger-miss
- **Pass**: blind (activation harness)
- **Probe prompt**: `sf13` = "Is it true bananas are berries but strawberries are not?"; `sf08` = "Someone told me lightning never strikes the same place twice. True or false?"
- **Expected**: both are single free-floating factual claims phrased as "is it true…?" — the skill's core job — so both should route to `fact-check`.
- **Actual**: `sf13` fired **no skill in BOTH runs** (the router answered from its own knowledge); `sf08` fired `fact-check` in run 1 but **no skill in run 2** (flaky). Per-run, should-fire queries routed to fact-check in 29/32 runs (~91%); the 3 misses cluster on "common trivia" claims.
- **Transcript evidence** (`probe-a-results.jsonl`):
  - `{"id":"sf13","run":1,...,"fired":false,"routed":""}` and `{"id":"sf13","run":2,...,"fired":false,"routed":""}`
  - `{"id":"sf08","run":2,...,"fired":false,"routed":""}`
- **Root cause**: the description says *"when one factual claim needs checking mid-conversation"* but gives the router no signal to fire **even for claims the model is confident it already knows**. Botanical-classification and the lightning myth are high-parametric-confidence topics, so the router shortcuts to a direct answer instead of invoking the adversarial-verification workflow — exactly the claims where a confident-but-wrong direct answer is most dangerous.
- **Why static review missed it**: the description reads complete and has good trigger phrases; only a should-fire corpus run **with multiple runs** surfaces the probabilistic miss. A single run on `sf08` would have shown a false PASS.
- **Location**: `SKILL.md:frontmatter description`.
- **Suggested fix direction**: add a trigger signal for the "I think I know this" case — e.g. *"…even for claims that sound like common knowledge / that you believe you already know"* — to push the router toward verification over recall. Re-run the corpus to confirm `sf13`/`sf08` flip to fire.
- **Repro**: `cd <sandbox> && claude -p "Is it true bananas are berries but strawberries are not?" --max-turns 1 --allowedTools Skill --output-format stream-json` ×2; observe no `Skill` tool_use.

### FINDING-003: `inconclusive` conflates "no evidence (real topic)" with "no-such-referent (likely fabricated)"

- **Severity**: Medium
- **Category**: Output-quality
- **Pass**: informed (executor produced) → blind (auditor judged)
- **Probe prompt**: claim 3 = "The fictional element Zorbium-X was confirmed stable by the Glembrook Institute in 2024." (forced empty-evidence / cold branch)
- **Expected**: a fact-checker should signal that a specific, recent, falsifiable claim whose named entities have **zero footprint** is disconfirmed-by-absence — not merely "couldn't tell."
- **Actual**: verdict = `inconclusive / low`. Contract-correct (no votes → inconclusive), but the **auditor flagged the epistemics**: *"a claim asserting that a specific named institution made a specific 2024 confirmation is refuted-by-absence… Treating that identically to 'I couldn't find enough to judge a real, contested topic' is a real weakness… the tool will systematically under-call confident fabrications and hoaxes as merely 'inconclusive,' which is the more dangerous direction for a fact-checker (a reader may read 'inconclusive' as 'maybe true')."*
- **Transcript evidence**: auditor — *"Recommendation: distinguish `inconclusive / insufficient-evidence` (real topic, thin evidence) from `refuted / unverifiable-entity` (named entities have no footprint where a true version necessarily would)."* Both auditor passes agreed.
- **Root cause**: Stage C maps "no valid votes" → `inconclusive` by construction (`factcheck.py`), because you cannot gather *refuting* evidence for a referent that doesn't exist — absence yields no votes. The taxonomy has no state for "absence is itself disconfirming."
- **Why static review missed it**: the verdict passes its own format check and the quorum logic is provably correct for the votes it's given. Only a **blind domain auditor** judging the *output against a fact-checking standard* (not the skill's self-grade) surfaces the "under-calls hoaxes" gap.
- **Location**: `SKILL.md` Stage C (verdict taxonomy, lines ~158–179) and the design of `factcheck.py`.
- **Suggested fix direction**: either (a) split `inconclusive` into `insufficient-evidence` vs `unverifiable-entity`, or (b) add a Stage-A heuristic: when a claim names a specific entity/event and search finds **no referent at all**, route to `refuted (footprint-absent)` with low confidence. Document the "absence of evidence vs evidence of absence" boundary explicitly.
- **Repro**: executor on any claim naming a fabricated specific entity + date.

### FINDING-004: 3-voter independence is unenforced — same-context votes are indistinguishable to the quorum

- **Severity**: Medium
- **Category**: Gate-bypass
- **Pass**: informed (executor)
- **Probe prompt**: "do the 3-voter adversarial fan-out as described."
- **Expected**: the quorum's integrity rests on **3 independent** votes; the skill should ensure (or at least assert) the votes come from independent contexts.
- **Actual**: nothing enforces independence. The executor — unable to dispatch real subagents in its harness — *simulated the 3 voters as 3 reasoning passes*, which is precisely the bypass: *"No script enforces that 3 distinct votes actually came from independent contexts — the only diversifier is the `--voter-idx` in the prompt text. A single reasoning pass emitting 3 near-identical votes would be indistinguishable to `factcheck.py`."*
- **Root cause**: independence is a *convention* ("dispatch N subagents"), not a *gate*. `factcheck.py` counts whatever 3 verdicts it receives; it has no way to know whether they were independent.
- **Why static review missed it**: the quorum math in `factcheck.py` is correct and tested; the hole is that the *upstream guarantee* (votes are independent) is unverifiable from the data. A green unit test on `factcheck.py` passes regardless.
- **Location**: `SKILL.md` "Portable fan-out convention" (lines ~48–61) + Stage B.
- **Suggested fix direction**: elevate the convention to a stated **integrity assumption / gate** — e.g. "votes produced in the same context do not constitute a valid quorum; a host that cannot fan out independently should report `inconclusive (no-quorum)` rather than 3 same-context votes." Make the degradation explicit so a portability shortcut can't silently fake a quorum.
- **Repro**: run the skill in any host without concurrent-subagent support; observe the only path is same-context simulation.

### FINDING-005: "fetch each novel source" contradicts the "small budget" point-check framing

- **Severity**: Medium
- **Category**: Workflow-drift
- **Pass**: informed (executor)
- **Probe prompt**: Stage A on a well-sourced claim (honey).
- **Expected**: a consistent fetch rule.
- **Actual**: `dedup.py` returns all high-relevance hits as `novel` (high-relevance is never budget-dropped, so `slots` can hit 0 with sources remaining). SKILL.md step 4 says *"for each novel source, fetch it"* — literally fetch all — while the skill's ethos says point-check / small budget. The executor **deviated**: *"I fetched 2-4 of the novel sources, not all of them… the literal instruction says fetch every novel source."*
- **Root cause**: two rules in tension — the soft budget in `dedup.py` (high-relevance bypasses the cap) vs the literal "fetch each novel source" prose — with no reconciliation.
- **Why static review missed it**: each rule is locally reasonable; the contradiction only bites when `dedup` returns more novel sources than the budget and an executor must choose.
- **Location**: `SKILL.md` Stage A steps 3–4 (lines ~90–120).
- **Suggested fix direction**: reconcile — e.g. "fetch novel sources **up to the budget**, highest-relevance first; high-relevance overflow is optional." Make "small budget" the binding constraint, or drop the soft-bypass.
- **Repro**: executor Stage A on any claim returning ≥6 high-relevance hits.

### FINDING-006: Controlled vocabularies are not enumerated in-file (forces opening `schemas.py`)

- **Severity**: Medium
- **Category**: Progressive-disclosure
- **Pass**: blind (cold-reader)
- **Probe prompt**: cold-reader Q1/Q4 "self-contained? undefined terms?"
- **Expected**: a reader should be able to act on the file without opening the bundled scripts to learn value vocabularies.
- **Actual**: cold-reader could not resolve the allowed values for **`sourceQuality`**, **`confidence`** (used by `factcheck.py`'s "strongest confidence" ordering), and **`relevance`** rank scale: *"'at least url + relevance' — 'at least' means I don't know the full required shape… I'd have to run the script or open `schemas.py`."* The `dedup.py` `results[]` element shape and the `seen` carry-over structure for multi-batch calls are likewise unspecified.
- **Root cause**: the body describes script *roles* but defers all *contracts* (field vocabularies, the `seen` shape) to the scripts, without telling the reader that's where to look or enumerating the small enums inline.
- **Why static review missed it**: the file looks self-contained to a structural check; only a **zero-context cold-reader** (not the in-session author, who knows the enums) hits the wall.
- **Location**: `SKILL.md` Stage A steps 2 & 4, Stage C (lines ~83–88, ~118–120, ~178).
- **Suggested fix direction**: enumerate the small controlled vocabularies inline (e.g. `confidence ∈ {low, medium, high}`, the `sourceQuality` tag set, the `relevance` scale) OR add one line per script pointing to `python scripts/schemas.py <cmd>` as the authoritative shape and noting the `seen` carry-over for batch loops.
- **Repro**: cold-reader pass on `SKILL.md` alone.

### FINDING-007: Script-error / tool-unavailable handling is entirely silent

- **Severity**: Low
- **Category**: Cold-start
- **Pass**: blind (cold-reader)
- **Probe prompt**: cold-reader Q5 "cold-start coverage?"
- **Expected**: given that several stdin shapes are under-specified (F001, F006), a malformed-input script error is a realistic failure that should have a fallback.
- **Actual**: *"A `python scripts/...` script errors (bad JSON in, traceback, non-zero exit): **NOT covered — silent.**"* Also: host lacking `WebSearch`/`WebFetch` — *"NOT covered — silent."* (Empty-evidence and voter-abstention paths **are** well covered — credit where due.)
- **Root cause**: the workflow documents the happy path + two graceful-degradation cases (empty evidence, abstention) but no script-failure / missing-tool path.
- **Why static review missed it**: not a structural concern; only surfaces when a reader asks "what if a script throws?"
- **Location**: `SKILL.md` (no error-handling section).
- **Suggested fix direction**: add a 2–3 line "if a script errors or a host tool is missing" note (retry once / treat as abstention / report `inconclusive`).
- **Repro**: feed `factcheck.py verdict` malformed JSON; observe traceback with no documented recovery.

### FINDING-008: Confidence `high` on absolute "never" claims is slightly generous

- **Severity**: Low
- **Category**: Output-quality
- **Pass**: blind (auditor)
- **Probe prompt**: claim 1 (honey) verdict = `supported / high`.
- **Actual**: auditor (both passes) rated axis-2 **WEAK**: *"`supported` for an absolute 'never' is overbroad — the answer's own ferment/botulism caveat contradicts a clean support… confidence `high` on an absolute claim is slightly generous."*
- **Root cause**: the verdict mapper takes the strongest non-refuting confidence; it has no notion of *claim scope* (an unconditional "never" deserves a confidence haircut when the support is conditional).
- **Why static review missed it**: format-correct, quorum-correct; only a domain auditor weighing claim wording vs evidence scope catches the calibration gap.
- **Location**: Stage C confidence rule (line ~178) / `factcheck.py`.
- **Suggested fix direction**: advisory only — optionally note that absolute-quantifier claims ("never/always/all") with conditional support should cap at `medium`. Low priority; the verdict text already surfaces the caveat.
- **Repro**: executor on any absolute-quantifier claim with conditional supporting evidence.

### FINDING-009: Doc polish — `--angle` example omits `rationale`; fetch-failure handling split prose↔prompt

- **Severity**: Low
- **Category**: Workflow-drift (cosmetic)
- **Pass**: informed (executor)
- **Actual**: (a) the `--angle '{"label":"claim","query":"<q>"}'` example omits the `rationale` key, so the rendered search prompt shows a dangling *"claim — "* empty dash. (b) Partial fetch failure (HTTP 403) is handled only inside the embedded fetch-prompt text; the prose body mentions dead/paywalled only in the *all-empty* case.
- **Root cause**: example/script drift + the same case documented in two places.
- **Location**: `SKILL.md` Stage A step 2 example (line ~78) and step 4 (lines ~104–124); `prompts.py`.
- **Suggested fix direction**: add `rationale` to the example (or make `prompts.py` render cleanly without it); add one prose line covering per-source fetch failure.
- **Repro**: run `python scripts/prompts.py search --angle '{"label":"claim","query":"x"}' --question "x"`; observe dangling dash.

---

## Triggering — positive result (no over-trigger; one trigger-miss cluster)

> Reported for completeness; **not** a pass stamp.

- **True-positive (should-fire → fact-check)**: 29/32 runs (~91%). Clean on 14/16 queries across both runs. Misses: `sf13` (0/2, robust) and `sf08` (1/2, flaky) — see **FINDING-002**.
- **Over-trigger (should-NOT → fact-check)**: **0/6 — perfect.** fact-check never stole a query meant for `deep-research`, `cite-check`, or `deep-read`. The description's "point-check counterpart to deep-research" framing differentiates it cleanly in the live router. This is the standout strength.
- **Advisory sibling note** (not a fact-check defect): `sn02` (deep-research, both runs) and `sn05` run 1 (cite-check) fired **no** skill — sibling trigger-miss in `deep-research`/`cite-check`. Worth checking if those two are dogfooded next; supports the cold-reader's observation that the deep-research↔fact-check boundary is *breadth/budget*, not phrasing.

---

## Raw outputs appendix

### A. Activation runs (blind pass) — real-harness sandbox, 2 runs/query

| # | id | Query (abbrev) | should | run1→ | run2→ | Verdict |
|---|---|---|---|---|---|---|
| 1 | sf01 | Is it true … Great Wall visible from space? | true | fact-check | fact-check | TP |
| 2 | sf02 | Can you verify: honey never spoils? | true | fact-check | fact-check | TP |
| 3 | sf03 | Fact-check: humans use 10% of brain | true | fact-check | fact-check | TP |
| 4 | sf04 | Did Einstein really fail math? | true | fact-check | fact-check | TP |
| 5 | sf05 | 這個說法對嗎：每天喝八杯水才健康 | true | fact-check | fact-check | TP |
| 6 | sf06 | この主張は本当？ナポレオンは背が低かった | true | fact-check | fact-check | TP |
| 7 | sf07 | goldfish 3-second memory accurate? | true | fact-check | fact-check | TP |
| 8 | sf08 | lightning never strikes same place twice? | true | fact-check | **(none)** | **PARTIAL** |
| 9 | sf09 | 真的假的？吃宵夜一定會變胖 | true | fact-check | fact-check | TP |
| 10 | sf10 | NASA space pen vs Soviet pencil? | true | fact-check | fact-check | TP |
| 11 | sf11 | swallow 8 spiders a year? | true | fact-check | fact-check | TP |
| 12 | sf12 | 事実確認：金魚の記憶は3秒 | true | fact-check | fact-check | TP |
| 13 | sf13 | bananas berries, strawberries not? | true | **(none)** | **(none)** | **FN(miss)** |
| 14 | sf14 | 幫我查證：長城是唯一從太空可見的人造建築 | true | fact-check | fact-check | TP |
| 15 | sf15 | COVID vaccines contain microchips? | true | fact-check | fact-check | TP |
| 16 | sf16 | Coriolis decides sink drain direction? | true | fact-check | fact-check | TP |
| 17 | sn01 | deep multi-source research report on… | false | deep-research | deep-research | TN |
| 18 | sn02 | thorough multi-source analysis w/ citations | false | (none) | (none) | TN |
| 19 | sn03 | 深入研究台灣半導體競爭格局，給報告 | false | deep-research | deep-research | TN |
| 20 | sn04 | check every citation supports its claim | false | cite-check | cite-check | TN |
| 21 | sn05 | audit references / misattributed | false | (none) | cite-check | TN |
| 22 | sn06 | deeply understand this 60-page paper | false | deep-read | deep-read | TN |

- True-positive rate: **29/32 runs (~91%)** · clean on 14/16 queries
- Over-trigger (to fact-check): **0/6 — none**
- Raw: `probe-a-results.jsonl`; per-run JSONL streams in `probe-a-raw/`.

### B. Cold-reader audit (blind pass) — verbatim highlights

- **Self-contained?** *"Mostly yes for orchestration, but no — the scripts' exact I/O shapes are only partially shown and verdict constants are referenced but not defined here."*
- **Biggest gap (Q3):** *"The verify command takes ONE `{claim, sourceUrl, sourceQuality, quote}` — my evidence pool has multiple sources. Does each voter get one source, all sources, the best source? Undefined. This is a real execution gap."* → FINDING-001
- **Undefined terms (Q4):** `sourceQuality` values undefined, `confidence` values undefined, `relevance` scale undefined, `rank.quorum_survives` named but never invoked. → FINDING-006
- **Cold-start (Q5):** empty-evidence ✔ covered, abstention ✔ covered; **script errors silent**, **missing host tool silent**. → FINDING-007
- **Triggering unsure cases:** *"'Research whether remote work increases productivity' sits right on the seam with deep-research"*; *"from this file alone there's no negative boundary against cite-check."* (Empirically the live router handled both cleanly — see Probe A.)

### C. Executor artifacts (informed pass) — the 3 verdicts the auditor judged

```
Claim 1 "Honey never spoils…":     {"verdict":"supported","confidence":"high","valid_count":3,"refuted_count":0}
Claim 2 "Humans use 10% of brain": {"verdict":"refuted","confidence":"high","valid_count":3,"refuted_count":3}
Claim 3 "Zorbium-X / Glembrook":   {"verdict":"inconclusive","confidence":"low","valid_count":0,"refuted_count":0}
```
(Full user-facing answers + cited URLs in the executor transcript.)

### D. Executor trajectory (informed pass) — verbatim highlights

- Every `python scripts/...` ran from inside `scripts/` as prescribed; flat imports resolve **only** because cwd is `scripts/` (instruction is load-bearing and correct).
- Smithsonian fetch returned **HTTP 403** → dropped per fetch-prompt rule (handled, but see FINDING-009).
- `dedup.py` returned all sources `novel` with `slots:0`/`slots:1` → executor trimmed fetches (FINDING-005).
- 3 voters **simulated as 3 reasoning passes** (harness had no subagent dispatch) — exactly the independence gap in FINDING-004.
- `factcheck.py verdict` behaved exactly as documented on all 3, incl. `[]` → `inconclusive` cold path (valid-count gate worked).

### E. Auditor judgment (informed pass) — blind, 2 passes, agreed

| Artifact | Axis-1 Contract | Axis-2 Domain | Note |
|---|---|---|---|
| 1 — Honey | PASS | **WEAK** | `supported/high` on absolute "never" is generous (FINDING-008) |
| 2 — 10% brain | PASS | PASS | real sources, label matches reality, no fabrication |
| 3 — Zorbium-X | PASS | **WEAK** | contract-correct but under-calls a near-certain hoax (FINDING-003) |

> Auditor overall: *"No artifact is outright domain-wrong"* + *"the tool will systematically under-call confident fabrications and hoaxes as merely 'inconclusive,' which is the more dangerous direction for a fact-checker."* Both passes agreed on all 6 buckets. Minor caveat: some cited URLs were truncated with "…", reducing exact-path verifiability (not a fabrication, but a real fact-checker would want full slugs).

---

## Fix log (post-dogfood)

> Applied by the main agent after this dogfood. Findings are advisory; these
> two were actioned + re-verified. The findings above are kept as the
> point-in-time record.

### F-001 — FIXED (doc)
Added a "reduce the Stage-A evidence pool to one claim object" paragraph at
the start of `SKILL.md` Stage B. Grounding: `factcheck.py` takes exactly 3
verdicts → fact-check runs **one** 3-voter quorum on the single claim (not
per-source), aligned with `deep-research`'s `(claim, voter_idx)` pattern.
Specifies: `claim` = claim under check; `sourceUrl/quality/quote` = strongest
supporting item (strongest = highest `sourceQuality`, ties by `importance`);
all 3 voters get the **same** object, diverging by `--voter-idx` + own
counter-search. **Verified**: a fresh cold-reader on the edited file answered
"what do you feed verify, same or different JSON?" unambiguously (was a guess
before).

### F-002 — FIXED + RE-TESTED (description)
Added explicit trigger phrasings ("is it true…?", "really?", "true or
false?", "這個說法對嗎", "真的假的", "本当？") and a "**even for claims that
sound like common knowledge / that you think you already know**" signal to
the description.

Re-ran Probe A against the **updated** description (same sandbox + distractors):

| Query | Before | After |
|---|---|---|
| `sf13` "bananas are berries…" | **0/2 fired nothing** | **3/3 → fact-check** |
| `sf08` "lightning never strikes…" | 1/2 (flaky) | **3/3 → fact-check** |
| `ck01` "only five senses?" (new) | — | 3/3 → fact-check |
| `ck02` "bulls hate red?" (new) | — | 3/3 → fact-check |
| `ck03` "tongue taste zones?" (new) | — | 3/3 → fact-check |
| should-NOT × 12 runs | 0 over-trigger | **0 over-trigger (preserved)** |

**should-fire → fact-check: 15/15 runs · over-trigger: 0/12.** The
trigger-miss is closed and the 0/6 over-trigger strength is preserved (no
regression). Raw: `retest-results.jsonl`, `retest-raw/`.

### F-003 — FIXED + RE-DOGFOODED (logic + doc, TDD)
Added a `reason` discriminator to `factcheck.py`'s output and an opt-in
`--no-referent` CLI flag (user chose: keep the 3 verdict labels, add a reason
field — no taxonomy expansion, no contract-break). `classify_verdict(verdicts,
*, no_referent=False)` now returns `{verdict, reason, confidence, valid_count,
refuted_count}` where `reason ∈ {quorum-survived, quorum-refuted,
no-referent, insufficient-evidence}`. The `inconclusive` bucket splits:
`no-referent` (zero footprint → "likely fabricated") vs `insufficient-evidence`
(real topic, thin). Verdict stays `inconclusive` (0 valid votes is math-true);
the flag never overrides a real quorum. `schemas.py` / `rank.py` (byte-identical
to deep-research, drift-locked) were **not** touched — only the fact-check-owned
`factcheck.py`. SKILL.md Stage A (two-empty-cases note) + Stage C (reason
handling, user-facing phrasing) + quick-ref table updated.

- **TDD**: 7 new tests written first (RED: missing `reason` key / CLI rejects
  flag) → implemented → GREEN. Full suite **21 passed** (was 14); siblings
  unaffected — deep-research 44 / cite-check 41 / deep-read 26 all green; the
  byte-identical drift check (`test_primitives_present.py`) still passes.
- **Re-dogfood (behavioral)**: fresh informed executor on the Zorbium-X hoax →
  correctly detected zero footprint, ran `factcheck.py verdict --no-referent`,
  got `reason: no-referent`, and phrased "most likely fabricated rather than
  merely unverified." Fresh **blind auditor** (firewalled, 2 passes, agreed) on
  that output: *"The 'under-calls hoaxes' weakness is **ABSENT** — leaves no
  room for a reader to mistake the hoax for 'possibly true'."* (was WEAK in the
  original dogfood.)

> Note — package-level `pytest research-toolkit` hits a **pre-existing**
> cross-skill basename collision (`test_primitives_present.py` shared by all 4
> skills, pytest `importmode=prepend`); not a regression — each skill ships its
> own `pytest.ini` and is run per-skill. (Known issue: root `importmode =
> importlib` would resolve it repo-wide.)

### F-004 — FIXED + RE-DOGFOODED (logic + doc, TDD)
Designed an **independence gate**. Considered an objective vote-dedup gate but
rejected it (the test fixtures use placeholder `evidence:"e"`, and terse real
votes can legitimately coincide → false-positive risk). Chose the **declaration
gate** (the report's recommendation): `classify_verdict(..., independent_fanout=
True)` + CLI `--solo`. When the executor cannot fan out independently and must
reason in one shared context, it MUST pass `--solo`; the gate then forces
`inconclusive` / `reason: no-quorum` **before** the supported/refuted checks —
non-independent votes can never drive a verdict. With no votes cast, the solo
gate is moot (the empty-evidence reasons apply). SKILL.md "Portable fan-out
convention" upgraded from a nicety to a stated MUST gate; Stage C + quick-ref
updated. `schemas.py`/`rank.py` untouched (drift-locked).

- **TDD**: 5 new tests first (RED: missing `independent_fanout` kwarg / CLI
  rejects `--solo`) → implemented → GREEN. fact-check **26 passed** (was 21);
  siblings green (deep-research 44 / cite-check 41 / deep-read 26); drift check
  intact.
- **Re-dogfood (behavioral)**: a fresh executor told *"your host CANNOT dispatch
  subagents"* honestly passed `--solo` and got `inconclusive`/`no-quorum` —
  **even though 2 of its 3 same-context votes refuted** (which would otherwise
  be `refuted`). The silent bypass is now an explicit, enforced degradation. The
  executor confirmed: *"I did NOT pass three same-context votes off as a real
  quorum… I complied with what the SKILL.md required."*
- **New minor nit surfaced** (F-005/F-006 family, not actioned): `dedup.py`'s
  `relevance` is an enum (high/medium/low), but SKILL.md Stage A step 2 calls it
  a "rank" → an executor first passed integer ranks and hit
  `ValueError: unknown relevance 1`. Wording fix belongs with F-006.

### F-005 → F-009 — FIXED (doc batch) + COLD-READER RE-VERIFIED
Cleared the remaining five in one SKILL.md pass (no script changes):

- **F-005** (fetch budget contradiction) — Stage A step 4 now reads "highest-
  `relevance` first, **up to the ≤6 budget**; overflow optional, not mandatory";
  step 3's old "can exceed the slot count — that is fine" reworded to point
  forward to the step-4 cap (closed a residual the cold-reader caught).
- **F-006** (controlled vocabularies) — all four enums now inline:
  `relevance` {high,medium,low}, `sourceQuality` {primary,secondary,blog,forum,
  unreliable}, `importance` {central,supporting,tangential}, `confidence`
  {high,medium,low}. No need to open `schemas.py`.
- **F-007** (error / cold-start silent) — new "When a step fails" section:
  script error → fix JSON + re-run (never swallow); host tool missing → say so,
  don't fabricate → `inconclusive`/`insufficient-evidence`; voter fails →
  abstention.
- **F-008** (confidence over-calibration) — Stage C calibration caveat: absolute
  quantifiers (never/always/all/none) with only conditional support cap at
  `medium`.
- **F-009** (cosmetic) — `--angle` example now includes `rationale` (verified:
  renders "claim — why this checks the claim", no dangling dash); the
  `relevance`-is-an-enum-not-an-integer warning also resolves the `ValueError`
  nit surfaced during the F-004 re-dogfood.

**Re-verification**: a fresh cold-reader on the updated SKILL.md confirmed
Q1 (vocabularies) "no finding — all four defined inline", Q3 (error/cold-start)
"no finding — all three explicit", Q4 (relevance type) "unambiguously a string
enum". The only residual it raised (step-3/step-4 budget tension) was then
closed by the reword above. SKILL.md ~2.8k tokens (well under the 6k budget);
fact-check tests still 26 passed.

### F-010 — FIXED (doc) — surfaced by the final confirmation re-test
The comprehensive re-test executor hit a **real contradiction**: SKILL.md said
"run `python scripts/…` commands from this skill's own `scripts/` directory",
but the examples carry the `scripts/` prefix — so from *inside* `scripts/` the
literal command resolves to `scripts/scripts/factcheck.py` and **fails**.
Verified empirically: prefix-from-scripts/ → `No such file or directory`;
prefix-from-skill-root → works (Python puts the script's dir on `sys.path`, so
the flat imports resolve either way). Fixed line 45 to say **run from the skill
root**; all 8 documented commands now run as written (verified OK from root).

## Final confirmation re-test (goal: "再測試一次確定有修好")

A full re-test against the fully-patched skill:

- **Unit suite**: fact-check **26 passed**; siblings unaffected (deep-research
  44 / cite-check 41 / deep-read 26); all 5 `reason` values reachable via CLI.
- **Activation (real harness, 6 queries ×2)**: should-fire **6/6 → fact-check**
  (incl. the previously-missed `sf13` "bananas/strawberries"); over-trigger
  **0/6** — F-002 holds, no regression after the body edits.
- **Full-workflow executor (4 claims on the final skill)** confirmed each fix
  end-to-end: F-001 "applied with zero guessing"; F-003 Claim-3 → `no-referent`
  phrased "likely fabricated"; F-004 Claim-4 → honest `--solo` → `no-quorum`
  (gate unfakeable); F-005/F-006 "no ValueError, every script ran first try";
  F-008 actually used (capped the "carrots improve night vision" votes at
  `medium` per the absolute-quantifier caveat).
- **Note (not a defect)**: the executor's own sandbox lacked any subagent
  primitive, so its honest path forced *every* vote-bearing claim to
  `no-quorum` — that is F-004's gate working correctly, an artifact of nested
  sub-subagent dispatch, not the main-agent case (where fan-out works, as the
  dedicated F-004 verification showed).

> **All 10 findings actioned** (9 from the dogfood + F-010 found by the
> confirmation re-test). F-001/F-002 (doc + description), F-003/F-004 (logic +
> doc, TDD), F-005–F-010 (doc). Each behaviorally / cold-reader / executor
> re-verified. fact-check tests 14 → 26. Not yet committed / versioned / PR'd.

## How to drive the fix

Findings are advisory. Suggested order: **FINDING-001** (High — the one workflow gap that forces every executor to improvise) → **FINDING-002 / -003 / -004** (Medium, behavioral: trigger-miss, hoax under-call, quorum integrity) → **-005 / -006** (Medium, doc/contract clarity) → **-007 / -008 / -009** (Low polish). Re-run Probe A after the FINDING-002 description edit to confirm `sf13`/`sf08` flip to fire.
