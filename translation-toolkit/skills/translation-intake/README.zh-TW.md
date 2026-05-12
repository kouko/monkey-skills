# translation-intake

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> translation-toolkit 的 Layer 1 — 釐清 5 個軸（mode / register / strategy / locale / domain）外加 skopos。
> 在任何翻譯 specialist 開工前先跑。

[translation-toolkit](../..) plugin 的一部分。Claude 載入的 operational
spec 是 [`SKILL.md`](SKILL.md)；此 README 提供給人類。

## 為何需要獨立的 intake skill

4 個 format-specialist skill（`translation-i18n`、`translation-doc`、
`translation-creative`、`translation-audit`）都需要相同 5 個 parameter 才能
開工：**哪一種翻譯**、**多正式**、**文化適應到多深**、**哪兩個 locale
之間**、**哪個 domain**。把 default 寫死等於默默替使用者做了她可能根本沒做
的選擇 — `register=neutral` 用在 runbook 沒問題，用在 marketing tagline
就錯了；`mode=literal` 會生出無法上線的 ad copy。

intake 把這些軸在一處一次性捕捉，下游 skill 讀取結果。auto 模式從 source
內容推論；explicit 模式在 auto 失準、或使用者有 source 不揭露的明確主張時，
帶使用者逐軸確認。

## 5 個軸

| 軸 | 允許值 | 影響 |
|---|---|---|
| `mode` | `literal` / `faithful` / `localized` / `transcreation` | Reflection 軸數（4D vs 5D）與 S1 gate threshold |
| `register` | `formal` / `neutral` / `warm` / `playful` | S2 register-preservation gate |
| `strategy` | `domestication` / `foreignization` | 文化參照的處理；與 mode 獨立 |
| `locale` | BCP-47 source + target（例：`en-US` → `ja-JP`） | 呼叫時必填；不自動推論 |
| `domain` | 13 domain taxonomy 中一個或多個（`general`、`ui`、`tech.software`、`tech.web`、`tech.data`、`tech.crypto`、`gov`、`legal`、`medical`、`finance`、`marketing`、`statistics`、`typography`） | glossary subset 選擇 + critique framing |

外加 **skopos / intent** — 自由形式的一句話，回答「誰會讀這段、應該採取
什麼 action？」。

## 兩個 mode

| Mode | 觸發 | 動作 |
|---|---|---|
| `auto`（預設） | 不加 flag | 單一 source-analysis 呼叫推論全部 5 軸；locale pair 仍由使用者提供 |
| `explicit`（`--explicit` / `-e`） | 使用者 flag | 帶使用者逐軸確認；auto 推論值作為 prompt default |

各 mode 的 pipeline 與 worked example 見
[`protocols/intake-auto.md`](protocols/intake-auto.md) 與
[`protocols/intake-explicit.md`](protocols/intake-explicit.md)。

## 何時使用

- 由 [`using-translation-toolkit`](../using-translation-toolkit) 在輸入缺少
  明確軸訊號（短 raw text、無 format / domain hint）時呼叫
- 在 4 個 active skill 任一個透過 `--intake` 直接呼叫，當你想在 format-specialist
  跑之前檢查 / 鎖定 spec 時
- auto pass 結果不滿意時，加上 `--explicit` 再呼叫一次，互動式覆寫一個或
  多個軸

## 何時 **不** 使用

- 使用者已提供完整 intake spec（5 軸 + locale pair + skopos） — 跳過
  intake，讓 format-specialist 直接消費
- 任務不是翻譯 — 見 router 的 "When NOT to use" 處理跨 plugin routing

## 輸出

寫出 pipeline 中下一個 skill 要消費的 `intake-spec`。Schema
（audit-trail 的 `intake` block 子集）：

```json
{
  "mode": "literal | faithful | localized | transcreation",
  "register": "formal | neutral | warm | playful",
  "strategy": "domestication | foreignization",
  "source_locale": "BCP-47",
  "target_locale": "BCP-47",
  "domain": "single value or comma-joined values",
  "intent": "free-form skopos hint",
  "inferred": {
    "mode": true, "register": true, "strategy": true, "domain": true
  },
  "inferred_values": {
    "mode": "faithful"
  }
}
```

`inferred` 逐軸標示：`true` 為 auto 推論，`false` 為使用者提供。
`source_locale` 與 `target_locale` 永遠 implicitly `false`。
`inferred_values` 在 `--explicit` 覆寫某推論軸時，記錄 heuristic
*本來* 會挑哪個值。

## 此 skill **不做** 的事

- **不翻譯。** intake 只捕捉 parameter。直接把 source text 貼這裡，回傳的
  是 intake-spec，絕不是翻譯。
- **不 parse format 檔。** PO / JSON / XLIFF / Markdown AST parsing 是各
  format-specialist Layer 2 的職責。
- **不跑 verification gate。** M1 / M2 / S1 / S2 / I1 屬 Layer 4，由
  format-specialist 擁有。
- **不呼叫下游 skill。** 串接呼叫由 harness 執行；intake 只發出 spec。

## Audit-trail integration

intake 的判斷透過 `lib/audit_trail.AuditTrailBuilder` 流入共享的
audit trail。`builder.set_intake(...)` 與 `builder.add_inferred_value(...)`
呼叫見 [`SKILL.md`](SKILL.md) §"Audit-trail integration"，完整 schema 見
`scripts/canonical/audit-trail-spec.md`。

## Reference distribution note

`translation-intake` **刻意** 不在 `scripts/distribute.py` 的 `ACTIVE_SKILLS`
清單中。intake 只需要 5 軸 taxonomy + auto-inference heuristic（已 inline
在 `protocols/intake-auto.md`）與 audit-trail schema 的 intake-block 子集
（已 inline 在 `SKILL.md`）。把整套 canonical reference set 配發過來只會
多塞 7+ 個無關的 prompt / gate 檔，無 behavioral gain。intake 不持有 copy，
所以 drift 不可能發生。

## See also

- [`SKILL.md`](SKILL.md) — operational spec（5 軸表、輸出 schema、
  audit-trail integration）
- [`protocols/intake-auto.md`](protocols/intake-auto.md) — auto 模式 pipeline
- [`protocols/intake-explicit.md`](protocols/intake-explicit.md) —
  explicit 模式互動 + 範例 transcript
- Plugin overview: [`../../README.md`](../../README.md)
- Router: [`../using-translation-toolkit`](../using-translation-toolkit)
- Downstream: [`translation-i18n`](../translation-i18n) ·
  [`translation-doc`](../translation-doc) ·
  [`translation-creative`](../translation-creative) ·
  [`translation-audit`](../translation-audit)
- Canonical sources: `../../scripts/canonical/orthogonal-axes.md` ·
  `../../scripts/canonical/audit-trail-spec.md`
