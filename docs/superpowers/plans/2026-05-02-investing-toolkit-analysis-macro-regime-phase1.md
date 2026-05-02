# investing-toolkit v2.1.0 — analysis-macro-regime Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Decompose `analysis-macro-regime/scripts/regime_compose.py` from a single unified IC + Hedgeye GIP classifier into 5 per-country classifier modules (`classify_us / jp / tw / kr / cn`), each implementing its country's native framework. Defer cross-country comparable surface to Phase 2.

**Architecture:** Per-country modules emit rich `native_verdict` blocks with convention-level uniform envelope (`country / framework_used / native_verdict / indicators_used / data_quality / confidence / provenance`). Legacy IC fallback preserved during transition. See [ADR-0004](../../../investing-toolkit/docs/adr/0004-analysis-macro-regime-phase1-per-country-classifiers.md).

**Tech Stack:** Python 3.11+, pytest, PyYAML, uv, pre-existing investing-toolkit data clients (BOJ/e-Stat/CBC/DGBAS/NDC/fdr/akshare/FRED).

---

## File Structure

### Created
- `investing-toolkit/skills/analysis-macro-regime/scripts/_legacy_ic.py` — preserved old `classify_country()` + helpers; called only by `regime_compose.py` for `_legacy.by_country` fallback block
- `investing-toolkit/skills/analysis-macro-regime/scripts/_surface.py` — `CountryRegimeCard` dataclass + `Phase1Output` schema definition
- `investing-toolkit/skills/analysis-macro-regime/scripts/classify_us.py` — IC + Fed FIT + 4-tier real-rate + yield curve overlay
- `investing-toolkit/skills/analysis-macro-regime/scripts/classify_jp.py` — BOJ stance + Tankan + ESRI CI + deflation regime
- `investing-toolkit/skills/analysis-macro-regime/scripts/classify_tw.py` — NDC 五色燈號 + 9 構成 + TIER + TSMC overlay
- `investing-toolkit/skills/analysis-macro-regime/scripts/classify_kr.py` — BOK target + KOSTAT cycle + 가계부채 overlay
- `investing-toolkit/skills/analysis-macro-regime/scripts/classify_cn.py` — PBOC reaction + credit impulse + 4-comp dispersion
- `investing-toolkit/skills/analysis-macro-regime/scripts/calibrations/__init__.py` — `load_calibration(country)` reader
- `investing-toolkit/skills/analysis-macro-regime/scripts/calibrations/us.yaml` — plumbed from thresholds-us.md
- `investing-toolkit/skills/analysis-macro-regime/scripts/calibrations/jp.yaml`
- `investing-toolkit/skills/analysis-macro-regime/scripts/calibrations/tw.yaml`
- `investing-toolkit/skills/analysis-macro-regime/scripts/calibrations/kr.yaml`
- `investing-toolkit/skills/analysis-macro-regime/scripts/calibrations/cn.yaml`
- `investing-toolkit/skills/analysis-macro-regime/research/grounding-{us,jp,tw,kr,cn}-2026-05.md` — partial-recalibration delta notes per country

### Modified
- `investing-toolkit/skills/analysis-macro-regime/scripts/regime_compose.py` — refactored from in-file classifier to thin dispatcher
- `investing-toolkit/skills/analysis-macro-regime/SKILL.md` — Phase 1 schema description, `_legacy` deprecation notice
- `investing-toolkit/skills/data-jp/scripts/pack.py` — wire e-Stat coincident-index + leading-index + machine-orders + Tankan business DI
- `investing-toolkit/skills/data-jp/scripts/boj_client.py` — new `--tankan-business-di` flag + parser
- `investing-toolkit/skills/data-cn/scripts/pack.py` — `_compute_credit_impulse()` helper
- `investing-toolkit/skills/data-kr/scripts/pack.py` — best-effort BOK ESI fetch
- `investing-toolkit/tests/integration/test_cross_layer_chains.py` — per-country `test_chain_{cc}_classifier_e2e` functions
- `investing-toolkit/.claude-plugin/plugin.json` — bump 2.0.1 → 2.1.0 (PR-7)

### Deleted (PR-7)
- `investing-toolkit/skills/analysis-macro-regime/scripts/_legacy_ic.py` — removed once Phase 1 stable

---

## PR Sequence

```
main
└─ PR-1 (feat/v2.1.0-phase1-pr1-infra)
   └─ PR-2 (feat/v2.1.0-phase1-pr2-us)
      ├─ PR-3 (feat/v2.1.0-phase1-pr3-jp)         ┐
      ├─ PR-4 (feat/v2.1.0-phase1-pr4-tw)         ├─ parallel
      ├─ PR-5 (feat/v2.1.0-phase1-pr5-kr)         │  via subagents
      └─ PR-6 (feat/v2.1.0-phase1-pr6-cn)         ┘
         └─ PR-7 (feat/v2.1.0-phase1-pr7-cleanup) — after all 4 country PRs merged
```

---

## PR-1 — Phase 1 Infrastructure

**Branch:** `feat/v2.1.0-phase1-pr1-infra`
**Predecessor:** main
**Estimated time:** 3-5 hours

**Files:**
- Create: `investing-toolkit/docs/adr/0004-analysis-macro-regime-phase1-per-country-classifiers.md` (already committed in this branch)
- Create: `investing-toolkit/skills/analysis-macro-regime/scripts/_legacy_ic.py`
- Create: `investing-toolkit/skills/analysis-macro-regime/scripts/_surface.py`
- Create: `investing-toolkit/skills/analysis-macro-regime/scripts/calibrations/__init__.py`
- Modify: `investing-toolkit/skills/analysis-macro-regime/scripts/regime_compose.py`
- Modify: `investing-toolkit/skills/analysis-macro-regime/SKILL.md`
- Test: `investing-toolkit/tests/integration/test_macro_regime_phase1_dispatch.py` (new)
- Test: `investing-toolkit/tests/integration/test_cross_layer_chains.py` (no change in PR-1; assertions added by per-country PRs)

### Task 1: Move legacy IC classifier to `_legacy_ic.py`

- [ ] **Step 1: Create `_legacy_ic.py` containing the current classifier verbatim**

