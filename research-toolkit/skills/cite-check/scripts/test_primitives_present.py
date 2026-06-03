"""Presence/import guard for the four synced primitives.

schemas.py / rank.py / prompts.py / dedup.py in this directory are
byte-identical functional copies of the deep-research SSOT
(research-toolkit/skills/deep-research/scripts/). They are kept in
sync — and their byte-identity is enforced — by CI MD5 sync check.
Do NOT edit them here; edit the SSOT and re-run
research-toolkit/scripts/sync-primitives.sh.

This test only asserts each copy imports flat and exposes a sentinel
symbol, so a missing/broken sync fails loudly at the skill level.
"""


def test_schemas_imports_with_sentinels():
    import schemas

    assert schemas.EXTRACT_SCHEMA is not None
    assert schemas.VERDICT_SCHEMA is not None


def test_rank_imports_with_sentinel():
    import rank

    assert callable(rank.quorum_survives)


def test_prompts_imports_with_sentinel():
    import prompts

    assert callable(prompts.fetch_prompt)


def test_dedup_imports_with_sentinel():
    import dedup

    assert callable(dedup.norm_url)
