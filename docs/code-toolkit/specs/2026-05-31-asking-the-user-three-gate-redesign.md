# Brief — `## Asking the user` three-gate redesign (code-toolkit)

Date: 2026-05-31 · Stage: brainstorming output → `writing-plans`
Decision locked: **Option A** (plain operative rules; Horvitz cited as rationale;
JA/EN research terms recorded as provenance, NOT in the rule body).

## Problem (Axis 1 — JTBD)

When code-toolkit pauses to ask the user something, the user wants every question
to have already passed three filters: (1) it is genuinely theirs to decide — not
reversible trivia the agent could just do; (2) the agent did its homework —
researched and brought a recommended option, not a raw open-ended punt; (3) it is
phrased so they can decide without decoding internal jargon. Today **only #3 is
enforced** (the existing 7 phrasing rules); #1 and #2 leak. Job: minimize the
user's decision-load — every interruption should be high-value and pre-digested.

## Users (Axis 2)

- **Primary consumer of the rule = the agent at runtime** (Claude), which does NOT
  inherit JA business context — this is the bounded-context fact that drives the
  plain-language decision below.
- **Recipient of the questions = kouko** — cost/step-conscious, conclusion-first,
  multilingual; works across heterogeneous repos: skill-meta work (home turf, high
  confidence) AND unfamiliar app/ML domains (komado-Refs iOS, meeting-transcriber).

## Current State Evidence

