# Brief — plain-relay contract + leak-point fixes (P0+P1)

> Frozen entry artifact for `writing-plans`. Approach locked by user
> 2026-08-15: Option A (independent file), P0+P1 in one PR, P2 deferred.
> Continuous mode: endpoint named ("一個 PR 做掉") → auto-advance to PR;
> never auto-merge.

## Problem

(Axis 1 — the job behind the request)

loom-family skills relay internal vocabulary (stage names, verdict tokens,
schedule words, raw gate strings) to the user verbatim. The user — mid-task,
working memory already taxed — must decode "Stage 1 = brainstorming (Axis 0
will check the upstream artifact…)" or "loom gate: no fresh review-PASS
marker…" before they can know what just happened. Over 2 months this produced
7 explicit "請說白話" pushbacks, all within 6 turns of a loom skill reply
(research note: `research/2026-08-15 loom skill 回應白話化研究…md` §1).

The job: *when I'm mid-task with a loom skill, I want its status updates in
plain words in my conversation language, so I grasp what happened and what I
must decide without first decoding the skill's internal vocabulary.*

This is a **relay-layer** problem only. Machine-facing artifacts (briefs,
verdicts, commits, plan docs) stay machine-precise — the fix touches only the
chat message the agent sends the user.

## Users

(Axis 2)

- **Primary**: kouko — ADHD-friendly reading preference (CLAUDE.md
  plain-language-first contract), mid-task context, Traditional Chinese
  conversation language. Reads loom relay on a terminal / IDE pane.
- **Secondary**: future agent sessions acting for end-users — they inherit
  whatever relay discipline the skills encode; today they inherit jargon
  leaks.
- **Conditions**: working memory taxed by the task itself; scans rather than
  reads; needs the conclusion in the first line or loses the thread.

## Smallest End State

(Axis 3)

The minimum that solves the problem, in one PR:

1. **One plain-relay contract** (`loom-pipeline/hooks/plain-relay.md`):
   7 rules (conclusion-first, translate tokens, hard caps, one-decision-per-ask,
   no raw gate string, outcome-language stages, symbols carry meaning) + a
   token→meaning glossary + one ✅/❌ calibration pair.
2. **One injected trigger card** (≤6 lines, appended to the SessionStart hook
   that already injects the Loom Family Reception) — the imperative short card
   the local A/B proved (2/2 vs 0/2 for descriptive preload). The full contract
   is pull-on-demand; only the card is preloaded.
3. **Six leak-point fixes** (P1): spec-expansion phase markers, git-guard MSG_*,
   brainstorming My-take ordering, finishing N/A noise, verification relay
   pointer, (docs-review options — see Open Questions).
4. **Dedup of brief-before-fork**: 6 full copies + 2 partial → one source, rest
   point. (NOT the three-gate rule — that is already SSOT-pointed; see
   Alternatives.)

NOT in the smallest end state: P2 hook enforcement (jargon-density +
first-line checks) — deferred to a later PR after a new baseline; rewriting
any machine artifact; touching the three-gate SSOT design.

## Current State Evidence

(Verified against the repo 2026-08-15 by two read-only agents + targeted
greps. `file:line` cited. One P1 touch point still open — see Open Questions.)

### Forward (what the relay path does today)

