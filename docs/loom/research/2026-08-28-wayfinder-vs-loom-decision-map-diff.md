# Wayfinder (upstream) vs loom decision-map — full design diff

> Purpose: complete inventory of where loom's decision-map port follows,
> extends, hardens, or drops the original design, gathered BEFORE
> revising the loom implementation. Upstream side: fresh full-text
> extraction from `github.com/mattpocock/skills`
> (`skills/engineering/wayfinder/SKILL.md` + `docs/engineering/wayfinder.md`,
> fetched 2026-08-28, verbatim anchors in the session transcript's agent
> report). Loom side: `loom-workflow/skills/decision-map/` SKILL.md +
> `references/map-format.md` + `references/prototype-contract.md`
> (v1.3.0), read whole. Companion context: the absorption-time research
> record `2026-08-28-wayfinder-mechanism-and-family-placement-research.md`.

## A. Followed faithfully (terrain model)

| Mechanism | Upstream | loom |
|---|---|---|
| Map body sections | Destination / Notes / Decisions-so-far / Not-yet-specified / Out-of-scope | Same five, same order (+ Parts, see §B) |
| Index-not-store | "a decision lives in exactly one place, its ticket" | Same: gist+link lines only; unlinked decision "does not count as recorded" |
| Fog concept | Deliberately incomplete map; fog-vs-ticket test = "can you state the question precisely NOW" | Same concept; graduation records `graduated-from: F-<n>` |
| One ticket per session, research excepted | Explicit | Explicit |
| Claim before work | Tracker self-assign, "first, before any work" | `claim` frontmatter field + status flip |
| Four ticket types | research / prototype / grilling / task | Same four, mapped to loom verbs (brainstorming / deep-deep-research / backlog / prototype protocol) |
| Task type never delivers the destination | Explicit | Same ("filing the backlog entry IS the resolution") |
| Resolution duties | Resolution comment + close + gist to map + graduate fog | Same, as work-through steps 2–4 |
| HITL on grilling & prototype outcomes | Agent never stands in for the human | user-ratified line, unconditional for both types |

## B. loom extensions (upstream has no equivalent)

1. **Feasibility-mode prototype** — upstream's prototype is design-mode
   only (human reaction); loom adds machine-measured
   constraint-clearing probes. (Used by the family-relocation
   feasibility ticket.)
2. **Risk pass / risk-driven front-loading** — Boehm/RAT/spike-sourced
   trigger list, run at charting close and every work-through close.
   Upstream's only analogue is FAQ advice to "prototype aggressively".
3. **Map lifecycle states** — `charting → active → clear → archived`
   frontmatter vocabulary. Upstream has no map-level state at all; the
   map just stops being worked and hands off to `to-spec` (its FAQ
   defines done = fog exhausted).
4. **Parts / delivery write-back** — join-key-bound plan progress table
   with a flipper script refusing to overwrite `done(<sha>)`. Upstream
   plans-don't-do and has nothing downstream-bound.
