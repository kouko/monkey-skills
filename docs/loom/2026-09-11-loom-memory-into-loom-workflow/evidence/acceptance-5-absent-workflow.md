# Acceptance 5 — absent-loom-workflow failure set, before and after

Method: `git archive` of origin/main and of this branch extracted into two
throwaway directories, `loom-workflow/` removed from each, then each plugin's
suite run in its OWN pytest invocation (loom-code and loom-design ship
same-named test modules, so one combined run reports import collisions that
are an artefact of the invocation, not of the code).

Commands:
    PYTHONDONTWRITEBYTECODE=1 python3 -m pytest loom-code/scripts/ -q
    PYTHONDONTWRITEBYTECODE=1 python3 -m pytest loom-design/scripts/ -q

## before (origin/main)

    ERROR loom-code/scripts/test_prose_pin_rule_text.py
    ERROR loom-code/scripts/test_simplified_station_text.py
    FAILED loom-design/scripts/interface/test_knowledge_triage.py::test_pin_block_byte_untouched_vs_head

## after (this branch)

    ERROR loom-code/scripts/test_prose_pin_rule_text.py
    ERROR loom-code/scripts/test_simplified_station_text.py
    FAILED loom-design/scripts/interface/test_knowledge_triage.py::test_pin_block_byte_untouched_vs_head

## diff

    (empty — the two sets are identical)

The two loom-code entries are the pre-existing cross-plugin reads named in the
intent's Amendments section. The loom-design entry compares a pinned block
against git HEAD, which an archive extraction does not carry; it appears on
both sides and is a property of this measurement, not of either tree.
