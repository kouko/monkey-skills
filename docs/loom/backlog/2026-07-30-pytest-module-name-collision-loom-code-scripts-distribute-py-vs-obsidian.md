---
name: 2026-07-30-pytest-module-name-collision-loom-code-scripts-distribute-py-vs-obsidian
description: pytest module-name collision: loom-code/scripts/distribute.py vs obsidian/scripts/distribute.py
status: OPEN
origin: 2026-07-30 chore-description-diet whole-branch review, both code arms independently reproduced (stash-and-rerun on main confirmed pre-existing).
start: next time a whole-repo pytest run is wanted, or a third `distribute.py` appears.
---

- Start: next time a whole-repo pytest run is wanted, or a third `distribute.py`
  appears.
- Origin: 2026-07-30 chore-description-diet whole-branch review, both code arms
  independently reproduced (stash-and-rerun on main confirmed pre-existing).
- What: running the two dirs in ONE pytest invocation caches whichever
  `distribute` imports first under `sys.modules`, failing 5 obsidian tests
  (`test_distribute.py` / `test_verify_drift.py` — `AttributeError`); each dir
  is green in isolation. Fix via per-dir conftest sys.path isolation, unique
  module names, or packageizing the scripts dirs.
