# Plan: backlog ready verb + close loop + inventory reset

Source brief: docs/loom/specs/2026-08-06-backlog-ready-verb-and-close-loop.md
Total tasks: 7
Critical-path depth: 4 (≤5)
Execution order: parallel-where-possible (Wave 1 = T1+T2+T3+T4, disjoint files; T5 after ALL of Wave 1; T6 after T5; T7 after T6)
Plan-document-reviewer verdict: PASS (2026-08-06, round 2 — round-1
NEEDS_REVISION's four gaps + two notes fixed and fix-verified)
Endpoint named: yes → continuous (user 「開始吧」 accepted the proposed
arc, whose deliverable is a PR; merge stays with the user)

## Task 1 — backlog_index.py --ready verb

- Description: Add a `--ready` mode to scripts/backlog_index.py: prints
  `## COMMITTED-NEXT` entries first (file-date order: sorted by
  filename, which starts YYYY-MM-DD), then `## OPEN` entries; each line
  is `- <name> — <description>`; an OPEN entry whose frontmatter has
  `start:` gets a second indented line `  start: <value>`; statuses
  PARKED/UPSTREAM/SHIPPED/CLOSED — SUPERSEDED/archived excluded; output
  ends with `ready: N committed / M open / K excluded by status`.
  `--ready` joins the existing mode flags (usable alone; composes with
  `--store`); the no-mode parser error message gains `--ready`. Extend
  scripts/test_backlog_index.py RED-first: a tmp-store fixture with one
  entry per status asserting (a) section order committed-before-open,
  (b) excluded statuses absent, (c) the start: line rendered for an
  OPEN entry that has one and absent otherwise, (d) the count line with
  exact numbers, (e) `--ready` accepted without other modes.
- Module: scripts (repo-root; CI lane loom-code-ci runs `pytest scripts/`)
- Files touched: scripts/backlog_index.py, scripts/test_backlog_index.py
- Context paths:
  - scripts/test_backlog_index.py (existing fixture shapes for tmp stores)
- Acceptance:
  - RED: the new tests fail before the mode exists (argparse error).
  - GREEN: `python3 -m pytest scripts/test_backlog_index.py -q` all
    pass (36 existing + new); live run
    `python3 scripts/backlog_index.py --ready` exits 0 on the real store.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State 1

## Task 2 — brainstorming Axis 0 kickoff read moment

- Description: Insert the pinned block N1 into
  loom-code/skills/brainstorming/SKILL.md §Axis 0, as its own short
  paragraph directly after the paragraph beginning
  `**Negative guard (silent skip)**`; create
  loom-code/scripts/test_brainstorming_backlog_read.py pinning: N1's
  lead phrase, the command string
  `python3 scripts/backlog_index.py --ready`, the N/A-silent clause,
  and the never-hijacks sentence — whitespace-normalized contiguous, +
  a positive-fact control (an existing Axis 0 phrase).
- Module: loom-code/skills/brainstorming
- Files touched: loom-code/skills/brainstorming/SKILL.md, loom-code/scripts/test_brainstorming_backlog_read.py
- Context paths:
  - loom-code/scripts/test_dispatch_hygiene_worktree_section.py (helper shape)
- Acceptance:
  - RED: new test fails against unedited SKILL.md (control passes).
  - GREEN: new test passes; brainstorming word count ≤4500 by len(text.split()).
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State 2

## Task 3 — finishing close moment + queue-tail report line

- Description: (a) Insert the pinned bullet N2 into
  loom-code/skills/finishing-a-development-branch/SKILL.md Step 8's
  hygiene list, directly after the Memory-store integrity bullet;
  (b) append the pinned sentence N3 to Step 13's report description;
  (c) create loom-code/scripts/test_finishing_backlog_close.py pinning:
  N2's lead phrase ("Backlog-close check"), the flip vocabulary
  ("SHIPPED (or CLOSED — SUPERSEDED)"), the same-commit duty
  ("in the same close-out commit"), the regenerate command string
  (`backlog_index.py --write`), the silent-skip clause, N3's queue-tail
  phrase — whitespace-normalized contiguous, + a positive-fact control.
- Module: loom-code/skills/finishing-a-development-branch
- Files touched: loom-code/skills/finishing-a-development-branch/SKILL.md, loom-code/scripts/test_finishing_backlog_close.py
- Context paths:
  - loom-code/scripts/test_finishing_attached_head_check.py (helper shape)
- Acceptance:
  - RED: new test fails against unedited SKILL.md (control passes).
  - GREEN: new test + all existing finishing pin files pass; word count
    ≤4500 by len(text.split()) (3923 + ~120).
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State 3

## Task 4 — charter §Verbs section

- Description: Add a short `## Verbs` section to
  docs/loom/backlog/README.md (after the status vocabulary section):
  the ready query (`python3 scripts/backlog_index.py --ready` — the
  read surface; COMMITTED-NEXT is the "now" queue, soft cap ≤5,
  file-date order), the close duty (pointer:
  finishing-a-development-branch Step 8 flips statuses at close-out —
  point, don't copy the procedure), the kickoff read (pointer:
  brainstorming Axis 0). Keep ≤15 lines; pointers by skill name +
  stable heading, never section numbers.
- Module: docs/loom/backlog
- Files touched: docs/loom/backlog/README.md
- Context paths:
  - docs/loom/backlog/README.md (existing section layout)
- Acceptance:
  - RED: `grep -q '^## Verbs' docs/loom/backlog/README.md` exits 1
    before the edit (the section does not exist).
  - GREEN: the same grep exits 0;
    `python3 scripts/backlog_index.py --validate` exit 0 (the
    README edit must not break the store's parsing);
    `python3 -m pytest scripts/test_backlog_index.py -q` green.
- Dependencies: none
- Independent: true
- Review-weight: prose
- Brief item covered: Smallest End State 4

## Task 5 — inventory sweep (data-only, conservative)

- Description: Classify all 90 live entries against the shipped record
  (loom-code/CHANGELOG.md 0.49.0-0.58.0, merged PRs #645-#655, current
  repo state). For each entry with CONCRETE evidence its subject
  shipped or was superseded: flip frontmatter `status:` to `SHIPPED`
  or `CLOSED — SUPERSEDED`, and append one body line
  `Swept 2026-08-06: <evidence — version/PR/path>` (also update the
  body's Origin/Start bullet ONLY if the charter's field-agreement
  rule requires it — run --validate to find out). No concrete evidence
  → untouched. Stale COMMITTED-NEXT entries re-judged the same way
  (the review-scope-remedy entry is a known SHIPPED case — 0.51.0/PR
  #648). Then regenerate the index
  (`python3 scripts/backlog_index.py --write`) and run `--validate`
  (must exit 0). Execution shape: dispatch 2-3 classifier subagents
  over entry partitions returning evidence-cited verdicts; the
  implementer applies only verdicts whose evidence it verifies
  (version heading exists in CHANGELOG / PR number in git log).
- Module: docs/loom/backlog
- Files touched: docs/loom/backlog/<entry-files>.md (status flips only, subset of the 90 entry files — never README.md), docs/loom/BACKLOG.md
- Context paths:
  - loom-code/CHANGELOG.md, docs/loom/backlog/README.md (charter rules)
- Acceptance:
  - RED: `python3 scripts/backlog_index.py --check` fails after entry
    flips and before index regeneration (drift detected) — the
    deterministic mid-task diagnostic.
  - GREEN: `--write` then `--check` exit 0; `--validate` exit 0; every
    flipped entry carries its evidence line.
- Dependencies: Tasks 1, 2, 3, 4 complete first (T1 provides --ready
  for the task's final verification step; waiting for all of Wave 1
  keeps the wave boundary unambiguous since T4 edits the store's
  README)
- Independent: false
- Brief item covered: Smallest End State 5

## Task 6 — bump 0.59.0

- Description: Both loom-code manifests → 0.59.0; CHANGELOG entry per
  pinned text N4; test_docs_review_blocking_class.py version pin
  rewritten 0.58.0 → 0.59.0 (name, docstring, assertions, messages).
- Module: loom-code (manifests + changelog)
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md ([0.58.0] head)
- Acceptance:
  - RED: rewritten version-pin test fails pre-bump.
  - GREEN: full `python3 -m pytest loom-code/scripts/ scripts/ -q` passes.
- Dependencies: Tasks 1, 2, 3, 4, 5 complete first
- Independent: false
- Review-weight: mechanical
- Brief item covered: Smallest End State 6

## Task 7 — three-leg haiku probes + dogfood report

- Description: Dispatch three haiku cold-read probes per brief item 7
  (by-path prompts against the edited working tree): (a) ready-verb
  output comprehension — given the real `--ready` output, which item
  is the default next-arc candidate and why; (b) finishing close duty
  — a branch that shipped an entry's subject: what must happen before
  the close-out commit; (c) kickoff read moment — a repo WITHOUT
  docs/loom/backlog/: what does Axis 0's backlog check do. Write
  docs/loom/dogfood/2026-08-06-backlog-ready-verb-probe.md
  summarizing each leg with verbatim key quotes and CLEAN/FAIL.
- Module: docs/loom/dogfood
- Files touched: docs/loom/dogfood/2026-08-06-backlog-ready-verb-probe.md
- Context paths:
  - docs/loom/dogfood/2026-08-05-request-derived-authorization-probe.md (report shape)
- Acceptance:
  - RED: a probe leg answering with the OLD behavior (invents a check
    without a store, skips the status flip, or cannot name the next
    candidate from the output) is the failure signal — any FAIL
    blocks close-out until the wording is fixed and the leg re-probed.
  - GREEN: the report exists at the named path with all three legs
    marked CLEAN, each carrying a verbatim supporting quote.
- Dependencies: Task 6 completes first
- Independent: false
- Review-weight: prose
- Brief item covered: Smallest End State 7

## Notes

Kickoff decisions: no one-way doors — all additive; status flips are
reversible edits with evidence lines; below-threshold decisions log
here. Counting convention: `len(text.split())`.

**Pinned canonical texts — transcribe VERBATIM**:

N1 — brainstorming Axis 0 backlog-read block:

```markdown
**Backlog ready check** — when the target repo has
`docs/loom/backlog/`, run `python3 scripts/backlog_index.py --ready`
before settling the arc's scope, and surface to the user any
COMMITTED-NEXT items plus OPEN items related to the seed idea (no
store → skip silently, N/A). The queue informs the arc decision — it
never hijacks it: the user's seed idea stays the default subject.
```

N2 — finishing Step 8 backlog-close bullet:

```markdown
   - Backlog-close check (orchestrator-only, ONCE per branch, same
     shape as its Step 8 siblings): when the repo has
     `docs/loom/backlog/`, check whether THIS branch ships or
     supersedes any backlog entry — grep the store for the branch's
     topic terms and read the hits. On a hit: flip that entry's
     `status:` to SHIPPED (or CLOSED — SUPERSEDED), append one body
     line naming the evidence (this branch/PR), regenerate the index
     with `python3 scripts/backlog_index.py --write`, and stage both
     in the same close-out commit. No hit, or no store → skip
     silently (auditable from the diff, like the memory-store
     bullet).
```

N3 — Step 13 queue-tail sentence:

```markdown
End the report with one line naming the top of the remaining
COMMITTED-NEXT backlog queue ("backlog next: <name>" — or "backlog
queue empty"), from `python3 scripts/backlog_index.py --ready`; skip
the line when the repo has no backlog store.
```

N4 — CHANGELOG entry:

```markdown
## [0.59.0] — 2026-08-06 — the backlog grows verbs

### Added

- **The backlog becomes readable and closable, not just writable.**
  Measured: 90 entries filed in five weeks, zero ever closed, no flow
  ever read the store. Three verbs close the loop, following the
  industry pattern (ready-query + close-in-the-work-loop):
  `backlog_index.py --ready` prints the COMMITTED-NEXT queue + OPEN
  candidates with their start conditions; brainstorming Axis 0 runs
  the ready check at arc kickoff (N/A-silent without a store);
  finishing Step 8 flips shipped/superseded entries in the close-out
  commit and Step 13 ends its report naming the queue's top. The
  inventory was swept once against the 0.49.0-0.58.0 shipped record —
  conservative flips only, each carrying its evidence line.
```

## Decision Log

- 2026-08-06: --ready output format (sections + count line) chosen for
  weak-reader parseability over JSON — the consumer is an agent
  reading prose, not a program; JSON can come later if a tool needs it.
- 2026-08-06: T5 classifier dispatch uses 3 partitions of 30 entries;
  implementer verifies evidence before applying any flip (a classifier
  verdict alone never flips an entry).
- 2026-08-06 (T1 execution): the `start:` second line renders for ANY
  listed entry carrying the field (field-presence rule), not OPEN-only
  — simpler, and COMMITTED-NEXT entries don't realistically carry
  `start:`; implementer-flagged, orchestrator-approved (two-way door).
- 2026-08-06 (whole-branch rounds): round 1 = code NEEDS_REVISION
  (archive-tier leak, coverage) + docs-A NEEDS_REVISION (5🟡) + docs-B
  PASS; fix commit fc3a53dc. Round 2 = code PASS_WITH_NOTES + docs-A
  NEEDS_REVISION (2 new 🟡, fix-round-writes-defects class) → docs
  2-round cap fired, surfaced to user; user authorized round 3
  (「修把」); fix commit fef95801. Round 3 delta = PASS (2🟢 nits
  recorded). Backlog-close check first live run: grep hit 5
  backlog-machinery entries, none shipped by this branch → silent
  skip per the bullet (the duplicate-keys entry's start: condition
  is FIRED by this branch — surfaces via --ready at the next arc).
- 2026-08-06 (round-1 fixes): brief item 7 became Task 7 (the 0.58.0
  precedent the parenthetical cited actually made probes a task —
  corrected; depth 3 → 4); T5 Module reduced to one path, its
  Review-weight dropped (docs/loom/BACKLOG.md is generated → full
  triad), glob scoped to entry files, dependency widened to all of
  Wave 1; T4 gained a deterministic grep RED; N1's placement anchor
  tightened to the `**Negative guard (silent skip)**` paragraph.
