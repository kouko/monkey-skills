import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CANONICAL = REPO_ROOT / "domain-teams/skills/code-team/standards/external-surface-grounding.md"
FUNCTIONAL_COPY = REPO_ROOT / "loom-code/skills/subagent-driven-development/standards/external-surface-grounding.md"
REVIEW_ORACLES = REPO_ROOT / "loom-code/skills/requesting-code-review/test-prompts.json"


def test_in_repo_grounding_is_path_plus_anchor_in_ssot_and_functional_copy() -> None:
    expected_rule = (
        "cited with its path plus an anchor (a verbatim string or stable heading); "
        "a line number is optional precision only when the anchor is ambiguous."
    )

    canonical = " ".join(CANONICAL.read_text().split())
    functional_copy_text = FUNCTIONAL_COPY.read_text()
    functional_copy = " ".join(functional_copy_text.split())

    assert expected_rule in canonical
    assert expected_rule in functional_copy
    assert functional_copy_text.endswith(CANONICAL.read_text())

    expected_example = (
        'Example: `salesforce-toolkit/scripts/upsert.py` with anchor '
        '`"sObjects/Contact/External_Id__c"` already calls that surface, so this '
        "PR mirrors it."
    )
    assert expected_example in canonical
    assert expected_example in functional_copy
    assert "Example: `salesforce-toolkit/scripts/upsert.py:42`" not in canonical
    assert "Example: `salesforce-toolkit/scripts/upsert.py:42`" not in functional_copy

    expected_installed_source_rule = (
        "`Read` of installed source under `node_modules/` / `site-packages/` / "
        "`vendor/` (cite its path plus an anchor: a verbatim string or stable "
        "heading; add a line number only when the anchor is ambiguous)"
    )
    assert expected_installed_source_rule in canonical
    assert expected_installed_source_rule in functional_copy
    assert "`vendor/` (cite `file:line`)" not in canonical
    assert "`vendor/` (cite `file:line`)" not in functional_copy


def test_review_panel_oracle_keys_findings_by_path_anchor_and_dimension() -> None:
    suite = json.loads(REVIEW_ORACLES.read_text())
    expected_behavior = suite["prompts"][0]["expected_behavior"]

    assert "path+anchor+dimension" in expected_behavior
    assert "ignoring optional line precision" in expected_behavior
