---
name: 2026-07-20-loom-gate-hardening-deferred-ci-side-arc
description: loom gate hardening — deferred CI-side arc
status: OPEN
origin: loom gate-hardening mechanical arc (branch `loom-gate-hardening-mechanical`, 2026-07-20/21); audit `docs/loom/audits/2026-07-20-loom-mechanism-weakness-audit.md` §7 + the branch brief §Out of Scope. The mechanical fixes (verified→`--run`, push-guard wrappers, batch precursor guard, version-bump `scripts/`) shipped this branch; the items below were deferred because they are NOT locally solvable as mechanical fixes.
start: next substantive touch of `loom-code/scripts/loom_gate_markers.py`, the pipeline seg2 validator (`loom-pipeline/scripts/driver_40_seg2.js`), or a decision to add server-side gate re-checks.
---

- Start: next substantive touch of `loom-code/scripts/loom_gate_markers.py`,
  the pipeline seg2 validator (`loom-pipeline/scripts/driver_40_seg2.js`), or a
  decision to add server-side gate re-checks.
- Origin: loom gate-hardening mechanical arc (branch
  `loom-gate-hardening-mechanical`, 2026-07-20/21); audit
  `docs/loom/audits/2026-07-20-loom-mechanism-weakness-audit.md` §7 + the
  branch brief §Out of Scope. The mechanical fixes (verified→`--run`, push-guard
  wrappers, batch precursor guard, version-bump `scripts/`) shipped this branch;
  the items below were deferred because they are NOT locally solvable as
  mechanical fixes.
- What: (a) **waiver + review-pass "cannot self-mint"** — local cryptographic
  unforgeability is impossible (the gated agent shares the shell; Axis-4 research
  in the audit §7). Real fix = CI-side re-check + a deliberateness bar (deny-list
  / PreToolUse), i.e. a separate trust domain. This SUPERSEDES audit §7 rec#2's
  "waiver needs an un-self-suppliable token" — that token does not exist locally.
  (b) **pipeline seg2 validator self-report**: the Workflow-sandboxed
  `driver_40_seg2.js` cannot exec a subprocess, so "the gate runs the validator
  itself" needs an architecture change (move the validator call to a
  sandbox-external step); `batch_queue.py` already does it right because it is
  sandbox-external Python. (c) **#8 DESIGN.md path resolution** —
  `mint_critic_verdict.py` resolves `--files` change-folder-relative but
  DESIGN.md is product-level → exit 4 under canonical layout. (d) **#6 Codex
  git-guard-shim fail-open** on payload-shape drift — needs Codex's real payload
  spec. (e) flat-folder CI omits loom-discovery + loom-pipeline; mint lockstep
  test lives only in loom-interface-design.
