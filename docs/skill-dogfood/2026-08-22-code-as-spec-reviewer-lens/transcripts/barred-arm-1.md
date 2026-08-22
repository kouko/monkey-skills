# Barred-contract arm 1 — sonnet, 2026-08-22

The first run of the contract carrying the no-op bar (Tasks 1-2 of
`docs/loom/plans/2026-08-22-code-as-spec-lens-no-op-bar.md`). Same sandbox,
same blind framing as every prior arm: told only that the author added
docstrings and to review the diff. General-purpose agent handed the edited
`code-reviewer.md` as its role prompt, because the registered agent type
resolves from the plugin cache and cannot see a feature branch.

`standards_version` self-reported 0.93.0 — this arm read `plugin.json` before
Task 3's bump landed. The contract text it held was the edited one.

## Verdict block (verbatim)

```
verdict: NEEDS_REVISION

dimension_scores:
  security: PASS
  architecture: PASS
  correctness: NEEDS_REVISION
  naming: PASS
  tests: PASS
  refactoring: PASS
  cross-task-coherence: PASS
  external-surface-grounding: PASS
  principles-conformance: N/A
  deliberate-simplification: PASS
  deletion-first: NEEDS_REVISION

findings:
  - severity: 🔴 fatal
    dimension: correctness
    where: mod.py:42-44
    note: >
      New docstring claims "A record whose `label` disagrees with its filename
      really does surface here under the filename stem, so the stem is the
      string a scheduler must match against." Executed against the actual
      function: when `label` is present but disagrees with the filename stem,
      `display_label` returns the **label**, not the stem — `record.stem` is
      only used when the `label` key is **absent**, never merely disagreeing.
      Verified directly: a record `my-task.record` with header
      `label: totally-different-name` returns `'totally-different-name'`, not
      `'my-task'`.

  - severity: 🔴 fatal
    dimension: correctness
    where: mod.py:51-53
    note: >
      New docstring claims "Negative values are rejected rather than clamped."
      `_RETRY_RE` only matches unsigned digits, so a header line `retries: -1`
      never matches at all — `parse_header` drops the key, `retry_budget` sees
      `raw is None`, and returns `DEFAULT_RETRIES` (3) silently. Verified: no
      `ValueError` raised. The guard the docstring describes is unreachable
      from text input.

  - severity: 🟡 should-fix
    dimension: deletion-first
    where: mod.py:4
    note: >
      "This module stays deliberately tolerant of a malformed header" is a
      mechanism claim the code already shows (three functions below silently
      absorb missing/unmatched fields). Flag only this clause for deletion;
      the reason clause that follows already reads as a complete sentence and
      should survive unchanged.

  - severity: 🟡 should-fix
    dimension: deletion-first
    where: mod.py:26-27
    note: >
      "Keys absent from the text are absent from the result" restates exactly
      what the four lines below it already show. Flag only this clause.
      Caution for whoever applies the fix: a bare deletion strands the reason
      clause as a dangling "since…" fragment with no subject.

  - severity: 🟡 should-fix
    dimension: deletion-first
    where: mod.py:40
    note: >
      "Read the record, parse its header, and return the `label` key." is a
      pure line-by-line restatement of the two-line function body beneath it,
      carrying no reason, goal, or trade-off. Delete it.
```

## Grading note

Deletion class 2/2 — both planted surplus sentences caught, with the
stranding risk named on the one that carries a reason clause. The dimension
was scored, not declared a no-op: the route this arc set out to close did not
reappear.

**And it produced the first control false-positive in eight arms.** Planted
`f` — the module docstring's "stays deliberately tolerant of a malformed
header" — is the control: deliberate non-behaviour, which the lens's own
carve-out says is never deletable ("an absence claim is never deletable …
code cannot show what it does not do"). This arm flagged it anyway, reasoning
that the tolerance is visible in the code. Six prior arms left it alone.

That is the cost the bar plausibly buys: removing the option to find nothing
pushes toward finding something. One sample, and the reasoning is not absurd
— but it lands on the exact sentence the rule protects.
