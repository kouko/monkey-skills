#!/usr/bin/env python3
"""Tests for book-audify's cleaner and validator.

Run with pytest, or standalone: python3 tests/test_book_audify.py

The fixtures mirror the shapes pandoc actually emits from commercial EPUBs
(TOC-linked headings, italic sub-headings, tables) plus the CJK shapes the
cleaner was originally built for.
"""
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from clean_for_tts import clean_chapter, should_skip  # noqa: E402

SCRIPTS = os.path.join(os.path.dirname(__file__), '..', 'scripts')


# ---------------------------------------------------------------- cleaner

def test_heading_with_toc_link_is_cleaned():
    # pandoc gives EPUB headings a TOC link — the normal shape, not exotic
    out = clean_chapter('# [Music as Medicine](toc.xhtml#toc-chapter005)\n\nBody.', 'en')
    assert out.split('\n\n')[0] == 'Music as Medicine.'
    assert '.xhtml' not in out and '[' not in out and '#' not in out


def test_italic_subheading_is_cleaned():
    out = clean_chapter('## *The power of lyrics*\n\nBody.', 'en')
    assert out.split('\n\n')[0] == 'The power of lyrics.'
    assert '*' not in out


def test_paragraph_inline_cleaning_still_works():
    out = clean_chapter('Body [link](toc.xhtml) with **bold** and *italic*.', 'en')
    assert out == 'Body link with bold and italic.'


def test_digit_heading_spoken_form():
    assert clean_chapter('# 01　標題', 'zh').startswith('第一章,標題')
    assert clean_chapter('# 01 Title', 'en').startswith('Chapter 1. Title')


def test_toc_linked_digit_heading_gets_spoken_form():
    # link cleaning must happen BEFORE the spoken-form match
    out = clean_chapter('# [01 Title](toc.xhtml#c1)\n\nBody.', 'en')
    assert out.startswith('Chapter 1. Title')


def test_duplicated_heading_deduped():
    out = clean_chapter('# Title\n\n# Title\n\nBody.', 'en')
    assert out.count('Title.') == 1


def test_markdown_table_dropped():
    out = clean_chapter('Before.\n\n|        | tune |\n|--------|------|\n| flute  | yes  |\n\nAfter.', 'en')
    assert out == 'Before.\n\nAfter.'


def test_equals_prose_survives_cleaning():
    text = 'That is 4 x 4 x 4 x 4 x 4 x 4 x 4 x 4 x 4 = 262,144.'
    assert clean_chapter(text, 'en') == text


def test_less_than_prose_survives():
    assert clean_chapter('We know a < b here.', 'en') == 'We know a < b here.'


def test_nested_emphasis_cleaned():
    out = clean_chapter('He wrote **bold *italic* inside** the line.', 'en')
    assert out == 'He wrote bold italic inside the line.'


def test_short_setext_underline_cleaned():
    assert clean_chapter('The Title\n=\n\nBody.', 'en') == 'Body.'
    assert clean_chapter('The Title\n==\n\nBody.', 'en') == 'Body.'


def test_callout_block_dropped():
    out = clean_chapter('> [!summary]\n> annotation line\n\nReal text.', 'zh')
    assert out == 'Real text.'


def test_circled_note_paragraph_dropped():
    out = clean_chapter('本文❶接續。\n\n❶譯注:這是注釋。', 'zh')
    assert out == '本文接續。'


def test_setext_underline_and_duplicate_title_dropped():
    out = clean_chapter('標題\n===\n\n內文。', 'zh')
    assert out == '內文。'


# -------------------------------------------------------------- skip logic

def test_body_chapters_with_skiplist_substrings_are_kept():
    for stem in ('05-9.-A-Few-Notes-about-Notes', '05-The Story of Us',
                 '12-History', '03-Notes on Method', '03-index-funds'):
        assert not should_skip(stem), stem


def test_front_back_matter_is_skipped():
    for stem in ('01-Cover', '02-Title-Page', '03-Table-of-Contents',
                 '25-Newsletters', '26-About-the-Author',
                 '27-Also-by-John-Powell', '28-References-and-Further-Reading',
                 '29-Suggestions-for-Listening-and-Viewing', '30-Notes',
                 '31-Index', '14-致謝', '15-版權頁'):
        assert should_skip(stem), stem


# -------------------------------------------------------------- validator

def _validate(files):
    d = tempfile.mkdtemp()
    for name, content in files.items():
        with open(os.path.join(d, name), 'w', encoding='utf-8') as f:
            f.write(content)
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, 'validate_tts.py'), d],
                       capture_output=True, text=True)
    return r.returncode, r.stdout


LONG = 'This sentence is ordinary spoken prose and long enough to pass. ' * 5


def test_validator_passes_clean_file():
    code, _ = _validate({'01-ch.txt': LONG})
    assert code == 0


def test_validator_accepts_equals_in_prose():
    code, out = _validate({'01-ch.txt': LONG + ' And 4 x 4 = 16.'})
    assert code == 0, out


def test_validator_rejects_markup_residue():
    for bad in ('# heading', '[link](x)', 'a │frame│', 'title\n\n===',
                'a | b | c', 'tag <div> residue', 'glued x<y compare',
                '**bold *nested* left'):
        code, _ = _validate({'01-ch.txt': LONG + '\n\n' + bad})
        assert code == 1, bad


def test_validator_accepts_spaced_comparison_operators():
    code, out = _validate({'01-ch.txt': LONG + ' We know a < b and 3 > 2 and a == b.'})
    assert code == 0, out


def test_e2e_comparison_prose_passes_gate():
    # the cleaner keeps these, so the validator must accept them — the two
    # halves of the contract have to agree
    cleaned = clean_chapter(LONG + ' We know a < b, 3 > 2, and a == b.', 'en')
    code, out = _validate({'01-ch.txt': cleaned})
    assert code == 0, out


def test_validator_accepts_three_digit_chapter_numbers():
    code, out = _validate({'100-ch.txt': LONG})
    assert code == 0, out


def test_validator_rejects_short_and_misnamed_files():
    code, _ = _validate({'01-ch.txt': 'too short'})
    assert code == 1
    code, _ = _validate({'chapter-one.txt': LONG})
    assert code == 1


def test_validator_ignores_underscore_files():
    code, _ = _validate({'01-ch.txt': LONG, '_glossary.md': '# glossary'})
    assert code == 0


# --------------------------------------------------------------- e2e clean

def test_end_to_end_realistic_epub_chapter_passes_gate():
    src, dst = tempfile.mkdtemp(), tempfile.mkdtemp()
    with open(os.path.join(src, '06-5.-Music-as-Medicine.md'), 'w', encoding='utf-8') as f:
        f.write('# [CHAPTER 5](toc.xhtml#toc-chapter005)\n\n'
                '# [Music as Medicine](toc.xhtml#toc-chapter005)\n\n'
                '## *The power of lyrics*\n\n' + LONG + '\n\n'
                'That is 4 x 4 x 4 x 4 x 4 x 4 x 4 x 4 x 4 = 262,144.\n\n'
                '|        | tune |\n|--------|------|\n| flute  | yes  |\n')
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, 'clean_for_tts.py'),
                        src, dst, '--lang', 'en'], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    code, out = _validate({f: open(os.path.join(dst, f), encoding='utf-8').read()
                           for f in os.listdir(dst)})
    assert code == 0, out


if __name__ == '__main__':
    failed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith('test_') and callable(fn):
            try:
                fn()
                print(f'PASS {name}')
            except AssertionError as e:
                failed += 1
                print(f'FAIL {name}: {e}')
    sys.exit(1 if failed else 0)
