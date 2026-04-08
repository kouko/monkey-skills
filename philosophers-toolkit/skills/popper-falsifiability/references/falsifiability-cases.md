# Falsifiability — Additional Cases

Extended examples for reference.

## "Our Rewrite Will Be Better"

| Step | Content |
|------|---------|
| Original Claim | "Rewriting the backend in Rust will solve our performance problems" |
| Operationalized | "After the Rust rewrite, p99 latency for the top 5 endpoints will drop below 50ms under 1000 concurrent users, compared to the current 300ms in Python" |
| Falsification Test | If p99 latency remains at or above 50ms after rewrite, the hypothesis is falsified |
| Evidence | No rewrite has been attempted yet; profiling shows 80% of latency comes from database queries, not application code |
| Verdict | **Falsified (pre-test)** — existing evidence suggests the bottleneck is database I/O, not language runtime. Rewriting in Rust would not address the actual cause. Reformulation: "Optimizing our top 5 database queries will reduce p99 latency below 100ms" |

## "Tests Slow Us Down"

| Step | Content |
|------|---------|
| Original Claim | "Writing unit tests slows down development" |
| Operationalized | "Teams that write unit tests for new features have a higher median lead time (ticket to production) than teams that skip tests, measured over the last quarter" |
| Falsification Test | If test-writing teams have equal or lower lead time, the hypothesis is falsified |
| Evidence | Team A (with tests): median lead time 5 days, rollback rate 2%. Team B (no tests): median lead time 4 days, rollback rate 18%. Team B spends ~3 days/sprint on production hotfixes |
| Verdict | **Falsified** — while raw lead time is slightly lower without tests, total cycle time (including hotfix rework) is higher. The operationalized claim survived narrowly, but a reformulated claim "tests slow us down overall" is falsified when rework is included |

## "Kubernetes Is Overkill for Us"

| Step | Content |
|------|---------|
| Original Claim | "We don't need Kubernetes — it's overkill for a team our size" |
| Operationalized | "A team of 5 engineers maintaining 3 services will spend more time on K8s operations (setup, debugging, upgrades) than on manual deployment, measured in hours per month" |
| Falsification Test | If K8s operational overhead is less than or equal to manual deployment overhead per month, the hypothesis is falsified |
| Evidence | Current manual deployment: ~20 hours/month (deploys, rollbacks, environment inconsistencies). Estimated K8s overhead after initial setup: ~30 hours/month (cluster management, YAML debugging, upgrade cycles). Initial setup cost: ~80 hours |
| Verdict | **Survived** — for a team of 5 with 3 services, the operational overhead of K8s appears to exceed manual deployment. However, this should be re-tested if the team grows to 10+ or services exceed 8, where manual coordination costs may tip the balance |

## "Our Users Want Feature X"

| Step | Content |
|------|---------|
| Original Claim | "Users want a dark mode" |
| Operationalized | "If we ship dark mode, at least 30% of active users will enable it within 30 days of release" |
| Falsification Test | If fewer than 30% of active users enable dark mode within 30 days, the hypothesis is falsified |
| Evidence | Feature request survey: 45 responses mentioning dark mode out of 12,000 active users (0.375%). No A/B test conducted. Vocal minority on social media |
| Verdict | **Unfalsifiable (currently)** — survey data shows low signal; social media is not representative. The claim "users want dark mode" lacks a clear denominator. Reformulation: run a feature flag with 10% of users, measure actual adoption before full build |

## "Monorepo Will Improve Collaboration"

| Step | Content |
|------|---------|
| Original Claim | "Moving to a monorepo will improve cross-team collaboration" |
| Operationalized | "After migrating to a monorepo, the number of cross-team PRs (PRs touching code owned by another team) will increase by at least 50% within 3 months" |
| Falsification Test | If cross-team PRs increase by less than 50% after 3 months, the hypothesis is falsified |
| Evidence | Pre-migration: 8 cross-team PRs per month. Post-migration (month 1-3 average): 11 cross-team PRs per month (37.5% increase) |
| Verdict | **Falsified** — cross-team PRs increased by 37.5%, below the 50% threshold. The monorepo made cross-team changes easier but did not reach the hypothesized level of collaboration improvement. Possible confound: organizational incentives matter more than repository structure |

## Real-World Cases

### Netflix: DVD-by-Mail → Streaming → Content Creation

| Step | Content |
|------|---------|
| Original Hypothesis | "Customers want convenient DVD rental by mail" |
| Falsification Signal | Streaming technology matured; download speeds increased; customer behavior shifted toward instant access |
| What Netflix Did | Treated each business model as a falsifiable hypothesis. When evidence showed streaming was overtaking DVD, pivoted — didn't cling to the original model |
| Key Insight | Netflix's willingness to cannibalize its own DVD business is Popperian: the hypothesis "DVD-by-mail is the best delivery model" was falsified by market evidence, and they accepted it |

### Spotify Car Thing: Hardware Hypothesis Falsified

| Step | Content |
|------|---------|
| Original Hypothesis | "Consumers want a dedicated Spotify hardware device for cars" |
| Operationalized | Ship a physical product (Car Thing) and measure adoption and retention |
| Falsification Evidence | Low sales, weak retention, customers preferred using their phones |
| Verdict | **Falsified** — Spotify discontinued Car Thing and redirected resources. Didn't persist with a falsified premise |
| Key Insight | Fast falsification saved resources. A non-Popperian company would have doubled down on marketing instead of accepting the evidence |

### Google: The Product Graveyard as Falsification Machine

| Step | Content |
|------|---------|
| Pattern | Google launches products as hypotheses, kills them when falsified |
| Examples | Google+ (hypothesis: users want a Google social network — falsified by low engagement), Google Glass (hypothesis: consumers want AR glasses — falsified by social rejection and limited use cases), Inbox (hypothesis: users want email reimagined — falsified by low migration from Gmail) |
| Key Insight | Google's "graveyard" is not failure — it's a systematic falsification process. Products that survive testing (Search, Maps, YouTube) are the ones whose hypotheses were not falsified |

Source: [Falsifiable Hypotheses in Data Science Practice — Crow Intelligence](https://crowintelligence.org/2025/02/25/falsifiable-hypotheses-how-poppers-philosophy-transformed-my-data-science-practice/)

## Sources

- Popper, K. (1934). *The Logic of Scientific Discovery*
- Popper, K. (1963). *Conjectures and Refutations*
- [Stanford Encyclopedia of Philosophy — Karl Popper](https://plato.stanford.edu/entries/popper/)
- [Falsifiability in Software Engineering — Hillel Wayne](https://www.hillelwayne.com/post/falsifiable/)
- [Falsifiable Hypotheses in Data Science — Crow Intelligence](https://crowintelligence.org/2025/02/25/falsifiable-hypotheses-how-poppers-philosophy-transformed-my-data-science-practice/)
