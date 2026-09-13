"""Inventory, extract and verify an isolated local Loom repository.

Paths are a reviewed allowlist, never a keyword-based guess. Directory entries
end in '/'; other entries select exactly one file. History rewriting and all
Git mutations are confined to a newly created destination repository.
"""
from __future__ import annotations

from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import re
import shutil
import subprocess

PLUGIN_ROOTS = ("loom-code/", "loom-design/", "loom-workflow/")
DEFAULT_MANIFEST = Path(__file__).with_name("loom_repository_paths.txt")


def _git(source, *args):
    return subprocess.check_output(
        ["git", "-C", str(source), *args], text=True, encoding="utf-8"
    )


def _validate_manifest(paths):
    if not paths or len(paths) != len(set(paths)):
        raise ValueError("manifest must be nonempty and contain no duplicates")
    for entry in paths:
        path = PurePosixPath(entry)
        if (not entry or entry.startswith(("/", "-", "./"))
                or any(part in ("..", ".git") for part in path.parts)
                or any(char in entry for char in "*?[]\\\x00\n\r")
                or str(path) != entry.rstrip("/")
                or entry in (".", "docs/", "docs/loom/", "scripts/", ".github/", ".github/workflows/")):
            raise ValueError(f"unsafe or overly broad manifest path: {entry!r}")
    return list(paths)


def read_manifest(path=DEFAULT_MANIFEST):
    return _validate_manifest([
        line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ])


def selected(path, manifest):
    return any(path.startswith(entry) if entry.endswith("/") else path == entry
               for entry in manifest)


def validate_retained_paths(paths, manifest):
    _validate_manifest(manifest)
    unexpected = sorted(path for path in paths if not selected(path, manifest))
    if unexpected:
        raise ValueError(f"unclassified retained paths: {unexpected}")


def validate_destination(source, destination):
    destination = Path(destination)
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"destination already exists: {destination}")
    if destination.resolve().is_relative_to(Path(source).resolve()):
        raise ValueError("destination must be outside the source repository")
    return destination.resolve()


def inventory(source, source_ref, manifest, required_paths=(), additional_tips=()):
    """Describe the fixed source tree and every touching commit, including merges.

    The complete reachable population is returned for commit-map validation.
    Comparing merges with each parent catches either side's retained changes.
    Historical-only manifest paths are accepted if Git can prove their history.
    """
    manifest = _validate_manifest(manifest)
    for root in PLUGIN_ROOTS:
        if root not in manifest:
            raise ValueError(f"missing required whole plugin root: {root}")
    commit = _git(source, "rev-parse", "--verify", f"{source_ref}^{{commit}}").strip()
    files = _git(source, "ls-tree", "-r", "--name-only", "-z", commit).split("\0")
    files = sorted(path for path in files if path)
    for path in (*PLUGIN_ROOTS, *required_paths):
        matches = [file for file in files if selected(file, [path])]
        if not matches or any(not selected(file, manifest) for file in matches):
            raise ValueError(f"missing required path coverage: {path}")
    for path in manifest:
        if not any(selected(file, [path]) for file in files):
            historical = _git(source, "log", "-1", "--format=%H", commit, "--", path)
            if not historical.strip():
                raise ValueError(f"declared path absent from source history: {path}")
    all_commits = _git(source, "rev-list", "--reverse", "--topo-order", commit, *additional_tips).splitlines()
    commits = []
    for sha in all_commits:
        changed = sorted(set(filter(None, _git(
            source, "diff-tree", "--root", "-m", "--no-commit-id", "--name-only",
            "--no-renames", "-r", "-z", sha
        ).split("\0"))))
        retained = [path for path in changed if selected(path, manifest)]
        if not retained and sha not in additional_tips:
            continue
        raw = _git(source, "show", "-s", "--format=%an%x00%ae%x00%aI%x00%cn%x00%ce%x00%cI%x00%B", sha)
        values = raw.removesuffix("\n").split("\0", 6)
        metadata = dict(zip(("author_name", "author_email", "author_date",
                             "committer_name", "committer_email", "committer_date", "message"), values))
        commits.append({"old": sha, "mixed": bool(retained) and len(retained) != len(changed),
                        "auxiliary_tip": sha in additional_tips,
                        "retained_paths": retained, **metadata})
    return {"source_commit": commit, "manifest": manifest,
            "files": [path for path in files if selected(path, manifest)],
            "all_commits": all_commits, "commits": commits}


def validate_commit_map(content, all_commits, retained_commits):
    """Reject missing, duplicated, malformed, or silently dropped provenance."""
    lines = content.splitlines()
    if not lines or lines[0].split() != ["old", "new"]:
        raise ValueError("invalid commit-map header")
    mapping = {}
    for line in lines[1:]:
        pair = line.split()
        if len(pair) != 2 or any(not re.fullmatch(r"[0-9a-f]{40}", sha) for sha in pair):
            raise ValueError("invalid commit-map row")
        old, new = pair
        if old in mapping:
            raise ValueError("duplicate commit-map source")
        mapping[old] = new
    if set(mapping) != set(all_commits):
        raise ValueError("commit-map does not cover the complete source population")
    if any(mapping.get(sha, "0" * 40) == "0" * 40 for sha in retained_commits):
        raise ValueError("commit-map dropped a retained commit")
    return mapping


