# Plan: cite-check skill (research-toolkit)

Source brief: docs/code-toolkit/specs/2026-06-03-research-toolkit-cite-check.md
Total tasks: 6
Critical-path depth: 4 (C1 → C4 → C5 → C6 ; verified — round 2 dropped C4's dep on C2 since citecheck.py holds its OWN schemas and does not runtime-import the copied schemas.py, only references their shape)
Execution order: parallel-where-possible (interleaves with fact-check plan — disjoint skill dirs)
Plan-document-reviewer verdict: PASS (2026-06-03, round 2 — Check-11 cross-plan ref moved to Notes; depth shortened 5→4)

Reuse model: decision A (see the fact-check plan F0). The shared sync foundation
(sync-primitives.sh + the research-toolkit MD5 CI group) is built ONCE in
fact-check Task F0; this plan's copy task (C2) reuses it and C7-of-F0's CI group
already lists cite-check's copies (F0 enumerates both siblings).

Resolved brief OQs: OQ1 3-way verdict scale (supported/partial/unsupported) per
Scite + FACTUM ; OQ2 deterministic pre-extract + LLM bind ; OQ3 non-URL refs
flag-and-skip in v1 ; OQ4 single-voter support-verdict default (quorum opt-in) ;
OQ5 unsourced claims reported as a separate class, not hunted.

Copied primitives (byte-identical from deep-research): `prompts.py`, `schemas.py`,
`rank.py`, `dedup.py`. New files: `parse_doc.py`, `citecheck.py` (+ new prompts/
schemas live inside citecheck.py to keep the copied prompts.py byte-identical).

---

## Task C1 — cite-check scaffold
- Description: Create `research-toolkit/skills/cite-check/SKILL.md` (valid
  frontmatter only: name cite-check, description, version 0.1.0; one-line body
  placeholder) + `research-toolkit/skills/cite-check/scripts/pytest.ini`
  (`pythonpath = .`, `cache_dir = /tmp/pytest_cache_cite_check`).
- Module: research-toolkit/skills/cite-check (packaging)
- Files touched: research-toolkit/skills/cite-check/SKILL.md, research-toolkit/skills/cite-check/scripts/pytest.ini
- Context paths:
  - research-toolkit/skills/deep-research/SKILL.md
  - research-toolkit/skills/deep-research/scripts/pytest.ini
- Acceptance:
  - RED: `test -f research-toolkit/skills/cite-check/SKILL.md` fails
  - GREEN: both files exist; frontmatter parses; `find research-toolkit/skills/cite-check -mindepth 2 -type d` empty; cache_dir is /tmp path
- External surfaces: none
- Dependencies: none
- Independent: true   # vs fact-check F1 (disjoint dir)
- Brief item covered: "a research-toolkit/skills/cite-check/ skill" (Smallest End State)

## Task C2 — Copy primitives into cite-check/scripts (via sync)
- Description: Run `research-toolkit/scripts/sync-primitives.sh cite-check` to
  place byte-identical `prompts.py`, `schemas.py`, `rank.py`, `dedup.py` into
  `research-toolkit/skills/cite-check/scripts/`. Add `test_primitives_present.py`
  asserting each imports.
- Module: research-toolkit/skills/cite-check/scripts (copied primitives)
- Files touched: research-toolkit/skills/cite-check/scripts/{prompts,schemas,rank,dedup}.py, research-toolkit/skills/cite-check/scripts/test_primitives_present.py
- Context paths:
  - research-toolkit/skills/deep-research/scripts/{prompts,schemas,rank,dedup}.py
  - research-toolkit/scripts/sync-primitives.sh
- Acceptance:
  - RED: `cd research-toolkit/skills/cite-check/scripts && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest test_primitives_present.py` fails
  - GREEN: pytest passes; md5 of each copy equals deep-research SSOT; F0 CI group reports `[ok]` for cite-check's copies
- External surfaces: none (stdlib)
- Dependencies: Task C1 completes first   # cross-plan prereq (fact-check F0a sync script) tracked in §Notes, not here
- Independent: true   # parallel wave after C1 (disjoint files vs C3/C4)
- Brief item covered: "Reuse fetch/extract + verify + quorum + dedup" (Smallest End State)

## Task C3 — parse_doc.py: deterministic (claim, cited-URL) pre-extractor
- Description: New flat module `research-toolkit/skills/cite-check/scripts/parse_doc.py`
  — deterministic (regex/markdown) pre-extraction of citation structure from a
  markdown doc: inline links `[text](url)`, footnote markers `[^n]`/`[n]` +
  reference-list resolution → list of `{citedUrl|citedRef, locator, anchorText}`.
  Also classify lines/claims with NO citation as `unsourced` (reported, not
  audited). Stdlib only (`re`, `urllib`). The LLM claim↔citation binding is NOT
  here (that's the SKILL.md's job using a prompt); this module is the
  deterministic scaffold the agent builds on. Add `__main__`: `parse_doc.py`
  (stdin markdown text → stdout JSON of citation anchors). RED test first.
- Module: research-toolkit/skills/cite-check/scripts/parse_doc.py
- Files touched: research-toolkit/skills/cite-check/scripts/parse_doc.py, research-toolkit/skills/cite-check/scripts/test_parse_doc.py
- Context paths:
  - docs/code-toolkit/specs/2026-06-03-research-toolkit-cite-check.md
- Acceptance:
  - RED: `pytest test_parse_doc.py` (in scripts/) fails (no module)
  - GREEN: pytest passes covering: inline link extracted with url+anchor; footnote `[^1]` resolved to its reference-list url; a paragraph with no link flagged unsourced; `echo '...md...' | python3 parse_doc.py` prints JSON anchors
- External surfaces: none (stdlib re/urllib)
- Dependencies: Task C1 completes first
- Independent: true   # disjoint from C2 (new file vs copied files); but see C4 dep
- Brief item covered: "Stage 1 — Parse (NEW): doc → (claim, cited-URL) pairs" (Smallest End State)

## Task C4 — cite-check schemas + support-verdict logic (citecheck.py)
- Description: New flat module `research-toolkit/skills/cite-check/scripts/citecheck.py`
  holding the cite-check-specific schemas + verdict logic (kept OUT of the copied
  `schemas.py`/`prompts.py` so those stay byte-identical for the sync check):
  `EXTRACT_CITED_CLAIMS` schema (binding output: `[{claim, citedUrl|citedRef,
  locator}]`), `SUPPORT_VERDICT` schema (3-way: `support ∈ supported|partial|
  unsupported`, + `misattributed`, `unresolvable` flags, `evidence`), and
  `classify_support(verdict_obj) -> normalized verdict`. Add `__main__`:
  `citecheck.py verdict` (stdin per-citation support objects → stdout audit
  summary counts). RED test first.
- Module: research-toolkit/skills/cite-check/scripts/citecheck.py
- Files touched: research-toolkit/skills/cite-check/scripts/citecheck.py, research-toolkit/skills/cite-check/scripts/test_citecheck.py
- Context paths:
  - research-toolkit/skills/cite-check/scripts/schemas.py (copied; VERDICT/EXTRACT for shape reference)
  - docs/code-toolkit/specs/2026-06-03-research-toolkit-cite-check.md
- Acceptance:
  - RED: `pytest test_citecheck.py` (in scripts/) fails (no module)
  - GREEN: pytest passes covering: SUPPORT_VERDICT enum has supported/partial/unsupported; a dead-link/`unresolvable` verdict counts separately; summary counts roll up correctly; `citecheck.py verdict` over stdin prints summary JSON
- External surfaces: none (stdlib)
- Dependencies: Task C1 completes first   # citecheck.py holds its OWN schemas; the copied schemas.py is referenced for shape only, NOT runtime-imported
- Independent: true   # parallel wave after C1 (disjoint files vs C2/C3)
- Brief item covered: "Stage 3 support-verdict 3-way + Stage 4 audit report" (Smallest End State)

## Task C5 — audit report renderer (in citecheck.py)
- Description: Add `render_audit(results) -> markdown` to citecheck.py: a
  per-citation verdict table (claim · cited source · verdict · note) + summary
  counts (supported / partial / unsupported / misattributed / unresolvable /
  unsourced). Add `citecheck.py report` subcommand (stdin results → stdout
  markdown). Extend test_citecheck.py (RED for the new function first).
- Module: research-toolkit/skills/cite-check/scripts/citecheck.py
- Files touched: research-toolkit/skills/cite-check/scripts/citecheck.py, research-toolkit/skills/cite-check/scripts/test_citecheck.py
- Context paths:
  - research-toolkit/skills/deep-research/scripts/synthesis.py (render pattern reference)
- Acceptance:
  - RED: new `test_render_audit` fails before implementation
  - GREEN: render emits a markdown table + the 6 summary counts; `citecheck.py report` prints markdown; full test_citecheck.py green
- External surfaces: none
- Dependencies: Task C4 completes first (same file)
- Independent: false
- Brief item covered: "Stage 4 — Audit report renderer" (Smallest End State)

## Task C6 — cite-check SKILL.md body
- Description: Author the SKILL.md body: executor model (agent supplies LLM +
  WebFetch; scripts = deterministic; NO API key), then the 4-stage flow — Stage 1
  Parse (`parse_doc.py` deterministic anchors → agent binds claims via an inline
  binding prompt conforming to `citecheck.py`'s EXTRACT_CITED_CLAIMS), Stage 2
  Fetch source (per cited URL: WebFetch + `prompts.py fetch`/`schemas.py extract`;
  dedup via `dedup.py`; dead → unresolvable), Stage 3 Support-verdict (per
  (claim,source) a support-focused check → 3-way via `citecheck.py`), Stage 4
  Audit report (`citecheck.py report`). Document correctness-only scope (not
  faithfulness), non-URL refs flag-skip, unsourced as a separate class. ≤6000-token body.
- Module: research-toolkit/skills/cite-check/SKILL.md
- Files touched: research-toolkit/skills/cite-check/SKILL.md
- Context paths:
  - docs/code-toolkit/specs/2026-06-03-research-toolkit-cite-check.md
  - research-toolkit/skills/cite-check/scripts/{parse_doc,citecheck}.py
  - research-toolkit/skills/deep-research/SKILL.md
- Acceptance:
  - RED: `grep -ci "audit" research-toolkit/skills/cite-check/SKILL.md` near 0 (placeholder)
  - GREEN: body names Stages 1-4 with `parse_doc.py`/`prompts.py fetch`/`schemas.py extract`/`citecheck.py` invocations + 3-way verdict + correctness-only scope note; states "no API key"; body ≤6000 tokens; frontmatter intact; folder hook clean
- External surfaces: none (doc)
- Dependencies: Tasks C2, C3, C5 complete first   # C2 = copies present (SKILL.md cites prompts.py/schemas.py); C3 = parse_doc; C5 = citecheck render
- Independent: false
- Brief item covered: "agent owns I/O + reasoning; 4-stage flow" (Smallest End State)

## Notes

- **Cross-plan prerequisite (Check-11 compliance)**: Task C2 (copy primitives
  via `sync-primitives.sh`) requires the shared sync foundation from the sibling
  **fact-check plan Task F0a** (`research-toolkit/scripts/sync-primitives.sh`)
  to land first, and the MD5 CI group from **F0b** enumerates cite-check's
  copies. This is a batch-level cross-plan ordering tracked here, NOT in C2's
  within-plan `Dependencies` field (which stays within-plan per plan-format).
  Practically: build F0a/F0b once before either skill's copy task.
- **Depth (round 2)**: dropping C4's dep on C2 (citecheck.py holds its own
  schemas, only references the copied shapes) shortens the critical path to
  C1→C4→C5→C6 = 4. C2/C3/C4 form a parallel wave after C1 (disjoint files).
