---
name: using-git-worktrees
description: |
  Use for parallel branches at once — features in flight, long experiments, design-then-build cycles outliving a session. Fires on 'work on X while keeping main', 'worktree for the redesign'. Uses git worktree; refuses 'just stash and switch'.
version: 0.9.0
---

<SUBAGENT-STOP>
If you are a subagent dispatched with an explicit role prompt, the parent orchestrator already chose worktree workflow. Follow your dispatched prompt directly.
</SUBAGENT-STOP>

## What git worktrees solve

`git worktree` lets one repo have multiple checked-out branches in separate directories simultaneously. Without worktrees, the choices are:

1. **Branch-switch with stash** — `git stash` your work, `git switch other-branch`, do work, `git switch back`, `git stash pop`. Loses the running build artifacts, IDE state, open files. Stash conflicts are a recurring sharp edge.
2. **Multiple clones** — `git clone` the repo into a second directory. Costs disk space (full `.git/` × N) and de-syncs (each clone has its own remote refs, branch list, hooks).
3. **Just don't context-switch** — works until reality forces a switch (production bug while feature is in flight).

`git worktree` is a fourth option: one `.git/` shared across N checkouts in N directories, each on its own branch. Cheap to create (no full clone); cheap to destroy (just delete the directory + `git worktree prune`); fully synced (one remote, shared hooks, shared object store).

## When to use

| Scenario | Use worktree? |
|---|---|
| Feature branch in flight + production bug fix needed | ✅ Yes — worktree for the bug fix, keep feature checkout intact |
| Long-running experiment / design exploration | ✅ Yes — design lives in `.worktrees/feat-design-X/`; main checkout stays clean |
| `loom-code`-style design-then-build (this repo's own pattern) | ✅ Yes — design phase in worktree (this repo's `.worktrees/loom-code-design/` is the example) |
| Comparing implementations of the same task across branches | ✅ Yes — two worktrees side-by-side, run `git diff` between them |
| Single branch, no context switching needed | ❌ No — just work on the main checkout |
| Trivial branch (one-line typo fix) | ❌ No — overhead > value; just commit on main |
| You need a fresh `.git/` (e.g. permission test, fork-style isolation) | ❌ No — `git worktree` shares `.git/`; you want `git clone` |

## When NOT to use

| Exempt category | What qualifies | What does NOT qualify |
|---|---|---|
| **No parallelism needed** | One branch, no concurrent work, no long-running experiment | "I might want to switch later" — speculation; create worktree when you actually need it |
| **Shared filesystem only** | Worktree across a slow network filesystem (NFS, SMB) — slow file ops compound across N worktrees | A local SSD — worktree cost is negligible |
| **Submodule-heavy repo** | Worktree + submodules has historical sharp edges (git < 2.25); modern git handles it but verify before committing to the workflow | Vanilla repo without submodules |

## The `.worktrees/` convention

This repo uses (and recommends) the `.worktrees/<branch-slug>/` subdirectory pattern:

```
repo-root/                   # main checkout, default branch
├── .git/                    # shared across all worktrees
├── .gitignore               # contains: .worktrees/
├── .worktrees/              # excluded from git, holds worktree checkouts
│   ├── feat-X/              # worktree on branch feat/X
│   ├── feat-Y/              # worktree on branch feat/Y
│   └── fix-prod-bug-2026-05/  # worktree on branch fix/prod-bug-2026-05
└── src/                     # main checkout's files
```

Why this layout:

- **`.worktrees/` is `.gitignore`'d** — checkouts don't show up as untracked in the main checkout's `git status` (they would otherwise — git sees them as random directories).
- **Subdirectory of repo root** — finder/explorer/IDE side-by-side navigation; easy to glob (`ls .worktrees/`) all in-flight branches.
- **Slug-named** — `feat/X` becomes `feat-X/` (slashes → dashes). Mirrors branch name predictably.

### Initial setup (one-time per repo)

