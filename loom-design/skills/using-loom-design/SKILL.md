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

All user-facing narration in this router — briefs, routing decisions,
recommendation asks — follows `references/design-relay.md` (the local
design-artifact and narration relay). That contract builds on
`references/family-relay.md §Family relay discipline`; load it through the
design relay rather than routing design work through a code-review skill.

**Step 1 — 前站檢查 (upstream check).** Check the target repo against the loom
family's on-ramp criteria table (`references/family-reception.md` — the
reception SSOT; reference it, don't copy its rows here). The negative guard: a
bug fix, a refactor, or a test-covered increment skips the design side entirely
and proceeds straight to whichever downstream station applies
(`loom-code:using-loom-code`). The design side is also internally ordered —
discovery normally comes FIRST (unarticulated problem/users →
`§Discovery station`), then product-principles (no `docs/loom/PRINCIPLES.md` +
product-shaped work → recommend `using-loom-design`'s own intake — this
section — as the starting point, then proceed to `§Product-principles
station`), then interface-design (no `DESIGN.md` / `ui-flows.md` exists yet →
`§Interface-design station`), then spec. When an upstream recommendation
fires, recommend **once**, record the user's choice, then proceed either way.
When both a discovery row and another row fire on the same ask, the
precedence note recorded in `family-reception.md` governs — don't re-derive
it here.

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

The UI/UX-surface and spec rows both redirect within this same router —
`using-loom-design` — via `§Interface-design station` (see its own
`Skill priority` table below) and `§Spec station`; only the code row
leaves for `using-loom-code`.

**Step 3 — brief before a complex fork.** A fork this router surfaces (a station
choice, a value commitment, an on-ramp choice) can itself be non-trivial. When
the fork is complex enough to warrant a brief, run
`dev-workflow:brief-before-asking` first instead of improvising the question —
the trigger threshold and stakes-first framing live in
`references/family-reception.md §Brief before a complex fork` (the
single source; reference it, don't copy it).

<EXTREMELY-IMPORTANT>
**You have loom-design.** This router does not map needs, assess worth, draft
constitutions, design interfaces, or write specs itself — it is the thin entry
that decides which of the four design-side stations the work needs — discovery /
product-principles / interface-design / spec — after checking whether the
design side is even the right station yet, then routes to that station's member
skill(s).
</EXTREMELY-IMPORTANT>

## Discovery station

The problem-space station. Discovery sits upstream of principles/design/spec/
code — it is normally the FIRST station a product-shaped idea reaches, not a
station something else feeds into. Route between its two members by the
specific verb:

- **"worth doing?" / is this worth my time or resources** — an adversarial
  worth-it check, a GO / NO-GO / NEEDS-MORE-RESEARCH call →
  `business-value`.
- **"what do users need?" / what problem exists, for whom** — evidence-linked
  opportunity mapping, or committing to which needs to serve →
  `user-insights`.

When in doubt, ask "are we deciding whether it's worth doing, or are we
figuring out what the problem/users actually are?" — the answer picks the
member.

**Family.**
- `business-value` — adversarial worth-it check (Shape Up betting register, not
  a Cagan business-viability study). Optional: fires only under its own named
  trigger conditions (see its SKILL.md), silently skipped for personal tools or
  an already-decided GO. Produces `business-value.md`.
- `user-insights` — the core research verb. Maps the opportunity space
  (evidence-linked needs) and then proposes a value commitment the user must
  ratify. Produces `user-insights.md`, `evidence.md`, `research/`.

**Typical sequence: `user-insights` ↔ `business-value`.** Most discovery work
starts with `user-insights` — map the opportunity space with evidence before
anyone can judge whether it's worth doing. `business-value` (the "assess" step)
is **skippable** — it only fires under its own trigger conditions — and
**re-entrant**: it can run again after `user-insights` surfaces more research,
and `user-insights` can loop back after a NEEDS-MORE-RESEARCH verdict. Neither
member is a required gate on the other; call the one the ask actually names.

**Professional isolation is contract-level.** The two skills share no artifact and no agent: `business-value`'s agents may not map needs; `user-insights`'s agents may not render investment verdicts. Do not blend their outputs into one file or one dispatch.

Host tool call shapes for discovery's research dispatch and delegation:
`references/discovery-claude-code-tools.md` (Claude Code) /
`references/discovery-codex-tools.md` (Codex).

## Product-principles station

The constitution station. This station does intake + routing, then hands off;
it does not write the constitution itself.

**Hand off.** Once intake confirms this is the right station, hand off to
`product-principles` — the member skill that elicits the idea, reads
`docs/loom/PURPOSE.md` as background context when present, and derives the
3–7 falsifiable principles into `PRINCIPLES.md`. If `docs/loom/PRINCIPLES.md`
already exists in the target repo, confirm with the user whether this
station's work is already done before proceeding.

**Unarticulated problem/users.** If the problem/users are unarticulated (no
evidence for who needs what), route to `§Discovery station` first; resume here
with its output as seed.

## Interface-design station

The surface station — design a product's interface/interaction/UX in any
modality (GUI/TUI/CLI). Three load-bearing rules:

1. **Record the modality first.** Before any design work, ask the user which
   **modality** the product is — **GUI / TUI / CLI** — and record it. If the
   user does not specify, **default to GUI**. The modality decides which
   design-system artifact you produce (GUI → `DESIGN.md`) and how interaction
   flows are expressed.
2. **PRINCIPLES.md governs.** Read the product's `PRINCIPLES.md` (produced by
   `product-principles`) as the **governing context**. Every design decision is
   checked against it — the design must not contradict the product's purpose
   (`docs/loom/PURPOSE.md`, when present) or any non-negotiable principle.
   If `PRINCIPLES.md` is absent, surface that gap;
   the principles layer comes first.
