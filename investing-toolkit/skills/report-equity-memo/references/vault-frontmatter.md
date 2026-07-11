# Vault frontmatter schema — SSOT

> Toolkit-owned. Phase 4 emits this block unconditionally at the top of
> `/tmp/${TICKER_SAFE}-memo.md`. Phase 5b (obsidian-markdown) MUST NOT
> re-invent these fields — it owns placement / wikilinks / conventions
> only. See SKILL.md Phase 4 and Phase 5b.

## Fields (flat snake_case — vault convention)

| Field | Type | Source (this run) |
|---|---|---|
| `type` | string, literal | always `equity-memo` |
| `ticker` | string | Input `ticker` param |
| `market` | string | Country-detection table (SKILL.md) — market code, e.g. `tw`, `us`, `jp` |
| `date` | Date | today's date, ISO `YYYY-MM-DD` — **must be typed Date** in Obsidian properties, not text (see Bases gotcha below) |
| `verdict` | string | investing-team's memo §一 執行摘要 (HOLD/BUY/SELL/…) |
| `confidence` | string enum: `high` / `medium` / `low` | investing-team's memo §一 — map its wording onto this enum (e.g. 信心中等 → `medium`); if the memo reports none, omit the field rather than guessing |
| `price_at_analysis` | number | Phase 1 `fetch.json` → `current_price` |
| `intrinsic_mid` | number | Phase 3 `dcf.json` → `mid` |

## Bases date-typing gotcha

Obsidian Bases compares `date` properties as dates only when the vault's
Properties panel has typed that key as **Date** (not Text). If `date` was
ever written as plain text for this key, Bases falls back to string
comparison and sort/filter-by-date silently breaks. When emitting the
frontmatter block, use bare ISO (`date: 2026-07-11`, no quotes) — Obsidian
auto-detects unquoted `YYYY-MM-DD` as Date type on first write; quoting it
forces Text type.

## Sample `.base` snippet (track-record view, convenience only)

```yaml
views:
  - type: table
    name: Track Record
    filters:
      and:
        - 'type == "equity-memo"'
    order:
      - ticker
      - date
      - verdict
      - confidence
      - price_at_analysis
      - intrinsic_mid
    sort:
      - property: date
        direction: DESC
```

## Filename & folder convention (vault delivery)

Folder: `investing/memos/` (default-unless-user-says-otherwise — see
SKILL.md Phase 5b). Filename, all-English:

```
YYYY-MM-DD {identifier} Equity Memo.md
e.g. 2026-07-12 2330.TW Equity Memo.md
```

- `{identifier}` for equities is the Yahoo/RIC ticker **as-is**, dot
  suffix included (`2330.TW`, `7203.T`, `AAPL`). Interior dots are safe
  in Obsidian note names; only leading/trailing dots are not.
- The type descriptor is the literal `Equity Memo`, aligned with
  `type: equity-memo`. Future non-equity memo skills follow the same
  shape with their own descriptor (`FX Memo`, `Commodity Memo`) and a
  **clean identifier — NEVER a raw vendor symbol**: FX = ISO 4217
  concatenation (`USDTWD`), metals = ISO pseudo-currency (`XAUUSD`),
  energy = house codes documented at introduction time (`WTI`, `BRENT`,
  `NATGAS`), indices = caret stripped (`TWII`, `SPX`). Rationale: Yahoo
  sigils `=X` / `=F` / `^` are link-hostile in Obsidian (`^` is a
  block-reference char); vendor symbols belong in frontmatter fields,
  not filenames (RESOLVED 2026-07-12 with the user; industry pattern:
  Ghostfolio/Beancount strip vendor sigils at the storage boundary).
- Same ticker re-analyzed the same day: update the existing note (one
  note per ticker per day; earlier days are never touched).

## Casing status

RESOLVED (2026-07-11): the user's vault standardizes on all-lowercase
snake_case properties — the brief's conditional reversal (Alternatives §4,
docs/loom/specs/2026-07-11-investing-obsidian-memory-layer.md) fired, so
this schema uses flat snake_case (`price_at_analysis`, `intrinsic_mid`;
single-word fields unchanged). Do not reintroduce camelCase.
