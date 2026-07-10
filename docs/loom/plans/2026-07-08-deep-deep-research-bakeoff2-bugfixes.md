# Plan: deep-deep-research bake-off round 2 bugfixes

**Source brief**: docs/loom/specs/2026-07-08-deep-deep-research-bakeoff2-bugfixes.md
**Total tasks**: 3
**Critical-path depth**: 1 (≤5 ✓) — all three tasks touch disjoint files, no semantic dependency
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-07-08)

## Task 1 — SKILL.md: run-scoped work directory + sourceUrl key naming

- **Description**: Edit the File-carrier rule (around SKILL.md:61-67) to instruct
  picking a run-scoped working-directory name at Stage-1 start (default
  `work/` for the common single-run case; a distinguishing suffix, e.g.
  `work-<short-id>/`, when the agent is one of several concurrent
  deep-deep-research invocations in the same session) and using that same
  chosen directory consistently for every stage reference in the rest of
  the document. Separately, add one sentence to Stage 3 step 3 (around
  SKILL.md:330-337) naming the literal key claims must carry for their
  source URL: `sourceUrl` (matching what `prompts.py verify_prompt()`
  reads at prompts.py:106, not `url`).
- **Module**: `research-toolkit/skills/deep-deep-research/SKILL.md`
- **Files touched**: `research-toolkit/skills/deep-deep-research/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/research-toolkit/skills/deep-deep-research/scripts/prompts.py` (line 106 — the literal key the doc must match)
  - `/Users/kouko/GitHub/monkey-skills/research-toolkit/skills/deep-deep-research/scripts/schemas.py` (EXTRACT_SCHEMA, lines 71-91 — confirms no URL field is currently documented there; do not add one to the schema itself, this task is prose-only)
- **Acceptance**:
  - **RED**: dispatch a fresh-context cold-read agent per
    `judgment-rubrics.md` §5 ("Prompt / skill / rule text" row), handing
    it ONLY the CURRENT (unedited) SKILL.md and this scenario: "You are
    asked to run deep-deep-research as one of 3 concurrent invocations in
    the same session/cwd. What working-directory name do you pick, and
    what key name do you write on each extracted claim for its source
    URL?" — on the unedited doc, the cold reader picks bare `work/` (no
    distinguishing name) and/or does not reliably name the key
    `sourceUrl` (the doc never states it), demonstrating the doc gap.
  - **GREEN**: same cold-read scenario, run against the EDITED SKILL.md —
    the cold reader (a) picks a distinguishing directory name rather than
    bare `work/`, AND (b) names the key `sourceUrl` without prompting.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "Fix A ... resolves bugs #1 and #2" + "Fix B ...
  Add one doc sentence to SKILL.md's Stage 3 step 3 naming the literal
  key"

## Task 2 — prompts.py: verify_prompt tolerates url key alongside sourceUrl

- **Description**: Change `verify_prompt()`'s source-URL lookup from a
  hard `claim["sourceUrl"]` index to `claim.get("sourceUrl") or
  claim.get("url", "")`, matching the `.get(...)`-tolerant pattern
  already used throughout `synthesis.py` (e.g. synthesis.py:68, 82, 96)
  wherever a claim dict is read. Add a regression test proving a claim
  dict keyed `url` (no `sourceUrl` key at all) no longer raises KeyError
  and the URL still appears in the rendered prompt.
- **Module**: `research-toolkit/skills/deep-deep-research/scripts/prompts.py`
- **Files touched**: `research-toolkit/skills/deep-deep-research/scripts/prompts.py`, `research-toolkit/skills/deep-deep-research/scripts/test_prompts.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/research-toolkit/skills/deep-deep-research/scripts/prompts.py` (verify_prompt at lines 98-134, current hard index at line 106)
  - `/Users/kouko/GitHub/monkey-skills/research-toolkit/skills/deep-deep-research/scripts/test_prompts.py` (existing verify_prompt test conventions at lines 99-128 — both existing fixtures already carry `sourceUrl`; do not remove that coverage, only add the new `url`-only case)
