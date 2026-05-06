# translation-i18n

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> i18n string を翻訳する — PO / JSON / XLIFF / Android `strings.xml` / iOS `.strings`。
> placeholder、key、plural、project glossary を保持する。

[translation-toolkit](../..) plugin の一部。Claude が読み込む operational
spec は [`SKILL.md`](SKILL.md)。本 README は人間向け。

## なぜ専用 i18n skill か

UI string には prose にはない制約がある — placeholder（`{name}`、
`%(count)s`、ICU `{n, plural, ...}`、Android `<plurals>`）は count と
arity を完全に round-trip しなければならない。key は drift 不可、
`translatable="false"` と PO `msgctxt` は遵守必須、1 つの key namespace 配下の
entry は cross-string consistency が必要（`Cancel` が同じアプリ内で
キャンセル と 中止 の両方になってはいけない）。

`translation-i18n` は専用設計：あらゆる placeholder を保護し、ファイル全体を
1 つの batch context で翻訳し、短い string 向けに調整した lean な gate matrix
を走らせ、byte レベルの忠実性で original format に書き戻す。

## Pipeline

```
intake-spec (translation-intake から)
        │
Layer 2 — Preparation
        ├── format parse（PO / JSON / XLIFF / Android / iOS）
        ├── protect-pass: placeholder を ⟦P:NN⟧ token として mask
        ├── source analysis: difficult term の候補を抽出
        └── glossary resolve（4-tier: L1 project → L2 bundled → L3 web → L4 LLM）
        │
Layer 3 — Core loop（DRAFT → REFLECT 4D → IMPROVE）
        │   └── single-batch context: 全 entry が <CONTEXT> で兄弟を見る；
        │       active entry は <TRANSLATE_THIS> でラップ
        │
Layer 4 — Verification（M1 + M2 のみ；S1 / S2 は短 string なので SKIPPED）
        │
Layer 5 — Output
        ├── ⟦P:NN⟧ → 元の placeholder bytes に restore
        ├── original format に書き戻す（key 順序、コメント、msgctxt、
        │   msgid_plural、<plurals>、translatable="false" を保持）
        └── audit-trail.json を発行
```

## Format サポート

最初に拡張子で auto-detect、続いて content sniffing。

| 拡張子 | Format | Notes |
|---|---|---|
| `.po` | gettext PO | `msgctxt` / `msgid_plural` / plural form を保持 |
| `.json` | JSON key-value | ネストオブジェクトを再帰；dot-notation key path |
| `.xliff` / `.xlf` | XLIFF 2.x | `<unit>` / `<segment>` / `<source>` / `<target>` |
| `strings.xml` | Android | `<string>` / `<plurals>` / `<string-array>`；`translatable="false"` はスキップ |
| `.strings` | iOS | `"key" = "value";` 行；`/* */` コメントを保持 |

format ごとの read+write アルゴリズムは
[`protocols/format-roundtrip.md`](protocols/format-roundtrip.md)。
8 項目の preflight は parse 前に MUST として
[`checklists/i18n-format-checklist.md`](checklists/i18n-format-checklist.md)
で走る。

## Verification gate matrix

4 つの format specialist で最も lean — M1 + M2 のみ HARD で、S1 / S2 は
SKIPPED。string ごとの i18n payload が短すぎて、back-translation 類似度や
register-classification gate が意味あるシグナルを出せないため。

| Gate | Tier | チェック内容 |
|---|---|---|
| **M1** | HARD | Placeholder integrity — `⟦P:NN⟧` の count と ID set parity を source / target 間で確認。決定論的な regex check。 |
| **M2** | HARD | Project glossary 準拠 — L1-mandated source term がすべて mapped target form として現れる。`notes: context-dependent` entry は PASS_ADVISORY。 |
| **S1** | SKIPPED | Back-translation — UI string は embedding-cosine 類似度が意味を持つには短すぎる。 |
| **S2** | SKIPPED | Register preservation — string あたりの token が少なすぎ。UI register は format 慣例（button text、dialog title）でいずれ pin される。 |
| **I1** | INFO | Untranslatability flagging — source-analysis が phrase を flag したときのみ実行。non-interactive: borrow / explain / approximate の判断を記録するが block しない。 |

**呼び出し側への含意**：i18n では M2 が支配的な品質レバー。
`<repo>/docs/i18n/glossary-{target_locale}.md` に投資すべきで、ここで
fire しない post-translation 類似度 gate に頼ってはいけない。

[`translation-audit`](../translation-audit) 経由で既存翻訳ペアに対して
呼ばれる場合は、audit のより厳格な semantics により完全な M1 + M2 + S1 + S2 + I1
matrix が適用される — i18n のローカルな skip は **forward-translation** run
に限る。

## Cross-string consistency

他の format specialist との決定的な違い：**ファイル全体が 1 つの batch
context**。entry が format レベルで independent でも、まとめて見る。

- 1 つの source ファイルから来る全 entry は、1 つの LLM context 内で単一の
  batch として翻訳される
- entry ごとの prompt は active entry を `<TRANSLATE_THIS>...</TRANSLATE_THIS>`
  でラップ；周辺 entry は `<CONTEXT>` のみで現れる
- 2000 token chunk threshold を超える file は entry 境界で分割
  （entry の途中では分割しない）；batch 内では全 entry が互いを見る

token はかさむが、語彙の一貫性で見返り、project-glossary churn を減らす。

## Web search ポリシー

デフォルト ON（spec Decision #15）。string 数千の batch i18n run では
miss あたりの search が cost と latency を倍増させるので OFF に上書きする：

```
--web-search=off
```

OFF のとき、glossary resolution は L2（bundled）で停止 — L3（web）は
スキップ、L4（LLM-fallback）は依然走る。フォローアップ pass で web search
を再有効化してサンプル spot-check する；untriaged な full batch を出荷しない。

## この skill が **行わないこと**

- **intake を走らせない。** [`translation-intake`](../translation-intake)
  に hand off する（または `--intake` で inline 実行）
- **Markdown を翻訳しない**（[`translation-doc`](../translation-doc)）、
  **transcreation variant を生成しない**（[`translation-creative`](../translation-creative)）、
  **既存ペアを audit しない**（[`translation-audit`](../translation-audit)）
- **M1 / M2 を bypass しない。** `--bypass-gates` フラグなし（spec
  Decision #15 によりアンチパターン）。元原因を直して再走させる。
- **I1 中に prompt しない。** Untranslatability の判断は記録され、聞かれない。

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
