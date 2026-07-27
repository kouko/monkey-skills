# Brief: plan-stage fact grounding — a plan may not restate a fact it can point at

Brainstorming output — 2026-07-27. Origin: the user's observation that the
recent investing-toolkit arcs shipped clean but review kept surfacing defects
that traced back to the planning stage. Evidence base:
`docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md`.

Citation tiers are marked inline: **[1st]** = primary/official source read
directly; **[2nd]** = secondary reporting of a primary source; **[measured]** =
measured in this repo during this brainstorm.

## Problem

**The plan is a technical SSOT that nothing validates.**

Plans in this repo carry more than task decomposition: they carry *technical
assertions* — an accounting identity's term list, a count of fields, a measured
number quoted from a probe, an instruction to reuse a specific helper. Every
downstream station then judges conformance **to the plan**. So when a plan
states something false, the pipeline confirms the falsehood: the implementer
implements it faithfully, `spec-reviewer` grades the artifact against it and
returns PASS, and the defect typically survives to close-out, where whole-branch
review or a live dogfood catches it at the most expensive point in the pipeline.

*(Corrected at close-out: an earlier draft said "only" whole-branch review or a
live dogfood can catch it. That is the same overbroad claim the audit's §5 makes
and the audit's erratum now retracts — the audit's own §3.7 and §6 record a
per-task reviewer's spontaneous cross-read and an implementer's pre-work refusal
catching A-class defects earlier. The tendency is real and is what motivates this
change; the exclusivity was not.)*

In Boehm's (1979) terms **[2nd]** the pipeline performs **verification** ("are
we building the product right?" — artifact vs plan) at every station and
**validation** ("are we building the right product?" — is the plan itself
right?) at none. That is the whole diagnosis in one line, and it is why adding
another conformance check would not help.

