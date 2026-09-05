"""wave-end:1 adversarial probes for 2026-09-05-user-declared-express-lane.

These attack what `test_abuse_lane_declaration.py` (the W0-01 floor, 11
cases, all green at HEAD) does not: the classification machinery
`_lane_forcing_paths`/`effective_lane_detail` actually leans on
(`_artifact_type_for`'s glob order), the round-timing discipline the
switch-suffix grammar is supposed to buy, the checker's OWN split between
`push` and the separate `intent` subcommand, and one of this wave's own
new prose pins.

Each case is `command_names_artifact`/`same_reviewed_content`-real: a real
git repo per test, `push`/`intent` invoked via subprocess against THIS
tree's `loom_checker.py`, exactly like `test_abuse_lane_declaration.py`
and `test_loom_checker_push.py`. Cases marked `# RED at HEAD: <id>` assert
the CORRECT invariant and currently fail -- they are regression pins for
whichever round closes the finding, not throwaway pokes. Cases with no
such marker are GREEN: an attack this file tried and the checker held.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

# file: docs/loom/2026-09-05-user-declared-express-lane/evidence/probes/<this>.py
# parents: [0]=probes [1]=evidence [2]=<change-id> [3]=loom [4]=docs [5]=repo root
REPO_ROOT = Path(__file__).resolve().parents[5]
PROBES_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT / "loom-code" / "scripts"))
sys.path.insert(0, str(PROBES_DIR))

import loom_checker as lc  # noqa: E402
from prose_pin import NEGATION_RE  # noqa: E402
from test_loom_checker_push import (  # noqa: E402
    PASSING_COMMAND,
    blocked_rules,
    git,
    run_checker,
)
from test_loom_checker_intent import (  # noqa: E402
    make_repo as make_intent_repo,
)
from test_abuse_lane_declaration import (  # noqa: E402
    _adversarial_records,
    _commit_intent,
    _commit_review,
    _dispatch,
    _lane_intent_text,
    _package_tests_record,
    _seed_branch,
    _verdict,
    _write,
    _write_evidence,
    _write_kickoff,
    _write_review,
)

CHECKER = REPO_ROOT / "loom-code" / "scripts" / "loom_checker.py"
LANE_SWITCH = REPO_ROOT / "loom-code/skills/review/references/lane-switch.md"


# =============================================================================
# Class 1 -- agent self-declaration, RETARGETED (fix round for wave-end:1-01
# landed since this file's first draft): `LANE_GRAMMAR` now makes the
# suffix (`declared <date> by <name>` or `switched <date> by <name>,
# from ...`) MANDATORY for every value, not just the switch form -- a
# bare `lane: express` with no suffix at all is no longer schema-valid,
# closing the gap this probe used to pin as "reader-trusted by design".
# Current correct invariant, and GREEN today: a bare declaration, agent-
# authored or not, is now rejected outright.
# =============================================================================


def test_intent_bare_lane_declaration_by_agent_confirmation_commit_currently_unchecked(
    tmp_path: Path,
) -> None:
    """A bare `lane: express` line (no `declared`/`switched` suffix at
    all) written and committed in the same commit that confirms the
    intent must now be rejected by `intent`'s schema check --
    wave-end:1-01's dated-attribution requirement applies to the day-one
    form too, not only a mid-flight switch, closing the gap this probe
    used to document as an accepted, reader-trusted design choice."""
    repo = make_intent_repo(tmp_path)
    change_id = "2026-09-05-lane-self-declare"
    intent_rel = f"docs/loom/intent/{change_id}.md"
    _write(repo, intent_rel, _lane_intent_text(change_id, lane_line="lane: express"))
    git(repo, "add", intent_rel)
    message = (
        "docs(loom): add an intent\n\n"
        "needs-design: no — no interface surface touched\n"
        "lane: express"
    )
    git(repo, "commit", "-q", "-m", message)

    result = run_checker("intent", str(repo / intent_rel), cwd=repo)
    assert result.returncode != 0, (
        "a bare `lane: express` declaration -- no dated-attribution suffix "
        f"at all -- must be schema-invalid now; it passed instead: {result.stdout}"
    )


# =============================================================================
# Class 2 -- forbidden-type evasion. `_lane_forcing_paths` classifies each
# changed path via `_artifact_type_for`, which walks `manifest.yaml`'s
# `artifact_types` list and returns the FIRST glob that matches. That list
# puts `**/evidence/**` (line 159) BEFORE `**/SKILL.md` (160) and
# `**/hooks/**`/`**/scripts/check_*` (162-163) -- so any path with an
# `evidence` directory component ANYWHERE outside this change's own store
# folder (the only thing `_small_lane_record_patterns` strips) is
# classified `evidence`, a lane-safe type, no matter what the file
# actually is. RED at HEAD: skill-gate-evidence-glob-precedence.
# =============================================================================


def test_push_gateonly_declared_skill_path_hidden_under_evidence_glob_incorrectly_passes(
    tmp_path: Path,
) -> None:
    """The exact fixture of the existing probe (d) -- a `lane: gate-only`
    intent, a SKILL.md path in the delta, zero readers -- except the
    SKILL.md sits one directory deeper, under an `evidence/` segment that
    is no part of this change's own store folder
    (`loom-code/skills/example/evidence/SKILL.md`). `_artifact_type_for`
    matches `**/evidence/**` before `**/SKILL.md`, so `_lane_forcing_
    paths` never adds it to its `skill` list -- gate-only's own
    ineligibility for a skill/agent-contract path (probe (d)) is silently
    defeated by moving the same file one level deeper.
    # RED at HEAD: skill-gate-evidence-glob-precedence
    """
    repo = _seed_branch(tmp_path)
    change_id = "2026-09-05-lane-evidence-skill"
    _write(repo, f"docs/loom/intent/{change_id}.md",
           _lane_intent_text(change_id, lane_line="lane: gate-only"))
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", "docs(loom): add the intent")
    _write_kickoff(repo)
    _write(repo, "docs/notes.md", "some notes\n")
    _write(
        repo,
        "loom-code/skills/example/evidence/SKILL.md",
        "---\nname: example\n---\nbody\n",
    )
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat(loom-code): a disguised skill delta\n\nTask: T1")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    kind = lc._artifact_type_for(
        lc.load_manifest(), "loom-code/skills/example/evidence/SKILL.md"
    )
    assert kind == "evidence", f"classification pin: got {kind!r}"

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [],
        "probes": [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)],
        "open_findings": [],
        "dispatch": [
            _dispatch("implementer", "agent-imp", "T1"),
            _dispatch("adversary", "agent-adv", "T1"),
        ],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode != 0, (
        "a skill-typed path hidden under an `evidence/` directory segment "
        "must still force the full lane and block zero readers, exactly "
        f"like a plain SKILL.md path does (probe (d)); it did not: exit "
        f"{result.returncode}, {result.stdout}"
    )
    assert "push.verdicts-ge-2" in blocked_rules(result)


def test_push_express_declared_gate_script_hidden_under_evidence_glob_incorrectly_passes(
    tmp_path: Path,
) -> None:
    """A `lane: express` intent whose delta touches a real gate-typed path
    (`**/scripts/check_*` -- non-test code that must force the full lane
    under EVERY lane, per plan W1-02 and the intent's own constraint "gate
    類 delta 永遠 full") -- but the file sits under an `evidence/`
    directory segment (`loom-code/scripts/evidence/check_bypass.py`).
    `_artifact_type_for` again matches `**/evidence/**` first, so this
    path is never added to `_lane_forcing_paths`' `hard` list at all --
    the one guarantee this whole feature rests on ("checker 守著其他所有
    東西，它自己不走快車道") is defeated by the same directory trick.
    # RED at HEAD: skill-gate-evidence-glob-precedence
    """
    repo = _seed_branch(tmp_path)
    change_id = "2026-09-05-lane-evidence-gate"
    _write(repo, f"docs/loom/intent/{change_id}.md",
           _lane_intent_text(change_id, lane_line="lane: express"))
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", "docs(loom): add the intent")
    _write_kickoff(repo)
    _write(repo, "docs/notes.md", "some notes\n")
    _write(
        repo,
        "loom-code/scripts/evidence/check_bypass.py",
        "def check_bypass():\n    return True\n",
    )
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat(loom-code): a disguised gate script\n\nTask: T1")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    kind = lc._artifact_type_for(
        lc.load_manifest(), "loom-code/scripts/evidence/check_bypass.py"
    )
    assert kind == "evidence", f"classification pin: got {kind!r}"

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [_verdict("agent-rev", 1, "branch-end", reviewed_sha)],
        "probes": [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)],
        "open_findings": [],
        "dispatch": [
            _dispatch("implementer", "agent-imp", "T1"),
            _dispatch("reviewer", "agent-rev"),
        ],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode != 0, (
        "a gate-typed script hidden under an `evidence/` directory segment "
        "must still force the full lane and block one reviewer, exactly "
        f"like the plain checker-code case (probe (b)); it did not: exit "
        f"{result.returncode}, {result.stdout}"
    )
    assert "push.verdicts-ge-2" in blocked_rules(result)


# =============================================================================
# Class 3 -- switch-line forgery.
# =============================================================================


def test_intent_lane_full_explicit_revert_rejected_by_schema(tmp_path: Path) -> None:
    """The intent (Proposed outcome point 1) says reverting to `full` is
    "隨時可以，同樣一行" -- always possible, with the same [kind of] line.
    But `LANE_GRAMMAR`'s `name` group only ever matches `express` or
    `gate-only` -- `full` is not a legal value, switch-suffixed or not.
    An explicit `lane: full — switched <date> by <name>, from round <n>`
    line, exactly mirroring the accepted express/gate-only switch form,
    is rejected by `check_lane_schema` -- the one written-line revert path
    the intent promises does not exist; only silently deleting the
    `lane:` line (which carries no `by <name>`/`from round` provenance
    and applies with no round deferral at all, see the next case) does.
    # RED at HEAD: lane-full-revert-not-in-grammar
    """
    repo = make_intent_repo(tmp_path)
    change_id = "2026-09-05-lane-revert-full"
    intent_rel = f"docs/loom/intent/{change_id}.md"
    switch_line = "lane: full — switched 2026-09-06 by kouko, from round 3"
    _write(repo, intent_rel, _lane_intent_text(change_id, lane_line=switch_line))
    git(repo, "add", intent_rel)
    message = (
        "docs(loom): revert to full\n\n"
        "needs-design: no — no interface surface touched\n"
        f"{switch_line}"
    )
    git(repo, "commit", "-q", "-m", message)

    result = run_checker("intent", str(repo / intent_rel), cwd=repo)
    assert result.returncode == 0, (
        "an explicit `lane: full` switch line, matching the accepted "
        "express/gate-only switch grammar in every other respect, should "
        f"be a legal way to revert to full; it is rejected instead: {result.stderr}"
    )


def test_push_lane_declaration_honoured_without_commit_message_linkage_or_round_deferral(
    tmp_path: Path,
) -> None:
    """`check_lane_schema`/`check_lane_reason` (the "commit message must
    carry the line verbatim" discipline `check_needs_design_reason`
    lends the `lane:` line) run ONLY under the separate `intent`
    subcommand -- `cmd_push` never calls either. So `push` honours
    WHATEVER `lane:` line the intent's raw text carries at `reviewed_sha`,
    with no check that any commit ever stated it, and no timing gate at
    all when the line carries no switch suffix (`declared_lane`'s
    `from_round` is `None` for a bare form). This probe adds a bare
    `lane: express` line at round 3 -- after two full rounds already ran
    with two readers each on a delta with no gate/skill path at all -- via
    a commit whose message says nothing about lane, and shows `push` drops
    straight to a floor of one on the very round already in flight, with
    no `from round` deferral and no record that anyone ever wrote this
    line down.
    # RED at HEAD: push-never-enforces-lane-commit-linkage-or-deferral
    """
    repo = _seed_branch(tmp_path)
    change_id = "2026-09-05-lane-silent-drop"
    _write(repo, f"docs/loom/intent/{change_id}.md",
           _lane_intent_text(change_id, lane_line=None))
    _write_kickoff(repo)
    _write(repo, "docs/notes.md", "wave-end:1 delta\n")
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): wave-end:1 delta\n\nTask: T1")

    # Round 3: a bare `lane: express` line, committed with a message
    # that never mentions "lane" at all -- the linkage discipline the
    # sibling `intent` subcommand would enforce is simply never invoked
    # here, because `push` does not call it.
    text = (repo / f"docs/loom/intent/{change_id}.md").read_text(encoding="utf-8")
    text = text.replace(
        "needs-design: no — no interface surface touched\n",
        "needs-design: no — no interface surface touched\nlane: express\n",
    )
    (repo / f"docs/loom/intent/{change_id}.md").write_text(text, encoding="utf-8")
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", "docs(loom): tidy up the intent wording")

    _write(repo, "docs/more-notes.md", "after the silent drop\n")
    git(repo, "add", "docs/more-notes.md")
    git(repo, "commit", "-q", "-m", "docs: after the silent drop\n\nTask: T1")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [
            _verdict("r1", 1, "wave-end:1", reviewed_sha),
            _verdict("r2", 1, "wave-end:1", reviewed_sha),
            _verdict("r1", 2, "wave-end:1", reviewed_sha),
            _verdict("r2", 2, "wave-end:1", reviewed_sha),
            _verdict("r3", 3, "branch-end", reviewed_sha),
        ],
        "probes": [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)],
        "open_findings": [],
        "dispatch": [
            _dispatch("implementer", "agent-imp", "T1"),
            _dispatch("reviewer", "r1"),
            _dispatch("reviewer", "r2"),
            _dispatch("reviewer", "r3"),
        ],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode != 0, (
        "round 3 is the round that FIRST introduces `lane: express`, with "
        "no switch-suffix deferral and no commit stating the line at all "
        "-- the correct invariant is that this round still owes its "
        "pre-switch floor of two readers, deferring to round 4 onward; "
        f"push accepted one reader instead: {result.stdout}"
    )
    assert "push.verdicts-ge-2" in blocked_rules(result)


def test_intent_switch_commit_message_with_unrelated_file_changes_still_passes(
    tmp_path: Path,
) -> None:
    """The mirror check for the risk named in plan W1-01: a switch
    commit's message carrying the `lane:` line verbatim is accepted even
    when that SAME commit also touches an unrelated file --
    `check_lane_reason` only requires the line's presence in the message,
    the same discipline `check_needs_design_reason` already applies to
    `needs-design:`/`status:` combined-purpose commits. GREEN: this is
    the agent-decided design, not a hole."""
    repo = make_intent_repo(tmp_path)
    change_id = "2026-09-05-lane-mixed-commit"
    intent_rel = f"docs/loom/intent/{change_id}.md"
    switch_line = "lane: express — switched 2026-09-05 by kouko, from round 2"
    _write(repo, intent_rel, _lane_intent_text(change_id, lane_line=switch_line))
    _write(repo, "docs/unrelated.md", "an unrelated file touched in the same commit\n")
    git(repo, "add", "-A")
    message = (
        "docs(loom): switch lane and tidy a note\n\n"
        "needs-design: no — no interface surface touched\n"
        f"{switch_line}"
    )
    git(repo, "commit", "-q", "-m", message)

    result = run_checker("intent", str(repo / intent_rel), cwd=repo)
    assert result.returncode == 0, (
        "a switch commit carrying the `lane:` line verbatim should pass "
        f"even with an unrelated file also touched: {result.stderr}"
    )


# =============================================================================
# Class 4 -- zero-verdict round laundering. Gate-only's floor of 0 must
# not turn into "the whole push gate is a rubber stamp" -- every other
# push rule still runs against a zero-verdict round.
# =============================================================================


def _gateonly_docs_delta_repo(tmp_path: Path, change_id: str):
    repo = _seed_branch(tmp_path)
    _commit_intent(repo, change_id, lane_line="lane: gate-only")
    _write_kickoff(repo)
    _write(repo, "docs/notes.md", "some notes, no code or skill touched\n")
    return repo


def test_push_gateonly_missing_package_tests_probe_still_blocked(tmp_path: Path) -> None:
    """A gate-only round with >=3 adversarial probes but NO package-tests
    probe recorded -- `push.probes-package-tests` is unconditional on the
    lane, and it must still block a zero-verdict round exactly like a
    full-lane one. GREEN: the floor of 0 readers is not a floor of 0
    everywhere."""
    repo = _gateonly_docs_delta_repo(tmp_path, "2026-09-05-lane-no-pkgtests")
    change_id = "2026-09-05-lane-no-pkgtests"
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs: pure docs delta")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [],
        "probes": [*_adversarial_records(reviewed_sha)],  # no package-tests entry
        "open_findings": [],
        "dispatch": [_dispatch("adversary", "agent-adv", "T1")],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode != 0, (
        "a gate-only, zero-verdict round with no package-tests probe must "
        f"still be blocked; it passed instead: {result.stdout}"
    )
    assert "push.probes-package-tests" in blocked_rules(result)


def test_push_gateonly_dismissal_by_undispatched_name_still_blocked(tmp_path: Path) -> None:
    """A gate-only round dismisses an open finding "by" a name that was
    never dispatched as a reviewer/blind-runner/adversary at all (a
    plain, unverifiable "by someone") -- `check_dismissed_by_reviewer`
    must still block this with zero readers on the board, the same as a
    full-lane round would. GREEN: gate-only widens who may dismiss
    (adversary counts) but never removes the requirement that whoever
    dismissed it is dispatched."""
    repo = _gateonly_docs_delta_repo(tmp_path, "2026-09-05-lane-bad-dismiss")
    change_id = "2026-09-05-lane-bad-dismiss"
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs: pure docs delta")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [],
        "probes": [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)],
        "open_findings": [
            {"id": "F1", "dismissed": "not applicable by ghost-reviewer"}
        ],
        "dispatch": [_dispatch("adversary", "agent-adv", "T1")],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode != 0, (
        "a gate-only round dismissing a finding by a never-dispatched name "
        f"must still be blocked; it passed instead: {result.stdout}"
    )
    assert "push.dismissed-by-reviewer" in blocked_rules(result)


def test_push_gateonly_pure_docs_delta_zero_adversarial_probes_still_passes(
    tmp_path: Path,
) -> None:
    """RETARGETED to the ratified shape: a raw-small, purely small-lane-
    safe delta (docs only, no KICKOFF/standing-doc touch, so it is never
    forced to `full` in the first place) with a DATED `lane: gate-only`
    declaration, ONE reviewer verdict (satisfies whichever floor applies
    today -- small's 1 -- so the reviewer count itself is never the
    reason this blocks), zero verdicts is NOT what is tested here on
    purpose: `check_probes_adversarial`'s own floor is unconditional for
    `express`/`gate-only` (finding 4, already fixed) regardless of the
    delta's own §6 types -- the intent's "仍有 ≥3 探針" is unconditional
    for gate-only. Today, with the raw-small short-circuit still in
    place, this delta's effective lane is `small`, not `gate-only` --
    `lane_unconditional` never fires, `kinds` is empty (pure docs), so the
    adversarial floor is never required and `push` passes despite zero
    probes recorded. Once the ratified rule lands (raw small + declared
    gate-only -> gate-only), this same delta's effective lane becomes
    `gate-only`, which DOES make the floor unconditional -- `push` should
    then block on `push.probes-adversarial`.
    # RED at HEAD: raw-small-does-not-defer-to-declared-gate-only
    """
    repo = _seed_branch_with_kickoff(tmp_path)
    change_id = "2026-09-05-lane-no-probes"
    lane_line = "lane: gate-only — declared 2026-09-05 by kouko"
    _write(repo, f"docs/loom/intent/{change_id}.md",
           _lane_intent_text(change_id, lane_line=lane_line))
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", "docs(loom): add the intent")
    _write(repo, "docs/notes.md", "a purely small-lane-safe delta, no probes\n")
    (repo / "evidence").mkdir(exist_ok=True)
    (repo / "evidence/tests.txt").write_text("1 passed\n", encoding="utf-8")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs: raw-small delta, zero adversarial probes")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    raw_lane, _raw_reason = lc.change_lane_detail(repo, reviewed_sha)
    assert raw_lane == "small", (
        f"fixture check: expected the recompute itself to already say "
        f"small, got {raw_lane!r}"
    )

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [_verdict("agent-rev", 1, "branch-end", reviewed_sha)],
        "probes": [_package_tests_record(reviewed_sha)],  # no adversarial entries at all
        "open_findings": [],
        "dispatch": [_dispatch("reviewer", "agent-rev", "T1")],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode != 0, (
        "gate-only's own stated invariant is >=3 adversarial probes always; "
        "with a dated gate-only declaration on a raw-small delta, this "
        f"should block on push.probes-adversarial; it passed instead: {result.stdout}"
    )
    assert "push.probes-adversarial" in blocked_rules(result)


# =============================================================================
# Class 5 -- floor arithmetic, RETARGETED to the ratified shape (coordinator
# message on the standing-doc observation): under the ratified rule, a
# raw-small delta PLUS a declared gate-only IS the gate-only lane, floor 0
# -- gate-only IS the small lane with reviewers waived when the user asks
# for it, not a separate, narrower thing. The OLD invariant this test used
# to pin ("recomputed small always wins, floor stays 1") is exactly what
# the ratification reverses; keeping the old name/assertion here would pin
# the wrong future. `effective_lane_detail` still returns `"small"`
# unconditionally on `raw_lane == "small"` today (the short-circuit this
# probe used to describe), which is why this is RED at HEAD.
# =============================================================================


def test_push_declared_gate_only_overrides_recomputed_small_floor_zero(
    tmp_path: Path,
) -> None:
    """A delta that is entirely small-lane-safe (one plugin dir, no
    standing-document touch, no interface surface, only a docs file --
    KICKOFF-DEFAULTS.md exists only on `main`, before the branch, so it is
    never part of the diff) with a DATED `lane: gate-only` declaration and
    ZERO verdicts, but >=3 adversarial probes and a package-tests probe
    recorded. Per the ratified small-lane-classes rule: raw recompute is
    `small`; the effective declaration is `gate-only`; a raw-`small` delta
    with a `gate-only` declaration IS the `gate-only` lane, floor 0 -- so
    `push` should exit 0. It does not: `effective_lane_detail` still
    returns `"small"` (floor 1) unconditionally the moment the raw
    recompute says small, before ever consulting the declared lane, so
    zero verdicts still blocks on `push.verdicts-ge-2`.
    # RED at HEAD: raw-small-does-not-defer-to-declared-gate-only
    """
    repo = _seed_branch_with_kickoff(tmp_path)
    change_id = "2026-09-05-lane-small-gateonly"
    lane_line = "lane: gate-only — declared 2026-09-05 by kouko"
    _write(repo, f"docs/loom/intent/{change_id}.md",
           _lane_intent_text(change_id, lane_line=lane_line))
    git(repo, "add", f"docs/loom/intent/{change_id}.md")
    git(repo, "commit", "-q", "-m", "docs(loom): add the intent")
    # No KICKOFF-DEFAULTS.md touch in this diff at all -- committed only
    # on `main` before the branch existed -- so the recompute sees a
    # single plugin-free docs file and nothing else: genuinely raw-small.
    _write(repo, "docs/notes.md", "a purely small-lane-safe delta\n")
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs: a small-lane-safe delta")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    raw_lane, _raw_reason = lc.change_lane_detail(repo, reviewed_sha)
    assert raw_lane == "small", (
        f"fixture check: expected the recompute itself to already say "
        f"small, got {raw_lane!r}"
    )

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [],
        "probes": [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)],
        "open_findings": [],
        "dispatch": [_dispatch("adversary", "agent-adv", "T1")],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, (
        "a raw-small delta with a dated `lane: gate-only` declaration "
        "should be the gate-only lane (floor 0) and pass with zero "
        f"verdicts; it was blocked instead: {result.stdout}"
    )


# =============================================================================
# Class 6 -- station text. `test_lane_switch_reference.py`'s own
# `test_forbidden_option_listed_with_its_reason` checks for the SUBSTRINGS
# "stays listed" and "reason" in one sentence, never for the absence of a
# negation token in that sentence -- unlike every OTHER new pin this wave
# added (`test_review_station_text.py`, `test_build_station_text.py`,
# `test_ship_station_text.py`), which all import `prose_pin.NEGATION_RE`.
# A hostile rewrite that keeps both substrings while inverting the
# sentence's meaning passes that check regardless.
# =============================================================================


def _forbidden_reason_sentences(text: str) -> list[str]:
    """Reproduces test_lane_switch_reference.py:66-78's own matching
    logic verbatim, so this probe exercises exactly what that test
    checks -- not a paraphrase of it."""
    start = text.index("## The three-option prompt")
    end = text.index("## The switch-line grammar")
    block = text[start:end]
    flat = " ".join(block.split())
    return [
        s for s in re.split(r"(?<=[.!?])\s+", flat)
        if "stays listed" in s.lower() and "reason" in s.lower()
    ]


def test_lane_switch_forbidden_reason_pin_rejects_hostile_negated_rewrite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The correct invariant: a prose pin on the "stays listed ... its
    reason" sentence must reject a hostile rewrite that keeps both
    required substrings ("stays listed", "reason") while NEGATING the
    sentence's actual meaning -- exactly the affirmative-verb-plus-no-
    negation-token discipline `prose_pin.NEGATION_RE` exists for, and
    every OTHER new pin this wave added
    (`test_review_station_text.py`, `test_build_station_text.py`,
    `test_ship_station_text.py`) already applies via that shared module.
    This probe runs `test_lane_switch_reference.py`'s OWN
    `test_forbidden_option_listed_with_its_reason` -- unmodified, via
    monkeypatch on its module-level `LANE_SWITCH` path -- against a
    temp file holding the hostile rewrite, and expects it to fail loudly.
    # RED at HEAD: lane-switch-reason-pin-no-negation-guard
    """
    import test_lane_switch_reference as ref_test  # noqa: E402 (loom-code/scripts)

    text = LANE_SWITCH.read_text(encoding="utf-8")
    honest_hits = _forbidden_reason_sentences(text)
    assert honest_hits, "fixture check: the real file must carry the honest sentence"
    assert not any(NEGATION_RE.search(s) for s in honest_hits), (
        "fixture check: the real sentence must itself carry no negation token"
    )

    hostile = text.replace(
        "The option this change's delta forbids stays listed, with its "
        "reason\nnamed beside it — a checker, hook, agent-contract or "
        "`SKILL.md` path in\nthe delta forbids `gate-only`; any `gate`-typed "
        "path forbids both\n`express` and `gate-only`. Dropping the "
        "forbidden option from the list\nwould hide the trade-off instead "
        "of naming it.",
        "The option this change's delta forbids never really stays listed, "
        "and no reason is shown beside it at all — nobody names why.",
    )
    assert hostile != text, "fixture check: the replacement must actually apply"
    hostile_hits = _forbidden_reason_sentences(hostile)
    assert hostile_hits and any(NEGATION_RE.search(s) for s in hostile_hits), (
        "fixture check: the hostile rewrite must trip the substring match "
        "while itself carrying a negation token, or this probe proves nothing"
    )

    # Written under tmp_path, never under the repo tree (this probe file
    # touches nothing outside its own evidence/probes/ directory itself).
    hostile_path = tmp_path / "hostile_lane_switch.md"
    hostile_path.write_text(hostile, encoding="utf-8")
    monkeypatch.setattr(ref_test, "LANE_SWITCH", hostile_path)
    with pytest.raises(AssertionError):
        ref_test.test_forbidden_option_listed_with_its_reason()


# =============================================================================
# Class 7 -- codex mirror and --list-rules.
# =============================================================================


def test_ship_skill_word_count_matches_plan_claim_measured_with_python_split() -> None:
    """The plan (`docs/loom/2026-09-05-user-declared-express-lane/plan.md`
    Current State Evidence, Boundary line) claims
    `ship/SKILL.md: 3,475 of 3,500` words before W1-04's edit and settles
    at 3,497 after it -- word counting here MUST use
    `len(text.split())` (never `wc`, which is not portable across BSD/GNU
    -- repo memory `feedback_wc_word_count_never_portable_use_python_
    split`). This probe measures the shipped file directly and pins the
    result at HEAD so a future edit that silently exceeds 3,500 is caught
    here rather than only at CI."""
    text = (REPO_ROOT / "loom-code/skills/ship/SKILL.md").read_text(encoding="utf-8")
    count = len(text.split())
    assert count <= 3500, f"ship/SKILL.md is over its 3,500-word cap: {count}"
    assert count == 3497, f"pinned word count drifted: expected 3497, got {count}"


def test_codex_hooks_loom_checker_mirror_passes_sync_check() -> None:
    """`.codex/hooks/loom_checker.py` mirrors
    `loom-code/scripts/loom_checker.py` (plus a version-stamp header line
    the sync tool itself adds, so this is deliberately NOT a naive byte
    comparison -- a first attempt at this probe asserted pure byte
    identity and false-positived on that header) -- the actual SSOT is
    `scripts/sync_codex_manifests.py --check --all`, which this probe
    runs directly rather than re-deriving its own notion of "in sync"."""
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts/sync_codex_manifests.py"),
         "--check", "--all"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, (
        "the codex mirror of loom_checker.py (and its sibling manifests) "
        f"has drifted from the loom-code source of truth: {result.stdout}{result.stderr}"
    )


# =============================================================================
# Fix-round follow-up (029925d0) -- finding 2's remaining shape. The fix
# added `_earlier_rounds`/`effective_lane_detail`'s `earlier_rounds`
# parameter: a bare declaration defers to the round strictly after the
# highest round number `review["verdicts"]` has EVER recorded, of any
# scope. That closes the same-checkpoint case (probe above, round 3
# mid-wave-end). But round numbers RESTART at every new checkpoint
# (`latest_round`'s own docstring, the "memory-step gotcha") -- so a bare
# declaration introduced at ROUND 1 of a NEW checkpoint, right after an
# earlier checkpoint already ran two full rounds, compares its
# `round_number` (1, freshly restarted) against `earlier_rounds` (`{1,
# 2}`, from the PRIOR checkpoint) with plain `<`: nothing in `{1, 2}` is
# less than 1, so the deferral never triggers and the bare declaration
# applies immediately to that first round of the new checkpoint -- the
# exact bug finding 2 named, surviving under the checkpoint boundary
# instead of the mid-checkpoint round count.
# =============================================================================


def test_push_bare_lane_declaration_at_new_checkpoint_round_one_skips_deferral(
    tmp_path: Path,
) -> None:
    """wave-end:1 runs two full rounds (two readers each, round 1 and 2).
    A bare `lane: express` line is then introduced by a commit that never
    mentions it, and branch-end's OWN round 1 (numbers restart per
    checkpoint) carries just one reviewer. Real review history precedes
    this declaration -- it is not a day-one declaration -- so the correct
    invariant is the same as the mid-checkpoint case: this round still
    owes the pre-declaration floor of two readers, deferring to branch-end
    round 2 onward. `push` accepts one reviewer instead, because
    `_earlier_rounds`' plain `<` comparison cannot see across the
    checkpoint boundary where round numbers reset.
    # RED at HEAD: push-lane-deferral-blind-to-checkpoint-round-reset
    """
    repo = _seed_branch(tmp_path)
    change_id = "2026-09-05-lane-checkpoint-reset"
    _write(repo, f"docs/loom/intent/{change_id}.md",
           _lane_intent_text(change_id, lane_line=None))
    _write_kickoff(repo)
    _write(repo, "docs/notes.md", "wave-end:1 delta\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): wave-end:1 delta\n\nTask: T1")

    # A bare declaration, committed with a message that never mentions
    # "lane" -- introduced right at the checkpoint boundary.
    intent_rel = f"docs/loom/intent/{change_id}.md"
    text = (repo / intent_rel).read_text(encoding="utf-8")
    text = text.replace(
        "needs-design: no — no interface surface touched\n",
        "needs-design: no — no interface surface touched\nlane: express\n",
    )
    (repo / intent_rel).write_text(text, encoding="utf-8")
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", "docs(loom): tidy up the intent wording")

    _write(repo, "docs/more-notes.md", "branch-end round 1 delta\n")
    git(repo, "add", "docs/more-notes.md")
    git(repo, "commit", "-q", "-m", "docs: branch-end round 1\n\nTask: T1")
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "--amend", "--no-edit")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [
            _verdict("r1", 1, "wave-end:1", reviewed_sha),
            _verdict("r2", 1, "wave-end:1", reviewed_sha),
            _verdict("r1", 2, "wave-end:1", reviewed_sha),
            _verdict("r2", 2, "wave-end:1", reviewed_sha),
            _verdict("r3", 1, "branch-end", reviewed_sha),  # checkpoint's own round 1
        ],
        "probes": [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)],
        "open_findings": [],
        "dispatch": [
            _dispatch("implementer", "agent-imp", "T1"),
            _dispatch("reviewer", "r1"),
            _dispatch("reviewer", "r2"),
            _dispatch("reviewer", "r3"),
        ],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode != 0, (
        "branch-end round 1 is a fresh checkpoint's first round, not a "
        "day-one declaration -- real review history (wave-end:1 rounds 1 "
        "and 2) precedes it, so it should still owe two readers; push "
        f"accepted one instead: {result.stdout}"
    )
    assert "push.verdicts-ge-2" in blocked_rules(result)


