# think-orbit

> シングルユーザー向け思考・計画パートナー——議論を透明な思考の連鎖に変換する：ノードごとに1つの Markdown ファイル、陳腐化伝播を伴う仮定ファイル、静かな機械的ゲート、再生成される DAG ビュー。意思決定は終わり方の一つであり、唯一の終わり方ではない。

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

**バージョン**: 0.1.1
**所属**: [monkey-skills](https://github.com/kouko/monkey-skills)
**ライセンス**: MIT
**状態**: Part 1 — プレリリース。中核となる対話プロトコルはまだ実装されていません（Task 11 で完成予定）。

## 使い方

「一緒に考えて」「X を計画したい」「意思決定を手伝って」（または「help me think through X」「plan X」「help me decide X」）と伝えると、入口スキル `using-think-orbit` が `thinking-session` へ案内し、エージェントがいくつか質問をしながら会話の内容を Markdown ファイルに書き出し、いつでも読める DAG ビューを再生成します。結論が出ないまま未解決の問いや計画の骨子で終わる回も、完結した記録です。

## インストール

```bash
/plugin marketplace add kouko/monkey-skills
/plugin install think-orbit@monkey-skills
```

**必要環境**: PyYAML 入りの Python 3（`pip install pyyaml`）— ゲートと DAG のスクリプトがこれで動きます。
