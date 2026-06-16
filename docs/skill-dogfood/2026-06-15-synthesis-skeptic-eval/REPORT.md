# Eval — synthesis-level adversarial check (缺口 1) — A/B, 6 seeds

date: 2026-06-15 · skill: deep-deep-research · status: findings (eval-first, pre-build)

## Question (null hypothesis to break)
A strong model's single-pass synthesis is already clean enough that a synthesis-level
skeptic pass finds nothing material → it would be a crutch, don't build.

## Design
- 6 seeds (3 investing add/trim/income-hold, 3 SWE macOS/microservices/k8s; 2 thin).
- Per seed: realistic confirmed-claims block (sonnet) → **Arm A** single-pass synthesis
  (sonnet, = current pipeline behaviour, no self-critique).
- Then, blind + independent, both opus:
  - **JUDGE** = ground-truth auditor (strict, default-not-flag) → material-defect list.
  - **SKEPTIC** = Arm B candidate feature (adversarial review of Arm A).
- Cross-model: generator = sonnet, judge+skeptic = opus (breaks same-model overclaim on
  the generator axis). Caveat: judge↔skeptic same model — see Limits.

## Results

| seed | judge material | skeptic found | skeptic verdict | recall | hallucinated? |
|---|---|---|---|---|---|
| ASML (add) | 1 (China 29% buried tension) | 2 (rated minor) | MINOR_REV | caught (sev↓) | 0 |
| Nvidia (trim) | 1 (export-ctrl overconf) | 2 (material) | MATERIAL_REV | caught ✓ | 0 |
| banks (income, thin) | 0 | 2 (minor) | MINOR_REV | n/a (agreed clean) | 0 |
| macOS (channel) | 0 (1 minor) | 2 (minor) | MINOR_REV | agreed | 0 |
| microservices | 0 (2 minor) | 3 (2 material) | MATERIAL_REV | n/a | 0 (judge under-rated) |
| k8s (thin) | 3 | 3 (2 material) | MATERIAL_REV | 3/3 ✓ | 0 |

- **Base rate of material defects (ground truth): 5 across 6 seeds; 3/6 seeds affected.**
  → **NULL HYPOTHESIS BREAKS.** Even a capable single-pass synthesis leaves material
  aggregation defects at a meaningful rate.
- **Skeptic recall on judge-material: 5/5 caught** (ASML downgraded to minor by skeptic).
- **Skeptic precision: 0 hallucinations / 6 seeds.** Every skeptic finding is verifiable
  against the claims. On the genuinely-clean seed (banks) the skeptic explicitly declined
  to manufacture a material defect.
- **Severity-line noise: 2/6 seeds** (ASML judge=material/skeptic=minor; microservices
  judge=minor/skeptic=material). The robust signal (real defect present vs clean) agreed;
  the material/minor line is model-dependent (= [[feedback_cross_model_validation_breaks_same_model_overclaim]]).

## The recurring defect class (4 of 5 material)

**CONFIDENCE-LAUNDERING / aggregation overconfidence** — not present in any single claim,
only created at the merge/aggregate step (which claim-level Stage-5 verification structurally
cannot catch):
1. **Merged finding tagged at the strongest claim's confidence, not its weakest load-bearing
   claim** (Nvidia: export-rule [high] launders the China-magnitude estimate [medium]; k8s:
   [8] editorial-gloss elevated to [high]; micro: low [8] folded into a [7]-voted [medium] row).
