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

Next step: teach the sweep to also scan `.py` module docstrings —
top-of-file string only, NOT the full file (a full-file .py scan would
drown in code identifiers) — and print the extended scope in its own leak
report so the report stays honest about what it can and cannot see. The
tool lives at repo top-level `scripts/` (no plugin bump — verified
precedent: the #638 arc shipped it top-level; re-verify against
`check_version_bump.py` behavior anyway). Its tests live in `scripts/`
too; check existing `scripts/test_claim_copy_sweep*.py` naming before
adding. Verification that the defect is still live:
`python3 scripts/claim_copy_sweep.py --claim "so the sample of recorded findings is never biased" | grep -c loom_gate_markers.py`
returns 0 while a raw grep finds the docstring copy.
