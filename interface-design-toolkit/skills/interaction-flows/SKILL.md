---
name: interaction-flows
description: Generate a ui-flows.md interaction-flow artifact for a product feature or change — modality-aware (GUI screens / TUI panels+keys / CLI commands+output). Maps the screen/panel/command inventory, navigation, user flows, transitions, entry/exit points, and information density across 7 UX dimensions, governed by the product's PRINCIPLES.md. Emits Mermaid flow diagrams + ASCII wireframes; the resulting ui-flows.md is the rich seed handed to spec-toolkit:spec-expansion. Key-free — runs on the host agent's own model, no API keys, no external services. Use when mapping a product's interface surface and UX flows before specing or building. 介面流程・畫面導覽・互動流程・UX 設計（GUI/TUI/CLI）。インターフェースフロー・画面遷移・UX設計・モダリティ別（GUI/TUI/CLI）。
version: 0.1.0
---

# interaction-flows

Generate a **`ui-flows.md`** — the **interaction-flow** artifact for one product
feature or change. It captures the **interface surface**: the screen / panel /
command inventory, navigation, user flows, layout, transitions, entry/exit
points, and information density — **modality-aware** across GUI, TUI, and CLI.

This is a **GENERATE** skill in the DESIGN → spec → code pipeline. It produces a
seed; it does **not** fan out the behavioral depth (state machines, edge cases,
acceptance scenarios) — that is `spec-toolkit:spec-expansion`'s job (see Seam
below). Design stops at the surface; spec owns the behavior.

## Executor model — who does what

**You (the agent running this skill) are the executor.** You supply the LLM
reasoning (modality detection, inventory enumeration, flow synthesis, layout
drafting) and any fan-out. There is no external runtime, no API key, no program
to install — the method rides on the host agent you are already in.

## Governing constraint — PRINCIPLES.md first

Before generating anything, **read the product's `PRINCIPLES.md`** (from
`product-principles-toolkit`, at
`docs/product-principles-toolkit/PRINCIPLES.md` in the consumer project). It is
the **product constitution** and **governs every design decision** here —
inventory choices, transition character, density posture, and exit-design must
stay consistent with it instead of drifting.

**If `PRINCIPLES.md` is absent, surface that loudly** — do not silently invent a
product constitution. Tell the user the design is **ungoverned** and either ask
them to run `product-principles-toolkit:product-principles` first or proceed only
with an explicit, flagged "no PRINCIPLES — design is unconstrained" caveat
recorded in the output. (Baseline Rule 12 — fail loud.)

## Procedure

### 1. Load the references and follow them

Read both bundled references and follow them as you generate — do not re-author
their rules:

- `references/ux-flow-checklist.md` — the **7 generation dimensions** (these are
  active generation prompts, not post-hoc capture questions) plus the
  **render-variant flag rule**.
- `references/ascii-ui-patterns.md` — the **ASCII layout skeletons** for the
  per-screen structure half, and the ASCII-vs-Mermaid split.

### 2. Read PRINCIPLES.md as the governing constraint

Per the section above — load `docs/product-principles-toolkit/PRINCIPLES.md`, or
surface its absence loudly.

### 3. Detect (or ask) the modality

Determine the product's interface **modality** — the artifact's whole shape
depends on it:

- **GUI** — screens + visual components; navigation between screens.
- **TUI** — panels / panes + keybindings; focus-driven movement.
- **CLI** — commands + sub-commands; command-output chaining.

If the feature spans more than one modality (e.g. a CLI tool with a TUI mode),
generate the relevant dimensions for each. If the modality is not inferable from
the feature description or PRINCIPLES.md, **ask the user** — do not guess.

### 4. Generate `ui-flows.md` covering the 7 dimensions

Walk `references/ux-flow-checklist.md` and **generate** (not merely record) each
dimension, reading each through the detected modality:

1. **Screen / panel / command inventory** — the full list of interface surfaces
   this feature introduces or touches, each **flagged** with its render variants
   (`empty / loading / error / success`) per the flag rule below.
2. **User flows (Mermaid)** — the user's path through the surfaces as a Mermaid
   diagram. **Invoke `obsidian:obsidian-mermaid-visualizer`** for the flow
   diagrams (`flowchart` for branching task paths, `stateDiagram` for mode-bound
   flows, `journey` for end-to-end journeys) — it owns canonical Mermaid syntax;
   do not re-author Mermaid rules.
