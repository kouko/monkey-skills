# Book figure inventory — *The 4 Disciplines of Execution* (2nd ed., 2021)

> **Purpose**: scan log + decision register for figures in the source book that were lost when the book was extracted to markdown via `tsundoku:book-extract`. Used as a **human-tier index** so future skill integration can locate source material without re-scanning the 330-page PDF.
>
> **Source**: McChesney / Covey / Huling / Thele / Walker (2021), *The 4 Disciplines of Execution: Revised and Updated*, Simon & Schuster.
>
> **Scan completion**: 100% (pp 1-330), conducted 2026-05-01.
>
> **Out of scope**: this file is a research-tier index, NOT a skill asset. Skills do NOT load this file at runtime. Mermaid renditions of these figures live in the consuming skill's `references/` or SKILL.md, not here.

---

## ⚠️ Critical framing — LLM-only consumption inside SKILL.md

**Most figures should NOT become mermaid.** Mermaid embedded in `SKILL.md` is parsed by the LLM as text/code, not rendered visually. Color, shape, layout, and renderer-specific quirks contribute zero semantic value. mermaid syntax boilerplate (`flowchart TD`, node IDs, arrow syntax) is pure token cost unless the structure being captured is **graph-shaped** in a way text cannot economically express.

**Mermaid wins only for**:
- **Cycles** (no entry / no exit point — `A → B → C → A`)
- **Multi-edge interdependence** (multiple bidirectional or cross-cutting edges where listing pairs in prose is more verbose than the graph)

**Markdown table / list wins for**:
- Linear sequences (Stage 1 → 2 → 3 → 4 → 5) — numbered list is denser
- Hierarchies (WIG → Team WIGs → Lead Measures) — nested list is denser
- 2×2 matrices (Battles, Individual×Daily) — markdown table is the native format
- Form templates (WIG Builder, Lead Measure Builder, Scoreboard Builder, Session Agenda) — they ARE tables
- Worked-example pairs (THIS / NOT THIS, Lag / Lead) — table is the native format
- Checklists (Did You Get It Right? gates) — bullet list is the native format

**Exception — README.md**: rendered for human consumption on GitHub. Visual mermaid rules apply there. Skill-internal SKILL.md uses LLM-consumption rules.

This reframing was applied 2026-05-01 after initial inventory; the per-figure `Priority` column below still reflects the original mermaid-centric scoring. The **authoritative current recommendation lives in the "Top format priorities" summary table near the bottom**, which re-scores each top candidate against the LLM-format-aware criteria above.

---

## How to use this inventory

1. **Looking up a book concept**: search by chapter or topic, get page ref → consult source PDF or markdown extraction at `~/.tsundoku/cache/markdown/The-4-Disciplines-of-Execution/` if quote needed.
2. **Building a new skill**: read the **Top format priorities** summary table first (LLM-aware). The per-figure rows are inventory + raw priority signals; the summary table is the load-bearing recommendation.
3. **Adding new content to a skill**: pick the right format using the LLM-consumption rules above, then update the figure's row status with `mermaid: <path>`, `table: <path>`, or `list: <path>` after embedding.

## Priority key (legacy mermaid-centric scoring, retained for backward reference)

- **P0** — Originally flagged as high-leverage mermaid candidate. Re-read with LLM lens: only ~25% of P0s should actually become mermaid; the rest are better as table/list.
- **P1** — Medium-leverage; mostly drops to table/list under LLM lens.
- **P2** — Low-leverage; mostly drops to inline text or omitted.
- **P3** — Marginal; almost never worth a dedicated figure.
- **N** — Not for mermaid (originally flagged for table/checklist/inline; this category was correct under both lenses).

## Format key (new — applies LLM-consumption framing)

- `mermaid` — graph-shaped semantic payload (cycle or multi-edge interdependence) that text cannot economically express. **Token-justified only when graph structure IS the message.**
- `table` — 2D matrix or comparison content; markdown table is native and dense.
- `list` — sequential or hierarchical content; numbered/nested list is denser than mermaid.
- `inline` — short conceptual content; one or two sentences in skill prose suffice.
- `omit` — book figure is decorative or already conveyed by adjacent narrative.

