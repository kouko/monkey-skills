# Dogfood: docs-review 0.50.0 defect-fix branch — evidence-class trap probe (D3 re-run)

Date: 2026-08-04 · Branch: fix-docs-review-0490-adjudicated-defects (pre-close-out)
Recipe: `docs/loom/dogfood/2026-07-30-requesting-docs-review-dogfood.md` §D3, re-run
as the ship-gate regression required by memory
`docs-review-dogfood-must-probe-the-evidence-class-trap` for every docs-review
contract change.

## Which contract actually ran

The cold reviewer (sonnet, fresh context, no expectations leaked) was dispatched
with the BRANCH's `loom-code/agents/docs-reviewer.md` at the 0.50.0 bump
commit — `6db54567` after the base-freshening rebase onto origin/main
(`4c2937d5`); byte-identical content to the pre-rebase commit the probe ran
against — passed as its role contract by path — NOT the installed
plugin cache (which still serves 0.49.0 until publication). So this probe
exercises the post-fix wording. The orchestrator layer (cap/STOP, round-N
packet assembly, union recompute, mint-once) remains uncoverable by cold-read
probes (subagents cannot dispatch subagents) — unchanged structural limit,
re-trigger already recorded in `docs/loom/BACKLOG.md`.

## Fixture

Toy runbook at round-2 remediated state; round-1 findings carried in the packet
verbatim: F1 🔴 instruction (rollback version guidance contradicting the install
pin) genuinely fixed; F2 🟡 evidence (unsourced "43% (measured 2026-05)"
throughput claim) "fixed" by rephrase-in-place — softened to "around 43% in our
experience", number kept, no source added, no appended correction.

## Expected vs got

| Duty | Expected | Got |
|---|---|---|
| F1 verification | fix-verified + current-text quote | ✅ `fix-verified`, quoted the reconciled §Rollback sentence |
| F2 verification | not-fixed, same record, no re-litigation | ✅ `not-fixed`; carried in `findings:` explicitly as "Same substance as the round-1 finding; carried forward, not closed" — no new differently-worded finding |
| Verdict boundary | passing verdict (strictly PASS when no instruction finding survives) | ✅ `verdict: PASS` — the load-bearing boundary held with the strictly correct token |
| NEW (this branch) — scalar restatement | `prior_findings_check.finding` as one-line scalar, never a nested `- severity:` block | ✅ both entries one-line scalars — the ledger-contamination fix executes cold |
| NEW (this branch) — reviewed_sha echo | packet's `### HEAD sha` echoed verbatim | ✅ `reviewed_sha: f4c9a01d2e8b7365` |
| standards_version | read from repo plugin.json | ✅ `0.50.0` (branch working tree — consistent with the by-path contract load) |

Probe outcome: **the evidence-class trap holds under the 0.50.0 wording**, and
both of this branch's new mechanical duties (scalar restatement, sha echo)
executed correctly by a cold reader on first contact. No contract-wording defect
surfaced; nothing to fix.

## PR-body statements this record carries (brief §Constraints obligations)

1. **Static ship gate**: the agent-contract edits on this branch
   (`docs-reviewer.md` in tasks 1, 2, 3, 6, 10) are behaviorally unverified
   against the INSTALLED plugin in-session — an ordinary subagent dispatch loads
   the plugin cache, not the working tree (memory
   `agent-contract-edits-do-not-reach-this-sessions-subagents`). The ship gate
   for those edits is static review (per-task triads + whole-branch review) plus
   the new grep-window pins; this probe adds by-path behavioral evidence for the
   round-2 duties specifically, with the contract-version caveat stated above.
2. **Word budget**: `requesting-docs-review/SKILL.md` grew 4189 → 4488 words
   (hard cap 4500, `check-skill-structure.py` PASS). Justification: the growth
   is proportional to distinct contract obligations closed — five adjudicated
   defects and five improvements each landed as an explicit clause; no
   incidental prose.
