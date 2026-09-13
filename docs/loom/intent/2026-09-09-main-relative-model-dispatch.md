# 以主代理為基準的子代理模型分派
originator: kouko
kind: engineering
needs-design: yes — 分派、升級與 fallback 是多狀態行為，目前沒有正式 spec
evidence: [docs/skill-dogfood/2026-09-09-loom-main-relative-dispatch-plan/policy-fixture.md, docs/skill-dogfood/2026-09-09-model-effort-cost-pilot/report.md, docs/skill-dogfood/2026-09-09-model-effort-cost-pilot/protocol.md]
status: confirmed 2026-09-10

## Problem
Loom 雖然能替子代理指定不同模型與推理強度，但目前沒有一套跨 Codex 與 Claude Code、以主代理當前配置為基準的明確分派規則。結果不是沿用 host 預設，就是依角色直接指定昂貴配置；使用者無法在不介入每次分派的情況下，同時控制成本並保留複雜任務的升級能力。

## Proposed outcome
Loom 依任務的可檢查證據，使用跨 host 的模型與五階段推理強度層級，相對於主代理配置自動維持、降級或升級。模型能力優先調整；high 以上只在較低配置已留下對應的具體失敗證據時使用，max 不由 routing 主動產生。host 不支援指定參數時，自動回到未指定 overrides 的執行方式。

## Acceptance
1. 我可以讓 Loom 根據 mechanical、ordinary、complex 三類可檢查條件，自動算出相對於主代理的子代理配置，而不是依角色名稱固定模型。
2. 我可以在 Codex 與 Claude Code 使用同一套 `economy`、`standard`、`frontier` 與 `low`、`medium`、`high`、`xhigh`、`max` 意義，由各 host 映射到實際支援的配置；Codex `ultra` 等非共通值仍能保留為 host 專屬繼承值。
3. 當指定 model 或 effort 不受支援或遭拒時，Loom 會自動省略兩個 overrides 後重試一次，不要求我選模型、effort 或 fallback。
4. 初始分派不會主動進入 `high`、`xhigh` 或 `max`；routing 只有在完整較低配置已產生規則列出的具體失敗證據後，才會新進入 `high` 或 `xhigh`，`max` 只繼承主代理既有設定。
5. 我可以從可重播測試確認五階段 tier arithmetic、可達性、clamp、host 專屬值、unknown capability、fallback 與 redispatch 上限，並從縮減後的真實 corpus 校準 host mapping，而不是依未驗證的成本假設。

## Constraints
- 核心政策不得寫死 Codex 或 Claude 的產品模型名稱；實際 mapping 屬於各 host。
- routing 以主代理可觀察到的 model 與 effort 為基準；無法可靠觀察時不猜測，省略兩個 overrides。
- 能力不足先升 model；推理深度不足才升 effort。升 model 不會自動降低 effort；`frontier/low` 可作為 `standard/medium` 的選擇性品質升級，但不會為了節省成本自動以它取代 `standard/medium`。
- mechanical 初始只降 model 一級並保留 effort；complex 初始升 model 一級並保留 effort，模型已在上限時才依 clamp 規則考慮 effort。
- 跨 host 的共通 effort 順序為 `low < medium < high < xhigh < max`。初始 routing 只會新產生 `low` 或 `medium`；`high`、`xhigh` 需要逐級失敗證據，`max` 只繼承；host 專屬且高於 `max` 的值只原樣繼承，不由共通規則主動產生。
- 每個 task 最多重新分派兩次；routing 不重設既有 Review round 上限。
- 保留目前 Build、Review 與 attestation 的責任邊界。

## Out of scope
- 建立完整的 model × effort benchmark 或宣稱跨任務、跨供應商的普遍成本排名。
- 新增持久 dispatch ledger、自動學習服務、runtime resolver service 或新的 attestation schema。
- 依 worker、reviewer 等角色固定 profile，或把 `high`、`xhigh`、`max` 設為初始預設。
- 讓使用者在每次 routing 失敗時選擇模型、effort、retry 或 fallback。
- 在這個 change 中 push、merge，或修改各供應商的帳號與方案設定。

## Open questions
- none
