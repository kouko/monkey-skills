---
name: extracting-a-sibling-module-breaks-hand-listed-cold-install-fixtures
description: Extracting shared logic into a new sibling module (git_exec.py, sibling_import.py) silently breaks every test fixture that copies scripts into a cold-install layout by hand-listed path — production copytree is fine, the fixture's list is not; grep test_*.py for copyfile/copytree before the first migration task lands, and add the new sibling to each list in the same task
type: gotcha
origin: branch loom-script-refector (2026-08-31) — Task 7 hit it in test_live_gate_station_receipt.py (6 subprocess tests → ModuleNotFoundError), Task 8's implementer misread the same 12 failures in test_live_host_review_gate.py as pre-existing until the orchestrator checked the branch baseline
---

When a script that other scripts import by sibling name gains a NEW
sibling dependency, any test that materialises a partial plugin tree —
`shutil.copyfile(source_root / relative, target)` over a hand-written
list such as `{"scripts/review_context.py", *RESOURCE_RELATIVE_PATHS.values()}`
— runs the copied script without the new sibling and fails with
`ModuleNotFoundError` only for the subprocess-driven tests. Production
is unaffected because it copies the whole plugin (`shutil.copytree`),
so the failure looks environmental and gets misattributed to
"pre-existing" or "concurrent implementers".

Two habits close it: (1) before dispatching the first task that adds
the import, `grep -ln "copyfile\|copytree" <plugin>/scripts/test_*.py`
and list the hits in the plan task's `Files touched`; (2) never accept
"pre-existing failure" from an implementer without a baseline run at
the branch's merge base — this branch started fully green.
