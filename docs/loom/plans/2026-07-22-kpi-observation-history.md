# Plan: KPI observation history — US lane (Slice C)

Source brief: docs/loom/specs/2026-07-20-kpi-observation-history.md
Total tasks: 8   (T8 added mid-SDD 2026-07-22 — a write-side guard for a double-scale hole found during T6 review; see Task 8 + Notes "T8 amendment")
Critical-path depth: 3 (≤5)   ← longest chain: T2 → T3 → T6 (period-fields → identity-key → history read); T8 is an independent leaf
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-22, 14/14 after the round-1 Check-8 fix — see Notes "amendment"). Round-1 NEEDS_REVISION was the missing decision-(B) coverage, now recorded as an explicit Notes exclusion; the two advisory notes (dispatcher-mechanism wording, per-predicate test bundling) are folded in. Amendment is additive (a Notes exclusion + reworded Notes + a test-splitting note), no task/DAG/field change → re-review skipped per writing-plans §"Amending a PASS plan" (b).

Scope: US lane only (see brief §Scope decision). Extends existing modules; adds no
new plugin. All test paths under `investing-toolkit/tests/`. Resolved test command:
`PYTHONDONTWRITEBYTECODE=1 uv run --quiet --with pytest --with 'pyyaml>=6.0' pytest investing-toolkit/tests/ -m "not network" -q`

Key seam facts from recon (2026-07-22):
- `kpi_store._DEDUP_KEY_FIELDS = ("company","kpi_id","period","as_of","source_accession")`
  (`kpi_store.py:151`) — a duplicate key is silent first-record-wins (`:207-210`).
- `_prose_candidate_to_point` (`kpi_prose_candidates.py:613`) is the sole prose→point
  assembler; the point carries `period` (an LLM string), `source_cell_ref="prose:{s}-{e}"`.
- No enumerate primitive: `_store_fs.py` has `resolve_store_dir` (`:43`) but no glob/iterdir.
- No surface/flattener version constant exists in `exhibit_prose.py` — T4 mints it.
- `_derive_fiscal_label` (`sec_edgar_client.py:2658`) + `FISCAL_BOUNDARY_TOLERANCE_DAYS=10`
  already exist; the XBRL lane emits `fiscal_period_focus`/`period_end` per fact. REUSE.

## Task 1 — store enumeration primitive
- Description: Add a `list_series()` (and a thin `list_companies()`/`list_kpis(company)` on top) to the store that scans the store dir and returns the `(company, kpi_id)` pairs held, reading each series file's points to recover the raw company/kpi_id (the filename digest is one-way, `kpi_store.py:68-93`). Returns an empty list on an absent store dir, never raises.
- Module: kpi_store.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py, investing-toolkit/tests/test_kpi_store_enumerate.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py (`_series_path`, `_load_series`, `resolve_store_dir`)
  - investing-toolkit/skills/analysis-kpi/scripts/_store_fs.py (`resolve_store_dir`)
- Acceptance:
  - RED: test_list_series_recovers_company_kpi — append two points under distinct (company,kpi_id), then `list_series()` returns both pairs recovered from file CONTENT (not the one-way digest); `list_series()` on an empty/absent store returns `[]` without raising.
  - GREEN: enumeration returns the held pairs; absent-dir returns `[]`.
- Dependencies: none
- Independent: true   # disjoint files, no shared symbol with T2/T4
- Brief item covered: Smallest End State (1) — "The store can be enumerated … without already knowing the query key"

## Task 2 — period identity fields on the prose point
- Description: Extend `_prose_candidate_to_point` so the committed point carries the raw period-identity fields `period_start` / `period_end` / `period_kind` (duration|instant) alongside the existing display `period` label — sourced from the candidate, defaulting to None when the candidate lacks them (prose candidates may not yet carry dates; this task only adds the FIELDS + pass-through, not their derivation). Do NOT change the dedup key yet (that is T3). Do NOT weaken `passes_substring_gate` or touch offsets.
- Module: kpi_prose_candidates.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py, investing-toolkit/tests/test_kpi_prose_candidates.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py (`_prose_candidate_to_point:613-668`, `commit_to_store`)
- Acceptance:
  - RED: test_prose_point_carries_period_identity_fields — a candidate with `period_start`/`period_end`/`period_kind` set produces a point carrying those three verbatim; a candidate without them produces a point with all three = None (no crash), and the existing `period` label field is unchanged.
  - GREEN: the three identity fields ride onto the point; label untouched.
