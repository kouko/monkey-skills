# Market reference — TW

Distilled from the pre-migration `skills/data-tw/SKILL.md`. All clients
below are byte-identical migrations (cache-layer only) — see
`references/migration-grounding.md` for the external-surface grounding.

## Sources + authority tiers (8 clients)

| Client | Tier | Coverage |
|---|---|---|
| `mops_client.py` | **A primary** | 公司基本資料、財報 BS/IS/CF、月營收、董監持股、內部人申報、股利、除權息、重大訊息 (16 actions) |
| `twse_openapi_client.py` | **A primary** | TWSE/TPEx OpenAPI: 日行情、PE/PB/殖利率、融資融券、三大法人 snapshot、產業 EPS、除權息日曆、`/rwd/` 歷史 OHLCV (sii only) |
| `finmind_client.py` | Tier 2 **by-design gap** | Fills a real Tier-A gap: T86 daily per-stock 三大法人, `.TWO` OHLCV, split-adjusted price, 融資融券時序. **Not** an auto-fallback on Tier-A error — Tier A failures surface as `_partial: true` + per-source `_error`; escalation is the consumer's call. |
| `yfinance_client.py` | Tier 2 cross-source | Price/info/multiples/batch (`.TW`/`.TWO` auto-dispatch) |
| `cbc_client.py` | **A primary** | 央行：重貼現率、TWD/USD、M2、準備貨幣 |
| `dgbas_client.py` | **A primary** | 主計總處：CPI/核心CPI/PPI/進出口物價 |
| `ndc_client.py` | **A primary** | 國發會：景氣對策信號 五色燈號、領先/同時指標、台灣 PMI/NMI |
| `statgov_client.py` | **A primary** | stat.gov.tw 隱藏 chart data：GDP/IPI/失業率/出口/外匯/TAIEX 等 17 presets |

Canonical financials (income statement / balance sheet / cash flow) ARE
Tier-A here via MOPS — TW is one of the two markets (with US) that has
real primary-source financials wired, not a Tier-2 placeholder.

## API keys + rate limits

| Env var | Required? | Effect |
|---|---|---|
| `FINMIND_API_TOKEN` | optional | Anonymous access: 300 req/hr. With a free token: 600 req/hr. A 429 during anonymous use surfaces as `"HTTP 429 rate limit"`. |

MOPS/TWSE/CBC/DGBAS/NDC/statgov are keyless.

## Caveats

**SSL — state plainly**: 6 of the 8 clients (`mops_client.py`,
`twse_openapi_client.py`, `cbc_client.py`, `dgbas_client.py`,
`ndc_client.py`, `statgov_client.py`) call their endpoint with
`verify=False` — a pre-existing workaround for a documented cert-chain
issue (Subject Key Identifier missing on macOS), inherited byte-identical
from the pre-migration clients, not introduced by this migration.
`mops_client.py`'s actual `verify=False` call is at **L143** (the L54
line in the same file is a comment, not the call site). `finmind_client.py`
and `yfinance_client.py` are the 2 of 8 that do NOT disable verification.

- `stat.gov.tw` extraction reads a hidden HTML field
  (`#ContentPlaceHolder1_hidChartData`) — not a documented API; a page
  redesign could break it silently.
- MOPS 重大訊息 (`realtime-announcements`) returns market-wide results;
  per-ticker filtering is best-effort via `--market sii|otc`.
- `.TWO` (TPEx) price history has no `/rwd/` endpoint — falls through to
  FinMind (Tier 2), tagged `_tier: "2"`, not `"2-gap"` (TWSE `/rwd/`
  covers the same need at Tier A for `.TW`/sii listings).

## Error dialect

TW tags every wrapped output with `_tier` (`"A"` / `"2"` / `"2-gap"`),
`_source`, and `_action`; a failed fetch carries `_error` +`_stderr`
instead of `data`. **No automatic Tier-A → Tier-2 fallback** — a Tier-A
error flips the whole-pack `_partial: true` and leaves the error in
place for the consumer to decide whether to escalate.
