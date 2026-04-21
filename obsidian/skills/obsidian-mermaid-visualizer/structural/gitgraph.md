# Git Graph (gitGraph)

Git branch / commit / merge visualization — for explaining branching strategies and release flows.

## When to use

**Best for**:
- Documenting branching strategies (GitFlow / GitHub Flow / trunk-based development)
- Explaining specific release flows (hotfix / feature branch / release branch)
- Teaching git workflows
- Post-mortem analysis of a specific branch history
- Visualizing rebase / merge / cherry-pick workflows

**User query 關鍵字**: git graph / branching / git branches / GitFlow / 分支圖 / 版本分支 / branch strategy / release flow

**Not for**: actual code dependencies (use `structural/class.md`), deployment pipelines (use `flow/flowchart.md`), commit history beyond ~20 commits (use real git log viewer).

## Canonical syntax

```mermaid
gitGraph
    commit
    commit
    branch develop
    checkout develop
    commit
    commit
    checkout main
    merge develop
    commit
```

**Minimum required**:
- `gitGraph` directive
- At least one `commit` statement

Commits happen on the currently-checked-out branch. Default branch is `main`.

## Configuration options

### Branch operations

```mermaid
gitGraph
    commit id: "initial"         # Custom commit ID
    branch feature-x             # Create branch
    checkout feature-x           # Switch to branch
    commit id: "add-auth"
    checkout main                # Switch back
    merge feature-x              # Merge
    commit type: REVERSE          # Revert commit
    commit type: HIGHLIGHT id: "release-v1.0" tag: "v1.0"
```

### Commit options

```mermaid
commit                           # Basic commit
commit id: "abc123"              # Custom ID
commit tag: "v1.2.0"             # Tagged commit
commit type: REVERSE             # Revert (x circle)
commit type: HIGHLIGHT           # Highlighted (larger circle)
```

### Cherry-pick

```mermaid
cherry-pick id: "abc123"         # Cherry-pick a commit by ID
```

### Init configuration

```mermaid
%%{init: { 'gitGraph': {'mainBranchName': 'master'}}}%%
gitGraph
    commit
```

### Orientation

```mermaid
%%{init: { 'gitGraph': {'mainBranchOrder': 0, 'rotateCommitLabel': true}}}%%
gitGraph LR         # Left-to-right (default)
```

Use `gitGraph TB` for top-to-bottom (but renders as LR in some versions).

## Obsidian 11.4.1 compatibility

- **Status**: ✅ Full support — gitGraph is stable across Mermaid versions
- **Known quirks**:
  - Complex diagrams with >5 branches get visually crowded — keep simple
  - Very long commit IDs / tags may overflow — keep concise
  - `gitGraph TB` may still render LR (orientation setting unreliable)
  - Parallel merges from multiple branches can look tangled — render each separately if needed
- **Workaround**: for complex branching, consider splitting into multiple smaller gitGraph diagrams showing different aspects

## Quote rule for gitGraph

Mermaid gitGraph requires quoting on **commit IDs** and **tags** — this is the canonical form and all examples in this file already follow that convention:

- **Commit IDs**: `commit id: "initial"` ✅ (always quoted per Mermaid docs)
- **Tags**: `commit tag: "v1.0"` ✅ (always quoted)
- **Cherry-pick IDs**: `cherry-pick id: "abc123"` ✅ (always quoted)
- **Branch names** (`branch develop`, `checkout develop`): identifiers — unquoted. Branch names are references, not display strings
- **Commit type keywords** (`type: REVERSE`, `type: HIGHLIGHT`): enum values — unquoted

## Worked examples

### Example 1: Simple feature branch workflow

```mermaid
gitGraph
    commit id: "setup"
    commit id: "baseline"
    branch feature-login
    checkout feature-login
    commit id: "add-login-ui"
    commit id: "add-auth-api"
    checkout main
    merge feature-login
    commit id: "release-v1.0" tag: "v1.0"
```

### Example 2: GitFlow (feature + release + hotfix)

```mermaid
gitGraph
    commit id: "init"

    branch develop
    checkout develop
    commit id: "start-dev"

    branch feature-x
    checkout feature-x
    commit id: "work-x"
    commit id: "finish-x"

    checkout develop
    merge feature-x

    branch release-1.0
    checkout release-1.0
    commit id: "rc-prep"
    commit id: "rc-fix"

    checkout main
    merge release-1.0 tag: "v1.0"

    checkout develop
    merge release-1.0

    checkout main
    branch hotfix-1.0.1
    checkout hotfix-1.0.1
    commit id: "hotfix"

    checkout main
    merge hotfix-1.0.1 tag: "v1.0.1"

    checkout develop
    merge hotfix-1.0.1
```

### Example 3: GitHub Flow (trunk-based, short-lived branches)

```mermaid
gitGraph
    commit
    commit

    branch feature-a
    checkout feature-a
    commit
    commit
    checkout main
    merge feature-a tag: "v1.0"

    branch feature-b
    checkout feature-b
    commit
    commit
    checkout main
    merge feature-b tag: "v1.1"

    branch feature-c
    checkout feature-c
    commit
    commit
    checkout main
    merge feature-c tag: "v1.2"
```

### Example 4: Cherry-pick example

```mermaid
gitGraph
    commit id: "A"
    commit id: "B"

    branch feature
    checkout feature
    commit id: "C"
    commit id: "D"
    commit id: "E"

    checkout main
    cherry-pick id: "D"
    commit id: "F"
```

### Example 5: Highlight + revert patterns

```mermaid
gitGraph
    commit
    commit type: HIGHLIGHT id: "critical-fix"
    commit
    commit type: REVERSE id: "revert-critical-fix"
    commit
    commit tag: "v2.0"
```

## Error prevention

| ❌ Wrong | ✅ Right | Reason |
|---|---|---|
| `gitgraph` (lowercase) | `gitGraph` (camelCase) | Directive is case-sensitive |
| `branch featureX && checkout featureX` (shell style) | `branch featureX` then `checkout featureX` on separate lines | Each command on its own line |
| `commit tag v1.0` (no quotes on tag) | `commit tag: "v1.0"` | Tag value needs quotes, with colon |
| `merge featureX id: "foo"` (mixing options) | `merge featureX tag: "v1.0"` or similar | Only certain options valid on merge |
| Implicit branch (no `branch X` declaration) | Declare branch before checkout: `branch featureX` then `checkout featureX` | Can't checkout non-existent branch |
| >5 parallel branches | Simplify or split into multiple diagrams | Visual clutter |
| Long commit IDs | Keep IDs short (<15 chars) | Long IDs overflow the commit dot |

### Pre-save validation

- [ ] `gitGraph` (correct casing) on line 1
- [ ] All branches declared with `branch name` before `checkout`
- [ ] Commit options use `id: "..."` and `tag: "..."` with quotes
- [ ] `merge` statements use branch names that exist
- [ ] Commit count ≤ 20 for readability
- [ ] Parallel branch count ≤ 5
- [ ] Use `type: HIGHLIGHT` and `type: REVERSE` sparingly for emphasis

See also [obsidian-common-quirks.md](../obsidian-common-quirks.md) for universal rules.
