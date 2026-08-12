#!/usr/bin/env python3
"""Tests for adjudication_render.py's --lang / per-profile page attributes
(Task 3): the renderer must stop hardcoding `<html lang="zh-Hant">` and the
"Noto Sans TC" font stack, instead reading both from the language profile
(adjudication_profiles.py). zh-Hant output must stay byte-identical to the
pre-Task-3 renderer (proven separately in the report via a captured-output
diff); this suite covers the `ja` behavior plus doc/verdict parity.

Per loom-code TDD iron law: written first against the not-yet-parameterized
renderer, so the first run is RED (the ja assertions fail against the
hardcoded zh-Hant literals).
"""

from adjudication_render import render_doc, render_verdict_html

DOC_UNITS = [
    {
        "id": "u1",
        "heading": "見出し",
        "source_text": "The splitter MUST emit one unit per section.",
        "anchors": ["MUST"],
        "rendition": "分割器は各セクションにつき一つの単位を出力しなければならない。",
    },
]

VERDICT_UNITS = [
    {
        "id": "u1",
        "heading": "file_a.py:12 security",
        "source_text": "severity: 🔴\ndimension: security\nwhere: file_a.py:12\n"
        "note: SQL injection risk",
        "anchors": ["🔴", "file_a.py:12"],
        "rendition": "SQL インジェクションの危険性。",
    },
]


def test_ja_lang_attribute_and_font_stack():
    """--lang ja must carry <html lang="ja"> and a Noto Sans JP-first font
    stack in doc mode -- today's renderer hardcodes zh-Hant/Noto Sans TC
    regardless of any flag, so this is the RED anchor for Task 3."""
    html_out = render_doc(DOC_UNITS, lang="ja")
    assert '<html lang="ja">' in html_out
    assert "Noto Sans JP" in html_out
    assert "Noto Sans TC" not in html_out


def test_zh_hant_lang_attribute_unchanged_by_explicit_flag():
    """Passing --lang zh-Hant explicitly must produce the same page
    attributes as the flagless default -- the profile lookup is the same
    either way."""
    html_out = render_doc(DOC_UNITS, lang="zh-Hant")
    assert '<html lang="zh-Hant">' in html_out
    assert "Noto Sans TC" in html_out


def test_verdict_html_mode_honors_lang():
    """Verdict mode's HTML rendition reuses the same page template, so it
    must honor --lang the same way doc mode does."""
    html_out = render_verdict_html(VERDICT_UNITS, lang="ja")
    assert '<html lang="ja">' in html_out
    assert "Noto Sans JP" in html_out


def test_default_lang_is_zh_hant_for_both_modes():
    """Flagless calls (no lang kwarg) must resolve to zh-Hant in both doc
    and verdict-html modes -- the default cannot silently change."""
    doc_out = render_doc(DOC_UNITS)
    verdict_out = render_verdict_html(VERDICT_UNITS)
    assert '<html lang="zh-Hant">' in doc_out
    assert '<html lang="zh-Hant">' in verdict_out
