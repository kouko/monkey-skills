# Plan: deep-research as a skill (agent-portable, key-free)

Source brief: docs/loom/specs/2026-06-02-deep-research-skill.md
Total tasks: 10 (width is fine — 5 parallel leaves at level 1)
Critical-path depth: 4 (longest chain: T1 → T2 → T6 → T10; verified, not just claimed)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-03, 14/14; 2 advisory notes — see Notes)

Layout decision (resolves brief OQ2): top-level `deep-research/` is restructured
from a standalone Python package INTO a plugin — `research-toolkit/.claude-plugin/
plugin.json` + `research-toolkit/skills/deep-research/{SKILL.md, scripts/}`,
following the distill-sessions convention (tests live in `scripts/` alongside
code; `scripts/pytest.ini` provides the test runner; no root pyproject). It is
its own plugin (a distinct research capability, not a fit for code-toolkit /
dev-workflow / obsidian).

Migration model: the existing pure modules (`schemas`, `rank`, `dedup`,
`prompts`) and the pure helpers inside `core.py` are already tested and
adapter-free; each migration task RELOCATES one module into `scripts/` (flat
imports), ports its test, and adds a minimal `__main__` CLI so the skill's
agent can invoke prompt-getters / pure ops over stdin-stdout JSON. The
adapter / provider / asyncio-orchestration layer is deleted (T7). The agent
(skill executor) supplies LLM reasoning + WebSearch + WebFetch + subagent
fan-out; the scripts supply only deterministic logic.

