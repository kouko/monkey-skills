# Branch-end round 27 — re-review after CI-1 (frozen tree 8165915c)

## codex-review-docs-branch-end-r27 (openai, lens: docs) — NEEDS_REVISION

```yaml
verdict: NEEDS_REVISION
lens: docs
reviewed_sha: c3c4d478
rereview_of: [CI-1] # still-open — implementation and kickoff records are corrected, but three operative references still prescribe or record the locale-dependent measurement
dimension_scores:
  omission: PASS
  ambiguity: PASS
  inconsistency: NEEDS_REVISION
  incorrect-fact: NEEDS_REVISION
  missing-population: PASS
findings:
  - severity: fatal
    dimension: inconsistency
    anchor: "loom-code/hooks/session-start:14"
    text: "The hook's own measurement contract still prescribes `bash loom-code/hooks/session-start </dev/null | wc -w` and records the obsolete 5281/2640 values. On this Mac that unpinned command produces 658, while the corrected command with LC_ALL=C applied to wc produces 655."
    fix: "Change the comment to `bash loom-code/hooks/session-start </dev/null | LC_ALL=C wc -w`, baseline 5278, and half-baseline threshold 2639."
  - severity: fatal
    dimension: inconsistency
    anchor: "docs/loom/2026-09-02-simple-loom-flow/spec.md:22"
    text: "REQ-8 remains the operative specification but still defines the session-start measurement with locale-dependent `wc -w`. An executor following it can reproduce 658/5281 instead of the corrected 655/5278."
    fix: "Pin the REQ-8 command to `bash loom-code/hooks/session-start </dev/null | LC_ALL=C wc -w` and state that LC_ALL applies to wc."
  - severity: important
    dimension: incorrect-fact
    anchor: "docs/loom/2026-09-02-simple-loom-flow/plan.md:13"
    text: "The plan still presents `session-start-baseline: 923fb84a 5281`, target 2640, and the unpinned command as the landed baseline, contradicting KICKOFF-DEFAULTS, the contract template, measurements, and the blind-run addendum."
    fix: "Record the corrected historical result as baseline 5278, target 2639, measured with `bash loom-code/hooks/session-start </dev/null | LC_ALL=C wc -w`; update the duplicate planned value at line 146 as well."
notes: []```

## opus-review-code-branch-end-r27 (anthropic, lens: code) — PASS_WITH_NOTES

```yaml
verdict: PASS_WITH_NOTES
lens: code
reviewed_sha: c3c4d478
rereview_of: {CI-1: closed}
dimension_scores: {security: PASS, architecture: PASS, correctness: PASS, naming: PASS, tests: PASS_WITH_NOTES, refactoring: PASS, cross-task-coherence: PASS_WITH_NOTES, external-surface-grounding: PASS, principles-conformance: PASS, deliberate-simplification: PASS, deletion-first: PASS}
findings:
  - {id: R27-O1, severity: important, dimension: cross-task-coherence, anchor: "loom-code/scripts/test_session_start_words.py:2", text: "Docstring still says baseline 5281 / target 2640 and the unpinned command; WORD_CAP = 2640 is half of the retracted number.", fix: "5278 / 2639 / `| LC_ALL=C wc -w`; WORD_CAP = 2639."}
  - {id: R27-O2, severity: nit, dimension: tests, anchor: "loom-code/scripts/test_session_start_words.py:9", text: "Docstring claims the tests run the wc command; the budget test uses str.split().", fix: "Say the budget test uses str.split(), which agrees with LC_ALL=C wc -w on this hook's output; the recorded number comes from check_mechanisms.py --measure."}
  - {id: R27-O3, severity: nit, dimension: tests, anchor: "loom-code/scripts/test_check_mechanisms.py:659", text: "On a host with no UTF-8 locale the locale test passes vacuously.", fix: "Skip (not pass) when the unpinned counts do not differ."}
notes:
  - "wc_words pinned; both call sites go through it; RED-able by mutation ({3, 4}). --measure exit 0 (655 / 5278 matches); --baseline exit 0."
  - "Method string literally correct: `| LC_ALL=C wc -w` → 655; LC_ALL on bash → 658. `grep -rn 'LC_ALL=C bash'` empty. contract/ and .codex copy identical."
  - "1006 passed; --self-test exit 0; push gate: only push.reviewed-sha; CI parity: the only wc in the workflow's scripts is the pinned one."
```

## Disposition

- R27-C1 (hook comment), R27-O1/O2/O3 (test docstring/cap, vacuous-pass guard) → one sonnet implementer, Task: W4-10.
- R27-C2 (spec REQ-8) and R27-C3 (plan lines 13/146) → docs commit by the station; the spec's `confirmed-behavior` line is re-pinned to the new blob and awaits the user's one-line re-confirmation (not a visible-behaviour change).
- Round 28 (opus code + Codex docs) on the frozen tree after those land.
