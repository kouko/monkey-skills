"""Structural tests for driver_40_seg2.js — segment-2 module of the
build-assembled Workflow driver (see
docs/loom/plans/2026-07-03-loom-pipeline-conductor.md Task 10). Source-only:
the concat-build lands in Task 14, so this checks the module in isolation via
`node --check` plus grep-asserts on the required contract surface:
spec-expansion writer station seeded by PATHS (not inlined content),
completeness-critic script-layer panel (>=2 fresh-context lens dispatches,
RALLY_CAP loop-back, G5 per-judge ledger recording), a hard validator gate on
the REAL loom-spec validator filename (no adopt-anyway on non-zero exit), and
the G3 Decisions-section presence check. Mirrors
test_pipeline_driver_runstation.py's structural-test pattern.
"""
import re
import subprocess
from pathlib import Path

MODULE_PATH = Path(__file__).parent / "driver_40_seg2.js"
HEADER_PATH = Path(__file__).parent / "driver_00_header.js"
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _seg2_phase_title() -> str:
    """Extract meta.phases[1].title ('Spec') from driver_00_header.js —
    never hardcode it, so a header edit cannot silently desync this test."""
    header_source = HEADER_PATH.read_text(encoding="utf-8")
    titles = re.findall(r"title:\s*'([^']+)'", header_source)
    assert len(titles) >= 2, f"expected >=2 phase titles in header, got {titles}"
    return titles[1]


def test_seg2_validator_gate():
    # @req: REQ-LOOM-PIPELINE-SEG2-1
    assert MODULE_PATH.exists(), f"module missing: {MODULE_PATH}"

    source = MODULE_PATH.read_text(encoding="utf-8")

    # node --check must pass (valid JS syntax, no runtime execution)
    result = subprocess.run(
        ["node", "--check", str(MODULE_PATH)], capture_output=True, text=True
    )
    assert result.returncode == 0, f"node --check failed: {result.stderr}"

    # public function name exactly runSegment2
    assert "async function runSegment2(" in source

    # phase() title matches driver_00_header.js segment-2 title verbatim
    title = _seg2_phase_title()
    assert f"phase('{title}')" in source or f'phase("{title}")' in source, (
        f"phase() call must use the header's segment-2 title verbatim: {title!r}"
    )

    # spec-expansion writer station, seeded with PATHS to segment-1 artifacts
    # (never inlined content — delegation contract)
    assert "loom-spec:spec-expansion" in source
    assert "docs/loom/PRINCIPLES.md" in source
    assert "docs/loom/DESIGN.md" in source
    assert "ui-flows.md" in source

    # completeness-critic panel at SCRIPT layer: >=2 distinct fresh agent()
    # dispatches, RALLY_CAP-bounded loop-back, G5 per-judge ledger recording
    assert source.count("agent(") >= 2, (
        "expects multiple separate agent() dispatches (spec + >=2 critic "
        "lenses + validator)"
    )
    assert "completeness-critic" in source
    assert "RALLY_CAP" in source
    assert source.count("recordLedger(") >= 2, (
        "expects a recordLedger() call per judge (G5) plus other stations"
    )

    # hard validator gate: the REAL validator filename (checked against the
    # actual loom-spec/scripts/ dir, never guessed)
    validator_dir = REPO_ROOT / "loom-spec" / "scripts"
    assert (validator_dir / "validate_spec_output.py").exists(), (
        "expected validate_spec_output.py under loom-spec/scripts/ — "
        "re-check the real filename before asserting on it"
    )
    assert "validate_spec_output.py" in source
    assert "validator_exit" in source

    # non-zero validator exit -> fail loud, no adopt-anyway path
    assert "validator_exit !== 0" in source or "validator_exit != 0" in source
    assert "throw new Error" in source

    # G3: Decisions-section presence check -> intervention record if absent
    assert "## Decisions" in source
    assert "intervention" in source.lower()

    # NO LEDGER / recordLedger DECLARATION here — only reference/usage.
    # Declared in driver_60_ledger.js (Task 12, concurrent).
    assert not re.search(r"\b(function|const|let|var)\s+recordLedger\b", source), (
        "driver_40_seg2.js must not DECLARE recordLedger — it is declared "
        "in driver_60_ledger.js"
    )
    assert not re.search(r"\b(const|let|var)\s+LEDGER\b", source), (
        "driver_40_seg2.js must not DECLARE LEDGER — it is declared in "
        "driver_60_ledger.js"
    )

    # returns an array of STATION results
    assert "return results" in source

    # self-contained: no imports, no non-deterministic clock/random tokens
    assert "import " not in source
    assert "require(" not in source
    for token in ["Date.now(", "Math.random(", "new Date()"]:
        assert token not in source, f"forbidden token present: {token}"


