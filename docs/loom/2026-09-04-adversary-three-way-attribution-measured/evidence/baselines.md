# Baselines: four N=10 cold-read distributions, side by side

W2-01. All four batches used `--role`'s matching contract, the same
8-item fixture (`fixture-coldread-8.json`), `--model sonnet` (the
script's default), and `--runs 10`. Every batch is `complete: true`
(`attempted_runs == 10`, `failed_runs == 0`) — no retries were needed.
Numbers below are recomputed directly from each `summary.json`, never
by hand.

## Exact command lines

```
python3 loom-code/scripts/coldread_role_split.py \
  --contract docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/contract-precap-adversary.md \
  --fixture docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/fixture-coldread-8.json \
  --role adversary --runs 10 \
  --out docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/baseline-precap-adversary

python3 loom-code/scripts/coldread_role_split.py \
  --contract docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/contract-precap-reviewer.md \
  --fixture docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/fixture-coldread-8.json \
  --role reviewer --runs 10 \
  --out docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/baseline-precap-reviewer

python3 loom-code/scripts/coldread_role_split.py \
  --contract loom-code/agents/adversary.md \
  --fixture docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/fixture-coldread-8.json \
  --role adversary --runs 10 \
  --out docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/baseline-current-adversary

python3 loom-code/scripts/coldread_role_split.py \
  --contract loom-code/agents/reviewer.md \
  --fixture docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/fixture-coldread-8.json \
  --role reviewer --runs 10 \
  --out docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/baseline-current-reviewer
```

`--model` and `--timeout` were left at their defaults (`sonnet`, 180s);
no run hit the timeout.

## Per-item three-way wrong rate (wrong/10), dominant wrong label

| item | expected owner | pre-cap adversary | pre-cap reviewer | current adversary | current reviewer |
|---|---|---|---|---|---|
| 1 | reviewer | 0/10 | 0/10 | 0/10 | 0/10 |
| 2 | adversary | 0/10 | 3/10 (mine) | 0/10 | 6/10 (mine) |
| 3 | adversary | 0/10 | 10/10 (mine) | 1/10 (other) | 0/10 |
| 4 | reviewer | 0/10 | 2/10 (other) | 0/10 | 0/10 |
| 5 | reviewer | 0/10 | 0/10 | 0/10 | 0/10 |
| 6 | adversary | 0/10 | 4/10 (mine) | 0/10 | 8/10 (mine) |
| 7 | reviewer | 0/10 | 0/10 | 0/10 | 0/10 |
| 8 | implementer | 0/10 | 9/10 (mine) | 0/10 | 0/10 |

(Rows read from each reader's own contract, so "mine"/"other" already
map back to reviewer/adversary in this table — item 2's "current
reviewer 6/10 (mine)" means 6 of 10 reviewer-contract runs claimed item
2 as the reviewer's own finding, when the fixture says it belongs to
the adversary.)

## Totals and systematic lists

| contract | own/not-own correct (of 80) | three-way correct (of 80) | systematic | failed_runs |
|---|---|---|---|---|
| pre-cap adversary | 80 | 80 | [] | 0 |
| pre-cap reviewer | 52 | 52 | [3, 8] | 0 |
| current adversary | 79 | 79 | [] | 0 |
| current reviewer | 66 | 66 | [2, 6] | 0 |

(`own_not_own_correct` and `three_way_correct` are identical here
because this fixture's labels collapse to the same correctness
judgment at both granularities for every item — an item is either
`mine`/`other`/`implementer` matching exactly, or it isn't.)

## Where the errors cluster

The adversary contract reads cleanly at both time points: pre-cap is
80/80 with no systematic item, and the current (capped) contract drops
one single non-repeating miss (item 3, 1/10, not systematic) — 79/80.
The reviewer contract is where the errors concentrate, at both time
points, on the same shape of mistake: item 8 (an implementer-owned
"missing unit test" finding) was systematically claimed as the
reviewer's own pre-cap (9/10, `systematic`) and is now unanimous and
correct post-cap (0/10) — the current three-way sentence fixed that
one cleanly. Item 3 shows the same pattern (10/10 wrong pre-cap →
0/10 post-cap, no longer systematic). But two adversary-owned items,
2 and 6, went the other way: pre-cap they were only partly wrong (3/10
and 4/10, below the `systematic` threshold) and post-cap they are both
systematic (6/10 and 8/10) with the same dominant wrong label
(`mine`) — the reviewer's current contract now over-claims boundary
findings (2: "stale origin/main short-circuits the candidate loop";
6: "merge-base --is-ancestor accepts a side-branch commit") that
belong to the adversary. So the current wording measurably fixed the
implementer-boundary confusion (items 3, 8) but introduced a new,
concentrated over-claim on two adversary-boundary items — the errors
did not scatter, they moved from one cluster to another.
