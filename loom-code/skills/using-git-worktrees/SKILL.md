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

`git worktree` gives one repo parallel branch directories: one `.git/` shared
across N checkouts, each on its own branch. It preserves builds and IDE state
without stash conflicts or duplicate clones, while sharing refs, hooks, and
objects.

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

Use `.worktrees/<branch-slug>/` under repo root; ignore `.worktrees/` so its
checkouts never appear untracked. Slug branch names predictably (`feat/X` →
`feat-X`). Before creating, run `git check-ignore .worktrees/`; nonzero stops setup — add and commit `.worktrees/` in `.gitignore` first. Then run `git worktree list`; refuse an existing path or a branch already attached to a worktree, but allow an existing unattached branch. Concurrent sessions use
one worktree and one branch per concurrent session — never share either.

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
Always confirm before removing a worktree; never discard another session's state.

File operations inside a worktree have sharp edges (e.g. renaming an untracked just-written file needs plain `mv`, not `git mv`) — see [`environment-gotchas`](../using-loom-code/references/environment-gotchas.md).

## Cross-skill contract

| Direction | Skill | Role |
|---|---|---|
| **Upstream invocation** | User starting a parallel branch | Direct user invocation |
| **Upstream invocation** | `brainstorming` produces a brief that explicitly says "this will be a long-running design phase" | Optional — recommend worktree for the design phase |
| **Downstream** | `finishing-a-development-branch` | When closing a branch that lives in a worktree, finishing-a-branch's cleanup phase invokes this skill's `git worktree remove` flow |
| **Lateral** | `loom-workflow:git-memory` | Worktrees share the same `.git/`; git-memory's commit-trailer mechanism works identically across worktrees (no special handling needed) |

## Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"I'll just stash and switch."* | Repeated switching loses state and risks conflicts. | Use one worktree. |
| *"Disk space is precious."* | Only the file tree is duplicated; `.git/` is shared. | Clone only when separate Git state is required. |
| *"I'll clone the repo a second time."* | Clones duplicate `.git/`, refs, hooks, and config. | Use a worktree. |
| *"Worktrees are confusing."* | Setup is one-time. | Follow §The `.worktrees/` convention. |
| *"My IDE doesn't handle worktrees well."* | Each directory is an ordinary workspace. | Open that directory directly. |
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
