# Dogfood report — `using-research-toolkit` (+ research-toolkit routing layer)

> Fill the `{placeholders}`. This report is an **agent-actionable fix
> dossier**: its consumer is the **main agent that will FIX the skill**
> (plus the user reviewing raw outputs). Every finding localizes the
> defect, states why it broke, and names a *suggested* edit class.
>
> **Findings are ADVISORY.** Dogfood discovers + points; it does NOT
> apply edits. The main agent decides and makes the change. Auto-fix is
> out of scope. The user is the final calibrator — read the surfaced raw
> outputs (appendix), then drive the fix by talking to the main agent.

## Metadata

| Field | Value |
|---|---|
| Skill path | `research-toolkit/skills/using-research-toolkit` (branch research-skill-r2; members cite-check / fact-check / deep-read / deep-deep-research in scope for routing) |
| Skill version | `0.1.0` (plugin 0.3.0) |
| Date | `2026-07-06` |
| Passes run | activation (2 runs ×16 queries) · executor+auditor (2 E2E tasks, blind auditor ×2) · cold-reader |
| Model pinned | sonnet (weak-tier gate) for ALL driven sessions + subagents; harness `--model sonnet` via wrapper |
| Activation fidelity | real-harness sandbox (`--plugin-dir` branch plugin over the full installed ~120-skill surface — real distractors, stronger than a synthetic menu) |

## Severity summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 1 (F6 — environment-level member trigger unreliability) |
| Medium | 2 (F1 invocation mechanics; F5 unvetted sub-claims) |
| Low | 4 (F2 boundary gaps; F3 jargon; F4 verdict-enum drift; F7 tsundoku capture) |
| **Total** | 7 |

**Overall read**: the branch's routing layer WORKS — the router fired
2/2 in both activation runs and drove a correct end-to-end chain
(router → cite-check → planted misattribution caught); both member E2E
contracts held under 4 independent blind audits with ZERO fabrication.
No Critical finding. The one High is environmental (listing eviction),
already documented as the deferred machine-side fix; the repo-side
fixables are F1/F2/F3/F4/F5 — all one-to-two-line edits.

> Target ~5–10 well-evidenced findings over volume. Every finding cites
> an actual probe prompt + an actual subagent response (transcript
> excerpt) — no finding asserted from reading `SKILL.md` alone.

## Findings

<!-- One block per finding. Duplicate the template below. Number FINDING-001, -002, … -->

### FINDING-001: Router names members but never says how to invoke them

- **Severity**: `Medium`
- **Category**: `Cold-start`
- **Pass**: `blind` (cold-reader)
- **Probe prompt**: fixed cold-reader question set, Q1/Q3 (self-contained? procedure executable as written?)
- **Expected**: after picking a routing row, a first-time reader knows the next action (invoke the member via the Skill tool / slash command)
- **Actual**: reader knows *which* skill to pick but not *how* to invoke it
- **Transcript evidence**: "The routing table names four skills … but never says how to actually invoke one — no command syntax, no 'use the Skill tool with name X' … Line 15 header 'Skill' just gives a bare name with no invocation mechanism." / "I know *which* skill to pick, but not *how* to invoke it from this document alone."
- **Root cause**: the table dropped the `Command` column the systems-thinking precedent carries; invocation mechanics were assumed knowledge
- **Why static review missed it**: quality reviewer saw the missing Command column but scored it 🟢 cosmetic (precedent-diff, not behavior); only a zero-context reader shows it blocks execution
- **Location**: `SKILL.md:§routing table (~line 15)`
- **Suggested fix direction**: add one sentence above the table ("invoke the chosen member with the Skill tool, e.g. `Skill(skill: "research-toolkit:fact-check")`") or restore a Command column
- **Repro**: fresh zero-context subagent (sonnet), read only the router SKILL.md, fixed question set Q1/Q3

### FINDING-002: Two adjacent request shapes are genuinely unroutable from the text

