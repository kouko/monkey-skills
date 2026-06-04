# SaaS / tech-industry context for 4DX + OKR-vs-4DX deep comparison

> **Purpose**: deeper research note answering two related questions:
>
> 1. **Why does industry view 4DX as poorly-suited to SaaS / software-tech, and what does this mean specifically for a restaurant POS SaaS (Company A) and an OMO e-commerce platform (Company B) target users?**
> 2. **What are the substantive differences between OKR and 4DX, and when do organizations choose one over the other?**
>
> **Status**: human reference document, NOT loaded by skills at runtime. Lives in `research/` per the inventory's plugin-shared-paths-not-supported finding.
>
> **Last updated**: 2026-05-01
>
> **Methodology**: 5 web searches (EN + zh-TW); 4 direct WebFetch + playwright reads of primary blog / interview / comparison sources; cross-validation against case-inventory.md Tier 1 findings.

---

## Part 1 — Why 4DX is considered poorly-suited to SaaS / software-tech

### The structural argument (validated across multiple sources)

The single most-cited limitation, paraphrased and quoted across multiple practitioner sources:

> **Lead measures (4DX D2) require *stable, repeatable behaviors* to anchor against. Software / engineering / research / design work has *shifting weekly priorities*. When the right activity this week may be the wrong one next week, fixed lead measures calcify into "activity theater" — work done to satisfy the metric, not work done to move the goal.**

Verbatim from mooncamp's 2024 OKR-vs-4DX comparison:

> *"In research, engineering, or design, the right activity this week can be the wrong one next week. Fixed lead measures in ambiguous work calcify into activity for its own sake."*

> *"4DX tends to fail in ambiguous knowledge work where this week's right activity is next week's wrong one, because fixed lead measures calcify into activity theater."*

Source: https://mooncamp.com/blog/4dx-vs-okr

### Industry-practitioner case anchor: the Goodhart problem in software

A 2014 Lean Beliefs post by "pcsontos" (long-running agile-management practitioner blog) makes this concern verbatim, articulating it from inside agile-software practice:

> *"as none of the examples in the book are from the software industry or even anything close to it, I have big question marks in my head. I have this strange feeling because my strong belief has been so far (based on lots of experience) that **you cannot reliably measure success of software engineering activities in quantitative ways due to the complexity and chaotic nature of this business. It's too easy to do tricks. For example, if the KPI is to produce more features in a given period, you split the features to smaller pieces and you're OK. If the goal is large unit test coverage, you create a big bunch of useless unit tests quickly and the KPI score is happy again.**"*

Source (via Wayback Machine 2019 snapshot): https://web.archive.org/web/20190412183357/http://leanbeliefs.com/2014/01/27/could-coveys-4-disciplines-of-execution-4dx-method-work-in-agile-software-engineering-teams/

This is a verbatim Goodhart-effect concern about D2 lead measures applied to software work — the same failure mode the four-dx-coach skill already grounds via Source 1 (Goodhart 1975) + Sources 3-5 (Wells Fargo / Phoenix VA / Atlanta APS) in `4dx-d2-lead-measures/references/industry-grounding.md`. Software engineering is structurally Goodhart-vulnerable: feature splits, test count gaming, code-line gaming, "PRs merged" gaming.

### The Bravelab.io confirmation (verbatim D2 collapse in dev-shop context)

The closest team-scale evidence is Bravelab.io (Polish digital agency, ~15 ppl) — already documented as Tier 1 ★★★ in `case-inventory.md`. Founder Mariusz Smenżyk's verbatim D2 failure quote:

> *"LEAD measures didn't work. Not everyone was able to define what he needs to do to bring our efforts closer to our LAG measure."*

This is the structural mismatch above, observed in production: dev-shop work is knowledge-heavy, behavior-shifting, ambiguous; behavioral lead measures couldn't be designed because the team couldn't articulate "what behavior reliably moves the lag."

### What the SaaS / tech industry uses instead — OKR

Empirically: every major SaaS / tech company that publicly discusses goal-setting uses OKR, not 4DX. Google (since 1999, John Doerr / Andy Grove lineage), Atlassian, HubSpot, Salesforce, Shopify, Stripe, Notion, Linear, etc. The 4DX-vs-OKR comparison literature uniformly recommends OKR for tech-knowledge-work and 4DX for execution-heavy operational teams.

Quantive's analysis: *"4DX works best for execution-heavy operational teams, while OKRs are better for strategy-heavy knowledge organizations."*
Source: https://quantive.com/resources/articles/okr-vs-4dx

### What this means for the four-dx-coach plugin

When a SaaS / tech user asks the plugin to help adopt 4DX, the agent should:

