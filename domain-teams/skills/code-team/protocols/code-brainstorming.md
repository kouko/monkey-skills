# Code Brainstorming Protocol

Understand intent, explore approaches, and confirm direction before
implementation. Core discipline: one question at a time, propose 2-3
approaches, YAGNI ruthlessly, AI proposes human decides.

## Primary Sources

- **Hunt, A. & Thomas, D. (2019)** *The Pragmatic Programmer: Your
  Journey to Mastery, 20th Anniversary Edition*, Addison-Wesley.
  ISBN 978-0135957059. Ch.2 topics grounding this protocol:
  - Topic "The Essence of Good Design (ETC — Easier to Change)" —
    the meta-principle that justifies every trade-off dimension
    below. Good design is design that is easier to change.
  - Topic "Tracer Bullets" — build a minimal end-to-end working
    version to validate an approach before committing to it.
  - Topic "Prototypes and Post-it Notes" — throw-away experiments
    to answer one specific design question.
  > Citation honesty: Pragmatic Programmer 20th anniv. publicly
  > enumerates Topic numbers only for Ch.2 (Topics 8–15). This
  > protocol cites Ch.2 topics by title; topics in other chapters
  > are referenced without a numeric Topic ID.
- **Fowler, M.** bliki "Yagni" —
  https://martinfowler.com/bliki/Yagni.html — authoritative source
  for the "You Ain't Gonna Need It" principle as applied by modern
  XP/agile practice. YAGNI does not forbid *thinking* ahead; it
  forbids *building* speculative capability.
- Team standard: `standards/pragmatic-principles.md` consolidates
  DRY / ETC / Orthogonality / Tracer Bullets / YAGNI / Rule of
  Three / KISS for code-team and is the authoritative reference
  for this protocol's principle vocabulary.

## Protocol

### Phase 0: Context Discovery & Shared Understanding

#### Step 1: Clarify intent

1. **Ask intent**: What are we trying to achieve, why, and what
   does success look like? Ask one question at a time, prefer
   multiple choice when possible. Keep this brief (1-2 questions)
   to establish direction before exploring code.

#### Step 2: Explore codebase

2. **Scan codebase**: Explore related code, existing patterns, and
   reusable implementations. Do not propose approaches before
   reading existing code.
3. **Identify constraints**: Technical constraints (language,
   framework, compatibility), team conventions, performance
   requirements, and hard boundaries.

#### Step 3: Grill — challenge assumptions

Using codebase findings, question the user's intent and assumptions
to reach shared understanding. One question at a time. For each
question, provide your recommended answer.

4. **Challenge assumptions**: "You said X, but the codebase shows Y
   — is that intentional?" Surface contradictions between user's
   stated intent and existing code reality.
5. **Probe dependencies**: "If we change X, it affects Y and Z —
   have you considered that?" Walk down each branch of the decision
   tree, resolving dependencies one by one.
6. **Test boundaries**: "What should happen when [edge case]?" Push
   on unstated requirements and implicit expectations.
7. **Explore the codebase** instead of asking, when a question can
   be answered by reading code.

Continue until no unresolved branches remain, or the user requests
to move on. Do not set a fixed question limit — the depth of
questioning should match the complexity of the task.

#### Step 4: Understanding Summary

8. **Produce Understanding Summary** and ask user to confirm before
   proceeding to Phase 1:

```
## Understanding Summary

### Intent
[What we're building and why]

### Key Constraints
[Technical, team, and scope constraints]

### Confirmed Assumptions
[Assumptions validated during grill]

### Resolved Ambiguities
[Questions that were unclear but now resolved]
```

Skip Phase 0 Steps 3-4 for small bug fixes and cosmetic changes
(comments, formatting, renames) — proceed directly to Phase 1.

### Phase 1: Approach Exploration

4. **Generate 2-3 approaches**: Propose with trade-offs. Even when
   one seems obvious, show alternatives and explain why they're
   less suitable.
5. **Trade-off matrix**: Compare each approach on the four
   code-team dimensions below. These dimensions are a **house
   convention** inspired by Pragmatic Programmer's ETC
   meta-principle (Ch.2 "The Essence of Good Design") and the
   cost-value framing found throughout Ch.2 — they are not an
   independent taxonomy and are not claimed to be exhaustive. See
   `standards/pragmatic-principles.md` §"Trade-off Dimensions" for
   the fuller list code-team maintains.
   - Complexity (implementation cost)
   - Maintainability (ease of future changes — ETC)
   - Risk (blast radius on existing code)
   - Effort (scope size, not time estimates)
6. **YAGNI check**: Strip unnecessary features and premature
   abstractions from each approach. Per Fowler bliki "Yagni":
   "Might need it later" is a reason to remove, not to keep. Design
   for change (ETC), but implement for today.

### Phase 2: Direction Confirmation

7. **Recommend**: Present your recommended approach with reasoning.
8. **User selects**: AI presents options, human makes final call.
   Provide enough information for an informed decision.
9. **Scope boundary**: State explicitly what is IN scope and what
   is OUT of scope. Out-of-scope items may be logged as future
   tasks but are not implemented now.
10. **Handoff summary**: Structure the selected approach as input
    for the architect plugin (Intent, Constraints, Approach, Scope).

## Rules

- One question at a time, multiple choice preferred
- Do not propose approaches before exploring existing code —
  complete Phase 0 before Phase 1
- During grill (Step 3): provide your recommended answer with each
  question — don't just ask, also propose
- If a question can be answered by exploring the codebase, explore
  the codebase instead of asking the user
- Understanding Summary must be confirmed by user before Phase 1
- YAGNI ruthlessly — eliminate abstractions for hypothetical
  future requirements
- AI presents options and recommendations; human decides
- Skip Phase 0 grill (Steps 3-4) for small bug fixes and cosmetic
  changes (comments, formatting, renames)
- Early questions are cheaper than late rework — resolve ambiguity
  before moving forward

## Output Format

1. **Intent Summary**: Purpose and success criteria
2. **Codebase Context**: Related existing code, patterns, dependencies
3. **Approach Comparison**: 2-3 approaches with trade-off table
4. **Selected Direction**: Chosen approach with scope boundary
5. **Architect Handoff**: Structured input for `feature-dev:code-architect`
   (Intent, Constraints, Approach, Scope)
