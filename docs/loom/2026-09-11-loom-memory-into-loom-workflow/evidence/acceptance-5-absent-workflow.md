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

## Superseded by the blind run's measurement

The blind runner re-measured this independently and its method is better.
Extracting with `git archive` drops `.git`, so every test that shells out to
git fails for a reason that has nothing to do with the change — including one
in loom-design, which made this file report a loom-design failure that does
not exist. Copying with real worktrees (both sides keeping their `.git`) gives
the true sets:

    loom-design   before and after: 183 passed, 1 skipped — green both sides
    loom-code     before and after: 824 passed, 2 skipped, 3 failed,
                  1 collection error — same names, same messages, verbatim

Both measurements agree that nothing got worse, which is what Acceptance 5
asks. Where they disagree on the specific failure list, the blind-run report's
numbers are the ones to read; this file's list carries an artefact of its own
method. It is kept rather than deleted because the artefact is itself the
lesson: a throwaway copy made without `.git` is not the tree you think you are
testing.
