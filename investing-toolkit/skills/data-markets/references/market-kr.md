# Market reference — KR

Distilled from the pre-migration `data-kr` skill's `SKILL.md`. All clients
below are byte-identical migrations (cache-layer only) — see
`references/migration-grounding.md` for the external-surface grounding.

## Sources + authority tiers

| Source | Tier | Client | Coverage |
|---|---|---|---|
| BOK ECOS-KEYSTAT (via FinanceDataReader) | **Tier A primary** | `fdr_client.py` | Macro — 54 indicators across 13 groups |
| FRED (DEXKOUS only) | Tier A | `fred_client.py` | KRW/USD daily fallback (ECOS-KEYSTAT has no clean KRW/USD series) |
| yfinance `.KS`/`.KQ` | Tier 2 | `yfinance_client.py` | Equity price/info/financials |
| DART (전자공시시스템) | — | not wired | **Deferred** — no primary-source equity client for KR in this skill |

**Honest gap**: canonical KR equity financials are Tier 2 (yfinance)
only — DART primary-source extraction is deferred, matching the
pre-migration skill's own stated limitation, not a new regression.
`_provenance.primary_source_status` is `"deferred"` on every `memo-fetch`
payload so downstream layers can reflect it.

## API keys + rate limits

No API key required for anything in this market. A free BOK ECOS API key
exists (https://ecos.bok.or.kr/api/#/AuthKeyApply) but is not wired in —
noted as a deferred candidate for direct integration, not a functioning
upgrade path today.

## Caveats

- **BOK ECOS access is via an undocumented internal endpoint** that
  FinanceDataReader reverse-engineers — endpoint risk is real; a BOK-side
  change could break the client with no advance notice.
- PMI (S&P Global) is licensed commercial data and is **not fetched**;
  closest free proxies are the `sentiment` group (K252 consumer
  sentiment, K269 economic sentiment).
- Ticker suffix defaults to `.KS` (KOSPI) for bare 6-digit codes; use
  `.KQ` explicitly for KOSDAQ-listed tickers to avoid a wrong-exchange
  lookup.

## Error dialect

KR surfaces provenance via `_provenance` (mirrors JP's convention):
`primary_source_status` (`"available"` / `"deferred"`),
`primary_source_note`, `tier`, plus pack-specific fields. Ticker
normalization issues (non-suffixed, non-6-digit tokens) surface under
`_provenance.ticker_normalization_warnings` rather than being refused —
the malformed token passes through so the consumer can inspect the
resulting yfinance failure with full context.
