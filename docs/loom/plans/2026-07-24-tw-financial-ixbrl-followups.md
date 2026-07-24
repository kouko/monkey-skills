# Plan: TW financial iXBRL 2.31.0 post-ship follow-ups

Source brief: docs/loom/specs/2026-07-24-tw-financial-ixbrl-followups.md
Total tasks: 8
Critical-path depth: 3 (≤5)
Execution order: parallel-where-possible (T1–T6 one level, T7 rides last, T8 dogfood after T7)
Plan-document-reviewer verdict: PASS (2026-07-24, round 2 — 14/14 checks)

## Notes

- **PIN — marker shape (transcribe VERBATIM, from `dcf_compute.py:427-442`)**:
  the financial-sector dcf.json is a flat object with exactly these keys:
  `ticker`, `not_applicable: "financial-sector"`, `reason` (prose string),
  `_provenance`. It omits `intrinsic_value`, `verdict_thresholds`,
  `sensitivity_table`, `current_price`, `margin_of_safety_base`.
- **PIN — N/A render wording (transcribe VERBATIM where the pin phrase
  appears; surrounding prose adapts to each surface)**: the section heading /
  label phrase is `DCF: N/A — financial sector`; the semantics sentence is:
  "`dcf.json` carries `not_applicable: \"financial-sector\"`;
  intrinsic-value and verdict fields are intentionally absent — state the
  `reason` string verbatim, do not fabricate a verdict, and treat
  CHK-THX-007 as vacuously satisfied (no `verdict_thresholds` to
  recompute). Frontmatter `intrinsic_mid` is `null` with this reason, never
  a silent default." Tasks T1/T2/T3 each transcribe from THIS pin, never
  from each other.
- Producer `dcf_compute.py` is OUT OF SCOPE (brief §Out of Scope) — no task
  touches it.
- T6 outcome rule (brief §Decision): if the UTF-8-first count assertion
  fails for any fixture, that is a surfaced FINDING (report, stop) — never
  silently re-baseline `EXPECTED_FACT_COUNTS`.
- Test suite command: `python3 -m pytest investing-toolkit/tests/` from repo
  root (963 passing at branch point).
- Kickoff sweep (2026-07-24): NO one-way-door decisions found — every task
  is reversible prose/refactor/test/version work inside versioned plugins;
  no researchable forks left open (wording + marker shape pinned above,
  dogfood ticker pinned to 2882.TW, versions pinned in T7). Nothing to
  brief; two-way-door choices route to ## Decision Log during SDD.
  (Post-PASS amendment: this Notes entry + the T7 Module anchor + T8 are
  the round-2 revisions the reviewer PASSed; this line itself is additive
  and schema-safe — re-review skipped.)

## Decision Log

- **T8 dogfood-triggered fix (2026-07-24, two-way door, agent-decided):**
  the 2882.TW render dogfood surfaced a cold-writer divergence — the seed
  contract / SKILL.md wording "state the reason next to `intrinsic_mid`"
  was readable as a frontmatter neighbor, and the blind writer invented an
  `intrinsic_mid_reason` frontmatter field against the fixed 8-field schema.
  Resolved by clarifying both surfaces (commit 384d8b3c) to route the reason
  into the §DCF section body and keep the frontmatter schema fixed. Reversible
  prose edit inside this arc's own N/A-render scope; logged not briefed.

## Task 1 — phase4-seed-contract N/A branch

- Description: Define the `not_applicable` marker semantics in the Phase-4
  seed contract: add an explicit N/A branch to the `verdict_thresholds.rule_verdict`
  clause (currently "binding-or-gated", reads as "when provided") stating the
  marker shape (per PIN) and that CHK-THX-007 is vacuously satisfied.
- Module: investing-toolkit/skills/report-equity-memo
- Files touched: investing-toolkit/skills/report-equity-memo/references/phase4-seed-contract.md
- Context paths:
  - investing-toolkit/skills/report-equity-memo/references/phase4-seed-contract.md (lines 18–29)
  - investing-toolkit/skills/analysis-dcf/scripts/dcf_compute.py (lines 419–442, read-only)
- Acceptance:
  - RED: `grep -c 'not_applicable' investing-toolkit/skills/report-equity-memo/references/phase4-seed-contract.md` → 0 today
  - GREEN: the grep hits ≥1; the N/A branch names all four marker keys from the PIN and the CHK-THX-007 vacuous-satisfaction rule
- External surfaces: none (markdown contract prose)
- Dependencies: none
- Independent: true
- Brief item covered: "`references/phase4-seed-contract.md`: marker semantics defined — `rule_verdict` N/A branch, CHK-THX-007 explicitly vacuous" (Smallest End State item 1)

## Task 2 — report-equity-memo SKILL Phase 3/4 branch

- Description: Add the orchestrator-side `not_applicable` branch to
  report-equity-memo SKILL.md: after Phase 3 runs `dcf_compute`, if dcf.json
  carries the marker (per PIN), Phase 4 frontmatter sets `intrinsic_mid: null`
  with the stated reason (never a silent default), and the Phase-4 seed
  notes DCF is N/A so investing-team renders the N/A section.
