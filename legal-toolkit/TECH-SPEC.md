# TECH-SPEC — legal-toolkit

> **Owner**: code-team (technical contract — module / data-flow / interface)
> **Companion**: [PRODUCT-SPEC.md](PRODUCT-SPEC.md) — business + design direction (planning-team owned)
> **Source of design**: `<obsidian-vault>/research/2026-05-09 法務 Agent Skill (legal-toolkit) 整體架構與執行流程設計.md` (1344 lines)
> **Roadmap**: [ROADMAP.md](ROADMAP.md)

## Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 0.1.0-draft | 2026-05-11 | kouko | Initial spec extracted from design note §2 + §3 + §4 + §5 + §6 |

---

## 1. Scope & Constraints

### 1.1 Delivery form

- monkey-skills marketplace plugin: `legal-toolkit/` 一個目錄
- `plugin.json` 宣告 (`name` / `version` / `description` / `author` / `license` / `keywords`)
- 加入 repo-level `.claude-plugin/marketplace.json` 條目（description **byte-identical**，CI gate by `scripts/check-marketplace-description-sync.py`）
- 3-lang README（en / ja / zh-TW）on plugin root + 每個 skill 內

### 1.2 Goals (技術目標；PRODUCT-SPEC §3.1 KR 對映)

| # | 技術目標 | 對映 PRODUCT-SPEC Goal |
|---|---|---|
| T1 | 3 skill SKILL.md + protocols + assets 全 ship | G1 |
| T2 | 4 條 bundled fallback baseline 在 `legal-contract-review/assets/baseline-fallback-*.md` | G2 |
| T3 | 7-layer pipeline protocols 全 implementing instructions written | G3 |
| T4 | Disclaimer + Escalation Override 在 3 skill assets 都 ship，內容 byte-identical | G4 |
| T5 | playbook-author bootstrap 5 題 protocols 實作 | G5 |
| T6 | 通過 monkey-skills CI lint（marketplace sync / skill structure / shared conventions / folder structure hook） | G6 |

### 1.3 Non-Goals (技術層面明列拒絕)

