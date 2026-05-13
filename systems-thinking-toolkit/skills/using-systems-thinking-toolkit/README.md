[English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

# using-systems-thinking-toolkit

Entry / router skill — finds the right systems-thinking method for your situation by asking ONE question: "What are you trying to do?"

## When to use

- You suspect a systems-thinking method applies but don't know which one to invoke.
- The user describes a vague pattern ("things keep getting worse", "we keep doubling spend but revenue won't move") — let the router classify before reaching for a specific skill.

## How to invoke

`/systems-thinking-toolkit:stt`

(There is no direct "stt" skill — the slash command invokes this router skill.)

## What you get

- A one-question intent table that routes to one of the current 7 functional skills (cld-craft, cld-archetypes, cld-overlay, team-mental-model, simulation-modeling, strategy-lever-and-cascade, manager-personality-quadrant). v0.6 absorbed `innovaction-martian-test` into strategy Step 5; v0.4 absorbed loop-and-link-primitives into cld-craft Step 11.
- Honest "don't combine multiple methods" rule + explicit "default to cld-craft" fallback for unclear cases (cld-craft is the carry-1 prose→CLD producer that most downstream skills consume).

## Boundaries

- NOT for users who already know which method they want — invoke the per-skill command directly.
- NOT a substitute for the methods themselves — the router recommends and hands off; it does NOT explain the method.
- NOT every problem needs systems thinking — if no method fits, the router says so honestly.

## Reference

- Full router logic: [SKILL.md](SKILL.md)
- Full plugin map: [`../../INDEX.md`](../../INDEX.md)

## Source

This entry skill is monkey-skills-internal (mirrors `using-philosophers-toolkit` pattern). The 9 routed skills are distilled from Dennis Sherwood, *Seeing the Forest for the Trees* (Nicholas Brealey, 2002).
