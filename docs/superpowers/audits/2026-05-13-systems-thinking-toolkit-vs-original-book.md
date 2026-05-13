# systems-thinking-toolkit v0.6 — Coverage Audit vs Original Book

**Date**: 2026-05-13
**Plugin state at audit time**: v0.6.0 (7 functional skills + 1 router); commit `7d0c2a0`
**Source book**: Dennis Sherwood, *Seeing the Forest for the Trees: A Manager's Guide to Applying Systems Thinking* (Nicholas Brealey, 2002)
**Audit baseline**: `systems-thinking-toolkit/references/BOOK_OVERVIEW.md` (Stage 0) + `INDEX-original.md` (Stage 3 14-skill original) + `VERIFIED.md` (Stage 1.5 verification record)

## Purpose

Honest answer to: "What's missing in the plugin compared to the original book?" Distinguishes (a) **deliberate scope cuts** documented in the distill pipeline, (b) **content merged into surviving skills** (not missing, just absorbed), and (c) **inherited 2002-vintage gaps** the book itself has.

## Methodology

For each of Sherwood's 7 top-level arguments (per `BOOK_OVERVIEW.md`),
trace whether the plugin covers it and where. Cross-check against the
Stage-1.5 VERIFIED.md rejection records (3 cases dropped, 6 principles
rejected, 9 counter-examples filtered, 1 glossary term cut). Surface
the deltas.

## Coverage by Sherwood's 7 top-level arguments

| # | Sherwood Argument | Book Chapter | Current plugin coverage |
|---|---|---|---|
| 1 | Reductionism fails for connected systems | Prologue, Ch 1 | ✅ Foundational R-section quotes in `cld-craft`; ontology preserved across all skills' "what is a system" framing |
| 2 | CLDs are the universal visual language | Ch 2-4 | ✅ `cld-craft` entire body + `cld-mermaid-emit.md` reference |
| 3 | All loops reduce to R (even-O) or B (odd-O) | Ch 4-6 | ✅ `cld-craft` Step 11 + `loop-classification-protocol.md` reference (Tier-1 + Tier-2 Sterman + variance audit ce27) |
| 4 | CLD construction is a craft (12 rules) | Ch 7 | ✅ `cld-craft` I + Steps 1-10; all 12 rules enforced |
| 5 | Limits-to-growth master archetype + take-the-brakes-off | Ch 8 | ✅ `cld-archetypes` Branch L + cases.md A1-A3 |
| 6 | Strategy = lever target settings + multi-stakeholder | Ch 9-10 | ✅ `strategy-lever-and-cascade` (levers/outcomes + 3-timescale + 3×N + Martian-test in Step 5 since v0.6) + `cld-overlay` (outward stakeholder) + `team-mental-model` (inward harmony) + `manager-personality-quadrant` (Gods/Gamblers/Grinders/Guides; v0.6 strengthened to "facilitation vocabulary only") |
| 7 | Toolkit scales up (Gaia) and down (ithink) | Ch 11-13 | ⚠️ **HALF COVERAGE** — Gaia (Ch 11) cut at Stage 0; ithink (Ch 12-13) reduced to text-only `simulation-modeling` |

## Genuine gaps (vs the book itself)

### 1. Ch 11 Gaia / planetary-scale systems thinking — EXPLICIT CUT (Stage 0)

`BOOK_OVERVIEW.md` Section 4.2 marks Ch 11 as "Content NOT suitable for skills":

> Gaia / global warming chapter — too domain-specific and too 2002-dated;
> the underlying constrained-R-loop pattern is reusable, but not the
> Gaia framing itself.

Stage-1.5 VERIFIED.md confirms:

> **Ch 11 (Gaia / Easter Island / global warming) excluded** per
> BOOK_OVERVIEW recommendation — the underlying constrained-R-loop
> pattern is preserved in sk05 [now `cld-archetypes` Branch L]; the
> chapter's specific Gaia framing is too 2002-dated and domain-specific.
> Glossary term g36 (Gaia) dropped.

What's NOT in the plugin as a result:
- Planetary / Earth-systems-scale CLD examples
- Public-policy / climate-policy CLD facilitation
- Multi-jurisdictional R+B coupling (e.g. carbon emissions × atmospheric residence time × adaptation capacity)
- Strong-Gaia vs weak-Gaia distinction
- Easter Island as standalone — present only as Case A3 paired with Caulerpa algae in `cld-archetypes/cases.md`

**Status**: User-approved cut. Reusable pattern preserved. Re-introducing Gaia framing would require user override.

### 2. Ch 12-13 executable stock-flow simulation — SCOPE REDUCTION (v0.1 → v0.6)

`simulation-modeling` is **text-only**. Sherwood's ithink/Stella numerical walkthroughs are not reproducible:

