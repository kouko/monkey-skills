# Plan: Portable Python deep-research (L1 → L2 → L3)

Source brief: docs/loom/specs/2026-06-02-deep-research-portable-python.md
Total tasks: 12 (width is fine — 6 parallel leaves at level 1, 2 at level 2, 3 at level 3)
Critical-path depth: 4 (longest chain: T1 → T2 → T8 → T11; verified, not just claimed)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-02, round 2, 14/14 — Task 7 split resolved round-1 Check-5; depth verified 4)

Layer map: L1 = T1–T8 + T10 (core, provider-agnostic, mock-tested — the
portability line, reached when T8+T10 are GREEN) · L2 = T9 adapters + T11 cli ·
L3 = T12 mcp_server.

Round-1 revision note: original Task 7 (whole orchestration engine in one ≤5-min
unit) failed Check 5. Split into T7 (asyncio helper, now an L1 leaf), T8 (core
happy-path), T10 (core degradation paths). `rank` (T5) no longer depends on
`schemas` (T2) — it operates on generic dicts — which shortens the pre-core
chain and holds critical-path depth at 4.

## Task 1 — Package skeleton + pyproject
- Description: Create `deep-research/` uv-managed package: `pyproject.toml`
  (Python 3.12, project name `deep-research`, optional-dependency groups
  `anthropic` / `search` / `mcp` / `dev`), `src/deep_research/__init__.py`
  exposing `__version__`, and `tests/__init__.py`. No logic yet.
- Module: deep-research/ (packaging)
- Files touched: deep-research/pyproject.toml, deep-research/src/deep_research/__init__.py, deep-research/tests/__init__.py, deep-research/tests/test_package.py
- Context paths:
  - obsidian/pyproject.toml
- Acceptance:
  - RED: `tests/test_package.py::test_imports` fails (no module) — `import deep_research; assert deep_research.__version__`
  - GREEN: `uv run --project deep-research pytest tests/test_package.py` passes
- External surfaces: build backend (hatchling) — packaging metadata only
- Dependencies: none
- Independent: false
- Brief item covered: "uv-managed Python package, three layers" (Decision)

## Task 2 — schemas.py (verbatim port)
- Description: Port the 5 JSON Schemas verbatim (SCOPE / SEARCH / EXTRACT /
  VERDICT / REPORT) as module-level dicts, plus typed dataclasses
  (`Angle`, `SearchResult`, `ExtractedClaim`, `Verdict`, `Finding`, `Report`).
  Constants `VOTES_PER_CLAIM=3`, `REFUTATIONS_REQUIRED=2`, `MAX_FETCH=15`,
  `MAX_VERIFY_CLAIMS=25`.
- Module: deep_research.schemas
- Files touched: deep-research/src/deep_research/schemas.py, deep-research/tests/test_schemas.py
- Context paths:
  - docs/loom/specs/2026-06-02-deep-research-portable-python.md
- Acceptance:
  - RED: `test_schemas::test_scope_schema_shape` fails — asserts SCOPE_SCHEMA requires `angles` with minItems 3 maxItems 6; VERDICT_SCHEMA requires `refuted`/`evidence`/`confidence`; constants equal 3/2/15/25
  - GREEN: pytest test_schemas passes
- External surfaces: none (stdlib dataclasses only)
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "Port the algorithm verbatim (prompts/schemas/quorum)" (Decision)

## Task 3 — prompts.py (verbatim port)
- Description: Port the 5 prompt builders as pure functions
  (`scope_prompt(question)`, `search_prompt(angle, question)`,
  `fetch_prompt(source, angle, question)`, `verify_prompt(claim, voter_idx, question)`,
  `synthesis_prompt(question, confirmed, killed)`), text copied verbatim from
  the decompiled source.
- Module: deep_research.prompts
- Files touched: deep-research/src/deep_research/prompts.py, deep-research/tests/test_prompts.py
- Context paths:
  - docs/loom/specs/2026-06-02-deep-research-portable-python.md
