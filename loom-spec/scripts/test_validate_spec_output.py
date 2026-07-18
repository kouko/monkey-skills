"""Tests for validate_spec_output.py — OpenSpec skeleton checks (Task 2).

The validator checks a loom-spec OUTPUT DIRECTORY against the OpenSpec
change-folder SKELETON. Skeleton-valid iff:
  1. proposal.md present.
  2. specs/ subdir with >=1 *.md delta file.
  3. >=1 delta carries a `## ADDED Requirements` header.
  4. >=1 `### Requirement:` whose body line carries RFC-2119 (MUST/SHALL/SHOULD/MAY).
  5. >=1 `#### Scenario:` with GIVEN/WHEN/THEN lines beneath it.

Validator must be tolerant of EXTRA content (structure-only, mirrors
`openspec validate`). Fixtures built INLINE via tmp_path (flat-folder rule:
no fixtures/ subdir).

Task 3 will ADD additive-section checks (test_additive_*) to this same file.
"""

import subprocess
import sys
from pathlib import Path

from validate_spec_output import (
    validate,
    _check_evidence_needed_whitelist,
    _check_domain_convention_tier_label,
    _check_shaping_without_deferred,
)


SCRIPT = Path(__file__).with_name("validate_spec_output.py")


# --- fixture builders (inline; no fixtures/ subdir) -------------------------

def _well_formed_delta() -> str:
    return (
        "## ADDED Requirements\n"
        "\n"
        "### Requirement: User login\n"
        "The system MUST authenticate a user with valid credentials.\n"
        "\n"
        "#### Scenario: Valid credentials\n"
        "- GIVEN a registered user\n"
        "- WHEN they submit a correct password\n"
        "- THEN they are granted a session\n"
    )


def _well_formed_additive() -> str:
    """The additive sections loom-spec requires in proposal.md (the
    three-flow artifacts USM backbone / OOUX object model / Path × edge matrix
    plus Provenance and a non-empty Blind-spots body, plus the L2/L3
    Cross-object combinations / Journey navigation sections)."""
    return (
        "## USM backbone\n"
        "- Sign up → Log in → Use feature → Log out\n"
        "\n"
        "## OOUX object model\n"
        "- User (objects), Session (objects)\n"
        "\n"
        "## Provenance\n"
        "- User login: seeded\n"
        "- Lockout after N tries: critic-found\n"
        "\n"
        "## Blind spots — needs human/field input\n"
        "- Lockout threshold N is a policy call I cannot judge.\n"
        "\n"
        "## Path × edge matrix\n"
        "| path | edge |\n"
        "| --- | --- |\n"
        "| login | wrong password |\n"
        "\n"
        "## Cross-object combinations\n"
        "- User × Session: one user holds many sessions\n"
        "\n"
        "## Journey navigation\n"
        "- From login screen → dashboard → feature\n"
    )


def _write_skeleton(root: Path, *, delta_body: str | None = None,
                    with_proposal: bool = True,
                    proposal_body: str | None = None) -> Path:
    """Build a skeleton output dir under root; return root.

    `proposal_body`, when given, is the full proposal.md content (lets
    additive tests control which sections are present)."""
    if with_proposal:
        content = ("# Proposal\n\nWhy this change.\n\n" + _well_formed_additive()
                   if proposal_body is None else proposal_body)
        (root / "proposal.md").write_text(content, encoding="utf-8")
    specs = root / "specs" / "auth"
    specs.mkdir(parents=True, exist_ok=True)
    body = _well_formed_delta() if delta_body is None else delta_body
    (specs / "spec.md").write_text(body, encoding="utf-8")
    return root


# --- skeleton tests --------------------------------------------------------

def test_skeleton_accepts_well_formed(tmp_path):
    root = _write_skeleton(tmp_path)
    ok, problems = validate(root)
    assert ok, f"well-formed skeleton should pass, got: {problems}"
    assert problems == []


def test_skeleton_rejects_missing_proposal(tmp_path):
    root = _write_skeleton(tmp_path, with_proposal=False)
    ok, problems = validate(root)
    assert not ok
    assert any("proposal.md" in p for p in problems), problems


