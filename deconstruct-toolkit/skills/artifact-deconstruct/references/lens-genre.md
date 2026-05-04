# Lens: Genre Analysis (Swales + Bhatia)

> **Sources**:
> - John M. Swales, *Genre Analysis: English in Academic and Research Settings* (Cambridge University Press, 1990). The CARS (Create A Research Space) model is presented in Ch 7, "Research-process genres," pp 141–146.
> - Vijay K. Bhatia, *Analysing Genre: Language Use in Professional Settings* (Longman, 1993). Move-step analysis is developed Ch 2; sales-letter genre Ch 3 (pp 45–64); legislative genre Ch 4.

Genre analysis recovers the **conventional move structure** of any
recognizable document type — and identifies when moves are **missing**
or **weak**.

## When to apply this lens

- Document packs (recognizable kits)
- SOPs / playbooks / procedures
- Academic papers (especially abstracts and introductions)
- Business proposals / RFPs / sales letters
- Anything where you can name the document genre

## When NOT to apply

- Unrecognizable / experimental forms
- Personal expression where no genre conventions apply
- Multimedia where text is secondary

## Step 1: Identify the genre

The first job of this lens is to **name the genre** and look up its
expected moves.

Common business / professional genres and their canonical move sets:

### Sales / marketing genres

#### Sales letter / DM (Bhatia)

1. Establishing credentials
2. Introducing the offer
3. Offering incentives
4. Enclosing documents
5. Soliciting response
6. Using pressure tactics (optional)
7. Ending politely

#### Landing page / DTC product page

1. Pain articulation (or aspiration evocation)
2. Solution introduction
3. Mechanism / feature display
4. Proof (testimonial / data / case)
5. Risk reversal (refund / trial)
6. Call to action

### Academic genres

#### Research paper introduction (Swales CARS)

- Move 1: **Establishing a territory**
  - Step 1A: Claiming centrality
  - Step 1B: Making topic generalization
  - Step 1C: Reviewing previous research
- Move 2: **Establishing a niche**
  - Step 2A: Counter-claiming
  - Step 2B: Indicating a gap
  - Step 2C: Question-raising
  - Step 2D: Continuing tradition
- Move 3: **Occupying the niche**
  - Step 3A: Outlining purposes
  - Step 3B: Announcing principal findings
  - Step 3C: Indicating structure of paper

### Business genres

#### Strategy proposal

1. Context establishment
2. Problem definition
3. Options consideration
4. Recommended option
5. Implementation roadmap
6. Risk register
7. Decision request

#### Internal rollout document

1. Pain articulation ("here's why we need to change")
2. Solution introduction ("here's what we're rolling out")
3. Proof / case study ("here's where it worked")
4. Risk acknowledgment ("here's where it might not")
5. Implementation plan ("here's how we'll do it")
6. Call to action ("here's what we need from you")

#### Sales pitch deck

1. Hook / problem statement
2. Market opportunity
3. Solution / product
4. Traction / proof
5. Business model
6. Team
7. Ask

## Step 2: Map the artifact's moves

For each section / paragraph of the artifact, label which canonical
move it performs. Use a table:

| Artifact section | Move performed | Notes |
|---|---|---|
| §1 "Why now" | Pain articulation | Strong |
| §2 "What we propose" | Solution introduction | Adequate |
| §3 (none) | Proof / case study | **Missing** |
| §4 "Risks" | Risk acknowledgment | Strong — explicit failure modes |

## Step 3: Identify missing or weak moves

The most common findings:

| Pattern | What it means |
|---|---|
| Move 2 missing in proposals | "No compelling reason now" — proposal will struggle |
| Risk move missing in rollout doc | "No credibility" — readers will distrust |
| Action move missing in marketing | "No conversion" — readers feel ambivalent |
| Implementation move missing in strategy | "No traction" — feels like wishful thinking |
| Counter-claim move missing in academic intro | "No engagement with literature" — feels insular |

Each missing move is data. Report each one.

## Step 4: Detect over-strong vs under-strong moves

Even when a move is present, it may be unbalanced:

- **Over-strong pain articulation** → reader feels manipulated
- **Under-strong proof** → reader doesn't trust the claim
- **Over-strong CTA** → feels pushy, lowers conversion
- **Under-strong risk register** → feels naive, lowers credibility

Note any unbalanced moves.

## Step 5: Genre transgressions

Sometimes the artifact deliberately violates its genre conventions.
This can be:

- **Successful subversion**: a CTA-less landing page that signals "we're not selling, just sharing" (high-trust play)
- **Failed transgression**: a strategy proposal without options consideration (looks predetermined / political)

Distinguish the two by asking: **does the violation serve the artifact's
purpose, or undermine it?**

## Worked example: Internal AI rollout document

Artifact: 5-page playbook from "Str-Team" introducing AI tools to a
strategy team.

### Move map

| Section | Canonical move | Strength |
|---|---|---|
| §1 "Why this, why now" | Pain articulation | Strong (concrete frustration) |
| §2 "Harness Engineering" | Solution introduction | Strong (named framework) |
| §3 Cases A/B/C | Proof | Strong (specific, recent) |
| §4 "Honest concerns" | Risk acknowledgment | **Unusually strong** (explicit failure modes) |
| §5 "What we ask of you" | Call to action | Strong (segmented by role) |
| § (none) | Implementation roadmap | **Missing** (or implicit only) |

### Findings

- **All moves present except implementation roadmap** — the gap is real
  but probably intentional (the document is awareness-stage, not
  rollout-stage)
- **Risk move is unusually strong** — distinguishes this from typical
  rollout docs which under-acknowledge risk
- **Action move is segmented (individual / manager)** — sophisticated
  audience routing inside a single move

### Verdict

Genre-faithful with one deliberate omission. The strong risk move is
the document's most distinctive feature.

## Pitfalls

- **Forcing the artifact into the wrong genre**: if a document does not
  match any canonical genre, name that fact — do not pick the
  closest-fit and pretend it works
- **Ignoring genre hybrids**: many real artifacts blend genres (rollout
  + sales pitch). Name the hybrid; don't force one genre's lens
- **Missing moves as success metric**: missing a move is **information**,
  not a failure to detect — sometimes the omission is the design

## Output format

```markdown
### Genre identified
<name>, with optional <hybrid notes>

### Move map
| Section | Canonical move | Strength | Notes |
|---|---|---|---|
| ... | ... | strong/adequate/weak/missing | ... |

### Findings
- Missing moves: ...
- Unbalanced moves: ...
- Genre transgressions: ...

### Verdict
<one paragraph>
```

End with 1-line synthesis: "The artifact is **genre-X**, with **N**
canonical moves; **M** are missing; the strongest deviation is **Y**."