- **Acceptance**:
  - **RED**: a new test (e.g.
    `test_verify_prompt_accepts_url_key_when_sourceurl_missing`) in
    test_prompts.py constructs `claim = {"claim": "X", "url":
    "https://source.example", "sourceQuality": "primary", "quote": "q"}`
    (no `sourceUrl` key) and calls `verify_prompt(claim=claim,
    voter_idx=0, question="Q?")` — fails on the current code with
    `KeyError: 'sourceUrl'`.
  - **GREEN**: same test passes after the fix, and asserts
    `"https://source.example" in result`. Existing tests
    (`test_verify_prompt_voter_numbering`, `test_verify_prompt_voter_idx_2`,
    `test_cli_verify`) still pass unmodified — they exercise the
    `sourceUrl`-present path and must not regress.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "Fix B (prompts.py, resolves bug #3) —
  verify_prompt() reads the source URL via claim.get('sourceUrl') or
  claim.get('url', '') instead of a hard claim['sourceUrl'] index"

## Task 3 — synthesis.py: _render_markdown handles list-shaped caveats and renders evidence

- **Description**: In `_render_markdown()`, (a) coerce
  `report["caveats"]` to a string before appending — if it is a list,
  join its items with newlines instead of assuming it is already a
  string; (b) in the findings-render loop, read and render each
  finding's `evidence` field (currently read nowhere in that loop,
  though every finding dict carries it per REPORT_SCHEMA), e.g. an
  indented `- Evidence: {evidence}` line under each finding's
  claim/confidence bullet, mirroring the existing `- <{src}>`
  per-source rendering style immediately below it.
- **Module**: `research-toolkit/skills/deep-deep-research/scripts/synthesis.py`
- **Files touched**: `research-toolkit/skills/deep-deep-research/scripts/synthesis.py`, `research-toolkit/skills/deep-deep-research/scripts/test_synthesis.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/research-toolkit/skills/deep-deep-research/scripts/synthesis.py` (_render_markdown at lines 128-166, caveats branch at 149-152, findings loop at 138-147)
  - `/Users/kouko/GitHub/monkey-skills/research-toolkit/skills/deep-deep-research/scripts/test_synthesis.py` (TestRenderMarkdown at lines 122-142 — existing convention for report-dict fixtures and markdown assertions)
  - `/Users/kouko/GitHub/monkey-skills/research-toolkit/skills/deep-deep-research/scripts/schemas.py` (REPORT_SCHEMA at lines 104-126 — confirms `caveats` is schema-typed `string` and `evidence` is schema-required per finding, i.e. this fix enforces schema intent the LLM output does not always satisfy)
- **Acceptance**:
  - **RED (caveats)**: a new test constructs `report = {"question": "Q?",
    "summary": "s", "findings": [], "caveats": ["First caveat.", "Second
    caveat."]}`, calls `_render_markdown(report)`, and currently raises
    `TypeError: sequence item N: expected str instance, list found` at
    the final `"\n".join(lines)`.
  - **GREEN (caveats)**: same test passes after the fix; asserts both
    `"First caveat."` and `"Second caveat."` appear in the returned
    markdown under a `## Caveats` heading.
  - **RED (evidence)**: a new test constructs a report with one finding
    carrying `"evidence": "Because of X and Y."` (plus existing required
    fields `claim`, `confidence`, `sources`), calls
    `_render_markdown(report)`, and asserts `"Because of X and Y." in
    md` — fails on current code (evidence never appears in output).
  - **GREEN (evidence)**: same assertion passes after the fix. Existing
    test `test_findings_section_emitted` (test_synthesis.py:122-142)
    still passes unmodified.
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "Fix C (synthesis.py, resolves bug #4) —
  _render_markdown(): (a) coerce caveats to a string ... (b) render each
  finding's evidence field"

## Notes

- All 3 tasks touch fully disjoint files (SKILL.md / prompts.py+test /
  synthesis.py+test) with no shared symbol or data dependency — eligible
  for `dispatching-parallel-agents` to dispatch all 3 implementers in one
  wave per `loom-code:dispatching-parallel-agents`.
- No task modifies `rank.py`, `dedup.py`, `schemas.py`, or any opt-in
  Stage-1/6 lever script — matches the brief's Out of Scope.
- Repo-memory mirror (docs/loom/BACKLOG.md or dogfood note for this
  bake-off round) travels in the same branch/PR as these 3 tasks, per
  this repo's "memory travels with the PR" convention — not a separate
  plan task; fold it into the branch-close step
  (`finishing-a-development-branch`).
