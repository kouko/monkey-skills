# Brief — Wire the spec→code seam (loom-spec → loom-code)

> brainstorming hand-off brief. Consumed by `loom-code:writing-plans`.
> Date: 2026-06-21 · Scope locked by user (Option 1): wire spec→code, 1-task-1-PR,
> upstream human-gated + never-auto-merge unchanged.

## Problem

(Axis 1 — JTBD) The user runs the loom- pipeline (principles → design → spec → code)
across real projects. The **implementation half already auto-loops** — loom-code's
Continuous mode runs `brief → plan → SDD → review → verify → PR-open` hands-off. The
job behind "完善整個系列、auto-loop 完成整個實作" is **not** full principles→PR autonomy
(industry + the repo's own doctrine reject automating upstream consensus). It is:
**after I approve a spec, let the work flow straight into the existing auto-loop without
me re-typing intent into brainstorming.** Today that one link is broken.

## Users

(Axis 2) kouko — solo developer (data analyst / app designer), Claude Code host,
building and dogfooding these toolkits on real work. Wants less per-station babysitting
on the mechanical (downstream) half; keeps judgment on the creative (upstream) half.

## Smallest End State

(Axis 3) loom-code's `writing-plans` can take a **human-approved, validated loom-spec
change-folder** as an alternative input to the brainstorming brief, mapping each
`#### Scenario:` (GIVEN/WHEN/THEN) → one task's `Acceptance: RED/GREEN`, and Continuous
mode's freeze accepts that approved change-folder as a valid entry artifact. Each
Scenario = one acceptance criterion = atomic task ⇒ **1-task-1-PR** granularity is
preserved (Mercari's load-bearing precondition for safe spec→code auto-handoff).

**Not** a cross-plugin orchestrator. **Not** auto-running design/spec. **Not** changing
the merge gate. The smallest change that closes the only broken link on the
implementation path.

## Current State Evidence

- **Forward (entry path):** Continuous-mode freeze requires the brainstorming **brief**
  at `docs/loom/specs/<topic>.md` — *"Entry — at the SPEC, not the plan… a human-approved,
  frozen spec exists — concretely the brainstorming hand-off brief"*
  (`loom-code/skills/using-loom-code/SKILL.md:69-72`). `writing-plans` reads **only** that
  brief (`loom-code/skills/writing-plans/SKILL.md:14,25,176`); it has no input path for a
  loom-spec change-folder.

- **Reverse (SSOT ownership):** loom-spec owns the change-folder format end-to-end. It
  emits `docs/loom/<change-id>/{proposal.md, specs/<capability>/spec.md}`
  (`loom-spec/skills/spec-expansion/SKILL.md:287-297`), with the testable contract in the
  `specs/.../spec.md` deltas. Format is enforced by the executable
  `loom-spec/scripts/validate_spec_output.py` (exit 0/1: requires `## ADDED Requirements`,
  a `### Requirement:` with RFC-2119 keyword, ≥1 `#### Scenario:` with GIVEN/WHEN/THEN).
  **loom-code references none of this** — SSOT stays in loom-spec; the wiring must
  *point at* it, not copy it.

- **Error (what happens today):** the seam is **unwired**. No file under `loom-code/`
  reads/parses a change-folder; every hit for `spec-expansion`/`OpenSpec`/`#### Scenario`
  is a deferred forward-pointer or a CHANGELOG/test marker
  (`loom-code/skills/brainstorming/SKILL.md:193`,
  `loom-code/scripts/test_brainstorming_greenfield_nudge.py:157-170`). Pointing
  `writing-plans` at a change-folder today = no handler; it expects a brainstorming brief.

- **Data (the two schemas to map):** Producer — Scenario block
  `#### Scenario: <name>` / `- GIVEN` / `- WHEN` / `- THEN`, parented by
  `### Requirement: <name>` + `The system MUST …` (`spec-expansion/SKILL.md:305-318`; each
  Scenario = 1 testable criterion, L317). Consumer — `writing-plans` task has
  `Acceptance: RED: … / GREEN: …`, atomic ≤5-min ≤1-module
  (`writing-plans/SKILL.md:138-156`). The map (`Scenario → RED/GREEN`) is **named by the
  producer but unimplemented by the consumer** (`spec-expansion/SKILL.md:317-318`).

- **Boundary (seam contract + the friction):** the existing design→spec seam uses
  **point-don't-copy** — link back to the source artifact's named sections, fan out only
  net-new, *"copying creates a second source of truth that drifts"*
  (`spec-expansion/SKILL.md:59-74`). This is the pattern the spec→code wiring mirrors.
  **Two invariants block a naive wiring:** (1) every task needs a `Brief item covered:`
  field traceable to a brainstorming brief, enforced by plan-document-reviewer Check 3
  (`writing-plans/SKILL.md:115,155-156`); (2) Continuous-mode freeze is keyed to the brief
  *path*, not a spec artifact. A change-folder supplies neither. The wiring must resolve
  both without breaking the upstream-human-gate doctrine.

  Evidence paths appendix:
  - `loom-code/skills/using-loom-code/SKILL.md:69-72,78-91` (freeze + STOP contract)
  - `loom-code/skills/writing-plans/SKILL.md:14,25,115,138-156,176`
  - `loom-code/skills/brainstorming/SKILL.md:170,193`
  - `loom-spec/skills/spec-expansion/SKILL.md:59-74,287-318`
  - `loom-spec/scripts/validate_spec_output.py:55-116`
  - `loom-code/CHANGELOG.md:94-96,114-117` (Tier-2 deferral)

## Alternatives Considered

(Axis 4 — research-grounded, EN + JA WebSearch, 2026-06-21)

Industry consensus (both languages agree): **automate the reversible downstream; gate
the irreversible boundaries** — plan/spec sign-off before code, PR review before merge.
No mainstream tool auto-merges feature code by default (Spec Kit, Kiro, Devin, SWE-agent,
OpenHands, Cursor, Copilot, Claude Code all stop at/ before PR). Sources:
[Spec Kit](https://github.github.io/spec-kit/reference/workflows.html),
[Kiro](https://kiro.dev/docs/specs/),
[Claude Code permission modes](https://code.claude.com/docs/en/permission-modes),
[Augment agentic SDLC](https://www.augmentcode.com/guides/agentic-sdlc),
[GitHub Copilot agent](https://github.blog/news-insights/product-news/github-copilot-meet-the-new-coding-agent/).

JA-distinct, load-bearing (Mercari pj-double,
[engineering.mercari.com 2025-12-01](https://engineering.mercari.com/blog/entry/20251201-pj-double-towards-ai-native-development/)):
- Automating upstream **consensus** is harmful — *"合意のない要求から誰も合意していない
  成果物が自動生成される"*. Upstream value = the human approval **record**, not the
  artifact. → keep design/spec human-gated (not for safety; to avoid agreed-by-nobody output).
- spec→code auto-handoff is safe **iff PR/task granularity is minimal (1-task-1-PR)** —
  then AI-code review load ≈ human-code. → the wiring must preserve atomic-task granularity.

Roadmap items with industry backing, **deferred** (conditional reversal): risk-tiered
merge gate (ZOZO Claude×Devin —
[techblog.zozo.com 2026-02-19](https://techblog.zozo.com/entry/ai-driven-dev-with-claude-and-devin),
auth/authz/security always NEEDS_HUMAN); spec-as-SSoT drift detection (DeNA —
[engineering.dena.com 2026-01](https://engineering.dena.com/blog/2026/01/ai-driven-develop/)).

## Decision

Build a **point-don't-copy spec→code adapter inside loom-code** with two coordinated parts:

1. **`writing-plans` gains a second input contract** — a validated loom-spec change-folder
   (`docs/loom/<change-id>/`, `validate_spec_output.py`-clean). It maps each
   `#### Scenario:` → one task's `Acceptance: RED/GREEN`, and **links back** to the source
   via a **stable join key** (R5 — `<change-id> / Requirement: <name> / Scenario: <name>`,
   the checkable traceability referent, à la Kiro `_Requirements:` / Spec-Kit `FR-###`).
   The generalized traceability field (`Brief item covered:` accepts this spec referent;
   no new field) keeps plan-document-reviewer Check 3 intact. **Point-don't-copy carve-out
   (R2/R8 — fact vs interpretation):** the THEN observable / magic values / signatures are
   **facts** → copied verbatim into the RED/GREEN assertion; narrative + design rationale
   are **interpretation** → linked back, not copied. **Consumer read-only (R7):**
   writing-plans MUST NOT modify the producer's change-folder (loom-spec stays SSOT).
   Atomic ≤5-min splitting still applies (one Requirement may fan to several tasks).

2. **Continuous-mode freeze accepts the approved change-folder** as an alternative entry
   artifact alongside the brainstorming brief — entry = *(human-approved spec change-folder,
   validate-clean)* OR *(human-approved brief)*. **Discrimination (R6 — NOT content-shape
   sniffing):** the user **declares** which artifact to run on; the freeze confirms by
   **named-artifact presence** (`specs/<capability>/spec.md` exists at the declared path)
   **and** `validate_spec_output.py` exit 0. This follows both the field (Spec-Kit
   `IF EXISTS`, declared flags) and our own [[feedback_declaration_gate_when_script_cant_infer]]
   learning ("don't fake a fuzzy objective detector — make the agent declare it"). Upstream
   stays human-gated (you approve the spec); STOP contract + never-auto-merge unchanged.

**We will NOT** build a parser/codegen for the mapping — the agent reads GIVEN/WHEN/THEN
and writes RED/GREEN itself (Bitter-Lesson: keep verification scaffolding, drop cognition
crutches). The new executable surface is limited to **tests** asserting the wiring behavior.
**No validator extension needed (R4):** our `validate_spec_output.py` already checks
GIVEN/WHEN/THEN bullets (L101-116) — stricter than OpenSpec's, which only counts `####`
blocks — so reusing it as the freeze gate is sound.

## Out of Scope

- Cross-plugin orchestrator chaining all 4 plugins (principles→design→spec→code).
- Auto-advance across principles→design and design→spec (upstream stays human-gated).
- Risk-tiered merge gate (ZOZO-style) — deferred roadmap item.
- Spec-as-SSoT drift / principles-conformance gate (DeNA-style) — deferred roadmap item.
- Any change to the merge gate (never-auto-merge holds) or the STOP contract semantics.
- A parser/codegen for Scenario→task (kept as agent cognition).

## What Becomes Obsolete

- The Tier-2 "deferred" markers (`brainstorming/SKILL.md:193`, `CHANGELOG.md:114-117`)
  describing this exact wiring as unbuilt — update/remove in the same change.
- The manual step "human re-types spec intent into brainstorming to enter loom-code" —
  removed by part 2.

## Validation round 2 — skill-project patterns (2026-06-21, EN+JA WebSearch + repo reads)

Direct reads of the two ancestors and the field confirm the design is mainstream and has a
named precedent. Canonical pattern names: **Adapter (GoF) + Anti-Corruption Layer (Evans,
DDD)** (consumer-side adapter); **SSOT + DRY / Claim Check (EIP)** (point-don't-copy —
no established name, but = SSOT+DRY); **Just-in-time context loading** (Anthropic) +
**Specification-by-Example** (agent-cognition, no parser); **bounded Tolerant Reader
(Fowler) + Postel's Law** (two-artifact entry). Named precedent for the exact seam:
**`superpowers-bridge` (@JiangWay)** — consumer-side, point-don't-copy, prompt-layer-only.

Honesty notes: (a) NOT "Blackboard" — this is a linear producer→consumer pipeline, no
opportunistic control. (b) NOT "industry-standard handoff" — framework-layer handoff
(CrewAI / AutoGen / OpenAI Agents SDK) defaults to **copying** the full transcript/output;
our reference-handoff aligns with Anthropic context-engineering + JA large-scale ops, so
describe it as **"lightweight reference handoff."** Sources:
[obra/superpowers](https://github.com/obra/superpowers),
[Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec),
[Fowler — Tolerant Reader](https://martinfowler.com/bliki/TolerantReader.html),
[Mercari pj-double](https://engineering.mercari.com/blog/entry/20251201-pj-double-towards-ai-native-development/),
[CyberAgent — file-as-interface](https://developers.cyberagent.co.jp/blog/archives/62110/).

Deferred roadmap (industry-backed, not this slice): spec-drift management (OpenSpec
diff-isolation + archive merge → the parked living-SoT item); Kiro's LLM-formalize →
SMT-check (the one verification-class idea absent here — study only if completeness-critic
misses logical inconsistencies).

## Open Questions — resolved (research-informed)

1. **Traceability field** — RESOLVED: keep the one field `Brief item covered:`; broaden its
   accepted referent to a **stable join key** `<change-id> / Requirement: <name> /
   Scenario: <name>` (R5). One field, checkable reference, Check 3 unchanged.
2. **Freeze artifact discrimination** — RESOLVED (R6, revised from shape-sniffing):
   **user declares** which artifact; freeze confirms by **named-artifact presence**
   (`specs/<capability>/spec.md` at the declared path) **+** `validate_spec_output.py`
   exit 0. No fuzzy content-shape classifier (aligns with the declaration-gate learning).
3. **Multi-Scenario Requirements** — RESOLVED: each `#### Scenario:` → one RED/GREEN; group
   or split per the ≤5-min rule (one `### Requirement:` may fan to N tasks).
