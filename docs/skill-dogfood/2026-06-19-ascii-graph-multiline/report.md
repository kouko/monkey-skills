# Dogfood report — ascii-graph multi-line labels (換行), PR #420 branch

Date: 2026-06-19 · Target: `ascii-graph-toolkit/skills/ascii-graph/` on
`feat/ascii-graph-multiline-labels` (== PR #420). Method:
`dev-workflow:dogfood-skill-testing` — adversarial edge-case sweep + reject-path
verification, both dimensions.

## Verdict

Normal multi-line rendering is **solid** — empty middle line, leading/trailing
newline, many lines, arch multi-line name+component all render correctly
(rectangular where required); seq/bar reject `\n` with clear `ValueError`. **One
real Medium finding**: carriage-return / CRLF handling.

| # | Severity | Finding | Status |
|---|---|---|---|
| C1 | **Medium** | `\r` / CRLF (`\r\n`) in a label leaks a raw carriage-return into output — corrupts alignment in a real terminal, at `exit 0` (silent). Affects all 4 render generators AND bypasses seq/bar's `\n`-only reject guard. | **Confirmed → fixing on #420** |
| C2 | Low | Other embedded control chars (`\t`, `\b`, `\x00`) similarly leak (0-width but cursor-moving). Pre-existing, broader than this feature. | Noted (not fixing now) |

Happy-path confirmed OK: empty-line `"a\n\nb"`, leading/trailing `\n`, only-`\n`,
4-line tree label, arch multi-line name+cells — all render as expected.

## C1 detail (Medium) — CR / CRLF leaks past split-on-`\n`

- **Root cause:** `width.split_lines(label)` = `label.split("\n")`. A `\r\n` label
  splits to `["a\r", "b"]` — the `\r` stays embedded in the first line; `\r`-only
  (`"a\rb"`, no `\n`) isn't split at all. `wcwidth("\r") == -1 → 0`, so the line
  passes width checks, but `\r` is a cursor-moving control char: in a terminal it
  overwrites the line → the alignment corruption the skill exists to prevent.
- **Confirmed (raw bytes, bypassing Python's universal-newline translation):**
  flow/table/arch/tree all emit a raw `\r` for a CRLF label at `exit 0`; seq and
  bar do NOT reject a `\r`-only label (`exit 0`, `\r` leaks) because the guard tests
  `"\n" in label` only.
- **Fix (verified):**
  1. `split_lines(label)` → `label.splitlines() or [""]` — `str.splitlines()` splits
     on `\r`, `\n`, `\r\n` (and `\v`/`\f`), so CRLF/CR become real line breaks with
     no embedded control char. All existing T1 cases still hold
     (`"a\n\nb"`→`["a","","b"]`, `""`→`[""]` via the `or [""]`). Trailing `\n` now
     yields no blank trailing line (an improvement, and untested before).
  2. seq/bar guard → reject when `split_lines(label) != [label]` (any line break,
     not just `\n`), so CRLF/CR in a seq/bar label is also rejected loud.
- **Why static + the prior reviews missed it:** every multi-line test used `\n`
  only; no test fed `\r`/CRLF. Python's text-mode subprocess capture also translates
  `\r`→`\n`, hiding the leak unless you read raw bytes.

## C2 detail (Low) — other control chars

`\t` (tab) and other non-line-separator control chars still embed (0-width per the
width policy, but they shift the cursor). `splitlines()` does not touch them. A full
fix would reject/strip any control char; out of scope for the CRLF fix. Pre-existing
(not introduced by the multi-line feature). Noted for a future hardening.
