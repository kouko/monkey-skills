# ADR-0004: analysis-macro-regime — Phase 1 Per-Country Classifiers + Deferred Comparable Surface (Phase 2)

- **Status**: Accepted
- **Date**: 2026-05-02
- **Version target**: investing-toolkit v2.1.0 (Phase 1 implementation, ~5-6 weeks)
- **Predecessor PRs**: #176-#183 (v2.0.2 staging-tier rollout — provides cross-country symmetry on Layer 1; this ADR addresses analysis-layer follow-up)
- **Supersedes** (partially): v1.9.0 commit `13a76d1` — "Option B (hybrid): framework universal + calibration per-country" — preserved in spirit but completed differently

## Context

### Current state on `main` (post v2.0.2)

`analysis-macro-regime/scripts/regime_compose.py` implements a **single unified Investment Clock + Hedgeye GIP classifier** applied uniformly to 5 countries (US / JP / TW / KR / CN). It works as follows:

1. Per-country lookup tables (`GROWTH_KEYS`, `INFLATION_KEYS`) resolve which series in each `data-{country}` regime-pack carries the growth proxy and inflation proxy.
2. A single `classify_direction()` rule (latest vs trailing 3-mo avg, ±0.5σ band) classifies direction per country.
3. A universal `map_ic_quadrant()` maps `(growth_dir, inflation_dir)` to one of four IC quadrants.
4. A universal `map_gip_quad()` maps IC quadrant to Hedgeye GIP regime.
5. Scattered `if country == 'jp' / 'tw' / 'cn'` patches add country-specific notes (BOJ 2% target, NDC 五色 score commentary, CN 4-component dispersion overlay).

### What was already known and consciously chosen (v1.9.0)

Commit `13a76d1` (2026-04-18) introduced 5 per-country threshold reference files (`thresholds-{us,japan,taiwan,korea,china}.md`) and explicitly framed the architectural choice as **"Option B (hybrid)"**:

> "The IC+GIP framework is genuinely universal, but the CALIBRATION is not."

The commit message enumerated the per-country specificities that motivated the calibration files — JP r* ≈ -0.25%, TW 彈性定義 vs rigid 2%, KR Samsung+SK Hynix ~30% KOSPI weight, CN 3% as ceiling not target, etc. — and chose to express those as **documentation thresholds** rather than per-country code paths.

### What broke between intent and implementation

Two gaps emerged between v1.9.0 design and the v2.0.0 refactored code (current `main`):

**Gap 1 — calibration never plumbed into the classifier.** `thresholds-{country}.md` documents per-country `direction_band_stdev`, `inflation_target`, `policy_neutral_band`, `nairu`, structural overlays, etc. None of this is read by `classify_country()`. The classifier uses `DIRECTION_BAND_STDEV = 0.5` (one global constant) and the threshold docs sit as un-executed documentation.

**Gap 2 — the framework universality claim breaks down on examination.** v1.9.0 said the IC+GIP framework is universal. But:

- **CN current stance** (per `thresholds-china.md` 2026-Q2 vintage): "CPI 目标 = 2% (central tendency, 不是 ceiling) — 2025、2026 政府工作报告连续两年下调；从『防过热 ceiling』转为『促回升 中枢』". The IC reading "inflation rising → IC2 overheat → policy should tighten" inverts CN's actual policy stance, which is "PBOC 想要通脹從 0.5% 升回 2%; rising inflation = supportive recovery, not warning".
- **JP** post-2024 exit-deflation: 30 years of CPI ≤ 1% means IC's "growth↑ + inflation↑ = overheat" mistakenly flags BOJ's first sustained 2% reading as a threat rather than the policy success it represents.
- **TW** has its own pre-aggregated official regime classifier (NDC 五色景氣燈號 9-45 score with 5 colour bands and a published methodology revised 2024). Re-classifying NDC's output via IC 2x2 is information loss.
- **KR** and **US** fit IC/GIP reasonably well — these are the cases v1.9.0's universality claim is most defensible for.

### Concrete failure observed (v2.0.2 cross-layer testing)

Running `regime_compose.py` against the JP and TW regime-pack fixtures:

