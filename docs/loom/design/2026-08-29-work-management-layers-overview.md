# Loom work-management layers — architecture overview

> Status: descriptive overview, verified against the shipped contracts
> as of loom-workflow 1.3.0 / loom-code 0.103.0 (2026-08-29). Items the
> in-flight protocol-hardening arc (loom-workflow 1.4.0, plan
> `docs/loom/plans/2026-08-29-decision-map-protocol-hardening.md`) will
> add are marked **[1.4.0-pending]**. This is a development record, not
> a runtime contract; each layer's own skill/README stays its SSOT.

## The one-sentence model

Loom manages work through five layers of decreasing granularity —
direction (maps), queue (backlog), arc (brief→plan), execution (SDD),
close-out (finishing) — where **layers are stages of refinement, not
containers**: every layer has its own entry points and its own item
lifecycle, arrows mark typical feed directions, and items reference
each other through greppable join keys rather than nesting.

## Layer diagram

```
┌──────────────────────────────────────────────────┐
│ L0 north star  docs/loom/PURPOSE.md              │
│ why the repo exists; bet entries link here       │
└────────────────────────┬─────────────────────────┘
                         ▼ only foggy multi-session direction enters L1
┌──────────────────────────────────────────────────┐
│ L1 direction  docs/loom/maps/<map-id>/           │
│ multiple live maps; tickets (grilling/research/  │
│ task/prototype) + fog; output = ratified         │
│ decisions, never code                            │
└────────────────────────┬─────────────────────────┘
                         ▼ task ticket files a backlog entry (one feeder
                           among several — see §Not containment)
┌──────────────────────────────────────────────────┐
│ L2 queue  docs/loom/backlog/                     │
│ standing pool, open/bet/closed + generated       │
│ BACKLOG.md index; "what is worth doing next"     │
└────────────────────────┬─────────────────────────┘
                         ▼ a bet is taken up — or the user names work
                           directly (Queue relation: unqueued)
┌──────────────────────────────────────────────────┐
│ L3 arc (one branch = one arc)                    │
│ brief (specs/, BI-n items)                       │
│ → plan (plans/, tasks + Status ledger + Stage)   │
└────────────────────────┬─────────────────────────┘
                         ▼ plan dispatches task by task
┌──────────────────────────────────────────────────┐
│ L4 execution  SDD                                │
│ per task: implementer + spec-reviewer +          │
│ code-quality-reviewer; TDD iron law              │
└────────────────────────┬─────────────────────────┘
                         ▼ one commit per task (git-memory trailers)
┌──────────────────────────────────────────────────┐
│ L5 close-out  finishing                          │
│ whole-branch review → verification → privacy     │
│ gate → PR → CI → human merges                    │
└──────────────────────────────────────────────────┘
```

## Not containment — the key reading rule

The stack is a refinement flow with **multiple entry points**, not a
nesting hierarchy:

- **L2 is not "inside" L1.** A map's `task` ticket filing a backlog
  entry is one feeder; backlog entries equally arrive from dogfood
  findings, review debts, close-out follow-ups (L5), and direct user
  filing — with no map involved.
- **L3 does not require L2 or L1.** A brief's `Queue relation` field
  legitimately reads `unqueued — <reason>`; the user naming work
  directly opens an arc with no bet behind it.
- **Every layer's items have independent lifecycles.** A map retires
  (`clear → archived`) without touching the backlog entries its task
  tickets created; a backlog entry outlives any arc; a plan freezes at
  merge while its map lives on.
- **Jump-in is by problem shape**: fog-heavy multi-session direction →
  L1 (on-ramp row 6, recommended and user-answered, never forced);
  known-worthwhile-but-not-now → L2; decided and ready → L3; a
  one-line known-pattern fix → straight to L4's TDD discipline. Routine
  bug-fix/refactor arcs never meet row 6's own condition (multi-session
  AND foggy), so they enter at L3/L4 without an L1 detour.

## Layer responsibilities