3. **UI structure (ASCII layout)** — the spatial layout of each key surface as an
   ASCII skeleton per `references/ascii-ui-patterns.md` (Mermaid has no native
   wireframe primitive, so structure-within-a-screen is ASCII).
4. **Transitions** — for each move between surfaces, its character: **instant**
   (no friction) / **guided** (wizard / confirm step) / **deliberate**
   (heavyweight, gated-behind-intent). This is *feel/pacing*, not the behavioral
   guard rules spec-expansion owns.
5. **Entry points** — every way a user can *arrive* (deep link, nav item,
   sub-command, alias, keybinding, pipe) — do not assume a single front door.
6. **Exit points** — the exit from *every* surface; actively **kill dead-ends**
   (every surface must offer a way forward, back, or out).
7. **Information density + mobile flow** — the density posture of each surface
   and the small/constrained-form-factor flow (GUI mobile reflow / TUI
   narrow-terminal / CLI non-TTY-piped output).

### 5. Apply the render-variant **flag-only** rule

When you inventory a surface (dimension 1), **flag** which render variants it can
present (`empty / loading / error / success`). This is **flag-only**: name the
variants that exist — do **not** author the transition logic, guards, or the full
state machine that moves between them. Enumerating *when* and *why* a surface
moves empty → loading → error is the **domain lifecycle**, which is
`spec-toolkit:spec-expansion`'s job. **Design stops at "these variants exist";
spec owns "here is how they transition."** Doing the state-machine / edge fan-out
here would duplicate spec-toolkit — do not.

### 6. Emit `ui-flows.md` into the consumer project

Write the artifact to `docs/interface-design-toolkit/ui-flows.md` in the consumer
project (per feature / change). Structure it as one `##` section per dimension,
provenance-honest about which surfaces / flows are derived from the feature
description vs inferred from domain priors.

**`ui-flows.md` is the rich seed to `spec-toolkit:spec-expansion`.** Name this
seam in the artifact: the inventory + render-variant flags feed
spec-expansion's object model and state-machine fan-out; the user-flows +
navigation feed its journey-navigation (③c) coverage; the transitions character
informs its guard-rule lenses. This skill *writes* the seed; spec-expansion
*reads* it and does the behavioral fan-out. Keep the boundary — flag here,
fan-out there.

### 7. Validate and fix

Run the change-folder validator (repo-root-relative path
`interface-design-toolkit/scripts/validate_design_output.py <design-output-dir>`;
the skill-relative form is `scripts/validate_design_output.py`) on the emitted
directory and **fix every flagged issue** before handing off. Do not declare the
artifact done with validator failures outstanding (Rule 12).

**Note — the validator checks the *whole* change-folder.** It requires BOTH
`DESIGN.md` (from the `design-system` skill) and `ui-flows.md` (this skill)
present. Run the full validation once the change-folder is assembled — i.e.
after `design-system` has also emitted into the same `docs/interface-design-toolkit/`
directory (the `using-interface-design-toolkit` router coordinates this). A
`ui-flows.md`-only run will correctly report the missing `DESIGN.md`.

## Boundary — stops at GENERATE (the surface)

This skill **stops at the interface surface**: inventory, flows, layout,
transitions character, entry/exit, density, and the render-variant **flags**. It
does **not** author the behavioral depth — object state machines, transition
rules, edge-case fan-out, or `#### Scenario:` acceptance blocks. That belongs to
`spec-toolkit:spec-expansion`, which consumes `ui-flows.md` as its rich seed.
**Flag here, fan-out there** — doing the fan-out in this skill would duplicate
spec-toolkit and blur the DESIGN → spec boundary.

## See also

- `references/ux-flow-checklist.md` — the 7 generation dimensions + flag rule.
- `references/ascii-ui-patterns.md` — ASCII layout skeletons + the
  ASCII-vs-Mermaid split.
- `obsidian:obsidian-mermaid-visualizer` — canonical Mermaid syntax for the flow
  diagrams.
- `spec-toolkit:spec-expansion` — the downstream consumer of `ui-flows.md`; owns
  the behavioral fan-out (state machines, edge cases, scenarios).
- `product-principles-toolkit:product-principles` — produces the governing
  `PRINCIPLES.md`.
