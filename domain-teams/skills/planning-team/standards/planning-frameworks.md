---
title: Planning Frameworks
tier: 1
---

# Planning Frameworks

Anchor for the core product-planning frameworks planning-team invokes
when defining a new product: Jobs-to-be-Done (JTBD) for user need,
Business Model Canvas (BMC) and Lean Canvas for business model,
the Value Proposition Canvas (VPC) for demand-supply fit, the 4
Big Risks (Value / Usability / Feasibility / Business Viability)
for assumption discovery, and 3C 分析 for market positioning.
Tier 1: these frameworks are canonical enough that LLMs recover
them well — the body stays compact, anchors the primary sources,
and spells out the attribution corrections that prior planning-team
versions got wrong.

## JP Genealogy Preamble

planning-team's main grounding is Western canonical (Christensen,
Ries, Osterwalder, Cagan, Doerr) because product planning as a
formalized discipline emerged primarily from US business schools,
Silicon Valley practice, and European business-model research.
Japanese planning tradition contributes at the **genealogy** level:

- **ジェームス・W・ヤング (1988 日譯)**『アイデアのつくり方』TBSブリタニカ — JP 企画 classic heuristic on idea generation (材料収集 → 咀嚼 → 熟成 → ひらめき → 具象化).
- **大野耐一 (1978)**『トヨタ生産方式』ダイヤモンド社 — TPS, the lineage Eric Ries's Lean Startup explicitly inherits from.
- **三枝匡 (1994)**『戦略プロフェッショナル』日経BP — canonical JP 経営企画 case-based teaching.
- **大前研一 (1975)**『企業参謀』プレジデント社 — 3C 分析 origin (see §3C below for full treatment).

These anchor the cultural inheritance. The load-bearing methodology
grounding is Western primary; JP appears as preamble notes, except
for 3C which is JP-origin and receives full JP treatment.

## Primary Sources

- **Clayton M. Christensen & Michael E. Raynor (2003)** *The Innovator's Solution* Ch.3. Harvard Business School Press. The canonical JTBD launch — introduces "customers hire products to do jobs" and the milkshake case.
- **Christensen, Taddy Hall, Karen Dillon, David S. Duncan (2016)** "Know Your Customers' 'Jobs to Be Done'". *Harvard Business Review* Sep–Oct 2016. https://hbr.org/2016/09/know-your-customers-jobs-to-be-done. The short, citable operational re-statement of JTBD.
- **Paul Adams (2016)** "How we accidentally invented Job Stories". *The Intercom Blog*, 2016-06-28. https://www.intercom.com/blog/accidentally-invented-job-stories/. **The actual origin of the "When [situation], I want to [motivation], so I can [outcome]" template** — Adams was Intercom CPO; Alan Klement later named it "Job Stories". NOT a Christensen format.
- **Alexander Osterwalder & Yves Pigneur (2010)** *Business Model Generation*. Wiley. Canonical source for the 9-block Business Model Canvas.
- **Ash Maurya (2022)** *Running Lean*, 3rd ed. O'Reilly Media. Ch.1 is the authoritative mapping from BMC to Lean Canvas — the 4 block substitutions that re-target BMC for early-stage startups.
- **Marty Cagan (2017)** *INSPIRED: How to Create Tech Products Customers Love*, 2nd ed. Wiley. Part III "The Right Product" defines the **Four Big Risks** (Value / Usability / Feasibility / Business Viability). https://www.svpg.com/four-big-risks/ is the open-access version.
- **David J. Bland & Alexander Osterwalder (2020)** *Testing Business Ideas*. Wiley. The canonical source for Assumption Mapping and the **3-axis DVF** framework (Desirability / Viability / Feasibility) plus 44 experiment patterns.
- **Alexander Osterwalder, Yves Pigneur, Gregory Bernarda, Alan Smith (2014)** *Value Proposition Design*. Wiley. Canonical Value Proposition Canvas — Customer Jobs / Pains / Gains on one side, Products & Services / Pain Relievers / Gain Creators on the other.
- **大前研一 (1975)**『企業参謀—戦略的思考とはなにか』プレジデント社. 3C 分析 (戦略的三角形) origin. Canonical JP text.
- **Kenichi Ohmae (1982)** *The Mind of the Strategist: The Art of Japanese Business*. McGraw-Hill. The English expansion of 大前 1975 (~60% rewritten for Western audiences, not a direct translation).

