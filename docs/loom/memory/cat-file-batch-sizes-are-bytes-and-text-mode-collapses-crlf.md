---
name: cat-file-batch-sizes-are-bytes-and-text-mode-collapses-crlf
description: A git `cat-file --batch` header declares each blob's size in bytes; slicing a `text=True` subprocess stdout by that size is wrong twice — a multi-byte character makes the str shorter than the byte count, and universal-newline translation has already turned every CRLF into one character — so a batched blob reader runs in bytes mode and decodes each blob afterwards, applying the same newline translation the text-mode reader would have
type: gotcha
origin: 2026-09-07-loom-script-performance W1-04 — two fix rounds on check_map_fog.py (CJK content caught by the orchestrator's diff read, CRLF content by a hand-built repro; the adversary had probed non-ASCII filenames only)
---

Replacing one `git show` per file with a single `git cat-file --batch`
turns a loop of subprocess spawns into one read of a concatenated
stream: `<sha> <type> <size>\n<content>\n` per object. The `<size>` is a
byte count. The first implementation called `subprocess.run(...,
text=True)` and sliced the decoded `str` by that count — every CJK
character in a ticket body shifted the next blob's boundary, and
`IndexError` or a wrong `graduated-from` followed. The second attempt
re-encoded the decoded str back to bytes to recover the sizes; that
fails too, because `text=True` applies universal-newline translation on
the way in (`\r\n` → `\n`), so a CRLF ticket has already lost one byte
per line before anything can be re-encoded. A 60-line CRLF ticket
followed by two LF tickets reproduced the crash; the old per-file
`git show` returned all three ids.

**Why:** both defects are invisible to ASCII-only, LF-only fixtures, and
this machine's global `core.autocrlf=input` normalises CRLF away unless
the fixture repo pins `core.autocrlf false` — so the ordinary test corpus
and the adversary's filename-shaped probes all stayed green while the
content-shaped boundary was wrong.

**How to apply:** read a `cat-file --batch` stream with `text=False`,
index `b"\n"` and slice by the declared byte size, then decode each blob
individually — with the same encoding the text-mode path used
(`locale.getpreferredencoding(False)`) and the same `\r\n`/`\r` → `\n`
translation — so the consumer receives byte-for-byte what `git show`
under `text=True` gave it. An adversary attacking a "one git pass instead
of N" change probes the CONTENT axis as well as the path axis: a
multi-byte body, a CRLF body (fixture pins `core.autocrlf false`), and a
body larger than a pipe buffer, each followed by at least one more object
whose result is asserted.