Move `GROWTH_KEYS`, `INFLATION_KEYS`, `CN_COMPONENT_KEYS`, `DIRECTION_BAND_STDEV`, `NORMALISED_BAND`, `CN_COMPONENT_DISAGREE_PP`, `resolve_series`, `classify_direction`, `map_ic_quadrant`, `map_gip_quad`, `compute_us_real_rate`, `cn_component_overlay`, `normalised_country`, and `classify_country` from `regime_compose.py` into a new `_legacy_ic.py`. Keep all logic byte-identical EXCEPT the TW GROWTH_KEYS patch in Step 2.

```python
# _legacy_ic.py header
"""Phase 1 transition fallback — preserves the v1.9.0 single-classifier
output for backward compatibility. Populates `_legacy.by_country` block
of the new Phase 1 schema. Will be removed at Phase 2 start or v2.2.0,
whichever earlier. See ADR-0004 for context."""
```

- [ ] **Step 2: Patch TW GROWTH_KEYS so the legacy fallback produces non-degenerate output**

Current `GROWTH_KEYS["tw"]` = `["cycle.signal", "signal", "ndc-signal", "gdp"]`. None of these match what TW's flatten emits (`signal-score / ndc.signal-score / coincident-index / leading-index`). Patch to:

```python
GROWTH_KEYS = {
    ...
    "tw": [
        "coincident-index",      # statgov.coincident-index also emitted as alias
        "signal-score",          # NDC 五色燈號 9-45 composite
        "ndc.signal-score",
        "leading-index",
        # legacy keys preserved as last-resort fallback
        "cycle.signal", "signal", "ndc-signal", "gdp",
    ],
    ...
}
```

- [ ] **Step 3: Run pytest to confirm no breakage from move-only refactor**

```bash
cd investing-toolkit
uv run pytest tests/integration/test_cross_layer_chains.py::test_chain_country_regime_to_macroregime -v
```

Expected: existing parametrized tests for jp/tw/kr/cn still pass; tw assertion that previously trapped on `confidence: low` may now pass at `confidence: medium`.

- [ ] **Step 4: Commit**

```bash
git add investing-toolkit/skills/analysis-macro-regime/scripts/_legacy_ic.py
git commit -m "refactor(analysis-macro-regime): extract legacy IC classifier to _legacy_ic.py + patch TW GROWTH_KEYS"
```

### Task 2: Create `_surface.py` with `CountryRegimeCard` dataclass

- [ ] **Step 1: Define convention-level uniformity envelope**

```python
"""Phase 1 convention-level uniformity envelope per ADR-0004.

The 6 outer keys are convention. native_verdict interior is deliberately
schema-free — each country owns its shape. Phase 2 may convert any inner
field to a comparable-surface contract later, informed by what each country
actually emits."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class CountryRegimeCard:
    country: str  # "us" / "jp" / "tw" / "kr" / "cn"
    framework_used: str  # human-readable framework name
    native_verdict: dict[str, Any]  # country-specific, no schema constraint
    indicators_used: list[str]
    data_quality: dict[str, Any]  # keys: missing, stale, _note
    confidence: Literal["low", "medium", "high"]
    provenance: dict[str, Any]  # keys: calibration_doc, calibration_vintage, last_grounded, fetched_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "country": self.country,
            "framework_used": self.framework_used,
            "native_verdict": self.native_verdict,
            "indicators_used": self.indicators_used,
            "data_quality": self.data_quality,
            "confidence": self.confidence,
            "provenance": self.provenance,
        }


@dataclass
class Phase1Output:
    schema_version: str = "2.0-phase1"
    by_country: dict[str, dict[str, Any]] = field(default_factory=dict)
    cross_country: None = None  # Phase 2 placeholder
    _legacy: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "by_country": self.by_country,
            "cross_country": self.cross_country,
            "_legacy": self._legacy,
        }
```

- [ ] **Step 2: Commit**

```bash
git add investing-toolkit/skills/analysis-macro-regime/scripts/_surface.py
git commit -m "feat(analysis-macro-regime): add CountryRegimeCard + Phase1Output dataclasses"
```

### Task 3: Create `calibrations/__init__.py` with `load_calibration` reader

- [ ] **Step 1: Create directory + reader**

```python
"""calibrations/ — per-country YAML calibrations plumbed from
references/thresholds-{country}.md. See ADR-0004."""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import yaml

CALIBRATIONS_DIR = Path(__file__).parent
SUPPORTED_COUNTRIES = {"us", "jp", "tw", "kr", "cn"}


@dataclass
class CountryCalibration:
    country: str
    raw: dict[str, Any]  # full YAML payload, country-specific shape

    def get(self, key: str, default: Any = None) -> Any:
        return self.raw.get(key, default)


def load_calibration(country: str) -> CountryCalibration:
    if country not in SUPPORTED_COUNTRIES:
        raise ValueError(f"unsupported country: {country!r}")
    path = CALIBRATIONS_DIR / f"{country}.yaml"
    if not path.exists():
        # Phase 1: not all calibrations land in the same PR. Empty calibration
        # is acceptable; classify_X.py decides how to handle missing fields.
        return CountryCalibration(country=country, raw={})
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return CountryCalibration(country=country, raw=payload)
```

- [ ] **Step 2: Confirm yaml availability**

```bash
cd investing-toolkit
uv run python -c "import yaml; print(yaml.__version__)"
```

Expected: prints version (PyYAML is available via existing requirements.txt).

- [ ] **Step 3: Commit**

```bash
git add investing-toolkit/skills/analysis-macro-regime/scripts/calibrations/
git commit -m "feat(analysis-macro-regime): add calibrations/ reader (load_calibration helper)"
```

### Task 4: Refactor `regime_compose.py` to thin dispatcher

- [ ] **Step 1: Replace in-file classifier with dispatcher**

