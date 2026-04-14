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
- OPTIONALLY include a single `research/grounding-v{X.Y.Z}.md`
  audit trail for the grounding work (see `grounding-principle.md`
  §The Research Workflow step 4). The research note is the layer-3
  companion to the standards grounding and is inseparable from
  commit 1 by design.
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
- MODIFY `SKILL.md` (persona rewrite, workflow tables, resource
  manifest) — REQUIRED for additive MINOR bumps (grounding refactors,
  brand-new teams); OPTIONAL for modify-only PATCH bumps where
  convention clarification does not require SKILL.md rewiring
- MODIFY `using-domain-teams/SKILL.md` (if adding a new team, add router row)
- MODIFY `.claude-plugin/plugin.json` (version bump)
- MODIFY `CHANGELOG.md` (new `[X.Y.Z]` entry documenting the change)
- DELETE any legacy files superseded by new work
- NO new content files here — this is purely wiring

**Why last**: SKILL.md is the entry point. Changing it "activates" the
new structure for Claude's skill discovery. Doing this last ensures
the new structure is already in place when Claude starts using it.

**Review question**: "Does the SKILL.md correctly expose the new
workflows, standards, and gates to the skill dispatch layer?"

## 2-Commit Variant: Refactor Without New Standards

The canonical 3-commit split assumes the refactor introduces or modifies
grounding in `standards/`. When a refactor touches **no standards files
at all** (all new content is in `protocols/`, `checklists/`, `rubrics/`,
or is pure wiring), the canonical Commit 1/3 ("Standards Foundation")
has no content to hold — forcing a placeholder or stub into it would be
an anti-pattern per `grounding-principle.md`.

For such refactors, use the **2-commit variant**:

### Commit 1/2 — Protocols, Gates, and Research

**Commit message**:
```
refactor({team}): {new-protocols/gates summary} (v{X.Y.Z} 1/2)
```

**Contents**:
- CREATE new `protocols/*.md` files
- MODIFY existing protocols
- CREATE new `checklists/*.md` and `rubrics/*.md` files
- MODIFY existing gates
- OPTIONALLY include a single `research/grounding-v{X.Y.Z}.md` companion
  (rare for no-standards refactors, but permitted)
- NOTHING else — no SKILL.md changes, no version bump, no `standards/`
  additions (which would trip detection into 3-commit mode)

### Commit 2/2 — SKILL.md Wiring and Version Bump

**Commit message**:
```
refactor({team}): wire {what}, bump {version} (v{X.Y.Z} 2/2)
```

**Contents**: identical to canonical Commit 3/3 (SKILL.md +
`.claude-plugin/plugin.json` + `CHANGELOG.md` + optional router update
+ optional legacy deletions). No new content files here.

### When to use the 2-commit variant

Detection rule (also used by the Commit Split Validity gate):

> If `git diff --name-only --diff-filter=A main..HEAD -- '**/standards/*.md'`
> is empty (**no new standards files added** on this branch — modifications
> to existing standards are permitted) → **2-commit variant applies**.
> Otherwise (at least one new standards file added) → canonical **3-commit
> split applies**.

The `--diff-filter=A` restricts the check to added files. Modify-only
standards edits (e.g., this very amendment modifies `commit-convention.md`
in the `standards/` directory of skill-team) stay in 2-commit mode
because no new grounding is introduced. The rationale: 3-commit split's
value is isolating *new grounding* for review; a branch that only
tweaks existing standards text does not need that isolation.

The variant is common for:
- Interaction-layer refactors that add intake protocols + UX checklists
  without touching grounding (e.g., copywriting-team v4.13.0 — intake
  protocol + handoff format + intake-completeness checklist)
- Adding a new MAY/SHOULD gate to an already-grounded team without
  expanding the standards base
- Workflow-tuning refactors that add a new protocol variant referencing
  existing standards

The variant is **NOT** appropriate for:
- Any refactor that adds new standards (→ canonical 3-commit)
- Grounding audits that uncover attribution drift and require standards
  rewrites (→ canonical 3-commit)

### 2-commit bump level

Same rules as 3-commit: MINOR when new runtime files are introduced
(protocols/gates are Read at runtime → MINOR); PATCH when modify-only.
The variant name (`1/2` and `2/2` suffix) is orthogonal to bump level.

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

- **`(v<X.Y.Z> <N>/<N>)` suffix**: position suffix uses the actual
  split size — `N/3` for canonical 3-commit split, `N/2` for the
  2-commit variant (see §2-Commit Variant above). Required for all
  split branches; individual hotfix commits on a 1-commit branch may
  omit the suffix.

### Examples

Good (3-commit):
```
refactor(qa-team): add ISTQB/ISO-29119/JSTQB-aligned standards (v4.2.0 1/3)
refactor(docs-team): Diátaxis quadrant protocols + README/ADR + 5 gates (v4.3.0 2/3)
refactor(devops-team): wire SRE/DORA workflows, fix Monitoring, bump 4.4.0 (v4.4.0 3/3)
```

Good (2-commit variant):
```
refactor(copywriting-team): add intake protocol + handoff format + completeness checklist (v4.13.0 1/2)
refactor(copywriting-team): wire intake into workflows, bump 4.13.0 (v4.13.0 2/2)
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
| **PATCH** (x.y.**z**) | Modify-only convention clarification, policy fix, typo fix, single-file tweak that does not introduce new files or new grounded content | `4.8.0 → 4.8.1` (skill-team research-note convention cleanup) |
| **MINOR** (x.**y**.0) | Additive grounding refactor, new workflow, new team, new standards / protocols / gates, new research-note infrastructure | `4.3.0 → 4.4.0` (devops-team grounding), `4.7.0` (research-note in-repo convention + backfills), `4.8.0` (design-team grounding) |
| **MAJOR** (**x**.y.0) | Breaking architectural change (agent contract change, directory restructure) — requires explicit authorization in the PR description; never applied automatically | `3.x.x → 4.0.0` (PR #10 — checkpoint architecture) |

**Distinguishing rule for PATCH vs MINOR**: does this branch
introduce new files that worker or evaluator agents will Read at
runtime (new standards, protocols, gates, research notes)? Yes →
MINOR. No (only modifies existing runtime files) → PATCH.

**3-commit-split bump level**: the 3-commit split pattern is valid
for either MINOR or PATCH bumps. The split is about review
ergonomics (foundation → operation → wiring), not about bump level.
Historically most 3-commit splits were MINOR grounding refactors,
but v4.6.1, v4.7.1, v4.7.2, and v4.8.1 are all 3-commit PATCH
precedents for skill-team convention cleanups. When SKILL.md
rewiring is not needed (see `### Commit 3/3`), a PATCH-level
3-commit split may ship commit 3 as plugin.json + CHANGELOG only.

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
