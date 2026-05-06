# translation-audit

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 既存の `(source, target)` ペアを完全な 5-gate suite に対してレビューし、diff レポートを発行する。

[translation-toolkit](../..) plugin の一部。Claude が読み込む operational
spec は [`SKILL.md`](SKILL.md)。本 README は人間向け。

## なぜ独立した audit skill か

forward 系 skill（`translation-i18n`、`translation-doc`、`translation-creative`）は
draft → revise の途中で「正当な stylistic restructuring を block しない」
ように gate を calibrate している。target が固定されており問いが
**「この target は受け入れ可能か」** であるとき、その calibration は誤り。

audit は **完全な M1 + M2 + S1 + S2 + I1** matrix を走らせ、**S1 + S2 を
SHOULD から HARD に upgrade する** — threshold 未満の verdict は WARN
ではなく FAIL となり、reviewer に具体的な triage queue を提供する。
これはツールキット中で唯一 S1 / S2 が HARD failure を生む context であり、
唯一 output が翻訳された artifact ではなく **review 文書** となる skill。
Layer 3（DRAFT / REFLECT / IMPROVE）は意図的に skip — ユーザー提供の target
こそ review の対象 unit である。

## 入力

| 入力 | 必須 | Notes |
|---|---|---|
| `source` | はい | ツールキットが parse できる任意 format（`.po` / `.json` / `.xliff` / `strings.xml` / `.strings` / `.md` / `.mdx` / plain text） |
| `existing target` | はい | ファイルパスまたは inline string。format は source と異なってよい（migration audit、vendor delivery review）。 |
| `intake-spec` | 推奨 | `translation-intake` から。なければ source に対して intake を先に走らせる。`mode` / `register` / locale pair を持ち、すべて S2 strictness と I1 framing を informす。 |
| `glossary_path` | 任意 | デフォルトは `<repo>/docs/i18n/glossary-{target_locale}.md` |

## Pipeline

```
intake-spec (translation-intake から; または source から auto-推論)
        │
Layer 2 — Preparation
        ├── source と target の **両方** を parse（format は異なってよい）
        ├── 両側に protect-pass（dual tokenization により M1 の
        │   count-parity check が意味を持つ）
        ├── 両側に source analysis（target は source と独立した issue を
        │   持ちうる）
        └── glossary resolve（4-tier; source term に対して resolve、
            target に対して compliance チェック）
        │
Layer 3 — SKIPPED（ユーザー提供の target が review 対象 unit）
        │
Layer 4 — Verification（FULL M1 + M2 + S1 + S2 + I1; S1 + S2 は HARD に upgrade）
        │
Layer 5 — Output
        ├── diff レポート（markdown; 6 セクション; rewrite なし）
        └── audit-trail.json（フル provenance）
```

## Verification gate matrix

より厳格な semantics を持つフル matrix — この skill が存在する理由。

| Gate | audit での Tier | チェック内容 |
|---|---|---|
| **M1** | HARD | dual protect-pass 後に source / target の placeholder count を比較。Diff フォーマットは chunk ごとに `source_count` / `target_count` / `missing_in_target` / `extra_in_target` を記録。 |
| **M2** | HARD | Project glossary 準拠。違反は term ごとに `project_glossary` vs `target_used` と tier / audit_path provenance と共に報告。`notes: context-dependent` entry には PASS_ADVISORY が依然適用される。 |
| **S1** | **HARD**（旧 SHOULD） | Subagent が target → source-language を翻訳；元 source に対する embedding-cosine 類似度。Threshold = **0.85**。threshold 未満 → diff レポートで **FAIL**、WARN ではない。 |
| **S2** | **HARD**（旧 SHOULD） | LLM JUDGE が既存 target の register を分類し、source + intake-spec から期待される register と比較。ミスマッチ → **FAIL**。reviewer がミスマッチを許容できる shift か defect か判断できるように JUDGE rationale を含める。 |
| **I1** | INFO | Untranslatability handling — untranslatable と flag された各 source phrase に対し、target は borrow / explain / approximate handling を示さなければならない。handling 欠落は報告されるが block しない。 |

