from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SKILL_PATH = REPO_ROOT / "loom-workflow/skills/independent-advisor/SKILL.md"
DETECTION_PATH = (
    REPO_ROOT
    / "loom-workflow/skills/independent-advisor/references/executor-detection.md"
)
DISPATCH_PATH = (
    REPO_ROOT
    / "loom-workflow/skills/independent-advisor/references/dispatch-protocol.md"
)
REPORT_PATH = (
    REPO_ROOT
    / "loom-workflow/skills/independent-advisor/references/report-contract.md"
)


def test_mode_routing_is_bound_to_a_citable_fact():
    # @req: REQ-1
    # @req: REQ-2
    # @req: REQ-12
    # @req: REQ-43
    assert SKILL_PATH.is_file(), f"missing entrypoint: {SKILL_PATH}"
    text = SKILL_PATH.read_text(encoding="utf-8")

    essence = {
        "frontmatter identity": [
            "name: independent-advisor",
            "version: 0.1.0",
            "different executor",
        ],
        "two modes": [
            "`explore`",
            "`audit`",
        ],
        "citable basis recorded verbatim": [
            "`mode_basis`",
            "verbatim",
            "Record the verbatim fact you looked up",
        ],
        "override preserves the basis": [
            "`mode_override`",
            "never erase the original `mode_basis`",
        ],
        "conflicting bases surfaced": [
            "record both facts",
            "surface the conflict at the user checkpoint",
        ],
        "no citable fact means ask": [
            "ask the user which mode to run",
            "Do not synthesise a basis",
        ],
        "no incumbent yet is legitimate": [
            "not yet existing",
            "distinct from an incomplete packet",
        ],
        "audit runs a single full-context leg and no proposer leg": [
            "a single leg with full context runs",
            "no `proposer` leg",
        ],
        "tier vocabulary": [
            "economy",
            "standard",
            "frontier",
        ],
    }
    for contract, needles in essence.items():
        missing = [needle for needle in needles if needle not in text]
        assert not missing, f"{contract} missing from entrypoint: {missing}"


def test_static_detection_excludes_and_never_claims_verification():
    # @req: REQ-3
    # @req: REQ-4
    # @req: REQ-20
    # @req: REQ-44
    # @req: REQ-45
    assert SKILL_PATH.is_file(), f"missing entrypoint: {SKILL_PATH}"
    assert DETECTION_PATH.is_file(), f"missing reference: {DETECTION_PATH}"
    text = SKILL_PATH.read_text(encoding="utf-8")
    detection = DETECTION_PATH.read_text(encoding="utf-8")

    entrypoint_essence = {
        "the reference is routed to": [
            "references/executor-detection.md",
        ],
        "a failing candidate is absent, not greyed out": [
            "never appears in the option list",
            "absent from the list, not shown as an unavailable option",
        ],
        "naming an excluded executor gets a refusal carrying the reason": [
            "refuse and state that exclusion reason",
        ],
        "four distinguishable exclusion reasons": [
            "`binary-missing`",
            "`binary-not-executable`",
            "`credential-missing`",
            "`credential-unusable`",
            "never collapse them into one",
        ],
        "static pass is not a verification claim": [
            "statically available, not yet verified",
            "permission to attempt a live probe",
            "never report a static pass downstream as a verified capability",
        ],
        "empty or same-family set stops rather than self-reviewing": [
            "stop the run",
            "a second opinion from the same executor is not a second opinion",
            "same-family",
        ],
        "exactly one candidate surfaces the distinct-executor conflict": [
            "exactly one candidate passes",
            "surface the conflict at the checkpoint",
        ],
    }
    for contract, needles in entrypoint_essence.items():
        missing = [needle for needle in needles if needle not in text]
        assert not missing, f"{contract} missing from entrypoint: {missing}"

    reference_essence = {
        "checkable invocations": [
            "sh -c 'command -v codex'",
            "sh -c 'command -v claude'",
        ],
        "an alias is not a path, so resolve in a non-interactive shell": [
            "does not read the user's interactive shell configuration",
            "whether the resolved value is an absolute path",
            "never on the pipeline's exit status",
        ],
        "an unresolvable command is binary-missing, not not-executable": [
            "No absolute path resolved → `binary-missing`",
            "Step 1 resolved no absolute path",
        ],
        "four reasons carry four different fixes": [
            "`binary-missing`",
            "`binary-not-executable`",
            "`credential-missing`",
            "`credential-unusable`",
        ],
        "record what the command printed": [
            "record what it printed",
        ],
        "the honest label": [
            "statically available, not yet verified",
        ],
    }
    for contract, needles in reference_essence.items():
        missing = [needle for needle in needles if needle not in detection]
        assert not missing, f"{contract} missing from reference: {missing}"