Notes:
- Amendment after PASS (2026-06-03, re-review skipped — additive + schema-safe per
  writing-plans §Amending a PASS plan): folded reviewer advisory into T1 —
  pytest.ini MUST set `cache_dir` to a /tmp path so `.pytest_cache/` is not
  created as a nested subfolder under `scripts/` (the flat-skill-structure hook,
  which T1's own GREEN asserts, bans depth≥2 dirs). No tasks added/removed, no
  dependency/DAG change.
- Advisory not actioned (reviewer Check 15): T6 (synthesis.py) and T9 (SKILL.md)
  are parallel-eligible (disjoint files, no edge) but left Independent:false —
  deliberate: SKILL.md authoring is reasoning-heavy and is sequenced after the
  script interfaces land. SDD may still run them concurrently if desired.
- Transition safety: migration tasks (T2-T6) ADD files under `skills/`; the old
  `src/`/`tests/` tree keeps passing until T7 deletes it last. Both test suites
  are green during the overlap.
- CLI contract (each keeper's `__main__`, consumed by SKILL.md T9/T10):
  - `prompts.py {scope|search|fetch|verify|synthesis} ...` → prints prompt text
  - `schemas.py {scope|search|extract|verdict|report}` → prints the JSON Schema
  - `dedup.py` (stdin: {results, seen, fetch_slots}) → prints {novel, seen, slots}
  - `rank.py` (stdin: claims) → prints ranked≤25; `rank.py quorum` (stdin: verdicts) → prints survived bool
  - `synthesis.py blocks` (stdin: ranked+verdicts) → confirmed/killed blocks;
    `synthesis.py report` (stdin: report+claims) → stats + markdown

---

## Task 1 — Plugin scaffold
- Description: Create the plugin skeleton: `.claude-plugin/plugin.json` (name
  `deep-research`, version `0.1.0`, description, author kouko, homepage,
  repository, license MIT, keywords), `skills/deep-research/SKILL.md` with
  VALID frontmatter only (name + description + version; body is a one-line
  placeholder), and `skills/deep-research/scripts/pytest.ini`
  (`[pytest]` with `pythonpath = .` AND `cache_dir = /tmp/pytest_cache_deep_research`
  — the cache_dir redirect is REQUIRED so pytest does not create a
  `scripts/.pytest_cache/` nested subfolder, which the flat-skill-structure hook
  bans at depth≥2; matches the distill-sessions convention). No logic, no stage
  prose yet.
- Module: deep-research/ (packaging)
- Files touched: research-toolkit/.claude-plugin/plugin.json, research-toolkit/skills/deep-research/SKILL.md, research-toolkit/skills/deep-research/scripts/pytest.ini
- Context paths:
  - dev-workflow/.claude-plugin/plugin.json
  - dev-workflow/skills/distill-sessions/scripts/pytest.ini
- Acceptance:
  - RED: `test -f research-toolkit/skills/deep-research/SKILL.md` fails (file absent)
  - GREEN: all three files exist; `python -c "import json,sys,re; d=json.load(open('research-toolkit/.claude-plugin/plugin.json')); assert d['name']=='deep-research'"` passes; SKILL.md frontmatter parses (has `name:` and `description:`); the `.claude/hooks/validate-skill-folder-structure.sh` constraint holds (scripts/ is single-level)
- External surfaces: plugin manifest schema (Claude Code plugin.json) — metadata only
- Dependencies: none
- Independent: false
- Brief item covered: "registered in marketplace.json … restructured into the skill's scripts/" (Decision)

## Task 2 — Migrate schemas.py → scripts/
- Description: Relocate the 5 JSON Schemas + constants (VOTES_PER_CLAIM=3,
  REFUTATIONS_REQUIRED=2, MAX_FETCH=15, MAX_VERIFY_CLAIMS=25) into
  `scripts/schemas.py` (flat module, no `deep_research.` package imports). Add
  `__main__`: `python schemas.py {scope|search|extract|verdict|report}` prints
  the named schema as JSON. Port `test_schemas.py`.
- Module: deep_research schemas (scripts/schemas.py)
- Files touched: research-toolkit/skills/deep-research/scripts/schemas.py, research-toolkit/skills/deep-research/scripts/test_schemas.py
- Context paths:
  - deep-research/src/deep_research/schemas.py
  - deep-research/tests/test_schemas.py
  - docs/loom/specs/deep-research-decompiled-source.md
- Acceptance:
  - RED: `cd research-toolkit/skills/deep-research/scripts && pytest test_schemas.py` fails (ModuleNotFoundError)
  - GREEN: same pytest passes; `python schemas.py verdict` prints JSON with required `refuted`/`evidence`/`confidence`; constants equal 3/2/15/25
- External surfaces: none (stdlib only)
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "`schemas` — the 5 JSON Schemas + constants (SSOT the agent conforms to)" (Smallest End State)

## Task 3 — Migrate rank.py (+ quorum) → scripts/
- Description: Relocate `rank_claims` (stable multi-key sort + slice to
  MAX_VERIFY_CLAIMS) and `quorum_survives` (`valid≥2 and refuted<2`,
  all-abstain guard) into `scripts/rank.py` (flat, no package import — it
  already operates on generic dicts). Add `__main__`: `rank.py` (stdin claims
  JSON → ranked JSON), `rank.py quorum` (stdin verdicts JSON → `true`/`false`).
  Port `test_rank.py`.
- Module: deep_research rank (scripts/rank.py)
- Files touched: research-toolkit/skills/deep-research/scripts/rank.py, research-toolkit/skills/deep-research/scripts/test_rank.py
- Context paths:
  - deep-research/src/deep_research/rank.py
  - deep-research/tests/test_rank.py
- Acceptance:
  - RED: `pytest test_rank.py` (in scripts/) fails (ModuleNotFoundError)
  - GREEN: pytest passes incl. the all-abstain → killed case; `echo '[]' | python rank.py` prints `[]`; quorum of 3 abstains prints `false`
- External surfaces: none (stdlib only)
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "`rank` — stable multi-key claim sort … quorum survival" (Smallest End State)

## Task 4 — Migrate dedup.py → scripts/
- Description: Relocate `filter_novel` + URL normalization (strip `www.`,
  strip trailing `/`, lowercase host+path; raw-lowercase on parse failure) +
  fetch-budget accounting into `scripts/dedup.py` (flat). Add `__main__`:
  stdin `{results, seen, fetch_slots}` → stdout `{novel, seen, slots}`. Port
  `test_dedup.py`.
- Module: deep_research dedup (scripts/dedup.py)
- Files touched: research-toolkit/skills/deep-research/scripts/dedup.py, research-toolkit/skills/deep-research/scripts/test_dedup.py
- Context paths:
  - deep-research/src/deep_research/dedup.py
  - deep-research/tests/test_dedup.py
  - docs/loom/specs/deep-research-decompiled-source.md (normURL)
- Acceptance:
  - RED: `pytest test_dedup.py` (in scripts/) fails (ModuleNotFoundError)
  - GREEN: pytest passes; `www.X.com/a/` and `x.com/a` dedupe to one; fetch-budget caps novel count
- External surfaces: none (stdlib `urllib.parse` only)
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "`dedup` — URL-normalized novelty filter + fetch-budget accounting" (Smallest End State)

## Task 5 — Migrate prompts.py → scripts/
- Description: Relocate the verbatim prompt templates (scope / search / fetch /
  verify / synthesis) into `scripts/prompts.py` (flat). Add `__main__`:
  `prompts.py {scope|search|fetch|verify|synthesis}` with the required args
  (e.g. question, angle JSON, claim JSON, voter index) → prints the assembled
  prompt text. Port `test_prompts.py`.
- Module: deep_research prompts (scripts/prompts.py)
- Files touched: research-toolkit/skills/deep-research/scripts/prompts.py, research-toolkit/skills/deep-research/scripts/test_prompts.py
- Context paths:
  - deep-research/src/deep_research/prompts.py
  - deep-research/tests/test_prompts.py
  - docs/loom/specs/deep-research-decompiled-source.md
- Acceptance:
  - RED: `pytest test_prompts.py` (in scripts/) fails (ModuleNotFoundError)
  - GREEN: pytest passes; `python prompts.py scope --question "X"` prints the scope prompt containing "X" verbatim-template text
- External surfaces: none (stdlib only)
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "`prompts` — the verbatim prompt templates (SSOT the agent fills)" (Smallest End State)

## Task 6 — Extract synthesis.py (blocks + stats + render) → scripts/
- Description: Extract the pure synthesis helpers from `core.py`
  (`_confirmed_block`, `_killed_block`, `_collect_sources`, `_build_stats`,
  the `_CONF_RANK` map) plus the markdown renderer from `cli.py`
  (`_render_markdown`) into `scripts/synthesis.py` (flat; imports constants
  from `schemas`). Add `__main__`: `synthesis.py blocks` (stdin: ranked claims
  + verdicts → confirmed/killed prompt blocks) and `synthesis.py report`
  (stdin: report dict + ranked claims → stats dict + markdown). Write
  `test_synthesis.py` (RED first) covering block format + agentCalls stats
  formula + markdown render.
- Module: deep_research synthesis (scripts/synthesis.py)
- Files touched: research-toolkit/skills/deep-research/scripts/synthesis.py, research-toolkit/skills/deep-research/scripts/test_synthesis.py
- Context paths:
  - deep-research/src/deep_research/core.py
  - deep-research/src/deep_research/cli.py
  - deep-research/tests/test_core.py
- Acceptance:
  - RED: `pytest test_synthesis.py` (in scripts/) fails (no module / no assertion target)
  - GREEN: pytest passes; confirmed block matches `### [i] {claim}` + `Vote: {v}-{r}` format; `_build_stats` agentCalls = `1+angles+sources+verified*3+1`; markdown render emits `## Findings`
- External surfaces: none (stdlib only)
- Dependencies: Task 2 completes first (imports schemas constants)
- Independent: false
- Brief item covered: "report formatting / stats" (Smallest End State)

## Task 7 — Remove obsolete package layer
- Description: Delete the adapter / provider / asyncio-orchestration layer and
  the old package scaffolding now that pure logic lives under `scripts/`:
  `src/deep_research/{adapters,providers,cli,pipeline,core,__init__}.py`,
  `tests/{test_adapters,test_cli,test_providers,test_pipeline,test_core,
  test_core_degradation,test_package,__init__}.py`, `deep-research/pyproject.toml`,
  `deep-research/uv.lock`, `deep-research/.gitignore` (package-specific), and the
  now-empty `src/` + `tests/` trees.
- Module: deep-research/ (cleanup)
- Files touched: deep-research/src/ (deleted), deep-research/tests/ (deleted), deep-research/pyproject.toml (deleted), deep-research/uv.lock (deleted), deep-research/.gitignore (deleted)
- Context paths:
  - deep-research/src/deep_research/core.py
- Acceptance:
  - RED: `test ! -e deep-research/src/deep_research/adapters.py` fails (still present)
  - GREEN: none of the deleted paths exist; `cd research-toolkit/skills/deep-research/scripts && pytest` is green (5 migrated/new test files pass); no remaining reference to `deep_research.` package imports anywhere under deep-research/
- External surfaces: none
- Dependencies: Tasks 2, 3, 4, 5, 6 complete first (keepers relocated before deletion)
- Independent: false
- Brief item covered: "with `adapters.py` removed … `providers.py`, `cli.py`, `pipeline.py`, and `core.py` … removed" (Decision / What Becomes Obsolete)

## Task 8 — Register plugin in marketplace
- Description: Add the `deep-research` plugin entry to
  `.claude-plugin/marketplace.json` (`{name, description, source:
  "./deep-research/"}`) following the existing entry format.
- Module: .claude-plugin (registration)
- Files touched: .claude-plugin/marketplace.json
- Context paths:
  - .claude-plugin/marketplace.json
- Acceptance:
  - RED: `python -c "import json; d=json.load(open('.claude-plugin/marketplace.json')); assert any(p['name']=='deep-research' for p in d['plugins'])"` fails
  - GREEN: same assertion passes; `source` is `./deep-research/`; JSON still valid
- External surfaces: marketplace manifest schema — metadata only
- Dependencies: Task 1 completes first (plugin source dir exists)
- Independent: true
- Brief item covered: "The skill is registered in marketplace.json" (Decision)

## Task 9 — SKILL.md body: pipeline overview + stages 1-3 (scope / search+dedup / fetch)
- Description: Write the SKILL.md body up to and including the fetch stage:
  the agent-as-executor model (agent supplies LLM reasoning + WebSearch +
  WebFetch; scripts supply deterministic logic; NO API keys), the portable
  subagent fan-out convention (per `dispatching-parallel-agents`, abstract
  "dispatch N subagents" — NOT the CC Workflow tool), and stages: (1) Scope —
  `prompts.py scope` → agent emits angles conforming to `schemas.py scope`;
  (2) Search+dedup — per angle (fan-out) WebSearch → agent ranks via
  `prompts.py search` → `dedup.py` filters novel; (3) Fetch — WebFetch each
  novel source → agent extracts claims via `prompts.py fetch` +
  `schemas.py extract`. Keep body within the ~6000-token cap.
- Module: deep-research skill doc (SKILL.md)
- Files touched: research-toolkit/skills/deep-research/SKILL.md
- Context paths:
  - docs/loom/specs/2026-06-02-deep-research-skill.md
  - deep-research/src/deep_research/core.py (pipeline shape docstring)
  - code-toolkit/skills/dispatching-parallel-agents/SKILL.md
- Acceptance:
  - RED: `grep -c "## " research-toolkit/skills/deep-research/SKILL.md` returns <1 for stage headers (body still placeholder)
  - GREEN: body names stages Scope / Search / Fetch with their `prompts.py` + `schemas.py` + `dedup.py` invocations and the subagent fan-out for per-angle work; explicitly states "no API key"; SKILL.md body ≤6000 tokens; frontmatter intact
- External surfaces: none (doc)
- Dependencies: Tasks 2, 3, 4, 5 complete first (references their CLI surfaces)
- Independent: false
- Brief item covered: "The agent owns the I/O + reasoning — scope / extract … search … fetch … orchestration" (Smallest End State)

## Task 10 — SKILL.md body: stages 4-5 (rank / verify / synthesize) + degradation
- Description: Append the remaining stages + degradation to SKILL.md: (4) Rank
  — `rank.py` over all claims; (5) Verify — fan out VOTES_PER_CLAIM=3 subagent
  voters per ranked claim (`prompts.py verify` + `schemas.py verdict`), quorum
  via `rank.py quorum`; (6) Synthesize — `synthesis.py blocks` →
  `prompts.py synthesis` → agent emits report (`schemas.py report`) →
  `synthesis.py report` for stats + markdown. Document the 3 degradation paths
  (no claims / all refuted / synthesis failed) as graceful early-returns the
  agent honors. Add a script-invocation quick-reference appendix.
- Module: deep-research skill doc (SKILL.md)
- Files touched: research-toolkit/skills/deep-research/SKILL.md
- Context paths:
  - deep-research/src/deep_research/core.py (verify/synth/degradation logic)
  - docs/loom/specs/2026-06-02-deep-research-skill.md
- Acceptance:
  - RED: `grep -i "quorum" research-toolkit/skills/deep-research/SKILL.md` returns nothing (stages 4-5 not yet written)
  - GREEN: body documents the 3-voter fan-out + quorum survival + the 3 degradation paths + `synthesis.py` invocations; SKILL.md body still ≤6000 tokens; `.claude/hooks/validate-skill-folder-structure.sh` constraint holds
- External surfaces: none (doc)
- Dependencies: Tasks 6, 9 complete first (T9 = same-file predecessor; T6 = synthesis CLI referenced)
- Independent: false
- Brief item covered: "verify / synthesize LLM steps … orchestration (loop over angles, fan out verify voters)" (Smallest End State)
