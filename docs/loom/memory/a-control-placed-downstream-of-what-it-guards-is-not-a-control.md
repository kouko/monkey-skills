---
name: a-control-placed-downstream-of-what-it-guards-is-not-a-control
description: A sanitizer, gate, or verifier that runs AFTER the step it is supposed to constrain protects nothing, and the code comment naming it as the mitigation is what stops anyone rechecking — mermaid's securityLevel cannot sanitize markup the browser already parsed, and a gate that judges file A while fingerprinting file B records a verdict about neither; the tell is that the comment argues the threat correctly and then sites the defence one step too late
type: practice
origin: 2026-08-19 cot-explain arc (dev-workflow 2.26.0) — two independent code reviewers found the same shape twice in one branch, both 🔴, in a skill written specifically to catch downstream-staleness
---

Both defects on that branch had the same skeleton: a real threat, correctly
identified in a comment, and a control that could not possibly address it
because of *where it ran*.

- The converter un-escaped a fence body into the page and cited mermaid's
  `securityLevel` as the reason that was safe. The browser parses `<pre>`
  content at load time, before mermaid initializes — the sanitizer is
  downstream of the injection point and never sees the payload.
- The gate read the HTML, then wrote its verdict into the markdown,
  fingerprinting the markdown. Nothing tied the two files together, so
  editing the markdown without re-rendering produced a page announcing
  `pass` for content the gate never read.

**The comment is the reason it survives review.** A control with no comment
invites the question "does this actually work?". A control with a confident
comment naming the threat answers that question in advance, and the reader
moves on. Both of these had been read by reviewers and by their own author
before someone reproduced them.

**Why:** ordering is invisible in the code's shape. The sanitizer call and
the un-escape call sit near each other and look like a pair; the check and
the stamp are two lines in one function. Nothing about the text says which
runs against which artifact, at what moment, in whose process. That has to
be reasoned about deliberately, and the deliberate reasoning is exactly what
a confident comment suppresses.

**How to apply:** for every control, name the artifact it examines and the
moment it examines it, then check that the dangerous transition happens
*after* that moment and *to that artifact*. Two questions do most of the
work:

- Does this run before or after the thing it constrains?
- Does it examine the same object that the consumer will?

When a control cannot be moved upstream, the honest move is to say in the
comment what it does NOT cover — a defence-in-depth note reads very
differently from a mitigation claim, and only one of them stops the next
reader looking. Related:
[[a-self-check-cannot-detect-its-own-staleness]],
[[a-stamp-recording-an-outcome-without-its-subject-cannot-go-stale]].
