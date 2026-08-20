---
name: 2026-07-04-mechanical-gates-v2-candidates-loom-code-0-23-0-follow-ups
description: Mechanical-gates v2 candidates (loom-code 0.23.0 follow-ups)
status: open
origin: PR #492 final verdict (2 🟢 next-touch) + its Decision trailers
start: first fatigue evidence from daily use of the push gate, or next git-guard touch — whichever comes first
---

- Start: first fatigue evidence from daily use of the push gate, or next
  git-guard touch — whichever comes first
- Origin: PR #492 final verdict (2 🟢 next-touch) + its Decision trailers
- What: (a) waiver `scope` field checked on the read side (single-scope
  today); (b) git-guard docstring limitations list gains the
  `git -c core.hooksPath` route; (c) **patch-id relaxation** of the
  strict-HEAD-sha review marker — today ANY post-verdict commit forces
  re-review or waiver, which is correct for content changes but costly
  for message-only amends; relax to diff patch-id match if re-review-on-
  amend proves too expensive. First candidate friction datum
  (2026-07-04): docs-only microbranches face the same full
  review-or-waiver cost as code branches.
