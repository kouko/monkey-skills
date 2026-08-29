# MAP.md and ticket format — decision-map layer

> SSOT for the decision-map store's schema: MAP.md's frontmatter and
> sections, the ticket file schema, the fog-id grammar,
> schema versioning, and the pinned command surface. Every checker,
> flipper, and skill-text reference in this skill cites this file
> instead of restating the grammar.

## Store layout

A map lives at `docs/loom/maps/<map-id>/`:

```
docs/loom/maps/<map-id>/
  MAP.md
  tickets/
    <slug>.md
    <slug>.md
```

`<map-id>` is a stable slug chosen at charting time and never renamed —
every join key and every ticket's location is anchored to it.

## MAP.md schema

### Frontmatter

```yaml
---
map-id: <slug>
schema_version: 1
state: charting
---
```

Frontmatter is parsed as simple `key: value` lines, not YAML — no
nesting, no quoting, no multi-line values (`map_store.py`'s
`parse_frontmatter` is the sanctioned parser).

- `map-id` — string, matches the store directory name.
- `schema_version` — integer. Bumped only on a breaking grammar
  change (a field renamed, removed, or reinterpreted — never on an
  additive change such as a new optional field). See §Schema
  versioning below.
- `state` — one of `charting`, `active`, `clear`, `archived`.
  - `charting` — the map is being built out (destination + first
    tickets + fog); not yet a stable work-through loop.
  - `active` — the work-through loop is live; tickets are being
    claimed and resolved.
  - `clear` — the clear condition in §Ticket boundary contract holds:
    zero non-closed tickets and an empty fog section.
  - `archived` — the map is retired and no longer accepts new tickets
    or fog entries.

`state` is hand-edited — no script under §Command surface owns this
transition in v1. The transitions: `charting → active` is flipped by
hand as the final act of the charting close, after the risk pass and a
clean `validate` run. `active → clear` is flipped by the work-through
close that satisfies the clear condition in §Ticket boundary contract.
`clear → archived` is the repo owner's explicit decision, never an
agent default. On archive, reopen every backlog entry whose ticket is
still non-closed and whose frontmatter says `origin: promoted to
<ticket>`; the map then remains a historical record, not a stranded
promotion target.

### Live-map criterion

`is_live_map` has exactly three results: `live` when `map_store.py
validate <map-dir> --repo-root <path>` exits `0` and the state is
`charting` or `active`; `not-present` when no map exists; and `broken`
for every existing map that is not live. Any consumer, including
umbrella checks and reception, must refuse until a `broken` map is
repaired — it must never treat `broken` as `not-present`.

### Sections

MAP.md's body carries these sections, in this order:

