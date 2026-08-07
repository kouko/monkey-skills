"""Structural grep-test guarding the memory-store integrity checkpoint in
finishing-a-development-branch/SKILL.md.

finishing-a-development-branch/SKILL.md is a prompt artifact, not
executable code. Its correctness here is the PRESENCE of a Step 8
checkpoint: when the branch adds or edits a file under
`docs/loom/memory/`, the orchestrator runs
`check_loom_memory_integrity.py` BEFORE committing, because the store's
§Index invariant requires one index line per memory file with the
description copied byte-identical from the file's frontmatter.

Origin: the invariant was violated twice. The second time (PR #634,
2026-07-31) a new memory entry shipped without its index line, the
close-out commit went green locally, and CI failed after push under a
job name ("plugin version bump") that names a different check — so the
failure did not even point at the store. Step 8 already carries the
structurally identical living-spec index regen bullet and the
archive-on-close bullet; the memory store had no equivalent, which is
why the same miss recurred.

These checks assert on load-bearing PHRASES. They tolerate rewording
*around* those phrases, but not changes to the phrases themselves or to
the row's anchor — a one-character anchor edit turns every test in
this file red. That is deliberate for a prompt artifact whose exact
wording is the contract; it is not the same as being wording-agnostic.

Stdlib only (pathlib). Resolve SKILL.md relative to this test file.
"""

from pathlib import Path

SKILL = Path(__file__).parents[1] / "skills" / "finishing-a-development-branch" / "SKILL.md"


def _text() -> str:
    assert SKILL.is_file(), f"SKILL.md is absent at {SKILL}"
    return SKILL.read_text(encoding="utf-8")


def _integrity_row(text: str) -> str:
    """The Memory-store integrity table ROW plus the table's lead-in
    sentence — the text under guard since Step 8's five ONCE-per-branch
    checks collapsed into one close-out sub-checks table (loom arc 4b).

    The row is one physical line, so extraction is line-scoped: no radius
    window (an earlier bullet-era draft of this file was false-green from a
    ±600-char window — the neighbor above satisfied the store-path, README
    and commit assertions with the guarded text deleted outright) and no
    structural terminators to recalibrate. The lead-in line above the table
    carries the shared "orchestrator-only, ONCE per branch" scope exactly
    once for every row, so it is part of the guarded text: delete the
    lead-in and the concurrency-tag test goes red.
    """
    row_start = text.find("| Memory-store integrity |")
    assert row_start != -1, (
        'no line matching the literal anchor "| Memory-store integrity |" '
        "— the table row is either absent, renamed, or the Check-cell "
        "label changed; check which before editing the tests"
    )
    row = text[row_start:].splitlines()[0]

    lead_start = text.find("Close-out sub-checks")
    assert lead_start != -1, (
        'no "Close-out sub-checks" lead-in above the table — the sentence '
        "carrying the shared orchestrator-only / ONCE-per-branch scope is "
        "absent or renamed"
    )
    header_start = text.find("| Check |", lead_start)
    assert header_start != -1 and header_start < row_start, (
        "table header not found between the lead-in and the Memory-store "
        "integrity row — the lead-in no longer governs this table"
    )
    lead = text[lead_start:header_start]
    return lead + "\n" + row


def test_memory_integrity_step_names_the_script_with_its_path():
    """The checkpoint must name the script AND its path.

    Scoped to the bullet, not the whole file: whole-branch review proved the
    whole-file form was reachable-false-green (delete the bullet, leave the
    bare basename in any cross-reference, and this test alone stayed green).
    The path matters on its own — Step 8's living-spec bullet points at
    `loom-code/scripts/`, this checker lives at the repo root's `scripts/`,
    and a reviewer probe confirmed that swapping one for the other kept every
    assertion green."""
    row = _integrity_row(_text())

    # The full invocation, not `…/scripts/…` plus a blacklist. Whole-branch
    # review probed the loose form: `scripts/check_loom_memory_integrity.py`
    # is satisfied by ANY prefix, and barring only `loom-code/` left
    # `loom-pipeline/scripts/`, `tools/scripts/` and `../scripts/` all
    # false-green. Asserting the literal command creates a token boundary
    # that admits no prefix at all.
    assert "python3 scripts/check_loom_memory_integrity.py" in row, \
        "must name the full repo-root invocation, admitting no path prefix"
    # "from the repo root", not "repo root": the bullet also says the script
    # "lives at the monkey-skills repo root", so the bare token was satisfied
    # by that sentence and deleting the cwd qualifier left every test green.
    # Fourth instance of this class in one branch — pin the phrase the failure
    # message names, never a token that merely occurs in the bullet.
    assert "from the repo root" in row, \
        "a relative script path is only correct with its cwd qualifier stated"


