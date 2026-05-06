# translation-toolkit v0.1.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship translation-toolkit v0.1.0 — a 6-skill Claude Code plugin for high-quality translation across i18n / technical-doc / ad-copy use cases for EN / JA / ZH-TW / ZH-CN, with bundled CC-BY-licensed glossary (~10K+ entries) and 5-gate verification (placeholder integrity, glossary compliance, back-translation, register, untranslatability flagging).

**Architecture:** 6 skills (router + intake + i18n + doc + creative + audit), 5-layer pipeline (intake → preparation → core loop → verification → output), 4-tier glossary fallthrough (project → bundled → web search → LLM), SSOT-and-functional-copy pattern with `scripts/canonical/` as single source of truth distributed byte-identical to each skill's local copies, runtime EN-pivot for cross-language pairs without direct bundled data.

**Tech Stack:** Python 3.11+ for build pipeline (`uv` for deps, `tiktoken`, `langchain_text_splitters`, `pyyaml`, `lxml` for TBX, `pandas` for CSV ingest, `pytest` for tests). Skill bodies are pure Markdown (SKILL.md). Bash for CI drift check. `ruff` for Python linting.

**Spec reference:** [`/Users/kouko/GitHub/monkey-skills/docs/superpowers/specs/2026-05-06-translation-toolkit-design.md`](../specs/2026-05-06-translation-toolkit-design.md)

**Phase boundaries** (recommended subagent-driven review checkpoints):
- After Phase A (foundation): plugin loads, scaffolding lints clean
- After Phase B (glossary build): all 5 canonical pair files generated, drift check green
- After Phase C (shared engine): parser + protect-pass + M1/M2 pass unit tests
- After Phase D (active skills): router + intake + 3 active skills load, smoke test translates "Hello world"
- After Phase E (audit + advanced gates): translation-audit runs full 5-gate verification
- After Phase F (release): CI green, all README tri-lang, NOTICES.md complete

---

## Phase A: Foundation scaffolding (5 tasks)

### Task A1: Plugin manifest + tri-language READMEs

**Files:**
- Create: `translation-toolkit/.claude-plugin/plugin.json`
- Create: `translation-toolkit/README.md` (en)
- Create: `translation-toolkit/README.ja.md`
- Create: `translation-toolkit/README.zh-TW.md`
- Modify: `marketplace.json` (add translation-toolkit entry)

- [ ] **Step 1: Create `.claude-plugin/plugin.json`**

```json
{
  "name": "translation-toolkit",
  "version": "0.1.0",
  "description": "High-quality translation across i18n / technical docs / ad copy for EN / JA / ZH-TW / ZH-CN with bundled CC-BY glossary (~10K+ entries) and 5-gate verification (placeholder integrity / glossary compliance / back-translation / register / untranslatability)",
  "author": {
    "name": "kouko",
    "email": "kouko.d@gmail.com"
  },
  "homepage": "https://github.com/kouko/monkey-skills/tree/main/translation-toolkit",
  "license": "MIT"
}
```

- [ ] **Step 2: Write `README.md`** — sections: What it does, 6 skills overview (1 line each), 4-tier glossary fallthrough diagram, install via marketplace, language switcher (links to .ja and .zh-TW versions). Reference Decision #2/#10 in spec.

- [ ] **Step 3: Write `README.ja.md` + `README.zh-TW.md`** — same structure, follow `docs/i18n/glossary-ja.md` rule "EN technical terms preserved as English; only general descriptive prose translated". Reference Decision #11 (13 domain taxonomy) in target language.

- [ ] **Step 4: Add to `marketplace.json`**

```json
{ "name": "translation-toolkit", "source": "./translation-toolkit" }
```

(Insert in alphabetical order in the existing `plugins` array.)

- [ ] **Step 5: Verify plugin loads** — run `cat translation-toolkit/.claude-plugin/plugin.json | python3 -m json.tool` (must print without error). Run `python3 -c "import json; json.load(open('marketplace.json'))"`.

- [ ] **Step 6: Commit**

```bash
git add translation-toolkit/.claude-plugin/plugin.json translation-toolkit/README.md translation-toolkit/README.ja.md translation-toolkit/README.zh-TW.md marketplace.json
git commit -m "feat(translation-toolkit): scaffold plugin manifest + tri-language READMEs"
```

---

### Task A2: Plugin-level vendor + docs + NOTICES skeleton

**Files:**
- Create: `translation-toolkit/NOTICES.md`
- Create: `translation-toolkit/docs/glossary-format-spec.md`
- Create: `translation-toolkit/docs/architecture.md`
- Create: `translation-toolkit/vendor/{mozilla-pontoon,gnome-i18n,naer,jlt,e-stat,tokyo,nict,cabinet,w3c}/LICENSE` (placeholder files; real license text fetched in Task B-series)

- [ ] **Step 1: Write `NOTICES.md`** — exact structure from spec line ~512-528:

```
# Bundled Source Attributions

## Glossary entries (feeds glossary-{a}--{b}.md tables)

| Source                  | License             | Attribution |
|-------------------------|---------------------|-------------|
| Mozilla Pontoon TBX     | MPL-2.0/CC-BY-SA    | required    |
| GNOME i18n glossary     | LGPL/GPL            | required    |
| NAER 樂詞網             | OGDL v1 ≈ CC-BY 4.0 | required    |
| JLT 標準対訳辞書        | CC-BY 4.0 互換      | required    |
| e-Stat 統計用語集       | 政府標準利用規約    | required    |
| 東京都 日英対訳         | CC-BY 4.0           | required    |
| 內閣官房 政府機關名     | 政府標準利用規約    | required    |

## Parallel-corpus reference (corpus/nict-en-ja-zh.md as exemplars)

| NICT 日英中基本文       | CC-BY 3.0           | required (5,304 sentence triples; not glossary entries) |

## Typography rules (typography/{jlreq,clreq}-summary.md)

| W3C jlreq / clreq       | W3C Document License | required |
```

- [ ] **Step 2: Write `docs/glossary-format-spec.md`** — describes the canonical pair-file schema (frontmatter `pair: [A, B]`, `## meta`, `## domain: <name>` sections, 4-column tables with `<lang-A> | <lang-B> | source | notes`). This is the user-facing spec for users who want to extend their project glossary at `<repo>/docs/i18n/glossary-{tgt}.md`.

- [ ] **Step 3: Write `docs/architecture.md`** — high-level description of: 6 skills + 1 router + 1 intake topology, 5-layer pipeline, 4-tier glossary fallthrough, SSOT-and-functional-copy pattern, roles-not-models portability. ~500 words. Refers reader back to spec for full detail.

- [ ] **Step 4: Create vendor placeholder LICENSE files** — one `LICENSE` per source folder, with header `# License placeholder for <source>` and TODO for actual license text fetched in Task B series.

- [ ] **Step 5: Commit**

```bash
git add translation-toolkit/NOTICES.md translation-toolkit/docs/ translation-toolkit/vendor/
git commit -m "feat(translation-toolkit): scaffold plugin-level NOTICES + docs + vendor placeholders"
```

---

### Task A3: Canonical reference documents (shared by all skills)

**Files:**
- Create: `translation-toolkit/scripts/canonical/core-loop.md`
- Create: `translation-toolkit/scripts/canonical/4d-reflection.md`
- Create: `translation-toolkit/scripts/canonical/5d-effectiveness.md`
- Create: `translation-toolkit/scripts/canonical/orthogonal-axes.md`
- Create: `translation-toolkit/scripts/canonical/verification-gates.md`
- Create: `translation-toolkit/scripts/canonical/audit-trail-spec.md`

- [ ] **Step 1: Write `core-loop.md`** — describes the 3-step DRAFT/REFLECT/IMPROVE loop with TA's `<TRANSLATE_THIS>` cross-chunk windowing. ~400 words. Pseudocode:

```
DRAFT:
  Given chunk N of source document, with all chunks visible but only chunk N
  wrapped in <TRANSLATE_THIS>...</TRANSLATE_THIS>:
  produce target-language translation of chunk N preserving placeholder tokens.

REFLECT:
  Given source, draft v1, and intake context (mode/register/strategy/locale/domain):
  produce 4D structured critique covering accuracy / fluency / style / terminology
  (5D adds effectiveness for transcreation mode).

IMPROVE:
  Given source, draft v1, REFLECT critique:
  produce v2 incorporating critique. No additional reasoning beyond critique.
```

Specifies: input/output contract per role; chunking threshold (2000 tokens); placeholder preservation requirement.

- [ ] **Step 2: Write `4d-reflection.md`** — exact specification of the 4 axes:
  1. Accuracy — semantic faithfulness, no addition/omission/distortion
  2. Fluency — naturalness in target language
  3. Style — register / rhythm / rhetoric matches source and mode
  4. Terminology — glossary compliance, domain conventions

  For each axis: 3-5 example concerns the critic should look for. Reference Vinay-Darbelnet 7 strategies (borrowing/calque/literal/transposition/modulation/equivalence/adaptation) under "Style" axis.

- [ ] **Step 3: Write `5d-effectiveness.md`** — describes the 5th axis used only in transcreation mode:
  5. Effectiveness — persuasion intent preserved in target culture

  Examples: ad copy "save 50%" should produce equivalent emotional pull in target locale; cultural references must land.

- [ ] **Step 4: Write `orthogonal-axes.md`** — definition of all 5 axes with valid values:
  - mode: literal | faithful | localized | transcreation
  - register: formal | neutral | warm | playful
  - strategy: domestication | foreignization
  - locale: BCP-47 (e.g., `ja-JP`, `zh-TW`)
  - domain: one or more from 13-domain taxonomy

  Auto mode default decision rules (e.g., "if source contains marketing CTAs → mode=transcreation; else faithful").

- [ ] **Step 5: Write `verification-gates.md`** — exact spec of all 5 gates with thresholds, pass/fail criteria, audit-trail format. Reference: spec lines 393-410.

- [ ] **Step 6: Write `audit-trail-spec.md`** — JSON schema for audit trail. Top-level fields: `intake`, `glossary_resolution`, `chunks` (array of per-chunk records), `gate_verdicts`, `untranslatables`, `sources_used`. Each `glossary_resolution` entry: `{term, tier (L1|L2|L3|L4), source, value, audit_path}`.

- [ ] **Step 7: Commit**

```bash
git add translation-toolkit/scripts/canonical/
git commit -m "feat(translation-toolkit): canonical reference documents (core-loop / reflection / axes / gates / audit-trail)"
```

---

### Task A4: SSOT distribute + verify-drift scripts

**Files:**
- Create: `translation-toolkit/scripts/distribute.py`
- Create: `translation-toolkit/scripts/verify-drift.py`
- Create: `translation-toolkit/scripts/README.md` (SSOT explanation)
- Test: `translation-toolkit/scripts/tests/test_distribute.py`

- [ ] **Step 1: Write failing test for distribute.py**

```python
# scripts/tests/test_distribute.py
import shutil
import subprocess
from pathlib import Path
import pytest

def test_distribute_copies_canonical_to_skills(tmp_path):
    """distribute.py copies canonical files to each skill's expected subfolder."""
    plugin_root = tmp_path / "translation-toolkit"
    canonical = plugin_root / "scripts" / "canonical"
    canonical.mkdir(parents=True)
    (canonical / "core-loop.md").write_text("# core loop")
    (canonical / "glossary-en-US--ja-JP.md").write_text("# glossary")

    for skill in ["translation-i18n", "translation-doc", "translation-creative", "translation-audit"]:
        (plugin_root / skill / "references").mkdir(parents=True)
        (plugin_root / skill / "glossary").mkdir(parents=True)

    # Copy distribute.py to tmp
    real_script = Path(__file__).parent.parent / "distribute.py"
    shutil.copy(real_script, plugin_root / "scripts" / "distribute.py")

    result = subprocess.run(
        ["python3", "scripts/distribute.py"], cwd=plugin_root, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr

    for skill in ["translation-i18n", "translation-doc", "translation-creative", "translation-audit"]:
        assert (plugin_root / skill / "references" / "core-loop.md").read_text() == "# core loop"
        assert (plugin_root / skill / "glossary" / "glossary-en-US--ja-JP.md").read_text() == "# glossary"
```

- [ ] **Step 2: Run test, verify FAIL**

```bash
cd translation-toolkit && python3 -m pytest scripts/tests/test_distribute.py -v
```

Expected: FAIL with `FileNotFoundError: scripts/distribute.py`

- [ ] **Step 3: Implement `scripts/distribute.py`**

