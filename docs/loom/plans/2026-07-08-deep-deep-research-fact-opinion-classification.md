# Plan: deep-deep-research fact/opinion classification

Source brief: docs/loom/specs/2026-07-08-deep-deep-research-fact-opinion-classification.md
Total tasks: 7
Critical-path depth: 4 (Task 1 → {Task 2, Task 3} → {Task 4, Task 5} → {Task 6, Task 7})
Execution order: parallel-where-possible. Task 1 is solo (no sibling at
  its level, Independent: false). Tasks 2/3 and 6/7 are each a genuine
  same-level sibling pair — disjoint Files touched, no dependency
  BETWEEN the two tasks in the pair (each depends only on an earlier
  level) — so each pair is marked Independent: true, per
  writing-plans/SKILL.md's rule that the Independent: true constraint is
  pairwise between co-marked tasks (no shared symbol, no sequential
  dependency between tasks that are BOTH marked true), not a ban on
  depending on an earlier, differently-marked task. Task 4 shares
  `prompts.py` with Task 3 and depends on it directly, so it is NOT
  independent of anything (Independent: false); Task 5 has no valid
  disjoint partner either (its would-be pairing with Task 4 collided on
  files once Task 4's real dependency was traced) but is itself
  Independent: true as a solo task, same as Task 1.
Plan-document-reviewer verdict: PASS (2026-07-08, round 4)

## Task 1 — claimType + heldBy on EXTRACT_SCHEMA
- Description: Add `claimType` (enum `["fact", "opinion"]`) and `heldBy`
  (optional string, global — not conditional on claimType) to
  `EXTRACT_SCHEMA`'s per-claim item shape in `schemas.py`. Add matching
  `claim_type: str = "fact"` and `held_by: Optional[str] = None` fields
  to the `ExtractedClaim` dataclass. `claimType` is NOT in the schema's
  `required` list (backward-compat: an extraction response that omits
  it must not fail validation) — code consuming a parsed claim treats a
  missing/unrecognized `claimType` as `"fact"`.
- Module: research-toolkit/skills/deep-deep-research/scripts/schemas.py
- Files touched: research-toolkit/skills/deep-deep-research/scripts/schemas.py,
  research-toolkit/skills/deep-deep-research/scripts/test_schemas.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/schemas.py (EXTRACT_SCHEMA lines 71-91, ExtractedClaim lines 157-164)
- Acceptance:
  - RED: test_schemas.py::test_extract_schema_supports_claim_type_and_held_by
    fails (claimType/heldBy absent from EXTRACT_SCHEMA properties;
    ExtractedClaim has no claim_type/held_by attrs)
  - GREEN: EXTRACT_SCHEMA's claims-item properties include `claimType`
    (enum fact/opinion) and top-level-or-per-claim `heldBy` (string);
    `claimType` not in `required`; `ExtractedClaim(claim=..., quote=...,
    importance=...).claim_type == "fact"` and `.held_by is None` by
    default
- External surfaces: none
- Dependencies: none
- Independent: false
- Brief item covered: "EXTRACT_SCHEMA gains a claimType field... two
  values... heldBy is a global optional field, not conditional on
  claimType"

## Task 2 — ATTRIBUTION_VERDICT_SCHEMA for the opinion-routing check
- Description: Add a new, lightweight `ATTRIBUTION_VERDICT_SCHEMA` to
  `schemas.py` — `{attributionConfirmed: bool, evidence: str}`, required
  `["attributionConfirmed", "evidence"]`. This is deliberately smaller
  than `VERDICT_SCHEMA` (no `confidence`/`counterSource` — attribution
  confirmation is binary, not a strength-graded refutation). Add a
  matching `AttributionVerdict` dataclass (`attribution_confirmed: bool`,
  `evidence: str`). Register it in `SCHEMAS_BY_NAME` under
  `"attribution-verdict"`.
- Module: research-toolkit/skills/deep-deep-research/scripts/schemas.py
- Files touched: research-toolkit/skills/deep-deep-research/scripts/schemas.py,
  research-toolkit/skills/deep-deep-research/scripts/test_schemas.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/schemas.py (VERDICT_SCHEMA lines 93-102 as the sibling pattern to follow structurally, SCHEMAS_BY_NAME lines 129-135)
- Acceptance:
  - RED: test_schemas.py::test_attribution_verdict_schema fails
    (ATTRIBUTION_VERDICT_SCHEMA / AttributionVerdict undefined)
  - GREEN: `python schemas.py attribution-verdict` prints the schema;
    `AttributionVerdict(attribution_confirmed=True, evidence="...")`
    round-trips
- External surfaces: none
- Dependencies: Task 1 completes first (needs Task 1 done before
  starting, but has no dependency on Task 3, its same-level sibling —
  disjoint files from Task 3, so paired Independent: true with it)
- Independent: true
- Brief item covered: "opinion claims → new, narrower
  attribution-confirmation check... new lightweight verdict shape"

## Task 3 — fetch_prompt: classify + decompose instead of falsifiable-only filter
- Description: Rewrite `fetch_prompt` in `prompts.py` — replace the
  "Extract 2-5 FALSIFIABLE claims" instruction with one that: (a)
  classifies each extracted claim's `claimType` (fact/opinion), (b)
  instructs decomposing any source statement that mixes a factual
  component with an opinion component into TWO separate claim objects
  (one fact-tagged, one opinion-tagged) rather than one ambiguous claim,
  with an explicit fail-safe — a statement that cannot be cleanly
  decomposed stays a single `fact`-tagged claim, never `opinion`, (c)
  instructs capturing `heldBy` whenever a claim has a natural
  attributable source, for BOTH fact and opinion claims (not
  conditional). Do not change `search_prompt` / `scope_prompt` /
  `verify_prompt` / `synthesis_prompt` in this task.
- Module: research-toolkit/skills/deep-deep-research/scripts/prompts.py
- Files touched: research-toolkit/skills/deep-deep-research/scripts/prompts.py,
  research-toolkit/skills/deep-deep-research/scripts/test_prompts.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/prompts.py (fetch_prompt lines 66-95)
  - research-toolkit/skills/deep-deep-research/scripts/schemas.py (claimType/heldBy from Task 1, for field-name consistency)
- Acceptance:
  - RED: test_prompts.py::test_fetch_prompt_instructs_claim_type_classification_and_decomposition
    fails (prompt text still says "FALSIFIABLE claims" with no
    claimType/decomposition/heldBy instruction)
  - GREEN: `fetch_prompt(...)` output contains instructions to tag
    `claimType`, to decompose mixed fact+opinion statements into
    separate claims with a fact fail-safe, and to capture `heldBy` for
    any claim with a natural attributable source (fact or opinion)
- External surfaces: none
- Dependencies: Task 1 completes first (needs Task 1 done before
  starting, but has no dependency on Task 2, its same-level sibling —
  disjoint files from Task 2, so paired Independent: true with it)
- Independent: true
- Brief item covered: "fetch_prompt (Stage 3) stops filtering to
  falsifiable-only... decompose any source statement that mixes a
  factual component with an opinion component into two separate claim
  objects"

## Task 4 — new attribution_prompt() builder for opinion-routed claims
- Description: Add a new prompt-builder function `attribution_prompt(claim,
  question)` to `prompts.py`, modeled structurally on `verify_prompt`
  but asking a narrower question: does the cited source actually
  hold/express this view, per the quote? (NOT "try to refute" — no
  adversarial-refutation framing, no counter-evidence WebSearch
  instruction.) Emits a verdict conforming to `ATTRIBUTION_VERDICT_SCHEMA`
  (Task 2). Add a corresponding `attribution` CLI subcommand in
  `prompts.py`'s `_main()`, mirroring the existing `verify` subcommand's
  argument shape (`--claim`, `--question`; no `--voter-idx`, since
  attribution-confirmation is a single check, not a 3-vote quorum).
- Module: research-toolkit/skills/deep-deep-research/scripts/prompts.py
- Files touched: research-toolkit/skills/deep-deep-research/scripts/prompts.py,
  research-toolkit/skills/deep-deep-research/scripts/test_prompts.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/prompts.py (verify_prompt lines 98-135, as the sibling pattern; _main() lines 172-221)
  - research-toolkit/skills/deep-deep-research/scripts/schemas.py (ATTRIBUTION_VERDICT_SCHEMA from Task 2)
- Acceptance:
  - RED: test_prompts.py::test_attribution_prompt_asks_whether_source_holds_view
    fails (attribution_prompt undefined)
  - GREEN: `attribution_prompt(claim={...}, question="...")` returns a
    prompt string asking whether the source expressed the claimed view
    (not asking to refute it); `python prompts.py attribution --claim
    '<JSON>' --question "<q>"` prints it
- External surfaces: none
- Dependencies: Tasks 2, 3 complete first — this shares `prompts.py`
  with Task 3 and depends on it directly, so it is NOT a same-level
  sibling of anything; Task 5 (which this was previously paired with)
  is a different level in practice (Task 5 only needs Task 2, so it can
  become ready before Task 3/Task 4 finish) — the two are not a valid
  disjointness pair once Task 3's file overlap is accounted for
- Independent: false
- Brief item covered: "opinion claims... get a narrower
  attribution-confirmation check instead — does the cited source
  actually hold/express this view, per the quote?"

## Task 5 — attribution_survives() decision function
- Description: Add an `attribution_survives(verdict: dict) -> bool`
  function to `rank.py`, structurally paralleling the existing `quorum`
  logic but for a SINGLE attribution verdict (no 3-vote quorum — an
  opinion claim gets one attribution-confirmation check, not adversarial
  voting). Returns `verdict.get("attributionConfirmed", False)`. Add a
  matching `attribution-check` CLI subcommand (stdin: one verdict JSON
  object → stdout: `true`/`false`), mirroring the existing `quorum`
  subcommand's stdin/stdout contract.
- Module: research-toolkit/skills/deep-deep-research/scripts/rank.py
- Files touched: research-toolkit/skills/deep-deep-research/scripts/rank.py,
  research-toolkit/skills/deep-deep-research/scripts/test_rank.py
- Context paths:
  - research-toolkit/skills/deep-deep-research/scripts/rank.py (existing `quorum` function/subcommand, for the sibling pattern)
  - research-toolkit/skills/deep-deep-research/scripts/schemas.py (ATTRIBUTION_VERDICT_SCHEMA from Task 2)
- Acceptance:
  - RED: test_rank.py::test_attribution_survives_reads_attribution_confirmed
    fails (attribution_survives undefined)
  - GREEN: `attribution_survives({"attributionConfirmed": True, ...}) ==
    True`; `attribution_survives({"attributionConfirmed": False, ...}) ==
    False`; `echo '{"attributionConfirmed": true, "evidence": "..."}' |
    python rank.py attribution-check` prints `true`
- External surfaces: none
- Dependencies: Task 2 completes first (needs the verdict schema shape;
  no sibling pairing needed — this is a solo Independent: true task,
  like Task 1, since Task 4 turned out to share files with Task 3
  rather than being a valid disjoint partner)
- Independent: true
- Brief item covered: "An attribution-confirmed opinion always survives
  to Stage 6"

## Task 6 — SKILL.md Stage 3/5 documentation update
- Description: Update `SKILL.md` Stage 3 (fetch + extract, lines
  314-354) to describe the claimType-classifying, decomposing
  extraction instruction (replacing the falsifiable-only framing) and
  the global heldBy capture. Update Stage 5 (verify, lines 377-425) to
  describe the routing split: `fact`-tagged claims → existing
  unmodified 3-voter adversarial-refutation quorum (unchanged);
  `opinion`-tagged claims → the new single attribution-confirmation
  check (Tasks 4-5), always surviving to Stage 6 when confirmed. State
  explicitly that decomposition already means no claim reaching Stage 5
  carries an unchecked factual assertion inside an opinion wrapper.
  Also add a `research-toolkit/CHANGELOG.md` entry for this change
  (moved here from Task 7 — hand-authored prose is documentation work,
  not a mechanical sync-script output, so it belongs with this task
  rather than diluting Task 7's `Review-weight: mechanical` claim).
- Module: research-toolkit/skills/deep-deep-research/SKILL.md
- Files touched: research-toolkit/skills/deep-deep-research/SKILL.md,
  research-toolkit/CHANGELOG.md
- Context paths:
  - research-toolkit/skills/deep-deep-research/SKILL.md (Stage 3 lines 314-354, Stage 5 lines 377-425)
- Acceptance:
  - RED (diagnostic, doc-only — no pytest applies): `grep -n
    "FALSIFIABLE" research-toolkit/skills/deep-deep-research/SKILL.md`
    still matches Stage 3's old framing, Stage 5 has no mention of
    `claimType`/`attribution` routing, and `research-toolkit/CHANGELOG.md`
    has no entry for this change
  - GREEN: fresh-context cold-read — an agent given only the edited
    SKILL.md correctly describes, unprompted, that opinion-tagged
    claims skip the refutation quorum and go through
    attribution-confirmation instead, and that mixed statements are
    decomposed at extraction (per `docs/loom/memory/cold-read-and-adversarial-review-catch-different-failures.md`,
    a cold-read is sufficient here — this is prose describing an
    already-implemented routing split, not itself introducing a
    gate/exemption an agent could game); `research-toolkit/CHANGELOG.md`
    has a new entry describing the change
- External surfaces: none
- Dependencies: Tasks 1, 2, 3, 4, 5 complete first (documents the
  shipped behavior of all of them, but has no dependency on Task 7, its
  same-level sibling — disjoint files from Task 7, so paired
  Independent: true with it)
- Independent: true
- Brief item covered: "Stage 5 routes by claimType... Nothing else
  changes... this is the minimal schema+routing fix"

## Task 7 — sync-primitives.sh + Codex manifest (mechanical)
- Description: SSOT is
  `research-toolkit/skills/deep-deep-research/scripts/{schemas.py,rank.py,prompts.py}`.
  Run `bash research-toolkit/scripts/sync-primitives.sh fact-check
  cite-check deep-read` (which copies the SSOT primitives touched by
  Tasks 1-5 into each sibling skill's own `scripts/`) and commit the
  result unmodified. No hand-written edits to the synced output. Bump
  `research-toolkit/.claude-plugin/plugin.json`'s version and run
  `python3 scripts/sync_codex_manifests.py research-toolkit` to mirror
  it into the Codex manifest. No hand-written edits to the Codex
  manifest output. (The CHANGELOG.md entry lives in Task 6, not here —
  hand-authored prose does not satisfy the mechanical-exemption bar.)
- Module: research-toolkit/scripts/ (sync outputs land in sibling skills' scripts/)
- Files touched: research-toolkit/skills/fact-check/scripts/schemas.py,
  research-toolkit/skills/fact-check/scripts/rank.py,
  research-toolkit/skills/fact-check/scripts/prompts.py,
  research-toolkit/skills/cite-check/scripts/schemas.py,
  research-toolkit/skills/cite-check/scripts/rank.py,
  research-toolkit/skills/cite-check/scripts/prompts.py,
  research-toolkit/skills/deep-read/scripts/schemas.py,
  research-toolkit/skills/deep-read/scripts/prompts.py,
  research-toolkit/.claude-plugin/plugin.json,
  research-toolkit/.codex-plugin/plugin.json
- Context paths:
  - research-toolkit/scripts/sync-primitives.sh
  - research-toolkit/scripts/sync_codex_manifests.py
- Acceptance:
  - RED: `git diff --stat` shows the sibling skills' synced copies
    still match the PRE-change SSOT (drifted from Tasks 1-5's edits)
  - GREEN: sibling copies are byte-identical to the post-change SSOT
    (re-running sync-primitives.sh produces zero diff); Codex manifest
    mirrors the version bump; CI's MD5 drift gate would pass
- External surfaces: none
- Dependencies: Tasks 1, 2, 3, 4, 5 complete first (syncs whatever
  those tasks changed in the SSOT, but has no dependency on Task 6, its
  same-level sibling — disjoint files from Task 6, so paired
  Independent: true with it)
- Independent: true
- Review-weight: mechanical
- Brief item covered: "Re-run sync-primitives.sh for fact-check
  cite-check deep-read after the schema/prompts changes land"

## Notes

- **Dogfood-test loop (post-plan, not an atomic task).** Per the
  standing session goal, after all 7 tasks are DONE and whole-branch
  review + verification pass, run `deep-deep-research` end-to-end on a
  real research question that exercises both paths (a question with
  genuine, evidence-backed expert disagreement, so at least one opinion
  claim is expected to survive via attribution-confirmation instead of
  being refutation-voted). This is an end-to-end behavioral check, not
  a unit-level RED/GREEN — it does not fit this plan's per-task
  schema, so it is NOT Task 8. The orchestrator drives it directly
  after SDD completion: run → inspect output for correct
  classification/routing → if a defect is found, fix (via a direct
  small patch + its own test, or a re-entry into writing-plans'
  BLOCKED-fallback split if the fix is non-trivial) → re-run → repeat
  until a dogfood run shows no defects.
