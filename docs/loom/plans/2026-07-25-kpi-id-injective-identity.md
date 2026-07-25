# Plan: injective kpi_id identity (consolidation axis + concept-case drift)

Source brief: docs/loom/specs/2026-07-25-kpi-id-injective-identity.md
Total tasks: 7
Critical-path depth: 5 (≤5) — 1→2→3→4→5; levels are {1,7} {2} {3} {4} {5,6}
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-25, round 2, 14/14 — round 1 returned NEEDS_REVISION on Task 7's non-runnable RED; fixed to a `git ls-files` diagnostic)

## Task 1 — `derive_kpi_id`: a non-default consolidation member enters the readable prefix

- Status: done(e60a0745)
- Description: give `derive_kpi_id` a third parameter carrying the
  consumer-normalized `ConsolidationItemsAxis` qualifier, and append a
  `__<member-slug>` token when that member is NOT the default
  `OperatingSegmentsMember`; a default or absent qualifier adds no token, so the
  2.36.0 fold survives by construction. Update the single production call site
  (`ingest_pack`, `kpi_xbrl_ingest.py:379`) to pass `_signature_key`'s already
  normalized qualifier — never the raw fact value. Rewrite the function
  docstring's now-false claim that the axis is "dropped from the signature".
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl_ingest.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl_ingest.py,
  investing-toolkit/tests/analysis/test_kpi_xbrl_ingest.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl_ingest.py (`derive_kpi_id` :117, `_consumer_consolidation` :144, `_signature_key` :162, `ingest_pack` :298)
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl.py (`_normalize_consolidation` :405, `_DEFAULT_CONSOLIDATION_MEMBER` :148)
  - docs/loom/memory/match-kpi-on-full-dimensional-signature-not-one-axis.md
- Acceptance:
  - RED: `investing-toolkit/tests/analysis/test_kpi_xbrl_ingest.py::test_derive_kpi_id_discriminates_non_default_consolidation` — over ONE (concept, dimensions), asserts `IntersegmentEliminationMember` and `OperatingSegmentsMember` mint DIFFERENT ids, and `None` and `OperatingSegmentsMember` mint the SAME id. Fails today because the axis is skipped at `:134-135`.
  - GREEN: that test passes AND `test_ingest_collapses_consolidation_variants_of_one_signature` (:219) still passes UNCHANGED — it is this arc's regression floor — AND `test_ingest_raises_on_two_non_default_consolidation_members` (:323) is re-pinned to its new polarity (the two members now mint distinct ids by construction, so the ingest SUCCEEDS with two series instead of raising) **with its stated rationale rewritten, not just its assertion flipped** (`docs/loom/memory/a-test-can-pin-behaviour-with-a-false-rationale.md`) — AND the full suite is green.
- External surfaces: none (pure internal logic; stdlib only).
- Dependencies: none
- Independent: false
- Brief item covered: "XOM's two consolidation views ingest as **two** series" and "The already-shipped fold stays intact: an **absent** consolidation tag and an explicit `OperatingSegmentsMember` remain **one** series".

## Task 2 — `derive_kpi_id`: append a 12-hex digest of the CASE-FOLDED identity tuple

- Status: done(80da4f7a)
- Description: append `__<12 lowercase hex>` to the readable prefix, computed as
  a sha1 over the NUL-separated, **case-folded** consumer identity tuple
  `(concept.casefold(), sorted (axis.casefold(), member.casefold()) pairs,
  normalized_consolidation.casefold())`. Mirrors `kpi_store._series_key`'s
  readable-stem-plus-digest precedent. Case is FOLDED, not preserved — the
  47-filer probe measured 21 series whose 10-Q and 10-K spellings differ, and
  preserving case files each series' quarterly history apart from its annual
  history. Update the function docstring to state the fold and its reason.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl_ingest.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl_ingest.py,
  investing-toolkit/tests/analysis/test_kpi_xbrl_ingest.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py (`_series_key` :71-92 — the digest precedent to mirror)
  - docs/loom/specs/2026-07-25-kpi-id-injective-identity.md (§Probe evidence)
  - docs/loom/memory/derived-durable-id-slug-is-a-lossy-one-way-door.md
- Acceptance:
  - RED: `investing-toolkit/tests/analysis/test_kpi_xbrl_ingest.py::test_derive_kpi_id_folds_case_and_stays_injective` — asserts (a) two signatures differing ONLY in letter case (e.g. `DataCenterMember` vs `DatacenterMember`) mint the SAME id, (b) two structurally distinct signatures mint DIFFERENT ids, (c) the id ends with `__` plus exactly 12 lowercase hex characters.
  - GREEN: that test passes and `test_ingest_kpi_id_derivation` (:374) is updated to the new shape and passes.
