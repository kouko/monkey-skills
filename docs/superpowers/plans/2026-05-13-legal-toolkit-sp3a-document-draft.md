# legal-toolkit SP3a — `legal-document-draft` v0.4.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `legal-document-draft` skill that drafts new legal documents (privacy / ToS / DPA / NDA) from company profile + playbook + per-session inputs, with hand-curated per-mode compliance checklists and deterministic structural grading, against current in-force Taiwan law (Path A from SP2).

**Architecture:** Plugin-level scripts (`scripts/load_profile.py` + `scripts/grade_draft.py`) under `legal-toolkit/skills/legal-document-draft/`; per-mode skeleton templates + hand-curated checklists in flat subfolders; profile lives at user-visible `legal-playbook/profile.yml`; LLM-executed protocol DAG (`protocols/draft.md`) orchestrates load_profile → select_template → scan_playbook → ask_gaps → merge → comply_check → self_grade → output to `legal-outputs/<timestamp>-<mode>/`.

**Tech Stack:** Python 3.11 stdlib (`pathlib`, `yaml` via `pyyaml`, `jsonschema`, `subprocess`), pytest. Markdown templates with `{{variable}}` placeholders. JSON Schema 2020-12 for profile validation. No new dependencies.

**Branch:** `feat/legal-toolkit-sp3a-document-draft` (already created on top of latest `origin/main`; SP3a spec committed as `b0db821`).

**Spec:** [docs/superpowers/specs/2026-05-13-legal-toolkit-sp3a-document-draft-design.md](../specs/2026-05-13-legal-toolkit-sp3a-document-draft-design.md)

