# External contracts used by the extractor

Verified against primary upstream documentation during closing-review fixes.
The test dependency pins `git-filter-repo==2.47.0`; callback behavior must be
retested before changing that version.

## git-filter-repo

The [v2.47.0 manual](https://github.com/newren/git-filter-repo/blob/v2.47.0/Documentation/git-filter-repo.txt)
defines these CLI/output contracts:

| Surface | Meaning relied on here |
| --- | --- |
| repeated `--path` | Select the named files/directories; historical renames are not followed automatically. |
| `--prune-empty never` | Disable automatic empty-commit pruning. |
| `--prune-degenerate never` | Preserve degenerate merges rather than automatically pruning them. |
| `--commit-callback` | Execute the supplied Python callback for commits. |
| `--preserve-commit-hashes` | Preserve textual references to old hashes **inside commit messages**. It does not preserve commit identity; rewritten trees/parents still produce new commit IDs. |
| `--force` | Bypass the fresh-clone safety check; history rewrite is destructive within the selected repository. |
| `filter-repo/commit-map` | Header names old/new IDs; order is unspecified; zero new ID means removal. |
| `--version` | Record the installed tool's version identifier in extraction evidence. |

Our use of `--force` is constrained by the new-destination guard, fresh clone,
sanitized Git environment and source snapshot comparison; it is never issued
against the source. This is an implementation safety policy, not an upstream
guarantee about arbitrary wrapper programs.

The callback uses `commit.original_id`, `commit.first_parent()` and
`commit.skip(new_id=...)`. The authoritative [v2.47.0 implementation](https://github.com/newren/git-filter-repo/blob/v2.47.0/git-filter-repo)
defines `original_id` on Commit, returns the first parent or None from
`first_parent`, and records the supplied ID replacement when skipping an
element. Its API compatibility caveat specifically advises pinning/retesting
callback consumers. Callback-skipped IDs being omitted from the raw map is an
observed behavior covered by real integration tests, not an assumption that
all tool versions guarantee omissions. The wrapper preserves raw output and
adds zero rows only for independently classified omitted unrelated commits.

## Git routing and local transport

[Git's environment reference](https://git-scm.com/docs/git#_environment_variables)
documents repository/worktree/index/object-directory routing and executable
lookup overrides. Dropping all inherited `GIT_*` variables prevents those
inputs from overriding the explicit repository selection. The wrapper then
supplies only its controlled environment to **every** Git invocation, including
clone and the environment inherited by filter-repo subprocesses.

[git-config](https://git-scm.com/docs/git-config#ENVIRONMENT) documents
global/system configuration overrides and numbered environment configuration.
The wrapper points global/system files to the null device and supplies only
`core.hooksPath=/dev/null` and an empty `init.templateDir`; this also reaches
Git commands launched inside filter-repo. Config's [core.hooksPath](https://git-scm.com/docs/git-config#Documentation/git-config.txt-corehooksPath)
documents the null-device hook-disabling convention.

[git-clone](https://git-scm.com/docs/git-clone) documents `--no-local` as using
normal Git transport instead of local copy/hardlink optimization, `--no-checkout`
as deferring checkout, and `--template` as selecting template content. Default
clones include tags. Therefore evidence tips use dedicated lightweight tags
`refs/tags/loom-evidence/<original-sha>`; a normal `--no-local` clone regression
verifies these tips survive without a special fetch refspec. Arbitrary archive
refs were rejected because ordinary clones did not transport them.

## Inventory, verification and bootstrap

| Command contract | Official source and use |
| --- | --- |
| `rev-parse --verify <id>^{commit}`; shallow detection | [git-rev-parse](https://git-scm.com/docs/git-rev-parse): validate object type/identity and source completeness before mutation. |
| `rev-list --reverse --topo-order <tips...>` | [git-rev-list](https://git-scm.com/docs/git-rev-list): enumerate the reachable union in ancestry order. |
| `diff-tree --root -m --no-renames -r -z --name-only` | [git-diff-tree](https://git-scm.com/docs/git-diff-tree): inventory root and per-parent changes with NUL-delimited paths. |
| `ls-tree -r -z` | [git-ls-tree](https://git-scm.com/docs/git-ls-tree): compare mode, object ID and path for every retained tree. |
| `show -s --format=...`; `show <revision>:<path>` | [git-show](https://git-scm.com/docs/git-show): read identities/dates/messages and committed citation content. |
| local `fetch --no-tags <source> <fixed-id>` | [git-fetch](https://git-scm.com/docs/git-fetch): obtain exactly selected objects without importing source tags. |
| `update-ref`, including `-d` | [git-update-ref](https://git-scm.com/docs/git-update-ref): set evidence tags and remove extraneous refs only in the fresh destination. |
| `checkout -B main <fixed-id>` | [git-checkout](https://git-scm.com/docs/git-checkout): pin the new clone's branch/worktree to the selected source. |
| `remote remove origin` | [git-remote](https://git-scm.com/docs/git-remote): remove the clone's local remote configuration; no server mutation. |
| `archive <mapped-id> <path>` | [git-archive](https://git-scm.com/docs/git-archive): materialize the historical hook for actual baseline recomputation. |
| `add` and `commit` | [git-add](https://git-scm.com/docs/git-add), [git-commit](https://git-scm.com/docs/git-commit): record only the explicit bootstrap/provenance files in a separate candidate commit. |

Snapshot diagnostics use read-only [show-ref](https://git-scm.com/docs/git-show-ref),
`config --local --list`, [status --porcelain=v1](https://git-scm.com/docs/git-status)
and [diff HEAD --binary](https://git-scm.com/docs/git-diff); these are safety observations,
not authorization to alter source refs, configuration, index or worktree.
