# Diátaxis Taxonomy (Shared Standard)

Authoritative documentation classification vocabulary for docs-team. Both worker
(when writing docs) and evaluator (when reviewing) reference this file. All terms
trace to Daniele Procida's Diátaxis framework.

Primary source: [diataxis.fr](https://diataxis.fr/) (Daniele Procida)

## Core Principle

Technical documentation has **four distinct kinds**, each serving a different
user need. **Mixing them in one document is the #1 documentation failure.**
Each quadrant has its own purpose, its own form, and must be kept separate.

## The Four Quadrants

| Mode | User Need | Orientation | Must Serve |
|------|-----------|-------------|------------|
| **Tutorial** | "Teach me" | Learning-oriented, practical | A new user in the hands of a teacher. Guided hands-on lesson with guaranteed success. |
| **How-to Guide** | "Show me how to do X" | Task-oriented, practical | A user who knows what they want to achieve and needs the steps. |
| **Reference** | "Tell me the facts" | Information-oriented, theoretical | A user who needs exact technical description of the machinery. |
| **Explanation** | "Help me understand" | Understanding-oriented, theoretical | A user who wants context, rationale, design decisions — the "why". |

## Two Axes (Procida's 2×2)

```
                    ACQUISITION (study)       APPLICATION (work)
                    ─────────────────         ─────────────────
    PRACTICAL       Tutorial                  How-to Guide
    (action)        Teaching the beginner     Helping the competent user

    THEORETICAL     Explanation               Reference
    (cognition)     Clarifying concepts       Describing the machinery
```

- **Acquisition vs Application**: Tutorials + Explanation serve acquiring knowledge;
  How-to + Reference serve applying existing knowledge.
- **Practical vs Theoretical**: Tutorials + How-to are about action and steps;
  Reference + Explanation are about cognition and understanding.

## Quadrant Identification Questions

When deciding which quadrant a document belongs to, ask in order:

1. **Is it study or work?**
   - Study (learning new things) → Tutorial or Explanation
   - Work (applying skills you already have) → How-to or Reference

2. **Is it action or cognition?**
   - Action (doing something with hands) → Tutorial or How-to
   - Cognition (understanding or looking up facts) → Reference or Explanation

3. **Who is the reader?**
   - A beginner who needs a safe first experience → **Tutorial**
   - A competent user with a specific problem → **How-to**
   - Someone who already knows what they want and needs facts → **Reference**
   - Someone who wants to understand design, trade-offs, history → **Explanation**

If the answer to "who is the reader" changes between paragraphs, the document
is mixing modes and must be split.

## Mode Characteristics

### Tutorial
- **Goal**: The reader finishes with a concrete achievement ("I made it work")
- **Voice**: Second person, imperative, encouraging
- **Structure**: Sequential, no branching
- **What to avoid**: Explaining why, offering alternatives, discussing theory
- **Success criterion**: A beginner can follow every step without getting stuck

### How-to Guide
- **Goal**: The reader solves a specific problem
- **Voice**: Second person, imperative, efficient
- **Structure**: Goal-statement-first, then steps, then result verification
- **What to avoid**: Teaching fundamentals, explaining concepts, exhaustive alternatives
- **Success criterion**: A competent reader can use it as a recipe

### Reference
- **Goal**: The reader can look up exact technical facts quickly
- **Voice**: Neutral, descriptive, austere
- **Structure**: Mirrors the structure of what is being described (API, CLI, config schema)
- **What to avoid**: Narrative, tutorials, opinions, history
- **Success criterion**: Exhaustive, accurate, scannable

### Explanation
- **Goal**: The reader understands the "why" behind design decisions
- **Voice**: Discursive, reflective, may use first person plural ("we chose")
- **Structure**: By topic or by trade-off, not by task
- **What to avoid**: Step-by-step instructions, exhaustive references, commands
- **Success criterion**: The reader can make informed decisions in novel situations

## Anti-Patterns (Common Diátaxis Failures)

1. **Tutorial that teaches concepts** — Tutorials should teach by doing, not by
   lecturing. Concepts belong in Explanation.
2. **How-to that explains why** — How-to is a recipe. Rationale belongs in
   Explanation; link to it, don't embed it.
3. **Reference with narrative** — Reference is austere and scannable. Stories,
   examples of use, and historical context belong elsewhere.
4. **Explanation with commands** — Explanation discusses; it does not instruct.
   Steps belong in Tutorial or How-to.
5. **"Getting Started" that mixes all four** — The classic README failure.
   Fix: structure README as labeled sections with each section in one mode.
6. **Dogmatic rigidity** — Treating the framework as four fixed buckets instead
   of an analytical lens. Small projects may need only one quadrant.
7. **Forced completeness** — Not every project needs all four modes. A library
   may only need Reference + a single Tutorial.

## Adoption Evidence (Widely Adopted Standard)

- **Framework docs**: Django, Gatsby, NumPy, django CMS, BeeWare, Snowpack,
  Sourcegraph, PostgREST, websockets, Wechaty, Gensim
- **Enterprise**: Cloudflare Workers, Canonical, IBM LoopBack/StrongLoop,
  Google Fuchsia OS, Ericsson, Bosch, Tesla Motors, Zalando, ING Bank

Source: [diataxis.qubitpi.org/en/latest/](https://diataxis.qubitpi.org/en/latest/)
(mirror listing adopters).

## Sources

- [diataxis.fr](https://diataxis.fr/) — Official Diátaxis framework site (Daniele Procida)
- [idratherbewriting — What is Diátaxis?](https://idratherbewriting.com/blog/what-is-diataxis-documentation-framework) — detailed walkthrough
- [diataxis mirror with adopter list](https://diataxis.qubitpi.org/en/latest/)
- [Recruit Data Blog — Diátaxis + C4](https://blog.recruit.co.jp/data/articles/diataxis-c4model/) — Japanese community adoption
