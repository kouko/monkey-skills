# Write Architecture Protocol

Write architecture documentation — system overviews, component
specifications, data flow diagrams, deployment topologies, security
models. Architecture docs sit between Reference and Explanation in
Diátaxis terms: they describe the system as it is (Reference) and
elaborate why it is that way (Explanation in adjacent sections), but
follow a fixed template more like Reference.

**Vocabulary reference**: `standards/diataxis-taxonomy.md`
**Style reference**: `standards/style-conventions.md`
**Structure reference**: `standards/architecture-doc-structure.md`
**Pre-writing reference**: `standards/pre-writing-checklist.md` — apply before Phase 0
**Origin**: protocol synthesized from [Trong-Tra/agent-skills `documentation-specialist`](https://github.com/Trong-Tra/agent-skills/tree/main/documentation-specialist) `architecture/SKILL.md` workflow phases, adapted to docs-team's worker/evaluator dispatch model and Diátaxis Reference + Explanation hybrid framing. Worked examples adapted from Trong-Tra's `architecture/examples.md` live in the companion file (see §Worked Examples below).

## Architecture Doc vs Other Modes

| This mode | NOT this mode |
|-----------|---------------|
| Describes system as it is today | Describes a single decision (→ ADR) |
| Mixes Reference (component specs) + Explanation (design rationale) | Pure narrative explanation (→ write-explanation) |
| Fixed-template sections | Open-form (→ Explanation) |
| For contributors and operators | For end users (→ README + tutorials) |

If the artifact is one specific decision with a status (proposed /
accepted), use `write-adr.md` instead. If the artifact is a discursive
"why" piece without a fixed structure, use `write-explanation.md`.

## Phase 0: Context Discovery

1. **Apply pre-writing checklist** (`standards/pre-writing-checklist.md`)
2. **Determine which architecture artifact is needed**:
   - L1 Architecture overview (system-wide)
   - L2 Component specification (one service)
   - Data flow diagram (request lifecycle)
   - Deployment topology (infrastructure)
   - Security model (trust boundaries + auth)
3. **Read existing architecture docs** in the same directory — match
   tone, diagram style, naming conventions
4. **Identify the source of truth** for the system being documented:
   code, infra-as-code (Terraform / Helm), runtime config

## Phase 1: Choose Document Level (L0–L4)

Match document level to reader need (per
`standards/architecture-doc-structure.md` §Document Hierarchy):

| If reader is... | Produce... |
|-----------------|------------|
| Anyone first encountering the project | L0 README — link to L1 from there |
| New contributor onboarding | L1 architecture overview |
| Implementer working on one service | L2 component spec |
| Maintainer evaluating a decision | L3 ADR |
| Operator handling an incident | L4 runbook (route to devops-team) |

**Rule**: link down, summarize up. Do not put L3 detail in an L1 doc; do
not duplicate L1 context in every L2 doc.

## Phase 2: Apply Template by Level

### L1 Architecture Overview

Required sections in order (per `standards/architecture-doc-structure.md`):

1. **System purpose** (1 paragraph)
2. **High-level diagram** (Mermaid, 5-10 boxes max)
3. **Component list** (table: name / purpose / tech stack / ownership)
4. **Data flow** (sequence diagram + prose)
5. **External dependencies** (table: service / purpose / critical / fallback)
6. **Deployment topology** (Mermaid + instance sizes)
7. **Security boundaries** (trust diagram + auth table)

Optional: capacity / scaling notes, known limitations.

### L2 Component Specification

For each non-trivial component, document the 10 fields from
`standards/architecture-doc-structure.md` §Component Specification:
purpose, responsibilities, tech stack, API surface, inbound data,
outbound data, state, **failure modes**, scaling, security notes.

Failure modes is the field most commonly omitted and most important for
operators. Always include it.

### Data Flow Diagram

- Use Mermaid sequence diagram
- Show happy path + one consequential error path
- Annotate critical latencies only when latency is part of the design
- Show retry logic only if the code actually implements it

### Deployment Topology

- Use Mermaid graph showing infrastructure
- Group by region / availability zone / subnet using subgraphs
- Document instance sizes, scaling triggers, network segmentation
- Include data replication topology

### Security Model

- Document trust boundaries explicitly
- For each boundary: protocol, authentication, authorization, data classification
- Use a network diagram showing the public → private layer transitions

## Phase 3: Apply Mermaid Standards

Per `standards/architecture-doc-structure.md` §Mermaid Diagram Standards:

1. **One concern per diagram** — split deployment from data flow
2. **Label every arrow** — protocol or message type
3. **Consistent shapes** — rectangles = services, cylinders = databases, clouds = external
4. **Text fallback** — describe each diagram in prose below it
5. **No legends** — if you need one, simplify

Diagram type matches the question being answered (see standard's table).

## Phase 4: Failure Mode Documentation

For each component or critical flow, document at least:

| Scenario | Behavior | Alert / detection |
|----------|----------|------------------:|
| Database unavailable | Return 503; retry with backoff | `db_connection_pool_exhausted` |
| External API timeout | Return 202 (accepted); async retry | `external_api_timeout_rate > 5%` |
| Invalid input | Return 400; do not log payload | None (expected) |
| Authentication failure | Return 401; log security event | `auth_failure_rate > 1/min` |

This table is the operator's runbook seed. Without it, the architecture
doc is incomplete.

## Phase 5: Cross-References

Link to:
- **README** for end-user perspective
- **ADRs** for the specific decisions that produced this architecture
- **Runbooks** (devops-team) for operational procedures
- **API reference** for the contract surface

Do **not** embed the content of these other artifacts. Architecture docs
describe the system; the linked artifacts describe usage / decisions /
operations / contract.

## Rules

- **One concern per diagram.** Splitting is always cheaper than merging.
- **Failure modes are mandatory.** Operators read this section first
  during incidents.
- **No fictional retries / fallbacks.** If the code does not implement
  it, do not document it. Architecture docs that describe aspirations
  rather than reality are worse than no docs.
- **Trust boundaries explicit.** Auth-and-authz live at boundaries; if
  boundaries are vague, the security analysis is broken.
- **Outdated diagrams must change.** If the architecture changes, the
  diagram must change in the same PR.

## Output Structure (L1 example skeleton)

```markdown
---
title: {System name} Architecture Overview
last_reviewed: {YYYY-MM-DD}
applies_to: {version or "main"}
owner: {team}
mode: reference
---

# {System name} Architecture Overview

## System purpose

{One paragraph: what problem does this solve?}

## High-level diagram

​```mermaid
graph LR
    {5-10 boxes max, labeled arrows}
​```

{2-3 sentence text fallback describing the diagram}

## Components

| Name | Purpose | Tech stack | Owner |
|------|---------|-----------|-------|
| {...} | {...} | {...} | {...} |

## Data flow

​```mermaid
sequenceDiagram
    {happy path}
​```

{Numbered prose walk-through}

## External dependencies

| Service | Purpose | Critical? | Fallback | Owner |
|---------|---------|-----------|----------|-------|

## Deployment topology

{Mermaid + instance table}

## Security boundaries

{Trust diagram + auth table}

## Known limitations

{Bulleted list — be honest}

## Related

- README: {link}
- ADR: {link to relevant ADRs}
- Runbooks: {link to runbook directory}
```

## Worked Examples (Companion File)

Five complete architecture documentation examples (System Context,
Component Spec, Data Flow + Error Path, Deployment Topology,
Security Model) live in the companion file:

```
protocols/write-architecture-examples.md
```

The `worker` agent loads this companion via the `additional:` field.
Architecture documentation is hard-blocked from quick mode (per
`protocols/quick-write.md` §Hard Block List), so the companion is
always available when this protocol runs.

When dispatching a worker for an architecture task, the main agent
passes:

```
- protocol: {base_path}/protocols/write-architecture.md
- additional: [{base_path}/protocols/write-architecture-examples.md]
```

## Mode Clarity Check

This architecture doc passes the Architecture Documentation Completeness
gate (`rubrics/architecture-doc-completeness.md`) if:

- The document level (L0-L4) is declared in frontmatter or first paragraph
- For L1 overviews: all 7 required sections present
- For L2 component specs: all 10 required fields present, **failure modes mandatory**
- All diagrams follow the 5 Mermaid rules (one concern, labeled arrows, consistent shapes, text fallback, no legends)
- Trust boundaries are explicit if any auth is documented
- Cross-references link to README / ADRs / runbooks; no embedded duplication
