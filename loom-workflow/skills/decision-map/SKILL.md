---
name: decision-map
version: 0.1.0
description: |
  Chart and work through a persistent decision map at docs/loom/maps/<map-id>/ — a destination, a growing Decisions-so-far log, and a Not-yet-specified (fog) list that graduates into tickets over many sessions instead of a one-shot plan. Use for '開地圖' / '開一張決策地圖' / 'chart a decision map' / 'work through the map' / '推進地圖' / 'デシジョンマップを開く' / 'ワークスルー' when a destination is clear but the path to it is not, and the work will span more sessions than one sitting can hold. Also use to assess live maps / 地圖還活著嗎 — is there a decision map already in progress for this repo. Not for a single self-contained task (use loom-code:writing-plans) and not for one factual question (use research-toolkit).
---

# Decision map

A decision map is a persistent store — not a one-shot document — for
charting toward a destination whose full path is not yet known. It
survives across sessions: a map is opened once (charting), then
advanced one ticket at a time over however many sessions it takes
(work-through), until the fog is empty and every ticket is closed.

Full schema authority for MAP.md and ticket files — including the
ticket boundary contract and command surface — lives in
`references/map-format.md`. Read it before charting or working through
a map; this file does not restate the schema or its boundary rules.
The prototype ticket type's full contract — when-to-use,
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

**No-fog STOP.** If charting surfaces no fog entry at all, stop and
ask the user before opening a map: an effort whose open questions can
all be stated now needs a plan (`loom-code:writing-plans`), not a map.

## Risk pass

