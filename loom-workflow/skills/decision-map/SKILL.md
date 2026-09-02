---
name: decision-map
version: 3.0.0
description: |
  Chart and work through a persistent Outcome Map at docs/loom/maps/<map-id>/ — one long-term outcome-control loop whose fog becomes typed tickets and whose delivery arcs close independently across many sessions. Use for '開地圖' / '開一張決策地圖' / 'chart a decision map' / 'work through the map' / '推進地圖' / 'デシジョンマップを開く' / 'ワークスルー', and to start, resume, claim, re-chart, migrate, retire, or assess a live Map. Not for one self-contained task (use loom-code:write-plan) or one factual question (use research-toolkit).
---

# Decision map

An Outcome Map is one persistent outcome-control loop that advances through
multiple independently closed delivery arcs. It is the long-term control
surface for a Destination whose whole route cannot yet be enumerated. Closing
a delivery arc must not clear the Map.

Exactly three ticket closure types exist: `grilling`, `research`, and
`prototype`. Dependencies order tickets; they never create a `task` or
`unblock` type. A delivery is not a ticket: it is one outcome-advancing
slice promised by an intent, not a generic task and not proof that the whole
Destination is complete.

`MAP.md` and its Tickets are the source of truth for durable outcome state.
Intents, Plans, Git, PRs, and CI retain ownership of delivery progress;
decision-map reads that state but never copies it into the Map or Ticket.

Schema and operation authority lives in `references/map-format.md`. The
prototype boundary lives in `references/prototype-contract.md`. Read both
before charting or mutating a Map.

## Requires loom-code

This is the only loom-workflow skill that depends on loom-code: starting a
delivery writes an intent from loom-code's contract template, and the
checker validates it. Every other loom-workflow tool works with
loom-workflow installed alone. Before the first delivery operation on a
repo, run the contract check and stop on anything but exit 0:

```
python3 <loom-code checkout>/scripts/loom_checker.py contract --require 1.0
```

(Codex form: `python3 .codex/hooks/loom_checker.py contract --require 1.0`.)
Exit 1 means loom-code is missing or older than contract 1.0 — tell the
user to install or update loom-code; charting, grilling, research and
prototype tickets do not need it.

## Store and lifecycle

Every Map has stable identity at `docs/loom/maps/<map-id>/` and uses
`schema_version: 3`. Its states are `charting`, `active`, `clear`, and
`archived`.

- `charting` records the ratified Destination, Destination acceptance
  (`DA-<n>`) criteria, first typed tickets, and monotonic fog (`F-<n>`).
- `active` accepts work-through operations and can close many delivery arcs.
- Map clear is allowed only when fog is empty, all tickets are `closed` or
  `withdrawn`, and every Destination acceptance criterion is satisfied with
  valid evidence and any required human ratification.
- Retirement preserves the stable directory and every historical relation.
  A clear Map may be archived; an active or charting Map may be retired only
  as explicit, named, dated abandonment, never as successful completion.

Clear and archived Maps are immutable history. Later regression or renewed
work creates a successor Map that cites its predecessor.

## Chart

Use `python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/map_init.py" "<map-id>" --repo-root "<path>"`
to create the schema-v3 `MAP.md` template and empty `tickets/` directory.
`${CLAUDE_PLUGIN_ROOT}` is replaced when the skill is loaded; it is not a
run-time shell variable. Fill the Destination,
author at least one stable Destination acceptance criterion, add the first
closure-typed tickets, and record genuine fog.

If every open question can already be stated and there is no fog, stop: the
work needs one intent and `loom-code:write-plan`, not an Outcome Map. Before activation,
run the risk pass from `references/prototype-contract.md`, record
`user-ratified: <name/handle>, <YYYY-MM-DD>`, run
`python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/map_store.py" validate "<map-dir>" --repo-root "<path>"`, then make the explicit
`charting` to `active` state transition and validate again.

## Re-enter and select

The Map is human-named or selected by an explicit recorded signal; topic
similarity never chooses it. Run
`python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/map_progress.py" "<target>" --repo-root "<path>"`
with a repository root, Ticket, or Plan. Add `--map-id <map-id>` when several
live Maps exist. Top-level re-entry states are exactly `absent`, `broken`,
`ambiguous-live`, `live`, `blocked`, `claimed`, and `da-gap`. Legacy delivery
phase values are separate and resolve only for pre-1.0 delivery tickets:
`unbriefed`, `briefed`, `planning`, `implementing`, `reviewing`, `finishing`,
`repair-required`, and `delivered`. The report names the authoritative owner
and gives the next CTA.

Broken is not absent. Repair a broken store before initialization or work.
Within the selected Map, prefer an open ticket whose `blocked-by` targets are
all closed. Never claim blocked work.

## User operations

These are the public workflow operations. Mutations use the functions shown
below from `loom-workflow/skills/decision-map/scripts/`; callers first capture
the current revision where the signature requires it, reuse an operation id on
retry, and surface conflicts rather than weakening the write.

### Start

Start a new Map with the installed `map_init.py` command above.

