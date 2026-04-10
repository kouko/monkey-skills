# DevOps Brainstorming Protocol

Understand infrastructure intent, explore approaches, and confirm
direction before building configs. Core principles: one question at a
time, propose 2-3 approaches, prefer boring infrastructure over clever
infrastructure, AI proposes human decides.

## Protocol

### Phase 0: Context Discovery

1. **Clarify intent**: What are we deploying, why, and what does
   "shipped safely" look like? Ask one question at a time, prefer
   multiple choice when possible.
2. **Scan existing infra**: Explore CI configs, Dockerfiles, IaC files,
   deployment scripts, and cloud resources. Do not propose approaches
   before understanding current state.
3. **Identify constraints**: Cloud provider, budget, compliance
   requirements (SOC2, HIPAA), team expertise, existing tooling,
   and hard boundaries (region restrictions, vendor lock-in limits).

### Phase 1: Approach Exploration

4. **Generate 2-3 approaches**: Propose with trade-offs. Even when
   one seems obvious, show alternatives and explain why they're
   less suitable.
5. **Trade-off matrix**: Compare each approach on:
   - Complexity (setup and maintenance cost)
   - Reliability (blast radius, recovery time)
   - Observability (how easy to debug in production)
   - Cost (cloud spend, operational overhead)
6. **Simplicity check**: Strip unnecessary infrastructure. A single
   VM with a deploy script beats Kubernetes for a weekend project.
   Match infrastructure to actual scale, not aspirational scale.

### Phase 2: Direction Confirmation

7. **Recommend**: Present your recommended approach with reasoning.
8. **User selects**: AI presents options, human makes final call.
   Provide enough information for an informed decision.
9. **Scope boundary**: State explicitly what is IN scope and what
   is OUT of scope. Out-of-scope items may be logged as future
   tasks but are not built now.
10. **Handoff summary**: Structure the selected approach as input
    for the spec-writing phase (Intent, Constraints, Approach, Scope).

## Rules

- One question at a time, multiple choice preferred
- Do not propose approaches before exploring existing infra --
  complete Phase 0 before Phase 1
- Match infrastructure to actual scale, not aspirational scale
- AI presents options and recommendations; human decides
- Skip this protocol for minor config changes (env var updates,
  version bumps, label changes)
- Early questions are cheaper than late outages -- resolve ambiguity
  before building infrastructure

## Output Format

1. **Intent Summary**: What we're deploying and success criteria
2. **Current State**: Existing infra, CI/CD, cloud resources
3. **Approach Comparison**: 2-3 approaches with trade-off table
4. **Selected Direction**: Chosen approach with scope boundary
5. **Spec Handoff**: Structured input for `protocols/deploy-spec-writing.md`
   (Intent, Constraints, Approach, Scope)
