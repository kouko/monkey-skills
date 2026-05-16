# tdd-iron-law

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> **失敗するテストを先に書かない限り、プロダクションコードを書いてはならない。** 根拠：Beck (2002) *Test-Driven Development: By Example* 序文＋第 1 章＋第 II 部 (Addison-Wesley, ISBN 978-0321146533)、Martin (2008) *Clean Code* 第 9 章 TDD の三法則 (Prentice Hall, ISBN 978-0132350884)、和田卓人 訳 (2017) 『テスト駆動開発』 オーム社 ISBN 978-4274217883。

[code-toolkit](../..) プラグインの一部。エージェントが読み込むのは [`SKILL.md`](SKILL.md)、本 README は人間向け。

## このスキルが強制する規律

一つの規律を三つの一次資料が支える：

- **Beck (2002) 序文**：*"Write the test you wish you had. Make it fail. Make it pass. Make it clean."*
- **Martin (2008) Clean Code 第 9 章「TDD の三法則」§1**：*"You may not write production code until you have written a failing unit test."*
- **和田卓人 訳 (2017) 訳者解説**：「テストは仕様の具体化であり、設計の feedback loop である」。

違反したときの唯一の正しい対応は **コードを削除して、テストを書き、最初からやり直す**。「あとでテスト追加します」ではない。削除は罰ではなく、違反で失われた feedback loop の復旧。

## 使う場面

`using-code-toolkit` が実装作業（新機能 / バグ修正 / リファクタ / マイグレーション）を検知した時点で自動呼び出し。さらに `subagent-driven-development` の implementer サブエージェント内部でも自己呼び出しされる。

## 使わない場面

例外リストは [`SKILL.md`](SKILL.md) §When NOT to Use で限定列挙：

- 使い捨ての spike（同セッション内で削除、commit しない）
- 仕様から生成されるコード（protobuf, ORM migration など）
- 自明な getter / setter / 単純委譲
- 純粋な設定ファイル（実行ロジックを含まない）
- ユーザーが明示的に override AND 上記いずれかに該当

このリストに該当しない作業には Iron Law が適用される。新しい例外を勝手に作らないこと。

## このスキルがしないこと

- カバレッジを測らない。カバレッジは遅延指標で、TDD のターゲットは feedback loop。
- ユーザーの代わりにテストを書かない — ユーザー / エージェントがプロダクションコードより先に失敗テストを書くことを強制するだけ。
- `verification-before-completion`（Phase 3）の代わりにはならない。後者は diff に含まれる全ての挙動について commit 履歴に「失敗→成功」のテストが存在することを再検証する。

## 知識層

[`standards/tdd-standard.md`](standards/tdd-standard.md) は `domain-teams/skills/code-team/standards/tdd-standard.md` のバイト一致 functional copy に 5 行の SSOT ヘッダを付けたもの。ドリフトは `code-toolkit/scripts/verify-drift.py` が監視。規律を変更する場合、`domain-teams:code-team` 側の canonical を編集し、同じコミットで `code-toolkit/scripts/distribute.py` を実行する。

## 関連

- [`SKILL.md`](SKILL.md) — エージェント向け運用仕様（鉄則 + サイクル + 例外リスト + Red Flags + 偽 GREEN 診断）。
- [`standards/tdd-standard.md`](standards/tdd-standard.md) — TDD 規律のキャノニカル全文 (F.I.R.S.T、三法則、anti-patterns、JP アンカー)。
- [`references/testing-anti-patterns.md`](references/testing-anti-patterns.md) — 一次資料引用付き anti-pattern 索引。
- [`../using-code-toolkit/SKILL.md`](../using-code-toolkit/SKILL.md) — ルーター（この skill の流れ上の位置）。
- [`../../scripts/canonical/README.md`](../../scripts/canonical/README.md) — SSOT ポインタ + drift ポリシー。
