"""Adversary probes for W1-02 (`loom-code/scripts/coldread_role_split.py`),
written before the module exists. Every case here is RED right now with
`ImportError`/`ModuleNotFoundError` -- that is the intended RED for the
implementer's failing-test-first task. Once the module lands, every probe
must go GREEN unmodified; a probe that needs the implementation weakened
to pass is not a probe.

Interface pinned by the dispatch packet (loom-code plan.md W1-02):

    parse_response(text: str, n_items: int) -> dict[int, str]
        keys 1..n_items always present; value in
        {"mine", "other", "implementer", "unparsed"}. A line matches when
        it starts (after optional whitespace, optional `**`/`-`/`*`
        markdown noise) with `<n>.` or `<n>)` or `<n>:` followed by the
        label token; label matching is case-insensitive and tolerates a
        trailing `'s`/`'s`, `--`/`-`/`:` separators, and markdown `**`.
        Anything else for that item -> "unparsed". A duplicate item number
        keeps the first occurrence.

    score(responses: list[str], fixture: dict, role: str) -> dict
        `role` in {"reviewer", "adversary"} else ValueError. `systematic`
        = items with wrong/n >= 0.5 AND the most frequent wrong label's
        count/n >= 0.5. `unparsed` counts as wrong and is itself eligible
        as the dominant wrong label.

Fixture used throughout: the real 8-item fixture at
`docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/
fixture-coldread-8.json`, whose expected map is
{1,4,5,7}->reviewer, {2,3,6}->adversary, {8}->implementer.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


def _find_repo_root(start: Path) -> Path:
    """Walk upward from `start` until a directory containing docs/loom is found."""
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "docs" / "loom").is_dir():
            return candidate
    raise RuntimeError(f"could not locate repo root (docs/loom) above {start}")


REPO_ROOT = _find_repo_root(Path(__file__).parent)
SCRIPTS_DIR = REPO_ROOT / "loom-code" / "scripts"
FIXTURE_PATH = (
    REPO_ROOT
    / "docs"
    / "loom"
    / "2026-09-04-adversary-three-way-attribution-measured"
    / "evidence"
    / "fixture-coldread-8.json"
)

sys.path.insert(0, str(SCRIPTS_DIR))

import coldread_role_split  # noqa: E402  (import after sys.path mutation, by design)

parse_response = coldread_role_split.parse_response
score = coldread_role_split.score


def _load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _make_response(labels_by_n: dict, n_items: int = 8) -> str:
    """Build a synthetic 8-item response string, one line per item present.

    Items absent from `labels_by_n` are simply not emitted as lines, so
    they exercise the "absent input" case in `parse_response`.
    """
    lines = []
    for n in range(1, n_items + 1):
        if n in labels_by_n:
            lines.append(f"{n}. {labels_by_n[n]} -- because reasons")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 1. Empty and absent input
# ---------------------------------------------------------------------------


def test_parse_response_empty_string_all_unparsed():
    """An empty response string must yield unparsed for every item 1..n, never a KeyError."""
    result = parse_response("", 8)
    assert result == {n: "unparsed" for n in range(1, 9)}


def test_score_empty_responses_list_yields_zero_totals():
    """score([], fixture, role) must not divide by zero; totals are 0, systematic is empty."""
    fixture = _load_fixture()
    result = score([], fixture, "reviewer")
    assert result["n"] == 0
    assert result["own_not_own_total"] == 0
    assert result["three_way_total"] == 0
    assert result["systematic"] == []


# ---------------------------------------------------------------------------
# 2. Boundary and one past it (item numbers out of range, duplicates)
# ---------------------------------------------------------------------------


def test_parse_response_item_number_past_n_items_ignored():
    """A line numbered beyond n_items (e.g. item 9 of 8) must not appear in the returned dict
    and must not crash parsing of the in-range items."""
    text = "1. mine -- ok\n9. other -- out of range, must be dropped"
    result = parse_response(text, 8)
    assert set(result.keys()) == set(range(1, 9))
    assert result[1] == "mine"


def test_parse_response_duplicate_item_number_keeps_first_occurrence():
    """When item n appears twice with different labels, the first occurrence wins."""
    text = "3. mine -- first\n3. other -- second, must be ignored"
    result = parse_response(text, 8)
    assert result[3] == "mine"


# ---------------------------------------------------------------------------
# 3. Hostile input: markdown decoration, non-ASCII/CJK noise
# ---------------------------------------------------------------------------


def test_parse_response_markdown_bolded_label_strips_asterisks():
    """`1. **Reviewer's** -- ...` must parse to the base label ("mine" under
    role reviewer's own mapping is applied by score, not parse_response;
    parse_response itself must return the raw label token "reviewer"-shaped
    text normalized to one of the four canonical tokens is NOT its job --
    parse_response only recognizes the three role-neutral tokens
    mine/other/implementer plus unparsed). This case pins that markdown
    noise around a valid token is stripped before matching."""
    text = "1. **mine** -- because it's a probe artifact question"
    result = parse_response(text, 8)
    assert result[1] == "mine"


def test_parse_response_cjk_noise_around_label_token_still_parses():
    """Non-ASCII / CJK commentary surrounding the label token must not
    prevent recognition of the leading `<n>. <label>` token."""
    text = "1. mine — 這是我認為對的答案，理由如下：測試非 ASCII 干擾"
    result = parse_response(text, 8)
    assert result[1] == "mine"


def test_parse_response_colon_and_paren_separators_after_number():
    """`<n>)` and `<n>:` must be recognized exactly like `<n>.` before the label."""
    text = "1) other: some reason\n2: implementer - another reason"
    result = parse_response(text, 8)
    assert result[1] == "other"
    assert result[2] == "implementer"


# ---------------------------------------------------------------------------
# 4. unparsed is never scored as correct, and counts toward wrong
# ---------------------------------------------------------------------------


def test_score_unparsed_line_never_counted_correct():
    """A response where every item line is garbage (no recognizable label)
    must show zero correct on both own_not_own and three_way for that run,
    and each item's `wrong` count must include this run."""
    fixture = _load_fixture()
    garbage = "\n".join(f"{n}. banana" for n in range(1, 9))
    result = score([garbage], fixture, "reviewer")
    assert result["own_not_own_correct"] == 0
    assert result["three_way_correct"] == 0
    for n in range(1, 9):
        assert result["items"][str(n)]["wrong"] == 1
        assert result["items"][str(n)]["counts"]["unparsed"] == 1


