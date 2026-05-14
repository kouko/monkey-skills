# legal-toolkit SP3b v0.4.3 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship v0.4.3 — patch 2 P0 + 3 P1 dogfood-surfaced contract bugs in SP3b `legal-incident-response` v0.4.2. Bump `profile-schema` v1 → v2 (additive: `dpo.phone`), fix authority-letter Step 2b nested-path bug, add 行政程序法 to canonical legal-sources, align 5 doc sites that previously lied about "v2 schema".

**Architecture:** Canonical SoT bumped (`scripts/canonical/profile-schema.yml` v1 → v2 + `legal-sources.json` +1 entry); distribute.py auto-syncs to both SP3a + SP3b skill copies; 6 commits via TDD with regression gate at end.

**Tech Stack:** Python 3.12+ (PYTHONDONTWRITEBYTECODE=1 for pytest), pytest, JSON Schema 2020-12, PyYAML, jsonschema lib.

**Predecessor:** Spec `docs/superpowers/specs/2026-05-14-legal-toolkit-sp3b-v0.4.3-dogfood-patches-design.md`. Audit `/tmp/legal-toolkit-sp3b-dogfood/AUDIT-v0.4.2.md`.

---

## File Structure

### Files to modify (canonical/ — SoT)

- `legal-toolkit/scripts/canonical/profile-schema.yml` — `schema_version: const: 1` → `2`; `dpo.properties` add `phone: { type: string }`
- `legal-toolkit/scripts/canonical/legal-sources.json` — add 行政程序法 (pcode A0030055) to `statute_sources`; bump `verified_at`
- `legal-toolkit/scripts/distribute.py` — extend `ROUTE` to include new migration doc

### Files to create (canonical/)

- `legal-toolkit/scripts/canonical/profile-schema-v2-migration.md` — 1-page v1 → v2 delta + when to populate `dpo.phone`

### Files to modify (SP3b)

- `legal-toolkit/skills/legal-incident-response/protocols/authority-letter.md` — Step 2b L70-72 nested-path → top-level path
- `legal-toolkit/skills/legal-incident-response/SKILL.md` — L26-28 align "v2 schema" claim
- `legal-toolkit/skills/legal-incident-response/README.md` — L57-59 align
- `legal-toolkit/skills/legal-incident-response/README.ja.md` — L59-61 align
- `legal-toolkit/skills/legal-incident-response/README.zh-TW.md` — L57-59 align

### Files to modify (auto-distributed; do NOT hand-edit — verify only)

- `legal-toolkit/skills/legal-document-draft/assets/profile-schema.yml`
- `legal-toolkit/skills/legal-incident-response/assets/profile-schema.yml`
- `legal-toolkit/skills/legal-contract-review/assets/legal-sources.json`
- `legal-toolkit/skills/legal-document-draft/references/profile-schema-v2-migration.md` (newly distributed)
- `legal-toolkit/skills/legal-incident-response/references/profile-schema-v2-migration.md` (newly distributed)

### Files to modify (fixtures + tests)

- `legal-toolkit/tests/fixtures-document-draft/profile-minimal.yml` — bump `schema_version: 1` → `2`
- `legal-toolkit/tests/fixtures-document-draft/profile-full.yml` — bump `schema_version: 1` → `2`
- `legal-toolkit/tests/fixtures-document-draft/profile-v2.yml` — bump `schema_version: 1` → `2` + add `dpo.phone: "02-1234-5678"`
- `legal-toolkit/tests/test_load_profile.py` — add 3 new tests (T-P-5 expanded for dpo.phone; T-P-6 v1 schema_version now rejected; T-P-7 v1 structure validates under v2 schema after version bump)
- `legal-toolkit/scripts/tests/test_distribute.py` — add 1 new test for `profile-schema-v2-migration.md` ROUTE entry

### Files to modify (metadata)

- `legal-toolkit/.claude-plugin/plugin.json` — version 0.4.2 → 0.4.3 + description append
- `.claude-plugin/marketplace.json` — sync description verbatim
- `legal-toolkit/ROADMAP.md` — v0.4.3 addendum under Phase 2
- `legal-toolkit/README.md` / `README.ja.md` / `README.zh-TW.md` — version badge 0.4.2 → 0.4.3

### Fixture to create

- `legal-toolkit/tests/fixtures-document-draft/profile-v1-rejected.yml` — `schema_version: 1` proof fixture (negative test)

---

## Task 1: P0-2 — authority-letter Step 2b nested-path fix

Pure doc-bug fix. Smallest patch in the release; ships first to flush the easy win.

**Files:**
- Modify: `legal-toolkit/skills/legal-incident-response/protocols/authority-letter.md` L70-72

- [ ] **Step 1: Verify the bug**

Run:
```
grep -n "profile.company\." legal-toolkit/skills/legal-incident-response/protocols/authority-letter.md
```
Expected: 3 matches at L70-72 (`profile.company.name` / `.tax_id` / `.id` / `.registered_address`).

- [ ] **Step 2: Apply the 3-line fix**

Edit `legal-toolkit/skills/legal-incident-response/protocols/authority-letter.md` Step 2b L70-72:

Old:
```
- `{{company_name}}` ← `profile.company.name`
- `{{company_id}}` ← `profile.company.tax_id` 或 `profile.company.id` (統一編號)
- `{{registered_address}}` ← `profile.company.registered_address` (公司登記地址)
```

New:
```
- `{{company_name}}` ← `profile.company_name` (top-level)
- `{{company_id}}` ← `profile.company_id` (top-level; 統一編號 8 digits per schema pattern `^[0-9]{8}$`)
- `{{registered_address}}` ← `profile.registered_address` (top-level; 公司登記地址)
```

- [ ] **Step 3: Verify fix**

Run:
```
grep -n "profile.company\." legal-toolkit/skills/legal-incident-response/protocols/authority-letter.md
```
Expected: 0 matches.

Cross-check pii-breach.md uses the same form (regression guard):
```
grep -n "company_name\b" legal-toolkit/skills/legal-incident-response/protocols/pii-breach.md
```
Expected: 1+ match showing `company_name | {{company_name}} | top-level`.

- [ ] **Step 4: Commit**

```bash
git add legal-toolkit/skills/legal-incident-response/protocols/authority-letter.md
git commit -m "$(cat <<'EOF'
fix(legal-toolkit): SP3b authority-letter Step 2b — top-level profile paths

Step 2b L70-72 wrote `profile.company.name / .tax_id / .id / .registered_address`,
but the actual schema declares these top-level (`company_name / company_id /
registered_address`). pii-breach.md was already correct; authority-letter.md
drift surfaced via v0.4.2 dogfood (audit P0-2).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: P1-2 — canonical/legal-sources.json + 行政程序法

Add 行政程序法 (pcode A0030055) to canonical SoT so authority-letter Step 3 EXTRACT no longer halts on legitimate citations. distribute.py auto-syncs to `legal-contract-review/assets/legal-sources.json`.

**Files:**
- Modify: `legal-toolkit/scripts/canonical/legal-sources.json`
- Auto-distributed: `legal-toolkit/skills/legal-contract-review/assets/legal-sources.json`

- [ ] **Step 1: Write failing test for new statute_source entry**

Add to `legal-toolkit/scripts/tests/test_distribute.py` (or wherever the canonical structural tests live — likely `test_verify_drift.py`'s sibling area; pick the file that already imports legal-sources):

```python
def test_canonical_legal_sources_includes_administrative_procedure_act():
    """行政程序法 (pcode A0030055) MUST be in canonical statute_sources;
    cited by statute-citations.md L42 for authority-letter 回函時程基準."""
    import json
    from pathlib import Path
    canonical = Path(__file__).resolve().parents[2] / "scripts" / "canonical" / "legal-sources.json"
    data = json.loads(canonical.read_text(encoding="utf-8"))
    assert "行政程序法" in data["statute_sources"], (
        "行政程序法 missing from canonical statute_sources; expected pcode A0030055"
    )
    assert data["statute_sources"]["行政程序法"]["pcode"] == "A0030055"
```

If no obvious test file exists for canonical/legal-sources.json structure, create `legal-toolkit/scripts/tests/test_legal_sources.py` with this test as the file's first entry.

- [ ] **Step 2: Run test to verify failure**

Run:
```
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/scripts/tests/test_legal_sources.py::test_canonical_legal_sources_includes_administrative_procedure_act -v
```
Expected: FAIL with KeyError `'行政程序法'` or AssertionError.

- [ ] **Step 3: Add 行政程序法 to canonical**

Edit `legal-toolkit/scripts/canonical/legal-sources.json`. In `statute_sources`, add (preserve alphabetic-by-pcode or existing ordering convention — currently appears keyed by Chinese name; place after 仲裁法 or where most natural):

```json
"行政程序法": {
  "pcode": "A0030055",
  "name_zh": "行政程序法",
  "single_article_url_template": "https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=A0030055&flno={article}",
  "full_text_url": "https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=A0030055",
  "scope_note": "主管機關函覆／公文書送達時程基準 (authority-letter path 法源依據)"
}
```

(Match exact JSON structure of an existing entry like 民法 — copy its shape.)

Bump `verified_at` to today's date (`2026-05-14`).

- [ ] **Step 4: Run test to verify pass**

Run:
```
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/scripts/tests/test_legal_sources.py::test_canonical_legal_sources_includes_administrative_procedure_act -v
```
Expected: PASS.

- [ ] **Step 5: Run distribute.py + verify drift catches sync**

Run:
```
PYTHONDONTWRITEBYTECODE=1 python3 legal-toolkit/scripts/distribute.py
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/scripts/tests/test_verify_drift.py -v
```
Expected: distribute prints copy count > 0; all drift tests PASS.

Verify functional copy synced:
```
shasum legal-toolkit/scripts/canonical/legal-sources.json legal-toolkit/skills/legal-contract-review/assets/legal-sources.json
```
Expected: identical hashes.

- [ ] **Step 6: Commit**

```bash
git add legal-toolkit/scripts/canonical/legal-sources.json \
        legal-toolkit/skills/legal-contract-review/assets/legal-sources.json \
        legal-toolkit/scripts/tests/test_legal_sources.py
