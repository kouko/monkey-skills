# using-git-worktrees

[English](README.md) | **日本語** | [繁體中文](README.zh-TW.md)

> Native `git worktree` ワークフロー、P3-C 準拠 — ラッパーなし、`git worktree add` + 文書化された `.worktrees/<branch-slug>/` サブディレクトリ規約 + `.gitignore` 規律のみ。並行ブランチの摩擦（stash-switch ループ、マルチクローンコスト、「context-switch するな」式の否認）を解消。このリポジトリ自身が同パターン採用（あなたが今読んでいるのは `.worktrees/code-toolkit-design/` の中）。

[code-toolkit](../..) プラグインの一部。エージェントが読み込むのは [`SKILL.md`](SKILL.md)、本 README は人間向け。

## Worktree が解決するもの

1 リポジトリ、N ブランチを N ディレクトリに同時 checkout、`.git/` は 1 つを共有。stash-switch ループなし、マルチクローンオーバーヘッドなし。

## `.worktrees/` 規約

```
repo-root/
├── .git/                    # 全 worktree 共有
├── .gitignore               # .worktrees/ を含む
├── .worktrees/
│   ├── feat-X/              # branch feat/X の worktree
│   ├── fix-prod-bug/        # branch fix/prod-bug の worktree
│   └── feat-design-redo/    # branch feat/design-redo の worktree
└── src/                     # main checkout
```

サブディレクトリ + `.gitignore` の理由：main checkout の `git status` が綺麗；IDE 横並びナビゲーション；ブランチ名を予測可能にミラー（スラッシュ → ハイフン）。

## クイックレシピ

```bash
# 初回セットアップ
echo ".worktrees/" >> .gitignore
mkdir -p .worktrees
git add .gitignore && git commit -m "chore: add .worktrees/ convention"

# 新ブランチを worktree で
git worktree add -b feat/foo .worktrees/feat-foo main
cd .worktrees/feat-foo

# 既存リモートブランチ
git fetch origin
git worktree add .worktrees/feat-foo feat/foo

# クリーンアップ
cd <repo-root>
git worktree remove .worktrees/feat-foo
```

## 使う場面 / 使わない場面

[`SKILL.md`](SKILL.md) §When to use + §When NOT to use を参照。クイックルール：`git stash` を週 1 回以上やって context-switch しているなら、worktree が欲しい。並行 context なしで 1 branch だけなら、不要。

## Cross-skill

- **`finishing-a-development-branch`** がブランチクリーンアップとして `git worktree remove` を呼ぶ
- **`dev-workflow:git-memory`** は worktree 間で同じ動作（`.git/` 共有なので commit trailer は特別扱い不要）

## このスキルがしないこと

- `git worktree` をカスタムツールでラップしない（P3-C）。ネイティブコマンド + 規約 がスキル全体
- worktree を自動作成しない — ユーザがコマンドを実行する
- worktree 数を追跡しない — 20 個 in-flight なら prune

## 関連

- [`SKILL.md`](SKILL.md) — 運用仕様 + Red Flags
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — worktree クリーンアップを呼ぶ
- `git help worktree` — キャノニカルリファレンス
- このリポジトリの `.worktrees/code-toolkit-design/` — design-then-build パターンの worked example