Start a delivery arc by writing its intent:
`python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/start_delivery.py" "<map-dir>" "<DA-id>" "<change-id>" --repo-root "<path>"`.
It writes `docs/loom/intent/<change-id>.md` carrying `originator: map:<map-id>`
and `map: <map-id>`, and lists that change-id under the Destination acceptance
criterion the slice serves as `- delivery-intent: <DA-id> | <intent path>` in
Notes. Re-running with the same change-id reuses the existing intent and never
rewrites it. Hand the intent to `loom-design:capture-intent` when loom-design
is installed, otherwise to `loom-code:write-plan`; that station owns the
intent, spec, plan, implementation, review, and PR thereafter. The stub is a
skeleton, not checker-clean — fill `kind:` and `needs-design:` and put the
needs-design line in that commit's message before running
`loom_checker.py intent`.

### Delivery state

Delivery state is derived from the intent's own `status:` field and is never
copied into the Map:

- `open` — the arc is not confirmed yet; the criterion stays blocked and no
  second arc opens against it.
- `confirmed <date>` — in delivery, owned by the loom-code stations.
- `closed` — the criterion may be satisfied once its own evidence pointer is
  recorded.
- `withdrawn — <reason>` — note `retired — <reason>` beside the change-id.
  Satisfying that criterion then needs a replacement intent or direct
  Destination acceptance evidence.

The Map is read-only on intents: it reads `status:` and never edits it.

### Resume

Resume with the installed `map_progress.py` command above. This operation is
read-only and reports the owning artifact plus a concrete next CTA. For a
direct Plan query, replace `<target>` with the contained repository-relative
or absolute Plan path.

### Claim

Capture `revision = map_transaction.capture_revision(map_dir)`, then call
`map_transaction.claim_ticket(map_dir, ticket_slug, owner=owner,
claimed_on=date, operation_id=operation_id, expected_revision=revision)`.
Only an open, unblocked ticket in an active valid Map can be claimed.

### Update blockers

Capture a fresh revision, then call
`map_transaction.update_blockers(map_dir, ticket_slug, blockers,
operation_id=operation_id, expected_revision=revision)`. Blockers must be
unique sibling slugs in the same Map; self-edges, missing targets, duplicates,
and cycles are refused.

### Close and re-chart

Call `map_transaction.close_and_rechart(map_dir, ticket_slug, gist=gist,
resolution=resolution, unknowns=unknowns)`. Closure evidence is checked by
ticket type. Closing preserves one durable Decisions-so-far gist and routes
every exposed unknown to fog, a typed ticket, or Out-of-scope, so the next
session can see why the result matters and what remains. Its result reports
Map-clear eligibility; it does not equate one closed delivery with Map
completion.

A legacy `delivery` Ticket also passes
`delivery_closure=map_transaction.DeliveryClosureInputs(...)`; that path exists
only to terminalize pre-1.0 tickets and authors no new arc.

Each item in `unknowns` is a `map_transaction.UnknownRoute`; use the exact
field and destination grammar in `references/map-format.md`. For example:
`map_transaction.UnknownRoute(text="Measure parser latency", destination="ticket", ticket_slug="measure-latency", ticket_type="research")`.

### Migrate v2 to v3

Migration is always preview then apply. Run the zero-write preview
`preview = migrate_map_v3.preview_migration(map_dir)`, inspect every proposed
closure classification and source digest, then run
`migrate_map_v3.apply_migration(map_dir, preview)`. Ambiguous v2 `task` or
feasibility `prototype` evidence refuses. Apply also refuses when any source
or reciprocal delivery binding changed after preview, and retry is idempotent.

### Archive

For a clear Map call
`map_transaction.archive_map_transition(map_dir, repo_root=repo_root)`. For
ratified abandonment call `map_transaction.retire_map(map_dir,
ratified_by=name, ratified_on=date, reason=reason, repo_root=repo_root)`.
Archive changes state at the stable Map path; it never relocates the store.

## Closure types

- `grilling` closes a value, direction, or trade-off decision with a named,
  dated human ratification. Delegate discussion to
  `loom-design:capture-intent` when available.
- `research` closes a factual question with an answer and inspectable
  evidence. Machine-measured feasibility is research.
- `prototype` closes only when a human evaluates or selects a newly created
  candidate artifact and records named, dated ratification. Follow
  `references/prototype-contract.md`.

Delivery tickets written before loom 1.0 stay in place, read-only, and are
never converted; their `brief:` binding and derived delivery phase remain
readable history. No new delivery ticket is authored.

Research may span sessions. Every other ticket should be sized to one sitting.
Terminal `closed` and `withdrawn` Tickets are immutable; corrections become
new fog or follow-up tickets.

## Close-time checks

Before every close-time gate, run the risk-front-loading pass in
`references/prototype-contract.md` over the unknowns exposed by this closure.
If the highest-risk assumption requires human reaction to a candidate, route
it to a one-sitting prototype Ticket; machine-measured feasibility remains
research. Then run all three gates:

- `python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/map_store.py" validate "<map-dir>" --repo-root "<path>"`
- `python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/check_map_links.py" "<map-dir>" --repo-root "<path>"`
- `python3 "${CLAUDE_PLUGIN_ROOT}/skills/decision-map/scripts/check_map_fog.py" "<map-dir>" --repo-root "<path>"`

Exit `0` is clean, `1` is an operational failure, and `2` is a contract
violation. Fix every nonzero result before ending the session. Use
`--base <git-ref>` with the fog checker only when an explicit comparison base
is required.

## See also

- `references/map-format.md` — schema-v3 templates, invariants, operation
  signatures, migration, and command surface.
- `references/prototype-contract.md` — human-evaluated candidate protocol and
  risk-front-loading rule.
