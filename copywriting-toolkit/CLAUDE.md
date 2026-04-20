# copywriting-toolkit — Plugin Conventions

## Setup

### Install

The plugin activates via Claude Code's marketplace mechanism — see `/Users/kouko/GitHub/monkey-skills/.claude-plugin/marketplace.json` entry for `copywriting-toolkit`. Once the marketplace is loaded, all 14 skills + 2 agents + 3 protocols (router phase-decision-tree + intake brainstorming + intake express-mode + 8 workflow protocols) resolve automatically.

### Permissions

Skills read files inside their own directory (`standards/`, `protocols/`, `checklists/`, `rubrics/`) and plugin-root shared resources (`agents/`, `CLAUDE.md`, `envelope.schema.json`). No network access required except `WebSearch` for `copywriting-neta-injection` Phase A (source-taxonomy allow-list only — Path A-1 SNS/meme, Path A-2 literary). No file writes outside the plugin directory.

### Model tiers

| Agent | Tier | Rationale |
|---|---|---|
| `copywriter` | sonnet | Drafting / ideation / audit-variant production — high volume, quality-sensitive but not judgement-critical |
| `copywriter-evaluator` | opus | Legal / framework / voice / form gates — low volume, judgement-critical; `FAIL_FATAL` decisions carry legal weight |

If your platform cannot differentiate tiers, default both to opus. Do not default both to sonnet — evaluator's aesthetic-capture anti-pattern is harder to resist at lower tiers.

### Environment variables

None required. Plugin is self-contained — no API keys, no cache paths, no persistent state.

### Persistence

The envelope is in-memory per pipeline run. Nothing is persisted across sessions unless the caller saves the envelope explicitly. `audit_trail[]` (when populated) lives on the envelope, not in plugin storage.

## Provenance & Divergence Principle (supersedes §Copy-First in v1.1.0)

Plugin files fall into two provenance tiers. The original v1.0.x "Copy-First" rule (byte-identical to source, zero modification) was tightened enough in early development but became a drag once copywriting-toolkit's own mechanics (L1/L2/L3 preconditions, Express Mode tier taxonomy, brief+draft scope, conflict_flagged cross-phase consumers, retry-cap mechanics) outgrew the original domain-teams:copywriting-team scope. Continuing the rule caused workaround sprawl (plugin-specific logic in SKILL.md §Evaluator hints, §Execution Paths, §8b extensions) that fragmented cohesive rules across 2+ files. v1.1.0 formalizes a 2-tier policy.

### Tier 1 — BYTE-IDENTICAL (immutable)

Files in this tier MUST match the source verbatim. No divergence allowed. Verify via `diff -q` against `domain-teams/skills/copywriting-team/`.

- `skills/*/standards/*.md` — academic canon: 神田 PASONA / 谷山 discipline / 今泉 曼陀羅 / 川喜田 KJ / Cialdini / Schwartz / Vaughn / Halliday / Fortin / Edwards / 小霜 / Kaushik / 秋山・杉山 AISAS / 飯髙 ULSSAS / McQuarrie & Mick / Lakoff & Johnson / Thornton etc.
- `skills/using-copywriting-toolkit/research/*.md` — grounding notes (historical versioning artifacts)

Rationale: these files carry third-party canon (books, papers, TCC 年鑑 citations). They should never drift per-plugin. A plugin has no authority to edit 神田昌典's PASONA definitions. `diff -q` must return empty.

