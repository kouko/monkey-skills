"""Compatibility and ownership checks for the Decision Map module boundaries."""

import ast
import importlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import map_store


DOCUMENT_SYMBOLS = (
    "SchemaViolation", "MapFrontmatter", "FogEntry", "DecisionLine",
    "DestinationAcceptance", "MapDocument", "TicketFrontmatter",
    "TicketDocument", "parse_frontmatter", "parse_map_document",
    "parse_ticket_document", "_parse_map_frontmatter", "_split_sections",
    "_parse_fog_entries", "_parse_decisions", "_parse_out_of_scope",
    "_parse_destination_acceptance", "_parse_retired_da_ids", "_null_or",
    "_parse_ticket_frontmatter", "_parse_ticket_section", "_parse_resolution",
)


def test_documents_existing_import_surface_preserves_identity():
    documents = importlib.import_module("map_documents")
    for name in DOCUMENT_SYMBOLS:
        assert getattr(map_store, name) is getattr(documents, name)
        assert getattr(documents, name).__module__ == "map_documents"
    with pytest.raises(map_store.SchemaViolation, match="opening"):
        documents.parse_frontmatter("missing fences")
    assert issubclass(map_store.AtomicExchangeUnsupported, documents.SchemaViolation)
    assert issubclass(map_store.AtomicExchangeBroken, documents.SchemaViolation)


def test_store_facade_has_no_document_definitions():
    tree = ast.parse(Path(map_store.__file__).read_text(encoding="utf-8"))
    definitions = {
        node.name for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.ClassDef))
    }
    assert definitions.isdisjoint(DOCUMENT_SYMBOLS)


def test_documents_ticket_parse_preserves_values_and_diagnostics():
    documents = importlib.import_module("map_documents")
    ticket = documents.parse_ticket_document(
        "---\ntype: delivery\nstatus: open\nblocked-by: first, second\n---\n"
        "## Resolution\nCompleted\n## Withdrawal\nReason\n",
        Path("tickets/example.md"),
    )
    assert isinstance(ticket, map_store.TicketDocument)
    assert ticket.frontmatter.blocked_by == ["first", "second"]
    assert ticket.frontmatter.claim is None
    assert ticket.resolution == "Completed"
    assert ticket.withdrawal == "Reason"
    with pytest.raises(map_store.SchemaViolation, match="duplicate frontmatter key"):
        documents.parse_frontmatter("---\ntype: delivery\ntype: research\n---")


def test_persistence_owner_preserves_exception_identity():
    persistence = importlib.import_module("map_persistence")
    for name in ("AtomicExchangeUnsupported", "AtomicExchangeBroken"):
        assert getattr(map_store, name) is getattr(persistence, name)
    assert persistence.atomic_write.__module__ == "map_persistence"
    tree = ast.parse(Path(map_store.__file__).read_text(encoding="utf-8"))
    definitions = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    assert definitions.isdisjoint({"_restore_cas_mismatch", "_commit_exchanged_candidate"})


@pytest.mark.parametrize("module", ["map_lifecycle", "map_transaction", "migrate_map_v3"])
def test_consumers_have_no_private_store_io_calls(module):
    tree = ast.parse((Path(__file__).parent / f"{module}.py").read_text())
    private_io = {"_atomic_write", "_exchange_paths", "_fsync_directory",
                  "_assert_contained", "_assert_no_symlink_components"}
    calls = {node.attr for node in ast.walk(tree)
             if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
             and node.value.id == "map_store"}
    assert calls.isdisjoint(private_io)


def test_persistence_atomic_write_and_cas_refusal(tmp_path):
    persistence = importlib.import_module("map_persistence")
    target = tmp_path / "target.md"
    persistence.atomic_write(target, "original\n")
    persistence.atomic_write(target, "updated\n", expected=b"original\n")
    assert target.read_bytes() == b"updated\n"
    with pytest.raises(map_store.SchemaViolation, match="changed"):
        persistence.atomic_write(target, "wrong\n", expected=b"stale\n")
    assert target.read_bytes() == b"updated\n"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["target.md"]


def test_store_public_write_preserves_legacy_fault_injection(tmp_path, monkeypatch):
    def fail(path, text, *, expected=None):
        raise OSError("injected legacy failure")

    monkeypatch.setattr(map_store, "_atomic_write", fail)
    with pytest.raises(OSError, match="injected legacy failure"):
        map_store.atomic_write(tmp_path / "target.md", "candidate")


def test_persistence_unsupported_exchange_preserves_original(tmp_path, monkeypatch):
    persistence = importlib.import_module("map_persistence")
    target = tmp_path / "target.md"
    target.write_bytes(b"original")

    def unsupported(first, second):
        raise persistence.AtomicExchangeUnsupported("injected unsupported exchange")

    monkeypatch.setattr(persistence, "exchange_paths", unsupported)
    with pytest.raises(map_store.AtomicExchangeUnsupported, match="injected"):
        persistence.atomic_write(target, "candidate", expected=b"original")
    assert target.read_bytes() == b"original"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["target.md"]


def test_validation_owner_and_facade_delegation(tmp_path, monkeypatch):
    validation = importlib.import_module("map_validation")
    tree = ast.parse(Path(validation.__file__).read_text())
    imports = {
        alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }
    assert "map_store" not in imports
    for name in ("_check_schema_version", "_check_map_structure",
                 "_check_destination_acceptance", "_check_blocked_by",
                 "_check_v3_ticket_closure_evidence", "_has_delivery_evidence"):
        assert getattr(map_store, name) is getattr(validation, name)
        assert getattr(validation, name).__module__ == "map_validation"
    calls = []

    def check(map_dir, doc, repo_root, *, read_ticket):
        calls.append((map_dir, doc, repo_root, read_ticket))
        raise map_store.SchemaViolation("injected validation diagnostic")

    (tmp_path / "MAP.md").write_text(
        "---\nmap-id: example\nschema_version: 3\nstate: charting\n---\n"
    )
    monkeypatch.setattr(validation, "validate_document", check)
    assert map_store.validate(tmp_path, tmp_path) == (
        2, "injected validation diagnostic"
    )
    assert len(calls) == 1
    assert calls[0][0] == calls[0][2] == tmp_path
    assert calls[0][3] is map_store.read_ticket


def test_validation_preserves_order_and_legacy_ticket_helpers(tmp_path):
    validation = importlib.import_module("map_validation")
    text = (
        "---\nmap-id: example\nschema_version: 3\nstate: charting\n---\n"
        "## Destination\n\n## Notes\n\n## Decisions-so-far\n\n"
        "## Not-yet-specified (fog)\n\n## Out-of-scope\n"
    )
    (tmp_path / "MAP.md").write_text(text)
    assert map_store.validate(tmp_path, tmp_path) == (
        0, f"{tmp_path} is a valid decision-map store"
    )
    assert map_store._check_tickets(tmp_path, "charting", 3) is None
    doc = map_store.read_map(tmp_path)
    assert map_store._check_monotonic_relations(tmp_path, doc) is None
    assert validation.validate_document(
        tmp_path, doc, tmp_path, read_ticket=map_store.read_ticket
    ) is None
    # Invalid version must win over the simultaneously missing sections.
    (tmp_path / "MAP.md").write_text(text.replace("version: 3", "version: 2").split("##")[0])
    assert map_store.validate(tmp_path, tmp_path) == (
        2, "schema_version 2 is retired; migrate MAP.md to schema_version 3 or later"
    )
