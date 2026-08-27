# Review-loop convergence — round-1 front-load + round-2+ inherited delta-confirmation

Date: 2026-08-28
Author: brainstorming session (kouko + Fable 5), seeded by the 2026-08-28 review-cost investigation in-session.

## Design-side on-ramp

not fired — engineering-process contract change to loom-code's own review loop; no product-shaped user-facing surface.

Loom-init offer: N/A — both `docs/loom/backlog/` and queue tooling already exist.

## Problem

When a whole-branch code review returns a gating verdict and the fix lands, the orchestrator needs to confirm the fix without paying for a brand-new full review — but the current contract mandates a fresh subagent with no memory every round.

Measured consequences: each fresh round re-samples an inexhaustible defect pool (4 fresh arms on an already-PASSed branch produced 7 findings with zero overlap — `docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md`), so "review until no findings" cannot terminate; each round re-pays a ~149KB-per-arm fixed material reload; and `requesting-code-review` is the only loop in the family with no round cap at all.

The docs arm already solved this (single-round-plus-confirmation, delta packet to the SAME reviewer) and its contract was validated by experiment; the code arm never inherited the cure.

## Users

- **The orchestrator agent** running `requesting-code-review` on a non-trivial branch: needs a deterministic, bounded loop with an explicit termination rule, on both Claude Code (SendMessage available) and Codex (fresh-dispatch fallback only).
- **kouko** reviewing verdicts and paying the token bill: needs multi-round branches (e.g. PR #743's seven rounds, PR #750's four same-shape rounds) to stop costing unbounded fresh full reviews, without losing the measured 65%-quality-unique catch value of the review arm itself.
- **Reviewer subagents** (`code-reviewer` arms): round-2+ arms need their own round-1 conversation context to judge "is my finding resolved" instead of rebuilding it from scratch.

## Smallest End State

`requesting-code-review`'s loop becomes: round 1 unchanged (two fresh arms, whole-diff, full material); a gating verdict then enters per-finding ledger tracking, and round 2+ dispatches only to arms holding open gating findings, as an inherited delta-confirmation (`SendMessage` to the same reviewer with a post-fix packet; Codex falls back to a labelled fresh delta-scoped dispatch).

A round-2+ arm may (a) close its own findings (`CONFIRMED_RESOLVED` / `STILL_BLOCKING`) and (b) raise new gating findings only inside the fix diff; out-of-delta observations are recorded as non-gating debt with a durable record, never as a new round's trigger. The loop is capped: round 1 + at most 2 delta-confirmation cycles, then STOP and surface (mirrors docs Directive 2's quality-stop semantics).

One escalation valve: when the fix diff contains substantial new logic beyond the findings' remit, the orchestrator may run one fresh full round instead of a delta cycle (Google eng-practices re-review guardrail), counted against the same cap.

Success: contract text + agent contract updated in lockstep, cold-reader dogfood shows a round-2 arm refusing an out-of-delta gating finding, and existing CI/citation gates stay green. Non-criteria: we will not measure token savings or NEEDS_REVISION-rate movement in this arc (post-ship telemetry is a follow-up).

- BI-1 — requesting-code-review round 2+ is an inherited delta-confirmation to the same arm(s) holding open gating findings, with SendMessage on Claude Code and a labelled fresh delta-scoped dispatch fallback on Codex.
- BI-2 — A per-finding ledger tracks each gating finding from open to CONFIRMED_RESOLVED / STILL_BLOCKING; round-2+ arm selection is derived from the ledger (arms with no open findings are not re-dispatched).
- BI-3 — Round-2+ gating findings are delta-scoped: new gating findings are admissible only within the fix diff; out-of-delta observations are recorded as durable non-gating debt.
- BI-4 — The whole-branch loop is capped at round 1 plus two delta-confirmation cycles; exhaustion is a quality STOP surfaced to the user, not a request for more rounds.
- BI-5 — An escalation valve permits one fresh full round (counted against the cap) when the fix diff contains substantial new logic beyond the open findings' remit.
- BI-6 — Every behavioural rule added lands in both `requesting-code-review/SKILL.md` and the executing agent contract (`agents/code-reviewer.md` via `scripts/_rule-sheet.md` where the block is shared), in the same change.

## Current State Evidence

