"""Task 9 acceptance test — deterministic grader.

`grade(answers, gold_questions_path)` scores a set of agent answers against
`gold-questions.yml`: each answer's numeric value is matched against the gold
`expected_answer` (Decimal equality within a documented tolerance), and each
gold `required_invariant` is mechanically checked against the answer's SQL/trace
string. This test drives one all-correct answer set (100% / all pass) and one
deliberately-wrong set (a numeric mismatch AND a naive-`AVG(` invariant
violation) and asserts the resulting per-question verdicts and overall score.
"""
from __future__ import annotations

from pathlib import Path

from grader import grade

GOLD_YAML = Path(__file__).parent / "fixtures" / "l2-harness" / "gold-questions.yml"


def test_grader_scores_correct_and_incorrect_answers():
    correct = {
        "avg_ratio": {
            "value": 0.0875,
            "trace": "SELECT SUM(numerator) / SUM(denominator) FROM seed_avg_ratio",
        },
        "fanout": {
            "value": 82.50,
            "trace": (
                "WITH li AS (SELECT order_id, SUM(quantity * unit_price) v "
                "FROM seed_fanout_line_items GROUP BY order_id) "
                "SELECT SUM(li.v + o.shipping_fee) FROM seed_fanout_orders o "
                "JOIN li USING (order_id)"
            ),
        },
        "categorical": {
            "value": 3,
            "trace": "SELECT COUNT(*) FROM seed_categorical WHERE status = 'active'",
        },
        "amortization": {
            "value": 800.00,
            "trace": (
                "SELECT book_value FROM seed_amortization "
                "WHERE as_of_date <= '2026-07-01' ORDER BY as_of_date DESC LIMIT 1"
            ),
        },
        "regional_twins": {
            "value": 160.00,
            "trace": "SELECT SUM(amount) FROM seed_regional_twins WHERE entity_id = 'widget'",
        },
    }

    report = grade(correct, GOLD_YAML)

    assert report.score == 1.0
    assert report.passed_count == 5
    assert report.total == 5
    assert all(r.passed for r in report.results)
    assert all(r.value_correct and not r.invariant_failures for r in report.results)

    wrong = dict(correct)
    # Wrong value AND a naive-AVG( invariant violation on the pre-aggregated column.
    wrong["avg_ratio"] = {
        "value": 0.10,
        "trace": "SELECT AVG(ratio) FROM seed_avg_ratio",
    }

    report2 = grade(wrong, GOLD_YAML)

    assert report2.score < 1.0
    assert report2.passed_count == 4

    avg = next(r for r in report2.results if r.trap == "avg_ratio")
    assert not avg.value_correct
    assert avg.invariant_failures  # naive AVG( detected in the trace
    assert not avg.passed

    # The untouched answers still pass.
    others = [r for r in report2.results if r.trap != "avg_ratio"]
    assert all(r.passed for r in others)


def test_grader_detects_naive_max_date_violation():
    """The MAX(-banning branch (amortization) must also fire, not just AVG(."""
    wrong = {
        "avg_ratio": {
            "value": 0.0875,
            "trace": "SELECT SUM(numerator) / SUM(denominator) FROM seed_avg_ratio",
        },
        "fanout": {
            "value": 82.50,
            "trace": (
                "WITH li AS (SELECT order_id, SUM(quantity * unit_price) v "
                "FROM seed_fanout_line_items GROUP BY order_id) "
                "SELECT SUM(li.v + o.shipping_fee) FROM seed_fanout_orders o "
                "JOIN li USING (order_id)"
            ),
        },
        "categorical": {
            "value": 3,
            "trace": "SELECT COUNT(*) FROM seed_categorical WHERE status = 'active'",
        },
        "amortization": {
            # Wrong value AND the naively-banned MAX(as_of_date) trace.
            "value": 0.00,
            "trace": "SELECT book_value FROM seed_amortization ORDER BY MAX(as_of_date) DESC LIMIT 1",
        },
        "regional_twins": {
            "value": 160.00,
            "trace": "SELECT SUM(amount) FROM seed_regional_twins WHERE entity_id = 'widget'",
        },
    }

    report = grade(wrong, GOLD_YAML)

    amortization = next(r for r in report.results if r.trap == "amortization")
    assert not amortization.value_correct
    assert amortization.invariant_failures  # naive MAX(as_of_date) detected
    assert not amortization.passed


