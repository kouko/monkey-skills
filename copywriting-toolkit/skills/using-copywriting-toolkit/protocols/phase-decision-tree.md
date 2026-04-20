# Protocol — Phase Decision Tree

Operational routing script for `using-copywriting-toolkit`. Read top-down, ask only the questions needed to disambiguate, and hand off with a populated handoff envelope.

This protocol is imperative — the orchestrating agent (main agent, or a dispatched `copywriter` subagent) can execute it step-by-step without further context.

## Invariants

- Never draft copy or produce gate verdicts inside this protocol; only route.
- Never skip Phase 0 Intake entirely — but a fully-qualified brief may take the Express Mode fast path (Step 0.5 below) instead of Q1-Q10. Both paths still run the Intake Completeness MUST gate.
- Every hand-off produces a handoff envelope (schema in `SKILL.md` §Handoff Envelope Schema).
- Ambiguous routing → ask ONE clarifying question from this protocol, not a freeform probe.
- **Precondition validation is mandatory before every skill launch** — load the target skill's `## Preconditions` schema, check envelope against it, emit `violation` envelope and route upstream if the schema does not hold (see `../../CLAUDE.md §Envelope Violation`). Do NOT launch a skill against an incomplete envelope.

## Step 0 — Detect Input Shape

Inspect the raw request. Classify into one of:

| Shape | Signal | Route |
|---|---|---|
| (A) Raw new brief | User describes a product/goal with no draft | Step 1 |
| (B) External copy + review ask | User pastes copy and asks for critique / improvement / A/B | Step A1 (audit alt-entry) |
| (C) Mid-pipeline continuation | Envelope already exists (prior skill returned) | Step 2 |
| (D) Explicit skill request | User names a specific skill | Hand off directly, no routing |
| (E) Out-of-scope | Technical doc / product strategy / UX microcopy / research / code | Hand off to another team (see SKILL.md §Out of Scope) |

## Step 0.5 — Express Qualification Check (Shape A only)

Before routing Shape A (raw new brief) to intake's Q1-Q10, check whether the brief already carries all Level 1 fields. If yes, dispatch intake in Express Mode (`copywriting-intake/protocols/express-mode.md`) instead of Q1-Q10.

### Qualification rules (ALL must hold)

