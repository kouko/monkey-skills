# Protocol: Skill Brainstorming

**When to use**: the trigger for the task is ambiguous — "can you
improve the code-team?" or "I want a new team for X". Run this before
committing to `new-skill-creation` or `skill-redesign`.

**Output**: a scope decision document (Skill Scope Brief) that
answers: trigger type, estimated file delta, needs research, commit
split estimate.

## Phase 1: Identify Trigger

Categorize the user's request into one of:

| Trigger | Description | Route to |
|---------|-------------|----------|
| **Brand-new team** | Domain not yet covered by any existing team | `new-skill-creation.md` |
| **Grounding refactor** | Existing team lacks primary-source grounding | `skill-redesign.md` |
| **Workflow addition** | Existing team needs a new workflow / protocol | `skill-redesign.md` (smaller scope) |
| **Gate addition** | Existing team needs a new quality gate | `skill-redesign.md` (smaller scope) |
| **Minor update** | Typo fix, single-file clarification | No protocol needed, direct edit |

If the user's request doesn't fit any category cleanly, treat it as
a hybrid and ask the user to clarify which aspects matter most.

## Phase 2: Scope Check

Assess whether the work fits in one skill-team execution or needs
decomposition.

Signals that scope is too large:
- The request touches more than one team
- The request includes both new standards AND a new workflow AND new gates (all three)
- The estimated file delta exceeds 15 new/modified files
- The user is also asking for cross-team restructuring

If scope is too large:
- Decompose into multiple smaller tasks
- Invoke skill-team per task, not as one mega-task
- Present the decomposition to the user for approval

## Phase 3: Grounding Assessment

Determine whether primary-source research is required.

Research is required when:
- The task introduces new taxonomies, categories, or frameworks
- Existing content in the skill invents load-bearing claims
- A named industry standard (SRE, Diátaxis, ISTQB, …) should ground the work
- The user asks for "best practices" without specifying the source

Research is NOT required when:
- The task is mechanical (rename, file reorganization, typo fix)
- The task only adds gates to already-grounded content
- The user has already supplied primary sources in the request

If research is required → route to `grounding-research.md` before
continuing to new-skill-creation or skill-redesign.

## Phase 4: Produce the Skill Scope Brief

Output a concise brief to the main agent or user:

```markdown
## Skill Scope Brief

**Target**: {team-name}
**Trigger**: {brand-new team | grounding refactor | workflow addition | gate addition | minor update}
**Decomposition needed**: {yes | no; if yes, list the sub-tasks}
**Research required**: {yes | no; if yes, what question(s)}
**Estimated file delta**:
- CREATE: {list of new files}
- MODIFY: {list of files to change}
- DELETE: {list of files to retire}
**Estimated commit split**: {3-commit | 1-commit | N-commit with rationale}
**Recommended next protocol**: {new-skill-creation | skill-redesign | grounding-research}
**Open questions for user**: {list, or "none"}
```

## Rules

- Prefer honest "I don't know enough" over guessing. If the user's
  request is underspecified, surface the gap in "Open questions".
- A "minor update" never needs the 3-commit split — direct edit is
  fine.
- A "brand-new team" always needs research unless the user brings
  their own primary sources.
- Never silently reclassify the user's request — always surface the
  categorization to them for confirmation.