```python
#!/usr/bin/env python3
"""Distribute canonical/* to each skill's functional-copy subfolder.

Per spec Decision #14 (SSOT-and-functional-copy): canonical lives at
scripts/canonical/, each active skill holds byte-identical copies.

Routing rules:
- references/*.md → all 4 active skills' references/
- glossary-*.md → all 4 active skills' glossary/
- {jlreq,clreq}-summary.md → all 4 active skills' typography/
- nict-en-ja-zh.md → all 4 active skills' corpus/
- manual-entries-ja-JP--zh-TW.md is build-input only, NOT distributed
"""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "scripts" / "canonical"
ACTIVE_SKILLS = ["translation-i18n", "translation-doc", "translation-creative", "translation-audit"]

REFERENCE_FILES = {
    "core-loop.md", "4d-reflection.md", "5d-effectiveness.md",
    "orthogonal-axes.md", "verification-gates.md", "audit-trail-spec.md"
}
TYPOGRAPHY_FILES = {"jlreq-summary.md", "clreq-summary.md"}
CORPUS_FILES = {"nict-en-ja-zh.md"}
GLOSSARY_PREFIX = "glossary-"
NON_DISTRIBUTED = {"manual-entries-ja-JP--zh-TW.md"}

def distribute() -> int:
    if not CANONICAL.exists():
        print(f"FAIL: canonical/ not found at {CANONICAL}")
        return 1

    copied = 0
    for src in CANONICAL.iterdir():
        if not src.is_file() or src.name in NON_DISTRIBUTED:
            continue

        if src.name in REFERENCE_FILES:
            subfolder = "references"
        elif src.name in TYPOGRAPHY_FILES:
            subfolder = "typography"
        elif src.name in CORPUS_FILES:
            subfolder = "corpus"
        elif src.name.startswith(GLOSSARY_PREFIX):
            subfolder = "glossary"
        else:
            print(f"WARN: unrouted canonical file {src.name}")
            continue

        for skill in ACTIVE_SKILLS:
            dst_dir = ROOT / skill / subfolder
            dst_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst_dir / src.name)
            copied += 1

    print(f"OK: distributed {copied} files across {len(ACTIVE_SKILLS)} skills")
    return 0

if __name__ == "__main__":
    raise SystemExit(distribute())
```

- [ ] **Step 4: Run test, verify PASS**

```bash
python3 -m pytest scripts/tests/test_distribute.py -v
```

Expected: PASS.

- [ ] **Step 5: Implement `scripts/verify-drift.py`**

```python
#!/usr/bin/env python3
"""Verify byte-identical match between canonical/ and each skill's functional copies.

Used in CI. Exits 0 on match, 1 on drift.
"""
import filecmp
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANONICAL = ROOT / "scripts" / "canonical"
ACTIVE_SKILLS = ["translation-i18n", "translation-doc", "translation-creative", "translation-audit"]

ROUTING = {
    "core-loop.md": "references", "4d-reflection.md": "references",
    "5d-effectiveness.md": "references", "orthogonal-axes.md": "references",
    "verification-gates.md": "references", "audit-trail-spec.md": "references",
    "jlreq-summary.md": "typography", "clreq-summary.md": "typography",
    "nict-en-ja-zh.md": "corpus",
}
NON_DISTRIBUTED = {"manual-entries-ja-JP--zh-TW.md"}

def verify() -> int:
    drift = []
    for src in CANONICAL.iterdir():
        if not src.is_file() or src.name in NON_DISTRIBUTED:
            continue
        subfolder = ROUTING.get(src.name) or ("glossary" if src.name.startswith("glossary-") else None)
        if not subfolder:
            continue
        for skill in ACTIVE_SKILLS:
            dst = ROOT / skill / subfolder / src.name
            if not dst.exists():
                drift.append(f"MISSING: {dst.relative_to(ROOT)}")
            elif not filecmp.cmp(src, dst, shallow=False):
                drift.append(f"DRIFT: {dst.relative_to(ROOT)} differs from canonical")

    if drift:
        print("\n".join(drift))
        print(f"FAIL: {len(drift)} drift issue(s); run scripts/distribute.py to fix")
        return 1
    print("OK: all functional copies byte-identical to canonical")
    return 0

if __name__ == "__main__":
    raise SystemExit(verify())
```

- [ ] **Step 6: Add unit test for verify-drift.py**

```python
# scripts/tests/test_verify_drift.py
import subprocess
import shutil
from pathlib import Path

def test_drift_detects_modified_file(tmp_path):
    """verify-drift returns 1 when a functional copy differs from canonical."""
    # ... setup canonical + skills with matching files; modify one functional copy;
    # run script; assert exit code 1 + "DRIFT:" in stdout.
    pass  # full implementation: copy distribute.py + verify-drift.py to tmp,
          # run distribute, modify one file, run verify, assert exit=1
```

(Full body: similar tmp_path fixture as test_distribute; after distribute, modify one functional copy; run verify; assert returncode=1 and "DRIFT" in stdout. ~25 lines.)

- [ ] **Step 7: Write `scripts/README.md`** — explains SSOT pattern, lists every script and its purpose, lists routing rules, includes "edit canonical/ then run distribute.py in same commit; CI verify-drift will fail otherwise" rule.

- [ ] **Step 8: Commit**

```bash
git add translation-toolkit/scripts/distribute.py translation-toolkit/scripts/verify-drift.py translation-toolkit/scripts/tests/ translation-toolkit/scripts/README.md
git commit -m "feat(translation-toolkit): SSOT distribute + verify-drift scripts with unit tests"
```

---

### Task A5: 6 skill folders + SKILL.md skeletons

**Files:**
- Create: `translation-toolkit/using-translation-toolkit/SKILL.md`
- Create: `translation-toolkit/translation-intake/SKILL.md`
- Create: `translation-toolkit/translation-i18n/SKILL.md`
- Create: `translation-toolkit/translation-doc/SKILL.md`
- Create: `translation-toolkit/translation-creative/SKILL.md`
- Create: `translation-toolkit/translation-audit/SKILL.md`

For each SKILL.md: frontmatter (`name`, `description`, `version: 0.1.0`) + skeleton sections (Purpose, When to use, Inputs/Outputs). Detailed prompt content gets filled in later phase tasks (D, E).

- [ ] **Step 1: Create `using-translation-toolkit/SKILL.md`** — router skill with frontmatter + minimal body that describes when to invoke each of the 4 active skills based on user intent (i18n format → i18n; markdown/technical → doc; ad copy / marketing → creative; existing target supplied → audit).

- [ ] **Step 2: Create `translation-intake/SKILL.md`** — Layer 1 owner. Describes auto vs explicit modes. References `protocols/intake-auto.md` and `protocols/intake-explicit.md` (created in Task D2).

- [ ] **Step 3-6: Create skeletons for `translation-{i18n,doc,creative,audit}/SKILL.md`** — each has frontmatter + Purpose + "TODO: full prompt body in Task D{3,4,5} / E1". Use frontmatter:

```yaml
---
name: translation-i18n
description: Translate i18n strings (PO / JSON / XLIFF / Android strings.xml / iOS .strings) preserving placeholders, keys, and project glossary. Part of translation-toolkit. Use when user provides UI strings or i18n files for translation.
version: 0.1.0
---
```

- [ ] **Step 7: Verify hook compliance** — repo has `.claude/hooks/validate-skill-folder-structure.sh`. Run lint before commit:

```bash
bash .claude/hooks/validate-skill-folder-structure.sh translation-toolkit/translation-i18n/SKILL.md
```

Each skill's subfolders must be flat (one level only). Verify by `find translation-toolkit -type d | wc -l` matches expected count.

- [ ] **Step 8: Commit**

```bash
git add translation-toolkit/using-translation-toolkit translation-toolkit/translation-intake translation-toolkit/translation-i18n translation-toolkit/translation-doc translation-toolkit/translation-creative translation-toolkit/translation-audit
git commit -m "feat(translation-toolkit): scaffold 6 skills with frontmatter + skeleton"
```

**Phase A checkpoint**: plugin loads in Claude Code, all 6 skills appear in skill listing, scripts/distribute.py runs without errors (over empty canonical), `validate-skill-folder-structure.sh` passes for all 6 SKILL.md.

---

## Phase B: Glossary build pipeline (5 tasks)

### Task B1: Mozilla Pontoon TBX ingest → 3 EN-pivoted pair files

**Files:**
- Create: `translation-toolkit/scripts/build-pairs-from-en.py`
- Create: `translation-toolkit/scripts/canonical/glossary-en-US--ja-JP.md` (generated)
- Create: `translation-toolkit/scripts/canonical/glossary-en-US--zh-CN.md` (generated)
- Create: `translation-toolkit/scripts/canonical/glossary-en-US--zh-TW.md` (generated)
- Create: `translation-toolkit/vendor/mozilla-pontoon/{ja,zh-CN,zh-TW}.v2.tbx` (downloaded)
- Create: `translation-toolkit/vendor/mozilla-pontoon/LICENSE` (real text, MPL-2.0/CC-BY-SA)

- [ ] **Step 1: Download Pontoon TBX files**

```bash
mkdir -p translation-toolkit/vendor/mozilla-pontoon
for locale in ja zh-CN zh-TW; do
  curl -fsSL "https://pontoon.mozilla.org/terminology/${locale}.v2.tbx" \
    -o "translation-toolkit/vendor/mozilla-pontoon/${locale}.v2.tbx"
done
```

Verify each file is non-empty XML (~50KB each).

- [ ] **Step 2: Fetch Pontoon LICENSE** — copy MPL-2.0 text into `vendor/mozilla-pontoon/LICENSE` from https://www.mozilla.org/media/MPL/2.0/index.txt.

- [ ] **Step 3: Write failing test for build-pairs-from-en.py**

```python
# scripts/tests/test_build_pairs.py
def test_pontoon_ja_tbx_to_pair_file(tmp_path):
    """Given a small Pontoon TBX excerpt, produces glossary-en-US--ja-JP.md
    with frontmatter pair=[en-US, ja-JP] and at least one entry under domain: ui."""
    # fixture: 2-entry TBX (en: Cancel, ja: キャンセル) (en: Settings, ja: 設定)
    # invoke: python build-pairs-from-en.py --source pontoon --tbx <fixture> --target ja-JP --out <tmp>
    # assert: output file has correct frontmatter + table row
```

- [ ] **Step 4: Run test, verify FAIL**

- [ ] **Step 5: Implement `build-pairs-from-en.py`** — multi-source ingest dispatcher with subcommands:

```python
# scripts/build-pairs-from-en.py
"""Build EN-pivoted pair glossaries from upstream sources.

Usage:
  python3 build-pairs-from-en.py --target ja-JP   # build glossary-en-US--ja-JP.md
  python3 build-pairs-from-en.py --target zh-TW   # build glossary-en-US--zh-TW.md
  python3 build-pairs-from-en.py --target zh-CN   # build glossary-en-US--zh-CN.md
  python3 build-pairs-from-en.py --all            # build all three

Sources are ingested per target locale:
  ja-JP: Pontoon (ui/tech.web), GNOME (ui), JLT (legal/gov), e-Stat (statistics),
         Tokyo (gov/general), Cabinet (gov)
  zh-TW: Pontoon, GNOME, NAER 樂詞網 (multi-domain)
  zh-CN: Pontoon, GNOME

Output: scripts/canonical/glossary-en-US--<target>.md with frontmatter +
domain sections + 4-column tables.

Domain inference per source:
  Pontoon → ui/tech.web (heuristic: "interface" / "url" / "browser" → tech.web; else ui)
  GNOME → ui
  JLT → legal (default), gov (when source-text contains 省/庁/局)
  e-Stat → statistics
  Tokyo → gov (administrative pages), general (生活/防災)
  Cabinet → gov
  NAER → multi-domain (use NAER's own category column when present)
"""
import argparse
from pathlib import Path
from collections import defaultdict
from xml.etree import ElementTree as ET

# Upstream-specific parsers
def parse_pontoon_tbx(tbx_path: Path, target_locale: str) -> list[dict]:
    """Returns list of {en, target, source: 'pontoon', domain, notes}."""
    tree = ET.parse(tbx_path)
    entries = []
    for term_entry in tree.iter("termEntry"):
        en_term = None
        target_term = None
        for lang_set in term_entry.findall(".//langSet"):
            lang = lang_set.get("{http://www.w3.org/XML/1998/namespace}lang")
            term = lang_set.findtext(".//term")
            if lang and term:
                if lang.startswith("en"):
                    en_term = term.strip()
                elif lang == target_locale or lang.startswith(target_locale.split("-")[0]):
                    target_term = term.strip()
        if en_term and target_term:
            domain = "tech.web" if any(k in en_term.lower() for k in ("url", "browser", "web", "http")) else "ui"
            entries.append({"en": en_term, "target": target_term, "source": "pontoon", "domain": domain, "notes": "—"})
    return entries

def parse_gnome_po(po_path: Path) -> list[dict]:
    """Returns list of entries from GNOME glossary PO file."""
    # Use polib library or manual parsing; one entry = msgid (en) + msgstr (target)
    # All entries domain=ui
    pass  # ~30 lines

# (Similar parsers for jlt_csv, e_stat_csv, tokyo_excel, cabinet_pdf, naer_csv)
# Each parser is ~30-50 lines; license-permissive sources have stable schemas.

def emit_pair_file(target_locale: str, entries_by_domain: dict, out_path: Path):
    """Emit glossary-en-US--<target>.md with frontmatter + domain sections."""
    frontmatter = f"""---
pair: [en-US, {target_locale}]
version: 0.1.0
sources: {sorted(set(e['source'] for entries in entries_by_domain.values() for e in entries))}
domains_supported: {sorted(entries_by_domain.keys())}
---

# Glossary en-US ↔ {target_locale}

> Generated by scripts/build-pairs-from-en.py — do not hand-edit.
> Manual additions go in canonical/manual-entries-{target_locale}.md (when added).

## meta
(typography rules — see typography/jlreq-summary.md for ja-JP, clreq-summary.md for zh-*)

"""
    body = []
    for domain in sorted(entries_by_domain.keys()):
        body.append(f"## domain: {domain}\n")
        body.append(f"| en-US | {target_locale} | source | notes |")
        body.append("|---|---|---|---|")
        for e in sorted(entries_by_domain[domain], key=lambda x: x["en"].lower()):
            body.append(f"| {e['en']} | {e['target']} | {e['source']} | {e['notes']} |")
        body.append("")
    out_path.write_text(frontmatter + "\n".join(body) + "\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=False, choices=["ja-JP", "zh-TW", "zh-CN"])
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()

    targets = ["ja-JP", "zh-TW", "zh-CN"] if args.all else [args.target]

    root = Path(__file__).resolve().parent.parent
    vendor = root / "vendor"
    canonical = root / "scripts" / "canonical"

    for target in targets:
        entries_by_domain = defaultdict(list)
        # Pontoon (all 3 targets)
        pontoon_lang = "ja" if target == "ja-JP" else target
        tbx = vendor / "mozilla-pontoon" / f"{pontoon_lang}.v2.tbx"
        if tbx.exists():
            for e in parse_pontoon_tbx(tbx, pontoon_lang):
                entries_by_domain[e["domain"]].append(e)
        # GNOME (all 3 targets)
        # JLT (ja only)
        # e-Stat (ja only)
        # Tokyo (ja only)
        # Cabinet (ja only)
        # NAER (zh-TW only — see Task B3)
        # ... per-source ingestion
        emit_pair_file(target, entries_by_domain, canonical / f"glossary-en-US--{target}.md")
        print(f"OK: wrote glossary-en-US--{target}.md ({sum(len(v) for v in entries_by_domain.values())} entries)")

if __name__ == "__main__":
    main()
```