```python
"""regime_compose.py — Phase 1 thin dispatcher per ADR-0004.

Per --input country=path pairs, dispatch to classify_X module if available,
fall through to _legacy_ic.classify_country otherwise. Aggregate by_country
+ _legacy.by_country blocks. cross_country is hardcoded null in Phase 1.
"""

from __future__ import annotations
import argparse
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import _legacy_ic  # legacy fallback
from _surface import CountryRegimeCard, Phase1Output

SUPPORTED_COUNTRIES = {"us", "jp", "tw", "kr", "cn"}


def _try_load_classifier(country: str):
    """Return classify_{country} callable if module exists, else None."""
    try:
        module = importlib.import_module(f"classify_{country}")
        return getattr(module, f"classify_{country}", None)
    except ImportError:
        return None


def _parse_input(arg: str) -> dict[str, str]:
    out = {}
    for chunk in arg.split(","):
        if "=" not in chunk:
            raise SystemExit(f"Bad --input fragment {chunk!r} — expected country=path")
        cc, path = chunk.split("=", 1)
        cc = cc.strip().lower()
        path = path.strip()
        if cc not in SUPPORTED_COUNTRIES:
            raise SystemExit(f"Unknown country {cc!r}")
        out[cc] = path
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 1 macro regime dispatcher")
    parser.add_argument("--input", required=True,
                        help="Comma-separated country=path pairs")
    args = parser.parse_args()

    inputs = _parse_input(args.input)
    output = Phase1Output()
    output._legacy = {"by_country": {}, "note":
        "Phase 1 transition fallback; classify_country() output preserved for "
        "memo / portfolio consumers. See ADR-0004."}

    for cc, path in inputs.items():
        regime_pack = json.loads(Path(path).read_text(encoding="utf-8"))

        # New per-country classifier path
        classifier = _try_load_classifier(cc)
        if classifier is not None:
            try:
                card: CountryRegimeCard = classifier(regime_pack)
                output.by_country[cc] = card.to_dict()
            except Exception as e:
                output.by_country[cc] = {
                    "country": cc,
                    "_error": str(e),
                    "_note": f"classify_{cc} raised; using _legacy fallback only",
                }

        # Legacy IC fallback (always populated for backward compat)
        try:
            legacy = _legacy_ic.classify_country(cc, regime_pack)
            output._legacy["by_country"][cc] = legacy
        except Exception as e:
            output._legacy["by_country"][cc] = {"_error": str(e)}

    print(json.dumps(output.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run regression test against existing fixtures**

```bash
cd investing-toolkit
uv run python skills/analysis-macro-regime/scripts/regime_compose.py \
  --input "us=tests/data/fixtures/data-us-regime-pack-sample.json,jp=tests/data/fixtures/data-jp-regime-pack-sample.json" \
  | python -c "import json,sys; d=json.load(sys.stdin); print(list(d.keys())); print('legacy us:', d['_legacy']['by_country']['us']['ic_quadrant'])"
```

Expected: keys = `['schema_version', 'by_country', 'cross_country', '_legacy']`; us legacy ic_quadrant = some IC label.

- [ ] **Step 3: Commit**

```bash
git add investing-toolkit/skills/analysis-macro-regime/scripts/regime_compose.py
git commit -m "refactor(analysis-macro-regime): regime_compose.py to thin dispatcher per ADR-0004"
```

### Task 5: Add Phase 1 dispatch integration test

- [ ] **Step 1: Write the test**

```python
# tests/integration/test_macro_regime_phase1_dispatch.py
"""Phase 1 dispatch integration test per ADR-0004.

Verifies regime_compose.py:
1. Produces 2.0-phase1 schema
2. cross_country is null in Phase 1
3. _legacy.by_country populated for all 5 countries
4. by_country populated only for countries with classify_X module
5. TW _legacy resolves growth proxy (was 'flat / proxy missing' before
   GROWTH_KEYS patch)
"""

import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "investing-toolkit" / "skills"
FIXTURES = ROOT / "investing-toolkit" / "tests" / "data" / "fixtures"
SCRIPT = SKILLS / "analysis-macro-regime" / "scripts" / "regime_compose.py"


def _run_dispatch(countries: list[str]) -> dict:
    args = ",".join(f"{cc}={FIXTURES / f'data-{cc}-regime-pack-sample.json'}"
                    for cc in countries
                    if (FIXTURES / f"data-{cc}-regime-pack-sample.json").exists())
    if not args:
        pytest.skip("no fixtures available")
    result = subprocess.run(
        ["uv", "run", "python", str(SCRIPT), "--input", args],
        capture_output=True, text=True, cwd=ROOT / "investing-toolkit",
    )
    assert result.returncode == 0, f"dispatch failed: {result.stderr}"
    return json.loads(result.stdout)


def test_phase1_schema_shape():
    out = _run_dispatch(["us", "jp", "tw", "kr", "cn"])
    assert out["schema_version"] == "2.0-phase1"
    assert out["cross_country"] is None
    assert "_legacy" in out
    assert "by_country" in out


def test_phase1_legacy_populated_for_all_countries():
    out = _run_dispatch(["us", "jp", "tw", "kr", "cn"])
    legacy_by_country = out["_legacy"]["by_country"]
    for cc in ["us", "jp", "tw", "kr", "cn"]:
        if cc in legacy_by_country:
            assert "ic_quadrant" in legacy_by_country[cc] or "_error" in legacy_by_country[cc]


def test_phase1_tw_legacy_resolves_growth_proxy():
    """After PR-1's GROWTH_KEYS patch, TW _legacy block should NOT report
    'growth proxy missing for tw' — it should resolve to signal-score or
    coincident-index."""
    out = _run_dispatch(["tw"])
    legacy_tw = out["_legacy"]["by_country"]["tw"]
    notes = legacy_tw.get("notes", [])
    assert not any("growth proxy missing for tw" in n for n in notes), (
        f"TW _legacy still reports growth proxy missing — GROWTH_KEYS patch broke. "
        f"notes: {notes}"
    )
