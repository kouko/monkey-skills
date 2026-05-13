[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

# Using Systems Thinking Toolkit (Router)

Intent-uncertainty router for the `systems-thinking-toolkit` plugin.

## When to use

Use `/systems-thinking-toolkit:stt` when:

- You don't know which method fits your situation
- Something is spiraling, oscillating, or hitting a ceiling
- You're stuck in a vicious cycle / death spiral / boom-and-bust
- You want to map a tangled situation but are unsure which method to reach for

NOT for when you've already named a specific method (`cld-craft`, `cld-archetypes`, `cld-overlay`, `simulation-modeling`, `strategy-lever-and-cascade`, `team-mental-model`, `manager-personality-quadrant`) — invoke the per-skill command directly.

## What you get

- A one-question intent table that routes to one of 7 functional skills: `cld-craft`, `cld-archetypes`, `cld-overlay`, `team-mental-model`, `simulation-modeling`, `strategy-lever-and-cascade`, `manager-personality-quadrant`.
- EN + zh-TW + JA trigger phrases per row (added in v0.5).
- Explicit prerequisite callout for the "I have a CLD" section (v0.4 patch).
- Default fallback to **`cld-craft`** for genuinely unclear cases.

## Boundaries

- NOT for users who already know which method they want — invoke the per-skill command directly.
- NOT a substitute for the methods themselves — the router recommends and hands off; it does NOT explain the method.
- NOT for combining multiple methods in one workflow — pick ONE; the user can re-invoke for the next method.

## Default fallback

When intent remains unclear after the narrowing questions, default to **`cld-craft`**. It is the carry-1 prose→CLD translator that downstream skills consume; producing the diagram first is rarely wrong even if a different downstream skill is eventually needed.

## See also

- Full routing table: [`SKILL.md`](SKILL.md)
- Plugin overview: [`../../README.md`](../../README.md)
- Full skill map: [`../../INDEX.md`](../../INDEX.md)

## Source

This entry skill is monkey-skills-internal (mirrors the `using-philosophers-toolkit` pattern). The 7 routed functional skills are distilled from Dennis Sherwood, *Seeing the Forest for the Trees* (Nicholas Brealey, 2002).
