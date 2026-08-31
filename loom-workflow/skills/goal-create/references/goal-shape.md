# The Four-Field Goal Shape

> **SSOT for `loom-workflow:goal-create`.**
> The authoritative definition of the four goal fields; other files in
> this skill route here rather than duplicating them.

A goal condition — the text a long-running agent run is checked against — is
written as four fields, in this order:

1. `Outcome`
2. `Constraints`
3. `Verification`
4. `Stop-when`

---

## 1 — `Outcome`

**Definition**: One measurable end state — not a vision.

A vision describes a direction ("make onboarding better"); an outcome
names the one condition that, once true, means the run is finished ("the
signup form submits with zero validation errors on the three test
accounts"). A field that cannot be checked true/false against evidence is
still a vision.

## 2 — `Constraints`

**Definition**: What must not change on the way to the outcome.

Constraints name the invariants the run is not allowed to break while
reaching the outcome — files it must not touch, behavior it must preserve,
budgets it must stay under. Without it, an agent optimizing purely for the
outcome may silently break something the outcome never mentioned.

**Standing decision rule**: choices the goal does not pre-decide are the
run's to make — it searches first, decides, and records the decision,
its candidates, and its sources in a named file, and never stops to ask.

SESSION mode emits this by default, tagged `derived` with this section as
its anchor — `input-floor.md` §5 lets a standing entry name the reference
that defines it — so a user need not write it each time.

Outside the run: an irreversible or outward-facing act — merge, deploy,
send — where `Outcome` already ends.

## 3 — `Verification`

**Definition**: Names a check, and requires that check's output be surfaced
in the conversation.

Naming a check is not enough on its own. **Claude Code's goal evaluator reads
only what has appeared in the conversation — it runs no commands and opens
no files.** A check whose output never appears in the conversation can never
be seen to hold, no matter how correctly it actually ran. So the run pastes
the check's output — test result, lint, diff — into the conversation,
rather than claiming it passed.

## 4 — `Stop-when`

**Definition**: Exactly one mechanical bound — a turn count or a
wall-clock limit — phrased as a completion condition, never a list of
exit conditions.

Reaching that bound, with a status report posted in the conversation,
counts as the run completing — as a failure report: the outcome was not
reached, but the run is done. A bare "stop after 20 turns" is read by
Claude Code's goal evaluator as permission to stop, not as the condition
having been met, so it neither releases the run nor bounds it.

For example: "Stop when the outcome above is reached, or when 20 turns
have passed and a status report has been posted — either way is the run
completing."

A human-dependent fork — a choice only a person can make — is never a
`Stop-when` branch; see `input-floor.md` §4 item 3 for where it goes
instead.

---

## The 4,000-character budget

A goal condition is capped at 4,000 characters. A goal whose full detail
would exceed that budget does not inline the detail — it points at a file
instead (the plan, the spec, the design doc) and keeps the goal condition
itself short enough for the evaluator to hold in view alongside the
conversation it is checking.

Only Anthropic's guidance documents this cap; OpenAI's guidance states no
length limit at all. This skill applies the same budget to goals for either
host, for portability — not because OpenAI documents a cap of its own.

---

## Provenance and attribution

This shape is grounded in both vendors' published long-running-agent
guidance, cited here so a reader in any repository can verify it directly:

- **Anthropic** — <https://code.claude.com/docs/en/goal> — names one
  measurable end state, a stated check, and the constraints that matter;
  caps the goal condition at 4,000 characters; suggests a turn clause such
  as "or stop after 20 turns."
- **OpenAI** — <https://learn.chatgpt.com/use-cases/follow-goals> — "Name
  one objective and one stopping condition. Point Codex at the files, docs,
  issue, logs, or plan it must read first. Define the commands or artifacts
  that prove progress. Tell Codex to work in checkpoints and keep a short
  progress log."
- **OpenAI** — <https://learn.chatgpt.com/docs/long-running-work> — names
  three goal elements: Outcome, Constraints, Verification.

**Attribution accuracy**: both vendors' guidance above covers the same
three elements, but they label them differently, and only one of the three
field names is shared. OpenAI's `long-running-work` uses all three —
`Outcome`, `Constraints`, `Verification`. Anthropic's bullets read "One
measurable end state", "A stated check", and "Constraints that matter", so
`Constraints` is common ground while `Outcome` and `Verification` are
borrowed from OpenAI rather than shared vocabulary. `Stop-when` is not
among the three at all — it is first-class in OpenAI's guidance (the "one
stopping condition" in `follow-goals`) but only optional, suggested
guidance in Anthropic's (the "or stop after 20 turns" example, not a
required field). Treating
`Stop-when` as a required fourth field alongside the other three is **this
skill's own choice** — the vendor sources above ground only the first three
fields as shared guidance.

That Anthropic example is quoted for attribution only: as §4 states, a bare
turn clause reads as permission to stop, so this skill writes the bound as
a completion condition.
