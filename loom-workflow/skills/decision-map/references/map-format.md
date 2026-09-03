# MAP.md and ticket format — Outcome Map v3

> Schema and command-surface SSOT for the decision-map store. Scripts and
> skill instructions cite this file instead of restating its grammar.

## Outcome-control loop

One MAP.md is one persistent outcome-control loop with multiple independently
closed delivery arcs. Closing a delivery arc must not clear the Map. Each
delivery advances one outcome-advancing slice; the wider loop remains active
while another Ticket, fog entry, or Destination acceptance gap remains.

Exactly three ticket closure types exist: `grilling`, `research`, and
`prototype`. They are mutually exclusive because each names different closure
evidence. Dependencies are graph edges, not ticket types; schema v3 rejects
`task` and `unblock`. A delivery is not a ticket: it is one outcome-advancing
slice promised by an intent under `docs/loom/intent/`.

`MAP.md` and Tickets are the source of truth for durable outcome state.
Intent, Plan, Git, PR, and CI artifacts own delivery progress. The Map
resolves that progress read-only and never persists a duplicate phase or
status.

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

Delivery arcs opened against a criterion are listed in Notes as
`- delivery-intent: DA-<n> | docs/loom/intent/<change-id>.md`. The line is the
whole binding: the intent's own `status:` (`open`, `confirmed <date>`,
`closed`, `withdrawn — <reason>`) is the delivery state, the Map never copies
it, and a withdrawn arc is annotated `retired — <reason>` beside its
change-id. A criterion with an `open` delivery arc opens no second arc; it is
satisfied either by that arc closing with evidence, by a replacement intent,
or by direct Destination acceptance evidence.

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
type: <grilling|research|prototype>
status: open
claim: null
graduated-from: null
---

<one-session-sized question or promised slice>
```

Normalized template fields are: `type: <grilling|research|prototype>
status: open claim: null graduated-from: null`.

Optional frontmatter:

- `blocked-by: <slug>, <slug>` — unique sibling Tickets in the same Map.
- `brief: <repo-relative-path>` — legacy delivery tickets only. Pre-1.0
  bindings stay readable; no new ticket carries this field.
- `ratification: pending` — a prototype candidate awaits human evaluation.
- `withdrawn-from: open|claimed` — required on withdrawn history.

No other v3 ticket fields are accepted. Delivery phase remains derived.

### Status and graph

Status is exactly `open`, `claimed`, `closed`, or `withdrawn`. A frontier
Ticket is open, unclaimed, and has only closed blockers. A blocker graph is
same-Map, unique, complete, and acyclic; missing, cross-Map, self, duplicate,
or cyclic edges fail. A claim is allowed only on the current frontier.

Claims use `<owner>, <YYYY-MM-DD>`. A claim is not transferable: no edit
reassigns a claimed Ticket to a different owner. An abandoned claimed
Ticket leaves `claimed` only through Withdrawal, recorded as
`withdrawn-from: claimed`.
Absent a recorded `withdrawn-from: claimed`, the Ticket remains claimed
by its original owner.

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
- `delivery` (legacy only): `delivery-evidence:` for the promised slice, after
  the bound Brief's authored `pr-ci`, `merged`, or `artifact` policy is
  currently met. Schema v3 still validates pre-1.0 delivery tickets so they
  can be terminalized in place; a new arc is an intent instead.

Unavailable, stale, unauthorized, pending, invalid, or contradictory evidence
does not close work.

## Public operations

Concurrent mutations refuse when authoritative Map or Ticket state changes,
so a caller re-reads instead of overwriting another session. Unsupported
filesystem safety assumptions refuse before mutation. The exact Python call
templates below match the implemented scripts; capture a fresh revision when
the signature requires it and reuse `operation_id` on retry.

- Start delivery: the installed
  `start_delivery.py` command in `## Command surface`. It writes
  `docs/loom/intent/<change-id>.md` with `originator: map:<map-id>` and
  `map: <map-id>`, then appends the `delivery-intent:` line to Notes. It
  refuses an unknown or already-satisfied criterion, a non-slug change-id, a
  charting or immutable Map, and an existing intent bound to another Map.
  Re-running with the same change-id reuses the intent and rewrites nothing.
- Claim:
  `map_transaction.claim_ticket(map_dir, ticket_slug, owner=owner, claimed_on=date, operation_id=operation_id, expected_revision=revision)`
- Update blockers:
  `map_transaction.update_blockers(map_dir, ticket_slug, blockers, operation_id=operation_id, expected_revision=revision)`
