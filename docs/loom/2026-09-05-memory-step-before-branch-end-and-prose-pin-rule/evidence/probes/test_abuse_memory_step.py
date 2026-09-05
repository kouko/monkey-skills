"""W0-01 adversary-first probes for
2026-09-05-memory-step-before-branch-end-and-prose-pin-rule, written before
W1-01/W1-02/W1-03/W2-01/W2-02 exist. Every case is RED today unless its
docstring says GREEN; each names the task that should turn it green
(plan.md, section "Wave 1"/"Wave 2").

Policy under test (intent.md Acceptance 2-5, plan.md task table): the
ship-station memory step (probe graduation, `docs/loom/memory/` store
entries) moves to build, before the branch-end checkpoint; ship keeps only
trailers and the escape-hatch sentence. adversary.md and
engineering-baseline.md each gain one sentence pinning the prose-pin rule
(affirmative verb, no negation, self-test named). build gains a copyable
`Task:` trailer-check command at wave end.

These probes pin FACTS, not verbatim wording (plan.md Risk: "pin facts ...
not sentences") - absence of two phrases in ship's memory section, presence
and position of a memory heading in build, a sentence-level affirmative/
negation/self-test check in two agent files, and a fenced command
containing both `git log` and `Task:` in build's after-task/wave-end
sections.

No branch-scope probe this time (the memory-store lesson from #791: a
branch-diff-scope probe pinned against a stale local `main` produced a
false positive once another change landed on main first).
"""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

import pytest

# evidence/probes/test_abuse_memory_step.py -> parents[5] is the repo root
# (probes -> evidence -> <change-id> -> loom -> docs -> repo root).
REPO = Path(__file__).resolve().parents[5]

SHIP_SKILL = REPO / "loom-code/skills/ship/SKILL.md"
BUILD_SKILL = REPO / "loom-code/skills/build/SKILL.md"
ADVERSARY_MD = REPO / "loom-code/agents/adversary.md"
BASELINE_MD = REPO / "loom-code/references/engineering-baseline.md"
LOOM_CHECKER = REPO / "loom-code/scripts/loom_checker.py"

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_NEGATION_RE = re.compile(r"\b(?:not|never|no)\b|n't", re.IGNORECASE)
_HEADING_RE = re.compile(r"^##\s+(.*)$", re.MULTILINE)
_FENCE_RE = re.compile(r"```(?:[a-zA-Z]*)\n(.*?)```", re.DOTALL)


def _sentences(text: str) -> list[str]:
    """Loose sentence splitter, matching the shape used by the
    2026-09-03-artifact-language-policy probe file."""
    flat = " ".join(text.split())
    return [p for p in _SENTENCE_SPLIT.split(flat) if p.strip()]


def _has_negation(sentence: str) -> bool:
    return bool(_NEGATION_RE.search(sentence))


def _headings(text: str) -> list[tuple[str, int]]:
    """Return [(heading title, char offset)] for every `## `-level heading,
    in document order."""
    return [(m.group(1).strip(), m.start()) for m in _HEADING_RE.finditer(text)]


def _section_body(text: str, heading_substr: str) -> str | None:
    """Text of the first `## `-level section whose heading contains
    `heading_substr` (case-insensitive), up to the next `## ` heading of
    equal or lesser depth (a `## 3.5` sub-heading does not end a `## 3`
    section's body under this splitter, but none of the probes below need
    that distinction)."""
    heads = _headings(text)
    for i, (title, offset) in enumerate(heads):
        if heading_substr.lower() in title.lower():
            end = heads[i + 1][1] if i + 1 < len(heads) else len(text)
            return text[offset:end]
    return None


# --- (a) ship §3 no longer instructs probe graduation or store entries -----