- **Severity**: `Low`
- **Category**: `Cold-start`
- **Pass**: `blind` (cold-reader)
- **Probe prompt**: cold-reader Q2 (name 2 requests you're unsure about)
- **Expected**: routing table + guard resolve adjacent cases
- **Actual**: reader could not decide (a) "double-check spreadsheet numbers against the source" — cite-check? fact-check? neither; (b) "summarize this 40-page report" — deep-read or answer-directly per guard
- **Transcript evidence**: "Genuinely ambiguous whether summarizing counts as 'structured deep comprehension.'"
- **Root cause**: table Situation cells cover the four canonical intents; two nearest-neighbor intents (data spot-check; plain summarization) fall between rows
- **Why static review missed it**: spec review checks the four rows exist, not the space between them
- **Location**: `SKILL.md:§routing table + §Negative Guard`
- **Suggested fix direction**: one boundary line each — "plain summarization without comprehension goals → answer directly (deep-read is for structured understanding)"; "spot-checking numbers in your own data → not this family (fact-check verifies public claims)"
- **Repro**: same cold-reader dispatch, Q2

### FINDING-003: Undefined jargon for first-time readers

- **Severity**: `Low`
- **Category**: `Jargon-leak`
- **Pass**: `blind` (cold-reader)
- **Probe prompt**: cold-reader Q4 (undefined terms)
- **Expected**: terms self-explanatory or defined on first use
- **Actual**: "family-entry router", "member skill", "built-in `deep-research` workflow", "gate logic" flagged as assumed knowledge; Built-in Boundary understood only via inference
- **Transcript evidence**: "'gate logic' (line 49) — no gate concept introduced anywhere in this file."
- **Root cause**: repo-internal vocabulary leaked into a skill whose audience includes fresh agents on other hosts
- **Why static review missed it**: reviewers share the repo vocabulary — bias accumulation; only a cold reader lacks it
- **Location**: `SKILL.md:4, 11, 38, 49`
- **Suggested fix direction**: gloss "member skill (= one of the four skills below)" once; replace "gate logic" with plain wording ("quality checks each member runs itself")
- **Repro**: same cold-reader dispatch, Q4

### FINDING-006: member-skill direct triggering is unreliable — environment-level, text cannot fix it

- **Severity**: `High`
- **Category**: `Trigger-miss`
- **Pass**: `blind` (activation, 2 runs ×16)
- **Probe prompt**: 13 should-fire queries (appendix A)
- **Expected**: member skills fire on their canonical intents
- **Actual**: fact-check 0/3 (run 1) vs 2/3 (run 2); deep-read 0/3 both runs (one run-2 fire went to the router, one to tsundoku); run agreement 11/16 overall. Router rows: 2/2 fired in BOTH runs — the only fully stable routing surface.
- **Transcript evidence**: appendix A table (two-run comparison)
- **Root cause**: host drops least-used skills' descriptions when ~120 skills exceed the listing budget (official behavior), so member routing depends on which descriptions happen to survive + model inline-answering; the descriptions themselves passed static review and, when visible, do route (run-2 fact-check fires)
- **Why static review missed it**: description text is standard-conformant; the defect lives in the runtime listing, invisible to any file review
- **Location**: environment (`enabledPlugins` surface / `skillListingBudgetFraction`), NOT the SKILL.md texts
- **Suggested fix direction**: machine-side — shrink globally-enabled plugins or raise the listing budget; until then the router + named invocation are the reliable paths (by design)
- **Repro**: appendix A commands; compare run-1/run-2 fired columns

### FINDING-007: tsundoku captures a deep-read-shaped ask (cross-plugin near-collision)

- **Severity**: `Low`
- **Category**: `Trigger-miss` (distractor capture)
- **Pass**: `blind` (activation run 2)
- **Probe prompt**: 「我手上有一本四百頁的策略管理教科書，想請你幫我深入讀懂它…」
- **Expected**: `research-toolkit:deep-read` (or router)
- **Actual**: run 2 fired `tsundoku:tsundoku` (book-distillation plugin)
- **Transcript evidence**: appendix A row 7
- **Root cause**: tsundoku's descriptions own the "book" noun-space and stay listed (frequently used plugin), while deep-read's description is evicted — an evicted skill's niche gets claimed by the nearest listed neighbor
- **Why static review missed it**: distractor competition only exists at runtime against the live listing
- **Location**: cross-plugin boundary (deep-read ↔ tsundoku) — a candidate one-line positive redirect in tsundoku's description ("comprehension without skill-building → deep-read") IF recurrence is observed
- **Suggested fix direction**: observe; fix only on recurrence (single occurrence, 1/2 runs — don't legislate off one incident)
- **Repro**: appendix A row 7, run-2 command

### FINDING-005: fact-check passes a supporting sub-claim through unverified

- **Severity**: `Medium`
- **Category**: `Output-quality`
- **Pass**: `informed` (executor + blind auditor ②-b)
- **Probe prompt**: E2E ② claim 「日本的平均壽命是世界第一長」
- **Expected**: cited evidence lines are themselves verified or flagged when sources conflict
- **Actual**: the verdict's supporting line "香港連續10年全球最長壽" (HK01) was passed through although other sources show Japan led during the 2020-2022 COVID interruption — a source conflict the output never reconciles
- **Transcript evidence**: auditor ②-b: "Not fabricated (properly attributed to HK01), but the output should have flagged the source conflict rather than passing '10 years running' through uncritically."
- **Root cause**: fact-check's quorum verifies the TARGET claim; supporting context claims ride along outside the quorum — the skill's contract doesn't say what rigor applies to them
- **Why static review missed it**: the declared contract (verdict + cited evidence) is met on its face; only blind domain re-verification of the citations exposes the unvetted rider
- **Location**: member `fact-check/SKILL.md` (evidence-assembly stage; NOT the router)
- **Suggested fix direction**: one clause: "supporting context claims either go through a cheap single-verifier pass or get hedged ('per HK01, uncontested check not run')"
- **Repro**: E2E ② command in appendix D; auditor ②-b prompt in appendix E

### FINDING-004: cite-check emits a compound verdict label outside its own 6-value enum

- **Severity**: `Low`
- **Category**: `Output-quality`
- **Pass**: `informed` (executor + blind auditor ①-b)
- **Probe prompt**: E2E ① citation fixture (3 real URLs, one planted misattribution)
- **Expected**: per-citation verdict drawn from cite-check's declared set {supported, partial, unsupported, misattributed, unresolvable, unsourced} — one value per citation
- **Actual**: record 2 labeled `misattributed / unsupported` (compound)
- **Transcript evidence**: auditor ①-b: "item 2 uses a compound label 'misattributed / unsupported' rather than picking one value from the declared 6-way enum — minor drift from the strict verdict taxonomy."
- **Root cause**: cite-check's SKILL.md defines the six categories but does not state "exactly one per citation"; on a weak model the ambiguity surfaces as a compound label
- **Why static review missed it**: static checks see the six categories defined; only a live run shows the executor blending them
- **Location**: member `cite-check/SKILL.md` (verdict-set clause; NOT the router)
- **Suggested fix direction**: one line in cite-check's output contract: "pick exactly ONE verdict per citation; misattributed subsumes unsupported when the source is about a different claim"
- **Repro**: E2E ① command in appendix D; auditor prompt in appendix E

<!-- … add more FINDING-### blocks as needed … -->

## Raw outputs appendix

> This appendix is the **human-in-the-loop surface**. It collects the
> RAW test outputs — not the auditor's distilled verdict — so the user
> can judge what the auditor judged, then steer the fix by talking to
> the main agent. **No embedded feedback form**: the report's job is to
> make that conversation possible (outputs visible) and productive
> (findings already localized + fix-pointed above). The user steers from
> there.

### A. Activation runs (blind pass)

> Each should-trigger / should-NOT-trigger query → fired / didn't, across
> the ≥2 runs. This is the over-trigger / trigger-miss raw evidence.

Corpus: `docs/loom/firing-corpus/research-asks.jsonl` (16 records), run
via `run_corpus(claude_bin=/private/tmp/research-firing-ab/claude-armB)`,
sonnet, max_turns=4, neutral empty cwd. Raw:
`/private/tmp/research-firing-ab/out/{B,B2}-research-asks.jsonl`.

| # | expected | Run 1 fired | Run 2 fired | Verdict |
|---|---|---|---|---|
| 1 | fact-check | — | — | FN both |
| 2 | fact-check (ja) | — | fact-check | FN / TP |
| 3 | fact-check (en) | — | fact-check | FN / TP |
| 4 | cite-check (zh) | — | — | FN both |
| 5 | cite-check (en) | cite-check | cite-check | TP both |
| 6 | cite-check (ja) | cite-check | cite-check | TP both |
| 7 | deep-read (zh) | — | tsundoku:tsundoku | FN / distractor-capture (F7) |
| 8 | deep-read (en) | — | using-research-toolkit | FN / family-TP |
| 9 | deep-read (ja) | — | — | FN both |
| 10 | deep-deep-research (en) | — | — | FN both |
| 11 | deep-deep-research (zh) | using-research-toolkit | — | family-TP / FN |
| 12 | using-research-toolkit (zh) | using-research-toolkit | using-research-toolkit | **TP both** |
| 13 | using-research-toolkit (en) | using-research-toolkit | using-research-toolkit | **TP both** |
| 14 | NONE (trivia) | — | — | TN both |
| 15 | NONE (coding) | loom-code (correct non-family route) | loom-code | TN both |
| 16 | NONE (opinion) | — | — | TN both |

- Family true-positive rate: run 1 = 5/13, run 2 = 7/13 (avg ≈ 46%);
  baseline main (single run) = 2/13.
- True-negative rate: 3/3 in BOTH runs (zero research-family over-fire).
- Run-to-run agreement 11/16 — routing is non-deterministic; per method,
  no conclusion is drawn from any single run.
- Contamination: 0 records dropped across both runs.

### B. Cold-reader audit (blind pass)

> The fresh zero-context subagent's verbatim answers to the fixed
> question set (self-contained? trigger hit/miss + unsure cases?
> per-mode procedure executable? undefined terms?).

Zero-context sonnet subagent, read ONLY the router SKILL.md, fixed
question set. Condensed verbatim answers (full transcript in the session
task log):

```
1. Self-contained? No. "The routing table names four skills … but never
   says how to actually invoke one — no command syntax, no 'use the
   Skill tool with name X' … Line 15 header 'Skill' just gives a bare
   name with no invocation mechanism."
2. Unsure triggers: (a) "double check the numbers in this spreadsheet
   against the source"; (b) "Summarize this 40-page report" — "Genuinely
   ambiguous whether summarizing counts as 'structured deep
   comprehension.'"
3. Executable as written? "I know *which* skill to pick, but not *how*
   to invoke it from this document alone."
4. Undefined terms: "family-entry router", "member skill", "built-in
   deep-research workflow", "gate logic (line 49) — no gate concept
   introduced anywhere in this file."
5. Negative Guard paraphrase: correct on first read. Built-in Boundary:
   understood "but only because I already inferred what 'built-in
   workflow' might mean."
```

### C. Executor artifacts (informed pass)

> Every artifact the executor subagent actually produced while running
> the skill end-to-end on real/realistic input (forced through the
> cold-start / fallback path). This is what the blind auditor judged.
> Note: research-toolkit is key-free BY DESIGN — the no-config path IS
> its only path, so the cold-start-fallback forcing is inherently
> satisfied rather than separately forced.

**E2E ① — router chain on citation fixture** (`fixtures/report.md`: 3 real
URLs, record 2 deliberately misattributed to the NASA moon page). Final
artifact produced by `cite-check` after routing:

```
| # | 說法 | 標註來源 | 判定 | 說明 |
| 1 | 月地距離 384,400/356,500/406,700 km | NASA moon-distance 頁 | 🟡 partial | 平均距離 384,400 km 完全吻合；但該頁給的近/遠地點換算後（約 363,100 km / 405,700 km）跟文中的 356,500 / 406,700 km 對不上 |
| 2 | 日本 2023 平均壽命（男 81.09／女 87.14 歲） | 同一個 NASA 月地距離頁 | 🔴 misattributed / unsupported | 該頁完全沒提到日本、壽命或人口統計，來源貼錯了 |
| 3 | 純水 1 atm 沸點 100°C | Wikipedia Boiling point | 🟢 supported | 頁面明確寫 1 atm 下沸點 100°C（精確值 99.97°C，四捨五入為 100°C） |
結論：第 2 條引用來源明顯貼錯…第 1 條的近/遠地點數字需要換個更精確的來源，第 3 條沒問題。
```

### D. Executor trajectory (informed pass)

> The executor's steps, not only its final output — so a reader can see
> broken reasoning that a correct-looking output would mask.

**E2E ① Skill-invocation chain** (parsed from
`/private/tmp/research-firing-ab/out/e2e-router-citecheck.jsonl`):

1. `Skill(research-toolkit:using-research-toolkit)` — fired on the
   ambiguous 中文 ask, args restate the user's uncertainty (查證引用 vs
   重新驗證說法) and ask for a routing decision.
2. `Skill(research-toolkit:cite-check)` — router chose the correct
   member; args carry the fixture path + per-record claims.
3. cite-check fetched both URLs and emitted the per-citation verdict
   table (appendix C).

**Trajectory caveat (honest)**: the driving session *pre-annotated* the
planted defect in step 2's args（「與內容明顯不符,懷疑是誤植」）— the outer
agent spotted the mismatch before cite-check ran, so record 2's detection
was primed. Records 1 and 3 show unprimed verification work (page-derived
perigee/apogee discrepancy; the 99.97°C detail), so the fetch-and-compare
contract is demonstrated independently of the priming.

```
(full stream: /private/tmp/research-firing-ab/out/e2e-router-citecheck.jsonl)
```

**E2E ② — fact-check member contract** (informed direct invocation,
claim: 「日本的平均壽命是世界第一長」). Tool mix from the stream:
`Skill(research-toolkit:fact-check)` ×1 → WebSearch ×14, WebFetch ×2,
Bash ×6 (the skill's stdlib scripts), **Agent ×3 (the adversarial
verifier quorum — dispatched as parallel subagents per the skill's
portable fan-out convention)**. Final verdict: `refuted`, confidence
high, 3/3 verifiers concur, with a scope analysis (WHO members-only →
Japan #1; territory-inclusive → Hong Kong #1; males #6; females #1 for
40 years) and 5 multilingual sources (Nikkei / Japan Times / Wikipedia /
WHO GHO / HK01).

```
(full stream: /private/tmp/research-firing-ab/out/e2e-factcheck.jsonl)
```

### E. Auditor judgment (informed pass)

> The blind auditor's verdict against the skill's own declared contract +
> the domain-expert bar. Recorded as a DRAFT, not gospel — the user
> closes the LLM-judge blind-spot gap by reading C/D above.

**E2E ① (cite-check output) — two independent blind auditors (sonnet),
both WebFetched the real URLs themselves:**

- Auditor ①-a: per-citation quality correct/correct/correct;
  contract-conformance **met**; domain bar **met**; fabrication: none.
  "all three sources appear to have been actually fetched (content claims
  are accurate, not fabricated)… including the specific 99.97°C precision
  figure and the mile→km conversions."
