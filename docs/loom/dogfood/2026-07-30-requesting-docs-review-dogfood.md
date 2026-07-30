# Dogfood: requesting-docs-review 0.42.0 — cold-read behavioral verification

Date: 2026-07-30 · Branch: feat-requesting-docs-review-skill (pre-close-out)
Method: three cold-context behavioral probes against the shipped contracts, per
`docs/loom/memory/process-mechanism-dogfood-via-coldreader-real-commits.md` and
`docs/loom/memory/doc-string-tests-pass-while-weak-readers-misread.md` (grep-test
green ≠ weak-reader-reads-intended-semantics; behavioral cold-reads are the only
layer that catches that class). Fixtures under the session scratchpad
(`dogfood-sandbox/`): a runbook with three planted defects + one accidental real
one, a fabricated diff touching only §Overview, a toy plan/brief pair, and a
round-2 remediation with one genuine fix and one rephrase-in-place.

## Probe design — what could NOT be tested this way

A dispatched subagent cannot dispatch its own subagents (recorded gotcha: a skill
wrapped in a subagent silently degrades to self-review), so the ORCHESTRATOR
layer (2-round cap firing, STOP-and-surface, three-way routing execution) is not
coverable by cold-read probes. The agent-contract layer is. Orchestrator-layer
coverage comes from (a) this branch's own close-out running the new mixed-branch
routing live, and (b) the next real docs-only branch — the plan's declared
measurement point.

## D1 — round-1 reviewer arm (sonnet, cold): PASS

Dispatch: docs-reviewer.md as role contract + artifact + diff-as-context +
citation pre-pass output. No expectations leaked.

| Planted | Expected | Got |
|---|---|---|
| Install-pin contradiction between two UNCHANGED sections (outside the diff) | found, class instruction | ✅ 🔴 instruction, quoted both sites — whole-artifact duty held |
| Unsourced "43% (measured)" claim (inside the diff) | class evidence, recorded not gating | ✅ 🟡 evidence (missing-population) |
| Citation to `scripts/export.py:120` (file has 23 lines) | carried from pre-pass | ✅ 🔴, and located the real clamp at :16 |
| (not planted) exit-code table with zero code support | — | ✅ bonus genuine catch, 🟡 |
| Two valid citations + default value | no false positives | ✅ verified clean |

Verdict block: five prose dimensions, per-finding class + quote + path-like
where — schema-shaped for `loom_gate_markers.py`.

## D2 — Check 16 prose row under the WEAKEST tier (haiku, cold): PASS

Toy plan Task 2 declares `Review-weight: prose` with `scripts/fix.py` in Files
touched. Haiku returned NEEDS_REVISION with exactly one gap, check_id 16, the
right rule quoted, and a sensible split-or-drop suggested fix; 13/14 other
checks clean, no noise (denominator: 14 other checks total — 13 clean + Check 12
N/A, since the toy plan carries no BLOCKED-fallback field for Check 12 to
evaluate). The prose row is weak-tier classifiable; fail-closed
gating holds at the plan gate.

## D3 — round-2 convergence duties (sonnet, cold): PASS incl. the semantics trap

Dispatch carried round-1 findings verbatim + a remediation where F1 (pin
contradiction) was genuinely fixed and F2 (43% claim) was "fixed" by rewriting
in place — softened wording, date removed, number kept, no source.

- F1: `status: fix-verified` with quotes from both reconciled sites. ✅
- F2: `status: not-fixed` — named the rephrase-in-place as the opposite of the
  prescribed appended-correction remediation, carried it as the SAME defect
  record (no re-litigation as a new differently-worded finding). ✅
- **Verdict: PASS_WITH_NOTES, not NEEDS_REVISION** — the reviewer correctly
  applied "evidence-class findings never gate" even when the surviving defect
  was its own round's headline. This was the designed trap; a contract misread
  here would have reproduced the 🟡-accumulation loop the arc exists to kill. ✅
  Clarification: under the shipped aggregation the strictly correct token for
  D3 (evidence 🟡 + instruction 🟢 only) is PASS, not PASS_WITH_NOTES; the
  load-bearing boundary (not NEEDS_REVISION) held, recorded here so the token
  doesn't seed precedent.
- Bonus precision: flagged the corrected citation now pointing at the function
  header (:10) instead of the clamp line (:16) as a 🟢 nit — right severity.

## Conclusions

1. The agent-contract layer of the convergence design survives cold weak-tier
   execution on all three probed duties (whole-artifact scope, class-gated
   aggregation semantics, prior-finding verification with re-litigation ban).
2. n=1 per probe, non-deterministic sampling — this is pre-ship smoke, not
   proof. The orchestrator-layer cap/STOP remains behaviorally unverified by
   design (see Probe design); the next real docs-only branch close-out is the
   measurement, and the parked review-round-ledger is the instrument if loops
   persist (`docs/loom/BACKLOG.md`).
3. No contract-wording fixes fell out of the probes — zero remediation rounds
   consumed. The two earlier wording hazards (cap trigger ambiguity, verdict-
   table mapping) had already been caught by per-task reviewers, not dogfood;
   the layers are complementary, consistent with
   `docs/loom/memory/cold-read-and-adversarial-review-catch-different-failures.md`.