```

- [ ] **Step 2: Run the new test**

```bash
cd investing-toolkit
uv run pytest tests/integration/test_macro_regime_phase1_dispatch.py -v
```

Expected: 3 tests pass.

- [ ] **Step 3: Commit**

```bash
git add investing-toolkit/tests/integration/test_macro_regime_phase1_dispatch.py
git commit -m "test(analysis-macro-regime): Phase 1 dispatch + TW GROWTH_KEYS regression test"
```

### Task 6: Update SKILL.md with Phase 1 schema

- [ ] **Step 1: Add Phase 1 schema description**

Edit `investing-toolkit/skills/analysis-macro-regime/SKILL.md` Output JSON section to describe `schema_version: 2.0-phase1`, `by_country`, `cross_country: null`, `_legacy.by_country`. Add a note that Phase 1 is per ADR-0004 and Phase 2 will design cross-country surface based on observed native verdicts.

- [ ] **Step 2: Run lint / sync check**

```bash
cd investing-toolkit
ls scripts/ 2>/dev/null  # confirm in correct dir
uv run pytest tests/integration/test_macro_regime_phase1_dispatch.py -v
```

- [ ] **Step 3: Commit**

```bash
git add investing-toolkit/skills/analysis-macro-regime/SKILL.md
git commit -m "docs(analysis-macro-regime): SKILL.md Phase 1 schema description"
```

### Task 7: Open PR-1

- [ ] **Step 1: Push branch**

```bash
git push -u origin feat/v2.1.0-phase1-pr1-infra
```

- [ ] **Step 2: Open PR**

```bash
gh pr create --base main --title "feat(investing-toolkit): ADR-0004 + Phase 1 infra (analysis-macro-regime dispatcher)" --body "<see ADR-0004 for full context>"
```

PR-1 acceptance: all tests green, ADR-0004 readable, dispatcher produces 2.0-phase1 schema, TW legacy block resolves growth proxy.

---

## PR-2 — US Classifier Baseline

**Branch:** `feat/v2.1.0-phase1-pr2-us` (branched off `feat/v2.1.0-phase1-pr1-infra`)
**Predecessor:** PR-1
**Estimated time:** 2-4 hours

**Goal:** Establish the per-country `classify_X.py` reference pattern for PR-3-6 to mirror.

**Files:**
- Create: `investing-toolkit/skills/analysis-macro-regime/scripts/classify_us.py`
- Create: `investing-toolkit/skills/analysis-macro-regime/scripts/calibrations/us.yaml`
- Create: `investing-toolkit/skills/analysis-macro-regime/research/grounding-us-2026-05.md`
- Modify: `investing-toolkit/tests/integration/test_cross_layer_chains.py` (add `test_chain_us_classifier_e2e`)

### Task 1: Plumb thresholds-us.md into calibrations/us.yaml

- [ ] **Step 1: Read source-of-truth**

```bash
cat investing-toolkit/skills/analysis-macro-regime/references/thresholds-us.md
```

- [ ] **Step 2: Extract calibration data**

Write `calibrations/us.yaml` containing:

```yaml
country: us
authority: Federal Reserve System
currency: USD

inflation_target: 2.0
inflation_target_type: central_tendency
inflation_target_framework: FIT  # post-FAIT 2025 per Powell Jackson Hole 2025-08-22
inflation_target_authority: FOMC 2012-01-25 statement; FAIT retired 2025-08

policy_rate_neutrality:
  hlw_real: 0.75       # NY Fed 2025-Q4 vintage; Williams maintains r* not meaningfully risen post-COVID
  lubik_matthes_real: 1.68  # Richmond Fed 2025-Q4 updated 2026-03-10
  fomc_sep_longer_run_real: 1.0  # Dec 2025 SEP median; CT 0.8-1.5%, range 0.6-1.9%
  ny_fed_composite_real: 1.7   # Aug 2025 Liberty Street, 0.9-2.5% band
  cross_method_central: [0.5, 1.9]
  term_premium_estimate_bp: 50

real_rate_4tier:
  accommodative: { upper: 0.0 }
  neutral: { lower: 0.0, upper: 1.0 }
  moderately_restrictive: { lower: 1.0, upper: 1.75 }
  clearly_restrictive: { lower: 1.75 }

nairu:
  point_estimate: 4.5  # CBO 2026 forecast
  band: [4.4, 4.6]

direction_band_stdev: 0.5
normalised_indicators: ["nowcast.CFNAI", "nowcast.WEI"]

structural_overlays:
  - yield_curve  # T10Y2Y inversion signal
  - real_rate_decomposition  # 4-tier per real_rate_4tier above

provenance:
  calibration_doc: thresholds-us.md
  calibration_vintage: 2026-Q1
  last_full_grounding: 2026-04-18
  partial_refresh: 2026-04-19  # v1.11.0 addendum
  authority_sources:
    - Federal Reserve / FOMC
    - NY Fed (HLW, Liberty Street)
    - Richmond Fed (Lubik-Matthes)
    - CBO Budget & Economic Outlook