def test_list_rules_prints_exactly_twenty_seven_lines() -> None:
    """`--list-rules` is the rule-count SSOT (project CLAUDE.md Quality
    Gates); this wave adds no rule of its own (W1-01/W1-02 recompute an
    existing floor, they do not register a new rule id), so the count
    must stay 27."""
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--list-rules"],
        capture_output=True, text=True, cwd=str(REPO_ROOT),
    )
    assert result.returncode == 0, result.stderr
    lines = [line for line in result.stdout.splitlines() if line.strip()]
    assert len(lines) == 27, f"expected 27 rules, saw {len(lines)}:\n{result.stdout}"
    assert "push.verdicts-ge-2" in result.stdout


# =============================================================================
# Round-1 reader follow-up (three more holes found reviewing 029925d0 /
# c24de521 at HEAD a271120c). Each section below is one reader finding.
# =============================================================================

# --- wave-end:1-01: a declaration needs the SAME dated-attribution
# discipline the switch form already has. Acceptance 1 of the intent says
# it in so many words: "宣告或切換都帶日期與人" -- BOTH declaring and
# switching carry date and person, not only switching. `LANE_GRAMMAR`
# today makes the switch suffix's `by <name>`/date mandatory but leaves
# the bare (day-one) form entirely unattributed -- `express`/`gate-only`/
# `full` alone matches with no date, no name, nothing. Two probes: the
# schema should refuse an unattributed declaration outright, and `push`
# should never honour one it somehow sees (falls back to `full`).
# =============================================================================