## Status key

- `not yet` — content not yet embedded in any skill
- `mermaid: <path>` — mermaid embedded
- `table: <path>` — content embedded as markdown table
- `list: <path>` — content embedded as markdown list
- `inline: <path>` — content quoted as prose, no diagram or table

---

## Inventory by chapter

### Front matter & Foreword (pp i-xxiv)

No figures.

### Part 1 — Learning 4DX as an Operating System

#### Chapter 1: The Real Problem with Execution (pp 1-17)

| # | Page | Figure | Priority | Status | Notes |
|---|---|---|---|---|---|
| 1 | 10 | Behavioral-Change vs Stroke-of-the-Pen Strategy 2-column conceptual contrast | P2 | not yet | Already covered by glossary entry; canonical book term distinction |
| 2 | 13 | Whirlwind 80/20 capacity diagram (day-job vs WIG) | P0 | `mermaid: README.md` | Already in README mechanism section |
| 3 | 16 | Models / Not Yets / Nevers behavioral-adoption distribution | P1 | not yet | Sustain skill candidate; bell-curve-ish concept |
| 4 | 17 | Behavioral-change adoption curve | P2 | not yet | Classic Rogers-style curve, low marginal value |

#### Chapter 2: Discipline 1 — Focus on the Wildly Important (pp 18-53)

| # | Page | Figure | Priority | Status | Notes |
|---|---|---|---|---|---|
| 5 | 36-40 | D1 main concept frame (4 rules: 1 WIG, supports primary, leader-vetoable, From X to Y by When) | P1 | not yet | d1-wig-formulation candidate |
| 6 | 42, 44 | "Narrow focus" funnel (many goals → few WIGs) | P2 | not yet | Decorative repetition |
| 7 | 50-51 | NASA Apollo example diagram (mission → WIG cascade) | P3 | not yet | Single example illustration |

#### Chapter 3: Discipline 2 — Act on the Lead Measures (pp 55-74)

| # | Page | Figure | Priority | Status | Notes |
|---|---|---|---|---|---|
| 8 | 57 | Lag vs Lead measure conceptual diagram (hindsight → foresight arrow) | P0 | not yet | d2-lead-measures core mental model |
| 9 | 58, 64 | Lag/Lead worked examples table (driving, weight loss, sales) | N | table candidate | Better as table than diagram |
| 10 | 71, 73, 74 | Lever metaphor (small lever moves big rock) | P1 | not yet | Iconic 4DX metaphor; used multiple places in book |

#### Chapter 4: Discipline 3 — Keep a Compelling Scoreboard (pp 75-87)

| # | Page | Figure | Priority | Status | Notes |
|---|---|---|---|---|---|
| 11 | 79, 80 | Engagement scoreboard motivation diagrams | P2 | not yet | Generic engagement-loop concept |
| 12 | 81 | "Players' scoreboard" (visible + simple) vs "Coach's scoreboard" (data-rich) contrast | P1 | not yet | d3-scoreboard core distinction |
| 13 | 82 | "Beating the goat" + scoreboard characteristics frame | P2 | not yet | Decorative; runner+goat metaphor on graph |
| 14 | 83-84 | "Creating a winnable game" framing | P3 | not yet | Conceptual frame, not visual figure |

#### Chapter 5: Discipline 4 — Create a Cadence of Accountability (pp 89-113)

| # | Page | Figure | Priority | Status | Notes |
|---|---|---|---|---|---|
| 15 | 89 | D4 circle / cadence of accountability conceptual diagram | P0 | not yet | d4-cadence core mental model |
| 16 | 94 | WIG Session 3-step (Account → Review → Plan) cycle — abbreviated version | P0 | dup with #79 below | Same concept as p 256 fuller version |
| 17 | 95 | 3-gears interlocking diagram (D1+D2+D3+D4 mechanical interdependence) | **P0** | not yet | **Recommended for README mechanism section as 3rd diagram** |
| 18 | 101-103, 102 | Black-and-Gray week calendar (WIG time vs whirlwind time) | P1 | not yet | d4-cadence + meta-strategy-triage candidate |
| 19 | 108-111 | Creativity / innovation engagement diagram | P3 | not yet | Decorative |

