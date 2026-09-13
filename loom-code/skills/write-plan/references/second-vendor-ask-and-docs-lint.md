# Second-vendor modes and `docs-lint:`

This file owns CLI availability probes and the user-facing behavior for
`second-vendor: suggest`, `second-vendor: ask`, and a fixed CLI.

## Availability probe

An independent cross-model review only counts if it uses a non-interactive
command-line tool from a **different model family than the current host**.
Host identity comes from the environment running this skill, never from which
executables happen to be installed. On Codex, probe `claude` then `gemini`.
On Claude Code, probe `codex` then `gemini`. Never offer the current host
family. Detect a candidate with `command -v <cli>` **and** a probe that it runs —
`<cli> --version` must exit 0. In zsh `command -v` may print an alias or a
function body rather than a path; do not try to parse it. **Any non-empty
output plus a `<cli> --version` that exits 0 counts as present**, and
nothing else does. Never `which`: it reports shell aliases and stale
hashes, and suggesting a tool that turns out not to run costs the user a
question for nothing. Never suggest the host itself.

Probe candidates in canonical order: Claude, Codex, Gemini, excluding the
host vendor. Supply every passing candidate to `second_vendor_policy.py` as
observed data. Do not install, authenticate, select models, or infer
availability from configuration. When the defaults file has no
`second-vendor:` line, create it from the template if needed and record
`- second-vendor: suggest — default non-blocking visibility (<date>)`.

## `second-vendor: suggest`

Run the policy only after the plan's Risk lines exist. The policy owns risk
classification and vendor choice; the station supplies grounded risk items
as `{signal, anchors}`; do not reclassify risk or synthesize a reason
the returned JSON did not contain.

For `availability`, tell the user that the returned other-vendor CLI is
available. For `recommendation`, recommend it and render the returned
`recommendation_reasons` with their anchors. In both cases, continue without
waiting. There is no background listener, reminder, or persistent opt-in
state: only a reply received in the active task before Closing Review causes
one policy reevaluation.

Render either suggest result as a one-column Markdown table with exactly one
heading and one descriptive cell. Emit exactly two blank lines before and after
the table. Keep the source readable as raw Markdown:

```markdown


| <heading> |
|---|
| <description> |


```

Use the semantic heading `Independent review from a different model family`
for availability and `Independent review from a different model family
recommended` for recommendation. Render the heading and description in the
user's current conversation language. Put the vendor, grounded reasons when
present, opt-in cutoff, and `continue without waiting` statement together in
the single description cell. Add no second column or decorative row.

When that reevaluation returns `selection-confirmed`, append
`user-decided — second-vendor selection-confirmed: <vendor>` to the plan's
`## Risks` section and commit that plan edit before Closing Review starts.
The plan charter's `plan-maintained` edits-after rule authorizes this update
even when the initial plan commit already exists. Closing Review consumes
that line as the selected reviewer; it is a result record, not a fabricated
entry in `## Questions asked`.

In the small lane the notice is informational only and the policy does not
accept an active-change vendor selection. If the user accepts anyway, report
the policy's `next-change-only` result; it does not mutate the current reviewer
identity or the standing default. The reviewer floor is computed later and
independently from the complete branch delta. A reply after Closing Review
starts is likewise next-change-only. No reply means no second vendor for this
change.

## `second-vendor: ask`

`ask` is a standing choice that puts one cross-model review question to the
user on every full-lane change. The answer governs only that change and never
rewrites the KICKOFF line. Probe the host-specific candidates above first.

With a runnable candidate, prefer the current host's native question tool.
Claude Code uses `AskUserQuestion` when it is available in the current agent;
the authoritative tool reference names that tool and owns its live schema
([Claude Code tools reference](https://code.claude.com/docs/en/tools-reference)).
Codex uses `request_user_input` only when the host exposes it in the active
mode; its live tool schema owns the valid question shape and availability, and
the official implementation enforces both mode and root-thread availability
([Codex handler](https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/request_user_input.rs)).
Ask whether to use the named candidate for an independent review by a different
model family. Treat the two choice meanings as `decline this change` and
`use <tool>`, and render both choices in the user's current conversation
language. If the native interface requires one option to be recommended, mark
`decline this change` as recommended so extra quota use and repository-data
egress remain opt-in.

When a runnable candidate exists but the native tool is unavailable, ask one
blocking plain-language Markdown question with the same two choices and no
fabricated recommendation. When there is no runnable different-model-family CLI,
state that no such review tool is currently available and continue without asking.

Add the question to the running list kept in step 3, so it lands in the
plan's `## Questions asked` section and the intent's decision record. That
answer names a CLI or declines cross-model review for this change.

**In the small lane**, this opt-in question is not asked. The reviewer floor
is computed later and independently from the complete branch delta.

## Fixed CLI

A fixed CLI remains the standing reviewer choice. Probe it with the same
rule before use and follow the existing review failure behavior if it is not
usable; do not silently substitute another vendor.

## `docs-lint: <command> | none — <why>`

`docs/loom/KICKOFF-DEFAULTS.md` may also carry this line — a repo declaring
its own prose linter, so the review station's reviewer contract can trust
it instead of raising style findings itself (declared → no style findings;
`none` → style findings capped at `nit`).

This station never installs a docs linter and never asks about one on first
contact with a repo. When the line is absent, treat it as `none` — there is
no detection step for it the way there is for `package-tests:`.
