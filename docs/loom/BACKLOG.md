# loom family backlog

> SSOT for cross-plugin open items. Convention: one entry per item with
> **start/re-trigger condition**, **origin** (PR / ledger / discussion),
> and **status** (`COMMITTED-NEXT` | `OPEN` | `PARKED` | `UPSTREAM`).
> Plugin-local parks stay in each plugin's README (§parked items with
> re-triggers); this file holds items that cross plugin boundaries or
> have no plugin home yet. Claude-side session memory keeps only a
> pointer here — this file is the durable truth (versioned, host-agnostic,
> greppable). Completed items are deleted, not archived — git history is
> the archive.

## Designer/PM loop — implementation after paper dogfood ✅ (COMMITTED-NEXT)
- Status: COMMITTED-NEXT
- Start: next loom design/build session.
- Origin: 2026-07-10 discussion session, user decision ledger §6 of
  `docs/loom/design/2026-07-10-designer-pm-loop-architecture.md`;
  canon lists in `docs/loom/research/2026-07-10-principles-canon-base-lists.md`.
  Paper dogfood COMPLETED same day — run + graded report + produced artifact
  in `docs/loom/dogfood/2026-07-10-designer-pm-loop-paper/` (verdict:
  instrument works; 4 PASS + 1 PARTIAL).
- What remains:
  1. **Cluster B (loom-code pipeline-hardening trio) DONE** on branch
     `feat-loom-code-upstream-hardening` (Tasks 8-14): writing-plans
     layered change-folder detection cascade, `check_scenario_coverage.py`
     + writing-plans wiring, `archive_change_folder.py` +
     finishing-a-development-branch archive-on-close step,
     code-reviewer principles-existence self-derivation, AGENTS.md
     command-surface declarations, loom-code version bump + CHANGELOG.
     See docs/loom/plans/2026-07-10-designer-pm-loop-implementation.md
     Tasks 8-14 for per-task detail.
  2. **Cluster A (loom-product-principles construction flow) still
     pending** — Tasks 1-7 of the same plan: canon base list reference
     files, question-sets reference, principles-rules.md Anchors +
     Deviation Ledger format, validator enforce-when-present checks,
     the SKILL.md construction-flow rewrite (incl. §Headless / seeded
     mode), and its own version bump + CHANGELOG. Runs on a separate
     branch/PR per the plan's Decision (Clusters are mutually
     independent; disjoint plugins).
  3. **Cold-operator dogfood (Task 6) still pending** — Cluster A's ship
     gate: a fresh-context operator (not the instrument/skill author,
     ideally weaker model) runs the shipped construction-flow skill on
     one real product idea end-to-end, graded against the paper-dogfood
     instrument's five success criteria; any criterion failing spawns
     fix tasks before Cluster A's version bump (Task 7).
  4. Instrument v0.1 is already applied
     (`instrument-v0.1.md` in the dogfood folder — Q8 lifecycle/scale,
     Q4 "replaces X" annotation, cross-section propagation, artifact
     landing spot, FINDING-08 pattern). Cluster A's SKILL.md rewrite
     consumes v0.1, not v0.

