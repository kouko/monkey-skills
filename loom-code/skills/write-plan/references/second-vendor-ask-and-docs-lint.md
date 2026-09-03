# The second-reviewer suggestion, `second-vendor: ask`, and `docs-lint:`

Three `docs/loom/KICKOFF-DEFAULTS.md` lines, all part of the decision point
① message written in step 3 item 3.

## The once-per-change suggestion (`second-vendor: <cli> | none`)

A second reviewer only counts if it is a non-interactive command-line tool
from a **different model vendor than the host you are running on**: on
Claude Code look for `codex` or `gemini`, on Codex look for `claude` or
`gemini`. Detect it with `command -v <cli>` **and** a probe that it runs —
`<cli> --version` must exit 0. In zsh `command -v` may print an alias or a
function body rather than a path; do not try to parse it. **Any non-empty
output plus a `<cli> --version` that exits 0 counts as present**, and
nothing else does. Never `which`: it reports shell aliases and stale
hashes, and suggesting a tool that turns out not to run costs the user a
question for nothing. Never suggest the host itself.

Include the suggestion only if `docs/loom/KICKOFF-DEFAULTS.md` has no
`second-vendor:` line and such a tool is present. Say it in one plain
sentence with the number in it: reviewing with a second vendor costs a few
minutes and some quota, and when this system's own spec was reviewed, five
of the seven serious problems were found by only one of the two vendors.
Whatever the answer, record it in `docs/loom/KICKOFF-DEFAULTS.md` as
`- second-vendor: <cli> | none — <reason> (<date>)` and never ask again; if
that file does not exist yet, create it first from
`contract/templates/KICKOFF-DEFAULTS.md`. If the line already exists, say
nothing about it.

## `second-vendor: ask`

This is a different line from the once-per-change suggestion above. `ask`
is a standing choice the user made once, in KICKOFF-DEFAULTS, that the
question itself should be put to them **every change** — the answer
governs only that one change and never rewrites the KICKOFF line.

When `docs/loom/KICKOFF-DEFAULTS.md` carries `second-vendor: ask`, ask one
plain sentence, in the same decision-point-① message as everything else:

> 這次要不要用 Codex 當第二位讀者？
>
> (Do you want to use Codex as the second reader this time?)

Add the question to the running list kept in step 3, so it lands in the
plan's `## Questions asked` section. The review station copies the answer
(`<cli>` or `none`) into `review.json`'s top-level `second_vendor` field at
the first checkpoint — that field is per-change, unlike the KICKOFF line.

**In the small lane**, there is only one reader, so this question is not
asked at all, and the `second_vendor` field is omitted from `review.json`
rather than written as `none`.

The existing `<cli>` / `none` values behave exactly as they did before this
line existed: a fixed answer, asked once, never revisited.

## `docs-lint: <command> | none — <why>`

`docs/loom/KICKOFF-DEFAULTS.md` may also carry this line — a repo declaring
its own prose linter, so the review station's reviewer contract can trust
it instead of raising style findings itself (declared → no style findings;
`none` → style findings capped at `nit`).

This station never installs a docs linter and never asks about one on first
contact with a repo. When the line is absent, treat it as `none` — there is
no detection step for it the way there is for `package-tests:`.
