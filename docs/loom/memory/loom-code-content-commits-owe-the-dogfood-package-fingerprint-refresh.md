---
name: loom-code-content-commits-owe-the-dogfood-package-fingerprint-refresh
description: Any commit that changes a tracked file under loom-code/ stales the `loom-code candidate SHA-256` line pinned in docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md and turns scripts/test_stage_specific_complexity_behavior_evidence.py red — the narrow loom-code/scripts suite does NOT catch it, only the full `pytest loom-code/scripts/ scripts/` floor does; refresh the line with `_tracked_worktree_fingerprint('loom-code')` in the same commit, and re-run the FULL floor after any post-review fix that touches loom-code/
type: gotcha
origin: contract-repair-post-v3 (2026-08-31) refreshed the line twice — once at T13 and again after whole-branch-review fixes touched SKILL.md + batch_review_cli.py without re-running the full floor (reviewer caught it as a 🔴); #764 and #766 made the same one-line refresh
---

The dogfood record binds the loom-code package bytes to a SHA-256 so
its live-run numbers cannot be quietly re-attributed to a different
tree. The binding is enforced by a test under `scripts/`, not under
`loom-code/scripts/`, so an implementer who runs "the loom-code suite"
after editing a loom-code file sees green and ships a red CI.

Recognise it by: `test_report_binds_baseline_and_final_candidate`
failing with two 64-hex digests that differ, right after a commit that
touched anything tracked under `loom-code/`.

Correct path: compute the new value with the test module's own helper
(`_tracked_worktree_fingerprint('loom-code')`), replace the
`loom-code candidate SHA-256:` line in the dogfood record, and commit
it with the change that staled it. The record lives under `docs/`, so
editing it does not perturb the fingerprint it pins. A late-round fix
(review round 2/3) that touches loom-code owes the refresh again — run
the full `pytest loom-code/scripts/ scripts/` floor before pushing, not
the narrow suite that happens to be nearby.
