# legal-toolkit SP3a — `legal-document-draft` v0.4.0 design

**Status**: Design (implementation-ready pending user review)
**Date**: 2026-05-13
**Authors**: kouko + Claude (brainstorming session, Q2–Q9)
**Predecessor**: legal-toolkit v0.3.6 (SP1 PR #272 — canonical/ SoT plumbing), legal-toolkit SP2 PR #273 (PDPA 2025/11 verify — research note + canonical metadata refresh)
**Target version**: legal-toolkit v0.4.0
**Sub-project**: SP3a of legal-toolkit Phase 2 program. Sibling SP3b ships `legal-incident-response` as v0.4.1.
**Skill scope**: 1 new skill `legal-document-draft`; updates to `using-legal-toolkit` router

---

## 1. Goal

Ship `legal-document-draft`, a new in-house legal toolkit skill that **drafts new legal documents** (privacy policy / ToS / DPA / NDA) from a user's company profile + negotiation playbook + per-session inputs. Templates are pinned to **current in-force Taiwan law** (Path A); items deferred by SP2's PDPA verify run (PDPC sub-regulations, 通報門檻, 72hr timer, etc.) are handled via safe defaults in the published document and a separate TBD migration tracker in the compliance audit file.

This unblocks the user's headline request — "幫使用者寫合約 / 法律文件的 skill" — and ships in `v0.4.0` ahead of SP3b (incident-response, reframed away from the obsidian SoT's 72hr-timer-centric design).

## 2. Why

**Trigger** — the existing `legal-contract-review` and `legal-playbook-author` skills cover *reviewing other parties' drafts* + *writing the company's negotiation stance*. Neither **drafts the company's own legal documents**. Phase 2 fills this gap, alongside `legal-incident-response` (SP3b, v0.4.1).

**Why ship-against-current-law (Path A from SP2)** —

- SP2's verify run (research note `legal-toolkit/research/2026-05-12-pdpa-2025-11-verify.md`) found that 5 obsidian-SoT-design pillars were GDPR contamination or rested on未生效 amendments:
  1. 72hr breach notification (Taiwan: "即時", per 施行細則 §22)
  2. PDPC notification form/URL (PDPC is still 籌備處)
  3. 2025/11 PDPA amendments (promulgated 2025-11-11; 施行日期：未定)
  4. Minor protection age threshold (no PDPA provision; 民法 §12-13 applies)
  5. Controller / processor split (Taiwan: 委託/受託 model, §4 + §8)
- Shipping against the future (Path B) would require hardcoding amendments not yet in force.
- Shipping dual-mode (Path C) doubles work without proportional return for Taiwan-domestic SME users.
- Deferring Phase 2 entirely (Path D) blocks the user's drafting use case indefinitely.

**Why bundled all 4 modes** — privacy / ToS / DPA / NDA all have well-defined Taiwan-law foundations (個資法 §8 / 民法 + 消保法 / 個資法 §4 + §8 / 民法 + 商業慣例). All can ship safely under Path A. The marginal cost of adding NDA + DPA to a privacy-only MVP is small once the multi-mode dispatch architecture exists.

**Why skeleton + LLM fill** —

