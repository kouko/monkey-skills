# legal-playbook-author

> Author / extend / revise the per-clause Markdown entries that power `legal-contract-review` and (Phase 2+) every other playbook-aware skill in legal-toolkit.

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

## What this skill does

`legal-playbook-author` is the **only sanctioned writer** of files under your working folder's `legal-playbook/`. (You can edit those files by hand of course; going through the skill enforces schema, prevents conflicts, and offers helpful prompts.)

Three modes auto-detected from context:

| Mode | Trigger | Output |
|---|---|---|
| **bootstrap** | `legal-playbook/` missing or empty | First-time setup; three-way choice: (a) seed from bundled fallback / (b) 5-question interview / (c) skip and use bundled read-only |
| **extend** | Playbook exists, user wants to add a new clause | New `legal-playbook/<clause-id>.md` (flat) or `<clause-id>/<variant-id>.md` (variant-folder) |
| **revise** | User points at an existing clause file | Selective field-by-field edit → diff confirm → write |

## When to use

- First-time install of legal-toolkit
- When `legal-contract-review` reports `source_type: advisory` (you have no entry for this clause) and you decide to codify your position
- When `legal-contract-review` reports a fallback was triggered and you want to tighten it
- Periodic refresh (the design recommends quarterly)

## When NOT to use

- You want to **read** the playbook, not change it → just open the file
- The task is really about contract review → use `/legal-contract-review`
- You want to add a non-clause asset (template, checklist, config) → those don't belong in `legal-playbook/`

## How it writes files

Every write is **per-question persisted** — if the conversation is interrupted mid-interview, the partial entry is still saved (marked `status: incomplete` in frontmatter; `TODO:` markers in unanswered body sections). Resuming the skill picks up where it left off.

## Stub templates

When the skill creates a new entry, it seeds the file from one of three stubs:

- [`assets/stub.flat.md`](assets/stub.flat.md) — flat clause (one Markdown file with frontmatter + body)
- [`assets/stub.variant.md`](assets/stub.variant.md) — per-variant file inside a variant-folder
- [`assets/stub._clause.md`](assets/stub._clause.md) — `_clause.md` container at the top of a variant-folder

## Variant-upgrade detection

In extend or revise mode, the skill watches for signals suggesting a flat clause should upgrade to a variant-folder:

- Different walk-aways at different deal sizes (「小單可以接受 X，大單絕對不行」)
- Counterparty-type-conditional positions (「對 enterprise 客戶會放鬆」)
- Jurisdiction overlays (「台灣只需要這樣，但 GDPR 要再加一層」)

When detected, the skill offers to migrate; the migration preserves the existing flat entry as the first variant.

## Disclaimer / Escalation Override

This skill ships the byte-identical Disclaimer + Override assets shared across all legal-toolkit output skills:

- [`assets/disclaimer-block.md`](assets/disclaimer-block.md) — appended to every emitted output (footer)
- [`assets/escalation-override.md`](assets/escalation-override.md) — prepended when high-risk triggers fire

Authoring playbook entries does not normally trigger Override (entries are negotiation rules, not legal opinions). The README auto-seeded into `legal-playbook/` during bootstrap includes the Disclaimer once.

## Anti-pattern defense

The skill enforces design note §七 5 anti-patterns:

- **Bloat** — SHOULD ≤ 24 clauses; warn when exceeded
- **Drift** — `last_updated` tracked; staleness warning > 180d
- **Conflict** — duplicate `clause_id` / overlapping `gates` detection
- **Static** — every entry has `## 為什麼這條重要` business translation
- **Over-rigid** — `escalate_to` is the escape valve; no entry rejects outright

## Reference

- SKILL.md (this skill's instructions): [`SKILL.md`](SKILL.md)
- Plugin spec: [`PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) / [`TECH-SPEC.md`](../../TECH-SPEC.md)
- Mode protocols: [`protocols/bootstrap-mode.md`](protocols/bootstrap-mode.md) / [`extend-mode.md`](protocols/extend-mode.md) / [`revise-mode.md`](protocols/revise-mode.md)
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## License

MIT — see [LICENSE](../../../LICENSE) at the monorepo root.