- **Ch 12 stock-flow translation primitives** — covered conceptually in `simulation-modeling` SKILL.md (translate CLD → stocks + flows + connectors); but no executable simulator
- **Ch 13 quantitative car-dealership case** — present as Case A2 in `cld-archetypes/cases.md` (qualitative; "Methodology applied (retrospective)" framing); the actual numerical simulation showing S-curve overshoot detection / inventory oscillation amplitude / 3-loop interactions is NOT in the plugin
- **Bathtub / coffee-cup stock-flow analogies** — present as text references; not as runnable examples
- **Behavior-over-time (BoT) graphs** — Sherwood pairs CLDs with BoT to surface delays; plugin has no BoT generation tool

**Status**: Deferred v0.5+ candidate "Python stock-flow companion script for simulation-modeling" (per `ROADMAP.md`). Pending. The qualitative learning lessons (model-for-learning-not-answers) are intact.

### 3. Ch 2-3 pre-CLD failure case studies — INCOMPLETE (covered as quotes, not standalone)

Sherwood demonstrates "the cost of *not* using CLDs" via reductionism-failure cases in Ch 2-3 before introducing the formal apparatus. These appear in current plugin as:

- Embedded **quotes** in `cld-craft` R section
- Scattered **anti-pattern callouts** in various Boundary sections

They do NOT appear as:

- Standalone "what-happens-without-systems-thinking vs with" comparison case
- Calibration set for "reductionism trap" pattern recognition

**Status**: Implicit. A new case 11-or-A4 candidate ("cost of reductionism" worked example) could be added in v0.7 if pedagogical value justifies.

### 4. Specific narratives demoted at Stage 1.5

VERIFIED.md records the following demotions from would-be cases:

| Dropped at Stage 1.5 | Reason | Where in plugin (if anywhere) |
|---|---|---|
| **c13 Adam Smith / Invisible Hand** | Bound only to abstract "emergence"; no surviving skill leans on emergence as primary | Not in plugin — emergence concept handled implicitly in `team-mental-model` via self-organization |
| **c16 Jay Forrester biographical sidebar** | Historical context only; no skill needs the biography to function | Not in plugin — historical-pedagogical content cut |
| **c22 BBC dominance context for c15** | Context-for-context; `cld-overlay` can cite c15 (TV "talent problem") directly | Not in plugin — context-of-context cut |

Plus 6 principles + 9 counter-examples filtered as too-general "systems-thinking warnings without distinctive procedure" (per VERIFIED.md Summary). Their pattern content was absorbed into surviving skills' Boundary sections.

**Status**: Filter is defensible per Stage-1.5 verification methodology. Re-introducing any of these would require new V1+V2+V3 evidence.

## Inherited 2002-vintage gaps (book itself has them)

These are limitations of the *source material*, not the plugin's failure to extract. Plugin partially addresses some via v0.5 + v0.6 additions; most remain open.

| # | Gap | Plugin partial coverage |
|---|---|---|
| 5 | **Platform-economy R-loops** (network effects, two-sided markets, algorithm-driven attention) | v0.5 Case B5 (algorithm-belief pseudo-target dangle) covers one pattern; network-effects + winner-take-most dynamics NOT covered |
| 6 | **2008-style cross-firm systemic contagion** | NOT covered. Sherwood's R-loops are within-firm; financial / supply-chain contagion is out of frame |
| 7 | **Behavioral economics biases as system-level drivers** (Kahneman, Tversky, Thaler) | NOT covered as primary mechanism. `manager-personality-quadrant` v0.6 Graduate-beyond routes to Klein 1998 / Kahneman externally |
| 8 | **CLD falsifiability protocol** | NOT covered. Sherwood Rule 10 ("recognized as real") is social validation, not empirical. Plugin inherits gap |
| 9 | **Modern facilitation tools** (Miro / FigJam / async-distributed workshops) | NOT covered. `team-mental-model` Boundary already flags "energy-pumping metaphor assumes co-presence" |
| 10 | **Modern personality science** (Big Five NEO-PI-R, Hogan PI) | v0.6 sk14 Graduate-beyond routes out to these externally; not internalized as plugin content |
| 11 | **Agent-based modeling alternatives to CLDs** | NOT covered. `cld-craft` Boundary mentions DAG / ABM but doesn't compare |
| 12 | **Causal-inference DAGs** (Pearl) | NOT covered. `cld-craft` Boundary mentions Pearl but explicitly distinguishes (S/O ≠ DAG direction) |

## Absorbed content (NOT missing — present but not standalone)

The Stage 3 → v0.1 → v0.4 → v0.6 progression merged/absorbed content into fewer skills. These are sometimes mis-read as "lost":

