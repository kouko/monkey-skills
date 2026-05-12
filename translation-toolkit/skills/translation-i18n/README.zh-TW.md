# translation-i18n

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 翻譯 i18n string — PO / JSON / XLIFF / Android `strings.xml` / iOS `.strings`。
> 保留 placeholder、key、plural 與 project glossary。

[translation-toolkit](../..) plugin 的一部分。Claude 載入的 operational
spec 是 [`SKILL.md`](SKILL.md)；此 README 提供給人類。

## 為何需要專用 i18n skill

UI string 帶有 prose 沒有的限制 — placeholder（`{name}`、
`%(count)s`、ICU `{n, plural, ...}`、Android `<plurals>`）必須以準確的
count 與 arity round-trip；key 不可漂移；`translatable="false"` 與 PO
`msgctxt` 必須遵守；同一 key namespace 下的 entry 需要 cross-string
consistency（`Cancel` 不能在同一個 app 裡同時是 キャンセル 又是 中止）。

`translation-i18n` 為此而生：保護每一個 placeholder、把整個檔案放在一個
batch context 內翻譯、跑一個為短 string 調校過的精簡 gate matrix、以
byte 級忠實度寫回原始 format。

## Pipeline

```
intake-spec（來自 translation-intake）
        │
Layer 2 — Preparation
        ├── parse format（PO / JSON / XLIFF / Android / iOS）
        ├── protect-pass: 將 placeholder mask 為 ⟦P:NN⟧ token
        ├── source analysis: 抽取困難 term 候選
        └── glossary resolve（4-tier: L1 project → L2 bundled → L3 web → L4 LLM）
        │
Layer 3 — Core loop（DRAFT → REFLECT 4D → IMPROVE）
        │   └── single-batch context: 全 entry 透過 <CONTEXT> 看見兄弟；
        │       active entry 以 <TRANSLATE_THIS> 包裹
        │
Layer 4 — Verification（僅 M1 + M2；S1 / S2 因 string 太短 SKIPPED）
        │
Layer 5 — Output
        ├── 還原 ⟦P:NN⟧ → 原本的 placeholder bytes
        ├── 寫回原始 format（保留 key 順序、註解、msgctxt、
        │   msgid_plural、<plurals>、translatable="false"）
        └── 發出 audit-trail.json
```

## Format 支援

先以副檔名 auto-detect，再以 content sniffing 確認。

| 副檔名 | Format | Notes |
|---|---|---|
| `.po` | gettext PO | 保留 `msgctxt` / `msgid_plural` / plural form |
| `.json` | JSON key-value | 遞迴展開巢狀物件；dot-notation key path |
| `.xliff` / `.xlf` | XLIFF 2.x | `<unit>` / `<segment>` / `<source>` / `<target>` |
| `strings.xml` | Android | `<string>` / `<plurals>` / `<string-array>`；`translatable="false"` 跳過 |
| `.strings` | iOS | `"key" = "value";` 列；保留 `/* */` 註解 |

各 format 的讀 / 寫演算法見
[`protocols/format-roundtrip.md`](protocols/format-roundtrip.md)。
8 項 preflight 由
[`checklists/i18n-format-checklist.md`](checklists/i18n-format-checklist.md)
在 parse 前 MUST 執行。

## Verification gate matrix

4 個 format specialist 中最精簡 — 只有 M1 + M2 為 HARD；S1 / S2 因
單一 i18n string payload 太短，無法讓 back-translation 相似度或
register-classification gate 產生有意義訊號，故 SKIPPED。

| Gate | Tier | 檢查內容 |
|---|---|---|
| **M1** | HARD | Placeholder integrity — 比對 source / target 的 `⟦P:NN⟧` count 與 ID set parity。確定性 regex check。 |
| **M2** | HARD | Project glossary 合規 — L1-mandated 的每個 source term 都以對應 target form 出現。`notes: context-dependent` entry 為 PASS_ADVISORY。 |
| **S1** | SKIPPED | Back-translation — UI string 太短，embedding-cosine 相似度無意義訊號。 |
| **S2** | SKIPPED | Register preservation — 每 string token 太少；UI register 反正會被 format 慣例（button text、dialog title）釘住。 |
| **I1** | INFO | Untranslatability flagging — 僅在 source-analysis flag 某 phrase 時觸發。non-interactive: 記錄 borrow / explain / approximate 決策；不阻擋。 |

**對呼叫者的含意**：i18n 的主要品質槓桿是 M2。把投資放在
`<repo>/docs/i18n/glossary-{target_locale}.md`，不要倚賴在這裡不會 fire 的
post-translation 相似度 gate。

當經由 [`translation-audit`](../translation-audit) 對既有翻譯配對呼叫時，
audit 較嚴的 semantics 會讓完整 M1 + M2 + S1 + S2 + I1 matrix 生效 — i18n
本地的 skip 只適用 **forward-translation** run。

## Cross-string consistency

與其他 format specialist 的關鍵差異：**整個檔案是一個 batch context**，
即使 entry 在 format 層級互相獨立。

- 一個 source 檔的全部 entry 在同一個 LLM context 內以單一 batch 翻譯
- 每 entry prompt 把 active entry 以 `<TRANSLATE_THIS>...</TRANSLATE_THIS>`
  包起；周邊 entry 以 `<CONTEXT>` 出現
- 超過 2000 token chunk threshold 的檔案於 entry 邊界切分
  （絕不在 entry 內切）；batch 內全 entry 互相可見

這多耗 token，但換得詞彙一致性與更少的 project-glossary churn。

## Web search 策略

預設 ON（spec Decision #15）。對 string 數千的 batch i18n run，每次 miss
的 search 會放大成本與 latency，覆寫為 OFF：

```
--web-search=off
```

OFF 時 glossary resolution 停在 L2（bundled） — L3（web）跳過，
L4（LLM-fallback）仍跑。後續 pass 重新開啟 web search 對樣本做 spot-check；
不要把未經 triage 的整個 batch 直接出貨。

## 此 skill **不做** 的事

- **不跑 intake。** 交棒給 [`translation-intake`](../translation-intake)
  （或用 `--intake` inline 跑）
- **不翻譯 Markdown**（[`translation-doc`](../translation-doc)）、
  **不生成 transcreation variant**（[`translation-creative`](../translation-creative)）、
  **不 audit 既有配對**（[`translation-audit`](../translation-audit)）
- **不 bypass M1 / M2。** 沒有 `--bypass-gates` flag（依 spec
  Decision #15 為反模式）。修根本問題後重跑。
- **I1 期間不 prompt。** Untranslatability 決策被記錄、不被詢問。

## See also

- [`SKILL.md`](SKILL.md) — operational spec
- [`protocols/placeholder-protect.md`](protocols/placeholder-protect.md) ·
  [`protocols/format-roundtrip.md`](protocols/format-roundtrip.md) ·
  [`checklists/i18n-format-checklist.md`](checklists/i18n-format-checklist.md)
- [`references/verification-gates.md`](references/verification-gates.md) ·
  [`references/protect-pass-spec.md`](references/protect-pass-spec.md)
- Plugin: [`../../README.md`](../../README.md) ·
  Router: [`../using-translation-toolkit`](../using-translation-toolkit) ·
  Layer 1: [`../translation-intake`](../translation-intake)
