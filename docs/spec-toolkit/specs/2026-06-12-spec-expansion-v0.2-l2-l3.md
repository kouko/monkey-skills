# Brief — spec-expansion v0.2: L2 cross-object combination + L3 journey navigation

> **Stage**: brainstorming output (consumed by `code-toolkit:writing-plans`)
> **Date**: 2026-06-12
> **Base**: branch off `origin/main` (`e38aa3a1`) — local main is stale. Modifies the SHIPPED `spec-toolkit:spec-expansion` (PR #387).
> **Validation**: both layers A/B-validated before this brief — `docs/spec-toolkit/design/2026-06-11-L2-ab-validation-results.md` (§7–§8). Design model: `…/design/2026-06-11-spec-expansion-v0.2-three-transition-layers.md`.

## Problem

(Axis 1 — committed JTBD read, established across this whole session; not re-asking)

When kouko starts a greenfield app from a sparse intent, the agent can't auto-plan **all** the UI operation flows + the reaction each situation needs — he ends up building it, then hand-inspecting the real UI and fixing reactions one by one. spec-expansion v0.1 systematizes only **L1** (one object's state machine). The two non-happy-path layers — **L2** (a screen's co-active objects in a simultaneous state *combination*) and **L3** (the user moving *between* stages: back / abandon / resume / error-escape) — are left to the completeness-critic's *judgment*. The A/B showed judgment **systematically misses** real cases there (session-expires-mid-payment, deposit-captured-while-reservation-pending, leave-and-resume landing points, pick-time corrupt/empty archive). Job: **systematically enumerate L2 + L3 so the spec names those situations + reactions BEFORE building**, not after.

## Users

(Axis 2) kouko, solo-building greenfield macOS/iOS apps (komado-Refs / -Viewfinder archetypes) where **no implemented UI exists to recon** — the spec must enumerate situations up front. Regime: greenfield / early / high-risk UI-flow design (per `feedback_spec_coverage_value_greenfield_regime`). Secondary consumer: any agent running spec-expansion on a multi-object / multi-stage flow.

## Smallest End State

(Axis 3) Add two additive sub-steps to the existing 3-phase engine — **no rewrite**:

- **L3 (the cheap half — do this even if L2 slips):** in Phase ① also build the backbone as a **navigation graph** (nodes=stages; edges=forward/back/skip/abandon/resume_reenter/error_escape/retry_self); add Phase **③c** = apply **0-switch state-transition coverage** to it (every nav edge once → reaction each requires). **Prompt-only, no script.** Apply to **any ≥2-stage flow** (not gated).
- **L2 (the heavier half):** add Phase **③b** = per stage, identify co-active objects → enumerate their joint state combinations → reaction each requires. **Gated on interaction-density** (run only where a stage's reaction depends on a joint ≥2-object state). Full in-prompt enumeration for narrow stages (≤3 objects); a **small pairwise generator** for wide stages (≥4 objects, which the A/B showed leak under pure in-prompt).
- **Both additive over the critic** — the critic stays (L2 single-object-regime recall + pruner; L3 nuanced resume-landing complement). Reframe the critic's role text accordingly (it is NOT merely "lighter").
- **Plumbing:** new `## ` proposal.md artifacts for L2 + L3 → matching `_SEC_*` checks in `validate_spec_output.py` + tests; emitted as more `#### Scenario:` entries (no consumer contract change).

The one genuinely-new **code** artifact = the pairwise generator script (everything else is SKILL.md prose + validator section-checks + tests). It is the natural descope lever (see Open Questions).

## Current State Evidence

- **Forward (control flow):** `spec-toolkit/skills/spec-expansion/SKILL.md` runs Phase ① USM backbone → ② OOUX object model → ③ matrix (build cartesian grid → prune via 6 lenses → emit). L2 inserts as **③b** (after the per-object grid), L3 as **③c**; L3's nav-graph is *built* in Phase ① alongside the spine. Each phase "announces itself" + emits a visible `##` artifact — L2/L3 must follow that same visibility contract.
- **Reverse (SSOT ownership):** `spec-toolkit/scripts/validate_spec_output.py` is the **section-contract SSOT** — `_SEC_USM_BACKBONE` / `_SEC_OOUX_OBJECT_MODEL` / `_SEC_PROVENANCE` / `_SEC_BLIND_SPOTS` / `_SEC_PATH_EDGE_MATRIX` (lines 124–128) are the enforced section names; SKILL.md prose must emit **exactly** these strings. New L2/L3 artifacts → add `_SEC_*` constants + checks here, and the SKILL.md section headers must byte-match.
- **Error (failure modes / guardrails at touch points):** Phase ① **seed-adequacy pre-flight gate** (don't fan out a too-sparse seed = manufacture fiction); Phase ③ **sparse-output fallback** (don't pad); **"ban the word complete"** honesty rail. L2/L3 must obey all three — esp. L2's wide-stage leak must be honestly blind-spotted if the pairwise script is descoped, never silently padded.
- **Data (shapes):** v1 grid cell = `backbone × object × CTA × state`. L2 cell = per-stage `{object=state, …}` joint assignment + required reaction. L3 = nav transition `from_stage → to_stage | transition_type` + required reaction. Both emit as `#### Scenario:` (GIVEN/WHEN/THEN) in `specs/<cap>/spec.md` + a proposal.md artifact section. Provenance tag (`seeded`/`inferred`/`critic-found`) on every emitted item.
- **Boundary (external interface):** output = OpenSpec change-folder (`proposal.md` + `specs/<cap>/spec.md`), validated by `validate_spec_output.py`, consumed by `code-toolkit:writing-plans` (reads `#### Scenario:` → RED/GREEN tasks). L2/L3 add **more scenarios** — no contract change to the consumer. Hard boundary: SKILL.md token budget (currently 255 lines; ceiling <500 lines / ~6000 tok — L2+L3 prose will pressure this → may extract method detail to `references/`, keeping load-bearing behavior rules inline per `feedback_extract_to_reference_load_bearing_rule`).

Evidence paths: `spec-toolkit/skills/spec-expansion/SKILL.md`, `spec-toolkit/scripts/validate_spec_output.py:124-128`, `spec-toolkit/skills/completeness-critic/SKILL.md`, `spec-toolkit/scripts/test_validate_spec_output.py`, `spec-toolkit/scripts/test_spec_expansion_skill.py`.

## Decision

Build **spec-expansion v0.2** = L2 (Phase ③b, interaction-density-gated, additive, pairwise script for wide stages) + L3 (Phase ①+③c nav-graph 0-switch coverage, broadly-applied, prompt-only, additive), with the completeness-critic reframed to a retained dual role. We will **NOT** rewrite the engine, change the output contract, model UI-widget states, or touch visual presentation. Each layer is gated/applied per the A/B-validated regime, never unconditionally, and every honesty rail (ban-"complete", seed pre-flight, sparse fallback) carries forward.

## Alternatives Considered (Axis 4 — researched EN+JA)

- **L2 wide-stage generation:** (a) **own tiny pure-Python pairwise/IPOG in `scripts/`** ✅ recommended — matches spec-toolkit's zero-dep / agent-portable principle (like `validate_spec_output.py`); grounded in NIST ACTS / pairwise.org + the A/B wide-stage-leak finding. (b) shell out to **PICT** (Microsoft) — rejected: external binary breaks portability. (c) **full cartesian in-prompt** — rejected for wide stages: the A/B showed it leaks (`missed_by_both` up to 11 on 4-object stages). *Reversal:* if dogfood shows in-prompt full-enum suffices up to ~5 objects, defer the script.
- **L3 coverage level:** **0-switch (every nav edge once)** ✅ recommended — ISTQB standard, EN+JA agree it's the pragmatic default; the A/B used 0-switch with zero residue. **1-switch** (transition pairs) optional for high-risk flows; **N-switch** rejected as default (combinatorial explosion — both EN+JA warn). 
- EN/JA agreement worth noting: both literatures warn against claiming "全網羅 / complete" from these techniques — reinforces the existing honesty rail.

Sources: [pairwise.org](https://www.pairwise.org/) · [PICT (classmethod, JA)](https://dev.classmethod.jp/articles/pairwise-testing-with-pict/) · [全網羅の落とし穴 (nihonbuson, JA)](https://nihonbuson.hatenadiary.jp/entry/AllCoverageTrap) · [ISTQB state-transition (getsoftwareservice)](https://getsoftwareservice.com/state-transition-testing/) · [switch coverage 整理 (kzsuzuki, JA)](https://www.kzsuzuki.com/entry/2020/05/06/225904)

## What Becomes Obsolete (Axis 5)

- The design-note framing "critic shifts to a **lighter** role" → obsolete; replaced by the **dual-role** (already corrected in the design note §2). The completeness-critic SKILL.md role description may need a one-line note that L2/L3 now systematize part of what it used to carry by judgment, so it refocuses on single-object-regime recall + nuanced resume-landings + true blind spots.
- The implicit v0.1 assumption that "per-object grid + critic judgment covers cross-object & journey" → explicitly removed (it was the validated gap).
- No **shipped code** becomes obsolete — v0.2 is additive.

## Out of Scope

- Visual presentation (layout / animation / pixel-feel / "looks like the screenshot") — kouko-LOCKED; belongs to an `agent-device` runtime loop.
- UI-component / screen-object modeling in OOUX (derived from backing objects; object-first).
- Tier-2 (brainstorming → spec-toolkit delegation) + OpenSpec DECLARE wiring — deferred; L2/L3 raise its value, re-weigh later.
- 1-switch / N-switch L3 coverage as a default — 0-switch only in v0.2 (1-switch optional, not built unless dogfood demands).
- Changing the output contract or the `code-toolkit:writing-plans` consumer.

## Open Questions

1. **Pairwise script in v0.2, or defer?** The one new code artifact. Include a minimal pure-Python pairwise generator for ≥4-object stages (closes the validated leak), or ship L2 in-prompt-full-enum only + blind-spot wide stages, adding the script in v0.2.1 if dogfood shows leakage? (Recommend: include it — small, mechanical, and the A/B specifically flagged the gap.)
2. **SKILL.md token budget.** L2+L3 prose may push past the ~6000-tok / <500-line ceiling → extract method detail to `references/` (keep load-bearing one-sentence rules inline). Decide split at plan time.
3. **completeness-critic edit scope.** Minimal role-note only, or also add explicit "L2/L3 already systematized — focus your hunt on single-object extremes + resume-landings" guidance? (Lean minimal.)
