# translation-intake

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> translation-toolkit の Layer 1 — 5 軸（mode / register / strategy / locale / domain）と skopos を明確化する。
> いずれかの翻訳 specialist が動き出す前に走る。

[translation-toolkit](../..) plugin の一部。Claude が読み込む operational
spec は [`SKILL.md`](SKILL.md)。本 README は人間向け。

## なぜ独立した intake skill か

4 つの format-specialist skill（`translation-i18n`、`translation-doc`、
`translation-creative`、`translation-audit`）はいずれも作業前に同じ 5 つの
パラメータを必要とする：**どの種類の翻訳か**、**どの程度フォーマルか**、
**どの程度文化的に適応させるか**、**どの locale 間か**、**どの domain か**。
デフォルト値をハードコードするのは、ユーザーが選んでいない判断を黙って
押し付けることになる — runbook なら `register=neutral` で問題ないが、
marketing tagline には不適切。`mode=literal` は使い物にならない ad copy を
生む。

intake はこれらの軸を一箇所で一度だけ捕捉し、downstream skill が結果を
読み取る。auto モードは source content から推論する。explicit モードは
auto が外したときや、source だけでは見えない強い意向がユーザーにあるときに、
各軸をユーザーに 1 つずつ確認する。

## 5 軸

| 軸 | 許容値 | 影響先 |
|---|---|---|
| `mode` | `literal` / `faithful` / `localized` / `transcreation` | Reflection 軸の数（4D vs 5D）と S1 gate threshold |
| `register` | `formal` / `neutral` / `warm` / `playful` | S2 register-preservation gate |
| `strategy` | `domestication` / `foreignization` | 文化参照の扱い；mode とは独立 |
| `locale` | BCP-47 source + target（例：`en-US` → `ja-JP`） | invocation 時に必須；自動推論しない |
| `domain` | 13 domain taxonomy から 1 つ以上（`general`、`ui`、`tech.software`、`tech.web`、`tech.data`、`tech.crypto`、`gov`、`legal`、`medical`、`finance`、`marketing`、`statistics`、`typography`） | glossary subset 選択 + critique フレーミング |

加えて **skopos / intent** — 「これを誰が読み、どんな action を取るべきか」
に答える自由形式の 1 行説明。

## 2 つの mode

| Mode | トリガー | 動作 |
|---|---|---|
| `auto`（デフォルト） | フラグなし | 単一の source-analysis 呼び出しで 5 軸すべてを推論。locale pair はユーザー指定のまま |
| `explicit`（`--explicit` / `-e`） | ユーザーフラグ | 各軸についてユーザーに確認。auto 推論結果はデフォルトとしてプロンプトに seed |

mode 別の pipeline と worked example は
[`protocols/intake-auto.md`](protocols/intake-auto.md) と
[`protocols/intake-explicit.md`](protocols/intake-explicit.md) を参照。

## 使うとき

- [`using-translation-toolkit`](../using-translation-toolkit) によって、
  入力に明確な軸シグナルがない（短い raw text、format / domain hint なし）
  ときに呼ばれる
- 4 つの active skill のいずれかで `--intake` を直接渡し、format-specialist
  が走る前に spec を検査 / ロックしたいとき
- 不満足な auto pass の後で `--explicit` を付けて再呼び出しし、1 つ以上の
  軸を対話的に上書きするとき

## 使わないとき

- ユーザーが既に完全な intake spec（5 軸 + locale pair + skopos）を渡して
  いる — intake はスキップし、format-specialist に直接渡す
- タスクが翻訳ではない — router の "When NOT to use" を参照（cross-plugin
  routing）

## 出力

pipeline の次の skill が消費する `intake-spec` を書き出す。スキーマ
（audit-trail の `intake` block のサブセット）：

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

`inferred` は軸ごと：`true` は auto 推論、`false` はユーザー指定。
`source_locale` と `target_locale` は常に implicitly `false`。
`inferred_values` は、`--explicit` で推論軸が上書きされたときに、
heuristic が *本来* 何を選んでいたかを記録する。

## この skill が **行わないこと**

- **翻訳しない。** intake は parameter 捕捉のみ。ここに source text を直接
  貼っても返るのは intake-spec で、決して翻訳ではない。
- **format ファイルを parse しない。** PO / JSON / XLIFF / Markdown AST
  parsing は各 format-specialist の Layer 2 の役目。
- **verification gate を走らせない。** M1 / M2 / S1 / S2 / I1 は Layer 4 で、
  format-specialist の所有。
- **下流 skill を呼び出さない。** チェイン呼び出しは harness が行う；
  intake は spec を発行するだけ。

## Audit-trail integration

intake の判断は `lib/audit_trail.AuditTrailBuilder` 経由で共有 audit
trail に流れる。`builder.set_intake(...)` および
`builder.add_inferred_value(...)` の呼び出しは [`SKILL.md`](SKILL.md)
§"Audit-trail integration" を、完全なスキーマは
`scripts/canonical/audit-trail-spec.md` を参照。

## Reference distribution note

`translation-intake` は `scripts/distribute.py` の `ACTIVE_SKILLS` リストに
意図的に **含まれない**。intake が必要とするのは 5 軸 taxonomy + auto-inference
heuristic（既に `protocols/intake-auto.md` に inline 済み）と、audit-trail
スキーマの intake-block subset（`SKILL.md` に inline 済み）のみ。完全な
canonical reference set をここに配信しても、無関係な prompt / gate ファイルを
7+ 増やすだけで behavioral gain がない。intake は copy を保持しないので
drift は起こり得ない。

## See also

- [`SKILL.md`](SKILL.md) — operational spec（5 軸表、出力スキーマ、
  audit-trail integration）
- [`protocols/intake-auto.md`](protocols/intake-auto.md) — auto モード pipeline
- [`protocols/intake-explicit.md`](protocols/intake-explicit.md) —
  explicit モードの interaction + サンプル transcript
- Plugin overview: [`../../README.md`](../../README.md)
- Router: [`../using-translation-toolkit`](../using-translation-toolkit)
- Downstream: [`translation-i18n`](../translation-i18n) ·
  [`translation-doc`](../translation-doc) ·
  [`translation-creative`](../translation-creative) ·
  [`translation-audit`](../translation-audit)
- Canonical sources: `../../scripts/canonical/orthogonal-axes.md` ·
  `../../scripts/canonical/audit-trail-spec.md`
