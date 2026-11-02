# concern: multi-choice and padded special picks must not fabricate a training winner
"""Reject non-single choice records before counting training readiness."""

import importlib.util
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[5]
SCRIPTS = ROOT / "skill-dev-toolkit/skills/skill-tuning/scripts"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("preference_log", SCRIPTS / "preference_log.py")
preferences = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preferences)


@pytest.mark.parametrize("pick", ["A+B", "A,C", " multiple ", "none ", "refine "])
def test_preferences_nonsingle_rejected(pick):
    """A decoded identity cannot turn a non-single user choice into a winner."""
    entry = {
        "skill": "synthetic", "verdict": "ADOPT", "user_pick": pick,
        "user_pick_identity": "candidate", "test_prompt_hash": "prompt",
        "variants_shown": [
            {"identity": "baseline", "skill_md_hash": "base"},
            {"identity": "candidate", "skill_md_hash": "candidate"},
        ],
    }
    usable, skipped = preferences.usable_preferences([entry], "synthetic")
    assert usable == []
    assert skipped == 1
