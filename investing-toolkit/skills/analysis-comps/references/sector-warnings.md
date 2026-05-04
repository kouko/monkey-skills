# Sector-relative valuation warnings — by schema_id

Loaded by `comps_compute.py --sector-benchmark` and pasted into
`anchor.etf_benchmark.warnings: [...]`. One row per known schema_id.
Keyed by schema_id (NOT yfinance sector name) to align with
v2.2.0-c routing source-of-truth (`sector-routing.yaml`).

Drift rule: when `sector_classifier.KNOWN_SCHEMA_IDS` gains a new
schema_id, also add a row here. Reviewers verify schema_id ↔ row parity.

## Warnings

| schema_id | warning_text |
|---|---|
| `default` | Default 5-multiple set; appropriate for cash-generating businesses with positive earnings. Verify operating-margin / FCF_yield indicators are non-negative; if not, a sector-specific schema may be more appropriate. |
| `bank` | Bank P/E and P/B work; EV/EBITDA is undefined (no operating-cash-flow concept of cash earnings). ROE is the primary profitability lens. Tier 1 capital + credit quality (deferred — supplemental disclosure not in standard XBRL) drive equity multiples in conjunction. |
| `insurance` | Combined ratio, reserves, premium-growth are the primary disclosures (deferred — supplemental disclosure not in standard XBRL). P/B is the most reliable price multiple in this output. |
| `asset-manager` | P/AUM is the canonical valuation metric (deferred — AUM not standard XBRL). P/E and P/B available but interpretive given AUM-driven earnings. |
| `reit` | P/FFO + EV/EBITDAre are REIT-canonical valuation; net-income-based P/E is misleading (depreciation distortion). AFFO requires gain-on-sale + straight-line rent adjustments — not in standard XBRL — so P/FFO only. |
| `tech-saas` | Rule-of-40 (revenue growth + operating margin) is the primary growth/quality lens. Pre-profit SaaS issuers may have negative trailingPE — interpret with operating-margin floor. |
| `tech-semis` | Cyclical industry; trailingPE near cycle troughs may be inflated and near peaks deflated. Inventory + book-to-bill ratios are sector-supplemental (deferred). |
| `energy` | P/E and EV/EBITDA on energy issuers are commodity-cycle distorted; production-volume + EV/EBITDAX (deferred — exploration_expense not standard XBRL) are more reliable in extreme cycle phases. |
| `utilities` | Dividend yield is the canonical valuation metric for utilities (deferred — dividend per share not standard XBRL); P/E and EV/EBITDA available but interpretive given regulated-rate-base economics. |
