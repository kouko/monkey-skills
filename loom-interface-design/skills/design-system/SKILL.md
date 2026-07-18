---
name: design-system
description: |
  Generate a product's visual design system — colors, typography, layout, component tokens — per PRINCIPLES.md. GUI → DESIGN.md (YAML tokens + prose); TUI/CLI → conventions stub. Use BEFORE spec/build to define the look. Flows → interaction-flows.
version: 0.3.0
---

# design-system

Generate a product's **visual design system** — the brand voice, color
palette, type scale, spacing, elevation, shape language, and component-token
defaults that the frontend implements and the spec inherits. This is the
**interface-design station's visual half**: it produces the **design-system
artifact** for a product, governed by the product's constitution.

The skill is **modality-aware**. The same design concerns (palette / type /
spacing / components) render differently per modality: a **GUI** has visual
tokens and screens; a **TUI** has a terminal palette and panels; a **CLI** has
output formatting and command/flag ergonomics. The MVP implements **GUI**
fully; **TUI / CLI** emit a lightweight stub plus a phase-2 note.

All output is **key-free**, **in-repo**, and **git-diffable**.

## Executor model — who does what

**You (the agent running this skill) are the executor.** You supply the LLM
reasoning (deriving the palette from the brand voice, picking a type scale,
binding component tokens, checking contrast). There is no external runtime and
no API key — the method rides the host agent you are already in. The only
deterministic tool is a stdlib validator you run at the end, plus the
spec's lint (`npx @google/design.md`) where available.

## Scope — visual system only, NOT flows

`DESIGN.md` documents the product's **visual system** only — brand, color,
type, spacing, elevation, shape, and component tokens. It does **NOT** address
user **flows**, screen/command inventory, navigation, or interaction — those
live in **`ui-flows.md`**, produced by the **`interaction-flows`** skill. Do
not put flows, screen inventories, or render-variant tables in `DESIGN.md`.

The emitted **`DESIGN.md` tokens are a side-channel** straight to
loom-code's frontend implementation (styling / lint) — the design system
the UI code reads its colors, spacing, and component defaults from.

## Procedure — modality-aware design-system generation

### Step 1 — Read the schema contract

Read **`references/design-md-schema.md`** before writing anything. It is the
authoring contract for the GUI artifact: the **8 canonical `##` sections** (in
order: Overview / Brand · Colors · Typography · Layout · Elevation & Depth ·
Shapes · Components · Do's & Don'ts), the YAML token keys per section, and the
**WCAG-AA contrast** requirement. The emitted `DESIGN.md` **MUST** follow it.
The schema also flags that the exact Google `DESIGN.md` keys and lint command
are young-ecosystem and should be **confirmed against the authoritative spec at
generation time**.

### Step 2 — Read the governing PRINCIPLES.md

Read the product's **`PRINCIPLES.md`** (from `loom-product-principles`, at
**`docs/loom/PRINCIPLES.md`** in the consumer project) as
the **governing constraint** on the visual system. The constitution's North
Star and principles **constrain** the design — e.g. a "minimal interface"
principle constrains the palette to few colors and a restrained component set;
a "calm, low-stimulus" principle constrains accent usage and motion. Every
design choice should be defensible against a principle.

