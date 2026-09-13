#!/usr/bin/env python3
"""Hard gate: verify a folder of chapter .txt files is TTS-ready.

Usage: validate_tts.py <dir>

Exit 0 when every file passes; otherwise prints each violation and exits 1.
Run this BEFORE batch synthesis — an hour of TTS on a dirty file is the
failure mode this gate exists to prevent. Files starting with '_' (e.g.
_glossary.md for translated books) are ignored.
"""
import os
import re
import sys

# '=' and '<'/'>' can be legitimate prose ("4 x 4 = 16", "a < b"), so they
# are banned only in markup-shaped positions: '='-runs of 3+ (setext
# residue; the cleaner strips whole '='-underline lines, so shorter runs in
# prose are fine), and '<'/'>' not surrounded by whitespace (tag residue —
# a comparison operator sits between spaces).
BANNED_CHARS = re.compile(r'[#*`\[\]|]|[❶-❿⓫-⓴➀-➓]')
BANNED_TOKENS = re.compile(r'https?://|\.xhtml|\.jpe?g|\.png|│|={3,}'
                           r'|(?<!\s)[<>]|[<>](?!\s)')
FNAME = re.compile(r'^\d{2,}-.+\.txt$')

root = sys.argv[1]
errors = []
files = sorted(f for f in os.listdir(root) if not f.startswith(('.', '_')))
if not files:
    errors.append('folder is empty')

for f in files:
    def err(msg):
        errors.append(f'{f}: {msg}')
    if not FNAME.match(f):
        err('filename must be NN-<chapter>.txt')
        continue
    text = open(os.path.join(root, f), encoding='utf-8').read()
    if len(text) < 200:
        err(f'suspiciously short ({len(text)} chars) — front/back matter or over-cleaned?')
    for m in set(BANNED_CHARS.findall(text)) | set(BANNED_TOKENS.findall(text)):
        err(f'residual markup: {m!r}')
    for i, p in enumerate(text.split('\n\n')):
        if not p.strip():
            err(f'paragraph {i+1} is empty (consecutive blank lines)')
        elif '\n' in p:
            err(f'paragraph {i+1} contains a hard line break')

if errors:
    print(f'FAIL: {len(errors)} violation(s)')
    for e in errors:
        print(' -', e)
    sys.exit(1)
print(f'PASS: {len(files)} files are TTS-ready')
