# MAP.md and ticket format — Outcome Map v3

> Schema and command-surface SSOT for the decision-map store. Scripts and
> skill instructions cite this file instead of restating its grammar.

## Outcome-control loop

One MAP.md is one persistent outcome-control loop with multiple independently
closed delivery arcs. Closing a delivery arc must not clear the Map. Each
delivery advances one outcome-advancing slice; the wider loop remains active
while another Ticket, fog entry, or Destination acceptance gap remains.

Exactly four closure types exist: `grilling`, `research`, `prototype`, and
`delivery`. They are mutually exclusive because each names different closure
evidence. Dependencies are graph edges, not ticket types; schema v3 rejects
`task` and `unblock`.

`MAP.md` and Tickets are the source of truth for durable outcome state. Brief,
Plan, Git, PR, and CI artifacts own delivery progress. The Map resolves that
progress read-only and never persists a duplicate phase or status.

## Store layout

A Map has stable identity and is never physically relocated:

```text
docs/loom/maps/<map-id>/
  MAP.md
  tickets/
    <slug>.md
```

`<map-id>` and ticket slugs are lowercase letters, digits, and hyphens. A
clear or archived predecessor remains immutable; later regression creates a
successor Map that cites the predecessor.

## MAP.md template

`map_init.py` emits this schema-v3 scaffold, with `<map-id>` replaced by the
requested slug:

```markdown
---
map-id: <slug>
schema_version: 3
state: charting
---

## Destination

TODO: what this map is charting toward.

<!-- charting close: replace this comment with the destination
ratification line, exact shape `user-ratified: <name/handle>, <date>` -->

## Notes

## Decisions-so-far

## Not-yet-specified (fog)

## Out-of-scope
```

The required sections occur exactly once and in that order. Before activation,
replace the Destination placeholder, add the ratification line, author at least
one Destination acceptance entry such as
`- DA-1: <criterion> | state: open | kind: objective`, and add genuine fog as
`- F-1: <open question>`.

### Frontmatter and lifecycle

- `map-id` equals the directory name and never changes.
- `schema_version` is exactly `3`. Versions below 3 are refused with migration
  guidance; future versions are refused rather than guessed.
- `state` is one of `charting`, `active`, `clear`, or `archived`.

`charting` accepts authoring but refuses work operations. Activation requires a
ratified Destination and a valid store. `active` accepts work-through.
Map clear requires empty fog, every Ticket terminal (`closed` or `withdrawn`),
and every authored Destination acceptance criterion satisfied with valid
evidence. A closed delivery alone is never a clear transition.

Retirement is distinct from success. A clear Map can archive; a charting or
active Map can retire only with a named, dated human and a non-empty reason.
Both retain the stable store path and all relationships. Archived Maps reject
new work.

### Destination acceptance

Each criterion uses a stable, monotonic, never-reused identity:

```text
- DA-<n>: <criterion> | state: <open|satisfied> | kind: <objective|evaluative> [| evidence: <pointer>] [| user-ratified: <name>, <YYYY-MM-DD>]
```

A satisfied criterion requires `evidence`. A satisfied evaluative criterion
also requires named, dated human ratification. Retired ids remain in Notes as
`retired-da: DA-<n> | <history>` and remain part of the high-water mark.
DA-shaped bullets outside the exact grammar are errors, never invisible prose.

### Decisions, fog, and scope

Every closed Ticket has exactly one gist in Decisions-so-far:

```text
- <one-sentence gist>. (tickets/<slug>.md)
```

The final parenthesized token is the sibling Ticket link. It must resolve to a
closed Ticket; duplicate or missing gists fail validation.

Fog uses `- F-<n>: <text>`. Ids are monotonic, never renumbered, and never
reused, including ids already graduated or moved Out-of-scope. A fog entry can
shrink in place, graduate exactly once to a Ticket carrying
`graduated-from: F-<n>`, or move intact to Out-of-scope. It never silently
vanishes.

## Ticket template

```markdown
---
type: <grilling|research|prototype|delivery>
status: open
claim: null
graduated-from: null
---

<one-session-sized question or promised slice>
```

Normalized template fields are: `type: <grilling|research|prototype|delivery>
status: open claim: null graduated-from: null`.

Optional frontmatter:

- `blocked-by: <slug>, <slug>` — unique sibling Tickets in the same Map.
- `brief: <repo-relative-path>` — delivery only; points to one reciprocal
  regular-file Brief relation.
- `ratification: pending` — a prototype candidate awaits human evaluation.
- `withdrawn-from: open|claimed` — required on withdrawn history.

No other v3 ticket fields are accepted. Delivery phase remains derived.

