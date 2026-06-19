---
name: 4dx-audit
description: |
  Cross-layer 4DX aggregator — diagnoses status across WIG / Lead / Scoreboard / Cadence / Substrate. Use with artifacts spanning ≥2 layers, or when you can't name the broken layer: 'which layer is broken?'. Single-layer → that topic skill.
source_book: The 4 Disciplines of Execution (2nd ed., 2021) — McChesney/Covey/Huling/Thele/Walker
source_chapter: "Cross-cutting (Foreword + Ch 1 framing + Ch 6 selection + Ch 10 sustaining)"
source_language: en
tags: [audit, consultant, artifact-synthesis, multi-layer, 4dx, entry-point, cross-discipline, diagnosis]
related_skills:
  - using-four-dx-coach
  - 4dx-meta-strategy-triage
  - 4dx-meta-whirlwind-triage
  - 4dx-meta-team-leader-onboarding
  - 4dx-meta-xps-evaluation
  - 4dx-d1-wig-formulation
  - 4dx-d1-wig-cascade
  - 4dx-d2-lead-measures
  - 4dx-d3-scoreboard
  - 4dx-d4-cadence
  - 4dx-sustain-momentum-rescue
---

# 4dx-audit — Cross-layer 4DX aggregator (multi-artifact synthesis)

## Mission

This skill is the **cross-layer aggregator** for the four-dx-coach plugin. v0.8.0 introduced dual-mode topic skills — every topic skill (D1 / D2 / D3 / D4 / cascade / strategy-triage / whirlwind-triage / leader-onboarding) now ships with its own `audit-mode.md` for **single-layer** synthesis from one artifact at that layer. This skill is reserved for cases the topic skills cannot own:

- **Artifacts spanning ≥2 D-layers** — e.g. user pastes strategy doc (L1 candidates) + OKR sheet (L1 + L2 mixed) + 12-metric dashboard (L3) + 4 weeks of meeting notes (L4 + L5). No single topic skill owns this scope; cross-layer synthesis is required to identify which layer is the bottleneck and what sequence to repair in.
- **Layer-unknown failure** — user knows 4DX is broken but cannot name which discipline collapsed. The audit's job is to map artifacts onto all 5 layers, then point at the broken layer (which then routes to that topic skill's audit-mode or coach-mode).
- **Cross-layer sequencing gaps** — even when layers are individually well-formed, cross-layer dependencies can be wrong (e.g. leads picked before WIG was well-formed; scoreboard built without cadence to populate it).

For **single-layer audits**, do NOT activate; route to the topic skill's audit-mode instead. The topic-skill audit-mode owns its layer's standards verbatim and is more depth-appropriate than this aggregator.

## R — Reading

> Strategy execution is a function of what people do, not what they know or believe. Most strategies fail in execution, not in design.
>
> — McChesney et al., *The 4 Disciplines of Execution* (2nd ed., 2021), Foreword

## I — Interpretation

The user has invested in some attempt at strategy / goals / metrics / cadence — but it's messy, mixed in with non-4DX vocabulary (OKRs, KPIs, sprint goals), or stalled. The job is **not to start over but to map their existing artifacts to the 4DX 5-layer framework** and surface where each layer is strong, missing, or wrong-shaped.

### The 4DX 5-layer framework (audit lens)

