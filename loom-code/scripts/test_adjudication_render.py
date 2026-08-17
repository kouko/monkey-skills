#!/usr/bin/env python3
"""Tests for adjudication_render.py (doc mode).

Per loom-code TDD iron law: this file is written FIRST, against a
not-yet-existing module, so the first run is RED (ModuleNotFoundError).

Split into single-concern tests (structural / style / per-unit content
/ escaping / external-URL absence) per the sibling convention in
test_adjudication_split.py -- each test asserts one behavior so a
future template change fails exactly the test that names the broken
behavior, not one monolithic assertion block.
"""

from adjudication_render import render_doc

FIXTURE_UNITS = [
    {
        "id": "u1",
        "heading": "Task 1 — split",
        "source_text": "The splitter MUST emit one unit per section.",
        "anchors": ["MUST"],
        "rendition": "分割器必須每個章節輸出一個單元。",
    },
    {
        "id": "u2",
        "heading": "Task 2 — lint",
        "source_text": "Watch for a <script>alert(1)</script> injection attempt.",
        "anchors": [],
        "rendition": "留意注入攻擊嘗試。",
    },
    {
        "id": "u3",
        "heading": "Task 3 — render",
        "source_text": "The renderer should produce print-safe HTML.",
        "anchors": ["should"],
        "rendition": "渲染器應產出可列印安全的 HTML。",
    },
]


def test_doc_mode_details_count_matches_unit_count():
    """One <details> collapsible per unit -- the doc-mode structural
    invariant (source_text always lives in a collapsible, never
    inlined bare) -- a dropped or duplicated unit would show up here
    first."""
    html_out = render_doc(FIXTURE_UNITS)
    assert html_out.count("<details>") == len(FIXTURE_UNITS)


def test_doc_mode_style_block_present():
    """Styling must be embedded inline (a single <style> block) -- the
    protocol requires a fully self-contained document, no external
    stylesheet link."""
    html_out = render_doc(FIXTURE_UNITS)
    assert "<style>" in html_out


def test_doc_mode_carries_rendition_per_unit():
    """Every unit's ZH rendition (the primary reading text) must
    appear in the output -- a unit silently dropped during templating
    would lose translated content without any structural signal."""
    html_out = render_doc(FIXTURE_UNITS)
    for unit in FIXTURE_UNITS:
        assert unit["rendition"] in html_out


def test_doc_mode_source_text_is_html_escaped():
    """source_text is untrusted external text pulled from a brief; a
    literal <script> tag must never reach the page unescaped -- this
    is the XSS boundary for adjudication content."""
    html_out = render_doc(FIXTURE_UNITS)
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html_out
    assert "<script>alert(1)</script>" not in html_out


def test_doc_mode_has_no_external_urls():
    """Output must be fully self-contained -- no http(s) URL anywhere
    -- matching the no-external-stylesheet / no-CDN requirement."""
    html_out = render_doc(FIXTURE_UNITS)
    assert "http://" not in html_out
    assert "https://" not in html_out


def test_doc_mode_heading_interpolation_is_escaped():
    """PIN: `heading` is attacker-reachable (briefs are external
    input) -- a heading carrying an <img onerror> payload must render
    escaped, never as live markup, even if a future template edit
    reorders interpolation. Non-vacuous: with html.escape() removed
    from the heading path, the second assertion below fails (the raw
    payload would be present verbatim)."""
    evil_unit = {
        "id": "u-evil-heading",
        "heading": "<img src=x onerror=alert(1)>",
        "source_text": "n/a",
        "anchors": [],
        "rendition": "n/a",
    }
    html_out = render_doc([evil_unit])
    assert "&lt;img src=x onerror=alert(1)&gt;" in html_out
    assert "<img src=x onerror=alert(1)>" not in html_out


def test_doc_mode_id_interpolation_is_escaped():
    """PIN: `id` feeds an HTML attribute (id="{unit_id}") -- a crafted
    id containing a quote-breakout payload must render escaped, never
    break out of the attribute into live markup, even if a future
    template edit changes how the attribute is built."""
    evil_unit = {
        "id": '"><script>alert(1)</script>',
        "heading": "n/a",
        "source_text": "n/a",
        "anchors": [],
        "rendition": "n/a",
    }
    html_out = render_doc([evil_unit])
    assert "&quot;&gt;&lt;script&gt;alert(1)&lt;/script&gt;" in html_out
    assert '"><script>alert(1)</script>' not in html_out


def _unit(rendition, uid="u1"):
    return {
        "id": uid,
        "heading": "n/a",
        "source_text": "n/a",
        "anchors": [],
        "rendition": rendition,
    }


def test_rendition_raw_html_is_escaped_not_passed_through():
    """PIN: `rendition` is the ONE field interpolated unescaped -- that is
    what makes its markdown render. What keeps that safe is the parser's
    `html: False`, and a rendition is agent-written model output, not
    developer text. Deleting that setting reverts silently: before this
    test, `MarkdownIt("commonmark", {"html": False})` -> `MarkdownIt()`
    left all 126 adjudication tests green."""
    html_out = render_doc([_unit("<script>alert(1)</script>")])
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html_out
    assert "<script>alert(1)</script>" not in html_out

    html_out = render_doc([_unit('<img src=x onerror="alert(2)">')])
    assert "<img src=x onerror=" not in html_out


def test_rendition_markdown_still_renders():
    """PIN: the escaping above must not be bought by disabling markdown --
    bold, lists, and tables are the point of parsing the rendition at all."""
    html_out = render_doc([_unit("**粗體**\n\n- 一\n- 二")])
    assert "<strong>粗體</strong>" in html_out
    assert "<li>一</li>" in html_out
    html_out = render_doc([_unit("| a | b |\n|---|---|\n| 1 | 2 |")])
    assert "<table>" in html_out and "<td>1</td>" in html_out


def test_mermaid_fence_rewrite_leaves_other_fences_intact():
    """PIN: the mermaid rewrite once ran `.replace('</code></pre>',
    '</div>')` unconditionally, so EVERY other fenced block's close tag
    became `</div>` -- a python fence rendered as
    `<pre><code class="language-python">x = 1</div>`. Only visible when one
    unit carries both a diagram and an ordinary code block."""
    md = "```python\nx = 1\n```\n\n```mermaid\nflowchart LR\n  A-->B\n```\n"
    html_out = render_doc([_unit(md)])
    assert html_out.count("<pre><code") == html_out.count("</code></pre>")
    assert '<div class="mermaid">' in html_out
    assert '<pre><code class="language-python">x = 1\n</code></pre>' in html_out


def test_consecutive_mermaid_fences_do_not_merge():
    """PIN: the rewrite regex is non-greedy so two diagrams stay two
    diagrams; a greedy match would swallow the text between them."""
    md = "```mermaid\nflowchart LR\n  A-->B\n```\n\ntext\n\n```mermaid\ngraph TD\n  C-->D\n```\n"
    html_out = render_doc([_unit(md)])
    assert html_out.count('<div class="mermaid">') == 2
    assert "text" in html_out
