Source: `writing-plans/SKILL.md` §"Red Flags — refuse these rationalizations" — serves `writing-plans`.

# Red Flags — refuse these rationalizations

| Agent / user says | Reality | Correct response |
|---|---|---|
| *"Just skip planning, the brief is enough."* | The brief is the *what*; the plan is the *how-cut-into-atomic-pieces*. SDD needs atomicity, not just scope. | Refuse. Produce the plan even if it's only 1-2 tasks. If 1 task, the brief was an exemption candidate (§When NOT to Use). |
| *"This task is roughly an hour but I don't know how to split it."* | "I don't know how to split" is a discovery failure, not a planning failure. The brief did not articulate Axis 3 (smallest end state) tightly enough. | Surface back to brainstorming for Axis 3 re-cut, do not produce a 1-hour task that resolves to a single assertion and calls itself done — split by criterion 1 (one failing test), not by the clock. |
| *"This chain is 8 tasks deep, that's fine."* | No — see §Plan size ceiling. Critical-path depth >5 = brief too big. (A wide-but-shallow 8-task plan is fine; a deep 8-link chain is not.) | Refuse the deep chain. Route back to brainstorming OR split into N briefs each with depth ≤5. |
| *"Skip the plan-document-reviewer, it's overkill."* | The reviewer catches the failure modes the splitting framework misses (orphan tasks, cycle dependencies, brief-task coverage gaps). | Refuse. Self-review is non-negotiable. If you genuinely produced a perfect plan, the reviewer takes 30 seconds to confirm. |
| *"Implementer returned BLOCKED, just retry."* | Beck Child Test pattern says split smaller, not retry. Silent retry burns SDD's 3-round cap. | Re-invoke writing-plans on the failing task per §BLOCKED fallback. |
| *"This task depends on Task 1, Task 3, AND a thing not in the plan."* | The "thing not in the plan" is a missing task. Declare it. | Add the missing task to the plan. Re-run plan-document-reviewer. |
| 「先跳過 plan 直接派 SDD 吧 / プランは飛ばして」 | Same rationalization, localized. | Same refusal — produce the plan. |
