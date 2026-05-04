# gws-toolkit

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> 🚧 **検証期間中 — Phase 1 完了、日常運用検証待ち。** [`slides-toolkit/`](../slides-toolkit/) の後継として 2026-05-04 に strangler-fig fork で seed。Phase 1（upstream 5 skill vendor + α-trim + リネーム + OAuth scope 拡張 + Drive 安全 wrapper）は 2026-05-04 に完了（CHANGELOG `0.4.0-strangler-fig-seed` 参照）。≥ 2 週間の検証期間に入り、(1) slides-builder で Slides deck 生成 ≥ 1 件、(2) vendored `gws-drive` 経由の ad-hoc Drive 操作 ≥ 1 件、(3) `safe-delete.sh` 経由の破壊的操作 ≥ 1 件、(4) KR1 deck 生成時間に regression なし — を確認。検証通過後 slides-toolkit が Phase 3 deprecation に入るまで、両 plugin が併存します。Google とは無関係。

> Brief から Google Workspace artifacts（Slides / Docs / Sheets / Drive）を Claude Code skill で生成。pure shell + `gws` CLI、Python / gcloud 不要。

> ⚠️ **Cowork 互換性 — Claude Code CLI / Code tab のみ対応。** Google
> Slides / Drive API 呼び出しは Claude Desktop Cowork sandbox の URL
> allowlist によって blocked されます（`investing-toolkit` と同じ
> 制約。詳細は
> [investing-toolkit MCP setup retrospective](../investing-toolkit/docs/mcp-setup.md)）。
> Cowork 利用者は Claude Code CLI または Claude Desktop Code tab に
> 切り替えてください。

## Background

Google Slides deck を継続的に作成する作業には、機械的な要素が大き
な比重を占める — 文字差し替え、画像 upload、placeholder の位置合
わせ。`slides-toolkit` はこの繰り返し layer を skill 化し、残った
時間を deck 配管ではなく内容と design 判断に向けるためのものです。

設計は **Platform Pivot architecture**（PRODUCT-SPEC v0.2）に従い
ます — backend-agnostic な設計知識 layer（`slides-design`）と、
plug 可能な execution layer を切り離しています。MVP では
`google-slides` backend のみを実装。`html` / `pptx` / `marp` backend
は Phase 2+ の trigger-gated 範囲です。

## Status

| 項目 | 値 |
|---|---|
| Release | `0.1.0-mvp`（[`CHANGELOG.md`](CHANGELOG.md) 参照） |
| Backends | `google-slides`（MVP）・`html` / `pptx` / `marp` は Phase 2+ trigger-gated |
| Platform | macOS（darwin-arm64 / darwin-x86_64） |
| Account scope | 個人 Google アカウント（`@gmail.com`）；Workspace アカウントは Phase 2+ |
| Runtime posture | shell + curl + browser のみ。`gws` / `jq` binary は toolkit が自動取得 |
| License | MIT |

## インストール

`monkey-skills` marketplace 経由で plugin を追加し、Claude Code を
再起動して skill を読み込ませます。

```bash
# Claude Code 内から
/plugin install gws-toolkit@monkey-skills
```

## Quick start

2 phase 構成。初回 setup は一度だけ。以降は毎回 deck 生成 phase の
みを使います。

### 1. 初回 setup（目標：≤ 20 分 — KR2）

```
> /gws-setup
```

`gws-setup` skill に route。現在の状態を検出し、`gws` +
`jq` を `~/.cache/slides-toolkit/bin/` に取得、GCP Console での
手動設定（OAuth Client + Test User）を案内し、必要なら issue #119
の workaround を `~/.config/gws/env.sh` に書き込みます。

Google の OAuth policy（External + Testing mode）による境界が
あります。何が自動化できて何ができないかは
[`docs/google-oauth-automation-limits.md`](docs/google-oauth-automation-limits.md)
を参照してください。

### 2. Deck 生成（目標：≤ 3 分 — KR1）

```
> /using-gws-toolkit
> 「この outline を 6 枚の product proposal に」
```

router の `using-gws-toolkit` が意図を判定し、必要に応じて
`slides-design` に narrative 構造（Minto / SCQA / chart 選択）を
委譲し、最終的に `slide-plan.json` v1.2 を `slides-builder`
に渡します。builder は 4 step pipeline（空 deck 作成 → predefined
layout で slide 作成 → text 挿入 → ローカル画像挿入）を実行し、
Drive URL を返します。

