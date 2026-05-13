# SP3b legal-incident-response v0.4.2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `legal-incident-response` v0.4.2 — Phase 2 closeout of legal-toolkit ROADMAP. 3-path classifier skill (PII-breach skeleton+LLM / Authority-letter pure-LLM / Contract-breach delegate). Path A discipline aligned with SP2 verify run.

**Architecture:** Single skill with 3-path classifier (auto-classify + confirm). Audience-shaped 2-file output (legal.md + business.md). Per-path authoring approach (mixed). Single `grade_response.py` per-path branch. SP1 canonical/ SSOT extends to cover pdpa-current-state / tbd-migration / profile-schema / load_profile (4 new files distributed to SP3a + SP3b functional copies).

**Tech Stack:** Python 3.12+ (PYTHONDONTWRITEBYTECODE=1 for pytest), pytest, JSON Schema 2020-12, PyYAML, jsonschema lib.

**Predecessor:** Spec `docs/superpowers/specs/2026-05-13-legal-toolkit-sp3b-incident-response-design.md` (commit `cdd1167` on branch `feat/legal-toolkit-sp3b-incident-response-spec`).

---

## File Structure

### New files to create

**Plugin-level canonical SSOT** (`legal-toolkit/scripts/canonical/`):
- `pdpa-current-state.md` (move from SP3a `references/`)
- `tbd-migration-template.md` (move from SP3a `references/`)
- `profile-schema.yml` (move from SP3a `assets/`; v1 → v2)
- `load_profile.py` (move from SP3a `scripts/`)

**New skill** (`legal-toolkit/skills/legal-incident-response/`):
- `SKILL.md`
- `README.md` / `README.ja.md` / `README.zh-TW.md`
- `assets/profile-schema.yml` (functional copy from canonical/)
- `assets/output-schema.json`
- `assets/path-classifier-keywords.yml`
- `assets/template-pii-breach-pdpc-notification.md`
- `assets/template-pii-breach-data-subject.md`
- `assets/template-pii-breach-incident-record.md`
- `assets/template-contract-breach-handoff.json`
- `protocols/classify-path.md`
- `protocols/pii-breach.md`
- `protocols/authority-letter.md`
- `protocols/contract-breach-delegate.md`
- `checklists/compliance-pii-breach.md`
- `checklists/compliance-authority-letter.md`
- `checklists/compliance-contract-breach.md`
- `references/pdpa-current-state.md` (functional copy from canonical/)
- `references/tbd-migration-template.md` (functional copy from canonical/)
- `references/statute-citations.md` (IR-specific)
- `references/ir-pii-breach-flow.md`
- `scripts/load_profile.py` (functional copy from canonical/)
- `scripts/classify_path.py`
- `scripts/grade_response.py`

**Tests** (`legal-toolkit/tests/`):
- `test_classify_path.py` (T-IR-CL-* prefix)
- `test_grade_response.py` (T-IR-GR-*)
- Extension to `test_canonical.py` (4 new T-D-* + 4 new T-V-* = 8 new tests for expanded ROUTE)

### Files to modify

- `legal-toolkit/scripts/distribute.py` — extend ROUTE table (4 new SoT entries)
- `legal-toolkit/skills/using-legal-toolkit/SKILL.md` — activate Q5 dispatch path
- `legal-toolkit/.claude-plugin/plugin.json` — version 0.4.1 → 0.4.2 + description append
- `.claude-plugin/marketplace.json` — sync description
- `legal-toolkit/README.md` / `README.ja.md` / `README.zh-TW.md` — version badge bump
- `legal-toolkit/ROADMAP.md` — Phase 2 v0.4.2 marked DONE

### Files to delete (after move to canonical/)

- `legal-toolkit/skills/legal-document-draft/references/pdpa-current-state.md` (then auto-recreated by distribute.py)
- `legal-toolkit/skills/legal-document-draft/references/tbd-migration-template.md` (then auto-recreated)
- `legal-toolkit/skills/legal-document-draft/assets/profile-schema.yml` (then auto-recreated; v2 schema)
- `legal-toolkit/skills/legal-document-draft/scripts/load_profile.py` (then auto-recreated)

(The `git mv → canonical/` + `distribute.py` re-materialization should leave SP3a functionally unchanged byte-identical at end of Task 1.)

---

## Task 1: Canonical SSOT extension + SP3b skill skeleton

**Phase A.** Migrate 4 SP3a files to plugin-level canonical/, extend distribute.py, create v2 profile schema (adds 2 optional fields), bootstrap SP3b skill dir with minimal SKILL.md so subsequent tasks have a valid skill structure to land into.

**Files:**
- Move: `legal-toolkit/skills/legal-document-draft/references/pdpa-current-state.md` → `legal-toolkit/scripts/canonical/pdpa-current-state.md`
- Move: `legal-toolkit/skills/legal-document-draft/references/tbd-migration-template.md` → `legal-toolkit/scripts/canonical/tbd-migration-template.md`
- Move: `legal-toolkit/skills/legal-document-draft/assets/profile-schema.yml` → `legal-toolkit/scripts/canonical/profile-schema.yml`
- Move: `legal-toolkit/skills/legal-document-draft/scripts/load_profile.py` → `legal-toolkit/scripts/canonical/load_profile.py`
- Modify: `legal-toolkit/scripts/canonical/profile-schema.yml` (v1 → v2; add 2 optional fields)
- Modify: `legal-toolkit/scripts/distribute.py` (extend ROUTE; +4 entries)
- Create: `legal-toolkit/skills/legal-incident-response/SKILL.md` (minimal frontmatter)
- Modify: `legal-toolkit/scripts/tests/test_canonical.py` (or whatever the existing test file is called — likely `test_distribute.py` and `test_verify_drift.py`)

- [ ] **Step 1: Locate existing canonical tests**

Run: `ls legal-toolkit/scripts/tests/`
Expected: identifies existing test files (e.g., `test_distribute.py` + `test_verify_drift.py`); we'll extend these.

- [ ] **Step 2: Write the failing test for expanded ROUTE**

Add to existing test file (e.g., `legal-toolkit/scripts/tests/test_distribute.py`):

```python
def test_distribute_includes_sp3b_canonical_files(tmp_path):
    """ROUTE must include pdpa-current-state.md / tbd-migration-template.md
    / profile-schema.yml / load_profile.py mapped to SP3a + SP3b destinations."""
    from distribute import ROUTE
    assert "pdpa-current-state.md" in ROUTE
    assert "tbd-migration-template.md" in ROUTE
    assert "profile-schema.yml" in ROUTE
    assert "load_profile.py" in ROUTE
    for canonical_name in ("pdpa-current-state.md", "tbd-migration-template.md",
                            "profile-schema.yml", "load_profile.py"):
        destinations = ROUTE[canonical_name]
        assert any("legal-document-draft" in d for d in destinations), \
            f"{canonical_name} missing SP3a destination"
        assert any("legal-incident-response" in d for d in destinations), \
            f"{canonical_name} missing SP3b destination"
```

- [ ] **Step 3: Run test to verify it fails**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/scripts/tests/test_distribute.py::test_distribute_includes_sp3b_canonical_files -v`
Expected: FAIL (ROUTE missing new entries)

- [ ] **Step 4: Create SP3b skill bootstrap SKILL.md**

Create `legal-toolkit/skills/legal-incident-response/SKILL.md`:

```markdown
---
name: legal-incident-response
description: Taiwan in-house 法務 incident response skill — 3-path classifier (個資外洩 PII-breach / 主管機關函覆 authority-letter / 合約違約 contract-breach). Auto-classifies free-text incident descriptions, dispatches per-path sub-protocols, emits 2-file audience-shaped output (legal.md / business.md) with ISO 8601 timeline + TBD migration tracker. PII-breach uses skeleton+LLM-fill templates pinned to current Taiwan law (Path A from SP2 verify run); authority-letter uses pure-LLM protocol; contract-breach delegates to legal-contract-review via handoff-context.json. Cross-references legal-playbook/profile.yml (shared with legal-document-draft) for company identity + regulatory_authorities + external_counsel.
---

# legal-incident-response

Taiwan in-house 法務 incident response (Phase 2 of legal-toolkit; v0.4.2).

Full design: `docs/superpowers/specs/2026-05-13-legal-toolkit-sp3b-incident-response-design.md`.

(Full SKILL.md body to be expanded in Task 11.)
```

- [ ] **Step 5: Move SP3a files to canonical/ via git mv**

Run:
```bash
git mv legal-toolkit/skills/legal-document-draft/references/pdpa-current-state.md \
       legal-toolkit/scripts/canonical/pdpa-current-state.md
git mv legal-toolkit/skills/legal-document-draft/references/tbd-migration-template.md \
       legal-toolkit/scripts/canonical/tbd-migration-template.md
git mv legal-toolkit/skills/legal-document-draft/assets/profile-schema.yml \
       legal-toolkit/scripts/canonical/profile-schema.yml
git mv legal-toolkit/skills/legal-document-draft/scripts/load_profile.py \
       legal-toolkit/scripts/canonical/load_profile.py
```

Expected: 4 files moved; `git status` shows R (rename) entries.

- [ ] **Step 6: Update canonical/profile-schema.yml v1 → v2**

Edit `legal-toolkit/scripts/canonical/profile-schema.yml` — add 2 optional properties under `properties:` section:

```yaml
  external_counsel:
    type: object
    description: 外部律師事務所聯絡資訊（高風險事件 escalation 用；optional）
    additionalProperties: false
    properties:
      firm_name: { type: string }
      contact_name: { type: string }
      email: { type: string, format: email }
      phone: { type: string }
      retainer_status: { type: string, enum: [active, ad-hoc, none] }
  regulatory_authorities:
    type: array
    description: 跟貴司業務相關主管機關清單（函覆 path 使用）
    items:
      type: object
      required: [name]
      additionalProperties: false
      properties:
        name: { type: string }
        url: { type: string, format: uri }
        scope_note: { type: string }
