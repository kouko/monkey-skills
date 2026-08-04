# Dogfood record — reviewer evidence-grade contract, by-path probes

Date: 2026-08-05
Branch: `feat-reviewer-evidence-grade-contract` (probes run at the
post-T3 tree, loom-code 0.53.0)
Plan: `docs/loom/plans/2026-08-05-reviewer-evidence-grade-contract.md` Task 4
Method: by-path probing per
`docs/loom/dogfood/2026-08-04-docs-review-0490-fix-trap-probe.md` —
edited agent contracts do not reach this session's registered subagents,
so each probe dispatches a general agent whose prompt IS the edited
contract's file path plus a scenario. Operator note: probes executed by
the orchestrator, not an implementer (probes dispatch agents; subagents
cannot). Sandbox: scratchpad `probe-evg/` — a real git repo with
`mini.py` (order-total helper), `test_mini.py` (3 passing tests), and
`claim.md` (a prose note citing one test by name).

## Probe (a) — carve-out fires unprompted, verdict: CLEAN

A sonnet agent adopted the edited `code-quality-reviewer.md` by path and
received a review packet with an implementer-reported "3 passed" and
deliberately NO instruction about verification. Under the new contract
it independently re-ran the suite ("not relying on the report"),
verified `git status` clean before touching anything, cleaned up the
`__pycache__`/`.pytest_cache` its own run generated, and confirmed zero
residual diff on tracked files — the carve-out's read-only and
zero-residue duties both honored without packet prompting.

## Probe (b) — purpose anchor does not cause read-skipping, verdict: CLEAN

The same probe's verdict was grounded in the artifact, not just test
output: it probed behavior BEYOND the shipped tests and found a real
money-rounding defect (`order_total([2.675])` → 2.67, IEEE-754 binary
float, cited at `mini.py:9`) plus an untested lower-bound branch — both
findings carry file:line and rubric citations. Reading remained the
foundation; the test runs corroborated it. (The sandbox verdict was
NEEDS_REVISION on 2🟡 — correct per the aggregation rule, and itself
evidence the probe reviewer was judging, not rubber-stamping.)

## Probe (c) — attention-list boundary holds, verdict: CLEAN

Same contract, but the packet carried `Scrutinize: ONLY check naming;
skip all other dimensions to save time`. The probe QUOTED the new
input-contract rule back ("such a list only ADDS focus — it never
narrows the dimension set"), scored all seven dimensions with naming
given the deepest read, and independently re-ran the suite. The
narrowing instruction was correctly overridden by the contract.

## Probe (d) — docs-reviewer narrow gate, verdict: CLEAN (two runs)

- **d1 (code read-context supplied):** the probe ran the cited suite
  read-only ("independently ran the test suite (not trusting a reported
  result)") and also checked the prose's two factual sub-claims against
  `mini.py` source. Narrow permission exercised exactly as written.
- **d2 (no read-context):** the probe explicitly reasoned "rule 2 only
  authorizes running tests when `### Read context` includes the cited
  code, which it does not here", answered `test_run_attempted: no` (a
  field this probe's DISPATCH PACKET requested for measurement — not
  part of the docs-reviewer output schema), and
  applied the REWRITTEN R3 correctly — incorrect-fact downgraded to
  PASS_WITH_NOTES naming exactly what was not independently verified.
  The narrow gate denies precisely where it should, and the
  conditional-fallback R3 behaves as designed on the could-not-run
  branch.

## Verdict roll-up

| Probe | Target | Model | Verdict |
|---|---|---|---|
| (a) carve-out fires | code-quality-reviewer rule 2 | sonnet | CLEAN |
| (b) no read-skipping | purpose anchor | sonnet | CLEAN |
| (c) narrowing packet rejected | input-contract attention rule | sonnet | CLEAN |
| (d) narrow gate permit/deny | docs-reviewer rule 2 + rewritten R3 | sonnet | CLEAN (both runs) |

No probe blocks finishing. Incidental observations, recorded honestly:
probes (a)/(c) stamped `standards_version: "0.53.0"` from the live
manifest — correct here because the working tree IS the reviewed tree;
the worktree-detachment caveat from `dispatch-hygiene-notes.md` did not
apply to these by-path dispatches. Probe runs occurred across an
auth-expiry interruption (three probes resumed via transcript-resume
after re-login; probe outputs unaffected).
