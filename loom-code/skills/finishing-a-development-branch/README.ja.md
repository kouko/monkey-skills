# finishing-a-development-branch

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> オーケストレータスキル — ブランチクローズシーケンスを束ねる：[`requesting-code-review`](../requesting-code-review)（Step 1 人間レビュー） → [`verification-before-completion`](../verification-before-completion)（Step 2 パッケージレベルテスト） → P3-D 必須 `dev-workflow:git-memory` 委譲（commit メッセージ trailer） → git commit → push → 任意 gh pr create → 任意 [`using-git-worktrees`](../using-git-worktrees) クリーンアップ。**自動 merge しない** — 最終 merge 決定はユーザの権限。

[loom-code](../..) プラグインの一部。エージェントが読み込むのは [`SKILL.md`](SKILL.md)、本 README は人間向け。

## フロー

```
finishing-a-development-branch
  ├─→ Step 1: requesting-code-review        （人間判断品質）
  ├─→ Step 2: verification-before-completion （パッケージレベルテスト pass）
  ├─→ Step 3: dev-workflow:git-memory       （commit メッセージ trailer、P3-D 必須）
  ├─→ Step 4: git commit                    （Step 3 のメッセージ使用）
  ├─→ Step 5: git push
  ├─→ Step 6: gh pr create                  （任意、ユーザ opt-in）
  └─→ Step 7: git worktree remove           （任意、ユーザ確認）
```

各 Step は次を gate する。🔴 fatal レビュー findings または test failure は進行を BLOCK。各 user-visible action（commit メッセージ承認、push、PR 作成、worktree 削除）前にユーザ確認必須。

## 使う場面

- 「ブランチ完了」/「機能完成」/「merge してよい」/「ship」/「クローズして」
- 「この branch で PR 開いて」
- 「ここまでで終わり、次は？」（「終わり」フレーミング → 次のタスク前にブランチ完了）
- SDD がマルチタスクプランの全タスク DONE 直後に積極的呼び出し

## 使わない場面

[`SKILL.md`](SKILL.md) §When NOT to Use：
- タスク途中作業（SDD プラン未完）
- main 直接コミットの trivial（個人プロジェクトの 1 行 doc fix）
- 廃棄予定ブランチ（スキル該当せず；削除でよい）
- ユーザの明示的 override AND 真の理由（cherry-pick / known-trivial クリーンアップ）

## 委譲の塊 — 意図的設計

本スキルは新規ロジックを意図的に軽く保つ。各 step は specialist に委譲：

| Step | 委譲先 | オーケストレータが直接やらない理由 |
|---|---|---|
| 1 | `requesting-code-review` | 品質レビューはそれ自体スキル |
| 2 | `verification-before-completion` | パッケージレベルテスト invocation はそれ自体スキル |
| 3 | `dev-workflow:git-memory` | P3-D 必須 — git-memory が trailer 必要性を判断；オーケストレータは複製しない |
| 4 | git CLI | 標準 git commit |
| 5 | git CLI | git push（新規ブランチなら upstream 設定） |
| 6 | gh CLI | gh pr create（opt-in） |
| 7 | `using-git-worktrees` | Worktree クリーンアップパターンは向こうに |

## このスキルがしないこと

- コードレビュー自体しない（委譲）
- テスト実行自体しない（委譲）
- Memory trailer 判断しない（P3-D — git-memory に委譲）
- main にマージしない（ユーザ権限）
- 認可なく force-push しない
- Commit amend しない（CLAUDE.md ポリシー準拠 — 常に新 commit）
- Opt-in なく PR を自動作成しない
- 確認なく worktree を自動削除しない

## 関連

- [`SKILL.md`](SKILL.md) — 運用仕様 + 7-step デフォルトフロー + Red Flags
- [`../requesting-code-review/SKILL.md`](../requesting-code-review/SKILL.md) — Step 1 委譲先
- [`../verification-before-completion/SKILL.md`](../verification-before-completion/SKILL.md) — Step 2 委譲先
- [`../using-git-worktrees/SKILL.md`](../using-git-worktrees/SKILL.md) — Step 7 委譲先
- `dev-workflow:git-memory` — Step 3 委譲先（P3-D 必須）
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — ルータ；本スキルは Stage 8（Branch close）
- CLAUDE.md §"Committing changes with git" — 継承される git ポリシー
