# salesforce-toolkit

> read-only Salesforce ツールキット — 公式 Salesforce DX MCP サーバー（[`salesforcecli/mcp`](https://github.com/salesforcecli/mcp)、Apache-2.0）を介して、自然言語の SOQL / SOSL クエリと Report / Dashboard 分析を組織（org）に対して実行。

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> ⚠️ **Cowork 非対応 — Claude Code CLI / Code タブ専用。** 初回セットアップは `sf org login web` を実行し、これは TTY 必須のブラウザ OAuth フローです。Claude Desktop の Cowork sandbox はそのパスを露出しません（[`gws-toolkit`](../gws-toolkit/) や [`collab-toolkit`](../collab-toolkit/) と同じ制約）。Cowork を使っている場合は Claude Code CLI または Claude Desktop の Code タブに切り替えてください。

## 機能

Claude Code を Salesforce org に接続し、以下を自然言語で問い合わせ可能にします：

- **データクエリ** — 自然言語の SOQL / SOSL：オブジェクト一覧、レコード取得、フィルタリング、集計、親子関係の traverse
- **Reports & Dashboards** — フォルダ一覧、metadata 取得、Report 実行、行データ取得、Dashboard ウィジェットの snapshot、トレンド / Top-N / ファネル分析
- **read-only 憲章** — `data,metadata` MCP toolset のみ。Apex deploy、metadata push、ユーザー CRUD は v0.2+ で破壊的操作の safety wrapper が入るまで非対応

v0.1.0 は upstream の Salesforce DX MCP サーバー（[`salesforcecli/mcp`](https://github.com/salesforcecli/mcp)、Apache-2.0、2026 GA）をラップします — ベンダー保守の schema-aware なツール群で、サードパーティ製クエリ DSL の drift はありません。

## クイックスタート

```bash
# Claude Code marketplace 経由で plugin をインストール
/plugin install salesforce-toolkit

# 初回ブートストラップ（~3-5 分 — ほとんどはブラウザ OAuth フローの時間）
/salesforce-toolkit:sf-setup
```

`sf-setup` は 6 ステップの idempotent インストーラ：macOS / TTY ガード → Homebrew 確保 → `brew install sf` → `brew install salesforce-mcp` → 3 層 alias 推論つき `sf org login web` → `sf org display` で検証。既にセットアップ済みなら再実行は ~5 秒で、完了済みステップはスキップされます。

セットアップ後は Claude に次のように尋ねられます：

- 「直近の Opportunity で $50K 超のものを 10 件出して」
- 「EMEA チームの stage 別 pipeline を見せて」
- 「Weekly Revenue Dashboard を取得して、上位の動きを要約して」

## スキル

| Skill | 用途 |
|---|---|
| [`sf-query`](skills/sf-query/) | 自然言語の SOQL / SOSL — オブジェクト一覧、レコード取得、フィルタリング、集計、親子関係の traverse |
| [`sf-report`](skills/sf-report/) | Salesforce Reports + Dashboards — フォルダ一覧、metadata 取得、Report 実行、行データ取得、ウィジェットの snapshot、トレンド / Top-N / ファネル分析 |

両 skill とも read-only です。書き込み toolset（`users` / `code-analyzer` / Apex deploy）は v0.2+ に延期され、その時点でもユーザーが明示的に書き込みを要求する文言を入力しないと走りません。

## ツール構成

| Component | Source | 役割 |
|---|---|---|
| [`sf` CLI](https://developer.salesforce.com/tools/salesforcecli) | `brew install sf` | Salesforce DX CLI — OAuth（`sf org login web`）、org / alias 管理、token キャッシュを提供 |
| [`salesforce-mcp`](https://github.com/salesforcecli/mcp) | `brew install salesforce-mcp`（Apache-2.0） | 60+ の Salesforce ツール（data / metadata / orgs / users / code-analyzer）を公開する MCP サーバー。v0.1.0 は `data,metadata` toolset のみ有効化 |
| [`bin/sf-mcp-launcher.sh`](bin/sf-mcp-launcher.sh) | plugin 同梱 shim | Launcher：brew バイナリを優先、無ければ `npx -y @salesforce/mcp` にフォールバック。どちらも無い場合は `sf-setup` への案内を出力 |
| Homebrew | https://brew.sh | macOS パッケージマネージャ — `sf-setup` が y/N 確認つきで自動インストール |
| Node ≥ 26（推移的依存） | Homebrew 依存 | `salesforce-mcp` サーバーの実行環境 |

`sf-setup` がこの 4 つのインストール対象を一括 orchestrate します。Launcher shim のおかげで brew が無い状態でも `.mcp.json` はロード可能 — 初回の MCP ツール呼び出し時に `npx` 経由でサーバーが起動します。

## 前提条件

| 項目 | 要件 |
|---|---|
| OS | macOS 14+（darwin-arm64 / darwin-x86_64）。Linux / WSL は Phase 2+。 |
| Shell | zsh または bash（macOS デフォルトの zsh で問題なし） |
| Terminal | 本物の TTY（Terminal.app / iTerm2 / VS Code 統合ターミナル）— OAuth 確認プロンプトに必須 |
| Browser | Chrome または Safari（`sf org login web` で 1 回だけ必要） |
| Salesforce org | ブラウザ OAuth でログインできる Production、Sandbox、Scratch、Developer Edition org。非 Production org の場合は `sf-setup` に `--instance-url=` を渡してください。 |

**不要なもの**：Python、uv、gcloud、独自の Connected App。v0.1.0 は `sf` CLI に同梱のパブリック OAuth client を使用します。

## token 期限切れ時の再認証

Salesforce DX OAuth の refresh token は org ポリシー依存の有効期限を持ちます（Sandbox は数時間〜数日、Production はもっと長い）。期限切れになると Claude Code が「MCP サーバーが org に到達できない」と返してきます。インストーラ全体を再実行せずに再認証するには：

```bash
bash scripts/sf/refresh-auth.sh
```

または、同等の `/salesforce-toolkit:sf-setup --force-reauth`。どちらも brew ステップはスキップし、既存 alias に対して `sf org login web` のみ再実行します。

## トラブルシューティング

大半の症状は [`commands/sf-setup.md`](commands/sf-setup.md) §Troubleshooting に網羅されています（TTY ガード / 非対応 OS / brew インストール失敗 / OAuth フローのキャンセル / verify 空 / 排他フラグ）。より深い状態調査には、副作用なしで現在の `sf` + brew + MCP 状態をダンプする `bash scripts/sf/credential-check.sh --json` を実行してください。

## アーキテクチャ

```
┌──────────────────────────────────────────────────────────────┐
│  Claude Code (CLI / Code タブ)                               │
│                                                              │
│  ┌─────────────┐         ┌─────────────┐                     │
│  │  sf-query   │         │  sf-report  │                     │
│  │  (SKILL.md) │         │  (SKILL.md) │                     │
│  └──────┬──────┘         └──────┬──────┘                     │
│         │                       │                            │
│         └───────────┬───────────┘                            │
│                     ▼                                        │
│        mcp__salesforce__*  (60+ tools, data + metadata)      │
└─────────────────────┬────────────────────────────────────────┘
                      │  stdio MCP transport
                      ▼
        bin/sf-mcp-launcher.sh   (brew → npx fallback)
                      │
                      ▼
        salesforce-mcp  (Apache-2.0, salesforcecli/mcp)
                      │
                      ▼
                  sf CLI  (sf org login web の OAuth token)
                      │
                      ▼
              Salesforce org REST API
```

セットアップ時間（1 回限り）：`/salesforce-toolkit:sf-setup` がユーザーのターミナルで 6 ステップのインストーラを実行。実行時：Claude Code が `.mcp.json` をロード → launcher shim を spawn → stdio 経由で `salesforce-mcp` を spawn → 2 つの skill から MCP ツールが利用可能になる。

## リンク

- [PRODUCT-SPEC.md](PRODUCT-SPEC.md) — プロダクトの方向性、Users、JTBD、Scope、Non-goals、競合ポジショニング、KR ターゲット
- [TECH-SPEC.md](TECH-SPEC.md) — モジュール設計、`.mcp.json` 形状、shell script 契約、alias 推論、セキュリティ
- [CHANGELOG.md](CHANGELOG.md) — バージョン履歴
- [`commands/sf-setup.md`](commands/sf-setup.md) — `/salesforce-toolkit:sf-setup` コマンドリファレンス + トラブルシューティング
- 親 repository：[`monkey-skills`](https://github.com/kouko/monkey-skills)

## 関連

- [`gws-toolkit`](../gws-toolkit/) — Google Workspace（Slides / Docs / Sheets / Drive）ツールキット。同じく Cowork 非対応（TTY 必須 OAuth）
- [`collab-toolkit`](../collab-toolkit/) — Asana / Slack / Notion を各サービスの公式 MCP サーバー経由で利用。同じ read-only 憲章
- [Salesforce DX MCP](https://github.com/salesforcecli/mcp) — この plugin がラップする upstream MCP サーバー（Apache-2.0）
- [Salesforce CLI ドキュメント](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/cli_reference_unified.htm) — `sf` コマンドリファレンス

## ライセンス

MIT — [LICENSE-MIT.txt](LICENSE-MIT.txt) を参照。
