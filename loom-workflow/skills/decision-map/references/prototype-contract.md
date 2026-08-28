# Prototype contract

## Purpose — the when-to-use test

A prototype ticket answers exactly one question that talking cannot
settle and a lookup cannot answer. Route by where the answer comes
from: discussion settles it → grilling; a lookup settles it →
research; **building-and-measuring settles it → prototype in
feasibility mode** ("can approach A meet constraint C" — the machine
answers); **human reaction settles it → prototype in design mode**
("how should this look / behave" — the human answers). The question is
written in the ticket body before any code exists; a prototype with no
named question is mis-typed.

## Definition — what qualifies

Throwaway code built to answer that one question, in one of three
shapes: a logic probe (state machine / algorithm / data-shape
playground — design mode), a surface probe (UI variants — design
mode), or a **feasibility probe** (a minimal build that measures
whether an approach clears a named constraint: latency, scale, API
capability, integration fit — feasibility mode; the resolution records
the measured numbers or pass/fail, not an impression). Constraints,
all mechanical where possible:

- lives only on its `prototype/<map-id>/<ticket-slug>` branch (the
  prototype branch fence; upstream wayfinder independently converged
  on `prototype/<name>` never-merged branches after reversing its own
  delete-it doctrine — "a prose summary of a prototype loses the thing
  that made it convincing");
- the question is written at the top of the artifact itself (a visible
  intro, not a comment), not only in the ticket;
- **one sitting**: answered in one session; still building a day later
  means the question was too big — split the ticket;
- no tests, no error handling beyond what makes it run, no persistence
  (in-memory state only), no speculative abstraction; **the moment you
  harden one (add a test, wire a real database, generalize for later)
  you have stopped prototyping** — that is the stop signal, not
  progress;
- logic probes isolate the answering logic in a pure portable module
  (reducer / machine / function set, zero DOM reach-in) so the
  validated module itself is the distillable artifact; surface probes
  render variants that disagree **structurally** (layout, hierarchy,
  primary affordance — "three tweaked card grids is wallpaper"),
  hosted inside a real page against real data wherever one exists (a
  variant judged in a vacuum always looks fine);
- must be trivially runnable (one command or one double-clickable
  file) and must surface its state after every action, so a human can
  judge it;
- marked as a prototype in its filenames/entry point — a casual reader
  can tell it is not production code;
- scoped to ONE named question — a whole-app prototype is refused
  ("what is the whole app" is not a question; it has no stopping point
  and becomes production by momentum). Feasibility mode is this
  contract's extension beyond upstream, whose two branches cover
  design questions only.

## Risk-driven front-loading — when a probe is scheduled early

"Research said probably-fine" is not evidence; the map front-loads a
feasibility/prototype ticket onto the frontier when any of these fire
(industry-standard triggers, EN/JA practice agreeing on substance):

- the item cannot be estimated or judged without building — the gap is
  knowledge-limited, not time-limited (XP spike solution; SAFe Spikes;
  JA スパイク practice, ryuzee.com — "誰も見積れないストーリー");
- it is architecturally significant and no proof-of-concept exists yet
  (RUP Elaboration's executable architecture baseline: retire the
  architecturally significant risks first, deliberately partial);
- it carries the map's highest risk exposure (probability × impact) —
  sequence it first, never defer it until reached (Boehm spiral,
  risk-driven ordering);
- the architecture is unproven end-to-end (new integration path, main
  components never yet linked) — a thin walking-skeleton / tracer-bullet
  slice, which loom's SDD standards already prescribe for execution,
  applied here at planning time (Cockburn; Hunt & Thomas);
- one assumption, if false, kills the whole effort — test that one
  first (Riskiest Assumption Test).

Anti-over-prototyping guardrails (same sources): if a conversation or
a lookup can settle it, no probe — spikes are the exception, not the
rule (SAFe; JA sources agree); the success criterion is named before
the probe starts (JA PoC practice: 事前に評価軸を定義); the
one-sitting timebox above applies.

## Lifecycle — six stages

1. **Birth**: charting or a work-through close types a ticket
   `prototype`, question in the body. The type is a claim the
   resolution gate checks.
2. **Build**: the session creates the namespace branch; artifacts
   exist nowhere else. TDD iron law's spike exemption applies inside
   the namespace only (the same-PR doctrine amendment of the prototype
   branch fence).
3. **React / Measure** (mode fork): design mode — the human drives the
   artifact and reacts; HITL, the agent never answers its own
   question. Feasibility mode — the agent runs the probe and records
   the measured result (numbers, pass/fail against the named
   constraint); AFK, no human reaction needed to produce the evidence.
4. **Select / Ratify** (mode fork): design mode — variant selection is
   the human's act; an agent-selected variant is the documented
   wayfinder failure this stage exists to block. Feasibility mode —
   the human ratifies the *conclusion drawn from* the measurement (the
   numbers are the machine's; what they mean for the map is a
   decision). Both modes close only through the resolution's
   user-ratified line (the ratification gate).
5. **Distill**: the validated decision — state machine, schema,
   reducer, snippet trimmed to its decision-rich parts — is inlined
   into the ticket resolution; the branch is linked as the primary
   source. The inlined decision, not the branch, is what downstream
   specs and plans cite.
6. **Death**: the branch never merges (git-guard enforces);
   implementation later re-lands the behavior from the inlined
   decision under full TDD — a validated pure module may be carried
   over as the starting point, but its tests are written first and it
   enters through a normal reviewed task, never through the prototype
   branch.
   The branch is retained read-only as primary source while the map is
   live; at map archival the archive note lists surviving prototype
   branches, and pruning them is the repo owner's recorded choice —
   never an agent default.
