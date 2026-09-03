# Checkpoint cost — orchestrator's observations and recommendation candidates

Written by the orchestrator during build (2026-09-03, at W0-04 in flight), at
kouko's request. This is **input** to `evidence/checkpoint-cost.md`, which the
blind-runner writes at branch end from `git log` and `review.json` — the
numbers below are what the orchestrator saw and must be recomputed there, not
copied. The recommendations are candidates; the blind-runner keeps, drops or
reorders them against the recomputed numbers, and the table's one-line
recommendation stays a recommendation (user-decided 2026-09-03: no coefficient
changes in this change).

## Observed at HEAD f0b11a1a (spec stage complete, 3 of 8 tasks committed)

| measure | observed | note |
|---|---|---|
| commits on branch (`git rev-list --count 4e25360c..HEAD`) | 46 | 2 code commits; the rest are spec versions (7), review-only (9), dispatch records (12), evidence (6), intents (5), plan (1) |
| dispatches (`review.json` `dispatch[]`) | 36 | reviewer 16, blind-runner 8, adversary 8, implementer 4 |
| spec review rounds | 8 | design assumed 1–2; rounds 1–4 found design defects, rounds 5–8 were mostly disclosure wording, with two real gate defects (round 6) and one real vendor split (round 5) |
| findings raised / closed | 45 / 45 | ids spec-C1..C13, S1..S8, R1..R23, B1..B4 |
| per arm | sonnet reviewer 110–127k tokens, 3–5 min; red team 110–143k, 3–8 min; cold read 93–106k, 2–3 min; Codex ~5 min | from task notifications |
| per implementer task | 7–12 min, one commit, package suite 2–2.5 min | W0-01 stalled before its commit once (background test run) |

## Where the cost sits
1. **Every spec round is full-strength** — two reviewers + cold read + red team, regardless of how many findings the previous round left. Round 7 had one stale sentence to check and still ran four arms.
2. **The red team has no stopping condition on prose** — 7 of 8 rounds NEEDS_REVISION; on a spec, "a behaviour the text fails to forbid" is unbounded, and from round 5 on most findings were "state this residual" rather than "this design is wrong".
3. **Three record commits per round** (dispatch, evidence, review-only): 24 of the 46 commits exist only to record 8 rounds. This is the #771 coefficient (34 vs 31) multiplied by the spec stage.

## Recommendation candidates (coefficients and stopping conditions, not rule semantics)
- **Fix rounds re-dispatch only the arm that said NEEDS_REVISION**; the arms that passed re-read only the diff of the fix. (Rounds 6–8 would have been 1–2 arms, not 4.)
- **Red team on a spec: at most two rounds.** After that, residuals it names are recorded in the spec as stated residuals without a further NEEDS_REVISION — the spec's own "stated residual" pattern already exists for this.
- **Dispatch record + evidence in one commit**; the review-only commit stays separate (the checker needs it alone). 3 → 2 commits per round.
- **Codex as second vendor earned its place** (round 5 fatal was Codex-only, round 6 contradiction Codex-only), so keep it on the read arm; do not spend it on cold read or red team.
- Not recommended: relaxing "three arms PASS" for code deltas — the two real gate defects of round 6 came from the red team on the tightened rules, exactly where it should fire.

The blind-runner appends the final per-checkpoint table (W0-04 after-task, W0-05 after-task, W0 wave-end, W1 branch-end, ship close-commit round) with recomputed totals, and writes the single recommendation line.

## Addendum at HEAD d9da281a (after-task W0-04 closed, W0-05 in flight)

| measure | observed |
|---|---|
| commits on branch | 88 (code 10: W0-01..03 one each, W0-04 one + six fixes; probes 3; the rest records) |
| dispatches | 61: reviewer 30 (incl. one opus design review), blind-runner 9, adversary 11, implementer 11 |
| after-task W0-04 | 5 review rounds, 6 fix dispatches, 3 designs (content-parsed → structural → regenerate-and-compare), spec amended three times (v10–v12) with three narrow spec rounds |
| spec rounds total | 11 (8 full + 3 narrow) |

What the W0-04 sequence shows: a rule that reads diff content attracts an unbounded series of parser-edge attacks (rename, deletion, BOM, symlink typechange, body decoy, headingless last-wins, CRLF, non-UTF-8); each fix round found a new one until the design changed to byte equality against a regenerated canonical. Two rounds were lost to the orchestrator's own packet errors (deletion-as-transition; the first "structural" spec had five sub-conditions). The user-requested opus design review (one dispatch, 2 minutes) settled in one pass what six sonnet fix rounds had not.

