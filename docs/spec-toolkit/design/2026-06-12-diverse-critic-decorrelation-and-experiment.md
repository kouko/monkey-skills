# Diverse-critic decorrelation for relative-completeness — design + validation experiment plan

> **Type**: design note + experiment plan (NOT yet built, NOT yet run). Date: 2026-06-12.
> **Mission anchor** (`project_spec_toolkit_mvp`): achieve **internal/relative completeness** — cover everything the GIVEN requirements entail or that's reasonably inferable, honestly marking inferred vs residual. NOT external/absolute completeness (unverifiable). Failure = a requirement-entailed situation silently dropped (dropped-but-flagged = honest residual, not failure).
> **Upstream research**: `2026-06-12-sdd-harness-bitter-lesson.md` (verification scaffolding is Bitter-Lesson-proof); the RE internal-vs-external completeness distinction (Leveson input-space partitioning, perspective-based reading, capture-recapture).

## Part A — Design

### A1. What we build vs what we reject
Both start from "run K independent completeness-critics on a spec draft", but:

- ✅ **BUILD — K diverse critics → UNION + loop-until-dry (a SEARCH).** Report only what was FOUND; add the union of gaps to the spec (raises recall toward relative-completeness); stop when K consecutive diverse rounds find nothing new ("relatively saturated relative to these perspectives"). Makes **no claim about the unseen** → cannot manufacture false completeness; worst case = honest under-coverage. This is verification scaffolding (keep regardless of model strength); design it deletable.
- ❌ **REJECT — capture-recapture POINT estimate / completeness-% (an EXTRAPOLATION).** Infers a number for the UNSEEN residual from the overlap ratio. Its validity needs INDEPENDENT captures; K LLM critics share one base model → **positively correlated captures** (find the same, miss the same) → estimator reads high overlap as "nearly exhausted" → **systematically UNDER-estimates residual → false completeness** (honesty-rail #3, the most dangerous failure). Numeric illustration: 100 true gaps, correlated critics each find the same easy 12 (overlap 11) → Lincoln-Petersen N̂ = 12·12/11 ≈ 13 → claims ~92% complete; reality 88 unfound. 🟡 If a number is ever wanted, only a heavily-caveated residual LOWER BOUND ("≥N, likely many more") as a stop/continue signal — never a percentage.

### A2. Why decorrelation matters (and its ceiling)
The shared weakness of both is correlated same-model critics drying up together. Decorrelation:
- **boosts UNION recall** (more orthogonal perspectives → more distinct gaps found) — a real win for the BUILD path;
- does **NOT** make capture-recapture safe (residual correlation remains; the estimator is hypersensitive to it).

So decorrelation is a **recall accelerator for the loop**, not a license for a statistical estimate. Same-base-model critics can never be fully decorrelated (shared prior).

### A3. Decorrelation levers (single-model-host realistic order)
Overlap sources → levers:

1. **Distinct lens / defect-class mandate (strongest; = Perspective-Based Reading, Basili).** Partition the defect space into disjoint mandates, one per critic: (a) state-completeness [every state×input has a response — Leveson], (b) error/empty/loading paths, (c) NFR/security/concurrency/timing, (d) permissions/actors, (e) data/boundary [BVA], (f) cross-object combinations + journey navigation [L2/L3]. Critics stop competing on the same cells.
2. **Distinct persona / adversarial frame** — malicious user, confused first-timer, 3am on-call ops, compliance auditor, competitor probing edges. Changes salience.
3. **Distinct input view** — don't feed every critic the same full draft; give slices/representations (state machines only / journey graph only / data model only / **original-requirements-only, not the draft** → catches "requirements entail X, draft dropped it").
4. **Blind-parallel vs adversarial-sequential** — parallel-blind (no anchoring) OR sequential where each round is told to hunt the COMPLEMENT of prior rounds (explicit anti-correlation; this is the loop-until-dry tail).
5. **Different model / tier (only lever touching the root cause)** — different model family → different priors → different blind spots. Within one Claude Code host you usually have one family → levers 1–4 are realistic, 5 is aspirational/future.

### A4. Overlap rate as a diagnostic (not a completeness claim)
Measure pairwise finding-overlap (Jaccard) between critics: ~90% → redundant panel, add a more orthogonal lens; ~20–40% → genuine diversity. **High overlap signals "panel not diverse enough", NOT "nearly complete"** — the exact misread capture-recapture makes.

## Part B — Validation experiment plan

### B1. Hypotheses
- **H1 (decorrelation works):** a DIVERSE critic panel has lower mean pairwise overlap AND higher union recall (of known gaps) than a HOMOGENEOUS panel of the same size N, on the same spec. Replicated.
- **H2 (capture-recapture misleads):** plugging each panel's overlap structure into capture-recapture UNDER-estimates the KNOWN residual (optimistic bias), MORE severely for the homogeneous panel → empirically justifies rejecting the point estimate.
- **H3 (loop-until-dry convergence):** the diverse panel's union recall saturates after some round R; report the marginal-recall-per-critic curve → the practical K.
- **H4 (lens load-bearingness):** which lens mandates contribute the most UNIQUE recovered gaps vs which are redundant.

### B2. Ground truth via DEFECT-SEEDING (the SE-standard method for validating capture-recapture)
Take spec drafts that are reasonably complete relative to a stated requirement (e.g. fuller versions of the L2/L3 dogfood seeds: archive viewer / booking / camera / PiP-note). **Remove M known requirements/scenarios** — a deliberate MIX of obvious + subtle — recording them as the **GOLD residual set** the critics must recover. A known injected population is exactly what capture-recapture claims to estimate → direct bias measurement. Track non-seeded real findings separately (precision/bonus), keep the primary metric on the known M.

### B3. Panels (each over the SAME seeded spec, all blind to each other + to gold)
- **P-homog:** N critics, identical generic "hunt omissions" prompt.
- **P-diverse:** N critics, each a distinct lens (B/A3.1) + persona + input view.
- **P-seq (optional):** N sequential rounds, each told to hunt the complement of prior rounds.
- N ≈ 4–6. Same base model across all (we are testing whether LENS diversity decorrelates within one model — the realistic lever).

### B4. Pipeline (per seeded-spec × panel) — mirrors the L2/L3 blind A/B harness
1. setup: take the seeded spec + record the gold residual set (the removed M).
2. run the N critics blind (parallel for P-homog/P-diverse; sequential for P-seq).
3. reconcile (judge, blind to provenance): dedup findings semantically; map each found gap → a gold gap or non-gold.
4. compute, in-script:
   - mean pairwise overlap (Jaccard) across critics;
   - union recall = |gold recovered by ∪ critics| / M;
   - marginal-recall curve (add critics 1..N) → saturation round;
   - capture-recapture estimate (Lincoln-Petersen pairwise + a Chao/jackknife N-sample variant) of total population → implied residual; compare to TRUE residual (M − recovered) → **bias**;
   - precision (non-gold rate);
   - per-lens unique-contribution (for P-diverse).
5. confirmation run (2nd independent measurement) + multi-seed, per `feedback_ab_baseline_reveals_marginal_behavioral_delta`. robustAgent retry for StructuredOutput flakiness.

### B5. Decision criteria
- **H1 PASS** → diverse union-recall > homog by a meaningful, replicated margin at lower overlap → build P-diverse as the completeness-critic panel; lock the load-bearing lenses (H4).
- **H2 PASS** (capture-recapture under-estimates known residual, worse for homog) → confirms "ship the loop, not the point estimate"; if even diverse panels mis-estimate, the residual-lower-bound idea is also dropped (or kept only as a stop signal).
- **H3** → sets the default K and the loop-until-dry stop rule (R consecutive dry rounds).
- **H4** → prunes redundant lenses (keep the orthogonal, high-unique-contribution set).

### B6. Honesty controls (from prior lessons)
- Seed obvious + subtle gaps (not only easy ones) so recall isn't inflated.
- Critics blind to each other + to gold; judge blind to panel/lens provenance.
- Same base model by design (this IS the test); model-diversity (lever 5) is a future arm if multiple models get wired in.
- Single-run → confirmation run for variance; multi-seed across regimes (greenfield/brownfield, narrow/wide).
- Watch the defect-seeding confound: removed requirements must be genuinely entailed by the stated requirement (else they're "external" gaps the mission excludes).

### B7. Expected cost / shape
~ (3 panels × 2–4 seeds × [N critics + reconcile + judge]) ≈ a 30–60 agent blind workflow, same family as the L2/L3 A/B harness — runnable as one Workflow with a confirmation re-run. Output: per-hypothesis verdict + the locked lens set + the loop stop-rule.

## Part C — Experiment results (2 runs, 2026-06-12)

Ran B as a blind workflow, 3 seeds × {homog, diverse} × 5 critics × blind judge, twice (defect-seeding regenerates draft+gold each run → confirmation is across fresh gold instances of the same requirements; compare EFFECT not absolute numbers). One cell invalid (run2 `judge-homog:S1` hit a session limit → excluded).

| Signal | Verdict | Evidence |
|---|---|---|
| **H1 decorrelation (overlap)** | ✅ **ROCK SOLID** | diverse mean-overlap 0.22–0.40 vs homog 0.67–0.96 on every valid cell (5/5) |
| **H1 union recall** | ✅ small but real | diverse > homog by ~+0.05–0.11 on 4/5 valid cells; the one run-1 negative (S3) did NOT replicate (noise). Recall lift is modest — both panels already reach 0.83–1.0 with 5 critics |
| **Precision (nongold noise)** | ✅ **ROCK SOLID (the biggest practical win)** | homog 67–121 off-target findings vs diverse 20–34 → ~3–4× less noise (lens-scoping keeps critics in lane) |
| **H2 capture-recapture under-estimates (homog)** | ✅ **CONFIRMED + clean** | homog under-estimates the KNOWN total on 4/5 valid cells (e.g. overlap 0.93 → Chao 15 < true 18 = textbook false-completeness); diverse NEVER under-estimates (0/6) — it over-estimates (Chao 19–23 vs true 17–18, conservative/safe; high f1 inflates Chao) |
| **H3 saturation** | homog saturates early+low (correlated→redundant); diverse climbs higher and sometimes not yet saturated at 5 → loop-until-dry genuinely adds | marginal curves |
| **H4 load-bearing lens** | ✅ **nfr_security #1** (generic critics structurally blind to it; uniquely recovered 3 gaps on multiple seeds, both runs); permissions secondary; **error/state redundant** (generic hunting already covers) | per-lens unique counts |

**Confound (honest):** the setup agent co-designs draft+gold with ≥2 gaps/class, which aligns gold with the diverse lenses → slightly favors diverse on recall; but overlap-drop, precision, H2 mechanism, and H4 are NOT sensitive to gold class-balance. Single-/double-run; Chao has high variance on small f1/f2. A future variant could FIX the gold and re-run only critics to isolate critic-panel variance (vs the current across-gold robustness test).

## Verdict & Status
**Experiment supports BUILD of the diverse-lens critic panel — value = ~3–4× higher precision + recovers NFR/security gaps generic critics miss + higher saturation ceiling (loop-until-dry adds), NOT a big recall lift.** Capture-recapture point-estimate stays REJECTED as primary (homog false-completeness reproduced); usable only as a conservative/over-estimate signal AFTER demonstrated low overlap, never a completeness %. Load-bearing lenses: **nfr_security > permissions / data_boundary > (error / state can be trimmed / merged with generic)**.
Next: brainstorm→plan→SDD the diverse-lens loop into `completeness-critic` (lens panel + loop-until-dry + overlap-as-diagnostic; design deletable per Bitter-Lesson). Optional: gold-fixed critic-variance variant before building.
