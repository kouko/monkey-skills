"""Tests for scripts/lib/protect_pass.py — placeholder masking + restoration.

Covers Task C2 of translation-toolkit v0.1.0 plan (lines 1106-1228):
  1. test_protect_curly_braces
  2. test_protect_icu_plurals
  3. test_protect_inline_code
  4. test_protect_fenced_code
  5. test_protect_urls
  6. test_protect_count_must_match_after_translation  (M1 primitive)
  7. test_protect_html_tags
  8. test_protect_printf
  9. test_restore_preserves_token_order
  10. test_protect_idempotent_when_no_placeholders
  + edge-case tests for overlap resolution (URL inside HTML, ICU vs curly).
"""
from __future__ import annotations

import sys
from pathlib import Path

# tests/ -> scripts/ -> translation-toolkit/ -> repo root
SCRIPTS_DIR = Path(__file__).resolve().parent.parent

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from lib.protect_pass import protect, restore, verify_count  # noqa: E402


# -------------------- 1. curly braces --------------------

def test_protect_curly_braces():
    text = "Hello {name}, you have {count} messages"
    masked, token_map = protect(text)
    assert "{name}" not in masked
    assert "{count}" not in masked
    assert masked.count("⟦P:") == 2
    assert restore(masked, token_map) == text


def test_protect_curly_braces_doubled():
    """`{{var}}` (escaped curly in some i18n schemes) is also masked."""
    text = "Hello {{name}}, world"
    masked, token_map = protect(text)
    assert "{{name}}" not in masked
    assert masked.count("⟦P:") == 1
    assert restore(masked, token_map) == text


def test_protect_numeric_positional_args():
    """Java MessageFormat / Python str.format() / Android: {0}, {1} are protected."""
    text = "Hello {0}, you have {1} messages"
    masked, token_map = protect(text)
    assert "{0}" not in masked
    assert "{1}" not in masked
    assert masked.count("⟦P:") == 2
    assert restore(masked, token_map) == text


# -------------------- 2. ICU plurals --------------------

def test_protect_icu_plurals():
    text = "{count, plural, one {1 item} other {# items}}"
    masked, token_map = protect(text)
    # Whole ICU block → 1 token
    assert masked.count("⟦P:") == 1
    assert restore(masked, token_map) == text


def test_protect_icu_plural_outer_wins_over_inner_curly():
    """ICU plural pattern must consume the whole construct as ONE token —
    inner ``{1 item}`` / ``{# items}`` must NOT each become separate tokens."""
    text = "{count, plural, one {1 item} other {# items}}"
    masked, token_map = protect(text)
    assert len(token_map) == 1
    # The token's mapped original must be the full ICU expression.
    only_token, only_original = next(iter(token_map.items()))
    assert only_original == text
    assert masked == only_token


# -------------------- 3. inline code --------------------

def test_protect_inline_code():
    text = "Run `npm install` then `npm start`"
    masked, _ = protect(text)
    assert "npm" not in masked
    assert masked.count("⟦P:") == 2


# -------------------- 4. fenced code --------------------

def test_protect_fenced_code():
    text = "Header\n```python\ndef foo():\n    pass\n```\nEnd"
    masked, token_map = protect(text)
    assert "def foo" not in masked
    assert masked.count("⟦P:") == 1
    assert restore(masked, token_map) == text


def test_protect_fenced_wins_over_inline_code():
    """Inline-code regex must NOT eat backticks already owned by fenced block."""
    text = "Pre `inline` between\n```\ncode block with `backticks` inside\n```\nPost"
    masked, token_map = protect(text)
    # Expected: 1 inline + 1 fenced = 2 tokens (the backticks INSIDE the fence
    # are part of the fenced span, not separately tokenised).
    assert len(token_map) == 2
    assert restore(masked, token_map) == text


# -------------------- 5. URLs --------------------

def test_protect_urls():
    text = "Visit https://example.com/path?q=1"
    masked, token_map = protect(text)
    assert "https://" not in masked
    assert masked.count("⟦P:") == 1
    assert restore(masked, token_map) == text


def test_protect_urls_stops_at_markdown_paren():
    """URL pattern stops at `)` so markdown link `[text](url)` round-trips."""
    text = "See [docs](https://example.com/page) for details"
    masked, token_map = protect(text)
    # The URL token must NOT include the trailing `)`.
    restored = restore(masked, token_map)
    assert restored == text
    assert "https://example.com/page)" not in token_map.values()


def test_url_with_internal_paren_truncates_at_first_close_paren():
    """v0.1 known limitation: URLs containing balanced parens are truncated at first ).

    Tradeoff: URL pattern stops at ) to avoid swallowing markdown link closers
    `[text](url)`. Documented in scripts/canonical/protect-pass-spec.md.
    """
    text = "See https://en.wikipedia.org/wiki/Foo_(bar) for details"
    masked, token_map = protect(text)
    captured = list(token_map.values())[0]
    assert captured == "https://en.wikipedia.org/wiki/Foo_(bar"
    # Round-trip preserves the visible text including the dangling )
    assert restore(masked, token_map) == text


# -------------------- 6. M1 verification primitive --------------------

