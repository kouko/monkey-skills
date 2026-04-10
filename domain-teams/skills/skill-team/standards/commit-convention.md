# Commit Convention

Defines the 3-commit split pattern, commit message format, and version
bump rules for domain-team skill work.

## Primary Sources

- Conventional Commits spec: https://www.conventionalcommits.org/en/v1.0.0/
- Semantic Versioning 2.0.0: https://semver.org/spec/v2.0.0.html
- Observed precedent: qa-team v4.2.0 (commits `c74a7dc` → `0659365`), docs-team v4.3.0 (`f946875` → `8a13d0b`), devops-team v4.4.0 (`a91efb6` → `f3959af`)

## The 3-Commit Split Pattern

Domain-team refactors that introduce new grounding or significant
structural changes ship in exactly three commits. Each commit is a
self-contained, reviewable unit.

### Commit 1/3 — Standards Foundation

**Commit message**:
```
refactor({team}): adopt {sources} standards (v{X.Y.Z} 1/3)
```

**Contents**:
- CREATE new `standards/*.md` files (primary-source-grounded)
- MODIFY existing `standards/*.md` files to add citations or anchors
- NOTHING else — no protocols, no gates, no SKILL.md changes, no
  version bump, no router updates

**Why first**: standards are the grounding foundation. Everything else
references them, so they must exist before protocols and gates can
cite them.

**Review question**: "Do the new standards cite primary sources and
avoid inventing taxonomies?"

### Commit 2/3 — Protocols and Gates

**Commit message**:
```
refactor({team}): {new-protocols} + {new-gates} (v{X.Y.Z} 2/3)
```

**Contents**:
- CREATE new `protocols/*.md` files (workflow SOPs referencing the
  standards from commit 1)
- MODIFY existing protocols (add phases, citations)
- CREATE new `checklists/*.md` and `rubrics/*.md` files
- MODIFY existing gates (add checks, citations)
- NOTHING else — no SKILL.md changes, no version bump

**Why second**: protocols and gates operationalize the standards. They
can exist with the old SKILL.md still in place (workflows still work,
just with the previous structure).

**Review question**: "Do the protocols guide work correctly, and do
the gates cover the right quality dimensions?"

### Commit 3/3 — SKILL.md Wiring and Version Bump

**Commit message**:
```
refactor({team}): wire {what}, {details}, bump {version} (v{X.Y.Z} 3/3)
```

**Contents**:
- MODIFY `SKILL.md` (persona rewrite, workflow tables, resource manifest)
- MODIFY `using-domain-teams/SKILL.md` (if adding a new team, add router row)
- MODIFY `.claude-plugin/plugin.json` (version bump)
- DELETE any legacy files superseded by new work
- NO new content files here — this is purely wiring

**Why last**: SKILL.md is the entry point. Changing it "activates" the
new structure for Claude's skill discovery. Doing this last ensures
the new structure is already in place when Claude starts using it.

**Review question**: "Does the SKILL.md correctly expose the new
workflows, standards, and gates to the skill dispatch layer?"

## Why 3 Commits (Not 1 or 5)

- **Smaller than 3**: collapsing into 1 commit makes review painful
  (hundreds of lines across many files). Splitting into stages gives
  reviewers natural checkpoints.
- **Larger than 3**: splitting standards into per-file commits
  fragments the narrative. Grouping by stage (foundation → operation →
  wiring) matches how a reviewer reasons about the change.
- **Rollback granularity**: each commit is safely revertible. Revert
  commit 3 → the team keeps its new standards/protocols but returns
  to the old SKILL.md. Revert all three → back to square one.

## Commit Message Format

Follows Conventional Commits subset:

```
<type>(<scope>): <subject> (v<X.Y.Z> <N>/3)
```

- **type**: `refactor` (most common), `feat` (brand-new team),
  `fix` (bug fix), `chore` (version bump only), `docs` (prose only)
- **scope**: kebab-case team name (`qa-team`, `docs-team`) OR
  `domain-teams` for cross-team changes
- **subject**: imperative mood, lowercase, no trailing period
- **`(v<X.Y.Z> <N>/3)` suffix**: required for 3-commit splits;
  identifies the version and the commit position

### Examples

Good:
```
refactor(qa-team): add ISTQB/ISO-29119/JSTQB-aligned standards (v4.2.0 1/3)
refactor(docs-team): Diátaxis quadrant protocols + README/ADR + 5 gates (v4.3.0 2/3)
refactor(devops-team): wire SRE/DORA workflows, fix Monitoring, bump 4.4.0 (v4.4.0 3/3)
```

Bad:
```
Update qa-team                                 # no type or scope
refactor(qa-team): Refactor the skill.         # vague subject
refactor: ISTQB (1/3)                          # no scope
fix(docs-team): typo                           # shouldn't use 3-commit split for a typo
```

## Semver for domain-teams Plugin

The `domain-teams` plugin uses Semantic Versioning 2.0.0 with these
repo-specific interpretations:

| Level | When to bump | Example |
|-------|--------------|---------|
| **PATCH** (x.y.**z**) | Typo fix, single-file clarification, non-structural tweak | `4.4.0 → 4.4.1` |
| **MINOR** (x.**y**.0) | Additive grounding refactor, new workflow, new team, new standards | `4.3.0 → 4.4.0` (devops-team grounding) |
| **MAJOR** (**x**.y.0) | Breaking architectural change (agent contract change, directory restructure) | `3.x.x → 4.0.0` (PR #10 — checkpoint architecture) |

A 3-commit refactor always bumps at least MINOR.

## Branch and PR Conventions

- Branch naming: `refactor/{team-name}-{focus}` for refactors;
  `feat/{team-name}-{feature}` for new teams;
  `fix/{short-description}` for bug fixes
- One PR per 3-commit split (not one PR per commit)
- PR title matches the commit 3/3 subject (or a broader summary)
- PR description: summary of the 3 commits + test/verification plan

## Anti-Patterns

- ❌ Squashing 3 commits into 1 at merge time — loses the review
  structure for git log archaeology
- ❌ Mixing stages: SKILL.md changes in commit 1, standards in commit 2
- ❌ "Fixup" or "wip" commits in the final branch — use interactive
  rebase or just recommit cleanly before pushing
- ❌ Skipping version bump in commit 3 — breaks plugin version tracking
- ❌ Bumping version in commit 1 before the new structure is in place
- ❌ Using `--no-verify` to skip pre-commit hooks (fix the underlying
  issue instead)
- ❌ Force-pushing after PR review has started — use additional
  commits, merge the PR, clean up in follow-up if needed
