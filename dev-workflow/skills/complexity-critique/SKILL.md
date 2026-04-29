---
name: complexity-critique
description: >-
  Gate for evaluating a specific proposed change — refactor, feature
  add, technical-debt cleanup, or even a should-we-build-this-at-all
  question with no existing code yet — through a deletion-first
  lens. Forces three checks: smallest possible result, before/after
  LOC count (N/A for pure greenfield; Q1 alternatives include
  "0 functions = decline to build"), what the change makes obsolete.
  Biases toward removing code over adding. Use when the user asks
  whether a change is worth the lines it adds, what can be deleted,
  whether a feature should exist at all, or how to keep a refactor
  small. Triggers: complexity audit / can this be simpler / what can
  we delete / worth the lines / should we build this / 降低複雜度 /
  可以再小一點 / 該不該做這個功能 / リファクタすべきか / 最佳實踐.
  Not-triggers: open-ended exploratory brainstorming with no specific
  feature or change proposed (use superpowers:brainstorming),
  multi-item proposal triage (use proposal-critique),
  post-implementation diff review (use Anthropic simplify), trivial
  single-line edits.
---

# Complexity Critique

A user-invoked gate skill: forces any specific proposed change —
refactor, feature add to existing code, technical-debt cleanup, or
a should-we-build-this question with no existing code yet — through
a deletion-first design pass before the change is implemented.

## Overview

More code begets more code. Every change is an opportunity to ask not
"how do I add this" but "what's the smallest end state that solves
this, and what can I delete (or never add) in the process?". This
skill turns that question into three mechanical checks before the
change is committed to.

**Core question:** *What does the codebase look like* after *the
change?* — not *what's the smallest change*.

This skill operates on a **specific proposed change**, whether to
existing code (refactor, feature add, debt cleanup) or proposed for
addition with no existing code yet ("should we build this feature
at all?" — Q2's LOC count gracefully degrades; Q1 / Q3 still anchor
the gate). It is not a multi-item proposal triage (use
`proposal-critique`), not an open-ended brainstorm without a
specific change in mind (use `superpowers:brainstorming`), and not
a post-implementation diff review (use Anthropic `simplify`).

## Before You Begin — Load a Mindset

**Required preamble**, carried forward from the upstream
`reducing-entropy` skill. The three questions below are mechanical
on their own; the mindset is what gives them weight. Skipping this
step is the single most common way to produce a competent-looking
critique with no actual deletion bias.

When `domain-teams:code-team` is installed:

1. Read the file list at
   `domain-teams/skills/code-team/standards/mindset-*.md` (4 files).
2. Read the frontmatter / opening section of each to see which
   applies to the change in front of you.
3. **Load at least one** by reading the full file.
4. Before answering Q1, state to the user which mindset you loaded
   and its core principle in one sentence.

When `domain-teams:code-team` is NOT installed:

1. State explicitly: "complexity-critique is running in advisory
   mode — mindset library unavailable; the user is asked to
   anchor the gate on one of the four upstream mindsets in plain
   language."
2. Recite, in one sentence each, the four mindset core principles
   from this file's §Reference Mindsets section so the user can
   pick.
