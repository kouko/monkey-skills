# Architecture Documentation Structure (Shared Standard)

Structural requirements for architecture documentation — system overviews,
component specifications, data flow diagrams, deployment topologies,
security models. Architecture docs are for contributors and operators,
not end users.

Primary sources:
- [C4 model — Simon Brown](https://c4model.com/) — context / container / component / code hierarchy
- [arc42 — Architecture documentation template](https://arc42.org/) — German enterprise standard
- [Mermaid diagram syntax](https://mermaid.js.org/) — markdown-native diagrams
- Synthesized from Trong-Tra/agent-skills documentation-specialist
  architecture module + observed industry practice

## Document Hierarchy (L0–L4)

Architecture documentation has five levels of detail. **Match document
depth to reader need** — do not put L3 detail in an L1 document.

| Level | Audience | Question answered | Typical artifact |
|------:|----------|-------------------|------------------|
| **L0** | Everyone | "What is this and how do I run it?" | README |
| **L1** | New contributors, evaluators | "What are the components? How do they talk?" | Architecture overview |
| **L2** | Implementers | "How does this specific service work?" | Component deep-dive / data flow |
| **L3** | Maintainers, future architects | "Why did we choose X over Y?" | ADR |
| **L4** | Operators | "What do I do when this breaks?" | Runbook (lives in devops-team) |

Rule: **link down, summarize up.** L1 documents link to L2 and L3 for
detail; L2 documents summarize their L1 context in 1-2 sentences and link
back.

## Architecture Overview (L1) Required Sections

Every architecture overview must answer all seven questions in order:

1. **System purpose** — one paragraph: what problem does this solve?
2. **High-level diagram** — Mermaid or equivalent, **5-10 boxes max**
3. **Component list** — for each: name, purpose, tech stack, ownership
4. **Data flow** — trace a typical request through the components
5. **External dependencies** — databases, message queues, third-party APIs, CDNs
6. **Deployment topology** — containers / VMs / serverless / where it runs
7. **Security boundaries** — what is trusted? what is untrusted? where is auth enforced?

Optional but common: capacity / scaling notes, known limitations, future
roadmap.

## Component Specification (L2) Required Fields

Every non-trivial component deserves a specification with these fields:

| Field | Description |
|-------|-------------|
| **Purpose** | One sentence: what this component does |
| **Responsibilities** | Bulleted list of duties owned by this component |
| **Tech stack** | Language, framework, database, queue |
| **API surface** | gRPC / REST / event / internal interface |
| **Inbound data** | Where requests / events arrive from |
| **Outbound data** | Where this component sends data |
| **State** | What is persisted, where, with what retention |
| **Failure modes** | What breaks the component, what behavior results, what alert fires |
| **Scaling** | CPU-bound / IO-bound / DB-bound; how to add capacity |
| **Security notes** | Trust boundary, auth requirements, sensitive data handling |

Failure modes is the most commonly omitted field and the most important
one for operators. **Always include failure modes.**

## Mermaid Diagram Standards

Use Mermaid for all architecture diagrams. Renders in GitHub, GitLab,
Notion, Obsidian, and most modern Markdown viewers.

### Five Diagram Rules

1. **One concern per diagram.** A deployment diagram and a data flow
   diagram are separate artifacts. A single diagram trying to show both
   is unreadable.
2. **Label every arrow.** `|HTTP|` or `|gRPC|` or `|Pub/Sub|` tells the
   reader the protocol. An unlabeled arrow is a mystery.
3. **Consistent shapes.** Rectangles for services, cylinders for databases,
   clouds for external APIs. Same shape means same thing throughout the
   document.
4. **Text fallback.** Every diagram must be described in prose below it.
   Not every reader can view rendered diagrams (screen readers, plain-text
   email, terminal-only environments).
5. **No legends.** If your diagram needs a legend, it is too complex.
   Simplify.

### Diagram Types

Match the type to the question being answered.

| Type | Use for | Avoid for |
|------|---------|-----------|
| System context | External actors and systems | Internal implementation |
| Container | Services, databases, queues | Class-level structure |
| Component | Modules within a service | Cross-service interactions |
| Deployment | Infrastructure topology | Business logic |
| Sequence | Request lifecycle | Static structure |
| Data flow | How data moves and transforms | Deployment locations |

Container and component diagrams come from the C4 model (Simon Brown).
Sequence and data flow are widely understood across notation traditions.

## Data Flow Documentation

For non-trivial flows, document **happy path + one error path**. Do not
diagram every possible error — pick the most consequential one.

Sequence diagram conventions:
- Show participants left-to-right in roughly the order they appear in the flow
- Annotate critical latencies (`| 50ms |`) only when latency is part of the design
- Show retry logic if it is part of the design (do not invent retries that the code does not implement)
- For events, name the event topic explicitly (`order.created`, not "publish event")

## Dependency Documentation

External dependencies are risks. Document each one explicitly in a table:

| Service | Purpose | Critical? | Fallback | Owner |
|---------|---------|-----------|----------|-------|
| Stripe | Payment processing | Yes | None — queue for retry | Finance |
| SendGrid | Transactional email | No | Queue indefinitely | Platform |
| AWS S3 | File storage | Yes | Cross-region replication | SRE |

Critical = "this system cannot fulfill its purpose without this dependency."
Non-critical = "degraded but functional."

State the **failure scenario** for each critical dependency: what happens
when it goes down? Reader will need to know during incidents.

## Security Boundary Documentation

Trust boundaries are the most important security artifact. State them
explicitly:

```
Internet (untrusted)
  ↓ TLS 1.3
Cloudflare WAF
  ↓ TLS 1.3
AWS ALB
  ↓ mTLS
API Gateway (auth boundary — JWT validated here)
  ↓ mTLS
Internal services (trusted)
  ↓ TLS
Databases (trusted, in private subnet)
```

For each boundary, document:
- What protocol crosses it (TLS 1.2 / 1.3 / mTLS / VPC peering)
- What authentication is enforced
- What authorization is enforced
- What data classification can cross it

## When to Use ADR vs Architecture Doc vs Explanation

| If the artifact is... | Use |
|----------------------|-----|
| A specific decision with status (proposed / accepted / superseded) | ADR (`protocols/write-adr.md`) |
| A description of the system as it is today | Architecture doc (`protocols/write-architecture.md`) |
| A discursive "why" piece that elaborates a concept or trade-off | Explanation (`protocols/write-explanation.md`) |

Architecture docs describe **the system**. ADRs describe **decisions
that produced the system**. Explanations describe **the thinking that
informed the decisions**.

## Sources

- [C4 model](https://c4model.com/) — Simon Brown's architecture diagram hierarchy
- [arc42](https://arc42.org/) — full architecture documentation template
- [Mermaid](https://mermaid.js.org/) — markdown-native diagram syntax
- `standards/diataxis-taxonomy.md` — Architecture docs are Reference + Explanation hybrid; component specs are Reference, design rationale is Explanation
- Synthesized from Trong-Tra/agent-skills documentation-specialist
  architecture module v1
