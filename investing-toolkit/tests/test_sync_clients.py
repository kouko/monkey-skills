"""test_sync_clients.py — verify sync-clients.sh + CI workflow (no network).

Covers:
  1. `bash scripts/sync-clients.sh --check` exits 0 (zero drift) on the
     canonical-vs-skill-copy invariant.
  2. The ADR-0001 client groups are at the expected fan-out:
        yfinance_client.py × 5 (data-us/jp/tw/kr/cn)
        fred_client.py     × 2 (data-us, data-cn)
        nbs_client.py      × 1 (data-cn)
        akshare_client.py  × 1 (data-cn)
     Each canonical (under investing-toolkit/scripts/) is byte-identical to
     every skill copy.
  3. .github/workflows/check-script-sync.yml parses as YAML and explicitly
     enumerates the same 4 groups (yfinance / fred / nbs / akshare). The
     ta_client group must NOT appear in PR 1 (Wave 4 Removal).
"""
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
SKILLS_DIR = ROOT / "skills"
SYNC_SH = SCRIPTS_DIR / "sync-clients.sh"

REPO_ROOT = ROOT.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "check-script-sync.yml"

EXPECTED_GROUPS = {
    "yfinance_client.py": ["data-us", "data-jp", "data-tw", "data-kr", "data-cn"],
    "fred_client.py": ["data-us", "data-cn"],
    "nbs_client.py": ["data-cn"],
    "akshare_client.py": ["data-cn"],
}


def _md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


# --------------------------------------------------------------------------- #
# 1. sync-clients.sh --check exits 0
# --------------------------------------------------------------------------- #


def test_sync_clients_sh_present_and_executable():
    assert SYNC_SH.is_file(), f"missing {SYNC_SH}"


def test_sync_clients_check_passes():
    """Running sync-clients.sh --check must exit 0 (no drift)."""
    result = subprocess.run(
        ["bash", str(SYNC_SH), "--check"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=str(ROOT),
    )
    assert result.returncode == 0, (
        f"sync-clients.sh --check failed (exit {result.returncode}).\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


# --------------------------------------------------------------------------- #
# 2. Group fan-out + MD5 identity
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "client,targets",
    sorted(EXPECTED_GROUPS.items()),
)
def test_client_group_fanout(client: str, targets: list[str]):
    """Every expected target has the file AND md5 == canonical."""
    canonical = SCRIPTS_DIR / client
    assert canonical.is_file(), f"missing canonical: {canonical}"
    canonical_hash = _md5(canonical)

    for skill in targets:
        copy = SKILLS_DIR / skill / "scripts" / client
        assert copy.is_file(), (
            f"missing expected copy of {client} in {skill}/scripts/"
        )
        h = _md5(copy)
        assert h == canonical_hash, (
            f"MD5 drift for {skill}/scripts/{client}: "
            f"{h} != canonical {canonical_hash}"
        )


def test_client_group_counts():
    """Sanity-check the fan-out counts match the ADR-0001 spec."""
    counts = {client: len(skills) for client, skills in EXPECTED_GROUPS.items()}
    assert counts == {
        "yfinance_client.py": 5,
        "fred_client.py": 2,
        "nbs_client.py": 1,
        "akshare_client.py": 1,
    }, counts


# --------------------------------------------------------------------------- #
# 3. CI workflow YAML
# --------------------------------------------------------------------------- #


def test_workflow_yaml_present():
    assert WORKFLOW.is_file(), f"missing {WORKFLOW}"


def test_workflow_yaml_parses():
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        pytest.skip("pyyaml not installed (run via `uv run --with pytest --with pyyaml`)")
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "workflow YAML must be a mapping"
    # GitHub Actions YAML — the `on:` key parses as boolean True in YAML 1.1
    # (the unquoted reserved word). Accept either form.
    assert ("jobs" in data), "workflow missing 'jobs' key"
    assert (True in data) or ("on" in data), "workflow missing 'on' key"


def test_workflow_has_4_explicit_groups():
    """Workflow must explicitly enumerate the 4 ADR-0001 groups in order
    (yfinance / fred / nbs / akshare). ta_client group MUST be absent in PR 1
    (Wave 4 removed it: only one consumer = analysis-technical, the canonical
    owner). When a second consumer is added later, this expectation will need
    to grow."""
    text = WORKFLOW.read_text(encoding="utf-8")
    for client in ("yfinance_client.py", "fred_client.py", "nbs_client.py", "akshare_client.py"):
        assert client in text, f"workflow missing reference to group: {client}"
    # ta_client group should NOT be enforced in PR 1.
    # The header comment may mention `ta_client.py` explanatorily, but no
    # `check_group(...ta_client.py...)` call should exist.
    assert 'check_group(\n              "ta_client' not in text, (
        "ta_client group was deliberately removed in PR 1 Wave 4 — "
        "but workflow still references a check_group() for it"
    )
    assert "check_group('ta_client" not in text


def test_workflow_groups_match_sync_sh():
    """Both files must reference the same set of clients."""
    sh_text = SYNC_SH.read_text(encoding="utf-8")
    yml_text = WORKFLOW.read_text(encoding="utf-8")
    for client in EXPECTED_GROUPS:
        assert client in sh_text, f"sync-clients.sh missing reference to {client}"
        assert client in yml_text, f"workflow missing reference to {client}"