### Part 2 — Applying 4DX as a Leader of Leaders

#### Chapter 6: Identify the Battles (pp 117-141)

| # | Page | Figure | Priority | Status | Notes |
|---|---|---|---|---|---|
| 20 | 118 | Strategy Map (full version: Mission → Vision → Strategy → WIG → Battles) | P1 | not yet | meta-team-leader-onboarding candidate |
| 21 | 121 | Failure impact 2x2 (cost vs likelihood) | P2 | not yet | Decision-aid quadrant |
| 22 | 131 | Approaches A/B/C cascade choices | P2 | not yet | Worked-example illustration |
| 23 | **138-139** | **Battles 2x2 prioritization (Impact × Likelihood) — Key Battles selection matrix** | **P1** | not yet | meta-strategy-triage candidate; iconic 4DX-leader-of-leaders artifact |
| 24 | 141 | Specific finish-lines table (battle-level lag measures) | N | table candidate | Better as markdown table |

#### Chapter 7: Translate Battles into Lower-Level WIGs (pp 143-150)

| # | Page | Figure | Priority | Status | Notes |
|---|---|---|---|---|---|
| 25 | 145, 146 | "Translating" cascade tree (org WIG → team WIGs across functionally similar units) | P2 | not yet | Decorative cascade |
| 26 | 148 | Organizational WIG rollup with battles | P3 | not yet | Decorative |

#### Chapter 8: Engage the Leadership Team (pp 151-165)

| # | Page | Figure | Priority | Status | Notes |
|---|---|---|---|---|---|
| 27 | 154-160 | Involvement spectrum diagram (leader-of-leader ownership zones vs frontline-team-leader ownership zones) | P2 | not yet | Org-design diagram, less relevant for personal-coach lens |

#### Chapter 9: Project Execution (pp 167-172)

| # | Page | Figure | Priority | Status | Notes |
|---|---|---|---|---|---|
| 28 | 169-171 | Project 9-step lead measures + milestones list with dated items | P2 | not yet | Project-as-WIG topic, deliberately scoped out per plan |

### Chapter 10: Sustaining 4DX Results and Engagement (pp 173-193)

| # | Page | Figure | Priority | Status | Notes |
|---|---|---|---|---|---|
| 29 | 174, 176, 177, 180, 182 | XPS (Executive Performance Score) framework + dashboard | P3 | not yet | Enterprise audit tool, deliberately scoped out per plan |
| 30 | 185-189 | Recognition + engagement micro-loops | P3 | not yet | Decorative |

### Part 3 — Applying 4DX as a Leader of a Frontline Team

#### Chapter 11: What to Expect (pp 197-210) ⭐ HIGH-VALUE CHAPTER

| # | Page | Figure | Priority | Status | Notes |
|---|---|---|---|---|---|
| 31 | 196 | Stage 1 box: Getting Clear (definition text in styled frame) | P1 | not yet | Component of #36 |
| 32 | 197 | Stage 2 box: Launch | P1 | not yet | Component of #36 |
| 33 | 198 | Stage 3 box: Adoption (the plateau stage) | P1 | not yet | Component of #36 |
| 34 | 200 | Stage 4 box: Optimization | P1 | not yet | Component of #36 |
| 35 | 200 | Stage 5 box: Habits | P1 | not yet | Component of #36 |
| 36 | **202** | **⭐⭐⭐ 5-Stage performance curve** (line graph: Stage 1→2→**plateau at 3**→ramp 4→5) | **P0** | not yet | **sustain skill core mermaid candidate**; book's most iconic "expected progress" visual |
| 37 | 203, 205, 206, 207 | Per-stage callouts and behavior-change application sub-figures | P2 | not yet | Already implied by #36 |