git commit -m "$(cat <<'EOF'
feat(legal-toolkit): add 行政程序法 to canonical statute_sources

statute-citations.md L42 already cites 行政程序法 §49 as authority-letter
path 回函時程基準, but canonical legal-sources.json (post-SP1 SoT) lacked
it. Without this entry, authority-letter Step 3 EXTRACT halt rule fires on
incoming letters citing 行政程序法 (very common for 主管機關 procedural matters).

Surfaced via v0.4.2 dogfood audit P1-2.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: P0-1 — canonical profile-schema v1 → v2 (dpo.phone)

The core fix. Bump canonical schema, add new tests, distribute to both skills, update fixtures.

**Files:**
- Modify: `legal-toolkit/scripts/canonical/profile-schema.yml`
- Auto-distributed: `legal-toolkit/skills/legal-document-draft/assets/profile-schema.yml`, `legal-toolkit/skills/legal-incident-response/assets/profile-schema.yml`
- Modify: `legal-toolkit/tests/fixtures-document-draft/profile-minimal.yml`, `profile-full.yml`, `profile-v2.yml`
- Create: `legal-toolkit/tests/fixtures-document-draft/profile-v1-rejected.yml`
- Modify: `legal-toolkit/tests/test_load_profile.py`

- [ ] **Step 1: Write failing test for dpo.phone acceptance**

Edit `legal-toolkit/tests/test_load_profile.py`. Modify existing `test_v2_profile_fields_validate` (line 83-95) — append `dpo.phone` assertion:

```python
def test_v2_profile_fields_validate():
    """v0.4.3 schema v2: external_counsel + regulatory_authorities + dpo.phone
    all validate. v1 fixtures must be bumped to schema_version: 2 (additive bump)."""
    load_profile = _load_module("load_profile.py")

    profile_path = FIXTURES / "profile-v2.yml"
    result = load_profile.load_profile(profile_path)

    assert result.valid is True, f"expected valid profile, got errors: {result.errors}"
    assert result.data["external_counsel"]["firm_name"] == "測試律師事務所"
    assert len(result.data["regulatory_authorities"]) == 2
    assert result.data["dpo"]["phone"] == "02-1234-5678"
    assert result.errors == []
```

Add 2 new tests:

```python
# ---------------------------------------------------------- T-P-6: v1 schema_version rejected
def test_v1_schema_version_rejected_under_v2_schema():
    """v0.4.3 schema bumps `schema_version: const: 2`; v1 fixtures bumped in same
    commit. A fixture still declaring `schema_version: 1` must now be rejected."""
    load_profile = _load_module("load_profile.py")

    profile_path = FIXTURES / "profile-v1-rejected.yml"
    result = load_profile.load_profile(profile_path)

    assert result.valid is False
    assert any("schema_version" in err for err in result.errors), (
        f"expected schema_version error, got: {result.errors}"
    )


# ---------------------------------------------------------- T-P-7: v1 structure forward-compat
def test_v1_structure_validates_when_schema_version_bumped(tmp_path):
    """Additive v1→v2 bump guarantee: a pure-v1 STRUCTURE (no dpo.phone, no
    external_counsel, no regulatory_authorities) must validate under v2 schema
    once schema_version is updated to 2. Locks in the additive-bump promise."""
    load_profile = _load_module("load_profile.py")

    v1_shape = tmp_path / "v1-shape.yml"
    v1_shape.write_text(
        """
schema_version: 2
company_name: 純 v1 結構公司
company_id: "12345678"
registered_address: 台北市中山區範例路 1 號
general_contact:
  email: contact@example.com
dpo:
  name: 王小明
  email: dpo@example.com
""",
        encoding="utf-8",
    )

    result = load_profile.load_profile(v1_shape)

    assert result.valid is True, f"v1 shape under v2 must validate, got: {result.errors}"
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/tests/test_load_profile.py -v
```
Expected: 3 FAILs:
- `test_v2_profile_fields_validate`: AssertionError on `dpo.phone` key not present in v2 fixture
- `test_v1_schema_version_rejected_under_v2_schema`: file not found (`profile-v1-rejected.yml`)
- `test_v1_structure_validates_when_schema_version_bumped`: schema_version 2 fails const:1

Also expect `test_schema_version_mismatch_fails` still PASSes (already tests version 99 != 1; will need update later — actually leave it for now, change in this task).

- [ ] **Step 3: Bump canonical schema**

Edit `legal-toolkit/scripts/canonical/profile-schema.yml`:

```yaml
# At line ~20-23 (schema_version block):
  schema_version:
    type: integer
    const: 2
    description: Schema version; bump on breaking changes. v2 (2026-05-14) adds dpo.phone.

# At line ~47-56 (dpo block):
  dpo:
    type: object
    required: [name, email]
    description: Data Protection Officer (個資法 §22 推定承辦人)
    additionalProperties: false
    properties:
      name:
        type: string
      email:
        type: string
      phone:
        type: string
        description: DPO 個人聯絡電話 (incident response 個資外洩通報 / 函覆落款用；可與 general_contact.phone 不同)
```

- [ ] **Step 4: Bump 3 fixtures**

