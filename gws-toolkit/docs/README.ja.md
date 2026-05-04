# slides-toolkit/docs — 実装経験ドキュメント

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

このディレクトリには slides-toolkit 開発過程で蓄積された**実証データ**と**外部境界の観察記録**が置かれます。`PRODUCT-SPEC.md` / `TECH-SPEC.md` との違い：

- **PRODUCT-SPEC / TECH-SPEC** = 仕様と設計上の意思決定（should-be）
- **本ディレクトリ `docs/`** = 実測した挙動、踏み抜き記録、環境前提（as-is）

spec と実装の間に drift が生じた際、`docs/` は当時「なぜこう設計したか」を復元する歴史的記録、そして「Google / gws の境界はどこか」を確認する reference になります。

## ファイル索引

| ファイル | 用途 | 想定読者 |
|---|---|---|
| [`implementation-journal-2026-04-24.md`](implementation-journal-2026-04-24.md) | 初回の live E2E テスト完全フローログ（kouko macOS arm64、`@gmail.com`）— brew install gcloud から実 deck 生成まで | v0.5.0 がなぜこの形に進化したかを知りたい人 |
| [`gws-cli-quirks.md`](gws-cli-quirks.md) | 実測で判明した gws CLI の実挙動と spec drift — `--params` vs flag、cwd sandbox、scope 構文、URL フォーマット | skill 作成時に踏み抜いた人 / 新しい recipe を追加する人 |
| [`google-oauth-automation-limits.md`](google-oauth-automation-limits.md) | Google OAuth policy の自動化境界 — なぜ OAuth client / test user / consent screen を自動化できないのか、gws ソースコード層の証拠 | 「本当に自動化できないの？」と疑う人 |
| [`console-ui-reference.md`](console-ui-reference.md) | Google Cloud Console 2026-04 新 UI（Google Auth Platform）のナビ対照 — Branding / Audience / Clients のパス | Console で迷子になった人 |

## 書き込みタイミング

以下の場面で `docs/` を更新します：

- **初回または重大な live E2E テスト** → `implementation-journal-*` を更新（日付付き）
- **gws CLI と spec の食い違いを発見** → `gws-cli-quirks.md` を更新
- **Google / upstream policy / API の境界変動** → `google-oauth-automation-limits.md` か `console-ui-reference.md` を更新
- **新 recipe 開発時に踏んだ落とし穴** → `gws-cli-quirks.md` を更新

## ここに置かない内容

- spec レベルの設計判断 → `PRODUCT-SPEC.md` / `TECH-SPEC.md`
- バージョン履歴 → `CHANGELOG.md`
- ユーザー向け操作ガイド → `skills/google-slides-setup/protocols/gcp-console-walkthrough.md`
- recipe の具体的な呼び出し方法 → `skills/google-slides-api/protocols/recipe-*.md`

`docs/` は歴史 + 外部境界のデータベースであり、how-to ではありません。
