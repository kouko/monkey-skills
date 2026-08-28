---
name: decision-map
version: 0.1.0
description: |
  Chart and work through a persistent decision map at docs/loom/maps/<map-id>/ — a destination, a growing Decisions-so-far log, and a Not-yet-specified (fog) list that graduates into tickets over many sessions instead of a one-shot plan. Use for '開地圖' / '開一張決策地圖' / 'chart a decision map' / 'work through the map' / '推進地圖' / 'デシジョンマップを開く' / 'ワークスルー' when a destination is clear but the path to it is not, and the work will span more sessions than one sitting can hold. Not for a single self-contained task (use loom-code:writing-plans) and not for one factual question (use research-toolkit).
---

# Decision map

A decision map is a persistent store — not a one-shot document — for
charting toward a destination whose full path is not yet known. It
survives across sessions: a map is opened once (charting), then
advanced one ticket at a time over however many sessions it takes
(work-through), until the fog is empty and every ticket is closed.

Full schema authority for MAP.md and ticket files —
frontmatter fields, section order, the fog-id grammar, the ticket
schema, schema versioning, and the pinned command surface — lives in
`references/map-format.md`. Read it before charting or working through
a map; this file does not restate the schema, only the protocol for
using it. The prototype ticket type's full contract — when-to-use,
both modes, the six-stage lifecycle — lives in
`references/prototype-contract.md`; read it before delegating a
`prototype` ticket.

Every map lives at `docs/loom/maps/<map-id>/` (MAP.md + `tickets/`),
per `references/map-format.md` §Store layout.

## Charting

Charting opens a new map or extends one already in `charting` state.
It produces:

1. **Destination** — one paragraph stating what the map is charting
   toward.
2. **First tickets** — the initial set of `tickets/<slug>.md` files
   for work that is already well-enough understood to act on
   directly.
3. **Fog** — the initial Not-yet-specified list, each entry an
   authored `F-<n>` id per §Fog entries in `references/map-format.md`.

## Risk pass

A risk pass is meant to run before charting closes, and again at every
work-through close (Work-through step 5's close-time gates do not yet
list it — see below). Both the trigger contract (front-loading a
feasibility/prototype ticket onto the frontier) and its applicability
at both close points are defined in a later revision of this skill;
this section is a placeholder heading until that contract lands.

Charting closes only after the risk pass above (once that contract
lands) and a clean validate run:
`map_store.py validate <target> --repo-root <path>`.

A non-zero exit means the map is not yet chartered cleanly — fix the
reported violation before treating the map as `charting`-state-ready
for work-through.

## Work-through mode

Work-through advances a map that is already `charting` or `active`.
One session works through **one ticket** — except a `research` ticket,
which may span multiple sessions before it resolves, since the lookup
itself can take longer than one sitting.

A session that works through a ticket does, in order:

1. **Claim before work.** Before touching the ticket's question, set
   its frontmatter `claim` field and move `status` from `open` to
   `claimed`. Never work an unclaimed ticket, and never work a ticket
   another session already claimed.
2. **Resolve the ticket.** Delegate the actual work by the ticket's
   `type`, per §Delegation by ticket type below. When the work
   concludes, fill in the ticket's Resolution section per §Ticket
   schema in `references/map-format.md`, including a user-ratified
   line for any HITL resolution, and move `status` to `closed`.
3. **Append one gist line to MAP.md.** Add exactly one bullet to
   Decisions-so-far: one gist sentence, ending in the ticket link as
   the line's last parenthesized token —
   `- <gist>. (tickets/<slug>.md)` — per §Sections' Decisions-so-far
   grammar. Never write the decision only in Notes; an unlinked
   decision is not mechanically checkable and does not count as
   recorded.
4. **Graduate fog in the same close.** If resolving this ticket
   surfaced new open questions, either add new `F-<n>` fog entries or
   graduate an existing fog entry into a new ticket (recording
   `graduated-from: F-<n>` on the new ticket's frontmatter) before the
   session ends — never leave a surfaced question undocumented for a
   later session to rediscover.
5. **Run the close-time gates.** All three must pass before the
   session ends: `map_store.py validate <target> --repo-root <path>`,
   `check_map_links.py <target> --repo-root <path>`, and
   `check_map_fog.py <target> --repo-root <path>`.
   A non-zero exit from any of the three means the close is not done —
   fix the reported violation (a bad link, a fog-monotonicity break, a
   schema violation) before ending the session.

### Delegation by ticket type

Each ticket's `type` selects the existing skill (or store) that
resolves it — decision-map never performs the resolution itself, only
schedules and records it. Delegation is by public skill name only,
never by a sibling plugin's internal file path, per the Cross-Plugin
Delegation Contract in this repo's root `CLAUDE.md`.

- **`grilling`** — delegate to a `loom-code:brainstorming` session.
  HITL: the ticket's Resolution section carries a user-ratified line
  (`references/map-format.md` §Ticket schema).
- **`research`** — delegate to `research-toolkit:deep-deep-research`.
  May span multiple sessions before it resolves (see Work-through
  mode above).
- **`task`** — delegate to a backlog entry in this repo's
  `docs/loom/backlog/` store.
- **`prototype`** — delegate to the protocol in
  `references/prototype-contract.md`. HITL: both prototype modes
  (variant selection and feasibility-conclusion) carry a
  user-ratified line in the Resolution section, per §Ticket schema in
  `references/map-format.md`.

## See also

- `references/map-format.md` — MAP.md schema, ticket schema,
  fog-id grammar, schema versioning, §Command surface.
- `references/prototype-contract.md` — the `prototype` ticket type's
  full contract.
