---
name: 2026-08-10-yellow-findings-should-default-to-debt-not-revision-loops
description: relax the 2+🟡→NEEDS_REVISION aggregation so 🟡 findings ship as documented debt at any count and only 🔴/instruction-class findings open a revision loop — mechanical count rule, weak-model-safe
status: OPEN
origin: 2026-08-10 review-cost discussion — review→fix loops in both the dev repo and the external consumer repo were dominated by 🟡-class conventional findings, each forcing a fix + re-verdict round
start: user authorizes the review-cost-reduction arc, or the next arc where a 🟡-driven revision loop demonstrably burns a round — whichever comes first
---

- Start: user authorizes the review-cost-reduction arc, or the next arc where a 🟡-driven revision loop demonstrably burns a round — whichever comes first

- Origin: 2026-08-10 review-cost discussion — review→fix loops in both the dev repo and the external consumer repo were dominated by 🟡-class conventional findings, each forcing a fix + re-verdict round

- Current contract: PASS_WITH_NOTES (exactly one 🟡) auto-proceeds
  carrying the 🟡 as debt, but **2+ 🟡 aggregate to NEEDS_REVISION** and
  open a revision loop (requesting-code-review verdict rules; SDD's
  resolution table; finishing Step 3). Bounded round caps exist at every
  station, but reaching a cap still costs the rounds.

- The proposal: 🟡 findings default to **documented debt at any count**
  (PR body + close-out report), and only 🔴 findings — or docs-review's
  instruction-class — open a revision loop. A reviewer who believes a
  specific 🟡 must not ship escalates it to 🔴 with the reason; that
  keeps the escape valve while making the default non-looping.

- Why a count rule and not prose judgment: the weak-model caveat
  precedent (需判斷的散文死、可查動作的散文活) — "stop when good
  enough" as prose would be rationalized away; "🟡 never loops, 🔴
  always loops" is mechanical and holds at any model tier.

- Evidence: dev repo 2026-08-10 cheap-hardening batch — the one 🟡 that
  was fixed in-flight cost an extra fix + delta-re-verdict cycle that
  the written PASS_WITH_NOTES rule already said to skip; consumer-repo
  sessions show 2-4 round per-task loops dominated by label/range/format
  🟡s. History check before legislating: sample past 2+🟡 NEEDS_REVISION
  verdicts and confirm how many 🟡s in practice turned out load-bearing
  (the falsified-neighbor carriers were 🟡-tagged) — the arc must weigh
  that tail before relaxing.

- Blast radius when the arc opens: requesting-code-review verdict rules,
  SDD §Verdict resolution, finishing Step 3, docs-review aggregation —
  four wording sites plus their pin tests; one plugin version bump.
