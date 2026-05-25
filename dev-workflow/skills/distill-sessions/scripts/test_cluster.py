"""Tests for cluster.py — cluster_memory_items pure function.

RED tests written before production code per TDD Iron Law.
Beck (2002) Ch.1 — each test is the smallest failing increment of behavior.
"""

import pytest

from cluster import cluster_memory_items


def _make_item(title: str, anchor: str, session_id: str, **kwargs) -> dict:
    """Build a minimal memory item dict for test fixtures."""
    return {
        "title": title,
        "description": "A description.",
        "content": "Some content.",
        "kind": "failure",
        "section_anchor": anchor,
        "session_id": session_id,
        **kwargs,
    }


# ---------------------------------------------------------------------------
# Required tests (from task spec)
# ---------------------------------------------------------------------------


def test_cluster_promotes_items_supported_by_two_or_more_sessions():
    """Items sharing (title, anchor) across >=2 distinct sessions are promoted.

    WHY: The cluster step is the mechanism by which cross-session evidence
    elevates an observation from anecdote to pattern. Without this gate,
    every single-session item would flood the promoted output, defeating the
    dedup purpose of v0.3.
    """
    item_a = _make_item("Use Read before Edit on existing files", "Examples", "session_a")
    item_b = _make_item("Use Read before Edit on existing files", "Examples", "session_b")
    item_c = _make_item("Different title", "Examples", "session_c")

    promoted, pending = cluster_memory_items([item_a, item_b, item_c])

    assert len(promoted) == 1
    assert promoted[0]["title"] == "Use Read before Edit on existing files"
    assert promoted[0]["supporting_sessions"] == ["session_a", "session_b"]

    assert len(pending) == 1
    assert pending[0]["session_id"] == "session_c"


def test_cluster_normalizes_title_case_whitespace_punctuation():
    """Surface differences in title case, whitespace, trailing punctuation are ignored.

    WHY: LLM-generated titles for the same underlying pattern may vary in
    capitalisation and trailing punctuation. Without normalization, "Use Read"
    and "use read." would form two groups, defeating the clustering goal.
    """
    item_a = _make_item("Use Read before Edit", "Examples", "session_a")
    item_b = _make_item("  use read before edit. ", "Examples", "session_b")

    promoted, pending = cluster_memory_items([item_a, item_b])

    assert len(promoted) == 1
    assert len(pending) == 0


# ---------------------------------------------------------------------------
# Recommended additional tests
# ---------------------------------------------------------------------------


def test_cluster_zero_items_returns_empty_tuples():
    """Empty input produces empty outputs without error.

    WHY: Pure functions must handle the degenerate case; callers should not
    need to guard against calling with [].
    """
    promoted, pending = cluster_memory_items([])
    assert promoted == []
    assert pending == []


def test_cluster_min_n_threshold_is_configurable():
    """min_n=3 requires 3+ distinct sessions before promotion.

    WHY: The threshold is a named parameter so callers can tighten the
    evidence bar. Testing that it is honoured prevents it silently becoming
    dead code after refactoring.
    """
    item_a = _make_item("Some observation", "Examples", "session_a")
    item_b = _make_item("Some observation", "Examples", "session_b")
    item_c = _make_item("Some observation", "Examples", "session_c")
    # 2 distinct sessions with same title/anchor
    promoted_2, pending_2 = cluster_memory_items([item_a, item_b], min_n=3)
    assert len(promoted_2) == 0
    assert len(pending_2) == 2

    # 3 distinct sessions → promoted
    promoted_3, pending_3 = cluster_memory_items([item_a, item_b, item_c], min_n=3)
    assert len(promoted_3) == 1
    assert len(pending_3) == 0


def test_cluster_supporting_sessions_alphabetically_sorted():
    """supporting_sessions on the representative is sorted alphabetically.

    WHY: Deterministic output order enables stable snapshot tests downstream
    and makes the rendered output predictable regardless of input order.
    """
    item_z = _make_item("Title X", "Examples", "session_z")
    item_a = _make_item("Title X", "Examples", "session_a")
    item_m = _make_item("Title X", "Examples", "session_m")

    promoted, _ = cluster_memory_items([item_z, item_a, item_m])

    assert len(promoted) == 1
    assert promoted[0]["supporting_sessions"] == ["session_a", "session_m", "session_z"]


def test_cluster_pending_items_have_no_supporting_sessions_field():
    """Items in pending preserve original shape — no supporting_sessions added.

    WHY: The §Cross-session evidence pending bucket renderer (Task 2) expects
    items in the original shape. Adding supporting_sessions to pending items
    would break the renderer's contract.
    """
    item_a = _make_item("Unique observation", "Examples", "session_a")

    _, pending = cluster_memory_items([item_a])

    assert len(pending) == 1
    assert "supporting_sessions" not in pending[0]


