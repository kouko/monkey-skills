# Cold-reader probes — review-cost-reduction (Task 15)

Date: 2026-08-11
Branch: feat/review-cost-reduction
Plan: docs/loom/plans/2026-08-11-review-cost-reduction.md, Task 15

## Method

Two fresh-context `haiku` agents (Agent tool, `subagent_type: general-purpose`,
`model: haiku`), each dispatched with **only** the rule text under test plus
one realistic task — no plan, no brief, no framing that this was a probe.
This is the institution quality floor for prompt/skill/rule text
(`~/.claude/rules/judgment-rubrics.md` §5: "A cold agent executes it blind
on one real case").

Rule-text sources (verbatim extraction, no paraphrase):
- Probe (a): `loom-code/skills/writing-plans/SKILL.md` `<SUBAGENT-STOP>`
  block (lines 8-10) + `## Self-review — plan-document-reviewer` section
  (lines 97-121), post-Task-2 state.
- Probe (b): `loom-code/skills/requesting-code-review/SKILL.md`
  `## Classification: contract-class vs record-class` section (lines
  49-55), post-Task-8 state.

## Probe (a) — misroute

**Task given to the haiku agent** (verbatim, appended after the rule text):

> You are orchestrating writing-plans and have just produced a plan at
> docs/loom/plans/X.md with source brief docs/loom/specs/X.md. Describe
> precisely, step by step, how you dispatch the self-review — which tool,
> which agent type, what you pass.

**PASS criterion**: the probe says it dispatches the PROMPT FILE
(`references/plan-document-reviewer-prompt.md`) via a generic/
general-purpose subagent — AND does NOT look up a `plan-document-reviewer`
agent type in a registry — AND does NOT substitute `docs-reviewer` or any
other reviewer agent.

**Key quotes from the probe's response**:

> "Agent type: omit `subagent_type` (defaults to `general-purpose`)"
>
> "Include the full reviewer prompt by reading it into the dispatch packet"
>
> Dispatch call shown: `Agent(description: "Plan-document-reviewer
> verdict", prompt: ("... using the full checklist in this prompt file:
> <absolute-path-to>/monkey-skills/loom-code/references/
> plan-document-reviewer-prompt.md" "\n\n[Full text of
> plan-document-reviewer-prompt.md] ..."), model: "sonnet")`

The probe correctly identified: (1) the prompt file is the dispatch
payload, (2) the agent type is generic (`general-purpose`, via omitted
`subagent_type`), never a registry lookup for a "plan-document-reviewer"
agent type, (3) it never mentioned `docs-reviewer` or any other named
reviewer agent as a substitute.

**Verdict: PASS**

## Probe (b) — classification

**Task given to the haiku agent** (verbatim, appended after the rule text):

> Classify each of these 10 paths as contract-class or record-class per
> the rule above. List each path with its classification, one per line.
>
> 1. loom-code/skills/brainstorming/SKILL.md
> 2. loom-code/agents/implementer.md
> 3. docs/loom/audits/2026-08-04-x.md
> 4. loom-code/skills/writing-plans/references/plan-format.md
> 5. loom-code/README.md
> 6. loom-code/CHANGELOG.md
> 7. loom-code/scripts/_reviewer-discipline.md
> 8. docs/loom/backlog/2026-08-10-y.md
> 9. loom-code/hooks/git-guard.py
> 10. investing-toolkit/skills/data-markets/SKILL.md

**PASS criterion**: all 10 classified correctly (contract: #1, #2, #4,
#7, #10; record: #3, #5, #6, #8; #9 must NOT be classified contract — any
phrasing that keeps it out of contract-class is accepted).

**Probe's verbatim response**:

> 1. loom-code/skills/brainstorming/SKILL.md — **Contract-class**
> 2. loom-code/agents/implementer.md — **Contract-class**
> 3. docs/loom/audits/2026-08-04-x.md — **Record-class**
> 4. loom-code/skills/writing-plans/references/plan-format.md —
>    **Contract-class**
> 5. loom-code/README.md — **Record-class** (excluded basename)
> 6. loom-code/CHANGELOG.md — **Record-class** (excluded basename)
> 7. loom-code/scripts/_reviewer-discipline.md — **Contract-class**
> 8. docs/loom/backlog/2026-08-10-y.md — **Record-class**
> 9. loom-code/hooks/git-guard.py — **Record-class** (not `.md` format)
> 10. investing-toolkit/skills/data-markets/SKILL.md — **Contract-class**

All 10 match the expected classification. Item 9 (`git-guard.py`) was
placed in "Record-class" with the reason "not `.md` format" rather than a
literal "outside the rule's domain" phrasing — the task's acceptance text
explicitly accepts any phrasing that does not classify it contract, so
this counts as correct.

**Verdict: PASS**

## Overall verdict

Both probes PASS. No wording fix required on either
`loom-code/skills/writing-plans/SKILL.md` §Self-review or
`loom-code/skills/requesting-code-review/SKILL.md` §Classification — a
cold `haiku` agent, given only the rule text and a realistic task,
routes correctly on both the misroute case and the classification case.
No skill text was edited as part of this task.

No pytest run — this task produces no code, only a dogfood report; the
report file's existence + content is the acceptance check (RED = file
absent, GREEN = file present with both probes recorded).