Load `copywriting-intake/SKILL.md §Preconditions` (hmm — intake has no envelope preconditions since it's the entry; use `copywriting-brainstorming.md §Level 1` field list instead). Check the raw brief against the Level 1 field set for the **predicted Phase 4 form**:

| Common Level 1 (all forms) | Source check |
|---|---|
| `form_type` (short / mid / long-pasona / long-extended / light-action / audit / ideation-only) | Detectable from channel / length / action cues in brief |
| `product` | User names a product / service / thing being copy-for |
| `value_proposition` | User states a 1-sentence value claim OR the claim is extractable as a single sentence |
| `target_audience` | User names at least one concrete demographic / persona |

Plus form-specific Level 1 (see each Phase 4 skill's `## Preconditions § Required envelope fields`):

- **short-form**: channel + char-limit band surfaced (or default 7-15 inferable)
- **mid-form**: ≥3 concrete benefits + channel + evidence sources
- **long-form-pasona**: target_length + channel + schwartz_level
- **long-form-extended**: positioning + language + schwartz_level
- **light-action**: action_weight + target_action

### Disqualifiers (ANY forces Q1-Q10)

- Any Level 1 field requires inference (cannot be quoted from the brief)
- Brief is a bounce-back re-entry (envelope.violation present from downstream) — bounce-backs ALWAYS take Q1-Q10 because synthesis missed something the first time
- User explicitly requested `full intake` / `detailed Q&A` / 詳しく聞いて etc.
- Brief contains a potential 景品表示法 / FTC red flag — grill requires interactive clarification

### Routing

- **ALL qualify + zero disqualifiers** → dispatch to `copywriting-intake` with `mode: express`, envelope carries `raw_request` only
- **Any disqualifier** → dispatch to `copywriting-intake` with `mode: full-q1-q10` (default), skip to Step 1
- **Partial qualification** (Level 1 mostly present, one missing) → dispatch with `mode: full-q1-q10` and include `skip_hint: [confirmed_field_1, ...]` so intake can short-circuit already-answered Q's (not an Express, just trimmed Q&A)

Express Mode itself includes a user confirmation turn + grill + Intake Completeness gate. Do NOT bypass those by routing directly to Phase 2+.

## Step 1 — New Brief (Shape A)

### 1.1. Lightweight scope check

Before routing, verify the request IS copywriting:

- Is the deliverable persuasive / marketing copy (LP, email, headline, tagline, ad, product description, voice guide)? If no, route to another team.
- Is the scope a single workflow or multiple? (e.g. LP + email + banner = three workflows). If multiple, decompose and route each separately.

### 1.2. Handoff to intake

Default route: `copywriting-intake`. The intake skill runs Phase 0 (brief intake) + Phase 1 (message confirmation) as a hard gate.

Envelope:

```json
{
  "phase": "phase-0-intake",
  "raw_request": "<user's original message, verbatim>",
  "brief": {},
  "next_stage": "copywriting-intake"
}
```

Do not infer `brief.product`, `brief.audience`, etc. at router level. The intake skill collects Level 1/2/3 fields via its own brainstorming protocol.

## Step 2 — Mid-Pipeline Continuation (Shape C)

Envelope arrived from a prior skill. Read `envelope.phase` and `envelope.gate_verdicts` to decide the next hop.

### 2.1. Envelope validation

Check required keys: `phase`, `brief`, `next_stage`. If malformed, return a structured error to the caller — do not best-effort mutate.

### 2.2. Phase-based routing

| Incoming `phase` | Gate verdicts state | Next route |
|---|---|---|
| `phase-0-intake` | `intake_completeness = PASS` | Step 3 (Phase 2 ideation decision) |
| `phase-0-intake` | `intake_completeness = NEEDS_REVISION` | Re-enter `copywriting-intake` |
| `phase-2-ideation` | passed | Step 4 (neta pre-draft decision) |
| `phase-3-neta-pre-draft` | passed | Step 5 (form selection) |
| `phase-4-draft` | form gate not yet run | Step 6 (neta overlay decision) |
| `phase-3-neta-overlay` | passed | `copywriting-voice-positioning-stage` (Phase 5) |
| `phase-5-voice-positioning` | passed | `copywriting-voice-tone-stage` (Phase 6) |
| `phase-6-voice-tone` | passed | `copywriting-ethics-check-stage` (Phase 7) |
| `phase-7-ethics` | PASS | `copywriting-form-check-stage` (Phase 8) |
| `phase-7-ethics` | NEEDS_REVISION | Return to whichever skill authored the draft (form-specific) |
| `phase-8-form-check` | PASS | Pipeline complete — deliver to user |
| `phase-8-form-check` | NEEDS_REVISION | Return to draft skill OR voice stage depending on revision notes |
| `audit` | (any stage) | Evaluate `envelope.audit_focus` to route to next gate skill |

## Step 3 — Phase 2 Ideation Decision

Ask (if not already answered in intake):

> "Do you want to generate candidate angles / headline options first, or go straight to drafting?"

Decision logic:

- **Yes, generate candidates** → Route to `copywriting-ideation`. Set envelope `next_stage = "copywriting-ideation"`.
- **No, brief is concrete** → Skip to Step 4.
- **Complex brief signals** (multi-channel, ambiguous target, SNS-native campaign, cultural/meme-driven) → Strongly recommend ideation; confirm with user before skipping.

## Step 4 — Phase 3 Neta Pre-Draft Decision

Check `envelope.brief.neta_opt_in`.

- **neta_opt_in = false** → Skip Phase 3 entirely. Go to Step 5.
- **neta_opt_in = true** → Ask for timing (if not already set):

  > "Neta timing — bake in pre-draft (neta is the angle, drives the draft) OR overlay post-draft (clean draft first, then 2-3 neta variants)?"

  - **bake-in** → Route to `copywriting-neta-injection` now; set `envelope.brief.neta_timing = "bake-in"` and `next_stage = "copywriting-neta-injection"`.
  - **overlay** → Set `envelope.brief.neta_timing = "overlay"` and continue to Step 5; Phase 3 runs after Phase 4.
  - **undecided** → Default to **overlay** (preserves draft's framework integrity, simplifies isolated neta safety gate).

## Step 5 — Phase 4 Form Selection

Walk the form decision tree in order. Stop at the first YES.

### 5.1. Audit branch

> Is this really a review / critique of existing copy?

If YES (shouldn't happen if you reached Step 5, but double-check) → Redirect to Step A1 (audit alt-entry).

### 5.2. Short form

> Is the deliverable a headline, tagline, SNS post, banner, CM title, short ad copy? Target length 7-15 chars (JP) or equivalent?

YES → `copywriting-short-form`. Framework: AIDMA A+I only, 5 切入點 (benefit / fear / subversion / calling / question), 谷山 なんかいいよね禁止 discipline, 3-秒ルール readability.

### 5.3. Mid form

> Is this an EC product description (Rakuten / Amazon JP / in-store POP / presentation materials)? Length 100-600 chars, product-centric.

YES → `copywriting-mid-form`. Framework: BEAF (Benefit → Evidence → Advantage → Feature), Benefit-first enforcement.

### 5.4. Light action

> Is this a micro-conversion target — email opt-in, newsletter subscribe, free download, LINE 登録, SNS post with light CTA, article with light action prompt?

Check `envelope.brief.action_weight`:

- `light` → `copywriting-light-action`. CREMA (5-stage) for explicit action; PREP (4-stage) for no-CTA logical/share payload.
- If brief claims light-action but target is high-ticket purchase → REROUTE to long-form (scope warning per original light-action-frameworks standard).

### 5.5. Long-form PASONA

> Long-form LP, sales letter, 記事広告, email campaign, or long CM? JP audience or JP-lineage positioning? Heavy-action macro-conversion (purchase)?

YES → `copywriting-long-form-pasona`. Framework: PASONA / 新 PASONA / PASBECONA (神田 2016/2021 canon) — Problem → Affinity → Solution → Offer → Narrow → Action.

### 5.6. Long-form Extended

> Long-form but non-JP audience OR expertise-based positioning OR personal-story shepherd-guide positioning?

YES → `copywriting-long-form-extended`. Framework: QUEST (Fortin 2005, education/expert) OR PASTOR (Edwards 2016, personal-story). Cross-pollination with PASONA stages documented inside that skill's standard.

### 5.7. Fallback

None of the above → Form indeterminate. Re-enter intake with a clarifying question about channel + length + action weight.

### 5.8. Handoff

Envelope:

```json
{
  "phase": "phase-4-draft",
  "form": "<selected>",
  "brief": { "...": "passed through" },
  "message_thesis": "...",
  "ideation_pool": ["... if Step 3 ran ..."],
  "neta_candidates": ["... if Step 4 ran bake-in ..."],
  "next_stage": "copywriting-<form>"
}
```

## Step 6 — Phase 3 Neta Overlay Decision (Post-Draft)

Only reached if Step 4 deferred neta to overlay.

- If `envelope.brief.neta_timing == "overlay"` → Route to `copywriting-neta-injection` now. Set `next_stage = "copywriting-neta-injection"`. The neta skill produces 2-3 variants then hands off to Phase 5.
- Otherwise → Skip to `copywriting-voice-positioning-stage`.

## Step 7 — Phases 5-8 (Linear)

Once the draft exists and neta overlay (if any) is done, the route is linear:

```
copywriting-voice-positioning-stage
  → copywriting-voice-tone-stage
  → copywriting-ethics-check-stage      (evaluator-only gate)
  → copywriting-form-check-stage        (evaluator-only gate)
  → pipeline complete
```

Each stage reads the envelope, appends its layer, updates `next_stage`, returns.

Gate-failure handling:

- **Ethics NEEDS_REVISION** → Return to authoring skill (form-specific) with ethics feedback. Never deliver ethics-failing copy.
- **Form NEEDS_REVISION** → Return to voice-tone OR authoring skill depending on which layer caused the failure (evaluator notes tell you which).
- **Voice-consistency SHOULD gate fails** → User-visible note; don't block delivery unless the user opted into a hard voice gate.

## Step A1 — Audit Alt-Entry (Shape B)

User arrives with existing external copy.

### A1.1. Collect audit focus

Ask:

> "Audit focus — framework adherence / ethics / voice / form / all dimensions?"

### A1.2. Ask for form hint (optional)

> "Do you know the original form (short / mid / long PASONA / long QUEST-PASTOR / light-action), or should the audit detect it?"

### A1.3. Handoff to audit skill

Envelope:

```json
{
  "phase": "audit",
  "existing_copy": "<pasted copy verbatim>",
  "audit_focus": "<framework | ethics | voice | form | all>",
  "form_hint": "<if supplied>",
  "brief": { "...": "collected via audit intake" },
  "next_stage": "copywriting-audit-stage"
}
```

`copywriting-audit-stage` runs its own Phase 0 light intake, detects form + framework, diagnoses issues by severity, and chains into gate skills (Phase 5-8) to produce verdicts against the external copy. If user asks for rewrite variants, those variants route through ethics gate before delivery.

## Step B — Loose Coupling Check to planning-team

Anywhere in Steps 1-5, if the request reveals:

- Product positioning undefined / ambiguous
- Target audience cannot be inferred AND user cannot clarify
- Goal is strategic voice/brand work rather than expression ("what should our brand voice be?")

Surface the hint:

> "This looks thesis-level rather than expression-level. Consider running `domain-teams:planning-team` first to clarify the value proposition, then return here for expression. You may proceed in copywriting-toolkit anyway — no hard block."

Record the recommendation in `envelope.notes`. Do NOT auto-invoke planning-team. Do NOT block. User decides.

## Step C — Out-of-Scope Routing (Shape E)

If the request is out of scope, hand off to another team:

| Signal | Target |
|---|---|
| API docs, tutorials, reference | `domain-teams:docs-team` |
| PRODUCT-SPEC authoring, value proposition definition | `domain-teams:planning-team` |
| Button labels, error messages, empty states | `domain-teams:design-team` |
| Audience insights, competitive analysis | `domain-teams:research-team` |
| Implementing copy in code / templates | `domain-teams:code-team` |

No envelope is produced — just a team recommendation.

## Reference — Envelope Schema

See `SKILL.md` §Handoff Envelope Schema. Summary:

```json
{
  "phase": "phase-N-<name>",
  "form": "... or null",
  "brief": { "... Level 1/2/3 intake fields ..." },
  "message_thesis": "...",
  "ideation_pool": [],
  "neta_candidates": [],
  "draft": "...",
  "voice_quadrant": "...",
  "voice_tone": "...",
  "gate_verdicts": { "...": "..." },
  "notes": [],
  "next_stage": "copywriting-<skill-name>"
}
```

Every routing decision in this protocol ends by populating `next_stage` and handing the envelope to that skill.
