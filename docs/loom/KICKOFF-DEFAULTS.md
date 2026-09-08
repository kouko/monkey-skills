# Kickoff Defaults — monkey-skills

<!-- One line per key, grammar `- <key>: <value> — <reason> (<date>)`.
Keys are declared in loom-code/contract/manifest.yaml `kickoff_defaults`;
loom_checker.py reads this file. Absent key = default. -->

- second-vendor: ask — kouko decides per change; asked once at decision point ① and recorded in review.json (2026-09-04)
- package-tests: uv run --isolated --with-requirements requirements-package-tests.lock python scripts/run_package_tests.py --loom-family -q — the runner is the single inventory for every Loom pytest and shell-test surface; CI selects named groups from the same inventory while closing Review runs all groups once; isolated invocations preserve per-directory pytest configurations and module names; the hash-verified lock avoids host-Python drift; the code group retains pytest-xdist `-n auto`; a bare pytest at the repo root aborts on dbt-wiki collection (2026-09-08)
- standing-docs: waived — DESIGN.md never applies to a plugin repo; PRINCIPLES.md exists and is ratified per change kind (2026-09-03)
- session-start-baseline: 923fb84a 5278 — measured with `bash loom-code/hooks/session-start </dev/null | python3 -c 'import sys;print(len(sys.stdin.read().split()))'` in an empty git repo, merge-base of the loom 1.0 change (Python str.split — wc disagrees between macOS and GNU) (2026-09-03)
- interface-surfaces: **/cli/**, **/api/**, **/commands/**, **/*.tsx, **/templates/** — manifest default; SKILL.md and hooks are the `skill`/`gate` artifact types, not user interfaces, so skill edits stay engineering (2026-09-03)
- docs-lint: none — no lint adopted yet; internal loom docs are English from 2026-09-05 — see intent 2026-09-03-artifact-language-policy (2026-09-05)
- default-lane: full — no change here has declared express or gate-only yet; every change to date has earned full (checker/hooks/agent-contract/SKILL.md edits are common in this repo) (2026-09-05)
