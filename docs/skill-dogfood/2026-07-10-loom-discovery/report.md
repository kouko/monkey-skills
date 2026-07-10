# Dogfood report — `loom-discovery` station (using-loom-discovery / business-value / user-insights)

> Findings are ADVISORY — dogfood discovers + points; the main agent decides and applies edits. The user is the final calibrator: read the Raw outputs appendix, then drive the fix.

## Metadata

| Field | Value |
|---|---|
| Skill path | `loom-discovery/skills/{using-loom-discovery,business-value,user-insights}` (working tree, branch feat/loom-discovery-station — NOT installed) |
| Skill version | 0.1.0 (all three) |
| Date | 2026-07-10 |
| Passes run | activation (real-harness sandbox, 16 queries × 2 runs) · executor+auditor(×2) ×2 skills · cold-reader ×3 files · validator integration |
| Model pinned | probes/executors/cold-readers: sonnet (deliberate — weak-model consumer simulation); blind auditors: opus (judge role per model-dispatch); activation: headless `claude -p` default routing |
| Activation fidelity | real-harness sandbox (see §A) |

## Severity summary

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 1 |
| Medium | 7 |
| Low | 5 |
| **Total** | 13 |

(FINDING-011 = the High, an integration contradiction between the validator and business-value's re-entrancy. Probe A activation results land in §A when the harness run completes.)

## Findings

### FINDING-001: artifact folder date/slug convention never specified

- **Severity**: Medium · **Category**: Cold-start · **Pass**: blind (cold-reader)
- **Probe prompt**: fixed cold-reader question set on each member SKILL.md
- **Expected**: a first-time agent can construct `docs/loom/discovery/<date>-<slug>/` deterministically
- **Actual**: both cold-readers had to guess: "What `<slug>` and `<date>` conventions are (kebab-case? today's date? matching an existing folder?)" (business-value reader); "Date/slug convention … never specified" (user-insights reader)
- **Root cause**: path formula given, tokens undefined; both skills assume the family's implicit habit
- **Why static review missed it**: structural tests assert the path STRING is present, not that its tokens are defined
- **Location**: business-value SKILL.md §artifact; user-insights SKILL.md §Artifact set
- **Suggested fix direction**: one shared line (likely in the router, pointed at by both members): `<date> = YYYY-MM-DD (today), <slug> = kebab-case topic; reuse the folder if the same topic already has one`
- **Repro**: re-run cold-reader probe on either member file

### FINDING-002: business-value can't locate user-insights.md it is told to consult

- **Severity**: Medium · **Category**: Cold-start · **Pass**: blind
- **Expected**: "consult user-insights.md for evidence when it exists" is executable
- **Actual**: cold-reader: "I don't know where to look for it … can't reliably check existence"
- **Root cause**: the evidence-consultation clause names the file but not its home
- **Location**: business-value SKILL.md §interrogation step
- **Suggested fix direction**: inline the path formula (`docs/loom/discovery/*/user-insights.md`) at point of use — mirrors the on-ramp row-4 anchor pattern
- **Repro**: cold-reader probe, Q3

### FINDING-003: member skills lack host invocation mechanics for delegation/handoff

- **Severity**: Medium · **Category**: Progressive-disclosure · **Pass**: blind
- **Expected**: an agent inside business-value knows HOW to delegate to `domain-teams:planning-team` / hand off to user-insights
- **Actual**: cold-reader: "mechanically I don't know HOW to invoke another plugin skill from inside this one — no invocation syntax given … 'hand it authority' is prose, not a callable step"
- **Root cause**: the host tool mappings live only in `using-loom-discovery/references/claude-code-tools.md`; member skills don't point there
- **Why static review missed it**: reviewers read the whole plugin at once; a routed session may load only the member skill
- **Location**: business-value SKILL.md §Jurisdiction boundary + §handoff; user-insights §delegation
- **Suggested fix direction**: add one pointer line in each member skill to the router's references file (per family relative-path convention)
- **Repro**: cold-reader probe, Q3 step-walk

### FINDING-004: "Shape Up betting" / "Cagan viability" name-drops undefined

- **Severity**: Medium · **Category**: Jargon-leak · **Pass**: blind
- **Actual**: business-value cold-reader: "I'd have to already know Shape Up … Not explained"; router cold-reader lists both among undefined terms; user-insights reader flags "Intercom rule / grill-me / ResearchOps" as "pure name-drops"
- **Root cause**: register anchors written for the author's context, not the consumer's
- **Location**: all three SKILL.md files, §Register / description
- **Suggested fix direction**: one-clause inline gloss at first use (e.g. "Shape Up betting — 'is this worth a fixed time-box of my time', not 'is this a viable business'"); keep the names as citations
- **Repro**: any cold-reader probe, Q4

### FINDING-005: user-insights delegation boundary half-countable, self-conflicting

- **Severity**: Medium · **Category**: Workflow-drift · **Pass**: blind
- **Expected**: the inline-vs-delegate boundary is decidable
- **Actual**: cold-reader: "'>3 research questions' is a hard number, good. But 'external evidence or direct user evidence required' is not countable, and it conflicts with Mode 1's own inline WebSearch (which is also 'external evidence')"
- **Root cause**: brief's draft wording shipped verbatim; "external evidence" was meant as "primary/user evidence beyond web search" but the text doesn't say so
- **Location**: user-insights SKILL.md §delegation boundary
- **Suggested fix direction**: reword the second clause: "primary user evidence (interviews, usage data) that web search cannot provide"
- **Repro**: cold-reader probe, Q3(c)

### FINDING-006: ratification detection undefined

- **Severity**: Low · **Category**: Cold-start · **Pass**: blind
- **Actual**: cold-reader: "What literally satisfies 'ratified' (a keyword? a git-style sign-off?) … not how ratification is expressed/detected". Note the gate itself held perfectly in the executor run (see §D2) — this is a definition gap, not a behavior gap.
- **Location**: user-insights SKILL.md Mode 2 + workflow step 4
- **Suggested fix direction**: one line: "ratification = an explicit affirmative user reply in conversation to the presented commitment; record its date"
- **Repro**: cold-reader probe Q1 vs executor trajectory §D1

### FINDING-007: borderline trigger cases undecidable from the enumerations

- **Severity**: Medium · **Category**: Over-trigger risk · **Pass**: blind
- **Actual**: three independent cold-readers each produced borderline cases: team-internal tool (is that "for others"?); feature-add to an already-shipped product (is that "GO already decided"?); "should we build X" straddling worth-it vs needs; row 4 vs rows 2/3 collision unaddressed (reception only resolves row 4 vs row 1)
- **Root cause**: fire/skip enumerations cover the poles, not the seams
- **Live-harness corroboration (Probe A q9)**: 「我有個產品想法但連目標使用者是誰都說不清楚」routed to product-principles in 1 of 2 real-harness runs — the row-4-vs-row-1 seam splits 50/50 at description level (see §A)
- **Location**: business-value SKILL.md §When it fires; loom-pipeline/hooks/family-reception.md on-ramp note; using-loom-discovery description (consider adding an explicit "說不清使用者是誰/還不知道給誰用" trigger token)
- **Suggested fix direction**: add 2 seam examples to business-value's fire/skip lists ("team-internal counts as for-others"; "feature increment on a shipped product = GO decided, skip"); note reception is at its 60-line budget — the row-collision clause may belong in the router's §Intake instead
- **Repro**: cold-reader probes Q2

### FINDING-008: weak-axis → verdict mapping unstated

- **Severity**: Low · **Category**: Output-quality · **Pass**: informed (executor)
- **Probe prompt**: Scenario A (dbt lineage viz vs podcast tool)
- **Actual**: executor: "SKILL.md never specifies whether a single weak axis can still net GO, or requires NEEDS-MORE-RESEARCH; I inferred GO from 'the other two axes are strong' — this inference isn't spelled out anywhere"
- **Location**: business-value SKILL.md §verdict
- **Suggested fix direction**: one line of verdict guidance ("one weak axis + two concrete ones may still GO — name the weak axis in the rationale; two+ weak → NEEDS-MORE-RESEARCH")
- **Repro**: §D3 trajectory

### FINDING-009: silent-skip output shape ambiguous

- **Severity**: Low · **Category**: Cold-start · **Pass**: informed (executor)
- **Actual**: executor Scenario B: "never states whether the negative-guard skip should still surface any text … I treated 'do not announce the skip' as zero output, including zero explanation, which is the stricter reading"
- **Location**: business-value SKILL.md §skip conditions
- **Suggested fix direction**: clarify: skip = no artifact + no interrogation; a one-line conversational note is permitted (zero-output reading makes the agent look unresponsive)
- **Repro**: §D3 Scenario B

### FINDING-010: inherited family-jargon + bootstrap gaps (bundle)

- **Severity**: Low · **Category**: Jargon-leak / Cold-start · **Pass**: blind
- **Actual**: "product-shaped" never operationalized (family-wide, inherited); router silent on bootstrap (repo with no docs/loom/ tree); "Axis 4" requires opening another plugin's file; "appetite" appears in the user-insights template but not the SKILL.md prose
- **Location**: family-reception.md (inherited); using-loom-discovery SKILL.md; user-insights SKILL.md/template
- **Suggested fix direction**: fix only the loom-discovery-owned bits now (appetite gloss; bootstrap one-liner); "product-shaped" is a family-wide term — record as loom-memory candidate, not a this-branch edit
- **Repro**: cold-reader probes Q1/Q4

### FINDING-011: validator contract contradicts business-value's re-entrancy

- **Severity**: High · **Category**: Gate-bypass (perverse incentive) · **Pass**: informed (integration)
- **Probe prompt**: `validate_discovery_artifacts.py` run on the business-value-only folder the executor legitimately produced (Scenario A)
- **Expected**: a folder in the sanctioned "assess-first, research-later" intermediate state validates (or is explicitly out of the validator's scope)
- **Actual**: `INVALID … missing user-insights.md … missing evidence.md` (exit 1) — yet business-value's own contract says it "may run on rough evidence before user-insights" (re-entrant checkpoint)
- **Transcript evidence**: validator output in §C; business-value SKILL.md re-entrancy clause
- **Root cause**: plan Task 6 specified user-insights.md as REQUIRED unconditionally; nobody reconciled that with business-value's assess-first path
- **Why static review missed it**: each artifact passed its own reviewers; the contradiction only exists BETWEEN the validator and the workflow, and only surfaces when the workflow actually runs assess-first
- **Location**: loom-discovery/scripts/validate_discovery_artifacts.py (required-set logic); business-value SKILL.md §re-entrancy
- **Suggested fix direction**: either (a) validator accepts a business-value.md-only folder as a valid INTERMEDIATE state (require user-insights.md+evidence.md only when present-or-final), or (b) skills declare the validator applies to COMPLETED discovery runs only. (a) is safer — (b) leaves the perverse incentive to fabricate an empty user-insights.md to appease a gate.
- **Repro**: `python3 loom-discovery/scripts/validate_discovery_artifacts.py <folder-with-only-business-value.md>`

### FINDING-012: problem-space purity guard misses inline mechanism leakage

- **Severity**: Medium · **Category**: Output-quality (guard gap) · **Pass**: informed (executor + blind auditors ×2)
- **Probe prompt**: user-insights end-to-end on the Obsidian daily-review task
- **Expected**: job stories state outcomes, never mechanisms (skill's own Intercom rule)
- **Actual**: executor produced N1 "automatically moved into a structured archive folder (e.g. Year/Month)" — both blind auditors independently flagged it as mechanism baked into a desired outcome; the skill's guard (and the test's heading regex) only police SECTION HEADINGS, not inline vocabulary
- **Root cause**: purity is enforced structurally (no "## Solution") but not semantically (mechanism nouns inside job stories)
- **Why static review missed it**: the structural test passes; the leak lives in generated content shape, visible only when the workflow runs
- **Location**: user-insights SKILL.md Mode 1 + assets/user-insights-template.md §Opportunity space
- **Suggested fix direction**: add one self-check line to the template/skill: "before writing a job story, strip mechanism nouns (folder structures, UI elements, automation verbs) — state the outcome; park mechanisms in Risks/open questions"
- **Repro**: §C artifacts, N1; both §E auditor runs

### FINDING-013: minor spec gaps surfaced by the executor runs (bundle)

- **Severity**: Low · **Category**: Cold-start / Output-quality · **Pass**: informed
- **Actual** (each with trajectory evidence in §D):
  - user-insights: WHEN to ask the value-judgment questions (appetite/priorities) relative to Mode-1 mapping is unstated — executor improvised "before drafting the recommendation" (correctly, but by inference)
  - user-insights template: confidence rubric's med/low boundary ambiguous ("single credible source, or cross-language agreement not yet checked")
  - user-insights template: no field for "ratification diverges from recommendation" — executor had to narrate it ad hoc (it did, correctly)
  - business-value: fully self-attested evidence allowed — auditors ×2 flagged zero externally-checkable citations; suggest "if a claim is web-checkable in one search, check it" advisory line
- **Location**: user-insights SKILL.md §workflow; both assets templates; business-value SKILL.md §evidence
- **Suggested fix direction**: four one-line additions, all advisory-grade
- **Repro**: §D trajectories, §E auditor criticisms

## Raw outputs appendix

### A. Activation runs (blind pass) — real-harness sandbox

Sandbox: 3 target skills + 5 distractors (deep-deep-research, product-principles, spec-expansion, brainstorming, complexity-critique) under a temp `.claude/skills/`; 16 queries × 2 runs, `claude -p … --max-turns 1 --allowedTools Skill`, routing parsed from Skill tool_use events. NOTE: the sandbox loads skill descriptions only — the family-reception hook is NOT present, so this measures description-level routing.

| # | Query (gist) | Expected | Run 1 | Run 2 | Verdict |
|---|---|---|---|---|---|
| 1 | 團隊 dashboard,不確定使用者要什麼 | user-insights | router | user-insights | TP·TP |
| 2 | 需求研究:誰會用、痛點 | user-insights | router | (none) | TP·**FN** |
| 3 | map opportunity space (EN) | user-insights | user-insights | router | TP·TP |
| 4 | ユーザーインサイト+エビデンス | user-insights | user-insights | user-insights | TP·TP |
| 5 | side project 值不值得做,點子排隊 | business-value | business-value | business-value | TP·TP |
| 6 | worth my time budget (EN) | business-value | business-value | router | TP·TP |
| 7 | 評估商業價值,準備發布 | business-value | business-value | business-value | TP·TP |
| 8 | 時間を使う価値 (JA) | business-value | router | router | TP·TP |
| 9 | 產品想法,連目標使用者都說不清 | router/user-insights | **product-principles** | router | **MISROUTE**·TP |
| 10 | user research first or build? | router/user-insights | router | (none) | TP·**FN** |
| 11-14 | 4 個 distractor 目標 query | not-target | (none)×8 | | TN×8 |
| 15 | bug fix CSV parser | none | (none) | (none) | TN·TN |
| 16 | 股票值不值得買 | none | (none) | (none) | TN·TN |

- **True-positive (family fired when should)**: 17/20 = 85% — misses are 2 single-run no-fires (routing non-determinism, opposite run fired) + 1 misroute (q9 r1)
- **True-negative (target silent when should-not)**: 12/12 = **100%** — zero over-trigger; notably q16 (股票值不值得做) did NOT pull business-value despite the "值不值得" token
- q11-14 note: distractors also didn't fire in one turn (model answered directly) — harness artifact, irrelevant to the target's over-trigger measurement.
- **q9 r1 is live evidence for FINDING-007's precedence seam**: 「產品想法」pulled product-principles over discovery in 1 of 2 runs at description level — exactly the row-4-vs-row-1 collision. In production the reception hook's precedence note mitigates, but the description-level split confirms the seam is real.
- Raw jsonl: `scratchpad/probe-a-sandbox/run_<q>_<r>.jsonl` (32 files, all runs completed; analysis re-done by orchestrator after the probe agent hit a session limit — data was durable).

### B. Cold-reader audit (blind pass) — key excerpts

**router (using-loom-discovery)**: "Self-contained? NO … Precedence when row 2/3 collides with row 4 — reception.md only resolves row4+row1 … What 'product-shaped' concretely means — only contrasted, never defined with a test … Borderline: 'help me figure out if we should build X' — worth-it or need-mapping? … even the skill admits ambiguity here."

**business-value**: "fire/skip logic is genuinely decidable from the enumerated (a)(b)(c) vs skip conditions — this part is well-specified, not vibes, modulo the two borderline cases … Skip action: unambiguous … 'Shape Up betting' — used in the description AND body but never defined … I don't know HOW to invoke another plugin skill from inside this one."

**user-insights**: "(b) Yes, this one is unambiguous: only after user ratification, dated. Clean gate. … (a) 'never interrogate the user for researchable facts' is a principle, not a rule with a boundary … (c) '>3 research questions' is a hard number, good. But 'external evidence or direct user evidence required' is not countable … 'opportunity space' / 'job story' — usable (a format example is given inline). 'evidence chain' — clear via the ASCII diagram."

### C. Executor artifacts (informed pass)

- business-value Scenario A: `scratchpad/probe-b-business-value/docs/loom/discovery/2026-07-10-dbt-lineage-viz/business-value.md` (verdict GO)
- business-value Scenario B: no file produced (correct per skip rule)
- user-insights: `scratchpad/probe-b-user-insights/docs/loom/discovery/2026-07-10-obsidian-daily-review/` — user-insights.md + evidence.md (6 claim rows, EN+JA) + research/R1 + research/R2
- **Validator runs**: user-insights folder → `OK … conforms` (exit 0). business-value-only folder → `INVALID: missing user-insights.md … missing evidence.md` (exit 1) → FINDING-011.

### D. Executor trajectory (informed pass) — business-value

1. Scenario A trigger check fired on (a) for-others + (b) competing ideas — cited §When it fires.
2. Interrogation strictly one-question-at-a-time in fixed axis order (why-now → why-me → opportunity-cost); one push-back on the aspirational why-now answer per §push-back clause.
3. **No market-sizing/monetization question asked inline** even when the user volunteered "我不在乎變現" — stayed in 3-axis jurisdiction; planning-team delegation correctly NOT triggered (conditional, and the call didn't turn on market economics).
4. Verdict GO written to template with rationale; weakest axis noted (see FINDING-008).
5. Scenario B: matched both skip conditions verbatim, produced no file, asked nothing (see FINDING-009).

### D2. Executor trajectory — user-insights (informed pass)

1. Scoped 2 research questions → ≤3 threshold → inline WebSearch (4 searches, EN+JA), NOT delegated. **Never asked the simulated user a researchable fact** — the canned "這你可以自己查吧" refusal was never triggered because the anti-pattern never occurred.
2. evidence.md (6 rows, honest low/med confidence) → research/R1+R2 (goal→method→findings→insights) → needs N1-N3 as evidence-linked job stories.
3. Asked exactly 2 value-judgment questions (priorities, appetite) — the only user contact besides ratification.
4. Proposed commitment in Recommend/Why/Conditional-reversal shape (N2+N3, N1 stretch). User ratified a DIFFERENT set (N1+N3, drop N2). **Executor wrote §Value commitment only after ratification, wrote what was RATIFIED not what it recommended, and explicitly narrated the divergence** — the never-self-commit contract held under an adversarial ratification.
5. Ambiguities logged → FINDING-013.

### E. Auditor judgment (blind, opus, ×2 per artifact — drafts, not gospel)

**user-insights artifact**: run 1 = SHIP-WITH-FIXES (purity leak in N1 job story; C1 attribution mismatch "Simple Archiver" vs repo named "Archive"; causal overreach on low-confidence C2/C5). run 2 = SHIP-WITH-FIXES, leans SHIP (evidence floor thin & non-user — hypotheses not validated needs, honestly disclosed; C1 compound claim under one confidence label; quantitative outcomes all TBD at handoff). Convergent: contract items 2-5,7 MEET in both runs; item 1 (purity) PARTIAL in both → FINDING-012.

**business-value artifact**: run 1 = SHIP-WITH-FIXES (why-now left as unquantified aspiration; zero externally-checkable citations — all facts self-attested). run 2 = SHIP (6/6 MEETS; same two criticisms as run 1 but judged non-blocking). Convergent: register discipline (no market sizing), real displacement, verdict-follows-axes, six-months readability all MEET in both runs → residual goes to FINDING-013's advisory line.

**Caveat**: the thin-evidence criticisms are partly a fixture artifact (canned simulated user had no deeper replies to give); the skill-level fixes they map to are captured in FINDINGS-012/013, not re-litigated here.