1. **Destination** — prose: what this map is charting toward. The
   single paragraph a session re-reads to re-orient. From the charting
   close onward, an `active` or `clear` map's Destination section also
   carries a destination ratification line — exact shape
   `user-ratified: <name/handle>, <date>` (the same dated shape
   §Ticket schema's HITL rule uses) — recording that a human ratified
   the map's direction. `map_store.py validate` machine-gates its
   presence on `active` and `clear` maps (exit 2 when missing), and
   `map_init.py` scaffolds the line slot. This gate tightens beyond
   new-rule writes under §Schema versioning's migration clause.
2. **Notes** — free-form prose; anything that does not fit the
   structured sections below. Never a substitute for a Decisions-so-far
   line or a fog entry — a decision or an open question written only
   in Notes is not mechanically checkable and does not count as
   recorded.
3. **Decisions-so-far** — a bulleted list of gist+link lines. Each
   line is one gist sentence followed by a link to the ticket file
   that produced it: `- <gist>. (tickets/<slug>.md)`. The gist
   sentence itself may contain parentheses; the ticket link is always
   the **last** parenthesized token on the line, and a parser reads
   the link from the line's final `(...)` group rather than its first.
   Every line here must link an existing **closed** ticket — a line
   with no resolvable link, or one linking an open/claimed ticket, is
   a gate violation (see `check_map_links.py` in §Command surface).
4. **Not-yet-specified (fog)** — a bulleted list of open questions the
   map has not yet resolved into a ticket. See §Fog entries below for
   the id grammar.
5. **Out-of-scope** — a bulleted list of things this map explicitly
   will not chart. A fog entry may graduate here instead of into a
   ticket (see §Fog monotonicity).

## Fog entries

Each fog entry carries an authored id of the form `F-<n>` — the
literal prefix `F`, a hyphen, then a decimal number — written by
whoever adds the entry, never derived from its text or its position
in the list (mirrors the `BI-<n>` brief-item-identifier grammar this
store's fog ids are modeled on).

The line itself is pinned to one grammar, mirroring how
Decisions-so-far pins its own line shape (§MAP.md schema's §Sections):
`- F-<n>: <text>` — a leading bullet, the id first, then a colon
separator. Any other shape is invisible to the sanctioned parser
(`map_store.py`) and to the fog gate (`check_map_fog.py`).

- **Monotonic, never renumbered, never reused.** A new fog entry takes
  the next unused number — the highest `F-<n>` this map has ever used,
  plus one — regardless of where in the Not-yet-specified list it
  sits. An entry already present keeps its number.
- **A fog entry may only shrink, graduate, or move to Out-of-scope —
  never silently vanish.** "Shrink" means its wording narrows without
  changing its id. "Graduate" means a ticket is created from it and
  the ticket's frontmatter records the source id (`graduated-from:
  F-<n>`); the fog entry is then removed from Not-yet-specified.
  "Move to Out-of-scope" means the entry is relocated verbatim (its id
  travels with it) into the Out-of-scope section. Any other
  disappearance — an entry that is simply deleted with no graduation
  record and no Out-of-scope line — is fog-monotonicity violation
  (`check_map_fog.py`, exit 2).
- A retired `F-<n>` (graduated or moved) is never reused by a later
  entry, the same rule as brief-item identifiers.

## Ticket schema

Each ticket is one file: `tickets/<slug>.md`.

### Frontmatter

```yaml
---
type: task
status: open
claim: null
graduated-from: null
---
```

- `type` — one of `grilling`, `research`, `task`, `prototype`. A
  `task` is decision-unblocking work: it produces an artifact or answer
  needed to decide the map's next move and never delivers the
  Destination. Its Resolution records that artifact or answer, never a
  backlog-entry filing. The other types select their resolver as
  described by their own contracts.
- `status` — one of `open`, `claimed`, `closed`.
- `claim` — `null` when unclaimed, otherwise a claim marker of the
  form `<who>, <YYYY-MM-DD>` (the same dated shape the user-ratified
  line uses), written when `status` moves to `claimed`.
  Concurrent-claim discipline beyond this single field is out of scope
  for v1. **Stale-claim rule**: a LATER session may reclaim a ticket
  when no commit has touched that ticket file since the claim marker's
  date — an observable git fact, not a trust call — by overwriting the
  `claim` line and noting the takeover in the ticket body. A claim
  with no date is reclaimable outright. This closes the dead-session
  deadlock without opening concurrency control.
- `graduated-from` — `null`, or the `F-<n>` fog id this ticket was
  graduated from (see §Fog entries).
- `blocked-by` — optional. Absent means no blockers — exactly today's
  meaning. When present, one line of comma-separated ticket slugs
  (frontmatter is simple `key: value` — no YAML lists, so the slugs
  share a single line); every slug names a sibling ticket file in the
  same map's `tickets/` directory. The blocked-by graph must be
  acyclic. Dangling slugs and cycles are machine-gated by
  `map_store.py validate` (§Command surface), exit 2.
- `ratification` — optional; sole defined value `pending`. Marks a
  prototype ticket whose measurement finished but whose conclusion
  the user deferred ratifying; the ticket stays `claimed` while the
  field is `pending`. Absent means no deferred ratification —
  exactly today's meaning. The field records measurement state, not
  claimant state, so it survives a stale-claim reclaim unchanged; the
  new claimant inherits the pending ratification duty.

**Frontier.** A ticket is on the frontier iff its `status` is `open`,
every ticket named in its `blocked-by` line is `closed`, and it is
unclaimed. A ticket with no `blocked-by` field is frontier-eligible
whenever it is open and unclaimed — the pre-`blocked-by` behavior,
unchanged.

### Body sections

- A free-text description of the question or task the ticket answers.
- **Resolution** — filled in when `status` moves to `closed`. Records
  what was decided/built/found. For a HITL resolution (any ticket
  whose answer required a human decision — grilling outcomes,
  prototype variant selection, prototype feasibility-conclusion
  ratification), the Resolution section carries a **user-ratified
  line**: a line stating that a human, not the agent, made the call,
  in a form a gate can find (e.g. `user-ratified: <name/handle>,
  <date>`). Every ticket with `type: grilling` or `type: prototype` is
  HITL unconditionally — both prototype modes (variant selection and
  feasibility-conclusion) close only through ratification, so a
  checker never has to inspect a prototype ticket's body to decide
  whether the duty applies; `type` alone decides it. A HITL ticket
  closed with no user-ratified line is a gate violation.
  `map_store.py validate` (§Command surface) enforces it: a `closed`
  grilling or prototype ticket whose Resolution carries no
  `user-ratified:` line exits 2.
  Every closed `task` ticket additionally has a non-empty Resolution
  and one `delivery-evidence: <commit SHA | PR | artifact path>` line;
  `map_store.py validate` rejects either omission.

### Ticket sizing

One ticket's question is sized to one agent session. A research
ticket may span several sessions resolving, but the QUESTION itself
stays one-session-sized — a question too large for one sitting is
split into multiple tickets (or returned to fog) rather than
stretched across one oversized ticket.

## Ticket boundary contract

This section is the sole authority for D2–D9; protocol text cites it
instead of paraphrasing its rules.

The **clear condition** is zero non-closed tickets (`open` and
`claimed` both count as non-closed) and an empty fog section.

**Umbrella checks** use two exact primitives. `check-umbrella` asks
whether a live map's clear condition requires the work; run it when a
backlog entry is created and again at pickup before work. `check-queue`
asks whether the backlog already tracks similar work; run it when a
map is charted and whenever a task ticket is created. Neither primitive
uses topical-overlap matching or `map-scope-check:` evidence lines.

When work belongs to more than one live map Destination, halt for human
adjudication. The selected map uniquely owns the ticket; every other
map records one `Out-of-scope` line citing the ticket's join key. A
ticket's join key is its literal `tickets/<slug>.md` path.
Duplicate task tickets for the same work violate this contract.

Promotion is close-and-cite: close the backlog entry and write
`origin: promoted to <ticket>` before creating the map ticket. There is
no blocked state, standing bidirectional link, or close-on-delivery
step.

## Schema versioning

`schema_version` is an integer on MAP.md's frontmatter only — v1 ships
one shared version across MAP.md and its tickets, so ticket
frontmatter never repeats the field (see §Ticket schema's example,
which carries no `schema_version` key). Every checker under §Command
surface reads `schema_version` before doing anything else. When the
checker's `target` is a ticket path rather than MAP.md itself, it
resolves the governing version by walking up from the ticket's
directory to that map's `MAP.md` and reading the field there — never
by assuming a version or by requiring the ticket to carry its own
copy. If the value is greater than the highest version that checker's
own code supports, the checker refuses to read further and exits 2
with a message naming both the file's version and the checker's
supported ceiling. A checker never guesses at an unknown schema shape.

Mechanism revisions to this store are additive-only. A revision may
add new optional fields, and may tighten a check only so that content
written under the new rules can newly fail — never so that an
untouched pre-existing store starts failing. One narrow exception —
the migration clause: a check MAY tighten beyond new-rule writes
only when the same revision migrates every known pre-existing store
and records that migration, so no untouched store is left to fail.
The destination-ratification gate (§Sections' Destination bullet) is
this clause's first instance: its one pre-existing map was ratified
in the same revision that introduced the check, emptying the legacy
population. Under this constitution
an older checker never mis-rejects a newer store, and a newer checker
never mis-rejects an untouched older store. The rationale is
operational, not hypothetical: cross-host plugin version skew is a
measured normal state, not an edge case.

## Command surface

Four scripts ship under `loom-workflow/skills/decision-map/scripts/`:

| Script | Purpose |
|---|---|
| `map_init.py` | Scaffold a new `docs/loom/maps/<map-id>/` store (MAP.md + empty `tickets/`). |
| `map_store.py` | Read/write primitives for MAP.md and ticket files, shared by the other three scripts and by skill-text tooling — the only sanctioned parser for this schema. Also exposes the `validate` CLI entrypoint: `map_store.py validate <map-dir> --repo-root <path>` — the sole check behind the §Live-map criterion's liveness check — exit 0/1/2 like the rest of §Command surface. |
| `check_map_links.py` | Verify every Decisions-so-far line links an existing, closed ticket. |
| `check_map_fog.py` | Verify fog-id monotonicity (§Fog entries): silent disappearance is machine-gated (exit 2); duplicate ids within the current MAP.md are gated by `validate`; reuse of a RETIRED id (graduated or moved to Out-of-scope, then re-issued) is review-enforced only in v1 — the same disclosure pattern the HITL resolution rule already uses (§Ticket schema). |

**Canonical arg shape**, shared by every script above: a positional
`target` argument (the map directory, a MAP.md path, or a ticket path,
depending on the script), plus an optional `--repo-root` flag (default:
`git rev-parse --show-toplevel` of the target's directory, falling
back to cwd — the `--repo-root` resolution convention loom-code's
on-ramp checker established). `map_store.py` alone
prefixes this with a leading subcommand verb before the positional
`target` — `validate` in v1 — since it is the one script in the table
exposing more than one operation; the other three scripts take the
bare positional shape with no verb.

Beyond the shared shape, `check_map_fog.py` additionally accepts
`--base <git-ref>` (default: the merge-base of
HEAD with the resolved default branch). `check_map_fog.py`'s gate is a
DIFF against that base, not a full-history scan: fog removed before
the branch point is invisible to it, and a brand-new map trivially
passes since it has no base version to compare against.

`map_init.py` is a deliberate writer-script carve-out from the other
three scripts' reader-script exit semantics: its positional argument is
a bare map-id slug, not a target path; its exit `1` covers the
already-exists refusal (an operational error, not a schema violation);
its exit `2` covers a malformed slug.

**Exit codes**, shared by the four reader scripts (map_init.py's writer carve-out above):

- `0` — clean: no violation found, or the requested write succeeded.
- `1` — operational error: the target does not exist, is unreadable,
  or another environmental failure prevented the check/write from
  running at all.
- `2` — violation: the target exists and was readable, but its
  content fails the check (a fog-monotonicity break, a link to a
  non-closed ticket, a `schema_version` past what the checker
  supports, and so on).

A checker that cannot distinguish "nothing to check" from "a
violation" is a defect — the 0/1/2 split exists precisely so a caller
never has to parse stdout to know which case it hit.
