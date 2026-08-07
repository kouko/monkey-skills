# Brief — arc 1: mechanical drift-guards for four duplicated loom rules

Date: 2026-08-07 · Branch: `refactor/loom-mechanical-dedup-arc1` @ d1e50685
Origin: docs/loom/backlog/2026-08-07-execute-complexity-audit-keep-lanes.md (arc 1)
+ docs/loom/audits/2026-08-07-family-complexity-audit.md (items B1/B2/C2/D2).
Endpoint named: no → human-pumped. Design-side on-ramp: N/A (refactor —
Axis 0 negative guard; backlog ready check ran: COMMITTED-NEXT empty, seed
entry itself is the related OPEN item).

2026-08-07 post-review corrections: measured figures and the C2/CI-pin
rationale updated to match the shipped artifacts; see the plan's Decision
Log.

## Problem

Four cross-file rule duplications in the loom family have no drift
protection: a semantic change to any of them requires a hand-sweep with no
machine-readable carrier list, and the audit ranked this the family's worst
maintenance tax. Deep recon (this brief's Evidence) falsified two of the
audit's premises, so the arc is RESHAPED from "relocate into distribute.py
SSOT" to "pin with drift-guard tests":

- B1 state-anchor: NOT 7 hand-copies of one text — 12 grep hits across 9
  files (recon's original "11 locations in 10 files" was itself a miscount
  against the same base tree; the shipped pin,
  scripts/test_state_anchor_carrier_inventory.py, is the source of truth),
  all deliberate paraphrases at different compression levels, none
  byte-identical. Byte-SSOT would rewrite rendered prose across those 9
  files (not behavior-neutral). Reshape: a carrier-inventory test that pins
  the known location list + shared fragment, giving semantic changes a
  machine-readable sweep list.
- B2 tdd-standard.md ×2: ALREADY managed — distribute.py ROUTE
  ("standards/tdd-standard.md" → both dests, distribute.py:59-62) and
  verify-drift.py:73-97 byte-check it. The audit's "not managed" claim is
  false. Reshape: no code change; correct the audit doc.
- C2 brief-before-asking ×4 routers: the operative trigger sentence is
  ALREADY word-identical across all 4 — loom-discovery's copy wraps
  differently, so the lockstep compares after whitespace normalization;
  only lead-in/fork-noun/one extra loom-discovery sentence differ
  (deliberate per-router localization). Each router's own test pins its
  copy of the sentence independently; nothing asserts the four copies
  stay equal to each other. Reshape: lockstep equality test on the shared
  anchor sentence (whitespace-normalized) (mint_critic_verdict ast-lockstep
  precedent) — no relocation, no per-session preload increase.
- D2 router-card 5 rules: the divergence is a RECORDED deliberate decision —
  session-start:6-11 says "card wording is deliberately compressed, not
  byte-identical — kept out of verify-drift.py scope for now". Reshape:
  honor it; add a token-presence lockstep test (each rule's distinctive
  anchor tokens present in BOTH files) instead of byte registration, and
  update the comment to point at the guard.

Ride-along: fix PR #669's noted debt in the audit doc (:109 "behavior-zero"
residue, :116 stale "42", 50-file grep mislabels 6 production scripts, hook
count 13 includes a gitignored .pyc → 12 tracked) PLUS the two premises this
recon falsified (B1 count/shape, B2 already-managed), and update the
execute-keep-lanes backlog entry to the reshaped arc-1 scope.

## Users

Future maintainers (human or agent) editing any of the four rules; CI as the
drift detector; weak-model readers of the rendered cards (unchanged — no
rendered text changes in this arc).

## Smallest End State

Three new tests + doc corrections + one comment update. Zero rendered-prose
changes, zero relocations, zero new mechanism types (all three tests follow
existing precedents: prose-pin tests, mint_critic_verdict cross-plugin
lockstep).

1. T1 (B1): carrier-inventory test — greps `state anchor|state-anchor` over
   `loom-*/`, asserts the live-carrier list matches the pinned 12-hit,
   9-file inventory (per scripts/test_state_anchor_carrier_inventory.py,
   the source of truth; grep population stated in-test; excludes only
   loom-code/CHANGELOG.md and loom-pipeline/hooks/test-prompts.json — a
   nonexistent path kept for forward-compat;
   loom-code/skills/requesting-code-review/test-prompts.json IS counted).
   Fails when a carrier appears/disappears → the failure message IS the
   sweep list for semantic changes.
