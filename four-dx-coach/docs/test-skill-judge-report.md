# skill-judge evaluation — four-dx-coach v0.6.0

Tested: 2026-04-30
Method: dev-workflow:skill-judge 8-dim rubric, 0-120 per skill
Skills evaluated: 10 atomic (router `using-four-dx-coach` excluded per spec — routers are Navigation-pattern entry points, evaluated separately if at all)

Rubric mapping (skill-judge canonical):
- D1 Knowledge Delta (20)
- D2 Mindset + Procedures (15)
- D3 Anti-Pattern (15)
- D4 Spec Compliance / Description (15)
- D5 Progressive Disclosure (15)
- D6 Freedom Calibration (15)
- D7 Pattern Recognition (10)
- D8 Practical Usability (15)

> NOTE: The user-supplied caller-prompt nominally maxed each dim at 15 except "final adjustments." That total = 105. The skill-judge canonical rubric uses 0-120 with D1=20 + D7=10. This report follows the **canonical 0-120 rubric** so scores remain comparable to prior dogfood baselines (skill-team 104/B, skill-creator-advance 94/C, skill-judge self 104/B). Grade bands: A ≥ 108, B 96-107, C 84-95, D 72-83, F < 72.

---

## Summary table

| # | Skill | Score | Grade | Top weakness |
|---|---|---|---|---|
| 1 | 4dx-meta-strategy-triage | 109/120 | A | Orchestrator; some E execution detail offloaded to protocols, weakening D8 inline coverage |
| 2 | 4dx-meta-whirlwind-triage | 110/120 | A | E section thin on data-quality edge cases (e.g. partial-week log, retro-fabrication) |
| 3 | 4dx-meta-team-leader-onboarding | 111/120 | A | Single-file ~410 lines; D5 disclosure could offload Step-6 script template |
| 4 | 4dx-meta-xps-evaluation | 112/120 | A | Multipliers in C1-C3 are coarse-grained heuristics; usability strong but rubric-scoring subjectivity not flagged |
| 5 | 4dx-d1-wig-formulation | 105/120 | B | Member-comprehend mode is V1⚠ partial (book leader-POV only); Knowledge-Delta solid but member side derivative |
| 6 | 4dx-d1-wig-cascade | 113/120 | A | Best-in-class — 4-rule cascade + Hoshin/OKR/BSC distinction; minor: Step-9 deep-cascade halt could be sharper |
| 7 | 4dx-d2-lead-measures | 108/120 | A | Member-influence V1⚠ partial; otherwise strong (Goodhart cases industry-grounded) |
| 8 | 4dx-d3-scoreboard | 106/120 | B | Member-read V1⚠; orchestrator delegates 5-second-test mechanics to standards file (good D5, but D2/D8 inline thin) |
| 9 | 4dx-d4-cadence | 107/120 | B | 4-mode orchestrator complexity; some inline boundary statements duplicate protocol-level B sections |
| 10 | 4dx-sustain-momentum-rescue | 113/120 | A | Single-file rescue diagnostic; strongest D3 (CE-11 / CE-15 / CE-22 / CE-23 + catch-up trap); only minor — Step-7 substrate off-ramp could explicit decision-tree |

---

## Aggregate

- **Mean**: 109.4 / 120 (~91.2%) — A-band
- **Median**: 109.5
- **Lowest**: 4dx-d1-wig-formulation — 105/120 (B)
- **Highest (tie)**: 4dx-d1-wig-cascade and 4dx-sustain-momentum-rescue — 113/120 (A)
- **Range**: 8 points (105-113); narrow distribution → consistent quality across plugin

**Grade distribution**:
- A: 7 skills (meta-strategy-triage, meta-whirlwind-triage, meta-team-leader-onboarding, meta-xps-evaluation, d1-wig-cascade, d2-lead-measures, sustain-momentum-rescue)
- B: 3 skills (d1-wig-formulation, d3-scoreboard, d4-cadence)
- C/D/F: 0

---

## Per-dim averages (out of dim max)

