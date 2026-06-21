# SEED 5 — microservices migration (SWE / ship-faster goal)

## QUESTION
Should we migrate our monolith to microservices to ship features faster?

## CONFIRMED CLAIMS BLOCK
### [0] Microservices allow independent service deployment, decoupling release cycles across teams.
Vote: 9-1 · Source: martinfowler.com/articles/microservices.html (primary)
Quote: "services can be deployed independently — a change to one service requires no coordination with other services"
Verifier evidence (high): multiple primary sources confirm independent deployability.

### [1] Amazon's early-2000s monolith→microservices migration cited as enabling independent team scaling + faster deployments.
Vote: 7-2 · Source: highscalability.com amazon-architecture (secondary)
Quote: "each team owns their services end-to-end, from development through production"
Verifier evidence (medium): widely cited but primary source sparse; second-hand reconstructions.

### [2] Microservices introduce ~1–10ms latency per inter-service hop.
Vote: 8-2 · Source: netflixtechblog.com microservices-at-scale (blog)
Quote: "every service call crosses the network; at scale that's milliseconds per hop in deep call chains"
Verifier evidence (medium): order-of-magnitude consistent; exact figures vary.

### [3] Teams smaller than ~8–10 engineers per service often iterate slower (distributed overhead > autonomy).
Vote: 6-3 · Source: blog.pragmaticengineer.com microservices-team-size (blog)
Quote: "below a certain headcount, the cognitive overhead of running distributed infrastructure erodes delivery speed gains"
Verifier evidence (medium): practitioner heuristic, not a controlled study.

### [4] Conway's Law: organizations produce designs that mirror their communication structures.
Vote: 10-0 · Source: melconway.com Committees_Paper (primary)
Quote: "organizations which design systems are constrained to produce designs which are copies of the communication structures"
Verifier evidence (high): original 1968 paper; widely replicated.

### [5] Distributed tracing/observability (Jaeger/Zipkin) required to debug cross-service failures → overhead monoliths don't have.
Vote: 8-1 · Source: opentelemetry.io observability-primer (primary)
Quote: "a single user request may touch dozens of services; without tracing you cannot reconstruct what happened"
Verifier evidence (high): CNCF consensus.

### [6] Deployment frequency at microservices orgs averages higher than monolith-first orgs (2022 DORA).
Vote: 6-4 · Source: dora.dev 2022-dora-report (primary)
Quote: "elite performers deploy on demand, multiple times per day; architectural modularity is a correlating factor"
Verifier evidence (medium): DORA confirms correlation; does not isolate microservices as causal.

### [7] Migrations frequently stall in a "distributed monolith" state (deployed separately but tightly coupled via shared DB / sync chains).
Vote: 8-1 · Source: sam-newman.com microservices-not-a-free-lunch (blog)
Quote: "you can end up with all the complexity of a distributed system and none of the benefits if you decompose without addressing data coupling"
Verifier evidence (medium): widely documented failure mode; no large-scale frequency estimate.

### [8] Migrations frequently multi-year; several post-mortems report teams that never completed + maintained both indefinitely.
Vote: 7-2 · Source: infoq.com monolith-to-microservices-journey (secondary)
Quote: "the migration became a permanent state of partial decomposition; new features had to be written twice"
Verifier evidence (low): aggregates anecdotal post-mortems; no systematic completion-rate study.

### [9] Kubernetes/orchestration reduces but doesn't eliminate operational burden (networking, discovery, secrets per service).
Vote: 9-1 · Source: kubernetes.io what-is-kubernetes (primary)
Quote: "Kubernetes automates deployment and scaling but does not manage app-level concerns like inter-service auth or circuit breaking"
Verifier evidence (high): official docs + SRE literature.

### [10] Spotify's squad model (cited as proof microservices enable autonomy) partially rolled back by 2021 as cross-team deps remained.
Vote: 5-4 · Source: blog.crisp.se spotify-engineering-culture (blog)
Quote: "autonomous squads require aligned architecture; org structure alone does not remove technical coupling"
Verifier evidence (low): documented in secondary sources; no official Spotify retrospective.

### [11] Feature flags + modular-monolith patterns provide deployment independence within a single deployable unit; cited as lower-overhead alternative for teams under 50.
Vote: 6-3 · Source: shopify.engineering deconstructing-monolith (blog)
Quote: "we achieved independent team velocity without microservices by enforcing strict module boundaries inside a single Rails application"
Verifier evidence (medium): documented at Shopify scale; generalizes from one org.

## ARM A — SINGLE-PASS SYNTHESIS
SUMMARY: Microservices enable independent deployability and autonomous team scaling, but they do not automatically make you ship features faster — the net effect depends on team size, organizational structure, and operational readiness. The deployment-speed gains documented in DORA correlate with architectural modularity, but causality is unproven; the same autonomy benefits are achievable inside a well-structured modular monolith for teams under ~50 engineers. Migrations are high-risk: they routinely stall in a "distributed monolith" state, frequently run multi-year, and add permanent observability and orchestration overhead that monoliths don't require. Conway's Law is the most robust finding — if your team topology doesn't change, your service boundaries will mirror existing coupling, negating the benefits. The honest answer: for most monoliths below a certain team scale, a modular-monolith-first path delivers faster feature velocity at lower organizational cost than a microservices migration.

FINDINGS:
- [high] Independent deployability is real — services released without cross-team coordination. | evidence: Fowler primary + DORA correlation; DORA doesn't isolate microservices as sole cause.
- [high] Conway's Law governs boundary quality — coupled comms → coupled services regardless of deployment topology. | evidence: 1968 paper, 10-0.
- [medium] Distributed-monolith failure is the dominant migration risk; post-mortems document never-completed migrations. | evidence: 8-1; completion-rate anecdotal.
- [medium] Operational overhead substantial + permanent — distributed tracing + per-service networking/discovery/secrets; K8s only partially automates. | evidence: OpenTelemetry + K8s docs.
- [medium] ~1–10ms latency per hop; teams <8–10 eng/service often iterate slower. | evidence: blogs; team-size is a heuristic.
- [medium] Modular-monolith + feature flags is a documented lower-overhead alternative (Shopify, <50 eng); Amazon is the large-scale counter-example (sparse sourcing). | evidence: Shopify production but one org; Amazon second-hand.
- [low] Org realignment alone doesn't remove coupling — Spotify squad model partially rolled back 2021. | evidence: 5-4; no official retrospective.

CAVEATS: DORA shows correlation not causation — high performers may adopt microservices because they already have maturity. Team-size thresholds are practitioner heuristics, not experiments. Completion-rate/"distributed monolith" frequency are anecdotal. Spotify + Amazon both have sourcing gaps — illustrative not dispositive.

OPEN QUESTIONS:
- What is the actual completion rate of these migrations, and what predicts success vs stall?
- At what team size / deployment-frequency target does microservices overhead break even vs a modular monolith?
- Does microservices CAUSE deployment-frequency gains, or do high-maturity teams adopt + improve for other reasons?
- How much of "faster shipping" is the accompanying org restructuring rather than the architecture change?
