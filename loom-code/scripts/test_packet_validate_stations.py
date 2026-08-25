"""Structural grep-window test guarding the packet fail-closed contract
(Task 5 round 2 of docs/loom/plans/2026-08-25-reviewer-packet-fail-closed.md).

SKILL.md is a prompt/contract artifact, not executable code: nothing
importable observes whether an orchestrator actually validates the
immutable context packet before fanning out reviewers. These files ARE
the instruction each orchestrator reads at its call site, so the
correctness condition is the PRESENCE of the load-bearing
`review_context.py --validate` refusal phrases inside each packet step
-- same convention as `test_review_scope_stations.py` (windowed per
call site: a whole-file substring check would pass if only one of the
three stations carried the clause).

Three call sites, three windows:
- requesting-code-review  §Process Step 1 ("Determine diff scope")
- requesting-docs-review  §Steps Step 1 ("Adopt a handed-down ... packet")
- subagent-driven-development §Per-task loop Step 3 ("If `status: DONE`")

The docs-review window additionally pins the adopt-path root binding
(round-2 finding 1: the verbatim-adopt branch forbids invoking
review_context.py for resolution, so without an explicit root lookup
the validator is unlocatable exactly where it matters) and the
tightened earlier pin "do not invoke review_context.py to re-resolve
it" (round-2 finding 3: the bare "do not invoke review_context.py"
contradicted the later validate call).

Stdlib + pytest only (pathlib, re).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

SKILLS = Path(__file__).parents[1] / "skills"
RCR_MD = SKILLS / "requesting-code-review" / "SKILL.md"
RDR_MD = SKILLS / "requesting-docs-review" / "SKILL.md"
SDD_MD = SKILLS / "subagent-driven-development" / "SKILL.md"

# The load-bearing validate call: the literal flag + packet-file
# placeholder, not just the script name (naming the script without
# --validate is the pre-fix state this arc replaced).
VALIDATE_CALL = re.compile(r"review_context\.py\"? --validate <packet-file>")

# The fail-closed refusal clause, identical across all three stations.
REFUSAL_PHRASE = "REFUSES the fan-out: do not dispatch any reviewer"

# Round-2 finding 1: the adopt path must bind a root for validation
# without re-resolving the packet.
RDR_ROOT_LOOKUP_ONLY = "root lookup only"
RDR_PACKET_STAYS_VERBATIM = "the packet itself stays verbatim"

# Round-2 finding 3: the tightened earlier pin. The untightened form
# ("do not invoke review_context.py" followed directly by sentence
# end) must be gone.
RDR_TIGHTENED_PIN = "do not invoke review_context.py to re-resolve it"
RDR_UNTIGHTENED_PIN = re.compile(
    r"do not invoke review_context\.py\**[.,;]"
)


def _read(path: Path) -> str:
    assert path.is_file(), f"SKILL.md is absent at {path}"
    return path.read_text(encoding="utf-8")


def _norm(s: str) -> str:
    """Collapse whitespace so a re-wrapped line still matches."""
    return re.sub(r"\s+", " ", s).strip()


def _numbered_step_section(
    text: str, start_pattern: str, label: str, where: str
) -> str:
    """Isolate one numbered-list step: from the column-0 line matching
    `start_pattern` to the next column-0 `<digit>. ` line, or EOF."""
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if re.match(start_pattern, line):
            start = i
            break
    assert start is not None, (
        f"{where} carries no '{label}' line -- the packet step must be "
        "findable, not absent"
    )
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.match(r"^\d+\.\s", lines[j]):
            end = j
            break
    return "".join(lines[start:end])


def _rcr_packet_step() -> str:
    return _numbered_step_section(
        _read(RCR_MD),
        r"^1\.\s+\*\*Determine diff scope",
        "1. **Determine diff scope**",
        "requesting-code-review/SKILL.md",
    )


def _rdr_packet_step() -> str:
    return _numbered_step_section(
        _read(RDR_MD),
        r"^1\.\s+\*\*Adopt a handed-down immutable context packet",
        "1. **Adopt a handed-down immutable context packet**",
        "requesting-docs-review/SKILL.md",
    )


def _sdd_packet_step() -> str:
    return _numbered_step_section(
        _read(SDD_MD),
        r"^3\.\s+\*\*If `status: DONE`",
        "3. **If `status: DONE`**",
        "subagent-driven-development/SKILL.md",
    )


@pytest.mark.parametrize(
    "step_fn, where",
    [
        (_rcr_packet_step, "requesting-code-review §Process Step 1"),
        (_rdr_packet_step, "requesting-docs-review §Steps Step 1"),
        (_sdd_packet_step, "subagent-driven-development §Per-task Step 3"),
    ],
    ids=["rcr", "rdr", "sdd"],
)
def test_validate_call_present_at_each_station(step_fn, where):
    """Each packet step must carry the literal --validate invocation:
    naming the script without the flag is the pre-fix state."""
    section = _norm(step_fn())
    assert VALIDATE_CALL.search(section), (
        f"{where} must invoke `review_context.py --validate "
        "<packet-file>` on the packet before reviewer fan-out"
    )


@pytest.mark.parametrize(
    "step_fn, where",
    [
        (_rcr_packet_step, "requesting-code-review §Process Step 1"),
        (_rdr_packet_step, "requesting-docs-review §Steps Step 1"),
        (_sdd_packet_step, "subagent-driven-development §Per-task Step 3"),
    ],
    ids=["rcr", "rdr", "sdd"],
)
def test_refusal_clause_present_at_each_station(step_fn, where):
    """A validate call without the fail-closed consequence is advisory;
    the refusal clause is the load-bearing half."""
    section = _norm(step_fn())
    assert REFUSAL_PHRASE in section, (
        f"{where} must state that a non-zero --validate exit "
        f"'{REFUSAL_PHRASE}'"
    )


def test_rdr_adopt_path_binds_root_for_validation():
    """Round-2 finding 1: on the verbatim-adopt path no plugin root is
    otherwise in scope, so the step must explicitly bind one (root
    lookup only -- never packet re-resolution) before the validate
    call; without it the validator is unlocatable in the common
    delegated case."""
    section = _norm(_rdr_packet_step())
    assert RDR_ROOT_LOOKUP_ONLY in section, (
        "requesting-docs-review Step 1 must bind the adapter root for "
        "validation with the 'root lookup only' qualifier"
    )
    assert RDR_PACKET_STAYS_VERBATIM in section, (
        "requesting-docs-review Step 1 must state the adopted packet "
        "stays verbatim while the root is looked up"
    )
    # The binding must precede the validate call it enables.
    validate = VALIDATE_CALL.search(section)
    assert validate is not None
    assert section.index(RDR_ROOT_LOOKUP_ONLY) < validate.start(), (
        "the adopt-path root binding must appear before the "
        "--validate invocation it locates"
    )


def test_rdr_earlier_pin_tightened_to_re_resolve():
    """Round-2 finding 3: the earlier pin must forbid re-RESOLUTION
    specifically, not invocation outright -- the bare form contradicts
    the later validate call in the same step."""
    section = _norm(_rdr_packet_step())
    assert RDR_TIGHTENED_PIN in section, (
        "requesting-docs-review Step 1 must carry the tightened pin "
        f"'{RDR_TIGHTENED_PIN}'"
    )
    assert not RDR_UNTIGHTENED_PIN.search(section), (
        "the untightened 'do not invoke review_context.py.' form must "
        "be gone -- it reads as contradicting the validate call"
    )


def test_oracle_rejects_phrase_removed():
    """Prove the oracle discriminates: a synthetic step text with the
    --validate call stripped (the exact regression this file guards)
    must fail both pattern checks, independent of the real files."""
    mutated = _norm(
        "1. **Determine diff scope**. Keep the packet unchanged and "
        "run python3 scripts/review_context.py --repo <path> once. "
        "Dispatch reviewers with the packet copied verbatim."
    )
    assert not VALIDATE_CALL.search(mutated)
    assert REFUSAL_PHRASE not in mutated
