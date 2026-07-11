# Market reference — JP

Distilled from the pre-migration `skills/data-jp/SKILL.md`. All clients
below are byte-identical migrations (cache-layer only) — see
`references/migration-grounding.md` for the external-surface grounding.

## Sources + authority tiers

| Source | Tier | Client | Coverage |
|---|---|---|---|
| yfinance `.T` | Tier 2 | `yfinance_client.py` | Price/info/history; always-on baseline |
| EDINET (金融庁) | **Tier A when keyed** / Tier 2 fallback | `edinet_client.py` | Filing summaries + material-event filings (180/220/350) |
| TDnet via Yanoshin (third-party mirror, `webapi.yanoshin.jp`) | Tier 2 | `tdnet_client.py` | Disclosure index |
| BOJ Time-Series | Tier A | `boj_client.py` | Call rate O/N, Tankan price outlook |
| e-Stat (統計ダッシュボード) | Tier A | `estat_client.py` | CPI/core-CPI/IP/unemployment/JGB10Y presets |
| ECB Data Portal | Tier A | `ecb_client.py` | JP real 10Y yield ex-post |

**Honest gap**: canonical JP equity financials are Tier 2 (yfinance)
unless `EDINET_API_KEY` is set. Primary-source XBRL extraction from
EDINET filings is deferred — this mirrors the pre-migration skill's own
Tier 2 fallback path, not a new limitation introduced by the merge.

## API keys + rate limits

| Env var | Required? | Effect |
|---|---|---|
| `EDINET_API_KEY` | optional | Set → Tier-A filing-summary + material-event filings (180/220/350) for `memo-fetch`; unset → yfinance annual + quarterly financials, tagged `tier_2` with an `_provenance.upgrade_hint` pointing to free EDINET registration. |

`snapshot`, `comps-multiples`, `screener-batch`, and `regime-pack` never
need the key — they only touch always-public sources.

## Caveats

- TDnet access is via Yanoshin, a **third-party mirror**, not the
  official TDnet API — treat as best-effort, not primary-source.
- BOJ/e-Stat/ECB endpoint URLs are documented at finer grain inside each
  client's own module docstring rather than in this file.
- JP tickers are bare 4-digit 証券コード (e.g. `7203`); `pack.py`
  auto-appends `.T` for yfinance and strips suffixes for EDINET/TDnet.

## Error dialect

JP surfaces failure via `_provenance` — every payload carries a
`_provenance.tier` (`tier_1` / `tier_a` / `tier_2`) and `tier_label`;
the Tier 2 fallback variant additionally carries
`_provenance.upgrade_hint`. Section-level failures still nest an
`error`/`_error` marker one level below the top-level section key
(same one-level walk `pack.py`'s classifier applies to every market).
