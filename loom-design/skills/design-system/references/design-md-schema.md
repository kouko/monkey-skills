# DESIGN.md schema reference (GUI design-system)

Reference for the GUI instantiation of the `design-system` artifact. The
`design-system` skill emits a `DESIGN.md` following Google's open,
Apache-2.0-licensed `DESIGN.md` format — the **visual system** for a product.

> **Grounding.** The `DESIGN.md` format (Google Labs, open-sourced ~2026-04, reported
> Apache-2.0) and its lint CLI (reported as `npx @google/design.md`) are documented from
> secondary sources, not a frozen in-repo copy of the spec. **Verify the format's current
> shape, exact license, and the exact lint package/command against the authoritative Google
> `DESIGN.md` spec at generation time** before relying on any of them. The frozen key sets
> this reference checks against (`design_md_spec_keys.py`), and the
> unrecognized-component-property-gets-a-warning behaviour this reference cites
> under Components below (the spec's Consumer Behavior for Unknown Content),
> were both verified against
> `@google/design.md` version `0.4.0` on 2026-08-10.

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

The artifact MUST contain these eight `##` sections, **in this order**. Five
of the eight carry a YAML token block, one per spec token group — `colors`
(Colors), `typography` (Typography), `rounded` (Shapes), `spacing` (Layout),
`components` (Components). The remaining three (Overview / Brand, Elevation
& Depth, Do's & Don'ts) are prose.

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
  **Mood is INHERITED, not invented.** `PRINCIPLES.md` pins **3-5 tone & manner
  adjectives** in its **`## Anchors`** section (the *primary visual anchor*);
  those adjectives ARE this design system's **governing mood** — **inherit**
  them verbatim into `brand_voice` and **do not re-derive** a mood of your own.
  A visual concept that fights the adjectives is a defect, not a style choice.
  **Fallback — when there is no `## Anchors` tone & manner row** (an older
  `PRINCIPLES.md`): derive the mood from `docs/loom/PURPOSE.md` + Product Principles,
  exactly as before — **and say so explicitly** to the user ("no tone & manner
  anchor found; mood derived here, ungoverned upstream"). **Never silently
  invent** a mood while presenting it as inherited.
- **Generative visual principles** — the small set of *canonical* visual-design
  principles this concept leans on, each with one line on how it shows up here.
  Draw from the established canon — **hierarchy, contrast, balance, rhythm /
  repetition, alignment, proximity, white space, gestalt grouping** — and pick
  the **3-5 that express this concept**, not all of them generically. They are
  *generative*: they justify the downstream token choices (e.g. "hierarchy via
  type-scale jumps, not color" → drives the Typography scale + a restrained
  palette).

**Derivation contract:** every token in Colors / Typography / Layout /
Shapes / Components MUST be derivable from, and defensible against,
this concept + its principles (and the governing `PRINCIPLES.md`). A token you
cannot trace back to the concept is an arbitrary default — the exact failure the
Anti-patterns section bans. A committed concept makes most of those bans
redundant: a design that commits to "restrained editorial" does not reach for a
purple gradient on its own.

`name` / `description` / `version` / `omitted` are spec frontmatter keys
below (confirm against the spec at generation time); `brand_voice` /
`theme` are documented loom extensions, not spec keys:

- `name` — product / system name
- `description` — one-line design-system intent
- `version` — the `DESIGN.md` spec version this document targets (e.g. `0.4.0`; confirm exact semantics against the spec)
- `omitted` — token groups intentionally left out of this document (spec meta key; confirm exact semantics against the spec)
- `brand_voice` — adjectives describing personality / mood (e.g. calm, precise) — **loom extension: `export` does not carry this token.**
- `theme` — `light` / `dark` / `system` — **loom extension: `export` does not carry this token.**

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
- `surface` — surface tint per elevation level (relocated from Elevation & Depth; `surface` is a spec-recommended color token name, not an extension)

Each token is a color value (hex / oklch / CSS variable). Every
foreground/background pairing MUST satisfy WCAG-AA contrast (see above).

## Typography

The type system — a set of **named typography levels**, each a nested
mapping of properties (not a flat list of scale/weight/family keys). A real
product's `DESIGN.md` typically names **9-15 levels** spanning display,
headline, title, body, and label roles at multiple sizes (e.g.
`display-lg`, `headline-lg`/`md`/`sm`, `title-lg`/`md`/`sm`,
`body-lg`/`md`/`sm`, `label-lg`/`md`/`sm`) — this reference shows 3
representative levels; extend the pattern to the full ramp when emitting.

Level names are open — pick names that fit the product's voice. Each
level's properties are drawn only from this closed set (confirm against
the spec):

- `fontFamily` — base / heading / mono font stack for this level
- `fontSize`
- `fontWeight`
- `lineHeight`
- `letterSpacing` — tracking, where it deviates from default
- `fontFeature` — OpenType feature settings, where used
- `fontVariation` — variable-font axis settings, where used

```yaml
typography:
  headline-lg:
    fontFamily: "Fraktion Mono, monospace"
    fontSize: "32px"
    fontWeight: 600
    lineHeight: 1.2
  body-md:
    fontFamily: "Fraktion Sans, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0.01em"
  label-sm:
    fontFamily: "Fraktion Sans, sans-serif"
    fontSize: "12px"
    fontWeight: 500
    lineHeight: 1.4
    letterSpacing: "0.02em"
```

## Layout

The `spacing` token group — the spatial skeleton. Container width, grid, and
breakpoints are entries nested under `spacing`, not separate token groups of
their own.

Expected keys (confirm against the spec):

- `spacing` — the spacing scale (e.g. base unit + steps), nesting:
  - `max_width` — content container max width
  - `grid` — column count / gutter
  - `breakpoints` — responsive breakpoints

## Elevation & Depth

The elevation system — shadows and layering used to express depth and
stacking order. `elevation` is not one of the spec's five token groups; both
keys below are documented loom extensions — plain prose, not YAML tokens,
listed here for reference:

- `shadows` — the shadow ramp (e.g. sm / md / lg / xl) — **loom extension: `export` does not carry this token.**
- `z_index` — named stacking layers (e.g. base / overlay / modal / toast) — **loom extension: `export` does not carry this token.**

This section carries no fenced YAML block.

## Shapes

Corner radii and border treatment — the shape language of components.

`rounded` is the spec key below (confirm against the spec at generation
time); `border_width` / `border_style` are documented loom extensions, not
spec keys:

- `rounded` — the corner-radius scale (e.g. none / sm / md / lg / full). Token key is `rounded` per the Google DESIGN.md spec (not `radius`).
- `border_width` — border weight tokens — **loom extension: `export` does not carry this token.**
- `border_style` — default border style where it matters — **loom extension: `export` does not carry this token.**

## Components

Component-level token defaults — the visual contract individual components
inherit from the system (buttons, inputs, cards, etc.). This section maps
the global tokens above onto named component slots; it does **not** describe
component *behavior* or *flows* (those are out of scope — see the scope note).

Component names (`button`, `input`, `card`, …) are open, matching
Typography's open level-name position. Each component's properties are
drawn from this recognised set — the spec accepts an unrecognized
component property with a warning rather than rejecting it, so this list
guides, but does not gate, what a property key may be:

- `backgroundColor` — fill color, typically a `{colors.*}` reference
- `textColor` — foreground/text color, typically a `{colors.*}` reference
- `typography` — which typography level the component's text uses,
  typically a `{typography.*}` reference
- `rounded` — corner-radius token, typically a `{rounded.*}` reference
- `padding` — internal spacing (CSS shorthand or per-side)
- `size` — named size variant (e.g. `sm` / `md` / `lg`), where the
  component has one
- `height` — fixed height, where applicable
- `width` — fixed width, where applicable

**`{token.reference}` syntax** — a component property can point at another
token group's value instead of repeating a literal, e.g.
`backgroundColor: "{colors.primary}"` means "resolve to whatever
`colors.primary` currently is," not the literal string. Prefer references
over duplicated literals so a palette or type-scale change propagates.

**Variants live under related keys, not a nested map.** A component's
stylistic variants (primary / secondary / destructive) and its visual
states (hover / focus / active / disabled) are each their own top-level
entry named `<component>-<variant>` (and `<component>-<variant>-<state>`
for a variant's state) — e.g. `button-primary` and `button-primary-hover`
are separate entries, each carrying only the properties that differ from
the base component, **not** a `states` sub-key nested under `button`. This
is **presentational** styling (hover/focus/disabled token deltas); the
behavioral lifecycle (empty / loading / error / success domain states)
still belongs to `ui-flows.md` + `spec-expansion`, not to `DESIGN.md`.

```yaml
components:
  button:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.background}"
    typography: "{typography.label-lg}"
    rounded: "{rounded.md}"
    padding: "12px 20px"
    height: "40px"
  button-primary:
    backgroundColor: "{colors.primary}"
  button-primary-hover:
    backgroundColor: "{colors.primaryHover}"
  input:
    backgroundColor: "{colors.background}"
    textColor: "{colors.foreground}"
    typography: "{typography.body-md}"
    rounded: "{rounded.sm}"
    padding: "8px 12px"
    size: "md"
  card:
    backgroundColor: "{colors.background}"
    rounded: "{rounded.lg}"
    padding: "24px"
    width: "100%"
```

## Do's & Don'ts

Usage guardrails — plain prose, not YAML tokens, matching the spec's own
Do's-and-Don'ts example (a bullet list). Pairs of recommended / discouraged
usage (e.g. "DO use `accent` sparingly for single primary actions; DON'T
tint large surfaces with `accent`") under two prose lists:

- `dos` — recommended-usage rules, as prose bullets
- `donts` — discouraged-usage rules, as prose bullets

This section carries no fenced YAML block.

## Generation checklist

When emitting `DESIGN.md`, the `design-system` skill MUST:

1. Confirm the exact YAML token keys against the authoritative Google
   `DESIGN.md` spec at generation time.
2. **Commit the visual concept first** (Overview / Brand: an art-direction idea
   + the 3-5 generative visual principles, per the *Derivation contract*), then
   emit all 8 `##` sections in the order above.
3. Populate the YAML token block for the five token-group sections —
   `colors`, `typography`, `rounded`, `spacing`, `components` — and write
   prose for the rest.
4. Verify every color pairing meets WCAG-AA contrast.
5. Run `npx @google/design.md` lint. A **failure** (e.g. a WCAG-AA contrast
   violation) is a blocker — resolve it before declaring done. A **warning**
   on a component property outside `## Components`'s recognised list is
   expected, and legitimate, when that property is a deliberately-chosen
   extension: the spec accepts an unrecognized component property with a
   warning rather than rejecting it (see `## Components`), so this step
   does not require resolving that warning away.
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
