# Ceremony cost: today's process vs the new model (v7), on 3 shipped changes

Target model read: `simple-loom-concept-model-v0.md` §2, §4, §5, §7.
Measurement only — no recommendation.

## Selected changes

| category | plan | spec/brief | PR | merge commit (main) |
|---|---|---|---|---|
| (i) refactor/cleanup | `docs/loom/plans/2026-08-31-loom-code-script-helper-extraction.md` | `docs/loom/specs/2026-08-31-loom-code-script-helper-extraction.md` | #771 | `5a437eb1` |
| (ii) feature adding behavior | `docs/loom/plans/2026-08-31-adversarial-audit-station.md` | `docs/loom/specs/2026-08-31-adversarial-audit-station.md` | #772 | `3ef8922a` |
| (iii) docs/prose-only (mostly) | `docs/loom/plans/2026-09-01-prose-edit-self-sweep.md` | `docs/loom/specs/2026-08-31-prose-edit-self-sweep.md` | #775 | `01e4fe54` |

Caveat on (iii): not pure docs — it also ships one small internal measurement
script (`loom-code/scripts/prose_selfsweep_tally.py` + its test), because the
change's own deliverable is an A/B-measured prose contract rule. No shipped
PR in the 2026-08-20+ window touched only `.md` files; this was the closest
fit (core deliverable is a prose rule in `implementer.md`).

---

## (i) loom-code script helper extraction — PR #771

### Today (measured)

| metric | value | source |
|---|---|---|
| a. commits in branch | 31 | `gh pr view 771 --json commits` |
| b. review dispatches | ≈22 = plan-review 3 rounds + 5 DL-amendment re-reviews (8) + task-level fan-outs 8 (plan Notes: "observed reviewer fan-outs: 8") + whole-branch 2 arms × 3 rounds (6) | plan Notes, `## Decision Log` DL-1..DL-6, line "observed reviewer fan-outs: 8 (rounds 7, batch reopens 2)" |
| c. human decision points | 2 = 1 (user-approved the 2-round revision cap override) + 1 (PR merge) | plan Notes: "Round-2 revision (2026-08-31, user-approved after the 2-round cap)"; "Kickoff sweep... No kickoff briefing issued." (zero one-way-door decisions found) |
| d. artifacts written | 7 = spec/brief file (new) + plan.md (new) + 1 new memory entry + memory/README (touched) + INDEX.md (touched) + dogfood fingerprint line (touched) + CHANGELOG entry (touched) | `git show 5a437eb1 --stat` |
| e. wall-clock | not reliably measurable — plan dates are all `2026-08-31`; PR commit timestamps span 08:09–10:22 UTC same day, but PR #772's 67 commits in 5 min shows commit timestamps are compressed/batched, not real session duration | `gh pr view --json commits` |

### New model (arithmetic)

Assumptions: `needs-design: no` (refactor, no user-facing interface, no new
multi-state behavior — §2b rule (a)/(b) both fail). 19 SDD tasks unchanged.
Plan's own Decision Log names 3 SDD waves ("wave 1", "wave 2", "wave 3");
each wave's diff (≥9 files) exceeds the 8-file/400-line checkpoint
threshold (§5), so each wave-end fires a checkpoint; the last wave-end
checkpoint is taken as the mandatory branch-end checkpoint (§5) — K = 3.
No `review: after-task` tags in the plan. Not a first use — no scaffold commit.

- a. commits = intent(1) + approval-only(1) + plan(1) + approval-only(1) + 19 task commits + K(3) review-only = **26**
- b. review dispatches = K(3) + 0 spec review = **3**
- c. human decisions = approvals(intent + plan = 2) + PR merge(1) = **3**
- d. artifacts = intent.md + plan.md + review.json (no spec.md) = **3**

---

## (ii) Adversarial audit station — PR #772

### Today (measured)

