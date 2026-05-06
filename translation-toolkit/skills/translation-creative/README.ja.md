# translation-creative

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> ad copy / headline / tagline / catchphrase を faithful または transcreation モードで翻訳する。

[translation-toolkit](../..) plugin の一部。Claude が読み込む operational
spec は [`SKILL.md`](SKILL.md)。本 README は人間向け。

## なぜ専用 creative skill か

ad copy は prose 翻訳が検出しないかたちで失敗する。back-translation
類似度スコアは PASS しても、target が source の説得 intent を失う —
弱い CTA、死んだ pun、異質な文化参照、silent な taboo。"Just do it." を
日本語に faithful 翻訳しても文法的には正しいが tagline としては使えない。

`translation-creative` は他の format specialist にない 2 要素を加える：
**5 番目の critique 軸**（Effectiveness、transcreation モード時）— target
が target 文化で説得 intent を保持しているかを評価 — と、**mode 条件付き
S1 tier flip** — WRITER が source 表面から逸脱する licence を持つときに
back-translation を HARD に昇格。variant も first-class 出力モードであり、
A/B 候補が paraphrase noise の代わりとなる。

## 2 つのモード

mode は intake-spec で宣言され、REFLECT 軸数 + S1 gate tier を制御する：

| Mode | REFLECT | S1 tier | Threshold | 使うとき |
|---|---|---|---|---|
| **faithful** | 4D（Accuracy / Fluency / Style / Terminology） | SHOULD（threshold 未満で WARN） | 0.85 | source 構造 + 文境界を保持し、phrasing のみ adapt |
| **transcreation** | 5D（4D + Effectiveness） | **MUST**（threshold 未満で FAIL） | 0.70 | target 文化で同等の説得を着地させるため source 表面を後にできる |

intake-spec で mode が指定されない場合、上流の `translation-intake` は
ad-shaped genre をデフォルトで `transcreation` に、prose-leaning な marketing
brief content を `faithful` にし、resolved mode + 理由を記録する。

完全な mode-entry contract — 5 番目の Effectiveness 軸、variant の差異、
S1 MUST contract、glossary leeway rule — は
[`protocols/transcreation-mode.md`](protocols/transcreation-mode.md) に。

## Pipeline

```
intake-spec (translation-intake から)
        │
Layer 2 — Preparation
        ├── brand brief intake（transcreation で推奨；faithful で任意）
        ├── protect-pass: URL / HTML / brand token を ⟦P:NN⟧ として mask
        ├── source analysis: 文化参照、wordplay、CTA verb、
        │   untranslatability 候補
        └── glossary resolve（4-tier）
        │
Layer 3 — Core loop（DRAFT → REFLECT 4D-or-5D → IMPROVE）
        │   └── WRITER は brand-brief context を受け取る；signature
        │       phrase + do-not-say リストを遵守
        │
Layer 4 — Verification（M1 + M2 HARD; S1 mode 条件付き;
        │   S2 SHOULD; I1 INFO）
        │
Layer 5 — Output
        ├── デフォルト: 1 翻訳
        ├── --variants=N: 軸差異化された prompt で N 個の独立した
        │   core-loop run（paraphrase ではない）
        └── audit-trail.json を発行（該当する場合 variant_index 付き）
```

## Brand brief

[`protocols/brand-brief-intake.md`](protocols/brand-brief-intake.md) に
従って捕捉。transcreation で推奨、faithful で任意（brief がなければ
intake-spec の `register` + `intent` に fallback）。

brief が捕捉するもの：brand archetype（Hero / Sage / Outlaw など）、
tone-of-voice 軸（authoritative ↔ playful、formal ↔ casual、
warm ↔ cool）、do-not-say リスト、signature phrase（verbatim-preserve
vs locale-transcreate）、target persona、CTA style、locale 別 brand-name
扱い（preserve / transliterate / locale-substitute）。出力は audit-trail
の `brand_brief` block に着地。

## Verification gate matrix

他の format specialist と区別する trait：**mode 条件付き S1 tier flip** —
back-translation は faithful で SHOULD だが transcreation で MUST に昇格。
ツールキット中で tier flip が HARD gate を駆動する唯一の場所。

