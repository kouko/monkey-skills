---
name: brainstorming
description: |
  Use BEFORE implementing new behavior or non-obvious design — explore intent + alternatives via an upstream-artifact gate (Axis 0) → a brief. Refuses 'this is simple' / 'just start coding'.
version: 0.12.1
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (implementer / spec-reviewer / code-quality-reviewer / code-reviewer), the parent orchestrator already finished discovery. **Do not** re-route through this skill. Follow your dispatched prompt directly.
</SUBAGENT-STOP>

## The HARD-GATE

> **DO NOT START IMPLEMENTING UNTIL YOU HAVE EXPLORED INTENT.**

Pressure to skip — *"this is simple," "I know what to build," "just start coding"* — is the failure mode. If you start drafting code, opening implementation files, or invoking `tdd-iron-law` before completing Axis 0–5, stop and return here.

### What counts as "before implementation"

| Phase | Iron-Law on TDD applies? | brainstorming applies? |
|---|---|---|
| User says *"add feature X"* | Not yet (no code being written) | **YES — start here** |
| Brief complete; plan being drafted | Not yet | Hand off to `writing-plans` |
| Atomic task / implementer dispatched | YES | Already complete; brief is in the prompt |

For new behavior, module boundaries, or non-obvious design, the first row is mandatory.

## When NOT to use

This list is exhaustive; otherwise the HARD-GATE applies.

