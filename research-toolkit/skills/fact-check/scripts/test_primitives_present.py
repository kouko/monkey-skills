"""Guard that fact-check's four reusable primitives are present and intact.

`schemas.py`, `rank.py`, `prompts.py`, and `dedup.py` in this directory are
byte-identical FUNCTIONAL COPIES of the deep-research skill's primitives,
which is the single source of truth (SSOT). They are placed here by
`research-toolkit/scripts/sync-primitives.sh` and kept in lockstep with the
SSOT by a CI MD5 sync-group check.

DO NOT edit the copied primitives in this directory — any divergence from the
SSOT will fail the CI MD5 check. This test only asserts that each copy imports
(flat import) and exposes a sentinel symbol; it does not re-test their behavior
(the SSOT owns the behavioral tests).
"""

import dedup
import prompts
import rank
import schemas


def test_schemas_sentinel():
    assert schemas.VOTES_PER_CLAIM == 3


def test_rank_sentinel():
    assert callable(rank.quorum_survives)


def test_prompts_sentinel():
    assert callable(prompts.verify_prompt)


def test_dedup_sentinel():
    assert callable(dedup.filter_novel)
