# Vault frontmatter schema — SSOT

> Toolkit-owned. Phase 4 emits this block unconditionally at the top of
> `/tmp/${TICKER_SAFE}-memo.md`. Phase 5b (obsidian-markdown) MUST NOT
> re-invent these fields — it owns placement / wikilinks / conventions
> only. See SKILL.md Phase 4 and Phase 5b.

## Fields (flat camelCase)

| Field | Type | Source (this run) |
|---|---|---|
| `type` | string, literal | always `equity-memo` |
| `ticker` | string | Input `ticker` param |
| `market` | string | Country-detection table (SKILL.md) — market code, e.g. `tw`, `us`, `jp` |
| `date` | Date | today's date, ISO `YYYY-MM-DD` — **must be typed Date** in Obsidian properties, not text (see Bases gotcha below) |
| `verdict` | string | investing-team's memo §一 執行摘要 (HOLD/BUY/SELL/…) |
| `confidence` | string enum: `high` / `medium` / `low` | investing-team's memo §一 — map its wording onto this enum (e.g. 信心中等 → `medium`); if the memo reports none, omit the field rather than guessing |
| `priceAtAnalysis` | number | Phase 1 `fetch.json` → `current_price` |
| `intrinsicMid` | number | Phase 3 `dcf.json` → `mid` |

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
      - priceAtAnalysis
      - intrinsicMid
    sort:
      - property: date
        direction: DESC
```

## Casing status

Pending: casing to be re-checked against live vault properties.
`obsidian-cli` was not available in this environment / no vault
configured — this pilot ships flat camelCase per the brief's default
(docs/loom/specs/2026-07-11-investing-obsidian-memory-layer.md
Alternatives §4); re-check when a live vault is reachable and follow the
vault's existing casing if it already standardizes differently.