def test_skeleton_rejects_missing_specs_dir(tmp_path):
    (tmp_path / "proposal.md").write_text("# Proposal\n", encoding="utf-8")
    ok, problems = validate(tmp_path)
    assert not ok
    assert any("specs/" in p for p in problems), problems


def test_skeleton_rejects_missing_added_requirements(tmp_path):
    body = (
        "### Requirement: User login\n"
        "The system MUST authenticate a user.\n"
        "\n"
        "#### Scenario: Valid\n"
        "- GIVEN a user\n- WHEN login\n- THEN session\n"
    )
    root = _write_skeleton(tmp_path, delta_body=body)
    ok, problems = validate(root)
    assert not ok
    assert any("ADDED Requirements" in p for p in problems), problems


def test_skeleton_rejects_requirement_without_rfc2119(tmp_path):
    body = (
        "## ADDED Requirements\n"
        "\n"
        "### Requirement: User login\n"
        "The system authenticates a user with valid credentials.\n"
        "\n"
        "#### Scenario: Valid\n"
        "- GIVEN a user\n- WHEN login\n- THEN session\n"
    )
    root = _write_skeleton(tmp_path, delta_body=body)
    ok, problems = validate(root)
    assert not ok
    assert any("RFC-2119" in p or "MUST" in p for p in problems), problems


def test_skeleton_rejects_missing_scenario(tmp_path):
    body = (
        "## ADDED Requirements\n"
        "\n"
        "### Requirement: User login\n"
        "The system MUST authenticate a user.\n"
    )
    root = _write_skeleton(tmp_path, delta_body=body)
    ok, problems = validate(root)
    assert not ok
    assert any("Scenario" in p for p in problems), problems


def test_skeleton_rejects_scenario_missing_given_when_then(tmp_path):
    body = (
        "## ADDED Requirements\n"
        "\n"
        "### Requirement: User login\n"
        "The system MUST authenticate a user.\n"
        "\n"
        "#### Scenario: Valid\n"
        "- GIVEN a user\n"
        "- WHEN they login\n"
    )  # missing THEN
    root = _write_skeleton(tmp_path, delta_body=body)
    ok, problems = validate(root)
    assert not ok
    assert any("THEN" in p for p in problems), problems


def test_skeleton_accepts_modified_only_delta(tmp_path):
    # An OpenSpec change whose delta is ONLY a `## MODIFIED Requirements`
    # block (no ## ADDED) is valid: a change may ADD / MODIFY / REMOVE.
    body = (
        "## MODIFIED Requirements\n"
        "\n"
        "### Requirement: User login\n"
        "The system MUST authenticate a user with valid credentials.\n"
        "\n"
        "#### Scenario: Valid credentials\n"
        "- GIVEN a registered user\n"
        "- WHEN they submit a correct password\n"
        "- THEN they are granted a session\n"
    )
    root = _write_skeleton(tmp_path, delta_body=body)
    ok, problems = validate(root)
    assert ok, f"MODIFIED-only delta should pass, got: {problems}"
    assert problems == []


def test_skeleton_tolerates_extra_content(tmp_path):
    body = _well_formed_delta() + (
        "\n## Some Unknown Section\n"
        "Extra prose the validator must not reject.\n"
        "\n### MODIFIED Requirements\n"
        "### Requirement: Other\n"
        "Whatever SHOULD happen.\n"
    )
    root = _write_skeleton(tmp_path, delta_body=body)
    ok, problems = validate(root)
    assert ok, f"extra content must be tolerated, got: {problems}"


# --- additive-section tests (Task 3) ---------------------------------------
# loom-spec's differentiating richness lives in proposal.md's additive
# sections; the OpenSpec delta under specs/ stays pure. So additive checks
# operate on proposal.md.

