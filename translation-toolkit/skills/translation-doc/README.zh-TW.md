# translation-doc

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> 翻譯 markdown / 技術文件。
> 保留 code block、URL、HTML、math、frontmatter、mermaid 與 ASCII 圖。

[translation-toolkit](../..) plugin 的一部分。Claude 載入的 operational
spec 是 [`SKILL.md`](SKILL.md)；此 README 提供給人類。

## 為何需要專用 doc skill

Markdown 看起來像 prose 但不全是 prose。一個天真的翻譯 pass 會 re-flow
code fence、把 URL path 翻譯掉、毀掉 mermaid 圖原始碼、漏掉 YAML
frontmatter key、打斷 TOC anchor — 全部在 LLM 輸出層級沉默無聲，要等到
renderer 壞掉或 reviewer 注意到 anchor 解析失敗才會浮現。

`translation-doc` 走訪 markdown AST、把每一個結構性 span（8 base
placeholder 類別 + markdown 專屬延伸）mask 起來、只翻譯 prose、再組裝出
roundtrip 乾淨的 target。chunk 夠長足以讓 S1 + S2（back-translation 相似度
+ register 分類）產生可靠訊號 — 不像 `translation-i18n` 短 UI string 讓
這些 gate 太雜訊。

## Pipeline

```
intake-spec（來自 translation-intake）
        │
Layer 2 — Preparation
        ├── markdown AST parse: prose block vs structural block
        ├── protect-pass: code / URL / HTML / math / frontmatter /
        │   mermaid / ASCII 圖 mask 為 ⟦P:NN⟧ token
        ├── source analysis: 抽取困難 term 候選
        └── glossary resolve（4-tier: L1 project → L2 bundled → L3 web → L4 LLM）
        │
Layer 3 — Core loop（DRAFT → REFLECT 4D → IMPROVE）
        │   └── cross-chunk windowing: 整份文件作為 context；
        │       active chunk 以 <TRANSLATE_THIS> 包裹
        │
Layer 4 — Verification（M1 + M2 HARD；S1 + S2 SHOULD；I1 INFO）
        │
Layer 5 — Output
        ├── 還原 ⟦P:NN⟧ → 原本 span
        ├── 重組 markdown（保留 heading 深度、list nesting、
        │   footnote 順序、table separator）
        ├── roundtrip check（code block byte-identical、link target
        │   不變、anchor 可解析）
        └── 發出 audit-trail.json
```

## 哪些東西會被保護

整段 mask（LLM 完全看不到內部 bytes）：fenced / inline / indented code、
裸 URL、HTML block + inline tag、LaTeX math（`$$…$$` / `$…$`）、
YAML frontmatter 內容、mermaid + ASCII 圖。在 markdown link 語法
`[text](url)` 中，只有 `url` 被 mask — `text` 仍可翻譯。table separator
與 footnote label 也會 mask。

markdown 專屬模式 layer 在 `references/protect-pass-spec.md` 文件化的 8 個
base 類別之上。逐元素規則見
[`protocols/markdown-ast-protect.md`](protocols/markdown-ast-protect.md)。

## Cross-chunk windowing

長 markdown 文件在章節邊界切 chunk。每個 chunk 內，WRITER / CRITIC /
REVISER prompt 都重新發出 **整份文件**，僅 active chunk 以
`<TRANSLATE_THIS>...</TRANSLATE_THIS>` 包裹；周邊章節以未包裹的形式作為
context 出現。

這樣可保住：

- **Cross-section term 一致性** — 在 Section 3 翻譯的 glossary term 在
  Section 7 再度出現時保持一致
- **Heading-anchor 連續性** — active chunk 的 heading 是在看見全文 heading
  set 的情況下翻譯，因此 target anchor 一致
- **Footnote-reference integrity** — label 沿用同一套 windowing

低於 2000 token chunk threshold 時，文件就是單一 chunk，windowing 退化為
普通 prompt。

## Verification gate matrix

為 prose 長度 chunk 校準的完整 gate set：

| Gate | Tier | 檢查內容 |
|---|---|---|
| **M1** | HARD | Placeholder integrity — code / URL / HTML / math / frontmatter / 圖 token 的 `⟦P:NN⟧` count + ID set parity |
| **M2** | HARD | Project glossary 合規 — L1-mandated 的每個 source term 都以對應 target form 出現 |
| **S1** | SHOULD | Back-translation — subagent blind 把 v2 → source 重譯；對 source 做 embedding-cosine 相似度。低於 threshold 給 WARN；output 仍進行。runtime 沒提供 isolation 時帶 audit-trail flag 跳過。 |
| **S2** | SHOULD | Register preservation — JUDGE 分類 source vs target register；不符給 WARN |
| **I1** | INFO | Untranslatability flagging — 僅當 source-analysis flag 某 phrase 時觸發。non-interactive。 |

S1 / S2 是 SHOULD 不是 HARD：成因明確的單一 chunk failure 會記錄到
audit-trail 並 surface 給 caller，但不阻擋 emit。M1 / M2 失敗仍 HARD-block。

## Roundtrip checklist

emit 前 [`checklists/doc-quality-checklist.md`](checklists/doc-quality-checklist.md)
會 verify：

1. Code block byte-identical
2. Link target 不變
3. Heading level 相符
4. TOC anchor 可解析
5. Mermaid + ASCII 圖 byte-identical
6. Frontmatter key 保留

任何項目失敗就 halt emit 並 surface 給 caller。

## Web search 策略

預設 ON。對 batch doc run（例如翻譯數百頁 handbook）覆寫為 OFF：

```
--web-search=off
```

OFF 時 glossary resolution 停在 L2（bundled） — L3（web）跳過，
L4（LLM-fallback）仍跑。

## 此 skill **不做** 的事

- **不跑 intake。** 交棒給 [`translation-intake`](../translation-intake)
  （或用 `--intake`）
- **不碰 code-block 內容**、**不修改 ASCII / mermaid 圖** —
  兩者皆整段 mask。把圖 node label 在地化是下游手動工作。
- **不翻譯 URL path** — 只有 link `text` 可譯。
- **不翻譯 i18n 檔**（[`translation-i18n`](../translation-i18n)）、
  **不生成 variant**（[`translation-creative`](../translation-creative)）、
  **不 audit 既有配對**（[`translation-audit`](../translation-audit)）
- **不 bypass M1 / M2。** 沒有 `--bypass-gates` flag（依 spec
  Decision #15 為反模式）

## See also

- [`SKILL.md`](SKILL.md) — operational spec
- [`protocols/markdown-ast-protect.md`](protocols/markdown-ast-protect.md) ·
  [`checklists/doc-quality-checklist.md`](checklists/doc-quality-checklist.md)
- [`references/verification-gates.md`](references/verification-gates.md) ·
  [`references/core-loop.md`](references/core-loop.md)（`<TRANSLATE_THIS>` windowing）
- Typography: [`typography/jlreq-summary.md`](typography/jlreq-summary.md)（ja-JP）·
  [`typography/clreq-summary.md`](typography/clreq-summary.md)（zh-CN / zh-TW）
- Plugin: [`../../README.md`](../../README.md) ·
  Router: [`../using-translation-toolkit`](../using-translation-toolkit) ·
  Layer 1: [`../translation-intake`](../translation-intake)
