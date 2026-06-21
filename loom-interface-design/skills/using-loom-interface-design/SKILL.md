---
name: using-loom-interface-design
description: |
  Router for loom-interface-design — design a product's interface/interaction/UX in any modality (GUI/TUI/CLI). Routes to design-system (→ DESIGN.md) + interaction-flows (→ ui-flows.md). Use for 'design the UI/UX', screen flow, TUI/CLI layout.
version: 0.1.0
---

<SUBAGENT-STOP>
If you are a subagent already dispatched with an explicit role prompt, **do not** re-route through this skill. Follow the prompt you were dispatched with directly. This router is for the parent orchestrator only.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
**You have loom-interface-design.** When the user wants to design a product's interface, interaction, or UX, route through this skill before producing any design artifact.

Three load-bearing rules:

1. **Record the modality first.** Before any design work, ask the user which **modality** the product is — **GUI / TUI / CLI** — and record it. If the user does not specify, **default to GUI**. The modality decides which design-system artifact you produce (GUI → `DESIGN.md`) and how interaction flows are expressed.
2. **PRINCIPLES.md governs.** Read the product's `PRINCIPLES.md` (produced by `loom-product-principles:product-principles`) as the **governing context**. Every design decision is checked against it — the design must not contradict the North Star or any non-negotiable principle. If `PRINCIPLES.md` is absent, surface that gap; the principles layer comes first.
3. **Two generate skills, one per concern.** Route to `design-system` for the static design-system artifact and `interaction-flows` for the dynamic interaction/flow artifact. Both are governed by the recorded modality + `PRINCIPLES.md`.

**Skipping the modality step or the PRINCIPLES governance = violation.** "It's obviously a GUI, skip asking" / "I don't need the principles" are rationalizations — record the modality (default GUI) and read `PRINCIPLES.md` first.
</EXTREMELY-IMPORTANT>

## Instruction priority

When instructions conflict, follow this order:

1. User's `CLAUDE.md` / project conventions — local rules always win.
2. The product's `PRINCIPLES.md` — the product constitution governs all design.
3. loom-interface-design skills loaded into context — this router + invoked generators.
4. Host default behavior — fallback only.

## Step 0 — Record the modality

| Modality | What it is | Design-system artifact |
|---|---|---|
| **GUI** (default) | Graphical screens — web / mobile / desktop | `DESIGN.md` |
| **TUI** | Terminal UI — panes, keybindings, in-terminal layout | design-system artifact (TUI shape) |
| **CLI** | Command-line surface — commands, flags, output format | design-system artifact (CLI shape) |

Ask the user once; if unspecified, default to **GUI**. Record the answer before routing. The modality is passed to both generate skills.

## Skill priority — decision order for interface-design tasks

Walk through these stages in order. Skip a stage only when its precondition is already met.

| # | Stage | Skill (target) | Output |
|---|---|---|---|
| 0 | Modality | (this router — Step 0) | recorded modality (GUI / TUI / CLI) |
| 1 | Static design system | `design-system` | the design-system artifact (GUI → `DESIGN.md`) |
| 2 | Interaction / flows | `interaction-flows` | `ui-flows.md` |
| 3 | Review (writer≠judge gate) | `design-critic` | gap-hunted design + `## Blind spots` |

Stages 1–2 read the product's `PRINCIPLES.md` as governing context.

**Stage 3 — the design station's completeness gate.** Once `design-system` +
`interaction-flows` have emitted their artifacts, route to `design-critic` for an
adversarial heuristic-evaluation pass (writer≠judge) that hunts SURFACE omissions —
undrawn empty/error/loading states, navigational dead-ends, unreachable screens,
missing entry/exit — **before** `ui-flows.md` is handed to `loom-spec:spec-expansion`.
It critiques the surface only; behavioral fan-out stays downstream.

## How to access skills

| Harness | Mechanism |
|---|---|
| Claude Code | Use the `Skill` tool, e.g. `Skill(skill: "design-system")`. |
| Codex CLI | Use the `skill` tool (Codex shape). |

If the user types `/skill-name`, that is an explicit invocation — load it via the Skill tool. Do not guess names that are not listed above.

## Red flags — agent rationalizations to refuse

| Agent says | Reality | Correct response |
|---|---|---|
| "It's clearly a GUI, no need to ask the modality." | Modality is load-bearing; assuming it skips the recorded contract. | Ask once; if no answer, default GUI and **record** it. |
| "I'll design without reading PRINCIPLES.md." | The design must be checked against the product constitution. | Read `PRINCIPLES.md` first; surface it if absent. |
| "Design system and flows are the same artifact." | Static system ≠ dynamic interaction. | Route `design-system` and `interaction-flows` separately. |

## Coexistence

- **`loom-product-principles:product-principles`** — produces the `PRINCIPLES.md` this toolkit reads as governing context. The principles layer comes **before** interface design; this toolkit consumes its output, never duplicates it.
- Downstream **spec** and **code** layers consume the design artifacts (the design-system artifact + `ui-flows.md`) produced here.

## What this router does NOT do

- Does **not** produce design artifacts itself — it routes to `design-system` and `interaction-flows`.
- Does **not** author or override `PRINCIPLES.md` — that belongs to `loom-product-principles`.
- Does **not** auto-invoke downstream skills — the harness invokes them when the user's next message + Skill Priority match.
