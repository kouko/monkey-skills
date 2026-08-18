# strategy-dag

> シングルユーザー向け意思決定支援エージェント——議論を透明な思考の連鎖に変換する：ノードごとに1つの Markdown ファイル、陳腐化伝播を伴う仮定ファイル、静かな機械的ゲート、再生成される DAG ビュー。

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

**バージョン**: 0.1.0
**所属**: [monkey-skills](https://github.com/kouko/monkey-skills)
**ライセンス**: MIT
**状態**: Part 1 — プレリリース。中核となる対話プロトコルはまだ実装されていません（Task 11 で完成予定）。

## 使い方

「意思決定を手伝って」（または「help me decide X」）と伝えると、エージェントがいくつか質問をしながら会話の内容を Markdown ファイルに書き出し、いつでも読める DAG ビューを再生成します。

## インストール

```bash
/plugin marketplace add kouko/monkey-skills
/plugin install strategy-dag@monkey-skills
```
