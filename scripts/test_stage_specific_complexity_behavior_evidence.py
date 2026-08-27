"""Require reproducible baseline/candidate evidence for complexity behavior."""

import io
import re
import runpy
import subprocess
import tarfile
import tempfile
from pathlib import Path

import pytest


REPORT = Path(__file__).parents[1] / "docs/loom/dogfood/2026-08-27-stage-specific-complexity-gates.md"
ROOT = Path(__file__).parents[1]
FINGERPRINT = runpy.run_path(
    str(ROOT / "loom-code/scripts/loom_firing_harness.py")
)["_plugin_tree_fingerprint"]
BASELINE_COMMIT = "0a7dcde2"
# The live hard cases observed the instruction surface of `7af88b70`, a commit
# on the pre-rebase branch. The rebase replaced it and no reachable commit
# carries those bytes, so a fresh clone cannot recompute its fingerprints —
# they are recorded here instead. This test still pins the report against a
# silent re-pin; it can no longer re-derive these two numbers from git.
HARD_CASE_BEHAVIOR_FINGERPRINTS = {
    "loom-design": "afa3b1dca93ab1a078cd5ddc495bd03c613da81e645c894625bce753a05e6241",
    "loom-code": "6ce0976774f213d4c6e7d4c60727a2fb6e7f2270edafbdf9c43fd41564c415c5",
}
# Behaviour-bearing files already known to differ between that surface and the
# anchor below. Recorded once, because the diff that produced them is no longer
# computable. Everything after the anchor is still read from git, so a later
# edit cannot reach the report without being named.
RECORDED_POST_HARD_CASE_DELTA = (
    "loom-code/agents/code-reviewer.md",
    "loom-code/skills/requesting-code-review/references/design-evidence.md",
    "loom-code/skills/requesting-code-review/references/implementation-complexity-lens.md",
    "loom-code/skills/writing-plans/SKILL.md",
    "loom-code/skills/writing-plans/references/plan-document-reviewer-prompt.md",
    "loom-code/skills/writing-plans/references/plan-format.md",
    "loom-design/skills/business-value/assets/business-value-template.md",
)
# The round-4 fixes in their merged form. Reachable from every clone that has
# this branch's history, which `7af88b70` was not.
DELTA_ANCHOR_COMMIT = "acd5a846"
REQUIRED_LENS_EVIDENCE = {
    "business-complexity-lens": "live hard case (pre-fix surface; not re-run)",
    "visual-complexity-lens": "live hard case",
    "interaction-complexity-lens": "live hard case",
    "behavioral-complexity-lens": "contract test",
    "architecture-complexity-lens": "live hard case (pre-fix surface; not re-run)",
    "implementation-complexity-lens": "contract test",
}


