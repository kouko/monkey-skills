# First Principles — Additional Cases

Extended examples for reference.

## SpaceX: Rocket Cost

| Phase | Content |
|-------|---------|
| Conventional | Rockets cost $65M because that's what aerospace companies charge |
| Problem Essence | Get payload to orbit affordably |
| Assumption Challenged | "Rockets are inherently expensive" — based on industry pricing, not physics |
| Ground Truths | Raw materials (aluminum, titanium, carbon fiber) cost ~2% of rocket price; physics of orbital mechanics is fixed |
| First-Principles Solution | Build rockets from raw materials with vertical integration; reuse boosters (landing them) |
| Result | Falcon 9 cost reduced to ~$28M, reusable variant even lower |

Source: [awesome-skills/first-principles-skill](https://github.com/awesome-skills/first-principles-skill/blob/main/references/elon-musk-examples.md)

## Tesla: Battery Cost

| Phase | Content |
|-------|---------|
| Conventional | Batteries cost $600/kWh because that's the market price |
| Problem Essence | Store energy affordably for electric vehicles |
| Assumption Challenged | "Battery costs are determined by the market" — but what determines the market? |
| Ground Truths | Battery components (cobalt, nickel, lithium, carbon) cost ~$80/kWh at commodity prices |
| First-Principles Solution | Build own battery factory, optimize cell chemistry, vertical integration |
| Result | Cost reduced toward $100/kWh, enabling mass-market EVs |

## Microservices Architecture Review

| Phase | Content |
|-------|---------|
| Conventional | "We need microservices for scalability" |
| Problem Essence | Handle increasing load without degrading user experience |
| Assumptions Challenged | "Microservices = scalability" (false: monoliths can scale horizontally too); "Our team is big enough for microservices" (unverified: 4 developers) |
| Ground Truths | Load increases 10x in 2 years; team is 4 people; deployment must not cause downtime |
| First-Principles Solution | Horizontally scaled monolith with zero-downtime deployment; split into services only when team grows past coordination limits |

Source: Adapted from [awesome-skills/first-principles-skill](https://github.com/awesome-skills/first-principles-skill/blob/main/examples/architecture-review.md)

## Frontend Framework Selection

| Phase | Content |
|-------|---------|
| Conventional | "We should use React because it's the most popular" |
| Problem Essence | Render interactive UI efficiently with our team's capabilities |
| Assumptions Challenged | "Popular = best for us" (analogy trap); "We need a SPA" (unverified) |
| Ground Truths | Most pages are content-heavy with minimal interactivity; team has strong HTML/CSS skills; SEO matters |
| First-Principles Solution | Server-rendered HTML with progressive enhancement; sprinkle interactivity only where needed |

## Build vs Buy

| Phase | Content |
|-------|---------|
| Conventional | "We should build our own X because we need customization" |
| Problem Essence | Solve specific business problem with sustainable maintenance cost |
| Assumptions Challenged | "We need full customization" (do we? which parts?); "Building is cheaper long-term" (total cost including maintenance?) |
| Ground Truths | We need 3 custom features; the other 20 features are standard; team has 2 developers for maintenance |
| First-Principles Solution | Buy standard tool, customize only the 3 features via API/plugins; don't build the 20 standard features |

## Sources

- [awesome-skills/first-principles-skill](https://github.com/awesome-skills/first-principles-skill) (MIT License)
- [Aristotle on First Principles — Stanford Encyclopedia](https://plato.stanford.edu/entries/aristotle-causality/)