- Good rule exists but coverage has holes + vocab leaks:
  - `loom-code/skills/requesting-code-review/references/relay-phrasing.md:27`
    (rule 2 translate jargon), `:29` (rule 4 state-anchor first line),
    `:37-43` (✅/❌ pair) — the good rule, scoped to ONE skill's review report.
  - `loom-code/skills/verification-before-completion/SKILL.md` — **no relay
    rule at all** (confirmed: no "relay"/"phrasing"/"plain language" anywhere).
    The "done" moment — when the user most needs one plain line — has zero
    phrasing discipline.
  - `loom-spec/skills/spec-expansion/SKILL.md:150,201,237,296,330` — forces
    printing 5 English phase markers (`— Phase ① USM backbone —` etc.) into
    output, no conversation-language requirement. Internal inconsistency:
    section heading `:235` is Japanese ("自動拓展矩陣") but the marker `:237`
    is English.
  - `loom-code/skills/brainstorming/references/axis4-research-protocol.md:88-108`
    — template lists 3 alternatives with evidence, THEN "My take" last
    (`:104-108`); `SKILL.md:150` confirms "end in an explicit recommendation".
    Conclusion-after-evidence, not conclusion-first.
  - `loom-code/hooks/git-guard.py:114-129` — MSG_NO_VERIFY / MSG_REVIEW /
    MSG_VERIFIED are **model-facing stderr** (per `:97`), jargon-dense ("loom
    gate", "PASS / PASS_WITH_NOTES", "review-PASS marker"), but DO embed
    plain action directives ("Drop the flag and let the hooks run"). No
    dedicated user-facing plain layer → agents paste the raw string (research
    §1.3 case 3).
  - `loom-code/skills/finishing-a-development-branch/SKILL.md:187-194` —
    close-out checks table; rows Memory-store `:192`, Archive-on-close `:190`,
    Backlog-close `:193`, Open-questions `:194` each emit an "N/A — checker not
    present" line when inapplicable, stacking up to ~4-5 noise lines before the
    plain conclusion.

### Reverse (SSOT ownership — read the sync script, not inferred)

- `loom-code/scripts/distribute.py` (head, docstring) syncs ONLY
  `domain-teams/skills/code-team/{standards,rubrics,checklists}/` →
  `loom-code/skills/<skill>/{standards,rubrics,checklists}/`. It does **not**
  touch `hooks/` or any relay doc. Therefore `plain-relay.md` is a single-source
  plugin-root resource with **no functional copy** — unlike the knowledge
  layer, it needs no distribute/verify-drift sync.
- Three-gate "how to ask the user" rule: SSOT is
  `loom-code/skills/subagent-driven-development/SKILL.md:25-51`; `ask-triage.py:11`
  docstring names SDD as source; `brainstorming/SKILL.md:50-56` references it.
  **Already point-don't-copy** — NOT a dedup target (corrects the research's
  root-cause ①).
- brief-before-fork template: **6 full copies** (using-loom-discovery `:63`,
  using-loom-interface-design `:41`, using-loom-product-principles `:43`,
  using-loom-spec `:19`, brainstorming `:58`, SDD `:40`) + 2 partial
  (using-loom-pipeline `:158`, relay-phrasing `:20`). No single source — the
  real dedup target.

### Error (failure modes at the touch points)

