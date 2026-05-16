# Character-encoding debug — encoding-specific bisection

> Companion to [`../SKILL.md`](../SKILL.md). New file shipped per ROADMAP P2-C. Encoding bugs hide in plain sight — the text "looks right" but the bytes don't match the decoder's assumption. This protocol surfaces them.

> **Security context**: encoding bugs are also a security vector. For the security-grounded version (徳丸本 第 2 版 Ch.6 「文字コードとセキュリティ」 ISBN 978-4797393163), see [`../../subagent-driven-development/standards/character-encoding-security.md`](../../subagent-driven-development/standards/character-encoding-security.md) — the code-team functional copy. This file focuses on debugging surface; that file focuses on attack surface. The two are complementary.

## When to suspect an encoding bug

The symptom is almost always *"this string looks fine but the program disagrees."*

| Symptom | Likely encoding issue |
|---|---|
| First column header lookup fails ("id" → no match) but the CSV looks right | UTF-8 BOM (`﻿` = `EF BB BF`) prepended to the file; first column name is actually `﻿id`, not `id`. |
| Japanese / Chinese text displays as `??`, `é\x82\x91`, or mojibake | Decoder mismatch — file is UTF-8 but read as latin-1 / shift-jis, or vice versa. |
| String length doesn't match user-visible character count | NFC vs NFD normalization mismatch (`é` as one codepoint vs `e` + combining-acute = two). |
| String compare fails despite identical-looking strings | NFC / NFD mismatch; or trailing zero-width characters (ZWSP `​`, ZWJ `‍`). |
| String length differs between source and DB-stored version | Surrogate pair handling — emoji + other supplementary-plane chars are two UTF-16 code units, one codepoint, one user-visible character. |
| Substring search misses a known-present substring | NFC / NFD again; or the search uses byte-offset where it should use code-point offset. |
| File reads partially then garbles | Stream decoder split a multi-byte sequence across buffer boundaries. |

## Hex-dump bisection — the workhorse

When the text "looks the same" but behavior differs, **always hex-dump first**. The byte-level diff is the smoking gun.

```bash
# Compare two "identical" files
diff <(xxd file-that-works.csv) <(xxd file-that-fails.csv)

# Or a specific subset (first 64 bytes — catches BOM, magic bytes, header)
xxd file.csv | head -4

# For a single suspicious string, in Python:
python3 -c "print(open('file.csv', 'rb').read(8).hex())"
```

The first byte sequence tells you a lot:

| Hex prefix | Meaning |
|---|---|
| `EF BB BF` | UTF-8 BOM |
| `FE FF` | UTF-16 BE BOM |
| `FF FE` | UTF-16 LE BOM (or, occasionally, UTF-32 LE) |
| `00 00 FE FF` | UTF-32 BE BOM |
| `FF FE 00 00` | UTF-32 LE BOM |
| Anything 0x80-0xFF early | Likely UTF-8 multi-byte or a non-ASCII encoding; check decoder |
| All bytes < 0x80 | ASCII-safe; encoding mismatch unlikely (but normalization still possible) |

## Bisection by encoding axis

Apply [`root-cause-tracing.md`](root-cause-tracing.md) axis #3 (Input bisect) specialized for bytes:

1. **Locate the failing byte range**. Halve the input by byte (not by line); rerun; keep halving until the smallest failing input.
2. **Hex-dump the smallest failing input + the closest-passing version**. The byte diff is your suspect.
3. **Identify the encoding assumption**. What does the decoder think this byte sequence is? Look at the decoder config / DB column charset / HTTP `Content-Type` charset.
4. **Test the assumption**. Force the decoder to a different encoding; rerun. If the bug disappears, the assumption was wrong.

## NFC vs NFD — the silent killer

Unicode normalization forms:

| Form | Description | Example: `é` |
|---|---|---|
| **NFC** (Normalization Form Composed) | Combine codepoints where possible | `U+00E9` (1 codepoint, 2 UTF-8 bytes) |
| **NFD** (Normalization Form Decomposed) | Always decompose | `U+0065 U+0301` (2 codepoints, 3 UTF-8 bytes) |

