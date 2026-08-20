---
name: 2026-08-21-lane-level-standing-bet-walk-a-line-without-per-arc-ratification
description: lane-level standing bet — the user bets a LINE of entries once, and agents auto-promote the next entry in that lane at each close-out citing the recorded standing decision; per-arc user-only betting stays the base rule
status: open
origin: 2026-08-21 dissolve-direction-layer brainstorming — the user asked whether agents could walk toward a far PURPOSE more autonomously than one user-ratified bet per arc; adjudicated in conversation, keep user-only as base, design the standing-bet extension later
start: the first real lane of 3 or more entries that needs consecutive arcs walked without per-arc ratification — or the design session on 2026-08-10-loom-lacks-a-milestone-layer-between-plan-stage-and-direction opening, whichever comes first (the two are one design: a lane must be expressible before it can be bet on)
---

- Start: the first real lane of 3 or more entries that needs consecutive
  arcs walked without per-arc ratification — or the design session on
  2026-08-10-loom-lacks-a-milestone-layer-between-plan-stage-and-direction
  opening, whichever comes first (the two are one design: a lane must be
  expressible before it can be bet on)

- Origin: 2026-08-21 dissolve-direction-layer brainstorming — the user
  asked whether agents could walk toward a far PURPOSE more autonomously
  than one user-ratified bet per arc; adjudicated in conversation, keep
  user-only as base, design the standing-bet extension later

- What: keep "agents never promote to `bet`" as the base rule — this
  repo measured 8 agent-defaulted direction choices vs 3 explicit ones
  before the on-ramp choice gate existed (0.87.0 arc origin), and an
  agent optimizing arc-by-arc toward a prose PURPOSE compounds small
  deviations with no error signal, each step self-licensed because the
  same agent writes and satisfies its own `serves:` line. The industry
  answer to per-item ratification fatigue is moving the human decision
  earlier and wholesale, not transferring it: Scrum pulls from a
  PO-ordered backlog without per-item approval; OKR sets the objective
  quarterly and delegates initiative choice.

- Candidate mechanism: a standing bet on a lane, in the same grammar
  family as the on-ramp standing choices (recorded once, cited on every
  use, revoked by editing the record). The user declares once "walk
  this lane's entries in order until done or I stop"; at each close-out
  the agent auto-promotes the lane's next entry, writing the promotion
  reason as a citation of the recorded standing decision (auditable,
  revocable, and every step traces to a real human decision). The
  betting prompt fires again when the lane is exhausted or revoked.

- Blocked on expressibility: loom currently has no artifact that names
  a lane (a `bet` is one entry; themes are just shared words in entry
  names). Design this together with the milestone-layer entry above,
  not before it.