```
jp -> { growth_direction: 'flat', inflation_direction: 'rising',
        ic_quadrant: '2-overheat', confidence: 'low',
        notes: ['growth proxy missing for jp; defaulted to flat'] }
tw -> { growth_direction: 'flat', inflation_direction: 'flat',
        ic_quadrant: '1-recovery', confidence: 'low',
        notes: ['growth proxy missing for tw; defaulted to flat'] }
```

JP fails because pack.py never fetches `coincident-index` (the e-Stat client supports the preset but pack.py's preset list omits it). TW fails because `regime_compose.py`'s `GROWTH_KEYS["tw"]` looks for `cycle.signal / signal / ndc-signal / gdp` but TW's flatten emits `signal-score / ndc.signal-score / coincident-index / leading-index` — name mismatch.

These are surface symptoms. The deeper diagnosis is: **the unified classifier flattens per-country reality at the analysis layer, mirroring exactly the failure mode the v2.0.0 staging-tier work avoided at the data layer**.

### What changed in our thinking 2 weeks after v1.9.0

Two follow-on findings drive this ADR's design:

1. **Each of the 5 countries has its own official cycle classifier** that we currently ignore: NBER for US, ESRI 景気動向指数 for JP, NDC 五色 + 9 構成 for TW, KOSTAT 경기종합지수 for KR, NBS PMI for CN. v1.9.0 chose to put IC on top of all of them; with hindsight, leveraging the native classifiers is more honest.

2. **Convention-level uniformity > formal shared schema** (per `feedback_convention_over_shared_schema.md`, 2026-05-02). v2.0.2 codified this principle for the data layer. The same principle applies to the analysis layer: shared key names + shape conventions, but per-country logic free to differ on substance.

## Decision

**Adopt a 2-phase staging:**

- **Phase 1**: Decompose `analysis-macro-regime` into 5 per-country classifier modules (`classify_us / jp / tw / kr / cn`), each implementing its country's native framework. Each emits a rich `native_verdict` plus a thin convention-level metadata wrapper (`framework_used`, `indicators_used`, `confidence`, `provenance`). **No comparable surface schema is enforced in Phase 1.**

- **Phase 2** *(deferred)*: After Phase 1 ships and stabilises, observe the actual shape of 5 native verdicts in production memos. Then design the cross-country comparable surface bottom-up based on what each country naturally produces. Open a new ADR (provisionally ADR-0005) at that time.

### Why this staging

- **Comparable surface design is downstream of native verdict shape.** Designing the surface before knowing what 5 countries actually want to say is premature design. Reversing the order avoids it.
- **Each country has standalone value.** Single-country buy-side memos (the dominant memo workflow) read only one country's block. Phase 1 alone delivers the user-facing benefit even if Phase 2 is permanently deferred.
- **Phase 1 is 5 independent workstreams.** No coordination tax — each country PR can ship, be reviewed, and grounded independently.
- **Honors the user's stated priority.** "比起跨國可比，我更在乎個別國家的研究深度是否足夠" — Phase 1 maximises per-country depth without spending budget on cross-country surface that may be reshaped later.
- **Optionality preservation.** If Phase 2 reveals 5 native outputs are too heterogeneous for a meaningful unified surface, the finding itself is informative; we simply ship a thin direction-only surface or skip it. The cost is a short Phase 2 brainstorm, not 6 weeks of misdirected work.

## Phase 1 — Per-Country Classifiers

### Output schema (`schema_version: "2.0-phase1"`)

```json
{
  "schema_version": "2.0-phase1",
  "by_country": {
    "us": { "<country regime card>": "see below" },
    "jp": { "..." },
    "tw": { "..." },
    "kr": { "..." },
    "cn": { "..." }
  },
  "cross_country": null,
  "_legacy": {
    "by_country": {
      "us": {
        "growth_direction": "rising | falling | flat",
        "inflation_direction": "rising | falling | flat",
        "ic_quadrant": "1-recovery | 2-overheat | 3-stagflation | 4-reflation",
        "gip_regime": "quad1..quad4",
        "real_rates": "...",
        "confidence": "low | medium | high",
        "notes": ["..."]
      }
    },
    "note": "Phase 1 transition fallback; full legacy classify_country() output preserved here so existing memo / portfolio consumers continue to work. Computed via _legacy_ic.py. Will be removed at Phase 2 start or v2.2.0, whichever earlier."
  }
}
```

### Country regime card shape (convention-level uniformity)

```json
{
  "country": "tw",
  "framework_used": "NDC 五色景氣燈號 + 9 構成項目 + TSMC 集中度 overlay",
  "native_verdict": {
    "_schema": "country-specific (no enforced shape)",
    "...": "rich, country-native fields"
  },
  "indicators_used": ["signal-score", "signal-components", "leading-index",
                      "coincident-index", "dgbas.cpi-yoy"],
  "data_quality": {
    "missing": [],
    "stale": [],
    "_note": "string list of indicator IDs with issues"
  },
  "confidence": "high",
  "provenance": {
    "calibration_doc": "thresholds-taiwan.md",
    "calibration_vintage": "2026-Q1",
    "last_grounded": "2026-04-18 (v1.9.0)",
    "fetched_at": "2026-05-02T..."
  }
}
```

The 6 outer keys (`country`, `framework_used`, `native_verdict`, `indicators_used`, `data_quality`, `confidence`, `provenance`) are convention. The `native_verdict` interior is **deliberately schema-free** — each country owns its shape. Phase 2 may convert any of these inner fields to a comparable-surface contract later, informed by what each country actually emits.

### File structure

```
analysis-macro-regime/scripts/
├── regime_compose.py          # Phase 1: thin dispatcher + by_country aggregation + _legacy fallback wrapper
├── _legacy_ic.py              # Old classify_country() preserved verbatim; called only for _legacy block
├── classify_us.py             # New US engine
├── classify_jp.py             # New JP engine
├── classify_tw.py             # New TW engine
├── classify_kr.py             # New KR engine
├── classify_cn.py             # New CN engine
├── calibrations/
│   ├── __init__.py            # load_calibration(country) -> CountryCalibration
│   ├── us.yaml                # Plumbed from thresholds-us.md
│   ├── jp.yaml
│   ├── tw.yaml
│   ├── kr.yaml
│   └── cn.yaml
└── overlays/                  # (optional, populated by country PRs as needed)
    ├── __init__.py
    └── (country-specific structural overlays, e.g., tw_tsmc_concentration.py)
```

### Calibration plumbing

`calibrations/{country}.yaml` is a machine-readable extract of the corresponding `thresholds-{country}.md`. Each calibration file carries:

- Inflation target + framing type (`central_tendency`, `flexible`, `ceiling-deprecated`)
- Policy rate neutrality bands (real / nominal where applicable)
- NAIRU + tightness band (where applicable)
- Direction band σ multiplier (default 0.5; override per country if vol regime differs)
- Structural overlay names registered for that country
- Provenance (source doc, vintage, last_grounded date, authority)

A drift-detection test (added in PR-1) walks each `calibrations/{country}.yaml`'s `provenance.calibration_doc` reference and confirms the doc still exists. A second test verifies that any numeric field in the YAML is also mentioned somewhere in the corresponding markdown (best-effort regex; flag mismatches in CI).

### Per-country fetch additions

| Country | Currently in regime-pack | Addition needed | Implementation |
|---------|-------------------------|-----------------|----------------|
| **US** | FRED full coverage | None | n/a |
| **JP** | BOJ call rate, e-Stat (cpi/core-cpi/ip/unemployment/jgb10y), ECB JP real-yield, BOJ Tankan **inflation outlook only** | (a) e-Stat `coincident-index` + `leading-index` + `machine-orders` (presets exist in client, missing from pack.py preset list); (b) **Tankan business sentiment DI** (大企業 / 中小企業 × 製造業 / 非製造業 業況判斷 DI) — new fetch in `boj_client.py` | (a) one-line preset addition; (b) new `--tankan-business-di` flag + parser in `boj_client.py`; both wired into `pack.py pack_regime()` |
| **TW** | CBC, DGBAS, NDC (signal + signal-components includes TIER among 9 構成 + pmi-mfg + pmi-nmi + leading + coincident), statgov | None — `signal-components` already includes TIER (製造業營業氣候測驗點) per 2024 revision | n/a |
| **KR** | fdr_client KEYSTAT (54 indicators) | BOK 경제심리지수 (consumer + business confidence index, ESI) — fdr fallback if available, else flag for v2.2.0 ECOS API addition | Best-effort fetch in PR-5; if unavailable, classify_kr.py degrades gracefully |
| **CN** | NBS new-SPA (21 indicators), akshare PBOC/SHIBOR, FRED RMB, yfinance | **Credit impulse proxy** — computed from existing 社融存量 (TSF stock) + M2 stock available via akshare. New computation, not new fetch source | New `_compute_credit_impulse()` helper in `data-cn/scripts/pack.py`, wires into `regime-pack.cn_specific.credit_impulse` |

### Per-country classifier framework intent

Each country's `classify_X.py` is free to choose its native framework. Recommended starting points (subject to per-country PR refinement):

| Country | Native framework | Key inputs |
|---------|-----------------|------------|
| **US** | IC + GIP + Fed FIT (post-FAIT 2025) + real-rate decomposition (HLW / LM / SEP 4-tier) + yield curve | DGS10, T10YIE, DFII10, CFNAI, CPIAUCSL, FEDFUNDS |
| **JP** | BOJ stance + Tankan business sentiment + ESRI 景気動向指数 CI + deflation/inflation regime detection | Tankan DI, ESRI CI, e-Stat CPI, BOJ call rate, real yield from ECB |
| **TW** | NDC 五色景氣燈號 score-led + 9 構成 dispersion + TIER + TSMC concentration overlay + DGBAS CPI | signal-score, signal-components, leading-index, coincident-index, pmi-mfg, dgbas.cpi-yoy |
| **KR** | BOK 2% target alignment + KOSTAT 경기종합지수 동행지수순환변동치 + 가계부채 / GDP overlay + KOSPI concentration overlay | KEYSTAT cycle codes, BOK base rate, K401 CPI, household debt ratio |
| **CN** | PBOC reaction function (7-day 逆回購 primary policy rate post-2024-07) + credit impulse + 4-component dispersion + property cycle overlay | NBS industrial-yoy / retail-yoy / fai-yoy / services-yoy, CPI, PBOC 7D RR / LPR / RRR, credit impulse |

These frameworks are explicitly **not required to fit IC**. `classify_jp.py` may emit `regime_label: "exit_deflation_phase_1"` rather than `ic_quadrant: "2-overheat"`. `classify_tw.py` may lead with `signal_color: "綠"` rather than IC mapping. The shape of `native_verdict` is each country's call.

### Legacy IC fallback during Phase 1

To preserve backward compatibility for `report-equity-memo`, `report-portfolio-review`, and any external consumer expecting the v1.9.0 IC quadrant output, Phase 1 keeps `classify_country()` running as `_legacy_ic.py`. Its output populates the `_legacy.ic_quadrants` block. This block is explicitly marked deprecated and scheduled for removal at Phase 2 start or v2.2.0, whichever comes first.

### Phase 1 acceptance criteria

- All 5 `classify_X.py` modules ship and have ≥ 1 country-specific integration test green
- `regime_compose.py` produces the new schema; `cross_country: null` is hardcoded in Phase 1
- Each country's `confidence: 'low' (proxy missing)` cases observed during v2.0.2 testing must resolve to `'medium'` or `'high'` after Phase 1
- All 5 `calibrations/{country}.yaml` exist with non-empty provenance
- `_legacy.ic_quadrants` block matches output of pre-Phase-1 `classify_country()` byte-for-byte (regression test)
- New cross-layer integration tests in `tests/integration/test_cross_layer_chains.py` verify each country's classify_X handles its regime-pack fixture without crash

## Phase 2 — Deferred (Comparable Surface)

### What is explicitly deferred

- Cross-country comparable surface schema (whether IC quadrant, OECD CLI methodology, growth/inflation enums, or no surface at all)
- Cross-country consensus aggregation logic
- Choice between Route 1 / 4 / 5 (calibration-driven IC vs facade vs CLI+IC dual axis) discussed during this ADR's brainstorming

### Re-trigger conditions for Phase 2 brainstorm

Open Phase 2 brainstorm when **any one** of the following is observed:

1. Phase 1 has been on `main` for ≥ 4 weeks with no urgent fixes
2. ≥ 5 multi-country invocations of `/invest-macro` or `/invest-portfolio` have produced a regime card; we have actual `native_verdict` outputs to inspect
3. A buy-side memo workflow concretely needs cross-country alignment information that Phase 1's `_legacy.ic_quadrants` doesn't adequately provide
4. v2.2.0 release is being planned and Phase 2 fits the scope

If none of these triggers fires within 6 months of Phase 1 ship, evaluate whether Phase 2 is needed at all. It may turn out that single-country `native_verdict` blocks are sufficient for the buy-side workflow and a comparable surface is unnecessary.

### Phase 2 brainstorm scope (when triggered)

- Inspect 5 actual `native_verdict` shapes
- Identify common axes (likely: growth_direction enum, inflation_direction enum, confidence enum) and country-specific axes (TW signal_color, JP exit_deflation_phase, CN policy_framing, etc.)
- Decide: thin enum surface only / IC quadrant relabelled / OECD CLI methodology / multi-axis surface / no surface
- Write ADR-0005 documenting the choice

## Alternatives Considered

### Alternative A — fix v1.9.0 Option B's plumbing gap only (~2 weeks, "Route 1")

Keep the unified IC + GIP framework. Make `classify_country()` actually read `thresholds-{country}.md` calibrations. No per-country classifier modules.

**Rejected because**: Even with calibration, the framework's universality claim fails for CN (inflation framing inversion) and JP (exit-deflation 2% reading misclassified). Calibration can encode `inflation_framing: below_target_rising_is_positive`, but at that point the per-country logic is large enough that splitting into per-country modules is cleaner. Also, fitting TW's NDC 五色 (already a regime classifier) into IC's 2x2 throws away information that calibration can't recover.

### Alternative B — facade pattern: per-country engines + mandatory comparable surface (~6-7 weeks, "Route 4")

Each country has its own classifier; all are required to emit a comparable-surface contract (growth_dir, inflation_dir, ic_quadrant, framing) in addition to native verdict.

**Rejected because**: The comparable surface schema would have to be designed before knowing what 5 countries naturally produce. This is the premature design failure mode this ADR's 2-phase staging avoids. The facade can be added in Phase 2 if needed, with the benefit of seeing actual per-country outputs first.

### Alternative C — IC + OECD CLI dual axis + per-country overlay (~7-8 weeks, "Route 5")

Route 4 augmented with OECD CLI methodology as a second axis (cycle strength, normalised to 100=trend). Country-native overlays as a third tier.

**Rejected because**: (a) OECD CLI methodology has implementation risk (HP filter parameter choice, phase-shift correction, turning-point detection — non-trivial). A spike is needed to validate feasibility on our existing data before committing 7-8 weeks. (b) The CLI axis decision belongs in Phase 2 alongside the comparable surface decision, not in Phase 1 where it would constrain per-country classifier design.

### Alternative D — keep v1.9.0 Option B implementation as-is

Do nothing structural. Fix only the immediate two bugs (jp `coincident-index` not fetched + tw `signal` vs `signal-score` name mismatch).

**Rejected because**: This was the small-step option proposed at the start of the brainstorm. It would leave the IC framework's mismatch with CN current stance and JP exit-deflation regime unresolved. Acceptable as a hot-fix pre-Phase-1 if Phase 1 timing is tight, but not as the destination state.

## Implementation Plan

### PR-1 — Phase 1 infrastructure (~3-5 days)

- Create `_legacy_ic.py` by moving current `classify_country()` + helpers verbatim
- Refactor `regime_compose.py` to a thin dispatcher: parse `--input` → for each country, call `classify_X` if module exists else fall through to `_legacy_ic.classify_country`; aggregate `by_country`; populate `_legacy.ic_quadrants` from `_legacy_ic` results
- Define `_surface.py` with `CountryRegimeCard` dataclass (the 6-key convention envelope; `native_verdict` is `dict` with no schema)
- Add `calibrations/__init__.py` with `load_calibration(country)` reader
- Patch the TW name mismatch in `_legacy_ic.py`'s `GROWTH_KEYS["tw"]` (currently `cycle.signal / signal / ndc-signal / gdp` — none match TW's flatten output; add `signal-score`, `coincident-index`, `leading-index` so `_legacy` block produces non-degenerate output for TW)
- Add CI test asserting `_legacy.by_country` matches pre-PR-1 `regime_compose.py` output byte-for-byte on US / JP / KR / CN fixtures (TW is excluded from byte-for-byte because of the GROWTH_KEYS patch above; instead, TW gets a forward-looking assertion that `confidence` is now `medium` or `high`)
- Update SKILL.md with Phase 1 schema and `_legacy` deprecation notice