Observed cost, from seven consecutive arcs (#605 / #610 / #611 / #612 / #616 /
#618 / #619 plus one in flight):

- #619: a plan PIN wrote a three-term equity identity while the 30/32-filer
  balance evidence it cited came from a **four-term** formula. 17 of 32
  verifiable filers (GE, Ford, GM, UnitedHealth, Citi, Morgan Stanley) would be
  false-flagged as not balancing.
- #619: the plan instructed the statement lane to reuse the top-line lane's
  selector. WMT lost revenue / net income / EPS; 17 companies lost equity; 4 of
  6 filers false-flagged in reconciliation. **1165 tests and 19 per-task review
  rounds were blind to it** — each task's tests were correct inside its own
  slice.
- In-flight arc: the plan states "15 fields" in three places where there are
  **14**; its RED clause still asserts a claim the tests had already retracted.

Naming the defect kinds: this brief uses the **INCOSE Guide for Writing
Requirements v4** characteristics — *correct / complete / consistent /
verifiable* — cited from INCOSE's free official summary sheet **[1st]**, with
ISO/IEC/IEEE 29148 noted as aligned but **not** cited (paywalled; we do not
cite text we have not read, and we do not cite unauthorized mirrors). Mapping:
the wrong formula is a **correct** failure, the missing dogfood task a
**complete** failure, 15-vs-14 fields a **consistent** failure, the undesigned
binding rule a **verifiable** failure.

Industry evidence that this is the expensive class: the requirements phase is
credited with 50–60% of injected defects and design 15–30% **[2nd]**; a
requirements defect corrects for ~10× more effort at system test than at
requirements time (Hughes Aircraft data, via McConnell) **[2nd]**. The
often-quoted 100× production multiplier is **not** cited here — its sourcing is
contested.

## Users

The `writing-plans` orchestrator and the three SDD subagents. **Which model each
runs on is set by SDD, not inherited** — see Current State Evidence (Boundary).
The consequence drives the whole design: `spec-reviewer` is structurally the
*weakest* reviewer in the triad, so anything it must do has to be written as a
checkable action, not a judgment.

Two standing constraints follow:

1. **Weak-tier readers.** Repo memory
   `doc-string-tests-pass-while-weak-readers-misread.md` records three shipped
   cases where prose passed its string-pinning tests and haiku cold-readers
   still misread it. Any term introduced here carries an inline operational
   definition — a name alone is not a contract.
2. **Prose that needs a judgment call dies; prose that names a checkable action
   survives** (auto-memory: weak-model caveats need verifiable action, not
   judgment). "Verify the plan's technical claims" is a judgment. "The plan
   cites `file:line`; open it and compare" is an action.

Job story: *When I am writing a plan that restates a number, a formula, or a
list I learned from a probe or an existing module, I want the plan to point at
that source instead of copying it, so that the copy cannot drift away from the
source while every test stays green.*

## Smallest End State

**A plan may not restate a verifiable technical fact it could point at.**

Five edits, ~19 added lines, no new agent, no new script, no new format element:

1. **Pointer-not-copy rule** (`skills/writing-plans/references/plan-format.md`) —
   any verifiable technical assertion in a plan (a number, a formula, a field
   list, a claim about existing behaviour) carries a `file:line` citation, or is
   explicitly marked an unverified assumption. A fact with no citable source
   means the source has to be produced first (a probe, a test) — that is a task,
   not a sentence.
2. **Conditional cross-read at a reviewer that already reads both** — one added
   instruction, worded as a trigger, not a mandate: *when the plan text this
   task is judged against carries a source citation, open the cited source and
   confirm it says what the plan says*. No citation present → the instruction is
   a no-op. **Which reviewer carries it is open** (see Open Questions 2).
3. **Reuse-adequacy declaration** (per-task block, `plan-format.md:42+`) — a task
   instructed to reuse an existing helper states in one line whether that
   helper's behaviour in the new lane matches its behaviour in the old one, and
   why any difference is acceptable.
4. **Obligation sweep** (`references/plan-document-reviewer-prompt.md`, check 8) —
   one added sentence: grep the brief for obligation sentences and list any not
   covered by a task.
5. **Closed list for post-PASS amendments** (`skills/writing-plans/SKILL.md:115`) —
   replace the author's self-judged "additive and schema-safe" skip note with an
   enumerated list of amendment kinds that may skip re-review; anything else
   re-reviews.

Coverage against the audit's planning-origin defects — **six** by its §1
scoreboard's A column (`A×1` + `A×2` + `A×3`), **seven** if §3.7's dossier is
read over the scoreboard, since that dossier enumerates three A-instances for
PR #619 where the scoreboard records two; that mismatch is the first item
BACKLOG's reconciliation entry leaves unresolved, so no total drawn from this
audit is trustworthy yet. Against those defects: items 1+2 prevent or
detect the wrong-formula and wrong-field-count class **when the plan cites a
source for the claim**; item 3 covers the illegal-reuse class; item 4 covers the
dropped-obligation class; item 5 covers the unreviewed-amendment class. Same
coverage as the rejected new-agent design at roughly 1/40 the added volume (see
Alternatives).

**What this does not cover — added at close-out, after whole-branch review held
this sentence to the branch's own standard.** Item 2 is by explicit design a
no-op when the plan states a fact with no citation, and nothing checks a plan for
item 1 compliance — the reviewer checks table stays at 16 and a guard test pins
that. So an **uncited** false fact passes untouched, which is both the cheaper
authoring path and the shape of the audit's own §3.8 instance ("15
fields" asserted three times where the code says 14). The **acceptance-criteria**
family (two further §3.8 instances) is likewise untouched. Those instances are
therefore not closed by this change — no total is stated for them, because which
of §3.8's items are A-class is one of the things the reconciliation has to
settle. The residual is enumerated in
`docs/loom/BACKLOG.md` under "Plan-stage fact grounding — what 0.39.0 does NOT
close". Stating the coverage claim unqualified would have reproduced the audit's
own P4 pattern (§4) inside the fix for P4's siblings.

**Prevention and detection are separable, and only one is model-dependent.**
Item 1's primary value is *preventive*: a fact that is never restated cannot
drift, on any model tier. Item 2 is *detective* and its reliability depends on
the reviewer's tier. This split is what makes item 1 worth shipping even if
item 2 later proves unreliable.

## Current State Evidence

- **Forward** — `skills/writing-plans/SKILL.md:103` dispatches
  `references/plan-document-reviewer-prompt.md` as a blocking evaluator; that
  prompt's checks 1–16 (`:33-48`) are **all formal** (field presence, DAG depth,
  RED/GREEN specificity, brief-item mapping, `Files touched` disjointness,
  mechanical-weight eligibility). None asks whether a stated fact is true. SDD
  then dispatches `agents/spec-reviewer.md`, whose contract is conformance of
  artifact to plan.
