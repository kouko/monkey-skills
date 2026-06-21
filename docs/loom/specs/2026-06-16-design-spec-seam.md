# Brief — DESIGN→spec seam (P1): doc-only point-don't-copy traceability convention

**Date:** 2026-06-16
**Touches:** `spec-toolkit:spec-expansion` (consumer, SSOT owner) + `interface-design-toolkit:interaction-flows` (producer)
**Type:** doc-only (skill prose). No parser, no Python, no validator change.

## Problem

(Axis 1 — JTBD) The design→spec pipeline produces a rich `ui-flows.md` (inventory,
flows, entry/exit, density flags) and then `spec-expansion` fans out behavior from a
"sparse seed". But **spec-expansion has zero awareness that the seed can BE a
`ui-flows.md`** (`grep -ci ui-flows` = 0), and **neither skill documents how the two
connect**. So an agent moving from ui-flows to spec hits an undocumented judgment leap
with two failure modes:

- **Re-express** — copy the whole ui-flows inventory/flows into the proposal →
  duplication + drift (two sources of truth for the same surface).
- **Under-use** — ignore ui-flows structure and re-derive surface from scratch → loses
  the work the design station already did; misses surfaces.

Job story: *When I run spec-expansion right after interaction-flows on the same feature,
I want to know exactly which ui-flows sections map to which spec phases, link back to
them, and fan out only the net-new behavior — so the spec stays a single source of truth
and doesn't re-litigate the design surface.*

## Users

(Axis 2) An agent (or kouko) running `spec-toolkit:spec-expansion` on a feature that
**already has a `docs/loom/ui-flows.md`**, on the host agent, no API
key. The complementary user is the agent running `interaction-flows` who needs to know to
**structure ui-flows sections so they're addressable** (stable headings) because the
downstream links back rather than copies.

## Smallest End State

(Axis 3) **Two prose edits, mapping table lives in ONE place:**

1. **spec-expansion (consumer, SSOT owner)** — add a short subsection ("Consuming a
   `ui-flows.md` seed") that states:
   - When the seed is a `ui-flows.md`, treat its inventory / flows / entry-exit as the
     **already-specified surface** — do not re-derive or re-express it.
   - **Link back** to the named ui-flows sections from the proposal; **fan out only
     NET-NEW behavior** (object state machines, transition guard rules, edge cases,
     `#### Scenario:` blocks) — *point-don't-copy*.
   - The mapping table (SSOT):
     | ui-flows section | feeds spec-expansion |
     |---|---|
     | §inventory + render-variant flags | Phase ② OOUX object/state model |
     | §User flows + §Entry + §Exit | Phase ③c `## Journey navigation` |
     | interaction-dense surface (density flag) | `## Cross-object combinations` |

2. **interaction-flows §6 (producer)** — extend the existing seam paragraph
   (lines 118–124, which already half-names the mapping) with the **reciprocal**
   point-don't-copy note: spec-expansion links back to these sections rather than copying,
   so structure them with stable/addressable headings. One-line pointer to
   `spec-toolkit:spec-expansion` for the canonical mapping (no copied table → no drift).

**No parser. No validator change. No Python. No new files** (inline subsection, not a new
reference — the mapping is ~3 rows).

## Current State Evidence

- **Forward (producer → seam):** `interface-design-toolkit/skills/interaction-flows/SKILL.md:118-124`
  already describes the seam ("ui-flows.md is the rich seed… the inventory + render-variant
  flags feed spec-expansion's object model… user-flows + navigation feed its
  journey-navigation (③c)… transitions inform guard-rule lenses"). **Missing:** the
  point-don't-copy reciprocal + addressability note.
- **Reverse (consumer side):** `spec-toolkit/skills/spec-expansion/SKILL.md` treats input as
  a generic "sparse seed" (line 9, line 32 honesty rail #1). `grep -ci ui-flows` = **0** —
  no awareness of ui-flows as a seed type, no link-back convention. The natural insertion
  point is near the seed-adequacy pre-flight (lines 66–82) or as a new `##` subsection
  before Phase ①.
- **Boundary:** interaction-flows §"Boundary" (lines 141–149) already enforces "flag here,
  fan-out there" — the new convention reinforces this, does not contradict it.
- **Data:** the mapping is a fixed 3-row correspondence; no runtime data, no state.
- **Error:** N/A — prose convention, no failure path. If ui-flows is absent, spec-expansion
  falls back to its existing generic-seed behavior (no regression).
- **SSOT ownership:** the two skills live in **different plugins** (spec-toolkit /
  interface-design-toolkit) so they cannot share a reference file. SSOT = the mapping table
  in spec-expansion (consumer); interaction-flows points to it by `plugin:skill` name (same
  pattern as its existing "See also" pointer at SKILL.md:158).

## Decision

Build a **doc-only traceability convention** across the two skills: spec-expansion gains a
"consuming a ui-flows.md seed" subsection (link-back + net-new-only + the 3-row mapping as
SSOT); interaction-flows §6 gains the reciprocal point-don't-copy/addressability note + a
pointer. We will **NOT** build a parser (`seed_spec_from_ui_flows.py`), will **NOT** copy
the mapping table into both skills, and will **NOT** change the validator. Verification is a
**re-run of dogfood station ⑤** against `~/pipeline-dogfood/invoice-tracker/` (which already
has ui-flows.md + a spec change-folder), checking the spec proposal links back to ui-flows
sections and fans out only net-new behavior.

## Alternatives Considered

(Axis 4 — researched last session via deep-research, 2 passes; decision locked by user.)

1. **Parser / automated extraction** (`seed_spec_from_ui_flows.py`) — **REJECTED.** EN+JA
   industry treats wireframe→spec as human judgment; automated extraction backfires
   (~71.6% accuracy, fabrication, false-precision). Bitter-Lesson: design→spec is the kind
   of judgment that gets worse, not better, when you scaffold it into a parser.
2. **Status-quo manual leap** (do nothing) — **REJECTED.** The two failure modes above
   (re-express drift / under-use) are exactly what's unmanaged today.
3. **Doc-only convention** (chosen) — formalizes the implicit seam interaction-flows §6
   already gestures at, with a point-don't-copy discipline. Cheap, model-friendly, no
   maintenance debt.

## What Becomes Obsolete

(Axis 5) Nothing is deleted. interaction-flows §6's current seam paragraph is **extended**,
not replaced. This is additive doc — but it formalizes an existing implicit convention
(§6 already names the mapping), so it is not speculative YAGNI; it closes a documented gap
surfaced by the 2026-06-15 pipeline dogfood.

## Out of Scope

- A `ui-flows.md` → spec parser or any code.
- Changing `validate_spec_output.py` enforcement.
- Stable-anchor / heading-ID tooling for ui-flows (the convention asks authors to use
  addressable headings; it does not enforce them mechanically).
- P2 (#4 principles-conformance lens) — separate backlog item.

## Open Questions

- None blocking. Placement of the spec-expansion subsection (near seed-adequacy pre-flight
  vs a standalone `##`) is a writing-plans-level detail.