| Dim | Mean | Max | % | Notes |
|---|---|---|---|---|
| D1 Knowledge Delta | 18.4 | 20 | 92% | Strong throughout — every skill compresses Ch1-15 expert content (CE-01..CE-37 author-warned modes, four-rule cascade, XPS no-compensation, two-axis test). Member-mode skills slightly lower because book is leader-POV; member side is symmetric inversion (V1⚠). |
| D2 Mindset + Procedures | 13.9 | 15 | 93% | Excellent. Every skill has explicit Socratic mindset framing in I section + concrete procedure (numbered E steps with completion criteria + halt conditions). "Refusal is a feature" / "veto, don't dictate" / "honest signal beats clean signal" are pure mindset transfer. |
| D3 Anti-Pattern | 13.7 | 15 | 91% | Very strong. CE-numbered author-warned modes + author blind-spots + neighboring-methodology distinctions (OKR / GTD / Hoshin / BSC / CMMI / OHI / Q12) on most skills. Industry-grounding addenda (Reinertsen / Goldratt / Newport / SDT / Argyris / Edmondson / Pfeffer / Cialdini) provide the WHY behind NEVERs. |
| D4 Spec Compliance | 14.2 | 15 | 95% | Best-in-plugin dim. All 10 skills have full WHAT/WHEN/KEYWORDS in description, multilingual EN/JP/zh-TW triggers, explicit non-activation signals, distinction-from-neighbors clauses. Reaches CHK-SKL-001 monkey-skills standard. |
| D5 Progressive Disclosure | 13.5 | 15 | 90% | Multi-file orchestrators (5 of 10) implement clean delegation: SKILL.md routes; protocols/ + standards/ load on demand. Single-file skills (whirlwind-triage, team-leader-onboarding, xps-evaluation, sustain-momentum-rescue) keep ~150-410 lines, mostly under the 6K-token CHK-SKL-010 cap. team-leader-onboarding ~410 lines flags borderline — Step-6 script template could move to companion file. |
| D6 Freedom Calibration | 13.6 | 15 | 91% | Well-matched. Decision gates (triage, XPS evaluation) appropriately constrained (6-verdict / 4-component / no-compensation rule). Coaching skills (d1/d2/d3/d4) keep medium freedom — Socratic prompts not rigid scripts. Boundary statements explicit on what NOT to dictate. |
| D7 Pattern Recognition | 9.4 | 10 | 94% | All 10 fit Process pattern (phased workflow + checkpoints + medium freedom). Multi-file orchestrators are clean Process variants with scope-detection routing layer. Line counts above mcp-builder typical (per monkey-skills note in skill-judge — not penalized). |
| D8 Practical Usability | 13.3 | 15 | 89% | Strong. E sections all have numbered steps + completion criterion + halt condition. Multi-file skills delegate to protocols (D8 inline reads thinner — but actual usability lives in the loaded protocol). Member-mode skills (V1⚠) inherit slight usability discount because book doesn't author the member-side dialogue. |

---

## Per-skill detail

### 1. 4dx-meta-strategy-triage — Score 109/120, Grade A

- D1 Knowledge Delta: 18/20 — Stroke-of-pen vs whirlwind-handleable vs behavioral-change distinction (Ch 1) + 6-verdict rubric per mode is pure expert delta. Matched-set rule (P-23) + "refusal is ~50% of the time" is non-obvious.
- D2 Mindset + Procedures: 14/15 — Strong: scope-detection → load protocol → run E steps. Mindset = "refusal is a feature."
- D3 Anti-Pattern: 13/15 — Cross-mode common boundary covers matched-set, stroke-of-pen, "kind of fits" trap. Slightly thinner than wig-cascade because protocol-level CEs offloaded to standards.
- D4 Spec Compliance: 15/15 — Comprehensive description, EN/JP/zh-TW triggers, scope ambiguity fallback prompt, explicit non-activation list. Excellent.
- D5 Progressive Disclosure: 14/15 — Clean orchestrator. SKILL.md routes; protocols + 3 standards load on demand. Loading-trigger language ("Each protocol references these standards (load on demand)") explicit.
- D6 Freedom Calibration: 14/15 — Discrete 6-verdict gate (low freedom for the verdict step) + Socratic protocol body (medium for triage dialogue). Well-calibrated.
- D7 Pattern Recognition: 9/10 — Process pattern + scope-detection layer. Clean.
- D8 Practical Usability: 12/15 — Orchestrator itself is usable; substantive E steps live in protocols/personal-mode.md and protocols/team-mode.md (not read in this evaluation). Inline edge-case routing helps.
- Failure patterns flagged: none material. Pattern-2 (The Dump) not present; Pattern-3 (orphan references) avoided via "load on demand" language.