## Critical Attribution Corrections

### Job Story template is Adams / Intercom, NOT Christensen

The sentence form "When [situation], I want to [motivation], so I can [outcome]"
is **not** Christensen's JTBD theory. It was invented by Paul Adams (then CPO
at Intercom) in the 2016-06-28 Intercom blog post "How we accidentally
invented Job Stories"; Alan Klement later coined the name "Job Stories" in
*When Coffee and Kale Compete* (2018). Christensen's 2003 book and 2016 HBR
article never use this sentence template. When planning-team uses the Job
Story template, cite Adams (2016) for the template; cite Christensen &
Raynor (2003) or the 2016 HBR article for the underlying JTBD theory.
**Do NOT attribute the template to Christensen.**

### The 4-axis DVF+Usability is Cagan, NOT Bland & Osterwalder

Prior planning-team standards listed four assumption categories:
**Desirability / Feasibility / Viability / Usability**. This 4-axis version is
*not* from Bland & Osterwalder (2020) *Testing Business Ideas* — Bland uses
only **3 axes** (DVF). The 4-axis version with Usability as a distinct fourth
category is **Marty Cagan's "Four Big Risks"** from *Inspired* 2nd ed (2017)
Part III. The substantive reframing is also Cagan's: he splits "Valuable"
into **customer Value** and **Business Viability**, and promotes Usability
from a sub-concern to its own axis. Planning-team uses the Cagan 4 Big Risks
as the canonical axes because Usability is a load-bearing product risk category
for software products. Cite Cagan (2017) *Inspired* 2nd ed Part III; do not
cite Bland & Osterwalder for the 4-axis version — they only cover 3.

### 3C 分析 origin is 大前 1975 Japanese original, NOT the 1982 English expansion

3C is often cited to "Kenichi Ohmae" or vaguely to "Japanese strategy school"
without a publication anchor. The correct attribution: the framework appeared
in 大前研一 (1975)『企業参謀』プレジデント社 — the Japanese original. Ohmae
(1982) *The Mind of the Strategist* McGraw-Hill is an English expansion,
not a direct translation; Ohmae rewrote ~60% of the content for Western
audiences and substituted many Japanese cases with global-recognized ones
(Honda, Toyota, Sony). Cite 大前 (1975) as the primary origin and Ohmae
(1982) as the English access point, in that priority order.

### Levitt's "quarter-inch drill" quote is not in the 1960 HBR original

The widely-quoted "People don't want a quarter-inch drill. They want a
quarter-inch hole" is attributed to Theodore Levitt (1960) "Marketing
Myopia" but is actually a **course aphorism** recorded by Philip Kotler
after Levitt's death, not a direct quote from the 1960 HBR article.
The load-bearing claim of Levitt (1960) is "railroads should have
defined themselves as being in the transportation business, not the
railroad business" — i.e. customer job over product category. When
anchoring JTBD's intellectual backdrop, cite Christensen (2003) Ch.3
directly rather than paraphrasing the drill aphorism.

## Jobs-to-be-Done (JTBD)

JTBD asks: **what job is the customer hiring this product to do?** Not
"what features does the customer want" but "what progress is the
customer trying to make in their life, and what are they currently
compensating for?"

Christensen's canonical framing: `Customers hire products to do jobs.`
When a new, better product arrives that does the job more effectively,
customers "fire" the old product and "hire" the new one.

### Job Story template (Adams 2016, Intercom)

```
When [situation],
I want to [motivation],
so I can [outcome].
```

Example:
- When I finish a meeting with multilingual participants, I want to get
  an accurate transcript with speaker labels, so I can review key
  moments without re-watching the recording.

The Job Story captures **context + motivation + outcome** without
smuggling in a solution. The common mistake is to write: "As a user,
I want a transcript tool, so I can save time." That names a product
(transcript tool), not a job. Reword to: "When... I want to get a
transcript... so I can review key moments..." — same substance, but
the customer's job is now legible.

