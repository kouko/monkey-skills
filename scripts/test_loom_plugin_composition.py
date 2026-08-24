"""Composition contract for independently installed loom plugins.

This deliberately complements the standalone-layout probe: it checks only the
public seam between the two packages, not either package's manifest inventory.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import check_plugin_boundaries


REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_LOOM_WORKFLOW_SKILLS = {
    "brief-before-asking",
    "complexity-critique",
    "git-memory",
    "proposal-critique",
}
ACTIVE_SURFACE_ROOTS = ("loom-code", "loom-design", "loom-workflow")
ACTIVE_SURFACE_DIRECTORIES = {"hooks", "scripts", "skills", "tests"}
ACTIVE_SURFACE_ROOT_FILES = {
    "PRODUCT-SPEC.md",
    "README.ja.md",
    "README.md",
    "README.zh-TW.md",
    "ROADMAP.md",
    "TECH-SPEC.md",
}
ACTIVE_SURFACE_SUFFIXES = {".json", ".jsonl", ".md", ".py", ".sh", ".toml", ".yaml", ".yml"}
EXTERNAL_ACTIVE_CONSUMERS = (
    "ATTRIBUTION.md",
    "dbt-wiki/skills/using-dbt-wiki/SKILL.md",
    "deconstruct-toolkit/docs/adr/0002-strict-skill-self-containment.md",
    "deconstruct-toolkit/docs/design-proposal.md",
    "deconstruct-toolkit/README.ja.md",
    "deconstruct-toolkit/README.md",
    "deconstruct-toolkit/README.zh-TW.md",
    "domain-teams/skills/code-team/SKILL.md",
    "domain-teams/skills/code-team/standards/mindset-extension-standard.md",
    "domain-teams/skills/skill-team/standards/file-conventions.md",
    "repo-wiki/README.ja.md",
    "repo-wiki/README.md",
    "repo-wiki/README.zh-TW.md",
    "translation-toolkit/scripts/README.md",
    "translation-toolkit/skills/using-translation-toolkit/references/claude-code-tools.md",
)
EXTERNAL_ACTIVE_CONSUMER_DIRECTORIES = ("skill-dev-toolkit/skills",)


def _copy_plugin(source_name: str, destination: Path) -> Path:
    source = REPO_ROOT / source_name
    shutil.copytree(source, destination)
    return destination


def _git(repo: Path, *args: str) -> str:
    """Run a successful git command in an isolated consumer fixture."""
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _isolated_review_consumer(tmp_path: Path) -> Path:
    """Build a fresh consumer branch whose base is a live local remote."""
    upstream = tmp_path / "upstream"
    upstream.mkdir()
    _git(upstream, "init", "-q", "-b", "main")
    _git(upstream, "config", "user.email", "review@example.test")
    _git(upstream, "config", "user.name", "Review Fixture")
    (upstream / "README.md").write_text("# Consumer\n", encoding="utf-8")
    _git(upstream, "add", "README.md")
    _git(upstream, "commit", "-qm", "base")

    consumer = tmp_path / "consumer-project"
    subprocess.run(
        ["git", "clone", "-q", str(upstream), str(consumer)],
        check=True,
        capture_output=True,
        text=True,
    )
    _git(consumer, "config", "user.email", "review@example.test")
    _git(consumer, "config", "user.name", "Review Fixture")
    _git(consumer, "checkout", "-qb", "review-flow")
    (consumer / "feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    (consumer / "CONTRACT.md").write_text("# Contract\n", encoding="utf-8")
    _git(consumer, "add", "feature.py", "CONTRACT.md")
    _git(consumer, "commit", "-qm", "reviewable mixed change")
    return consumer


def _loom_artifacts(markdown: str) -> set[str]:
    """Return the consumer-project artifact names declared in code spans."""

    return {
        span.rstrip("/")
        for span in re.findall(r"`([^`\n]*docs/loom[^`\n]*)`", markdown)
    }


def _resolve_qualified_skill(qualified_name: str, plugin_roots: tuple[Path, ...]) -> Path | None:
    plugin_name, separator, skill_name = qualified_name.partition(":")
    if not separator or not plugin_name or not skill_name:
        return None
    for plugin_root in plugin_roots:
        manifest_path = plugin_root / ".claude-plugin/plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("name") == plugin_name:
            skill_path = plugin_root / "skills" / skill_name / "SKILL.md"
            return skill_path if skill_path.is_file() else None
    return None


def _active_plugin_surfaces() -> tuple[Path, ...]:
    """Return active plugin and external-consumer surfaces, excluding history."""

    surfaces = []
    for plugin_name in ACTIVE_SURFACE_ROOTS:
        plugin_root = REPO_ROOT / plugin_name
        for path in plugin_root.rglob("*"):
            if (
                not path.is_file()
                or path.name.startswith("CHANGELOG")
                or path.suffix not in ACTIVE_SURFACE_SUFFIXES
            ):
                continue
            relative = path.relative_to(plugin_root)
            if relative.name in ACTIVE_SURFACE_ROOT_FILES or (
                relative.parts and relative.parts[0] in ACTIVE_SURFACE_DIRECTORIES
            ):
                surfaces.append(path)
    external_surfaces = [REPO_ROOT / path for path in EXTERNAL_ACTIVE_CONSUMERS]
    for directory in EXTERNAL_ACTIVE_CONSUMER_DIRECTORIES:
        external_surfaces.extend(
            path
            for path in (REPO_ROOT / directory).rglob("*")
            if path.is_file() and path.suffix in ACTIVE_SURFACE_SUFFIXES
        )
    return tuple(surfaces + external_surfaces)


def test_plugins_compose_only_through_public_skills_and_artifacts(tmp_path: Path) -> None:
    design_root = _copy_plugin(
        "loom-design", tmp_path / "design-host" / "extensions" / "design-bundle"
    )
    code_root = _copy_plugin(
        "loom-code", tmp_path / "code-host" / "plugins" / "code-bundle"
    )

    # The installs intentionally have neither a shared parent package directory
    # nor their repository names.  A valid composition therefore cannot depend
    # on resolving ../loom-code (or an absolute sibling-plugin internal path).
    assert design_root.parent.parent != code_root.parent.parent
    design_router_path = design_root / "skills/using-loom-design/SKILL.md"
    design_pipeline_path = design_root / "skills/using-loom-pipeline/SKILL.md"
    design_spec_path = design_root / "skills/spec-expansion/SKILL.md"
    code_planner_path = code_root / "skills/writing-plans/SKILL.md"
    design_router = design_router_path.read_text()
    design_pipeline = design_pipeline_path.read_text()
    handoff = "loom-code:using-loom-code"
    assert f"`{handoff}`" in design_router
    assert f"`{handoff}`" in design_pipeline

    code_manifest = json.loads(
        (code_root / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
    )
    assert code_manifest["name"] == "loom-code"
    installed_roots = (design_root, code_root)
    resolved_handoff = _resolve_qualified_skill(handoff, installed_roots)
    assert resolved_handoff == code_root / "skills/using-loom-code/SKILL.md"

    # Mutation probe: the public name must stop resolving when its exported
    # skill disappears; mere presence of the handoff string is insufficient.
    hidden_skill = resolved_handoff.with_suffix(".md.hidden")
    resolved_handoff.rename(hidden_skill)
    try:
        assert _resolve_qualified_skill(handoff, installed_roots) is None
    finally:
        hidden_skill.rename(resolved_handoff)

    design_spec = design_spec_path.read_text()
    code_planner = code_planner_path.read_text()
    shared_artifacts = _loom_artifacts(design_spec) & _loom_artifacts(code_planner)

    # The producer and consumer meet in the target project's named change
    # folder.  Plugin source paths are intentionally absent from this seam.
    assert shared_artifacts == {"docs/loom/<change-id>"}
    assert "emitted by `loom-design:spec-expansion`" in code_planner
    assert not any(
        re.search(r"loom-(?:code|design)/(?:hooks|skills|scripts)/", artifact)
        for artifact in shared_artifacts
    )

    violations = {
        plugin_root: check_plugin_boundaries.find_boundary_violations(plugin_root)
        for plugin_root in (design_root, code_root)
    }
    assert not any(violations.values()), violations


def test_isolated_consumer_review_primitives_are_sha_bound_end_to_end(
    tmp_path: Path,
) -> None:
    """A copied plugin keeps every executable review primitive on one SHA.

    This is deliberately an installed-plugin test rather than an import of
    repository modules: the consumer has no ``loom-code/`` directory and the
    bundle name carries no cache-layout signal to guess from.
    """
    installed_root = _copy_plugin(
        "loom-code", tmp_path / "host-install" / "review-bundle-983"
    )
    consumer = _isolated_review_consumer(tmp_path)
    assert not (consumer / "loom-code").exists()

    context_result = subprocess.run(
        [
            sys.executable,
            str(installed_root / "scripts" / "review_context.py"),
            "--repo",
            str(consumer),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    packet = json.loads(context_result.stdout)
    reviewed_sha = _git(consumer, "rev-parse", "HEAD")
    assert packet["target_repo"] == str(consumer.resolve())
    assert packet["reviewed_sha"] == reviewed_sha
    assert packet["resources"]
    for resource in packet["resources"].values():
        assert Path(resource).is_relative_to(installed_root)

    scope_result = subprocess.run(
        [
            sys.executable,
            packet["resources"]["review_scope"],
            "--repo",
            packet["target_repo"],
            "--reviewed-sha",
            packet["reviewed_sha"],
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert set(scope_result.stdout.splitlines()) == {"CONTRACT.md", "feature.py"}

    # Deliberately poison only the mutable worktree after packet creation.
    # The ordinary mode must see the bad citation, while the packet mode must
    # still read the committed snapshot and produce a different result.
    contract = consumer / "CONTRACT.md"
    contract.write_text(
        "# Contract\n\nBad mutable citation: `feature.py:999`\n",
        encoding="utf-8",
    )
    mutable_citation_result = subprocess.run(
        [
            sys.executable,
            packet["resources"]["doc_citation_checker"],
            str(contract),
            "--repo-root",
            packet["target_repo"],
        ],
        capture_output=True,
        text=True,
    )
    assert mutable_citation_result.returncode == 1
    assert "line 999 exceeds file length" in mutable_citation_result.stdout

    # Citation checking executes from the packet-approved installed resource,
    # and reads the committed document snapshot rather than this worktree.
    citation_result = subprocess.run(
        [
            sys.executable,
            packet["resources"]["doc_citation_checker"],
            str(contract),
            "--repo-root",
            packet["target_repo"],
            "--reviewed-sha",
            packet["reviewed_sha"],
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "checked 0 / unchecked 0 / findings 0" in citation_result.stdout

    marker = Path(packet["resources"]["gate_markers"])
    verdict = tmp_path / "terminal-verdict.md"
    marker_path = consumer / ".git" / "loom" / "review-pass.json"

    # A syntactically valid verdict for another commit must not authorize the
    # packet commit, and it must leave no marker behind.
    verdict.write_text(
        "\n".join(
            (
                "standards_version: 2026-08",
                "reviewed_sha: " + "0" * 40,
                "verdict: PASS",
                "dimension_scores:",
                "  correctness: 5",
                "findings: []",
                "",
            )
        ),
        encoding="utf-8",
    )
    mismatch = subprocess.run(
        [
            sys.executable,
            str(marker),
            "review-pass",
            "--repo",
            packet["target_repo"],
            "--verdict-file",
            str(verdict),
            "--expected-head",
            packet["reviewed_sha"],
        ],
        capture_output=True,
        text=True,
    )
    assert mismatch.returncode != 0
    assert not marker_path.exists()

    # A valid terminal verdict for the exact packet commit is mintable.
    verdict.write_text(
        verdict.read_text(encoding="utf-8").replace("0" * 40, reviewed_sha),
        encoding="utf-8",
    )
    current = subprocess.run(
        [
            sys.executable,
            str(marker),
            "review-pass",
            "--repo",
            packet["target_repo"],
            "--verdict-file",
            str(verdict),
            "--expected-head",
            packet["reviewed_sha"],
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(marker_path) in current.stdout
    assert json.loads(marker_path.read_text(encoding="utf-8"))["head_sha"] == reviewed_sha

    # HEAD drift after packet creation is also a refusal; an old verdict never
    # authorizes a later commit merely because both are otherwise valid.
    (consumer / "later.md").write_text("later\n", encoding="utf-8")
    _git(consumer, "add", "later.md")
    _git(consumer, "commit", "-qm", "later commit")
    marker_path.unlink()
    stale = subprocess.run(
        [
            sys.executable,
            str(marker),
            "review-pass",
            "--repo",
            packet["target_repo"],
            "--verdict-file",
            str(verdict),
            "--expected-head",
            packet["reviewed_sha"],
        ],
        capture_output=True,
        text=True,
    )
    assert stale.returncode != 0
    assert not marker_path.exists()

    # The code station's record-only route intentionally has no reviewer
    # verdict, but it still must bind its continuity marker to a fresh packet.
    _git(consumer, "reset", "--hard", "origin/main")
    record = consumer / "docs" / "review-record.md"
    record.parent.mkdir()
    record.write_text("# Review record\n", encoding="utf-8")
    _git(consumer, "add", "docs/review-record.md")
    _git(consumer, "commit", "-qm", "record-only change")
    record_packet = json.loads(
        subprocess.run(
            [
                sys.executable,
                str(installed_root / "scripts" / "review_context.py"),
                "--repo",
                str(consumer),
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    )
    record_marker = Path(record_packet["resources"]["gate_markers"])
    record_mint = subprocess.run(
        [
            sys.executable,
            str(record_marker),
            "mint",
            "--repo",
            record_packet["target_repo"],
            "--expected-head",
            record_packet["reviewed_sha"],
            "--review-na-record-only",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert str(marker_path) in record_mint.stdout
    assert json.loads(marker_path.read_text(encoding="utf-8"))["head_sha"] == record_packet[
        "reviewed_sha"
    ]


def test_loom_workflow_hard_cut_is_the_only_runtime_dependency_namespace() -> None:
    """The renamed workflow plugin must be installable without its old identity."""

    marketplace = json.loads(
        (REPO_ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
    )
    marketplace_names = [plugin["name"] for plugin in marketplace["plugins"]]
    assert len(marketplace_names) == len(set(marketplace_names))
    marketplace_plugins = dict(zip(marketplace_names, marketplace["plugins"]))
    workflow_entry = marketplace_plugins["loom-workflow"]
    assert workflow_entry["source"] == "./loom-workflow/"
    assert "dev-workflow" not in marketplace_plugins

    workflow_root = REPO_ROOT / workflow_entry["source"]
    assert workflow_root.is_dir()
    claude_manifest = json.loads(
        (workflow_root / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
    )
    codex_manifest = json.loads(
        (workflow_root / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
    )
    assert claude_manifest["name"] == "loom-workflow"
    assert codex_manifest["name"] == "loom-workflow"
    for field in (
        "name",
        "version",
        "description",
        "author",
        "homepage",
        "repository",
        "license",
        "keywords",
    ):
        assert codex_manifest[field] == claude_manifest[field]
    assert claude_manifest["name"] == workflow_entry["name"]
    assert workflow_root.name == claude_manifest["name"]
    for skill_name in REQUIRED_LOOM_WORKFLOW_SKILLS:
        assert (workflow_root / "skills" / skill_name / "SKILL.md").is_file()

    # Scan active installed surfaces, including tests and tool scripts because
    # their path/name contracts are invoked after installation. Historical docs,
    # plans, research, archives, and changelogs are intentionally excluded.
    runtime_skills = _active_plugin_surfaces()
    loom_workflow_names = set()
    for skill in runtime_skills:
        source = skill.read_text(encoding="utf-8")
        assert "dev-workflow:" not in source, skill
        assert "dev-workflow/" not in source, skill
        loom_workflow_names.update(re.findall(r"loom-workflow:([a-z0-9-]+)", source))
    assert REQUIRED_LOOM_WORKFLOW_SKILLS <= loom_workflow_names