Edit `legal-toolkit/tests/fixtures-document-draft/profile-minimal.yml`:
- Change `schema_version: 1` → `schema_version: 2`
- No other changes (minimal stays minimal; demonstrates v1-shape forward-compat)

Edit `legal-toolkit/tests/fixtures-document-draft/profile-full.yml`:
- Change `schema_version: 1` → `schema_version: 2`

Edit `legal-toolkit/tests/fixtures-document-draft/profile-v2.yml`:
- Change `schema_version: 1` → `schema_version: 2`
- Under `dpo:`, add `phone: "02-1234-5678"` so the fixture demonstrates the new field

- [ ] **Step 5: Create v1-rejected fixture**

Create `legal-toolkit/tests/fixtures-document-draft/profile-v1-rejected.yml`:

```yaml
# Negative-test fixture: profile that declares schema_version 1 must be rejected
# under v2 schema (const: 2). Use this fixture to lock the version bump.
schema_version: 1
company_name: v1 已棄用版本
company_id: "12345678"
registered_address: 台北市中山區範例路 1 號
general_contact:
  email: contact@example.com
dpo:
  name: 王小明
  email: dpo@example.com
```

- [ ] **Step 6: Update test_schema_version_mismatch_fails for v2 const**

Edit the existing `test_schema_version_mismatch_fails` to reflect v2 schema. The test currently writes `schema_version: 99`; under v2 schema, `99 != 2` so it still fails — but the docstring should explicitly note v2:

```python
def test_schema_version_mismatch_fails(tmp_path):
    """schema_version must be const 2 under v0.4.3 schema."""
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

- [ ] **Step 7: Run distribute.py + verify byte-identical to both skills**

Run:
```
PYTHONDONTWRITEBYTECODE=1 python3 legal-toolkit/scripts/distribute.py
shasum legal-toolkit/scripts/canonical/profile-schema.yml \
       legal-toolkit/skills/legal-document-draft/assets/profile-schema.yml \
       legal-toolkit/skills/legal-incident-response/assets/profile-schema.yml
```
Expected: 3 identical hashes.

- [ ] **Step 8: Run all profile tests to verify pass**

Run:
```
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/tests/test_load_profile.py -v
```
Expected: all 7 tests PASS (5 existing updated + 2 new).

- [ ] **Step 9: Run full legal-toolkit suite for regression**

Run:
```
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/ -v 2>&1 | tail -30
```
Expected: all tests PASS. If any SP3a baseline test fails on profile fixture, fix in this same task (likely fixture path coupling).

- [ ] **Step 10: Run drift verify**

Run:
```
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/scripts/tests/test_verify_drift.py -v
```
Expected: PASS.

- [ ] **Step 11: Commit**

```bash
git add legal-toolkit/scripts/canonical/profile-schema.yml \
        legal-toolkit/skills/legal-document-draft/assets/profile-schema.yml \
        legal-toolkit/skills/legal-incident-response/assets/profile-schema.yml \
        legal-toolkit/tests/fixtures-document-draft/profile-minimal.yml \
        legal-toolkit/tests/fixtures-document-draft/profile-full.yml \
        legal-toolkit/tests/fixtures-document-draft/profile-v2.yml \
        legal-toolkit/tests/fixtures-document-draft/profile-v1-rejected.yml \
        legal-toolkit/tests/test_load_profile.py
git commit -m "$(cat <<'EOF'
feat(legal-toolkit): bump canonical profile-schema v1 → v2 (dpo.phone)

Additive bump: schema_version const 1 → 2; dpo.properties gains optional
phone (string). Existing v1 STRUCTURE remains valid after schema_version is
bumped; only the version literal changes.

Why: SP3b v0.4.2 template-pii-breach-pdpc-notification.md + 5 other doc
sites reference dpo.phone, but v1 schema declared dpo as
additionalProperties:false with only [name, email] — making no valid v1
profile.yml able to supply dpo.phone. Surfaced via v0.4.2 dogfood audit P0-1.

distribute.py auto-syncs canonical → both SP3a + SP3b skill copies; verified
byte-identical via shasum + test_verify_drift.

Fixtures: profile-minimal / profile-full / profile-v2 all bumped to
schema_version: 2 (additive bump means structure unchanged). New
profile-v1-rejected.yml fixture proves schema_version: 1 is now rejected.

Tests: 5 existing test_load_profile.py tests updated; 2 new tests added
(T-P-6 v1 version rejected; T-P-7 v1 structure forward-compat at v2 version).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: P1-1 — SP3b 5-site doc alignment

5 doc sites currently say "v2 schema" + "v2-added fields backward-compat v1 profiles". After Task 3, the first claim is true; the second was always misleading (fields existed in v1 as optional, not "v2-added"). Reword to match reality.

**Files:**
- Modify: `legal-toolkit/skills/legal-incident-response/SKILL.md` L26-28
- Modify: `legal-toolkit/skills/legal-incident-response/README.md` L57-59
- Modify: `legal-toolkit/skills/legal-incident-response/README.ja.md` L59-61
- Modify: `legal-toolkit/skills/legal-incident-response/README.zh-TW.md` L57-59

- [ ] **Step 1: Verify pre-state**

