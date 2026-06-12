"""Novelty metrics for the VS-vs-baseline arm comparison (eval tooling).

Compares two research arms (the deep-deep-research "VS" arm and a baseline
arm) across N research questions. For each question it measures how much of
the VS arm's confirmed evidence the baseline arm never even fetched, and
whether the VS arm "wins" the question.

Definitions (per question):
  baseline_fetched = {norm_url(u) for u in baseline.fetched}
  A VS confirmed finding is NOVEL iff at least one of its sources normalizes
    to a URL absent from baseline_fetched.
  contribution_rate = novel_confirmed / total_vs_confirmed   (0/0 := 0.0)
  direction (VS wins) = (novel_confirmed >= 1)
                        AND (len(vs.confirmed) >= len(baseline.confirmed))

Stdlib only; no network. Reuses norm_url from dedup.py (synced SSOT primitive)
so URL canonicalization matches the live pipeline exactly.

The paired permutation significance test over `direction` is a SEPARATE,
later concern — not implemented here.

CLI (__main__): reads the per-question list as JSON from stdin, writes the
aggregate object as JSON to stdout.
"""

from __future__ import annotations

import itertools
import json
import sys
from typing import Any

from dedup import norm_url


def _baseline_fetched_keys(question: dict[str, Any]) -> set[str]:
    """Normalized set of URLs the baseline arm fetched for this question."""
    baseline = question["baseline"]
    return {norm_url(u) for u in baseline["fetched"]}


def _is_novel(finding: dict[str, Any], baseline_fetched: set[str]) -> bool:
    """A finding is novel iff >=1 of its sources is absent from baseline_fetched."""
    return any(norm_url(src) not in baseline_fetched for src in finding["sources"])


def per_question_metrics(questions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compute the per-question novelty/contribution/direction breakdown.

    Returns one dict per input question with keys:
      question, contribution_rate, novel_confirmed, total_vs_confirmed, direction.
    """
    rows: list[dict[str, Any]] = []
    for q in questions:
        baseline_fetched = _baseline_fetched_keys(q)
        vs_confirmed = q["vs"]["confirmed"]
        baseline_confirmed = q["baseline"]["confirmed"]

        novel = sum(1 for f in vs_confirmed if _is_novel(f, baseline_fetched))
        total = len(vs_confirmed)
        # 0/0 is defined as 0.0 (no VS evidence -> no contribution).
        contribution_rate = (novel / total) if total else 0.0
        direction = novel >= 1 and len(vs_confirmed) >= len(baseline_confirmed)

        rows.append(
            {
                "question": q["question"],
                "contribution_rate": contribution_rate,
                "novel_confirmed": novel,
                "total_vs_confirmed": total,
                "direction": direction,
            }
        )
    return rows


def aggregate(questions: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate the per-question breakdown into {n, vs_wins, per_question}."""
    rows = per_question_metrics(questions)
    return {
        "n": len(rows),
        "vs_wins": sum(1 for r in rows if r["direction"]),
        "per_question": rows,
    }


def exact_paired_permutation_p(diffs: list[float]) -> dict[str, Any]:
    """Exact one-sided paired permutation test over per-question differences.

    Given paired differences d_i = metric_VS(q_i) - metric_baseline(q_i) over N
    questions, enumerate all 2**N independent sign-flips (itertools.product) and
    use the sum of the signed diffs as the statistic. The observed statistic is
    sum(diffs) (the all-+1 arrangement). One-sided p is the fraction of
    arrangements whose statistic is >= the observed statistic.

    Exact (not sampled): the full 2**N permutation space is enumerated, so this
    is only tractable for small N (the eval regime). The minimum achievable p at
    a given N is 1 / 2**N — the floor a paired sign-test can ever reach, useful
    for telling "no effect" apart from "underpowered to detect one".

    N == 0: nothing to permute, so p and the floor are both 1.0 (no evidence).
    """
    n = len(diffs)
    if n == 0:
        return {"p_one_sided": 1.0, "min_achievable_p": 1.0, "n": 0}

    observed = sum(diffs)
    # Tiny tolerance so float rounding never drops the observed arrangement itself.
    tol = 1e-12
    at_or_above = sum(
        1
        for signs in itertools.product((1, -1), repeat=n)
        if sum(s * d for s, d in zip(signs, diffs)) >= observed - tol
    )
    total = 2**n
    return {
        "p_one_sided": at_or_above / total,
        "min_achievable_p": 1 / total,
        "n": n,
    }


if __name__ == "__main__":
    data = json.load(sys.stdin)
    json.dump(aggregate(data), sys.stdout)