| metric | value | source |
|---|---|---|
| a. commits in branch | 67 | `gh pr view 772 --json commits` |
| b. review dispatches | ≈58 = plan-review 8 rounds + task-level fan-outs 34 (plan Notes: "observed reviewer fan-outs: 34 (rounds 23, batch reopens 2)") + whole-branch 2 opus code arms + 2 opus docs arms over 3 rounds (≤12) + the station firing on itself twice (2 audit dispatches, plan Notes: "station fired twice...first audit reproduced 7...second reproduced 6") + 1 cold-reader firing recorded in Notes ("cold reader: fired") | plan `Plan-document-reviewer verdict: PASS (round 8)`; Notes lines on fan-outs, whole-branch review, station self-firing |
| c. human decision points | 2 = 1 (kickoff decision: `docs/loom/ATTACK-CATALOGUE.md` naming, "kouko 2026-08-31") + 1 (PR merge) — plus one *documented bypass*: "Autonomy note... the orchestrator judged each round a new variant... and proceeded" without asking kouko, i.e. today's practice explicitly skipped a would-be decision point | plan Notes: "Kickoff decision: store path..."; "Autonomy note (2026-08-31)..." |
| d. artifacts written | 17 = spec/brief(new) + plan.md(new) + ATTACK-CATALOGUE.md(new, product artifact) + BACKLOG.md(touched) + 4 new backlog entries + dogfood record(new) + dogfood fingerprint line(touched) + memory/README(touched) + 5 new memory entries + CHANGELOG entry(touched) | `git show 3ef8922a --stat` |
| e. wall-clock | not measurable — PR commits span only 10:42–10:47 UTC (5 min) for 67 commits; this is a compressed/batch-committed timestamp series, not the real working duration; plan dates are all `2026-08-31` | `gh pr view --json commits` |

### New model (arithmetic)

Assumptions: `needs-design: yes` — the station adds a CLI subcommand
(`check_attack_catalogue.py signal`) and multi-state prose behavior (fires /
doesn't fire, STOP routing) with no prior DESIGN.md/ui-flows coverage,
satisfying §2b rule (a) and (b). 16 SDD tasks. Plan Notes name 2 explicit
SDD waves plus a late Task-16 addition; assumed 3 checkpoint-eligible
wave-ends given the branch's total diff (45 files, 5056 lines, comfortably
over the 8-file/400-line threshold in every wave) — K = 3, last one doubling
as branch-end. One spec review (needs-design: yes).

- a. commits = intent(1) + approval-only(1) + spec(1) + review-only-spec(1) + approval-only-spec(1) + plan(1) + approval-only(1) + 16 task commits + K(3) review-only = **26**
- b. review dispatches = K(3) + spec review(1) = **4**
- c. human decisions = approvals(intent + spec + plan = 3) + PR merge(1) = **4**
- d. artifacts = intent.md + spec.md + plan.md + review.json = **4**

---

## (iii) prose-edit self-sweep — PR #775

### Today (measured)

| metric | value | source |
|---|---|---|
| a. commits in branch | 28 | `gh pr view 775 --json commits` |
| b. review dispatches | ≈14 = plan-review 2 rounds + task-level fan-outs 8 (plan Notes: "observed reviewer fan-outs: 8 (rounds 8...)") + whole-branch review (≥2 rounds: round 1 `NEEDS_REVISION`, then fixes, DL-4) + station self-firing on this branch (audit fired + cold reader fired = 2) — **excludes** the 16 implementer+judge dispatches for the A/B measurement itself, which the plan explicitly marks as "session work AFTER this plan's tasks complete... not an SDD task" | plan Notes fan-out line; DL-4 "Finishing Step 3 whole-branch (opus) returned NEEDS_REVISION..."; "adversarial audit: fired..."; "cold reader: fired..." |
| c. human decision points | 2 = 1 (isolation-hold release: "先收尾吧" per Notes "Close-out (2026-09-01): isolation hold RELEASED by the user") + 1 (PR merge) | plan Notes |
| d. artifacts written | 16 = spec/brief(new) + plan.md(new) + evidence doc(new) + dogfood A/B dir, 4 files(new) + dogfood fingerprint line(touched) + memory/README(touched) + 3 new memory entries + BACKLOG.md(touched) + 2 new backlog entries + CHANGELOG entry(touched) | `git show 01e4fe54 --stat` |
| e. wall-clock | not measurable — PR commits span only 23:58–00:02 (4 min) for 28 commits, a compressed/batch series; plan/spec dates ("brief names 2026-08-31, actual artifacts 2026-09-01") show a date drift the plan itself flags as non-substantive | `gh pr view --json commits`; plan Notes |