Run:
```
grep -n "v2 schema\|v2-added\|backward-compat" \
  legal-toolkit/skills/legal-incident-response/SKILL.md \
  legal-toolkit/skills/legal-incident-response/README*.md
```
Expected: 8 matches across 4 files (2 per file: one in "Required" block, one in "Optional from profile" block).

- [ ] **Step 2: Edit SKILL.md (L26-28)**

Replace:
```
- **Required**: `legal-playbook/profile.yml` (v2 schema; validated by `scripts/load_profile.py`)
- **Required at session**: incident free-text description (or explicit `--type` override)
- **Optional from profile**: `external_counsel` + `regulatory_authorities` (v2-added fields; backward-compat v1 profiles)
```

With:
```
- **Required**: `legal-playbook/profile.yml` (schema v2; validated by `scripts/load_profile.py`; see `references/profile-schema-v2-migration.md` for v1→v2 delta)
- **Required at session**: incident free-text description (or explicit `--type` override)
- **Optional from profile**: `external_counsel` + `regulatory_authorities` + `dpo.phone` (all optional in schema v2)
```

- [ ] **Step 3: Edit README.md (L57-59)**

Apply same content change as Step 2 (English wording).

- [ ] **Step 4: Edit README.ja.md (L59-61)**

Replace (preserve ja wording style):
```
- **Required**：`legal-playbook/profile.yml`（v2 schema；session 開始前に `scripts/load_profile.py` が validate）
- **Required at session**：incident 自由記述 (or `--type` override)
- **Optional from profile**：`external_counsel` + `regulatory_authorities`（v2 追加項目；backward-compat v1 profile）
```

With:
```
- **Required**：`legal-playbook/profile.yml`（schema v2；session 開始前に `scripts/load_profile.py` が validate；v1→v2 delta は `references/profile-schema-v2-migration.md` を参照）
- **Required at session**：incident 自由記述 (or `--type` override)
- **Optional from profile**：`external_counsel` + `regulatory_authorities` + `dpo.phone`（schema v2 で全て optional）
```

- [ ] **Step 5: Edit README.zh-TW.md (L57-59)**

Replace (preserve zh-TW wording style):
```
- **Required**：`legal-playbook/profile.yml`（v2 schema；session 開始前由 `scripts/load_profile.py` validate）
- **Required at session**：incident 自由文字描述（或 `--type` override）
- **Optional from profile**：`external_counsel` + `regulatory_authorities`（v2 新增；backward-compat v1 profile）
```

With:
```
- **Required**：`legal-playbook/profile.yml`（schema v2；session 開始前由 `scripts/load_profile.py` validate；v1→v2 delta 詳 `references/profile-schema-v2-migration.md`）
- **Required at session**：incident 自由文字描述（或 `--type` override）
- **Optional from profile**：`external_counsel` + `regulatory_authorities` + `dpo.phone`（schema v2 皆為 optional）
```

- [ ] **Step 6: Verify post-state**

Run:
```
grep -n "v2 schema\|v2-added\|backward-compat" \
  legal-toolkit/skills/legal-incident-response/SKILL.md \
  legal-toolkit/skills/legal-incident-response/README*.md
```
Expected: 0 matches for `v2-added` / `backward-compat`; matches for `schema v2` are now accurate.

- [ ] **Step 7: Commit**

```bash
git add legal-toolkit/skills/legal-incident-response/SKILL.md \
        legal-toolkit/skills/legal-incident-response/README.md \
        legal-toolkit/skills/legal-incident-response/README.ja.md \
        legal-toolkit/skills/legal-incident-response/README.zh-TW.md
git commit -m "$(cat <<'EOF'
docs(legal-toolkit): SP3b align "schema v2" claim across 4 sites

SKILL.md + 3 READMEs previously asserted "v2 schema" with "v2-added fields
backward-compat v1 profiles". After Task 3 schema bump (v1 → v2 with dpo.phone),
the "v2 schema" claim is true. Reword "v2-added" framing (which was misleading
even pre-bump: external_counsel + regulatory_authorities existed in v1 as
optional fields, not "added in v2") + add pointer to migration doc.

Surfaced via v0.4.2 dogfood audit P1-1.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: P1-3 + migration doc — profile-v2 fixture + canonical migration page

Create canonical migration page, route via distribute.py, fixture already bumped in Task 3.

**Files:**
- Create: `legal-toolkit/scripts/canonical/profile-schema-v2-migration.md`
- Modify: `legal-toolkit/scripts/distribute.py` — extend ROUTE
- Modify: `legal-toolkit/scripts/tests/test_distribute.py` — assert new ROUTE entry
- Auto-distributed: `legal-toolkit/skills/legal-document-draft/references/profile-schema-v2-migration.md`, `legal-toolkit/skills/legal-incident-response/references/profile-schema-v2-migration.md`

- [ ] **Step 1: Write failing test for new ROUTE entry**

Edit `legal-toolkit/scripts/tests/test_distribute.py`. Add:

```python
def test_distribute_routes_profile_schema_v2_migration_to_both_skills():
    """profile-schema-v2-migration.md (canonical/) must distribute to both
    SP3a + SP3b references/ as byte-identical functional copies."""
    from distribute import ROUTE  # if import shape differs, mirror existing test imports
    assert "profile-schema-v2-migration.md" in ROUTE
    dests = ROUTE["profile-schema-v2-migration.md"]
    assert any("legal-document-draft/references" in d for d in dests), (
        "migration doc missing SP3a destination"
    )
    assert any("legal-incident-response/references" in d for d in dests), (
        "migration doc missing SP3b destination"
    )
