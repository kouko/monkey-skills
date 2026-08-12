# Brief: authoring form for loom's implementable documents — fill the holes, then measure before legislating

Date: 2026-08-13
Stage: brainstorming output → writing-plans input
Design-side on-ramp: no criteria row fired (increment to shipped loom-code
mechanisms; no UI surface, no new multi-state behavior) — no detour offered.
Axis 0 queue check: `## Now` empty (no competing bet). One OPEN backlog entry
is adjacent — `2026-07-06-anti-copy-acceptance-greps-pass-paraphrase-copies`,
whose start condition is "next touch of loom-code writing-plans SKILL.md or the
plan-document-reviewer prompt". This arc touches `plan-format.md`, not that
SKILL.md, so the condition does NOT strictly fire; carried in Open Questions
rather than folded in.

## Problem

loom produces two English documents that another agent then implements from:
the **brief** (`docs/loom/specs/`) and the **plan** (`docs/loom/plans/`).
Both are governed by schemas that say what fields must be PRESENT and say
almost nothing about the FORM the field values take — and form is measurably
load-bearing for whether a downstream agent complies.

Two concrete holes, both verified:

1. **The brief schema ships no worked example at all.** Its template
   (`handoff-brief-format.md:119-176`) is a placeholder skeleton whose every
   slot is a descriptive gloss (`:128` `(JTBD-form: when [situation]…)`,
   `:137` `(what will be true when shipped…)`). The only concrete strings in
   the file sit inside anti-patterns (`:180`, `:181`) and both are descriptive
   noun phrases. An author imitating this file has zero examples of a written
   field value to copy.
2. **The plan schema teaches imperative form for two fields and descriptive
   form for the rest.** The rule at `plan-format.md:79` names imperative voice
   for `Description`, and the worked example honors it (`:315` task name,
   `:317` Description) — but the fields an implementer actually executes
   against are Acceptance RED/GREEN, and their example values are descriptive
   (`:325` "query param parsed; passed to renderer; existing JSON path
   unchanged").

Neither document has ever been checked for wording by anything:
`docs/**` is outside the docs-reviewer's jurisdiction
(`agents/docs-reviewer.md:337-340`), and no test in the repo targets
`docs/loom/specs/**` or `docs/loom/plans/**` content. **The two documents that
everything downstream implements from carry the least authoring discipline in
the system.**

The job: **close the two holes that need no new evidence, and build the
smallest instrument that can tell us whether any further authoring rule is
worth legislating — before legislating it.**

## Users

Two, and they are not the same reader:

- **The implementer subagent** (and its two reviewers) — reads a plan task and
  acts. Runs at whatever tier the session runs; the measured failures below
  were all observed on the weak tier, which is the tier that matters because
  it is where form stops being cosmetic.
- **kouko** — reads the brief to sign off scope before SDD starts, and reads
  plan cards throughout. Works in 繁體中文 / 日本語 / English.

Job story: *when I hand a plan to an implementer I have never briefed in
conversation, I want the task text to be written in the form that agent
actually complies with, so that I do not spend a review round on a task that
was executed as written and still wrong.*

## Smallest End State

Two tracks. Track A ships; track B measures and reports, and legislates
nothing on its own.

### Track A — fill the two holes (no new rules, no new evidence needed)

1. **A worked example in `handoff-brief-format.md`.** One complete, realistic
   brief — every required section filled with a real value, not a gloss.
   This is a REPLACEMENT for the placeholder skeleton's descriptive slots,
   not an addition beside them.
2. **Imperative example values for the plan's Acceptance fields.** Extend the
   worked example at `plan-format.md:293-370` so RED/GREEN read in the same
   voice the rule already mandates for `Description`. The RULE text is not
   widened in this arc — only the example, which is what authors copy.

Both are schema-file edits that ship with the plugin. Neither invents a
constraint the repo has not already committed to: the plan's imperative rule
already exists at `:79`; the brief's sections already exist.

### Track B — the smallest blinded panel, run once, on ONE rule

3. **A blinded evaluation harness**, shaped after `slopgent`'s (MIT; see
   Alternatives): authored cases each targeting one named failure mode,
   **matched controls where the rule under test would be the WRONG choice**,
   candidate outputs relabelled and shuffled per case against a stored key,
   a small independent judge panel scoring a fixed rubric, and a
   **pre-registered pass gate declared before the run**.
4. **One rule measured**: does placement/prominence of an instruction inside a
   PLAN TASK change whether an implementer complies? Chosen because it is the
   axis where our own evidence is strongest and the published literature is
   emptiest (see Alternatives).
