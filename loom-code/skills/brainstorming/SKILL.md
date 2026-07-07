---
name: brainstorming
description: |
  Use BEFORE implementing new behavior or non-obvious design — explore intent + alternatives via an upstream-artifact gate (Axis 0, family §Intake) + 5-axis framework (Problem / Users / Smallest End State / Alternatives / Obsoletes) → a brief. Refuses 'this is simple' / 'just start coding'.
version: 0.12.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt (implementer / spec-reviewer / code-quality-reviewer / code-reviewer), the parent orchestrator already finished discovery. **Do not** re-route through this skill. Follow your dispatched prompt directly.
</SUBAGENT-STOP>

## The HARD-GATE

> **DO NOT START IMPLEMENTING UNTIL YOU HAVE EXPLORED INTENT.**

This is not a guideline. The pressure to skip — *"this is simple,"* *"I know what to build,"* *"let's just start coding"* — is exactly the failure mode this skill exists to prevent. **The first 5 minutes of brainstorming saves the next 50 minutes of building the wrong thing and the 500 minutes of refactoring out of it.**

If you catch yourself drafting code, opening files, or reaching for the Skill tool to call `tdd-iron-law` *before* the user has answered the axes below (Axis 0 through Axis 5) — **stop**. Return to this skill. Beck's *"if it's hard to test, it's probably hard to use"* (Preface, 2002) has a discovery-phase analogue: *if it's hard to articulate what success looks like, it's probably the wrong target.*

### What counts as "before implementation"

| Phase | Iron-Law on TDD applies? | brainstorming applies? |
|---|---|---|
| User says *"add feature X"* | Not yet (no code being written) | **YES — start here** |
| Brief sketched, plan being drafted | Not yet | Skill complete; hand off to `writing-plans` |
| writing-plans split into atomic tasks | Each task triggers it | Skill complete |
| implementer subagent dispatched | YES — Iron Law applies | Skill complete (subagent has the brief in its prompt) |

If you are in the first row and the task is non-trivial (touches new behavior, new module boundary, or non-obvious design space), this skill is **mandatory** before anything else.

## When NOT to use

Narrow, enumerated exemption list. If your task is **not** on this list, the HARD-GATE applies.

