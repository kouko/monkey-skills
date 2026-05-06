# Optional fetch scripts (translation-toolkit v0.1.0)

Two scripts ship for users who want larger glossary coverage at the cost of
non-bundled licensing:

## `fetch-microsoft-terms.py`
- Source: Microsoft Terminology Collection (~33k entries × 100+ languages).
- License: GRAY. Microsoft Learn allows "use to develop localized versions or
  integrate into other terminology collections" but does not explicitly license
  redistribution. NOT bundled.
- Personal cache only; verify license before commercial use.
- Cache: `~/.cache/translation-toolkit/microsoft-terminology/`

## `fetch-jpo-utx.py`
- Source: 特許庁 UTX patent term dictionary (~130k EN-JA terms).
- License: AAMT — single dead-copy redistribution NOT permitted; format-converted
  derivatives permitted with attribution to 特許庁 + INPIT.
- NOT bundled; fetch implies attribution responsibility.
- Cache: `~/.cache/translation-toolkit/jpo-utx/`

## How they integrate
At runtime, the active skill checks for cache presence at startup. If found,
entries are loaded as L2-tier glossary (sit alongside bundled glossary in
the 4-tier fallthrough). If absent, the script is a no-op.

## Disclaimer
Both upstream sources may change URL or license terms. The scripts are
best-effort fetchers; verify upstream availability before relying on them
in production.
