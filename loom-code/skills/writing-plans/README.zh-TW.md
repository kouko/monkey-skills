# writing-plans

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> [`brainstorming`](../brainstorming)（生 brief）和 [`subagent-driven-development`](../subagent-driven-development)（派 subagent）之間的橋。把 brief 拆成 ≤5 個原子任務，附明確的 RED-GREEN 驗收條件，透過 plan-document-reviewer 自審，遇阻時用 Kent Beck (2002) §Child Test pattern (ISBN 978-0321146533) 做 fallback。

[loom-code](../..) plugin 的一部分。Agent 載入的是 [`SKILL.md`](SKILL.md)；本 README 是給人類看的。

## 本 skill 在 pipeline 中的位置

```
brainstorming → brief                             (Discovery 階段)
                  ↓
              writing-plans → plan + self-review    (本 skill — Planning 階段)
                  ↓ (PASS)
              subagent-driven-development → per-task triad
                                                     (Execution 階段)
                  ↓
              tdd-iron-law (各 implementer 內部)
```

## 硬性規則

**每任務一個失敗測試。** 寫不出一個「任務做完就變綠」的失敗測試，就不算一個任務——拆掉（需要 3 個測試就是 3 個任務）。這條準則不含任何時間估計：LLM agent 對 wall-clock 時長沒有體感基礎，也沒有嚴謹文獻把「plan-writer 猜 agent 要花多久」跟 agent 可靠度綁在一起——完整依據見 [`SKILL.md`](SKILL.md) §No time-box criterion。

這條規則擋下太貪心的 brief，也擋下用模糊任務藏複雜度的 plan——但擋的依據是測試，不是時鐘。

*（另一個獨立的軸：計畫大小由 critical-path **depth** ≤5 管控——依賴鏈的最長長度，不是任務總數；很多獨立任務並排的 wide-but-shallow 計畫沒問題。細節見 [`SKILL.md`](SKILL.md) §Plan size ceiling。）*

## 每個任務帶什麼

依 [`references/plan-format.md`](references/plan-format.md)，每個任務都帶：

- **Description**: 一個 assertion 份量的命令式動作
- **Module**: 1 個路徑 / module 名（不是 2 個）
- **Context paths**: implementer 讀的既有 code 路徑（paths-not-content）
- **Acceptance**: RED 測試名 + GREEN 可觀察條件
- **Dependencies**: `none` | `Task N completes first` | `Tasks N, M parallel`
- **Brief item covered**: 引 brief 的 Smallest End State / Decision 對應段落

這個 shape 就是 `subagent-driven-development` 派 3 個 subagent 時消費的形狀。

## 宣告 DONE 前的自審

Plan 寫好後，writing-plans 派 [`references/plan-document-reviewer-prompt.md`](references/plan-document-reviewer-prompt.md) 當 evaluator subagent。Reviewer 跑 16 項檢查（其中 2 項 non-blocking——1 項已退役、1 項僅供參考，實際會擋審的是 14 項），涵蓋每任務的失敗測試驗收條件、brief-任務 coverage map、DAG 無 cycle 等，回 PASS / NEEDS_REVISION。NEEDS_REVISION 就修 plan + 重審。最多 2 輪；還沒過就 escalate 給 user（多半是 brief 本身需要重想）。

plan-document-reviewer 與 SDD 的 spec-reviewer / code-quality-reviewer **不同** — 後者評 code，這個評 plan 結構。

## BLOCKED fallback — Beck 2002 §Child Test

當 SDD 派 implementer subagent 回傳 `BLOCKED` + `unblock_step: "這個任務需要拆更細"`，orchestrator **再次呼叫 writing-plans** 對失敗任務做拆解。本 skill 把失敗任務拆成 ladder up 的子任務 — Kent Beck 的 Child Test pattern（*Test-Driven Development: By Example* Part II）：

> "當你在做一個 test 而它太大時，寫一個更小的 test 表達大 test 壞掉的部分。讓小 test 過。然後回去處理大 test。"

writing-plans 把同樣的 pattern 套到 plan 任務。這是本 skill 的 **主要遞迴價值** — 不只是初期 planning，也是 SDD 在實作過程中遇到原子性失敗時的適應性 re-planning。

## 不使用時機

[`SKILL.md`](SKILL.md) §When NOT to Use 限定列舉：

- 上游 brief 未產出（先去 brainstorming）
- Brief 的 Smallest End State 本身就是 1 個檔案、1 個 assertion，且 Out of Scope 完整（brief 就是 plan）
- 使用者明確 override AND 已給出符合 plan-format schema 的任務清單

## 這個 skill 不做的事

- 不寫 code。Plan 是未來工作的 metadata。
- 不派 SDD subagent（implementer / spec-reviewer / code-quality-reviewer）— 那是 SDD 的工作。
- 完全不估 dev-time — split-trigger 是「寫不寫得出一個失敗測試」，不是時鐘。
- 不決定依賴圖以外的優先順序 / sequencing。

## 參考

- [`SKILL.md`](SKILL.md) — 運作規格（拆分框架、BLOCKED fallback 流、Red Flags）。
- [`references/plan-format.md`](references/plan-format.md) — 附 worked example 的 plan schema。
- [`references/plan-document-reviewer-prompt.md`](references/plan-document-reviewer-prompt.md) — 自審 evaluator prompt。
- [`../brainstorming/SKILL.md`](../brainstorming/SKILL.md) — 上游 brief producer。
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — 下游 plan consumer。
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — 每個 implementer subagent 內觸發的規律。
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — Router；本 skill 是 Stage 2（Planning）。