- Acceptance:
  - RED: `test_prompts::test_verbatim_markers` fails — asserts `verify_prompt` contains "Default to refuted=true if uncertain", "Try to REFUTE"; `fetch_prompt` contains "FALSIFIABLE"; `scope_prompt` contains "complementary search angles"
  - GREEN: pytest test_prompts passes
- External surfaces: none
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "Port the algorithm verbatim (prompts/schemas/quorum)" (Decision)

## Task 4 — dedup.py (pure logic)
- Description: Port URL normalization + dedup/budget gate as pure functions:
  `norm_url(u)` (strip `www.`, trailing slash, lowercase), and
  `filter_novel(results, seen, fetch_slots, rel_rank)` returning
  `(novel, dupes, budget_dropped, fetch_slots)`.
- Module: deep_research.dedup
- Files touched: deep-research/src/deep_research/dedup.py, deep-research/tests/test_dedup.py
- Context paths:
  - docs/loom/specs/2026-06-02-deep-research-portable-python.md
- Acceptance:
  - RED: `test_dedup::test_norm_and_budget` fails — `norm_url("https://www.x.com/a/")=="x.com/a"`; duplicate URL pushed to dupes; low-relevance over budget pushed to budget_dropped
  - GREEN: pytest test_dedup passes
- External surfaces: none (stdlib urllib.parse)
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "quorum logic ... dedup ... ported verbatim" (Smallest End State / Error)

## Task 5 — rank.py (pure logic + quorum)
- Description: Port `rank_claims(claims, imp_rank, qual_rank, limit)`
  (importance×quality sort + slice to `limit`) and `quorum_survives(verdicts)`
  implementing `valid>=REFUTATIONS_REQUIRED and refuted<REFUTATIONS_REQUIRED`
  with abstain handling (None votes drop from `valid`). Operates on plain
  dicts / sequences — does NOT import `schemas` (keeps it an L1 leaf).
- Module: deep_research.rank
- Files touched: deep-research/src/deep_research/rank.py, deep-research/tests/test_rank.py
- Context paths:
  - docs/loom/specs/2026-06-02-deep-research-portable-python.md
- Acceptance:
  - RED: `test_rank::test_quorum_rule` fails — 3 valid/0 refuted → survives; 1 refuted/2 valid → survives; 2 refuted → killed; 1 valid only (2 abstain) → killed (unadjudicated); ranking puts central+primary first
  - GREEN: pytest test_rank passes
- External surfaces: none
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "quorum rule valid>=2 && refuted<2 ... abstain handling" (Reverse / Error)

## Task 6 — providers.py (Protocols)
- Description: Define `LLMProvider` (async `complete(prompt, schema) -> dict | None`),
  `SearchProvider` (async `search(query) -> list[dict]`), `FetchProvider`
  (async `fetch(url) -> str | None`) as `runtime_checkable typing.Protocol`s
  with docstrings documenting the structured-output + null-on-skip contract.
- Module: deep_research.providers
- Files touched: deep-research/src/deep_research/providers.py, deep-research/tests/test_providers.py
- Context paths:
  - docs/loom/specs/2026-06-02-deep-research-portable-python.md
- Acceptance:
  - RED: `test_providers::test_mock_conforms` fails — a mock class with the 3 async methods passes `isinstance(mock, LLMProvider)` (runtime_checkable)
  - GREEN: pytest test_providers passes
- External surfaces: none (typing.Protocol)
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "injectable LLMProvider / SearchProvider / FetchProvider Protocols" (Smallest End State)

## Task 7 — pipeline.py (asyncio helper)
- Description: Implement two small async helpers replicating the Workflow
  engine primitives: `gather_bounded(thunks, concurrency)` (parallel with a
  `Semaphore`, None-on-error → drop) and `pipeline(items, *stages, concurrency)`
  (per-item streaming through stages, no inter-stage barrier). Pure asyncio.
