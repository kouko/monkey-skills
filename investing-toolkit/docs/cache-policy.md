# Cache Policy — investing-toolkit Adaptive TTL

**Spec version**: 1.0 (introduced 2026-05-03 as part of v2.2.0-j)
**Authority**: This document is the single source of truth for cache TTL decisions across the 14 data clients.
**Companion**: [ADR-0007 — Skill-Self-Contained Cache Helpers](adr/0007-skill-self-contained-cache-helpers.md) (the *why*).

## Purpose

Replaces the v2.0.0–v2.1.x pattern of per-client `CACHE_TTL_SECONDS` constants (1h / 6h / 24h, no rationale) with a **cadence-aware adaptive TTL**: every preset declares its data-publication frequency, and the cache helper computes TTL based on cadence × observed staleness.

Two failure modes from the old model that this policy fixes:

1. **Wasted fetches on slow-publication data** — monthly CPI cached for 24h means 30 cache misses per release cycle, each hitting upstream API needlessly.
2. **Stale cache served via mtime exploitation** — `cp` / `rsync` / Docker volume mount reset filesystem mtime to "now" while data inside is old. New policy reads `_cache_meta.fetched_at` from the JSON envelope; mtime is no longer load-bearing.

## Cadence taxonomy

Each preset declares one of these cadence labels in its `PRESETS` dict entry:

| Cadence | Used for | Examples |
|---|---|---|
| `tick` | Real-time / intraday quotes during market hours | `yfinance` price quotes, TWSE OpenAPI realtime |
| `daily` | Once-per-day published series (T+1 typical) | FRED `T10Y2Y`, ECB FX rates, daily CBC reference |
| `weekly` | Weekly publication cadence | Some ECB monetary aggregates, weekly EIA energy |
| `monthly` | Monthly macro / sector indicators | CPI, PPI, IP, retail sales, monthly revenue, NDC signal |
| `quarterly` | Quarterly published series | GDP final, BOJ Tankan, financial statements |
| `annual` | Yearly published series | Annual reports, demographic stats |
| `event` | Event-driven indices (low-frequency, unpredictable timing) | TDnet adhoc filing index, EDINET filing index |
| `immutable` | Once-published-never-changes records | Filed 10-K / 10-Q (by accession), EDINET 有報書 (by docID) |

**Default cadence** (when a preset omits the field): `monthly`. Closely matches the previous 24h default behavior on macro data without forcing an explicit declaration on every legacy preset.

## TTL bands

