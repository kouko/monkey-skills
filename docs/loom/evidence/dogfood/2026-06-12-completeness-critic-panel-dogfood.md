# Dogfood — completeness-critic v0.2.0 diverse-critic panel (run on the PiP-note-app draft)

> Date 2026-06-12. Target: the shipped `spec-toolkit:completeness-critic` v0.2.0 panel (PR #391, merged `55abacb1`).
> Input draft: `docs/spec-toolkit/dogfood/2026-06-12-pip-note-app/` (proposal.md + specs/, spec-expansion v0.2.1 output — kouko's product idea, LOCAL ONLY, not published).
> Method: executed the shipped SKILL.md literally — dispatched 5 fresh-context lens-critics (NFR/security, policy/permissions, missing-object [seed-only view], state-completeness, cross-object/system), each with a distinct persona + input view, per the panel spec. Then ran the overlap diagnostic + consolidation. Purpose: find ADOPTION GAPS that only real execution surfaces (the F-1/F-3 lesson — `feedback_real_dogfood_catches_semantic_bugs`).

## Did the panel WORK? (value check — yes)

The panel surfaced genuine high-value omissions the spec-expansion writer missed, beyond the draft's own 6 blind spots:

- 🔴 **Screen-capture / screenshare leakage** (NFR lens) — notes floating over other apps are captured in Zoom/screenshots/recordings; the writer was structurally blind to it. **Exactly the H4 prediction** (generic omission-hunt blind to NFR/security; the load-bearing-#1 lens earns its rank).
- 🔴 **IME / CJK composition mid-keystroke** (state lens, confused-first-timer persona) — the seed is literally Chinese; macOS IME emits one commitText on accept, so composition interleaving with autocomplete/render/conflict is a real data-loss edge the draft never specs. Concrete, only the state lens + persona caught it.
- 🔴 **Crash durability / atomic-autosave / torn-file** (NFR ∩ system, multi-lens convergence) — the draft says "autosave" on every nav edge but never specs durability/atomicity/WAL.
- 🔴 **Multi-device SIMULTANEOUS-edit merge semantics** (system ∩ policy ∩ missing-object[ConflictResolver]) — the draft has C3 "conflict arrives while typing" but never the true two-devices-both-editing convergence model (LWW/CRDT/OT).
- 🟡 Accessibility-permission-denied fallback; note identity (UUID vs title collision on multi-device create); missing structural objects **SearchIndex / Preferences / HotkeyRegistry / MarkdownAssets(images/attachments)** — the seed-only missing-object critic caught these *because* it was blind to the draft's 7-object OOUX (the input-view decorrelation lever paid off).

**Decorrelation levers all paid off:** (a) seed-only input view → caught dropped structural objects; (b) nfr_security load-bearing #1 → caught the single highest-value blind spot; (c) personas changed salience (confused-first-timer→IME, 3am-on-call→torn-file/races, compliance-auditor→App-Store-entitlement-review). Overlap ~40% (healthy — convergence on load-bearing gaps, not >70% redundant).

## Adoption GAPS (the real dogfood payoff — surfaced only by running the panel)

Both gaps are **consequences of the v0.1.0 single-agent → v0.2.0 panel change** that the design + per-task review did NOT catch, because they only appear when you actually execute a 5-subagent panel on a real draft (the F-3 pattern: a rule that was fine for the old shape becomes a forced-fit after the v0.2 change).

### F-1 (🔴 the load-bearing gap): loop-until-dry was written for a CHEAP single agent; a 5-critic panel makes each round expensive → the executor is pulled to skip the loop

The shipped `## loop-until-dry` rule (inherited verbatim from v0.1.0) says: re-seed every gap, sweep all lenses again, terminate after **K=2 consecutive dry rounds**. When each "round" was one agent's 5 blind passes, looping ~3× was cheap. **Now each round is 5 fresh-context subagent dispatches** → K=2-dry means ~15 subagent calls. Running the panel, I instinctively wanted to STOP after one thorough round rather than re-seed and re-dispatch all 5 critics twice more — the exact F-1 "executor reasons around the expensive instruction" failure spec-expansion hit with `pairwise.py`. The skill gives the executor no cost-aware off-ramp, so under real cost pressure the loop rule gets silently skipped.

**Fix direction (v0.2.1):** reconcile the loop with the panel's per-round cost. Make re-seeding **targeted, not blanket**: after round 1, re-dispatch **only the lens(es) whose re-seeded gaps open a genuinely new object/actor/state-class** (a real new seed), and escalate to a full second panel round **only** when a re-seed surfaces a new defect class — not on a blanket K=2-dry sweep of all 5 critics. Keep K=2-dry as the *logical* stop, but bound the *mechanism* to "re-run a lens only when its input actually changed." (Mirrors the depth-not-count / WIP discipline — bound the expensive thing, not the backlog.)

### F-2 (🟡): the panel emits a 5-way UNION (40+ raw findings); the "How you write back" section assumes a single consolidated list → missing a dedup-rank-triage step before re-seeding

v0.1.0's single agent naturally produced one consolidated, de-duplicated list. The v0.2.0 panel produces a **fragmented union across 5 critics with cross-lens duplicates** (durability appeared 2×, multi-device merge 3–4×, autocomplete-privacy 4×). The shipped `## How you write back` says re-seed gaps as `critic-found` provenance + candidate GIVEN/WHEN/THEN scenarios — but with 40 raw findings and no specified **consolidation pass** (dedup across lenses → rank by severity × cross-lens-convergence → keep the load-bearing set), the executor risks dumping noise back into the spec. The experiment's ~3–4× precision win is per-critic; the *panel-level* union still needs a merge/rank step the skill underspecifies.

**Fix direction (v0.2.1):** add a short **consolidation step** between UNION and write-back: dedup semantically across lenses, rank by (severity × number-of-lenses-that-found-it) — cross-lens convergence is the precision signal — then re-seed only the ranked load-bearing set as `critic-found` + candidate scenarios; list the long tail under blind-spots/residue, don't pad the spec with all 40.

### F-3 (🟢 minor): overlap diagnostic is advisory prose, not a forcing step

The `### Overlap-rate diagnostic` rule reads as "after each round, judge overlap" but isn't wired as a step the executor must emit — running the panel, I had to consciously remember to compute it. Low severity (it's correctly advisory), but a one-line "report the overlap judgment in the round summary" hook (which the round-summary line already half-implies) would make it land.

## Verdict

The panel **works and delivers** (found 4× 🔴 high-value omissions the writer was blind to, decorrelation levers all paid off, nfr_security-#1 validated live). But two real adoption gaps — **F-1 loop-cost (🔴)** and **F-2 union-consolidation (🟡)** — are v0.2.0 coherence debts from not reconciling the inherited single-agent loop/write-back machinery with the new panel cost/shape. Recommend a **v0.2.1** prose fix (both are SKILL.md-only): targeted-re-seed loop off-ramp + a consolidation/rank step before write-back + the overlap forcing-line. Same shape as spec-expansion's v0.2.1 dogfood hardening (F-1/F-3 there).