**Dependency on SP2 (PR #273)**: this plan's content-authoring tasks reference statute citations + safe defaults sourced from SP2's research note (`legal-toolkit/research/2026-05-12-pdpa-2025-11-verify.md`). If SP2 hasn't merged into main by implementation time, rebase SP3a on top of SP2 branch first (or have implementer pull the research note from SP2 PR #273).

---

## File Structure

**Created — skill directory** (`legal-toolkit/skills/legal-document-draft/`):
- `SKILL.md` — skill entrypoint with frontmatter + protocol summary
- `README.md` / `README.ja.md` / `README.zh-TW.md` — tri-language user docs (PR #150 convention)
- `assets/template-privacy.md` — privacy policy skeleton
- `assets/template-tos.md` — ToS skeleton
- `assets/template-dpa.md` — DPA skeleton
- `assets/template-nda.md` — NDA skeleton
- `assets/profile-schema.yml` — JSON Schema for `legal-playbook/profile.yml`
- `assets/output-schema.json` — output directory contract
- `checklists/compliance-privacy.md` — 15 items aligned to 個資法 §8 八款 + §9 + §21 + 施行細則 §22 + §27
- `checklists/compliance-tos.md` — 12 items (民法 + 消保法 §11-1 + §17 + 公平交易法)
- `checklists/compliance-dpa.md` — 10 items (個資法 §4 + §8 + 施行細則 §12)
- `checklists/compliance-nda.md` — 7 items (民法 + 商業慣例)
- `protocols/draft.md` — main DAG protocol
- `protocols/grade.md` — deterministic structural grading steps
- `scripts/load_profile.py` — profile.yml reader + schema validator
- `scripts/grade_draft.py` — output directory grader (deterministic)
- `references/pdpa-current-state.md` — SP2 ground truth summary
- `references/tbd-migration-template.md` — Phase 2.5 patch guide
- `references/statute-citations.md` — central URL index

**Created — plugin-level tests** (`legal-toolkit/tests/`):
- `test_load_profile.py` (4 tests T-P-1..4)
- `test_grade_draft.py` (6 tests T-G-1..6)
- `fixtures-document-draft/profile-minimal.yml`
- `fixtures-document-draft/profile-full.yml`
- `fixtures-document-draft/draft-output-sample-privacy/` (synthetic sample for grade tests)
  - `privacy.md` + `compliance.md`

**Modified**:
- `legal-toolkit/skills/using-legal-toolkit/SKILL.md` — activate Q2 dispatch path for "起草 / draft / write a..."
- `legal-toolkit/.claude-plugin/plugin.json` — version `0.3.6` → `0.4.0`, description appended with Phase 2 v0.4.0 note
- `.claude-plugin/marketplace.json` — sync description
- `legal-toolkit/ROADMAP.md` — Phase 1.10 → Phase 2 transition, mark Phase 2 split into v0.4.0 (draft) + v0.4.1 (IR)

**NOT touched** (out of scope per spec §13):
- `legal-toolkit/skills/legal-contract-review/` (NDA collision resolved via shared `legal-playbook/confidentiality.md`)
- `legal-toolkit/skills/legal-playbook-author/`
- `legal-toolkit/scripts/canonical/` (no canonical/ extension for SP3a)

---

## Task 1: Skeleton scaffold + SKILL.md + tri-language READMEs

**Files:**
- Create: `legal-toolkit/skills/legal-document-draft/SKILL.md`
- Create: `legal-toolkit/skills/legal-document-draft/README.md`
- Create: `legal-toolkit/skills/legal-document-draft/README.ja.md`
- Create: `legal-toolkit/skills/legal-document-draft/README.zh-TW.md`
- Create: empty placeholder dirs `assets/` `checklists/` `protocols/` `scripts/` `references/` (via touch + .gitkeep removed at later tasks)

- [ ] **Step 1: Create skill directory structure**

```bash
mkdir -p legal-toolkit/skills/legal-document-draft/{assets,checklists,protocols,scripts,references}
```

- [ ] **Step 2: Write `SKILL.md`**

`legal-toolkit/skills/legal-document-draft/SKILL.md`:

```markdown
---
name: legal-document-draft
description: Draft new Taiwan-law legal documents (privacy policy / ToS / DPA / NDA) from company profile + negotiation playbook + per-session inputs. Skeleton-and-LLM-fill templates pinned to current in-force 個資法 + 民法 + 消保法 + 公平交易法; hand-curated per-mode compliance checklists with statute citations; deterministic structural grading; safe defaults for items deferred to PDPC 子法 (Phase 2.5 patch path documented in compliance.md TBD migration section). Outputs 2 files per session — <doc-type>.md (publish-ready) + compliance.md (法務 internal review) — into legal-outputs/<timestamp>-<mode>/. Cross-references legal-playbook/ for variable defaults; uses legal-playbook/profile.yml as the single source of company identity shared across legal-toolkit skills.
---

# legal-document-draft

In-house legal toolkit drafting skill for Taiwan SME → 上市櫃 法務. Generates **new** legal documents (the company's own privacy policy / ToS / DPA / NDA) from a 4-mode template library, with current-Taiwan-law statute citations and deterministic structural verification.

## Modes

- **privacy** — 隱私權政策 / 個資告知事項 (個資法 §8 + §9 + §21 + 施行細則 §22)
- **tos** — Terms of Service / 服務條款 (民法 + 消保法 §11-1 / §17 + 公平交易法)
- **dpa** — Data Processing Agreement / 委託處理協議 (個資法 §4 + §8 + 施行細則 §12)
- **nda** — Non-Disclosure Agreement / 保密協議 (民法 + 商業慣例)

## Pipeline

`protocols/draft.md` orchestrates: LOAD_PROFILE → SELECT_TEMPLATE → SCAN_PLAYBOOK → ASK_GAPS → MERGE → COMPLY_CHECK → SELF_GRADE → OUTPUT.

## Inputs

- **Required**: `legal-playbook/profile.yml` (validated against `assets/profile-schema.yml`)
- **Required at session**: mode flag + per-mode session variables (collected via ASK_GAPS)
- **Optional**: `legal-playbook/<clause>.md` (playbook supplies stance defaults for variables; session can override)

## Outputs

Per session, writes 2 files to `legal-outputs/<timestamp>-<mode>/`:
- `<doc-type>.md` — publish-ready Markdown document; safe defaults inline for items deferred to PDPC 子法 (e.g., breach notification timeframe = "即時")
- `compliance.md` — 法務 internal review: hand-curated checklist with PASS / FAIL / TBD_<reason> verdicts + TBD migration tracking (instructions for upgrading when PDPC sub-regulations land)

## Quality gates

- `scripts/load_profile.py` validates `legal-playbook/profile.yml` against `assets/profile-schema.yml` before draft starts; missing required fields halt with explicit message
- `scripts/grade_draft.py` runs deterministic structural checks on the output directory: no orphan `{{variable}}`, all checklist items have verdicts, no fabricated TBDs (must match canonical OPEN list from `references/pdpa-current-state.md`), document.md exceeds minimum byte count
- Hand-curated compliance checklists (per mode) ground the COMPLY_CHECK step in primary-source statute references

## Limitations (current scope per spec §13)

- Path A: tracks current in-force Taiwan law only; GDPR-style features (controller/processor split, 72hr breach window) are NOT included
- 2025/11 PDPA amendments are tracked as TBD in compliance.md migration sections; templates use current施行細則 §22 "即時" language until PDPC 子法 publishes specific timeframes
- Minor protection: cites 民法 §12-13 (not invented PDPA-specific age threshold)
- 5th mode (員工合約 / 服務契約 / 採購合約 / SLA): YAGNI per spec §13; add when user demand emerges

## Cross-skill

- Shares `legal-playbook/confidentiality.md` stance with `legal-contract-review nda` mode (draft generates new; review redlines existing)
- Reads `legal-playbook/profile.yml` (created and maintained by user; skill does NOT auto-modify)
- References `legal-toolkit/skills/legal-contract-review/assets/legal-sources.json` URL templates **at template authoring time** (templates hardcode URLs); NOT a runtime dependency

## References

- Spec: `docs/superpowers/specs/2026-05-13-legal-toolkit-sp3a-document-draft-design.md`
- SP2 ground truth: `legal-toolkit/research/2026-05-12-pdpa-2025-11-verify.md`
- TBD migration guide: `references/tbd-migration-template.md`
- Statute URL index: `references/statute-citations.md`
- Plugin spec: `legal-toolkit/PRODUCT-SPEC.md` + `legal-toolkit/TECH-SPEC.md`
- Roadmap: `legal-toolkit/ROADMAP.md`
```

- [ ] **Step 3: Write `README.md` (English)**

`legal-toolkit/skills/legal-document-draft/README.md`:

```markdown
# legal-document-draft

Drafts new Taiwan-law legal documents (privacy / ToS / DPA / NDA) from a company profile + negotiation playbook.

## Quick start

1. Ensure `legal-playbook/profile.yml` exists in your repo (see `assets/profile-schema.yml` for the schema)
2. Optionally maintain `legal-playbook/<clause>.md` files for stance defaults
3. Invoke via the `using-legal-toolkit` router by asking to "draft a privacy policy" / "write an NDA" / etc.
4. The skill asks for session-specific variables (product name, data categories, SDK list, etc.) interactively
5. Output appears at `legal-outputs/<timestamp>-<mode>/`:
   - `<doc-type>.md` — publish-ready document
   - `compliance.md` — 法務 review with checklist verdicts + TBD migration

## Modes

| Mode | Document | Primary statutes |
|---|---|---|
| privacy | 隱私權政策 / 個資告知事項 | 個資法 §8, §9, §21, 施行細則 §22, §27 |
| tos | Terms of Service / 服務條款 | 民法, 消保法 §11-1 + §17, 公平交易法 |
| dpa | 委託處理協議 | 個資法 §4 + §8, 施行細則 §12 |
| nda | 保密協議 | 民法 §227, §247-1, §250, 商業慣例 |

## TBD migration

Items deferred to PDPC 子法 (e.g., specific breach notification timeframe, reporting threshold) appear as TBD entries in `compliance.md`. The `references/tbd-migration-template.md` documents the patch path when PDPC sub-regulations land — typically a `<10-line edit to `assets/template-*.md` + `checklists/compliance-*.md`.

## Not in scope

- Drafting GDPR-style documents (Path A is Taiwan-current-law only; see spec §3 + §13)
- Reviewing existing documents — use `legal-contract-review` instead
- Auto-monitoring PDPC for sub-regulation publication — manual monitoring sufficient at low publication frequency

## See also

- `legal-contract-review` — review counterparty drafts (NDA / SaaS / etc.)
- `legal-playbook-author` — author the negotiation stances draft consumes
```

- [ ] **Step 4: Write `README.ja.md` (Japanese)**

`legal-toolkit/skills/legal-document-draft/README.ja.md`:

```markdown
# legal-document-draft

台湾法務に基づき、新規の法律文書（プライバシーポリシー / 利用規約 / DPA / NDA）を、会社プロフィール + 交渉プレイブックから生成します。

## クイックスタート

1. リポジトリに `legal-playbook/profile.yml` を用意（スキーマは `assets/profile-schema.yml` 参照）
2. 必要に応じて `legal-playbook/<clause>.md` でスタンスのデフォルトを管理
3. `using-legal-toolkit` ルーター経由で「プライバシーポリシーをドラフトして」「NDA を書いて」と依頼
4. セッション固有の変数（製品名・個人情報項目・SDK 一覧など）を対話的に収集
5. 出力先: `legal-outputs/<timestamp>-<mode>/`
   - `<doc-type>.md` — 公開可能なドキュメント
   - `compliance.md` — 法務内部レビュー（チェックリスト判定 + TBD 移行ガイド）

## モード

| モード | 文書 | 主要法令 |
|---|---|---|
| privacy | 隱私權政策 / 個資告知事項 | 個資法 §8, §9, §21, 施行細則 §22, §27 |
| tos | 利用規約 | 民法, 消保法 §11-1 + §17, 公平交易法 |
| dpa | 委託処理契約 | 個資法 §4 + §8, 施行細則 §12 |
| nda | 機密保持契約 | 民法 §227, §247-1, §250, 商習慣 |

## TBD 移行

PDPC 子法に委ねられた項目（具体的通報時限・通報基準値など）は `compliance.md` の TBD エントリとして残ります。PDPC 子法公布後の更新手順は `references/tbd-migration-template.md` に記載（typically `assets/template-*.md` と `checklists/compliance-*.md` への 10 行未満の編集）。

## 対象外

- GDPR スタイルの文書生成（Path A により台湾現行法のみ扱う；spec §3 + §13 参照）
- 既存文書のレビュー — `legal-contract-review` を使用
- PDPC 子法公布の自動監視 — 頻度が低いため手動監視で十分

## 関連

- `legal-contract-review` — 相手方ドラフトのレビュー（NDA / SaaS など）
- `legal-playbook-author` — draft が参照する交渉スタンスの作成
```

- [ ] **Step 5: Write `README.zh-TW.md` (Traditional Chinese)**

`legal-toolkit/skills/legal-document-draft/README.zh-TW.md`:

```markdown
# legal-document-draft

依台灣法源起草新法律文件（隱私權政策 / 服務條款 / DPA / NDA），結合公司 profile + 談判 playbook。

## 快速上手

1. 確保 repo 根 `legal-playbook/profile.yml` 存在（schema 見 `assets/profile-schema.yml`）
2. 視需要維護 `legal-playbook/<clause>.md` 給談判立場預設值
3. 透過 `using-legal-toolkit` router 請求「起草隱私權政策」「寫一份 NDA」等
4. skill 互動詢問當次需要的變數（產品名 / 個資類別 / SDK 清單 等）
5. 輸出寫到 `legal-outputs/<timestamp>-<mode>/`
   - `<doc-type>.md` — 可上線文件
   - `compliance.md` — 法務內部 review（checklist 判定 + TBD 遷移指南）

## 4 個 mode

| Mode | 文件 | 主要法源 |
|---|---|---|
| privacy | 隱私權政策 / 個資告知事項 | 個資法 §8, §9, §21, 施行細則 §22, §27 |
| tos | 服務條款 | 民法, 消保法 §11-1 + §17, 公平交易法 |
| dpa | 委託處理協議 | 個資法 §4 + §8, 施行細則 §12 |
| nda | 保密協議 | 民法 §227, §247-1, §250, 商業慣例 |

## TBD 遷移

PDPC 子法授權的項目（具體通報時限 / 通報門檻）以 TBD 形式留在 `compliance.md`。PDPC 子法發布後的 patch 步驟在 `references/tbd-migration-template.md`（通常是 `assets/template-*.md` + `checklists/compliance-*.md` 10 行內編輯）。

## 不在範圍內

- 起草 GDPR-style 文件（Path A 只處理台灣現行法；spec §3 + §13 詳述）
- 審閱既有文件 — 改用 `legal-contract-review`
- 自動監視 PDPC 子法發布 — 頻率低，手動 monitor 即可

## 相關

- `legal-contract-review` — 審閱對方提供的草案（NDA / SaaS / etc.）
- `legal-playbook-author` — 撰寫 draft 引用的談判立場
```

- [ ] **Step 6: Verify dir structure + commit**

```bash
ls legal-toolkit/skills/legal-document-draft/
# Expected: SKILL.md README.md README.ja.md README.zh-TW.md assets/ checklists/ protocols/ scripts/ references/
```

- [ ] **Step 7: Commit**

```bash
git add legal-toolkit/skills/legal-document-draft/
git commit -m "$(cat <<'EOF'
feat(legal-toolkit): legal-document-draft skill skeleton (SP3a Task 1)

Scaffolding only — SKILL.md frontmatter (mode list / pipeline summary /
inputs/outputs / quality gates / cross-skill notes / limitations) +
tri-language READMEs per PR #150 convention + 5 empty subfolder dirs
(assets, checklists, protocols, scripts, references). All templates +
checklists + protocols + scripts populated in subsequent tasks.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: profile-schema + load_profile.py + 4 tests (T-P-1..4)

**Files:**
- Create: `legal-toolkit/skills/legal-document-draft/assets/profile-schema.yml`
- Create: `legal-toolkit/skills/legal-document-draft/scripts/load_profile.py`
- Create: `legal-toolkit/tests/test_load_profile.py`
- Create: `legal-toolkit/tests/fixtures-document-draft/profile-minimal.yml`
- Create: `legal-toolkit/tests/fixtures-document-draft/profile-full.yml`

- [ ] **Step 1: Write JSON Schema (yaml-formatted) at `assets/profile-schema.yml`**

```yaml
# JSON Schema 2020-12 for legal-playbook/profile.yml
$schema: "https://json-schema.org/draft/2020-12/schema"
$id: "legal-document-draft://profile-schema.yml"
title: Legal Toolkit Company Profile
description: |
  Company identity profile shared across legal-toolkit skills (draft, IR,
  future corp-governance, dd-quickscan). Lives at legal-playbook/profile.yml
  (user-visible, git-tracked).

type: object
required:
  - schema_version
  - company_name
  - company_id
  - registered_address
  - general_contact
  - dpo

properties:
  schema_version:
    type: integer
    const: 1
    description: Schema version; bump on breaking changes
  company_name:
    type: string
    minLength: 2
    description: Official 公司名稱 (Chinese)
  company_name_en:
    type: string
    description: English company name (optional)
  company_id:
    type: string
    pattern: "^[0-9]{8}$"
    description: 統一編號 (8 digits)
  registered_address:
    type: string
    minLength: 5
  general_contact:
    type: object
    required: [email]
    properties:
      email:
        type: string
        format: email
      phone:
        type: string
  dpo:
    type: object
    required: [name, email]
    description: Data Protection Officer (個資法 §22 推定承辦人)
    properties:
      name:
        type: string
      email:
        type: string
        format: email
  business_scope:
    type: array
    items: { type: string }
  cross_border_destinations:
    type: array
    items:
      type: object
      required: [country, purpose]
      properties:
        country: { type: string }
        purpose: { type: string }
  security_measures:
    type: array
    items: { type: string }
  governing_law:
    type: object
    properties:
      default_jurisdiction: { type: string }
      preferred_court: { type: string }
  last_updated:
    type: string
    format: date
  maintained_by:
    type: string

additionalProperties: false
```

- [ ] **Step 2: Write test fixtures**

`legal-toolkit/tests/fixtures-document-draft/profile-minimal.yml`:

```yaml
schema_version: 1
company_name: 範例股份有限公司
company_id: "12345678"
registered_address: 台北市信義區信義路五段7號
general_contact:
  email: contact@example.com
dpo:
  name: 王小明
  email: dpo@example.com
```

`legal-toolkit/tests/fixtures-document-draft/profile-full.yml`:

```yaml
schema_version: 1
company_name: 範例股份有限公司
company_name_en: Example Inc.
company_id: "12345678"
registered_address: 台北市信義區信義路五段7號
general_contact:
  email: contact@example.com
  phone: +886-2-1234-5678
dpo:
  name: 王小明
  email: dpo@example.com
business_scope:
  - SaaS 雲端服務
  - 訂閱式軟體
cross_border_destinations:
  - country: US
    purpose: AWS 雲端託管
  - country: JP
    purpose: 客服外包
security_measures:
  - TLS 1.3 in transit
  - AES-256 at rest
  - Annual ISO 27001 audit
governing_law:
  default_jurisdiction: 中華民國
  preferred_court: 臺灣臺北地方法院
last_updated: "2026-05-13"
maintained_by: 法務部
```

- [ ] **Step 3: Write failing tests at `legal-toolkit/tests/test_load_profile.py`**

```python
"""Tests for legal-document-draft/scripts/load_profile.py.

load_profile.py reads legal-playbook/profile.yml + validates against the
JSON Schema at legal-document-draft/assets/profile-schema.yml. Schema
validation uses jsonschema (Draft 2020-12).
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "legal-toolkit" / "skills" / "legal-document-draft" / "scripts"
FIXTURES = REPO / "legal-toolkit" / "tests" / "fixtures-document-draft"


def _load_module(filename: str):
    spec = importlib.util.spec_from_file_location("load_profile", SCRIPTS / filename)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------- T-P-1: minimal valid
def test_minimal_profile_loads_and_validates(tmp_path):
    load_profile = _load_module("load_profile.py")

    profile_path = FIXTURES / "profile-minimal.yml"
    result = load_profile.load_profile(profile_path)

    assert result.valid is True
    assert result.data["company_name"] == "範例股份有限公司"
    assert result.data["company_id"] == "12345678"
    assert result.data["dpo"]["email"] == "dpo@example.com"
    assert result.errors == []


# ---------------------------------------------------------- T-P-2: full profile
def test_full_profile_loads_and_validates():
    load_profile = _load_module("load_profile.py")

    profile_path = FIXTURES / "profile-full.yml"
    result = load_profile.load_profile(profile_path)

    assert result.valid is True
    assert len(result.data["cross_border_destinations"]) == 2
    assert result.data["governing_law"]["preferred_court"] == "臺灣臺北地方法院"
    assert result.errors == []


# ---------------------------------------------------------- T-P-3: missing required
def test_missing_dpo_email_fails_validation(tmp_path):
    load_profile = _load_module("load_profile.py")

    bad = tmp_path / "bad-profile.yml"
    bad.write_text(
        """
schema_version: 1
company_name: 缺 DPO 的公司
company_id: "12345678"
registered_address: 台北市
general_contact:
  email: contact@example.com
dpo:
  name: 沒填 email
""",
        encoding="utf-8",
    )

    result = load_profile.load_profile(bad)

    assert result.valid is False
    assert any("email" in err.lower() for err in result.errors), (
        f"Expected an error mentioning 'email', got: {result.errors}"
    )


# ---------------------------------------------------------- T-P-4: schema version mismatch
def test_schema_version_mismatch_fails(tmp_path):
    load_profile = _load_module("load_profile.py")

    bad = tmp_path / "version-mismatch.yml"
    bad.write_text(
        """
schema_version: 99
company_name: 版本錯誤
company_id: "12345678"
registered_address: 台北市
general_contact:
  email: contact@example.com
dpo:
  name: x
  email: x@example.com
""",
        encoding="utf-8",
    )

    result = load_profile.load_profile(bad)

    assert result.valid is False
    assert any("schema_version" in err for err in result.errors), (
        f"Expected schema_version error, got: {result.errors}"
    )
```

- [ ] **Step 4: Run tests to verify they FAIL**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/tests/test_load_profile.py -v
```

Expected: 4 tests FAIL with `ModuleNotFoundError` or path-not-found (load_profile.py doesn't exist yet).

- [ ] **Step 5: Implement `scripts/load_profile.py`**

```python
#!/usr/bin/env python3
"""Load and validate legal-playbook/profile.yml against profile-schema.yml.

Public API:
    load_profile(profile_path: Path) -> LoadResult

LoadResult fields:
    valid: bool          True iff schema validation passed
    data: dict           parsed YAML; empty dict if file unreadable
    errors: list[str]    human-readable validation errors

Usage from a skill protocol:
    from load_profile import load_profile
    r = load_profile(Path("legal-playbook/profile.yml"))
    if not r.valid:
        for err in r.errors:
            print(f"profile.yml validation error: {err}")
        sys.exit(2)
    company = r.data["company_name"]
    ...
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import jsonschema
import yaml

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "assets" / "profile-schema.yml"


@dataclass
class LoadResult:
    valid: bool
    data: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


def _load_schema() -> dict:
    return yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_profile(profile_path: Path) -> LoadResult:
    if not profile_path.is_file():
        return LoadResult(valid=False, errors=[f"profile file not found: {profile_path}"])

    try:
        data = yaml.safe_load(profile_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        return LoadResult(valid=False, errors=[f"YAML parse error: {e}"])

    schema = _load_schema()
    validator = jsonschema.Draft202012Validator(schema)
    errors = []
    for err in validator.iter_errors(data):
        path = ".".join(str(p) for p in err.absolute_path) or "<root>"
        errors.append(f"{path}: {err.message}")

    return LoadResult(valid=not errors, data=data, errors=errors)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("usage: load_profile.py <path/to/profile.yml>", file=sys.stderr)
        sys.exit(2)
    result = load_profile(Path(sys.argv[1]))
    if result.valid:
        print(f"OK: profile valid; company={result.data.get('company_name')}")
        sys.exit(0)
    else:
        for err in result.errors:
            print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(1)
```

- [ ] **Step 6: Run tests to verify they PASS**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/tests/test_load_profile.py -v
```

Expected: 4/4 PASS.

- [ ] **Step 7: Commit**

```bash
git add legal-toolkit/skills/legal-document-draft/assets/profile-schema.yml \
        legal-toolkit/skills/legal-document-draft/scripts/load_profile.py \
        legal-toolkit/tests/test_load_profile.py \
        legal-toolkit/tests/fixtures-document-draft/
git commit -m "$(cat <<'EOF'
feat(legal-toolkit): profile-schema + load_profile.py (SP3a Task 2)

JSON Schema 2020-12 declaration for legal-playbook/profile.yml +
Python loader/validator + 4 tests (T-P-1..4: minimal valid / full
valid / missing dpo.email / schema_version mismatch). Shared profile
location feeds draft / IR / corp-governance / dd-quickscan skills.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: grade_draft.py + 6 tests (T-G-1..6)

**Files:**
- Create: `legal-toolkit/skills/legal-document-draft/scripts/grade_draft.py`
- Create: `legal-toolkit/skills/legal-document-draft/assets/output-schema.json`
- Create: `legal-toolkit/tests/test_grade_draft.py`
- Create: `legal-toolkit/tests/fixtures-document-draft/draft-output-sample-privacy/` (synthetic sample)

- [ ] **Step 1: Write output-schema.json (declares output directory contract)**

`legal-toolkit/skills/legal-document-draft/assets/output-schema.json`:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "legal-document-draft://output-schema.json",
  "title": "legal-document-draft output directory contract",
  "description": "Each draft session writes exactly 2 files: <doc-type>.md (publish-ready) + compliance.md (法務 review). Directory: legal-outputs/<timestamp>-<mode>/",
  "type": "object",
  "required": ["files", "mode"],
  "properties": {
    "files": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 2,
      "maxItems": 2
    },
    "mode": {
      "type": "string",
      "enum": ["privacy", "tos", "dpa", "nda"]
    }
  },
  "additionalProperties": false
}
```

- [ ] **Step 2: Write synthetic sample at `fixtures-document-draft/draft-output-sample-privacy/`**

Create two files in that directory.

`fixtures-document-draft/draft-output-sample-privacy/privacy.md`:

```markdown
# 隱私權政策

本政策由 範例股份有限公司 制定，依個資法 §8 揭露相關事項。

## 1. 蒐集者身分

公司名稱：範例股份有限公司
聯絡：dpo@example.com

## 2. 蒐集目的

提供 SaaS 雲端服務、訂閱管理、客戶支援。

## 3. 蒐集個資類別

身分識別資料 (姓名/email/手機)、帳務資料、使用紀錄。

## 4. 利用期間、地區、對象、方式

期間：服務存續期間 + 終止後 5 年。地區：US (AWS) + JP (客服外包)。

## 5. 當事人權利

依個資法 §3 行使查詢/更正/刪除/停止處理/異議權，聯絡 dpo@example.com。

## 6. 不提供影響

未提供必要個資將無法使用本服務。

## 7. 跨境傳輸

US (AWS 雲端託管) / JP (客服外包) — 已採適當保護措施。

## 8. 個資外洩通報

本公司將於發現個資外洩事件時，依個資法相關規定**即時**通報主管機關。

## 9. 安全維護

TLS 1.3 加密傳輸、AES-256 加密儲存、ISO 27001 年度稽核。

## 10. 修訂與生效

本政策自 2026-05-13 生效。修訂時將公告於本網站。
```

`fixtures-document-draft/draft-output-sample-privacy/compliance.md`:

```markdown
# Privacy mode — compliance review

## Checklist verdicts

- [x] §8 第一項第一款 — 公開揭露蒐集者 (公司) 名稱 — **PASS**
- [x] §8 第一項第二款 — 公開揭露蒐集目的 — **PASS**
- [x] §8 第一項第三款 — 公開揭露個資類別 — **PASS**
- [x] §8 第一項第四款 — 公開揭露利用期間 / 地區 / 對象 / 方式 — **PASS**
- [x] §8 第一項第五款 — 公開揭露當事人權利 — **PASS**
- [x] §8 第一項第六款 — 公開揭露當事人不提供之影響 — **PASS**
- [x] §9 — 特種個資處理機制 — **PASS** (no special-category data collected)
- [x] §21 — 跨境傳輸揭露 — **PASS**
- [x] 施行細則 §22 — 個資外洩通報使用「即時」語句 — **PASS**
- [x] §27 — 安全維護措施 — **PASS**
- [ ] §20-1 — Audit framework 段落 — **TBD_PDPC_pending** (Art. 20-1 promulgated 2025-11-11; 施行日期未定)

## TBD migration

- **TBD_PDPC_pending — Art. 20-1 audit framework**: monitor PDPC announcements; when 施行日期 set + sub-regs published, add audit-framework section to §9 安全維護. See `references/tbd-migration-template.md`.
```

- [ ] **Step 3: Write failing tests at `legal-toolkit/tests/test_grade_draft.py`**

```python
"""Tests for legal-document-draft/scripts/grade_draft.py.

grade_draft.py runs deterministic structural checks on an output
directory and emits PASS / FAIL with a reason list.
"""
from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "legal-toolkit" / "skills" / "legal-document-draft" / "scripts"
FIXTURES = REPO / "legal-toolkit" / "tests" / "fixtures-document-draft"
SAMPLE = FIXTURES / "draft-output-sample-privacy"


def _load():
    spec = importlib.util.spec_from_file_location("grade_draft", SCRIPTS / "grade_draft.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _copy_sample(tmp_path: Path) -> Path:
    target = tmp_path / "2026-05-13T120000-privacy"
    shutil.copytree(SAMPLE, target)
    return target


# ---------------------------------------------------------- T-G-1: complete draft PASS
def test_complete_draft_passes(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path)

    result = grade.grade_draft(output_dir, mode="privacy")

    assert result.passed is True, f"expected PASS, got reasons: {result.reasons}"


# ---------------------------------------------------------- T-G-2: unresolved variable FAIL
def test_orphan_variable_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path)
    doc = output_dir / "privacy.md"
    doc.write_text(doc.read_text(encoding="utf-8") + "\n\n## 11. 額外 {{unfilled_section}}", encoding="utf-8")

    result = grade.grade_draft(output_dir, mode="privacy")

    assert result.passed is False
    assert any("orphan" in r.lower() or "{{" in r for r in result.reasons)


# ---------------------------------------------------------- T-G-3: missing verdict FAIL
def test_missing_checklist_verdict_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path)
    compliance = output_dir / "compliance.md"
    # Strip one PASS verdict from a checklist line
    text = compliance.read_text(encoding="utf-8")
    text = text.replace("§8 第一項第一款 — 公開揭露蒐集者 (公司) 名稱 — **PASS**", "§8 第一項第一款 — 公開揭露蒐集者 (公司) 名稱")
    compliance.write_text(text, encoding="utf-8")

    result = grade.grade_draft(output_dir, mode="privacy")

    assert result.passed is False
    assert any("verdict" in r.lower() for r in result.reasons)


# ---------------------------------------------------------- T-G-4: fabricated TBD FAIL
def test_fabricated_tbd_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path)
    compliance = output_dir / "compliance.md"
    text = compliance.read_text(encoding="utf-8")
    # Insert a TBD that doesn't match the canonical OPEN list
    text = text.replace(
        "- [ ] §20-1 — Audit framework 段落 — **TBD_PDPC_pending**",
        "- [ ] §99 — 某虛構條文 — **TBD_FABRICATED_ITEM**",
    )
    compliance.write_text(text, encoding="utf-8")

    result = grade.grade_draft(output_dir, mode="privacy")

    assert result.passed is False
    assert any("tbd" in r.lower() and ("fabricated" in r.lower() or "canonical" in r.lower()) for r in result.reasons)


# ---------------------------------------------------------- T-G-5: truncated document FAIL
def test_truncated_document_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path)
    doc = output_dir / "privacy.md"
    doc.write_text("# 隱私權政策\n\n太短了。", encoding="utf-8")  # < min_bytes

    result = grade.grade_draft(output_dir, mode="privacy")

    assert result.passed is False
    assert any("truncat" in r.lower() or "byte" in r.lower() for r in result.reasons)


# ---------------------------------------------------------- T-G-6: missing output file
def test_missing_output_file_fails(tmp_path):
    grade = _load()
    output_dir = _copy_sample(tmp_path)
    (output_dir / "compliance.md").unlink()

    result = grade.grade_draft(output_dir, mode="privacy")

    assert result.passed is False
    assert any("compliance" in r.lower() and ("missing" in r.lower() or "not found" in r.lower()) for r in result.reasons)
```

- [ ] **Step 4: Run tests to verify they FAIL**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/tests/test_grade_draft.py -v
```

Expected: 6 FAIL with `ModuleNotFoundError` / file-not-found (grade_draft.py doesn't exist).

- [ ] **Step 5: Implement `scripts/grade_draft.py`**

```python
#!/usr/bin/env python3
"""Deterministic structural grader for legal-document-draft output directories.

A grader run checks an output dir at legal-outputs/<timestamp>-<mode>/ and
verifies:
    1. Both expected files exist (<doc-type>.md + compliance.md)
    2. <doc-type>.md has no orphan {{variable}} placeholders
    3. compliance.md has a verdict for every checklist item
       (each "- [ ]" or "- [x]" line ends with **PASS** | **FAIL** | **TBD_<id>**)
    4. Every TBD_* id used in compliance.md is in the canonical OPEN list
       (sourced from references/pdpa-current-state.md)
    5. <doc-type>.md byte-count > MIN_DOC_BYTES (catches truncated LLM runs)

Public API:
    grade_draft(output_dir: Path, mode: str) -> GradeResult

GradeResult:
    passed: bool
    reasons: list[str]     reasons for failure (empty if passed)
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

REFS = Path(__file__).resolve().parent.parent / "references"
MIN_DOC_BYTES = 500
DOC_FILENAME = {"privacy": "privacy.md", "tos": "tos.md", "dpa": "dpa.md", "nda": "nda.md"}


@dataclass
class GradeResult:
    passed: bool
    reasons: list[str] = field(default_factory=list)


def _canonical_tbd_ids() -> set[str]:
    """Parse references/pdpa-current-state.md for the canonical OPEN list.

    Looks for lines of the form `- **TBD_<id>** ...` to enumerate the
    valid TBD identifiers. Falls back to a hardcoded baseline list if
    the references file is missing (e.g., during early skill scaffolding).
    """
    ref = REFS / "pdpa-current-state.md"
    if not ref.is_file():
        return {"TBD_PDPC_pending", "TBD_PDPC_threshold", "TBD_PDPC_notification_url"}
    text = ref.read_text(encoding="utf-8")
    return set(re.findall(r"TBD_[A-Za-z0-9_]+", text))


def _check_no_orphans(doc_text: str) -> list[str]:
    matches = re.findall(r"\{\{[^}]+\}\}", doc_text)
    if matches:
        return [f"orphan template placeholder(s) in doc: {sorted(set(matches))[:5]}"]
    return []


def _check_checklist_verdicts(compliance_text: str) -> list[str]:
    """Every `- [ ]` or `- [x]` line should end with a verdict marker."""
    errors = []
    verdict_pattern = re.compile(r"\*\*(PASS|FAIL|TBD_[A-Za-z0-9_]+)\*\*")
    for i, line in enumerate(compliance_text.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("- [ ]") or stripped.startswith("- [x]") or stripped.startswith("- [X]"):
            if not verdict_pattern.search(line):
                errors.append(f"checklist line {i} has no verdict (PASS/FAIL/TBD_<id>): {stripped[:80]}")
    return errors


def _check_tbd_ids_match_canonical(compliance_text: str) -> list[str]:
    canonical = _canonical_tbd_ids()
    used = set(re.findall(r"TBD_[A-Za-z0-9_]+", compliance_text))
    fabricated = used - canonical
    if fabricated:
        return [f"fabricated TBD id(s) not in canonical OPEN list: {sorted(fabricated)}"]
    return []


def grade_draft(output_dir: Path, mode: str) -> GradeResult:
    reasons: list[str] = []

    if mode not in DOC_FILENAME:
        return GradeResult(passed=False, reasons=[f"unknown mode: {mode}"])

    doc_path = output_dir / DOC_FILENAME[mode]
    compliance_path = output_dir / "compliance.md"

    if not doc_path.is_file():
        reasons.append(f"missing document: {doc_path.name}")
    if not compliance_path.is_file():
        reasons.append(f"missing compliance.md")

    if reasons:
        return GradeResult(passed=False, reasons=reasons)

    doc_text = doc_path.read_text(encoding="utf-8")
    compliance_text = compliance_path.read_text(encoding="utf-8")

    if len(doc_text.encode("utf-8")) < MIN_DOC_BYTES:
        reasons.append(f"possible truncation: {doc_path.name} is {len(doc_text.encode('utf-8'))} bytes (< {MIN_DOC_BYTES})")

    reasons.extend(_check_no_orphans(doc_text))
    reasons.extend(_check_checklist_verdicts(compliance_text))
    reasons.extend(_check_tbd_ids_match_canonical(compliance_text))

    return GradeResult(passed=not reasons, reasons=reasons)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("usage: grade_draft.py <output_dir> <mode>", file=sys.stderr)
        sys.exit(2)
    result = grade_draft(Path(sys.argv[1]), sys.argv[2])
    if result.passed:
        print("OK: structural grading PASS")
        sys.exit(0)
    else:
        for r in result.reasons:
            print(f"FAIL: {r}", file=sys.stderr)
        sys.exit(1)
```

- [ ] **Step 6: Run tests to verify they PASS**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/tests/test_grade_draft.py -v
```

Expected: 6/6 PASS.

- [ ] **Step 7: Commit**

```bash
git add legal-toolkit/skills/legal-document-draft/assets/output-schema.json \
        legal-toolkit/skills/legal-document-draft/scripts/grade_draft.py \
        legal-toolkit/tests/test_grade_draft.py \
        legal-toolkit/tests/fixtures-document-draft/draft-output-sample-privacy/
git commit -m "$(cat <<'EOF'
feat(legal-toolkit): grade_draft.py + 6 tests (SP3a Task 3)

Deterministic structural grader for legal-document-draft outputs.
Checks: (1) both files present (<doc-type>.md + compliance.md);
(2) no orphan {{variable}} in doc; (3) every checklist line has a
PASS/FAIL/TBD_<id> verdict; (4) every TBD id used matches the
canonical OPEN list in references/pdpa-current-state.md; (5) doc
byte-count > 500 to catch LLM truncation. 6 tests cover happy path
+ 5 failure modes. Sample fixture (privacy mode) provides ground
truth for grader tests.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: References — pdpa-current-state + tbd-migration + statute-citations

**Files:**
- Create: `legal-toolkit/skills/legal-document-draft/references/pdpa-current-state.md`
- Create: `legal-toolkit/skills/legal-document-draft/references/tbd-migration-template.md`
- Create: `legal-toolkit/skills/legal-document-draft/references/statute-citations.md`

- [ ] **Step 1: Write `references/pdpa-current-state.md`**

This file is the offline-readable summary of SP2 research findings (see `legal-toolkit/research/2026-05-12-pdpa-2025-11-verify.md` for full source). It MUST list the canonical TBD_* ids used by grade_draft.py.

```markdown
# PDPA Current State (SP2 ground truth summary)

> **Source**: `legal-toolkit/research/2026-05-12-pdpa-2025-11-verify.md` (SP2 PR #273)
> **Verified**: 2026-05-12 against 全國法規資料庫 + PDPC + 法務部 (Tier-A primary sources)
> **Scope**: Items used by `legal-document-draft` templates + checklists. Full per-item analysis in SP2 research note.

## Currently in force (HIGH confidence)

- 個資法 §3 — 當事人權利 (查詢 / 更正 / 刪除 / 停止處理 / 異議)
- §4 — 委託處理 + 委託者全責
- §5 — 利用範圍
- §6 — 特種個資限制
- §7-9 — 蒐集 / 處理 / 利用 + 第三人提供告知
- §8 第一項 一至六款 — 個資告知事項 (mandatory disclosure items in privacy policy)
- §11 — 個資保管期間 / 正確性
- §21 — 跨境傳輸 (主管機關公告限制)
- §22 — 主管機關職權 (DPO 推定承辦人)
- §27 — 安全維護措施 (現行)
- §47-48 — 行政罰 (pre-2025 amendment tier; new tier in 2025/11 not yet effective)
- 施行細則 §22 — 個資外洩通報「即時」(safe default for breach notification timeframe; NOT 72hr GDPR)
- 民法 §12-13 — 行為能力 (used for minor protection; NOT a PDPA-specific provision)
- 民法 §227 / §247-1 / §250 — 違約 / 定型化檢視 / 違約金
- 消保法 §11-1 — 等候期 / §17 — 定型化契約
- 公平交易法 — 不公平競爭

## Promulgated 2025-11-11 but NOT yet effective (TBD pending Executive Yuan announcement of 施行日期)

The following exist in the official law text but Art. 1-2 / 20-1 / 21-1~5 / 12 / 47-48 (new tier) are 施行日期未定. Templates use safe defaults; compliance.md tracks via TBD entries.

## Canonical TBD OPEN list

Templates and checklists may emit only the following TBD identifiers in `compliance.md`. `grade_draft.py` rejects any TBD id not in this list as "fabricated":

- **TBD_PDPC_pending** — PDPC 籌備處 → 正式委員會 transition; notification mechanism unverified
- **TBD_PDPC_threshold** — 通報範圍 (numeric / categorical trigger; Art. 12 §2 一定通報範圍授權子法)
- **TBD_PDPC_timeframe** — 通報時限具體小時數 (Art. 12 §4 sub-regulations)
- **TBD_PDPC_notification_url** — 正式通報入口 URL (form / email / paper); pdpc.gov.tw 籌備處 site JS-rendered, body unverified
- **TBD_PDPA_effective_date** — Executive Yuan announcement of 2025/11 batch 施行日期
- **TBD_PDPA_audit_framework** — Art. 20-1 audit framework (promulgated, 施行日期未定)
- **TBD_GOV_CLOUD_restrictions** — 政府機關雲端服務 mainland-China-restriction specifics (likely 政府採購法 / 資通安全管理法, not PDPA-specific; needs Tier-A primary source verification before locking)

## Out of scope for this skill (Path A boundary)

- GDPR 72hr / controller-processor / minor age threshold — NOT in current Taiwan PDPA
- HKSAR / Singapore / EU privacy laws — international expansion is a future Phase
- 2025/11 amendments-as-effective — assume promulgated-but-not-yet-effective until行政院 announcement

## Update path

When PDPC sub-regulations publish, follow `tbd-migration-template.md` to patch templates + checklists. Each TBD id has an associated migration entry.
```

- [ ] **Step 2: Write `references/tbd-migration-template.md`**

```markdown
# TBD migration template — Phase 2.5 patch guide

When PDPC sub-regulations or 行政院 announcements resolve a TBD item, follow this guide to patch templates + checklists. Each entry below corresponds to a canonical TBD id in `pdpa-current-state.md`.

## TBD_PDPC_pending

**Current state**: PDPC remains 籌備處 (preparatory office); no operational notification mechanism verified.

**Trigger to update**: PDPC website (www.pdpc.gov.tw) transitions from 籌備處 to 正式委員會; or 法務部 announces operational date.

**Patch action**:
1. Update `pdpc_status` in `legal-toolkit/scripts/canonical/legal-sources.json` from "籌備處" to "正式委員會"
2. Run `python3 legal-toolkit/scripts/distribute.py`
3. Edit `assets/template-privacy.md` and `assets/template-dpa.md` — update 個資外洩通報 section if specific mechanism announced
4. Edit `checklists/compliance-privacy.md` + `checklists/compliance-dpa.md` — replace TBD_PDPC_pending with PASS criteria
5. Bump skill version per Phase 2.5 patch convention
6. Update `references/pdpa-current-state.md` — move TBD_PDPC_pending from OPEN list to RESOLVED section

## TBD_PDPC_threshold

**Current state**: Art. 12 §2 通報範圍 undefined; "一定通報範圍" 由主管機關公告。

**Trigger to update**: PDPC publishes 通報辦法 (likely under 個資法施行細則 §12 expansion).

**Patch action**:
1. Read PDPC 通報辦法 to extract numeric / categorical thresholds
2. Edit `assets/template-privacy.md` Section 8 — replace safe-default language with threshold-aware language
3. Edit `checklists/compliance-privacy.md` — replace TBD_PDPC_threshold with PASS criteria for "threshold disclosure in privacy policy"
4. Same for `assets/template-dpa.md` (DPA mode references mirroring obligation)

## TBD_PDPC_timeframe

**Current state**: 施行細則 §22 says "即時"; specific hour-count授權 sub-reg.

**Trigger to update**: PDPC publishes 通報辦法 specifying timeframe (likely 72hr or 24hr).

**Patch action**:
1. Edit `assets/template-privacy.md` Section 8 — replace "即時" with specific timeframe (e.g., "於發現後 X 小時內")
2. Edit `assets/template-dpa.md` — same for 受託人 → 委託人 notification
3. Edit `checklists/compliance-privacy.md` — update §22 verdict criteria
4. Update `references/pdpa-current-state.md` — note the locked timeframe

## TBD_PDPC_notification_url

**Current state**: pdpc.gov.tw 籌備處 site JS-rendered; notification form / email / URL not extracted.

**Trigger to update**: PDPC publishes operational notification entry (form / hotline / portal).

**Patch action**:
1. Read PDPC announcement to extract notification URL / form / email
2. Update `pdpc_url` in `legal-toolkit/scripts/canonical/legal-sources.json` to the operational entry (not just the homepage)
3. Run `python3 legal-toolkit/scripts/distribute.py`
4. Edit `assets/template-privacy.md` + `assets/template-dpa.md` — embed the operational URL in通報 contact section

## TBD_PDPA_effective_date

**Current state**: 2025/11 amendments promulgated 2025-11-11; 施行日期未定 (set by行政院).

**Trigger to update**: 行政院 announces 施行日期 in 行政院公報.

**Patch action**:
1. Update `amendment_note` in `legal-toolkit/scripts/canonical/legal-sources.json` to "公布 2025-11-11; 施行 YYYY-MM-DD"
2. Run `python3 legal-toolkit/scripts/distribute.py`
3. For each affected article (Art. 12 / 20-1 / 21-1~5 / 47-48), audit templates + checklists: if the new article is now in force, replace safe-default text with the new statutory language
4. Re-run draft on in-use documents (privacy / dpa) to validate the migration
5. Phase 2.5 release notes documenting the new effective date

## TBD_PDPA_audit_framework

**Current state**: Art. 20-1 audit framework promulgated, not effective.

**Trigger to update**: When Art. 20-1 effective date arrives + PDPC publishes 稽核辦法.

**Patch action**:
1. Edit `assets/template-privacy.md` §9 安全維護 — add audit-framework subsection per Art. 20-1
2. Edit `checklists/compliance-privacy.md` — add new checklist items for audit framework
3. Update `references/pdpa-current-state.md` to move Art. 20-1 from "promulgated not yet effective" to "in force"

## TBD_GOV_CLOUD_restrictions

**Current state**: Mainland-China cloud / ICT restrictions for government scope likely live in 政府採購法 / 資通安全管理法, NOT PDPA per Mondaq guide; not Tier-A verified in SP2.

**Trigger to update**: Sourced primary statute located (e.g., 行政院 procurement 法規 specific article).

**Patch action**:
1. Add government-procurement-relevant statute to `legal-toolkit/scripts/canonical/legal-sources.json` `statute_sources`
2. Run `python3 legal-toolkit/scripts/distribute.py`
3. Edit `assets/template-tos.md` (if SaaS service has 政府 customer scope) — add 政府採購注意 section
4. Edit `checklists/compliance-tos.md` — add new checklist item

## How to add a new TBD

If implementation discovers a new deferred item not in this list:
1. Add a row to `references/pdpa-current-state.md` "Canonical TBD OPEN list"
2. Add a corresponding migration block to this file
3. Re-run `grade_draft.py` self-tests to confirm the new id is recognized
```

- [ ] **Step 3: Write `references/statute-citations.md`**

```markdown
# Statute citation index — hardcoded URLs

> All URLs use `law.moj.gov.tw` (全國法規資料庫 — 法務部 maintained). URL pattern stable since ~2015.
> Source of truth: `legal-toolkit/scripts/canonical/legal-sources.json` (post-SP1 SoT); this file is the manual cross-reference for template authoring.

## 個資法 (個人資料保護法, pcode I0050021)

- §3 (當事人權利): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=3
- §4 (委託): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=4
- §5 (利用範圍): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=5
- §6 (特種個資): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=6
- §8 (告知事項 — 第一項一至六款): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=8
- §9 (第三人提供告知): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=9
- §11 (個資保管 / 正確性): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=11
- §12 (通報義務 — promulgated 2025-11 amend; 施行日期未定): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=12
- §21 (跨境傳輸): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=21
- §22 (主管機關職權): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=22
- §27 (安全維護): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=27
- §47 (行政罰): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=47
- §48 (行政罰 — new tier promulgated 2025-11, 施行日期未定): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=48

Full text: https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=I0050021

## 個人資料保護法施行細則 (pcode I0050022)

- §12 (受託人義務): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050022&flno=12
- §22 (即時通報 — safe default for breach notification timeframe): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050022&flno=22

Full text (last amended 2016-03-02; not yet updated for 2025/11): https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=I0050022

## 民法 (pcode B0000001)

- §12 (成年年齡): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=12
- §13 (未滿七歲無行為能力 / 七歲以上未成年限制行為能力): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=13
- §227 (不完全給付): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=227
- §247-1 (定型化契約檢視): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=247-1
- §250 (違約金約定): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=250

## 消費者保護法 (pcode J0170001)

- §11-1 (定型化契約等候期 — 30 日): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=J0170001&flno=11-1
- §17 (定型化契約檢視): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=J0170001&flno=17

## 公平交易法 (pcode J0150002)

- §1 (立法目的): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=J0150002&flno=1
- §21 (不實廣告): https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=J0150002&flno=21

## When to regenerate

If `legal-toolkit/scripts/canonical/legal-sources.json` URL templates change (very rare — last format change was ~2015), grep this file + all `assets/template-*.md` files for the affected pcode and update.
```

- [ ] **Step 4: Verify dirs + commit**

```bash
ls legal-toolkit/skills/legal-document-draft/references/
# Expected: pdpa-current-state.md tbd-migration-template.md statute-citations.md
```

- [ ] **Step 5: Commit**

```bash
git add legal-toolkit/skills/legal-document-draft/references/
git commit -m "$(cat <<'EOF'
docs(legal-toolkit): SP2 ground-truth references for draft skill (SP3a Task 4)

Three reference files for legal-document-draft authoring:
- pdpa-current-state.md — offline-readable summary of SP2 research note;
  defines the canonical TBD_* OPEN list that grade_draft.py validates against
- tbd-migration-template.md — Phase 2.5 patch guide; per-TBD upgrade steps
  when PDPC sub-regulations or 行政院 announcements resolve deferred items
- statute-citations.md — hardcoded URL index for templates; per spec §3
  decision 7 (templates pin URLs at authoring time, no runtime fetch)

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Privacy mode — template + checklist

**Files:**
- Create: `legal-toolkit/skills/legal-document-draft/assets/template-privacy.md`
- Create: `legal-toolkit/skills/legal-document-draft/checklists/compliance-privacy.md`

- [ ] **Step 1: Write `assets/template-privacy.md`**

```markdown
<!--
  Skeleton: legal-document-draft / privacy mode
  Citations hardcoded from references/statute-citations.md
  Variables marked {{name}} are filled by protocols/draft.md
  Safe defaults applied for items deferred to PDPC 子法 (see references/tbd-migration-template.md)
-->

# {{company_name}} 隱私權政策

**生效日期**: {{effective_date}}
**最後更新**: {{last_updated}}

## 一、蒐集者身分

蒐集者：{{company_name}} (統一編號 {{company_id}})
登記地址：{{registered_address}}
聯絡：{{general_contact_email}}
個人資料保護聯絡人 (DPO)：{{dpo_name}} ({{dpo_email}})

(法源：個資法 §8 第一項第一款 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=8)

## 二、蒐集目的

本公司蒐集個人資料之主要目的：
{{collection_purposes_bullets}}

(法源：個資法 §8 第一項第二款)

## 三、蒐集個資類別

本公司蒐集之個人資料類別：
{{collected_categories_bullets}}

如蒐集 §6 特種個資 ({{special_category_handling}})，將另行書面同意。

(法源：個資法 §8 第一項第三款 + §6 + §9)

## 四、利用期間、地區、對象、方式

- 期間：{{retention_period}}
- 地區：{{usage_regions}}
- 對象：本公司及{{third_party_categories}}
- 方式：{{processing_methods}}

(法源：個資法 §8 第一項第四款 + §5)

## 五、當事人權利

依個資法 §3，您有以下權利：
- 查詢或請求閱覽
- 請求製給複製本
- 請求補充或更正
- 請求停止蒐集、處理或利用
- 請求刪除

行使方式：致函或寄送電子郵件至 {{dpo_email}}。

(法源：個資法 §3 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=3)

## 六、不提供個人資料之影響

當事人若不提供必要個人資料，可能無法使用 {{product_or_service_name}} 之全部或部分服務功能。

(法源：個資法 §8 第一項第六款)

## 七、第三方 SDK / 服務提供者揭露

本公司於提供服務時使用下列第三方 SDK / 服務：
{{third_party_sdks_bullets}}

如有跨境傳輸個資至下列國家 / 地區：
{{cross_border_destinations_bullets}}

跨境傳輸已採適當保護措施 (合約 / 標準條款 / 主管機關公告適格名單)。

(法源：個資法 §21 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=21)

## 八、個人資料外洩之通報

當本公司察覺個人資料遭非法蒐集、處理、利用或洩漏時，將依個資法相關規定**即時**通報主管機關，並通知受影響當事人。

<!--
  Safe default: 施行細則 §22 「即時」(see references/pdpa-current-state.md)
  TBD_PDPC_timeframe: When PDPC publishes 通報辦法 specifying timeframe, replace
  「即時」with the specific timeframe per references/tbd-migration-template.md
  TBD_PDPC_threshold: If 通報範圍 announced, add threshold-aware language here
-->

(法源：個資法施行細則 §22 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050022&flno=22)

## 九、安全維護措施

本公司採取下列安全維護措施：
{{security_measures_bullets}}

(法源：個資法 §27 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=27)

<!-- TBD_PDPA_audit_framework: When Art. 20-1 effective + PDPC 稽核辦法 published, add audit framework subsection here -->

## 十、未成年人保護

如使用者未滿七歲，不具行為能力，應由父母或監護人代為同意；未滿二十歲限制行為能力人，應經父母或監護人同意。本公司不主動蒐集未成年人之非必要個人資料。

(法源：民法 §12 + §13 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=12)

## 十一、政策修訂與生效

本政策得不定期修訂，修訂時將於 {{product_url_or_app}} 公告。修訂後之政策自公告日 30 日後生效，或您繼續使用服務時即視為同意。

## 十二、爭議處理

本政策依中華民國法律解釋。爭議發生時，雙方同意以{{preferred_court}}為第一審管轄法院。

## 十三、聯絡

如對本政策有疑問，請聯絡：
- 一般：{{general_contact_email}}
- 個人資料保護：{{dpo_email}}
```

- [ ] **Step 2: Write `checklists/compliance-privacy.md`**

```markdown
# Privacy mode — compliance review checklist

> Hand-curated checklist aligned with current in-force 個資法 + 民法.
> Each item is verified by the LLM during the COMPLY_CHECK step of protocols/draft.md.
> Verdict options: PASS / FAIL / TBD_<id> where <id> is from references/pdpa-current-state.md canonical OPEN list.

## 個資法 §8 mandatory disclosure items (一至六款)

- [ ] §8 第一項第一款 — 蒐集者公司名稱已揭露？ — **{{verdict}}**
- [ ] §8 第一項第二款 — 蒐集目的已揭露？ — **{{verdict}}**
- [ ] §8 第一項第三款 — 蒐集個資類別已揭露？ — **{{verdict}}**
- [ ] §8 第一項第四款 — 利用期間 / 地區 / 對象 / 方式已揭露？ — **{{verdict}}**
- [ ] §8 第一項第五款 — 當事人權利 (§3) 已揭露 + 行使方式說明？ — **{{verdict}}**
- [ ] §8 第一項第六款 — 不提供個資之影響已揭露？ — **{{verdict}}**

## 特種個資 + 跨境

- [ ] §6 + §9 — 若蒐集特種個資，書面同意機制已說明？ — **{{verdict}}** (PASS if not collecting; FAIL if collecting but no mechanism)
- [ ] §21 — 若涉跨境傳輸，目的地清單揭露 + 保護措施說明？ — **{{verdict}}**

## 安全維護 + 通報

- [ ] §27 — 安全維護措施列舉？ — **{{verdict}}**
- [ ] 施行細則 §22 — 個資外洩通報用「即時」(NOT 72hr GDPR)？ — **{{verdict}}**
- [ ] §20-1 — Audit framework 段落？ — **TBD_PDPA_audit_framework** (Art. 20-1 promulgated 2025-11-11; 施行日期未定)

## 未成年人保護

- [ ] 民法 §12-13 — 未成年人同意機制依民法行為能力規定？(NOT a PDPA-specific age threshold) — **{{verdict}}**

## 結構性

- [ ] 政策生效日期已填？ — **{{verdict}}**
- [ ] DPO 聯絡 email 已填？ — **{{verdict}}**
- [ ] 第三方 SDK 揭露段落 (即使列表為空亦應說明「未使用」)？ — **{{verdict}}**

## TBD migration tracking

(populate during COMPLY_CHECK; cite references/tbd-migration-template.md for migration steps when PDPC sub-regulations resolve)

- **TBD_PDPA_audit_framework**: monitor PDPC announcements; when Art. 20-1 effective + 稽核辦法 published, add audit-framework subsection to §9 安全維護 per tbd-migration-template.md entry.

(Additional TBD entries appear here only if specific session conditions warrant — e.g., TBD_PDPC_timeframe if user explicitly asks about 72hr language; TBD_PDPC_threshold if special-volume notification.)
```

- [ ] **Step 3: Commit**

```bash
git add legal-toolkit/skills/legal-document-draft/assets/template-privacy.md \
        legal-toolkit/skills/legal-document-draft/checklists/compliance-privacy.md
git commit -m "$(cat <<'EOF'
feat(legal-toolkit): privacy mode template + checklist (SP3a Task 5)

assets/template-privacy.md — 13-section skeleton + {{variables}} +
hardcoded statute URLs (個資法 §3/§5/§6/§8/§9/§21/§27 + 施行細則 §22 +
民法 §12-13); safe default "即時" for breach notification per施行細則
§22 (NOT 72hr GDPR); TBD markers per references/tbd-migration-template.md.

checklists/compliance-privacy.md — 15 hand-curated items aligned with
§8 八款 mandatory disclosure + §6/§9 特種 + §21 跨境 + §27 安全 + 民法
§12-13 minor + 施行細則 §22 即時. Each item ends with {{verdict}}
placeholder for COMPLY_CHECK to fill. TBD_PDPA_audit_framework already
declared for Art. 20-1 未生效 status.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: DPA mode — template + checklist

**Files:**
- Create: `legal-toolkit/skills/legal-document-draft/assets/template-dpa.md`
- Create: `legal-toolkit/skills/legal-document-draft/checklists/compliance-dpa.md`

- [ ] **Step 1: Write `assets/template-dpa.md`**

```markdown
<!--
  Skeleton: legal-document-draft / dpa mode
  Citations hardcoded from references/statute-citations.md
  Variables marked {{name}} are filled by protocols/draft.md
-->

# {{client_company_name}} 與 {{processor_company_name}} 個人資料委託處理協議

**簽訂日期**: {{effective_date}}

## 第一條 委託範圍

委託人 {{client_company_name}} 委託受託人 {{processor_company_name}} 處理下列個人資料：

- 個資類別：{{processor_data_categories}}
- 處理目的：{{processing_purpose}}
- 處理方式：{{processing_methods}}
- 處理期間：{{processing_period}}

(法源：個資法 §4 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=4)

## 第二條 受託人義務

受託人應遵守下列義務：

1. 依委託範圍處理個資；非經委託人書面同意，不得逾越委託範圍或為其他目的之利用。
2. 採取適當之安全維護措施 (§27 + 施行細則 §12)：{{processor_security_measures}}
3. 不得將委託處理之個資外洩予第三人。
4. 受託人之受僱人或受託處理之第三人，亦負本協議所定義務。
5. 配合委託人或主管機關之監督、稽核要求。

(法源：個資法 §8 + 施行細則 §12 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050022&flno=12)

## 第三條 子委託 (再委託)

受託人非經委託人事前書面同意，不得將委託處理之個資再委託第三人。

如經同意之子委託，子受託人應遵守與本協議同等之義務，受託人對子受託人之行為負完全責任。

(法源：個資法 §4 第二項解釋)

## 第四條 個資外洩通報

受託人察覺個資遭非法蒐集、處理、利用或外洩時，應**即時**通知委託人，並提供下列資訊：

- 事件發生時間 (推定 / 實際)
- 影響個資類別 + 當事人估算數量
- 已採取之防止擴大措施
- 復原計畫與時程

委託人依個資法 §22 + 施行細則 §22 對主管機關通報之責任不因受託人之通知而免除。

<!--
  TBD_PDPC_timeframe: When PDPC publishes 通報辦法 specifying timeframe,
  replace 「即時」 with specific timeframe (see references/tbd-migration-template.md).
-->

(法源：個資法施行細則 §22 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050022&flno=22)

## 第五條 委託人之監督權

委託人對受託人之個資處理情形，得依下列方式行使監督權：

- 書面查詢
- 現場稽核 (預先通知 {{audit_notice_days}} 日以上)
- 委由第三方獨立稽核
- 要求受託人提供安全維護措施執行紀錄

受託人應配合，不得無正當理由拒絕。

## 第六條 委託終止後之處理

本協議終止後，受託人應於 {{post_termination_disposal_days}} 日內：

- 返還或銷毀全部受託處理之個資及其副本
- 出具書面證明返還或銷毀完成
- 如法律另有保存義務，僅得保留必要之最低限度

## 第七條 責任分配

依個資法 §4 解釋，委託人 (控制者) 對受託人 (處理者) 之違法行為負連帶責任。受託人若違反本協議致委託人受損害，應負損害賠償責任，賠償範圍包括：

- 委託人對當事人之賠償金
- 主管機關之行政罰
- 訴訟費用及合理律師費

(法源：個資法 §4 + §28-29 + 民法 §227 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=I0050021&flno=4)

## 第八條 通知方式

任何依本協議所為之通知，應寄送下列地址：

- 委託人 DPO：{{client_dpo_email}}
- 受託人 DPO：{{processor_dpo_contact}}

## 第九條 適用法律與管轄

本協議依中華民國法律解釋。爭議應以 {{preferred_court}} 為第一審管轄法院。

## 第十條 其他

- 本協議自雙方簽署日生效，有效期間至委託處理結束或本協議解除為止。
- 本協議修訂應經雙方書面同意。
- 本協議一式兩份，雙方各執一份為憑。

---

委託人：{{client_company_name}} (蓋章 / 代表簽名)
受託人：{{processor_company_name}} (蓋章 / 代表簽名)
日期：{{effective_date}}
```

- [ ] **Step 2: Write `checklists/compliance-dpa.md`**

```markdown
# DPA mode — compliance review checklist

> Hand-curated checklist aligned with 個資法 §4 + §8 + 施行細則 §12.

## 委託範圍 (§4)

- [ ] 第一條 — 個資類別 / 處理目的 / 處理方式 / 處理期間均明確？ — **{{verdict}}**

## 受託人義務 (§8 + 施行細則 §12)

- [ ] 第二條 — 委託範圍限制條款 (非經書面同意不得逾越)？ — **{{verdict}}**
- [ ] 第二條 — 安全維護措施具體列舉 (§27 + 施行細則 §12)？ — **{{verdict}}**
- [ ] 第二條 — 受僱人 / 第三人連帶義務條款？ — **{{verdict}}**
- [ ] 第二條 — 監督 / 稽核配合條款？ — **{{verdict}}**

## 子委託 (§4 解釋)

- [ ] 第三條 — 子委託事前書面同意條款？ — **{{verdict}}**
- [ ] 第三條 — 子受託人同等義務 + 受託人連帶責任？ — **{{verdict}}**

## 通報 (施行細則 §22)

- [ ] 第四條 — 個資外洩「即時」通知委託人 (NOT 72hr)？ — **{{verdict}}**
- [ ] 第四條 — 通知內容包含時間 / 影響範圍 / 防止擴大措施 / 復原計畫？ — **{{verdict}}**

## 監督權 (商業慣例)

- [ ] 第五條 — 委託人監督權 (書面 / 現場 / 第三方 / 紀錄) 明確？ — **{{verdict}}**

## 終止後處理 (§11)

- [ ] 第六條 — 終止後返還 / 銷毀期限 + 書面證明條款？ — **{{verdict}}**

## 責任分配 (§4 + §28-29 + 民法 §227)

- [ ] 第七條 — 受託人對委託人之損害賠償範圍明確 (含當事人賠償 / 行政罰 / 訴訟費)？ — **{{verdict}}**

## TBD migration tracking

(none expected for current dpa mode; if user explicitly references 72hr / GDPR controller-processor split, surface TBD_PDPC_timeframe per references/tbd-migration-template.md)
```

- [ ] **Step 3: Commit**

```bash
git add legal-toolkit/skills/legal-document-draft/assets/template-dpa.md \
        legal-toolkit/skills/legal-document-draft/checklists/compliance-dpa.md
git commit -m "$(cat <<'EOF'
feat(legal-toolkit): dpa mode template + checklist (SP3a Task 6)

assets/template-dpa.md — 10-clause skeleton (委託範圍 / 受託人義務 /
子委託 / 通報 / 監督 / 終止 / 責任 / 通知 / 管轄 / 其他) with
hardcoded URLs for 個資法 §4 / §8 + 施行細則 §12 + §22; 委託/受託
model (NOT GDPR controller/processor split per Path A).

checklists/compliance-dpa.md — 12 items covering 委託範圍 / 受託人
義務 (5 sub-items) / 子委託 / 通報 (即時 not 72hr) / 監督 / 終止 /
責任 ; designed to surface TBD_PDPC_timeframe only if session
explicitly references GDPR-style timeframe.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: NDA mode — template + checklist

**Files:**
- Create: `legal-toolkit/skills/legal-document-draft/assets/template-nda.md`
- Create: `legal-toolkit/skills/legal-document-draft/checklists/compliance-nda.md`

- [ ] **Step 1: Write `assets/template-nda.md`**

```markdown
<!--
  Skeleton: legal-document-draft / nda mode
  Citations hardcoded from references/statute-citations.md
  Variables marked {{name}} are filled by protocols/draft.md
  Bilateral NDA template; for unilateral, COMPLY_CHECK adjusts wording.
-->

# {{party_a_name}} 與 {{party_b_name}} 保密協議

**簽訂日期**: {{effective_date}}

## 第一條 機密資訊定義

「機密資訊」係指雙方因 {{purpose_of_disclosure}} 而揭露之下列資訊，無論其載體：

- 商業策略、業務計畫、財務資料
- 技術、產品、製程、原始碼
- 客戶 / 供應商名單
- 內部會議紀錄、報價、討論草案
- 其他標示「機密」或於揭露時口頭聲明為機密之資訊

**例外** (Carve-outs)：機密資訊不包括：
1. 揭露前已為接受方合法知悉者
2. 揭露時或揭露後已為公眾所知 (非因接受方違反本協議所致)
3. 接受方自第三方合法取得，且該第三方無保密義務者
4. 接受方獨立開發，無須使用揭露方機密資訊者
5. 經揭露方事前書面同意公開者

## 第二條 雙方義務

接受方應：

1. 採取**至少與保護自身機密資訊相同**之注意義務，且不低於合理注意義務。
2. 僅用於本協議所載 {{purpose_of_disclosure}} 之目的。
3. 揭露範圍限於接受方之受僱人、顧問、或受託處理人，且其有合理需求知悉者；該等人員應受同等保密義務拘束，接受方對其行為負連帶責任。
4. 不得反向工程、解構、複製機密資訊。
5. 機密資訊應與其他資訊分離保管。

## 第三條 法律強制揭露

接受方因法律、法院命令或主管機關要求必須揭露機密資訊時：

- 應於可行範圍內事前通知揭露方
- 配合揭露方爭取保密處理 (e.g., protective order)
- 揭露範圍限於法律所要求之最低限度

## 第四條 保密期間

本協議之保密義務自簽訂日起生效，**繼續有效 {{survival_years}} 年** ({{survival_years_explanation}})，**除非機密資訊已符合第一條 carve-outs 例外之一**。

(預設 survival period 來自 legal-playbook/confidentiality.md；典型範圍 3-7 年；技術機密可延至 10 年或永久)

## 第五條 違約救濟

如接受方違反本協議：

- **金錢損害賠償**：依民法 §227 (不完全給付) 應賠償揭露方所受損害及所失利益。
- **約定違約金**：每次違約 {{liquidated_damages}}，揭露方仍得就超過違約金部分請求賠償 (民法 §250 第二項)。
- **禁制令**：揭露方得請求法院命接受方停止違約行為，包括但不限於假處分。
- **返還義務**：機密資訊應於違約時或揭露方書面要求時 {{return_days}} 日內銷毀或返還，並出具書面證明。

(法源：民法 §227 + §250 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=227)

## 第六條 適用法律與管轄

本協議依中華民國法律解釋。爭議應以 {{preferred_court}} 為第一審管轄法院。

## 第七條 其他

- **完整協議**：本協議為雙方就機密資訊揭露之完整約定，取代雙方先前所有書面或口頭協議。
- **修訂**：本協議修訂應經雙方書面同意。
- **可分割性**：本協議任一條款被認定無效時，不影響其他條款之效力。
- **無放棄**：揭露方未即時行使任一權利，不視為放棄該權利。
- **轉讓限制**：未經對方書面同意，任一方不得將本協議權利義務轉讓予第三人。
- **正本份數**：本協議一式兩份，雙方各執一份為憑。

---

{{party_a_name}} (蓋章 / 代表簽名)
{{party_b_name}} (蓋章 / 代表簽名)
日期：{{effective_date}}
```

- [ ] **Step 2: Write `checklists/compliance-nda.md`**

```markdown
# NDA mode — compliance review checklist

> Hand-curated checklist for bilateral NDA (unilateral adjustments noted inline).

## 機密資訊定義 (Definition)

- [ ] 第一條 — 機密資訊類別具體列舉？ — **{{verdict}}**
- [ ] 第一條 — Carve-outs 例外 5 款齊備 (已知 / 公開 / 第三方 / 獨立開發 / 同意公開)？ — **{{verdict}}**

## 接受方義務 (Obligations)

- [ ] 第二條 — 注意義務標準 (至少與自身機密相同)？ — **{{verdict}}**
- [ ] 第二條 — 揭露範圍限制 (有合理需求知悉者) + 第三人連帶責任？ — **{{verdict}}**
- [ ] 第二條 — 反向工程禁止條款？ — **{{verdict}}**

## 法律強制揭露 (Compelled disclosure)

- [ ] 第三條 — 事前通知 + 配合保密處理 + 限於必要範圍？ — **{{verdict}}**

## 保密期間 (Survival)

- [ ] 第四條 — 具體年限 ({{survival_years}}) 明確？ — **{{verdict}}**
- [ ] 第四條 — Carve-outs 連動 (符合例外則終止)？ — **{{verdict}}**

## 違約救濟 (Remedies)

- [ ] 第五條 — 民法 §227 損害賠償 + §250 違約金 + 禁制令 + 返還義務齊備？ — **{{verdict}}**

## TBD migration tracking

(none expected for nda mode — no statutory PDPC dependencies)
```

- [ ] **Step 3: Commit**

```bash
git add legal-toolkit/skills/legal-document-draft/assets/template-nda.md \
        legal-toolkit/skills/legal-document-draft/checklists/compliance-nda.md
git commit -m "$(cat <<'EOF'
feat(legal-toolkit): nda mode template + checklist (SP3a Task 7)

assets/template-nda.md — 7-clause bilateral NDA skeleton (定義 + 5
carve-outs / 義務 / 強制揭露 / survival / 違約救濟 / 管轄 / 其他)
with hardcoded URLs for 民法 §227 + §250. Variables include
{{survival_years}} sourced from legal-playbook/confidentiality.md
stance defaults per spec Q5 decision.

checklists/compliance-nda.md — 7 items covering definition + 5
carve-outs / obligations / compelled-disclosure / survival /
remedies (民法 §227 損害賠償 + §250 違約金 + 禁制令 + 返還義務).
No PDPC TBD entries (NDA mode doesn't depend on 個資法 sub-regs).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: ToS mode — template + checklist

**Files:**
- Create: `legal-toolkit/skills/legal-document-draft/assets/template-tos.md`
- Create: `legal-toolkit/skills/legal-document-draft/checklists/compliance-tos.md`

- [ ] **Step 1: Write `assets/template-tos.md`**

```markdown
<!--
  Skeleton: legal-document-draft / tos mode
  Citations hardcoded from references/statute-citations.md
  Variables marked {{name}} are filled by protocols/draft.md
-->

# {{company_name}} {{service_name}} 服務條款

**生效日期**: {{effective_date}}

## 第一條 服務範圍

{{company_name}} ({{company_id}}) (以下稱「本公司」) 提供 {{service_description}} (以下稱「本服務」)。本條款規範使用者與本公司之間因本服務所生之權利義務。

## 第二條 使用者註冊

使用者註冊時應提供真實、正確、完整資訊。如資訊變更，使用者應即時更新。本公司得依個資法蒐集、處理及利用使用者之個人資料 (詳見 [隱私權政策]({{privacy_policy_url}}))。

未滿七歲不具行為能力者，不得使用本服務。未滿二十歲限制行為能力人使用本服務，視為已得法定代理人同意。

(法源：民法 §12 + §13 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=B0000001&flno=12)

## 第三條 費用與付款

- 費用：{{pricing_summary}}
- 計費期間：{{billing_cycle}}
- 付款方式：{{payment_methods}}
- 退款政策：依消費者保護法 §19 之七日鑑賞期 (如適用) 及本條款規定。

(法源：消費者保護法 §19 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=J0170001&flno=19)

## 第四條 智慧財產權

- **本公司權利**：本服務之軟體、商標、版權、設計及相關智慧財產均屬本公司或其授權人所有。使用者僅取得依本條款使用本服務之非專屬、不可轉讓授權。
- **使用者內容**：使用者上傳之內容權利仍屬使用者。但使用者授與本公司及其關係企業全球範圍、非專屬、可轉授權之授權，以提供、改進、宣傳本服務。

## 第五條 使用者義務 (禁止行為)

使用者不得：

1. 違反中華民國法律之行為
2. 侵害第三人智慧財產或其他權利
3. 散布病毒、惡意程式
4. 反向工程、解構、未經授權複製本服務
5. 干擾本服務正常運作
6. 假冒他人或不實陳述身分
7. 蒐集他人個人資料而未經其同意

## 第六條 服務終止

- **使用者終止**：使用者得隨時停止使用本服務並關閉帳號。
- **本公司終止**：使用者違反本條款重大條款，或本公司停止營運時，本公司得終止使用者之帳號，並依本條款規定處理使用者資料。
- **終止後之效力**：本條款第七條 (限制責任)、第八條 (爭議解決) 及任何性質上應於終止後持續之條款，於終止後繼續有效。

## 第七條 限制責任

- 本服務依「現狀」提供，本公司不就本服務之適合性、可靠性、不中斷或不誤性等作擔保。
- 在法律允許之最大範圍內，本公司之累計責任**不超過使用者於發生損害之事件前 {{liability_cap_months}} 個月支付之費用總額**。
- 本公司不就間接、特殊、衍生性損害負責。
- 本條限制不適用於下列情形：本公司之故意或重大過失；違反消保法或公平交易法之強制規定。

(法源：消保法 §11-1 + §17 + 公平交易法 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=J0170001&flno=11-1)

## 第八條 定型化契約等候期

本條款屬定型化契約，使用者首次同意後享有 30 日之審閱期，得於該期間內以書面表示終止合約，本公司應退還已收取之款項。

(法源：消保法 §11-1 + §17 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=J0170001&flno=17)

## 第九條 條款修訂

本公司得不定期修訂本條款。修訂時將於本服務或 {{company_url}} 公告，並通知使用者。**自公告起 30 日**後生效，使用者繼續使用本服務即視為同意修訂後條款。如不同意修訂，使用者應於生效日前停止使用並終止帳號。

(法源：消保法 §17 第二項)

## 第十條 不公平競爭注意

本服務之經營遵守公平交易法。如有疑義，得向公平交易委員會申訴。

(法源：公平交易法 — https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=J0150002&flno=1)

## 第十一條 個人資料保護

本公司依個資法及 [隱私權政策]({{privacy_policy_url}}) 處理使用者個人資料。

## 第十二條 爭議解決

- **適用法律**：本條款依中華民國法律解釋。
- **管轄法院**：雙方同意以 {{preferred_court}} 為第一審管轄法院。
- **不阻止調解**：本條不限制當事人尋求消費爭議調解委員會之調解程序。

## 第十三條 聯絡方式

如對本條款有疑問，請聯絡：{{general_contact_email}}

---

**本條款一式兩份**，使用者點選同意或繼續使用本服務時，視為簽署。
```

- [ ] **Step 2: Write `checklists/compliance-tos.md`**

```markdown
# ToS mode — compliance review checklist

> Hand-curated checklist aligned with 民法 + 消保法 §11-1/§17/§19 + 公平交易法.

## 服務範圍 + 註冊

- [ ] 第一條 — 服務範圍具體說明 (不是空泛 boilerplate)？ — **{{verdict}}**
- [ ] 第二條 — 個資蒐集連結到 privacy 政策？ — **{{verdict}}**
- [ ] 第二條 — 未成年人民法 §12-13 行為能力處理？ — **{{verdict}}**

## 費用 + 退款 (消保法 §19)

- [ ] 第三條 — 費用 / 計費期間 / 付款方式明確？ — **{{verdict}}**
- [ ] 第三條 — 退款政策提及消保法 §19 七日鑑賞期 (如適用)？ — **{{verdict}}** (PASS if 非通訊交易 explicitly noted; PASS if 七日鑑賞期 included)

## 智財

- [ ] 第四條 — 本公司權利 + 使用者內容權利 + 授權範圍明確？ — **{{verdict}}**

## 限制責任 + 等候期 (消保法 §11-1 + §17)

- [ ] 第七條 — 限制責任不超過 {{liability_cap_months}} 個月費用？ — **{{verdict}}**
- [ ] 第七條 — 強制規定豁免 (故意/重大過失/消保法/公平交易法) 已標示？ — **{{verdict}}**
- [ ] 第八條 — 30 日定型化契約審閱期？ — **{{verdict}}**
- [ ] 第九條 — 條款修訂公告 30 日後生效 (§17 第二項)？ — **{{verdict}}**

## 公平競爭 + 管轄

- [ ] 第十條 — 公平交易法注意條款？ — **{{verdict}}**
- [ ] 第十二條 — 適用法律 / 管轄 / 不阻止調解？ — **{{verdict}}**

## TBD migration tracking

(none expected — ToS mode uses fully in-force 民法/消保法/公平交易法; no PDPC dependencies)

- [ ] (TBD_GOV_CLOUD_restrictions only if user explicitly mentions 政府客戶) — **{{verdict}}**
```

- [ ] **Step 3: Commit**

```bash
git add legal-toolkit/skills/legal-document-draft/assets/template-tos.md \
        legal-toolkit/skills/legal-document-draft/checklists/compliance-tos.md
git commit -m "$(cat <<'EOF'
feat(legal-toolkit): tos mode template + checklist (SP3a Task 8)

assets/template-tos.md — 13-clause skeleton (服務範圍 / 註冊 / 費用
/ 智財 / 使用者義務 / 終止 / 限制責任 / 30日等候期 / 修訂 / 公平
競爭 / 個資 / 爭議 / 聯絡) with hardcoded URLs for 民法 §12-13 +
消保法 §11-1/§17/§19 + 公平交易法.

checklists/compliance-tos.md — 13 items covering 服務範圍 / 註冊 /
費用 (含 §19 7日鑑賞期) / 智財 / 限制責任 / 30日定型化等候期
(§11-1/§17) / 修訂生效 (§17 第二項) / 公平競爭 / 爭議. No required
TBD entries; optional TBD_GOV_CLOUD_restrictions only if 政府客戶
scope.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: Protocols — draft.md + grade.md

**Files:**
- Create: `legal-toolkit/skills/legal-document-draft/protocols/draft.md`
- Create: `legal-toolkit/skills/legal-document-draft/protocols/grade.md`

- [ ] **Step 1: Write `protocols/draft.md`**

```markdown
# Protocol — draft

The main LLM-executed pipeline for legal-document-draft. Triggered by `using-legal-toolkit` router Q2 dispatch.

## Input contract

- `mode`: "privacy" | "tos" | "dpa" | "nda"
- working dir: a git repo with `legal-playbook/profile.yml` present (may also have `legal-playbook/<clause>.md` files)

## Pipeline (sequential, no parallelism)

### Step 1: LOAD_PROFILE

Run:

```bash
python3 legal-toolkit/skills/legal-document-draft/scripts/load_profile.py legal-playbook/profile.yml
```

Expected: exit 0 with `OK: profile valid; company=<name>`.

If exit 1:
- Read the error list from stderr.
- Surface to user: "Profile validation failed. Fix `legal-playbook/profile.yml` first, then re-run."
- Do NOT proceed.

### Step 2: SELECT_TEMPLATE

Read `assets/template-<mode>.md` (mode from input).

### Step 3: SCAN_PLAYBOOK

For each variable in the template that has a corresponding clause in `legal-playbook/`, read the clause and extract the stance default.

Mapping (current — extend as playbook grows):

| Template variable | Source playbook clause | Field |
|---|---|---|
| `{{survival_years}}` (nda) | `legal-playbook/confidentiality.md` | `survival_period` (years) |
| `{{liquidated_damages}}` (nda) | `legal-playbook/confidentiality.md` | `liquidated_damages` |
| `{{return_days}}` (nda) | `legal-playbook/confidentiality.md` | `return_days` |
| `{{audit_notice_days}}` (dpa) | `legal-playbook/data-protection-dpa.md` | `audit_notice` (days) |
| `{{post_termination_disposal_days}}` (dpa) | `legal-playbook/data-protection-dpa.md` | `disposal_period` (days) |
| `{{preferred_court}}` (all) | `legal-playbook/governing-law-jurisdiction.md` | `preferred_court` |
| `{{liability_cap_months}}` (tos) | `legal-playbook/limitation-of-liability/_clause.md` | `cap_months` |

If a playbook clause is missing → variable falls through to ASK_GAPS.

### Step 4: ASK_GAPS

Identify all template variables NOT satisfied by profile + playbook. Ask the user in a single batched interactive prompt:

```
我需要以下資訊以完成 {{mode}} draft：

1. {{var_1_human_label}}: ?
2. {{var_2_human_label}}: ?
...
```

Provide:
- Profile/playbook-derived defaults inline (e.g., "preferred_court (legal-playbook 預設: 臺灣臺北地方法院, 按 Enter 使用)")
- Human-friendly labels (not raw variable names)
- Sensible suggestions / examples per variable

Per-mode required vars (variables NOT in profile.yml):

**privacy**: collection_purposes / collected_categories / retention_period / usage_regions / third_party_categories / processing_methods / product_or_service_name / product_url_or_app / third_party_sdks / special_category_handling

**tos**: service_name / service_description / pricing_summary / billing_cycle / payment_methods / liability_cap_months / privacy_policy_url / company_url

**dpa**: client_company_name / processor_company_name / processor_data_categories / processing_purpose / processing_methods / processing_period / processor_security_measures / audit_notice_days / post_termination_disposal_days / client_dpo_email / processor_dpo_contact / preferred_court

**nda**: party_a_name / party_b_name / purpose_of_disclosure / survival_years / liquidated_damages / return_days / preferred_court / effective_date

### Step 5: MERGE

Resolve final variable values; precedence: session input > playbook default > profile field > template-implied default.

Apply safe defaults for TBD variables:
- privacy: §8 通報 → "即時" (NOT 72hr); §20-1 audit framework → TBD_PDPA_audit_framework marker; minor → 民法 §12-13 cite
- dpa: §22 通報 → "即時"
- nda: no TBDs
- tos: no required TBDs

LLM fills the skeleton with values. Optional sections (e.g., 第三方 SDK in privacy when none used) get adapted text instead of empty placeholders.

### Step 6: COMPLY_CHECK

Read `checklists/compliance-<mode>.md`. For each `- [ ]` item, evaluate the draft and emit one of:
- **PASS** — verified the item is satisfied
- **FAIL** — item not satisfied; surface explicit reason
- **TBD_<id>** — item depends on a canonical OPEN list entry (see `references/pdpa-current-state.md`); cite the migration template entry

Render `compliance.md` by substituting each `{{verdict}}` with the determined verdict + a short rationale.

### Step 7: SELF_GRADE

Run:

```bash
python3 legal-toolkit/skills/legal-document-draft/scripts/grade_draft.py \
  legal-outputs/<timestamp>-<mode>/ <mode>
```

Expected: exit 0 with `OK: structural grading PASS`.

If exit 1:
- Read failure reasons from stderr.
- Identify which check failed (orphan / verdict / TBD / truncation / missing file).
- Patch and re-run COMPLY_CHECK + SELF_GRADE until exit 0.

### Step 8: OUTPUT

Write final files:

```
legal-outputs/<timestamp>-<mode>/
├── <doc-type>.md     (privacy.md | tos.md | dpa.md | nda.md)
└── compliance.md
```

Print summary to user:

```
Draft complete:
  Document: legal-outputs/<timestamp>-<mode>/<doc-type>.md
  Compliance: legal-outputs/<timestamp>-<mode>/compliance.md

Verdict counts:
  PASS: <N>
  FAIL: <N>
  TBD: <N> (see compliance.md TBD migration section)

Next steps:
- Review compliance.md before publishing
- For TBD items, monitor references/tbd-migration-template.md for upgrade triggers
- Patch legal-playbook/<clause>.md if a session value should become the default for future drafts
```

## Failure modes

- Profile invalid → halt at Step 1
- Template mode unknown → halt at Step 2
- LLM-fill produces malformed markdown (broken headers, etc.) → grade_draft catches in Step 7
- User abandons session mid-way → drafts in `legal-outputs/<timestamp>-<mode>/` may be partial; safe to delete

## Notes for implementers

- This protocol is LLM-executed; the Python scripts (load_profile / grade_draft) are deterministic safety nets, not the primary logic.
- The MERGE step must respect "safe defaults" semantics: do NOT hardcode 72hr / GDPR-style content; defer to施行細則 §22 "即時" + TBD_PDPC_* tracking.
- TBD verdicts must use canonical ids from `references/pdpa-current-state.md`; fabricated ids fail SELF_GRADE.
```

- [ ] **Step 2: Write `protocols/grade.md`**

```markdown
# Protocol — grade

Deterministic structural grading details, complementing `scripts/grade_draft.py`. The Python script handles file-level checks; this protocol documents the rationale for each check.

## Why deterministic-only at MVP

Per spec §3 decision Q9b, structural checks catch ~95% of "I forgot to fill X" mistakes without requiring Pearson-calibrated LLM rubric (which needs hand-graded baselines we don't have yet). Heavier LLM-rubric scoring is deferred to v0.4.0.1+ once 5-10 dogfood drafts give us calibration data.

## What grade_draft.py checks

1. **File presence** — both `<doc-type>.md` (privacy/tos/dpa/nda) + `compliance.md` exist
2. **No orphan placeholders** — `<doc-type>.md` has no `{{...}}` lingering (catches MERGE step omissions)
3. **Verdict coverage** — every `- [ ]` or `- [x]` line in `compliance.md` has a `**PASS**` / `**FAIL**` / `**TBD_<id>**` marker
4. **TBD canonicality** — every `TBD_<id>` used must appear in `references/pdpa-current-state.md` canonical OPEN list (rejects fabricated ids; LLM might invent `TBD_GDPR_72hr` which is wrong for Path A)
5. **Truncation guard** — `<doc-type>.md` byte-count > 500 bytes (catches LLM session timeout / context limit truncation)

## What grade_draft.py does NOT check (deferred)

- Semantic correctness of legal language (LLM rubric, post-dogfood)
- Statute citation URL liveness (templates are pinned at authoring; runtime fetch would be over-engineered)
- Optional-section appropriateness (e.g., did the LLM correctly omit 第三方 SDK when none declared?)
- Cross-mode consistency (e.g., did privacy and tos reference the same liability cap?)

## When grader emits FAIL

The pipeline halts. The COMPLY_CHECK step must re-run, addressing each FAIL reason. Common patterns:

| FAIL reason | Likely cause | Fix |
|---|---|---|
| `orphan template placeholder(s) in doc` | A `{{variable}}` was not resolved during MERGE | Re-run MERGE; check ASK_GAPS captured all required variables |
| `checklist line X has no verdict` | LLM forgot to substitute `{{verdict}}` for a checklist item | Re-run COMPLY_CHECK; emphasize "every item must end with PASS/FAIL/TBD_<id>" |
| `fabricated TBD id(s)` | LLM invented a new TBD identifier | Replace with a canonical id from `pdpa-current-state.md`; if a genuinely new deferred item exists, FIRST add it to the canonical list + tbd-migration-template.md before re-running |
| `possible truncation` | LLM output was cut off; doc too short | Re-run draft (entire pipeline); check session token budget |
| `missing compliance.md` | OUTPUT step skipped a file | Re-run OUTPUT |

## Exit codes

- 0 — all checks passed
- 1 — at least one structural failure (reasons on stderr)
- 2 — invalid invocation (wrong args, unknown mode)
```

- [ ] **Step 3: Commit**

```bash
git add legal-toolkit/skills/legal-document-draft/protocols/
git commit -m "$(cat <<'EOF'
feat(legal-toolkit): draft + grade protocols (SP3a Task 9)

protocols/draft.md — main LLM-executed pipeline (8 steps:
LOAD_PROFILE → SELECT_TEMPLATE → SCAN_PLAYBOOK → ASK_GAPS → MERGE →
COMPLY_CHECK → SELF_GRADE → OUTPUT). Per-mode variable lists +
playbook-mapping table + safe-default rules (即時 not 72hr) +
TBD canonical-id discipline.

protocols/grade.md — deterministic structural grading rationale.
Documents what grade_draft.py checks (5 categories) + what it
does NOT check (deferred to v0.4.0.1+ rubric) + common FAIL
patterns and remediation.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: Router update — `using-legal-toolkit` Q2 dispatch

**Files:**
- Modify: `legal-toolkit/skills/using-legal-toolkit/SKILL.md`

- [ ] **Step 1: Read current router state**

```bash
grep -n "Q2\|起草\|draft\|legal-document-draft\|Phase 2-5" legal-toolkit/skills/using-legal-toolkit/SKILL.md
```

Expected output: lines noting Q2 is "planned for Phase 2" or similar placeholder text.

- [ ] **Step 2: Edit `using-legal-toolkit/SKILL.md`**

Locate the Q2 section (or where Q2 is described as planned). Replace the Q2 placeholder block with active dispatch logic:

Find:

```
   planned for Phase <N> per the roadmap at legal-toolkit/ROADMAP.md.
```

(or similar placeholder text for Q2)

Replace the Q2 section so it actively dispatches. Edit the file to include a Q2 block like:

```markdown
### Q2 — Document drafting (active in v0.4.0+)

**Keyword triggers**: 起草 / draft / 寫一份 / write a / 草擬 / generate / create a (followed by) 隱私權 / privacy / ToS / 服務條款 / DPA / 委託處理 / NDA / 保密協議

**Disambiguation**: if the user does not explicitly name a mode, ask:

> 哪種文件？1) 隱私權政策 (privacy)  2) 服務條款 (tos)  3) 委託處理協議 (dpa)  4) 保密協議 (nda)