### Distinguishing JTBD from user stories

| Format | Grammatical structure | Hides what |
|---|---|---|
| User story | "As a **[role]**, I want **[feature]**, so that **[benefit]**" | Context + emotional motivation |
| Job Story | "When **[situation]**, I want to **[motivation]**, so I can **[outcome]**" | Nothing — context is explicit |

User stories over-specify the role and the feature; Job Stories leave
both open and name the situation. Planning-team prefers Job Stories
for spec writing; feature lists come later in implementation planning.

## The 4 Big Risks (Cagan 2017, *Inspired* 2nd ed Part III)

Every product idea must pass four independent risk checks. Each risk
corresponds to a responsible team role in a product org; planning-team
uses this framework to stress-test a product direction before committing
to a spec.

| Risk | Question | Typical owner | Fail mode |
|---|---|---|---|
| **Value** | Will customers actually want this? Will they buy / use it? | Product Manager | Built a thing nobody hires |
| **Usability** | Can users figure out how to use it? | Product Designer | Built a thing people want but cannot operate |
| **Feasibility** | Can engineering actually build it with the tech / time / skills at hand? | Engineering Lead | Built a plan nobody can deliver |
| **Business Viability** | Does it work for the business? (legal, sales, marketing, finance, privacy, compliance, partners) | PM + cross-functional | Built a thing that ships but cannot be monetized or sustained |

Every assumption in a product spec must be mappable to at least one
of the 4 Big Risks. Assumptions that fall outside all four are either
(a) not load-bearing, or (b) disguised as something else and should
be reframed.

### Assumption Mapping (Bland & Osterwalder 2020)

Once risks are enumerated, list the assumptions underneath each risk
and plot them on an **Impact × Evidence** 2×2:

```
              weak evidence            strong evidence
  high impact  ┌─────────────────┐ ┌─────────────────┐
               │  VALIDATE FIRST │ │    use as-is    │
               │  (top-right in  │ │                 │
               │   the original  │ │                 │
               │    Bland grid)  │ │                 │
  low impact   ├─────────────────┤ ├─────────────────┤
               │   note + defer  │ │   ignore        │
               │                 │ │                 │
               └─────────────────┘ └─────────────────┘
```

Assumptions in the **high-impact × weak-evidence** quadrant are the
ones to validate before investing in delivery. Mark the top 3 as
`[ASSUMPTION]` in PRODUCT-SPEC.md with a named validation approach
(experiment, interview, desk research, prototype test — Bland's book
lists 44 concrete experiment patterns).

## Business Model Canvas — Compact Reference

research-team's `strategic-frameworks.md` holds the full 9-block BMC
treatment (for market-analysis use cases). Planning-team uses a
**compact** reference: the 9 blocks exist, the right half answers
"who is the customer and what do we deliver", the left half answers
"what do we need to deliver it", and the center **Value Proposition**
block is the bridge. When planning-team needs a full BMC for a new
product, reference Osterwalder & Pigneur (2010) directly.

## Lean Canvas — 4 BMC Substitutions (Maurya 2022)

Lean Canvas is a derivative of BMC, licensed under BMC's CC BY-SA,
re-targeted by Maurya for early-stage startups where the original
BMC blocks are premature. Five BMC blocks survive unchanged;
**four are substituted**:

| BMC block (removed) | Lean Canvas block (added) | Why |
|---|---|---|
| Key Partners | **Unfair Advantage** | Early startups have no leverage partners; the question is "what moat?" |
| Key Activities | **Key Metrics** | Activities are internal; metrics are the progress signal |
| Key Resources | **Solution** | Resources are under-defined at Day 1; solution is the load-bearing unknown |
| Customer Relationships | **Problem** | Relationships assume product-market fit; the real early question is "what problem are we even solving?" |

