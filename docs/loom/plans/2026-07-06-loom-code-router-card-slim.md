# loom-code router-card slim — brief + plan (2026-07-06)

## Problem (upstream artifact)

`docs/harness-audit/2026-07-06-a-harness-diagnosis.md` diagnosis #1:
the loom-code SessionStart hook injects the **full** `using-loom-code`
SKILL.md body (~11 KB consumed context) on `startup|clear|compact` in
every project — ~3.1M input tokens/30d floor (865 sessions). The full
body is redundant pre-invocation: the Skill tool loads it anyway when
the router fires. BACKLOG entry: "SessionStart reception slimming".

## Smallest end state

`loom-code/hooks/session-start` injects a new `hooks/router-card.md`
(~2 KB) instead of the full SKILL.md. Nothing else changes: same
3-key JSON emission, same `LOOM_CODE_MODE=off` escape hatch, same
fail-open on missing file, same banner. loom-pipeline reception is
**out of scope** (already pointer-only, 3.1 KB).

## Card content contract (wording is contract surface — see
docs/loom/memory/preamble-wording-is-contract-surface.md)

KEEP (verbatim-or-tightened, never paraphrased into new vocabulary):
- SUBAGENT-STOP block
- The coding mandate line ("must route through this skill before
  writing implementation code")
- The five load-bearing rules (numbers, skill names, violation
  framing; decorations like ISBN may drop, rule sentences stay)
- The anti-rationalization line ("Skipping any of these = violation…")

ADD:
- One pull-pointer line: full routing (stage order, red flags,
  continuous mode, references) loads when `using-loom-code` is invoked.

CUT (available post-invocation via Skill load):
- Instruction priority, How to access skills, Skill-priority stage
  table, Continuous mode, Red-flags table, Skill types, Coexistence,
  What-this-router-does-NOT-do, Reference list.

## Firing gate (user-mandated: 驗證過才准剪)

A/B on the 28-record corpus (`docs/loom/firing-corpus/*.jsonl`),
method per `docs/loom/dogfood/2026-07-04-family-tissue-firing-test.md`:
- Arm A (baseline): main-state plugins via `--plugin-dir` ×5
- Arm B (candidate): branch-state plugins via `--plugin-dir` ×5
- Both arms: `--model sonnet` wrapper (weak-tier gate — the audience
  the card must keep working for), neutral empty cwd, max-turns 4.
- PASS bar: arm B shows no new over-fires on near-miss, and no loss
  of coding-mandate fires / upstream recommendations relative to
  arm A **under the same model** (2026-07-04 adjudication rules:
  error_max_turns records keep their valid `fired` field).

## Acceptance

1. New integration test RED→GREEN: injected ctx is 1-5 KB, contains
   SUBAGENT-STOP + five-rule tokens + mandate, does NOT contain
   full-body-only markers ("Skill priority — decision order",
   "## Continuous mode").
2. Existing tests stay green (mode-on >1000 chars, mode-off empty,
   3-key shape).
3. Firing A/B PASS per above; report at
   `docs/loom/dogfood/2026-07-06-router-card-firing-ab.md`.
4. plugin.json 0.23.1 → 0.24.0, CHANGELOG entry, marketplace.json
   description unchanged (sync check).
5. Whole-branch review PASS before push/PR; no auto-merge.

## Tasks

1. RED: `tests/integration/test-router-card-slim.sh`
2. GREEN: `hooks/router-card.md` + `session-start` CARD_PATH swap
3. Docs sweep: session-start header comment, TECH-SPEC/README
   mentions of full-SKILL injection
4. Version + CHANGELOG
5. Firing A/B (background) → report → adjudicate
6. Review → git-memory → push → PR