Once mode is determined → hand off to `legal-document-draft` skill with the mode flag.

**Prerequisite check before handoff**: confirm `legal-playbook/profile.yml` exists in the working directory. If absent, surface to user:

> 起草前需要 `legal-playbook/profile.yml`（公司基本資料）。建議：
> 1) 看 `legal-toolkit/skills/legal-document-draft/assets/profile-schema.yml` schema
> 2) 在 `legal-playbook/` 下新建 `profile.yml`，填入公司名稱 / 統編 / 地址 / DPO 聯絡 / 一般聯絡 email
> 3) 完成後重新呼叫此 skill

Boilerplate keywords that should NOT route to draft (route to review instead): 看一下 / 審 / review / redline / 修改 (followed by) 我們收到 / 對方 / counterparty.
```

(adjust exact insertion location based on the existing SKILL.md layout — the goal is to flip Q2 from placeholder to active)

- [ ] **Step 3: Verify the edit**

```bash
grep -n "active in v0.4.0\|legal-document-draft" legal-toolkit/skills/using-legal-toolkit/SKILL.md
```

Expected: lines confirming the Q2 dispatch is active.

- [ ] **Step 4: Commit**

```bash
git add legal-toolkit/skills/using-legal-toolkit/SKILL.md
git commit -m "$(cat <<'EOF'
feat(legal-toolkit): activate Q2 router dispatch for draft (SP3a Task 10)