Five unchanged blocks: **Customer Segments**, **Unique Value Proposition**
(Maurya adds "Unique" vs BMC's plain "Value Propositions"), **Channels**,
**Revenue Streams**, **Cost Structure**.

Use Lean Canvas when the product is pre-PMF and the question is
"should we build this at all?" Use BMC when the business model is
established and the question is "how does this make money?"

## Value Proposition Canvas — the Bridge to Customer Jobs

VPC (Osterwalder, Pigneur, Bernarda, Smith 2014) is a zoom-in on the
BMC's **Value Proposition** block. Two halves:

**Customer Profile** (right side):
- **Customer Jobs** — the JTBD the customer is trying to complete
- **Pains** — what frustrates, costs, or risks them in current solutions
- **Gains** — what outcomes they hope for (desired, expected, wished)

**Value Map** (left side):
- **Products & Services** — your offering
- **Pain Relievers** — how your offering removes pains
- **Gain Creators** — how your offering produces gains

**Fit** is achieved when Pain Relievers match explicit Pains, Gain
Creators match explicit Gains, and Products & Services support the
Customer Jobs. Planning-team uses VPC as the bridge from JTBD
(customer side) to product concept (value map side).

## 3C 分析（戦略的三角関係）

3C は JP origin の framework である。大前研一 (1975)『企業参謀』
プレジデント社 で戦略的三角形として提示された — Customer（顧客）、
Competitor（競合）、Company（自社）の三要素に分解して戦略ポジションを
決定する。Ohmae (1982) *The Mind of the Strategist* は英語版 expansion
であり、戦略的三角形を "strategic triangle" と呼び換えている。

| 要素 | 問い | planning-team 使用場面 |
|---|---|---|
| **Customer（顧客）** | 顧客は誰か？ 今何を使っているか？ 何が不足しているか？ | Phase 1 Vision — ターゲットユーザー定義 |
| **Competitor（競合）** | 既存の解決策は？ その強み・弱み・価格帯は？ | Phase 1 Vision — 市場文脈評価 |
| **Company（自社）** | 自分の優位性は？ リソースは？ 制約は？ | Phase 4 Direction Setting — 戦略ポジション確認 |

3C is the simplest positioning framework in planning-team's toolkit
and is the right starting point when a market context already exists
(i.e., competitors are known and the question is "where do we fit?").
For greenfield markets with no competitors, 3C is under-specified;
use JTBD + the 4 Big Risks instead. See `standards/discovery-frameworks.md`
for Lean Startup and Product Discovery when no competitor exists yet.

## When to Use Which Framework — Decision Rule

| Product planning question | Primary framework | Supporting |
|---|---|---|
| "What problem are we solving?" / "Why would anyone use this?" | **JTBD / Job Story** | Christensen 2003, Adams 2016 |
| "What are the riskiest assumptions that could kill this?" | **4 Big Risks + Assumption Mapping** | Cagan 2017, Bland 2020 |
| "Does the business model work?" (pre-PMF) | **Lean Canvas** | Maurya 2022 |
| "Does the business model work?" (post-PMF) | **Business Model Canvas** | Osterwalder 2010 |
| "How do we fit customer jobs to our offering?" | **Value Proposition Canvas** | Osterwalder et al. 2014 |
| "Where do we sit in a known market?" | **3C 分析** | 大前 1975 |

Picking the wrong framework is a bigger error than filling in the
right framework sloppily. Apply Porter Five Forces or Blue Ocean
Strategy only when the question is **market analysis**, not product
planning — those belong to `research-team/standards/strategic-frameworks.md`.

## Anti-Patterns

- Writing a Job Story as "As a user, I want X..." — that is a user
  story, not a Job Story. Reword to the "When... I want to... so I
  can..." template.
- Listing only the 4 Big Risks without mapping concrete assumptions
  under each — the risks framework is load-bearing only when tied to
  specific, testable assumptions.
- Using BMC on a pre-PMF product — Lean Canvas is designed for that
  case; BMC's Key Partners / Key Activities / Customer Relationships
  blocks force premature commitments.
- Citing "the DVF framework" without specifying which axis-count —
  3-axis (Bland) and 4-axis (Cagan) are different tools. Always name
  the author.
- Attributing the Job Story template to Christensen — it is Paul
  Adams / Intercom 2016. Christensen never used this sentence form.
- Citing 3C without the 大前 1975 publication anchor — "Kenichi
  Ohmae" alone is insufficient; the publication is『企業参謀』
  プレジデント社 1975.
