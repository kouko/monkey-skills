---
name: 2026-08-04-claim-copy-sweep-blind-to-py-module-docstrings
description: claim_copy_sweep.py scans only .md files, so contract-prose mirrors living in .py module docstrings are invisible to the sweep, and its leak report does not name that blind spot
status: COMMITTED-NEXT
origin: 0.50.0 fix arc close-out (2026-08-04) — third copy of the "never biased" ledger claim found only by manual grep
---

`scripts/claim_copy_sweep.py` (shipped in the #643 arc) sweeps `.md` files
for copies of a claim and honestly prints its known leaks — but its scope
is .md-only. Observed live during the 0.50.0 fix arc: the third copy of
the "so the sample of recorded findings is never biased" ledger claim
lived in the module docstring of `loom-code/scripts/loom_gate_markers.py`;
the sweep missed it and a recon agent's manual grep found it.

Contract-prose mirrors in `.py` module docstrings are NORMAL in this repo,
not an edge case (`gate-markers-spec.md` ↔ `loom_gate_markers.py`
docstring is the standing example), so the blind spot hits precisely the
class of copies the tool exists to enumerate.

Fix shipped this arc (branch fix-review-scope-remedy-and-claim-sweep-py,
plan Tasks 5-6): the sweep now walks `*.py` files and matches against
each file's MODULE docstring only (ast-based; parse failures land on the
unreadable list; reported line numbers are actual file lines), and both
the summary line ("swept N markdown files and M python module
docstrings") and the printed leak list name the extended scope. RED
coverage: `scripts/test_claim_copy_sweep.py`
(`test_py_module_docstring_copy_is_reported`,
`test_output_names_python_docstring_scope`,
`test_unparseable_py_lands_on_unreadable_list`).

Two corrections to the entry as originally filed, kept here honestly:
the filing-time verification recipe pinned the "never biased" exemplar,
but that docstring copy had already been retired by the 0.50.0 arc's own
claim rewrite (commit on main before this branch was cut), so the recipe
was unreproducible from day one. A live verification that survives:
`python3 scripts/claim_copy_sweep.py --claim "The resolver never returns a file list it cannot vouch for"`
lists `loom-code/scripts/review_scope.py` and
`loom-code/scripts/test_review_scope_docs_station.py` module-docstring
hits alongside the `.md` copies. Remaining blind spots (function/class
docstrings, non-docstring string literals, comments, commit messages)
stay out of scope by construction and are named in the tool's own leak
report.