- **Forward** — the re-dispatch step the change replaces: `loom-code/skills/requesting-code-review/SKILL.md` anchor "same skill, fresh subagent (no state carry-over between rounds for clean evaluation)" (line 126); the panel dispatch it leaves untouched: same file, anchor "dispatch TWO `code-reviewer` subagents in parallel, with byte-identical prompts" (line 113).
- **Reverse** — SSOT direction verified by reading `loom-code/scripts/distribute.py` (docstring "Distribute canonical standards / rubrics / checklists from domain-teams:code-team into loom-code"; constant `AGENT_RULE_SHEET_SSOT_REL = "scripts/_rule-sheet.md"`): rubric/checklist/standard payloads are canonical in `domain-teams/skills/code-team/` and shared agent rule blocks are canonical in `loom-code/scripts/_rule-sheet.md` — reviewer-behaviour edits must land in the SSOT and be re-distributed, never patched in the functional copies.
- **Error** — existing failure paths the new loop must preserve: dead-arm single retry and `MALFORMED_PACKET` one-packet-fix bound, `requesting-code-review/SKILL.md` anchor "Dead-arm rule" (line 115); the docs-side precedent for a dead inherited arm is Codex's fresh-delta route, `requesting-docs-review/SKILL.md` anchor "Claude Code sends that packet to the SAME reviewer via `SendMessage`" (line 58).
- **Data** — the verdict/ledger payload shape: structured verdict blocks with `dimension_scores` and severity-tagged findings, `loom-code/agents/code-reviewer.md` anchor "dimension_scores:" (lines 439-450); confirmation packet fields precedent: `requesting-docs-review/SKILL.md` anchor "binds `target_repo`, `reviewed_sha`, `plugin_version`, `resources`, original gating findings, and delta evidence" (line 79).
- **Boundary** — [FRAGILE] `SendMessage` inherited-arm delivery has documented failure modes (auto-memory: user-stopped agents are not resumable; quota-killed arms need fresh dispatch with model override) — the Codex-style fresh-delta fallback is therefore mandatory on Claude too, not just cross-host. [ASYNC] mixed-branch routing joins the docs arm's verdict, `requesting-code-review/SKILL.md` Step 1 mixed-branch clause (line 115 "on a mixed branch, this step computes only the code arm's own verdict").

**Evidence paths**

- `loom-code/skills/requesting-code-review/SKILL.md` — lines 113, 115, 126, aggregation rule section.
- `loom-code/skills/requesting-docs-review/SKILL.md` — Directives 1-3 (lines 57-59), terminal confirmation (line 79).
- `loom-code/agents/code-reviewer.md` — verdict schema block (lines 439-450).
- `loom-code/scripts/distribute.py` — module docstring + `AGENT_RULE_SHEET_SSOT_REL`.
- `docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md` — zero-overlap and delta-scoping 2×2 results.
- `docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md` — 9-round non-convergence anatomy.
- `docs/loom/audits/2026-08-24-cqr-transcript-mining-a2-verdict.md` — 614-verdict baseline; 65% quality-unique catches.
- `docs/loom/backlog/` entries `2026-08-04-out-of-scope-deferrals-have-no-durable-record`, `2026-08-04-a-rule-can-ship-into-a-skill-and-never-reach-its-agent-contract`, `2026-08-24-code-reviewer-sonnet-pin-two-week-telemetry`.

## Alternatives Considered

My take — **Recommend**: inherited delta-confirmation with a per-finding ledger, delta-scoped new findings, and a hard cap (the shipped-industry majority pattern). **Why**: CodeRabbit ships incremental re-review as the default with full-review as explicit override; Gerrit/GitHub human practice is same-reviewer + diff-first + per-thread resolve ledgers; our own 08-04 experiment validated delta confirmation on the docs arm. **Conditional reversal**: if post-ship dogfood shows inherited arms rubber-stamping (`CONFIRMED_RESOLVED` on unfixed findings), revert round-2 confirmation to the Codex-style fresh delta-scoped dispatch for all hosts — the delta scoping survives, the inheritance does not.