def test_protect_count_must_match_after_translation():
    """M1 primitive: detect dropped placeholder."""
    text = "Hello {user}, welcome"
    masked, token_map = protect(text)
    # Find the actual token (don't assume specific width)
    token = next(iter(token_map.keys()))
    bad = masked.replace(token, "")  # drop placeholder
    assert verify_count(bad, token_map) is False


def test_verify_count_passes_when_translation_preserves_tokens():
    text = "Hello {user}, you have {count} items"
    masked, token_map = protect(text)
    # Simulate translation that keeps all tokens intact (just rearrange prose).
    fake_translated = masked.replace("Hello", "こんにちは").replace("items", "件")
    assert verify_count(fake_translated, token_map) is True


def test_verify_count_detects_invented_tokens():
    """LLM hallucinates an extra ⟦P:NN⟧ → count mismatch."""
    text = "Hello {user}"
    masked, token_map = protect(text)
    # Append a token not in the source.
    bad = masked + " ⟦P:99⟧"
    assert verify_count(bad, token_map) is False


# -------------------- 7. HTML tags --------------------

def test_protect_html_tags():
    text = 'Click <a href="https://example.com">here</a>'
    masked, token_map = protect(text)
    # HTML pattern wins on overlap with URL inside attribute. Expected:
    # one ⟦P⟧ for <a href="…"> and one for </a> = 2 tokens.
    assert len(token_map) == 2
    # The URL must NOT be separately tokenised (it lives inside the <a> span).
    for original in token_map.values():
        assert "https://example.com" not in original or original.startswith("<a")
    assert restore(masked, token_map) == text


def test_protect_html_simple_tags():
    text = "Bold: <b>important</b> word"
    masked, token_map = protect(text)
    assert len(token_map) == 2  # <b> and </b>
    assert restore(masked, token_map) == text


# -------------------- 8. printf --------------------

def test_protect_printf():
    text = "Hello %s, you have %d messages and %1$s pending"
    masked, _ = protect(text)
    assert masked.count("⟦P:") == 3


def test_protect_printf_variants():
    """Cover %s %d %i %f %x %X %c %% (literal percent)."""
    text = "%s %d %i %f %o %x %X %c %%"
    masked, token_map = protect(text)
    # 9 specifiers, all consumed.
    assert len(token_map) == 9
    assert restore(masked, token_map) == text


# -------------------- 9. restore preserves order --------------------

def test_restore_preserves_token_order():
    text = "{a} and {b}"
    masked, token_map = protect(text)
    restored = restore(masked, token_map)
    assert restored == text


def test_restore_preserves_token_order_more():
    """Many placeholders, mixed types — restoration must reproduce input."""
    text = "User {name} ran `cmd` at https://x.io producing %d errors"
    masked, token_map = protect(text)
    assert restore(masked, token_map) == text


# -------------------- 10. idempotent on plain text --------------------

def test_protect_idempotent_when_no_placeholders():
    text = "Just plain text without any placeholders"
    masked, token_map = protect(text)
    assert masked == text
    assert token_map == {}


def test_protect_empty_string():
    masked, token_map = protect("")
    assert masked == ""
    assert token_map == {}


# -------------------- edge cases: overlap resolution --------------------

def test_url_inside_html_tag_html_wins():
    """When a URL appears inside an HTML attribute, the HTML span owns it."""
    text = 'Link: <a href="https://example.com/x">here</a>'
    masked, token_map = protect(text)
    # The first token must include the full opening tag with URL inside.
    first_original = list(token_map.values())[0]
    assert first_original.startswith("<a ")
    assert "https://example.com/x" in first_original
    # No separate URL token — exactly 2 tokens (open + close).
    assert len(token_map) == 2


def test_token_width_widens_past_99():
    """For ≥ 100 placeholders, NN auto-widens to 3 digits."""
    text = " ".join(f"{{v{i}}}" for i in range(150))
    masked, token_map = protect(text)
    assert len(token_map) == 150
    # Earliest token uses widened format ⟦P:001⟧.
    assert "⟦P:001⟧" in masked
    assert "⟦P:150⟧" in masked
    assert restore(masked, token_map) == text


def test_multiple_pattern_types_in_one_string():
    """Round-trip a realistic UI string mixing curly, printf, code, URL."""
    text = (
        "Hello {user}! You have %d unread items. "
        "Visit https://app.example.com or run `app sync` for details."
    )
    masked, token_map = protect(text)
    # Expect: {user} + %d + URL + `app sync` = 4 tokens.
    assert len(token_map) == 4
    assert restore(masked, token_map) == text
    assert verify_count(masked, token_map) is True


def test_email_protected():
    text = "Contact us at support@example.com please"
    masked, token_map = protect(text)
    assert "support@example.com" not in masked
    assert len(token_map) == 1
    assert restore(masked, token_map) == text


def test_restore_leaves_unknown_tokens_untouched():
    """LLM-invented ⟦P:NN⟧ that wasn't in source map → leave for caller to spot."""
    text = "Hello {user}"
    masked, token_map = protect(text)
    # Inject an unknown token after translation.
    polluted = masked + " plus rogue ⟦P:99⟧"
    restored = restore(polluted, token_map)
    # Original {user} is back, rogue token survives unmolested for the caller.
    assert "{user}" in restored
    assert "⟦P:99⟧" in restored
