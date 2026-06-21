# Brief — interface-design-toolkit MVP (cross-modal interface/UX GENERATE front-end)

> Date: 2026-06-14 · Stage: brainstorming → (next) writing-plans
> Pipeline position: **interface-design station** (optional; fires for any product with a human interface) → spec-toolkit → code-toolkit
> Governed by `product-principles-toolkit`'s `PRINCIPLES.md`. Split from the superseded `docs/product-design-toolkit/specs/2026-06-14-product-design-toolkit-mvp.md`.

## Problem

(Axis 1 — JTBD) When kouko designs a product that has a **human interface**, he wants to do the **interface &
interaction design** up front and produce design documents that **flow into `spec-toolkit:spec-expansion`** —
instead of jumping to spec/code and discovering UX/UI gaps late. Crucially the interface spans **multiple
modalities** — GUI, TUI, CLI — each with the **same design concerns but different representation** (a CLI has
command/flag ergonomics, output format, help/error UX; a TUI has panels/keybindings; a GUI has screens + visual
tokens). The existing `domain-teams:design-team` is **audit/consultant-only** (never used as a generator) — there
is no *active GENERATE* interface-design layer, the same asymmetry `spec-toolkit` fixed for specs vs `code-team`.
Sub-job: **discuss design visually** (mermaid flows / ascii layout, optionally real UI mockups), not purely prose.

## Users

(Axis 2) kouko — solo dev, macOS, Claude Code + Codex hosts, public marketplace, **key-free / portable** ethos.
Builds **GUI + TUI + CLI** products (and pure-headless ones that skip this toolkit entirely). Today jumps straight
to spec-expansion; design-team exists but is passive/audit and unused. Wants a GENERATE interface front-end he
actually uses, with visual design communication, that adapts to the product's modality.

## Smallest End State

(Axis 3 — **minimal core**) **Two generate skills + a router**, in a new `interface-design-toolkit` plugin:

1. **`design-system`** (modality-aware) → the design-system artifact:
   - **GUI** → **`DESIGN.md`** in Google's open Apache-2.0 **8-section** format (Overview/Brand · Colors ·
     Typography · Layout · Elevation & Depth · Shapes · Components · Do's & Don'ts; YAML tokens + prose; lint-able
     via `npx @google/design.md`). Visual *system* only — product-level (one per product).
   - **TUI / CLI** → a lightweight conventions doc (terminal palette/layout for TUI; output-format + command/flag
     naming + help/error style for CLI). *(MVP implements GUI fully; TUI/CLI are phase-2 — see Out of Scope.)*
2. **`interaction-flows`** (modality-aware) → **`ui-flows.md`** (per-feature/change): screen/panel/command
   inventory (+ a *flag* of which render variants exist — empty/loading/error/success), **user flows** as mermaid
   (reuse `obsidian:obsidian-mermaid-visualizer`), **UI structure** as ascii layout blocks (mermaid has no native
   wireframe — issue #1184), plus transitions, entry/exit points, information density, mobile flow (a 7-dimension
   UX-flow checklist). For CLI/TUI the same dimensions render as command/output flows or panel/keybinding flows.
3. **`using-interface-design-toolkit`** (router) — routes to the two skills + records the modality.

A `validate_*` script (mirror `validate_spec_output.py`) validates the emitted **change-folder** (the
design-system doc + `ui-flows.md` present and well-formed). All artifacts **key-free, in-repo, git-diffable**.

**Two downstream paths:**
- `ui-flows.md` (inventory + nav + render-variant flags) is the **rich seed** to `spec-toolkit:spec-expansion` —
  it names objects / starting states / journey; spec-expansion does the **behavioral fan-out** (state machines,
  edges, `#### Scenario:`) — NOT duplicated here.
- `DESIGN.md` tokens are a **side-channel** straight to code-toolkit's frontend implementation (styling/lint).

