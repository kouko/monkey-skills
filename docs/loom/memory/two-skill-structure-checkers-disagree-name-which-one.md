---
name: two-skill-structure-checkers-disagree-name-which-one
description: This repo enforces skill folder structure with TWO tools that do not agree — `.claude/hooks/validate-skill-folder-structure.sh` rejects only nested subdirectories (`find -mindepth 2 -type d`) while `scripts/check-skill-structure.py` additionally rejects unexpected top-level files as CHK-SKL-012 — so "the skill-structure checker forbids X" is an ambiguous claim that a reviewer will probe against whichever one they reach first and disprove; always name the tool and the rule id
type: reference
origin: 2026-08-19 cot-explain arc (dev-workflow 2.26.0) — a docs reviewer returned STILL_BLOCKING on a sentence saying "the skill-structure checker rejects a trigger-eval.json at a skill root"; they ran the hook, got exit 0, and were right
---

Two tools in this repo enforce the skill folder convention, with different
rules:

| Tool | What it rejects | Runs |
|---|---|---|
| `.claude/hooks/validate-skill-folder-structure.sh` | Nested subdirectories only — `find "$skill_root" -mindepth 2 -type d`. A loose file at a skill root passes. | PostToolUse on Write/Edit |
| `scripts/check-skill-structure.py` | The above, plus unexpected top-level files — `CHK-SKL-012` | Invoked with a plugin dir; CI |

They genuinely disagree, and the disagreement is live rather than
theoretical: `python3 scripts/check-skill-structure.py dev-workflow`
currently FAILs `brief-before-asking` and `distill-sessions`, both for a
shipped `trigger-eval.json` that the hook happily allowed through when those
skills were written.

**Why this bites:** an unqualified sentence — "the skill-structure checker
forbids X" — reads as one checkable claim and is two. A reviewer verifying it
picks whichever tool the phrase suggests to them, and can honestly disprove a
statement that is true of the other one. That cost a review cycle here, and
the cost lands on the author, because the reviewer's probe was correct.

**How to apply:** in prose, name the tool and the rule id
(`scripts/check-skill-structure.py` … `CHK-SKL-012`), not the category. When
the two disagree about the case you are describing, say so — a reader who
only ever runs the hook will otherwise conclude the constraint does not
exist. And when adding a file to a skill root, run the *python* checker: the
hook passing means nothing about CI.

Open: whether the two should be reconciled, and which way. The hook cannot
see top-level files cheaply on a single-file edit event, so the split may be
deliberate; nobody has recorded a decision either way. Related:
[[a-guard-whose-marker-restates-the-artifact-can-never-fire]],
[[error-message-text-is-not-the-rules-statement]].
