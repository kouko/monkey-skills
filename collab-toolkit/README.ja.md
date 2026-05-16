# collab-toolkit

> [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) をラップしたブラウザ自動化ツールキット。
> 職場情報収集（workplace intelligence）向け read-only 5 skill。

[![Language: English](https://img.shields.io/badge/lang-EN-blue)](README.md) [![日本語](https://img.shields.io/badge/lang-JA-blue)](README.ja.md) [![繁體中文](https://img.shields.io/badge/lang-zh--TW-blue)](README.zh-TW.md)

## 機能

日常的に使っているオフィス協働サービス — Asana、Slack、Notion、Google Calendar、Gmail — に接続し、以下を提供します：

- **状態の可視化**：会社の状況、進行中の作業、チームの動き
- **横断検索**：Claude Code 経由で社内データへの自然言語検索
- **バックグラウンド動作**：初回ログイン後はヘッドレスで動作し、作業中も並行して稼働

agent-browser のセマンティックファーストな snapshot モデルを基盤としており、脆弱な CSS セレクターも API token も不要で、既存の Chrome ログイン状態をそのまま利用します。

## クイックスタート

```bash
# Claude Code marketplace 経由で plugin をインストール
/plugin install collab-toolkit

# 初回セットアップ（macOS では Homebrew 推奨）
/collab-setup
```

以上です。`/collab-setup` が自動で行う処理：
1. `agent-browser` のインストール（macOS では brew、fallback は npm）
2. Chrome for Testing のダウンロード
3. `~/.local/bin/abx` ラッパーのインストール
4. Chrome profile の検出と設定の書き込み
5. 5 サービス全てのログイン状態の確認

セットアップ後は、Claude に次のような質問ができます：
- "今週締め切りの Asana タスクを一覧表示して"
- "5月1日以降の #engineering チャンネルで OKR に関する Slack メッセージを検索して"
- "今日の Google Calendar の予定を教えて"
- "来週の火曜 10am〜4pm の間で 30 分の空きスロットを探して"

## プロファイルモード

| モード | 内容 | 用途 |
|---|---|---|
| **Dedicated**（デフォルト・v0.1.2 以降） | `~/.local/share/collab-toolkit/profiles/dedicated/` の単一統合プロファイル。Google SSO がサービス間でカスケード → 5 サービス全部で通常 2-3 回のログインで完了。セットアップは Claude 主導（AskUserQuestion 経由、ターミナル操作不要）。 | **デフォルト — オフィスコラボ用途で推奨。** マルチプロファイル・マルチアカウント・SSO リフレッシュなどの環境でも安定動作。日常 Chrome の状態から独立。 |
| **Shared**（`--shared`、オプトイン） | `--profile <name>` で日常使い Chrome のログイン状態を再利用 | ⚠️ Shared には実環境での失敗モードあり：Chrome 起動中は cookies が転送できない（profile lock）、macOS Keychain の手動許可が必要な場合あり、Chrome に複数 profile があると「正しい」profile を選ぶ必要、SSO リフレッシュ系サービスは headless で動かないことあり、verify が marketing リダイレクトを誤検出。**Chrome profile が 1 つ・5 サービス全部が同じ Google アカウント・SSO リフレッシュなし、の単純な構成のときのみ推奨。** |

いつでも切り替え可能：`/collab-setup --switch-mode`（v0.1.2 以降は双方向 toggle）。

## スキル

| Skill | 主要 protocol |
|---|---|
| `asana-automate` | task-list, task-detail, project-overview, search-global |
| `slack-automate` | search-messages, channel-read, thread-read, find-user |
| `notion-automate` | search-workspace, page-fetch, database-query, page-backlinks |
| `gcal-automate` | agenda-view, event-search, find-free-slots, shared-calendar-read |
| `gmail-automate` | mail-search, thread-read, inbox-summary, label-read |

## 注意事項

- ⚠️ **Cowork sandbox 非対応** — ローカルの Chrome / OS アクセスが必要です
- ⚠️ **CI / スケジュール実行は v0.1.0 では非対応**（shared モードはローカル専用；dedicated モードのポータビリティは v0.2.0+ に延期）
- **プライバシーの範囲**：shared モードでは、agent-browser は 5 サービスだけでなく Chrome の全 cookie にアクセスします。信頼はローカル Rust バイナリとオープンソースによって担保されています。
- **ログイン状態への依存**：shared モードでは、日常使い Chrome でサービスからログアウトすると、再ログインするまで自動化が機能しなくなります。

## トラブルシューティング

| 症状 | 対処 |
|---|---|
| `ERR: config not found` | `/collab-setup` を実行 |
| `⚠️ ~/.local/bin not on PATH` | シェルの rc ファイルに `export PATH="$HOME/.local/bin:$PATH"` を追加 |
| `ERR: UI changed` | 対象 skill の `references/ui-patterns.md` を開き、re-snapshot して更新 |
| `Login wall detected` | Shared モード: Chrome からログイン。Dedicated モード: `/collab-setup --reauth <service>` |

## 開発

```bash
# ユニットテスト（bats）
cd collab-toolkit && bats scripts/tests/

# 構造チェック（リポジトリルートから実行）
python scripts/check-skill-structure.py
```

## アーキテクチャ

完全な設計仕様は `docs/superpowers/specs/2026-05-15-collab-toolkit-v0.1.0-design.md` を参照してください。