- Module: investing-toolkit/skills/report-equity-memo
- Files touched: investing-toolkit/skills/report-equity-memo/SKILL.md
- Context paths:
  - investing-toolkit/skills/report-equity-memo/SKILL.md (Phase 3 gate ~line 344, Phase 4 frontmatter clause ~line 496)
- Acceptance:
  - RED: `grep -c 'not_applicable' investing-toolkit/skills/report-equity-memo/SKILL.md` → 0 today
  - GREEN: the grep hits ≥1 in both the Phase-3 and Phase-4 regions; the pin phrase `DCF: N/A — financial sector` appears; SKILL.md body stays within the repo token cap
- External surfaces: none (skill prose)
- Dependencies: none
- Independent: true
- Brief item covered: "report-equity-memo/SKILL.md Phase 3/4: on marker, frontmatter `intrinsic_mid: null` is stated (with reason), not silently defaulted" (Smallest End State item 1)

## Task 3 — investing-team protocol N/A render

- Description: Add the `not_applicable` render branch to the investing-team
  memo protocol §DCF and its memo template: when the seeded dcf.json carries
  the marker (per PIN), the memo renders a `DCF: N/A — financial sector`
  section quoting the `reason` string; the rule_verdict adopt/Deviation-Block
  flow (protocol lines ~318–332) is explicitly bypassed in this branch (no
  fabricated verdict).
- Module: domain-teams/skills/investing-team
- Files touched: domain-teams/skills/investing-team/protocols/deep-equity-research-memo.md
- Context paths:
  - domain-teams/skills/investing-team/protocols/deep-equity-research-memo.md (§DCF ~99–106, rule_verdict ~318–332, template ~468–469)
- Acceptance:
  - RED: `grep -c 'not_applicable' domain-teams/skills/investing-team/protocols/deep-equity-research-memo.md` → 0 today
  - GREEN: the grep hits ≥1; the pin phrase `DCF: N/A — financial sector` appears in both §DCF prose and the template region
- External surfaces: none (protocol prose)
- Dependencies: none
- Independent: true
- Brief item covered: "domain-teams …/deep-equity-research-memo.md (+ template): §DCF renders 'DCF N/A — financial sector' with the reason string; Deviation Block not required in the N/A branch" (Smallest End State item 1)

## Task 4 — canonical.py meta-block helper + citation cleanup

- Description: Extract the triplicated `sorted→values→meta` block
  (`twse_ixbrl_canonical.py:231-244`, `:449-462`, `:700-713`) into one shared
  helper parameterized by `source_label` / `concept` / value extractor /
  extra meta keys; replace the 4 dead `scratchpad/fh-measurement*` comment
  citations (lines 391, 569, 647, 654) with the operative measurement fact
  stated inline (or trim if the code now self-documents).
- Module: investing-toolkit/skills/data-markets
- Files touched: investing-toolkit/skills/data-markets/scripts/twse_ixbrl_canonical.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/twse_ixbrl_canonical.py
  - investing-toolkit/tests/ (existing canonical tests, read-only)
- Acceptance:
  - RED: N/A — pure refactor under existing coverage (tdd-iron-law §When NOT to Use); diagnostic RED: the meta-block pattern occurs at 3 sites and `grep -c 'scratchpad' …/twse_ixbrl_canonical.py` → 4 today
  - GREEN: full suite passes (`python3 -m pytest investing-toolkit/tests/`); the meta-construction lives in exactly one helper (the three call sites contain no inline meta-dict literal); scratchpad grep → 0
- External surfaces: none (internal refactor, stdlib only)
- Dependencies: none
- Independent: true
- Brief item covered: "extract one shared meta-block helper in `twse_ixbrl_canonical.py` (3 sites)" + "the 5 dead scratchpad citations replaced by the operative measurement fact inline" (Smallest End State items 2 & 4 — canonical.py share)

## Task 5 — notes.py group+select helper + citation cleanup

- Description: Extract the triplicated by-concept grouping + `_select_current_fact`
  block (`twse_ixbrl_notes.py:146-154`, `:253-267`, `:339-347`) into one
  shared helper parameterized by the `label` formatter (the fh variant keeps
  its per-company outer loop and calls the helper inside it); replace the
  dead citation at line 217 with the operative fact inline.
- Module: investing-toolkit/skills/data-markets
- Files touched: investing-toolkit/skills/data-markets/scripts/twse_ixbrl_notes.py
- Context paths:
  - investing-toolkit/skills/data-markets/scripts/twse_ixbrl_notes.py
  - investing-toolkit/tests/ (existing notes tests, read-only)
- Acceptance:
  - RED: N/A — pure refactor under existing coverage; diagnostic RED: grouping pattern at 3 sites and `grep -c 'scratchpad' …/twse_ixbrl_notes.py` → 1 today
  - GREEN: full suite passes; grouping+selection lives in exactly one helper; scratchpad grep → 0
- External surfaces: none (internal refactor, stdlib only)
- Dependencies: none
- Independent: true
- Brief item covered: "one group+select helper in `twse_ixbrl_notes.py` (3 sites)" + citation cleanup (Smallest End State items 2 & 4 — notes.py share)

