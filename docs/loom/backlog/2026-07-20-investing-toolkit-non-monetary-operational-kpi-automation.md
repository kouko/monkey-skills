---
name: 2026-07-20-investing-toolkit-non-monetary-operational-kpi-automation
description: investing-toolkit 非金錢營運 KPI 自動化 (2026-07-19..20; Route B SHIPPED; ARC PIVOTED to a narrative-evidence layer; XBRL Route A demoted)
status: OPEN
---

- **Pivot evidence (2026-07-20):** a live probe of the 7 mega-caps showed the
  XBRL footprint allowlist yields ~0 real operational KPIs for big tech (only
  traps: AMZN mwh hedge-notional, TSLA 20M pay-package milestone); the real
  operational KPIs live in 8-K earnings-release PROSE — which Route B's TABLE
  walker AND the bulk-narrative layer both drop (META Family DAP, GOOGL MAU,
  TSLA deliveries). An agent-project prior-art survey confirmed no popular OSS
  project does verbatim-anchored + longitudinal + human-confirm grounding — that
  triad is our differentiator. Research: `docs/loom/research/2026-07-19-*.md`.
- **Narrative-evidence arc — Slice A = "Route B for prose" (3-part split, user-approved):**
  - **Part 1 SHIPPED (#593, 2.28.0):** mechanical prose KPI producer —
    `exhibit_prose.py` (surface + `--locate`) + `kpi_prose_candidates.py`
    (propose/gate/confirm/commit_to_store/intake) → prose datum with verbatim
    quote + `prose:{start}-{end}` anchor into the byte-unchanged tier-① store.
    Change-folder `docs/loom/2026-07-19-8k-prose-kpi-intake/`, plan
    `docs/loom/plans/2026-07-19-8k-prose-kpi-intake-part-1.md`. NOT yet
    SKILL-wired (foundational machinery).
  - **Part 2 SHIPPED (this PR, 2.29.0) — number robustness:** word-scale
    (locator absorbs the magnitude word; value multiplier via `Decimal`, so META
    DAP "3.56 billion" is 3,560,000,000 not 3.56), one consistent normalization
    (nbsp/thin-space grouping, full-width + Arabic-Indic digits, full-width
    comma/period, curly quotes — every fold length-preserving so offsets and the
    anchor survive), date/fiscal-period label rejection, bounding-qualifier
    metadata, bounded provenance context window. Plan
    `docs/loom/plans/2026-07-20-8k-prose-kpi-intake-part-2.md`.
    **Three fabrication bugs of one class were caught in review** — a token whose
    anchor holds LITERALLY while being semantically meaningless (nbsp fusing two
    unrelated numbers; magnitude absorption reopening the period-label filter;
    nbsp after a comma-grouped number). The lesson for Part 3: `text[start:end]
    == token` is guaranteed by construction and therefore proves nothing about
    whether the match is semantically right. Two declared limits remain in the
    plan's §Notes (non-adjacent qualifier; same-clause PII proximity).
  - **Part 2 next-touch (2🟢 from whole-branch review, logged not fixed):**
    `_bounded_quote` re-anchors on the FIRST occurrence of a repeated token, so
    the re-clamped window can center on an occurrence other than the one
    `char_offset_span` names (still grounded, no fabrication); and
    `commit_to_store` never invokes `passes_substring_gate` — the gate is a
    predicate callers must remember to call rather than a barrier on the commit
    path (pre-existing from Part 1). Make it structural in Part 3.
  - **Part 3 must carry a SURFACE-VERSION marker.** Part 2 changed how the
    canonical prose surface is produced (newline fold + char folds), i.e. a
    silent surface-version bump. An audit confirmed this is SAFE today — no
    consumer re-derives the surface to re-check a stored offset, no committed
    fixture carries a `prose:` anchor, and the route is not SKILL-wired, so
    nothing is stored in anger. But the spec's own MUST (change-folder
    `spec.md:149-165`: store a content hash + flattener version, re-verify
    `quote == canonical_text[start:end]` on read) is exactly the mechanism that
    would have made this unsafe — and it is the one deferred to Part 3. When
    Part 3 builds the re-verifier it needs a policy/surface version marker, or a
    live store written under an older surface will drift undetectably.
  - **Part 2 next-touch, two more of the recurring class (🟢, logged not fixed):**
    the `--locate` CLI fuses a U+2028-separated file (a public entry point whose
    documented contract is canonical input, so input-conditional); and
    `<style>`/`<script>` text is not suppressed by the walker, so CSS/JS numerals
    enter the candidate stream (`10.5pt`, `720px`) — PRE-EXISTING at origin/main,
    0 of 4 real filings checked carry either tag.
