---
name: re-multiline-whitespace-captures-across-lines
description: Python re — \s* matches newlines even under re.M, so an empty-valued key swallows the next line and chains wrong-field parses; use [ \t]* or anchor the value
type: gotcha
origin: PR #492 (loom-code 0.23.0 mechanical gates, 2026-07-04)
---

In Python regular expressions, `\s` includes `\n` regardless of
flags — `re.M` (multiline) only changes what `^`/`$` anchor to, not
what `\s` matches. So a field pattern like `key:\s*(...)` applied to
a key with an EMPTY value swallows the newline and captures the NEXT
line as this key's value, which then chains: subsequent fields parse
against the wrong lines. Real case: parsing `verdict:` / `where:`
fields of review output — one empty value shifted every following
field.

**Why:** the pattern looks correct and passes on well-formed input;
it only corrupts parses on the empty-value edge case, and the
corruption is offset-by-one confusion rather than a loud failure.

**How to apply:** for same-line whitespace use `[ \t]*` instead of
`\s*`, and/or anchor the value to the line (e.g. end with `$` under
`re.M`). Add an empty-valued-key case to the parser's tests.
