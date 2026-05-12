# revise-mode — modify an existing playbook entry

**Trigger**: user points at an existing clause file (e.g. `legal-playbook/confidentiality.md`) or says "update X" / "改 LoL 的 fallback" / "remove this walk-away".
**Inverse**: see `protocols/bootstrap-mode.md` (no playbook yet) / `protocols/extend-mode.md` (new clause).

---

## Purpose

Revise mode is **selective editing** of an existing entry — only the fields the user wants to change get touched. Everything else stays byte-identical. The mode shows a diff, asks for confirmation, then writes.

Three common revise flows:

1. **Tighten / loosen a fallback**: contract-review surfaced that the user's Fallback 1 was triggered too often → user wants to revise either to a stricter walk-away or to a softer fallback
2. **Customise a seeded entry**: bootstrap Path A copied `escalate_to: [請編輯…]` placeholders → user comes back to fill in their actual escalate role
3. **Regulation-watch hit**: (Phase 4) `legal-regulation-watch` flagged that the user's DPA fallback no longer aligns with 個資法 2025/11 新制 → user revises

---

## Pipeline

### Step 1 — Identify the target

The user provides a target in one of these forms:

- An absolute / relative file path: `legal-playbook/confidentiality.md` or `<cwd>/legal-playbook/limitation-of-liability/mid-deal.md`
- A clause id: `confidentiality` → resolve to file path (error if multiple variant files exist; ask for variant id)
- A clause id + variant id: `limitation-of-liability/mid-deal`
- "The one I just reviewed" — only works if a previous skill output in the same session referenced an entry; otherwise ask

**Validate**: the target file exists. If it doesn't, abort and suggest `extend-mode` instead.

### Step 2 — Load and parse

Read the file. Parse frontmatter as YAML; keep body as raw markdown blocks (split by `^## ` headers). Compute a checksum / hash for later diff display.

Validate the file has the required fields for its layout (flat / variant / _clause). If validation fails (corrupt frontmatter, missing required field), abort with a clear error and suggest the user repair manually.

### Step 3 — Ask what to change

Show the user a numbered list of revisable fields:

```
Current entry: <cwd>/legal-playbook/confidentiality.md (flat layout)

Revisable fields:
  Frontmatter:
   [1] walk_away_triggers     (3 entries)
   [2] escalate_to            (current: "[請編輯為你公司的角色：法務主管 / GC / 部門主管]")
   [3] risk_default           (current: yellow)
   [4] contract_types_applicable (current: [SaaS, MSA, NDA])
   [5] owner                  (current: "[請編輯為你的姓名]")
   [6] last_updated           (current: 2026-05-09; bumping is automatic on save)
  Body:
   [7] 偏好立場
   [8] Fallback 1
   [9] Fallback 2             (not present — add new)
   [10] 為什麼這條重要
   [11] 替代條款文字         (not present — add new)
   [12] 相關判例             (not present — add new)

Which field(s) do you want to change? (comma-separated, or "all" for everything)
```

The user picks 1+ fields.

### Step 4 — Targeted interview

For each selected field, run a tiny single-question interview, seeded with the current value as default. Example:

For walk_away_triggers (field 1):
```
Current walk_away_triggers:
  - 單方面（只我方有義務）
  - 永久保密（影響營運）
  - <something else>

What would you like to do?
  (a) Replace all
  (b) Add new triggers (keep existing)
  (c) Remove some triggers
  (d) Edit specific triggers in place
```

For escalate_to (field 2):
```
Current: "[請編輯為你公司的角色：法務主管 / GC / 部門主管]"
This looks like a placeholder. What should escalate_to actually be?

(Common: 法務主管 / GC / 部門主管 / 老闆兼法務 / 外部律師)
```

For body sections, show the current prose then ask for the new version (or for an edit / append):
```
Current "## 偏好立場":
  雙向、5 年、明確定義機密範圍...

What's the new version? (paste full replacement, or describe the change and I'll edit)
```

### Step 5 — Show diff and confirm

After all selected fields have new values, render a unified diff of the changes:

```
Diff for legal-playbook/confidentiality.md:

  frontmatter.walk_away_triggers:
-   - 單方面（只我方有義務）
-   - 永久保密（影響營運）
+   - 單方面（只我方有義務）
+   - 保密期間 > 5 年
+   - 永久保密 (任何情況)

  frontmatter.escalate_to:
-   "[請編輯為你公司的角色：法務主管 / GC / 部門主管]"
+   "法務主管 (王經理)"

  body.## 偏好立場:
-   雙向、5 年、明確定義機密範圍...
+   雙向、5 年、明確定義機密範圍且必須附 schedule A 清單。
+   重要：客戶資料一律納入機密範圍。

  frontmatter.last_updated:
-   2026-05-09
+   2026-05-11

Confirm? (yes / no / re-edit)
```

- yes → write
- no → discard changes; exit
- re-edit → go back to Step 4

### Step 6 — Write and validate (v0.2.0+ Phase 1.5)

Write the new file content. Then invoke `validate_schema.py` against
the just-written file (see extend-mode Step 6 for command). On hard
errors, prompt user to fix before continuing.

If the change introduced a variant-upgrade trigger (e.g. user added "對 enterprise 客戶我們會放鬆" to a walk_away), prompt the upgrade offer (see SKILL.md §"Variant-upgrade detection").

### Step 7 — Conflict re-check (v0.2.0+ Phase 1.5)

Any change to `gates` or `clause_id` can introduce conflicts with other entries. Run `detect_conflicts.py` over the whole `legal-playbook/` (see extend-mode Step 7 for command) and report.

### Step 8 — Report

```
✅ Revised <cwd>/legal-playbook/<file>
Fields changed: <count> (<list>)
Validation: PASS / WARN: <issue>
Conflicts: none / <list>
last_updated bumped to: <today>

Suggested next:
- [ ] Revise another clause? Type: revise <clause-id>
- [ ] Run a contract review against the updated playbook? /legal-contract-review <path>
- [ ] Look at the change history? (git log legal-playbook/<file>)
- [ ] Exit. (Your file is saved.)
```

---

## Output contract

```
✅ revise-mode complete.
   File: <path>
   Fields changed: <count>
   Validation: PASS / WARN
   Variant upgrade offered: yes / no
```

---

## Edge cases

- **Whole-file overwrite**: if the user picks "all" in Step 3, run the full 5-question interview (same as extend mode Step 3) but pre-seed every prompt with the current value as default. User can type "keep" to retain any individual value.
- **Concurrent edit**: if the file's mtime is newer than what we read in Step 2 (someone else edited the file mid-session), abort and tell the user to re-read.
- **Diff is empty** (user didn't actually change anything): tell the user "no effective change", do not bump `last_updated`, exit cleanly.
- **User reverts the placeholder to itself** (escalate_to remained `[請編輯…]`): warn that the placeholder is still present; ask for confirmation; if confirmed, proceed (don't block — user might want to defer the decision).
- **Variant file `_clause.md`** target: revise mode supports this; the field list in Step 3 shows the fields valid for `_clause.md` (clause_id / contract_types_applicable / has_variants / market_data / etc.) rather than the full per-variant set.
- **Phase 1.5 hook**: when `scripts/detect_conflicts.py` exists, Step 7 runs it for real. Phase 1 only does a naive in-skill scan.
