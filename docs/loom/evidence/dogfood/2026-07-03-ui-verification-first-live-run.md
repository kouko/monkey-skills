# ui-verification — first live run (2026-07-03, same session as the skill's birth)

> The skill shipped and was immediately exercised against the pipeline
> dogfood's toy product (`focus-timer`, session scratchpad, branch
> `feat/focus-timer-mvp` — the app whose 28/28-green suite shipped a GUI with
> zero behavioral verification). Executor: the session orchestrator following
> the SKILL.md procedure by hand; roadmap ② close-out evidence.

## Tooling reality (the degradation path got exercised on day one)

- `chrome-devtools` MCP could not connect: the user's long-running main
  Chrome (up since Jun 27) already held `127.0.0.1:9222` answering 404, and a
  freshly launched debug instance could only bind `[::1]` (IPv6) — the MCP
  dials IPv4 only. Killing the user's daily browser was not acceptable.
- Fell back to the skill's own tooling table: **Playwright-family** —
  `puppeteer-core` connected to the headless instance's IPv6 WS endpoint.
  The fallback row earned its place in the table on the first run.

## Result — verdict `NEEDS_REVISION`

19 checklist states driven (ui-flows.md §1 inventory + critic-found rows):
**9 verified / 6 mismatch / 4 untestable**. Evidence: 6 screenshots +
`report.json` (session scratchpad `ui-verify/evidence/`).

Verified (highlights): idle numeral + idle-controls; running-controls swap;
the numeral **actually ticks** (t0≠t+2s) and **actually freezes** when paused
(t0=t+1.5s — behavioral checks a DOM read cannot fake); reset round-trip;
mute toggle draws its `muted` variant with a real accessible label
("Mute end-of-session sound"); an `aria-live` surface exists.

Mismatches (all map to critic-found rows the 5-of-13-requirements task cut
never implemented — the gate caught exactly the shipped-vs-enumerated gap):

| State | Observation |
|---|---|
| PhaseIndicator/work | No Work/Break label anywhere on the page — the surface is absent, not mis-styled |
| landmark/heading structure | No `<main>`, no `<h1>` |
| paused-state cue | Nothing beyond the button swap signals "paused" |
| second-instance cue | Second tab opens silently; no cue (double-fire risk stands) |
| 320px + 200% zoom reflow | Real horizontal overflow (screenshot) — WCAG 1.4.10 gap |
| script-failure fallback | No static fallback text/`noscript` in the DOM (**half-measure check** — the real failure path needs JS-blocked load, classified untestable) |

Untestable, with named conditions: session-end states (ending pulse / toast /
break / sound) need a **25-minute real-time wait — the app exposes no duration
override**; tab-throttle resync; audio-blocked indicator; script-failure
runtime path.

## What the run taught the skill (folded back same-session)

1. **Time-dependent states need a stance**: classified `untestable` with the
   named condition + "flag the missing test affordance as worth adding" —
   now explicit in §Process step 4. A pipeline-produced app should probably
   grow a duration-override affordance at design or plan time; that is a
   candidate enumeration item for interaction-flows, noted for a future pass.
2. **Half-measure labeling**: a static DOM-presence check standing in for an
   undriveable failure path must be labeled a half-measure and never upgrades
   to `verified` — now explicit in §Process step 4.
3. The N/A-loud + tooling-fallback design survived contact with a messy real
   environment (occupied debug port, IPv4/IPv6 split) without faking anything.

## Relation to the pipeline dogfood

The whole-branch review (pipeline station 7) had already flagged 1 🔴 from
source; this gate adds **6 rendered-runtime mismatches invisible to both the
test suite and static review**. Together they close the loop the 2026-07-03
pipeline-driver dogfood opened: suite-green ≠ UI-verified, and now there is a
gate that says so with screenshots.
