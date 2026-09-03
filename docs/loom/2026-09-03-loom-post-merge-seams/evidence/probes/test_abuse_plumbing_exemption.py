"""Adversarial probes for REQ-3 / Design decision "Content-bound plumbing
exemption" (docs/loom/2026-09-03-loom-post-merge-seams/spec.md), written
BEFORE task W0-05 implements the exemption in
`loom_checker.py::check_dispatch_covers_tasks` / `commit_paths` /
`_is_host_plumbing`.

Today `push.dispatch-covers-tasks` has no exemption for `.codex/hooks/` at
all -- every plumbing path is typed `gate` by the `**/hooks/**` manifest
rule and therefore owes a `Task:` trailer like any other gate-typed change
(loom-code/scripts/loom_checker.py:2610). So every case below already
BLOCKs today except case 1 (the genuine refresh), which the spec says
should PASS once the exemption exists -- that one is the RED the
implementer turns green. Cases 2-10 assert today's BLOCK and must keep
blocking after the exemption lands (they are the abuse/boundary cases the
exemption must not open up).

Each fixture builds on `test_loom_checker_push.py`'s real-git-repo harness
(imported, not duplicated) and calls `codex_scaffold.scaffold()` from THIS
repo's `loom-code/scripts/` to produce a genuine copy -- the canonical the
spec's exemption compares against is this running tree.
"""
from __future__ import annotations

import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[5] / "loom-code" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import codex_scaffold  # noqa: E402  (local import: needs SCRIPTS_DIR on sys.path)
from test_loom_checker_push import (  # noqa: E402
    REVIEW,
    build_repo,
    git,
    review_body,
    run_checker,
    write_review,
)

CHECKER = SCRIPTS_DIR / "loom_checker.py"

RULE = "push.dispatch-covers-tasks"


def blocked_rules(result: subprocess.CompletedProcess) -> set[str]:
    return {
        line.split(":", 1)[0].removeprefix("BLOCK ").strip()
        for line in result.stderr.splitlines()
        if line.startswith("BLOCK ")
    }


def _plumbing_commit(repo: Path, *, trailer: bool, mutate=None,
                      msg: str = "chore(loom): scaffold hooks") -> str:
    """Undo the review-only HEAD `build_repo` left behind, scaffold a
    genuine `.codex/hooks/` copy from THIS repo's tree, optionally mutate
    it, commit (with or without a `Task:` trailer), rebuild review.json so
    `reviewed_sha` names the new commit, and re-commit the review-only
    HEAD on top. Returns the new commit's sha (HEAD^ after this call)."""
    git(repo, "reset", "-q", "--soft", "HEAD~1")
    codex_scaffold.scaffold(repo)
    if mutate is not None:
        mutate(repo)
    full_msg = msg + ("\n\nTask: T1" if trailer else "")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", full_msg)
    new_sha = git(repo, "rev-parse", "HEAD")
    write_review(repo, review_body(new_sha))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")
    return new_sha


def _bootstrap_scaffold(repo: Path) -> None:
    """An already-scaffolded install, one version behind (out of scope:
    REQ-3's stated residual is the FIRST-contact scaffold commit's own
    trailer duty, `write-plan` step 0b -- not this rule). Stamped with a
    decoy version, never this repo's own, so the SUBSEQUENT genuine
    refresh (case 1) has real bytes to change under `.codex/hooks/` --
    the way an actual plugin version bump does -- without writing to this
    repo's own `plugin.json`. `.codex/hooks.json` and `.gitignore` are
    version-independent, so they land here once and the later refresh
    never touches them again (both outside HOST_PLUMBING_FILES, so if the
    refresh DID touch them it would rightly still owe a trailer)."""
    git(repo, "reset", "-q", "--soft", "HEAD~1")
    original = codex_scaffold.plugin_version
    codex_scaffold.plugin_version = lambda: "0.0.1-bootstrap"
    try:
        codex_scaffold.scaffold(repo)
    finally:
        codex_scaffold.plugin_version = original
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "chore: bootstrap scaffold\n\nTask: T1")
    new_sha = git(repo, "rev-parse", "HEAD")
    write_review(repo, review_body(new_sha))
    git(repo, "add", REVIEW)
    git(repo, "commit", "-q", "-m", "chore(loom): checkpoint review")