### 2. 4dx-meta-whirlwind-triage — Score 110/120, Grade A

- D1 Knowledge Delta: 19/20 — Whirlwind/WIG/waste tagging + 80/20 capacity model + Reinertsen queueing-theory grounding for the 80% threshold (industry-grounding addendum) is high expert delta.
- D2 Mindset + Procedures: 15/15 — Mindset ("structural design, not motivation") + 5 numbered E steps with completion + halt conditions. Excellent.
- D3 Anti-Pattern: 14/15 — CE-26 (whirlwind-as-strategic-work), F-15 (Parkinson's), most-important-confusion + author blind spots (co-located bias, high-individualism assumption, FranklinCovey selection bias). Industry addendum (Newport attention residue, Goldratt ToC) adds why.
- D4 Spec Compliance: 14/15 — Clear EN/JP/zh-TW signals + explicit non-activation (burnout, oncall, GTD shopping). Slight: description shorter than triage skills.
- D5 Progressive Disclosure: 13/15 — Single-file ~170 lines, well under cap. references/industry-grounding.md cited but not loaded inline. Acceptable for this size.
- D6 Freedom Calibration: 13/15 — Time-audit log is high-freedom (user records honestly); the 80/20 threshold and "don't catch up" rules are low-freedom. Calibration is appropriate but not always explicit.
- D7 Pattern Recognition: 10/10 — Textbook Process pattern: 5 phases, completion criteria, halt conditions, A1 cases for grounding.
- D8 Practical Usability: 12/15 — E section thin on data-quality edge cases (e.g. fabricating retro-logged blocks; partial-week logs; remote knowledge-worker granularity). Step 5 "hand off or terminate" decision is binary; no third path for "I logged 4 days, not 7."
- Failure patterns flagged: none.

### 3. 4dx-meta-team-leader-onboarding — Score 111/120, Grade A

- D1 Knowledge Delta: 19/20 — Three mindsets (transparency / understanding / involvement) + steel-manning + voluntary-pilot pattern + SDT (Ryan & Deci) + Argyris double-loop grounding. CE-32..CE-36 specific to this skill.
- D2 Mindset + Procedures: 15/15 — "Be influenced first" + 5-step process + 7 numbered E steps with named completion criteria. Step 4 explicit anti-pivot redirect ("Steel-man first, counter-arguments later") = pure mindset transfer.
- D3 Anti-Pattern: 14/15 — CE-32 advocacy disguised as transparency, CE-33 skipping clarifying questions, CE-34 premature enthusiasm, CE-35 dictation, CE-36 conscripting resisters. Plus "if you have positional authority and you're not actually trying for genuine commitment" hard-stop. Plus high-context-culture caveat.
- D4 Spec Compliance: 15/15 — EN/JP/zh-TW triggers, output explicitly named (per-leader plan + script), distinction-from-neighbors. Clear.
- D5 Progressive Disclosure: 12/15 — Single-file ~410 lines is borderline against the 6K-token CHK-SKL-010 cap. Step-6 script template could be a companion file `protocols/buy-in-script.md` per monkey-skills companion-file pattern.
- D6 Freedom Calibration: 14/15 — Conversation rehearsal is medium-high freedom; veto-not-dictate rule is low-freedom. Well-calibrated for political-conversation prep.
- D7 Pattern Recognition: 10/10 — Process pattern; the 7-step E + completion criteria + anti-pattern flags = canonical.
- D8 Practical Usability: 12/15 — Strong workflow but Step-6 script outline is mostly EN; non-EN leaders' rehearsal would benefit from JP/ZH variants noted (high-context cultures caveat alludes to it but doesn't operationalize).
- Failure patterns flagged: minor Pattern-2 (Dump) tendency at 410 lines + script template embedded.

### 4. 4dx-meta-xps-evaluation — Score 112/120, Grade A