- Dependencies: none
- Independent: false   # shares kpi_prose_candidates.py with T5; and T3 depends on it
- Brief item covered: Smallest End State (2) / §Period model — "a stored point's period IDENTITY is the raw (start,end) context pair … labels remain first-class fields"

## Task 3 — same-period identity match on (start,end), month-end-snap fallback
- Description: Add a `same_period(point_a, point_b)` predicate (and a `_period_sort_key(point)` returning `end` then a duration-quarters tiebreak) that matches two observations as the same period by exact `(period_start, period_end)`, with a fallback that matches when `period_end` snapped to nearest month-end is equal AND the duration in quarters (`qtrs`, 0=instant) is equal — per brief §Period model. Sorting is by `period_end`. This is pure logic over the fields T2 added; it does NOT alter the store dedup key (recorded exclusion — see Notes).
- Module: kpi_store.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py, investing-toolkit/tests/test_kpi_store_period_identity.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py (`_matching_points`, `_dedup_key`)
- Acceptance:
  - RED: test_same_period_exact_and_snap — two points with byte-identical `(start,end)` match; two points whose `end` differs by 1 day but snap to the same month-end AND share `qtrs` match via fallback; two genuinely different periods (different month-end OR different qtrs) do NOT match (no false merge — pin the event-style same-end-date/different-qtrs case).
  - GREEN: exact match + snap fallback both hold; no false merge across different qtrs.
- Dependencies: Task 2 completes first (consumes the identity fields)
- Independent: false
- Brief item covered: §Period model — "match exact (start,end), fallback = end snapped to month-end + qtrs"; §Constraints — "normalize … before comparing" (no false merge)

