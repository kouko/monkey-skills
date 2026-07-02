# loom-interface-design

The **active-GENERATE interface/UX design station** that sits between the product constitution and the spec: turn a product idea into a **design change-folder** — a design-system doc plus interaction flows — that **seeds `loom-spec:spec-expansion`** so UX/UI gaps surface *before* spec/code, not after.

```
  PRINCIPLES.md  (loom-product-principles — the constitution)
        │ governs ↓
  interface-design   →   spec   →   code
   (this toolkit)        (GENERATE)   (VERIFY)
```

The station is **cross-modal**: a human interface spans **GUI, TUI, CLI** — the same design concerns with different representation (a GUI has screens + visual tokens; a TUI has panels + keybindings; a CLI has command/flag ergonomics + output/help/error UX). The MVP is **GUI-first**: the skills are written **modality-aware**, but only GUI ships fully — TUI/CLI are phase-2 (see Scope).

It fills the same asymmetry `loom-spec` fixed for specs: `domain-teams:design-team` is **audit/consultant-only** (never a generator), so there was no *active GENERATE* interface-design layer. This toolkit is that layer.

Agent-portable and key-free: the skills drive the host agent's own LLM — no external runtime, no API key, no install beyond the plugin.

## What it does

Two generate skills, a critic, and a router:

- **`design-system`** (modality-aware) → the **design-system artifact** (product-level, one per product):
  - **GUI** → **`DESIGN.md`** in Google's open Apache-2.0 **8-section** format (Overview/Brand · Colors · Typography · Layout · Elevation & Depth · Shapes · Components · Do's & Don'ts; YAML tokens + prose). Visual *system* only — it explicitly does **not** cover flows/screens/navigation, which is why `ui-flows.md` is separate.
  - **TUI / CLI** → a lightweight conventions doc (terminal palette/layout for TUI; output-format + command/flag naming + help/error style for CLI). *Phase-2 — the GUI path ships first.*
- **`interaction-flows`** (modality-aware) → **`ui-flows.md`** (per-feature/change): screen/panel/command inventory (with a *flag* of which render variants exist — empty/loading/error/success), **user flows** as mermaid, **UI structure** as ascii layout blocks, plus transitions, entry/exit points, information density, and mobile flow — a 7-dimension UX-flow checklist. For CLI/TUI the same dimensions render as command/output or panel/keybinding flows.
- **`design-critic`** → adversarial critique of the emitted change-folder (`DESIGN.md` + `ui-flows.md`) via a writer≠judge panel hunting **surface omissions** — undrawn states, dead-end flows, a11y gaps — plus principle-conformance against `PRINCIPLES.md` when present. Surface only, never code.
- **`using-loom-interface-design`** (router) — routes to the three skills and records the modality.

## What it's for

The output is the **design change-folder** — the surface of the interface — that downstream stations consume:

- **Seam-1 (the seed):** `ui-flows.md` is the **rich seed** to `loom-spec:spec-expansion`. It names the objects / starting states / journey; `spec-expansion` does the **behavioral fan-out** (state machines, edge cases, `#### Scenario:` acceptance). That depth is **not** duplicated here — interface-design owns the **surface**, spec-expansion owns the **behavioral depth**.
- **Side-channel:** `DESIGN.md` tokens feed the frontend build itself — colors, spacing, and component defaults the UI code reads. This seam is human/code level, **not** a loom-code skill: no loom-code skill machine-reads `DESIGN.md`.

"States" split by axis: the design lists **render variants per screen** as a presentational *flag*; the spec owns the **domain lifecycle + transition rules**. Design stops at the surface — doing the fan-out would duplicate loom-spec.

## Governed by PRINCIPLES.md

Both skills read `loom-product-principles`'s **`PRINCIPLES.md`** (cross-plugin, path-passed) as the constraining constitution. A principle such as "minimal interface" or "primary task in ≤3 steps" constrains what `ui-flows.md` and the design-system doc may emit, so the interface stays anchored to the product's original intent.

## Output format

The design change-folder is written into the **consumer project** under the established `docs/<toolkit>/` convention:

```
docs/loom/
  DESIGN.md               # GUI design-system, product-level (one per product)
  <change-id>/
    ui-flows.md           # interaction flows, per-feature/change
```

The design-system doc lives at the toolkit root (product-level); `ui-flows.md` is per-feature/change and lives in a **per-change folder** — the same `<change-id>` that `loom-spec:spec-expansion` uses, so the design seed sits beside the spec delta it feeds (a fixed product-level `ui-flows.md` would be overwritten by the next feature). All artifacts are **key-free, in-repo, git-diffable**. A `validate_*` script (mirroring `loom-spec/scripts/validate_spec_output.py`) is the executable format contract: it checks the change-folder's documents are present and well-formed (exit 0 = conformant).

The OpenSpec change-folder that `loom-spec` later produces lives under `docs/loom/` — consistent with the in-use `docs/<toolkit>/` convention, not a root `openspec/`.

## Scope (v0.3.x)

In: the `design-system` and `interaction-flows` generate skills, the `design-critic` writer≠judge gate (shipped v0.2.0, mirroring `loom-spec:completeness-critic`), the router, and the change-folder validator. GUI ships fully (DESIGN.md + ui-flows + validator). The skills are written modality-aware so the architecture is cross-modal from day one.

Out (still deferred):

- **Full TUI / CLI modality implementation** — MVP implements GUI completely; TUI/CLI are **additive** phase-2, not a rewrite. Re-trigger: a real TUI/CLI product needs its conventions/flows.
- **Stitch / Figma / v0 MCP integration** — tier-2 (account/service-bound, breaks key-free purity); good as an optional graceful-degradation add-on, not core.
- **Knowledge-sync (distribute.py)** with `domain-teams:design-team` — kept as the audit complement, no sync in MVP.
- **Behavioral state/edge/path fan-out** — `spec-expansion`'s turf; `ui-flows.md` seeds it, doesn't do it.
- **Automated interface-design → loom-spec hand-off seam** — manual via the shared `docs/<toolkit>/` convention first.
- **Machine consumer for `DESIGN.md` tokens** (loom-code review gate / implementer intake / lint export) — **deliberately parked** (2026-07-02 audit batch ③, reaffirming #456): consumer-side machinery — including the shadcn-vs-Material color-naming question any conformance check must interpret — is undecidable until a real frontend consumer exists, and the upstream DESIGN.md spec is alpha with consumer behavior unspecified. The seam stays human/code-level (documented honestly in `design-system` §Downstream). Re-trigger: the first real GUI product wires its frontend to this pipeline (which also unlocks the shadcn-vs-Material color-naming decision), **or** the upstream spec reaches 1.0 / gains a second-vendor adoption signal.

See `docs/loom/specs/2026-06-14-loom-interface-design-mvp.md` (brief).

## License

This plugin is **MIT**. The `DESIGN.md` *format* it emits derives from Google Labs' open
`DESIGN.md` spec (reported Apache-2.0) — that upstream format license is separate from this
plugin's MIT license; confirm the format's current license against the authoritative spec.
