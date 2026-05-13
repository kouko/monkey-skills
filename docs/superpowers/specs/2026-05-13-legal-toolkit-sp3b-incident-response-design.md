# legal-toolkit SP3b — `legal-incident-response` v0.4.2 design

**Status**: Design (implementation-ready)
**Date**: 2026-05-13
**Authors**: kouko + Claude (brainstorming session, Q1–Q11)
**Predecessor**: legal-toolkit v0.4.1 (SP3a dogfood patches PR #279), v0.4.0 (SP3a PR #277), v0.3.6 (SP1 PR #272), SP2 PR #273
**Target version**: legal-toolkit v0.4.2
**Sub-project**: SP3b — Phase 2 closeout of `legal-toolkit` ROADMAP
**Skill scope**: 1 new skill `legal-incident-response`; 2 new canonical/ files (extending SP1 SSOT plumbing); 1 router patch (Q5 dispatch active); SP3a `profile-schema.yml` v1 → v2 via canonical/

---

## 1. Goal

Ship `legal-incident-response`, a 3-path classifier skill for Taiwan in-house 法務 dealing with **post-event response** (incident occurred / 主管機關來函 / 對方違約). Pinned to current-Taiwan-law (Path A from SP2 verify run); items deferred by SP2 (PDPC 通報門檻 / 時限 / URL / 籌備處狀態) handled via TBD canonical id strategy mirroring SP3a.

This closes Phase 2 of `legal-toolkit` ROADMAP (SP3a `legal-document-draft` + SP3b `legal-incident-response` = 累計 5 skills active).

## 2. Why

**Trigger** — obsidian SoT §3.5 designed `legal-incident-response` with 72hr GDPR-style timer at its center. SP2 PR #273 verify run found 72hr is GDPR Art. 33, not Taiwan PDPA (which uses「即時」per 施行細則 §22). The original design was contaminated by GDPR. SP3b reframes:

| obsidian SoT §3.5 original | SP3b v0.4.2 actual | Why (sourced) |
|---|---|---|
| 72hr 倒數計時器 | ISO 8601 時間軸 (no 72hr) | SP2 research note line 80-85: `施行細則 §22 = "即時"`; 2025/11 amendment Art. 12 §4 defers timeframe to PDPC sub-reg (未發) |
| Hard-coded PDPC notification URL | TBD_PDPC_notification_url canonical id | SP2: PDPC operating as 籌備處; URL unverified |
| Hard-coded 通報範圍 (X persons) | TBD_PDPC_threshold canonical id | SP2: Art. 12 §2「一定通報範圍」wholly undefined |
| 3 path 平等對待 (PII / 函覆 / 違約) | 違約 path → delegate to `legal-contract-review` | YAGNI: 違約 path = post-execution remedy analysis ≠ document-gen; overlaps with existing contract-review skill scope |
| 當事人通知文 多語版本 | zh-TW only; i18n via `translation-toolkit` plugin | YAGNI: MVP收斂; multi-language is `translation-toolkit` territory |

**Why bundle 3 paths into single skill** (Q1) — preserve obsidian SoT's "incident response is one routing entry point" mental model; user enters with raw incident description, skill auto-classifies (Q3). Splitting into 3 skills duplicates router-dispatch + classifier logic.

**Why audience-shaped 2-file output** (Q2) — mirror SP3a v0.4.0 + `legal-contract-review` v0.3.4. `legal.md` for 法務 audience (full incident record + 通報文 + 時間軸 + compliance); `business.md` for CEO/BD (Top 3 + 對外溝通 + deadline). User mental model consistent across plugin.

**Why TBD body strictly aligned to current law** (Q6) — 個資外洩通報文 is a legal document sent to 主管機關. Mixing SOP-suggested numbers (e.g., "24 hours") into body = misrepresentation risk; cleaner to keep body 100% statute-aligned (即時) and route SOP numbers to compliance.md.

**Why Mixed per-path authoring** (Q4) — 3 paths have very different template-ability:
- PII-breach: HIGH (PDPC 通報文 + 當事人通知文 + 內部記錄 have standard structure) → skeleton + LLM fill (mirror SP3a)
- Authority-letter: LOW (incoming letter content varies wildly per regulator + per matter) → pure-LLM protocol
- Contract-breach: delegate to `legal-contract-review` (existing skill owns post-execution clause extraction + remedy analysis)

## 3. Locked decisions

| # | Decision | Choice | Reasoning |
|---|---|---|---|
| 1 | Scope unification | Single skill, 3-path classifier | Preserve obsidian SoT architecture; router dispatch logic shared |
| 2 | Output | 2-file audience-shaped (`legal.md` + `business.md`), always 2 files | Mirror SP3a v0.4.0 + contract-review v0.3.4 |
| 3 | Path routing | Auto-classify + confirm (transparent `inferred_type` + `confidence` + `signals[]`) | Incident user wants "what do I do" not "which mode"; classifier signals make decision auditable |
| 4 | Authoring per-path | Mixed: PII-breach skeleton+LLM; Authority-letter pure-LLM; Contract-breach delegate | Template-ability differs; force-fit one approach degrades quality |
| 5 | Timeline | ISO 8601 datetime table; `⏳ 待 X` for unrealized anchors | Audit-ready format; relative T+offset derivable; no fake numbers for unknown times |
| 6 | TBD body | Body strictly aligned to current law (即時); SOP numbers (24hr / 1000筆) only in compliance.md | 通報文 is legal document; SOP-as-body = misrepresentation risk |
| 7 | profile.yml | +2 optional fields: `external_counsel` (object) + `regulatory_authorities` (array) | High reuse cross 3 paths; profile.yml schema v1 → v2 via canonical/ SSOT |
| 8 | Cross-skill | Contract-breach path = thin classifier + handoff JSON to `legal-contract-review`; v0.4.2 ships handoff schema, contract-review consumption is v0.4.3+ enhancement | YAGNI: contract-review owns deep analysis; no scope creep into v0.4.2 |
| 9 | Grader | Single `grade_response.py` per-path branch | Mirror SP3a `grade_draft.py` pattern; per-path checks share helpers |
| 10 | Playbook clauses | NONE in v0.4.2; defer to v0.4.3 dogfood-driven | YAGNI: no real signal yet that stance defaults reuse cross-session; profile.yml +2 fields already covers external counsel + regulators |
| 11 | Language | zh-TW only | MVP; i18n delegated to `translation-toolkit` plugin |
| 12 | SSOT files | `pdpa-current-state.md` + `tbd-migration-template.md` + `profile-schema.yml` moved to `legal-toolkit/scripts/canonical/`; distribute.py syncs to SP3a + SP3b `references/` and `assets/` | Extends SP1 plumbing; prevents drift between sibling skills |

## 4. Architecture overview

```
USER intent ("剛發現用戶資料異常存取 8000 筆…" / "金管會來函要 7 日內回覆…" / "對方違約沒付款 60 天")
    │
    v
using-legal-toolkit (router; Q5 dispatch path activated by this PR)
    │
    v
legal-incident-response (NEW; this PR)
    │
    │ Step 0 — CLASSIFY (auto + confirm)
    │   - input: incident free-text description
    │   - classifier: assets/path-classifier-keywords.yml (Python deterministic) + LLM judgement
    │   - output: inferred_type + confidence + signals[] (matched keywords)
    │   - user confirms / overrides
    │
    │ Step 1 — LOAD_PROFILE
    │   - reuse scripts/load_profile.py (functional copy from SP3a via canonical/)
    │   - validate against profile-schema.yml v2 (with external_counsel + regulatory_authorities optional)
    │
    │ Step 2 — DISPATCH path-specific sub-protocol
    │   - pii-breach          → protocols/pii-breach.md          (skeleton + LLM fill)
    │   - authority-letter    → protocols/authority-letter.md    (pure-LLM)
    │   - contract-breach     → protocols/contract-breach-delegate.md (classifier + handoff)
    │
    │ Step 3 — ASK_GAPS (per-path session vars)
    │
    │ Step 4 — RENDER (per-path)
    │   - pii-breach          → fill 3 templates → consolidate to legal.md
    │   - authority-letter    → LLM generates 函覆 + 內部摘要 → legal.md
    │   - contract-breach     → emit handoff-context.json + thin legal.md / business.md with pointer
    │
    │ Step 5 — TIMELINE assembly (ISO 8601; ⏳ for unrealized anchors)
    │
    │ Step 6 — COMPLY_CHECK (per-path checklist with statute citations; verdicts as PASS / FAIL / TBD_<canonical_id>)
    │
    │ Step 7 — SELF_GRADE (scripts/grade_response.py output-dir path-type → exit 0/1)
    │
    │ Step 8 — OUTPUT (always 2 files + optional handoff JSON for contract-breach)
    │   legal-outputs/<timestamp>-incident-<path-type>/
    │     - legal.md
    │     - business.md
    │     - handoff-context.json    (only for contract-breach path)
    v
USER reviews; if contract-breach: continues into legal-contract-review session (user invokes manually; v0.4.2 NO auto-orchestration)
```

### Path-classifier signal table

```yaml
# assets/path-classifier-keywords.yml
pii-breach:
  high_confidence_keywords:
    - 外洩 / leak / breach / hack / 駭客 / 異常存取
    - 用戶資料 / 客戶資料 / 個資 / 個人資料
    - 數萬筆 / N 筆 / 資料庫 / database
  required_context:
    - 有具體事件描述 (時間 / 規模 / 影響)
    - 涉及用戶或個人資料

authority-letter:
  high_confidence_keywords:
    - 金管會 / 證交所 / 個資組 / 公平會 / 勞動部 / 環保署 / 衛福部
    - 函 / 來文 / 公文 / 行政處分 / 行政檢查 / 命令
    - deadline / 限期 / 期限 / N 日內
  required_context:
    - 有主管機關名稱
    - 有 deadline 標示

contract-breach:
  high_confidence_keywords:
    - 違約 / breach / default
    - 對方未付 / 對方未交付 / 對方延遲
    - 解除合約 / 終止合約
    - 催告 / 賠償 / 救濟 / 違反條款
  required_context:
    - 有已生效合約存在
    - 對方為履約對象
```

LLM在 Step 0 reads description + matches above table → emits `inferred_type` + `confidence` (HIGH/MEDIUM/LOW) + `signals[]` list of matched keywords. User confirms (default ENTER) or overrides type.

## 5. File layout

```
legal-toolkit/skills/legal-incident-response/
├── SKILL.md
├── README.md
├── README.ja.md                                   # tri-language per PR #150
├── README.zh-TW.md
│
├── assets/
│   ├── profile-schema.yml                         # v2 (synced from canonical/ via distribute.py)
│   ├── output-schema.json                         # 2-file audience-shaped + optional handoff-context.json schema
│   ├── path-classifier-keywords.yml               # Step 0 classifier signal table
│   ├── template-pii-breach-pdpc-notification.md   # 個資外洩: PDPC 通報文 skeleton (Path A 即時)
│   ├── template-pii-breach-data-subject.md        # 個資外洩: 當事人通知文 skeleton (zh-TW)
│   ├── template-pii-breach-incident-record.md     # 個資外洩: 內部記錄 skeleton (時間軸 + 影響範圍 + 採取措施)
│   └── template-contract-breach-handoff.json      # 違約: delegation seed JSON template (schema_version 1)
│
├── protocols/
│   ├── classify-path.md                           # Step 0 classifier protocol (LLM 讀 description 對表 + emit confidence)
│   ├── pii-breach.md                              # 個資外洩 sub-protocol (skeleton + LLM fill pipeline)
│   ├── authority-letter.md                        # 主管機關函覆 sub-protocol (pure-LLM)
│   └── contract-breach-delegate.md                # 違約 delegate sub-protocol
│
├── checklists/
│   ├── compliance-pii-breach.md                   # 個資法 §12 / 施行細則 §22 / §6 / §21 / §27 + TBD migration
│   ├── compliance-authority-letter.md             # 函要求齊備 / deadline 標示 / 法源 in canonical / 主管機關權限對齊
│   └── compliance-contract-breach.md              # Handoff completeness checklist
│
├── references/
│   ├── pdpa-current-state.md                      # SHARED with SP3a (functional copy from canonical/)
│   ├── tbd-migration-template.md                  # SHARED with SP3a (functional copy from canonical/)
│   ├── statute-citations.md                       # IR-specific (個資法 §12 §22 / 民法 §227 §250 §234 / 公司法 §202 / 行政程序法 §49)
│   └── ir-pii-breach-flow.md                      # 個資外洩 path 法源流程 narrative reference
│
└── scripts/
    ├── load_profile.py                            # SHARED (functional copy from canonical/; mirror SP3a)
    ├── classify_path.py                           # deterministic helper: matched signals only; LLM owns confidence
    └── grade_response.py                          # single grader, per-path branch
```

### SSOT extension (canonical/ files)

`legal-toolkit/scripts/canonical/` (extends SP1 PR #272 plumbing):

```
canonical/
├── legal-sources.json                             # EXISTING (SP1)
├── pdpa-current-state.md                          # NEW (move from SP3a; SoT)
├── tbd-migration-template.md                      # NEW (move from SP3a; SoT)
├── profile-schema.yml                             # NEW (move from SP3a; v1 → v2 in this PR; SoT)
└── load_profile.py                                # NEW (move from SP3a; SoT)
```

`distribute.py` ROUTE table grows:

```python
ROUTE = {
    "legal-sources.json": [
        "skills/legal-contract-review/assets/legal-sources.json",
    ],
    "pdpa-current-state.md": [
        "skills/legal-document-draft/references/pdpa-current-state.md",
        "skills/legal-incident-response/references/pdpa-current-state.md",
    ],
    "tbd-migration-template.md": [
        "skills/legal-document-draft/references/tbd-migration-template.md",
        "skills/legal-incident-response/references/tbd-migration-template.md",
    ],
    "profile-schema.yml": [
        "skills/legal-document-draft/assets/profile-schema.yml",
        "skills/legal-incident-response/assets/profile-schema.yml",
    ],
    "load_profile.py": [
        "skills/legal-document-draft/scripts/load_profile.py",
        "skills/legal-incident-response/scripts/load_profile.py",
    ],
}
```

`verify-drift.py` runs on the expanded ROUTE (same logic; just more entries). CI gate unchanged structurally.

## 6. Per-path protocol details

### 6.1 pii-breach (skeleton + LLM fill)

Pipeline within `protocols/pii-breach.md`:

```
LOAD_PROFILE → SELECT_TEMPLATES (3 templates loaded)
  → ASK_GAPS (incident_datetime / discovery_datetime / affected_count /
              data_categories[] / cross_border_subjects[] / containment_actions[] /
              notification_channels[] / external_counsel_engaged{}/...)
  → MERGE (fill 3 templates with session vars + profile defaults)
  → ASSEMBLE_LEGAL_MD (consolidate: §1 摘要 / §2 時間軸 / §3 影響範圍 /
                       §4 採取措施 / §5 PDPC 通報文 / §6 當事人通知文 /
                       §7 compliance + TBD migration)
  → ASSEMBLE_BUSINESS_MD (§1 incident 1-sentence / §2 Top 3 / §3 對外溝通要點 / §4 預估時程)
  → COMPLY_CHECK (compliance-pii-breach.md verdicts)
  → SELF_GRADE → OUTPUT
```

**Path A discipline in pii-breach body**:
- 通報文 body 用「即時」(施行細則 §22); 不寫具體小時數
- TBD_PDPC_timeframe / threshold / notification_url / pending / effective_date in compliance.md migration tracker (canonical ids only)
- 民法 §12 成年年齡 = 18 (v0.4.1 lock-in propagates)
- 委託/受託 model (NOT controller/processor)

### 6.2 authority-letter (pure-LLM)

Pipeline within `protocols/authority-letter.md`:

```
LOAD_PROFILE → ASK_GAPS (incoming_letter_summary_or_paste /
                         incoming_authority / incoming_date / deadline /
                         requested_items[] / mode: 函覆/補件/不服救濟)
  → EXTRACT (LLM reads incoming letter content;
             extracts 主管機關 / 法源依據 / 要求項目 / deadline)
  → DRAFT (LLM writes 函覆 with: 受文者 / 主旨 / 說明 / 法源回應 / 附件清單)
  → ASSEMBLE_LEGAL_MD (§1 incoming 函要求摘要 / §2 時間軸 (收文 / deadline / 我方計畫) /
                       §3 函覆草稿 / §4 compliance)
  → ASSEMBLE_BUSINESS_MD (§1 函要求 1-line / §2 Top 3 / §3 deadline / §4 風險摘要)
  → COMPLY_CHECK (compliance-authority-letter.md verdicts)
  → SELF_GRADE → OUTPUT
```

**Structural checks despite pure-LLM**:
- deadline ISO date is present in legal.md timeline
- 函覆 body references the incoming 函要求 items (LLM自己 cross-link)
- 法源引用 (if any) appear in `canonical/legal-sources.json` (deterministic check)

### 6.3 contract-breach (thin classifier + handoff)

Pipeline within `protocols/contract-breach-delegate.md`:

```
LOAD_PROFILE → ASK_GAPS (contract_path /
                         breach_type / breach_date / discovery_date /
                         counterparty / alleged_breach_clauses[] /
                         damages_estimate_twd? / urgency_level)
  → CLASSIFY_BREACH_TYPE (民法 §227 不完全給付 / §225 給付不能 /
                          §234 受領遲延 / §229 給付遲延 / etc.)
  → RENDER_HANDOFF (write handoff-context.json from template)
  → ASSEMBLE_LEGAL_MD (§1 違約 classification / §2 時間軸 /
                       §3 §Handoff section (pointer to legal-contract-review) /
                       §4 compliance (handoff completeness))
  → ASSEMBLE_BUSINESS_MD (§1 違約事件摘要 / §2 Top 3 即時動作 (保存證據/聯絡對方/評估救濟) /
                          §3 後續流程 / §4 deadline 警示 (民法時效 5 年 §125))
  → COMPLY_CHECK (compliance-contract-breach.md verdicts;
                  schema-validate handoff-context.json)
  → SELF_GRADE → OUTPUT
```

**v0.4.2 explicit non-scope**:
- ❌ SP3b does NOT auto-invoke `legal-contract-review` (user manually triggers)
- ❌ SP3b does NOT do deep contract clause extraction (that's contract-review's L0-L7)
- ✅ SP3b emits `handoff-context.json` + clear pointer in legal.md §3

**v0.4.3+ optional enhancement** (not in this PR):
- contract-review adds `--seed <handoff.json>` flag → reads SP3b's seed → skips overlapping ASK_GAPS
- contract-review may add `breach-remedy` mode (post-execution remedy analysis)

### 6.4 Cross-path output dir naming convention

`legal-outputs/<timestamp>-incident-<path-type>/`

- `<timestamp>` ISO 8601 compact: `2026-05-13T1430`
- `<path-type>` ∈ `{pii-breach, authority-letter, contract-breach}`

Example: `legal-outputs/2026-05-13T1430-incident-pii-breach/`

Mirror SP3a `<timestamp>-<mode>/` convention; "incident-" prefix distinguishes IR session from draft session, useful when user runs both in same day.

## 7. Grader design (`scripts/grade_response.py`)

Mirror SP3a `grade_draft.py` shape:

```python
PATH_TYPES = {"pii-breach", "authority-letter", "contract-breach"}

# Path A anti-patterns — byte-identical copy of SP3a v0.4.1 PATH_A_ANTIPATTERNS
# (functional duplication; 4 regexes; cross-Python-module import across sibling
# skills is YAGNI). If the regex bank needs to extend post-v0.4.2, refactor to
# canonical/path_a_antipatterns.py + distribute.py at that time.
PATH_A_ANTIPATTERNS = [
    (r"未滿\s*二十\s*歲|未滿\s*20\s*歲", "民法 §12 修正 2023-01-01..."),
    (r"72\s*小時|72\s*hour", "Taiwan PDPA 施行細則 §22 = 即時..."),
    (r"controller[\s\-/]+processor", "Taiwan uses 委託者/受託者 model..."),
    (r"資料控管者", "「資料控管者」 is GDPR controller direct translation..."),
]

def grade_response(output_dir: Path, path_type: str) -> GradeResult:
    common = []
    common.extend(_check_two_files_present(output_dir))
    common.extend(_check_iso_timeline_section_in_legal_md(output_dir))
    common.extend(_check_tbd_ids_canonical(output_dir))
    common.extend(_check_path_a_antipatterns_in_legal_md(output_dir))

    if path_type == "pii-breach":
        return GradeResult(passed=..., reasons=common + _check_pii_breach_specific(output_dir))
    elif path_type == "authority-letter":
        return GradeResult(passed=..., reasons=common + _check_authority_letter_specific(output_dir))
    elif path_type == "contract-breach":
        return GradeResult(passed=..., reasons=common + _check_contract_breach_handoff(output_dir))
    else:
        return GradeResult(passed=False, reasons=[f"unknown path_type: {path_type}"])
```

**Common structural checks**:
1. Both `legal.md` + `business.md` exist + byte-count > MIN
2. legal.md contains §時間軸 section with ≥ 1 ISO 8601 date row
3. All `TBD_*` ids in legal.md / business.md are in canonical OPEN list
4. Path A anti-patterns absent from legal.md + business.md (mirror v0.4.1)

**Per-path checks**:
- pii-breach: 3 template sections present (PDPC 通報文 / 當事人通知 / 內部記錄); checklist verdicts; mandatory items (事故描述/影響範圍/採取措施/法源)
- authority-letter: deadline ISO date present; 函覆 body non-empty; 法源 references valid (in canonical/legal-sources.json)
- contract-breach: handoff-context.json present + schema-valid; legal.md §3 contains pointer; alleged_breach_clauses non-empty

## 8. Quality gates

- Tests: existing 201 (v0.4.1) + ~30-40 new tests for SP3b (T-IR-* prefix); target ≥ 240 pass
  - T-IR-CL-* classifier behavior (mock LLM; deterministic keyword match)
  - T-IR-LP-* load_profile.py v2 schema (backward-compatible with v1 user profiles)
  - T-IR-GR-* grade_response.py per-path branches (mirror T-G-* style from v0.4.1)
  - T-IR-DR-* drift verification on canonical/ expanded ROUTE (mirror SP1 T-D-* / T-V-*)
- CI checks: pytest + drift + skill-folder-structure + marketplace description sync + SKILL.md structure (all must pass)
- Dogfood: post-merge, user runs 1 PII-breach + 1 authority-letter hypothetical scenario; verify legal.md / business.md / timeline / Path A discipline / classifier confidence
- Path A anti-pattern grader inherits SP3a v0.4.1 bank + adds IR-specific entries if needed (e.g., "T+72:00 hr" hardcoded should be regex-rejected? — defer decision to implementation; may be unnecessary if templates don't allow such pattern)

## 9. Out-of-scope (deferred to v0.4.3 / Phase 2.5)

- legal-playbook clauses (`incident-response-stance.md` / `data-breach-thresholds.md` / etc.) — dogfood-driven (Q10)
- legal-contract-review consumption of handoff JSON (`--seed` flag; future `breach-remedy` mode) — contract-review's own scope
- 當事人通知文 multi-language (en/ja) — via `translation-toolkit`
- 違約 path SP3b自己做的 deep analysis — explicitly delegated (Q8)
- Auto-invocation of contract-review from SP3b — user manual接力 (Q8)
- Real-time PDPC 通報入口 URL polling (waits for 籌備處 → 正式委員會)
- Automated post-incident audit-log generation (litigation-ready timestamp + signature) — Phase 6 governance

## 10. Migration path (when PDPC sub-regs publish)

When PDPC eventually publishes 通報辦法 + 通報範圍:

1. Update `canonical/pdpa-current-state.md`: remove resolved TBD_* ids; mark as RESOLVED with effective date
2. Update `canonical/tbd-migration-template.md`: replace TBD placeholders in templates with concrete values
3. Run `distribute.py` → templates in SP3b (and SP3a) automatically pick up resolved values
4. Bump versions: legal-toolkit v0.4.x → v0.5.x (or whatever current); update README to note PDPC sub-reg resolution

Migration cost is bounded by canonical/ SSOT: edit 1-2 files in canonical/, run distribute, done.

## 11. Implementation plan placeholder

Implementation plan to be authored by `superpowers:writing-plans` skill in next step. Estimated phases:

1. **Phase A — canonical/ expansion + SSOT migration** (1 commit): move pdpa-current-state.md / tbd-migration-template.md / profile-schema.yml / load_profile.py into canonical/; extend distribute.py ROUTE; verify-drift exit 0
2. **Phase B — classifier + grader scaffolding** (1 commit per script): assets/path-classifier-keywords.yml + scripts/classify_path.py + scripts/grade_response.py + tests
3. **Phase C — pii-breach path** (parallelizable subagents): 3 templates + protocols/pii-breach.md + checklists/compliance-pii-breach.md + references/statute-citations.md + tests
4. **Phase D — authority-letter path** (parallelizable subagents): protocols/authority-letter.md + checklists/compliance-authority-letter.md + tests
5. **Phase E — contract-breach delegate path** (parallelizable subagents): protocols/contract-breach-delegate.md + assets/template-contract-breach-handoff.json + checklists/compliance-contract-breach.md + tests
6. **Phase F — SKILL.md + tri-lang READMEs + router activation + version bump + ROADMAP** (1 commit)
7. **Phase G — post-PR dogfood** (separate session): 1 PII + 1 authority-letter scenario; capture findings; defer to v0.4.3 patches if needed

Estimated 3-4 days subagent-driven (close to ROADMAP estimate of 4-6 days; reduced by 1-2 days because contract-breach path is thin).

## 12. References

- ROADMAP: `legal-toolkit/ROADMAP.md` §Phase 2 v0.4.2 (SP3b)
- SP2 verify run: `legal-toolkit/research/2026-05-12-pdpa-2025-11-verify.md` (Path A ground truth)
- SP3a design: `docs/superpowers/specs/2026-05-13-legal-toolkit-sp3a-document-draft-design.md`
- SP3a dogfood audit: `docs/superpowers/audits/2026-05-13-legal-document-draft-sp3a-dogfood.md` (Path A anti-pattern lessons → reused in SP3b grader)
- SP1 canonical/ refactor: `docs/superpowers/specs/2026-05-12-legal-toolkit-sp1-sources-canonical-refactor-design.md`
- obsidian SoT §3.5: `<obsidian-vault>/research/2026-05-09 法務 Agent Skill (legal-toolkit) 整體架構與執行流程設計.md#3.5 legal-incident-response`
- Cross-skill delegation contract: `monkey-skills/CLAUDE.md` §Cross-Plugin Delegation Contract
- Skill structure: `monkey-skills/CLAUDE.md` §Skill Structure（flat subfolders, no nesting）