## Task 4 — surface-version stamp minted at the flattener
- Description: Mint a `SURFACE_VERSION` constant in `exhibit_prose.py` (a single monotonic string, documented that it bumps whenever `prose_surface`'s normalization changes — the Part-2 folds were such a change) and expose it so a consumer can read the version that produced a given surface. Locator/flatten behavior is unchanged; this task only adds the declared version primitive.
- Module: exhibit_prose.py
- Files touched: investing-toolkit/skills/data-markets/scripts/exhibit_prose.py, investing-toolkit/tests/test_exhibit_prose.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/exhibit_prose.py (`prose_surface`, module docstring on normalization)
- Acceptance:
  - RED: test_surface_version_declared — `exhibit_prose.SURFACE_VERSION` exists, is a non-empty str, and is stable across two calls; a comment/docstring ties a bump to a normalization change.
  - GREEN: the constant is present and stable.
- Dependencies: none
- Independent: true   # disjoint file (data-markets), no shared symbol with T1/T2
- Brief item covered: Smallest End State (3) — "flattener/surface version" half of the integrity stamp

## Task 5 — integrity stamp written onto the prose point
- Description: In `_prose_candidate_to_point`, add an `integrity` field = `{ "span_sha256": sha256(matched_token bytes), "surface_version": <value> }`, where `surface_version` is passed in by the caller (the value read from `exhibit_prose.SURFACE_VERSION` via the existing subprocess boundary — do NOT in-process import data-markets; thread it as a parameter through `commit_to_store`, defaulting to None so non-prose callers are unaffected). Hash the ANCHORED TOKEN (the load-bearing datum), not the whole quote. Write-time only; no read-time verification (Part 3).
- Module: kpi_prose_candidates.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py, investing-toolkit/tests/test_kpi_prose_candidates.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py (`_prose_candidate_to_point`, `commit_to_store` signature)
- Acceptance:
  - RED: test_prose_point_carries_integrity_stamp — a committed point carries `integrity.span_sha256` == sha256 of the matched token and `integrity.surface_version` == the threaded value; the hash is over the token, not the bounded quote (assert they differ when quote ≠ token).
  - GREEN: the stamp rides onto the point; hash is the token's.
- Dependencies: Task 2 completes first   # both edit _prose_candidate_to_point; serialize to avoid churn
- Independent: false   # shares kpi_prose_candidates.py with T2
- Brief item covered: Smallest End State (3) — "a hash of the anchored span, plus the flattener/surface version. Write-time only."

## Task 6 — history read: observations of a period across filings, disagreement flagged
- Description: Add a `history(company, kpi_id, period_match)` read that returns every stored observation matching one period (via T3's `same_period`), ordered by `as_of` (T3's sort), each carrying its value + source_accession + as_of, and a computed `disagreement: bool` = True when ≥2 observations share the period but differ in `value` after unit normalization. Detection is a VALUE DIFF across the returned observations, never an event lookup (brief §Constraints). A superseded value is retained and returned, not marked wrong (§Constraints).
- Module: kpi_store.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py, investing-toolkit/tests/test_kpi_store_history.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_store.py (`_matching_points`, `query_latest`, and T3's `same_period`/`_period_sort_key`)
- Acceptance:
  - RED: test_history_flags_disagreement_across_filings — the J&J shape: two observations of one period (values 93775000000 and 78740000000) from different accessions/as_of return both, ordered by as_of, with `disagreement=True`; two observations with the same value return `disagreement=False`; a single observation returns `disagreement=False`. All observations retained (none dropped as "wrong").
  - GREEN: history returns the ordered vintages with a correct disagreement flag.
- Dependencies: Task 3 completes first (consumes `same_period`/sort)
- Independent: false
- Brief item covered: Smallest End State (4) — "history answers 'what has been said about period P, and when' … flagging when they disagree"

## Task 8 — prose commit rejects a magnitude-word unit (added mid-SDD, 2026-07-22)
- Description: The prose lane stores BASE-SCALE values (`_normalize_value` folds the
  magnitude word into `value` at write time), so a prose point's `unit` must be a
  dimensional label, never a magnitude word. `commit` currently accepts any unit on a
  confirmed candidate, so a human/LLM confirming `unit="billion"` on an already-scaled
  3,560,000,000 would make T6's `history` scaler multiply it AGAIN (→ 3.56e18). This guard
  rejects a magnitude-word unit (whole-word matched, `\b`, per the Part-2 lesson) at prose
  commit, fail-closed. Added after both T6 re-reviews passed but the orchestrator verified
  the write-side hole is live (`commit` returns `list(candidates)` with zero unit check).
- Module: kpi_prose_candidates.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py, investing-toolkit/tests/test_kpi_prose_candidates.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py (`commit` ~:552-578)
  - investing-toolkit/skills/data-markets/scripts/exhibit_prose.py (the `\b`-guarded magnitude regex to mirror)
- Acceptance:
  - RED: test_commit_rejects_magnitude_word_unit — a confirmed candidate with unit="billion"/"millions" (case-insensitive) does not reach the committed set; a dimensional unit ("USD"/"people"/"GW") commits unchanged; a unit containing a magnitude word only as a substring of a larger token is NOT falsely rejected.
  - GREEN: magnitude-word units never reach the store via commit.
- Dependencies: none   # different file from T6; closes the write-side of T6's read-side scaling
- Independent: true   # kpi_prose_candidates.py — disjoint from T6's kpi_store.py
- Brief item covered: §Constraints 4 (normalize unit before comparing) + §Problem (no fabricated value) — the write-side guarantee T6's history docstring trusts

## Task 7 — BACKLOG correction + brief-obsolescence cleanup
- Description: Delete the unevidenced "≥10yr, industry norm" claim from `docs/loom/BACKLOG.md:167`, replace the "Slice C = coverage file + retention + tearsheet" framing with this slice's shipped shape, and log the five pre-existing defects the recon found (from brief §Pre-existing defects) as next-touch items. Docs-only.
- Module: docs/loom/BACKLOG.md
- Files touched: docs/loom/BACKLOG.md
- Context paths:
  - docs/loom/BACKLOG.md (§非金錢營運 KPI)
  - docs/loom/specs/2026-07-20-kpi-observation-history.md (§What Becomes Obsolete, §Pre-existing defects)
- Acceptance:
  - RED: grep diagnostic — `grep -n "≥10yr" docs/loom/BACKLOG.md` returns a hit before, zero after; the five pre-existing defects each appear as a next-touch line.
  - GREEN: the stale claim is gone; the five defects are logged.
- Dependencies: none
- Independent: true   # docs-only, disjoint from all code files
- Brief item covered: §What Becomes Obsolete — "delete the ≥10yr claim"; §Pre-existing defects — "log, do not fix here"

## Notes

- **Depth 3, one chain:** T2 (period fields) → T3 (identity match on those fields) →
  T6 (history read consuming the match). T5 also depends on T2 (same file). T1, T4, T7
  are independent leaves. Same-file serialization: T2/T5 both edit
  `kpi_prose_candidates.py` (T5 after T2); T3/T6 both edit `kpi_store.py` but T6 depends
  on T3 semantically anyway. T1 also edits `kpi_store.py` — it is `Independent: true`
  only against T2/T4 (different files). Against T3/T6 it shares the file, but this is
  NOT a parallel-dispatch hazard: T3/T6 are `Independent: false`, so no Independent-pair
  disjointness rule is engaged. The safety net is SDD's own default — the per-task triad
  runs one task at a time, and `dispatching-parallel-agents` only batches a cluster of
  MUTUALLY `Independent: true` tasks (of which only T1/T4/T7 qualify, and those three
  touch three disjoint files: kpi_store.py / exhibit_prose.py / BACKLOG.md). T1 vs
  T3/T6 never co-dispatch because T3/T6 aren't in any Independent batch. (Round-1
  reviewer note: an earlier draft cited a nonexistent "dispatcher file-overlap floor";
  the real mechanism is SDD sequential dispatch + Independent-only batching, as stated
  here.)
- **Amendment (2026-07-22, post round-1 review) — decision (B) is an explicit
  exclusion, not an omission.** The brief §Decision closes conflict resolution with TWO
  policies: (A) same-source-type / different-filing-dates → EXPOSE the choice, and
  (B) different-source-types / same-period → AUTO-resolve by source precedence (audited
  wins, loser retained). T6 implements (A) — retain all vintages, flag disagreement —
  and applies it uniformly. (B)'s auto-resolution is **deliberately deferred from this
  slice**, parallel to the dedup-key exclusion below, for a concrete reason: applying
  "audited wins" requires each point to carry a source-TYPE classification
  (audited-filing vs preliminary press-release), and **no field this slice adds carries
  that** — the prose lane's points have `source_accession` but no audited/preliminary
  tag, and the XBRL lane is not in the store at all (brief §Decision "no copying XBRL
  facts"). So (B) has no data to resolve on until a source-type field and a second
  populated lane exist. Until then T6 correctly surfaces a (B)-shaped conflict as
  `disagreement=True` (safe: retain-all, decide-nothing) rather than silently applying a
  precedence it cannot yet compute. Adding the field + audited-wins is a separate,
  data-gated follow-up. Recorded so a reviewer does not read (B)'s absence as accidental.
- **Test bundling (T3/T6) is idiomatic, by design.** T3's `test_same_period_exact_and_snap`
  and T6's `test_history_flags_disagreement_across_filings` each exercise three cases of
  ONE predicate's contract (exact/snap/no-false-merge; disagree/agree/single). That is
  boundary-testing one seam, not three features — the `Description` stays single-assertion.
  The implementer MAY split them into parametrized cases for failure diagnosability; not
  required.
- **Deliberate exclusion — the dedup key is NOT changed to the date pair (§Error in
  brief).** The store's `_DEDUP_KEY_FIELDS` still contains the string `period`.
  Changing identity to `(start,end)` at the DEDUP layer would silently drop or
  mis-merge already-stored points (first-record-wins on a changed key), and backfill
  is blocked (brief §Error / §Out of Scope). So this slice adds the identity fields and
  a `same_period` predicate used by READS (T3/T6), while the write-side dedup key is
  left untouched. Recorded so a reviewer does not read the untouched dedup key as an
  omission. The dedup-key migration is a separate, user-gated decision.
- **No XBRL-lane producer task.** The brief keeps XBRL facts out of the store
  (machine-reproducible, derived on read). This slice's identity/history machinery is
  built and tested on the prose lane + synthetic points; wiring an XBRL producer into
  the store is explicitly out of scope. T6's J&J test uses synthetic points carrying
  the two real values, not a live XBRL fetch.
- **Reuse, not rebuild.** No task re-derives fiscal geometry — `_derive_fiscal_label`
  and the `kpi-quarterly` per-fact labels already exist (brief §Period model). The
  label is an analysis coordinate produced upstream; this slice consumes it and never
  recomputes it.
- **SKILL wiring deferred.** None of these seams is exposed in `analysis-kpi/SKILL.md`
  as a user CLI in this slice (the prose lane is still not user-invocable — brief
  §Out of Scope). These are library primitives + tests; the user-facing `history`/
  `list` CLI is a separable follow-up.