| Exempt category | What qualifies | What does NOT qualify |
|---|---|---|
| **One-line known-pattern fix** | Typo in a string literal; bumping a version number in `package.json`; flipping a documented config value (no behavior change for the user). | A "small change" that touches behavior (e.g. retries: 3 → 5 — that's a retry-policy decision, not a config tweak). |
| **Pure refactor under existing test coverage** | Rename a private function; extract a method while all existing tests stay green. | Architecture-shifting refactor (extract a new module boundary, replace a synchronous call with an event). |
| **Bug fix where the failing test already exists** | A test is RED reproducibly; you know which line is wrong. | A bug where *"the test should fail but doesn't"* (false-green diagnostic; see `tdd-iron-law/SKILL.md` §False-green diagnostic). |
| **Explicit user override** | User says *literally* "skip brainstorming, here's the spec, go" AND hands in a written spec / plan that already covers the 5 axes. | User says *"just figure it out"* — that's an instruction to brainstorm, not to skip. |

If a reasonable engineer could choose wrongly from the prompt, brainstorming applies.

## The 5-axis exploration framework

"5-axis" is the historical name. Walk all axes below, starting at Axis 0. Only Axis 0's negative guard may skip its upstream-artifact walk; its ready check still runs. Record unknowns in the brief's Open Questions.

When user input is necessary, ask **at most one axis per `AskUserQuestion` call**: the highest-uncertainty axis.

Make the rendered question self-contained:

- Put a **one-line state anchor** in the `question` field: what is settled and what remains open.
- Use **Outcome, not mechanism**: options describe what the user gets, without axis numbers, internal labels, or cluster names.
- Give numbers and symbols plain-language meaning; keep bare counts out of headlines.

Axis 1 avoids re-asking a confident interpretation; Axis 4 brings a researched recommendation rather than an empty choice.

For a complex fork, follow `loom-code/hooks/family-reception.md §Brief before a complex fork`: run `loom-workflow:brief-before-asking` before `AskUserQuestion`. Per `family-relay.md`, show ≥2 options in a markdown comparison table unless the ask is a trivial binary.

### Axis 0 — Upstream artifacts (family §Intake)

Before Axis 1, check the target repo against **the loom family reception's** on-ramp criteria (`loom-code/hooks/family-reception.md`); it owns the table.

**Negative guard (silent skip)**: skip the upstream-artifact walk for a bug fix, refactor, or test-covered increment. The **Backlog ready check** runs regardless. Continue the full walk only for product-shaped, user-facing, or multi-state new work.

**Backlog ready check** — if `docs/loom/backlog/` exists, run `python3 scripts/backlog_index.py --ready` before fixing scope; surface `bet` items and related `open` items. Prefer the repo script, else run:
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/backlog_index.py" --ready`
`${CLAUDE_PLUGIN_ROOT}` is load-time substitution: no store, or neither copy of `backlog_index.py` → skip silently, N/A. The queue informs the arc decision; it never hijacks it, and the user's seed remains the default subject. This check is independent of the Negative guard (backlog entries are often exactly bug-fix shaped).

**No queue layer yet** — only when both `docs/loom/backlog/` and `docs/loom/KICKOFF-DEFAULTS.md` are absent, offer scaffolding **ONCE** via:
`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/loom_init.py"`
This plugin-only bootstrap uses load-time substitution and refuses if either artifact exists. If declined or ignored, proceed and never re-raise it. Below the `## Design-side on-ramp` value line record:
`Loom-init offer: offered — user chose <scaffold/decline>`. Never write
it as the value itself; that line accepts only the four canonical forms. When neither copy of `backlog_index.py` resolves, stay N/A as today; the scaffold ships alongside it, so there is no offer to make.

If a criteria row triggers, first read `docs/loom/KICKOFF-DEFAULTS.md` `## On-ramp standing choices`. If every row has a standing choice, record `fired: rows <n> — standing <direct|detour> (KICKOFF-DEFAULTS.md)` and continue. Otherwise record `pending`, then ask **ONCE** in a standalone ask that recommends and names the concrete sequence (for example `using-loom-design`). After the answer, record `fired: rows <n> — user chose <detour|direct>` per `references/handoff-brief-format.md`; never invent a default or re-ask.

### Axis 1 — Problem

Identify the problem behind the proposed solution and its measurable success criteria. Use Christensen et al. (2016), *Competing Against Luck*'s Jobs-To-Be-Done framing: articulate the job before the product.

One requested feature may hide different jobs: sharing daily numbers with a non-technical stakeholder, backing up data before deletion, or feeding a downstream pipeline. Do not treat the proposed interface as the job; each underlying purpose implies different acceptance criteria.

If context gives a confident JTBD read, state `I read this as X — correct me if wrong` and proceed to Axis 4. Reserve `AskUserQuestion` for genuine ambiguity.

### Axis 2 — Users

Identify specific users, conditions, tools, and constraints. Combine Axes 1+2 with Klement's job-story format: `When [situation], I want to [motivation], so I can [outcome].`

Be concrete enough to distinguish, for example, an internal analyst copying SQL results into Sheets under installation restrictions from an external API consumer running nightly ETL. Their tooling and stability needs produce different designs.

### Axis 3 — Smallest End State

Define the *minimum shippable* end state. Challenge the first proposed solution; for example, a CSV query parameter may solve an export need without UI. Delegate suspected accidental complexity to `loom-workflow:complexity-critique`.

Shrink systems as well as features: one environment variable may replace a proposed feature-flag system, and extracting only the email-notification path may unblock a bug without refactoring an entire service. Explicitly defer the rest rather than leaving an implied expansion.

### Axis 4 — Alternatives Considered (**research-grounded, not imagined**)

Enumerate 2–3 shipped alternatives and why each was rejected so the chosen trade-off survives context loss.

**Research shipped options, not imagined ones.** Per round, WebSearch at least **one English AND one Japanese** query. Cite and label both languages; agreement strengthens evidence, while **disagreement between EN and JA is itself a finding**. Lead with a recommendation.

**Output format** — lead with the "My take: Recommend / Why / Conditional reversal" block, then surface each alternative with source + pros/cons + who ships it. Concrete template in [`references/axis4-research-protocol.md`](references/axis4-research-protocol.md) §Output format.

Use [`references/axis4-research-protocol.md`](references/axis4-research-protocol.md) for query patterns, unavailable-search handling, edge cases, anti-patterns, and the template. Router rule #5 applies it to decisions outside Axis 4 too.

### Axis 5 — What Becomes Obsolete

Name code, process, or conventions made redundant and remove them in the same change. If nothing becomes obsolete, check for additive YAGNI or incomplete exploration.

Count documentation and operational procedures too: a new export endpoint can obsolete a copy-paste runbook, while a new flag must replace—not coexist indefinitely with—the hardcoded behavior. Ask whether a new helper merely covers for an API that should instead be corrected.

Pair this forward-looking axis with backward-looking `## Current State Evidence`. Both use a path plus verbatim-string or stable-heading anchor; add a line number only when ambiguous. See the handoff format.

## Output Contract — the brief

Brainstorming's deliverable is a **structured brief** that `writing-plans` consumes. Schema in [`references/handoff-brief-format.md`](references/handoff-brief-format.md); minimum required sections:

```markdown
## Design-side on-ramp
(Axis 0 — one line in the canonical grammar; SSOT `references/handoff-brief-format.md`)

## Problem
(Axis 1 — the JTBD-style job behind the user's request)

## Users
(Axis 2 — who specifically, in what conditions)

## Smallest End State
(Axis 3 — minimum shippable resolution)

## Current State Evidence
(Required when touching existing code. Five sub-bullets — Forward / Reverse / Error / Data / Boundary — each citing a path plus an anchor: a verbatim string or stable heading. A line number is optional precision only when the anchor is ambiguous. Choose the anchor by artifact type using [`references/handoff-brief-format.md`](references/handoff-brief-format.md) §Current State Evidence; plus Evidence paths appendix. `N/A — greenfield` allowed only for truly greenfield work. Agent fills via grep / Read / Explore; user reviews — same model as Axis 4 research.)

## Decision
(One paragraph: what we will build, what we will NOT build, why)

## Out of Scope
(Bulleted list of adjacent things explicitly NOT in this change)

## Queue relation
(grammar SSOT `references/handoff-brief-format.md` — write the line there, do not leave it `pending`)
```

Optional but recommended sections: What Becomes Obsolete (Axis 5), Open Questions. `## Alternatives Considered` (Axis 4) and `## Diagrams` are fill-or-declare — see `references/handoff-brief-format.md`.

The brief lands in the user's repo at `docs/loom/specs/<date>-<topic>.md`.

**Before handoff, self-check the brief**: run `python3 loom-code/scripts/check_field_microstructure.py --brief <brief-path>`. Exit 0 is clean. Exit 1 names a paragraph violating `references/handoff-brief-format.md`'s rule (or reports the path as unreadable) — fix it before handing off, not after `writing-plans` catches it. Exit 2 means the file has no `## ` sections at all, so nothing was scanned: supply the brief's structure, and do not read it as a pass.

**Plain language in the summary message**: the chat message you send the user after brainstorming must use plain descriptions ("the distribution script now owns SSOT for module X"), not internal identifiers (`Option B`, `Finding #2`, `Q-v0.3-1`, cluster names). Those identifiers are shorthand for *you*; the user needs the human-readable meaning. The brief *file* may keep precise identifiers for `writing-plans` consumption. Relaying this summary and any diagrams: see `loom-code/hooks/family-relay.md §Family relay discipline`.

**Reverse sub-bullet (SSOT ownership)**: before writing the Reverse sub-bullet, `Read` the distribution/sync script (e.g. `distribute.py`, `sync.sh`) to confirm which module owns canonical SSOT and which direction data flows. Never infer the direction from folder hierarchy alone — the file structure is often misleading.

### Greenfield UI-state nudge

This nudge fires **only** when **both** hold: (a) Current State Evidence is `N/A — greenfield` or thin (no pre-existing recon to lean on), **AND** (b) the feature has a UI / interaction / stateful surface (something a user clicks, types into, navigates, or watches change over time). When both are true, before finalizing the brief **enumerate the UI states across these six categories**: **empty / error / loading / state-transition / permission / boundary**. Greenfield is exactly where these get silently dropped — there is no Current-State-Evidence recon to surface them, so the happy path is all that gets written down.

It does **not** fire in brownfield (the Current-State-Evidence recon — Forward / Reverse / Error / Data / Boundary — already walks these touch points) and **not** for pure-logic / data-only features with no interactive surface.

**DRY guardrail** — this is a category *reminder only*: enumerate which of the six states the feature has, don't model them. The full method (BVA / state-machine modeling / permission matrix, with keep-flag-drop discrimination per lens) lives in `loom-design:spec-expansion`; **do not reproduce it here**.

## Red Flags — refuse these rationalizations

Rationalizations that push to skip discovery — *"this is simple," "I know what to build, let's just start," "let's just start coding and see," "the user already gave me a spec," "it's just refactoring," "I'll fill Current State Evidence from memory," "it's greenfield, skip Evidence"* (and localized variants 「太簡單了 / 簡単すぎる」). Refuse each; walk Axis 1+2 minimally, then name a §When NOT to Use exemption only if the task is genuinely trivial after. Full table (rationalization → why it is one → correct response) in [`references/red-flags.md`](references/red-flags.md).

## Cross-skill delegation

| When | Delegate to | Why |
|---|---|---|
| Axis 3 surfaces "this change might be bigger than necessary" (smell of accidental complexity / YAGNI) | `loom-workflow:complexity-critique` | Systematic deletion-first triage (three questions: smallest end state / before-after LOC / what becomes obsolete). Optional but strongly recommended. |
| Axis 4 produces 3+ real options that need triage | `loom-workflow:proposal-critique` | Evidence-grounded KEEP / DEFER / DROP triage. Optional. |
| Brainstorming output indicates work >1 hour OR >1 module | `writing-plans` (next stage) | Brief becomes the input to plan-splitting. Before delegating, surface Axis 1 + Axis 3 (smallest end state) + Out-of-Scope as a visible checkpoint and require explicit user sign-off — do not proceed on an implicit "ok continue." Per the firing conditions in [`../using-loom-code/protocols/adjudication-view.md`](../using-loom-code/protocols/adjudication-view.md), produce the brief's document view before requesting sign-off. |
| Brainstorming output indicates a simple one-line known-pattern fix | Skip writing-plans; route straight to `tdd-iron-law` | The brief documented the smallness; trust it. |
| Greenfield UI feature needs **high-coverage / high-risk** state fan-out (beyond the inline six-category reminder) | `loom-design:spec-expansion` | Runs the full lens (USM / OOUX / auto-expansion matrix) on a sparse seed. **Active / wired**: `writing-plans` now reads loom-design change-folders (see its **§Consuming a loom-design change-folder**), so the full spec can flow spec→plan→code. Use the inline §Greenfield UI-state nudge for lightweight cases; escalate to `loom-design:spec-expansion` (→ a validated change-folder) for the high-coverage path. |

Delegation contract (see CLAUDE.md cross-plugin section): pass **paths + structured seed context**, not full file content. The target skill loads its own resources.

## Visual companion

For non-trivial system design — especially when axes 1+2 (problem + users) need a flow / interaction diagram, or axis 5 (what becomes obsolete) needs an architecture-before-and-after — see [`references/visual-companion.md`](references/visual-companion.md). The companion documents when a Mermaid sequence / C4 / ER diagram pays for itself vs when prose is enough.

Flow / state diagrams in briefs and user-facing summaries are GENERATED via `ascii-graph-toolkit` (or Mermaid where the channel renders it) — never hand-drawn box art. SSOT for the channel rule: `loom-code/hooks/family-relay.md §(b) Visual defaults`.

## What this skill does NOT do

- Does **not** write code. The brief is text + diagrams; implementation starts in `writing-plans` → SDD → `tdd-iron-law`.
- Does **not** make the final decision for the user. It surfaces the 5 axes so the *user* can decide intelligently. The agent's role is to enforce the framework, not to choose.
- Does **not** replace `loom-workflow:complexity-critique`. complexity-critique runs deletion-first against a specific proposal; brainstorming runs discovery against an open problem. Sequence: brainstorming first, complexity-critique invoked on demand from inside brainstorming.
- Does **not** require all 5 axes to surface novel content. Sometimes Axis 4 returns *"no real alternatives — the problem space is narrow"* and that is a valid output. The discipline is walking the axes, not generating volume.

## See also

- [`references/visual-companion.md`](references/visual-companion.md) — when to reach for diagrams.
- [`references/handoff-brief-format.md`](references/handoff-brief-format.md) — output schema for `writing-plans` consumption.
- [`references/axis4-research-protocol.md`](references/axis4-research-protocol.md) — full Axis-4 research protocol (bilingual query patterns, edge cases, anti-patterns).
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; routes to this skill at Stage 1 (Discovery) of any coding task.
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — the discipline that fires once implementation begins.
- `loom-workflow:complexity-critique` — optional delegation target when Axis 3 surfaces complexity smell.
- `loom-workflow:proposal-critique` — optional delegation target when Axis 4 surfaces multi-option triage.