def _proposal_with(*, usm=True, ooux=True, provenance=True, blind_spots=True,
                   blind_spots_empty=False, matrix=True,
                   cross_object=True, journey=True) -> str:
    parts = ["# Proposal\n\nWhy this change.\n"]
    if usm:
        parts.append("## USM backbone\n- Sign up → Log in → Use feature\n")
    if ooux:
        parts.append("## OOUX object model\n- User (objects), Session (objects)\n")
    if provenance:
        parts.append("## Provenance\n- User login: seeded\n")
    if blind_spots:
        if blind_spots_empty:
            parts.append("## Blind spots — needs human/field input\n")
        else:
            parts.append("## Blind spots — needs human/field input\n"
                         "- Lockout threshold is a policy call I cannot judge.\n")
    if matrix:
        parts.append("## Path × edge matrix\n| path | edge |\n| --- | --- |\n"
                     "| login | wrong password |\n")
    if cross_object:
        parts.append("## Cross-object combinations\n"
                     "- User × Session: one user holds many sessions\n")
    if journey:
        parts.append("## Journey navigation\n"
                     "- From login screen → dashboard → feature\n")
    return "\n".join(parts)


def test_additive_rejects_missing_usm_backbone(tmp_path):
    root = _write_skeleton(tmp_path, proposal_body=_proposal_with(usm=False))
    ok, problems = validate(root)
    assert not ok
    assert any("USM backbone" in p for p in problems), problems


def test_additive_rejects_missing_ooux_object_model(tmp_path):
    root = _write_skeleton(tmp_path, proposal_body=_proposal_with(ooux=False))
    ok, problems = validate(root)
    assert not ok
    assert any("OOUX object model" in p for p in problems), problems


def test_additive_usm_prose_mention_does_not_satisfy(tmp_path):
    # A prose mention of "USM backbone" must NOT count — whole-line header only.
    body = _proposal_with(usm=False)
    body += "\nWe considered a USM backbone here but did not add the section.\n"
    root = _write_skeleton(tmp_path, proposal_body=body)
    ok, problems = validate(root)
    assert not ok
    assert any("USM backbone" in p for p in problems), problems


def test_additive_rejects_missing_provenance(tmp_path):
    root = _write_skeleton(tmp_path, proposal_body=_proposal_with(provenance=False))
    ok, problems = validate(root)
    assert not ok
    assert any("Provenance" in p for p in problems), problems


def test_additive_rejects_missing_blind_spots(tmp_path):
    root = _write_skeleton(tmp_path, proposal_body=_proposal_with(blind_spots=False))
    ok, problems = validate(root)
    assert not ok
    assert any("Blind spots" in p for p in problems), problems


def test_additive_rejects_empty_blind_spots(tmp_path):
    root = _write_skeleton(
        tmp_path, proposal_body=_proposal_with(blind_spots_empty=True))
    ok, problems = validate(root)
    assert not ok
    assert any("Blind spots" in p for p in problems), problems


def test_additive_rejects_missing_path_edge_matrix(tmp_path):
    root = _write_skeleton(tmp_path, proposal_body=_proposal_with(matrix=False))
    ok, problems = validate(root)
    assert not ok
    assert any("Path × edge matrix" in p for p in problems), problems


def _proposal_five_original_only() -> str:
    """The five ORIGINAL additive sections, but MISSING the two L2/L3 sections
    (Cross-object combinations / Journey navigation)."""
    return (
        "# Proposal\n\nWhy this change.\n"
        "\n## USM backbone\n- Sign up → Log in → Use feature\n"
        "\n## OOUX object model\n- User (objects), Session (objects)\n"
        "\n## Provenance\n- User login: seeded\n"
        "\n## Blind spots — needs human/field input\n"
        "- Lockout threshold is a policy call I cannot judge.\n"
        "\n## Path × edge matrix\n| path | edge |\n| --- | --- |\n"
        "| login | wrong password |\n"
    )


def test_rejects_missing_cross_object_and_journey(tmp_path):
    root = _write_skeleton(tmp_path, proposal_body=_proposal_five_original_only())
    ok, problems = validate(root)
    assert not ok
    assert any("Cross-object combinations" in p for p in problems), problems
    assert any("Journey navigation" in p for p in problems), problems


