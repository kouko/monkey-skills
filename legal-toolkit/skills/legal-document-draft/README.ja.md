# legal-document-draft

台湾法務に基づき、新規の法律文書（プライバシーポリシー / 利用規約 / DPA / NDA）を、会社プロフィール + 交渉プレイブックから生成します。

## クイックスタート

1. リポジトリに `legal-playbook/profile.yml` を用意（スキーマは `assets/profile-schema.yml` 参照）
2. 必要に応じて `legal-playbook/<clause>.md` でスタンスのデフォルトを管理
3. `using-legal-toolkit` ルーター経由で「プライバシーポリシーをドラフトして」「NDA を書いて」と依頼
4. セッション固有の変数（製品名・個人情報項目・SDK 一覧など）を対話的に収集
5. 出力先: `legal-outputs/<timestamp>-<mode>/`
   - `<doc-type>.md` — 公開可能なドキュメント
   - `compliance.md` — 法務内部レビュー（チェックリスト判定 + TBD 移行ガイド）

## モード

| モード | 文書 | 主要法令 |
|---|---|---|
| privacy | 隱私權政策 / 個資告知事項 | 個資法 §8, §9, §21, 施行細則 §22, §27 |
| tos | 利用規約 | 民法, 消保法 §11-1 + §17, 公平交易法 |
| dpa | 委託処理契約 | 個資法 §4 + §8, 施行細則 §12 |
| nda | 機密保持契約 | 民法 §227, §247-1, §250, 商習慣 |

## TBD 移行

PDPC 子法に委ねられた項目（具体的通報時限・通報基準値など）は `compliance.md` の TBD エントリとして残ります。PDPC 子法公布後の更新手順は `references/tbd-migration-template.md` に記載（typically `assets/template-*.md` と `checklists/compliance-*.md` への 10 行未満の編集）。

## 対象外

- GDPR スタイルの文書生成（Path A により台湾現行法のみ扱う；spec §3 + §13 参照）
- 既存文書のレビュー — `legal-contract-review` を使用
- PDPC 子法公布の自動監視 — 頻度が低いため手動監視で十分

## 関連

- `legal-contract-review` — 相手方ドラフトのレビュー（NDA / SaaS など）
- `legal-playbook-author` — draft が参照する交渉スタンスの作成
