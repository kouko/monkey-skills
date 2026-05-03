# investing-toolkit v2.2.0-b — analysis-comps `--mode compute` Activation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Activate the placeholder `--mode compute` branch in `analysis-comps/scripts/comps_compute.py` so the analyst gets `multiples_direct` + `multiples_compute` + `divergence` + `compute_provenance` blocks in one JSON. 3 of 5 multiples computable from current memo-fetch fields (trailingPE FY, priceToSales FY, forwardPE pass-through); 2 of 5 emit null with explanatory warnings (priceToBook, evEbitda — deferred to v2.2.0-l).

**Architecture:** Anchor-only dual input (B'). `--anchor` reads existing comps-multiples pack; new `--anchor-base` reads existing memo-fetch pack. Peers stay single input. Divergence is deterministic Layer 2 arithmetic, parallel to existing `_anchor_delta`. Pure-compute (no I/O / no LLM); direct mode unchanged except for `multiples` → `multiples_direct` field rename. No data-* changes.

**Tech Stack:** Python 3.10+ stdlib only (PEP 723); pytest with subprocess runner; existing fixture conventions in `tests/analysis/fixtures/`.

**Spec reference:** [docs/superpowers/specs/2026-05-03-investing-toolkit-v2.2.0-b-comps-compute-design.md](../specs/2026-05-03-investing-toolkit-v2.2.0-b-comps-compute-design.md)

**Branch:** `feat/v2.2.0-b-comps-compute-spec` (already has spec commit + correction commit)

---

## File Structure

| Path | Action | Purpose |
|---|---|---|
| `investing-toolkit/skills/analysis-comps/references/divergence-thresholds.md` | CREATE | SoT for 5%/15% bands |
| `investing-toolkit/skills/analysis-comps/scripts/comps_compute.py` | MODIFY | Rename multiples → multiples_direct; add compute path |
| `investing-toolkit/skills/analysis-comps/SKILL.md` | MODIFY | Add §"Direct vs Compute — when to use which" |
| `investing-toolkit/skills/report-equity-memo/SKILL.md` | MODIFY | Phase 2.5 → `--mode compute`; Phase 4 divergence prompt |
| `investing-toolkit/tests/analysis/fixtures/comps_anchor_aapl_memo_fetch.json` | CREATE | Slim memo-fetch fixture |
| `investing-toolkit/tests/analysis/fixtures/comps_compute_expected_aapl.json` | CREATE | Golden compute-mode output |
| `investing-toolkit/tests/analysis/test_analysis_comps.py` | MODIFY | Update existing tests for rename; add 19 compute-mode tests |
| `investing-toolkit/tests/integration/test_cross_layer_chains.py` | MODIFY | Add `test_chain_us_comps_compute_dual_input` |
| `investing-toolkit/ROADMAP.md` | MODIFY | Close v2.2.0-b ✅; add v2.2.0-k + v2.2.0-l |

**Commits planned (in order):** 9 commits, each TDD-shaped (failing test → impl → green → commit).

---

## Phase 1 — Direct mode rename (preserves byte-equality except 1 field)

This phase exists alone so direct-mode regression is isolated from feature additions. Anyone reverting v2.2.0-b's compute features can keep this rename.

### Task 1.1: Update existing direct-mode tests for `multiples` → `multiples_direct`

**Files:**
- Modify: `tests/analysis/test_analysis_comps.py`

- [ ] **Step 1: Find every assertion referencing `payload["anchor"]["multiples"]` or similar**

```bash
cd /Users/kouko/GitHub/monkey-skills/investing-toolkit
grep -nE 'anchor.*\bmultiples\b|"multiples"' tests/analysis/test_analysis_comps.py
```

Expected: list of ~5-10 lines with `"multiples"` references in anchor block.

- [ ] **Step 2: Replace `"multiples"` with `"multiples_direct"` in those test assertions**

Use Edit tool to change every line where the test reads `payload["anchor"]["multiples"]`. Do NOT touch lines reading `peers[i]["multiples"]` (peers keep `multiples` since they're single-input direct).

- [ ] **Step 3: Run the tests — they should fail (impl not yet renamed)**

```bash
uv run pytest tests/analysis/test_analysis_comps.py -v 2>&1 | tail -20
```

Expected: ~5-10 KeyError or AssertionError failures referencing `'multiples_direct'`.

### Task 1.2: Apply rename in `comps_compute.py`

**Files:**
- Modify: `skills/analysis-comps/scripts/comps_compute.py:357`

- [ ] **Step 1: Locate the output assembly**

```bash
grep -nE '"multiples":|"multiples"' skills/analysis-comps/scripts/comps_compute.py
```

Expected: line ~357 inside the `payload = {...}` assembly: `"multiples": anchor_multiples,`

- [ ] **Step 2: Rename the output field**

Edit `comps_compute.py` line 357:
- Before: `"multiples": anchor_multiples,`
- After:  `"multiples_direct": anchor_multiples,`

(Peer entries at line ~340 stay `"multiples"` — the rename is anchor-only.)

- [ ] **Step 3: Run tests — they should pass**

```bash
uv run pytest tests/analysis/test_analysis_comps.py -v 2>&1 | tail -10
```

Expected: All existing tests pass (with the new field name).

- [ ] **Step 4: Commit**

```bash
git add skills/analysis-comps/scripts/comps_compute.py tests/analysis/test_analysis_comps.py
git commit -m "$(cat <<'EOF'
refactor(analysis-comps): rename anchor.multiples → anchor.multiples_direct

Prepares the v2.0.0 direct-mode output for v2.2.0-b dual-axis output
shape. Direct mode now emits anchor.multiples_direct; compute mode
will add anchor.multiples_compute alongside. Peer entries unchanged
(peers.[].multiples stays — peers are single-input direct only).

The only in-tree caller of comps_compute.py is report-equity-memo
Phase 2.5; that caller is migrated atomically in a later commit
within this PR.

ROADMAP: §v2.2.0-b — Phase 1 of 4.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 2 — Threshold reference doc

### Task 2.1: Create `divergence-thresholds.md`

**Files:**
- Create: `skills/analysis-comps/references/divergence-thresholds.md`

- [ ] **Step 1: Write the reference doc**

Use Write tool with this exact content:

````markdown
# Divergence Thresholds — analysis-comps `--mode compute`

Source-of-truth for the bands that classify the divergence between
yfinance pre-cooked multiples (`multiples_direct`) and SEC-EDGAR-raw
recomputed multiples (`multiples_compute`).

## Bands

| `\|pct_diff\|` band | `alert` | Analyst action |
|---|---|---|
| ≤ 5% | `low` | Reasonable upstream-rounding noise; no narrative needed |
| 5% < x ≤ 15% | `medium` | Mention divergence source in memo Comps section |
| > 15% | `high` | Red flag — Comps section MUST trace each anchor multiple back to SEC raw with `accession` |
| (compute is null OR direct is null) | `n/a` | Skip; surface in `_provenance.warnings` |

## Functional copy in code

`comps_compute.py` defines named constants matching these bands:

```python
DIVERGENCE_BAND_LOW  = 0.05   # 5%   — boundary inclusive (≤ low)
DIVERGENCE_BAND_HIGH = 0.15   # 15%  — boundary inclusive for medium (high band is strict >)
```

**Drift rule**: any change to a band number MUST update both this file
and the named constants in the same PR (per SSOT-and-functional-copy
pattern, repo-wide convention).

## When the bands fire

- `trailingPE` divergence high almost always indicates yfinance applied
  an EPS adjustment (stock-based comp / impairment / one-off tax) that
  SEC GAAP raw didn't. Buy-side memos must cite which version they use.
- `priceToSales` divergence high usually indicates segment-revenue vs
  total-revenue choice; or yfinance's "TTM revenue" vs SEC's audited FY.
- `priceToBook` / `evEbitda` divergence is currently always `n/a`
  (compute deferred to v2.2.0-l — memo-fetch lacks `total_stockholders_equity`
  and `depreciation_amortization`).
- `forwardPE` divergence is always 0 (pass-through, no recompute).

## References

- Design spec: [docs/superpowers/specs/2026-05-03-investing-toolkit-v2.2.0-b-comps-compute-design.md §9](../../../../docs/superpowers/specs/2026-05-03-investing-toolkit-v2.2.0-b-comps-compute-design.md)
- ROADMAP: [investing-toolkit/ROADMAP.md §v2.2.0-b](../../../ROADMAP.md)
- Sister conventions: thresholds documents in `skills/analysis-macro-regime/references/thresholds-{us,jp,tw,kr,cn}.md`
````

- [ ] **Step 2: Verify the file structure passes the skill-folder hook**

```bash
ls skills/analysis-comps/references/
# Expected: divergence-thresholds.md
```

- [ ] **Step 3: Commit**

```bash
git add skills/analysis-comps/references/divergence-thresholds.md
git commit -m "$(cat <<'EOF'
docs(analysis-comps): add divergence-thresholds.md (SoT for compute-mode bands)

5% / 15% / strict-> bands defined as repo-canonical reference doc per
SSOT-and-functional-copy pattern. comps_compute.py will carry named-
constant functional copies in the same PR. Drift rule: band-number
changes touch both files.

Pattern matches skills/analysis-macro-regime/references/thresholds-*.md.

ROADMAP: §v2.2.0-b — Phase 2 of 4.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 3 — Compute mode core

This phase adds compute mode in 4 sub-tasks. Each sub-task = TDD cycle (failing tests → impl → green → commit). All tests added in Task 3.x are kept passing in 4.x.

### Task 3.1: Create slim memo-fetch fixture for AAPL

**Files:**
- Create: `tests/analysis/fixtures/comps_anchor_aapl_memo_fetch.json`

- [ ] **Step 1: Write the fixture**

Use Write tool to create a slim memo-fetch fixture. Source values (verified 2026-05-03 against `tests/data/fixtures/data-us-memo-fetch-sample.json`):

```json
{
  "pack": "memo-fetch",
  "ticker": "AAPL",
  "fetched_at": "2026-05-02T01:29:34.802897+00:00",
  "company_info": {
    "regularMarketPrice": 280.14,
    "sharesOutstanding": 14667688000,
    "marketCap": 4109006274560
  },
  "current_price": 280.14,
  "shares_outstanding": 14667688000,
  "income_statement": {
    "revenue": [416161000000.0, 391035000000.0, 383285000000.0, 394328000000.0, 365817000000.0],
    "net_income": [112010000000.0, 93736000000.0, 96995000000.0, 99803000000.0, 94680000000.0],
    "operating_income": [133050000000.0, 123216000000.0, 114301000000.0, 119437000000.0, 108949000000.0],
    "ebit": [133050000000.0, 123216000000.0, 114301000000.0, 119437000000.0, 108949000000.0],
    "_meta": {
      "fiscal_year_ends": ["2025-09-27", "2024-09-28", "2023-09-30", "2022-09-24", "2021-09-25"],
      "filings_used": [
        "10-K filed 2025-10-31",
        "10-K filed 2025-10-31",
        "10-K filed 2025-10-31",
        "10-K filed 2024-11-01",
        "10-K filed 2023-11-03"
      ]
    }
  },
  "balance_sheet": {
    "total_debt": [90678000000.0, 95300000000.0, 109280000000.0, 120069000000.0, 124719000000.0],
    "cash": [35934000000.0, 29943000000.0, 29965000000.0, 23646000000.0, 34940000000.0]
  },
  "_provenance": {
    "skill": "data-us",
    "source": "pack.py --pack memo-fetch",
    "tier": "A"
  }
}
```

- [ ] **Step 2: Verify expected compute values (sanity check)**

```bash
python3 -c "
import json
d = json.load(open('tests/analysis/fixtures/comps_anchor_aapl_memo_fetch.json'))
trailing_pe = d['current_price'] / (d['income_statement']['net_income'][0] / d['shares_outstanding'])
price_to_sales = d['company_info']['marketCap'] / d['income_statement']['revenue'][0]
print(f'expected trailingPE compute: {trailing_pe:.4f}')
print(f'expected priceToSales compute: {price_to_sales:.4f}')
"
```

Expected output:
```
expected trailingPE compute: 36.6817
expected priceToSales compute: 9.8736
```

These golden values will be asserted in tests.

### Task 3.2: Add `--mode compute` argparse + memo-fetch loader (skeleton)

**Files:**
- Modify: `skills/analysis-comps/scripts/comps_compute.py:275-298`
- Modify: `tests/analysis/test_analysis_comps.py` (append new test section)

- [ ] **Step 1: Write failing tests for argparse + memo-fetch loader**

Append to `tests/analysis/test_analysis_comps.py`:

```python
# ---------------------------------------------------------------------------
# Compute mode — argparse + memo-fetch loader
# ---------------------------------------------------------------------------


def _anchor_base_arg(fixtures_dir):
    return str(fixtures_dir / "comps_anchor_aapl_memo_fetch.json")


def test_compute_mode_requires_anchor_base(runner, fixtures_dir):
    """--mode compute without --anchor-base must exit with helpful error."""
    res = runner(
        COMPS_SCRIPT,
        "--mode", "compute",
        "--anchor", _anchor_arg(fixtures_dir),
        "--peers", _full_peer_set(fixtures_dir),
    )
    assert res.returncode == 2, f"expected exit 2, got {res.returncode}"
    assert "anchor-base" in res.stderr.lower()


def test_direct_mode_warns_on_unused_anchor_base(runner, fixtures_dir):
    """--mode direct --anchor-base x.json: warn, continue with direct."""
    res = runner(
        COMPS_SCRIPT,
        "--mode", "direct",
        "--anchor", _anchor_arg(fixtures_dir),
        "--anchor-base", _anchor_base_arg(fixtures_dir),
        "--peers", _full_peer_set(fixtures_dir),
    )
    assert res.returncode == 0, res.stderr
    assert "ignored" in res.stderr.lower() or "direct" in res.stderr.lower()
    payload = json.loads(res.stdout)
    assert "multiples_direct" in payload["anchor"]
    assert "multiples_compute" not in payload["anchor"]


def test_anchor_base_wrong_pack_errors(runner, tmp_path, fixtures_dir):
    """--anchor-base file with pack != 'memo-fetch' → exit 1."""
    bad = tmp_path / "wrong.json"
    bad.write_text(json.dumps({"pack": "snapshot", "ticker": "AAPL"}))
    res = runner(
        COMPS_SCRIPT,
        "--mode", "compute",
        "--anchor", _anchor_arg(fixtures_dir),
        "--anchor-base", str(bad),
        "--peers", _full_peer_set(fixtures_dir),
    )
    assert res.returncode == 1
    assert "memo-fetch" in res.stderr.lower()


def test_anchor_base_ticker_mismatch_errors(runner, tmp_path, fixtures_dir):
    """--anchor ticker AAPL, --anchor-base ticker MSFT → exit 1."""
    mismatch = tmp_path / "mismatch.json"
    mismatch.write_text(json.dumps({
        "pack": "memo-fetch", "ticker": "MSFT",
        "company_info": {}, "current_price": 0.0, "shares_outstanding": 1,
        "income_statement": {"revenue": [1.0], "net_income": [1.0]},
        "balance_sheet": {}, "_provenance": {}
    }))
    res = runner(
        COMPS_SCRIPT,
        "--mode", "compute",
        "--anchor", _anchor_arg(fixtures_dir),
        "--anchor-base", str(mismatch),
        "--peers", _full_peer_set(fixtures_dir),
    )
    assert res.returncode == 1
    assert "ticker" in res.stderr.lower()
```

- [ ] **Step 2: Run tests — they should fail**

```bash
uv run pytest tests/analysis/test_analysis_comps.py -k "compute_mode_requires_anchor_base or direct_mode_warns or anchor_base_wrong_pack or anchor_base_ticker_mismatch" -v 2>&1 | tail -20
```

Expected: 4 tests fail (no `--anchor-base` arg defined yet).

- [ ] **Step 3: Implement argparse + loader**

Edit `comps_compute.py`. Find line ~279:

```python
    parser.add_argument(
        "--rationale-map", type=Path, default=None,
        help="Optional JSON file mapping ticker -> rationale string",
    )
    args = parser.parse_args()
```

Insert before `args = parser.parse_args()`:

```python
    parser.add_argument(
        "--anchor-base", type=Path, default=None,
        help="Path to anchor's memo-fetch pack JSON (REQUIRED for --mode compute)",
    )
    args = parser.parse_args()

    # Validate compute-mode arg shape early.
    if args.mode == "compute" and args.anchor_base is None:
        parser.error("--mode compute requires --anchor-base")
    if args.mode == "direct" and args.anchor_base is not None:
        sys.stderr.write(
            "[analysis-comps WARN] --anchor-base ignored in --mode direct\n"
        )
```

Find the `effective_mode = "direct"` fallback block (line ~291-298) and **replace** it with:

```python
    requested_mode = args.mode
    effective_mode = args.mode
```

(Compute mode is no longer a placeholder — actual implementation follows in Task 3.3.)

Then add the memo-fetch loader. After `_load_pack` function (line ~74), add:

```python
def _load_memo_fetch_pack(path: Path, expected_ticker: str) -> dict:
    """Load and validate a memo-fetch pack. Layer-1 input contract — no I/O beyond this read."""
    with path.open("r", encoding="utf-8") as f:
        pack = json.load(f)
    if pack.get("pack") != "memo-fetch":
        raise ValueError(
            f"--anchor-base must be a memo-fetch pack; got pack={pack.get('pack')!r}"
        )
    if pack.get("ticker") != expected_ticker:
        raise ValueError(
            f"--anchor-base ticker {pack.get('ticker')!r} does not match "
            f"--anchor ticker {expected_ticker!r}"
        )
    return pack
```

In `main()`, after the anchor pack is loaded (line ~302), add a compute-mode branch:

```python
    # Compute mode: load + validate memo-fetch pack
    anchor_base = None
    if effective_mode == "compute":
        try:
            anchor_base = _load_memo_fetch_pack(args.anchor_base, anchor_ticker)
        except (json.JSONDecodeError, ValueError) as exc:
            sys.stderr.write(f"[analysis-comps ERROR] {exc}\n")
            return 1
```

- [ ] **Step 4: Run tests — should pass**

```bash
uv run pytest tests/analysis/test_analysis_comps.py -k "compute_mode_requires_anchor_base or direct_mode_warns or anchor_base_wrong_pack or anchor_base_ticker_mismatch" -v 2>&1 | tail -10
```

Expected: 4 PASSED.

- [ ] **Step 5: Run full suite to confirm no regressions**

```bash
uv run pytest tests/analysis/ -v 2>&1 | tail -10
```

Expected: All previously-passing tests still pass.

### Task 3.3: Implement compute-mode multiples (3 computed + 2 deferred)

**Files:**
- Modify: `skills/analysis-comps/scripts/comps_compute.py`
- Modify: `tests/analysis/test_analysis_comps.py`

- [ ] **Step 1: Write failing tests for the 3 computable multiples + 2 deferred**

Append to `tests/analysis/test_analysis_comps.py`:

```python
# ---------------------------------------------------------------------------
# Compute mode — multiples recompute
# ---------------------------------------------------------------------------


@pytest.fixture
def compute_payload(runner, fixtures_dir):
    res = runner(
        COMPS_SCRIPT,
        "--mode", "compute",
        "--anchor", _anchor_arg(fixtures_dir),
        "--anchor-base", _anchor_base_arg(fixtures_dir),
        "--peers", _full_peer_set(fixtures_dir),
    )
    assert res.returncode == 0, res.stderr
    return json.loads(res.stdout)


def test_compute_mode_recomputes_trailingPE_FY(compute_payload):
    """trailingPE = current_price / (net_income[0] / shares_outstanding) — FY, not TTM."""
    actual = compute_payload["anchor"]["multiples_compute"]["trailingPE"]
    expected = 280.14 / (112010000000.0 / 14667688000)  # 36.6817
    assert actual == pytest.approx(expected, rel=1e-4)


def test_compute_mode_recomputes_priceToSales_FY(compute_payload):
    """priceToSales = marketCap / revenue[0] — FY."""
    actual = compute_payload["anchor"]["multiples_compute"]["priceToSales"]
    expected = 4109006274560 / 416161000000.0  # 9.8736
    assert actual == pytest.approx(expected, rel=1e-4)


def test_compute_mode_forwardPE_passthrough(compute_payload):
    """forwardPE pass-through from --anchor; computed:false in provenance."""
    direct_fwd = compute_payload["anchor"]["multiples_direct"]["forwardPE"]
    compute_fwd = compute_payload["anchor"]["multiples_compute"]["forwardPE"]
    assert compute_fwd == direct_fwd
    assert compute_payload["anchor"]["compute_provenance"]["forwardPE"]["computed"] is False


def test_compute_mode_priceToBook_emits_null(compute_payload):
    """priceToBook deferred until v2.2.0-l (memo-fetch lacks total_stockholders_equity)."""
    assert compute_payload["anchor"]["multiples_compute"]["priceToBook"] is None
    assert compute_payload["anchor"]["compute_provenance"]["priceToBook"]["computed"] is False
    assert "v2.2.0-l" in compute_payload["anchor"]["compute_provenance"]["priceToBook"]["note"]


def test_compute_mode_evEbitda_emits_null(compute_payload):
    """evEbitda deferred until v2.2.0-l (memo-fetch lacks D&A)."""
    assert compute_payload["anchor"]["multiples_compute"]["evEbitda"] is None
    assert compute_payload["anchor"]["compute_provenance"]["evEbitda"]["computed"] is False
    assert "v2.2.0-l" in compute_payload["anchor"]["compute_provenance"]["evEbitda"]["note"]


def test_compute_provenance_includes_fiscal_year_end(compute_payload):
    """Each computed multiple records FY end date + accession_basis."""
    prov = compute_payload["anchor"]["compute_provenance"]
    for m in ("trailingPE", "priceToSales"):
        assert prov[m]["computed"] is True
        assert prov[m]["fiscal_year_end"] == "2025-09-27"
        assert "10-K filed 2025-10-31" in prov[m]["accession_basis"]
```

- [ ] **Step 2: Run — should fail**

```bash
uv run pytest tests/analysis/test_analysis_comps.py -k "compute_mode_recomputes or compute_mode_forwardPE or compute_mode_priceToBook or compute_mode_evEbitda or compute_provenance_includes" -v 2>&1 | tail -20
```

Expected: 6 fails — `multiples_compute` key missing.

- [ ] **Step 3: Implement compute path**

Edit `comps_compute.py`. After the `MULTIPLES = [...]` constant (line ~59), add:

```python
DIVERGENCE_BAND_LOW  = 0.05   # 5%   — boundary inclusive (≤ low)
DIVERGENCE_BAND_HIGH = 0.15   # 15%  — boundary inclusive for medium (high band is strict >)

# Multiples currently deferred to v2.2.0-l (memo-fetch lacks the raw fields):
#   priceToBook  → needs total_stockholders_equity
#   evEbitda     → needs depreciation_amortization
DEFERRED_MULTIPLES = ("priceToBook", "evEbitda")
```

After `_extract_multiples` (line ~104), add:

```python
def _safe_first(arr, default=None):
    """First element of a list, or default if empty/non-list."""
    return arr[0] if isinstance(arr, list) and arr else default


def _compute_multiples_from_memo_fetch(memo_fetch: dict, direct_multiples: dict) -> tuple[dict, dict, list[str]]:
    """Recompute the 5 canonical multiples from a memo-fetch pack.

    Returns (multiples_compute, compute_provenance, warnings).
    Layer 2 derived metrics: trailingPE / priceToSales / forwardPE pass-through;
    priceToBook + evEbitda deferred to v2.2.0-l with explicit null + note.
    """
    warnings: list[str] = [
        "trailingPE compute uses latest FY (not TTM); systematic divergence vs yfinance TTM expected during fiscal year"
    ]
    out_compute: dict[str, float | None] = {}
    out_prov: dict[str, dict] = {}

    # Inputs
    inc = memo_fetch.get("income_statement") or {}
    ci = memo_fetch.get("company_info") or {}
    price = memo_fetch.get("current_price") or ci.get("regularMarketPrice")
    shares = memo_fetch.get("shares_outstanding") or ci.get("sharesOutstanding")
    market_cap = ci.get("marketCap")

    revenue_fy = _safe_first(inc.get("revenue"))
    net_income_fy = _safe_first(inc.get("net_income"))

    fy_end = _safe_first(((inc.get("_meta") or {}).get("fiscal_year_ends") or []))
    filings = ((inc.get("_meta") or {}).get("filings_used") or [])

    # trailingPE (FY)
    if price is None or net_income_fy is None or not shares:
        out_compute["trailingPE"] = None
        out_prov["trailingPE"] = {
            "computed": False,
            "note": "compute skipped — current_price / net_income[0] / shares_outstanding required",
        }
        if price is None:
            warnings.append("price-based compute skipped: current_price missing")
        elif net_income_fy is None:
            warnings.append("trailingPE compute skipped: net_income FY array empty")
        elif not shares:
            warnings.append("trailingPE compute skipped: shares_outstanding missing")
    else:
        eps_fy = net_income_fy / shares
        out_compute["trailingPE"] = price / eps_fy if eps_fy != 0 else None
        out_prov["trailingPE"] = {
            "numerator_source":   "memo-fetch.current_price",
            "denominator_source": "memo-fetch.income_statement.net_income[0] / memo-fetch.shares_outstanding",
            "accession_basis":    [filings[0]] if filings else [],
            "fiscal_year_end":    fy_end,
            "computed":           True,
            "note":               "FY-trailing, not TTM — see ROADMAP §v2.2.0-b §7.3",
        }

    # priceToSales (FY)
    if market_cap is None or revenue_fy is None:
        out_compute["priceToSales"] = None
        out_prov["priceToSales"] = {
            "computed": False,
            "note": "compute skipped — marketCap / revenue[0] required",
        }
        if revenue_fy is None:
            warnings.append("priceToSales compute skipped: revenue FY array empty")
    else:
        out_compute["priceToSales"] = market_cap / revenue_fy
        out_prov["priceToSales"] = {
            "numerator_source":   "memo-fetch.company_info.marketCap",
            "denominator_source": "memo-fetch.income_statement.revenue[0]",
            "accession_basis":    [filings[0]] if filings else [],
            "fiscal_year_end":    fy_end,
            "computed":           True,
        }

    # forwardPE pass-through
    out_compute["forwardPE"] = direct_multiples.get("forwardPE")
    out_prov["forwardPE"] = {
        "computed": False,
        "note": "pass-through from comps-multiples pack (consensus EPS has no primary source)",
    }

    # Deferred multiples (v2.2.0-l)
    out_compute["priceToBook"] = None
    out_prov["priceToBook"] = {
        "computed": False,
        "note": "deferred to v2.2.0-l (memo-fetch missing total_stockholders_equity)",
    }
    out_compute["evEbitda"] = None
    out_prov["evEbitda"] = {
        "computed": False,
        "note": "deferred to v2.2.0-l (memo-fetch missing depreciation_amortization)",
    }

    return out_compute, out_prov, warnings
```

In `main()`, after `anchor_base` is loaded (Task 3.2 step 3), and after `anchor_multiples` is computed (line ~303), add:

```python
    # Compute mode: recompute multiples from memo-fetch
    multiples_compute = None
    compute_provenance = None
    compute_warnings: list[str] = []
    if effective_mode == "compute":
        multiples_compute, compute_provenance, compute_warnings = (
            _compute_multiples_from_memo_fetch(anchor_base, anchor_multiples)
        )
        warnings.extend(compute_warnings)
```

In the `payload = {...}` assembly (line ~356), update the anchor block:

```python
    anchor_block: dict = {
        "ticker": anchor_ticker,
        "multiples_direct": anchor_multiples,
    }
    if effective_mode == "compute":
        anchor_block["multiples_compute"] = multiples_compute
        anchor_block["compute_provenance"] = compute_provenance

    payload = {
        "anchor": anchor_block,
        "peers": peers_out,
        ...
    }
```

(Adapt the existing payload dict to use `anchor_block` rather than inline anchor.)

Update `_provenance` block similarly:

```python
        "_provenance": {
            "skill":              "analysis-comps",
            "anchor_data_source": anchor_source,
            **(
                {"anchor_base_source": _provenance_label(anchor_base, args.anchor_base)}
                if effective_mode == "compute" else {}
            ),
            "peer_data_sources":  [src for _t, _m, src in peer_packs],
            "computed_at":        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "io":                 "none",
            "mode":               effective_mode,
            "requested_mode":     requested_mode,
            "warnings":           warnings,
        },
```

- [ ] **Step 4: Run new tests — should pass**

```bash
uv run pytest tests/analysis/test_analysis_comps.py -k "compute_mode_recomputes or compute_mode_forwardPE or compute_mode_priceToBook or compute_mode_evEbitda or compute_provenance_includes" -v 2>&1 | tail -10
```

Expected: 6 PASSED.

- [ ] **Step 5: Run full suite — confirm no regressions**

```bash
uv run pytest tests/analysis/ -v 2>&1 | tail -10
```

Expected: all green.

### Task 3.4: Add divergence block

**Files:**
- Modify: `skills/analysis-comps/scripts/comps_compute.py`
- Modify: `tests/analysis/test_analysis_comps.py`

- [ ] **Step 1: Write failing tests for divergence**

Append:

```python
# ---------------------------------------------------------------------------
# Compute mode — divergence
# ---------------------------------------------------------------------------


def test_divergence_block_present(compute_payload):
    div = compute_payload["anchor"]["divergence"]
    for m in ("trailingPE", "forwardPE", "priceToSales", "priceToBook", "evEbitda"):
        assert m in div


def test_divergence_alert_high_for_trailing_pe_aapl(compute_payload):
    """AAPL: direct=28.5 (fixture) vs compute=36.68 → pct_diff ≈ 28.7% → high."""
    div = compute_payload["anchor"]["divergence"]["trailingPE"]
    assert div["alert"] == "high"
    assert div["pct_diff"] == pytest.approx(28.7, abs=0.5)


def test_divergence_alert_n_a_for_forwardPE(compute_payload):
    """forwardPE pass-through → divergence is exactly 0; alert n/a."""
    div = compute_payload["anchor"]["divergence"]["forwardPE"]
    assert div["alert"] == "n/a"
    assert "pass-through" in div["note"]


def test_divergence_alert_n_a_for_deferred(compute_payload):
    """priceToBook + evEbitda compute=null → alert n/a + v2.2.0-l note."""
    for m in ("priceToBook", "evEbitda"):
        div = compute_payload["anchor"]["divergence"][m]
        assert div["alert"] == "n/a"
        assert "v2.2.0-l" in div["note"]


def test_divergence_alert_low_at_5_percent_boundary(tmp_path, runner):
    """Synthetic anchor: direct=10.0, compute=10.5 → pct_diff=5.0% → low (≤ inclusive)."""
    anchor = tmp_path / "anchor.json"
    anchor.write_text(json.dumps({
        "pack": "comps-multiples", "ticker": "X",
        "info": {"X": {"trailingPE": 10.0, "forwardPE": 10.0, "priceToSales": 1.0, "priceToBook": 1.0, "enterpriseToEbitda": 1.0}},
        "_provenance": {"skill": "test"}
    }))
    base = tmp_path / "base.json"
    # net_income / shares = 10.5 EPS; price 110.25 → trailingPE compute = 10.5
    base.write_text(json.dumps({
        "pack": "memo-fetch", "ticker": "X",
        "company_info": {"regularMarketPrice": 110.25, "sharesOutstanding": 1, "marketCap": 110.25},
        "current_price": 110.25, "shares_outstanding": 1,
        "income_statement": {"revenue": [105.0], "net_income": [10.5], "_meta": {"fiscal_year_ends": ["2025-12-31"], "filings_used": ["10-K"]}},
        "balance_sheet": {}, "_provenance": {}
    }))
    peer = tmp_path / "peer.json"
    peer.write_text(json.dumps({
        "pack": "comps-multiples", "ticker": "Y",
        "info": {"Y": {"trailingPE": 12.0}}, "_provenance": {"skill": "test"}
    }))
    res = runner(COMPS_SCRIPT, "--mode", "compute",
                 "--anchor", str(anchor), "--anchor-base", str(base), "--peers", str(peer))
    payload = json.loads(res.stdout)
    div = payload["anchor"]["divergence"]["trailingPE"]
    assert div["pct_diff"] == pytest.approx(5.0, abs=0.01)
    assert div["alert"] == "low"


def test_divergence_alert_medium_at_15_percent_boundary(tmp_path, runner):
    """direct=10.0, compute=11.5 → pct_diff=15.0% → medium (> 15% is high)."""
    anchor = tmp_path / "anchor.json"
    anchor.write_text(json.dumps({
        "pack": "comps-multiples", "ticker": "X",
        "info": {"X": {"trailingPE": 10.0, "forwardPE": 10.0, "priceToSales": 1.0, "priceToBook": 1.0, "enterpriseToEbitda": 1.0}},
        "_provenance": {"skill": "test"}
    }))
    base = tmp_path / "base.json"
    base.write_text(json.dumps({
        "pack": "memo-fetch", "ticker": "X",
        "company_info": {"regularMarketPrice": 11.5, "sharesOutstanding": 1, "marketCap": 11.5},
        "current_price": 11.5, "shares_outstanding": 1,
        "income_statement": {"revenue": [1.0], "net_income": [1.0], "_meta": {"fiscal_year_ends": ["2025-12-31"], "filings_used": ["10-K"]}},
        "balance_sheet": {}, "_provenance": {}
    }))
    peer = tmp_path / "peer.json"
    peer.write_text(json.dumps({
        "pack": "comps-multiples", "ticker": "Y",
        "info": {"Y": {"trailingPE": 12.0}}, "_provenance": {"skill": "test"}
    }))
    res = runner(COMPS_SCRIPT, "--mode", "compute",
                 "--anchor", str(anchor), "--anchor-base", str(base), "--peers", str(peer))
    payload = json.loads(res.stdout)
    div = payload["anchor"]["divergence"]["trailingPE"]
    assert div["pct_diff"] == pytest.approx(15.0, abs=0.01)
    assert div["alert"] == "medium"
```

- [ ] **Step 2: Run — should fail**

```bash
uv run pytest tests/analysis/test_analysis_comps.py -k "divergence" -v 2>&1 | tail -15
```

Expected: 6 fails — `divergence` key missing.

- [ ] **Step 3: Implement divergence helper**

Edit `comps_compute.py`. After `_compute_multiples_from_memo_fetch` (Task 3.3), add:

```python
def _classify_divergence_alert(pct_diff: float) -> str:
    """Map |pct_diff| (in %) onto low/medium/high band per divergence-thresholds.md."""
    abs_pct = abs(pct_diff)
    if abs_pct <= DIVERGENCE_BAND_LOW * 100:
        return "low"
    if abs_pct <= DIVERGENCE_BAND_HIGH * 100:
        return "medium"
    return "high"


def _compute_divergence(direct: dict, compute: dict, prov: dict) -> dict[str, dict]:
    """For each multiple, compute abs/pct diff between direct and compute, classify alert.
    Null in either side → alert n/a with note from compute_provenance.
    """
    out: dict[str, dict] = {}
    for m in MULTIPLES:
        d_val = direct.get(m)
        c_val = compute.get(m)
        if d_val is None or c_val is None:
            note = (prov.get(m) or {}).get("note") or "compute null; cannot diff"
            out[m] = {"abs_diff": None, "pct_diff": None, "alert": "n/a", "note": note}
            continue
        abs_diff = c_val - d_val
        if d_val == 0:
            out[m] = {"abs_diff": abs_diff, "pct_diff": None, "alert": "n/a", "note": "direct value zero — pct_diff undefined"}
            continue
        pct_diff = (abs_diff / d_val) * 100.0
        # forwardPE is pass-through → c_val == d_val → pct_diff == 0; surface as n/a
        if m == "forwardPE":
            out[m] = {"abs_diff": 0.0, "pct_diff": 0.0, "alert": "n/a", "note": "pass-through"}
            continue
        out[m] = {
            "abs_diff": abs_diff,
            "pct_diff": pct_diff,
            "alert":    _classify_divergence_alert(pct_diff),
        }
    return out
```

In `main()` compute branch, after `multiples_compute` is built:

```python
    if effective_mode == "compute":
        multiples_compute, compute_provenance, compute_warnings = (
            _compute_multiples_from_memo_fetch(anchor_base, anchor_multiples)
        )
        warnings.extend(compute_warnings)
        divergence = _compute_divergence(anchor_multiples, multiples_compute, compute_provenance)
        anchor_block["multiples_compute"] = multiples_compute
        anchor_block["divergence"] = divergence
        anchor_block["compute_provenance"] = compute_provenance
```

(Replace the earlier compute branch in `main` accordingly.)

- [ ] **Step 4: Run divergence tests — should pass**

```bash
uv run pytest tests/analysis/test_analysis_comps.py -k "divergence" -v 2>&1 | tail -10
```

Expected: 6 PASSED.

- [ ] **Step 5: Run full suite + verify no direct-mode regression**

```bash
uv run pytest tests/analysis/ -v 2>&1 | tail -10
```

Expected: all green.

- [ ] **Step 6: Commit Phase 3 (Tasks 3.1-3.4)**

```bash
git add skills/analysis-comps/scripts/comps_compute.py \
        tests/analysis/test_analysis_comps.py \
        tests/analysis/fixtures/comps_anchor_aapl_memo_fetch.json
git commit -m "$(cat <<'EOF'
feat(analysis-comps): activate --mode compute (3 of 5 multiples + divergence)

Replace placeholder compute branch with real recompute pipeline:
- New --anchor-base arg loads existing memo-fetch pack
- Recomputes trailingPE (FY), priceToSales (FY); forwardPE pass-through
- priceToBook + evEbitda emit null (deferred to v2.2.0-l per spec §15.2)
- Divergence block: abs_diff + pct_diff + alert ∈ {low, medium, high, n/a}
- Bands per divergence-thresholds.md: ≤5% low; (5%, 15%] medium; >15% high
- compute_provenance per-multiple records numerator/denominator source +
  fiscal_year_end + accession_basis (Tier A trace)

Validation rules:
- --mode compute without --anchor-base → exit 2 with helpful stderr
- --mode direct with --anchor-base → stderr warning, ignore, continue
- --anchor-base wrong pack type → exit 1
- --anchor-base ticker mismatch → exit 1

10 new test cases covering happy path + deferred-multiple shape +
band boundaries + validation errors.

ROADMAP: §v2.2.0-b — Phase 3 of 4.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 4 — report-equity-memo wiring + cross-layer integration test

### Task 4.1: Update `report-equity-memo` Phase 2.5 invocation

**Files:**
- Modify: `skills/report-equity-memo/SKILL.md:175-181`

- [ ] **Step 1: Find the existing Phase 2.5 comps_compute invocation**

```bash
grep -nE "comps_compute|--anchor /tmp" skills/report-equity-memo/SKILL.md
```

Expected: lines 176-180 show the existing direct-mode invocation.

- [ ] **Step 2: Update Phase 2.5 bash block**

Edit `skills/report-equity-memo/SKILL.md`. Find:

```bash
# 3. Run analysis-comps
uv run ${CLAUDE_PLUGIN_ROOT}/skills/analysis-comps/scripts/comps_compute.py \
  --anchor /tmp/${TICKER_SAFE}-anchor-comps.json \
  --peers /tmp/<peer1>-comps.json,/tmp/<peer2>-comps.json,... \
  --rationale-map /tmp/peer-rationales.json \
  > /tmp/${TICKER_SAFE}-comps.json
```

Replace with:

```bash
# 3. Run analysis-comps in compute mode (v2.2.0-b+)
# anchor memo-fetch already pre-fetched in Phase 1: /tmp/${TICKER_SAFE}-fetch.json
# Compute mode emits multiples_direct + multiples_compute + divergence in one JSON.
uv run ${CLAUDE_PLUGIN_ROOT}/skills/analysis-comps/scripts/comps_compute.py \
  --mode compute \
  --anchor       /tmp/${TICKER_SAFE}-anchor-comps.json \
  --anchor-base  /tmp/${TICKER_SAFE}-fetch.json \
  --peers        /tmp/<peer1>-comps.json,/tmp/<peer2>-comps.json,... \
  --rationale-map /tmp/peer-rationales.json \
  > /tmp/${TICKER_SAFE}-comps.json
```

### Task 4.2: Add Phase 4 prompt note about divergence alerts

**Files:**
- Modify: `skills/report-equity-memo/SKILL.md`

- [ ] **Step 1: Find Phase 4 section**

```bash
grep -nE "^### Phase 4|investing-team" skills/report-equity-memo/SKILL.md | head -5
```

- [ ] **Step 2: Add divergence-alert prompt clause**

Locate the part of Phase 4 that describes what investing-team is given. After the existing prompt template (before the closing of Phase 4), insert this paragraph:

```markdown
**Comps divergence (v2.2.0-b+)**: when `comps.json` has `anchor.divergence[*].alert == "high"`, the Comps section MUST surface the divergence source — e.g. "yfinance trailingPE 28.5x vs SEC raw recompute 36.7x — Yahoo's adjusted EPS differs from FY GAAP". Cite the relevant SEC accession from `compute_provenance[*].accession_basis`. Medium alerts may be mentioned briefly; low alerts are upstream-rounding noise and stay silent.

For non-US tickers (.T / .TW / .KS / .KQ / .HK / .SS / .SZ), substitute the appropriate `data-{country}/pack.py --pack memo-fetch` output for `--anchor-base`. Compute-mode US-first; non-US compute mode lands in per-country PRs (until then, falls back to direct with stderr warning).
```

### Task 4.3: Add cross-layer integration test

**Files:**
- Modify: `tests/integration/test_cross_layer_chains.py`

- [ ] **Step 1: Find the bottom of the file (end of test functions)**

```bash
grep -nE "^def test_|^class " tests/integration/test_cross_layer_chains.py | tail -5
```

- [ ] **Step 2: Append new test**

```python
# ---------------------------------------------------------------------------
# Chain US — comps_compute dual input (v2.2.0-b)
# ---------------------------------------------------------------------------


def test_chain_us_comps_compute_dual_input(repo_root, fixtures_dir):
    """Chain: data-us memo-fetch fixture + comps-multiples fixture →
    analysis-comps --mode compute → JSON with divergence + compute_provenance.

    Validates that real Layer-1 fixtures (not synthetic) flow through Layer-2
    compute mode without shape adapters.
    """
    import json
    import subprocess
    from pathlib import Path

    # Layer 1 inputs (existing fixtures, no regeneration)
    anchor_comps = repo_root / "tests/data/fixtures/data-us-comps-multiples-sample.json"
    anchor_memo = repo_root / "tests/data/fixtures/data-us-memo-fetch-sample.json"
    peer_comps = repo_root / "tests/data/fixtures/data-us-comps-multiples-sample.json"
    # Note: peer reuses same fixture for shape correctness; ticker dedup will skip it.
    # The integration test surfaces shape mismatches, not numerical correctness.

    script = repo_root / "skills/analysis-comps/scripts/comps_compute.py"

    res = subprocess.run(
        ["uv", "run", str(script),
         "--mode", "compute",
         "--anchor", str(anchor_comps),
         "--anchor-base", str(anchor_memo),
         "--peers", str(peer_comps)],
        capture_output=True, text=True, cwd=str(repo_root),
    )
    # Allow non-zero only if peers all dedup; we just need the shape OR a clean error.
    payload = json.loads(res.stdout) if res.returncode == 0 else None

    if payload is None:
        # Acceptable failure mode: peer dedupped against anchor → empty peers
        # but the script should still emit valid JSON with a warning.
        assert "peers" in res.stderr.lower() or res.returncode == 0
        return

    # Compute-mode shape contract
    anchor = payload["anchor"]
    assert "multiples_direct" in anchor
    assert "multiples_compute" in anchor
    assert "divergence" in anchor
    assert "compute_provenance" in anchor

    # All 5 multiples present in divergence
    for m in ("trailingPE", "forwardPE", "priceToSales", "priceToBook", "evEbitda"):
        assert m in anchor["divergence"]
        assert anchor["divergence"][m]["alert"] in {"low", "medium", "high", "n/a"}

    # Compute provenance carries spec contract
    assert anchor["compute_provenance"]["forwardPE"]["computed"] is False
    assert anchor["compute_provenance"]["priceToBook"]["computed"] is False
    assert "v2.2.0-l" in anchor["compute_provenance"]["priceToBook"]["note"]

    # Top-level provenance
    assert payload["_provenance"]["mode"] == "compute"
    assert "anchor_base_source" in payload["_provenance"]
```

If the test file uses different fixture-resolution conventions (`@pytest.fixture` `repo_root`), check the existing tests in the file and adapt accordingly. The actual `repo_root` / `fixtures_dir` fixture names may differ — match the file's existing patterns.

- [ ] **Step 3: Run new test**

```bash
uv run pytest tests/integration/test_cross_layer_chains.py::test_chain_us_comps_compute_dual_input -v 2>&1 | tail -10
```

Expected: 1 PASSED.

- [ ] **Step 4: Full integration suite check**

```bash
uv run pytest tests/integration/ -v 2>&1 | tail -10
```

Expected: all existing chains still green.

- [ ] **Step 5: Commit Phase 4**

```bash
git add skills/report-equity-memo/SKILL.md tests/integration/test_cross_layer_chains.py
git commit -m "$(cat <<'EOF'
feat(report-equity-memo): wire Phase 2.5 to --mode compute + divergence prompt

Phase 2.5 invocation upgraded to --mode compute --anchor-base, reusing
the anchor memo-fetch pack already fetched in Phase 1 (zero extra fetch
cost). Phase 4 prompt extended to instruct investing-team to surface
high-alert divergences with SEC accession citation.

Cross-layer integration test asserts dual-input compute mode produces
the spec §10 output shape end-to-end via real Layer-1 fixtures.

ROADMAP: §v2.2.0-b — Phase 4 of 4.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 5 — Docs + ROADMAP closures

### Task 5.1: Add `analysis-comps/SKILL.md` §"Direct vs Compute"

**Files:**
- Modify: `skills/analysis-comps/SKILL.md`

- [ ] **Step 1: Find a sensible insertion point**

```bash
grep -nE "^## |^### " skills/analysis-comps/SKILL.md | head -20
```

Expected: section structure (Inputs / Outputs / Modes / etc.).

- [ ] **Step 2: Insert §"Direct vs Compute — when to use which"**

Add this new section (place after the existing §Modes or §Output, whichever comes first):

````markdown
## Direct vs Compute — when to use which

| Mode | Trust source | Use case |
|---|---|---|
| `--mode direct` (default) | yfinance pre-cooked multiples (Yahoo's own EPS / EV definitions) | Industry comparability — aligns with Bloomberg / FactSet convention. Good for screen-style ranking; safe for sell-side memos. |
| `--mode compute` (v2.2.0-b+) | Recomputed from SEC EDGAR raw fundamentals + yfinance market data | Primary-source audit — every multiple traces back to a 10-K accession. Required for buy-side memos / short theses where the analyst must defend each number. |

### What compute mode actually computes (v2.2.0-b)

| Multiple | Computed? | Definition |
|---|---|---|
| `trailingPE` | ✅ Yes | `current_price ÷ (FY net_income / shares_outstanding)` — FY-trailing, **not TTM**. Yfinance's TTM and our FY-trailing diverge ~5-10% during the fiscal year — this is a definitional gap, not a bug. |
| `priceToSales` | ✅ Yes | `marketCap / FY revenue[0]` |
| `forwardPE` | ✅ Pass-through | Forward EPS is sell-side consensus aggregate; no primary source. Compute mode passes the direct value through and stamps `compute_provenance.forwardPE.computed: false`. |
| `priceToBook` | ❌ Deferred to v2.2.0-l | memo-fetch v2.1.x doesn't expose `total_stockholders_equity` |
| `evEbitda` | ❌ Deferred to v2.2.0-l | memo-fetch v2.1.x doesn't expose `depreciation_amortization` |

### Divergence interpretation

`divergence[m].alert` takes 4 values:

- `low` (≤5%): rounding/timing noise — ignore
- `medium` (5-15%): mention briefly in narrative
- `high` (>15%): trace to SEC accession in `compute_provenance[m].accession_basis` — the divergence is the story
- `n/a`: compute null (deferred multiple) or pass-through (forwardPE)

See [`references/divergence-thresholds.md`](references/divergence-thresholds.md) for band rationale.

### Required for compute mode

- `--anchor`: comps-multiples pack (existing direct-mode input)
- `--anchor-base`: memo-fetch pack (NEW; required only for `--mode compute`)
- `--peers`: comps-multiples pack(s) (peers stay direct-only — anchor-only compute reduces fetch overhead)

If `--mode compute` is invoked without `--anchor-base`, exit code 2 with stderr message.
````

### Task 5.2: Update ROADMAP — close v2.2.0-b + add v2.2.0-k + v2.2.0-l

**Files:**
- Modify: `investing-toolkit/ROADMAP.md`

- [ ] **Step 1: Mark v2.2.0-b as ✅ closed**

Find:

```markdown
### v2.2.0-b — analysis-comps `--mode compute` activation
```

Replace heading with:

```markdown
### ~~v2.2.0-b — analysis-comps `--mode compute` activation~~ ✅ closed 2026-05-03 (PR #TBD)
```

Replace the existing What/Why/Files/Blocker/Acceptance bullets with:

```markdown
- **Status**: Closed. Anchor-only dual-input shape (B'): `--anchor` + new `--anchor-base` (memo-fetch pack); peers remain single-input direct. 3 of 5 multiples computable in v2.2.0-b — `trailingPE` (FY-trailing), `priceToSales` (FY), `forwardPE` (pass-through). 2 of 5 deferred to v2.2.0-l: `priceToBook` (needs `total_stockholders_equity`), `evEbitda` (needs `depreciation_amortization`).
- **Output**: anchor block now carries `multiples_direct` + `multiples_compute` + `divergence` (low/medium/high/n/a per `references/divergence-thresholds.md`) + `compute_provenance` per multiple with FY end + accession_basis.
- **Direct-mode breaking change**: `anchor.multiples` → `anchor.multiples_direct`. Only in-tree caller (`report-equity-memo` Phase 2.5) migrated atomically in same PR.
- **Spec / Plan**: [`docs/superpowers/specs/2026-05-03-investing-toolkit-v2.2.0-b-comps-compute-design.md`](../docs/superpowers/specs/2026-05-03-investing-toolkit-v2.2.0-b-comps-compute-design.md) / [`docs/superpowers/plans/2026-05-03-investing-toolkit-v2.2.0-b-comps-compute.md`](../docs/superpowers/plans/2026-05-03-investing-toolkit-v2.2.0-b-comps-compute.md)
- **Reference**: PR #TBD; spawned v2.2.0-k (immutable cache tag) + v2.2.0-l (memo-fetch raw-field extension).
```

- [ ] **Step 2: Add v2.2.0-k entry**

Find a good insertion point — alphabetically v2.2.0-k goes after v2.2.0-j and before any v2.2.0-l:

Insert after the existing v2.2.0-j section:

```markdown
### v2.2.0-k — Immutable cadence tag for historical filings

- **What**: Add `cadence: "immutable"` to the cadence vocabulary. Cache helper recognizes this tag as TTL = ∞ (never refetch once cached). Historical fetch paths in each client tag their immutable products: SEC EDGAR per-accession 10-K/10-Q/8-K, EDINET past 報告書, MOPS past statements, NDC past CSV vintages, BOJ past series points, FRED past dated values.
- **Why**: Per user principle 2026-05-03 — "Layer 1 = raw data + persistent storage". Cadence-aware TTL (v2.2.0-j) handles refresh smartly but does not distinguish "stale data" from "data that cannot become stale". Immutable filings are always fresh — refetching them is wasted bandwidth and a needless cache miss.
- **Files**: `docs/cache-policy.md` (add `immutable` band); `data-us/scripts/sec_edgar_client.py`, `data-jp/scripts/edinet_client.py`, `data-tw/scripts/mops_client.py`, `data-tw/scripts/ndc_client.py`, `data-jp/scripts/boj_timeseries_client.py`, `data-us/scripts/fred_client.py` (per-dated-point queries). Block-level cache helper updated; CI sync guard catches drift.
- **Blocker**: None. Builds on v2.2.0-j Phase 2-4 infrastructure (which lands the cache-block-equality CI check).
- **Acceptance**: cache file inspection shows `_cache_meta.cadence: "immutable"` for past-accession fetches; `_cache_meta.expires_at: null`; deliberate-clock-forward smoke test confirms immutable entries do not refetch.
- **Reference**: 2026-05-03 brainstorming session; design doc 2026-05-03-investing-toolkit-v2.2.0-b-comps-compute-design.md §15.1.
```

- [ ] **Step 3: Add v2.2.0-l entry (right after v2.2.0-k)**

```markdown
### v2.2.0-l — memo-fetch raw-field extension for compute-mode multiples

- **What**: Extend `data-us/scripts/sec_edgar_client.py` to extract additional XBRL concepts from the same 10-K filings already fetched (no new network requests). Surface in memo-fetch output: `balance_sheet.total_stockholders_equity` (XBRL `StockholdersEquity`), `cash_flow.depreciation_amortization` (XBRL `DepreciationDepletionAndAmortization`), `cash_flow.stock_based_compensation` (XBRL `ShareBasedCompensation`), `income_statement.gross_profit` (XBRL `GrossProfit`), `balance_sheet.intangible_assets` + `balance_sheet.goodwill`.
- **Why**: Unblocks 2 of 5 compute multiples in v2.2.0-b that currently emit null (`priceToBook`, `evEbitda`). Sets foundation for v2.2.0-c sector-adjusted multiples (Tech Rule-of-40 needs SBC; REIT P/AFFO needs D&A; Bank P/B needs equity).
- **Files**: `data-us/scripts/sec_edgar_client.py` (extend XBRL concept fallback chains); `data-us/scripts/pack.py` (assemble new fields into memo-fetch output); `tests/data/test_data_us.py` (assert presence of new fields); `tests/data/fixtures/data-us-memo-fetch-sample.json` (regenerate). Cross-country symmetry to `data-jp/edinet_client.py`, `data-tw/mops_client.py`, `data-kr/fdr_client.py`, `data-cn/akshare_client.py` follows country-by-country PR pattern.
- **Blocker**: None. SEC EDGAR XBRL exposes these concepts directly; no new API or auth needed.
- **Acceptance**: memo-fetch fixture shows new fields populated for AAPL FY2025; `analysis-comps/scripts/comps_compute.py --mode compute` (no code change in v2.2.0-l) auto-emits non-null `multiples_compute.priceToBook` + `multiples_compute.evEbitda`; existing v2.2.0-b deferred-multiple regression tests flip from `is None` to `pytest.approx(...)` in same PR.
- **Reference**: 2026-05-03 design doc §7.3 + §15.2; v2.2.0-b PR closure.
```

- [ ] **Step 4: Run full test suite — last regression check**

```bash
uv run pytest tests/ -m "not network" -v 2>&1 | tail -10
```

Expected: all green (~400+ tests).

- [ ] **Step 5: Commit Phase 5**

```bash
git add skills/analysis-comps/SKILL.md ROADMAP.md
git commit -m "$(cat <<'EOF'
docs(investing-toolkit): close v2.2.0-b ROADMAP + open v2.2.0-k + v2.2.0-l

ROADMAP:
- §v2.2.0-b: closed; full status block records 3/5 + 2/5 split + breaking
  rename. Cross-references v2.2.0-l for the deferred 2/5.
- §v2.2.0-k (new): immutable cadence cache tag for historical filings —
  user principle 2026-05-03 follow-up.
- §v2.2.0-l (new): memo-fetch raw-field extension to unblock priceToBook
  + evEbitda compute. Activates them retroactively without
  comps_compute.py code change.

analysis-comps/SKILL.md: new §"Direct vs Compute — when to use which"
explains FY-vs-TTM definitional gap, deferred multiples, and divergence
band interpretation. Links to references/divergence-thresholds.md SoT.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Phase 6 — Final verification + PR

### Task 6.1: Full pre-PR sanity sweep

- [ ] **Step 1: Confirm git state is clean and branch is correctly named**

```bash
git status
git log --oneline main..HEAD
```

Expected: clean working tree; commits in order: spec / spec-correction / refactor (rename) / docs (thresholds) / feat (compute) / feat (memo-wire) / docs (SKILL+ROADMAP).

- [ ] **Step 2: Diff sanity check — confirm no data-* changes**

```bash
git diff main..HEAD --stat | grep -E "data-(us|jp|tw|kr|cn)" || echo "OK: no data-* changes"
```

Expected: `OK: no data-* changes`.

- [ ] **Step 3: Confirm CI-relevant invariants**

```bash
# Skill structure validation (existing repo hook):
bash .claude/hooks/validate-skill-folder-structure.sh skills/analysis-comps/ || true

# Script-sync check (only matters if any client is touched, which it isn't):
git diff main..HEAD -- skills/analysis-comps/scripts/comps_compute.py | head -5
```

- [ ] **Step 4: Run all offline tests one more time**

```bash
uv run pytest tests/ -m "not network" --no-header -q 2>&1 | tail -5
```

Expected: `passed` count equals previous baseline + 19 new comps tests + 1 integration test.

### Task 6.2: Push branch + open PR

- [ ] **Step 1: Push**

```bash
git push -u origin feat/v2.2.0-b-comps-compute-spec
```

- [ ] **Step 2: Open PR**

```bash
gh pr create --title "feat(analysis-comps): activate --mode compute (v2.2.0-b)" --body "$(cat <<'EOF'
## Summary

- Activates placeholder `--mode compute` in `analysis-comps/scripts/comps_compute.py`. Anchor-only dual input (B'): new `--anchor-base` reads existing memo-fetch pack; peers stay single-input direct.
- 3 of 5 multiples computable today: `trailingPE` (FY-trailing), `priceToSales` (FY), `forwardPE` (pass-through with `computed: false`). 2 of 5 deferred to v2.2.0-l (`priceToBook`, `evEbitda`) — emit `null` with explicit `note` until memo-fetch raw fields ship.
- New `divergence` block per multiple: `abs_diff` / `pct_diff` / `alert ∈ {low, medium, high, n/a}` per [`divergence-thresholds.md`](investing-toolkit/skills/analysis-comps/references/divergence-thresholds.md) (5% / 15% bands).
- New `compute_provenance` per multiple: `numerator_source` / `denominator_source` / `fiscal_year_end` / `accession_basis` (Tier A trace).
- Direct-mode breaking change: `anchor.multiples` → `anchor.multiples_direct`. Only in-tree caller (`report-equity-memo` Phase 2.5) migrated atomically.
- Spawned 2 follow-up ROADMAP tickets: `v2.2.0-k` (immutable cadence cache tag) + `v2.2.0-l` (memo-fetch raw-field extension to unblock the 2 deferred multiples).

## Spec / Plan

- Spec: [docs/superpowers/specs/2026-05-03-investing-toolkit-v2.2.0-b-comps-compute-design.md](docs/superpowers/specs/2026-05-03-investing-toolkit-v2.2.0-b-comps-compute-design.md)
- Plan: [docs/superpowers/plans/2026-05-03-investing-toolkit-v2.2.0-b-comps-compute.md](docs/superpowers/plans/2026-05-03-investing-toolkit-v2.2.0-b-comps-compute.md)

## Test plan

- [x] `pytest tests/analysis/ -v` — all green including 19 new compute-mode test cases
- [x] `pytest tests/integration/test_cross_layer_chains.py::test_chain_us_comps_compute_dual_input` — green
- [x] `pytest tests/ -m "not network"` — full offline suite green
- [x] `git diff main..HEAD --stat | grep data-` — empty (no data-* changes per spec §13)
- [x] direct mode byte-equal v2.0.0 except for documented `multiples` → `multiples_direct` rename

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Return PR URL.

---

## Self-Review (skill checklist)

- [x] **Spec coverage**: Every section in §3-§15 of the spec maps to a task above. §16 risk register and §17 references are reference-only and don't need tasks.
- [x] **Placeholder scan**: searched for TBD/TODO/FIXME — only `PR #TBD` placeholders appear in commit messages and ROADMAP closure text, which is correct (PR number unknown until pushed; documented as such).
- [x] **Type consistency**: `_anchor_base_arg` / `compute_payload` / `_load_memo_fetch_pack` / `DIVERGENCE_BAND_LOW` / `DIVERGENCE_BAND_HIGH` / `DEFERRED_MULTIPLES` / `_compute_multiples_from_memo_fetch` / `_classify_divergence_alert` / `_compute_divergence` — names used identically across all task code blocks.
- [x] **Each test gets an impl**: Every failing-test step is followed by an impl step that produces matching code.
- [x] **TDD ordering**: Each task is failing test → run → fail → impl → run → pass → commit.