def test_shipmemory_graduationtext_absent():
    """Attack: ship/SKILL.md's "## 3." (Memory) section must contain
    neither "evidence/probes/" nor a sentence instructing ship to copy
    probes into the permanent test directory or write a
    `docs/loom/memory/` store entry and re-run the branch-end checkpoint.
    RED today: the section (lines ~129-197) contains "evidence/probes/"
    (graduation instructions) and "Store entries" + "re-run the
    `branch-end` checkpoint" (store-entry instructions) verbatim. GREEN
    target: W1-01, which moves this text to build."""
    body = _section_body(SHIP_SKILL.read_text(encoding="utf-8"), "3. Memory")
    assert body is not None, "ship/SKILL.md has no '## 3. Memory' heading at all"

    offenders = []
    if "evidence/probes/" in body:
        offenders.append("evidence/probes/")
    if "store entries" in body.lower() and "branch-end" in body.lower():
        offenders.append("store-entry + branch-end re-run instruction")
    assert not offenders, (
        f"ship §3 still instructs ship-time memory work: {offenders}"
    )


# --- (b) build carries a memory section before the hand-off to ship -------


def _handoff_heading_index(headings: list[tuple[str, int]], text: str) -> int | None:
    """Index (into `headings`) of the first heading whose title contains
    'hand-off'/'handoff', OR whose body mentions calling the branch-end
    checkpoint / handing to ship — whichever comes first. Returns None if
    neither is found."""
    candidates = []
    for i, (title, offset) in enumerate(headings):
        end = headings[i + 1][1] if i + 1 < len(headings) else len(text)
        body = text[offset:end]
        title_low = title.lower()
        body_low = body.lower()
        if "hand-off" in title_low or "handoff" in title_low:
            candidates.append(i)
        elif "loom-code:ship" in body_low or "branch end" in body_low or "branch-end" in body_low:
            candidates.append(i)
    return min(candidates) if candidates else None


def _memory_section_index(headings: list[tuple[str, int]]) -> int | None:
    for i, (title, _offset) in enumerate(headings):
        if "memory" in title.lower():
            return i
    return None


def test_buildmemorysection_beforehandoff_absent():
    """Attack: build/SKILL.md must carry a `## `-level heading whose title
    contains "memory"/"Memory", whose body mentions both probe graduation
    (`evidence/probes/` or "graduat") and `docs/loom/memory/`, and which
    sits BEFORE the heading that hands off to ship / calls the branch-end
    checkpoint. RED today: build/SKILL.md has no heading titled "memory" at
    all (grep confirmed) — the only "memory" occurrence is the prose
    sentence in `## 7. Hand-off` that still says "`ship` runs the memory
    step". GREEN target: W1-02."""
    text = BUILD_SKILL.read_text(encoding="utf-8")
    headings = _headings(text)

    mem_idx = _memory_section_index(headings)
    assert mem_idx is not None, (
        "build/SKILL.md has no heading whose title contains 'memory' — "
        "the memory step has not moved here yet"
    )

    end = headings[mem_idx + 1][1] if mem_idx + 1 < len(headings) else len(text)
    mem_body = text[headings[mem_idx][1]:end].lower()
    assert ("evidence/probes/" in mem_body or "graduat" in mem_body), (
        "build's memory section does not mention probe graduation"
    )
    assert "docs/loom/memory/" in mem_body, (
        "build's memory section does not mention the docs/loom/memory/ store"
    )

    handoff_idx = _handoff_heading_index(headings, text)
    assert handoff_idx is not None, (
        "could not locate a hand-off / branch-end-checkpoint heading to "
        "compare position against"
    )
    assert mem_idx < handoff_idx, (
        f"build's memory heading ({headings[mem_idx][0]!r}, index {mem_idx}) "
        f"does not sit before the hand-off heading "
        f"({headings[handoff_idx][0]!r}, index {handoff_idx})"
    )


