---
name: interaction-flows
description: |
  Generate a ui-flows.md interaction-flow artifact — screens, navigation, user flows, state transitions, wireframes (GUI/TUI/CLI). Use when the user wants to map, design, or lay out a UI/UX flow, screen, or its states before specing or coding.
version: 0.3.0
---

# interaction-flows

Generate one feature/change's **`ui-flows.md`**: a modality-aware interface
surface covering inventory, navigation, flows, layout, transitions, entry/exit,
and information density across GUI, TUI, and CLI.

This DESIGN-stage GENERATE skill seeds `loom-design:spec-expansion`; it does not
fan out state machines, edge cases, or acceptance scenarios. Design stops at
the surface; spec owns the behavior.

**Ending gate — before you end ANY run of this skill → confirm `ui-flows.md` exists on disk and §7's validator ran, FIRST. A narrated analysis with no file written is a FAILED run, never a partial success.**

## Governing constraint — PRINCIPLES.md first

Before generating anything, read the consumer project's
`docs/loom/PRINCIPLES.md`. It governs inventory, transition character, density,
and exit design.

**If `PRINCIPLES.md` is absent, surface that loudly.** Ask the user to run
`loom-design:product-principles`, or proceed only with their explicit approval
and record `no PRINCIPLES — design is unconstrained` in the output.

## Procedure

### 1. Load the references and follow them

Read and follow these bundled references; do not re-author their rules:

- `references/ux-flow-checklist.md` — 7 active generation dimensions and the
  render-variant flag rule.
- `references/ascii-ui-patterns.md` — ASCII skeletons and the
  ASCII-vs-Mermaid split.

### 2. Read PRINCIPLES.md as the governing constraint

Load `docs/loom/PRINCIPLES.md`; apply the absent-file behavior above.

### 3. Detect (or ask) the modality

Determine the interface **modality**:

- **GUI** — screens + visual components; navigation between screens.
- **TUI** — panels / panes + keybindings; focus-driven movement.
- **CLI** — commands + sub-commands; command-output chaining.

Cover each modality a feature spans. If neither the seed nor PRINCIPLES.md makes
the modality inferable, **ask the user** — do not guess.

### 4. Generate `ui-flows.md` covering the 7 dimensions

Using `references/ux-flow-checklist.md`, generate each dimension for the
detected modality:

1. **Screen / panel / command inventory** — every introduced or touched surface,
   flagged with its `empty / loading / error / success` render variants.
2. **User flows (Mermaid)** — paths through surfaces. Invoke
   `obsidian:obsidian-mermaid-visualizer`: `flowchart` for branches,
   `stateDiagram` for mode-bound flows, and `journey` for end-to-end journeys.
3. **UI structure (ASCII layout)** — each key surface as an ASCII skeleton per
   `references/ascii-ui-patterns.md`; Mermaid is for flow, not wireframes.
4. **Transitions** — label every move **instant**, **guided**, or **deliberate**.
   Capture feel/pacing, not spec-expansion's behavioral guards.
5. **Entry points** — every arrival route (deep link, nav, sub-command, alias,
   keybinding, pipe); do not assume one front door.
6. **Exit points** — kill dead-ends: every surface needs a way forward, back,
   or out.
7. **Information density + mobile flow** — each surface's density and constrained
   form (GUI mobile reflow, TUI narrow terminal, CLI non-TTY/piped output).

**Before drafting a flow, transition, or display convention (color/sign/period)
not derivable from PRINCIPLES.md or the seed, read
`references/knowledge-triage.md` and run its classification question FIRST.**
Classify, then tag or route; never guess a domain convention.

### 5. Apply the render-variant **flag-only** rule

For each inventory item, use the **flag-only** rule: name its
`empty / loading / error / success` variants, but do not author transition
logic, guards, or the state machine. Design names which variants exist; spec
owns why and how they transition.

### 6. Emit `ui-flows.md` into the consumer project

