---
name: 2026-08-31-loom-design-unified-pytest-root
description: loom-design's scripts run as five separate per-directory pytest jobs instead of one shared pytest root
status: closed
origin: 2026-08-31 — three-plugin script audit (Phase 3 item 3c), deferred from docs/loom/specs/2026-08-31-decision-map-script-cleanup.md §Out of Scope
start: event — the next time a loom-design script directory is added and needs its own CI job, or a cross-directory test needs to import two station modules
---

`loom-design/scripts/` today has no shared pytest root: every station
directory gets its own CI job invoking pytest against just that directory.
Five such invocations exist across three workflow files:

- `.github/workflows/loom-pipeline-ci.yml:72` — `python3 -m pytest loom-design/scripts/pipeline/ -q`
- `.github/workflows/loom-siblings-ci.yml:62` — `python3 -m pytest loom-design/scripts/interface/ -v`
- `.github/workflows/loom-siblings-ci.yml:82` — `python3 -m pytest loom-design/scripts/principles/ -v`
- `.github/workflows/loom-siblings-ci.yml:102` — `python3 -m pytest loom-design/scripts/discovery/ -v`
- `.github/workflows/loom-spec-ci.yml:53` — `python3 -m pytest loom-design/scripts/spec/ -v`

Goal: collapse these to one pytest root (one `loom-design/scripts/`
invocation, one CI job) instead of five hand-maintained per-directory
commands that must each be updated whenever a new station directory is
added.

Why per-directory invocation is the workaround today: the closed entry
`docs/loom/backlog/2026-07-30-pytest-module-name-collision-loom-code-scripts-distribute-py-vs-obsidian.md`
diagnosed that running sibling script directories in one pytest process
collides on module identity — pytest caches same-named modules
(`distribute.py` in that case) under `sys.modules` keyed by basename, so
whichever directory's module imports first wins and the other directory's
same-named tests fail with `AttributeError`. loom-design's five station
directories are exposed to the same collision risk the moment two of them
share a module basename or a cross-directory test tries to import two
station modules at once; per-directory jobs sidestep it by construction,
at the cost of a growing job list. A unified root needs the same fix
that entry proposed but never applied: per-directory conftest sys.path
isolation, unique module names, or packageizing the scripts directories.

Closed — shipped on branch `loom-script-refactor-phase3`. A `pytest.ini`
at `loom-design/scripts/` now sets `--import-mode=importlib` plus a
`pythonpath` line enumerating the five station directories, so
`python3 -m pytest loom-design/scripts/` runs the whole plugin suite in
one invocation (1017 passed) without the module-basename collision this
entry described. The five per-directory CI jobs collapsed to one in
`.github/workflows/loom-pipeline-ci.yml`; `loom-siblings-ci.yml` and
`loom-spec-ci.yml` were deleted.
