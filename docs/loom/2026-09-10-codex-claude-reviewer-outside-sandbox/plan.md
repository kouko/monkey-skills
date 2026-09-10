# Codex Claude reviewer outside-sandbox execution — plan
intent: 2026-09-10-codex-claude-reviewer-outside-sandbox@9ca1435d3a3bee7c8ba9324ffe0a400e8b10723f
spec: docs/loom/2026-09-10-codex-claude-reviewer-outside-sandbox/spec.md@9894ac657
charter: 1.0

## Task DAG

### Wave 1 — One host execution contract

**W1-01 Require the proven Codex execution boundary**  after: none  acceptance: 1, 2, 3
- Files: loom-code/skills/review/SKILL.md, loom-code/scripts/test_simplified_station_text.py, loom-code/CHANGELOG.md, loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json
- Test: A1 positive: existing-login-visible; boundary: no-repeat-login. A2 positive: outside-sandbox-runner; negative: no-sandbox-fallback. A3 positive: effective-auth-diagnostic; boundary: authorization-blocker-before-login-guidance.
- Risk: agent-decided — extend the existing Codex-specific station contract only; preserve the runner, retry, attestation, and Claude-native paths defined by the spec.

## Questions asked
1 — behaviour — 這就是你要固定的行為，對嗎？
2 — behaviour — 這就是你要固定的行為，對嗎？

## Risks
1. Codex host APIs may name outside-sandbox permission differently; keep the contract behavioural while naming the currently proven execution option as guidance.
2. A first runner invocation may still require host approval; denial stops explicitly rather than falling back to a misleading sandboxed authentication result.
