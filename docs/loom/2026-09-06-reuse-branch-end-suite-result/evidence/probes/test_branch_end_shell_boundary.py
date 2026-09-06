"""Fix-round 7 executable evidence for shell expansion and snapshot binding."""
from pathlib import Path
import sys

ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "loom-code/scripts/loom_checker.py").exists())
sys.path.insert(0, str(ROOT / "loom-code/scripts"))
import test_push_shell_boundary as permanent


def test_shell_wordsplit_rejected(tmp_path):
    """The exact intercepted shell string cannot publish an additional branch."""
    permanent.test_shell_wordsplit_rejected(tmp_path, fixed=False)


def test_shell_literal_publishesonlypinned(tmp_path):
    """The canonical command executes one suite and publishes one pinned branch."""
    permanent.test_shell_literal_publishesonlypinned(tmp_path, external=True)


def test_snapshot_validatedhead_rejected(tmp_path, monkeypatch):
    """A commit interleaved before probe snapshots is refused before execution."""
    permanent.test_snapshot_validatedhead_rejected(tmp_path, monkeypatch, fixed=False)
