# legal-toolkit

> In-house legal toolkit for 台灣 SME → 上市櫃 法務 — 7-layer schema-driven contract review, playbook-driven negotiation, disclaimer-driven outputs.

Read this in: **English** | [日本語](README.ja.md) | [繁體中文](README.zh-TW.md)

![version](https://img.shields.io/badge/version-0.3.2-blue) ![license](https://img.shields.io/badge/license-MIT-green) ![phase](https://img.shields.io/badge/phase-1.6_Eval-orange)

> ⚠️ **Not legal advice.** This is a free open-source tool, not a law firm and not a licensed practitioner. Every output ships with a Mandatory Disclaimer; high-risk findings ship with an Escalation Override (「請諮詢執業律師」). See [§Disclaimer policy](#disclaimer-policy).

## What it does

legal-toolkit gives in-house legal counsel — solo / SME / listed-mid — a **markdown-first, runtime-portable** workflow for the high-frequency 80% of in-house work: **contract review** (the 主戰場), **playbook authoring** (your company's negotiation rules), and (planned Phase 2-5) document drafting / incident response / issue spotting / research / contract lifecycle tracking / regulation watch / corporate governance / due-diligence quick-scan.

Three design commitments distinguish it from BigLaw-port tools:

1. **Schema-driven, not vibe-driven** — contract review runs a deterministic 7-layer pipeline (Stark 7 contract concepts / Adams 10 language categories / Burnham 6 functional tiers) with a Taiwan-jurisdiction overlay (強行/任意 規定二分 / 定型化契約 §247-1 / 六準則 contract interpretation).
2. **Playbook lives where you can see and edit it** — `legal-playbook/<clause>.md` in your working folder, visible, Markdown, git-trackable. Not buried in a SQLite blob; not in a hidden dotfolder; not in a vendor's cloud. Three-layer ownership: visible `legal-playbook/` (you own) + visible `legal-outputs/` (you own) + hidden `.legal-toolkit/` (tool internals).
3. **Disclaimer-driven, not feature-stripped** — Taiwan's 律師法 §48 governs **people**, not tools, and a free open-source utility ≠ a service. Hard-excluding legal-opinion output would gut half the planned sub-skills (issue-spot / research). Every output ships with a Mandatory Disclaimer; high-risk findings ship with an Escalation Override red banner.

## 3 skills (MVP + Phase 1.5 DSL infra, v0.2.0)

| Skill | Role |
|---|---|
| `using-legal-toolkit` | **Router** — recognises intent across 6 clusters (Playbook / Template / Runbook / IRAC / Tracker / Compliance) and dispatches; lists Phase 2-5 sub-skills as not-yet-available with a clear cluster menu. |
| `legal-playbook-author` | **Cross-cluster utility** — bootstrap / extend / revise modes; produces per-clause Markdown entries with deterministic frontmatter (`gates` / `walk_away_triggers` / `escalate_to` / `risk_default`) and LLM-comparison body (`preferred` / `fallback N` / `為什麼這條重要`). Detects when a flat clause should upgrade to a variant-folder (gate-keyed by deal_size / counterparty_type / jurisdiction). |
| `legal-contract-review` | **The main event** — 7-layer pipeline with TW overlay; ABAC pre-filter selects matched variants before LLM evaluation (so the LLM only sees one variant, never picks among them). Three modes: `review` (full 6-output), `redline` (focus on substitute clause text), `nda` (skip L2-L3 for simpler structure). Six output files: `issues.md` / `redline.md` / `memo-legal.md` / `memo-business.md` / `escalation.md` / `self-grade.md`. |

Phase 2-5 ships 8 more skills — see **[ROADMAP.md](ROADMAP.md)** for the v0.1.0 → v1.0.0 plan, version strategy, critical path, and risk callouts.

## Cold-start fallback (works without your own playbook)

First-time install: there is **no `legal-playbook/`** in your working folder. The toolkit still operates — `legal-contract-review` reads **4 bundled fallback baseline clauses** from inside the plugin:

| clause_id | Layout |
|---|---|
| `confidentiality` | flat |
| `governing-law-jurisdiction` | flat |
| `auto-renewal` | flat |
| `termination-and-survival` | flat |

Each finding generated from a bundled clause carries a banner: `⚠️ Using bundled fallback baseline — run legal-playbook-author to customise for your company`. The `escalate_to` field ships as a placeholder string (`[請編輯為你公司的角色：法務主管 / GC / 部門主管]`); review-time detection emits a warning so users notice the placeholder before treating output as final.

Run `legal-playbook-author bootstrap` to migrate from bundled fallback to your own customised playbook. **v0.2.0 (Phase 1.5)** expands the bundled baseline to 8 clauses — adds variant-folder `limitation-of-liability` (small/mid/large-deal), `indemnification` (small/mid/large-deal), `data-protection-dpa` (tw-only/gdpr-overlay/cross-border), plus flat `ip-assignment-and-license`. Run `seed_baseline.py` to extract the full 8-clause tarball into your working folder.

## Playbook layout (the source of negotiation truth)

```
<your working folder>/
├── legal-playbook/                    ← visible, you own
│   ├── README.md                      # auto-seeded "how to maintain"
│   ├── confidentiality.md             # flat clause
│   ├── governing-law-jurisdiction.md
│   ├── limitation-of-liability/       ← variant-folder (deal-size keyed)
│   │   ├── _clause.md
│   │   ├── small-deal.md              # gates: deal_size < 100K USD
│   │   ├── mid-deal.md                # gates: 100K-1M USD
│   │   └── large-deal.md              # gates: >= 1M USD
│   └── data-protection-dpa/           ← variant-folder (jurisdiction keyed)
│       ├── _clause.md
│       ├── tw-only.md
│       ├── gdpr-overlay.md
│       └── cross-border.md
│
├── legal-outputs/                     ← visible, you own (per-run review results)
│   └── 2026-05-11-acme-saas-msa/
│       ├── issues.md
│       ├── redline.md
│       ├── memo-legal.md
│       ├── memo-business.md
│       ├── escalation.md
│       └── self-grade.md
│
└── .legal-toolkit/                    ← hidden, tool owns
    ├── config.yml                     # profile + global_rules
    ├── schema.json
    └── cache/
```

Discovery walks `<cwd>` → 5 levels of ancestors → BFS depth 5 → bundled fallback. Add `legal-outputs/` and `.legal-toolkit/` to `.gitignore`; track `legal-playbook/` (it's your company's negotiation IP).

## Contract review pipeline

```
INPUT (contract path + contract_type + jurisdiction + deal_context)
   ↓
LOAD PLAYBOOK  (scan legal-playbook/ → build index; validate schema; staleness warning if last_updated > 180 days)
   ↓
[Taiwan only]  L0a 強行/任意 規定二分  →  L0b 定型化契約 §247-1 + 消保法 §11-1
   ↓
L1  Expectations           bundled template ∪ playbook_index keys
L2  Anatomy mapping        preamble / definitions / action / endgame / boilerplate
L3  Categorize             Stark 7 contract concepts + Adams 10 language categories
L4  Functional tier        money / risk / control / standards / endgame
L5  Domain priority        bundled[contract_type] + playbook augment
L6  Cycle / cross-ref      if-breach branch; definitions re-read; missing-items flag (loops until gaps == 0 AND cycle >= 2)
   ↓
[Taiwan only]  L6.5  六準則 contract interpretation  (當事人目的 → 習慣 → 任意法規 → 誠信原則)
   ↓
L7  Evaluate Against Playbook  (per-clause)
       ├── clause.id in user playbook_index?     → user variant evaluation
       ├── clause.id in bundled fallback?         → bundled fallback + banner
       └── neither?                               → advisory mode + suggest playbook-author extend
   ↓
   For each matched entry:
   ABAC pre-filter (gates vs deal_context) → single matched variant
   walk_away_trigger LLM judge → 🔴 walk / 🟢 preferred / 🟡 fallback / 🔴 worse
   LLM uncertain? → use frontmatter risk_default
   ↓
SELF-GRADE  (Harvey dual-score: answer_score / source_score — never collapsed; all-pass binary)
   ↓
OUTPUT  6 files → legal-outputs/<timestamp>-<contract-name>/
   + Mandatory Disclaimer (every output, footer)
   + Escalation Override (high-risk only, header red banner)
```

## Disclaimer policy

Every output file carries a footer Mandatory Disclaimer:

- Not a law firm and not a licensed practitioner
- Free open-source tool, not a service (no fee, no SLA, no advisor-client relationship)
- Outputs are for internal decision-making reference only; do **not** constitute legal advice
- For litigation / criminal exposure / major business decisions, **consult a licensed lawyer**
- Cite primary sources from 全國法規資料庫 / 司法院判決系統 / 主管機關官網, not from this tool's output

High-risk findings — `risk_default: red` / `walk_away_triggered: true` / `confidence < 0.7` / criminal-liability mention / `deal_size > escalation_threshold` — additionally trigger an **Escalation Override** red banner at the top of the affected output, stating: *「請諮詢執業律師」*.

Industry context: Harvey / Spellbook / LawGeex / Lawsnote / 律果 LegalSign.ai all use disclaimer-driven design; none hard-excludes legal-opinion output. Taiwan's 律師法 §48 governs the natural-person practice of law (representing clients before courts / authorities; holding out as a lawyer; fee-based legal-document drafting for external parties) — it does not extend to free open-source utilities or to in-house counsel doing internal advisory work.

## Install

```bash
# In Claude Code, with monkey-skills marketplace enabled
/plugin install legal-toolkit@monkey-skills
```

The plugin is self-contained — bundled fallback baseline + protocols + schemas ship inside. The toolkit is local-FS-first and works fully offline; no external API calls. Tested on Claude Code CLI; Cowork "Work in a Folder" mount supported but the FUSE pre-existing-file behavior may require a one-time onboarding step (Phase 2 will document).

## Usage

```
/using-legal-toolkit
```

Three common shapes:

| Shape | Trigger | Path |
|---|---|---|
| **Shape A** — review a contract | "Review this SaaS MSA against our playbook" / "Redline this NDA" | router → contract-review → 6 outputs |
| **Shape B** — author / extend playbook | "Add a clause for auto-renewal" / "Update our LoL fallback for enterprise" | router → playbook-author (extend / revise mode) |
| **Shape C** — first-time install | "I just installed this, what do I do?" | router → playbook-author (bootstrap mode) → offer to seed from bundled fallback or interview-from-scratch |

Direct skill invocation is supported when intent is unambiguous (e.g. `/legal-contract-review` on a contract path).

## Language policy (cross-cutting)

**English skeleton + zh-TW flesh** (decided in design phase, locked in TECH-SPEC):

- **English**: SKILL.md / protocols / scripts / JSON schema keys — LLM instruction-following is measurably stronger in English; aligns with Anthropic's official skill conventions; better cross-runtime portability.
- **zh-TW (preserve original)**: legal citations (民法 §247-1 / 個資法 §21 / 勞基法 §9-1) / Taiwan case law / baseline playbook body content / user-facing output.
- **Bilingual triggers**: frontmatter `description` lists EN + zh-TW keyword aliases — coverage goes up, false-positive routing does not.
- **No translation of**: legal articles (translating 民法 §247-1 to "unconscionability" makes the LLM misroute to US doctrine), Stark / Adams / Burnham terminology (專有名詞, breaks citation lookup).

## Status

- **Version**: 0.3.0 (2026-05-12)
- **Stability**: MVP + Phase 1.5 DSL + Phase 1.6 Eval infra complete; dogfood calibration is owner-run, not ship-blocking
- **Phase**: 1.6 (Eval rubric + self_grade.py + dogfood procedure) — see [ROADMAP.md](ROADMAP.md) for v0.1.0 → v1.0.0 plan
- **Test suite**: 110+ tests across schema / discover / validate / detect_conflicts / abac_filter / build_baseline / seed_baseline / self_grade — all green via `uv run --with jsonschema --with pyyaml --with pytest`
- **License**: MIT (plugin code)

## Reference

- **ROADMAP**: [`ROADMAP.md`](ROADMAP.md) — 7-phase plan, version strategy, risk callouts
- **PRODUCT-SPEC**: (Step B, pending) — business + design direction
- **TECH-SPEC**: (Step B, pending) — module + data-flow + interface contracts
- **Design note (SoT)**: `<obsidian-vault>/research/2026-05-09 法務 Agent Skill (legal-toolkit) 整體架構與執行流程設計.md` (1344 lines, 38+ locked decisions)

## Contributing

PRs welcome via `https://github.com/kouko/monkey-skills`. Conventions:

- **Skill structure** follows monkey-skills convention: flat skill directory, no nested subfolders inside `<subfolder>/`. See repo `CLAUDE.md` for hook enforcement.
- **Commit prefixes**: `feat(legal-toolkit)` / `fix(legal-toolkit)` / `docs(legal-toolkit)` / `chore(legal-toolkit)` / `refactor(legal-toolkit)` / `test(legal-toolkit)`.
- **Three skill READMEs (en/ja/zh-TW) required** per monkey-skills PR #150 — applies to per-skill README.md as well as this plugin-level README.
- **Disclaimer block** — every output file's footer disclaimer text must remain byte-identical across the three skills shipping it (Phase 6 adds a CI gate).

## License

MIT — see [LICENSE](../LICENSE) at the repository root.
