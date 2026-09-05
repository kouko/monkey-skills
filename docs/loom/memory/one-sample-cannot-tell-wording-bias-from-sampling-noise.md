---
name: one-sample-cannot-tell-wording-bias-from-sampling-noise
description: A cold-read that scores a contract on a fixed item list is a distribution, not a number; one run per revision cannot separate a wording defect from model noise, so an attribution question is answered by N runs per contract with a stated rule for "systematic" (same item wrong in at least half the scored runs, same wrong label in at least half, N at least three) and by measuring the control contract with the same fixture
type: practice
origin: 2026-09-04-adversary-three-way-attribution-measured — four N=10 baselines (2026-09-05), following the single-sample cold reads of #787 and #789
---

Three single-sample cold reads of the adversary contract scored 7/8,
7/8 and 6/8 on three-way attribution, each wrong on different items,
and the second fix round showed that "one more sentence" made the reader
more conservative, not more accurate. Measured at N=10 with the same
eight-item fixture, the adversary contract scored 80/80 before the
sentence-cap change and 79/80 after it, with no item wrong in even two
runs — the earlier misses were noise, and the sentence added on their
account was not what fixed anything. The reviewer contract, run as a
control, scored 52/80 then 66/80 with two items claimed "mine" in 6 and
8 of 10 runs — a real, systematic bias that three single samples had
reported as 8/8.

**Why:** a single sample can only confirm or deny one outcome; it cannot
say whether a different sample would agree. Rewording on a single miss
optimises the contract against noise, and the control shows that the
side nobody was watching is where the systematic error lived.

**How to apply:** before editing a contract on the strength of a cold
read, run the same fixture N times (ten is enough to separate ≥50% from
≤20%), commit the transcripts and a `summary.json` with per-item counts,
decide the arm mechanically from the `systematic` list, and always run
the sibling contract as a control with the same fixture and the same
N — the surprise tends to be there. `claude -p` exposes no seed flag, so
record N and the model and treat runs as exchangeable samples. Related:
[[a-failed-call-is-a-non-observation-not-a-wrong-answer]].