- Legal templates are partially mandatory (個資告知事項 §8 enumerable items / NDA 必載) and partially open (company-specific stances).
- Skeleton-with-`{{variables}}` makes the mandatory portion **reliable and reviewable** (you can read `assets/template-privacy.md` and predict every output's structure).
- LLM-fill handles the variable portion (variable selection, copywriting tone, optional sections).
- Pure-LLM generation risks omission of mandatory items; pure-template approach is brittle for variable content.

## 3. Locked decisions

| # | Decision | Choice | Reasoning |
|---|---|---|---|
| 1 | Direction | Path A (current Taiwan law) | SP2 verify findings; legally accurate today; zero fabrication |
| 2 | Modes | 4 modes: privacy / tos / dpa / nda | All have verified statutory basis; bundled for unified architecture |
| 3 | Authoring approach | Skeleton + LLM fill | Reliable mandatory portion + flexible variable portion |
| 4 | Output | 2 files per session: `<doc-type>.md` (publish-ready) + `compliance.md` (法務 review), in `legal-outputs/<timestamp>-<doc-type>/` | Audience-shaped pattern (mirrors `legal-contract-review` v0.3.4 — `legal.md` + `business.md`) |
| 5 | Playbook integration | Variable defaults from playbook (skeleton structure unchanged; playbook supplies stance defaults; session can override) | Reuses playbook investment; doesn't conflict with skeleton authority |
| 6 | Profile location | `legal-playbook/profile.yml` (visible + git-tracked) | Company info is shared asset; lives with playbook not in hidden `.legal-toolkit/` |
| 7 | Citation URLs | Hardcode in templates | URL pattern stable; avoids extending canonical/ pattern; consistent with Q3 decision |
| 8 | TBD strategy | Safe defaults in `<doc-type>.md`; TBD migration tracking in `compliance.md` | Document is publish-ready; compliance is audit + upgrade path |
| 9a | Compliance checklist | Heavy hand-curated per mode (privacy 15-20 / dpa 8-12 / nda 6-8 / tos 10-15 items, each with statute citation) | Aligned with `legal-contract-review` v0.3.0 rubric pattern |
| 9b | Self-grade | Deterministic structural checks (variables filled / no orphan placeholder / checklist has verdicts) | MVP sufficient; defer Pearson-calibrated LLM rubric to v0.4.0.1+ post-dogfood |

## 4. Architecture overview

```
USER intent ("我要起草 privacy policy")
    │
    v
using-legal-toolkit (router)
    │ — Q2 dispatch path (active)
    v
legal-document-draft (NEW; this PR)
    │
    │ inputs:
    │  - mode flag (privacy / tos / dpa / nda)
    │  - legal-playbook/profile.yml (公司基本資料)
    │  - legal-playbook/<clause>.md per-mode (stance defaults)
    │  - session vars (產品名 / 個資類別 / SDK 清單 / etc.)
    │
    │ pipeline:
    │  load_profile → select_template → scan_playbook
    │      → ask_gaps → merge → comply_check → self_grade → output
    │
    │ outputs (to legal-outputs/<timestamp>-<mode>/):
    │  - <doc-type>.md         publish-ready, safe defaults inline
    │  - compliance.md         hand-curated checklist with verdicts + TBD migration list
    v
USER reviews, publishes
```

## 5. File layout

Per `monkey-skills/CLAUDE.md` Skill Structure rule (flat subfolders only, no nesting):

```
legal-toolkit/skills/legal-document-draft/
├── SKILL.md
├── README.md
├── README.ja.md            # tri-language per PR #150 convention
├── README.zh-TW.md
├── assets/
│   ├── template-privacy.md  # 個資告知事項 §8 八款 + §9 特種個資 + §21 跨境 + §6 限制
│   ├── template-tos.md      # 民法 + 消保法 §11-1 + §17 定型化 + 公平交易法
│   ├── template-dpa.md      # 個資法 §4 + §8 委託處理 + 施行細則 §12 受託人義務
│   ├── template-nda.md      # 民法 + 商業慣例 + 救濟條款
│   ├── profile-schema.yml   # legal-playbook/profile.yml schema (reference)
│   └── output-schema.json   # legal-outputs/<timestamp>-<mode>/ output structure
├── checklists/
│   ├── compliance-privacy.md  # 15-20 hand-curated items, each cite 個資法 statute
│   ├── compliance-tos.md      # 10-15 items
│   ├── compliance-dpa.md      # 8-12 items
│   └── compliance-nda.md      # 6-8 items
├── protocols/
│   ├── draft.md             # main protocol (DAG below)
│   └── grade.md             # deterministic structural self-grade steps
├── scripts/
│   ├── grade_draft.py       # CLI: scans legal-outputs/<run>/ + verifies completeness
│   └── load_profile.py      # CLI: reads legal-playbook/profile.yml + applies schema validation
└── references/
    ├── pdpa-current-state.md  # summary of SP2 research note (offline-readable ground truth)
    ├── tbd-migration-template.md   # "when PDPC sub-regs land, do these edits" guide
    └── statute-citations.md   # central index of all hardcoded URLs used across templates
```

**Tests live at plugin level** (not in `legal-document-draft/tests/`), following the established legal-toolkit + translation-toolkit precedent. Skill folders stay flat (SKILL.md + single-level subfolders only; no `tests/` inside the skill):

```
legal-toolkit/tests/                          ← existing 171-test suite; SP3a appends here
├── test_grade_draft.py                       ← NEW; deterministic structural checks
├── test_load_profile.py                      ← NEW; profile schema validation
└── fixtures-document-draft/                  ← NEW; flat-named to avoid nested subfolder
    ├── profile-minimal.yml
    ├── profile-full.yml
    └── draft-output-sample/                  ← (acceptable: fixtures-document-draft is plugin-level
                                              ←  tests/ subfolder; nesting under it follows the
                                              ←  translation-toolkit/scripts/tests/fixtures/
                                              ←  sample-book-ja/ precedent that the validator hook
                                              ←  has not flagged historically)
```

If the validator hook unexpectedly flags `fixtures-document-draft/draft-output-sample/`, fall back to fully flat fixture naming (single-file fixtures or path-encoded directories).

## 6. Per-mode template + variable schema

### 6.1 privacy mode

**Template** (`assets/template-privacy.md`):

Sections (in order):
1. 公司基本資料 (from profile.yml — name, contact, DPO)
2. 蒐集個資類別 (個資法 §8 第一項第三款 — `{{collected_categories}}`)
3. 蒐集目的 (§8 第一項第二款 — `{{collection_purposes}}`)
4. 個資利用範圍 (§5 — `{{usage_scope}}`)
5. 第三方 SDK 揭露 (`{{third_party_sdks}}` — 自填 list with default examples)
6. 跨境傳輸 (§21 — `{{cross_border_destinations}}` from profile; safe default = empty list)
7. 當事人權利 (§3 — 查詢 / 更正 / 刪除 / 停止處理 / 異議 / 退出 — boilerplate)
8. 個資保管期間 (§5 + §11 — `{{retention_period}}`)
9. 安全維護措施 (§27 + §20-1 [not-yet-effective, marked TBD] — `{{security_measures}}` from profile)
10. 個資外洩通報 (施行細則 §22 — **safe default: "本公司將依個資法相關規定即時通報主管機關"**; TBD migration: when PDPC §12 §4 子法 published, update to specific timeframe + threshold + URL)
11. 隱私權政策修訂與生效 (`{{effective_date}}`)
12. 聯絡方式 (from profile.yml DPO)

**Variables**:

```yaml
# Required (must be in profile.yml OR session ask_gaps)
company_name: str
company_contact: str  # email/phone
dpo_contact: str      # data protection officer email
effective_date: date

# Required from session (ask_gaps)
collected_categories: list[str]  # 個資類別 names
collection_purposes: list[str]
usage_scope: enum[domestic, cross_border_limited, cross_border_unrestricted]
third_party_sdks: list[dict]  # [{name, purpose, transferred_categories}]
retention_period: str
security_measures: list[str]  # mappable to common categories

# Optional (defaults provided)
cross_border_destinations: list[str]  # from profile.yml; default []
minor_data_handling: enum[none, parental_consent_required]  # references 民法 §12-13 not PDPA
```

### 6.2 tos mode

Sections: 服務範圍 → 使用者註冊 → 費用 → 智慧財產 → 使用者義務 → 終止 → 限制責任 (消保法 §11-1 等候期 + §17 定型化檢視) → 救濟與管轄 → 修改 → 公平交易法 注意 → 附則

### 6.3 dpa mode

Sections: 委託處理範圍 (§4 受託) → 受託人義務 (§8 + 施行細則 §12) → 子委託 (§4 第二項) → 安全維護 (§27) → 個資外洩通知 (受託 → 委託；safe default "即時") → 終止後處理 → 監督 audit 權 → 責任分配 (委託 bears 全責 per §4 解釋)

### 6.4 nda mode

Sections: 定義 (機密資訊 + 揭露方/接受方) → 義務 → 例外 (carve-outs) → 期間 (`{{survival_years}}` default 3, from playbook if specified) → 違約救濟 (民法 §227 + §250 違約金) → 管轄 → 附則

**Variable schemas for tos / dpa / nda** are detailed in template comments at implementation time. The pattern above (privacy mode) demonstrates the structure each mode follows: skeleton sections + statute citations + variable list + safe defaults.

## 7. `legal-playbook/profile.yml` schema

```yaml
# legal-playbook/profile.yml
# Company profile shared across legal-toolkit skills (draft, IR, future corp-governance, dd-quickscan).
# Schema version: 1
schema_version: 1

# Required identity
company_name: "<official 公司名稱>"
company_name_en: "<English name>"
company_id: "<統一編號>"
registered_address: "<註冊地址>"

# Required contacts
general_contact:
  email: "<contact@example.com>"
  phone: "<+886-2-XXXX-XXXX>"

dpo:                       # data protection officer (個資法 §22 推定承辦人)
  name: "<姓名>"
  email: "<dpo@example.com>"

# Optional — defaults applied if absent
business_scope:
  - "<業務領域 1>"
  - "<業務領域 2>"

cross_border_destinations: # countries you transfer personal data to
  - country: "US"
    purpose: "雲端服務 (AWS)"
  - country: "JP"
    purpose: "客服外包"

security_measures:         # standard set referenced by privacy + dpa templates
  - "TLS 1.3 encryption in transit"
  - "AES-256 encryption at rest"
  - "Annual ISO 27001 audit"

governing_law:
  default_jurisdiction: "中華民國"
  preferred_court: "臺灣臺北地方法院"

# Optional — version control
last_updated: "2026-05-13"
maintained_by: "<法務 / 業務 owner>"
```

`assets/profile-schema.yml` (in the skill) declares the JSON Schema for validation; `scripts/load_profile.py` validates and reports missing required fields.

## 8. Protocol DAG (`protocols/draft.md`)

```
START (user invokes via router with mode=<privacy|tos|dpa|nda>)
  │
  v
LOAD_PROFILE
  - read legal-playbook/profile.yml
  - validate against assets/profile-schema.yml
  - if missing required fields → error with explicit "fix profile.yml first"
  │
  v
SELECT_TEMPLATE
  - load assets/template-<mode>.md
  │
  v
SCAN_PLAYBOOK
  - for each variable that has a corresponding playbook clause, read default:
    - nda survival_years → legal-playbook/confidentiality.md `survival_period` stance
    - dpa retention_period → legal-playbook/data-protection-dpa.md `retention` stance
    - tos jurisdiction → legal-playbook/governing-law-jurisdiction.md `preferred_court` stance
  │
  v
ASK_GAPS
  - identify variables not satisfied by profile + playbook
  - prompt user for each in a single interactive batch
  - user can override profile / playbook defaults per session
  │
  v
MERGE
  - resolve final variable values (precedence: session > playbook > profile > template default)
  - apply safe defaults for TBD variables (e.g., breach notification timeframe)
  - LLM fills template skeleton with values + selects optional sections
  │
  v
COMPLY_CHECK
  - load checklists/compliance-<mode>.md
  - for each item, LLM evaluates the draft and emits verdict (PASS / FAIL / TBD_<reason>)
  - TBD verdicts flow into the migration section of compliance.md
  │
  v
SELF_GRADE
  - call scripts/grade_draft.py with the output directory
  - script checks:
    1. all template variables resolved (no `{{...}}` orphan left)
    2. all checklist items have verdicts
    3. TBD items match the canonical OPEN list (no fabricated TBDs)
    4. document.md byte-count > minimum threshold (catches truncated runs)
  - failure exits with explicit error; user re-runs after fixing
  │
  v
OUTPUT
  - write legal-outputs/<timestamp>-<mode>/<doc-type>.md
  - write legal-outputs/<timestamp>-<mode>/compliance.md
  - print summary: path + verdict counts + TBD count
```

## 9. Compliance checklist structure (per-mode example)

`checklists/compliance-privacy.md` (excerpt):

```markdown
# Privacy policy compliance checklist (個資法 §8 八款)

> Each item is verified by the LLM during the COMPLY_CHECK step. Verdict
> options: PASS / FAIL / TBD_<reason>. TBD verdicts MUST cite an entry from
> the SP2 verify research note's OPEN list (see references/pdpa-current-state.md).

- [ ] §8 第一項第一款 — 公開揭露蒐集者 (公司) 名稱 (法源：個資法 §8 第一項第一款，https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=8)
- [ ] §8 第一項第二款 — 公開揭露蒐集目的
- [ ] §8 第一項第三款 — 公開揭露個資類別
- [ ] §8 第一項第四款 — 公開揭露利用期間 / 地區 / 對象 / 方式
- [ ] §8 第一項第五款 — 公開揭露當事人權利 (查詢/更正/刪除/停止處理/異議)
- [ ] §8 第一項第六款 — 公開揭露當事人不提供之影響
- [ ] §9 — 若蒐集特種個資 (§6 一項一至五款)，書面同意機制是否明示？
- [ ] §21 — 若涉跨境傳輸，是否揭露目的地 + 是否符合主管機關公告之限制？
- [ ] 施行細則 §22 — 個資外洩通報語句是否使用「即時」（避免 hardcode 72hr GDPR 觀念）
- [ ] §27 — 安全維護措施是否載明？
- [ ] §20-1 (TBD — 施行日期未定，視為 TBD_PDPC_pending) — 預留 audit framework 段落？
- ...
```

Each verdict in the protocol's COMPLY_CHECK output becomes a line in `compliance.md` after substitution.

## 10. TBD migration tracking

`references/tbd-migration-template.md` declares the standard upgrade-path for each TBD item:

```markdown
# TBD migration template

When PDPC sub-regulations are published, follow this guide to patch templates.

## TBD_1 — 個資外洩通報具體時限 (個資法 §12 §4 子法)

**Current safe default in templates**: "依個資法相關規定即時通報主管機關"

**Trigger to update**: Monitor https://www.pdpc.gov.tw for "通報辦法" announcement
or 行政院公告 of Art. 12 effective date.

**Patch action**:
1. Edit `assets/template-privacy.md` Section 10 — replace "即時" with specific timeframe (e.g., "於發現後 X 小時內")
2. Edit `assets/template-dpa.md` 個資外洩通知 section — same change
3. Edit `checklists/compliance-privacy.md` §22 item — update PASS criteria
4. Bump `legal-playbook/profile.yml` cross-border block if PDPC announces new restrictions
5. Re-run draft for all in-use documents
6. Phase 2.5 patch commit with notes referencing PDPC announcement URL
```

(items TBD_2 through TBD_7 follow same structure)

`compliance.md` for each draft session reproduces only the TBDs that apply to that session's mode, with the migration template's content inlined.

## 11. Cross-skill relations

### 11.1 Router (`using-legal-toolkit`)

`legal-toolkit/skills/using-legal-toolkit/SKILL.md` Q2 dispatch path:

- Q2 keyword set: "起草" / "draft" / "寫一份" / "privacy policy" / "ToS" / "DPA" / "NDA" / "服務條款" / "委託處理協議" / "保密協議"
- Hands off to `legal-document-draft` with `mode` extracted from keywords (privacy / tos / dpa / nda)
- If mode ambiguous → router asks user explicitly

### 11.2 `legal-contract-review` NDA collision

| Skill | Function | Input | Output |
|---|---|---|---|
| `legal-contract-review nda` | Review **existing** NDA (counterparty's draft) | Counterparty NDA text + playbook | Redline + memo |
| `legal-document-draft nda` | Generate **new** NDA from scratch | Profile + playbook + session vars | `nda.md` + `compliance.md` |

Both skills **share `legal-playbook/confidentiality.md`** as the canonical stance source. Draft uses stance values as variable defaults; review uses stances as the comparison baseline.

### 11.3 Profile.yml ownership

`profile.yml` is **created and edited by the user**. Skills only READ it. If skills detect missing required fields, they emit an error pointing the user to edit profile.yml (don't auto-create / auto-update from skill side — single source of truth = user).

### 11.4 `legal-sources.json` consumption

Draft reads `legal-toolkit/skills/legal-contract-review/assets/legal-sources.json` (the functional copy materialized by SP1's `distribute.py`) **only at template authoring time**, NOT at runtime. Specifically: the author of `assets/template-*.md` reads `statute_sources.<statute>.single_article_url_template` to construct hardcoded URLs.

Runtime: templates contain literal URL strings; no `legal-sources.json` lookups.

This keeps SP3a self-contained and does NOT extend the canonical/ pattern.

## 12. Test plan

### 12.1 Unit tests (pytest, plugin-level `legal-toolkit/tests/`)

- `legal-toolkit/tests/test_load_profile.py`:
  - T-P-1: minimal valid profile.yml loads correctly
  - T-P-2: full profile.yml loads correctly
  - T-P-3: missing required field (e.g., dpo.email) raises validation error with explicit message
  - T-P-4: schema_version mismatch handled
- `legal-toolkit/tests/test_grade_draft.py`:
  - T-G-1: complete draft output passes structural checks
  - T-G-2: unresolved `{{variable}}` in output → grade FAIL
  - T-G-3: compliance.md missing verdict on a checklist item → grade FAIL
  - T-G-4: TBD verdict not matching canonical OPEN list → grade FAIL with "fabricated TBD" message
  - T-G-5: document.md byte-count below threshold → grade FAIL with "possible truncation"
  - T-G-6: optional sections correctly omitted when not applicable

Tests read fixtures from `legal-toolkit/tests/fixtures-document-draft/`.

### 12.2 Integration / smoke

For each mode, generate a dogfood-quality draft using a synthetic `profile.yml`:
- Privacy: SaaS company, US + JP cross-border, 3 SDKs (Google Analytics / Sentry / Stripe), 個資保管 5 年
- ToS: B2C SaaS, 月訂閱模式, 中華民國管轄
- DPA: cloud processor relationship, 個資保管 90 天 post-termination, sub-processor allowed with approval
- NDA: bilateral, 5-year survival, USDM-style carve-outs

Each smoke run must produce passing compliance.md and structural grade.

### 12.3 CI integration

`.github/workflows/legal-toolkit-ci.yml` already runs `pytest legal-toolkit/tests/` + `pytest legal-toolkit/scripts/tests/`. SP3a's new tests live in `legal-toolkit/tests/` (the existing 171-test suite location), so the workflow does NOT need new pytest invocations — the existing `pytest legal-toolkit/tests/ -v` step picks up `test_grade_draft.py` + `test_load_profile.py` automatically.

Expected post-SP3a test count: 171 + 13 (SP1) + 10 (SP3a — 4 T-P + 6 T-G) = ~194 total.

## 13. Out of scope (explicitly deferred)

| Item | Why deferred | Lands in |
|---|---|---|
| `legal-incident-response` skill | SP3b sub-project | v0.4.1 |
| Heavy LLM-rubric scoring (Pearson calibrated like contract-review v0.3.0) | MVP doesn't have dogfood baselines for calibration | v0.4.0.1+ after 5-10 dogfood drafts hand-graded |
| 5th mode (e.g., 員工合約 / 服務契約 / 採購合約 / SLA) | YAGNI | Future Phase 2.X based on user feedback |
| Multi-company profile / inheritance schema | YAGNI | profile-schema.yml v2 when multi-entity user emerges |
| Runtime citation URL fetch via canonical/ extension | Templates pin URLs at authoring time; runtime not needed | Never (unless URL format breaks) |
| Draft template diff / version control across sessions | YAGNI | Future contract-tracker hooks (Phase 4) |
| GDPR-style draft mode (separate template set) | Path A excludes this scope | If real EU exporter user appears, Phase 2.X considers |
| Auto-monitor PDPC for sub-regulation publication | Manual monitoring sufficient at low publication frequency | regulation-watch skill (Phase 4) |
| `<doc-type>.md` HTML / PDF export | User can convert manually (pandoc) | YAGNI |
| Privacy policy revision diff vs prior version | YAGNI | Phase 4 contract-tracker integration |

## 14. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `profile.yml` schema over- or under-spec | MED | MED | Start from SP2 verified fields; YAGNI for nice-to-haves; user can extend |
| 4 mode hand-curated checklist 工程量低估 | MED | MED | Privacy + DPA prioritized (legally rigorous); NDA + ToS lighter (business custom-driven) |
| Skeleton paradigm too rigid for edge cases | LOW | LOW | LLM-fill provides flexibility within skeleton; playbook override safety valve |
| 個資法 2025/11 amendments suddenly become effective mid-PR | LOW | HIGH | TBD migration template ready; patch path documented; canonical/legal-sources.json already has amendment metadata from SP2 |
| Playbook clause missing → variable default unfilled silently | LOW | MED | LOAD_PROFILE + ASK_GAPS step catches missing variables explicitly; grade_draft.py double-checks |
| NDA mode collision confusion between draft + review | LOW | LOW | Router routes to draft on "起草/寫" keywords, review on "審/check/redline" — keyword separation tight |
| `legal-sources.json` URL format changes (very rare) | LOW | LOW | Hardcoded URLs in templates → grep-replace patches; one-time migration |

## 15. References

- **Predecessor PRs**:
  - PR #272 (SP1 v0.3.6 — canonical/ SoT plumbing)
  - PR #273 (SP2 — PDPA 2025/11 verify run)
- **Brainstorming session**: this conversation (Q2–Q9 sequence)
- **Path A rationale**: SP2 research note `legal-toolkit/research/2026-05-12-pdpa-2025-11-verify.md` (pending merge of PR #273 into main)
- **Obsidian SoT (original design, partly invalidated by SP2)**: vault `research/2026-05-09 法務 Agent Skill (legal-toolkit) 整體架構與執行流程設計.md` §3.4
- **Convention**: `monkey-skills/CLAUDE.md` Skill Structure (flat subfolders, plugin-level scripts/ permitted)
- **Cross-skill data**: `legal-toolkit/scripts/canonical/legal-sources.json` (SoT) → `legal-toolkit/skills/legal-contract-review/assets/legal-sources.json` (functional copy that draft reads at authoring time)
- **NDA stance source (shared with review)**: `legal-playbook/confidentiality.md`
- **Existing rubric pattern for inspiration**: `legal-toolkit/skills/legal-contract-review/protocols/L7-evaluate.md` (deterministic 22-criterion rubric)

## 16. Estimate

- 1 day — design spec (this doc) + implementation plan
- 4-5 days — implementation (sequential):
  - Day 1: skeleton scaffolding + profile-schema + load_profile.py + grade_draft.py + tests
  - Day 2: privacy mode (template + checklist + smoke)
  - Day 3: dpa + nda modes
  - Day 4: tos mode + integration smoke across all 4
  - Day 5: dogfood polish + router update + tri-language README
- Compressible to ~3 days with subagent-driven parallel (4 worktrees, one per mode, after Day 1 scaffolding lands)
- 1 day — review iteration + CI green

Total: 5-7 days. Single PR `v0.4.0`.

## 17. Open questions (to resolve during plan or implementation)

1. **Compliance checklist size per mode** — current estimates (privacy 15-20 / dpa 8-12 / nda 6-8 / tos 10-15) are based on quick reads of statute scope. Authoring may discover more / fewer items; the spec budgets the upper end.
2. **Profile.yml `business_scope` semantics** — should this be free-text or controlled vocabulary? Defer to plan; default free-text.
3. **`scripts/grade_draft.py` `--strict` vs `--lenient` mode** — should the CLI have a lenient flag that downgrades FAIL to WARN (for ongoing-draft iteration)? Defer to plan.
4. **`tests/fixtures/` subfolder** — if `validate-skill-folder-structure.sh` rejects it, fall back to flat-naming. Decide at implementation time after running the hook.
5. **Migration of obsidian SoT §3.4 design notes** — should the old (invalidated) sections of the SoT be amended or marked-as-superseded? Out of scope for SP3a; obsidian housekeeping.