using-legal-toolkit/SKILL.md Q2 path flipped from "planned" to
active. Routes 起草/draft/寫一份/write/草擬/generate + 隱私權/ToS/
DPA/NDA keyword combinations to legal-document-draft with mode
flag. Disambiguation prompt for unclear mode + prerequisite check
for legal-playbook/profile.yml before handoff. Boilerplate guard
keeps 看一下/審/review/redline keywords routed to contract-review.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: Dogfood smoke — generate one privacy draft end-to-end

**Files:**
- (no new committed files; smoke is for self-validation)

The first 10 tasks build the skill plumbing + templates + checklists + grader. This task validates end-to-end behavior by running the draft pipeline manually against the `profile-full.yml` fixture, producing one synthetic privacy.md + compliance.md, and verifying `grade_draft.py` passes.

- [ ] **Step 1: Prepare working dir**

```bash
mkdir -p /tmp/legal-document-draft-smoke/legal-playbook
mkdir -p /tmp/legal-document-draft-smoke/legal-outputs
cp legal-toolkit/tests/fixtures-document-draft/profile-full.yml /tmp/legal-document-draft-smoke/legal-playbook/profile.yml
cd /tmp/legal-document-draft-smoke
```

- [ ] **Step 2: Validate profile.yml**

```bash
python3 /Users/kouko/GitHub/monkey-skills/legal-toolkit/skills/legal-document-draft/scripts/load_profile.py legal-playbook/profile.yml
```