`/using-gws-toolkit` と `/gws-setup` はどちらも skill
の auto-route です（`commands/` shim はなく、plugin に slash
command は含まれません）。skill 名を入力すれば Claude Code が
dispatch します。

## アカウント管理

`/gws-setup` 完了後の日常運用。toolkit は同時に refresh token を 1 つ
だけ保存する。OAuth クライアント設定（`client_secret.json`, `env.sh`）は
ログイン間で保持されるので、再認証やアカウント切り替えで GCP Console の
手順を再実行する必要はない。

### 7 日期限の再認証（同一アカウント）

External + Testing モードの OAuth refresh token は 7 日で失効する。
切れたら：

```
bash scripts/gws/refresh-auth.sh
```

同じスコープで `gws auth login` を再実行する；ブラウザ側のプロンプト
は短く（authorise 済みアプリ）、新しい refresh token がまた約 7 日有効。

### Google アカウントの切り替え

```
bash scripts/gws/gws-login.sh --switch
```

`gws-logout.sh` 経由でローカル credentials を消してから OAuth を
再実行する。ブラウザに Google のアカウント選択が出るので（複数の
Google アカウントがブラウザに sign-in されている場合）、新しい
アカウントを選ぶと新しい refresh token が保存される。`--switch`
を付けない場合 `gws-login.sh` は idempotent — 既に authed なら
exit 0。

### Logout

```
bash scripts/gws/gws-logout.sh
```

