"""Pins for check_anchor_copies.py — verifies the two INLINE-duplicated Tier 1
standards files (copywriting-toolkit/CLAUDE.md §INLINE-duplicate clarification)
stay byte-identical across their skill copies.

No registered REQ-ids in this dispatch — @req tags intentionally omitted.
"""

import importlib.util
import sys
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parent / "check_anchor_copies.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("check_anchor_copies", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_live_tree_is_clean():
    # WHY: the plan's acceptance criterion is that the real repo tree (5
    # psychology-anchor copies + 2 AISAS copies) is currently identical —
    # this pin fails loud the day someone edits one copy without the others.
    mod = _load_module()
    failures = mod.check_all(mod.SKILLS_ROOT)
    assert failures == [], f"unexpected drift in live tree: {failures}"


def test_synthetic_drift_is_detected(tmp_path):
    # WHY: a script that only ever runs against the (currently clean) live
    # tree has never proven it can catch drift — this fixture mutates one
    # byte in one copy and requires the failure to name that exact file.
    mod = _load_module()

    canonical_rel = mod.PSYCHOLOGY_CANONICAL
    drifted_rel = mod.PSYCHOLOGY_COPIES[0]

    canonical_src = mod.SKILLS_ROOT / canonical_rel
    original = canonical_src.read_bytes()

    for rel in [canonical_rel, *mod.PSYCHOLOGY_COPIES]:
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(original)

    for rel in [mod.AISAS_CANONICAL, *mod.AISAS_COPIES]:
        src = mod.SKILLS_ROOT / rel
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())

    drifted_path = tmp_path / drifted_rel
    mutated = bytearray(drifted_path.read_bytes())
    mutated[0] ^= 0xFF  # flip one byte — deliberately not "make it empty"
    drifted_path.write_bytes(bytes(mutated))

    failures = mod.check_all(tmp_path)
    assert failures, "mutated copy must be reported as drift"
    joined = "\n".join(failures)
    assert drifted_rel in joined, f"drifted file {drifted_rel!r} not named in output: {joined}"


def test_main_returns_nonzero_and_names_file_on_drift(tmp_path, capsys):
    # WHY: acceptance criterion is "non-zero exit with a diff summary on
    # drift" at the CLI level, not just the internal check_all() list.
    mod = _load_module()

    for rel in [mod.PSYCHOLOGY_CANONICAL, *mod.PSYCHOLOGY_COPIES]:
        src = mod.SKILLS_ROOT / rel
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())

    for rel in [mod.AISAS_CANONICAL, *mod.AISAS_COPIES]:
        src = mod.SKILLS_ROOT / rel
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(src.read_bytes())

    drifted_rel = mod.AISAS_COPIES[0]
    drifted_path = tmp_path / drifted_rel
    mutated = bytearray(drifted_path.read_bytes())
    mutated[-1] ^= 0xFF
    drifted_path.write_bytes(bytes(mutated))

    exit_code = mod.main(tmp_path)
    out = capsys.readouterr().out
    assert exit_code != 0
    assert drifted_rel in out


def test_main_returns_zero_on_clean_live_tree(capsys):
    # WHY: pins the exit-0 contract the acceptance criteria require for the
    # actual live run (`python3 check_anchor_copies.py` must exit 0 today).
    mod = _load_module()
    exit_code = mod.main(mod.SKILLS_ROOT)
    assert exit_code == 0
