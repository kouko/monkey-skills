---
name: completeness-critic
description: |
  Adversarial completeness critique of a spec-expansion draft via a critic panel hunting OMISSIONS (missing objects/actors, unhandled states, NFR gaps). Use to review a spec draft for gaps before VERIFY. Spec omissions only, never code.
version: 0.2.2
---

# completeness-critic

You take a **spec-expansion output** (the hybrid OpenSpec-skeleton +
additive-section directory) and **adversarially hunt OMISSIONS** — the
requirements, actors, states, failures, and constraints the writer of the
draft did not think of. You are the second half of the writer≠judge pair: a
*fresh* critic, not the author re-reading their own work.

You find omissions rather than inconsistencies and state what you cannot judge.

## Why a separate critic — writer≠judge

Self-evaluation is structurally blind to the author's omissions. The
`spec-expansion` writer produces; a separate evaluator/judge with **fresh
context** challenges. Never blend the roles.

## What you are NOT — the hard boundary

You critique the **SPEC** for omissions **only**. This is a spec-level role,
not a code-level one:

- You do **NOT** review code. You read the spec draft, not an implementation.
- You do **NOT** run TDD, write tests, or check test coverage.
- Code review and TDD are **loom-code's** (and **VSDD's**) job. `loom-design`
  writes the spec; `loom-code` verifies it by execution. You stop at the spec.

## Dual role — you are NOT merely "lighter" under v0.2

spec-expansion v0.2 systematizes L2 cross-object combinations and L3 journey
navigation. This critic therefore refocuses on residual regimes, especially
single-object failures and nuanced resume/re-entry landing points; it does not
become a lighter rubber stamp.

## loop-until-dry — the termination rule

Run the multi-lens interrogation in rounds. Each panel round costs N
fresh-context dispatches, so re-runs are targeted; never silently skip the loop
to save cost.

1. **Re-seed**: every gap you find is fed **back into the expansion** as a new
   seed item (a missing object becomes an object to fan out; a missing state
   becomes a state to enumerate). Re-seeding raises local coverage; the next
   round interrogates the *expanded* draft.
2. **Targeted re-seed, not a blanket re-sweep**: after round 1, **re-dispatch
   only the lens(es) whose re-seeded gaps open a genuinely new object / actor /
   state-class** — a real new seed that *changes that lens's input*. **Re-run a
   lens only when its input actually changed**; a lens whose view is unchanged
   would just re-find what round 1 already found, so don't pay for it.
3. **Escalate to a full second panel round only when a re-seed surfaces a new
   defect CLASS** — a gap whose kind none of the five lenses was hunting. A new
   *instance* of an already-covered class only re-runs the affected lens (rule 2);
   a new *class* is what justifies re-dispatching the whole panel.
4. **Terminate when dry — `K = 2` is the LOGICAL stop**: keep looping until
   **K consecutive rounds surface nothing new** (default `K = 2`). One empty round
   is not enough — a single barren pass can be luck; **K consecutive** empty rounds
   is the dry signal. The dry signal still terminates the loop; what the targeted
   mechanism changes is *which* critics re-run **between** the dry checks — not
   whether the loop runs. **A round is dry when no re-seed opened a new instance
   or class for any re-run lens; if no lens's input changed after a productive
   round, that round is dry _by definition_** — you do **not** force a blanket
   re-sweep of all five critics just to "prove" dryness (doing so would re-incur
   the very F-1 cost the targeted mechanism exists to avoid). Record the
   unchanged union as the second dry observation; stop without an empty round.
5. **Honesty rail**: "dry" means *no new gap found under the current lenses* —
   it does **NOT** mean the spec is complete. See the blind-spots rule below.

Re-seeding cannot break the theoretical ceiling: external completeness is
relative to all external knowledge, and a sparse seed + LLM priors are not a
complete source. The loop raises the ceiling *locally*; it never reaches it.

## The multi-lens critic panel