1. **Surface the structural fit question explicitly, not assume validation.** The literature documents reasoned skepticism, not blanket acceptance.
2. **Route to `4dx-meta-strategy-triage`** to verify that the user's goal genuinely has stable, weekly-controllable behaviors that predict the lag — not just "we want to ship more features this quarter."
3. **If the goal IS execution-heavy (ops, support, sales, customer-success — the parts of a SaaS company that DO have stable behaviors)**: 4DX may genuinely fit. These functions inside a SaaS company are operationally similar to traditional sectors.
4. **If the goal is product / engineering / research / design**: warn that fixed lead measures may calcify; suggest OKR or hybrid (OKR strategic layer + 4DX execution layer for the parts that do have stable behaviors).
5. **For founder-scope** (indie SaaS / product founder doing personal-scale 4DX): Lou Franco's case (Tier 2 #12 in `case-inventory.md`) is the closest anchor — but it's a binary launch-blocker WIG with hard deadline, not a continuous-metric SaaS WIG.

---

## Part 2 — Specific implications for Company A (a restaurant POS SaaS)

### Company context (verified via public sources + media interviews 2024-2025)

- **Company**: Company A (a Taiwan restaurant POS SaaS vendor)
- **Founded**: 2012, Taipei. Origin in a restaurant the founders ran — operational pain drove product
- **Co-founders**: the co-founders (CEO, Chief Growth Officer, CIO)
- **Scale (2024)**: 10,000+ restaurant clients across Taiwan / Hong Kong / Singapore / Malaysia
- **Business model**: iPad POS + cloud reporting; subscription SaaS for F&B SMBs
- **Going public**: announced IPO trajectory; 2020 onward profitable
- **Sources**: (public company / interview sources)

### Company A's stated framework: OKR (verified via official engineer-interview page)

From Company A's own engineering interview page (public company / interview sources):

Company A uses OKR with individual and team-aligned goal-setting. The stated purpose is not 100% achievement but developing ownership of personal growth. OKRs are reset semi-annually after performance review, with two axes: (1) alignment to team OKR, and (2) alignment to next career level and growth direction.

This is **textbook Google / Doerr-style OKR**:
- Aspirational stretch goals (not 100% achievement target)
- Personal + team alignment via two axes
- Semi-annual cycle (slightly longer than the canonical Google quarterly, but within OKR norms)
- Growth-oriented, not control-oriented

**Company A's cadence + supporting practices**:
- Semi-annual performance reviews + 1:1 with the CTO and the CIO every 6 months
- Weekly fixed knowledge-sharing sessions (engineering)
- Engineer rotation across teams (including frontline support) for cross-functional understanding
- Conference budget for engineers
- Peer-review culture rigorous in engineering

**No mention of 4DX, WIG Sessions, lead measures, or scoreboard-discipline language anywhere in Company A's public engineering content.**

### Why Company A likely chose OKR over 4DX

Inferring from the company's engineering culture + restaurant-tech SaaS context:

1. **Engineering work is the structural bad-fit zone for 4DX D2** — Company A's engineering team writes POS software, reporting features, integrations. This is knowledge-heavy product work where weekly behaviors shift. OKR's quarterly direction-setting + key-result milestones tolerate this; 4DX's weekly behavioral lead measures would struggle.
2. **Customer-side restaurants are a different scope** — the *restaurants using Company A* might benefit from 4DX (their work IS execution-heavy: tickets-cleared, table-turn-time, daily-cover-count have stable behaviors). But Company A the company isn't running 4DX *for itself*; its developers ship a SaaS tool that helps its restaurant customers run better. These are two different contexts.
3. **Growth-stretch culture vs winnable-game culture** — Company A's framing (OKR purpose is not 100% achievement but learning to take responsibility for growth) is the OKR moonshot stance. 4DX is winnable-game-oriented (the team should genuinely be able to hit the WIG by the deadline). These are different cultural posture choices.

### Where 4DX *could* fit inside Company A (if you were to introduce it)

