---
adr: 0003
title: Lens Synthesis Disclosure — Combined-Author Lens Files
status: accepted
date: 2026-05-05
deciders: kouko
related: design-proposal.md §6, ADR-0002
---

# ADR-0003: Lens Synthesis Disclosure

## Status

Accepted (2026-05-05, post v0.1.0 grounding patch)

## Context

The flagship `artifact-deconstruct` skill ships 6 lens reference files. **5 of the 6 combine 2+ primary sources into a single file**, even though most of the original authors did not co-publish or directly synthesize their own work. This is a methodological choice that affects how skill consumers should read these lenses.

| Lens file | Combined sources | Original authors co-published? |
|---|---|---|
| `lens-rhetoric.md` | Burke (1945) + Toulmin (1958) | ❌ No |
| `lens-frame.md` | Goffman (1974) + Lakoff (1980) | ❌ No |
| `lens-genre.md` | Swales (1990) + Bhatia (1993) | ✅ Yes — Bhatia's work is direct lineage of Swales |
| `lens-ux.md` | Norman (1988/2013) + Nielsen (1994/2020) | ✅ Yes — Nielsen Norman Group is co-founded |
| `lens-persuasion.md` | Cialdini (2021) + Brignull (2024) | ❌ No (Brignull cites Cialdini, but they did not co-publish) |
| `lens-semiotic.md` | Barthes (1970) only | n/a — single source |

3 of the 5 combinations are **synthetic** (Burke+Toulmin, Goffman+Lakoff, Cialdini+Brignull). 2 are **organic** (Swales+Bhatia, Norman+Nielsen).

When v0.1.0 first shipped, this synthesis was **not explicitly disclosed** to skill consumers. The lens files looked monolithic — readers might assume the combined methods were a single coherent framework as the original authors intended, when in fact 3 of them are deliberate operational composites authored by this plugin.

## Decision

**Disclose the synthesis** at the top of each combined-lens file, immediately after the primary-source citation block.

### Format

For each combined-lens reference file, add a bold-prefixed paragraph after the source citation:

> **Synthesis note**: This file combines [Author A]'s [method 1] (primary source 1) and [Author B]'s [method 2] (primary source 2). The two were not co-published. Combining them is a methodological choice by `deconstruct-toolkit` to operationalize multi-angle analysis in a single lens. Each method retains its original semantics; their *combination* in this lens is the synthesis. See [ADR-0003](../../../docs/adr/0003-lens-synthesis-disclosure.md).

### Where the disclosure does not apply

- `lens-semiotic.md` — single source (Barthes), no synthesis
- `argument-deconstruct/references/lens-toulmin.md` — single source, no synthesis
- `argument-deconstruct/references/lens-burke-pentad.md` — single source, no synthesis (deliberately split from `artifact-deconstruct`'s combined lens-rhetoric per §3.4 below)
- `assumption-surface/references/lens-symptomatic-reading.md` — single source (Althusser), no synthesis

## Rationale

### Why synthesis is acceptable

The synthetic combinations are pedagogically defensible:

1. **Burke + Toulmin**: both analyze argumentative texts; Burke surfaces motive structure (pentad), Toulmin surfaces logical structure (claim-grounds-warrant). They complement rather than contradict; combining them produces richer argument analysis than either alone.

2. **Goffman + Lakoff**: both analyze how implicit context shapes meaning. Goffman names the *social frame* (what kind of situation does this text presume), Lakoff names the *cognitive frame* (what mental structures shape the language). They operate at different levels of the same phenomenon.

3. **Cialdini + Brignull**: Cialdini catalogs *what* mechanisms persuade, Brignull catalogs *when* persuasion crosses into manipulation. Brignull's deceptive-design taxonomy is downstream of Cialdini's principles (most dark patterns weaponize a Cialdini trigger). Combining them gives ethical-position verdicts that pure-Cialdini cannot produce.

### Why disclosure is mandatory

Without the disclosure:

- A reader who already knows Burke might be confused why Toulmin is mixed in
- A reader who already knows Cialdini might think the dark patterns came from Cialdini's own work
- A future maintainer might "clean up" the lens by removing one author, not realizing it was a deliberate synthesis
- The skill consumer cannot distinguish "what these methods originally claimed" from "how this plugin operationalizes them"

The disclosure preserves intellectual honesty and lets readers consult primary sources separately if they want pure-method depth.

### Why argument-deconstruct deliberately splits Burke and Toulmin

`argument-deconstruct/references/` ships **two separate files** (`lens-toulmin.md` + `lens-burke-pentad.md`), not one combined lens. This is the inverse design choice from `artifact-deconstruct`'s combined `lens-rhetoric.md`.

Reason: `argument-deconstruct` is **argument-focused**. Toulmin gets full depth (8-pattern warrant taxonomy, common backing failures, 3-state rebuttal classification). Burke gets full depth (5 elements + 8 ratios + motive-laundering detection). Combining them in a single file would force compression that loses the depth this skill needs.

`artifact-deconstruct` is broader (6 lenses across all artifact types); its combined `lens-rhetoric.md` is intentionally lighter on each method to leave room for the other 5 lenses.

This is consistent with ADR-0002 — each skill is self-contained and may operationalize the same primary source differently. Same source, different specialization.

## Consequences

### Positive

- Skill consumers can distinguish primary methods from operational composites
- Future maintainers see the synthesis rationale before editing
- Primary-source pedagogical respect — original authors are credited for what they actually wrote, not for what this plugin built on top
- Sets precedent for v0.2+ lenses (e.g., if `pricing-decode` combines Cialdini + Ariely, same disclosure applies)

### Negative

- 3 lens files get +5 lines of disclosure boilerplate (acceptable cost)
- Reader unfamiliar with the synthesis concept may find the disclosure noisy (mitigated by clear formatting)

### Mitigation

- Disclosure is short (one paragraph) and bold-prefixed for skim
- The ADR link gives interested readers the full rationale
- Single-source lens files (`lens-semiotic`, `lens-toulmin`, `lens-burke-pentad`, `lens-symptomatic-reading`) need no disclosure — keeps noise out of files that don't need it

## Alternatives Considered

### Alternative 1: Split every combined lens into separate files

Reject. Would inflate file count from 6 to 11 lens files in `artifact-deconstruct/references/`. Lens selection (per `protocols/lens-selection.md`) operates at the combined-lens level. Splitting would force users to remember that "rhetoric" actually means "Burke + Toulmin together" — increasing cognitive load without benefit.

### Alternative 2: Leave synthesis implicit (status quo before this ADR)

Reject. Implicit synthesis is the original v0.1.0 problem. Honesty requires explicit disclosure.

### Alternative 3: One combined `synthesis.md` document instead of per-file disclosure

Reject. Per-file disclosure is read at the moment the lens is consulted; a separate `synthesis.md` requires the reader to look it up. Friction = under-reading.

## References

- ADR-0001 (naming convention)
- ADR-0002 (skill self-containment) — explains why per-skill duplication is intentional
- design-proposal.md §6 (primary-source grounding)
- docs/grounding-v0.1.0.md (research note documenting which sources were directly consulted vs cited from training memory)