- External surfaces: none (`hashlib` is stdlib; no new dependency).
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "`derive_kpi_id` becomes **injective over the consumer's own identity tuple, up to case**".

## Task 3 — `_claim_kpi_id` accepts a case-insensitively equal claimant

- Status: done(80da4f7a)
- Description: relax the collision guard so a second claimant whose claim key is
  case-insensitively equal to the incumbent's is ACCEPTED (both selectors feed
  one series), while every other distinct claimant still raises. `_fact_matches`
  and `_signature_key` are NOT touched — each selector keeps exact-matching its
  own spelling's facts. Rewrite the module docstring paragraph
  (`kpi_xbrl_ingest.py:30-38`) that still describes the old drop-the-axis,
  lowercase-everything scheme.
- Module: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl_ingest.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl_ingest.py,
  investing-toolkit/tests/analysis/test_kpi_xbrl_ingest.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_xbrl_ingest.py (`_claim_kpi_id` :205)
  - docs/loom/memory/a-test-can-pin-behaviour-with-a-false-rationale.md (read each existing test's stated RATIONALE as a claim to verify, not as context)
- Acceptance:
  - RED: `investing-toolkit/tests/analysis/test_kpi_xbrl_ingest.py::test_ingest_folds_case_variant_selectors_into_one_series` — a pack carrying ONE signature under two spellings ingests into ONE series holding every vintage from both, instead of raising.
  - GREEN: that test passes; `test_ingest_collision_guard_fires_across_consolidation_variants` (:285) is re-pinned to its new polarity (two series, no raise) with its rationale rewritten; `test_ingest_raises_on_kpi_id_collision` (:171) is re-read and either kept or re-pinned per whether its two signatures differ structurally or only by case; a structurally distinct collision STILL raises. (`test_ingest_raises_on_two_non_default_consolidation_members` moved to Task 1 — see the Notes amendment.)
- External surfaces: none.
- Dependencies: Task 2 completes first
- Independent: false
- Brief item covered: "§Required companion change to the collision guard" — "`_claim_kpi_id` must accept a second claimant whose claim key is **case-insensitively equal** to the incumbent's, and keep raising otherwise".

## Task 4 — end-to-end: both real shapes ingest correctly from one fact-pack

- Status: done(92baf061)
- Description: add an end-to-end test over a committed fact-pack fixture that
  carries BOTH measured shapes — (a) one signature under two consolidation
  members present in the same filing, (b) one signature under two spellings
  split across 10-Q (3/6/9-month) and 10-K (12-month) durations — plus one flat
  top-line fact. Fixture values are synthetic; its shape mirrors the probe's
  observed producer output.
- Module: investing-toolkit/tests/analysis/test_kpi_id_identity_e2e.py
- Files touched: investing-toolkit/tests/analysis/test_kpi_id_identity_e2e.py,
  investing-toolkit/tests/analysis/fixtures/xbrl_kpi_id_identity_factpack.json
- Context paths:
  - investing-toolkit/tests/analysis/fixtures/xbrl_consolidation_variant_factpack.json (existing sibling fixture to mirror in shape)
  - investing-toolkit/tests/analysis/test_top_line_two_lane_e2e.py (the arc's e2e precedent, incl. isolated-store fixture usage)
  - docs/loom/memory/fixtures-mirror-producer-shape.md
- Acceptance:
  - RED: `investing-toolkit/tests/analysis/test_kpi_id_identity_e2e.py::test_consolidation_splits_and_case_folds_in_one_ingest` — asserts the consolidation pair lands as TWO series, the spelling pair lands as ONE series holding both its quarterly AND its annual points, and the flat fact still lands under the literal `total_revenue` id (no digest).
  - GREEN: that test passes and the whole `investing-toolkit/tests/` suite is green under `-m "not network"`.
- External surfaces: none (offline fixture; no network).
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "a filer's 10-Q and 10-K spellings of one segment ingest as **one** series carrying both its quarterly and its annual history"; also "The fixed canonical top-line series `total_revenue` is **untouched**" and "Measured target: the 23 of 47 filers that abort today all ingest, with 0 unintended merges".

## Task 5 — docs: analysis-kpi SKILL.md states what the id derivation now discriminates

- Status: done(bd88c0cd)
- Description: amend the one sentence describing the dimensional ingest
  (`SKILL.md:98-99`, "derives a `kpi_id` per dimensional signature") so it names
  both identity rules: a non-default consolidation member discriminates, and
  spelling case does not.
- Module: investing-toolkit/skills/analysis-kpi/SKILL.md
- Files touched: investing-toolkit/skills/analysis-kpi/SKILL.md
- Context paths:
  - investing-toolkit/skills/analysis-kpi/SKILL.md (:92-100)
  - docs/loom/specs/2026-07-25-kpi-id-injective-identity.md (§Chosen mechanism)
- Acceptance:
  - RED: diagnostic — `grep -n 'per dimensional signature' investing-toolkit/skills/analysis-kpi/SKILL.md` shows the sentence with no mention of the consolidation qualifier or of case folding.
  - GREEN: the same grep shows a sentence naming both rules, and no other SKILL.md claim about `kpi_id` contradicts the shipped behavior.
- External surfaces: none (documentation).
- Dependencies: Task 4 completes first
- Independent: true
- Brief item covered: "§Chosen mechanism" — the shipped identity rules must be discoverable from the skill's own documentation, not only from a docstring.

## Task 6 — version bump 2.37.0 + CHANGELOG + Codex manifest sync

- Status: done(bd88c0cd)
- Description: bump `investing-toolkit` to 2.37.0 in BOTH manifests and add the
  CHANGELOG entry describing the identity change and its blast radius (no
  migration; the store was empty at ship time).
- Module: investing-toolkit/CHANGELOG.md
- Files touched: investing-toolkit/CHANGELOG.md,
  investing-toolkit/.claude-plugin/plugin.json,
  investing-toolkit/.codex-plugin/plugin.json
- Context paths:
  - investing-toolkit/CHANGELOG.md (the 2.36.0 entry as the format precedent)
  - docs/loom/specs/2026-07-25-kpi-id-injective-identity.md (§Decision)
- Acceptance:
  - RED: diagnostic — `grep -m1 '"version"' investing-toolkit/.claude-plugin/plugin.json` reads `2.36.0` while the branch has changed shipped script behavior (repo rule: a skill-content change requires a version bump or the marketplace update is a silent no-op).
  - GREEN: both manifests read `2.37.0` and `CHANGELOG.md` carries a 2.37.0 entry naming the consolidation split, the case fold, and the empty-store clean break.
- External surfaces: none.
- Dependencies: Task 4 completes first
- Independent: true
- Brief item covered: "§Decision" — "Ship no migration path, no alias map, and no back-compat id", which the CHANGELOG must state for anyone holding a store elsewhere.

## Task 7 — commit the probe as a regeneratable capture + counts-only fixture

- Status: done(d9572c73)
- Description: commit the 47-filer identity probe as a hand-run capture script
  plus a COUNTS-ONLY JSON, mirroring
  `tests/data/fixtures/capture_companyconcept_form_domain.py`. No financial
  values are captured — only collision counts, kinds, co-occurrence, and the
  observed `ConsolidationItemsAxis` member domain. Not collected by pytest (not
  a `test_*` module).
- Module: investing-toolkit/tests/data/fixtures/capture_kpi_id_identity_probe.py
- Files touched: investing-toolkit/tests/data/fixtures/capture_kpi_id_identity_probe.py,
  investing-toolkit/tests/data/fixtures/kpi_id_identity_probe_2026-07-25.json
- Context paths:
  - investing-toolkit/tests/data/fixtures/capture_companyconcept_form_domain.py (the precedent: module docstring states WHAT IT ANSWERS / NETWORK / FILER SAMPLE and why each filer is in it)
  - docs/loom/specs/2026-07-25-kpi-id-injective-identity.md (§Probe evidence — the numbers the fixture must reproduce)
- Acceptance:
  - RED: diagnostic — `git ls-files investing-toolkit/tests/data/fixtures/capture_kpi_id_identity_probe.py investing-toolkit/tests/data/fixtures/kpi_id_identity_probe_2026-07-25.json` prints EMPTY today (neither file is tracked), so the brief's §Probe evidence numbers have no committed artifact behind them.
  - GREEN: the same `git ls-files` prints both paths; `python3 -c "import json;d=json.load(open('investing-toolkit/tests/data/fixtures/kpi_id_identity_probe_2026-07-25.json'));print(d['_summary']['n_filers_aborting_today'], d['_summary']['proposed_total_collisions'])"` prints `23 0`, matching §Probe evidence; the JSON carries a `_capture` block naming the endpoint, capture date, and filer-sample rationale; and `pytest --collect-only investing-toolkit/tests/data/fixtures/` does not collect the capture script.
- External surfaces: SEC EDGAR over HTTPS (`data.sec.gov`) via a `pack.py` subprocess — network, hand-run only, never part of the offline suite; same posture as the sibling capture script it mirrors.
- Dependencies: none
- Independent: true
- Brief item covered: "§What Becomes Obsolete" — "the arc commits a regeneratable capture script plus a COUNTS-ONLY JSON so the §Probe evidence numbers are reproducible rather than assertions in prose".

## Notes

- Post-PASS amendment #2, re-review skipped: re-pinning
  `test_ingest_raises_on_two_non_default_consolidation_members` moved from Task 3's
  GREEN to Task 1's GREEN. Found during execution — Task 1's change ALONE makes the two
  members mint distinct ids, so the guard never fires and the test flips at Task 1, not
  Task 3. Leaving it on Task 3 would have left the suite RED across two intermediate
  commits. No task, dependency edge, `Files touched` set, or `Independent` claim changed
  — one acceptance clause moved between two tasks that already both declare that test
  file, so the DAG and every field-presence check are untouched.
- Post-PASS amendment #1, re-review skipped: the kickoff pins and the `## Decision Log`
  section below were appended after the reviewer's PASS. Purely additive — no task
  field, dependency edge, or `Independent` claim changed, so the DAG and every
  schema-checked field are untouched (writing-plans §Amending a PASS plan, option b).
- Kickoff decision: digest length → 12 lowercase hex, matching `kpi_store._series_key`'s
  shipped digest (`kpi_store.py:89-91`). Arm-1 look-up: the repo already answered this
  one layer down; a second length would be an unexplained divergence.
- Kickoff decision: prefix↔digest delimiter → `__`, the delimiter `derive_kpi_id`
  already uses between signature segments. Arm-1 look-up, same reason.
- Kickoff decision: fold function → `str.casefold()` for the DIGEST input; the readable
  prefix keeps the shipped `_slug_token`'s `.lower()`. The two agree on every ASCII
  XBRL NCName, which is the entire observed corpus (47 filers, 51,147 facts); `casefold`
  is chosen for the identity-bearing half because it is the stricter fold. Pinned here
  because a future non-ASCII element name is the one input where they could diverge —
  and the digest is the durable half.
- Kickoff appetite read: no `docs/loom/PRINCIPLES.md` in this repo, so the §d default
  applies (brief every one-way-door hit). The sweep found no UNRESOLVED one-way-door
  decision: the identity format itself is the arc's one-way door and was briefed and
  decided twice — chosen as C on 2026-07-25 and amended to C′ the same day after the
  47-filer probe disproved the case-preserving half. The three pins above are arm-1
  look-ups (settled by in-repo precedent), recorded unbriefed per kickoff-briefing §b.

- **No loom-spec change-folder bound.** Two non-archived change-folders exist
  (`docs/loom/2026-07-12-us-sec-primary-source-layer`,
  `docs/loom/2026-07-19-8k-prose-kpi-intake`); neither covers this arc, and the
  caller handed a brainstorming brief path directly (Layer 0). The scenario
  coverage self-check (`check_scenario_coverage.py`) is therefore N/A — it
  applies only to the change-folder input path.
- **Tasks 1-4 are strictly sequential by construction**: they edit the same two
  files, and each one's RED test only becomes writable once its predecessor's
  behavior exists. No parallel opportunity is being missed there.
- **Branch** `feat-kpi-id-consolidation-axis`, created from `90374e63` (the
  2.36.0 squash) — NOT from the merged branch tip, so the PR diff carries only
  this arc.
- **Out of scope, per brief**: BACKLOG item (l) pack-wide blast radius, the TW
  producer `kpi_tw._tw_kpi_id`, fact-matching semantics, and any migration path.

## Decision Log

- 2026-07-25 — **Tasks 2 and 3 land in ONE commit.** The plan split them for TDD
  granularity, but the green-suite boundary falls after Task 3: Task 2's digest makes
  two case-variant selectors derive one id, which the un-relaxed guard still refuses,
  so Task 2 alone leaves the suite red. Committing a knowingly-red intermediate would
  break bisectability for no gain. Both tasks' reviewers run against the combined diff.
  Two-way door. Discovered during execution, not at kickoff.
- 2026-07-25 — **The collision guard keeps a forced-collision test via monkeypatch.**
  After Task 2 the guard's raise path is unreachable through ordinary inputs (the id is
  injective over the consumer identity tuple; only a case-variant pair — now accepted —
  or a sha1 collision could reach it). Options were: keep it untested and document the
  unreachability, delete it, or construct the unreachable case with a test double. Chose
  the test double: a tripwire that never demonstrates it fires advertises protection it
  cannot show, and the guard's value is defense-in-depth against a FUTURE change to the
  derivation — which is exactly what a forced-collision test pins. No product
  consequence, two-way door (a test technique, freely changed later).
- 2026-07-25 — Version bump is **2.37.0 (minor), not 3.0.0**. The id-format change
  is breaking for any holder of an existing store, which would argue for a major
  bump; it is recorded as minor because the store is verifiably empty at ship time
  (no `~/.local/share/investing-toolkit`, no env override) so no consumer is broken
  in fact, and the repo's shipped convention bumps minor per capability arc.
  Two-way door — a later release can renumber. Late-vetoable.