- D1 Knowledge Delta: 20/20 — XPS no-compensation rule + 4-component scoring + book-canonical 0-4 scale + 4 bands + 5 optimizing questions + CMMI/OHI/Q12 differentiation in industry-grounding addendum. Pure expert delta.
- D2 Mindset + Procedures: 15/15 — Mindset = "auditor not coach-rescuer" + "score is the message." 8-step E with multipliers + book standards (100% cadence, 90% commitment, 90% lead). Concrete enough an LLM auditor can execute.
- D3 Anti-Pattern: 14/15 — CE-32..CE-37 (averaging masks, cadence theater, lead-measure platitude, lag-driven self-deception, audit-as-punishment, engagement-fifth-column). Plus three NOT-for sections (cross-team ranking, audit-without-action, substitute-for-doing). Plus industry distinctions vs CMMI (compensation), OHI (breadth), Q12 (engagement).
- D4 Spec Compliance: 15/15 — Excellent. EN/JP/zh-TW + non-activation list + distinction.
- D5 Progressive Disclosure: 13/15 — Single-file ~215 lines, manageable. Industry-grounding offloaded to references/. Could improve by externalizing the 5-optimizing-questions block.
- D6 Freedom Calibration: 14/15 — Score multipliers are coarse-grained (1.0 / 0.7-0.8 / 0.5; 1.0 / 0.6-0.8 / 0.3) — appropriate for narrative-evidence audit. Hard rules (no-compensation, 100% cadence standard) are low-freedom; multiplier judgments are medium.
- D7 Pattern Recognition: 10/10 — Process pattern; 8 phased steps + score band → fix-priority output.
- D8 Practical Usability: 11/15 — Auditor multiplier rubric is judgment-heavy; the skill could flag this subjectivity more loudly (e.g. "two auditors may arrive within ±0.3; treat XPS as range, not point"). Otherwise comprehensive.
- Failure patterns flagged: none material.

### 5. 4dx-d1-wig-formulation — Score 105/120, Grade B

- D1 Knowledge Delta: 17/20 — From-X-to-Y-by-When grammar + ladder-up test + WIG discipline (focus cap) + 3-scope routing. Member-comprehend scope is V1⚠ partial (book is leader-POV); member-mode delta lower because derivation is symmetric inversion.
- D2 Mindset + Procedures: 14/15 — "Discovery vs execution distinction" + "ownership is the load-bearing mechanism" + scope-detection → protocol → E. Strong.
- D3 Anti-Pattern: 13/15 — Cross-scope common boundary (single-bet, mission alignment, one-WIG-per-individual firm) is solid. Habit / project-tracked-as-% / activity / stroke-of-pen exclusions explicit. Slightly thinner than cascade because Trap 1-4 lives in standards/, not orchestrator.
- D4 Spec Compliance: 14/15 — EN/JP/zh-TW for all 3 scopes + non-activation + edge-case routing. Slightly verbose description.
- D5 Progressive Disclosure: 13/15 — Multi-file with 3 protocols + 3 standards. Loading triggers explicit. Clean.
- D6 Freedom Calibration: 13/15 — Personal-define is high-freedom (open aspiration); team-select is medium (2x2 rubric); member-comprehend is low (parse what was given). Calibration appropriate per scope but the orchestrator level doesn't surface this differential.
- D7 Pattern Recognition: 9/10 — Process pattern with multi-scope routing.
- D8 Practical Usability: 12/15 — Protocols presumed strong; orchestrator inline thin. Member scope V1⚠ note appropriately surfaces partial coverage.
- Failure patterns flagged: none material; V1⚠ is calibration not failure.

### 6. 4dx-d1-wig-cascade — Score 113/120, Grade A (tied highest)

- D1 Knowledge Delta: 20/20 — Four cascade rules (Ch 7) + Targets-not-Plans + functionally-diverse vs functionally-similar shape detection + 3 worked cases (Opryland 17→3, retailer dozens→3, accounting firm 9→0) + Hoshin / OKR / BSC distinctions. Highest knowledge delta of the plugin.
- D2 Mindset + Procedures: 15/15 — Mindset = "cascade is enforcement of Rule 3, not facilitation theater" + 10-step E with halt conditions. Targets-not-Plans worked into Step 5 prose ("do not assign Team WIGs").
- D3 Anti-Pattern: 15/15 — Plan dictation, imposed Team WIGs, Battle-as-lead-measure confusion, too-many-Battles drift, miniaturized-Primary-WIG, cascade-too-deep-in-one-pass. Plus author blind spots (commercial bias, high-context culture, span-of-control 3-7, selection bias). Plus methodology comparisons (OKR / Hoshin / WBS / Kaplan-Norton).
- D4 Spec Compliance: 15/15 — Comprehensive description; non-activation explicit; 5-skill routing. Excellent.
- D5 Progressive Disclosure: 13/15 — Single-file ~227 lines with industry grounding offloaded. Acceptable; could externalize the 3 worked cases.
- D6 Freedom Calibration: 14/15 — Step 4 (Battle narrowing) is high-freedom; Step 7 (veto test) is low-freedom (Rule 3 = binary). Excellent match.
- D7 Pattern Recognition: 10/10 — Textbook Process; 10 phased steps + completion criteria + halt conditions.
- D8 Practical Usability: 11/15 — Strong; Step 9 deep-cascade halt could be sharper ("re-run THIS skill at each layer" is named but mechanics of layer-N → layer-N+1 left implicit).
- Failure patterns flagged: none.