def test_grader_passes_a_correct_scoped_max_answer():
    """A CORRECT scoped `MAX(` answer must score as passed.

    Whole-branch review: `_invariant_violated` banned the aggregate named in
    a "must not" invariant wherever it appeared in the trace, so the
    idiomatic correct form — `MAX(as_of_date)` inside an as-of filter, which
    is exactly what the fixture's own reference model
    `fct_amortization_trap.sql` does — was mechanically failed. The existing
    all-correct set sidesteps this by writing `ORDER BY … LIMIT 1` instead.
    The prohibition check is advisory (the harness's own journal says so, and
    `--output-format json` exposes no SQL transcript to check against); it
    records a flag, it does not decide `passed`.
    """
    scoped_max = {
        "avg_ratio": {
            "value": 0.0875,
            "trace": "SELECT SUM(numerator) / SUM(denominator) FROM seed_avg_ratio",
        },
        "fanout": {
            "value": 82.50,
            "trace": (
                "WITH li AS (SELECT order_id, SUM(quantity * unit_price) v "
                "FROM seed_fanout_line_items GROUP BY order_id) "
                "SELECT SUM(li.v + o.shipping_fee) FROM seed_fanout_orders o "
                "JOIN li USING (order_id)"
            ),
        },
        "categorical": {
            "value": 3,
            "trace": "SELECT COUNT(*) FROM seed_categorical WHERE status = 'active'",
        },
        "amortization": {
            # Correct value, correct as-of scoping — expressed with MAX().
            "value": 800.00,
            "trace": (
                "SELECT book_value FROM seed_amortization WHERE as_of_date = ("
                "SELECT MAX(as_of_date) FROM seed_amortization "
                "WHERE as_of_date <= '2026-07-01')"
            ),
        },
        "regional_twins": {
            "value": 160.00,
            "trace": "SELECT SUM(amount) FROM seed_regional_twins WHERE entity_id = 'widget'",
        },
    }

    report = grade(scoped_max, GOLD_YAML)

    amortization = next(r for r in report.results if r.trap == "amortization")
    assert amortization.value_correct
    assert amortization.passed, "a correct scoped MAX() answer must not be failed"
    assert report.score == 1.0

    # The advisory flag is still RECORDED — it is surfaced, just not gating.
    assert amortization.invariant_failures
    assert report.invariant_flag_count == 1


def test_grader_does_not_falsely_flag_aggregate_free_prohibitions():
    """Traps whose prohibitions name no uppercase aggregate (fanout, categorical,
    regional_twins) must still pass on a correct trace — the empty-banned-set
    no-op must not accidentally reject a clean answer."""
    correct = {
        "avg_ratio": {
            "value": 0.0875,
            "trace": "SELECT SUM(numerator) / SUM(denominator) FROM seed_avg_ratio",
        },
        "fanout": {
            "value": 82.50,
            "trace": (
                "WITH li AS (SELECT order_id, SUM(quantity * unit_price) v "
                "FROM seed_fanout_line_items GROUP BY order_id) "
                "SELECT SUM(li.v + o.shipping_fee) FROM seed_fanout_orders o "
                "JOIN li USING (order_id)"
            ),
        },
        "categorical": {
            "value": 3,
            "trace": "SELECT COUNT(*) FROM seed_categorical WHERE status = 'active'",
        },
        "amortization": {
            "value": 800.00,
            "trace": (
                "SELECT book_value FROM seed_amortization "
                "WHERE as_of_date <= '2026-07-01' ORDER BY as_of_date DESC LIMIT 1"
            ),
        },
        "regional_twins": {
            "value": 160.00,
            "trace": "SELECT SUM(amount) FROM seed_regional_twins WHERE entity_id = 'widget'",
        },
    }

    report = grade(correct, GOLD_YAML)

    for trap in ("fanout", "categorical", "regional_twins"):
        result = next(r for r in report.results if r.trap == trap)
        assert not result.invariant_failures
        assert result.passed
