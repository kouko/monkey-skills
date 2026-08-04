# Brief: loom mechanism defect fixes from the 0.50.0 close-out (D-A / D-D / D-C / E-3)

Date: 2026-08-04
Source: HANDOFF-2026-08-04-174130 Block 2/5 (evidence recorded there verbatim) +
this session's git-history investigation + user approvals (this session).
Status: FROZEN — user approved Option A for D-A ("把 A 做完吧") and P1+P2 scope.

## Problem

Four loom-* mechanism defects were observed live during the 0.50.0 fix arc.
Two are code defects (D-A, D-D), two are one-sentence contract hardenings
(D-C, E-3). Backlog entries for D-A/D-D exist under `docs/loom/backlog/`
(2026-08-04-review-scope-stale-base-remedy-wrong-old-base,
2026-08-04-claim-copy-sweep-blind-to-py-module-docstrings).

## Verified root cause for D-A (overturns the handoff hypothesis)

Investigated against real git history this session:

- `review_scope.py:209` already computes `git merge-base HEAD <ref>` at
  refusal time; the printed old-base `099af0c9` WAS the true merge-base
  (`git merge-base 249887fd 4c2937d5` reproduces it; `249887fd` = the
  pre-rebase branch tip recovered from reflog).
- The 0490 branch had been cut from `f61837ed` — the tip of the previous
  arc's local branch `docs-loom-close-out-backlog-and-memory`, NOT a main
  commit — so merge-base..HEAD contained 7 foreign commits whose content
  was already squash-merged into main. Squash changes patch-ids, so
  rebase's duplicate-skip cannot drop them; replaying them conflicts
  (first foreign commit `f422f494`, exactly as observed).
- The remedy command is textbook-correct for merge/rebase workflows but
  unsafe in a squash-merge repo whenever the branch was cut from a stale
  merged tip — the second occurrence of this state (first:
  `docs/loom/memory/new-arc-branch-bases-on-origin-main-not-merged-tip.md`).

## Decisions (all user-ratified this session)

1. **D-A = Option A (mechanical fix + fallback caveat).** The remedy
   prefers the branch's reflog creation sha as the printed old-base when
   that sha is a descendant-or-equal of the merge-base AND an ancestor of
   HEAD; otherwise it falls back to the merge-base and prints one extra
   stderr caveat line pointing at a verifiable action (abort + substitute
   the reflog creation sha). Rationale: the remedy exists for
   already-wedged weak-model orchestrators; prose-judgment caveats alone
   are the documented weak-model failure mode
   (`feedback_weak_model_caveats_need_verifiable_action_not_judgment`).
2. **D-D**: `claim_copy_sweep.py` additionally scans `.py` MODULE
   docstrings (top-of-file string only, never the full file), reports
   hits with real file line numbers, and updates both its summary line
   and its printed leak list to name the new scope honestly.
3. **D-C**: one pinned sentence added to
   `plan-document-reviewer-prompt.md` §Verdict mapping making the
   per-check full-task sweep an explicit obligation.
4. **E-3**: one pinned pointer sentence in `requesting-code-review/SKILL.md`
   Step 3 (dead-arm context) to SDD's `dispatch-hygiene-notes.md`
   §Capacity-error recovery, paid for by trimming the unpinned
   `v0.6.0 / P15-12 Phase 2` version tag in Step 2 — net ≤ +2 words
   against the CHK-SKL-010 cap (current 4498/4500).
5. **Weak-model dogfood before finishing** (user directive, this
   session): D-A gets a live probe — reconstruct the stale-cut state in a
   sandbox repo, hand a weak model ONLY the refusal stderr, verify it
   un-wedges by following the printed remedy verbatim. D-C/E-3 get
   cold-reader probes; D-D is mechanically self-verifying (re-run the
   sweep on the "never biased" claim and see the `loom_gate_markers.py`
   docstring hit).
6. The D-A backlog entry's now-disproven hypothesis paragraph is
   corrected in-place (honest record: hypothesis overturned by
   investigation).
7. loom-code plugin content changes → version bump 0.50.0 → 0.51.0 with a
   named CHANGELOG entry. `scripts/claim_copy_sweep.py` is top-level, no
   bump (precedent: #638/#643 arcs).

## Smallest End State

1. `review_scope.py` stale-base remedy prints the branch-creation sha as
   old-base in the stale-cut state; falls back to merge-base + caveat
   line when the creation sha is unavailable or unusable; module
   docstring and the `AGENTS.md` mirror describe the new semantics.
2. `claim_copy_sweep.py` finds the `loom_gate_markers.py` module-docstring
   copy of the "never biased" claim, and its output names the extended
   scope in the summary line and the leak list.
3. `plan-document-reviewer-prompt.md` carries the per-check sweep
   obligation sentence.
4. `requesting-code-review/SKILL.md` carries the capacity-recovery
   pointer within the word cap.
5. Corrected D-A backlog entry; dogfood record with probe verdicts;
   plugin bumped to 0.51.0 with CHANGELOG entry.

## Out of scope

- D-B (reviewer test-running carve-out) — user decision pending; touches
  agent contracts (P3 in the handoff).
- E-1 (extraction-to-references refactor of the two ceiling-bound review
  SKILL.md files) — standalone future arc.
- E-2 (plan-format example row) — optional, not taken this arc.
- Any change to `loom_gate_markers.py` or the gate-markers spec — the
  remedy shape `git rebase --onto <new> <old> HEAD` itself is unchanged;
  only which sha fills `<old>` changes.

## Copy-sweep partition for the remedy claim (taken this session)

`claim_copy_sweep.py --claim "git rebase --onto"`: 12 operative hits.
Must change: `AGENTS.md:119` (names `<base_sha>` as the old-base — the
placeholder semantics change). Must NOT change: memory/backlog/plans/specs
records (historical evidence), `requesting-code-review/SKILL.md:96`
("a ready-to-run remedy" — stays true), CHANGELOG (frozen). The
`review_scope.py` module docstring copy is out of the sweep's .md scope
but updates with T2 (same file). Synonym leak stays open, as the tool
itself states.