def _run_from_copy(repo: Path) -> subprocess.CompletedProcess:
    """Invoke the `.codex/hooks/` copy itself, not the canonical -- case 9:
    Codex has no external canonical to compare against, so no exemption
    ever applies there."""
    copy = repo / ".codex" / "hooks" / "loom_checker.py"
    return subprocess.run(
        [sys.executable, str(copy), "push"],
        capture_output=True, text=True, cwd=str(repo),
    )


# --- case 1: genuine refresh, no trailer -----------------------------------


def test_a_genuine_scaffold_refresh_with_no_trailer_is_exempt(tmp_path: Path) -> None:
    """Expected per spec: PASS. W0-05 landed the content-bound plumbing
    exemption in check_dispatch_covers_tasks/commit_paths/_is_host_plumbing
    (REQ-3), so this genuine refresh no longer owes a trailer."""
    repo = build_repo(tmp_path)
    _bootstrap_scaffold(repo)
    _plumbing_commit(repo, trailer=False)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, (
        "expected the genuine scaffold refresh to be exempt from trailer "
        f"duty (REQ-3); checker said: {result.stderr}"
    )


# --- case 2: one byte altered in the checker copy --------------------------


def test_an_altered_checker_copy_byte_is_blocked(tmp_path: Path) -> None:
    """Expected per spec: BLOCK (blob mismatch against the canonical)."""
    def mutate(repo: Path) -> None:
        path = repo / ".codex" / "hooks" / "loom_checker.py"
        path.write_text(path.read_text(encoding="utf-8") + "# tampered\n", encoding="utf-8")

    repo = build_repo(tmp_path)
    _plumbing_commit(repo, trailer=False, mutate=mutate)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert RULE in blocked_rules(result)


# --- case 3: extra file under contract/ -------------------------------------


def test_an_extra_contract_file_is_blocked(tmp_path: Path) -> None:
    """Expected per spec: BLOCK (a plumbing path with no canonical
    counterpart fails the comparison)."""
    def mutate(repo: Path) -> None:
        extra = repo / ".codex" / "hooks" / "contract" / "extra.yaml"
        extra.write_text("bogus: true\n", encoding="utf-8")

    repo = build_repo(tmp_path)
    _plumbing_commit(repo, trailer=False, mutate=mutate)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert RULE in blocked_rules(result)


# --- case 4: git_exec.py deleted --------------------------------------------


def test_a_deleted_sibling_module_is_blocked(tmp_path: Path) -> None:
    """Expected per spec: BLOCK (a deleted entry has no blob at the commit
    and fails the comparison like any other mismatch)."""
    def mutate(repo: Path) -> None:
        (repo / ".codex" / "hooks" / "git_exec.py").unlink()

    repo = build_repo(tmp_path)
    _plumbing_commit(repo, trailer=False, mutate=mutate)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert RULE in blocked_rules(result)


# --- case 5: mode-only change -----------------------------------------------


def test_a_mode_only_change_is_blocked(tmp_path: Path) -> None:
    """Expected per spec: BLOCK (blob AND mode must match; a mode-only
    change fails like a content change)."""
    def mutate(repo: Path) -> None:
        path = repo / ".codex" / "hooks" / "contract" / "manifest.yaml"
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    repo = build_repo(tmp_path)
    _plumbing_commit(repo, trailer=False, mutate=mutate)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert RULE in blocked_rules(result)


# --- case 6: checker copy replaced by a symlink -----------------------------


def test_a_symlinked_checker_copy_is_blocked(tmp_path: Path) -> None:
    """Expected per spec: BLOCK (mode 120000 is never exempt, whatever it
    points at)."""
    def mutate(repo: Path) -> None:
        path = repo / ".codex" / "hooks" / "loom_checker.py"
        path.unlink()
        os.symlink(str(CHECKER), str(path))

    repo = build_repo(tmp_path)
    _plumbing_commit(repo, trailer=False, mutate=mutate)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert RULE in blocked_rules(result)


# --- case 7: stamp version changed, content otherwise identical ------------


