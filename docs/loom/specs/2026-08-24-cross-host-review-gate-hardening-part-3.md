# Brief: cross-host review-gate hardening — part 3

Date: 2026-08-24
Origin: review findings from part 2 implementation.

## Design-side on-ramp

fired: rows 1 — user chose direct

## Queue relation

unqueued — completes the already approved cross-host review-gate hardening arc.

## Problem

Part 2 correctly established a portable context packet, but its plan split
callers by files instead of by the packet's data flow. Code review must hand
the exact packet to delegated docs review; host adapters must exist before a
docs terminal route claims host-complete behavior; every reviewer artifact and
terminal verdict must identify the same immutable SHA it reviewed.

## Users

- Maintainers who need code, docs, and SDD review to mean the same thing.
- Kouko, who needs a dogfood result that proves the complete workflow rather
  than isolated wording checks.

## Smallest End State

- BI-1 — Every reviewer input, artifact/diff, and output verdict is bound to
  the packet's valid immutable `reviewed_sha`.
- BI-2 — Code review hands its unchanged packet to docs-only and mixed routes;
  docs uses it when handed and resolves one only when no caller supplied one.
- BI-3 — Claude Code and Codex have explicit, tested adapters: Claude may use
  same-reviewer delta confirmation; Codex runs a labelled fresh whole-artifact
  review. Both return a current-SHA terminal verdict.
- BI-4 — A local isolated-consumer dogfood test covers code-only, docs-only,
  mixed, and SDD routes; every marker path rejects stale SHA and accepts only
  a schema-valid current-SHA terminal verdict.

## Decision

Sequence work by packet ownership: first define its immutable reviewer
contract, then make code review the upstream handoff owner, then provide both
host adapters, then complete the docs terminal consumer, and only then run the
end-to-end dogfood fixture.

## Alternatives Considered

- Let each station resolve a replacement packet — rejected because it permits
  one logical review to span different commits.
- Document the host adapters after docs acceptance — rejected because docs
  cannot truthfully claim a host-complete terminal route without them.

## Out of Scope

- Replacing the privacy judge.
- Live model-costing Claude Code or Codex dogfood runs.
- New reviewer roles or model-selection changes.
