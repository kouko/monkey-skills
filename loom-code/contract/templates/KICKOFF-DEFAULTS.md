# Kickoff Defaults

> Minted from loom-code's contract package. From that moment it is
> THIS repo's own file — it never syncs back to the plugin; edit it
> freely.

<!-- One line per key, grammar `- <key>: <value> — <reason> (<date>)`.
Keys are declared in loom-code/contract/manifest.yaml `kickoff_defaults`;
loom_checker.py reads this file. Absent key = default. -->

- second-vendor: none — <why> (<date>)
- package-tests: <command> — the command a checkpoint's package-test probe must record; `none — <why>` when this repo has no suite (<date>)
- standing-docs: waived — <why> (<date>)          # silences the three-line WARN only; never the product PRINCIPLES rejection
- session-start-baseline: <sha> <words> — measured with `bash loom-code/hooks/session-start </dev/null | wc -w` in an empty git repo (<date>)
- interface-surfaces: **/cli/**, **/api/**, **/commands/**, **/*.tsx, **/templates/** — <why> (<date>)   # this is the default; edit to match the repo
- artifact-types: <glob>=<type> — <why> (<date>)