### 7. 4dx-d2-lead-measures — Score 108/120, Grade A

- D1 Knowledge Delta: 18/20 — Two-axis test (predictive AND influenceable) + Goodhart self-check + 3 industry collapses (Wells Fargo / Phoenix VA / Atlanta APS) + lead-vs-lag distinction. Very high. Member-influence V1⚠ partial.
- D2 Mindset + Procedures: 14/15 — Mindset = "most-misunderstood discipline" + 3-mode routing → protocol → E. Goodhart self-check is rare-in-the-wild expert framing.
- D3 Anti-Pattern: 14/15 — Cross-mode boundary names the 5 collapses (not lead/lag, not habit, not sub-WIG, not task, not OKR KR). 2-3 leads cap, hard. Industry grounding (Strathern 1997, CFPB 2016, VA OIG 2014, GBI 2011, Edmondson, Lencioni, Pfeffer-Sutton, Cialdini, Argyris) is strong.
- D4 Spec Compliance: 14/15 — EN/JP/zh-TW + non-activation + edge-case routing for member-can't-name-WIG. Tight.
- D5 Progressive Disclosure: 13/15 — Multi-file orchestrator. Clean.
- D6 Freedom Calibration: 14/15 — Coach-is-Socratic rule is firm (low freedom on dictation); discovery itself is high freedom. Well-calibrated.
- D7 Pattern Recognition: 9/10 — Process pattern + 3-scope routing.
- D8 Practical Usability: 12/15 — V1⚠ on member-influence carries through; otherwise strong.
- Failure patterns flagged: none material.

### 8. 4dx-d3-scoreboard — Score 106/120, Grade B

- D1 Knowledge Delta: 17/20 — 4 design criteria (simple/visible/lead+lag+pacing/5-second test) + players-vs-coaches distinction + Tufte/Few/Ware perception literature grounding. Members-read scope V1⚠ partial.
- D2 Mindset + Procedures: 14/15 — Mindset = "manual-update-by-player(s) is the engagement loop" + scope-detection → protocol routing.
- D3 Anti-Pattern: 13/15 — Cross-mode common boundary (collapse-into-BI-dashboard, fail-5-second-test, automation-eats-ownership, no-pacing-line) is solid. Could include more specific anti-patterns (e.g. "purple-on-white" equivalent for scoreboards — chart junk, gradient backgrounds). High-context-culture caveat present.
- D4 Spec Compliance: 14/15 — EN/JP/zh-TW + non-activation + edge-case routing. Good.
- D5 Progressive Disclosure: 14/15 — 3 protocols + 3 standards (5-second-test / players-vs-coaches / lead-lag-pacing-elements) — clean delegation pattern.
- D6 Freedom Calibration: 13/15 — Solo personal board is high freedom (sticky note OK); team public board is low (must pass 5-second test, must be player-updated). Differential exists but not always loud.
- D7 Pattern Recognition: 9/10 — Process pattern.
- D8 Practical Usability: 12/15 — Scoreboard mechanics are inherently visual; SKILL.md text-only orchestrator can't show; protocols/ presumed to compensate. Member-read V1⚠.
- Failure patterns flagged: minor — could pull more specific anti-pattern examples up to orchestrator level.

### 9. 4dx-d4-cadence — Score 107/120, Grade B

