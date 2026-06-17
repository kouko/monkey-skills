# Plan: ascii-graph skill (v1, in-house only)

Source brief: docs/code-toolkit/specs/2026-06-17-ascii-graph-skill.md
Total tasks: 13 (width uncapped; many parallel leaves)
Critical-path depth: 5 (T2 → L1 → L2 → T12 → T13) — at the ceiling, ≤5
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-17, 14/14 checks, zero defects)

Home: `ascii-graph-toolkit/skills/ascii-graph/` — **CONFIRMED by user 2026-06-17**
(new plugin `ascii-graph-toolkit`, skill `ascii-graph`). Skill subfolders are flat
(scripts/, tests/ one level) per repo CLAUDE.md.

Shared primitive: `scripts/width.py` (display-width via wcwidth) is imported by all
check/generator modules. Modules run from the skill ROOT (flat imports; `python
scripts/align.py` with sys.path[0]=scripts dir — see repo lesson on flat-import scripts).

---

## Task 1 — plugin + skill skeleton
- Description: Create the plugin/skill skeleton: `.claude-plugin/plugin.json`, a `plugins` entry in the repo `.claude-plugin/marketplace.json`, the skill dir with a SKILL.md **stub** (valid frontmatter `name`/`description`, body TBD), and empty `scripts/` + `tests/` dirs.
- Module: `ascii-graph-toolkit/` (manifest + skeleton)
- Files touched: ascii-graph-toolkit/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, ascii-graph-toolkit/skills/ascii-graph/SKILL.md
- Context paths:
  - .claude-plugin/marketplace.json (existing entries as template)
  - obsidian/.claude-plugin/plugin.json (a plugin.json example)
  - .claude/hooks/validate-skill-folder-structure.sh
- Acceptance:
  - RED: `validate-skill-folder-structure.sh` run against the new skill dir fails before the dir exists / passes after; `python -c "import json;json.load(open('.claude-plugin/marketplace.json'))"` parses.
  - GREEN: folder-structure hook passes; marketplace.json parses and contains the new plugin entry.
- Dependencies: none
- Independent: true
- Brief item covered: "New skill = thin SKILL.md router + two pure-Python tools" (Smallest End State)

## Task 2 — width.py shared display-width primitive
- Description: Implement `display_width(s)` and `char_width(c)` using `wcwidth`, with the brief's policy: CJK Wide/Fullwidth = 2, Ambiguous = 1, box-drawing = 1, control/zero-width = 0; emoji not relied on.
- Module: `scripts/width.py`
- Files touched: ascii-graph-toolkit/skills/ascii-graph/scripts/width.py, ascii-graph-toolkit/skills/ascii-graph/tests/test_width.py
- Context paths:
  - docs/code-toolkit/specs/2026-06-17-ascii-graph-skill.md (width policy)
- Acceptance:
  - RED: test_width asserts display_width('中文')==4, ('ｱ'/'あ'/'ア')==2 each, ('abc')==3, box '─│┌'==1 each, ambiguous '·'==1.
  - GREEN: all assertions pass via `pytest`.
- External surfaces: `wcwidth` (third-party, jquast) — sole external dep; declared here, imported by all other modules. Pure-Python, no binary.
- Dependencies: none
- Independent: true
- Brief item covered: "Do not reinvent width computation — wcwidth is canon" (Alternatives); width policy (Smallest End State)

## Task 3 — checks_seam.py (vertical-seam connect)
- Description: Implement the PoC core check: every box `│` must have a structural glyph (│ or corner/junction) directly above or below at the SAME display-column; return list of (line, display-col) violations.
- Module: `scripts/checks_seam.py`
- Files touched: ascii-graph-toolkit/skills/ascii-graph/scripts/checks_seam.py, ascii-graph-toolkit/skills/ascii-graph/tests/test_checks_seam.py
- Context paths:
  - /tmp/poc/align.py (proven seam logic to port)
  - ascii-graph-toolkit/skills/ascii-graph/scripts/width.py
- Acceptance:
  - RED: test_seam flags the PoC R1 CJK-overflow box (≥1 violation) and passes the R2 clean box (0 violations).
  - GREEN: both assertions pass.
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "align.py — vertical-seam drift flags" (Smallest End State / PoC Result)

## Task 4 — checks_table.py (table-block equal-width)
- Description: Detect table blocks (consecutive lines bracketed by ┌─┐ / ├─┤ / └─┘ or all starting+ending with │) and flag rows whose display width differs from the block's border width.
- Module: `scripts/checks_table.py`
- Files touched: ascii-graph-toolkit/skills/ascii-graph/scripts/checks_table.py, ascii-graph-toolkit/skills/ascii-graph/tests/test_checks_table.py
- Context paths:
  - ascii-graph-toolkit/skills/ascii-graph/scripts/width.py
