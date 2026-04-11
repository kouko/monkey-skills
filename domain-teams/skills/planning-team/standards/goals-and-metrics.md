---
title: Goals and Metrics
tier: 1
---

# Goals and Metrics

Anchor for how planning-team expresses goals, success criteria, and
progress metrics in a PRODUCT-SPEC.md: OKRs (Objectives & Key Results)
for aspirational goals, North Star Metric for the single load-bearing
value indicator, AARRR Pirate Metrics for the conversion funnel, and
the Goals / Non-Goals convention for scope boundary. Tier 1: these
frameworks are canonical enough that LLMs recover them well — the body
stays compact, anchors the primary sources, and spells out the
attribution corrections that prior planning-team versions missed
(planning-team v4.9.x had **no OKR coverage at all**).

## Primary Sources

- **Peter F. Drucker (1954)** *The Practice of Management* Ch.11. Harper & Brothers. Canonical source for Management by Objectives (MBO), the intellectual ancestor of OKR.
- **Andrew S. Grove (1983)** *High Output Management*. Random House (2015 reprint Vintage Books). **The OKR origin** — Grove formalized "What do I want to accomplish? (Objective)" plus "How will I know I'm getting there? (Key Results)" at Intel in the 1970s as iMBO (Intel Management by Objectives). This is the load-bearing primary for OKR's origin.
- **John Doerr (2018)** *Measure What Matters: How Google, Bono, and the Gates Foundation Rock the World with OKRs*. Portfolio / Penguin. **The modern canonical OKR text** — introduces the formula "I will [Objective] as measured by [Key Results]", the 0.0–1.0 grading scale, the 0.7-is-success rule for aspirational OKRs, and the 3-5-KRs-per-O convention. Doerr was a 1975 Grove trainee at Intel who brought OKRs to Google in 1999. https://www.whatmatters.com is Doerr's open-access educational site.
- **Dave McClure (2007)** "Startup Metrics for Pirates: AARRR!". 500 Hats blog / SlideShare (Seattle Ignite 2007). https://500hats.typepad.com/500blogs/2007/09/startup-metrics.html. Canonical AARRR (Acquisition / Activation / Retention / Referral / Revenue) origin. Grey-literature primary; no book-form canonical.
- **Sean Ellis & Morgan Brown (2017)** *Hacking Growth: How Today's Fastest-Growing Companies Drive Breakout Success*. Crown Business. Part I "The Method" introduces the **North Star Metric** and its role in aligning a growth team. Ellis coined both "growth hacking" and "North Star Metric". https://www.growthhackers.com is Ellis's open-access site.
- **Malte Ubl (2020, last modified 2022)** "Design Docs at Google". https://www.industrialempathy.com/posts/design-docs-at-google/. The best public source for the **Goals / Non-Goals** convention. Personal blog of a Google Principal Engineer (later Vercel CTO); not an official Google document, but the de-facto canonical description of the convention.

## Critical Attribution Corrections

### OKR origin is Grove / Intel 1970s, NOT Doerr / Google

OKRs are frequently miscredited to John Doerr or to Google. The
correct lineage:

1. Drucker (1954) Management by Objectives — the intellectual backdrop
2. Grove formalizes iMBO at Intel in the early 1970s with Key Results
3. Grove (1983) *High Output Management* — book-form canonical with
   examples from Intel's internal practice
4. John Doerr joins Intel in 1975 and is trained by Grove personally
5. Doerr introduces OKRs to Google in 1999 as a board member / investor
6. Doerr (2018) *Measure What Matters* popularizes OKRs to the broader
   tech industry

**Cite Grove (1983) as the origin and Doerr (2018) as the modern
operational canonical.** Do not cite Doerr as the inventor. Do not
cite Google as the inventor — Google is a 1999 downstream adopter.

### North Star Metric is Sean Ellis, NOT Facebook or Airbnb

Facebook's DAU and Airbnb's nights-booked are frequently-cited
**examples** of North Star Metrics, not the **origin**. Sean Ellis
coined the term "North Star Metric" and popularized it via his 2017
book *Hacking Growth* (co-authored with Morgan Brown) and his earlier
Growth Hackers blog posts. When planning-team cites NSM, the primary
is Ellis & Brown (2017); Facebook/Airbnb can appear as canonical
examples but not as origin.

