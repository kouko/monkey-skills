# Second-vendor mode routing

A second reviewer only counts if it is a
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

When `docs/loom/KICKOFF-DEFAULTS.md` has no `second-vendor:` line, create
the file from `KICKOFF-DEFAULTS.md` in loom-code's contract templates if
needed and record `second-vendor: suggest`. `suggest` adds no question at
capture-intent. Pass the observed mode forward; write-plan owns the
post-plan availability or recommendation notice and its response timing.

This standalone plugin does not call `second_vendor_policy.py` and does not
reimplement its risk mapping. That executable belongs to loom-code.

**`ask`** puts one question into decision point ① on every full-lane change:
when
`docs/loom/KICKOFF-DEFAULTS.md` carries that value, ask one plain
sentence in this same message — 「這次要不要用 Codex 當第二位讀者？」
("Do you want to use Codex as the second reader this time?") — and the
answer governs this change only, never rewriting the KICKOFF line. Add
the question to the running list kept in SKILL.md, so it lands in the
plan's `## Questions asked`; pass the accepted CLI or the decline directly
to the closing review. In the small lane there is only one reader, so this
question is not asked.

A **fixed CLI** is the standing reviewer choice and adds no intent question.
Probe it with the same availability rule before downstream use; never replace
it silently with another vendor.
