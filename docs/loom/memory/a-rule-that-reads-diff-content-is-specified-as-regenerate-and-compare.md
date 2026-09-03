---
name: a-rule-that-reads-diff-content-is-specified-as-regenerate-and-compare
description: A checker rule that must inspect file content is specified as "regenerate the canonical text and compare blob ids", never as a set of line/regex conditions — the close-commit shape rule took six fix rounds under line-level conditions (rename, deletion, BOM, symlink typechange, body decoy, headingless last-wins, CRLF, non-UTF-8) and converged in one round once rewritten as byte equality
type: practice
origin: 2026-09-03-loom-post-merge-seams, opus design review
---

A checker rule written as a list of line-level or regex conditions over a
diff ("the line must start with X", "must not be a rename", "must not be
CRLF") grows one condition per adversarial round, because each round
finds a shape the enumerated conditions never named — a rename, a
deletion, a BOM, a symlink typechange, a decoy body, a headingless
last-wins case, CRLF line endings, non-UTF-8 bytes. The close-commit
shape rule went through six such fix rounds this way, each round adding
a condition and each round leaving another shape open.

**Why:** every line/regex condition encodes one way content can be
WRONG; it says nothing about what content must BE. A rule of that shape
can only converge by enumerating every wrong shape in advance, which is
unbounded. A rule that instead regenerates the canonical text from the
same inputs the writer used, and compares blob ids (or byte equality)
against what was actually committed, has exactly one way to pass: being
byte-identical to the canonical text. Every one of the eight adversarial
shapes above is automatically excluded by that one comparison, because
none of them can produce byte-identical output to the regenerated
canonical form.

**How to apply:** before writing a checker rule that must judge file
CONTENT (not just presence or metadata), ask whether the correct content
can be regenerated deterministically from the same inputs the author
had. If yes, specify the rule as "regenerate, then compare blob ids (or
raw bytes)" — never as a growing list of conditions. This converged the
close-commit shape rule in one round after six rounds under the
line-level approach.
