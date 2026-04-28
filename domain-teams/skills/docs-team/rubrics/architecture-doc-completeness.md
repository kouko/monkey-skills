# Architecture Documentation Completeness Gate

## Scope Boundary

Review the **structural completeness** of an architecture document
(L1 system overview, L2 component specification, data flow, deployment
topology, or security model) against the requirements in
`standards/architecture-doc-structure.md` and `protocols/write-architecture.md`.

Do NOT review: factual correctness of the architecture, Diátaxis mode
clarity (architecture docs are explicitly Reference + Explanation hybrid),
freshness, or style — those belong to other gates or are out of scope.

**Standard reference**: `standards/architecture-doc-structure.md`
**Protocol reference**: `protocols/write-architecture.md`

## Document Level Detection

Before applying flags, determine the document level from frontmatter or
the first paragraph:

| Frontmatter / opening signal | Level |
|------------------------------|------:|
| "Architecture overview" / "System architecture" / 5-10 box top-level diagram | L1 |
| "{Service name} Service" / "{Component name} Component" specification | L2 |
| "Data flow" / "Request lifecycle" / sequence diagram is primary content | Data flow |
| "Deployment topology" / region-scoped infrastructure diagram | Deployment |
| "Security model" / trust boundary diagram | Security |

If the level cannot be determined, return `NEEDS_REVISION` with evidence
"Document level cannot be inferred — declare in frontmatter or first paragraph."

## Flag Definitions (L1 Architecture Overview)

### Required Sections

- 🔴 **Fatal**: Any of the 7 required L1 sections is missing: System
  purpose, High-level diagram, Component list, Data flow, External
  dependencies, Deployment topology, Security boundaries.
- 🟡 **Warning**: All 7 sections present but one is perfunctory (e.g.
  "External dependencies: TBD" or single-sentence Security boundaries).
- 🟢 **Clear**: All 7 sections present with substantive content.

### High-Level Diagram

- 🔴 **Fatal**: Diagram has more than 10 boxes (overview is too detailed
  for L1) OR fewer than 3 boxes (no architecture to show) OR no diagram
  at all.
- 🟡 **Warning**: 5-10 boxes but unlabeled arrows or inconsistent shapes.
- 🟢 **Clear**: 3-10 boxes, all arrows labeled with protocol / message
  type, consistent shapes (rectangles for services, cylinders for DBs,
  clouds for external).

### Component List

- 🔴 **Fatal**: No component table OR table missing required columns
  (name / purpose / tech stack / ownership).
- 🟡 **Warning**: Table present but ownership is "TBD" / "team" without
  specificity.
- 🟢 **Clear**: Every row has all 4 fields filled.

## Flag Definitions (L2 Component Specification)

### Required Fields

- 🔴 **Fatal**: Any of these required fields is missing: Purpose,
  Responsibilities, Tech stack, API surface, Inbound data, Outbound data,
  State, **Failure modes**, Scaling, Security notes.
- 🟡 **Warning**: All fields present but one is single-sentence.
- 🟢 **Clear**: All 10 fields present with substantive content.

### Failure Modes

- 🔴 **Fatal**: Failure modes section is missing entirely. This is the
  field operators read first during incidents — its absence makes the
  spec unusable for on-call.
- 🟡 **Warning**: Failure modes table present but covers fewer than 3
  scenarios.
- 🟢 **Clear**: Failure modes table covers ≥3 distinct failure scenarios
  with behavior + alert / detection columns.

### Security Notes

- 🔴 **Fatal**: Component handles authentication, sensitive data, or
  external integrations but has no Security notes section.
- 🟡 **Warning**: Security notes present but non-specific ("uses TLS").
- 🟢 **Clear**: Security notes name specific mechanisms (mTLS, HMAC
  verification, IAM roles) and data classifications.

## Flag Definitions (Mermaid Diagrams)

Applies to all diagrams in any architecture artifact.

### Diagram Discipline

- 🔴 **Fatal**: Single diagram tries to show two concerns (deployment
  AND data flow) OR no text fallback for any diagram OR diagram has a
  legend (indicates over-complexity).
- 🟡 **Warning**: Most diagrams clean, one or two have unlabeled arrows
  or missing text fallback.
- 🟢 **Clear**: All diagrams follow 5 Mermaid rules: one concern, labeled
  arrows, consistent shapes, text fallback, no legends.

## Flag Definitions (Common to All Levels)

### Cross-References

- 🔴 **Fatal**: Architecture doc embeds full content of ADRs or runbooks
  inline (duplicates SSOT).
- 🟡 **Warning**: References ADRs / runbooks but links are missing or broken.
- 🟢 **Clear**: Cross-references to README, ADRs, runbooks, API reference
  are present and resolve.

### Aspiration vs Reality

- 🔴 **Fatal**: Architecture doc describes retries / fallbacks / failover
  that the code does not implement (verifiable via code reference). This
  is the most dangerous architecture-doc failure mode.
- 🟡 **Warning**: Some sections marked "planned" or "v2" without clear
  separation from current behavior.
- 🟢 **Clear**: Document describes the system as it currently is; future
  plans are clearly marked as such.

## Verdict Rules

1. **NEEDS_REVISION**: Any 1 🔴 fatal flag
2. **NEEDS_REVISION**: 2 or more 🟡 warning flags
3. **PASS_WITH_NOTES**: Exactly 1 🟡 warning flag, no 🔴
4. **PASS**: All 🟢 clear

## Rules

- **Failure modes are mandatory for L2.** No exceptions. A component
  spec without failure modes is not a spec; it is marketing.
- **Aspiration-vs-reality is the most dangerous failure.** If the doc
  describes a retry the code does not implement, operators will trust
  the doc and be wrong. Flag aggressively.
- **One concern per diagram is non-negotiable.** A "small" violation
  here cascades — readers stop trusting any diagram in the doc.
- **Embedded ADRs are an SSOT violation.** Architecture docs link to
  ADRs; they do not duplicate them.
- **Do not grade architecture quality.** This gate checks whether the
  doc is structurally complete, not whether the architecture is good.

## Output Format

1. **Document level**: detected level (L1 / L2 / data flow / deployment / security)
2. **Flags**: List each triggered flag with `[🔴 Dimension]` or `[🟡 Dimension]`
3. **Evidence**: Quote the specific section or diagram
4. **Fix instruction**: Specific addition or correction needed
5. **Verdict**: PASS / PASS_WITH_NOTES / NEEDS_REVISION

## Sources

- `standards/architecture-doc-structure.md` — required sections per level + Mermaid rules
- `protocols/write-architecture.md` — workflow that produces architecture docs
- [C4 model](https://c4model.com/) — Simon Brown's diagram hierarchy
- [arc42](https://arc42.org/) — full architecture documentation template
