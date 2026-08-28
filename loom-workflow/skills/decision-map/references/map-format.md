# MAP.md and ticket format — decision-map layer

> SSOT for the decision-map store's schema: MAP.md's frontmatter and
> sections, the ticket file schema, the fog-id and join-key grammars,
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
  - `clear` — every ticket is closed and the fog is empty or fully
    moved to Out-of-scope; the map has nothing left to work through.
  - `archived` — the map is retired. An archived map's Parts rows and
    any surviving prototype branches stay listed for reference, but
    the map no longer accepts new tickets or fog entries.

`state` is hand-edited — no script under §Command surface owns this
transition in v1. The transitions: `charting → active` is flipped by
hand as the final act of the charting close, after the risk pass and a
clean `validate` run. `active → clear` is flipped by the work-through
close that leaves zero open tickets and an empty fog section.
`clear → archived` is the repo owner's explicit decision, never an
agent default.

### Live-map criterion

**A map is live if and only if it is checker-valid AND its `state` is
`charting` or `active`.** "Checker-valid" is pinned to one exact
check: `map_store.py validate <map-dir> --repo-root <path>`
(§Command surface) exits `0` against the map. A non-zero exit — `1`
(operational error) or `2` (a structural/schema-version violation) —
is not checker-valid. `check_map_links.py` and `check_map_fog.py` are
not part of this liveness check; they gate a ticket's or fog entry's
own close-time state (see §MAP.md schema's Decisions-so-far bullet and
§Fog entries), not whether the map itself is live. Directory presence
alone is never adoption —
a directory that exists but fails validation, or that carries `clear`
or `archived`, is not a live map. Anything that needs to detect "is
there a map in progress here" (on-ramp detection, brainstorming's
upstream-artifact walk, a work-through session's own resume check)
applies this exact two-part test, never a bare existence check.

### Sections

MAP.md's body carries these sections, in this order:

1. **Destination** — prose: what this map is charting toward. The
   single paragraph a session re-reads to re-orient.
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
6. **Parts** — a table tracking plan-level delivery progress against
   this map. See §Parts section below.

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

- `type` — one of `grilling`, `research`, `task`, `prototype`. Selects
  which existing skill resolves the ticket (grilling →
  `loom-code:brainstorming`; research → `research-toolkit:deep-deep-research`;
  task → a backlog entry; prototype → the
  `prototype/<map-id>/<ticket-slug>` branch protocol).
- `status` — one of `open`, `claimed`, `closed`.
- `claim` — `null` when unclaimed, otherwise a free-text claim marker
  (who/what claimed it) written when `status` moves to `claimed`.
  Concurrent-claim discipline beyond this single field is out of scope
  for v1. **Stale-claim rule**: a LATER session may reclaim a ticket
  whose `claim` shows no commit touching that ticket file since the
  claim date, by overwriting the `claim` line and noting the takeover
  in the ticket body — this closes the dead-session deadlock without
  opening concurrency control.
- `graduated-from` — `null`, or the `F-<n>` fog id this ticket was
  graduated from (see §Fog entries).

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
  closed with no user-ratified line is a gate violation. No script
  under §Command surface enforces this in v1 — it is enforced by
  review only; a future checker may absorb it, at which point this
  line names it.

## Parts section

MAP.md's Parts section is a table, one row per plan part this map's
destination decomposes into:

| Part | Join key | Status |
|---|---|---|
| <part name> | `<map-id> / Part: <part name>` | not-started / in-progress / done(\<sha\>) |

The **join key** — `<map-id> / Part: <name>` — is the explicit,
literal string a plan's own metadata cites to bind that plan to this
map part. No topic-similarity inference is ever used to bind a plan to
a Parts row; a plan with no matching join key string is not bound to
any part, however similar its subject looks.

A plan binds itself to a Parts row by carrying, in its own `## Notes`
section, one line of the exact form `Map part: <map-id> / Part:
<name>` — no schema change to the plan format elsewhere, no
topic-similarity inference. The ` / Part: ` infix is the grep literal
a reader or a future checker matches on.

A Parts row's Status cell is flipped **only** by the `map_parts.py`
flipper (see §Command surface) — never hand-edited. Status is one of
`not-started`, `in-progress`, or `done(<sha>)` — the third form
records, in parentheses, the commit sha that delivered the part; a
row already carrying a `done(<sha>)` cell is not flipped again
(`map_parts.py` exits 2 on that target rather than overwrite an
existing delivery record). This section is the sanctioned replacement
for a hand-kept, manually-updated multi-plan progress table: any such
hand-kept table is the declared anti-pattern this section exists to
retire.

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

## Command surface

Five scripts ship under `loom-workflow/skills/decision-map/scripts/`:

| Script | Purpose |
|---|---|
| `map_init.py` | Scaffold a new `docs/loom/maps/<map-id>/` store (MAP.md + empty `tickets/`). |
| `map_store.py` | Read/write primitives for MAP.md and ticket files, shared by the other four scripts and by skill-text tooling — the only sanctioned parser for this schema. Also exposes the `validate` CLI entrypoint: `map_store.py validate <target> --repo-root <path>` — the sole check behind the §Live-map criterion's "checker-valid" test — exit 0/1/2 like the rest of §Command surface. |
| `check_map_links.py` | Verify every Decisions-so-far line links an existing, closed ticket. |
| `check_map_fog.py` | Verify fog-id monotonicity (§Fog entries): silent disappearance is machine-gated (exit 2); id reuse is review-enforced only in v1 — the same disclosure pattern the HITL resolution rule already uses (§Ticket schema). |
| `map_parts.py` | The Parts-row flipper: the only script permitted to change a Parts row's Status cell. |

**Canonical arg shape**, shared by every script above: a positional
`target` argument (the map directory, a MAP.md path, or a ticket path,
depending on the script), plus an optional `--repo-root` flag (default:
`git rev-parse --show-toplevel` of the target's directory, falling
back to cwd — the `--repo-root` resolution convention loom-code's
on-ramp checker established). `map_store.py` alone
prefixes this with a leading subcommand verb before the positional
`target` — `validate` in v1 — since it is the one script in the table
exposing more than one operation; the other four scripts take the
bare positional shape with no verb.

Beyond the shared shape, two scripts carry additional flags:
`map_parts.py` additionally REQUIRES `--part <join-key>` and `--sha
<commit>` (the row it flips and the delivering commit); `check_map_fog.py`
additionally accepts `--base <git-ref>` (default: the merge-base of
HEAD with the resolved default branch). `check_map_fog.py`'s gate is a
DIFF against that base, not a full-history scan: fog removed before
the branch point is invisible to it, and a brand-new map trivially
passes since it has no base version to compare against.

`map_init.py` is a deliberate writer-script carve-out from the other
four scripts' reader-script exit semantics: its positional argument is
a bare map-id slug, not a target path; its exit `1` covers the
already-exists refusal (an operational error, not a schema violation);
its exit `2` covers a malformed slug.

**Exit codes**, shared by every script above:

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
