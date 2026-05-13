# legal-document-draft SP3a dogfood — 2026-05-13

**Scope**: Validate v0.4.0 `legal-document-draft` skill against the spec by running the full pipeline on 2 hypothetical Taiwan SME use cases. Self-dogfood (Claude played both author + reviewer).

**Modes covered**: `privacy` + `nda` (50% of 4-mode surface). `tos` and `dpa` deferred — same template scaffolding pattern, low marginal signal at this round.

**Working dir**: `/tmp/legal-dogfood-2026-05-13/`
**Profile fixture**: 墨韻設計有限公司 (fictional SME design studio)

---

## TL;DR

| Pipeline step | Run 1 (privacy) | Run 2 (nda) |
|---|---|---|
| LOAD_PROFILE | ✅ PASS | ✅ PASS |
| SELECT_TEMPLATE | ✅ found | ✅ found |
| SCAN_PLAYBOOK | ✅ 4 vars resolved from playbook | n/a (privacy has no playbook mapping) |
| ASK_GAPS contract | ⚠️ **1 var missing from list** (#1) | n/a |
| MERGE | ✅ all variables resolved | ✅ all variables resolved |
| COMPLY_CHECK | ✅ 15/15 verdicts | ✅ 9/9 verdicts |
| SELF_GRADE (`grade_draft.py`) | ✅ PASS (exit 0) | ✅ PASS (exit 0) |

**But the grader's "PASS" is misleading**: it caught zero of the real issues found by hand review. See Finding #4 + #6.

**Net signal**: **green build, yellow material quality**. Two `PASS`-ed structural runs hide one P0 Path A correctness regression (民法 §12 age 20 vs 18), two P1 template hygiene issues, and one P1 grader-coverage gap.

---

## Findings

### 🔴 P0 — Finding #4: 民法 §12 成年年齡 outdated (20 → 18)

| | |
|---|---|
| **File** | `legal-toolkit/skills/legal-document-draft/assets/template-privacy.md:102` |
| **Current text** | `如使用者未滿七歲，不具行為能力，應由父母或監護人代為同意；未滿二十歲限制行為能力人，應經父母或監護人同意。` |
| **Correct text** | `…未滿七歲，不具行為能力…；滿七歲未滿十八歲為限制行為能力人，應經父母或監護人同意。` |
| **Authority** | 民法 §12 修正（2020-12-25 三讀，2023-01-01 施行）：成年年齡 20 → 18 |
| **Internal contradiction** | SP3a's own SP2 ground-truth note (`legal-toolkit/research/2026-05-12-pdpa-2025-11-verify.md:168`) literally says: *"7–20 (限制行為能力人, 滿7歲未滿18歲 per 民法 Art. 12 as amended in 2023)"* — template authoring transcribed the legacy 20 instead of the SP2-locked 18. |
| **Why grader missed it** | `_check_no_orphans` / `_check_checklist_verdicts` / `_check_tbd_ids_match_canonical` are structural; no semantic Path A check. |
| **Why checklist missed it** | `compliance-privacy.md:29` checks "NOT a PDPA-specific age threshold" — passes when ANY 民法 citation appears, regardless of the age inside. |
| **Severity** | Path A correctness is the load-bearing promise of v0.4.0. Shipping wrong age = the bug class SP2 was explicitly designed to prevent. |

**Fix**: 1-line template update + 1-line ref update + add a `grade_draft.py` anti-pattern check (see Finding #6).

---

### 🟠 P1 — Finding #6: `grade_draft.py` doesn't enforce Path A anti-patterns

Grader checks 5 structural conditions (orphans / verdict markers / TBD ids / byte count / file existence) but enforces **zero** of the 5 Path A discipline pillars locked in SP2:

| SP2 Path A pillar | Grader check? |
|---|---|
| 即時 (NOT 72hr breach window) | ❌ |
| 委託/受託 (NOT controller/processor) | ❌ |
| 民法 §12-13 age (NOT PDPA-specific) — **AND specifically age 18 not 20** | ❌ |
| 施行日期未定 (NOT 2025/11 effective) | ❌ |
| PDPC 籌備處 (NOT operational regulator) | ❌ |

**Fix**: add `_check_path_a_antipatterns(doc_text)` to `grade_draft.py`:

```python
PATH_A_ANTIPATTERNS = [
    (r"72\s*小時", "72hr breach window is GDPR Art. 33, not Taiwan PDPA. Use 即時."),
    (r"未滿二十歲|未滿\s*20\s*歲", "民法 §12 amended 2023-01-01: 成年 = 18. Use 未滿十八歲."),
    (r"controller[\s-]+processor|資料控管者", "Taiwan uses 委託/受託 model (§4 + §8), not controller/processor."),
    # ...
]
```

This is a deterministic safety net that would have caught Finding #4 on first run.

---

### 🟠 P1 — Finding #2: NDA template line 51 leaks playbook-author note into delivered document

| | |
|---|---|
| **File** | `legal-toolkit/skills/legal-document-draft/assets/template-nda.md:51` |
| **Current** | `(預設 survival period 來自 legal-playbook/confidentiality.md；典型範圍 3-7 年；技術機密可延至 10 年或永久)` |
| **Issue** | Reads like an authoring annotation, leaks into the final NDA delivered to counterparty. A real lawyer reviewer would flag it as unprofessional or potentially weakening (signals "this is a default we picked, not specifically negotiated"). |
| **Fix** | Convert to HTML comment `<!-- ... -->` so it stays in source but disappears from rendered doc; or move to `compliance.md` under "rationale" notes. |

---

### 🟠 P1 — Finding #3: privacy template line 34 produces awkward sentence

| | |
|---|---|
| **File** | `legal-toolkit/skills/legal-document-draft/assets/template-privacy.md:34` |
| **Template** | `如蒐集 §6 特種個資 ({{special_category_handling}})，將另行書面同意。` |
| **Rendered (Run 1)** | `如蒐集 §6 特種個資 (不主動蒐集 §6 特種個資；如客戶提供含特種個資之原稿，將另行書面同意並隔離儲存)，將另行書面同意。` |
| **Problem** | Double "§6 特種個資" + double "書面同意" — grammatically circular. Most users will say "we don't collect" → produces sentence that contradicts its own outer clause. |
| **Fix options** | (a) Split into 2 ASK_GAPS booleans: `collects_special_category: bool` → if false, emit "本公司不蒐集 §6 特種個資。"; if true, emit "本公司蒐集 §6 特種個資 ({{categories}})，另行書面同意 ({{consent_mechanism}})。" (b) Loosen the parenthetical and let LLM write the connecting prose. Prefer (a) — deterministic + less LLM drift. |

---

### 🟡 P2 — Finding #1: `{{survival_years_explanation}}` undocumented in ASK_GAPS

| | |
|---|---|
| **File** | `template-nda.md:49` uses `{{survival_years_explanation}}` |
| **Drift** | `protocols/draft.md` Step 4 ASK_GAPS nda required vars (line 74) lists 8 vars; `survival_years_explanation` is **not** in the list. |
| **Today's behavior** | LLM has to invent it (I filled "一般商業機密典型 3-7 年中位數…"). No orphan emitted; grader passes. |
| **Risk** | Future maintainer reads ASK_GAPS list → misses the variable → template orphan in production. |
| **Fix** | Either (a) add `survival_years_explanation` to ASK_GAPS nda required; (b) remove the `({{survival_years_explanation}})` from template line 49 since it's already explained by the parenthetical on line 51 (which is being moved to HTML comment per Finding #2). Prefer (b) — simpler scaffolding. |

---

### 🟡 P2 — Finding #8: compliance.md checkbox flipping convention undocumented

I marked items `- [x]` after evaluation; grader accepts both `- [ ]` and `- [x]`. Spec doesn't say which is correct. Cosmetic but worth a 1-line note in `protocols/draft.md` Step 6 (e.g., "Flip `- [ ]` → `- [x]` after determining verdict").

---

### ✅ Finding #7 (positive): playbook → variable flow works

For NDA: `survival_years=5` / `liquidated_damages=100000` / `return_days=7` / `preferred_court=臺灣臺北地方法院` all pulled correctly from `legal-playbook/confidentiality.md` + `legal-playbook/governing-law-jurisdiction.md`. The two-layer (playbook → session) design is sound.

---

### ➖ Non-issue — Finding #5: usage_regions / cross-border slight duplication

Privacy §4 `usage_regions` (session-supplied) and §7 cross-border bullets (profile-derived) both name countries. Reads as slight redundancy but technically each serves a different §8 disclosure requirement. Cosmetic only.

---

## ASK_GAPS UX signal (qualitative)

| Aspect | Signal |
|---|---|
| Variable count (privacy: 10 required + 7 derived; nda: 8 required + 1 undocumented) | OK for privacy; nda has the drift in #1 |
| Default visibility (playbook → ASK_GAPS) | ✅ works (playbook defaults like `preferred_court` would be shown inline per protocol) |
| Human-friendly labels | ⚠️ protocol says "Human-friendly labels (not raw variable names)" but doesn't supply the mapping. LLM has to translate per-session. Risk of inconsistency between sessions. |
| Batched single-prompt | ✅ design is sound; protocol explicit |

**Potential v0.4.1 polish**: ship an `assets/ask-gaps-labels.yml` (var_name → human_label_zh) so the prompt is deterministic across sessions.

---

## Grader signal (deterministic)

`grade_draft.py` runs in 5 ms. Caught 0 of 4 real issues this dogfood surfaced. Reframe accordingly:

- **Today**: grader = "did the LLM finish without obvious mechanical breakage"
- **Should be**: grader = "did the output satisfy structural + Path A discipline pillars"

Add anti-pattern checks (Finding #6); current grader stays as floor, not ceiling.

---

## v0.4.1 patch list (prioritized)

| Pri | Patch | Files | Est. effort |
|---|---|---|---|
| 🔴 P0 | 民法 §12 age 20 → 18 + 限制行為能力 phrasing | template-privacy.md:102 + statute-citations.md:34 | 5 min |
| 🟠 P1 | Add `_check_path_a_antipatterns` to grader (catches age 20 / 72hr / controller-processor) | grade_draft.py + tests | 30 min |
| 🟠 P1 | NDA template playbook note → HTML comment | template-nda.md:51 | 2 min |
| 🟠 P1 | Privacy `{{special_category_handling}}` split into 2-state collects/details | template-privacy.md:34 + protocols/draft.md:68 + checklist | 20 min |
| 🟡 P2 | NDA `{{survival_years_explanation}}` either documented in ASK_GAPS or removed from template | template-nda.md:49 + protocols/draft.md:74 | 5 min |
| 🟡 P2 | Checkbox flipping convention `- [ ]` → `- [x]` in Step 6 protocol | protocols/draft.md:88 | 1 min |
| 🟡 P2 | (optional) deterministic `assets/ask-gaps-labels.yml` for human labels | new file | 20 min |

**Total**: 1 P0 (5 min) + 3 P1 (~52 min) + 3 P2 (~26 min) ≈ 80 min for a clean v0.4.1.

**Recommended split** (3 PRs):
1. **v0.4.1 P0+P1** — Path A correctness (age fix + grader anti-patterns + parenthetical hygiene). Single PR. ~55 min.
2. **v0.4.2 P2 polish** — ASK_GAPS contract cleanup + checkbox convention. Single PR. ~10 min.
3. **(optional) v0.4.3** — ask-gaps-labels.yml deterministic UX. ~20 min.

---

## What dogfood did NOT cover

- **`tos` mode** — template scaffold same as privacy/nda; would surface similar drift if any. Marginal signal.
- **`dpa` mode** — has its own 委託/受託 Path A pillar; should be a separate dogfood once v0.4.1 anti-pattern checks land.
- **Real user friction** — I simulated answers; real users will have edge cases (Chinese name with apostrophes / multi-product company / consultancy without DPO). Add to v0.5 backlog.
- **Cross-skill** — privacy policy → contract-review pairing not tested. Phase 2.5 once SP3b ships.

---

## Memory updates

- Add to `project_legal_toolkit_design.md`: SP3a dogfood found 1 P0 + 3 P1 + 3 P2; v0.4.1 patch plan locked.
- Add to `feedback_grader_structural_vs_semantic.md` (new): structural graders (orphan / verdict / byte) don't catch domain regressions like age-20 vs age-18 drift; Path A pillars need explicit anti-pattern grep. Pattern reusable for any "spec-as-discipline" skill.
- Add to `feedback_dogfood_authoring_drift.md` (new): When `references/<state>.md` is the ground truth, templates should be machine-checked against it — not just human-cited. SP3a's own SP2 note said "age 18"; SP3a templates said "age 20". Author-time drift between Phase n research and Phase n+1 template is a real failure mode.