def test_memory_integrity_step_handles_the_script_being_absent():
    """This skill ships as a distributed plugin, but the checker exists only
    in this repo. `loom-pipeline:loom-memory` fires in ANY repo carrying
    `docs/loom/memory/README.md`, so a consuming repo can satisfy this
    row's trigger with no such script present — where the command exits
    nonzero for "No such file" and the row's own "exit 0 is the gate"
    rule would convert that into a phantom store violation.

    Both sibling Step 8 rows name their not-applicable case; this one
    must too."""
    row = _integrity_row(_text())
    low = row.lower()

    # The exact line, not `"n/a" or "absent" or "not present"`. That OR was
    # this test's first form and it survived deleting the whole N/A sentence,
    # because a later rewrite happened to use the word "absent" in the
    # *condition* ("If that path is absent") — leaving the OR satisfied while
    # the prescribed output was gone.
    assert "memory-store integrity: n/a" in low, \
        "must prescribe the exact loud N/A line, not merely mention absence"
    assert "no such file" in low, \
        "must tell the reader not to read a missing-file nonzero as a violation"


def test_memory_integrity_step_carries_the_concurrency_tag():
    """The row's failure action edits `docs/loom/memory/README.md`, so it
    must not run in a parallel wave. The sibling this file mirrors pins the
    same clause (`test_finishing_archive_step.py` asserts `orchestrator-only`
    in its own window); whole-branch review caught that the docs arm restored
    this clause while the test arm did not follow it."""
    row = _integrity_row(_text())
    low = row.lower()

    assert "orchestrator-only" in low, \
        "must carry the orchestrator-only tag its siblings carry"
    assert "once per branch" in low, \
        "must state the once-per-branch scope, not just the actor"


def test_memory_integrity_step_states_the_failure_action():
    """Stating the pass condition is not enough. Step 9b, the nearest
    can-fail gate, spells out its failure action ("STOP … Do NOT push"); a
    weak orchestrator that sees exit 1, notes it, and commits anyway is not
    contradicted by a row that only says what passing looks like."""
    row = _integrity_row(_text())
    low = row.lower()

    assert "nonzero" in low or "non-zero" in low, \
        "must name the failure condition explicitly"
    assert "do not commit" in low or "before committing" in low, \
        "must say what NOT to do on a violation, not only what passing means"
    # The checker validates the WORKING TREE, so exit 0 alone does not mean the
    # commit is clean: fixing the index line and forgetting to stage it ships
    # the very defect this row guards, while passing its own gate.
    assert "git add" in low, \
        "must tell the reader to stage the corrected file, not just fix it"


def test_memory_integrity_step_gated_on_touching_the_store():
    """The checkpoint fires when the branch touched docs/loom/memory/ —
    not unconditionally, and not only on brand-new files (an edited
    description must stay byte-identical to its index line too)."""
    row = _integrity_row(_text())
    low = row.lower()

    # The trigger CLAUSE, not the bare store path — that substring occurs three
    # times in the bullet (the parallel-wave clause and the §Index sentence both
    # satisfy it), so pinning it left the trigger condition of a *conditional*
    # checkpoint unguarded.
    assert "added or edited a file under `docs/loom/memory/`" in row, \
        "must name the trigger clause, not merely mention the store path"
    assert "index" in low, \
        "must reference the §Index invariant the check enforces"
    assert "added or edited" in low, \
        "must fire on edits too, not only on newly added memory files"


def test_memory_integrity_step_states_when_it_does_not_fire():
    """A conditional step that never says when it is N/A gets run as a
    ritual or skipped silently. The row must name the skip case."""
    row = _integrity_row(_text())
    low = row.lower()

    assert "skip" in low, \
        "must state the skip case explicitly"
    assert "fires only when" in low, \
        "must scope the trigger, not read as unconditional"


def test_memory_integrity_step_states_the_index_line_duty():
    """Naming the script is not enough — the reader must know the fix is a
    README §Index line whose description matches the frontmatter, which is
    the specific invariant that was violated twice."""
    row = _integrity_row(_text())
    low = row.lower()

    assert "readme" in low, \
        "must point at README.md as where the index line goes"
    assert "description" in low, \
        "must state that the index line carries the frontmatter description"
    # The run-instruction phrasing, not the bare token: adding invariant (d) to
    # the failure enumeration put a second "byte-identical" in the bullet, which
    # disarmed this assertion — deleting the load-bearing sentence left every
    # test green. Updated for the generated-index reality (loom arc 3, D1): the
    # index line is no longer hand-copied, it is generated from frontmatter, but
    # the byte-identical invariant itself is unchanged.
    assert "frontmatter `description`, byte-identical" in row, \
        "must state the description is byte-identical to the file's frontmatter, not paraphrased"


def test_memory_integrity_step_runs_before_the_commit():
    """The check must run BEFORE committing. Running it after is what CI
    already does — the point of the checkpoint is to catch it locally.

    Asserts the full phrase, not `"before" in text or "commit" in text`:
    that OR was the first draft's wording and both words are common
    enough in Step 8 that it could not fail."""
    row = _integrity_row(_text())
    low = row.lower()

    assert "before" in low and "close-out commit" in low, \
        "must place the check before the close-out commit"
    assert "exit 0" in low, \
        "must state what passing looks like, not just what to run"
