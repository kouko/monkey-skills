---
name: dont-fix-guards-jtbd-isbn-and-5axis-names
description: Don't-fix guards — the JTBD 1997 ISBN 978-0875845852 in four-dx-coach is CORRECT (Innovator's Dilemma context, not Competing Against Luck), and the 5-axis long/short names in loom-code brainstorming (Alternatives vs Alternatives Considered) are deliberate description-vs-body usage, not drift
type: practice
origin: PR #465 (loom-* consistency audit, 2026-07-01)
---

Two audit-confirmed "looks wrong, is right" facts — do not "fix"
either:

1. **Originating example (from `four-dx-coach`, a non-loom skill;
   recorded here as the guard's concrete payload):** the
   Jobs-to-be-Done (JTBD) citation carrying the 1997 ISBN
   **978-0875845852** is CORRECT. JTBD framing is commonly
   associated with Christensen's *Competing Against Luck* (2016), so
   a 1997-looking citation reads like a misattribution to *The
   Innovator's Dilemma* — but that passage cites the idea in its
   Innovator's Dilemma (1997) disruption context, and the ISBN
   matches that book. The PR #465 audit verified it; "fixing" it to
   the 2016 book would introduce the error.
2. **loom half:** in loom-code's brainstorming skill, the 5-axis
   framework's axis names deliberately appear in two lengths — short
   forms (e.g. "Alternatives") in the skill's description field,
   long forms (e.g. "Alternatives Considered") in the skill body.
   The description is optimized for routing/trigger matching, the
   body for reading. Intended description-vs-body usage, NOT
   cross-file drift — do not unify the names.

**Why:** consistency audits hunt for the same concept spelled or
cited differently across files; a deliberate variation or a
correct-but-surprising citation is indistinguishable from drift
unless recorded, and "fixing" it introduces the very error the
audit exists to prevent.

**How to apply:** when an audit flags the four-dx-coach JTBD ISBN or
the 5-axis name variation, leave them — cite this guard. More
generally: before "fixing" an apparent inconsistency, check whether
it is a recorded deliberate choice (this store, git history, skill
comments) — a documented decision beats a symmetry argument.
