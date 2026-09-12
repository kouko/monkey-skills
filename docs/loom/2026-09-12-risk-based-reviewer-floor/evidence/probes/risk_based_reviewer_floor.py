#!/usr/bin/env python3
"""Adversarial replay for the risk-based reviewer-floor allowlist."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[5]
CHECKER = REPO / "loom-code/scripts/loom_checker.py"
CHANGE = "2026-09-12-example"


def load_checker():
    sys.path.insert(0, str(CHECKER.parent))
    spec = importlib.util.spec_from_file_location("reviewer_floor_checker", CHECKER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    checker = load_checker()
    allowed = {
        f"docs/loom/intent/{CHANGE}.md",
        f"docs/loom/{CHANGE}/plan.md",
        "loom-code/scripts/test_policy.py",
        "docs/guide.md",
    }
    assert checker.reviewer_floor_for_paths(allowed, CHANGE) == 1

    attacks = (
        "runtime.py",
        "loom-code/skills/review/SKILL.md",
        "loom-code/agents/reviewer.md",
        "loom-code/contract/manifest.yaml",
        "loom-code/hooks/hooks.json",
        "docs/loom/KICKOFF-DEFAULTS.md",
        "PRINCIPLES.md",
        "unknown.bin",
        f"docs/loom/{CHANGE}/../../runtime.py",
        "docs/loom/another-change/plan.md",
    )
    for attack in attacks:
        assert checker.reviewer_floor_for_paths(allowed | {attack}, CHANGE) == 2, attack
    assert checker.reviewer_floor_for_paths(set(), CHANGE) == 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
