"""Adversarial probe for W1-02 of
2026-09-05-graduated-probes-independent-of-local-history: the graduated
probe suite must carry no test whose only way to run is to read this
change's own local branch history.

Builds a CI-shaped clone of HEAD itself (W1-01's `rehearse_probes.py` has
not landed while this probe is written; once it lands the same clone
shape is available as a reusable script, but this probe stays
self-contained rather than depending on dispatch order): a full-history
`git clone --no-local`, detached at the source repo's current HEAD sha,
with the local `main` (and `master`, if present) ref removed -- the same
shape `origin/main`-resolves / no-local-trunk shape CI's `fetch-depth: 0`
checkout produces, and the shape
`docs/loom/memory/pre-branch-end-ci-rehearsal-uses-full-history-without-a-local-main.md`
names.

Inside that clone, `python3 -m pytest loom-code/scripts/test_probes_*.py
-q -rs -p no:cacheprovider` must report zero `SKIPPED` lines whose reason
names local branch history (`history`, `squash-merged`, `shipped`, or
"its own branch") and zero `FAILED` lines. Before W1-02's deletions this
is red: 5 such skips (2 from `_confirm_intent_sha()` in
test_probes_complexity_wave_end.py, 3 from
`_skip_if_language_policy_shipped()` across test_probes_language_policy.py
and test_probes_language_policy_branch_end.py).

Independently re-runnable: `python3 -m pytest
docs/loom/2026-09-05-graduated-probes-independent-of-local-history/evidence/probes/test_no_history_class_skips_on_main.py
-q` from the repo root.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
)

HISTORY_CLASS_RE = re.compile(
    r"history|squash-merged|shipped|its own branch", re.IGNORECASE
)


def _clone_ci_shaped(tmp_dir: Path) -> Path:
    """Clone REPO into `tmp_dir` the way CI's `fetch-depth: 0` checkout
    looks: full history, detached at REPO's current HEAD sha, with the
    local `main`/`master` trunk ref removed so only `origin/main`
    resolves as a base ref."""
    clone_dir = tmp_dir / "clone"
    subprocess.run(
        ["git", "clone", "--no-local", f"file://{REPO}", str(clone_dir)],
        capture_output=True, text=True, check=True,
    )
    head_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(REPO), capture_output=True, text=True, check=True,
    ).stdout.strip()
    subprocess.run(
        ["git", "checkout", "--detach", head_sha],
        cwd=str(clone_dir), capture_output=True, text=True, check=True,
    )
    for trunk in ("main", "master"):
        probe = subprocess.run(
            ["git", "rev-parse", "--verify", f"refs/heads/{trunk}"],
            cwd=str(clone_dir), capture_output=True, text=True,
        )
        if probe.returncode == 0:
            subprocess.run(
                ["git", "update-ref", "-d", f"refs/heads/{trunk}"],
                cwd=str(clone_dir), capture_output=True, text=True, check=True,
            )
    return clone_dir


NESTED_ENV = "REHEARSE_PROBES_NESTED"


def test_no_history_class_skips_on_main() -> None:
    # This probe clones the repository and runs every graduated probe file
    # inside the clone -- including its own graduated copy. Both this probe
    # and rehearse_probes.py set the marker below for the pytest they spawn;
    # inside such a run this probe skips, so the clone never clones again.
    if os.environ.get(NESTED_ENV):
        pytest.skip(
            f"already inside a rehearsal clone ({NESTED_ENV} is set); a "
            "nested clone-and-run would recurse"
        )
    with tempfile.TemporaryDirectory() as tmp:
        clone_dir = _clone_ci_shaped(Path(tmp))

        xdist_probe = subprocess.run(
            [sys.executable, "-c", "import xdist"],
            cwd=str(clone_dir), capture_output=True, text=True,
        )
        # pytest does not itself expand a glob passed as argv (only a
        # shell does); expand it here since subprocess.run is invoked
        # without shell=True.
        probe_paths = sorted(
            str(p.relative_to(clone_dir))
            for p in (clone_dir / "loom-code" / "scripts").glob("test_probes_*.py")
        )
        assert probe_paths, f"no test_probes_*.py files found under {clone_dir}"
        pytest_args = [
            sys.executable, "-m", "pytest",
            *probe_paths,
            "-q", "-rs", "-p", "no:cacheprovider",
        ]
        if xdist_probe.returncode == 0:
            pytest_args += ["-n", "auto"]

        result = subprocess.run(
            pytest_args, cwd=str(clone_dir), capture_output=True, text=True,
            env={**os.environ, NESTED_ENV: "1"},
        )

        # wave-end:1-02: a collection error or a "no tests collected" exit
        # leaves no FAILED lines and would otherwise pass this probe
        # silently -- the rehearsal must actually have run and passed.
        assert result.returncode == 0, (
            f"pytest exited {result.returncode} in the CI-shaped clone "
            f"(expected 0)\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )

        skipped_lines = [
            line for line in result.stdout.splitlines()
            if line.strip().startswith("SKIPPED")
        ]
        # Classify the REASON only: a `-rs` line is `SKIPPED [n] <path>:<line>: <reason>`,
        # and the path may itself contain the word "history" (this probe's
        # own graduated copy does), which is not a history-bound skip.
        history_class_skips = [
            line for line in skipped_lines
            if HISTORY_CLASS_RE.search(line.split(": ", 1)[1] if ": " in line else line)
        ]
        failed_lines = [
            line for line in result.stdout.splitlines()
            if line.strip().startswith("FAILED")
        ]

        assert history_class_skips == [], (
            "graduated probe suite still carries history-bound skips in a "
            f"CI-shaped clone: {history_class_skips}\nfull stdout:\n{result.stdout}"
        )
        assert failed_lines == [], (
            f"graduated probe suite failed in a CI-shaped clone: {failed_lines}\n"
            f"full stdout:\n{result.stdout}"
        )


if __name__ == "__main__":  # pragma: no cover
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
