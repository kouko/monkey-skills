# Standard: 6-verdict triage rubric

## Statement

The triage skill returns exactly **one verdict** from a fixed rubric per
mode. The rubric is discrete — no "kind of fits". Refusing to issue a
clean verdict is the documented failure mode (4DX defaults to install →
wastes attention). When in doubt, the default is NOT-APPLICABLE.

### Solo mode (personal-mode.md)

| Verdict | Trigger | Hand-off |
|---|---|---|
| **APPLICABLE** | All gates passed: behavioral-change goal + no anti-pattern + time-sovereignty + matched-set commitment | `4dx-meta-whirlwind-triage` → `4dx-d1-wig-formulation` |
| **stroke-of-the-pen** | Single decision / purchase / hire / rule change suffices | Pull the lever; 4DX is ceremony |
| **whirlwind-handleable** | Existing routine working better suffices | GTD / time-blocking |
| **habit-formation** | "Do tiny thing X every day" (floss / meditate) | Atomic-habits / habit-stacking (Clear) |
| **portfolio-bet** | Multiple bets, unsure which pays off | OKR / lean experimentation (kill criteria 4DX lacks) |
| **emergency-role** | Reactive role where whirlwind IS strategic value (ER, on-call SRE) | Tighten reactive-quality metrics; 4DX inverts wrong |
| **creative-output** | Pure creative work, subjective quality (novelist, painter) | Constraint methods; Goodhart corrupts lead measures |
| **no-time-sovereignty** | <20% weekly hours under user's control | Fix schedule problem upstream first |

(8 redirect categories + APPLICABLE; "6-verdict" name groups emergency
+ creative + the time-sovereignty hard-gate as the discrete decision
branches in source skill. Any redirect is valid terminal output.)

### Team-leader mode (team-mode.md)

| Verdict | Trigger | Hand-off |
|---|---|---|
| **TEAM-APPLICABLE** | All gates passed including change-readiness preconditions | `4dx-meta-team-leader-onboarding` → `4dx-d1-wig-formulation` |
| **stroke-of-the-pen** | Leader's authority delivers outcome | Sign the contract / change the rule |
| **whirlwind-handleable** | Team's existing work + sharper execution suffices | Optimize existing flow |
| **wrong-team-shape (size)** | Team <3 or >12 | Split / consolidate to 3-12 |
| **wrong-team-shape (firefighting)** | Reactive primary purpose (ER, NOC, frontline support) | Tighten reactive-quality metrics |
| **no-time-authority** | Leader cannot carve out ~20% protected WIG time | Fix demand-protection upstream |
| **single-shot-project** | Fixed end-state + known plan | Project management (PMI / Agile / Gantt) |
| **mission-misaligned** | WIG conflicts with mission/vision (P-45 hard rule) | Pick a different WIG |
| **TEAM-NOT-YET-READY** | Goal-shape + team-shape clear but change-readiness fails (Kotter / Galbraith / Schein) | Fix urgency / incentives / assumption layer first |

## Source

Original to this skill, derived from book Ch 1 + Ch 6 triage logic plus
author-warned failure modes (CE-06 / CE-25 / CE-26 / CE-27 / CE-30 /
CE-31). Solo anti-patterns extend the three-bucket carve to personal
scale (book is dominant-leader-POV). Team-shape gates derived from book
practice (3-12 band, Strategy Map, P-45, F-28). TEAM-NOT-YET-READY
layers Kotter / Galbraith / Schein on top — citations in
`../references/industry-grounding.md`.

## Why it matters

Discrete-verdict discipline is the load-bearing mechanism. Without it,
the skill reverts to "4DX-friendly counseling" — sympathetic exploration
ending in installation regardless of fit. The rubric forces commitment
to a single classification, which forces the user to recognize misfit.

Asymmetry: APPLICABLE has high cost if wrong (quarter spent on misfit
methodology); redirect has low cost if wrong (user re-triages). Default
skews toward redirect, deliberately.

## Application across modes

| Mode | How this rubric applies |
|---|---|
| **Solo** | All 8 solo verdicts available. Steps 2-6 in protocol map 1:1 to redirects; Step 7 issues APPLICABLE if all gates pass. Step 4 anti-pattern screen can short-circuit habit / portfolio / emergency / creative. |
| **Team-leader** | All 9 team verdicts. Steps 2-8 map to redirects; Step 9 issues TEAM-APPLICABLE. Two redirects share wrong-team-shape category — surface which gate failed in verdict text. TEAM-NOT-YET-READY reserved for Step 7 change-readiness failures, distinct from mission-misaligned (goal-shape, not readiness). |
| **Member** | Not applicable — members inherit WIG, do not triage methodology fit. SKILL.md routes member queries out before this rubric is consulted. |

Same rubric **structure** across modes (discrete verdict + hand-off);
different **labels** (APPLICABLE vs TEAM-APPLICABLE; solo anti-patterns
vs team-shape gates). No protocol may invent a new category mid-session.
