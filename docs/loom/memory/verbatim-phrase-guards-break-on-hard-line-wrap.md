---
name: verbatim-phrase-guards-break-on-hard-line-wrap
description: A grep/substring guard that asserts a multi-word phrase VERBATIM fails the moment an editor hard-wraps that phrase across a newline (e.g. "blast\nradius") — the file reads fine to a human but the contiguous-substring assertion misses; keep any guard-pinned canonical phrase on ONE physical line, and prefer a contiguous-match assertion over non-contiguous fragment checks
type: gotcha
origin: feat-bba-proactive-trigger-hardening (2026-07-25) — 3 of 6 SDD implementers hit it independently pinning the trigger triple
---

When a guard test asserts a canonical multi-word phrase verbatim
(`assert "≥3 trade-offs, ≥2 implementation paths, or architectural blast
radius" in text`), a hard line-wrap that splits the phrase across a
newline in the SKILL.md / card prose (`…blast\nradius…`) breaks the
contiguous-substring match even though the rendered text is correct.
Three of six implementers on the bba-hardening branch hit this
independently: RED→first-GREEN attempt failed on the triple assertion,
fixed only by reflowing the sentence so the phrase stayed unwrapped.

**Why:** the phrase is a *fact* copied verbatim into both the prose
carrier and the assertion; markdown/prose editors wrap on width, but the
substring check has no wrap-awareness. A non-contiguous guard (checking
the three fragments separately) hides the problem the other direction —
it passes even when a wrap HAS split the phrase, so it under-protects.

**How to apply:** (1) keep any guard-pinned canonical phrase on a single
physical line in the carrier — never let it wrap; (2) write the guard as
a single contiguous-substring assertion (the strong form), so a future
wrap fails loudly instead of silently passing; (3) if a phrase is too
long to keep on one line, normalize whitespace in BOTH the text and the
assertion before comparing, rather than downgrading to fragment checks.
Related: [[assertion-must-encode-the-property-it-claims]],
[[doc-string-tests-pass-while-weak-readers-misread]].
