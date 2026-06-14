# DESIGN.md schema reference (GUI design-system)

Reference for the GUI instantiation of the `design-system` artifact. The
`design-system` skill emits a `DESIGN.md` following Google's open,
Apache-2.0-licensed `DESIGN.md` format — the **visual system** for a product.

> **Grounding.** The `DESIGN.md` format (Google Labs, open-sourced ~2026-04, reported
> Apache-2.0) and its lint CLI (reported as `npx @google/design.md`) are documented from
> secondary sources, not a frozen in-repo copy of the spec. **Verify the format's current
> shape, exact license, and the exact lint package/command against the authoritative Google
> `DESIGN.md` spec at generation time** before relying on any of them.

> **Scope — visual system only.** `DESIGN.md` documents the product's
> *visual* design system: brand, color, type, spacing, elevation, shape,
> and component tokens. It **does NOT** address flows, screens, navigation,
> or interaction. Those live in **`ui-flows.md`** (the `interaction-flows`
> skill). Do not put user flows, screen inventories, or render-variant
> tables in `DESIGN.md`.

> **Token keys are the Google-spec shape.** The 8 sections below are the
> canonical, stable structure. The YAML token *keys* listed per section
> follow the Google `DESIGN.md` spec shape, but **confirm the exact keys
> against the authoritative spec at generation time** (fetch the current
> Google `DESIGN.md` spec) — the ecosystem is young and keys may shift.

> **One per product.** `DESIGN.md` is product-level (the design *system*),
> not per-feature. There is exactly one `DESIGN.md` per product; per-feature
> interaction design goes in `ui-flows.md`.

## Lint + accessibility

- **Lint:** the emitted `DESIGN.md` is lint-able via `npx @google/design.md`.
  Run the lint as a self-verification step before declaring the artifact done.
- **WCAG-AA contrast:** color tokens MUST meet the **WCAG-AA** contrast
  requirement — body text ≥ 4.5:1, large text ≥ 3:1, against their intended
  background/foreground pairings. The lint surfaces contrast violations;
  treat an AA failure as a blocker, not a nit.

## The 8 canonical sections (in order)

The artifact MUST contain these eight `##` sections, **in this order**. Each
section carries a short prose rationale plus a YAML token block.

## Overview / Brand

Product identity and the design system's intent — voice, personality, and
the high-level brand direction the visual tokens express.

Expected YAML frontmatter / token keys (confirm against the spec):

- `name` — product / system name
- `description` — one-line design-system intent
- `brand_voice` — adjectives describing personality (e.g. calm, precise)
- `theme` — `light` / `dark` / `system`

## Colors

The color palette as semantic tokens, not raw hex scattered through prose.

Expected token keys (confirm against the spec):

- `primary`
- `secondary`
- `accent`
- `background`
- `foreground`
- `destructive`
- `muted`

Each token is a color value (hex / oklch / CSS variable). Every
foreground/background pairing MUST satisfy WCAG-AA contrast (see above).

## Typography

The type system — font families, the modular scale, and the weight ramp.

Expected token keys (confirm against the spec):

- `font_family` — base / heading / mono font stacks
- `scale` — the type scale (e.g. ratio or explicit step sizes)
- `weights` — the weight ramp (e.g. regular / medium / bold)
- `line_height` — base leading
- `letter_spacing` — tracking, where it deviates from default

## Layout

Spacing, container width, and grid — the spatial skeleton.

Expected token keys (confirm against the spec):

- `spacing` — the spacing scale (e.g. base unit + steps)
- `max_width` — content container max width
- `grid` — column count / gutter
- `breakpoints` — responsive breakpoints

## Elevation & Depth

The elevation system — shadows and layering used to express depth and
stacking order.

Expected token keys (confirm against the spec):

- `shadows` — the shadow ramp (e.g. sm / md / lg / xl)
- `z_index` — named stacking layers (e.g. base / overlay / modal / toast)
- `surface` — surface tints per elevation level

## Shapes

Corner radii and border treatment — the shape language of components.

Expected token keys (confirm against the spec):

- `radius` — the radius scale (e.g. none / sm / md / lg / full)
- `border_width` — border weight tokens
- `border_style` — default border style where it matters

## Components

Component-level token defaults — the visual contract individual components
inherit from the system (buttons, inputs, cards, etc.). This section maps
the global tokens above onto named component slots; it does **not** describe
component *behavior* or *flows* (those are out of scope — see the scope note).

Expected token keys (confirm against the spec):

- `button` — variants (primary / secondary / destructive) and their token bindings
- `input` — field styling tokens
- `card` — surface / radius / elevation bindings
- `states` — visual states (hover / focus / active / disabled) as token deltas

> Note: `states` here is **presentational** (hover/focus/disabled styling).
> The behavioral lifecycle (empty / loading / error / success domain states)
> belongs to `ui-flows.md` + `spec-expansion`, not to `DESIGN.md`.

## Do's & Don'ts

Usage guardrails — the prose rules that keep the system coherent when applied.
Pairs of recommended / discouraged usage (e.g. "DO use `accent` sparingly for
single primary actions; DON'T tint large surfaces with `accent`").

Expected token keys (confirm against the spec):

- `dos` — list of recommended-usage rules
- `donts` — list of discouraged-usage rules

## Generation checklist

When emitting `DESIGN.md`, the `design-system` skill MUST:

1. Confirm the exact YAML token keys against the authoritative Google
   `DESIGN.md` spec at generation time.
2. Emit all 8 `##` sections in the order above.
3. Populate each section's YAML token block.
4. Verify every color pairing meets WCAG-AA contrast.
5. Run `npx @google/design.md` lint and resolve violations before declaring done.
6. Keep flows / screens / navigation **out** — those go in `ui-flows.md`.
