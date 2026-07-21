# Plan: 8-K prose KPI intake — Part 2 (number robustness)

Source change-folder: docs/loom/2026-07-19-8k-prose-kpi-intake/ (loom-spec, validated + completeness-critic PASS_WITH_NOTES, re-minted 2026-07-20 after the word-scale requirement was added)
Bound via: Layer 0 explicit handoff (orchestrator-authored change-folder; same as Part 1)
Total tasks: 6
Critical-path depth: 2 (≤5)   ← longest Dependencies chain: T1→T2 (word-scale locator → value multiplier)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-20, 14/14 checks)

Scope: Part 2 of the user-approved 3-part split. Part 1 (walking skeleton) SHIPPED
(PR #593, 2.28.0). Part 2 = NUMBER ROBUSTNESS — make the extracted values correct
and reject non-KPI numbers. Motivated by the live 5-company test matrix (2026-07-20):
META Family DAP "3.56 billion" was captured with value 3.56 instead of 3,560,000,000
(the word-scale gap) — the #1 fix for big-tech prose KPIs. Part 3 (lifecycle/
hardening) stays deferred.

Extends the shipped Part-1 files (no new modules):
- `investing-toolkit/skills/data-markets/scripts/exhibit_prose.py` (locator + surface)
- `investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py` (value derivation + producer)

## Task 1 — word-scale locator: absorb the magnitude word into the token
- Description: Extend `locate_numbers` so a magnitude word (thousand / million / billion / trillion, case-insensitive) immediately following a number is absorbed into the matched token — "3.56 billion" → token "3.56 billion" (span covers the whole phrase) — while a following NON-magnitude word is not ("931 warehouses" → token "931"). The exact-substring anchor invariant text[start:end]==token must still hold over the extended span.
- Module: exhibit_prose.py
- Files touched: investing-toolkit/skills/data-markets/scripts/exhibit_prose.py, investing-toolkit/tests/test_exhibit_prose.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/exhibit_prose.py (the committed `_NUMBER_RE` + `locate_numbers`)
- Acceptance:
  - RED: test_locate_absorbs_magnitude_word — "Family DAP was 3.56 billion on average" → a candidate token "3.56 billion" with text[start:end]=="3.56 billion"; "operates 931 warehouses" → token "931" (no absorb).
  - GREEN: `locate_numbers` returns the magnitude word inside the token when present, span covering it, anchor invariant intact.
- Dependencies: none
- Independent: false   # shares exhibit_prose.py with Task 5
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Word-scale magnitude parsing / Scenario: billion magnitude scales the value, token stays verbatim
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Word-scale magnitude parsing / Scenario: a plain number without a magnitude word is unchanged

## Task 2 — word-scale value multiplier
- Description: Extend `_normalize_value` so a token ending in a magnitude word applies the multiplier: "3.56 billion" → 3560000000, "500 million" → 500000000, "1.2 trillion" → 1200000000000; a token with no magnitude word is unchanged ("931" → 931, "1,576,000" → 1576000). The normalized value is DERIVED (not required to be a source substring — the anti-fabrication gate still checks the verbatim token, which now includes the magnitude word).
- Module: kpi_prose_candidates.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py, investing-toolkit/tests/test_kpi_prose_candidates.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py (the committed `_normalize_value` + `build_candidates`)
- Acceptance:
  - RED: test_normalize_value_word_scale — `_normalize_value("3.56 billion")`==3560000000; `("500 million")`==500000000; `("931")`==931; `("1,576,000")`==1576000 (plain unchanged).
  - GREEN: the multiplier is applied only when a magnitude word is present.
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Word-scale magnitude parsing / Scenario: million magnitude

