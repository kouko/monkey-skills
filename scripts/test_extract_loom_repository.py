"""History extraction safety and provenance contracts, on an actual Git DAG."""
from pathlib import Path
import json
import os
import runpy
import subprocess

import pytest

from scripts import extract_loom_repository as extraction


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


@pytest.fixture
def source(tmp_path):
    repo = tmp_path / "source"
    repo.mkdir()
    git(repo, "init", "-q")
    git(repo, "config", "user.name", "Fixture Author")
    git(repo, "config", "user.email", "fixture@example.test")
    for root in extraction.PLUGIN_ROOTS:
        (repo / root).mkdir()
        (repo / root / "file.txt").write_text("first\n")
    (repo / "unrelated.txt").write_text("private unrelated\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "Initial mixed commit")
    (repo / "loom-code/file.txt").write_text("second\n")
    (repo / "unrelated.txt").write_text("another unrelated change\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "Second mixed commit")
    return repo


def test_inventory_preserves_current_coverage_mixed_changes_and_metadata(source):
    head = git(source, "rev-parse", "HEAD")
    config = (source / ".git/config").read_bytes()
    result = extraction.inventory(source, head, extraction.PLUGIN_ROOTS)
    assert result["source_commit"] == head
    assert set(result["files"]) == {f"{p}file.txt" for p in extraction.PLUGIN_ROOTS}
    assert len(result["commits"]) == 2
    last = result["commits"][-1]
    assert last["old"] == head
    assert last["mixed"] is True
    assert last["retained_paths"] == ["loom-code/file.txt"]
    assert last["author_name"] == "Fixture Author"
    assert last["author_email"] == "fixture@example.test"
    assert last["author_date"] == git(source, "show", "-s", "--format=%aI", head)
    assert last["message"] == "Second mixed commit\n"
    assert (source / ".git/config").read_bytes() == config
    assert git(source, "status", "--porcelain") == ""


def test_missing_required_root_fails(source):
    with pytest.raises(ValueError, match="required"):
        extraction.inventory(source, "HEAD", ["loom-code/"])


def test_missing_declared_path_fails(source):
    with pytest.raises(ValueError, match="absent"):
        extraction.inventory(source, "HEAD", [*extraction.PLUGIN_ROOTS, "missing.py"])


def test_required_shared_file_cannot_be_silently_omitted(source):
    with pytest.raises(ValueError, match="required path coverage"):
        extraction.inventory(source, "HEAD", extraction.PLUGIN_ROOTS,
                             required_paths=["unrelated.txt"])


def test_deleted_historical_path_is_inventoried(source):
    (source / "retired-loom").mkdir()
    (source / "retired-loom/old.txt").write_text("historical ancestor\n")
    git(source, "add", ".")
    git(source, "commit", "-qm", "Add predecessor")
    old = git(source, "rev-parse", "HEAD")
    git(source, "rm", "retired-loom/old.txt")
    git(source, "commit", "-qm", "Remove predecessor")
    result = extraction.inventory(source, "HEAD", [*extraction.PLUGIN_ROOTS, "retired-loom/"])
    assert "retired-loom/old.txt" not in result["files"]
    assert old in [entry["old"] for entry in result["commits"]]
    assert result["commits"][-1]["retained_paths"] == ["retired-loom/old.txt"]


def test_merge_inventory_covers_both_parent_sides(source):
    main = git(source, "branch", "--show-current")
    git(source, "checkout", "-qb", "topic")
    (source / "loom-design/file.txt").write_text("topic\n")
    git(source, "commit", "-qam", "Topic Loom change")
    topic = git(source, "rev-parse", "HEAD")
    git(source, "checkout", "-q", main)
    (source / "unrelated.txt").write_text("main unrelated\n")
    git(source, "commit", "-qam", "Main unrelated change")
    unrelated = git(source, "rev-parse", "HEAD")
    git(source, "merge", "--no-ff", "-qm", "Merge topic", "topic")
    result = extraction.inventory(source, "HEAD", extraction.PLUGIN_ROOTS)
    assert topic in [entry["old"] for entry in result["commits"]]
    assert unrelated in result["all_commits"]
    assert unrelated not in [entry["old"] for entry in result["commits"]]
    assert result["commits"][-1]["retained_paths"] == ["loom-design/file.txt"]


def test_retained_population_rejects_non_loom(source):
    with pytest.raises(ValueError, match="unclassified"):
        extraction.validate_retained_paths(["loom-code/file.txt", "unrelated.txt"], extraction.PLUGIN_ROOTS)


def test_destination_must_be_new_and_outside_source(source, tmp_path):
    extraction.validate_destination(source, tmp_path / "new-candidate")
    for destination in (source, source / "candidate", tmp_path):
        with pytest.raises(ValueError):
            extraction.validate_destination(source, destination)
    link = tmp_path / "dangling"
    link.symlink_to(tmp_path / "absent")
    with pytest.raises(ValueError):
        extraction.validate_destination(source, link)


@pytest.mark.parametrize("path", ["../outside", "/absolute", "docs/loom/", "scripts/", "loom-code/*", "loom-code/../other", "./loom-code/", ".git/config"])
def test_manifest_rejects_broad_or_unsafe_paths(tmp_path, path):
    manifest = tmp_path / "paths.txt"
    manifest.write_text(path + "\n")
    with pytest.raises(ValueError):
        extraction.read_manifest(manifest)


def test_manifest_allows_explicit_reviewed_paths(tmp_path):
    manifest = tmp_path / "paths.txt"
    manifest.write_text("# Reviewed roots\nloom-code/\ndocs/loom/example/spec.md\n")
    assert extraction.read_manifest(manifest) == ["loom-code/", "docs/loom/example/spec.md"]


def test_commit_map_requires_full_source_population_and_retained_commits():
    old, removed, new = "1" * 40, "2" * 40, "3" * 40
    assert extraction.validate_commit_map(f"old new\n{old} {new}\n{removed} {'0' * 40}\n", [old, removed], [old]) == {old: new, removed: "0" * 40}
    for content in (f"old new\n{old} {new}\n", f"old new\n{old} {'0' * 40}\n{removed} {'0' * 40}\n"):
        with pytest.raises(ValueError):
            extraction.validate_commit_map(content, [old, removed], [old])


@pytest.mark.parametrize("rows", ["bad row", "1 2", f"{'1' * 40} {'2' * 40}\n{'1' * 40} {'3' * 40}"])
def test_commit_map_rejects_malformed_or_duplicate_rows(rows):
    with pytest.raises(ValueError):
        extraction.validate_commit_map("old new\n" + rows, ["1" * 40], ["1" * 40])


def test_extract_real_clone_preserves_map_blame_and_source(source, tmp_path):
    head = git(source, "rev-parse", "HEAD")
    git(source, "update-ref", "refs/remotes/origin/main", head)
    before = extraction.source_snapshot(source)
    destination = tmp_path / "candidate"
    report = extraction.extract_repository(source, destination, head, extraction.PLUGIN_ROOTS)
    assert extraction.source_snapshot(source) == before
    assert git(destination, "remote") == ""
    assert report["source_commit"] == head
    assert report["verified_commits"] == 2
    assert report["mixed_commits"] == 2
    assert (destination / "docs/migration/commit-map.tsv").is_file()
    assert (destination / "README.md").read_text().startswith("# Loom\n")
    assert (destination / "loom-code/scripts/test_probes_cumulative_boundary_reassessment.py").is_file()
    assert not list(destination.rglob("*.template"))
    mapping = extraction.validate_commit_map((destination / "docs/migration/commit-map.tsv").read_text(),
                                             git(source, "rev-list", head).splitlines(), [head])
    assert mapping[head] != head
    assert git(destination, "show", "-s", "--format=%B", mapping[head]) == "Second mixed commit"
    assert "Fixture Author" in git(destination, "blame", "loom-code/file.txt")
    assert not (destination / "unrelated.txt").exists()
    assert git(destination, "status", "--porcelain") == ""


def test_extract_rejects_stale_source_before_creating_destination(source, tmp_path):
    head = git(source, "rev-parse", "HEAD")
    git(source, "update-ref", "refs/remotes/origin/main", head)
    destination = tmp_path / "candidate"
    with pytest.raises(ValueError, match="source ref"):
        extraction.extract_repository(source, destination, git(source, "rev-parse", "HEAD~1"), extraction.PLUGIN_ROOTS)
    assert not destination.exists()


def test_extract_rejects_existing_destination_without_mutation(source, tmp_path):
    head = git(source, "rev-parse", "HEAD")
    git(source, "update-ref", "refs/remotes/origin/main", head)
    destination = tmp_path / "candidate"
    destination.mkdir()
    marker = destination / "keep.txt"
    marker.write_text("keep\n")
    with pytest.raises(ValueError, match="already exists"):
        extraction.extract_repository(source, destination, head, extraction.PLUGIN_ROOTS)
    assert marker.read_text() == "keep\n"


def test_extract_prunes_unrelated_commit_and_preserves_retained_merge(source, tmp_path):
    main = git(source, "branch", "--show-current")
    git(source, "checkout", "-qb", "topic")
    (source / "loom-design/file.txt").write_text("topic\n")
    git(source, "commit", "-qam", "Topic retained")
    git(source, "checkout", "-q", main)
    (source / "unrelated.txt").write_text("Unrelated only\n")
    git(source, "commit", "-qam", "Unrelated only")
    unrelated = git(source, "rev-parse", "HEAD")
    git(source, "merge", "--no-ff", "-qm", "Retained merge", "topic")
    head = git(source, "rev-parse", "HEAD")
    git(source, "update-ref", "refs/remotes/origin/main", head)
    destination = tmp_path / "candidate"
    extraction.extract_repository(source, destination, head, extraction.PLUGIN_ROOTS)
    mapping = extraction.validate_commit_map((destination / "docs/migration/commit-map.tsv").read_text(),
                                             git(source, "rev-list", head).splitlines(), [head])
    assert mapping[unrelated] == "0" * 40
    assert mapping[head] != "0" * 40
    assert "Unrelated only" not in git(destination, "log", "--format=%s")


def test_extract_rejects_shallow_source_before_creating_destination(source, tmp_path):
    shallow = tmp_path / "shallow"
    subprocess.run(["git", "clone", "--depth", "1", source.as_uri(), str(shallow)], check=True)
    head = git(shallow, "rev-parse", "HEAD")
    destination = tmp_path / "candidate"
    with pytest.raises(ValueError, match="shallow"):
        extraction.extract_repository(shallow, destination, head, extraction.PLUGIN_ROOTS, source_ref="HEAD")
    assert not destination.exists()


def test_bootstrap_limits_manifests_and_marketplace_to_three_plugins():
    bootstrap = Path(extraction.__file__).with_name("loom-repository-bootstrap")
    namespace = runpy.run_path(str(bootstrap / "scripts/sync_codex_manifests.py"))
    expected = {root.rstrip("/") for root in extraction.PLUGIN_ROOTS}
    assert set(namespace["CODEX_ELIGIBLE"]) == expected
    marketplace = json.loads((bootstrap / ".claude-plugin/marketplace.json").read_text())
    assert {plugin["name"] for plugin in marketplace["plugins"]} == expected
    assert len(marketplace["plugins"]) == 3
    assert all(plugin["source"] == f"./{plugin['name']}/" for plugin in marketplace["plugins"])


def test_manifest_includes_shared_dependencies_of_retained_gates():
    paths = extraction.read_manifest()
    for path in ("requirements-package-tests.lock", ".claude/hooks/test_check_codex_manifest_drift.py",
                 "docs/skill-dogfood/2026-09-13-compress-loom-skill-descriptions/cases.md",
                 "CLAUDE.md", "PRINCIPLES.md",
                 "docs/skill-dogfood/2026-09-09-model-effort-cost-pilot/report.md",
                 "docs/loom/plans/2026-07-18-knowledge-triage-three-buckets.md"):
        assert extraction.selected(path, paths), path


def test_bootstrap_history_lookup_maps_revisions_but_not_frozen_evidence(tmp_path):
    helper = Path(extraction.__file__).with_name("loom-repository-bootstrap") / "loom-code/scripts/_migration_history.py"
    resolve = runpy.run_path(str(helper))["migration_git_args"]
    migration = tmp_path / "docs/migration"
    migration.mkdir(parents=True)
    old, new = "1" * 40, "2" * 40
    (migration / "commit-map.tsv").write_text(f"old new\n{old} {new}\n")
    assert resolve(tmp_path, ("git", "show", old + ":file")) == ("git", "show", new + ":file")
    assert resolve(tmp_path, ("git", "show", old[:8] + ":file"))[-1] == new + ":file"
    assert resolve(tmp_path, ("git", "show", "3" * 40))[-1] == "3" * 40
    assert resolve(tmp_path, ("printf", old)) == ("printf", old)


def test_auxiliary_history_is_referenced_filtered_and_isolated(source, tmp_path):
    main = git(source, "branch", "--show-current")
    git(source, "checkout", "-qb", "evidence-topic")
    (source / "loom-code/file.txt").write_text("auxiliary evidence\n")
    git(source, "commit", "-qam", "Referenced development evidence")
    tip = git(source, "rev-parse", "HEAD")
    git(source, "checkout", "-q", main)
    git(source, "checkout", "-qb", "abandoned-topic")
    (source / "loom-code/file.txt").write_text("unreferenced abandoned branch\n")
    git(source, "commit", "-qam", "Unreferenced abandoned development")
    abandoned = git(source, "rev-parse", "HEAD")
    git(source, "checkout", "-q", main)
    (source / "loom-code/citation.md").write_text(tip + "\n")
    git(source, "add", ".")
    git(source, "commit", "-qm", "Record required evidence identity")
    head = git(source, "rev-parse", "HEAD")
    git(source, "update-ref", "refs/remotes/origin/main", head)
    destination = tmp_path / "candidate"
    report = extraction.extract_repository(source, destination, head, extraction.PLUGIN_ROOTS,
        auxiliary=[{"commit": tip, "citations": ["loom-code/citation.md"]}])
    mapping = dict(line.split() for line in (destination / "docs/migration/commit-map.tsv").read_text().splitlines()[1:])
    assert tip in mapping and mapping[tip] != "0" * 40
    assert abandoned not in mapping
    assert git(destination, "rev-parse", f"refs/tags/loom-evidence/{tip}") == mapping[tip]
    transported = tmp_path / "transported"
    git(tmp_path, "clone", "--no-local", str(destination), str(transported))
    assert git(transported, "show", f"refs/tags/loom-evidence/{tip}:loom-code/file.txt") == "auxiliary evidence"
    assert git(destination, "remote") == ""
    assert report["auxiliary_history"][0]["commit"] == tip
    for invalid in ({"commit": "f" * 40, "citations": ["loom-code/citation.md"]},
                    {"commit": abandoned, "citations": ["loom-code/citation.md"]},
                    {"commit": tip, "citations": ["unrelated.txt"]}):
        target = tmp_path / "rejected"
        with pytest.raises((ValueError, subprocess.CalledProcessError)):
            extraction.extract_repository(source, target, head, extraction.PLUGIN_ROOTS, auxiliary=[invalid])
        assert not target.exists()


def test_referenced_auxiliary_tip_survives_even_without_a_retained_delta(source, tmp_path):
    main = git(source, "branch", "--show-current")
    git(source, "checkout", "-qb", "snapshot-tip")
    (source / "unrelated.txt").write_text("tip identifies the snapshot\n")
    git(source, "commit", "-qam", "Referenced snapshot boundary")
    tip = git(source, "rev-parse", "HEAD")
    git(source, "checkout", "-q", main)
    (source / "loom-code/citation.md").write_text(tip[:8] + "\n")
    git(source, "add", ".")
    git(source, "commit", "-qm", "Record snapshot identity")
    head = git(source, "rev-parse", "HEAD")
    git(source, "update-ref", "refs/remotes/origin/main", head)
    destination = tmp_path / "candidate"
    extraction.extract_repository(source, destination, head, extraction.PLUGIN_ROOTS,
        auxiliary=[{"commit": tip, "citations": ["loom-code/citation.md"]}])
    assert git(destination, "show", f"refs/tags/loom-evidence/{tip}:loom-code/file.txt") == "second"
    assert not (destination / "unrelated.txt").exists()


def test_whole_extraction_ignores_hostile_git_routing(source, tmp_path, monkeypatch):
    head = git(source, "rev-parse", "HEAD")
    git(source, "update-ref", "refs/remotes/origin/main", head)
    decoy = tmp_path / "decoy"
    git(tmp_path, "clone", "--no-local", str(source), str(decoy))
    before = extraction.source_snapshot(source)
    decoy_before = extraction.source_snapshot(decoy)
    sentinel = tmp_path / "hook-fired"
    template = tmp_path / "hostile-template"
    (template / "hooks").mkdir(parents=True)
    hook = template / "hooks/post-checkout"
    hook.write_text(f"#!/bin/sh\ntouch '{sentinel}'\n")
    hook.chmod(0o755)
    global_config = tmp_path / "hostile-config"
    global_config.write_text(f"[core]\n hooksPath = {template / 'hooks'}\n worktree = {decoy}\n")
    hostile = {
        "GIT_DIR": str(decoy / ".git"), "GIT_COMMON_DIR": str(decoy / ".git"),
        "GIT_WORK_TREE": str(decoy), "GIT_INDEX_FILE": str(decoy / ".git/index"),
        "GIT_OBJECT_DIRECTORY": str(decoy / ".git/objects"),
        "GIT_ALTERNATE_OBJECT_DIRECTORIES": str(source / ".git/objects"),
        "GIT_CONFIG_GLOBAL": str(global_config), "GIT_CONFIG_SYSTEM": str(global_config),
        "GIT_CONFIG": str(global_config), "GIT_TEMPLATE_DIR": str(template),
        "GIT_CONFIG_COUNT": "2", "GIT_CONFIG_KEY_0": "core.worktree", "GIT_CONFIG_VALUE_0": str(decoy),
        "GIT_CONFIG_KEY_1": "core.hooksPath", "GIT_CONFIG_VALUE_1": str(template / "hooks"),
        "GIT_CONFIG_PARAMETERS": "'core.worktree'='" + str(decoy) + "'",
    }
    with monkeypatch.context() as environment:
        for key, value in hostile.items():
            environment.setenv(key, value)
        extraction.extract_repository(source, tmp_path / "candidate", head, extraction.PLUGIN_ROOTS)
    assert extraction.source_snapshot(source) == before
    assert extraction.source_snapshot(decoy) == decoy_before
    assert not sentinel.exists()


def test_filter_repo_is_pinned_in_declared_test_environment():
    root = Path(extraction.__file__).parents[1]
    assert "git-filter-repo==2.47.0" in (root / "requirements-dev.txt").read_text()
    assert "git-filter-repo==2.47.0" in (root / "requirements-package-tests.lock").read_text()


def test_historical_probe_imports_in_a_fresh_process(tmp_path):
    bootstrap = Path(extraction.__file__).with_name("loom-repository-bootstrap")
    repo = tmp_path / "repo"
    scripts = repo / "loom-code/scripts"
    scripts.mkdir(parents=True)
    (scripts / "coldread_role_split.py").write_text("")
    (scripts / "_migration_history.py").write_text((bootstrap / "loom-code/scripts/_migration_history.py").read_text())
    evidence = repo / "docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence"
    evidence.mkdir(parents=True)
    (evidence / "fixture-coldread-8.json").write_text("{}")
    probe = evidence / "probes/test_abuse_coldread_branch_end.py"
    probe.parent.mkdir()
    probe.write_text((bootstrap / "docs/loom/2026-09-04-adversary-three-way-attribution-measured/evidence/probes/test_abuse_coldread_branch_end.py.template").read_text())
    result = subprocess.run([os.sys.executable, "-m", "pytest", str(probe), "--collect-only", "-q"],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
