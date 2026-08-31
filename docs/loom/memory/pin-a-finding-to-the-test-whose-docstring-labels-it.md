---
name: pin-a-finding-to-the-test-whose-docstring-labels-it
description: A plan's finding→test pin table built by grepping test NAMES for a plausible match is unreliable — the correct binding is the test whose own docstring self-labels the finding (e.g. a `"""F1: …"""` line), and only a reviewer checking docstrings against the pin table catches a name-based mispin
type: practice
origin: adversarial-audit-station arc, docs/loom/plans/2026-08-31-adversarial-audit-station.md — spec-reviewer caught the mispin at 5721b1fe
---

The plan's F1/F2 pin table (which regression test proves which
adversarial finding is closed) was authored by grepping test function
names for wording that looked like it matched each finding. The
mapping was wrong: a test whose name suggested it covered F1 actually
carried a `"""F1: …"""`-style label in a DIFFERENT test, and the
grep-by-name pass had pinned the wrong one. The spec-reviewer caught
it not by re-deriving the mapping from names either, but by reading
each test's own docstring label and checking it against what the pin
table claimed.

**Why:** a test's function name is chosen for readability and can
drift from what the test actually asserts; a docstring label written
at the same time as the test body is the author's own claim about
what the test proves, and is the only signal that doesn't require
re-reading the assertion logic to verify.

**How to apply:** when building a finding→test pin table, take the
`pinned by` name from the test's own self-labeling docstring (e.g. a
literal `F1:` / `F2:` prefix in the docstring), never from a name-match
grep. A reviewer verifying pins should open each cited test and check
its docstring label against the table, not just confirm the test file
exists.
