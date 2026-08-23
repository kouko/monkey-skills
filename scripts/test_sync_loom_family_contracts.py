"""Tests for sibling-neutral loom family policy distribution."""

import re

import sync_loom_family_contracts as sync

POLICY_NAMES = ("family-reception.md", "family-relay.md", "plain-relay.md")
PLUGIN_INTERNAL_PATH = re.compile(
    rb"(?:loom-code|loom-design)/(?:hooks|skills|scripts)/"
)


def _managed_header(source_rel: str) -> bytes:
    return (
        "<!--\n"
        "FUNCTIONAL COPY — DO NOT EDIT IN PLACE\n"
        f"SSOT: {source_rel}\n"
        "Sync via: scripts/sync_loom_family_contracts.py\n"
        "-->\n\n"
    ).encode("utf-8")


def test_real_functional_copies_match_sibling_neutral_family_policy_ssot():
    for name in POLICY_NAMES:
        source_rel = f"scripts/canonical/loom-family/{name}"
        destination_rels = (
            f"loom-code/hooks/{name}",
            f"loom-design/skills/using-loom-design/references/{name}",
        )
        source = sync.REPO_ROOT / source_rel

        assert source.is_file(), f"missing neutral SSOT: {source_rel}"
        expected = _managed_header(source_rel) + source.read_bytes()
        for destination_rel in destination_rels:
            destination = sync.REPO_ROOT / destination_rel
            assert destination.is_file(), f"missing copy: {destination_rel}"
            assert destination.read_bytes() == expected


def test_identifier_grammar_has_one_neutral_source_and_two_packaged_copies():
    source_rel = "scripts/canonical/loom-artifacts/requirement-identifiers.md"
    destination_rels = (
        "loom-design/skills/spec-expansion/references/requirement-identifiers.md",
        "loom-code/skills/writing-plans/references/requirement-identifiers.md",
    )
    source = sync.REPO_ROOT / source_rel

    assert sync.ROUTE[source_rel] == destination_rels
    assert source.is_file(), f"missing neutral SSOT: {source_rel}"
    expected = _managed_header(source_rel) + source.read_bytes()
    for destination_rel in destination_rels:
        destination = sync.REPO_ROOT / destination_rel
        assert destination.is_file(), f"missing copy: {destination_rel}"
        assert destination.read_bytes() == expected


def test_canonical_and_generated_policy_has_no_plugin_internal_paths():
    policy_paths = []
    for source_rel, destination_rels in sync.ROUTE.items():
        policy_paths.append(sync.REPO_ROOT / source_rel)
        policy_paths.extend(sync.REPO_ROOT / rel for rel in destination_rels)

    offenders = [
        str(path.relative_to(sync.REPO_ROOT))
        for path in policy_paths
        if PLUGIN_INTERNAL_PATH.search(path.read_bytes())
    ]
    assert offenders == []


def test_neutral_family_policy_has_no_mandatory_sibling_skill():
    reception = (
        sync.REPO_ROOT / "scripts/canonical/loom-family/family-reception.md"
    ).read_text(encoding="utf-8")
    relay = (
        sync.REPO_ROOT / "scripts/canonical/loom-family/family-relay.md"
    ).read_text(encoding="utf-8")

    assert "You have the loom family of plugins available" not in reception
    assert "Sibling plugins are optional" in reception
    assert "loom-code:requesting-code-review" not in relay
    assert "If a referenced sibling skill is unavailable" in relay
    assert "state anchor" in relay
    assert "ships in the loom-code plugin" not in relay
    assert "If `plan_card.py` is unavailable" in relay

    assert "and its public skill is available" in reception
    assert "owning plugin's path continues" in reception
    assert "If `dev-workflow:brief-before-asking` is available" in reception
    for heading in (
        "Mental Model",
        "Situation",
        "Why this is a fork",
        "Options",
        "My take",
        "Open ends",
    ):
        assert heading in reception
    assert "handoff-brief-format.md" not in reception
    assert "When the public `loom-code:writing-plans` skill is available" in reception


def test_check_detects_byte_drift_without_rewriting(tmp_path, monkeypatch):
    source_rel = "scripts/canonical/loom-family/family-relay.md"
    destination_rels = (
        "loom-code/hooks/family-relay.md",
        "loom-design/references/family-relay.md",
    )
    source = tmp_path / source_rel
    source.parent.mkdir(parents=True)
    source.write_bytes(b"canonical\n")
    for destination_rel in destination_rels:
        destination = tmp_path / destination_rel
        destination.parent.mkdir(parents=True)
        destination.write_bytes(b"drifted\n")
    monkeypatch.setattr(sync, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(sync, "ROUTE", {source_rel: destination_rels})

    before = {rel: (tmp_path / rel).read_bytes() for rel in destination_rels}
    assert sync.check() == 1
    assert {rel: (tmp_path / rel).read_bytes() for rel in destination_rels} == before


def test_check_rejects_plugin_internal_path_in_canonical_policy(tmp_path, monkeypatch):
    source_rel = "scripts/canonical/loom-family/family-relay.md"
    destination_rels = ("loom-code/hooks/family-relay.md",)
    source = tmp_path / source_rel
    source.parent.mkdir(parents=True)
    source.write_bytes(b"Read loom-code/hooks/family-relay.md\n")
    destination = tmp_path / destination_rels[0]
    destination.parent.mkdir(parents=True)
    destination.write_bytes(_managed_header(source_rel) + source.read_bytes())
    monkeypatch.setattr(sync, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(sync, "ROUTE", {source_rel: destination_rels})

    before = destination.read_bytes()
    assert sync.check() == 1
    assert destination.read_bytes() == before


def test_sync_writes_header_then_canonical_bytes_to_both_plugins(tmp_path, monkeypatch):
    source_rel = "scripts/canonical/loom-family/plain-relay.md"
    destination_rels = (
        "loom-code/hooks/plain-relay.md",
        "loom-design/references/plain-relay.md",
    )
    source = tmp_path / source_rel
    source.parent.mkdir(parents=True)
    source.write_bytes(b"# Policy\n\xff\n")
    monkeypatch.setattr(sync, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(sync, "ROUTE", {source_rel: destination_rels})

    assert sync.sync() == 2
    expected = _managed_header(source_rel) + source.read_bytes()
    assert all((tmp_path / rel).read_bytes() == expected for rel in destination_rels)