| Layer | What it should be | Audit signals |
|---|---|---|
| **L1 WIG** (Discipline 1) | One Wildly Important Goal in *From X to Y by When* form; ONE per individual; selected via Battles 2×2 at team level | Present? Well-formed (X / Y / When all explicit)? Within ONE per individual? Aligned to mission? |
| **L2 Lead measures** (Discipline 2) | 2-3 measures that are BOTH predictive AND influenceable; daily-actionable | Present? Pass two-axis test? ≤3? Goodhart-resistant? Distinct from KPIs / lag / OKR-KRs? |
| **L3 Lag + Scoreboard** (Discipline 3) | Compelling players' scoreboard with ≤4 elements (lead + lag + pacing + delta); passes 5-second test; team builds + maintains | Present? Glance-readable? Players' or coaches' shape? Updated by team? Public/multi-stakeholder legible? |
| **L4 Cadence** (Discipline 4) | Weekly WIG Session, 20-30 min, Account → Review → Plan grammar; commitments-not-assignments; whirlwind-excluded | Running consistently? Last 4-week cadence pattern? Commitment quality (specific / lead-moving / own-control)? Members own commitments? |
| **L5 Substrate** | Capacity (whirlwind ≤80% / WIG slot ~20%); commitment-not-compliance from leaders/members; engagement (members care) | Time sovereignty real? Buy-in genuine vs theatrical? Engagement signals present? |

### Audit posture (consultant-mode)

- **Read everything provided** — strategy doc / OKRs / KPI list / scoreboard images or descriptions / meeting notes / chat history
- **Map content to layers** — extract WIG candidates, identify what's framed as "lead measure" but is actually lag, etc.
- **Diagnose status per layer** — `well-formed` / `malformed` / `absent` / `wrong-shape`
- **Identify gaps + risks** — what's missing for full 4DX implementation; what's currently doing harm (e.g. Goodhart-vulnerable lead, scoreboard nobody looks at)
- **Prescribe concrete next steps** — usually 3-5 actions in priority order, each routing to a specific coach skill for deep work
- **Route to deep-dive skills** — this skill is the entry; the 11 coach skills are deep-dives. End the audit by saying "next, run [skill X] to fix [layer Y]"

### What this skill does NOT do

