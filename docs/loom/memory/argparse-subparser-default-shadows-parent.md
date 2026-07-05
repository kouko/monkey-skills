---
name: argparse-subparser-default-shadows-parent
description: Python argparse — a subparser's default silently overwrites the parent parser's already-parsed option value (silent wrong-value bug class)
type: gotcha
origin: PR #492 (loom-code 0.23.0 mechanical gates, 2026-07-04)
---

In Python `argparse`, when a subparser declares a default for an
option name the parent parser also owns, the subparser's default
silently overwrites the value the parent parser already parsed
(subparser parsing runs after the parent's). The result is a silent
wrong-value bug: the user passes the option explicitly, and the
program runs with the subparser's default instead. Real case: a
gate-marker CLI minted markers against the wrong repository because
the subparser default swallowed the parent's already-parsed
`--repo`.

**Why:** nothing errors — the program just uses the wrong value, and
the bug only appears for the parent-level options a subparser
happens to redeclare.

**How to apply:** declare each option in exactly one parser. If a
subparser must redeclare a parent option, give it
`default=argparse.SUPPRESS` so it cannot clobber the parent's parsed
value; add a test that passes the option before the subcommand and
asserts it survives.
