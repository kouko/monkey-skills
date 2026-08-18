---
name: break-assumption
description: |
  When a premise breaks or the situation changes — mark the assumption broken, let the load-bearing chain go stale, and hand the user the impact view. The agent only raises its hand; the user declares. Normally reached via using-think-orbit; fires on 假設破了 / 情況變了 / 前提不成立了 / "assumption broke" / "situation changed".
source_language: en
tags: [decision-making, chain-of-thought, dag, assumptions, part-1-draft]
---

# Break assumption — the moment a premise breaks

This is the script for one moment: a premise the graph stands on no
longer holds. You normally arrive here from `using-think-orbit`, which
already resolved `<root>`. If you got here without one, ask for it once.

**You may only raise your hand. The user declares.** When something in
the conversation matches an assumption's `breaks_if`, say so and ask:
"this sounds like `<assumption-id>` may have broken — do you declare it
broken?"

You never declare a break on your own, however obvious it looks.
Marking a premise dead rewrites the user's own reasoning, and that
authorship is theirs.

Raise your hand on the explicit cues: 「假設破了」「情況變了」
「前提不成立了」 / "assumption broke" / "situation changed". Raise it
also on the silent cue — a fact stated in passing that matches a
`breaks_if` line you have on disk.

## Identify which assumption

If the user named one, use it. Otherwise read `<root>/assumptions/*.md`
and list the ones with `status: open` — `id`, `statement`, and
`breaks_if`, one line each — then ask which one broke. Keep the list to
what is open; a broken or confirmed assumption is not a candidate.

If nothing on that list matches what happened, say so plainly: an
unnamed premise cannot be "broken", because it was never tracked.
Offer to write it as a new assumption in `thinking-session` instead, so
the next time it moves the graph can see it.

## Run the break

Once the user declares, run exactly:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dag.py break <root> <assumption-id>
```

What it does: rewrites the assumption's `status` to `broken`; rewrites
`status: stale` on every node reached through a chain whose every hop is
`load_bearing: true`; writes an impact view under `<root>/views/`; and
prints three lines — `stale: <ids>`, `weakened: <ids>`, and
`impact view: <relative path>`.

Take the view's filename from that third line, never by computing it.
The name is `views/impact-<id>.md` with every character of the id
outside `[A-Za-z0-9_-]` replaced by `_`, so an id with a slash, a space,
or CJK does not spell its own filename.

What it does **not** do: a node reached only through a non-load-bearing
hop is reported on the `weakened:` line and its file is left untouched.
And it recomputes nothing — no conclusion is rewritten, no branch is
re-argued, no DECISION is reopened. The graph is marked, not rethought.

If it prints `assumption <id> not found` and exits 1, the id is wrong —
re-list the open assumptions and ask again. Do not guess a nearby id.

## Then offer exactly two follow-ups

One short exchange, not a menu. Ask which of these two the user wants:

- **direct dependents only** — relay the `stale:` ids from stdout in
  plain words ("these now rest on a broken premise"), and the
  `weakened:` ids as "weakened, not stale — still standing, just less
  supported".
- **full impact** — tell them to open the path `break` printed on its
  `impact view:` line (`views/impact-<sanitized-id>.md`, the id's
  non-`[A-Za-z0-9_-]` characters replaced by `_`).
  **You never read a file under `views/`** — it is a lossy, human-only
  rendering. If they want it regenerated, run
  `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dag.py impact <root> <assumption-id>`,
  which prints the same `impact view:` line.

Then stop. What to re-examine is the user's call, not yours. Stale nodes
stay stale until the user rewrites them in `thinking-session` or rules
that they still hold — in which case set `status: current` on those node
files, by hand or through `thinking-session`.

## Close the exchange

Regenerate the view and re-run the gate:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dag.py render <root>
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/dag.py check <root>
```

`check` is silent on pass — say nothing. On failure, relay each line in
plain words and fix the file. Then hand back to `thinking-session` if
the user wants to keep going, or end the sitting there.

## The reverse moves

An assumption can also settle the other way. When the user says a
premise is now confirmed, edit that file to `status: confirmed` — no
propagation, nothing downstream changes, a confirmed premise was
already being relied on.

When the user says they were wrong about the break, set the assumption
back to `status: open` and hand-edit the affected node files from
`stale` to `current`. In Part 1 that reversal is manual: there is no
un-break verb, so say so rather than implying the tool will undo it.

## The hard limit — say it once

The assumption graph only protects premises that were **named**. An
unnamed one fails silently: nothing marks it, nothing goes stale, and
the conclusion keeps standing on air. That is exactly why
`thinking-session` asks 「這條路踩在什麼上面？」 every time a branch
opens — this skill can only work with what that moment captured.

## Pointers

- `${CLAUDE_PLUGIN_ROOT}/skills/thinking-session/references/node-schema.md`
  §assumptions — the field SSOT: `id`, `status` (`open` / `broken` /
  `confirmed`), `statement`, `breaks_if`, `branch`.
- `thinking-session` — writing and rewriting nodes and assumptions.
- `using-think-orbit` — root resolution, state detection, routing.
