# Brief: bounded auto-third-round + fix-dispatch / finishing-entry hardening

Date: 2026-08-06
Status: FROZEN (user: 「開跑吧 三件一起收」 — endpoint = PR, continuous)
Consumer: writing-plans → SDD; ships as loom-code 0.62.0

## Problem

Three findings from the 0.61.0 retrospective, all evidence-backed:

1. **The docs 2-round cap fired in three consecutive arcs (0.59.0 /
   0.60.0 / 0.61.0) with identical shape**: round-2 NEEDS_REVISION
   carrying ≤2 NEW 🟡 with all prior findings fix-verified → user
   authorized round 3 every time (100% authorization, zero course
   changes) → round 3 converged in one scoped delta every time. The
   ask carries no decision information — it is the pump class 0.58.0
   exists to eliminate. n=3 meets the legislative threshold.
2. **fix-round-writes-defects, placement variant** (memory entry
   `splicing-into-a-pinned-sentence-creates-false-readings`): fix
   implementers splice new contract material into existing pinned
   sentences; presence-pins stay green while the joint reading flips.
   No dispatch surface currently warns fix appliers.
3. **Skill-version skew across compaction**: post-compaction the
   orchestrator ran finishing from a stale (0.50.0) cached skill text
   — wrong privacy-scan path (one lost locate round) and the 0.59.0
   backlog-close duty silently not run (zero-hit this time, real risk
   next time). No entry sentence tells the conductor to Read the
   current SKILL.md before executing.

## Smallest End State

1. **requesting-docs-review Directive 1 gains a bounded auto-third
   round** with purely mechanical conditions readable from the
   reviewer's structured verdict (never a semantic judgment):
   - conditions, ALL required: (a) every prior-round finding
     fix-verified (zero surviving); (b) NEW findings: zero 🔴 and
     ≤2 🟡; (c) no auto-third-round has already run on this branch
     (once per branch).
   - shape: the orchestrator runs ONE delta-scoped round 3
     automatically (scope = the NEW findings' fixes only) and
     REPORTS the auto-round in the terminal rollup — visible, not
     silent.
   - any other round-2 shape → STOP and surface (unchanged).
   - round-3 verdict other than PASS / PASS_WITH_NOTES → hard STOP,
     surface; a round 4 never runs without explicit user
     authorization.
   Word ceiling: rdr is at 4122/4130 — this edit REQUIRES a
   deliberate ceiling raise in test_rdr_extraction_pointers.py
   (changelog-noted; banked-headroom contract honored). All
   cap-stating sites inside rdr SKILL.md (frontmatter description,
   :19, :36, :82, :152, :164, :173) reworded consistently; verbatim
   pins in test_requesting_docs_review_skill.py updated; RED-first.
2. **Neighbor cap-statements swept** (same-PR contradiction sweep,
   the semantics-change duty): finishing-a-development-branch's
   cap-STOP bullet routes on rdr's new contract by POINTER (does not
   copy the conditions — anti-copy convention); requesting-code-review
   :90 and agents/docs-reviewer.md :519 one-line rewords.
   references/design-evidence.md stays historical (evidence tails,
   not operative rules). Distinct caps (SDD 3-round, writing-plans
   2-round, continuous-mode) are OUT of population — different loops.
3. **Fix-dispatch placement guard**: one sentence in finishing Step 4
   (the fix-application preconditions, :135-137 area) + one rule in
   agents/implementer.md's role contract: new contract material goes
   in its OWN sentence (or inside the placeholder it governs), never
   spliced into an existing pinned sentence; cite the memory entry.
   Pin tests for both.
4. **Finishing entry duty**: one sentence in the conductor paragraph
   (:14 area): before executing, Read the CURRENT SKILL.md from the
   installed plugin — never run the flow from memory or a compacted
   summary (version-skew incident, 2026-08-06). Pin test.
5. loom-code → 0.62.0 (both plugin.json manifests + CHANGELOG +
   shipping-version pin rewrite in test_docs_review_blocking_class.py
   :215-220).
6. **Haiku probes**: (a) new Directive 1 + a conditions-met round-2
   verdict fixture → auto-runs ONE scoped round 3 and reports it;
   (b) conditions-not-met fixture (3 new 🟡, or a 🔴, or unverified
   prior finding) → STOP and surface; (c) finishing entry duty —
   what must the conductor do before Step 1. Dogfood report under
   docs/loom/dogfood/.

## Out of scope

- SDD's 3-round NEEDS_REVISION cap, writing-plans' 2-round plan
  reviewer cap, continuous-mode's accounting (different loops,
  untouched).
- Any change to what counts as 🔴/🟡 or to the fix-verification
  protocol itself.
- Retro-editing design-evidence.md's historical quotes.

## Decisions

- Discriminator is count/verdict-shape ONLY (zero 🔴, ≤2 new 🟡,
  zero surviving, once per branch) — "non-semantic finding" was
  rejected as a condition because it requires judgment prose, which
  weak models self-certify past (memory: verifiable-action-vs-
  judgment caveats).
- Worst case is bounded by construction: a genuinely divergent loop
  costs one extra scoped delta dispatch, then hard-stops at round 3
  — the cap moves one notch, it does not disappear.
- Sample-bias caveat accepted: n=3 is same-repo same-work-class; the
  mechanical conditions are repo-agnostic, so bias affects trigger
  frequency, not safety.
- Ceiling raises are deliberate acts: new ceiling pinned at
  (new count + small margin), CHANGELOG-noted.
- Counting convention len(text.split()); verified at plan time:
  rdr 4122/4130 (raise required), finishing 4232/4500 global-only,
  implementer.md unpinned.
