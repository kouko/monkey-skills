# using-translation-toolkit

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> translation-toolkit の router skill — 意図と入力形状を検査し、適切な specialist に dispatch する。
> 翻訳は行わない。

[translation-toolkit](../..) plugin の一部。Claude が読み込む operational spec は
[`SKILL.md`](SKILL.md)。本 README は router を呼び出すかどうか、どう
呼び出すかを判断する人間向け。

## なぜ router が必要か

このツールキットには 5 つの worker skill が同梱されている。locale pair は
重なるが、入力形状・gate matrix・core-loop の variant（4D vs 5D、
S1 SHOULD vs MUST、full pipeline vs audit）で大きく分岐する。誤った
specialist を選ぶと silent な品質劣化を招く — 例えば markdown ドキュメントに
`translation-i18n` を走らせれば AST protect-pass がスキップされて code fence が
壊れる。PO ファイルに `translation-doc` を走らせれば cross-string consistency
batch が無視される。

router の存在意義は、ユーザーがその matrix を覚えなくて済むようにすること。
単一エントリーポイントがリクエストを検査し、1 本の routing rule（input
shape が intent に勝つ）を適用してハンドオフする。

## どこに route するか

| Specialist | 該当条件 |
|---|---|
| [`translation-intake`](../translation-intake) | brief が曖昧、format / domain hint なし、または `--explicit` 指定 |
| [`translation-i18n`](../translation-i18n) | 入力が `.po` / `.json` / `.xliff` / `strings.xml` / `.strings` |
| [`translation-doc`](../translation-doc) | 入力が `.md` / `.mdx` / `.markdown` または technical-doc prose |
| [`translation-creative`](../translation-creative) | 入力が ad copy / headline / tagline / catchphrase / brand brief |
| [`translation-audit`](../translation-audit) | source AND 既存 target の両方が review intent と共に提供される |

## Routing rule

```
input-shape signal > intent signal
```

PO ファイルが添付されていれば、ユーザーが「creative」と言っても
`translation-i18n` に route される。`(source, target)` ペアは format が
i18n でも `translation-audit` に route される。完全な disambiguation table
は [`SKILL.md`](SKILL.md) §"Routing rules" を参照。

## この router を使うとき

- ユーザーが `en-US` / `ja-JP` / `zh-TW` / `zh-CN` 間の翻訳を依頼し、
  特定の specialist を名指ししていない
- ユーザーが翻訳対象コンテンツを貼ったが explicit な pipeline 指定がない
- トリガーフレーズ（言語不問）：「translate / 翻訳して / 翻譯一下 / 翻译」、
  「i18n / localize / 本地化 / ローカライズ」、「audit translation /
  翻訳レビュー / 翻譯審核」、「transcreation / トランスクリエーション」

## 使わないとき

- ユーザーが downstream skill を明示的に名指ししている — 直接呼び出す
- タスクが翻訳スコープ外：
  - 元言語での copywriting → [`copywriting-toolkit`](../../../copywriting-toolkit)
  - 元言語でのドキュメント執筆 → [`domain-teams:docs-team`](../../../domain-teams)
  - target locale で原文起こし → [`domain-teams:copywriting-team`](../../../domain-teams)
- locale pair が v0.1.0 サポート集合外（en-US ↔ ja-JP ↔ zh-TW ↔ zh-CN）

## Cross-plugin composition

`copywriting-toolkit` と `translation-toolkit` は **直交する** 品質次元を
表す（翻訳 fidelity ≠ copywriting の説得 / form / 倫理）。どちらも
他方を auto-invoke しない。翻訳後の copy 仕上げが欲しい場合は明示的に
チェインする：

```
translation-toolkit  →  target-language draft + audit-trail + gate verdicts
                            ↓ (ユーザーが明示的に依頼)
copywriting-toolkit  →  voice / form / 倫理 gate を draft に適用
```

これは設計上 opt-in — router は plugin 境界を跨いで先回りすることはない。

## この skill が **行わないこと**

- **翻訳しない。** router 会話に source text を貼って target を期待しても、
  router はどの specialist が該当するかを伝え、harness が呼び出すのを待つ。
- **Skill ツール経由で specialist を呼び出さない。** routing 判断を述べる
  だけで、実際のチェイン呼び出しは runtime / harness が行う。
- **locale pair や strategy を決めない。** それは
  [`translation-intake`](../translation-intake) の役割。
- **翻訳の audit はしない。** それは
  [`translation-audit`](../translation-audit) の役割。

## Web search のデフォルト

4 つの active な翻訳 skill はすべて web search **ON** がデフォルト
（spec Decision #7）。router は `--web-search=off` が妥当な 2 ケースを
ドキュメント化している：

1. **Batch i18n run（数千の string）** — miss あたりの search が cost と
   latency を倍増させる
2. **Locked brand voice** — 競合 copy が register を汚染する恐れ

4 つの downstream が継承するポリシーは [`SKILL.md`](SKILL.md) §"Web search
trade-off note" を参照。

## See also

- [`SKILL.md`](SKILL.md) — operational spec（routing rules、disambiguation
  examples、roles vocabulary、cross-plugin contract）
- [`../../README.md`](../../README.md) — plugin レベル overview（4-tier
  glossary、5-gate verification、サポート locale）
- [`../../docs/architecture.md`](../../docs/architecture.md) — 5-layer
  pipeline + 4-tier glossary fallthrough
- 兄弟 skill の README：
  [`translation-intake`](../translation-intake) ·
  [`translation-i18n`](../translation-i18n) ·
  [`translation-doc`](../translation-doc) ·
  [`translation-creative`](../translation-creative) ·
  [`translation-audit`](../translation-audit)
- Design spec: [`docs/superpowers/specs/2026-05-06-translation-toolkit-design.md`](../../../docs/superpowers/specs/2026-05-06-translation-toolkit-design.md)