## Designer/PM loop — escalation interface, decision log, acceptance-surface contracts (OPEN)
- Status: OPEN
- Start: next designer/PM-loop session after Cluster A ships.
- Origin: `docs/loom/design/2026-07-10-designer-pm-loop-architecture.md`
  §1-§2 (Four load-bearing inversions #2-#4; Engineering-decision
  escalation rubric) + this branch's (`feat-loom-code-upstream-
  hardening`) close — Cluster B shipped only the pipeline-hardening
  trio (must-consume detection cascade, coverage script/gate,
  archive-on-close, reviewer self-derivation); the architecture doc's
  remaining KEEPs are behavioral contracts, not yet built into any
  station skill.
- What: the escalation interface / decision-log / acceptance-surface
  behavioral contracts —
  1. **Escalation interface**: the two-axis routing test (product
     consequence × reversal cost, §2) wired as the actual decision
     point for "ask the user vs agent decides"; the **kickoff briefing**
     mechanism batching a plan's one-way-door engineering decisions into
     one product-stakes briefing at the spec→plan transition (each
     option: plain-language stakes → 2-3 choices with product
     consequences → recommendation; derivation-for-confirmation framing
     when principles already lock the choice); mid-implementation
     escalation as the exception path of the SAME interface, not a
     second protocol.
  2. **Decision log**: a product-language record for every
     agent-decided engineering choice ("chose X because Y; the day you
     want Z, this choice costs W") — the auditable, late-vetoable
     safety net that makes silent agent-decisions cheap while
     escalation stays expensive.
  3. **Acceptance-surface promotion**: ui-verification promoted from
     side gate to the user's main acceptance stage (the only
     product-perceivable surface a non-engineer user can judge "done"
     by: running app, ui-verification results, product-language
     completion reports); NEEDS_REVISION review loops digest silently
     rather than surfacing to the user.
  4. **Per-project escalation appetite**: a declaration living in
     PRINCIPLES.md's Engineering Principles section, read once and
     never re-asked (judgment-rubrics §3(c)) — needs a home in
     whichever station skill consumes PRINCIPLES.md engineering
     content.

## Operationalize "product-shaped" in family reception (OPEN)
- Status: OPEN
- Start: next time any session or dogfood cold-reader again reports
  guessing at whether work is "product-shaped" vs "an increment" (one
  more occurrence past the 2026-07-10 loom-discovery dogfood, per the
  two-occurrence rule).
- Origin: loom-discovery dogfood
  (`docs/skill-dogfood/2026-07-10-loom-discovery/report.md` FINDING-010)
  — three independent cold-readers flagged "product-shaped" as never
  operationalized; it gates on-ramp rows 1 AND 4, so the ambiguity is
  family-wide, not loom-discovery's.
- What: add a one-line decidable test (or 2 worked examples) to
  `loom-pipeline/hooks/family-reception.md` — mind the 60 non-empty-line
  budget enforced by `test_pipeline_reception.py`; may need to land in
  the entry skills' §Intake instead.

## Grounding notes for sibling stations' claude-code-tools.md (OPEN)
- Status: OPEN
- Start: next touch of loom-spec or loom-interface-design references/.
- Origin: loom-discovery SDD Task 3 code-quality review (2026-07-10) —
  loom-discovery's claude-code-tools.md now carries a verified-against-
  frontmatter grounding note; loom-spec's and loom-interface-design's
  equivalents lack one (same gap, inherited convention).
- What: add the same one-paragraph grounding note (verification date +
  evidence grain) to each sibling's references/claude-code-tools.md.

## On-ramp row 4 vs rows 2/3 precedence unstated (OPEN)
- Status: OPEN
- Start: a real session where discovery and interface-design/spec
  on-ramp rows fire together and the session visibly picks wrong (the
  row-4-vs-row-1 case is already resolved in the reception file).
- Origin: loom-discovery dogfood FINDING-007 + router cold-reader
  (2026-07-10); Probe A q9 live-confirmed the adjacent row-4-vs-row-1
  seam splits 50/50 at description level.
- What: one precedence sentence covering row 4 vs rows 2/3 — but the
  reception file sits exactly at its 60-line budget, so this likely
  lands in `using-loom-discovery` §Intake as a tie-break note instead.

## Automate research-toolkit's sync-primitives.sh (PARKED)
- Status: PARKED
- Start: a second real drift incident (a synced primitive shipped out of
  sync with its SSOT and reached `main` before CI's MD5 drift gate
  caught it — not just failed a PR check, actually merged wrong). One
  incident (PR #519) was caught by the existing CI gate before merge,
  which is the gate working as designed, not a failure of it.
- Origin: raised during review of
  `docs/loom/specs/2026-07-08-deep-deep-research-fact-opinion-classification.md`
  (2026-07-08) — an external critique suggested moving
  `research-toolkit/scripts/sync-primitives.sh` from a manual step
  (backstopped only by a CI-side MD5 drift gate) to a git pre-commit
  hook or build-pipeline dependency, for local "fail loud" instead of
  async CI-only catch. Valid idea, evaluated and deliberately deferred
  from that brief because it targets the *pre-existing, repo-wide*
  SSOT-sync convention shared by every synced primitive in
  `research-toolkit` (not something that brief's `claimType` change
  introduced) — out of scope for a single-feature brief.
- What: if triggered, add a local pre-commit hook (or equivalent) that
  detects an edit to a declared SSOT primitive
  (`research-toolkit/skills/deep-deep-research/scripts/{schemas,rank,prompts,dedup}.py`)
  and either auto-runs `sync-primitives.sh` for the known sibling skills
  or blocks the commit until it's run manually. Keep the existing CI MD5
  gate regardless — this is a local speed-up, not a replacement for the
  CI backstop.

## Mechanical reminder hook for docs/loom/memory-worthy trailers (PARKED)
- Status: PARKED
- Start: the "trailers written but docs/loom/memory not checked" lapse
  (documented only in this session's private machine-local auto-memory
  as `feedback_fold_repo_memory_writes_into_same_branch_pr.md` — not yet
  promoted to a repo-committed `docs/loom/memory/` entry) recurs a THIRD
  time even after PR #521's fix (the
  finishing-a-development-branch Step 6/Step 8 re-sequencing). Two
  occurrences (PR #519, PR #520) already triggered the process fix in
  #521; a third occurrence AFTER that fix is the signal this needs
  mechanical backup, not just better sequencing.
- Origin: PR #521 review discussion (2026-07-08) — an external critique
  suggested a `PostToolUse` hook enforcing this "100% declaratively";
  evaluated and deliberately deferred, not built, because (a) PR #521's
  process fix hasn't had a single real-world data point yet, (b) "is
  this content memory-worthy" is a semantic judgment a hook can't
  reliably make — at best a heuristic reminder (git-memory returned a
  non-empty trailer set AND no docs/loom/memory/ file touched in this
  commit → warn), which risks false-positive noise on the many routine
  commits that correctly have local-only trailers.
- What: if triggered, build a lightweight `PostToolUse` hook on `git
  commit` that fires the heuristic above as a non-blocking reminder
  (never a hard block — the judgment call stays with the agent/user).
  Do not attempt to make the memory-worthiness decision itself
  mechanical.

## Mechanical-gates v2 candidates (loom-code 0.23.0 follow-ups)
- Status: OPEN
- Start: first fatigue evidence from daily use of the push gate, or next
  git-guard touch — whichever comes first
- Origin: PR #492 final verdict (2 🟢 next-touch) + its Decision trailers
- What: (a) waiver `scope` field checked on the read side (single-scope
  today); (b) git-guard docstring limitations list gains the
  `git -c core.hooksPath` route; (c) **patch-id relaxation** of the
  strict-HEAD-sha review marker — today ANY post-verdict commit forces
  re-review or waiver, which is correct for content changes but costly
  for message-only amends; relax to diff patch-id match if re-review-on-
  amend proves too expensive. First candidate friction datum
  (2026-07-04): docs-only microbranches face the same full
  review-or-waiver cost as code branches.

## TDD Guard pilot + TDD-mining tightenings
- Status: OPEN
- Start: first real SDD venue — same trigger as G4 / Segment-3
  (komado-Viewfinder batch6)
- Origin: harness-engineering audit rec 4
  (docs/loom/audits/2026-07-04-harness-engineering-audit.md) + the
  2026-07-04 three-route TDD-miss mining
- What: mount nizos/tdd-guard (or a loom-built equivalent: hook
  guarantees the check fires, LLM judges) on one real SDD run; measure
  latency / spend / false-block rate → adopt-vs-build decision. Bundle
  the two mining-derived tightenings into the same touch: reviewer
  tests-dimension must flag a zero-new-test feature branch on
  non-carve-out code (miss 3: whole-branch PASS never flagged it), and
  tdd-iron-law carve-outs must be DECLARED before coding, not claimed
  post-hoc (miss 2: "legacy backfill" framing for code shipped untested
  under the workflow's own banner).

## validate_design_output.py dual-root mode
- Status: UPSTREAM (loom-interface-design)
- Start: next loom-interface-design touch
- Origin: live-verify finding 4 (report
  docs/loom/dogfood/2026-07-04-loom-pipeline-v1-live-verify.md); the
  validator assumes DESIGN.md + ui-flows.md are colocated, but the
  sanctioned layout (audit #472) splits product-level vs per-change —
  exit 1 is structurally guaranteed. Needs --design-root/--flows-root
  (or equivalent) arguments.

## Segment-3 first live run
- Status: OPEN
- Start: first real change (deliberately NOT burned on a toy — agreed
  2026-07-04; dispatch machinery already proven by the F5 spike and the
  2026-07-03 dogfood)
- What: SDD triads via agentType + whole-branch review + conditional
  ui-verification, driven by the merged driver against a real repo.

## duration-override test affordance → interaction-flows enumeration
- Status: OPEN (original 值得做 list item 4)
- Origin: ui-verification first live run (PR #477 dogfood note) — 4
  states untestable behind a 25-minute wait; pipeline-produced apps
  should be required at design time to expose a test affordance.
  Candidate enumeration item for loom-interface-design:interaction-flows.

## Goal-oriented firing-corpus `expected` narrower than design
- Status: OPEN
- Start: next reuse of docs/loom/firing-corpus/goal-oriented.jsonl, or
  next firing-harness touch
- Origin: PR #489 residual; transcript-check requirement documented as
  trap #6 in the loom-code/scripts/loom_firing_harness.py module
  docstring
- What: every goal-oriented record expects `loom-code:using-loom-code`,
  so fired-skill grading alone cannot catch a design-side on-ramp
  regression (deleting brainstorming's Axis 0 would not move a single
  record off EXACT/FAMILY). The corpus's real acceptance criterion —
  whether the design-side recommendation SURFACES in the transcript —
  is not automated; any reuse must run the F3-style transcript check,
  or the corpus needs `expected` widened to the design-sanctioned set.

## Sibling plugin SKILL.md frontmatter versions lag plugin.json
- Status: OPEN
- Start: next version bump of any sibling plugin, or next touch of the
  manifest-drift tooling (.claude/hooks/check-codex-manifest-drift.sh)
- Origin: PR #490 loom-interface-design agent flag — drift lives in
  SKILL.md frontmatter, not READMEs, so #490's README pass left it
  unfixed
- What: SKILL.md frontmatter `version:` is stale across all three
  siblings (verified 2026-07-06): loom-interface-design 4× 0.3.0 vs
  plugin.json 0.4.1; loom-product-principles 0.3.0/0.1.0 vs 0.4.0;
  loom-spec 0.2.2/0.2.1/0.1.0 vs 0.4.1. Decide the contract
  (frontmatter tracks plugin version vs deliberate per-skill semver),
  then either sync or add a drift gate next to the codex-manifest one.
  New instance: loom-pipeline shipped loom-memory SKILL.md frontmatter
  `version: 0.1.0` while plugin.json moved to 0.5.0 (2026-07-06,
  followed sibling practice deliberately) — the undecided contract now
  covers loom-pipeline too.

## .claude/hooks ↔ .codex/hooks mirror has no drift gate
- Status: OPEN
- Start: third mirrored hook-script pair, or next touch of
  check-codex-manifest-drift.sh — whichever comes first
- Origin: PR (this branch) Tasks 6+7 quality review, 2026-07-06 —
  remind-memory-mirror.sh became the SECOND byte-identical
  .claude/.codex hook pair (first: validate-skill-folder-structure.sh,
  since 2026-06-17); nothing enforces identity
  (check-codex-manifest-drift.sh gates only */plugin.json; loom-code CI
  pytests .claude/hooks/ only; CLAUDE.md documents the manifest mirror,
  not the hook-script mirror)
- What: Rule of Three — at the third pair (or next drift-tooling
  touch), add a cmp-based identity test or extend the drift hook to
  cover .claude/hooks/*.sh ↔ .codex/hooks/*.sh.

## #468 reviewer next-touch nits (loom-code TECH-SPEC + CI)
- Status: OPEN
- Start: next loom-code/TECH-SPEC.md touch
- Origin: PR #468 whole-branch reviewer 🟢 next-touch nits (2026-07-02)
- What: freshness-checked 2026-07-06 — (a) dimension-count drift STILL
  PRESENT: TECH-SPEC.md:420 `dimension_scores` lists 6 keys and :261
  says "7-dimension scores" for code-reviewer, whose actual contract is
  10 dimensions (agents/code-reviewer.md description); the same drift
  exists INSIDE agents/code-reviewer.md itself (verified 2026-07-06:
  its line 10 says "7-dimension scores" while its own frontmatter
  description and findings `dimension` enum say 10), so the fix touch
  should sweep the agent file too; (b) dual
  path-presentation styles (mixed backtick/plain paths) STILL PRESENT
  in TECH-SPEC.md; (c) loom CI steps sharing one `run:` block appears
  ALREADY FIXED — all four loom-*-ci.yml workflows now run one command
  per step; confirm and drop sub-item (c) at next touch.

## Living-spec deferred debt bundle
- Status: OPEN
- Start: next living-spec script touch
  (loom-code/scripts/living_spec_*.py or check-living-spec-index.py)
- Origin: living-spec index slices 1–4 + capstone G (#447–#455)
  deferred-debt ledger
- What: (a) regex suffix-vocab lockstep — two regexes must move
  together when the suffix vocabulary changes; (b) drift-lane
  tokenize-ization; (c) Rule-of-Three `_matched_files` extraction;
  (d) Open-Q6 ready-signal binding for BOTH merge-boundary gates
  (verify-index + active-coverage).

## Codex hook events — apply_patch handler emits none (UPSTREAM)
- Status: UPSTREAM (openai/codex#16732, #20204)
- Start: next Codex CLI version bump in this environment — re-run the
  live-fire ritual in docs/loom/codex-verification.md §remind-memory-mirror
  (codex exec writes a type:project note to a memory-pattern path; grep the
  session rollout log for the reminder fingerprint)
- Origin: 2026-07-06 live-fire test on Codex 0.139.0 — apply_patch wrote
  files but the rollout log carried zero hook events; official docs say
  apply_patch matches Edit/Write matchers, so wiring is dormant-correct
- What: BOTH mirrored repo hooks (.codex/hooks/remind-memory-mirror.sh and
  .codex/hooks/validate-skill-folder-structure.sh) are inert on Codex until
  upstream fixes ApplyPatchHandler hook emission. No local fix applies —
  matcher/payload changes cannot help when the handler never emits. On
  upstream fix: verify firing, then also confirm the payload carries
  tool_input.file_path (the script's silent-no-op tolerance would mask a
  key-name mismatch; probe with a catch-all debug hook if needed).

## Anti-copy acceptance greps pass paraphrase copies
- Status: OPEN
- Start: next touch of loom-code writing-plans SKILL.md or the
  plan-document-reviewer prompt
- Origin: 2026-07-06 loom-memory-skill task 1 quality review — the
  plan's anti-copy GREEN criterion grepped for verbatim charter-row
  text; the implementer shipped a complete five-row PARAPHRASE of the
  charter's jurisdiction table that passed the mechanical grep while
  violating its intent; only the quality reviewer's judgment leg
  caught it
- What: anti-copy / SSOT-protection acceptance criteria authored in
  plans need TWO legs — the mechanical verbatim grep AND an explicit
  reviewer-judgment check ("no paraphrase reproduction of the
  protected content"); candidate: one line in writing-plans'
  acceptance-criteria guidance + one check hint in the
  plan-document-reviewer prompt.

## research-toolkit primitive-sync tests cite old deep-research SSOT path
- Status: OPEN
- Start: next research-toolkit scripts/primitives touch, or as a tiny
  surgical PR
- Origin: whole-branch review of research-skill-r2 (2026-07-06,
  docs/loom/dogfood/2026-07-06-research-toolkit-firing-ab.md branch)
- What: per-skill `test_primitives_present.py` files + sync headers still
  cite the SSOT path `research-toolkit/skills/deep-research/scripts/`,
  but the folder is now `deep-deep-research/` (pre-existing residue of
  the earlier rename; functional copies still verify byte-identity, only
  the cited path string is stale). Sweep the path strings, keep
  `scripts/sync-primitives.sh` + check-script-sync.yml semantics intact.
  ALSO sweep member SKILL.md body prose (fact-check ~L12-21, deep-read
  ~L11-18 and siblings) where bare "deep-research" still means the
  sibling deep-deep-research — since the using-research-toolkit router
  now reserves "deep-research" for the host BUILT-IN skill, the bare
  term is newly ambiguous to readers (2026-07-06 review-panel nit).
