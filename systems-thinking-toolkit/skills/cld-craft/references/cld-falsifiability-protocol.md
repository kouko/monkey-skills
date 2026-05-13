# CLD Falsifiability Protocol — Empirical Tests for CLD Correctness

Sherwood's Rule 10 says a CLD is "finished only when stakeholders recognize it as real" — that's social validation, NOT empirical falsifiability. Stakeholder consensus and empirical truth are different things. Both can be wrong simultaneously; either can be wrong with the other right.

This protocol defines 6 falsification tests for CLDs that aim beyond facilitation into decision-grade truth claims. Mandatory for high-stakes decisions; optional but recommended for serious quantitative-modeling pipelines (`simulation-modeling`).

## When to apply (MANDATORY triggers)

- Regulatory / compliance contexts (SOX, IFRS, FDA, FAR, public policy) where the CLD informs a decision needing audited rationale
- Financial decision-grade modeling (M&A diligence, capital allocation, fund decision-making) where CLD claims monetize directly
- Litigation expert-witness contexts where causal claims will be cross-examined
- High-stakes operational decisions (clinical, safety-critical, large-N workforce decisions) where a wrong CLD imposes substantial cost

## When NOT to apply (skip the protocol)

- Early-stage facilitation / divergent brainstorming where the CLD's job is "make us think harder, surface hidden assumptions" not "be a decision rationale"
- Learning / pedagogical contexts (Sherwood's "models for learning") where social validation is fit-for-purpose
- Conversational vocabulary use (e.g., naming a vicious cycle to a colleague) where formal testability is overkill
- Workshop with non-quantitative stakeholders where the test methodology itself imposes a higher epistemic burden than the diagram bears

## The 6 falsification tests

### Test F1 — Sign falsification (per-link)

For each S/O label in the CLD, ask: **what observable data would falsify this label?**

- If you cannot point to time-series, natural experiment, or counterfactual scenario that would falsify the sign, the link is conjectural — flag with `[unfalsifiable]` and proceed with caution
- If the link is supported by historical correlation, run a regime-shift test: did the sign flip in any historical regime change? If yes, the link is regime-dependent — apply Rule 7 split-fuzzy trick (see `cld-craft` Step 5)
- Document evidence per link in the audit metadata

### Test F2 — Loop closure falsification (per-loop)

For each closed loop, ask: **can you trace ONE full cycle in observable data?**

- Pick one node in the loop; track one tick of its trajectory through every downstream node and back to itself. Do the time-series align with the predicted causal sequence?
- If the loop closes only theoretically (the closing edge has never been observed firing), flag with `[loop closure unobserved]`
- Distinguish from one-way modifier chains (per `loop-classification-protocol.md` halt rule) — these aren't loops at all

### Test F3 — Magnitude falsification (R-loop intensity)

For R-loops currently spinning, predict the per-cycle delta (rough order of magnitude):

- If observed per-cycle delta is 10× off from predicted, the loop is mis-specified (wrong nodes, wrong signs, or missing brake)
- This is the "frogs and lily-pad" calibration (Sherwood Ch 5) operationalized — the lily-pad doubles each day, so predicted growth should be observable
- Acceptable error: within 3× for R-loops; within 2× for B-loops near equilibrium

### Test F4 — Behavioral signature falsification

The behavioral-signature line (per `loop-classification-protocol.md` caption spec) makes 4 falsifiable claims:

- "deceleration toward asymptote" → predicts decreasing per-cycle delta
- "oscillation around target" → predicts alternating signs, bounded amplitude
- "monotone divergence" → predicts continuing acceleration (no asymptote)
- "stable" → predicts variation within noise band (SPC ±2σ)

If observed time-series contradicts the predicted signature for 3+ consecutive cycles, the CLD is empirically wrong — either reclassify the loops or accept that the named archetype doesn't apply

### Test F5 — Fuzzy variable proxy validation (per Rule 7 elevation)

Every elevated fuzzy variable (per `cld-craft` Step 4) should have at least ONE observable proxy:

- Cite the proxy explicitly: NPS for "Customer Trust"; eNPS or retention for "Team Morale"; intangible asset valuation for "Brand Strength"
- If you cannot name ANY proxy, the variable is unfalsifiable and the loop containing it is conjectural — mark `[no proxy]`
- The Skandia precedent (Case 5 in cld-craft cases.md) is the template: fuzzy stocks CAN have proxies even when they resist direct measurement

### Test F6 — Sign-flip regime falsification

For any link that was split via Rule 7 (split-fuzzy-variable trick), the split presupposes a regime boundary:

- Can you predict WHERE the regime boundary lies? (Concrete threshold on the cause variable below/above which sign flips)
- If yes, the split is falsifiable — observing the cause cross the threshold without the predicted sign-flip falsifies the model
- If no (the split is post-hoc rationalization with no specifiable threshold), flag with `[split is post-hoc]` — the loop classification arithmetic is suspect

## Output: falsifiability annotation

When this protocol is applied, append to the cld-craft Mermaid block's caption:

```
**Falsifiability annotations** (per cld-falsifiability-protocol.md):

- Link Trust → Referrals: F1 verified (historical regime 2020-2023 stable; positive correlation 0.7); F2 verified (loop traced in cohort data)
- Link Volume → Quality: F1 [unfalsifiable] (no historical observation of cause-side variation in this firm)
- Loop R1 spin rate: F3 within 2× of predicted (observed +3.2% / predicted +2.0%-4.0%); within tolerance
- Fuzzy variable [Team Morale]: F5 proxied by eNPS quarterly survey
- Regime split on [Customer Trust]: F6 threshold not specified — split is post-hoc, flagging
```

## Anti-patterns

- **Falsifiability theater**: declaring a CLD "falsifiable" because you can imagine an experiment, without actually defining the threshold or experiment design. Specify thresholds.
- **All-or-nothing falsification**: a CLD is rarely 100% falsifiable; it's a collection of falsifiable + conjectural + unfalsifiable claims. Annotate each claim's status, don't pass/fail the whole diagram.
- **Premature falsification**: applying this protocol during early-stage facilitation defeats the diagram's purpose (surface assumptions). Use the "When NOT to apply" section above.

## Cross-references

- Sherwood Rule 10 (`cld-craft` SKILL.md) — social validation contrast
- Sterman behavior-over-time (BoT) graphs — closely related practice for time-series visualization; pairs naturally with this protocol
- Pearl causal-inference DAGs — different framework for sign falsification; relevant for Test F1 evidence
- `loop-classification-protocol.md` halt rules — one-way modifier detection feeds Test F2
- `cld-archetypes` Step-0 magnitude rule (v0.7) — feeds Test F4 behavioral-signature falsification
- `cld-craft` Step 4 Rule 7 fuzzy elevation — feeds Test F5
- Case 5 Skandia (cld-craft cases.md) — fuzzy-stock-proxy template
- `simulation-modeling` Stage 2 sensitivity sweep (v0.2 A5) — pairs with Test F3 and F4 for quantitative falsification

## Source provenance

This protocol is a v0.8 plugin contribution NOT present in Sherwood 2002. It is the plugin's first methodological improvement over the source book — Sherwood Rule 10 ends at social validation; this protocol takes the next step toward empirical falsifiability for high-stakes CLD use.

Theoretical grounding:
- Popper falsifiability criterion (Logik der Forschung 1934)
- Sterman BoT discipline (Business Dynamics 2000, ch 4)
- Pearl-style causal evidence (The Book of Why 2018)

The protocol is craft-grade, not science-grade — it operationalizes the spirit of falsifiability for managerial CLD use without claiming to make every CLD test-grade. It catches the worst failure modes (unfalsifiable fuzzy variables, post-hoc splits, ungrounded magnitude claims, unobserved closures) without imposing infeasible burden.
