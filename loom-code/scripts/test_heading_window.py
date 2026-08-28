"""Behavioural pins for `heading_window.line_leading`.

This helper is the single source for every heading window in THIS IMPORT
ROOT that used the hand-rolled line-leading idiom. It is not the single
source for every heading window here: other resolvers in this root scan
line by line, which is a different and equally correct mechanism, and they
do not import it. It shipped without a test of its own. A review arm mutated it
and found two survivors across the whole consumer suite: replacing
`max(0, start - 1)` with `start`, and dropping the `start == 0 and` guard.
Both are the deliberate offset choices that separate this helper from a
naive one, and both were unprotected — only one call site passes a non-zero
`start`, and it never reaches the boundary.

The consumers cannot cover this: they call with `start=0` on documents whose
headings never sit at offset 0, so the branches below are unreachable from
them by construction. Each test names the mutant it kills.
"""
from __future__ import annotations

from heading_window import line_leading


def test_heading_at_the_very_start_of_the_file_is_found():
    """Kills the mutant that drops the `start == 0 and text.startswith(...)`
    guard. Without it, a heading on line 1 has no preceding newline, the
    `find` misses, and the helper reports the heading absent — every window
    anchored on a file's first heading would raise or slice from -1."""
    assert line_leading("## Alpha\nbody\n", "## Alpha") == 0


def test_a_heading_at_offset_zero_is_not_matched_when_the_scan_starts_later():
    """The guard must be conditional on `start == 0`, not unconditional: a
    caller scanning for the NEXT occurrence past an earlier hit must not be
    handed offset 0 again. Kills a mutant that returns 0 whenever the text
    happens to start with the heading, regardless of `start`."""
    text = "## Alpha\nbody\n## Alpha\nmore\n"
    first = line_leading(text, "## Alpha")
    assert first == 0
    second = line_leading(text, "## Alpha", first + 1)
    assert second == text.index("## Alpha", 1), (
        "the scan must move past the offset-0 heading to the next one"
    )
    assert second != 0


def test_a_heading_beginning_exactly_at_start_is_found():
    """Kills the `max(0, start - 1)` → `start` mutant. When `start` lands on
    the first character of a heading line, the newline that proves it is a
    line start sits at `start - 1`; scanning from `start` steps over it and
    reports the heading absent. This is the boundary no consumer exercises,
    which is why the mutant survived the whole suite."""
    text = "intro\n## Beta\nbody\n"
    idx = text.index("## Beta")
    assert line_leading(text, "## Beta", idx) == idx


def test_the_result_never_precedes_start():
    """Kills `max(0, start - 1)` → `max(0, start - 2)` and any wider lookback.
    A result before `start` re-finds a heading the caller has already
    consumed, so a `find next` loop built on `line_leading(t, h, prev + 1)`
    never advances. The one-character lookback exists to see the newline that
    proves a heading at exactly `start` begins a line — never more than that."""
    text = "a\n## A\n"
    assert line_leading(text, "## A", 3) == -1, (
        "start=3 is past the heading; a wider lookback would re-find it"
    )
    for start in range(len(text) + 1):
        idx = line_leading(text, "## A", start)
        assert idx == -1 or idx >= start, (
            f"line_leading returned {idx} for start={start}"
        )


def test_the_first_line_leading_occurrence_wins():
    """Kills `find` → `rfind`. Every window built on this helper takes the
    FIRST matching heading; binding to the last silently stretches the
    window across everything between them while the assertions inside it
    keep passing — the branch's own target defect, reached through its own
    helper. No live call site has two line-leading matches, so no consumer
    can reach this: it has to be pinned here."""
    text = "## A\nfirst\n## A\nsecond\n## A\nthird\n"
    assert text.count("## A") == 3, "fixture must offer a later match to bind to"
    assert line_leading(text, "## A") == 0
    second = line_leading(text, "## A", 1)
    assert second == text.index("## A", 1), "must take the NEXT match, not the last"
    assert second != text.rindex("## A")


def test_start_is_clamped_at_zero():
    """`max(0, start - 1)` must not let a `start` of 0 become -1, which
    Python would read as "one character from the end" and make the scan
    miss everything before it."""
    assert line_leading("intro\n## Beta\n", "## Beta", 0) == 6


def test_a_mid_line_mention_is_not_a_heading():
    """The whole point: prose naming a heading must not bind the window.
    A bare `.find` returns the mention; this must return the real heading."""
    text = "See the ## Gamma section below.\ntext\n## Gamma\nreal\n"
    assert text.find("## Gamma") == 8, "fixture must contain the decoy first"
    assert line_leading(text, "## Gamma") == 37


def test_a_deeper_heading_does_not_satisfy_a_shallower_one():
    """`"## Foo"` is a substring of `"### Foo"`. A bare search binds to the
    `###` line; this must skip it and find the real `##` heading."""
    text = "### Delta\nsub\n## Delta\ntop\n"
    assert text.find("## Delta") == 1, "fixture must contain the ### decoy first"
    assert line_leading(text, "## Delta") == 14


def test_absent_heading_returns_minus_one_rather_than_raising():
    """Callers guard on -1; the helper must never raise, or those guards
    would be dead code and the failure would surface as a ValueError with
    no heading named."""
    assert line_leading("nothing here\n", "## Missing") == -1


def test_absent_after_start_returns_minus_one():
    assert line_leading("## Alpha\nbody\n", "## Alpha", 5) == -1


if __name__ == "__main__":
    import pytest

    raise SystemExit(pytest.main([__file__, "-q"]))