### Status and graph

Status is exactly `open`, `claimed`, `closed`, or `withdrawn`. A frontier
Ticket is open, unclaimed, and has only closed blockers. A blocker graph is
same-Map, unique, complete, and acyclic; missing, cross-Map, self, duplicate,
or cyclic edges fail. A claim is allowed only on the current frontier.

Claims use `<owner>, <YYYY-MM-DD>`. Reclaim is conservative: only a dated
claimed Ticket with observable repository evidence of no post-claim work may
change owners; unavailable or contradictory evidence preserves the owner.

Terminal Tickets are immutable. Withdrawal records a `## Withdrawal` with
`reason:` and named, dated `user-ratified:` evidence, carries no Resolution,
and cannot strand a nonterminal dependent.

### Closure evidence

Every closed Ticket has a non-empty `## Resolution` and exactly one subtype
contract:

- `grilling`: `decision:` plus `user-ratified: <name>, <YYYY-MM-DD>`.
- `research`: `factual-answer:` plus `inspectable-evidence:`. Machine-measured
  feasibility belongs here.
- `prototype`: `candidate-artifact:`, `evaluation:`, and named, dated
  `user-ratified:` evidence. A human evaluates or selects a newly created
  candidate; machine feasibility alone is not prototype closure.
- `delivery`: `delivery-evidence:` for the promised slice, after the bound
  Brief's authored `pr-ci`, `merged`, or `artifact` policy is currently met.

Unavailable, stale, unauthorized, pending, invalid, or contradictory evidence
does not close work. Each delivery owns one reciprocal Brief, at most one Plan,
one or more ordered PRs, and exclusive ownership of every cited PR.

## Public operations

Mutations run under the Map-local descriptor-safe lock and refuse unsupported
filesystem assumptions. The exact Python call templates below match the
implemented scripts; capture a fresh revision when the signature requires it
and reuse `operation_id` on retry.

- Start delivery:
  `start_delivery.start_delivery(ticket_path, brief_path, repo_root=repo_root)`
- Claim:
  `map_transaction.claim_ticket(map_dir, ticket_slug, owner=owner, claimed_on=date, operation_id=operation_id, expected_revision=revision)`
- Update blockers:
  `map_transaction.update_blockers(map_dir, ticket_slug, blockers, operation_id=operation_id, expected_revision=revision)`
- Close and re-chart:
  `map_transaction.close_and_rechart(map_dir, ticket_slug, gist=gist, resolution=resolution, unknowns=unknowns)`
- Archive a clear Map:
  `map_transaction.archive_map_transition(map_dir, repo_root=repo_root)`
- Retire charting or active work:
  `map_transaction.retire_map(map_dir, ratified_by=name, ratified_on=date, reason=reason, repo_root=repo_root)`

Close and re-chart records Map-side effects before terminalizing the Ticket,
routes every newly exposed unknown, and reports Map-clear eligibility. It does
not silently perform or claim whole-Map acceptance.

## Schema-v2 migration

Migration is evidence-based, previewable, and idempotent. First run the
zero-write `preview = migrate_map_v3.preview_migration(map_dir)`. Inspect its
source digests and closure classifications. Only then run
`migrate_map_v3.apply_migration(map_dir, preview)`.

V2 `task` and feasibility `prototype` names are not mechanically renamed.
Factual or measured evidence becomes research; a formally delivered slice
becomes delivery and must already have a canonical reciprocal Brief; a
human-evaluated candidate becomes prototype; a ratified value decision becomes
grilling. Ambiguity refuses. Any source, membership, or binding change after
preview refuses apply. Repeating an applied migration produces no duplicates.

## Command surface

These exact runnable templates match the shipped CLI parsers:

- `map_init.py <map-id> --repo-root <path>`
- `map_store.py validate <map-dir> --repo-root <path>`
- `check_map_links.py <map-dir> --repo-root <path>`
- `check_map_fog.py <map-dir> --repo-root <path>`
- `map_progress.py <target> --repo-root <path>`

`map_progress.py` accepts a repository root, Ticket, or Plan and optionally
`--map-id <map-id>`. It is read-only. `check_map_fog.py` optionally accepts
`--base <git-ref>`; otherwise it resolves the default comparison base.

`map_init.py` is the writer carve-out: exit `0` creates, exit `1` refuses an
existing store or reports an operational error, and exit `2` rejects the slug.
The four reader commands share:

- `0` — clean.
- `1` — missing, unreadable, unavailable, or environmental failure.
- `2` — readable input violates schema or relation rules.

A caller never parses prose output to distinguish these cases.