```

- [ ] **Step 3: Verify YAML loads**

```bash
cd investing-toolkit/skills/analysis-macro-regime/scripts
uv run python -c "from calibrations import load_calibration; c = load_calibration('us'); print(c.country, c.get('inflation_target'))"
```

Expected: `us 2.0`.

- [ ] **Step 4: Commit**

```bash
git add investing-toolkit/skills/analysis-macro-regime/scripts/calibrations/us.yaml
git commit -m "feat(analysis-macro-regime): calibrations/us.yaml from thresholds-us.md"
```

### Task 2: Implement classify_us.py

- [ ] **Step 1: Write classifier**

```python
"""classify_us.py — US per-country classifier per ADR-0004.

Framework: IC + Hedgeye GIP + Fed FIT + 4-tier real-rate decomposition
(HLW / LM / SEP / NY Fed composite) + yield curve overlay.

Reads calibrations/us.yaml. Produces CountryRegimeCard with rich
native_verdict carrying:
- ic_quadrant + gip_regime
- real_rate_band: accommodative / neutral / moderately_restrictive / clearly_restrictive
- yield_curve_state: normal / flat / inverted
- fed_qualitative_anchor: text from Williams Dec 2025 / Jan 2026 speeches
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

from _legacy_ic import (
    classify_direction, map_ic_quadrant, map_gip_quad, resolve_series,
    GROWTH_KEYS, INFLATION_KEYS,
)
from _surface import CountryRegimeCard
from calibrations import load_calibration


def _classify_real_rate(dfii: float | None, calib_4tier: dict) -> str:
    if dfii is None:
        return "unknown"
    if dfii < calib_4tier["accommodative"]["upper"]:
        return "accommodative"
    if dfii < calib_4tier["neutral"]["upper"]:
        return "neutral"
    if dfii < calib_4tier["moderately_restrictive"]["upper"]:
        return "moderately_restrictive"
    return "clearly_restrictive"


def _classify_yield_curve(t10y2y: float | None) -> str:
    if t10y2y is None:
        return "unknown"
    if t10y2y < -0.10:
        return "inverted"
    if t10y2y < 0.20:
        return "flat"
    return "normal"


def classify_us(regime_pack: dict[str, Any]) -> CountryRegimeCard:
    series = regime_pack.get("series", {})
    calib = load_calibration("us")

    growth_values = resolve_series(series, GROWTH_KEYS["us"])
    inflation_values = resolve_series(series, INFLATION_KEYS["us"])

    growth_dir = classify_direction(growth_values or [], normalised=True)
    inflation_dir = classify_direction(inflation_values or [])

    ic_quadrant = map_ic_quadrant(growth_dir, inflation_dir)
    gip_regime = map_gip_quad(ic_quadrant)

    # Real-rate decomposition (US-specific overlay)
    dfii10_series = series.get("real_rates.DFII10") or series.get("DFII10")
    dfii10_latest = (
        float(dfii10_series[-1])
        if isinstance(dfii10_series, list) and dfii10_series
        else None
    )
    real_rate_band = _classify_real_rate(
        dfii10_latest, calib.get("real_rate_4tier", {}))

    # Yield curve overlay
    t10y2y_series = series.get("rates.T10Y2Y") or series.get("T10Y2Y")
    t10y2y_latest = (
        float(t10y2y_series[-1])
        if isinstance(t10y2y_series, list) and t10y2y_series
        else None
    )
    yield_curve_state = _classify_yield_curve(t10y2y_latest)

    indicators_used = []
    for keyname in ("growth", "inflation", "real_rate", "yield_curve"):
        pass  # populated below

    indicators_used = (
        (GROWTH_KEYS["us"] if growth_values else [])
        + (INFLATION_KEYS["us"] if inflation_values else [])
        + (["DFII10"] if dfii10_latest is not None else [])
        + (["T10Y2Y"] if t10y2y_latest is not None else [])
    )

    has_g = growth_values is not None and len(growth_values) >= 4
    has_i = inflation_values is not None and len(inflation_values) >= 4
    confidence = "high" if has_g and has_i else "medium" if has_g or has_i else "low"

    native_verdict = {
        "framework_label": "IC + Hedgeye GIP + Fed FIT + 4-tier real-rate",
        "growth_direction": growth_dir,
        "inflation_direction": inflation_dir,
        "ic_quadrant": ic_quadrant,
        "gip_regime": gip_regime,
        "real_rate_decomposition": {
            "dfii10": dfii10_latest,
            "band": real_rate_band,
            "fed_qualitative_anchor": (
                "Williams Dec 2025 'Resilience' / Jan 2026 'A Few Words for the "
                "New Year' — current policy 'modestly restrictive'"
            ) if real_rate_band in ("moderately_restrictive", "clearly_restrictive")
              else None,
        },
        "yield_curve": {
            "t10y2y": t10y2y_latest,
            "state": yield_curve_state,
        },
        "policy_framework": calib.get("inflation_target_framework", "FIT"),
        "policy_target_pct": calib.get("inflation_target", 2.0),
    }

    return CountryRegimeCard(
        country="us",
        framework_used=native_verdict["framework_label"],
        native_verdict=native_verdict,
        indicators_used=indicators_used,
        data_quality={
            "missing": [k for k, v in
                        [("growth", growth_values), ("inflation", inflation_values),
                         ("real_rate", dfii10_latest), ("yield_curve", t10y2y_latest)]
                        if not v],
            "stale": [],
        },
        confidence=confidence,
        provenance={
            "calibration_doc": calib.get("provenance", {}).get(
                "calibration_doc", "thresholds-us.md"),
            "calibration_vintage": calib.get("provenance", {}).get(
                "calibration_vintage", "2026-Q1"),
            "last_grounded": calib.get("provenance", {}).get(
                "partial_refresh", calib.get("provenance", {}).get(
                    "last_full_grounding", "unknown")),
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        },
    )
```

- [ ] **Step 2: Test directly**

```bash
cd investing-toolkit
uv run python -c "
import sys
sys.path.insert(0, 'skills/analysis-macro-regime/scripts')
from classify_us import classify_us
import json
pack = json.load(open('tests/data/fixtures/data-us-regime-pack-sample.json'))
card = classify_us(pack)
print(json.dumps(card.to_dict(), indent=2, ensure_ascii=False, default=str))
"
```

Expected: prints CountryRegimeCard with framework_used / native_verdict.ic_quadrant / real_rate_decomposition.band / yield_curve.state / confidence.

- [ ] **Step 3: Commit**

```bash
git add investing-toolkit/skills/analysis-macro-regime/scripts/classify_us.py
git commit -m "feat(analysis-macro-regime): classify_us.py — US classifier baseline (IC + 4-tier real-rate + yield curve)"
```

### Task 3: Add US-specific integration test

- [ ] **Step 1: Add test_chain_us_classifier_e2e**

Append to `investing-toolkit/tests/integration/test_cross_layer_chains.py`:

```python
def test_chain_us_classifier_e2e():
    """data-us regime-pack → classify_us → CountryRegimeCard with valid
    Phase 1 envelope. Per ADR-0004."""
    fixture = FIXTURES / "data-us-regime-pack-sample.json"
    if not fixture.exists():
        pytest.skip("missing fixture")

    import json
    import subprocess
    result = subprocess.run(
        ["uv", "run", "python", str(SKILLS / "analysis-macro-regime" /
                                    "scripts" / "regime_compose.py"),
         "--input", f"us={fixture}"],
        capture_output=True, text=True, cwd=ROOT / "investing-toolkit",
    )
    assert result.returncode == 0, f"dispatch failed: {result.stderr}"
    out = json.loads(result.stdout)

    us_card = out["by_country"]["us"]
    assert us_card["country"] == "us"
    assert "framework_label" in us_card["native_verdict"] or \
           "framework_used" in us_card
    assert us_card["native_verdict"]["ic_quadrant"] in [
        "1-recovery", "2-overheat", "3-stagflation", "4-reflation"
    ]
    assert us_card["confidence"] in ("low", "medium", "high")
    assert us_card["provenance"]["calibration_doc"] == "thresholds-us.md"
```

- [ ] **Step 2: Run test**

```bash
cd investing-toolkit
uv run pytest tests/integration/test_cross_layer_chains.py::test_chain_us_classifier_e2e -v
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add investing-toolkit/tests/integration/test_cross_layer_chains.py
git commit -m "test(analysis-macro-regime): test_chain_us_classifier_e2e"
```

### Task 4: Write US grounding delta refresh note

- [ ] **Step 1: Create research/ directory + grounding note**

```bash
mkdir -p investing-toolkit/skills/analysis-macro-regime/research
```

Write `investing-toolkit/skills/analysis-macro-regime/research/grounding-us-2026-05.md` containing a partial-recalibration delta from v1.11.0 (2026-04-19) to 2026-05-02 — only changes captured. Format follows recalibration-protocol.md "partial recalibration" template.

Minimal content: vintage timestamp, sources verified for currency (e.g., FOMC Dec 2025 SEP still latest, no new HLW vintage, Williams speech anchor still current), any deltas (none expected for ~2 week window unless FOMC Jan 2026 meeting changed signals).

- [ ] **Step 2: Commit**

```bash
git add investing-toolkit/skills/analysis-macro-regime/research/grounding-us-2026-05.md
git commit -m "docs(analysis-macro-regime): grounding-us-2026-05.md partial refresh from v1.11.0"
```

### Task 5: Open PR-2

- [ ] **Step 1: Push branch**

```bash
git push -u origin feat/v2.1.0-phase1-pr2-us
```

- [ ] **Step 2: Open PR**

```bash
gh pr create --base feat/v2.1.0-phase1-pr1-infra --title "feat(investing-toolkit): Phase 1 PR-2 — classify_us.py baseline + calibration plumbing"
```

PR-2 acceptance: classify_us produces valid CountryRegimeCard, US integration test green, calibrations/us.yaml schema serves as reference for PR-3-6.

---

## PR-3 — JP Classifier (parallel via subagent)

**Branch:** `feat/v2.1.0-phase1-pr3-jp` (branched off `feat/v2.1.0-phase1-pr2-us`)
**Predecessor:** PR-2 (and parallel-safe with PR-4/5/6)
**Estimated time:** 1 week sequential / ~30-60 min via dedicated implementer subagent

**Files:**
- Create: `investing-toolkit/skills/analysis-macro-regime/scripts/classify_jp.py`
- Create: `investing-toolkit/skills/analysis-macro-regime/scripts/calibrations/jp.yaml`
- Create: `investing-toolkit/skills/analysis-macro-regime/research/grounding-jp-2026-05.md`
- Modify: `investing-toolkit/skills/data-jp/scripts/boj_client.py` — add `--tankan-business-di` flag + parser
- Modify: `investing-toolkit/skills/data-jp/scripts/pack.py` — wire e-Stat coincident-index + leading-index + machine-orders presets + Tankan business DI
- Modify: `investing-toolkit/skills/data-jp/references/schema-regime-pack.json` — additive only (forward-compat additionalProperties: true)
- Modify: `investing-toolkit/tests/integration/test_cross_layer_chains.py` — add `test_chain_jp_classifier_e2e`
- Modify: `investing-toolkit/tests/data/fixtures/data-jp-regime-pack-sample.json` — regenerate with new fields (acceptable to do at end)

### Task 1-7: Standard per-country pattern

Per-country PRs follow this pattern (mirroring PR-2 US baseline):

- [ ] **Task 1**: Native-language grounding research — verify thresholds-japan.md vintage (2026-Q2 from v1.9.0), check for delta events (BOJ 展望 Apr 2026 release, policy rate changes since v1.11.0). Run web searches in **Japanese** (`日銀 政策金利 2026`, `BOJ 短観 業況判断 最新`, `JILPT 均衡失業率`). Cross-verify with primary sources (boj.or.jp, jilpt.go.jp). Delta refresh `grounding-jp-2026-05.md` per recalibration-protocol.md template.

- [ ] **Task 2**: Plumb thresholds-japan.md into `calibrations/jp.yaml`. Mirror US YAML schema structure. Required fields: country, authority, currency, inflation_target (2.0), inflation_target_framework (post-deflation), policy_rate_path (0.75% peak, 野村 ターミナル 1.50% via 3 hikes), nairu (2.80 JILPT 2026-02), real_rate (BOJ WP24-J-09 r* -0.25% mean), structural_overlays (deflation_regime_exit, tankan_dispersion).

- [ ] **Task 3**: Add Tankan business DI fetch to `boj_client.py`. Tankan series codes for 大企業/中小企業 × 製造業/非製造業 業況判断 DI. If BOJ Time-Series API doesn't expose cleanly, fall back to BOJ CSV download (same pattern as `tankan_inflation_outlook`). New flag: `--tankan-business-di`.

- [ ] **Task 4**: Wire Tankan business DI + e-Stat coincident-index + leading-index + machine-orders into `data-jp/scripts/pack.py pack_regime()`. Update `data-jp/references/schema-regime-pack.json` additively.

- [ ] **Task 5**: Implement `classify_jp.py`. Framework: BOJ stance + Tankan business DI dispersion + ESRI 景気動向指数 CI + deflation/inflation regime detection. Native verdict shape:

  ```python
  native_verdict = {
      "framework_label": "BOJ stance + Tankan business DI + ESRI CI + deflation regime",
      "boj_stance": "post-zirp" | "exit-deflation" | "ZIRP" | ...,
      "tankan_business_di": {
          "large_mfg": ..., "large_nonmfg": ..., "small_mfg": ..., "small_nonmfg": ...,
          "dispersion": ...,
      },
      "esri_coincident_index": {"value": ..., "trend": "rising/falling/flat"},
      "deflation_phase": "exited_2024" | "exit_2025" | "..." ,
      "ic_quadrant_legacy": ...,  # for backward reference, not load-bearing
      "policy_target_pct": 2.0,
  }
  ```

- [ ] **Task 6**: Add `test_chain_jp_classifier_e2e` (independent function, not parametrized — to avoid PR file conflicts). Assert `confidence != 'low'`, `framework_label` non-empty, `tankan_business_di.dispersion` populated.

- [ ] **Task 7**: Push branch, open PR targeting `feat/v2.1.0-phase1-pr2-us`.

PR-3 acceptance: classify_jp produces valid CountryRegimeCard with Tankan + ESRI CI populated, JP integration test green, grounding-jp-2026-05.md present, no fetch regression.

---

## PR-4 — TW Classifier (parallel via subagent)

**Branch:** `feat/v2.1.0-phase1-pr4-tw`
**Predecessor:** PR-2
**Estimated time:** 1 week / ~30-60 min via implementer subagent

**No fetch additions — TW signal-components already includes TIER (製造業營業氣候測驗點) per 2024 revision.**

### Task 1-7: Standard per-country pattern

- [ ] **Task 1**: Native-language grounding research in **繁體中文** (`NDC 五色景氣燈號 2024 修訂`, `CBC 理監事會 2026`, `中華經濟研究院 PMI 最新`). Cross-verify primary sources (ndc.gov.tw, cbc.gov.tw, dgbas.gov.tw). Delta refresh `grounding-tw-2026-05.md`.

- [ ] **Task 2**: `calibrations/tw.yaml` from thresholds-taiwan.md. Required fields: 5-color band thresholds (red ≥38, yellow-red 32-37, green 23-31, yellow-blue 17-22, blue ≤16), 9 構成項目 names per 2024 revision, CBC 「彈性定義」not rigid 2%, TSMC TAIEX 集中度 (2026-03-31 = 44.30%), 2014-2023 十年無紅燈 + 2024-02 首度紅燈 31 年新高 40 分.

- [ ] **Task 3**: No fetch additions.

- [ ] **Task 4**: No data-tw modifications.

- [ ] **Task 5**: Implement `classify_tw.py`. Framework: NDC 五色燈號 score-led + 9 構成 dispersion + TIER 製造氣候 + TSMC concentration overlay + DGBAS CPI. Native verdict:

  ```python
  native_verdict = {
      "framework_label": "NDC 五色景氣燈號 + 9 構成 + TIER + TSMC overlay",
      "signal_score": ..., "signal_color": "綠" | ...,
      "score_band_meaning": "31 年來首度紅燈" | "綠燈中位區" | ...,
      "components_9": {...},  # 9 indicators with individual color
      "tier_manufacturing_climate": ...,
      "tsmc_concentration_overlay": {"weight_pct": 44.30, "top_10_pct": 58.27},
      "cpi_context": {"latest": ..., "cbc_framing": "彈性定義"},
      "ic_quadrant_legacy": ...,
  }
  ```

- [ ] **Task 6**: `test_chain_tw_classifier_e2e` — assert signal_color valid, components_9 has 9 entries, tsmc_concentration_overlay populated.

- [ ] **Task 7**: Push branch, open PR.

PR-4 acceptance: classify_tw produces signal-led native verdict, TW integration test green, grounding-tw-2026-05.md present.

---

## PR-5 — KR Classifier (parallel via subagent)

**Branch:** `feat/v2.1.0-phase1-pr5-kr`
**Predecessor:** PR-2
**Estimated time:** 1 week / ~30-60 min via implementer subagent

### Task 1-7: Standard per-country pattern

- [ ] **Task 1**: Native-language grounding research in **한국어** (`한국은행 물가목표 2026`, `한국은행 경제심리지수 ESI 최신`, `한국 가계부채 GDP 비율`, `KOSPI 시가총액 집중도 삼성전자`). Cross-verify primary sources (bok.or.kr, kostat.go.kr). Delta refresh `grounding-kr-2026-05.md`.

- [ ] **Task 2**: `calibrations/kr.yaml` from thresholds-korea.md. Required fields: BOK 단일 2% target (since 2018-12-26, 무기한 적용), policy rate 2.50% (2025-05-29 인하 후 동결), 가계부채 89.4-92.3% GDP (2025-Q3-Q4), 삼성+SK 합계 61.29% KOSPI, 청년실업 7.7% 5 년 최고.

- [ ] **Task 3**: Best-effort BOK 경제심리지수 (ESI) fetch via fdr_client. If unavailable, classify_kr.py degrades gracefully (confidence: "medium" with note ESI missing), does NOT fail the country chain.

- [ ] **Task 4**: Wire ESI into `data-kr/scripts/pack.py pack_regime()` if fetch succeeds. Update schema additively.

- [ ] **Task 5**: Implement `classify_kr.py`. Framework: BOK 2% target alignment + KOSTAT 경기종합지수 동행지수순환변동치 + 가계부채/GDP overlay + KOSPI concentration overlay + KEYSTAT 54-indicator subset. Native verdict:

  ```python
  native_verdict = {
      "framework_label": "BOK 2% target + KOSTAT 동행 cycle + 가계부채 overlay",
      "bok_target_alignment": {"target": 2.0, "current": ..., "gap": ...},
      "cycle_phase": "expansion" | "peak" | "contraction" | "trough",
      "household_debt_overlay": {"ratio": 0.92, "macroprudential_concern": True},
      "kospi_concentration_overlay": {"top_2": 0.4090, "top_groups": 0.6129},
      "youth_unemployment": ...,
      "esi_status": "fetched" | "unavailable",
      "ic_quadrant_legacy": ...,
  }
  ```

- [ ] **Task 6**: `test_chain_kr_classifier_e2e` — assert bok_target_alignment populated, household_debt_overlay populated, ESI either fetched or marked unavailable (test does NOT fail on unavailable).

- [ ] **Task 7**: Push branch, open PR.

PR-5 acceptance: classify_kr produces native verdict, KR integration test green even when ESI unavailable, grounding-kr-2026-05.md present.

---

## PR-6 — CN Classifier (parallel via subagent)

**Branch:** `feat/v2.1.0-phase1-pr6-cn`
**Predecessor:** PR-2
**Estimated time:** 1 week / ~30-60 min via implementer subagent

### Task 1-8: Standard per-country pattern + credit impulse computation

- [ ] **Task 1**: Native-language grounding research in **简体中文** (`PBOC 7天逆回购 政策利率 2026`, `中国 CPI 目标 2025 政府工作报告`, `中国 社融存量 同比 2026 最新`, `中国 房地产 GDP 占比`). Cross-verify primary sources (pbc.gov.cn, stats.gov.cn). Delta refresh `grounding-cn-2026-05.md`.

- [ ] **Task 2**: `calibrations/cn.yaml` from thresholds-china.md. Required fields: CPI 目标 2.0 central tendency (2025 起从 ceiling 改为 中枢), policy rate primary = 7-day 逆回购 1.40% (2025-09 下调后未动), MLF 2.0% 数量工具 (2024-07 起非政策利率), LPR 1Y 3.0% / 5Y 3.5%, RRR 大银行 9.0%, 房地产 23.6% GDP 直接 / 31% 含基建, 4-comp dispersion alarm 2pp threshold.

- [ ] **Task 3**: New helper `_compute_credit_impulse()` in `data-cn/scripts/pack.py`:

  ```python
  def _compute_credit_impulse(tsf_stock_yoy: list, m2_yoy: list) -> dict:
      """Credit impulse proxy = (社融存量 yoy - GDP nominal yoy) or
      simply 社融存量 yoy 12m change. Methodology choice per CICC convention.
      Returns: {value, trend, methodology_note}."""
      ...
  ```

  Document methodology in a new `references/credit-impulse-methodology.md` note grounded against CICC / CITIC published definitions.

- [ ] **Task 4**: Wire credit_impulse computation into `pack_regime()` cn_specific block. Update schema additively.

- [ ] **Task 5**: Implement `classify_cn.py`. Framework: PBOC reaction (7-day 逆回购 primary) + credit impulse + 4-component dispersion + property cycle overlay + CPI framing. Native verdict:

  ```python
  native_verdict = {
      "framework_label": "PBOC reaction + credit impulse + 4-comp + property",
      "pboc_stance": "适度宽松" | "稳健" | "稳健中性" | ...,
      "policy_rate_primary": {"7d_reverse_repo": 1.40, "moved_2025_09": True},
      "cpi_framing": {
          "target": 2.0, "current": ..., "gap": ...,
          "policy_stance":
              "supportive_recovery_below_target" if current < target/2
              else "near_target_balanced" if abs(gap) < 0.5
              else ...,
      },
      "credit_impulse": {"value": ..., "trend": "expanding/contracting"},
      "4_component_dispersion": {
          "industrial": ..., "retail": ..., "fai": ..., "services": ...,
          "spread_pp": ..., "alarm": False,
      },
      "property_overlay": {"gdp_share_direct": 0.236, "gdp_share_incl_infra": 0.31},
      "ic_quadrant_legacy": ...,
  }
  ```

- [ ] **Task 6**: `test_chain_cn_classifier_e2e` — assert pboc_stance populated, cpi_framing.policy_stance valid, credit_impulse computed, 4_component_dispersion has 4 entries.

- [ ] **Task 7**: Add `references/credit-impulse-methodology.md` documenting methodology choice + grounding sources.

- [ ] **Task 8**: Push branch, open PR.

PR-6 acceptance: classify_cn produces native verdict with credit impulse + 4-comp + policy framing, CN integration test green, methodology note grounded.

---

## PR-7 — Cleanup + ADR Closure

**Branch:** `feat/v2.1.0-phase1-pr7-cleanup` (branched off main after PR-3-6 all merged)
**Predecessor:** all of PR-3, PR-4, PR-5, PR-6 merged
**Estimated time:** 30-60 min

### Task 1: Remove _legacy_ic.py fallback path

- [ ] **Step 1**: In `regime_compose.py`, remove the `_legacy.by_country` block computation; set `_legacy` to `null`.
- [ ] **Step 2**: Delete `_legacy_ic.py`.
- [ ] **Step 3**: Update `test_macro_regime_phase1_dispatch.py` to not assert on `_legacy.by_country`.
- [ ] **Step 4**: Run full test suite. Expected: all tests green (per-country tests are now the source of truth).

### Task 2: Bump plugin.json + update docs

- [ ] **Step 1**: Bump `investing-toolkit/.claude-plugin/plugin.json` from 2.0.1 → 2.1.0.
- [ ] **Step 2**: Update SKILL.md, README.md (US/JP/zh-TW), CHANGELOG.md, ROADMAP.md with v2.1.0 entry.
- [ ] **Step 3**: Update ADR-0004 status from "Accepted" to "Implemented".

### Task 3: Open PR-7

- [ ] Push, open PR targeting main.

PR-7 acceptance: full test suite green, plugin v2.1.0, ADR-0004 marked Implemented.

---

## Cross-Country Fresh-Eyes Audit (between PR-3-6 and PR-7)

Per `feedback_fresh_eyes_audit_after_internal_review.md` memory: dispatch one fresh-eyes auditor subagent **without the per-country implementation context** to check 4 country PRs for drift. Specifically:

- [ ] All 4 `calibrations/{country}.yaml` use consistent field naming
- [ ] All 4 `classify_{country}.py` implement the `def classify_{country}(regime_pack) -> CountryRegimeCard` signature consistently
- [ ] All 4 `native_verdict` dicts have `framework_label` as first key
- [ ] All 4 grounding notes follow recalibration-protocol.md partial-recalibration template
- [ ] Test functions are independent (not parametrized) — confirms no merge conflicts on test_cross_layer_chains.py
- [ ] No country imports another country's classify_X module

Audit findings → if MAJOR: open follow-up PR before PR-7. If MINOR: document in PR-7's commit message.

---

## Self-Review

After PR-2 ships and before dispatching PR-3-6:

- [ ] Confirm `calibrations/us.yaml` schema is the reference all 4 country YAMLs will follow
- [ ] Confirm `classify_us.py` structure (function signature, native_verdict shape, return type) is the reference all 4 country classifiers will mirror
- [ ] Confirm `test_chain_us_classifier_e2e` pattern is the reference all 4 per-country tests will mirror
- [ ] Confirm `grounding-us-2026-05.md` partial-recalibration template is the reference all 4 country grounding notes will mirror

---

## Execution Handoff

Plan complete. Two execution paths per writing-plans skill:

1. **Subagent-Driven (recommended for PR-3-6 parallelism)** — controller dispatches fresh implementer subagent per country, two-stage review per task. PR-1 + PR-2 + PR-7 done by controller directly.

2. **Inline Execution** — controller does everything sequentially. PR-3-6 lose parallelism advantage.

This plan assumes **option 1 hybrid**: controller (current Claude session) runs PR-1 + PR-2 inline, dispatches 4 subagents in worktrees for PR-3-6 in parallel, runs PR-7 inline after all 4 country PRs merged.

REQUIRED SUB-SKILL: `superpowers:subagent-driven-development` for PR-3-6 dispatch + two-stage review.
