---
name: a-single-package-suite-failure-during-a-concurrent-run-in-the-same-tree-is-rerun-before-it-is-believed
description: A test that patches a real repo file in place (the contract manifest, restored in a finally block) makes every other worker that reads that file fail during the patch window — under xdist or a concurrent run in the same tree that shows up as exactly one failure no rerun reproduces; give the checker an override (env var or flag) so tests point it at a scratch copy, and never write into the tree from a test
type: gotcha
sources:
  - resource: 2026-09-05-artifact-charter-boundaries-and-edit-rights — three checkpoints in one day each showed "1 failed" while a fresh reviewer was running the same command in the same tree; every solo rerun was green (1656, 1687, 1716 passed)
---

At three separate checkpoints the orchestrator's package run and a
reviewer's independent run overlapped in one worktree. Each time one test
failed, a different one each time, and two solo reruns came back green.
The suite contains tests that write scratch files under the repo and
tests that glob evidence directories, so two runners can see each other's
temporary state.

**Cause found later:** two permanent tests and two probes rewrote `loom-code/contract/manifest.yaml` in place to drop a policy id, restoring it in `finally`; under `-n auto` any worker that loaded the manifest inside that window failed with a charter or policy error. The fix is an override the checker reads (`LOOM_MANIFEST_PATH`) so the test patches a copy under tmp_path.

**Why:** a recorded package-tests probe is re-run by the push gate in a
clean tree, so a phantom failure costs a round of investigation, not a
merge — but a phantom pass would be worse, and the same collision can hide
a real failure behind "flaky".

**How to apply:** a test never writes into the repository tree; when it must
change what the checker reads, it sets the override to a scratch copy. When a
package run shows a single failure, grep the suite for `write_text` on a
repo path before calling it flaky; rerun alone and record the solo numbers.
