# Risk-triggered pre-build review and branch-end-only Build review — plan
intent: 2026-09-06-remove-build-time-reviews@c780ff3c
spec: docs/loom/2026-09-06-remove-build-time-reviews/spec.md@a6056ff5
charter: 1.0

## Task DAG

**W0-01 Adversarial probes for readiness and risk gating**  after: —  acceptance: 1,2,6
- Files: `docs/loom/2026-09-06-remove-build-time-reviews/evidence/probes/test_abuse_review_reduction.py`
- Test: A1 positive: paired-plan; negative: uncovered-acceptance. A2 positive: low-risk-skip; boundary: legacy-required. A6 positive: declaration-independent-lane; boundary: forcing-path-full.
- Risk: agent-decided — attack omissions and bypasses before checker implementation; this high-risk gate task is adversary-first.

**W0-02 Checker and plan-contract enforcement**  after: W0-01  acceptance: 1,2,6
- Files: `loom-code/scripts/loom_checker.py`, `loom-code/scripts/test_loom_checker_intake.py`, `loom-code/scripts/test_loom_checker_cli.py`, `loom-code/scripts/test_loom_checker_hardening.py`, `loom-code/contract/manifest.yaml`, `loom-code/contract/templates/*.md`, `docs/loom/evidence/mechanisms.yaml`
- Test: A1 positive: paired-plan; negative: empty-or-missing-case. A2 positive: one-required-reader; boundary: legacy-two-reader. A6 positive: lane-independent; boundary: gate-path-full.
- Risk: agent-decided — preserve legacy records while changing new-plan intake; keep existing rule IDs except the one-for-one budget replacement.

**W1-01 Spec and plan authoring contracts**  after: W0-02  acceptance: 1,2
- Files: `loom-code/skills/write-plan/**`, `loom-design/skills/write-spec/**`, `loom-code/scripts/test_station_text*.py`, `loom-design/tests/**`
- Test: A1 positive: compact-case-contract; negative: unresolved-question-block. A2 positive: declared-low-risk-skip; boundary: required-single-reader-no-blind.
- Risk: agent-decided — keep scenario detail in specs and case IDs in capped plan lines; do not add a new user decision point.

**W1-02 Build keeps tests and removes automatic checkpoints**  after: W1-01  acceptance: 3,4
- Files: `loom-code/skills/build/SKILL.md`, `loom-code/scripts/test_build*.py`, `loom-code/scripts/test_station_text*.py`
- Test: A3 positive: task-tests-advance; negative: no-after-task-or-wave-dispatch. A4 positive: adversary-red-first; boundary: small-lane-implementer-first.
- Risk: agent-decided — waves remain dependency boundaries; legacy review markers stay readable but have no new-runtime dispatch effect.

**W1-03 Review and Ship keep one complete branch-end checkpoint**  after: W1-02  acceptance: 2,5,6
- Files: `loom-code/skills/review/**`, `loom-code/skills/ship/**`, `loom-code/agents/reviewer.md`, `loom-code/scripts/test_review*.py`, `loom-code/scripts/test_ship*.py`
- Test: A2 positive: focused-spec-reader; negative: no-spec-blind. A5 positive: branch-end-full; negative: failed-verdict-blocks. A6 positive: second-vendor; boundary: lane-preserved.
- Risk: agent-decided — special-case only spec scope; branch-end reviewer, adversary, blind, fix-round, and second-vendor contracts remain unchanged.

**W2-01 Synchronize public contracts, versions, and mirrors**  after: W1-03  acceptance: 6
- Files: `loom-code/.claude-plugin/plugin.json`, `loom-code/.codex-plugin/plugin.json`, `loom-code/CHANGELOG.md`, `loom-design/.claude-plugin/plugin.json`, `loom-design/.codex-plugin/plugin.json`, `loom-design/CHANGELOG.md`, `README.md`, `.codex/hooks/**`
- Test: A6 positive: manifests-and-mirror-sync; negative: old-checkpoint-prose-absent.
- Risk: agent-decided — bump only changed plugins and regenerate mirrors after source settles; preserve unrelated plugin versions.

**W2-02 Replay the historical multi-task change**  after: W2-01  acceptance: 7
- Files: `docs/loom/2026-09-06-remove-build-time-reviews/evidence/replay-fixture.yaml`, `docs/loom/2026-09-06-remove-build-time-reviews/evidence/replay-results/**`
- Test: A7 positive: zero-build-review-wait; negative: missing-input-ungradable.
- Risk: agent-decided — fixed patches prevent regenerated-code drift; report unavailable runtime or model as UNGRADABLE, never as a speed win.

**W2-memory Memory step — graduated probes and store entries**  after: W2-02  acceptance: none
- Files: `loom-code/scripts/test_probes_review_reduction.py`, `docs/loom/memory/**`
- Test: positive: graduated-probes-pass; negative: memory-integrity-detects-drift.
- Risk: agent-decided — graduate only unique executable probes and file only durable lessons earned by implementation.

## Questions asked
1 — what — 實作前保留正向與負向測試設計，實作途中只跑測試、不做自動正式審查；全部實作完成後做一次 branch-end review，其餘流程維持原樣。確認這就是你要我實作的範圍嗎？
1 — consequence — 這次要使用 Claude 作為第二家模型的審閱者嗎？這會多花幾分鐘與一些額度，但能增加不同模型發現問題的機會。
2 — behaviour — 這些修正符合你的意思嗎？確認後我就提交修正版並交給 Codex 與 Claude 審閱。
2 — behaviour — 請再次確認這份修正版符合你的意思；確認後我會提交並讓 Codex、Claude 複核各自提出的問題。

## Risks
1. The current checker still demands two spec readers; W0-02 is the bootstrap that makes this already-passed single-reader checkpoint valid under the approved flow.
2. Explicit pre-build risk can be understated; branch-end lane recomputation remains independent, and the final adversarial review checks the declaration against the diff.
3. Removing intermediate verdicts increases late-fix radius; task tests and dependency-boundary integration checks remain mandatory before downstream work starts.
4. The replay pins runtime and model availability; unavailable external inputs produce UNGRADABLE evidence and cannot support a speed claim.
