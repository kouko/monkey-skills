"""Deterministic grader for the L2 e2e harness (Task 9).

`grade(answers, gold_questions_path)` scores agent answers against
`gold-questions.yml`. It is intentionally mechanical (no LLM): a wrong answer or
a violated invariant must fail the same way every run.

Answer shape
------------
`answers` maps each trap id to that trap's answer. An answer is either:
  - a dict ``{"value": <numeric>, "trace": <sql/trace str>}``, or
  - a bare numeric value (treated as ``value`` with an empty trace).
A trap missing from `answers` scores as an incorrect value with no trace.

Numeric matching
----------------
Values round-trip through YAML/Python with mixed types and lost trailing zeros
(``82.50`` loads as float ``82.5``; ``categorical``'s ``3`` stays ``int``), so
matching uses ``Decimal(str(x))`` and passes when ``abs(actual - expected) <=
TOLERANCE``. String/float ``==`` would spuriously reject correct answers.

Invariant checking
------------------
Invariants are checked mechanically against the answer's `trace` string. Only
*prohibition* invariants (those containing "must not" or "never") are checked:
any SQL aggregate function named in UPPERCASE within the invariant (AVG/SUM/
MAX/MIN/COUNT) becomes a banned call — the check flags the answer if ``FUNC(``
appears in the trace. E.g. avg_ratio's "must not compute a naive AVG ..." flags
``AVG(``. Positive ("must ...") invariants can't be soundly refuted by a
substring absence, so they are recorded but never flagged.

**Invariant flags are ADVISORY — they do not decide ``passed``.** A substring
scan cannot distinguish the banned use of an aggregate from a correct one:
amortization's "must not take MAX(as_of_date) over all rows" is tripped just as
readily by the correct as-of form (``WHERE as_of_date = (SELECT MAX(as_of_date)
… WHERE as_of_date <= '<date>')``) — which is what the fixture's own reference
model `fct_amortization_trap.sql` does — as by the naive one. Gating on it would
mechanically fail correct answers. Two further limits compound this: the real
runs feed the final assistant *summary* as the trace (``--output-format json``
exposes no SQL transcript), and only 2 of the 5 gold invariants name an
uppercase aggregate a substring scan can ban at all. So ``passed`` is decided by
value correctness; flags are recorded on the result, counted by
``GradeReport.invariant_flag_count``, and surfaced for a human to read.
Authoritative per-question invariant enforcement needs ``--output-format
stream-json`` and a semantic check — deferred, tracked in the campaign backlog.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import yaml

TOLERANCE = Decimal("1e-9")

_AGGREGATE_FUNCS = ("AVG", "SUM", "MAX", "MIN", "COUNT")
_PROHIBITION_MARKERS = ("must not", "never")


@dataclass
class QuestionResult:
    trap: str
    value_correct: bool
    expected: Any
    actual: Any
    invariant_failures: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Value correctness alone — invariant flags are advisory (see module
        docstring: a substring scan cannot tell a banned aggregate use from a
        correct one, so gating on it fails correct answers)."""
        return self.value_correct


@dataclass
class GradeReport:
    results: list[QuestionResult]

    @property
    def passed_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def score(self) -> float:
        return self.passed_count / self.total if self.results else 0.0

    @property
    def invariant_flag_count(self) -> int:
        """How many results carry at least one advisory invariant flag.

        Reported alongside `score`, never folded into it — a nonzero count is
        a prompt to read the traces, not a failure.
        """
        return sum(1 for r in self.results if r.invariant_failures)


def _to_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _values_match(actual: Any, expected: Any) -> bool:
    a, e = _to_decimal(actual), _to_decimal(expected)
    if a is None or e is None:
        return False
    return abs(a - e) <= TOLERANCE


def _invariant_violated(invariant: str, trace: str) -> bool:
    lowered = invariant.lower()
    if not any(marker in lowered for marker in _PROHIBITION_MARKERS):
        return False
    banned = {f for f in _AGGREGATE_FUNCS if re.search(rf"\b{f}\b", invariant)}
    return any(re.search(rf"\b{f}\s*\(", trace, re.IGNORECASE) for f in banned)


def _split_answer(answer: Any) -> tuple[Any, str]:
    if isinstance(answer, dict):
        return answer.get("value"), str(answer.get("trace") or "")
    return answer, ""


def grade(answers: dict[str, Any], gold_questions_path: Path) -> GradeReport:
    with Path(gold_questions_path).open() as f:
        gold = yaml.safe_load(f)

    results: list[QuestionResult] = []
    for entry in gold:
        trap = entry["trap"]
        expected = entry["expected_answer"]
        actual, trace = _split_answer(answers.get(trap))

        invariant_failures = [
            inv
            for inv in entry.get("required_invariants", [])
            if _invariant_violated(inv, trace)
        ]

        results.append(
            QuestionResult(
                trap=trap,
                value_correct=_values_match(actual, expected),
                expected=expected,
                actual=actual,
                invariant_failures=invariant_failures,
            )
        )

    return GradeReport(results=results)
