---
name: importing-a-module-runs-its-module-level-imports
description: A test that uses only a module's PURE helpers still runs that module's module-level imports — so its non-stdlib module-level deps (requests/edgar/etc.) must be stubbed in sys.modules BEFORE the import, or the offline CI env errors at fixture setup (module import != function call)
type: gotcha
origin: multi-filing historical fetch scope A, CI offline-suite failure on PR #573 (feat-multifiling-historical-fetch, 2026-07-16)
---

Importing a module executes ALL of its module-level statements, including its
top-level `import` lines — even when the caller only intends to use a couple of
that module's PURE (dict->dict, no-I/O) helper functions. So a test that reaches
into a data/IO module for its pure helpers still needs that module's non-stdlib
module-level dependencies satisfied at IMPORT time. Real case: an analysis-layer
e2e test imported `sec_edgar_client` only for `_is_dimensional_revenue_fact` /
`_build_dimensional_revenue_fact` (pure), but the module does a top-level
`import requests`; the offline CI suite (which installs neither `requests` nor
`edgartools`) errored `ModuleNotFoundError: No module named 'requests'` at
FIXTURE SETUP. Local runs passed because the dev env had `requests` installed —
so it is invisible until the offline CI env exposes it.

**Why:** `import module` != `module.func()`. The module object is built by
running its body once, top to bottom, on first import; a lazy per-function
import defers only the deps *inside* functions, never the ones at module scope.
"I only call the pure functions, so I don't need the network deps" is a false
inference — the import itself pays for every module-level dep.

**How to apply:** when a test imports a module that has non-stdlib module-level
imports (a data/IO layer, an SDK wrapper) but you only exercise its pure
helpers, stub those deps in `sys.modules` BEFORE the import and restore them in
a `finally` — e.g. `sys.modules["requests"] = mock.MagicMock()` then
`importlib.import_module(...)`. The stubs are never exercised (the pure helpers
don't touch them); they only satisfy the import. Mirror the repo's existing
offline-import fixture rather than inventing a new one, and reproduce the
offline condition locally (block the dep via an import hook that still honors
sys.modules) — a dev env with the dep installed hides the failure. Better still,
prefer feeding the test analysis-shaped fixtures so it need not import the IO
layer at all. Relates to [[fixtures-mirror-producer-shape]].