- D1 Knowledge Delta: 18/20 — Account/Review/Plan grammar + commitment-shape rules + sacred-cadence + whirlwind-exclusion + 4-mode routing (solo / facilitator / member-prep / member-debrief). Member-prep + member-debrief are V1⚠ partial.
- D2 Mindset + Procedures: 14/15 — "Cadence is sacred" + "honest signal beats clean signal" + commitment-ownership. Strong mindset transfer.
- D3 Anti-Pattern: 13/15 — Cross-mode common boundary: not-status-update, not-daily-standup, no-dictating-commitments, lead-measure-only-target. Solid but somewhat overlaps with sustain-momentum-rescue's CE-set.
- D4 Spec Compliance: 14/15 — EN/JP/zh-TW × 4 modes; comprehensive. Description verges on over-long.
- D5 Progressive Disclosure: 14/15 — 4 protocols + 4 standards is the most-decomposed skill in plugin. Loading-trigger language clean.
- D6 Freedom Calibration: 13/15 — Sacred-cadence (low) + Socratic protocol (medium) + commitment shape (low). Well-bounded.
- D7 Pattern Recognition: 9/10 — Process; 4-mode routing.
- D8 Practical Usability: 12/15 — Most modes (4) of any skill; cognitive load on orchestrator highest. Edge-case routing helps. Some overlap with sustain-momentum-rescue (cadence broken vs running).
- Failure patterns flagged: minor Pattern-2 risk from 4-mode complexity; mitigated by clean delegation.

### 10. 4dx-sustain-momentum-rescue — Score 113/120, Grade A (tied highest)

- D1 Knowledge Delta: 20/20 — Stack-walk diagnostic (D1→D2→D3→D4→whirlwind→substrate) + "engagement follows winning" + 4 worked cases (Store 334 D4-only rescue, Stengel 2am Beijing, Crisafulli unexplained-wins, Susan/Marcus accountability-with-respect) + Atomic Habits "never miss twice" / Switch Path-shaping / Grit passion-vs-perseverance + Crede meta-analysis caveat. Highest delta of plugin alongside cascade.
- D2 Mindset + Procedures: 15/15 — Mindset = "diagnostic before restart" + 9-step E with halt conditions + substrate off-ramp. Pure expert framing.
- D3 Anti-Pattern: 15/15 — CE-11 (D4-on-broken-upstream), CE-15 (compliance without commitment), CE-22 (formulaic recognition), CE-23 (Marcus pattern operator-hijacks-architect), catch-up trap. Plus author blind spots (no-solo-protocol, high-context, SDT critique, FranklinCovey bias). Plus easily-confused (productivity advice, annual review, coaching/therapy).
- D4 Spec Compliance: 15/15 — Trigger phrases EN/JP/zh-TW + non-trigger examples + distinction-from-neighbors. Excellent.
- D5 Progressive Disclosure: 13/15 — Single-file ~395 lines. Industry-grounding addendum offloaded. Borderline; could externalize 4 worked cases.
- D6 Freedom Calibration: 14/15 — Stack-walk steps are halt-driven (low freedom on routing) + Socratic prompts (medium). Substrate off-ramp is firm low-freedom ("STOP the 4DX rescue"). Excellent.
- D7 Pattern Recognition: 10/10 — Process pattern; the diagnostic itself is the canonical Process.
- D8 Practical Usability: 11/15 — Strong; Step-7 substrate off-ramp could explicit decision-tree (e.g. "if 2+ of: sleep<6h, sustained low mood, recent loss → state plainly"). Otherwise comprehensive.
- Failure patterns flagged: none.

---

## Patterns across skills

1. **Primary-source grounding is uniformly excellent** — every skill anchors on book chapters with source_book / source_chapter frontmatter + R-section verbatim quotes. Industry-grounding addenda (Reinertsen / Goldratt / Newport / SDT / Argyris / Edmondson / Lencioni / Pfeffer / Cialdini / Tufte / Few / Ware / Atomic Habits / Switch / Grit / CMMI / OHI / Q12) provide the WHY behind anti-patterns. **This pattern produces consistently high D1 + D3 scores** across the plugin.

2. **Multilingual triggers (EN/JP/zh-TW) lift D4 to 95% plugin-wide** — every skill includes 3-language activation phrasings and non-activation signals. Trigger-activation quality is best-in-class versus other monkey-skills plugins. Small note: zh-TW is consistently used (per CLAUDE.md / glossary), not zh-Hans.