def test_additive_accepts_complete_hybrid(tmp_path):
    root = _write_skeleton(tmp_path, proposal_body=_proposal_with())
    ok, problems = validate(root)
    assert ok, f"complete hybrid (skeleton + 5 additive) should pass, got: {problems}"
    assert problems == []


def test_additive_accepts_complete_hybrid_cli(tmp_path):
    root = _write_skeleton(tmp_path, proposal_body=_proposal_with())
    proc = _run_cli(root)
    assert proc.returncode == 0, proc.stderr + proc.stdout


# --- CLI contract (thin __main__) ------------------------------------------

def _run_cli(target: Path):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(target)],
        capture_output=True, text=True,
        env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": ""},
    )


def test_cli_exit_zero_on_valid(tmp_path):
    root = _write_skeleton(tmp_path)
    proc = _run_cli(root)
    assert proc.returncode == 0, proc.stderr + proc.stdout


def test_cli_nonzero_with_actionable_message_on_invalid(tmp_path):
    root = _write_skeleton(tmp_path, with_proposal=False)
    proc = _run_cli(root)
    assert proc.returncode != 0
    combined = proc.stdout + proc.stderr
    assert "proposal.md" in combined, combined


# --- evidence_needed tag checks (Task 14, cut (a)) --------------------------
# Literal strings copied VERBATIM from the leg-1 haiku dogfood artifact
# (docs/loom/dogfood/2026-07-18-knowledge-triage-live-spec-leg.md
# "Weak-model leg" section) proving each check catches the REAL failure it
# was written against, not a synthetic stand-in.

_LEG1_INVENTED_TECHNICAL_CONSTRAINT = (
    "| **Concurrency** | **FLAG** | Multiple position updates in same month; "
    "race condition risk on aggregation. Locking strategy needed "
    "(evidence_needed: technical-constraint). |\n"
)

_LEG1_INVENTED_AUDIT_LOG_FORMAT = (
    "#### Scenario: Audit trail for position changes\n"
    "- GIVEN multiple trades affecting the same position in a month\n"
    "- WHEN report is generated\n"
    "- THEN report includes trade_count and a snapshot of all trades that "
    "contributed to each position (evidence_needed: audit-log-format)\n"
)

_LEG1_UNTIERED_DOMAIN_CONVENTION = (
    "| **Settlement lag** | **FLAG** | Trades settle 2–3 business days after "
    "trade date. Which date controls monthly bucketing? Trade date or "
    "settlement date? (evidence_needed: domain-convention) |\n"
)


def _write_tag_fixture(tmp_path: Path, *, proposal_extra: str = "",
                       spec_extra: str = "") -> Path:
    """Minimal proposal.md + specs/<cap>/spec.md for isolated evidence_needed
    tag-check tests. Skeleton/additive checks are exercised separately
    (above) via _write_skeleton; these tests call the tag-check functions
    directly so a missing '## ADDED Requirements' etc. never masks the tag
    assertion under test."""
    (tmp_path / "proposal.md").write_text(
        "# Proposal\n\n" + proposal_extra, encoding="utf-8")
    specs = tmp_path / "specs" / "cap"
    specs.mkdir(parents=True, exist_ok=True)
    (specs / "spec.md").write_text("# Spec\n\n" + spec_extra, encoding="utf-8")
    return tmp_path


# --- (1) evidence_needed value whitelist ------------------------------------

def test_evidence_needed_whitelist_rejects_leg1_technical_constraint(tmp_path):
    root = _write_tag_fixture(
        tmp_path, proposal_extra=_LEG1_INVENTED_TECHNICAL_CONSTRAINT)
    problems = _check_evidence_needed_whitelist(root)
    assert any("technical-constraint" in p and "proposal.md" in p
               for p in problems), problems


def test_evidence_needed_whitelist_rejects_leg1_audit_log_format(tmp_path):
    root = _write_tag_fixture(
        tmp_path, spec_extra=_LEG1_INVENTED_AUDIT_LOG_FORMAT)
    problems = _check_evidence_needed_whitelist(root)
    assert any("audit-log-format" in p and "spec.md" in p
               for p in problems), problems