- Close and re-chart:
  `map_transaction.close_and_rechart(map_dir, ticket_slug, gist=gist, resolution=resolution, unknowns=unknowns)`
  A legacy delivery ticket also passes current inputs, only to terminalize a
  pre-1.0 arc:

  ```python
  delivery_closure=map_transaction.DeliveryClosureInputs(
      brief_text=brief_text,
      plan_text=plan_text,
      acceptance_satisfied=acceptance_satisfied,
      review_head=review_head,
      verification_head=verification_head,
      pr=pr,
      pr_roles=pr_roles,
      pr_owners=pr_owners,
      ownership_complete=True,
  )
  ```

  Current PR/check evidence is re-evaluated before closure.
- Archive a clear Map:
  `map_transaction.archive_map_transition(map_dir, repo_root=repo_root)`
- Retire charting or active work:
  `map_transaction.retire_map(map_dir, ratified_by=name, ratified_on=date, reason=reason, repo_root=repo_root)`

Close and re-chart records Map-side effects before terminalizing the Ticket,
routes every newly exposed unknown, and reports Map-clear eligibility. It does
not silently perform or claim whole-Map acceptance.

`unknowns` is a list of `map_transaction.UnknownRoute` values. Construct one
as `map_transaction.UnknownRoute(text="Measure parser latency", destination="ticket", ticket_slug="measure-latency", ticket_type="research")`.
The exact grammar is:

- `text` is non-empty after trimming.
- `destination` is exactly `fog`, `ticket`, or `out-of-scope`.
- A `ticket` destination requires `ticket_slug` matching
  `[a-z0-9]+(?:-[a-z0-9]+)*` and `ticket_type` equal to `grilling`, `research`,
  or `prototype`.
- Only a `ticket` route may carry `ticket_slug` or `ticket_type`; both are
  `None` for `fog` and `out-of-scope`.
- The tuple `(destination, text, ticket_slug)` is unique within one close, and
  every ticket route also has a unique `ticket_slug`.

Before every close-time gate, run the risk-front-loading pass in
`prototype-contract.md` over newly exposed unknowns. A high-risk assumption
that needs human reaction to a candidate becomes a one-sitting prototype
Ticket; a machine-measured feasibility question remains research. Then run
validate, link, and fog gates in that order.

## Schema-v2 migration

Migration is evidence-based, previewable, and idempotent. First run the
zero-write `preview = migrate_map_v3.preview_migration(map_dir)`. Inspect its
source digests and closure classifications. Only then run
`migrate_map_v3.apply_migration(map_dir, preview)`.

V2 `task` and feasibility `prototype` names are not mechanically renamed.
Factual or measured evidence becomes research; a formally delivered slice
becomes a legacy delivery ticket and must already have a canonical reciprocal
Brief; a human-evaluated candidate becomes prototype; a ratified value decision
becomes grilling. Ambiguity refuses. Any source, membership, or binding change after
preview refuses apply. Repeating an applied migration produces no duplicates.

## Command surface

These exact runnable templates match the shipped CLI parsers:

- `python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/map_init.py" "<map-id>" --repo-root "<path>"`
- `python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/map_store.py" validate "<map-dir>" --repo-root "<path>"`
- `python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/check_map_links.py" "<map-dir>" --repo-root "<path>"`
- `python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/check_map_fog.py" "<map-dir>" --repo-root "<path>"`
- `python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/map_progress.py" "<target>" --repo-root "<path>"`
- `python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/start_delivery.py" "<map-dir>" "<DA-id>" "<change-id>" --repo-root "<path>"`

`${CLAUDE_PLUGIN_ROOT}` is a load-time substitution performed when Claude or
Codex renders the skill, not a run-time shell variable. Quoting the installed
script and path placeholders keeps the rendered argv safe when paths contain
spaces.

`map_progress.py` accepts a repository root, Ticket, or Plan and optionally
`--map-id <map-id>`. It is read-only. `check_map_fog.py` optionally accepts
`--base <git-ref>`; otherwise it resolves the default comparison base.

Top-level re-entry states are exactly `absent`, `broken`, `ambiguous-live`,
`live`, `blocked`, `claimed`, and `da-gap`. Legacy delivery phase values are
separate and resolve only for pre-1.0 delivery tickets: `unbriefed`, `briefed`,
`planning`, `implementing`, `reviewing`, `finishing`, `repair-required`, and
`delivered`.

`map_init.py` and `start_delivery.py` are the writer carve-outs: `map_init.py`
exits `0` on create, `1` on an existing store or operational error, and `2` on
a rejected slug; `start_delivery.py` exits `0` when the intent is created or
reused, `1` on an operational failure, and `2` on any structural refusal. The
four reader commands share:

- `0` — clean.
- `1` — missing, unreadable, unavailable, or environmental failure.
- `2` — readable input violates schema or relation rules.

A caller never parses prose output to distinguish these cases.
