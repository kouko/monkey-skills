# Kickoff Defaults — monkey-skills

<!-- One line per key, grammar `- <key>: <value> — <reason> (<date>)`.
Keys are declared in loom-code/contract/manifest.yaml `kickoff_defaults`;
loom_checker.py reads this file. Absent key = default. -->

- second-vendor: codex — kouko chose Codex CLI as the second reviewer; this design's own spec review found 5 of 7 fatal findings with only one vendor (2026-09-02)
- package-tests: python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q — same line as CI; a bare pytest at the repo root aborts on dbt-wiki collection (2026-09-02)
- standing-docs: waived — engineering repo: no product principles by decision of 2026-08-18; DESIGN.md never applies (2026-09-03)
- session-start-baseline: 923fb84a 5281 — measured with `bash loom-code/hooks/session-start </dev/null | wc -w` in an empty git repo, merge-base of the loom 1.0 change (2026-09-02)
- interface-surfaces: **/cli/**, **/api/**, **/commands/**, **/*.tsx, **/templates/** — manifest default; SKILL.md and hooks are the `skill`/`gate` artifact types, not user interfaces, so skill edits stay engineering (2026-09-03)