def test_memorysectionlocator_afterhandoff_rejected():
    """Attack (self-test on the locator used by the probe above, attack-
    catalogue class 'forge an artifact'): a synthetic document with a
    memory section placed AFTER its hand-off heading must be rejected by
    the same position check, so a future implementer cannot satisfy (b) by
    appending the memory section at the end of the file. GREEN now — pins
    the locator's own discriminating power, independent of any real repo
    file."""
    synthetic = (
        "## 1. Setup\n\nsome text.\n\n"
        "## 7. Hand-off\n\nhand to `loom-code:ship` with the change id; "
        "this calls the branch-end checkpoint.\n\n"
        "## 8. Memory\n\ngraduat probes under evidence/probes/ into "
        "docs/loom/memory/ store entries.\n"
    )
    headings = _headings(synthetic)
    mem_idx = _memory_section_index(headings)
    handoff_idx = _handoff_heading_index(headings, synthetic)
    assert mem_idx is not None and handoff_idx is not None
    assert not (mem_idx < handoff_idx), (
        "a memory section placed AFTER the hand-off heading must not "
        "satisfy the before-hand-off position check"
    )


# --- (c) adversary.md / engineering-baseline.md prose-pin sentence --------

_AFFIRM_VERB_RE = re.compile(r"\b(require|requires|must|is|are|asserts)\b")
_AFFIRM_KW_RE = re.compile(r"\baffirmative(ly)?\b")
_NEGATION_KW_RE = re.compile(r"\bnegat(?:ion|ed)\b")
_SELFTEST_KW_RE = re.compile(r"\b(self-test|synthetic)\b")


def _sentence_pins_prose_rule(sentence: str) -> bool:
    """True iff `sentence` (lowercased for keyword matching) names
    "affirmative"/"affirmatively", "negation"/"negated", and "self-test"/
    "synthetic", has one of the affirmative verb forms
    (require/requires/must/is/are/asserts) BEFORE the earliest of those
    three keyword hits, and carries no negation token anywhere in the
    sentence."""
    low = sentence.lower()
    m_affirm = _AFFIRM_KW_RE.search(low)
    m_negation = _NEGATION_KW_RE.search(low)
    m_selftest = _SELFTEST_KW_RE.search(low)
    if not (m_affirm and m_negation and m_selftest):
        return False
    first_kw_idx = min(m_affirm.start(), m_negation.start(), m_selftest.start())
    if not _AFFIRM_VERB_RE.search(low[:first_kw_idx]):
        return False
    return not _has_negation(sentence)


@pytest.mark.parametrize("path", [ADVERSARY_MD, BASELINE_MD], ids=lambda p: p.name)
def test_prosepinsentence_missing_absent(path: Path):
    """Attack: adversary.md and engineering-baseline.md must each carry
    one sentence with an affirmative verb before "affirmative"/"negation"/
    "self-test" vocabulary, and no negation token anywhere in that
    sentence. RED today: neither file contains any of "affirmative",
    "negation", "negated", "self-test", or "synthetic" at all (grep
    confirmed empty on both). GREEN target: W1-03."""
    text = path.read_text(encoding="utf-8")
    sentences = _sentences(text)
    hits = [s for s in sentences if _sentence_pins_prose_rule(s)]
    assert hits, (
        f"{path.name} has no sentence pinning the prose-pin rule "
        "(affirmative verb + affirmative/negation/self-test vocabulary, "
        "no negation token) — none of those keywords appear in the file "
        "at all"
    )


