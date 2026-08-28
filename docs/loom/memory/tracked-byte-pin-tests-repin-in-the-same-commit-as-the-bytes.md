---
name: tracked-byte-pin-tests-repin-in-the-same-commit-as-the-bytes
description: A test that pins a fingerprint of a plugin's TRACKED BYTES (the complexity-evidence candidate SHA-256s, any cold-package hash) goes red on EVERY content commit to that plugin — the re-pin is part of each such commit, not a cleanup afterward; batching one re-pin per wave-commit and folding it into the last content commit of the wave keeps every commit's suite green without a churn commit per edit
type: gotcha
origin: check-wayfinder decision-map arc (2026-08-28) — the loom-code/loom-design candidate fingerprints in docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md were re-pinned eight times across the branch; implementers repeatedly mis-reported the red pin test as "pre-existing/unrelated" because their baseline claim predated the sibling wave's edits
---

The stage-specific-complexity evidence report pins each plugin's
tracked-tree fingerprint, so any commit that changes any tracked file
under loom-code/ or loom-design/ — a doctrine line, a version bump, a
test comment — turns the pin test red until the report's candidate
SHA-256 lines are recomputed. Two traps recurred: (a) dispatched
implementers, whose file allowlist excludes the report, read the red
test as pre-existing noise and reported DONE_WITH_CONCERNS against a
stale baseline; (b) re-pinning before the LAST edit of a wave wastes
the pin — the orchestrator's re-pin belongs in the wave's final
content commit (compute via the test module's own
`_tracked_worktree_fingerprint`, both plugins, one edit). Same
discipline applies to any sibling pin the release ritual owns: the
shipping-version pin tests and the skill-compaction dependency
snapshots move WITH the commit that moves their subject, never after.
