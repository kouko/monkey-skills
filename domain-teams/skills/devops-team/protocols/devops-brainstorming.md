# DevOps Brainstorming Protocol

Understand infrastructure intent, explore approaches, and confirm
direction before building configs. Core principles: one question at a
time, propose 2-3 approaches, prefer boring infrastructure over clever
infrastructure, AI proposes human decides.

## Protocol

### Phase 0: Context Discovery & Shared Understanding

#### Step 1: Clarify intent

1. **Ask intent**: What are we deploying, why, and what does
   "shipped safely" look like? Ask one question at a time, prefer
   multiple choice when possible. Keep this brief (1-2 questions)
   to establish direction before exploring infra.

#### Step 2: Explore codebase

2. **Scan existing infra**: Explore CI configs (`.github/workflows/`
   for GitHub Actions, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/`),
   Dockerfiles, IaC files, deployment scripts, and cloud resources.
   Do not propose approaches before understanding current state.
3. **Identify constraints**: Cloud provider, budget, compliance
   requirements (SOC2, HIPAA), team expertise, existing tooling,
   and hard boundaries (region restrictions, vendor lock-in limits).

#### Step 3: Grill — challenge assumptions

Using infra findings, question the user's deployment intent and
assumptions to reach shared understanding. One question at a time.
For each question, provide your recommended answer.

4. **Challenge assumptions**: "You want Kubernetes, but your current
   traffic fits a single VM — what's driving the choice?" Surface
   contradictions between stated intent and actual infrastructure
   needs.
5. **Probe dependencies**: "Adding a CDN requires DNS changes and
   certificate provisioning — who manages that?" Walk down each
   branch of the decision tree, resolving dependencies one by one.
6. **Test boundaries**: "What's the acceptable downtime during
   deployment? What's the rollback plan if it fails?" Push on
   unstated requirements and implicit expectations.
7. **Explore the codebase** instead of asking, when a question can
   be answered by reading configs or scripts.

Continue until no unresolved branches remain, or the user requests
to move on. Do not set a fixed question limit.

#### Step 4: Understanding Summary

8. **Produce Understanding Summary** and ask user to confirm before
   proceeding to Phase 1:

```
## Understanding Summary

### Intent
[What we're deploying and why]

### Key Constraints
[Cloud provider, budget, compliance, team expertise constraints]

### Confirmed Assumptions
[Assumptions validated during grill]

### Resolved Ambiguities
[Questions that were unclear but now resolved]
```

Skip Phase 0 Steps 3-4 for minor config changes (env var updates,
version bumps, label changes) — proceed directly to Phase 1.

### Phase 1: Approach Exploration

4. **Generate 2-3 approaches**: Propose with trade-offs. Even when
   one seems obvious, show alternatives and explain why they're
   less suitable.
5. **Trade-off matrix**: Compare each approach on:
   - Complexity (setup and maintenance cost)
   - Reliability (blast radius, recovery time)
   - Observability (how easy to debug in production)
   - Cost (cloud spend, operational overhead)
   - **DORA lead-time impact** (how the choice affects lead time for changes;
     see `standards/dora-metrics.md`) — infrastructure choices that add
     deploy-time friction will show up in lead time over weeks
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
- During grill (Step 3): provide your recommended answer with each
  question — don't just ask, also propose
- If a question can be answered by exploring configs or scripts,
  explore instead of asking the user
- Understanding Summary must be confirmed by user before Phase 1
- Match infrastructure to actual scale, not aspirational scale
- AI presents options and recommendations; human decides
- Skip Phase 0 grill (Steps 3-4) for minor config changes (env var
  updates, version bumps, label changes)
- Early questions are cheaper than late outages -- resolve ambiguity
  before building infrastructure

## Output Format

1. **Intent Summary**: What we're deploying and success criteria
2. **Current State**: Existing infra, CI/CD, cloud resources
3. **Approach Comparison**: 2-3 approaches with trade-off table
4. **Selected Direction**: Chosen approach with scope boundary
5. **Spec Handoff**: Structured input for `protocols/deploy-spec-writing.md`
   (Intent, Constraints, Approach, Scope)
