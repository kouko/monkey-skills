"""Behavioral contract for segment 2's installed-plugin root."""

import json
import shutil
import subprocess
from pathlib import Path


PIPELINE_DIR = Path(__file__).parent
PLUGIN_ROOT = PIPELINE_DIR.parent.parent


def _write_valid_change(project: Path) -> None:
    change = project / "docs" / "loom" / "renamed-root"
    (change / "specs" / "example").mkdir(parents=True)
    (change / "proposal.md").write_text(
        "# Proposal\n\n"
        "## USM backbone\n- Start → Finish\n\n"
        "## OOUX object model\n- User\n\n"
        "## Provenance\n- Seed: user\n\n"
        "## Blind spots — needs human/field input\n- None known.\n\n"
        "## Path × edge matrix\n| path | edge |\n| --- | --- |\n| start | none |\n\n"
        "## Cross-object combinations\n| Stage | Objects |\n| --- | --- |\n| Start | User |\n\n"
        "## Journey navigation\n- Start → Finish\n\n"
        "## Decisions\n- Keep the probe minimal.\n",
        encoding="utf-8",
    )
    (change / "specs" / "example" / "spec.md").write_text(
        "## ADDED Requirements\n\n"
        "### Requirement: Renamed root\n"
        "The pipeline MUST resolve its validator from the installed plugin root.\n\n"
        "#### Scenario: Installed under an arbitrary name\n"
        "- GIVEN a renamed plugin root\n"
        "- WHEN segment 2 validates its output\n"
        "- THEN the packaged validator executes successfully\n",
        encoding="utf-8",
    )


def test_segment2_executes_validator_from_renamed_plugin_root(tmp_path: Path):
    installed_root = tmp_path / "cache entry '7f31"
    shutil.copytree(PLUGIN_ROOT, installed_root)
    project = tmp_path / "project with 'quote"
    _write_valid_change(project)

    combined = "\n".join(
        (PIPELINE_DIR / name).read_text(encoding="utf-8")
        for name in (
            "driver_20_runstation.js",
            "driver_60_ledger.js",
            "driver_40_seg2.js",
        )
    )
    harness = combined + "\n" + f"""
const {{ execFileSync }} = require('child_process');
var budget = {{ spent: () => 0, remaining: () => 999999 }};
async function agent(prompt, opts) {{
  let validatorExit = 0;
  if (opts && opts.label === 'spec-validator') {{
    const command = prompt.split('\\n').find((line) => line.startsWith('Run via Bash: python3 '));
    if (!command) throw new Error('validator command missing from prompt');
    const shellCommand = command.slice('Run via Bash: '.length);
    execFileSync('/bin/bash', ['-lc', shellCommand], {{ stdio: 'pipe' }});
  }}
  return {{ verdict: 'PASS', artifacts: [], validator_exit: validatorExit,
            interventions: [], summary: 'stub' }};
}}
function phase(title) {{}}
function log(message) {{}}
async function parallel(fns) {{ return Promise.all(fns.map((fn) => fn())); }}
(async () => {{
  await runSegment2({{
    changeId: 'renamed-root',
    projectPath: {json.dumps(str(project))},
    skillsRoot: {json.dumps(str(installed_root))},
    budgets: {{ perStation: {{ spec: 100000, critic: 100000, validator: 100000 }} }},
    models: {{}},
  }});
  console.log('OK');
}})().catch((error) => {{ console.error(error.message); process.exit(1); }});
"""

    result = subprocess.run(
        ["node", "-e", harness], capture_output=True, text=True, timeout=15
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "OK"
