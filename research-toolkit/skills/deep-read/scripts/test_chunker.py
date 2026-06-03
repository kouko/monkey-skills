"""Tests for chunker.py — stdlib markdown heading/chapter chunker.

Flat import (pytest.ini sets pythonpath = .).

Chunk contract: split markdown into ordered {heading, text, ordinal} chunks
on headings. A chunk runs from its heading to the next heading of the SAME
OR HIGHER level (a ## chunk swallows nested ###; a new ## or # ends it).
The heading line IS included in the chunk's text.
"""
import json
import subprocess
import sys

from chunker import chunk_markdown


# --- 3-heading flat doc: 3 chunks, correct headings + ordinals -------------

def test_three_headings_yield_three_ordered_chunks():
    md = "# A\nalpha\n# B\nbeta\n# C\ngamma\n"
    chunks = chunk_markdown(md)
    assert len(chunks) == 3
    assert [c["heading"] for c in chunks] == ["# A", "# B", "# C"]
    assert [c["ordinal"] for c in chunks] == [0, 1, 2]
    # heading line is part of the chunk text; body follows
    assert chunks[0]["text"].startswith("# A")
    assert "alpha" in chunks[0]["text"]
    assert "beta" not in chunks[0]["text"]
    assert "gamma" in chunks[2]["text"]


# --- preamble before the first heading gets its own heading-"" chunk -------

def test_preamble_before_first_heading_is_its_own_chunk():
    md = "intro line one\nintro line two\n# A\nbody\n"
    chunks = chunk_markdown(md)
    assert len(chunks) == 2
    assert chunks[0]["heading"] == ""
    assert chunks[0]["ordinal"] == 0
    assert "intro line one" in chunks[0]["text"]
    assert "intro line two" in chunks[0]["text"]
    # the real heading starts the second chunk
    assert chunks[1]["heading"] == "# A"
    assert "body" in chunks[1]["text"]


# --- nested ## -> ### stays inside ONE ## chunk (same-or-higher boundary) ---

def test_nested_subsection_stays_in_one_parent_chunk():
    md = "## Parent\np-body\n### Child\nc-body\n## Sibling\ns-body\n"
    chunks = chunk_markdown(md)
    assert len(chunks) == 2
    # the ### Child does NOT start a new chunk — it is swallowed by ## Parent
    assert chunks[0]["heading"] == "## Parent"
    assert "### Child" in chunks[0]["text"]
    assert "c-body" in chunks[0]["text"]
    # the next same-level ## ends the parent chunk
    assert chunks[1]["heading"] == "## Sibling"
    assert "s-body" in chunks[1]["text"]
    assert "### Child" not in chunks[1]["text"]


# --- a shallower heading after a deeper one is the section level ------------
# UPDATED for the section-level rule. Old same-or-higher rule split "## Sub"
# and "# Top" into 2 sibling chunks. Under the new rule no level repeats, so
# L = shallowest present = 1 (the # Top). Only headings of level <= 1 start a
# chunk, so the leading "## Sub" (level 2 > L) is NOT a chunk start — it
# becomes the heading-"" preamble, and "# Top" heads the section chunk. Still
# 2 chunks, but the leading deeper heading is preamble (corrected intent: the
# repeated/shallowest level is the section boundary, not every heading).

def test_deeper_heading_before_section_level_is_preamble():
    md = "## Sub\nx\n# Top\ny\n"
    chunks = chunk_markdown(md)
    assert len(chunks) == 2
    # "## Sub" precedes the section-level "# Top" -> folded into the preamble
    assert chunks[0]["heading"] == ""
    assert "## Sub" in chunks[0]["text"]
    assert "x" in chunks[0]["text"]
    assert "# Top" not in chunks[0]["text"]
    # "# Top" is the shallowest level present -> it is the section level
    assert chunks[1]["heading"] == "# Top"
    assert "y" in chunks[1]["text"]


# --- heading-less doc -> exactly ONE chunk, heading "" ---------------------

def test_heading_less_doc_is_single_chunk():
    md = "just some text\nwith two lines\n"
    chunks = chunk_markdown(md)
    assert len(chunks) == 1
    assert chunks[0]["heading"] == ""
    assert chunks[0]["ordinal"] == 0
    assert "just some text" in chunks[0]["text"]
    assert "with two lines" in chunks[0]["text"]


# --- empty input -> no chunks ----------------------------------------------

def test_empty_input_yields_no_chunks():
    assert chunk_markdown("") == []


# --- dogfood shape: one # title + intro + N ## sections (one with ###) ------
# Real-document shape that collapsed to 1 chunk under the old same-or-higher
# rule (the # title absorbed every deeper ##). Under the section-level rule,
# the repeated ## level is the chunk level: title+intro chunk + one chunk per
# ## section, with each ### swallowed by its parent ##.

def test_single_h1_title_with_h2_sections_chunks_at_section_level():
    md = (
        "# Title\n"
        "intro paragraph\n"
        "## Section One\n"
        "s1 body\n"
        "### Sub of one\n"
        "sub body\n"
        "## Section Two\n"
        "s2 body\n"
        "## Section Three\n"
        "s3 body\n"
    )
    chunks = chunk_markdown(md)
    # ## repeats (3x) -> L=2. The lone # Title is shallower than L, so it does
    # NOT split off its ## children; it heads the leading title+intro chunk.
    # Then one chunk per ## section. -> 4 chunks (NOT 1).
    assert len(chunks) == 4
    assert [c["heading"] for c in chunks] == [
        "# Title",
        "## Section One",
        "## Section Two",
        "## Section Three",
    ]
    assert [c["ordinal"] for c in chunks] == [0, 1, 2, 3]
    # the title chunk carries the intro, not the sections
    assert "intro paragraph" in chunks[0]["text"]
    assert "## Section One" not in chunks[0]["text"]
    # the ### subsection is swallowed by its parent ## (NOT its own chunk)
    assert "### Sub of one" in chunks[1]["text"]
    assert "sub body" in chunks[1]["text"]
    assert "### Sub of one" not in chunks[2]["text"]


# --- __main__ CLI: reads stdin markdown, prints ordered JSON chunk array ----

def test_cli_prints_chunks_in_order():
    proc = subprocess.run(
        [sys.executable, "chunker.py"],
        input="# A\nx\n## B\ny\n",
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    chunks = json.loads(proc.stdout)
    # "# A" swallows the nested "## B" (## is lower than #) -> ONE chunk
    assert len(chunks) == 1
    assert chunks[0]["heading"] == "# A"
    assert chunks[0]["ordinal"] == 0
    assert "## B" in chunks[0]["text"]


def test_cli_two_sibling_headings_print_two_chunks_in_order():
    proc = subprocess.run(
        [sys.executable, "chunker.py"],
        input="# A\nx\n# B\ny\n",
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    chunks = json.loads(proc.stdout)
    assert [c["heading"] for c in chunks] == ["# A", "# B"]
    assert [c["ordinal"] for c in chunks] == [0, 1]
