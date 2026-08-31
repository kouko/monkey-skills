---
name: 2026-08-31-loom-gate-markers-split
description: loom_gate_markers.py mixes git/marker I/O, verdict parsing, and CLI in one 1389-line file with no package boundary between the regions
status: open
origin: 2026-08-31 — three-plugin script audit (Phase 3 item 3a), deferred from docs/loom/specs/2026-08-31-decision-map-script-cleanup.md §Out of Scope
start: event — the next time a change must touch two of the three regions of the file in one task, or a reviewer flags the file's size
---

`loom-code/scripts/loom_gate_markers.py` is 1389 lines and mixes three
responsibilities with no module boundary between them:

- **git/marker I/O** (`_git`, `_show_committed_file`, `default_branch_ref`,
  `compute_patch_id`, `resolve_marker_dir`, `_write_marker`, `_now_iso`,
  and the record-only-file helpers `_is_contract_class_md`,
  `_record_only_offending_files`, `_record_only_changed_files`) — talks to
  the repo and the marker directory on disk.
- **verdict parsing** (`validate_verdict_text`, `_simplification_ledger_problems`,
  `_fence_toggle`, `_terminal_reviewed_sha`, `_origin_required`,
  `_parse_origin`, `_origin_grammar_problem`, `_origin_path_quote`,
  `_finding_quote_status`, `_normalize_for_quote_match`,
  `_quote_match_tier`, the `_FindingInfo` class, `_iter_findings`,
  `_finding_problems`, `_quote_verification_statuses`,
  `_print_normalised_quote_advisory`, `validate_suite_line`) — pure text
  analysis over a reviewer's verdict prose, no I/O.
- **CLI** (`run_verification`, `_cmd_review_pass`, `_cmd_verified`,
  `_cmd_mint`, `_cmd_waiver`, `_cmd_validate`, `main`) — argparse wiring
  and subcommand dispatch, calling into the two regions above.

The candidate cut is three modules — `gate_markers_git.py` (I/O),
`gate_markers_verdict.py` (parsing), and the existing
`loom_gate_markers.py` trimmed to a thin CLI top that imports both.

Why it matters: a change to one region currently forces reading the
whole 1389-line file to find the boundary, and per-task review scope
cannot be narrowed below "the whole file" even when the actual change
is confined to, say, only the quote-matching logic.

Risk: this file is the hot path for every push gate (`review-pass`,
`verified`, `mint`, `waiver`, `validate` all route through it), and the
scripts under `loom-code/scripts/` use sibling imports rather than a
package — splitting it means re-threading those sibling imports
correctly across the new module boundary, not just moving functions.
