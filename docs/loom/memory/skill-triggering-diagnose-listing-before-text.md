---
name: skill-triggering-diagnose-listing-before-text
description: Skill under-firing recipe — diagnose the live listing first (host evicts least-used descriptions over the ~1% budget), fix with an entry router + repositioned descriptions (routers survive eviction; CJK keyword stuffing is A/B-refuted), measure with a corpus A/B on the firing harness
type: practice
origin: research-skill-r2 branch (research-toolkit triggering + dogfood, 2026-07-06)
---

When a plugin's skills "rarely auto-trigger", the defect is usually NOT
the description wording: Claude Code drops least-used skills'
descriptions from the system-prompt listing once total descriptions
exceed ~1% of context (official; raisable via
`skillListingBudgetFraction`), and a name-only entry cannot be
semantically routed to. research-toolkit's fix that measurably worked:
a `using-<family>` entry router (fired 2/2 in both A/B runs while
sibling members stayed evicted) + repositioning vs the host built-in by
positive specificity, verified by a 16-record 中/日/英 corpus driven
through `loom-code/scripts/loom_firing_harness.py` (family fires
2/13 → 5/13, zero over-fire). CJK keyword stuffing was NOT part of the
fix — the house 51-probe A/B (PR #426/#428/#429) shows it changes
nothing; keep at most one representative CJK trigger.

**Why:** description rewrites are the visible knob, so sessions reach
for them first and burn effort where the routing signal never arrives;
the listing, the built-in competitors, and the router are where firing
is actually decided.

**How to apply:** (1) inspect the LIVE session listing for name-only
entries before touching any description; (2) if evicted, add/route
through the family's `using-*` router and keep descriptions within the
house standard; (3) reposition against host built-ins by what only your
skill offers, never by fighting for the generic phrasing; (4) prove the
change with a two-run corpus A/B (routing is non-deterministic — never
conclude from one run); (5) environment-level residual (eviction,
inline answering) is fixed machine-side, not with more text.