- Module: deep_research.pipeline
- Files touched: deep-research/src/deep_research/pipeline.py, deep-research/tests/test_pipeline.py
- Context paths:
  - docs/loom/specs/2026-06-02-deep-research-portable-python.md
- Acceptance:
  - RED: `test_pipeline::test_gather_and_pipeline` fails — `gather_bounded` runs N coros under a concurrency cap and drops the one that raises; `pipeline` streams each item through 2 stages and returns per-item results
  - GREEN: pytest test_pipeline passes
- External surfaces: none (asyncio stdlib)
- Dependencies: Task 1 completes first
- Independent: true
- Brief item covered: "in-process asyncio orchestration" / "replace only the orchestration shell (CC Workflow → asyncio)" (Smallest End State / Decision)

## Task 8 — core.py happy-path (L1 core wiring)
- Description: Implement `async deep_research(question, llm, search, fetch, *,
  concurrency=8)` sequencing scope → parallel search → dedup → parallel
  fetch+extract → rank → 3-vote verify → synthesize, using the T7 helper and
  the pure modules. Replicate the no-barrier search→fetch streaming and the
  verify barrier. Happy path only (≥1 confirmed claim → full Report); the
  degradation/fallback branches are Task 10.
- Module: deep_research.core
- Files touched: deep-research/src/deep_research/core.py, deep-research/tests/test_core.py
- Context paths:
  - deep-research/src/deep_research/schemas.py
  - deep-research/src/deep_research/prompts.py
  - deep-research/src/deep_research/dedup.py
  - deep-research/src/deep_research/rank.py
  - deep-research/src/deep_research/providers.py
  - deep-research/src/deep_research/pipeline.py
- Acceptance:
  - RED: `test_core::test_end_to_end_mocked` fails — with scripted mock llm/search/fetch (all returning well-formed data, ≥1 surviving claim), the run decomposes angles, dedups sources, extracts+ranks claims, runs 3-vote verify, and returns a Report whose `findings` reflect quorum-survivors and `refuted` reflects killed claims; `stats` counts agree
  - GREEN: pytest test_core passes
- External surfaces: none (asyncio; providers injected as mocks)
- Dependencies: Tasks 2, 3, 4, 5, 6, 7 complete first
- Independent: false
- Brief item covered: "L1 — core: in-process asyncio orchestration ... provider-agnostic; unit-tested with mock adapters" (Smallest End State)

## Task 9 — adapters.py (reference providers — L2 capability)
- Description: Implement concrete adapters conforming to the Protocols:
  `AnthropicLLM` (Anthropic Messages API, tool-forced structured output),
  `BraveSearch` (Brave Search API), `HttpxFetch` (httpx GET + basic text
  extraction). Each reads its key from env. HTTP is mocked in tests.
- Module: deep_research.adapters
- Files touched: deep-research/src/deep_research/adapters.py, deep-research/tests/test_adapters.py
- Context paths:
  - deep-research/src/deep_research/providers.py
- Acceptance:
  - RED: `test_adapters::test_adapters_conform` fails — with mocked HTTP clients, each adapter satisfies its Protocol and maps a canned API response to the expected dict/str shape; missing-key raises a clear error
  - GREEN: pytest test_adapters passes
- External surfaces: third-party — `anthropic` SDK, `httpx` (mocked in tests); Brave/Anthropic REST APIs
- Dependencies: Task 6 completes first
- Independent: true
- Brief item covered: "capability self-contained: adapters hold their own API keys" + Axis-4 Brave/Anthropic reco (Decision / Alternatives)

## Task 10 — core.py degradation paths
- Description: Add the graceful-degradation branches to `deep_research`:
  0 claims extracted → summary Report with empty findings + stats; all claims
  refuted → "inconclusive" Report listing refuted; synthesis returns None →
  salvage confirmed claims unmerged. Mirror the original's fallback return
  shapes. Edits core.py (after T8 establishes the happy path).
