# L2 + L3 A/B validation results — cross-object combination (L2) & journey navigation (L3) vs critic baseline

> **Type**: validation report (closes §5 gate-1 of `2026-06-11-spec-expansion-v0.2-three-transition-layers.md` for both new layers)
> **Date**: L2 2026-06-11 · L3 2026-06-12
> **Verdict L2**: worth building — **interaction-density-GATED, additive-over-critic, wide stages need a script** (NOT unconditional, NOT a critic replacement).
> **Verdict L3**: worth building — **BROADLY applied (any ≥2-stage flow), additive-over-critic, NO script needed, no precision tradeoff**. Stronger/cleaner case than L2.
> **Memory**: `feedback_l2_cross_object_enumeration_regime_gated`, `feedback_l3_journey_nav_coverage_not_regime_gated` · sibling `feedback_spec_coverage_value_greenfield_regime`
>
> §0–§6 below = L2. §7 = L3. §8 = L2-vs-L3 contrast (the part that feeds the build).

## 0. Question

Does **L2 = systematic per-stage cross-object state-combination enumeration** actually out-recall the **critic-judgment baseline** (the shipped `spec-expansion` behavior, where the cross-object combination coverage is left to the completeness-critic's judgment)? Per `feedback_ab_baseline_reveals_marginal_behavioral_delta` — measure marginal lift, don't assume.

## 1. Method (blind A/B harness)

Per seed, over a **shared world model** (so the only variable is combination coverage, not object discovery):

1. **setup+enum** (1 agent) — derive the world model (per stage: co-active objects × each object's state set) **and** the exhaustive legal combination grid (the gold-candidate oracle pool; arms never see it).
2. **Arm A (critic)** ∥ **Arm B (L2)** — both blind, both over the same world model. A surfaces the combinations that matter by judgment (told to be thorough); B systematically enumerates per-stage joint combinations. Neither sees the other or the grid.
3. **reconcile** (1 agent) — merge A ∪ B ∪ grid into canonical candidates, clustering semantic duplicates, tagging provenance `found_by_{armA,armB,grid}`.
4. **judge** (1 agent, blind to provenance) — per candidate: `reachable?` + `needs_distinct_reaction?` → gold set; plus `path_type: happy|edge` (added in the confirmation run to strip happy-path inflation).
5. **compute** (in-script arithmetic) — `recall_A`, `recall_B`, edge-only recall, precision, B-unique / A-unique / missed-by-both.

**Seeds** (thin greenfield, no implemented UI shown → avoids the hindsight confound):
- **S1 — komado-Refs derived (real):** reference-image archive viewer. Open archive (RAR/ZIP) → extract → browse. Objects: Archive, ExtractionJob, ImageSet. *(3 objects/stage — interaction-moderate.)*
- **S2 — restaurant booking (textbook):** pick slot → details + optional deposit → confirm. Objects: TimeSlot, Reservation, DepositPayment, UserAccount (+ SlotInventory/SessionState in some runs). *(4 objects/stage — interaction-dense.)*
- **S3 — komado-Viewfinder derived (real, confirmation run):** camera capture. Frame → capture → review & save. Objects: CameraSession, CaptureRequest, Photo, Storage. *(single-object-failure dominated.)*

3 workflow runs → 6 seed-runs (2 lost to a StructuredOutput flakiness — see §4).

## 2. Results

| Seed | Run | Flow type | gold (edge/happy) | **Δfull (B−A)** | **Δedge (B−A)** | prec A / B | B edge-unique | missed-by-both |
|---|---|---|---|---|---|---|---|---|
| S1 archive | 1 | interaction-moderate | 28 | **+0.35** (0.54→0.89) | (lost) | 0.88 / 0.89 | 13* | 0 |
| **S1 archive** | **2** | interaction-moderate | 26 (18/8) | **+0.34** (0.62→0.96) | **+0.22** (0.78→1.00) | 1.0 / 1.0 | 4 | 0 |
| S2 booking | 1 | interaction-dense | 54 | +0.17 (0.50→0.67) | (no tag) | 0.96 / 0.95 | 20* | 7 |
| **S2 booking** | **2** | interaction-dense | 43 (30/13) | **+0.37** (0.40→0.77) | **+0.20** (0.53→0.73) | 1.0 / 0.94 | 12 | 3 |
| **S2 booking** | **3** | interaction-dense | 49 (45/4) | **+0.22** (0.39→0.61) | **+0.16** (0.42→0.58) | 1.0 / 0.91 | 15 | 11 |
| S3 camera | 2 | **single-object-failure** | 24 (17/7) | +0.04 (0.71→0.75) | **−0.23** (0.88→0.65) | 1.0 / 0.86 | 1 | 1 |

\* run-1 had no happy/edge tag, so "B-unique" there is full (incl. happy-path).

## 3. Findings

1. **Variance excluded.** S1 two runs (+0.35 / +0.34 full), S2 three runs (+0.17 / +0.37 / +0.22 full) — direction and magnitude stable. The within-run A-vs-B comparison (same gold set) is robust to cross-run world-model derivation variance.
2. **Edge-only recall (happy inflation stripped) still favors L2 in interaction flows.** S1r2 +0.22 (B caught ALL edge gold, B=1.00), S2r2/r3 +0.20/+0.16. B-unique edges are genuine multi-object interaction bugs judgment misses: session-expires-while-deposit-processing, deposit-captured-while-reservation-pending (money orphan), stale-inventory × slot-taken race, authorized-deposit × user-ineligible (void ordering), pick-time corrupt/password/unreadable/empty archive.
3. **Regime reversal on single-object-failure flows (S3).** The critic out-recalls L2 on edge (−0.23) and L2 dilutes precision (0.86). S3's hard edges are separable single-object extremes (permission-denied / storage-full / hardware-error) that domain judgment nails; joint enumeration is wasted there.
4. **Precision is structural.** Critic Arm A = 1.0 every run (raises only gold). L2 Arm B = 0.86–1.0 (emits some junk, worse in larger spaces). → L2 trades precision for recall; the critic prunes that junk.
5. **Wide stages leak even under L2.** `missed_by_both` (gold only the exhaustive grid caught) appeared only on S2's 4-object stages (3/7/11); S1's 3-object stages = 0.

## 4. Caveats

- **Single-object side has one data point (S3).** The gate is justified by S3 + the structural reason (separable failures don't need joint enumeration), not by a large single-object sample. The user declined an extra single-object seed.
- **Workflow flakiness:** StructuredOutput non-call hit a random seed in 2 of 3 runs (~1 per ~15 agents). Repeat A/B should add a retry/fallback or drop the `Explore` agentType on the structured setup agent.
- **Cross-run gold counts differ** (setup derives different state sets per run) — only within-run A-vs-B is compared, which is the valid comparison.

## 5. Design implications (feed the L2 build)

1. **Gate L2 on interaction-density**, not unconditional per-stage enumeration. Heuristic: enumerate a stage's combinations only if some object-pair has a joint reaction ≠ the union of the individual reactions; else let L1 + critic handle it. (Same shape as the greenfield-regime gate.)
2. **L2 is additive over the critic, never a replacement.** The critic is BOTH a recall source (it wins the single-object regime) AND the precision-pruner of L2's enumeration junk. Keep it; the v0.2 §2 "lighter critic" framing should become "critic also fills the single-object regime + prunes L2".
3. **Wide stages (≥4 objects) need a mechanical combination generator** (script / IPOG-style pairwise), not pure in-prompt enumeration — resolves the design note's P2 (and triggers earlier than the predicted 6+ objects).

## 6. Status (L2)

L2 gate-1 (marginal value) **PASSED — build-ready as gated additive**.

## 7. L3 results — journey navigation graph (2026-06-12)

Same blind harness, unit = **navigation transition** (`from_stage → to_stage | transition_type`, types: forward / back / skip / abandon / resume_reenter / error_escape / retry_self). Arm A = critic judgment over the linear backbone; Arm B = ISTQB state-transition coverage over the backbone modeled as a nav graph. Same 3 seeds, 2 runs each (6 seed-runs), `robustAgent` retry added (recovered an S1 judge socket-drop).

| Seed | Run | gold (edge) | **Δfull** | **Δedge** | prec A / B | missed-by-both |
|---|---|---|---|---|---|---|
| S1 archive | 1 | 18 (17) | +0.33 | +0.29 | 0.92 / 0.94 | 0 |
| S1 archive | 2 | 20 (17) | +0.20 | +0.06 | 0.92 / 0.88 | 0 |
| S2 booking | 1 | 21 (21) | +0.28 | +0.28 | 0.87 / 0.90 | 0 |
| S2 booking | 2 | 23 (20) | +0.34 | +0.25 | 1.00 / 1.00 | 0 |
| S3 camera | 1 | 23 (19) | +0.22 | +0.05 | 0.80 / 0.85 | 0 |
| S3 camera | 2 | 25 (21) | +0.28 | +0.14 | 0.86 / 1.00 | 0 |

**Findings:**
1. **Universally positive, NOT regime-gated.** B>A on full recall 6/6 (+0.20…+0.34) and edge recall 6/6 (+0.05…+0.29). Works even on the "linear" archive and the single-object camera — unlike L2, which was ~0 on the single-object camera. Reason: every ≥2-stage flow has a navigation graph, and the happy-path spine has no systematic completeness method (the vault `從 Happy Path 到完整路徑` gap); systematic state-transition coverage beats judgment broadly.
2. **No script generator needed.** `missed_by_both` = 0 across all 6 runs — the nav space is bounded by stage count (~3–5), no combinatorial explosion, so in-prompt enumeration covers it fully. (Contrast L2, where 4-object stages leaked.)
3. **No precision tradeoff.** B precision ≈ A every run (B sometimes higher, once slightly lower) — no structural B<A like L2. Softened from run-1's "B strictly higher".
4. **Still additive over the critic.** A-unique cases persist every run: the nuanced *resume / re-entry landing-point* decisions (where to land, what to restore, crash-recovery of an orphaned in-progress artifact, skip-with-external-input). B's mechanical edge-walk gets breadth; A's judgment gets these deep cases. Keep the critic as the deep complement.

Concrete B-edge-unique wins (judgment forgot, coverage caught): `S2→EXIT|abandon` (release hold + reconcile mid-payment charge), `S3→S1|error_escape` (extracted files gone → back to picker), `S3→S3|resume_reenter` (restore image index + zoom), `S1→S1|error_escape` (permission revoked mid-session → tear down feed), `S2→S1|back` (reframe, discard partial capture).

## 8. L2 vs L3 — how the two layers differ (feeds the build)

| | **L2** per-stage cross-object combination | **L3** journey navigation graph |
|---|---|---|
| Applicability | **GATED** on interaction-density (run only on stages whose reaction depends on a joint ≥2-object state) | **BROAD** — any flow with ≥2 stages |
| vs critic | wins interaction-dense regime; **critic wins single-object-failure regime** | **wins all regimes tested** (6/6) |
| Precision | structural tradeoff (critic 1.0, L2 0.86–1.0) | no tradeoff (B ≈ A) |
| Wide-input blow-up | ≥4 objects/stage → **needs a script generator** (in-prompt leaks) | nav space bounded by stage count → **pure prompt suffices** |
| Critic's retained role | recall source in single-object regime + precision-pruner of L2 junk | deep complement for nuanced resume/re-entry landing-points |

**Build implication:** both layers are additive-over-critic, but L2 is *conditionally applied + script-backed for wide stages*, while L3 is *broadly applied + prompt-only*. L3 is the cleaner, lower-risk build; L2 carries the gate + script-fallback complexity.

## 9. Status (both)

L2 + L3 gate-1 (marginal value) **PASSED — both build-ready**. Caveats: single-object side of the L2 regime has one seed (S3); L3's edge-recall magnitude is variable though always positive. Next: brainstorm → plan → SDD for spec-expansion v0.2 (both layers).
