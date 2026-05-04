# Lens: Persuasion Analysis (Cialdini + Brignull)

> **Sources**:
> - Robert Cialdini, *Influence: The Psychology of Persuasion*, New and Expanded edition (Harper Business, 2021). Original 6 principles introduced in 1984 first edition (Reciprocity / Commitment & Consistency / Social Proof / Authority / Liking / Scarcity); each principle gets its own chapter in the original numbering. **Unity is the seventh principle, added as Ch 8 of the 2021 expanded edition** (originally surfaced in *Pre-Suasion*, 2016). Cialdini frames Unity as distinct from Liking — about belonging and shared identity, not interpersonal preference.
> - Harry Brignull (with collaborators), *deceptive.design* (originally darkpatterns.org, registered 28 July 2010; renamed to deceptive.design and "deceptive patterns" framing 2023). Online taxonomy at [https://www.deceptive.design/](https://www.deceptive.design/) — note the taxonomy is continuously updated; the 12 patterns enumerated below are the canonical "second wave" set. Academic backing: Mathur et al., "Dark Patterns at Scale" (Proceedings of the ACM on Human-Computer Interaction, CSCW 2019).

> **Synthesis note**: This file combines Cialdini's 7 principles (1984/2021) and Brignull's 12 deceptive patterns (2010/2024). They were not co-published — Brignull cites Cialdini as upstream influence but did not co-author. Combining them is a methodological choice by `deconstruct-toolkit`: Cialdini catalogs *what* mechanisms persuade, Brignull catalogs *when* persuasion crosses into manipulation. Most dark patterns weaponize a Cialdini trigger — e.g., scarcity (#6) → fake countdowns (manipulation); commitment (#2) → roach motel (dark pattern). The combination lets us assign the **🟢/🟡/🔴/⚫ ethical-position verdict** that pure-Cialdini cannot produce. See [ADR-0003](../../../docs/adr/0003-lens-synthesis-disclosure.md).

Two sides of the same field: Cialdini's **7 principles of influence**
catalog *what* mechanisms persuade, and Brignull's **12 deceptive
patterns** catalog *when* persuasion crosses into manipulation.

## When to apply this lens

- Marketing copy, advertising, sales pages
- Landing pages, signup flows
- Onboarding (yes, onboarding is persuasion)
- Political / policy texts that mobilize action
- Subscription / upsell flows
- Any artifact designed to change behavior

## When NOT to apply

- Pure informational content with no persuasive intent
- Reference material (dictionaries, technical docs)
- Personal correspondence

---

## Part 1: Cialdini's 7 Principles

For each principle, check **if** and **how** the artifact triggers it,
and assign an **ethical position** (see Part 3).

### 1. Reciprocity

The instinct to repay favors. Triggered by:

- Free gifts, samples, trials
- Disproportionate "give first" framing
- Useful content provided before any ask
- Personalized attention or unsolicited help

Detection signals: "Free guide / template / chapter"; "Take this with you whether or not you buy"; surprise upgrades; gestures that exceed the cost of asking.

### 2. Commitment & Consistency

The instinct to align behavior with prior commitments. Triggered by:

- Small initial asks → larger asks (foot-in-the-door)
- Public / written commitments solicited
- Value-affirmation requests ("agree that X is important?")
- Identity claims ("you're the kind of person who…")

Detection signals: multi-step signups; "Do you agree?" early-form questions; pre-purchase value-statements; quizzes that lock you into a self-identified type.

### 3. Social Proof

The instinct to follow the crowd. Triggered by:

- "X thousand users" / "Y% adopted"
- Testimonials, case studies, logo walls
- Recent-activity feeds ("Sarah from Toronto just signed up")
- Top-ranked / best-selling indicators

Detection signals: any quantitative crowd-claim; trust badges; press mentions; star ratings; "join 10,000+ founders."

### 4. Authority

The instinct to defer to expertise. Triggered by:

- Titles, certifications, credentials
- Expert endorsements
- Authoritative tone / formal register
- Visual signals (suit, lab coat, professional photo)

Detection signals: PhD/MBA mentions; "as featured in"; legal / scientific framing; institutional logos; expert headshots.

### 5. Liking

The instinct to comply with people we like. Triggered by:

- Similarity claims ("just like you")
- Relatable narrator / founder story
- Compliments
- Cooperation / shared-goal framing

Detection signals: founder origin stories; "we get it because we lived it"; localized references; humor; informal voice.

### 6. Scarcity

The instinct to value what is rare. Triggered by:

- Limited-time offers
- Limited-quantity inventory
- Loss-framed messaging ("don't miss out")
- Countdown timers

Detection signals: "X left in stock"; "ends Friday"; "while supplies last"; ticking countdown; waitlist-only access.

### 7. Unity (added 2016)

The instinct to support our in-group. Triggered by:

- "We" framing
- Shared identity invocation
- Tribal markers (slang, references, aesthetic)
- "We vs them" framing

Detection signals: nationality / generation / profession / fandom appeals; "for women in tech"; "fellow operators"; insider jargon; identity-based filtering.

---

## Part 2: Brignull's 12 Dark Patterns

For each pattern, mark detection status:

| # | Pattern | What it does |
|---|---|---|
| 1 | **Confirmshaming** | Guilts user into a choice ("No thanks, I don't want to save money") |
| 2 | **Roach Motel** | Easy to enter, hard to leave (subscriptions, accounts, mailing lists) |
| 3 | **Privacy Zuckering** | Tricks user into sharing more data than intended |
| 4 | **Misdirection** | Visual emphasis steers user away from less-profitable choice |
| 5 | **Hidden Costs** | Final price differs from listed (shipping, fees, conversion) |
| 6 | **Forced Continuity** | Free trial silently rolls into paid charge |
| 7 | **Bait and Switch** | Click expecting X, get Y instead |
| 8 | **Trick Questions** | Confusing wording (double negatives, opposite-of-expected default) |
| 9 | **Sneak into Basket** | Pre-added items at checkout |
| 10 | **Disguised Ads** | Ad styled as content (native ads, fake reviews) |
| 11 | **Friend Spam** | Default to spamming user's contacts |
| 12 | **Price Comparison Prevention** | Different units / bundles frustrate comparison |

---

## Part 3: Ethical Position Verdict (mandatory)

After detecting Cialdini triggers and Brignull patterns, classify each
into one of four positions:

| Position | Definition | Example |
|---|---|---|
| 🟢 **Transparent persuasion** | Principle used + user can see and reject | "Join 10,000+ founders" with link to anonymized roster |
| 🟡 **Gray zone** | Principle used + user is unaware | Manufactured scarcity ("only 3 left!" when stock is unlimited) |
| 🔴 **Manipulation** | Creates urgency / false belief | Fake countdown timers, fabricated testimonials |
| ⚫ **Dark pattern** | Actively deceives, harms user | Forced continuity, hidden costs, confirmshaming |

**Rule**: Every detected mechanism gets one of these positions. Neutral
description of persuasion mechanisms is not allowed in the output.

---

## Worked example: Notion landing page

### Cialdini triggers

| Principle | Triggered? | How | Position |
|---|---|---|---|
| Reciprocity | ✓ | "Free for personal use" | 🟢 Transparent |
| Commitment | ✓ | "Plan your week" mini-quiz before signup | 🟡 Gray zone (unaware) |
| Social proof | ✓ | "Used by Pixar, Mitsubishi, Nike" + testimonial wall | 🟢 Transparent |
| Authority | ✓ | Implicit via brand logos | 🟢 Transparent |
| Liking | ✓ | "Beautifully made for teams who get things done" | 🟢 Transparent |
| Scarcity | ✗ | Not used | — |
| Unity | ✓ | "For builders, for thinkers" | 🟢 Transparent |

### Dark pattern check

| Pattern | Detected? | Note |
|---|---|---|
| Confirmshaming | ✗ | Opt-outs are neutral |
| Roach motel | ⚠️ borderline | Account deletion is multi-step but findable |
| Hidden costs | ✗ | Pricing transparent |
| Forced continuity | ✗ | Free tier doesn't auto-roll |
| (other 8) | ✗ | Not detected |

### Verdict

**🟢 Mostly transparent persuasion** with one **🟡 gray-zone** on the
commitment-via-quiz pattern (user does not realize the quiz is
generating commitment, not just configuration). No dark patterns.

---

## Worked example: A subscription-trap streaming service

### Cialdini triggers

| Principle | Triggered? | How | Position |
|---|---|---|---|
| Reciprocity | ✓ | "30-day free trial" | 🟡 Gray zone (free is bait) |
| Commitment | ✓ | Account creation before trial | 🟡 Gray zone |
| Scarcity | ✓ | Fake "ends Sunday" timer | 🔴 Manipulation |
| Authority | — | — | — |
| Social proof | ✓ | "Trusted by millions" | 🟢 Transparent |

### Dark patterns

| Pattern | Detected? | Note |
|---|---|---|
| Forced continuity | ✓ | Trial auto-converts to paid without re-confirmation | ⚫ |
| Roach motel | ✓ | Cancel requires phone call, M–F 9–5 | ⚫ |
| Hidden costs | ✓ | "Premium" tier required for ad-free | ⚫ |
| Confirmshaming | ✓ | Cancel page says "Are you sure you want to lose your progress?" | ⚫ |

### Verdict

**⚫ Multiple dark patterns** in subscription / cancellation flow. Even
the legitimate Cialdini triggers (social proof) are tainted by the
overall pattern of deception. Recommend escalation: this is not just
unethical, it is a regulatory risk under FTC / EU consumer protection.

## Pitfalls

- **Treating Cialdini as a checklist of evils**: legitimate persuasion
  uses these mechanisms transparently. Marking every triggered
  principle as suspicious is over-detection.
- **Ignoring intent**: dark patterns require *deception or coercion*.
  A legitimate countdown for a real flash sale is **🟢**, not **🔴**.
- **Missing the cumulative effect**: a single 🟡 gray-zone may be fine;
  five stacked 🟡s create the same harm as one ⚫.
- **Forgetting positive framing**: when persuasion is fully transparent,
  **say so** — design that respects user autonomy is rarer than it
  should be and deserves naming.

## Output format

```markdown
### Cialdini 7 principles
| Principle | Triggered? | How | Position |
|---|---|---|---|
| Reciprocity | ✓/✗ | <description> | 🟢/🟡/🔴/⚫ |
| Commitment | ... | ... | ... |
| Social proof | ... | ... | ... |
| Authority | ... | ... | ... |
| Liking | ... | ... | ... |
| Scarcity | ... | ... | ... |
| Unity | ... | ... | ... |

### Brignull 12 patterns
| Pattern | Detected? | Note |
|---|---|---|
| Confirmshaming | ... | ... |
| ... | ... | ... |

### Verdict
<one paragraph>
```

End with 1-line ethical position: "Overall: **🟢/🟡/🔴/⚫** — **N**
principles triggered transparently, **M** in gray zones, **K** dark
patterns detected."