def test_three_roles_blind_packet_and_dual_order_judging():
    # @req: REQ-10
    # @req: REQ-11
    # @req: REQ-19
    # @req: REQ-23
    # @req: REQ-39
    assert SKILL_PATH.is_file(), f"missing entrypoint: {SKILL_PATH}"
    assert DISPATCH_PATH.is_file(), f"missing reference: {DISPATCH_PATH}"
    text = SKILL_PATH.read_text(encoding="utf-8")
    dispatch = DISPATCH_PATH.read_text(encoding="utf-8")

    entrypoint_essence = {
        "the reference is routed to": [
            "references/dispatch-protocol.md",
        ],
        "packet completeness is an obligation stated in the entrypoint": [
            "Hold the request until every required section is present",
            "rather than filling it in",
            "counts as a missing section",
            "ends before any spending path",
        ],
        "normalisation fidelity is an obligation stated in the entrypoint": [
            "compresses; it never rewrites",
            "may not change what",
            "disclosed in the report unsoftened",
        ],
        "three named roles, not three copies of one leg": [
            "`proposer`",
            "`normalizer`",
            "`blind judge`",
        ],
        "the proposer never sees the incumbent": [
            "never sees the incumbent solution",
            "that leg is void",
            "no prior challenger output",
        ],
        "anonymisation and counterbalancing are two separate controls": [
            "two separate controls",
            "either one alone is insufficient",
            "identity bias",
            "position bias",
        ],
        "counterbalancing is structural, not a prompt reminder": [
            "two runs in opposite presentation orders",
            "a prompt reminder is not a substitute for a second run",
        ],
        "four rejected shapes are named one by one": [
            "anonymised but judged in a single order",
            "judged in both orders with the origins visible",
            "only the forward run carries a verdict",
            "voids every verdict from that leg",
        ],
        "de-anonymisation waits for every verdict": [
            "only after every scheduled swap run has a verdict",
        ],
        "disagreement is reported, never averaged": [
            "recorded as inconclusive rather than averaged",
        ],
        "the reversed run shares no state": [
            "fresh executor process",
            "Reusing one session for both orders",
            "record that isolation",
        ],
        "early stop happens only after normalisation": [
            "substantially the same claim",
            "degrade to a single leg",
            "never before normalisation",
        ],
    }
    for contract, needles in entrypoint_essence.items():
        missing = [needle for needle in needles if needle not in text]
        assert not missing, f"{contract} missing from entrypoint: {missing}"

    reference_essence = {
        "the packet's four required sections": [
            "decision statement",
            "rejected options",
            "evidence paths",
            "incumbent proposal",
        ],
        "an incomplete packet is held, never filled in": [
            "hold the request",
            "name the missing section",
            "no empty placeholder",
        ],
        "an empty rejected-options section is written out, not left blank": [
            "explicitly marked empty",
        ],
        "an unreadable evidence path counts as missing": [
            "treated as missing",
        ],
        "an uncompletable packet ends the run before any spend": [
            "ends without entering any spending path",
            "the partial packet is retained",
        ],
        "one shared card template": [
            "core claim",
            "key assumptions",
            "failure modes",
            "cost",
        ],
        "normalisation compresses without rewriting": [
            "must not rewrite the substance",
            "comparable length before anonymisation",
        ],
        "a normaliser that authored the incumbent is disclosed": [
            "`normalized_by_is_incumbent_author`",
        ],
    }
    for contract, needles in reference_essence.items():
        missing = [needle for needle in needles if needle not in dispatch]
        assert not missing, f"{contract} missing from reference: {missing}"