## Task 3 — date / fiscal-period token rejection
- Description: A number that functions as a date or fiscal-period label ("Q1 2026", "fiscal 2025", a bare 4-digit year in a temporal phrase) MUST NOT be emitted as a KPI value candidate.
- Module: kpi_prose_candidates.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py, investing-toolkit/tests/test_kpi_prose_candidates.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py (build_candidates — where the filter lands)
- Acceptance:
  - RED: test_period_label_not_a_candidate — "In the first quarter of fiscal 2026, deliveries rose" → "2026" is NOT emitted as a value candidate.
  - GREEN: date/period tokens are filtered from the emitted candidates.
- Dependencies: none
- Independent: false   # shares kpi_prose_candidates.py with Tasks 2/4/6
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Date and period tokens are not KPI values / Scenario: period label is not a candidate

## Task 4 — bounding-qualifier flag (not a bare equality value)
- Description: When a bounding/approximation qualifier precedes a number ("up to", "approximately", "~", "over", "at least", "more than"), the candidate MUST carry the qualifier (a flag/field) and NOT be committed as a bare equality point value.
- Module: kpi_prose_candidates.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py, investing-toolkit/tests/test_kpi_prose_candidates.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py
- Acceptance:
  - RED: test_bounding_qualifier_flagged — "up to 45,000 deliveries" → the candidate carries the qualifier ("up to") and is not a bare 45000 equality value; a plain "45,000 deliveries" has no qualifier.
  - GREEN: the qualifier is captured on the candidate.
- Dependencies: none
- Independent: false
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Date and period tokens are not KPI values / Scenario: bounding qualifiers are not stored as bare equality values

## Task 5 — consistent normalization (nbsp / entities / full-width digits)
- Description: Apply ONE normalization (non-breaking/thin spaces, HTML entity decoding, smart quotes, full-width/Arabic-Indic digits) consistently to the surface/locate/quote/offset so a legitimately formatted number ("3 560 000" with nbsp separators) is located as one number, its offset maps to the canonical text, and it is neither false-rejected nor mis-indexed.
- Module: exhibit_prose.py
- Files touched: investing-toolkit/skills/data-markets/scripts/exhibit_prose.py, investing-toolkit/tests/test_exhibit_prose.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/exhibit_prose.py (prose_surface + locate_numbers)
- Acceptance:
  - RED: test_nbsp_separated_number_located — canonical text containing "3 560 000 subscribers" (nbsp separators) → located as one number with a valid offset span (text[start:end]==token); not dropped.
  - GREEN: the normalization is applied consistently; the anchor invariant holds.
- Dependencies: none
- Independent: false   # shares exhibit_prose.py with Task 1
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Consistent text normalization / Scenario: nbsp-separated number is not false-rejected

## Task 6 — PII: minimal bounded context window
- Description: The committed provenance MUST store the minimal verbatim token span plus a BOUNDED surrounding context window (a fixed char budget), not an unbounded full sentence/paragraph — to limit incidental capture of personal data (names, compensation figures) in SEC prose.
- Module: kpi_prose_candidates.py
- Files touched: investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py, investing-toolkit/tests/test_kpi_prose_candidates.py
- Context paths:
  - investing-toolkit/skills/analysis-kpi/scripts/kpi_prose_candidates.py (_prose_candidate_to_point / commit_to_store provenance)
- Acceptance:
  - RED: test_bounded_context_window — a KPI sentence embedded in a longer paragraph that also names an executive + a comp figure → provenance stores the token span plus a bounded window (≤ a fixed budget), NOT the whole paragraph.
  - GREEN: the stored context is bounded, not the full surrounding text.
- Dependencies: none
- Independent: false
- Brief item covered: 2026-07-19-8k-prose-kpi-intake / Requirement: Minimal provenance capture for privacy / Scenario: bounded context window, not full paragraph

## Notes

- **Depth 2:** only T1→T2 (word-scale locator → value multiplier) is a chain; the
  other four are independent leaves. Same-file serialization: T1/T5 touch
  exhibit_prose.py; T2/T3/T4/T6 touch kpi_prose_candidates.py — marked
  Independent: false so same-file tasks dispatch serially (dispatch constraint,
  not critical-path depth).