def _materialize_tracked_file(source: Path, target: Path, git_mode: str) -> None:
    if git_mode == "120000" or source.is_symlink():
        raise AssertionError(f"tracked symlink is not package-safe: {source}")
    if git_mode not in {"100644", "100755"} or not source.is_file():
        raise AssertionError(f"unsupported tracked package entry: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())
    target.chmod(0o755 if git_mode == "100755" else 0o644)


def _normalize_tree_modes(root: Path) -> None:
    root.chmod(0o755)
    for path in root.rglob("*"):
        if path.is_dir():
            path.chmod(0o755)


def _archive_fingerprint(plugin: str, revision: str) -> str:
    archive = subprocess.check_output(
        ["git", "-C", str(ROOT), "archive", "--format=tar", revision, plugin]
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        destination = Path(temp_dir)
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as bundle:
            for member in bundle.getmembers():
                target = (destination / member.name).resolve()
                if not target.is_relative_to(destination.resolve()):
                    raise AssertionError(f"unsafe archive member: {member.name}")
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    source = bundle.extractfile(member)
                    if source is None:
                        raise AssertionError(f"unreadable archive member: {member.name}")
                    target.write_bytes(source.read())
                    target.chmod(0o755 if member.mode & 0o111 else 0o644)
                else:
                    raise AssertionError(f"unsupported archive member: {member.name}")
        _normalize_tree_modes(destination / plugin)
        return FINGERPRINT(destination / plugin)


def _tracked_worktree_fingerprint(plugin: str) -> str:
    tracked = subprocess.check_output(
        ["git", "-C", str(ROOT), "ls-files", "--stage", "-z", "--", plugin]
    ).decode().split("\0")
    with tempfile.TemporaryDirectory() as temp_dir:
        destination = Path(temp_dir) / plugin
        for record in filter(None, tracked):
            metadata, relative = record.split("\t", 1)
            git_mode = metadata.split(" ", 1)[0]
            source = ROOT / relative
            target = Path(temp_dir) / relative
            _materialize_tracked_file(source, target, git_mode)
        _normalize_tree_modes(destination)
        return FINGERPRINT(destination)


def _instruction_surface_delta() -> list[str]:
    """Behaviour-bearing paths that differ between the hard-case surface and now.

    Two segments: the recorded delta up to the anchor, and everything git
    reports since. Only the second half is computable, and it is the half that
    a new edit lands in.
    """
    changed = subprocess.check_output(
        ["git", "-C", str(ROOT), "diff", "--name-only", DELTA_ANCHOR_COMMIT, "--",
         "loom-code/skills", "loom-code/agents",
         "loom-design/skills", "loom-design/agents"]
    ).decode().splitlines()
    return sorted(
        set(RECORDED_POST_HARD_CASE_DELTA)
        | {
            relative
            for relative in changed
            if relative.endswith(".md")
            and not Path(relative).name.startswith(("README", "CHANGELOG"))
        }
    )


def test_report_binds_baseline_and_final_candidate():
    """Bind reported bytes to reconstructible Git inputs.

    Grounding (live CLI help, 2026-08-27): `git archive -h` documents
    `--format <fmt>`, `<tree-ish>`, and optional paths; `git ls-files -h`
    documents `--stage`, `-z`, and path arguments. Those are the exact Git
    surfaces used by the reconstruction helpers above.

    The coverage table is pinned including its caveats: a lane whose governing
    files changed after its live run must say so in the row a reader consults,
    not only in prose further down.
    """
    text = REPORT.read_text(encoding="utf-8")
    flat_text = " ".join(text.split())
    assert "immutable pre-edit snapshot" in text
    assert "base commit `0a7dcde2`" in text
    assert "final cold-install candidate bytes" in text
    for plugin in ("loom-design", "loom-code"):
        baseline_match = re.search(
            rf"{plugin} baseline SHA-256: `([0-9a-f]{{64}})`", text
        )
        assert baseline_match, f"report must record a full {plugin} baseline fingerprint"
        assert baseline_match.group(1) == _archive_fingerprint(plugin, BASELINE_COMMIT)
        assert f"{plugin} candidate SHA-256" in text
        match = re.search(rf"{plugin} candidate SHA-256: `([0-9a-f]{{64}})`", text)
        assert match, f"report must record a full {plugin} candidate fingerprint"
        assert match.group(1) == _tracked_worktree_fingerprint(plugin)
    for case in ("no-upstream", "misleading-upstream", "trivial-exempt", "over-complex"):
        assert f"`{case}`" in text
    coverage_rows = dict(
        re.findall(r"^\| `([^`]+-complexity-lens)` \| ([^|]+?) \| PASS \|$", text, re.MULTILINE)
    )
    assert coverage_rows == REQUIRED_LENS_EVIDENCE
    assert "purpose preservation" in flat_text.lower()
    assert "scope trade-off" in flat_text.lower()
    assert "Pre-existing invariant result: PASS" in text


def test_report_enumerates_any_post_hard_case_instruction_change():
    """A changed instruction surface must be enumerated, never re-hashed away.

    The candidate fingerprint moves for a version bump, so matching it proves
    nothing about behaviour. This test binds the report to the instruction
    bytes the hard cases actually observed: either nothing has moved since, or
    the report names every file that did. The delta since the anchor is read
    from git, so recomputing a hash cannot satisfy it; the two fingerprints
    themselves are compared against the recorded values, because the commit
    that produced them no longer exists in any clone.
    """
    text = REPORT.read_text(encoding="utf-8")
    for plugin, fingerprint in HARD_CASE_BEHAVIOR_FINGERPRINTS.items():
        match = re.search(rf"{plugin} hard-case behavior SHA-256: `([0-9a-f]{{64}})`", text)
        assert match, (
            f"report must record the {plugin} instruction-surface fingerprint the "
            "hard cases ran against"
        )
        assert match.group(1) == fingerprint

    delta = _instruction_surface_delta()
    if not delta:
        return
    assert "## Instruction-surface changes after the hard cases" in text, (
        "the instruction surface moved after the hard cases ran; the report must "
        "carry the delta section rather than restate the old results as current"
    )
    for relative in delta:
        assert relative in text, (
            f"{relative} changed after the hard cases ran and is not named in the "
            "report's delta section"
        )


def test_delta_anchor_commit_is_reachable_from_this_branch():
    """The anchor has to survive a fresh clone, which `7af88b70` did not.

    That commit lived only in local object stores: every developer checkout
    passed while CI, cloning from the remote, died with exit 128 before a
    single assertion ran. Reachability from HEAD is the property that
    difference turns on, so it is asserted rather than assumed.
    """
    probe = subprocess.run(
        ["git", "-C", str(ROOT), "merge-base", "--is-ancestor",
         DELTA_ANCHOR_COMMIT, "HEAD"],
        capture_output=True,
    )
    assert probe.returncode == 0, (
        f"{DELTA_ANCHOR_COMMIT} is not an ancestor of HEAD; a fresh clone of this "
        "branch cannot resolve it, and every git-backed assertion here dies with it"
    )


def test_tracked_copy_rejects_symlinks(tmp_path):
    real_file = tmp_path / "real.txt"
    real_file.write_text("payload", encoding="utf-8")
    symlink = tmp_path / "link.txt"
    symlink.symlink_to(real_file)

    with pytest.raises(AssertionError, match="symlink"):
        _materialize_tracked_file(symlink, tmp_path / "copy.txt", "120000")


def test_fingerprint_directory_modes_are_umask_independent(tmp_path):
    nested = tmp_path / "plugin" / "skills" / "demo"
    nested.mkdir(parents=True)
    for directory in (tmp_path / "plugin", tmp_path / "plugin/skills", nested):
        directory.chmod(0o700)

    _normalize_tree_modes(tmp_path / "plugin")

    for directory in (tmp_path / "plugin", tmp_path / "plugin/skills", nested):
        assert directory.stat().st_mode & 0o777 == 0o755


# Hard-case rows whose governing instruction files changed after the live run.
# Keyed by the row's case label; the value must appear in that row's Result
# column, so the detailed table cannot read as an unqualified PASS while the
# delta section says the lane was not re-run.
_NOT_RERUN_ROWS = {
    "`no-upstream` business burden",
    "`no-upstream` architecture plan",
    "`misleading-upstream` architecture claim",
}
_NOT_RERUN_MARKER = "not re-run after the round-4 fixes"


def test_hard_case_rows_flag_the_lanes_that_were_not_rerun():
    """The detailed results table carries the same caveat as the summary.

    A partial read of an evidence report normally lands on the results table.
    Pinning only the coverage table left three rows reading as confident PASS
    for lanes the report elsewhere admits were not re-verified.
    """
    text = REPORT.read_text(encoding="utf-8")
    rows = {
        line.split("|")[1].strip(): line.split("|")[4].strip()
        for line in text.splitlines()
        if line.startswith("| `") and line.count("|") >= 5
    }
    for case in _NOT_RERUN_ROWS:
        assert case in rows, f"hard-case row {case} is missing from the results table"
        assert _NOT_RERUN_MARKER in rows[case], (
            f"{case} names a lens whose instruction files changed after the live "
            f"run; its Result must say {_NOT_RERUN_MARKER!r}"
        )
