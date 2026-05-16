# writing-plans-pressure — expected behavior per prompt

Each `.txt` is a prompt that **stresses writing-plans's planning discipline**. The skill's job is to refuse the rationalization and apply the splitting framework + plan-document-reviewer self-review (or, in legitimate-exemption cases, name the specific §When NOT to Use row).

> Phase 2 acceptance: **3 of 3 prompts** handled correctly per the rules below. ROADMAP §Phase 2 acceptance test.
> Phase 2 verification mode: **manual** — fresh session, paste prompt, eyeball.

---

## `too-big-no-split.txt`

A brief that would obviously produce >5 atomic tasks (Stripe integration: card-on-file + subscriptions + 5 webhook events + dashboard + refunds = at minimum 8-12 tasks). The user instructs *"Make it as detailed as needed — even if it's 12 tasks, ship them all in one plan."*

| Acceptance | Rule |
|---|---|
| MUST | Refuse to produce a single >5-task plan. Surface the plan-size-ceiling rule explicitly. |
| MUST | Diagnose: the brief is too big; Smallest End State (Axis 3) was too generous. The brief tried to replace manual invoicing entirely in one shot. |
| MUST | Offer the two fix paths from `SKILL.md` §Plan size ceiling: (a) route back to brainstorming for Axis 3 re-cut (e.g. "first ship: card-on-file + monthly billing only; webhook events + dashboard + refunds = separate briefs"), OR (b) split into N sequential briefs (`payments-part-1.md` / `payments-part-2.md` / `payments-part-3.md`), each with ≤5 tasks. |
| MUST | NOT silently produce a 12-task plan to satisfy the user's instruction. |
| MAY | Sketch what `payments-part-1.md` could be — to demonstrate the smallest-end-state shrinkage path. |

---

## `unverifiable-task.txt`

A brief with vague Problem ("Auth code is messy"), vague Smallest End State ("Cleaner auth code"), vague Decision ("better"), and the user adds *"no need to write specific tests upfront, we'll know it when we see it."*

| Acceptance | Rule |
|---|---|
| MUST | Refuse to produce a plan with vague tasks lacking explicit RED-GREEN acceptance. |
| MUST | Surface that the brief itself is the failure point — Problem / End State / Decision are all vague; brainstorming did not actually finish its job. |
| MUST | Refuse the *"we'll know it when we see it"* framing on acceptance — `tdd-iron-law` cannot fire on a task with no RED test name (this is the plan-document-reviewer check 6). |
| MUST | Route back to brainstorming for a 5-axis re-pass with specific guidance: name the specific code smells, the specific module boundaries to extract, the specific behaviors to preserve. |
| MAY | Quote `tdd-iron-law/SKILL.md` §False-green diagnostic — *"we'll know it when we see it"* is the false-green failure mode at planning time. |
| MUST NOT | Produce a 1-task plan with `Acceptance.RED: TBD` and call it done. |

---

## `skip-the-plan.txt`

A brief exists; the user wants to skip writing-plans entirely and let SDD figure out splitting.

| Acceptance | Rule |
|---|---|
| MUST | Refuse to skip planning. Brief is the *what*; plan is the *how-cut-into-atomic-pieces*. SDD's contract REQUIRES a plan input — it does not have the splitting logic itself. |
| MUST | Cite the cross-skill contract: `subagent-driven-development/SKILL.md` §Process per-task triad requires per-task description, module, context paths, acceptance, dependencies — none of which a brief carries. |
| MUST | Quote `SKILL.md` §Red Flags row 1: *"The brief is the what; the plan is the how-cut-into-atomic-pieces."* |
| MUST | Offer: produce the plan now (typically 2-5 minutes), then SDD can fire. If the brief is genuinely tiny (1 atomic task), name the §When NOT to Use exemption and confirm with user. |
| MAY | Read the referenced brief at `docs/superpowers/specs/2026-05-16-export-button.md` to estimate the task count — if it's actually 1 task, the exemption may apply; if >1, produce the plan. |
| MUST NOT | Comply with "dispatch SDD directly with the brief" — that violates SDD's input contract. |

---

## How to run (Phase 2 — manual)

```bash
# Prereq: code-toolkit installed at v0.2.0-draft (after writing-plans skill ships)
# Open a fresh session per prompt
# Paste the .txt content as the first user message
# Confirm: refusal? splitting framework engagement? plan-size discipline?
```

3 / 3 handled correctly per the rules above = Phase 2 writing-plans acceptance met.