| Original (Stage 3, 14-skill) | Current location |
|---|---|
| sk01 reinforcing-balancing-loop-diagnosis | `cld-craft` Step 11 (R3-3 absorb, v0.4) |
| sk02 s-o-link-assignment | `cld-craft` Step 11 + `loop-classification-protocol.md` (R3-3 absorb, v0.4) |
| sk03 cld-drawing-craft-12-rules | `cld-craft` Interpretation + Steps 1-10 (v0.1 merge with sk04) |
| sk04 fuzzy-variable-elevation | `cld-craft` Step 4 (Rule 7 sub-procedure) + split-fuzzy-variable trick in Step 5 (v0.1 merge with sk03) |
| sk05 limits-to-growth-take-the-brakes-off | `cld-archetypes` Branch L (R3-1 merge with sk06, v0.4) |
| sk06 variance-target-action-template | `cld-archetypes` Branch V (R3-1 merge with sk05, v0.4) |
| sk07 lever-vs-outcome-reframing | `strategy-lever-and-cascade` Steps 1-3 (v0.1 merge with sk08) |
| sk08 strategic-cascade-scenario-planning | `strategy-lever-and-cascade` Steps 4-8 (v0.1 merge with sk07) |
| sk09 multi-perspective-cld-wise-policy | `cld-overlay` (R3-2 split outward, v0.4) |
| sk10 mental-models-harmony-leadership-energy | `team-mental-model` (R3-2 split inward, v0.4) |
| sk11 stock-flow-translation | `simulation-modeling` Stage 1 (v0.1 merge with sk12) |
| sk12 models-for-learning-not-answers | `simulation-modeling` Stage 2 (v0.1 merge with sk11) |
| sk13 innovaction-martian-test | `strategy-lever-and-cascade` Step 5 (absorb, v0.6) |
| sk14 manager-personality-quadrant | `manager-personality-quadrant` (kept with strengthened Boundary, v0.6) |

**14 → 7 functional skills + 1 router**. Zero content loss; all 14 original skill bodies are recoverable from the consolidated locations.

## Coverage-rate estimate

Quantifying is rough, but for the book's **methodological content** (not narrative / historical / illustrative material):

| Layer | Coverage |
|---|---|
| **Methods + procedures** (CLD craft, R/B classification, fuzzy elevation, limits-to-growth, V/T/A, strategy, multi-perspective, mental-models, scenario perturbation) | **~95%** (only Ch 11 Gaia framing missing) |
| **Worked cases** (24 retained / 27 total per VERIFIED.md) | **~89%** (3 dropped were context-of-context or biographical) |
| **Quantitative simulation** (Ch 12-13 ithink walkthroughs) | **~30%** (concepts in `simulation-modeling`, but no executable companion) |
| **Manager-personality / facilitation framing** (Ch 14 + scattered) | **~60%** (2×2 retained in sk14 but loosely-evidenced; v0.6 strengthening Graduate-beyond routes covers modern science via external pointers) |
| **Gaia / planetary-scale** (Ch 11) | **~10%** (constrained-R-loop pattern preserved abstractly; specific framing cut) |

**Aggregate**: ~85% of book methodology + ~70% of book illustrative material.

## v0.7+ implications

Based on this audit, the highest-ROI gap closures are:

1. **Python stock-flow simulator companion** for `simulation-modeling` — closes Ch 12-13 quantitative gap, the single largest scope reduction. Already in v0.5+ deferred backlog.
2. **Ch 2-3 pre-CLD failure comparison case** as new Case 11 (cld-craft) — pedagogical scaffolding for "why use a CLD at all" that the current plugin assumes
3. **Platform-economy R-loop case bundle** — extending v0.5 Case B5 to cover network effects, winner-take-most, two-sided markets; modern Sherwood-blind-spot fix
4. **Falsifiability protocol** — propose Stage-1.5-equivalent verification rubric for CLDs (Sherwood doesn't have one; plugin could improve on the book here)

Lower-ROI but worth noting:
- **2008 cross-firm contagion case bundle** — niche but periodically requested
- **Behavioral econ biases bundle** — would require new skill, not just case extension
- **Modern facilitation companion** — async-distributed workshop adaptation; specifically called out in `team-mental-model` Boundary as a known blind spot

NOT recommended for re-introduction:
- **Ch 11 Gaia framing** — Stage-0 user cut still defensible; reusable pattern is preserved
- **c13 / c16 / c22 dropped cases** — Stage-1.5 filter was correct (biographical / context-of-context / emergence-abstract)

## Cross-reference summary

- `systems-thinking-toolkit/references/BOOK_OVERVIEW.md` — Stage 0 thesis + 14-item skill-distillable list + Critical phase
- `systems-thinking-toolkit/references/INDEX-original.md` — Stage 3 14-skill atomic map (pre-v0.1 merge)
- `systems-thinking-toolkit/references/VERIFIED.md` — Stage 1.5 verification record + rejection logs
- `systems-thinking-toolkit/ROADMAP.md` — Current backlog; v0.7+ candidates carry several gap-closure items from this audit
- `docs/superpowers/audits/2026-05-13-systems-thinking-toolkit-dogfood.md` — Dogfood audit (different methodology — tests how the plugin works in practice; this doc tests what content the plugin contains vs source)
