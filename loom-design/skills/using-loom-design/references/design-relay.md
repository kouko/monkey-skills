# Loom Design Relay

Use this local contract whenever loom-design reports progress, presents an
artifact, or decides whether an artifact needs review. Apply the shared
presentation rules in [`family-relay.md`](family-relay.md), then select the
design-specific path below.

## Artifact review routing

- A changed `DESIGN.md` or `ui-flows.md` routes to
  `loom-design:design-critic`. That critic judges the designed surface,
  including missing states, dead ends, accessibility, and UX gaps.
- A changed spec artifact routes to `loom-design:completeness-critic`. That
  critic judges requirement and behavior omissions, not visual quality or
  implementation correctness.
- Ordinary narration, routing, progress, or explanation is not an artifact
  review. Do not invoke a critic merely to relay it.

These routes are local loom-design responsibilities. Never route a design or
spec artifact through a code-review skill.

## Ordinary narration fallback

Ordinary narration is complete without another plugin. Open with a state anchor:
what is true now. Follow with the **stakes**: why that state or choice
matters to the user. Then state what changed and the next action or decision,
using the live conversation language and the shared family-relay rules.

If no artifact review is due, stop there. Do not turn narration into a review
gate and do not require a sibling skill.

## Code handoff boundary

When the requested work genuinely becomes implementation — writing, changing,
reviewing, or shipping code — return to the router's separate public handoff,
`loom-code:using-loom-code`. This transition is not part of design relay and
does not change which critic owns design or spec artifacts.
