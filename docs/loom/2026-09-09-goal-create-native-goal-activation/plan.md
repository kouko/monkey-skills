# goal-create native Goal activation — plan
intent: 2026-09-09-goal-create-native-goal-activation@a1b7e31be6739ca92cc7307b577cdc5457e30321
spec: docs/loom/2026-09-09-goal-create-native-goal-activation/spec.md@d19ff3af3dcfec61d517f324d0aa2d50a8411cd3
charter: 1.0

## Task DAG

### Wave 0 — Host activation contract

**W0-01 Implement the tested SESSION activation decision tree**  acceptance: 1,2,3,4,5
- Files: loom-workflow/skills/goal-create/SKILL.md, loom-workflow/skills/goal-create/references/goal-shape.md, loom-workflow/skills/goal-create/scripts/test_skill_md.py, loom-workflow/skills/goal-create/scripts/test_goal_shape.py
- Test: A1 positive: codex-creates; boundary: active-goal-clear. A2 positive: claude-proposes; boundary: inferred-confirmation. A3 positive: manual-fallback; boundary: replacement-disclosed. A4 positive: success-evidence; negative: false-activation. A5 positive: preserved-contract; boundary: length-budgets.
- Risk: agent-decided — encode one capability branch in prose, not adapters or status types; preserve every behavior-changing constraint, and prefer honest fallback over a lossy 500-character proposal.

### Wave 1 — Discovery surfaces

**W1-01 Align the three-language skill and plugin descriptions**  after: W0-01  acceptance: 1,2,3,5
- Files: loom-workflow/skills/goal-create/README.md, loom-workflow/skills/goal-create/README.ja.md, loom-workflow/skills/goal-create/README.zh-TW.md, loom-workflow/README.md, loom-workflow/README.ja.md, loom-workflow/README.zh-TW.md, loom-workflow/skills/goal-create/scripts/test_readmes.py
- Test: A1 positive: codex-activation-described; boundary: existing-goal-limit. A2 positive: claude-capability-described; boundary: confirmation-only-for-content. A3 positive: fallback-described; negative: unsupported-auto-claim. A5 positive: ARC-preserved; boundary: shared-shape.
- Risk: agent-decided — keep each locale's existing terminology and link to SKILL.md for the contract instead of duplicating the full host decision tree.

### Wave 2 — Release consistency

**W2-01 Publish the behavior as a loom-workflow patch**  after: W1-01  acceptance: 1,2,3,4,5
- Files: loom-workflow/.claude-plugin/plugin.json, loom-workflow/.codex-plugin/plugin.json, loom-workflow/CHANGELOG.md, README.md, scripts/sync_codex_manifests.py
- Test: A1 positive: patch-version-visible; boundary: root-version-aligned. A2 positive: claude-manifest-synced; negative: manifest-drift. A3 positive: fallback-changelog; boundary: conditional-capability. A4 positive: honest-state-noted; negative: success-overclaim. A5 positive: package-suite-passes; boundary: ARC-regression.
- Risk: agent-decided — use a patch bump because behavior improves without changing invocation syntax; generate the Codex manifest from the Claude SSOT and avoid editing the sync script.

### Wave 3 — Publication-gate correction

**W3-01 Place the mechanism budget exception in its checker-owned release section**  after: W2-01  acceptance: 4,5
- Files: loom-code/CHANGELOG.md, loom-workflow/CHANGELOG.md
- Test: Existing permanent gate: `python3 loom-code/scripts/check_mechanisms.py --baseline origin/main`; negative reproduced in PR CI when the exception existed only in the feature plugin changelog, positive requires the exception in the current loom-code release section.
- Risk: agent-decided — move the existing exception instead of adding another checker or duplicating it across plugin changelogs; the central mechanism checker remains the single owner.

## Questions asked
2 — behaviour — 你確認上述行為與選項 A 嗎？
2 — behaviour — 如果以上正確，請回覆「確認」，我就會把這一版標記為已確認並送回同一位規格審查者。

## Risks
1. Claude Code exposes `ProposeGoal` conditionally, so implementation must test capability presence at runtime and keep the complete manual `/goal` path equally usable.
2. Codex `create_goal` cannot overwrite an unfinished Goal; the skill must preserve it, report the failed replacement honestly, and direct `/goal clear` plus a rerun.
3. The full Goal and Claude proposal are two representations; tests must prevent compression from dropping a behavior-changing constraint or turning an exact reference into a vague pointer.
4. Existing uncommitted skill and test drafts predate the final spec; Build must treat them as provisional, retain only conforming parts, and preserve unrelated working-tree content.