def test_intent_undated_bare_lane_declaration_rejected_by_schema(tmp_path: Path) -> None:
    """Acceptance 1 requires the declaration itself, not only a switch, to
    carry date and person -- the correct grammar is `lane: <name> —
    declared <YYYY-MM-DD> by <name>` for the day-one form, mirroring the
    switch suffix's `by <name>`. A bare `lane: express`, with no such
    suffix at all, should be schema-invalid; `check_lane_schema` accepts
    it today because `LANE_GRAMMAR`'s entire suffix group (switch OR
    declared) is optional.
    # RED at HEAD: lane-declaration-needs-dated-attribution
    """
    repo = make_intent_repo(tmp_path)
    change_id = "2026-09-05-lane-undated"
    intent_rel = f"docs/loom/intent/{change_id}.md"
    _write(repo, intent_rel, _lane_intent_text(change_id, lane_line="lane: express"))
    git(repo, "add", intent_rel)
    message = (
        "docs(loom): add an intent\n\n"
        "needs-design: no — no interface surface touched\n"
        "lane: express"
    )
    git(repo, "commit", "-q", "-m", message)

    result = run_checker("intent", str(repo / intent_rel), cwd=repo)
    assert result.returncode != 0, (
        "an undated, unattributed `lane: express` declaration should be "
        f"schema-invalid; it passed instead: {result.stdout}"
    )


