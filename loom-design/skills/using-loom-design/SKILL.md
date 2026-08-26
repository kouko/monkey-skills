---
name: using-loom-design
# firing-evidence: merged from using-loom-discovery (2026-07-14 baseline 3/3 EXACT) + the other three design-side routers
description: |
  The loom-design family entry router — intake + routing when unsure which
  design skill applies, or 不確定從哪開始 ('where do I start'): 值不值得做,
  需求研究, ユーザーインサイト, UI/UX design, spec asks all route here first.
version: 0.1.0
---

# using-loom-design

<SUBAGENT-STOP>
If you are a subagent already dispatched with an explicit role prompt, **do not** re-route through this skill. Follow the prompt you were dispatched with directly. This router is for the parent orchestrator only.
</SUBAGENT-STOP>

## §Intake

All user-facing narration follows `references/design-relay.md`, which builds on
`references/family-relay.md §Family relay discipline`. Never route design work
through a code-review skill.

**Step 1 — 前站檢查 (upstream check).** Load `references/family-reception.md`
and apply its on-ramp table (the family
reception SSOT; do not copy it).
A bug fix, refactor, or test-covered increment skips design and goes to
`loom-code:using-loom-code`. Within design, discovery normally comes FIRST
(unarticulated problem/users), then product-principles (product-shaped work
without `docs/loom/PRINCIPLES.md`: recommend this `using-loom-design` intake,
then `§Product-principles station`), then interface-design (no `DESIGN.md` /
`ui-flows.md`), then spec. Recommend an upstream stop once, record the choice,
and proceed either way. If discovery and another row both fire, use the
precedence rule in `family-reception.md`.

**Step 2 — 對站檢查 (station check).** Route by what the ask actually is —
redirect to the matching station rather than forcing the ask through the wrong
one:

| The ask is… | Station | Go to |
|---|---|---|
| 值不值得做 / is it worth my time / 需求研究 / what do users need / ユーザーインサイト | discovery | `§Discovery station` |
| product-constitution / PRINCIPLES.md / 不確定從哪開始 / where do I start | product-principles | `§Product-principles station` |
| UI/UX surface / screen flow / TUI/CLI layout | interface-design | `§Interface-design station` |
| spec fan-out / draft-or-critique a spec | spec | `§Spec station` |
| write / change / review / ship code | code | `loom-code:using-loom-code` |

UI/UX and spec redirect within `using-loom-design` to `§Interface-design
station` (its Skill priority table) and `§Spec station`; only code leaves.

**Step 3 — brief before a complex fork.** Before a non-trivial station, value,
or on-ramp choice, run `loom-workflow:brief-before-asking`. Use the trigger and
stakes framing in `references/family-reception.md §Brief before a complex fork`.

<EXTREMELY-IMPORTANT>
**You have loom-design.** This thin entry does not map needs, assess worth,
author constitutions, design interfaces, or write specs. It checks whether
design applies, then routes to discovery / product-principles /
interface-design / spec member skills.
</EXTREMELY-IMPORTANT>

## Discovery station

Discovery is the upstream problem-space station. Route by the verb:

- **"worth doing?" / is this worth my time or resources** — an adversarial
  worth-it check, a GO / NO-GO / NEEDS-MORE-RESEARCH call →
  `business-value`.
- **"what do users need?" / what problem exists, for whom** — evidence-linked
  opportunity mapping, or committing to which needs to serve →
  `user-insights`.

When in doubt, ask "are we deciding whether it's worth doing, or are we
figuring out what the problem/users actually are?" — the answer picks the
member.

`business-value` is an optional adversarial worth-it check; it fires only under
its SKILL.md triggers, skips personal tools or an already-decided GO, and emits
`business-value.md`. `user-insights` maps evidence-linked needs, proposes a
user-ratified value commitment, and emits `user-insights.md`, `evidence.md`,
and `research/`.

**Typical sequence: `user-insights` ↔ `business-value`.** Start with evidence
mapping when needed. The assess step is skippable and re-entrant: rerun it after
new research, or return to research after NEEDS-MORE-RESEARCH. Neither member
gates the other; call the verb requested.

**Professional isolation is contract-level.** They share no artifact and no agent:
business-value agents may not map needs; user-insights agents may not
render investment verdicts. Never combine their file or dispatch.

Host tool call shapes for discovery's research dispatch and delegation:
`references/discovery-claude-code-tools.md` (Claude Code) /
`references/discovery-codex-tools.md` (Codex).

## Product-principles station

This constitution station routes; it does not write. Hand off to
`product-principles`, which elicits the idea, reads `docs/loom/PURPOSE.md` when
present, and derives 3–7 falsifiable principles into `PRINCIPLES.md`. If that
file exists, confirm whether this work is already done.

If evidence does not articulate who needs what, route to `§Discovery station`
first, then resume here with its output.

## Interface-design station

The surface station handles GUI/TUI/CLI. Three load-bearing rules:

1. **Record the modality first.** Ask once for **GUI / TUI / CLI**; if
   unspecified, default to and record GUI. It determines the artifact (GUI →
   `DESIGN.md`) and flow notation.