```

- [ ] **Step 2: Run test to verify failure**

Run:
```
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/scripts/tests/test_distribute.py::test_distribute_routes_profile_schema_v2_migration_to_both_skills -v
```
Expected: FAIL with KeyError or AssertionError.

- [ ] **Step 3: Create migration page**

Create `legal-toolkit/scripts/canonical/profile-schema-v2-migration.md`:

```markdown
# profile.yml schema v1 → v2 migration

> **Source of truth**: this file is in `legal-toolkit/scripts/canonical/` and distributed byte-identical to `legal-document-draft/references/` and `legal-incident-response/references/` via `scripts/distribute.py`.
> **Effective**: legal-toolkit v0.4.3 (2026-05-14)
> **Previous**: v1 schema, in force from v0.3.6 (2026-05-12) to v0.4.2 (2026-05-13)

## What changed

Additive bump. Existing v1 profile **STRUCTURE** is forward-compatible; only the `schema_version` literal must change.

| Field | v1 | v2 |
|---|---|---|
| `schema_version` | `const: 1` | `const: 2` |
| `dpo.phone` | not in `dpo.properties`; rejected by `additionalProperties: false` | `dpo.properties.phone: { type: string }`; optional |
| `dpo.required` | `[name, email]` | `[name, email]` (unchanged; phone is optional) |
| All other fields | (unchanged) | (unchanged) |

## How to migrate an existing v1 profile.yml

1. Open `legal-playbook/profile.yml`.
2. Change `schema_version: 1` to `schema_version: 2`.
3. (Optional) Add a `phone` field under `dpo`:
   ```yaml
   dpo:
     name: 王小明
     email: dpo@example.com
     phone: "+886-2-1234-5678"   # NEW in v2; optional
   ```
4. Re-run any skill that loads profile.yml (e.g., `legal-incident-response`). `load_profile.py` validates against schema v2.

## When to populate `dpo.phone`

- **Recommended**: in-house DPO with dedicated direct line (incident response: PDPC 通報落款 / 主管機關函覆 落款 use this).
- **Acceptable workaround**: leave `dpo.phone` absent; templates fall back to `general_contact.phone` for落款 (公司總機).
- **Not recommended**: setting `dpo.phone` equal to `general_contact.phone` — the schema distinguishes them so future stakeholders can update one without the other (e.g., 委外 DPO with rotating personal phone vs static 公司總機).

## Why the bump

v0.4.2 SP3b `legal-incident-response` shipped 6 doc sites assuming `dpo.phone` exists (PDPC 通報文 落款 + 函覆 落款 + 2 binding tables + 2 checklists). The v1 schema's `additionalProperties: false` on `dpo` rejected any profile.yml that tried to supply this field. Live dogfood surfaced this on 2026-05-14; the fix is the additive v2 bump rather than removing `dpo.phone` from 6 doc sites (DPO 個人聯絡 ≠ 公司總機 — keep the field, fix the schema).

## Backward compatibility guarantee

The bump is **additive**. The structural shape of a v1 profile.yml (no `dpo.phone`, no `external_counsel`, no `regulatory_authorities`) remains a valid shape under v2. Only the `schema_version` literal must move from `1` to `2`. No other content rewriting required.

Regression coverage: `legal-toolkit/tests/test_load_profile.py::test_v1_structure_validates_when_schema_version_bumped` locks this guarantee.
```

- [ ] **Step 4: Extend distribute.py ROUTE**

Edit `legal-toolkit/scripts/distribute.py`. In the `ROUTE` dict (around line 29-49), add:

```python
    "profile-schema-v2-migration.md": [
        "skills/legal-document-draft/references/profile-schema-v2-migration.md",
        "skills/legal-incident-response/references/profile-schema-v2-migration.md",
    ],
```

(Place after `load_profile.py` entry for ordering consistency.)

- [ ] **Step 5: Run distribute + verify both copies materialized**

Run:
```
PYTHONDONTWRITEBYTECODE=1 python3 legal-toolkit/scripts/distribute.py
shasum legal-toolkit/scripts/canonical/profile-schema-v2-migration.md \
       legal-toolkit/skills/legal-document-draft/references/profile-schema-v2-migration.md \
       legal-toolkit/skills/legal-incident-response/references/profile-schema-v2-migration.md
```
Expected: 3 identical hashes.

- [ ] **Step 6: Run distribute + drift tests to confirm**

Run:
```
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/scripts/tests/ -v
```
Expected: all PASS including the new test_distribute_routes_profile_schema_v2_migration entry.

- [ ] **Step 7: Commit**

```bash
git add legal-toolkit/scripts/canonical/profile-schema-v2-migration.md \
        legal-toolkit/scripts/distribute.py \
        legal-toolkit/skills/legal-document-draft/references/profile-schema-v2-migration.md \
        legal-toolkit/skills/legal-incident-response/references/profile-schema-v2-migration.md \
        legal-toolkit/scripts/tests/test_distribute.py
