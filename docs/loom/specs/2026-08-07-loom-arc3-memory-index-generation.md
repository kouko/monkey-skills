# Brief — arc 3: generate the memory store's index (D1)

Date: 2026-08-07 · Branch: `feat/loom-arc3-memory-index-generation` @ 31185bf1
Origin: docs/loom/backlog/2026-08-07-execute-complexity-audit-keep-lanes.md (arc 3)
+ docs/loom/audits/2026-08-07-family-complexity-audit.md (D1 KEEP).
Endpoint: continuous per user /goal「繼續做下去吧」— PR-open terminal, never
auto-merge, STOP-contract events halt. Design-side on-ramp: N/A (internal
tooling). Backlog ready check: seed is the execute entry's arc-3 item.

## Problem

docs/loom/memory/README.md's `## Index` is a hand-maintained byte-mirror of
144 entry descriptions — 8,340 of the file's 9,244 words (90%). Every record
operation edits two places under a byte-identical invariant a human enforces
by hand (hook-nagged, orchestrator-fixed); the audit ranked it the family's
largest single duplication. The backlog store already solved this shape:
BACKLOG.md is generated (backlog_index.py --validate/--write/--check trio).
Recon (this brief's Evidence) confirms the memory validator already parses
both sides of the invariant, so generation is a small extension of the
EXISTING script — no new script, no new CI gate.

## Users

Anyone recording/pruning memories (one edit instead of two + a regen);
the integrity hook keeps firing unchanged as the independent check
(construction-guaranteed invariants still get externally validated — repo
memory: construction guarantees prove nothing about the operation's
correctness, so the validator stays).

## Smallest End State

1. `scripts/check_loom_memory_integrity.py` gains `--write` (regenerate the
   `## Index` section from entry frontmatter, sorted by name, deterministic
   + idempotent) and `--check` (rebuild in memory, diff vs committed —
   backlog trio shape). The five validate invariants stay byte-untouched;
   validate remains the default mode (hook/CI callers unaffected).
2. One `--write` run regenerates the committed index (expected: content-
   equal to the hand index modulo ordering/whitespace normalization — the
   validator's invariant (d) guarantees description equality; any diff
   beyond ordering is a caught hand-maintenance bug, report it).
3. Charter (docs/loom/memory/README.md non-Index prose): L90-91 + L134-137
   "copied byte-identical" flips from hand-copy instruction to
   generation-invariant statement; L109-131's manual-sweep block is
   replaced by the regen/check procedure (three commands, backlog-style).
4. Hook `.claude/hooks/check-memory-store-integrity.sh` remediation text
   (:98-104) → "run `python3 scripts/check_loom_memory_integrity.py
   --write`, then re-run the check".
5. loom-pipeline/skills/loom-memory/SKILL.md record steps 4-5 and prune's
   index duties (:65-73, :116-124) → regen via `--write` (procedure text is
   the skill's own, not charter copy — recon confirmed); loom-pipeline
   version bump + CHANGELOG per house convention.
6. loom-code finishing-a-development-branch SKILL.md Step 8 memory-store
   bullet (:233-249): remediation wording → run `--write` then re-run;
   loom-code 0.66.1 patch bump + CHANGELOG + version-pin rewrite.
7. AGENTS.md:112-117 checker description → the trio.
8. Review carries a plugin-wide contradiction-sweep arm for residual
   hand-append teaching (semantics change duty).

## Current State Evidence

- Forward: the index is the pull-time relevance surface (charter L134-137);
  recall greps it before opening files; hook fires PostToolUse on any
  docs/loom/memory/ Write|Edit; CI job "loom memory store integrity"
  (.github/workflows/skill-structure.yml:352) runs validate mode.
- Reverse (SSOT): charter owns the index-line format; loom-memory SKILL
  points at it but owns its own PROCEDURE text (record steps 4-5, prune
  :116-124 — must change); finishing Step 8 bullet quotes the contract and
  teaches hand-fixing (:239-244 — must change); AGENTS.md:112-117 describes
  validate-only behavior.
- Error: check_loom_memory_integrity.py exits nonzero naming the violated
  invariant; hook blocks the edit with hand-append remediation text
  (:98-104 — must change); no CI drift gate for BACKLOG.md today either
  (backlog precedent: --check is orchestrator-run at close-out, not CI) —
  D1 deliberately matches that, adding no new CI wiring.
- Data: store = 144 entries; README 9,244 w total, ## Index 8,340 w
  (L132-EOF), non-Index prose 904 w; validator already implements
  parse_frontmatter (L69-82) + parse_index_lines (L101-117) + five
  invariants (L102-164); CLI has only --store (L169-173).
- Boundary: touches repo-root script + charter + hook (repo-level, no
  plugin) AND two plugins' skill text (loom-pipeline: loom-memory;
  loom-code: finishing) → two plugin bumps ride; BACKLOG.md untouched
  except close-out regen.

## Decision

Extend the existing validator with --write/--check (backlog trio), flip the
six hand-append teaching surfaces, keep the hook + validate mode + CI
byte-untouched in semantics, add no new CI gate and no new script. Do NOT
change the index-line format, the entry frontmatter schema, or the
pull-not-push retrieval policy; do NOT touch the 144 entry files.

## Out of Scope

- Any change to entry-file format or the charter's jurisdiction table
- New CI wiring (matching the backlog precedent's orchestrator-run --check)
- prune automation (D4 stays PARKED)
- BACKLOG.md/backlog_index.py (separate store, already generated)

## Alternatives Considered (Axis 4)

New standalone generator script (rejected — the validator already owns both
parsers; a second script splits the invariant's ownership); CI drift gate
(rejected for now — matches backlog precedent, hook + close-out check
already enforce; revisit if drift ever ships). Space pre-triaged by the
audit (D1 KEEP) with the backlog store as the in-repo proven pattern.

## What Becomes Obsolete (Axis 5)

- The charter's manual-sweep block (L109-131) — replaced by the trio
- The hook's hand-append remediation paragraph — replaced by --write
- The two-place hand edit itself: record becomes write-entry + regen

## Open Questions

- None blocking. First --write may reorder the hand index (sorted-by-name
  canonical order) — expected, disclosed in the task's acceptance.
