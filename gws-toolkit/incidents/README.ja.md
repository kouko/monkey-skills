# incidents/

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

Credential-leak incident playbook の出力先。**On-demand** — 実際に
credential-leak incident が発生した場合にのみ、このディレクトリに
markdown ファイルを追加します（incident 1 件につき 1 ファイル）。
通常はこの README のみが置かれます。

## トリガー条件

以下のいずれかが発生したら playbook を起動：

- `gws` OAuth client ID / secret が work tree に `git commit` されてしまった
- `git log -p` または `gitleaks` で credential pattern が検出された
- GCP Console のアラート（unauthorized API calls / quota spike）
- 本人または協力者が `~/.config/gws/*` を誤って repo 配下にコピーした

## ファイル名規約

```
incidents/YYYY-MM-DD-<short-slug>.md
```

例：`incidents/2026-05-12-leaked-client-secret.md`

## ファイル内容フレーム

`TECH-SPEC.md §8.4 Credential 洩漏 incident response playbook` の 7
ステップに対応。各 incident markdown には**実際の secret 値を絶対に
含めない**（ASVS V16 audit log のコンプライアンス要件）。記録対象：

1. 発見時刻 + 発見経路（例：`gitleaks protect` / code review / GCP アラート）
2. 影響範囲（どの commit / branch / remote か）
3. 実施済みステップ（`TECH-SPEC.md §8.4` 7 ステップに対応；完了時刻 + 実施者を併記）
4. Rotate リスト（OAuth Client ID、Keychain / file-backend の旧 token、
   7 日以内に派生したリソース）
5. フォローアップ action item（pre-commit hook の強化、deny rule 追加、
   協力者への rebase 状況の通知）
6. Post-mortem（次回予防：どの defence-in-depth が失敗したか？なぜか？）

## 他ディレクトリとの関係

- `.gitignore` + `.claude/settings.json` deny rule は**事前防御**
- `incidents/` は**事後記録** + 改善ループ
- `scripts/install-pre-commit.sh`（Phase 2 trigger-gated）は中間に位置する
  shift-left な検知層

事前防御は 100% カバーを保証できない（home-dir credential、外部ツール
の誤動作など）。そのため事後 playbook が補完網として必須となる。
