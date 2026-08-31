# Prose-edit self-sweep — implementer-side silent checklist + A/B validation

Date: 2026-08-31 · Author: doc-writer-r2 session (kouko) · Status: brief

## Design-side on-ramp

not fired — process/contract change to an existing development workflow (implementer agent contract + measurement harness), not product-shaped, user-facing, or multi-state new work

Loom-init offer: N/A — store exists

## Queue relation

unqueued — seeded by a user-supplied proposal in-session (external suggestion text); no existing backlog entry covers writer-side prose self-sweep, and none of the 10 open entries (2026-08-31 `--ready` run) overlaps this scope

## Problem

When an implementer or orchestrator edits authored prose (`.md`) during development, the docs review that follows loops for multiple rounds on defects the writer could have caught in the same turn, so review cost (subagent rounds, wall-clock) stays high. Measured across 4 projects (104 findings, per the audit's own post-recount total), 72% (75 of 104) of docs-review findings are edit-consistency defects — stale restatements (A), false claims about the writer's own work (B), unsupported claims (H), misplacement (C) — not omission-class gaps; kumiko branches ran up to 8 review rounds, dotfiles PR#40 ran 10 with rounds 4–10 prose-only.

## Users

- Orchestrator sessions and SDD implementer subagents in loom-adopting repos (monkey-skills, kumiko-zaiku-app-icons, dotfiles, yss) that edit `.md` prose mid-development on both Claude Code and Codex (both hosts consume `loom-code/agents/implementer.md` verbatim as the role prompt).
- kouko, who pays for every extra docs-review round.

## Smallest End State

One new numbered rule ("Prose-edit self-sweep") in `loom-code/agents/implementer.md`'s hand-written Role-contract section, firing when every file in the task's `Files touched` is `.md`, executed silently in the same generation — no checklist output, no tick marks, no self-score, no PASS claim.

- The rule's five verifiable actions: grep restatements of every changed claim; re-run the command behind every self-referential claim or downgrade it to "not verified"; walk the doc's own reading path; check agent-facing instructions against their target schema; N/A entries carry reasons.
- Plus: a pinned contract test, one evidence doc consolidating the 4-project finding-cause mining, and an A/B harness (case manifest + tally script + protocol) with a first A/B run.
- Branch stays unmerged until A/B results exist; effectiveness is NOT claimed in any shipped prose.

## Current State Evidence

- Forward: `loom-code/agents/implementer.md` Role contract holds hand-written rules 1–13 ending at "13. **Scoped inner-loop test runs.**"; rule 12 "**Prose-contract placement guard.**" already covers cause C for fix tasks, so the new rule extends an existing prose lane rather than opening one.
- Reverse: `loom-code/scripts/distribute.py` owns the two managed blocks in the same file ("BEGIN baseline-v1 — managed by loom-code/scripts/distribute.py" / "BEGIN rule-sheet-v1"), sourced from `loom-code/scripts/_baseline.md` and `_rule-sheet.md`; the new rule must live OUTSIDE both blocks, in the hand-written section, or distribute will overwrite it.
- Error: docs review's failure mode is recorded in `docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md` ("A document carrying many small real defects, reviewed by a sampler, yields new findings on every pass") and its prescription "a standing mechanism outranks another review round"; the reviewer contract `loom-code/agents/docs-reviewer.md` stays untouched (verdict-only role, judge for the A/B).
- Data: raw finding-cause tables from the 3 external projects sit in this session's scratchpad (`findings-kumiko.md` 52 findings, `findings-dotfiles.md` 16, `findings-yss.md` 22) plus monkey-skills' 14 from `docs/loom/audits/2026-08-11-yellow-finding-load-bearing-sample.md`; they land in-repo as the evidence doc.
- Boundary: the rule's firing condition reuses the plan grammar's `Review-weight: prose` precondition shape ("every file in `Files touched` is `.md` authored prose", `loom-code/skills/writing-plans/references/plan-format.md` §Review-weight); Codex consumes the same file via `spawn_agent` per `loom-code/skills/using-loom-code/references/codex-tools.md` §Re-binding loom-code's dispatch points onto Codex.

## Alternatives Considered

My take: Recommend the single-generation silent self-sweep; why — it is the only zero-extra-call variant, and the measured defect classes (A/B/H/C) are all decidable by actions the writer can run in the same turn; conditional reversal — if the A/B shows no reduction in first-round gating findings, drop the rule from the branch and record the negative result in the evidence doc.

- Chain-of-Verification (Dhuliawala et al. 2023, arXiv:2309.11495; EN sources: learnprompting.org, mirascope.com) — plan verification questions, answer them, then regenerate. Shipped and shown to reduce hallucination, but costs 2+ extra model calls per artifact; rejected for cost — our variant folds the verify step into the same generation.
- SelfCheckGPT-style multi-sample consistency (JA source: zenn.dev/lluminai_tech "自己チェックLLMを組み込む" — generate N times, route low-agreement output to human review) — N× generation cost; rejected for cost.
- Second docs-review round / weak-model pre-review — refuted in-repo: `2026-08-04` audit shows reviewer sampling never reaches an empty round on a defect-dense artifact; the user's seed proposal also explicitly excludes a pre-review.
- Harm gate on the reviewer — already tested and dropped in-repo (`2026-08-04` audit, treatment arms unchanged vs control).
- EN/JA divergence finding: JA literature includes a direct caution — NLP2025 P5-9 (anlp.jp) questions checklist efficacy in generative auto-evaluation — which is why this brief hard-binds "no effectiveness claim before A/B results" instead of assuming the EN self-verification consensus transfers.

## What Becomes Obsolete

Nothing is deleted in this arc; the candidate obsolescence is downstream — review rounds 2+ on prose tasks (measured, not assumed) and the user's original omission-class checklist proposal, which this brief supersedes with a cause-matched action list (the omission checklist remains a phase-2 candidate for from-scratch specs only). This is deliberate additive YAGNI-tension: accepted because the rule is 1 file / ~18 lines and the A/B decides whether it stays.

## Decision

Build a writer-side standing mechanism plus the measurement that decides its fate; touch one contract file only. Why: 4-project mining shows edit-consistency defects dominate where docs review actually loops, the 2026-08-04 audit prescribes "a standing mechanism outranks another review round", and silence + verifiable actions avoid both checklist-theater and judgment-prose failure modes.

- Build (1): evidence doc `docs/loom/audits/2026-08-31-docs-review-finding-causes.md` consolidating the 4-project cause distribution.
- Build (2): rule 14 "Prose-edit self-sweep" in `loom-code/agents/implementer.md` hand-written section, TDD-first via a pinned case in `loom-code/scripts/test_agent_contract.py`.
- Build (3): A/B harness under `docs/loom/dogfood/2026-08-31-prose-selfsweep-ab/` — protocol, 4 historical prose-task cases, tally script `loom-code/scripts/prose_selfsweep_tally.py` + test; dispatch runs from the session (implementer arms A/B × 2 reps, sonnet; judge = unchanged `docs-reviewer`; blind cause labelling).
- Build (4): CHANGELOG + version bump.
- Do NOT build: any change to `docs-reviewer.md` or `requesting-docs-review/`; any new mechanical section gate (existing validators already cover section presence/N/A); any second review stage; any checklist output format.

## Out of Scope

- The omission-class checklist for from-scratch specs (phase-2 candidate, blocked on this A/B).
- Restructuring `implementer.md`'s 13-rule narrative (user declined the extra structural-review dispatch; cost).
- Any edit to `product-principles/SKILL.md` (replay-workflow input + 4500 wordcap), `docs-reviewer.md`, `requesting-docs-review/`, or the sibling worktree's baseline corpus / reviewer prompts.
- Merging this branch or claiming effectiveness before A/B results.
- Codex-side live verification of the dispatch path (doc-sourced mapping only).

## Open Questions

- Case selection for the A/B: 2 kumiko + 2 monkey-skills historical prose tasks is the plan; if a task's pre-state cannot be reconstructed cleanly from git history, substitute another from the same project — resolved at harness-build time, recorded in the case manifest.
- Whether `Review-weight: prose` tasks are frequent enough in future arcs for the rule to fire often; if telemetry later shows near-zero fire rate, the rule is a candidate for `distill-sessions` review. N/A for this arc's deliverable.

## Diagrams

N/A — single-file contract edit plus a measurement harness; no multi-component flow a diagram would compress.

## Evidence paths appendix

- loom-code/agents/implementer.md (rules 12–13, managed-block markers)
- loom-code/scripts/distribute.py; loom-code/scripts/_baseline.md; loom-code/scripts/_rule-sheet.md
- loom-code/scripts/test_agent_contract.py
- docs/loom/audits/2026-08-04-docs-review-convergence-experiment.md
- docs/loom/audits/2026-08-11-yellow-finding-load-bearing-sample.md
- loom-code/skills/writing-plans/references/plan-format.md (§Review-weight)
- loom-code/skills/using-loom-code/references/codex-tools.md (§Re-binding)
- loom-code/skills/subagent-driven-development/SKILL.md (§Prose review-weight substitution)
