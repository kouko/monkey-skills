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


# --- a higher-level heading also ends a lower-level chunk -------------------

def test_higher_level_heading_ends_lower_level_chunk():
    md = "## Sub\nx\n# Top\ny\n"
    chunks = chunk_markdown(md)
    assert len(chunks) == 2
    assert chunks[0]["heading"] == "## Sub"
    assert "x" in chunks[0]["text"]
    assert "# Top" not in chunks[0]["text"]
    assert chunks[1]["heading"] == "# Top"


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