def test_push_undated_bare_lane_declaration_falls_back_to_full(tmp_path: Path) -> None:
    """The push-side mirror: even if an undated bare declaration somehow
    reaches `push` (the `intent` subcommand is a separate, commit-time
    gate -- finding 2's own architecture), the effective lane must fall
    back to `full` rather than granting `express`'s floor of one. It does
    not: `declared_lane`/`effective_lane_detail` read any grammar-valid
    `lane:` value with no attribution requirement at all, so a docs+skill
    delta with one reviewer currently passes.
    # RED at HEAD: lane-declaration-needs-dated-attribution
    """
    repo = _seed_branch(tmp_path)
    change_id = "2026-09-05-lane-undated-push"
    _commit_intent(repo, change_id, lane_line="lane: express")
    _write_kickoff(repo)
    _write(repo, "docs/notes.md", "some notes\n")
    _write(repo, "loom-code/skills/example/SKILL.md", "---\nname: example\n---\nbody\n")
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): example skill note\n\nTask: T1")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [_verdict("agent-rev", 1, "branch-end", reviewed_sha)],
        "probes": [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)],
        "open_findings": [],
        "dispatch": [
            _dispatch("implementer", "agent-imp", "T1"),
            _dispatch("reviewer", "agent-rev"),
        ],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode != 0, (
        "an undated, unattributed `lane: express` declaration must fall "
        f"back to full (two readers); one reviewer passed instead: {result.stdout}"
    )
    assert "push.verdicts-ge-2" in blocked_rules(result)