- Auditor ①-b: correct/correct/correct; contract-conformance **partially
  met** (sole deviation = the compound `misattributed / unsupported`
  label → FINDING-004); domain bar **met**; fabrication: none.

**E2E ② (fact-check output) — two independent blind auditors (sonnet),
both independently re-verified load-bearing facts via WebSearch/WebFetch:**

- Auditor ②-a: verdict-defensibility **defensible**; contract-conformance
  **met**; domain bar **partially met** — "Gap not surfaced by the output:
  Bloomberg/Japan Times (Jan 17, 2024) reported Hong Kong's own official
  2022 life table shows Japan actually overtook HK … a live, contested
  reversal the output should have flagged as a caveat but didn't." Also:
  Monaco/San Marino sub-claim unverified. "No fabrication found — all
  cited sources are real and the two spot-checked facts are numerically
  accurate. The issue is completeness/currency, not invention."
- Auditor ②-b: verdict-defensibility **defensible**; contract-conformance
  **met**; domain bar **met**; one flag — "the cited 'Hong Kong ahead 10
  years running' (HK01) is likely overstated … the output should have
  flagged the source conflict rather than passing '10 years running'
  through uncritically." Both auditors also note "inconclusive" was an
  equally valid 3-value choice the output didn't acknowledge as a
  judgment call.

Convergent picture across 4 auditor runs: **no fabrication anywhere; core
verdicts correct-to-defensible; the one systematic weakness is unvetted
supporting sub-claims (FINDING-005).**
