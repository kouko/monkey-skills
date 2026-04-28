# slides-toolkit

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> ⚠️ **Cowork 互換性**：Claude Code CLI / Code tab のみ動作。Cowork tab は sandbox の URL allowlist により Google Slides API 呼び出しがブロックされる。詳細な retrospective は [`investing-toolkit/docs/mcp-setup.md`](../investing-toolkit/docs/mcp-setup.md) を参照。

**Version**: 0.1.0-mvp
**Part of**: [monkey-skills](https://github.com/kouko/monkey-skills)
**License**: MIT

Google Slides 生成 toolkit — 構造化された brief（outline + tables +
ローカル画像）を Claude Code skills 経由で完成した Google Slides
deck に変換します。単一コマンドの pipeline：`brief → deck URL ≤ 3 分`。

Backend-agnostic な設計知識層（`slides-design`）と、差し替え可能な
backend builders を組み合わせる構成。MVP は Google Slides backend
のみ提供；HTML / PPTX / Marp backends は Phase 2+ で trigger-gated
（`PRODUCT-SPEC.md §3.5` 参照）。

## Status

- **Release**：MVP v0.1.0-mvp（pre-release；Platform-Pivot spec は 2026-04-23 に凍結）
- **Backends**：`google-slides` のみ
- **Platform**：macOS 14+（darwin-arm64 / darwin-x64）
- **Primary user**：kouko（個人の生産性ツール）
- **Runtime posture**：純粋な shell + `curl` + ブラウザ；`gws` / `jq` の
  binary は `~/.cache/slides-toolkit/bin/` へ self-fetch し SHA-256 で検証

## Quick Start

クリーンなマシンから最初の deck まで 3 ステップ。

### 1. インストール

```bash
# monkey-skills Claude Code marketplace 経由で plugin を追加
# （marketplace.json に登録すれば plugin は自動で有効化される）
```

### 2. Setup（初回 onboarding、約 20 分）

Claude Code 内で setup skill を呼び出す：

```
/google-slides-setup
```

以下を順に案内：

- `gws` binary の取得 + SHA-256 検証
- Google Cloud Console 4 ステップの OAuth client 設定（External + Testing モード）
- Keychain / file-backend credential 保存方式の検出
- Issue-119 workaround 環境変数 guard（`GOOGLE_WORKSPACE_CLI_CLIENT_ID/SECRET`）
- 初回ログイン認証 + token smoke test

予算：クリーンな macOS マシンで **≤ 20 分**（KR2）。

### 3. 最初の deck を生成

```
/using-slides-toolkit
```

まず物語構成 + chart-type のガイダンスを得たい場合は `slides-design`
を選び、その後 `google-slides-builder` で deck をビルドします。
すでに `slide-plan.json` と登録済みの template Drive ID があれば、
直接 builder へ進む形でも可。

予算：brief 提出から Drive URL まで **≤ 3 分**（KR1）。

## Skills Inventory

| Skill | Layer | 用途 |
|-------|-------|------|
| `using-slides-toolkit` | router（backend-agnostic） | エントリーポイント — `target` で setup / design / builder へ振り分け |
| `slides-design` | knowledge（backend-agnostic） | Minto Pyramid + SCQA + chart-selection リファレンス；どの backend にも適用 |
| `google-slides-setup` | google-slides backend | 初回 onboarding（gws + GCP + auth）；状態に応じた分岐 |
| `google-slides-builder` | google-slides backend | 実行層 — gws 経由で copy template / replaceAllText / insert-image |

Phase 2+（trigger-gated；MVP には含めない）：`html-builder`、`pptx-builder`、
`marp-builder`。

## Prerequisites

すべて macOS 14+ に同梱：

- `zsh` / `bash`
- `curl`
- 任意のモダンブラウザ（Google OAuth 同意フロー用）

その他は toolkit が自動取得：

- `gws` binary → `~/.cache/slides-toolkit/bin/gws`（SHA-256 pinned）
- `jq` binary → `~/.cache/slides-toolkit/bin/jq`（SHA-256 pinned）

**不要**：Python、uv、gcloud、Homebrew、Node.js。shell 以外の言語
runtime はゼロ。

## Architecture

3 層構成（全体像は `PRODUCT-SPEC.md §6.3.1` + `TECH-SPEC.md §2.1-§2.2`
を参照）：

```
┌──────────────────────────────────────────────────────┐
│ Layer 1 — Router (backend-agnostic)                  │
│   using-slides-toolkit                               │
│     → dispatches by slide-plan target field          │
└────────┬─────────────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────────────┐
│ Layer 2 — Design knowledge (backend-agnostic)        │
│   slides-design                                      │
│     → Minto / SCQA / chart-selection                 │
│     → applies to google-slides / html / pptx / marp  │
└────────┬─────────────────────────────────────────────┘
         │
┌────────▼─────────────────────────────────────────────┐
│ Layer 3 — Backend execution (backend-specific)       │
│   google-slides-setup     [MVP]                      │
│   google-slides-builder   [MVP]                      │
│   html-builder            [Phase 2+]                 │
│   pptx-builder            [Phase 2+]                 │
│   marp-builder            [Phase 2+]                 │
└──────────────────────────────────────────────────────┘
```

**なぜ**：設計原則（物語構成、chart 選択）は出力フォーマットを跨いで
安定する一方、実行技術（gws / pandoc / python-pptx / marp-cli）は
backend ごとに進化するため。分離することで、新しい backend を追加
するたびに知識層が揺さぶられるのを防ぐ。

クロスドメインのプロダクト観点（vision + MVP scope + Job Story + 4 Big Risks）
は `PRODUCT-SPEC.md`、モジュール設計・データフロー・interface contract
は `TECH-SPEC.md` を参照。

## Security Notes

Credentials は repository に決して入らない。二重の防御層：

1. **`.claude/settings.json` deny rule** — credential ファイル
   （home-dir + repo-relative）への Claude 側ツール（Read / Bash /
   Write）アクセスを遮断。Repo-relative の `.gitignore` は git が `~`
   を展開しないため `~/.config/gws/**` を保護できない；deny rule が
   その隙間を埋める。
2. **`.gitignore`** — repo-relative の機密パターンを除外：
   `.config/gws/`、`**/client_secret*.json`、`**/credentials.enc`、
   `**/.encryption_key`、`.env*`、`.cache/`、ローカルテスト fixture。

完全な脅威モデル（OWASP ASVS v5.0.0 L1 — V1 / V2 / V5 / V13 / V14 / V16
マッピング）、pre-commit hook の推奨事項、credential 流出時の incident
response playbook は `TECH-SPEC.md §8 Security & Credential Hygiene`
を参照。

Incident log（万が一トリガーされた場合）は要求ベースで `incidents/`
に置く — 事前作成はしない。Playbook の項目フォーマットは
`incidents/README.md` を参照。

## License

MIT — 親リポジトリ `monkey-skills` と整合。repo ルートの `/LICENSE`
を参照。

## Links

- [PRODUCT-SPEC.md](./PRODUCT-SPEC.md) — planning-team spec（vision、ユーザー、
  ゴール、非ゴール、Platform Pivot の根拠）
- [TECH-SPEC.md](./TECH-SPEC.md) — code-team spec（アーキテクチャ、モジュール、
  インターフェース、テスト、セキュリティ、OPEN answers）
- [CHANGELOG.md](./CHANGELOG.md) — バージョン履歴
- [parent repo](https://github.com/kouko/monkey-skills)