def test_evidence_needed_whitelist_accepts_all_three_pinned_values(tmp_path):
    body = (
        "- A: evidence_needed: craft\n"
        "- B: evidence_needed: domain-convention\n"
        "- C: evidence_needed: project-local\n"
    )
    root = _write_tag_fixture(tmp_path, proposal_extra=body)
    assert _check_evidence_needed_whitelist(root) == []


# --- (2) SHAPING/DEFERRABLE tier-label presence -----------------------------

def test_tier_label_rejects_leg1_untiered_domain_convention(tmp_path):
    # This IS leg-1's real failure: the tag survived, the tier label did not.
    root = _write_tag_fixture(
        tmp_path, proposal_extra=_LEG1_UNTIERED_DOMAIN_CONVENTION)
    problems = _check_domain_convention_tier_label(root)
    assert any("SHAPING or DEFERRABLE" in p for p in problems), problems


def test_tier_label_accepts_compliant_same_line_shaping(tmp_path):
    body = (
        "- FLAG — SHAPING open question: settlement-date vs trade-date "
        "month bucketing convention is unresolved. evidence_needed: "
        "domain-convention; deferred: obligations stated hold under either "
        "answer, pending domain research.\n"
    )
    root = _write_tag_fixture(tmp_path, proposal_extra=body)
    assert _check_domain_convention_tier_label(root) == []


def test_tier_label_accepts_compliant_deferrable(tmp_path):
    body = (
        "- FLAG — DEFERRABLE open question: currency rounding display "
        "precision. evidence_needed: domain-convention.\n"
    )
    root = _write_tag_fixture(tmp_path, proposal_extra=body)
    assert _check_domain_convention_tier_label(root) == []


def test_tier_label_accepts_strong_leg_html_comment_style(tmp_path):
    # Second emission style seen in the wild: the tag rides an HTML comment,
    # the tier label + deferred reason ride the visible prose beneath it.
    body = (
        "<!-- evidence_needed: domain-convention -->\n"
        "**Open question (SHAPING):** trade-date vs settlement-date month "
        "attribution — 約定日 vs 受渡日 (JP brokerage convention).\n"
        "deferred: pending domain research; obligations stated hold under "
        "either answer.\n"
    )
    root = _write_tag_fixture(tmp_path, proposal_extra=body)
    assert _check_domain_convention_tier_label(root) == []
    assert _check_shaping_without_deferred(root) == []


# --- (3) SHAPING-without-deferred = VERIFY gate encoding --------------------

def test_shaping_without_deferred_rejects(tmp_path):
    body = (
        "- FLAG — SHAPING open question: settlement-date vs trade-date "
        "month bucketing convention is unresolved. evidence_needed: "
        "domain-convention.\n"  # no deferred: reason
    )
    root = _write_tag_fixture(tmp_path, proposal_extra=body)
    problems = _check_shaping_without_deferred(root)
    assert any("VERIFY" in p for p in problems), problems


def test_shaping_without_deferred_accepts_with_reason(tmp_path):
    body = (
        "- FLAG — SHAPING open question: settlement-date vs trade-date "
        "month bucketing convention is unresolved. evidence_needed: "
        "domain-convention; deferred: obligations stated hold under either "
        "answer, pending domain research.\n"
    )
    root = _write_tag_fixture(tmp_path, proposal_extra=body)
    assert _check_shaping_without_deferred(root) == []


def test_shaping_without_deferred_ignores_deferrable_class(tmp_path):
    # DEFERRABLE items never need a deferred: reason — only SHAPING does.
    body = (
        "- FLAG — DEFERRABLE open question: currency rounding display "
        "precision. evidence_needed: domain-convention.\n"
    )
    root = _write_tag_fixture(tmp_path, proposal_extra=body)
    assert _check_shaping_without_deferred(root) == []


# --- full validate() integration --------------------------------------------

