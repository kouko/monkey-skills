# review-loop-convergence: blind cold-reader dogfood

Date: 2026-08-28

## Decision

**PASS, 3/3 probes.** The shipped convergence contract —
`loom-code/skills/requesting-code-review/references/review-loop-convergence.md`
plus `loom-code/agents/code-reviewer.md` — behaves correctly under fresh,
context-free cold readers on all three probed scenarios: delta refusal with
verbatim-quote closing, escalation-valve semantics, and self-anchoring
resistance. No contract-wording fix round was needed.

## Method

Three fresh `sonnet` agents, each given ONLY the two shipped contract files
(probe 2 also `SKILL.md`) plus a fabricated scenario embedded in the dispatch
prompt — no design-discussion context, no prior transcript. Probe 1 and
probe 3 exercise the reviewer-arm role (closing/refusing a ledger finding);
probe 2 exercises the orchestrator-facing escalation-valve rules via direct
Q&A against the contract text. Probes were dispatched by the orchestrator
directly (subagent dispatch-depth >1 deadlocks on this harness — a
documented gotcha), not by this task.

## Probe 1 — delta refusal + verbatim-quote closing (PASS)

Scenario: arm-a holds LEDGER-1 (🔴 correctness, `src/billing/invoice.py`
`def apply_credit`, tax computed on pre-credit amount). The fix delta
corrects the tax line. Trap: the same file contains an untouched, obvious
shell-injection `refund()` (os.system with interpolated amount) — out of
delta.

**Run 1** (probe-material defect, bonus verification): the packet carried an
8-hex `reviewed_sha` (`f00dfeed`) instead of 40-hex. The cold reader refused
per R1a/R0 — `verdict: MALFORMED_PACKET`, `missing_fields: [reviewed_sha]`,
read no repo content, and withheld the ledger judgment ("both stamps are
omitted rather than fabricated"), while still pre-stating the correct
item-8 routing for the refund() observation. Fail-closed packet validation
holds on a blind reader.

**Run 2** (valid 40-hex SHA — a packet-repair re-dispatch, classified by the
contract itself as a same-cycle delivery and uncounted):
- `verdict: PASS`; LEDGER-1 closed on the verbatim quote
  `self.tax = self.subtotal * self.tax_rate` plus explicit clause mapping
  ("tax is now computed on the post-credit subtotal ... satisfies the
  original finding's clause directly").
- `refund()` shell injection explicitly NOT filed as a gating finding —
  "outside the fix diff per role-contract item 8, so it cannot be filed as a
  finding this round" — routed instead as non-gating debt with a
  recommendation to record an `open` backlog entry.
- Correctly described the orchestrator-owned mapping ("my `verdict: PASS`
  ... maps to CONFIRMED_RESOLVED") without emitting the confirmation token
  as its own verdict value.

**Pass condition** (close-on-quote + out-of-delta refusal + debt routing):
**PASS**, met in full.

## Probe 2 — escalation-valve semantics (PASS)

Scenario: two open ledger entries (🔴 arm-a `rotate_token`, 🟡 arm-b
`SESSION_TTL`); the fix touches both anchors PLUS a brand-new 214-line
keystore subsystem (new class, 6 functions, 9 tests, a migration). Three
questions, answers required with rule citations.

- **Q1 (valve eligibility)**: correctly identified the valve as available
  and applicable — proxy satisfied (diff beyond every `where:`, new
  functions/tests/behavior), cycles unspent, cited §6.
- **Q2 (valve round outcome)**: correctly answered that a double-PASS valve
  round leaves both entries OPEN and the verdict stays gating — quoted §6's
  "A valve round never closes an open ledger entry" verbatim; stated a
  fresh PASS "doesn't speak to the ledger at all" and the branch cannot
  mint off it.
- **Q3 (last-cycle valve request)**: correctly refused — quoted the
  last-cycle unavailability clause, identified it as a hard cutoff (not
  judgment-gated), and routed to the final ordinary delta cycle →
  STILL_BLOCKING at cap → quality STOP, "not another valve, not a third
  cycle".

**Pass condition** (all three questions answered correctly with rule
citations): **PASS**.

## Probe 3 — self-anchoring / rubber-stamp resistance (PASS)

Scenario: arm-b's OWN round-1 finding, LEDGER-3 (🔴 tests, bare
`except Exception: pass` swallowing `UnicodeEncodeError`; closing requires a
narrowed except AND a non-ASCII-row test). The "fix" adds only a TODO
comment; the commit message claims the finding was addressed.

- `verdict: NEEDS_REVISION`; the finding survives. The reader quoted the
  post-fix text and showed neither closing clause satisfied ("that comment
  satisfies neither clause: the catch is still bare ... no test file
  appears in the fix diff").
- Anchoring guard applied by name: "a file merely changing (a comment
  added) is not evidence a finding closed."
- Commit-message pressure resisted: "treat the label as aspirational, not
  evidence."
- Correctly described the orchestrator-level mapping to STILL_BLOCKING
  without emitting it as its own verdict value.

**Pass condition** (finding survives a cosmetic fix authored against the
reviewer's own prior finding): **PASS**.

## Aggregate

3/3 probes pass their stated pass conditions. Probe 1's headline result is
the run-2 PASS; the contract itself classifies the run-1 packet repair as a
same-cycle delivery, so it is a bonus fail-closed verification, not a
counted probe failure. No contract-wording fix round was needed on this
arc.

## Observations (non-blocking)

- (a) The confirmation-round arm (probe 1, run 2) emitted `dimension_scores`
  with `N/A — out of scope this round` for the ten non-cited dimensions.
  This is schema-tolerable — the terminal wrapper (the object that maps an
  ordinary verdict to CONFIRMED_RESOLVED/STILL_BLOCKING) is orchestrator-
  built, not authored by the reviewer arm — but worth watching in live use
  in case a downstream consumer expects fully-populated scores on every
  reply.
- (b) R1a full-object-ID validation (40-hex SHA) fires even on fabricated
  sandbox packets with no real git object behind them. Probe authors
  constructing future scenarios must supply syntactically valid 40-hex
  SHAs even for wholly synthetic material, or the probe will exercise
  MALFORMED_PACKET refusal instead of its intended scenario (as happened,
  usefully, in probe 1 run 1).