**なぜ S1 / S2 がここで HARD に upgrade するか**：WARN 限定は forward 系
skill の draft → revise loop 向け calibration。target が固定されているとき、
あらゆる客観的および structured-judgment issue は reviewer の triage queue
向けに具体的な failure として surface すべき。M2 の `notes: context-dependent`
PASS_ADVISORY 例外は保たれる — その例外は entry についてのもので、gate
tier についてではない。

## Diff レポート

[`protocols/diff-report.md`](protocols/diff-report.md) に従った markdown
文書で、6 セクション：header（path + timestamp + intake snapshot +
glossary version）、summary verdict、per-gate verdict block（M1 / M2 /
S1 / S2 / I1 と diff）、line ref 付き inline issue、recommendations
（guidance であって edit ではない）、reviewer 判断捕捉のための sign-off block。

改善提案は inline issue ごとに現れるが、レポートは **決して** 修正された
target を書かない。reviewer は下流で fix を適用する（典型的には source に
対して `translation-{i18n,doc,creative}` を再走させるか、手で編集して
re-audit する）。

## 出力パス

デフォルト emit（caller は service interface 経由で override 可能）：

- `<target_path>.audit.md` — diff レポート
- `<target_path>.audit-trail.json` — machine-readable companion

audit はディスク上の target ファイルを変更しない。

## 使うとき

- pre-merge 翻訳 review
- ベンダー / agency delivery 品質チェック
- 再翻訳後の regression check
- localized release 公開前の 内部 QA gate
- 同一 source の競合する 2 翻訳の A/B 比較
  （候補ごとに 1 回ずつ計 2 回走らせる）

## 使わないとき

- 順方向翻訳 — `translation-{i18n,doc,creative}` を使う
- intake clarification のみ — [`translation-intake`](../translation-intake) を使う
- 競合翻訳の作成 — audit は生成しない

## Web search ポリシー

デフォルト ON。Audit モードは 4 つの active skill 中 web search の恩恵を
最も多く受ける — L3（web）glossary lookup は existing target が無視した
authoritative target form を頻繁に surface する。offline 実行（例えば
network-isolated CI host 上）でのみ OFF に上書き：

```
--web-search=off
```

## Roles

ツールキット残部と同じ vocabulary、ただし Layer 3 の skip により
**WRITER / REVISER は除外**：

- **CRITIC** — 既存 target に対し S2 / I1 framing 中に structured 4D / 5D
  critique を生成；rewrite はしない
- **BACK-TRANSLATOR** — blind に target → source を retranslation、S1 で使用
- **JUDGE** — register 分類、S2 で使用

## この skill が **行わないこと**

- **既存 target を rewrite しない。** Audit は設計上 read-only。Layer 3 は
  skip され `--produce-target` フラグは存在しない（その path は forward 系 skill）。
- **改善提案を適用しない** — それらは reviewer 向け guidance であって edit ではない。
- **ファイル format を変更しない。** write-back なし。ディスク上の元 target
  ファイルは触らない。
- **M1 / M2 / S1 / S2 を bypass しない。** `--bypass-gates` フラグなし
  （spec Decision #15 によりアンチパターン）。5 gate すべてが走る。
- **I1 中に prompt しない。** target に存在する untranslatability handling
  は記録される；handling 欠落は issue として報告される。
- **human reviewer の判断を置き換えない。** S1 / S2 の FAIL verdict は
  review 用に issue を flag する；ship / no-ship 判断は diff レポートの
  sign-off セクションが捕捉し、skill ではない。

## See also

- [`SKILL.md`](SKILL.md) — operational spec
- [`protocols/diff-report.md`](protocols/diff-report.md) ·
  [`checklists/audit-completeness-checklist.md`](checklists/audit-completeness-checklist.md)
- [`references/verification-gates.md`](references/verification-gates.md) ·
  [`references/protect-pass-spec.md`](references/protect-pass-spec.md)
- Plugin: [`../../README.md`](../../README.md) ·
  Router: [`../using-translation-toolkit`](../using-translation-toolkit) ·
  Layer 1: [`../translation-intake`](../translation-intake)
- Forward 系 skill: [`translation-i18n`](../translation-i18n) ·
  [`translation-doc`](../translation-doc) ·
  [`translation-creative`](../translation-creative)
