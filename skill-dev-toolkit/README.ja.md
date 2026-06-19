# skill-dev-toolkit

Claude Agent Skill を端から端まで作るための **自己完結型** ツールキット。
クロスプラグイン依存ゼロ — 単独でインストールして動きます。

skill オーサリングのライフサイクルを dev-workflow から独立して配布できるよう、
`dev-workflow` から切り出しました（2026-06-20）。

## スキル（ライフサイクル）

| スキル | 役割 |
|---|---|
| `skill-creator-advance` | 新規 skill 作成・大規模再設計・評価駆動開発・description の発火最適化。 |
| `skill-judge` | skill の設計品質を 8 次元ルーブリックで採点（0–120 + グレード）。 |
| `dogfood-skill-testing` | 草案 SKILL.md の盲目的な挙動テスト — 期待通り発火するか、ワークフローが契約を満たすか。 |
| `skill-refactor` | 出力挙動を保ったままの token / 構造リファクタ。 |
| `skill-tuning` | skill 出力品質の A/B — 人間判定でバリアント選択。 |

典型フロー: **作成** → **採点 / 挙動テスト** → **リファクタ / 出力チューニング**。

## 自己完結

各 skill は worth-it / 最小 skill チェックを内蔵し、他プラグインに委譲しません。
よって **他プラグインへの `plugin:skill` 参照はゼロ**。（汎用のコード変更クリティーク
`complexity-critique` / `proposal-critique` と、セッションログ採掘 `distill-sessions`
は `dev-workflow` に残ります。本ツールキットはそれらに依存しません。）

## ライセンス

MIT — リポジトリ直下の `LICENSE` を参照。