def test_cluster_does_not_mutate_input():
    """cluster_memory_items does not modify the caller's list or dicts.

    WHY: Pure-function contract — callers may reuse input items after calling;
    silent mutation would produce hard-to-diagnose bugs.
    """
    item_a = _make_item("Repeated title", "Examples", "session_a")
    item_b = _make_item("Repeated title", "Examples", "session_b")
    original_keys_a = set(item_a.keys())
    original_keys_b = set(item_b.keys())

    cluster_memory_items([item_a, item_b])

    assert set(item_a.keys()) == original_keys_a
    assert set(item_b.keys()) == original_keys_b
    assert "supporting_sessions" not in item_a
    assert "supporting_sessions" not in item_b


def test_cluster_representative_preserves_extra_fields():
    """All fields from the first item in a group are kept on the representative.

    WHY: callers (propose.py renderer) may use extra fields (e.g. kind,
    description) from the representative. Silent field dropping would break
    downstream rendering.
    """
    item_a = _make_item(
        "Shared title", "Examples", "session_a", extra_field="important_value"
    )
    item_b = _make_item("Shared title", "Examples", "session_b")

    promoted, _ = cluster_memory_items([item_a, item_b])

    assert len(promoted) == 1
    assert promoted[0].get("extra_field") == "important_value"


def test_cluster_promoted_ordered_by_group_size_descending():
    """promoted list is sorted by group size descending, then alphabetic title.

    WHY: The renderer surfaces highest-evidence patterns first. Deterministic
    tie-breaking by title makes output stable across equivalent inputs.
    """
    # Group A: 3 sessions — "Bravo" (alphabetically second, but bigger group)
    bravo_items = [_make_item("Bravo title", "Examples", f"session_{i}") for i in range(3)]
    # Group B: 2 sessions — "Alpha" (alphabetically first, smaller group)
    alpha_items = [_make_item("Alpha title", "Examples", f"sess_{i}") for i in range(2)]

    promoted, _ = cluster_memory_items(bravo_items + alpha_items)

    assert len(promoted) == 2
    # Bravo (size 3) comes before Alpha (size 2)
    assert promoted[0]["title"] == "Bravo title"
    assert promoted[1]["title"] == "Alpha title"


def test_cluster_pending_ordered_by_session_id_then_normalized_title():
    """pending list is ordered by session_id then normalized title.

    WHY: Deterministic ordering in pending enables stable downstream rendering
    and reproducible snapshot tests.
    """
    item_b = _make_item("Zebra", "Examples", "session_b")
    item_a2 = _make_item("Mango", "Examples", "session_a")
    item_a1 = _make_item("Apple", "Examples", "session_a")

    _, pending = cluster_memory_items([item_b, item_a2, item_a1])

    # session_a items come first (sorted by session_id), then within session_a by title
    assert pending[0]["session_id"] == "session_a"
    assert pending[0]["title"] == "Apple"
    assert pending[1]["session_id"] == "session_a"
    assert pending[1]["title"] == "Mango"
    assert pending[2]["session_id"] == "session_b"


def test_cluster_same_session_does_not_promote():
    """Two items from the same session with the same title/anchor stay in pending.

    WHY: The promotion criterion is *distinct* session_ids >= min_n.
    Intra-session duplicates must not artificially inflate the count.
    """
    item_1 = _make_item("Repeated within session", "Examples", "session_a")
    item_2 = _make_item("Repeated within session", "Examples", "session_a")

    promoted, pending = cluster_memory_items([item_1, item_2])

    assert len(promoted) == 0
    # Both items go to pending (each preserved individually)
    assert len(pending) == 2


# ---------------------------------------------------------------------------
# min_n validation tests (RED — should fail before validation is added)
# ---------------------------------------------------------------------------


def test_cluster_min_n_zero_raises_value_error():
    """min_n=0 is invalid and raises ValueError.

    WHY: min_n=0 would silence-promote single-session items (because
    len(seen) >= 0 evaluates true), violating the docstring's stated
    semantics of requiring "distinct session_ids required for promotion."
    Per baseline Rule 12 "Fail loud" — invalid input must raise, not
    silently corrupt.
    """
    item_a = _make_item("Some title", "Examples", "session_a")
    with pytest.raises(ValueError, match="min_n must be >= 1"):
        cluster_memory_items([item_a], min_n=0)


def test_cluster_min_n_negative_raises_value_error():
    """min_n < 0 is invalid and raises ValueError.

    WHY: Negative thresholds are semantically nonsensical and would
    silently pass the comparison check. Fail early with clear error.
    """
    item_a = _make_item("Some title", "Examples", "session_a")
    with pytest.raises(ValueError, match="min_n must be >= 1"):
        cluster_memory_items([item_a], min_n=-1)