- Run Socratic step-by-step coaching (that's the 11 coach skills)
- Replace the deep-dive skills — it's an **entry point + roadmap**, not a substitute
- Audit non-4DX frameworks (OKR audit, agile retro, balanced scorecard) — its lens is specifically 4DX

## A1 — Past Application

Two worked composite cases illustrating cross-layer audit pattern (mid-size company OKRs+12-metric+collapsed cadence; strategy-doc kickoff with 9 priorities). Load `references/audit-cases.md` for full case writeups when the user's situation resembles either pattern OR when constructing per-layer recommendation rationale.

## A2 — Future Trigger ★

### When the user needs this skill (cross-layer signals only)

1. **Multi-artifact spanning ≥2 D-layers**. User pastes / attaches / describes artifacts that map to multiple 4DX layers simultaneously:
   - EN: "Here's our strategy doc + OKR + dashboard + meeting notes — audit 4DX across the board", "We have WIG + leads + scoreboard but cadence broken — diagnose across layers", "Our quarterly plan covers goal + metrics + weekly review — translate to 4DX", "What's missing in our 4DX setup across all 5 layers?"
   - JP:「策略 doc + OKR + dashboard + meeting notes をまとめて 4DX 視点で診断」「複数文書から 4DX 現状整理」「四半期 plan を全層 4DX に展開」
   - zh-TW:「資料跨好幾層（WIG + leads + scoreboard + cadence）都有，幫我整理現況 + 建議下一步」「我們 4DX 整套都有但卡住，跨層診斷」

2. **Layer-unknown failure**. User cannot name which discipline collapsed:
   - EN: "I don't know which layer is broken — look at the whole picture", "Something's wrong with our 4DX but I can't tell what"
   - JP:「どの layer が壊れてるか分からない、全体を見て」
   - zh-TW:「我們導入 4DX 但卡住，不知道哪一層斷掉」

3. **Cross-layer sequencing diagnostic**. User suspects layers are individually OK but the sequence is wrong (e.g. leads chosen before WIG locked).

### Non-activation signals (do NOT trigger when…)

- **Single-layer audit** — user provides artifacts at exactly ONE layer → route to that topic skill's audit-mode (see redirect table below in Boundary). E.g. only a WIG to diagnose → `4dx-d1-wig-formulation` audit-mode; only a lead-measure list → `4dx-d2-lead-measures` audit-mode; only a scoreboard → `4dx-d3-scoreboard` audit-mode; only a cadence log → `4dx-d4-cadence` audit-mode.
- **Cold-start with no artifacts** — user just says "I want to use 4DX" with no context → `using-four-dx-coach`.
- **Single-discipline question + Socratic preference** — "help me write a WIG, here's my situation" → `4dx-d1-wig-formulation` coach-mode directly.
- **Non-4DX framework audit** — OKR audit, agile retro, BSC scorecard — out of scope.
- **Mid-flow inside an active deep-dive coach skill** — don't interrupt with audit reframing.
- **Pure venting / emotional support** — "我們團隊一團糟" without artifacts → router or external support.

### Distinction from neighbors

- vs. `using-four-dx-coach` (router): router triages cold-start scope; this skill audits provided context. Router activates on vague queries; audit activates on artifact-rich queries.
- vs. `4dx-meta-strategy-triage`: that's a 6-verdict gate ("should X use 4DX?"); audit assumes 4DX is already chosen and audits the implementation.
- vs. `4dx-meta-xps-evaluation`: XPS is a 0-4 score on 4 components for an established team running 4DX; audit is broader (across all 5 layers, including whether artifacts even map to 4DX correctly).
- vs. `4dx-sustain-momentum-rescue`: rescue assumes one specific failure (cadence collapse, scoreboard ignored); audit is the diagnostic when the user can't yet name what's broken.

## E — Execution

When this skill activates:

### Step 1 — Inventory all provided context

- Read every artifact / paste / attachment / chat history segment the user has provided.
- List what artifacts are present (e.g. "1 strategy doc, 1 OKR sheet, 12-metric dashboard description, 4 weeks of meeting notes").
- If the user mentions context but hasn't actually provided it, ask ONCE for the missing pieces; do not invent content.

### Step 2 — Map content to the 5 layers

For each layer, extract relevant content from the artifacts:

| Layer | Look for in artifacts |
|---|---|
| L1 WIG | Goal statements, mission/vision, "objectives", "targets", "north star metric", existing WIG declarations |
| L2 Lead | "Daily actions", "leading indicators", "input metrics", OKR Key Results that are activity-shaped (not outcome-shaped) |
| L3 Lag + Scoreboard | "Outcome metrics", KPI dashboards, retention curves, charts, scoreboards, weekly/monthly result reports |
| L4 Cadence | Meeting notes, "weekly review", "WIG Session", "1-on-1 / standup" descriptions, chat about cadence rhythm |
| L5 Substrate | Capacity language ("we're swamped"), buy-in / commitment language ("leaders bought in" / "team complies but doesn't believe"), engagement signals |

Don't force every layer to have content — note which layers are unrepresented in the artifacts.

### Step 3 — Diagnose per-layer status

For each layer, label:

- `well-formed` — present + matches 4DX standards
- `malformed` — present but doesn't match (e.g. WIG has no When, lead measures are actually lag, scoreboard has 12 elements)
- `absent` — not in artifacts (genuinely missing or just not provided)
- `wrong-shape` — looks 4DX but is actually a different framework (e.g. OKR objective masquerading as WIG; OKR-KR masquerading as lead)

For each `malformed` / `wrong-shape`, cite the specific 4DX standard violated **using exact 4DX terminology** (not paraphrases). Findings should echo the canonical phrasing — "fails the 5-second test", "violates Ch 7 Rule 1", "Goodhart-vulnerable", etc. — so users can search the book / standards for follow-up:

- **WIG**: *From-X-to-Y-by-When* grammar (Ch 2); **Ch 7 Rule 1: no team focuses on more than 2 WIGs at the same time** (cite this rule explicitly when 3+ "WIGs" are declared in artifacts, e.g. "ship 3 features" framed as 3 separate WIGs violates Rule 1's team-level focus cap; an individual-level corollary is "no person is the lead on more than 1-2 WIGs simultaneously"); Ch 7 Rule 2: Battles-must-win-the-war; Ch 7 Rule 3: leaders veto-not-dictate; Ch 7 Rule 4: WIG must have *From X to Y by When* finish line
- **Lead measures**: predictive AND influenceable **two-axis test** (Ch 3); 2-3 cap; daily-actionable; if a candidate fails one axis, name which axis (predictive-fail vs influenceable-fail)
- **Scoreboard**: **5-second test** (Ch 4) — say "fails the 5-second test" verbatim, not paraphrases; ≤4 elements rule; **players' not coaches' shape** (use this exact distinction)
- **Cadence**: weekly; **Account → Review → Plan** grammar (verbatim); commitments-not-assignments; whirlwind-excluded; sacred cadence (no skipping)
- **Substrate**: ~20% protected WIG slot; **commitment vs compliance** distinction (Ch 8); engagement vs theater

### Step 3.5 — Cross-validate against Cindrich's 5 named failure modes (load `references/cross-validation-checks.md`)

After per-layer rule checks, run the artifact stack through 5 practitioner-named cross-layer failure modes. Load `references/cross-validation-checks.md` §Cindrich-5 for the full mode list + verbatim signal matching.

### Step 3.6 — Cross-validate against OKR-drift patterns (load `references/cross-validation-checks.md`)

After Step 3.5, run the artifact stack through OKR-drift signals across D1/D2/D3/D4/Substrate. Load `references/cross-validation-checks.md` §OKR-drift for the full per-layer signal list. Key framing rule: most "drift to OKR" is actually drift toward bad OKR shape that Wodtke would also reject — discipline-drift, not framework-drift.

### Step 4 — Identify gaps and risks

Cross-layer synthesis:

- **Sequencing gaps** — what depends on what? (e.g. can't pick leads if WIG isn't well-formed)
- **Goodhart risks** — are any "lead measures" likely to be gamed? (cite Wells Fargo / VA / APS pattern if applicable)
- **Cindrich diagnostic equation** — Goal Clarity + Commitment + Cadence = Results. If audit reveals one or two of the three are missing, name explicitly which factor and why
- **Engagement collapse signals** — scoreboard ignored, meetings skipped, "compliance theater" language
- **Capacity collapse signals** — firefighting language, multi-week missed commitments, "no time for the WIG"
- **Mis-framing risks** — OKR / KPI / sprint vocabulary smuggled in unchanged

### Step 5 — Prescribe concrete next steps with skill routes

Output 3-5 prioritized actions, each:
- Names the gap (cite which layer + which standard)
- Recommends a specific action (concrete, not "improve communication")
- Routes to the deep-dive coach skill that will help
- **Specifies sequencing** — every recommendation must say one of: `[FIRST]` (do before all others; usually a foundational fix that unblocks downstream work), `[NEXT]` (sequential after [FIRST] — do these in listed order), `[PARALLEL]` (can run alongside [FIRST] without dependency), or `[LATER]` (deferred until earlier items land)

Sequencing rules:
- **Exactly one [FIRST]** — the single most-blocking gap; everything else waits or runs alongside
- **[PARALLEL] only when truly independent** — capacity audit can run alongside WIG reformulation because they don't share a dependency; lead-measure work cannot run alongside WIG reformulation because leads depend on a well-formed WIG
- **[NEXT] order matters** — list [NEXT] items in the actual execution sequence (not topic order)
- **No more than 1 [LATER]** — if you want to defer 3+ items, the audit is over-prescribing; trim

Format example:
1. **[FIRST] Reformulate the WIG** — current "improve retention" lacks From-X-to-Y-by-When form (Ch 2 grammar violation). Specific recommendation: choose baseline + target + deadline. **→ Run `4dx-d1-wig-formulation` (team-select mode if leader, personal-define if solo).** Until this lands, downstream layers cannot be diagnosed cleanly.
2. **[PARALLEL] Capacity audit** — firefighting language indicates ~80%+ whirlwind without a protected WIG slot (substrate gap, L5). Independent of WIG reformulation; can run in parallel. **→ Run `4dx-meta-whirlwind-triage`.**
3. **[NEXT] Diagnose cadence collapse** — 4 weeks skipped indicates rescue territory (not normal D4); requires the WIG to exist first to diagnose what was supposed to be running. **→ Run `4dx-sustain-momentum-rescue`** after step 1.
4. **[NEXT] Cull lead-measure list from 12 → 2-3** — current dashboard violates ≤4 rule (Ch 4) + most "leads" are lag-shape (Ch 3 two-axis test fail). **→ Run `4dx-d2-lead-measures`** after WIG is well-formed.

End the audit with: "These are diagnostic findings + sequenced recommendations. Start with [FIRST], run [PARALLEL] alongside if capacity allows, then move through [NEXT] in order."

### Output format (audit report)

```markdown
# 4DX Audit — [user-provided context label / date]

## Inventory
- [list artifacts read]

## Layer status

| Layer | Status | Finding |
|---|---|---|
| L1 WIG | malformed | [one-line reason + standard cite] |
| L2 Lead | absent | [...] |
| L3 Scoreboard | wrong-shape | [...] |
| L4 Cadence | broken (4 wk) | [...] |
| L5 Substrate | weak | [...] |

## Gaps + risks
- [bullet list of cross-layer issues]

## Recommendations (sequenced)
1. **[FIRST] [Action name]** — [reason citing exact 4DX standard, e.g. "fails the 5-second test", "violates Ch 7 Rule 1"] → run `[skill-slug]`
2. **[PARALLEL] [Action name]** — [why it can run alongside [FIRST]] → run `[skill-slug]`
3. **[NEXT] [Action name]** — [why it depends on [FIRST] completing] → run `[skill-slug]`
4. ...

## Suggested next move
[1-2 sentences: start with [FIRST], run [PARALLEL] alongside if capacity allows, then [NEXT] in order]
```

## B — Boundary ★

### Single-layer audit redirect table

If the user's artifacts cover ONE layer only, this skill is the wrong tool — the corresponding topic skill's `audit-mode.md` owns that layer's standards verbatim and is depth-appropriate. Hand off via:

| If user provides artifacts at this layer only | Route to topic skill's audit-mode |
|---|---|
| WIG statement / goal candidates only | `4dx-d1-wig-formulation` audit-mode (`protocols/audit-mode.md`) |
| Lead-measure list / candidate metrics only | `4dx-d2-lead-measures` audit-mode |
| Scoreboard / KPI dashboard only | `4dx-d3-scoreboard` audit-mode |
| WIG-Session / cadence log only | `4dx-d4-cadence` audit-mode |
| Multi-team cascade tree only | `4dx-d1-wig-cascade` audit-mode |
| Strategy-fit gate / "should we use 4DX" memo only | `4dx-meta-strategy-triage` audit-mode |
| 7-day time log / capacity audit only | `4dx-meta-whirlwind-triage` audit-mode |
| Direct-report leader-onboarding artifacts only | `4dx-meta-team-leader-onboarding` audit-mode |

Only fire `4dx-audit` itself when the user crosses ≥2 of these rows OR cannot yet name the broken layer.

### Do NOT use this skill in:

- **Single-layer scope** — see redirect table above; route to that topic skill's audit-mode.
- **Cold-start with no artifacts** — user has nothing to audit yet → `using-four-dx-coach` for scope triage.
- **Socratic preference** — user wants step-by-step coaching → topic-skill coach-mode.
- **Non-4DX audits** — OKR audit, agile retro, BSC review — wrong framework lens.
- **Pure dialogue / venting** — without 4DX-framing intent → router.

### Author-warned failure modes (consultant-mode specific)

- **Audit-as-replacement-for-coaching** — once audit done, user might want full hand-holding through every recommendation; don't let audit substitute for the deep-dive skills. End the audit, route, exit.
- **Forced-fit mapping** — not every artifact maps cleanly to 4DX layers. If something doesn't fit (e.g. BSC strategy map, OKR alignment matrix), say so explicitly: "This doesn't map to 4DX; it's a [other-framework] artifact. We can leave it aside or translate it explicitly — your call."
- **Recommendation-overload** — listing 12 gaps overwhelms; prioritize 3-5 with explicit "do this first" sequencing.
- **Ignoring substrate** — easy to focus on D1-D4 visible artifacts and miss capacity / engagement / commitment substrate. Always check L5.
- **Goodhart-blindness** — easy to validate existing "leads" without applying two-axis test; cite Wells Fargo / VA / APS pattern when leads look gameable.
- **Single-snapshot bias** — audit reads what's provided; if user provides only success-framed artifacts, audit will overstate health. Note explicitly when audit is data-limited.

### Author's blind spots / period limitations

- **Book is dialogue-coaching POV** — the audit consultant role is derived from book content, not directly written. Audit standards drawn from book chapter rules; audit *posture* (synthesizer-from-artifacts) is consultant-craft, not 4DX-craft. Use `references/industry-grounding.md` for consultant-craft sources (Block / Schein).
- **MVP scope** — this is a single-protocol audit covering all artifact types and stages. v1+ might add per-artifact-type sub-protocols (strategy-doc-specific / OKR-specific / scoreboard-specific) if usage shows the generic protocol misses depth.

### Easily-confused neighboring methodologies

- **OKR audit** — different framework lens; OKR audits look at alignment / measurability of KRs, not predictive AND influenceable; don't conflate.
- **BSC (Balanced Scorecard) review** — Kaplan-Norton has its own 4-perspective framework; not 4DX.
- **Agile retro** — sprint review / process retro; different cadence + scope.
- **Stoic review / personal retrospective** — reflective practice, not 4DX-framed audit.

## Related skills

- `using-four-dx-coach` — composes-with — router complements this for cold-start; this skill takes over when artifacts are provided
- `4dx-meta-strategy-triage` — depends-on — strategy-triage gates whether 4DX even applies; audit assumes 4DX has been chosen
- `4dx-meta-xps-evaluation` — contrasts-with — XPS is narrower (0-4 score on 4 components for established team); audit is broader (5-layer status across solo / leader / member contexts)
- `4dx-d1-wig-formulation` / `4dx-d2-lead-measures` / `4dx-d3-scoreboard` / `4dx-d4-cadence` — composes-with — audit routes to these for deep-dive after diagnosis
- `4dx-sustain-momentum-rescue` — composes-with — audit may identify rescue territory and route there
- `4dx-meta-whirlwind-triage` — composes-with — substrate-layer capacity gap routes here

## Audit metadata

- **Skill type**: cross-layer aggregator (single-file; distinct from topic-skill audit-mode protocols)
- **Verification status**: V1 ⚠️ partial — book is leader-dialogue POV; consultant-from-artifacts posture is derived
- **Test pass rate**: see `test-prompts.json`
- **Created**: 2026-04-30 (v0.7.0 MVP — universal 5-layer synthesis)
- **Repositioned**: 2026-04-30 (v0.8.0 — narrowed to cross-layer / multi-artifact only; per-layer audit moved into topic-skill `audit-mode.md` protocols)
- **Output language**: body — English; description + trigger phrasings — multilingual EN/JP/zh-TW
- **Future**: if MVP proves valuable, consider expanding to multi-file with per-artifact-type sub-protocols (strategy-doc-specific / OKR-specific / scoreboard-specific / cadence-specific / full-stack)