Expected: `OK: profile valid; company=範例股份有限公司`

- [ ] **Step 3: Manually compose a privacy draft in `legal-outputs/2026-05-13T120000-privacy/`**

This is an LLM-executed step. As an implementer, follow protocols/draft.md and produce a complete privacy.md + compliance.md filling in:
- profile-derived values (company name / 統編 / DPO / cross-border destinations)
- session ASK_GAPS values (use plausible SaaS-company stand-ins: collection purposes = ["訂閱管理", "客戶支援", "服務改進"]; categories = ["身分識別", "帳務", "使用紀錄"]; retention = "服務期間 + 終止後 5 年"; SDKs = [{"name": "Google Analytics", "purpose": "使用統計", ...}, {"name": "Stripe", "purpose": "金流", ...}])
- safe defaults (即時 for breach; minor → 民法 §12-13; §20-1 → TBD_PDPA_audit_framework)

- [ ] **Step 4: Run grader**

```bash
python3 /Users/kouko/GitHub/monkey-skills/legal-toolkit/skills/legal-document-draft/scripts/grade_draft.py \
  legal-outputs/2026-05-13T120000-privacy/ privacy
```

Expected: exit 0 with `OK: structural grading PASS`.

If grader fails, fix the privacy.md or compliance.md per `protocols/grade.md` FAIL-pattern table, then re-run until PASS.

