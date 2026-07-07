# Plan: deep-deep-research file-carrier fix + heavyweight trigger

Source brief: docs/loom/specs/2026-07-07-deep-deep-research-file-carrier.md
Total tasks: 6
Critical-path depth: 4 (T1/T2 → T3 → T4 → T6; T5 independent leaf)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-07, 14/14 checks; 3 dispatch-time notes recorded in reviewer output)

## Task 1 — rank.py --claims-dir input mode
- Description: Add `--claims-dir DIR` to rank.py's rank path: read every
  `*.json` in DIR (each a JSON array of claims), merge in deterministic
  filename-sorted order, rank the merged pool. stdin path unchanged.
  `--claims-dir` and stdin are mutually exclusive (flag wins; document in
  module docstring CLI block). Quorum subcommand untouched.
- Module: research-toolkit/skills/deep-deep-research/scripts/rank.py
- Files touched: research-toolkit/skills/deep-deep-research/scripts/rank.py, research-toolkit/skills/deep-deep-research/scripts/test_rank.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/rank.py
  - research-toolkit/skills/deep-deep-research/scripts/test_rank.py
- Acceptance:
  - RED: test_rank.py::test_claims_dir_merges_files_in_filename_order fails
    (unknown flag) — test builds a tmp dir with 2 claim files, asserts merged
    ranking equals stdin-equivalent ranking and file order is name-sorted.
  - GREEN: that test passes; existing test_rank.py tests all still pass.
- External surfaces: none (stdlib argparse/json/pathlib only).
- Dependencies: none
- Independent: true
- Brief item covered: "rank.py accepts --claims-dir DIR (merge all *.json arrays, deterministic filename sort)"

## Task 2 — synthesis.py per-key file flags
- Description: Add repeatable `--key NAME=FILE` (JSON value from file) and
  `--key-dir NAME=DIR` (merge all `*.json` arrays in DIR, filename-sorted)
  to synthesis.py's blocks/report subcommands, assembling the payload dict
  from flags; stdin remains the fallback when no flags given (flags and
  stdin mutually exclusive — any flag disables stdin read). Update module
  docstring CLI block.
- Module: research-toolkit/skills/deep-deep-research/scripts/synthesis.py
- Files touched: research-toolkit/skills/deep-deep-research/scripts/synthesis.py, research-toolkit/skills/deep-deep-research/scripts/test_synthesis.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/synthesis.py
  - research-toolkit/skills/deep-deep-research/scripts/test_synthesis.py
- Acceptance:
  - RED: test_synthesis.py::test_blocks_payload_from_key_files fails (unknown
    flag) — test writes ranked/votes/verdicts JSON to tmp files, runs blocks
    via --key flags, asserts output equals the stdin-payload run.
  - GREEN: that test passes; existing test_synthesis.py tests all still pass.
- External surfaces: none (stdlib only).
- Dependencies: none
- Independent: true
- Brief item covered: "synthesis.py blocks/report accept per-key file flags (--key name=FILE, --key-dir name=DIR)"