- Acceptance:
  - RED: test_table flags a CJK table with a too-wide content row; passes an aligned table.
  - GREEN: both assertions pass.
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "Oracle blind-spots to harden: table-block equal-width" (PoC Result)

## Task 5 — checks_kink.py (seam-straightness + arrowhead)
- Description: Flag connector kinks the v0 rule misses: a vertical run (│/┬/┴/▼/▲) that shifts display-column between adjacent lines without a junction; and an arrowhead (▼/▲) whose column is not inside the box it points into.
- Module: `scripts/checks_kink.py`
- Files touched: ascii-graph-toolkit/skills/ascii-graph/scripts/checks_kink.py, ascii-graph-toolkit/skills/ascii-graph/tests/test_checks_kink.py
- Context paths:
  - ascii-graph-toolkit/skills/ascii-graph/scripts/width.py
- Acceptance:
  - RED: test_kink flags an off-by-one connector kink; passes a straight seam.
  - GREEN: both assertions pass.
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "Oracle blind-spots to harden: seam-straightness + arrowhead-into-box" (PoC Result)

## Task 6 — gen_table.py (CJK-aligned table generator)
- Description: `render_table(headers, rows)` → display-width-aligned Unicode box table (and pure-ASCII fallback). One-shot, no iteration.
- Module: `scripts/gen_table.py`
- Files touched: ascii-graph-toolkit/skills/ascii-graph/scripts/gen_table.py, ascii-graph-toolkit/skills/ascii-graph/tests/test_gen_table.py
- Context paths:
  - ascii-graph-toolkit/skills/ascii-graph/scripts/width.py
- Acceptance:
  - RED: test_gen_table renders a 中/日/EN-mixed table; assert every output line has equal display_width.
  - GREEN: assertion passes.
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "Deterministic generators … CJK-aligned tables" (Smallest End State)

## Task 7 — gen_flow.py (linear/layered flow generator)
- Description: `render_flow(steps)` → vertical stack of CJK-aligned boxes joined by centered down-arrows; supports a simple 2-way branch.
- Module: `scripts/gen_flow.py`
- Files touched: ascii-graph-toolkit/skills/ascii-graph/scripts/gen_flow.py, ascii-graph-toolkit/skills/ascii-graph/tests/test_gen_flow.py
- Context paths:
  - ascii-graph-toolkit/skills/ascii-graph/scripts/width.py
- Acceptance:
  - RED: test_gen_flow renders a 中/日 step list; assert each box's border width == its content display width and the trunk column is constant.
  - GREEN: assertions pass.
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "Deterministic generators … linear/layered flows" (Smallest End State)

## Task 8 — gen_tree.py (tree/hierarchy generator)
- Description: `render_tree(node)` → indented Unicode tree (├─ / └─ / │) from a nested dict/list; CJK labels aligned.
- Module: `scripts/gen_tree.py`
- Files touched: ascii-graph-toolkit/skills/ascii-graph/scripts/gen_tree.py, ascii-graph-toolkit/skills/ascii-graph/tests/test_gen_tree.py
- Context paths:
  - ascii-graph-toolkit/skills/ascii-graph/scripts/width.py
- Acceptance:
  - RED: test_gen_tree renders a 2-level 中/日 tree; assert branch glyphs sit at the expected display-columns.
  - GREEN: assertion passes.
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "Deterministic generators … trees / hierarchies" (Smallest End State)

## Task 9 — gen_bar.py (horizontal bar generator)
- Description: `render_bar(pairs)` → horizontal bar chart; CJK labels right-padded to a common display-width, bars scaled to max value.
- Module: `scripts/gen_bar.py`
- Files touched: ascii-graph-toolkit/skills/ascii-graph/scripts/gen_bar.py, ascii-graph-toolkit/skills/ascii-graph/tests/test_gen_bar.py
- Context paths:
  - ascii-graph-toolkit/skills/ascii-graph/scripts/width.py
- Acceptance:
  - RED: test_gen_bar renders 中/日-labelled bars; assert label column has constant display-width and bar lengths are proportional.
  - GREEN: assertions pass.
- Dependencies: Task 2 completes first
- Independent: true
- Brief item covered: "Deterministic generators … horizontal bar charts" (Smallest End State)

