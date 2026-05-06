# translation-doc

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> markdown / technical documentation を翻訳する。
> code block、URL、HTML、math、frontmatter、mermaid、ASCII 図を保持する。

[translation-toolkit](../..) plugin の一部。Claude が読み込む operational
spec は [`SKILL.md`](SKILL.md)。本 README は人間向け。

## なぜ専用 doc skill か

Markdown は prose に見えるが全部が prose ではない。素朴に翻訳 pass を
かければ code fence が re-flow され、URL path が翻訳され、mermaid 図の
source が壊れ、YAML frontmatter の key が落ち、TOC anchor が壊れる —
すべて LLM 出力レベルでは silent で、renderer が壊れるか、reviewer が
anchor が解決しないことに気付くまで露見しない。

`translation-doc` は markdown AST を歩き、すべての構造的 span（base
placeholder 8 クラス + markdown 固有拡張）を mask し、prose のみ翻訳し、
roundtrip clean な target を再構築する。chunk は十分長く、S1 + S2
（back-translation 類似度 + register 分類）が信頼できるシグナルを出す —
短い UI string で gate が noisy になる `translation-i18n` と違って。

## Pipeline

```
intake-spec (translation-intake から)
        │
Layer 2 — Preparation
        ├── markdown AST parse: prose block vs structural block
        ├── protect-pass: code / URL / HTML / math / frontmatter /
        │   mermaid / ASCII 図を ⟦P:NN⟧ token として mask
        ├── source analysis: difficult term の候補を抽出
        └── glossary resolve（4-tier: L1 project → L2 bundled → L3 web → L4 LLM）
        │
Layer 3 — Core loop（DRAFT → REFLECT 4D → IMPROVE）
        │   └── cross-chunk windowing: 全文書を context として；
        │       active chunk は <TRANSLATE_THIS> でラップ
        │
Layer 4 — Verification（M1 + M2 HARD; S1 + S2 SHOULD; I1 INFO）
        │
Layer 5 — Output
        ├── ⟦P:NN⟧ → 元の span に restore
        ├── markdown を再構築（heading 深度、list nesting、
        │   footnote 順序、table separator を保持）
        ├── roundtrip check（code block byte-identical、link target
        │   不変、anchor 解決可能）
        └── audit-trail.json を発行
```

## 何が保護されるか

全体が mask される（LLM は中身の bytes を見ない）：fenced / inline / indented
code、bare URL、HTML block + inline tag、LaTeX math（`$$…$$` / `$…$`）、
YAML frontmatter 本体、mermaid + ASCII 図。markdown link syntax
`[text](url)` の中では `url` のみ mask — `text` は翻訳可能のまま。
table separator と footnote label も mask。

markdown 固有のパターンは `references/protect-pass-spec.md` に文書化された
8 base クラスの上に layer されている。要素ごとのルールは
[`protocols/markdown-ast-protect.md`](protocols/markdown-ast-protect.md)。

## Cross-chunk windowing

長い markdown 文書はセクション境界で chunk 化する。chunk ごとに、
WRITER / CRITIC / REVISER prompt は **文書全体** を再発行し、active chunk
のみ `<TRANSLATE_THIS>...</TRANSLATE_THIS>` でラップ；周辺セクションは
ラップなしで context として現れる。

これにより以下が保たれる：

- **Cross-section term 一貫性** — Section 3 で翻訳された glossary term は
  Section 7 で再使用されても一貫
- **Heading-anchor 連続性** — active chunk の heading は文書全体の heading
  set を完全に見て翻訳されるため、target anchor が一貫する
- **Footnote-reference integrity** — label も同じ windowing に従う

2000 token chunk threshold 以下では、文書は単一 chunk であり windowing は
通常の prompt に縮退する。

## Verification gate matrix

prose 長 chunk 向けに調整されたフル gate set：

| Gate | Tier | チェック内容 |
|---|---|---|
| **M1** | HARD | Placeholder integrity — code / URL / HTML / math / frontmatter / 図 token の `⟦P:NN⟧` count + ID set parity |
| **M2** | HARD | Project glossary 準拠 — L1-mandated 全 source term が mapped target form として現れる |
| **S1** | SHOULD | Back-translation — subagent が blind に v2 → source を retranslation；source に対する embedding-cosine 類似度。threshold 未満で WARN；output は進む。runtime が isolation を提供しない場合は audit-trail フラグ付きでスキップ。 |
| **S2** | SHOULD | Register preservation — JUDGE が source vs target の register を分類；ミスマッチで WARN |
| **I1** | INFO | Untranslatability flagging — source-analysis が phrase を flag したときのみ実行。non-interactive。 |

S1 / S2 は SHOULD で HARD ではない：明確な原因のある single-chunk failure
は audit-trail に記録され caller に surface するが、emit を block しない。
M1 / M2 は依然 failure で HARD-block。

## Roundtrip checklist

emit 前に [`checklists/doc-quality-checklist.md`](checklists/doc-quality-checklist.md)
が以下を verify：

1. Code block が byte-identical
2. Link target が不変
3. Heading level が一致
4. TOC anchor が解決可能
5. Mermaid + ASCII 図が byte-identical
6. Frontmatter key が保持されている

いずれかの項目で failure があれば emit を halt し caller に surface。

## Web search ポリシー

デフォルト ON。数百ページのハンドブック翻訳のような batch doc run では
OFF に上書きする：

```
--web-search=off
```

OFF のとき、glossary resolution は L2（bundled）で停止 — L3（web）は
スキップ、L4（LLM-fallback）は依然走る。

## この skill が **行わないこと**

- **intake を走らせない。** [`translation-intake`](../translation-intake)
  に hand off する（または `--intake` を使う）
- **code-block の中身に触らない**、**ASCII / mermaid 図を変更しない** —
  両方とも全体 mask。図 node label のローカライズは下流の手作業タスク。
- **URL path を翻訳しない** — link `text` のみ翻訳可能。
- **i18n ファイルを翻訳しない**（[`translation-i18n`](../translation-i18n)）、
  **variant を生成しない**（[`translation-creative`](../translation-creative)）、
  **既存ペアを audit しない**（[`translation-audit`](../translation-audit)）
- **M1 / M2 を bypass しない。** `--bypass-gates` フラグなし（spec
  Decision #15 によりアンチパターン）

## See also

- [`SKILL.md`](SKILL.md) — operational spec
- [`protocols/markdown-ast-protect.md`](protocols/markdown-ast-protect.md) ·
  [`checklists/doc-quality-checklist.md`](checklists/doc-quality-checklist.md)
- [`references/verification-gates.md`](references/verification-gates.md) ·
  [`references/core-loop.md`](references/core-loop.md) (`<TRANSLATE_THIS>` windowing)
- Typography: [`typography/jlreq-summary.md`](typography/jlreq-summary.md) (ja-JP) ·
  [`typography/clreq-summary.md`](typography/clreq-summary.md) (zh-CN / zh-TW)
- Plugin: [`../../README.md`](../../README.md) ·
  Router: [`../using-translation-toolkit`](../using-translation-toolkit) ·
  Layer 1: [`../translation-intake`](../translation-intake)
