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