**Runtime output location:** consumer project `docs/loom/` (per the established `docs/<toolkit>/`
convention) — design-system doc at the toolkit root (product-level), `ui-flows.md` per-feature/change. The OpenSpec
change-folder that spec-toolkit later produces lives under `docs/spec-toolkit/` (artifact-location decision **A**:
in-`docs/`, consistent with the in-use convention, not a root `openspec/`).

## Current State Evidence

- **DESIGN.md scope (research-confirmed):** Google's open `DESIGN.md` is the **visual *system*** — 8 token
  sections only — and **explicitly does not address flows/screens/navigation**. → the separate `ui-flows.md` is
  required; DESIGN.md is the GUI instantiation of the design-system slot, not the whole design.
- **Surface/depth boundary generalizes across modalities:** interface-design owns the **interface surface** (any
  modality — screens/commands/panels, nav, visual/terminal/CLI conventions); `spec-expansion` owns the
  **behavioral depth** (object state machines, edge cases, acceptance scenarios). "States" split by axis: design
  lists **render variants per screen** as a *flag* (presentational), spec owns the **domain lifecycle + transition
  rules** (behavioral). Design stops at the surface — doing the fan-out would duplicate spec-toolkit.
- **Seam-1 (corrected):** the seed to `spec-expansion` is **`ui-flows.md`** (not DESIGN.md tokens). `spec-toolkit/
  skills/spec-expansion/SKILL.md` consumes a "sparse seed"; `ui-flows.md` is the richer seed.
- **Governed by PRINCIPLES.md:** both skills read `product-principles-toolkit`'s `PRINCIPLES.md` (cross-plugin
  reference, path-passed) as the constraining constitution — e.g. "minimal interface" constrains `ui-flows.md`.
- **External corroboration (a reference implementation reviewed privately — PATTERNS ONLY, kept out of this
  repo):** a larger product-development skill suite independently splits the **visual system** from the **UX
  flow** into two separate artifacts, and defers external visual tools to a reference tier. This validates: (a)
  separate visual-system from UX-flow; (b) the 7-dimension UX-flow checklist; (c) defer Stitch/Figma to tier-2.
  Difference we keep: we *generate* (the reference *captures* post-hoc — we invert its capture-questions into
  generation prompts).
- **Audit complement (SSOT):** `domain-teams/skills/design-team/SKILL.md` is the audit/consultant team
  (the generate-gap this toolkit fills); kept as the audit complement, **no knowledge-sync (distribute.py)** in MVP.
- **Reuse:** `obsidian/skills/obsidian-mermaid-visualizer/SKILL.md` — mature mermaid generation (reference the
  pattern; do not re-author mermaid rules).
- **Scaffold convention:** `.claude-plugin/plugin.json` + `skills/` + `scripts/` + `README.md` + root
  `marketplace.json` entry; `spec-toolkit/` is the template.

### Evidence paths appendix
- `spec-toolkit/skills/spec-expansion/SKILL.md`, `domain-teams/skills/design-team/SKILL.md`,
  `obsidian/skills/obsidian-mermaid-visualizer/SKILL.md`, `spec-toolkit/scripts/validate_spec_output.py`
