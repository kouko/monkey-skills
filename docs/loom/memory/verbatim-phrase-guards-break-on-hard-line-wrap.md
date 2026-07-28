---
name: verbatim-phrase-guards-break-on-hard-line-wrap
description: A grep/substring guard that asserts a multi-word phrase VERBATIM fails the moment an editor hard-wraps that phrase across a newline (e.g. "blast\nradius") — the file reads fine to a human but the contiguous-substring assertion misses; keep any guard-pinned canonical phrase on ONE physical line, and prefer a contiguous-match assertion over non-contiguous fragment checks. The same wrap defeats verbatim EDITING: a str.replace/Edit whose target spans a newline silently no-ops, and a verification grep written the same way confirms the false success — normalize whitespace on BOTH sides before editing AND before verifying
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
**A second consequence, added 2026-07-28 — the wrap also defeats verbatim
EDITING, and the obvious verification inherits the blindness.** A
`str.replace` / Edit whose target phrase spans a hard wrap matches nothing
and **fails silently** — `str.replace` returns the string unchanged rather
than raising — so the edit reports success. If the follow-up check is a
`grep` for the same phrase, it cannot match across the newline either, and
therefore CONFIRMS the false success. Observed on
`docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md`: a
seven-rounds→six-rounds correction no-opped and its verification grep
reported the old wording gone. Two rules follow: assert the replacement
count (`assert t.count(old) == 1` before replacing, or use a
whitespace-tolerant regex), and run the verification against
`re.sub(r"\s+", " ", text)` so a wrap cannot hide either the old string or
the new one.

Related: [[assertion-must-encode-the-property-it-claims]],
[[doc-string-tests-pass-while-weak-readers-misread]].