ローカル credentials のみ消去（`credentials.enc` + `token_cache.json`
+ Keychain entry）。Server-side では refresh token は ~7 日 Testing
モード期限まで有効なまま。即座に server-side revoke したい場合は
[myaccount.google.com/permissions](https://myaccount.google.com/permissions)
を訪問する。toolkit は server-side revoke を自動化しない — それを
やると `credentials.enc` を復号して refresh token を取り出す必要が
あり、`credential-check.sh` の metadata-only アクセスパターン
（ASVS V14 secrets-at-rest）を破ることになる。

## Skills

plugin は **9 skill** を 2 層の provenance で提供します — 4 toolkit-original
+ 5 vendored from upstream
[`googleworkspace/cli`](https://github.com/googleworkspace/cli) at
`v0.22.5` (Apache-2.0；各 vendored SKILL.md frontmatter
`metadata.vendored_from` に provenance を記録)。

**Toolkit-original (4)**

| Skill | Layer | 役割 |
|---|---|---|
| `using-gws-toolkit` | Router | 意図判定、`slide-plan.target` 読み込み、適切な skill へ route |
| `gws-setup` | Setup（generic） | 初回 GCP Console / OAuth (4 scopes: presentations + drive + documents + spreadsheets) / `gws` + `jq` bootstrap、state detection、7 日サイクル re-auth |
| `slides-design` | Knowledge（Slides 専用） | Minto Pyramid + SCQA narrative、chart 選択 |
| `slides-builder` | Execution（Slides 専用） | `slide-plan.json` v1.2 → pre-flight → 4 recipe chain → deck URL；placeholder-map composition pattern を内蔵 |

**Vendored upstream (5, Apache-2.0)**

| Skill | API surface |
|---|---|
| `gws-shared` | auth + global flags + security rules（他 4 skill が PREREQUISITE で参照） |
| `gws-drive` | Drive API v3（about / files / permissions / changes など） |
| `gws-docs` | Docs API v1（`documents.{batchUpdate, create, get}`） |
| `gws-slides` | Slides API v1（`presentations.{batchUpdate, create, get}` + pages） |
| `gws-sheets` | Sheets API v4（`spreadsheets.*` + values + sheets + developerMetadata） |

`using-gws-toolkit` は backend-agnostic に設計してあるため、将来の
`html-builder` / `pptx-builder` / `marp-builder` skill が同じ
routing entry を変更なしで再利用できます。

Drive / Docs / Sheets / Slides の raw API method 探索は vendored 各
skill が一次線。slide-plan pipeline・三段階削除安全機構・provenance
tag 等の toolkit-opinion は toolkit-original 層が一次線。

## 前提条件

| 項目 | 要件 |
|---|---|
| OS | macOS 14+（darwin-arm64 / darwin-x86_64）。Linux / WSL は Phase 2+ |
| Shell | zsh または bash（macOS 標準の zsh で OK） |
| ネットワーク tool | `curl`（macOS 標準） |
| Browser | Chrome または Safari（GCP Console step で 1 回だけ必要） |
| Google アカウント | 個人 `@gmail.com`。Workspace アカウントは Phase 2+ |

**不要**：Python、uv、gcloud、brew、npm。`gws` と `jq` の binary
は `scripts/gws/bootstrap.sh` が HTTPS + `curl -f` で
`~/.cache/slides-toolkit/bin/` に取得します。

## Architecture

3 layer 構成。router と design 知識 layer は backend-agnostic で、
出力 format に bind されるのは execution layer のみです。

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1 — Router（backend-agnostic）                       │
│  using-gws-toolkit                                       │
│  意図判定 · slide-plan.target 読み込み · dispatch            │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────────┐
        ▼                    ▼                        ▼
┌─────────────────┐  ┌─────────────────┐  ┌──────────────────────┐
│  Layer 2 —      │  │  Layer 3 —      │  │  Layer 3 —           │
│  Design         │  │  Backend exec   │  │  Backend exec        │
│  knowledge      │  │ （onboarding） │  │ （build pipeline）   │
│ （agnostic）    │  │                 │  │                      │
│  slides-design  │  │  google-slides- │  │  google-slides-      │
│                 │  │  setup          │  │  builder             │
│  Minto · SCQA · │  │                 │  │      ↓ uses          │
│  chart 選択     │  │  GCP / OAuth /  │  │  google-slides-api   │
│                 │  │  gws bootstrap  │  │  (per-op recipes)    │
└─────────────────┘  └────────┬────────┘  └──────────┬───────────┘
                              │                      │
                              └──────────┬───────────┘
                                         ▼
                              scripts/gws/*.sh
                              gws CLI · ~/.cache binaries
                                         ▼
                              Google Slides + Drive API
                                         ▼
                                   Deck URL
```

Phase 2+ backend（`html-builder` / `pptx-builder` /
`marp-builder`）は `slides-builder` の隣に Layer 3 として
追加でき、Layer 1 / Layer 2 には変更が不要です。詳細は PRODUCT-SPEC
§2.1 / §2.2 と TECH-SPEC §2.1 / §2.2 を参照してください。

## セキュリティ

Credential を repo に入れない。これを 2 つの仕組みで担保しています
（TECH-SPEC §8）。

**Claude tool layer block** — `.claude/settings.json` で gws の
credential store に触れる Read / Bash / Write をすべて deny：

```json
{
  "permissions": {
    "deny": [
      "Read(~/.config/gws/**)",
      "Read(~/.cache/slides-toolkit/bin/.version)",
      "Bash(cat ~/.config/gws/*)",
      "Bash(cat ~/.config/gws/**)",
      "Bash(cp ~/.config/gws/* *)",
      "Bash(git add ~/.config/gws/*)",
      "Write(~/.config/gws/**)"
    ]
  }
}
```

**Repo-relative な ignore** — `.gitignore` で repo tree に
入り込み得る credential を弾く：

```
.config/gws/
*/keyring-file.json
*/env.sh
.cache/slides-toolkit/
```

`.gitignore` は `~/.config/gws/**` には match できません（git は
repo-relative path のみで `~` を展開しないため）。home directory
側は上の `settings.json` deny rule が責任を持ちます。万一
credential を漏洩した場合は TECH-SPEC §8.4 の incident playbook
に従ってください。

## リンク

- [PRODUCT-SPEC.md](PRODUCT-SPEC.md) — product 方向、Job Story、OKR / KR、Non-Goals、Phase 2+ trigger
- [TECH-SPEC.md](TECH-SPEC.md) — module 設計、`slide-plan.json` v1.2、shell script 契約、セキュリティ
- [CHANGELOG.md](CHANGELOG.md) — version 履歴（`0.1.0-spec` → `0.6.0-i18n`）
- [docs/console-ui-reference.md](docs/console-ui-reference.md) — 現在の Google Cloud Console UI walkthrough
- [docs/google-oauth-automation-limits.md](docs/google-oauth-automation-limits.md) — 自動化できないものとその理由
- [docs/gws-cli-quirks.md](docs/gws-cli-quirks.md) — live test で発見した gws CLI の罠
- 親 repository：[`monkey-skills`](https://github.com/kouko/monkey-skills)

## 貢献

本 plugin は [`monkey-skills`](https://github.com/kouko/monkey-skills)
repository の一部です。Issue / PR は同 repo に投げてください。skill
構造は repo root の `CLAUDE.md` と `domain-teams:skill-team` skill
の慣例に従います。

## License

MIT — 詳細は repository root の [LICENSE](../LICENSE) を参照。
