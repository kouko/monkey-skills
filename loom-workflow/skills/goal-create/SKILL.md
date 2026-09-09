---
name: goal-create
version: 0.1.0
description: |
  Create a goal condition — SESSION mode validates the four-field goal (Outcome / Constraints / Verification / Stop-when) and activates it in the current host when supported; otherwise it gives one honest manual activation command. ARC mode drafts a repository's purpose artifact `Why` / `Done when` for the user to land. Use for 'set a goal', 'give this run a stopping condition', '設一個目標', 'ゴールを立てて'. This skill never fires on its own; it must be invoked by name.
---

# Goal Create

One skill, two named modes: **SESSION** and **ARC**. Which mode runs is
chosen by what the user asks for — a goal for this run, or a purpose for
the repository — never by the agent guessing from context.

## SESSION mode

SESSION emits the four-field goal condition defined in
`references/goal-shape.md`. Read that file for the field order and each
field's definition before drafting; do not reconstruct the shape from
memory.

Before drafting, read `references/input-floor.md` for the two input slots
a goal is drafted from, the refusal rule when a slot is empty, the
provenance tag every field must carry, and the citation boundary between
quoting a recorded purpose and a user's own decision.

Once a draft is ready, run the mechanical floor:

```
python3 scripts/goal_lint.py <goal-file>
```

(or pipe the goal text on stdin with no argument). This checker enforces
structure only — a field label present with content, a backticked command
inside `Verification`, the character limit — never whether the prose
actually reads as decidable, already-false, or free of a person. The bar
in `references/input-floor.md` §4 stays a judgement call the agent makes
each time; no script can pass or fail it on the agent's behalf.

The script exits 1 on any hard failure and 0 otherwise. On exit 1, the
draft is rewritten to fix what it flagged and the checker is re-run — a
draft is never shown to the user until it exits 0.

After exit 0, show the complete four-field condition in the conversation,
then use the capability actually exposed by the current host. Invoking the
named `goal-create SESSION` mode is explicit authorization to replace any
active Goal with this condition, without a separate replacement confirmation.
Confirmation is only for content: when the Outcome was inferred or materially
changed from the user's words, use the host's confirmation path.

### Codex activation

Call `create_goal` with the complete four-field condition as its objective.
Call the Goal active only after host-provided success. On any failure, report
the host's reason and say the new Goal is not active. In particular, when an
unfinished Goal makes `create_goal` refuse replacement, preserve it and tell
the user to run `/goal clear`, then run `goal-create SESSION` again.

### Claude Code activation

When the interactive session exposes `ProposeGoal`, derive a proposal of at
most 500 characters from the complete condition just shown. It preserves the
Outcome, every behavior-changing Constraint, the decisive Verification, and
the Stop-when bound, either inline or through an exact reference to that
immediately preceding condition. A generic phrase such as "the goal above"
is not an exact reference. If the faithful proposal cannot fit, skip
`ProposeGoal` and use the manual fallback below.

Call `ProposeGoal` with `ask_user: false` only when the user's own words state
the exact Outcome. Otherwise use its confirmation path and report the Goal as
pending, not active, until the host confirms kickoff. An existing Goal does
not change this content-confirmation rule: the SESSION invocation already
authorizes replacing it without a separate replacement confirmation.

When the current session does not expose `ProposeGoal`, or native activation
returns a non-success result, say the Goal is not active and user action is
required. Emit one copyable `/goal <condition>` command containing the
complete condition, not the compact proposal, and disclose that submitting it
replaces any active Goal. Do not invoke `claude -p`, inject keystrokes, launch
another process, or install a custom Stop hook.

For either host, an attempted call, displayed prose, pending confirmation, or
manual command is not activation evidence. Report active only from the host's
successful result, and keep its recoverable reason visible otherwise.

## ARC mode

ARC drafts a `Why` and a `Done when` for the repository's purpose artifact
at `docs/loom/PURPOSE.md` — see that file for its exact two-field format;
this skill does not restate it. ARC never writes that file itself; the
draft is only ever landed by the user's own confirmation.

ARC is conditional. When the repository has no `docs/loom/` store and no
`docs/loom/PURPOSE.md` file — nothing yet scaffolded to hold one — ARC
reports itself not applicable, names the reason, and scaffolds nothing —
creating the store is `loom-init`'s job, not this skill's.

## Invocation

This skill never fires on its own — the description above makes no
auto-fire claim. It is named as an available
option at exactly one point where the need for a goal is already
visible: `loom-workflow:handoff`'s Prepare mode, when a user closes a
session without capturing an explicit goal. That surface names this
skill as an option the user can invoke; it never invokes it. loom 1.0
deleted the other two offer sites with the skills that carried them.

When `loom-design:capture-intent` is already running for the same work,
that station keeps discovery and this skill runs only after its intent
exists, rather than competing for the same turn.

## See also

- `references/goal-shape.md` — the four-field goal shape, SESSION's SSOT.
- `references/input-floor.md` — the two input slots, the refusal rule, the
  bar, and provenance tags.
- `scripts/goal_lint.py` — the mechanical floor SESSION's draft is run
  through before it is presented.