| Gate | Tier | Action |
|---|---|---|
| **M1** | HARD | Placeholder integrity — count + ID set parity |
| **M2** | HARD | Project glossary 準拠。transcreation では [`protocols/transcreation-mode.md`](protocols/transcreation-mode.md) §"Glossary leeway" を参照 — 文化的に駆動された違反は audit 可能で許容される。 |
| **S1** | **transcreation で MUST、faithful で SHOULD** | Back-translation 類似度。Threshold = faithful で **0.85**（WARN）、transcreation で **0.70**（threshold 未満で FAIL は output を block）。 |
| **S2** | SHOULD | Register preservation — JUDGE が source vs target register を分類；ミスマッチで WARN。 |
| **I1** | INFO | Untranslatability flagging — transcreation で特に active。non-interactive: borrow / explain / approximate の判断を記録。 |

**なぜ S1 が transcreation で MUST に昇格するか**（spec Decision #4）：
WRITER が source 表面から大きく逸脱する licence を持つとき、M1
（placeholder count）と S2（register）は outright topic drift に対して
不十分な防御 — S1 は「v2 は別の製品の well-written copy」という事態を
唯一捕捉できる gate。

## Variants

`--variants=N` は opt-in。set されると、skill は N 個の **真に異なる**
代替案を発行する — 各 variant は完全で独立した DRAFT → REFLECT → IMPROVE
run であり、WRITER prompt は戦術軸（source 構造を保持 / target rhythm の
ために再構造 / 文化的に同等のメタファに置換 / など）で variation するよう
指示される。

variant は単一 draft の paraphrase ではない — このパターンは synonym-swap
noise を生むため明示的に禁止されている。audit trail の `variant_index`
field は issue を特定 variant に帰属させる。variant が transcreation モード
で S1 を fail すれば drop される；N 個すべてが fail すれば、N 未満を
silent に発行するのではなく run を halt する。

## Web search ポリシー

デフォルト ON — creative work は現在の文化 / campaign context から恩恵を
受ける。確立された brand voice が競合 copy から汚染されるリスクがある場合は
OFF（`--web-search=off`）に上書きする。Effectiveness 軸の critique は web
off でも training-time 知識から動作する；transcreation は web search を
要求しないが最近の slogan / meme / campaign 参照の鮮度を失う。

## Cross-plugin composition

`copywriting-toolkit` は creative 翻訳の **後** に voice / form / 倫理の
仕上げ用に呼び出せる。Composition は **user-explicit のみ** —
`translation-creative` は `copywriting-toolkit` を auto-invoke しない。
望むなら 2 つを sequential pair として走らせる；両 skill は補完的。

## この skill が **行わないこと**

- **intake を走らせない。** [`translation-intake`](../translation-intake)
  に hand off
- **brand strategy を生成しない。** transcreation モードで brief 不在は
  WARN を生み、生成された strategy ではない。
- **brand name を翻訳しない** — 明示的な intake 指示なしのデフォルトは
  verbatim-preserve。
- **`copywriting-toolkit` を auto-invoke しない** — composition は明示的。
- **単一 draft を variant に paraphrase しない** — `--variants=N` は N 個の
  独立した core loop を走らせる。
- **transcreation モードで S1 を bypass しない。** S1 が MUST のとき、
  threshold 未満の v2 は output を block する；revise するか human に
  escalate する。gate を off に flip しない。
- **human creative review を置き換えない。** audit trail + variant index は
  下流レビューを高速化するために設計されている。

## See also

- [`SKILL.md`](SKILL.md) — operational spec
- [`protocols/brand-brief-intake.md`](protocols/brand-brief-intake.md) ·
  [`protocols/transcreation-mode.md`](protocols/transcreation-mode.md)
  （5D Effectiveness、variant strategy、S1 MUST contract、glossary leeway）
- [`checklists/creative-checklist.md`](checklists/creative-checklist.md) ·
  [`references/5d-effectiveness.md`](references/5d-effectiveness.md)
- Plugin: [`../../README.md`](../../README.md) ·
  Router: [`../using-translation-toolkit`](../using-translation-toolkit) ·
  Layer 1: [`../translation-intake`](../translation-intake)
