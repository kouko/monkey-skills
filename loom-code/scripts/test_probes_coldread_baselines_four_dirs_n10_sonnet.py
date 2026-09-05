"""W2-01 acceptance probe: four N=10 cold-read baselines exist and are
shaped as the design re-look (`docs/loom/2026-09-04-adversary-three-way-
attribution-measured/evidence/design-relook-run-status-2026-09-05.md`)
pins.

For each of the four baseline directories (precap/current x
adversary/reviewer): `summary.json` exists with `n == 10`,
`model == "sonnet"`, `complete is True`, `attempted_runs == 10`,
`failed_runs == 0`; ten `run-<i>.txt` files exist whose first line
starts with `# command:`. The "current" summaries' `contract.sha256`
must equal sha256 of the checked-in agent file at HEAD; the "precap"
summaries' `contract.sha256` must equal sha256 of the committed
`contract-precap-<role>.md` copy.

Fails today because none of the four baseline directories exist.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest


def _find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "docs" / "loom").is_dir():
            return candidate
    raise RuntimeError(f"could not locate repo root (docs/loom) above {start}")


REPO_ROOT = _find_repo_root(Path(__file__).parent)
CID = "2026-09-04-adversary-three-way-attribution-measured"
EVIDENCE_DIR = REPO_ROOT / "docs" / "loom" / CID / "evidence"

_CASES = [
    ("baseline-precap-adversary", EVIDENCE_DIR / "contract-precap-adversary.md"),
    ("baseline-precap-reviewer", EVIDENCE_DIR / "contract-precap-reviewer.md"),
    ("baseline-current-adversary", REPO_ROOT / "loom-code" / "agents" / "adversary.md"),
    ("baseline-current-reviewer", REPO_ROOT / "loom-code" / "agents" / "reviewer.md"),
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize("dirname,contract_path", _CASES, ids=[c[0] for c in _CASES])
def test_baselines_four_dirs_n10_sonnet(dirname: str, contract_path: Path) -> None:
    baseline_dir = EVIDENCE_DIR / dirname
    summary_path = baseline_dir / "summary.json"
    assert summary_path.is_file(), f"missing {summary_path}"

    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    assert summary["n"] == 10, f"{dirname}: expected n == 10, got {summary['n']!r}"
    assert summary["model"] == "sonnet", f"{dirname}: expected model 'sonnet', got {summary['model']!r}"
    assert summary["complete"] is True, f"{dirname}: expected complete is True, got {summary['complete']!r}"
    assert summary["attempted_runs"] == 10, (
        f"{dirname}: expected attempted_runs == 10, got {summary['attempted_runs']!r}"
    )
    assert summary["failed_runs"] == 0, f"{dirname}: expected failed_runs == 0, got {summary['failed_runs']!r}"

    expected_hash = _sha256(contract_path)
    actual_hash = summary["contract"]["sha256"]
    assert actual_hash == expected_hash, (
        f"{dirname}: contract sha256 mismatch — summary has {actual_hash}, "
        f"expected {expected_hash} (from {contract_path})"
    )

    run_files = sorted(baseline_dir.glob("run-*.txt"))
    assert len(run_files) == 10, f"{dirname}: expected 10 run-<i>.txt files, found {len(run_files)}"
    for i in range(1, 11):
        run_path = baseline_dir / f"run-{i}.txt"
        assert run_path.is_file(), f"{dirname}: missing {run_path.name}"
        first_line = run_path.read_text(encoding="utf-8").splitlines()[0]
        assert first_line.startswith("# command:"), (
            f"{dirname}: {run_path.name} first line does not start with '# command:': {first_line!r}"
        )