def source_snapshot(source):
    """Record source refs, local configuration, index/worktree state and HEAD."""
    return {"head": _git(source, "rev-parse", "HEAD").strip(),
            "refs": _git(source, "show-ref"),
            "config": _git(source, "config", "--local", "--list"),
            "status": _git(source, "status", "--porcelain=v1", "--untracked-files=all"),
            "diff": _git(source, "diff", "HEAD", "--binary")}


def _tree(source, sha, manifest=None):
    records = _git(source, "ls-tree", "-r", "-z", sha).split("\0")
    return {record.split("\t", 1)[1]: record.split("\t", 1)[0]
            for record in records if record and
            (manifest is None or selected(record.split("\t", 1)[1], manifest))}


def extract_repository(source, destination, source_commit, manifest, source_ref="origin/main", auxiliary=()):
    """Build and verify a fresh local clone; a failed candidate is left for inspection.

    All mutations target the new clone. Unrelated-only commits are pruned, but
    degenerate merges remain to preserve selected ancestry. Verification rejects
    any touching commit that the filter unexpectedly drops.
    """
    source = Path(source).resolve()
    destination = validate_destination(source, destination)
    if _git(source, "rev-parse", "--is-shallow-repository").strip() != "false":
        raise ValueError("shallow source cannot provide complete development history")
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("source commit must be a full fixed SHA")
    actual = _git(source, "rev-parse", "--verify", f"{source_ref}^{{commit}}").strip()
    if actual != source_commit:
        raise ValueError("source ref does not match the fixed source commit")
    if not shutil.which("git-filter-repo"):
        raise ValueError("git-filter-repo is required")
    auxiliary_tips = []
    for entry in auxiliary:
        tip = entry["commit"]
        if not re.fullmatch(r"[0-9a-f]{40}", tip) or tip in auxiliary_tips:
            raise ValueError("auxiliary tips must be unique full commit IDs")
        if _git(source, "rev-parse", "--verify", f"{tip}^{{commit}}").strip() != tip:
            raise ValueError("auxiliary tip is not an existing commit")
        if not entry.get("citations"):
            raise ValueError("auxiliary tip requires a current retained citation")
        for citation in entry["citations"]:
            validate_retained_paths([citation], manifest)
            cited_text = _git(source, "show", f"{source_commit}:{citation}")
            cited_ids = re.findall(r"(?<![0-9a-f])[0-9a-f]{7,40}(?![0-9a-f])", cited_text)
            candidates = [value for value in cited_ids if tip.startswith(value)]
            if not candidates or not any(
                _git(source, "rev-parse", "--verify", f"{value}^{{commit}}").strip() == tip
                for value in candidates
            ):
                raise ValueError(f"auxiliary tip is not justified by current citation: {tip}")
        auxiliary_tips.append(tip)
    before = source_snapshot(source)
    evidence = inventory(source, source_commit, manifest, additional_tips=auxiliary_tips)
    subprocess.run(["git", "clone", "--no-local", "--no-checkout", str(source), str(destination)], check=True)
    # Fetch a fixed object directly: the source worktree's local main can lag
    # origin/main. This creates no source ref and never writes its configuration.
    _git(destination, "fetch", "--no-tags", str(source), source_commit)
    _git(destination, "checkout", "-B", "main", source_commit)
    _git(destination, "remote", "remove", "origin")
    for ref in _git(destination, "for-each-ref", "--format=%(refname)").splitlines():
        if ref != "refs/heads/main":
            _git(destination, "update-ref", "-d", ref)
    for tip in auxiliary_tips:
        _git(destination, "fetch", "--no-tags", str(source), tip)
        _git(destination, "update-ref", f"refs/archive/loom-evidence/{tip}", tip)
    # filter-repo freshness detection cannot accept the pinning checkout above.
    # --force is restricted to this newly created destination, never the source.
    retained_file = destination / ".git/loom-retained-commits.txt"
    retained_file.write_text("\n".join(entry["old"] for entry in evidence["commits"]), encoding="ascii")
    callback = (
        "global loom_retained_ids\n"
        "if 'loom_retained_ids' not in globals():\n"
        "    with open('.git/loom-retained-commits.txt', 'rb') as stream:\n"
        "        loom_retained_ids = set(stream.read().splitlines())\n"
        "if commit.original_id not in loom_retained_ids:\n"
        "    commit.skip(new_id=commit.first_parent())\n"
    )
    arguments = ["filter-repo", "--force", "--prune-empty", "never",
                 "--prune-degenerate", "never", "--preserve-commit-hashes",
                 "--commit-callback", callback]
    for path in manifest:
        arguments.extend(["--path", path])
    _git(destination, *arguments)
    raw_map_text = (destination / ".git/filter-repo/commit-map").read_text(encoding="utf-8")
    # filter-repo omits callback-skipped IDs instead of emitting zero rows.
    # Add only IDs independently classified as unrelated before rewriting;
    # the original tool output is preserved alongside the complete map.
    mapped_ids = {line.split()[0] for line in raw_map_text.splitlines()[1:]}
    retained_ids = {entry["old"] for entry in evidence["commits"]}
    omitted_unrelated = set(evidence["all_commits"]) - retained_ids - mapped_ids
    map_text = raw_map_text + "".join(f"{old} {'0' * 40}\n" for old in sorted(omitted_unrelated))
    mapping = validate_commit_map(map_text, evidence["all_commits"],
                                  [entry["old"] for entry in evidence["commits"]] + auxiliary_tips)
    for tip in auxiliary_tips:
        if _git(destination, "rev-parse", f"refs/archive/loom-evidence/{tip}").strip() != mapping[tip]:
            raise ValueError(f"auxiliary archive ref does not match its mapping: {tip}")
    verified = 0
    for entry in evidence["commits"]:
        old, new = entry["old"], mapping[entry["old"]]
        expected = _tree(source, old, manifest)
        actual_tree = _tree(destination, new)
        validate_retained_paths(actual_tree, manifest)
        if actual_tree != expected:
            raise ValueError(f"retained tree differs at {old}")
        metadata_format = "--format=%an%x00%ae%x00%aI%x00%cn%x00%ce%x00%cI%x00%B"
        if _git(source, "show", "-s", metadata_format, old) != _git(destination, "show", "-s", metadata_format, new):
            raise ValueError(f"commit metadata differs at {old}")
        verified += 1
    if _tree(destination, "HEAD") != _tree(source, source_commit, manifest):
        raise ValueError("candidate current tree differs from selected source files")
    if _git(destination, "remote").strip():
        raise ValueError("candidate must not have a remote")
    if source_snapshot(source) != before:
        raise ValueError("source changed during extraction")
    report = {"source_commit": source_commit, "source_ref": source_ref,
              "filter_repo_version": _git(destination, "filter-repo", "--version").strip(),
              "auxiliary_history": list(auxiliary),
              "primary_source_commits": len(_git(source, "rev-list", source_commit).splitlines()),
              "filtered_commit": _git(destination, "rev-parse", "HEAD").strip(),
              "source_commits": len(evidence["all_commits"]),
              "verified_commits": verified,
              "mixed_commits": sum(entry["mixed"] for entry in evidence["commits"]),
              "selected_files": len(evidence["files"]),
              "manifest": list(manifest),
              "commit_map_sha256": hashlib.sha256(map_text.encode()).hexdigest(),
              "source_unchanged": True, "destination_remotes": [],
              "history_policy": "retain reviewed-path changes and explicitly cited evidence tips; preserve their merges and messages; discard unrelated commits"}
    migration = destination / "docs/migration"
    migration.mkdir(parents=True, exist_ok=True)
    (migration / "commit-map.tsv").write_text(map_text, encoding="utf-8")
    (migration / "filter-repo-commit-map.tsv").write_text(raw_map_text, encoding="utf-8")
    (migration / "extraction.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    bootstrap = Path(__file__).with_name("loom-repository-bootstrap")
    bootstrap_paths = []
    for template in sorted(bootstrap.rglob("*")):
        if template.is_file():
            relative = template.relative_to(bootstrap)
            if relative.suffix == ".template":
                relative = relative.with_suffix("")
            if ".git" in relative.parts or template.is_symlink():
                raise ValueError(f"unsafe bootstrap template: {relative}")
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(template, target)
            bootstrap_paths.append(str(relative))
    _git(destination, "add", "docs/migration/commit-map.tsv", "docs/migration/filter-repo-commit-map.tsv", "docs/migration/extraction.json")
    if bootstrap_paths:
        _git(destination, "add", "--", *bootstrap_paths)
    _git(destination, "-c", "user.name=Loom repository migration", "-c", "user.email=loom-migration@example.invalid",
         "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", "commit", "-m",
         "chore: preserve source history map and extraction evidence")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-ref", default="origin/main")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--auxiliary-manifest", type=Path,
                        default=Path(__file__).with_name("loom-repository-bootstrap") / "docs/migration/auxiliary-history.json")
    args = parser.parse_args()
    print(json.dumps(extract_repository(args.source, args.destination, args.source_commit,
                                       read_manifest(args.manifest), args.source_ref,
                                       auxiliary=json.loads(args.auxiliary_manifest.read_text())), indent=2))


if __name__ == "__main__":
    main()
