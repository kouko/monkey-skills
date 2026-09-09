# Derived intent delivery state — plan
intent: 2026-09-09-close-intent-after-merge@bf1a64c038a86d3d42469723f7b557690b27927b
spec: docs/loom/2026-09-09-close-intent-after-merge/spec.md@8d163b1e96372feae311b6012ed9588b0d829c3e
charter: 1.0

## Task DAG

### Wave 1 — One derived-state implementation

**W1-01 Resolve delivery from remote-default evidence**  after: none  acceptance: 1, 2, 4, 7
- Files: loom-code/scripts/loom_checker.py, loom-code/scripts/test_loom_checker_intake.py
- Test: A1 positive: canonical-witness-delivered; boundary: no-intent-no-delivery. A2 positive: remote-only-active; boundary: local-evidence-active. A4 positive: complete-witness; negative: malformed-witness. A7 positive: legacy-closed-readable; boundary: indeterminate-blocks-intake.
- Risk: agent-decided — use one pure resolver shared by reporting and intake; never revalidate historical content digests or fall back to local branches.

**W1-02 Expose active and delivered intent queries**  after: W1-01  acceptance: 3, 5
- Files: loom-code/scripts/loom_checker.py, loom-code/scripts/test_loom_checker_cli.py
- Test: A3 positive: delivered-four-filtered; negative: active-remains-listed. A5 positive: git-metadata-derived; boundary: offline-delivered-without-metadata.
- Risk: agent-decided — extend the checker CLI instead of adding a script; optional metadata failure cannot erase repository-proven delivery.

### Wave 2 — Remove the obsolete current-contract promise

**W2-01 Align contract and package surfaces**  after: W1-01, W1-02  acceptance: 6
- Files: loom-code/contract/manifest.yaml, loom-code/scripts/test_loom_checker_cli.py, loom-code/CHANGELOG.md, loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json
- Test: A6 positive: existing-publish-suite; boundary: current-contract-declares-no-close-transition.
- Risk: agent-decided — retain legacy closed grammar for reads while deleting only the promise that Ship writes new closed states.

## Questions asked

1 — what — 這就是你要的嗎？
2 — behaviour — 這就是你預期的修改後行為嗎？

## Risks

1. A stale remote-default ref can report stale state; indeterminate refs block intake, while successful snapshots remain explicitly caller-refreshed and offline.
2. Delivery evidence proves historical completion, not current-tree equivalence; tests must keep later unrelated merges from reopening delivered work.
3. The public CLI output must stay deterministic so skills can consume it without introducing another ledger or network dependency.
