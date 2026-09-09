# Cross-host plugin contracts — plan
intent: 2026-09-09-cross-host-plugin-contracts@c974a1a7e
spec: docs/loom/2026-09-09-cross-host-plugin-contracts/spec.md@4d1b98d96
charter: 1.0

## Task DAG

### Wave 1 — Native host boundaries

**W1-01 Split host hooks and make Codex recovery stale-safe**  acceptance: 1,2,3,5
- Files: loom-code/hooks/hooks.json, loom-code/hooks/hooks-codex.json, loom-code/.codex-plugin/plugin.json, loom-code/scripts/test_hooks_json.py, loom-code/scripts/test_codex_stale_hook.py
- Test: A1 positive: one-native-manifest; negative: no-double-registration. A2 positive: missing-root-safe-reads; boundary: unsafe-options-denied. A3 positive: checker-present-policy; negative: missing-checker-publication. A5 positive: reviewed-contract; boundary: review-findings-closed.
- Risk: agent-decided — implement the spec's closed recovery allowlist inline; keep every normal-state Bash payload on the existing shared checker path.

**W1-02 Align shared skills and standing host terminology**  after: W1-01  acceptance: 1
- Files: loom-code/skills/write-plan/SKILL.md, loom-code/skills/write-plan/references/codex-first-contact.md, PRINCIPLES.md, loom-code/scripts/test_simplified_station_text.py
- Test: A1 positive: native-host-instructions; negative: no-Codex-Claude-root-or-repo-hook claim.
- Risk: agent-decided — share provider-neutral workflow prose; label only runtime-specific commands and preserve the confirmed installed-plugin trust boundary.

### Wave 2 — Lifecycle and release integration

**W2-01 Prove both install lifecycles and account for the adapter**  after: W1-01,W1-02  acceptance: 1,2,3,4
- Files: scripts/test_loom_plugin_install_layout.py, loom-code/scripts/check_mechanisms.py, loom-code/scripts/test_check_mechanisms.py, docs/loom/evidence/mechanisms.yaml, loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md
- Test: A1 positive: isolated-host-installs; negative: foreign-contract-absent. A2 positive: removed-cache-read; boundary: executing-options-denied. A3 positive: publication-shared-verdict; negative: no-substitute-checker. A4 positive: lifecycle-matrix; boundary: malformed-input.
- Risk: agent-decided — add one host-qualified mechanism with its regression eval and explicit budget exception; use the existing manifest sync command for the release.

## Questions asked

1 — what — 你要的是：修正 Loom 在 Codex／Claude Code 共用 hook 時的宿主差異，避免 plugin 升級或舊 cache 消失後，失效的 hook 路徑連一般唯讀指令都擋住；同時保留 publish 檢查，不能因容錯而讓 push／PR publication 繞過 gate。這樣正確嗎？
1 — what — 這次要不要使用 Claude Code 作為第二位讀者？
1 — what — 修正後的主要目標是同一套 Loom plugin 能同時符合 Codex 與 Claude Code 各自官方的 plugin、skill 與 hook 開發規範，並保留上述升級安全與發布防護。這樣才是你要的嗎？
1 — what — 另外，這次是否使用 Claude Code 作為第二位讀者？

## Risks

1. The stale-root recovery command survives without plugin files, so its allowlist must stay small, deterministic, and hostile-input tested rather than becoming another shell parser.
2. Codex and Claude Code documentation can evolve independently; tests must pin documented host contracts without claiming cache behavior that either vendor does not guarantee.
3. The two manifests are mutually exclusive at runtime but both ship in one package; mechanism accounting must remain explicit without duplicating the publication-policy rule.
