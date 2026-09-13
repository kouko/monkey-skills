# Recap state natural output — plan
intent: 2026-09-12-recap-state-natural-output@3b6e9a73573de5bd8b8bd7f9a77f7ae4f1692a5d
charter: 1.0

## Current State Evidence
- Forward: `loom-workflow/skills/recap-state/SKILL.md` under `2. Output exactly two sibling top-level tags` exposes planning and numbered block labels.
- Reverse: `loom-workflow/scripts/test_recap_state_compaction.py::test_entrypoint_preserves_l3_blocks_verbatim_rules_and_synthesis_gate` requires the exposed tags and discontinuous headings.
- Error: `references/seven-block-schema.md` under `Block 4` says rendered output renumbers six blocks, contradicting the entrypoint.
- Data: `README.md` under `Overview` describes seven blocks and every user message, diverging from the L3 six-section contract.
- Boundary: `docs/loom/KICKOFF-DEFAULTS.md` classifies skill artifacts outside declared interface surfaces, so this remains engineering work.

## Task DAG

### Wave 1

**W1-01 Encode and implement the goal-grounded recap contract**  acceptance: 1,2,3,4,6,7,8
- Files: loom-workflow/scripts/test_recap_state_compaction.py, loom-workflow/skills/recap-state/scripts/test_seven_block_schema.py, loom-workflow/skills/recap-state/SKILL.md, loom-workflow/skills/recap-state/references/seven-block-schema.md
- Test: A1 positive: ordered-natural-sections; negative: reordered-loop. A2 positive: clean-template; negative: control-markers. A3 positive: grounded-goals; negative: invented-horizons. A4 positive: aligned-check; negative: unchecked-continuation. A6 positive: capability-fallback; negative: decorative-diagram. A7 positive: retained-contracts; negative: leaked-markers. A8 positive: synchronized-reference; negative: stale-example.
- Risk: agent-decided — retain the six-section boundary and redefine responsibilities; adding a seventh section would increase scan cost without new information.

### Wave 2

**W2-01 Document the alignment loop in three languages**  after: W1-01  acceptance: 5
- Files: loom-workflow/skills/recap-state/scripts/test_readmes.py, loom-workflow/skills/recap-state/README.md, loom-workflow/skills/recap-state/README.ja.md, loom-workflow/skills/recap-state/README.zh-TW.md
- Test: A5 positive: localized-loop-diagrams; negative: missing-or-divergent-diagram.
- Risk: agent-decided — use one localized Mermaid architecture diagram per README; runtime output remains content-dependent rather than repeating this static diagram.

## Questions asked

1 — what — 你要的是讓 `recap-state` 以「目標錨定對齊閉環」協助使用者重新定位：先對齊有依據的當前目的，再說明位置、背景、差距、確認需求與待辦，最後一起確認目的、位置和下一步；同時不顯示 `<thinking>`、`<recap>`、closing tags 或 `Block N`，README 使用 Mermaid 解釋架構，執行時只有在圖能壓縮實際資訊時才依 client 能力選 Mermaid 或 ASCII。此次只做本地實作與驗證，不發布。這就是你要的範圍嗎？
1 — what — 這次要不要用 Claude 作為第二位讀者？

## Risks

1. The authoritative reference serves L3 recap and historical L2 concepts; edits must narrow L3 rendering without silently redesigning the separate HANDOFF skill.
2. Mermaid support has no reliable shared runtime signal; capability must be explicit, with ASCII as the unknown-client fallback.
3. User-decided — closing Review includes Claude; publication remains explicitly excluded.
