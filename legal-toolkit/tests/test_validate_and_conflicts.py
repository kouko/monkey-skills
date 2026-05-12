#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema>=4.20", "pyyaml>=6.0", "pytest>=7.0"]
# ///
"""Tests for validate_schema.py + detect_conflicts.py.

Covers:
  - validate_schema: PASS on valid fixtures, FAIL on broken ones
  - validate_schema: frontmatter parsing edges (missing / unparseable)
  - detect_conflicts: duplicate clause_id (flat-vs-flat, flat-vs-folder)
  - detect_conflicts: overlapping gates (numeric range, enum, mixed)
  - detect_conflicts: clean playbook returns zero conflicts
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
import textwrap

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATE_SCRIPT = REPO_ROOT / "skills" / "legal-playbook-author" / "scripts" / "validate_schema.py"
CONFLICTS_SCRIPT = REPO_ROOT / "skills" / "legal-playbook-author" / "scripts" / "detect_conflicts.py"


def _load(script_path: Path, mod_name: str):
    spec = importlib.util.spec_from_file_location(mod_name, script_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def validate_module():
    return _load(VALIDATE_SCRIPT, "validate_schema")


@pytest.fixture(scope="session")
def conflicts_module():
    return _load(CONFLICTS_SCRIPT, "detect_conflicts")


def _write_md(dir: Path, name: str, frontmatter: str, body: str = "# Test\n"):
    p = dir / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"---\n{frontmatter}\n---\n{body}", encoding="utf-8")
    return p


# -------------------------------------------------------------------- validate


def test_validate_extracts_frontmatter(validate_module, tmp_path):
    p = _write_md(tmp_path, "x.md", "clause_id: confidentiality\nfoo: bar")
    fm = validate_module.extract_frontmatter(p.read_text())
    assert fm == {"clause_id": "confidentiality", "foo": "bar"}


def test_validate_missing_frontmatter(validate_module, tmp_path):
    p = tmp_path / "no-fm.md"
    p.write_text("just a markdown body, no frontmatter\n", encoding="utf-8")
    fm = validate_module.extract_frontmatter(p.read_text())
    assert fm is None


def test_validate_pass_flat(validate_module, tmp_path):
    p = _write_md(
        tmp_path,
        "confidentiality.md",
        textwrap.dedent(
            """\
            clause_id: confidentiality
            walk_away_triggers:
              - 單方面
            escalate_to: GC
            risk_default: yellow
            source_type: user_playbook
            """
        ).rstrip(),
    )
    import json as _json
    schema = _json.loads((REPO_ROOT / "skills/legal-playbook-author/assets/schema.json").read_text())
    import jsonschema
    v = jsonschema.Draft202012Validator(schema)
    record = validate_module.validate_one(p, v)
    assert record["ok"] is True, record["errors"]


def test_validate_fail_missing_required(validate_module, tmp_path):
    p = _write_md(
        tmp_path,
        "broken.md",
        "clause_id: confidentiality\n",  # missing walk_away_triggers, escalate_to, etc.
    )
    import json as _json
    schema = _json.loads((REPO_ROOT / "skills/legal-playbook-author/assets/schema.json").read_text())
    import jsonschema
    v = jsonschema.Draft202012Validator(schema)
    record = validate_module.validate_one(p, v)
    assert record["ok"] is False
    assert len(record["errors"]) > 0


# -------------------------------------------------------------------- conflicts: duplicates


def test_conflicts_clean_playbook(conflicts_module, tmp_path):
    pb = tmp_path / "legal-playbook"
    pb.mkdir()
    _write_md(
        pb,
        "confidentiality.md",
        "clause_id: confidentiality\nwalk_away_triggers: [x]\nescalate_to: GC\nrisk_default: yellow\nsource_type: user_playbook",
    )
    _write_md(
        pb,
        "auto-renewal.md",
        "clause_id: auto-renewal\nwalk_away_triggers: [x]\nescalate_to: GC\nrisk_default: yellow\nsource_type: user_playbook",
    )
    report = conflicts_module.detect(pb)
    assert report["total_conflicts"] == 0
    assert report["total_entries"] == 2


def test_conflicts_duplicate_flat_flat(conflicts_module, tmp_path):
    pb = tmp_path / "legal-playbook"
    pb.mkdir()
    _write_md(pb, "a.md", "clause_id: confidentiality\nwalk_away_triggers: [x]\nescalate_to: GC\nrisk_default: yellow\nsource_type: user_playbook")
    _write_md(pb, "b.md", "clause_id: confidentiality\nwalk_away_triggers: [y]\nescalate_to: GC\nrisk_default: yellow\nsource_type: user_playbook")
    report = conflicts_module.detect(pb)
    types = [c["type"] for c in report["conflicts"]]
    assert "duplicate_clause_id" in types


def test_conflicts_duplicate_flat_vs_folder(conflicts_module, tmp_path):
    pb = tmp_path / "legal-playbook"
    pb.mkdir()
    _write_md(pb, "limitation-of-liability.md", "clause_id: limitation-of-liability\nwalk_away_triggers: [x]\nescalate_to: GC\nrisk_default: yellow\nsource_type: user_playbook")
    lol = pb / "limitation-of-liability"
    lol.mkdir()
    _write_md(lol, "_clause.md", "clause_id: limitation-of-liability\ncontract_types_applicable: [SaaS]\nhas_variants: true")
    _write_md(lol, "small.md", "clause_id: limitation-of-liability\nvariant_id: small\ngates:\n  deal_size:\n    lt: 100000\nwalk_away_triggers: [x]\nescalate_to: GC\nrisk_default: yellow\nsource_type: user_playbook")
    report = conflicts_module.detect(pb)
    types = [c["type"] for c in report["conflicts"]]
    assert "duplicate_clause_id" in types


def test_conflicts_missing_clause_id(conflicts_module, tmp_path):
    pb = tmp_path / "legal-playbook"
    pb.mkdir()
    _write_md(pb, "naked.md", "foo: bar")  # no clause_id
    report = conflicts_module.detect(pb)
    types = [c["type"] for c in report["conflicts"]]
    assert "missing_clause_id" in types


# -------------------------------------------------------------------- conflicts: overlapping gates


def test_conflicts_overlapping_numeric_gates(conflicts_module, tmp_path):
    pb = tmp_path / "legal-playbook"
    pb.mkdir()
    lol = pb / "limitation-of-liability"
    lol.mkdir()
    _write_md(lol, "_clause.md", "clause_id: limitation-of-liability\ncontract_types_applicable: [SaaS]\nhas_variants: true")
    _write_md(
        lol,
        "small.md",
        textwrap.dedent("""\
            clause_id: limitation-of-liability
            variant_id: small
            gates:
              deal_size:
                lt: 200000
            walk_away_triggers: [x]
            escalate_to: GC
            risk_default: yellow
            source_type: user_playbook
        """).rstrip(),
    )
    _write_md(
        lol,
        "mid.md",
        textwrap.dedent("""\
            clause_id: limitation-of-liability
            variant_id: mid
            gates:
              deal_size:
                gte: 100000
                lt: 1000000
            walk_away_triggers: [y]
            escalate_to: GC
            risk_default: yellow
            source_type: user_playbook
        """).rstrip(),
    )
    report = conflicts_module.detect(pb)
    overlap = [c for c in report["conflicts"] if c["type"] == "overlapping_gates"]
    assert len(overlap) == 1
    assert {overlap[0]["variant_a"], overlap[0]["variant_b"]} == {"small", "mid"}


def test_conflicts_non_overlapping_numeric_gates(conflicts_module, tmp_path):
    pb = tmp_path / "legal-playbook"
    pb.mkdir()
    lol = pb / "limitation-of-liability"
    lol.mkdir()
    _write_md(lol, "_clause.md", "clause_id: limitation-of-liability\ncontract_types_applicable: [SaaS]\nhas_variants: true")
    _write_md(lol, "small.md", "clause_id: limitation-of-liability\nvariant_id: small\ngates:\n  deal_size:\n    lt: 100000\nwalk_away_triggers: [x]\nescalate_to: GC\nrisk_default: yellow\nsource_type: user_playbook")
    _write_md(lol, "mid.md", "clause_id: limitation-of-liability\nvariant_id: mid\ngates:\n  deal_size:\n    gte: 100000\n    lt: 1000000\nwalk_away_triggers: [y]\nescalate_to: GC\nrisk_default: yellow\nsource_type: user_playbook")
    _write_md(lol, "large.md", "clause_id: limitation-of-liability\nvariant_id: large\ngates:\n  deal_size:\n    gte: 1000000\nwalk_away_triggers: [z]\nescalate_to: GC\nrisk_default: yellow\nsource_type: user_playbook")
    report = conflicts_module.detect(pb)
    assert report["total_conflicts"] == 0


def test_conflicts_overlapping_enum_gates(conflicts_module, tmp_path):
    pb = tmp_path / "legal-playbook"
    pb.mkdir()
    dpa = pb / "data-protection-dpa"
    dpa.mkdir()
    _write_md(dpa, "_clause.md", "clause_id: data-protection-dpa\ncontract_types_applicable: [SaaS]\nhas_variants: true")
    _write_md(
        dpa,
        "a.md",
        textwrap.dedent("""\
            clause_id: data-protection-dpa
            variant_id: a
            gates:
              jurisdiction:
                any_of: [EU, UK]
            walk_away_triggers: [x]
            escalate_to: GC
            risk_default: red
            source_type: user_playbook
        """).rstrip(),
    )
    _write_md(
        dpa,
        "b.md",
        textwrap.dedent("""\
            clause_id: data-protection-dpa
            variant_id: b
            gates:
              jurisdiction:
                any_of: [UK, EEA]
            walk_away_triggers: [y]
            escalate_to: GC
            risk_default: red
            source_type: user_playbook
        """).rstrip(),
    )
    report = conflicts_module.detect(pb)
    overlap = [c for c in report["conflicts"] if c["type"] == "overlapping_gates"]
    assert len(overlap) == 1  # UK overlaps both


def test_conflicts_disjoint_enum_gates(conflicts_module, tmp_path):
    pb = tmp_path / "legal-playbook"
    pb.mkdir()
    dpa = pb / "data-protection-dpa"
    dpa.mkdir()
    _write_md(dpa, "_clause.md", "clause_id: data-protection-dpa\ncontract_types_applicable: [SaaS]\nhas_variants: true")
    _write_md(dpa, "a.md", "clause_id: data-protection-dpa\nvariant_id: a\ngates:\n  jurisdiction:\n    any_of: [EU, UK]\nwalk_away_triggers: [x]\nescalate_to: GC\nrisk_default: red\nsource_type: user_playbook")
    _write_md(dpa, "b.md", "clause_id: data-protection-dpa\nvariant_id: b\ngates:\n  jurisdiction:\n    any_of: [US, CA]\nwalk_away_triggers: [y]\nescalate_to: GC\nrisk_default: red\nsource_type: user_playbook")
    report = conflicts_module.detect(pb)
    assert report["total_conflicts"] == 0
