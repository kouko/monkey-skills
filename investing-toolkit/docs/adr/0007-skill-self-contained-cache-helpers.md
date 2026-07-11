# ADR-0007: Skill-Self-Contained Cache Helpers (no central `_cache.py`)

- **Status**: Accepted — §"What CI enforces" (block-level guard design)
  superseded by [ADR-0009](0009-data-markets-consolidation-and-cache-util.md)
  (2026-07-11); cadence-aware TTL policy retained, see that ADR's "What is
  retained from ADR-0007" section
- **Date**: 2026-05-03
- **Version target**: investing-toolkit v2.2.0 (`v2.2.0-j` cadence-aware adaptive TTL)
- **Spec**: `investing-toolkit/docs/cache-policy.md`

## Context

Through v2.0.0–v2.1.x each of the 14 data clients (`dgbas`, `ndc`, `cbc`, `statgov`, `fdr`, `fred`, `akshare`, `boj`, `ecb`, `estat`, `nbs`, `yfinance`, `finmind`, `tdnet`) carried its own copy-pasted cache logic:

- A `CACHE_TTL_SECONDS` constant (1h / 6h / 24h, no shared rationale)
- A `load_cache(path)` function — uses `path.stat().st_mtime` to compute age
- A `save_cache(path, data)` function — bare `path.write_text(json.dumps(...))`
- A `get_cache_path(...)` function (signature varies per client)

PR #222 (2026-05-03) added byte-equality CI guards for the 5 TW/KR client files via `check-script-sync.yml`, but **the cache-helper code blocks themselves are not enforced byte-equal across clients**. `ensure_ascii=False` and other small edits already drifted between `dgbas_client.py` and `fred_client.py`.

Two design problems became blocking when planning v2.2.0-j:

1. **TTL is a flat constant, not data-aware.** A monthly CPI series and a daily yield curve both default to 24h. The CPI cache misses 30× per month for no reason; the yield curve cache might serve stale data overnight if release timing shifts.
2. **`mtime`-based expiry is fragile.** `cp` / `rsync` / Docker volume mount / `tar -xzf` (without `-p`) all reset mtime to "now" while data inside is old. The JSON envelope already contains `fetched_at` — but `load_cache` ignores it.

The natural engineering instinct is to factor out a central `_cache.py` module with `Cache.get(key)` / `Cache.put(key, data, *, cadence, ...)`. Imported via `sys.path.insert + from _cache import Cache`. Mirrored across all 5 skill `scripts/` directories via `sync-clients.sh`.

But this conflicts with two prior commitments:

- **Anthropic skill convention**: each skill is self-contained, `SKILL.md` + flat single-level subdirectories, no nested directories, no cross-skill imports. (Hook `validate-skill-folder-structure.sh` enforces flatness; CLAUDE.md formalises "Reference files one level deep".)
- **investing-toolkit PEP 723 self-contained scripts**: each `*_client.py` is a single file invokable as `uv run <client>.py` with all deps declared in its `# /// script` block. A reader copies one file and it just works.

A central `_cache.py` would technically still satisfy the flat-directory rule (the file lives directly inside `scripts/`, no nesting), but it would:

- Break PEP 723 self-containment — `dgbas_client.py` no longer "just works" without `_cache.py` in the same directory
- Couple skills via shared code (changes to `_cache.py` ripple across 5 skills automatically)
- Add `sys.path` manipulation to every client (boilerplate the toolkit has avoided)

We considered three alternatives during the v2.2.0-j design discussion (2026-05-03 session):

| Option | DRY | Self-contained | Skill independence | Verdict |
|---|---|---|---|---|
| **A.** Central `_cache.py` + sync across skill copies | ✅ | ❌ broken | ❌ broken | rejected |
| **B.** Pure copy-paste, no policy doc, no sync guard | ❌ | ✅ | ✅ | drift-prone (current state, broken) |
| **C.** Copy-paste of a single canonical helper *block* + central policy doc + block-level CI sync guard | ⚠️ partial | ✅ | ✅ | **accepted** |
| **D.** Publish `investing-toolkit-cache` as its own PyPI package | ✅ | ✅ | ✅ | overkill for solo dev |

## Decision

Adopt **Option C**: every client embeds an identical, byte-checked block of cache helpers. The policy itself (cadence taxonomy, TTL bands, schema version) lives in `investing-toolkit/docs/cache-policy.md` as the single source of truth. The block is delimited by sentinel comments and CI enforces byte-equality across all client files.

### Block delimiters

Each client carries this exact block (no per-client variation, including indentation and comments):

