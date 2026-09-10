# loom-memory

> **OKF v0.2 互換のストア形式を持つ、オプションかつ受動的にのみ発火する
> リポジトリ記憶capability。** 単体でインストール・単体で動作し —
> `loom-code`・`loom-design`・`loom-workflow` のいずれにも依存しない。
> これらのどれか、あるいはどれも入れていないユーザーでも、同じ公開
> skill を呼び出せる。

**Status**: v0.1.0 — 現時点ではスキャフォールドのみ。skill・ストア
バリデータ・移行ツールはまだ未実装。実装後は [CHANGELOG.md](CHANGELOG.md)
を参照。
**Languages**: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)
**Repository**: [`monkey-skills`](https://github.com/kouko/monkey-skills) の一部

---

## これは何か

リポジトリの知識 — 学んだ教訓、ハマった落とし穴、再び学び直す価値のない
決定 — はどの変更よりも長く生きる。loom-memory はその知識が住む場所だ。
Open Knowledge Format（OKF）v0.2 プロファイルに準拠した Markdown 文書の
ストアと、そこに対して recall（想起）・record（記録）・reconcile（照合）・
retire（廃止）を行う 1 つの公開 skill からなる。

この capability は受動的だ：ユーザーが明示的にリポジトリの知識を思い出す・
記録する・照合する・廃止するよう頼んだとき、または agent 自身が過去の
リポジトリ経験への具体的な必要性を判断したときにのみ動作する。どの Loom
ステーションも、そこに到達しただけで呼び出すことはない。存在しなくても
`loom-code`・`loom-design`・その他の利用側を止めることはない — ストアが
無い、または recall 結果が空なのは正常な「記憶なし」結果であり、失敗
ではない。

## 単体でインストール可能

loom-memory は自分自身の plugin として配布される。skill・ストアテンプレート・
バリデータはすべてこの plugin ディレクトリ内に収まっており、manifest は
`loom-code`・`loom-design`・`loom-workflow` への必須依存を一切宣言しない —
`loom-design` と違い、姉妹 plugin の contract package を読むこともない。
`loom-code` と `loom-design` も同様にこれへの依存を宣言しない：
plugin 同士は plugin 名付き skill 名とプロジェクト自身のファイルだけで
繋がり、他 plugin の `hooks/`・`skills/`・`scripts/` を直接触ることは
絶対にない。

## OKF v0.2 互換ストア

この plugin が管理するストアは OKF v0.2 に準拠する：非予約の Markdown
文書はすべて解析可能な YAML frontmatter を持ち `type` は非空、存在する
予約ファイル `index.md` と `log.md` はそれぞれの予約構造に従う。この
互換性により、OKF プロファイルを理解する任意のツールがこのストアを
読み書き・検証できる — この plugin に限らない。

## インストール

### Claude Code

```bash
claude plugin marketplace add https://github.com/kouko/monkey-skills.git
claude plugin install loom-memory@monkey-skills
claude plugin list | grep loom-memory     # enabled と出れば OK
```

loom-memory は単体でインストールし、単体で動く。`loom-code` と
`loom-design` は決して必須ではない — plugin 名付き skill 名と、
プロジェクト自身の `docs/loom/`（または相当のもの）を通じてのみ繋がる。

### Codex CLI

同じ手順で Codex plugin をインストールする。専用の
`.codex-plugin/plugin.json` を同梱している。

## ライセンス

MIT（`monkey-skills` の一部として）。