### New model (arithmetic)

Assumptions: `needs-design: no` — rule 14 is a single silent contract rule
(§2b condition (a) fails: no user-visible interface touched by the
prose rule itself, the tally script is internal dev-tooling not an
"external API"; condition (b) is judgment — a single new rule is not
"multi-state/multi-object behavior", so `no`). 6 SDD tasks. Total diff
(24 files, 1936 lines) clears the threshold on its first wave; assumed 2
checkpoints (one mid-branch wave-end + branch-end) — K = 2.

- a. commits = intent(1) + approval-only(1) + plan(1) + approval-only(1) + 6 task commits + K(2) review-only = **12**
- b. review dispatches = K(2) + 0 spec review = **2**
- c. human decisions = approvals(intent + plan = 2) + PR merge(1) = **3**
- d. artifacts = intent.md + plan.md + review.json (no spec.md) = **3**

---

## Totals

| metric | today (i+ii+iii) | new model (i+ii+iii) |
|---|---|---|
| a. commits | 31 + 67 + 28 = **126** | 26 + 26 + 12 = **64** |
| b. review dispatches | 22 + 58 + 14 = **94** | 3 + 4 + 2 = **9** |
| c. human decision points | 2 + 2 + 2 = **6** | 3 + 4 + 3 = **10** |
| d. artifacts written | 7 + 17 + 16 = **40** | 3 + 4 + 3 = **10** |
| e. wall-clock | not measurable (see per-change rows) | not applicable — no shipped instance exists |

---

## Where the new model is HEAVIER

**c. human decision points — heavier on all three changes (10 vs 6 total; +1 on every single change).**
Cause: §4's fixed floor — "簽核點：intent → (spec) → plan → PR，每 change 最多四、最少三" (every change gets a minimum of 3 approval-only commits plus PR merge, rising to 4 when `needs-design: yes`). Today's actual practice frequently found *zero or one* explicit human decision needed per change — e.g. #771's own kickoff sweep recorded "zero one-way-door decisions... No kickoff briefing issued," and #772's orchestrator explicitly *proceeded without asking* kouko on a judgment call ("Autonomy note"). The new model's per-change approval floor is a standing cost that today's process only pays when a real fork exists; under the new model it is paid every time, whether or not anything actually needs a human call.

**d. artifacts — marginally heavier for change (ii) only (4 vs a today-equivalent ~3 core per-change artifacts: spec + plan + dogfood-record).**
Cause: §2a mandates `review.json` as a committed per-change artifact at every checkpoint. Today, review verdicts for #772 lived in ephemeral packets / PR review threads / a dogfood record, not as a committed `docs/loom/<id>/review.json`; the new model turns "review happened" from an ephemeral/PR-thread fact into a standing committed file, adding one artifact type the old process didn't require to commit. (For (i) and (iii) this is not heavier: today's total *artifact file count* — 7 and 16 respectively — was inflated by memory/backlog entries the model itself says are NOT per-change artifacts (§2a), so on a like-for-like "core per-change artifact" comparison the new model is lighter there, not heavier.)

No other cell (a, b) is heavier under the new model for any of the three changes — both commit count and review-dispatch count are substantially lower in every case, driven mainly by §5 collapsing "review every task + review every batch + whole-branch review + plan-document-reviewer per-amendment re-review" into one checkpoint contract fired only at wave-end/branch-end.

## Could not measure

- **Wall-clock (e)** for all three changes: PR commit timestamps are compressed into a few minutes regardless of actual session length (67 commits in 5 minutes for #772), and plan/spec documents record only calendar dates, not session start/end times. No reliable proxy for real working duration was found in the plan, spec, or PR data.
- **Exact wave count / per-wave diff size** for computing K precisely under the new model: today's plans don't track a "checkpoint" concept, so wave boundaries were inferred from Decision Log wave-tags ("SDD wave 1/2/3") rather than read off an explicit ledger. K values above are stated assumptions, not measured facts.
- **DL-amendment count for (ii) and (iii)**: DL amendments are individually described in prose but not all carry an explicit "re-reviewed as round N" marker, so the review-dispatch totals for those two changes are lower-bound estimates built from the numbers the plans do state explicitly (fan-out lines, round numbers), not an exhaustive recount of every prose amendment.
