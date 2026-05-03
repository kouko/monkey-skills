"""test_sync_clients.py — verify sync-clients.sh + CI workflow (no network).

Post-ADR-0008 (2026-05-03): MCP server removed; the
`investing-toolkit/scripts/` canonical directory is gone. Only
cross-skill duplications remain — `data-us` is the reference skill for
both groups:

  - yfinance_client.py: data-us → data-jp / data-tw / data-kr / data-cn
                        (4 cross-skill copies must equal data-us)
  - fred_client.py:     data-us → data-cn (1 copy must equal data-us)

All other clients are single-skill (no cross-skill copies; no sync).

Covers:
  1. `bash scripts/sync-clients.sh --check` exits 0 (zero drift).
  2. The 2 cross-skill groups have the expected fan-out.
  3. .github/workflows/check-script-sync.yml parses as YAML and
     enumerates the same 2 groups.
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

# Cross-skill duplication groups. `data-us` is the canonical reference;
# every other skill in the list must hold a byte-identical copy.
EXPECTED_GROUPS = {
    "yfinance_client.py": ["data-jp", "data-tw", "data-kr", "data-cn"],
    "fred_client.py": ["data-cn"],
}
REFERENCE_SKILL = "data-us"


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
# 2. Group fan-out + MD5 identity (cross-skill)
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "client,targets",
    sorted(EXPECTED_GROUPS.items()),
)
def test_client_group_fanout(client: str, targets: list[str]):
    """Every expected target has the file AND md5 == data-us reference."""
    reference = SKILLS_DIR / REFERENCE_SKILL / "scripts" / client
    assert reference.is_file(), f"missing reference: {reference}"
    reference_hash = _md5(reference)

    for skill in targets:
        copy = SKILLS_DIR / skill / "scripts" / client
        assert copy.is_file(), (
            f"missing expected copy of {client} in {skill}/scripts/"
        )
        h = _md5(copy)
        assert h == reference_hash, (
            f"MD5 drift for {skill}/scripts/{client}: "
            f"{h} != reference {reference_hash}"
        )


def test_client_group_counts():
    """Sanity-check the fan-out counts match ADR-0008's surface."""
    counts = {client: len(skills) for client, skills in EXPECTED_GROUPS.items()}
    assert counts == {
        "yfinance_client.py": 4,  # jp + tw + kr + cn
        "fred_client.py": 1,       # cn
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


def test_workflow_has_2_explicit_groups():
    """Workflow must explicitly enumerate the 2 ADR-0008 cross-skill groups
    (yfinance / fred). Other clients (nbs / akshare / dgbas / ndc / cbc /
    statgov / fdr / etc.) are single-skill post-MCP-removal — they MUST NOT
    appear as check_group(...) calls in the workflow."""
    text = WORKFLOW.read_text(encoding="utf-8")
    for client in EXPECTED_GROUPS:
        assert client in text, f"workflow missing reference to group: {client}"
    # Single-skill clients must not appear as check_group calls.
    for orphan in (
        "nbs_client.py", "akshare_client.py",
        "dgbas_client.py", "ndc_client.py", "cbc_client.py",
        "statgov_client.py", "fdr_client.py",
    ):
        assert f'check_group("\n              "{orphan}' not in text, (
            f"{orphan} is single-skill post-ADR-0008 — must not have a "
            "check_group(...) call. Header comment may mention it as context."
        )


def test_workflow_groups_match_sync_sh():
    """Both files must reference the same set of cross-skill clients."""
    sh_text = SYNC_SH.read_text(encoding="utf-8")
    yml_text = WORKFLOW.read_text(encoding="utf-8")
    for client in EXPECTED_GROUPS:
        assert client in sh_text, f"sync-clients.sh missing reference to {client}"
        assert client in yml_text, f"workflow missing reference to {client}"