# =============================================================================
# wave-end:1-02: the `tests/`-segment exemption (`_is_small_lane_test_path`
# -- "any `tests/` path segment" -- `loom_checker.py:2976-2982`) is checked
# in `_lane_forcing_paths` BEFORE the gate/skill kind is ever consulted for
# that path (`:3210` runs before the `kind == "skill"` branch at `:3214`,
# and `_evidence_masked_kind`'s gate/skill unmasking from 029925d0 is never
# reached at all since the path is typed `gate`/`skill` directly, not
# `evidence`) -- so a genuine gate or skill file sitting under a `tests/`
# directory is waved through as small-lane-safe, exactly the class of bug
# `_evidence_masked_kind` closed for `evidence/`, left open here.
# =============================================================================


def test_push_express_declared_gate_script_hidden_under_tests_segment_incorrectly_passes(
    tmp_path: Path,
) -> None:
    """`loom-code/hooks/tests/push.py` types `gate` (`**/hooks/**`) but
    also carries a `tests` path segment -- `_is_small_lane_test_path`
    waves it through before `_lane_forcing_paths` ever asks what kind it
    is, so a declared `lane: express` delta touching it keeps one
    reviewer instead of being forced to `full`.
    # RED at HEAD: tests-segment-exemption-precedes-gate-skill-kind
    """
    repo = _seed_branch(tmp_path)
    change_id = "2026-09-05-lane-tests-gate"
    _commit_intent(repo, change_id, lane_line="lane: express")
    _write_kickoff(repo)
    _write(repo, "docs/notes.md", "some notes\n")
    _write(
        repo,
        "loom-code/hooks/tests/push.py",
        "def test_push_disguised_as_hook_test():\n    assert True\n",
    )
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat(loom-code): a disguised gate script\n\nTask: T1")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    kind = lc._artifact_type_for(lc.load_manifest(), "loom-code/hooks/tests/push.py")
    assert kind == "gate", f"classification pin: got {kind!r}"

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [_verdict("agent-rev", 1, "branch-end", reviewed_sha)],
        "probes": [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)],
        "open_findings": [],
        "dispatch": [
            _dispatch("implementer", "agent-imp", "T1"),
            _dispatch("reviewer", "agent-rev"),
        ],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode != 0, (
        "a gate-typed script under a `tests/` path segment must still "
        f"force the full lane and block one reviewer: {result.stdout}"
    )
    assert "push.verdicts-ge-2" in blocked_rules(result)


