"""The progress tooling ships INSIDE the loom-code plugin.

Task 1 of docs/loom/plans/2026-08-10-ship-progress-tooling.md: five
shipped skills mandate plan_card.py / backlog_index.py at 10 call
sites, but the scripts lived only at the repo root — every external
repo silently degraded to hand-editing. The scripts must be files
under loom-code/scripts/ (so `plugin update` delivers them), and the
old repo-root paths must remain working exec shims.

False-green discipline (docs/loom/memory/
subprocess-red-tests-go-false-green-before-the-script-exists.md): the
existence assert comes FIRST in every test, and each subprocess
assert pins a positive fact only a real run produces (the usage
string on stderr, the `--validate: OK` line on stdout) — never a bare
exit-code check, which a missing script file also satisfies (the
interpreter itself exits 2 on a file it cannot open).
"""

import subprocess
import sys
from pathlib import Path

PLUGIN_SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = PLUGIN_SCRIPTS.parent.parent
SHIM_DIR = REPO_ROOT / "scripts"

PLUGIN_PLAN_CARD = PLUGIN_SCRIPTS / "plan_card.py"
PLUGIN_BACKLOG_INDEX = PLUGIN_SCRIPTS / "backlog_index.py"
SHIM_PLAN_CARD = SHIM_DIR / "plan_card.py"
SHIM_BACKLOG_INDEX = SHIM_DIR / "backlog_index.py"


def _run(script: Path, *args: str) -> subprocess.CompletedProcess:
    """Run `script` with cwd at the repo root — backlog_index.py's
    default `--store docs/loom/backlog` resolves relative to cwd."""
    return subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


def test_plan_card_ships_in_the_plugin_and_runs():
    assert PLUGIN_PLAN_CARD.is_file(), (
        f"plan_card.py does not ship in the plugin at {PLUGIN_PLAN_CARD}"
    )
    result = _run(PLUGIN_PLAN_CARD)  # no args -> usage error
    assert "usage" in result.stderr.lower(), result.stderr
    assert result.returncode == 2, result.stdout + result.stderr


def test_backlog_index_ships_in_the_plugin_and_runs():
    assert PLUGIN_BACKLOG_INDEX.is_file(), (
        f"backlog_index.py does not ship in the plugin at {PLUGIN_BACKLOG_INDEX}"
    )
    result = _run(PLUGIN_BACKLOG_INDEX, "--validate")
    assert "backlog_index --validate: OK" in result.stdout, (
        result.stdout + result.stderr
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_repo_root_shims_exist_and_match_the_plugin_copies():
    """Argv-binding discipline: every shim invocation below passes an
    argument that CHANGES the script's output, so a shim that drops
    `sys.argv[1:]` cannot stay output-identical. (A flagless
    `backlog_index.py` run defaults to the same output as `--validate`,
    so `--validate` alone cannot discriminate — probed 2026-08-10.)"""
    assert SHIM_PLAN_CARD.is_file(), f"missing shim at {SHIM_PLAN_CARD}"
    assert SHIM_BACKLOG_INDEX.is_file(), f"missing shim at {SHIM_BACKLOG_INDEX}"

    # plan_card WITH a real plan path renders the card (exit 0,
    # "end-state:" line); an argv-dropping shim falls to the flagless
    # usage error (exit 2) and both asserts below fail.
    plan_path = "docs/loom/plans/2026-08-10-ship-progress-tooling.md"
    shim = _run(SHIM_PLAN_CARD, plan_path)
    plugin = _run(PLUGIN_PLAN_CARD, plan_path)
    assert shim.returncode == 0 and "end-state:" in shim.stdout, (
        shim.stdout + shim.stderr
    )
    assert (shim.returncode, shim.stdout, shim.stderr) == (
        plugin.returncode,
        plugin.stdout,
        plugin.stderr,
    ), "shim scripts/plan_card.py must be output-identical to the plugin copy"

    # --ready prints the ready queue, NOT the validate line — an
    # argv-dropping shim runs flagless (= validate output) and the
    # marker asserts below fail before the equality check can lie.
    shim_b = _run(SHIM_BACKLOG_INDEX, "--ready")
    plugin_b = _run(PLUGIN_BACKLOG_INDEX, "--ready")
    assert "backlog_index --validate: OK" not in shim_b.stdout, (
        "shim ignored --ready and ran the flagless default:\n" + shim_b.stdout
    )
    assert "## OPEN" in shim_b.stdout, shim_b.stdout + shim_b.stderr
    assert (shim_b.returncode, shim_b.stdout) == (
        plugin_b.returncode,
        plugin_b.stdout,
    ), "shim scripts/backlog_index.py must be output-identical to the plugin copy"
