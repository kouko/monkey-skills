# using-git-worktrees

[English](README.md) | [日本語](README.ja.md) | **繁體中文**

> Native `git worktree` 工作流，P3-C 規定 — 無 wrapper、純 `git worktree add` + 文件化的 `.worktrees/<branch-slug>/` 子目錄慣例 + `.gitignore` 紀律。解決平行 branch 的摩擦（stash-switch 迴圈、多 clone 成本、「不要 context switch」式的否認）。本 repo 自己採這個 pattern（你現在讀的這份就在 `.worktrees/loom-code-design/` 裡）。

[loom-code](../..) plugin 的一部分。Agent 載入的是 [`SKILL.md`](SKILL.md)；本 README 是給人類看的。

## Worktree 解決什麼

1 個 repo、N 個 branch 同時 checkout 在 N 個目錄、共用一個 `.git/`。沒 stash-switch 迴圈、沒多 clone 成本。

## `.worktrees/` 慣例

```
repo-root/
├── .git/                    # 全 worktree 共用
├── .gitignore               # 含 .worktrees/
├── .worktrees/
│   ├── feat-X/              # branch feat/X 的 worktree
│   ├── fix-prod-bug/        # branch fix/prod-bug 的 worktree
│   └── feat-design-redo/    # branch feat/design-redo 的 worktree
└── src/                     # main checkout
```

子目錄 + `.gitignore` 的理由：main checkout 的 `git status` 乾淨；IDE 並排導航；branch 名稱可預期 mirror（slash → dash）。

## 快速 recipe

```bash
# 一次性 setup
echo ".worktrees/" >> .gitignore
mkdir -p .worktrees
git add .gitignore && git commit -m "chore: add .worktrees/ convention"

# 開新 branch 進 worktree
git worktree add -b feat/foo .worktrees/feat-foo main
cd .worktrees/feat-foo

# 既存 remote branch
git fetch origin
git worktree add .worktrees/feat-foo feat/foo

# 清理
cd <repo-root>
git worktree remove .worktrees/feat-foo
```

## 用 / 不用時機

看 [`SKILL.md`](SKILL.md) §When to use + §When NOT to use。快速規則：你一週要 `git stash` 一次以上來 context switch，那就該用 worktree。只做 1 條 branch 沒並行 context，就不需要。

## Cross-skill

- **`finishing-a-development-branch`** 在 branch 清理流程呼 `git worktree remove`
- **`dev-workflow:git-memory`** 在 worktree 間運作完全相同（共用 `.git/`，commit trailer 不需特殊處理）

## 這個 skill 不做的事

- 不把 `git worktree` 包成 custom 工具（P3-C）。Native 指令 + 慣例 是整個 skill
- 不自動 create worktree — 使用者自己下指令
- 不追蹤 worktree 數 — 你有 20 個 in-flight 就 prune

## 參考

- [`SKILL.md`](SKILL.md) — 運作規格 + Red Flags
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — 呼 worktree 清理
- `git help worktree` — canonical 文件
- 本 repo 的 `.worktrees/loom-code-design/` — design-then-build pattern 的 worked example
