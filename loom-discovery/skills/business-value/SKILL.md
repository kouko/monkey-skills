---
name: business-value
description: Adversarial worth-it check before betting real time on a product-shaped idea. Use for worth it? / should I build this / weighing ideas against one time budget. Market sizing → domain-teams:planning-team. 值不值得做 / ビジネスバリュー / 時間の使い方.
version: 0.1.0
---

# business-value

The **adversarial worth-it check**. The job: before you sink real time into a
product-shaped idea, decide honestly whether **this** idea deserves **your** time
budget — over everything else that same time could go to. It produces a short,
git-diffable `business-value.md` so the reasoning survives for the re-reader six
months later.

## Register — Shape Up betting, NOT Cagan viability

This is a **betting** call in the Shape Up sense (Basecamp's method: bet a
**fixed time-box** on an idea — *"is this worth my time budget?"*) — a personal
appetite decision, bounded and reversible. It is explicitly **NOT** Cagan-style
business viability (SVPG's market-level assessment): no market sizing, no
revenue model, no GTM. Those are a different profession (see the delegation
boundary below).
Frame every question as *how I spend a fixed time budget*, never *how big the
market is*.

## Executor model — who does what

**You (the agent running this skill) are the executor.** You supply the LLM
reasoning — running the interrogation, weighing the answers, drafting the
recommendation and pushing back on hand-waving. There is no external runtime and
no API key; the method rides the host agent you are already in. The one artifact
is `business-value.md`, authored from `assets/business-value-template.md`.

## When it fires — decidable trigger enumeration

This step is **optional**. A weak-model session must be able to decide fire-vs-skip
**without judgment**, so the conditions are enumerated, not vibes.

**Fire when ANY of:**

- **(a)** the outcome is **for others** — it will be **published** or **maintained**
  (someone other than you-right-now depends on it; a **team-internal tool counts
  as for-others**);
- **(b)** **multiple ideas compete** for the **same time budget** (you can only
  build one now);
- **(c)** it means a **meaningful resource spend** (non-trivial hours, money, or
  ongoing upkeep).

**Skip silently when** (negative-guard style — emit **no** noise, do not announce
the skip):

- it is a **personal tool** for yourself only (throwaway, private, unpublished); OR
- a **GO is already decided** by the user (they have committed; do not re-litigate
  — an **incremental feature on an already-shipped product is a decided GO**,
  fire only if the increment itself meets (b) or (c)).

When skipped, **proceeding downstream is the implicit GO** — do **not** write an
empty `business-value.md`. A skipped check leaves no artifact; the absence *is*
the signal, and a blank file would be a false audit record. ("Silently" bounds
the workflow — no artifact, no interrogation; a one-line conversational note
that you are proceeding is fine, going mute is not the goal.)

## Re-entrant — a checkpoint, not a one-way gate

This check is **re-entrant**. It may run on **rough evidence** before
`user-insights` has done its research, and be **revisited** after research
deepens (a `NEEDS-MORE-RESEARCH` verdict is the explicit invitation to come back).
It is a **checkpoint** you may pass through more than once — **not a one-way gate**
that locks a decision forever. Re-running it and overwriting `business-value.md`
with a firmer verdict is the intended flow, not a violation.

## The interrogation — one question at a time

Grill the **user** with **value-judgment questions only**, **one question at a
time** (never a wall of questions — ask, hear the answer, let it steer the next
one). Cover three axes; push back on any answer that is an aspiration rather than
a checkable reason:

1. **Why now?** — why is this the right moment, versus later or never? What
   changes if you wait?
2. **Why me?** — why you specifically, versus someone else / an existing tool /
   not at all? What is the unfair advantage or the itch only you feel?
3. **Opportunity cost** — what does this time **NOT** go to? Name the concrete
   thing you are giving up. If nothing real is displaced, the appetite claim is
   hollow.

Only **value-judgment** questions belong here. Feasibility, need-mapping, and how
to build it are **out of jurisdiction** (see boundaries below).

## Jurisdiction boundary — delegate, never inline

**Market sizing / GTM / revenue modeling → delegate to
`domain-teams:planning-team`.** Follow the cross-plugin delegation contract:
**pass paths + a structured seed context**, hand the target full authority to run
its own analysis and gates, and let its verdict flow back — **never inline** that
analysis into `business-value.md`. If the worth-it call genuinely turns on market
economics, that is planning-team's turf; record the hand-off and its returned
verdict, do not reproduce the reasoning here.

**Need-mapping is `user-insights`' profession, not yours.** This skill decides
*worth-it*; it does **not** map user needs, job stories, or opportunity spaces.
When the interrogation reveals you don't actually know who this is for or what
they need, that is a `NEEDS-MORE-RESEARCH` verdict pointing at `user-insights`.

## Agent behavioral contract

- business-value agents **render the worth-it verdict** (GO / NO-GO /
  NEEDS-MORE-RESEARCH) and author `business-value.md`.
- business-value agents **may NOT map user needs** — that is `user-insights`'
  profession; the two skills share **no artifact and no agent** (contract-level
  professional isolation).
- The verdict is the user's call to ratify; the agent proposes a recommendation
  with a one-paragraph rationale, it does not unilaterally commit the user's time.

## Verdict enum

Every non-skipped run ends in exactly one of:

- **GO** — worth the time budget; proceed downstream.
- **NO-GO** — not worth it now; record why so the decision isn't re-litigated blind.
- **NEEDS-MORE-RESEARCH** — the worth-it call can't be made on current evidence;
  route to `user-insights` (or planning-team for market economics), then revisit
  (re-entrant).

Weak-axis guidance: **one** weak axis with two concrete ones may still net GO —
name the weak axis in the rationale, never bury it. **Two or more** weak axes →
NEEDS-MORE-RESEARCH, not a hopeful GO.

## Procedure

1. **Check the triggers.** If a skip condition holds, stop silently — no artifact,
   implicit GO downstream.
2. **Read the template** — `assets/business-value-template.md` — so the artifact
   shape (and its verdict enum) is fixed before you write.
3. **Run the interrogation** one question at a time across why-now / why-me /
   opportunity-cost. Consult the sibling artifact at
   `docs/loom/discovery/<date>-<slug>/user-insights.md` for evidence when it
   exists. When an answer's factual claim is web-checkable in one search,
   check it and cite — don't leave every axis purely self-attested.
4. **Delegate** any market/GTM/revenue sub-question to `domain-teams:planning-team`
   (pass paths + seed context); fold only its returned verdict back in. Host
   invocation shapes for delegation/handoff live in
   `../using-loom-discovery/references/claude-code-tools.md` (Codex:
   `codex-tools.md` beside it).
5. **Emit `business-value.md`** into the change's discovery folder at
   `docs/loom/discovery/<date>-<slug>/business-value.md` (`<date>` = today,
   `YYYY-MM-DD`; `<slug>` = kebab-case topic; reuse the folder when the same
   topic already has one), following the template, with a
   **GO / NO-GO / NEEDS-MORE-RESEARCH** recommendation + one-paragraph
   rationale.
6. **Validate, then fix.** Before declaring done, run the discovery validator
   against the change's discovery folder — resolve the script path to an
   absolute path and run from the consumer project root:

   ```
   cd <consumer-project-root>
   python <resolved-absolute-path-to>/loom-discovery/scripts/validate_discovery_artifacts.py docs/loom/discovery/<date>-<slug>
   ```

   Fix any flagged issue and re-run, **bounded at 2 attempts**; on the 2nd
   failure, stop and surface the remaining problems to the user rather than
   looping silently. The validator tolerates the assess-first greenfield state
   (`business-value.md` alone, before `user-insights.md` exists) — a fresh
   first run in that state is not a failure.
7. On `NEEDS-MORE-RESEARCH`, hand off to `user-insights`; revisit this checkpoint
   once evidence deepens.

## Boundary

Stop at the worth-it one-pager. Do **not** map user needs (`user-insights`), do
**not** size the market or model revenue (`domain-teams:planning-team`), and do
**not** design, spec, or build. Those are downstream stations that *read* this
verdict.