2. T2 (C2): lockstep test — compares the shared anchor sentence (after
   whitespace normalization)
   ("≥3 trade-offs, ≥2 implementation paths, or architectural blast radius —
   run `dev-workflow:brief-before-asking`…") across the 4 design-side router
   SKILL.md files.
3. T3 (D2): token-presence lockstep — for each of the 5 load-bearing rules,
   asserts its distinctive anchor tokens appear in BOTH
   hooks/router-card.md:9-13 and skills/using-loom-code/SKILL.md:16-21;
   update session-start:6-11 comment to name the guard.
4. Doc corrections (audit doc + execute-keep-lanes entry) per Ride-along
   above.

## Current State Evidence

- Forward: rules reach readers via SessionStart hook injection
  (loom-code/hooks/session-start renders router-card.md; ask-triage.py:44-45
  card fires on AskUserQuestion) and via SKILL.md render on invocation
  (using-loom-code/SKILL.md:16-21; subagent-driven-development/SKILL.md:47
  carries the fullest state-anchor definition).
- Reverse (SSOT ownership — distribute.py read in full by recon):
  distribute.py owns two hand-registered mechanisms — whole-file ROUTE copies
  (distribute.py:54-99, canonical → skills/*/{standards,rubrics,checklists})
  and HTML-comment marker-block injection into agents/*.md only
  (:170-221, :250-274). verify-drift.py imports both registries
  (verify-drift.py:25-33) and byte-diffs them (:73-97, :106-129). Nothing
  else feeds it. ask-triage.py cannot carry HTML-comment markers (invalid
  Python) — a .py target would need new marker syntax (out of scope).
- Error: drift surfaces only via verify-drift.py exit 1 in CI
  (loom-code-ci.yml); design-side routers under loom-siblings-ci.yml
  (loom-discovery/product-principles/interface-design) and loom-spec-ci.yml.
  Each of the four router tests already pins its OWN copy of the trigger
  triple verbatim (e.g. loom-discovery/scripts/test_using_skill.py:146-149
  and its three siblings) — but the four pins are independent single-file
  assertions; nothing asserts the four copies stay equal to each other, or
  pins the tail clause after the triple. T2 adds that cross-file equality
  lockstep.
- Data: C2 anchor sentence word-identical ×4 (loom-discovery's copy wraps
  differently, so the lockstep compares after whitespace normalization)
  (using-loom-discovery/SKILL.md:59-65 with one extra sentence,
  using-loom-product-principles/SKILL.md:43,
  using-loom-interface-design/SKILL.md:41, using-loom-spec/SKILL.md:19);
  B1 = 12 hits, 9 files per
  scripts/test_state_anchor_carrier_inventory.py (the shipped pin is the
  source of truth, superseding recon's "11 locations in 10 files"; grep
  `state anchor|state-anchor` over `loom-*/`, excluding only
  loom-code/CHANGELOG.md and loom-pipeline/hooks/test-prompts.json — a
  nonexistent path kept for forward-compat;
  loom-code/skills/requesting-code-review/test-prompts.json IS counted);
  tdd-standard.md md5 8063cbb… identical ×2; router-card.md:9-13 vs
  using-loom-code/SKILL.md:16-21 rules 4-5 diverge substantially by design
  (session-start:6-11).
- Boundary: C2 spans 4 plugins → cross-plugin lockstep test follows the
  mint_critic_verdict precedent (a test in one plugin reads sibling plugin
  files); T1/T3 are loom-code-internal. Plugin versions at branch base:
  loom-code 0.65.1, loom-discovery 0.4.1, loom-product-principles 0.12.1,
  loom-interface-design 0.9.0, loom-spec 0.8.1.

## Decision

Build the three drift-guard tests + doc corrections + comment update, and
nothing else. Do NOT relocate any rule text, do NOT touch rendered prose in
any SKILL.md/hook card (except the session-start comment, which is
non-rendered), do NOT extend distribute.py to new target classes. Where the
new tests land decides version bumps: tests inside a plugin's scripts/ imply
that plugin's patch bump; a repo-root location avoids bumps but needs CI
wiring — writing-plans decides per file with the CI paths evidence above.

## Out of Scope

- Any rendered-text normalization of the four rules (incl. C2 fork-noun
  unification — deliberate localization stays)
- distribute.py support for .py targets or SKILL.md marker blocks
- The other audit KEEP items (E1/E3 legislation arc, D1 index generation,
  A-lane prose slims) — later arcs per the execute entry
- B1 full-text SSOT (re-trigger: if T1's sweep list is ever walked twice for
  real semantic changes and the paraphrase sweep proves error-prone,
  reconsider)

## Alternatives Considered (Axis 4)

Pre-triaged by the audit → proposal-critique → two docs-review rounds; the
in-house SSOT+drift machinery is the industry-standard shape (config-as-code
drift checks). Narrow space; recon replaced the one open fork (C2 carrier:
family-reception relocation vs lockstep pin) with evidence — the sentence is
already word-identical (loom-discovery's copy wraps differently), so the
pin wins: zero preload cost, zero cross-plugin file dependency, precedent
exists. No further research needed.

## What Becomes Obsolete (Axis 5)

- session-start:6-11 "kept out of verify-drift.py scope for now" caveat →
  superseded by T3 (comment updated in-arc)
- The audit doc's B1/B2 premises and the four noted-debt values → corrected
  in-arc
- execute-keep-lanes entry's arc-1 description → updated to reshaped scope

## Open Questions

- Test placement (per-plugin vs repo-root scripts/) — writing-plans decides
  with the CI paths evidence; affects which plugins get patch bumps.
