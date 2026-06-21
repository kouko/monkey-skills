# Plan: fact-check skill (research-toolkit)

Source brief: docs/loom/specs/2026-06-03-research-toolkit-fact-check.md
Total tasks: 7 (incl. the shared reuse foundation F0a/F0b, built once for the batch)
Critical-path depth: 4 (F0a → F2 → F3 → F4 ; verified)
Execution order: parallel-where-possible (interleaves with the cite-check plan — disjoint skill dirs)
Plan-document-reviewer verdict: PASS (2026-06-03, round 2 — F0 split into F0a/F0b per Check-4; depth still 4)

Reuse model (decision A — locked 2026-06-03): deep-research = SSOT. Sibling
skills functional-COPY the reusable primitives **byte-identical** into their own
`scripts/` (new skill-specific logic goes in NEW files that flat-import the
copies). A repo-level MD5 drift-check (extending `.github/workflows/check-script-sync.yml`
with a research-toolkit group) + a `research-toolkit/scripts/sync-primitives.sh`
copier guard byte-identity, mirroring the existing investing-toolkit MD5-sync
pattern. F0 builds this shared foundation once (the cite-check plan reuses it).

Resolved brief OQs: OQ1 keep a minimal Stage-A evidence gather (≤6 sources,
shared pool) ; OQ2 `inconclusive` = all-abstain OR <2 valid votes OR zero
evidence found ; OQ3 functional-copy + sync (A) ; OQ4 keep VOTES_PER_CLAIM=3.

Copied primitives (byte-identical from research-toolkit/skills/deep-research/scripts/):
`schemas.py`, `rank.py`, `prompts.py`, `dedup.py`. New file: `factcheck.py`.

---

## Task F0a — Shared sync copier script
- Description: Create `research-toolkit/scripts/sync-primitives.sh` — copies
  `research-toolkit/skills/deep-research/scripts/{schemas,rank,prompts,dedup}.py`
  into a sibling skill's `scripts/` dir (arg: target skill name(s); idempotent
  cp; mkdir -p the target). Mirror `investing-toolkit/scripts/sync-clients.sh`.
- Module: research-toolkit/scripts (shared copier)
- Files touched: research-toolkit/scripts/sync-primitives.sh
- Context paths:
  - investing-toolkit/scripts/sync-clients.sh
  - research-toolkit/skills/deep-research/scripts/
- Acceptance:
  - RED: `test -f research-toolkit/scripts/sync-primitives.sh` fails (absent)
  - GREEN: exists + executable (`test -x`); running `bash research-toolkit/scripts/sync-primitives.sh fact-check` (after F1 scaffold) places the 4 primitives into fact-check/scripts byte-identical to SSOT (`md5` equal each)
- External surfaces: shell (bash, cp, md5)
- Dependencies: none
- Independent: true   # disjoint files vs F0b, F1
- Brief item covered: "functional-copy ... (decision A)" (Decision)

## Task F0b — research-toolkit MD5 drift CI group
- Description: Extend `.github/workflows/check-script-sync.yml` with a
  research-toolkit group: reference = deep-research's 4 primitives, copies = the
  same 4 filenames under `fact-check/scripts/` AND `cite-check/scripts/` (reuse
  the existing `check_group`, which auto-`[skip]`s missing copies). Update the
  "Fix locally" hint to mention `research-toolkit/scripts/sync-primitives.sh`.
- Module: .github/workflows/check-script-sync.yml (CI)
- Files touched: .github/workflows/check-script-sync.yml
- Context paths:
  - .github/workflows/check-script-sync.yml
- Acceptance:
  - RED: `grep -c "research-toolkit" .github/workflows/check-script-sync.yml` == 0
  - GREEN: yml parses (py-yaml load); the new group references the 4 deep-research primitives + both siblings' copies; running the embedded check prints `[skip]`/`[ok]` (not `[FAIL]`) for the research-toolkit group given current copies
- External surfaces: GitHub Actions workflow schema
- Dependencies: none
- Independent: true   # disjoint files vs F0a, F1
- Brief item covered: "an MD5/drift sync check (decision A)" (Decision)

## Task F1 — fact-check scaffold
- Description: Create `research-toolkit/skills/fact-check/SKILL.md` (valid
  frontmatter only: name fact-check, description, version 0.1.0; one-line body
  placeholder) + `research-toolkit/skills/fact-check/scripts/pytest.ini`
  (`[pytest]` with `pythonpath = .` and `cache_dir = /tmp/pytest_cache_fact_check`).
- Module: research-toolkit/skills/fact-check (packaging)
- Files touched: research-toolkit/skills/fact-check/SKILL.md, research-toolkit/skills/fact-check/scripts/pytest.ini
- Context paths:
  - research-toolkit/skills/deep-research/SKILL.md
  - research-toolkit/skills/deep-research/scripts/pytest.ini
- Acceptance:
  - RED: `test -f research-toolkit/skills/fact-check/SKILL.md` fails
  - GREEN: both files exist; frontmatter parses (name/description/version); `find research-toolkit/skills/fact-check -mindepth 2 -type d` empty; cache_dir is /tmp path