- **Part-1 scenarios (SHIPPED, PR #593 — not covered by THIS plan, not a drop):**
  the 15 Part-1 walking-skeleton scenarios shipped in the Part-1 plan
  (`docs/loom/plans/2026-07-19-8k-prose-kpi-intake-part-1.md`). Note: the two
  Part-1 scenarios that used "3.56 billion → 3560000000" as their example
  (Requirement "Mechanical prose candidate extraction" / "locate a prose-stated
  KPI"; Requirement "Anti-fabrication substring gate" / "normalized value need not
  be a substring") were implemented in Part 1 with PLAIN-integer test examples;
  Part 2's word-scale (T1/T2) is what makes those word-scale examples actually
  produce 3,560,000,000.
- **Part-3 scenarios (DEFERRED, next brief — not a drop):** the 12 lifecycle/
  hardening scenarios (dedup, 8-K/A supersession, anchor drift, concurrency,
  resource bounds, injection, propose-failure, human-edit-re-gate) remain in the
  change-folder for Part 3.
- **Number-format blind spots (Part-2 known-edge, note-and-defer — NOT silently
  dropped):** ranges with a magnitude ("40 to 45 billion" / "40-45 million");
  mixed comma+scale ("3,560 million"); currency-prefixed scale ("$3.56 billion" —
  monetary, should be skipped like Part-1's $-prefix rule, but that skip is not
  yet a scenario); repeated magnitude words. These are exercised opportunistically
  if cheap during T1–T4, otherwise flagged for a Part-2.5 / Part-3 hardening pass.
- **Non-adjacent bounding qualifier (declared deferral, T4 review round):** T4's
  `_detect_qualifier` is an ADJACENT-only lookback — the qualifier phrase must
  end immediately before the number. A qualifier separated from its figure by any
  intervening word ("up to a total of 45,000 vehicles", "approximately, or
  thereabouts, 931 warehouses") is NOT detected, and the figure commits as a bare
  equality — a real SEC-prose pattern, and the exact failure T4 exists to close,
  merely narrower. Widening the match to tolerate filler words trades this false
  negative for false positives (a qualifier belonging to a DIFFERENT clause
  landing inside the window), which is the worse error here: a fabricated bound
  is asserted, whereas a missed bound merely leaves the human confirmer reading
  the unannotated quote they already see. Deferred to the Part-2.5 / Part-3
  hardening pass, where the right fix is likely clause-aware rather than
  window-widening. Recorded via this designated channel per the T5 precedent.
- **Same-clause personal data survives the provenance window (declared deferral,
  T6 review round):** T6's `_context_window` is a fixed-WIDTH bound (160 chars,
  one shared budget). What it GUARANTEES: no paragraph-scale capture — the
  committed quote is a bounded contiguous slice, so personal data more than about
  one clause away from the figure cannot reach the durable store, which is the
  privacy failure the requirement names. What it does NOT guarantee: that the
  window is free of personal data. A name in the SAME clause as the figure sits
  inside it — verified during the T6 review round, "Jane Q. Ramirez earned a bonus
  and 1,576,000 full-time employees...", where the name starts 35 chars before the
  token and survives any window wide enough to be useful. The control is therefore
  PROXIMITY-DEPENDENT, and the docstrings say so rather than claiming containment
  they do not deliver. Widening or narrowing the window is NOT the fix: narrowing
  far enough to exclude a same-clause name also strips the subject and unit the
  human confirmer reads the number against, destroying the window's purpose while
  still failing on a name one word nearer. Excluding same-clause personal data
  needs entity recognition (NER), which this deliberately-mechanical, LLM-free
  layer does not do and should not grow — the values-and-coordinates-never-pass-
  through-an-LLM rail is the reason this layer stays mechanical. Deferred to the
  Part-2.5 / Part-3 hardening pass, where the right fix is an NER-based or
  clause-aware redaction pass over the committed quote, not a width tweak.
  Recorded via this designated channel per the T5 precedent.