**Read its `## Anchors` section — the tone & manner row is the governing
mood.** `PRINCIPLES.md` pins **3-5 tone & manner adjectives** (e.g. *calm,
precise, unhurried*) as its own version-pinned `## Anchors` row — upstream
calls them the **primary visual anchor**. Those adjectives ARE this design
system's **governing mood**: **inherit** them verbatim as the mood of the
visual concept (Step 4a) — **do not re-derive** a mood of your own, and never
contradict them. A palette, type scale, or component default that fights the
adjectives is a defect, not a style choice. This is a **read-and-honor**
instruction: read the section as prose and honor it — do not parse, grep, or
regex the row (the row's formatting is not a contract).

**Fallback — when there is no `## Anchors` tone & manner row** (an older
`PRINCIPLES.md`, written before the anchor existed): derive the mood yourself
from the North Star + Product Principles, exactly as before — **and say so
explicitly** to the user ("no tone & manner anchor found; mood derived here,
ungoverned upstream"). **Never silently invent** a mood while presenting it as
inherited.

**If `PRINCIPLES.md` is absent, surface it** — do not invent a constitution.
Tell the user the design system will be ungoverned and recommend running
`loom-product-principles:product-principles` first; proceed only on their
say-so, noting the design is principle-ungoverned.

### Step 3 — Detect / ask the modality

Detect or **ask** the product's modality (**GUI / TUI / CLI**); default to
**GUI** when unstated. Branch on it:

- **GUI** → go to Step 4a (full 8-section `DESIGN.md`).
- **TUI / CLI** → go to Step 4b (lightweight conventions stub + phase-2 note).

**Before deriving any color, type, or component token/convention whose
correct form is not derivable from `PRINCIPLES.md` or the seed, read
`references/knowledge-triage.md` and run its classification question
FIRST** — do not guess a domain convention into a token; classify, then tag
or route per that reference. Applies in both Step 4a and Step 4b.

### Step 4a — GUI: emit the 8-section `DESIGN.md`

Emit a **`DESIGN.md`** following the schema contract from Step 1:

1. Confirm the exact YAML token keys against the authoritative Google
   `DESIGN.md` spec at generation time.
2. **Run the surface-treatment candidate round** (below) — the pick is the
   generative choice the concept and the depth/shape tokens hang off.
3. **Commit the visual concept** in **Overview / Brand** — one specific
   art-direction idea plus the **3-5 generative visual principles** it leans on
   (per the schema's *Derivation contract*), with the chosen surface treatment
   named in its prose. This is the conceptual ground for
   everything below; a generic identity here is what makes output look
   "AI-generated."
4. Emit **all 8 `##` sections in order**, each with a short prose rationale
   plus its YAML token block (Overview / Brand → Colors → Typography → Layout →
   Elevation & Depth → Shapes → Components → Do's & Don'ts), then **derive every
   token from that committed concept + the `PRINCIPLES.md` constraints** — each
   token defensible against the concept, never an arbitrary default.
5. **Verify WCAG-AA contrast** for every foreground/background pairing (body
   text ≥ 4.5:1, large text ≥ 3:1). Treat an AA failure as a **blocker**.
6. Run the spec lint `npx @google/design.md` where available and resolve
   violations.

**Surface treatment — the candidate round (step 2 above, in full).** The
surface-treatment axis (skeuomorphic / flat / material-elevation / neumorphic /
glassmorphic / neubrutalist …) is a **choice over the very tokens the schema
already ships** — `surface`, `shadows`, radii and borders. This station owns
that choice; it is never an unnamed default.

- **This round is downstream of the tone & manner anchor** (Step 2): the
  inherited **3-5 tone & manner adjectives** are the governing mood and they
  **constrain which treatments are even proposable**. Run this round only with
  the anchor in hand — never before it.
- **Propose 3-5 surface-treatment candidates**, drawn from
  **`references/canon-design-surface.md`**, each with **fit/tension** notes.
  The canon is agent-facing recall insurance — a completeness audit ("did I
  miss a closer treatment?"); the user **never sees the raw list**, only the
  fitted candidates.
- **Name 1-2 considered-but-rejected candidates** and **surface them to the
  user with reasons** — the rejection list is the honesty device, not an
  internal note.
- **The user decides.** Present the candidates and let them pick;
  "**bespoke — no canon treatment fits**" is a legal **escape hatch** (a
  bespoke treatment loses the third-party anchor, so it compensates with a
  stricter written rationale against the adjectives).
- **Name and rationalize the pick in prose** in **Overview / Brand**:
  `Surface treatment: X — because <the tone & manner adjectives> +
  <constraint>`. It rides inside that existing section — **do not add a 9th
  `##` section**; the 8-section contract is frozen.
- **The pick then constrains the `## Elevation & Depth` and `## Shapes` token
  blocks** — `surface`, `shadows`, `radius` and border tokens are **derived
  from the chosen treatment**, never an arbitrary default. A flat pick with a
  deep shadow ramp is a defect.
- **Anti-costume law.** A treatment may enrich candidates but **never
  overrides a PRINCIPLES value**. Its vocabulary is inspiration; the values are
  non-negotiable — when the two collide, the treatment loses.
- **The canon's WCAG risk flag is a BLOCKER, not a note.** A flagged treatment
  (e.g. neumorphism, dark-mode surfaces, mesh-gradient backdrops) **cannot
  ship until the flag is resolved** against WCAG-AA — surface the flag when you
  propose it, and if the resolution fails contrast, the treatment is out.

### Step 4b — TUI / CLI: lightweight conventions stub (phase-2)

The full TUI / CLI design-system is **not yet built** (phase-2). Emit a
**minimal stub** conventions doc capturing what is known — for a TUI the
terminal palette and panel layout conventions; for a CLI the output-format,
command/flag naming, and help/error style — and add a clear **phase-2 note**
that the full TUI/CLI design-system (with a validator and lint) is deferred.
Do not fake an 8-section `DESIGN.md` for a non-GUI modality.

### Step 5 — Emit into the consumer project

Emit the artifact into the consumer project under
**`docs/loom/`** (the established `docs/<toolkit>/`
convention). `DESIGN.md` is **product-level — one per product** (the design
*system*), so place it at the toolkit root, not per-feature.

### Step 6 — Validate, then fix

Run the validator against the emitted design output directory and **fix any
flagged issue before declaring done**:

```
python loom-interface-design/scripts/validate_design_output.py <design-output-dir>
```

The path relative to this skill dir is `../../scripts/validate_design_output.py`
(the script ships at the plugin root's `scripts/`).
It mechanically checks the change-folder structure (the design-system doc
present, the GUI `DESIGN.md` carrying all 8 canonical `##` sections). The
validator checks *structure*; the *quality* of the tokens (palette derived from
the brand voice, contrast actually meeting AA, choices defensible against the
principles) is your responsibility.

**Note — the validator checks the *whole* change-folder.** It requires
`ui-flows.md` (the `interaction-flows` skill) in the change folder
(`docs/loom/<change-id>/`) and resolves `DESIGN.md` (this skill)
most-specific-first — change folder, then its parent: this skill's canonical
home is the product level, `docs/loom/DESIGN.md`, one per product. Run the
full validation once the change-folder is assembled — after
`interaction-flows` has emitted (the `using-loom-interface-design` router
coordinates this). A `DESIGN.md`-only run will correctly report the missing
`ui-flows.md`.

## Downstream — where the design system goes

- **Frontend implementation:** the `DESIGN.md` tokens side-channel directly to
  the UI code — colors, spacing, type scale, and component defaults the
  styling/lint reads. This seam is the frontend build itself (human / code
  level), **not** a loom-code skill — no loom-code skill reads `DESIGN.md`.
  That is a **deliberate park, not a gap** (audit 2026-07-02, reaffirming
  #456): consumer-side machinery is undecidable until a real frontend
  consumer exists. Re-trigger conditions live in the plugin README §Scope.
- **Spec (loom-spec):** the design system is the *visual* surface; the
  *behavioral* fan-out (object state machines, edges, acceptance scenarios) is
  `spec-expansion`'s turf, seeded by `ui-flows.md` — not duplicated here.

**Next station.** Once `DESIGN.md` is done, hand off to `using-loom-spec` to
expand the feature into a spec — or to `interaction-flows` first if the
product's flows haven't been mapped yet.

This skill *writes* the visual system; it does not run TDD, write frontend
code, or design the flows — those are downstream stations that *read* it.
