# loom-code

> **一つの変更を計画からマージ済み PR まで運ぶ 5 つのステーションと、
> レビューが実際に行われていない push を拒む checker。** loom-code が
> 前提にするのは基本的なソフトウェア工学の知識であって、この plugin の
> 知識ではありません。1 変更につき質問は 3 つだけ、残りは自分で決めます。
> 品質の出どころは機械が機械を検査することだからです — 書く agent が
> レビューする agent になることは決してありません。

**状態**: v1.0.0 — skill 5 個。破壊的変更：1.0 以前の skill・agent・script は
リネームではなく削除されました。詳細は [CHANGELOG.md](CHANGELOG.md)。
**言語**: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)
**リポジトリ**: [`monkey-skills`](https://github.com/kouko/monkey-skills) の一部

---

## 5 つのステーション

| ステーション | 産出物 | 本文 |
|---|---|---|
| `write-plan` | `docs/loom/<change-id>/plan.md` — タスク DAG | [SKILL.md](skills/write-plan/SKILL.md) |
| `build` | コミット。1 タスク 1 コミット、各々 `Task: <id>` trailer 付き | [SKILL.md](skills/build/SKILL.md) |
| `review` | `docs/loom/<change-id>/review.json` — verdict・probe・finding | [SKILL.md](skills/review/SKILL.md) |
| `ship` | PR、memory trailer、マージ | [SKILL.md](skills/ship/SKILL.md) |
| `maintain` | アラートや障害から intent を起こす | [SKILL.md](skills/maintain/SKILL.md) |

やりたいことを言えば入口は `write-plan` です。`loom-design` を入れている
場合は上流に `capture-intent` と `write-spec` が付き、入れていない場合は
`write-plan` が両方の役目を自分でこなします。

## 訊かれる 3 つの質問

これ以外はすべて理由を記録した上で自動的に決まります。

1. **これがやりたいことですか？** — コードが存在する前に、意図を平易な
   言葉で言い直したもの。
2. **X と打つと Y が見える。合っていますか？** — 目に見える振る舞い。
   product の変更でのみ訊かれ、engineering では訊かれません。
3. **できましたか？** — その変更に一切触れていない agent が書いた
   盲検レポートを読みます。diff は読みません。

不可逆な分岐（データの削除、公開インターフェース、片道のマイグレーション）
は ① か ② の開いている方に、結果の形で足されます。

## contract package

`contract/manifest.yaml` がステーション、アクション、そして 4 つの
artifact（intent・spec・plan・review）の全フィールドを宣言します。
`loom-design` はこれを読み `requires-contract` を宣言します。
`loom-workflow` はそうではなく——配信（delivery）の前に `decision-map`
skill だけが `contract --require` を実行します。書き込むのは loom-code
のみ。空のひな型は `contract/templates/` にあります。

## checker

`scripts/loom_checker.py` が決定的な層のすべてです — ルール 20 個、
`--list-rules` で一覧できます。SessionStart hook と
`git push` / `gh pr create` / `gh pr merge` の前に走り、宣言を信じずに
再計算します：package テストと敵対 probe を自分で走らせ直し、終了コードを
見ます。防げるのは手滑りであって、本気の不正ではありません。

## インストール

### Claude Code

```bash
claude plugin marketplace add https://github.com/kouko/monkey-skills.git
claude plugin install loom-code@monkey-skills
claude plugin list | grep loom-code       # 期待値: enabled
```

`loom-design` と `loom-workflow` も同じ手順で入ります。3 つは独立して
インストール可能で、loom-code はどちらも必要としません。任意の受け渡し先が
不在のときは、そのステップを理由付きで N/A と報告し、自分の契約が許す範囲で
続行します。接続点は `loom-design:write-spec` のような plugin 名付き skill 名、
contract package、そしてプロジェクト自身の `docs/loom/` 成果物だけで、
他 plugin の `hooks/`・`skills/`・`scripts/` を直接読むことはありません。

### Codex CLI

Codex には plugin マーケットプレースがないため、checker をリポジトリ内に
複製します：

```bash
python3 scripts/codex_scaffold.py --probe
```

`.codex/hooks.json` とバージョン刻印付きの checker のコピーを書き、偽の
push を撃ち込みます。ブロックされなければ exit 2 で「Codex で `/hooks` を
実行してください」と表示します — 未信頼の hook は黙って飛ばされ、それは
検査に通った状態と見分けがつかないからです。

## ライセンス

MIT（`monkey-skills` の一部として）。
