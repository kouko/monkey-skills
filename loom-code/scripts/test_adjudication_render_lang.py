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

import json

from adjudication_render import main, render_doc, render_verdict, render_verdict_html

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


# --- Whole-branch review F3: verdict mode never joined the profile layer.
# The verdict table's column labels were hardcoded Traditional Chinese, so
# `--lang ja --html` emitted a Japanese page with Chinese headers; and the
# markdown verdict path validated `--lang` via get_profile() then never
# threaded it, so the flag was accepted and did nothing at all.


def test_verdict_markdown_honors_lang():
    """A non-default --lang must CHANGE the markdown verdict output --
    the label pair comes from the profile, not from a module constant."""
    table = render_verdict(VERDICT_UNITS, lang="ja")
    header = table.splitlines()[0]
    assert header == "| # | severity | 要約 | アンカー |"


def test_verdict_markdown_default_header_byte_identical():
    """zh-Hant (explicit and flagless) keeps today's header byte-for-byte."""
    expected = "| # | severity | 摘述 | 錨點 |"
    assert render_verdict(VERDICT_UNITS).splitlines()[0] == expected
    assert render_verdict(VERDICT_UNITS, lang="zh-Hant").splitlines()[0] == expected


def test_verdict_html_uses_japanese_column_labels():
    """The HTML verdict page already carried lang="ja" + Noto Sans JP while
    its column headers stayed Chinese -- chrome and page attributes must
    come from the same profile."""
    html_out = render_verdict_html(VERDICT_UNITS, lang="ja")
    assert "<th>要約</th>" in html_out and "<th>アンカー</th>" in html_out
    assert "摘述" not in html_out and "錨點" not in html_out


def test_verdict_html_zh_hant_headers_unchanged():
    html_out = render_verdict_html(VERDICT_UNITS)
    assert "<th>摘述</th>" in html_out and "<th>錨點</th>" in html_out


def test_cli_verdict_markdown_threads_lang(tmp_path, capsys):
    """The defect at its own layer: `verdict u.json --lang ja` (no --html)
    resolved the profile and then discarded it. Driving main() pins that
    the flag reaches the markdown renderer."""
    units_path = tmp_path / "units.json"
    units_path.write_text(json.dumps(VERDICT_UNITS, ensure_ascii=False), encoding="utf-8")
    assert main(["verdict", str(units_path), "--lang", "ja"]) == 0
    assert "| # | severity | 要約 | アンカー |" in capsys.readouterr().out


def test_both_mode_names_stay_accepted(tmp_path, capsys):
    """Characterization guard for collapsing `MODES` from a dead dispatch
    dict to a tuple of names (F4): both mode words must still be accepted
    by the parser and reach their renderer. Green before and after the
    collapse by design — it guards the refactor, it does not drive it."""
    units_path = tmp_path / "units.json"
    units_path.write_text(json.dumps(DOC_UNITS, ensure_ascii=False), encoding="utf-8")
    assert main(["doc", str(units_path)]) == 0
    assert "<html lang=" in capsys.readouterr().out
    units_path.write_text(json.dumps(VERDICT_UNITS, ensure_ascii=False), encoding="utf-8")
    assert main(["verdict", str(units_path)]) == 0
    assert capsys.readouterr().out.startswith("| # | severity |")