- `docs/loom/specs/2026-06-14-product-principles-toolkit-mvp.md` (the governing constitution plugin)
- Research: Google open `DESIGN.md` 8-section visual-system scope (designmd.app/what-is-design-md, howaiworks.ai, anthropics/skills#1008)

## Decision

Build a **new, separate `interface-design-toolkit` plugin** — the active-GENERATE, **cross-modal** interface/UX
design station. MVP = **two generate skills** (`design-system` modality-aware, `interaction-flows` modality-aware)
+ a router, producing a design change-folder that **seeds `spec-expansion`**. Separate from
`product-principles-toolkit` (principles is product-level/cross-cutting; this is interface-craft). Separate from
spec-toolkit (modular peer station; B/D = D posture). We adopt the **Google `DESIGN.md` format** for the GUI
design-system and **mermaid/ascii** for flows, but **not**: the Stitch/Figma MCP yet, a design-critic yet, full
TUI/CLI modality implementation yet (architecture is modality-aware from day one; GUI ships first), nor a
design-team knowledge-sync.

## Out of Scope (MVP)

- **`design-critic` skill** (omission + principle-conformance hunt over the change-folder; writer≠judge, mirrors
  `spec-toolkit:completeness-critic`). Deferred to phase-2 — `code-toolkit` reviewers + `completeness-critic`
  already exist. Re-trigger: real design output ships with missed states/flows that a critic would have caught.
- **Full TUI / CLI modality implementation.** MVP implements GUI completely (DESIGN.md + ui-flows + validator);
  the skills are written **modality-aware** so TUI/CLI are **additive** phase-2, not a rewrite. Re-trigger: kouko
  designs a real TUI/CLI product and needs the conventions/flows for it.
- Stitch / Figma / v0 MCP integration (tier-2; official MCP with graceful degradation; breaks key-free purity).
- Knowledge-sync (distribute.py) with `domain-teams:design-team`.
- State/edge/path behavioral fan-out (spec-expansion's turf — `ui-flows.md` seeds it, doesn't do it).
- product-design → spec-toolkit **automated** hand-off seam (manual via shared `docs/<toolkit>/` convention first).

## Alternatives Considered

(Axis 4 — research-grounded, EN+JP via WebSearch)
- **DESIGN.md (Google open Apache-2.0)** — *chosen for the GUI design-system artifact.* Portable,
  Claude-Code-consumable, git-diffable, key-free, lint-able. **8 token sections, visual-system scope only** →
  hence the separate `ui-flows.md`. Con: newer ecosystem; GUI-only (TUI/CLI need our own conventions doc).
- **mermaid + ascii (diagrams-as-code)** — *chosen for flows/UI structure.* Agent-generatable, key-free, in-repo,
  reuse existing skill. Con: mermaid has no native wireframe (#1184) → ascii for layout.
- **One modality-agnostic generate skill** vs **two split skills** — *chose two* (`design-system` +
  `interaction-flows`): different mindsets (visual/conventions vs journey/interaction), independently re-runnable,
  matches the external reference's visual/flow split. Con: slightly more routing surface (accepted).
- **Stitch / Figma via official MCP** — *deferred to tier-2.* Real UI mockups + React/Tailwind export; account/
  service-bound, breaks key-free, non-production code. Good as optional.
- **Reuse `domain-teams:design-team` as the generator** — *rejected.* It's audit/consultant, not a generator
  (the gap this toolkit fills); kept as audit complement.

## What Becomes Obsolete

(Axis 5) Closes the "jump straight to spec with no interface-design front-end" gap. Nothing is deleted —
design-team stays as audit, spec-expansion stays for behavioral fan-out, `product-principles-toolkit` owns
principles. Additive → YAGNI risk acknowledged, justified by the real generate-gap (design-team audit-only) +
kouko's multi-modality pipeline-front-end scenario. Re-baseline if the skills go unused after a real product run.

## Open Questions

- **Plugin/skill names:** plugin `interface-design-toolkit` vs `interaction-design-toolkit`; skills
  `design-system` / `interaction-flows` (file `ui-flows.md` vs `interaction-flows.md`). Decide in writing-plans.
- **Modality detection:** does the skill ask the user the modality (GUI/TUI/CLI) or infer it? (Lean: ask, default
  GUI.) MVP only branches GUI fully; TUI/CLI emit a stub + phase-2 note.
- **Exact `DESIGN.md` YAML token keys:** fetch the authoritative Google spec at build time to lock keys (the
  8 sections are known); validator validates the whole change-folder.
- **Codex 1024-char description guardrail** applies to each new skill's description.
- **Governance:** synthetic examples only; **no company/customer names** in any committed file (run the
  identifiable-token grep before commit — the session already bit the scrub-in-guardrail-note trap); explicit
  `git add <paths>`, never `-A`.
