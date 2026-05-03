# Category Routing — Where Does This Knowledge Belong?

`wiki-ingest` must decide which of the 6 type folders a new piece of knowledge goes into. This is a **type-axis** classification (not domain-axis): "what kind of knowledge" decides location, not "which subject area".

## The 6 categories

| Folder | What goes here | Examples |
|---|---|---|
| `entities/` | Trackable named entities — has version, GitHub repo, creator, or stable identity | qlib, obsidian-wiki, Thompson Sampling (as algorithm impl), TSMC |
| `concepts/` | Abstract ideas / frameworks — no specific subject, can be implemented by any system | Exploration-exploitation, Knowledge compounding, Alpha factor (as concept) |
| `synthesis/` | Cross-source analysis answering a specific question | "MAB applications in quant trading: full landscape" |
| `skills/` | Procedural know-how, runbooks, operation steps | "How to install qlib", "wiki-ingest operating procedure" |
| `journal/` | Time-stamped observations, dated entries | Weekly market notes, learning progress logs |
| `references/` | Per-source citation index — auto-generated, one page per source | `2026-04-20-台積電財報.md` |

## Decision tree

```
Is this a procedure / runbook / how-to step?
├── YES → skills/
└── NO ↓

Is this a time-stamped observation tied to a specific date?
├── YES → journal/
└── NO ↓

Is this synthesizing across multiple sources to answer a question?
├── YES → synthesis/
└── NO ↓

Can you point to a specific GitHub repo / version / creator / company / paper?
├── YES → entities/
└── NO  → concepts/
```

## entities vs. concepts (the hardest call)

The 80% rule:

| Question | If YES → entities/ | If NO → concepts/ |
|---|---|---|
| Has a single canonical name that doesn't change? | ✓ | ✗ |
| Has a GitHub repo / paper DOI / company website? | ✓ | ✗ |
| Has a creator or maintainer? | ✓ | ✗ |
| Has versions or releases? | ✓ | ✗ |
| Could be implemented by another system tomorrow? | ✗ | ✓ |
| Is it a "principle" rather than a "thing"? | ✗ | ✓ |

### Worked examples

| Topic | Verdict | Why |
|---|---|---|
| `qlib` | entities/ | Microsoft's Python library, has repo + versions |
| `Alpha factor` | concepts/ | Idea framework; any quant system can have alpha factors |
| `Thompson Sampling` | **entities/** | Algorithm has canonical name, papers, implementations. Boundary case → favor entities |
| `Exploration-exploitation` | concepts/ | Pure trade-off principle, no canonical implementation |
| `TSMC` | entities/ | Specific company |
| `Semiconductor industry concentration` | concepts/ | Phenomenon, not a thing |

**Boundary rule**: when ambiguous, prefer `entities/` (it's easier to navigate downward into specifics than upward into abstractions).

## When the source is multi-topic

A single source (e.g., a research paper) often contributes to multiple wiki pages. The reference page lives in `references/`; each contribution updates the relevant entity/concept page.

```
references/2026-04-15-MAB-survey-paper.md
  contributes_to:
    - entities/Thompson-Sampling
    - entities/UCB
    - concepts/exploration-exploitation
    - synthesis/MAB-quant-trading-landscape (if synthesis triggered)
```

Do NOT put the full paper content in any one entity page. Each entity page extracts only what's relevant to it.

## When to create synthesis pages

Synthesis pages should be created **lazily**, only when:
- User explicitly asks "give me the landscape of X"
- 3+ entity/concept pages have accumulated and a meta-view emerges
- A question crosses domains (e.g., AI + finance)

Do NOT preemptively create synthesis pages during routine ingest.

## When to create skills pages

Skills pages capture **procedural** knowledge:
- Step-by-step runbooks
- "How to use X" guides
- Operational checklists

Distinguish from concepts: `concepts/exploration-exploitation` describes *what* the principle is; `skills/tune-MAB-hyperparams` describes *how* to do something.

## When to create journal pages

Journal pages are explicitly time-bound observations:
- Weekly market summary
- Learning log entries
- Dated incident reports

If the content's value depends on **when** it was observed, it's a journal entry. If the value is timeless, it's an entity/concept.
