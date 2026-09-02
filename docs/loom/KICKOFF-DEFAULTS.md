# Kickoff Defaults — monkey-skills

<!-- One line per key, grammar `- <key>: <value> — <reason> (<date>)`.
Keys are declared in loom-code/contract/manifest.yaml `kickoff_defaults`;
loom_checker.py reads this file. Absent key = default. -->

- second-vendor: codex — kouko chose Codex CLI as the second reviewer; this design's own spec review found 5 of 7 fatal findings with only one vendor (2026-09-02)
- package-tests: python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q — same line as CI; a bare pytest at the repo root aborts on dbt-wiki collection (2026-09-02)
- standing-docs: waived — DESIGN.md never applies to a plugin repo; PRINCIPLES.md exists and is ratified per change kind (2026-09-03)
- session-start-baseline: 923fb84a 5278 — measured with `LC_ALL=C bash loom-code/hooks/session-start </dev/null | wc -w` in an empty git repo, merge-base of the loom 1.0 change; `wc -w` disagrees with itself across locales on some unicode punctuation, so the count is pinned to LC_ALL=C (2026-09-03)
- interface-surfaces: **/cli/**, **/api/**, **/commands/**, **/*.tsx, **/templates/** — manifest default; SKILL.md and hooks are the `skill`/`gate` artifact types, not user interfaces, so skill edits stay engineering (2026-09-03)
