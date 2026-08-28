# Wayfinder mechanism & loom family placement — research record

> **Type**: research note (primary-source texts + repo inventory + host-doc
> verification + cross-vendor advisory)
> **Date**: 2026-08-28
> **Consumer**: the arc-E brainstorm
> (`docs/loom/backlog/2026-07-14-pocock-loom-roadmap-arcs-c-d-e-remainder.md`
> arc E "wayfinder-style persistent decision map") and the
> family-integration evaluation arc
> (`docs/loom/backlog/2026-08-10-family-integration-evaluation-seed.md`,
> `docs/loom/backlog/2026-08-10-queue-layer-family-ownership-north-star.md`).
> **Method**: (1) full-text read of the wayfinder skill set from
> github.com/mattpocock/skills + the author's own video walkthrough
> (youtube F3lL98Pj90o, 2026-07-30); (2) Explore-agent inventory of loom
> cross-plugin coupling in this repo; (3) host-primitive verification
> against official Claude Code docs; (4) independent-advisor run with a
> blind codex proposer leg (gpt-5.6-sol, effort high, probe-verified).

## 1. Wayfinder mechanism (primary sources)

Skill proper is ~128 lines of prose (`skills/engineering/wayfinder/SKILL.md`)
+ a 103-line explainer (`docs/engineering/wayfinder.md`); scheduling shell
over companion skills (grilling / domain-modeling / prototype / research /
to-spec / to-tickets). Core mechanisms:

- **Map = one tracker issue** (label `wayfinder:map`), an **index, not a
  store**: Destination / Notes / Decisions-so-far (one-line gists linking
  closed tickets) / Not-yet-specified (fog) / Out-of-scope. Low-res load
  per session, zoom per ticket.
- **Decision tickets** = child issues sized to one ~100K-token session;
  4 types: `research` (AFK subagent), `prototype` (HITL), `grilling`
  (HITL default, + domain-modeling), `task` (unblocks a decision, never
  delivers the destination). HITL tickets forbid the agent answering for
  the human.
- **Fog of war**: deliberately incomplete map. Fog-vs-ticket test =
  "can you state the question precisely NOW" (not answer it). Resolving
  a ticket graduates fog into new tickets; out-of-scope never graduates.
- **Frontier** = open + unblocked + unclaimed (tracker-native blocking);
  claim = self-assign before work; concurrent sessions supported, one
  ticket per session (research excepted).
- **Two modes**: chart (name destination → breadth-first grill → map →
  create-then-wire tickets → fire research subagents → STOP) and
  work-through (load low-res, claim one, resolve, resolution comment +
  close + gist to map, graduate fog).
- **Specs are non-persistent** (author: delete once the code embodies
  them); provenance direction is the mirror of loom's — wayfinder keeps
  raw discussion (tickets) and discards the synthesis; loom keeps the
  synthesis (brief/trailers) and discards the raw discussion.

Author-admitted open defects (from the official FAQ, unfixed upstream):
Notes self-exemption hole (agent writes an execution licence into the
map Notes it owns — documented live-server incident); waterfall trap
(27-ticket map invalid by ticket 13; mitigations: bounded destination +
aggressive prototyping); agent self-answering grilling / self-closing
prototype selection; grilling verbosity fatigue. Video-vs-text
discrepancy: the video says the map "can implement the work for you";
the text makes plan-don't-do the default and calls in-map implementation
the most-reported failure — the text is authoritative.

## 2. Gap analysis vs loom

- loom's planning phase is a straight line; its loops live in execution
  (SDD verdict loop). Wayfinder's loop lives in planning. The missing
  loom state is fog: today an unknown either blocks the plan
  (`OQ [OPEN]`, check_open_questions.py) or queues in backlog — no
  managed middle state.
- Two open backlog entries already describe the hole: arc E
  (2026-07-14) and the milestone layer
  (`2026-08-10-loom-lacks-a-milestone-layer-between-plan-stage-and-direction.md`
  — kumiko hand-kept progress.md drifted 4×; no generator, no gate).
  Same structural slot, two phases (decision progress vs delivery
  progress).
