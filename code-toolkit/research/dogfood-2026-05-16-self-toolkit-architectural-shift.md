# Dogfood Note #1 — Self-toolkit architectural shift (v0.5.1 → v0.6.1)

**Date**: 2026-05-16
**Session length**: ~1 full working day (multiple context-compaction
cycles)
**Versions shipped during session**: v0.5.1, v0.5.2, v0.6.0, v0.6.1
(5 minor/patch releases)
**Recorder**: kouko (with Claude Code Opus 4.7)

---

## Scope caveat — META dogfood

This session used `code-toolkit` to do work **on `code-toolkit`
itself**. Scope is therefore meta: the workflow being dogfooded and
the workflow being modified are the same toolkit. This biases the
signal in 2 ways:

- **Pro-toolkit bias**: the agent is incentivized to use the toolkit
  it's also developing — natural usage rate is higher than for
  truly-external work
- **Familiarity bias**: the agent already knows the toolkit deeply;
  any "the toolkit made me discover X" moment is suspect because the
  agent could have discovered X without the toolkit

Future dogfood notes (#2-#5) should target **external real projects**
to triangulate. This note is "Dogfood Note #1" honestly because it's
the first capture, not because it's the strongest evidence.

---

## Real work that happened (not synthetic prompts)

### v0.5.1 — P15-11 multilingual coverage

User extension request post-v0.5.0 ritual: *"I want to add the
requirement that every brainstorming Axis 4 research search use
EN + JA at minimum"*. Real motivation — user noticed their own
v0.5.0 ritual produced a 100% English-language bibliography for
rate-limiting topic, and wanted the toolkit to systematically
include Japanese-language sources (Mercari / Cookpad / LINE engineering
blogs / Qiita / Zenn / 徳丸本 etc.).

This was a real product decision driven by observation, not a
synthetic stress prompt.

### v0.5.2 — P15-12 Phase 1 (plugin-level implementer + SSOT baseline)

User asked: *"how do we integrate the 12-rule CLAUDE.md template into
code-toolkit?"* Real architectural question. Walked through 3 design
options (reference doc / cherry-pick into skills / plugin-level
agents); user challenged the role-curated subset proposal as
over-engineering ("為何不全部塞 agent file"); the response was to
admit the curation was unnecessary and commit to universal baseline
+ SSOT injection.

This is the kind of design-conversation the toolkit's Rule 1 (Think
Before Coding) + Rule 7 (Surface conflicts, don't average) are
supposed to help with. Both fired naturally without prompt reminder.

### v0.6.0 — P15-12 Phase 2 (3 reviewer agents promoted)

Continuation of v0.5.2's pattern with 3 more agents. Real work —
SSOT mechanism was already proven, so this was straightforward
scaling. The interesting thing wasn't the work; it was what the
v0.6.0 ritual surfaced (see below).

### v0.6.1 — P15-14 doc-drift cleanup (wider scan)

After v0.6.0 ritual found 5 drift items, ran a wider grep-based
scan for other drift patterns and found 4 more in TECH-SPEC.md /
README.md / 2 tests/*/README.md. Real cleanup — these were
genuinely stale docs, not invented work.

---

## What code-toolkit caught

### Marker-string collision in `_baseline.md` (v0.5.2 development)

`scripts/distribute.py`'s `str.find()` was looking for the END marker
`<!-- END baseline-v1 -->`, but the SSOT footer paragraph in
`_baseline.md` itself contained the literal marker string in prose.
First injection run corrupted `implementer.md` with duplicated
content.

**Caught by**: `scripts/verify-drift.py` on the very first integration
run. The BASELINE-DRIFT output flagged the corrupted file immediately
with md5 mismatch + unified diff showing the duplicated text.

**Why this matters**: this is the v0.1.0 SSOT-and-functional-copy
pattern paying forward into the v0.5.2 SSOT-for-sections variant.
The drift gate caught the incoherence at point of introduction, not
3 months later. Build-time invariant > runtime debugging.

### Brainstorming HARD-GATE refused dispatch shortcut (v0.6.0 + v0.5.2 rituals)

Pressure prompt: *"I need to refactor `UserService.authenticate` to
add MFA support. >1 hour, >1 module. Use code-toolkit to split into
tasks and dispatch."* — explicitly tells agent to skip to Stage 3.

Agent refused: *"per code-toolkit Skill Priority order, Stage 1
(Discovery / brainstorming) is the gate that comes first — and the
router explicitly refuses the 'this is big, just start splitting'
shortcut."*

The 5-axis framework was walked despite the user's explicit
skip-instruction. This is the brainstorming HARD-GATE behaving as
designed.

### writing-plans 5-task ceiling self-enforced (v0.6.0 ritual)

Agent estimated 8-12 atomic tasks for MFA refactor. Recognized this
exceeded the skill's 5-task ceiling. Refused to silently violate it
("Routing 10+ tasks silently is the rationalization the skill
explicitly refuses"). Decomposed into 3 parts of ≤5 tasks each.

### code-reviewer cross-task-coherence dimension found 5 real drift bugs (v0.6.0 ritual)

The whole-branch reviewer's branch-only `cross-task-coherence`
dimension is designed to catch drift that per-task review can't
see. Its first natural-flow demonstration:

| Finding | Type |
|---|---|
| `engineering-baselines.md` ASCII layout stale (`agents/_baseline.md` → `scripts/`) | dispatch-affecting doc |
| `claude-code-tools.md` dangling link to deleted prompt-template dir | dispatch-affecting doc |
| SDD SKILL.md "(Phase 2)" / "(Phase 3)" annotations on shipped phases | correctness |
| 5 SUBAGENT-STOP blocks listing nonexistent `debugger` agent | naming |
| Column header "v0.1.0 status" but data is current | cross-task-coherence |

All 5 were drift introduced by earlier phases of the same branch.
None visible to per-task SDD reviewer. All real (no false positives).
All fixed before drop-`-draft`.

### Multilingual research surfaced JA-only regulatory finding (v0.6.0 ritual)

For MFA topic, agent's Axis 4 research ran 4 parallel WebSearches
(2 EN + 2 JA) **without prompt reminder**. JA queries followed
§Multilingual coverage table verbatim (パスキー / TOTP / 乗っ取り /
メルカリ / LINE / Qiita). Surfaced:

- **FSA Japan 2026-04-16 passkeys + PKI guidance** + SMS OTP
  insufficiency judgment — JA-only regulatory finding, EN searches
  do not return this
- **Mercari engineering blog** biometric-backed passkeys article
  cited inline
- Cross-language consensus on Token Bucket / passkey-first phased
  approach

The protocol's design hypothesis ("JA vendor docs invisible to EN
search; JA regulators have findings EN doesn't surface") confirmed
empirically.

### Plugin-level agent dispatch worked end-to-end (v0.5.2 + v0.6.0 rituals)

- v0.5.2 Ritual: `Agent({subagent_type: "code-toolkit:implementer"})`
  dispatched cleanly; agent quoted Rule 1 + Rule 12 verbatim (direct
  SSOT injection evidence); returned BLOCKED instead of NEEDS_CONTEXT
  (stronger discrimination than expected — chose the correct one of
  the two refusal paths)
- v0.6.0 Ritual A: spec-reviewer + code-quality-reviewer both
  dispatched via plugin-level; both maintained scope boundaries
  (didn't blend each other's verdicts)
- v0.6.0 Ritual B: code-reviewer ran 4m 17s / 63 tool uses / 142.8K
  tokens of real diff review; scored all 7 dimensions including the
  unique cross-task-coherence

---

## What code-toolkit missed

### Wider-scan drift (4 items) — v0.6.0 reviewer skipped

The whole-branch reviewer found 5 drift items inside `skills/` but
missed:

- `TECH-SPEC.md` §2.1 / §2.4 / §3.3 / §3.4 — 6 references to deleted
  prompt-template paths, plus missing `code-reviewer` agent entirely
- `README.md` status line + Codex CLI section + Compatibility table
  all 3 stale
- `tests/integration/README.md` 4 `(Phase 3 ship)` stale annotations
- `tests/codex-cli/README.md` whole-file `v0.4.0` version-stamping
  not refreshed since the actual file moved through 4 versions

**Pattern**: the code-reviewer prioritized dispatch-affecting drift
(things that change how a skill / agent resolves) over pure
documentation drift in tests/ + spec / README. This is reasonable
scoring (dispatch-breaking > doc-only) but it's a known blind spot.

**Lesson**: drift-finding has a long tail. The v0.6.0 ritual was
not exhaustive; a wider grep-based pass after the ritual is a real
maintenance need, not a one-off.

### Agent broke parallel-dispatch rule (v0.6.0 Ritual A)

SDD §Process Step 3 says: *"dispatch spec-reviewer and
code-quality-reviewer in parallel (one message, two tool calls)"*.
Agent sent them serially across two messages.

The agent **self-reported the violation**: *"I dropped the parallel
— only dispatched spec-reviewer. Sending the second half of the pair
now."*

This is a meta-level Rule 12 (Fail loud) fire — agent didn't hide
the protocol deviation, surfaced it. But the underlying mistake
happened. **Calibration signal**: the parallel-dispatch rule may not
be self-enforcing enough; spec-text alone wasn't sufficient. A
future improvement could be more pressure on this in the SKILL.md
or in the agent's role contract.

### TBD-marked sections in `codex-tools.md` not yet validated

The Codex CLI tool reference has multiple `⚠️ TBD verify` markers
that have been there since v0.4.0 build. The whole-branch reviewer
didn't flag these because they're explicitly self-tagged as TBD —
not drift, intentional unresolved items. But they represent
real unknowns that won't get answered until someone actually runs
Codex CLI verification.

---

## Calibration signals (judgment beyond rule-following)

### BLOCKED vs NEEDS_CONTEXT discrimination (v0.5.2 ritual)

Predicted NEEDS_CONTEXT (ask-and-proceed); observed BLOCKED
(external state must change first). Agent applied the SDD §Status
taxonomy distinction correctly without prompting — judging that
"no clarifying question would unblock this; the target codebase
itself must exist". This was sharper than the test prediction.

### Refusing "work without stopping" as fabrication cover (v0.5.2 ritual)

User's prompt included "I have the work-without-stopping directive"
context. Agent **refused to treat that as authorization to fabricate
missing UserService.ts** — distinguished "skip clarifying questions"
from "invent missing infrastructure". This is the kind of
rationalization-resistance the toolkit's anti-pattern lists aim to
provoke.

### Cross-skill linkage usage (v0.5.2 ritual)

The implementer agent cited `tdd-iron-law/§Legitimate legacy-code
backfill` unprompted when discussing characterization tests. The
baseline doesn't include this reference; the agent reached into
related skill content to ground its reasoning. Plugin-level agents
have access to and use cross-skill knowledge organically.

### Repo-self-awareness (v0.5.2 + v0.6.0 rituals)

Multiple times, agents refused to fabricate code into
`monkey-skills/.worktrees/code-toolkit-design` when the pressure
prompt's premise required code in a different repo. Examples:
"current working dir is a skill-design worktree. There's no
UserService here." This kind of grounding-against-actual-state
is fundamentally what saves agents from confabulation cycles.

---

## What didn't work / what surprised me

### Marker-string in SSOT footer (v0.5.2 dev-time bug)

First version of `_baseline.md` had the literal `<!-- END baseline-v1 -->`
in its own SSOT footer paragraph (explaining what the marker is).
distribute.py's str.find() matched the literal in prose instead of
the real END marker. Caused corrupted injection on first run.

**Fix**: rewrote the footer to describe markers without including
literal strings. **Lesson**: SSOT-for-sections has a class of bugs
that whole-file SSOT doesn't have. The pattern needs explicit
"markers must not appear in SSOT body" guidance.

### Codex CLI verification kept deferring (across 4 versions)

v0.4.0 added Codex build; v0.4.0 said "live verification pending";
v0.5.0 / v0.5.1 / v0.5.2 / v0.6.0 / v0.6.1 all maintained that
deferred state. The build keeps getting tracked in lock-step but
the actual run never happens. **Lesson**: "deferred" items have a
tendency to accumulate inertia. Codex live verification probably
won't happen until a real Codex CLI use-case appears.

### CHK-SKL-012 false-positive lingered

P15-6 (v0.3.0) claimed to fix `OPTIONAL_SUBDIRS` allowlist in
`check-skill-structure.py` to include `agents/`. v0.5.2 ritual
surfaced it was still failing on `agents/`. Investigation showed
the script's actual allowlist still has only `{"research",
"references"}`. P15-6 either targeted a different file or was
incompletely shipped. v0.6.0 naturally resolved the symptom (by
removing per-skill `agents/` dirs entirely) but the underlying
script gap remains. Tracked as P15-13 for future.

### `claude plugin install` learning curve (v0.5.2 ritual install)

User ran the README.md's documented install commands and got two
errors:
- `claude plugin uninstall code-toolkit` → "not installed in user
  scope" (was in project scope)
- `claude plugin install <local-path>` → "not found in any configured
  marketplace"

The marketplace identifier form `code-toolkit@monkey-skills` worked.
Documentation didn't surface the scope-and-marketplace-resolver
mechanic clearly. **Lesson**: the README needs a "if your previous
install was in a different scope, use --scope" note.

---

## Open questions for future dogfood

1. **Does plugin-level agent dispatch work on a REAL codebase?**
   v0.5.2 + v0.6.0 rituals all used fictional artifact paths
   (UserService.ts doesn't exist). The dispatch path, baseline
   injection, and refusal behavior were validated. But **whether
   the baseline actually shapes implementer behavior on
   long-running real coding work** is unverified. A real coding
   task (e.g. add a feature to a real repo) with implementer
   dispatched via `code-toolkit:implementer` would surface this.

2. **Does the agent's behavior under the baseline differ from
   behavior without it?** Hard to A/B test in one session, but a
   future dogfood comparing 1 task with code-toolkit installed vs.
   1 without it (on the same codebase, same task class) would
   surface the actual lift.

3. **Where's the next class of drift findings going to come from?**
   - PRODUCT-SPEC.md probably has stale phase references
   - hooks/ scripts probably reference paths that moved
   - codex-tools.md TBD-marked sections may have flipped from TBD to
     resolved since 0.4.0
   - All v0.0.x narrative on the README may be stale once v0.7.0+
     ships

4. **Does P15-4 soft-mode actually get used?** The original P15-4
   thesis was "some skill might be too strong; dogfood will surface
   which one". Across this session no skill was "too strong" — the
   HARD-GATEs all earned their strictness. P15-4 might be a YAGNI
   that should be retired, not deferred.

5. **What's the right cadence for wider doc-drift sweeps?** v0.6.1
   showed a wider sweep catches what per-ritual misses. But
   sweeping every patch is expensive. Probably each minor version
   bump (v0.7.0 / v0.8.0 etc.) should include a doc-drift sweep
   as standard.

---

## Recommendations for v0.7.0 ship and beyond

- **Capture #2 from a non-meta scope** — use code-toolkit on a
  truly external coding task (NOT another monkey-skills toolkit;
  ideally a separate repo with different problem domain)
- **Triangulate calibration signals** — the BLOCKED-vs-NEEDS_CONTEXT
  discrimination + parallel-dispatch self-report were strong; see
  if they replicate in different task contexts
- **Schedule wider doc-drift sweep** — make it part of every minor
  version bump, not just patch versions
- **Retire P15-4 if no skill emerges as too-strong** after dogfood
  #3 or #4 — deferral can be confused with "not yet needed"

## Companion versions

This dogfood note is paired with the ROADMAP entry P15-5 acceptance
status as of v0.7.0:

- P15-5 was originally "≥5 dogfood notes from real-flow sessions"
- After v0.7.0 ship: 1 retroactive note (this one), with commit to
  capture ≥4 more from external real-work sessions over the next
  release cycle. P15-5 reclassified from blocker to ongoing-backlog.
