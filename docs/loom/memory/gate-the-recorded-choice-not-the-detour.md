---
name: gate-the-recorded-choice-not-the-detour
description: When a rule says "recommend X once, record the user's choice, proceed either way", the recommendation degrades into a status bullet and the agent records its own default as the answer (measured 8 agent-default vs 3 explicit-user over 86 briefs) — mechanize the CHOICE, not the detour: a canonical brief line with `pending` until the user answers, a standalone ask, a repo-level standing-choice file so a decided row is never re-asked, and a checker at plan-commit that refuses any non-canonical wording as unresolved
type: practice
origin: branch onramp-explicit-choice-gate (2026-08-18) — on-ramp explicit-choice gate arc; evidence docs/loom/specs/2026-08-18-onramp-explicit-choice-gate.md §Problem, docs/loom/audits/2026-08-18-onramp-choice-gate-fire-rate.md; trigger case strategy-dag session (agent wrote "使用者未反對" for a choice the user never saw)
---

The family reception's on-ramp rule ("surface ONCE, record the user's
choice, then proceed either way") was prose-only and produced the exact
failure it named: under brief-before-asking's one-decision-per-ask
pressure the recommendation slid into a "現況" bullet inside another
briefing, and the agent wrote "direct — per repo precedent" as if the
user had answered. Measured over the 86 briefs carrying the line:
71 not-fired, 8 fired-with-agent-default, 3 fired-with-explicit-user
choice — the default was the norm, not the exception.

Two things made the failure invisible: the brief line was write-only
(specified in one skill's prose, read by nothing), and "product-shaped"
— the trigger — cannot be machine-decided, so the trigger itself could
never be gated. The durable shape that works:

- gate the *choice*, not the *action* — the user saying "direct" IS the
  waiver; no separate waiver file;
- one canonical grammar (`not fired — …` / `pending` / `fired: rows n —
  user chose …` / `fired: rows n — standing … (DIRECTION.md)`), any other
  wording = unresolved, never pass (lookalike lesson);
- write `pending` before asking; the ask is standalone (its own
  question), never a bullet in a bigger briefing;
- a repo-level standing-choice section (DIRECTION.md) so a decided row
  is answered once per repo, not per arc — the measured "per repo
  precedent" habit made honest;
- the checker runs where both hosts fire (writing-plans intake +
  Bash-matched git-guard on plan commit), loud fail-open on every path
  it cannot evaluate.