The TTL helper reads `cadence` + `staleness_days` (= days between data's reference period and now) and returns a TTL in seconds. The "staleness band" splits the lifecycle into three phases:

- **Fresh** — data was just published; long TTL since no new data is expected
- **Imminent** — next release window is approaching; medium TTL to catch the new release without spamming
- **Overdue** — past the expected next-release date but cache still has the old reference period; short TTL to actively poll

| Cadence | Fresh | Imminent | Overdue |
|---|---|---|---|
| `tick` | 60 s (during market hours) / 1 h (after-hours) | — | — |
| `daily` | 4 h (`staleness_days ≤ 1`) | 1 h (`> 1`) | 30 min (`> 2`) |
| `weekly` | 5 d (`≤ 7`) | 12 h (`> 7`) | 2 h (`> 10`) |
| `monthly` | 7 d (`≤ 30`) | 1 d (`> 30`) | 4 h (`> 45`) |
| `quarterly` | 30 d (`≤ 90`) | 1 d (`> 90`) | 4 h (`> 100`) |
| `annual` | 90 d (`≤ 365`) | 7 d (`> 365`) | 1 d (`> 380`) |
| `event` | 1 h (always — events are by definition unpredictable) | — | — |
| `immutable` | effectively never expires (TTL set to ~100 years) | — | — |

When `staleness_days is None` (first fetch, no `reference_period` known yet) the helper treats the cache as **overdue** — short TTL — so the next attempt actively re-checks rather than coasting on uncertain data.

### Worked example: monthly CPI series

DGBAS CPI publishes around the 5th of each month for the prior month's reference period.

| Date now | Cached `reference_period` | `staleness_days` | Band | TTL |
|---|---|---|---|---|
| 2026-05-08 | `202604` (just published) | 8 | fresh | 7 d |
| 2026-05-25 | `202604` | 25 | fresh | 7 d |
| 2026-06-01 | `202604` | 32 | imminent | 1 d |
| 2026-06-08 (release window) | `202605` (refetched cleanly) | 8 | fresh | 7 d |
| 2026-06-15 | `202604` (release didn't land — DGBAS late) | 46 | overdue | 4 h |

The "imminent" band gives ~7 days of daily polling around the release window; the "overdue" band kicks in if the release is late.

### Worked example: yfinance tick quote

| Time | TTL |
|---|---|
| 2026-05-04 13:35 UTC (NYSE open) | 60 s |
| 2026-05-04 21:00 UTC (NYSE closed) | 1 h |
| 2026-05-05 03:00 UTC (overnight) | 1 h |

Trading-hours awareness uses a simple weekday + UTC-time check per market (US, JP, TW, KR, CN). Holiday calendars are not modelled in v1.0 — listed as a v2.0 enhancement.

## Cache file envelope (schema v2.0)

Every cache file conforms to this shape:

```json
{
  "_cache_meta": {
    "version": "2.0",
    "client": "dgbas",
    "key": "cpi-yoy",
    "cadence": "monthly",
    "fetched_at": "2026-05-03T08:40:24Z",
    "reference_period": "202603",
    "staleness_days_at_fetch": 62,
    "ttl_seconds_at_fetch": 604800,
    "expires_at_hint": "2026-05-10T08:40:24Z"
  },
  "_provenance": { ... },
  "data": {
    "preset": "cpi-yoy",
    "name": "...",
    "observations": [...],
    "latest": {...},
    ...
  }
}
```

Field semantics:

- `version` — schema version. Helper rejects anything other than `"2.0"` as cache miss.
- `fetched_at` — UTC ISO timestamp of when this cache file was written. **Authoritative for TTL**; never substitute `path.stat().st_mtime`.
- `reference_period` — the latest data point covered by this cache. Format is preset-defined (`"202603"` for monthly, `"2026Q1"` for quarterly, `"2026-05-03"` for daily). Used to compute `staleness_days_at_fetch`.
- `staleness_days_at_fetch` — days between `reference_period` and `fetched_at`, as observed at write time. Stored for the loader's TTL re-computation.
- `ttl_seconds_at_fetch` — TTL the policy returned when this file was written. **Informational only**; the loader recomputes TTL from current policy on every read so policy updates take effect immediately.
- `expires_at_hint` — `fetched_at + ttl_seconds_at_fetch`, ISO format. **Debug aid only** — `cat $cache_file | jq ._cache_meta.expires_at_hint` is human-readable. Not consulted by the loader.

## Loader semantics

```python
def load_cache(path: Path, cadence: str) -> dict | None:
    if not path.exists():
        return None
    try:
        envelope = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None

    meta = envelope.get("_cache_meta") or {}
    if meta.get("version") != "2.0":
        return None  # schema drift → miss

    fetched_at_str = meta.get("fetched_at")
    if not fetched_at_str:
        return None
    fetched_at = parse_iso(fetched_at_str)

    # Recompute TTL from current policy — old envelope's
    # ttl_seconds_at_fetch is NOT consulted.
    staleness = meta.get("staleness_days_at_fetch")
    ttl = _compute_ttl(cadence, staleness)
    age = (now_utc() - fetched_at).total_seconds()

    if age > ttl:
        return None

    out = dict(envelope.get("data", {}))
    out["_cache"] = "hit"
    out["_cache_age_seconds"] = int(age)
    out["_cache_ttl_seconds"] = ttl
    out["_provenance"] = envelope.get("_provenance", {})
    return out
```

Three policy commitments embedded here:

1. **Schema versioning gates compatibility.** Old `v1` cache files (no `_cache_meta`) silently fail and refetch. No migration code path.
2. **TTL is recomputed on every load.** `ttl_seconds_at_fetch` in the envelope is informational. If we later loosen `monthly` from 7d → 14d, all existing cache files immediately benefit on next load. Conversely, if we tighten the policy, all existing cache files immediately re-validate.
3. **`fetched_at` is authoritative.** `path.stat().st_mtime` is never read. This is the single behavioural change that fixes the cp/rsync/Docker-volume mtime hazards.

## Writer semantics

```python
def save_cache(path: Path, key: str, data: dict, cadence: str,
               reference_period: str | None,
               provenance: dict | None = None) -> None:
    now = datetime.now(timezone.utc)
    staleness_days = _compute_staleness_days(reference_period, now)
    ttl = _compute_ttl(cadence, staleness_days)

    envelope = {
        "_cache_meta": {
            "version": "2.0",
            "client": _client_name(path),
            "key": key,
            "cadence": cadence,
            "fetched_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "reference_period": reference_period,
            "staleness_days_at_fetch": staleness_days,
            "ttl_seconds_at_fetch": ttl,
            "expires_at_hint": (now + timedelta(seconds=ttl)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
        "_provenance": provenance or {},
        "data": data,
    }

    # Atomic write: tmp file + rename
    final = path
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=str(final.parent),
        prefix=f".{final.name}.", suffix=".tmp", delete=False,
    ) as f:
        json.dump(envelope, f, ensure_ascii=False, indent=2, default=str)
        tmp = Path(f.name)
    tmp.rename(final)
```

Atomic-rename pattern prevents partial-write corruption: a Ctrl-C during write leaves the old cache intact (or the `.tmp.` file orphan, which loaders ignore by extension).

## Adopting cadence in a client's PRESETS dict

Every preset entry in a client's `PRESETS` dict gains a `cadence` field:

```python
PRESETS: dict[str, dict] = {
    "cpi": {
        "url": f"{BASE}/cpispl.xls",
        "sheet": "CPI",
        "name": "Consumer Price Index INDEX",
        "cadence": "monthly",          # ← required for v2.2.0-j+
    },
    "cpi-yoy": {
        ...,
        "cadence": "monthly",
    },
}
```

`fetch_preset()` reads `cadence = config.get("cadence", "monthly")` and passes it to `load_cache` / `save_cache`. Default `"monthly"` ensures backwards compatibility for any preset that hasn't been migrated yet.

## Trading-hours awareness (`tick` cadence only)

```python
MARKETS = {
    "us": {"open_utc": (13, 30), "close_utc": (20, 0), "weekdays": {0,1,2,3,4}},
    "jp": {"open_utc": (0, 0),   "close_utc": (6, 0),  "weekdays": {0,1,2,3,4}},
    "tw": {"open_utc": (1, 0),   "close_utc": (5, 30), "weekdays": {0,1,2,3,4}},
    "kr": {"open_utc": (0, 0),   "close_utc": (6, 30), "weekdays": {0,1,2,3,4}},
    "cn": {"open_utc": (1, 30),  "close_utc": (7, 0),  "weekdays": {0,1,2,3,4}},
}

def _is_market_open(market: str) -> bool:
    spec = MARKETS.get(market)
    if not spec:
        return False
    now = datetime.now(timezone.utc)
    if now.weekday() not in spec["weekdays"]:
        return False
    h, m = now.hour, now.minute
    open_h, open_m = spec["open_utc"]
    close_h, close_m = spec["close_utc"]
    return (open_h, open_m) <= (h, m) <= (close_h, close_m)
```

Tick presets pass `market` through their PRESETS entry. Holiday calendars (NYSE, TSE 国民の祝日, TWSE 國定假日 etc.) are NOT modelled in v1.0 — false positives during holidays produce one wasteful 60s cache miss, which is acceptable.

## What this policy does NOT cover

- **Cross-process locking.** Concurrent writes from MCP server + skill subprocess to the same cache key rely on filesystem atomic-rename semantics. No `fcntl` / lock files. Race conditions can in theory produce one wasted fetch but never corrupt data.
- **Cache eviction / LRU.** Old cache files accumulate forever (staleness in storage, not freshness in semantics). Manual cleanup if disk fills: `rm -rf ~/.cache/investing-toolkit/<client>/` or whole `~/.cache/investing-toolkit/`.
- **Negative caching.** Failed fetches (5xx, network error) don't write a "miss marker" — next call retries upstream. Acceptable because retries with backoff are the responsibility of the network adapter.
- **Bundled-preset cache.** `pack.py --pack regime-pack` calls many client presets and assembles the result; the assembly is not cached. Each individual preset hits its own cache. The whole pack is recomputed every call.

## v1.0 → v2.0 migration

This is v1.0 of the policy spec. Future revisions tracked here:

- **v2.0 (planned)** — holiday calendar support for tick cadence; per-region holiday data sources.
- **v3.0 (speculative)** — pack-level cache (cache the assembled regime-pack JSON) if profiling shows the assembly is expensive.

When the spec changes major version, helper `CACHE_SCHEMA_VERSION` constant bumps in lockstep, all old cache becomes miss-then-refetch, no migration code needed.

## Cross-references

- [ADR-0007](adr/0007-skill-self-contained-cache-helpers.md) — *why* we embed instead of import
- [ADR-0001](adr/0001-data-analysis-report-layers.md) — three-layer architecture (data layer owns cache)
- [industry-indicator-cadence.md](industry-indicator-cadence.md) — companion doc; covers publication-lag taxonomy from a data-quality perspective. This policy borrows its cadence labels for consistency.
- [check-script-sync.yml](../../.github/workflows/check-script-sync.yml) — CI guard enforcing the helper block byte-equality (Group 10, added in Phase 2 of v2.2.0-j)
