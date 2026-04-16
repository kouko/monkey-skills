---
name: stock-screener
description: Multi-criteria stock screener (ships in v1.2.0). Screen US or Taiwan stocks by valuation, momentum, and quality criteria.
---

# stock-screener

This skill screens US or Taiwan stocks against user-defined criteria — valuation
multiples (PE, PB, EV/EBITDA), momentum signals (price vs. 52-week high, relative
strength), and quality factors (ROE, debt/equity, earnings consistency). It ships in
**investing-toolkit v1.2.0**.

See `../../ROADMAP.md` for the v1.2.0 timeline and planned screener implementation.

---

## Status: Not Yet Available

stock-screener is planned for v1.2.0 and is not available in the current release.

---

## Interim Option

For individual stock lookups, use the `us-stock-snapshot` skill. It fetches price
history and company info for a single ticker via yfinance. Screening across a universe
of tickers is not supported until v1.2.0.