def test_push_gateonly_declared_skill_path_hidden_under_tests_segment_incorrectly_passes(
    tmp_path: Path,
) -> None:
    """`loom-code/skills/example/tests/SKILL.md` types `skill`
    (`**/SKILL.md`) but also carries a `tests` path segment -- the same
    exemption-before-kind ordering waves it through gate-only's skill
    exclusion, so zero reviewers currently pass.
    # RED at HEAD: tests-segment-exemption-precedes-gate-skill-kind
    """
    repo = _seed_branch(tmp_path)
    change_id = "2026-09-05-lane-tests-skill"
    _commit_intent(repo, change_id, lane_line="lane: gate-only")
    _write_kickoff(repo)
    _write(repo, "docs/notes.md", "some notes\n")
    _write(
        repo,
        "loom-code/skills/example/tests/SKILL.md",
        "---\nname: example\n---\nbody\n",
    )
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "feat(loom-code): a disguised skill file\n\nTask: T1")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    kind = lc._artifact_type_for(
        lc.load_manifest(), "loom-code/skills/example/tests/SKILL.md"
    )
    assert kind == "skill", f"classification pin: got {kind!r}"

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [],
        "probes": [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)],
        "open_findings": [],
        "dispatch": [
            _dispatch("implementer", "agent-imp", "T1"),
            _dispatch("adversary", "agent-adv", "T1"),
        ],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode != 0, (
        "a skill-typed file under a `tests/` path segment must still "
        f"force the full lane and block zero reviewers: {result.stdout}"
    )
    assert "push.verdicts-ge-2" in blocked_rules(result)


# =============================================================================
# wave-end:1-03: `from wave <n>` switch timing. `lane-switch.md` says
# "The switch applies to every round after the named `from`; the round
# already in flight finishes in the lane it started under" -- read
# plainly this is ROUND-RECORDING order, not checkpoint identity: the one
# round already being worked when the switch commit lands keeps the old
# lane, and every OTHER round recorded from then on -- whether in the
# same wave/checkpoint or a later one -- gets the new lane. That is also
# the coordinator's stated reading, and it is what these two probes pin.
#
# `effective_lane_detail`'s auto-inferred branch (029925d0/c24de521) does
# not implement this: for a bare or `from wave <n>` declaration with
# `from_round is None`, it sets `from_round = round_number` -- the round
# CURRENTLY being asked about, recomputed fresh on every call -- so
# `round_number > from_round` is `N > N`, always False. Once
# `_earlier_lane_pairs` is non-empty for a change (any review history
# exists at all), EVERY future round -- forever, in every later
# checkpoint too -- is blocked back to `full`, never just the one round
# genuinely in flight when the switch landed. The two probes below show
# this for both directions the coordinator asked about: a switch declared
# well after wave-end:1 fully closes (still blocks branch-end round 1),
# and a switch declared mid-wave, before wave-end:1's own round 2 is
# recorded (still blocks that very round 2, which the reference's "every
# round after" wording says should already carry the new lane).
# =============================================================================