### "Goals / Non-Goals" is a community convention, NOT an official Google document

The "Goals / Non-Goals" document structure is common in engineering
spec writing, particularly in the Google-influenced community. There
is **no official Google publication** defining it. The best public
source is Malte Ubl (2020) "Design Docs at Google" on his personal
blog industrialempathy.com. When planning-team uses Goals / Non-Goals,
cite Ubl (2020) as the community-established convention; do not
claim Google official authorship.

### AARRR is grey-literature primary

Dave McClure's 2007 "Startup Metrics for Pirates" was a talk at
Seattle Ignite 2007, published as a SlideShare deck and a 500 Hats
blog post. There is **no book-form canonical upgrade** of AARRR. When
planning-team cites AARRR, cite the SlideShare / blog as the
canonical primary, and disclose it as grey-literature (analogous to
how research-team cites Sherman Kent 1964 "Words of Estimative
Probability" as grey-literature for IPCC's probability ladder).

### AARRR has 5 stages, NOT 6

Growth-hacking community (Reforge, Growth Hackers) sometimes extends
AARRR to 6 stages by prepending "Awareness" (AAARRR) or appending
other stages. McClure's **original 2007 canonical** has exactly
5 stages: Acquisition / Activation / Retention / Referral / Revenue.
Planning-team uses the 5-stage original unless the user specifies
otherwise.

## OKRs — Objectives and Key Results (Grove 1983 / Doerr 2018)

An OKR pair is:

```
Objective:
  {qualitative, inspirational, time-bounded}

Key Results:
  1. {quantitative, measurable, date-bounded}
  2. {quantitative, measurable, date-bounded}
  3. {quantitative, measurable, date-bounded}
  (3 to 5 Key Results per Objective — Doerr 2018)
```

Doerr's canonical formula:

> I will **[Objective]** as measured by **[Key Results]**.

Example:
- I will **launch a usable transcript tool that meeting participants
  trust** as measured by:
  1. 100 weekly active users by end of Q2
  2. ≥ 85% user satisfaction survey score by end of Q2
  3. ≤ 10% transcript error rate by end of Q2

### OKR grading (Doerr 2018)

OKRs are graded at the end of the period on a 0.0 – 1.0 scale:

| Score | Color | Meaning |
|---|---|---|
| 0.0 – 0.3 | 🔴 red | Failed to make meaningful progress |
| 0.4 – 0.6 | 🟡 yellow | Progress but missed target |
| 0.7 – 1.0 | 🟢 green | Target met (0.7 is the success floor) |

For **aspirational / stretch OKRs**, the target grade is **0.7**, not
1.0 — hitting 1.0 on every OKR means the goals were too conservative.
For **committed OKRs** (must-deliver items), the target is 1.0 and
anything less requires a post-mortem.

### OKRs vs KPIs

| | OKRs | KPIs |
|---|---|---|
| Purpose | Drive change | Monitor health |
| Lifecycle | Quarterly (usually) | Continuous |
| Nature | Aspirational | Operational |
| Required outcome | 0.7 (aspirational) / 1.0 (committed) | "within normal range" |

An OKR is a measure of change; a KPI is a measure of health. Both
can exist together; planning-team uses OKRs for goal-setting in
PRODUCT-SPEC.md's Goals section and defers KPIs to operational
documents (not a planning-team deliverable).

## North Star Metric (Ellis & Brown 2017)

The **North Star Metric** (NSM) is the **single metric that best
captures the core value your product delivers to customers and
predicts long-term growth**. Ellis's definition:

> The North Star Metric is the single metric that best captures the
> core value that your product delivers to customers and is the key
> to driving sustainable growth across your full customer base.

### Canonical examples

| Company | North Star Metric |
|---|---|
| Facebook | Monthly Active Users (MAU) → Daily Active Users (DAU) |
| Airbnb | Nights booked |
| Spotify | Total listening time |
| WhatsApp | Messages sent |
| Amazon | Purchases per Prime member |

**These are examples, not definitions.** A planning-team spec must
derive its own NSM from the product's JTBD, not copy an example.

### NSM selection criteria (Ellis 2017)

An NSM candidate must:
1. **Reflect core value** — increases in the metric correspond to
   customers getting more value from the product
2. **Predict future growth** — a leading indicator, not a lagging one
3. **Be measurable** — the team can actually track it in operations
4. **Reflect customer activity, not just revenue** — revenue alone
   can be gamed by price changes without customer value delivery

**Not** every product needs an NSM in its first spec. Early-stage
products often have a **lifecycle NSM sequence**: a pre-PMF NSM
(e.g., activation rate), a PMF NSM (e.g., retention), and a
post-PMF NSM (e.g., revenue per customer). Planning-team names the
current-lifecycle NSM, not all three.

## AARRR Pirate Metrics (McClure 2007)

McClure's five-stage conversion funnel for tracking startup metrics:

```
┌─────────────────────────────────────────────┐
│  A  Acquisition  — users arrive (channel)    │
├─────────────────────────────────────────────┤
│  A  Activation   — first happy experience    │
├─────────────────────────────────────────────┤
│  R  Retention    — repeat usage              │
├─────────────────────────────────────────────┤
│  R  Referral     — users recommend others    │
├─────────────────────────────────────────────┤
│  R  Revenue      — monetization              │
└─────────────────────────────────────────────┘
```

Each stage has its own conversion rate and its own improvement
tactics. The funnel is ordered: a product with 0% retention cannot
improve by pushing acquisition; the load-bearing fix is retention.
Planning-team uses AARRR to structure the **Success Criteria** section
of a PRODUCT-SPEC.md when the product has a clear conversion funnel
(SaaS, consumer app, marketplace). For infrastructure or internal
tools, AARRR may be over-specified; use simpler adoption metrics.

## Goals / Non-Goals (Ubl 2020)

Ubl's canonical framing:

> **Non-goals** aren't negated goals... but rather things that could
> reasonably be goals, but are explicitly chosen not to be goals.

A good Non-Goals list names **plausible goals that were considered
and rejected**, not "things that are obviously not in scope". Example:

- ❌ "Non-goal: we will not build a UI" (obvious — CLI tool)
- ✅ "Non-goal: we will not support real-time transcription in the
  first version" (plausible — explicitly rejected for Phase 1)

The Non-Goal list **prevents scope creep** because it forces the
team to explicitly decide not to do things that others will later
propose. An empty or near-empty Non-Goals section is a red flag:
it means the team has not actually made the hard scope decisions.

### Planning-team rule

Every PRODUCT-SPEC.md Goals section MUST be paired with a Non-Goals
section of **at least equal specificity**. CHK-PROD-002 in
`checklists/product-spec-completeness.md` enforces this: an empty or
trivial Non-Goals section fails the gate.

## When to Use Which Framework — Decision Rule

| Goal / metric question | Primary framework |
|---|---|
| "What are our quarterly goals and how will we know we met them?" | **OKR** (Grove 1983 / Doerr 2018) |
| "What is the single metric that captures product success?" | **North Star Metric** (Ellis & Brown 2017) |
| "How do we track conversion through the customer lifecycle?" | **AARRR Pirate Metrics** (McClure 2007) |
| "What is in scope for this version, and what is explicitly out?" | **Goals / Non-Goals** (Ubl 2020) |

All four can coexist in a single PRODUCT-SPEC.md. OKRs in the
**Goals** section. NSM in the **Success Criteria** section. AARRR
funnel in the **Success Criteria** section when the product has a
clear funnel. Non-Goals in the **Scope** section.

## Anti-Patterns

- Writing a key result as a task ("Launch the feature") instead of a
  measurable outcome ("Reach 100 weekly active users by end of Q2").
  KRs are **results**, not activities.
- Setting all OKRs at 1.0 target — aspirational OKRs should target
  0.7 per Doerr. Consistent 1.0 scores mean the goals were sandbagged.
- Picking a revenue metric as NSM when the product has not reached
  PMF yet. Pre-PMF NSM should be activation or retention, not revenue.
- Claiming "Goals / Non-Goals is Google official" — cite Ubl (2020)
  as the community-established convention.
- Writing an empty or near-empty Non-Goals section. If you cannot
  name 3+ plausible rejected goals, you have not done the scope work.
- Citing Doerr as the OKR inventor — cite Grove (1983). Doerr (2018)
  is the modern canonical, not the origin.
- Extending AARRR to 6 stages without naming the source — the
  canonical AARRR is 5 stages (McClure 2007).