def test_live_probe_verifies_both_tiers_and_frontier_fails_loud():
    # @req: REQ-5
    # @req: REQ-6
    # @req: REQ-7
    # @req: REQ-8
    # @req: REQ-21
    # @req: REQ-22
    assert SKILL_PATH.is_file(), f"missing entrypoint: {SKILL_PATH}"
    assert DETECTION_PATH.is_file(), f"missing reference: {DETECTION_PATH}"
    text = SKILL_PATH.read_text(encoding="utf-8")
    detection = DETECTION_PATH.read_text(encoding="utf-8")

    entrypoint_essence = {
        "the probe procedure is routed to the reference": [
            "references/executor-detection.md",
        ],
        "a probe runs only for an executor the user selected": [
            "only for an executor the user selected",
            "no probe runs at all",
        ],
        "the outcome comes from the probe's own exit status": [
            "own exit status",
            "never a pipeline",
            "is a probe failure, not a pass",
        ],
        "a pass needs both the model and the effort": [
            "`verified_model`",
            "`verified_effort`",
            "self-reports",
            "a missing effort value is a failure",
            "treated as unverified",
        ],
        "frontier fails loud and is never auto-downgraded": [
            "never auto-downgraded",
            "stop and surface the reason",
            "unavailable capability",
            "only on explicit user confirmation",
        ],
        "a non-frontier mismatch is still disclosed": [
            "return to the checkpoint",
            "is still disclosed",
        ],
        "the verified executor is the dispatched executor": [
            "the verified executor is the executor you dispatch",
            "alias",
            "judge and the proposer",
            "identical settings",
        ],
        "the probe grants no write access": [
            "no write access",
        ],
    }
    for contract, needles in entrypoint_essence.items():
        missing = [needle for needle in needles if needle not in text]
        assert not missing, f"{contract} missing from entrypoint: {missing}"

    reference_essence = {
        "a checkable probe invocation": [
            "codex exec",
            "--sandbox read-only",
            "--skip-git-repo-check",
            "model_reasoning_effort=",
        ],
        "stdin is closed or the run hangs": [
            "< /dev/null",
        ],
        "the header is the evidence": [
            "That header is the evidence",
            "whatever the executor prints back",
        ],
        "the pipeline trap is spelled out": [
            "tail",
        ],
    }
    for contract, needles in reference_essence.items():
        missing = [needle for needle in needles if needle not in detection]
        assert not missing, f"{contract} missing from reference: {missing}"


def test_report_leads_with_divergence_and_discloses_degradation():
    # @req: REQ-13
    # @req: REQ-14
    # @req: REQ-15
    # @req: REQ-16
    # @req: REQ-18
    # @req: REQ-24
    # @req: REQ-73
    assert SKILL_PATH.is_file(), f"missing entrypoint: {SKILL_PATH}"
    assert REPORT_PATH.is_file(), f"missing reference: {REPORT_PATH}"
    text = SKILL_PATH.read_text(encoding="utf-8")
    report = REPORT_PATH.read_text(encoding="utf-8")

    entrypoint_essence = {
        "the reference is routed to": [
            "references/report-contract.md",
        ],
        "divergence leads the report": [
            "divergence points are the body",
            "no divergence point was found",
        ],
        "the report is a read-only record": [
            "read-only record",
            "outside this consultation's scope",
        ],
        "six shape rejections, each distinguishable": [
            "distinguishable reason",
            "own claim of completion",
            "empty output",
            "a refusal",
            "a missing template field",
            "restates its own input",
            "fabrication suspect",
            "no reasoning trace",
        ],
        "degraded and failed legs are disclosed": [
            "`degraded_legs`",
            "failure attribution",
            "no leg produced usable output",
            "no verification evidence",
            "listed separately",
        ],
        "agreement is never weighted upward": [
            "`corroborated_by`",
            "not an input to `confidence`",
            "measures the sample, not the world",
        ],
        "the standing weakness note rides on every report": [
            "`known_weaknesses`",
            "shared by all reviewers",
        ],
        "no completeness wording, and the disclaimer gates delivery": [
            "never appear in the report",
            "in any language the report is written in",
            "`coverage_disclaimer`",
            "delivery is refused",
        ],
        "an early stop is visible in the report": [
            "`early_stopped`",
            "`leg_count`",
        ],
        "actual cost is truthful": [
            "`actual_cost`",
            "unknown with its reason",
        ],
        "every finding carries three things": [
            "a factual error or a judgement call",
            "the concrete change proposed",
        ],
        "external text stays marked as untrusted": [
            "externally authored and untrusted",
            "travels with the report",
            "downstream agent",
        ],
    }
    for contract, needles in entrypoint_essence.items():
        missing = [needle for needle in needles if needle not in text]
        assert not missing, f"{contract} missing from entrypoint: {missing}"

    reference_essence = {
        "the report skeleton is ordered divergence first": [
            "divergence_points",
            "known_weaknesses",
            "coverage_disclaimer",
            "degraded_legs",
        ],
        "the six rejection reasons are named keys": [
            "`empty-output`",
            "`refusal`",
            "`missing-field`",
            "`restates-input`",
            "`unbacked-claim`",
            "`no-reasoning-trace`",
        ],
        "worked wording for the standing note": [
            "measured the material",
        ],
    }
    for contract, needles in reference_essence.items():
        missing = [needle for needle in needles if needle not in report]
        assert not missing, f"{contract} missing from reference: {missing}"


