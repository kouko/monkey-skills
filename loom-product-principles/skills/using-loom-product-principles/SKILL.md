---
name: using-loom-product-principles
description: |
  The loom-product-principles family entry: intake + routing. Start here first when you are not sure where to begin on a new product or feature idea — checks the target repo against the loom family's on-ramp criteria, then hands off to product-principles for the actual principles-writing work. Use for 'where do I start', '不確定從哪開始', 'entry point', or a general loom-product-principles family ask.
version: 0.1.0
---

<SUBAGENT-STOP>
If you are a subagent already dispatched with an explicit role prompt, **do not** re-route through this skill. Follow the prompt you were dispatched with directly. This router is for the parent orchestrator only.
</SUBAGENT-STOP>

This is the **loom-product-principles family entry** — a thin router, not
the skill that writes the constitution. It does intake + routing, then
hands off.

## §Intake

### Step 1 — 前站檢查 (upstream check)

Check the target repo against the loom family reception's on-ramp criteria
table — the single source of truth lives in
`loom-pipeline/hooks/family-reception.md`. Reference it, do not copy its
rows here. If `docs/loom/PRINCIPLES.md` already exists in the target repo,
confirm with the user whether this station's work is already done before
proceeding.

### Step 2 — 對站檢查 (sibling-station redirect)

If the user's actual ask belongs to a different family entry, redirect
instead of proceeding here:

- A design-surface ask (UI/UX, screens, interaction flows) →
  `using-loom-interface-design`
- A spec / requirement fan-out ask (multi-state behavior, edge cases,
  acceptance criteria) → `using-loom-spec`
- A coding ask (write, change, review, or ship code) → `using-loom-code`

### Step 3 — Hand off

Once intake confirms this is the right station, hand off to
`product-principles` — the member skill that elicits the idea, drafts the
`## North Star`, and derives the 3–7 falsifiable principles into
`PRINCIPLES.md`. This entry does not do that work itself.

## What this router does NOT do

- Does **not** author `PRINCIPLES.md` itself — that is `product-principles`'s job.
- Does **not** duplicate the on-ramp criteria table — it references
  `loom-pipeline/hooks/family-reception.md` as the single source of truth.
- Does **not** auto-invoke `product-principles` — the harness invokes it
  once intake and routing confirm this is the right station.
