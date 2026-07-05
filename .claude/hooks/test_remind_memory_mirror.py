"""Behavioral tests for the loom-memory mirror-reminder PostToolUse hook.

The hook (``remind-memory-mirror.sh``) is host-neutral: it reads a
PostToolUse stdin-JSON payload, and when a project-type memory note
(``*/.claude/projects/*/memory/*.md`` whose frontmatter says
``type: project``) was written, it exits 2 with a stderr reminder to
mirror the note into the repo's committed store (``docs/loom/BACKLOG.md``
/ ``docs/loom/memory/``). Everything else — other note types, MEMORY.md
index writes, non-memory paths, malformed or alternate-shaped payloads —
must be a silent exit-0 no-op (a hook must never break the session).

Tests drive the hook the way Claude Code does: a mock PostToolUse
stdin-JSON ``{"tool_input": {"file_path": ...}}`` piped to the script.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".claude" / "hooks" / "remind-memory-mirror.sh"


def run_hook(stdin: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(HOOK)],
        input=stdin,
        capture_output=True,
        text=True,
    )


def run_hook_on(file_path: str) -> subprocess.CompletedProcess[str]:
    return run_hook(json.dumps({"tool_input": {"file_path": file_path}}))


def _make_note(tmp_path: Path, filename: str, content: str) -> Path:
    """Create a memory note on disk under a realistic auto-memory layout.

    The hook reads the written file's frontmatter from disk, so the fixture
    must materialize the file, not just fabricate a path.
    """
    memory_dir = tmp_path / ".claude" / "projects" / "-Users-x-somerepo" / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)
    note = memory_dir / filename
    note.write_text(content, encoding="utf-8")
    return note


# --- (a) project-type note -> exit 2 + mirror reminder ----------------------

def test_project_type_note_triggers_reminder(tmp_path):
    note = _make_note(
        tmp_path,
        "project_loom_memory_store.md",
        "---\ntype: project\n---\n\nbody\n",
    )
    result = run_hook_on(str(note))
    assert result.returncode == 2
    assert "docs/loom/BACKLOG.md" in result.stderr
    assert "docs/loom/memory/" in result.stderr


def test_project_type_under_metadata_key_triggers_reminder(tmp_path):
    """Real notes sometimes nest the type under a `metadata:` key (indented
    `  type: project`). The frontmatter grep must tolerate both forms."""
    note = _make_note(
        tmp_path,
        "project_indented_form.md",
        "---\nmetadata:\n  type: project\n---\n\nbody\n",
    )
    result = run_hook_on(str(note))
    assert result.returncode == 2
    assert "docs/loom/BACKLOG.md" in result.stderr
    assert "docs/loom/memory/" in result.stderr


# --- (b) user / feedback types -> silent no-op ------------------------------

def test_user_type_note_is_silent(tmp_path):
    note = _make_note(
        tmp_path, "reference_user_note.md", "---\ntype: user\n---\n\nbody\n"
    )
    result = run_hook_on(str(note))
    assert result.returncode == 0
    assert result.stderr == ""


def test_feedback_type_note_is_silent(tmp_path):
    note = _make_note(
        tmp_path, "feedback_some_lesson.md", "---\ntype: feedback\n---\n\nbody\n"
    )
    result = run_hook_on(str(note))
    assert result.returncode == 0
    assert result.stderr == ""


# --- (c) MEMORY.md index writes -> silent no-op -----------------------------

def test_memory_index_write_is_silent(tmp_path):
    """The MEMORY.md index is curated in place — never a mirror candidate,
    even if its content happens to contain `type: project`."""
    note = _make_note(tmp_path, "MEMORY.md", "---\ntype: project\n---\n\nindex\n")
    result = run_hook_on(str(note))
    assert result.returncode == 0
    assert result.stderr == ""


# --- (d) non-memory-dir paths -> silent no-op -------------------------------

def test_non_memory_path_is_silent():
    result = run_hook_on("/somewhere/research-toolkit/SKILL.md")
    assert result.returncode == 0
    assert result.stderr == ""


# --- (e) malformed / missing stdin -> exit 0, never break the session -------

def test_malformed_stdin_is_noop():
    result = run_hook("this is not json {{{")
    assert result.returncode == 0
    assert result.stderr == ""


def test_empty_stdin_is_noop():
    result = run_hook("")
    assert result.returncode == 0
    assert result.stderr == ""


# --- (f) payload-shape tolerance (dual-host) -> exit 0, never crash ---------

def test_alternate_path_key_is_silent(tmp_path):
    """A host that ships the path under a different key (e.g. `path`) must
    not crash the hook — it silently no-ops."""
    note = _make_note(
        tmp_path, "project_alt_key.md", "---\ntype: project\n---\n\nbody\n"
    )
    result = run_hook(json.dumps({"tool_input": {"path": str(note)}}))
    assert result.returncode == 0
    assert result.stderr == ""


def test_missing_tool_input_is_noop():
    result = run_hook(json.dumps({"tool_name": "Write"}))
    assert result.returncode == 0
    assert result.stderr == ""


# --- robustness: unreadable file / body horizontal rules ---------------------

@pytest.mark.skipif(os.geteuid() == 0, reason="root ignores file permissions")
def test_unreadable_note_is_noop(tmp_path):
    """A memory-dir file that exists but cannot be read (e.g. a permissions
    race between the -f check and the frontmatter read) must be a silent
    exit-0 no-op — never a raw awk error escaping to stderr as an
    exit-2-without-reminder session break."""
    note = _make_note(
        tmp_path, "project_unreadable.md", "---\ntype: project\n---\n\nbody\n"
    )
    note.chmod(0o000)
    try:
        result = run_hook_on(str(note))
    finally:
        note.chmod(0o644)
    assert result.returncode == 0
    assert result.stderr == ""


def test_body_horizontal_rules_do_not_false_positive(tmp_path):
    """A note with NO frontmatter whose body contains a `---` horizontal-rule
    pair enclosing a `type: project` line must not trigger — a fence pair
    only counts as frontmatter when it opens at line 1."""
    note = _make_note(
        tmp_path,
        "reference_body_rules.md",
        "Some intro text.\n\n---\ntype: project\n---\n\nmore body\n",
    )
    result = run_hook_on(str(note))
    assert result.returncode == 0
    assert result.stderr == ""
