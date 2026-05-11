---
name: legal-playbook-author
description: |
  Author and maintain your company's contract-negotiation playbook for the legal-toolkit ecosystem. Produces / updates per-clause Markdown entries under `legal-playbook/` in the working folder, with deterministic frontmatter (gates / walk_away_triggers / escalate_to / risk_default) and LLM-comparison body (preferred / fallback N / 為什麼這條重要). Supports three modes: bootstrap (first-time setup with cold-start fallback seeding option), extend (add new clause), revise (modify existing clause selectively). Auto-detects when a flat clause should upgrade to a variant-folder schema (gate-keyed by deal_size / counterparty_type / jurisdiction).

  契約議價 playbook の作成・維持。台湾 in-house 法務向け playbook authoring skill。

  TRIGGER (中英雙語):
  - playbook author / playbook bootstrap / extend / revise
  - 建 playbook / 改紅線 / 加條款 / 升級 fallback / 更新 walk-away
  - 第一次安裝 / first install / cold start / seed baseline

  USE WHEN: user wants to create or modify clause-level negotiation rules
  in their legal-playbook/ folder, or is setting up for the first time.
version: 0.1.0
---

# legal-playbook-author

Author / extend / revise the per-clause Markdown entries that power
`legal-contract-review` and (Phase 2+) every other playbook-aware
skill in the toolkit. The playbook lives in the **user's** working
folder at `legal-playbook/` — visible, Markdown, git-trackable. This
skill is the only sanctioned writer of those files; the user can of
course edit them by hand, but going through the skill enforces
schema, prevents conflicts, and offers helpful prompts.

## Language Policy

- Skill instructions (this file, protocols/, checklists/): English
- Domain content (legal terms, citations, baseline playbooks): zh-TW (preserve original)
- User-facing output: zh-TW (Traditional Chinese)
- Mixed-language is by design — do NOT translate domain terms.

## Modes

The skill auto-detects mode from context; user can also pass explicitly.

| Mode | Trigger | Output |
|---|---|---|
| **bootstrap** | `legal-playbook/` missing or empty | First-time setup; offers 3-way choice (seed from bundled fallback / 5-question interview / read-only mode) |
| **extend** | User says "add a clause for X" or `legal-playbook/` exists but new clause requested | New `legal-playbook/<clause-id>.md` (or `<clause-id>/<variant-id>.md`) |
| **revise** | User points at an existing clause file or says "update LoL fallback" | Selective interview → diff-confirm → patched file |

Each mode runs the protocol under `protocols/{mode}-mode.md`. See those
files for the exact pipeline.

## When to use

- First-time install of `legal-toolkit` (router → here for bootstrap)
- After `legal-contract-review` surfaces a finding like "advisory mode — no playbook entry for X" or "your fallback was triggered, consider tightening"
- Periodic refresh (the design recommends quarterly)
- After `legal-regulation-watch` (Phase 4) flags a regulation change affecting a clause

## When NOT to use

- The user wants to **read** the playbook, not change it — direct file
  open is fine; this skill is for write operations.
- The user is asking a question that is really about `legal-contract-review`
  (e.g. "review this NDA") — route back to the contract-review skill.
- The user wants to add a non-clause asset (a template, a checklist, a
  config) — those belong outside `legal-playbook/`.

## Inputs

- `mode: "bootstrap" | "extend" | "revise"` (auto-detect if absent)
- `clause_id: string` (optional; required for extend / revise if not
  inferable from conversation context)
- `target_file: path` (optional; revise mode if user points at a specific
  file)

## Outputs

Files written to the user's working folder (NEVER to the plugin bundle):

```
<working folder>/legal-playbook/
├── README.md                          # written by bootstrap mode on first run
├── <clause-id>.md                     # flat layout (simple clauses)
└── <clause-id>/                       # variant-folder layout (complex clauses)
    ├── _clause.md
    └── <variant-id>.md
```

Every write is **per-question persisted** — if the conversation is
interrupted mid-interview, the partial entry is still saved with
`status: incomplete` in the frontmatter and a `TODO:` marker in
each unanswered body section. Resuming the skill picks up where it
left off.

## Workflow shape

```
detect mode
   ↓
load matching protocol → protocols/{bootstrap|extend|revise}-mode.md
   ↓
interactive interview (5 questions for new entries; diff-driven for revise)
   ↓
per-question persist to disk
   ↓
detect variant-upgrade trigger (user mentioned deal_size / counterparty_type)
   ↓ if triggered
offer to migrate flat → variant-folder layout
   ↓
schema validate (best-effort warn; Phase 1.5 makes this stricter)
   ↓
report PASS / WARN / what triggered changed
   ↓
ask "continue with next clause?" → loop or exit
```

## Stub assets

When producing a new entry, this skill seeds the file from one of three
stubs under `assets/`:

- [`assets/stub.flat.md`](assets/stub.flat.md) — flat clause (simplest;
  one Markdown file with frontmatter + body)
- [`assets/stub.variant.md`](assets/stub.variant.md) — per-variant file
  inside a variant-folder
- [`assets/stub._clause.md`](assets/stub._clause.md) — `_clause.md`
  container at the top of a variant-folder

## Disclaimer + Escalation Override

Any output that includes legal-advice-shaped text inherits the
Mandatory Disclaimer footer at [`assets/disclaimer-block.md`](assets/disclaimer-block.md)
and, when triggered, the Escalation Override callout at
[`assets/escalation-override.md`](assets/escalation-override.md).

Authoring playbook entries does not normally trigger Override (the
entries themselves are negotiation rules, not legal opinions on
specific facts). However, the README seeded into `legal-playbook/`
during bootstrap mode includes the Disclaimer footer once.

## Schema (Quick Reference)

Full schema is in [TECH-SPEC §4](../../../TECH-SPEC.md#4-interface--data-flow).
Frontmatter shape per layout:

| Field | flat | `<variant>.md` | `_clause.md` |
|---|---|---|---|
| `clause_id` | required | required | required |
| `variant_id` | — | required | — |
| `contract_types_applicable` | optional | — | required |
| `gates` | — | required | — |
| `walk_away_triggers` | required ≥ 1 | required ≥ 1 | — |
| `escalate_to` | required | required | — |
| `risk_default` | required (green/yellow/red) | required | — |
| `has_variants` | — | — | required (`true`) |
| `source_type` | required (user_playbook \| bundled_fallback \| advisory) | required | required |
| `last_updated` | recommended (ISO date) | recommended | recommended |

Body convention (after frontmatter):

```markdown
# <Clause Name in zh-TW>

## 偏好立場
<preferred 立場文字, 1-3 句>

## Fallback 1
<第一退讓階梯>

## 為什麼這條重要
<業務翻譯，一句話告訴非法務>
```

Optional sections: `## Fallback 2` / `## 替代條款文字` / `## 相關判例` —
add when the clause has the depth to support them; leave out otherwise.

## Variant-upgrade detection

When in extend or revise mode, watch for these signals in the user's
answers that suggest the clause should move from flat to variant-folder:

- User mentions different walk-aways at different deal sizes
  ("小單可以接受 X，大單絕對不行")
- User mentions counterparty-type-conditional positions
  ("對 enterprise 客戶我們會放鬆，對 startup 比較嚴")
- User mentions jurisdiction overlays
  ("台灣只需要這樣，但 GDPR 要再加一層")

When at least one of these is detected, offer to migrate the entry to
a variant-folder. The migration preserves the existing flat entry as
the first variant (renamed to `<clause-id>/_clause.md` + the body kept
in a sensible variant id like `default.md` or `small-deal.md`), then
prompts the user to author additional variants.

Migration is opt-in; if the user prefers to keep the flat layout, the
skill records `variant_upgrade_offered: true` in the frontmatter so
the same offer is not repeated on every revise.

## Anti-pattern defense (design note §七)

- **Bloat**: SHOULD ≤ 24 clauses in the playbook; warn when exceeded.
  Body length SHOULD ≤ 200 lines per file.
- **Drift**: `last_updated` is tracked; `legal-contract-review` warns
  on entries older than 180 days at session start.
- **Conflict**: duplicate `clause_id` and overlapping `gates` are
  caught at validate time (Phase 1: best-effort warning; Phase 1.5:
  `scripts/detect_conflicts.py` runs the full check).
- **Static / no-enforcement**: every entry has a `## 為什麼這條重要`
  business-translation section so the rule cannot become a fossil.
- **Over-rigid**: `escalate_to` is the escape valve; no entry rejects
  outright, it always escalates.

## Output contract (the protocol files own this)

See `protocols/{bootstrap,extend,revise}-mode.md`. Each protocol ends
with a `Report` section that the skill prints back to the user:

```
✅ Wrote legal-playbook/<clause-id>.md (or <clause-id>/<variant-id>.md)
- Frontmatter: PASS / WARN: <issue>
- Conflicts:   none / <list>
- Triggers added / changed: <list>
- last_updated bumped to: 2026-05-11

Suggested next:
- [ ] Review another clause? Type: extend <clause-id>
- [ ] Run a contract review against the updated playbook? /legal-contract-review <path>
- [ ] Exit. (Your file is saved.)
```

## References

- Plugin spec: [`PRODUCT-SPEC.md`](../../../PRODUCT-SPEC.md) / [`TECH-SPEC.md`](../../../TECH-SPEC.md)
- Roadmap: [`ROADMAP.md`](../../../ROADMAP.md)
- Design note (SoT): see TECH-SPEC §10 References
