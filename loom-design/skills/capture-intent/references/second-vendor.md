# Second-vendor mode routing

An independent cross-model review only counts if it uses a non-interactive
command-line tool from a **different model family than the current host**.
Host identity comes from the environment running this skill, never from which
executables happen to be installed. On Codex, probe `claude` then `gemini`.
On Claude Code, probe `codex` then `gemini`. Never offer the current host
family. Detect a candidate with
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

**`ask`** puts one cross-model review question into decision point ① on every
full-lane change. Probe the host-specific candidates above first. With a
runnable candidate, prefer the current host's native question tool: Claude Code
uses `AskUserQuestion` when available in the current agent; Codex uses
`request_user_input` when available in the active mode. Offer `這次不使用` and
`使用 <tool>`. If the interface requires a recommended choice, mark
`這次不使用` as recommended so quota use and repository-data egress remain
opt-in. If the candidate runs but no native question tool is available, ask one
blocking plain-language Markdown question with the same choices and no
fabricated recommendation. If there is no runnable different-model-family CLI,
state that no such review tool is available and continue without asking.

The answer governs this change only and never rewrites the KICKOFF line. Add
the question to the running list kept in SKILL.md, so it lands in the plan's
`## Questions asked`; pass the accepted CLI or decline directly to Closing
Review. In the small lane there is only one reader, so this question is not
asked.

A **fixed CLI** is the standing reviewer choice and adds no intent question.
Probe it with the same availability rule before downstream use; never replace
it silently with another vendor.