def test_validate_full_rejects_leg1_artifact_style(tmp_path):
    proposal_body = _proposal_with() + "\n" + _LEG1_UNTIERED_DOMAIN_CONVENTION
    root = _write_skeleton(
        tmp_path,
        proposal_body=proposal_body,
        delta_body=_well_formed_delta() + "\n" + _LEG1_INVENTED_AUDIT_LOG_FORMAT,
    )
    ok, problems = validate(root)
    assert not ok
    assert any("audit-log-format" in p for p in problems), problems
    assert any("SHAPING or DEFERRABLE" in p for p in problems), problems


def test_validate_full_accepts_compliant_two_tier_fixture(tmp_path):
    tag_block = (
        "\n## Open questions\n"
        "- FLAG — SHAPING open question: settlement-date vs trade-date "
        "month bucketing convention. evidence_needed: domain-convention; "
        "deferred: obligations stated hold under either answer.\n"
        "- FLAG — DEFERRABLE open question: currency rounding precision. "
        "evidence_needed: domain-convention.\n"
    )
    root = _write_skeleton(tmp_path, proposal_body=_proposal_with() + tag_block)
    ok, problems = validate(root)
    assert ok, f"compliant two-tier fixture should pass, got: {problems}"


def test_validate_full_accepts_strong_leg_html_comment_style(tmp_path):
    tag_block = (
        "\n<!-- evidence_needed: domain-convention -->\n"
        "**Open question (SHAPING):** trade-date vs settlement-date month "
        "attribution.\n"
        "deferred: pending domain research; obligations stated hold under "
        "either answer.\n"
    )
    root = _write_skeleton(tmp_path, proposal_body=_proposal_with() + tag_block)
    ok, problems = validate(root)
    assert ok, f"strong-leg HTML-comment fixture should pass, got: {problems}"


# --- structural scoping (round-2 fix: replace fixed-radius window) ---------
# The round-1 fixed ±200-char window violated the plan's own wording ("same
# list item / comment block / heading section") and broke four ways on real
# acceptance data: strong-leg false positives (governing SHAPING header out
# of range), strong-leg false negatives (adjacent DEFERRABLE list's header
# leaks in), and cross-tag compliance borrowing (a sibling item's tier label
# or deferred: reason satisfying THIS item). These tests encode the
# structural-scope boundary the fix must hold: OWN SCOPE (the tag's own list
# item / paragraph) + GOVERNING HEADER (the immediately enclosing block's
# lead-in line or heading) — never a sibling's or a different block's.

def test_adjacent_items_one_tiered_one_untiered_flags_only_untiered(tmp_path):
    # (a) Two adjacent bullet items sharing one block (no blank line between
    # them). Item A carries its own SHAPING tier label; item B has none. A
    # fixed-radius window lets item B borrow item A's nearby "SHAPING" word
    # (cross-tag contamination) — the round-1 bug. Structural scope must not.
    body = (
        "- Item A — SHAPING open question about X. "
        "evidence_needed: domain-convention.\n"
        "- Item B — open question about Y with no tier label nearby. "
        "evidence_needed: domain-convention.\n"
    )
    root = _write_tag_fixture(tmp_path, proposal_extra=body)
    problems = _check_domain_convention_tier_label(root)
    # Exactly one flagged occurrence: item B's tag (proposal.md line 4 —
    # "# Proposal\n\n" prefix consumes lines 1-2, item A is line 3).
    assert len(problems) == 1, problems
    assert "proposal.md:4" in problems[0], problems


def test_adjacent_shaping_items_one_with_own_deferred_flags_only_missing(tmp_path):
    # (b) Two adjacent SHAPING items sharing one block. Item A has its own
    # deferred: reason; item B does not. A fixed-radius window lets item B
    # borrow item A's nearby "deferred: ..." text (round-1 bug). Structural
    # scope must require the deferred: reason to sit in the item's OWN SCOPE.
    body = (
        "- Item A — SHAPING open question. evidence_needed: "
        "domain-convention; deferred: reason A given right here.\n"
        "- Item B — SHAPING open question. evidence_needed: "
        "domain-convention.\n"
    )
    root = _write_tag_fixture(tmp_path, proposal_extra=body)
    problems = _check_shaping_without_deferred(root)
    # Item B's tag is on proposal.md line 4 (item A is line 3).
    assert len(problems) == 1, problems
    assert "proposal.md:4" in problems[0], problems


