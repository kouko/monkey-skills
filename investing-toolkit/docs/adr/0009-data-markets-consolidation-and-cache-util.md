# ADR-0009: data-markets Consolidation + Single `cache_util.py`

- **Status**: Accepted
- **Date**: 2026-07-11
- **Version target**: investing-toolkit v2.3.0
- **Supersedes**: ADR-0007 §"What CI enforces" block-level guard design
  (the byte-equality-synced-block-across-14-files mechanism). ADR-0007's
  **cadence-aware TTL policy is RETAINED** — it is now implemented once in
  `cache_util.compute_ttl`, applied to all clients, instead of copy-pasted
  per client. See "What is retained from ADR-0007" below.
- **Spec**: `docs/loom/specs/2026-07-11-investing-toolkit-data-consolidation.md`
- **Plan**: `docs/loom/plans/2026-07-11-investing-toolkit-data-consolidation.md`

## Context

### The live-reproduced bug

`data-{us,jp,tw,kr,cn}/SKILL.md`'s canonical invocation set
`INVESTING_TOOLKIT_CACHE=${CLAUDE_PLUGIN_DATA}/cache`. `${CLAUDE_PLUGIN_DATA}`
is a hook-context-only variable — inside a Bash tool call it is empty, so
the expression collapsed to the literal string `/cache`. Every client's
cache-path resolution was `os.environ.get("INVESTING_TOOLKIT_CACHE") or
<home fallback>` — a bare `or` that treats any truthy string, including
`"/cache"`, as valid. `/cache` is not writable by a normal user; the
unguarded `CACHE_DIR.mkdir()` call at each client's cache-init site (e.g.
`yfinance_client.py:91`) crashed. **4 of 5** `pack.py` implementations
caught that crash per-section and wrapped it into a `{"error":
"client_failed"}` slot **while still exiting 0** (`data-us/pack.py:198,213,814`
— `return 0` unconditional; data-cn/data-jp implicit exit 0). The sole
partial exception was `data-kr/pack.py:681-682` (`sys.exit(1)` iff the
top-level `_partial` flag was set — still not a general contract). No
downstream consumer checked the error slots (grep: zero hits across
data-us/tw/cn pack consumers). Net effect: a report skill's data step
"succeeded" (exit 0) while every price/fundamental value was `None`,
propagating garbage numbers downstream — the same failure class ADR-0002
already fixed once, resurrected via the cache path instead of the parse
path.

### The drift machine

23 client scripts (`skills/data-{us,jp,tw,kr,cn}/scripts/*_client.py`)
carried ~1,077 LOC of copy-pasted cache boilerplate across 3 naming
dialects (`load_cache`/`save_cache`, underscore-prefixed
`_load_cache`/`_save_cache`, and ad hoc per-client variants). ADR-0007
committed to a synced-block-plus-CI-guard discipline to keep that
boilerplate honest:

- The cadence-aware `_compute_ttl` design landed in exactly **1 of 23**
  clients (`dgbas_client.py` — the PoC named in ADR-0007 Phase 1). Phases
  3 (bulk migration to the other 13 post-ADR-0008 targets) and 4
  (constant cleanup) were never executed.
- The **block-level CI guard** ADR-0007 designed (`# === BEGIN cache
  helpers (synced) ===` sentinel + MD5 check in `check-script-sync.yml`)
  was never built. Only the pre-existing **file-level** sync (yfinance ×5,
  fred ×2 — the two genuine cross-skill duplications) has ever run in CI.
