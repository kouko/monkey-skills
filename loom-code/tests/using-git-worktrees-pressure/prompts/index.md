# using-git-worktrees-pressure — expected behavior per prompt

Each `.txt` stresses the worktree-vs-alternative trade-off. Acceptance: 2 of 2 handled correctly.

---

## `just-stash-and-switch.txt`

The stash-and-switch rationalization — the classic friction worktrees exist to remove.

| Acceptance | Rule |
|---|---|
| MUST | Push back on stash-as-default. Cite §Red Flags row 1 — *"if you find yourself running git stash more than once a week to context-switch, you want a worktree."* The stash-pop loop loses IDE state + build artifacts + open-file state; stash conflicts are a recurring sharp edge. |
| MUST | Offer the worktree alternative: `git worktree add -b fix/prod-bug-2026-05 .worktrees/fix-prod-bug main` — feature/csv-export checkout stays intact; fix happens in a second checkout; close the worktree when done. |
| MAY | Acknowledge stash is fine for genuine one-off context switches (< once / week); the discipline kicks in when stash becomes the default escape hatch. |
| MUST | Offer to run the worktree setup command if user confirms. |
| MUST NOT | Silently approve the stash flow as the standard answer. |

---

## `just-clone-twice.txt`

The second-clone rationalization — assumes isolation requires duplication.

| Acceptance | Rule |
|---|---|
| MUST | Refuse second-clone as the default. Cite §Red Flags row 3 — *"Full clone = duplicated .git/ + de-synced refs + duplicated hooks + duplicated config. All the cost, none of the sharing."* |
| MUST | Compare worktree vs second-clone explicitly: shared `.git/` (one source of truth for refs / branches / hooks / config); per-worktree cost is just the checked-out file tree (which a clone would need anyway). |
| MUST | Offer the worktree setup: `.worktrees/v2-redesign/` for the long-running branch, main checkout stays for parallel work. Cite this very repo as the worked example (this branch IS in `.worktrees/loom-code-design/`). |
| MAY | Note the legitimate second-clone case: you need a fresh `.git/` (e.g. permission test, fork-style isolation). The "long-running parallel branches" case is NOT it. |
| MUST NOT | Recommend `git clone` for "I want parallel branches" — that's worktree's exact use case. |
