# spec-expansion v0.2 design — three transition layers (cross-object combinations + journey navigation)

> **Type**: design note (discussion-grounded; NOT yet a brief, NOT built)
> **Date**: 2026-06-11
> **Status**: design captured for a future brainstorm → plan → SDD. Two new layers proposed (L2, L3); both gated behind A/B validation vs the current critic.
> **Context**: refines the SHIPPED `spec-toolkit:spec-expansion` (PR #387, merged `e38aa3a1`/`ffd82717`). Sibling: the Tier-1 greenfield nudge in `code-toolkit:brainstorming` (PR #388, merged). See memory `project_spec_toolkit_mvp`, `feedback_spec_coverage_value_greenfield_regime`.

## 0. Scope boundary (LOCKED — kouko's emphasis)

**This framework handles ONLY: user-flow (journey) + object states + their combinations + the reaction each situation requires.** It *relates to* UI states (a screen's state = a reflection of its backing objects' states), but **the detailed visual presentation — layout, animation, pixel-feel, "does it look like the reference screenshot" — is NOT in scope.** That half is unspecifiable and belongs to a runtime observe-and-fix loop (`agent-device`), not to GENERATE.

Output = the **structural** spec ("what situations exist + what reaction each requires"), never "what it looks like."

## 1. The completeness model — three transition layers

"Cover all non-happy-path situations" decomposes into three orthogonal transition layers. The shipped engine systematizes only L1; L2 and L3 are the gaps.

| Layer | What transitions | Non-happy-paths it covers | Shipped? |
|---|---|---|---|
| **L1 — object state machine** | one object's states | illegal object transitions (refund→ship), retry loops, extreme states | ✅ shipped (Phase ② + state-transition lens) |
| **L2 — per-stage cross-object combination** | the simultaneous state *combination* of the objects co-active at one flow-stage / screen | "this screen with A=failed AND B=expired AND C=empty" → the reaction that combination requires | 🆕 **gap 1** — ✅ A/B-validated as a **gated additive** layer (§5) |
| **L3 — journey navigation graph** | the user moving *between* flow-stages / screens | back-and-forth, go-back-and-edit, skip, mid-flow abandon, leave-and-resume / re-enter, error-escape | 🆕 **gap 2** |

Together: object extremes (L1) + screen-state combinations (L2) + journey back-and-forth (L3) = systematic non-happy-path coverage, all at the flow/object-state level, none of it visual.

### Why L2 is tractable (kouko's correction — earlier "combinatorial explosion" was over-stated)
The explosion `S^N` is over ALL objects globally. But L2 is scoped **per flow-stage to only that screen's backing objects** — typically 2–5 objects × 3–6 states ≈ a few dozen combinations, **fully enumerable**. Cross-stage is **additive, not multiplicative**. **The USM backbone is the natural partitioner** that keeps each stage's combination set small. → full enumeration is the default; **pairwise / n-wise combinatorial coverage is only a fallback** for the rare wide stage (6+ backing objects). (Sister technique to the Chow n-switch the engine already uses; grounded in NIST/Kuhn combinatorial-testing "interaction rule" — verify exact fault-distribution figures if/when building.)

### Why L3 is a real gap (grounded in the vault)
Two distinct transition graphs exist; the engine systematized only the object one:
- **Object state machine** (L1) — ✅ done.
- **Journey navigation graph** (L3) — ⚠️ NOT done. The backbone is currently a **linear happy-path spine**; it has a *place* for alternative flows (USM "body") but **no systematic completeness method** — exactly what `2026-06-10 從 Happy Path 到完整路徑` flagged. L2 (within-stage) does not fix this (L3 is between-stage).
- **Fix**: model the backbone *also* as a navigation graph (nodes = stages, edges = forward / back / skip / abandon / resume / error-escape) and apply ISTQB state-transition coverage to **that** graph — symmetric to what Phase ② does for objects.

## 2. Refined pipeline (stage by stage; shipped vs new)

| Stage | What it does | Layer | Shipped? |
|---|---|---|---|
| **① USM backbone** | lay the journey spine **AND build it as a navigation graph** (nodes=stages; edges=forward/back/skip/abandon/resume/error-escape) | L3 source | ✅ spine shipped / 🆕 nav-graph |
| **② OOUX object model** | per object: ORCA + state machine | L1 | ✅ shipped |
| **③a per-object grid** | `backbone × object × CTA × state` cells | — | ✅ shipped |
| **③b per-stage cross-object combination** | for each stage → identify that screen's backing objects → enumerate their legal state combinations → the reaction each requires | **L2** | 🆕 |
| **③c journey-transition coverage** | apply state-transition coverage to the nav graph (every legal nav edge walked; invalid nav flagged; back/abandon/resume/re-enter enumerated) → reaction each requires | **L3** | 🆕 |
| **③d lens prune** | state-transition / BVA / CRUD / permissions / empty-error-loading / NFR + legality + USM priority | — | ✅ shipped |
| **④ completeness-critic** | loop-until-dry; with L2/L3 systematized the critic shifts from *carrying* cross-object/journey coverage to *verifying + filling gaps + emitting blind spots* — **but A/B showed it is NOT merely "lighter": it remains the recall source for single-object-failure stages (where it out-recalls L2) and the precision-pruner of L2's enumeration junk** (see §5 / validation report) | — | ✅ shipped (retained, dual role) |
| **⑤ emit** | combination→reaction and nav-transition→reaction become `#### Scenario:` entries in the hybrid output | — | ✅ shipped |

## 3. Worked example — checkout flow (Cart → Payment → Confirm)

- **L3 journey nav graph**: `Payment ──back→ Cart` (edit qty, return), `Payment ──abandon→ leave`, `Payment ──error-escape→ ?`, `leave-and-re-enter → which stage do they land on?` — each edge → a reaction to define.
- **L2 Payment-stage combination**: `Cart=full × Payment=failed × Coupon=expired` → show retry + expired-coupon banner, keep cart contents.
- **L1 Payment object**: `idle → processing → failed → retry → processing` (cycle).

→ each layer enumerated systematically; together = all the back-and-forth + error + combination reactions to spec — **none of it visual**.

## 4. Honesty rails (unchanged)
- High recall **relative to the seed**, NOT global completeness (may miss a backing object or a cross-flow interaction → critic + blind-spots cover that residue). Keep the ban on the word "complete".
- **Visual presentation is permanently out of scope** (kouko's lock) → `agent-device` runtime loop.

## 5. Validation gates (BEFORE building — one per new layer)
1. **A/B marginal value (per layer, separately).** The critic already catches *some* cross-object (L2) and journey (L3) cases by judgment. So A/B each layer: does systematic L2 / L3 enumeration actually out-recall the current critic-judgment baseline, on the same seeds? Per `feedback_ab_baseline_reveals_marginal_behavioral_delta` — don't assume; measure. If a layer doesn't lift, don't build it.
   - **L2 — ✅ VALIDATED (2026-06-11), build-ready as a GATED ADDITIVE layer.** Blind A/B, 6 seed-runs → full results in `2026-06-11-L2-ab-validation-results.md`. L2 out-recalls the critic in **interaction-dense flows** (booking/archive: 5/5 runs Δfull +0.17…+0.37, Δedge +0.16…+0.22) but the **critic wins single-object-failure flows** (camera: Δedge −0.23). So: **gate L2 on interaction-density** (enumerate a stage only if an object-pair has a joint reaction ≠ union of individual reactions), keep it **additive over the critic** (critic = recall source in the single-object regime + precision-pruner of L2 junk; critic precision was 1.0 every run, L2 0.86–1.0), and use a **script generator for wide stages (≥4 objects)** (they leak even under in-prompt enumeration). See `feedback_l2_cross_object_enumeration_regime_gated`.
   - **L3 — ✅ VALIDATED (2026-06-12), build-ready as a BROADLY-APPLIED additive layer.** Blind A/B, 6 seed-runs (2 runs × 3 seeds), results in §7–§8 of `2026-06-11-L2-ab-validation-results.md`. L3 out-recalls the critic on **every** flow tested (full 6/6 +0.20…+0.34, edge 6/6 +0.05…+0.29) — including the linear archive and single-object camera, so **NOT regime-gated** (unlike L2). **No precision tradeoff** (B ≈ A) and **no script generator needed** (`missed_by_both` = 0 all 6 runs; nav space bounded by stage count). Apply broadly to any ≥2-stage flow; keep the critic as the deep complement for nuanced resume/re-entry landing-point decisions. See `feedback_l3_journey_nav_coverage_not_regime_gated`.
2. **Implementation reliability.** Can an LLM reliably enumerate per-stage combinations (L2) + nav-graph transition coverage (L3) in-prompt, or does it need a small `scripts/` generator (like `validate_spec_output.py`)? Pairwise generation especially (IPOG-style) may want a script.

## 6. Open questions for the next session
- Build order: L2 first or L3 first? (L2 is more bounded; L3 has the richer vault grounding.) Or A/B both before committing to either.
- Does L3's nav-graph live in Phase ① (backbone becomes a graph) or as a new ③c step? (Design note leans: build the graph in ①, cover it in ③c.)
- How do L2 and L3 compose at emit — one merged scenario set, or two labeled groups?
- Relationship to Tier-2 (brainstorming→spec-toolkit delegation, deferred on OpenSpec DECLARE wiring): these layers make spec-expansion heavier/better, which *raises* Tier-2's value — re-weigh once L2/L3 land.
- Reconfirm: spec-toolkit's defensible home is still greenfield/early/high-risk UI/flow design (per the regime finding); these layers deepen that, they don't change the regime gate.
