"""Executable contract for `coldread_role_split.parse_response`/`score`.

Uses a small inline fixture (not the docs/ evidence file) so this
package test stays repo-independent, matching `test_git_exec.py`'s
bare-import convention.
"""
from __future__ import annotations

import coldread_role_split

parse_response = coldread_role_split.parse_response
score = coldread_role_split.score


def _fixture() -> dict:
    return {
        "items": [
            {"n": 1, "text": "a", "expected": "reviewer"},
            {"n": 2, "text": "b", "expected": "adversary"},
            {"n": 3, "text": "c", "expected": "adversary"},
            {"n": 4, "text": "d", "expected": "reviewer"},
            {"n": 5, "text": "e", "expected": "reviewer"},
            {"n": 6, "text": "f", "expected": "adversary"},
            {"n": 7, "text": "g", "expected": "reviewer"},
            {"n": 8, "text": "h", "expected": "implementer"},
        ],
        "source": "inline-test-fixture",
    }


def _response(labels: dict[int, str], n_items: int = 8) -> str:
    lines = []
    for n in range(1, n_items + 1):
        if n in labels:
            lines.append(f"{n}. {labels[n]} -- because reasons")
    return "\n".join(lines)


def test_score_counts_labels_per_item_and_flags_systematic():
    fixture = _fixture()
    correct = {1: "mine", 2: "other", 3: "other", 4: "mine",
               5: "mine", 6: "other", 7: "mine", 8: "implementer"}

    resp_all_correct = _response(correct)
    resp_wrong_1 = _response({**correct, 1: "other"})
    resp_wrong_1_same_label = _response({**correct, 1: "other"})

    result = score(
        [resp_all_correct, resp_wrong_1, resp_wrong_1_same_label],
        fixture,
        "reviewer",
    )

    assert result["n"] == 3
    for n in range(1, 9):
        item = result["items"][str(n)]
        assert set(item["counts"]) <= {"mine", "other", "implementer", "unparsed"}

    # item 1: 2/3 wrong, all wrong runs say "other" -> systematic (>=50% wrong,
    # >=50% dominant wrong label share)
    assert 1 in result["systematic"]
    # items 2-8 all correct in every run -> never systematic
    for n in range(2, 9):
        assert n not in result["systematic"]

    assert result["own_not_own_correct"] < result["own_not_own_total"]
    assert result["three_way_correct"] < result["three_way_total"]
    assert result["three_way_total"] == 3 * 8


def test_parse_response_unparsed_line_never_scored_correct():
    fixture = _fixture()
    garbage = "not a valid line at all"
    result = score([garbage], fixture, "reviewer")
    assert result["own_not_own_correct"] == 0
    assert result["three_way_correct"] == 0
    for n in range(1, 9):
        assert result["items"][str(n)]["counts"]["unparsed"] == 1


def test_role_reviewer_maps_expected_owners_to_labels():
    fixture = _fixture()
    resp = _response({1: "mine", 2: "other", 8: "implementer"})
    result = score([resp], fixture, "reviewer")
    assert result["items"]["1"]["expected"] == "mine"
    assert result["items"]["2"]["expected"] == "other"
    assert result["items"]["8"]["expected"] == "implementer"


def test_role_adversary_maps_expected_owners_to_labels_symmetric():
    fixture = _fixture()
    resp = _response({1: "other", 2: "mine", 8: "implementer"})
    result = score([resp], fixture, "adversary")
    assert result["items"]["1"]["expected"] == "other"
    assert result["items"]["2"]["expected"] == "mine"
    assert result["items"]["8"]["expected"] == "implementer"