| Exempt category | What qualifies | What does NOT qualify |
|---|---|---|
| **One-line known-pattern fix** | Typo in a string literal; bumping a version number in `package.json`; flipping a documented config value (no behavior change for the user). | A "small change" that touches behavior (e.g. retries: 3 → 5 — that's a retry-policy decision, not a config tweak). |
| **Pure refactor under existing test coverage** | Rename a private function; extract a method while all existing tests stay green. | Architecture-shifting refactor (extract a new module boundary, replace a synchronous call with an event). |
| **Bug fix where the failing test already exists** | A test is RED reproducibly; you know which line is wrong. | A bug where *"the test should fail but doesn't"* (false-green diagnostic; see `tdd-iron-law/SKILL.md` §False-green diagnostic). |
| **Explicit user override** | User says *literally* "skip brainstorming, here's the spec, go" AND hands in a written spec / plan that already covers the 5 axes. | User says *"just figure it out"* — that's an instruction to brainstorm, not to skip. |

When uncertain, ask: *"Could a reasonable engineer pick the wrong solution from the user's prompt as written?"* If yes, you are in brainstorming scope.

## The 5-axis exploration framework

"5-axis" is the framework's historical name; the walk itself now starts one step earlier. Walk all axes below, starting at Axis 0 — a mandatory member of the walk (its own negative guard is the only sanctioned skip). Don't skip any. If an axis returns *"don't know"* or *"need more from user"* — that is itself a discovery output and goes into Open Questions in the brief.

When axis uncertainty requires user input, ask **at most one axis per `AskUserQuestion` call** — the single highest-uncertainty one. Bundling multiple axes (e.g. Axis 1 + Axis 3 + Axis 4 with 3-4 options each) overloads the call and will be rejected by the harness as too many options.

When that axis question fires, phrase it for the warm-but-interrupted user who reads the rendered question, not your chat preamble:

- **Open with a one-line state anchor inside the `AskUserQuestion` `question` field** — *here's what we've settled, here's the axis still open.* The anchor must live in the `question` field itself, not only in prose above the call; the user sees the rendered menu first. A bare axis prompt («Which approach?» with no context) is the failure.
- **Outcome, not mechanism.** Each option says what the user *gets* or which design direction it commits to ("ship CSV as a URL query param, no UI work"), not the internal machinery — no axis numbers, no "Option B", no cluster names.
- **Numbers (and symbols) carry their meaning.** Translate raw counts and jargon into plain words in the option text: "3 industry approaches found" → "the three ways teams actually ship this"; let any bare count sink to a sub-line, never the headline.

These three join the two gates already woven into the axes: gate ① (ask only when genuinely uncertain) lives in **Axis 1** as the confident-JTBD-read rule — state a confident reading as a committed interpretation rather than re-asking — and gate ② (bring a recommendation, not an open question) lives in **Axis 4** as the research-then-"My take: Recommend / Why / Conditional reversal" protocol; together the three read as one coherent set.

**Above all — lead with the stakes, and brief first when the fork is complex.** The framing rules above make the *options* legible; they do not guarantee the user grasps *why they are being asked*. Before the options, the `question` field's first line must say, in plain words, *what this choice changes for the user and why it matters* — not just what the options are (a user can read three well-framed options and still not see the point). And when the fork is genuinely complex (≥3 trade-offs, ≥2 implementation paths, or architectural blast radius), **brief before you ask**: run `dev-workflow:brief-before-asking` (Mental Model → My take) first, then fire the `AskUserQuestion`. That skill is the canonical source for this framing; the rules here are its in-workflow shorthand.

### Axis 0 — Upstream artifacts (family §Intake)

Before Axis 1, check the target repo against **the loom family reception's**
on-ramp criteria table (`loom-pipeline/hooks/family-reception.md`) — point to
it, never copy its rows here (SSOT: that file owns the table body).

**Negative guard (silent skip)**: if the work is a bug fix, a refactor, or a
test-covered increment, Axis 0 is skipped silently — no noise on incremental
work. Only proceed past this guard for product-shaped / user-facing /
multi-state new work.

If a criteria row triggers, surface the recommendation **ONCE** — name the
concrete design-side sequence (e.g. `using-loom-product-principles` →
`using-loom-interface-design` → `using-loom-spec`, whichever rows fired), then
record the user's choice in the brief under a `## Design-side on-ramp` line
("offered — user chose <direct/detour>") and proceed either way.
Never re-raise it after a decline — the recommend-once rule holds for the
rest of this task.

### Axis 1 — Problem

What is the user trying to accomplish? **Not the solution they proposed — the problem behind the solution.**

If the user says *"add a CSV export button,"* the problem is not *"have a button."* It might be *"share daily numbers with a non-technical stakeholder who lives in Excel,"* OR *"backup data before deletion,"* OR *"feed data into a downstream pipeline."* Each problem has different success criteria.

Grounded in: **Christensen, C.M., Hall, T., Dillon, K., & Duncan, D.S. (2016) *Competing Against Luck*, Harper Business** (and the HBR companion "Know Your Customers' Jobs to Be Done", Sept 2016) — the Jobs-To-Be-Done framing: *"customers don't buy products; they hire them to do a job."* Articulate the job before the product. (Note: this framing is **not** in *The Innovator's Dilemma* (1997), which is about disruption — a common misattribution; JTBD's origin is also contested with Ulwick's Outcome-Driven Innovation, HBR 2002.)

When session context gives a confident JTBD read (e.g. the user's prior messages or inline comment already name the job), state it as a committed interpretation — *"I read this as X — correct me if wrong"* — and proceed to Axis 4. `AskUserQuestion` fits genuine cold-start ambiguity; re-presenting an already-confident prose reading as a multiple-choice menu wastes a turn and signals the agent isn't listening.

### Axis 2 — Users

Who specifically? Under what conditions? With what existing tools and constraints?

*"Internal data analysts who currently export by SQL-copy-paste to Sheets, on a daily cadence, blocked by IT from installing new desktop tools"* is a different design than *"external API consumers who need a stable CSV format for nightly ETL."*

Grounded in: **Klement, A. (2018) *When Coffee and Kale Compete*, ISBN 978-1718626751** — job story format: *"When [situation], I want to [motivation], so I can [expected outcome]."* Use this format when articulating Axis 1+2 together.

### Axis 3 — Smallest End State

What is the *minimum* shippable end state that solves the problem? Defaulting to the user's first-suggested solution is a smell — the first solution is usually bigger than necessary.

Examples of "smaller than first ask":
- *"Add a CSV export button"* → smallest may be: *"add a `?format=csv` query param to the existing report URL"* (no UI work at all).
- *"Add a feature-flag system"* → smallest may be: *"add one env var + a hardcoded list check"* (defer the whole flag system).
- *"Refactor `OrderService`"* → smallest may be: *"extract just the email-notification subset that's blocking the current bug"* (defer the rest).

This axis often delegates to `dev-workflow:complexity-critique` for systematic deletion-first triage. See §Cross-skill delegation.

### Axis 4 — Alternatives Considered (**research-grounded, not imagined**)

What are 2-3 other ways this could be solved, and why were they rejected? Force the user (or yourself, in conversation with the user) to enumerate.

The point is not to pick from the alternatives — it is to make the chosen path's trade-offs visible. *"We picked X over Y because Z"* is a sentence that survives 6 months of context loss; *"X is the obvious choice"* does not.

**Research the SHIPPED options, not imagined ones.** Run **WebSearch** for what the industry currently does — the agent's training data is frozen, so *"alternatives I can imagine"* produces hallucinated libraries / deprecated patterns. Per round, search **at minimum one English AND one Japanese** query (single-language is sampling bias; JA blogs / post-mortems often cover what EN misses). EN+JA agreement is a stronger signal — and **a disagreement between EN and JA is itself a finding** worth surfacing, not a tie to resolve silently. End in an explicit recommendation ("my take"), citing sources in **both languages**, each labeled by source language.

**Output format** — when surfacing alternatives to the user:

```
Industry approaches found (3, via WebSearch):

1. <Approach name> — <source citation, e.g. RFC 6585, Cloudflare blog, Stripe API docs>
   • Pros: <2-3 bullets>
   • Cons: <2-3 bullets>
   • Used by: <named vendors / open-source projects>

2. <Approach name> — <source>
   ...

3. <Approach name> — <source>
   ...

My take (given your context):
  Recommend: <approach #N>
  Why: <1-2 sentences tying recommendation to user's brief + constraints>
  Conditional reversal: <if X changes, prefer approach #M instead>
```

Full protocol — the bilingual query-pattern tables, the why-both-languages rationale, WebSearch-unavailable handling, the "only ≤3 alternatives exist" case, and the anti-patterns — in [`references/axis4-research-protocol.md`](references/axis4-research-protocol.md). That protocol is also referenced by **router rule #5** (Research before asking) for decisions arising outside Axis 4 (e.g. an SDD implementer asking "which retry strategy?" mid-execution).

### Axis 5 — What Becomes Obsolete

What existing code / process / convention does this make redundant? Anything that becomes obsolete and is **not removed in the same change** is technical debt by design.

Examples:
- New CSV export endpoint → the documented Sheets-copy-paste runbook becomes obsolete; delete it in the same PR.
- New feature flag → the hardcoded behavior it replaces becomes obsolete; remove it in the same PR.
- New helper function → if it's covering for an existing API's shortcomings, can the existing API be improved instead?

If nothing becomes obsolete, that is a flag: either the change is purely additive (probably YAGNI — see `dev-workflow:complexity-critique`) or the design space wasn't explored enough.

**Pairs with `## Current State Evidence` in the brief**: Axis 5 is forward-looking (what gets removed); Current State Evidence is backward-looking (what currently exists at the touch points). The same `file:line` citations often serve both — the recon you do to fill Evidence is the same recon that surfaces obsolescence candidates here. See [`references/handoff-brief-format.md`](references/handoff-brief-format.md) §Current State Evidence for the format.

## Output Contract — the brief

Brainstorming's deliverable is a **structured brief** that `writing-plans` consumes. Schema in [`references/handoff-brief-format.md`](references/handoff-brief-format.md); minimum required sections:

```markdown
## Problem
(Axis 1 — the JTBD-style job behind the user's request)

## Users
(Axis 2 — who specifically, in what conditions)

## Smallest End State
(Axis 3 — minimum shippable resolution)

## Current State Evidence
(Required when touching existing code. Five sub-bullets — Forward / Reverse / Error / Data / Boundary — each citing file:line; plus Evidence paths appendix. `N/A — greenfield` allowed only for truly greenfield work. Agent fills via grep / Read / Explore; user reviews — same model as Axis 4 research.)

## Decision
(One paragraph: what we will build, what we will NOT build, why)

## Out of Scope
(Bulleted list of adjacent things explicitly NOT in this change)
```

Optional but recommended sections: Alternatives Considered (Axis 4), What Becomes Obsolete (Axis 5), Open Questions.

The brief lands in the user's repo at `docs/loom/specs/<date>-<topic>.md`.

**Plain language in the summary message**: the chat message you send the user after brainstorming must use plain descriptions ("the distribution script now owns SSOT for module X"), not internal identifiers (`Option B`, `Finding #2`, `Q-v0.3-1`, cluster names). Those identifiers are shorthand for *you*; the user needs the human-readable meaning. The brief *file* may keep precise identifiers for `writing-plans` consumption. Relaying this summary and any diagrams: see `loom-pipeline/hooks/family-relay.md §Family relay discipline`.

**Reverse sub-bullet (SSOT ownership)**: before writing the Reverse sub-bullet, `Read` the distribution/sync script (e.g. `distribute.py`, `sync.sh`) to confirm which module owns canonical SSOT and which direction data flows. Never infer the direction from folder hierarchy alone — the file structure is often misleading.

### Greenfield UI-state nudge

This nudge fires **only** when **both** hold: (a) Current State Evidence is `N/A — greenfield` or thin (no pre-existing recon to lean on), **AND** (b) the feature has a UI / interaction / stateful surface (something a user clicks, types into, navigates, or watches change over time). When both are true, before finalizing the brief **enumerate the UI states across these six categories**: **empty / error / loading / state-transition / permission / boundary**. Greenfield is exactly where these get silently dropped — there is no Current-State-Evidence recon to surface them, so the happy path is all that gets written down.

It does **not** fire in brownfield (the Current-State-Evidence recon — Forward / Reverse / Error / Data / Boundary — already walks these touch points) and **not** for pure-logic / data-only features with no interactive surface.

**DRY guardrail** — this is a category *reminder only*: enumerate which of the six states the feature has, don't model them. The full method (BVA / state-machine modeling / permission matrix, with keep-flag-drop discrimination per lens) lives in `loom-spec:spec-expansion`; **do not reproduce it here**.

## Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"This is simple, no need to brainstorm."* | The framing *"this is simple"* almost always means *"I have already picked a solution and am defending against discovery friction."* | Refuse. Walk Axis 1+2 with one clarifying question each; if both come back trivial, the §When NOT to Use exemption may apply — name it explicitly. |
| *"I know what to build, let's just start."* | Same rationalization, agent-side. Common after the user has framed the task and the agent feels the cost of asking back. | Refuse. Articulate Axis 3 (smallest end state) in writing first; if it matches the user's first ask exactly, the discovery was redundant — but the writing-down made it visible. |
| *"Let's just start coding and see what happens."* | Iterative-prototyping rationalization. Discovery and prototyping are different — prototyping happens INSIDE the smallest end state, not in place of articulating one. | Refuse. The smallest-end-state articulation is the prototype-scope decision; do that first. |
| *"The user already gave me a spec."* | Maybe — but specs that skip Axis 4 (alternatives) and Axis 5 (what becomes obsolete) leave the agent unable to make follow-on decisions intelligently. | Read the spec against the 5 axes. If any axis is empty, ask the user — do not invent. |
| *"It's just refactoring, no new behavior."* | Refactoring under existing test coverage is the §When NOT to Use exemption — but architecture-shifting refactor (new module boundary, new contract) is NOT covered by that exemption. | Distinguish: rename / extract-under-coverage = exempt; new boundary / new contract = brainstorm. |
| *「太簡單了不用討論 / 簡単すぎる / こんな簡単な話」* | Same rationalization, localized. | Same refusal — walk the 5 axes minimally; if trivial after, name the §When NOT to Use exemption. |
| *"I'll fill Current State Evidence from memory."* | Hallucinated reconnaissance. The whole point of the section is grounded `file:line` citations; bullets without them defeat it. | Refuse. Run `grep` / `Read` / dispatch `Explore` first; quote what you actually read. If the codebase is unfamiliar enough that recon is genuinely expensive, surface that as an Open Question — do not invent. |
| *"It's greenfield, skip Current State Evidence."* | Valid only when nothing pre-existing is touched (new module from scratch, no integration points). Adding a method to an existing class, integrating with an existing API, or extending existing config is NOT greenfield. | Distinguish honestly. If any touch point is pre-existing, fill the relevant sub-bullets and mark only the irrelevant ones `N/A`. |

## Cross-skill delegation

| When | Delegate to | Why |
|---|---|---|
| Axis 3 surfaces "this change might be bigger than necessary" (smell of accidental complexity / YAGNI) | `dev-workflow:complexity-critique` | Systematic deletion-first triage (three questions: smallest end state / before-after LOC / what becomes obsolete). Optional but strongly recommended. |
| Axis 4 produces 3+ real options that need triage | `dev-workflow:proposal-critique` | Evidence-grounded KEEP / DEFER / DROP triage. Optional. |
| Brainstorming output indicates work >1 hour OR >1 module | `writing-plans` (next stage) | Brief becomes the input to plan-splitting. Before delegating, surface Axis 1 + Axis 3 (smallest end state) + Out-of-Scope as a visible checkpoint and require explicit user sign-off — do not proceed on an implicit "ok continue." |
| Brainstorming output indicates a simple one-line known-pattern fix | Skip writing-plans; route straight to `tdd-iron-law` | The brief documented the smallness; trust it. |
| Greenfield UI feature needs **high-coverage / high-risk** state fan-out (beyond the inline six-category reminder) | `loom-spec:spec-expansion` | Runs the full lens (USM / OOUX / auto-expansion matrix) on a sparse seed. **Active / wired**: `writing-plans` now reads loom-spec change-folders (see its **§Consuming a loom-spec change-folder**), so the full spec can flow spec→plan→code. Use the inline §Greenfield UI-state nudge for lightweight cases; escalate to `loom-spec:spec-expansion` (→ a validated change-folder) for the high-coverage path. |

Delegation contract (see CLAUDE.md cross-plugin section): pass **paths + structured seed context**, not full file content. The target skill loads its own resources.

## Visual companion

For non-trivial system design — especially when axes 1+2 (problem + users) need a flow / interaction diagram, or axis 5 (what becomes obsolete) needs an architecture-before-and-after — see [`references/visual-companion.md`](references/visual-companion.md). The companion documents when a Mermaid sequence / C4 / ER diagram pays for itself vs when prose is enough.

## What this skill does NOT do

- Does **not** write code. The brief is text + diagrams; implementation starts in `writing-plans` → SDD → `tdd-iron-law`.
- Does **not** make the final decision for the user. It surfaces the 5 axes so the *user* can decide intelligently. The agent's role is to enforce the framework, not to choose.
- Does **not** replace `dev-workflow:complexity-critique`. complexity-critique runs deletion-first against a specific proposal; brainstorming runs discovery against an open problem. Sequence: brainstorming first, complexity-critique invoked on demand from inside brainstorming.
- Does **not** require all 5 axes to surface novel content. Sometimes Axis 4 returns *"no real alternatives — the problem space is narrow"* and that is a valid output. The discipline is walking the axes, not generating volume.

## See also

- [`references/visual-companion.md`](references/visual-companion.md) — when to reach for diagrams.
- [`references/handoff-brief-format.md`](references/handoff-brief-format.md) — output schema for `writing-plans` consumption.
- [`references/axis4-research-protocol.md`](references/axis4-research-protocol.md) — full Axis-4 research protocol (bilingual query patterns, edge cases, anti-patterns).
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; routes to this skill at Stage 1 (Discovery) of any coding task.
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — the discipline that fires once implementation begins.
- `dev-workflow:complexity-critique` — optional delegation target when Axis 3 surfaces complexity smell.
- `dev-workflow:proposal-critique` — optional delegation target when Axis 4 surfaces multi-option triage.