A risk pass runs before charting closes, and again at every
work-through close (Work-through step 5 lists it among the close-time
duties — see below). The pass looks over the map's open tickets and
remaining fog for any unknown matching a front-load trigger in
§Risk-driven front-loading of `references/prototype-contract.md` (e.g.
build-to-estimate, an unproven architecturally-significant path, the
map's highest risk exposure). Any match gets a feasibility/prototype
ticket created on the frontier immediately — ordered by risk exposure
(probability × impact), highest first — never deferred until reached.
The same reference's anti-over-prototyping guardrails apply: no probe
when a conversation or lookup would settle it, a success criterion
named before the probe starts, and the one-sitting timebox.

Charting closes only after the risk pass above and a clean validate
run: `map_store.py validate <map-dir> --repo-root <path>`.
Between those two steps, write the destination ratification line into
the Destination section — the user-ratified line whose exact shape and
validate gate are pinned in §Sections of `references/map-format.md`
(read that section for the shape rather than re-deriving it here). The close
order therefore reads: risk pass → ratification line → validate →
the hand-flip to `active` below.

Exit 2 means the map content is not yet chartered cleanly — fix the
reported violation; exit 1 means the path or environment is wrong,
not the map — fix the invocation. Only then treat the map as ready
for work-through. Once clean, flip `state` from `charting` to `active`
by hand — this is the final act of the charting close (no script owns
`state` transitions in v1; see `references/map-format.md`
§Frontmatter).

## Work-through mode

Work-through advances a map that is already `charting` or `active`.
One session works through **one ticket** — except a `research` ticket,
which may span multiple sessions before it resolves, since the lookup
itself can take longer than one sitting.

### Selecting the map and the ticket

The MAP is human-named — never agent-picked. Work-through starts on a
map the user named, or on one a recorded signal designates (e.g. the
session's worktree or branch name matching a ticket slug in that map).
With more than one live map and no such signal, ask the user which map
to work — never infer the map from topic similarity. The TICKET within
the named map is agent-picked: prefer a frontier ticket (§Ticket
schema in `references/map-format.md` defines the frontier test). The
claim records the selection basis — step 1 below says where.

A session that works through a ticket does, in order:

1. **Claim before work.** Before touching the ticket's question, set
   its frontmatter `claim` field and move `status` from `open` to
   `claimed`. Never work an unclaimed ticket, and never work a ticket
   another session already claimed. In the same claim edit, write one
   selection-basis line into the ticket body: who or what named the
   map (the user, or the recorded signal, quoted) and why this ticket
   was picked (e.g. the only frontier ticket, or the highest-risk
   frontier ticket).
2. **Resolve the ticket.** Delegate the actual work by the ticket's
   `type`, per §Delegation by ticket type below. When the work
   concludes, fill in the ticket's Resolution section per §Ticket
   schema in `references/map-format.md`, including a user-ratified
   line for any HITL resolution, and move `status` to `closed`.
3. **Append one gist line to MAP.md.** Steps 3-4 apply only when step
   2 closed the ticket this session — a multi-session `research`
   ticket that did not close has no ticket to gist-link yet, and the
   session ends after step 2. Add exactly one bullet to
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
   later session to rediscover. Recording need not wait for the
   close: a question surfaced mid-ticket is recorded as fog (or
   graduated) when surfaced — this step is the deadline, never a
   reason to park a known question until close. Route what surfaces
   by where it binds: an unknown blocking THIS map's destination goes
   to this map's fog; a lesson or unknown that outlives every map
   goes to the repo's backlog store (`docs/loom/backlog/`) instead.
   The agent routes without asking, but the entry it files records
   the routing basis — one line stating which of the two criteria
   placed it there.
5. **Run the risk pass, then the close-time gates.** Run the risk
   pass from §Risk pass above first — this is a prose judgment step,
   not a script, so read the open tickets and fog yourself and front-
   load any ticket the triggers call for. Only then run the three
   mechanical gates, all of which must pass before the session ends:
   `map_store.py validate <map-dir> --repo-root <path>`,
   `check_map_links.py <map-dir> --repo-root <path>`, and
   `check_map_fog.py <map-dir> --repo-root <path>`.
   Exit 2 from any of the three means the close is not done — fix the
   reported violation (a bad link, a fog-monotonicity break, a schema
   violation) before ending the session. Exit 1 means the path or
   environment is wrong, not the map — fix the invocation and re-run.
   If this close satisfies the clear condition in
   `references/map-format.md` §Ticket boundary contract, flip `state`
   from `active` to `clear` by hand.

### Delegation by ticket type

Each ticket's `type` selects the existing skill (or store) that
resolves it — decision-map never performs the resolution itself, only
schedules and records it. Delegation is by public skill name only,
never by a sibling plugin's internal file path, per loom's
cross-plugin delegation contract (paths + names, never sibling file
content).

- **`grilling`** — delegate to a `loom-code:brainstorming` session.
  HITL: the ticket's Resolution section carries a user-ratified line
  (`references/map-format.md` §Ticket schema).
- **`research`** — delegate to `research-toolkit:deep-deep-research`.
  May span multiple sessions before it resolves (see Work-through
  mode above).
- **`task`** — follow `references/map-format.md` §Ticket boundary
  contract.
- **`prototype`** — delegate to the protocol in
  `references/prototype-contract.md`. HITL: both prototype modes
  (variant selection and feasibility-conclusion) carry a
  user-ratified line in the Resolution section, per §Ticket schema in
  `references/map-format.md`. When the measurement finished but the
  user deferred ratifying the conclusion, the ticket stays `claimed`,
  records a progress note in its body, and may set
  `ratification: pending` (§Ticket schema owns the field); it closes
  only when the deferred ratification lands.

## Liveness assessment

A caller (e.g. a kickoff flow) invokes this skill to ask "is there a
live map here": enumerate `docs/loom/maps/*/`, then apply
`references/map-format.md` §Live-map criterion. Return the live
map-ids paired with each Destination section's first line, an explicit
"no live map" answer, or refuse until a broken map is repaired, as the
criterion requires.

## See also

- `references/map-format.md` — MAP.md schema, ticket schema,
  fog-id grammar, schema versioning, §Command surface.
- `references/prototype-contract.md` — the `prototype` ticket type's
  full contract.
- `references/family-reception.md` — the family reception contract,
  including the on-ramp row that routes work here; read it when a
  session arrives without having passed through a family entry.
