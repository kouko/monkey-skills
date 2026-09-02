# Kickoff Defaults — monkey-skills

## On-ramp standing choices

<!-- Repo-level on-ramp decisions read by check_onramp_choice.py; revisited
only by editing this file. Grammar owned by
loom-code/hooks/family-reception.md §On-ramp standing choices. -->

- row 1 (product-principles): standing direct — monkey-skills deliberately keeps no docs/loom/PRINCIPLES.md; loom-family arcs go direct to a brief (2026-08-18)

## loom contract keys

<!-- One line per key, grammar `- <key>: <value> — <reason> (<date>)`.
Keys are declared in loom-code/contract/manifest.yaml `kickoff_defaults`;
loom_checker.py reads this file. Absent key = default. -->

- package-tests: python3 -m pytest loom-code/scripts/ scripts/ .claude/hooks/ -q — same line as CI; a bare pytest at the repo root aborts on dbt-wiki collection (2026-09-02)