#### Chapter 12: Applying Discipline 1 (pp 211-224)

| # | Page | Figure | Priority | Status | Notes |
|---|---|---|---|---|---|
| 38 | 205 | IF/THEN ranking decision matrix (3 rows: many goals / org-WIG-set / team-is-org) | N | table candidate | Better as markdown decision table |
| 39 | **206** | **Top-down + Bottom-up 4DX center diagram** (Strategic Direction ↓ + Engagement ↑ → 4DX) | **P1** | not yet | d1-wig-formulation candidate |
| 40 | 208 | Hotel WIG brainstorm by department table | N | table candidate | Worked example as table |
| 41 | 209, 211 | Event Management clipboard brainstorm | N | inline | Worked example, kept in book quote |
| 42 | **213** | **WIG → 3 Team WIG line-of-sight tree** | P1 | not yet | d1-wig-formulation cascade visual |
| 43 | 214 | Top-down vs bottom-up brainstorming options | P3 | not yet | Decorative |
| 44 | 215 | THIS / NOT THIS verb-start examples | N | table | d1-wig-formulation worked examples table |
| 45 | 216 | From X to Y by When examples table (3 rows) | N | table | d1-wig-formulation worked examples table |
| 46 | 217 | THIS / NOT THIS WIG quality examples | N | table | d1-wig-formulation worked examples table |
| 47 | 217 | THIS / NOT THIS Focus on what not how | N | table | d1-wig-formulation rule examples |
| 48 | 218 | "Test top ideas" 4-question filter | N | checklist | d1-wig-formulation SHOULD-gate input |
| 49 | **219** | **WIG Builder 5×5 grid template** (Ideas / From X / To Y / Deadline / Rank) | **P0** | not yet | **d1-wig-formulation `worksheets/wig-builder.md` direct port** |
| 50 | **220** | **D1 lag-measure 7-item "Did You Get It Right?" SHOULD-checklist** | N | checklist | **d1-wig-formulation `audit-mode` SHOULD-gate direct port** |

#### Chapter 13: Applying Discipline 2 (pp 225-241)

| # | Page | Figure | Priority | Status | Notes |
|---|---|---|---|---|---|
| 51 | 221 | Team / Lag / Lead measure examples table (Hospital / Shipping / Restaurant) | N | table | d2-lead-measures worked examples table |
| 52 | **224** | **WIG → Small Outcome / Leveraged Behavior dual-track diagram** (Younger Brothers safety boots example) | **P1** | not yet | d2-lead-measures two-types-of-leads visual |
| 53 | 224 | Same dual-track template (grocery sales example) | P3 | not yet | Duplicate of #52 |
| 54 | 226 | 3-bucket lead-measure brainstorm template (New Actions / Pockets of Excellence / Fix Inconsistencies) | P1 | not yet | d2-lead-measures brainstorm template |
| 55 | 228 | Event Management lead-measure clipboard brainstorm | N | inline | Worked example |
| 56 | 229 | Uninfluenceable Lag vs Influenceable Lead conversion table | N | table | d2-lead-measures conversion examples |
| 57 | 230 | Ongoing Process vs One-and-Done filter table | N | table | d2-lead-measures filter rule |
| 58 | 233 | Individual / Team × Daily / Weekly 2×2 (granularity decision) | P1 | not yet | d2-lead-measures + d3-scoreboard granularity decision visual |
| 59 | 233 | Same 2×2 with full trade-off text | P3 | not yet | Duplicate of #58 |
| 60 | 235 | WIG / Lead Measure verb-start examples table | N | table | d2-lead-measures rule examples |
| 61 | 237 | 11-step Sales Process flow (Identify Target → Resolve Concerns → WIG=$) | P2 | not yet | d2-lead-measures process-as-leverage example |
| 62 | **237** | **Process leverage points diagram** (steps 4, 6 circled as Lead Measures, step 11 = Lag) | **P1** | not yet | d2-lead-measures process-leverage core teaching visual |
| 63 | 239 | Overall WIG → Team WIG → 2 Lead Measures cascade | P3 | not yet | Repeats #42 with leads attached |
| 64 | **240** | **Lead Measure Builder 3×3 grid template** | **P0** | not yet | **d2-lead-measures `worksheets/lead-measure-builder.md` direct port** |
| 65 | **241** | **D2 lead-measure 6+1 "Did You Get It Right?" SHOULD-checklist** | N | checklist | **d2-lead-measures `audit-mode` SHOULD-gate direct port** |

