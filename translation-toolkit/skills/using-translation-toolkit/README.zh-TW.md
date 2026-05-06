# using-translation-toolkit

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> translation-toolkit 的 router skill — 檢查 intent 與輸入形狀後 dispatch 到正確的 specialist。
> 不執行翻譯。

[translation-toolkit](../..) plugin 的一部分。Claude 載入的 operational spec 是
[`SKILL.md`](SKILL.md)；此 README 提供給人類判斷是否、以及如何呼叫
router。

## 為何需要 router

工具組附帶 5 個 worker skill，locale pair 重疊但在輸入形狀、gate matrix
與 core-loop variant（4D vs 5D、S1 SHOULD vs MUST、full pipeline vs audit）
上分歧明顯。挑錯 specialist 會造成沉默式品質退化 — 例如對 markdown
文件跑 `translation-i18n` 會跳過 AST protect-pass 並破壞 code fence；
對 PO 檔跑 `translation-doc` 則忽略 cross-string consistency batch。

router 存在的目的是讓使用者不必背誦那張 matrix。單一入口點檢查請求、
套用一條 routing rule（input shape 勝過 intent），然後交棒。

## 在哪些 specialist 之間 route

| Specialist | 何時落到此處 |
|---|---|
| [`translation-intake`](../translation-intake) | brief 含糊、無 format / domain hint，或指定 `--explicit` |
| [`translation-i18n`](../translation-i18n) | 輸入為 `.po` / `.json` / `.xliff` / `strings.xml` / `.strings` |
| [`translation-doc`](../translation-doc) | 輸入為 `.md` / `.mdx` / `.markdown` 或 technical-doc prose |
| [`translation-creative`](../translation-creative) | 輸入為 ad copy / headline / tagline / catchphrase / brand brief |
| [`translation-audit`](../translation-audit) | 同時提供 source AND 既有 target 並帶有 review intent |

## Routing rule

```
input-shape signal > intent signal
```

附上 PO 檔即使使用者說「creative」也會 route 到 `translation-i18n`。
`(source, target)` 配對即使 format 是 i18n 也會 route 到 `translation-audit`。
完整 disambiguation table 見 [`SKILL.md`](SKILL.md) §"Routing rules"。

## 何時使用此 router

- 使用者要求 `en-US` / `ja-JP` / `zh-TW` / `zh-CN` 之間翻譯，但未指名
  特定 specialist
- 使用者貼上待譯內容但沒有明示 pipeline
- 觸發語（任意 locale）：「translate / 翻訳して / 翻譯一下 / 翻译」、
  「i18n / localize / 本地化 / ローカライズ」、「audit translation /
  翻訳レビュー / 翻譯審核」、「transcreation / トランスクリエーション」

## 何時 **不** 使用

- 使用者明確指名下游 skill — 直接呼叫該 skill
- 任務不在翻譯範疇：
  - 原語言 copywriting → [`copywriting-toolkit`](../../../copywriting-toolkit)
  - 原語言文件撰寫 → [`domain-teams:docs-team`](../../../domain-teams)
  - 以 target locale 從零起草 → [`domain-teams:copywriting-team`](../../../domain-teams)
- locale pair 不在 v0.1.0 支援集合內（en-US ↔ ja-JP ↔ zh-TW ↔ zh-CN）

## 跨 plugin composition

`copywriting-toolkit` 與 `translation-toolkit` 代表 **正交** 的品質維度
（翻譯 fidelity ≠ copywriting 的說服 / form / 倫理）。兩者皆不會
auto-invoke 對方。若需要翻譯後的 copy 潤飾，必須明示串接：

```
translation-toolkit  →  target-language draft + audit-trail + gate verdicts
                            ↓ (使用者明確要求)
copywriting-toolkit  →  voice / form / 倫理 gate 套到 draft 上
```

這是設計上 opt-in — router 不會未經提示就跨越 plugin 邊界。

## 此 skill **不做** 的事

- **不翻譯。** 若把 source text 貼到 router 對話期待 target，router 會告訴
  你哪個 specialist 適用，並等待 harness 呼叫它。
- **不透過 Skill 工具呼叫 specialist。** 它描述 routing 決策；實際的串接
  呼叫由 runtime / harness 執行。
- **不決定 locale pair 或 strategy。** 那是
  [`translation-intake`](../translation-intake) 的職責。
- **不 audit 翻譯。** 那是
  [`translation-audit`](../translation-audit) 的職責。

## Web search 預設

4 個 active 的翻譯 skill 預設都開啟 web search（spec Decision #7）。
router 文件化兩種應使用 `--web-search=off` 的情境：

1. **Batch i18n run（數千條 string）** — 每次 miss 的 search 會放大成本與
   latency
2. **鎖定的 brand voice** — 競品 copy 可能污染 register

4 個下游所繼承的策略見 [`SKILL.md`](SKILL.md) §"Web search trade-off note"。

## See also

- [`SKILL.md`](SKILL.md) — operational spec（routing rules、disambiguation
  examples、roles vocabulary、跨 plugin contract）
- [`../../README.md`](../../README.md) — plugin 層級 overview（4-tier
  glossary、5-gate verification、支援 locale）
- [`../../docs/architecture.md`](../../docs/architecture.md) — 5-layer
  pipeline + 4-tier glossary fallthrough
- 兄弟 skill 的 README：
  [`translation-intake`](../translation-intake) ·
  [`translation-i18n`](../translation-i18n) ·
  [`translation-doc`](../translation-doc) ·
  [`translation-creative`](../translation-creative) ·
  [`translation-audit`](../translation-audit)
- Design spec: [`docs/superpowers/specs/2026-05-06-translation-toolkit-design.md`](../../../docs/superpowers/specs/2026-05-06-translation-toolkit-design.md)
