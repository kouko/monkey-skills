# The second-reviewer suggestion

At most once per change. A second reviewer only counts if it is a
non-interactive command-line tool from a **different model vendor than
the host you are running on**: on Claude Code look for `codex` or
`gemini`, on Codex look for `claude` or `gemini`. Detect it with
`command -v <cli>` **and** a probe that it runs — `<cli> --version` must
exit 0. In zsh `command -v` may print an alias or a function body rather
than a path; do not try to parse it. **Any non-empty output plus a
`<cli> --version` that exits 0 counts as present**, and nothing else
does. Never `which`: it reports shell aliases and stale hashes, and
suggesting a tool that turns out not to run costs the user a question for
nothing. Never suggest the host itself.

Include the suggestion only when `docs/loom/KICKOFF-DEFAULTS.md` has no
`second-vendor:` line and such a tool is present. Say it in one plain
sentence with the number in it: reviewing with a second vendor costs a
few minutes and some quota, and when this system's own spec was
reviewed, five of the seven serious problems were found by only one of
the two vendors. Whatever the answer, record it in
`docs/loom/KICKOFF-DEFAULTS.md` as
`- second-vendor: <cli> | none — <reason> (<date>)` and never ask again;
if that file does not exist yet, create it first from
`KICKOFF-DEFAULTS.md` in `loom-code`'s `contract/templates/`. If the line
already exists, say nothing about it.

**`second-vendor: ask`** is a different line from the two above and is
asked every change, not suggested once: when
`docs/loom/KICKOFF-DEFAULTS.md` carries that value, ask one plain
sentence in this same message — 「這次要不要用 Codex 當第二位讀者？」
("Do you want to use Codex as the second reader this time?") — and the
answer governs this change only, never rewriting the KICKOFF line. Add
the question to the running list kept in SKILL.md, so it lands in the
plan's `## Questions asked`; the review station copies the answer
(`<cli>` or `none`) into `review.json`'s top-level `second_vendor` field
at the first checkpoint. In the small lane there is only one reader, so
this question is not asked and the field is omitted.
