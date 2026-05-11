---
name: legal-contract-review
description: |
  Taiwan in-house legal contract review skill. Runs a 7-layer schema-driven pipeline (Stark 7 contract concepts / Adams 10 language categories / Burnham 6 functional tiers) with Taiwan-jurisdiction overlay (L0a 強行/任意 規定二分 / L0b 定型化契約 §247-1 / L6.5 六準則契約解釋) and a playbook-driven L7 evaluate step (ABAC pre-filter + Harvey dual-score self-grade). Outputs 6 structured Markdown files (issues / redline / memo-legal / memo-business / escalation / self-grade) under legal-outputs/<timestamp>-<contract-name>/. Three modes: review (default, full 6-output) / redline (focus on substitute clause text) / nda (skip L2-L3 for simpler structure). Cold-start fallback: if user has no legal-playbook/, reads 4 bundled fallback baselines (confidentiality / governing-law / auto-renewal / termination-and-survival) so the toolkit produces useful output on first install.

  台灣 in-house 法務合約審查 skill。台湾 in-house 法務向け契約レビュー skill。

  TRIGGER (中英雙語):
  - contract review / redline / NDA review / contract analysis
  - 合約審查 / 合約 review / 合約紅線 / 條款比對 / NDA review
  - 服務合約 / SaaS / MSA / 採購合約 / 勞動契約 / 保密協議 / DPA

  USE WHEN: User provides a contract file (or pastes a contract) and
  asks for review, redlining, risk analysis, or playbook comparison.
version: 0.1.0
---

# legal-contract-review

