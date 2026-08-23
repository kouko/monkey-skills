"""Self-local drift gate for loom-code's Codex manifest.

The shared engine ``scripts/sync_codex_manifests.py`` (repo-level SSOT) now owns
all the pure sync/check logic; those functions are exercised by
``scripts/test_sync_codex_manifests.py``. loom-code no longer ships its own copy
of the engine — this test only asserts that loom-code's COMMITTED manifests
(``.claude-plugin`` SSOT vs ``.codex-plugin`` derived) stay in lock-step when
run through the shared engine.

It exercises the shared engine via its CLI (subprocess) rather than importing
it, so loom-code/scripts/ needs no sys.path hacking to reach the repo-level
module. Stdlib only (subprocess).
"""

import json
import subprocess
import sys
from pathlib import Path

# loom-code/scripts/<this file> -> repo root is two parents up from loom-code/.
REPO_ROOT = Path(__file__).resolve().parents[2]
ENGINE = REPO_ROOT / "scripts" / "sync_codex_manifests.py"
MANDATORY_DEPENDENCY_KEYS = {
    "dependencies",
    "pluginDependencies",
    "requiredPlugins",
    "requires",
}


def test_loom_code_codex_manifest_in_sync_via_shared_engine():
    """loom-code's committed Codex manifest matches its Claude SSOT.

    Guards against the manifests drifting AND against the shared engine ever
    changing loom-code's output — `--check` is a pure read that exits 0 only
    when the shared fields already match byte-for-byte.
    """
    proc = subprocess.run(
        [sys.executable, str(ENGINE), "--check", "loom-code"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr


def test_loom_code_manifest_and_docs_preserve_optional_composition():
    for host_manifest in (".claude-plugin", ".codex-plugin"):
        manifest = json.loads(
            (REPO_ROOT / "loom-code" / host_manifest / "plugin.json").read_text()
        )
        mandatory = {
            key: manifest[key]
            for key in MANDATORY_DEPENDENCY_KEYS
            if key in manifest
        }
        assert "loom-design" not in json.dumps(mandatory, sort_keys=True)

    readme = (REPO_ROOT / "loom-code" / "README.md").read_text()
    for phrase in (
        "independently installable",
        "plugin-qualified skill names",
        "docs/loom/",
        "N/A with the reason",
    ):
        assert phrase in readme
