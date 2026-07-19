---
name: test-must-land-in-the-ci-lane-its-plugin-runs
description: A new test only gates if it lands in the exact lane its plugin's CI actually runs — dev-workflow CI runs ONLY dev-workflow/tests/test-*.sh (bash glob, no pytest job over dev-workflow/skills/**), and loom-code CI runs pytest loom-code/scripts/ + only 3 explicitly-named integration .sh (it does NOT glob loom-code/tests/*.sh); a test dropped in the wrong lane is a dark test that passes locally and never gates
type: gotcha
origin: PR closeout-privacy-gate (2026-07-19) — caught twice at plan + execution time
---

Two different plugins in this repo run their CI test suites two
different ways, and neither globs everything:

- **dev-workflow** (`.github/workflows/dev-workflow-ci.yml`) runs ONLY
  `for t in dev-workflow/tests/test-*.sh; do bash "$t"; done`. There is
  **no pytest job anywhere in CI** that covers `dev-workflow/skills/**`.
  A `test_*.py` co-located next to a skill script (mirroring
  distill-sessions) runs locally and is a real dev-time suite, but it
  **never gates in CI**. To gate a `dev-workflow/skills/` behavior, add
  a bash CLI test under `dev-workflow/tests/test-*.sh` that exercises the
  real script (exit codes / output), not only a pytest.
- **loom-code** (`.github/workflows/loom-code-ci.yml`) runs
  `pytest loom-code/scripts/ scripts/ .claude/hooks/` PLUS only **three
  explicitly-named** integration shells
  (`tests/integration/test-command-surface-*.sh`,
  `test-rule-sheet-drift.sh`). It does **NOT** glob `loom-code/tests/*.sh`.
  A new bash test dropped in `loom-code/tests/` (outside those three
  named) is dark; the gating lane for a SKILL.md prose pin is a
  `loom-code/scripts/test_*.py` pytest (precedent:
  `test_finishing_merge_path_guidance.py`).

Caught twice in one arc: a plan first routed finishing-SKILL pins to
`loom-code/tests/*.sh` (dark) → moved to `loom-code/scripts/test_*.py`;
and a `privacy-scan.py` pytest had no CI gate → added a paired bash CLI
test under `dev-workflow/tests/`.

**Why:** "the test passes locally" and "the test gates in CI" are
different claims. A dark test gives false regression confidence — the
behavior it guards can break on main with a green check. Test *type*
(pytest vs bash) is not a free choice; it is dictated by which lane the
target plugin's CI actually executes.

**How to apply:** before choosing a new test's type + location, open the
target plugin's `.github/workflows/*-ci.yml` and read the actual `run:`
lines. Place the test where that workflow will execute it: for
`dev-workflow/skills/**`, a bash test in `dev-workflow/tests/`; for a
loom-code SKILL.md/prose pin, a pytest under `loom-code/scripts/`. A rich
pytest may still live beside the code as dev-time coverage, but the
CI-gating test must sit in the lane the workflow runs. (Extends
[[gha-paths-filter-gates-at-workflow-level]]: that entry is about which
*pushes* trigger a workflow; this is about which *tests* a triggered
workflow actually executes.)