The main event. Runs a 7-layer pipeline against a contract and emits
6 structured output files. The pipeline is **deterministic** (LLM
runs each layer once, no looping outside L6's bounded cycle-check),
**playbook-driven** (L7 evaluates each clause against the user's
playbook or the 4 bundled fallback baselines), and **disclaimer-
driven** (every output ships with the Mandatory Disclaimer footer;
high-risk findings ship with the Escalation Override red banner).

## Language Policy

- Skill instructions (this file, protocols/, checklists/): English
- Domain content (legal terms, citations, baseline playbooks): zh-TW (preserve original)
- User-facing output: zh-TW (Traditional Chinese)
- Mixed-language is by design — do NOT translate domain terms.

## Inputs

| Field | Type | Required | Default |
|---|---|---|---|
| `contract_path` | string (path) or pasted contract text | yes | — |
| `contract_type` | string (`SaaS` / `MSA` / `NDA` / `採購` / `勞動` / `DPA` / etc.) | no | auto-detect from L2 |
| `jurisdiction` | string (`TW` / `US` / `CN` / ...) | no | `TW` |
| `deal_context` | object: `{deal_size?: number, currency?: string, counterparty_type?: string, data_subjects_jurisdiction?: string}` | no | best-effort extract from contract |
| `mode` | `"review"` (default) / `"redline"` / `"nda"` | no | `review` |
| `stance` | `"ours"` / `"theirs"` / `"neutral"` | no | `ours` |

## Outputs

Six files under `<cwd>/legal-outputs/<YYYY-MM-DD>-<contract-name-slugified>/`:

| File | Content |
|---|---|
| `issues.md` | Issue 矩陣 + 5 商業議題標籤 + playbook trace |
| `redline.md` | 修改建議 + 替代條款文字 (from playbook body or LLM-generated) |
| `memo-legal.md` | CRAC 完整版 + citation + carve-outs |
| `memo-business.md` | Why / What / What-if 三句業務翻譯 |
| `escalation.md` | 哪些升級給誰 + trigger 條件 |
| `self-grade.md` | Harvey dual-score (answer_score / source_score) + failed_criteria |

Each output is validated against its JSON schema in [`assets/`](assets/).
Each output's footer carries the Mandatory Disclaimer (see [§Disclaimer](#disclaimer)).
High-risk outputs prepend the Escalation Override banner.

## Pipeline (7 layers + TW overlay)

Layer-by-layer protocols under [`protocols/`](protocols/):

| Layer | File | When |
|---|---|---|
| **L0a** | [`L0a-strong-arbitrary.md`](protocols/L0a-strong-arbitrary.md) | jurisdiction == TW only |
| **L0b** | [`L0b-standard-form.md`](protocols/L0b-standard-form.md) | jurisdiction == TW only |
| **L1** | [`L1-expectations.md`](protocols/L1-expectations.md) | always |
| **L2** | [`L2-anatomy.md`](protocols/L2-anatomy.md) | mode != nda |
| **L3** | [`L3-categorize.md`](protocols/L3-categorize.md) | mode != nda |
| **L4** | [`L4-functional-tier.md`](protocols/L4-functional-tier.md) | always |
| **L5** | [`L5-domain-priority.md`](protocols/L5-domain-priority.md) | always |
| **L6** | [`L6-cycle.md`](protocols/L6-cycle.md) | always (loops until gaps==0 AND cycle>=2) |
| **L6.5** | [`L6_5-tw-six-criteria.md`](protocols/L6_5-tw-six-criteria.md) | jurisdiction == TW only |
| **L7** | [`L7-evaluate.md`](protocols/L7-evaluate.md) | always; the playbook integration layer |

### Mode dispatch

| Mode | Layers run | Output emphasis |
|---|---|---|
| `review` (default) | L0a → L0b → L1 → L2 → L3 → L4 → L5 → L6 → L6.5 → L7 | full 6-output |
| `redline` | L1 → L2 → L3 → L4 → L5 → L6 → L6.5 → L7 | strong substitute-clause generation from playbook body |
| `nda` | bundled NDA template → L4 → L5 → L6 → L7 | issues + redline + memo-legal only (3 outputs) |

## When to use

- User provides a contract file and asks for review / redline / risk analysis
- Dispatched by `using-legal-toolkit` router on contract-shaped intent
- User is preparing a counterproposal and wants to systematically compare against their playbook

## When NOT to use

- The task is really about authoring a playbook entry → `/legal-playbook-author`
- The task is starting a privacy policy / ToS / NDA from scratch → (Phase 2) `legal-document-draft`
- The task is a fact-pattern issue-spotting question ("can we do X?") → (Phase 3) `legal-issue-spot`
- The task is litigation strategy / complex negotiation tactics — **out of scope by design**, refuse and tell user to consult a practising lawyer

## Cold-start fallback (works without user playbook)

If `discover_playbook()` returns empty (no `legal-playbook/` in working folder or ancestors), the skill DOES NOT abort. Instead, L7 evaluates against 4 bundled fallback baseline clauses in [`assets/baseline-fallback-*.md`](assets/):

- `baseline-fallback-confidentiality.md`
- `baseline-fallback-governing-law-jurisdiction.md`
- `baseline-fallback-auto-renewal.md`
- `baseline-fallback-termination-and-survival.md`

Each finding generated from a bundled clause:
- Tagged `source_type: bundled_fallback` in `issues.md`
- Stamped with a banner: `⚠️ 使用 bundled fallback baseline — 建議跑 legal-playbook-author 客製化你公司的紅線`
- If `escalate_to` starts with `[請編輯` (the placeholder), L7 prepends a warning callout to `escalation.md` urging customisation

Clauses outside the 4 bundled fallback (e.g. LoL / Indemnification / DPA — those are Phase 1.5 baseline additions) fall through to **advisory mode** in L7: finding marked `source_type: advisory`, with a suggestion `建議呼叫 /legal-playbook-author extend <clause-id>` to codify a custom position.

See [`protocols/L7-evaluate.md`](protocols/L7-evaluate.md) for the full fallback decision tree.

## Playbook integration (L7)

L7 is the heart of the skill — the layer that actually compares each
contract clause to a playbook entry and emits findings.

Per-clause flow:

```
clause_id (from L3 / L5)
   ↓
IDX_LOOKUP — is clause_id in user playbook_index?
   ├── yes → load user entry → VTYPE check
   └── no  → BUNDLED_LOOKUP: is clause_id in fallback?
       ├── yes → load bundled + tag source_type=bundled_fallback + banner
       └── no  → ADVISORY finding + suggest playbook-author extend
   ↓
VTYPE check — flat or variant-folder?
   ├── flat → use entry directly
   └── variant-folder → ABAC pre-filter (gates vs deal_context) → matched variant
       ├── 0 matched → ADVISORY (deal context doesn't fit any variant)
       ├── 1 matched → use it
       └── >1 matched → log warning, use first (v1 — Phase 1.5 detect_conflicts.py
                        catches the over-broad gate at validate time)
   ↓
escalate_to placeholder detect:
  if entry.escalate_to.startswith("[請編輯"):
    emit_warning("uncustomised escalate_to placeholder")
    add callout to escalation.md
  (pipeline continues regardless)
   ↓
walk_away_trigger LLM judge (one-shot in Phase 1):
   ├── 🔴 walk → use frontmatter escalate_to (do NOT let LLM rewrite)
   └── 🟢/🟡/🔴 → LLM body comparison (preferred / fallback prose):
       ├── ≥ preferred → 🟢 finding
       ├── ∈ fallback range → 🟡 finding
       └── < worst fallback → 🔴 finding
   ↓
LLM uncertain (low confidence) → fallback to frontmatter risk_default
   ↓
collect finding with source_type tag + playbook_trace + triggers cited
```

Per-layer playbook access (full table in [TECH-SPEC §3.3](../../TECH-SPEC.md#33-legal-contract-review)):

| Layer | reads playbook? | what |
|---|---|---|
| L0a / L0b | no | bundled TW legal knowledge |
| L1 | index (filenames + clause field) | expectations = bundled ∪ playbook |
| L2 | no | pure structure mapping |
| L3 | no | universal taxonomy (Stark / Adams) |
| L4 | optional | cross-check business_issues tags |
| L5 | optional | priority augment |
| L6 | index | missing-items high-weight flag |
| L6.5 | no | bundled TW interpretation rules |
| **L7** | **frontmatter + body (matched only)** | the main integration |

ABAC pre-filter is rule-based (no LLM); it runs BEFORE the LLM
comparison so the LLM only ever sees a single matched variant —
simpler, cheaper, testable.

## Disclaimer + Escalation Override

Every output file receives the Mandatory Disclaimer footer from
[`assets/disclaimer-block.md`](assets/disclaimer-block.md) — runtime
fills the `[X.Y.Z]` / `[timestamp]` / `[pipeline path]` / `[self-grade]`
placeholders.

High-risk findings (any of: `risk_default: red` matched / `walk_away_triggered: true` / LLM confidence < 0.7 / criminal-liability mention / `deal_size > escalation_threshold` / cross-border + 個資事故) cause [`assets/escalation-override.md`](assets/escalation-override.md) to be prepended to the affected output's header.

When `--external-share` flag is passed:
- Playbook IDs in `issues.md` / `memo-legal.md` / `escalation.md` are stripped (replaced with generic "依本公司紅線政策")
- Override red banner is **never stripped** — counterparties need to see it even more than internal readers do

## Schemas

JSON Schema validation of each output file (Phase 1: schema files
exist + protocols reference them; Phase 1.5 adds programmatic
validation in `scripts/`):

- [`assets/output-schema-issues.json`](assets/output-schema-issues.json)
- [`assets/output-schema-redline.json`](assets/output-schema-redline.json)
- [`assets/output-schema-memo-legal.json`](assets/output-schema-memo-legal.json)
- [`assets/output-schema-memo-business.json`](assets/output-schema-memo-business.json)
- [`assets/output-schema-escalation.json`](assets/output-schema-escalation.json)
- [`assets/output-schema-self-grade.json`](assets/output-schema-self-grade.json)

## Self-grade (Harvey dual-score)

After the pipeline emits the 6 outputs, the skill runs a binary
all-pass rubric against the produced findings. Two separate scores,
never collapsed (Harvey BigLaw Bench convention):

- **answer_score**: how many of N rubric criteria the answer
  satisfies (e.g. "all 7 layers executed" / "all clauses tagged with
  Stark concept" / "every finding has a playbook trace")
- **source_score**: how many of M citations are valid (real, exist,
  support the conclusion they're attached to)

Failed criteria are listed explicitly in `self-grade.md` — no
rounding, no averaging, no hiding.

Phase 1 ships the rubric as protocol stubs at
[`checklists/answer-criteria.md`](checklists/answer-criteria.md) and
[`checklists/source-criteria.md`](checklists/source-criteria.md);
Phase 1.6 adds `scripts/self_grade.py` for automated scoring + the
dogfood corpus correlation gate (Pearson ≥ 0.6 / 0.7).

## References

- Plugin spec: [`PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) / [`TECH-SPEC.md`](../../TECH-SPEC.md)
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)
- Domain references:
  - [`references/stark-7-concepts.md`](references/stark-7-concepts.md) — Stark's 7 contract concepts (Obligation / Discretion / Representation / Warranty / Condition / Declaration / Performance)
  - [`references/adams-10-categories.md`](references/adams-10-categories.md) — Adams's 10 categories of contract language
  - [`references/domain-priority-by-type.md`](references/domain-priority-by-type.md) — contract-type-specific clause priority lists

## Output contract (signal to router)

Last line(s) of the skill end with:

```
✅ legal-contract-review complete.
   Output folder: <abs path to legal-outputs/<timestamp>-<name>/>
   Mode used: review / redline / nda
   Playbook source: user_playbook (N clauses matched) / bundled_fallback (M clauses) / advisory (K clauses)
   Self-grade: answer=N/M / source=N/M
   High-risk findings: <count> (Override prepended to <list of files>)
```