RUNSTATION_PATH = Path(__file__).parent / "driver_20_runstation.js"
LEDGER_PATH = Path(__file__).parent / "driver_60_ledger.js"


def test_seg2_execution_wiring_behavioral():
    """Execution-level probe: concatenate driver_20 (runStation/RALLY_CAP) +
    driver_60 (LEDGER/recordLedger) + driver_40 (runSegment2) sources, stub
    the ambient `agent`/`phase`/`log`/`parallel`/`budget` primitives, and run
    runSegment2() far enough to prove two regressions stay fixed:

    (a) no recordLedger throw during a normal run (every recordLedger() call
        site in driver_40_seg2.js must carry judge OR role — the 2026-07-03
        code-quality-reviewer NEEDS_REVISION finding).
    (b) a missing args.skillsRoot fails loud with the segment-2-specific
        message BEFORE any station dispatch — no hardcoded validator path
        fallback.

    # @req: REQ-LOOM-PIPELINE-SEG2-1
    """
    combined_source = "\n".join(
        p.read_text(encoding="utf-8")
        for p in (RUNSTATION_PATH, LEDGER_PATH, MODULE_PATH)
    )

    harness = combined_source + "\n" + (
        "var budget = { spent: () => 0, remaining: () => 999999 };\n"
        "async function agent(prompt, opts) {\n"
        "  return {\n"
        "    verdict: 'PASS_WITH_NOTES',\n"
        "    artifacts: ['/tmp/x/proposal.md'],\n"
        "    validator_exit: 0,\n"
        "    interventions: [],\n"
        "    summary: 'stub-' + (opts && opts.label),\n"
        "  };\n"
        "}\n"
        "function phase(title) {}\n"
        "function log(msg) {}\n"
        "async function parallel(fns) { return Promise.all(fns.map((fn) => fn())); }\n"
        "\n"
        "(async () => {\n"
        "  // (b) missing skillsRoot must throw, loudly, before any dispatch.\n"
        "  let skillsRootThrew = false;\n"
        "  try {\n"
        "    await runSegment2({\n"
        "      segment: 2, changeId: 'c1', projectPath: '/tmp/x',\n"
        "      budgets: {}, models: {},\n"
        "    });\n"
        "  } catch (e) {\n"
        "    skillsRootThrew = true;\n"
        "    console.error('SKILLSROOT_THREW: ' + e.message);\n"
        "  }\n"
        "  if (!skillsRootThrew) {\n"
        "    console.error('FAIL: missing args.skillsRoot did not throw');\n"
        "    process.exit(1);\n"
        "  }\n"
        "\n"
        "  // (a) a fully-args'd run must not throw inside recordLedger.\n"
        "  let results;\n"
        "  try {\n"
        "    results = await runSegment2({\n"
        "      segment: 2, changeId: 'c1', projectPath: '/tmp/x',\n"
        "      skillsRoot: '/tmp/skills',\n"
        "      budgets: { perStation: { spec: 100000, critic: 100000, validator: 100000 } },\n"
        "      models: {},\n"
        "    });\n"
        "  } catch (e) {\n"
        "    console.error('FAIL: valid run threw unexpectedly: ' + e.message);\n"
        "    process.exit(1);\n"
        "  }\n"
        "\n"
        "  if (!Array.isArray(results) || results.length < 4) {\n"
        "    console.error('FAIL: expected >=4 station results (spec + 2 critics + validator), got ' + (results && results.length));\n"
        "    process.exit(1);\n"
        "  }\n"
        "  if (LEDGER.length < 4) {\n"
        "    console.error('FAIL: expected >=4 recordLedger entries, got ' + LEDGER.length);\n"
        "    process.exit(1);\n"
        "  }\n"
        "\n"
        "  console.log('OK');\n"
        "  process.exit(0);\n"
        "})().catch((e) => {\n"
        "  console.error('UNCAUGHT: ' + e.message);\n"
        "  process.exit(1);\n"
        "});\n"
    )

    result = subprocess.run(
        ["node", "-e", harness], capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0, (
        f"behavioral probe failed: stdout={result.stdout!r} stderr={result.stderr!r}"
    )
    assert "SKILLSROOT_THREW" in result.stderr, (
        "expected runSegment2 to fail loud when args.skillsRoot is missing"
    )
    assert "segment 2 requires args.skillsRoot" in result.stderr, (
        "missing-skillsRoot error must name the fail-loud contract"
    )
    assert "OK" in result.stdout
