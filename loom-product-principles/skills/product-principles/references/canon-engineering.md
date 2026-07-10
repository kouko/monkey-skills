# Canon: Software architecture (agent-consumed only)

Agent-facing recall insurance, consulted at the propose-candidates step as a
completeness audit — never shown raw to the user.

Including but not limited to the entries below; doctrine content stays in
the model (this list carries name + fits-when hint + stability note +
source only).

Consumed ONLY by the autonomous engineering agent for (a) self-decided
architecture and (b) kickoff-briefing option generation (translated to
product-stakes language) — it does not put MVVM-tier choices back on the
user's table. Fit hints carry the reversibility profile (two-way / one-way
door) because the escalation rubric's two-axis test keys on it.

Grounded in `docs/loom/research/2026-07-10-principles-canon-base-lists.md` §4.

| Entry (originator, year) | Fits when… (reversibility) | Stability | Source |
|---|---|---|---|
| Monolithic architecture | Small team, unclear domain, ship fast — one-way once scale forces a split | Evergreen default | [MonolithFirst](https://martinfowler.com/bliki/MonolithFirst.html) |
| Modular Monolith (Simon Brown, 2015) | Service-style boundaries without distributed tax — two-way (extractable if boundaries held) | Growing (Shopify, Spring Modulith) | [simonbrown.je](https://simonbrown.je/modular-monolith/) |
| Microservices (Lewis & Fowler, 2014) | Independent team/deploy/scale — one-way org-wide | Mainstream, tempered by monolith-first backlash | [martinfowler.com](https://martinfowler.com/articles/microservices.html) |
| Event-Driven Architecture (Hohpe & Woolf, 2003) | Async decoupling, multiple consumers — two-way per event, one-way once schemas have many dependents | Stable, resurging via streaming | [EIP](https://www.enterpriseintegrationpatterns.com/) |
| Serverless / FaaS (AWS Lambda, 2014) | Spiky/short-lived workloads, zero infra ops — two-way per function, one-way at vendor lock-in | Mainstream | [aws.amazon.com](https://aws.amazon.com/lambda/) |
| Local-First (Ink & Switch / Kleppmann, 2019) | User owns data + offline + multi-device sync — two-way (cloud addable later) | Emerging, CRDT-driven (long-tail) | [inkandswitch.com](https://www.inkandswitch.com/local-first/) |
| Layered / N-Tier (POSA, 1996) | Straightforward CRUD, horizontal separation — two-way | Enterprise default | [wikipedia](https://en.wikipedia.org/wiki/Multitier_architecture) |
| Hexagonal / Ports & Adapters (Cockburn, 2005) | Core domain must stay IO/framework-independent — two-way, adapters swappable | Stable, foundational | [cockburn.us](https://alistair.cockburn.us/hexagonal-architecture/) |
| Clean Architecture (Martin, 2012/17) | Dependency-inversion discipline app-wide — two-way but upfront layering cost | Popular, over-applied to small apps | [cleancoder.com](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) |
| MVC / MVP / MVVM (1979 / 1996 / 2005) | UI display/logic separation — two-way, sticky once binding tech chosen | MVVM current data-binding default | [wikipedia](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93viewmodel) |
| Unidirectional Data Flow — Flux/Redux/Elm (2012-15) | Nested UI state needs predictable mutations — two-way per reducer, one-way once store shape is load-bearing | Stable; atom-based libs push back | [redux.js.org](https://redux.js.org/understanding/thinking-in-redux/three-principles) |
| CQRS (Greg Young, 2010) | Read/write models diverge sharply — one-way once paired with event sourcing | Stable niche, DDD-paired | [martinfowler.com](https://martinfowler.com/bliki/CQRS.html) |
| DDD strategic + tactical (Evans, 2003) | Complex domain needs ubiquitous language + bounded contexts — one-way once teams/data organize around contexts | Canonical 20+ yrs | [domainlanguage.com](https://www.domainlanguage.com/ddd/) |
| Apple SwiftUI architecture — MV/MVVM + @Observable | SwiftUI on Apple platforms — two-way at ViewModel granularity | Evolves each WWDC (Observation, 2023) | [developer.apple.com](https://developer.apple.com/documentation/swiftui/managing-model-data-in-your-app) |
| Android recommended architecture — UDF + layers | Android/Compose needing Google-blessed testability — two-way | Actively maintained, official | [developer.android.com](https://developer.android.com/topic/architecture) |
| React Server Components / App Router (2023-26) | Server-rendered-by-default web + selective client interactivity — semi one-way once data-fetching restructures | Rapidly evolving, not settled | [react.dev](https://react.dev/reference/rsc/server-components) |
| 12-Factor App (Wiggins/Heroku, 2011) | Cloud-native horizontally scalable services — cross-cutting checklist | Canonical; some factors pre-container | [12factor.net](https://12factor.net/) |
| AWS Well-Architected (2012; 6 pillars) | Vendor-endorsed audit lens (ops/security/reliability/perf/cost/sustainability) | Actively maintained | [docs.aws.amazon.com](https://docs.aws.amazon.com/wellarchitected/latest/framework/the-pillars-of-the-framework.html) |
| Evolutionary Architecture / Fitness Functions (Ford/Parsons/Kua, 2017) | Architecture must change incrementally under CD — automates safe two-way doors | Stable, CI/CD-governance tied | [O'Reilly](https://www.oreilly.com/library/view/building-evolutionary-architectures/9781491986356/) |
| Two-Way Door framework (Bezos, 2015 letter) | The reversibility meta-lens itself (escalation rubric's Axis B) | Canonical | [aboutamazon.com](https://www.aboutamazon.com/news/company-news/2016-letter-to-shareholders) |
| Cell-Based / Bulkhead (AWS guidance) | Bound blast radius at scale — two-way to add cells, one-way once sharded | Growing at hyperscale (long-tail) | [docs.aws.amazon.com](https://docs.aws.amazon.com/wellarchitected/latest/reducing-scope-of-impact-with-cell-based-architecture/what-is-a-cell-based-architecture.html) |
| Vertical Slice Architecture (Bogard, 2018) | Feature-first organization minimizing cross-layer churn — two-way, slices independent | Growing in .NET/CQRS, less known elsewhere (long-tail) | [jimmybogard.com](https://www.jimmybogard.com/vertical-slice-architecture/) |

**Popularity head**: Microservices, MVC (reflexive UI answer), Layered/N-Tier,
Clean Architecture — get proposed even when Modular Monolith, Vertical Slice,
Cell-Based, or Local-First fits the constraints better. If a draft's
candidate set is only these four, re-check the full list above before
deciding.