2. **Split / tied votes flattened into "consensus"** (k8s: a 2-2 tie presented as "consensus
   converge"; banks: a 1-1 split absorbed into framing).
3. **Summary headline more confident than the hedged body/claims** (ASML: "restrictions
   threaten ~29%" while body says ceiling-case + legacy-node; micro: "modular-monolith
   delivers faster velocity for most monoliths" from one org + one heuristic; Nvidia:
   "resolved/permanent" headwind contradicted by its own open question).

**What did NOT appear:** the "buried decisive / moot factor" failure that purpose-fit (lever ③)
targets. Arm A *surfaced* mooting factors well (macOS FDA gate, microservices modular-monolith,
k8s small-team verdict all elevated correctly). → 缺口1 addresses a **different** defect class
than purpose-fit: confidence discipline at aggregation, not relevance/decisiveness.

## Bitter-Lesson read

- A synthesis-level skeptic is **verification-class** (checks ON output), not a crutch — it
  catches real aggregation defects that claim-level verification cannot. The null broke.
- BUT the eval also shows the dominant defect class is **largely PREVENTABLE at generation**
  by explicit confidence-calibration rules (don't tag a merged finding above its weakest
  load-bearing claim; never call a split/tied vote "consensus"; headline confidence ≤ body).
  ~3/5 material defects would be stopped by a prompt rule — cheaper than a full extra pass.
- prompts.py synthesis is a **SYNCED primitive (Do Not Touch)** → any generation-side fix must
  ride the PREPEND mechanism (like meta-mode / purpose-fit) or the sync, not edit prompts.py.

## Decision options (eval-grounded)
- **A. Calibration-prepend (cheap, generation-side)** — a short additive directive prepended to
  the synthesis prompt encoding the 3 anti-laundering rules. Stops ~3/5 material defects at zero
  extra agent pass. Mirrors meta-mode/purpose-fit; no synced-primitive edit.
- **B. Skeptic-pass (full, verification-side)** — one opus adversarial review of the final
  synthesis → flag/return material defects. Recall 5/5 but +1 pass/run and severity noisy →
  should FLAG for reader, not auto-rewrite.
- **C. Hybrid** — A always-on (cheap), B opt-in for high-stakes / contested syntheses.
- **D. Don't build** — rejected: null broke (5 material / 6 seeds).

## Round 2 — strengthening (cross-model judge + N→8)

Per user request ("先補強 eval 再決定"), added (a) a **second judge in a different model
(sonnet)** re-auditing the same 6 Arm-A syntheses blind, and (b) **2 new seeds**: Raft
(descriptive, deliberately CLEAN control = precision test) + Rust adoption (decision, mooting
potential).

**Cross-model judge agreement (opus judge vs sonnet judge, material counts on seeds 1–6):**

| seed | opus | sonnet | same defect region? |
|---|---|---|---|
| ASML | 1 | 0 (minor) | yes — China-29% headline |
| Nvidia | 1 | 1 | yes — export "resolved" overconfidence |
| banks | 0 | 1 | yes — summary states low-conf −10% as fact |
| macOS | 0 | 0 | yes — both ~clean (only minor kext tag) |
| microservices | 0 | 1 | yes — DORA props "deployability=high"/speed crux |
| k8s | 3 | 1 | yes — [8] editorial-gloss tagged high |

→ **The robust binary (real defect present vs clean) agrees on 6/6.** Only the MATERIAL/MINOR
line wobbles (model-dependent, as predicted). A *different model* independently confirms the
defects → they are NOT opus hallucination. This directly answers the same-model-overclaim worry.

**New seeds (each: opus judge + sonnet judge + skeptic):**

| seed | opus judge | sonnet judge | skeptic | read |
|---|---|---|---|---|
| Raft (CLEAN) | 0 material | 0 material | 0 material (2 genuine minor, declined near-misses) | **PRECISION PASS — no cry-wolf on clean** |
| Rust (decision) | 1 material | 1 material | 1 material (+1 minor) | all three converge on same confidence-laundering defect |

**Updated totals (8 seeds):**
- **Real material defect present (≥1 model): 6/8.** Genuinely clean: 2/8 (macOS, Raft).
- **Every material defect is the same class: confidence-calibration at aggregation** —
  medium/low/split-vote claim tagged high on a load-bearing finding, or summary more confident
  than its own body. Relevance / moot-burying did NOT appear (Arm A surfaced decisive factors
  well on macOS/microservices/k8s/Rust).
- **Skeptic: 0 hallucinations / 8 seeds; 0 material on the clean control (Raft).** Recall: hit
  the defect region on every seed that had one. Precision is the strong result — it stays quiet
  when the synthesis is sound.

## Refined verdict (post-strengthening)
- Null is **firmly broken, cross-model**: 6/8 seeds carry a real material aggregation defect.
- The defect is **one narrow, well-characterized class** (confidence-laundering / headline>body),
  NOT a broad analysis weakness → a **cheap generation-side calibration rule targets it directly**
  and would prevent most of the 6/8. This shifts the recommendation toward **Option A first**
  (calibration-prepend) as the Bitter-Lesson-cleanest, highest-ROI build; B/C add the (noisier)
  severity/edge coverage and the cry-wolf-safe skeptic, deferrable until A is shown insufficient.

## Honest limits
- N=6, single judge per seed; judge↔skeptic both opus (recall may be optimistic; a sonnet judge
  could rate Arm A cleaner — untested). Mitigation: defects are concrete + claim-checkable (e.g.
  k8s [6] genuinely a 2-2 vote; [8] verifier literally says "editorial gloss overstates"), so
  they're robust to model choice. Generator=sonnet vs judge=opus is cross-model on the key axis.
- Confirmed-claims blocks are constructed (sonnet), not real pipeline output — but the eval tests
  the *aggregation layer's* behaviour on a given block, which is the target.
- 4/6 seeds carry split-vote / low-confidence material by design (realistic), which may slightly
  raise the laundering base rate vs uniformly-strong inputs.