#### Chapter 14: Applying Discipline 3 (pp 243-257)

| # | Page | Figure | Priority | Status | Notes |
|---|---|---|---|---|---|
| 66 | **243** | **Less / More Involvement see-saw fulcrum diagram** (Choose Theme → Contribute Ideas → Design → Build → Ownership ↑) | **P1** | not yet | d3-scoreboard team-involvement teaching visual |
| 67 | 244 | "Beat the Goat" trend-line scoreboard (runner vs goat icons on line graph) | P2 | not yet | One of 5 scoreboard themes; iconic but example-specific |
| 68 | 245 | Speedometer scoreboard (3 gauge meters) | P2 | not yet | One of 5 scoreboard themes |
| 69 | 246 | Bar Chart scoreboard (3rd-grade reading classes) | P3 | not yet | Common chart type, no mermaid value-add |
| 70 | 246 | Smiley / Andon scoreboard (red/green tile faces) | P2 | not yet | One of 5 scoreboard themes |
| 71 | 247 | THIS / NOT THIS simple-vs-complex line chart | P3 | not yet | Decorative contrast |
| 72 | 247 | THIS / NOT THIS planned-vs-actual with Net Gain/Loss | N | inline | Layout convention example |
| 73 | 248 | Trend-line target-line vs ramp-up-and-sustain target options | P2 | not yet | d3-scoreboard target-line subtype |
| 74 | 248 | Bottling water dual-line graph + maintenance check matrix | P3 | not yet | Worked example |
| 75 | **249** | **Serena Event Management 3-tile final scoreboard** (WIG line + individual table + lead-measure bar) | P1 | not yet | d3-scoreboard complete-template worked example |
| 76 | **250** | **Scoreboard Builder template** (Team WIG / Lag / Lead 1+2 + Graph slots) | **P0** | not yet | **d3-scoreboard `worksheets/scoreboard-builder.md` direct port** |
| 77 | **251** | **D3 scoreboard 8-item "Did You Get It Right?" SHOULD-checklist** | N | checklist | **d3-scoreboard `audit-mode` SHOULD-gate direct port** |

#### Chapter 15: Applying Discipline 4 (pp 259-276)