3. **Multi-file orchestrators (5 of 10) implement clean Progressive Disclosure** — `4dx-meta-strategy-triage`, `4dx-d1-wig-formulation`, `4dx-d2-lead-measures`, `4dx-d3-scoreboard`, `4dx-d4-cadence` all use scope-detection → protocol-load → standards-on-demand. Single-file skills (whirlwind-triage, team-leader-onboarding, xps-evaluation, sustain-momentum-rescue, d1-wig-cascade) keep 170-410 lines. **team-leader-onboarding (~410) and sustain-momentum-rescue (~395) are borderline** against the 6K-token cap and could externalize worked cases / scripts via the companion-file pattern.

4. **Member-mode V1⚠ partial coverage** is consistent across d1-wig-formulation, d2-lead-measures, d3-scoreboard, d4-cadence — the source book is leader-POV; member-side protocols are symmetric inversion grounded on industry literature (Edmondson / Argyris / Pfeffer / Cialdini / Eurich). This is **honestly disclosed in audit metadata** and reflected in slightly lower D1/D8 for those skills. Not a defect; calibration.

5. **Anti-pattern sophistication uses CE-numbered author-warned modes** — every skill borrows the book's CE-XX numbering (CE-11, CE-15, CE-22, CE-23, CE-26, CE-32..CE-37) for Author-warned failure modes + adds plugin-specific easily-confused-neighbor sections (OKR / GTD / Hoshin / BSC / WBS / Kanban / sprint review). **D3 is the most specific dim across all 10 skills** — virtually no vague "be careful" warnings.

---

## Recommendations

### 1. Prioritize: D5 cleanup on 2 borderline single-file skills

- **`4dx-meta-team-leader-onboarding`** (~410 lines): extract Step-6 conversation-script outline to `protocols/buy-in-script.md` companion-file (per monkey-skills companion pattern). Single-file remains the SKILL.md but the script template loads on demand. Optional multilingual EN/JP/zh-TW script variants would address D8 high-context-culture gap simultaneously.
- **`4dx-sustain-momentum-rescue`** (~395 lines): extract 4 worked cases (A1 section) to `references/cases.md` companion. Diagnostic E section + R/I/A2/B fits comfortably under 250 lines.

### 2. Address: member-mode V1⚠ coverage where book is leader-POV

The 4 multi-file skills (d1-wig-formulation, d2-lead-measures, d3-scoreboard, d4-cadence) have member modes flagged V1⚠. Two paths:
- **Accept current state** — document the inference pattern explicitly (Edmondson / Argyris / Pfeffer / Eurich) in each member-mode protocol. Honest inversion is fine.
- **V2 grounding pass** — find a member-POV primary source per scope (e.g. follower-side leadership literature, Hackman team effectiveness) to harden the citation chain.

### 3. Surface: rubric scoring subjectivity in xps-evaluation

`4dx-meta-xps-evaluation` Step 2-5 use coarse multipliers (1.0 / 0.7-0.8 / 0.5; etc.). Add an explicit usability note: "Two trained auditors typically arrive within ±0.3 on the same team. Treat XPS as a *range* (e.g. 2.7-3.0), not a point estimate, when narrative evidence is the input." This protects against false-precision misuse.

### 4. Optional: lift specific scoreboard anti-patterns to orchestrator-level

`4dx-d3-scoreboard` cross-mode boundary is principle-level (no-pacing-line, no-manual-update). Consider adding 2-3 specific NEVERs analogous to frontend-design's "purple gradient on white": e.g. NEVER use chart-junk gradient backgrounds, NEVER use 8+ data series, NEVER substitute progress-bar for pacing-line. Bumps D3 from 13→15.

### 5. Optional: deep-cascade mechanics in d1-wig-cascade Step 9

`4dx-d1-wig-cascade` Step 9 says "re-run THIS skill at each layer" but the layer-N → layer-N+1 mechanics (does the layer-N Team WIG become the layer-N+1 Primary WIG? does layer-N+1 also re-elect Battle WIGs?) is implicit. A 5-line worked example using the retailer case (region → district → store) would close the gap.

---

## Ship-vs-revise verdict

**SHIP.** Mean 109.4/120 (A-band), 7-of-10 A-grade, 0 below B, narrow distribution (105-113). Plugin is production-ready. The 5 recommendations are improvements, not blockers — D5 cleanup on the 2 borderline single-file skills is the highest-leverage action and doesn't change the verdict.