def test_shaping_header_far_beyond_200_chars_no_false_positive(tmp_path):
    # (c) Mirrors the real strong-leg shape: one governing "SHAPING" lead-in
    # line, then a numbered list whose items sit well past 200 chars from
    # that header (padded prose per item). The round-1 fixed radius produces
    # a false positive (untiered) on every item here; structural scope must
    # not, because the governing header is found via block adjacency, not
    # distance.
    lead_in = (
        "Unresolved **SHAPING** open questions (each blocks VERIFY until "
        "resolved or explicitly deferred with a reason — none carries a "
        "`deferred:` note yet):\n"
    )
    padding = "padding word " * 20  # ~260 chars, pushes the tag past 200
    items = "".join(
        f"{i}. **Blind spot {i}** — {padding}decides something important. "
        f"`evidence_needed: domain-convention`\n"
        for i in range(1, 4)
    )
    # Blank line between the lead-in and the list — matches the real
    # strong-leg fixture's actual layout (a separate governing-header block).
    root = _write_tag_fixture(tmp_path, proposal_extra=lead_in + "\n" + items)
    tier_problems = _check_domain_convention_tier_label(root)
    assert tier_problems == [], (
        f"governing SHAPING header must satisfy all 3 far items, got: {tier_problems}")
    deferred_problems = _check_shaping_without_deferred(root)
    assert len(deferred_problems) == 3, (
        f"all 3 undeferred SHAPING items must be flagged by check (3), "
        f"got: {deferred_problems}")


def test_deferrable_list_adjacency_no_cross_leak_either_direction(tmp_path):
    # (d) A SHAPING list, then an untiered paragraph, then a DEFERRABLE
    # paragraph — mirrors the real strong-leg layout (SHAPING list followed
    # by a DEFERRABLE paragraph). The middle, untiered tag sits between both
    # and must inherit neither label from either neighbor.
    body = (
        "Unresolved **SHAPING** open questions (blocks VERIFY unless "
        "deferred):\n"
        "\n"
        "1. **Blind spot** — short. `evidence_needed: domain-convention`\n"
        "\n"
        "Other flags (untiered, project-adjacent): something unresolved. "
        "evidence_needed: domain-convention\n"
        "\n"
        "DEFERRABLE open questions (recorded, non-blocking): rounding "
        "precision.\n"
    )
    root = _write_tag_fixture(tmp_path, proposal_extra=body)
    problems = _check_domain_convention_tier_label(root)
    # The untiered middle paragraph's tag is on proposal.md line 7
    # (lead-in=3, blank=4, item1=5, blank=6, untiered paragraph=7).
    assert len(problems) == 1, (
        f"exactly the untiered middle paragraph's tag must be flagged, "
        f"got: {problems}")
    assert "proposal.md:7" in problems[0], problems


def test_glued_lead_in_governs_its_list_without_blank_line(tmp_path):
    # (e) A colon-terminated SHAPING lead-in glued DIRECTLY to its list
    # (no blank line) lives inside the same block — the r2 quality review
    # proved this false-positived check (2). The intra-block lead-in must
    # govern: tier check clean, and check (3) still fires (SHAPING via
    # the glued header, no deferred: in the item's own scope).
    body = (
        "Unresolved **SHAPING** open questions (blocks VERIFY unless "
        "deferred):\n"
        "1. **Glued item** — short. `evidence_needed: domain-convention`\n"
    )
    root = _write_tag_fixture(tmp_path, proposal_extra=body)
    tier_problems = _check_domain_convention_tier_label(root)
    assert tier_problems == [], (
        f"a glued colon lead-in must govern its list — no tier "
        f"false-positive, got: {tier_problems}")
    deferred_problems = _check_shaping_without_deferred(root)
    assert len(deferred_problems) == 1, (
        f"the glued item is SHAPING via its lead-in and has no own "
        f"deferred: — check (3) must fire once, got: {deferred_problems}")
