# Write Explanation Protocol (Diátaxis: Explanation Quadrant)

Write an **understanding-oriented** document. Discursive, reflective, answers
the "why". The reader wants to understand the thinking behind a design, the
trade-offs considered, and the alternatives rejected.

**Vocabulary reference**: `standards/diataxis-taxonomy.md` §Explanation
**Style reference**: `standards/style-conventions.md`

## Explanation vs Other Modes

| This mode | NOT this mode |
|-----------|---------------|
| Discusses "why" | Teaches "how" (→ Tutorial) |
| Reflective | Recipe for a task (→ How-to) |
| Selective and opinionated | Exhaustive facts (→ Reference) |
| Historical / design context | Step-by-step instructions |

## Phase 0: Context Discovery

1. **Identify the topic** — a design decision, a concept, a trade-off. Explanation
   docs illuminate; they don't instruct.
2. **Identify the reader's question** — what is the reader trying to understand?
   ("Why do we use X instead of Y?" "How should I think about Z?")
3. **Gather sources** — if the explanation discusses history or trade-offs, what
   are the primary sources? ADRs, design docs, mailing list discussions, papers.
4. **Check for ADR opportunity** — if the topic is a specific architectural
   decision with a clear status, write an ADR instead (see `write-adr.md`).
   Explanation is for broader discussions that don't fit the ADR format.

## Phase 1: Open with the Question

The first line of an explanation states the question the reader is asking,
not a summary of the answer. Compare:

| Wrong (summary first) | Right (question first) |
|----------------------|--------------------------|
| "We use event sourcing for auditability." | "Why does this system use event sourcing instead of a traditional CRUD store?" |
| "The rate limiter uses a token bucket." | "How does the rate limiter handle traffic bursts?" |

The question-first opening invites the reader to lean in rather than feeling
lectured at.

## Phase 2: Discuss the Trade-offs

Explanation docs are honest about trade-offs. Every design decision has costs.
A good explanation:

1. States the decision
2. Lists the alternatives considered
3. Explains the trade-offs for each alternative
4. Articulates the criteria used to choose
5. Names the costs of the chosen path

Example:

```markdown
## Why token bucket instead of leaky bucket?

We chose a token bucket rate limiter over a leaky bucket because our traffic
has natural burstiness (login storms at business hours, flash sales on
marketing campaigns). Token bucket absorbs short bursts up to the bucket
capacity, while leaky bucket smooths them out — and smoothing would cause
user-visible latency spikes at exactly the times users care most.

The cost is that token bucket is less predictable: under sustained overload,
the effective rate depends on bucket state rather than being a strict ceiling.
We accept this because our overload protection is downstream of the rate
limiter.
```

## Phase 3: Provide Historical Context

If the decision has history — prior approaches, failed experiments, deprecated
patterns — include it. Historical context helps readers understand why the
current approach exists even if it seems strange today.

Do not dwell on history gratuitously. The reader is trying to understand
**today's** system; history is useful only when it explains a current quirk.

## Phase 4: Connect to Related Modes

Explanation naturally connects to other modes. At the end, link to:

- **Reference** for the exhaustive facts about the thing being discussed
- **How-to** for practical use of the thing
- **ADR** for the specific decision that this explanation elaborates

Do not embed reference material or step-by-step instructions in the
explanation itself. Link instead.

## Rules

- **First person plural allowed** ("we chose", "we considered") — explanations
  discuss design rationale, which is naturally "we" voice
- **Past tense allowed** for historical context — "we used to use X" is
  acceptable
- **No step-by-step instructions.** If readers should do something as a
  result of reading, link to a how-to guide
- **No exhaustive coverage.** Explanation is selective — pick the parts that
  illuminate, skip the rest
- **Honest about costs.** If the chosen design has downsides, name them
- **Link generously** to Reference, How-to, and ADR for the action-oriented
  content that explanation intentionally avoids

## Output Structure

```markdown
---
title: {Question being answered — "Why X?" or "How does Y work?"}
last_reviewed: {YYYY-MM-DD}
applies_to: {version or "design"}
owner: {team}
mode: explanation
---

# {Question being answered}

{1-2 sentence context setting}

## The question

{Restate the reader's question in their words}

## The short answer

{2-3 sentences summarizing the conclusion for readers who just want the gist}

## The trade-offs

{Discussion of alternatives considered, criteria, chosen path, costs}

## Historical context (optional)

{Prior approaches and why they changed — only if relevant to today's reader}

## Related

- Reference: {link to the authoritative facts}
- How-to: {link to practical use}
- ADR: {link to the specific decision, if any}
```

## Mode Clarity Check

This explanation passes the Diátaxis Mode Clarity gate if:

- The opening asks a question, not states a conclusion
- Trade-offs are discussed honestly (alternatives + costs + chosen path)
- No step-by-step instructions embedded
- No exhaustive reference material embedded (links instead)
- First person plural voice is acceptable
- Historical context is included only where it explains current state
