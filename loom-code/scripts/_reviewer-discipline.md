# Reviewer output discipline — v1

These rules apply to every verdict this reviewer agent produces. They
are output discipline that the role-contract above amplifies, not
replaces. Unlike the 12-rule engineering baseline (which applies to
every plugin-level agent), this block ships ONLY in reviewer agents
(code-quality-reviewer / code-reviewer / spec-reviewer) — the
implementer does not produce verdicts and does not carry it.

## Rule R1 — Stamp every verdict with `standards_version`

At dispatch start, anchor at the repository root via
`git rev-parse --show-toplevel`, then read
`<root>/loom-code/.claude-plugin/plugin.json`. Carry the
`version` field through to your output as `standards_version`.

The standards / rubrics / checklists / evidence sources this agent
loads all ship together under one plugin version; the stamp lets
downstream readers tell whether a verdict was scored under the rules
in effect now or a prior revision.

## Rule R2 — Every output element needs an evidence citation

Every flag / finding / gap in your output must include the evidence
citation field defined by your agent-specific output schema (typically
`where:`, `artifact:`, or `spec_ref:`). The value cites `file:line`,
commit SHA, or commit SHA range.

An element without evidence is opaque — the implementer or user
cannot remediate *"naming is off somewhere."* Missing evidence flips
the whole verdict to `NEEDS_REVISION` regardless of severity. The
orchestrator treats a verdict with any opaque element as malformed.

## Rule R3 — A verdict resting on unconfirmed evidence downgrades

You may not run tests; your correctness / tests verdict rests on the
implementer's reported `test_results`, which you did not produce. When
a dimension's PASS rests on evidence you could not independently
confirm, do not emit a clean PASS for it — downgrade to
`PASS_WITH_NOTES` naming exactly what you could not verify (e.g.
"correctness rests on implementer `test_results`; not independently
run"). For the binary spec-reviewer, which has no `PASS_WITH_NOTES`
token, record the same caveat in `notes` rather than passing it
silently. Never false-pass ("can't see it → assume fine").

This downgrade sets that dimension's `dimension_scores` entry only — it
is not itself a counted 🟡 finding and does not feed the 2+ 🟡 →
NEEDS_REVISION aggregation (that aggregation counts `findings[]`
entries, each with its own `where:` citation).

## Common anti-patterns the orchestrator will reject

- Output missing the `standards_version` field — the orchestrator
  cannot date the review against a specific rubric revision. Stamp
  every verdict, including `PASS`.
- Any output element with an empty / missing evidence citation field
  (`where:` / `artifact:` / `spec_ref:`) — opaque rejection. The
  agent-specific aggregation rule below flips the whole verdict to
  `NEEDS_REVISION`.

---

**SSOT note**: this content is the canonical text. Every loom-code
reviewer agent embeds it verbatim between BEGIN/END
reviewer-discipline markers. Drift is enforced by
`loom-code/scripts/verify-drift.py`; regenerate the injected blocks
via `python3 loom-code/scripts/distribute.py`. Do not edit the
injected block in any reviewer agent file — edit
`loom-code/scripts/_reviewer-discipline.md` (this file) and re-run
distribute.

This file lives in `scripts/` rather than `agents/` for the same
reason as `_baseline.md`: Claude Code's plugin validator treats every
`.md` under `agents/` as a dispatchable agent definition (requiring
YAML frontmatter). This file is data the distribute script reads, not
a dispatchable agent.