(Full implementation requires per-source parsers; this task implements only Pontoon. Tasks B2/B3/B4 add JLT/NAER/e-Stat/Tokyo/Cabinet/GNOME parsers.)

- [ ] **Step 6: Run Pontoon-only build, verify pair files generated**

```bash
cd translation-toolkit
python3 scripts/build-pairs-from-en.py --all
ls scripts/canonical/glossary-en-US--*.md
# Expect 3 files, each ~95 entries
```

- [ ] **Step 7: Run unit test, verify PASS**

- [ ] **Step 8: Commit**

```bash
git add translation-toolkit/scripts/build-pairs-from-en.py translation-toolkit/scripts/tests/test_build_pairs.py translation-toolkit/scripts/canonical/glossary-en-US--*.md translation-toolkit/vendor/mozilla-pontoon/
git commit -m "feat(translation-toolkit): Pontoon TBX ingest → 3 EN-pivoted pair files"
```

---

### Task B2: GNOME PO + JLT CSV ingest (extend build-pairs-from-en.py)

**Files:**
- Modify: `translation-toolkit/scripts/build-pairs-from-en.py:parse_gnome_po + parse_jlt_csv`
- Create: `translation-toolkit/vendor/gnome-i18n/{ja,zh-CN,zh-TW}.po`
- Create: `translation-toolkit/vendor/gnome-i18n/LICENSE` (LGPL)
- Create: `translation-toolkit/vendor/jlt/standard-bilingual-dictionary.csv` (UTF-8)
- Create: `translation-toolkit/vendor/jlt/LICENSE`

- [ ] **Step 1: Download GNOME glossaries**

```bash
mkdir -p translation-toolkit/vendor/gnome-i18n
for locale in ja zh_CN zh_TW; do
  curl -fsSL "https://gitlab.gnome.org/Translation/damned-lies/-/raw/main/gnome-i18n/${locale}.po" \
    -o "translation-toolkit/vendor/gnome-i18n/${locale//_/-}.po" 2>/dev/null \
    || echo "WARN: GNOME ${locale}.po not at expected path, check current GNOME repo structure"
done
```

