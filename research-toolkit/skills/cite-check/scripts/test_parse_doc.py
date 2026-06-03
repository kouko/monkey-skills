"""RED-first tests for parse_doc.py — deterministic citation-anchor extractor.

This module is the deterministic scaffold (stdlib re/urllib only). The LLM
claim<->citation binding is NOT here (the SKILL.md owns that). We only test
that the regex/markdown structure extraction is correct.
"""

import json
import subprocess
import sys

from parse_doc import parse_doc


def _by_type(anchors, t):
    return [a for a in anchors if a["type"] == t]


# --- inline links -----------------------------------------------------------


def test_inline_link_extracted_with_url_and_anchor_text():
    """An inline [text](url) becomes an `inline` anchor carrying url + anchorText.

    WHY: the audit binds a claim to the URL the author cited; losing the anchor
    text or the URL would break that binding downstream.
    """
    anchors = parse_doc("The sky is blue [per NOAA](https://noaa.gov/sky).")
    inline = _by_type(anchors, "inline")
    assert len(inline) == 1
    assert inline[0]["citedUrl"] == "https://noaa.gov/sky"
    assert inline[0]["anchorText"] == "per NOAA"
    assert "locator" in inline[0]


def test_multiple_inline_links_each_get_their_own_anchor():
    """Two distinct inline links must yield two distinct anchors, not one."""
    anchors = parse_doc("A [one](http://a.com) then B [two](http://b.com).")
    inline = _by_type(anchors, "inline")
    assert {a["citedUrl"] for a in inline} == {"http://a.com", "http://b.com"}


# --- footnotes --------------------------------------------------------------


def test_footnote_marker_resolved_to_reference_list_url():
    """A `[^1]` marker resolves to its `[^1]: <url>` reference-list entry.

    WHY: a footnote citation is only auditable once the marker is bound to the
    URL in the reference list; an unresolved marker cannot be fetched.
    """
    doc = (
        "Growth was strong last year.[^1]\n"
        "\n"
        "[^1]: https://example.com/report\n"
    )
    anchors = parse_doc(doc)
    footnotes = _by_type(anchors, "footnote")
    assert len(footnotes) == 1
    assert footnotes[0]["citedRef"] == "1"
    assert footnotes[0]["citedUrl"] == "https://example.com/report"


def test_footnote_marker_without_reference_resolves_to_null_url():
    """A marker whose reference entry is missing keeps citedUrl == None.

    WHY: an unresolvable footnote must still be reported (it is a citation that
    cannot be fetched), distinct from silently dropping it.
    """
    doc = "An unbacked claim.[^9]\n"
    anchors = parse_doc(doc)
    footnotes = _by_type(anchors, "footnote")
    assert len(footnotes) == 1
    assert footnotes[0]["citedRef"] == "9"
    assert footnotes[0]["citedUrl"] is None


def test_bracket_number_marker_resolved_from_references_block():
    """A `[1]`-style marker resolves from a `## References` list entry URL."""
    doc = (
        "Claim with numeric cite [1].\n"
        "\n"
        "## References\n"
        "[1] Some Author. https://ref.example/1\n"
    )
    anchors = parse_doc(doc)
    footnotes = _by_type(anchors, "footnote")
    assert any(
        f["citedRef"] == "1" and f["citedUrl"] == "https://ref.example/1"
        for f in footnotes
    )


# --- unsourced --------------------------------------------------------------


def test_paragraph_with_no_link_flagged_unsourced():
    """A line that makes a claim but cites nothing is reported as `unsourced`.

    WHY: OQ5 — unsourced claims are a separate reported class (not audited, not
    silently dropped).
    """
    anchors = parse_doc("This sweeping claim has no citation at all.")
    unsourced = _by_type(anchors, "unsourced")
    assert len(unsourced) == 1
    assert "anchorText" in unsourced[0]
    assert "locator" in unsourced[0]


def test_line_with_a_citation_is_not_also_unsourced():
    """A line carrying a citation must NOT additionally be flagged unsourced."""
    anchors = parse_doc("Backed claim [src](http://s.com).")
    assert _by_type(anchors, "unsourced") == []


def test_reference_list_lines_are_not_flagged_unsourced():
    """The reference-list definition lines themselves are not claims."""
    doc = "A claim.[^1]\n\n[^1]: https://e.com/x\n"
    anchors = parse_doc(doc)
    unsourced_text = [u["anchorText"] for u in _by_type(anchors, "unsourced")]
    assert all("https://e.com/x" not in t for t in unsourced_text)


def test_wrapped_paragraph_with_citation_on_second_line_not_unsourced():
    """A claim wrapped across lines, cited on a continuation line, is sourced.

    WHY (dogfood): ~80-col wrapped prose puts the citation on a later physical
    line than the sentence start. Line-by-line scanning falsely flags the first
    line `unsourced` even though the paragraph IS cited. The paragraph is the
    unit of sourcing, not the physical line.
    """
    doc = (
        "Python 3.13 ships an experimental free-threaded build in which the GIL can be\n"
        "disabled [free-threading howto](https://docs.python.org/3.13/howto/free-threading-python.html).\n"
    )
    anchors = parse_doc(doc)
    inline = _by_type(anchors, "inline")
    assert len(inline) == 1
    assert (
        inline[0]["citedUrl"]
        == "https://docs.python.org/3.13/howto/free-threading-python.html"
    )
    # The wrapped paragraph must NOT be flagged unsourced — its citation is on
    # the second physical line but belongs to the same claim block.
    assert _by_type(anchors, "unsourced") == []


def test_blank_line_separates_paragraphs_for_unsourced_flagging():
    """Two paragraphs separated by a blank line are sourced independently.

    WHY: paragraph grouping must not over-merge — a genuinely uncited paragraph
    after a cited one must still be flagged, so the blank line is the boundary.
    """
    doc = (
        "First claim is cited [src](http://a.com).\n"
        "\n"
        "Second claim has no citation whatsoever.\n"
    )
    anchors = parse_doc(doc)
    assert len(_by_type(anchors, "inline")) == 1
    unsourced = _by_type(anchors, "unsourced")
    assert len(unsourced) == 1
    assert "Second claim" in unsourced[0]["anchorText"]


# --- CLI --------------------------------------------------------------------


def test_cli_prints_json_inline_anchor():
    """`echo '...' | python3 parse_doc.py` prints a JSON array with the anchor."""
    proc = subprocess.run(
        [sys.executable, "parse_doc.py"],
        input="[see this](http://x.com) and plain text.",
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert isinstance(data, list)
    inline = [a for a in data if a["type"] == "inline"]
    assert len(inline) == 1
    assert inline[0]["citedUrl"] == "http://x.com"
    assert inline[0]["anchorText"] == "see this"


def test_heading_citation_is_extracted_not_dropped():
    # A citation auditor must never silently drop a citation, even in a heading.
    anchors = parse_doc("# Section [src](http://h.com)\n\nplain prose.")
    inline = [a for a in anchors if a["type"] == "inline"]
    assert len(inline) == 1 and inline[0]["citedUrl"] == "http://h.com"
    # ...but the heading itself is never flagged as an unsourced prose claim.
    assert not any(
        a["type"] == "unsourced" and a["anchorText"].lstrip().startswith("#")
        for a in anchors
    )
