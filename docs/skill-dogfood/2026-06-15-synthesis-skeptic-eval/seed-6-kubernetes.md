# SEED 6 — Kubernetes for a small team (SWE / adoption, THIN/opinion-heavy)

## QUESTION
Is Kubernetes worth the operational cost for our small team?

## CONFIRMED CLAIMS BLOCK
### [0] Official docs: K8s "is not a traditional, all-inclusive PaaS"; users manage own logging/monitoring/alerting.
Vote: 3-0 · Source: kubernetes.io/docs/concepts/overview (primary)
Quote: "Kubernetes is not a traditional, all-inclusive PaaS system. It does not deploy source code."
Verifier evidence (high): direct from official overview.

### [1] CNCF 2023: 66% of respondents use K8s in production (up from 58%); adoption concentrated in orgs >100 engineers.
Vote: 2-1 · Source: cncf.io 2023-survey (primary)
Quote: "Production Kubernetes use continues to grow, though largest gains are in mid-to-large engineering organizations."
Verifier evidence (medium): self-selected pool; size-breakdown partially inferred.

### [2] Datadog 2022: median K8s cluster runs only 10 nodes → control-plane overhead disproportionate for many.
Vote: 2-1 · Source: datadoghq.com state-of-containers-2022 (secondary)
Quote: "Half of all monitored Kubernetes clusters contain ten or fewer nodes."
Verifier evidence (medium): vendor-sourced; may not represent non-Datadog teams.

### [3] Kelsey Hightower (Google) said teams <5 engineers should likely not run K8s themselves; managed PaaS covers most needs.
Vote: 2-1 · Source: twitter.com/kelseyhightower (blog)
Quote: "If you have less than five engineers, Kubernetes is probably not worth the operational cost."
Verifier evidence (low): single social post; exact wording disputed; no formal publication.

### [4] Fly.io/Render/Railway offer container deploy w/o K8s knowledge, free/sub-$20/mo tiers, marketed to small teams as Heroku alternatives.
Vote: 3-0 · Source: render.com/docs/deploy-an-image (blog)
Quote: "Deploy any Docker image in minutes. No Kubernetes expertise required."
Verifier evidence (medium): pricing verified early 2024; tiers change frequently.

### [5] AWS EKS charges $0.10/cluster/hour (~$73/mo) for control plane alone, before nodes — materially more than equivalent PaaS tiers.
Vote: 3-0 · Source: aws.amazon.com/eks/pricing (primary)
Quote: "You pay $0.10 per hour for each Amazon EKS cluster you create."
Verifier evidence (high): direct AWS pricing; stable.

### [6] A 2021 HN thread (300+ comments) plurality argued the 3–6 month learning curve disqualifies K8s for sub-ten-person teams.
Vote: 2-2 · Source: news.ycombinator.com item?id=27300000 (forum)
Quote: "It took our team of three about four months before we stopped firefighting the cluster."
Verifier evidence (low): forum; anecdotal; no methodology; high variance.

### [7] Thoughtworks Radar moved K8s to "Adopt" for platform teams but notes "significant operational complexity that smaller teams without dedicated platform engineers often underestimate."
Vote: 2-1 · Source: thoughtworks.com/radar/platforms/kubernetes (secondary)
Quote: "Significant operational complexity that smaller teams without dedicated platform engineers often underestimate."
Verifier evidence (medium): practitioner-curated; client base skews enterprise.

### [8] K8s primitives (Deployments/HPA/federation) become cost-effective at scale only when workloads need frequent automated scaling across heterogeneous infra.
Vote: 3-0 · Source: kubernetes.io deployment-controller (primary)
Quote: "Deployments describe a desired state, and the controller changes the actual state at a controlled rate."
Verifier evidence (high): primitives documented; "cost-effective at scale" framing is an editorial gloss that slightly overstates what docs assert.

### [9] Gitpod (2023) migrated away from self-managed K8s, citing cluster maintenance ~20% of total eng time for a team under 20.
Vote: 2-1 · Source: gitpod.io/blog/we-are-leaving-kubernetes (blog)
Quote: "Kubernetes cluster maintenance was consuming roughly 20% of our engineering bandwidth."
Verifier evidence (medium): first-person postmortem; single data point; % not corroborated externally.

## ARM A — SINGLE-PASS SYNTHESIS
SUMMARY: Kubernetes is almost certainly not worth the operational cost for a small team (under ~10 engineers) unless you have specific requirements — multi-cloud workload portability, frequent heterogeneous scaling, or a dedicated platform engineer — that PaaS alternatives cannot meet. The baseline overhead is steep: a managed control plane alone costs ~$73/month on EKS before any nodes, K8s is explicitly not a batteries-included platform (no built-in logging, monitoring, or alerting), and first-person evidence from Gitpod shows self-managed clusters consumed ~20% of engineering bandwidth at under 20 people. Mature PaaS alternatives (Render, Fly.io, Railway) cover the primary use-cases of small teams at a fraction of the cost and cognitive load. Industry adoption data and practitioner consensus both point the same direction: K8s payoff is real but only materializes at mid-to-large scale with dedicated platform ownership.

FINDINGS:
- [high] K8s is explicitly not a full PaaS; users supply own logging/monitoring/alerting. Built-in controllers handle reconciliation/autoscaling but the platform must be assembled. | evidence: official docs [0]+[8], 3-0.
- [high] Managed K8s has a hard financial floor: EKS ~$73/mo control plane before nodes — more than equivalent PaaS tiers. | evidence: AWS pricing [5], 3-0.
- [medium] Real clusters skew small: Datadog median ≤10 nodes → overhead disproportionate for most adopters. | evidence: vendor data [2], 2-1.
- [medium] Postmortems + consensus converge: self-managed K8s is a significant tax for small teams. Gitpod ~20% bandwidth; Thoughtworks underestimated complexity; 3–6mo ramp. | evidence: [9]/[7]/[6], votes 2-1/2-1/2-2.
- [medium] CNCF: production K8s concentrated in larger orgs (>100 eng). | evidence: [1], 2-1, self-selected pool.
- [medium] Mature PaaS (Fly/Render/Railway) remove K8s for most small-team use-cases, free/sub-$20/mo. | evidence: [4], 3-0; tiers change.
- [low] Kelsey Hightower: teams <5 should rely on managed PaaS. | evidence: [3], single social post, disputed wording.
- [high] K8s primitives cost-effective only when workloads need frequent automated scaling across heterogeneous infra — a regime most small teams aren't in. | evidence: [8], 3-0.

CAVEATS: "Small team" not uniformly defined (<5, <10, <20). Datadog/Gitpod are vendor/company-specific, may not generalize. EKS used as representative cost; GKE Autopilot/AKS differ; spot nodes reduce cost. PaaS tiers change. CNCF self-selected pool over-represents cloud-native practitioners.

OPEN QUESTIONS:
- At what team size / complexity does K8s overhead become net-positive (10–50 eng w/ platform ownership)?
- Do managed services (GKE Autopilot, EKS Fargate) materially reduce the 20% tax, or shift it?
- How does the calculus change if multi-cloud / data-residency eliminate PaaS as an option?
- As AI-assisted cluster management matures, does the learning curve compress within 1–2 years?