### PR-2 — US classifier (~1 week)

- `classify_us.py` implementing IC + Fed FIT + 4-tier real-rate (HLW / LM / SEP / NY Fed composite) + yield curve overlay, reading `calibrations/us.yaml`
- `calibrations/us.yaml` plumbed from `thresholds-us.md` (FIT post-FAIT, HLW r* 0.75%, LM r* 1.68%, SEP longer-run 1.0%, 4-tier real-rate band)
- US-specific integration test (existing US regime-pack fixture)
- US confirmed as Phase 1 baseline pattern

### PR-3 ~ PR-6 — JP / TW / KR / CN classifiers (each ~1 week, 4 worktrees in parallel)

Each PR includes:

- `classify_X.py` implementing the country's native framework (per the table above)
- `calibrations/{country}.yaml` plumbed from `thresholds-{country}.md`
- Necessary fetch additions in the corresponding `data-{country}/scripts/`:
  - **PR-3 JP**: `boj_client.py` `--tankan-business-di` flag + `pack.py` wires Tankan business DI, e-Stat coincident/leading/machine-orders
  - **PR-4 TW**: no fetch additions (already complete); pure analysis-layer work
  - **PR-5 KR**: best-effort BOK 경제심리지수 via fdr_client; if not retrievable, `classify_kr.py` proceeds with the 54-indicator KEYSTAT subset already in regime-pack and records `confidence: "medium"` with a note that ESI is missing — does NOT fail the country chain
  - **PR-6 CN**: `data-cn/scripts/pack.py` `_compute_credit_impulse()` helper from akshare TSF + M2
