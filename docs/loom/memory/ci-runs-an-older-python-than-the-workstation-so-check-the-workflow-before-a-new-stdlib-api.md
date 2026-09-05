---
name: ci-runs-an-older-python-than-the-workstation-so-check-the-workflow-before-a-new-stdlib-api
description: The workstation runs Python 3.12 while `.github/workflows/loom-code-ci.yml` pins 3.11, so a stdlib keyword added in 3.12 (`TemporaryDirectory(delete=...)`) passes every local test and raises `TypeError` on every CI run; before using a stdlib API newer than the workflow's `python-version`, run the file once under that interpreter (`uv run --python 3.11 --with-requirements requirements-dev.txt -- python …`), and expect the second-vendor reader to be the one that notices
type: gotcha
origin: 2026-09-05-graduated-probes-independent-of-local-history — wave-end:1 round 1 (2026-09-06); the Codex reader raised it as fatal, the Anthropic reader and thirty-two green probes on 3.12 did not
---

The rehearsal script's first version kept or removed its clone with
`tempfile.TemporaryDirectory(delete=not args.keep)`. That keyword exists
from Python 3.12. The workstation, the implementer's shell and both
adversaries ran 3.12, so 32 probes were green. CI installs 3.11
(`python-version: '3.11'` in the loom-code workflow), where the call
raises `TypeError` before the clone is even made — a red that would have
appeared only after merge, the exact failure class the change exists to
remove.

Only the Codex reader caught it, by reading the workflow file against
the script. The fix is `tempfile.mkdtemp` plus an explicit
`shutil.rmtree` in a `finally`, and a test that runs the script under
3.11 when `python3.11`, `uv python find 3.11`, or the uv-managed
interpreter is present, skipping with the interpreter named otherwise.

**Rule of thumb.** Any `python-version:` pin in the CI workflow that is
older than the workstation's interpreter is a compatibility boundary:
before a new stdlib keyword, `match` form or typing feature, run the
file once under the pinned version. `uv run --python 3.11` makes that a
one-line check.

Related: [[pre-branch-end-ci-rehearsal-uses-full-history-without-a-local-main]],
[[a-failed-call-is-a-non-observation-not-a-wrong-answer]].
