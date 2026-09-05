"""Scoring core for the cold-read role-split measurement.

Parses one cold-read answer transcript into a per-item label map and
scores N such transcripts against a fixture's expected-owner map. The
label vocabulary is exactly four tokens: "mine" (the reader's own
contract owns this finding), "other" (the counterpart role owns it),
"implementer" (a positive RED belongs to the implementer), and
"unparsed" (the line for that item did not match the pinned answer
format and is never counted as correct).
"""
from __future__ import annotations

import re
from collections import Counter

_LABEL_TOKENS = ("mine", "other", "implementer")

# Matches an optional leading markdown bullet/bold marker, an item number,
# one of `.` `)` `:` as the number/label separator, then the label token
# (tolerating a trailing possessive and markdown emphasis around it).
_LINE_RE = re.compile(
    r"""^\s*
    (?:[\*\-]\s*)*          # optional markdown bullet noise
    \**\s*
    (?P<n>\d+)
    \s*[.\):]
    \s*
    (?:[\*\-]\s*)*
    (?P<label>mine|other|implementer)
    (?:'s|’s)?
    \**
    """,
    re.IGNORECASE | re.VERBOSE,
)

_ROLE_OTHER = {"reviewer": "adversary", "adversary": "reviewer"}


def parse_response(text: str, n_items: int) -> dict[int, str]:
    """Parse one cold-read answer transcript into {1..n_items: label}.

    Every key from 1 to n_items is always present. A line is recognized
    when, after optional whitespace and markdown noise, it starts with
    `<n>.`, `<n>)`, or `<n>:` followed by one of the three label tokens
    (case-insensitive, tolerating a trailing possessive and surrounding
    `**`). Anything else for that item is "unparsed". A duplicate item
    number keeps the first occurrence. Item numbers outside 1..n_items
    are ignored.
    """
    result: dict[int, str] = {n: "unparsed" for n in range(1, n_items + 1)}
    if n_items <= 0:
        return {}

    for line in text.splitlines():
        match = _LINE_RE.match(line)
        if not match:
            continue
        n = int(match.group("n"))
        if n < 1 or n > n_items:
            continue
        if result.get(n) != "unparsed":
            continue
        result[n] = match.group("label").lower()

    return result


def _expected_label(expected_owner: str, role: str) -> str:
    if expected_owner == role:
        return "mine"
    if expected_owner == "implementer":
        return "implementer"
    return "other"


def score(responses: list[str], fixture: dict, role: str) -> dict:
    """Score N cold-read answer transcripts against `fixture` for `role`.

    `role` must be "reviewer" or "adversary" (ValueError otherwise).
    `fixture` must carry an "items" list of {n, expected} (KeyError
    otherwise). "unparsed" is never counted as correct in either tally.
    """
    if role not in _ROLE_OTHER:
        raise ValueError(f"unknown role: {role!r}")

    items = fixture["items"]
    n_items = len(items)
    expected_by_n = {item["n"]: _expected_label(item["expected"], role) for item in items}

    n = len(responses)
    parsed = [parse_response(r, n_items) for r in responses]

    items_out: dict[str, dict] = {}
    own_not_own_correct = 0
    three_way_correct = 0

    for item_n, expected in expected_by_n.items():
        counts: Counter = Counter()
        wrong = 0
        for labels in parsed:
            label = labels.get(item_n, "unparsed")
            counts[label] += 1
            if label == expected:
                three_way_correct += 1
            else:
                wrong += 1

            expected_is_mine = expected == "mine"
            label_is_mine = label == "mine"
            if label != "unparsed" and expected_is_mine == label_is_mine:
                own_not_own_correct += 1

        dominant_wrong = None
        dominant_wrong_count = 0
        for label, count in counts.items():
            if label == expected:
                continue
            if count > dominant_wrong_count:
                dominant_wrong = label
                dominant_wrong_count = count

        items_out[str(item_n)] = {
            "expected": expected,
            "counts": dict(counts),
            "wrong": wrong,
            "dominant_wrong": dominant_wrong,
        }

    systematic = []
    for item_n in sorted(expected_by_n):
        info = items_out[str(item_n)]
        if n == 0:
            continue
        wrong_rate = info["wrong"] / n
        dominant_wrong = info["dominant_wrong"]
        if dominant_wrong is None:
            continue
        dominant_count = info["counts"].get(dominant_wrong, 0)
        dominant_rate = dominant_count / n
        if wrong_rate >= 0.5 and dominant_rate >= 0.5:
            systematic.append(item_n)

    total_runs_times_items = n * n_items

    return {
        "n": n,
        "role": role,
        "items": items_out,
        "own_not_own_correct": own_not_own_correct,
        "own_not_own_total": total_runs_times_items,
        "three_way_correct": three_way_correct,
        "three_way_total": total_runs_times_items,
        "systematic": systematic,
    }
