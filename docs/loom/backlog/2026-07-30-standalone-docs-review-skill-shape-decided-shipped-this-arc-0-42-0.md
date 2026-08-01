---
name: 2026-07-30-standalone-docs-review-skill-shape-decided-shipped-this-arc-0-42-0
description: Standalone docs-review skill — shape decided this arc (0.42.0)
status: SHIPPED
origin: 2026-07-30 four-stream root-cause reassessment of the doc-branch review loops (PR #626–628 archaeology; 30-item repo-evidence scan; review-machinery map; 35-day session mining that found ~10 doc-artifact loops of 2–6 rounds vs ~3 code loops all converging in 2). User discussion following the reassessment.
start: unpark if, after 0.41.0's blocking-class change has governed 2–3 docs-heavy branch close-outs, either (a) a mixed (`.md`+code) branch runs a pathological review loop — the second measured loop was mixed and 0.41.0's docs-only trigger does not cover it (`docs/loom/specs/2026-07-30-docs-review-blocking-class.md:196-201`) — or (b) the docs-mode dispatch-prose override fails in practice (a reviewer ignores the Step 1 override and falls back to code rubrics). If prose branches converge in 1–2 rounds and neither trigger fires, close this entry instead — the mode-inside-code-review design is sufficient.
---

- **Post-merge follow-up (open, cheap — NARROWED after the pre-merge probe ran)**: the
  weak-orchestrator CONTRACT question is answered pre-merge — a sandbox with the
  branch's skill/agent at project level (`.claude/skills` + `.claude/agents`) under
  headless `claude -p --model sonnet` executed the full two-round flow correctly (cap
  STOP, no third round, mint refused on NEEDS_REVISION, not-fixed vs resurfaced
  distinguished; dogfood record §Weak-orchestrator probe). What remains post-merge:
  (a) installed-plugin WIRING fidelity — does the three-way routing fire through the
  real requesting-code-review entry + hook preloads on device; (b) the haiku-arm
  noise-rate observation (dogfood addendum) on the first real docs branches. Sonnet is
  the orchestrator floor by the operator's own model-dispatch rules (haiku excluded
  from multi-step git workflows), so no haiku-orchestrator probe is owed.
- Start (historical — the unpark condition that was in force before this arc shipped,
  kept for record): unpark if, after 0.41.0's blocking-class change has governed 2–3 docs-heavy branch
  close-outs, either (a) a mixed (`.md`+code) branch runs a pathological review loop — the
  second measured loop was mixed and 0.41.0's docs-only trigger does not cover it
  (`docs/loom/specs/2026-07-30-docs-review-blocking-class.md:196-201`) — or (b) the docs-mode
  dispatch-prose override fails in practice (a reviewer ignores the Step 1 override and falls
  back to code rubrics). If prose branches converge in 1–2 rounds and neither trigger fires,
  close this entry instead — the mode-inside-code-review design is sufficient.
- Origin: 2026-07-30 four-stream root-cause reassessment of the doc-branch review loops
  (PR #626–628 archaeology; 30-item repo-evidence scan; review-machinery map; 35-day session
  mining that found ~10 doc-artifact loops of 2–6 rounds vs ~3 code loops all converging in 2).
  User discussion following the reassessment.
- **Shape decided (user's call, 2026-07-30): a standalone skill with clean jurisdiction — NOT a
  prose-reviewer agent grafted onto the shared requesting-code-review skeleton.** Recorded so a
  future session does not re-litigate skill-vs-shared-skeleton. Sketch agreed with the user:
  - New skill (working name `loom-code:requesting-docs-review`, sibling of
    requesting-code-review) owns: the five prose dimensions, instruction/evidence blocking
    class, `check_doc_citations.py`, whole-artifact scope, and a **prose-native reviewer agent
    contract** (today's docs mode is a ~900-word per-dispatch override on the code-shaped
    `code-reviewer` agent — `requesting-code-review/SKILL.md:97`).
  - Convergence machinery ships inside it, not alongside: a round cap (critics' 2-round +
    user-authorized-breach precedent) and append-corrections-not-rewrites. Without the cap the
    9-round loop just relocates — prose still has no test oracle
    (`docs/loom/audits/2026-07-28-doc-branch-review-loop-audit.md:46-49`).
  - Routing concentrates in `finishing-a-development-branch` Step 1: pure-docs → new skill;
    mixed → per-file split (`.md` files to the docs reviewer, code files to code-reviewer,
    verdicts aggregated); pure-code path unchanged. requesting-code-review sheds its Step 1
    docs paragraph.
  - Boundary vs GENERATE-station critics is non-overlapping by phase: completeness-critic /
    design-critic critique drafts during writing; this skill gates committed doc changes at
    branch close-out.
  - Standalone-only dividend: SDD gains `Review-weight: prose` dispatching the same
    docs-reviewer agent per-task — doc-only SDD tasks today get the full code triad and the
    tests-dimension caveat verbatim-repeats across rounds
    (`subagent-driven-development/SKILL.md:104-117`).
- Independently actionable before unparking (cheap, orthogonal): the whole-branch round cap —
  whole-branch review is the only loop in the family with no cap at all
  (`docs/loom/specs/2026-07-29-review-round-ledger-and-bad-fix-recheck.md:20-33`) — and the
  mixed-branch per-file split, which stands on its own even if this skill never ships.