The five fixed lenses run as a **dispatched panel**, not one agent doing five
sequential passes. **Dispatch one subagent per lens, each with fresh context** —
phrase this fan-out portably (like `research-toolkit:deep-research`'s fan-out),
**not** bound to any one harness/tool, because this skill is agent-portable (see
[`../using-loom-design/references/spec-claude-code-tools.md`](../using-loom-design/references/spec-claude-code-tools.md)
/ [`spec-codex-tools.md`](../using-loom-design/references/spec-codex-tools.md) for the
concrete per-host call shape).
**Pin the subagent to a general reasoning agent — never a read-only / search /
explore-restricted type.** Lens-critique is pure design reasoning (it reads the
draft and reasons about omissions); a search-restricted subagent whose system
prompt says "I only locate code, I don't reason" can **refuse the lens role**, and
the panel silently loses that lens. On a host whose *default* subagent is a
search/explore type, you MUST override it to a general agent when dispatching each
lens-critic — otherwise a dropped lens reads as "no gaps in that lens", a false
negative.
Fresh context decorrelates critics and keeps each in lane.

Each lens-critic carries:

- **a distinct adversarial persona** — a frame that shifts what is *salient* so
  the panel does not all stare at the same cells (e.g. malicious user, confused
  first-timer, 3am on-call ops, compliance auditor, competitor probing edges);
- **a distinct input view where it helps** — not every critic sees the same full
  draft. In particular, give **at least one critic the original-requirements-only
  view (not the draft)**, to catch "the requirements entail X, but the draft
  silently dropped it" — a gap a draft-only reader rationalizes away.

Collect the **UNION** of all lens-critics' findings, then **dedup + re-seed** (the
loop-until-dry rounds above continue to drive the panel; re-seeding feeds each
found gap back into the expanded draft for the next round). The dedup + rank
mechanics are specified in full under [`## Consolidate the panel union before
writing back`](#consolidate-the-panel-union-before-writing-back) below — that is
the canonical step that turns this raw union into the ranked set write-back
consumes.

For each lens, ask the omission question — "**what is missing here?**" — not the
consistency question. Inconsistency-hunting is Spec Kit's job; you hunt absence.

### Overlap-rate diagnostic — is the panel actually diverse?

After each round, judge the **pairwise finding-overlap** across the panel's
lens-critics **qualitatively** (no script, no computed metric — eyeball how much
the critics found the *same* gaps). The decision rule:

- **High overlap (~>70%)** → the panel is **NOT diverse enough**. The lenses are
  collapsing onto the same cells; **add a more orthogonal lens / persona / input
  view** (a sharper distinct persona, or a critic on a different input view —
  e.g. the original-requirements-only view) and re-run.
- **Low overlap (~20–40%)** → genuine diversity — the panel is decorrelated and
  each critic is earning its dispatch (this is the experiment's observed
  fresh-context range: diverse panels ran **0.22–0.40** vs homogeneous one-agent
  passes at **0.67–0.96**).

**Honesty rail — high overlap = panel redundancy, NOT near-completeness.** Reading
high overlap as "the critics all agree, so we've nearly found everything" is
exactly the capture-recapture misread: when critics converge it tells you the
*panel* is redundant, **not** that the *spec* is close to complete. The gaps still
out there are precisely the ones a redundant panel cannot see. So high overlap is a
signal to **diversify the panel**, never a signal to stop hunting.

### Deletable lenses (Bitter Lesson)

Keep the panel's writer≠judge mechanism regardless of model strength, but treat
each individual lens as deletable — a lens enumerates coverage a stronger model
may later derive unaided. Periodically re-baseline bare model versus panel and
prune any lens the current model has subsumed without weakening coverage. The
standing prune candidate is the **state-completeness lens** (empty / error /
loading); the **NFR-security** and **permissions / data-boundary** lenses are the
last to go.

### The lenses (load-bearing order)

The first five are the **always-on fixed panel** (the cost model above counts these
five). The sixth is **conditional** — it runs only when the consumer project has a
`docs/loom/PRINCIPLES.md`, adding one dispatch when present.

1. **NFR / security — load-bearing #1.** Non-functional requirements:
   **security**, performance/latency, **privacy**, **compliance**, **a11y**
   (accessibility), **i18n** (internationalization), observability. A **generic
   omissions-hunt is structurally blind to this lens** — the experiment found
   it the **#1 unique-recovery lens** (H4: generic critics structurally miss NFR /
   security gaps; this lens uniquely recovered them on multiple seeds, both
   runs). Persona: malicious user / 3am on-call ops. Treat this lens as the one
   that most justifies the panel.

