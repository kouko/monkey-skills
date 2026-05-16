# Codex CLI — tool name mapping (Phase 2.5 ship target)

> **Status**: skeleton. Full mapping fills out in Phase 2.5 when Codex CLI variant ships (see [`../../../ROADMAP.md`](../../../ROADMAP.md) §Phase 2.5).
>
> Until then, this file documents what `code-toolkit` currently knows about the Codex CLI tool surface; gaps are marked `TBD`.

## Skill invocation

```
skill <skill-name>             # Codex CLI shape (verify in Phase 2.5)
skill <plugin>:<skill-name>    # plugin-scoped — TBD
```

Tracked open question: TQ-3 (Codex CLI hook JSON shape compatibility with Claude Code) — see `../../../TECH-SPEC.md` §9.

## Subagent dispatch

`TBD` — Codex CLI's subagent surface verifies in Phase 2.5. `subagent-driven-development` prompts are written in plain Markdown specifically so they re-bind cleanly when Codex's exact dispatch shape is settled.

## File operations

`TBD` — Codex CLI exposes Read / Write / Edit primitives but exact tool names may differ. Phase 2.5 audit will document the mapping.

## Shell

`TBD`

## Notes

- The `hooks/session-start` bash script emits **three** JSON keys to be portable across Claude Code (`hookSpecificOutput.additionalContext`), Codex CLI (`additional_context`), and any mixed-shape host (`additionalContext`). See [`../../../TECH-SPEC.md`](../../../TECH-SPEC.md) §2.3.
- Phase 1 only ships Claude Code; this Codex manifest path is a placeholder.
