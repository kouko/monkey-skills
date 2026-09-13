# Host-aware cross-model review language — plan
intent: 2026-09-12-host-aware-cross-model-review-language@f080b1a90d8521db4f54c40048a85bcd86e4d916
spec: docs/loom/2026-09-12-host-aware-cross-model-review-language/spec.md@e7fbb00e2
charter: 1.0

## Task DAG
<!-- When a spec requirement changes after this commit, the un-landed
     tasks it touches are replaced and the reason is named in the commit
     message. Landed tasks stay as they are. -->

### Wave 0 — host-aware interaction contract

**W0-01 Define host-native ask and one-cell suggest output**  after: none  acceptance: 1, 2, 3, 5, 6
- Files: loom-code/skills/write-plan/references/second-vendor-ask-and-docs-lint.md, loom-code/skills/write-plan/SKILL.md, loom-code/scripts/test_write_plan_station_text.py, loom-design/skills/capture-intent/references/second-vendor.md, loom-design/skills/capture-intent/SKILL.md, loom-design/scripts/spec/test_capture_intent_contract.py
- Test: A1 positive: codex-offers-claude; negative: codex-never-self. A2 positive: claude-offers-codex; negative: claude-never-self. A3 positive: cross-model-language; negative: no-second-reader. A5 positive: one-cell-table-spacing; boundary: raw-markdown. A6 positive: native-conservative-ask; boundary: unavailable-fallback.
- Risk: Host tool names and availability differ; agent-decided — specify capability-based native use plus an explicit Markdown fallback rather than claiming one universal UI.

### Wave 1 — cross-plugin regression and release

**W1-01 Pin mode boundaries and publish compatible patch versions**  after: W0-01  acceptance: 4
- Files: loom-code/scripts/test_write_plan_station_text.py, loom-design/scripts/spec/test_capture_intent_contract.py, loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-design/.claude-plugin/plugin.json, loom-design/.codex-plugin/plugin.json, loom-design/CHANGELOG.md
- Test: A4 positive: dual-host-three-mode-contract; boundary: no-tool-and-fixed-failure-no-substitution.
- Risk: Independently installed plugins can drift; agent-decided — bump both patch versions and run manifest, boundary, and isolated-layout checks together.

## Questions asked

① — what — 你要的是上述行為，且回答「對」也代表 Review 與發布檢查通過後可自動 push 並建立 Ready PR，但最後 merge 仍會另外詢問。對嗎？
② — behaviour — 以上就是你要的最終行為，對嗎？
② — behaviour — 這就是接下來實作的可見行為，對嗎？
② — behaviour — 這就是你要的統一反應，對嗎？
② — behaviour — 這個補完後的可見行為對嗎？

## Risks

1. Native question widgets are host capabilities, so package tests can prove routing instructions and fallback contracts but not every future client renderer.
2. Markdown renderers may collapse visual whitespace; raw output tests must pin two blank lines before and after the one-cell table source.
3. `loom-design` cannot call `loom-code` runtime code, so matching contract tests must prevent its standalone prose route from drifting.