```

These are **optional** (NOT in top-level `required:` array). Existing v1 profile.yml files MUST still validate against v2 schema (backward compatibility).

- [ ] **Step 7: Update distribute.py ROUTE table**

Edit `legal-toolkit/scripts/distribute.py` — replace ROUTE dict:

```python
ROUTE: dict[str, list[str]] = {
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

- [ ] **Step 8: Run distribute.py to materialize functional copies**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 legal-toolkit/scripts/distribute.py`
Expected:
```
[deploy] canonical/legal-sources.json -> skills/legal-contract-review/assets/legal-sources.json
[deploy] canonical/load_profile.py -> skills/legal-document-draft/scripts/load_profile.py
[deploy] canonical/load_profile.py -> skills/legal-incident-response/scripts/load_profile.py
[deploy] canonical/pdpa-current-state.md -> skills/legal-document-draft/references/pdpa-current-state.md
...
OK: deployed 9 copies from canonical/ to skill assets/.
```

This recreates SP3a's files at their old paths (byte-identical to canonical/) AND creates SP3b's new files in `skills/legal-incident-response/{assets,references,scripts}/`.

- [ ] **Step 9: Verify drift zero**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 legal-toolkit/scripts/verify-drift.py`
Expected: exit 0; `OK: all N functional copies byte-identical to canonical.`

- [ ] **Step 10: Run the failing test from Step 2; expect PASS now**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/scripts/tests/test_distribute.py::test_distribute_includes_sp3b_canonical_files -v`
Expected: PASS

- [ ] **Step 11: Add T-V drift test for SP3b destinations**

Add to existing verify-drift test file (e.g., `legal-toolkit/scripts/tests/test_verify_drift.py`):

```python
def test_verify_drift_catches_sp3b_destination_modification(tmp_path):
    """Modifying SP3b's functional copy (e.g., load_profile.py) should be
    caught by verify-drift.py as drift (exit 1)."""
    # arrange: snapshot SP3b's load_profile.py
    sp3b_copy = REPO / "legal-toolkit" / "skills" / "legal-incident-response" / "scripts" / "load_profile.py"
    original = sp3b_copy.read_bytes()
    try:
        # act: introduce drift
        sp3b_copy.write_text(original.decode() + "\n# drift marker\n", encoding="utf-8")
        result = subprocess.run(
            ["python3", "legal-toolkit/scripts/verify-drift.py"],
            cwd=REPO, capture_output=True, env={"PYTHONDONTWRITEBYTECODE": "1"},
        )
        # assert
        assert result.returncode == 1, "verify-drift should fail on drift"
    finally:
        # cleanup
        sp3b_copy.write_bytes(original)
```

(Adapt the test class structure to match the existing test file's style — REPO constant, subprocess invocation, etc.)

- [ ] **Step 12: Run full pytest to ensure nothing else broke**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/ -q`
Expected: 201 (v0.4.1 baseline) + new tests pass; e.g., `203 passed` or `204 passed`.

If `test_load_profile.py` (SP3a) is broken by the schema v1 → v2 change: fix the failing tests inline (v2 schema must still accept v1 profile.yml — confirm with a backward-compatibility test).

- [ ] **Step 13: Run skill structure check**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-skill-structure.py legal-toolkit 2>&1 | tail -10`
Expected: `legal-incident-response` not in any FAIL section (or only same pre-existing FAILs as before — see v0.4.1 PR #279 history).

- [ ] **Step 14: Commit**

Run:
```bash
git add legal-toolkit/scripts/canonical/ legal-toolkit/scripts/distribute.py legal-toolkit/scripts/tests/ \
        legal-toolkit/skills/legal-document-draft/ legal-toolkit/skills/legal-incident-response/

git commit -m "feat(legal-toolkit): SP3b Phase A — canonical SSOT extension + skill bootstrap

Move 4 SP3a files to legal-toolkit/scripts/canonical/ (pdpa-current-state.md,
tbd-migration-template.md, profile-schema.yml, load_profile.py); extend
distribute.py ROUTE to deploy byte-identical functional copies to both SP3a
(legal-document-draft) and SP3b (legal-incident-response).

profile-schema.yml v1 → v2: +2 optional fields (external_counsel,
regulatory_authorities); v1 profile.yml files still validate (backward
compat verified).

Bootstrap legal-toolkit/skills/legal-incident-response/SKILL.md with minimal
frontmatter so skill dir is structurally valid; full SKILL.md body landed
in Task 11.

verify-drift.py exit 0 on expanded ROUTE; full pytest passes (203+ tests).
"
```

---

## Task 2: Path classifier (deterministic helper + LLM-facing protocol)

**Phase B (1/3).** Build the auto-classify mechanism: a deterministic Python helper that emits matched-keyword signals from incident description, plus an LLM-facing protocol that consumes signals + does confidence judgement.

**Files:**
- Create: `legal-toolkit/skills/legal-incident-response/assets/path-classifier-keywords.yml`
- Create: `legal-toolkit/skills/legal-incident-response/scripts/classify_path.py`
- Create: `legal-toolkit/tests/test_classify_path.py`
- Create: `legal-toolkit/skills/legal-incident-response/protocols/classify-path.md`

- [ ] **Step 1: Write the failing test**

Create `legal-toolkit/tests/test_classify_path.py`:

```python
"""Tests for legal-incident-response/scripts/classify_path.py.

classify_path.py is a deterministic helper: reads incident description
+ keyword table, returns matched signals (per-path lists). LLM owns
confidence judgement separately (in classify-path.md protocol).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "legal-toolkit" / "skills" / "legal-incident-response" / "scripts"
KEYWORDS = REPO / "legal-toolkit" / "skills" / "legal-incident-response" / "assets" / "path-classifier-keywords.yml"


def _load():
    spec = importlib.util.spec_from_file_location("classify_path", SCRIPTS / "classify_path.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_pii_breach_keywords_matched():
    classify = _load()
    desc = "今天早上發現有 8000 筆客戶資料被異常存取"
    result = classify.classify(desc, keywords_path=KEYWORDS)
    assert "pii-breach" in result.matched_paths
    assert any(kw in result.signals["pii-breach"] for kw in ["客戶資料", "異常存取"])


def test_authority_letter_keywords_matched():
    classify = _load()
    desc = "金管會來函要 7 日內回覆關於資安事件"
    result = classify.classify(desc, keywords_path=KEYWORDS)
    assert "authority-letter" in result.matched_paths
    assert any(kw in result.signals["authority-letter"] for kw in ["金管會", "函", "日內"])


def test_contract_breach_keywords_matched():
    classify = _load()
    desc = "對方違約沒付款已經 60 天，要不要催告解除合約"
    result = classify.classify(desc, keywords_path=KEYWORDS)
    assert "contract-breach" in result.matched_paths
    assert any(kw in result.signals["contract-breach"] for kw in ["違約", "催告", "解除合約"])


def test_multi_path_match_returns_all_matched():
    """When incident description matches multiple paths' keywords,
    classifier returns all of them; LLM (in protocol) handles primary selection."""
    classify = _load()
    desc = "金管會來函說我們公司有客戶資料外洩，要 7 日內說明"
    result = classify.classify(desc, keywords_path=KEYWORDS)
    assert "authority-letter" in result.matched_paths
    assert "pii-breach" in result.matched_paths


def test_no_keyword_match_returns_empty():
    classify = _load()
    desc = "天氣很好"
    result = classify.classify(desc, keywords_path=KEYWORDS)
    assert result.matched_paths == []
    assert all(sigs == [] for sigs in result.signals.values())
```

- [ ] **Step 2: Create the keyword table**

Create `legal-toolkit/skills/legal-incident-response/assets/path-classifier-keywords.yml`:

```yaml
# Deterministic keyword bank for path classification.
# scripts/classify_path.py reads this; LLM (in protocols/classify-path.md)
# judges confidence from matched signals + full description context.
#
# To extend a path's signal: add to high_confidence_keywords below.
# Pure substring match (case-insensitive); no regex.

pii-breach:
  high_confidence_keywords:
    - 外洩
    - leak
    - breach
    - hack
    - 駭客
    - 異常存取
    - unauthorized access
    - 用戶資料
    - 客戶資料
    - 個資
    - 個人資料
    - 資料庫
    - database
  required_context_notes: |
    PII-breach 場景：具體事件描述 + 涉及個人資料的洩漏 / 異常存取 / 駭客攻擊。
    若描述只是「考慮個資處理流程」(政策性) 不適用此 path → 應走 legal-document-draft privacy mode。

authority-letter:
  high_confidence_keywords:
    - 金管會
    - 證交所
    - 個資組
    - 公平會
    - 勞動部
    - 環保署
    - 衛福部
    - 主管機關
    - 函
    - 來文
    - 公文
    - 行政處分
    - 行政檢查
    - 命令
    - deadline
    - 限期
    - 期限
    - 日內
  required_context_notes: |
    Authority-letter 場景：具體主管機關發函 + 有 deadline 或 specific 要求。
    若只是一般法令諮詢（無具體函） → 應走 legal-research (Phase 3 future skill)。

contract-breach:
  high_confidence_keywords:
    - 違約
    - breach
    - default
    - 對方未付
    - 對方未交付
    - 對方延遲
    - 解除合約
    - 終止合約
    - 催告
    - 賠償
    - 救濟
    - 違反條款
  required_context_notes: |
    Contract-breach 場景：具體合約 + 已生效 + 對方明確違反某條款。
    若還在合約 review 階段（尚未簽署） → 應走 legal-contract-review。
```

- [ ] **Step 3: Create the deterministic helper script**

Create `legal-toolkit/skills/legal-incident-response/scripts/classify_path.py`:

```python
#!/usr/bin/env python3
"""Deterministic keyword-based path classifier for legal-incident-response.

Reads an incident description + path-classifier-keywords.yml; returns
matched keywords per path. LLM (in protocols/classify-path.md) judges
confidence and selects primary path from this output.

Public API:
    classify(description: str, keywords_path: Path) -> ClassifyResult

ClassifyResult:
    matched_paths: list[str]      paths with at least 1 matched keyword
    signals: dict[str, list[str]] per-path list of matched keywords
"""
# NOTE: do NOT add `from __future__ import annotations` — see SP3a
# load_profile.py / grade_draft.py for the importlib+@dataclass trap.

from dataclasses import dataclass, field
from pathlib import Path

import yaml

PATH_TYPES = ("pii-breach", "authority-letter", "contract-breach")


@dataclass
class ClassifyResult:
    matched_paths: list[str] = field(default_factory=list)
    signals: dict[str, list[str]] = field(default_factory=dict)


def classify(description: str, keywords_path: Path) -> ClassifyResult:
    """Match description against per-path keyword bank.

    Args:
      description: free-text incident description from user.
      keywords_path: path to path-classifier-keywords.yml.

    Returns:
      ClassifyResult; empty matched_paths if no keyword hit.
    """
    if not keywords_path.is_file():
        return ClassifyResult()

    data = yaml.safe_load(keywords_path.read_text(encoding="utf-8")) or {}
    desc_lower = description.lower()

    signals: dict[str, list[str]] = {p: [] for p in PATH_TYPES}
    for path_type in PATH_TYPES:
        path_def = data.get(path_type, {}) or {}
        keywords = path_def.get("high_confidence_keywords", []) or []
        for kw in keywords:
            if kw.lower() in desc_lower:
                signals[path_type].append(kw)

    matched_paths = [p for p in PATH_TYPES if signals[p]]
    return ClassifyResult(matched_paths=matched_paths, signals=signals)


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) != 3:
        print("usage: classify_path.py <description> <path/to/path-classifier-keywords.yml>", file=sys.stderr)
        sys.exit(2)

    result = classify(sys.argv[1], Path(sys.argv[2]))
    print(json.dumps({"matched_paths": result.matched_paths, "signals": result.signals}, ensure_ascii=False, indent=2))
    sys.exit(0)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/tests/test_classify_path.py -v`
Expected: 5 passed.

- [ ] **Step 5: Create the LLM-facing classifier protocol**

Create `legal-toolkit/skills/legal-incident-response/protocols/classify-path.md`:

```markdown
# Protocol — classify-path

The Step 0 classifier for legal-incident-response. Auto-classifies user's free-text incident description into one of 3 paths (pii-breach / authority-letter / contract-breach). User confirms before pipeline dispatches.

## Input

- `description` (str): user's free-text incident description, e.g., "今天早上發現有 8000 筆客戶資料被異常存取"

## Pipeline

### Step 0.1: Run deterministic keyword scan

```bash
python3 legal-toolkit/skills/legal-incident-response/scripts/classify_path.py \
  "<description>" \
  legal-toolkit/skills/legal-incident-response/assets/path-classifier-keywords.yml
```

Output JSON: `{"matched_paths": [...], "signals": {"pii-breach": [...], ...}}`.

### Step 0.2: LLM confidence judgement

Read the description full text + Step 0.1 signals output. Determine:

- **inferred_type**: which of (pii-breach / authority-letter / contract-breach) is the PRIMARY path
- **confidence**: HIGH / MEDIUM / LOW
- **rationale**: 1-2 sentences explaining why

Confidence rubric:

| Signals | Description match | Confidence |
|---|---|---|
| ≥ 3 keywords matched for 1 path, none for others | clear narrative fit | HIGH |
| ≥ 2 keywords matched + clear context fit | likely fit | MEDIUM |
| 1 keyword matched OR multi-path keywords | ambiguous | LOW |
| 0 keywords matched | description out-of-scope | (escalate; ASK user clarification) |

If `matched_paths` is empty: emit `inferred_type=null` + `confidence=NONE` and ASK user "請問這個事件比較像：(1) 個資外洩 (2) 主管機關函覆 (3) 合約違約？或您能再多描述一些細節？"

### Step 0.3: Confirm with user

Present to user:

```
事件分類：{{inferred_type_zh}}（{{inferred_type_en}}）
信心度：{{confidence}}
匹配關鍵字：{{signals[inferred_type]}}
判斷理由：{{rationale}}

請確認：
- 按 Enter 繼續走 {{inferred_type_zh}} 流程
- 輸入 1 / 2 / 3 切換 path（1=個資外洩 / 2=主管機關函覆 / 3=合約違約）
- 輸入 'q' 取消
```

If user confirms: proceed to Step 1 LOAD_PROFILE (in main pipeline). If user overrides: re-run classify-path with the override + continue.

### Step 0.4: Edge case — multi-path detection

If `matched_paths` ≥ 2 (e.g., "金管會來函說有客戶資料外洩，7 日內說明" matches both authority-letter + pii-breach):

- inferred_type = primary path (typically the OUTER trigger — here authority-letter, because 函 來文 deadline is the URGENT axis; pii-breach analysis runs INSIDE the 函覆 prep)
- LLM mentions secondary path in rationale: "本事件同時涉及 PII-breach 內容；可先走 authority-letter path（外部 deadline 緊），同 session 後續可再跑 pii-breach path 詳處 PDPC 通報"
- Confidence MEDIUM (not HIGH due to ambiguity)

## Output

JSON snippet returned to main pipeline:

```json
{
  "inferred_type": "authority-letter",
  "confidence": "MEDIUM",
  "signals_matched": ["金管會", "函", "日內", "客戶資料"],
  "rationale": "...",
  "secondary_path_hint": "pii-breach"
}
```

Main pipeline reads `inferred_type` for dispatch.
```

- [ ] **Step 6: Commit**

Run:
```bash
git add legal-toolkit/skills/legal-incident-response/assets/path-classifier-keywords.yml \
        legal-toolkit/skills/legal-incident-response/scripts/classify_path.py \
        legal-toolkit/skills/legal-incident-response/protocols/classify-path.md \
        legal-toolkit/tests/test_classify_path.py

git commit -m "feat(legal-toolkit): SP3b Phase B/1 — path classifier (helper + protocol)

Add deterministic keyword-based classifier (classify_path.py + path-
classifier-keywords.yml) that emits matched signals per path. LLM-facing
protocol (classify-path.md) consumes signals + judges confidence
HIGH/MEDIUM/LOW + handles multi-path edge case + user confirmation flow.

5 unit tests cover per-path keyword hits + multi-path + empty match.
"
```

---

## Task 3: Grader (single grade_response.py per-path branch)

**Phase B (2/3).** Build the deterministic grader. Mirrors SP3a `grade_draft.py` structure with PATH_A_ANTIPATTERNS bank (byte-identical copy per spec §7). Per-path branch logic; structural common floor.

**Files:**
- Create: `legal-toolkit/skills/legal-incident-response/scripts/grade_response.py`
- Create: `legal-toolkit/tests/test_grade_response.py`
- Create: `legal-toolkit/tests/fixtures-incident-response/draft-output-sample-pii-breach/` (minimal valid sample)
- Create: `legal-toolkit/tests/fixtures-incident-response/draft-output-sample-authority-letter/`
- Create: `legal-toolkit/tests/fixtures-incident-response/draft-output-sample-contract-breach/`

- [ ] **Step 1: Write the failing tests (skeleton)**

Create `legal-toolkit/tests/test_grade_response.py`:

```python
"""Tests for legal-incident-response/scripts/grade_response.py.

grade_response.py is a deterministic structural grader. Per-path branch
on top of common structural floor (2-file present / ISO timeline /
TBD canonical / Path A anti-patterns).
"""
from __future__ import annotations

import importlib.util
import shutil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "legal-toolkit" / "skills" / "legal-incident-response" / "scripts"
FIXTURES = REPO / "legal-toolkit" / "tests" / "fixtures-incident-response"


def _load():
    spec = importlib.util.spec_from_file_location("grade_response", SCRIPTS / "grade_response.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _copy_sample(tmp_path: Path, name: str) -> Path:
    target = tmp_path / "2026-05-13T1430-incident-pii-breach"
    shutil.copytree(FIXTURES / name, target)
    return target


# ---------------------------------------------------------- T-IR-GR-1: complete pii-breach PASS
def test_complete_pii_breach_passes(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path, "draft-output-sample-pii-breach")
    result = grade.grade_response(output_dir, path_type="pii-breach")
    assert result.passed is True, f"expected PASS, got reasons: {result.reasons}"


# ---------------------------------------------------------- T-IR-GR-2: missing legal.md FAIL
def test_missing_legal_md_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path, "draft-output-sample-pii-breach")
    (output_dir / "legal.md").unlink()
    result = grade.grade_response(output_dir, path_type="pii-breach")
    assert result.passed is False
    assert any("legal.md" in r and "missing" in r.lower() for r in result.reasons)


# ---------------------------------------------------------- T-IR-GR-3: missing business.md FAIL
def test_missing_business_md_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path, "draft-output-sample-pii-breach")
    (output_dir / "business.md").unlink()
    result = grade.grade_response(output_dir, path_type="pii-breach")
    assert result.passed is False
    assert any("business.md" in r and "missing" in r.lower() for r in result.reasons)


# ---------------------------------------------------------- T-IR-GR-4: unknown path_type FAIL
def test_unknown_path_type_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path, "draft-output-sample-pii-breach")
    result = grade.grade_response(output_dir, path_type="bogus-path")
    assert result.passed is False
    assert any("unknown path_type" in r.lower() for r in result.reasons)


# ---------------------------------------------------------- T-IR-GR-5: missing timeline section FAIL
def test_missing_timeline_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path, "draft-output-sample-pii-breach")
    legal = output_dir / "legal.md"
    text = legal.read_text(encoding="utf-8")
    # Strip the §時間軸 section
    text = text.replace("## §時間軸", "## §[REDACTED]")
    legal.write_text(text, encoding="utf-8")
    result = grade.grade_response(output_dir, path_type="pii-breach")
    assert result.passed is False
    assert any("timeline" in r.lower() or "時間軸" in r for r in result.reasons)


# ---------------------------------------------------------- T-IR-GR-6: fabricated TBD FAIL
def test_fabricated_tbd_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path, "draft-output-sample-pii-breach")
    legal = output_dir / "legal.md"
    text = legal.read_text(encoding="utf-8")
    text += "\n\n- TBD_FAKE_ID — 虛構的 TBD\n"
    legal.write_text(text, encoding="utf-8")
    result = grade.grade_response(output_dir, path_type="pii-breach")
    assert result.passed is False
    assert any("tbd" in r.lower() and ("fabricated" in r.lower() or "canonical" in r.lower()) for r in result.reasons)


# ---------------------------------------------------------- T-IR-GR-7..10: Path A anti-pattern
@pytest.mark.parametrize(
    "leak,fragment",
    [
        ("age_20", "未滿二十歲限制行為能力人"),
        ("breach_72hr", "72 小時內通報"),
        ("gdpr_controller", "controller-processor model"),
        ("gdpr_zh", "依資料控管者規定"),
    ],
)
def test_path_a_antipattern_in_legal_md_fails(tmp_path, leak, fragment):
    grade = _load()
    output_dir = _copy_sample(tmp_path, "draft-output-sample-pii-breach")
    legal = output_dir / "legal.md"
    legal.write_text(legal.read_text(encoding="utf-8") + f"\n\n## 違規測試 ({leak})\n{fragment}\n", encoding="utf-8")
    result = grade.grade_response(output_dir, path_type="pii-breach")
    assert result.passed is False
    assert any("path a violation" in r.lower() for r in result.reasons)


# ---------------------------------------------------------- T-IR-GR-11: authority-letter PASS
def test_complete_authority_letter_passes(tmp_path):
    grade = _load()
    target = tmp_path / "2026-05-13T1430-incident-authority-letter"
    shutil.copytree(FIXTURES / "draft-output-sample-authority-letter", target)
    result = grade.grade_response(target, path_type="authority-letter")
    assert result.passed is True, f"expected PASS, got reasons: {result.reasons}"


# ---------------------------------------------------------- T-IR-GR-12: contract-breach handoff present PASS
def test_complete_contract_breach_passes(tmp_path):
    grade = _load()
    target = tmp_path / "2026-05-13T1430-incident-contract-breach"
    shutil.copytree(FIXTURES / "draft-output-sample-contract-breach", target)
    result = grade.grade_response(target, path_type="contract-breach")
    assert result.passed is True, f"expected PASS, got reasons: {result.reasons}"


# ---------------------------------------------------------- T-IR-GR-13: contract-breach missing handoff FAIL
def test_contract_breach_missing_handoff_fails(tmp_path):
    grade = _load()
    target = tmp_path / "2026-05-13T1430-incident-contract-breach"
    shutil.copytree(FIXTURES / "draft-output-sample-contract-breach", target)
    (target / "handoff-context.json").unlink()
    result = grade.grade_response(target, path_type="contract-breach")
    assert result.passed is False
    assert any("handoff" in r.lower() for r in result.reasons)
```

- [ ] **Step 2: Create minimal fixture for pii-breach sample**

Create `legal-toolkit/tests/fixtures-incident-response/draft-output-sample-pii-breach/legal.md`:

```markdown
# 個資外洩事件法務記錄

## §1 事件摘要

於 2026-05-13 09:42 (system log) 察覺異常存取，影響筆數 8,000 筆。

## §時間軸

| 時間 (ISO 8601) | 事件 | 來源 |
|---|---|---|
| 2026-05-13 09:42 | 異常存取首見 | system log |
| 2026-05-13 09:59 | GC 知悉 | SOC 通知 |
| 2026-05-13 10:27 | 停止外洩源 | API key 停用 |
| 2026-05-14 09:00 | 當事人通知開始 | DPO 操作 |
| ⏳ 待 PDPC 子法 | 主管機關通報 | TBD_PDPC_timeframe |

## §2 影響範圍

涉及 8,000 筆客戶資料（識別資料 + 帳務資料）。無特種個資。

## §3 採取措施

- 停用受影響 API key
- 強制變更受影響用戶密碼
- 啟動安全稽核

## §4 PDPC 通報文

受文機關：個人資料保護委員會（籌備處）
通報期限：即時 (個資法施行細則 §22)
通報事項：本公司於察覺個資事故後即時通報，事故概要如下...

## §5 當事人通知文

(zh-TW only per Q11)

親愛的客戶您好：

本公司於 2026-05-13 察覺您的個人資料可能受到非法存取，謹此通知並說明本公司採取的因應措施...

## §6 Compliance Checklist

- [x] §8 第一項第二款 — 蒐集目的揭露？ — **PASS**
- [x] 施行細則 §22 — 即時通報使用？ — **PASS**
- [x] §6 + §9 — 特種個資處理？ — **PASS** (本案無特種個資)
- [x] §21 — 跨境傳輸 — **PASS** (本案無跨境)
- [x] §27 — 安全維護 — **PASS**
- [x] §20-1 — Audit framework — **TBD_PDPA_audit_framework** (Art. 20-1 promulgated 2025-11-11; 施行日期未定)

## §7 TBD migration tracker

- **TBD_PDPA_audit_framework**: monitor PDPC; when Art. 20-1 effective + 稽核辦法 published, update.
- **TBD_PDPC_timeframe**: 即時 used; SOP recommends 24-hour initial notification; replace when PDPC publishes specific hour count.
- **TBD_PDPC_threshold**: SOP triggers at >1000 affected; replace with statutory threshold when published.
```

Create `legal-toolkit/tests/fixtures-incident-response/draft-output-sample-pii-breach/business.md`:

```markdown
# 個資外洩事件——業務摘要

## §1 事件 1-句

8,000 筆客戶資料於 5/13 09:42 遭異常存取；已於 10:27 停止外洩源。

## §2 Top 3 即時動作

1. 已停用受影響 API key（10:27）
2. 啟動當事人通知（預定 5/14 09:00 開始；分批寄信）
3. 召開內部跨部門應變會議（CTO + CEO + DPO + 法務；今日 14:00）

## §3 對外溝通要點

- 公司主動察覺並即時止血
- 已啟動當事人通知與主管機關通報程序
- 採取的強化措施（密碼重置 + 安全稽核）
- 客服 hotline + email 對受影響用戶

## §4 預估時程

- 當事人通知完成：5/15
- 主管機關通報完成：5/17（按內部 SOP 24 小時內；確定法定時限後 align）
- 內部事故報告完稿：5/20
```

- [ ] **Step 3: Create authority-letter + contract-breach fixtures**

Similar structure, smaller content. For authority-letter fixture create `legal.md` with 函要求摘要 + 時間軸 (with ISO date for deadline) + 函覆草稿 + compliance section; and `business.md` with Top 3 + deadline alert.

For contract-breach fixture create thin `legal.md` (classification + 時間軸 + handoff pointer + compliance), `business.md`, AND `handoff-context.json`:

```json
{
  "schema_version": 1,
  "from_skill": "legal-incident-response",
  "to_skill": "legal-contract-review",
  "contract_path": "/path/to/contract.md",
  "breach_type": "不完全給付",
  "alleged_breach_clauses": ["§3.2", "§4.4"],
  "breach_date": "2026-05-08",
  "discovery_date": "2026-05-13",
  "counterparty": {"name": "對方公司"},
  "urgency_level": "moderate",
  "session_ref": "legal-outputs/2026-05-13T1430-incident-contract-breach/"
}
```

(Fixture contents should be just-enough for grader tests to pass; not production-quality drafts.)

- [ ] **Step 4: Create grade_response.py**

Create `legal-toolkit/skills/legal-incident-response/scripts/grade_response.py`:

```python
#!/usr/bin/env python3
"""Deterministic structural grader for legal-incident-response output directories.

Mirrors SP3a grade_draft.py shape (legal-document-draft/scripts/). Common
structural floor + per-path branch.

Path-type: "pii-breach" | "authority-letter" | "contract-breach"
"""
# NOTE: do NOT add `from __future__ import annotations`.
# See SP3a grade_draft.py for the importlib+@dataclass trap explanation.

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

REFS = Path(__file__).resolve().parent.parent / "references"
MIN_LEGAL_MD_BYTES = 500
MIN_BUSINESS_MD_BYTES = 200

PATH_TYPES = ("pii-breach", "authority-letter", "contract-breach")

# Byte-identical copy of SP3a v0.4.1 PATH_A_ANTIPATTERNS — see spec §7.
# Functional duplication; cross-Python-module import across sibling
# skills is YAGNI for 4 regexes. If the regex bank needs to extend
# post-v0.4.2, refactor to canonical/path_a_antipatterns.py + distribute.py
# at that time.
PATH_A_ANTIPATTERNS = [
    (
        re.compile(r"未滿\s*二十\s*歲|未滿\s*20\s*歲"),
        "民法 §12 修正 2023-01-01 起成年年齡為 18。Use 「未滿十八歲」 instead of 「未滿二十歲」.",
    ),
    (
        re.compile(r"72\s*小時|72\s*hour", re.IGNORECASE),
        "72hr notification window is GDPR Art. 33. Taiwan PDPA 施行細則 §22 = 「即時」.",
    ),
    (
        re.compile(r"controller[\s\-/]+processor", re.IGNORECASE),
        "Taiwan uses 委託者/受託者 model (個資法 §4 + §8), not GDPR controller/processor.",
    ),
    (
        re.compile(r"資料控管者"),
        "「資料控管者」 is GDPR controller direct translation. Taiwan uses 委託者 (個資法 §4).",
    ),
]


@dataclass
class GradeResult:
    passed: bool
    reasons: list[str] = field(default_factory=list)


def _canonical_tbd_ids() -> set[str]:
    """Parse references/pdpa-current-state.md for canonical OPEN TBD list."""
    ref = REFS / "pdpa-current-state.md"
    if not ref.is_file():
        # Fallback baseline (same as SP3a grade_draft.py).
        return {
            "TBD_PDPC_pending",
            "TBD_PDPC_threshold",
            "TBD_PDPC_timeframe",
            "TBD_PDPC_notification_url",
            "TBD_PDPA_effective_date",
            "TBD_PDPA_audit_framework",
            "TBD_GOV_CLOUD_restrictions",
        }
    text = ref.read_text(encoding="utf-8")
    return set(re.findall(r"TBD_[A-Za-z0-9_]+", text))


def _check_two_files_present(output_dir: Path) -> list[str]:
    errors = []
    legal = output_dir / "legal.md"
    business = output_dir / "business.md"
    if not legal.is_file():
        errors.append(f"missing legal.md in {output_dir.name}")
    if not business.is_file():
        errors.append(f"missing business.md in {output_dir.name}")
    return errors


def _check_byte_counts(legal_text: str, business_text: str) -> list[str]:
    errors = []
    if len(legal_text.encode("utf-8")) < MIN_LEGAL_MD_BYTES:
        errors.append(f"legal.md possibly truncated: {len(legal_text.encode('utf-8'))} bytes (< {MIN_LEGAL_MD_BYTES})")
    if len(business_text.encode("utf-8")) < MIN_BUSINESS_MD_BYTES:
        errors.append(f"business.md possibly truncated: {len(business_text.encode('utf-8'))} bytes (< {MIN_BUSINESS_MD_BYTES})")
    return errors


def _check_timeline_section(legal_text: str) -> list[str]:
    """Legal.md must contain a §時間軸 section header."""
    if "## §時間軸" not in legal_text:
        return ["missing §時間軸 section in legal.md (Q5 ISO timeline required)"]
    return []


def _check_tbd_ids_canonical(*texts: str) -> list[str]:
    canonical = _canonical_tbd_ids()
    used = set()
    for t in texts:
        used.update(re.findall(r"TBD_[A-Za-z0-9_]+", t))
    fabricated = used - canonical
    if fabricated:
        return [f"fabricated TBD id(s) not in canonical OPEN list: {sorted(fabricated)}"]
    return []


def _check_path_a_antipatterns(*texts: str) -> list[str]:
    errors = []
    for text in texts:
        for pattern, why in PATH_A_ANTIPATTERNS:
            match = pattern.search(text)
            if match:
                errors.append(f"Path A violation: matched {match.group(0)!r} — {why}")
    return errors


def _check_pii_breach_specific(legal_text: str) -> list[str]:
    """PII-breach: legal.md must contain PDPC 通報文 + 當事人通知文 + 內部記錄 sections."""
    errors = []
    expected_sections = ["PDPC 通報文", "當事人通知文", "影響範圍", "採取措施"]
    for section in expected_sections:
        if section not in legal_text:
            errors.append(f"pii-breach: missing section reference '{section}' in legal.md")
    return errors


def _check_authority_letter_specific(legal_text: str) -> list[str]:
    """Authority-letter: legal.md must contain 函覆 body + ISO deadline date."""
    errors = []
    # 函覆 body marker (loose check; LLM-generated)
    if "函覆" not in legal_text and "回函" not in legal_text:
        errors.append("authority-letter: missing 函覆/回函 reference in legal.md")
    # ISO date pattern in timeline (at least 1)
    if not re.search(r"\d{4}-\d{2}-\d{2}", legal_text):
        errors.append("authority-letter: missing ISO 8601 date in legal.md timeline (deadline tracking required)")
    return errors


def _check_contract_breach_handoff(output_dir: Path, legal_text: str) -> list[str]:
    """Contract-breach: handoff-context.json must exist + schema-valid; legal.md §3 pointer."""
    errors = []
    handoff_path = output_dir / "handoff-context.json"
    if not handoff_path.is_file():
        errors.append(f"contract-breach: missing handoff-context.json")
        return errors

    try:
        data = json.loads(handoff_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        errors.append(f"contract-breach: handoff-context.json parse error: {e}")
        return errors

    required = ["schema_version", "from_skill", "to_skill", "contract_path",
                "breach_type", "alleged_breach_clauses", "breach_date",
                "discovery_date", "counterparty", "urgency_level"]
    for key in required:
        if key not in data:
            errors.append(f"contract-breach: handoff-context.json missing key '{key}'")

    if "alleged_breach_clauses" in data and not data["alleged_breach_clauses"]:
        errors.append("contract-breach: handoff-context.json alleged_breach_clauses is empty")

    # legal.md must reference legal-contract-review handoff
    if "legal-contract-review" not in legal_text:
        errors.append("contract-breach: legal.md missing pointer to legal-contract-review")

    return errors


def grade_response(output_dir: Path, path_type: str) -> GradeResult:
    reasons: list[str] = []

    if path_type not in PATH_TYPES:
        return GradeResult(passed=False, reasons=[f"unknown path_type: {path_type}"])

    reasons.extend(_check_two_files_present(output_dir))
    if reasons:
        return GradeResult(passed=False, reasons=reasons)

    legal_text = (output_dir / "legal.md").read_text(encoding="utf-8")
    business_text = (output_dir / "business.md").read_text(encoding="utf-8")

    reasons.extend(_check_byte_counts(legal_text, business_text))
    reasons.extend(_check_timeline_section(legal_text))
    reasons.extend(_check_tbd_ids_canonical(legal_text, business_text))
    reasons.extend(_check_path_a_antipatterns(legal_text, business_text))

    if path_type == "pii-breach":
        reasons.extend(_check_pii_breach_specific(legal_text))
    elif path_type == "authority-letter":
        reasons.extend(_check_authority_letter_specific(legal_text))
    elif path_type == "contract-breach":
        reasons.extend(_check_contract_breach_handoff(output_dir, legal_text))

    return GradeResult(passed=not reasons, reasons=reasons)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("usage: grade_response.py <output_dir> <path_type>", file=sys.stderr)
        sys.exit(2)
    result = grade_response(Path(sys.argv[1]), sys.argv[2])
    if result.passed:
        print("OK: structural grading PASS")
        sys.exit(0)
    else:
        for r in result.reasons:
            print(f"FAIL: {r}", file=sys.stderr)
        sys.exit(1)
```

- [ ] **Step 5: Run all tests; expect 13 pass**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/tests/test_grade_response.py -v`
Expected: 13 passed (T-IR-GR-1..13).

Iterate fixtures if any FAIL (likely culprit: fixture missing a section the grader expects).

- [ ] **Step 6: Commit**

Run:
```bash
git add legal-toolkit/skills/legal-incident-response/scripts/grade_response.py \
        legal-toolkit/tests/test_grade_response.py \
        legal-toolkit/tests/fixtures-incident-response/

git commit -m "feat(legal-toolkit): SP3b Phase B/2 — grade_response.py + fixtures

Single grader (grade_response.py) with common structural floor +
per-path branch. PATH_A_ANTIPATTERNS regex bank byte-identical to
SP3a v0.4.1 grade_draft.py (functional duplication per spec §7).

Common floor: 2 files present / byte counts / §時間軸 section /
TBD canonical ids / Path A anti-patterns.
Per-path: PII-breach (expected sections), authority-letter (函覆 body
+ ISO deadline), contract-breach (handoff-context.json schema).

13 unit tests (T-IR-GR-*). Fixtures cover all 3 paths' minimum valid
output dirs.
"
```

---

## Task 4: PII-breach templates (3 templates + statute citations)

**Phase C (1/2).** Author the 3 skeleton templates for PII-breach path (PDPC 通報文 + 當事人通知文 + 內部記錄) + IR-specific statute citations reference. All templates strictly Path A aligned (即時 / 委託-受託 / 民法 §12 = 18 / TBD canonical ids only).

**Files:**
- Create: `legal-toolkit/skills/legal-incident-response/assets/template-pii-breach-pdpc-notification.md`
- Create: `legal-toolkit/skills/legal-incident-response/assets/template-pii-breach-data-subject.md`
- Create: `legal-toolkit/skills/legal-incident-response/assets/template-pii-breach-incident-record.md`
- Create: `legal-toolkit/skills/legal-incident-response/references/statute-citations.md`

- [ ] **Step 1: Create template-pii-breach-pdpc-notification.md (PDPC 通報文)**

Path A discipline: use 即時, NOT 72hr; controller/processor = 委託者/受託者; minor protection = 民法 §12-13 (age 18); SOP numbers only in compliance.md, NOT in this template body.

Content sections: 受文機關 (PDPC 籌備處) / 主旨 / 說明 (事故時間 / 影響範圍 / 採取措施 / 法源依據 = 個資法 §12 + 施行細則 §22) / 後續行動 / 聯絡窗口 (from profile.yml dpo + external_counsel).

Variables: `{{company_name}}` / `{{incident_datetime}}` / `{{affected_count}}` / `{{data_categories_bullets}}` / `{{containment_actions_bullets}}` / `{{dpo_name}}` / `{{dpo_email}}` / `{{external_counsel_block}}` (optional from profile).

HTML comment marker for TBD reference: `<!-- TBD_PDPC_notification_url: 籌備處 URL 未驗證；正式委員會掛牌後 update -->`

- [ ] **Step 2: Create template-pii-breach-data-subject.md (當事人通知文)**

zh-TW only per Q11. Content: 開頭問候 / 事件摘要 / 您的資料是否受影響 / 本公司採取措施 / 您可以做什麼 / 聯絡資訊 / 落款.

Path A markers: 通報語氣「即時」/ NOT GDPR phrases.

Variables: `{{company_name}}` / `{{incident_date}}` / `{{data_categories_affected}}` / `{{containment_actions_consumer_facing}}` / `{{recommended_user_actions}}` / `{{customer_service_contact}}` / `{{dpo_email}}`.

- [ ] **Step 3: Create template-pii-breach-incident-record.md (內部記錄)**

Internal audit document, 不對外。Content: §基本資訊 / §事件分類 + 嚴重度 / §時間軸 (ISO 8601 table with `⏳ 待 X` for未發) / §影響範圍 (筆數 / 個資類別 / 跨境 / 特種個資判斷) / §採取措施 (technical + administrative) / §法源引用 (個資法 §12 / 施行細則 §22 / §27 / 委託-受託 §4 etc.) / §責任分工 (CEO / CTO / DPO / 外部律師 if engaged).

- [ ] **Step 4: Create references/statute-citations.md (IR-specific 法源)**

URL index for IR-relevant statutes. Sourced from `legal-toolkit/scripts/canonical/legal-sources.json` (consistent with SP1 SoT). Include:

- 個資法 §12 (通報義務 — 2025/11 promulgated, 施行日期未定)
- 個資法 施行細則 §22 (即時通報語言基準)
- 民法 §12 / §13 (成年年齡 18 + 限制行為能力)
- 民法 §125 (一般時效 15 年；違約侵權時效 5 年)
- 民法 §227 (不完全給付)
- 民法 §234 (受領遲延)
- 民法 §229 (給付遲延)
- 民法 §250 (違約金約定)
- 公司法 §202 (董事會職權)
- 行政程序法 §49 (主管機關公文書送達時程)

Format mirrors SP3a `references/statute-citations.md` shape.

- [ ] **Step 5: Verify templates render without orphans against test fixtures**

(Smoke test only at this stage; full pipeline tests come in Task 5.) Run grader on Task 3 fixtures to ensure baseline still PASS:

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/tests/test_grade_response.py -v`
Expected: 13 passed (no regression).

- [ ] **Step 6: Commit**

Run:
```bash
git add legal-toolkit/skills/legal-incident-response/assets/template-pii-breach-*.md \
        legal-toolkit/skills/legal-incident-response/references/statute-citations.md

git commit -m "feat(legal-toolkit): SP3b Phase C/1 — PII-breach 3 templates + IR statute citations

PDPC 通報文 skeleton (Path A 即時; controller/processor=委託-受託;
TBD canonical ids only; no SOP numbers in body per spec §6).
當事人通知文 skeleton (zh-TW only per Q11).
內部記錄 skeleton (§時間軸 ISO 8601 + ⏳ for未發生 anchors).
references/statute-citations.md IR-specific (個資法 §12 §22 / 民法
§12-13/§227/§234/§250 / 公司法 §202 / 行政程序法 §49).

13 grader tests still passing (T-IR-GR-* baseline).
"
```

---

## Task 5: PII-breach protocol + compliance checklist + flow narrative

**Phase C (2/2).** Author the LLM-facing protocol for PII-breach pipeline; hand-curated compliance checklist with statute citations; narrative flow reference.

**Files:**
- Create: `legal-toolkit/skills/legal-incident-response/protocols/pii-breach.md`
- Create: `legal-toolkit/skills/legal-incident-response/checklists/compliance-pii-breach.md`
- Create: `legal-toolkit/skills/legal-incident-response/references/ir-pii-breach-flow.md`

- [ ] **Step 1: Create protocols/pii-breach.md**

Pipeline (mirror SP3a `protocols/draft.md` structure):

```
LOAD_PROFILE (delegate to scripts/load_profile.py; reuse from canonical SSOT)
  → SELECT_TEMPLATES (3 templates loaded)
  → SCAN_PROFILE (extract company_name / dpo / external_counsel / regulatory_authorities)
  → ASK_GAPS (incident-specific session vars)
  → MERGE (fill templates with session + profile + safe defaults)
  → ASSEMBLE_LEGAL_MD (consolidate 3 templates + timeline + compliance into single legal.md)
  → ASSEMBLE_BUSINESS_MD
  → COMPLY_CHECK (checklists/compliance-pii-breach.md verdicts)
  → SELF_GRADE (scripts/grade_response.py output_dir pii-breach)
  → OUTPUT
```

Required session vars (ASK_GAPS):
- `incident_datetime` (ISO 8601)
- `discovery_datetime` (ISO 8601)
- `affected_count` (int)
- `data_categories[]` (識別 / 帳務 / 工作往來 / 特種 / 未成年人個資)
- `cross_border_subjects[]` (countries; auto-populate from profile.cross_border_destinations if N/A)
- `containment_actions[]` (free-text bullets)
- `notification_channels[]` (email / SMS / app push / web banner)
- `external_counsel_engaged` (bool; pulls profile.external_counsel if true)
- `severity_level` (minor / moderate / major; user judgement, SOP guidance in compliance.md)

Path A enforcement notes within protocol body:
- Body MUST use「即時」not「72 小時」
- Body MUST cite 「委託者/受託者」 model, NOT controller/processor
- Minor protection MUST cite 民法 §12 = 18 (post-2023 修正)
- SOP numbers (24hr / 1000 affected threshold) ONLY in compliance.md TBD migration section

- [ ] **Step 2: Create checklists/compliance-pii-breach.md**

Hand-curated checklist mirroring SP3a pattern. Sections:

- 個資法 §8 mandatory disclosure (re-applied to incident notification context)
- 個資法 §12 (通報義務) — 即時 verdict
- 施行細則 §22 — 即時 (NOT 72hr GDPR)
- §6 / §9 特種個資 (PASS if not affected; FAIL if affected without 書面同意)
- §21 跨境傳輸 (PASS / N/A)
- §27 安全維護
- 民法 §12-13 (未成年人保護; 滿7歲未滿18歲 — 確認 v0.4.1 lock-in)
- 結構性 (時間軸 ISO date / DPO 聯絡 / 採取措施明列 / Top 3 對外溝通要點)
- TBD migration tracker (canonical ids: TBD_PDPC_timeframe / TBD_PDPC_threshold / TBD_PDPC_notification_url / TBD_PDPA_audit_framework)

Each item: `- [ ] <item> — **{{verdict}}**` template; LLM fills verdict during COMPLY_CHECK.

- [ ] **Step 3: Create references/ir-pii-breach-flow.md**

Narrative reference (NOT protocol). Explains the legal flow + reasoning behind each step in pii-breach pipeline. Useful for LLM that needs to navigate a non-standard incident or explain decisions to user. ~200-300 lines covering:

- 個資法 §12 通報義務全文 + 即時 vs PDPC sub-reg authorization
- 施行細則 §22 「即時」的實務含義
- 委託處理 (§4) 對 PII-breach 通報主體的影響
- 特種個資 (§6) 涉及時的書面同意機制
- §21 跨境傳輸涉及時的告知要點
- §27 安全維護的「應變措施」對應
- 民法 §12-13 未成年人保護 cross-reference
- TBD canonical ids 各代表什麼 + 子法公布時 migration path

- [ ] **Step 4: Verify grader still passes**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/tests/test_grade_response.py -v`
Expected: 13 passed.

- [ ] **Step 5: Commit**

Run:
```bash
git add legal-toolkit/skills/legal-incident-response/protocols/pii-breach.md \
        legal-toolkit/skills/legal-incident-response/checklists/compliance-pii-breach.md \
        legal-toolkit/skills/legal-incident-response/references/ir-pii-breach-flow.md

git commit -m "feat(legal-toolkit): SP3b Phase C/2 — PII-breach protocol + compliance + flow

LLM pipeline (load_profile → templates → ASK_GAPS → MERGE → assemble
legal.md / business.md → COMPLY_CHECK → SELF_GRADE → OUTPUT).
Hand-curated compliance checklist with statute citations (個資法 §8/§12/
§22/§6/§9/§21/§27, 民法 §12-13). TBD migration tracker uses canonical
ids only (no fabrication). Path A enforcement notes inline in protocol.
Narrative flow reference for LLM navigation of edge cases.
"
```

---

## Task 6: Authority-letter path (protocol + checklist)

**Phase D.** Pure-LLM path (no template files; protocol-driven generation from incoming letter).

**Files:**
- Create: `legal-toolkit/skills/legal-incident-response/protocols/authority-letter.md`
- Create: `legal-toolkit/skills/legal-incident-response/checklists/compliance-authority-letter.md`

- [ ] **Step 1: Create protocols/authority-letter.md**

Pipeline:

```
LOAD_PROFILE
  → ASK_GAPS (incoming_letter_text OR incoming_letter_summary /
              incoming_authority / incoming_date (ISO) /
              deadline (ISO) / requested_items[] /
              mode: 函覆 / 補件 / 不服救濟)
  → EXTRACT (LLM reads incoming letter; extracts 主管機關 / 法源依據 /
             要求項目 / deadline structurally)
  → DRAFT (LLM writes 函覆 body following 公文格式:
           - 受文者: <incoming_authority>
           - 主旨: <summary of 函要求>
           - 說明:
             一、來文要求: <verbatim quoting>
             二、本公司回應: <point-by-point>
             三、法源依據: <statute citations from canonical/legal-sources.json>
           - 附件清單 (if any)
           - 落款 (company + DPO + dated))
  → ASSEMBLE_LEGAL_MD (
       §1 incoming 函要求摘要
       §2 時間軸 (ISO 8601: 收文日 / deadline / 我方回函日 / ⏳ for未發)
       §3 函覆草稿
       §4 法源引用清單
       §5 compliance)
  → ASSEMBLE_BUSINESS_MD (
       §1 函要求 1-line summary
       §2 Top 3 即時動作 (回應 / 內部核稿 / 寄出)
       §3 deadline 警示 (red if < 3 day, yellow if < 7 day)
       §4 風險摘要 (refusal/补件 if applicable))
  → COMPLY_CHECK (compliance-authority-letter.md)
  → SELF_GRADE
  → OUTPUT
```

Path A enforcement: 法源引用 必須 in `legal-toolkit/scripts/canonical/legal-sources.json`（不可 LLM invent §number）；deadline ISO date 必填; 函覆 body 不可含「72 小時」「controller/processor」「資料控管者」「未滿二十歲」(同 grader anti-pattern).

- [ ] **Step 2: Create checklists/compliance-authority-letter.md**

Sections:

- 函要求齊備性 (incoming items 是否完整 quote 在 §1 incoming 函要求摘要)
- Deadline ISO date 標示 (PASS if present; FAIL otherwise)
- 法源引用 (PASS if all cited §s in canonical/legal-sources.json; FAIL with list otherwise)
- 主管機關權限對齊 (例如：金管會發函求個資處理事項 — 通常 invalid 因為個資為個資組權限；user judgement + LLM 建議)
- 公文格式 (受文者 / 主旨 / 說明 / 附件 / 落款 五段齊備)
- 對外溝通 (回函若涉及客戶責任 — flag 是否需 PR 同步)

- [ ] **Step 3: Commit**

Run:
```bash
git add legal-toolkit/skills/legal-incident-response/protocols/authority-letter.md \
        legal-toolkit/skills/legal-incident-response/checklists/compliance-authority-letter.md

git commit -m "feat(legal-toolkit): SP3b Phase D — authority-letter path

Pure-LLM protocol (no template files). EXTRACT incoming 函要求 →
DRAFT 函覆 (公文格式: 受文者/主旨/說明/附件/落款) → ASSEMBLE legal.md
+ business.md → COMPLY_CHECK → SELF_GRADE → OUTPUT.

Path A enforcement: 法源引用 only from canonical/legal-sources.json
(no LLM-invented §s); ISO 8601 deadline required; PATH_A_ANTIPATTERNS
checked by grade_response.py.

Compliance checklist: 函要求齊備 / deadline ISO / 法源 valid /
主管機關權限對齊 / 公文格式 / 對外溝通 flag.
"
```

---

## Task 7: Contract-breach delegate path (template + protocol + checklist)

**Phase E.** Thin classifier + handoff JSON emitter. Does NOT auto-invoke legal-contract-review.

**Files:**
- Create: `legal-toolkit/skills/legal-incident-response/assets/template-contract-breach-handoff.json`
- Create: `legal-toolkit/skills/legal-incident-response/protocols/contract-breach-delegate.md`
- Create: `legal-toolkit/skills/legal-incident-response/checklists/compliance-contract-breach.md`

- [ ] **Step 1: Create assets/template-contract-breach-handoff.json**

JSON template + schema (schema_version 1 — locked in spec §5 / §6.3):

```json
{
  "schema_version": 1,
  "from_skill": "legal-incident-response",
  "to_skill": "legal-contract-review",
  "contract_path": "{{contract_path}}",
  "breach_type": "{{breach_type}}",
  "alleged_breach_clauses": "{{alleged_breach_clauses}}",
  "breach_date": "{{breach_date}}",
  "discovery_date": "{{discovery_date}}",
  "counterparty": {
    "name": "{{counterparty_name}}",
    "company_id": "{{counterparty_company_id}}",
    "contact_email": "{{counterparty_contact_email}}"
  },
  "damages_estimate_twd": "{{damages_estimate_twd}}",
  "urgency_level": "{{urgency_level}}",
  "session_ref": "{{session_ref}}",
  "notes": "{{notes}}"
}
```

Note: this is a template (not a JSON Schema). LLM fills `{{}}` placeholders during MERGE. Grader (Task 3) validates the rendered output has all required keys.

- [ ] **Step 2: Create protocols/contract-breach-delegate.md**

Pipeline:

```
LOAD_PROFILE
  → ASK_GAPS (contract_path /
              breach_type (free-text initial) /
              breach_date (ISO) /
              discovery_date (ISO) /
              counterparty (name + optional company_id + contact_email) /
              alleged_breach_clauses[] (e.g., ["§3.2", "§4.4"]) /
              damages_estimate_twd? (optional) /
              urgency_level: high/moderate/low)
  → CLASSIFY_BREACH_TYPE
      (LLM judges from breach_type free-text + alleged_breach_clauses →
       map to 民法 article:
         §227 不完全給付 — partial / defective performance
         §225 給付不能 — impossibility
         §234 受領遲延 — creditor's delay
         §229 給付遲延 — debtor's delay (most common)
         §259 解除契約 — rescission
       Output: breach_type updated to canonical 民法 § + label)
  → RENDER_HANDOFF (fill template-contract-breach-handoff.json with
                    session vars + classified breach_type)
  → ASSEMBLE_LEGAL_MD (
       §1 違約 classification (民法 § + 違約類型 + 條款引用)
       §2 §時間軸 (簽約日 / 違約發生日 / 我方知悉日 / 催告日 ⏳ if 未發 / 解除日 ⏳ if 未發)
       §3 §Handoff to legal-contract-review:
         - contract_path: <path>
         - 請執行: /legal-contract-review --contract <path>
         - 可選 seed file: legal-outputs/<this-session>/handoff-context.json
         - 預期 contract-review 將跑 L0-L7 七層分析
       §4 compliance (handoff completeness verdicts))
  → ASSEMBLE_BUSINESS_MD (
       §1 違約事件 1-句
       §2 Top 3 即時動作:
         1. 保存證據 (合約 + 違約事實 records + 對方所有通訊)
         2. 聯絡對方確認違約事實 (避免事實爭執)
         3. 評估救濟方式 (催告 / 解除 / 賠償 / 訴訟) — 推 contract-review 深度分析
       §3 後續流程 (轉 legal-contract-review → 法務分析 → 救濟決定 → 寄發催告函)
       §4 deadline 警示 (民法 §125 一般時效 15 年；§197 侵權時效 2 年；§125 / §126 / §197 相應))
  → COMPLY_CHECK (compliance-contract-breach.md)
  → SELF_GRADE
  → OUTPUT (legal.md + business.md + handoff-context.json)
```

Cross-skill explicit notes:
- ❌ SP3b does NOT auto-invoke contract-review
- ❌ SP3b does NOT do deep clause extraction (contract-review's L2-L7 territory)
- ✅ SP3b emits handoff-context.json + clear "next step" pointer in legal.md §3
- ✅ User manually invokes contract-review subsequently

- [ ] **Step 3: Create checklists/compliance-contract-breach.md**

Sections:

- 違約 classification 對齊民法 article (PASS if classify_breach_type emitted valid 民法 §; FAIL otherwise)
- 時間軸 ISO date completeness (signing date / breach date / discovery date — 3 required; 催告 / 解除 dates optional ⏳)
- alleged_breach_clauses 非空 (PASS if ≥ 1 clause cited)
- handoff-context.json schema (10 required keys per template-contract-breach-handoff.json)
- legal.md §3 pointer (PASS if contains "legal-contract-review" string)
- 民法 §125 / §197 時效 acknowledged in business.md (deadline 警示)

- [ ] **Step 4: Verify grader catches missing handoff**

Run the test from Task 3:
`PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/tests/test_grade_response.py::test_contract_breach_missing_handoff_fails -v`
Expected: PASS (this was already covered in Task 3).

- [ ] **Step 5: Commit**

Run:
```bash
git add legal-toolkit/skills/legal-incident-response/assets/template-contract-breach-handoff.json \
        legal-toolkit/skills/legal-incident-response/protocols/contract-breach-delegate.md \
        legal-toolkit/skills/legal-incident-response/checklists/compliance-contract-breach.md

git commit -m "feat(legal-toolkit): SP3b Phase E — contract-breach delegate path

Thin classifier + handoff JSON template + protocol + checklist. Does
NOT auto-invoke legal-contract-review (user manual接力 per Q8).

Pipeline: LOAD_PROFILE → ASK_GAPS → CLASSIFY_BREACH_TYPE (map to 民法
§227/§225/§234/§229/§259 etc.) → RENDER_HANDOFF (handoff-context.json)
→ ASSEMBLE legal.md (§1 classify / §2 時間軸 / §3 handoff pointer /
§4 compliance) + business.md (Top 3 即時動作 + 民法 §125/§197 時效) →
COMPLY_CHECK → SELF_GRADE → OUTPUT.

Compliance checklist enforces 民法 § classification valid, 時間軸 ISO,
handoff-context.json schema, legal.md pointer to contract-review.
"
```

---

## Task 8: SKILL.md full body + router activation + version bump

**Phase F (1/2).** Author the production-ready SKILL.md (replacing Task 1 stub); activate Q5 dispatch in router; bump version 0.4.1 → 0.4.2; sync marketplace description.

**Files:**
- Modify: `legal-toolkit/skills/legal-incident-response/SKILL.md` (full body)
- Modify: `legal-toolkit/skills/using-legal-toolkit/SKILL.md` (activate Q5 dispatch)
- Modify: `legal-toolkit/.claude-plugin/plugin.json` (version + description)
- Modify: `.claude-plugin/marketplace.json` (description sync)

- [ ] **Step 1: Author SKILL.md full body**

Replace Task 1's stub SKILL.md with full body. Structure:

```markdown
---
name: legal-incident-response
description: [unchanged from Task 1 — already production-grade description]
---

# legal-incident-response

[Brief 1-paragraph intro: who this is for + 3 paths + Path A discipline alignment]

## Paths

- **個資外洩 (pii-breach)** — [1 line]
- **主管機關函覆 (authority-letter)** — [1 line]
- **合約違約 (contract-breach)** — [1 line; mention delegation to legal-contract-review]

## Pipeline

[Brief reference to protocols/classify-path.md → per-path sub-protocol → output. Mirror SP3a SKILL.md §Pipeline section length]

## Inputs

- Required: `legal-playbook/profile.yml` (v2 schema; backward-compat v1)
- Required at session: incident free-text description (or explicit `--type` override)
- Optional: profile.external_counsel + profile.regulatory_authorities

## Outputs

[2-file always; +handoff-context.json for contract-breach]

## Quality gates

- `scripts/load_profile.py` (functional copy from canonical/) validates profile
- `scripts/grade_response.py` deterministic structural + Path A anti-pattern checks
- Hand-curated per-path checklists with statute citations

## Limitations (v0.4.2 scope per spec §9)

- Path A: tracks current in-force Taiwan law only
- 違約 path = thin delegator; contract-review owns deep analysis
- zh-TW only; no multi-language
- No auto-invocation of contract-review from SP3b
- No legal-playbook clauses for IR (defer to v0.4.3)

## Cross-skill

- Shares profile.yml with `legal-document-draft` (canonical/ SSOT)
- Hands off to `legal-contract-review` via handoff-context.json (Soft delegation; user manually invokes)
- References `canonical/legal-sources.json` for statute URLs

## References

- Spec: `docs/superpowers/specs/2026-05-13-legal-toolkit-sp3b-incident-response-design.md`
- SP2 ground truth: `legal-toolkit/research/2026-05-12-pdpa-2025-11-verify.md`
- Classifier protocol: `protocols/classify-path.md`
- Per-path protocols: `protocols/pii-breach.md` / `protocols/authority-letter.md` / `protocols/contract-breach-delegate.md`
- Grader: `scripts/grade_response.py`
- ROADMAP: `legal-toolkit/ROADMAP.md`
```

Keep total SKILL.md body under 200 lines per CLAUDE.md convention (~6000 token target). Mirror SP3a SKILL.md style.

- [ ] **Step 2: Activate Q5 dispatch in router**

Read `legal-toolkit/skills/using-legal-toolkit/SKILL.md`; find where Q2/Q3/Q4 dispatches are described; add Q5 entry following the same pattern. The Q5 dispatch routes "事件 / incident / 應變 / 違約 / 函覆" queries to `legal-incident-response`.

Example entry (adapt to actual router style):

```markdown
### Q5 — 事件 / 應變 / 違約 / 函覆

If user describes a happened incident (個資外洩 / 主管機關來函 / 對方違約):

→ Dispatch to **`legal-incident-response`** skill
→ skill 自動 classify path + confirm
```

- [ ] **Step 3: Bump version + description append**

Edit `legal-toolkit/.claude-plugin/plugin.json`:

- Version: `0.4.1` → `0.4.2`
- Description: append paragraph at end (before closing `",`):

```
v0.4.2 Phase 2 closeout ships legal-incident-response (3-path classifier — 個資外洩 / 主管機關函覆 / 合約違約): auto-classify + confirm path routing; audience-shaped 2-file output (legal.md + business.md) with optional handoff-context.json for contract-breach delegation; ISO 8601 timeline section with ⏳ markers for未發 anchors; mixed per-path authoring (PII skeleton+LLM / Authority pure-LLM / Contract-breach delegate); single grade_response.py per-path branch sharing Path A anti-pattern bank with v0.4.1 SP3a; profile.yml schema v1 → v2 (+2 optional fields external_counsel + regulatory_authorities; backward-compat v1 profiles); legal-toolkit/scripts/canonical/ SSOT extends to cover pdpa-current-state.md + tbd-migration-template.md + profile-schema.yml + load_profile.py (distributed to both legal-document-draft + legal-incident-response functional copies via distribute.py); router Q5 dispatch activated; contract-breach 違約 path delegates to legal-contract-review via handoff-context.json (soft delegation; user manually invokes; --seed flag consumption deferred to v0.4.3); zh-TW only (multi-language via translation-toolkit). Closes Phase 2 of legal-toolkit ROADMAP (累計 5 skills active: router + playbook-author + contract-review + document-draft + incident-response). Phase 3 IRAC cluster (legal-issue-spot + legal-research) is next.
```

- [ ] **Step 4: Sync marketplace.json**

Edit `.claude-plugin/marketplace.json` legal-toolkit `description` field to byte-match plugin.json description (per CI sync check).

- [ ] **Step 5: Verify marketplace sync**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-marketplace-description-sync.py 2>&1 | tail -3`
Expected: `OK: 15 plugin description(s) in sync` (or similar; exit 0).

- [ ] **Step 6: Run full pytest**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/ -q 2>&1 | tail -5`
Expected: 240+ passed (201 v0.4.1 + 13 grader + 5 classifier + Task 1 drift = ~220+ if no other test changes).

- [ ] **Step 7: Verify drift on canonical/**

Run: `PYTHONDONTWRITEBYTECODE=1 python3 legal-toolkit/scripts/verify-drift.py`
Expected: exit 0.

- [ ] **Step 8: Commit**

Run:
```bash
git add legal-toolkit/skills/legal-incident-response/SKILL.md \
        legal-toolkit/skills/using-legal-toolkit/SKILL.md \
        legal-toolkit/.claude-plugin/plugin.json \
        .claude-plugin/marketplace.json

git commit -m "feat(legal-toolkit): SP3b Phase F/1 — SKILL.md body + router + version bump

Full SKILL.md body for legal-incident-response (paths / pipeline /
inputs / outputs / quality gates / limitations / cross-skill / refs).

Router Q5 dispatch activated (using-legal-toolkit) — incident /
應變 / 違約 / 函覆 queries route to legal-incident-response.

Plugin v0.4.1 → v0.4.2; description appended with SP3b summary +
canonical SSOT extension note; marketplace.json description synced.
"
```

---

## Task 9: Tri-lang READMEs + ROADMAP update

**Phase F (2/2).** Per PR #150 convention, every skill ships README en/ja/zh-TW. Also update plugin-level READMEs + ROADMAP.

**Files:**
- Create: `legal-toolkit/skills/legal-incident-response/README.md` (en)
- Create: `legal-toolkit/skills/legal-incident-response/README.ja.md`
- Create: `legal-toolkit/skills/legal-incident-response/README.zh-TW.md`
- Modify: `legal-toolkit/README.md` (version badge)
- Modify: `legal-toolkit/README.ja.md` (version badge)
- Modify: `legal-toolkit/README.zh-TW.md` (version badge)
- Modify: `legal-toolkit/ROADMAP.md` (Phase 2 v0.4.2 marked DONE)

- [ ] **Step 1: Author skill-level READMEs (3 languages)**

Each README ~80-120 lines mirroring SP3a's `legal-document-draft/README.md` structure:
- Language switcher line at top
- Version badge
- Disclaimer (`⚠️ Not legal advice`)
- §What it does (3 paths summarized)
- §When to use / §When NOT to use
- §How to use (router invocation + per-path examples)
- §Inputs / §Outputs (point to spec section + actual file paths)
- §Quality gates (load_profile + grade_response + checklists)
- §Limitations (Path A scope, 違約 delegation, zh-TW only)
- §Related skills (links to document-draft / contract-review / Phase 3+ planned)
- §References (spec / ROADMAP / SP2 research note)

Use English for skill instructions; zh-TW for domain content (per PR #166 + #150 conventions).

- [ ] **Step 2: Update plugin-level READMEs version badge**

Edit `legal-toolkit/README.md` / `README.ja.md` / `README.zh-TW.md`:
- version: `0.4.1` → `0.4.2`
- phase: `2_Template_dogfooded` → `2_Closeout` (or similar — `2_IR_shipped`)

- [ ] **Step 3: Update ROADMAP.md**

Edit `legal-toolkit/ROADMAP.md`:

In Timeline overview (line 19-37 area):
- Change row `2 SP3b  0.4.2   🔜 next` → `✅ DONE` (or similar)

In §Phase 2 section:
- Update header: `v0.4.0 SP3a ship 2026-05-13；v0.4.1 dogfood patches ship 2026-05-13；v0.4.2 SP3b IR ship 2026-05-13` (now Phase 2 fully DONE)
- Replace v0.4.2 (SP3b) ✅ entry with full DONE block similar to v0.4.0 / v0.4.1 entries

In §版本策略 table:
- Update v0.4.2 row from `🔜 pending` to ship note (mirror v0.4.0 / v0.4.1 entry style)

Also update overall status header: "Phase 2 (v0.4.2) — 5 skills active" / next phase ready (Phase 3 v0.5.0 IRAC cluster).

- [ ] **Step 4: Run full lint + tests**

Run:
```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/ -q 2>&1 | tail -5
PYTHONDONTWRITEBYTECODE=1 python3 legal-toolkit/scripts/verify-drift.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-marketplace-description-sync.py 2>&1 | tail -3
```

Expected: all pass / exit 0.

- [ ] **Step 5: Commit**

Run:
```bash
git add legal-toolkit/skills/legal-incident-response/README.md \
        legal-toolkit/skills/legal-incident-response/README.ja.md \
        legal-toolkit/skills/legal-incident-response/README.zh-TW.md \
        legal-toolkit/README.md \
        legal-toolkit/README.ja.md \
        legal-toolkit/README.zh-TW.md \
        legal-toolkit/ROADMAP.md

git commit -m "feat(legal-toolkit): SP3b Phase F/2 — READMEs + ROADMAP

Skill-level tri-lang READMEs (en/ja/zh-TW per PR #150 convention) for
legal-incident-response — 3 paths summarized, inputs/outputs/limitations
documented, related skills linked.

Plugin-level README version badges 0.4.1 → 0.4.2; phase label updated.

ROADMAP §Phase 2 marked DONE for v0.4.2 SP3b — closes legal-toolkit
Phase 2 program. §版本策略 v0.4.2 row updated. Phase 3 v0.5.0 IRAC
cluster (legal-issue-spot + legal-research) is next.
"
```

---

## Task 10: PR creation (open as draft for review)

**Phase F (3/3).** Open PR; let CI run; user reviews diff before squash-merge.

**Files:** none (push + PR ops only)

- [ ] **Step 1: Verify branch state + status**

Run:
```bash
git log --oneline origin/main..HEAD
git status --short
```
Expected: ~9 commits on this branch (one per task); clean working tree.

- [ ] **Step 2: Push branch**

Run: `git push -u origin <branch-name>`

Expected: branch created on origin.

- [ ] **Step 3: Open PR with detailed body**

Run via `gh pr create --title "feat(legal-toolkit): v0.4.2 — SP3b legal-incident-response (Phase 2 closeout)" --body "$(cat <<'EOF' ... EOF)"`:

PR body sections:
- ## Summary (1-paragraph; 3-path classifier; Path A discipline; closes Phase 2)
- ## Locked decisions table (Q1-Q12 condensed)
- ## File changes summary (count of new / modified / moved files)
- ## Test plan (240+ tests pass / verify-drift exit 0 / marketplace sync OK)
- ## Cross-skill compatibility (SP3a backward-compat verified after canonical SSOT migration)
- ## Memory (Decision / Learning / Gotcha trailers — sourced from individual commit trailers)
- ## Related (PR #279 v0.4.1, PR #277 v0.4.0, spec commit cdd1167)

- [ ] **Step 4: Wait for CI**

Run: `gh pr checks <pr#> --watch`

Expected: all 9+ checks green within 1-2 min.

- [ ] **Step 5: Notify user with PR URL**

After CI green, surface PR URL to user. Wait for user merge action (per CLAUDE.md: don't push to main without explicit ask).

---

## Task 11: Post-PR dogfood plan (separate session)

**Phase G.** NOT part of this PR; documented here for handoff to next session.

After v0.4.2 PR is merged, user should run a separate dogfood session to verify the skill behavior:

1. **PII-breach scenario** — provide a hypothetical incident description (e.g., "今天早上發現 API endpoint 暴露導致 8000 筆用戶資料外洩"). Verify:
   - Classifier matches `pii-breach` with HIGH confidence
   - ASK_GAPS collects ISO datetime + affected_count + data_categories etc.
   - Generated legal.md contains all 3 sections (PDPC 通報文 / 當事人通知文 / 內部記錄)
   - PDPC 通報文 body uses 即時 (NOT 72 小時)
   - Timeline ISO dates present + ⏳ for未發
   - compliance.md migration tracker references TBD canonical ids only
   - grade_response.py exit 0

2. **Authority-letter scenario** — provide a hypothetical 金管會 letter requesting 7-day reply on a 資安事件. Verify:
   - Classifier matches `authority-letter` with HIGH confidence
   - ASK_GAPS collects incoming text + deadline ISO
   - Generated 函覆 references the specific items in incoming letter
   - 法源引用 valid against canonical/legal-sources.json
   - business.md deadline 警示 colored correctly
   - grade_response.py exit 0

3. **Findings & v0.4.3 patch list** — write audit doc similar to `docs/superpowers/audits/2026-05-13-legal-document-draft-sp3a-dogfood.md`. Capture any P0/P1 issues found; queue v0.4.3 patches.

---

## Self-Review Notes

**Spec coverage verified:**
- §1 Goal → Task 1-9
- §2 Why → Task 11 (dogfood) verifies the Path A reframe was correct
- §3 Locked decisions Q1-Q12 → all addressed across tasks
- §4 Architecture pipeline → Tasks 2 (classifier), 5 (PII protocol), 6 (Authority protocol), 7 (Breach protocol), 8 (SKILL.md ties it together)
- §5 File layout → Task 1 (canonical), Tasks 2-9 (per-skill files)
- §6 Per-path protocols → Tasks 5, 6, 7
- §7 Grader → Task 3
- §8 Quality gates → grader (Task 3) + checklists (Tasks 5, 6, 7) + CI (Task 10)
- §9 Out-of-scope → documented in SKILL.md (Task 8) + ROADMAP (Task 9)
- §10 Migration path → documented in compliance.md TBD migration sections (Tasks 5, 6) + canonical/tbd-migration-template.md (Task 1)
- §11 Implementation plan → this document

**Placeholder scan: clean** (one strategic "TBD canonical name" inline note in Task 1 Step 1 — refers to actually identifying the existing test file; expected to be `test_distribute.py` based on SP1 pattern).

**Type consistency: verified** — `ClassifyResult` / `GradeResult` / `PATH_TYPES` / `PATH_A_ANTIPATTERNS` consistently named across Tasks 2, 3, and grade_response.py file body.

**No subagent will need to context-search beyond:** spec + this plan + the current codebase state (which is the v0.4.1 baseline). Each task has full file paths + code blocks + commit commands.

**Estimated total tests:** 201 (v0.4.1) + ~13 (T-IR-GR-*) + ~5 (T-IR-CL-*) + ~6-8 (T-IR-LP-* + T-V-* extension for canonical) = **~225-230 tests** (target stated 240+ — minor undershoot OK; spec said "240+ tests total" was an aspirational rough number; actuals are LLM-protocol-driven (markdown) which don't have direct unit tests).

**Estimated effort:** 3-4 days subagent-driven (~30-50 min per task with two-stage review per memory pattern).
