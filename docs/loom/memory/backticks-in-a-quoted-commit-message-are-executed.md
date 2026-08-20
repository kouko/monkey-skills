---
name: backticks-in-a-quoted-commit-message-are-executed
description: Backticks inside a double-quoted `git commit -m` argument are command-substituted by the shell before git ever sees them, so a message quoting an identifier in backticks silently loses that word — and the loss is invisible in the command you typed; compose commit bodies in a file and pass -F
type: gotcha
origin: branch direction-queue-gate (2026-08-20) — a commit message explaining a substring collision had the substring in backticks; the shell ate it and the sentence lost its subject
---

The commit body said: *the substring `resolv` matches inside both*. The shell
saw a command substitution, tried to run `resolv`, printed
`command not found: resolv`, substituted the empty result, and git recorded:

> the substring  matches inside both

The sentence that survived is grammatical and meaningless, and the whole point
of the message was that word. The `command not found` line scrolled past inside
the commit's own output, where it reads like noise from an unrelated tool.

**Why:** double quotes do not protect backticks — that is what single quotes are
for — and a commit message is exactly the place where technical prose is full of
identifiers a writer wants to set in backticks. The failure is silent in the
only place anyone looks: the command you typed still contains the word, so
re-reading your own invocation confirms nothing. Only `git log` after the fact
shows the hole, and by then the commit exists.

**How to apply:** write commit bodies to a file and pass `git commit -F <file>`,
with the file written by a quoted heredoc (`<<'EOF'`, quoted so the heredoc
itself does not expand). This is the same discipline the repo already uses for
PR bodies via `--body-file`. If a `-m` string is unavoidable, single-quote it,
and read `git log -1 --format=%B` afterwards rather than trusting the invocation.
Amending is available while the commit is unpushed — the fix is cheap, the
detection is what costs.