## Task 10 — align.py CLI (wire the three checks)
- Description: CLI that reads a diagram (stdin or file arg), prints the per-line display-width report, runs checks_seam + checks_table + checks_kink, prints violations (line + display-col), and exits 0 (clean) / 1 (issues).
- Module: `scripts/align.py`
- Files touched: ascii-graph-toolkit/skills/ascii-graph/scripts/align.py, ascii-graph-toolkit/skills/ascii-graph/tests/test_align_cli.py
- Context paths:
  - ascii-graph-toolkit/skills/ascii-graph/scripts/checks_seam.py, checks_table.py, checks_kink.py, width.py
  - /tmp/poc/r1.txt, /tmp/poc/r2.txt (PoC fixtures)
- Acceptance:
  - RED: test_align_cli runs the CLI on the PoC R1 input → exit 1 with ≥6 issues; on R2 → exit 0.
  - GREEN: both pass.
  - Command-surface: `python scripts/align.py <file>` documented in SKILL.md (T12) as the verify-loop verb.
- Dependencies: Tasks 3, 4, 5 complete first
- Independent: true
- Brief item covered: "Alignment oracle (align.py) — the verify-loop" (Smallest End State)

## Task 11 — generate.py CLI (dispatch to generators)
- Description: CLI dispatching a subcommand (`table`/`flow`/`tree`/`bar`) reading JSON/args on stdin to the matching gen_*.py module and printing the rendered diagram.
- Module: `scripts/generate.py`
- Files touched: ascii-graph-toolkit/skills/ascii-graph/scripts/generate.py, ascii-graph-toolkit/skills/ascii-graph/tests/test_generate_cli.py
- Context paths:
  - ascii-graph-toolkit/skills/ascii-graph/scripts/gen_table.py, gen_flow.py, gen_tree.py, gen_bar.py
- Acceptance:
  - RED: test_generate_cli invokes each subcommand with a 中/日 fixture; assert output non-empty and (via width.py) every line equal display-width for table.
  - GREEN: all subcommands pass.
  - Command-surface: `python scripts/generate.py <shape>` documented in SKILL.md (T12).
- Dependencies: Tasks 6, 7, 8, 9 complete first
- Independent: true
- Brief item covered: "Deterministic generators … one-shot" routing (Smallest End State)

## Task 12 — SKILL.md router content
- Description: Write the SKILL.md body: routing (layout-trivial → generate.py one-shot; model-drawn → draft→align.py→fix verify-loop), width policy (box=1/ambiguous=1/emoji-not-anchor), CN/EN/JP note, honest ceiling (class/ER/state/etc → emit Mermaid source SSOT), bundled relative paths, the two command-surface verbs. Keep <6000 tokens.
- Module: `skills/ascii-graph/SKILL.md`
- Files touched: ascii-graph-toolkit/skills/ascii-graph/SKILL.md
- Context paths:
  - docs/code-toolkit/specs/2026-06-17-ascii-graph-skill.md
  - ascii-graph-toolkit/skills/ascii-graph/scripts/align.py, generate.py
- Acceptance:
  - RED: a doc-lint check — SKILL.md frontmatter parses, all `scripts/…` relative paths it references exist, token count <6000, folder-structure hook passes.
  - GREEN: all checks pass.
- Dependencies: Tasks 1, 10, 11 complete first
- Independent: false
- Brief item covered: "thin SKILL.md router" (Smallest End State)

## Task 13 — end-to-end dogfood + package test suite
- Description: Dogfood the verify-loop end-to-end: draft a fresh mixed 中/日 flowchart, run `align.py`, fix to convergence; render one of each generator shape; run the full package test suite from repo root.
- Module: `skills/ascii-graph/tests/test_e2e.py`
- Files touched: ascii-graph-toolkit/skills/ascii-graph/tests/test_e2e.py
- Context paths:
  - ascii-graph-toolkit/skills/ascii-graph/scripts/ (all)
- Acceptance:
  - RED: test_e2e asserts a known-good converged flowchart passes align.py (exit 0) and each generator subcommand returns equal-width output.
  - GREEN: `pytest` over the package is green; align.py converges on the dogfood diagram.
  - Command-surface: package test invocation (`pytest ascii-graph-toolkit/`) runs and passes.
- Dependencies: Task 12 completes first
- Independent: false
- Brief item covered: "PoC-validated … converged" + verification (Decision / PoC Result)

## Notes
- T1 and T2 are level-0 parallel leaves (disjoint files: manifest vs scripts). T3–T9 are a 7-wide parallel level on T2. T10/T11 are a 2-wide level. Depth = 5.
- Same-file conflict guard: no two `Independent: true` tasks share a file (each check/generator is its own module). Per repo lesson, parallel implementers must not interleave commits in one worktree — orchestrator commits, or dispatch the wide level with file-disjoint partitions.
- wcwidth is the only external dependency (pure-Python). No Go/Rust/npm binary in v1.
- Home/name (`ascii-graph-toolkit`) is provisional — confirm before T1.
