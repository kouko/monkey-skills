# /invest-macro

**Trigger**: `/invest-macro [--region us|japan|taiwan|korea|china|global|asia-pac|all]`

Diagnose the current macro regime using the Investment Clock + Hedgeye GIP
framework, extended with an LSEG-style real-rate decomposition block for
the US. Routes to country-specific macro skills for data; maps each country
to an IC phase + GIP quadrant; outputs a 5-block dashboard per country:

1. **Macro Summary** — growth / inflation / labor / policy with LSEG-style
   signal labels (Expansion/Contraction, Accommodative/Restrictive)
2. **Yield Curve Snapshot** — 2s10s slope + curve shape
3. **Real Rate Decomposition** — US only (T5YIE/T10YIE/DFII5/DFII10)
4. **IC + GIP Regime Call** — phase + quadrant + divergence note
5. **Asset-Class Tilts** — 3-row equities / fixed income / commodities

## What This Does

Invokes `skills/macro-regime-snapshot/SKILL.md`.

## Examples

```
/invest-macro                                   # Default: US only
/invest-macro --region us
/invest-macro --region japan
/invest-macro --region taiwan
/invest-macro --region korea
/invest-macro --region china
/invest-macro --region global                   # US + JP (backward compat)
/invest-macro --region asia-pac                 # JP + TW + KR + CN
/invest-macro --region all                      # 5 markets side-by-side
/invest-macro --region us,korea                 # Free-form comma list
```

## Notes

- Countries delegate to their own macro skills: `us-macro` (FRED),
  `japan-macro` (BOJ + e-Stat), `taiwan-macro` (stat.gov.tw + CBC + DGBAS +
  NDC), `korea-macro` (BOK ECOS via FinanceDataReader), `china-macro`
  (NBS + PBOC via akshare).
- All data sources are free — no API keys required for core operation.
  `FRED_API_KEY` optional for higher US rate limits.
- Block 3 renamed "Rate Stress Dashboard" in v1.10.0: 3a Real Rate
  Decomposition covers US (unchanged from v1.9.0) + JP (new via
  C+D+E: MoF JGBi auction anchor + ECB monthly ex-post + BOJ Tankan
  期待インフレ). 3b Swap Spread (Treasury-SOFR 3M proxy) is US-only.
  TW has no free linker market; KR KTBi deferred to v1.11.0+ (ECOS
  API key); CN has no linker market. Full MoF 連動係数 + QuantLib
  YTM solver for daily JGBi real yield = v1.11.0 candidate.
- Publication lags: CPI ~2-3 weeks, monthly GDP proxies ~3-6 weeks
  after reference month. Always cite reference dates in Confidence Note.
- For full analysis with investment verdict → use `/invest-memo` or
  `domain-teams:investing-team`.
