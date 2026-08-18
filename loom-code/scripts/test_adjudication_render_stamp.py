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

import adjudication_render
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


def test_unreadable_manifest_stamps_unknown(tmp_path, monkeypatch):
    """An absent, unreadable, malformed-JSON, non-dict-shaped, or
    version-less/version-null manifest must not crash the render -- it
    stamps the literal 'unknown' so a copy that cannot even name itself
    is still visibly marked, never silently unmarked. Driven through
    render_doc (the production path) rather than _deployment_version
    alone -- the non-dict-shape crash only surfaces through that path."""
    missing_path = tmp_path / "does-not-exist.json"

    bad_json_path = tmp_path / "not-json.json"
    bad_json_path.write_text("not json")

    versionless_path = tmp_path / "versionless.json"
    versionless_path.write_text("{}")

    non_dict_path = tmp_path / "non-dict.json"
    non_dict_path.write_text("[1, 2, 3]")

    null_version_path = tmp_path / "null-version.json"
    null_version_path.write_text('{"version": null}')

    for manifest_path in (
        missing_path,
        bad_json_path,
        versionless_path,
        non_dict_path,
        null_version_path,
    ):
        monkeypatch.setattr(
            adjudication_render, "_PLUGIN_MANIFEST_PATH", manifest_path
        )
        html_out = render_doc(FIXTURE_UNITS)

        assert (
            '<meta name="generator" content="loom-code-adjudication-render/unknown">'
            in html_out
        )
        footer_body = html_out.split('<footer class="stamp">', 1)[1].split(
            "</footer>", 1
        )[0]
        assert "loom-code-adjudication-render/unknown" in footer_body
