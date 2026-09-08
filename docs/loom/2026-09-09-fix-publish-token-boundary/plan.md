# Fix publication shell token boundaries — plan
intent: 2026-09-09-fix-publish-token-boundary@138d1909a
charter: 1.0

## Current State Evidence
- Forward: `loom-code/scripts/loom_checker.py` uses `SEGMENT_SPLIT` before all publication classifiers.
- Reverse: `cmd_push` calls `is_push_command` before selecting publication validation.
- Error: `is_pr_create_command` turns a quoted regex fragment into a blocked noncanonical publication.
- Data: PreToolUse supplies one opaque shell command string whose quoted arguments may contain operators.
- Boundary: `.codex/INSTALL.md` and Loom READMEs own installation guidance; intent status files own delivery state.

## Task DAG

### Wave 1 — independent corrections

**W1-01 Respect quoted shell token boundaries**  after: none  acceptance: 1, 2
- Files: loom-code/scripts/loom_checker.py, loom-code/scripts/test_publish_command_detection.py
- Test: A1 positive: quoted-search-text; boundary: quoted-operators. A2 positive: real-publishers; negative: dynamic-or-ambiguous.
- Risk: agent-decided — preserve conservative malformed-command handling; replace only quote-blind segmentation.

**W1-02 Document safe Codex plugin updates**  after: none  acceptance: 3
- Files: loom-code/README.md, loom-code/README.ja.md, loom-code/README.zh-TW.md
- Test: A3 positive: upgrade-add-list; negative: remove-before-update.
- Risk: agent-decided — document observed safe sequence without claiming host cache lifecycle guarantees.

**W1-03 Close delivered intents from merge evidence**  after: none  acceptance: 4
- Files: docs/loom/intent/2026-09-06-reuse-branch-end-suite-result.md, docs/loom/intent/2026-09-08-bound-review-convergence.md, docs/loom/intent/2026-09-08-fix-plugin-hook-worktree-resolution.md, docs/loom/intent/2026-09-08-remove-legacy-loom-contract.md, docs/loom/intent/2026-09-08-simplify-loom-evidence-gates.md, docs/loom/intent/2026-09-08-simplify-loom-publication.md
- Test: A4 positive: six-pr-status-map; negative: unrelated-confirmed-intent-unchanged.
- Risk: agent-decided — close only intents with merge commits visible on current main.

## Questions asked
1 — what — 依照你的建議做吧

## Risks
1. Shell parsing is security-sensitive; existing adversarial publisher cases must remain green.
2. Documentation translations must preserve the same operational sequence without byte-level mirroring.
