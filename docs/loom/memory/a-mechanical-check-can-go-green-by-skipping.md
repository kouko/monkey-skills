---
name: a-mechanical-check-can-go-green-by-skipping
description: A check that fires only when BOTH sides are present goes green by SKIPPING when one side stops matching its pattern — striking through a field label made the backlog store's field-agreement check silently stop checking, and the resulting exit 0 was reported as agreement; before trusting a green on a pair-check, probe that the check actually ran
type: gotcha
sources:
  - resource: feat-us-quarterly-statement-series (US quarterly three-statement series arc, round-4 whole-branch review, 2026-08-07)
---

`scripts/backlog_index.py --validate` enforces that a backlog entry's frontmatter
`origin:`/`start:` agrees with the matching body bullet. The matcher is

```
^-\s*\**Start\**\s*(\([^)]*\))?\s*:
```

— it tolerates `**Start**` but not `~~Start~~`. When an entry superseded its start
condition, the body bullet was written as `- ~~Start: before any live
multi-filing run …~~`, striking through the LABEL along with the text. The matcher
stopped matching, `_find_body_bullet` returned `None`, and `_check_field_agreement`
hit its `if bullet_value is None: continue`.

`--validate` then exited **0** — and the fix report said the pair had been
"rewritten to match its body bullet". It had not. The field was no longer checked
at all.

**Why this is worse than a red.** A red is a demand. A green earned by skipping is
a *false receipt*: it is quoted in a fix report, it satisfies a reviewer who reruns
the command, and it retires the very question it stopped answering. Two independent
docs reviewers caught this only because both went into the validator's source and
probed `_find_body_bullet` in-process rather than reading its exit code.

**The general shape.** Any check of the form *"when both A and B exist, assert
they agree"* has three outcomes, not two: agree, disagree, and **one side stopped
being findable**. Markup around a matched label, a renamed heading, a file moved
out of the glob, a field spelled with a different key — each converts the check
into a no-op while every command still exits 0.

**What to do**

- When you change the SHAPE of something a mechanical check keys on — a label, a
  heading, a filename, a frontmatter key — assume the check went blind, and prove
  it did not. Import the checker and call its matcher on the artifact, or add the
  disagreement on purpose and confirm the check turns red.
- Never report a green as "the fix worked" for a pair-check without that proof.
  Report it as "exit 0" and say separately whether the check ran.
- Prefer marking supersession INSIDE the value (`- Start: ~~old text~~ **now
  X**`) over striking the label, so the field stays findable.

Related: [[a-no-mutation-test-cannot-baseline-off-shared-fixture-state]] — the same
family, one level down: a check that cannot fail is indistinguishable from a check
that passes.
