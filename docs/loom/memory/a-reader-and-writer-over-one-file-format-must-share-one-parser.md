---
name: a-reader-and-writer-over-one-file-format-must-share-one-parser
description: When one task ships a tolerant reader for a file format and a later task ships a stricter writer for the same format, inputs the reader accepts silently fall through the writer — the write reports success and changes nothing; reader and writer must call one shared span/parse routine, and a writer that cannot locate its target must fail loud, never return quietly
type: practice
origin: think-orbit Part 1 whole-branch review (2026-08-18) — the frontmatter loader accepted a delimiter line that strips to `---` (trailing whitespace) while `break`'s rewriter required an exact `---\n` and returned None on mismatch; `check` passed, `break` printed `stale: …` and exit 0, and the assumption stayed `open`; both per-task triads had PASSed — only the branch-scope panel saw the seam
---

Two functions parsed the same frontmatter delimiter with different
acceptance rules because they were written in different tasks against
different tests. Every input that lived in the gap between the two rules
produced a successful-looking no-op in the only verb that mutates data.

**Why:** per-task review grades each function against its own spec and
cannot see that the other function disagrees; the defect exists only at
the seam. A tolerant reader plus a strict writer is the specific shape
that fails silently — a strict reader plus a tolerant writer would at
least refuse the file up front.

**How to apply:** (1) when a later task adds a writer for a format an
earlier task already reads, make the writer call the reader's span/parse
routine (extract it if needed) rather than re-deriving the grammar with a
new regex; (2) a writer that cannot find its anchor returns an error the
caller turns into a non-zero exit — never a silent `return`; (3) plan all
rewrites before performing any so a failed anchor leaves zero partial
writes; (4) at whole-branch review, ask explicitly "which pairs of
functions parse the same bytes?" — that question is what surfaced this.