```python
# === BEGIN cache helpers (synced — DO NOT EDIT INDIVIDUALLY) ===
# Cadence taxonomy + TTL bands + schema documented in
# investing-toolkit/docs/cache-policy.md (v1.0).
# Changes must be applied to ALL 14 client files in lockstep —
# block-level sync is enforced by .github/workflows/check-script-sync.yml
# Group 10. Run `bash investing-toolkit/scripts/sync-clients.sh` after editing.

CACHE_SCHEMA_VERSION = "2.0"

def _compute_ttl(cadence: str, staleness_days: int | None) -> int:
    """Return TTL seconds. See cache-policy.md §"TTL bands"."""
    ...

def load_cache(path: Path, cadence: str) -> dict | None:
    """Read envelope; return data dict if fresh per current policy.

    Uses `_cache_meta.fetched_at` from the envelope (NOT filesystem
    mtime) — robust against cp/rsync/tar that reset mtime.
    Recomputes TTL on every load so policy changes apply to old cache.
    """
    ...

def save_cache(path: Path, key: str, data: dict, cadence: str,
               reference_period: str | None,
               provenance: dict | None = None) -> None:
    """Write standardized envelope atomically (tmp + rename)."""
    ...

# === END cache helpers ===
```

### Per-preset cadence

Each client's `PRESETS` dict gains a `cadence` field per preset:

```python
PRESETS = {
    "cpi":      {..., "cadence": "monthly"},
    "cpi-yoy":  {..., "cadence": "monthly"},
    "cpi-sa-yoy": {..., "cadence": "monthly"},
    # etc.
}
```

`fetch_preset()` reads `cadence = config.get("cadence", "monthly")` and passes it to `load_cache` / `save_cache`. Default is `"monthly"` (matches current 24h-ish behaviour for unknown cases).

### Cache file envelope (schema v2.0)

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
    "...": "..."
  }
}
```

`expires_at_hint` is informational only (debug aid when reading cache files by hand). The actual freshness check happens at load time using `compute_ttl(meta.cadence, meta.staleness_days_at_fetch)` — so policy updates take effect immediately on next load, without invalidating existing cache files.

### What CI enforces

> **2026-05-03 amendment (per ADR-0008)**: MCP server removed; the
> `investing-toolkit/scripts/` canonical-vs-skill-copy duality is gone.
> File-level MD5 now enforces only the 2 true cross-skill groups
> (yfinance × 5, fred × 2). Block-level MD5 spans 14 single-skill
> client files instead of the original 28 (skill + MCP) — half the cost.

> **2026-07-11 amendment (per ADR-0009)**: the 5 data skills (and their
> 23 client files) merged into one `data-markets` skill with a single
> `cache_util.py`. The block-level MD5 guard described below was never
> actually built (0 of the planned Phase 2/3/4 rollout landed beyond the
> 1-client `dgbas_client.py` PoC) and, post-merge, has nothing left to
> enforce — there is exactly one copy of the cache-helper code, not N
> copies to keep byte-equal. This section is superseded; see ADR-0009
> "What is retained from ADR-0007" for what still stands (the
> cadence-aware TTL design, now implemented once in `cache_util.compute_ttl`).

- **File-level MD5** (existing, scoped down by ADR-0008): `data-jp/scripts/yfinance_client.py` etc. must equal `data-us/scripts/yfinance_client.py` byte-for-byte (yfinance × 4 cross-skill copies; fred × 1 cross-skill copy).
- **Block-level MD5** (new, this ADR's Phase 2): the `# === BEGIN cache helpers === … # === END cache helpers ===` region must be byte-identical across all 14 clients. (1 new check group in `check-script-sync.yml`; 14 file scope post-ADR-0008.)

The block-level check uses a regex-extract-then-MD5 approach inside the existing workflow Python; no new tooling.

### Schema migration: no migration

Old cache files (no `_cache_meta` envelope) fail `meta["version"] == "2.0"` check → treated as miss → refetched on next access. The `~/.cache/investing-toolkit/` directory becomes effectively cleared the first time the new code runs. This is acceptable because:

- Cache is reproducible from upstream APIs
- No user-modified data lives in cache
- v2.2.0 is a planned major-feature release; one-time refetch is expected

Users can manually `rm -rf ~/.cache/investing-toolkit` before upgrading if they want a clean slate; otherwise the system self-cleans naturally over the first day.

## Consequences

### Positive