- **investing-toolkit test-suite hygiene (found 2026-07-20, unrelated to the
  prose arc):** `test_pack_schemas.py::test_pack_live_output_matches_schema[kr-
  snapshot]` fails on `ModuleNotFoundError: No module named 'edgar'`
  (`sec_edgar_client.py:801`) — a MISSING OPTIONAL DEPENDENCY, not a network
  failure, but it is hidden by the `-m "not network"` deselect everyone runs. If
  the deselect list and the optional-dep set drift, this fails for a reason
  nobody is watching. Fits the repo's existing pytest-config-drift gotcha.
  - **Part 3 (next brief) — lifecycle/hardening:** table-vs-prose + prose-vs-prose
    + order-independent dedup, 8-K/A supersession, anchor drift (hash+version
    re-verify), concurrency scope + batch atomicity, resource bounds/ReDoS,
    prompt-injection, propose-failure state, human-edit-re-gate. 12 deferred
    scenarios in the change-folder §Notes.
  - **SKILL wiring** (analysis-kpi SKILL.md CLI-reference + a user-facing prose
    intake workflow) — pending; do when the capability is user-ready.
  - **Slice B (later) — curated narrative PASSAGES → memo** (relevance/taste
    layer over the existing bulk narrative text).
  - **Slice C — KPI observation history (US lane)** (plan
    `docs/loom/plans/2026-07-22-kpi-observation-history.md`, brief
    `docs/loom/specs/2026-07-20-kpi-observation-history.md`) — shipped shape:
    store enumeration; period identity = raw `(start,end)` pair with fiscal
    labels as analysis coordinates; write-time integrity stamp (hash of the
    anchored span + surface version); `history`/coverage read across filings,
    disagreement flagged. **Retention DROPPED** — the earlier ten-year-lookback
    "industry norm" framing was unevidenced (CFA sets no lookback window;
    practitioner guidance clusters 3–5yr; 会社四季報 prints 5 periods by default;
    vendors sell depth as product tiers — no consensus to conform to).
    **Tearsheet
    DEFERRED** — no shipped public format exists for "one company, many
    operating KPIs, many years", and the prose lane is not yet user-invocable.
  - **Slice C deferred / future items:**
    - Conflict-resolution policy (B) — different source types, same period:
      audited-wins auto-resolution, **data-gated** (needs a per-point
      source-TYPE field + a second populated lane before it can resolve on
      anything; today T6 surfaces a (B)-shaped conflict as `disagreement=True`).
    - Dedup-key migration — moving store identity to the `(start,end)` date
      pair at the write-side dedup layer (the 5-tuple still carries the string
      `period`); user-gated, backfill-blocked by first-record-wins.
  - **Pre-existing defects found during the Slice C recon (2026-07-22) — log,
    not fixed here (not ours, out of scope):**
    - `comps_compute._concept_fy_end` (`comps_compute.py:206-207`) hardcodes
      `fiscal_year_ends`, so a TW pack (which emits `periods`) returns `None`
      every time — provenance column silently blank, no error.
    - Values/periods can pair WRONGLY on a mid-series gap: `_extract` skips
      missing labels instead of appending `None`, then `_meta` slices
      `periods[: len(revenue)]`, truncating periods from the END
      (`pack_jp.py:232-236`/`:274`, `pack_tw.py:275`, `pack_kr.py:325`).
    - JP EDINET Tier-A canonical is an empty stub (`pack_jp.py:463-478`) — the
      better source produces the emptier canonical.
    - TW canonical blocks are absent from `tw-schema-memo-fetch.json` entirely.
    - The four `_YF_LABEL_MAP*` copies differ in content, so ADR-0001's CI MD5
      drift check covers none of them.
- **Route A — XBRL non-monetary footprint/capacity allowlist — DEMOTED/PARKED**
  (serves retail/REIT/utility filers, NOT big tech; only pick up if the user's
  portfolio needs those names). Census outcome — the only viable territory is a
  physical-footprint / capacity allowlist keyed on standard (not extension)
  concepts:
  - `us-gaap:NumberOfStores` — COST, CVS
  - `us-gaap:NumberOfRestaurants` — MCD
  - `us-gaap:NumberOfRealEstateProperties` — O (clean total), PLD
    (dimensioned); AMT is extension-only (excluded from the standard-concept
    allowlist)
  - utility generating capacity in MW — NEE, DUK, SO
  - program-unit counts — BA
  THREE mandatory defenses, each required before ANY allowlist promotion:
  (a) per-filer semantic verification — a standard concept can still be the
  wrong quantity (SBUX `NumberOfStores`=113 is a sub-brand trap, not the
  system total); (b) value-sanity gate — reject corrupted magnitudes (MET
  claims-count tagged 3,360 in one filing, 308B in another — a ~10⁸ jump
  that must fail loud, not pass through); (c) QName-keyed classification,
  never unit-string — 7/15 energy/utility filers tag hedge-notional
  bbl/mcf/MWh with units identical to real production volumes, so the unit
  string cannot disambiguate; classify on the concept QName. Route A DOES
  carry the per-point `currency` ISO-code passthrough rider (gate already
  reads it, drops it before emission — CSV/feed currently carries
  implicit-USD only) since Route A touches XBRL feed emission.
- FAR-PARKED, out of scope for BOTH routes: pre-2003 KPI extraction from
  10-K prose. Before the 2003-03 earnings-8-K furnishing mandate (then
  Item 12; renumbered Item 2.02 in 2004-08) there is no
  structured earnings-release exhibit to parse (Route B) and no XBRL fact to
  allowlist (Route A) — recovering those KPIs is a separate 10-K-text
  problem, not a variant of either arc here.
