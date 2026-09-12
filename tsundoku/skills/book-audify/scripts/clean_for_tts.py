#!/usr/bin/env python3
"""Clean book-extract Markdown chapters into TTS-ready plain text.

Usage: clean_for_tts.py <src_dir> <dst_dir> [--lang zh|en|ja]

Reads every numbered chapter .md in <src_dir>, strips everything a TTS
engine would mispronounce (markup, footnote anchors, decorative titles,
end-of-chapter translator notes), and writes one .txt per chapter to
<dst_dir>. Front/back matter (dedication, acknowledgments, copyright,
index) is skipped entirely — the skip list is printed at the end and MUST
be reviewed against the book's chapter list: a wrongly skipped chapter is
silent data loss no downstream check can catch.

Output contract is enforced by validate_tts.py — run it before synthesis.
"""
import argparse
import os
import re
import sys

# Front/back matter is skipped by EXACT match on the normalized stem (or a
# few unambiguous prefixes), never by substring — "A Few Notes about Notes"
# is a body chapter, "Notes" is back matter.
SKIP_EXACT = {
    # front matter
    'cover', 'title page', 'half title', 'half title page', 'frontispiece',
    'copyright', 'copyright page', 'dedication', 'epigraph',
    'contents', 'table of contents', 'toc', 'newsletters',
    # back matter
    'acknowledgments', 'acknowledgements', 'notes', 'endnotes', 'footnotes',
    'index', 'bibliography', 'references', 'further reading',
    'references and further reading', 'suggestions for listening and viewing',
    'about the author', 'about the authors', 'colophon', 'credits',
    'permissions',
    # zh
    '封面', '書名頁', '版權', '版權頁', '版權聲明', '獻詞', '致謝', '目錄',
    '注釋', '註釋', '索引', '參考書目', '參考文獻', '延伸閱讀',
    '作者簡介', '關於作者',
    # ja
    '謝辞', '奥付', '献辞', '目次', '訳者あとがき', '著者について',
}
SKIP_PREFIXES = ('also by ', 'praise for ', 'other books by ')

CN_NUM = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十',
          '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十']

# ➀-➓ (U+2780–U+2793) already covers ➊-➓
CIRCLED = r'[❶-❿⓫-⓴➀-➓]'


def normalized_stem(stem: str) -> str:
    s = re.sub(r'^\d+[-._\s]*', '', stem)       # play-order prefix "05-"
    s = re.sub(r'^\d+[.、]?[-_\s]+', '', s)     # in-book number "9.-"
    s = re.sub(r'[-_\s]+', ' ', s.lower())
    return s.strip(' .,:;!?')


def should_skip(stem: str) -> bool:
    s = normalized_stem(stem)
    return s in SKIP_EXACT or any(s.startswith(p) for p in SKIP_PREFIXES)


def spoken_chapter(n: int, lang: str) -> str:
    if lang in ('zh', 'ja'):
        num = CN_NUM[n] if n < len(CN_NUM) else str(n)
        return f'第{num}章'
    return f'Chapter {n}.'


def clean_inline(line: str) -> str:
    line = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', line)
    # bold is non-greedy so nested emphasis (**bold *italic* inside**)
    # unwraps instead of leaving stray asterisks
    line = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
    line = re.sub(r'\*([^*]+)\*', r'\1', line)
    line = re.sub(r'`([^`]+)`', r'\1', line)
    return line