def test_prosepinmatcher_negatedsynthetic_rejected():
    """Attack (self-test on `_sentence_pins_prose_rule`): a negated
    synthetic sentence carrying all three keyword groups must still be
    rejected, and an affirmative synthetic sentence must be accepted —
    otherwise (c) above could be satisfied by a sentence that FORBIDS the
    rule rather than requiring it (same round-2 class of finding as the
    2026-09-03-artifact-language-policy probe file's probe (e)). GREEN
    now: pins the matcher's own discriminating power."""
    affirmative = (
        "A prose-pin rule requires an affirmative sentence verified through "
        "a self-test against a synthetic negated example."
    )
    assert _sentence_pins_prose_rule(affirmative), (
        "a genuinely affirmative synthetic sentence must pass"
    )

    negated = (
        "A prose-pin rule does not require an affirmative sentence, and "
        "skips both the self-test and the synthetic negated example."
    )
    assert not _sentence_pins_prose_rule(negated), (
        "a negated synthetic sentence must be rejected even though it "
        "names all three keyword groups"
    )

    no_verb = (
        "Affirmative wording, a negated clause, and a synthetic self-test "
        "example, listed here with zero verbs connecting them."
    )
    assert not _sentence_pins_prose_rule(no_verb), (
        "a sentence with the keywords but no affirmative verb before them "
        "must be rejected"
    )


# --- (d) build §4/§5 carries a copyable Task:-trailer-check command --------


def _fenced_blocks(text: str) -> list[str]:
    return [m.group(1) for m in _FENCE_RE.finditer(text)]


def _trailer_check_command(text: str) -> str | None:
    """First fenced code block in `text` whose content contains both
    "git log" and "Task:" — the copyable trailer-check command — or None."""
    for block in _fenced_blocks(text):
        if "git log" in block and "Task:" in block:
            return block
    return None


def test_buildtrailercommand_fencedblock_absent():
    """Attack: build/SKILL.md's "## 4. After each task returns" or
    "## 5. Wave end" section must contain a fenced code block whose text
    contains both "git log" and "Task:" (the copyable trailer-check
    command), and the wave-end paragraph must mention running it over
    `<reviewed_sha>..HEAD` or "the wave's commits". RED today: §4 has no
    fenced block at all (its only check is prose: "check the commit exists
    and carries its `Task:` trailer"); §5's only fenced block is
    `git diff --stat <reviewed_sha>..HEAD`, which contains neither "git
    log" nor "Task:". GREEN target: W1-02."""
    text = BUILD_SKILL.read_text(encoding="utf-8")
    sec4 = _section_body(text, "4. After each task returns") or ""
    sec5 = _section_body(text, "5. Wave end") or ""

    command = _trailer_check_command(sec4) or _trailer_check_command(sec5)
    assert command is not None, (
        "neither build §4 nor §5 contains a fenced code block with both "
        "'git log' and 'Task:' in it"
    )
    assert "<reviewed_sha>..HEAD" in sec5 or "the wave's commits" in sec5.lower(), (
        "build §5 does not say the trailer-check command runs over "
        "<reviewed_sha>..HEAD or 'the wave's commits'"
    )


def test_trailercommandlocator_proseonly_rejected():
    """Attack (self-test on `_trailer_check_command`, attack-catalogue
    class 'forge an artifact'): a paragraph that mentions `git log` and
    `Task:` only in ordinary prose — never inside a fenced code block —
    must not satisfy the locator, so a future implementer cannot satisfy
    (d) by describing the command in words instead of giving a copyable
    one. GREEN now."""
    prose_only = (
        "## 5. Wave end\n\n"
        "Run `git log <reviewed_sha>..HEAD` and check every commit's "
        "`Task:` trailer by eye; there is no copyable command here.\n"
    )
    assert _trailer_check_command(prose_only) is None, (
        "a prose-only mention of git log and Task: (no fenced block) must "
        "not satisfy the trailer-check-command locator"
    )


# --- (e) GREEN pin: --list-rules line count ---------------------------------


