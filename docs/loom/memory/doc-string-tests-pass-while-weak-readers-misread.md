---
name: doc-string-tests-pass-while-weak-readers-misread
description: Tests that pin a SKILL.md's documentation STRINGS verify the words exist, not that a weak executor reads the intended semantics — three live cases shipped green-tested prose that haiku cold-readers then misread (mint-at-exhaustion inverted, cap budgets conflated, cross-plugin script path garbled); behavioral cold-read rounds on the weak tier are the only test layer that catches this class, and each fix was a few words
type: practice
origin: loop-convergence-fixes branch (2026-07-19) — 6 dogfood rounds, 59 haiku cold reads, 3 wording defects found+fixed+re-verified; fix commits 33effa0c/26db3788/65b0bf2c
---

Three SKILL.md clauses on one branch each shipped with green string-pinning
tests (the repo's standard prose-testing convention) and were then misread
by fresh haiku cold-readers given only the file and a scenario:

1. **Semantics inverted by omission**: the critic outer-cap clause said
   "stop re-running and hand back" — a weak reader concluded "do not mint
   the verdict" at exhaustion, defeating the exit-2 (never ran) vs exit-3
   (ran and blocked) distinction the verdict files exist for. The pinning
   test could not fail: every pinned string was present.
2. **Two adjacent budgets conflated**: "mirroring the 3-round cap below"
   read as a SHARED budget to a conservative reader (fails safe, but a
   round early). No string was missing; the relationship was unstated.
3. **Cross-plugin path garbled**: prose named the owning plugin in a
   sentence, but the copyable command lacked the plugin path — a reader
   reproduced the command with the wrong plugin's directory.

Each fix was ≤15 words plus a tightened assertion; each was re-verified by
a fresh cold read on the same scenario, and two later all-new-material
rounds stayed clean (loop-until-dry, K=2).

**Why:** string-pinning tests and weak-reader comprehension test different
things — presence of words vs the reading a cold executor actually forms.
The gap class is invisible to every static layer (the strings ARE there)
and only surfaces when a weak model acts on the text. Sibling entries:
[[prose-only-enforcement-dies-on-weak-executors]] (validator-checked
survives, prose-only dies) and
[[cold-read-and-adversarial-review-catch-different-failures]]
(comprehension vs robustness); this entry adds the third axis —
string-tested prose can still fail comprehension.

**How to apply:** when shipping loop/gate/cap semantics carried by prose,
budget one behavioral dogfood round: fresh weak-tier agents, real
scenarios (include a tempting shortcut), zero hints, "what do you do next
+ quote the deciding sentence". Grade the ACTION, not the recitation. A
misread = the text is wrong (fix wording, not the reader); re-verify the
fix with a fresh cold read on the same scenario, then run new-material
rounds until two consecutive rounds are clean.
