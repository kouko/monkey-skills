# Reviewer output discipline — v1

These rules apply to every verdict this reviewer agent produces. They
are output discipline that the role-contract above amplifies, not
replaces. Unlike the 12-rule engineering baseline (which applies to
every plugin-level agent), this block ships ONLY in reviewer agents
(code-quality-reviewer / code-reviewer / spec-reviewer /
docs-reviewer) — the implementer does not produce verdicts and does
not carry it.

Where docs-reviewer is the routing target for authored prose, that
routing is scoped to contract-class `.md` only — see
`requesting-code-review/SKILL.md` §"Classification: contract-class vs
record-class"; record-class prose is review-exempt from this routing.

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

Every finding / gap in your output must include the evidence
citation field defined by your agent-specific output schema (typically
`where:`, `artifact:`, or `spec_ref:`). For source artifacts, every
citation pairs a file path plus an anchor — a verbatim string or stable
heading in the cited file. Select the anchor by artifact type: prose uses a
stable heading or distinctive phrase; code uses a function, class, or method
signature, a constant, or a distinctive message; config/data uses a key path
plus a distinctive value fragment. A line number is optional precision,
required only when the anchor alone is ambiguous (the string occurs more than
once in the file). A commit SHA or commit SHA range is also a valid locator
for revision-history evidence.

An element without evidence is opaque — the implementer or user
cannot remediate *"naming is off somewhere."* Missing evidence flips
the whole verdict to `NEEDS_REVISION` regardless of severity. The
orchestrator treats a verdict with any opaque element as malformed.

## Rule R3 — A verdict resting on unconfirmed evidence downgrades

When a dimension's PASS rests on the implementer's reported
`test_results` or other evidence you did not independently confirm —
whether the check could not run (environment, capacity, no runnable
check exists) or you simply did not run it — do not emit a clean
PASS for it — downgrade to
`PASS_WITH_NOTES` naming exactly what was not independently verified (e.g.
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
