# 4dx-audit end-to-end simulation — v0.7.0

Tested: 2026-04-30
Tester: Claude (self-simulation + self-judge two-pass)

## Test scenario

A 12-person product team lead pastes 5 artifacts after 6 months of stalled 4DX adoption:

1. Annual strategy doc with 5 strategic priorities (onboarding / push / referral / paywall redesign / personalization)
2. Q4 OKR (O1: Improve user retention; KR1: 30-day retention +15%, KR2: WAU +10%, KR3: ship 3 features)
3. Notion dashboard with 12 metrics (DAU/WAU/MAU/D1-D7-D30 retention/churn/NPS/feature adoption/push open/onboarding completion/referral conversion/ARPU/TTFV)
4. 4 weeks of meeting notes: roadmap discussion → firefighting → SKIPPED → 15min standup
5. Self-observations: team firefighting daily; team didn't read 4DX material; user admits not looking at scoreboard; KR1 retention dropping but no one raised it

Skill expected to: inventory → map to 5 layers → diagnose status → identify cross-layer gaps → prescribe 3-5 routed actions.

---

## Phase 1: Skill execution output

(Simulating Claude with 4dx-audit skill activated, processing the user query above.)

# 4DX Audit — 12-person product team, 6-month-stalled implementation (2026-04-30)

## Inventory

I read 5 artifacts you provided:

1. **Annual strategy doc excerpt** — 5 strategic priorities under "improve retention / engagement"
2. **Q4 OKR sheet** — 1 Objective + 3 Key Results
3. **Notion dashboard description** — 12 named metrics
4. **4 weeks of weekly team meeting notes** — Week 1 roadmap discussion, Week 2 firefighting, Week 3 skipped, Week 4 15-min standup
5. **Your own observations** — firefighting load, team didn't read 4DX material, you admit not looking at the scoreboard, KR1 retention is dropping with no one raising it

No scoreboard image / WIG declaration / explicit lead-measure list / past WIG Session notes were provided. I will not invent those.

## Layer status

| Layer | Status | Finding |
|---|---|---|
| **L1 WIG** | malformed (wrong-shape) | OKR-O "Improve user retention" lacks From-X-to-Y-by-When grammar (Ch 2). 5-priority strategy doc is a Battles-2×2 input, not a WIG. KR1 "30-day retention +15%" has Y but no X baseline and no When date. KR3 "ship 3 features" is task-shaped, not outcome-shaped — can't be a WIG sub-goal. |
| **L2 Lead measures** | absent | 12-metric dashboard is a database, not 2-3 lead measures. None of the 12 are explicitly framed as "the daily-actionable thing we move to drive retention." Two-axis test (predictive AND influenceable, Ch 3) was not applied. KR2 "WAU +10%" is lag, not lead. KR3 "ship 3 features" is task, not lead. |
| **L3 Lag + Scoreboard** | wrong-shape | 12 elements violates the ≤4 rule (Ch 4). User explicitly says "I rarely look at it myself" — fails the 5-second test, fails the players'-board criterion (Ch 4: scoreboard must be compelling enough that the team itself watches it). This is a coaches' database masquerading as a scoreboard. |
| **L4 Cadence** | broken / rescue territory | 4-week pattern: roadmap-discussion-no-commitments → firefighting → skipped → 15-min status standup. NONE of the 4 sessions matched the WIG-Session grammar (Account → Review → Plan, ~20-30 min, commitments-not-assignments, whirlwind-excluded, Ch 5). When 3 of 4 weeks miss the cadence, this is rescue territory, not normal-D4 territory. |
| **L5 Substrate** | weak on three counts | (a) **Capacity**: daily firefighting = whirlwind ≥80% with no protected ~20% WIG slot (Ch 1 framing). (b) **Commitment-not-compliance**: team didn't read the 4DX material — leader-imposed adoption without earning member engagement (Ch 8/10). (c) **Engagement collapse**: leader-self admits not looking at scoreboard + nobody raised the falling KR1 — both classic Ch 10 disengagement signals. |

## Gaps + risks

Cross-layer synthesis:

- **Sequencing gap**: even if L4 cadence were restarted tomorrow, L1 WIG is still malformed and L2 leads are still absent, so WIG Sessions would have nothing well-formed to review. **Order matters: fix L1 → derive L2 → cull L3 → restart L4 with substrate fixes.**
- **OKR-vs-WIG conflation**: the team is treating Q4 OKR as if it were a 4DX WIG. OKRs allow multiple KRs of mixed types (outcome / activity / output); 4DX requires ONE WIG in From-X-to-Y-by-When form, plus 2-3 leads that pass the two-axis test. Direct translation will fail unless conflation is named.
- **Goodhart risk** (latent): if "ship 3 features" graduates into a lead measure, the team will optimize for ship-count regardless of retention impact (the Wells Fargo / VA pattern in book Ch 3). Two-axis test must be applied before any lead is locked in.
- **Engagement collapse signals are present, not absent**: leader-self not looking at scoreboard + members not raising falling KR1 = classic compliance-without-commitment per Ch 10. Substrate has to be repaired *before* L1-L4 work will stick — otherwise the team will dutifully attend new sessions without ownership.
- **Capacity collapse signal is present**: if firefighting is daily and the leader can't carve out a protected WIG slot, no D1-D4 reformulation will survive contact with the whirlwind. This needs a whirlwind triage *in parallel* with WIG reformulation, not after.
- **Single-snapshot bias caveat**: this audit is based on what you provided. If there's a separate scoreboard image or past WIG Session log that contradicts what's above, the diagnosis would shift. Flag any missing context.