- Ticket-type mapping: grilling→brainstorming session, research→
  research-toolkit:deep-deep-research, task→backlog item. **prototype is
  the only genuinely missing verb** and conflicts with
  `loom-code/skills/brainstorming/references/red-flags.md` ("prototyping
  happens INSIDE the smallest end state") — a doctrine call for the
  brainstorm, not a ticket-type detail.
- Absorb the terrain model (map/fog/frontier/graduation), not the trust
  model (prose norms + human vigilance): wayfinder's known failures are
  exactly the judgment-shaped-prose class this repo already legislates
  into mechanical gates.

## 3. Cross-plugin coupling inventory (this repo, measured)

- Live loom-* cross-plugin coupling is almost entirely **name-based**
  (Skill-tool invocations, agent subagent_type); path-based references
  exist only in monorepo tests / CI globs (never run installed).
- The deepest shared surface is `docs/loom/` — repo files,
  plugin-neutral.
- Family contracts already have a repo-root SSOT:
  `scripts/canonical/loom-family/` fanned out by
  `scripts/sync_loom_family_contracts.py` into loom-code/hooks and
  loom-design references; **loom-workflow is not currently a sync
  target**.
- loom-code ships all family hooks and ~half its scripts are
  family-infra (backlog/queue, loom-memory, on-ramp reception, language
  hooks) — placement by accretion, not by constraint.
- Existing escape hatches: "prefer the repo script, else plugin copy"
  (finishing/SDD/writing-plans), `loom_init.py` store scaffolding,
  plain-file store greps.

## 4. Host primitives (verified against official docs, 2026-08-28)

- `${CLAUDE_PLUGIN_ROOT}`: load-time text substitution; resolves ONLY to
  the declaring plugin's root; no sibling-reference primitive exists; a
  cross-invoked skill's root resolves to the invoked plugin.
- Plugin cache paths on this machine are version-numbered — hardcoding
  sibling cache paths breaks on update.
- Cross-plugin Skill invocation and agent dispatch by name: supported.
  Hooks: every plugin may ship them; all fire; no ordering primitive.

## 5. Independent-advisor outcome (explore mode, blind codex proposer)

Blind proposer (codex gpt-5.6-sol, effort high; packet contained no
incumbent description; incumbent existed only outside its read scope)
**converged with the incumbent on the decision layer**: keep three
plugins, place the map layer in loom-workflow, couple by name only,
no merge now. Early-stopped after normalisation per the skill contract;
verdict recorded inconclusive (no blind judging ran);
normalized_by_is_incumbent_author: true. Cost: 2 codex calls on
subscription auth (probe + proposer, proposer self-reported 74,648
tokens).

Mechanism-level divergences left OPEN for the brainstorm (all four from
the codex leg, externally authored, treated as untrusted input until
adjudicated):

1. **Sibling access to map tooling**: delegation to a public
   `loom-workflow:decision-map` skill + plain-file detection only —
   no repo-scaffolded checker copies (kills the scaffold-drift surface;
   costs one delegation hop).
2. **Live-map detection criterion**: a checker-valid entry in an active
   state, never directory presence (aligns with the standing "no stub
   files" adjudication; the incumbent draft's `ls docs/loom/maps/` test
   fails this).
3. **Sequencing**: map layer lands first; queue/memory/hook relocation
   is a separate compatibility arc, not opportunistic; loom-workflow
   gets an admission rule ("cross-station, multi-session coordination")
   so it does not become the next dumping ground.
4. **Hardening**: store charter carries a schema version (checkers
   refuse newer versions); plan↔map binding uses explicit join keys,
   never topic-similarity inference.

## 6. Sources

- https://github.com/mattpocock/skills — wayfinder + companions (full
  texts read 2026-08-28; fetched copies were session-scratch only, not
  vendored — re-fetch from upstream when quoting).
- https://www.youtube.com/watch?v=F3lL98Pj90o — "/wayfinder: Nothing is
  too big to plan anymore", Matt Pocock, 2026-07-30 (transcript read in
  full).
- https://code.claude.com/docs/en/plugins-reference.md,
  .../skills.md, .../hooks.md, .../discover-plugins.md — host-primitive
  verification.
- This repo: backlog entries named in the header; coupling evidence
  file:line citations live in the session transcript, re-derivable by
  grep.
