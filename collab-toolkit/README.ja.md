# collab-toolkit

> **non-Google** サービス（Asana / Slack / Notion）向け read-only オフィスコラボツールキット — 各サービスの公式 MCP サーバーで駆動。
> Gmail / Google Calendar は [`gws-toolkit`](../gws-toolkit/) に移管（Phase 2+）。

[![Language: English](https://img.shields.io/badge/lang-EN-blue)](README.md) [![日本語](https://img.shields.io/badge/lang-JA-blue)](README.ja.md) [![繁體中文](https://img.shields.io/badge/lang-zh--TW-blue)](README.zh-TW.md)

## 機能

日常的に使う non-Google オフィス協働サービス — Asana、Slack、Notion — に Claude Code を接続し、以下を提供します：

- **状態の可視化**：会社の状況、進行中の作業、チームの動き
- **横断検索**：Claude Code 経由で社内データへの自然言語検索
- **read-only 憲章**：書き込み・破壊的操作なし — v0.1.x の non-goal を v0.2.0 でもそのまま踏襲

v0.2.0 は各サービスを**公式 MCP サーバー**で駆動します — 3 サービス全てで MCP 対応が成熟したため、v0.1.x のブラウザ snapshot スタックを完全に廃止しました。

## クイックスタート

```bash
# Claude Code marketplace 経由で plugin をインストール
/plugin install collab-toolkit

# 初回セットアップ
/collab-setup
```

3 つの MCP サーバー（Asana / Slack / Notion）は plugin の `mcpServers` ブロックで**自動登録**されます — 手動の `/mcp add` ステップは不要。OAuth は各サーバーへの初回ツール呼び出し時に発火します。

セットアップ後は、Claude に次のような質問ができます：
- "今週締め切りの Asana タスクを一覧表示して"
- "5月1日以降の #engineering チャンネルで OKR に関する Slack メッセージを検索して"
- "<トピック> に関する Notion ページを探して"

## 対応サービス

| Service | チャネル | 配線方式 |
|---|---|---|
| Asana  | 公式 MCP V2 (`mcp.asana.com/v2/mcp`)         | plugin の `mcpServers` で自動登録 |
| Slack  | 公式 MCP（2026-02 GA、`mcp.slack.com/mcp`） | 自動登録；OAuth scope はインライン宣言 |
| Notion | 公式リモート MCP (`mcp.notion.com/mcp`)      | plugin の `mcpServers` で自動登録 |

> Gmail と Google Calendar は v0.2.0 brief（5 サービス計画）に含まれていましたが、サイクル末で [`gws-toolkit`](../gws-toolkit/) へ移管する方向に転換しました — Google OAuth クライアントの一元化、既存の Slides/Docs/Sheets/Drive スキルとのバイナリ/scope 重複回避が理由です。詳細は `CHANGELOG.md` §"Late-pivot 2026-05-19" を参照。

## スキル

| Skill | 主要 protocol |
|---|---|
| `asana-automate`  | task-list, task-detail, project-overview, search-global |
| `slack-automate`  | search-messages, channel-read, thread-read, find-user |
| `notion-automate` | search-workspace, page-fetch, database-query |

> Notion `page-backlinks` は v0.2.0 で廃止 — Notion API に backlinks エンドポイントが存在せず、v0.1.6 の UI スクレイピング回避策は公式 MCP に移植できないため。詳細は `CHANGELOG.md` §Notes を参照。

## 注意事項

- ⚠️ **Cowork sandbox 非対応** — sandbox では露出しないサービスごとの `/mcp add` OAuth フローが必要なため
- **read-only 憲章**：書き込み操作は導入しません — v0.1.x の non-goal を踏襲

## トラブルシューティング

| 症状 | 対処 |
|---|---|
| `/mcp list` に MCP サーバーが表示されない | plugin がロードされていない — `/plugin list` で `collab-toolkit` のインストールを確認；必要なら Claude Code を再起動 |
| MCP ツールが "auth required" を返す | 初回 OAuth が未完了 — Claude Code が自動的に促すはず；されない場合は Claude Code を再起動 |
| Asana OAuth が `redirect_uri not registered` で失敗 | per-user `clientId` の escape hatch については `commands/collab-setup.md` §Troubleshooting を参照 |

## v0.1.x からの移行

v0.1.x は `~/.local/share/` と `~/.config/collab-toolkit/` 配下のブラウザ自動化スタックに依存していました。v0.2.0 ではいずれも参照されません。具体的な `rm -rf` クリーンアップコマンドと、オプションのパッケージアンインストール手順は `CHANGELOG.md` §Migration block を参照してください。

## 開発

```bash
# 構造チェック（リポジトリルートから実行）
python scripts/check-skill-structure.py collab-toolkit
```

## アーキテクチャ

v0.2.0 移行 brief：`docs/collab-toolkit/specs/2026-05-19-v0.2.0-migration.md`（当初 5 サービスでスコープ作成、サイクル末で 3 サービスに pivot — 詳細は `CHANGELOG.md` 参照）。
