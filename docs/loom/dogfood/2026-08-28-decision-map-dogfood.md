# Decision-map layer — first real map dogfood

Date: 2026-08-28. Task 18 of `docs/loom/plans/2026-08-28-decision-map-layer.md`
(BI-2 exercise; the Smallest End State's "one real map charted and worked in
this repo (dogfood) with all gates exercised" criterion).

## Subject

`docs/loom/maps/family-relocation/` — the family-infrastructure relocation
question held open by the queue-ownership north-star backlog entry. A real,
multi-session, foggy effort; chosen by the user over the kumiko-zaiku
migration candidate (AskUserQuestion, 2026-08-28).

## What was exercised, with transcripts

1. **Scaffold** — `python3 loom-workflow/skills/decision-map/scripts/map_init.py family-relocation --repo-root .`
   → `map-init: scaffolded docs/loom/maps/family-relocation`, exit 0. The
   scaffolded store passed `validate` unmodified.
2. **Charting (HITL)** — destination, four first tickets (grilling /
   research / prototype-feasibility / task), four fog entries (F-1..F-4),
   two out-of-scope lines; drafted by the agent, ratified by the user
   before the state flip to `active`.
3. **Risk pass (BI-12, first live firing)** — the Riskiest Assumption Test
   trigger matched: the whole relocation rests on unverified cross-plugin
   script resolution. A feasibility-mode prototype ticket
   (`tickets/feasibility-cross-plugin-store-access.md`) was front-loaded
   onto the frontier at charting time with its success criterion named
   before any build, per the prototype contract's guardrails.
4. **Work-through of one ticket (HITL)** — `tickets/grilling-first-cut.md`:
   claim-before-work recorded, options presented, user ruled "hooks first"
   (AskUserQuestion), Resolution written with the rejected alternatives and
   a `user-ratified:` line, one gist line appended to MAP.md's
   Decisions-so-far linking the closed ticket, and fog entry F-4 shrunk in
   the same close (its ordering half was answered by the decision).
5. **All three gates, on the worked map** —
   - `map_store.py validate docs/loom/maps/family-relocation --repo-root .`
     → "is a valid decision-map store", exit 0.
   - `check_map_links.py …` → "all Decisions-so-far links resolve to closed
     tickets", exit 0 (a real closed-ticket link this time, not a fixture).
   - `check_map_fog.py …` → "no base version … (new map) — clean", exit 0
     (the new-map branch; the shrink/graduate transitions are pinned by the
     checker's own test suite against real git fixtures).

## Observations

- The one-command scaffold → validate round-trip held on first use; no
  hand-fixes to the template were needed.
- The risk pass produced a genuinely non-obvious scheduling decision (the
  feasibility probe would otherwise have been discovered only when the
  queue-relocation arc opened — the exact failure mode BI-12 exists for).
- The fog checker's new-map branch reports itself loudly ("no base version
  … clean") rather than silently passing — its monotonicity teeth engage
  once this commit becomes the base for future sessions.
- Remaining open on the map: three tickets (research, feasibility probe,
  task) and fog F-1..F-4; the map stays `active` and is now what
  brainstorming Axis 0's Live-map check will surface at the next kickoff.
