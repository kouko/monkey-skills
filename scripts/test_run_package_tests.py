"""fix:W1-05 — the package-tests runner runs one pytest session per group."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNNER = REPO / "scripts" / "run_package_tests.py"
sys.path.insert(0, str(RUNNER.parent))
from run_package_tests import split_groups  # noqa: E402


def test_split_groups_separates_on_double_dash() -> None:
    assert split_groups(["a/", "-q", "--", "b/", "-q"]) == [["a/", "-q"], ["b/", "-q"]]
    assert split_groups(["a/"]) == [["a/"]]
    assert split_groups(["--", "b/"]) == [["b/"]]


def test_runner_exit_code_is_nonzero_when_a_later_group_fails(tmp_path: Path) -> None:
    ok = tmp_path / "ok"; ok.mkdir()
    (ok / "test_ok.py").write_text("def test_ok():\n    assert True\n")
    bad = tmp_path / "bad"; bad.mkdir()
    (bad / "test_bad.py").write_text("def test_bad():\n    assert False\n")
    good = subprocess.run([sys.executable, str(RUNNER), str(ok), "-q", "-p", "no:cacheprovider"], capture_output=True)
    assert good.returncode == 0, good.stdout
    mixed = subprocess.run([sys.executable, str(RUNNER), str(ok), "-q", "-p", "no:cacheprovider", "--", str(bad), "-q", "-p", "no:cacheprovider"], capture_output=True)
    assert mixed.returncode != 0


def test_runner_with_no_groups_exits_nonzero() -> None:
    for argv in ([], ["--"]):
        result = subprocess.run([sys.executable, str(RUNNER), *argv], capture_output=True)
        assert result.returncode == 2, argv
