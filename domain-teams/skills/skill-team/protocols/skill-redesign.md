# Protocol: Skill Redesign

**When to use**: an existing domain-team skill needs grounding or
structural improvement. The dominant use case — e.g. qa-team v4.2.0,
docs-team v4.3.0, devops-team v4.4.0 refactors.

**Output**: a redesigned skill with new/updated standards + protocols
+ gates + SKILL.md, in 3 atomic commits ready for PR.

Grounds on: all 6 `../standards/*.md`.

## Phase 1: Gap Assessment

Read the target skill's current state:

```
domain-teams/skills/{team-name}/
├── SKILL.md               ← read in full
├── standards/             ← inventory
├── protocols/             ← inventory
├── checklists/            ← inventory
└── rubrics/               ← inventory
```

Produce a gap report answering:

- **Load-bearing claims without citations**: list every taxonomy,
  definition, threshold, or framework that isn't traced to a primary
  source
- **Structural gaps**: missing required SKILL.md sections, broken
  workflow phases (marked `--`), missing agent launch templates
- **Anti-pattern occurrences**: inlined content, absolute paths,
  stale deprecation stubs, nested subdirectories
- **Line budget status**: is SKILL.md approaching 500 lines?
- **JP integration status**: does the current JP content match the
  content-density rule?

The gap report is the source of truth for what this redesign will fix.

## Phase 2: Research

Run `grounding-research.md` for every load-bearing claim cluster
identified in phase 1.

Output: a grounding plan mapping gaps → standards files to create or
modify → primary sources.

Skip this phase only if the redesign is purely structural (no new
grounding needed). Rare.

## Phase 3: Delta Planning

From the gap report + grounding plan, build a precise file delta:

```markdown
## Redesign Delta

**CREATE**:
- standards/{new-standard-1}.md
- standards/{new-standard-2}.md
- protocols/{new-protocol}.md
- checklists/{new-gate}.md

**MODIFY**:
- standards/{existing-standard}.md — add citations, link to new standards
- protocols/{existing-protocol}.md — add phase N, cite primary sources
- checklists/{existing-gate}.md — add CHK-X-00N item
- SKILL.md — persona rewrite, workflow updates, resource manifest expansion

**DELETE**:
- standards/{legacy-standard}.md — superseded by new grounding
```

Assign each entry to one of the three commits:
- Commit 1: all CREATE/MODIFY in `standards/`
- Commit 2: all CREATE/MODIFY in `protocols/`, `checklists/`, `rubrics/`
- Commit 3: SKILL.md, router updates, version bump, DELETE ops

## Phase 4: Commit 1 Execution — Standards Foundation

Execute all `standards/` operations from the delta:

1. CREATE each new standard (follow `../standards/skill-md-structure.md`
   Primary Sources + body + Anti-Patterns structure)
2. MODIFY each existing standard (add citations, cross-link to new
   standards, preserve existing voice)
3. Write all files, verify with Read
4. Stage with `git add domain-teams/skills/{team-name}/standards/`
5. Commit with the message format from
   `../standards/commit-convention.md`:

```
refactor({team-name}): adopt {sources} standards (v{X.Y.Z} 1/3)
```

## Phase 5: Commit 2 Execution — Protocols and Gates

Execute all `protocols/`, `checklists/`, `rubrics/` operations:

1. CREATE new protocols — each references standards from commit 1
2. MODIFY existing protocols — add phases, citations
3. CREATE new gates (checklists + rubrics)
4. MODIFY existing gates — add checks, citations
5. Stage and commit:

```
refactor({team-name}): {new-protocol} + {new-gate} + {details} (v{X.Y.Z} 2/3)
```

## Phase 6: Commit 3 Execution — SKILL.md Wiring and Version Bump

Execute the wiring operations:

1. MODIFY `SKILL.md`:
   - Persona rewrite (anchor on primary sources)
   - Workflow tables reflect new protocols
   - Resource Manifest expanded with new standards
   - Agent Launch templates updated with new standards array
2. MODIFY `using-domain-teams/SKILL.md` only if routing needs to change
3. MODIFY `domain-teams/.claude-plugin/plugin.json` (MINOR bump)
4. DELETE any legacy files superseded by new work
5. Stage and commit:

```
refactor({team-name}): wire {what}, {details}, bump {version} (v{X.Y.Z} 3/3)
```

## Phase 7: Dogfood Verification

Run the skill-team's own gates against the redesigned skill:

1. `checklists/skill-completeness-checklist.md` on the modified SKILL.md
2. `checklists/commit-split-checklist.md` on the 3 commits (git log)
3. `rubrics/primary-source-grounding.md` on the new / modified standards
4. `rubrics/skill-coherence.md` on the complete skill

If any gate returns NEEDS_REVISION → fix and amend the relevant
commit (or create a follow-up commit within the same PR). Do NOT
open the PR with failing gates.

## Phase 8: PR Preparation

1. Push the branch: `git push -u origin refactor/{team-name}-{focus}`
2. Open a PR titled matching commit 3/3 subject (or a broader summary)
3. PR body summarizes the 3 commits + lists the primary sources
   adopted + test/verification plan
4. Assign reviewers, wait for merge

## Rules

- Never rewrite all 3 commits in one file — the split IS the
  reviewability guarantee
- If you discover during commit 2 that a standard needs a change,
  amend commit 1 BEFORE commit 2 lands (don't accumulate mid-PR drift)
- Version bump is always in commit 3, never in 1 or 2
- Legacy file deletions happen in commit 3, after new content is fully
  wired

## Anti-Patterns

- ❌ Skipping phase 1 (gap assessment) and "just refactoring based on
  memory" — always read the current state first
- ❌ Merging stages: putting protocol work in commit 1 or SKILL.md
  updates in commit 2
- ❌ Running dogfood after opening the PR — surface failures before
  reviewer time is spent
- ❌ Deleting legacy files in commit 1 — new content must land first
- ❌ Modifying `using-domain-teams/SKILL.md` unnecessarily — only
  touch it if routing actually changes