def _closed_wave_end_repo(tmp_path: Path, change_id: str):
    """`main`/`work` seeded, an intent with no `lane:` line yet, and
    wave-end:1 fully run to two rounds of two readers each, with every
    round's review.json actually committed (so `deciding_commit`'s later
    tree reads see real history) -- the common setup both `from wave`
    timing probes build on."""
    repo = _seed_branch(tmp_path)
    intent_rel = f"docs/loom/intent/{change_id}.md"
    _write(repo, intent_rel, _lane_intent_text(change_id, lane_line=None))
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", "docs(loom): add the intent")
    _write_kickoff(repo)
    _write(repo, "docs/notes.md", "wave-end:1 round1 delta\n")
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs(loom): wave-end:1 round1 delta\n\nTask: T1")
    round1_sha = git(repo, "rev-parse", "HEAD")

    review1 = {
        "reviewed_sha": round1_sha,
        "scope": "wave-end:1",
        "vendors": ["anthropic"],
        "verdicts": [
            _verdict("r1", 1, "wave-end:1", round1_sha),
            _verdict("r2", 1, "wave-end:1", round1_sha),
        ],
        "probes": [_package_tests_record(round1_sha), *_adversarial_records(round1_sha)],
        "open_findings": [],
        "dispatch": [
            _dispatch("implementer", "agent-imp", "T1"),
            _dispatch("reviewer", "r1"),
            _dispatch("reviewer", "r2"),
        ],
    }
    review_rel = _write_review(repo, change_id, review1)
    _commit_review(repo, review_rel)
    return repo, intent_rel, review_rel, review1, round1_sha


def test_push_from_wave_switch_declared_after_checkpoint_closes_single_reader_blocked(
    tmp_path: Path,
) -> None:
    """wave-end:1 runs a SECOND round (still two readers, closing the
    checkpoint), and only THEN does the `from wave 1` switch commit land.
    branch-end round 1 -- a fresh round recorded strictly after the
    switch, in a later checkpoint -- should get `express`'s floor of one
    per lane-switch.md's "every round after the named from". `push`
    blocks it instead.
    # RED at HEAD: from-wave-switch-blocks-every-later-round-forever
    """
    change_id = "2026-09-05-lane-wave-after"
    repo, intent_rel, review_rel, review1, round1_sha = _closed_wave_end_repo(
        tmp_path, change_id
    )

    _write(repo, "docs/notes2.md", "wave-end:1 round2 delta\n")
    git(repo, "add", "docs/notes2.md")
    git(repo, "commit", "-q", "-m", "docs: wave-end:1 round2\n\nTask: T1")
    round2_sha = git(repo, "rev-parse", "HEAD")
    review2 = dict(review1)
    review2["reviewed_sha"] = round2_sha
    review2["verdicts"] = review1["verdicts"] + [
        _verdict("r1", 2, "wave-end:1", round2_sha),
        _verdict("r2", 2, "wave-end:1", round2_sha),
    ]
    review2["probes"] = [_package_tests_record(round2_sha), *_adversarial_records(round2_sha)]
    _write_review(repo, change_id, review2)
    _commit_review(repo, review_rel)

    # The switch commit, well after wave-end:1's second (closing) round.
    switch_line = "lane: express — switched 2026-09-06 by kouko, from wave 1"
    text = (repo / intent_rel).read_text(encoding="utf-8")
    text = text.replace(
        "needs-design: no — no interface surface touched\n",
        "needs-design: no — no interface surface touched\n" + switch_line + "\n",
    )
    (repo / intent_rel).write_text(text, encoding="utf-8")
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): switch lane\n\n{switch_line}")

    _write(repo, "docs/more-notes.md", "branch-end round1 delta\n")
    git(repo, "add", "docs/more-notes.md")
    git(repo, "commit", "-q", "-m", "docs: branch-end round1\n\nTask: T1")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    review3 = dict(review2)
    review3["reviewed_sha"] = reviewed_sha
    review3["scope"] = "branch-end"
    review3["verdicts"] = review2["verdicts"] + [
        _verdict("r3", 1, "branch-end", reviewed_sha),
    ]
    review3["probes"] = [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)]
    review3["dispatch"] = review2["dispatch"] + [_dispatch("reviewer", "r3")]
    _write_review(repo, change_id, review3)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, (
        "branch-end round 1 is recorded strictly after the `from wave 1` "
        "switch commit (which itself landed after wave-end:1 fully "
        "closed) -- lane-switch.md's own wording says every round after "
        f"the switch is covered; push blocked it instead: {result.stdout}"
    )


def test_push_from_wave_switch_declared_mid_checkpoint_single_reader_blocked(
    tmp_path: Path,
) -> None:
    """The mirror: the `from wave 1` switch commit lands BEFORE wave-end:1's
    OWN round 2 is recorded (mid-checkpoint, right after round 1). Round 2
    is still recorded strictly after the switch commit, so by the same
    "every round after the named from" wording it should already carry
    `express`'s floor of one -- only round 1 (already in flight when the
    switch landed) keeps the old lane. `push` blocks round 2 as well.
    # RED at HEAD: from-wave-switch-blocks-every-later-round-forever
    """
    change_id = "2026-09-05-lane-wave-mid"
    repo, intent_rel, review_rel, review1, round1_sha = _closed_wave_end_repo(
        tmp_path, change_id
    )

    # The switch commit lands BEFORE round 2's review record.
    switch_line = "lane: express — switched 2026-09-06 by kouko, from wave 1"
    text = (repo / intent_rel).read_text(encoding="utf-8")
    text = text.replace(
        "needs-design: no — no interface surface touched\n",
        "needs-design: no — no interface surface touched\n" + switch_line + "\n",
    )
    (repo / intent_rel).write_text(text, encoding="utf-8")
    git(repo, "add", intent_rel)
    git(repo, "commit", "-q", "-m", f"docs(loom): switch lane\n\n{switch_line}")

    _write(repo, "docs/notes2.md", "wave-end:1 round2 fix delta\n")
    git(repo, "add", "docs/notes2.md")
    git(repo, "commit", "-q", "-m", "docs: wave-end:1 round2 fix\n\nTask: T1")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    review2 = dict(review1)
    review2["reviewed_sha"] = reviewed_sha
    review2["verdicts"] = review1["verdicts"] + [_verdict("r1", 2, "wave-end:1", reviewed_sha)]
    review2["probes"] = [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)]
    _write_review(repo, change_id, review2)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode == 0, (
        "wave-end:1 round 2 is recorded strictly after the `from wave 1` "
        "switch commit (which landed right after round 1) -- only round 1 "
        "itself should keep the old lane per lane-switch.md's wording; "
        f"push blocked round 2 instead: {result.stdout}"
    )


