# Migration grounding — external surfaces

Every client script under `skills/data-markets/scripts/` is a
**cache-layer-only migration** of the corresponding `skills/data-{us,jp,tw,kr,cn}/scripts/`
original: fetch logic, endpoints, SDK calls, and CLI invocations are
byte-identical to code that was live-verified in production use. Only the
cache read/write path changed (local per-skill cache helpers → shared
`cache_util`). Migration commits:

| Market | Commit |
|---|---|
| US | `792936ef` |
| JP | `3ef8cbfe` |
| TW | `92ed1fb9` |
| KR | `23d3d4a2` |
| CN | `c8b38f01` |

No new external surface, endpoint, or SDK call was introduced by any
migration — grounding basis for every row below is **"byte-identical
migration; live-verified pre-migration"** unless noted otherwise.

## Surface inventory

| Surface | Category | Market(s) | Source-of-truth doc | Auth |
|---|---|---|---|---|
| yfinance | SDK (unofficial) | US, JP, TW, KR, CN | `skills/data-us/SKILL.md` §Sources (L15-21) | keyless |
| SEC EDGAR (`data.sec.gov`) | HTTP | US | `skills/data-us/SKILL.md` §Sources (L15-21) | keyless |
| FRED (CSV + keyless `fredgraph` fallback) | HTTP | US, KR (DEXKOUS fallback), CN (DEXCHUS, TRESEGCNM052N) | `skills/data-us/SKILL.md` §Sources (L15-21); `skills/data-kr/SKILL.md` §Tier status (L20-26); `skills/data-cn/SKILL.md` L18 | keyless |
| EDINET (金融庁) | HTTP, key-gated | JP | `skills/data-jp/SKILL.md` §EDINET tier routing (L42-57) | keyed (`EDINET_API_KEY`; else yfinance Tier-2 fallback) |
| TDnet via Yanoshin (`webapi.yanoshin.jp`) | HTTP | JP | `skills/data-jp/SKILL.md` L150-157; `scripts/tdnet_client.py` module docstring (L9-19) | keyless |
| BOJ / e-Stat / ECB | HTTP | JP | `skills/data-jp/SKILL.md` §Regime pack indicator list (L126-129) | keyless |
| FinanceDataReader SDK + BOK ECOS-KEYSTAT endpoint | SDK + HTTP | KR | `skills/data-kr/SKILL.md` §Tier status (L24) + §Underlying clients (L189-196) | keyless (free ECOS API key improves reliability, not required — see Limitations §221-223) |
| TWSE/TPEx OpenAPI | HTTP, `verify=False` | TW | `skills/data-tw/SKILL.md` §Bundled clients (L25-38); `scripts/twse_openapi_client.py` L54, L120 | keyless |
| MOPS | HTTP, `verify=False` | TW | `skills/data-tw/SKILL.md` §Bundled clients (L25-38); `scripts/mops_client.py` L54 (comment), L143 (call site) | keyless |
| FinMind | HTTP | TW | `skills/data-tw/SKILL.md` §Bundled clients (L31), §Tier policy (L67-75) — Tier-2 by-design gap, not an auto-fallback | keyless |
| CBC / DGBAS / NDC / stat.gov.tw | HTTP, `verify=False` | TW | `skills/data-tw/SKILL.md` §Bundled clients (L33-36); `scripts/{cbc,dgbas,ndc,statgov}_client.py` (SSL cert workaround documented at each file's top) | keyless |
| akshare SDK (PBOC chinamoney + SHIBOR + Caixin via eastmoney mirror) | SDK | CN | `skills/data-cn/SKILL.md` unlabeled source table after the intro paragraph (L17, no "Sources" heading exists in this file) + §Indicator coverage (L128-131) | keyless |
| NBS new-SPA API (`data.stats.gov.cn`) | HTTP | CN | `skills/data-cn/SKILL.md` unlabeled source table after the intro paragraph (L16, no "Sources" heading exists in this file) | keyless |
| `uv run` CLI invocation pattern | CLI | all 5 | `scripts/pack_kr.py` `_run()` (L171-173) — identical pattern in every `pack_*.py` | n/a |

## Notes

- `verify=False` (SSL) on TWSE/MOPS/CBC/DGBAS/NDC endpoints is a pre-existing
  TW-specific workaround for a documented cert-chain issue (Subject Key
  Identifier missing on macOS) — inherited byte-identical, not introduced by
  this migration.
- JP's BOJ/e-Stat/ECB endpoint URLs are documented at finer grain in each
  client's module docstring (`boj_client.py`, `estat_client.py`,
  `ecb_client.py`) rather than in a dedicated SKILL.md section — the old
  SKILL.md's indicator list (L126-129) plus those docstrings together are
  the source of truth.
- No `docs/` ADR documents individual external-surface endpoints; the old
  per-market SKILL.md files are the sole source of truth cited above.