- `code-toolkit/skills/subagent-driven-development/SKILL.md` — `## Asking the user`
  block: intro + **7 phrasing rules** (outcome / jargon / numbers / state-anchor /
  research-first[#5] / ≤4-options / compound) + ✅❌ worked example. All 7 govern
  HOW to phrase; none govern WHETHER to ask or WHAT homework to bring.
- `code-toolkit/skills/requesting-code-review/SKILL.md` — near-identical block
  (per-skill duplication, boundary held per CLAUDE.md skill-independence) + a
  boundary note protecting the `code-reviewer` agent's machine-precise verdict.
- Investigation data (session-log mining, 2026-05-31):
  - **Reviewer-pair parallelism: code-toolkit SDD 113/113 (0% serialized)** — not a
    defect; see [[project_code_toolkit_parallelism_well_tuned]].
  - **Under-propose finding**: in non-monkey-skills projects (komado-Refs etc., 237
    questions) only **49%** of questions carry a `(Recommended)` option (vs **71%**
    on home turf), and **17%** are open-ended "how to fix?" punts (vs 5%). Domain
    unfamiliarity inverts the wrong way: less confidence → fewer recommendations.
  - **Over-confirm**: save-memory + per-step "continue?" asks under standing
    authorization (mostly a GLOBAL behavior, only partly code-toolkit's flow).

## Decision

Restructure `## Asking the user` (both skills) from a flat 7-rule list into **three
gates — ① whether to ask · ② what to bring · ③ how to phrase**:

- **① Whether to ask** (NEW): tier by reversibility × cost. Reversible + inferable
  → just do it, mention after (no per-step re-confirm under a standing "just finish
  it" authorization). Irreversible / outward / costly (push / PR / merge / deploy /
  delete / paid run) → always confirm (router rule #4). Genuine taste/scope/
  un-inferable intent → ask, per ②.
- **② What to bring** (NEW teeth; ABSORBS + strengthens old rule #5): a researched
  `(Recommended)` option, never an open-ended punt. Less familiar domain → MORE
  research, not less.
- **③ How to phrase** (KEPT): the existing phrasing rules minus #5 (now 6) + the
  ✅❌ worked example + the "calibration target" closing line, verbatim.

**Wording is plain-language English/behavioral. The operative rules name NO
culturally-specific term.** Grounding cite = **Horvitz, *Principles of
Mixed-Initiative User Interfaces*, CHI 1999** (the canonical, peer-reviewed anchor;
act-vs-ask is a threshold on goal-confidence × cost-of-being-wrong).

Net length: ~+12 lines (gate ① + gate ②), offset by deleting standalone rule #5.

## Alternatives Considered (Axis 4 — research-grounded, EN + JA)

Three wording variants were weighed: **A** plain rule + Horvitz-only citation;
**B** plain rule + one-clause 確連報 echo in the rationale; **C** the JA term as the
rule's mnemonic in the body. **A chosen; C rejected.** Four independent traditions
converge on "operative rules plain, term out of the rule body":

- **Plain language** ([Digital.gov Federal Plain Language Guidelines](https://digital.gov/guides/plain-language/principles/avoid-jargon)):
  avoid unnecessary jargon; if unavoidable, define nearby in plain words.
- **DDD Ubiquitous Language** ([Agile Alliance](https://agilealliance.org/glossary/ubiquitous-language/)):
  named concepts help only WITHIN a shared bounded context; cross-boundary terms
  "leak" and alienate. The rule's consumer (the agent) does not share JA context →
  the term is a cross-boundary leak. **This is the decisive test.**
- **Style-guide practice** ([Google C++ Style Guide](https://google.github.io/styleguide/cppguide.html)):
  rules carry rationale ("why") — Horvitz is the legitimate why.
- **JA 形骸化** ([Monoxer](https://corp.monoxer.com/blog/enterprise/business-manual-creation)):
  jargon-laden manuals become dead form; even JA practice doesn't assume the reader
  knows business terms like 確連報.

Counter (acknowledged, overridden): the mnemonic tradition (SMART / SOLID / 報連相)
shows named framings aid adoption — but only when the term is shared vocabulary,
which fails the bounded-context test here.

Self-referential note: this block IS the AskUserQuestion jargon-leak fix; injecting
JA jargon into the anti-jargon rule is the very failure it exists to prevent.

## Terminology Provenance (REQUIRED — do not delete; preserve across future edits)

The plain wording in the operative rules is a **deliberate translation** of a rich
research lineage. Future editors: before re-wording these gates, read this section
so you neither (a) drift back toward injecting these terms into the rule body, nor
(b) lose the grounding. The plain rule and these source terms are two faces of one
decision.

| Plain rule (what ships) | Original research term | Source |
|---|---|---|
| Act on reversible + inferable; don't ask what you can infer | **察する** (sense without being told); over-asking = **察しが悪い** | JA high-context comms; [Hall 1959, high/low-context](https://en.wikipedia.org/wiki/High-context_and_low-context_cultures) |
| Use session context before asking cold | **空気を読む** (read the air); KY = 空気が読めない | JA high-context comms |
| Bring a recommendation, confirm it — don't punt the open question | **確連報 (確認・連絡・報告)** — the 相談→確認 shift: judge first, confirm a recommendation, vs 報連相's 相談 (punt to boss) | [MoneyForward](https://biz.moneyforward.com/work-efficiency/basic/17537/), [東洋経済](https://toyokeizai.net/articles/-/176175) |
| Never silently guess on consequential/irreversible matters | **忖度** as the failure mode the above guards against | JA business comms |
| Act-vs-ask threshold scaled by cost-of-being-wrong | Expected-utility threshold p*(D,A); scope precision to confidence | **Horvitz, CHI 1999** (the cited anchor) |
| Don't over-confirm low-stakes steps | Confirmation fatigue / autonomy levels | [Changkun](https://changkun.de/blog/ideas/human-in-the-loop-agents/), [Knight Institute](https://knightcolumbia.org/content/levels-of-autonomy-for-ai-agents-1) |

EN ↔ JA convergence (strongest Axis-4 signal): US decision-theory HCI (Horvitz
1999) and modern JA management practice (確連報) independently prescribe the SAME
behavior — judge, then confirm a recommendation; infer the inferable; never punt.

## What Becomes Obsolete (Axis 5)

- Standalone phrasing rule #5 ("research first; don't invent options") — absorbed
  and strengthened into gate ②.
- The flat "Seven rules" framing — replaced by the three-gate structure; the
  remaining 6 phrasing rules survive verbatim under gate ③.

## Out of Scope

- **Save-memory over-confirm** — a GLOBAL behavior (global CLAUDE.md memory
  guidance), not reachable by editing code-toolkit; correct via memory separately.
- **brainstorming skill + using-code-toolkit router** rollout — defer to v0.2
  (matches the plain-language investigation's "fix SDD + requesting-code-review
  first" cadence).
- **>4-options AskUserQuestion InputValidationError** — known bug, unrelated.

## Open Questions

1. **Behavioral validation, not pytest**: SKILL.md prose has no executable test.
   Validate via test-prompts that exercise all three gates (does the agent now (a)
   skip a reversible confirm under standing authorization, (b) bring a recommendation
   instead of an open punt, (c) keep phrasing plain?). Carry the
   exemption-polarity-flip risk ([[feedback_compressing_exemption_section_flips_polarity]]):
   demoting the 6 phrasing rules under gate ③ may lower their prominence — verify
   the phrasing discipline still fires.
2. requesting-code-review gets the same gate ① + a LIGHTER gate ② (its asks are
   "fix now / defer / merge anyway" → carry a recommendation); its verdict-structure
   boundary note stays intact.
