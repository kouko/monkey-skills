#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["jsonschema>=4.20", "pyyaml>=6.0", "pytest>=7.0"]
# ///
"""Tests for build_baseline.py + seed_baseline.py end-to-end.

Covers:
  - build_baseline determinism (--check vs fresh build)
  - manifest shape + hash agreement
  - seed_baseline extracts all 8 clauses + 17 files
  - seed_baseline mutates frontmatter (source_type / last_updated)
  - seed_baseline writes seed-history.yml
  - seed_baseline refuses overwrite without --force
  - seed_baseline --merge skips existing
  - seed_baseline --dry-run writes nothing
  - cross-check: extracted files validate against the JSON schema
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = REPO_ROOT / "skills" / "legal-contract-review" / "scripts" / "build_baseline.py"
SEED_SCRIPT = REPO_ROOT / "skills" / "legal-contract-review" / "scripts" / "seed_baseline.py"
VALIDATE_SCRIPT = REPO_ROOT / "skills" / "legal-playbook-author" / "scripts" / "validate_schema.py"
TARBALL_PATH = REPO_ROOT / "skills" / "legal-contract-review" / "assets" / "baseline-playbooks.tar.gz"
MANIFEST_PATH = REPO_ROOT / "skills" / "legal-contract-review" / "assets" / "seed-manifest.yml"
SCHEMA_PATH = REPO_ROOT / "skills" / "legal-playbook-author" / "assets" / "schema.json"


def _load(script_path: Path, mod_name: str):
    spec = importlib.util.spec_from_file_location(mod_name, script_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def seed_module():
    return _load(SEED_SCRIPT, "seed_baseline")


@pytest.fixture(scope="session")
def build_module():
    return _load(BUILD_SCRIPT, "build_baseline")


@pytest.fixture(scope="session")
def validate_module():
    return _load(VALIDATE_SCRIPT, "validate_schema")


# ----------------------------------------------------------- build determinism


def test_build_artifact_exists():
    assert TARBALL_PATH.is_file(), "build_baseline.py must be committed with the tarball"
    assert MANIFEST_PATH.is_file()


def test_manifest_hash_matches_tarball():
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    actual = hashlib.sha256(TARBALL_PATH.read_bytes()).hexdigest()
    assert manifest["tarball_sha256"] == actual


def test_manifest_counts():
    manifest = yaml.safe_load(MANIFEST_PATH.read_text(encoding="utf-8"))
    assert manifest["total_clauses"] == 8
    assert manifest["total_files"] == 17  # 4 flat + 1 ip-flat + 3*4 variant-folder files
    assert manifest["version"] == "1.0"


def test_build_check_passes(build_module):
    """Re-build in memory and compare to committed bytes."""
    entries = build_module._enumerate_entries()
    fresh_tar = build_module._build_tarball_bytes(entries)
    committed_tar = TARBALL_PATH.read_bytes()
    assert fresh_tar == committed_tar, "tarball drift — re-run build_baseline.py"


# ----------------------------------------------------------- seed_baseline


def test_seed_extracts_all_files(seed_module, tmp_path):
    report = seed_module.seed(tmp_path)
    pb = tmp_path / "legal-playbook"
    md_files = sorted(p.relative_to(pb).as_posix() for p in pb.rglob("*.md"))
    assert len(md_files) == 17
    assert "auto-renewal.md" in md_files
    assert "limitation-of-liability/_clause.md" in md_files
    assert "limitation-of-liability/small-deal.md" in md_files


def test_seed_mutates_source_type(seed_module, tmp_path):
    seed_module.seed(tmp_path)
    sample = (tmp_path / "legal-playbook" / "confidentiality.md").read_text(encoding="utf-8")
    assert "source_type: user_playbook" in sample
    assert "source_type: bundled_fallback" not in sample


def test_seed_mutates_last_updated(seed_module, tmp_path):
    seed_module.seed(tmp_path)
    today = _dt.date.today().isoformat()
    sample = (tmp_path / "legal-playbook" / "confidentiality.md").read_text(encoding="utf-8")
    assert f"last_updated: {today}" in sample


def test_seed_preserves_escalate_to_placeholder(seed_module, tmp_path):
    seed_module.seed(tmp_path)
    sample = (tmp_path / "legal-playbook" / "confidentiality.md").read_text(encoding="utf-8")
    # placeholder must STILL be present so user sees they need to edit
    assert "[請編輯為你公司的角色" in sample


def test_seed_writes_history(seed_module, tmp_path):
    seed_module.seed(tmp_path)
    hist_path = tmp_path / ".legal-toolkit" / "seed-history.yml"
    assert hist_path.is_file()
    hist = yaml.safe_load(hist_path.read_text(encoding="utf-8"))
    assert isinstance(hist, list)
    assert len(hist) == 1
    assert hist[0]["total_clauses"] == 8
    assert hist[0]["mode"] == "fresh"
    assert len(hist[0]["files_written"]) == 17


def test_seed_refuses_existing_without_force(seed_module, tmp_path):
    pb = tmp_path / "legal-playbook"
    pb.mkdir()
    (pb / "existing.md").write_text("---\nclause_id: existing\n---\n")
    with pytest.raises(SystemExit):
        seed_module.seed(tmp_path)


def test_seed_force_overwrites(seed_module, tmp_path):
    pb = tmp_path / "legal-playbook"
    pb.mkdir()
    (pb / "confidentiality.md").write_text("OLD CONTENT", encoding="utf-8")
    report = seed_module.seed(tmp_path, force=True)
    sample = (pb / "confidentiality.md").read_text(encoding="utf-8")
    assert "OLD CONTENT" not in sample
    assert len(report["files_overwritten"]) >= 1


def test_seed_merge_skips_existing(seed_module, tmp_path):
    pb = tmp_path / "legal-playbook"
    pb.mkdir()
    (pb / "confidentiality.md").write_text("MY OWN VERSION", encoding="utf-8")
    report = seed_module.seed(tmp_path, merge=True)
    sample = (pb / "confidentiality.md").read_text(encoding="utf-8")
    assert sample == "MY OWN VERSION"  # not overwritten
    assert "confidentiality.md" in report["files_skipped"]
    # Other files were still seeded
    assert (pb / "auto-renewal.md").is_file()


def test_seed_dry_run_writes_nothing(seed_module, tmp_path):
    report = seed_module.seed(tmp_path, dry_run=True)
    pb = tmp_path / "legal-playbook"
    assert report["dry_run"] is True
    assert len(report["files_written"]) == 17  # report still lists them
    # But nothing actually written
    assert not pb.exists() or not list(pb.rglob("*.md"))


# ----------------------------------------------------------- cross-check schema


def test_seeded_files_validate_against_schema(seed_module, validate_module, tmp_path):
    """The 17 seeded files MUST validate against the JSON schema."""
    seed_module.seed(tmp_path)
    pb = tmp_path / "legal-playbook"

    import jsonschema
    schema = json.loads(SCHEMA_PATH.read_text())
    v = jsonschema.Draft202012Validator(schema)

    failures = []
    for md in sorted(pb.rglob("*.md")):
        record = validate_module.validate_one(md, v)
        if not record["ok"]:
            failures.append((md.relative_to(pb).as_posix(), record["errors"]))
    assert failures == [], f"seeded files failed schema validation: {failures}"
