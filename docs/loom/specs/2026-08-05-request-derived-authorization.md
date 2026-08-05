# Brief: request-derived authorization (B-full, reshaped) + ask-triage SSOT

Date: 2026-08-05
Status: FROZEN (user: 「照 reshape 版凍結 brief 開跑」; complexity-critique
verdict RESHAPE applied — per-station mode branches deleted in favor of
single-point recognition + station-local deletions)
Consumer: writing-plans → SDD; ships as loom-code 0.58.0

## Problem

Measured across 6 projects / 49+ sessions: user pump phrases cluster
~10:1 after PR/review/plan/brief language versus limit-recovery. The
waste is AUTHORIZATION re-asking: the same publish action is gated by
three skills, `Open a PR? (y/N)` has never been answered No, and
stage-to-stage "go" pumps exist only to hand control back. The
continuous-mode doctrine ALREADY removes every one of these stops —
what is missing is only the entry: recognizing that a request naming a
publish endpoint IS the explicit opt-in. Decision-side ask-minimization
(three-way triage) works but its vocabulary is restated in fragments
across skills instead of being pointed at.

Unifying principle: **authorization derives from the request — given
once at entry, never re-asked per station; questions resolvable by
checking sources or researching are resolved, not asked.** Hard gates
(NEEDS_REVISION, privacy BLOCK, one-way-door briefing, UI acceptance,
BLOCKED, merge) are not authorization and never auto.

## Users

- The owner running multi-stage loom arcs (target: brief approval +
  merge = 2 stops per arc).
- Weak-tier subagents executing the wording (probe-gated, both
  directions).

## Smallest End State

Partition A — endpoint recognition, decided ONCE at entry:
1. `using-loom-code/SKILL.md` §Continuous mode: opt-in is ALSO
   recognized from a kickoff request that names a publish endpoint
   ("finish this branch", "ship it", "開 PR", "run to PR"); the
   recognition is recorded in one line in the plan header
   ("endpoint named: yes → continuous"); a request naming no endpoint
   never triggers; 「一站一站來」 restores human-pumped mode at any
   point. Named deliverables: recognition sentence + non-trigger
   sentence + escape-hatch sentence + pin test.
2. `using-loom-code/references/continuous-mode.md` §Entry: the same
   recognition at doctrine level; STOP contract and never-auto-merge
   unchanged. Named deliverables: entry paragraph + pin test.

Partition B — station-local deletions (keyed to the REQUEST, never to
the mode recording — stations stay correct standalone):
3. `finishing-a-development-branch/SKILL.md`: Step 11's
   `Open a PR? (y/N)` ask is DELETED — every §When to use trigger names
   the close-out endpoint, so the authorization always arrived with the
   request; Step 11 auto-opens the PR (privacy gate, PR-carrier check,
   both merge paths, loud report all unchanged). The one ambiguous
   trigger ("I'm done here, what's next?") confirms intent at ENTRY
   (§When to use note), never at the tail. Neighbor sweep: Phase-6
   diagram line, delegation-table row 6, §ASK rationale paragraph all
   restate the old ask — update in the same task (falsified-neighbor
   duty). Named deliverables: Step 11 rewrite + entry note + 3 neighbor
   edits + pin rewrites (test_finishing_step7_privacy_gate.py step-11
   assertions; test_finishing_merge_path_guidance.py slice marker).
4. `requesting-code-review/SKILL.md` Push-as-trigger steps 4/6: after
   PASS, the push WAS the request — execute and report loudly, no
   re-ask; after PASS_WITH_NOTES, push carrying the findings into the
   report (aligns with finishing Step 3 and continuous row 6);
   NEEDS_REVISION unchanged; sync-marker's 1-row §When to use summary
   swept in the same edit. Named deliverables: steps 4/6 rewrite +
   summary-row sweep + pin test.
5. `subagent-driven-development/SKILL.md` §Asking the user gate ①
   "always confirm" row: one clause — the confirm is asked ONCE; a
   kickoff request that already names the endpoint IS that ask, and
   stations report loudly instead of re-asking; merge/deploy/delete/
   paid runs always confirm regardless. Named deliverables: clause +
   pin test.

Partition C — ask-triage SSOT (net text REDUCTION):
6. Gate ①'s three-way triage gains a one-sentence SSOT marker;
   finishing's and rcr's ask-moments point at it by STABLE HEADING
   TEXT (never section numbers — cross-file-§refs Shotgun-Surgery
   memory) and drop any restated fragment found during implementation.
   NO new pre-ask duty sentence (the triage already mandates
   "checkable → look it up, never ask"; a restatement is drift
   surface, not strengthening). Named deliverables: marker sentence +
   pointer edits + pin test.

Partition D — bump + verification:
7. loom-code → 0.58.0 (both manifests + CHANGELOG + shipping-version
   pin rewrite to 0.58.0).
8. Haiku cold-read probes, five legs: (a) endpoint-named request at
   close-out → auto-opens PR, no ask; (b) endpoint-unnamed request →
   still asks; (c) merge never auto in both; (d) checkable-fact
   question → resolved, not asked; (e) ambiguous "done" trigger →
   confirms at entry. Probe report under docs/loom/dogfood/.

## Alternatives considered

- Original B-full (per-station endpoint branches): RESHAPED away —
  duplicates continuous-mode logic into three stations (+400-500
  words), the dual-copy drift class this repo's memory store records
  most often.
- B-lite / global CLAUDE.md opt-in / pre-ask interceptor agent: all
  rejected earlier (user ratification + no decision-side failure
  evidence).

## What becomes obsolete

- finishing Step 11's `Open a PR? (y/N)` + its restatements (diagram,
  table row, rationale list).
- rcr push-trigger re-ask on PASS + PASS_WITH_NOTES push-anyway ask.
- Triage fragments outside gate ① (replaced by pointers).

## Out of scope

- Merge (never-auto-merge restated, not weakened); brainstorming brief
  sign-off; one-way-door stops; UI acceptance; privacy gates;
  git-guard markers; docs 2-round cap; worktree-removal ask (Step 12);
  loom-pipeline / Codex ports.

## Decisions

- Endpoint recognition is judged ONCE at kickoff (anchor phrases are
  examples; operative test = "does the request name a publish
  endpoint?"), recorded in the plan header; a mid-arc 「一站一站來」
  or scope change flips the recording from that point.
- Station-local rules are keyed to the request (locally checkable),
  NOT to the mode recording — standalone invocations stay correct.
- SSOT pointers anchor on stable heading text, never numbers.
- Counting convention `len(text.split())`; ceilings: rcr ≤3900
  (headroom 112), SDD ≤3900 (headroom 76) — Partition B/C net deltas
  budgeted at plan time.
- Pin survey (plan-time input, done): `Open a PR? (y/N)` pinned at
  test_finishing_step7_privacy_gate.py:79,174 +
  test_finishing_merge_path_guidance.py:61; rcr/SDD target sentences
  unpinned; continuous-mode pins are additive-safe phrase checks.