3. Wait for the user to nominate one (or accept "design-is-taking-
   apart" as default — the most broadly applicable).

**Do not proceed to Q1 until a mindset is named and acknowledged.**
This is non-negotiable.

## The Iron Law

```
NO CHANGE SHIPS WITHOUT (1) A NAMED MINDSET AND (2) THE THREE QUESTIONS
```

Two-part discipline is non-negotiable. "It's just a small
change" is exactly when the discipline goes unrun and the codebase
grows for no good reason. Skipping the mindset turns the three
questions into a counting exercise with no design judgment.

## The Gate Function

When invoked, run these 3 questions in order:

### Q1. What's the smallest end state that solves this?

Not "what's the smallest change" — what's the smallest **result**.

- Could this be 2 functions instead of the 14 currently here?
- Could this be 0 functions — i.e., delete the feature?
- If we were starting from scratch with the current requirement,
  what would we build?

The change you would make to reach the smallest end state is often
not the change you were originally proposing.

### Q2. Does the proposed change result in less total code?

Count lines / functions / files **before** and **after** the
proposed change.

| If after > before | Reject the change as proposed |
| If after = before | OK — net-neutral on volume; assess Q3 |
| If after < before | Strong signal; usually correct |

**Pure greenfield handling**: when there is no existing code
("should we build this feature at all?"), Q2's LOC comparison
degrades — there's no `before`. Substitute: *what's the smallest
code that ships this feature, and is "0 lines = decline to build"
on the table?* Carry the deletion bias into the build decision; the
upstream skill explicitly listed "Evaluating feature requests
(should we add this?)" as a primary use case.

Common false-positive arguments to refuse:
- "Better organized" but more code = more entropy
- "More flexible" but more code = more entropy (and YAGNI)
- "Cleaner separation" but more code = the separation is shallow
  (Ousterhout, *A Philosophy of Software Design*)
- "Type safety" worth N lines is a real trade-off, not an automatic
  pass — name N

### Q3. What can we delete?

Every change makes something else *available* to delete. Ask:

- What does this change make obsolete?
- What was only there because of what we're replacing?
- What's the maximum we could remove while making the change?

A change that adds 50 lines and deletes 200 is a net win
(-150 lines). A change that keeps 14 functions to avoid writing 2
is a net loss (+12 functions). **Effort is not the metric. End-state
volume is.**

## Verdict

After the three questions, emit one of:

- **PROCEED** — change reduces total code; ship it.
- **PROCEED-WITH-CAVEAT** — change is net-neutral or marginally
  positive; ship but name the trade-off the user is choosing
  ("type safety worth ~30 lines", "explicit error path worth ~12
  lines").
- **RESHAPE** — change as proposed adds more than it removes; the
  user is choosing easy over simple. Propose the smallest-end-state
  alternative from Q1.
- **REJECT** — change adds code with no end-state justification;
  redirect the user to Q1's alternative or to deletion.

Do NOT silently approve a change that fails Q2 without naming the
trade-off. Hidden growth is the failure mode this skill exists to
prevent.

## Red Flags — STOP

These thoughts mean you are rationalizing your way past the gate:

| Argument | Why it fails |
|---|---|
| "Keep what exists" | Status quo bias. The metric is total code, not churn. |
| "This adds flexibility" | Flexibility for what? YAGNI. (See `domain-teams:code-team/standards/pragmatic-principles.md` §YAGNI.) |
| "Better separation of concerns" | More files / functions = more code. Separation is not free. (See `mindset-design-is-taking-apart.md` Ousterhout deep-vs-shallow.) |
| "Type safety" | Worth how many lines? Sometimes runtime checks in less code wins. Name the line cost. |
| "Easier to understand" | 14 things are not easier than 2 things. (See `mindset-simplicity-vs-easy.md`.) |
| "Industry standard pattern" | Industry standard is not a primary source. Either cite the source or mark it speculative. |
| "We might need this later" | YAGNI. PAGNI is the named exception — see `mindset-expensive-to-add-later.md` for the *high* bar. |

## Rationalization Prevention

| Excuse | Reality |
|---|---|
| "It's just a small change." | Small changes accumulate. Run the gate anyway. |
| "Refactoring it later is fine." | Later is more expensive than not adding it. |
| "The diff looks clean." | Clean diff ≠ clean end state. Q1 is about end state. |
| "All these classes are already there." | The current state is not a justification; it's the evidence Q1 might disagree with. |
| "I don't have time for the gate." | The gate is one read of the file plus three questions. The cost of skipping it is permanent. |

## Reference Mindsets

The four mindsets that anchor this skill (one of which MUST be
loaded per §Before You Begin). They live in
`domain-teams:code-team/standards/` as the single source of truth
(per CLAUDE.md §Cross-Plugin Delegation Contract — paths only, no
content duplication).

| Mindset | Core principle | Use when… |
|---|---|---|
| `mindset-data-over-abstractions.md` | Perlis #9 / Hickey: 100 functions on 1 data structure beats 10 on 10 | Q1 / Q2 are arguing about whether something deserves its own class / type / wrapper |
| `mindset-design-is-taking-apart.md` | Hickey: design is separation, not addition; *complect* vs *compose* | Q3 is asking whether concerns are *complected* (must be combined) or merely tidy-looking; **default if unsure** |
| `mindset-expensive-to-add-later.md` | Willison: PAGNI is YAGNI's named exception; high bar | "we might need this later" is being invoked; need the PAGNI three-test bar |
| `mindset-simplicity-vs-easy.md` | Hickey: simple = objective, not braided; easy = subjective, familiar | An "easy" / familiar choice is being made over a less-familiar simpler one |

If `domain-teams` is not installed, recite the four core principles
above to the user verbatim and accept their nomination in plain
language; the gate runs in advisory mode but still requires a named
anchor before Q1.

## Composes With

This skill triages **a proposed change to existing code**. It does
not do deeper research, multi-item triage, or post-implementation
review. Hand off when the case calls for it:

- **Multi-item proposal triage** — when the input is a list / plan /
  prose with ≥3 separate proposals, see `proposal-critique` first.
  This skill operates on a *single change*, not a backlog.
- **Greenfield design** — when there is no existing code to compare
  before/after against, see `superpowers:brainstorming`. Q2's LOC
  count requires existing code as the baseline.
- **Post-implementation simplification** — when the change is
  already written and the question is "can this diff be smaller",
  see Anthropic `simplify`. This skill runs *before* the change.
- **Refactor mechanics** — when the change is approved and the
  question is "how to do the refactor safely", see
  `domain-teams:code-team/protocols/refactoring.md` (Two Hats, Bad
  Smells, Feathers seam model).

This skill names those tools but does not invoke them.

## Worked Examples

### Example 1 — feature add to existing forms

**Input**: "I need to add validation to these 5 forms."

**Q1 (smallest end state)**:
- Could the codebase have 1 validator instead of 5 form-specific
  schemas? (Often yes if the rules overlap.)
- Could 3 of the 5 forms be merged or deleted? (Forms accumulate
  faster than they prove useful.)
- Smallest end state candidate: 2 forms + 1 validator function.

**Q2 (LOC count)**:
- Current: 5 forms (~500 lines), 0 validation
- Proposed (5 schemas + helper file + 5 form updates): ~800 lines
- Q1 alternative (delete 3 forms, add 1 validator): ~350 lines
- Q1 wins by 450 lines.

**Q3 (what becomes obsolete)**:
- 3 of the deleted forms had only 2 users / month — usage data
  available; deletion is justified.
- The 2 surviving forms can share one validator → no per-form schema
  duplication.

**Verdict**: RESHAPE — original proposal grows the codebase by 300
lines for marginal validation coverage. Q1 alternative reduces total
code by 150 lines and delivers the validation as a side effect.

### Example 2 — refactor to "improve type safety"

**Input**: "Convert this 80-line module to use a tagged union for
result types."

**Q1**: smallest end state is either (a) keep current module, (b)
add tagged union, (c) inline the module entirely if its only caller
could read the raw value.

**Q2**: tagged union adds ~30 lines (new type, constructor variants,
exhaustiveness handling). 80 → 110 lines, +30.

**Q3**: nothing in the module becomes obsolete; the existing
runtime checks stay because callers don't all migrate at once.

**Verdict**: PROCEED-WITH-CAVEAT — the 30 lines buy compile-time
exhaustiveness, which the user explicitly chose. Name the trade-off:
"30 lines bought, 0 lines saved, exhaustiveness check enforced".
This is a legitimate choice — but call it what it is.

## When To Apply

**Primary triggers (user-spoken)**:

- "Should I add this?" / "is this worth the code?"
- "Should we build this feature at all?" / "該不該做這個功能"
- "Can this be simpler?" / "可以再小一點 嗎"
- "What can we delete here?" / "リファクタすべきか"
- "降低複雜度" / "complexity audit on this change"

**Shape**: A *specific proposed change*. The change can be a
refactor, a feature add to existing code, a debt cleanup, or a
should-we-build-this-feature-at-all question with no existing code
yet. The upstream skill (`reducing-entropy`) explicitly lists
"Evaluating feature requests (should we add this?)" as a primary
use case alongside refactor / debt cleanup; this distribution
preserves that scope.

**Not-triggers** — do NOT invoke for:

- **Open-ended exploratory brainstorming** — no specific change or
  feature proposed yet, just "what could we build". Use
  `superpowers:brainstorming` to land on a specific proposal first;
  then complexity-critique applies. Pure greenfield with a *named*
  proposal IS in scope.
- **Multi-item proposal triage** — a list / plan with ≥3 separate
  recommendations; use `proposal-critique` first, then this skill on
  surviving items.
- **Post-implementation review** — the change is already written;
  use Anthropic `simplify`.
- **Trivial micro-changes** — single-line fixes, variable renames,
  comment updates. The gate cost exceeds the change cost.
- **External-API constraints driving the addition** — when an
  upstream API mandates the structure, Q1's alternatives may not
  exist. Note the constraint and proceed.

## Bottom Line

```
The end state is the metric.
Bias toward deletion.
Name the trade-off when you choose to add.
```
