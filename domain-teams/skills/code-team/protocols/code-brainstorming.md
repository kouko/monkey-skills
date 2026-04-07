# Code Brainstorming Protocol

Understand intent, explore approaches, and confirm direction before
implementation. Core principles from superpowers:brainstorming adapted
for code engineering: one question at a time, propose 2-3 approaches,
YAGNI ruthlessly, AI proposes human decides.

## Protocol

### Phase 0: Context Discovery

1. **Clarify intent**: What are we trying to achieve, why, and what
   does success look like? Ask one question at a time, prefer
   multiple choice when possible.
2. **Scan codebase**: Explore related code, existing patterns, and
   reusable implementations. Do not propose approaches before
   reading existing code.
3. **Identify constraints**: Technical constraints (language,
   framework, compatibility), team conventions, performance
   requirements, and hard boundaries.

### Phase 1: Approach Exploration

4. **Generate 2-3 approaches**: Propose with trade-offs. Even when
   one seems obvious, show alternatives and explain why they're
   less suitable.
5. **Trade-off matrix**: Compare each approach on:
   - Complexity (implementation cost)
   - Maintainability (ease of future changes)
   - Risk (blast radius on existing code)
   - Effort (scope size, not time estimates)
6. **YAGNI check**: Strip unnecessary features and premature
   abstractions from each approach. "Might need it later" is a
   reason to remove, not to keep.

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
- YAGNI ruthlessly — eliminate abstractions for hypothetical
  future requirements
- AI presents options and recommendations; human decides
- Skip this protocol for small bug fixes and cosmetic changes
  (comments, formatting, renames)
- Early questions are cheaper than late rework — resolve ambiguity
  before moving forward

## Output Format

1. **Intent Summary**: Purpose and success criteria
2. **Codebase Context**: Related existing code, patterns, dependencies
3. **Approach Comparison**: 2-3 approaches with trade-off table
4. **Selected Direction**: Chosen approach with scope boundary
5. **Architect Handoff**: Structured input for `feature-dev:code-architect`
   (Intent, Constraints, Approach, Scope)