| Layer | Component | Question it owns | Granularity | Terminal state |
|---|---|---|---|---|
| L0 | `PURPOSE.md` | why does this repo exist | one statement | rarely changes; absent in some repos (then `bet` promotion prompts for it) |
| L1 | decision map (MAP.md + tickets + fog) | where are we going, when the route is foggy | one session works one ticket (research may span several); a per-ticket question-size cap is **[1.4.0-pending]** | `charting → active → clear → archived` (archival is the owner's explicit act; retired maps stay in place as a decision archive) |
| L2 | backlog store (entries + generated index) | what is worth doing next; debts that must not silently age | one file per entry; `open / bet / closed` | none — entries open and close individually; `closed` may move to `archive/` |
| L3 | brief (`specs/`) → plan (`plans/`) | how one decided piece of work is cut | one arc = one branch; one task = one failing test, ≤1 module | plan freezes at merge; `Stage:` ends at `finishing` |
| L4 | SDD triads | is each task done right | one commit per task; `Status: done(<sha>)` | per task |
| L5 | finishing | is the branch shippable, and is everything written back | once per arc | PR merged by the human — never by the agent |

## Join keys (all greppable strings; no semantic inference anywhere)

| Key | From → To | Written by |
|---|---|---|
| `serves: <link or unrelated — reason>` | L2 `bet` entry → L0 | bet promotion (required only when PURPOSE.md exists) |
| `graduated-from: F-<n>` | L1 ticket → its source fog entry | work-through close |
| backlog entry filename in a ticket's Resolution | L1 `task` ticket → L2 entry | the session resolving the ticket (established practice — Resolution's schema does not pin this grammar the way the other rows are pinned) |
| `Queue relation: in-queue: <entry> / unqueued — <reason> / displaces: <entry> — <reason>` | L3 brief → L2 | brainstorming intake |
| `BI-<n>` in `Brief item covered` | L3 plan task → L3 brief item | writing-plans |
| `Map part: <map-id> / Part: <name>` (plan `## Notes`) ↔ the map's Parts row | L3 plan ↔ L1 map | whoever adds the Parts row; flipped to `done(<sha>)` by `map_parts.py` at close-out |
| `Status: done(<sha>)` | L3 plan ledger → L4 commit | SDD |
| `Decision:` / `Learning:` / `Gotcha:` trailers | L4/L5 commits → recall surface (`memory-grep.sh`) | git-memory gate |

## Cross-layer duties at close-out (L5 write-backs)

Finishing is where the layers reconcile: it regenerates the living-spec
index, flips the plan's `Stage`, closes backlog entries the branch
shipped (with an evidence line + index regen), flips bound map Parts
rows via the decision-map skill, and lands durable lessons in
`docs/loom/memory/`. These write-backs are the mechanism that keeps the
five layers consistent without any layer containing another.

## What each layer never does

- L1 produces decisions, never code; its prototype tickets build only
  on never-merged `prototype/<map-id>/<slug>` fence branches.
- L2 never executes; promotion of a `bet` is never an agent default.
- L3's plan freezes its `Goal` at plan time and is consumed, not
  edited, by L4 (ledger fields excepted).
- L4 never pushes; L5 never merges — the human merges every PR.

## 1.4.0-pending additions (in-flight arc)

- Map selection is human-named (or a recorded signal); ticket selection
  is agent-picked with a recorded basis. **[1.4.0-pending]**
- Destination carries a `user-ratified` line from charting close;
  `validate` gains HITL presence checks. **[1.4.0-pending]**
- Optional `blocked-by:` ticket field makes the frontier computable;
  optional `ratification: pending` records a measured-but-deferred
  prototype conclusion. **[1.4.0-pending]**
- The store-routing criterion (map fog vs backlog: "which destination
  does this unknown block?") becomes SKILL text. **[1.4.0-pending]**
- Additive-only revision constitution lands in map-format §Schema
  versioning. **[1.4.0-pending]**
