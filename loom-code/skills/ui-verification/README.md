# ui-verification

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> **Drive the real rendered app through every state `ui-flows.md` enumerates — before the branch closes.** Born from the 2026-07-03 pipeline dogfood, which shipped a GUI product with a 28/28-green test suite while the rendered half had **zero behavioral verification** ("no live browser was used", per the code station's own ledger). Package tests verify logic; they cannot verify that the empty state renders or that the error toast is reachable.

Part of the [loom-code](../..) plugin. Operational spec the agent loads is [`SKILL.md`](SKILL.md); this README is for humans.

## What this skill does

The runtime gate for the half of a UI change that no test suite can see: open the real app (browser / simulator via the host's automation tools — `chrome-devtools` MCP, Playwright-family, `agent-device` MCP), walk every §1 inventory row, render-variant flag (empty / loading / error / success / …), flow, and entry/exit point that `ui-flows.md` enumerates, and record one observation per state. `critic-found` rows are first-class checklist items — the design-critic added them precisely because the writer missed them. Each state is classified `verified` / `mismatch` / `unreachable` / `untestable`; a weaker static substitute for an undriveable state is labeled a **half-measure** and never upgrades to `verified`.

## When to use

The gate is **CONDITIONAL** — both must hold, checked first:

1. A `ui-flows.md` exists for this change (canonically `docs/loom/<change-id>/ui-flows.md`). It is the checklist; the design station owns the enumeration, this skill owns only the runtime check.
2. The branch touched a UI surface — HTML/JSX/templates/styles/DOM wiring.

Either condition false → emit **`ui-verification: N/A`** with the reason. N/A is a first-class honest outcome, never a silent skip. Same when the host has no browser/device automation: say N/A and why — never fake a walkthrough by re-reading the source.

Invoked by `finishing-a-development-branch` alongside `verification-before-completion` (the two verification halves: suite + UI), and available on demand right after the last UI-touching SDD task lands — the earlier run gives the whole-branch reviewer observation evidence instead of re-derived UI claims.

## When NOT to use

- Pure-logic branch, even in a UI-bearing repo — condition 2 fails, N/A.
- No `ui-flows.md` for the change — condition 1 fails, N/A (this skill never re-derives the enumeration).
- TUI / CLI — out of scope for v1 (matches the design station's phase-2 posture); note it and stop.

## Verdict — two-valued, no bare PASS

- **`NEEDS_REVISION`** — any `mismatch`, or any `unreachable` state not marked future/deferred in `ui-flows.md`. Resolution routes to the implementer, or to the design station if the enumeration itself is wrong — say which.
- **`PASS_WITH_NOTES`** — every driveable enumerated state `verified`; `untestable` items listed with their conditions (the skill's blind-spots section, allowed to be non-empty).

There is deliberately no bare `PASS`: coverage is relative to `ui-flows.md`'s enumeration, which has its own blind spots. State coverage as "N of M enumerated states verified" — never "the UI is verified".

## What this skill does NOT do

- **Not the package-test gate** — complements, never replaces, `verification-before-completion`.
- **Not DESIGN.md token conformance** — colors/spacing/typography checking is explicitly parked (loom-interface-design README §Scope, PR #473); this skill verifies behavioral states, not visual token values.
- **Not a design critic** — never adds states to `ui-flows.md` or judges the enumeration; omission-hunting is `loom-interface-design:design-critic`'s job, upstream.
- **Not a code editor** — verdict-only role; fixes route back through the implementer.

## See also

- [`SKILL.md`](SKILL.md) — operational spec (conditional gate + tooling resolution + 5-step process + verdict rules).
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — the package-test sibling gate.
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — the orchestrator that invokes both gates.
- `loom-interface-design:interaction-flows` — produces the `ui-flows.md` this skill drives; `loom-interface-design:design-critic` — enriches it with `critic-found` rows.
