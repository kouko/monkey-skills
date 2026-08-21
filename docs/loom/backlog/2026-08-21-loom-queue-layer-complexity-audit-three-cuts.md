---
name: 2026-08-21-loom-queue-layer-complexity-audit-three-cuts
description: a complexity audit of the dissolve-direction-layer arc measured concept count 7 to 5 (not the brief's claimed 6 to 1) and named three cuts — delete BACKLOG.md plus its --write/--check pair as the same materialized-view-plus-drift-guard the arc set out to kill, delete the archive tier, and put bet/serves:/PURPOSE.md on probation as zero-instance concepts
status: open
origin: 2026-08-21 dissolve-direction-layer close-out — kouko asked for a complexity critique alongside the whole-branch review fixes; its verdict was PROCEED-WITH-CAVEAT and the three cuts were deliberately not acted on inside that branch
start: the next time this repo actually places a bet (which makes the zero-instance concepts real and settles the probation), or the next arc that touches backlog_index.py's --write/--check pair for any other reason
---

- Start: the next time this repo actually places a bet (which makes the
  zero-instance concepts real and settles the probation), or the next arc
  that touches backlog_index.py's --write/--check pair for any other reason

- Origin: 2026-08-21 dissolve-direction-layer close-out — kouko asked for a
  complexity critique alongside the whole-branch review fixes; its verdict
  was PROCEED-WITH-CAVEAT and the three cuts were deliberately not acted on
  inside that branch

- What the audit measured (numbers as reported then; re-measure before
  acting, per this store's own standing lesson that a count measured by the
  commit that changes it is wrong twice):
  mechanism −563 lines, tests −1073, arc paperwork +1029. Concept count
  **7 → 5**, not the brief's claimed 6 → 1. Its summary line was
  「這一弧溶解了一個空的視圖，出貨了一個空的查詢」.

- Cut 1 — **`docs/loom/BACKLOG.md` plus `--write`/`--check`.** This is the
  same materialized-view-plus-drift-guard pattern the arc set out to kill,
  one file over: a `<!-- GENERATED … do not edit by hand. -->` document
  regenerated from the entries, with a `--check` drift detector guarding it,
  while `--ready` answers the same question live from the store. Verified at
  the time: the file was 148 lines and every question it answers `--ready`
  answers without it. The counter-argument worth weighing is that
  `BACKLOG.md` is the surface a HUMAN browsing the repo on GitHub lands on,
  which `--ready` is not — so this is a real trade-off, not an obvious cut.

- Cut 2 — **the archive tier.** Zero instances: no `archive/` directory
  exists in this store. It costs an invariant (`_check_archive_tier`), a
  branch in every reader, and a documented precedence rule (archive
  overrides status).

- Cut 3 — **probation for `bet`, `serves:` and `PURPOSE.md`.** All three
  were zero-instance at close-out: 0 `bet` entries, no `PURPOSE.md` in this
  repo. A concept with no instances cannot be validated by use, and the
  close-out betting prompt has now fired once with the user declining to
  place a bet. Probation means: if the next two close-outs also decline,
  ask whether the concept is earning its machinery rather than assuming it
  is.

- Why not then: the arc's scope was fixed by the user before implementation
  ("我想一次做完" over a named list), and every cut here widens it. Acting
  on an audit of a branch inside that same branch also destroys the audit's
  independence.