5. **A written result** — including the case where the gate fails. A failed
   gate ends the question for this rule; it does not get re-run until it
   passes.

The harness does NOT ship in the plugin this arc (see Decision).

## Current State Evidence

- **Forward** (what constrains authoring today): exactly one mood rule exists
  across the whole authoring surface — `plan-format.md:79`
  "`Description`: `<one-assertion unit of work, imperative voice>`", mirrored
  at `writing-plans/SKILL.md:171` and `writing-plans/README.md:34`. Adjacent
  surface-form rules, all in the same file: `:197` (`Observed` in present
  tense), `:225` (unverified assumptions carry a literal label), `:263`
  (Decision Log entries are single physical lines), `:105-109` (Gloss is one
  line in the user's conversation language, never a restatement of the task
  name).
- **Reverse** (who owns the form): `handoff-brief-format.md` owns the brief
  schema and constrains only content and length (`:32` "1-3 sentences",
  `:74` "3-6 sentences") — no mood, placement, or prominence rule anywhere.
  `brainstorming/SKILL.md:197`'s plain-language rule is scoped to the chat
  message and explicitly exempts the artifact ("The brief *file* may keep
  precise identifiers").
- **Error** (today's failure mode): the brief template has no worked example,
  so the prescriptive surface an author imitates is absent
  (`handoff-brief-format.md:119-176`). In the plan, the prescriptive surface
  exists but is mixed: imperative at `:315`/`:317`, descriptive at `:325`
  (GREEN), `:330` (Gloss), `:278` (Decision Log).
- **Data**: no schema change. Both tracks add example values and an
  out-of-plugin instrument; no field is added, removed, or retyped.
- **Boundary**: `agents/docs-reviewer.md:337-340` places `docs/**` outside
  docs-review jurisdiction, so produced briefs and plans are never reviewed
  for wording; no test targets their content. The one runtime prose-form
  validator in the repo, `adjudication_lint.py:11-30`, runs on translated
  renditions, so an English-authoring check would be cloning its shape rather
  than extending its scope. The house pattern for a placement pin already
  exists at `test_requesting_docs_review_skill.py:126-145` (a windowed
  extraction an appended trailing aside fails), and its docstring cites the
  placement memory entry as its reason.

Evidence paths appendix:
loom-code/skills/brainstorming/references/handoff-brief-format.md;
loom-code/skills/writing-plans/references/plan-format.md;
loom-code/skills/writing-plans/SKILL.md; loom-code/agents/docs-reviewer.md;
loom-code/scripts/test_requesting_docs_review_skill.py;
loom-code/scripts/adjudication_lint.py;
docs/loom/memory/imperative-placement-prominence-decides-weak-model-firing.md;
docs/loom/memory/imperative-trigger-cards-beat-descriptive-preloads.md;
docs/loom/memory/prose-only-enforcement-dies-on-weak-executors.md.

## Alternatives Considered (research-grounded)

Three research arms ran: a classification of this repo's own recorded defects,
a bilingual literature sweep (EN + JA), and a source read of two third-party
skill projects. Their results disagree with the starting proposal, which is
why the proposal changed.

| Option | What it means | Evidence |
|---|---|---|
| **Adopt ASD-STE100 / a controlled vocabulary** | One approved term per concept, closed modal set, banned constructions | **Rejected on measurement.** Three independent corpora agree: 6.4% of the 157-entry practice store, 7.7% of 222 findings across PRs #660–#691 (11.0% of prose findings), and 1 case per 199 trailers in secondary consumer repos. Honest range with a looser classification line: 8–13%. Decisive sub-finding: of the prose findings a linter would even be aimed at, ~77% are tagged ambiguity/inconsistency that no vocabulary rule reaches — missing steps, doc-vs-code drift, contradictions only execution exposes. STE also lengthens text (it forbids the compressions that shorten it), which collides with this repo's word ceilings. |
| **A prose linter over authored English** | Mechanical checks on the English source | **Rejected — in-repo base rate exists.** `docs/loom/memory/a-prose-scanner-meets-its-own-vocabulary-first.md`: the closest thing this repo has shipped fired five false positives on the toolchain's OWN severity vocabulary on its first real input. `prose-only-enforcement-dies-on-weak-executors.md` measured the complementary half: vocabulary is the part that already survives on weak executors; enforcement semantics are what die. |
| **A post-hoc rewrite pass** (the `slopkit` architecture, MIT) | Let the model write, then rewrite the draft | **Deferred, not rejected.** It targets slop — unsupported claims, hollow phrasing, overstated confidence — which is a tone/honesty failure, not the ambiguity/compliance failure this brief addresses. Worth its own arc for the relay surface, where loom already has an overclaim problem. Its `slopbeth` benchmark cannot be reused: the project itself calls scoring rivals with its own lint "circular", and its advertised "264 independent judge rows" parse as 3 fixed personas emitting an identical score vector on all 88 cases — a count check, not an evaluation. |
| **Write all four candidate rules now from our own evidence** | Legislate imperative mood, placement, proximity, and check-backed consequences across the authoring stations | **Rejected for the shipping half.** Our evidence is n=2 (`imperative-trigger-cards`: imperative 2/2 vs descriptive 0/2) and n=3 (`imperative-placement-prominence`: haiku 3/3 vs 0–1/3 on identical wording). Shipping a plugin-wide prose contract on that, to repos we cannot observe, is the exact failure mode the two rejected rows above describe. |
| **Fill the evidence-free holes, then measure one rule (CHOSEN)** | Track A ships what needs no new evidence; Track B builds the instrument and reports one result | Matches what the most prescriptive shipped standard actually mandates: Anthropic's skill-authoring guide asserts every one of its prose-form rules without data, and the only method it ships is **evaluation-driven development** — build evals before writing docs, test across Haiku/Sonnet/Opus. |

**What the literature does and does not support** (full arm output in session;
sources listed below by language):

- **Imperative vs descriptive mood — no isolating measurement exists.**
  Explicit absence: no study varies mood alone and reports compliance. Vendor
  guidance asserts it (Anthropic suggests "MUST" over "always"; OpenAI's
  GPT-4.1 guide says one firm sentence is usually sufficient) with no data.
  Our own 2/2-vs-0/2 is therefore *more* direct evidence than anything
  published on this axis — which is a statement about how empty the field is,
  not about how strong our number is.
- **Placement — well measured, but the measurements are about RETRIEVAL, not
  compliance.** *Lost in the Middle* (Liu et al., TACL 2023) measures finding a
  target. *Context Rot* (Chroma, 2025, 18 models) issues no
  instruction-placement recommendation at all. *Instruction Position Matters*
  (WeChat AI, 2023, +9.7 BLEU) is an instruction-TUNING data intervention, not
  a runtime prompt tip. *Instruction (In)Stability* (Harvard, 2024) measures
  system-prompt drift within 8 dialogue rounds but its remedy is model-side
  (`split-softmax`); it did **not** validate restating a rule at the point of
  action. Microsoft's own guide records a null result for instructions-first +
  repeat-at-end on GPT-4.
- **Negative vs positive framing — near-universal vendor rule, essentially
  unmeasured**, and the only counter-evidence found is JA: a practitioner
  reporting that over 217 routing tasks the positive form was ignored ~30% of
  the time while the explicit negation held. Method undocumented — a
  well-specified anecdote, not a refutation, but enough that this arc does not
  import the positive-framing rule.
- **Rule proximity — nothing measured.** Anthropic's "keep references one
  level deep" is mechanism-asserted (models may read a referenced file
  partially), with no numbers.
- **The one cross-vendor standard declines to legislate form**: AGENTS.md
  (Agentic AI Foundation / Linux Foundation) mandates nothing about prose —
  "just standard Markdown. Use any headings you like."
- **EN vs JA divergence** (a finding, not a tie): EN is vendor-standardized and
  unanimous with no data; JA has no institutional standard, produced the only
  counter-claim, and contributed the one measured register result the EN guides
  omit entirely — prompt politeness has a language-dependent optimum
  (RIKEN/Waseda, 2024, EN/ZH/JA).

**Rule form worth adopting from the third-party read** (`slopkit`, MIT): its
rules are imperative and moment-bound, and their distinctive move is a
**paired negative** — the wrong output written immediately beside the right
one ("Edited `verifyToken` at `auth.ts:42`. Tests not run yet." / Not "Fixed
the auth bug."). That sits between the EN vendor rule (say what to do, never
what not to do) and the JA counter-anecdote (the negation is what held): it
supplies both, adjacent. Track A's worked examples use this form.

**My take:** ship Track A, run Track B once, and let the result decide whether
any further authoring rule is written at all. Conditional reversal: if the
Track B panel cannot separate the arms — if judges score placement-varied plan
tasks indistinguishably — then plan/brief text does not behave like skill text,
the four candidate rules stay unlegislated for documents, and the whole
question closes rather than being re-run at a larger sample.

Sources (EN): [Anthropic — Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices);
[Anthropic — Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices);
[OpenAI — GPT-4.1 Prompting Guide](https://developers.openai.com/cookbook/examples/gpt4-1_prompting_guide);
[AGENTS.md](https://agents.md/);
[Lost in the Middle](https://arxiv.org/abs/2307.03172);
[Context Rot](https://www.trychroma.com/research/context-rot);
[Instruction Position Matters](https://arxiv.org/abs/2308.12097);
[Instruction (In)Stability](https://arxiv.org/abs/2402.10962);
[FormatSpread](https://arxiv.org/abs/2310.11324);
[slopkit](https://github.com/ehmo/slopkit) (MIT, © 2026 ehmo).
Sources (JA-origin): [Prompt politeness, EN/ZH/JA](https://arxiv.org/abs/2402.14531);
[Microsoft Learn — プロンプト エンジニアリング手法](https://learn.microsoft.com/ja-jp/azure/ai-foundry/openai/concepts/prompt-engineering);
[Qiita — 217件の実測（否定形が効いたとする反例）](https://qiita.com/yurukusa/items/77ddcd55410e37b570d2).

## Decision

Build Track A (a worked example for the brief schema; imperative example
values for the plan's Acceptance fields) and Track B (a blinded panel with
matched controls and a pre-registered gate, run once on the
placement/prominence rule, with the result written down either way).

Do NOT build: a controlled vocabulary or terminology table; a prose linter
over authored English; a rewrite pass; a general writing standard; any rule
text widening beyond the two example fixes; authoring rules at the reviewer
agents or at any sibling loom plugin.

**The harness does not ship in the plugin this arc.** It has produced no
result yet, and shipping an unused instrument is worse than shipping none.
This is deliberately NOT the `plan_card.py` / `backlog_index.py` case
(`docs/loom/memory/` records external repos silently degrading when tooling
five skills REQUIRED failed to ship): no skill depends on this harness, so its
absence degrades nothing. Ship it in a later arc if and only if it earns its
keep here.

## Out of Scope

- Any authoring rule for the five reviewer agents' findings, SDD's Decision
  Log, or the sibling plugins' documents (`loom-spec` change-folders,
  `DESIGN.md`, `ui-flows.md`, `PRINCIPLES.md`)
- The name-surface checks (documented enumeration vs the code's closed set;
  confusable flag pairs; names that follow the agent convention without being
  agents) — a separate, evidence-backed arc; a backlog entry is owed
- Word choice, voice, sentence length, `-ing`, passive constructions
- Widening `plan-format.md:79`'s imperative rule to more fields (this arc
  changes the example, not the rule)
- Shipping the harness in the plugin

## What Becomes Obsolete

Honestly thin, and that is a flag worth recording rather than papering over:
this arc is largely additive. The one genuine replacement is the brief
template's placeholder skeleton, whose descriptive slots are replaced (not
supplemented) by the worked example. Nothing else is removed.

What the arc closes is a QUESTION, not code: whether to adopt a controlled
writing standard for loom's documents. The measurement above settles it, and
the settlement should be recorded where a future session will meet it before
re-proposing STE.

## Open Questions

1. **The transfer gap — the load-bearing uncertainty.** Every measurement
   behind the four candidate rules was taken on SKILL text: instructions
   telling an agent what to do at a moment. A plan task is a different genre —
   a work order the agent executes and then reports on. Whether placement and
   mood transfer from the first genre to the second is UNTESTED, and it is
   precisely what Track B exists to find out. Track A does not depend on the
   answer (it fills holes rather than applying the rules).
2. Which model tier the Track B judges run at, and whether the implementer
   arm should run on the weak tier where the original placement effect was
   observed (3/3 vs 0–1/3 was measured on haiku). Resolve at plan time.
3. The adjacent backlog entry
   `2026-07-06-anti-copy-acceptance-greps-pass-paraphrase-copies` names
   `writing-plans/SKILL.md` in its start condition. This arc edits
   `plan-format.md`, not that SKILL.md, so it does not strictly fire. If plan
   work turns out to require a SKILL.md mirror edit, the condition fires and
   the entry should ride along; otherwise it stays OPEN.
4. Whether Track A's brief example should be a real past brief (concrete,
   already proven readable) or a synthetic one (no risk of a reader treating a
   historical decision as current guidance). Resolve at plan time.
