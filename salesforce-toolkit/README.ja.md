# salesforce-toolkit

> read-only Salesforce ツールキット — 公式 Salesforce DX MCP サーバー（[`salesforcecli/mcp`](https://github.com/salesforcecli/mcp)、Apache-2.0）を介して、自然言語の SOQL クエリを組織（org）に対して実行。

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> ⚠️ **Cowork 非対応 — Claude Code CLI / Code タブ専用。** 初回セットアップは `sf org login web` を実行し、これは TTY 必須のブラウザ OAuth フローです。Claude Desktop の Cowork sandbox はそのパスを露出しません（[`gws-toolkit`](../gws-toolkit/) や [`collab-toolkit`](../collab-toolkit/) と同じ制約）。Cowork を使っている場合は Claude Code CLI または Claude Desktop の Code タブに切り替えてください。

## 機能

Claude Code を Salesforce org に接続し、以下を自然言語で問い合わせ可能にします：

- **SOQL クエリ** — upstream の `run_soql_query` MCP tool を介した自然言語 SOQL：オブジェクト一覧、レコード取得、フィルタリング、集計、親子関係の traverse
- **真の read-only** — `data` MCP toolset のみ（唯一の tool：`run_soql_query`）。Apex deploy、metadata push、ユーザー CRUD はなし。`metadata` toolset は `deploy_metadata`（org への書き込み）を含むため意図的に **無効化**

v0.1.1 は upstream の Salesforce DX MCP サーバー（[`salesforcecli/mcp`](https://github.com/salesforcecli/mcp)、Apache-2.0、2026 GA）をラップします — ベンダー保守の schema-aware なツール群で、サードパーティ製クエリ DSL の drift はありません。Salesforce Report / Dashboard tools は現時点で upstream MCP に存在しないため、Phase 2+（upstream が公開した場合）に持ち越し。

## クイックスタート

```bash
# 0. 初回のみ：Homebrew をインストール（未インストールの場合）。
#    Terminal.app で 1 回だけ実行し、Claude Code を再起動：
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**推奨（ワンショット — org URL がわかっている場合）** — 単一コマンド、AskUserQuestion プロンプトなし：

```
# Claude Code 内で：
1. /plugin install salesforce-toolkit
2. /salesforce-toolkit:sf-setup --instance-url=https://YOUR-ORG.my.salesforce.com --no-prompt
3. /reload-plugins
```

**代替（対話モード — Claude にガイドさせる）** — 同じ end state、AskUserQuestion 2 回（instance ピッカー + alias 確認）で約 20 秒長くなる：

```
1. /plugin install salesforce-toolkit
2. /salesforce-toolkit:sf-setup
3. /reload-plugins
```

`/sf-setup` はこの会話の中で完結します：Claude が `credential-check.sh` で状態を確認 → **両方未インストールなら `brew install sf salesforce-mcp` をまとめて実行**（v0.1.1+、brew 起動 1 回分省略 + formula 並列ダウンロード）→ instance URL と alias を必要なら question UI で確認 → `sf org login web` をバックグラウンドで起動 → 30 秒ごとに **進捗を明示的に emit しながらポーリング**（沈黙時間を排除）→ `/reload-plugins` を案内。所要時間：~3-5 分（大半はブラウザでの OAuth 承認）。再実行は ~5 秒（各 step が状態を確認、完了済みは skip）。

> **brew だけが唯一の外部の 1 回限り step です。** brew installer 自体は `sudo` を呼ぶため Claude Code の Bash tool からは動きません — それが Step 0 を残している理由。brew が入った後はすべて会話内で完結します。

> Power-user パス：自分の terminal から `bash $CLAUDE_PLUGIN_ROOT/scripts/sf/auto-setup.sh` を実行すれば、TTY prompt 付きで同じ end-to-end install が走ります。両パスは同じ end state に収束。

セットアップ後は Claude に次のように尋ねられます：

- 「直近の Opportunity で $50K 超のものを 10 件出して」
- 「EMEA チームの stage 別 pipeline を見せて」
- 「今 quarter の Case を Status 別に count して」

## スキル

| Skill | 用途 |
|---|---|
| [`sf-query`](skills/sf-query/) | 自然言語の SOQL — オブジェクト一覧、レコード取得、フィルタリング、集計、親子関係の traverse（upstream の `run_soql_query` MCP tool 経由） |

設計上 read-only。書き込み toolset（`metadata` / `users` / `code-analyzer` / Apex deploy）は v0.2+ に延期され、その時点でもユーザーが明示的に書き込みを要求する文言を入力しないと走りません。

## ツール構成

| Component | Source | 役割 |
|---|---|---|
| [`sf` CLI](https://developer.salesforce.com/tools/salesforcecli) | `brew install sf` | Salesforce DX CLI — OAuth（`sf org login web`）、org / alias 管理、token キャッシュを提供 |
| [`salesforce-mcp`](https://github.com/salesforcecli/mcp) | `brew install salesforce-mcp`（Apache-2.0） | Salesforce tools（data / metadata / orgs / users / code-analyzer toolsets）を公開する MCP サーバー。v0.1.1 は真の read-only surface のため `data` toolset のみ有効化（唯一の tool：`run_soql_query`）。brew formula 名は `salesforce-mcp` ですが、install されるバイナリ名は `sf-mcp-server`（npm パッケージ `@salesforce/mcp` も同じバイナリを ship） |
| [`bin/sf-mcp-launcher.sh`](bin/sf-mcp-launcher.sh) | plugin 同梱 shim | Launcher：PATH 上の `sf-mcp-server` バイナリを優先、無ければ `npx -y @salesforce/mcp` にフォールバック。どちらも無い場合は `sf-setup` への案内を出力 |
| Homebrew | https://brew.sh | macOS パッケージマネージャ — `sf-setup` が y/N 確認つきで自動インストール |
| Node ≥ 26（推移的依存） | Homebrew 依存 | `sf-mcp-server` バイナリの実行環境 |

`sf-setup` がこの 4 つのインストール対象を一括 orchestrate します。Launcher shim のおかげで brew が無い状態でも `.mcp.json` はロード可能 — 初回の MCP ツール呼び出し時に `npx` 経由でサーバーが起動します。

## 前提条件

| 項目 | 要件 |
|---|---|
| OS | macOS 14+（darwin-arm64 / darwin-x86_64）。Linux / WSL は Phase 2+。 |
| Shell | zsh または bash（macOS デフォルトの zsh で問題なし） |
| Terminal | 本物の TTY（Terminal.app / iTerm2 / VS Code 統合ターミナル）— OAuth 確認プロンプトに必須 |
| Browser | Chrome または Safari（`sf org login web` で 1 回だけ必要） |
| Salesforce org | ブラウザ OAuth でログインできる Production、Sandbox、Scratch、Developer Edition org。非 Production org の場合は `sf-setup` に `--instance-url=` を渡してください。 |

**不要なもの**：Python、uv、gcloud、独自の Connected App。v0.1.1 は `sf` CLI に同梱のパブリック OAuth client を使用します。

## token 期限切れ時の再認証

Salesforce DX OAuth の refresh token は org ポリシー依存の有効期限を持ちます（Sandbox は数時間〜数日、Production はもっと長い）。期限切れになると Claude Code が「MCP サーバーが org に到達できない」と返してきます。インストーラ全体を再実行せずに再認証するには：

```bash
bash scripts/sf/refresh-auth.sh
```

または、同等の `/salesforce-toolkit:sf-setup --force-reauth`。どちらも brew ステップはスキップし、既存 alias に対して `sf org login web` のみ再実行します。

## トラブルシューティング

大半の症状は [`commands/sf-setup.md`](commands/sf-setup.md) §Troubleshooting に網羅されています（TTY ガード / 非対応 OS / brew インストール失敗 / OAuth フローのキャンセル / verify 空 / 排他フラグ）。より深い状態調査には、副作用なしで現在の `sf` + brew + MCP 状態をダンプする `bash scripts/sf/credential-check.sh --json` を実行してください。

スクリプトに組み込まれた 2 つの非 TTY 対応の注意点（ユーザーは何もしなくて OK — 文脈として記載）：

- **`SF_DISABLE_TELEMETRY=true` を自動 export。** 初回 `sf` 実行時に表示される y/N の telemetry 同意 prompt は非 TTY 環境（Claude Code の Bash tool）で hang するため、setup script はこの env var を export して prompt を skip します。
- **非 TTY モードでは OAuth URL が出力されません。** `sf org login web` は本物の TTY に attach されていないと auth URL を stdout/stderr に出力しないので、Claude が URL をインライン表示することはできません（ブラウザは自動で開きます）。ブラウザが開かない場合は Path B（Terminal power-user）にフォールバックしてください — そちらは URL をネイティブに表示します。

## アーキテクチャ

```
┌──────────────────────────────────────────────────────────────┐
│  Claude Code (CLI / Code タブ)                               │
│                                                              │
│              ┌─────────────┐                                 │
│              │  sf-query   │                                 │
│              │  (SKILL.md) │                                 │
│              └──────┬──────┘                                 │
│                     ▼                                        │
│        mcp__salesforce__run_soql_query  (data toolset)       │
└─────────────────────┬────────────────────────────────────────┘
                      │  stdio MCP transport
                      ▼
        bin/sf-mcp-launcher.sh   (brew → npx fallback)
                      │
                      ▼
        sf-mcp-server  (brew `salesforce-mcp` / npm `@salesforce/mcp` のバイナリ, Apache-2.0)
                      │
                      ▼
                  sf CLI  (sf org login web の OAuth token)
                      │
                      ▼
              Salesforce org REST API
```

セットアップ時間（1 回限り）：`/salesforce-toolkit:sf-setup` がユーザーのターミナルで 6 ステップのインストーラを実行。実行時：Claude Code が `.mcp.json` をロード → launcher shim を spawn → stdio 経由で `sf-mcp-server` を spawn → `sf-query` skill から `run_soql_query` MCP tool が利用可能になる。

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
