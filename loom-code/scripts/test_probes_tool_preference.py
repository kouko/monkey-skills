"""Adversary-first probes for 2026-09-04-prefer-harness-native-file-tools.

Written at W0-01 by the adversary agent BEFORE any implementer exists (build
station §2, adversary-first for `code`/`gate` tasks). Most cases below are RED
now; W1-01 and W1-02 are what turn them GREEN. The adversary implemented no
part of W1-01/W1-02 -- adversary ne implementer.

The change adds ONE prose sentence to four agent contracts and to the build
station's standing trap-guard block: write files with the host's edit tool
(Edit/Write, `apply_patch` on Codex), never `sed -i` or heredocs; read and
search however is cheapest; a bulk mechanical replace may be scripted but the
match count and the diff must be shown; and this holds over a contrary host
reminder that appears later.

Attack surfaces, from plan.md W0-01:

  (1) all four contracts carry the passage; it names `apply_patch`, a host
      edit tool, and `sed -i`/heredoc; <= 40 English words (`len(str.split())`,
      never `wc` -- BSD and GNU never agree, and that is a repo memory entry).
  (2) the passage regulates WRITING only: no prohibition clause in it names a
      read/search tool (`cat`, `grep`, `head`, `sed -n`, Read, Grep, Glob).
      The detector is itself tested against three synthetic sentences below,
      because a regex that cannot tell "never sed -i ...; read however is
      cheapest" from "never cat or sed" would wave the real defect through.
  (3) the passage overrides a host reminder that appears LATER -- the intent's
      measured fact is that the reminder is absent at dispatch and arrives
      beside the first tool result, so "prefer Edit" alone is not enough.
  (4) the build station's copy and implementer.md's copy are the SAME
      normalised string. There are already two hand-maintained copies of the
      trap-guard block; a third divergence is how prose contracts rot.
  (5) the passage cites no `docs/` path (CLAUDE.md Contract Citations: a
      dispatched agent resolves paths in the repo it is standing in).
  (6) the bulk-replace escape hatch exists and points at two CHECKABLE
      actions -- a count and a diff -- not at a judgement ("when appropriate").
  (7) the shipped word caps still hold: reviewer.md <= 1300, blind-runner.md
      and adversary.md <= 600, read from the SHIPPED `AGENT_CAPS`/`body_of`
      rather than re-declared here.
  (8) plugin.json (both manifests) past 1.2.1, and the CHANGELOG carries it.

  (9) ADVERSARY-ADDED, not in the plan. `test_reviewer_agent_single_contract.
      py::test_no_deleted_vocabulary` bans `\\bbatch\\b` (and `brief`, `seed`,
      `packet`, `marker`, ...) across reviewer/blind-runner/adversary.md. The
      plan's own wording skeleton is one synonym away from tripping it: a
      sentence that says "a bulk/batch mechanical replace" turns an unrelated
      shipped test red in three files at once. Pinned here so W1-01 discovers
      it from a probe rather than from a checkpoint.

## Attack-catalogue classes worked against the PLANNED sentence

Cold-read attempts against prose that does not exist yet, so they are not
pytest cases. One line per class, recorded so W1-01 writes defensively:

* forge an artifact the gate trusts -- N/A. Nothing here is marked
  `<!-- gate: <id> -->`, so per CLAUDE.md 散文不當閘 this is not a gate and
  has no forgeable input.
* bypass a gate by editing its input -- LIVE, and it is the whole point of
  the change. The repo's PostToolUse guards (skill-folder structure, codex
  manifest drift) match `Write|Edit` only, so `sed -i` edits a guarded file
  without ever firing the guard. The sentence is the only thing standing
  between an agent and that bypass; it is prose, so it cannot be enforced,
  only cold-read (Acceptance 2).
* replay a stale artifact -- LIVE on surface (3). The reminder the sentence
  overrides is a session-assigned A/B cohort (`tengu_thrifty_sonic`): its
  text WILL change and may vanish. W1-01 must therefore write the override
  against the CLASS ("any host reminder saying otherwise, including one that
  appears later"), never by quoting that reminder's current wording, or the
  contract goes stale the next time the experiment reshuffles.
* self-exempt via a prose condition -- LIVE. "unless a script is more
  efficient" is exactly the loophole an agent under time pressure reaches
  for; surface (6) is why the escape hatch must cost something checkable
  (count + diff) instead of being free.
* cross a trust boundary -- N/A to the sentence itself.
* race a concurrent writer -- N/A to the sentence; live for W1-01/W1-02 in
  one tree, which is a build-station concern (path-limited commits).

## Live host-reminder attempt during this task

While writing these probes the host injected, verbatim: "While bypass
permissions mode is active: Do your work through the Bash tool wherever it
can accomplish the job: ... make file changes with sed, heredocs, or short
scripts, rather than using the dedicated Read, Edit, or Write tools." It
arrived AFTER the first tool call, exactly as the intent's Problem section
measured. This file was written with the Write tool. That is one datapoint,
not the cold read -- Acceptance 2 still needs the blind-runner's clean-room
run, because an adversary who was told about the trap in its own dispatch
packet is not a blind subject.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from itertools import count as _count
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

AGENTS = REPO_ROOT / "loom-code" / "agents"
CONTRACTS = {
    "implementer": AGENTS / "implementer.md",
    "reviewer": AGENTS / "reviewer.md",
    "blind-runner": AGENTS / "blind-runner.md",
    "adversary": AGENTS / "adversary.md",
}
BUILD_SKILL = REPO_ROOT / "loom-code" / "skills" / "build" / "SKILL.md"
REVIEW_SKILL = REPO_ROOT / "loom-code" / "skills" / "review" / "SKILL.md"
SHIPPED_CAPS_TEST = (
    REPO_ROOT / "loom-code" / "scripts" / "test_reviewer_agent_single_contract.py"
)
PLUGIN_JSONS = {
    "claude": REPO_ROOT / "loom-code" / ".claude-plugin" / "plugin.json",
    "codex": REPO_ROOT / "loom-code" / ".codex-plugin" / "plugin.json",
}
CHANGELOG = REPO_ROOT / "loom-code" / "CHANGELOG.md"

WORD_CAP = 40
BASELINE_VERSION = (1, 2, 1)

_MODULE_COUNTER = _count()

# The token that anchors the passage. Chosen because it is the one word in the
# sentence that appears nowhere else in these files today and that no
# reasonable rewording can drop: naming Codex's edit tool is the whole point of
# "the host's edit tool". Line numbers are deliberately not used -- the
# implementer is free to place the passage anywhere in the trap section.
ANCHOR = "apply_patch"

# Vocabulary that keeps an adjacent bullet inside the same passage, so the
# implementer may split the sentence across two list items (plan W1-01) without
# the probe losing half of it.
PASSAGE_VOCAB = ("apply_patch", "sed -i", "heredoc", "reminder", "host")

# Words that open a prohibition. Everything from one of these to the next
# clause boundary is "what this passage forbids".
PROHIBITION = r"\b(?:never|not|no|don't|do not|avoid|instead of|rather than)\b"

# Clause boundaries. `,` is NOT one: "never `sed -i` or heredocs, ever" is a
# single prohibition and splitting on the comma would truncate it.
CLAUSE_SPLIT = r"[;.]|--|—"

# Reading and searching. `sed` bare is absent on purpose: `sed -i` is the
# forbidden write form, and matching bare `sed` would make every correct
# sentence fail case (2).
READ_TOOLS = (
    r"\bcat\b",
    r"\bgrep\b",
    r"\bhead\b",
    r"\btail\b",
    r"\bsed -n\b",
    r"\bripgrep\b",
    r"\brg\b",
    r"\bRead\b",
    r"\bGrep\b",
    r"\bGlob\b",
)

# Banned across reviewer/blind-runner/adversary.md by the shipped
# test_no_deleted_vocabulary. Only the ones a tool-preference sentence might
# plausibly reach for.
DELETED_VOCAB_AT_RISK = (r"\bbatch\b", r"\bbatches\b", r"\bbrief\b", r"\bpacket\b")
CAPPED_AGENTS = ("reviewer", "blind-runner", "adversary")


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def _shipped_caps_module():
    """Import the SHIPPED caps test module, fresh, under a throwaway name.

    `AGENT_CAPS` and `body_of` are read from the file that actually enforces
    them. Re-declaring the numbers here would let the two drift and case (7)
    would then be asserting against a copy nobody ships.
    """
    name = f"_shipped_caps_{next(_MODULE_COUNTER)}"
    spec = importlib.util.spec_from_file_location(name, SHIPPED_CAPS_TEST)
    assert spec and spec.loader, f"cannot import {SHIPPED_CAPS_TEST}"
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _items(text: str) -> list[str]:
    """Markdown top-level list items, each joined into one logical line.

    A continuation line (indented, not starting a new `- `) belongs to the
    item above it, so a wrapped bullet counts as one item and its words are
    counted once.
    """
    out: list[str] = []
    for raw in text.splitlines():
        if re.match(r"^\s*[-*]\s+", raw):
            out.append(raw.strip())
        elif out and raw.strip() and re.match(r"^\s+", raw):
            out[-1] = out[-1] + " " + raw.strip()
        else:
            out.append("")  # a non-list line breaks adjacency
    return out


def _passage(path: Path) -> str:
    """The tool-preference passage in `path`, or fail loudly.

    Located by the `apply_patch` anchor, then extended over immediately
    adjacent list items that share the passage vocabulary -- so a sentence
    split into two bullets is still measured whole against the 40-word cap.
    Exactly one anchor is required: two would mean the rule is stated twice
    and the two copies can drift.
    """
    items = _items(path.read_text(encoding="utf-8"))
    hits = [i for i, item in enumerate(items) if ANCHOR in item]
    rel = path.relative_to(REPO_ROOT)
    assert hits, (
        f"{rel} has no list item naming `{ANCHOR}` -- the tool-preference "
        "sentence is missing (RED until W1-01)"
    )
    assert len(hits) == 1, (
        f"{rel} names `{ANCHOR}` in {len(hits)} list items; the rule must be "
        "stated once so the two statements cannot drift apart"
    )
    start = end = hits[0]
    while start - 1 >= 0 and any(v in items[start - 1] for v in PASSAGE_VOCAB):
        start -= 1
    while end + 1 < len(items) and any(v in items[end + 1] for v in PASSAGE_VOCAB):
        end += 1
    return " ".join(items[start : end + 1])


def _normalise(passage: str) -> str:
    """Collapse whitespace and strip list markers, for copy-vs-copy equality."""
    stripped = re.sub(r"^\s*[-*]\s+", "", passage)
    stripped = re.sub(r"\s*[-*]\s+", " ", stripped)
    return " ".join(stripped.split())


def _forbidden_read_tools(passage: str) -> list[str]:
    """Read/search tools this passage forbids. Empty means it forbids none.

    Method: cut the passage into clauses, keep only clauses containing a
    prohibition word, and look for read-tool names inside those. A read tool
    named in a non-prohibiting clause ("read and search however is cheapest")
    is the sentence doing its job, not a violation -- which is exactly the
    distinction `test_the_read_detector_itself_is_calibrated` pins down.
    """
    offenders: list[str] = []
    for clause in re.split(CLAUSE_SPLIT, passage):
        if not re.search(PROHIBITION, clause, re.IGNORECASE):
            continue
        for pattern in READ_TOOLS:
            if re.search(pattern, clause, re.IGNORECASE):
                offenders.append(f"{pattern} in clause {clause.strip()!r}")
    return offenders


def _version(path: Path) -> tuple[int, ...]:
    raw = json.loads(path.read_text(encoding="utf-8"))["version"]
    return tuple(int(part) for part in raw.split("."))


# --------------------------------------------------------------------------
# surface (2), calibration -- the detector before what it detects
# --------------------------------------------------------------------------


CALIBRATION = [
    # (id, sentence, expect_offenders)
    (
        "forbids-reading",
        "Never use cat or sed to touch files.",
        True,
    ),
    (
        "permits-reading",
        "Read and search however is cheapest.",
        False,
    ),
    (
        "tricky-both-in-one",
        "Edit files with Edit/Write or apply_patch; never `sed -i` or "
        "heredocs; read and search however is cheapest.",
        False,
    ),
    (
        "tricky-em-dash",
        "Write through the host's edit tool -- never `sed -i`, never a "
        "heredoc -- but grep and cat are fine.",
        False,
    ),
    (
        "sneaky-prohibits-grep",
        "Do not grep; use the Glob tool.",
        True,
    ),
]


@pytest.mark.parametrize(
    "sentence,expect", [(s, e) for _, s, e in CALIBRATION],
    ids=[i for i, _, _ in CALIBRATION],
)
def test_the_read_detector_itself_is_calibrated(sentence: str, expect: bool) -> None:
    """Surface (2), calibration. GREEN NOW -- it tests the probe, not the repo.

    A detector nobody tested is an assertion that asserts nothing. The
    load-bearing case is `tricky-both-in-one`: the real sentence contains a
    prohibition AND the word "read" a few words apart, and a naive
    `never.*read` regex marks the correct wording as a violation. If this
    case ever goes red, case (2) below is lying in whichever direction this
    one broke.
    """
    offenders = _forbidden_read_tools(sentence)
    assert bool(offenders) is expect, (
        f"detector said {offenders!r} for {sentence!r}; expected "
        f"{'a violation' if expect else 'no violation'}"
    )


# --------------------------------------------------------------------------
# surface (1) -- the passage exists in all four contracts and is capped
# --------------------------------------------------------------------------


@pytest.mark.parametrize("role", sorted(CONTRACTS), ids=sorted(CONTRACTS))
def test_every_contract_carries_a_capped_tool_preference_passage(role: str) -> None:
    """Surface (1). RED until W1-01.

    All four contracts, not three: an agent reads only its own file, so a
    contract without the sentence is an agent that never sees the rule.
    reviewer.md is included even though it edits nothing -- there the
    sentence is the boundary condition on the one case where it would.
    <= 40 words by `len(str.split())`; `wc` is banned repo-wide.
    """
    passage = _passage(CONTRACTS[role])
    for token in ("sed -i", "heredoc"):
        if token in passage:
            break
    else:
        pytest.fail(
            f"agents/{role}.md tool-preference passage names neither `sed -i` "
            "nor `heredoc`; it says what to use without saying what it "
            "replaces, which is the half a hurried reader skips"
        )
    assert re.search(r"\bEdit\b|\bWrite\b", passage), (
        f"agents/{role}.md tool-preference passage never names the host edit "
        "tool (`Edit`/`Write`); `apply_patch` alone leaves Claude Code unsaid"
    )
    words = len(passage.split())
    assert words <= WORD_CAP, (
        f"agents/{role}.md tool-preference passage is {words} words, cap is "
        f"{WORD_CAP} (intent Constraints: <= 40 English words per place)"
    )


# --------------------------------------------------------------------------
# surface (2) -- it regulates writing, never reading
# --------------------------------------------------------------------------


@pytest.mark.parametrize("role", sorted(CONTRACTS), ids=sorted(CONTRACTS))
def test_passage_forbids_no_read_or_search_tool(role: str) -> None:
    """Surface (2). RED until W1-01 (the passage must exist to be clean).

    intent Proposed outcome 1 is "只管寫" -- writing only. A sentence that
    also forbids `cat`/`grep` would fight the host reminder on ground where
    the reminder is right (shell reads really are cheaper) and would give a
    weak reader a reason to discard the whole rule as overreach.
    """
    offenders = _forbidden_read_tools(_passage(CONTRACTS[role]))
    assert not offenders, (
        f"agents/{role}.md tool-preference passage forbids reading/searching: "
        + "; ".join(offenders)
    )


# --------------------------------------------------------------------------
# surface (3) -- it survives a reminder that arrives mid-task
# --------------------------------------------------------------------------


@pytest.mark.parametrize("role", sorted(CONTRACTS), ids=sorted(CONTRACTS))
def test_passage_overrides_a_later_host_reminder(role: str) -> None:
    """Surface (3). RED until W1-01.

    The measured fact (intent Problem, point 3) is that the contrary reminder
    is NOT in the launch context; it appears beside the first tool result. So
    "prefer Edit" is satisfied by an agent that preferred Edit once and then
    obeyed the reminder. The passage has to name the later arrival explicitly.
    """
    passage = _passage(CONTRACTS[role])
    low = passage.lower()
    assert re.search(r"\breminder\b|\bhost\b|\binstruction\b", low), (
        f"agents/{role}.md tool-preference passage never mentions the host "
        "reminder it is supposed to outrank"
    )
    assert re.search(r"\blater\b|\bany time\b|\banytime\b|\bmid-task\b|\bafter\b", low), (
        f"agents/{role}.md tool-preference passage does not say the override "
        "covers a reminder that appears LATER; an agent that obeyed the rule "
        "on its first edit and switched on its second is compliant with the "
        "weaker wording"
    )


# --------------------------------------------------------------------------
# surface (4) -- the two copies are one string
# --------------------------------------------------------------------------


def test_build_dispatch_copy_is_verbatim_the_implementer_copy() -> None:
    """Surface (4). RED until W1-01.

    `build/SKILL.md`'s "And these standing trap-guards, verbatim:" block is
    pasted into every implementer dispatch packet, and implementer.md is read
    by that same agent. Compared as whitespace-normalised strings, so a
    reflow is not a failure and a reworded clause is.

    Note for the implementer: the two blocks are NOT verbatim identical today
    (build has a `git stash` guard implementer.md lacks, and says "a guard or
    hook" where implementer.md says "a guard"). This case pins only the NEW
    passage, which is the copy this change creates.
    """
    build = _normalise(_passage(BUILD_SKILL))
    impl = _normalise(_passage(CONTRACTS["implementer"]))
    assert build == impl, (
        "the tool-preference passage differs between build/SKILL.md and "
        "agents/implementer.md; two hand-maintained copies that already "
        "disagree must not gain a third disagreement.\n"
        f"  build/SKILL.md: {build!r}\n"
        f"  implementer.md: {impl!r}"
    )


# --------------------------------------------------------------------------
# surface (5) -- portable, no docs/ path
# --------------------------------------------------------------------------


@pytest.mark.parametrize("role", sorted(CONTRACTS), ids=sorted(CONTRACTS))
def test_passage_cites_no_repo_local_path(role: str) -> None:
    """Surface (5). RED until W1-01.

    A dispatched agent resolves paths against the repository it is standing
    in, so a contract citing `docs/...` is unresolvable everywhere but here.
    CLAUDE.md Contract Citations calls this a portability defect, not style.
    """
    passage = _passage(CONTRACTS[role])
    assert "docs/" not in passage, (
        f"agents/{role}.md tool-preference passage cites a `docs/` path; an "
        "agent dispatched into an adopting repo cannot resolve it"
    )


# --------------------------------------------------------------------------
# surface (6) -- the escape hatch costs something checkable
# --------------------------------------------------------------------------


@pytest.mark.parametrize("role", sorted(CONTRACTS), ids=sorted(CONTRACTS))
def test_bulk_replace_escape_hatch_names_two_checkable_actions(role: str) -> None:
    """Surface (6). RED until W1-01.

    A rule with no escape hatch gets ignored wholesale the first time a
    genuine cross-file rename shows up. A hatch with no price gets used every
    time. So the hatch must exist AND cost two things an agent can be seen to
    have done -- count the matches, show the diff -- rather than a judgement
    like "when a script is more appropriate", which recomputes to nothing.
    """
    passage = _passage(CONTRACTS[role])
    low = passage.lower()
    assert re.search(r"\bscript|\bbulk\b|\bmechanical\b|\bsweep\b", low), (
        f"agents/{role}.md tool-preference passage has no bulk-replace escape "
        "hatch; a blanket ban is a rule that gets dropped whole at the first "
        "real cross-file rename"
    )
    assert re.search(r"\bcount", low), (
        f"agents/{role}.md escape hatch never asks for a match count -- the "
        "check that catches a BSD `sed -i` that silently matched nothing"
    )
    assert re.search(r"\bdiff\b", low), (
        f"agents/{role}.md escape hatch never asks for the diff -- without it "
        "the count is self-reported and unverifiable"
    )


# --------------------------------------------------------------------------
# surface (9) -- the new sentence must not trip a shipped test
# --------------------------------------------------------------------------


@pytest.mark.parametrize("role", CAPPED_AGENTS, ids=CAPPED_AGENTS)
def test_passage_avoids_the_deleted_vocabulary(role: str) -> None:
    """Surface (9), adversary-added. RED until W1-01.

    `test_reviewer_agent_single_contract.py::test_no_deleted_vocabulary`
    fails these three files on `\\bbatch\\b`, `\\bbrief\\b`, `\\bpacket\\b`
    and friends, case-insensitively, anywhere in the file. The natural
    English for surface (6) -- "a batch replace may be scripted" -- turns
    that shipped test red in three files at once. Say "bulk" or "mechanical".
    """
    passage = _passage(CONTRACTS[role])
    offenders = [p for p in DELETED_VOCAB_AT_RISK if re.search(p, passage, re.IGNORECASE)]
    assert not offenders, (
        f"agents/{role}.md tool-preference passage uses deleted vocabulary "
        f"{offenders}; the shipped test_no_deleted_vocabulary bans it in this "
        "file"
    )


# --------------------------------------------------------------------------
# surface (7) -- the shipped caps still hold after the sentence lands
# --------------------------------------------------------------------------


def test_agent_bodies_still_fit_the_shipped_caps() -> None:
    """Surface (7). GREEN NOW -- a regression guard, and a live warning.

    Caps and the body extractor are imported from the shipped test, never
    re-declared. Green today at reviewer 1279 / cap 1300: TWENTY-ONE words of
    headroom for a passage capped at forty. W1-01 cannot land the sentence in
    reviewer.md without compressing something else first -- and per plan
    Risk (b) the thing compressed must not be the new sentence, which is this
    change's load-bearing text.
    """
    module = _shipped_caps_module()
    caps = module.AGENT_CAPS
    body_of = module.body_of
    over = []
    for name, cap in sorted(caps.items()):
        path = AGENTS / name
        assert path.is_file(), f"agents/{name} is missing"
        words = len(body_of(path.read_text(encoding="utf-8")).split())
        if words > cap:
            over.append(f"agents/{name}: {words} words (cap {cap})")
    assert not over, (
        "adding the tool-preference passage pushed an agent contract past its "
        "shipped word cap: " + "; ".join(over) + ". Compress other prose in "
        "the same file; do not raise AGENT_CAPS and do not trim the new "
        "passage away."
    )


# --------------------------------------------------------------------------
# surface (8) -- version bump on both manifests, and a changelog entry
# --------------------------------------------------------------------------


@pytest.mark.parametrize("host", sorted(PLUGIN_JSONS), ids=sorted(PLUGIN_JSONS))
def test_both_manifests_bumped_past_the_baseline(host: str) -> None:
    """Surface (8), version half. RED until W1-02.

    Shipping changed skill/agent prose without a bump makes `plugin update` a
    silent no-op for every consumer (repo memory). Both manifests, because
    the Codex mirror is what a Codex-hosted reviewer loads. Compared as an
    integer tuple: "1.2.10" sorts BEFORE "1.2.9" as a string.
    """
    version = _version(PLUGIN_JSONS[host])
    assert version > BASELINE_VERSION, (
        f"{PLUGIN_JSONS[host].relative_to(REPO_ROOT)} is still "
        + ".".join(str(n) for n in version)
        + "; a contract-text change must bump past "
        + ".".join(str(n) for n in BASELINE_VERSION)
    )


def test_manifests_agree_and_the_changelog_carries_the_version() -> None:
    """Surface (8), consistency half. GREEN NOW -- a regression guard.

    Green because both manifests read 1.2.1 today and the CHANGELOG carries
    `[1.2.1]`. It is pinned before W1-02 so that bumping ONE manifest, or
    bumping both without a CHANGELOG entry, turns it red rather than sliding
    through on the version test alone.

    The two manifests must bump together -- a Codex mirror one patch behind
    is exactly the drift `test_sync_codex_manifest.py` exists to stop -- and
    the version the manifests declare must have a CHANGELOG entry, or the
    consumer who does update cannot tell what changed.
    """
    versions = {host: _version(path) for host, path in PLUGIN_JSONS.items()}
    assert len(set(versions.values())) == 1, (
        f"manifest versions disagree: "
        + ", ".join(
            f"{h}={'.'.join(str(n) for n in v)}" for h, v in sorted(versions.items())
        )
    )
    version = ".".join(str(n) for n in next(iter(versions.values())))
    changelog = CHANGELOG.read_text(encoding="utf-8")
    assert f"[{version}]" in changelog, (
        f"loom-code/CHANGELOG.md has no `[{version}]` entry for the version "
        "the manifests now declare"
    )


# --------------------------------------------------------------------------
# surface (8b) -- the review station points at the contracts, not a 3rd copy
# --------------------------------------------------------------------------


def test_review_station_points_at_contracts_without_a_third_copy() -> None:
    """Surface (4)/(8b), plan W1-02. RED until W1-02.

    The review station's blind-runner and adversary dispatches must tell the
    dispatcher to carry the contract's trap section. They must NOT paste the
    sentence a third time: plan W1-02 chose "point, do not re-copy" precisely
    because two copies are already drifting. So the station names the trap
    section, and `apply_patch` appears nowhere in it.
    """
    text = REVIEW_SKILL.read_text(encoding="utf-8")
    assert ANCHOR not in text, (
        "review/SKILL.md pastes the tool-preference sentence itself; W1-02 "
        "requires it to point at the agent contract instead of minting a "
        "third copy that can drift"
    )
    assert re.search(r"trap", text, re.IGNORECASE), (
        "review/SKILL.md never tells its dispatches to carry the contract's "
        "trap section, so a blind-runner or adversary reaches the tool rule "
        "only if it reads its own contract closely"
    )
