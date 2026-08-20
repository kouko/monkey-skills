# DIRECTION.md Charter

SSOT for the rules governing every consuming repo's `docs/loom/DIRECTION.md`
(and its scaffold template) — those files point here, never copy this
block back into themselves. Read this on demand when editing
`DIRECTION.md`; it is not preloaded by `family-reception.md`.

- `## Now` is GENERATED from COMMITTED-NEXT entry files by
  `scripts/backlog_index.py --direction-write docs/loom/DIRECTION.md`
  (repo-root first, else the loom-code plugin copy) — never hand-edit it.
- `## Now` is a PARALLEL ACTIVE SET, not a serial queue: one entry
  typically maps to one worktree/lane; the ≤5 cap is parallel-steering
  capacity.
- `## Next` (scaffolded) and an optional `## Later` — a repo may add
  one, it is not part of the scaffold — are human-written themes
  only; a `## Next` line MAY point at a roadmap entry in
  `docs/loom/backlog/` by filename (the filename's date prefix —
  YYYY-MM-DD — is a file identifier, exempt from the no-dates rule
  below).
- No dates anywhere in this file (entry names inside the generated
  `## Now` are exempt — file identifiers, not schedule promises).
- Betting promotes backlog entries to COMMITTED-NEXT — user-only;
  agents never promote.
- On a `## Now` merge conflict: take either side wholesale, then
  regenerate via `--direction-write` — never hand-merge.