## Task 3 — SKILL.md file-carrier stage rewrites
- Description: Rewrite the four monolith sites in deep-deep-research
  SKILL.md to the file-carrier flow: Stage 3 fetch subagents WRITE
  extraction to `work/claims/<angle>-<idx>.json` and return `{path, count}`
  only; Stage 4 uses `python scripts/rank.py --claims-dir work/claims >
  work/ranked.json`; Stage 5 collects verdicts into
  `work/verdicts/claim-<i>.json` + accumulates `work/votes.json`; Stage 6
  blocks/report use the Task-2 `--key`/`--key-dir` flags (report's
  all_claims via `--key-dir all_claims=work/claims`). Add one file-carrier
  rule beside the fan-out convention ("never emit the full claims pool
  inline in a command or a single response — pass file paths"). Update
  tool-matrix rows (lines ~662/672) to the new input shapes.
- Module: research-toolkit/skills/deep-deep-research/SKILL.md
- Files touched: research-toolkit/skills/deep-deep-research/SKILL.md
- Context paths:
  - research-toolkit/skills/deep-deep-research/SKILL.md
  - research-toolkit/skills/deep-deep-research/scripts/rank.py
  - research-toolkit/skills/deep-deep-research/scripts/synthesis.py
- Acceptance:
  - RED (diagnostic): `grep -n "echo '\[<all claims>\]'" SKILL.md` currently
    hits line ~336; blocks/report echo payloads at ~397/~607.
  - GREEN: zero grep hits for the three monolithic echo payloads; grep hits
    for `--claims-dir`, `--key`, `work/claims`; file-carrier rule present;
    tool-matrix rows match the new CLI; flag names byte-match Tasks 1-2
    implementations.
- External surfaces: none (doc).
- Dependencies: Tasks 1, 2 complete first (doc mirrors shipped CLI)
- Independent: false
- Brief item covered: "SKILL.md gains one explicit file-carrier rule … Stage 3/4/5/6 rewrites"

## Task 4 — description trigger swap + router row
- Description: In deep-deep-research SKILL.md frontmatter description, swap
  the single CJK trigger 想調整研究流程 → 徹底研究 (keep ≤250 chars, exactly
  ONE CJK trigger; pipeline-tweak intent stays as an EN clause). In
  using-research-toolkit SKILL.md, extend the deep-deep-research routing-row
  triggers with 徹底研究／多輪深挖 (body table — no budget cap).
- Module: research-toolkit/skills/using-research-toolkit/SKILL.md
- Files touched: research-toolkit/skills/deep-deep-research/SKILL.md, research-toolkit/skills/using-research-toolkit/SKILL.md
- Context paths:
  - research-toolkit/skills/deep-deep-research/SKILL.md
  - research-toolkit/skills/using-research-toolkit/SKILL.md
  - research-toolkit/scripts/test_research_toolkit_descriptions.py
- Acceptance:
  - RED (diagnostic): grep 徹底研究 in both files → 0 hits today.
  - GREEN: description contains 徹底研究, not 想調整研究流程, length ≤250;
    router row lists 徹底研究; `pytest research-toolkit/scripts/` (the #506
    static description gate) passes.
- External surfaces: none.
- Dependencies: Task 3 completes first (same SKILL.md file — sequential edit
  ordering, no semantic coupling)
- Independent: false
- Brief item covered: "swap the one CJK trigger … to 徹底研究; router row adds 徹底研究／多輪深挖"

## Task 5 — bake-off evidence mirror (dogfood report + memory store entry)
- Description: Write docs/loom/dogfood/2026-07-07-research-bakeoff-vs-builtin.md
  (method, 2/2 blind-judge verdicts with scores, citation spot-check 4/5+4/5,
  cost table, the two failure modes: headless 600s bg ceiling + monolithic
  mid-response 5xx, n=1 caveat). Add loom memory store entry
  docs/loom/memory/file-carrier-for-bulk-payloads.md per the store charter
  (README index line included).
- Module: docs/loom
- Files touched: docs/loom/dogfood/2026-07-07-research-bakeoff-vs-builtin.md, docs/loom/memory/file-carrier-for-bulk-payloads.md, docs/loom/memory/README.md
- Context paths:
  - docs/loom/memory/README.md
  - docs/loom/dogfood/2026-07-06-research-toolkit-firing-ab.md
- Acceptance:
  - RED (diagnostic): both new files absent today.
  - GREEN: both files exist; README.md index lists the new entry; dogfood
    report contains the score table and both failure modes.
- External surfaces: none (docs).
- Dependencies: none
- Independent: true
- Brief item covered: "Bake-off evidence mirrored to the repo: dogfood report file + a loom memory store entry"

## Task 6 — version bump 0.3.1 + codex sync
- Description: Bump research-toolkit version 0.3.0 → 0.3.1 in
  .claude-plugin/plugin.json, regenerate .codex-plugin mirror via
  `python3 scripts/sync_codex_manifests.py research-toolkit`, verify with
  `--check` (exit 0) and `check-marketplace-description-sync.py` still green.
- Module: research-toolkit/.claude-plugin
- Files touched: research-toolkit/.claude-plugin/plugin.json, research-toolkit/.codex-plugin/plugin.json
- Context paths:
  - research-toolkit/.claude-plugin/plugin.json
  - scripts/sync_codex_manifests.py
- Acceptance:
  - RED (diagnostic): version currently 0.3.0 in both manifests.
  - GREEN: both manifests read 0.3.1; `sync_codex_manifests.py --check
    research-toolkit` exit 0.
- External surfaces: repo tooling scripts (in-repo, no third-party).
- Dependencies: Tasks 1, 2, 3, 4 complete first (bump ships them)
- Independent: false
- Brief item covered: "research-toolkit 0.3.0 → 0.3.1 in .claude-plugin + .codex-plugin (sync script)"

## Notes

- T1+T2 are dispatch-parallel-safe (Independent: true, disjoint files). T5 is
  also Independent: true and disjoint from T1/T2 — eligible for the same wave.
- Command surface unchanged: new tests join the existing pytest suites under
  each skill's scripts/ (pytest.ini present); no new runnable verb.
- CI gates that must stay green: research-toolkit-ci.yml (description static
  gate), skill-structure hook (flat subfolders — no new dirs added),
  Conventional Commits (single kebab-case scope).
