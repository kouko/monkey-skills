# Pluggable second-vendor suggestion — plan
intent: 2026-09-12-pluggable-second-vendor-suggest@a725da6bb6da7fe842b0f901aa5a9b93d4241712
spec: docs/loom/2026-09-12-pluggable-second-vendor-suggest/spec.md@3770ea54cad735e8018a3068d3ab2d712a2cdeb4
charter: 1.0

## Task DAG

### Wave 0 — policy boundary

**W0-01 Implement the pure suggestion policy contract**  after: none  acceptance: 1,2,3,4,6
- Files: loom-code/scripts/second_vendor_policy.py, loom-code/scripts/test_second_vendor_policy.py
- Test: A1 positive: full-pending; boundary: no-opt-in. A2 positive: full-risk; boundary: full-ordinary. A3 positive: small-available; boundary: unavailable. A4 positive: pre-review-accept; boundary: late-or-small-accept. A6 positive: grounded-output; negative: malformed-input.
- Risk: Contract drift could leak classification into callers; agent-decided — make exhaustive table tests own every input/output enum and invalid combination.

### Wave 1 — contract consumers

**W1-01 Remove none and adopt suggest in kickoff contracts**  after: W0-01  acceptance: 5,7
- Files: loom-code/contract/manifest.yaml, loom-code/contract/templates/KICKOFF-DEFAULTS.md, docs/loom/KICKOFF-DEFAULTS.md, loom-code/scripts/loom_checker.py, loom-code/scripts/test_contract_manifest.py, loom-code/scripts/test_loom_checker_standing.py, docs/loom/evidence/mechanisms.yaml
- Test: A5 positive: suggest-grammar; negative: none-rejected-with-migration. A7 positive: repository-default-suggest; boundary: template-default-suggest.
- Risk: Immediate removal breaks old configs by design; user-decided — reject with actionable migration text and never alias or silently rewrite none.

**W1-02 Integrate non-blocking decisions into loom-code**  after: W0-01,W1-01  acceptance: 1,2,3,4,5,6
- Files: loom-code/skills/write-plan/SKILL.md, loom-code/skills/write-plan/references/second-vendor-ask-and-docs-lint.md, loom-code/hooks/session-start, loom-code/scripts/test_write_plan_station_text.py, loom-code/scripts/test_session_start_words.py
- Test: A1 positive: suggest-does-not-ask; boundary: ask-still-blocks. A2 positive: risk-recommendation; boundary: ordinary-availability. A3 positive: small-information; boundary: no-tool. A4 positive: timely-opt-in; boundary: late-response. A5 positive: fixed-and-ask; negative: none. A6 positive: policy-result-presented; negative: prose-reclassification.
- Risk: Prose may duplicate policy decisions; agent-decided — prose defines timing and presentation only, with outputs copied verbatim from the resolver.

**W1-03 Keep loom-design intent capture compatible**  after: W1-01  acceptance: 1,5
- Files: loom-design/skills/capture-intent/SKILL.md, loom-design/skills/capture-intent/references/second-vendor.md, loom-design/scripts/spec/test_capture_intent_contract.py
- Test: A1 positive: suggest-skips-decision-point-question; boundary: ask-keeps-question. A5 positive: modes-match-contract; negative: none-not-documented.
- Risk: Independent plugin cannot call loom-code internals; agent-decided — capture-intent only routes modes, while post-plan suggestion policy stays in loom-code.

### Wave 2 — package integration and adversarial evidence

**W2-01 Synchronize package surfaces and prove standalone behavior**  after: W1-02,W1-03  acceptance: 5,6,7
- Files: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-design/.claude-plugin/plugin.json, loom-design/.codex-plugin/plugin.json, loom-design/CHANGELOG.md, .claude-plugin/marketplace.json
- Test: A5 positive: manifest-sync; negative: stale-version. A6 positive: isolated-install-policy; boundary: no-sibling-runtime. A7 positive: marketplace-versions; boundary: repository-default-check.
- Risk: Dual-plugin versions can drift; agent-decided — update Claude manifests first, sync Codex manifests, then run boundary and isolated-install gates.

**W2-02 Add closing adversarial coverage**  after: W2-01  acceptance: 1,2,3,4,5,6,7
- Files: docs/loom/2026-09-12-pluggable-second-vendor-suggest/evidence/probes/test_second_vendor_suggest_adversarial.py
- Test: A1 positive: nonblocking-default; boundary: absent-reply. A2 positive: all-risk-signals; boundary: zero-risk. A3 positive: small-matrix; boundary: unavailable. A4 positive: timing-matrix; boundary: contradictory-response. A5 positive: supported-modes; negative: removed-none. A6 positive: caller-order-independent; negative: forged-anchor. A7 positive: repo-default; boundary: installed-layout.
- Risk: A probe that only mirrors unit tests adds no evidence; agent-decided — run the packaged resolver from a hostile temporary repository and assert public CLI behavior.

## Questions asked
① — what — 你要我同時把 `monkey-skills` 目前的 `second-vendor: ask` 改成新的 `suggest`，還是只新增可抽換的 `suggest` 能力、暫時保留此 repo 的 `ask` 設定？
① — what — 你要的是：新增可獨立測試與替換的 `suggest` 判斷核心，預設不使用第二供應商；只有完整變更命中明確高風險且工具可用時，才發出一次不阻塞流程的建議。同時把 `monkey-skills` 從每次詢問的 `ask` 改成 `suggest`，並保持其他模式相容。對嗎？
① — consequence — 這次是否使用 Claude Code 作為第二位 reviewer？
② — behaviour — 這就是你預期會看到的行為嗎？
② — behaviour — 你希望 small lane 也顯示並允許啟用第二供應商嗎？
② — behaviour — 這份最終行為可以確認嗎？
② — consequence — 你要採用這個向後相容方案，還是現在就完全移除 `none`？
② — behaviour — 這就是你要的最終行為嗎？
② — behaviour — 請再回覆一次「對」，我就能更新規格綁定並直接完成正式 plan。

## Risks
1. `suggest` spans two standalone plugins; only loom-code may execute the resolver, while loom-design must remain a prose-only mode router with no sibling runtime dependency.
2. Removing `none` is intentionally breaking; its new checker rule needs mechanism registration, a regression eval, and the same-version CHANGELOG budget exception.
3. Non-blocking replies live only in active task context; no persistent listener, preference ledger, background wait, or reviewer-identity mutation after Review may appear.
4. Recommendation evidence must remain anchored and machine-readable; free-form risk interpretation outside the policy module would defeat replaceability.
5. user-decided — second-vendor selection-confirmed: claude