- **Each client remains self-contained** — `uv run dgbas_client.py` works in isolation, no `sys.path` manipulation, no sibling-file dependency. PEP 723 metadata fully describes the script's needs.
- **Anthropic skill convention preserved** — every skill remains a self-contained directory; no cross-skill imports.
- **TTL becomes data-aware** — monthly CPI cached for 7 days when fresh, 4 hours when next release is overdue. Tick data cached briefly; immutable filings cached indefinitely.
- **`mtime` fragility eliminated** — `_cache_meta.fetched_at` is the single source of truth; `cp`/`rsync` no longer reset effective cache age.
- **Policy changes propagate without code edits** — adjust the TTL band table in cache-policy.md + helper block, sync the block across 14 files, every existing cache file picks up the new policy on next load.
- **Drift surfaced immediately by CI** — block-level MD5 check fails the moment any client's helper edits drift from the others.

### Negative

- **DRY is partial** — 14 byte-identical copies of `_compute_ttl + load_cache + save_cache` exist across the skill copies. Roughly 50 lines × 14 = 700 lines of duplicated code, byte-pinned. _(Post-ADR-0008 figure; previously 28 file copies including the MCP canonical.)_
- **Editing the helper requires touching 14 files** — `sync-clients.sh` automates the propagation but the discipline is on the developer to remember to run it (CI catches failures post-hoc).
- **Block delimiters become a load-bearing convention** — a careless edit that breaks the `# === BEGIN cache helpers ===` marker silently disables the CI sync check for that client. Mitigation: the helper functions inside the block are also imported / called by the rest of `<client>.py`, so a broken delimiter usually breaks the file too.
- **TTL policy is "embed + sync" not "import + share"** — feels less elegant than the central-module instinct. ADR exists primarily to justify why we deliberately chose inelegance.

### Neutral

- **Cache files become slightly larger** (~200 bytes of `_cache_meta` envelope per file). Negligible at typical cache size (117 MB current, ~22k files).
- **Old cache effectively discarded on upgrade** — by design, no migration cost. Users with very large cache directories should `rm -rf ~/.cache/investing-toolkit` before the upgrade if disk is tight.

## Alternatives considered (recap)

- **Option A — Central `_cache.py` mirrored across skill `scripts/` dirs.** Cleanest DRY, but breaks PEP 723 self-containment (each `*_client.py` would need `sys.path.insert + from _cache import Cache` boilerplate, and the file no longer "just works" when copied elsewhere). Rejected because investing-toolkit explicitly committed to single-file PEP 723 scripts in v2.0.0.
- **Option B — Status quo (copy-paste, no policy doc, no sync guard).** Already broken: `ensure_ascii=False` drift between `dgbas_client.py` and `fred_client.py` discovered during this design session. Rejected.
- **Option D — Publish `investing-toolkit-cache` to PyPI.** Solves DRY perfectly while keeping each script self-contained (just declare the package as a PEP 723 dep). Rejected as overkill for a solo-developer toolkit; PyPI publishing introduces semver discipline and CI publish workflows that don't currently exist. _Post-ADR-0008 update_: With MCP server removed, PyPI is now the most likely future path for cross-LLM exposure should it ever be needed.

## Implementation phases

1. **Phase 0** (this ADR + `cache-policy.md` + ROADMAP §v2.2.0-j entry) — design lock-in. ✅ Landed in PR #224.
2. **Phase 1** — PoC: `dgbas_client.py` refactored end-to-end. Validates the block-delimiter pattern, the schema, the CI guard. ✅ Landed in PR #224 (also included MCP copy at the time; per ADR-0008 the MCP copy was deleted in the next PR).
3. **Phase 2** — extend `check-script-sync.yml` with block-level MD5 group (added 2026-05-03 Q4). Spans 14 single-skill client files post-ADR-0008 (was originally planned for 28 = 14 skill + 14 MCP copies; halved by MCP removal).
4. **Phase 3** — bulk migration: remaining 13 clients adopt the synced block + per-preset cadence. Halved effort post-ADR-0008 (13 file edits instead of 26). Likely staged across 2-3 PRs by domain.
5. **Phase 4** — close out: remove all `CACHE_TTL_SECONDS = ...` constants; update `industry-indicator-cadence.md` cross-reference; deprecate any leftover top-level `fetched_at` field on data dicts (canonical lives in `_cache_meta`).

## References

- ADR-0001: Three-Layer Skill Architecture — establishes PEP 723 self-contained scripts as a v2.0.0 commitment.
- `investing-toolkit/docs/cache-policy.md` — the cadence taxonomy + TTL band table referenced by the synced helper block.
- `investing-toolkit/docs/industry-indicator-cadence.md` — pre-existing publication-lag taxonomy; `cache-policy.md` borrows the cadence labels for consistency.
- PR #222 — first sync-clients.sh extension to TW/KR clients (file-level MD5 model that block-level extends).
- 2026-05-03 design session — rejected Option A (central `_cache.py`) explicitly.
