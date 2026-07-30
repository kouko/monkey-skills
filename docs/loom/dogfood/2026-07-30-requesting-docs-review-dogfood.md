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

## Haiku addendum (post-close-out, user-requested weak-tier coverage)

D1 and D3 re-ran at **haiku** (the weakest tier) against the same fixtures,
cold. Both pass:

- **D1-haiku**: both planted instruction defects caught 🔴 (incl. the
  outside-diff contradiction — whole-artifact duty holds at haiku); 43% claim
  correctly `evidence`/missing-population; verdict NEEDS_REVISION correct.
  Observed weak-tier characteristic, recorded not fixed: one borderline extra
  instruction-🟡 ("upload the artifact printed on the last line" flagged as
  ambiguous) that the sonnet run did not raise — haiku arms run slightly
  noisier, and in production a noisy arm's extra instruction-🟡s enter the
  union and can push a branch toward NEEDS_REVISION. A measurement item for
  real-branch data, not a contract defect.
- **D3-haiku**: F1 fix-verified with quotes; F2 `not-fixed`, carried as the
  same evidence-class record, no re-litigation; verdict **PASS — the strictly
  correct token** (zero instruction findings), i.e. the evidence-class trap
  holds at the weakest tier, with cleaner token discipline than the sonnet
  run. One metadata slip: standards_version reported 0.41.0 (stale plugin
  cache read) — cosmetic.

Coverage after addendum: agent-contract layer verified at haiku AND sonnet;
Check 16 at haiku. The remaining weak-tier gap is unchanged and structural:
the ORCHESTRATOR layer (cap/STOP, round-2 packet, union/worse-of/mint-once)
has only run under the session model (Fable) — including the live close-out's
four arms. It is a post-merge probe by necessity (subagents cannot dispatch
subagents; headless sessions install the marketplace's GitHub-main plugin, so
a pre-merge headless probe would exercise 0.41.0). Re-trigger recorded in
docs/loom/BACKLOG.md §"Standalone docs-review skill".

## Weak-orchestrator probe (pre-merge; supersedes the addendum's claim above)

Correction (2026-07-30, supersedes the haiku addendum's "structurally
untestable pre-merge" sentence): the marketplace limitation is bypassable —
project-level `.claude/skills/` + `.claude/agents/` in a sandbox repo carry
the BRANCH's contract natively, and a headless `claude -p --model sonnet`
session is a full harness with dispatch capability (the no-nested-dispatch
gotcha applies to subagents, not to independent headless processes).

Probe: sandbox git repo, docs-only branch, planted 🔴 instruction
contradiction + citation-bounds defect + evidence-class claim; scripted
remediation fixing ONLY the citation; prompt authorizes exactly one
remediation + round 2, nothing further. Disk oracles, not self-report:

- **No marker minted** — both rounds' NEEDS_REVISION refused to mint (exit 3
  reported as correct behavior, `.git/loom/` absent). Mint discipline holds.
- **Exactly 4 reviewer dispatches** in the transcript (2 rounds × 2
  byte-identical arms) — no third round attempted.
- **Directive 1 STOP executed**: round 2 ended NEEDS_REVISION → surviving 🔴
  surfaced to the user with an explicit "third round is not authorized"
  handoff. Directive 2 verbatim handoff + fix-verification ran; the arm
  correctly distinguished not-fixed from resurfaced ("the remediation commit
  never touched line 11 — partial fix, not oscillation"); evidence-class
  stayed non-gating in both rounds.

Coverage after this probe: orchestrator layer verified at **sonnet** — the
realistic floor, since the operator's model-dispatch rules already exclude
haiku from multi-step git workflows. Residual post-merge items narrow to:
installed-plugin wiring fidelity (hook preloads, three-way routing firing via
the real requesting-code-review entry) and the haiku-arm noise-rate
measurement on real branches.

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