- Module: deep_research.core
- Files touched: deep-research/src/deep_research/core.py, deep-research/tests/test_core_degradation.py
- Context paths:
  - deep-research/src/deep_research/core.py
  - docs/loom/specs/2026-06-02-deep-research-portable-python.md
- Acceptance:
  - RED: `test_core_degradation::test_fallback_shapes` fails — mock providers driving each of the 3 paths (no claims / all refuted / synthesis None) return the documented salvage Report shape with correct stats, never raising
  - GREEN: pytest test_core_degradation passes
- External surfaces: none
- Dependencies: Task 8 completes first
- Independent: false
- Brief item covered: "replicate all graceful-degradation fallbacks (0 claims / all-refuted / synthesis fail)" (Smallest End State / Error)

## Task 11 — cli.py (L2 entry point)
- Description: Implement `deep-research "<question>" [--json|--markdown]
  [--max-fetch N]` (argparse) that builds the adapter set from env and runs
  `core.deep_research`, printing JSON or rendered markdown. Register console
  script in pyproject.
- Module: deep_research.cli
- Files touched: deep-research/src/deep_research/cli.py, deep-research/tests/test_cli.py
- Context paths:
  - deep-research/src/deep_research/core.py
  - deep-research/src/deep_research/adapters.py
- Acceptance:
  - RED: `test_cli::test_cli_smoke` fails — invoking the CLI entry with a monkeypatched `core.deep_research` (returns a canned Report) and `--json` prints valid JSON to stdout and exits 0; no-question exits non-zero with a usage message
  - GREEN: pytest test_cli passes
- External surfaces: CLI entry point (console_scripts)
- Dependencies: Tasks 8, 9 complete first
- Independent: true
- Brief item covered: "L2 — CLI: deep-research \"<question>\" wrapping L1" (Smallest End State)

## Task 12 — mcp_server.py (L3 entry point)
- Description: Implement an MCP server (stdio) exposing one `deep_research`
  tool whose handler builds adapters from env and calls `core.deep_research`,
  returning the report as structured content. Gate behind the `mcp` optional
  dependency group.
- Module: deep_research.mcp_server
- Files touched: deep-research/src/deep_research/mcp_server.py, deep-research/tests/test_mcp_server.py
- Context paths:
  - deep-research/src/deep_research/core.py
  - deep-research/src/deep_research/adapters.py
- Acceptance:
  - RED: `test_mcp_server::test_tool_registered` fails — the server lists a `deep_research` tool with name+description+input schema; calling the handler with a monkeypatched `core.deep_research` returns the canned report
  - GREEN: pytest test_mcp_server passes
- External surfaces: third-party — `mcp` Python SDK (stdio server); skipped if `mcp` extra absent
- Dependencies: Tasks 8, 9 complete first
- Independent: true
- Brief item covered: "L3 — MCP server: exposes a deep_research tool over MCP" (Smallest End State)

## Notes

- Critical-path depth = 4. Longest chains: T1→T2→T8→T11 and T1→T6→T9→T11 and
  T1→T2→T8→T10 — all depth 4. T10/T11/T12 sit at the same level off T8 (+T9);
  T10 is `Independent: false` (edits core.py that T8 owns — sequential after
  T8, and would share core.py with no other parallel task). T11/T12 are
  `Independent: true` with disjoint files (cli.py / mcp_server.py).
- Parallel waves: L1 = {T2,T3,T4,T5,T6,T7} after T1; L2 = {T8, T9}
  (disjoint, T9 needs only T6 so may start during L1); L3 = {T10, T11, T12}.
- L1 portability line reached when T8 + T10 are GREEN (core complete incl.
  fallbacks). L2/L3 are additive.
- Provider choice (Brave/Anthropic) confined to T9/T11; core (T7/T8/T10)
  stays provider-agnostic per the brief's Boundary evidence.
- Check-14 disjointness (Independent:true tasks T2,3,4,5,6,7,9,11,12): all
  file sets pairwise disjoint (distinct module + distinct test file each).