- External surfaces: none
- Dependencies: none
- Independent: true   # vs cite-check's C1 (disjoint dir)
- Brief item covered: "a research-toolkit/skills/fact-check/ skill (SKILL.md + minimal scripts/)" (Smallest End State)

## Task F2 — Copy primitives into fact-check/scripts (via sync)
- Description: Run `research-toolkit/scripts/sync-primitives.sh fact-check` to
  place byte-identical copies of `schemas.py`, `rank.py`, `prompts.py`,
  `dedup.py` into `research-toolkit/skills/fact-check/scripts/`. Add a
  `test_primitives_present.py` asserting each imports + a provenance note. Do NOT
  copy the deep-research test files (the sync check covers the source files; the
  primitives' own tests already run in deep-research).
- Module: research-toolkit/skills/fact-check/scripts (copied primitives)
- Files touched: research-toolkit/skills/fact-check/scripts/{schemas,rank,prompts,dedup}.py, research-toolkit/skills/fact-check/scripts/test_primitives_present.py
- Context paths:
  - research-toolkit/skills/deep-research/scripts/{schemas,rank,prompts,dedup}.py
  - research-toolkit/scripts/sync-primitives.sh
- Acceptance:
  - RED: `cd research-toolkit/skills/fact-check/scripts && PYTHONDONTWRITEBYTECODE=1 python3 -m pytest test_primitives_present.py` fails (no modules)
  - GREEN: pytest passes (imports `schemas`,`rank`,`prompts`,`dedup`); `md5` of each copy equals the deep-research SSOT; the F0 CI group reports `[ok]` for fact-check's 4 copies
- External surfaces: none (stdlib)
- Dependencies: Tasks F0a, F1 complete first
- Independent: false
- Brief item covered: "reused scripts are functional-copied into fact-check's scripts/" (Decision)

## Task F3 — factcheck.py: verdict mapper + CLI
- Description: New flat module `research-toolkit/skills/fact-check/scripts/factcheck.py`
  with `classify_verdict(verdicts) -> {verdict, confidence, refuted_count, valid_count}`
  mapping `quorum_survives` + vote distribution to the 3-way taxonomy:
  `supported` (survives quorum), `refuted` (≥REFUTATIONS_REQUIRED refute),
  `inconclusive` (all-abstain OR <2 valid OR empty input / no evidence). Imports
  `quorum_survives`, `REFUTATIONS_REQUIRED`, `VOTES_PER_CLAIM` from the copied
  `rank`/`schemas`. Add `__main__`: `factcheck.py verdict` (stdin verdicts JSON →
  stdout verdict object). RED test first (`test_factcheck.py`).
- Module: research-toolkit/skills/fact-check/scripts/factcheck.py
- Files touched: research-toolkit/skills/fact-check/scripts/factcheck.py, research-toolkit/skills/fact-check/scripts/test_factcheck.py
- Context paths:
  - research-toolkit/skills/fact-check/scripts/rank.py (copied; quorum_survives)
  - research-toolkit/skills/fact-check/scripts/schemas.py (copied; constants)
- Acceptance:
  - RED: `pytest test_factcheck.py` (in scripts/) fails (no module)
  - GREEN: pytest passes covering: 3 valid+0 refute → supported; 2 refute → refuted; all-abstain (`[null,null,null]`) → inconclusive; `[]` (no evidence) → inconclusive; `echo '[null,null,null]' | python3 factcheck.py verdict` prints a JSON object with `"verdict":"inconclusive"`
- External surfaces: none (stdlib)
- Dependencies: Task F2 completes first (imports copied primitives)
- Independent: false
- Brief item covered: "Stage C — Verdict: map to supported/refuted/inconclusive" (Smallest End State)

## Task F4 — fact-check SKILL.md body
- Description: Author the SKILL.md body: the executor model (agent supplies LLM +
  WebSearch + WebFetch; scripts = deterministic logic; NO API key), then the
  3-stage flow — Stage A Gather evidence (1-2 WebSearch queries confirming +
  disconfirming → `dedup.py` small budget ≤6 → per-source WebFetch + extract a
  quote via `prompts.py fetch` + `schemas.py extract`), Stage B Verify (3 voters
  via `prompts.py verify` + `schemas.py verdict`), Stage C Verdict
  (`factcheck.py verdict`). State that it reuses deep-research primitives and is a
  lightweight point-check vs deep-research's breadth. ≤6000-token body.
- Module: research-toolkit/skills/fact-check/SKILL.md
- Files touched: research-toolkit/skills/fact-check/SKILL.md
- Context paths:
  - docs/loom/specs/2026-06-03-research-toolkit-fact-check.md
  - research-toolkit/skills/deep-research/SKILL.md
  - research-toolkit/skills/fact-check/scripts/factcheck.py
- Acceptance:
  - RED: `grep -ci "verdict" research-toolkit/skills/fact-check/SKILL.md` near 0 (placeholder)
  - GREEN: body names Stages A/B/C with their `prompts.py`/`schemas.py`/`dedup.py`/`factcheck.py` invocations + the 3-way verdict; states "no API key"; body ≤6000 tokens; frontmatter intact; folder-structure hook clean
- External surfaces: none (doc)
- Dependencies: Task F3 completes first
- Independent: false
- Brief item covered: "agent owns I/O + reasoning; 3-stage flow" (Smallest End State)