git commit -m "$(cat <<'EOF'
docs(legal-toolkit): add canonical profile-schema-v2-migration page

1-page v1→v2 delta + additive-bump guarantee + dpo.phone usage guidance.
Distributed via distribute.py ROUTE to both SP3a (legal-document-draft) +
SP3b (legal-incident-response) references/ as byte-identical functional copies.

Cited from SP3b SKILL.md + 3 READMEs (Task 4) as the migration reference.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: v0.4.3 release — dogfood replay + version bump + ROADMAP

Final task: re-run both v0.4.2 dogfood scenarios with a schema-clean v2 profile.yml that **declares `dpo.phone`**, confirm orphan-free output + grader passes, bump versions, sync READMEs.

**Files:**
- Modify: `legal-toolkit/.claude-plugin/plugin.json`
- Modify: `.claude-plugin/marketplace.json`
- Modify: `legal-toolkit/ROADMAP.md`
- Modify: `legal-toolkit/README.md`, `README.ja.md`, `README.zh-TW.md`

- [ ] **Step 1: Run dogfood A (PII-breach) with v2 profile + dpo.phone declared**

Create `/tmp/legal-toolkit-sp3b-v0.4.3-replay/legal-playbook/profile.yml` based on the v0.4.2 audit dogfood profile but bumped to v2 with dpo.phone populated. Specifically:

```yaml
schema_version: 2
company_name: 鯨魚商城股份有限公司
company_name_en: Whale Mall Co., Ltd.
company_id: "53912807"
registered_address: 11491 台北市內湖區瑞光路 583 巷 22 號 9 樓
general_contact:
  email: contact@whalemall.example.tw
  phone: "02-2799-1234"
dpo:
  name: 林志偉
  email: dpo@whalemall.example.tw
  phone: "02-2799-1235"      # NEW in v2 — DPO direct line (not 公司總機)
# ... (rest identical to audit dogfood profile)
```

Run:
```
mkdir -p /tmp/legal-toolkit-sp3b-v0.4.3-replay/legal-outputs
cd /tmp/legal-toolkit-sp3b-v0.4.3-replay
PYTHONDONTWRITEBYTECODE=1 python3 /Users/kouko/GitHub/monkey-skills/legal-toolkit/skills/legal-incident-response/scripts/load_profile.py legal-playbook/profile.yml
```
Expected: `OK: profile valid; company=鯨魚商城股份有限公司` (exit 0).

Then either re-author the v0.4.2 dogfood `legal.md` + `business.md` (PII-breach scenario) with `dpo.phone = 02-2799-1235` directly populated (no workaround comment) into the落款, OR replay by hand-running the templates with `dpo_phone = "02-2799-1235"` substituted.

Run grader:
```
PYTHONDONTWRITEBYTECODE=1 python3 /Users/kouko/GitHub/monkey-skills/legal-toolkit/skills/legal-incident-response/scripts/grade_response.py \
  /tmp/legal-toolkit-sp3b-v0.4.3-replay/legal-outputs/2026-05-14T-incident-pii-breach pii-breach
```
Expected: `OK: structural grading PASS`.

- [ ] **Step 2: Orphan grep**

Run:
```
grep -rn '{{[a-z_]\+}}' /tmp/legal-toolkit-sp3b-v0.4.3-replay/legal-outputs/
```
Expected: 0 matches (no template-orphan tokens shipped to either legal.md or business.md).

- [ ] **Step 3: Run dogfood B (authority-letter)**

Mirror Step 1 for authority-letter scenario (公平會 公處字第 11512345 號 promo "銷量第一" 廣告不實 函詢) with `dpo.phone` populated directly. Run grader + orphan grep.

Verify落款 includes:
```
電話：02-2799-1235
```
(no workaround comment about general_contact.phone).

- [ ] **Step 4: Run full legal-toolkit test suite for regression**

Run:
```
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/ legal-toolkit/scripts/tests/ -v 2>&1 | tail -20
```
Expected: all tests PASS. The 226-test SP3b baseline + ~30 SP3a baseline + canonical drift tests should all be green.

Confirm count:
```
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/ legal-toolkit/scripts/tests/ --collect-only -q 2>&1 | tail -5
```
Expected: test count is 226 + 4 (3 from Task 3 + 1 from Task 5) = 230 (give or take depending on existing-test mutations).

- [ ] **Step 5: Bump plugin.json**

Edit `legal-toolkit/.claude-plugin/plugin.json`:
- `"version": "0.4.2"` → `"version": "0.4.3"`
- Append to description: `" / v0.4.3: profile-schema v2 (dpo.phone) + SP3b dogfood patches"`

- [ ] **Step 6: Sync marketplace.json**

Edit `.claude-plugin/marketplace.json`. Find the `legal-toolkit` entry; replace its `description` field with the verbatim value from `plugin.json`. Per [[feedback_plugin_json_location_and_description_sync]] CI enforces verbatim sync.

Run:
```
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-marketplace-description-sync.py
```
Expected: exit 0.