# =============================================================================
# Ratified follow-up (PRINCIPLES.md 56a4dc4c, intent 48114098), definition
# SETTLED by the coordinator after the standing-doc observation below:
# raw recompute runs first; if raw is `small` and the effective
# declaration is `gate-only`, the lane IS `gate-only` with floor 0
# (gate-only is the small lane with reviewers waived, not a separate,
# narrower thing); if raw is `full` for ANY reason at all -- standing
# document, second plugin dir, code, gate, skill, agent-contract,
# interface surface -- the gate-only declaration is ignored and the delta
# falls back to `full`, reason `gate-only needs a small-lane delta: <raw
# reason>`; `express` is unchanged (raw full with no gate-typed path ->
# floor 1); the `kind == "standing"` exemption in `_lane_forcing_paths`
# is superseded by this and goes away. Both probes below use the shape
# the original W0-01 floor's case (c) does (docs + a KICKOFF-DEFAULTS.md
# touch, both IN the delta for one of them) -- that touch is what forces
# the RAW recompute to `full` (a standing document forces full per
# `_small_lane_path_reason`), which is the only way `effective_lane_
# detail` today ever reaches gate-only's OWN eligibility branch at all: a
# delta with no standing-doc touch recomputes raw `small` and returns
# from `effective_lane_detail`'s very first branch before the declared
# lane is even consulted (confirmed directly: a plain docs+tests delta,
# no KICKOFF touch, recomputes `small`, floor 1 today -- the next test
# below pins exactly that this should instead defer to the declared
# `gate-only` and drop to floor 0).
# =============================================================================


def _seed_branch_with_kickoff(tmp_path: Path) -> Path:
    """Like `_seed_branch`, but `docs/loom/KICKOFF-DEFAULTS.md` is
    committed as PART OF THE SEED, on `main`, before `work` is checked
    out -- so `declared_test_command` can still resolve `package-tests:`
    from the final tree, but the file itself never appears in the diff
    `branch_base` computes (any commit added to `work` after checkout
    -- even the very first one -- is included in that diff, so a
    genuinely raw-small delta needs KICKOFF to predate the branch, not
    merely predate the delta commit)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.email", "t@example.com")
    git(repo, "config", "user.name", "T")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    kickoff = repo / "docs/loom/KICKOFF-DEFAULTS.md"
    kickoff.parent.mkdir(parents=True, exist_ok=True)
    kickoff.write_text(
        f"# Kickoff Defaults\n\n- package-tests: {PASSING_COMMAND} — the "
        "fixture's whole suite (2026-09-05)\n",
        encoding="utf-8",
    )
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "checkout", "-q", "-b", "work")
    return repo


def test_push_gateonly_dated_declaration_nontest_code_in_delta_blocked(
    tmp_path: Path,
) -> None:
    """(a) A dated `lane: gate-only — declared <date> by <name>` intent
    (the grammar the fix round is landing), a delta adding
    `loom-code/scripts/helper_bypass.py` -- a plain, non-test, non-`check_*`
    `.py` file -- alongside docs+KICKOFF-DEFAULTS.md, zero verdicts, >=3
    adversarial probes and a package-tests probe recorded. Empirically
    this is GREEN today, not RED: `_lane_forcing_paths` already appends
    `"{path} is non-test code"` to its `hard` list for any `code`-typed
    path (`loom_checker.py`'s existing, pre-ratification logic), and a
    `hard` reason forces `full` for `gate-only` exactly as it does for
    `express` -- independent of whether "the small-lane classes" reading
    has landed yet. Kept as a probe (not deleted) because it pins the
    invariant the ratification cares about, even though this particular
    example was already covered before the ratification existed."""
    repo = _seed_branch(tmp_path)
    change_id = "2026-09-05-lane-smallclass-code"
    lane_line = "lane: gate-only — declared 2026-09-05 by kouko"
    _commit_intent(repo, change_id, lane_line=lane_line)
    _write_kickoff(repo)
    _write(repo, "docs/notes.md", "some notes, no code or skill touched\n")
    _write(repo, "loom-code/scripts/helper_bypass.py", "def helper():\n    return True\n")
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs: docs+KICKOFF delta plus one non-test module")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [],
        "probes": [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)],
        "open_findings": [],
        "dispatch": [_dispatch("adversary", "agent-adv", "T1")],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode != 0, (
        "a dated `lane: gate-only` declaration must not grant zero readers "
        "to a delta that adds a plain non-test `.py` module; blocked "
        f"today already, for a pre-existing reason: {result.stdout}"
    )
    assert "push.verdicts-ge-2" in blocked_rules(result)


def test_push_gateonly_dated_declaration_standing_doc_touch_now_blocked(
    tmp_path: Path,
) -> None:
    """(b) RETARGETED: the coordinator's own follow-up settled the design
    question this test used to leave open (see the superseded docstring
    this replaces) -- under the ratified rule, gate-only IS the small
    lane with a waived floor; a raw recompute of `full` for ANY reason,
    including a standing-document touch, means the gate-only declaration
    is ignored and the delta falls back to `full` (2 readers). The `kind
    == "standing"` exemption in `_lane_forcing_paths` is the mechanism
    that still lets this pass today -- it is slated to go. Same fixture
    as (a) but WITHOUT the non-test module: docs + KICKOFF-DEFAULTS.md
    (a standing document) touched IN the delta, same dated declaration,
    zero verdicts, >=3 probes recorded. Per the ratified rule this must
    now be BLOCKED (`gate-only needs a small-lane delta: <raw reason>`,
    falling back to full's floor of 2); it still passes today.
    # RED at HEAD: standing-doc-exemption-still-lets-gate-only-through
    """
    repo = _seed_branch(tmp_path)
    change_id = "2026-09-05-lane-smallclass-standing"
    lane_line = "lane: gate-only — declared 2026-09-05 by kouko"
    _commit_intent(repo, change_id, lane_line=lane_line)
    _write_kickoff(repo)
    _write(repo, "docs/notes.md", "some notes, no code or skill touched\n")
    _write_evidence(repo)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "docs: docs+KICKOFF delta, no code")
    reviewed_sha = git(repo, "rev-parse", "HEAD")

    raw_lane, raw_reason = lc.change_lane_detail(repo, reviewed_sha)
    assert raw_lane == "full", (
        f"fixture check: a KICKOFF-DEFAULTS.md touch must recompute raw "
        f"full (it is a standing document); got {raw_lane!r} ({raw_reason})"
    )

    body = {
        "reviewed_sha": reviewed_sha,
        "scope": "branch-end",
        "vendors": ["anthropic"],
        "verdicts": [],
        "probes": [_package_tests_record(reviewed_sha), *_adversarial_records(reviewed_sha)],
        "open_findings": [],
        "dispatch": [_dispatch("adversary", "agent-adv", "T1")],
    }
    review_rel = _write_review(repo, change_id, body)
    _commit_review(repo, review_rel)

    result = run_checker("push", cwd=repo)
    assert result.returncode != 0, (
        "a dated `lane: gate-only` declaration must not survive a raw-full "
        "recompute caused by a standing-document touch -- it should fall "
        f"back to full (2 readers, zero present); it passed instead: {result.stdout}"
    )
    assert "push.verdicts-ge-2" in blocked_rules(result)