Hybrid pattern (FranklinCovey's own recommended model when both frameworks coexist):
- **OKR layer**: company / team strategic direction (already in place)
- **4DX layer wrapped around 1-2 specific OKRs that need execution discipline**, where:
  - The work has stable behavioral leads (e.g. customer-success outreach quotas; sales call quotas; support-ticket-resolution targets)
  - Not for product engineering itself

For Company A specifically, candidate domains where 4DX *might* add value:
- **Customer-success team** chasing renewal / retention outcomes (stable behaviors: account check-ins per week, training sessions delivered per month)
- **Sales team** for restaurant onboarding (stable behaviors: demos booked, restaurants signed)
- **Support team** for ticket throughput (already operational)

Domains where 4DX would likely *not* fit at Company A:
- Product engineering (POS feature dev)
- Design (UX research, interface iteration)
- Data team (analytics / BI work)
- Founders' strategic direction-setting (company-level OKR layer is appropriate)

---

## Part 3 — Specific implications for Company B (an OMO e-commerce platform)

### Company context

- **Company**: Company B (a publicly-listed Taiwan OMO e-commerce platform)
- **Founder / Chairman**: the chairman (a category-leadership positioning for D2C / OMO; prior company in e-commerce)
- **Founded**: 2013
- **Business model**: OMO (Online Merge Offline) e-commerce SaaS platform; serves mid-large retail brands; subscription + transaction-fee revenue
- **Scale (2024)**: publicly-reported strong revenue growth and record net income; first publicly-listed SaaS service provider in Taiwan
- **Strategic positioning**: a category-leadership positioning — D2C / OMO category leader
- **Sources**: (public company / interview sources)

### Company B's framework — operational metrics, not explicitly OKR or 4DX

Unlike Company A, Company B does not publicly name a goal-setting framework. The CPO and the chairman discuss execution in metric-oriented language:

**Core revenue identity** (paraphrased from public seminar / interview sources):

The company operates on a multiplicative revenue model: Traffic × Conversion Rate × Average Order Value = Revenue. This identity anchors team metric-orientation across all three growth pillars.

**Three-pillar operational system**:
1. eCOM (traffic growth loops)
2. OMO Suite (OMO momentum cycles)
3. Member Systems (member engagement)

**Strategic-philosophy framing** (paraphrased from public interview sources):

The chairman emphasizes that execution speed and action-orientation are core cultural values — "seeing a trend and acting on it" is a stated team characteristic. The chairman also maintains a rigorous continuous-learning practice, running monthly academic-paper study sessions during prior company years to apply academic management research to operational decisions.

### Inference: Company B runs metric-oriented operational discipline, likely with OKR-flavor for direction

**What can be confirmed publicly**:
- Company B runs metric-driven execution culture (Traffic × Conversion × AOV = Revenue identity)
- Action-orientation is a stated cultural pillar
- The chairman is high-rigor with continuous-learning culture (academic-paper monthly sessions)

**What cannot be confirmed from public sources**:
- No public statement of OKR or 4DX adoption
- No public WIG Session / cadence specifics
- No public scoreboard description

**Likely framework state** (inference, not verified):
- Probably OKR (or KPI-derived OKR-flavor) — matches Taiwan tech-industry norm + the metric-orientation visible in public comms
- Possible internal hybrid (OKR for direction, KPI for daily ops) — matches the chairman's career-long practice of running metric-driven scale-up companies

### Why Company B likely doesn't run 4DX (inference)

Same structural reasons as Company A:
1. **Product engineering / data science / OMO platform development** is knowledge-heavy work with shifting weekly priorities — D2 calcification risk
2. **Multi-tenant SaaS retail platform** has multiple parallel customer cohorts — 4DX's "one WIG max" rule is awkward for multi-customer-segment growth
3. **Public-listed company governance** — quarterly investor reporting + KR-style metric-tracking aligns culturally with OKR, not 4DX

### Where 4DX *might* fit inside Company B (similar to Company A analysis)

- **Sales team for retail-brand onboarding** (stable behaviors: demos, signings, deployment milestones)
- **Customer-success team for retention** (stable behaviors: QBRs, training sessions, OMO-feature-adoption nudges)
- **Support / ops team for SLA throughput** (already operational)

But NOT for:
- Product engineering (OMO platform features)
- Data science / AI-recommendation work
- Strategic D2C / category-leadership direction-setting

---

## Part 4 — OKR vs 4DX deep comparison

### Origin & lineage

| Dimension | OKR | 4DX |
|---|---|---|
| **Originator** | Andy Grove (Intel, late 1970s) | Chris McChesney + Sean Covey + Jim Huling (FranklinCovey, early 2000s) |
| **Popularizer** | John Doerr (*Measure What Matters*, 2018, via Google adoption) | Sean Covey + book *4 Disciplines of Execution* (1st ed. 2012, 2nd ed. 2021) |
| **Anchor company** | Google (since 1999) | Marriott / Opryland / Younkers / Sydney accounting / Methodist Le Bonheur / CSN College |
| **Industry tilt** | Tech (Silicon Valley → global SaaS) | Hospitality / healthcare / education / government / manufacturing (operational sectors) |

### Cycle & pace

| Dimension | OKR | 4DX |
|---|---|---|
| **Goal cycle** | Quarterly (canonical Google), some orgs use semi-annual or annual | Continuous; weekly cadence is the load-bearing rhythm |
| **Review meeting** | Quarterly OKR review + monthly check-in | Weekly WIG Session, 30-min ceiling, Account → Review → Plan |
| **Adjustment** | OKRs may be adjusted mid-cycle if context shifts (flexibility = strength) | WIG and lead measures relatively fixed within a cycle (commitment = strength) |
| **Time-box** | Explicit (Q1 OKR, Q2 OKR…) | Less explicit — the WIG runs until achieved or replaced |

### Structural elements

| Element | OKR | 4DX |
|---|---|---|
| **Goal statement** | Objective (qualitative, ambitious, time-boxed) | WIG (Wildly Important Goal): "From X to Y by When" — quantitative, measurable, deadline-bound |
| **Tracking metric** | 2-5 Key Results per Objective, mostly *outcome* metrics | Lead measures (predictive AND influenceable) + Lag measure (the WIG outcome) |
| **Number of goals** | Multiple Objectives allowed (typically 3-5 per team), each with multiple KRs | 1-2 WIGs maximum per team; book mantra: "more than two WIGs = no WIGs" |
| **Achievement target** | Aspirational stretch (Google convention: 60-70% achievement = healthy; 100% = goals were too easy) | Winnable game (the team should genuinely be able to hit the WIG by the deadline) |
| **Posture** | Strategic direction-setting + outcome tracking | Execution discipline + behavioral commitment |

### KR vs Lead Measure — the most-confused distinction

This is the conceptual collision point. Many practitioners conflate KRs with lead measures; they're different:

- **OKR Key Result**: usually an **outcome metric** (customer acquisition, NPS, revenue, retention rate). Measures *what happened*, not *what behaviors caused it*.
- **4DX Lead Measure**: a **behavior** the team can perform this week that is *predictive* of the lag and *influenceable* by the team. Measures *the inputs that drive the outcome*, not the outcome itself.

Erik Eldridge (software engineer, 2019 blog post — verified via wordpress mirror):

> *"4DX describes lead vs lag metrics. For example, we have to wait thirty days to know if we've increased thirty-day active users, so there's a thirty day lag in the metric. As opposed to other metrics, e.g., signups per day, features built, etc., that can be measured on a smaller scale and correlate with increasing thirty-day actives. Objectives seem like lag metrics, and KRs like lead metrics."*

Eldridge's mapping is a useful first-cut but slightly imprecise: KRs in canonical OKR are usually **lag-shaped outcome metrics** ("MRR grows from $X to $Y", "NPS rises from N to M"). 4DX leads are **upstream behaviors** ("send 50 personalized outreach emails per week", "complete 3 customer-success calls per week"). The two frameworks measure at different layers of the cause→effect chain.

### Strengths

| OKR | 4DX |
|---|---|
| Cross-team alignment at scale ("connecting everyone's goals to the company's overall strategy") | Weekly accountability discipline against the whirlwind ("ensuring the team stays locked in on what really matters") |
| Flexibility — KRs can be adjusted mid-cycle as context shifts | Focus discipline — explicit constraint to ≤2 WIGs forces real prioritization |
| Aspirational goal-setting culture (60-70% achievement is healthy) | Winnable-game culture (commitment to deliverable outcomes) |
| Quarterly time-box gives natural retrospective rhythm | Lead-measure lens gives mechanism-of-action visibility (not just outcome tracking) |

### Weaknesses

| OKR | 4DX |
|---|---|
| Doesn't prescribe HOW teams should execute; teams can have great OKRs with poor execution | Rigidity — fixed lead measures calcify in ambiguous knowledge work |
| Risk of becoming KPI-tracking-with-extra-steps if the moonshot culture isn't enforced | No native time-box (cycles are open-ended; some practitioners argue 4DX lags OKR on this) |
| KR-design is hard; teams default to lag metrics that don't reveal the work | D2 (lead measures) is "the most-misunderstood discipline" per book Ch 3 + practitioner consensus |
| Works less well in operational / execution-heavy teams where the whirlwind crushes strategy | Works less well in knowledge-heavy domains where weekly behaviors shift |

### When organizations choose which (the canonical pattern)

| Choose **OKR** when | Choose **4DX** when | Choose **both** when |
|---|---|---|
| Cross-team alignment matters | The whirlwind is winning | OKR sets quarterly direction; 4DX wraps around 1-2 OKRs that need execution discipline |
| Knowledge-heavy work (research, engineering, design, product) | Operational / execution-heavy work (ops, support, sales, customer-success) | Tech company has BOTH product-engineering AND operational functions |
| Aspirational stretch culture | Winnable-game culture | Hybrid is FranklinCovey's own recommended model |
| Quarterly cycle natural | Weekly cadence natural | Each layer plays its role |

### When organizations specifically reject 4DX for tech work

The recurring pattern in practitioner-reflection literature:

1. **Goodhart vulnerability** — "feature splits, test count, code lines, PRs merged" all gameable (Lean Beliefs 2014)
2. **Behavior instability** — "the right activity this week can be the wrong one next week" (mooncamp)
3. **D2 collapse in practice** — "LEAD measures didn't work" (Bravelab.io 2021)
4. **Cross-team work mismatch** — most book examples are single-team operational; tech orgs have multiple parallel projects with shifting members (multiple Lean Beliefs / mooncamp critiques)

---

## Part 5 — Synthesis: what should the four-dx-coach plugin do for SaaS / tech users?

### Activation behavior recommendations

When a SaaS / tech user (especially product-engineering / design / research role) activates the plugin:

1. **Surface the structural fit question proactively in `4dx-meta-strategy-triage`** — agent should not assume 4DX validation. Ask explicitly:
   - "Does the work you want to apply 4DX to have stable, weekly-controllable behaviors that predict the lag? Or does the right activity shift week-by-week?"
   - "Are you planning 4DX for an execution-heavy function (sales, ops, customer-success) or a knowledge-heavy function (engineering, product, design, research)?"
2. **If knowledge-heavy**: route output should suggest hybrid (OKR + 4DX-around-execution-OKRs) or pure-OKR alternative; do not pretend 4DX is uncomplicated for the domain.
3. **If execution-heavy** (even inside a SaaS company): proceed with 4DX confidently; cite Bravelab.io as a partial-success/partial-failure anchor (D1 succeeded; D2 collapsed because dev-shop work isn't stable behavior — relevant if the user is also in dev work).
4. **For founders / solo product builders**: cite Lou Franco's case (binary launch-blocker WIG with hard deadline) as the closest fit; note it's solo personal scope, not team scale.

### What NOT to do

- Do not present 4DX as universally suitable for SaaS / tech.
- Do not dismiss OKR or treat it as inferior — for tech work, OKR is the default-correct framework.
- Do not generate hypothetical SaaS WIGs without first running the structural fit question.
- Do not frame 4DX as competing with OKR when the FranklinCovey-recommended pattern is actually hybrid (4DX wrapped around 1-2 OKRs).

### What new skill behavior could optionally be added (deferred decision)

Consider adding to `4dx-meta-strategy-triage`:

- A **"knowledge work vs operational work" gate** as a pre-check before fit-verdict
- A **"is your work behavior-stable?"** Socratic prompt
- An **"OKR-instead-of-4DX" verdict option** for clear knowledge-work cases (currently the verdict palette is APPLICABLE / TEAM-APPLICABLE / stroke-of-pen / whirlwind / habit / portfolio / emergency / creative / no-time-sovereignty / wrong-team-shape / single-shot / mission-misaligned / TEAM-NOT-YET-READY — does not include "knowledge-work-route-to-OKR")

This is an architecture-level decision; recorded here as a pointer, not implemented.

---

## Part 6 — Company A / Company B specific takeaways

### Company A (verified)

- **Confirmed**: Company A runs OKR (semi-annual cycle, individual + team alignment, growth-orientation, not 100%-achievement-target).
- **Inferred**: 4DX would not be a natural fit for Company A's engineering team (knowledge-heavy POS development).
- **Possible 4DX use cases inside Company A**: customer-success team chasing renewal; sales team for restaurant onboarding; support throughput. NOT product engineering.
- **What the plugin should do**: if a user from Company A asks for 4DX coaching, recommend keeping company-level OKR + considering 4DX for specific operational sub-teams only.

### Company B (partially verified)

- **Confirmed**: Company B runs metric-driven operational discipline (Traffic × Conversion × AOV = Revenue identity) with strong action-orientation culture.
- **Inferred (not confirmed)**: probably OKR or OKR/KPI hybrid; consistent with Taiwan tech-listed-company norms + the chairman's career-long metric-driven scale-up practice.
- **Inferred non-fit for 4DX**: same reasons as Company A — product engineering / data science / OMO platform work is knowledge-heavy.
- **Possible 4DX use cases inside Company B**: brand-onboarding sales team; customer-success for OMO-feature adoption; support throughput. NOT product or data team.
- **What the plugin should do**: same as Company A — recommend keeping company-level direction framework + considering 4DX for specific operational sub-teams only.

### Common pattern: "SaaS company runs OKR for the whole business, may wrap 4DX around specific operational sub-teams"

This is the FranklinCovey-endorsed hybrid pattern. It explicitly is NOT "SaaS company adopts 4DX as primary framework" — that pattern is rare and structurally fragile.

---

## Sources cited

1. **mooncamp 4DX vs OKR** (verified WebFetch read, 2026-05-01) — https://mooncamp.com/blog/4dx-vs-okr — comprehensive verbatim limitations of 4DX in knowledge work.
2. **Quantive OKR vs 4DX** (verified search snippet) — https://quantive.com/resources/articles/okr-vs-4dx — execution-vs-strategy framing.
3. **Lean Beliefs 2014** (verified via Wayback playwright read, 2026-05-01) — verbatim Goodhart concerns about 4DX in agile software engineering.
4. **Erik Eldridge 2019** (verified via wordpress mirror playwright read, 2026-05-01) — software engineer's perspective; OKR-Objectives-as-lag / KRs-as-lead mapping.
5. **Bravelab.io / Smenżyk 2021** (already in case-inventory.md Tier 1) — verbatim D2 collapse in dev-shop context.
6. **Lou Franco 2024** (already in case-inventory.md Tier 2 #12) — indie SaaS founder personal-scope 4DX series.
7. **Company A public engineering/interview sources** (verified WebFetch read) — (public company / interview sources) — OKR adoption + cadence details.
8. **Company A public engineering/interview sources** (verified search) — (public company / interview sources) — founder background and company origin.
9. **Company B public seminar/interview sources** (verified WebFetch read) — (public company / interview sources) — Traffic × Conversion × AOV revenue identity.
10. **Company B public seminar/interview sources** (verified search) — (public company / interview sources) — strategic positioning and chairman philosophy.
11. **Multiple OKR-vs-4DX comparison sources** — perdoo, keka, peoplestrong, tability.io, datalligence, simplamo, reclaro — cross-validated convergence on the canonical pattern documented in Part 4.

---

## Part 7 — Cross-framework coordination: "engineering uses OKR, sales uses 4DX" pattern

### The honest empirical finding

**No verified named real-company case** exists for "engineering team uses OKR + sales team uses 4DX simultaneously in the same company." The hybrid pattern is widely promoted theoretically by FranklinCovey, Workpath, Simplamo, mooncamp, and others — but the published case literature does not document a specific named company running this dual-framework horizontal split. (Workpath's only named case study is DB Schenker, which uses OKR alone, not OKR+4DX hybrid.)

Sources searched 2026-05-01: 5 EN web searches across "OKR + 4DX hybrid", "FranklinCovey hybrid model", "dual framework engineering sales different department", "4DX sales SaaS implementation", "channel sales 4DX". All surface theoretical hybrid guidance; none surface a named real-company case for the specific horizontal pattern.

### Why the published guidance describes vertical hybrid, not horizontal

The hybrid model FranklinCovey + practitioner-blog literature describes is **vertical**, not **horizontal**:

- **Vertical hybrid** (the documented pattern): Same goal exists in BOTH frameworks at different layers. OKR sets quarterly Objective ("grow ARR by $5M in Q3"); 4DX wraps this Objective as a WIG with weekly cadence ("from $X ARR to $Y ARR by Sept 30"). Each team uses BOTH layers.
- **Horizontal hybrid** (the user's question): DIFFERENT goals exist in DIFFERENT frameworks across departments. Engineering team has OKR ("ship feature set X by Q3"); sales team has independent 4DX WIG ("close $5M ARR by Sept 30"). Each team uses ONE framework.

FranklinCovey's recommended pattern is vertical because it preserves single-language alignment across the org. Horizontal hybrid is rare in published literature because it introduces coordination friction (documented below). When companies in practice run "different frameworks for different departments," the coordination cost is usually absorbed quietly without published case studies.

### Where horizontal hybrid coordination friction actually surfaces

Four predictable friction points if engineering runs OKR (quarterly cycle + aspirational stretch + outcome-shaped KRs + knowledge-work-shaped) and sales runs 4DX (weekly cadence + winnable-game commitment + behavioral-lead-shaped):

> **Cadence-framing correction (2026-05-01 same-day update)**: an earlier draft of this section framed the cycle distinction as "OKR=quarterly only vs 4DX=weekly". This was inaccurate. **Canonical OKR has a weekly cadence too** — Wodtke's *Radical Focus* (2016/2021) explicitly recommends Monday commitments + Friday wins meetings; Doerr's *Measure What Matters* (2018) documents Google's weekly OKR check-ins. See `okr-primary-sources.md` Sources 2-3. The structural difference between OKR weekly and 4DX weekly is **what gets committed**: OKR weekly = confidence-update + priorities; 4DX weekly = hard behavioral commitment via Account → Review → Plan. The friction below is therefore not "weekly vs quarterly" but rather "confidence-update cadence vs hard-commitment cadence" plus the OKR vs 4DX cycle-boundary structure (OKR has clear quarterly bookends; 4DX runs continuously until WIG hit/replaced).

#### Friction 1: Cycle-boundary mismatch (engineering's quarterly bookend vs sales' continuous WIG)

Engineering's OKR quarter has a clear bookend: "we'll re-evaluate at Q3 retro." Sales' 4DX WIG runs continuously until achieved or replaced. When sales' weekly WIG Session surfaces a roadblock that depends on an engineering quarterly OKR deliverable, sales needs an answer THIS week — but engineering's natural bookend is the quarter end, even though engineering DOES have weekly OKR check-ins of its own. The mismatch isn't that engineering doesn't run weekly cadence; it's that engineering's weekly cadence is *confidence-update-shaped* not *hard-commitment-shaped*, so engineering's weekly answer to sales is "still on track / might slip / blocker noted" rather than "I commit to delivering X by Friday."

**Coordination pattern**: agree at quarterly OKR boundary which engineering deliverables sales can depend on this quarter; engineering creates sub-OKR specifically for sales-enabling deliverables; this sub-OKR carries 4DX-style WINNABLE-game commitment framing (sub-OKR's KRs explicitly become committed, not aspirational); sales' WIG depends only on this sub-OKR (NOT engineering's broader roadmap); cross-team weekly 1:1 reviews this slice only with explicit hard-commitment language. The friction-resolving move is **converting the relevant slice of engineering's OKR to 4DX-flavor hard commitments**, not changing engineering's broader cycle.

#### Friction 2: Achievement-culture mismatch (60-70% vs winnable-game)

Engineering OKR culture: stretch goals, 60-70% achievement is healthy. Sales 4DX culture: winnable game, hit the WIG by deadline. When sales-depends-on-engineering, sales models engineering's deliverables as commitments (4DX framing); engineering models them as stretch goals (OKR framing). Same artifact gets read two ways.

**Coordination pattern**: engineering's sales-enabling sub-OKR explicitly carries WINNABLE-game framing (no 60-70% target — these are commitments, not stretch). Engineering's broader strategic OKR keeps stretch framing. The dual framing is explicit at sub-OKR level, with documented expectation that sales-enabling sub-OKR achievement target = 95-100%.

#### Friction 3: Metric-shape mismatch (KR-as-outcome vs Lead-as-behavior)

Engineering KRs are usually outcome-shaped lag metrics ("ship feature X"; "reduce p99 latency to 200ms"). Sales 4DX leads are behavior-shaped predictive metrics ("50 outreach emails per week"; "3 demos per week per AE"). When sales asks engineering for a "lead measure on the engineering deliverable," engineering doesn't have one — they have a milestone-shaped KR.

**Coordination pattern**: when an engineering deliverable is on the sales-WIG critical path, ask engineering to surface a *behavioral lead measure* alongside the milestone-shaped KR. E.g., milestone-KR = "feature X shipped"; behavioral lead = "code reviews on feature X completed within 24h" (engineering can run this weekly; sales can see it weekly). Engineering may resist (this isn't OKR-natural language) — the workaround is asking engineering to add the behavioral lead as a *4DX-style annotation* on the sub-OKR, not as a full new KR.

#### Friction 4: Meeting-rhythm mismatch (sprint review + quarterly OKR retro + OKR weekly check-in vs WIG Session weekly)

Engineering's natural meeting stack: sprint review (2-3 weekly) + OKR weekly check-in (Wodtke Mondays/Fridays) + quarterly OKR retro. Sales' natural meeting: weekly WIG Session (≤30 min, Account → Review → Plan). If a cross-functional WIG depends on engineering deliverables, the question is which of engineering's three meetings is the right place for sales-side accountability — sprint review is too internal-engineering, OKR weekly check-in is confidence-update-shaped (not commitment-shaped), and engineering rep showing up at sales WIG Session adds a fourth meeting to engineering's calendar.

**Coordination pattern**: weekly WIG Session has a *brief* engineering-status segment (2 min, slot-locked) where engineering rep reports binary "on track / blocker surfaced". Detail-level engineering review happens in engineering's own sprint review or sub-OKR check-in. Engineering rep at WIG Session functions as a one-way status conduit, not a debate partner.

### Cross-framework coordination patterns (synthesized)

If you decided to run horizontal hybrid (engineering OKR + sales 4DX) despite the friction points above, four practical patterns:

#### Pattern A — Sub-OKR / WIG-dependency contract (highest discipline)

1. At quarterly OKR-setting boundary, sales WIG owner + engineering OKR owner negotiate *sales-enabling sub-OKR*: a slice of engineering's quarter explicitly committed to sales' WIG critical path
2. Sub-OKR has WINNABLE-game framing (95-100% target), not stretch framing
3. Sub-OKR carries milestone-KR (engineering's natural shape) + behavioral-lead annotation (4DX shape) so sales can read it weekly
4. Sales' WIG depends ONLY on this sub-OKR, not on engineering's broader roadmap
5. Cross-team weekly 1:1 (sales lead + engineering lead) reviews sub-OKR slice; lasts ≤15 min; not the same as sales' WIG Session

#### Pattern B — Embedded engineering rep at sales WIG Session (medium discipline)

1. Sales WIG Session has a 2-min slot for engineering rep to report sub-OKR status
2. Engineering rep is the sub-OKR owner, not a generalist
3. Status format: "on track / blocker surfaced [if blocker, owner-of-blocker-resolution named]"
4. Detail discussion deferred to async or to engineering's own sprint review
5. Engineering rep does NOT make weekly behavioral commitments at sales WIG Session — that's the engineering OKR cycle's job

#### Pattern C — Joint scoreboard for the cross-functional WIG (highest visibility)

1. Sales WIG scoreboard shows BOTH sales execution (lead+lag) AND engineering deliverable status (sub-OKR milestone)
2. Both teams can see "are we winning the joint outcome?" at one glance
3. Eliminates the "we did our part, you missed yours" framing — both teams own the WIG
4. Most useful when sales and engineering share an outcome metric (e.g. enterprise-deal close, where engineering's feature shipping is critical-path)

#### Pattern D — Quarterly re-anchoring (bookend pattern)

1. At quarter boundary, both teams attend joint OKR-WIG retro
2. Sales WIG carried forward, retired, or replaced based on quarter results
3. Engineering OKR cycle generates next quarter's sales-enabling sub-OKR
4. Cross-functional dependencies for next quarter explicitly negotiated, not assumed
5. Bookend prevents drift between weekly cadence and quarterly cadence

### What goes wrong if coordination is not designed deliberately

Four predictable failure modes:

1. **Sales blames engineering for WIG slip** — sales' WIG misses target because engineering didn't deliver; sales-side post-mortem reads "blocked by engineering"; engineering-side OKR retro reads "shipped 70% of stretch goals = healthy quarter". Both interpretations are internally coherent, opposite in implication.
2. **Engineering feels overrun by weekly demands** — sales' WIG Session generates weekly questions for engineering ("when is feature X shipping?"); engineering's natural rhythm is bi-weekly sprint review or quarterly OKR; engineering rep at WIG Session feels like reporting to a different cadence-clock than the rest of engineering.
3. **Cultural-bonus mismatch resentment** — sales hits 100% of WIGs (winnable-game); engineering hits 70% of OKRs (stretch); if compensation is tied to achievement %, sales gets bonuses, engineering doesn't, despite engineering doing harder work. This corrodes cross-team trust over multiple quarters.
4. **Cadence drift** — engineering treats weekly WIG Session attendance as low-priority; engineering rep increasingly skips; weekly visibility into sub-OKR status degrades; sales loses early-warning on engineering blockers; WIG slips at quarter end without intermediate signals.

### What this means for the four-dx-coach plugin

When a SaaS / tech user describes a horizontal-hybrid context (engineering OKR + their own team running 4DX) and asks the plugin for help:

1. **Surface the four friction points proactively** — agent should not pretend the horizontal hybrid is simple to run. Ch 8 onboarding skill should flag this as an extra layer of coordination work.
2. **Recommend Pattern A (sub-OKR / WIG-dependency contract)** as the highest-discipline coordination pattern — explicitly named at quarterly boundary, dependencies negotiated not assumed, sub-OKR carries winnable-game framing.
3. **Treat the engineering rep at WIG Session as a 2-min slot, not a debate partner** — protects the 30-min ceiling.
4. **Joint scoreboard recommended when** sales and engineering share an outcome metric (enterprise deals, feature-driven adoption, etc.).
5. **Cultural-bonus mismatch is a Ch 8 onboarding risk** that the plugin should flag at WIG-formulation time if compensation is tied to achievement %.

### Honest caveat

This entire Part 7 is **synthesized from the four practitioner sources documented in Parts 1-4 + first-principles reasoning about cycle / culture / metric / cadence mismatches**, not from a verified named real-company case of horizontal hybrid. The patterns above are the *expected* coordination friction and the *recommended* coordination patterns based on what we know about the two frameworks individually. If a specific named company publicly documents this horizontal hybrid in the future, this section should be revised against actual implementation evidence.

---

## Provenance

This research note was assembled 2026-05-01 in response to user request for deeper investigation of (1) why 4DX is industry-considered poorly-suited to SaaS / software-tech with specific focus on Company A and Company B, and (2) substantive OKR vs 4DX comparison.

Total research: 6 web searches + 4 direct primary-source reads (2 via WebFetch, 2 via playwright after redirects / SSL issues) + cross-validation against existing case-inventory.md Tier 1 + Tier 2 entries.

Re-running annually is sensible if the SaaS / tech 4DX adoption landscape changes (e.g. if FranklinCovey publishes a new SaaS-specific case study, or if Company A / Company B publicly change their goal-setting framework).

**Update 2026-05-01 (same day, second pass)**: added Part 7 on horizontal-hybrid coordination pattern (engineering OKR + sales 4DX). Five additional searches + 4 verified WebFetch reads (Workpath / Simplamo / FranklinCovey blog / mooncamp 4DX-vs-OKR). Honest finding: no verified named real-company case for this specific horizontal pattern; FranklinCovey's documented hybrid is vertical (same goal at OKR + 4DX layers), not horizontal (different goals across departments). Part 7 synthesizes expected friction points + recommended coordination patterns from first principles + practitioner-blog convergence. Section explicitly labeled as synthesis, not as verified case-anchored guidance.