- `loom-pipeline/hooks/language-stop-check.py:12-19` — the only hook that
  inspects the final reply. Uses an **absolute CJK-char count, NOT a ratio**
  (docstring `:14` "Why an absolute count, not a ratio"), deliberately to avoid
  false-positives on technical replies dense with English identifiers. It
  checks script density, **not jargon or plainness** — so a jargon-dense
  Chinese reply passes. (Corrects the research's §2.3 "ratio" description.)
- No hook checks jargon density, sentence length, or first-line-conclusion.

### Data (what the research measured; reproducibility caveat)

- Research scanned 828 sessions (92 loom, 11.1%) across
  `~/.claude/projects` + `~/.claude-ichef/projects`; 7 pushbacks all within 6
  turns of a loom reply. jargon density: loom-reply n=108 → 1.56; non-loom
  n=20 → 0 (self-admitted thin sample).
- **Caveat carried into this brief**: scan scripts live in a scratchpad temp
  dir, not committed → the acceptance "rerun the scan" (research §5) is
  asserted-reproducible, not ensured. Committing the scan script is out of
  scope here but flagged for the close-out.

### Boundary (what this change does NOT touch)

- Machine-facing artifacts: briefs, verdicts, commit messages, plan docs —
  stay machine-precise (existing repo boundary; CLAUDE.md
  response-style scope rule).
- The three-gate SSOT design (SDD → ask-triage/brainstorming) — already
  point-don't-copy, left untouched.
- `language-stop-check.py` existing absolute-count language check — kept as
  is; P2 (deferred) adds checks alongside, does not rewrite it.
- `distribute.py` / knowledge-layer sync — plain-relay is outside its scope.

## Alternatives Considered

(Axis 4 — research-grounded; industry sources in research note §3)

- **A. Independent file `loom-pipeline/hooks/plain-relay.md`** (CHOSEN) —
  plugin-root resource, same class as family-relay.md; compliant by exemption
  (Anthropic skill-structure rules govern `skills/<name>/`, not plugin-root
  `hooks/`); matches the established cross-plugin reference convention
  (`loom-pipeline/hooks/<file>.md §section`, already used by
  using-loom-product-principles `:19`, using-loom-spec `:25`). Clean
  separation of "relay mechanics" (family-relay) vs "plain-language contract"
  (plain-relay). The "fewer instructions = better compliance" argument does
  NOT favor the alternative, because plain-relay is pull-on-demand (0
  preloaded instruction burden either way).
- **B. Section inside family-relay.md** (rejected) — also compliant; saves one
  file but mixes two concerns in one doc and worsens addressability. Rejected
  on separation + addressability.
- **Per-skill relay rules instead of one contract** (rejected) — the research
  established single-contract-pointed-to beats per-skill duplication (the
  three-gate rule is already this pattern). A new per-skill sprawl would
  repeat the exact failure mode being fixed.
- **P2 hook enforcement in the same PR** (rejected for this PR) — deferred;
  needs a post-P0/P1 baseline to attribute effect and measure false-positive
  rate. Doing it now violates "one change too many to attribute."

## Decision

Build P0 + P1 as **one PR** on a feature branch:

- P0: new `loom-pipeline/hooks/plain-relay.md` (7 rules + glossary + ✅/❌
  pair); ≤6-line `<PLAIN-RELAY>` trigger card appended to the SessionStart hook
  injection that emits the Loom Family Reception; dedup brief-before-fork (one
  source, 6+2 point); family-relay.md + relay-phrasing.md gain a one-line
  pointer to plain-relay.
- P1 (six leak points): spec-expansion → announce step in conversation
  language, internal marker only in artifact; git-guard MSG_* → prepend a
  user-facing plain line; brainstorming axis4 → recommendation first;
  finishing → collapse N/A noise into one summary line after the conclusion;
  verification-before-completion → one-line pointer to plain-relay;
  requesting-docs-review options → plain labels (this item open — see OQ-1).

What we will NOT build: P2 hook checks; three-gate dedup (already SSOT);
machine-artifact plainification; a committed scan script (flagged, separate).

## What Becomes Obsolete

(Axis 5 — removed in the same PR)

- The 6 full + 2 partial brief-before-fork template copies → replaced by
  pointers to one source. (If not removed: duplicated instruction drift, the
  exact debt this contract exists to prevent.)
- The 5 forced English `— Phase ① … —` chat prints in spec-expansion → replaced
  by outcome-language announcements. Internal markers remain in the artifact.
- The 4-5 stacked "N/A — checker not present" close-out lines → collapsed to
  one summary line.
- The research's stated "淨效果是 skill 總字數下降" (§4.3) → NOT claimed; three-gate
  dedup is already done, so this PR is near-net-additive on字数. The字数 delta
  will be measured at close-out, not asserted.

## Out of Scope

- P2 hook enforcement (jargon-density + first-line checks) — separate PR after
  a baseline.
- Committing the research's scan script — flagged for later, not this PR.
- dev-workflow:git-memory (2 of the 7 pushbacks were dev-workflow, not loom
  family) — separate plugin, separate change (research §4.5 caveat c).
- Three-gate rule dedup — already SSOT; touching it is out of scope.
- Any machine-artifact (brief/verdict/commit/plan) wording change.

## Open Questions

- **OQ-1**: The research's P1 item "requesting-docs-review 3 選項 (delta-scoped /
  reviewed_sha jargon)" could NOT be confirmed as a literal 3-option jargon
  menu — the SKILL.md uses those terms as internal mechanism names
  (`:8,:22,:47,:57,:80`), not as a user-facing 3-option block. **Resolve in the
  plan/recon**: either (a) find the actual user-facing option block and plainify
  its labels, or (b) drop this P1 item as research-overreach. Default if
  unrecoverable: **drop** — do not invent a 3-option menu to fix.

## Design-side on-ramp

- Negative guard fires (refactor of existing skill files, test-covered
  increment) → upstream-artifact walk (product-principles / interface-design /
  spec) skipped silently. Confirmed: no `docs/loom/PRINCIPLES.md`-shaped new
  product work; this is relay-behavior refactor on existing skills.
- Backlog ready check ran (`scripts/backlog_index.py --ready`):
  COMMITTED-NEXT = requirement-identity arc (unrelated); OPEN list has no
  plain-relay item. Seed idea stays the subject — no hijack.
- Recall: `docs/loom/memory/` exists; load-bearing gotcha
  `imperative-trigger-cards-beat-descriptive-preloads.md` (0/2 vs 2/2) already
  incorporated into the trigger-card design via the research note. MEMORY.md
  index in context; no separate recall pass run.

## Endpoint / continuous-mode record

endpoint named: yes ("一個 PR 做掉" = 開 PR) → continuous. Terminal stop =
PR-open; never auto-merge.