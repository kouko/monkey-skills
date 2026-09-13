# Compress Loom skill descriptions — plan
intent: 2026-09-13-compress-loom-skill-descriptions@bd6af61c73bc
charter: 1.0

## Current State Evidence

- Forward: `loom-code/skills/write-plan/SKILL.md` `description:` repeats family-entry routing that a plugin router can own once.
- Reverse: `scripts/check-skill-structure.py:is_router_skill` already recognizes thin router skills without imposing the normal description word floor.
- Error: `loom-code/scripts/check_mechanisms.py:R1/R3/R4` rejects unregistered routers, unjustified mechanism growth, or routing mechanisms without executable evaluation.
- Data: the 20 current `loom-*/skills/*/SKILL.md` descriptions render to 6,746 characters and 1,052 whitespace-delimited words.
- Boundary: `scripts/test_loom_plugin_install_layout.py:test_isolated_loom_plugins_are_standalone_and_compose_by_public_contract` verifies each plugin without private sibling dependencies.

## Task DAG

### Wave 0 — freeze cost and routing expectations

**W0-01 Add the failing catalogue budget and routing corpus**  after: none  acceptance: 1, 2
- Files: scripts/test_loom_skill_description_catalog.py, docs/skill-dogfood/2026-09-13-compress-loom-skill-descriptions/cases.md
- Test: A1 positive: rendered-total-at-most-4047; boundary: router-overhead-counted. A2 positive: plugin-umbrella-and-direct-skill; negative: adjacent-skill-and-ordinary-request.
- Risk: A synthetic corpus can reward its own wording; agent-decided — freeze realistic direct, umbrella, collision, multilingual, and explicit-only cases before editing descriptions.

### Wave 1 — add thin routers and remove repeated metadata

**W1-01 Route loom-code and compress its five leaf descriptions**  after: W0-01  acceptance: 1, 2, 3
- Files: loom-code/skills/using-loom-code/SKILL.md, loom-code/skills/*/SKILL.md, loom-code/README*.md
- Test: A1 positive: code-budget-share; boundary: router-counted. A2 positive: plan-build-review-ship-maintain; negative: design-or-workflow-tool. A3 positive: direct-leaf-load; boundary: router-only-routing.
- Risk: A router can duplicate station control; agent-decided — keep it to classification and loading the selected existing station, with no workflow policy of its own.

**W1-02 Route loom-design and compress its four leaf descriptions**  after: W0-01  acceptance: 1, 2, 3
- Files: loom-design/skills/using-loom-design/SKILL.md, loom-design/skills/*/SKILL.md, loom-design/README*.md
- Test: A1 positive: design-budget-share; boundary: router-counted. A2 positive: intent-spec-principles-system; negative: implementation-or-toolbox. A3 positive: direct-leaf-load; boundary: standalone-install.
- Risk: Intent and spec entry triggers overlap; agent-decided — route by artifact state and preserve each leaf's unique positive trigger in its short description.

**W1-03 Route loom-workflow and compress its eleven leaf descriptions**  after: W0-01  acceptance: 1, 2, 3
- Files: loom-workflow/skills/using-loom-workflow/SKILL.md, loom-workflow/skills/*/SKILL.md, loom-workflow/README*.md
- Test: A1 positive: workflow-budget-share; boundary: router-counted. A2 positive: eleven-tool-routing; negative: lifecycle-station-collisions. A3 positive: explicit-only-goal-create; boundary: direct-leaf-load.
- Risk: Eleven heterogeneous tools can bloat the router; agent-decided — use one compact decision table and leave every procedure in its existing leaf skill.

### Wave 2 — prove the net win and admit the routers

**W2-01 Run fresh routing cases and catalogue accounting**  after: W1-01, W1-02, W1-03  acceptance: 1, 2, 3
- Files: docs/skill-dogfood/2026-09-13-compress-loom-skill-descriptions/cases.md, docs/skill-dogfood/2026-09-13-compress-loom-skill-descriptions/report.md, scripts/test_loom_skill_description_catalog.py
- Test: A1 positive: at-least-40-percent-reduction; negative: body-text-excluded. A2 positive: held-out-route-pass; negative: collision-misroute. A3 positive: direct-invocation-preserved; boundary: no-policy-change.
- Risk: One model run cannot prove universal routing; agent-decided — report exact model, prompts, outcomes, and bounded claims, reverting descriptions that fail their cases.

**W2-02 Register only passing routers and synchronize releases**  after: W2-01  acceptance: 3, 4
- Files: docs/loom/evidence/mechanisms.yaml, loom-*/.claude-plugin/plugin.json, loom-*/.codex-plugin/plugin.json, loom-*/CHANGELOG.md, .claude-plugin/marketplace.json
- Test: A3 positive: three-isolated-installs; negative: private-sibling-reference. A4 positive: mechanism-evals-and-version-sync; negative: missing-budget-exception-or-stale-manifest.
- Risk: Three routers increase the governed mechanism count; agent-decided — admit each only with the shared executable routing eval and an explicit per-router budget exception.

## Questions asked

① — what — 你要的是：讓 Loom 每次啟動時讀入的能力說明大幅變短，同時仍能正確找到對應功能，且不改變既有流程、直接呼叫和獨立安裝能力。對嗎？
① — consequence — 回答「對」也代表：Review 與發布檢查通過後，我可以自動非強制推送並建立 Ready PR；合併仍由你另行決定，你也可在發布前取消授權。

## Risks

1. Shorter leaf descriptions can lose implicit matches; each retains one unique WHAT/WHEN trigger while shared cross-routing moves to the plugin router.
2. Router bodies add context only after activation; measure initial metadata separately from routed execution cost so savings are not overstated.
3. Existing tests pin multilingual and negative-boundary phrases in some descriptions; update those assertions only when the router carries equivalent routing evidence.
4. Concurrent unmerged entrypoint refactoring exists on another branch; this change starts from `origin/main` and must not import or overwrite that work implicitly.
