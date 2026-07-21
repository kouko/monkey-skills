---
name: departure-disguised-as-conformance-cites-wrong-precedent
description: A convention-departure justification that cites an "established pattern" the code actually diverges from is a departure DISGUISED as conformance — worse than an honest one; verify the cited precedent actually covers your case, and have review check the citation, not just the code
type: gotcha
origin: feat-narrative-kpi-evidence-coverage T3 (8-K prose KPI producer, investing-toolkit 2.27.0, 2026-07-20)
---

An implementer reached the data-markets `exhibit_prose` locator from an
analysis-kpi producer by an **in-process cross-skill import** (a
`sys.path.insert(0, <data-markets/scripts>)` shim), and justified it with a
comment: *"mirrors the same-dir shim kpi_8k_candidates / kpi_memo_feed use for
their siblings."* But that cited shim imports **same-skill** siblings
(`kpi_store`) — it does **not** cross the analysis→data-markets boundary. The
actual precedent for THAT boundary is the opposite: the sibling
`kpi_8k_candidates.run_exhibit_tables` crosses it by **subprocess**
(`uv run exhibit_tables.py`), documented as a layer boundary crossed by process
(and repo memory "analysis-* reach data-markets by process"). So the comment
told a future reader "this conforms to an established shim" while the code in
fact departed from the established pattern for that specific crossing.

The code-quality reviewer caught it by **checking the cited precedent against
what it actually does** — not by re-judging the import in isolation. The fix
reverted to the subprocess crossing (adding an `exhibit_prose --locate` CLI +
`run_exhibit_prose` mirroring `run_exhibit_tables`, with a pure
`build_candidates` seam), and rewrote the comment to state honestly it is the
subprocess boundary crossing.

**Why:** a departure disguised as conformance is worse than an honest departure
— it launders a real design choice past a reader who trusts the comment, and it
skips the scrutiny the choice deserves (here: the in-process import mutated
`sys.path[0]` globally, a stdlib-shadow risk this repo already burned on — see
[[python-path-parent-resolve-gotcha]] / the select.py-shadows-stdlib scar — and
bypassed the callee's PEP-723 declared env). The false "we conform" framing is
the load-bearing defect, independent of whether the departure itself is
defensible.

**How to apply:** (1) when you justify a convention departure by citing an
"existing pattern", VERIFY the cited instance actually covers your case (same
boundary, same direction) — a same-skill shim is not a cross-skill precedent;
(2) if the case genuinely IS a departure, say so honestly and give the real
reason, don't dress it as conformance; (3) in review, treat a
"mirrors/conforms-to X" comment as a claim to CHECK against X, not decoration —
the reviewer who opened the cited file is the one who caught this. Relates to
[[cross-module-field-contracts-execute-probes]] (verify the claim against the
artifact, don't take the comment's word) and the boundary convention itself:
analysis-* reach data-markets by SUBPROCESS, never in-process import.