- [ ] **Step 5: Cleanup smoke dir**

```bash
cd /Users/kouko/GitHub/monkey-skills
rm -rf /tmp/legal-document-draft-smoke
```

(no commit for this task — it's validation-only; the only output is confidence in end-to-end behavior)

---

## Task 12: Version bump + ROADMAP + marketplace.json sync

**Files:**
- Modify: `legal-toolkit/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `legal-toolkit/ROADMAP.md`

- [ ] **Step 1: Bump plugin.json version + append v0.4.0 description sentence**

Edit `legal-toolkit/.claude-plugin/plugin.json`:

1. Change `"version": "0.3.6"` to `"version": "0.4.0"`.
2. Append this sentence to the description, immediately before the final "Phase 2-5 adds..." sentence:

   ```
   v0.4.0 Phase 2 ships legal-document-draft (4 modes — privacy / ToS / DPA / NDA): skeleton-and-LLM-fill templates pinned to current in-force Taiwan law (Path A from SP2 verify run); 2-file audience-shaped output (<doc-type>.md publish-ready + compliance.md 法務 review); hand-curated per-mode compliance checklists with statute citations (個資法 §8 八款 / §9 / §21 / §27 / 民法 §12-13/§227/§247-1/§250 / 消保法 §11-1/§17/§19 / 公平交易法); deterministic structural grading (no orphan {{vars}} / verdict coverage / canonical TBD ids / truncation guard); legal-playbook/profile.yml as shared company identity SoT; 委託/受託 model (NOT GDPR controller-processor); safe defaults for items deferred to PDPC 子法 (Phase 2.5 migration template documented). Cross-skill: shares legal-playbook/confidentiality.md stance with legal-contract-review nda mode; references legal-sources.json URL templates at template authoring time (NOT runtime fetch).
   ```

- [ ] **Step 2: Sync marketplace.json description**

```bash
python3 - <<'PY'
import json
from pathlib import Path

plugin_json = json.loads(Path("legal-toolkit/.claude-plugin/plugin.json").read_text(encoding="utf-8"))
new_desc = plugin_json["description"]

market_path = Path(".claude-plugin/marketplace.json")
market = json.loads(market_path.read_text(encoding="utf-8"))
for p in market["plugins"]:
    if p.get("source") == "./legal-toolkit/":
        p["description"] = new_desc
        break
else:
    raise SystemExit("legal-toolkit entry not found in marketplace.json")

market_path.write_text(
    json.dumps(market, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print("OK: marketplace.json description synced to plugin.json")
PY
```

- [ ] **Step 3: Verify sync**

```bash
python3 scripts/check-marketplace-description-sync.py
```

Expected: exit 0.

- [ ] **Step 4: Append Phase 2 v0.4.0 ship section to `legal-toolkit/ROADMAP.md`**

Locate `## Phase 2 — Template + Runbook（v0.4.0，10 天）` and replace with the v0.4.0-shipped version showing draft delivered + IR deferred to v0.4.1:

```markdown
## Phase 2 — Template + Runbook（v0.4.0 部分 ship 2026-05-13；v0.4.1 IR pending）

**Scope**: 累計 4 skills (router + playbook-author + contract-review + document-draft); legal-incident-response delayed to v0.4.1 per SP3 sequenced ship decision (B path) after SP2 PDPA verify reframed IR's 72hr-timer-centric design.

### v0.4.0 (SP3a) ✅ **DONE 2026-05-13**

`legal-document-draft` — 4 modes (privacy / tos / dpa / nda), skeleton + LLM fill, 2-file audience-shaped output, hand-curated per-mode checklists with statute citations, deterministic structural grader, Path A (current Taiwan law).

Decisions locked in spec brainstorm Q2-Q9: 4 modes / skeleton+LLM / 2-file output / playbook variable defaults / profile at legal-playbook/profile.yml / hardcode URLs / safe defaults + TBD tracking / heavy hand-curated checklists / deterministic structural self-grade.

Cross-skill: shares `legal-playbook/confidentiality.md` stance with `legal-contract-review nda`; uses `legal-playbook/profile.yml` as company identity SoT (future SP3b / corp-governance / dd-quickscan all read this).

Full design + plan:
- spec: `docs/superpowers/specs/2026-05-13-legal-toolkit-sp3a-document-draft-design.md`
- plan: `docs/superpowers/plans/2026-05-13-legal-toolkit-sp3a-document-draft.md`

### v0.4.1 (SP3b) 🔜 pending — `legal-incident-response`

IR skill reframed from obsidian SoT §3.5's 72hr-timer-centric design after SP2 found 72hr was GDPR contamination. New scope: 事件分流 + 法源引用器 + 通報文起草 (3-path classifier: 個資外洩 / 主管機關函覆 / 違約; emits 內部記錄 + 通報文 with safe-default placeholders). To brainstorm + spec + ship after v0.4.0 dogfood feedback.

### Quality gate

- draft privacy / ToS / DPA / NDA modes all produce passing compliance.md
- `grade_draft.py` exits 0 across modes with synthetic fixtures
- `load_profile.py` validates profile.yml against schema
- 184 + 10 (4 T-P + 6 T-G) = ~194 tests green

---
```

(replace existing `## Phase 2 — ...` section through to its closing `---`; keep `## Phase 3` and later sections intact)

- [ ] **Step 5: Update version-strategy table**

Find the 版本策略 table in `legal-toolkit/ROADMAP.md` and replace the `v0.4.0` row with:

```markdown
| v0.4.0 | Phase 2 (partial) — legal-document-draft ship | 「4 mode 起草：隱私權政策 / 服務條款 / DPA / NDA。Path A 對現行台灣法務實。Skeleton + LLM fill；hand-curated 合規 checklist；deterministic 結構性 grading；profile.yml 共用公司身份。IR 延後到 v0.4.1。」 |
```

(insert a new v0.4.1 row after it):

```markdown
| v0.4.1 | Phase 2 (complete) — legal-incident-response ship | 「事件分流 + 法源引用器 + 通報文起草 (3-path: 個資外洩 / 主管機關函覆 / 違約)。SP2 reframe 後不再有 72hr GDPR timer。」 |
```

- [ ] **Step 6: Final smoke**

```bash
python3 scripts/check-marketplace-description-sync.py
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/ 2>&1 | tail -3
python3 legal-toolkit/scripts/verify-drift.py
```

Expected:
- check-marketplace exit 0
- pytest ~194 PASS
- verify-drift exit 0 (SP3a does not touch canonical/)

- [ ] **Step 7: Commit**

```bash
git add legal-toolkit/.claude-plugin/plugin.json \
        .claude-plugin/marketplace.json \
        legal-toolkit/ROADMAP.md
git commit -m "$(cat <<'EOF'
chore(legal-toolkit): bump to v0.4.0 + Phase 2 ROADMAP partial ship section

Phase 2 split — SP3a (legal-document-draft, 4 modes) ships as v0.4.0;
SP3b (legal-incident-response, reframed away from 72hr timer per SP2
findings) deferred to v0.4.1. ROADMAP §Phase 2 documents both halves;
版本策略 table gets new v0.4.0 + v0.4.1 rows.

plugin.json + marketplace.json descriptions synced per repo CI rule
(scripts/check-marketplace-description-sync.py).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 13: PR readiness — final triple-smoke

**Files:** none modified

- [ ] **Step 1: Branch state**

```bash
git status --short
git log --oneline main..HEAD
```

Expected:
- working tree clean (pre-existing untracked files outside legal-toolkit/ are OK)
- 12-13 commits ahead of main (1 spec + 12 implementation)

- [ ] **Step 2: Final triple-smoke**

```bash
PYTHONDONTWRITEBYTECODE=1 pytest legal-toolkit/ -v 2>&1 | tail -5
python3 legal-toolkit/scripts/verify-drift.py
python3 scripts/check-marketplace-description-sync.py
bash .claude/hooks/validate-skill-folder-structure.sh legal-toolkit/skills/legal-document-draft/SKILL.md
bash .claude/hooks/validate-skill-folder-structure.sh legal-toolkit/skills/using-legal-toolkit/SKILL.md
bash .claude/hooks/validate-skill-folder-structure.sh legal-toolkit/skills/legal-playbook-author/SKILL.md
bash .claude/hooks/validate-skill-folder-structure.sh legal-toolkit/skills/legal-contract-review/SKILL.md
```

Expected:
- pytest: ~194 PASS (171 existing + 13 SP1 + 10 SP3a)
- verify-drift: exit 0 (SP3a does not touch canonical/)
- marketplace sync: exit 0
- All 4 skill-folder-structure validators: silent (no violations)

- [ ] **Step 3: Pause for user authorization to push + open PR**

Per CLAUDE.md global red lines, push + PR is outbound and requires explicit user approval. Surface the branch state to the user and await their go signal.

When user authorizes, run:

```bash
git push -u origin feat/legal-toolkit-sp3a-document-draft
gh pr create --title "feat(legal-toolkit): v0.4.0 — legal-document-draft 4-mode skill" --body "$(cat <<'EOF'
## Summary

SP3a of the legal-toolkit Phase 2 program. Ships `legal-document-draft` skill (4 modes: privacy / ToS / DPA / NDA) for drafting **new** Taiwan-law legal documents from company profile + negotiation playbook. Path A direction (current in-force Taiwan law); items deferred to PDPC 子法 (72hr timeframe / 通報門檻 / etc.) tracked as canonical TBDs with documented migration path.

**Phase 2 split**: SP3b (`legal-incident-response`, reframed away from 72hr timer per SP2 findings) deferred to `v0.4.1` per sequenced ship decision.

## What changed

- **NEW skill** `legal-toolkit/skills/legal-document-draft/` — 4 modes × (template + checklist), 2 protocols, 2 scripts (load_profile + grade_draft), 3 reference docs, 3 READMEs.
- **NEW tests** `legal-toolkit/tests/test_load_profile.py` (4 T-P-*) + `test_grade_draft.py` (6 T-G-*) + `fixtures-document-draft/` (profile fixtures + draft-output-sample-privacy).
- **MODIFIED** `using-legal-toolkit/SKILL.md` — Q2 dispatch path flipped from "planned" to active with disambiguation + prereq check.
- **BUMP** `plugin.json` 0.3.6 → 0.4.0, `marketplace.json` synced.
- **DOCS** `ROADMAP.md` §Phase 2 split section + 版本策略 table rows for v0.4.0 / v0.4.1.

## Test plan

- [x] ~194/194 tests pass locally (171 + 13 SP1 + 10 SP3a)
- [x] `python3 .../load_profile.py legal-playbook/profile.yml` exit 0 for fixtures
- [x] `python3 .../grade_draft.py <output_dir> <mode>` exit 0 for synthetic sample
- [x] Manual dogfood smoke: 1 privacy mode end-to-end via fixtures
- [x] `verify-drift.py` exit 0 (SP3a does not touch canonical/)
- [x] `check-marketplace-description-sync.py` exit 0
- [x] 4 skill-folder-structure validators silent
- [ ] **CI green on first push** (this PR)
- [ ] User dogfood: generate own company privacy.md + compliance.md; verify usability

## Design / plan

- Spec: `docs/superpowers/specs/2026-05-13-legal-toolkit-sp3a-document-draft-design.md`
- Plan: `docs/superpowers/plans/2026-05-13-legal-toolkit-sp3a-document-draft.md`
- SP2 ground truth (Path A direction): `legal-toolkit/research/2026-05-12-pdpa-2025-11-verify.md`

## Memory

- **Decision**: Path A (current Taiwan law) over B (future-effective 2025/11 with TODO placeholders) / C (dual-mode GDPR + Taiwan) / D (defer Phase 2). Reason: SP2 verify revealed 5 obsidian-SoT-design pillars were GDPR contamination or un-effective; Path A is legally accurate today + zero fabrication.
- **Decision**: Skeleton + LLM fill (over pure-LLM generation or hybrid). Reliable mandatory portion + flexible variable portion; matches contract-review's deterministic-rubric philosophy.
- **Decision**: Profile at `legal-playbook/profile.yml` (visible + git-tracked) over `.legal-toolkit/config.yml` per obsidian SoT. Company info is shared asset; lives with playbook, not in hidden runtime state dir.
- **Learning**: Plugin-level tests/ (not skill-internal) is the convention in legal-toolkit + translation-toolkit; skill folders stay flat per Anthropic SKILL.md spec + monkey-skills CLAUDE.md.
- **Gotcha**: Don't hardcode 72hr in any Taiwan-PDPA template. 施行細則 §22 says 「即時」; specific timeframe deferred to PDPC sub-regs. Use TBD_PDPC_timeframe marker + tbd-migration-template.md for upgrade path.

## Related

- Predecessor: PR #272 (SP1 canonical/ plumbing), PR #273 (SP2 PDPA verify run)
- Successor: SP3b `legal-incident-response` (v0.4.1)
- D-track: SP4 Phase 4.5 上市櫃 Compliance research stub (parallel; out of scope for this PR)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

- [ ] **Step 4: Done**

After PR is open, monitor CI. If CI fails, iterate on the failing check (per SP1 / SP2 precedents, the most common failure mode is missing test deps in the CI install step — already addressed in SP1's CI workflow update).

---

## Completion checklist

After Task 13 passes triple-smoke + PR is open:

- [ ] 12 implementation commits + 1 spec commit (already shipped) = 13 commits ahead of main
- [ ] All commits use Conventional Commits with kebab-case scope (per repo CI lint)
- [ ] Branch `feat/legal-toolkit-sp3a-document-draft` pushed
- [ ] PR open + linked to SP2 PR #273
- [ ] User dogfoods at least one mode end-to-end before merge

---

## Estimate (per spec §16)

- 5-7 days total: 1 day for plan iteration + 4-5 days implementation + 1 day review/CI polish
- Compressible to ~3 days via subagent-driven parallel (after Task 4 reference files land, Tasks 5-8 per-mode template+checklist are independent — 4 worktrees, 4 modes in parallel)
- Subagent-driven recommended: per-task fresh subagent + 2-stage review per SP1 precedent (caught 5 important issues across 14 tasks)
