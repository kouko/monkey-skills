# profile.yml schema v1 → v2 migration

> **Source of truth**: this file is in `legal-toolkit/scripts/canonical/` and distributed byte-identical to `legal-document-draft/references/` and `legal-incident-response/references/` via `scripts/distribute.py`.
> **Effective**: legal-toolkit v0.4.3 (2026-05-14)
> **Previous**: v1 schema, in force from v0.3.6 (2026-05-12) to v0.4.2 (2026-05-13)

## What changed

Additive bump. Existing v1 profile **STRUCTURE** is forward-compatible; only the `schema_version` literal must change.

| Field | v1 | v2 |
|---|---|---|
| `schema_version` | `const: 1` | `const: 2` |
| `dpo.phone` | not in `dpo.properties`; rejected by `additionalProperties: false` | `dpo.properties.phone: { type: string }`; optional |
| `dpo.required` | `[name, email]` | `[name, email]` (unchanged; phone is optional) |
| All other fields | (unchanged) | (unchanged) |

## How to migrate an existing v1 profile.yml

1. Open `legal-playbook/profile.yml`.
2. Change `schema_version: 1` to `schema_version: 2`.
3. (Optional) Add a `phone` field under `dpo`:
   ```yaml
   dpo:
     name: 王小明
     email: dpo@example.com
     phone: "+886-2-1234-5678"   # NEW in v2; optional
   ```
4. Re-run any skill that loads profile.yml (e.g., `legal-incident-response`). `load_profile.py` validates against schema v2.

## When to populate `dpo.phone`

- **Recommended**: in-house DPO with dedicated direct line (incident response: PDPC 通報落款 / 主管機關函覆 落款 use this).
- **Acceptable workaround**: leave `dpo.phone` absent; templates fall back to `general_contact.phone` for落款 (公司總機).
- **Not recommended**: setting `dpo.phone` equal to `general_contact.phone` — the schema distinguishes them so future stakeholders can update one without the other (e.g., 委外 DPO with rotating personal phone vs static 公司總機).

## Why the bump

v0.4.2 SP3b `legal-incident-response` shipped 6 doc sites assuming `dpo.phone` exists (PDPC 通報文 落款 + 函覆 落款 + 2 binding tables + 2 checklists). The v1 schema's `additionalProperties: false` on `dpo` rejected any profile.yml that tried to supply this field. Live dogfood surfaced this on 2026-05-14; the fix is the additive v2 bump rather than removing `dpo.phone` from 6 doc sites (DPO 個人聯絡 ≠ 公司總機 — keep the field, fix the schema).

## Backward compatibility guarantee

The bump is **additive**. The structural shape of a v1 profile.yml (no `dpo.phone`, no `external_counsel`, no `regulatory_authorities`) remains a valid shape under v2. Only the `schema_version` literal must move from `1` to `2`. No other content rewriting required.

Regression coverage: `legal-toolkit/tests/test_load_profile.py::test_v1_structure_validates_when_schema_version_bumped` locks this guarantee.
