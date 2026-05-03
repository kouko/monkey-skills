# ADR-0007: Skill-Self-Contained Cache Helpers (no central `_cache.py`)

- **Status**: Accepted
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

- **File-level MD5** (existing, PR #222): `data-{country}/scripts/<client>.py` must equal `investing-toolkit/scripts/<client>.py` byte-for-byte. (5 paired groups; 14 single-file clients.)
- **Block-level MD5** (new, this ADR): the `# === BEGIN cache helpers === … # === END cache helpers ===` region must be byte-identical across all 14 clients. (1 new check group in `check-script-sync.yml`.)

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

- **DRY is partial** — 14 byte-identical copies of `_compute_ttl + load_cache + save_cache` exist across the skill copies (and 14 more in `investing-toolkit/scripts/` for MCP). Roughly 50 lines × 28 = 1,400 lines of duplicated code, byte-pinned. Cumulative repository size grows accordingly.
- **Editing the helper requires touching 14 files** — `sync-clients.sh` automates the propagation but the discipline is on the developer to remember to run it (CI catches failures post-hoc).
- **Block delimiters become a load-bearing convention** — a careless edit that breaks the `# === BEGIN cache helpers ===` marker silently disables the CI sync check for that client. Mitigation: the helper functions inside the block are also imported / called by the rest of `<client>.py`, so a broken delimiter usually breaks the file too.
- **TTL policy is "embed + sync" not "import + share"** — feels less elegant than the central-module instinct. ADR exists primarily to justify why we deliberately chose inelegance.

### Neutral

- **Cache files become slightly larger** (~200 bytes of `_cache_meta` envelope per file). Negligible at typical cache size (117 MB current, ~22k files).
- **Old cache effectively discarded on upgrade** — by design, no migration cost. Users with very large cache directories should `rm -rf ~/.cache/investing-toolkit` before the upgrade if disk is tight.

## Alternatives considered (recap)

- **Option A — Central `_cache.py` mirrored across skill `scripts/` dirs.** Cleanest DRY, but breaks PEP 723 self-containment (each `*_client.py` would need `sys.path.insert + from _cache import Cache` boilerplate, and the file no longer "just works" when copied elsewhere). Rejected because investing-toolkit explicitly committed to single-file PEP 723 scripts in v2.0.0.
- **Option B — Status quo (copy-paste, no policy doc, no sync guard).** Already broken: `ensure_ascii=False` drift between `dgbas_client.py` and `fred_client.py` discovered during this design session. Rejected.
- **Option D — Publish `investing-toolkit-cache` to PyPI.** Solves DRY perfectly while keeping each script self-contained (just declare the package as a PEP 723 dep). Rejected as overkill for a solo-developer toolkit; PyPI publishing introduces semver discipline and CI publish workflows that don't currently exist. Reconsider if the toolkit ever serves multiple maintainers or external consumers beyond the MCP server.

## Implementation phases

1. **Phase 0** (this ADR + `cache-policy.md` + ROADMAP §v2.2.0-j entry) — design lock-in
2. **Phase 1** — PoC: `dgbas_client.py` + MCP copy refactored end-to-end. Validates the block-delimiter pattern, the schema, the CI guard. Single PR.
3. **Phase 2** — extend `check-script-sync.yml` Group 10 (block-level MD5). Single PR atop Phase 1.
4. **Phase 3** — bulk migration: remaining 13 clients adopt the synced block + per-preset cadence. Likely staged across 3-4 PRs (TW data clients, KR/CN data clients, JP data clients, US/global data clients).
5. **Phase 4** — close out: remove all `CACHE_TTL_SECONDS = ...` constants; update `industry-indicator-cadence.md` cross-reference; deprecate any leftover top-level `fetched_at` field on data dicts (canonical lives in `_cache_meta`).

## References

- ADR-0001: Three-Layer Skill Architecture — establishes PEP 723 self-contained scripts as a v2.0.0 commitment.
- `investing-toolkit/docs/cache-policy.md` — the cadence taxonomy + TTL band table referenced by the synced helper block.
- `investing-toolkit/docs/industry-indicator-cadence.md` — pre-existing publication-lag taxonomy; `cache-policy.md` borrows the cadence labels for consistency.
- PR #222 — first sync-clients.sh extension to TW/KR clients (file-level MD5 model that block-level extends).
- 2026-05-03 design session — rejected Option A (central `_cache.py`) explicitly.