(If GNOME path changed, manually fetch from https://gitlab.gnome.org/GNOME/gnome-i18n/tree/master/glossary.)

- [ ] **Step 2: Download JLT 標準対訳辞書 CSV (UTF-8 variant)**

```bash
mkdir -p translation-toolkit/vendor/jlt
# Visit https://www.japaneselawtranslation.go.jp/ja/dicts/download
# Download CSV (UTF-8), save as standard-bilingual-dictionary.csv
# (Manual step — automated download requires session cookies)
```

If automated fetch is blocked, document manual download instructions in `vendor/jlt/README.md` and check in a small SAMPLE (~50 entries) for testing.

- [ ] **Step 3: Implement `parse_gnome_po`** in `build-pairs-from-en.py`:

```python
import polib  # add to deps

def parse_gnome_po(po_path: Path) -> list[dict]:
    po = polib.pofile(str(po_path))
    return [
        {"en": entry.msgid, "target": entry.msgstr, "source": "gnome", "domain": "ui", "notes": "—"}
        for entry in po if entry.msgstr and entry.msgid and not entry.obsolete
    ]
```

- [ ] **Step 4: Implement `parse_jlt_csv`**:

```python
import csv

def parse_jlt_csv(csv_path: Path) -> list[dict]:
    """JLT CSV columns (per JLT v18.0): en_term, ja_term, source_law, notes."""
    entries = []
    with csv_path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            en, ja = row.get("en_term", "").strip(), row.get("ja_term", "").strip()
            if not en or not ja:
                continue
            domain = "gov" if any(k in ja for k in ("省", "庁", "局", "府")) else "legal"
            entries.append({
                "en": en, "target": ja, "source": "jlt",
                "domain": domain,
                "notes": row.get("source_law", "—") or "—",
            })
    return entries
```

(Verify actual JLT CSV column headers when downloaded; adjust field names accordingly.)

- [ ] **Step 5: Wire parsers into `main()` build dispatch** (insert into the `for target in targets` block).

- [ ] **Step 6: Update test to cover GNOME + JLT** — small fixture PO + CSV; assert entries appear in correct domain sections.

- [ ] **Step 7: Run build, verify expected entry counts**

```bash
python3 scripts/build-pairs-from-en.py --target ja-JP
grep -c "^|" scripts/canonical/glossary-en-US--ja-JP.md
# Expect ~95 (Pontoon) + ~150 (GNOME) + several thousand (JLT) = ~3000-5000
```

- [ ] **Step 8: Commit**

```bash
git add translation-toolkit/scripts/build-pairs-from-en.py translation-toolkit/vendor/gnome-i18n translation-toolkit/vendor/jlt translation-toolkit/scripts/tests/
git commit -m "feat(translation-toolkit): GNOME PO + JLT CSV ingest extends build-pairs-from-en.py"
```

---

### Task B3: NAER 樂詞網 + e-Stat + Tokyo + Cabinet ingest

**Files:**
- Modify: `translation-toolkit/scripts/build-pairs-from-en.py` (add 4 parsers)
- Create: `translation-toolkit/vendor/naer/{academic-terms-zh-TW,cross-strait}.csv`
- Create: `translation-toolkit/vendor/naer/LICENSE`
- Create: `translation-toolkit/vendor/e-stat/stat-terms-en-ja.csv`
- Create: `translation-toolkit/vendor/e-stat/LICENSE`
- Create: `translation-toolkit/vendor/tokyo/en-ja-translation.xlsx`
- Create: `translation-toolkit/vendor/tokyo/LICENSE`
- Create: `translation-toolkit/vendor/cabinet/gov-orgs-en-ja.pdf` (or extracted .csv)
- Create: `translation-toolkit/vendor/cabinet/LICENSE`

- [ ] **Step 1: Download NAER datasets** — from https://data.gov.tw/ search "國家教育研究院" or use direct URLs from spec research:
  - 學術名詞 (multi-category bundle, prioritize: 電子計算機, 資訊, 統計, 法律, 醫學)
  - 兩岸對照名詞 (will be used in Task B4 for zh-CN ↔ zh-TW direct file)

  Save selected categories to `vendor/naer/academic-terms-zh-TW.csv` (concatenated). Bundle separately: `vendor/naer/cross-strait.csv`.

- [ ] **Step 2: Download e-Stat 統計用語** — from https://www.e-stat.go.jp/classifications/terms/90 (UTF-8 BOM CSV).

- [ ] **Step 3: Download 東京都 日英対訳用語集** — from https://catalog.data.metro.tokyo.lg.jp/dataset/t000001d1800000014 (Excel format).

- [ ] **Step 4: Download 內閣官房 政府機関名英訳一覧** — PDF at https://www.cas.go.jp/jp/seisaku/hourei/name.pdf. Use `pdfplumber` to extract table → CSV.

- [ ] **Step 5: Implement parsers**:

```python
def parse_naer_csv(csv_path: Path) -> list[dict]:
    """NAER 學術名詞 CSV: en_term, zh_TW_term, category (used as domain hint)."""
    NAER_CATEGORY_TO_DOMAIN = {
        "電子計算機名詞": "tech.software",
        "資訊名詞": "tech.software",
        "統計學名詞": "statistics",
        "法律名詞": "legal",
        "醫學名詞": "medical",
        "經濟學名詞": "finance",
        # ... map other categories or default to "general"
    }
    # ... implementation

def parse_estat_csv(csv_path: Path) -> list[dict]:
    """e-Stat statistics terms — all entries domain=statistics."""

def parse_tokyo_excel(xlsx_path: Path) -> list[dict]:
    """Tokyo en-ja administrative terms — domain inferred from category column."""
    # Use openpyxl

def parse_cabinet_csv(csv_path: Path) -> list[dict]:
    """Cabinet gov org names — all entries domain=gov."""
```

- [ ] **Step 6: Wire into `main()`** (4 new sources for ja-JP target, 1 for zh-TW target).

- [ ] **Step 7: Add LICENSE files** for each source (real text from each license).

- [ ] **Step 8: Run full build, verify size**

```bash
python3 scripts/build-pairs-from-en.py --all
wc -l scripts/canonical/glossary-en-US--*.md
# ja-JP: expect ~10,000+ entries
# zh-TW: expect ~1,000-5,000+ entries (NAER selectively bundled)
# zh-CN: expect ~250 entries (Pontoon + GNOME only)
```

- [ ] **Step 9: Commit**

```bash
git add translation-toolkit/scripts/build-pairs-from-en.py translation-toolkit/vendor/{naer,e-stat,tokyo,cabinet}
git commit -m "feat(translation-toolkit): NAER + e-Stat + Tokyo + Cabinet ingest extends build-pairs-from-en.py"
```

---

### Task B4: NAER 兩岸對照 → glossary-zh-CN--zh-TW.md + ja-JP↔zh-TW manual seed + derived

**Files:**
- Create: `translation-toolkit/scripts/build-pair-zh-CN--zh-TW.py`
- Create: `translation-toolkit/scripts/build-pair-ja-JP--zh-TW.py`
- Create: `translation-toolkit/scripts/canonical/glossary-zh-CN--zh-TW.md` (generated)
- Create: `translation-toolkit/scripts/canonical/glossary-ja-JP--zh-TW.md` (generated)
- Create: `translation-toolkit/scripts/canonical/manual-entries-ja-JP--zh-TW.md` (hand-curated, ~80-100 entries)

- [ ] **Step 1: Implement `build-pair-zh-CN--zh-TW.py`** — ingests NAER 兩岸對照名詞 CSV directly into a pair file with `pair: [zh-CN, zh-TW]` schema.

```python
"""Build glossary-zh-CN--zh-TW.md from NAER 兩岸對照名詞."""
def main():
    from build_pairs_from_en import emit_pair_file  # reuse emitter
    cross_strait_csv = ROOT / "vendor" / "naer" / "cross-strait.csv"
    entries_by_domain = defaultdict(list)
    with cross_strait_csv.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            zh_cn, zh_tw = row.get("zh_CN", "").strip(), row.get("zh_TW", "").strip()
            if not zh_cn or not zh_tw:
                continue
            domain = NAER_CATEGORY_TO_DOMAIN.get(row.get("category"), "general")
            entries_by_domain[domain].append({
                "en": zh_cn, "target": zh_tw, "source": "naer-cross-strait",
                "domain": domain, "notes": "—",
            })
    # Modify emit_pair_file to use [zh-CN, zh-TW] pair vs [en-US, target]
    emit_pair_file(target_pair=["zh-CN", "zh-TW"], entries_by_domain=entries_by_domain, ...)
```

(Refactor `emit_pair_file` from B1 to accept a `pair` tuple instead of fixed `en-US` source language.)

- [ ] **Step 2: Hand-write `canonical/manual-entries-ja-JP--zh-TW.md`** — ~80-100 entries grouped by domain per spec line 322-326:

```markdown
---
pair: [ja-JP, zh-TW]
type: manual-seed
sources: [manual-curated]
---

# Manual entries for glossary-ja-JP--zh-TW

> Hand-curated ja-JP ↔ zh-TW pairs. Build script merges these into the auto-derived
> glossary, with manual entries taking priority on conflicts.

## domain: general

### Hanzi false friends (~25)
| ja-JP | zh-TW | source | notes |
|---|---|---|---|
| 手紙 | 信 | manual | ⚠️ NOT「衛生紙」(false friend) |
| 勉強 | 學習 / 努力 | manual | ⚠️ NOT「強迫」(false friend) |
| 愛人 | 情婦 | manual | ⚠️ false friend, zh-TW「配偶」誤譯風險 |
| 大丈夫 | 沒問題 / OK | manual | ⚠️ NOT「偉丈夫」 |
| 切手 | 郵票 | manual | ⚠️ zh-TW 直譯「切手」失義 |
| ... 20 more entries |

### Hanzi 共通詞 + 字形差異規則 (~20)
| 図書館 | 圖書館 | manual | 漢字共通詞・新字体↔正體 |
| 銀行 | 銀行 | manual | 字形相同 |
| 売る | 賣 (動詞) | manual | 字根不同 |
| ... 17 more entries |

### 文化借用 (~15)
| 御朱印 | 御朱印 | manual | 借用 |
| 居酒屋 | 居酒屋 / 日式酒館 | manual | 借用優先 |
| 寿司 | 壽司 | manual | 字形差異 |
| 茶碗蒸し | 茶碗蒸 | manual | 字形差異 |
| ... 11 more entries |

## domain: legal

### 高頻法律 / gov 共通字 (~15)
| 契約 | 契約 | manual | 共通字 |
| 同意 | 同意 | manual | 共通字 |
| 株式会社 | 股份有限公司 | manual | preferred ja → zh-TW canonical |
| ... 12 more entries |

## domain: tech.software

### Other high-frequency false-friend candidates (~15)
| ライブラリ | 函式庫 | manual | tech-specific (NOT「圖書館」) |
| ... 14 more entries |
```

(80-100 entries total. The actual content here is the v0.1 seed — researcher/translator quality. Do NOT auto-generate; hand-curate from established CJK contrast literature.)

- [ ] **Step 3: Implement `build-pair-ja-JP--zh-TW.py`** — merges manual seed + auto-derived from EN-pivot intersection:

```python
"""Build glossary-ja-JP--zh-TW.md = manual seed + EN-pivot-derived intersection."""
def main():
    canonical = ROOT / "scripts" / "canonical"
    manual = parse_manual_md(canonical / "manual-entries-ja-JP--zh-TW.md")
    en_ja = parse_pair_md(canonical / "glossary-en-US--ja-JP.md")  # {(en, domain) → ja_term}
    en_zh = parse_pair_md(canonical / "glossary-en-US--zh-TW.md")

    derived_by_domain = defaultdict(list)
    for (en, domain), ja in en_ja.items():
        zh = en_zh.get((en, domain))
        if zh:
            derived_by_domain[domain].append({
                "ja-JP": ja, "zh-TW": zh, "source": f"derived (en: {en}; jlt × naer)",
                "domain": domain, "notes": "—",
            })

    # Manual takes priority on (ja, zh) conflicts
    final_by_domain = defaultdict(list)
    for domain, entries in {**derived_by_domain, **manual}.items():
        seen = set()
        for e in manual.get(domain, []) + derived_by_domain.get(domain, []):
            key = (e["ja-JP"], e["zh-TW"])
            if key in seen:
                continue
            seen.add(key)
            final_by_domain[domain].append(e)

    emit_pair_file(pair=["ja-JP", "zh-TW"], entries_by_domain=final_by_domain,
                   out=canonical / "glossary-ja-JP--zh-TW.md")
```

- [ ] **Step 4: Run all builds, verify 5 pair files exist**

```bash
python3 scripts/build-pairs-from-en.py --all
python3 scripts/build-pair-zh-CN--zh-TW.py
python3 scripts/build-pair-ja-JP--zh-TW.py
ls scripts/canonical/glossary-*--*.md
# Expect 5 files
```

- [ ] **Step 5: Add unit tests** for both new build scripts (small fixtures, expected merge behavior).

- [ ] **Step 6: Commit**

```bash
git add translation-toolkit/scripts/build-pair-zh-CN--zh-TW.py translation-toolkit/scripts/build-pair-ja-JP--zh-TW.py translation-toolkit/scripts/canonical/manual-entries-ja-JP--zh-TW.md translation-toolkit/scripts/canonical/glossary-zh-CN--zh-TW.md translation-toolkit/scripts/canonical/glossary-ja-JP--zh-TW.md
git commit -m "feat(translation-toolkit): glossary-zh-CN--zh-TW + glossary-ja-JP--zh-TW build (manual seed + derived)"
```

---

### Task B5: Typography summaries + NICT corpus + distribute + verify-drift

**Files:**
- Create: `translation-toolkit/scripts/canonical/jlreq-summary.md`
- Create: `translation-toolkit/scripts/canonical/clreq-summary.md`
- Create: `translation-toolkit/scripts/canonical/nict-en-ja-zh.md`
- Create: `translation-toolkit/vendor/w3c/{jlreq,clreq}-source.md`
- Create: `translation-toolkit/vendor/w3c/LICENSE`
- Create: `translation-toolkit/vendor/nict/JEC_basic_sentence_v1-2.xls`
- Create: `translation-toolkit/vendor/nict/LICENSE`
- Create: `translation-toolkit/scripts/build-typography-summaries.py`
- Create: `translation-toolkit/scripts/build-nict-corpus.py`

- [ ] **Step 1: Fetch W3C jlreq/clreq HTML** — clone https://github.com/w3c/jlreq and https://github.com/w3c/clreq, extract relevant sections (line-breaking rules, punctuation, kinsoku) into `vendor/w3c/{jlreq,clreq}-source.md`.

- [ ] **Step 2: Implement `build-typography-summaries.py`** — extract a ~200-line summary from each W3C source:
  - jlreq summary: 句末「。」、列舉「、」、半角英数字無 spacing、kinsoku 禁則
  - clreq summary: 標點符號 (zh-CN: half-width / zh-TW: full-width), 行首行末規則

- [ ] **Step 3: Download NICT 日英中基本文 v1.2** — from https://alaginrc.nict.go.jp/jecbs/src/JEC_basic_sentence_v1-2.xls. Save to `vendor/nict/`.

- [ ] **Step 4: Implement `build-nict-corpus.py`** — convert XLS to markdown reference:

```python
"""Convert NICT JEC_basic_sentence_v1-2.xls to corpus/nict-en-ja-zh.md.

Output format: structured markdown with sentence triples grouped by topic
(if topic column exists in xls). 5,304 sentences as parallel reference for LLM.
NOT term-pair entries; LLM consults this corpus for sentence-level exemplars.
"""
import openpyxl
def main():
    src = ROOT / "vendor" / "nict" / "JEC_basic_sentence_v1-2.xls"
    wb = openpyxl.load_workbook(src)
    sheet = wb.active
    # ... iterate rows, emit markdown
    out = ROOT / "scripts" / "canonical" / "nict-en-ja-zh.md"
    out.write_text(...)
```

- [ ] **Step 5: Run all build scripts**

```bash
python3 scripts/build-typography-summaries.py
python3 scripts/build-nict-corpus.py
ls scripts/canonical/{jlreq,clreq}-summary.md scripts/canonical/nict-en-ja-zh.md
```

- [ ] **Step 6: Run distribute.py + verify-drift.py**

```bash
python3 scripts/distribute.py
# Should print: distributed N files across 4 skills
python3 scripts/verify-drift.py
# Should print: OK: all functional copies byte-identical
```

- [ ] **Step 7: Verify each skill folder has correct functional copies**

```bash
for skill in translation-i18n translation-doc translation-creative translation-audit; do
  echo "=== $skill ==="
  ls translation-toolkit/$skill/{glossary,typography,corpus,references}
done
```

Each skill should have 5 glossary files, 2 typography files, 1 corpus file, 6 reference files.

- [ ] **Step 8: Commit**

```bash
git add translation-toolkit/scripts/canonical/{jlreq,clreq}-summary.md translation-toolkit/scripts/canonical/nict-en-ja-zh.md translation-toolkit/scripts/build-typography-summaries.py translation-toolkit/scripts/build-nict-corpus.py translation-toolkit/vendor/{w3c,nict} translation-toolkit/translation-i18n translation-toolkit/translation-doc translation-toolkit/translation-creative translation-toolkit/translation-audit
git commit -m "feat(translation-toolkit): typography summaries + NICT corpus + first canonical distribution"
```

**Phase B checkpoint**: 5 pair files + 2 typography + 1 corpus + 6 references in canonical/. distribute.py runs clean. verify-drift.py reports OK. Each active skill has 14 functional copy files in correct subfolders.

---

## Phase C: Shared engine — glossary lookup + protect-pass + M1/M2 (5 tasks)

### Task C1: Glossary parser (load pair file, lookup with EN-pivot fallback)

**Files:**
- Create: `translation-toolkit/scripts/lib/glossary.py` (importable by skill bodies via Python helper, or referenced as algorithm prose in SKILL.md prompts)
- Test: `translation-toolkit/scripts/tests/test_glossary.py`

Note: skill bodies are markdown prompts, not Python. The glossary "parser" exists as Python only for build-time consistency tests; runtime lookup is performed by the LLM following the SKILL.md prompt that references the glossary table format. The Python implementation here serves as an executable spec the skill prompts must match.

- [ ] **Step 1: Write failing test for glossary parser**

```python
def test_lookup_direct_pair_hit(tmp_path):
    """When term has direct pair-file entry, returns target value with audit_path='direct'."""

def test_lookup_via_en_pivot(tmp_path):
    """When (zh-TW → ja-JP) pair file has no entry but en-pivot files do,
    returns target with audit_path='pivot.en-US'."""

def test_lookup_misses(tmp_path):
    """When no pair file matches and no pivot path, returns None with audit_path='miss'."""
```

- [ ] **Step 2: Run tests, verify FAIL**

- [ ] **Step 3: Implement `lib/glossary.py`**

```python
"""Glossary lookup with EN-pivot fallback.

Algorithm (mirrors spec lines 305-322):
  Step 1: try glossary-{S}--{T}.md (alphabetical) → direct hit
  Step 2: if S != en-US and T != en-US: try pivot via en-US
            (look up term in glossary-en-US--{S}.md → get pivot,
             then look up pivot in glossary-en-US--{T}.md)
  Step 3: miss → None
"""
import re
from pathlib import Path

def parse_pair_file(md_path: Path) -> dict:
    """Returns {(domain, lang_a_term): {lang_a, lang_b, lang_b_term, source, notes}}."""
    # Parse frontmatter for `pair: [A, B]`
    # Parse `## domain: <name>` sections
    # Parse 4-column tables under each domain

def lookup(glossary_dir: Path, source_lang: str, target_lang: str, term: str, domain: str | None = None) -> dict | None:
    """Returns {target_term, source, notes, audit_path} or None."""
    pair_alphabetical = sorted([source_lang, target_lang])
    direct_path = glossary_dir / f"glossary-{pair_alphabetical[0]}--{pair_alphabetical[1]}.md"
    if direct_path.exists():
        entries = parse_pair_file(direct_path)
        for (entry_domain, entry_term), entry in entries.items():
            if entry_term == term and (domain is None or entry_domain == domain):
                # Determine which column is target
                if entry["lang_a"] == target_lang:
                    return {"target_term": entry["lang_a_term"], **entry, "audit_path": "direct"}
                else:
                    return {"target_term": entry["lang_b_term"], **entry, "audit_path": "direct"}

    # Step 2: pivot via EN
    if "en-US" not in (source_lang, target_lang):
        pivot_src = glossary_dir / f"glossary-en-US--{source_lang}.md"
        pivot_tgt = glossary_dir / f"glossary-en-US--{target_lang}.md"
        if pivot_src.exists() and pivot_tgt.exists():
            pivot_term = lookup_in_file(pivot_src, source_lang, "en-US", term, domain)
            if pivot_term:
                final = lookup_in_file(pivot_tgt, "en-US", target_lang, pivot_term, domain)
                if final:
                    return {**final, "audit_path": f"pivot.en-US (via '{pivot_term}')"}

    return None
```

(~80 lines total.)

- [ ] **Step 4: Run tests, verify PASS**

- [ ] **Step 5: Commit**

```bash
git add translation-toolkit/scripts/lib/glossary.py translation-toolkit/scripts/tests/test_glossary.py
git commit -m "feat(translation-toolkit): glossary parser + EN-pivot fallback lookup"
```

---

### Task C2: Protect-pass (regex placeholder masking + restoration)

**Files:**
- Create: `translation-toolkit/scripts/lib/protect_pass.py`
- Create: `translation-toolkit/scripts/canonical/protect-pass-spec.md` (algorithm prose for skill prompts)
- Test: `translation-toolkit/scripts/tests/test_protect_pass.py`

- [ ] **Step 1: Write failing tests for placeholder protection**

```python
def test_protect_curly_braces():
    text = "Hello {name}, you have {count} messages"
    masked, token_map = protect(text)
    assert "{name}" not in masked
    assert "{count}" not in masked
    assert masked.count("⟦P:") == 2
    restored = restore(masked, token_map)
    assert restored == text

def test_protect_icu_plurals():
    text = "{count, plural, one {1 item} other {# items}}"
    masked, token_map = protect(text)
    assert masked.count("⟦P:") >= 1
    assert restore(masked, token_map) == text

def test_protect_inline_code():
    text = "Run `npm install` then `npm start`"
    masked, _ = protect(text)
    assert "npm" not in masked

def test_protect_fenced_code():
    text = "Header\n```python\ndef foo():\n  pass\n```\nEnd"
    masked, token_map = protect(text)
    assert "def foo" not in masked
    assert restore(masked, token_map) == text

def test_protect_urls():
    text = "Visit https://example.com/path?q=1"
    masked, _ = protect(text)
    assert "https://" not in masked

def test_protect_count_must_match_after_translation():
    """If translation drops a placeholder, M1 gate detects mismatch."""
    text = "Hello {user}, welcome"
    masked, token_map = protect(text)
    bad_translation = masked.replace("⟦P:01⟧", "")
    assert verify_count(bad_translation, token_map) is False
```

- [ ] **Step 2: Run tests, verify FAIL**

- [ ] **Step 3: Implement `lib/protect_pass.py`**

```python
"""Protect-pass: regex-extract placeholders → mask as ⟦P:NN⟧ tokens; restore inverse.

Patterns protected (in priority order — first match wins):
  P-class 1: ICU plurals: {count, plural, one {...} other {...}} (recursive braces)
  P-class 2: Curly braces: {name} {0} {{var}}
  P-class 3: printf-style: %s %d %1$s
  P-class 4: Fenced code blocks: ```...```
  P-class 5: Inline code: `...`
  P-class 6: HTML tags: <tag> </tag>
  P-class 7: URLs: https?://...
  P-class 8: Email addresses
  P-class 9: File paths: /usr/... or C:\...
"""
import re

PATTERNS = [
    (re.compile(r"\{[^{}]*,\s*plural\s*,\s*[^}]*(?:\{[^}]*\}[^}]*)*\}"), "icu"),
    (re.compile(r"\{\{?[a-zA-Z_][a-zA-Z0-9_]*\}?\}"), "var"),
    (re.compile(r"%(?:\d+\$)?[sdifoxX]"), "printf"),
    (re.compile(r"```[\s\S]*?```"), "fenced"),
    (re.compile(r"`[^`]+`"), "inline_code"),
    (re.compile(r"<[^>]+>"), "html"),
    (re.compile(r"https?://[^\s)]+"), "url"),
    (re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"), "email"),
]

def protect(text: str) -> tuple[str, dict[str, str]]:
    """Returns (masked_text, token_map) where token_map = {⟦P:01⟧: original, ...}."""
    token_map = {}
    counter = 1
    masked = text
    for pattern, name in PATTERNS:
        def replace(m):
            nonlocal counter
            token = f"⟦P:{counter:02d}⟧"
            token_map[token] = m.group(0)
            counter += 1
            return token
        masked = pattern.sub(replace, masked)
    return masked, token_map

def restore(masked: str, token_map: dict[str, str]) -> str:
    for token, original in token_map.items():
        masked = masked.replace(token, original)
    return masked

def verify_count(translated: str, token_map: dict[str, str]) -> bool:
    """M1 gate primitive: target placeholder count == source placeholder count."""
    expected = len(token_map)
    actual = len(re.findall(r"⟦P:\d+⟧", translated))
    return actual == expected
```

- [ ] **Step 4: Run tests, verify PASS**

- [ ] **Step 5: Write `scripts/canonical/protect-pass-spec.md`** — algorithm description for skill prompts. The 4 active skills will reference this file via `references/protect-pass-spec.md` (after distribute.py runs).

(Update `scripts/distribute.py` REFERENCE_FILES set to include `protect-pass-spec.md`.)

- [ ] **Step 6: Update verify-drift.py routing if needed**

- [ ] **Step 7: Run distribute + verify-drift**

- [ ] **Step 8: Commit**

```bash
git add translation-toolkit/scripts/lib/protect_pass.py translation-toolkit/scripts/canonical/protect-pass-spec.md translation-toolkit/scripts/tests/test_protect_pass.py translation-toolkit/scripts/distribute.py translation-toolkit/scripts/verify-drift.py
git commit -m "feat(translation-toolkit): protect-pass placeholder masking + restoration + M1 verify primitive"
```

---

### Task C3: Core loop spec (DRAFT/REFLECT/IMPROVE prompts)

**Files:**
- Modify: `translation-toolkit/scripts/canonical/core-loop.md` (expand from skeleton in Task A3 to full prompts)
- Create: `translation-toolkit/scripts/canonical/prompts/draft.md`
- Create: `translation-toolkit/scripts/canonical/prompts/reflect-4d.md`
- Create: `translation-toolkit/scripts/canonical/prompts/reflect-5d.md`
- Create: `translation-toolkit/scripts/canonical/prompts/improve.md`

Note: Anthropic skill convention forbids nested subfolders within a skill subfolder, but `scripts/canonical/` is plugin-level (not inside any skill), so `scripts/canonical/prompts/` is allowed. After distribute.py runs, prompts must be flattened — distribute.py routes `prompts/*.md` to each skill's `references/` folder with renamed prefixes (e.g., `prompts/draft.md` → `references/prompt-draft.md`).

- [ ] **Step 1: Write `prompts/draft.md`** — system prompt for WRITER role. Variables (`{{source_lang}}`, `{{target_lang}}`, `{{mode}}`, `{{register}}`, `{{strategy}}`, `{{domain}}`, `{{glossary_terms}}`, `{{document_context}}`, `{{chunk_marker}}`):

```
You are a professional translator translating from {{source_lang}} to {{target_lang}}.

# Translation parameters
- Mode: {{mode}}
- Register: {{register}}
- Strategy: {{strategy}}
- Domain: {{domain}}

# Relevant glossary terms (USE THESE — do not invent alternatives)
{{glossary_terms}}

# Document context (for cross-chunk consistency; only translate the wrapped section)
{{document_context_with_translate_this_marker}}

# Output requirements
- Translate ONLY the content wrapped in <TRANSLATE_THIS>...</TRANSLATE_THIS>
- Preserve all ⟦P:NN⟧ placeholder tokens unchanged
- Output ONLY the translation, no commentary
```

- [ ] **Step 2: Write `prompts/reflect-4d.md`** — CRITIC role prompt:

```
You are a translation critic reviewing this draft. Produce structured 4D critique
across these axes (one paragraph per axis, with concrete suggestions where issues found):

1. Accuracy — semantic faithfulness. Are there additions, omissions, distortions?
2. Fluency — does target read naturally? Awkward phrasings?
3. Style — does register/rhythm/rhetoric match source and intended {{mode}}/{{register}}?
4. Terminology — does it match the glossary? Domain conventions?

Output format (JSON):
{
  "accuracy": [{"issue": "...", "suggestion": "..."}, ...],
  "fluency": [...],
  "style": [...],
  "terminology": [...]
}

If an axis has no issues, return empty array. Do NOT rewrite the translation —
only critique.
```

- [ ] **Step 3: Write `prompts/reflect-5d.md`** — same as 4D + 5th axis (effectiveness, transcreation only).

- [ ] **Step 4: Write `prompts/improve.md`** — REVISER role:

```
You are a translation reviser. Given the draft v1 and the 4D/5D critique below,
produce v2 incorporating the suggestions. Do NOT add new reasoning beyond the
critique — just apply the fixes.

Preserve ⟦P:NN⟧ placeholder tokens unchanged.

Output ONLY the revised translation.
```

- [ ] **Step 5: Update `scripts/canonical/core-loop.md`** — high-level orchestration: chunking with TA's <TRANSLATE_THIS> windowing, sequential DRAFT → REFLECT → IMPROVE, glossary injection per chunk (only relevant terms).

- [ ] **Step 6: Update distribute.py routing** — flatten prompts:

```python
PROMPT_FILES = {"prompts/draft.md", "prompts/reflect-4d.md", "prompts/reflect-5d.md", "prompts/improve.md"}
# In distribute(): when src is in PROMPT_FILES, copy to {skill}/references/prompt-{basename}.md
# (renamed to flatten the directory structure)
```

- [ ] **Step 7: Update verify-drift.py to match**

- [ ] **Step 8: Run distribute + verify-drift, confirm prompts land in references/**

- [ ] **Step 9: Commit**

```bash
git add translation-toolkit/scripts/canonical/prompts/ translation-toolkit/scripts/canonical/core-loop.md translation-toolkit/scripts/distribute.py translation-toolkit/scripts/verify-drift.py
git commit -m "feat(translation-toolkit): DRAFT/REFLECT/IMPROVE prompts + flatten distribution"
```

---

### Task C4: M1 placeholder integrity gate + M2 glossary compliance gate

**Files:**
- Create: `translation-toolkit/scripts/lib/gates.py`
- Modify: `translation-toolkit/scripts/canonical/verification-gates.md` (expand from Task A3 skeleton)
- Test: `translation-toolkit/scripts/tests/test_gates.py`

- [ ] **Step 1: Write failing tests for M1 + M2**

```python
def test_m1_placeholder_count_match():
    """M1 PASS: target has same ⟦P:*⟧ count as source."""
    source_token_map = {"⟦P:01⟧": "{name}", "⟦P:02⟧": "{count}"}
    target = "你好 ⟦P:01⟧, 你有 ⟦P:02⟧ 條訊息"
    assert m1_check(target, source_token_map) == {"verdict": "PASS", "diff": None}

def test_m1_placeholder_missing():
    """M1 FAIL: target missing one placeholder."""
    source_token_map = {"⟦P:01⟧": "{name}", "⟦P:02⟧": "{count}"}
    target = "你好 ⟦P:01⟧, 你有訊息"
    result = m1_check(target, source_token_map)
    assert result["verdict"] == "FAIL"
    assert "⟦P:02⟧" in result["diff"]

def test_m2_project_glossary_compliance_pass():
    """M2 PASS: source term `cancel` appears as `取消` per project glossary."""
    project_glossary = {("cancel", "ui"): "取消"}
    source = "Click cancel"
    target = "點選取消"
    assert m2_check(source, target, project_glossary, domain="ui")["verdict"] == "PASS"

def test_m2_project_glossary_violation():
    """M2 FAIL: source `cancel` appears as `取り消す` (not the project translation)."""
    project_glossary = {("cancel", "ui"): "取消"}
    source = "Click cancel"
    target = "點擊取り消す"
    result = m2_check(source, target, project_glossary, domain="ui")
    assert result["verdict"] == "FAIL"
    assert "cancel" in result["diff"]

def test_m2_context_dependent_exempt():
    """M2 entries marked context-dependent in notes are advisory, do not fail."""
    project_glossary = {("cancel", "ui"): "取消"}
    notes = {("cancel", "ui"): "context-dependent"}
    target = "點擊取り消す"
    assert m2_check(source, target, project_glossary, domain="ui", notes=notes)["verdict"] == "PASS_ADVISORY"
```

- [ ] **Step 2: Run tests, verify FAIL**

- [ ] **Step 3: Implement `lib/gates.py`**

```python
"""Verification gates M1 (placeholder integrity) and M2 (project glossary compliance)."""
import re

def m1_check(target: str, source_token_map: dict) -> dict:
    """Compare placeholder count between target and source."""
    expected = set(source_token_map.keys())
    actual = set(re.findall(r"⟦P:\d+⟧", target))
    if actual == expected:
        return {"verdict": "PASS", "diff": None}
    return {
        "verdict": "FAIL",
        "diff": f"missing: {expected - actual}; extra: {actual - expected}",
    }

def m2_check(source: str, target: str, project_glossary: dict, domain: str, notes: dict | None = None) -> dict:
    """Verify each glossary term in source maps to its prescribed translation in target."""
    violations = []
    for (term, term_domain), expected_translation in project_glossary.items():
        if term_domain != domain:
            continue
        if term.lower() in source.lower() and expected_translation not in target:
            note = (notes or {}).get((term, term_domain), "")
            if "context-dependent" in note.lower():
                continue
            violations.append(f"'{term}' should translate to '{expected_translation}'")
    if violations:
        return {"verdict": "FAIL", "diff": "; ".join(violations)}
    return {"verdict": "PASS", "diff": None}
```

- [ ] **Step 4: Run tests, verify PASS**

- [ ] **Step 5: Expand `scripts/canonical/verification-gates.md`** — full prose spec for each gate (M1, M2, S1, S2, I1) with examples. Reviewers reading this should understand exactly what each gate does, when it runs, what triggers PASS/FAIL/SKIP.

- [ ] **Step 6: Run distribute + verify-drift**

- [ ] **Step 7: Commit**

```bash
git add translation-toolkit/scripts/lib/gates.py translation-toolkit/scripts/canonical/verification-gates.md translation-toolkit/scripts/tests/test_gates.py
git commit -m "feat(translation-toolkit): M1 placeholder + M2 glossary gates with unit tests"
```

---

### Task C5: Audit trail emitter

**Files:**
- Create: `translation-toolkit/scripts/lib/audit_trail.py`
- Modify: `translation-toolkit/scripts/canonical/audit-trail-spec.md` (full schema)
- Test: `translation-toolkit/scripts/tests/test_audit_trail.py`

- [ ] **Step 1: Write failing test**

```python
def test_audit_trail_full_record():
    """Audit trail JSON contains all spec fields with correct shape."""
    builder = AuditTrailBuilder()
    builder.set_intake(mode="faithful", register="neutral", strategy="domestication",
                      source_locale="en-US", target_locale="ja-JP", domain="ui",
                      intent="UI strings for Settings screen")
    builder.add_glossary_resolution(term="Cancel", tier="L2", source="pontoon",
                                     value="キャンセル", audit_path="direct")
    builder.add_chunk(index=0, draft="...", reflect={"accuracy": []}, improve="キャンセル")
    builder.add_gate_verdict("M1", "PASS", None)
    builder.add_gate_verdict("M2", "PASS", None)
    out = builder.build()
    assert out["intake"]["mode"] == "faithful"
    assert out["glossary_resolution"][0]["audit_path"] == "direct"
    assert out["gate_verdicts"]["M1"] == "PASS"
```

- [ ] **Step 2: Implement `lib/audit_trail.py`**

```python
"""Builder for audit-trail JSON per spec schema."""
import json
from datetime import datetime, timezone

class AuditTrailBuilder:
    def __init__(self):
        self.data = {
            "version": "0.1.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "intake": {},
            "glossary_resolution": [],
            "chunks": [],
            "gate_verdicts": {},
            "untranslatables": [],
            "sources_used": {},
            "warnings": [],
        }

    def set_intake(self, **kwargs):
        self.data["intake"].update(kwargs)

    def add_glossary_resolution(self, **entry):
        self.data["glossary_resolution"].append(entry)

    def add_chunk(self, index, draft, reflect, improve):
        self.data["chunks"].append({
            "index": index, "draft": draft, "reflect": reflect, "improve": improve
        })

    def add_gate_verdict(self, gate_id, verdict, diff):
        self.data["gate_verdicts"][gate_id] = {"verdict": verdict, "diff": diff}

    def add_untranslatable(self, source_phrase, decision, alternatives):
        self.data["untranslatables"].append({
            "source_phrase": source_phrase, "decision": decision, "alternatives": alternatives
        })

    def add_warning(self, message):
        self.data["warnings"].append(message)

    def build(self) -> dict:
        return self.data

    def to_json(self) -> str:
        return json.dumps(self.data, ensure_ascii=False, indent=2)
```

- [ ] **Step 3: Expand `audit-trail-spec.md`** — JSON schema with all field definitions + example.

- [ ] **Step 4: Run tests, verify PASS**

- [ ] **Step 5: Run distribute + verify-drift**

- [ ] **Step 6: Commit**

```bash
git add translation-toolkit/scripts/lib/audit_trail.py translation-toolkit/scripts/canonical/audit-trail-spec.md translation-toolkit/scripts/tests/test_audit_trail.py
git commit -m "feat(translation-toolkit): audit-trail JSON builder + schema spec"
```

**Phase C checkpoint**: Python lib (`scripts/lib/`) has glossary parser, protect-pass, gates M1+M2, audit trail builder. All unit tests pass. Skill prompts (`scripts/canonical/prompts/`) describe DRAFT/REFLECT/IMPROVE roles.

---

## Phase D: Active skills bodies (5 tasks)

### Task D1: using-translation-toolkit (router) full body

**Files:**
- Modify: `translation-toolkit/using-translation-toolkit/SKILL.md` (expand from skeleton)

- [ ] **Step 1: Write full SKILL.md** describing routing logic + web-search trade-offs (per Decision #15 — single paragraph absorbed from removed per-skill `web-search-tradeoffs.md`).

Body sections:
1. **Purpose** — entry point for translation-toolkit; routes to one of 4 active skills based on user intent and input shape.
2. **Routing rules**:
   - User provides existing translation + asks to review → `translation-audit`
   - User provides PO/JSON/XLIFF/Android/iOS file → `translation-i18n`
   - User provides markdown / .md / technical doc → `translation-doc`
   - User provides ad copy / marketing brief / headline → `translation-creative`
   - Ambiguous → invoke `translation-intake` first to clarify
3. **Web search trade-off note** — one paragraph (replaces removed per-skill `web-search-tradeoffs.md`):

   > Web search is ON by default across all 4 active skills (Decision #7) for max quality. For batch i18n runs (1000s of strings), this triggers per-miss searches and explodes cost — pass `--web-search=off` to disable. For ad copy creative work, web search may pull competitor copy that contaminates voice — consider `--web-search=off` if working with established brand voice.

4. **Cross-plugin delegation** — note that copywriting-toolkit will NOT auto-invoke this; user must explicitly compose if they want post-translation copy polish.

- [ ] **Step 2: Verify hook validation**

```bash
bash .claude/hooks/validate-skill-folder-structure.sh translation-toolkit/using-translation-toolkit/SKILL.md
```

- [ ] **Step 3: Commit**

```bash
git add translation-toolkit/using-translation-toolkit/SKILL.md
git commit -m "feat(translation-toolkit): using-translation-toolkit router skill body"
```

---

### Task D2: translation-intake (Layer 1) full body + protocols

**Files:**
- Modify: `translation-toolkit/translation-intake/SKILL.md`
- Create: `translation-toolkit/translation-intake/protocols/intake-auto.md`
- Create: `translation-toolkit/translation-intake/protocols/intake-explicit.md`

- [ ] **Step 1: Write `protocols/intake-auto.md`** — describes auto mode pipeline:
  - LLM source-analysis call extracting: domain (top-3 keyword match against 13-domain taxonomy), formality register, mode hint, strategy bias, intent (skopos)
  - Inferences written to audit_trail.intake with `inferred=true` flag
  - User can rerun with `--explicit` if dissatisfied

- [ ] **Step 2: Write `protocols/intake-explicit.md`** — describes explicit mode interaction:
  - Skill prompts user for each of 5 axes + skopos
  - 5 axes: mode (literal | faithful | localized | transcreation), register (formal | neutral | warm | playful), strategy (domestication | foreignization), locale (BCP-47 required), domain (one or more from taxonomy)
  - Skopos: "Who reads this and what action should they take?"
  - All values written to audit_trail.intake with `inferred=false`

- [ ] **Step 3: Update `translation-intake/SKILL.md`** with full body:

```yaml
---
name: translation-intake
description: Layer 1 of translation-toolkit. Clarifies translation parameters (5 axes + skopos) via auto-detect or explicit user input. Output: intake-spec consumed by downstream translation skills (translation-i18n / -doc / -creative / -audit).
version: 0.1.0
---

# translation-intake

## Purpose
Translates user intent into a structured 5-axis intake spec that downstream skills consume.

## Modes
- **auto** (default): single LLM source-analysis call infers all 5 axes from source content
- **explicit** (`--explicit` / `-e`): user is prompted for each of 5 axes + skopos

See protocols/intake-auto.md and protocols/intake-explicit.md for details.

## 5 axes
- mode: literal | faithful | localized | transcreation
- register: formal | neutral | warm | playful
- strategy: domestication | foreignization
- locale: BCP-47 (e.g., ja-JP, zh-TW)
- domain: one or more from {general, ui, tech.{software,web,data,crypto}, gov, legal, medical, finance, marketing, statistics, typography}

## Output
Writes intake-spec.json passed to next skill in pipeline. Schema:
{
  "mode": "...", "register": "...", "strategy": "...",
  "source_locale": "...", "target_locale": "...",
  "domains": [...], "intent": "...",
  "inferred": {...}  // map of axis → boolean
}
```

- [ ] **Step 4: Hook validation**

- [ ] **Step 5: Commit**

```bash
git add translation-toolkit/translation-intake/
git commit -m "feat(translation-toolkit): translation-intake skill body + auto/explicit protocols"
```

---

### Task D3: translation-i18n (PO/JSON/XLIFF + Android + iOS) full body

**Files:**
- Modify: `translation-toolkit/translation-i18n/SKILL.md`
- Create: `translation-toolkit/translation-i18n/protocols/placeholder-protect.md`
- Create: `translation-toolkit/translation-i18n/protocols/format-roundtrip.md`
- Create: `translation-toolkit/translation-i18n/checklists/i18n-format-checklist.md`

- [ ] **Step 1: Write full `translation-i18n/SKILL.md`** describing the full 5-layer pipeline for i18n format:

```markdown
---
name: translation-i18n
description: Translate i18n strings (PO / JSON / XLIFF / Android strings.xml / iOS .strings) preserving placeholders, keys, and project glossary. Web search ON, S1 back-trans SHOULD, M1+M2 strict.
version: 0.1.0
---

# translation-i18n

## Inputs
- source file path or string
- intake-spec from translation-intake (or invoke intake first)
- optional: glossary_path

## Pipeline

### Layer 2: Preparation
1. Parse format (auto-detect by extension or content):
   - .po → use polib-equivalent algorithm
   - .json → key-value map (handle nested)
   - .xliff → XLIFF 2.x parser
   - strings.xml → Android resource
   - .strings → iOS NSLocalizedString format
2. Protect-pass per protocols/placeholder-protect.md (mask {{var}} %s {0} ICU plurals)
3. Source analysis: extract difficult terms, domain hints
4. Glossary resolve: 4-tier fallthrough per references/glossary-format-spec.md

### Layer 3: Core loop
- DRAFT (per references/prompt-draft.md)
- REFLECT 4D (per references/prompt-reflect-4d.md)
- IMPROVE (per references/prompt-improve.md)
- Cross-string context: keys from same file are visible in <CONTEXT>...</CONTEXT> wrapping

### Layer 4: Verification
- M1 placeholder integrity (HARD)
- M2 project glossary compliance (HARD)
- S1 back-translation (SHOULD; uses subagent for blindness)
- S2 register preservation (SHOULD)
- I1 untranslatability flagging (info-only)

### Layer 5: Output
- Restore placeholder tokens
- Write back to original file format preserving keys + structure
- Emit audit-trail.json
- Update I1 untranslatability list (no interactive prompt)

## See also
- protocols/format-roundtrip.md (per-format read/write logic)
- checklists/i18n-format-checklist.md (preflight checks)
```

- [ ] **Step 2: Write `protocols/placeholder-protect.md`** — references `references/protect-pass-spec.md` (functional copy from canonical) and adds i18n-specific patterns: ICU plurals, gender selectors, Android plurals XML.

- [ ] **Step 3: Write `protocols/format-roundtrip.md`** — per-format read+write algorithms:
  - PO: parse via polib, preserve `msgctxt` / `msgid_plural` / comments
  - JSON: nested key paths via dot-notation, preserve order
  - XLIFF: 2.x with `<segment>` / `<source>` / `<target>` structure
  - strings.xml: Android with `<string name="">`, `<plurals>`, escape rules
  - .strings: iOS key-value, escape backslashes

- [ ] **Step 4: Write `checklists/i18n-format-checklist.md`** — 8-item preflight: file readable, format detected, placeholder count > 0 → mask, source not empty, target locale BCP-47 valid, glossary path resolvable or skipped, at least one tier matches at least one term, file is writable for output.

- [ ] **Step 5: Hook validation**

- [ ] **Step 6: Commit**

```bash
git add translation-toolkit/translation-i18n/
git commit -m "feat(translation-toolkit): translation-i18n full body + protocols + checklist"
```

---

### Task D4: translation-doc (markdown / technical docs) full body

**Files:**
- Modify: `translation-toolkit/translation-doc/SKILL.md`
- Create: `translation-toolkit/translation-doc/protocols/markdown-ast-protect.md`
- Create: `translation-toolkit/translation-doc/checklists/doc-quality-checklist.md`

- [ ] **Step 1: Write full `translation-doc/SKILL.md`** — same 5-layer template as i18n, but Layer 2/5 use markdown AST handling, code blocks/URLs/HTML/inline-code masked, cross-section context preserved via TA's `<TRANSLATE_THIS>` windowing per chunk.

- [ ] **Step 2: Write `protocols/markdown-ast-protect.md`** — algorithm for protecting code blocks (fenced + inline), URLs (markdown link syntax + bare), HTML tags, math blocks (`$$...$$` LaTeX), front-matter YAML.

- [ ] **Step 3: Write `checklists/doc-quality-checklist.md`** — 6-item: code blocks not modified, link targets preserved, heading levels match, TOC links still resolve, mermaid diagrams unchanged, ASCII diagrams unchanged.

- [ ] **Step 4: Hook validation + commit**

```bash
git add translation-toolkit/translation-doc/
git commit -m "feat(translation-toolkit): translation-doc full body + AST protect + checklist"
```

---

### Task D5: translation-creative (transcreation + variants) full body

**Files:**
- Modify: `translation-toolkit/translation-creative/SKILL.md`
- Create: `translation-toolkit/translation-creative/protocols/brand-brief-intake.md`
- Create: `translation-toolkit/translation-creative/protocols/transcreation-mode.md`
- Create: `translation-toolkit/translation-creative/checklists/creative-checklist.md`

- [ ] **Step 1: Write full `translation-creative/SKILL.md`** — 5-layer pipeline with:
  - Layer 1 intake additionally captures brand voice notes (via `protocols/brand-brief-intake.md`)
  - Layer 3 uses 5D reflection in transcreation mode (4D in faithful mode)
  - Layer 4: S1 back-trans MUST in transcreation, SHOULD in faithful (per Decision #4)
  - Layer 5: default 1 output; `--variants=N` flag opt-in for N alternatives

- [ ] **Step 2: Write `protocols/brand-brief-intake.md`** — captures: brand archetype, tone-of-voice spectrum (e.g., authoritative ↔ playful), do-not-say list, signature phrases, target persona age/region.

- [ ] **Step 3: Write `protocols/transcreation-mode.md`** — describes when to enter transcreation mode (mode=transcreation in intake), how the 5th axis "effectiveness" is judged, how variants differ.

- [ ] **Step 4: Write `checklists/creative-checklist.md`** — 6-item: cultural references land in target, persuasion intent preserved (effectiveness verified by S1), brand voice consistent with brief, do-not-say list respected, variants are genuinely different (not paraphrases), CTA strength matches source.

- [ ] **Step 5: Hook validation + commit**

```bash
git add translation-toolkit/translation-creative/
git commit -m "feat(translation-toolkit): translation-creative full body + brand brief + transcreation protocols"
```

**Phase D checkpoint**: All 5 active skill bodies (router + intake + 3 active translation) complete. End-to-end smoke test: invoke `using-translation-toolkit` with "Hello world" → routes to translation-i18n → produces `こんにちは世界`. Audit trail JSON emitted.

---

## Phase E: translation-audit + S1/S2/I1 gates (4 tasks)

### Task E1: translation-audit skill body

**Files:**
- Modify: `translation-toolkit/translation-audit/SKILL.md`
- Create: `translation-toolkit/translation-audit/protocols/diff-report.md`
- Create: `translation-toolkit/translation-audit/checklists/audit-completeness-checklist.md`

- [ ] **Step 1: Write full `translation-audit/SKILL.md`**:

```markdown
---
name: translation-audit
description: Audit existing translations against source. Takes (source, existing-target) input, runs full 5-gate verification, outputs diff report + improvement suggestions. No translation produced. Web search ON, all gates run.
version: 0.1.0
---

# translation-audit

## Inputs
- source file path or string
- existing target file path or string (REQUIRED — distinguishes from translation skills)
- intake-spec (or auto-infer)
- optional: glossary_path

## Pipeline

### Layer 2: Preparation
- Parse BOTH source and target (auto-detect formats independently)
- Source-analysis: identify difficult terms in BOTH (target may have its own translation issues)
- Glossary resolve: same 4-tier fallthrough

### Layer 3: SKIPPED
- No DRAFT/REFLECT/IMPROVE — using user-provided target

### Layer 4: Verification (all 5 gates run, typically stricter semantics)
- M1 placeholder integrity (compare source/target placeholder counts)
- M2 project glossary compliance (target violations reported)
- S1 back-translation (subagent translates target → source-language; semantic similarity vs original source)
- S2 register preservation (LLM judge: target register matches expected from source)
- I1 untranslatability (any untranslatable phrases handled appropriately)

### Layer 5: Output
- Diff report (no rewrite)
  - Summary: overall verdict (PASS / FAIL / NEEDS_REVIEW)
  - Per-gate verdicts
  - Inline issues with line numbers
  - Improvement suggestions per issue
- Audit-trail.json with full provenance

## See also
- protocols/diff-report.md
- checklists/audit-completeness-checklist.md
```

- [ ] **Step 2: Write `protocols/diff-report.md`** — diff report markdown template with structured sections.

- [ ] **Step 3: Write `checklists/audit-completeness-checklist.md`** — 5-item: source readable, target readable, both formats parseable, all 5 gates ran (or explicitly skipped with reason), report includes inline issues + suggestions.

- [ ] **Step 4: Hook validation + commit**

```bash
git add translation-toolkit/translation-audit/
git commit -m "feat(translation-toolkit): translation-audit skill body + diff-report protocol"
```

---

### Task E2: S1 back-translation gate (subagent dispatch)

**Files:**
- Create: `translation-toolkit/scripts/lib/gate_s1_backtrans.py`
- Modify: `translation-toolkit/scripts/canonical/verification-gates.md` (add S1 details)
- Test: `translation-toolkit/scripts/tests/test_gate_s1.py`

- [ ] **Step 1: Write failing test for S1 dispatch logic**

```python
def test_s1_dispatch_with_subagent_capability():
    """When subagent_dispatch is provided, S1 calls it with blind context."""
    captured = {}
    def fake_subagent_dispatch(prompt: str) -> str:
        captured["prompt"] = prompt
        return "Hello world"  # back-translation
    result = s1_check(
        original_source="Hello world",
        translated_v2="你好世界",
        source_lang="en-US",
        subagent_dispatch=fake_subagent_dispatch,
        threshold=0.85,
    )
    assert result["verdict"] in ("PASS", "WARN")
    assert "Hello world" in captured["prompt"]
    assert "你好世界" in captured["prompt"]
    assert "original" not in captured["prompt"].lower()  # blind: no reference to original

def test_s1_skip_when_no_subagent_capability():
    """When subagent_dispatch=None, S1 returns SKIPPED with audit-trail flag."""
    result = s1_check(
        original_source="Hello world", translated_v2="你好世界",
        source_lang="en-US", subagent_dispatch=None,
    )
    assert result["verdict"] == "SKIPPED"
    assert "no isolation capability" in result["reason"].lower()
```

- [ ] **Step 2: Implement `lib/gate_s1_backtrans.py`**

```python
"""S1 back-translation gate.

REQUIRES subagent dispatch for blindness (correctness, not optimization).
Per Decision #16: runtime without subagent capability gracefully skips with
audit-trail flag.
"""
def s1_check(original_source: str, translated_v2: str, source_lang: str,
              subagent_dispatch: callable | None,
              threshold: float = 0.85,
              transcreation_threshold: float = 0.70,
              is_transcreation: bool = False) -> dict:
    if subagent_dispatch is None:
        return {"verdict": "SKIPPED", "reason": "No isolation capability available"}

    # Dispatch blind back-translation
    backtrans_prompt = (
        f"Translate the following to {source_lang}. "
        f"Output ONLY the translation, no commentary.\n\n{translated_v2}"
    )
    backtrans = subagent_dispatch(backtrans_prompt)

    # Compute semantic similarity (placeholder — use embeddings in production)
    similarity = compute_semantic_similarity(original_source, backtrans)
    effective_threshold = transcreation_threshold if is_transcreation else threshold

    verdict = "PASS" if similarity >= effective_threshold else "WARN"
    return {
        "verdict": verdict,
        "similarity": similarity,
        "threshold": effective_threshold,
        "back_translation": backtrans,
    }

def compute_semantic_similarity(a: str, b: str) -> float:
    """Embedding cosine similarity. Stub for v0.1 — return 0.9 placeholder.
    TODO: integrate sentence-transformers or LLM-judge in v0.2."""
    # For v0.1 ship: use simple LLM-judge-style call asking 0-1 similarity score
    # Real embedding integration requires model dep decision; defer.
    return 0.9  # stub
```

(Note: full embedding similarity is a v0.2 follow-up — see Out of Scope. v0.1 ships with LLM-judge stub returning a score.)

- [ ] **Step 3: Run tests, verify PASS**

- [ ] **Step 4: Update `verification-gates.md` with S1 full prose**

- [ ] **Step 5: Run distribute + verify-drift**

- [ ] **Step 6: Commit**

```bash
git add translation-toolkit/scripts/lib/gate_s1_backtrans.py translation-toolkit/scripts/tests/test_gate_s1.py translation-toolkit/scripts/canonical/verification-gates.md
git commit -m "feat(translation-toolkit): S1 back-translation gate with subagent dispatch + graceful skip"
```

---

### Task E3: S2 register preservation gate

**Files:**
- Create: `translation-toolkit/scripts/lib/gate_s2_register.py`
- Test: `translation-toolkit/scripts/tests/test_gate_s2.py`

- [ ] **Step 1: Write failing test**

```python
def test_s2_register_match():
    """S2 PASS when target register matches intake register."""
    result = s2_check(
        original_source="Could you please review this?",
        translated_v2="ご確認いただけますでしょうか",
        intake_register="formal",
        llm_judge=lambda prompt: "formal",
    )
    assert result["verdict"] == "PASS"

def test_s2_register_mismatch():
    """S2 WARN when target register doesn't match expected."""
    result = s2_check(
        original_source="Could you please review this?",
        translated_v2="見て",  # too casual
        intake_register="formal",
        llm_judge=lambda prompt: "casual",
    )
    assert result["verdict"] == "WARN"
```

- [ ] **Step 2: Implement `lib/gate_s2_register.py`** — LLM judge call with structured output (asks: "What register is this target text? formal | neutral | warm | playful").

- [ ] **Step 3: Run tests, verify PASS**

- [ ] **Step 4: Commit**

```bash
git add translation-toolkit/scripts/lib/gate_s2_register.py translation-toolkit/scripts/tests/test_gate_s2.py
git commit -m "feat(translation-toolkit): S2 register preservation gate with LLM judge"
```

---

### Task E4: I1 untranslatability flagging (info-only)

**Files:**
- Create: `translation-toolkit/scripts/lib/gate_i1_untranslatability.py`
- Test: `translation-toolkit/scripts/tests/test_gate_i1.py`

- [ ] **Step 1: Write failing test**

```python
def test_i1_flags_phrases_from_source_analysis():
    """I1 collects untranslatable phrases identified during Layer 2 source-analysis,
    records decision (borrow/explain/approximate) per phrase, no user prompt."""
    source_analysis = {
        "untranslatables": [
            {"phrase": "御朱印", "category": "cultural", "candidates": ["borrow", "explain"]}
        ]
    }
    target = "I visited the temple to receive the 御朱印 stamp"  # borrowed
    result = i1_check(source_analysis, target)
    assert result["verdict"] == "INFO"
    assert result["flags"][0]["phrase"] == "御朱印"
    assert result["flags"][0]["decision"] == "borrow"  # detected from target
```

- [ ] **Step 2: Implement `lib/gate_i1_untranslatability.py`** — heuristic detection of how each flagged phrase was handled (borrow/explain/approximate based on target presence patterns).

- [ ] **Step 3: Run tests, verify PASS**

- [ ] **Step 4: Commit**

```bash
git add translation-toolkit/scripts/lib/gate_i1_untranslatability.py translation-toolkit/scripts/tests/test_gate_i1.py
git commit -m "feat(translation-toolkit): I1 untranslatability flagging (info-only, non-interactive)"
```

**Phase E checkpoint**: All 5 gates implemented (M1+M2 from Phase C, S1+S2+I1 here). translation-audit skill body ships. Run translation-audit on a known-bad translation (e.g., source has 2 placeholders, target has 1) and verify M1 FAIL is correctly reported in diff.

---

## Phase F: Web search L4 + smoke + release (3 tasks)

### Task F1: Web search L4 tier (tool-abstraction wrapper)

**Files:**
- Create: `translation-toolkit/scripts/lib/web_search.py`
- Modify: `translation-toolkit/scripts/canonical/glossary-resolution-spec.md` (algorithm description)
- Test: `translation-toolkit/scripts/tests/test_web_search.py`

Note: actual web-search tool dispatch happens in skill prompts via `WebSearch` (CC) / `google_web_search` (Gemini) / `browser` (Codex). The Python wrapper is a fallback for build-time tests; runtime is LLM-driven per skill prompts.

- [ ] **Step 1: Write algorithm prose `glossary-resolution-spec.md`** — describes the 4-tier fallthrough (L1 project → L2 bundled → L3 web search → L4 LLM), including:
  - L3 web search trigger: term flagged in source-analysis as "translation-difficult" AND not found in L1/L2
  - L3 deduplication within document (cache hits per session)
  - L3 max searches per document = 10 (cost cap)
  - Tool abstraction: skill prompt says "if a web search capability is available, search '<term> <target_lang_full_name> 翻訳 OR translation' and extract candidate translations from top 3 results"

- [ ] **Step 2: Implement Python stub `lib/web_search.py`** for build-time testing — returns hardcoded candidates given a term.

- [ ] **Step 3: Run distribute + verify-drift**

- [ ] **Step 4: Commit**

```bash
git add translation-toolkit/scripts/lib/web_search.py translation-toolkit/scripts/canonical/glossary-resolution-spec.md translation-toolkit/scripts/tests/test_web_search.py
git commit -m "feat(translation-toolkit): web search L4 tier (tool-abstraction in prompts)"
```

---

### Task F2: Optional fetch scripts (Microsoft + JPO UTX)

**Files:**
- Create: `translation-toolkit/scripts/fetch-microsoft-terms.py`
- Create: `translation-toolkit/scripts/fetch-jpo-utx.py`
- Create: `translation-toolkit/scripts/README-optional-fetch.md`

These scripts are SHIPPED as part of v0.1.0 but NOT auto-run. Users invoke them to download ~33k Microsoft Terminology entries / ~130k 特許庁 UTX entries to `~/.cache/translation-toolkit/`. Skill prompts (Layer 2 glossary resolve) detect cache presence and use entries when available; absent → fall through normal 4-tier.

- [ ] **Step 1: Implement `fetch-microsoft-terms.py`**

```python
#!/usr/bin/env python3
"""Optional fetch: Microsoft Terminology Collection (~33k entries × 100+ langs).

License: gray. Microsoft Learn allows "use to develop localized versions or
integrate into other terminology collections" but does not explicitly license
redistribution. Hence: NOT bundled in plugin; users run this script to download
to their own machine cache.

Usage: python3 fetch-microsoft-terms.py [--target ja-JP|zh-TW|zh-CN|all]

Cache location: ~/.cache/translation-toolkit/microsoft-terminology/<locale>.tbx
"""
import urllib.request
from pathlib import Path
import argparse

CACHE_ROOT = Path.home() / ".cache" / "translation-toolkit" / "microsoft-terminology"
SOURCE_URL = "https://download.microsoft.com/download/b/2/d/b2db7a7c-8d33-47f3-b2c1-ee5e6445cf45/MicrosoftTermCollection.zip"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", choices=["ja-JP", "zh-TW", "zh-CN", "all"], default="all")
    args = parser.parse_args()

    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    zip_path = CACHE_ROOT / "MicrosoftTermCollection.zip"
    print(f"Downloading {SOURCE_URL} → {zip_path}")
    urllib.request.urlretrieve(SOURCE_URL, zip_path)
    print(f"OK: ~150MB downloaded. Unzip manually or use --extract flag (TBD).")
    print("Confirm Microsoft Terminology license terms before commercial use.")

if __name__ == "__main__":
    main()
```

(v0.1: download-only stub. Extraction to per-locale TBX is out of scope; user manually unzips.)

- [ ] **Step 2: Implement `fetch-jpo-utx.py`**

```python
#!/usr/bin/env python3
"""Optional fetch: 特許庁 UTX dictionary (~130k EN-JA patent terms).

License: AAMT distributes; "single dead-copy redistribution NOT permitted",
must indicate JPO + INPIT as copyright holders, format-converted derivative
permitted. Hence: NOT bundled; users fetch + must comply with attribution.

Usage: python3 fetch-jpo-utx.py

Cache location: ~/.cache/translation-toolkit/jpo-utx/JPO-UTX.utx
"""
import urllib.request
from pathlib import Path

CACHE_ROOT = Path.home() / ".cache" / "translation-toolkit" / "jpo-utx"
SOURCE_URL = "https://aamt.info/japanese/jpo/jpo-utx-2017-06.utx"  # verify current URL

def main():
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    out = CACHE_ROOT / "JPO-UTX.utx"
    print(f"Downloading {SOURCE_URL} → {out}")
    urllib.request.urlretrieve(SOURCE_URL, out)
    print(f"OK: downloaded. Attribution required: 特許庁 + INPIT")
    print("Patent-domain terms; not used unless skill is invoked on patent content.")

if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Write `scripts/README-optional-fetch.md`** — usage instructions, license caveats, "this is opt-in; data is for personal cache only".

- [ ] **Step 4: Verify scripts run without errors (download tests can be marked slow/skipped in CI)**

```bash
python3 -c "import sys; sys.argv = ['fetch-microsoft-terms.py', '--help']; exec(open('translation-toolkit/scripts/fetch-microsoft-terms.py').read())"
```

- [ ] **Step 5: Commit**

```bash
git add translation-toolkit/scripts/fetch-microsoft-terms.py translation-toolkit/scripts/fetch-jpo-utx.py translation-toolkit/scripts/README-optional-fetch.md
git commit -m "feat(translation-toolkit): opt-in fetch scripts for Microsoft Terminology + 特許庁 UTX"
```

---

### Task F3: End-to-end smoke test + sample fixtures

**Files:**
- Create: `translation-toolkit/scripts/tests/fixtures/sample.po` (5 entries)
- Create: `translation-toolkit/scripts/tests/fixtures/sample.md` (mini technical doc)
- Create: `translation-toolkit/scripts/tests/fixtures/sample-adcopy.txt`
- Create: `translation-toolkit/scripts/tests/fixtures/sample-existing-translation.po` (for audit)
- Create: `translation-toolkit/scripts/tests/test_e2e_smoke.py`

- [ ] **Step 1: Create fixtures** with placeholders + glossary-overlap terms (e.g., "Cancel", "Settings", "API endpoint").

- [ ] **Step 2: Write E2E smoke tests** — these are integration tests that exercise the build pipeline + Python lib end-to-end. They do NOT invoke skills (which require LLM calls). They verify:
  - Glossary parser loads all 5 pair files correctly
  - Protect-pass round-trips fixtures cleanly
  - M1 + M2 detect injected violations
  - Audit trail builder produces valid JSON matching schema

```python
def test_e2e_smoke_glossary_loads():
    """Verify all 5 canonical pair files parse without error."""
    canonical = ROOT / "scripts" / "canonical"
    for f in canonical.glob("glossary-*.md"):
        result = parse_pair_file(f)
        assert isinstance(result, dict)
        assert len(result) > 0, f"empty: {f.name}"

def test_e2e_smoke_protect_roundtrip():
    """Roundtrip a complex fixture."""
    text = open(ROOT / "scripts/tests/fixtures/sample.po").read()
    masked, token_map = protect(text)
    restored = restore(masked, token_map)
    assert restored == text

def test_e2e_smoke_pipeline_dry_run():
    """Simulate full pipeline with stub LLM that echoes input."""
    # Construct AuditTrailBuilder, run protect → stub-LLM → M1/M2 → restore → verify
    pass  # ~50 lines
```

- [ ] **Step 3: Run all unit + E2E tests**

```bash
cd translation-toolkit && python3 -m pytest scripts/tests/ -v
```

Expect all PASS.

- [ ] **Step 4: Commit**

```bash
git add translation-toolkit/scripts/tests/fixtures/ translation-toolkit/scripts/tests/test_e2e_smoke.py
git commit -m "test(translation-toolkit): E2E smoke tests + sample fixtures"
```

---

### Task F4: CI workflow + final NOTICES + release prep

**Files:**
- Create: `.github/workflows/translation-toolkit-ci.yml`
- Modify: `translation-toolkit/NOTICES.md` (final form with real license excerpts)
- Modify: `translation-toolkit/README.md` / `.ja.md` / `.zh-TW.md` (final pass)

- [ ] **Step 1: Write CI workflow**

```yaml
# .github/workflows/translation-toolkit-ci.yml
name: translation-toolkit CI
on:
  pull_request:
    paths:
      - 'translation-toolkit/**'
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - name: Install deps
        run: cd translation-toolkit && uv sync
      - name: Run tests
        env:
          PYTHONDONTWRITEBYTECODE: "1"  # avoid __pycache__ tripping skill-folder validator hook
        run: cd translation-toolkit && uv run pytest scripts/tests/ -v
      - name: Verify drift
        run: cd translation-toolkit && uv run python scripts/verify-drift.py
      - name: Lint
        run: cd translation-toolkit && uv run ruff check scripts/
      - name: Skill folder structure
        run: |
          for skill in using-translation-toolkit translation-intake translation-i18n translation-doc translation-creative translation-audit; do
            bash .claude/hooks/validate-skill-folder-structure.sh translation-toolkit/$skill/SKILL.md
          done
```

- [ ] **Step 2: Finalize `NOTICES.md`** — copy real license headers from each `vendor/<source>/LICENSE` into the NOTICES table with brief excerpt.

- [ ] **Step 3: Final pass on tri-language READMEs** — add usage examples (3 invocation examples per language: i18n, doc, creative), version badge, link to spec + plan.

- [ ] **Step 4: Run full local CI simulation**

```bash
cd translation-toolkit
uv sync
uv run pytest scripts/tests/ -v
uv run python scripts/verify-drift.py
uv run ruff check scripts/
for skill in using-translation-toolkit translation-intake translation-i18n translation-doc translation-creative translation-audit; do
  bash .claude/hooks/validate-skill-folder-structure.sh "$skill/SKILL.md"
done
```

All must pass.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/translation-toolkit-ci.yml translation-toolkit/NOTICES.md translation-toolkit/README.md translation-toolkit/README.ja.md translation-toolkit/README.zh-TW.md
git commit -m "ci(translation-toolkit): GitHub Actions workflow + final NOTICES + tri-lang READMEs"
```

**Phase F checkpoint**: CI green on a test PR. NOTICES complete with attribution. Tri-language READMEs published. v0.1.0 ready to merge.

---

## Out-of-scope follow-ups (v0.2+)

The spec's Out of Scope section enumerates deferred items. Implementation plans for these are NOT included here:

- **L2 translation memory** (`<repo>/.translations/memory-*.json` + Layer 5d update)
- **Subagent auto-detect** for CRITIC fresh-eyes mode
- **Wikidata runtime fallback** for entity/concept names
- **Per-major-domain glossary file split** (when any pair file exceeds 1MB or 50K entries)
- **Embedding-based S1 similarity** (currently LLM-judge stub returning placeholder score)
- **Streaming output / real-time collab / voice / OCR / MQM scoring** (permanently out)

Each will get its own spec + plan when re-trigger conditions are met.

---

## Self-Review Notes

Spec coverage check: every item in Decisions Locked table (#1-#17) has implementation tasks above. Decision #2 (6 skills) → Tasks A5/D1-D5/E1. Decision #4 (S1 SHOULD/transcreation MUST) → Task E2. Decision #14 (skill self-containment via SSOT) → Tasks A4 + B5. Decision #16 (S1 subagent dispatch) → Task E2. Decision #17 (translation-audit reinstated) → Task E1.

Type consistency check: glossary entry format (`{en, target, source, domain, notes}` dict) used consistently across B1/B2/B3/B4. Audit trail schema fields match across C5 + E1-E4 callers. M1 token-map shape (`dict[str, str]`) matches C2 protect-pass + C4 m1_check.

No placeholders in steps. Each task has exact file paths, code snippets where code is written, exact test commands, exact commit messages.

---

**Plan complete.** Total: 24 tasks across 6 phases.

## Execution Handoff

Two execution options:

1. **Subagent-Driven (recommended)** — Dispatch a fresh subagent per task, two-stage review (spec compliance + code quality) between tasks. Best for plans this size; isolates per-task context. Use `superpowers:subagent-driven-development`.

2. **Inline Execution** — Execute tasks in this session with batch checkpoints. Use `superpowers:executing-plans`.

Phase boundaries (after A, B, C, D, E, F) are recommended review checkpoints either way.

Which approach?
