"""Tests for the skill text (task W3-01, acceptance 8).

The skill must run unchanged on any host (Claude Code or Codex), so the
orchestrator and detector texts may not name host-only tools or model ids.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = SKILL_DIR.parents[2]
SKILL_MD = SKILL_DIR / "SKILL.md"
DETECT_READ = SKILL_DIR / "references" / "detector-read.md"
DETECT_SIM = SKILL_DIR / "references" / "detector-simulate.md"
SKILL_TEXTS = (SKILL_MD, DETECT_READ, DETECT_SIM)

HOST_ONLY_TOOLS = ("workflow tool", "subagent_type", "task tool", "agent tool",
                   "spawn_agent")
MODEL_IDS = ("claude-", "sonnet", "haiku", "opus", "gpt-")
EXEMPT_PREFIX = "Validated on:"


def _env():
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def test_structure_and_description_checks_pass():
    proc = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "check-skill-structure.py"),
         str(REPO_ROOT / "skill-dev-toolkit")],
        capture_output=True, text=True, env=_env(),
    )
    lines = proc.stdout.splitlines()
    assert "PASS  skill-consistency-check" in lines, proc.stdout
    assert not any(
        "skills/skill-consistency-check/" in line and "[CHK-SKL-" in line
        for line in lines
    ), proc.stdout

    desc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
         str(REPO_ROOT / "skill-dev-toolkit" / ".claude-plugin"
             / "test_skill_description_standard.py")],
        capture_output=True, text=True, env=_env(),
    )
    assert desc.returncode == 0, desc.stdout + desc.stderr


def _scannable_lines(path):
    assert path.is_file(), f"missing {path}"
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.lstrip().startswith(EXEMPT_PREFIX):
            continue
        yield n, line.lower()


def test_no_host_only_tool_or_model_id_in_skill_text():
    hits = []
    for path in SKILL_TEXTS:
        for n, line in _scannable_lines(path):
            for token in HOST_ONLY_TOOLS + MODEL_IDS:
                if token in line:
                    hits.append(f"{path.name}:{n}: {token!r}")
    assert not hits, hits


def test_validation_note_is_the_only_exempt_line():
    exempt = [line for line in SKILL_MD.read_text(encoding="utf-8").splitlines()
              if line.lstrip().startswith(EXEMPT_PREFIX)]
    assert len(exempt) == 1, exempt
    assert "sonnet" in exempt[0].lower()


def test_detectors_keep_validated_definitions():
    for path in (DETECT_READ, DETECT_SIM):
        text = path.read_text(encoding="utf-8")
        for heading in ("## Counts as a contradiction", "## Does NOT count",
                        "## Output"):
            assert re.search(rf"^{re.escape(heading)}\s*$", text, re.M), \
                f"{path.name} lacks {heading!r}"
        assert "Precision matters as much as recall" in text
    sim = DETECT_SIM.read_text(encoding="utf-8")
    assert "## Method: execution walk-through (follow this procedure)" in sim
    assert "## Method" not in DETECT_READ.read_text(encoding="utf-8")
