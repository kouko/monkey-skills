---
name: design-system
description: Generate a product's visual design system — colors, typography, layout, elevation, shapes, component tokens — governed by the product's PRINCIPLES.md. Modality-aware: for a GUI it emits a DESIGN.md in Google's open 8-section format (YAML tokens + prose); for a TUI / CLI it emits a lightweight conventions stub (full TUI/CLI design-system is phase-2). Use BEFORE spec / build when defining a product's look — brand voice, palette, type scale, spacing, component styling — that the frontend implements and the spec inherits. Visual system only — flows live in interaction-flows. Triggers — en: design system, visual system, design tokens, color palette, typography scale, component styling. zh-TW: 設計系統 / 視覺系統 / 設計規範 / 設計 token / 配色 / 字體排版. ja: デザインシステム / ビジュアルシステム / デザイントークン / カラーパレット / タイポグラフィ.
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
code-toolkit's frontend implementation (styling / lint) — the design system
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

Read the product's **`PRINCIPLES.md`** (from `product-principles-toolkit`, at
**`docs/product-principles-toolkit/PRINCIPLES.md`** in the consumer project) as
the **governing constraint** on the visual system. The constitution's North
Star and principles **constrain** the design — e.g. a "minimal interface"
principle constrains the palette to few colors and a restrained component set;
a "calm, low-stimulus" principle constrains accent usage and motion. Every
design choice should be defensible against a principle.

**If `PRINCIPLES.md` is absent, surface it** — do not invent a constitution.
Tell the user the design system will be ungoverned and recommend running
`product-principles-toolkit:product-principles` first; proceed only on their
say-so, noting the design is principle-ungoverned.

### Step 3 — Detect / ask the modality

Detect or **ask** the product's modality (**GUI / TUI / CLI**); default to
**GUI** when unstated. Branch on it:

- **GUI** → go to Step 4a (full 8-section `DESIGN.md`).
- **TUI / CLI** → go to Step 4b (lightweight conventions stub + phase-2 note).

### Step 4a — GUI: emit the 8-section `DESIGN.md`

Emit a **`DESIGN.md`** following the schema contract from Step 1:

1. Confirm the exact YAML token keys against the authoritative Google
   `DESIGN.md` spec at generation time.
2. Emit **all 8 `##` sections in order**, each with a short prose rationale
   plus its YAML token block (Overview / Brand → Colors → Typography → Layout →
   Elevation & Depth → Shapes → Components → Do's & Don'ts).
3. Derive the tokens from the **brand voice** and the **PRINCIPLES.md**
   constraints — not arbitrary defaults.
4. **Verify WCAG-AA contrast** for every foreground/background pairing (body
   text ≥ 4.5:1, large text ≥ 3:1). Treat an AA failure as a **blocker**.
5. Run the spec lint `npx @google/design.md` where available and resolve
   violations.

### Step 4b — TUI / CLI: lightweight conventions stub (phase-2)

The full TUI / CLI design-system is **not yet built** (phase-2). Emit a
**minimal stub** conventions doc capturing what is known — for a TUI the
terminal palette and panel layout conventions; for a CLI the output-format,
command/flag naming, and help/error style — and add a clear **phase-2 note**
that the full TUI/CLI design-system (with a validator and lint) is deferred.
Do not fake an 8-section `DESIGN.md` for a non-GUI modality.

### Step 5 — Emit into the consumer project

Emit the artifact into the consumer project under
**`docs/interface-design-toolkit/`** (the established `docs/<toolkit>/`
convention). `DESIGN.md` is **product-level — one per product** (the design
*system*), so place it at the toolkit root, not per-feature.

### Step 6 — Validate, then fix

Run the validator against the emitted design output directory and **fix any
flagged issue before declaring done**:

```
python interface-design-toolkit/scripts/validate_design_output.py <design-output-dir>
```

The relative path from this skill dir is `scripts/validate_design_output.py`.
It mechanically checks the change-folder structure (the design-system doc
present, the GUI `DESIGN.md` carrying all 8 canonical `##` sections). The
validator checks *structure*; the *quality* of the tokens (palette derived from
the brand voice, contrast actually meeting AA, choices defensible against the
principles) is your responsibility.

**Note — the validator checks the *whole* change-folder.** It requires BOTH
`DESIGN.md` (this skill) and `ui-flows.md` (the `interaction-flows` skill)
present. Run the full validation once the change-folder is assembled — after
`interaction-flows` has also emitted into the same `docs/interface-design-toolkit/`
directory (the `using-interface-design-toolkit` router coordinates this). A
`DESIGN.md`-only run will correctly report the missing `ui-flows.md`.

## Downstream — where the design system goes

- **Frontend (code-toolkit):** the `DESIGN.md` tokens side-channel directly to
  the UI implementation — colors, spacing, type scale, and component defaults
  the styling/lint reads.
- **Spec (spec-toolkit):** the design system is the *visual* surface; the
  *behavioral* fan-out (object state machines, edges, acceptance scenarios) is
  `spec-expansion`'s turf, seeded by `ui-flows.md` — not duplicated here.

This skill *writes* the visual system; it does not run TDD, write frontend
code, or design the flows — those are downstream stations that *read* it.