- The sync discipline empirically failed twice: a phantom
  `check-script-sync.yml` block-level-guard claim was left standing in
  4 of 5 `SKILL.md`s (referencing a check that didn't exist), and a
  `LOG_TAG` regression (commit `c97b7852`) drifted silently between
  copies with no guard to catch it.

Both problems trace to the same root: cache handling was duplicated
per-client with no single point of validation or enforcement, and the
enforcement mechanism ADR-0007 designed for that duplication (Option C —
copy-paste-plus-CI-sync) was itself only ever partially built.

## Decision

Two structural changes, landed together as one arc (plan tasks T1–T5d):

### 1. Merge 5 data skills into one `data-markets` skill

`skills/data-{us,jp,tw,kr,cn}/` (5 skills, 1,237 lines / 6,661 words of
`SKILL.md` alone, plus 23 client scripts with 4× duplicate
`yfinance_client.py` and 2× duplicate `fred_client.py`) become one
`skills/data-markets/` skill:

- **18 unique clients** (23 → 18: yfinance ×5 → 1 canonical copy, fred ×2
  → 1 canonical copy; the other 16 clients were already single-market and
  move as-is) + 5 per-market `pack_{market}.py` modules, each exposing a
  uniform `build_pack(pack_name, tickers)` entry point.
- **One `pack.py` facade** (new) dispatching to the right `pack_{market}`
  module via ticker-suffix market auto-detection (`.TW/.TWO`→tw,
  `.KS/.KQ`→kr, `.SS/.SZ/.HK`→cn, `.T`/bare-4-digit→jp, else→us) with an
  explicit `--market` override (required for `regime-pack`, which has no
  ticker dimension).
- **Thin `SKILL.md`** (routing + shared contract + worked examples) +
  `references/market-{us,jp,tw,kr,cn}.md` for per-market detail (sources,
  tiers, key requirements, caveats) — replacing the 5 monolithic
  per-market `SKILL.md`s.
- `scripts/sync-clients.sh` and its MD5-sync discipline are deleted
  outright — a single-copy skill has nothing left to sync (down from 2
  groups post-ADR-0008 to 0).

### 2. Single `cache_util.py`, no sync required

One `skills/data-markets/scripts/cache_util.py`, imported by every client
in the same skill directory (co-located, so this does **not** reopen the
central-`_cache.py`-across-skill-directories question ADR-0007 rejected
in Option A — see "Relationship to ADR-0007 Option A" below):

- **XDG/uv-style precedence ladder**: explicit arg > `INVESTING_TOOLKIT_CACHE`
  (stripped; empty-after-strip treated as unset — closes the exact bug
  above) > `$XDG_CACHE_HOME/investing-toolkit` > `~/.cache/investing-toolkit`.
- **Writability gate**: the resolved candidate is probed with a real
  write; on failure, a loud one-line stderr warning names the rejected
  path and falls back to `tempfile.gettempdir()/investing-toolkit`. The
  function's contract is "always returns a writable directory, or
  raises" — never a silent no-op `mkdir` that later crashes a caller.
- **Cadence-aware TTL** (`compute_ttl(cadence, staleness_days)`),
  generalizing `dgbas_client.py`'s `_compute_ttl` — the one client ADR-0007
  actually finished — to all 18 clients via cache-policy.md's TTL bands
  (immutable / event / weekly / monthly / daily / tick).
  `CACHE_SCHEMA_VERSION = "2.0"` roundtrip helpers (`load_cache`,
  `save_cache`) are fail-open (corrupt/expired ⇒ `None`, never raise) and
  fail-loud on write (`save_cache` prints a stderr warning on write
  failure — never a silent `except: pass`).
- No external cache library adopted (`requests-cache` breaks yfinance's
  `curl_cffi` transport; `diskcache` doesn't address path-resolution
  validation, which is the actual bug) — see plan brief §Alternatives
  Considered item 4 for the full trade-off table and sources.

### 3. Fail-loud `pack.py` exit contract

| Exit | `_status.status` | Replaces |
|---|---|---|
| `0` | `ok` | (unchanged — all sections fetched) |
| `2` | `partial` | some-sections-failed (previously silent-0 in 4/5 packs) |
| `1` | `failed` | all-sections-failed / unexpected exception with traceback |
| `64` | `usage_error` | bad args, bad pack name, mixed-market ticker list, missing `--market` for `regime-pack` (moved off exit `2`, which `data-us/pack.py:784-811` used for arg validation — freed for the partial-failure signal above; grep confirmed zero consumers of the old `return 2 = arg error` behavior) |

A top-level `_status` block (`status`, `market`, `pack`,
`failed_sections[]`, `warnings[]`, plus `message` on `usage_error` or
`traceback` on a crash) is injected into every response. The classifier
that populates `failed_sections` walks one level into each top-level
section (direct `error`/`_error` key, or a dict/list section whose
sub-entries all carry that marker) — see the `LOOM-SIMPLIFY` marker at
`pack.py:264` for the documented ceiling of that walk (two-or-more-levels
nesting still relies on the whole-pack `_partial` flag with no
per-section attribution).

## What is retained from ADR-0007

ADR-0007's central claim — cache TTL should be cadence-aware, not a flat
per-client constant, and `mtime`-based expiry is fragile against
`cp`/`rsync`/`tar` — is **not** overturned by this ADR. It is now
*implemented* rather than *designed-but-9̶5̶%̶-unbuilt*: `cache_util.compute_ttl`
is exactly ADR-0007's cadence-taxonomy idea, and `cache_util.load_cache`
uses the envelope's `_cache_meta.fetched_at` (not filesystem mtime) for
the same reason ADR-0007 specified. What this ADR removes is only the
*enforcement mechanism* ADR-0007 chose for keeping N copies of that logic
in sync (Option C: byte-identical block + block-level CI MD5 guard) —
because after this merge there is exactly **one** copy, so byte-equality
enforcement across copies has nothing left to enforce.

### Relationship to ADR-0007 Option A (rejected central `_cache.py`)

ADR-0007 rejected a central `_cache.py` imported *across skill
directories* (`sys.path.insert` into a sibling skill) because that breaks
the Anthropic skill-self-containment convention and PEP 723
single-file-script self-containment. This ADR does not reopen that
rejection: `cache_util.py` lives *inside* `skills/data-markets/scripts/`
and is imported only by its own skill's sibling client files — the same
flat, single-skill-directory shape the hook `validate-skill-folder-structure.sh`
already enforces. What changed is not the file-organization principle
(same-skill-directory imports were always fine) but the skill-count: 5
skills each needing their own copy → 1 skill needing exactly 1 copy.
ADR-0007's Option A concern (cross-skill coupling) never applied to a
same-skill import in the first place.

## Consequences

### Positive

- **The live-reproduced bug is closed by construction**: `resolve_cache_dir`
  strips + empty-checks the env var and writability-probes the result
  before any client ever calls `mkdir` on it; the whole
  silent-empty-shell failure mode (crash → swallowed → exit 0) requires
  the exit-code contract change too — both landed in the same arc so
  neither fix is load-bearing alone.
- **Net LOC reduction**: data layer ~19,198 → ~14–15k (−4–5k), primarily
  4 duplicate `yfinance_client.py` copies (572 LOC each) + 1 duplicate
  `fred_client.py` (354 LOC) ≈ 2,642 LOC, plus the ~1,077 LOC of
  per-client cache boilerplate collapsing into one ~250-line
  `cache_util.py`, plus `sync-clients.sh` and its two remaining groups.
- **Sync discipline debt eliminated, not just deferred**: there is no
  second copy of `cache_util.py` to drift from a first — the class of bug
  ADR-0007 spent an ADR designing a guard against no longer has an
  attack surface for cache logic (yfinance/fred client *content* sync,
  unrelated to cache handling, is unaffected by this ADR).
- **Cadence-aware TTL reaches all clients**, not just the 1-of-23 PoC.

### Negative / documented debts (deliberate scope cuts, marked in code)

- **Classifier ceiling for 2+-level nesting** (`pack.py:264`,
  `LOOM-SIMPLIFY`): a failure nested two-or-more levels below a section
  (e.g. `mops.balance_sheet.rows.assets._error`) is invisible to
  `failed_sections`; the whole-pack `_partial` flag is the only signal
  for that case today. Upgrade path: a general recursive per-source
  provenance walk, gated on cross-market provenance-shape normalization
  (explicitly out of scope for this arc — see plan brief §Out of Scope
  "Output-shape unification across markets").
- **`tick`-cadence market-awareness deferred** (`cache_util.py:117`,
  `LOOM-SIMPLIFY`): `compute_ttl("tick", ...)` returns a flat 60s TTL
  rather than the trading-hours-aware 60s/1h split `cache-policy.md`
  documents, matching the one pre-existing implementation
  (`dgbas_client.py`'s `_compute_ttl`) this generalizes — it never
  exercised that distinction either. Upgrade path: add a `market`
  parameter and port cache-policy.md's `_is_market_open` table.
- **Cache-hit bookkeeping keys are documented behavior, not a bug**:
  `cache_util.load_cache` injects `_cache`, `_cache_age_seconds`,
  `_cache_ttl_seconds` into the returned `dict` on a hit. Clients whose
  underlying payload is a bare list (e.g. TWSE's `STOCK_DAY_ALL`) must
  wrap/unwrap around a `{"_rows": [...]}` marker to round-trip through
  that dict-shaped envelope and strip the bookkeeping keys before
  returning to callers (`twse_openapi_client.py:143-166`) — a
  documented, tested consequence of a shared cache module needing one
  storage shape across markets with different native payload shapes, not
  a defect.

### Neutral

- Existing cache files under `~/.cache/investing-toolkit/` are
  effectively discarded on upgrade (same precedent as ADR-0007's schema
  v2.0 migration decision: cache is reproducible from upstream APIs, no
  user-modified data lives there). No action required from the sole
  maintainer/user.
- `INVESTING_TOOLKIT_CACHE` becomes fully optional — previously "required
  by SKILL.md's canonical invocation (and silently wrong)", now "omit it
  entirely for the default `~/.cache/investing-toolkit` path, or set it
  deliberately to override".

## Alternatives considered

See plan brief `docs/loom/specs/2026-07-11-investing-toolkit-data-consolidation.md`
§Alternatives Considered for the full trade-off table (patch-in-place ×23;
shared-cache-module-via-extended-sync as a third sync group; full
fetch-architecture rewrite; external cache library). All four rejected —
summary: patching in place leaves the sync-discipline root cause intact;
extending the sync mechanism keeps a per-market skill boundary the user
does not value (they consume exclusively through the report layer);
a subprocess→import rewrite destroys per-client individual runnability
and was out of scope; `requests-cache`/`diskcache` don't fix the actual
bug (path validation) and `requests-cache` is incompatible with
yfinance's `curl_cffi` transport.

## References

- ADR-0002: Layer-1 staging-tier normalization — same failure class
  (well-formed-but-empty JSON silently propagating downstream) this ADR's
  exit-code contract also guards against, at the cache layer instead of
  the parse layer.
- ADR-0007: Skill-Self-Contained Cache Helpers — cadence-TTL policy
  retained (see "What is retained from ADR-0007" above); block-level
  guard design superseded (see header).
- ADR-0008: Remove MCP Server — established the single-consumer
  (Claude-Code-skill-only) model this ADR builds on; its "2 real
  cross-skill duplications" framing (yfinance ×5, fred ×2) is what this
  ADR collapses to 2 single copies inside `data-markets`.
- `docs/loom/specs/2026-07-11-investing-toolkit-data-consolidation.md` —
  brief (Problem / Users / Smallest End State / Alternatives / Out of
  Scope), user sign-off 2026-07-11.
- `docs/loom/plans/2026-07-11-investing-toolkit-data-consolidation.md` —
  12-task execution plan, tasks T1–T5d.
- `docs/cache-policy.md` — TTL band table `cache_util.compute_ttl`
  implements.
- `skills/data-markets/references/migration-grounding.md` — per-surface
  migration commit hashes + grounding basis for every external surface
  carried forward byte-identical.
