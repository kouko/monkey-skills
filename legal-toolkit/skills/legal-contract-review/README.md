# legal-contract-review

> The main event of legal-toolkit. 7-layer schema-driven contract review (Stark + Adams + Burnham + Taiwan overlay) with playbook-driven L7 evaluation and disclaimer-driven outputs.

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

## What this skill does

Runs a deterministic 7-layer pipeline against a contract and emits **6 structured Markdown files**:

| File | Content |
|---|---|
| `issues.md` | Findings matrix + business-issue tags + playbook trace |
| `redline.md` | Substitute clause text (from playbook body or LLM-generated) |
| `memo-legal.md` | Full CRAC memo with statute / case citations |
| `memo-business.md` | 3-sentence Why/What/What-if for non-legal stakeholders |
| `escalation.md` | Who-signs-what + trigger conditions |
| `self-grade.md` | Harvey dual-score (answer + source) with failed criteria listed |

Each output ships with the Mandatory Disclaimer footer; high-risk findings prepend the Escalation Override red banner.

## Pipeline

```
INPUT (contract + type + jurisdiction + deal_context + mode + stance)
   ↓
LOAD PLAYBOOK (user legal-playbook/ OR bundled fallback)
   ↓
[TW only] L0a 強行/任意 → L0b 定型化契約 §247-1
   ↓
L1 Expectations → L2 Anatomy → L3 Categorize → L4 Functional tier → L5 Domain priority → L6 Cycle
   ↓
[TW only] L6.5 六準則契約解釋
   ↓
L7 Evaluate against playbook (ABAC pre-filter + LLM compare)
   ↓
SELF-GRADE (Harvey dual-score: answer / source, never collapsed)
   ↓
WRITE 6 outputs → legal-outputs/<timestamp>-<contract-name>/
```

Each layer's protocol file under [`protocols/`](protocols/) is self-contained instruction.

## Three modes

| Mode | Layers run | Output emphasis |
|---|---|---|
| `review` (default) | L0a → L7 + L6.5 (full) | 6-output full review |
| `redline` | L1-L7 + L6.5 | Substitute clause text from playbook body |
| `nda` | bundled NDA template + L4-L7 | Issues + redline + memo-legal (3 outputs) |

## Cold-start fallback

If the user has no `legal-playbook/`, the skill **does not abort**. L7 reads 4 bundled fallback baselines from [`assets/`](assets/):

- `baseline-fallback-confidentiality.md`
- `baseline-fallback-governing-law-jurisdiction.md`
- `baseline-fallback-auto-renewal.md`
- `baseline-fallback-termination-and-survival.md`

Findings derived from bundled fallback carry a banner urging customisation. The `escalate_to` field uses `[請編輯為你公司的角色：...]` placeholder; L7 detects it and adds a warning callout to `escalation.md`.

Clauses outside the 4 bundled fallback fall through to **advisory mode** in L7: finding marked `source_type: advisory`, with a suggestion to run `legal-playbook-author extend <clause-id>`.

Phase 1.5 expands the bundled fallback to 8 clauses (adds LoL / Indemnification / DPA / IP-Assignment with variant-folder layout).

## Inputs

| Field | Required | Default |
|---|---|---|
| `contract_path` | yes | — |
| `contract_type` | no | auto-detect |
| `jurisdiction` | no | `TW` |
| `deal_context` | no | best-effort extract |
| `mode` | no | `review` |
| `stance` | no | `ours` |

## When to use

- Reviewing a contract before signing / counterproposal
- Producing redlines for back-and-forth negotiation
- Comparing terms against your playbook for portfolio consistency
- Generating a memo for legal-counsel discussion

## When NOT to use

- Want to **author** a playbook entry → `/legal-playbook-author`
- Want to **start** a privacy policy / ToS from scratch → (Phase 2) `legal-document-draft`
- Fact-pattern question ("can we do X?") → (Phase 3) `legal-issue-spot`
- Litigation strategy / complex negotiation tactics — **out of scope by design**

## Output structure

```
<cwd>/legal-outputs/<YYYY-MM-DD>-<contract-name-slugified>/
├── issues.md              # findings matrix
├── redline.md             # substitute clauses
├── memo-legal.md          # CRAC + citations
├── memo-business.md       # Why/What/What-if
├── escalation.md          # who-signs-what
└── self-grade.md          # answer + source dual-score
```

Every file footer: Mandatory Disclaimer (from `assets/disclaimer-block.md`)
High-risk files header: Escalation Override red banner (from `assets/escalation-override.md`)

## External-share mode

`--external-share` flag strips playbook IDs from `issues.md` / `memo-legal.md` / `escalation.md` (replaced with "依本公司紅線政策"). The Override red banner is **never** stripped.

## Reference

- SKILL.md (instruction): [`SKILL.md`](SKILL.md)
- Per-layer protocols: [`protocols/`](protocols/)
- Output schemas: [`assets/output-schema-*.json`](assets/)
- Bundled fallback: [`assets/baseline-fallback-*.md`](assets/)
- Self-grade rubric: [`checklists/answer-criteria.md`](checklists/answer-criteria.md) + [`source-criteria.md`](checklists/source-criteria.md)
- Domain references: [`references/`](references/) (Stark 7 concepts / Adams 10 categories / per-type priority)
- Plugin spec: [`PRODUCT-SPEC.md`](../../PRODUCT-SPEC.md) / [`TECH-SPEC.md`](../../TECH-SPEC.md)
- Roadmap: [`ROADMAP.md`](../../ROADMAP.md)

## License

MIT — see [LICENSE](../../../LICENSE) at the monorepo root.
