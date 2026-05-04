---
adr: 0002
title: Strict Skill Self-Containment for Lens Cross-skill Strategy
status: accepted
date: 2026-05-04
deciders: kouko
related: design-proposal.md §5
---

# ADR-0002: Strict Skill Self-Containment

## Status

Accepted (2026-05-04, v0.1.0)

## Context

`deconstruct-toolkit` skills share a 6-lens analytical library (Cialdini / Toulmin / Lakoff / Brignull / Bhatia / Nielsen-Norman). The same lens content appears across multiple skills:

| Lens | artifact | argument | assumption | future product | future pricing |
|---|---|---|---|---|---|
| Toulmin | ✓ | ✓ | ✓ | | |
| Cialdini 7 | ✓ | | | ✓ | ✓ |
| Lakoff | ✓ | ✓ | ✓ | ✓ | |
| Brignull | ✓ | | | ✓ | ✓ |
| Bhatia | ✓ | ✓ | | | |
| Nielsen-Norman | ✓ | | | ✓ | |

Three approaches were evaluated:

1. **SSOT-and-functional-copy** (PR #159 cross-plugin pattern) — plugin-level `docs/lenses/*.md` as Single Source of Truth, each skill's `references/` is a functional copy with sync header
2. **Cross-skill path reference** — skills reference `../../docs/lenses/*` via relative path
3. **Strict skill self-containment** — each skill ships its own `references/lens-*.md` with no plugin-level shared SoT

## Decision

Adopt **Strict skill self-containment** (Option 3).

### Rule

- Each skill is fully self-contained per Anthropic's official skill convention
- Each skill's `references/lens-*.md` is authored independently
- No `docs/lenses/` plugin-level SoT directory
- No cross-skill imports or shared paths
- Lens content **may differ** across skills as long as both remain primary-source-faithful

## Rationale

Anthropic's official Agent Skills documentation emphasizes:

- Each skill is a self-contained unit of progressive disclosure
- Skills are independently loadable
- Skill consumers (e.g., `dev-workflow:skill-creator-advance`) load one skill directory at a time

Plugin-level SoT erodes this principle:

1. Skill consumers loading just `artifact-deconstruct/` would not see `docs/lenses/`
2. Cross-plugin SSOT (PR #159) is materially different — there each consumer is in a different plugin and there is no in-plugin alternative
3. Within one plugin, allowing skills to reference plugin-level resources blurs the skill-as-unit boundary
4. If a `dev-workflow:skill-creator-advance` audit reads `artifact-deconstruct` standalone, references to plugin-level lens content become broken pointers

The self-containment cost (up to 5x duplication for high-reuse lenses at v1.0) is accepted in exchange for full Anthropic compliance.

## Consequences

### Positive

- Each skill is independently loadable, complete on its own
- No CI complexity around SoT-vs-copy drift detection
- Skills can specialize lens operationalization without shared-file constraint (e.g., `lens-persuasion` in `artifact-deconstruct` may emphasize landing-page examples, while in future `product-deconstruct` it may emphasize SaaS retention examples — both faithful to Cialdini, both legitimate)

### Negative

- Up to 5x duplication for high-reuse lenses (Cialdini, Lakoff, Toulmin) at v1.0
- Manual sync discipline required when primary sources update (e.g., Cialdini new edition)
- Risk of slow drift between same-source lenses across skills

### Mitigation (drift control without violating self-containment)

1. **Version-locked primary-source anchor at top of every lens file**

    Every `references/lens-*.md` opens with version-locked citation:

    > Source: Cialdini, *Influence: The Psychology of Persuasion*, expanded ed. (Harper Business, 2021). Ch 3 pp 84–98.

    This locks the primary-source version. Anyone editing must respect the same source.

2. **Different operationalizations are allowed and expected**

    Lens files do **not** need to be byte-identical across skills. They need to be **primary-source-faithful**. A `lens-persuasion` operationalized for landing-page analysis may differ from one operationalized for pricing-page analysis — both are correct, both cite Cialdini 2021.

3. **Quarterly skill audit** (folds into existing `dev-workflow:quarterly-audit-runbook.md`)

    When 2+ skills cite the same primary source, audit confirms:
    - Version consistency (all citing same edition)
    - No contradictions in core method
    - Reasonable specialization (operationalization differences justified, not accidental)

4. **Same-PR conscientiousness rule**

    When a PR touches a lens that lives in multiple skills, the PR description must list all instances and either:
    - Justify why only one is changed (e.g., `artifact-deconstruct` got a new example but the underlying method didn't change)
    - Or update all consistently (e.g., Cialdini new edition → all `lens-persuasion` instances updated in same PR)

## Alternatives Considered

### Option 1 — SSOT-and-functional-copy

Rejected because:

- Erodes skill self-containment principle even with functional copies (the SoT pointer is itself a cross-skill dependency)
- CI complexity (lint to detect SoT-copy drift) introduces tooling friction
- Cross-plugin SSOT precedent (PR #159) does not apply intra-plugin

### Option 2 — Cross-skill path reference

Rejected because:

- Hard violation of skill self-containment
- Breaks `skill-judge` and `skill-creator-advance` audits that load skills individually
- Violates monkey-skills CLAUDE.md skill-as-unit principle

## References

- design-proposal.md §5 (Lens Cross-skill Strategy)
- Anthropic Agent Skills documentation (skill self-containment)
- monkey-skills CLAUDE.md (subfolder structure rules)
- PR #159 SSOT-and-functional-copy precedent (rejected for intra-plugin use here)
- `dev-workflow:quarterly-audit-runbook.md` (drift mitigation hook)
