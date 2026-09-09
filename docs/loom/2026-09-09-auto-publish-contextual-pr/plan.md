# Automatic contextual pull-request publication — plan
intent: 2026-09-09-auto-publish-contextual-pr@dcdd58b1668b95d877d42ba92f48c3de77d4f943
spec: docs/loom/2026-09-09-auto-publish-contextual-pr/spec.md@4b2055ad2d060abc6b5ab16c9990ec731efa692a
charter: 1.0

## Task DAG

### Wave 1 — Behavioural seams

**W1-01 Bind intent authorization to publication**  acceptance: 1, 6
- Files: loom-code/scripts/loom_checker.py, loom-code/scripts/test_loom_publish.py, loom-code/skills/ship/SKILL.md
- Test: A1 positive: confirmed-current-intent-publishes; boundary: legacy-intent-requires-decision. A6 positive: publish-stops-before-merge; negative: publish-never-invokes-merge.
- Risk: agent-decided — extend the existing publish wrapper and explicit intent evidence; never infer authorization from plugin version, branch age, or a bare confirmed status.

**W1-02 Make the PR body self-contained**  after: W1-01  acceptance: 2, 3, 4
- Files: loom-code/skills/ship/SKILL.md, loom-code/scripts/test_simplified_station_text.py, loom-workflow/skills/git-memory/protocols/compose-pr.md
- Test: A2 positive: full-context-sections-present; negative: missing-context-rejected. A3 positive: graph-shaped-change-selects-mermaid; boundary: simple-change-omits-diagram. A4 positive: decision-summary-is-auditable; negative: hidden-reasoning-claim-rejected.
- Risk: agent-decided — Ship owns one top-level body schema; git-memory supplies durable memory content without creating a second template or restoring legacy review fields.

**W1-03 Observe required CI every thirty seconds**  after: W1-02  acceptance: 8
- Files: loom-code/scripts/loom_checker.py, loom-code/scripts/test_loom_publish.py, loom-code/skills/ship/SKILL.md
- Test: A8 positive: pending-then-pass-polls-thirty-seconds; boundary: fail-cancel-action-or-task-stop-terminates-without-pending-spam.
- Risk: agent-decided — keep polling inside the existing publish process with injectable time and GitHub calls; create no scheduler, daemon, resume state, or optional-check wait.

### Wave 2 — Publication integration and release contract

**W2-01 Close publication failures and regression coverage**  after: W1-01, W1-02, W1-03  acceptance: 5, 7
- Files: loom-code/scripts/test_loom_publish.py, loom-code/scripts/test_simplified_station_text.py, loom-code/scripts/check_mechanisms.py, docs/loom/evidence/mechanisms.yaml, loom-code/CHANGELOG.md, loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json
- Test: A5 positive: create-update-ready-and-ci-success; negative: each-publication-boundary-stops. A7 positive: current-artifacts-and-regressions-pass; boundary: legacy-ledger-absent-and-mechanism-count-does-not-rise-without-exception.
- Risk: agent-decided — prefer extending existing tests and registered mechanisms; add no mechanism unless the concrete behaviour cannot be proved within the current publish and skill gates.

## Questions asked

1 — what — 這份 intent 是否正確？
1 — what — 監控只在同一個 Codex task 持續，還是重啟 Desktop 後也要恢復？
2 — behaviour — 這就是你預期的修改後行為嗎？
2 — behaviour — 這些補充也符合你的預期嗎？

## Risks

1. Automatic publication expands outward action; positive current-intent evidence, explicit opt-out, destination binding, non-forced push, privacy checks, and separate merge authorization remain mandatory.
2. Existing PR reuse can silently preserve stale context; update and draft-to-ready operations must bind to the same repository, head, base, and live HEAD as creation.
3. Thirty-second polling can hang on optional or unknown checks; observe required checks only, define every terminal state, and stop with the active task.
4. Rich PR bodies can become ceremonial; require complete semantic sections but include Mermaid only when graph structure materially improves understanding.