def clean_chapter(text: str, lang: str) -> str:
    # Obsidian-style callout blocks (> [!summary] ...) are annotations, not book text
    lines, out, i = text.splitlines(), [], 0
    while i < len(lines):
        if re.match(r'^>\s*\[!\w+\]', lines[i]):
            while i < len(lines) and (lines[i].startswith('>') or not lines[i].strip()):
                i += 1
            continue
        out.append(lines[i])
        i += 1
    text = '\n'.join(out)

    # HTML: drop footnote anchors and images entirely, unwrap everything else.
    # Tag pattern requires a tag-like start so prose "a < b" survives.
    text = re.sub(r'<a\b[^>]*>.*?</a>', '', text, flags=re.DOTALL)
    text = re.sub(r'<img\b[^>]*/?>', '', text)
    text = re.sub(r'<[A-Za-z/!][^>]*>', '', text)

    # Decorative chapter-title blocks: │第一章│ rules, setext underlines + the
    # duplicated title line above them, and --- horizontal rules
    lines, out = text.splitlines(), []
    for line in lines:
        s = line.strip().rstrip('\\').strip()
        if re.fullmatch(r'│[^│]*│', s):
            continue
        if re.fullmatch(r'=+|-{3,}', s):
            if out and out[-1].strip() and not out[-1].startswith('#'):
                out.pop()
            continue
        out.append(line)
    text = '\n'.join(out)

    result, prev_heading = [], None
    for line in text.splitlines():
        line = line.strip().rstrip('\\').strip()
        if not line:
            continue
        # Markdown tables are layout, not prose — narrated cells are noise
        if re.match(r'^\|.*\|$', line) or re.fullmatch(r'\|?[\s:|-]+\|?', line):
            continue
        m = re.match(r'^(#{1,6})\s*(.+)$', line)
        if m:
            # Headings share the inline cleaning path with body text — pandoc
            # gives EPUB headings a TOC link, italic sub-headings are common
            title = clean_inline(m.group(2).strip()).strip()
            if not title:
                continue
            # H1 like "01　Title" would be read digit-by-digit → spoken form
            m2 = re.match(r'^(\d{1,2})[\s　]+(.+)$', title)
            if m.group(1) == '#' and m2:
                sep = ',' if lang in ('zh', 'ja') else ' '
                title = f'{spoken_chapter(int(m2.group(1)), lang)}{sep}{m2.group(2)}'
            if title == prev_heading:      # chapter-page heading repeated in body
                continue
            prev_heading = title
            end = '。' if lang in ('zh', 'ja') else '.'
            result.append(title.rstrip('。.') + end)
            continue
        # Markdown-footnote noise: definition blocks at chapter end, scene
        # dividers (e.g. "\　\　\*" or "* * *"), then inline [^N] references
        if re.match(r'^\\?\[\^[^\]]+\]:', line):
            continue
        if re.fullmatch(r'[\\\s　*·]+', line) and '*' in line:
            continue
        line = re.sub(r'\[\^[^\]]+\]', '', line)
        line = clean_inline(line)
        line = re.sub(r'^>\s*', '', line)          # ordinary quotes: keep the words
        # End-of-chapter translator/footnote paragraphs (circled-number bullets)
        # are orphans once their inline anchors are gone — drop them
        if re.match(rf'^{CIRCLED}', line):
            continue
        line = re.sub(CIRCLED, '', line)
        if line.strip():
            result.append(line)
    return '\n\n'.join(result)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('src_dir')
    ap.add_argument('dst_dir')
    ap.add_argument('--lang', default='zh', choices=['zh', 'en', 'ja'])
    args = ap.parse_args()

    os.makedirs(args.dst_dir, exist_ok=True)
    total, skipped = 0, []
    for fname in sorted(os.listdir(args.src_dir)):
        if not fname.endswith('.md'):
            continue
        stem = fname[:-3]
        if should_skip(stem):
            skipped.append(fname)
            print(f'skip  {fname}')
            continue
        text = open(os.path.join(args.src_dir, fname), encoding='utf-8').read()
        cleaned = clean_chapter(text, args.lang)
        open(os.path.join(args.dst_dir, stem + '.txt'), 'w', encoding='utf-8').write(cleaned)
        total += len(cleaned)
        print(f'ok    {fname}  -> {len(cleaned)} chars')
    print(f'TOTAL {total} chars')
    if skipped:
        print(f'SKIPPED {len(skipped)} file(s) as front/back matter:')
        for f in skipped:
            print(f'  - {f}')
        print('REVIEW this list against the book\'s chapter list before synthesis —')
        print('a wrongly skipped chapter is silent data loss no gate can catch.')
    if total == 0:
        print('nothing produced — check src_dir', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
