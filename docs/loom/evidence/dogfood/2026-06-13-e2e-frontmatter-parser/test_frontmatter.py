"""Acceptance tests for parse_frontmatter — one test per spec.md scenario.

Spec: specs/frontmatter/spec.md (19 scenarios across 5 requirements).
Each test is named after its scenario so the scenario→test mapping is auditable.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(__file__))

from frontmatter import parse_frontmatter  # noqa: E402


# --- Requirement: Parse a valid frontmatter block ---

def test_single_key_value_pair():
    # Scenario: Single key-value pair
    meta, body = parse_frontmatter("---\ntitle: Hello\n---\nbody text")
    assert meta == {"title": "Hello"}
    assert body == "body text"


def test_multiple_key_value_pairs():
    # Scenario: Multiple key-value pairs
    meta, body = parse_frontmatter("---\ntitle: Hello\nauthor: kouko\n---\nbody")
    assert meta == {"title": "Hello", "author": "kouko"}
    assert body == "body"


# --- Requirement: Pass through text with no frontmatter ---

def test_plain_text_with_no_frontmatter():
    # Scenario: Plain text with no frontmatter
    text = "just a body, no frontmatter"
    meta, body = parse_frontmatter(text)
    assert meta == {}
    assert body == text


def test_empty_string_input():
    # Scenario: Empty string input
    meta, body = parse_frontmatter("")
    assert meta == {}
    assert body == ""


def test_delimiter_not_on_first_line_is_not_frontmatter():
    # Scenario: Delimiter not on the first line is not frontmatter
    text = "intro\n---\ntitle: x\n---\nbody"
    meta, body = parse_frontmatter(text)
    assert meta == {}
    assert body == text


# --- Requirement: Reject malformed frontmatter loudly ---

def test_unclosed_frontmatter_block():
    # Scenario: Unclosed frontmatter block
    with pytest.raises(ValueError):
        parse_frontmatter("---\ntitle: Hello\nbody with no closing delimiter")


def test_frontmatter_line_without_a_colon():
    # Scenario: Frontmatter line without a colon
    with pytest.raises(ValueError):
        parse_frontmatter("---\ntitle: Hello\nthisHasNoColon\n---\nbody")


def test_empty_key_after_stripping_is_malformed():
    # Scenario: Empty key after stripping is malformed (critic-found)
    with pytest.raises(ValueError):
        parse_frontmatter("---\n: value\n---\nbody")
    # AND likewise for a key that is only whitespace before the colon
    with pytest.raises(ValueError):
        parse_frontmatter("---\n   : value\n---\nbody")


# --- Requirement: Handle frontmatter value and key edge cases ---

def test_empty_frontmatter_block():
    # Scenario: Empty frontmatter block
    meta, body = parse_frontmatter("---\n---\nbody")
    assert meta == {}
    assert body == "body"


def test_value_containing_a_colon_splits_on_first_colon_only():
    # Scenario: Value containing a colon splits on the first colon only
    meta, body = parse_frontmatter("---\nurl: http://example.com\n---\nbody")
    assert meta == {"url": "http://example.com"}


def test_surrounding_whitespace_on_keys_and_values_is_stripped():
    # Scenario: Surrounding whitespace on keys and values is stripped
    meta, body = parse_frontmatter("---\n  title  :   Hello World   \n---\nbody")
    assert meta == {"title": "Hello World"}


def test_duplicate_keys_keep_the_last_value():
    # Scenario: Duplicate keys keep the last value
    meta, body = parse_frontmatter("---\ntag: a\ntag: b\n---\nbody")
    assert meta == {"tag": "b"}


def test_blank_lines_inside_the_block_are_skipped():
    # Scenario: Blank lines inside the block are skipped
    meta, body = parse_frontmatter("---\ntitle: Hello\n\nauthor: kouko\n---\nbody")
    assert meta == {"title": "Hello", "author": "kouko"}


def test_crlf_line_endings_are_handled_like_lf():
    # Scenario: CRLF line endings are handled like LF
    meta, body = parse_frontmatter("---\r\ntitle: Hello\r\n---\r\nbody")
    assert meta == {"title": "Hello"}
    assert body == "body"


def test_empty_value_yields_an_empty_string():
    # Scenario: Empty value yields an empty string
    meta, body = parse_frontmatter("---\ntitle:\n---\nbody")
    assert meta == {"title": ""}


# --- Requirement: Pin the function contract (type, value-typing, fence exactness) ---

def test_non_string_input_raises_typeerror():
    # Scenario: Non-string input raises TypeError (critic-found)
    with pytest.raises(TypeError):
        parse_frontmatter(None)


def test_values_are_never_coerced_to_non_string_types():
    # Scenario: Values are never coerced to non-string types (critic-found)
    meta, body = parse_frontmatter(
        "---\nport: 8080\nflag: true\ntags: [a, b]\n---\nbody"
    )
    assert meta == {"port": "8080", "flag": "true", "tags": "[a, b]"}


def test_opening_line_not_exactly_a_fence_is_not_frontmatter():
    # Scenario: An opening line that is not exactly a fence is not frontmatter (critic-found)
    text = "---extra\ntitle: x\n---\nbody"
    meta, body = parse_frontmatter(text)
    assert meta == {}
    assert body == text


def test_body_is_empty_when_text_ends_at_the_closing_fence():
    # Scenario: Body is empty when text ends at the closing fence (critic-found)
    meta, body = parse_frontmatter("---\ntitle: x\n---\n")
    assert meta == {"title": "x"}
    assert body == ""