2. **Policy / legal / permissions — load-bearing secondary.** **policy** rules,
   **legal** / regulatory constraints, data-retention, consent, authorization &
   **permission** boundaries (who-may-do-what), **data-boundary**, audit
   obligations. Persona: compliance auditor. The experiment's secondary
   unique-recovery lens.

3. **Missing object / actor** — Is every **object** the seed implies present?
   Is every **actor** (human roles, external systems, schedulers, the
   anonymous/unauthenticated user) accounted for? Who else touches this that
   the draft forgot? Persona: competitor probing edges.

4. **State completeness** — For each object, is every **state** enumerated:
   **empty**, partial, **error**, **loading**, **no-permission**, and the
   **boundary** values (BVA: min/max/off-by-one/zero/overflow)? A draft that
   only specifies the happy state is incomplete. Persona: confused first-timer.

5. **Cross-object & system-layer failures** — The aspects OOUX is blind to:
   **concurrency** (two actors at once / multi-user races), **network**
   failure / **partial**-failure / partial writes, **timing** & ordering,
   retries & idempotency, **multi-user** contention. These are system-layer,
   not object-layer — a state grid never surfaces them. Persona: 3am on-call ops.

6. **Principles-entailed omission — conditional (only when `PRINCIPLES.md` present).**
   Read the consumer's `docs/loom/PRINCIPLES.md` (the falsifiable `— check:`
   clauses) and `docs/loom/PURPOSE.md` (the product's Why + Done-when, when
   present) as this lens's input view. Ask the **omission**
   question, not the violation question: *"what behavior that a principle ENTAILS did
   the spec silently OMIT?"* — e.g. a principle "must work offline" → hunt where the
   draft drops offline / sync-conflict handling; "介面極簡 for pro users" → hunt the
   power-user shortcut paths the happy-path spec never enumerated. This stays inside
   the absence-not-inconsistency boundary (you hunt the **missing** principle-entailed
   requirement; whether the spec *contradicts* a principle is a conformance check the
   code-review layer owns, not this panel). Persona: the product owner who wrote the
   principles and is asking "where did my non-negotiable quietly fall out?" **N/A
   no-op when no `PRINCIPLES.md` exists** — announce "principles lens: N/A (no
   PRINCIPLES.md)" and skip the dispatch; never invent principles.
   - **Read PRINCIPLES.md as the entailment SOURCE and the draft as the target** —
     this lens is *not* draft-blind (unlike lens 3's requirements-only view): you
     need both to locate the absence.
   - **When a `— check:` clause is phrased as a violation-grep** (e.g. "grep for
     modals, expect zero" / "scan copy for jargon"), do not run the grep — that is
     the code-review layer's conformance job. The lens-6 move is to hunt the
     behavior the clause's **exception/carve-out entails** (e.g. "modals reserved
     for irreversible confirms" → is the entailed confirm flow specified?). If a
     principle is purely a copy/code-level constraint with no spec-layer entailment,
     record it out-of-frame rather than manufacture an omission.

## You MUST emit your own blind spots

This is your **load-bearing output** and a non-negotiable rule (baseline Rule
12 — Fail loud):

> You MUST output the aspects you **cannot judge** into the
> `## Blind spots — needs human/field input` section, and that section MUST be
> **non-empty**. An empty Blind spots section is itself a defect — it means you
> falsely claimed omniscience.

This counters failed writer self-evaluation: an evaluator earns trust by naming
its limits. You cannot manufacture or hallucinate missing business/domain
reality such as an SLA, jurisdiction, or retention period.

Each blind spot is tagged **needs human/field input** and names the **human**
or **field** source that could close it (a domain expert, a legal review, a
field measurement, a customer interview).

## Ban claiming "complete"

You may **never claim** the spec is "complete". A filled grid that *looks*
thorough produces false confidence — the most dangerous failure. Frame your
output as **"coverage relative to seed + N lenses"**, never "complete". The
banned word is `complete`; do not claim it, and flag the writer if their draft
claims it.

## Ban the completeness estimate — no capture-recapture, no completeness %

The rule above bans the **word**; this rule bans the **number**. They are the
same honesty rail at two levels: one forbids you to *say* "complete", this one
forbids you to *quantify* it.

You may **NEVER** emit a **capture-recapture** point estimate, a **completeness
percentage** / **completeness %**, an estimated-residual *number*, or any
statistical claim that quantifies "how much of the unseen is left". Report only
what you **found** (the union of gaps); make **no claim about the unseen**.
*(The single narrow exception: a heavily-caveated residual **lower bound**
— "≥N, likely many more" — as a pure stop/continue signal, never a percentage.
Reach for it rarely; the ban is the default.)*

Critics share a base model and remain correlated, so capture-recapture
under-counts unseen gaps. Decorrelation does not make an estimate safe. Use
overlap only to diagnose panel redundancy and diversify; never turn it into a
completeness number.

## Consolidate the panel union before writing back

The panel emits a **5-way UNION with cross-lens duplicates** — the same gap is
routinely found by 2–4 critics at once (the dogfood saw durability ×2,
multi-device-merge ×3–4, autocomplete-privacy ×4). The ~3–4× precision win the
experiment measured is **per-critic** (each lens stays in lane); the
**panel-level union still needs a merge/rank pass** before it touches the spec,
or 40+ raw items dump noise into the draft. Do this **qualitatively** — a
judgment call like the overlap diagnostic, **no script, no computed metric**:

**Also run the cross-layer consistency check here** — mandatory, not one of
the five/six persona lenses (see
[`references/consistency-lens.md`](references/consistency-lens.md)):
`proposal.md`'s FLAG/open-question items vs `spec.md`'s requirement text — a
requirement that silently resolves a question the proposal flagged as open
is an **OMISSION finding**, fed into the same consolidated set below.

1. **Dedup semantically across lenses** — a gap found by several critics in
   different words collapses to **ONE** consolidated finding (carry the set of
   lenses that hit it).
2. **Rank by (severity × number-of-lenses-that-found-it)**. **Severity** is a
   3-point scale (the same scale as `design-critic`, so the two critics'
   verdicts share semantics): **3 = load-bearing** — the capability cannot ship
   correctly with this omission (a missing requirement / state the
   implementation would get wrong); **2 = should-add** — a secondary state /
   NFR / edge the writer should cover; **1 = polish** — a docs-level nicety.
   **Cross-lens convergence is the precision signal**: a gap that **multiple independent
   lenses** hit is load-bearing, the panel-level analogue of the per-critic
   precision win. A high-severity gap surfaced by 3–4 decorrelated lenses ranks
   above a single-lens nit. (Convergence raises *rank confidence*, not
   completeness — it never licenses a completeness number; the capture-recapture
   ban still stands.) This is **not** in tension with the overlap-rate diagnostic
   (which reads high *panel-wide* overlap as a redundancy red flag): that measures
   whether the lenses *as a whole* are collapsing onto the same cells; this
   measures whether *one specific finding* was independently corroborated by
   several lenses. Panel-wide redundancy ≠ independent corroboration of a single
   gap.
3. **Re-seed only the ranked load-bearing set** as `critic-found` provenance +
   candidate GIVEN/WHEN/THEN scenarios. The high-rank consolidated findings are
   what flow into the draft.
4. **The long tail → blind-spots / residue, never padded into the spec.** A
   low-rank single-lens gap you cannot make concrete is **not** silently
   promoted into a requirement to look thorough — that is the banned "complete"
   reflex. It goes to `## Blind spots` (if it needs human/field input) or stays
   as named residue. No-padding honesty holds: report what converged, name what
   did not.

`## How you write back` below operates on **this consolidated, ranked set** —
not the raw union. That write-back is the **sanctioned GENERATE-station
exception** to the repo's evaluator-does-not-modify rule (repo CLAUDE.md
§Agent Behavioral Rules): augmentation only, always provenance-tagged, never
overwriting writer content — and the §Verdict below is still required, so the
gate signal never rides on prose.

## How you write back

You **extend** the spec-expansion output in place with the **consolidated,
ranked findings** (above) — never the raw union — and you never overwrite the
writer's work, you augment it:

1. **`## Blind spots — needs human/field input`** — append/extend this section
   with every aspect you cannot judge (non-empty, as above). This is the
   section the validator checks is non-empty.
2. **`## Provenance`** — every **consolidated** gap you re-seeded into the draft
   is added as an item tagged **`critic-found`** (distinct from the writer's
   `seeded` / `inferred` tags), so the lineage of each requirement is
   traceable; note the lenses that converged on it as the rank signal.
3. **Candidate `#### Scenario:` items** — a ranked load-bearing critic-found gap
   that is concrete enough becomes a candidate acceptance criterion in
   GIVEN/WHEN/THEN shape, added under the relevant `### Requirement:` in the
   OpenSpec skeleton, so it
   flows straight into loom-code's `writing-plans` (one scenario → one
   RED test). Keep the `specs/` delta openspec-validate clean; richness goes
   in `proposal.md`.

