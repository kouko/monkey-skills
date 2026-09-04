"""Behavioral tests for the .codex/hooks/*.sh thin shims (W1-02).

Per docs/loom/2026-09-04-codex-hook-trust-covers-every-definition-and-worktree
/plan.md `## 設計決定`, `.codex/hooks/validate-skill-folder-structure.sh` and
`.codex/hooks/remind-memory-mirror.sh` must become thin shims: read stdin
once, record the firing (best-effort, never fatal), then `exec` the real
`.claude/hooks/<name>.sh` with the same stdin. On every observable axis
(exit code, stdout, stderr) a shim must behave exactly like the original it
delegates to.

Each test runs both copies from a scratch directory that contains its own
`.codex/` + `.claude/hooks/` (copied from this repo), so the ledger side
effect never touches this repo's real
`.codex/hooks/.loom-hook-fired`.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SHIM_NAMES = ("validate-skill-folder-structure.sh", "remind-memory-mirror.sh")


def _scratch_repo(tmp_path: Path) -> Path:
    """A scratch copy of just enough of the repo for the shims to run:
    .codex/hooks/ (shims + recorder) and .claude/hooks/ (the originals they
    delegate to). Keeps the real repo's ledger untouched."""
    target = tmp_path / "scratch"
    (target / ".codex" / "hooks").mkdir(parents=True)
    (target / ".claude" / "hooks").mkdir(parents=True)
    for name in SHIM_NAMES:
        shutil.copy(REPO_ROOT / ".codex" / "hooks" / name, target / ".codex" / "hooks" / name)
        shutil.copy(REPO_ROOT / ".claude" / "hooks" / name, target / ".claude" / "hooks" / name)
        (target / ".codex" / "hooks" / name).chmod(0o755)
        (target / ".claude" / "hooks" / name).chmod(0o755)
    shutil.copy(
        REPO_ROOT / ".codex" / "hooks" / "loom_record_fire.py",
        target / ".codex" / "hooks" / "loom_record_fire.py",
    )
    return target


def _fire(command: Path, payload: dict, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(command)],
        cwd=str(cwd),
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=60,
    )


def _post_write_payload(cwd: Path, file_path: str) -> dict:
    return {
        "hook_event_name": "PostToolUse",
        "tool_name": "Write",
        "tool_input": {"file_path": file_path},
        "cwd": str(cwd),
        "permission_mode": "default",
    }


def _assert_equivalent(scratch: Path, name: str, payload: dict) -> None:
    codex_cmd = scratch / ".codex" / "hooks" / name
    claude_cmd = scratch / ".claude" / "hooks" / name
    codex_proc = _fire(codex_cmd, payload, cwd=scratch)
    claude_proc = _fire(claude_cmd, payload, cwd=scratch)
    assert codex_proc.returncode == claude_proc.returncode
    assert codex_proc.stdout == claude_proc.stdout
    assert codex_proc.stderr == claude_proc.stderr


# --- (a) a nested skill subfolder path -> validate exits 2 ---


def test_validate_shim_matches_original_on_nested_violation(tmp_path):
    scratch = _scratch_repo(tmp_path)
    skill_dir = scratch / "skills" / "foo"
    nested = skill_dir / "assets" / "scripts"
    nested.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text("---\nname: foo\n---\n", encoding="utf-8")
    (nested / "bad.py").write_text("# nested\n", encoding="utf-8")
    payload = _post_write_payload(scratch, str(skill_dir / "assets" / "SKILL.md"))
    _assert_equivalent(scratch, "validate-skill-folder-structure.sh", payload)


# --- (b) a project-type memory note path -> remind exits 2 ---


def test_remind_shim_matches_original_on_project_memory_note(tmp_path):
    scratch = _scratch_repo(tmp_path)
    memory_dir = scratch / ".claude" / "projects" / "proj" / "memory"
    memory_dir.mkdir(parents=True)
    note = memory_dir / "project_thing.md"
    note.write_text("---\ntype: project\n---\nsome note\n", encoding="utf-8")
    payload = _post_write_payload(scratch, str(note))
    _assert_equivalent(scratch, "remind-memory-mirror.sh", payload)


# --- (c) an unrelated path -> both exit 0 ---


def test_both_shims_match_originals_on_unrelated_path(tmp_path):
    scratch = _scratch_repo(tmp_path)
    payload = _post_write_payload(scratch, str(scratch / "README.md"))
    for name in SHIM_NAMES:
        _assert_equivalent(scratch, name, payload)


# --- guard: the shim still writes a ledger line the original never would ---


def test_validate_shim_records_a_firing_the_original_does_not(tmp_path):
    scratch = _scratch_repo(tmp_path)
    payload = _post_write_payload(scratch, str(scratch / "README.md"))
    _fire(scratch / ".codex" / "hooks" / "validate-skill-folder-structure.sh", payload, cwd=scratch)
    ledger = scratch / ".codex" / "hooks" / ".loom-hook-fired"
    assert ledger.is_file(), "the shim must record its own firing"
    assert "PostToolUse" in ledger.read_text(encoding="utf-8")
