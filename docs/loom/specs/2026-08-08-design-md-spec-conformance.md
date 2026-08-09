# Brief: DESIGN.md token-shape conformance for `design-system`

Design-side on-ramp: N/A — bug fix to an existing station's reference
contract, no new product/UI surface (Axis 0 negative guard applies; the
Backlog ready check ran, see Open Questions).

Revision note (2026-08-10): scope NARROWED after reading the spec's
§"Consumer Behavior for Unknown Content" and the repo's `PHILOSOPHY.md`,
both missed in the first pass. Most of what the first draft proposed to
delete is sanctioned extension, not error. See §What This Brief No
Longer Claims.

## Problem

`design-system` is built to emit a Google-spec `DESIGN.md` — its own
description says "GUI → DESIGN.md (YAML tokens + prose)" and its Step 6
runs the authoritative lint. But the schema reference it tells the
implementer to read *before writing anything* puts loom's typography
keys in **property position**, and properties are a closed set. The
result is a typography block the spec cannot read.

Measured against `@google/design.md@0.4.0` (live CLI):

| Probe | Result |
|---|---|
| `lint` a file shaped per the reference | 30 warnings, **0 errors, exit 0** |
| `export --format json-tailwind` | `fontFamily: {}`, `fontSize: {}` — typography **empty** |
| `validate_design_output.py` on the same file | `OK … conforms` |

Nothing anywhere turns red. The job: when `design-system` runs for real,
its typography decisions must survive into the toolchain instead of
evaporating silently.

## Users

kouko, and any agent dispatched to run `design-system`. The primary
consumer is an agent *reading* the emitted `DESIGN.md` as context —
`PHILOSOPHY.md` is explicit that "token values serve as context and are
not rendering instructions". The secondary consumer is `export`
(Tailwind v3/v4, W3C DTCG), which is where the malformed typography is
observably lost. The reference is read by an implementer with no
independent knowledge of the spec; its wording is the whole contract.

## Smallest End State

`design-md-schema.md` puts every key in a position the spec recognises,
and one mechanical check fails when that stops being true.

## Current State Evidence

- **Forward** — `design-system/SKILL.md:118-124` Step 4 orders "all 8
  `##` sections in order, each with **its YAML token block**". The spec
  defines five token groups (`colors`, `typography`, `rounded`,
  `spacing`, `components`); Overview, Elevation & Depth and Do's &
  Don'ts have none — their content is prose (spec §Elevation & Depth
  ships a prose-only example).
- **Reverse** — the SSOT is external and unfrozen. `design-md-schema.md:7-11`
  states the format is "documented from secondary sources, not a frozen
  in-repo copy" and defers verification to generation time; `:20-24`
  repeats "confirm the exact keys against the authoritative spec". Both
  are prose addressed to the implementer, with no mechanical backing —
  and `rounded` at `:152` carries a correct spec citation while the
  typography block does not, so the hedge demonstrably did not hold.
- **Error** — no error path exists. `validate_design_output.py:172-177`
  registers four checks; none inspects the YAML. The authoritative lint
  reports malformed properties as **warnings** and exits 0. The spec's
  own §Consumer Behavior table says a duplicate `##` heading must
  "Error; reject the file" — probed, and v0.4.0 does **not** implement
  it (0 errors), so the document and the shipped tool already diverge.
- **Data** — the defect is confined to **property position**, which is
  closed; **name position is open** (spec §Consumer Behavior: an unknown
  typography token name such as `telemetry-data` is "Accept as valid").
  `design-md-schema.md:116-122` lists `font_family` / `scale` /
  `weights` / `line_height` / `letter_spacing` as though typography were
  a flat set of properties. The spec models it as **9–15 named levels**
  (`headline-lg`, `body-md`, `label-sm` …), each carrying `fontFamily`,
  `fontSize`, `fontWeight`, `lineHeight`, `letterSpacing`,
  `fontFeature`, `fontVariation`. Wrong case *and* wrong nesting.
  `:163-168` omits the component sub-token whitelist
  (`backgroundColor`, `textColor`, `typography`, `rounded`, `padding`,
  `size`, `height`, `width`); unknown properties there are "Accept with
  warning". The reference also never documents `{token.reference}` brace
  syntax, `version`, or `omitted`.
- **Boundary** — `brand_voice` is pinned by
  `test_design_system_skill.py:331` (`assert "brand_voice" in block`).
  This brief no longer proposes removing it (see below), so that pin
  stands; any future change to it must move in the same commit.

