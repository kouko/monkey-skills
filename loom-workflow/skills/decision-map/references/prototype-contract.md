# Prototype contract

## Purpose — the closure boundary

Schema v3 has exactly four closure types: `grilling`, `research`, `prototype`,
and `delivery`. A prototype exists only when a human evaluates or selects a
newly created candidate artifact. The human reaction is the evidence.

Route by what settles the question:

- discussion and a ratified value or direction decision → `grilling`;
- lookup, inventory, experiment, or machine-measured feasibility → `research`;
- a human evaluates or selects a newly created candidate → `prototype`;
- formal evidence delivers one promised outcome slice → `delivery`.

A machine pass/fail result is research even when code had to be built to
measure it. Calling that work a prototype would give factual evidence a human-
evaluation closure contract it does not need.

## Definition — what qualifies

A prototype is throwaway candidate code built to answer one human-evaluation
question, in one of two forms: a logic interaction candidate (state machine,
algorithm, or data-shape playground) or a surface candidate (UI variants).
The question is written in the Ticket before code exists and at the top of the
artifact itself.

Constraints:

- lives only on `prototype/<map-id>/<ticket-slug>` and never merges;
- one sitting of agent build work; human reaction time is outside the timebox;
- no tests, persistence, production error handling, or speculative abstraction;
- logic candidates isolate decision-rich behavior in a pure portable module;
- surface candidates disagree structurally and use real context/data when
  available;
- trivially runnable and visibly reports state after each action;
- filenames or entry point visibly say prototype;
- exactly one named question; a whole-app prototype is refused.

The moment the artifact is hardened for production, the prototype has ended.
Production behavior is re-landed later through normal TDD and review.

## Risk-driven front-loading

Front-load a Ticket when the Map's highest-risk assumption can only be judged
by human reaction to a candidate: an architecturally significant interaction
has no candidate, a surface direction could invalidate the effort, or a
Riskiest Assumption Test requires someone to experience alternatives.

Do not mint a prototype when conversation settles the decision, research can
answer it, or a machine measurement can establish feasibility. Those routes
are `grilling` or `research`. Name the evaluation question and success signal
before the build; keep the one-sitting timebox.

## Lifecycle — six stages

1. **Birth** — charting or re-charting creates a `prototype` Ticket with one
   human-evaluation question.
2. **Build** — the agent creates the fenced prototype branch and throwaway
   candidates. TDD's spike exemption applies only inside this fence.
3. **React** — the named human drives or inspects the candidate. The agent
   never answers its own evaluation question.
4. **Evaluate / Select** — the human records the evaluation or selected
   candidate. Closure requires named, dated `user-ratified:` evidence.
5. **Distill** — the Resolution records `candidate-artifact:`, `evaluation:`,
   the ratification, and the decision-rich result; the branch remains linked
   as primary evidence.
6. **Death** — the branch never merges. Later implementation re-lands the
   behavior under full TDD. The branch stays read-only while the Map is live;
   retirement lists surviving branches, and only the repo owner chooses
   whether to prune them.

If measurement completes but human evaluation is deferred, the Ticket stays
`claimed` and may carry `ratification: pending`. It closes only after the
human evaluation arrives.
