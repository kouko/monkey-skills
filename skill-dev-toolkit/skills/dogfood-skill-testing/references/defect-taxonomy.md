# Defect taxonomy — dogfood-skill-testing

> **A bad SKILL.md doesn't throw an error — it just never gets invoked.**

A skill defect is not a crash. The dominant failure mode is *silent*:
the skill never fires, fires for the wrong request, or produces
valid-looking output that is domain-wrong. This taxonomy gives the
dogfood agent a vocabulary to classify findings and a base-rate prior
(measured community frequencies, where known) so it probes the
high-yield defects first.

Every finding is tagged **`<severity> × <category>`**. The two axes are
independent: severity measures user impact, category measures *what kind*
of defect it is. A Trigger-miss can be Critical (the skill's whole reason
to exist never fires) or Low (a rare synonym phrasing doesn't match) — so
always score severity per the concrete skill, never inherit it from the
category.

---

## Severity (impact on the user)

Score the *consequence* if this defect ships, not how easy it is to fix.

| Level | One-line definition |
|---|---|
| **Critical** | Blocks the skill's core job — it never fires when it must, or produces actively wrong output a user would act on. |
| **High** | A major part of the workflow is broken with no workaround; the user cannot complete the intended task. |
| **Medium** | The skill works, but with noticeable problems; a workaround exists. |
| **Low** | Minor cosmetic / polish issue; no functional impact. |

---

## Categories (what kind of defect)

Annotated with the **measured community frequency** where known, from the
214-skill audit (DEV/thestack_ai, *"73% silently broken"*) and Scott
Spence's sandboxed-activation evals. Probe the high-base-rate categories
first.

### Trigger-miss — *the skill never fires when it should*
The `description` lacks the trigger phrases a real user would say, so the
router never selects it — the skill is **"silently broken."** Highest-yield
defect class. **68%** of audited skills had missing trigger phrases;
**41%** had a description under 20 words (too thin for the router to match).
Detected by the activation pass: should-trigger queries that don't fire.

### Over-trigger — *the skill fires when it should NOT*
The description is too broad or overlaps a sibling's, so the router picks
this skill for requests it shouldn't handle (or steals them from the right
skill). Only measurable with **should-NOT-trigger** queries plus a
distractor set present; the 214-skill audit found overlapping-description
conflict pairs. Detected by the activation pass: a true-negative that fires.

### Cold-start — *breaks when invoked with zero prior context*
The skill assumes session state, a config folder, or earlier conversation
that a fresh invocation doesn't have, and collapses on first use. Highest
bug density of any path, least exercised — force the no-config / fallback
path to surface it. Detected by the cold-reader and the executor run
through the fallback path.

### Workflow-drift — *the executor doesn't follow the steps the SKILL.md describes*
The body prescribes a procedure, but an agent actually running the skill
diverges — skips a step, reorders, or improvises — because a step is
under-specified ("verify" with no how) or ambiguous. Detected by the
informed executor pass: compare the trajectory against the written steps.

### Gate-bypass — *a gate the skill claims to enforce gets skipped*
The skill says it blocks on a check (a quality gate, a SHOULD/MUST clause,
a required review), but in practice the gate is worded weakly or placed
where the executor sails past it. Detected when the executor completes
without the gate firing. A SHOULD that needs to be a MUST is the common
root cause.

### Jargon-leak — *undefined internal terms surface to the user*
The skill emits author-internal vocabulary (acronyms, project codenames,
status tokens like `PASS X/X`) that a first-time user can't parse. The
in-session dev agent treats its own jargon as baseline; only a
zero-context cold-reader reacts like a real first user. Detected by the
cold-reader's "undefined terms?" question.

### Convention-violation — *breaks the repo / Anthropic skill conventions*
Structural non-conformance: **missing `version` field (62%** of audited
skills), nested-subfolder breach of the flat-folder rule, non-kebab-case
naming, broken bundled-file paths. Often Low severity individually but
hard-gates (CI / structure hooks) can make it blocking. Detected by the
informed auditor against the declared conventions.

### Progressive-disclosure — *bundled references loaded wrong*
A bundled reference / template the workflow needs is **not loaded when
needed** (the agent never reads it, so the rule it carries doesn't fire),
or is **loaded eagerly** (pulled in upfront, burning context it should
defer). Detected by checking which bundle files the executor actually
opened versus which the workflow required.

### Output-quality — *valid-looking output that is domain-wrong*
The skill produces output that passes its own format / self-grade check
but is **domain-wrong**: a fabricated citation, leaked private data, the
wrong number. The skill *"met its own bar but is domain-wrong."* This is
why the auditor is firewalled from how the output was produced and judges
against a domain standard, not the skill's self-grade — self-grading is
structurally blind to its own blind spots. Detected by the blind auditor
pass on a real / realistic executor artifact.

---

## How the axes compose

Severity and category are orthogonal. The category tells the main agent
*where to look* and *what edit class fixes it* (e.g. Trigger-miss → add
trigger tokens to the description's first line); the severity tells it
*how urgently*. Always report both, and derive severity from the concrete
skill-under-test — the same category lands at different severities
depending on whether the affected behavior is the skill's core job or a
rare edge.
