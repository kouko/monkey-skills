# Branch-end round 23 — re-review after the round-22 fixes

Re-review delta: `65c55387..e8b5a6fe`. Same two lenses and vendors as round 22.

## codex-review-docs-branch-end-r23 (openai, lens: docs) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: docs
reviewed_sha: c3c4d478
rereview_of:
  - "R22-C1: still-open — 32cf87d3 adds a blind-run addendum, but it tests b61b87ff rather than the final pre-review tree e8b5a6fe; its dispatch totals are already stale."
  - "R22-C2: closed — f01ea57b marks the old guard as historical and identifies the current repo-local loom-checker path."
  - "R22-C3: closed — f01ea57b updates the memory index and entry to the current Claude Code and Codex hook surfaces."
  - "R22-C4: closed — f01ea57b states both trailer duty and the spec/intent/plan/docs/evidence/review exemptions."
  - "R22-C5: closed — ea5c902a documents both failure modes, their return paths, and the spec exemption."
dimension_scores:
  omission: PASS
  ambiguity: PASS
  inconsistency: NEEDS_REVISION
  incorrect-fact: NEEDS_REVISION
  missing-population: PASS
findings:
  - severity: fatal
    dimension: incorrect-fact
    anchor: "docs/loom/2026-09-02-simple-loom-flow/blind-run-report.md:3"
    text: "R22-C1 remains open. The report calls b61b87ff the tested W4-fix-round tree, but two later commits changed the report and review.json before this re-review. At HEAD, review.json contains 85 dispatches (44 implementers, 30 reviewers, 7 blind-runners, 4 adversaries), contradicting the report's 79/40/28/7/4 at lines 47 and 251. It therefore is not the requested branch-end acceptance report."
    fix: "Run the blind-run delta against the final pre-review SHA, update the header and all derived counts/results, and ensure no artifact-changing commit follows it before review dispatch."
  - severity: fatal
    dimension: inconsistency
    anchor: "docs/loom/2026-09-02-simple-loom-flow/plan.md:193"
    text: "W4-06 still says scaffold overwrite is an open question that will not be fixed in this change, while f79a337a fixes it and blind-run-report.md:233-234 presents merging existing hooks as current verified behavior."
    fix: "Mark this risk as superseded by f79a337a and record that the scaffold now merges Loom's entry while preserving existing hook blocks."
  - severity: fatal
    dimension: incorrect-fact
    anchor: "docs/loom/2026-09-02-simple-loom-flow/concept-model.md:173"
    text: "The concept model still says checker recomputation ignores all of .codex/. Commit 8331f6c6 changed the implementation to exempt only scaffold-owned paths under .codex/hooks/, specifically so adopting-repo files such as other-hook.sh remain visible."
    fix: "Replace the whole-.codex exemption claim with the exact scaffold-owned exemption and state that other .codex files and non-scaffold hook files remain in changed_paths."
  - severity: fatal
    dimension: incorrect-fact
    anchor: "loom-code/README.md:57"
    text: "The README says the checker has 20 rules. Running `python3 loom-code/scripts/loom_checker.py --list-rules` prints 27 rules, matching concept-model.md:160."
    fix: "Change 20 to 27, or avoid a duplicated count by directing readers to `--list-rules` as the rule-count source of truth."
  - severity: fatal
    dimension: incorrect-fact
    anchor: "docs/loom/2026-09-02-simple-loom-flow/review.json :: \"the commits' short shas above are pre-rewrite\""
    text: "Six orchestrator-inline dispatch notes still label the 14 listed short SHAs as pre-rewrite. Round 22 already established that those SHAs were remapped by 2ac26023 and resolve in the current history; e8b5a6fe retained the false qualifier while restructuring the dispatch entries."
    fix: "Replace the qualifier in all six notes with the recorded fact that 2ac26023 remapped the listed SHAs to their post-rewrite successors."
notes: []```

Disposition: C2–C5 confirmed closed. New findings R23-C1 (report counts drift with every dispatch-record commit), R23-C2 (plan W4-06 risk note), R23-C3 (§7 whole-.codex claim), R23-C4 (README 20→27) fixed in the docs commit that follows this file; R23-C5 (= R22-O4) is scheduled for the review-only commit. A docs re-review (round 24) is owed.
