# Methodical Doubt --- Additional Cases

Extended examples for reference.

## Cloud Provider Trust

| Layer | Content |
|-------|---------|
| Original Belief | "AWS is reliable, so our system is reliable" |
| Sensory Doubt | Have you measured YOUR system's reliability, or are you citing AWS's SLA? AWS guarantees 99.99% for individual services, not for your specific architecture combining multiple services |
| Reasoning Doubt | Even if AWS is reliable, does that make your system reliable? Your application code, configuration, and integration logic are separate failure domains |
| Systemic Doubt | What if "reliable" is the wrong frame? Maybe the question is "how does the system behave when things fail?" — resilience, not reliability |
| What Survived | "AWS individual services have high uptime." Everything else (our architecture's reliability, our definition of reliable) was unverified |
| Rebuilt Foundation | Measure OUR system's actual reliability; design for failure, not for uptime; define what "reliable" means for our users |

## "Our Tests Prove the Code Works"

| Layer | Content |
|-------|---------|
| Original Belief | "We have 90% test coverage, so the code is correct" |
| Sensory Doubt | What does "90% coverage" measure? Lines executed, not behaviors verified. Tests can execute code without asserting correct behavior |
| Reasoning Doubt | Even with perfect coverage, does "tests pass" equal "code is correct"? Tests verify expected behavior — but who verified the expectations? Tests can encode the wrong requirements perfectly |
| Systemic Doubt | What if testing itself is insufficient? What about emergent behaviors, race conditions, production-only configurations? The testing paradigm has known blind spots |
| What Survived | "Our tests execute 90% of code lines and currently pass." Nothing about correctness survived doubt |
| Rebuilt Foundation | Complement coverage with mutation testing; verify test assertions match actual requirements; add production observability as a separate verification layer |

## Microservices Migration Justification

| Layer | Content |
|-------|---------|
| Original Belief | "We need to migrate to microservices to scale" |
| Sensory Doubt | What evidence do you have that the monolith cannot scale? Have you profiled it? Have you tried horizontal scaling? Or is this based on conference talks and blog posts? |
| Reasoning Doubt | Even if the monolith has scaling issues, does microservices solve them? Microservices introduce network latency, distributed transactions, and operational complexity. Could the scaling issue be in the database, not the application? |
| Systemic Doubt | What if "scaling" is not actually your problem? What if the real issue is deployment speed, team autonomy, or a single slow query? "We need to scale" might be a proxy for a different concern entirely |
| What Survived | "We experience performance issues under load." The cause, the solution, and whether "scale" is the right frame were all uncertain |
| Rebuilt Foundation | Profile the actual bottleneck; try the cheapest fix first (query optimization, caching, horizontal scaling of the monolith); only decompose if the bottleneck is proven to be architectural |

## "Users Want This Feature"

| Layer | Content |
|-------|---------|
| Original Belief | "Users are asking for dark mode, so we should build it" |
| Sensory Doubt | How many users asked? Through what channel? Could it be a vocal minority? Are feature requests representative of actual need, or just stated preference? |
| Reasoning Doubt | Even if users say they want it, does building it achieve a business outcome? Will dark mode increase retention, reduce churn, or drive revenue? "Users want it" does not equal "we should build it" |
| Systemic Doubt | What if feature requests are the wrong signal entirely? What if users request dark mode because they use the product at night, and the real problem is eye strain from poor contrast — not the absence of dark mode specifically? |
| What Survived | "Some users communicated a preference related to visual comfort." The specific solution (dark mode), the scale of demand, and the business impact were all uncertain |
| Rebuilt Foundation | Quantify demand; investigate the underlying need (visual comfort, not dark mode specifically); validate whether solving the need moves a metric you care about |

## "Our Architecture Is Event-Driven, So It's Decoupled"

| Layer | Content |
|-------|---------|
| Original Belief | "We use message queues between services, so our system is decoupled" |
| Sensory Doubt | Have you tested decoupling by actually taking a service down? Or is "decoupled" a property of the architecture diagram, not the running system? |
| Reasoning Doubt | Message queues decouple timing, but do they decouple semantics? If Service B cannot function without data from Service A's events, they are semantically coupled regardless of the transport layer |
| Systemic Doubt | What if "decoupled" is the wrong goal? What if what you actually need is "independently deployable" or "fault-isolated"? Event-driven architecture serves specific goals — are those your goals? |
| What Survived | "Services communicate asynchronously via message queues." Whether this constitutes meaningful decoupling for your operational goals was not established |
| Rebuilt Foundation | Define what "decoupled" means operationally (independently deployable? fault-isolated? schema-independent?); test each property directly; accept that async communication is a mechanism, not a guarantee |

## Sources

- Descartes, R. *Meditations on First Philosophy* (1641)
- [Stanford Encyclopedia — Descartes' Epistemology](https://plato.stanford.edu/entries/descartes-epistemology/)
