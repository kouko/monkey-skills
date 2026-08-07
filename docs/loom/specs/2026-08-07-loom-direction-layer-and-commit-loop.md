# Brief — loom direction layer (DIRECTION.md) + commitment loop

Date: 2026-08-07 · Branch: (pending) · Origin: user decision "把整個
ROADMAP / todo list / backlog 機制做完整" after the 2026-08-07
complexity-audit arc closed; option A + the name DIRECTION.md both
user-拍板 in conversation. Endpoint: PR-open terminal, never auto-merge.
Design-side on-ramp: N/A — process/tooling for the repo itself, not a
user-facing product surface (precedent: the backlog-verbs arc, 0.59.0,
went straight through brainstorming).

## Problem

**Scope note (user correction, 2026-08-07): the subject is the loom
MECHANISM, not this repo.** loom's work-planning funnel — brainstorm →
plan → SDD → finishing → backlog — is a portable capability any
consuming repo adopts (the backlog store already ships this way:
stations fire conditionally on `docs/loom/backlog/` existing, scripts
carry absent-in-this-repo fallbacks). The funnel is missing its top two
layers AS A MECHANISM; every consuming repo hits the same gap.
monkey-skills is evidence exhibit #1 and the first consumer, not the
product:

1. **No direction layer.** "Where is this repo going" exists nowhere —
   five per-plugin ROADMAP.md files all froze at birth (four still claim
   pre-ship states; loom-code's says "no skill shipped yet" at 0.68.0).
   Cold-starting a session on "what's next?" requires re-scanning 76
   OPEN backlog entries and rebuilding a menu from scratch (happened
   live, 2026-08-07).
2. **No commitment loop.** The backlog charter defines COMMITTED-NEXT
   ("decided, scheduled, next in line", ≤5 policy) with read verbs wired
   (--ready, Axis 0 kickoff read, finishing close) — but NO station ever
   proposes promotion into it. Entries are born OPEN/PARKED; the queue
   has been empty since the 0.59.0 inventory. Read and close loops exist;
   the write loop does not.

Research (4 reports, EN+JP converging): no surveyed practice keeps a
forward-looking artifact alive by discipline — only (a) artifacts that
are the working surface of a recurring decision ritual, or (b) artifacts
mechanically forced by a ceremony on the commit path. The agent-tool
survey sharpened this: release notes never rot (publishing forces the
write); every forward artifact without a forcing ceremony rotted —
including claude-task-master's own tasks.json (stale 7 months inside the
task-management tool's own repo), BMAD's bucket roadmap, OpenHands'
milestones. Planning-tool authors steer their own repos by issues +
intuition. spec-kit's constitution and superpowers' plan files are the
two survivors — both live because feature PRs must touch or produce
them. loom already owns the rare precondition the dead projects lack:
mandatory gates on the commit path (Axis 0 read at kickoff, Step-8
close-out table at finishing).

## Users

- **Any consuming repo's human owner** — direction owner of THAT repo;
  the only writer of its Next/Later and the only promoter into its
  COMMITTED-NEXT (agents never self-commit). Direction is per-repo,
  exactly as the backlog store is per-repo.
- **Agents working in any consuming repo** — cold-start readers: one
  file answers "where is this repo going, what's next" without a
  full-backlog scan.
- **Stations (the portable teaching surfaces)** — brainstorming Axis 0
  (reads, conditional on the file existing, silent-N/A like the ready
  check), finishing Step 8 (closes + triggers the betting moment,
  conditional + fallback wording like the backlog-close row).
- kouko + monkey-skills — first consumer (dogfood), supplies the seed
  content and the live verification that the loops actually fire.

## Smallest End State

1. **`docs/loom/DIRECTION.md`** — one file, three sections + a short
   charter header stating its own update rules:
   - `## Now` — **generated** from COMMITTED-NEXT entry files (derived
     state, never hand-edited; same doctrine as BACKLOG.md and the
     memory §Index — shared-index store lesson).
   - `## Next` — themes only (arc-shaped candidates, one line each,
     optional pointer to a backlog entry), human-written only.
   - `## Later` — direction themes, no dates anywhere in the file
     (granularity rule: distance = vagueness; nothing distant needs
     upkeep, so nothing distant can rot).
2. **Generation + validation**: `backlog_index.py` grows a
   `--direction` write/check pair (or the plan chooses a sibling
   script) that regenerates `## Now` from entry frontmatter; flagless
   validation stays the independent guard (arc-3 doctrine). CI-adjacent
   hook optional, NOT required.
3. **Betting moment (the missing write loop)**: finishing's
   backlog-close row gains one sentence of duty — after flipping
   SHIPPED, if COMMITTED-NEXT is EMPTY, surface a betting prompt to the
   user: candidates = `--ready` output + DIRECTION `## Next` themes;
   the USER promotes (edits status to COMMITTED-NEXT) or declines;
   agents never auto-promote. Manual betting anytime remains legal.
4. **Kickoff read**: brainstorming Axis 0's ready check extends one
   line — also read `docs/loom/DIRECTION.md` when present (surface
   Now + Next alongside the ready queue; same recommend-once posture).
5. **Charter sync**: backlog README §Verbs gains the fourth flow
   (Bet/promote — user-only), and the COMMITTED-NEXT tier description
   cross-references DIRECTION.md's generated Now.
6. **Five ROADMAP.md tombstones**: one header line each — historical
   design record, superseded; forward direction lives in
   `docs/loom/DIRECTION.md` (kills the necromancy grep problem).
7. Pin-test migration (3 files name COMMITTED-NEXT / charter wording:
   scripts/test_backlog_index.py, scripts/backlog_index.py's own
   asserts, loom-code/scripts/test_finishing_backlog_close.py) +
   loom-code minor bump (brainstorming + finishing SKILL.md change) +
   CHANGELOG.
8. **Portability requirements (mechanism-first, non-negotiable)**:
   every station edit fires CONDITIONALLY on the target repo having the
   artifact — Axis 0 reads DIRECTION.md only when present (silent skip
   otherwise, matching the ready check's no-store posture); finishing's
   betting duty fires only when both the backlog store and DIRECTION.md
   exist, with an explicit absent-artifact fallback wording (matching
   the backlog-close row's script-absent pattern); generation scripts
   live at the repo root and ship in no plugin, so station wording must
   carry the "checker not present in this repo" N/A form. The
   convention's SSOT is DIRECTION.md's own charter header (per-repo,
   like the backlog README) — station text points, never copies.
9. **Initial content ride-along (first-consumer dogfood)**: seed
   monkey-skills' DIRECTION.md Next/Later with the user's actual
   current direction (collected at kickoff briefing — a mechanism
   shipped empty would be the sixth frozen roadmap), and let this
   arc's own close-out exercise the betting moment live.

## Current State Evidence

- Charter: status enum docs/loom/backlog/README.md:17; ≤5 policy
  :120-121; §Verbs :115 (Ready :119 / Close :125 / Kickoff :132).
- Live counts (main @ 1d5afad1): OPEN 76, PARKED 12, SHIPPED 11,
  UPSTREAM 2, CLOSED—SUPERSEDED 2, COMMITTED-NEXT 0.
- backlog_index.py argparse :573-600 (--validate/--write/--check/--ready).
- Wiring points: brainstorming SKILL.md:73-80 (Axis 0 ready check);
  finishing SKILL.md:196 (backlog-close row in the Step-8 table);
  loom-memory SKILL.md:48-51 (record-time routing).
- Five ROADMAP.md staleness: loom-code (claims "no skill shipped yet");
  investing-toolkit (framed post-v2.1.0, reality v2.40.0);
  philosophers-toolkit (2026-04-08 skeleton, skills since shipped);
  legal-toolkit (2026-05-16, unsynced); systems-thinking (manually
  re-synced once 2026-05-13 — the exception proving the no-loop rule).
- PRODUCT-SPEC/TECH-SPEC both frozen at 0.1.0-draft — out of scope here.
- Pin surface: scripts/backlog_index.py, scripts/test_backlog_index.py,
  loom-code/scripts/test_finishing_backlog_close.py.

## Decision

Build A-shape as user-拍板, **as a portable loom convention** (the
mechanism is the deliverable; monkey-skills is its first consumer):
DIRECTION.md (name chosen over ROADMAP — the file refuses
dates/sequence promises, GitLab Direction-pages precedent, and
"ROADMAP" is empirically a dead word in this repo).
Now = generated; Next/Later = human-only prose; betting = event-driven
at close (queue EMPTY → prompt) + manual anytime; promotion =
user-only. Tombstone the five ROADMAPs. Seed real content at ship.
Do NOT build: calendar-driven reviews (solo death mode, JP evidence),
RICE or any scoring machinery (score-theater risk for solo), agent
auto-promotion (direction is the human's), per-plugin roadmap revival,
PRODUCT-SPEC/TECH-SPEC refresh (separate debt), plan_card/DIRECTION
integration.

## Out of Scope

- Reviving or rewriting the five per-plugin ROADMAP.md bodies
- PRODUCT-SPEC.md / TECH-SPEC.md refresh (frozen drafts — own arc if ever)
- Any external PM tool (GitHub Projects/issues) integration
- Scoring frameworks (RICE etc.)
- Calendar/cron-driven review mechanisms
- Codex-side port of station wording (rides the normal sync pipeline)

## Alternatives Considered (Axis 4)

- **B — betting ritual only, no direction file** (superpowers/aider
  live this way: release notes + issues + intuition): rejected by user;
  also the documented Shape Up critique (ideas homeless) and the
  cold-start cost stays.
- **C — direction section inside backlog README**: rejected — charter
  already carries charter+generated-index duties; overload risk.
- **Calendar cadence reviews** (CNCF/GitLab style): rejected for solo —
  JP evidence says solo calendar rituals die; replaced by close-event
  trigger.
- **Heavyweight task graphs** (task-master tasks.json): anti-model —
  rotted in its own repo; our tasks stay as human-readable md entry
  files (independently confirmed best AI-compatibility, JP #2 pattern).
- Research corpus: 5 reports (EN industry, JP industry, EN agent-repo
  survey, JP agent-repo survey, local 19-target survey), 2026-08-07,
  all convergent.
- **Local survey highlights** (19 targets: 14 own repos + dotfiles + 4
  third-party plugin projects): loom's dated plan/spec files are ALIVE
  in 6/13 own repos — last-touch tracks repo last-touch by
  construction, because they are byproducts of doing the work; every
  hand-maintained CHANGELOG found (local + third-party) is frozen or
  decorative, while monkey-skills' plugin CHANGELOGs live because
  version-pin tests force them — the write-forcing wiring, again.
  Three borrowable shapes confirmed or noted: (1)
  kumiko-zaiku-app-icons' `verify-docs.sh` — a companion verifier that
  turns prose ledgers into checked contracts (our --direction
  write/check pair is this pattern); (2) safety-net's CI-generated
  changelog — a generated-not-written ledger section (our `## Now`);
  (3) company-context-layer's `product-context.yaml` — single-writer-
  per-stage state file (considered as an alternative single-file shape;
  rejected for the direction layer because it trades per-arc history
  for a snapshot, and our Now/Next/Later writers are already
  partitioned by section — generation owns Now, the human owns
  Next/Later, which is the same single-writer guarantee without a new
  file format). The notion plugin's remote status-state-machine shape
  noted, not adopted (portable mechanism stays file-based).

## What Becomes Obsolete (Axis 5)

- The five ROADMAP.md files' implicit claim to be the forward plan
  (tombstoned, kept as history)
- The "what's next?" cold-start re-scan (replaced by reading DIRECTION.md)
- COMMITTED-NEXT's dead-letter status (gains its write loop)

## Open Questions

- None blocking. Betting-prompt floor chosen as EMPTY (not <5) — the
  least-nag option, reversible by one word later. Seed content for
  Next/Later comes from the user at kickoff briefing.

## Addendum — same-day design discussion (user-拍板, 2026-08-07)

1. **Roadmap entries (the middle layer).** Between DIRECTION themes and
   single arcs sits the user's requested "ordered sub-goal set with
   dependencies". Shape chosen: **(a) a NAMED PATTERN of ordinary
   backlog entries** — an entry whose body is an ordered arc list with
   dependency notes, serving one DIRECTION theme; DIRECTION `## Next`
   lines may point at such an entry by filename. NOT a new file type,
   NOT a DIRECTION section. Precedent: the complexity-audit's
   execute-keep-lanes entry ran exactly this shape live across five
   PRs. Machine-readable fields deferred (YAGNI) — prose pointers v1.
2. **Backlog = the pool.** Ordinary OPEN/PARKED entries are the
   someday/trigger-gated/debt pool and need no relation to any current
   theme — that is a feature (Shape Up's lost-ideas critique, solved).
   One physical store; the distinction is semantic (entries migrate by
   one status edit, both directions — de-commit precedent exists).
3. **`## Now` = PARALLEL ACTIVE SET, not a serial queue.** The user
   works multiple worktrees with different goals; one Now entry ↔ one
   worktree/lane typically; the ≤5 cap reads as parallel-steering
   capacity. Charter + DIRECTION header must state this definition.
4. **Betting candidate ordering: same-lane first.** When an arc of
   theme X closes, the prompt lists theme X's roadmap-entry next arc
   first (keep the lane hot), then other lanes / ready pool.
5. **Worktree/merge doctrine rides along**: DIRECTION header carries
   one line — on `## Now` merge conflict, take either side wholesale
   and regenerate (`--direction-write`), never hand-merge (store
   entry precedent, twice-proven).
6. **Section name stays `Now`** (Now/Next/Later triad recognizability;
   "Task" rejected for hard term-collision with plan/SDD tasks —
   portability term-collision doctrine).
7. **Seed themes confirmed** (first-consumer content): Next — ①
   investing-toolkit 三大表＋管理層 KPI 完整歷史入 kpi_store ②
   loom-code replay matrix 客觀迴歸量測; Later — ① 投資線營運指標
   敘事層 ② loom 機制 Codex 移植線 ③ obsidian wiki 知識線深化.
