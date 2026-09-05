# Kickoff Defaults — monkey-skills

<!-- One line per key, grammar `- <key>: <value> — <reason> (<date>)`.
Keys are declared in loom-code/contract/manifest.yaml `kickoff_defaults`;
loom_checker.py reads this file. Absent key = default. -->

- second-vendor: ask — kouko decides per change; asked once at decision point ① and recorded in review.json (2026-09-04)
- package-tests: python3 scripts/run_package_tests.py loom-code/scripts/ scripts/ .claude/hooks/ -q -n auto -- loom-design/scripts/ -q — one pytest session per `--` group because loom-design/scripts/ carries its own pytest.ini (importlib mode) and cannot share a session with the loom-code paths; CI's loom-code job runs the loom-code/scripts, scripts and .claude/hooks paths (-v in place of -q) and a separate loom-design job runs loom-design/scripts/; `-n auto` = pytest-xdist 取 runner 偵測到的可用 CPU 數（2026-09-03 量測：本機 16 核 34 秒、原串行 200 秒；CI 4 核預期 ~40 秒）；固定數字會在其中一邊過載或閒置；a bare pytest at the repo root aborts on dbt-wiki collection (2026-09-05)
- standing-docs: waived — DESIGN.md never applies to a plugin repo; PRINCIPLES.md exists and is ratified per change kind (2026-09-03)
- session-start-baseline: 923fb84a 5278 — measured with `bash loom-code/hooks/session-start </dev/null | python3 -c 'import sys;print(len(sys.stdin.read().split()))'` in an empty git repo, merge-base of the loom 1.0 change (Python str.split — wc disagrees between macOS and GNU) (2026-09-03)
- interface-surfaces: **/cli/**, **/api/**, **/commands/**, **/*.tsx, **/templates/** — manifest default; SKILL.md and hooks are the `skill`/`gate` artifact types, not user interfaces, so skill edits stay engineering (2026-09-03)
- docs-lint: none — no lint adopted yet; internal loom docs are English from 2026-09-05 — see intent 2026-09-03-artifact-language-policy (2026-09-05)
