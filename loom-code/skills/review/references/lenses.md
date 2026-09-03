# Lenses — what each dimension means, and what it is scored against

One reviewer contract, six lenses. This file is the dimension definition
for all of them; `agents/reviewer.md` names the dimensions and points here
for what each one is asking. General knowledge of Clean Code, SOLID, DRY,
TDD, F.I.R.S.T and OWASP is assumed — the citations below say which source
settles a disagreement, not what to read first.

## Severity and verdict

Severity is decided by consequence, never by where a finding lands or how
literally wrong the text is:

- **fatal** — ships a defect: a wrong result, an exploitable hole, a lost
  guarantee.
- **important** — a reader following the text would act wrongly, or a
  fact the checker or CI relies on is wrong (a path, a command, a number a
  rule reads back).
- **nit** — everything else: wording, terminology, units, the same fact
  stated two ways, readability — a reader following it still does the
  right thing, and nothing mechanical reads it. A sentence can be
  literally incorrect and still a nit, if no reader or machine acts on the
  wrong part of it.
- Any fatal → `NEEDS_REVISION`. Two or more important → `NEEDS_REVISION`.
  One important → `PASS_WITH_NOTES`. Only nits, or nothing →`PASS`.
- **Nits never open a round.** They are recorded in `findings` like any
  other finding, but never become an `open_findings` entry and never block
  a verdict on their own. `ship` folds every open nit into one commit
  before push; the reader who raised each one confirms the fix in a single
  line, and that confirmation is not a new round.
- A finding with no anchor is opaque and flips the whole verdict to
  `NEEDS_REVISION` however small it is: "naming is off somewhere" cannot be
  fixed by anyone.
- A dimension whose pass rests on evidence you did not run yourself scores
  `PASS_WITH_NOTES`, naming what was not independently checked. Never
  "could not see it, so it is fine".
- A conformance dimension with no document to conform to scores `N/A` with
  the reason. `N/A` is not a pass and is never given for convenience.

## Code — eleven dimensions

| Dimension | What it asks | Settled by |
|---|---|---|
| security | Injection, authn/authz, secrets, unsafe deserialization, encoding confusion in every changed path | OWASP ASVS; 徳丸本 Ch.6 for character-encoding attacks |
| architecture | Does the shape the change produces hold — responsibilities, dependency direction, boundaries | SOLID (Martin) |
| correctness | Does it do what it claims, at the boundaries as well as the middle; is there RED→GREEN evidence in the history | the tests, run |
| naming | Names say what the thing is; functions stay short — 20 lines soft, 50 hard, 100 is a finding on its own | Clean Code Ch.2–3 (Martin) |
| tests | Every shipped behaviour has a test that failed first; F.I.R.S.T holds for the suite, not just the new file. Read `probes[]` too: each entry's `command` and `artifact`, not its `result` — a command that exits 0 without running the suite or the abuse case (a shell builtin, or one that never names its artifact) is a finding, not evidence | Beck, *Test-Driven Development* (2002) |
| refactoring | Duplication and smells; Rule of Three — three sites doing the same thing is an extraction | Fowler, *Refactoring*; the Pragmatic Programmer's DRY |
| cross-task-coherence | Only a whole-delta reviewer can see this: abstractions that disagree between tasks, logic duplicated because each task saw one slice, a task that quietly did more than its title | — |
| external-surface-grounding | Every call into a surface the author does not own — HTTP API, SDK package, MCP tool, CLI flag, a sibling team's contract — carries a grounding citation. Missing on the first four is fatal; missing on a sibling contract is important; two tasks calling the same surface with conflicting shapes is important | — |
| principles-conformance | Does the change violate a falsifiable clause of the repo's `PRINCIPLES.md`? Scored only when that file exists, else `N/A` | the consumer's own `PRINCIPLES.md` |
| deliberate-simplification | A shortcut taken on purpose is annotated with its ceiling and its upgrade path; an annotation saying "later" or "someday" names no ceiling and is a finding | — |
| deletion-first | Every new abstraction, flag, config or extension point justifies itself with two concrete users now, an explicit request, or a visible motivation. A finding must name the smaller shape that does the same job — no finding without a concrete alternative | — |

## Docs — five dimensions

| Dimension | What fires it |
|---|---|
| omission | An obligation or referent the text needs and lacks: a step the reader cannot execute, a term used but never defined, a promised section absent, a required diagram or comparison table missing (or declared not-applicable for a reason the text's own content contradicts) |
| ambiguity | An absolute — "only", "never", "zero" — with no support; a sentence with two live readings that fork what the executor does |
| inconsistency | Two passages contradicting, including changed against unchanged: the delta says X and an untouched paragraph still says not-X |
| incorrect-fact | A citation that does not support its claim — open the source and read the cited span before scoring — or a stated number or path that is wrong against the artifact it describes |
| missing-population | A measured number with no denominator or scope: "0% false positives" without saying over what |

Read the whole artifact, not the delta. The delta says where to look
hardest; it never bounds the review.

## Conformance and question lenses

| Dimension | What it asks |
|---|---|
| spec-conformance | Does the change do what the spec's `REQ-<n>` lines require, and only that? Every requirement is either satisfied, explicitly out of scope, or a finding. Unbuilt requirements and unrequired behaviour are both defects |
| design-conformance | Against `DESIGN.md` and the spec's UI flows: does every screen, state and transition the change touches exist in the design, and does a user reach it and get back out? `N/A` with the reason when there is no `DESIGN.md` |
| principles-conformance | As in the code lens, applied to any artifact type |
| user-judgment-leak | Fires when the change asks the user something they cannot answer. A question is legitimate only if it is *what do you want*, *is this the behaviour you will see*, *is it done*, or the consequence form of a hard-to-reverse choice ("from then on it only runs on ___, ___ per month"). A question about spec quality, how tasks were split, or how a review came out is a leak, and a leak is `NEEDS_REVISION`. It fires the other way round too, on a decision that was **not** put to the user: a `Design decision` that introduces a paid service, an account the user must hold, or the user's data leaving their machine, with no `user-decided` mark, is `NEEDS_REVISION`. Those are one-way-door classes (b) and (e) — the user pays the bill or loses the data — so an `agent-decided` mark settles it only when the option taken carries zero obligation and is reversible |

## Skill lens

A `SKILL.md` or an agent contract is prose that an agent executes, so it is
scored on the five docs dimensions plus `user-judgment-leak`, with two
sharpenings: a step whose input the reader must guess is an omission, and a
paragraph used as a rule without a `<!-- gate: <id> -->` comment is an
omission too — an unregistered rule is a mechanism nobody recomputes.
