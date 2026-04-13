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
- **Token budget status**: is SKILL.md approaching ~6,000 tokens?
- **JP integration status**: does the current JP content match the
  content-density rule?

The gap report is the source of truth for what this redesign will fix.

## Phase 1 Variant: Post-Grounding Expansion Track (added v4.11.0)

**When to use this track instead of the full Phase 1 → Phase 7 path**:

The target skill is already grounded AND you are doing an **additive
expansion**, not a re-grounding or workflow repair:

1. The target skill already has a `research/grounding-v{X.Y.Z}.md`
   file (prior grounding completed) OR has load-bearing claims
   already grounded in standards/ from a previous refactor
2. You are **adding new frameworks** to the existing grounding —
   not re-grounding existing frameworks, and not fixing broken
   workflows
3. The new frameworks naturally fit the existing scale / tier
   structure, OR the refactor introduces a new scale-hierarchy
   split of existing content (see `../standards/file-conventions.md
   §Standards Splitting Discipline §Scale-hierarchy decision rule`)

This is the **post-grounding expansion scenario**. research-team
v4.11.0 was the first precedent: research-team was grounded in
v4.9.0, v4.10.x shipped incremental PATCHes, and v4.11.0 expanded
investment analysis by adding 5 new frameworks (Hedgeye GIP / MMT /
RAI / Taleb Barbell / Fama-French) AND splitting the monolithic
canon into 4 scale-based files (L1 macro / L2 sector / L3 security
/ portfolio meta).

### Streamlined Phase 1 (post-grounding expansion only)

Instead of the full gap-assessment path:

1. **Read the existing `standards/` inventory** to understand what
   grounding is already in place. Do NOT re-scan for "load-bearing
   claims without citations" — prior grounding closed that gap
   already.
2. **Identify the new-framework gap** — list the frameworks to add
   (e.g., "Hedgeye GIP, MMT, RAI, Taleb Barbell, Fama-French are
   not yet covered"). This is a much narrower scan than full gap
   assessment.
3. **Classify each new framework** — by layer (if the target uses
   scale-hierarchy), by tier, or by topic. Example from v4.11.0:
   "Hedgeye GIP / MMT / RAI → L1 macro; Fama-French → L2 sector;
   Barbell + Risk Parity → Portfolio meta".
4. **Decide split vs extend**:
   - If new frameworks fit existing files → MODIFY existing
     standards (extend in place)
   - If new frameworks + existing content require a scale-hierarchy
     split → CREATE new layer files + DELETE the retired monolith
     (the v4.11.0 pattern)
5. **Skip the broken-workflow scan** — no broken workflows, just
   additive expansion
6. **Skip the JP integration strategy re-decision** unless a new
   framework surfaces JP content (e.g., v4.11.0's MMT Japan debate
   section + Taleb Barbell JP terminology trap). Otherwise,
   inherit the existing team's JP strategy.

### Output of streamlined Phase 1

A narrow new-framework list + layer-split decisions + delta plan —
NOT a full gap report. Typical output is 1-2 pages.

### Jump to Phase 2b (not Phase 2)

Post-grounding expansion with **3+ new frameworks** should use
`grounding-research.md §Phase 2b: Multi-Cluster Parallel Research`
instead of the sequential Phase 2 research-team launch. Parallel
research is faster and more thorough for additive multi-framework
scenarios.

With only 1-2 new frameworks, regular Phase 2 is fine.

### Why this track is distinct

Initial grounding and post-grounding expansion are qualitatively
different refactor types:

| | Initial grounding | Post-grounding expansion |
|---|---|---|
| **Target state** | Ungrounded or partially grounded team | Already-grounded team |
| **Phase 1 focus** | Full gap assessment (structural + citation + JP) | Narrow new-framework gap |
| **Phase 2 launch** | Single sequential research-team | Phase 2b parallel (if 3+ frameworks) |
| **File operations** | Mostly CREATE new standards | Mix: CREATE (new layer files) + DELETE (retired monoliths) + MODIFY (extend existing) |
| **Version bump** | Usually MINOR (many new runtime files) | MINOR or PATCH depending on whether any new files are read at runtime |
| **Dogfood gates** | All 4 triggered | All 4 triggered (same) |
| **Typical precedent** | qa v4.2 / docs v4.3 / devops v4.4 / code v4.6 / design v4.8 / research v4.9 / planning v4.10 | research v4.11.0 (first instance) |

Both tracks converge at Phase 3 (Delta Planning) and proceed
identically through Phases 4-8. Only Phase 1 and the Phase 2 launch
differ.

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
