# User insights — <date>-<slug>

> Problem-space artifact. States **WHAT** users need and **why now**, never
> **HOW** to solve it (Intercom rule — no solution content here; solutions
> belong downstream in interface-design / spec / code). Every need links to a
> claim row in `evidence.md`; every commitment is written only **after the user
> ratifies** it.

## Problem framing

- **What** — the problem in one or two sentences, framed as a user's difficulty,
  not a missing feature.
- **Why now** — what changed that makes this worth attention today.
- **Whose problem** — the affected people / segments (not personas of buyers).

_No solutions in this section. If a sentence describes a mechanism, move it out._

## Opportunity space

The mapped space of needs. Each need is a **job story**, evidence-linked, with
its lived context and today's workaround. (Torres opportunity-space semantics.)

### Need N1 — <short label>

- **Job story**: When <situation / trigger>, I want <motivation / goal>, so I
  can <expected outcome>. _(Outcome words only — no mechanism nouns: folder
  layouts, UI elements, "automatically X" all belong in Risks/open questions,
  not inside the story.)_
- **Evidence**: `evidence.md` C1, C2 (never assert a need with no claim row).
- **Context / journey stage**: where in the user's journey this arises.
- **Today's workaround**: what the user does now instead (the cost of the gap).

### Need N2 — <short label>

- **Job story**: When …, I want …, so I can …
- **Evidence**: `evidence.md` C…
- **Context / journey stage**:
- **Today's workaround**:

## Value commitment

> Written **only after the user ratifies** the recommendation. The agent maps
> the space and proposes; the user decides which needs are served. Agents never
> self-commit on the user's behalf.

- **Committed needs**: N1, N3 (the subset we choose to serve; state why these).
- **Desired outcome per need**:
  - N1 — qualitative: <what "better" feels like>; quantitative: <a measurable
    target / signal, or "TBD — metric to define">.
- **Appetite** (Shape Up): how much time/effort this is worth — a budget, not
  an estimate.
- **Ratified by user on** <YYYY-MM-DD>.
- **Divergence from recommendation** (only when the user ratified a different
  set than the agent recommended): what changed and the user's stated reason.

## Risks & open questions

- **R1** — <risk to the framing or the commitment; what would falsify it>.
- **Q1** — <unresolved question; note whether it blocks commitment or not>.
- Unsupported claims (no `evidence.md` row) live here until researched, never in
  Opportunity space as if settled.