Write the artifact to `docs/loom/<change-id>/ui-flows.md` in the consumer
project — **per feature / change, one folder per change**. `<change-id>` is
the kebab-case name of this feature/change, the **same id**
`loom-design:spec-expansion` uses for its change folder, so the design seed sits
beside the spec delta it will feed (ask the user for the change name if the
feature description does not yield an obvious one). Do **not** write to a
fixed product-level `docs/loom/ui-flows.md` — a per-feature artifact at a
fixed path means the second feature overwrites the first. (`DESIGN.md` stays
product-level at `docs/loom/` — one per product, not per change.)
Structure it as one `##` section per dimension,
provenance-honest about which surfaces / flows are derived from the feature
description vs inferred from domain priors.

**`ui-flows.md` is the rich seed to `loom-design:spec-expansion`.** Name this
seam in the artifact: the inventory + render-variant flags feed
spec-expansion's object model and state-machine fan-out; the user-flows +
navigation feed its journey-navigation (③c) coverage; the transitions character
informs its guard-rule lenses. This skill *writes* the seed; spec-expansion
*reads* it and does the behavioral fan-out. Keep the boundary — flag here,
fan-out there.

**Point-don't-copy — structure for addressability.** spec-expansion does not copy
this surface into its proposal; it **links back** to these sections and fans out only
net-new behavior. So give each `##` dimension a **stable, addressable heading** the
downstream can cite. The canonical section→phase mapping lives in
`loom-design:spec-expansion` (§"Consuming a `ui-flows.md` seed") — do not duplicate it
here; a copied table would drift.

### 7. Validate and fix

Run the change-folder validator
(`argv: ["python3", "${CLAUDE_PLUGIN_ROOT}/scripts/interface/validate_design_output.py", "<design-output-dir>"]`) on the
emitted **change folder** (`docs/loom/<change-id>/`) and **fix every flagged
issue** before handing off. Do not declare the artifact done with validator
failures outstanding (Rule 12).
Pass this argv array directly to process execution; never through a shell.

**Note — the validator checks the *whole* change-folder.** It requires
`ui-flows.md` (this skill) in the change folder and resolves `DESIGN.md`
(from the `design-system` skill) most-specific-first — the change folder
itself, then its parent (the product level, `DESIGN.md`'s canonical home).
Run the full validation once the change-folder is assembled — i.e. after
`design-system` has also emitted (the `using-loom-design` router
coordinates this). A `ui-flows.md`-only run with no `DESIGN.md` at either
level will correctly report the missing `DESIGN.md`.

## Boundary — stops at GENERATE (the surface)

This skill **stops at the interface surface**: inventory, flows, layout,
transitions character, entry/exit, density, and the render-variant **flags**. It
does **not** author the behavioral depth — object state machines, transition
rules, edge-case fan-out, or `#### Scenario:` acceptance blocks. That belongs to
`loom-design:spec-expansion`, which consumes `ui-flows.md` as its rich seed.
**Flag here, fan-out there** — doing the fan-out in this skill would duplicate
loom-design and blur the DESIGN → spec boundary.

**Next station.** Once `ui-flows.md` is done, hand off to `using-loom-design` to
expand the feature into a spec.

## See also

- `references/ux-flow-checklist.md` — the 7 generation dimensions + flag rule.
- `references/ascii-ui-patterns.md` — ASCII layout skeletons + the
  ASCII-vs-Mermaid split.
- `references/knowledge-triage.md` — classify a stuck domain-convention
  question (craft / domain-convention / project-local) before drafting.
- `obsidian:obsidian-mermaid-visualizer` — canonical Mermaid syntax for the flow
  diagrams.
- `loom-design:spec-expansion` — the downstream consumer of `ui-flows.md`; owns
  the behavioral fan-out (state machines, edge cases, scenarios).
- `loom-design:product-principles` — produces the governing
  `PRINCIPLES.md`.
