---
name: headless-branch-plugin-testing-recipe
description: Recipe for behaviorally testing an unpushed branch's Claude Code plugins headlessly — --plugin-dir wrapper, neutral empty cwd, probe hook injection first, parse_corpus takes content
type: process
origin: PR #488 (loom family connective tissue, firing tests 2026-07-04)
---

To behaviorally test Claude Code plugins from an UNPUSHED branch
(e.g. with the firing/refusal harness
`loom-code/scripts/loom_firing_harness.py`): installed plugins track
GitHub main, so a normal session exercises stale code — the cache's
version directories are the tell. Recipe:

1. **Wrapper script per plugin** overriding the installed copy:
   `exec claude "$@" --plugin-dir <repo>/<plugin>` — feed the
   wrapper into the harness's `claude_bin` seam (the harness
   parameter that names the claude binary to invoke).
2. **Run from a neutral EMPTY directory** — leftover artifacts in a
   working/scratchpad directory contaminated 3 test records by
   giving the model unintended context.
3. **Probe that the hook injects BEFORE burning corpus runs** — one
   cheap probe session to confirm the branch's hook content actually
   loads, before spending tokens on the full corpus.
4. **`parse_corpus` takes file CONTENT, not a path** — read the file
   and pass the text.

**Why:** without the wrapper you silently test main instead of your
branch; without the empty directory and the probe, failed records
look like routing bugs when they are setup bugs.

**How to apply:** follow the four steps above. Before running any
corpus, also read the behavioral-test method traps (#1–#6) in the
module docstring of `loom-code/scripts/loom_firing_harness.py` —
that docstring is the authoritative trap list; this file
deliberately does not duplicate it.
