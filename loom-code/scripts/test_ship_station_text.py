"""RED/GREEN evidence for W1-01 — the probe-graduation and store-entry text
that used to live in ship's "## 3. Memory" section moved to build's
"## 6.5 Memory step" section (task W1-02); ship's own §3 keeps only the
trailer paragraphs and one escape-hatch sentence. These five pins
re-target the same phrases, now read from build/SKILL.md, plus one new
pin on ship's escape-hatch sentence.

A cheap string-presence assertion; it does not parse or execute the
prose, it only proves the paragraph landed in the file the reading
station reads, in the right place, within the section's word cap.

W2-01 adds: ship no longer closes the intent in its own commit, its own
checkpoint and a second push after the pull request exists (option A).
The close line now rides in the same review-only commit §3 already
amends for the memory trailers, and §6 is "Merge, then verify" — pins
below cover that shape, the PR body's new "## Closing log" section, and
the one-line backward-compatibility note for branches shipped under the
older `PR #<N>` grammar.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SHIP_SKILL_MD = REPO / "loom-code/skills/ship/SKILL.md"
BUILD_SKILL_MD = REPO / "loom-code/skills/build/SKILL.md"
BLIND_RUN_REPORT_REFERENCE = REPO / "loom-code/skills/review/references/blind-run-report.md"

from prose_pin import NEGATION_RE as _NEGATION_RE  # shared matcher, one place to widen


def _has_negation(sentence: str) -> bool:
    """True iff `sentence` contains a word-boundary negation token — 'not',
    'never' or 'no' as whole words, or an "n't" contraction."""
    return bool(_NEGATION_RE.search(sentence))


def _sentences(text: str) -> list[str]:
    """Split text into sentences after collapsing newlines to spaces, so a
    sentence that line-wraps in the SKILL.md source still reads as one
    unit here."""
    flat = " ".join(text.split())
    return [p for p in re.split(r"(?<=[.!?])\s+", flat) if p.strip()]


def _section_6_merge_then_verify() -> str:
    text = SHIP_SKILL_MD.read_text(encoding="utf-8")
    start = text.index("## 6. Merge, then verify")
    end = text.index("## 7. Clean-up")
    return text[start:end]


def _section_4_push() -> str:
    text = SHIP_SKILL_MD.read_text(encoding="utf-8")
    start = text.index("## 4. Push")
    end = text.index("## 5. The pull request")
    return text[start:end]


def _section_0_contract_check() -> str:
    text = SHIP_SKILL_MD.read_text(encoding="utf-8")
    start = text.index("## 0. Contract check")
    end = text.index("## 1. Preconditions")
    return text[start:end]


def test_ship_never_reuses_a_wave_end_round_as_branch_end() -> None:
    text = SHIP_SKILL_MD.read_text(encoding="utf-8")
    section = text.split("## 1. Preconditions", 1)[1].split("## 2.", 1)[0]
    assert "last wave-end checkpoint" not in section
    assert "latest round is a branch-end pass" in section.lower()
    assert "its `scope` is `branch-end`" in section.lower()
    assert "any other scope" in section


def _pr_body_template() -> str:
    """The fenced block right after the PR-body anchor comment."""
    text = SHIP_SKILL_MD.read_text(encoding="utf-8")
    tail = text.split("<!-- pr-body-template -->", 1)[1].splitlines()
    opened = False
    collected: list[str] = []
    for line in tail:
        if line.strip().startswith("```"):
            if opened:
                return "\n".join(collected)
            opened = True
            continue
        if opened:
            collected.append(line)
    raise AssertionError("the PR-body anchor is not followed by a closed fenced block.")


def _section_3_memory() -> str:
    text = SHIP_SKILL_MD.read_text(encoding="utf-8")
    start = text.index("## 3. Memory")
    end = text.index("## 3.5 The nit batch")
    return text[start:end]


def _build_memory_step_section() -> str:
    """Text of build/SKILL.md's "## 6.5 Memory step" section, up to the
    "## 7. Hand-off" heading that follows it — the section that now owns
    probe graduation and docs/loom/memory/ store entries (moved here from
    ship's §3 by W1-02, commit 08904fd1)."""
    text = BUILD_SKILL_MD.read_text(encoding="utf-8")
    start = text.index("## 6.5 Memory step")
    end = text.index("## 7. Hand-off")
    return text[start:end]


def _unwrapped(section: str) -> str:
    """Markdown hard-wraps a paragraph across lines; join those wraps back
    into single-spaced prose before substring-matching a phrase that may
    straddle a line break."""
    return " ".join(section.split())


def test_memory_section_documents_probe_graduation() -> None:
    section = _build_memory_step_section()
    flat = _unwrapped(section)
    assert "evidence/probes/" in section
    assert "test-function name" in flat
    assert "cold-read" in flat.lower()
    assert "never graduate" in flat or "do not graduate" in flat


def test_probe_graduation_paragraph_after_store_entries_paragraph() -> None:
    """Moved pin, inverted order: ship's old §3 wrote "Store entries" before
    the probe-graduation paragraph, and this pin asserted that order. Build's
    §6.5 (commit 08904fd1) writes "**Probe graduation.**" first and
    "**Store entries.**" second — the opposite order — so the assertion
    below is inverted to match the section as it now reads, not deleted."""
    section = _build_memory_step_section()
    store_idx = section.index("**Store entries.**")
    probe_idx = section.index("evidence/probes/")
    assert probe_idx < store_idx


def test_probe_graduation_paragraph_within_word_cap() -> None:
    """Moved pin, widened cap: ship's old §3 kept the probe-graduation
    instruction and the name-collision clause as two separate paragraphs
    (blank-line delimited), each within a 60-word cap. Build's §6.5 merges
    them into one physical paragraph (no blank line between "test-function
    name." and "A test that shares..."), which measures 75 words — so the
    cap here is widened to 90 to match the merged shape while still
    bounding it, rather than asserting a 60-word fact the text no longer
    has."""
    section = _build_memory_step_section()
    start = section.index("evidence/probes/")
    # back up to the start of the paragraph (previous blank line)
    para_start = section.rindex("\n\n", 0, start) + 2
    para_end = section.index("\n\n", start)
    paragraph = section[para_start:para_end]
    assert len(paragraph.split()) <= 90


def test_probe_graduation_paragraph_names_collision_not_duplicate() -> None:
    section = _build_memory_step_section()
    flat = _unwrapped(section)
    assert (
        "a name collision, not a duplicate" in flat
    ), "expected the name-collision-vs-duplicate clause in the graduation paragraph"
    assert "rename the probe copy rather than dropping it" in flat


def test_graduation_commit_reruns_branch_end_before_review_only_commit() -> None:
    """Moved pin, inverted subject: this pin used to assert that ship's §3
    told the graduation commit to re-run the branch-end checkpoint before
    the review-only commit. That instruction moved to build (W1-02), whose
    §6.5 now states the memory step precedes the review round that closes
    the plan instead — and ship's own §3 no longer instructs any re-run at
    all. Both halves are asserted below."""
    build_section = _build_memory_step_section()
    flat_build = _unwrapped(build_section)
    assert (
        "this step precedes the round" in flat_build
    ), "expected build's §6.5 to say the memory step precedes the closing review round"
    assert "loom-code:review" in flat_build

    ship_section = _section_3_memory()
    flat_ship = _unwrapped(ship_section)
    assert (
        "re-run the `branch-end` checkpoint" not in flat_ship
        and "re-run the branch-end checkpoint" not in flat_ship
    ), "ship's §3 must no longer instruct a branch-end re-run"


def test_ship_memory_escapehatch_names_build_task() -> None:
    """New pin (W1-01): ship's §3 keeps one escape-hatch sentence — a
    lesson or probe ship finds that build missed is a task for
    `loom-code:build` followed by a fresh branch-end checkpoint, never a
    commit made here."""
    section = _section_3_memory()
    flat = _unwrapped(section)
    assert "a task for `loom-code:build`" in flat
    assert "fresh" in flat and "branch-end" in flat
    assert "never a commit made here" in flat


def test_ship_close_line_rides_in_review_only_commit() -> None:
    """W2-01: ship's §6 states the intent's close line rides in the same
    review-only commit that carries `review.json` — pushed once and PR'd
    once, no separate close commit or second push. Affirmative,
    un-negated."""
    section = _section_6_merge_then_verify()
    hits = [
        s for s in _sentences(section)
        if "close line" in s.lower()
        and "review-only" in s.lower()
        and "pushed once and pr'd once" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "ship/SKILL.md §6 has no affirmative close-line-rides-in-commit sentence"
    )


def test_ship_push_review_only_head_admits_close_shape() -> None:
    """§6: `push.review-only-head` admits the `review.json` + one intent
    line shape — the rule this option relies on."""
    section = _section_6_merge_then_verify()
    hits = [
        s for s in _sentences(section)
        if "push.review-only-head" in s.lower()
        and "admits exactly that shape" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "ship/SKILL.md §6 has no push.review-only-head admits-exactly-that-shape "
        "sentence"
    )


def test_ship_older_pr_number_shape_still_accepted() -> None:
    """§6: a branch shipped before this rule used `status: closed <date> —
    PR #<N>`; the checker still accepts that older shape — a one-line
    backward-compatibility note, not a second code path this station
    produces."""
    section = _section_6_merge_then_verify()
    flat = _unwrapped(section)
    assert "PR #<N>" in flat
    assert "the checker still accepts that older shape" in flat


def test_ship_pr_body_has_closing_log_section_before_memory() -> None:
    """§5's PR-body template gains a `## Closing log` section that pastes
    `git log <reviewed_sha>..HEAD --format='%h %s'`, placed before
    `## Memory` — the trailer footer must stay the template's last
    block (`ship.pr-body-carries-trailer-footer`)."""
    text = SHIP_SKILL_MD.read_text(encoding="utf-8")
    closing_idx = text.index("## Closing log")
    memory_idx = text.index("## Memory")
    assert closing_idx < memory_idx
    flat = _unwrapped(text)
    assert "git log <reviewed_sha>..HEAD --format='%h %s'" in flat


# --- synthetic self-tests for the negation-aware matcher --------------------


def test_matcher_close_line_sentence_negated_rejected() -> None:
    """A sentence carrying every required substring but negated with
    'never' must be rejected by the matcher, mirroring
    test_language_station_text.py's synthetic-negative pattern."""
    sentence = (
        "The intent's close line never rides in the review-only commit, "
        "pushed once and PR'd once."
    )
    assert _has_negation(sentence)


def test_matcher_review_only_head_sentence_negated_rejected() -> None:
    sentence = "`push.review-only-head` does not admit exactly that shape."
    assert _has_negation(sentence)


def test_matcher_close_line_sentence_affirmative_accepted() -> None:
    sentence = (
        "The intent's close line rides in the review-only commit, pushed "
        "once and PR'd once."
    )
    assert "rides in" in sentence.lower()
    assert not _has_negation(sentence)


def test_matcher_review_only_head_sentence_affirmative_accepted() -> None:
    sentence = "`push.review-only-head` admits exactly that shape."
    assert "admits exactly that shape" in sentence.lower()
    assert not _has_negation(sentence)


def test_ship_preflight_in_section_3_fallback_in_section_6() -> None:
    """§3 tells a cold agent to check the gating checker's own rule text
    BEFORE the amend that adds the close line (an older checker would
    otherwise block the push before any fallback text is reached); §6
    names the fallback the older checker accepts."""
    sec3 = _section_3_memory()
    flat3 = _unwrapped(sec3)
    assert "--list-rules | grep push.review-only-head" in flat3
    assert "leave the `status:` line untouched here" in flat3
    # the preflight is read before the amend command that stages the intent
    preflight_idx = sec3.index("--list-rules | grep push.review-only-head")
    amend_idx = sec3.index("git add docs/loom/<change-id>/review.json docs/loom/intent/<change-id>.md")
    assert preflight_idx < amend_idx, "§3 preflight sits after the amend command"
    assert "when the preflight admitted" in flat3
    flat = _unwrapped(_section_6_merge_then_verify())
    assert "§3's preflight" in flat
    hits = [
        s for s in _sentences(_section_6_merge_then_verify())
        if "closed <date> — PR #<N>" in s and "commit of its own" in s
        and not _has_negation(s)
    ]
    assert hits, "§6 has no affirmative fallback sentence for an older checker"


# --- W1-04: process-cost section in the PR body; push checklist ------------


def test_ship_pr_body_has_process_cost_section_between_closing_log_and_memory() -> None:
    """The PR-body template gains a `## Process cost` section, pinned by
    index order: after `## Closing log`, before `## Memory` (the trailer
    footer must stay the template's last block — ship.pr-body-carries-
    trailer-footer)."""
    text = SHIP_SKILL_MD.read_text(encoding="utf-8")
    closing_idx = text.index("## Closing log")
    process_idx = text.index("## Process cost")
    memory_idx = text.index("## Memory")
    assert closing_idx < process_idx < memory_idx


def test_ship_pr_body_process_cost_lists_rounds_dispatches_caps_hours() -> None:
    """The `## Process cost` section lists rounds, dispatches, cap changes
    and hours, sourced from `review.json`'s `cost` block."""
    section = _pr_body_template()
    idx = section.index("## Process cost")
    tail = _unwrapped(section[idx:])
    assert "cost.rounds" in tail
    assert "cost.dispatches" in tail
    assert "cost.cap_changes" in tail
    assert "cost.hours_plan_to_pr" in tail
    assert "review.json" in tail


def test_ship_push_checklist_keeps_nonpackage_deterministic_checks() -> None:
    """§4 keeps deterministic CI checks but leaves the complete suite to
    the hook-triggered checker."""
    section = _section_4_push()
    for expected in (
        "check_plugin_boundaries.py loom-code",
        "check_plugin_boundaries.py loom-design",
        "sync_codex_manifests.py --check --all",
        "check_mechanisms.py --baseline origin/main",
        "check_mechanisms.py --measure",
        "check_contract_citations.py",
        "check_doc_citations.py",
        "check-skill-crossrefs.py",
    ):
        assert expected in section, f"§4's checklist is missing {expected!r}"
    assert not re.search(r"^python3 -m pytest\b", section, re.MULTILINE)
    checklist_idx = section.index("check-skill-crossrefs.py")
    branch_command_idx = section.index("'--no-follow-tags'")
    assert checklist_idx < branch_command_idx


def test_ship_issues_canonical_immutable_refspec_without_explicit_checker_preflight() -> None:
    """Ship emits an immutable source without separately invoking the
    deterministic checker first."""
    section = _section_4_push()
    assert "'command' '<absolute-trusted-git>' '-C' '<absolute-selected-repository>' 'push'" in section
    assert "'--no-follow-tags' '--recurse-submodules=no' '-u' '--no-verify' 'origin'" in section
    assert "'<full-40-character-HEAD-SHA>:refs/heads/<current-symbolic-branch>'" in section
    assert "python3 ${CLAUDE_PLUGIN_ROOT}/scripts/loom_checker.py push" not in section


def test_ship_push_uses_immutable_full_head_refspec() -> None:
    """The network push cannot re-resolve a mutable branch after its hook."""
    section = _section_4_push()
    assert "shutil.which(\"git\")" in section
    assert "git rev-parse --show-toplevel" in section
    assert "git rev-parse HEAD" in section
    assert "git symbolic-ref --quiet --short HEAD" in section
    assert "40-character object id" in " ".join(section.split())
    assert "not `HEAD`, branch, abbreviation, or variable" in " ".join(section.split())
    assert "git push -u origin <branch>" not in section


def test_ship_push_requires_quote_all_literal_command_and_fixed_containment_flags() -> None:
    section = _section_4_push()
    flat = " ".join(section.split())
    assert "token.replace(\"'\", \"'\\\"'\\\"'\")" in flat
    assert "join with one ASCII space" in flat
    assert "Use no variables, substitutions, or other shell syntax" in flat
    assert "Flags block tags, submodules, pre-push hooks" in flat
    assert "standard `command` builtin is the supported-shell trust root" in flat
    assert "bypasses absolute-executable functions" in flat
    assert "A malicious `command` replacement is outside this guarantee" in flat


def test_ship_push_checklist_mirrors_nonpackage_workflow_jobs() -> None:
    section = _section_4_push()
    hits = [
        s for s in _sentences(section)
        if "mirror" in s.lower()
        and "loom-code-ci.yml" in s.lower()
        and "jobs" in s.lower()
        and "non-package" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "ship/SKILL.md §4 has no affirmative sentence stating its non-package "
        "checks mirror the workflow's jobs"
    )


def test_matcher_push_checklist_mirrors_sentence_negated_rejected() -> None:
    sentence = (
        "This checklist never mirrors `.github/workflows/loom-code-ci.yml`'s "
        "jobs."
    )
    assert _has_negation(sentence)


def test_matcher_push_checklist_mirrors_sentence_affirmative_accepted() -> None:
    sentence = (
        "This checklist mirrors `.github/workflows/loom-code-ci.yml`'s jobs, "
        "command for command."
    )
    assert "mirrors" in sentence.lower()
    assert "loom-code-ci.yml" in sentence.lower()
    assert "jobs" in sentence.lower()
    assert not _has_negation(sentence)


def test_ship_supported_host_hook_is_sole_package_suite_owner() -> None:
    """A1: the supported host's hook invokes the deterministic checker and
    owns the one complete package-suite execution."""
    section = _section_4_push()
    hits = [
        s for s in _sentences(section)
        if "supported host's local push hook" in s.lower()
        and "sole owner" in s.lower()
        and "deterministic push checker" in s.lower()
        and "exactly once" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "ship/SKILL.md §4 has no affirmative sentence making the supported "
        "host hook sole owner of exactly one package-suite execution"
    )


def test_matcher_hook_owner_sentence_negated_rejected() -> None:
    sentence = (
        "The supported host's local push hook is never the sole owner and its "
        "deterministic push checker does not execute the package suite exactly once."
    )
    assert _has_negation(sentence)


def test_matcher_hook_owner_sentence_affirmative_accepted() -> None:
    sentence = (
        "The supported host's local push hook is the sole owner: its "
        "deterministic push checker executes the package suite exactly once."
    )
    assert "supported host's local push hook" in sentence.lower()
    assert "sole owner" in sentence.lower()
    assert "deterministic push checker" in sentence.lower()
    assert "exactly once" in sentence.lower()
    assert not _has_negation(sentence)


def test_ship_missing_or_inactive_supported_host_hook_blocks() -> None:
    """A2 negative: an unchecked manual network operation is not Ship."""
    hits = [
        s for s in _sentences(_section_0_contract_check())
        if "missing or inactive" in s.lower()
        and "supported-host hook" in s.lower()
        and "blocks ship" in s.lower()
        and not _has_negation(s)
    ]
    assert hits, (
        "ship/SKILL.md §0 has no affirmative missing-or-inactive hook block"
    )


# --- W1-04: lane PR line, gate-only ③ pointer -------------------------------


def test_pr_body_template_carries_lane_line() -> None:
    """The `## Review` section of the PR-body template carries the literal
    `lane: <name>（第 N 輪起）` line — the format string a checkpoint round
    fills in, not prose, so it is exempt from the English-only station-text
    policy the same way `needs-design:` is."""
    template = _pr_body_template()
    section = template.split("## Review", 1)[1]
    assert "lane: <name>（第 N 輪起）" in section


def test_decision_point_3_points_at_gateonly_replacement_material() -> None:
    """Ship's step 2 (decision point ③) is at the file's word cap
    (3,497/3,500), so the affirmative sentence naming gate-only's
    replacement material -- a one-page probe-and-package-test result, in
    place of the blind-run report -- lives in
    `references/blind-run-report.md`'s own "Gate-only's replacement
    material" section instead; ship/SKILL.md itself carries only the one
    pointer sentence naming that section. The pointer never spells out
    the literal path `references/blind-run-report.md` -- that exact
    substring, anywhere in a SKILL.md, is read by `test_ship_pr_body.py`'s
    `test_referenced_paths_exist` as a same-skill reference and would
    wrongly demand `loom-code/skills/ship/references/blind-run-report.md`,
    which does not exist (the file lives under review's own `references/`
    instead)."""
    text = SHIP_SKILL_MD.read_text(encoding="utf-8")
    section = text.split("## 2. Decision point", 1)[1].split("## 3. Memory", 1)[0]
    assert "Gate-only's replacement material" in section
    assert "blind-run-report.md" in section
    assert "references/blind-run-report.md" not in section

    reference = BLIND_RUN_REPORT_REFERENCE.read_text(encoding="utf-8")
    ref_section = reference.split("## Gate-only's replacement material", 1)[1]
    ref_section = ref_section.split("## What makes a report unusable", 1)[0]
    hits = [
        s for s in _sentences(ref_section)
        if "gate-only" in s.lower()
        and "probe" in s.lower()
        and "package-test" in s.lower()
        and "blind-run-report.md" in s
        and not _has_negation(s)
    ]
    assert hits, (
        "references/blind-run-report.md's gate-only section has no "
        "affirmative sentence naming the one-page probe-and-package-test "
        "result"
    )


def test_matcher_gateonly_sentence_negated_rejected() -> None:
    sentence = (
        "Gate-only does not present the review station's blind-run report "
        "at decision point 3, never showing it."
    )
    assert _has_negation(sentence)


def test_matcher_gateonly_sentence_affirmative_accepted() -> None:
    sentence = (
        "Gate-only presents the one-page probe-and-package-test result "
        "there instead, shaped in `references/blind-run-report.md`."
    )
    assert "gate-only" in sentence.lower()
    assert "probe" in sentence.lower()
    assert "blind-run-report.md" in sentence
    assert not _has_negation(sentence)
