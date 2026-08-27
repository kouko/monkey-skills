# The Four-Field Goal Shape

> **SSOT for `loom-workflow:goal-create`.**
> This file is the authoritative definition of the four fields a goal
> condition is written in. Other files in this skill route here; do not
> duplicate the field definitions elsewhere.

A goal condition — the text a long-running agent run is checked against — is
written as four fields, in this order:

1. `Outcome`
2. `Constraints`
3. `Verification`
4. `Stop-when`

---

## 1 — `Outcome`

**Definition**: One measurable end state — not a vision.

A vision describes a direction ("make the onboarding flow better"). An
outcome names the one condition that, once true, means the run is finished
("the signup form submits with zero client-side validation errors on the
three test accounts"). If the field cannot be checked true/false against
concrete evidence, it is still a vision and has not yet become an outcome.

## 2 — `Constraints`

**Definition**: What must not change on the way to the outcome.

Constraints name the invariants the run is not allowed to break while
reaching the outcome — files it must not touch, behavior it must preserve,
budgets it must stay under. Without this field an agent optimizing purely
for the outcome may take a path that silently breaks something the outcome
statement never mentioned.

## 3 — `Verification`

**Definition**: Names a check, and requires that check's output be surfaced
in the conversation.

Naming a check is not enough on its own. **Claude Code's goal evaluator reads
only what has appeared in the conversation — it runs no commands and opens
no files.** A check whose output never appears in the conversation can never
be seen to hold, no matter how correctly it actually ran. Concretely, this
means the run must paste the test output, the lint result, the diff, or
whatever evidence the check produces, into the conversation itself — not
merely claim the check passed.

## 4 — `Stop-when`

**Definition**: Bounds the run.

`Stop-when` gives the run an explicit stopping condition beyond "when the
outcome is reached" — for example a turn clause such as "or stop after 20
turns." Without a bound, a run that cannot reach the outcome has no signal
to stop and report back instead of continuing indefinitely.

---

## The 4,000-character budget

A goal condition is capped at 4,000 characters. A goal whose full detail
would exceed that budget does not inline the detail — it points at a file
instead (the plan, the spec, the design doc) and keeps the goal condition
itself short enough for the evaluator to hold in view alongside the
conversation it is checking.

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
  the columns Outcome / Constraints / Verification.

**Attribution accuracy**: `Outcome`, `Constraints`, and `Verification` are
each named by both vendors' guidance above. `Stop-when` is not — it is
first-class in OpenAI's guidance (the "one stopping condition" in
`follow-goals`) but only optional, suggested guidance in Anthropic's (the
"or stop after 20 turns" example, not a required field). Treating
`Stop-when` as a required fourth field alongside the other three is **this
skill's own choice** — the vendor sources above ground only the first three
fields as shared guidance.