| # | Page | Figure | Priority | Status | Notes |
|---|---|---|---|---|---|
| 78 | 261 | Serena WIG Session 3-tile scoreboard (D4 context) | P3 | not yet | Duplicate of #75 |
| 79 | **256** | **⭐⭐⭐ Account → Review Scoreboard → Plan WIG Session 3-step cycle** | **P0** | not yet | **d4-cadence core mermaid candidate**; book's canonical D4 mechanism diagram |
| 80 | **258** | **WIG Huddle 5-7 minute alternative** (Review Scoreboard / Report on Last Week's Team Commitment / Make New Commitments) | **P1** | not yet | d4-cadence flexibility clause for low-discretionary-time teams |
| 81 | 264 | Low-impact vs High-impact Commitment 5-row contrast table | N | table | d4-cadence commitment-quality examples |
| 82 | **266** | **⭐⭐⭐ 3 Steps to Accountability circle** (Demonstrate Respect → Reinforce Accountability → Encourage Performance) | **P0** | not yet | **sustain + d4-cadence accountability-with-respect mermaid candidate**; book's missed-commitment recovery script |
| 83 | 268 | Weekly Commitments calendar grid (Mon-Fri × time slots × commitment placement) | P1 | not yet | d4-cadence `worksheets/weekly-commitments-calendar.md` candidate |
| 84 | 271 | WIG Session Agenda template (Where/When/WIGs/Individual Reports/Scoreboard Update) | P0 | not yet | d4-cadence `worksheets/wig-session-agenda.md` direct port |
| 85 | **272** | **D4 WIG Session 10-item "Did You Get It Right?" SHOULD-checklist** | N | checklist | **d4-cadence `audit-mode` SHOULD-gate direct port** |

### The Missing Ingredient (pp 279-285)

No figures. Pure narrative on Humility / Determination / Courage / Love.

### Glossary (pp 286-290)

| # | Page | Figure | Priority | Status | Notes |
|---|---|---|---|---|---|
| 86 | 286-290 | Official term definitions (4DX / WIG / Lag / Lead / From X to Y by When / Battle / War / Whirlwind / Behavioral-Change Strategy / Stroke-of-the-Pen Strategy etc.) | N | inline | **Authoritative vocabulary; ALL skills should reflect these definitions for canonical alignment** |

### Notes / Endnotes (pp 291-301)

No figures, but **endnotes contain primary-source citations** worth grounding. Notable:
- Ch 5 endnote 12: Atul Gawande, *Better* (2007)
- Ch 5 endnote 13: Patrick Lencioni, *Three Signs of a Miserable Job* (2007), pp 136-37 — immeasurement / irrelevance / anonymity origin
- Ch 5 endnote 14: Edward Hallowell, *Crazy Busy* (2007), p 183 — whirlwind psychology anchor
- Ch 11 endnote 16: Vos et al. (2009) PubMed — Erasmus MRSA search-and-destroy primary source
- Ch 13 endnote 17: Jim Collins, "Turning Goals into Results" *HBR* Jul-Aug 1999 — 3M 15% rule academic citation
- Ch 15 endnote 18: John Case, "Keeping Score" *Inc.* June 1998 — whirlwind-meeting failure mode verbatim
- Ch 15 endnote 19: Eric Matson, "Discipline of High-Tech Leaders" *Fast Company* Apr-May 1997 — Stephen Cooper Etec case origin

---

## Top format priorities — authoritative recommendation (LLM-format-aware)

Re-evaluated 2026-05-01 against LLM-only-consumption framing. The original 8-figure mermaid shortlist drops to **2 mermaid candidates** for skill-internal use (+ 1 README mermaid for human visual rendering). The other 5 originally-flagged figures convert to markdown table or list, which is denser for LLM parsing.

### Skill-internal content (LLM consumption)

| Rank | Figure | Page | Target skill | Format | Why |
|---|---|---|---|---|---|
| 1 | **Account → Review Scoreboard → Plan cycle** | 256 | d4-cadence SKILL.md | **mermaid** | 3-node cycle with no entry/exit; loop-back semantics ("week N's Plan becomes week N+1's Account") cannot be expressed as a list without losing the cyclic invariant |
| 2 | **3-gears interlocking (D1-D4 interdependence)** | 95 | (See README row below; if needed inside any skill, use mermaid for same reason) | **mermaid** | Multi-edge bidirectional dependency; enumerating all D1↔D2↔D3↔D4 pairs as prose is more verbose than the graph |
| 3 | 5-Stage performance curve | 202 | sustain SKILL.md | **list** + 1-line plateau callout | Linear 5-stage sequence; the only non-linear semantic ("plateau at Stage 3") is one inline sentence. Curve shape is decorative for LLM |
| 4 | 3 Steps to Accountability (Demonstrate Respect → Reinforce → Encourage) | 266 | sustain + d4-cadence | **list** + per-step verbatim script | Linear 3-step recovery sequence; numbered list with sub-bullets for each step's script is denser than a 3-node mermaid |
| 5 | WIG Builder template | 219 | d1-wig-formulation `worksheets/` | **table** | The template IS a 5×5 table; markdown table is the native format |
| 6 | Lead Measure Builder template | 240 | d2-lead-measures `worksheets/` | **table** | Same — template IS a table |
| 7 | Scoreboard Builder template | 250 | d3-scoreboard `worksheets/` | **table** | Same — template IS a table |
| 8 | WIG Session Agenda template | 271 | d4-cadence `worksheets/` | **table** | Same — template IS a table |
| 9 | Battles 2×2 prioritization (Impact × Likelihood) | 138 | meta-strategy-triage | **table** | 2×2 matrix renders as a 2-row × 2-col markdown table |
| 10 | WIG → 3 Team WIG line-of-sight tree | 213 | d1-wig-formulation | **list** | Hierarchical tree → nested bullet list is denser |
| 11 | Top-down + Bottom-up 4DX center | 206 | d1-wig-formulation | **inline** | Two sentences capture it: "WIGs need both top-down strategic direction AND bottom-up engagement; pure top-down loses ownership, pure bottom-up loses alignment" |
| 12 | WIG → Small Outcome / Leveraged Behavior dual-track | 224 | d2-lead-measures | **table** | 2-column table with worked example beneath |

### Direct-port checklists (LLM-consumption already optimal as bullet lists)

The 4 SHOULD-checklists (pp 220 / 241 / 251 / 272) are **not mermaid candidates**, but are **direct-port material** for the four D-skill `audit-mode` SHOULD-gates as bullet lists. This was the original recommendation and remains correct under the LLM lens.

### Human-rendered content (visual rendering on GitHub)

| Rank | Figure | Page | Target | Format | Status | Why |
|---|---|---|---|---|---|---|
| R1 | WIG Session 3-step cycle (Account → Review → Plan) | 256 | README mechanism section (3 langs) | **mermaid** | ✅ shipped 2026-05-01 in `README.md` / `README.zh-TW.md` / `README.ja.md` | Embedded between "The closed loop" and "Why each discipline matters". Cycle topology + bidirectional next-week loop is graph-shaped. Visual fidelity targeted at GitHub renderer. |
| R2 | 5-Stage performance curve | 202 | README mechanism section (3 langs) | **flowchart LR with stage cards** | ✅ shipped 2026-05-01 in `README.md` / `README.zh-TW.md` / `README.ja.md` | Embedded between discipline table and vocabulary. Used flowchart-with-annotations form (vs xychart-beta) so plateau callout `⚠ most teams quit here` is rendered in-node. Sets time-dimension expectation users currently lacked. |
| R3 | 3-gears interlocking | 95 | README mechanism section (3 langs) | **mermaid (deferred)** | not yet — deferred | Originally proposed as 3rd README mermaid. Deferred because closed-loop diagram (existing) + 5-stage curve (new) already convey D1-D4 interdependence + time dimension. Adding 3-gears risks visual overload at intro level. Reconsider if user feedback indicates interdependence is unclear. |

`obsidian-mermaid-visualizer` skill is **not relevant** for skill-internal mermaid (visual rendering is irrelevant for LLM consumption). It MAY be useful for the README mermaid above if visual quality concerns arise; otherwise hand-written mermaid validated by GitHub markdown preview is sufficient.

### Net effort revision

Original Phase B estimate (8 mermaid + 4 worksheet ports): ~3-4 hours.
LLM-aware Phase B estimate (1 skill mermaid + 1 README mermaid + ~10 markdown tables/lists + 4 worksheet table ports): ~2-3 hours, with output that costs **fewer tokens at runtime** than mermaid-everywhere.

---

## Cross-references

- Source markdown: `~/.tsundoku/cache/markdown/The-4-Disciplines-of-Execution/`
- Book overview (Stage 0): `~/.tsundoku/cache/distilled/The-4-Disciplines-of-Execution/BOOK_OVERVIEW.md`
- Case bank with two-axis grading: `four-dx-coach/research/case-inventory.md`
- OKR primary sources: `four-dx-coach/research/okr-primary-sources.md`
- SaaS/tech context + horizontal hybrid: `four-dx-coach/research/saas-tech-context-and-okr-vs-4dx.md`
