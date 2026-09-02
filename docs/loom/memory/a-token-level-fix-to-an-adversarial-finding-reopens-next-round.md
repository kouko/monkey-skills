---
name: a-token-level-fix-to-an-adversarial-finding-reopens-next-round
description: When an adversarial reviewer defeats a gate with one example, fixing that example (a keyword, a substring, a regex branch) reopens the class next round; the fix that survives replaces the judgement with structure (execute the thing itself, count characters not words, strip every markdown prefix) or hands the judgement to the reviewer lens explicitly — and the same finding id surviving a third round is the signal to change design, not patch again
type: practice
origin: simple-loom-flow (2026-09-03) — `spec.ui-flows-recompute` went N/A → synonyms → arrow char → fence/prefix bypass → CJK false-blocks across W2 rounds 2–5; the structural rule (no keyword list, ≥4 visible chars each side of an arrow, fences/comments/indented code stripped) is what closed it
---

Two checker rules in this change followed the same arc: the reviewer
found a bypass, the implementer closed exactly that bypass, the next
reviewer found the neighbouring one. The UI-flows rule collected a
keyword list of "nothing" spellings in two languages before anyone asked
whether a checker should be guessing at meaning at all.

The rule that held has no keyword list: strip fenced code, indented code,
HTML comments and every leading markdown marker, then require one line
with an arrow and at least four visible characters on each side —
counted per character so Chinese and Japanese, which have no word
breaks, are not falsely blocked. Whether the flow is TRUE is the reviewer
lens's job, and the rule's `--list-rules` description says so.

Dispatch packets now phrase adversarial findings as classes ("any shell
form whose exit code does not reflect the artifact") and require the
implementer to add ≥5 variants to the tests, not just the reviewer's one.