def test_a_changed_stamp_version_is_blocked(tmp_path: Path) -> None:
    """Expected per spec: BLOCK (the stamp names another version than the
    running checker's own; fails before any blob is even read)."""
    def mutate(repo: Path) -> None:
        path = repo / ".codex" / "hooks" / "loom_checker.py"
        text = path.read_text(encoding="utf-8")
        stamped = text.replace(
            codex_scaffold.stamp_line(codex_scaffold.plugin_version()),
            codex_scaffold.stamp_line("0.0.1-decoy"),
            1,
        )
        assert stamped != text, "the stamp line must actually be present to mutate"
        path.write_text(stamped, encoding="utf-8")

    repo = build_repo(tmp_path)
    _plumbing_commit(repo, trailer=False, mutate=mutate)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert RULE in blocked_rules(result)


# --- case 8: shim command string changed ------------------------------------


def test_an_altered_shim_command_is_blocked(tmp_path: Path) -> None:
    """Expected per spec: BLOCK (`.codex/hooks/loom-checker` must equal
    the rendered SHIM_TEMPLATE for that version, byte for byte)."""
    def mutate(repo: Path) -> None:
        path = repo / ".codex" / "hooks" / "loom-checker"
        text = path.read_text(encoding="utf-8")
        altered = text.replace(
            "exec python3 {checker} push --hook".format(checker=codex_scaffold.CHECKER_COPY),
            "exec python3 {checker} push --hook --extra-flag".format(
                checker=codex_scaffold.CHECKER_COPY
            ),
            1,
        )
        assert altered != text, "the exec line must actually be present to mutate"
        path.write_text(altered, encoding="utf-8")

    repo = build_repo(tmp_path)
    _plumbing_commit(repo, trailer=False, mutate=mutate)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert RULE in blocked_rules(result)


# --- case 9: run FROM the copy (Codex has no canonical) --------------------


def test_running_the_copy_itself_is_never_exempt(tmp_path: Path) -> None:
    """Expected per spec: BLOCK. When the checker doing the push IS the
    `.codex/hooks/` copy there is no external canonical to compare against
    and no exemption applies -- verify the copy actually runs standalone
    (it imports git_exec.py and reads contract/manifest.yaml, both of
    which the scaffold ships beside it) and still blocks."""
    repo = build_repo(tmp_path)
    _plumbing_commit(repo, trailer=False)
    result = _run_from_copy(repo)
    assert result.returncode in (1, 2), (
        f"the copy did not even run as a checker: {result.stderr or result.stdout}"
    )
    assert RULE in blocked_rules(result), (
        "the copy exempted its own trailer duty with no canonical to check "
        f"against: {result.stderr}"
    )


# --- case 10: a plumbing-looking path outside the exempt set ---------------


def test_an_unlisted_plumbing_path_is_never_exempt(tmp_path: Path) -> None:
    """Expected per spec: BLOCK. `.codex/hooks/other-hook.sh` is not in
    HOST_PLUMBING_FILES and not under HOST_PLUMBING_DIR_PREFIX
    (`.codex/hooks/contract/`) -- it is gate work like any other hook
    script an adopting repo keeps in that directory (loom_checker.py:427:
    "an adopting repo may keep its own gate scripts there too")."""
    def mutate(repo: Path) -> None:
        other = repo / ".codex" / "hooks" / "other-hook.sh"
        other.write_text("#!/usr/bin/env bash\necho hi\n", encoding="utf-8")

    repo = build_repo(tmp_path)
    _plumbing_commit(repo, trailer=False, mutate=mutate)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert RULE in blocked_rules(result)


# --- case 11: extra probe -- the marker file mutated ------------------------


def test_a_forced_hook_fired_marker_commit_is_blocked(tmp_path: Path) -> None:
    """`.loom-hook-fired` is explicitly ignored by the exemption (spec
    Design decision) and gitignored by the scaffold itself, so it never
    appears in a genuine refresh's diff -- forcing it into the commit
    anyway (`git add -f`) makes this a hostile input, not a genuine
    refresh, and case 1's EXPECTED-RED-UNTIL-W0-05 status does not carry
    over: a marker file present in the commit must not, by itself, buy an
    exemption it would not otherwise earn. Today (no exemption at all)
    this blocks regardless, same as every other case here."""
    def mutate(repo: Path) -> None:
        marker = repo / ".codex" / "hooks" / ".loom-hook-fired"
        marker.write_text("forced\n", encoding="utf-8")
        git(repo, "add", "-f", str(marker))

    repo = build_repo(tmp_path)
    _plumbing_commit(repo, trailer=False, mutate=mutate)
    result = run_checker("push", cwd=repo)
    assert result.returncode == 1
    assert RULE in blocked_rules(result)