def test_checker_rulecount_pinned():
    """GREEN pin: `loom_checker.py --list-rules`, resolved inside REPO,
    prints exactly 27 lines today — intent Acceptance 5 requires this
    stays unchanged by this branch (no checker rule is added or removed)."""
    assert LOOM_CHECKER.is_file(), f"loom_checker.py not found at {LOOM_CHECKER}"
    result = subprocess.run(
        ["python3", str(LOOM_CHECKER), "--list-rules"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    lines = [l for l in result.stdout.splitlines() if l.strip() != ""]
    assert result.returncode == 0, (
        f"loom_checker.py --list-rules exited {result.returncode}: {result.stderr}"
    )
    assert len(lines) == 27, (
        f"--list-rules printed {len(lines)} non-empty lines, expected 27:\n"
        + "\n".join(lines)
    )


# --- (f) sandbox demonstration: the extracted command catches a missing ----
# --- Task: trailer, in a throwaway repo (never the real repo's git state) --


def test_trailercommand_missingtrailercommit_caught():
    """Attack: extract the fenced trailer-check command from build's own
    §5 text (the block located by (d) above); in a temporary git repo
    (tempfile, never REPO) build three commits deterministically — a
    genesis commit (`reviewed_sha`), one carrying a `Task: W9-99` trailer,
    one without — read them back with `git rev-list` (no NUL-splitting a
    single log string, the bug W1-02 found: a string with no NUL byte
    splits into one element, so an `or`-fallback after it never runs and
    the commit count never matches). Substitute `<reviewed_sha>` with the
    genesis commit's own sha, run the extracted command with cwd = the
    sandbox repo, and assert its output names exactly the trailer-less
    commit and not the trailered one. Skips (never fails) only when no
    fenced git-log/Task: command exists yet (probe (d) still RED). Never
    touches the real repo's git state."""
    text = BUILD_SKILL.read_text(encoding="utf-8")
    sec5 = _section_body(text, "5. Wave end") or ""
    sec4 = _section_body(text, "4. After each task returns") or ""
    command = _trailer_check_command(sec5) or _trailer_check_command(sec4)
    if command is None:
        pytest.skip(
            "build §4/§5 has no fenced git-log/Task: command yet "
            "(probe (d) is still RED) — nothing to extract or run"
        )

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        git = ["git", "-C", str(tmp_path)]
        subprocess.run(git + ["init", "-q"], check=True)
        subprocess.run(git + ["config", "user.email", "probe@example.com"], check=True)
        subprocess.run(git + ["config", "user.name", "probe"], check=True)

        def _commit(filename: str, message: str, trailer: str | None) -> str:
            (tmp_path / filename).write_text(f"{filename}\n")
            subprocess.run(git + ["add", filename], check=True)
            args = git + ["commit", "-q", "-m", message]
            if trailer is not None:
                args += ["--trailer", trailer]
            subprocess.run(args, check=True)
            return subprocess.run(
                git + ["rev-parse", "HEAD"], capture_output=True, text=True, check=True
            ).stdout.strip()

        reviewed_sha = _commit("genesis.txt", "genesis", None)
        trailered_sha = _commit("with_trailer.txt", "with trailer", "Task: W9-99")
        missing_sha = _commit("without_trailer.txt", "without trailer", None)

        wave_commits = subprocess.run(
            git + ["rev-list", f"{reviewed_sha}..HEAD", "--no-merges"],
            capture_output=True, text=True, check=True,
        ).stdout.split()
        assert set(wave_commits) == {trailered_sha, missing_sha}, (
            f"sandbox rev-list over {reviewed_sha}..HEAD did not return "
            f"exactly the two wave commits: {wave_commits}"
        )

        substituted = command.replace("<reviewed_sha>", reviewed_sha)
        result = subprocess.run(
            ["bash", "-c", substituted],
            cwd=tmp_path,
            capture_output=True,
            text=True,
        )
        assert missing_sha in result.stdout, (
            f"build's §5 trailer loop did not name the missing-trailer "
            f"commit {missing_sha} in its output: {result.stdout!r} "
            f"(stderr {result.stderr!r})"
        )
        assert trailered_sha not in result.stdout, (
            f"build's §5 trailer loop wrongly named the trailered commit "
            f"{trailered_sha} as missing its trailer: {result.stdout!r}"
        )


if __name__ == "__main__":  # pragma: no cover
    import sys
    sys.exit(pytest.main([__file__, "-q"]))