5. **Schema versioning** — checkers refuse newer schema versions.
6. **Mechanical gates** — `validate` / `check_map_links` /
   `check_map_fog` (0/1/2 exit contract), fog-id grammar `F-<n>` with
   monotonicity (never renumber, never silently vanish), gist-line
   grammar with last-parenthesized-token parsing. Upstream enforcement
   is tracker primitives + prose only (author admits "no hard in-skill
   stop").
7. **Stale-claim reclaim rule** — reclaimable when no commit touched
   the ticket since the claim date. Upstream has no dead-session story.
8. **Multi-map support** — liveness assessment enumerates
   `docs/loom/maps/*/` and returns a LIST. Upstream is
   single-map-assumed ("a single issue … the canonical artifact").
9. **Prototype branch fence** — `prototype/<map-id>/<slug>` never-merge
   branches, git-guard-blocked where loom-code is installed, retained
   read-only while the map lives, pruning = owner's recorded choice.
   ⚠ See §E discrepancy — upstream's current text has NO prototype
   branch convention (only `research/<name>` throwaway branches).
10. **Notes hardening** — loom: Notes is "never a substitute for a
    Decisions-so-far line or a fog entry". Directly closes upstream's
    documented Notes self-exemption hole (agent writing itself an
    execution licence into Notes).
11. **One-sitting timebox + anti-over-prototyping guardrails** —
    named success criterion before the probe, no-probe-when-a-lookup-
    settles-it, hardening-is-the-stop-signal.

## C. Upstream mechanisms loom dropped (each needs a keep/drop ruling)

1. **Blocking links / frontier** — upstream: ticket dependency links
   via the tracker's native blocking; frontier = open ∧ unblocked ∧
   unclaimed, rendered visually in the tracker UI. loom ticket schema
   has NO blocked-by field; "frontier" appears in loom prose (risk
   pass "front-load onto the frontier") with no mechanical meaning.
   Consequence: upstream's charting step "create tickets, then wire
   blocking in a second pass" has no loom equivalent; ticket ordering
   knowledge lives only in prose (e.g. family-relocation's grilling
   resolution saying sequencing "hangs on the feasibility ticket").
2. **Ticket sizing rule** — upstream: body sized to one 100K-token
   session. loom: no sizing rule anywhere.
3. **Chart-mode STOP when no fog surfaces** — upstream: "you don't
   need a map. Stop and ask the user." loom charting has no
   no-fog-abort; nothing stops charting a map for a fully-specifiable
   effort (over-mapping guard missing).
4. **Parallel research burn-down at charting** — upstream fires all
   research tickets as parallel subagents during chart mode. loom
   treats research tickets as ordinary work-through items (one per
   session, possibly multi-session), and this repo further gates
   deep-research on per-run user authorization.
5. **Map located by human handle** — upstream invocation: "User
   invokes with a map (URL or number)". loom: liveness enumeration
   exists, but no rule says the human names the map (see §D).
6. **Wrong-closed-decision guidance** — upstream FAQ: tell wayfinder
   what changed; it updates the map and comments on closed tickets.
   loom has no reopen/invalidate path for a closed ticket or a
   Decisions-so-far line (fog monotonicity governs fog only).
7. **Companion verbs not ported** — domain-modeling (paired with
   grilling for destination-naming), handoff (conversation ⇄ map
   bridging; loom-workflow:handoff exists but is not wired to
   decision-map), to-spec collapse (loom's downstream is
   brief/plans/Parts instead — deliberate, but the "collapse the
   map's linked decisions into one artifact" step has no named loom
   owner).

## D. Divergent philosophy (deliberate, documented at absorption)

1. **Persistence direction — full reversal.** Upstream: map+tickets
   are transient scaffolding; local-markdown storage in the repo is
   explicitly "not recommended … accidental persistence"; the spec is
   the persisted artifact and even it is author-deleted once embodied.
   loom: the store is repo-native BY DESIGN, committed, validated,
   retained as a permanent decision archive after `clear`/`archived`.
   This is the loom-wide "keep the synthesis, discard the raw
   discussion" provenance stance (absorption research §1) applied in
   the opposite direction to the same artifact.
2. **Trust model.** Absorption ruling: "absorb the terrain model, not
   the trust model" — upstream's prose norms + human vigilance are
   replaced by mechanical gates (§B.6). Upstream's four
   author-admitted defects (Notes self-exemption, waterfall trap,
   HITL self-answering, grilling fatigue) are the motivation.
3. **Tracker-native vs repo-native primitives.** Upstream rides issue
   assignee/labels/blocking; loom re-implements claim/type/state as
   frontmatter + scripts. Cost of the choice: everything the tracker
   gave for free (blocking UI, cross-session visibility) must be
   re-built or consciously dropped (§C.1).

## E. Discrepancy to verify before citing upstream again

`references/prototype-contract.md` claims: "upstream wayfinder
independently converged on `prototype/<name>` never-merged branches
after reversing its own delete-it doctrine — 'a prose summary of a
prototype loses the thing that made it convincing'". Today's full-text
extraction of upstream's SKILL.md + docs.md found **no prototype
branch convention and no such quote** — only `research/<name>`
throwaway branches, and no stated delete-vs-keep doctrine for
prototype artifacts. Possible sources of the claim: the 2026-07-30
video transcript, an upstream revision since absorption, or an
attribution error at absorption time. Until re-verified against the
exact source, treat the fence doctrine as **loom's own** (it stands on
its own merits) and do not attribute it upstream.

## F. Where the 2026-08-28 dogfood findings land on this diff

| Dogfood finding (first work-through session) | Diff location |
|---|---|
| Ticket-selection authority unspecified (agent inferred from branch name) | Upstream ANSWERS it: agent picks the ticket ("you pick the next decision, not the user") once the human has named the map. loom copied neither half. → §C.5 + backlog `2026-08-28-decision-map-ticket-selection-authority-unspecified` |
| Destination has no HITL ratification duty | Upstream charts the destination THROUGH grilling (+ domain-modeling), HITL by construction; loom charting names no such duty. → §C.7 (domain-modeling not ported) |
| "Measured, pending ratification" third state missing | Genuinely novel — upstream prototypes resolve in one HITL sitting, so the state cannot arise there; loom's feasibility mode + deferred ratification created it. → §B.1 side-effect |
| Mid-ticket fog additions unregulated in prose (checker permits) | loom-only surface (upstream fog has no grammar/gate at all) |
| Map summary blind to in-progress work | Shared with upstream (Decisions-so-far is closed-only in both); upstream compensates with tracker UI (open/assigned visible), loom dropped that visibility with the tracker. → §D.3 cost |
| Multi-map selection ambiguity | loom-created (upstream is single-map). → §B.8 |

## G. Revision candidates for the loom implementation (not yet decided)

Ordered by how directly today's evidence supports them:

1. Write the selection-authority rule: human names the map (or a
   recorded signal like worktree-branch == ticket-slug does), agent
   picks the ticket within it and RECORDS the basis in the claim
   marker. (Restores upstream's split + covers loom's multi-map
   extension.)
2. Charting close gains a destination-ratification duty (user-ratified
   line on MAP.md or an equivalent), mirroring the ticket-level gate.
3. Define the claimed-with-progress state (or an explicit
   `pending-ratification` note convention) for deferred prototype
   conclusions.
4. Legalize mid-ticket fog additions in SKILL.md prose (checker
   already permits).
5. Decide §C.1: port blocking/frontier (a `blocked-by:` frontmatter
   field + checker) or record its omission as deliberate.
6. Adopt upstream's chart-mode STOP (no fog ⇒ no map) and the
   100K-session ticket-sizing rule — both cheap prose additions.
7. Add a wrong-closed-decision path (upstream FAQ §8.6) — how a later
   session challenges a closed ticket without violating link/fog gates.
8. Fix or re-attribute the §E citation in prototype-contract.md.
