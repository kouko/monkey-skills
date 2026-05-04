---
adr: 0001
title: Convention B — Mixed Naming for deconstruct-toolkit Skills
status: accepted
date: 2026-05-04
deciders: kouko
related: design-proposal.md §3
---

# ADR-0001: Convention B — Mixed Naming

## Status

Accepted (2026-05-04, v0.1.0)

## Context

`deconstruct-toolkit` ships with multiple skills that perform reverse-direction analysis on external artifacts. We need a naming convention that:

1. Signals plugin membership at a glance
2. Preserves semantic precision per skill
3. Allows future expansion without forced renames

Two candidates were evaluated:

- **Convention A — Strict suffix**: every skill named `<noun>-deconstruct` (e.g., `artifact-deconstruct`, `bias-deconstruct`)
- **Convention B — Mixed**: mainstream skills use `<noun>-deconstruct`; specialized verb skills retain their natural verb (e.g., `assumption-surface`, `frame-reveal`, `bias-audit`)

## Decision

Adopt **Convention B (Mixed)**.

### Rule

| Skill type | Pattern | Examples |
|---|---|---|
| Mainstream deconstruct skills | `<noun>-deconstruct` | `artifact-deconstruct`, `argument-deconstruct`, future `product-deconstruct` |
| Specialized verb skills | `<noun>-<verb>` | `assumption-surface`, future `frame-reveal`, future `bias-audit` |
| Router | `using-<plugin-name>` | `using-deconstruct-toolkit` |

### Two membership gates

Every new skill in this plugin **must** pass both:

1. **Verb gate** — verb belongs to the deconstruct family: `deconstruct / surface / reveal / audit / decode / expose / archaeology`
2. **Object gate** — object is an external, polished, non-code artifact (per design-proposal.md §2.1)

If a proposed skill fails either gate, it does not belong in this plugin.

## Rationale

Convention A was rejected because:

- `bias-deconstruct` is semantically wrong — bias is *exposed*, not *deconstructed*
- `assumption-deconstruct` loses the precision of `surface` (= bring up from below)
- Forcing every skill into `<noun>-deconstruct` would either degrade naming precision or exclude legitimate family members

Convention B preserves naming precision while keeping plugin membership clear via:

- Plugin name `deconstruct-toolkit` itself signals family membership at install time
- Router skill `using-deconstruct-toolkit` provides discoverability
- Description fields (per skill) reinforce the reverse-direction theme

### Precedent

This pattern is already validated in monkey-skills:

- `copywriting-toolkit` (14 skills): `copywriting-*` prefix with stage-specific names (`intake / ideation / audit / form-check`)
- `philosophers-toolkit`: skills named after philosophers with no shared verb suffix

## Consequences

### Positive

- Each skill's name reflects its semantic action precisely
- v0.2 / v0.3 expansion (`frame-reveal`, `bias-audit`, `decision-archaeology`) does not require forced renames
- Two membership gates prevent scope creep

### Negative

- New users may not immediately recognize `assumption-surface` as part of `deconstruct-toolkit` without seeing the plugin context
- Future maintenance requires verb-gate review on each new skill PR

### Mitigation

- Plugin README opening explicitly lists all sibling skills
- Each skill SKILL.md `description` field references the plugin theme
- `using-deconstruct-toolkit` decision tree includes all sibling skills

## Alternatives Considered

- **Convention A — Strict `*-deconstruct` suffix**: rejected for semantic-precision loss
- **Convention B-with-fallback**: keep Convention B but reserve right to revert in v0.3 if naming bifurcation causes confusion. Rejected as ADR softness; can always issue ADR-0003 to revise if real evidence emerges.

## References

- design-proposal.md §3 (Naming Convention)
- copywriting-toolkit precedent (14-skill mixed naming)
- philosophers-toolkit precedent (philosopher-named skills)
