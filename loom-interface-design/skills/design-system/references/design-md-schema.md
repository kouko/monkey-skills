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

Product identity **and the committed visual concept the whole system answers
to.** This section is the design system's *generative* layer — the conceptual
ground every downstream token is derived from and defensible against. A thin,
generic identity here ("clean and modern") is the root cause of generic,
"AI-generated"-looking output; a committed concept is what prevents it.

Carry, in the **prose body** of this section (the YAML keys below stay thin):

- **Visual concept (art direction)** — ONE specific, committed creative
  direction the design expresses, in a sentence or two (e.g. "editorial print
  weekly — generous measure, restrained palette, confident serif headlines" /
  "utilitarian terminal — monospace, high-density, near-zero ornament").
  Commit to a specific aesthetic; a non-committal concept yields non-committal
  tokens.
- **Mood** — the emotional target as a few adjectives (the `brand_voice` token).
- **Generative visual principles** — the small set of *canonical* visual-design
  principles this concept leans on, each with one line on how it shows up here.
  Draw from the established canon — **hierarchy, contrast, balance, rhythm /
  repetition, alignment, proximity, white space, gestalt grouping** — and pick
  the **3-5 that express this concept**, not all of them generically. They are
  *generative*: they justify the downstream token choices (e.g. "hierarchy via
  type-scale jumps, not color" → drives the Typography scale + a restrained
  palette).

**Derivation contract:** every token in Colors / Typography / Layout /
Elevation / Shapes / Components MUST be derivable from, and defensible against,
this concept + its principles (and the governing `PRINCIPLES.md`). A token you
cannot trace back to the concept is an arbitrary default — the exact failure the
Anti-patterns section bans. A committed concept makes most of those bans
redundant: a design that commits to "restrained editorial" does not reach for a
purple gradient on its own.

Expected YAML frontmatter / token keys (confirm against the spec):

- `name` — product / system name
- `description` — one-line design-system intent
- `brand_voice` — adjectives describing personality / mood (e.g. calm, precise)
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

- `rounded` — the corner-radius scale (e.g. none / sm / md / lg / full). Token key is `rounded` per the Google DESIGN.md spec (not `radius`).
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
- `card` — surface / rounded / elevation bindings
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

## Anti-patterns — NEVER ship these (the "AI-generated" tells)

Generic AI-generated UI has a recognizable signature. A designer cringes at it on
sight; the model has not stepped on these landmines, so name them explicitly. The
emitted `DESIGN.md` MUST avoid:

- **NEVER default to the AI-signature fonts** (Inter, Roboto, Open Sans, system-ui)
  *without a brand reason*. They are the overused default of generated UI and read
  as "no one chose this." Pick type that carries the brand voice; if you do use a
  ubiquitous face, say *why* in the Typography rationale.
- **NEVER use the purple/indigo → blue gradient on white.** It is *the* tell of an
  AI-generated landing page. Cliché color stories (purple-on-white, neon-on-dark
  "cyberpunk", pastel-everything) signal zero taste. Derive the palette from the
  brand voice + PRINCIPLES, not from the model's prior.
- **NEVER apply one uniform `border-radius` to everything.** Blanket rounding
  flattens visual hierarchy and is a generated-UI smell. Vary radius by component
  role (cards vs inputs vs pills); a deliberate radius scale > a single default.
- **NEVER use pure black `#000` on pure white `#fff` for body text.** The maximal
  contrast vibrates and reads cheap; use a near-black (e.g. an off-black token)
  and a near-white surface. (Still meet WCAG-AA — `#000`/`#fff` is a taste fault,
  not a contrast fault.)
- **NEVER exceed ~2–3 accent colors** or scatter unscoped accents. More colors =
  less hierarchy. One primary, one (maybe two) supporting, semantic colors for
  state — that is usually the whole budget.
- **NEVER let a token contradict a PRINCIPLES.md principle.** A "minimal,
  low-stimulus" constitution with 6 accents and heavy motion is incoherent — the
  design system answers to the constitution, not to defaults.

The test for each: would a designer say "yes, I learned that the hard way," or
"that's obvious"? Keep only the former.
