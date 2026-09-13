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