Recommendation candidates added:
- **Redesign trigger**: a second NEEDS_REVISION on the same checkpoint sends the finding history to a fresh higher-tier agent for a one-question design review before any further fix dispatch (open intent 2026-09-03-fix-round-cap-triggers-redesign).
- **Adversarial probes before implementation** for gate rules: W0-05 ran this way (11 probes first, one xfail as the implementer's RED); compare its round count with W0-04's when it closes.
- **Content-reading rules are a category to avoid**: when a rule must inspect content, specify it as "regenerate the canonical and compare bytes", never as line/regex conditions.
- **Shared worktree cost**: three reviewers found the tree moving under them and re-ran on `git archive` snapshots; the verdict-sha tie also forces adversary/blind-run commits BEFORE the readers are dispatched (two-phase checkpoints). One worktree per implementer, and the two-phase order written into the review station, would remove both.
- **Harness trap**: three subagent stalls came from the Bash tool's 120 s default timeout on a 150 s suite; dispatch packets now state `timeout 300000`.

## Addendum at HEAD c87488c3 (W0 closed)

| checkpoint | rounds | fix dispatches | designs | outcome |
|---|---|---|---|---|
| after-task W0-04 (content-reading rule, probes after implementation) | 5 | 6 | 3 | PASS_WITH_NOTES |
| after-task W0-05 (probes BEFORE implementation, 11 probes, 1 xfail as RED) | 3 | 2 | 1 | PASS_WITH_NOTES |

W0-05's two fixes were both omissions in one gate (stamp check not applied to every path; copy mode ignored) found by Codex, not design changes. W0 wave-end skipped as a separate round: the after-task W0-05 review-only commit left an empty unreviewed delta; branch-end re-reads 160658c2..HEAD in full.
Subagent stalls on the 120 s Bash timeout: 5 so far (packets stating the parameter did not prevent the last two — the fix belongs in the implementer contract or a harness default, not in packet prose).

## Addendum at HEAD dcbb66eb (branch-end PASS_WITH_NOTES, ship blocked at the dry run)

The two push-gate dry runs at the review-only HEAD (branch checker and the installed 1.0.0 plugin) both returned exit 1 on `push.probes-adversarial`: the change touches code, skill and spec, which needs three usable adversarial probes, and two were usable. The 21 per-case probes (`-k <test>`) stayed pinned to the after-task shas (7d055bb8, b7a9136c); only the two whole-file probes were re-pinned to 771a7e65 at the branch-end round. The prose probes (spec red-team rounds, the attack-catalogue pass over two `SKILL.md`) are records of what an agent did, not files the checker can run, so they never count towards the floor.

What this costs: one more narrow branch-end round (two fresh readers on this addendum plus the dispatch record, one adversary re-running the 23 probe commands and the package suite at the new commit), one review-only commit, and one more pair of dry runs — the same shape as the close-commit round that follows the PR. The orchestrator error is the same one the previous change recorded: the push gate was not run before the review-only commit was made. Written into the ship station as a candidate: run `push` at the checkpoint's reviewed commit BEFORE the review-only commit, with the probe records staged, so a short floor is caught while the round is still open.


## Addendum at HEAD 1e8b5bd2 → round 4/5 (two open intents committed after the checkpoint)

kouko asked for two more open intents (package tests in parallel; push-gate probe re-run dedup) while the round-3 dry runs were still going. Committing them after the review-only commit voids the branch-end exemption, so each late commit costs one narrow round: round 4 (two readers, intent lens) returned NEEDS_REVISION from Codex — two open questions read as technical questions put to the user, and two probe counts were wrong (22/24 for 21 per-case + 2 whole-file = 23) — and round 5 re-reads the fix. Cost of recording an idea late: two rounds, ~20 minutes, against zero if the intent had been written before the branch-end checkpoint. Candidate for the ship station: collect open intents BEFORE the branch-end round, and after it treat a new intent as belonging to the next change (write it on the trunk after the merge).
Round 5 (the fix): Codex PASS_WITH_NOTES (one contradiction my fix introduced: `-n auto` pinned in one section, left open in another), sonnet NEEDS_REVISION (my round-4 resolution note overstated "not wired": the stale script is listed in AGENTS.md as a self-check). Round 6 reads the corrections and one more open intent for that script/template drift. Three late-intent rounds so far; the lesson stands.
