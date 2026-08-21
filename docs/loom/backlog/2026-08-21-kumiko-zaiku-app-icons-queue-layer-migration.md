---
name: 2026-08-21-kumiko-zaiku-app-icons-queue-layer-migration
description: kumiko-zaiku-app-icons still carries a live DIRECTION.md with two COMMITTED-NEXT entries; docs/loom/plans/2026-08-21-dissolve-direction-layer.md deleted the direction layer from loom-code, so that repo needs a guided migration to the backlog store's bet/open/closed vocabulary
status: open
origin: this repo's own dissolve-direction-layer arc (docs/loom/plans/2026-08-21-dissolve-direction-layer.md) deleted DIRECTION.md, its generator verbs, charter, and template; kumiko-zaiku-app-icons is an external repo that adopted the now-retired direction layer and has not migrated
start: the next time kumiko-zaiku-app-icons runs a loom gate against its DIRECTION.md — check_queue_relation.py (this arc's renamed queue gate) fails loudly there and fails loudly on the first entry whose status is outside the closed vocabulary, naming that entry and its status, so the migration is guided rather than guessed
---

- Origin: this repo's own dissolve-direction-layer arc (docs/loom/plans/2026-08-21-dissolve-direction-layer.md) deleted DIRECTION.md, its generator verbs, charter, and template; kumiko-zaiku-app-icons is an external repo that adopted the now-retired direction layer and has not migrated
- Start: the next time kumiko-zaiku-app-icons runs a loom gate against its DIRECTION.md — check_queue_relation.py (this arc's renamed queue gate) fails loudly there and fails loudly on the first entry whose status is outside the closed vocabulary, naming that entry and its status, so the migration is guided rather than guessed

What: `kumiko-zaiku-app-icons` (the external repo whose 2026-08-10
session first surfaced the milestone-layer gap recorded in the
sibling entry `2026-08-10-loom-lacks-a-milestone-layer-between-plan-
stage-and-direction.md`) still carries a live `docs/loom/DIRECTION.md`
with two `## Now` entries in the retired `COMMITTED-NEXT` status word.
This arc (`docs/loom/plans/2026-08-21-dissolve-direction-layer.md`)
deleted `DIRECTION.md`, its generator verbs, its charter
(`loom-code/hooks/direction-charter.md`), and its scaffold template
from `loom-code` itself — but a plugin update only changes what a repo
reads going forward, not files an external repo already wrote by hand.
`kumiko-zaiku-app-icons`'s own `DIRECTION.md` instance is unaffected
until someone migrates it.

Why this is guided, not guessed: `check_queue_relation.py` (the
renamed `check_direction_freshness.py`, Task 4 of this arc) no longer
resolves `in-queue:`/`displaces:` against a `DIRECTION.md` `## Now`
list at all — it resolves against `docs/loom/backlog/` entries
carrying `status: bet`. Once `kumiko-zaiku-app-icons` next runs that
gate (or `backlog_index.py --validate`, which rejects any status
outside the closed `open`/`bet`/`closed` vocabulary), the failure
message names the live candidates to promote instead of a blank
"unresolved" — the mechanism this arc shipped for exactly this
transition.

Next step for that repo: convert the two `COMMITTED-NEXT` entries in
its `DIRECTION.md` into backlog-store entries under
`docs/loom/backlog/` with `status: bet`, delete `DIRECTION.md` once
nothing reads it, and re-run `backlog_index.py --write` +
`--validate` there — the same sequence Task 13 of this arc ran on
this repo.
