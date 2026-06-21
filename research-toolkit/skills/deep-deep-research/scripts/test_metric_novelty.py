"""Tests for metric_novelty.py — per-question novelty/contribution/direction and the CLI.

Synthetic data deliberately includes www. and trailing-slash variants to prove
norm_url() is applied when matching VS finding sources against baseline.fetched.
"""

import json
import subprocess
import sys
from pathlib import Path

from metric_novelty import (
    aggregate,
    exact_paired_permutation_p,
    per_question_metrics,
)

_MODULE = str(Path(__file__).parent / "metric_novelty.py")


def _sample() -> list[dict]:
    """Three questions with hand-controlled novelty.

    Q1 — VS wins: 3 VS confirmed, 2 of them novel; vs.confirmed (3) >= baseline.confirmed (1).
         norm_url must collapse www./trailing-slash so F1's source counts as seen.
    Q2 — direction loss: the single VS confirmed finding IS novel, but baseline has
         MORE confirmed findings (2 > 1), so VS does not win the question.
    Q3 — empty VS confirmed: contribution_rate is the defined 0/0 == 0.0 case.
    """
    return [
        {
            "question": "Q1",
            "vs": {
                "fetched": ["https://b.com/x", "https://new.com/a", "https://fresh.com/p"],
                "confirmed": [
                    # source normalizes to b.com/x -> present in baseline.fetched -> NOT novel
                    {"claim": "F1", "sources": ["https://b.com/x"]},
                    # new.com/a absent from baseline -> novel
                    {"claim": "F2", "sources": ["https://new.com/a"]},
                    # b.com/x seen, but fresh.com/p absent -> at-least-one-absent -> novel
                    {"claim": "F3", "sources": ["https://b.com/x", "https://www.fresh.com/p/"]},
                ],
            },
            "baseline": {
                # www. + trailing slash: norm_url -> b.com/x
                "fetched": ["https://www.b.com/x/"],
                "confirmed": [{"claim": "B1", "sources": ["https://www.b.com/x/"]}],
            },
        },
        {
            "question": "Q2",
            "vs": {
                "fetched": ["https://other.com/z"],
                "confirmed": [
                    {"claim": "F1", "sources": ["https://other.com/z"]},  # novel
                ],
            },
            "baseline": {
                "fetched": ["https://site.com/1"],
                "confirmed": [
                    {"claim": "B1", "sources": ["https://site.com/1"]},
                    {"claim": "B2", "sources": ["https://site.com/2"]},
                ],
            },
        },
        {
            "question": "Q3",
            "vs": {"fetched": [], "confirmed": []},  # 0/0 contribution -> 0.0
            "baseline": {"fetched": [], "confirmed": []},
        },
    ]


def test_novelty_and_direction() -> None:
    rows = per_question_metrics(_sample())
    by_q = {r["question"]: r for r in rows}

    # Q1: 2 of 3 VS confirmed are novel; direction win (3 >= 1 confirmed, >=1 novel).
    q1 = by_q["Q1"]
    assert q1["novel_confirmed"] == 2
    assert q1["total_vs_confirmed"] == 3
    assert q1["contribution_rate"] == 2 / 3
    assert q1["direction"] is True

    # Q2: the lone VS finding is novel but baseline has more confirmed -> direction loss.
    q2 = by_q["Q2"]
    assert q2["novel_confirmed"] == 1
    assert q2["total_vs_confirmed"] == 1
    assert q2["contribution_rate"] == 1.0
    assert q2["direction"] is False

    # Q3: empty VS confirmed -> defined 0/0 == 0.0, no novel, no win.
    q3 = by_q["Q3"]
    assert q3["novel_confirmed"] == 0
    assert q3["total_vs_confirmed"] == 0
    assert q3["contribution_rate"] == 0.0
    assert q3["direction"] is False

    # Aggregate: only Q1 is a VS win.
    agg = aggregate(_sample())
    assert agg["n"] == 3
    assert agg["vs_wins"] == 1
    assert len(agg["per_question"]) == 3

    # CLI: same payload over stdin produces the same aggregate.
    proc = subprocess.run(
        [sys.executable, _MODULE],
        input=json.dumps(_sample()),
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    cli = json.loads(proc.stdout)
    assert cli["n"] == 3
    assert cli["vs_wins"] == 1
    cli_by_q = {r["question"]: r for r in cli["per_question"]}
    assert cli_by_q["Q1"]["contribution_rate"] == 2 / 3
    assert cli_by_q["Q1"]["direction"] is True
    assert cli_by_q["Q2"]["direction"] is False


def test_exact_permutation_p() -> None:
    # All-positive N=3: observed sum is the unique maximum over all 2^3 sign-flips,
    # so exactly ONE arrangement (all +1) meets/exceeds it -> p == 1/8.
    res = exact_paired_permutation_p([0.2, 0.5, 0.3])
    assert res["n"] == 3
    assert res["p_one_sided"] == 1 / 8
    assert res["min_achievable_p"] == 1 / 8

    # Mixed-sign N=3 hand count: d = [0.4, -0.1, 0.2], observed sum = 0.5.
    # Two of the 8 arrangements reach >= 0.5: all-plus (0.5) and flipping the
    # lone negative to +0.1 -> [0.4, 0.1, 0.2] = 0.7. So p == 2/8 == 0.25.
    mixed = exact_paired_permutation_p([0.4, -0.1, 0.2])
    assert mixed["n"] == 3
    assert mixed["p_one_sided"] == 2 / 8
    assert mixed["min_achievable_p"] == 1 / 8

    # min-achievable floor scales as 1 / 2**N: N=4 -> 1/16.
    four = exact_paired_permutation_p([0.1, 0.2, 0.3, 0.4])
    assert four["n"] == 4
    assert four["min_achievable_p"] == 1 / 16
    assert four["p_one_sided"] == 1 / 16  # all-positive -> unique max -> 1/16

    # N=0: nothing to permute -> p and min both 1.0 (no evidence of an effect).
    empty = exact_paired_permutation_p([])
    assert empty["n"] == 0
    assert empty["p_one_sided"] == 1.0
    assert empty["min_achievable_p"] == 1.0
