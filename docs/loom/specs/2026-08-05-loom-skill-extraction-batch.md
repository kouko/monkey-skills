# Brief: loom-code skill extraction batch (writing-plans / SDD / requesting-docs-review)

Date: 2026-08-05
Source: user directive（「用跟剛才一樣的方法幫其他 loom-* 的 skill 檔案瘦身」）
applying the pilot recipe validated by PR #651; three parallel recon
sweeps this session (their partitions are transcribed here — they exist
nowhere else).
Status: FROZEN.

## Problem

Three loom-code SKILL.md files sit at the CHK-SKL-010 wall:
`writing-plans` 4496/4500 (found by this arc's own measurement — tighter
than either known file), `requesting-docs-review` 4490, and
`subagent-driven-development` 4482. Same tax as the pilot: every future
contract fix pays word surgery first.

## Method (pilot recipe, PR #651)

Zero-pin sections move whole behind pointers; audience-misplaced
maintainer evidence moves to author-facing `design-evidence.md` files
("do NOT load this file at runtime" header); load-bearing rules,
test-pinned text, transcribed-verbatim contract blocks, and
externally-referenced headings stay inline. Equivalence bar: existing
pin-test files untouched BY THE EXTRACTION (the version-pin rewrite in
T4 is excepted — the pilot's frozen-absolute lesson, scoped here at
freeze time) and green; pointer-pin pytests per file; cold-read probes.
Pilot lessons baked in: fix relative links when prose moves one level
deeper; never leave a referent ("the table above" class) pointing at
moved content; never rename/renumber externally-referenced headings or
steps; never resurrect retired negative-pin phrasings.

## Partition A — writing-plans/SKILL.md (4496 → target ≤3900)

MOVE (all verified zero-pin, zero inbound §-referents):
1. §Cross-skill contract (194w) → `references/cross-skill-map.md`;
   residue: one line naming the delegation convention + pointer. Fix
   relative links (one `../` deeper).
2. §What this skill does NOT do (101w) → folded into
   `references/cross-skill-map.md` (its own H2 there); residue: pointer
   line.
3. §Red Flags — refuse these rationalizations (340w) →
   `references/red-flags.md`; residue: one-line refusal-posture
   distillation + pointer (pilot house shape). PROBE-GATED: the
   pressure probe must show a weak model still refuses; FAIL → move
   back, ship 1-2 + D only.
4. Maintainer-facing fragments (~178w) →
   `references/design-evidence.md` (author-facing header): the Beck
   Child Test quote + "verbatim" narrative in §BLOCKED fallback (the
   5-step process and anti-pattern paragraph STAY); the "Why depth —
   heuristic not law" paragraph in §Plan size ceiling; the
   spec-kit/OpenSpec/Jira precedent parenthetical and the
   D8/code-reviewer mirror parenthetical inside §Consuming (splice
   around pins — that section is otherwise UNTOUCHABLE: 3 test files /
   15 functions pin it clause-level).
MUST NOT MOVE: §Consuming a loom-spec change-folder (except the two
parentheticals); §Amending a PASS plan (test_post_pass_amendment_gate
pins phrases AND an exact count of 3 list items); the splitting
framework, plan-size core rule, When-NOT-to-use, Output contract
schema; §-referenced headings stay present.

## Partition B — subagent-driven-development/SKILL.md (4482 → target ≤3900)

MOVE (all verified zero-pin):
1. Environment hygiene block (~110w net) → APPEND as a section of the
   existing `references/dispatch-hygiene-notes.md` (its preamble's
   two-kind sentence gains this as standing guidance; check for
   near-duplicate dcg framing against environment-gotchas.md before
   pasting); residue: pointer line.
2. Progress ledger (~220w net) + Decision Log maintenance (~125w net) →
   new `references/plan-ledger-notes.md` (keep both H-headings
   identical in the new file); residues: one pointer line each.
3. Definition of Done — command-surface accretion (~220w net) → new
   `references/command-surface-accretion.md`; residue: ~30w core-rule
   stub (accretion binds capability-add to surface-declare) + pointer.
MUST NOT MOVE: Mechanical review-weight exemption AND Prose
review-weight substitution (test-pinned ~15+ assertions AND
plan-format.md names both headings as external transcription
contracts); §Verdict resolution; §Model selection (Check-17 SSOT
pointer line); §Status handling (BLOCKED anchor windows); ② What to
bring (whole-file pins); step 2's NEEDS_CONTEXT cap sentences. The
version/Phase provenance parentheticals and the Horvitz/design-doc
citations MAY move to `references/design-evidence.md` (new,
author-facing) as polish if word math wants them — not required.

## Partition C — requesting-docs-review/SKILL.md (4490 → target ≤4100, HONEST REDUCED SCOPE)

Recon verdict transcribed: pin saturation far exceeds the pilot's file
(two test files, ~30 windowed functions; phrase-level pins in every
major section; negative pins ban retired phrasings). ≥600 words is NOT
reachable without touching operative prose. DECISION (recorded here at
freeze): safe-tier evidence extraction only, ~476w gross / ~396w net —
fragments A-K per the recon: citation tails and worked-example asides
in Directives 1/2, Step 3's recorded-miss citation sentence, the intro
audit citation, Red Flags row-1 evidence tail (removes a duplication),
the Aggregation "revisit if" clause — all → new
`references/design-evidence.md` (author-facing header), rule sentences
staying inline verbatim.
MUST NOT MOVE: both §Pinned contracts (verbatim wire protocol); the
Verdict-structure YAML; Aggregation gating logic; all Directive rule
sentences; heading names and step numbers (requesting-code-review and
cross-skill-map reference them by name/number with no test coverage on
the pointing side). NEVER reintroduce: "three gating defects", "the
next round caught", "worse of the two arms' scores", "deferred on the
record", "last minted round", bare "without pass".

## Smallest End State

1. writing-plans ≤3900; SDD ≤3900; requesting-docs-review ≤4100 —
   each with its destination files, itemized residues + pointers, and
   a pointer-pin pytest (headings absent from body / present in
   destination; residue+pointer lines present; word ceiling; retained
   pinned survivors still inline).
2. Full suite green with every pre-existing pin-test file untouched by
   the extraction tasks (T4's version-pin rewrite excepted, version
   strings only).
3. Cold-read probes CLEAN, recorded in a dogfood file: (a) red-flags
   pressure probe on writing-plans (haiku; #A3 exit clause on FAIL);
   (b) comprehension probes sonnet + haiku per file (three load-bearing
   questions each, answered from the slimmed body alone); (c) link
   sweep per file (every relative link resolves, including inside
   moved content).
4. loom-code 0.54.0 → 0.55.0, four bump deliverables; suite green
   post-commit.

## Out of scope

- Any wording change to rules that stay (pure move; splice connectives
  and itemized residues only).
- requesting-code-review (done in the pilot); all other loom-* plugins
  (their files are far under cap).
- The higher-risk trim tier for requesting-docs-review (~+120w) —
  deliberately declined; revisit only if a future arc actually needs
  the room.
- Renaming/renumbering any externally-referenced heading or step.
