---
name: a-prose-scanner-meets-its-own-vocabulary-first
description: A check that scans prose for keywords will meet the toolchain's OWN vocabulary before it meets a user's — severity labels, verdict tokens, field names and status words are prose to a scanner, so the first real run fires false positives on the very machinery that dispatched it; exercise every new prose check against a real artifact of the system it ships inside before trusting its signal
type: gotcha
origin: 2026-08-12 adjudication-view arc (loom-code 0.77.0) — the modality check's first real input was the arc's own whole-branch verdict
---

A modality check was built to compare an English source unit against its
Chinese rendition: source `should` must map to 應, `must` to 必須, and so
on. It was tested against hand-written bilingual fixtures and shipped
green.

Its first real input was this arc's own review verdict — and it fired
five false-positive warnings, all on the same token: the severity label
**`should-fix`**. The scanner has no idea that `should-fix` is a
machine enum rather than an English obligation; to a keyword scan it is
just the word "should" followed by a hyphen. The same hazard sits in
every neighbouring vocabulary the toolchain writes into prose:
`must`-shaped field names, `no`/`not` inside flag names like
`--no-verify`, `may` inside a quoted enum.

**Why:** hand-written fixtures are written by someone thinking about
the linguistic phenomenon, so they contain natural prose. The artifacts
the check actually runs on are produced by the surrounding machinery
and are saturated with its vocabulary — verdict tokens, severity
labels, field keys, CLI flags. That vocabulary is statistically far
denser in the real input than in any fixture, so a scanner's real-world
false-positive rate is dominated by material no fixture author would
think to write.

**How to apply:** before trusting a new prose-scanning check's signal,
run it once against a genuine artifact of the system it ships inside —
a real verdict, a real plan, a real close-out report — not only against
authored fixtures. Treat every hit on a machine token as a spec bug in
the scanner, and encode the exclusion (hyphen compounds, backticked
spans, flag context) as a test at that moment. A check whose first
production run must be triaged by a human is a check nobody will read
the second time.

Related: [construction-guaranteed-invariant-proves-nothing](construction-guaranteed-invariant-proves-nothing.md)
(a green signal whose greenness came from the setup, not the subject).