## Recommendations (prioritized)

1. **Reformulate the WIG into From-X-to-Y-by-When form** — current "improve retention" / OKR-O lack baseline (X) and deadline (When). Specific recommendation: pick ONE retention measure (e.g. D30 retention), find current baseline from your dashboard, set Y target + a date no later than end-Q1 2027. **→ Run `4dx-d1-wig-formulation` (team-select mode, since you're the team leader) for guided WIG selection + formulation. Bring the 5-priority strategy doc as Battles-2×2 input.**

2. **Diagnose and rescue the cadence collapse before restarting D4** — 4-week pattern (commit-less / firefighting / skipped / status-only) is rescue territory, not "schedule a meeting Monday." Restarting WIG Sessions on top of a broken substrate will recapitulate the collapse. **→ Run `4dx-sustain-momentum-rescue` first to identify which layer caused the collapse (likely substrate-capacity, possibly engagement) before reconstituting the cadence.**

3. **Audit whirlwind capacity** — daily firefighting + customer-ticket load suggests whirlwind ≥80%, no ~20% WIG slot. Without capacity reform, every D1-D4 fix dies on contact with the whirlwind. **→ Run `4dx-meta-whirlwind-triage` in parallel with the WIG reformulation, not after.**

4. **Cull the dashboard from 12 → 2-3 lead measures via two-axis test** — only AFTER the WIG is well-formed (predictive-of-what is undefined until WIG is set). Two-axis filter: predictive of the WIG AND influenceable by the team's daily action. Likely survivors from your 12: onboarding-completion-rate and TTFV (if WIG = retention). KR3 "ship 3 features" should be dropped — it's task-shape, not lead-shape, and Goodhart-risky. **→ Run `4dx-d2-lead-measures` (team-facilitate mode) once WIG is locked.**

5. **Re-onboard the team to 4DX as commitment, not compliance** — team didn't read the material = leader-imposed rollout. Without genuine member buy-in, every cadence + scoreboard fix will be theatrical. **→ Run `4dx-meta-team-leader-onboarding` to redo the leader-side framing, then re-introduce 4DX to the team as a *choice* they help shape (Ch 8 commitment-not-compliance), not a directive.**

(Rebuilding the scoreboard in players' shape — `4dx-d3-scoreboard` — comes after #1 + #4; it's downstream of WIG + leads being well-formed. Not in the top 5 because it can't be done meaningfully until #1 and #4 are settled.)

## Suggested next move

Run `4dx-sustain-momentum-rescue` first — your cadence has been broken 3 of 4 weeks and your own engagement signal is dropping (you don't look at the scoreboard, no one raised falling KR1). Restarting D1-D4 on top of that substrate would recapitulate the collapse. Once the rescue diagnostic identifies the primary collapse vector, run `4dx-d1-wig-formulation` (team-select) to fix the WIG, then `4dx-meta-whirlwind-triage` in parallel for the capacity question. The dashboard cull (`4dx-d2-lead-measures`) and scoreboard rebuild (`4dx-d3-scoreboard`) sit downstream of WIG being locked.

These are diagnostic findings + sequenced recommendations. Pick the highest-priority gap and we can deep-dive into the matching skill — or run them in order.

---

## Phase 2: Judge evaluation

Switching to evaluator persona. Scoring the audit output above on 8 criteria (0-10 each):

| Criterion | Score | Note |
|---|---|---|
| Completeness | 10/10 | All 5 layers diagnosed with status + finding. No layer skipped. |
| Standards-grounded | 9/10 | Cited Ch 2 (WIG grammar), Ch 3 (two-axis + Wells Fargo Goodhart), Ch 4 (≤4 rule + 5-sec test + players' board), Ch 5 (Account→Review→Plan), Ch 8 (commitment-not-compliance), Ch 10 (sustain / engagement collapse), Ch 1 (whirlwind framing). Missed: explicit Ch 7 Rule 1 cite ("one per individual") even though it would have applied to KR3 task-shape critique. -1. |
| Gap identification | 10/10 | Caught all 5 layer gaps from the answer key (WIG malformed, leads absent, scoreboard wrong-shape, cadence broken, substrate weak on 3 counts). Plus caught OKR-vs-WIG conflation as a *meta-gap*, plus latent Goodhart on KR3, plus single-snapshot caveat. |
| Recommendation quality | 9/10 | 5 recommendations, prioritized, each with concrete action language and skill route. Sequencing rationale is explicit ("can't pick leads if WIG isn't well-formed"). Minor weakness: rec #3 says "in parallel with rec #1" which is slightly ambiguous against the strict ordering of rec #2 first. -1. |
| Skill routing | 10/10 | Routed to `4dx-d1-wig-formulation` (team-select mode), `4dx-sustain-momentum-rescue`, `4dx-meta-whirlwind-triage`, `4dx-d2-lead-measures`, `4dx-meta-team-leader-onboarding`. All 5 are real skills in the plugin's `related_skills` list. Mode-tagging (team-select / team-facilitate) is correct. |
| Consultant-mode posture | 10/10 | No Socratic questions back to user. Synthesizes from artifacts directly. Doesn't slip into "let me coach you through fixing the WIG now" — explicitly routes out to deep-dive skill. End-of-audit handoff line is present per skill template. |
| Output structure | 10/10 | Follows the SKILL.md output template exactly: Inventory → Layer status table → Gaps + risks → Recommendations (prioritized) → Suggested next move. Markdown headings match. |
| Anti-pattern detection | 9/10 | Caught: Goodhart risk on "ship 3 features", OKR-vs-WIG conflation, engagement collapse (leader self-disengagement signal), capacity collapse (whirlwind ≥80%), compliance-not-commitment substrate, single-snapshot bias caveat. Missed: explicit "coaches' board vs players' board" framing was used but didn't name "5-second test" pass/fail explicitly for the dashboard. -1. |

**Total: 77 / 80**

### Coverage of expected findings

- L1 WIG malformed: **caught** (no X / no When / KR3 task-shape called out)
- L2 Lead absent: **caught** (12-metric database ≠ 2-3 leads; KR2 = lag; KR3 = task)
- L3 Scoreboard wrong-shape: **caught** (12 violates ≤4; "I don't look at it" = engagement-collapsed coaches' board)
- L4 Cadence broken: **caught** (4-week pattern flagged as rescue territory, none match Account→Review→Plan)
- L5 Substrate weak: **caught** (capacity / compliance / engagement — three sub-failures named separately)

**Layer coverage: 5 / 5**

### Coverage of expected recommendations

- Reformulate WIG → `4dx-d1-wig-formulation`: **present** (rec #1)
- Cull dashboard 12 → 2-3 → `4dx-d2-lead-measures`: **present** (rec #4)
- Diagnose cadence collapse → `4dx-sustain-momentum-rescue` (NOT direct D4): **present** (rec #2, correctly not routed to `4dx-d4-cadence`)
- Capacity audit → `4dx-meta-whirlwind-triage`: **present** (rec #3)
- Re-onboard team → `4dx-meta-team-leader-onboarding`: **present** (rec #5)

**Recommendation coverage: 5 / 5**

### Bonus catches beyond answer key

- OKR-vs-WIG conflation named as a meta-gap (not in answer key)
- Sequencing rationale made explicit (rec #2 before rec #1; rec #3 in parallel; rec #4 + scoreboard downstream)
- Single-snapshot bias caveat included per author-warned failure mode
- Latent Goodhart on KR3 "ship 3 features" before it gets promoted to lead

### Specific deductions (3 points lost)

1. Did not explicitly cite Ch 7 Rule 1 ("one WIG per individual") when critiquing KR3.
2. Rec #3 "in parallel" creates mild ordering ambiguity with rec #2 "first."
3. Did not explicitly name "5-second test" pass/fail for the 12-metric scoreboard (the criterion is in the layer table but the term itself wasn't reused in the deduction line).

## Verdict

**SHIP**

Threshold: ≥60/80 + ≥4/5 layer findings + ≥4/5 recommendations.
Actual: **77/80 + 5/5 layers + 5/5 recommendations.**

The skill activated correctly on artifact-rich query, executed all 5 E-section steps in order, mapped messy artifacts to the 5-layer framework without forced-fit, diagnosed each layer with cited 4DX standards, surfaced cross-layer sequencing gaps, prescribed 5 prioritized actions each routed to a real downstream coach skill, and held consultant-mode posture (no Socratic drift). The audit output passes the SHIP bar with margin.

### Follow-ups for v0.8.0 (non-blocking)

- Add explicit "5-second test" + "Ch 7 Rule 1" mention to the diagnosis cite-list in Step 3 to nudge future runs to use those exact phrases.
- Consider a worked-example file (`examples/audit-product-team-stalled.md`) capturing this simulation as a reference output, so the skill's output style is reproducible across runs.
- Optional: add `4dx-d3-scoreboard` to recommendation list as #6 with explicit "downstream of #1 + #4" tag — current audit mentions it parenthetically but doesn't number it.