- **Reverse** — read `scripts/distribute.py` before assuming ownership: it
  distributes canonical `standards/` / `rubrics/` / `checklists/` **from**
  `domain-teams/skills/code-team/` **into** loom-code (`:8-11`, map at `:50-93`).
  `agents/` is **not** in that map, so `loom-code/agents/*.md` are loom-code-owned
  and item 2 lands here directly — no domain-teams round-trip, no
  `verify-drift.py` exposure.
- **Error** — there is no error path today. A faithful implementation of a false
  plan returns PASS from both per-task reviewers; the only observed catch
  (#619 T7) happened because the **code-quality-reviewer** *spontaneously* read
  the probe script against the plan's PIN — behaviour no contract requires.
- **Data** — the plan document; per-task fields defined at `plan-format.md:42+`.
  Note: **`PIN` is not a defined format element** — absent from both
  `plan-format.md` and `writing-plans/SKILL.md`, and used in **1 of 160** plans
  (`docs/loom/plans/2026-07-26-us-as-reported-statement-lane.md:312,349`). The
  rule therefore attaches to *any* stated fact, not to a PIN section.
- **Boundary — reviewer model tiers (load-bearing for item 2).** No agent file
  pins a `model:`; the tier comes from
  `skills/subagent-driven-development/SKILL.md:182`: *"Reviewers usually run at
  one tier below the implementer … **Exception**: when the implementer ran at the
  most-capable tier on an architectural task, the **code-quality-reviewer** also
  runs at most-capable."* The exception names code-quality-reviewer only.
  Derived tiers:

  | Task category | implementer | spec-reviewer | code-quality-reviewer |
  |---|---|---|---|
  | Architecture | opus | **sonnet** | opus |
  | Integration | sonnet | **haiku** | sonnet |
  | Mechanical | haiku | **haiku** | haiku |

  So `spec-reviewer` is structurally the weakest reviewer, while
  `code-quality-reviewer` is tier-protected exactly on the architecture tasks
  that carry technical facts — and that is the slot where the one observed
  spontaneous cross-read happened.
- **Boundary — sweep surface.** `plan-document-reviewer-prompt.md:37` shows
  check 5 RETIRED in place rather than renumbered, because other files cite check
  numbers literally; new checks append, never renumber (repo memory
  `retire-numbered-checks-dont-renumber.md`). `plan-document-reviewer` is
  referenced in **17 files** including `skills/writing-plans/README.{md,ja.md,zh-TW.md}`,
  `skills/subagent-driven-development/SKILL.md`, `skills/requesting-code-review/SKILL.md`,
  `skills/finishing-a-development-branch/SKILL.md`, `ROADMAP.md` and the
  writing-plans pressure-test prompts (repo memory
  `core-rule-removal-needs-plugin-wide-sweep.md`).

Evidence paths appendix:
- `loom-code/skills/writing-plans/SKILL.md`
- `loom-code/skills/writing-plans/references/plan-format.md`
- `loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md`
- `loom-code/skills/subagent-driven-development/SKILL.md`
- `loom-code/agents/spec-reviewer.md`, `loom-code/agents/code-quality-reviewer.md`
- `loom-code/scripts/distribute.py`
- `docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md`

## Decision

We will make the plan stop carrying copies of facts, and we will put the
cross-read — as a conditional trigger — in a reviewer that already reads both
the plan and the source. We will **not** build a `plan-critic` agent, will
**not** add a deterministic obligation-scanning script, and will **not** add a
mandatory new section to every brief.

The reasoning is deletion-first, and it is measured. A new plugin-level agent
costs ~400 lines (the four existing agent contracts are 343 / 400 / 409 / 537)
plus dispatch wiring, three-language READMEs, and edits across the 17-file
`plan-document-reviewer` reference surface — for the same coverage as ~19 lines
of rule text. Worse, it is purely additive: nothing becomes deletable. The
pointer rule is subtractive — #619's two PIN sections span 74 lines of restated
schema (`:312-385`) that become roughly 10 lines of pointers.

The design principle is already law in this repo, one station over: loom-memory's
SKILL.md `## SSOT — point, never copy` — *"a copy drifts; the pointer never
does."* This brief applies that same rule to the plan document itself.

**Model-generation guidance, and its scope.** Anthropic's Claude Opus 5
migration guidance **[1st]** says to *delete* verification scaffolding —
"Claude Opus 5 verifies its own work without being asked … removing them reduces
over-verification with no capability regression" — and reports that Opus 5
delegates to subagents *more* readily than 4.8, recommending an explicit cap.
Related context-engineering guidance summarised as "thin prompts, thick
artifacts, thin skills" **[2nd]** reports ~80% of Claude Code's system prompt
was removed for Opus 5 with no measurable eval loss.

Three consequences, and one non-consequence:

- The over-delegation finding is a **second independent reason** not to add a
  `plan-critic` agent, on top of the volume argument.
- "Thick artifacts, thin skills" **supports item 1**: it moves load out of skill
  prose and into the plan artifact.
- It argues for keeping the total prose addition small — hence ~19 lines, with
  rationale living in this brief and the audit rather than in skill text.
- **It does not license deleting item 2.** That guidance is Opus-5-specific; per
  the tier table above, `spec-reviewer` runs at sonnet or haiku, and the one
  observed spontaneous cross-read was the *code-quality-reviewer* at
  most-capable tier — a different agent at a different tier. Item 2 is also not
  the shape the guidance targets: it is a conditional trigger ("if a citation is
  present, open it"), not a blanket self-verification mandate.

**Named risk.** A `file:line` citation that no consumer ever opens is
*decorative provenance* — it makes a plan look grounded without any check that
it is. That is precisely the pathology named in
`docs/loom/audits/2026-07-20-loom-mechanism-weakness-audit.md` ("validates shape
… almost never validates provenance"). Shipping item 1 without a working item 2
would re-create that defect class in a new place. Item 1's preventive value
survives regardless; the risk is specifically that the *citation* becomes an
unchecked ornament.

Every term entering skill contract text carries an inline operational
definition.

## Alternatives Considered

Researched EN + JA (Axis 4 protocol); full source list in the audit's §research.

| Alternative | Who ships it | Why rejected |
|---|---|---|
| **New `plan-critic` agent** (a third family critic, after `completeness-critic` and `design-critic`) | The 2026 spec-driven-development pattern of a critique layer before code **[2nd]** | ~40× the added volume for identical coverage; purely additive; would have had to first invent `PIN` as a format element (n=1 usage); and Opus 5 already over-delegates **[1st]** |
| **Add fact checks as rows 17–18 of the plan-document-reviewer prompt** | — | Complects formal checking with semantic checking in one evaluator and one verdict — they could no longer be reasoned about, tested, or changed independently (Hickey, *Simple Made Easy*) |
| **Requirements Traceability Matrix** — enumerate every brief obligation, require a mapped task | Standard RE practice; the named form of our "candidate 2" | Industry experience is negative on cost/benefit ("hardly sustainable"; maintenance exceeds value — itemis; matrices grow gaps that themselves lower quality — Jama) **[2nd]**. Structurally it verifies *coverage*, not *correctness*: it addresses 1 of our 7 observed defects |
| **Deterministic obligation-scanning script** | Analogue: our own `check_scenario_coverage.py` | **[measured]** an obligation pattern fires 0.28×/brief over 173 briefs across 6 repos; only 20% of briefs produce any signal; ground truth is 1 hit / 1 miss (n=2, confirmed against the full 1.7 GB transcript corpus). The join is also undecidable — prose vs task list — so it could only advise, never block, unlike `check_scenario_coverage.py` which compares two structured key sets. The academic form ("Requirements Smells", arXiv 1611.08847) has the same known ceiling **[2nd]** |
| **Bold-emphasis as the obligation discriminator** | — | **[measured]** dead end: 14–64 `**…**` spans per brief, one to two orders of magnitude noisier than the temporal-marker pattern |
| **Fagan inspection** | Classic formal review | Its value is the role structure (moderator / reader / author / formal rework); loom has none of those. Borrowing the name would manufacture the impression of a control we do not have |

## What Becomes Obsolete

- The practice of restating schemas and formulas inside plans — #619's two PIN
  sections (74 lines) shrink to pointers.
- The `PIN` heading convention itself (1 of 160 plans) is not promoted to a
  format element; it stays an ad-hoc heading with no governance attached.
- A share of post-PASS amendment churn: two of #619's four post-PASS edits were
  rewording PIN prose. Pointers do not need rewording, which independently
  shrinks the problem item 5 addresses.

## Open Questions

1. **How is success measured?** Proposed: Phase Containment Effectiveness — the
   share of planning-origin defects caught at plan review rather than at
   close-out (ODC / PCE, IBM 1992 & automotive SPICE practice) **[2nd]**.
   Cheapest viable form: classify only defects found at close-out (rare), not
   every defect. Without this the change ships unfalsifiable.
2. **Which reviewer carries item 2 — `spec-reviewer`, `code-quality-reviewer`,
   or both?** Arguments both ways: spec-reviewer is the one judging the artifact
   *against the plan text*, but runs at the weakest tier; code-quality-reviewer
   is tier-protected on architecture tasks (`SKILL.md:182` exception) and is
   where the one observed spontaneous cross-read happened. Unmeasured.
3. **Does the conditional trigger actually fire at sonnet/haiku?** This is the
   change's own verification task. Repo memory
   (`cold-read-and-adversarial-review-catch-different-failures.md`) says a
   gate-mechanism change needs **both** a fresh-context cold read and an
   adversarial round — one does not substitute for the other.
4. **Reversal condition.** If the dogfood shows the cross-read produces false
   alarms at a rate that would train reviewers to ignore it, fall back to "cite
   the source, do not auto-adjudicate", ship item 1 alone for its preventive
   value, and say plainly that the detective layer failed — rather than shipping
   a gate that can self-certify.

## Out of Scope

- A `plan-critic` agent (dropped; revisit only with evidence that items 1–3 leak).
- Any deterministic script for briefs or plans.
- A new mandatory brief section.
- **Changing the reviewer tier assignment at
  `subagent-driven-development/SKILL.md:182`.** That `spec-reviewer` is
  structurally weakest is defensible for conformance checking and questionable
  for fact-checking, but re-tiering is a separate change with its own blast
  radius.
- Renaming `PIN`, or any renaming inside loom-code (the 17-file surface makes
  renames expensive; repo memory `big-rename-operative-frozen-sweep.md`).
- Rewriting the audit document's vocabulary into INCOSE/ODC terms — separate,
  cheaper change.
- Porting any of this to Codex (`.codex/` shims) — not evaluated here.
