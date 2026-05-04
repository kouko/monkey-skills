# Lens: Frame Analysis (Goffman + Lakoff)

> **Sources**:
> - Erving Goffman, *Frame Analysis: An Essay on the Organization of Experience* (Harper & Row, 1974). Primary frameworks Ch 2; keying Ch 3 (definition with quote on p 44 — "an activity already meaningful in terms of some primary framework... transformed into something patterned on this activity but seen... to be quite something else"); fabrications Ch 4; the manufacture of negative experience Ch 11; vulnerabilities of experience and frame traps Ch 12.
> - George Lakoff & Mark Johnson, *Metaphors We Live By* (University of Chicago Press, 1980; 2003 afterword edition). Book is 30 chapters total. Three-type taxonomy (Structural / Orientational / Ontological) introduced in Ch 1; orientational metaphors Ch 4; ontological metaphors Ch 6.

> **Synthesis note**: This file combines Goffman's frame analysis (1974) and Lakoff & Johnson's conceptual metaphor theory (1980). The two were not co-published. Combining them is a methodological choice by `deconstruct-toolkit` — Goffman names the *social frame* (what kind of situation the text presumes), Lakoff names the *cognitive frame* (what mental structures shape the language). They operate at different levels of the same phenomenon. See [ADR-0003](../../../docs/adr/0003-lens-synthesis-disclosure.md).

Two complementary framings: Goffman's **frame analysis** for the social
context-setting work the artifact performs, Lakoff's **conceptual
metaphor** for the cognitive structures embedded in the language.

## When to apply this lens

- Political / ideological texts
- Texts with strong recurring metaphors
- Texts where you suspect hidden assumptions or worldview enforcement
- Branding / corporate identity materials (heavy framing work)
- Manifestos / mission statements

## When NOT to apply

- Texts with no metaphorical structure (technical reference)
- Texts where the frame is openly disclosed (peer-reviewed papers usually)
- Pure descriptive content (raw data, news reports without editorial)

---

## Part 1: Goffman's Frame Analysis

A "frame" is the implicit world-view that makes a text meaningful.
Same words inside different frames carry different weight.

| Concept | Question |
|---|---|
| **Primary framework** | What world-view does the text presume? What is the "real" thing this text refers to? |
| **Keying** | What tone / register is in play? (Serious / ironic / instructional / playful / urgent) |
| **Fabrication** | Is the surface frame ≠ real intent? (Does the text say one thing while doing another?) |
| **Frame vulnerability / break** | Where does the text deliberately violate its own expectations or expose a frame trap? (Ch 12, "Vulnerabilities of Experience") |

### Worked move 1: Primary framework detection

Ask: "If a reader from outside this context picked up this text, what
would they need to know to even begin understanding it?"

That is the primary framework. Make it explicit.

Example: A SaaS startup pitch deck assumes a primary framework of
**venture-funded growth tech**. Inside that frame: "burn rate" is
acceptable; "cash flow positive" is suspect (signals slow growth).
**Outside** that frame, those valences flip.

### Worked move 2: Keying

The same content can be keyed differently:

- "We hit our Q3 numbers" — *celebratory* keying (party / champagne emoji)
- "We hit our Q3 numbers" — *military* keying (mission accomplished, salute)
- "We hit our Q3 numbers" — *deadpan* keying (next slide, please)

Identify which keying the artifact uses, and what would change if it
were re-keyed differently.

### Worked move 3: Fabrication detection

A fabrication is when the surface frame differs from the actual frame.

| Surface frame | Actual frame |
|---|---|
| "Open discussion" | The decision is made; this is consultation theater |
| "Customer obsession" | Internal-metrics obsession dressed as customer focus |
| "Empowering individuals" | Standardization through individual-flavored UI |

Spotting fabrication is core to deconstruction. Look for places where
the *invitation* of the text contradicts its *structure*.

---

## Part 2: Lakoff's Conceptual Metaphor

Every strong metaphor maps a **source domain** onto a **target domain**.
The mapping carries consequences — and the consequences are usually
invisible until named.

### Analytical procedure

For each strong metaphor in the text:

1. **Identify the source domain** — what is being borrowed? (war / journey / family / horse harness / building / disease / sports / theater)
2. **Identify the target domain** — what is being described? (AI governance / business / life / education / politics)
3. **Map the features that carry over** — which attributes of source are projected onto target?
4. **Examine power relations** — who's the rider / general / parent / coach in the implicit hierarchy?
5. **Reframe** — what other metaphors could replace this? What changes when they do?

### Worked example: "Harness Engineering" for AI governance

- **Source domain**: Horse harness (reins, bridle, bit, halter)
- **Target domain**: AI agent governance
- **Mapping**: Human=rider, AI=horse, rules=reins, oversight=bit-and-bridle
- **Power relations**: Human dominant, AI as powerful-but-controlled animal
- **Reframe options**:
  - "AI as colleague" — implies negotiation, no harness
  - "AI as toolbox" — implies inanimate, no agency
  - "AI as apprentice" — implies growing capability, gradual autonomy
  - "AI as tide" — implies cannot be controlled, must be channeled

Each reframe carries different ethics: the harness frame justifies
strict constraint; the colleague frame demands respectful collaboration;
the tide frame admits limits to control.

### Common metaphor source domains in business writing

| Source | Target often is | Embedded values |
|---|---|---|
| **War** | Competition, marketing, sales | Adversarial, zero-sum, conquest |
| **Journey** | Career, project, learning | Linear, destination-oriented, milestones |
| **Family** | Team, company | Loyalty, hierarchy, obligation |
| **Construction** | Strategy, system | Foundation, layers, blueprints |
| **Sports** | Team, project | Coach-player hierarchy, season metaphor |
| **Disease** | Problem, threat | Spread, infection, immune response |
| **Garden** | Growth, ecosystem | Cultivation, weeds, organic |

### Pitfalls

- **Treating metaphor as decoration**: Lakoff's claim is that conceptual metaphors *structure thought*, not just decorate it. The metaphor is doing work, not just adding flavor.
- **Reframing without commitment**: listing alternative metaphors is preparation, not analysis. Pick one alternative and articulate what specifically changes.
- **Mistaking dead metaphors for live ones**: "leverage," "synergy," "deep dive" are mostly dead. Focus analytic attention on metaphors that still carry live cognitive structure.

---

## Combining Goffman + Lakoff

Use Goffman to surface the *social frame* (what kind of situation does
this text assume), and Lakoff to surface the *cognitive frame* (what
mental structures shape the language).

A strong frame analysis names both:

> "The text operates inside a **venture-funded growth tech** social
> frame (Goffman) and uses a **war metaphor** (Lakoff) to structure
> competitive language. Together: the reader is positioned as a
> wartime founder, where adversarial action is keyed as virtuous and
> the horse-harness metaphor would be unthinkable."

## Output format

```markdown
### Goffman frame analysis
- Primary framework: ...
- Keying: ...
- Fabrication detected? <yes / no — describe>
- Frame break(s): ...

### Lakoff conceptual metaphor
- Source domain: ...
- Target domain: ...
- Mapping: <bullet list of carried-over features>
- Power relations: ...
- Reframe alternative: ... (describe what changes)
```

End with 1-line synthesis: "The text positions the reader as **X**,
using **Y** metaphor to make **Z** feel natural. The unstated
alternative is **W**."
