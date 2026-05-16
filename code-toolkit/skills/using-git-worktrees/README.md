# using-git-worktrees

**English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

> Native `git worktree` workflow per P3-C — no wrapper, just `git worktree add` with a documented `.worktrees/<branch-slug>/` subdirectory convention + `.gitignore` discipline. Solves the friction of parallel branches (stash-switch loops, multi-clone costs, "don't context switch" denialism). This very repo uses the pattern (`.worktrees/code-toolkit-design/` is where you're reading this from right now).

Part of the [code-toolkit](../..) plugin. Operational spec the agent loads is [`SKILL.md`](SKILL.md); this README is for humans.

## What worktrees solve

One repo, N branches checked out in N directories simultaneously, sharing one `.git/`. No stash-switch loops, no multi-clone overhead.

## The `.worktrees/` convention

```
repo-root/
├── .git/                    # shared across all worktrees
├── .gitignore               # contains: .worktrees/
├── .worktrees/
│   ├── feat-X/              # worktree on branch feat/X
│   ├── fix-prod-bug/        # worktree on branch fix/prod-bug
│   └── feat-design-redo/    # worktree on branch feat/design-redo
└── src/                     # main checkout
```

Why subdirectory + `.gitignore`d: keeps `git status` clean in the main checkout; IDE side-by-side navigation; mirrors branch names predictably (slashes → dashes).

## Quick recipes

```bash
# One-time setup
echo ".worktrees/" >> .gitignore
mkdir -p .worktrees
git add .gitignore && git commit -m "chore: add .worktrees/ convention"

# New branch in a worktree
git worktree add -b feat/foo .worktrees/feat-foo main
cd .worktrees/feat-foo

# Existing remote branch
git fetch origin
git worktree add .worktrees/feat-foo feat/foo

# Cleanup
cd <repo-root>
git worktree remove .worktrees/feat-foo
```

## When to use / NOT use

See [`SKILL.md`](SKILL.md) §When to use + §When NOT to use. Quick rule: if you find yourself running `git stash` more than once a week to context-switch, you want worktrees. If you only work on one branch with no parallel context, you don't need them.

## Cross-skill

- **`finishing-a-development-branch`** invokes `git worktree remove` as part of branch cleanup.
- **`dev-workflow:git-memory`** works identically across worktrees (shared `.git/` means commit trailers don't need special handling).

## What this skill does NOT do

- Does **not** wrap `git worktree` in a custom tool (P3-C). Native command + convention is the whole skill.
- Does **not** auto-create worktrees — user invokes the command.
- Does **not** track worktree count — if you have 20 in flight, prune.

## See also

- [`SKILL.md`](SKILL.md) — operational spec + Red Flags.
- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — invokes worktree cleanup.
- `git help worktree` — canonical reference.
- This repo's `.worktrees/code-toolkit-design/` — worked example of the design-then-build pattern.
