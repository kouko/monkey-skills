# data-jp output schema overview

JSON Schema (draft-07) contracts for every `pack.py` output shape and the
embedded client-error envelope. Layer 2 (`analysis-*`) and Layer 3
(`report-*`) consumers should validate against these schemas before
treating a payload as well-formed.

All schema files live in `investing-toolkit/skills/data-jp/references/`
(flat layout — one level deep, no sub-folders, prefix-naming convention).

## Schemas

| Schema file                    | Pack            | Required `EDINET_API_KEY`? | Tier      |
|--------------------------------|-----------------|:--------------------------:|-----------|
| `schema-snapshot.json`         | `snapshot`      | no                         | tier_1    |
| `schema-memo-fetch.json`       | `memo-fetch`    | optional (tier-routed)     | tier_a / tier_2 |
| `schema-comps-multiples.json`  | `comps-multiples` | no                       | tier_1    |
| `schema-screener-batch.json`   | `screener-batch` | no                        | tier_1    |
| `schema-regime-pack.json`      | `regime-pack`   | no                         | tier_a    |
| `schema-error-envelope.json`   | (referenced from every pack schema) | n/a    | n/a       |

## Common envelope

Every pack output contains:

```json
{
  "pack": "<pack-name>",
  "fetched_at": "<UTC ISO 8601>",
  "_provenance": {
    "tier": "tier_1 | tier_a | tier_2",
    "tier_label": "<human-readable>",
    "sources": ["<source 1>", ...]
  }
}
```

Single-ticker packs (`snapshot`, `memo-fetch`) add `ticker` (bare 4-digit JP
証券コード) + `yf_ticker` (`.T` suffix). Batch packs (`comps-multiples`,
`screener-batch`) use a `tickers[]` array. `regime-pack` is ticker-less.

## JP-specific schema notes

### Ticker format

- Bare ticker: `^[0-9A-Z]{4,5}$` (4-digit 証券コード, e.g. `7203`, `9984`).
  Pattern accommodates the rare 5-char codes (e.g. `130A0`, `131A0`).
- yfinance ticker: `^[0-9A-Z]{4,5}\.(T|TO)$` — `.T` auto-appended by
  `pack.py`, `.TO` accepted on input and preserved.

### Currency

- Prices, marketCap, enterpriseValue: **JPY** for .T-listed tickers (yfinance
  default for the Tokyo exchange).
- Cross-rate fields (e.g. ECB-side real-yield, USD/JPY pulled from FRED)
  carry their own native unit in the per-block payload.

### Tier routing — `memo-fetch` only

`pack.py` checks `EDINET_API_KEY` at runtime:

| Key state | `fundamentals.tier` | `_provenance.tier` | `material_events`              |
|-----------|---------------------|--------------------|--------------------------------|
| set       | `tier_a`            | `tier_a`           | EDINET list-filings (180/220/350) |
| unset     | `tier_2`            | `tier_2`           | `{"_skipped": "..."}` stub     |

The schema expresses both paths via `oneOf` on the `fundamentals` and
`_provenance` properties. Tier 2 fallback's `_provenance.upgrade_hint` is
required and must contain the EDINET registration URL
(`https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html`).

The other four packs (`snapshot`, `comps-multiples`, `screener-batch`,
`regime-pack`) never touch EDINET and are not tier-routed.

### TDnet block (snapshot + memo-fetch)

`timely_disclosures` is the Yanoshin TDnet recent-index payload, fetched
with bare ticker (no `.T`), `limit=20`. Per-disclosure shape is the
Yanoshin schema (loosely typed `array<object>` in the schema — typical
keys: `pubdate`, `company_code`, `company_name`, `title`, `url`, `pdf_url`).

### `regime-pack` — JP real-rate caveat

`groups.real_rates.real_10y_monthly_ecb` may be `null` or carry an empty
`observations` array. ECB occasionally drops the JP real-yield series for
maintenance windows; per the analysis-macro-regime team's
`japan-real-rate-roadmap.md` reference, Layer 2 callers must handle this
as a soft-missing condition, not an error. The schema permits `null` and
`{observations: []}` as valid shapes.

## Error envelope

When a sibling client subprocess fails (uv missing, JSON-decode error,
non-zero exit, timeout), `pack.py:_run_client(...)` returns the
`schema-error-envelope.json` shape **embedded inline** at the position
where the successful payload would have appeared:

```json
{
  "error": "client timeout after 300s",
  "_cmd": ["uv", "run", "/path/to/yfinance_client.py", "..."],
  "_stderr": "<tail of stderr>",
  "_stdout_head": "<first 500 chars of stdout, on JSONDecodeError only>"
}
```