## Task 6 — decode-coverage fact-count test

- Description: Add a test asserting whole-file fact-count equality when
  fixtures are decoded through the production `decode_ixbrl_document`
  (UTF-8-first, big5hkscs fallback) instead of the legacy
  `big5hkscs, errors="replace"` path used at
  `test_twse_ixbrl_fixtures.py:76-81`. Keep the existing legacy-path test;
  the new test covers ALL fixtures with stored expected counts (financial +
  ci). Per plan Notes: a count mismatch is a surfaced finding, not a
  re-baseline.
- Module: investing-toolkit/tests
- Files touched: investing-toolkit/tests/data/test_twse_ixbrl_fixtures.py
- Context paths:
  - investing-toolkit/tests/data/test_twse_ixbrl_fixtures.py (decode + comment, lines 70–81)
  - investing-toolkit/skills/data-markets/scripts/twse_ixbrl_parser.py (`decode_ixbrl_document`, read-only)
  - docs/loom/memory/tw-financial-ixbrl-served-utf8-despite-big5-declaration.md (rationale)
- Acceptance:
  - RED: the new test does not exist (collection count for `decode_ixbrl_document`-based count test = 0)
  - GREEN: new test collected and passing for every fixture with an expected count; full suite passes
- External surfaces: none (offline fixtures, stdlib decode)
- Dependencies: none
- Independent: true
- Brief item covered: "new test asserting whole-file fact-count equality under the production `decode_ixbrl_document` (UTF-8-first)" (Smallest End State item 3)

## Task 7 — version bumps + manifest sync

- Description: Bump investing-toolkit to 2.31.1 and domain-teams to 5.10.1
  in each plugin's `.claude-plugin/plugin.json`; add CHANGELOG entries per
  each plugin's existing convention; mirror codex manifests via
  `python3 scripts/sync_codex_manifests.py investing-toolkit` (and for
  domain-teams if it has a codex mirror — check, don't assume); verify any
  marketplace.json / pyproject version references per repo convention
  (grep before editing; never hand-edit `.codex-plugin/plugin.json`).
- Module: investing-toolkit/.claude-plugin/plugin.json (coordination anchor; sibling coordination files listed in Files touched)
- Files touched: investing-toolkit/.claude-plugin/plugin.json, investing-toolkit/CHANGELOG.md, domain-teams/.claude-plugin/plugin.json, domain-teams/CHANGELOG.md (if present), investing-toolkit/.codex-plugin/plugin.json (via sync script only)
- Context paths:
  - scripts/sync_codex_manifests.py
  - investing-toolkit/CHANGELOG.md
- Acceptance:
  - RED: `grep -m1 version investing-toolkit/.claude-plugin/plugin.json` → 2.31.0 today (domain-teams → 5.10.0)
  - GREEN: versions read 2.31.1 / 5.10.1; sync script run clean (no diff on re-run); CHANGELOG entries present
- External surfaces: none (repo metadata; sync via committed script)
- Dependencies: Tasks 1, 2, 3, 4, 5, 6 complete first
- Independent: false
- Brief item covered: "Version bumps: investing-toolkit → 2.31.1, domain-teams → patch bump; codex manifests via sync script" (Smallest End State item 5)

## Task 8 — live e2e memo dogfood (financial ticker)

- Description: Run the report-equity-memo pipeline end-to-end for one real TW
  financial ticker (2882.TW 國泰金) against the branch's updated SKILL /
  contract / protocol files, fetching live MOPS data, and verify the memo
  renders the N/A branch instead of silently omitting valuation. This is a
  verification task: it produces a dogfood report (memo artifact + findings),
  not production code. Any failure to render the pin phrase is a surfaced
  finding routed back to Tasks 1–3, not patched inline.
- Module: investing-toolkit/skills/report-equity-memo
- Files touched: none (verification run; artifacts land in scratchpad, not the repo)
- Context paths:
  - investing-toolkit/skills/report-equity-memo/SKILL.md (as updated by Task 2)
  - investing-toolkit/skills/report-equity-memo/references/phase4-seed-contract.md (as updated by Task 1)
  - domain-teams/skills/investing-team/protocols/deep-equity-research-memo.md (as updated by Task 3)
- Acceptance:
  - RED: baseline (pre-Tasks-1–3 behavior): a financial-ticker memo run yields frontmatter `intrinsic_mid` silently null with NO explanation and no `DCF: N/A — financial sector` section
  - GREEN: the dogfood memo for 2882.TW contains the pin phrase `DCF: N/A — financial sector` quoting the dcf.json `reason` string, and frontmatter states `intrinsic_mid: null` with the reason
- External surfaces: live TWSE MOPS fetch (network required; C→A report fallback already shipped in 2.31.0); no repo file writes
- Dependencies: Tasks 1, 2, 3, 7 complete first
- Independent: false
- Brief item covered: "Final verification includes one live e2e memo dogfood on a financial ticker (e.g. 2882) to see the 'DCF N/A' render actually appear" (Decision section)