```bash
# Add to .gitignore
echo ".worktrees/" >> .gitignore
mkdir -p .worktrees
git add .gitignore
git commit -m "chore: add .worktrees/ convention"
```

### Creating a new worktree

```bash
# For a new branch off main
git worktree add -b feat/foo .worktrees/feat-foo main

# For an existing branch (someone else pushed it; you want to work on it locally)
git fetch origin
git worktree add .worktrees/feat-foo feat/foo

# Then cd into it
cd .worktrees/feat-foo
```

### Removing a worktree

```bash
# When the branch is merged or abandoned
cd <repo-root>
git worktree remove .worktrees/feat-foo

# If the directory was already deleted manually
git worktree prune
```

`git worktree remove` refuses if the worktree has uncommitted changes — that's a feature, not a bug. Force with `--force` only if you've verified the changes are intentional throwaways.

## Cross-skill contract

| Direction | Skill | Role |
|---|---|---|
| **Upstream invocation** | User starting a parallel branch | Direct user invocation |
| **Upstream invocation** | `brainstorming` produces a brief that explicitly says "this will be a long-running design phase" | Optional — recommend worktree for the design phase |
| **Downstream** | `finishing-a-development-branch` | When closing a branch that lives in a worktree, finishing-a-branch's cleanup phase invokes this skill's `git worktree remove` flow |
| **Lateral** | `dev-workflow:git-memory` | Worktrees share the same `.git/`; git-memory's commit-trailer mechanism works identically across worktrees (no special handling needed) |

## Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"I'll just stash and switch."* | Repeated stash/switch is the friction worktrees exist to remove. If you're stashing more than once a week to context-switch, you want a worktree. | Set up worktree once; no more stash-and-switch loop. |
| *"Disk space is precious."* | Worktree shares `.git/`; per-worktree cost is just the checked-out file tree (which you'd need anyway). Cheap. | The cost is the file tree, not duplicated `.git/`. Worry about disk space only if your repo's working tree is multi-GB. |
| *"I'll clone the repo a second time."* | Full clone = duplicated `.git/` + de-synced refs + duplicated hooks + duplicated config. All the cost, none of the sharing. | Use worktree; it's the same outcome with shared state. |
| *"Worktrees are confusing."* | One-time setup learning curve; long-term reduces switching friction. Same pattern this very repo uses. | Walk the §The .worktrees/ convention section once; then it's just `git worktree add`. |
| *"My IDE doesn't handle worktrees well."* | Most modern IDEs do (VS Code, JetBrains, Vim, Emacs). If yours doesn't, open the worktree directory as its own workspace — not the repo root. | Treat each worktree as its own workspace; the IDE never knows it's a worktree. |
| 「stash でいい / 用 stash 就好」 | Same rationalization, localized. | Same refusal — worktree for ongoing parallelism. |

## What this skill does NOT do

- Does **not** wrap `git worktree` in a custom tool. Per P3-C, the discipline is native `git worktree` + a documented `.worktrees/` convention. Wrappers add abstraction without value.
- Does **not** auto-create worktrees. The user invokes `git worktree add` themselves (or asks the agent to run the command); this skill provides the convention + guard rails.
- Does **not** sync worktree state. Each worktree has its own checkout; the user / git handles refs.
- Does **not** track worktree count. If you have 20 worktrees in flight, that's a workflow problem this skill cannot solve. Prune aggressively.

## See also

- [`../finishing-a-development-branch/SKILL.md`](../finishing-a-development-branch/SKILL.md) — invokes `git worktree remove` as part of branch cleanup.
- [`../using-loom-code/SKILL.md`](../using-loom-code/SKILL.md) — router; this skill is auxiliary (no specific Skill Priority stage; available on demand).
- Git documentation: `git help worktree` — the canonical reference for the underlying command.
- This very repo's `.worktrees/loom-code-design/` directory — worked example of the design-then-build pattern.
