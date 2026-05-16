# systematic-debugging

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> **HARD-GATE — 沒重現前不准修。** 4-phase 紀律：REPRODUCE → ISOLATE → HYPOTHESIZE → VERIFY。tdd-iron-law「沒失敗測試不准實作」的除錯版。一級書目：Kernighan & Pike (1999) *The Practice of Programming* 第 5 章 (ISBN 978-0201615869) + Hunt & Thomas (2019) *Pragmatic Programmer* Topic 28 (ISBN 978-0135957059)。對亂試 patch、無假設加 log、try/except 蓋掉、「我這邊可以」這類合理化 **拒絕**。

[code-toolkit](../..) plugin 的一部分。Agent 載入的是 [`SKILL.md`](SKILL.md)；本 README 是給人類看的。

## 4 個 phase

| Phase | 目標 | 通往下一個的 gate |
|---|---|---|
| 1 — **REPRODUCE** | 可重現的 trigger（等同 RED 測試） | 🟢 reproducible OR 🟡 條件已限定 |
| 2 — **ISOLATE** | 把 bug 範圍縮到最小單位（1 行 / function / 依賴 / 輸入欄位） | 縮到單一 component |
| 3 — **HYPOTHESIZE** | 預測一個你還沒觀察的事象的 **falsifiable** 假設 | 假設可被反證（明確說出觀察到什麼就會被否決） |
| 4 — **VERIFY** | 跑實驗；確認 or 反證；確認就 fix + regression test + 按 blast radius 比例加 defense-in-depth | 假設確認；fix 落地；regression test 就位 |

任何 phase 沒過 gate 就 **不准** 進下一個 — 帶新資訊回上一個 phase。

## 使用時機

自動 routing：
- `tdd-iron-law` §False-green diagnostic 回「test 第一次跑就 pass 且 comment out production code 也不 fail」（測試沒在測你以為的東西）。
- SDD `implementer` subagent 回 `BLOCKED` + `unblock_step: "test will not go RED"`（無法為真實 bug 寫出失敗測試）。
- 使用者說「不會動」但原因 non-obvious — *"intermittent"*、*"我這邊可以但 CI 不行"*、*"照理應該動但不動"*。

## 不使用時機

[`SKILL.md`](SKILL.md) §When NOT to Use 限定列舉：

- 失敗測試已存在 AND 錯的 line 顯而易見（直接在 tdd-iron-law 下修）
- typo / config 值的 trivial bug（沒有 behavior chain 要追）
- code 照 spec 跑但 spec 寫錯了（用 brainstorming 改 spec）
- 前 session 已 root-cause 過

## 這個 skill 包什麼

- [`SKILL.md`](SKILL.md) — 4-phase 運作規格，Red Flags（8 種 rationalization × ja + zh-TW 在地化），cross-skill 契約。
- [`references/root-cause-tracing.md`](references/root-cause-tracing.md) — Phase 2 ISOLATE 的 sub-protocol。Bisection 軸表（git / dependency / input / component / time / 5-Whys）；halving cost heuristics；anti-patterns。
- [`references/condition-based-waiting.md`](references/condition-based-waiting.md) — Phase 1 🟡 + Phase 2 time-axis bisection。把 `sleep(500)` anti-pattern 換成 condition-polling。各語言 library helpers。
- [`references/defense-in-depth.md`](references/defense-in-depth.md) — Phase 4 VERIFY 後的 layering。6 層 ladder（regression test → input validation → invariant assert → type system → monitoring → architectural refactor）+ 比例規則（成本 ≤ 下次同類 bug 的預期損害）。
- [`references/character-encoding-debug.md`](references/character-encoding-debug.md) — 編碼專屬 bisection（BOM / UTF mismatch / NFC-NFD / surrogate pairs / stream decoder buffer 邊界）。連到 `domain-teams:code-team/standards/character-encoding-security.md`（徳丸本 第 2 版 Ch.6）安全視角版。

## Cross-skill 契約

- **上游**：被 `tdd-iron-law`（false-green diagnostic）或 `subagent-driven-development`（implementer BLOCKED on test-cannot-go-RED）呼叫。
- **下游**：Phase 4 VERIFY 的 fix 觸發 `tdd-iron-law` 寫 regression test（再現本身就是 RED）。
- **橫向（可選）**：ISOLATE 發現 module 太糾結時 `dev-workflow:complexity-critique` 走 refactor-before-fix；要理解「這段 code 為什麼這樣寫」之前先用 `repo-wiki:query` / `dbt-wiki:query`。

## 這個 skill 不做的事

- 不寫新功能（用 brainstorming → writing-plans → SDD → tdd-iron-law）。
- 不取代 `tdd-iron-law` 的 false-green diagnostic — 那是 entry condition，不是 substitute。
- 不會搶先加 defense-in-depth。防護層是 Phase 4 *結果*，不是 Phase 0 *姿勢*。
- 不決定 blast radius / 優先度 — 使用者 / orchestrator 的判斷。

## 參考

- [`SKILL.md`](SKILL.md) — 運作規格。
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — 呼叫本 skill 且消費其輸出的紀律。
- [`../subagent-driven-development/SKILL.md`](../subagent-driven-development/SKILL.md) — implementer-BLOCKED 時呼叫本 skill 的 orchestrator。
- [`../using-code-toolkit/SKILL.md`](../using-code-toolkit/SKILL.md) — Router；本 skill 是 Stage 5（Repair，卡住時）。