Evidence paths: `loom-interface-design/skills/design-system/references/design-md-schema.md`,
`loom-interface-design/skills/design-system/SKILL.md`,
`loom-interface-design/scripts/validate_design_output.py`,
`loom-interface-design/scripts/test_design_system_skill.py`,
authoritative spec dump (`npx @google/design.md@0.4.0 spec`),
`https://raw.githubusercontent.com/google-labs-code/design.md/main/PHILOSOPHY.md`.

## Decision

Fix **position**, not vocabulary. Three edits to
`design-md-schema.md`, one to `SKILL.md`, one new pin:

1. **Typography** — replace the flat property list with the spec's
   nested shape: named levels, each carrying camelCase properties from
   the closed set. Carry the spec's own sizing guidance (9–15 levels)
   and its recommended level names.
2. **Components** — document the eight-item sub-token whitelist and the
   `{token.reference}` brace syntax; note that variants live under
   related keys (`button-primary`, `button-primary-hover`).
3. **Relocate, don't delete** — `surface` is a *recommended* color token
   name, so it belongs under `colors`; `max_width` / `grid` /
   `breakpoints` belong as `spacing` entries (the spec's own example is
   `grid-columns: '5'`). Add the `version` and `omitted` meta keys.
4. **`SKILL.md:118-124`** — replace "each with its YAML token block"
   with the five-groups reality.
5. **Pin** — freeze the two closed sets (typography properties,
   component sub-tokens) as an in-repo fixture and assert the reference
   documents nothing outside them. Frozen copy + drift test, mirroring
   `loom-code/scripts/canonical/`, chosen because the format is `alpha`
   with no compatibility promise and CI must not depend on the network.

Keep `brand_voice`, `theme`, `shadows`, `z_index`, `border_width`,
`border_style` as **documented loom extensions** — the spec sanctions
arbitrary additional top-level sections (`PHILOSOPHY.md` uses `motion:`
as its own example) — but label them as such and state plainly that
`export` does not carry them. Move `dos` / `donts` to prose, matching
the spec's own Do's-and-Don'ts example, which is a bullet list.

We will NOT add token validation to `validate_design_output.py`: the
authoritative lint already owns it, and this branch's job is to stop
prescribing unreadable shapes, not to re-implement someone else's
linter.

## What This Brief No Longer Claims

The first draft proposed moving every non-spec key into prose. Probing
the live CLI showed that was wrong on four counts, each verified:

| First draft said | Verified reality |
|---|---|
| Custom section headings risk interop | `## Overview / Brand` and `## Overview` produce **byte-identical** lint findings |
| `surface` / `grid` / `max_width` must become prose | All are legal token positions; `grid-columns: '5'` is the spec's own example |
| Invented top-level groups are errors | Extensions are sanctioned; unknown *map*-shaped keys draw a `token-like-ignored` warning at worst |
| Google is silent on authoring | `PHILOSOPHY.md` (repo root, 110 lines) is authoring guidance; only `docs/` lacks it |

## What Becomes Obsolete

- The flat typography property list (`:116-122`) — replaced, not
  deprecated.
- The blanket "each section carries a YAML token block" instruction
  (`SKILL.md:118-124`, `design-md-schema.md:41-42`).
- Part of the `:20-24` prose hedge: "confirm the exact keys" becomes a
  mechanical check for the two closed sets. The grounding note at
  `:7-11` stays but gains the version verified against (`0.4.0`) and the
  date — the same convention the OPEN backlog entry
  `2026-07-10-grounding-notes-for-sibling-stations-claude-code-tools-md`
  asks for on the sibling files.

## Out of Scope

- **The mood-vs-reference hierarchy.** `PHILOSOPHY.md` argues that
  "adjectives describe a region; a specific reference describes a
  point", and that a long don't-list signals a description too vague to
  carry its own constraints. `design-system` currently makes 3–5
  inherited tone-and-manner adjectives the governing mood and ships six
  NEVER rules. That is a design judgement about the station's generative
  layer, independent of token shape, and bundling it here would mix a
  mechanical correction with a taste decision. Filed as a separate
  backlog entry.
- `interaction-flows` / `ui-flows.md` — untouched.
- Token validation inside `validate_design_output.py` (see Decision).
- Section-heading naming (proven a non-issue, see table above).
- The sibling grounding notes on `references/claude-code-tools.md`.
  That backlog entry's start condition ("next touch of loom-spec or
  loom-interface-design references/") **is** satisfied by this branch,
  but it concerns a different file and subject. Surfaced; left OPEN.

## Open Questions

- None blocking. `DIRECTION.md` `## Now` is empty and `## Next` does not
  cover this arc, so this is unbetted work taken on user request; the
  Backlog ready check surfaced no COMMITTED-NEXT item.