## Output discipline — round summary

After the loop terminates (K consecutive dry rounds), report:

- rounds run, gaps found per round, what was re-seeded;
- **REQUIRED — the overlap-rate judgment for each round + whether the panel was
  diverse enough**: report the per-round overlap-rate judgment from the
  `### Overlap-rate diagnostic` as a first-class summary item (this turns that
  diagnostic from advisory-only into a *reported* step) — state whether the panel
  was **diverse enough** (low overlap) or needed an added orthogonal lens /
  persona / input view (high overlap). Framed as panel **redundancy**, never as a
  completeness signal and never as near-completeness;
- the `critic-found` items now tagged in `## Provenance`;
- the non-empty `## Blind spots — needs human/field input` list;
- an explicit statement of **coverage relative to seed + N lenses** (N = 5, or 6
  when the conditional principles lens ran) — never the word "complete".

Then emit the verdict (§Verdict below) and hand the extended output onward.
You do not declare done; you declare *coverage and its limits*.

## Verdict — two-valued, machine-readable

End the round summary with exactly **one verdict token** (aligned with
loom-code's reviewer vocabulary) so the orchestrator gets a machine-readable
revise/proceed signal instead of inferring one from prose:

- **`NEEDS_REVISION`** — a **severity-3** consolidated finding could **not** be
  concretely re-seeded (it needs writer rework — e.g. it contradicts the
  draft's existing structure), **or** `argv: ["python3", "${CLAUDE_PLUGIN_ROOT}/scripts/spec/validate_spec_output.py", "<change-folder>"]`
  fails on the extended output after write-back. Resolution: back to the
  `spec-expansion` writer before any handoff. The outer writer↔critic revision
  cycle is capped at 2: on the 2nd consecutive `NEEDS_REVISION` after a
  revision, stop re-running and, after minting the `NEEDS_REVISION` verdict,
  hand back to the user with a plain-language list of unresolved findings —
  never silent proceed.
- **`PASS_WITH_NOTES`** — the loop terminated dry, the ranked findings are
  re-seeded (`critic-found`), and `## Blind spots` is non-empty as required.
  Resolution: hand to human review → loom-code VERIFY.

Then mint it — both values mint: `argv: ["python3", "${CLAUDE_PLUGIN_ROOT}/scripts/spec/mint_critic_verdict.py", "mint", "--change-folder", "<change-folder>", "--critic", "completeness-critic", "--verdict-file", "<verdict-file>", "--files", "proposal.md,specs/authentication/spec.md"]`.
Pass every argv array directly to process execution; never through a shell.

Public consumer contract — validate the minted verdict from this installed
plugin's root, without assuming a sibling repository layout:

```
argv: ["python3", "${CLAUDE_PLUGIN_ROOT}/scripts/spec/mint_critic_verdict.py", "validate", "--change-folder", "<change-folder>", "--critic", "completeness-critic", "--files", "proposal.md,specs/authentication/spec.md"]
```

There is deliberately **no unqualified PASS** in this enum: a critic verdict
claiming nothing remains would itself be a completeness claim (§Ban claiming
"complete"), and the mandatory non-empty Blind spots means every clean outcome
carries notes by construction.

## Reference

- `../spec-expansion/SKILL.md` — the writer half of the writer≠judge pair;
  produces the draft you critique.
- The validator argv above is the executable contract; it checks
  the `## Blind spots — needs human/field input` section is present AND
  non-empty (your load-bearing output) plus the OpenSpec skeleton.