3. **Two generate skills, one per concern.** Route to `design-system` for the
   static design-system artifact and `interaction-flows` for the dynamic
   interaction/flow artifact. Both are governed by the recorded modality +
   `PRINCIPLES.md`.

**Skipping the modality step or the PRINCIPLES governance = violation.**
"It's obviously a GUI, skip asking" / "I don't need the principles" are
rationalizations — record the modality (default GUI) and read `PRINCIPLES.md`
first.

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

Ask the user once; if unspecified, default to **GUI**. Record the answer before
routing. The modality is passed to both generate skills.

### Skill priority — decision order for interface-design tasks

Walk through these stages in order. Skip a stage only when its precondition is
already met.

| # | Stage | Skill (target) | Output |
|---|---|---|---|
| 0 | Modality | (this router — Step 0) | recorded modality (GUI / TUI / CLI) |
| 1 | Static design system | `design-system` | the design-system artifact (GUI → `DESIGN.md`) |
| 2 | Interaction / flows | `interaction-flows` | `ui-flows.md` |
| 3 | Review (writer≠judge gate) | `design-critic` | gap-hunted design + `## Blind spots` |

Stages 1–2 read the product's `PRINCIPLES.md` as governing context.

**Stage 3 — the design station's completeness gate.** Once `design-system` +
`interaction-flows` have emitted their artifacts, route to `design-critic` for
an adversarial heuristic-evaluation pass (writer≠judge) that hunts SURFACE
omissions — undrawn empty/error/loading states, navigational dead-ends,
unreachable screens, missing entry/exit — **before** `ui-flows.md` is handed to
`spec-expansion`. It critiques the surface only; behavioral fan-out stays
downstream.

**Stage-3 resolution rule.** `design-critic` ends with a two-valued verdict:
`NEEDS_REVISION` → route back to `design-system` / `interaction-flows` for the
flagged surfaces, then re-run the critic; `PASS_WITH_NOTES` → the change-folder
proceeds (`ui-flows.md` hands to `spec-expansion`). There is no bare `PASS` —
the critic never claims the surface is complete.

### Red flags — agent rationalizations to refuse

| Agent says | Reality | Correct response |
|---|---|---|
| "It's clearly a GUI, no need to ask the modality." | Modality is load-bearing; assuming it skips the recorded contract. | Ask once; if no answer, default GUI and **record** it. |
| "I'll design without reading PRINCIPLES.md." | The design must be checked against the product constitution. | Read `PRINCIPLES.md` first; surface it if absent. |
| "Design system and flows are the same artifact." | Static system ≠ dynamic interaction. | Route `design-system` and `interaction-flows` separately. |

### Coexistence

- **`product-principles`** — produces the `PRINCIPLES.md` this toolkit reads as
  governing context. The principles layer comes **before** interface design;
  this station consumes its output, never duplicates it.
- Downstream **spec** (`spec-expansion`) consumes `ui-flows.md`; the **code /
  frontend** layer consumes the `DESIGN.md` tokens directly at implementation
  time (a human / code-level seam, not a loom-code skill).

Host tool call shapes for the design critic's multi-lens panel:
`references/interface-claude-code-tools.md` (Claude Code) /
`references/interface-codex-tools.md` (Codex).

## Spec station

The requirements station — fans a sparse seed out into a spec draft, or
critiques an existing draft for omissions. Route between its two members by the
specific verb — this distinction is load-bearing, not cosmetic:

- **draft/expand a spec from a seed** — a few lines of feature intent, or a
  `ui-flows.md`, that needs fan-out into objects/states/paths/edge cases →
  `spec-expansion`.
- **critique/audit an EXISTING draft for omissions** — a spec-expansion output
  already exists and needs a completeness pass before VERIFY →
  `completeness-critic`.

This closes the **#456-documented adjacent mis-route**: a critique-an-existing-
spec ask getting sent to `spec-expansion` (which would silently re-draft instead
of auditing) instead of `completeness-critic`. When in doubt, ask "does a draft
already exist to critique, or am I starting from a seed?" — the answer picks the
member.

**Family.**
- `spec-expansion` — GENERATE-layer writer. Fans a sparse seed out into a
  high-recall spec draft (OpenSpec change-folder shape).
- `completeness-critic` — GENERATE-layer critic. Adversarially hunts omissions
  in an existing `spec-expansion` draft via a fresh-context lens panel; never
  touches code.

Both stop at GENERATE — `loom-code:writing-plans` reads the emitted
`#### Scenario:` criteria downstream; that is the one-directional spec→code
handoff, not this router's job.

Host tool call shapes for the completeness critic's multi-lens panel:
`references/spec-claude-code-tools.md` (Claude Code) /
`references/spec-codex-tools.md` (Codex).

## How to access skills

| Harness | Mechanism |
|---|---|
| Claude Code | Use the `Skill` tool, e.g. `Skill(skill: "business-value")`, `Skill(skill: "user-insights")`, `Skill(skill: "product-principles")`, `Skill(skill: "design-system")`, `Skill(skill: "interaction-flows")`, `Skill(skill: "design-critic")`, `Skill(skill: "spec-expansion")`, or `Skill(skill: "completeness-critic")`. |
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
