#!/usr/bin/env python3
"""Tests for the Task-1 version stamp: a `<meta name="generator">` tag
plus a visible muted footer, both naming the version of the copy of
adjudication_render.py that produced the page, read from the
`.claude-plugin/plugin.json` shipped beside the running script (never a
hardcoded constant, never the invocation) -- so a stale copy stamps its
own older version and the page is never mistaken for a fresh one.

Per loom-code TDD iron law: written FIRST against the not-yet-existing
stamp behavior, so the first run is RED.
"""

import json
from pathlib import Path

from adjudication_render import render_doc, render_verdict_html

FIXTURE_UNITS = [
    {
        "id": "u1",
        "heading": "Task 1 — split",
        "source_text": "The splitter MUST emit one unit per section.",
        "anchors": ["MUST"],
        "rendition": "分割器必須每個章節輸出一個單元。",
    },
]


def _expected_version() -> str:
    """Read the expected version straight from the shipped manifest so
    a later version bump does not break this test."""
    plugin_json = (
        Path(__file__).resolve().parent.parent / ".claude-plugin" / "plugin.json"
    )
    return json.loads(plugin_json.read_text())["version"]


def test_doc_page_carries_generator_meta_and_visible_footer():
    version = _expected_version()
    html_out = render_doc(FIXTURE_UNITS)

    assert (
        f'<meta name="generator" content="loom-code-adjudication-render/{version}">'
        in html_out
    )
    assert '<footer class="stamp">' in html_out
    footer_body = html_out.split('<footer class="stamp">', 1)[1].split(
        "</footer>", 1
    )[0]
    assert version in footer_body


def test_verdict_html_carries_generator_meta_and_visible_footer():
    """render_verdict_html shares _render_page with render_doc
    deliberately -- the stamp must appear in both."""
    version = _expected_version()
    html_out = render_verdict_html(FIXTURE_UNITS)

    assert (
        f'<meta name="generator" content="loom-code-adjudication-render/{version}">'
        in html_out
    )
    assert '<footer class="stamp">' in html_out
    footer_body = html_out.split('<footer class="stamp">', 1)[1].split(
        "</footer>", 1
    )[0]
    assert version in footer_body
