# Plan: deep-read skill (research-toolkit)

Source brief: docs/code-toolkit/specs/2026-06-03-research-toolkit-deep-read.md
Total tasks: 6
Critical-path depth: 4 (D1 → D2 → D5 → D6 ; verified)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-06-03, 14/14; advisory: D2 marked Independent for D2∥D4 wave)

Reuse model: decision A (deep-research = SSOT). deep-read functional-COPIES the
primitives it reuses (`schemas.py`, `prompts.py`, `dedup.py` for per-chunk
extraction + cross-chunk claim merge; `rank.py` copied too for set-uniformity
though deep-read does not import it) BYTE-IDENTICAL via the existing
`research-toolkit/scripts/sync-primitives.sh` (shipped in #370). New
skill-specific logic lives in NEW files (`chunk.py`, `deepread.py`); new schemas
/ prompts live inside `deepread.py` so the copied `schemas.py`/`prompts.py` stay
byte-identical for the MD5 drift check.

Resolved brief decisions (see brief Open Questions, all RESOLVED): NO adversarial
verify (single-source) ; stdlib heading/chapter chunker ; content-agnostic TEXT
core with ZERO format deps (agent's own Read/WebFetch ingests; book-extract /
defuddle are optional SKILL.md skill-composition pointers, NOT code deps) ; own
`READ_SCHEMA` ; no cross-plugin code dependency.

Notes:
- The shared sync foundation (`sync-primitives.sh` + the research-toolkit MD5 CI
  group in `.github/workflows/check-script-sync.yml`) already exists on main
  from #370. D2 reuses the copier; D3 only ADDS `deep-read` to the CI group's
  sibling list (the group's `check_group` auto-`[skip]`s missing copies).
- CLI contract (consumed by SKILL.md D6):
  - `chunk.py` (stdin: markdown text) → prints JSON array of `{heading, text, ordinal}` chunks
  - `deepread.py merge` (stdin: per-chunk extraction objects) → merged+deduped claims/sections JSON
  - `deepread.py report` (stdin: merged understanding) → markdown READ report
  - `deepread.py schema` is NOT provided — `READ_SCHEMA`/extraction-prompt are module dicts read from source (mirrors cite-check's EXTRACT_CITED_CLAIMS).

---

## Task D1 — deep-read scaffold
- Description: Create `research-toolkit/skills/deep-read/SKILL.md` (valid
  frontmatter only: name deep-read, description, version 0.1.0; one-line body
  placeholder `<!-- body authored in D6 -->`) + `research-toolkit/skills/deep-read/scripts/pytest.ini`
  (`[pytest]` with `pythonpath = .` and `cache_dir = /tmp/pytest_cache_deep_read`).
- Module: research-toolkit/skills/deep-read (packaging)
- Files touched: research-toolkit/skills/deep-read/SKILL.md, research-toolkit/skills/deep-read/scripts/pytest.ini
- Context paths:
  - research-toolkit/skills/cite-check/SKILL.md
  - research-toolkit/skills/cite-check/scripts/pytest.ini
- Acceptance:
  - RED: `test -f research-toolkit/skills/deep-read/SKILL.md` fails
  - GREEN: both files exist; frontmatter parses (name/description/version), and the description has NO colon-space `: ` inside an unquoted scalar (YAML safe_load succeeds); `find research-toolkit/skills/deep-read -mindepth 2 -type d` empty; cache_dir is /tmp path
- External surfaces: none
- Dependencies: none
- Independent: true   # disjoint from D3 (CI yml) and D4
- Brief item covered: "A research-toolkit/skills/deep-read/ skill" (Smallest End State)

## Task D2 — Copy primitives into deep-read/scripts (via sync)
- Description: Run `bash research-toolkit/scripts/sync-primitives.sh deep-read`
  to place byte-identical `schemas.py`, `rank.py`, `prompts.py`, `dedup.py` into
  `research-toolkit/skills/deep-read/scripts/`. Add `test_primitives_present.py`
  asserting each imports + sentinel symbols (`schemas.EXTRACT_SCHEMA`,
  `prompts.fetch_prompt`, `dedup.filter_novel`). Docstring: byte-identical
  functional copies of deep-research SSOT, guarded by CI MD5 sync — do NOT edit.
- Module: research-toolkit/skills/deep-read/scripts (copied primitives)
- Files touched: research-toolkit/skills/deep-read/scripts/{schemas,rank,prompts,dedup}.py, research-toolkit/skills/deep-read/scripts/test_primitives_present.py
- Context paths:
  - research-toolkit/skills/deep-research/scripts/{schemas,prompts,dedup}.py
  - research-toolkit/scripts/sync-primitives.sh
- Acceptance:
  - RED: `cd research-toolkit/skills/deep-read/scripts && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest test_primitives_present.py` fails (no modules)
  - GREEN: pytest passes; for f in schemas rank prompts dedup: `diff research-toolkit/skills/deep-research/scripts/$f.py research-toolkit/skills/deep-read/scripts/$f.py` empty
- External surfaces: none (stdlib)
- Dependencies: Task D1 completes first
- Independent: true   # D2∥D4 wave after D1 (disjoint files: copies vs chunk.py)
- Brief item covered: "reuse fetch_prompt + EXTRACT_SCHEMA + dedup (decision A)" (Smallest End State)

## Task D3 — Add deep-read to the MD5 drift CI group
- Description: Edit `.github/workflows/check-script-sync.yml` — add `deep-read`
  to the research-toolkit group's sibling list (alongside fact-check, cite-check)
  so deep-read's 4 copied primitives are MD5-checked against the deep-research
  SSOT. (One-line list edit; the existing `check_group` auto-`[skip]`s missing
  copies.)
- Module: .github/workflows/check-script-sync.yml (CI)
- Files touched: .github/workflows/check-script-sync.yml
- Context paths:
  - .github/workflows/check-script-sync.yml
- Acceptance:
  - RED: `grep -c "deep-read" .github/workflows/check-script-sync.yml` == 0
  - GREEN: `deep-read` appears in the research-toolkit sibling list; yml parses (py-yaml safe_load); the existing fact-check/cite-check groups are byte-unchanged; embedded check prints `[ok]`/`[skip]` (not `[FAIL]`) for deep-read given current copies
- External surfaces: GitHub Actions workflow schema
- Dependencies: none
- Independent: true   # disjoint file from D1/D4
- Brief item covered: "decision A … MD5 drift check" (Decision)

## Task D4 — chunk.py: stdlib heading/chapter chunker
- Description: New flat module `research-toolkit/skills/deep-read/scripts/chunk.py`
  — split a markdown document into ordered chunks on its headings (stdlib `re`
  only). Each chunk = `{heading, text, ordinal}` (heading = the `#`-line that
  starts the chunk, or `""` for a preamble before the first heading; text = the
  body up to the next heading of the same-or-higher level; ordinal = 0-based
  index). Long heading-less docs → a single chunk (or size-based fallback split).
  Add `__main__`: `chunk.py` reads markdown from stdin → prints the JSON chunk
  array. RED test first.
- Module: research-toolkit/skills/deep-read/scripts/chunk.py
- Files touched: research-toolkit/skills/deep-read/scripts/chunk.py, research-toolkit/skills/deep-read/scripts/test_chunk.py
- Context paths:
  - docs/code-toolkit/specs/2026-06-03-research-toolkit-deep-read.md
- Acceptance:
  - RED: `pytest test_chunk.py` (in scripts/) fails (no module)
  - GREEN: pytest passes covering: a 3-heading doc → 3 chunks with headings + ordinals; preamble-before-first-heading → its own chunk with heading ""; a heading-less doc → 1 chunk; `printf '# A\\nx\\n## B\\ny\\n' | python3 chunk.py` prints 2+ chunks in order
- External surfaces: none (stdlib re)
- Dependencies: Task D1 completes first
- Independent: true   # parallel wave after D1 (disjoint file vs D2)
- Brief item covered: "Chunk: heading/chapter-aware" (Smallest End State)

## Task D5 — deepread.py: READ_SCHEMA + cross-chunk merge + report renderer
- Description: New flat module `research-toolkit/skills/deep-read/scripts/deepread.py`
  holding deep-read-specific logic (new schemas kept OUT of copied schemas.py):
  - `READ_SCHEMA` (JSON Schema dict): the final structured understanding —
    `{sourceQuality, sections[], claims[] (each {claim, quote, importance,
    section}), methodology, caveats, openQuestions, argumentStructure}`.
  - `CHUNK_EXTRACT_SCHEMA` (JSON Schema dict): the per-chunk extraction shape the
    agent emits (richer than EXTRACT_SCHEMA — adds section role / methodology /
    caveats per chunk).
  - `merge_chunks(chunk_extractions) -> dict`: flatten + dedup claims across
    chunks (reuse the copied `dedup` normalization where applicable), assemble
    the sections list in chunk order, collect methodology/caveats/openQuestions.
  - `render_report(understanding) -> str`: markdown READ report (sections
    outline + claims-with-quotes table + methodology/caveats/open-questions).
  - `__main__`: `deepread.py merge` (stdin chunk extractions → merged JSON) and
    `deepread.py report` (stdin merged understanding → markdown); unknown
    subcommand → stderr + exit 1.
  RED test first (`test_deepread.py`).
- Module: research-toolkit/skills/deep-read/scripts/deepread.py
- Files touched: research-toolkit/skills/deep-read/scripts/deepread.py, research-toolkit/skills/deep-read/scripts/test_deepread.py
- Context paths:
  - research-toolkit/skills/deep-read/scripts/dedup.py (copied; claim-merge reuse)
  - research-toolkit/skills/cite-check/scripts/citecheck.py (sibling pattern: own schemas + classify + render)
  - research-toolkit/skills/deep-research/scripts/synthesis.py (render pattern reference)
- Acceptance:
  - RED: `pytest test_deepread.py` (in scripts/) fails (no module)
  - GREEN: pytest passes covering: READ_SCHEMA has the 7 named fields; `merge_chunks` dedups a claim repeated across 2 chunks into one + preserves section order; `render_report` emits a sections outline + a claims table + methodology/caveats; `echo '<merged understanding JSON>' | python3 deepread.py report` prints markdown; unknown subcommand fails loud
- External surfaces: none (stdlib)
- Dependencies: Task D2 completes first (reuses copied dedup at runtime)
- Independent: false
- Brief item covered: "Hierarchical synthesis (the real new logic) + render report" (Smallest End State)

## Task D6 — deep-read SKILL.md body
- Description: Author the SKILL.md body (preserve frontmatter, replace the
  placeholder): (1) executor model — agent supplies LLM reasoning + its own
  read-capability; scripts = deterministic logic; NO API key; depth-on-ONE-source
  vs deep-research's breadth. (2) Ingest — get the document as TEXT by whatever
  the host can: `Read` a .md/.txt/PDF; `WebFetch` (or `obsidian:defuddle`) a URL;
  `tsundoku:book-extract` an EPUB → chapter markdown. State these are optional
  composition pointers, deep-read itself only needs text. (3) Chunk — `chunk.py`
  (or one-file-per-chapter from book-extract). (4) Per-chunk extract — FAN OUT
  one subagent per chunk (portable "dispatch N subagents", NOT the CC Workflow
  tool); each emits a chunk extraction conforming to `deepread.py`'s
  CHUNK_EXTRACT_SCHEMA, reusing `prompts.py fetch` framing + `schemas.py extract`
  fields. (5) Hierarchical synthesis — `deepread.py merge` to dedup/assemble. (6)
  Render — `deepread.py report`. State explicitly: NO adversarial verify (single
  source); grounding is per-claim quotes. Boundary note vs tsundoku:book-distill
  (skills, not understanding) + wiki-ingest (vault). Body ≤6000 tokens.
- Module: research-toolkit/skills/deep-read/SKILL.md
- Files touched: research-toolkit/skills/deep-read/SKILL.md
- Context paths:
  - docs/code-toolkit/specs/2026-06-03-research-toolkit-deep-read.md
  - research-toolkit/skills/deep-read/scripts/{chunk,deepread}.py
  - research-toolkit/skills/deep-research/SKILL.md
- Acceptance:
  - RED: `grep -ci "chunk" research-toolkit/skills/deep-read/SKILL.md` near 0 (placeholder)
  - GREEN: body names the ingest (text-via-agent-read) + chunk (`chunk.py`) + per-chunk extract (fan-out + `deepread.py` CHUNK_EXTRACT_SCHEMA) + merge (`deepread.py merge`) + render (`deepread.py report`) steps with accurate CLI invocations; states "no API key" AND "no adversarial verify"; describes fan-out abstractly (not CC Workflow); body ≤6000 tokens; frontmatter intact; folder-structure hook clean
- External surfaces: none (doc)
- Dependencies: Tasks D4, D5 complete first
- Independent: false
- Brief item covered: "agent owns I/O + reasoning; ingest→chunk→extract→synthesis→render" (Smallest End State)
