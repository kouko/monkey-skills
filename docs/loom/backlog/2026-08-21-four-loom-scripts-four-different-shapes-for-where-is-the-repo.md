---
name: 2026-08-21-four-loom-scripts-four-different-shapes-for-where-is-the-repo
description: the loom script family answers "where is the repo/store" four different ways — backlog_index takes --store with no --repo-root and resolves it against the CWD, the two brief gates take a positional path plus --repo-root with git auto-detection, check_north_star_link takes a bare positional store path, and archive_change_folder takes a positional identifier plus an optional positional root; a newcomer guessing the wrong flag gets an argparse error rather than a pointer
status: open
origin: 2026-08-21 dissolve-direction-layer end-to-end dogfood, finding #4 — a cold agent walking the whole queue lifecycle hit the inconsistency five scripts in a row and guessed --root for backlog_index before finding --store
start: the next arc that touches two or more of these scripts' argument parsing for any other reason, or the first time a consuming repo other than kumiko adopts the queue layer
---

- Start: the next arc that touches two or more of these scripts' argument
  parsing for any other reason, or the first time a consuming repo other
  than kumiko adopts the queue layer

- Origin: 2026-08-21 dissolve-direction-layer end-to-end dogfood, finding
  #4 — a cold agent walking the whole queue lifecycle hit the
  inconsistency five scripts in a row and guessed --root for
  backlog_index before finding --store

- What: four scripts, four shapes for the same question.

  | Script | Shape |
  |---|---|
  | `backlog_index.py` | `--store STORE`, no `--repo-root`, resolved against the CWD |
  | `check_queue_relation.py` / `check_onramp_choice.py` | positional `brief_path` + `--repo-root`, auto-detected via `git rev-parse --show-toplevel` |
  | `check_north_star_link.py` | bare positional `store_path`, no flag at all |
  | `archive_change_folder.py` | positional `<identifier> [root]`, hand-rolled argv parsing |

  Per call the friction is small — guess wrong and argparse says
  `unrecognized arguments` rather than pointing at the right flag. It
  compounds across a walk that touches five scripts in one session, which
  is exactly what a close-out does.

- Why this is not just tidiness: `backlog_index.py` is the one whose
  CWD-relative resolution has now produced TWO shipped fail-open defects
  on one arc — a typo'd `--store` reading as a clean empty store, and a
  `--output` default that overwrote a different repo's `BACKLOG.md`. Both
  are fixed, but the underlying asymmetry (this script alone has no
  `--repo-root` and no git auto-detection) is what made both reachable.

- Shape when it happens: give `backlog_index.py` the same `--repo-root`
  with git auto-detection its siblings have, keeping `--store` as an
  explicit override. That is additive and breaks no caller. Unifying the
  other three is a larger and more debatable change — `archive_change_folder`
  hand-rolls its parsing deliberately (it ships standalone), and
  `check_north_star_link`'s bare positional is the narrowest surface of the
  four. Do the additive half first and re-judge.

- Not covered here: the four scripts also differ in whether an absent
  store is a failure or a loud N/A, which is deliberate and documented —
  `check_queue_relation` exempts a repo that never adopted the queue
  layer, `backlog_index` refuses because it was pointed at a store
  explicitly. Do not "unify" that one.
