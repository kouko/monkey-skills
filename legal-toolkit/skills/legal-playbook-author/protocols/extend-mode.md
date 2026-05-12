# extend-mode — add a new clause to an existing playbook

**Trigger**: `legal-playbook/` exists with at least one entry, AND the user wants to add a new clause that is not yet present.
**Inverse**: see `protocols/bootstrap-mode.md` (no playbook yet) / `protocols/revise-mode.md` (modify existing entry).

---

## Purpose

Extend mode is the **steady-state path** for growing a playbook over time. Users come back here whenever `legal-contract-review` reports `source_type: advisory` for some clause and they decide to codify their position. The mode reuses the 5-question interview from bootstrap mode but starts from an empty stub (no Path A seed available — by definition the clause is new).

Extend mode produces **one** entry per invocation. To add several clauses in one sitting, loop the mode.

---

## Pipeline

### Step 1 — Identify the clause

Ask which clause to add. Acceptable forms:

- English clause id: `confidentiality`, `limitation-of-liability`, `indemnification`, etc. (kebab-case)
- zh-TW clause name: 「保密」「責任上限」「賠償」「終止」 — the skill maps these to the canonical English `clause_id`
- "Look at this contract section": the user pastes a clause from a recent review; the skill suggests a clause_id

If the user is vague ("加一條 NDA 那個的"), ask for clarification with 2-3 plausible candidates from a curated list of common clause types.

**Validate**: ensure the proposed `clause_id` does not already exist in `<cwd>/legal-playbook/`. If it does, abort and suggest revise mode instead.

### Step 2 — Decide initial layout (flat vs variant-folder)

Default: **flat**. Most clauses start flat and graduate to variant-folder later when the user actually has different walk-aways at different deal sizes.

Promote to variant-folder upfront only if the user explicitly says one of:
- "對小單跟大單我要分開設"
- "GDPR overlay 要另外一條"
- "對 enterprise 跟 startup 不一樣"

In those cases, create the `<clause-id>/` folder with `_clause.md` first (from `assets/stub._clause.md`), then proceed to Step 3 for the first variant.

### Step 3 — 5-question interview (same as bootstrap mode)

Run the same 5-question interview as `bootstrap-mode.md` Step 3b. Persist after each answer.

Target file:
- Flat layout: `<cwd>/legal-playbook/<clause-id>.md`
- Variant-folder layout: `<cwd>/legal-playbook/<clause-id>/<variant-id>.md`
  (For the first variant, ask the user for a variant_id; suggest defaults like `default` / `small-deal` / `tw-only` based on the upgrade trigger they gave.)

### Step 4 — Fill the rest of the frontmatter

After the 5 questions, compute / ask for:

- `clause_id` ← from Step 1
- `variant_id` (variant-folder only) ← from Step 2 / Step 3 prompt
- `contract_types_applicable: array` — best-effort guess; ask user to confirm
- `gates` (variant only) — based on the user's upgrade trigger; offer common gate shapes:
  ```yaml
  # deal-size-keyed
  gates:
    deal_size:
      gte: 100000
      lt: 1000000

  # jurisdiction-keyed
  gates:
    data_subjects_jurisdiction:
      any_of: [EU, UK, EEA]

  # counterparty-keyed
  gates:
    counterparty_type:
      eq: enterprise
  ```
- `last_updated: <today>`
- `owner` — default to the existing playbook's owner field if any; ask if missing
- `source_type: user_playbook`

### Step 5 — Variant-upgrade re-check (flat layout only)

If the user chose flat layout in Step 2 but their Q1 / Q5 answers reveal variant-upgrade triggers (see SKILL.md §"Variant-upgrade detection"), prompt:

> 我看到你提到「<the trigger phrase>」——這通常表示這條 clause 對不同 deal size /
> counterparty / jurisdiction 有不同立場。要不要升級為 variant-folder 結構？
> (yes — split into a folder / no — keep flat / remind me later)

- yes → migrate: move `<cwd>/legal-playbook/<clause-id>.md` to `<cwd>/legal-playbook/<clause-id>/<original-as-first-variant>.md`, create `_clause.md`, prompt user to author additional variants.
- no → set `variant_upgrade_offered: true` in frontmatter; do not ask again.
- remind me later → do nothing this run; the upgrade will be offered again next time the user revises this clause.

### Step 6 — Schema validate (v0.2.0+ Phase 1.5)

Run the validator script:

```bash
uv run <plugin>/skills/legal-playbook-author/scripts/validate_schema.py \
    <cwd>/legal-playbook/<just-written-file>
```

The script validates against `assets/schema.json` (JSON Schema 2020-12,
oneOf flat / variant / _clause). Report any errors to user; for
warnings, do not abort. For hard errors (cross-shape contamination,
missing required), prompt user to fix before proceeding to Step 7.

### Step 7 — Conflict scan (v0.2.0+ Phase 1.5)

Run the conflict detector across the entire playbook:

```bash
uv run <plugin>/skills/legal-playbook-author/scripts/detect_conflicts.py \
    <cwd>/legal-playbook/
```

Catches:
- Duplicate `clause_id` (flat-vs-flat, flat-vs-folder)
- Overlapping `gates` between variants of the same clause
- Missing `clause_id`

Quick scan of the rest of `legal-playbook/`:
- Any other entry with overlapping `gates` for this `clause_id`? (Shouldn't happen if Step 1 validation worked, but check anyway.)
- Any entry that references this `clause_id` indirectly (e.g. via `## 相關判例` body link)?

Report to user.

### Step 8 — Report and offer next step

```
✅ Wrote <cwd>/legal-playbook/<clause-id>.md (or <clause-id>/<variant-id>.md)

Frontmatter validation: PASS / WARN: <issue>
Conflicts:               none / <list>
Triggers captured:       <count walk_away_triggers> walk_away, <count fallbacks> fallback layers

Suggested next:
- [ ] Add another clause? Type: extend <next-clause-id>
- [ ] Add another variant to <clause-id>? (variant-folder only) Type: extend <clause-id>/<new-variant>
- [ ] Run a contract review against the updated playbook? /legal-contract-review <path>
- [ ] Exit. (Your file is saved.)
```

---

## Output contract

```
✅ extend-mode complete.
   File written: <path>
   Clause id: <clause-id>
   Variant id: <variant-id> (or "—" if flat)
   Layout: flat / variant-folder
   Validation: PASS / WARN
```

---

## Edge cases

- **User wants to add a non-clause asset** (template / checklist / config) — refuse and explain that those don't belong in `legal-playbook/`. Suggest the right home (templates go in Phase 2's `legal-document-draft` skill assets; configs go in `.legal-toolkit/config.yml`).
- **User mixes English and zh-TW for the clause name** ("加一條 limitation-of-liability") — accept; canonical `clause_id` is the English kebab-case form.
- **User adds the 25th+ clause** — emit a soft warning per the anti-pattern defense (SKILL.md §"Anti-pattern defense"); proceed if confirmed.
- **User aborts mid-interview** — files are per-question persisted; on next invocation, detect the partial entry and offer to resume / discard.
- **Variant-folder upgrade refused but the user comes back next session with a clearly variant-keyed walk-away** — revise mode will re-detect and re-offer.