Every pack-schema `oneOf` branch lists the error envelope as an
alternative for fields populated by client subprocesses (`info`,
`price_history`, `timely_disclosures`, `fundamentals.annual`,
`groups.rates.call_rate_on`, ...). Layer 2 / Layer 3 consumers MUST treat
presence of `error` as "block unusable" and propagate the failure
without crashing.

For `comps-multiples`, when the **batch-level** yfinance call itself
fails, each per-ticker `multiples` object is replaced by a `{"error":
"..."}` envelope (the ticker entry is still present so input ordering is
preserved).

## Validation harness

```python
import json
from pathlib import Path
from jsonschema import Draft7Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7

base = Path("investing-toolkit/skills/data-jp/references")
resources = []
for p in base.glob("schema-*.json"):
    s = json.load(open(p))
    sid = s.get("$id")
    if sid:
        resources.append((sid, Resource(contents=s, specification=DRAFT7)))
registry = Registry().with_resources(resources)

schema = json.load(open(base / "schema-snapshot.json"))
sample = json.load(open("/tmp/jp-snap.json"))
Draft7Validator(schema, registry=registry).validate(sample)
```

Note: schemas use absolute `$id` URLs of the form
`https://monkey-skills/investing-toolkit/data-jp/<pack>.json`. These are
namespacing identifiers, not network resources — no HTTP fetches occur
when the `Registry` is pre-populated as shown above.

## Sample fixtures

`investing-toolkit/tests/data/fixtures/data-jp-*.json` — five fixtures,
one per pack, captured live against ticker `7203` (Toyota) on
2026-05-01 with no `EDINET_API_KEY` (so `memo-fetch` exercises the Tier 2
fallback shape).

Heavy nested arrays (`price_history.data`, `timely_disclosures.disclosures`,
`history_batch.tickers.<YF>.data`, BOJ / ECB / e-Stat `observations`) are
truncated to ≤5 entries to keep fixtures compact (~2-20 KB each); each
truncated container carries an inline `_truncated_for_fixture` /
`_observations_truncated` / `_data_truncated` annotation. The truncations
are schema-compatible — `pack.py` does not emit these annotations in
production output.

> **Fixture trim convention**: Truncation is **head-truncation** (oldest
> rows kept). Summary fields (`latest_close` / `latest_date` /
> `latest` / `reference_period`) reflect the most-recent observation
> at fixture-capture time and may not align with the head-truncated
> rows. Live `pack.py` output is not truncated. Same convention
> applies across all `data-{cn,jp,kr,tw,us}` fixtures.

| Fixture                                  | Bytes  | Pack            |
|------------------------------------------|--------|-----------------|
| `data-jp-snapshot-sample.json`           | ~7 KB  | snapshot        |
| `data-jp-memo-fetch-sample.json`         | ~16 KB | memo-fetch (Tier 2) |
| `data-jp-comps-multiples-sample.json`    | ~1.5 KB | comps-multiples |
| `data-jp-screener-batch-sample.json`     | ~20 KB | screener-batch  |
| `data-jp-regime-pack-sample.json`        | ~19 KB | regime-pack     |

A Tier A `memo-fetch` fixture is intentionally not committed — it requires
a live `EDINET_API_KEY`. To verify the Tier A schema branch locally:

```bash
EDINET_API_KEY=... INVESTING_TOOLKIT_CACHE=/tmp/jp-cache \
  uv run skills/data-jp/scripts/pack.py --ticker 7203 --pack memo-fetch \
  > /tmp/jp-memo-tier-a.json

uv run --with jsonschema --with referencing python3 -c "
import json
from pathlib import Path
from jsonschema import Draft7Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7
base = Path('investing-toolkit/skills/data-jp/references')
resources = []
for p in base.glob('schema-*.json'):
    s = json.load(open(p))
    sid = s.get('\$id')
    if sid: resources.append((sid, Resource(contents=s, specification=DRAFT7)))
registry = Registry().with_resources(resources)
schema = json.load(open(base / 'schema-memo-fetch.json'))
sample = json.load(open('/tmp/jp-memo-tier-a.json'))
Draft7Validator(schema, registry=registry).validate(sample)
print('Tier A memo-fetch validates')
"
```

## See also

- `investing-toolkit/skills/data-jp/SKILL.md` — pack contracts + tier-routing rationale
- `investing-toolkit/skills/data-jp/scripts/pack.py` — implementation
- `investing-toolkit/skills/analysis-macro-regime/references/japan-real-rate-roadmap.md`
  — context for the JP real-rate null-allowed contract
- `investing-toolkit/docs/adr/0001-data-analysis-report-layers.md` — three-layer ADR