- [ ] **Step 7: Update ROADMAP**

Edit `legal-toolkit/ROADMAP.md`. Under Phase 2 closeout section, add v0.4.3 entry:

```markdown
- **v0.4.3** (2026-05-14) — SP3b dogfood patches
  - P0 fix: profile-schema v1 → v2 (dpo.phone) + 5-site doc alignment
  - P0 fix: authority-letter Step 2b nested-path bug (top-level paths)
  - P1: canonical legal-sources +行政程序法 (pcode A0030055)
  - P1: profile-v2.yml fixture promoted to actual v2; new profile-v1-rejected fixture for negative test
  - Migration doc: `references/profile-schema-v2-migration.md` (canonical SoT)
  - SP3a parity: schema v2 auto-distributed (purely additive; zero functional change)
```

- [ ] **Step 8: Sync version badges in 3 plugin-level READMEs**

Edit `legal-toolkit/README.md` / `README.ja.md` / `README.zh-TW.md` — find `v0.4.2` version badge / version statement and bump to `v0.4.3`.

- [ ] **Step 9: Final regression run**

Run:
```
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest legal-toolkit/ legal-toolkit/scripts/tests/ -v 2>&1 | tail -10
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-marketplace-description-sync.py
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-skill-structure.py 2>&1 | tail -5
```
Expected: all PASS / exit 0.

- [ ] **Step 10: Commit**

```bash
git add legal-toolkit/.claude-plugin/plugin.json \
        .claude-plugin/marketplace.json \
        legal-toolkit/ROADMAP.md \
        legal-toolkit/README.md \
        legal-toolkit/README.ja.md \
        legal-toolkit/README.zh-TW.md
git commit -m "$(cat <<'EOF'
chore(legal-toolkit): v0.4.3 — SP3b dogfood patches

Release bundle for v0.4.3:
- Task 1 (P0-2): authority-letter Step 2b top-level profile paths
- Task 2 (P1-2): canonical legal-sources +行政程序法 (pcode A0030055)
- Task 3 (P0-1): canonical profile-schema v1 → v2 (dpo.phone field)
- Task 4 (P1-1): SP3b 5-site "v2 schema" claim alignment
- Task 5 (P1-3): canonical profile-schema-v2-migration page + fixture promote

Dogfood replay (PII-breach + authority-letter) with v2 profile + dpo.phone
populated: both grade_response.py runs PASS; orphan-grep returns 0 matches;
SP3a + SP3b test baselines green.

P2 polish (§8 第六款 reframe / TBD label split / classify-path examples /
grader template-orphan check) deferred to v0.4.4 per audit ranking.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Self-review

**1. Spec coverage**

| Spec section | Plan task |
|---|---|
| §2 Why P0-1 (`dpo.phone` 6 sites) | Task 3 (schema bump + tests) + downstream propagation |
| §2 Why P0-2 (authority-letter nested paths) | Task 1 |
| §2 Why P1-1 (5-site v2 claim) | Task 4 |
| §2 Why P1-2 (行政程序法) | Task 2 |
| §2 Why P1-3 (profile-v2 fixture) | Task 3 Step 4 (fixture bumped); Task 5 (canonical migration doc) |
| §3 Locked decision 1 (additive bump) | Task 3 |
| §3 Locked decision 2 (SP3a parity via distribute) | Task 3 Step 7 + Task 6 Step 4 regression |
| §3 Locked decision 3 (dpo.phone ≠ general_contact.phone) | Task 5 migration doc body |
| §3 Locked decision 7 (defer P2 to v0.4.4) | (out-of-scope; noted in Task 6 commit message) |
| §3 Locked decision 9 (v1 forward-compat) | Task 3 Step 1 T-P-7 test |
| §3 Locked decision 10 (migration doc) | Task 5 |
| §6 Q1 (v1-rejected fixture) | Task 3 Step 5 |
| §9 Acceptance #1-9 | Task 6 Steps 1-9 |

**2. Placeholder scan** — All commands explicit. All edits show exact before/after. No TBD / TODO / "as appropriate" / "similar to" placeholders.

**3. Type consistency** — Field names verified against schema:
- `dpo.phone` (not `dpoPhone` or `dpo_phone` at schema level — but template variable is `{{dpo_phone}}` underscore form per existing convention)
- `schema_version` (const 1 → 2)
- `company_name` / `company_id` / `registered_address` (top-level; matches schema)
- `行政程序法` (pcode A0030055) matches `references/statute-citations.md` L42
- ROUTE entries follow existing tuple shape (key = canonical filename, value = list of skill-relative paths)

---

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-14-legal-toolkit-sp3b-v0.4.3-dogfood-patches.md`. Two execution options:

1. **Subagent-Driven (recommended)** — Fresh subagent per task + 2-stage review (spec then code-quality). Aligned with [[feedback_subagent_driven_development_validated]] precedent (PR #239 / #286). 6 tasks × 3 subagents (implementer + 2 reviewers) ≈ 18 subagent invocations.

2. **Inline Execution** — Execute tasks in current session using superpowers:executing-plans; batch with checkpoints at end of Task 3 (mid-point regression check) and end of Task 6 (final).

Which approach?
