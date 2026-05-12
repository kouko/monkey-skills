#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest>=7.0"]
# ///
"""Tests for discover_playbook.py — discovery order + index shape.

Covered:
  - direct cwd hit
  - ancestor walk hit
  - BFS hit (nested project layouts)
  - exhaustion (returns found=false, never crashes)
  - clause indexing (flat / variant-folder / mixed)
  - dot-dir skip during BFS
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "legal-playbook-author"
    / "scripts"
    / "discover_playbook.py"
)


@pytest.fixture(scope="session")
def discover_module():
    spec = importlib.util.spec_from_file_location("discover_playbook", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["discover_playbook"] = module
    spec.loader.exec_module(module)
    return module


# -- direct hit -------------------------------------------------------------


def test_discovers_direct_cwd(tmp_path, discover_module):
    pb = tmp_path / "legal-playbook"
    pb.mkdir()
    (pb / "confidentiality.md").write_text("---\nclause_id: confidentiality\n---\n", encoding="utf-8")

    report = discover_module.discover(tmp_path)

    assert report["found"] is True
    assert report["source"] == "cwd"
    assert Path(report["path"]) == pb
    assert len(report["index"]) == 1
    assert report["index"][0]["clause_id"] == "confidentiality"
    assert report["index"][0]["layout"] == "flat"


# -- ancestor hit -----------------------------------------------------------


def test_discovers_ancestor(tmp_path, discover_module):
    pb = tmp_path / "legal-playbook"
    pb.mkdir()
    nested = tmp_path / "project" / "src" / "app"
    nested.mkdir(parents=True)

    report = discover_module.discover(nested)

    assert report["found"] is True
    assert report["source"] == "ancestor"
    assert Path(report["path"]) == pb


def test_ancestor_walk_respects_limit(tmp_path, discover_module):
    pb = tmp_path / "legal-playbook"
    pb.mkdir()
    # 7 levels deep — exceeds default 5 ancestor limit
    nested = tmp_path / "a" / "b" / "c" / "d" / "e" / "f" / "g"
    nested.mkdir(parents=True)

    report = discover_module.discover(nested, max_ancestors=5)

    # Default BFS depth=5 also won't reach playbook from nested because
    # BFS goes DOWN from cwd, not up
    assert report["found"] is False


# -- BFS hit ----------------------------------------------------------------


def test_discovers_via_bfs(tmp_path, discover_module):
    # legal-playbook is nested under a subfolder of cwd
    sub = tmp_path / "subproject"
    sub.mkdir()
    pb = sub / "legal-playbook"
    pb.mkdir()

    report = discover_module.discover(tmp_path)

    assert report["found"] is True
    assert report["source"] == "bfs"
    assert Path(report["path"]) == pb


def test_bfs_respects_depth_limit(tmp_path, discover_module):
    deep = tmp_path / "a" / "b" / "c" / "d" / "e" / "f"
    deep.mkdir(parents=True)
    pb = deep / "legal-playbook"
    pb.mkdir()

    # depth=2 won't reach legal-playbook 6 levels down
    report = discover_module.discover(tmp_path, bfs_depth=2)

    assert report["found"] is False


def test_bfs_skips_dot_dirs(tmp_path, discover_module):
    hidden = tmp_path / ".cache"
    hidden.mkdir()
    pb = hidden / "legal-playbook"
    pb.mkdir()

    report = discover_module.discover(tmp_path)

    assert report["found"] is False, ".cache/ should be skipped by BFS"


def test_bfs_skips_node_modules(tmp_path, discover_module):
    nm = tmp_path / "node_modules"
    nm.mkdir()
    pb = nm / "legal-playbook"
    pb.mkdir()

    report = discover_module.discover(tmp_path)

    assert report["found"] is False


# -- exhaustion -------------------------------------------------------------


def test_returns_not_found(tmp_path, discover_module):
    report = discover_module.discover(tmp_path)

    assert report["found"] is False
    assert report["index"] == []
    assert report["source"] is None
    assert report["path"] is None
    assert len(report["search_log"]) >= 1


# -- indexing ---------------------------------------------------------------


def test_indexes_mixed_layout(tmp_path, discover_module):
    pb = tmp_path / "legal-playbook"
    pb.mkdir()

    # flat clauses
    (pb / "confidentiality.md").write_text("---\nclause_id: confidentiality\n---\n", encoding="utf-8")
    (pb / "auto-renewal.md").write_text("---\nclause_id: auto-renewal\n---\n", encoding="utf-8")

    # variant-folder
    lol = pb / "limitation-of-liability"
    lol.mkdir()
    (lol / "_clause.md").write_text("---\nclause_id: limitation-of-liability\nhas_variants: true\n---\n", encoding="utf-8")
    (lol / "small-deal.md").write_text("---\nclause_id: limitation-of-liability\nvariant_id: small-deal\n---\n", encoding="utf-8")
    (lol / "mid-deal.md").write_text("---\nclause_id: limitation-of-liability\nvariant_id: mid-deal\n---\n", encoding="utf-8")

    report = discover_module.discover(tmp_path)

    assert report["found"] is True
    clause_ids = {e["clause_id"] for e in report["index"]}
    assert clause_ids == {"auto-renewal", "confidentiality", "limitation-of-liability"}

    lol_entry = next(e for e in report["index"] if e["clause_id"] == "limitation-of-liability")
    assert lol_entry["layout"] == "variant-folder"
    variant_ids = {v["variant_id"] for v in lol_entry["variants"]}
    assert variant_ids == {"small-deal", "mid-deal"}


def test_skips_seed_readme(tmp_path, discover_module):
    pb = tmp_path / "legal-playbook"
    pb.mkdir()
    (pb / "README.md").write_text("# Legal Playbook\n", encoding="utf-8")
    (pb / "confidentiality.md").write_text("---\nclause_id: confidentiality\n---\n", encoding="utf-8")

    report = discover_module.discover(tmp_path)

    clause_ids = [e["clause_id"] for e in report["index"]]
    assert clause_ids == ["confidentiality"]  # README excluded


def test_skips_unrecognised_variant_folder(tmp_path, discover_module):
    pb = tmp_path / "legal-playbook"
    pb.mkdir()
    # a directory without _clause.md is not a variant-folder
    junk = pb / "looks-like-a-clause"
    junk.mkdir()
    (junk / "random.md").write_text("not a clause\n", encoding="utf-8")
    (pb / "confidentiality.md").write_text("---\nclause_id: confidentiality\n---\n", encoding="utf-8")

    report = discover_module.discover(tmp_path)

    clause_ids = [e["clause_id"] for e in report["index"]]
    assert clause_ids == ["confidentiality"]
