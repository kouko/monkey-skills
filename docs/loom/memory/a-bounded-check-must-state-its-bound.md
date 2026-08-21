---
name: a-bounded-check-must-state-its-bound
description: A completeness check that recognises by NAME or by PATTERN is always partial, and a partial check whose docstring promises totality is worse than no check — it licenses the next reviewer to stop looking at the exact class it was built for; state the bound in the assertion message and the docstring, name the shapes that still escape, and treat "widen the mechanism" and "size the claim" as two obligations, not one
type: practice
origin: north-star-serves-link / dissolve-direction-layer (2026-08-21) — review rounds 6, 7 and 8 each rated the then-current revision of one test file fatal, each by injecting a bare filesystem read the docstring implied was impossible
---

The same test file was defeated three times, each revision built to fix
the last:

1. **Counted `.read_text(` occurrences** against a case count. Two scripts
   had slack; a reviewer injected a bare read into the slack and 14/14
   stayed green.
2. **AST fixpoint over reachability**, claiming "an OSError can escape" was
   impossible. It walked only module-level `FunctionDef`s and a fixed
   attribute-name set, so `path.open()` — the most idiomatic Path read in
   Python — walked through, along with `os.*`, `shutil`, class methods and
   module-level code.
3. **Widened, and the claim resized** to "no RECOGNISED escape shape
   reaches `main`", with the escapes it cannot see named in the docstring.
   A reviewer then defeated the *comment* rather than the leg —
   `from os import listdir` produces an `ast.Name`, which the Name branch
   did not check against the recogniser set, while the comment claimed
   from-imports "land the same way".

**Why:** every recognition-based check draws a boundary. The boundary is
not the defect; claiming there is no boundary is. Round 6's reviewer stated
the cost exactly: *the branch's headline mechanism telling the next round
it may stop looking, on precisely the defect class it was built for.* A
check known to be partial gets read with suspicion, which is correct. A
check believed total ends the search.

**How to apply:** pair every completeness check with (a) an explicit
`## What this does and does not catch` section naming the escapes, (b) an
assertion message that repeats the bound ("no RECOGNISED escape"), and
(c) a companion behavioural check, because the two fail differently —
`except OSError: pass` satisfies a reachability analysis and fails every
behavioural case. Verify by REPLAYING the escape shapes rather than by
reading: the last real defect on that arc came from taking a reviewer's
`from os import X` experiment one variant further to `from os import X as
y`, which was still open. Related: [[a-mechanical-check-can-go-green-by-skipping]],
[[prose-shipped-with-a-mechanism-describes-the-road-not-taken]].
