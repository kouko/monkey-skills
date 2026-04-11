---
title: Discovery Frameworks
tier: 1
---

# Discovery Frameworks

Anchor for the canonical product-discovery frameworks planning-team
invokes when the question is "what should we learn before we commit
to delivery": Eric Ries's Lean Startup (Build-Measure-Learn, MVP,
Validated Learning, Pivot), Steve Blank's Customer Development,
Marty Cagan's Product Discovery (discovery ≠ delivery, empowered
product teams), Teresa Torres's Continuous Discovery (Opportunity
Solution Tree), and Amazon's PR/FAQ Working Backwards method.
Tier 1: these frameworks are canonical enough that LLMs recover
them well — the body stays compact, anchors the primary sources,
and spells out the lineage corrections prior planning-team
versions got wrong.

## JP Genealogy Note

Eric Ries explicitly inherits "Lean" from **大野耐一 (1978)**
『トヨタ生産方式』ダイヤモンド社 (Ohno's Toyota Production System).
The English translation Ohno (1988) *Toyota Production System: Beyond
Large-Scale Production*, Productivity Press, is the bridge Ries cites
in *The Lean Startup* (2011). When quoting Ries's Lean lineage, this
JP → US genealogy is load-bearing; when using Ries's methods in a
product context, the JP genealogy is cultural context only.

## Primary Sources

- **Steve Blank (2005, re-released 2013)** *The Four Steps to the Epiphany: Successful Strategies for Products that Win*. K&S Ranch. The canonical Customer Development framework (Customer Discovery → Customer Validation → Customer Creation → Company Building). The prerequisite methodology Ries builds on.
- **Steve Blank (2013)** "Why the Lean Start-Up Changes Everything". *Harvard Business Review* May 2013. https://hbr.org/2013/05/why-the-lean-start-up-changes-everything. The HBR-level short canonical.
- **Eric Ries (2011)** *The Lean Startup*. Crown Business. Part One ("Vision") defines Validated Learning; Part Two ("Steer") defines Build-Measure-Learn, MVP, and Pivot-or-Persevere; Part Three ("Accelerate") covers batch size, growth engines, and innovation accounting.
- **Marty Cagan (2017)** *INSPIRED: How to Create Tech Products Customers Love*, 2nd ed. Wiley. Parts III–IV separate **Product Discovery** from **Product Delivery** and introduce **empowered product teams**. SVPG.com is Cagan's open-access site.
- **Marty Cagan & Chris Jones (2020)** *EMPOWERED: Ordinary People, Extraordinary Products*. Wiley. Product team structure canonical — how to build teams that can actually run discovery rather than being feature factories.
- **Teresa Torres (2021)** *Continuous Discovery Habits*. Product Talk LLC. Canonical source for **Opportunity Solution Tree (OST)** and the discipline of weekly customer touchpoints. https://www.producttalk.org is Torres's open-access blog.
- **Colin Bryar & Bill Carr (2021)** *Working Backwards: Insights, Stories, and Secrets from Inside Amazon*. St. Martin's Press. Ch.4 "Working Backwards: Start with the Desired Customer Experience" is the book-form canonical of the Amazon **PR/FAQ** method.

## Critical Attribution Corrections

### MVP is Ries 2011, NOT Steve Blank

The Minimum Viable Product concept is often misattributed to Steve
Blank. Blank is Ries's mentor and the author of Customer Development,
which is a **prerequisite** to Ries's Lean Startup; but MVP itself is
defined by Ries in his 2009 blog post "The Minimum Viable Product: a
guide" and formalized in Ries (2011) *The Lean Startup* Part Two. Cite
Ries (2011) for MVP and for Build-Measure-Learn; cite Blank (2005) only
when referring to Customer Development or the four steps to the
epiphany.

### Product Discovery predates Lean Startup

Marty Cagan was using "product discovery" on the SVPG blog by 2008,
three years before Ries (2011) *The Lean Startup*. The two traditions
developed in parallel and overlap — both reject feature-factory
delivery without validated learning — but Cagan's framing is *not* a
subset of Ries's. When planning-team cites discovery-vs-delivery, cite
Cagan (2017) *Inspired* 2nd ed Parts III–IV; when citing MVP / BML /
Validated Learning, cite Ries (2011). Do not roll one into the other.

### Working Backwards PR/FAQ is Bryar/Carr 2021, NOT the 1997 Bezos letter

Amazon's "Working Backwards" method is sometimes cited to Jeff Bezos's
1997 shareholder letter. The 1997 letter only mentions "customer
obsession"; the PR/FAQ method is a 2004–2005 internal convention at
Amazon. The first public description is Ian McAllister's 2012 Quora
answer. The canonical book-form source is **Bryar & Carr (2021)
*Working Backwards* Chapter 4**. Cite Bryar/Carr (2021) as primary;
McAllister (2012) Quora can be noted as the pre-book genealogy.

## The Lean Startup — Core Concepts (Ries 2011)

Ries's framework names four concepts; **all four** must be cited to
Ries specifically.

### Validated Learning (Ries 2011 Part One)

> Validated learning is the process of demonstrating empirically that
> a team has discovered valuable truths about a startup's present and
> future business prospects. It is more concrete, more accurate, and
> faster than market forecasting or classical business planning.

Validated learning is the **unit of progress** in Lean Startup,
replacing "features shipped" or "milestones hit". Every experiment
should produce validated learning — a claim about the customer or
business that was previously an assumption and is now evidence-backed.

### Build-Measure-Learn loop (Ries 2011 Part Two)

```
     ┌──────────┐
     │   IDEAS  │
     │          │
     └────┬─────┘
          │
          ▼  (build)
     ┌──────────┐
     │   CODE   │
     │          │
     └────┬─────┘
          │
          ▼  (measure)
     ┌──────────┐
     │   DATA   │
     │          │
     └────┬─────┘
          │
          ▼  (learn)
    back to IDEAS
```

The loop's goal is to **minimize total time through the loop**, not
to minimize any single phase. Batch size matters; small batches loop
faster.

### Minimum Viable Product (Ries 2011 Part Two)

> The minimum viable product is that version of a new product which
> allows a team to collect the maximum amount of validated learning
> about customers with the least effort.

MVP is **not** "the smallest shippable feature set". MVP is "the
smallest product that lets you start the Build-Measure-Learn loop
and get validated learning". A throwaway landing page can be an MVP
if it validates demand; a half-built feature is usually not.

### Pivot or Persevere (Ries 2011 Part Two)

After each BML loop, the team decides: are we making progress? If
yes, **persevere** — keep learning. If no, **pivot** — change one
fundamental hypothesis while keeping what has been learned. Ries
lists 10 pivot types (zoom-in, zoom-out, customer segment, customer
need, platform, business architecture, value capture, engine of
growth, channel, technology). A pivot is a **structured change**,
not "trying something else".

## Customer Development (Blank 2005)

Blank's four steps run in parallel to product development but as a
distinct track:

| Step | Question | Output |
|---|---|---|
| **Customer Discovery** | Are there customers for our vision? Who are they? | Customer archetype + problem validation |
| **Customer Validation** | Is the business model repeatable and scalable? | Validated sales roadmap |
| **Customer Creation** | How do we create end-user demand? | Positioning + launch strategy |
| **Company Building** | When do we transition from learning to executing? | Scaled organization |

The two tracks matter: product development can run as planned only
after Customer Discovery and Customer Validation have confirmed the
vision. Skipping directly from idea to company-building is the classic
"execution failure" pattern Blank and Ries both warn against.

## Product Discovery vs Product Delivery (Cagan 2017)

Cagan's central distinction:

- **Delivery** is about shipping reliable, quality code. Answered by
  engineering practices (CI, testing, monitoring).
- **Discovery** is about making sure you are building the right thing.
  Answered by user research, prototypes, experiments.

A team that only delivers is a **feature factory**: it ships what it
is told, regardless of whether the output creates value. A team that
only discovers is a **research lab**: it never ships. Cagan's
empowered product teams run both tracks concurrently.

### The 4 Big Risks (cross-reference)

The 4 Big Risks framework (Value / Usability / Feasibility / Business
Viability) is defined in Cagan (2017) *Inspired* 2nd ed Part III and
is covered in full in `standards/planning-frameworks.md` §The 4 Big
Risks. Discovery work's purpose is to **retire** the 4 Big Risks
before delivery commits; the 4 Big Risks are the lens through which
discovery experiments are chosen.

## Continuous Discovery — Opportunity Solution Tree (Torres 2021)

Torres's OST decomposes product work into four layers:

```
         ┌─────────────────────────┐
         │    Desired Outcome      │
         │  (the business outcome  │
         │    the team is driving) │
         └───────────┬─────────────┘
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
     ┌─────────┐┌─────────┐┌─────────┐
     │  Opp 1  ││  Opp 2  ││  Opp 3  │  ← opportunities (customer needs)
     └────┬────┘└────┬────┘└────┬────┘
          │          │          │
       ┌──┴──┐    ┌──┴──┐    ┌──┴──┐
       ▼     ▼    ▼     ▼    ▼     ▼
     [sol] [sol][sol] [sol][sol] [sol]  ← solutions
        │     │   │     │   │     │
        ▼     ▼   ▼     ▼   ▼     ▼
      [exp] [exp][exp] [exp][exp] [exp] ← experiments / assumption tests
```

The tree forces teams to (a) connect every solution to a concrete
customer opportunity, (b) connect every opportunity to the desired
business outcome, and (c) test assumptions before investing in a
solution. Torres's discipline is **weekly customer touchpoints**: a
product team that does not talk to customers every week is not
practicing continuous discovery.

## Amazon PR/FAQ Working Backwards (Bryar & Carr 2021 Ch.4)

Before building a product, write the press release and FAQ as if
the product were launching **today**. The exercise forces the team
to clarify the customer benefit in plain language *before* writing
any code or spec.

### Press Release structure (max ~1 page)

1. **Heading** — the product name in a line a customer would read
2. **Sub-heading** — description of the target customer and benefit
3. **Summary paragraph** — what and why, in plain language
4. **Problem paragraph** — the problem the product solves
5. **Solution paragraph** — how the product solves it
6. **Quote from company** — a leader's endorsement with the vision
7. **How-to-get-started paragraph** — what a new customer does on day 1
8. **Customer quote** — a quoted beneficiary (real or archetypal)
9. **Closing call-to-action** — where to go next

### FAQ structure (max ~5 pages)

Two FAQ sets:
- **Internal FAQ** — engineering, economics, legal, operational
  questions the team needs to answer before committing
- **Customer FAQ** — the questions a customer would ask after
  reading the PR

The PR/FAQ is an **artifact of discovery**, not delivery. If the PR
is not compelling, the product concept is not compelling — iterate
the PR before iterating the spec.

## When to Use Which Framework — Decision Rule

| Product discovery question | Primary framework | Supporting |
|---|---|---|
| "Is our vision valid? Who are the customers?" | **Customer Development** | Blank 2005 |
| "What is the smallest experiment that gives us validated learning?" | **Lean Startup MVP + BML** | Ries 2011 |
| "Are we building the right thing vs building the thing right?" | **Product Discovery vs Delivery** | Cagan 2017 |
| "How do we tie every solution to a business outcome?" | **Opportunity Solution Tree** | Torres 2021 |
| "How do we force-pressure-test a concept before committing?" | **PR/FAQ Working Backwards** | Bryar & Carr 2021 Ch.4 |
| "Our hypothesis failed — now what?" | **Pivot (10 types)** | Ries 2011 Part Two |

## Anti-Patterns

- Treating MVP as "smallest feature set we can ship" rather than
  "smallest product that validates learning". The definition is
  Ries's, and it is about learning, not shipping.
- Running Build-Measure-Learn on a product with no clear leap-of-faith
  assumption. BML without a hypothesis to test is just ordinary
  iteration.
- Skipping Customer Discovery / Validation and going directly to
  feature delivery. Blank's entire thesis is that this is the
  dominant failure mode.
- Collapsing discovery and delivery into a single track. Cagan's
  point is that they are concurrent but distinct; a feature factory
  is delivery without discovery.
- Writing a PR/FAQ and then treating it as marketing copy to be
  published. The PR/FAQ is a discovery artifact — it is designed
  to be rewritten, not shipped as-is.
- Citing Ries for Customer Development — that is Blank. Citing
  Blank for MVP — that is Ries. The two are a linked but distinct
  pair.