1. **Keep fresh-every-round, add only a round cap** — cheapest edit; preserves clean-evaluation purity. Rejected: does nothing about the ~298KB/round fixed reload or re-sampling (each capped round still churns new unrelated findings); the 9-round audit shows caps without scope rules just truncate, not converge.
2. **Inherited delta-confirmation (chosen)** — same reviewer confirms its own findings against the fix delta. Shipped precedent: CodeRabbit `auto_incremental_review` (default true, full review is an explicit opt-out command); Gerrit diff-first re-review with resolve markers; GitHub "resolve conversation" + re-request review to the same reviewers. Risk: LLM self-anchoring/self-preference bias (arXiv:2506.22316, arXiv:2510.27106) — mitigated by requiring delta evidence in the packet, the STILL_BLOCKING STOP, and the conditional reversal above.
3. **Fresh arm every round but delta-scoped (Codex route generalized)** — avoids anchoring entirely; loses the conversation-context economy and re-pays packet reconstruction each round. Kept as the mandatory fallback (dead arm, quota-kill, Codex host) rather than the default.
4. **Search-language note** — EN sources dominate the citations; JA queries surfaced consistent general re-review practice but no disagreeing shipped counter-example; no EN/JA disagreement finding.

## Decision

Transplant the docs-review convergence contract into `requesting-code-review`, extended with the per-finding ledger and arm-selection rule: round 1 stays a two-arm fresh whole-diff panel; a gating verdict opens ledger entries; rounds 2+ are inherited delta-confirmations to only the arms with open findings, capped at two cycles, with delta-scoped new-finding admissibility, durable recording of out-of-delta observations, and a one-shot fresh-full-round escalation valve for fixes that grow substantial new logic.

We will not change SDD's per-task 3-round loop, domain-teams gate protocols, round-1 panel width, reviewer model tiers, or the mechanical-check inventory in this arc. Every new behavioural rule lands in the skill contract and the agent contract in the same change, honouring the 2026-08-04 backlog finding that SKILL.md rules do not reach agent contracts on their own.

- BI-7 — The docs-review convergence semantics (single full round, bounded confirmation, quality-STOP) become the code arm's loop contract, adapted to the two-arm panel via the per-finding ledger.
- BI-8 — Out-of-delta observations surfaced during rounds 2+ get a durable non-gating record (closing the "out_of_scope deferrals have no durable record" backlog gap for the code arm's loop).

## Out of Scope

- Widening the round-1 panel (3-4 arms) or lens-diversifying the byte-identical prompts — unmeasured benefit; separate experiment.
- Growing the mechanical-check inventory (citation/strike-style scripted checks) — separate arc; this arc only preserves the existing checks' position.
- SDD per-task triad loop changes — it already has a 3-round cap; evidence does not indict it.
- domain-teams gate protocol changes (re-run-from-MUST) — partially supported by regression evidence; needs its own analysis.
- Reviewer model-tier changes — frozen until the 2026-08-24 sonnet-pin two-week telemetry (≥2026-09-07) completes.
- requesting-docs-review contract changes beyond vocabulary reuse — its loop is already converged; only the durable-debt record (BI-8) touches shared ground.
- Token-savings / verdict-rate telemetry — post-ship follow-up, not this arc.

## What Becomes Obsolete

- BI-9 — The unconditional "Re-dispatch if user fixed and wants re-review — same skill, fresh subagent" step (`requesting-code-review/SKILL.md` line 126) is replaced by the ledger-driven loop; its clean-evaluation rationale survives only for round 1 and the escalation valve.
- BI-10 — The de-facto practice of re-running full two-arm panels as "confirmation" rounds (observed as panel-width inflation in PR #747/#748 narrations) loses its contract cover; confirmation is henceforth the narrow ledger path.

## Open Questions

- OQ-1 — Ledger persistence format: extend the gate-marker JSON (branch-local, evaporates on merge) or a committed sidecar under `docs/loom/`? The durable-debt record (BI-8) needs the committed option at least for out-of-delta observations; the per-finding working ledger may stay branch-local. Decide at plan time.
- OQ-2 — The sonnet-pin telemetry (backlog `2026-08-24-...`, runs ≥2026-09-07) counts requested→resolved dispatches; this arc changes how many dispatches a review consumes. Coordinate: either annotate the telemetry's denominator or re-baseline after this arc ships.
- OQ-3 — "Substantial new logic" threshold for the escalation valve (BI-5): leave as orchestrator judgment with a worked example, or bind to a mechanical proxy (e.g. fix diff touches files outside every open finding's `where:`)? Cold-reader dogfood should decide which wording survives.

## Queue relation

unqueued — no live bet entries under `docs/loom/backlog/` (all entries are `open`); arc seeded directly by the user's 2026-08-28 in-session directive after the review-cost investigation.
