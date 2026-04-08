# Popper's Falsifiability Skill

Turn vague claims into testable hypotheses and design tests that
could prove them wrong.

## The Five Steps

| Step | Question | Purpose |
|------|----------|---------|
| State the Claim | What exactly is the hypothesis? | Capture the claim before transforming it |
| Operationalize | How would you measure this? | Make vague claims specific and testable |
| Design Falsification Test | What evidence would prove this wrong? | Define pass/fail criteria before testing |
| Evaluate Evidence | Does existing data falsify or support? | Apply the test to available evidence |
| Verdict | Falsified, survived, or unfalsifiable? | Reach a conclusion with recommended next steps |

## Method Type

Process-driven (step-by-step hypothesis testing flow).
Unlike First Principles (decompose to truths) or Dialectics (examine trade-offs).

## Three Verdicts

| Verdict | Meaning | Next Action |
|---------|---------|-------------|
| Falsified | Evidence contradicts the hypothesis | Revise or abandon |
| Survived | Not disproven (not proven either) | Proceed with caution; design harder tests |
| Unfalsifiable | No possible evidence could disprove it | Reformulate or acknowledge as belief/value |

## Red Flags for Unfalsifiability

| Signal | Example |
|--------|---------|
| Immune to evidence | "No data could change my mind" |
| Infinitely deferrable | "We just need more data" |
| Exception-proof | "Any counter-example is a special case" |
| Unmeasurable | "It works in ways we can't observe" |

## Examples in SKILL.md

| Example | Domain | Claim | Verdict |
|---------|--------|-------|---------|
| Performance Claim | Caching | "Redis makes us faster" | Survived (p95 dropped from 350ms to 180ms) |
| Architecture Assumption | Microservices | "Microservices help us ship faster" | Unfalsifiable (confounding variables) |

## Complements

- **Assumption Mapping** (planning-team): AM identifies assumptions, Popper tests them
- **First Principles**: decomposes to ground truths; Popper tests specific claims
- **Socratic Method**: challenges thinking through dialogue; Popper structures the test

## Inspiration

Five-step falsification process based on Karl Popper's
*The Logic of Scientific Discovery* (1934) and *Conjectures and
Refutations* (1963). Adapted for guided dialogue style per
philosophers-toolkit standard.
