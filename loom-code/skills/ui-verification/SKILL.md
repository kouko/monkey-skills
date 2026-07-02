---
name: ui-verification
description: |
  Use AFTER UI code lands and BEFORE the branch closes — drives the real rendered app through every state ui-flows.md enumerates (render variants, flows, entry/exit) using the host's browser/device automation tools. CONDITIONAL: fires only when a ui-flows.md exists AND the branch touched a UI surface; otherwise N/A. Not for package tests (verification-before-completion), not DESIGN.md token conformance (parked), not TUI/CLI (v1 is GUI). Triggers: "verify the UI", "did the screens actually render", 畫面驗證, UI 検証.
version: 0.1.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt, your dispatcher
already decided whether UI verification applies. Follow your dispatched prompt
directly.
</SUBAGENT-STOP>

# ui-verification — drive the real pixels before the branch closes

The 2026-07-03 pipeline dogfood shipped a GUI product whose test suite was
28/28 green while **the rendered half had zero behavioral verification** —
"no live browser was used" (the code station's own ledger). Package tests
verify logic; they cannot verify that the empty state renders, that the error
toast is reachable, that pause actually swaps the controls. This skill is the
runtime gate for that half: **open the real app, walk the states the design
station already enumerated, and report what you observed.**

## The gate is CONDITIONAL — check both conditions first

Mirroring the D8 principles-conformance pattern (`loom-code/agents/code-reviewer.md`):

1. **A `ui-flows.md` exists** for this change — canonically
   `docs/loom/<change-id>/ui-flows.md` (legacy side-by-side `docs/loom/`
   also occurs). It is the checklist: its §1 inventory rows + render-variant
   flags + flows + entry/exit points are what you verify. The design station
   owns that enumeration (do not re-derive it); this skill owns the runtime
   check — the same seam split as the spec→code validator (#442 precedent).
2. **The branch touched a UI surface** — HTML/JSX/templates/styles/DOM
   wiring. A pure-logic branch under a UI-bearing repo does not fire this
   gate.

Either condition false → emit **`ui-verification: N/A`** with the reason and
move on. N/A is a first-class honest outcome, never a silent skip.

## Tooling — use what the host has, and be loud when it has nothing

Resolve the automation surface in this order; the skill is written against
capabilities, not one vendor:

| Modality | Typical host tools |
|---|---|
| Web GUI | `chrome-devtools` MCP (navigate / click / fill / snapshot / screenshot / wait_for), or Playwright-family tooling |
| iOS / Android / macOS app | `agent-device` MCP (boot / open / tap / type / screenshot / snapshot) |
| TUI / CLI | **out of scope for v1** — matches the design station's phase-2 posture; note it and stop |

**No usable tooling → `ui-verification: N/A (no browser/device automation
available in this environment)`.** Never fake it: do not "simulate" a
walkthrough by re-reading the source, do not fabricate observations from what
the code *should* do, do not let a static read stand in for a rendered check.
A faked pass here recreates exactly the hole this skill exists to close. If a
static read is all you can offer, say N/A and say why — the finishing flow
surfaces that honestly to the user.

## Process

1. **Load the checklist.** Read `ui-flows.md`: collect every §1 inventory row
   with its render-variant flags (empty / loading / error / success / …),
   the user flows, and the entry/exit points. Note `critic-found` rows —
   they were added by the design-critic precisely because the writer missed
   them; they are first-class checklist items, not optional extras.
2. **Launch the real app.** Serve/open it the way a user would (static file,
   dev server, simulator build). If launching needs a command, prefer the
   project's declared surface (`AGENTS.md` / README) — same declared-first
   posture as `verification-before-completion`.
3. **Walk the enumeration.** For each inventory row and each flagged variant:
   drive the app into that state through the UI (click / type / wait —
   through real interactions, not by poking internal state), and record one
   observation per state — a screenshot or accessibility/DOM snapshot plus a
   one-line "what I saw vs what the row promises". For flows: walk each
   mermaid flow end-to-end; confirm every entry point lands and no dead-end
   appears that `ui-flows.md` says shouldn't exist.
4. **Classify per state**: `verified` (reached, matches the row) /
   `mismatch` (reached, contradicts the row — e.g. variant missing, dead-end
   present) / `unreachable` (could not drive the app into it through the UI)
   / `untestable` (needs conditions this environment cannot produce — e.g.
   real network failure, OS permission dialogs, **or long real-time waits**:
   a 25-minute timer's end states are `untestable` unless the project exposes
   a test affordance such as a duration override — name the condition, and
   flag the missing affordance as worth adding). If you substitute a weaker
   static check for an undriveable state (e.g. DOM presence instead of the
   real failure path), label it a **half-measure** in the observation — it
   never upgrades the state to `verified`.
5. **Report** with the verdict below. Findings carry `where` (the state/flow
   + the artifact row) and the observation evidence, mirroring the R2
   evidence-citation discipline every loom-code gate uses.

## Verdict — two-valued, machine-readable

- **`NEEDS_REVISION`** — any `mismatch`, or any `unreachable` state whose row
  is not marked as future/deferred in `ui-flows.md`. Resolution: back to the
  implementer (the state is code's to fix) or, if the enumeration itself is
  wrong, flag for the design station — say which.
- **`PASS_WITH_NOTES`** — every driveable enumerated state `verified`;
  `untestable` items listed with their conditions (they are this skill's
  blind-spots section, and the list may be non-empty).

There is deliberately **no bare PASS**: this gate's coverage is **relative to
`ui-flows.md`'s enumeration** — the enumeration itself has blind spots (its
own critic says so), so an unqualified PASS would claim a completeness this
skill cannot see. State coverage as "N of M enumerated states verified;
untestable: …" — never "the UI is verified".

## What this skill is NOT

- **Not the package-test gate.** It complements, never replaces or
  substitutes, `verification-before-completion` — logic verification stays
  with the test suite; this gate covers only what a suite cannot see
  (the rendered runtime).
- **Not DESIGN.md token conformance.** Checking whether the UI's colors /
  spacing / typography match `DESIGN.md`'s tokens is **explicitly out of
  scope** — that machine consumer is deliberately parked with re-triggers
  (loom-interface-design README §Scope, PR #473); this skill must not
  front-run the park. Verify *behavioral states*, not visual token values.
- **Not a design critic.** It never adds states to `ui-flows.md` or judges
  whether the enumeration is good design — omission-hunting is
  `loom-interface-design:design-critic`'s job, upstream.
- **Not a code editor.** Verdict-only role: it observes and reports; fixes
  route back through the implementer.

## Where it runs in the branch flow

Invoked by `finishing-a-development-branch` alongside
`verification-before-completion` (the two verification halves: suite + UI),
and available on demand after any UI-touching SDD task lands. Run it **before
the whole-branch review** when possible, so the reviewer sees the observation
evidence instead of re-deriving UI claims from source.

- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — the package-test sibling gate.
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — the orchestrator that invokes both gates.
- `loom-interface-design:interaction-flows` — produces the `ui-flows.md` this skill drives; `loom-interface-design:design-critic` — enriches it with `critic-found` rows.