**Exception** — ZH voice lineage: `skills/copywriting-voice-tone-stage/standards/zh-copy-craft-lineage.md` is **newly authored for this toolkit in v1.0.1** (not cp'd from domain-teams source — the source never had a ZH counterpart to `jp-copy-craft-lineage.md`). It is Tier 1 in the sense of "immutable canon", but has no upstream source to diff against.

### Tier 2 — MAY DIVERGE with explicit documentation

Files in this tier MAY be modified to adopt plugin-specific execution mechanics. Each modified file MUST:

1. Carry a `<!-- DIVERGED FROM -->` header at the top of the file (see template below)
2. Preserve ALL original prose — changes are **additive only**; do NOT delete, re-order, or rewrite original sentences
3. Mark plugin-specific additions clearly with `<!-- v1.x.y addition: <topic> -->` blocks
4. Log every divergence in `CHANGELOG.md` per version bump

Covers:
- `skills/*/protocols/*.md` — execution SOPs; plugin-specific mechanics are legitimate divergence
- `skills/*/checklists/*.md` — gate items; plugin-specific hint subitems OK
- `skills/*/rubrics/*.md` — qualitative flag criteria; plugin-specific dimensions OK

Rationale: execution mechanics legitimately vary between plugins. copywriting-toolkit's L1/L2/L3 precondition / bounce-back / Express Mode / tier taxonomy / cross-phase flag preservation are plugin-specific, and belong in the protocols / checklists / rubrics where evaluators and workers actually read them — not shunted into SKILL.md workarounds that agents have to cross-reference.

### DIVERGED header template

Every modified Tier 2 file carries this block at the top:

```
<!--
DIVERGED FROM domain-teams:copywriting-team
Original source: domain-teams/skills/copywriting-team/<path>
Changes in copywriting-toolkit:
  - v1.1.0: ADDED §<topic>
  - v1.x.y: ...
Original content preserved verbatim below. All divergences are additive;
no deletion or re-order of original prose. Search for "v1.x.y addition"
markers to locate plugin-specific additions.
-->
```

### Enforcement

- **Lint** (future CI): Tier 1 files diff-checked against source; Tier 2 files with content beyond the DIVERGED header checked for the header's presence
- **Review gate**: Tier 2 modifications without a CHANGELOG entry = PR rejection
- **Additive-only discipline**: if an existing sentence needs actual correction (not addition), raise it to `domain-teams:copywriting-team` upstream and keep waiting; do not rewrite in place

### INLINE-duplicate clarification (Tier 1 standards)

"INLINE" means `cp` the same Tier 1 standard into multiple skills' `standards/` directories — NOT prose paste into SKILL.md.

- `persuasion-psychology-anchor.md` → duplicated across 5 Phase-4 workflow skills (identical copies, all Tier 1)
- `sns-evolution-aisas-ulssas.md` → duplicated across long-form-pasona + light-action (both Tier 1)
- `kosimo-instinct-analysis.md` → single copy in ideation (Tier 1)

All remain discrete files — referenced, never pasted. Tier 1 discipline (byte-identical) applies to each copy.

## SKILL.md Budget

Each SKILL.md body ≤6K tokens (skill-team v4.8.1 budget). If grounding exceeds this, reference `standards/` files instead of inlining.

## Handoff Envelope

Between-skill artifact shape (JSON):

```json
{
  "phase": "phase-4-draft",
  "form": "long-form-pasona",
  "brief": { "...": "from intake" },
  "message_thesis": "...",
  "ideation_pool": ["... optional if Phase 2 ran ..."],
  "neta_candidates": ["... optional if Phase 3 ran pre-draft ..."],
  "draft": "...",
  "next_stage": "copywriting-voice-positioning-stage"
}
```

Each stage reads envelope, adds its layer, updates `next_stage`, returns.

### Immutable fields — preservation contract

Certain envelope fields MUST pass through downstream skills unchanged. A skill is free to READ them, but must NOT mutate, omit, or re-type them when emitting its output envelope. These fields travel multiple hops and have multiple consumers; silent drops are how defense-in-depth mechanisms (Phase 5 flag consumed by Phase 8, bounce-back context carried across sessions) fail invisibly.

| Field | Writer | Readers | Mutability |
|---|---|---|---|
| `voice_quadrant` (entire object) | Phase 5 | Phase 6 Pre-pass + Phase 6 Pass 1 + Phase 8 8b | **Immutable** after Phase 5 |
| `voice_quadrant.schwartz_alignment` | Phase 5 | Phase 6 Pre-pass + Phase 8 8b rubric | **Immutable** — consumers rely on the exact enum value (`ok` / `hard_rule_applied` / `conflict_flagged`) |
| `tone_notes.schwartz_conflict_carried` | Phase 6 Pre-pass | Phase 8 8b | **Immutable** after Phase 6 |
| `tone_notes.lineage_gap` | Phase 6 Pass 3 | Phase 8 8b | **Immutable** after Phase 6 |
| `brief.*` Level 1 fields | Phase 0 intake | All downstream | **Immutable** unless user explicitly edits brief in a user-override turn (e.g., Phase 7 NEEDS_REVISION Option 2) |
| `audit_trail[]` | Any skill / router | All skills, user on halt | **Append-only** — no skill may remove or reorder entries |
| `retries.*` counters | Router | Router | **Monotonic** — counters only increment, never reset by a downstream skill (resetting is how stall-loops hide) |
| `express_mode_used` | Phase 0 intake | Phase 7 audit, debugging tools | **Immutable** after intake |
| `violation` (when present) | Router | Target bounce-to skill | Present until bounce-back consumed; target skill clears it only on successful re-intake |

If a skill must transform a field (e.g., edit `draft` at Phase 6), it creates a NEW version alongside — it does not rewrite history. Phase 6 output envelope carries BOTH the Phase 4 `draft` (unchanged) and a new `tone_notes` + polished draft annotation. The router's re-entry invariant check (see `using-copywriting-toolkit/protocols/phase-decision-tree.md §2.4`) verifies immutable fields are still present on every Shape C continuation.

**Enforcement**: router bounces any envelope with a dropped immutable field back to the skill that last wrote it, per §2.4. This is cheap (presence check, not semantic) and makes drops auditable.

## Envelope Violation (bounce-back contract)

Every downstream skill declares its `## Preconditions` schema in its own SKILL.md. The `using-copywriting-toolkit` router validates the envelope against that schema BEFORE launching the skill. On violation, the router does not launch; instead it emits a bounce-back envelope and re-routes upstream.

### Violation envelope shape

```json
{
  "violation": {
    "detected_by": "copywriting-<skill-that-rejected>",
    "detected_at": "ISO8601 timestamp",
    "missing": ["field1", "field2.nested"],
    "malformed": [{ "field": "name", "expected": "enum[a|b|c]", "got": "..." }],
    "bounce_to": "copywriting-<upstream-skill-to-re-enter>",
    "bounce_round": 1,
    "user_message": "Plain-language explanation for the user — what the pipeline cannot proceed without"
  },
  "original_envelope": { "...": "frozen snapshot of the envelope that failed validation — operator / audit inspection only; NOT auto-merged on re-entry" },
  "retries": {
    "bounce_round": 1,
    "revise_round_count": 0,
    "total_retries": 1
  }
}
```

### Bounce rules

1. **Single skill declares, router enforces** — skills do NOT self-dispatch bounce; they return the violation shape and let the router route.
2. **`original_envelope` is a forensic snapshot, not a merge source** — it freezes the envelope the router rejected so the user / operator can inspect what failed. On re-entry the upstream skill (typically `copywriting-intake`) runs FRESH; `original_envelope` is not merged back into the live envelope. This mirrors Express Mode's rule that bounce-backs force Q1-Q10: if Express synthesis was good enough, the violation would not have fired — so the re-entry starts from user words, not stale synthesis.
3. **Round caps** — three independent counters converge into `total_retries`:
   - `bounce_round` — increments on each schema violation
   - `revise_round_count` — increments on each evaluator-verdict auto-revise (Phase 7 FIXABLE, Phase 8 loop-back)
   - `total_retries = bounce_round + revise_round_count` — the aggregate
   Hard caps:
   - `bounce_round >= 3` → HALT (schema-loop stuck)
   - `revise_round_count >= 2` per phase → HALT (evaluator-loop stuck)
   - **`total_retries >= 4` (combined)** → HALT regardless of which counter got there. Prevents pathological cycles where schema bounces and verdict revisions alternate to bypass individual caps (mirrors `superpowers:executing-plans` stop-and-ask: when you can't make progress, ask)
4. **Evaluator verdicts are NOT violations** — `NEEDS_REVISION` from a MUST gate is a verdict with its own loop-back rule. Do not conflate: violation = schema gap before skill runs; verdict = judgement after skill runs. Both increment `total_retries`.
5. **user_message is mandatory** — always human-readable; cite the specific SKILL.md Preconditions row that failed (or evaluator finding, for verdict loops).

### Multi-field violations

If several fields are missing, list them all in `missing[]`. Router picks the SINGLE furthest-upstream skill to bounce to — usually `copywriting-intake` if any Level 1 field is absent. Bouncing to multiple upstreams in one round is forbidden (round counter would be ambiguous).

### Audit-stage exception

`copywriting-audit-stage` does NOT accept bounce-back to `copywriting-intake` (audit bypasses intake by design). Its only bounce target is `using-copywriting-toolkit` for re-collecting `external_copy` full text.

## Router Validation

`using-copywriting-toolkit` is the single enforcement point for precondition validation. It performs three checks before every skill launch:

1. **Aggregate retry cap** — read `envelope.retries.total_retries`; if `>= 4`, HALT and ask the user (do not launch any skill, do not bounce). Present the retries breakdown (`bounce_round` / `revise_round_count`) so the user can see why progress stalled.
2. **Preconditions check** — load the target skill's `## Preconditions § Required envelope fields` table from its SKILL.md, verify every row against the current envelope. On any missing / malformed field → emit `violation` envelope, do NOT launch the target skill, route to the `bounce_to` skill named in the target's Preconditions, increment `bounce_round` and `total_retries`.
3. **Express qualification (Shape A only)** — per `using-copywriting-toolkit/protocols/phase-decision-tree.md §Step 0.5`, inspect raw brief against intake's Level 1 field set. If qualified, dispatch intake in Express Mode (`copywriting-intake/protocols/express-mode.md`); otherwise default to Q1-Q10 full intake.

Router does not draft, does not judge gate verdicts, does not rewrite. It routes, validates, and bounces.

### Why validation lives in the router, not each skill

- **Single source of truth** — when preconditions change, only the target skill's SKILL.md Preconditions table changes. Router reads it fresh; no duplicated validation logic drifts.
- **Downstream skills stay focused** — ideation, drafting, voice tuning, gates all assume a well-formed envelope. They do not contain defensive input-validation code paths.
- **bounce_round counter is a router-local concern** — a single validator keeps the round cap coherent. If skills self-dispatched bounces, round counting would fragment and the round-3 HALT rule could be violated.

### Express Mode is not a Preconditions bypass

Express Mode replaces Q1-Q10 **elicitation** with synthesis-plus-single-turn-confirmation. The Intake Completeness MUST gate still runs. The downstream skill still sees a well-formed envelope that satisfies its Preconditions. If Express-synthesised fields turn out to be wrong, a downstream skill will emit a violation → router routes back to intake → intake on re-entry forces Q1-Q10 (not Express) because bounce-backs are a disqualifier.

## Audit Trail

The envelope's `audit_trail[]` field (defined in `.claude-plugin/envelope.schema.json`) is an append-only log of pipeline events. Each entry records one of:

| event | written by | purpose |
|---|---|---|
| `skill-entered` | router, before skill launch | marks which skill starts processing the envelope |
| `skill-exited` | router, after skill returns | pairs with `skill-entered` so run duration + control flow is auditable |
| `gate-verdict` | `copywriter-evaluator` | records `PASS` / `PASS_WITH_NOTES` / `NEEDS_REVISION` + which gate |
| `violation-detected` | router, on Preconditions check failure | captures the missing / malformed fields |
| `bounce-dispatched` | router, after emitting violation envelope | names the upstream skill routed to |
| `auto-revise` | Phase 7 / 8 FIXABLE handler | marks a round of automatic revision |
| `halt-ask-user` | router, on `total_retries >= 4` or `bounce_round >= 3` | surfaces a stall to the user |

Entries carry `{at, event, skill, detail}`. The router is the sole writer for routing / violation events; the evaluator is the sole writer for verdict events. Skills do NOT append to `audit_trail[]` themselves — a skill that fails its own precondition returns a violation envelope and lets the router log it.

Rendering to user: on `halt-ask-user` events, the router SHOULD render the last 5-10 `audit_trail[]` entries as a compact timeline so the user can see where the pipeline stalled. For normal completion (`phase: delivered`), the full trail is available to the caller but not rendered by default.

Persistence: `audit_trail[]` lives on the envelope. Callers who want cross-session auditability must save the envelope themselves (the plugin does not persist).

## External Caller Guide

If you invoke skills directly (not through `using-copywriting-toolkit` router), you are responsible for constructing the initial envelope correctly. The router's Step 0.5 Express Qualification + Preconditions validator are skipped in this path — you own both.

### Minimum envelope shapes

**Shape A — new brief** (go through router; Express / Q1-Q10 decided there):

```json
{
  "phase": "phase-0-intake",
  "raw_request": "<user's original message, verbatim>",
  "brief": {}
}
```

Only `phase` and `raw_request` are required. Leave `brief: {}` empty — intake will populate it. Do NOT pre-fill `brief.*` from your own inference.

**Audit alt-entry** (external copy review):

```json
{
  "phase": "phase-audit-entry",
  "form": "unknown",
  "brief": {
    "review_focus": "all"
  },
  "external_copy": "<FULL TEXT — not a summary>"
}
```

`external_copy` MUST be full text. Summaries collapse the form-adherence + voice-consistency checks and will be rejected by `copywriting-audit-stage`.

**Mid-pipeline re-entry** (you kept an envelope from a prior run):

Pass it as-is. The router's Step 2 mid-pipeline table (`phase-decision-tree.md`) routes based on `envelope.phase` + latest verdict. Do NOT mutate `phase` yourself — that violates the router's state machine.

### What NOT to do

- **Do NOT construct `voice_quadrant` yourself** — it's Phase 5's output. If you try to inject a pre-computed quadrant, Phase 5's validation may accept it (the Preconditions only check `draft` + `form` + audience), but the downstream gates will compare it against the draft's actual register and likely flag a conflict.
- **Do NOT set `gate_verdict: "PASS"` manually** — evaluators own verdicts. A manual PASS bypasses ethics / form gates silently.
- **Do NOT omit `retries: { bounce_round, revise_round_count, total_retries }`** if you're resuming a previously-bounced envelope — the router halts at `total_retries >= 4`, and omitting the field resets the counter, allowing the stall loop to hide.

### Envelope evolution

Future plugin versions may add optional fields. Callers should preserve unknown fields verbatim on re-entry (forward-compatible). Required fields are locked per semantic version — changes go in CHANGELOG and bump the minor version at minimum.

## Cross-Plugin Delegation (Loose)

Phase 1 Message Confirmation inside `copywriting-intake` may RECOMMEND `planning-team` when the problem is thesis-level (unclear positioning / audience / goal). Do NOT enforce — user may proceed anyway. No auto-delegation.

## Agents

Plugin-local pair — NOT shared with `domain-teams`. Infrastructure stays independent.

### `agents/copywriter.md` (worker)

Drafting / ideation / audit-variant producer. Persona: reader-first copywriter in 糸井 / 岩崎 / 眞木 / 谷山 (JP) and Ogilvy / Schwartz / Halbert / Cialdini (Anglo) lineages, with 小霜「嘘をつかない」 discipline. Model tier: sonnet.

Used by (launches the agent, passing protocol + standards paths):
- `copywriting-intake` (Phase 0-1 brainstorming + Q1-Q10 intake)
- `copywriting-ideation` (Phase 2 divergence subagents + convergence)
- `copywriting-neta-injection` (Phase 3 WebSearch pipeline A-D + 4 techniques)
- 5 Phase-4 drafter skills (short / mid / long-pasona / long-extended / light-action)
- `copywriting-voice-positioning-stage` / `copywriting-voice-tone-stage` (Phase 5-6 tuning passes)
- `copywriting-audit-stage` (Phase 2 diagnose / Phase 3 rewrite variants)

Does NOT produce gate verdicts — that is `copywriter-evaluator`'s role.

### `agents/copywriter-evaluator.md` (evaluator)

Gate verdict producer. Persona: strict legal / framework reviewer (景品表示法 / FTC / Cialdini misuse / PASONA / BEAF / QUEST / PASTOR / PREP / CREMA / voice quadrant / form appropriate). Deliberately NOT copywriter-persona — aesthetic capture is an anti-pattern that contaminates ethics / form judgement. Model tier: opus.

Used by:
- `copywriting-intake` (Intake Completeness MUST gate on Understanding Summary)
- `copywriting-neta-injection` (Neta Safety SHOULD gate)
- `copywriting-voice-tone-stage` (Voice Consistency SHOULD gate)
- `copywriting-ethics-check-stage` (Ethics MUST gate, Phase 7)
- `copywriting-form-check-stage` (Form 8a MUST + 8b SHOULD, Phase 8)
- `copywriting-audit-stage` (reuses Phase 5-8 gates on external copy)

Does NOT draft or soften — only judges.

### Why two agents, two personas

Separation keeps each role honest:

- Copywriter persona (reader-first, voice-disciplined) produces quality drafts but is the wrong lens for legal / ethics / framework judgement — it prioritises elegance over compliance.
- Legal-reviewer persona produces reliable gate verdicts but is the wrong lens for drafting — it prioritises risk-avoidance over rhetorical force.

Running a single multi-role agent blurs both. Using `domain-teams:worker` / `domain-teams:evaluator` (generic) loses the copywriting-specific priors (lineage attribution rules, ethics landmines, voice traditions). Hence the specialized pair.

## A/B Coexistence

`domain-teams:copywriting-team` remains untouched. Both plugins run in parallel. Do NOT modify the original in this plugin's commits. Consolidation deferred to post-A/B retrospective.

## Inline-Duplication Drift Risk

`persuasion-psychology-anchor.md` appears 5× identical in workflow skills. If drift observed later, a sync script is acceptable — do not attempt cross-skill loading at runtime.

## Skill Structure

```
copywriting-toolkit/
  .claude-plugin/plugin.json
  README.md
  CLAUDE.md
  agents/
    copywriter.md              # worker — sonnet, drafting / ideation / audit variants
    copywriter-evaluator.md    # evaluator — opus, legal / framework / voice gates
  skills/
    <skill>/
      SKILL.md                  # ≤6K tokens, references the rest
      standards/*.md            # cp from domain-teams, byte-identical
      protocols/*.md            # same
      checklists/*.md           # only gate skills
      rubrics/*.md              # only gate skills
      research/*.md             # grounding notes, cp
```

## Branch / Commit Convention

- Branch: `feat/copywriting-toolkit-v1.0.0`
- Commit prefixes: `feat(copywriting-toolkit)` or `chore(copywriting-toolkit)` — CC CI whitelist only
- No `test:` / `ci:` commits — fixtures bundle into relevant `feat` commit
