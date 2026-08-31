---
name: a-pin-that-cannot-see-markdown-reshapes-the-prose-it-pins
description: A prose-pinning regex that cannot match through a markdown code span or emphasis marker does not fail loudly — the author, seeing the RED, quietly drops the backticks from the sentence so the pin passes, and the artifact ends up spelling one term two ways; the defect is in the helper's tokenisation, so widen the helper to tolerate glued markdown and restore the prose, never bend the sentence to the regex
type: gotcha
origin: goal-cerate-r2 (goal-create Stop-when repair, 2026-08-31) — three implementers in one arc each hit `_negation_binds` refusing "never a `Stop-when` branch" because `\s+\b` cannot precede a backtick, and each shipped the sentence bare; the whole-branch docs arm then flagged the bare spelling as an inconsistency, and the code arm found a sibling copy of the same helper missing the trailing `\b`, so `never … asked` satisfied a check for `never … ask`
---

The negation-binding helper this repo sanctions (`\bnever\b\W*(?:\s+\S+){0,n}\s+\b<target>\b`)
was written for plain words. Put the target inside a markdown code span
and the `\b` between a space and a backtick is not a word boundary, so
the match fails. Nothing tells the author *why* — the RED just says the
obligation is not stated — and the cheapest way to GREEN is to remove
the backticks. Three implementers in one arc did exactly that, one after
another, and the artifact left the branch spelling `Stop-when` two ways
in the same paragraph. A reviewer then had to spend a finding on the
inconsistency the test had manufactured.

**Why:** a pin's job is to hold a sentence's *meaning* still; when its
tokenisation is narrower than the prose conventions the file already
uses, it starts legislating typography instead, and the author cannot
tell the two apart from inside a failing test. The same class showed up
in the opposite direction on the same arc: a second copy of the helper
without the trailing `\b` accepted `asked` for `ask`, so an inverted
sentence ("may stop to ask … never reuse an asked question") passed a
never-asks check. Both are the helper's boundaries being wrong, not the
prose.

**How to apply:** when a pin fails on a sentence that plainly states the
obligation, suspect the helper before the sentence. Tolerate the file's
own markdown at the seam (`\s+[`*_]*\b<target>\b`), keep a word boundary
on BOTH ends of the target, and keep exactly one copy of the helper per
skill — a divergent sibling copy is how the weaker semantics reach the
next test author unannounced. Then put the backticks back.
