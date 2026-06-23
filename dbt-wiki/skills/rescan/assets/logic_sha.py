#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["sqlglot>=25.0"]
# ///
"""Compute a comment-stripped, normalized SQL fingerprint.

dbt-wiki's rescan uses this to tell cosmetic SQL changes (comment- or
whitespace-only edits) apart from material ones (logic changes). Two SQL
strings that differ only in comments or formatting yield the same sha;
any change to the logic yields a different sha.

Primary path uses sqlglot to parse + re-emit the SQL with comments
dropped and the AST normalized, then md5s the canonical form. If sqlglot
cannot parse the input (any error), it falls back to a regex comment-strip
+ whitespace collapse so the function never raises — the fingerprint is
still stable for a given input, just coarser.
"""
import hashlib
import re

_LINE_COMMENT = re.compile(r"--[^\n]*")
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_JINJA_COMMENT = re.compile(r"\{#.*?#\}", re.DOTALL)
_WHITESPACE = re.compile(r"\s+")


def _md5(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def _regex_fingerprint(sql):
    """Comment-strip + whitespace-collapse + lowercase, then md5."""
    text = _JINJA_COMMENT.sub(" ", sql)
    text = _BLOCK_COMMENT.sub(" ", text)
    text = _LINE_COMMENT.sub("", text)
    text = _WHITESPACE.sub(" ", text).strip().lower()
    return {"sha": _md5(text), "method": "regex"}


def compute_logic_sha(sql, dialect="redshift"):
    """Return {"sha", "method"} — a normalized, comment-free SQL fingerprint.

    sql: the SQL string (None / empty are treated as "").
    dialect: sqlglot read dialect for the primary parse path.

    method is "sqlglot" on a clean parse, "regex" on the fallback path
    (including empty / None input, which short-circuits to the regex path).
    """
    if not sql:
        return _regex_fingerprint("")
    try:
        import sqlglot

        canonical = sqlglot.parse_one(sql, read=dialect).sql(
            comments=False, normalize=True
        )
        return {"sha": _md5(canonical), "method": "sqlglot"}
    except Exception:
        return _regex_fingerprint(sql)