2. **PRINCIPLES.md governs.** Read it first and check every decision against it
   and `docs/loom/PURPOSE.md` when present. If absent, surface the gap; the
   principles layer comes first.
3. **Two generate skills, one per concern.** `design-system` owns the static
   artifact; `interaction-flows` owns dynamic flows. Both receive modality and
   principles.

Skipping modality recording or principles governance is a violation.

Do not accept shortcuts that erase these boundaries. An apparently obvious GUI
still requires one recorded modality decision (with GUI as the fallback), and
design work still reads or explicitly surfaces the missing `PRINCIPLES.md`.
Static design-system choices and dynamic interaction flows remain separate
artifacts owned by separate member skills. The router records and passes the
inputs; it does not fill either artifact itself.

### Instruction priority

When instructions conflict, follow this order:

1. User's `CLAUDE.md` / project conventions — local rules always win.
2. The product's `PRINCIPLES.md` — the product constitution governs all design.
3. loom-design skills loaded into context — this router + invoked generators.
4. Host default behavior — fallback only.

### Step 0 — Record the modality

| Modality | What it is | Design-system artifact |
|---|---|---|
| **GUI** (default) | Graphical screens — web / mobile / desktop | `DESIGN.md` |
| **TUI** | Terminal UI — panes, keybindings, in-terminal layout | design-system artifact (TUI shape) |
| **CLI** | Command-line surface — commands, flags, output format | design-system artifact (CLI shape) |

Record the answer before routing and pass it to both generators.

### Skill priority — decision order for interface-design tasks

Follow this order; skip only an already-satisfied stage.

| # | Stage | Skill (target) | Output |
|---|---|---|---|
| 0 | Modality | (this router — Step 0) | recorded modality (GUI / TUI / CLI) |
| 1 | Static design system | `design-system` | the design-system artifact (GUI → `DESIGN.md`) |
| 2 | Interaction / flows | `interaction-flows` | `ui-flows.md` |
| 2a | Integrated validation | resume `design-system` Step 6 | validated change folder |
| 3 | Review (writer≠judge gate) | `design-critic` | gap-hunted design + `## Blind spots` |

Stages 1–2 read the product's `PRINCIPLES.md` as governing context.

**Stage 3 — completeness gate.** After both generators emit artifacts, route to
writer≠judge `design-critic` to hunt SURFACE omissions (missing states,
dead-ends, unreachable screens, entry/exit) before handing `ui-flows.md` to
`spec-expansion`. Behavioral fan-out remains downstream.

**Stage-3 resolution.** `NEEDS_REVISION` → repair via `design-system` /
`interaction-flows`, then re-run the critic. `PASS_WITH_NOTES` → proceed and
hand `ui-flows.md` to `spec-expansion`. There is no bare `PASS`.

### Coexistence

- `product-principles` produces the governing `PRINCIPLES.md`; interface design
  consumes, never duplicates it.
- `spec-expansion` consumes `ui-flows.md`; code/frontend consumes `DESIGN.md`
  tokens at implementation time (a human/code seam, not a loom-code skill).

Host tool call shapes for the design critic's multi-lens panel:
`references/interface-claude-code-tools.md` (Claude Code) /
`references/interface-codex-tools.md` (Codex).

## Spec station

The requirements station routes by a load-bearing verb distinction:

- **draft/expand a spec from a seed** — a few lines of feature intent, or a
  `ui-flows.md`, that needs fan-out into objects/states/paths/edge cases →
  `spec-expansion`.
- **critique/audit an EXISTING draft for omissions** — a spec-expansion output
  already exists and needs a completeness pass before VERIFY →
  `completeness-critic`.

This closes the **#456-documented adjacent mis-route** where critique was sent
to a re-drafter. If unclear, ask whether a draft exists or this starts from a
seed.

`spec-expansion` is the GENERATE-layer writer; `completeness-critic` is its
fresh-context omission critic and never touches code.

Both stop at GENERATE. Downstream `loom-code:writing-plans` reads emitted
`#### Scenario:` criteria; this one-way spec→code handoff is not router work.

The distinction depends on the input state, not merely the word "spec": a seed
needs generation, while an already-authored draft needs independent omission
critique. Never replace the existing draft during an audit request, and never
ask the critic to invent the first draft.

Host tool call shapes for the completeness critic's multi-lens panel:
`references/spec-claude-code-tools.md` (Claude Code) /
`references/spec-codex-tools.md` (Codex).

## How to access skills

| Harness | Mechanism |
|---|---|
| Claude Code | Use the `Skill` tool with the listed member name. |
| Codex CLI | Use the `skill` tool (Codex shape). |

If the user types a member skill's `/name`, that is an explicit invocation —
load it via the Skill tool directly. Do not guess names that are not listed
above.

## What this router does NOT do

- Does **not** assess worth-doing itself — that is `business-value`.
- Does **not** map needs or research evidence itself — that is `user-insights`.
- Does **not** author `PRINCIPLES.md` itself — that is `product-principles`.
- Does **not** produce design artifacts itself — that is `design-system` and
  `interaction-flows`.
- Does **not** draft or critique a spec itself — that is `spec-expansion` and
  `completeness-critic`.
- Does **not** auto-invoke any member — the harness invokes them when the user's
  next message + this routing decision match.