| 非目標 | 為什麼 |
|---|---|
| ❌ Vector embedding / RAG | Long context + ABAC pre-filter 在 < 100 entries 規模更穩；Phase 1 不需要 |
| ❌ Custom UI / Web app | Plugin 是 CLI-native；UI = Claude Code / Cowork host 提供 |
| ❌ DB（Postgres / SQLite for playbook）| Playbook 是 markdown file；本機 fs 即 db；Phase 4 contract-tracker 才用 SQLite |
| ❌ Server / API hosting | 無外部服務；完全 local-FS-first |
| ❌ 自寫 LLM client | 透過 host runtime（Claude Code / Cowork）跑；plugin 不 import anthropic SDK |
| ❌ Scripts/*.py 在 MVP（Phase 1） | Phase 1 是 instructions-only；scripts 留 Phase 1.5 |

### 1.4 Hard constraints

- **Anthropic skill folder convention**：`<skill>/<subfolder>/` 內不可再開 subfolder；hook `validate-skill-folder-structure.sh` 擋
- **CLAUDE.md type whitelist**：commit type ∈ {refactor / feat / fix / chore / docs / test}；scope **mandatory kebab-case** `[a-z][a-z0-9-]*`
- **monkey-skills 3-lang README convention**（PR #150）：en/ja/zh-TW 三份；plugin root + per-skill 都要
- **Marketplace description byte-identical**：`marketplace.json` 條目 `description` 跟 `plugin.json` 的 `description` 必須 byte-identical；`scripts/check-marketplace-description-sync.py` 擋
- **Disclaimer / Override 跨 skill byte-identical**：3 個 ship 它們的 skill 中 `assets/disclaimer-block.md` + `assets/escalation-override.md` 內容必須 byte-identical（Phase 6 CI gate；Phase 1-5 靠 review discipline）

---

## 2. Architecture

### 2.1 Plugin layout

```
legal-toolkit/
├── .claude-plugin/
│   └── plugin.json                      # v0.1.0
├── README.md / README.ja.md / README.zh-TW.md
├── PRODUCT-SPEC.md
├── TECH-SPEC.md                         # this file
├── ROADMAP.md
└── skills/
    ├── using-legal-toolkit/             # MVP — router
    │   ├── SKILL.md
    │   └── README.md / README.ja.md / README.zh-TW.md
    │
    ├── legal-playbook-author/           # MVP — cross-cluster utility
    │   ├── SKILL.md
    │   ├── protocols/
    │   │   ├── bootstrap-mode.md
    │   │   ├── extend-mode.md
    │   │   └── revise-mode.md
    │   ├── assets/
    │   │   ├── stub.flat.md             # stub template — simple flat clause
    │   │   ├── stub.variant.md          # stub template — variant file
    │   │   ├── stub._clause.md          # stub template — _clause.md container
    │   │   ├── disclaimer-block.md      # byte-identical with the other 2 skills
    │   │   └── escalation-override.md   # byte-identical with the other 2 skills
    │   └── README.md / README.ja.md / README.zh-TW.md
    │
    └── legal-contract-review/           # MVP — main event
        ├── SKILL.md
        ├── protocols/
        │   ├── L0a-strong-arbitrary.md
        │   ├── L0b-standard-form.md
        │   ├── L1-expectations.md
        │   ├── L2-anatomy.md
        │   ├── L3-categorize.md
        │   ├── L4-functional-tier.md
        │   ├── L5-domain-priority.md
        │   ├── L6-cycle.md
        │   ├── L6_5-tw-six-criteria.md
        │   └── L7-evaluate.md
        ├── assets/
        │   ├── output-schema-issues.json
        │   ├── output-schema-redline.json
        │   ├── output-schema-memo-legal.json
        │   ├── output-schema-memo-business.json
        │   ├── output-schema-escalation.json
        │   ├── output-schema-self-grade.json
        │   ├── baseline-fallback-confidentiality.md
        │   ├── baseline-fallback-governing-law-jurisdiction.md
        │   ├── baseline-fallback-auto-renewal.md
        │   ├── baseline-fallback-termination-and-survival.md
        │   ├── disclaimer-block.md       # byte-identical
        │   └── escalation-override.md    # byte-identical
        ├── checklists/
        │   ├── answer-criteria.md        # stub for Phase 1.6 rubric
        │   └── source-criteria.md        # stub for Phase 1.6 rubric
        ├── references/
        │   ├── stark-7-concepts.md
        │   ├── adams-10-categories.md
        │   └── domain-priority-by-type.md
        └── README.md / README.ja.md / README.zh-TW.md
```

**Phase 1.5+ 擴充**（不在 MVP，但 plugin layout 已預留）：

```
        skills/legal-contract-review/
        ├── scripts/                       # Phase 1.5 — add here
        │   ├── abac_filter.py
        │   ├── seed_baseline.py
        │   └── self_grade.py
        └── assets/
            ├── baseline-playbooks.tar.gz  # Phase 1.5 — full 8 baseline incl variant-folder
            └── seed-manifest.yml
        skills/legal-playbook-author/
        ├── scripts/                       # Phase 1.5
        │   ├── discover_playbook.py
        │   ├── validate_schema.py
        │   └── detect_conflicts.py
        └── assets/schema.json
```

### 2.2 Working folder (使用者端)

```
<user's working folder>/
├── legal-playbook/                       # visible — user owns; tracked in git
│   ├── README.md                         # seeded by author bootstrap
│   ├── <clause-id>.md                    # flat clause
│   └── <clause-id>/                      # variant-folder clause
│       ├── _clause.md
│       └── <variant-id>.md
├── legal-outputs/                        # visible — user owns; .gitignore'd
│   └── <timestamp>-<contract-name>/
│       ├── issues.md
│       ├── redline.md
│       ├── memo-legal.md
│       ├── memo-business.md
│       ├── escalation.md
│       └── self-grade.md
└── .legal-toolkit/                       # hidden — tool owns; .gitignore'd
    ├── config.yml                        # profile + global_rules
    ├── schema.json                       # frontmatter validation (copied from bundle at first use)
    ├── seed-history.yml                  # baseline seed version tracking
    └── cache/                            # parsed contract cache / LLM intermediate
```

### 2.3 Cross-skill dependency graph

```
                       ┌─────────────────┐
                       │ using-legal-    │
                       │   toolkit       │  ← router; reads no playbook
                       └────────┬────────┘
                                │ dispatch
                ┌───────────────┴───────────────┐
                ↓                               ↓
       ┌────────────────┐              ┌────────────────────┐
       │ legal-playbook-│              │ legal-contract-    │
       │   author       │              │   review           │
       │                │              │                    │
       │ writes:        │              │ reads:             │
       │  legal-        │ ─────────→   │  legal-playbook/   │
       │   playbook/    │  produces    │  bundled fallback  │
       │                │              │  .legal-toolkit/   │
       │ reads:         │              │                    │
       │  bundled stubs │              │ writes:            │
       │  bundled       │              │  legal-outputs/    │
       │   fallback     │              │                    │
       └────────────────┘              └────────────────────┘

Phase 2-5 sub-skill 都會讀 legal-playbook/（contract-tracker / regulation-watch /
document-draft override / etc.）—— author 是 cross-cluster utility，是所有 playbook-
aware skill 的 prerequisite。
```

### 2.4 External dependencies

| 依賴 | 目的 | 階段 |
|---|---|---|
| Anthropic Claude Code CLI | host runtime | Phase 1+ |
| Anthropic Cowork（optional）| "Work in a Folder" mount | Phase 1+（最佳 Phase 2 onboarding 後）|
| Python 3.10+ + `uv` | Phase 1.5+ scripts/ runtime (PEP 723 inline metadata) | Phase 1.5+ |
| `jsonschema` (via PEP 723) | playbook frontmatter validation | Phase 1.5 |
| `pyyaml` (via PEP 723) | config.yml / seed-manifest.yml read | Phase 1.5 |

**無依賴 / 無 import**：anthropic SDK / openai SDK / FAISS / vector DB / 任何 web framework。Plugin = pure markdown + JSON schemas + Python scripts (Phase 1.5+)。

---

## 3. Module Design

### 3.1 `using-legal-toolkit` (router)

**Abstraction**: Model System（routing primitive; no plan/adapt/interact loop）

**Input**: 使用者自然語言請求 + 可能附檔案路徑

**Output**: dispatch to one of 11 sub-skills（或在 Phase 1 只 dispatch 到 3 個 MVP skill，其他 8 個標 not-yet-available）

**Internal logic**:

1. 抽 intent keywords（中英雙語 — 「合約」 / "contract" / "redline" / "playbook" / etc.）
2. 6-cluster Q tree（design note §3.1）：
   - Q1 合約 review/redline/nda → `legal-contract-review`
   - Q2 起草 privacy/tos/dpa/nda → `legal-document-draft`（Phase 2）
   - Q3 事故應變（個資 / 主管機關 / 違約） → `legal-incident-response`（Phase 2）
   - Q4 fact-driven 諮詢 / 法律研究 → `legal-issue-spot` / `legal-research`（Phase 3）
   - Q5 合約 lifecycle / 法規追蹤 → `legal-contract-tracker` / `legal-regulation-watch`（Phase 4）
   - Q6 公司治理 / DD → `legal-corporate-governance` / `legal-dd-quickscan`（Phase 5 — BLOCKED）
   - Q7 建/改 playbook → `legal-playbook-author`
3. 多義 priority：playbook-author > 主任務 skill（先跑主任務，最後建議呼叫 author）
4. 識別失敗：列 6-cluster 選單請使用者選，**不亂猜**

**SKILL.md 結構** (Phase 1):
- frontmatter: name / description（含 EN + zh-TW trigger keywords）/ tools
- body sections: When to use / Decision tree / Output format / Phase 2-5 not-yet-available notice / Language directive

### 3.2 `legal-playbook-author`

**Abstraction**: Workflow（goal = produce playbook entry; plan + adapt + interact 三能力齊備）

**Input**: mode (auto-detect or explicit) + optional clause hint

**Output**: `legal-playbook/<clause-id>.md` 或 `<clause-id>/<variant-id>.md`（落到使用者本機）

**Mode decisions**:

```
mode := auto_detect()
   ├── legal-playbook/ 不存在 / 空 → bootstrap
   ├── 使用者說 "add clause X" → extend
   └── 指向既有 clause file → revise
```

**Bootstrap mode** (key flow):

1. 偵測 `legal-playbook/` empty/missing
2. Offer 三選一：
   - (a) Seed from bundled fallback 4 條（copy `legal-contract-review/assets/baseline-fallback-*.md` to user's `legal-playbook/`，加 `[請編輯]` 提示）
   - (b) 5-question interview (Q_WAT / Q_ESC / Q_RISK / Q_PREF / Q_FB / Q_BIZ) → 產 stub flat + body
   - (c) 暫不建 → exit；contract-review 會自動用 bundled fallback read-only
3. 寫回策略：per-question persist（design note §3.2 決定 14），中斷不遺失
4. 偵測「需要 variants」（user 答 walk_away 提到 deal_size / counterparty_type）→ offer 升級為 variant-folder
5. 結束時 schema validate（best-effort + warn，Phase 1 暫無實作；Phase 1.5 加 `validate_schema.py`）

**Extend mode**: load 既有 index → 問 clause_id → 走 bootstrap 後半段（5 題 interview）
**Revise mode**: load 既有 file → diff-driven selective interview → 寫回

**Files**: SKILL.md + 3 protocol files + 3 stub assets + disclaimer/override assets + 3-lang README

### 3.3 `legal-contract-review`

**Abstraction**: Workflow (7-layer schema-driven pipeline + TW overlay + L7 playbook integration)

**Input**:
- `contract_path: string` (required)
- `contract_type: string` (optional — SaaS / MSA / NDA / 採購 / 勞動 / DPA / ...; default = auto-detect from L2)
- `jurisdiction: string` (default = TW)
- `deal_context: { deal_size?: number, currency?: string, counterparty_type?: string }` (optional but recommended)
- `mode: "review" | "redline" | "nda"` (default = review)
- `stance: "ours" | "theirs" | "neutral"` (default = ours)

**Output**: 6 files → `legal-outputs/<timestamp>-<contract-name>/`

**Pipeline DAG** — see [PRODUCT-SPEC.md](PRODUCT-SPEC.md) §5.1 entry chart + design note §3.3.1 full mermaid.

**Per-layer playbook access** (design note §3.3.2 table):

| Layer | reads playbook? | 讀什麼 | 用途 |
|---|---|---|---|
| L0a / L0b | ❌ | — | bundled TW 法律知識（強行規定清單 / §247-1） |
| L1 | ✅ | index (檔名 / `clause` 欄位) | expectations = bundled ∪ playbook |
| L2 | ❌ | — | 純結構 mapping |
| L3 | ❌ | — | 普世 taxonomy（Stark / Adams） |
| L4 | ⚠️ 可選 | index frontmatter `business_issues` | cross-check 標籤一致性 |
| L5 | ⚠️ 可選 | index | priority 排序 augment |
| L6 | ✅ | index | missing-items 高權重 flag |
| L6.5 | ❌ | — | bundled TW 解釋規則 |
| **L7** | **✅** | **frontmatter + body (matched only)** | 評斷 + escalation + 替代條款 |

→ **ABAC pre-filter** 在 L7 LLM 前面跑（rule-based, no LLM），LLM 永遠只看單一 matched variant。

**Mode 分支**:

| mode | 跑哪些 layer | 主要輸出 |
|---|---|---|
| `review` | L0a-L7 全跑 | 6 份檔案齊全 |
| `redline` | L1-L7 全跑，L7 強化「替代條款文字」 | 主推 redline.md，其他簡化 |
| `nda` | bundled NDA template + L4-L7（NDA 結構簡單跳過 L2-L3） | issues + redline + memo-legal 三份 |

**Files**: SKILL.md + 10 protocol files + 6 output schemas + 4 baseline-fallback + 2 disclaimer/override + 2 checklist stub + 3 references + 3-lang README

---

## 4. Interface & Data Flow

### 4.1 Playbook frontmatter schema

#### 4.1.1 Flat clause (simple)

```yaml
---
clause_id: confidentiality                       # required, kebab-case
contract_types_applicable: [SaaS, MSA, NDA]      # optional
walk_away_triggers:                              # required, ≥ 1 item
  - "單方面（只我方有義務）"
  - "永久保密（影響營運）"
escalate_to: "[請編輯：通常 = 法務主管 / GC]"      # required; placeholder allowed for fallback
risk_default: yellow                             # required ∈ {green, yellow, red}
currency: USD                                    # optional ∈ {USD, TWD}
last_updated: 2026-05-09                         # recommended (ISO date)
owner: kouko                                     # optional
source_type: user_playbook                       # required ∈ {user_playbook, bundled_fallback, advisory}
---
```

#### 4.1.2 Variant-folder `_clause.md` (container)

```yaml
---
clause_id: limitation-of-liability               # required
contract_types_applicable: [SaaS, MSA]           # required
has_variants: true                               # required ∈ {true}
market_data: "WorldCC 2024: median LoL = 12 個月"  # optional
last_updated: 2026-05-09
owner: kouko
---
```

`_clause.md` body = 共享 metadata + 業務翻譯 + 替代條款 template；不含 walk_away/escalate（那些落到 variant）。

#### 4.1.3 Variant file `<variant-id>.md`

```yaml
---
clause_id: limitation-of-liability               # required (same as _clause.md)
variant_id: mid-deal                             # required, kebab-case
gates:                                           # required, ABAC rule
  deal_size:
    gte: 100000
    lt: 1000000
  counterparty_type: any
walk_away_triggers:
  - "cap < 12 個月服務費"
  - "IP 侵權無 carve-out"
escalate_to: GC
risk_default: yellow
currency: USD
last_updated: 2026-05-09
source_type: user_playbook
---
```

### 4.2 Playbook body convention

```markdown
# <Clause Name in zh-TW>

## 偏好立場
<preferred 立場文字, 1-3 句>

## Fallback 1
<第一退讓階梯文字>

## Fallback 2 (optional)
<第二退讓階梯文字>

## 為什麼這條重要
<業務翻譯, 一句話告訴非法務 why>

## 替代條款文字 (optional)
<可直接 paste 進 redline 的 text>

## 相關判例 (optional)
<judicial 連結 / 學說 reference>
```

### 4.3 Discovery protocol

```
Discovery order (working folder lookup):
  1. <cwd>/legal-playbook/                  # primary
  2. <ancestors>/legal-playbook/            # walk 5 levels up
  3. BFS depth 5 from <cwd>/                # any nested folder
  4. <bundle>/legal-contract-review/assets/baseline-fallback-*.md   # cold-start fallback

Config / schema discovery (parallel):
  1. <cwd>/.legal-toolkit/config.yml
  2. <ancestors>/.legal-toolkit/config.yml
  3. <bundle>/.../assets/config.template.yml   # (Phase 1.5 — copy to user on first use)
```

### 4.4 ABAC gate matching

Phase 1: rule-based interpretation in protocols (no Python yet).
Phase 1.5: `scripts/abac_filter.py` implements:

```python
# Pseudocode (Phase 1.5)
def match_variant(deal_context, entry_variants):
    matches = []
    for variant in entry_variants:
        if all(check_gate(g, deal_context) for g in variant.gates):
            matches.append(variant)
    if len(matches) == 0: return ("advisory", None)
    if len(matches) > 1: log_warning("multi-match"); return ("single", matches[0])
    return ("single", matches[0])

def check_gate(gate, ctx):
    # Numeric: gate.lt / gate.gte / gate.eq → compare ctx[gate.key]
    # Enum:    gate.any_of / gate.eq        → membership
    # Always:  gate == "any"                → True
    ...
```

### 4.5 Output schemas

Six JSON Schema files at `legal-contract-review/assets/output-schema-*.json` constrain LLM structured output:

| File | Required top-level keys (excerpt) |
|---|---|
| `output-schema-issues.json` | `findings: array of {clause_id, source_type, severity, business_issues, playbook_trace, banner?}` |
| `output-schema-redline.json` | `redlines: array of {clause_id, original, proposed, reason, source_type}` |
| `output-schema-memo-legal.json` | `crac: {conclusion, rule, analysis, conclusion_again}, citations: array` |
| `output-schema-memo-business.json` | `summary: {why, what, what_if}` (3 sentences each) |
| `output-schema-escalation.json` | `escalations: array of {clause_id, escalate_to, trigger, deadline?}` |
| `output-schema-self-grade.json` | `answer_score: {n, of}, source_score: {n, of}, failed_criteria: array` |

`source_type ∈ {user_playbook, bundled_fallback, advisory}` 是貫穿 6 份輸出的 traceability 欄位。

### 4.6 End-to-end data flow

```
INPUT (contract path + contract_type + jurisdiction + deal_context + mode + stance)
   │
   ├──[1]── LOAD PLAYBOOK
   │       discover_playbook() → index = scan legal-playbook/ OR bundled fallback
   │       validate_schema()    (Phase 1.5 — best-effort warn)
   │       staleness_check()    (last_updated > 180d → warn)
   │
   ├──[2]── EXTRACT DEAL CONTEXT
   │       parse contract → contract_type / deal_size / counterparty_type / currency
   │
   ├──[3]── [TW only] L0a 強行/任意 → L0b 定型化契約
   │
   ├──[4]── L1 Expectations = bundled ∪ playbook_index keys
   ├──[5]── L2 Anatomy mapping (preamble/definitions/action/endgame/boilerplate)
   ├──[6]── L3 Categorize (Stark 7 concepts + Adams 10 categories)
   ├──[7]── L4 Functional tier (money/risk/control/standards/endgame)
   ├──[8]── L5 Domain priority (bundled[type] + playbook augment)
   ├──[9]── L6 Cycle / cross-ref (loop until gaps==0 AND cycle>=2)
   │
   ├──[10]── [TW only] L6.5 六準則解釋
   │
   └──[11]── L7 Evaluate per clause:
            ├── IDX_LOOKUP: clause.id in user playbook?
            │   ├── yes → FETCH user entry → VTYPE check
            │   └── no  → BUNDLED_LOOKUP: clause.id in fallback?
            │       ├── yes → FETCH bundled + tag source_type=bundled_fallback + banner
            │       └── no  → ADVISORY mode finding (suggest playbook-author extend)
            │
            ├── VTYPE check: flat or variant-folder?
            │   ├── flat → use entry directly
            │   └── variant-folder → ABAC pre-filter → matched variant
            │
            ├── escalate_to placeholder detect:
            │   if escalate_to contains "[請編輯" → emit_warning("uncustomised placeholder")
            │
            └── walk_away_trigger LLM judge (one-shot, Phase 1):
                ├── 🔴 walk → use frontmatter escalate_to (do NOT let LLM rewrite)
                ├── 🟢 preferred / 🟡 fallback / 🔴 worse → LLM body comparison
                └── LLM uncertain → use frontmatter risk_default
   │
   ├──[12]── SELF-GRADE
   │       binary all-pass rubric (Phase 1: protocols-only stub; Phase 1.6: scripts/self_grade.py)
   │       output: answer_score: N/M / source_score: N/M / failed_criteria: array
   │
   └──[13]── WRITE OUTPUTS
            legal-outputs/<timestamp>-<contract-name>/{issues,redline,memo-legal,memo-business,escalation,self-grade}.md
            + Mandatory Disclaimer (every file, footer)
            + Escalation Override (header red banner, conditional)
```

---

## 5. Cold-Start Fallback (CRITICAL chapter)

> 對應 Q-F lock decision in ROADMAP — 沒有自訂 playbook 時 toolkit 仍須運作。

### 5.1 Contract

When `discover_playbook()` returns empty / missing:
- `legal-contract-review` continues normally
- L1 Expectations layer uses `<bundle>/legal-contract-review/assets/baseline-fallback-*.md` as the playbook index
- L7 evaluate reads from bundled fallback for any of the 4 clauses (`confidentiality` / `governing-law-jurisdiction` / `auto-renewal` / `termination-and-survival`)
- Each finding tagged `source_type: bundled_fallback` and stamped with a banner: `⚠️ 使用 bundled fallback baseline — 建議跑 legal-playbook-author 客製化你公司的紅線`

### 5.2 escalate_to placeholder strategy (β scheme)

Bundled fallback entries ship with placeholder:

```yaml
escalate_to: "[請編輯為你公司的角色：法務主管 / GC / 部門主管]"
escalate_to_hint: "通常是 法務主管 / GC / 部門主管 / 老闆兼法務"
owner: "[請編輯為你的姓名]"
```

L7 detect logic:
```
if entry.escalate_to.startswith("[請編輯"):
    emit_warning("escalate_to is uncustomised placeholder; run playbook-author revise")
    add_callout_to_escalation_md(
        "⚠️ 此 finding 使用未客製化的 bundled fallback。"
        "建議：跑 `legal-playbook-author` revise 把 escalate_to 改成"
        "你公司的實際角色（法務主管 / GC / 部門主管 / 老闆）"
    )
    # pipeline does NOT abort — escalation.md still produced, with the warning callout
```

### 5.3 4 條 bundled fallback 內容來源

每條 fallback baseline 內文（preferred / fallback / walk_away / 業務翻譯）的 source attribution：

| Clause | Primary source |
|---|---|
| `confidentiality` | WorldCC 2024 Benchmark + ContractKen Playbooks; carve-out 慣例參考理律 newsletter |
| `governing-law-jurisdiction` | SpotDraft Glossary + 民事訴訟法 §6 國際管轄 |
| `auto-renewal` | WorldCC 2024 + ContractKen + 消保法 §17 定型化契約 |
| `termination-and-survival` | WorldCC 2024 + 民法 §263 + ContractKen survival clause patterns |

每條 baseline frontmatter `source_attribution` 欄位記載；body 末尾「## 為什麼這條重要」段落帶 reference link。

### 5.4 Migration path to user playbook

Cold-start → custom playbook 三條路徑：

1. **Path A** (recommended): `legal-playbook-author bootstrap` → 選 (a) → copy 4 條 fallback to `legal-playbook/` → user edit
2. **Path B** (clean slate): `legal-playbook-author bootstrap` → 選 (b) → 5-question interview → 第一條 entry
3. **Path C** (read-only): 暫不建 `legal-playbook/`，contract-review 持續用 bundled fallback；每次都有 banner 提示

Phase 1.5 upgrade: bundled fallback 從 4 條擴到 8 條（加 LoL / Indemnification / DPA / IP-Assignment variant-folder），Path A 變更豐盛。

### 5.5 Cold-start telemetry (Phase 1.6 future)

不在 MVP，但 schema 預留：
- `seed-history.yml` 記錄第一次 cold-start fallback hit timestamp + 4 條命中率
- 之後 user 跑 `playbook-author` 客製化後寫 `source_type: user_playbook`，可比對「fallback → user customisation conversion rate」

---

## 6. Conventions (cross-skill drift prevention)

### 6.1 Disclaimer block byte-identical

Each of the three MVP skills ships an identical `assets/disclaimer-block.md`. Content drift between the three is a defect. Phase 1-5 enforces by review discipline; Phase 6 adds CI gate.

**Disclaimer block content** (zh-TW, appended to every output footer):

```markdown
---

## ⚠️ 重要聲明（Disclaimer）

本文件由 AI 工具（legal-toolkit skill）產出，**非律師意見**：

- 本工具非律師事務所、亦非執業律師
- 本工具為**免費 open-source 工具**，與使用者無 advisor-client 關係
- 輸出僅供使用者**內部決策參考**，不構成法律意見或律師建議
- 涉及訴訟、刑責、重大商業決策時，**請諮詢執業律師**
- 使用者對採用本工具輸出之決策**自負其責**
- 引用之法條 / 判例 / 函釋請以**全國法規資料庫 / 司法院判決系統 / 主管機關官網**為準

---

工具版本：legal-toolkit v[X.Y.Z]
產出時間：[ISO 8601 timestamp]
Pipeline 路徑：[L0a → L0b → L1 → ... → L7]
Self-grade：answer_score=[X/N] / source_score=[Y/M]
```

`[X.Y.Z]` / timestamp / path / self-grade 由 review skill 動態填入；其餘文字 byte-identical 跨三 skill。

### 6.2 Escalation Override byte-identical

Triggered when **any** of:
- `risk_default: red` in matched entry
- `walk_away_triggered: true` in L7 evaluate
- LLM `confidence < 0.7`
- `always_escalate` rule hit (e.g. 涉及刑責 / 重大訊息揭露 / 賠償上限 > 年營收 10%)
- `deal_size > profile.escalation_threshold` from `.legal-toolkit/config.yml`
- Cross-border + 個資事故 (mandatory)

**Override content** (zh-TW, prepended to output header):

```markdown
# [原本的標題]

> [!danger] ⚠️ 高風險議題——本工具強烈建議諮詢執業律師
>
> 本次 review 偵測到以下高風險訊號：
> - [觸發條件 1]：[簡述]
> - [觸發條件 2]：[簡述]
>
> 本工具的分析**僅供初步參考**。涉及上述議題時：
> 1. **不要**直接採用本工具輸出做最終決定
> 2. **必須**諮詢執業律師（建議：理律 / 寰瀛 / 眾達 / 協合 / 漢威 / 或公司現有外部律師）
> 3. 將本工具輸出作為**律師討論的初稿材料**，加速但不取代律師判斷

---

[原本的內容]
```

Strip rule：`--external-share` flag 即使 strip playbook ID 也 **不 strip** Override（對方 / 第三方更需要看到警告）。

### 6.3 Language directive

每個 SKILL.md 開頭加：

```markdown
## Language Policy

- Skill instructions (this file, protocols/, checklists/): English
- Domain content (legal terms, citations, baseline playbooks): zh-TW (preserve original)
- User-facing output: zh-TW (Traditional Chinese)
- Code (scripts/): English
- Mixed-language is by design — do NOT translate domain terms.
```

LLM 看到 directive 自動分流。

### 6.4 Frontmatter trigger keywords

Skill `frontmatter.description` 必含中英雙語 trigger keywords，覆蓋同一意圖在兩語的常見表述：

```yaml
description: |
  Taiwan in-house legal contract review skill.
  台灣 in-house 法務合約審查 skill。

  ...

  TRIGGER (中英雙語):
  - contract review / redline / NDA review
  - 合約審查 / 合約 review / 合約紅線 / 條款比對
  - 服務合約 / SaaS / MSA / 採購合約 / 勞動契約 / 保密協議

  USE WHEN: User provides a contract file and asks for review,
  redlining, risk analysis, or playbook comparison.
```

---

## 7. Implementation Plan

### 7.1 Phase 1 commit split (CC CI type 白名單)

| Commit | type / scope | scope |
|---|---|---|
| 1 | docs(legal-toolkit) | ROADMAP.md — Done (`a4ba16e`) |
| 2 | feat(legal-toolkit) | Plugin root + marketplace entry + 3-lang README — Done (`a256aef`) |
| 3 | docs(legal-toolkit) | PRODUCT-SPEC.md + TECH-SPEC.md (this commit) |
| 4 | feat(legal-toolkit) | `using-legal-toolkit` scaffold (SKILL.md + README×3) |
| 5 | feat(legal-toolkit) | `legal-playbook-author` scaffold (SKILL.md + protocols×3 + assets×5 + README×3) |
| 6 | feat(legal-toolkit) | `legal-contract-review` scaffold (SKILL.md + protocols×10 + assets×12 + checklists×2 + references×3 + README×3) |

Total Phase 1 = 6 commits / single PR `feat/legal-toolkit-v0.1.0`.

### 7.2 Quality gate (Phase 1 done = mergeable)

- [ ] All 6 commits land on branch
- [ ] `scripts/check-marketplace-description-sync.py` passes
- [ ] `scripts/check-shared-conventions-drift.py` passes
- [ ] `scripts/check-skill-structure.py legal-toolkit` passes
- [ ] `.claude/hooks/validate-skill-folder-structure.sh` not triggered (flat subfolder convention)
- [ ] 5 contract dogfood: contract-review produces 6 outputs + Disclaimer footer + correct Override trigger for high-risk

### 7.3 Phase 1.5 → 6 pickup points

Phase 1.5+ work plugs into the same plugin layout — see [ROADMAP.md](ROADMAP.md) for per-phase deliverable lists. Key extension points:

- `legal-playbook-author/scripts/` (Phase 1.5)
- `legal-contract-review/scripts/` + `assets/baseline-playbooks.tar.gz` (Phase 1.5)
- `legal-contract-review/checklists/*-criteria.md` content (Phase 1.6)
- New skill folders (`legal-document-draft/` ... etc.) under `skills/` (Phase 2-5)

---

## 8. Risks & Workaround Implementation

### 8.1 Skill folder structure hook may block multi-file commits

**Risk**: `validate-skill-folder-structure.sh` triggers on `Write|Edit` in `skills/`; if any sub-subfolder accidentally created (e.g. by IDE auto-formatter, by pytest cache), all subsequent edits in that skill blocked with opaque "violation" message.

**Mitigation**:
- Phase 1 has no `scripts/*.py` → no pytest cache concern
- Phase 1.5+ uses `PYTHONDONTWRITEBYTECODE=1` env var for all pytest invocations (per global memory: `feedback_pycache_hook_blocks_edits.md`)
- Future small `chore(hooks)` PR to whitelist `__pycache__/` in the validator (out of legal-toolkit scope)

### 8.2 Marketplace description drift on multi-PR Phase 2-5

**Risk**: When Phase 2 adds new skill, both `plugin.json` description and `marketplace.json` entry need updating in same commit.

**Mitigation**: `scripts/check-marketplace-description-sync.py` runs in pre-merge CI; described in §1.1.

### 8.3 LLM jumps a step in 7-layer pipeline

**Risk**: With Chinese instructions in protocols, LLM may skip L4 / L5 (functional tier / domain priority). Observed in past dogfood of similar pipelines.

**Mitigation**:
- English骨架 (per §6.3 language directive) measurably reduces step-skipping
- Phase 1 dogfood: track 5 contract runs, flag any layer skipped, iterate SKILL.md / protocols
- Phase 1.6 rubric adds binary check「all 7 layers executed」per run

### 8.4 Cold-start fallback placeholder leaks to final output

**Risk**: User runs contract-review on cold-start, gets `escalation.md` with `escalate_to: [請編輯為你公司的角色]`, treats it as final and forwards to opposing counsel.

**Mitigation** (§5.2):
- L7 placeholder detection emits warning at runtime
- escalation.md auto-prepended with callout urging customisation
- Phase 1.6 rubric binary check: `escalate_to_is_placeholder == false`
- Bundled README + bootstrap mode (Path A) actively prompt user to edit `escalate_to` first

### 8.5 Phase 5 blocker (上市櫃 Compliance prerequisite research)

**Risk**: Phase 5 needs 3-5 GC primary interviews + 70-100hr research bracket; if interviews unobtainable, Phase 5 never ships.

**Mitigation** (ROADMAP §Risk Callouts):
- Use second-tier sources (public disclosures + legal periodicals + GC public talks) as fallback
- Accept confidence LOW for first iteration; refine in v1.x.0 with follow-up interviews

---

## 9. Testing & Verification

### 9.1 Phase 1 dogfood corpus

| File | Contract type | Reason |
|---|---|---|
| `dogfood-nda-en.md` | NDA | Simplest structure; tests `nda` mode + L4-L7 fast path |
| `dogfood-saas-msa-tw.md` | SaaS MSA | Mainstream; tests all 7 layers + LoL fallback (advisory mode since no LoL in fallback baseline) |
| `dogfood-procurement-tw.md` | 採購合約 | 民法 §247-1 定型化契約檢查（L0b） |
| `dogfood-labour-tw.md` | 勞動契約 | 勞基法 §9-1 競業條款；advisory mode（no labour entry in fallback） |
| `dogfood-dpa-gdpr-overlay.md` | DPA + GDPR overlay | Cross-border; tests escalation override 跨境 + 個資 trigger |

Dogfood corpus 不 ship 進 plugin（敏感 content 風險）；保留 `docs/dogfood-corpus/` (Phase 1.6+) 給 owner only。Phase 1 dogfood 結果手寫進 commit message 即可。

### 9.2 Self-test checklist (manual, before merging Phase 1 PR)

- [ ] `/plugin install legal-toolkit@monkey-skills` 成功
- [ ] `/using-legal-toolkit` 出現在 skill list
- [ ] `/legal-contract-review` 可呼叫；對 5 份 dogfood contract 都產出 6 份檔案
- [ ] 高風險 finding 100% 觸發 Override 紅字
- [ ] 每份輸出檔尾含 Disclaimer
- [ ] Cold-start：直接跑 review (無 `legal-playbook/`) → 4 條 fallback 命中時 banner 出現
- [ ] `/legal-playbook-author` bootstrap → 三選一 menu 出現
- [ ] disclaimer-block.md / escalation-override.md 在 3 個 skill 內 `diff` 為 zero

---

## 10. References

- **PRODUCT-SPEC (companion)**: [`PRODUCT-SPEC.md`](PRODUCT-SPEC.md)
- **ROADMAP**: [`ROADMAP.md`](ROADMAP.md)
- **Design note (SoT)**: `<obsidian-vault>/research/2026-05-09 法務 Agent Skill (legal-toolkit) 整體架構與執行流程設計.md`
- **monkey-skills convention**: `monkey-skills/CLAUDE.md`
- **CI scripts**: `monkey-skills/scripts/check-{marketplace-description-sync,skill-structure,shared-conventions-drift}.py`
- **Folder structure hook**: `monkey-skills/.claude/hooks/validate-skill-folder-structure.sh`
