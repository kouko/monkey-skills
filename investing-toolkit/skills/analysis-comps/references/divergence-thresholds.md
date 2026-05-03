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