- Country-specific integration test against existing regime-pack fixture
- Short grounding research note (delta refresh of `thresholds-{country}.md` per `recalibration-protocol.md`'s partial-recalibration template)
- Update of `tests/integration/test_cross_layer_chains.py::test_chain_country_regime_to_macroregime` parametrized case to assert `confidence != 'low'` for that country

### PR-7 — cleanup + ADR-0004 acceptance closure (~3-5 days)

- Verify all 5 `classify_X.py` shipped; remove `_legacy_ic.py` fallback path from `regime_compose.py` (block is set to `null` rather than removed entirely — schema-stable for downstream)
- Bump plugin.json to v2.1.0
- Update SKILL.md, README.md, CHANGELOG.md, ROADMAP.md
- Mark this ADR as "Implemented" (status update only)
- Open Phase 2 placeholder issue with re-trigger condition checklist

PR sequence: PR-1 → PR-2 → (PR-3 / 4 / 5 / 6 in parallel worktrees) → PR-7

## Consequences

### What we gain

- **Each country's analysis is researched and implemented at its own native depth**, leveraging the country-specific calibration knowledge that v1.9.0 documented but never executed
- **The `thresholds-{country}.md` files become the source-of-truth reference for `calibrations/{country}.yaml`** — drift between docs and code becomes a CI-detectable bug
- **Per-country development is parallelisable**, no coordination tax; each country PR is independently reviewable / groundable / shippable
- **The 4 broken cross-layer chain tests on jp/tw observed in v2.0.2 fixture-replay get resolved** as a side effect (Phase 1 acceptance criterion)
- **Single-country buy-side memos benefit immediately** without waiting for cross-country surface design
- **Comparable surface design moves from "premature" to "informed by data"** — Phase 2 brainstorm has 5 actual native verdicts to look at

### What we accept

- **5-6 weeks of work before any cross-country dashboard improvement.** Mitigated by `_legacy.ic_quadrants` block continuing to exist during Phase 1
- **Schema breaks for downstream consumers** that read `regime_compose.py` output directly (currently flat `countries.{cc}.ic_quadrant`; new schema is `by_country.{cc}.native_verdict.*`). Migration path: consumers continue reading `_legacy.ic_quadrants` until Phase 2; new consumers read `by_country` natively
- **Possible Phase 2 finding that 5 native outputs are too heterogeneous** for a meaningful unified surface. This is acceptable — the finding itself is informative and the user has explicitly stated cross-country comparability is a lower priority than per-country depth
- **Calibration YAML drift risk** vs threshold MD docs. Mitigated by CI drift-detection test in PR-1
- **Deferred Phase 2 may end up never-implemented.** This is acceptable — Phase 1 stands on its own value. The IC + CLI architectural debate is parked in this ADR, not lost

### Risks

- **Per-country classifier explosion of LOC**: each country PR may push 400-600 LOC + tests + research note. Total Phase 1 footprint may be ~3000 LOC vs current ~400 LOC. Mitigated by per-country reviewability and the fact that each country's logic is genuinely independent
- **`thresholds-{country}.md` recalibration triggers may surface during Phase 1**: per `recalibration-protocol.md`, FOMC SEP, BOJ 展望, CBC quarterly statement, BOK semi-annual, 政府工作报告 may all release during the 5-6 week window. Each PR should do its country's partial recalibration as part of the work
- **JP Tankan business DI fetch is non-trivial**: BOJ Time-Series API has Tankan series codes that aren't documented as cleanly as the inflation outlook. PR-3 may need to spike on Tankan series resolution before completing the classifier
- **CN credit impulse computation has methodological choices** (TSF stock vs flow, which window, which lag). PR-6 should ground the choice against published Chinese-language sources (CICC / CITIC / 第一財経) with primary sourcing

## Open Questions (deferred to PR-3-6 implementation)

1. **JP Tankan series code resolution**: Tankan business DI for 大企業/中小企業 × 製造業/非製造業 — confirm series codes via BOJ Time-Series API documentation before PR-3 starts. If BOJ Time-Series API doesn't expose Tankan business DI cleanly, fall back to BOJ's published CSV/XLSX download (the same pattern `boj_client.py` already uses for `tankan_inflation_outlook`). Tankan is BOJ-published only — not republished by e-Stat or ESRI.

2. **KR ECOS vs fdr trade-off**: 경제심리지수 (ESI) ideal source is BOK ECOS API which requires a free API key. Phase 1 PR-5 attempts fdr fallback; if quality unacceptable, defer ESI integration to v2.2.0 with explicit ECOS key acquisition.

3. **CN credit impulse methodology choice**: TSF flow / GDP rolling 12m vs TSF stock yoy growth. CICC and CITIC publish slightly different definitions. Lock methodology in PR-6 with a `references/credit-impulse-methodology.md` note.

4. **(Resolved in PR-1)** TW `_legacy_ic.py` GROWTH_KEYS patch — see PR-1 deliverables. The byte-for-byte regression test scope was narrowed to US / JP / KR / CN to accommodate this patch.

5. **Calibration drift CI rigour**: the regex-based "numeric value in YAML must appear in MD" check may produce false positives. Acceptable initial implementation; refine if noisy.

## See Also

- [ADR-0001](0001-data-analysis-report-layers.md) — three-layer split (data / analysis / report)
- [ADR-0002](0002-layer-1-staging-tier-normalization.md) — staging-tier model at data layer (this ADR's analysis-layer counterpart)
- [ADR-0003](0003-t3-financial-statement-normalization.md) — T3 financial statement normalization
- [`docs/normalization-contract.md`](../normalization-contract.md) — convention-level uniformity principle
- `feedback_convention_over_shared_schema.md` (memory) — principle this ADR extends from data layer to analysis layer
- v1.9.0 commit `13a76d1` — original "Option B (hybrid)" design decision this ADR partially supersedes
- `skills/analysis-macro-regime/references/thresholds-{us,japan,taiwan,korea,china}.md` — per-country calibration source-of-truth
- `skills/analysis-macro-regime/references/recalibration-protocol.md` — partial-recalibration trigger and template referenced by PR-3-6
- `skills/analysis-macro-regime/references/investment-clock-cheatsheet.md` — IC + GIP framework reference (preserved in `_legacy_ic.py`)
