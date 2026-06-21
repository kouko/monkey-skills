"""Structural tests for the dogfood-skill-testing skill.

Stdlib only (json, pathlib, re). YAML frontmatter is parsed by
hand-splitting the `---` fences — no third-party YAML dependency.
The skill directory resolves relative to this test file so the suite
runs from any working directory.
"""

import json
import re
from pathlib import Path

SKILL_DIR = Path(__file__).parent
SKILL_MD = SKILL_DIR / "SKILL.md"
DEFECT_TAXONOMY = SKILL_DIR / "references" / "defect-taxonomy.md"
REPORT_TEMPLATE = SKILL_DIR / "templates" / "dogfood-report-template.md"
TRIGGER_EVAL = SKILL_DIR / "trigger-eval.json"


def _read(path):
    """Read a file, asserting it exists so failures are clear (not import errors)."""
    assert path.exists(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


def _frontmatter(text):
    """Hand-split the leading ---fenced YAML frontmatter into a dict.

    Handles simple `key: value` lines and YAML block scalars
    (`key: >-` / `key: |`) by folding their indented continuation
    lines into a single string value.
    """
    assert text.startswith("---"), "SKILL.md must start with --- frontmatter fence"
    parts = text.split("---", 2)
    assert len(parts) >= 3, "SKILL.md must have an opening and closing --- fence"
    body = parts[1]

    fields = {}
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            i += 1
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in (">", ">-", "|", "|-", ">+", "|+"):
            # Block scalar: collect indented continuation lines.
            collected = []
            i += 1
            while i < len(lines) and (lines[i].startswith((" ", "\t")) or not lines[i].strip()):
                collected.append(lines[i].strip())
                i += 1
            fields[key] = " ".join(c for c in collected if c).strip()
        else:
            fields[key] = val
            i += 1
    return fields


def test_frontmatter():
    text = _read(SKILL_MD)
    fm = _frontmatter(text)
    assert fm.get("name") == "dogfood-skill-testing", f"name was {fm.get('name')!r}"
    desc = fm.get("description", "")
    assert len(desc) > 200, f"description too short: {len(desc)} chars"
    version = fm.get("version", "")
    assert re.match(r"^\d+\.\d+\.\d+$", version), f"version not semver: {version!r}"


def test_flat_folder():
    assert SKILL_DIR.exists(), f"skill dir missing: {SKILL_DIR}"
    # The skill ships references/ and templates/ subfolders; require them to
    # exist so this test fails meaningfully before the skill is built, then
    # verify each subfolder is flat (Anthropic no-nested-subdir convention).
    expected = [SKILL_DIR / "references", SKILL_DIR / "templates"]
    for sub in expected:
        assert sub.is_dir(), f"missing skill subfolder: {sub}"
    for sub in SKILL_DIR.iterdir():
        if not sub.is_dir():
            continue
        nested = [c for c in sub.iterdir() if c.is_dir()]
        assert not nested, f"flat-folder violation: {sub} contains subdirs {nested}"


def test_defect_taxonomy_content():
    text = _read(DEFECT_TAXONOMY)
    for sev in ("Critical", "High", "Medium", "Low"):
        assert sev in text, f"defect-taxonomy missing severity {sev!r}"
    categories = [
        "Trigger", "Over-trigger", "Cold-start", "Workflow", "Gate",
        "Jargon", "Convention", "Progressive", "Output",
    ]
    present = [c for c in categories if c in text]
    assert len(present) >= 7, f"only {len(present)} category words present: {present}"
    assert "%" in text, "defect-taxonomy must contain at least one '%' frequency"


def test_report_template_content():
    text = _read(REPORT_TEMPLATE)
    low = text.lower()
    for needle in ("severity", "category", "root cause", "why static", "location", "suggested fix"):
        assert needle in low, f"report template missing {needle!r}"
    assert "raw outputs" in low, "report template missing 'Raw outputs' appendix heading"


def test_trigger_eval_schema():
    text = _read(TRIGGER_EVAL)
    data = json.loads(text)
    assert isinstance(data, list) and data, "trigger-eval.json must be a non-empty list"
    for item in data:
        assert isinstance(item, dict), f"item not a dict: {item!r}"
        assert isinstance(item.get("query"), str), f"query not str: {item!r}"
        assert isinstance(item.get("should_trigger"), bool), f"should_trigger not bool: {item!r}"
    triggers = [it["should_trigger"] for it in data]
    assert any(triggers), "trigger-eval needs at least one should_trigger=True"
    assert not all(triggers), "trigger-eval needs at least one should_trigger=False"


def test_skill_md_refs():
    text = _read(SKILL_MD)
    assert "references/defect-taxonomy.md" in text, "SKILL.md must reference references/defect-taxonomy.md"
    assert "templates/dogfood-report-template.md" in text, "SKILL.md must reference templates/dogfood-report-template.md"
    # trigger-eval.json is a shipped bundle asset (the Probe A corpus starter) — it must be
    # documented so the skill doesn't make the reader rebuild it (re-dogfood finding 2026-06-03).
    assert "trigger-eval.json" in text, "SKILL.md must reference the shipped trigger-eval.json corpus"
    assert DEFECT_TAXONOMY.exists(), f"referenced file missing: {DEFECT_TAXONOMY}"
    assert REPORT_TEMPLATE.exists(), f"referenced file missing: {REPORT_TEMPLATE}"


def test_skill_md_workflow():
    text = _read(SKILL_MD).lower()
    for needle in ("activation", "cold-reader", "executor", "auditor", "claude -p", "docs/skill-dogfood"):
        assert needle in text, f"SKILL.md workflow missing {needle!r}"
    assert "fallback" in text or "fidelity" in text, "SKILL.md must mention 'fallback' or 'fidelity'"