macOS HFS+ filesystem stores filenames as NFD. Most other systems (Linux ext4, web inputs, most APIs) use NFC. **If your code compares a filename read from disk against a filename received from an API, they may be byte-different despite displaying identical.**

Fix: normalize both sides to the same form before compare. In Python: `unicodedata.normalize('NFC', s)`.

## Surrogate pairs — emoji and supplementary-plane

UTF-16 represents codepoints above U+FFFF (most emoji, lots of CJK extensions) as **surrogate pairs** — two 16-bit code units that together encode one codepoint.

| Operation | Counts what |
|---|---|
| `string.length` (JavaScript, Java) | UTF-16 code units (emoji = 2) |
| `string.codePointCount()` (Java); `[...string].length` (JS) | Codepoints (emoji = 1) |
| User-visible character | Grapheme clusters (some emoji = 1; flag emoji like 🇯🇵 = 1 user-visible but 2 codepoints + 4 UTF-16 units) |

For user-visible character count, use a grapheme-cluster library (`Intl.Segmenter` in modern JS; ICU's `BreakIterator` in Java; `unicode-segmentation` crate in Rust).

DB column lengths often allocate by bytes (`VARCHAR(255)` in MySQL legacy charset) or characters (`VARCHAR(255)` in utf8mb4) — verify which when emoji input fails to insert.

## Stream decoder buffer boundaries

When reading a UTF-8 stream in chunks, a multi-byte sequence can straddle a chunk boundary:

```
chunk 1: ...XYZ E3 81           (incomplete: E3 81 is start of a 3-byte sequence)
chunk 2: 82 ABC...              (rest: 82 + chunk-2-data)
```

If chunk 1's decoder doesn't buffer the incomplete sequence, you get an exception or replacement character. Fix: use a streaming decoder that handles partial sequences (`io.TextIOWrapper` in Python's stdlib; `TextDecoder` with `{stream: true}` in JS).

## Anti-patterns

- ❌ **Reading the file in latin-1 "to avoid encoding errors."** This silently corrupts non-ASCII text into mojibake. The encoding error was the file telling you about a mismatch — fix the mismatch, don't silence it.
- ❌ **Comparing strings without normalizing.** Especially when one side comes from filesystem (NFD-prone on macOS) and the other from API (NFC).
- ❌ **Using `string.length` for "character count."** Byte count for UTF-16 code units, not user-visible characters. Differs from grapheme clusters for emoji / CJK / accented chars.
- ❌ **Trusting the file's declared encoding.** HTTP `Content-Type` says `text/csv; charset=utf-8`; the actual bytes might be cp1252. Hex-dump before trusting metadata.
- ❌ **Stripping BOM in the parser.** Strip at the lexer / file-read level, exactly once, with a logged decision. Stripping in the parser means the BOM might survive into a database where it'll come back to haunt.

## Cross-skill contract

- Encoding bugs in **security-sensitive** contexts (input validation, SQL injection via charset attacks, mojibake auth bypass): defer to `domain-teams:code-team/standards/character-encoding-security.md` AND `subagent-driven-development/checklists/security-checklist.md`. Debugging here is necessary but not sufficient — the fix must also pass security review.
- Encoding bugs in **storage** (DB charset mismatch, file system NFC/NFD): the fix often touches schema or filesystem config — route through `brainstorming` if the change has migration implications.

## See also

- [`../SKILL.md`](../SKILL.md) — the 4-phase framework.
- [`root-cause-tracing.md`](root-cause-tracing.md) — axis #3 Input bisect specialized here.
- [`../../subagent-driven-development/standards/character-encoding-security.md`](../../subagent-driven-development/standards/character-encoding-security.md) — security-grounded version (徳丸本 第 2 版 Ch.6, ISBN 978-4797393163).
- `tests/skill-triggering/prompts/bug-fix.txt` — code-toolkit's own pressure prompt featuring exactly this bug class (UTF-8 BOM in CSV first column).
