# Branch-end round 30 — re-review after CI-2 (frozen tree 07357215)

## codex-review-docs-branch-end-r30 (openai, lens: docs) — PASS_WITH_NOTES

```yaml
verdict: PASS_WITH_NOTES
lens: docs
reviewed_sha: c3c4d478
rereview_of: [CI-2] # closed — current instructions consistently use Python str.split; the template copies match, and the spec pin is valid and explicitly pending user re-confirmation
dimension_scores:
  omission: PASS
  ambiguity: PASS
  inconsistency: PASS_WITH_NOTES
  incorrect-fact: PASS
  missing-population: PASS
findings:
  - severity: important
    dimension: inconsistency
    anchor: "docs/loom/2026-09-02-simple-loom-flow/blind-run-report.md:3"
    text: "The introduction says that after 0bb3f9c0 only human-readable records would change and that code and hooks would not change, but the CI-2 fix later changed check_mechanisms.py, session-start, and tests. The postscript explains the later fix, but does not supersede this categorical statement."
    fix: "Rewrite line 3 to say that 0bb3f9c0 was the last fully tested tree before the later CI-2 counter change, then point to the CI-2 postscript for the final code and measurement status; remove the claim that code and hooks would not change."
notes:
  - "HEAD was 073572153dc1bfa825ab53909ad410cc3820d993."
  - "The contract template and .codex copy are byte-identical."
  - "The spec hash excluding confirmed-behavior is 7c92f365d8f9978d9010e36e070e1f9640a8e0d8, matching @7c92f36; the line says user re-confirmation is still pending."
  - "Relevant LC_ALL=C and wc -w hits in the change are historical descriptions or regression-test commentary; current measurement instructions use Python str.split."
  - "The empty-repository reproduction and check_mechanisms.py --measure could not run because the read-only sandbox provides no usable temporary directory; check_mechanisms exited 2 for that environmental reason."```

## opus-review-code-branch-end-r30 (anthropic, lens: code) — PASS

```yaml
verdict: PASS
lens: code
reviewed_sha: c3c4d478
rereview_of: {CI-2: closed}
dimension_scores: {security: PASS, architecture: PASS, correctness: PASS_WITH_NOTES, naming: PASS, tests: PASS, refactoring: PASS, cross-task-coherence: PASS, external-surface-grounding: PASS, principles-conformance: PASS, deliberate-simplification: PASS, deletion-first: PASS}
findings:
  - {id: R30-O1, severity: nit, dimension: tests, anchor: "loom-code/scripts/test_check_mechanisms.py:670", text: "RED assertion recomputes the oracle with the implementation's own expression; the literal 5 is never pinned.", fix: "assert cm.wc_words(SAMPLE) == 5 with a comment that wc under LC_ALL=C gives 4."}
  - {id: R30-O2, severity: nit, dimension: tests, anchor: "loom-code/scripts/test_check_mechanisms.py:672", text: "test_count_is_stable_across_locales cannot fail for a reintroduced pinned wc.", fix: "Drop it, or assert the module source contains no wc subprocess."}
  - {id: R30-O3, severity: nit, dimension: correctness, anchor: "loom-code/scripts/test_session_start_words.py:49", text: "_run decodes with the ambient locale (text=True) while the counter decodes UTF-8 explicitly.", fix: "Capture bytes and decode UTF-8 with errors='replace'."}
notes:
  - "CI-2 diagnosis reproduced by byte-level GNU-C emulation: 5131 vs 5278 (Python split, BSD LC_ALL=C); BSD UTF-8 5281. RED sample genuine (BSD LC_ALL=C 4, Python 5)."
  - "No wc subprocess remains; contract and .codex copy identical; --measure 655/5278 matches; 1007 passed; --self-test exit 0; push gate: only push.reviewed-sha."
  - "Docs observation: report line 3 restated the round-27 re-run as done with the Python method; the blind runner actually used LC_ALL=C wc (same 655)."
```

## Disposition

- CI-2 closed (6a349dcb). R30-C1 (Codex, important: line 3's categorical "no code changes after 0bb3f9c0" claim) and the opus docs observation are both fixed in the same commit as this file: line 3 now narrates the two later program edits with their commits, the method each re-run actually used, and the unchanged 655.
- R30-O1/O2/O3 (nits, test-level): accepted, not fixed — carried to the first post-merge change with R24-O2 and R28-O2; no program file changes after 6a349dcb.
- Both legs pass (PASS / PASS_WITH_NOTES). The review-only commit follows: rounds 27–30 recorded, probes re-pinned at the reviewed tree, CI-1 / CI-2 / R27-* / R28-* closed, `reviewed_sha` = its parent. Still owed before the push: the user's one-line re-confirmation of the spec's REQ-8 wording (spec.md line 3, pending).