# ---------------------------------------------------------------------------
# 5. Exact threshold boundaries for `systematic`
# ---------------------------------------------------------------------------


def _item1_reviewer_response(label: str) -> str:
    """A minimal 8-item response giving item 1 the given label (item 1's
    expected owner is reviewer, i.e. correct label under role=reviewer is
    "mine"); the other 7 items are all answered correctly so only item 1
    can go systematic."""
    correct_labels = {1: "mine", 2: "other", 3: "other", 4: "mine",
                       5: "mine", 6: "other", 7: "mine", 8: "implementer"}
    overrides = dict(correct_labels)
    overrides[1] = label
    return _make_response(overrides)


def test_score_systematic_exactly_5_of_10_same_wrong_label_included():
    """5/10 wrong on item 1, all 5 wrong runs sharing the same wrong label
    ("other"), must mark item 1 as systematic (>=50% wrong AND >=50% same
    wrong label, both satisfied exactly at the boundary)."""
    fixture = _load_fixture()
    responses = (
        [_item1_reviewer_response("other")] * 5
        + [_item1_reviewer_response("mine")] * 5
    )
    result = score(responses, fixture, "reviewer")
    assert 1 in result["systematic"]


def test_score_systematic_5_of_10_wrong_split_evenly_excluded():
    """5/10 wrong on item 1 (>=50% wrong rate) but the 5 wrong runs split
    3-vs-2 across two different wrong labels ("other" and "implementer")
    must NOT mark item 1 as systematic: the dominant wrong label's own
    share is 3/10 = 30% < 50%."""
    fixture = _load_fixture()
    responses = (
        [_item1_reviewer_response("other")] * 3
        + [_item1_reviewer_response("implementer")] * 2
        + [_item1_reviewer_response("mine")] * 5
    )
    result = score(responses, fixture, "reviewer")
    assert 1 not in result["systematic"]


def test_score_systematic_4_of_10_wrong_excluded_below_wrong_threshold():
    """4/10 wrong on item 1, all sharing the same wrong label, must NOT be
    systematic: the wrong-rate itself (40%) is below the 50% floor even
    though the dominant-label share among wrong runs is 100%."""
    fixture = _load_fixture()
    responses = (
        [_item1_reviewer_response("other")] * 4
        + [_item1_reviewer_response("mine")] * 6
    )
    result = score(responses, fixture, "reviewer")
    assert 1 not in result["systematic"]


# ---------------------------------------------------------------------------
# 6. Role-mapping symmetry
# ---------------------------------------------------------------------------


def test_score_role_reviewer_maps_adversary_expected_to_other():
    """Under role=reviewer, an item whose fixture `expected` is "adversary"
    is scored correct when the response labels it "other" (not "mine",
    not "implementer")."""
    fixture = _load_fixture()
    # item 2's expected owner is "adversary" in the real fixture.
    response = _make_response({2: "other"})
    result = score([response], fixture, "reviewer")
    assert result["items"]["2"]["expected"] == "other"
    assert result["items"]["2"]["wrong"] == 0


def test_score_role_adversary_maps_adversary_expected_to_mine():
    """Under role=adversary, the same item (expected owner "adversary")
    is scored correct when the response labels it "mine" -- the symmetric
    mapping to the reviewer case above."""
    fixture = _load_fixture()
    response = _make_response({2: "mine"})
    result = score([response], fixture, "adversary")
    assert result["items"]["2"]["expected"] == "mine"
    assert result["items"]["2"]["wrong"] == 0


# ---------------------------------------------------------------------------
# 7. Invalid role -> ValueError
# ---------------------------------------------------------------------------


def test_score_invalid_role_raises_value_error():
    """An unrecognized role string (neither "reviewer" nor "adversary")
    must raise ValueError, not silently default or KeyError."""
    fixture = _load_fixture()
    response = _make_response({1: "mine"})
    with pytest.raises(ValueError):
        score([response], fixture, "implementer")


# ---------------------------------------------------------------------------
# 8. Wrong call order / malformed n_items
# ---------------------------------------------------------------------------


def test_parse_response_zero_n_items_returns_empty_dict():
    """n_items=0 must return an empty dict, not raise and not fabricate
    item 0 or item 1 keys."""
    result = parse_response("1. mine -- stray line", 0)
    assert result == {}


def test_score_fixture_missing_items_key_raises_rather_than_silently_scoring():
    """A malformed fixture (no "items" key) must raise -- KeyError or
    ValueError are both acceptable failure-loud signals -- rather than
    returning a result with an empty items map as if scoring succeeded."""
    with pytest.raises((KeyError, ValueError)):
        score(["1. mine -- x"], {"source": "nope"}, "reviewer")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
