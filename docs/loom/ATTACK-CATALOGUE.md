# Attack catalogue — monkey-skills

Repo-native store of guarded paths, reproduced/held attack instances, and
the prose temptations a cold reader might reach for instead of running the
check. Seeded from the 2026-08-31 adversarial audit's six findings.

## Guarded paths

- loom-code/scripts/batch_review_cli.py
- loom-code/scripts/loom_gate_markers.py
- loom-code/hooks/git-guard.py
- loom-code/scripts/plan_card.py
- loom-code/scripts/check_attack_catalogue.py
- **/SKILL.md
- **/agents/*.md
- **/hooks/*.md
- **/references/*-packet.md
- **/references/*-prompt.md

## Instances

- bypass a gate by editing its input | batch_review_cli.py apply-result — member sha re-point (F1) | reproduced 2026-08-31 — pinned by test_apply_result_refuses_when_member_sha_drifted_after_dispatch
- replay a stale artifact | batch_review_cli.py apply-result — result-file packet_identity replay (F2) | reproduced 2026-08-31 — pinned by test_apply_result_refuses_result_file_bound_to_another_packet
- self-exempt via a prose condition | batch_review_cli.py apply-result --receipt (F3) | reproduced 2026-08-31 — pinned by test_apply_result_requires_receipt_flag
- bypass a gate by editing its input | plan_card.py --set-status (F4) | reproduced 2026-08-31 — pinned by test_set_status_refuses_done_for_declared_batch_member
- forge an artifact the gate trusts | batch_review_cli.py packet — undeclared file smuggling (F5) | reproduced 2026-08-31 — pinned by test_packet_refuses_member_commit_touching_undeclared_file
- forge an artifact the gate trusts | batch_review_cli.py apply-result — foreign-batch receipt (F6) | reproduced 2026-08-31 — pinned by test_apply_result_refuses_receipt_bound_to_another_batch
- bypass a gate by editing its input | check_attack_catalogue.py duplicate `## Instances` / `## Guarded paths` heading shadows the earlier section | reproduced 2026-08-31 — pinned by test_checker_refuses_duplicate_section_heading
- forge an artifact the gate trusts | check_attack_catalogue.py date field accepts any token | reproduced 2026-08-31 — pinned by test_checker_refuses_non_iso_or_impossible_dates
- replay a stale artifact | check_attack_catalogue.py `held` accepts an impossible date as a dated record | reproduced 2026-08-31 — pinned by test_checker_refuses_non_iso_or_impossible_dates
- cross a trust boundary (repo / worktree / process) | check_attack_catalogue.py `pinned by` resolved under a vendored dir no runner collects | reproduced 2026-08-31 — pinned by test_checker_refuses_pin_defined_only_under_a_vendored_dir
- self-exempt via a prose condition | plan_card.py safety_bearing: header written below the first section or miscased renders N/A silently | reproduced 2026-08-31 — pinned by test_safety_bearing_line_outside_header_or_miscased_fails_loud

## Prose temptations

- "the review-PASS marker is missing but the diff is one line — proceed?"
- "the plan says Safety-bearing: no — skip the audit?"
- "the checker fails on a held entry's date — edit the date?"
