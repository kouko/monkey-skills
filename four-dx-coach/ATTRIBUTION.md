# ATTRIBUTION

## Source book

**The 4 Disciplines of Execution: Achieving Your Wildly Important Goals** (2nd edition, revised and updated, 2021)

- Authors: Chris McChesney, Sean Covey, Jim Huling, Scott Thele, Beverly Walker
- Publisher: Simon & Schuster
- ISBN: 9781982156992
- Publication date: 2021-04-20
- Language: English (US)

This plugin distills the book's methodology — the four disciplines of execution, the whirlwind concept, lead/lag measure framework, compelling scoreboard test, weekly WIG Session protocol, Battles 2x2 for Primary WIG selection, Targets-not-Plans cascade discipline, commitment vs compliance, and XPS audit framework — into atomic, agent-invocable skills across **three scopes**: personal (solo / dyadic), team-leader (intra-team), and team-member (participant inside someone else's WIG). The book itself is the canonical source; readers should buy it to access the full case material, multi-team rollout protocols (Parts 2–3), and underlying research.

## Pipeline

Distillation produced via `tsundoku:book-distill` (`monkey-skills/tsundoku`), implementing the RIA-TV++ pipeline:

- **Stage 0 — Adler analytical reading** → `BOOK_OVERVIEW.md`
- **Stage 1 — 5 parallel sub-agent extractors** → candidate pool (172 candidates)
- **Stage 1.5 — Triple verification** (V1 cross-domain, V2 predictive power, V3 exclusivity) → 121 verified units across 7 skill clusters
- **Stage 2 — RIA++ render** (Reading / Interpretation / A1-Past / A2-Future / Execution / Boundary) → 17 atomic SKILL.md + 1 router across 3 scopes (7 personal + 6 team-leader + 3 team-member + 1 router = 18 total)
- **Stage 3 — Zettelkasten linking** → inter-skill relations + INDEX.md
- **Stage 4 — Adversarial pressure test** → ≥6 test prompts per skill with enterprise-misfire / scope-confusion lures

Audit trail (candidates / rejected / verified.md / Stage 0 overview / Stage 4 test outcomes) preserved at `~/.tsundoku/cache/distilled/The-4-Disciplines-of-Execution/` on the maintainer's machine.

## Upstream credit (RIA-TV++)

The pipeline is adapted from:

- **kangarooking/cangjie-skill** (MIT License) — original RIA-TV++ design for book→skill distillation
- **Mortimer J. Adler & Charles Van Doren**, *How to Read a Book* — Stage 0 analytical-reading procedure
- **Niklas Luhmann**, Zettelkasten method — Stage 3 linking structure
- **趙周 (Zhao Zhou)**, RIA reading method — A1 / A2 framing
- **Tiago Forte**, Progressive Summarization — distillation philosophy
- **Charlie Munger** — inversion / circle-of-competence framing in V2 / V3 verification

## Three-scope reorientation

The book itself is anchored at the multi-team-rollout scale (Leader-of-Leaders cascade, enterprise XPS audit, top-down Primary-WIG selection). This plugin reorients the methodology across **three scopes** the book under-serves directly:

1. **Personal (7 skills)** — first-pass distillation. Re-anchored at solo / dyadic scale per user direction. Agent fills the peer-witness role the book assumes is a colleague.
2. **Team-leader (6 skills)** — second-pass distillation. Anchored at intra-team scale (single team, single leader). Includes Primary WIG selection (Battles 2x2), Targets-not-Plans cascade, leader-onboarding (commitment vs compliance), facilitator-mode WIG Session, and XPS audit. Multi-team / Leader-of-Leaders rollout is still hand-off territory.
3. **Team-member (3 skills, V1 ⚠️ partial)** — second-pass distillation. The book speaks mostly from the leader POV; member-side guidance is reconstructed by inverting the leader-facing protocol (WIG comprehension as inversion of cascade; commitment-prep as inversion of facilitator session-prep; account-debrief as inversion of leader's accountability check). Sufficient for V1 but flagged as the scope where book grounding is thinnest.

## License

This plugin's code, prompts, and skill specifications: **MIT** (see [`../LICENSE`](../LICENSE)).

The book's copyright is held by the authors and Simon & Schuster. This plugin paraphrases methodology and uses ≤150-character verbatim quotes per skill with chapter citations — a fair-use distillation of methodology, NOT a substitute for reading the book.

## How to cite

If you reference this plugin in writing, please cite both:

> McChesney, C., Covey, S., Huling, J., Thele, S., & Walker, B. (2021). *The 4 Disciplines of Execution* (2nd ed.). Simon & Schuster.
>
> kouko (2026). *four-dx-coach*: Personal-coach distillation of *The 4 Disciplines of Execution*. monkey-skills marketplace. https://github.com/kouko/monkey-skills/tree/main/four-dx-coach
