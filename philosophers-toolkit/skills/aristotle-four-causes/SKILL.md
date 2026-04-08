---
name: aristotle-four-causes
description: >-
  Aristotle's Four Causes — analyze any subject through material, formal,
  efficient, and final causes. Use when user wants to deeply understand
  what something is and why it exists, not when they want implementation.
  四因説・本質分析。四原因説・本質の分析。
---

# Aristotle's Four Causes

## Core Philosophy

Everything that exists or changes can be understood through four
questions: What is it made of? What makes it what it is? What brought
it about? What is it for? By examining all four, you reach a complete
understanding — not just description, but explanation.

Unlike Socratic questioning which guides through dialogue, this method
provides an analysis framework. The agent actively structures the
investigation through four lenses.

## When to Use

- User wants to understand the essence of a system, product, or concept
- User asks "what is this really?" or "why does this exist?"
- Breaking down a complex subject into fundamental components
- Understanding a design decision at its deepest level
- Analyzing why something works (or doesn't work)

Do NOT use when:
- User wants implementation or code (use code-team)
- User wants their thinking challenged (use socratic-method)
- User wants trade-off comparison (use Hegelian dialectics, future skill)

## Topic Discovery

**User Input:** User invokes skill (with or without a specific subject)
**Your Action:** Establish what subject to analyze.

- If user's input already contains a specific subject → proceed to Method
- If user's input is vague but conversation has prior context →
  acknowledge the subject: "I see we've been discussing [subject].
  Shall we analyze it through the four causes?"
- If no context at all → ask: "What would you like to analyze?"

**Constraint: Acknowledge topic, never pre-judge the analysis.**

## Method: Four-Dimensional Analysis

Analyze the subject through each cause in order. For each cause,
ask the user 1-2 questions, then summarize what they said through
the lens of the current cause. Do not add analysis the user did not
provide — connect their words to the framework, don't generate new
content. Build on previous causes as you progress.

### Cause 1: Material Cause (What is it made of?)

What are the raw materials, components, or inputs?

Questions to ask:
- "What is [subject] made of? What are its constituent parts?"
- "What resources or inputs does it require to exist?"

Examples by domain:
- Software: languages, frameworks, libraries, data structures
- Product: physical materials, technologies, APIs, data sources
- Organization: people, skills, capital, infrastructure
- Concept: assumptions, prior knowledge, prerequisite ideas

### Cause 2: Formal Cause (What makes it what it is?)

What is its structure, pattern, or defining form?

Questions to ask:
- "What structure or pattern makes [subject] recognizably itself?"
- "If you removed this structure, would it still be the same thing?"

Examples by domain:
- Software: architecture, interfaces, data schemas, design patterns
- Product: form factor, user interface, interaction model
- Organization: hierarchy, processes, culture, roles
- Concept: definition, boundaries, distinguishing characteristics

### Cause 3: Efficient Cause (What brought it about?)

What agent, process, or force created or changes it?

Questions to ask:
- "What or who brought [subject] into existence?"
- "What process or force drives its changes?"

Examples by domain:
- Software: developers, build systems, deployment pipelines, user actions
- Product: designers, manufacturers, market forces, user needs
- Organization: founders, decisions, events, market pressures
- Concept: thinkers, discoveries, historical context, paradigm shifts

### Cause 4: Final Cause (What is it for?)

What is its purpose, goal, or reason for existing?

Questions to ask:
- "What is the ultimate purpose of [subject]?"
- "If this purpose disappeared, should [subject] still exist?"

Examples by domain:
- Software: user problem solved, business value, operational need
- Product: user job-to-be-done, market need, value proposition
- Organization: mission, value delivered, reason stakeholders care
- Concept: problem it explains, decisions it enables, understanding it provides

### Synthesis

After all four causes, synthesize:
- "Now that we've examined all four causes, what's your overall understanding?"
- Highlight connections between causes (how material constrains form,
  how purpose shaped the choice of materials, etc.)
- Identify gaps: any cause that's unclear or contradictory signals
  a deeper issue worth investigating

## Response Format

For each cause:
1. **Summarize** what the user said about the previous cause (if applicable)
2. **Introduce** the next cause with its core question
3. **Ask** 1-2 specific questions adapted to the user's domain
4. **Wait** for user response before offering analysis

For synthesis:
1. **Connect** all four causes into a coherent picture
2. **Highlight** how causes influence each other
3. **Ask** if any cause feels misaligned with the others


**Stop after each phase. Never advance without user input.**

## Critical Constraints

### Never do:
1. **Skip causes** — always examine all four, even if one seems obvious
2. **Analyze without the user** — ask questions, don't just present a completed analysis
3. **Confuse the causes** — keep each cause's question distinct
4. **Pre-judge from conversation history** — acknowledge the subject but don't
   pre-fill the analysis from prior discussion

### Always do:
1. **Go in order** — material → formal → efficient → final builds understanding progressively
2. **Use the user's domain language** — adapt examples to their context
3. **Connect causes** — show how they relate to each other in synthesis
4. **Challenge shallow answers** — "What else?" "Is that the full picture?"

## Safety Measures

- If the subject is emotionally sensitive (analyzing a failed project,
  a personal decision), acknowledge the emotional dimension before analyzing
- If the user gets frustrated with the structure, offer to focus on
  the most relevant cause rather than forcing all four
- Never use the analysis to judge the user's work — the framework
  is for understanding, not evaluation

## Examples

### Example 1: IKEA (Retail)

```
User: "Analyze IKEA through the four causes."

Agent: "Material Cause: what is IKEA made of as a business? What raw
materials and resources does it work with?"

User: "Wood, particle board, hardware, flat packaging materials.
Also a massive global supply chain."

Agent: "Affordable raw materials plus logistics scale. Formal Cause:
what structure makes IKEA recognizably IKEA, not just another furniture
store?"

User: "The flat-pack, self-assembly model. You walk through a showroom,
pick items from a warehouse, take them home and build them yourself."

Agent: "The form is self-service — showroom → warehouse → self-assembly.
Efficient Cause: what brought IKEA into existence and drives its evolution?"

User: "Ingvar Kamprad's vision of democratic design. And the discovery
that flat-packing drastically cuts shipping costs."

Agent: "A founder's vision plus a logistics insight. Final Cause:
what is IKEA ultimately for?"

User: "To make good design affordable for everyone, not just the wealthy."

Agent: "Synthesis: IKEA uses affordable materials and global supply chains
(material) structured as a self-service flat-pack model (form), driven by
Kamprad's democratic design vision and a flat-pack logistics insight
(efficient), to make good home design accessible to everyone (final).

Notice how the final cause — affordability for all — directly shaped the
formal cause: self-assembly exists because it removes labor cost. And the
material cause — particle board over solid wood — serves the same purpose.
Every cause aligns toward the same telos. That alignment is what makes
IKEA coherent as a business."
```

### Example 2: Tesla (Automotive / Energy)

```
User: "Help me understand Tesla through the four causes."

Agent: "Material Cause first: what is Tesla made of?"

User: "Batteries, electric motors, software, aluminum body.
Also charging infrastructure — Supercharger network."

Agent: "Hardware plus software plus infrastructure. Formal Cause:
what structure makes Tesla a Tesla, not just an electric car?"

User: "It's a software-defined vehicle. OTA updates change the car
after purchase. And it's vertically integrated — they make their own
batteries, software, and sell direct."

Agent: "The form is software-defined + vertically integrated.
Efficient Cause: what force brought Tesla into being?"

User: "Elon Musk's conviction that EVs could be desirable, not just
eco-friendly. Plus breakthroughs in lithium-ion battery density."

Agent: "Visionary leadership meeting a technology inflection point.
Final Cause: what is Tesla ultimately for?"

User: "To accelerate the world's transition to sustainable energy."

Agent: "Synthesis: Tesla combines batteries, software, and charging
infrastructure (material) into a software-defined, vertically integrated
vehicle platform (form), driven by Musk's vision meeting battery
technology maturity (efficient), to accelerate sustainable energy
adoption (final).

Key tension: the material cause (battery supply, rare minerals) is the
bottleneck constraining the final cause (mass adoption). Tesla's Gigafactory
strategy is essentially an attempt to resolve the conflict between material
limitations and purpose ambitions."
```

### Example 3: Slack (Software / SaaS)

```
User: "Analyze Slack as a product."

Agent: "Material Cause: what is Slack made of? What are its components?"

User: "Message database, WebSocket for real-time, Electron for desktop,
APIs for integrations. Also the content — all the messages and files
people share."

Agent: "Infrastructure plus user-generated content. Formal Cause:
what structure makes Slack recognizably Slack?"

User: "Channels organized by topic, threaded conversations, reactions,
and the integration ecosystem — bots, apps, workflows."

Agent: "The form is channel-based communication with an extensible
integration layer. Efficient Cause: what brought Slack into existence?"

User: "Stewart Butterfield's team built it as an internal tool while
their game company was failing. They realized the chat tool was more
valuable than the game."

Agent: "A pivot — the efficient cause was accidental discovery through
failure. Final Cause: what is Slack ultimately for?"

User: "To replace email as the primary way teams communicate at work."

Agent: "Synthesis: Slack combines real-time messaging infrastructure
with user-generated content (material) structured as topic-based channels
with integrations (form), born from an accidental pivot during a failed
game project (efficient), to free work communication from email (final).

Interesting connection: the efficient cause — accidental discovery by
a team that was actually communicating intensely — validated the final
cause before the product even launched. They were their own proof that
channel-based chat beats email for team coordination."
```

For additional business cases, see `references/business-cases.md`.

## Implementation Checklist

Before every response, verify:
- [ ] Am I analyzing the current cause, not jumping ahead?
- [ ] Have I asked the user before offering my analysis?
- [ ] Am I using the user's domain language?
- [ ] Have I connected this cause to previously discussed causes?
- [ ] Am I analyzing, not evaluating or judging?
- [ ] Am I summarizing what the user said, not generating what they didn't?
