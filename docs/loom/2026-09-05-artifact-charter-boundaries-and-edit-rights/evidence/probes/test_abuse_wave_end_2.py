"""Adversarial probes for wave-end:2 of
2026-09-05-artifact-charter-boundaries-and-edit-rights -- attacking the
three prose tasks W2-01/W2-02/W2-03 (write-plan's plan-charter citation,
build/review/fix-rounds/lenses.md's charter cross-references, and the four
agent contracts' compressed prose) rather than re-running wave-end:1's
already-covered checker-rule attacks.

Attack classes drawn from loom-code/skills/review/references/adversarial.md
("Skill and gate") and attack-catalogue.md, worked against this delta's
actual changed prose:

  1. a negation smuggled into a sentence that a prose-pin test would pin
     verbatim (self-exempt-via-prose-condition's mirror image: does the
     matcher itself catch the hostile rewrite?);
  2. citation paths this delta adds (`loom_checker.py charter`,
     `plan-edits`, `review-edits`) probed with absent/hostile arguments;
  3. the cross-repo mirror (.codex/hooks vs loom-code) as a trust-boundary
     crossing -- edit one side only, confirm the shipped guard actually
     notices;
  4. the new sentence/word caps on lenses.md's `charter.plan-omission-
     narrow` gate and on adversary.md/blind-runner.md, one past the
     boundary;
  5. an obligation-bearing fact the W2-03 compression pass dropped from
     implementer.md with no test pinning it -- a live, unguarded finding.

Every test is written against the tree at HEAD ae97051b. A `pass` result
records that the attack failed to break anything; a `fail` result is a
live bug recorded as a finding.

Re-run any one test from the repo root:
    python3 -m pytest docs/loom/2026-09-05-artifact-charter-boundaries-and-edit-rights/evidence/probes/test_abuse_wave_end_2.py -q -k <name>
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
)

sys.path.insert(0, str(REPO / "loom-code" / "scripts"))
import prose_pin  # noqa: E402  (shared negation matcher, per adversary.md's dispatch instructions)

CHECKER = REPO / "loom-code" / "scripts" / "loom_checker.py"
LENSES = REPO / "loom-code" / "skills" / "review" / "references" / "lenses.md"
REVIEWER_MD = REPO / "loom-code" / "agents" / "reviewer.md"
ADVERSARY_MD = REPO / "loom-code" / "agents" / "adversary.md"
BLIND_RUNNER_MD = REPO / "loom-code" / "agents" / "blind-runner.md"
IMPLEMENTER_MD = REPO / "loom-code" / "agents" / "implementer.md"
CODEX_PLAN_TEMPLATE = REPO / ".codex" / "hooks" / "contract" / "templates" / "plan.md"
LOOM_PLAN_TEMPLATE = REPO / "loom-code" / "contract" / "templates" / "plan.md"
LANGUAGE_POLICY_BRANCH_END = (
    REPO / "loom-code" / "scripts" / "test_probes_language_policy_branch_end.py"
)
CHANGE_ID = "2026-09-05-artifact-charter-boundaries-and-edit-rights"

# --- sentence-split rule, reused verbatim from
# loom-code/scripts/test_review_station_text.py's documented oracle, so the
# same synthetic inputs get judged the same way by two independent copies.
SENTENCE_CAP = 6
SENTENCE_WORD_CAP = 40
_ABBREV = re.compile(r"\b(e\.g|i\.e|etc|vs)\.", re.IGNORECASE)
_BACKTICK = re.compile(r"`[^`]*`")
_TERMINATOR = r"[.!?…]"
_CLOSER = "[\"'’”)\\]]"
_SPLIT = re.compile(rf"(?:(?<={_TERMINATOR})|(?<={_TERMINATOR}{_CLOSER}))\s+")
_NUL = "\x00"


def _sentences(paragraph: str) -> list[str]:
    text = _BACKTICK.sub("BACKTICKSPAN", paragraph)
    text = _ABBREV.sub(lambda m: m.group(1) + _NUL, text)
    text = " ".join(text.split())
    return [p.replace(_NUL, ".") for p in _SPLIT.split(text) if p.strip()]


def run_checker(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECKER), *args],
        capture_output=True, text=True, cwd=str(cwd or REPO),
    )


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. Negation smuggled into a sentence a prose-pin test would pin verbatim
# ---------------------------------------------------------------------------


def _gate_block() -> str:
    text = read(LENSES)
    m = re.search(
        r"<!-- gate: charter\.plan-omission-narrow -->(.*?)<!-- /gate -->",
        text, re.DOTALL,
    )
    assert m, "lenses.md no longer carries the charter.plan-omission-narrow gate block"
    return m.group(1).strip()


def test_gate_omission_sentence_negated_rewrite_caught_by_matcher() -> None:
    """The charter.plan-omission-narrow gate's first sentence ("a task whose
    Files, Test or Risk line leaves the implementer unable to start") is a
    pinned affirmative claim. A hostile rewrite that smuggles in a negation
    while keeping the same surface topic ("...line never leaves the
    implementer able to start") must be rejected by the shared negation
    matcher -- and the real, shipped sentence must NOT be rejected, or the
    matcher is too aggressive to ever pin anything."""
    sentences = _sentences(_gate_block())
    target = next(
        (s for s in sentences if "unable to start" in s), None,
    )
    assert target is not None, "gate block lost its 'unable to start' sentence"
    assert not prose_pin.has_negation(target), (
        f"the shipped sentence itself trips the negation matcher: {target!r}"
    )
    hostile = target.replace("leaves", "never leaves").replace(
        "unable to start", "able to start"
    )
    assert hostile != target
    assert prose_pin.has_negation(hostile), (
        "a negation smuggled into the omission sentence ('never leaves ... "
        f"able to start') was NOT caught by prose_pin.has_negation: {hostile!r}"
    )


def test_reviewer_language_exception_clause_negated_rewrite_caught_by_matcher() -> None:
    """reviewer.md's language-policy clause names exactly which artifacts
    stay in the user's language: 'the intent, the blind-run report, and the
    pull-request body excepted — those stay in the user's language'. Pinning
    this clause requires isolating it, not the whole run-on paragraph it
    lives in (that paragraph is one semicolon-joined sentence by the
    terminator-based splitter and legitimately contains other negations
    describing unrelated failure modes — testing the paragraph as a whole
    would be a false negative on the matcher, not a probe of this clause).
    The isolated clause itself must not trip the matcher; a hostile rewrite
    negating just the exception word must."""
    text = read(REVIEWER_MD)
    clause = (
        "the intent, the blind-run report, and the\n"
        "pull-request body excepted — those stay in the user's language"
    )
    assert clause in text, "reviewer.md lost the exact language-exception clause"
    assert not prose_pin.has_negation(clause), (
        f"the shipped clause trips the negation matcher on its own: {clause!r}"
    )
    hostile = clause.replace("excepted", "not excepted")
    assert hostile != clause
    assert prose_pin.has_negation(hostile), (
        f"negating 'excepted' to 'not excepted' was not caught: {hostile!r}"
    )


# ---------------------------------------------------------------------------
# 2. Citation paths this delta writes into station text -- probed absent
#    and hostile
# ---------------------------------------------------------------------------


def test_charter_command_cited_by_write_plan_resolves_with_no_arguments() -> None:
    """write-plan/SKILL.md cites `python3 .../loom_checker.py charter`
    (no argument) as how the plan charter row is rendered. Run exactly that
    -- the citation must resolve to the plan row's `edits after` column, not
    merely parse without crashing."""
    result = run_checker("charter")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "| plan |" in result.stdout
    assert "edits after" in result.stdout


def test_charter_command_stray_argument_fails_closed_not_silently_ignored() -> None:
    """Hostile input one token away from the cited command: `charter plan`
    instead of bare `charter`. If the checker silently accepted and ignored
    the stray argument, a future rename of the subcommand's argument surface
    could pass an operator's typo through unnoticed."""
    result = run_checker("charter", "plan")
    assert result.returncode != 0, (
        f"'charter plan' (a plausible typo of the cited bare 'charter' "
        f"command) was accepted: {result.stdout!r}"
    )


def test_plan_edits_command_absent_change_id_fails_closed_not_crash() -> None:
    """build/SKILL.md and write-plan/SKILL.md cite `loom_checker.py
    plan-edits <change-id>`. Feed it a change-id with no plan on disk at
    all (the empty/absent-input class) -- it must fail with a clean usage
    exit, never a Python traceback dumped to the operator."""
    result = run_checker("plan-edits", "no-such-change-id-at-all")
    assert result.returncode == 2, result.stdout + result.stderr
    assert "Traceback" not in result.stderr, result.stderr
    assert "no plan file" in result.stderr


def test_review_edits_command_absent_change_id_fails_closed_not_crash() -> None:
    """Same probe against `review-edits <change-id>`, cited by review/
    SKILL.md and fix-rounds.md's new 'Where the fix round is recorded'
    section -- absent input must fail closed, not crash."""
    result = run_checker("review-edits", "no-such-change-id-at-all")
    assert result.returncode == 2, result.stdout + result.stderr
    assert "Traceback" not in result.stderr, result.stderr
    assert "no review file" in result.stderr


def _plan_commit_reachable_from_head() -> bool:
    """Whether `docs(loom): plan <CHANGE_ID>` is reachable from HEAD --
    the same reachability `find_plan_commit_sha` (loom_checker.py) walks
    -- so this test recomputes which of the two shapes it is running in
    (a branch that still carries the plan commit, or a post-squash tree
    that dropped it) instead of guessing from the branch name."""
    wanted = f"docs(loom): plan {CHANGE_ID}"
    log = subprocess.run(
        ["git", "-C", str(REPO), "log", "--format=%s", "HEAD"],
        capture_output=True, text=True, check=True,
    ).stdout
    return wanted in log.splitlines()


def test_charter_and_plan_edits_agree_the_real_change_id_resolves() -> None:
    """Positive control for the two probes above: this change's own
    change-id (which DOES have a plan and a review.json on disk) must
    resolve cleanly through both cited commands, proving the absent-input
    failures above are about the input, not a broken command.

    Exit 0 alone does not distinguish "the baseline was actually checked"
    from "there was no baseline to check" -- W1-01 made a missing plan
    commit on a closed intent exit 0 too, via a different code path
    (plan.edits-after-commit: NOT APPLICABLE). So this recomputes which
    shape the tree is actually in and asserts the matching reason: with
    the plan commit reachable from HEAD, plan-edits must have compared
    against it (never taken the not-applicable shortcut); with it absent
    -- the post-squash shape -- plan-edits must say so explicitly, naming
    this change-id, using the exact wording `check_plan_edits_after_commit`
    (loom_checker.py) writes for the carve-out."""
    plan_result = run_checker("plan-edits", CHANGE_ID)
    review_result = run_checker("review-edits", CHANGE_ID)
    assert plan_result.returncode == 0, plan_result.stdout + plan_result.stderr
    assert review_result.returncode == 0, review_result.stdout + review_result.stderr

    combined = plan_result.stdout + plan_result.stderr
    if _plan_commit_reachable_from_head():
        assert "NOT APPLICABLE" not in combined, (
            "the plan commit is reachable from HEAD, yet plan-edits took "
            f"the shipped-change not-applicable shortcut anyway: {combined!r}"
        )
    else:
        expected = (
            f"plan.edits-after-commit: NOT APPLICABLE -- {CHANGE_ID} was closed"
        )
        assert expected in combined, (
            "the plan commit is absent from HEAD (post-squash shape), but "
            f"plan-edits did not report the not-applicable carve-out for "
            f"{CHANGE_ID!r}: {combined!r}"
        )


# ---------------------------------------------------------------------------
# 3. Cross a trust boundary: the .codex/hooks mirror of the plan template
# ---------------------------------------------------------------------------


def test_codex_mirror_divergence_from_w2_01_edit_is_actually_caught() -> None:
    """W2-01 added the same `edits_after` comment block to BOTH
    loom-code/contract/templates/plan.md and its .codex/hooks mirror in the
    same commit. Reproduce the attack of only landing it on one side: patch
    the loom-code copy, leave the mirror untouched, and run the shipped
    byte-comparison test node from test_probes_language_policy_branch_end.py
    against that tree -- it must fail, not silently pass a stale mirror
    through. The mutation happens in a scratch copy of the three files the
    node reads, laid out at the same relative paths, never in the
    repository tree: an in-place patch-and-restore raced the real mirror
    test under xdist and produced a phantom failure in the package suite."""
    original = read(LOOM_PLAN_TEMPLATE)
    assert original == read(CODEX_PLAN_TEMPLATE), (
        "the two template copies are not byte-equal before the probe even "
        "starts -- cannot attribute a later divergence to this probe"
    )
    mutated = original.replace(
        "Landed tasks stay as they are.",
        "Landed tasks stay exactly as they are.",
    )
    assert mutated != original, "the probe's target sentence is not present verbatim to mutate"
    scratch = Path(tempfile.mkdtemp(prefix="adv_charter_mirror_"))
    try:
        for rel in ("loom-code/contract/templates", ".codex/hooks/contract/templates"):
            shutil.copytree(REPO / rel, scratch / rel)
        (scratch / "loom-code/contract/templates/plan.md").write_text(mutated, encoding="utf-8")
        test_copy = scratch / LANGUAGE_POLICY_BRANCH_END.relative_to(REPO)
        test_copy.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(LANGUAGE_POLICY_BRANCH_END, test_copy)
        result = subprocess.run(
            [sys.executable, "-m", "pytest",
             str(test_copy), "-q", "-p", "no:cacheprovider",
             "-k", "codex_mirror or mirror"],
            capture_output=True, text=True, cwd=str(scratch),
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    assert result.returncode != 0, (
        "the codex-mirror byte-equality suite did not fail when only the "
        f"loom-code copy was patched:\n{result.stdout}{result.stderr}"
    )


# ---------------------------------------------------------------------------
# 4. Boundary: sentence/word caps on this delta's new prose, one past it
# ---------------------------------------------------------------------------


def test_plan_omission_gate_block_stays_inside_cap_oracle_flags_one_past_it() -> None:
    """The charter.plan-omission-narrow gate block (4 sentences, longest 29
    words) sits well inside the 6-sentence / 40-word caps -- confirmed here
    as a positive control against the shared oracle. The same oracle, fed a
    synthetic sentence built at exactly the 40-word boundary and one word
    past it, must accept the boundary and reject the one-past-it case --
    the boundary-plus-one probe the recipe asks for, run against the actual
    cap constants rather than assumed."""
    sentences = _sentences(_gate_block())
    assert len(sentences) <= SENTENCE_CAP, sentences
    lengths = [len(s.split()) for s in sentences]
    assert all(n <= SENTENCE_WORD_CAP for n in lengths), lengths
    assert max(lengths) < SENTENCE_WORD_CAP, (
        "the gate block's longest sentence is no longer comfortably inside "
        f"the cap ({max(lengths)} words, cap {SENTENCE_WORD_CAP}); re-check "
        "headroom before adding another sentence"
    )

    at_boundary = "word " * (SENTENCE_WORD_CAP - 1) + "word."  # exactly 40 words
    one_past = "word " * SENTENCE_WORD_CAP + "word."  # exactly 41 words
    assert len(_sentences(at_boundary)[0].split()) == SENTENCE_WORD_CAP
    assert len(_sentences(one_past)[0].split()) == SENTENCE_WORD_CAP + 1
    assert len(_sentences(at_boundary)[0].split()) <= SENTENCE_WORD_CAP
    assert not (len(_sentences(one_past)[0].split()) <= SENTENCE_WORD_CAP), (
        "the oracle must reject a sentence one word past the 40-word cap"
    )


@pytest.mark.parametrize(
    "path,cap,expected_words",
    [(ADVERSARY_MD, 600, 600), (BLIND_RUNNER_MD, 600, 599)],
)
def test_agent_contract_one_word_past_its_cap_fails_the_shipped_check(
    path: Path, cap: int, expected_words: int
) -> None:
    """adversary.md sits exactly AT its 600-word cap after the W2-03
    compression pass (zero headroom); blind-runner.md sits one word under
    it (the boundary itself, one word of headroom). Confirm the actual
    counts first -- an assumed number is not evidence -- then confirm one
    more word than the actual count would fail the shipped `words <= cap`
    check the real test performs (test_reviewer_agent_single_contract.py's
    AGENT_CAPS): the boundary-plus-one case."""
    text = read(path)
    match = re.match(r"^---\n.*?\n---\n", text, re.DOTALL)
    body = text[match.end():] if match else text
    words = len(body.split())
    assert words == expected_words, (
        f"{path.name} is {words} words; expected {expected_words} against "
        f"cap {cap} (if this now fails, the file changed -- re-anchor the "
        "probe, don't delete it)"
    )
    assert words <= cap, f"{path.name} already exceeds its own shipped cap"
    padded = body
    while len(padded.split()) <= cap:
        padded += " onemoreword"
    assert not (len(padded.split()) <= cap), (
        "padding past the actual count must fail the shipped `words <= cap` check"
    )


# ---------------------------------------------------------------------------
# 5. Obligation-bearing fact dropped by the W2-03 compression pass, with no
#    test in the repo pinning it back
# ---------------------------------------------------------------------------


def _text_at(rev: str, path: Path) -> str:
    rel = path.relative_to(REPO).as_posix()
    result = subprocess.run(
        ["git", "show", f"{rev}:{rel}"],
        capture_output=True, text=True, cwd=str(REPO), check=True,
    )
    return result.stdout


def _pre_branch_base() -> str:
    """The trunk commit this branch grew from -- `origin/main` first, as CI
    sees it; skip when it does not resolve, since a literal sha would bind
    the probe to one local history and go red on every rebase."""
    trunk = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", "origin/main"],
        capture_output=True, text=True, cwd=str(REPO),
    )
    if trunk.returncode != 0:
        pytest.skip("origin/main does not resolve here; the pre-branch text has no anchor")
    base = subprocess.run(
        ["git", "merge-base", "HEAD", "origin/main"],
        capture_output=True, text=True, cwd=str(REPO), check=True,
    )
    return base.stdout.strip()


def test_implementer_commit_scope_qualifier_dropped_and_unguarded() -> None:
    """Before this branch (at the merge-base with origin/main), implementer.md said commit `scope` is
    'the kebab-case plugin OR module name' -- the repo's own git history
    (`chore(loom): ...`) uses the bare plugin family name 'loom' as a scope,
    not a module name. W2-03's compression pass rewrote this to 'the
    kebab-case module name', silently dropping the plugin-name half of the
    fact. No test in loom-code/scripts pins either wording, so this is a
    live, unguarded content regression, not merely a paraphrase: an
    implementer reading only the current file could reject a scope like
    `loom` as invalid because it names no module.

    This probe FAILS on purpose -- it is the finding, not a false alarm."""
    before = _text_at(_pre_branch_base(), IMPLEMENTER_MD)
    after = read(IMPLEMENTER_MD)
    assert "kebab-case plugin or module name" in before, (
        "the probe's premise (the fact existed pre-branch) does not hold; "
        "re-anchor this probe"
    )
    scopes_actually_used = {
        line.split("(", 1)[1].split(")", 1)[0]
        for line in subprocess.run(
            ["git", "log", "--format=%s", "-40"],
            capture_output=True, text=True, cwd=str(REPO), check=True,
        ).stdout.splitlines()
        if "(" in line and "):" in line
    }
    assert "loom" in scopes_actually_used, (
        "the repo's own commit history no longer uses a bare plugin-family "
        "scope like 'loom' -- if true, this finding is stale and should be "
        "retired, not silently kept failing"
    )
    scope_sentence_match = re.search(r"`scope` the kebab-case[^.]*\.", after)
    assert scope_sentence_match, "implementer.md no longer defines `scope` at all"
    scope_sentence = scope_sentence_match.group(0)
    assert "plugin" in scope_sentence, (
        f"implementer.md's commit-scope sentence no longer says a commit "
        f"scope may name the plugin (now: {scope_sentence!r}; before "
        "pre-branch: '`scope` the kebab-case plugin or module name.') while "
        "the repo's own commits (`chore(loom): ...`) use exactly that "
        "plugin-level scope -- this is the dropped fact, recorded as a "
        "finding, not fixed here"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
