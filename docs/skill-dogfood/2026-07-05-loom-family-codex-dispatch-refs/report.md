# Dogfood report — loom-interface-design + loom-spec Codex dispatch refs (PR #497)

**Date:** 2026-07-05
**Target:** `docs/loom-family-codex-dispatch-refs` branch, commit `ac82da13` — new `claude-code-tools.md`/`codex-tools.md` reference pairs for `design-critic` (loom-interface-design) and `completeness-critic` (loom-spec).
**Method:** same design as the PR #496 dogfood — 2 real, live Codex CLI sessions (`codex exec -s read-only`, Codex 0.139.0, auth already configured) + 2 Claude Code fidelity checks (fresh dry-run subagents), one pair per plugin.

## Result: dogfood-verified, no regressions

### Real Codex — design-critic (loom-interface-design)

Correctly derived, unprompted: one combined `spawn_agent` instruction naming all 5 lenses (not 5 separate spawns), `wait_agent` → consolidate, agent type `default` (explicitly rejecting `explorer` as "read-heavy exploration... too narrow for reasoning," and `worker` as execution-focused). Correctly reproduced all 5 real lens names, their personas' rationale, and the "do not load `loom-spec:completeness-critic`" boundary rule verbatim from the actual SKILL.md content.

### Real Codex — completeness-critic (loom-spec)

Same combined-instruction / `default`-agent-type derivation. Correctly reproduced the 5 real fixed lenses with their actual personas from the file (NFR/security, policy/legal, missing object/actor, state completeness, cross-object/system-layer), and correctly flagged that the missing-object/actor lens should get "the original-requirements-only view for at least this one" — a specific, easy-to-miss detail it pulled directly from the source file rather than genericizing.

### Claude Code — design-critic fidelity

Fresh subagent reconstructed all 5 `Agent()` calls correctly: `subagent_type: "general-purpose"`, no `name:`, all 5 issued in one assistant message. All three load-bearing facts confirmed unambiguous from the two files alone. Flagged ambiguities are pre-existing properties of `design-critic/SKILL.md` itself (only 3 of 5 lenses have an illustrative example persona; artifact paths are consumer-project-specific by design) — not introduced by this PR's new reference files.

### Claude Code — completeness-critic fidelity

Same result: all 5 `Agent()` calls correctly shaped, all three load-bearing facts confirmed unambiguous. Flagged ambiguities (which lens gets the original-requirements-only view; exact prompt wording) are pre-existing under-specification in `completeness-critic/SKILL.md` itself, reasonably resolved by the subagent's own inference — not a defect in the new reference files.

## Verdict

**Dogfood-verified.** Both new reference-file pairs are legible and actionable to a real, live Codex session (not simulated) and lose no fidelity for Claude Code. No follow-up fix identified as necessary before merge.