def test_blindness_and_scan_claims_are_bounded_by_scope_boundary():
    # @req: REQ-69
    # @req: REQ-70
    # @req: REQ-71
    assert SKILL_PATH.is_file(), f"missing entrypoint: {SKILL_PATH}"
    text = SKILL_PATH.read_text(encoding="utf-8")

    essence = {
        "blindness is qualified by the readable range": [
            "`scope_boundary`",
            "unconditional blindness claim",
            "state the qualification",
        ],
        "a scan records what it checked, not a verdict": [
            "what the scan checked",
            "never a safety verdict",
        ],
        "the report states the packet-only limitation": [
            "covered the dispatch packet",
            "was not subject to it",
        ],
        "a pinned revision is the packet's origin": [
            "packet was extracted from",
            "not what was reviewed",
        ],
    }
    for contract, needles in essence.items():
        missing = [needle for needle in needles if needle not in text]
        assert not missing, f"{contract} missing from entrypoint: {missing}"


def test_skill_body_stays_under_the_repo_word_cap():
    # mirrors WORD_HARD_CAP in scripts/check-skill-structure.py (CHK-SKL-010)
    assert SKILL_PATH.is_file(), f"missing entrypoint: {SKILL_PATH}"
    word_hard_cap = 4500
    word_count = len(SKILL_PATH.read_text(encoding="utf-8").split())
    assert word_count <= word_hard_cap, (
        f"SKILL.md is {word_count} words, over the {word_hard_cap}-word hard cap"
    )


def test_single_checkpoint_carries_three_elements_and_egress_disclosure():
    # @req: REQ-9
    # @req: REQ-27
    # @req: REQ-47
    # @req: REQ-68
    # @req: REQ-69
    # @req: REQ-72
    # @req: REQ-74
    assert SKILL_PATH.is_file(), f"missing entrypoint: {SKILL_PATH}"
    text = SKILL_PATH.read_text(encoding="utf-8")

    essence = {
        "exactly one checkpoint, before any spend": [
            "Exactly one checkpoint exists",
            "any money is spent",
        ],
        "one ask carries leg count, executors, cost and egress": [
            "the leg count",
            "which executor runs which leg",
            "the estimated cost",
            "the egress disclosure",
        ],
        "splitting, dispatching unapproved and partial answers are violations": [
            "**splitting** these into separate questions",
            "without a recorded user confirmation",
            "partial answer as approval",
            "never fill it with a default",
        ],
        "a changed executor set voids the approval and recomputes": [
            "the prior approval is void",
            "Never carry a previous static result or cost figure",
        ],
        "unknown cost is never written as zero, and zero never as unknown": [
            "unknown, with the reason",
            "never as zero and never omitted",
            "genuinely zero",
        ],
        "egress names the vendor and the categories": [
            "the vendor that receives material",
            "the file paths the executor will be authorised to read",
            "cost only",
        ],
        "the readable range is larger than the inspected packet": [
            "`scope_boundary` is the larger of the two",
            "enumerate what",
        ],
        "a passing scan is not a safety claim": [
            "the packet was checked and nothing matched",
            "carries that meaning",
        ],
        "loading project configuration runs third-party code": [
            "instructions, hooks, skills and MCP servers",
            "third-party code in the user's repository",
            "state that it cannot be enumerated in advance",
        ],
        "a verbatim audit record declares itself and its location": [
            "material verbatim rather than references and summaries",
            "state its location at this checkpoint",
            "same restrictions as the dispatch packet",
        ],
        "cancellation after a transfer is stated honestly": [
            "cannot be recalled",
        ],
    }
    for contract, needles in essence.items():
        missing = [needle for needle in needles if needle not in text]
        assert not missing, f"{contract} missing from entrypoint: {missing}"
