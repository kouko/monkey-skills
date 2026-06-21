# verification-before-completion

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> **HARD-GATE — パッケージレベルテスト実行なしで「DONE」を宣言するな。** P3-B 準拠。正規パッケージレベルテストコマンド（`npm test` / `pytest` / `go test ./...` / `cargo test` 等）を実行し、実行エビデンスなしの "done" 主張を拒否。捕捉対象：テスト相互作用バグ（A + B 一緒だと fail）、orphan テスト（存在するが既定 suite に入っていない）、lint pass だがテスト fail、manual テストは検証ではない。

[loom-code](../..) プラグインの一部。エージェントが読み込むのは [`SKILL.md`](SKILL.md)、本 README は人間向け。

## パッケージレベル実行のみが捕まえる 3 つの失敗モード

1. **テスト相互作用バグ** — Test A 単独 PASS、B 単独 PASS、A+B 一緒で FAIL（共有可変 state、fixture リーク、ポート衝突）
2. **Orphan テスト** — テストファイルが存在し assertion もあるが実行されない（`tests/` glob 漏れ、拡張子間違い、config 除外）。著者は「カバー済み」と思っているが現実は穴
3. **Lint ≠ テスト** — TypeScript コンパイル成功 + ESLint クリーン + ランタイム null-deref。静的解析はテスト実行と直交

## 使う場面

- 機能 / タスク / ブランチを "done" 宣言する前
- `subagent-driven-development` がタスク終端で自動呼び出し（高速 suite のオーケストレータ判断）
- `finishing-a-development-branch` がクローズフロー Step 2 で **必ず** 呼ぶ

## 使わない場面

[`SKILL.md`](SKILL.md) §When NOT to Use：
- テストがまだ無い（新規 repo、これが最初のテストを足す commit）
- 純 doc / config / 生成コード再生成（ランタイム挙動変更なし）
- テストインフラ自体が壊れている（runner クラッシュ、テスト failure ではない）
- ユーザの明示的 override AND 変更が exempt カテゴリ該当

## 同梱物

- [`SKILL.md`](SKILL.md) — HARD-GATE 措辞、免責リスト、4 ステップ手順、8 つの Red Flags 拒否
- [`references/test-invocation-by-stack.md`](references/test-invocation-by-stack.md) — 言語/ビルドツール別正規コマンド（20+ stacks）；monorepo 取扱；runner ごとの「0 tests ran」検出；遅い suite 対処

## Cross-skill 契約

- **呼び出し元**：`subagent-driven-development`（任意、タスク終端）+ `finishing-a-development-branch`（必須 Step 2）
- **失敗時 route**：`tdd-iron-law`（自明な失敗 → RED 書いて修正）/ `systematic-debugging`（非自明 → 4-phase REPRODUCE）
- **CI の代わりにはならない** — CI は push 後；本スキルは push 前に走り push に綺麗な diff だけ載せる

## このスキルがしないこと

- テストを書かない（`tdd-iron-law` の役割）
- コード品質を判定しない（`requesting-code-review` / SDD レビュア）
- どのテストが存在すべきか決めない — suite は suite、本スキルは「実行 + パス」を検証

## 関連

- [`SKILL.md`](SKILL.md) — 運用仕様
- [`references/test-invocation-by-stack.md`](references/test-invocation-by-stack.md) — コマンドテーブル
- [`../tdd-iron-law/SKILL.md`](../tdd-iron-law/SKILL.md) — テストを作る規律
- [`../requesting-code-review/SKILL.md`](../requesting-code-review/SKILL.md) — 兄弟 pre-merge gate（人間レビュー）
- [`../systematic-debugging/SKILL.md`](../systematic-debugging/SKILL.md) — 非自明 failure のとき
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — オーケストレータ
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — ルータ；本スキルは Stage 7（Verification）
