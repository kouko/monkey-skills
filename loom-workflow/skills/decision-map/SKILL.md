---
name: decision-map
version: 3.0.0
description: |
  Chart and work through a persistent Outcome Map at docs/loom/maps/<map-id>/ — one long-term outcome-control loop whose fog becomes typed tickets and whose delivery arcs close independently across many sessions. Use for '開地圖' / '開一張決策地圖' / 'chart a decision map' / 'work through the map' / '推進地圖' / 'デシジョンマップを開く' / 'ワークスルー', and to start, resume, claim, re-chart, migrate, retire, or assess a live Map. Not for one self-contained task (use loom-code:writing-plans) or one factual question (use research-toolkit).
---

# Decision map

An Outcome Map is one persistent outcome-control loop that advances through
multiple independently closed delivery arcs. It is the long-term control
surface for a Destination whose whole route cannot yet be enumerated. Closing
a delivery arc must not clear the Map.

Exactly four closure types exist: `grilling`, `research`, `prototype`, and
`delivery`. A delivery is one outcome-advancing slice, not a generic task and
not proof that the whole Destination is complete. Dependencies order tickets;
they never create a `task` or `unblock` type.

`MAP.md` and its Tickets are the source of truth for durable outcome state.
Briefs, Plans, Git, PRs, and CI retain ownership of delivery progress;
decision-map reads that state but never copies it into the Map or Ticket.

Schema and operation authority lives in `references/map-format.md`. The
prototype boundary lives in `references/prototype-contract.md`. Read both
before charting or mutating a Map.

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

Use `map_init.py <map-id> --repo-root <path>` to create the schema-v3
`MAP.md` template and empty `tickets/` directory. Fill the Destination,
author at least one stable Destination acceptance criterion, add the first
closure-typed tickets, and record genuine fog.

If every open question can already be stated and there is no fog, stop: the
work needs `loom-code:writing-plans`, not an Outcome Map. Before activation,
run the risk pass from `references/prototype-contract.md`, record
`user-ratified: <name/handle>, <YYYY-MM-DD>`, run
`map_store.py validate <map-dir> --repo-root <path>`, then make the explicit
`charting` to `active` state transition and validate again.

## Re-enter and select

The Map is human-named or selected by an explicit recorded signal; topic
similarity never chooses it. Run
`map_progress.py <target> --repo-root <path>` with a repository root, Ticket,
or Plan. Add `--map-id <map-id>` when several live Maps exist. The report
distinguishes absent, broken, live, blocked, claimed, acceptance-gap, and
delivery phases, names the authoritative owner, and gives the next CTA.

Broken is not absent. Repair a broken store before initialization or work.
Within the selected Map, prefer an open ticket whose `blocked-by` targets are
all closed. Never claim blocked work.

## User operations

These are the public workflow operations. Mutations use the functions shown
below from `loom-workflow/skills/decision-map/scripts/`; callers first capture
the current revision where the signature requires it, reuse an operation id on
retry, and surface conflicts rather than weakening the write.

### Start

Start a new Map with `map_init.py <map-id> --repo-root <path>`. Start a claimed
delivery arc with
`start_delivery.start_delivery(ticket_path, brief_path, repo_root=repo_root)`.
It creates or recovers one reciprocal Ticket-to-Brief binding; loom-code owns
the Brief, Plan, implementation, review, PR, and CI thereafter.

### Resume

Resume with `map_progress.py <target> --repo-root <path>`. This operation is
read-only and reports the owning artifact plus a concrete next CTA. For a
direct Plan query, the concrete form is
`map_progress.py <plan-path> --repo-root <path>`.

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
ticket type. The same transaction records exactly one Decisions-so-far gist,
routes every exposed unknown to fog, a typed ticket, or Out-of-scope, and
writes the terminal Ticket last. Its result reports Map-clear eligibility; it
does not equate one closed delivery with Map completion.

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
  `loom-code:brainstorming` when available.
- `research` closes a factual question with an answer and inspectable
  evidence. Machine-measured feasibility is research.
- `prototype` closes only when a human evaluates or selects a newly created
  candidate artifact and records named, dated ratification. Follow
  `references/prototype-contract.md`.
- `delivery` closes one promised outcome slice under the closure policy its
  Brief authors: `pr-ci`, `merged`, or `artifact`. Current formal evidence is
  queried from its owning artifacts; stale or unavailable evidence cannot
  close the Ticket.

Research may span sessions. Every other ticket should be sized to one sitting.
Terminal `closed` and `withdrawn` Tickets are immutable; corrections become
new fog or follow-up tickets.

## Close-time checks

After re-charting, run all three gates:

- `map_store.py validate <map-dir> --repo-root <path>`
- `check_map_links.py <map-dir> --repo-root <path>`
- `check_map_fog.py <map-dir> --repo-root <path>`

Exit `0` is clean, `1` is an operational failure, and `2` is a contract
violation. Fix every nonzero result before ending the session. Use
`--base <git-ref>` with the fog checker only when an explicit comparison base
is required.

## See also

- `references/map-format.md` — schema-v3 templates, invariants, operation
  signatures, migration, and command surface.
- `references/prototype-contract.md` — human-evaluated candidate protocol and
  risk-front-loading rule.
- `references/family-reception.md` — family on-ramp for long, foggy efforts.
