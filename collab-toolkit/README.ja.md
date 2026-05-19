# collab-toolkit

> 各サービスの公式 MCP サーバー / CLI で駆動する read-only オフィスコラボツールキット — 5 スキル。
> Asana / Slack / Notion / Gmail / Google Calendar。

[![Language: English](https://img.shields.io/badge/lang-EN-blue)](README.md) [![日本語](https://img.shields.io/badge/lang-JA-blue)](README.ja.md) [![繁體中文](https://img.shields.io/badge/lang-zh--TW-blue)](README.zh-TW.md)

## 機能

日常的に使っているオフィス協働サービス — Asana、Slack、Notion、Gmail、Google Calendar — に Claude Code を接続し、以下を提供します：

- **状態の可視化**：会社の状況、進行中の作業、チームの動き
- **横断検索**：Claude Code 経由で社内データへの自然言語検索
- **read-only 憲章**：書き込み・破壊的操作なし — v0.1.x の non-goal を v0.2.0 でもそのまま踏襲

v0.2.0 は各サービスを**公式チャネル**で駆動します — 5 サービス全てで vendor 側の MCP / CLI 対応が成熟したため、v0.1.x のブラウザ snapshot スタックを完全に廃止しました。

## クイックスタート

```bash
# Claude Code marketplace 経由で plugin をインストール
/plugin install collab-toolkit

# 初回セットアップ
/collab-setup
```

`/collab-setup` の流れ：`gws` CLI のインストール（Homebrew 推奨、npm fallback）→ Google OAuth 1 回（Gmail + GCal を同時にカバー）→ Asana / Slack / Notion を `/mcp add`。5 サービスで OAuth は計 4 回。

セットアップ後は、Claude に次のような質問ができます：
- "今週締め切りの Asana タスクを一覧表示して"
- "5月1日以降の #engineering チャンネルで OKR に関する Slack メッセージを検索して"
- "今日の Google Calendar の予定を教えて"
- "来週の火曜 10am〜4pm の間で 30 分の空きスロットを探して"

## 対応サービス

| Service | チャネル | セットアップ手順 |
|---|---|---|
| Asana  | 公式 MCP V2 (`mcp.asana.com/v2/mcp`)         | `/mcp add asana` — Claude Code native OAuth pre-registration |
| Slack  | 公式 MCP（2026-02 GA）                       | `/mcp add slack` |
| Notion | 公式リモート MCP (`mcp.notion.com/mcp`)      | `/mcp add notion` |
| Gmail  | Google Workspace CLI (`gws`)                 | `gws auth`（GCal と OAuth 共有） |
| GCal   | Google Workspace CLI (`gws`、同じバイナリ)   | （Gmail と同じ OAuth） |

## スキル

| Skill | 主要 protocol |
|---|---|
| `asana-automate`  | task-list, task-detail, project-overview, search-global |
| `slack-automate`  | search-messages, channel-read, thread-read, find-user |
| `notion-automate` | search-workspace, page-fetch, database-query |
| `gcal-automate`   | agenda-view, event-search, find-free-slots, shared-calendar-read |
| `gmail-automate`  | mail-search, thread-read, inbox-summary, label-read |

> Notion `page-backlinks` は v0.2.0 で廃止 — Notion API に backlinks エンドポイントが存在せず、v0.1.6 の UI スクレイピング回避策は公式 MCP に移植できないため。詳細は `CHANGELOG.md` §Notes を参照。

## 注意事項

- ⚠️ **Cowork sandbox 非対応** — ローカルでの `gws` バイナリインストールと、sandbox では露出しないサービスごとの `/mcp add` OAuth フローが必要なため
- **read-only 憲章**：書き込み操作は導入しません — v0.1.x の non-goal を踏襲
- **個人 Google アカウント**：OAuth 同意画面は未検証アプリに対して 25 scope の上限を強制します — 上限に達したら Cloud Console で不要 API を整理してください

## トラブルシューティング

| 症状 | 対処 |
|---|---|
| `gws: command not found` | `brew install gws`（または npm fallback）を再実行；`PATH` に brew prefix（`brew --prefix`/bin）が含まれているか確認 |
| `gws auth` → `connection refused` | ブラウザフロー timeout — `gws auth` を再実行し、consent 画面を素早くクリックスルー（idempotent） |
| `OAuth scope exceeded 25` | 個人 Google アカウントの未検証アプリ上限 — Cloud Console で不要 API を整理 |
| `/mcp add` 失敗 | Claude Code を更新 — native OAuth pre-registration は 2026 年後半に登場、旧ビルドにはワンクリックフローがありません |
| `GOOGLE_CLOUD_PROJECT not set` | shell rc で env var を export し reload — `/collab-setup` Step 2 を参照 |

## v0.1.x からの移行

v0.1.x は `~/.local/share/` と `~/.config/collab-toolkit/` 配下のブラウザ自動化スタックに依存していました。v0.2.0 ではいずれも参照されません。具体的な `rm -rf` クリーンアップコマンドと、オプションのパッケージアンインストール手順は `CHANGELOG.md` §Migration block を参照してください。

## 開発

```bash
# 構造チェック（リポジトリルートから実行）
python scripts/check-skill-structure.py
```

## アーキテクチャ

v0.2.0 移行 brief：`docs/collab-toolkit/specs/2026-05-19-v0.2.0-migration.md`。
