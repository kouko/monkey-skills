# Dogfood report — loom-code host-neutral SKILL.md rewrite + codex-tools.md re-binding

**Date:** 2026-07-05
**Target:** loom-code branch `docs/loom-code-named-agent-gotcha` (PR #496), commit `8ddaee4d` — the rewrite that removed literal Claude-Code `Agent()` syntax from 4 SKILL.md bodies and added Codex re-binding guidance (`spawn_agent`/`wait_agent`/`close_agent`) to `codex-tools.md`.
**Method:** targeted follow-up to the earlier §A1 dogfood (2026-07-04). Two probes: (1) **real, live Codex CLI sessions** (`codex exec -s read-only`, model auth already configured locally, Codex 0.139.0) reading the actual current file content and describing their dispatch plan — not a simulated/dry-run subagent this time, an actual Codex model; (2) Claude Code regression check (2 fresh dry-run subagents) confirming the rewrite didn't lose fidelity versus the pre-rewrite literal-syntax version.

## Result: dogfood-verified, no regressions, Codex re-binding confirmed legible to real Codex

### Probe 1 — real Codex CLI, single dispatch

Prompt: read `requesting-code-review/SKILL.md`'s dispatch step + `codex-tools.md`'s re-binding subsection, describe the dispatch plan (dry run, no real spawn).

Codex correctly derived, unprompted, from the actual files:
- `spawn_agent` → `wait_agent` → `close_agent`, explicitly noting "Codex has no Claude-style blocking/non-blocking toggle."
- The exact role identifier (`loom-code:code-reviewer`) and role-anchor requirement ("You ARE the reviewer" verbatim).
- The explicit-trigger constraint: *"I would frame this as an explicit spawn instruction, not as a hidden autonomous skill step... The skill text alone saying 'dispatch a code-reviewer' is not treated as a silent background spawn."*
- Correctly distinguished Codex's `name` (reusable TOML profile) from a per-dispatch label, and correctly noted no confirmed Codex-native plugin-bundled agent profile exists yet.
- Even correctly cited the downstream `loom_gate_markers.py review-pass --verdict-file` minting step from the SKILL.md.

### Probe 2 — real Codex CLI, parallel dispatch

Prompt: read `dispatching-parallel-agents/SKILL.md` + `codex-tools.md`'s "Parallel fan-out" subsection, describe fanning out 3 implementers.

Codex correctly derived: **one combined explicit multi-agent instruction naming all 3 targets**, not 3 separate Claude-Code-style concurrent tool calls — matching exactly what `codex-tools.md` documents (citing the official manual's own "spawn one agent per point, wait for all" example). Produced a concrete worked instruction template unprompted.

### Probe 3 — Claude Code regression, single dispatch

Fresh subagent reconstructed the correct `Agent({subagent_type: "loom-code:code-reviewer", description: ..., prompt: ...})` call, unnamed, with the role anchor — all three load-bearing facts preserved. One legitimate (pre-existing, not a new regression) observation: assembling the full prompt string requires combining step 2 + the cross-skill-contract table + `claude-code-tools.md`, since neither the old nor new SKILL.md ever inlined a byte-exact prompt string (`<branch + diff body>` was always a placeholder).

### Probe 4 — Claude Code regression, parallel dispatch

Fresh subagent correctly reconstructed "3 separate `Agent()` calls in one assistant message" — but explicitly noted this fact is **only** resolvable by combining `dispatching-parallel-agents` §3 (host-neutral invariant) with `claude-code-tools.md`'s "Parallel fan-out" subsection (the concrete "same assistant message" mechanism); §3 alone is intentionally a stub. This is the disclosed, intended tradeoff of the host-neutral design (matches `obra/superpowers`'s own pattern), not an accidental information loss — but it is a genuine "two-file read is now required, one-file was sufficient before" cost, worth knowing.

## Verdict

**Dogfood-verified.** The rewrite achieves its goal on both fronts: (a) a real, live Codex session — not a simulation — correctly and unprompted reconstructs the intended `spawn_agent`/`wait_agent`/`close_agent` flow and the correct parallel-fan-out framing from the actual current file content; (b) Claude Code loses no load-bearing information, at the cost of requiring the reader to combine the skill body with its host's reference file (an intentional, disclosed design tradeoff, not a defect). No follow-up fix identified as necessary before merge.
