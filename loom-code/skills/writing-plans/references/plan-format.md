# Plan format — handoff from `writing-plans` to `subagent-driven-development`

> Companion to [`../SKILL.md`](../SKILL.md). Defines what writing-plans produces and what `subagent-driven-development` (SDD) consumes.

## Why this schema

SDD dispatches three subagents per task (implementer + spec-reviewer + code-quality-reviewer). To do that without re-extracting metadata from prose, SDD needs each task pre-decorated with:

- **Description** — the implementer's task text.
- **Module** — for code-quality-reviewer's per-task scoping.
- **Context paths** — what the implementer reads (paths-not-content delegation).
- **Acceptance** — for tdd-iron-law's RED-GREEN-REFACTOR cycle (failing test name + GREEN condition).
- **Dependencies** — for sequencing / parallelization.

Free-form plans force SDD to re-parse; this schema makes the parse trivial.

## Where the plan lives

| Mode | Path | When |
|---|---|---|
| File | `docs/loom/plans/YYYY-MM-DD-<topic>.md` | **Default.** Sibling to the brief at `docs/loom/specs/`. |
| Inline (no file) | Plan in chat context | Only for §When NOT to Use exempt cases — brief was its own plan; document inline; do not commit. |

## Schema

### Top-level header (required)

```markdown
# Plan: <topic>

**Source brief**: <path to brief, e.g. docs/loom/specs/2026-05-16-csv-export.md>
Goal: <one sentence transcribed from the brief's Smallest End State at
    plan time, no nested body — see §Field-value grammar; frozen with
    the plan (wrap continuation lines WITH indentation — unindented
    wraps silently truncate the rendered goal); never edited
    afterward>
Stage: <planning | sdd:wave-N | review:round-N | blocked:user-decision |
    finishing — updated by the orchestrator at each transition,
    committed with the nearest ledger or close-out commit>
Steps: <OPTIONAL numbered block, one line per derived dependency
    level, titles in the user's conversation language; when present
    the count must equal the plan's dependency-level count —
    plan_card.py exits 1 loud on mismatch>
**Total tasks**: <N>
**Critical-path depth**: <D> (must be ≤5; if >5 route back to brainstorming)
**Execution order**: sequential | parallel-where-possible
**Plan-document-reviewer verdict**: PASS (timestamp) | PENDING
```

If `Plan-document-reviewer verdict` is `PENDING`, the plan has not been self-reviewed yet and SDD MUST NOT consume it.

blocked:user-decision marks an arc halted awaiting a user ruling: set it when the orchestrator stops mid-arc to wait for a user decision (an open finding, a deferred choice), and on resume flip Stage to the stage the ruling re-enters.

A `Steps:` line with content after the colon is rejected loudly by `plan_card.py` — the bare `Steps:` line followed by indented numbered titles is the only accepted form.

**Critical-path depth** is the **longest chain of tasks linked by `Dependencies`** (the longest sequential path through the dependency DAG). N independent tasks at the **same dependency level** (disjoint `Files touched`, no semantic dependency) count as **one level**, not N. The ceiling is on this depth, NOT on `Total tasks` — `Total tasks` is uncapped.

### Plan-level diagram slot

Every plan carries one required top-level section, `## Task-flow diagram`, placed between the header and Task 1: a Mermaid `flowchart` of the task dependency DAG (the same graph `Dependencies` fields encode, drawn once so a reader sees the shape before reading tasks in order).

This section is fill-or-declare: either embed the diagram(s) this section
names, or replace the body with the single line
`N/A — no flow/state/architecture-shaped content: <one-line reason>`.
Do not delete the section heading — an absent heading or a bare section is
a reviewable omission, and an N/A whose reason does not hold against the
artifact's own content is a reviewable claim. A paragraph that suffices
needs no diagram — the slot forces the declaration, not the drawing.
Channel rule SSOT: `loom-code/hooks/family-relay.md §(b) Visual defaults`.

When-to-draw judgment: see [`../../brainstorming/references/visual-companion.md`](../../brainstorming/references/visual-companion.md).

Per-task diagrams are explicitly NOT required — this slot is plan-level only, one diagram per plan, never one per task.

### Plan-level open-questions slot

Every plan carries one required top-level section, `## Open Questions`, placed after the plan-level diagram slot and before Task 1: the plan's home for a question nobody has resolved yet. When a fork surfaces during planning or execution and nobody resolves it, it goes here instead of into `## Decision Log` — silently absorbing an unresolved question into a section meant for decisions is what let a known-undecided design question reach the user as a whole-branch review finding instead of a planning decision.

This section is fill-or-declare: either record every question — settled or not — as an entry, or replace the body with the single line
`N/A — no unresolved question: <one-line reason>`.
Do not delete the section heading — an absent heading or a bare section is
a reviewable omission, and an N/A whose reason does not hold against the
artifact's own content is a reviewable claim.

Entry form: `- OQ-<n> [<TOKEN>] — <question text>`.

- **`OQ-<n>` is authored, never derived.** The plan's author types the number. It is never slugified, hashed, or otherwise generated from the question's text — mirroring the `BI-<n>` rule in [`../../brainstorming/references/handoff-brief-format.md`](../../brainstorming/references/handoff-brief-format.md) §Brief item identifiers.
- **Monotonic, never renumbered, never reused.** A new entry takes the next unused number — the highest `OQ-<n>` this plan has ever used, plus one — regardless of where it sits in the list. An entry already present keeps the number it already has. A deleted entry's number is retired: no later entry may carry it. This mirrors the same `BI-<n>` rule in [`../../brainstorming/references/handoff-brief-format.md`](../../brainstorming/references/handoff-brief-format.md) §Brief item identifiers.
- **`<TOKEN>` is exactly one of two values: `[OPEN]` or `[RESOLVED]`.** No third status exists.
- **A `[RESOLVED]` entry carries how it was resolved, on the same entry.** The resolution is not a separate field or a separate line — it is written into the entry's own question text (for example: "...→ resolved: <how>").

This section deliberately carries no owner field, no deadline field, no routing field, and no per-task linkage field — each is a decided omission, not an oversight. An owner or deadline exists in mature closure-tracking practice to let a question stay open *through* a phase; a gate that blocks on any `[OPEN]` entry removes that permission, so the fields that governed it are removed too. A routing field distinguishing "the agent may settle this" from "the user must" is not carried either — that classification is already written down: see `~/.claude/rules/judgment-rubrics.md` §3 for when an agent must stop and ask the user rather than settle a question itself. A per-task `Blocked by: OQ-n` linkage field is likewise not carried — the section-level gate, not the task, is this schema's unit of blocking.

### Per-task block (required, repeats N times)

```markdown
## Task <N> — <short imperative name>

- **Description**: <first line is imperative voice, written in English, and stays within a 300-character ceiling; route every further clause into a nested bullet or a markdown table beneath it — see §Field-value grammar>
- **Module**: <path or module name; ONE only>
- **Files touched**: <comma-separated paths the implementer will Write / Edit>
- **Context paths**:
  - <absolute path to existing code the implementer reads>
  - <... additional context paths>
- **Acceptance**:
  - **RED**: <first line states the assertion, written in English, and stays within the same 300-character ceiling — e.g. the `Fails today because ...` clause below fits inside it; route anything beyond that into a nested bullet or a markdown table beneath it — see §Field-value grammar>
  - **GREEN**: <same first-line rule as RED — states the assertion, written in English, within the same 300-character ceiling; anything beyond that goes into a nested bullet or a markdown table — see §Field-value grammar>
- **External surfaces**: <v0.9.0+ — required when task touches non-stdlib external surface. See §External surfaces below. Omit field entirely if task is pure internal logic.>
- **Reuse-adequacy**: <v0.43.0+ — required when the task's Description instructs the implementer to reuse an existing helper in a new lane. Two author-written slots, `Observed` (ends in a source marker) and `Intended`; no author-side adequacy verdict — that judgement is the reviewer's, not the plan's. See §`Reuse-adequacy` below. Omit field entirely if the task authors new logic instead of reusing an existing helper across lanes.>
- **Dependencies**: <one of: "none" | "Task N completes first" | "Tasks N, M complete first" (multi-prerequisite — N and M must both finish before this task starts) | "Tasks N, M parallel" (both are prerequisites, may run in parallel). Cross-part ordering: use "none" at task level + a plan-level `Notes` entry; the field is within-plan only and cannot reference a sibling part's tasks.>
- **Independent**: <true | false>  # v0.8.0+ — opt-in marker for `dispatching-parallel-agents`. Default false.
- **Review-weight**: <mechanical | prose | OMIT>  # v0.11.0+ — opt-in, default absent = full triad (implementer + spec-reviewer + code-quality-reviewer). `mechanical` may ONLY be set when this task is an identical or near-identical edit reproducible from an exact spec — never for logic, heuristic, hook, or security-surface changes. `prose` (v0.42.0+) may ONLY be set when every file in `Files touched` is `.md` authored prose. See §`Review-weight` below.
- **Brief item covered**: <traceability referent — ONE field, four accepted referent kinds:
    (a) a quote or reference from the brief's Smallest End State / Decision section, OR
    (b) when the plan consumes a loom-design change-folder, a **stable join key** of the form
    `<change-id> / Requirement: <name> / Scenario: <name>` (R5 — a checkable provenance referent,
    à la Kiro `_Requirements:` / Spec-Kit `FR-###`), OR
    (c) a `BI-<n>` identifier declared by the source brief, OR
    (d) a `REQ-<n>` id declared by an id-mode spec file's header, or the id-form join key
    `<change-id> / REQ-<n> / Scenario: <name>`. A bare `REQ-<n>` (no `/ Scenario:` suffix) is
    requirement-level coverage of every scenario under it (OQ-3, option A) — see
    the packaged [`requirement-identifiers.md`](requirement-identifiers.md) contract
    for the identifier rules (do not restate them here). This is the SAME field with a broadened
    referent — do NOT add a second field; point at the source `### Requirement:` / `#### Scenario:`
    names rather than copying their prose. One no-requirement value is legal: `none — <reason>`.
    See §`Brief item covered` below for kind (c), that value, and the tie-break rule.>
- **Status**: <runtime ledger field, DEFAULT-ON — see §Progress ledger. One of:
    "pending" | "claimed(@<agent>)" | "done(<sha>)" | "blocked". writing-plans emits
    "pending" at plan time; an old plan without Status fields behaves exactly as
    before — fully backward compatible. NOT authoring content beyond the initial
    "pending"; SDD writes the transitions, the plan-document-reviewer ignores it.>
- **Gloss**: <one line in the user's conversation language stating
    the task's user-visible effect and why it matters to the goal —
    NEVER a restatement of the task name; rendered under the task row
    by plan_card.py; emitted by writing-plans for new plans, optional
    on old ones>
```

#### Field-value grammar (v0.89.0+)

A field's value is bounded by WHERE its content goes, not by how long the
document is — nothing is deleted, overflow is relocated. This replaces
the earlier judgment-shaped rule that asked for a single unbounded
sentence of work, which let a writer producing a 1,452-character
`Description` believe in good faith that it satisfied that duty. Two
later attempts at a machine-checkable *sentence* rule were tried and
retired in turn: occurrence counting false-positived on `0.89.0`,
`e.g.`, `i.e.` and an ellipsis; the sentence-boundary heuristic that
replaced it false-negatived on a lowercase-initial third sentence —
letting an over-cap field pass silently — while still false-positiving
on `e.g. Python`. The rule below is a plain character-length cap
instead, which has no punctuation edge case to enumerate, so a
mechanical checker decides it the same way every time.

- **`Description`, `Acceptance.RED`, `Acceptance.GREEN`.** Keep every
  prose unit within a **300-character ceiling** — a unit being either
  the field's first line (the text on the bullet's own line, right
  after the colon), or one nested bullet's own text folded across
  however many physical lines it wraps to. This is the SAME number and
  the SAME rule for all three fields, and for every nested bullet
  beneath them; there is no per-field branch and no per-bullet
  exemption. Route every further clause — a caveat, a grounding clause
  such as the `Fails today because ...` clause this file already
  teaches (see the Worked example below), a list of sub-steps, a table
  of cases — into a nested bullet or a markdown table beneath that
  first line, never onto the first line itself; a markdown table row
  carries no character ceiling of its own, only the first line and
  each nested bullet do.
- **`Goal:`.** Carries no length ceiling — admits no nested body:
  `plan_card.py`'s `_header_value` folds any indented continuation
  into the card's single `end-state:` line, so a nested body there is
  silently flattened rather than rendered. One sentence is brevity
  guidance, not a mechanical rule — no check enforces sentence
  counting on this field.

See the Worked example section below for a before/after rewrite of an
over-long `Description` under this rule.

#### `Files touched` and `Independent` (v0.8.0+)

- **`Files touched`** is the **disjointness oracle** for cross-task parallel dispatch. List every file the implementer will Write or Edit (not files it merely Reads — those go in `Context paths`).
- **`Independent: true`** is the plan author's claim that this task has no shared symbol / no sequential data dependency with other `Independent: true` tasks. Default `false`.
- **`Dependencies` is the ordering authority** — `Independent: true` governs concurrency only among tasks at the same dependency level, never against a declared dependency.
- [`../../dispatching-parallel-agents/SKILL.md`](../../dispatching-parallel-agents/SKILL.md) MAY dispatch tasks concurrently only when **both** declare `Independent: true` AND their `Files touched` sets are disjoint. Otherwise SDD's sequential dispatch is the floor.
- **Empty-recon sentinel.** When target-repo reconnaissance finds **no existing target** (greenfield target / wrong repo), the contract forbids fabricating an existing path — so `Files touched` / `Module` may be written as a **PROPOSED-new** form clearly marked NEW (`NEW: <proposed-path>`, or `greenfield — no existing target found`), **never a guessed existing path**. A task whose `Files touched` is a PROPOSED-new path defaults to **`Independent: false`**: the disjointness oracle cannot be trusted on a path that does not exist yet, so such tasks must not be marked parallel-eligible.

#### `Review-weight` (v0.11.0+, optional)

`Review-weight: mechanical` is an **opt-in exemption marker**, not a default. Default (field absent) is the full triad — implementer + spec-reviewer + code-quality-reviewer — unchanged.

It may ONLY be set when this task is an identical or near-identical edit reproducible from an exact spec — never for logic, heuristic, hook, or security-surface changes. If the task involves any conditional branching, a heuristic threshold, a hook, or touches a security-relevant surface, do NOT set this field; leave it absent so the full triad runs.

One named category worth calling out explicitly (see the worked example below): a task whose entire content is **running an established, deterministic sync/mirror script and committing its output**, verified by a checksum match or an existing drift-detection test — e.g. re-running a functional-copy sync script so a sibling skill's file matches its SSOT, or re-running a manifest-mirror script after a version bump. Zero hand-written logic, output fully determined by the script and the current SSOT state — this already satisfies "reproducible from an exact spec," it just isn't obvious without naming it.

`Review-weight: prose` (v0.42.0+) is a second, separate opt-in marker for a task whose whole diff is authored prose. Declaring it keeps the implementer dispatch and the spec-reviewer dispatch exactly as in the full triad, but **replaces the code-quality-reviewer arm with the docs-reviewer agent** — the two arms (spec-reviewer, docs-reviewer) still run in parallel, and the docs-reviewer's verdict substitutes into the same `code-quality-reviewer` slot when verdicts resolve (see `subagent-driven-development/SKILL.md`'s "Prose review-weight substitution" for the full mechanics).

Eligibility is narrow — transcribed from that same SSOT wording: this may ONLY be set when **all files listed in the task's `Files touched` are `.md` authored prose — never code, never config, never a generated/sync artifact**. Fail-closed, mirroring the mechanical exemption above: if any touched or diffed file is not `.md` authored prose, the orchestrator falls back to the full triad rather than silently narrowing review. `plan-document-reviewer` Check 16 gates this marker at plan review — a plan setting it without satisfying Check 16's eligibility test never reaches SDD.

Authoring guidance (non-gating — Check 16 stays the gate): when a task's Description already names an exact-spec target per Check 16's eligibility, declare `Review-weight: mechanical`, and when every file in the task's `Files touched` is `.md` authored prose, consider `Review-weight: prose` — an eligible task left undeclared costs a full reviewer triad for zero marginal defect yield. Check 16's exclusions apply unchanged — never declare the mechanical lane for logic, heuristic, hook, or security-surface work.

#### Progress ledger — the `Status` field (v0.10.0+; default-on v0.60.0+)

The per-task `Status` field turns the plan into a **run-scoped, durable, shared progress
ledger**. It is **runtime state**, not plan-authoring content: `writing-plans` emits its initial
value (`Status: pending` on every task at plan time — see below), `subagent-driven-development`
**maintains** it as it executes, and `plan-document-reviewer` **ignores** it.

Vocabulary (exactly these four):

| Value | Meaning | Set by SDD when |
|---|---|---|
| `pending` | not started (omission = old-plan opt-in only; new plans write it) | — |
| `claimed(@<agent>)` | an agent is working it; `<agent>` is the worktree branch name (unique per agent) | the implementer is dispatched |
| `done(<sha>)` | resolved + committed; `<sha>` is the task's commit | reviewers PASS and the task is committed |
| `blocked` | stuck (NEEDS_CONTEXT / BLOCKED / 3-round cap) | the task cannot proceed |

Why it earns its place:
- **Interruption (crash / session death):** the committed ledger + per-task commits let a resumed run
  skip `done(<sha>)` tasks and redo only the in-flight `claimed` one — no full-plan re-derivation.
- **Scale:** explicit status beats reconstructing progress from `git log` on a large plan.
- **Multi-agent (b):** the ledger is the **shared task-claim doc** that coordinates several concurrent
  agents (see `dispatching-parallel-agents` §Multiple concurrent sessions) — worktrees isolate files,
  the ledger coordinates *who does what*.

The ledger is DEFAULT-ON: writing-plans emits `Status: pending` on
every task at plan time. A plan without `Status` fields (written
before this default) behaves exactly as before — the ledger stays
opt-in-by-presence for old plans.

Every ledger flip routes through `python3 scripts/plan_card.py
<plan-path> --set-status "T<N>=<status>"` when `scripts/plan_card.py`
exists at the repo root — it rewrites only the task's `Status` line
and performs no whole-plan validation. When no repo-root copy exists,
run the same plan_card.py that ships in the loom-code plugin (under
the plugin installation's `scripts/` directory — the executing
SKILL.md carries the resolved invocation). Hand-edit only when both
copies are absent.

#### `External surfaces` (v0.9.0+)

When an atomic task touches a **non-stdlib external surface** the agent does not author, the plan MUST declare it. This is the plan-time half of the external-surface-grounding discipline (see `loom-code/skills/subagent-driven-development/standards/external-surface-grounding.md`); the review-time half is D7 in `code-quality-reviewer.md` + `code-reviewer.md`. The two halves form one defense-in-depth gate.

Five surface categories trigger the field (per the standard's §Five Surface Categories): **HTTP API**, **SDK package**, **MCP tool**, **CLI flag**, **internal sibling-team contract**. A third-party library reached for to do version / date / format work (e.g. `packaging`) is an **SDK package** surface — declare it or replace it with stdlib. Stdlib parsing (`json`, `datetime`, version-tuple split) is authored-internal and needs no declaration.

Format — one bullet per surface:

```markdown
- **External surfaces**:
  - SDK package: @anthropic-ai/sdk@0.40 client.messages.create — grounding: WebFetch https://docs.anthropic.com/en/api/messages (captured 2026-05-22)
  - MCP tool: claude_ai_Asana__create_tasks — grounding: in-context tool schema
  - CLI flag: gh pr create --base — grounding: gh pr create --help (captured 2026-05-22)
```

Each bullet declares **category** + **specific name / identifier** + **grounding source** (one of the four valid types: Live verification / MCP schema / Pinned reference / In-repo evidence — see the standard for details).

**Omit the field entirely** when the task is pure internal logic (renames a local symbol, edits a markdown doc with no external references, refactors an existing function with no new external calls, etc.). The field is opt-in by surface presence, not by every task.

Per-task `code-quality-reviewer.md` D7 enforces that any external call in the task's diff carries a grounding cite. Whole-branch `code-reviewer.md` D7 additionally checks for cross-task surface-consistency conflicts. The `spec-consistency.md` checklist (`CHK-SPEC-008`) requires this field's presence when the task description / `Files touched` reference any of the five surface categories.

#### `Reuse-adequacy` (v0.43.0+)

When a task's Description instructs the implementer to reuse an existing helper, function, or selector in a **new lane** — a different call site, a different data shape, or a different code path than the one the helper was originally written for — the task MUST carry a **Reuse-adequacy** declaration made of two author-written slots with opposite directions of fit:

- **`Observed`** — a report: words answer to the code. State, in the present tense, what the helper does **today**, about code that already exists, and end the slot in one **source marker** from a closed vocabulary of exactly three:

  ```
  read <repo-relative-path>:<line>
  inferred from docstring
  unverified assumption — <what would settle it>
  ```

  The `<repo-relative-path>` in the `read` form is **repo-relative** — an absolute path resolves on no other machine and `check_doc_citations.py` cannot bounds-check it. A sentence about what the **new** code will do belongs in `Intended`, not here: writing it here is the direction-of-fit mistake this slot exists to prevent. `unverified assumption` reuses the escape hatch already defined in §Stated facts below (name what would settle it) rather than a parallel rule.

  An absent marker, a marker outside this vocabulary, or an absolute path in the `read` form makes the block malformed: the reviewer returns NEEDS_REVISION on that ground alone and does not evaluate adequacy.

- **`Intended`** — a specification: code answers to the words. State what the new call path will do with the behaviour `Observed` reported.

**There is no author-written adequacy or justification field.** Whether the reuse is adequate — whether the behaviour `Observed` reports still holds on the call path `Intended` names — is the reviewer's verdict (`plan-document-reviewer` Check 17 (c2)), not a claim the plan author gets to make about their own work.

Before v0.43.0, this field was one free-prose line combining a behaviour-match claim and a why-acceptable clause in the same sentence — a shape whose direction of fit was ambiguous enough that a live weak-tier author took the specification reading and invented a reassuring behaviour difference that the code did not have. The combined field is retired, not extended: `Observed` / `Intended` replace it. Motivating case: PR #619 reused the top-line lane's selector in the statement lane without re-checking whether its old-lane behaviour still held; the selector's semantics did not carry over, and 1165 passing tests never crossed the seam to notice (`docs/loom/audits/2026-07-27-investing-arc-defect-provenance-audit.md` §3.7 A-2).

**Omit the field entirely** when the task authors new logic rather than reusing an existing helper across lanes. The field is opt-in by reuse presence, not by every task.

#### `Brief item covered` — kinds (c) and (d), the none-value, and the tie-break (v0.79.0+)

**Referent kind (c): a `BI-<n>` identifier declared by the source brief.** It joins the quote kind (a) and the change-folder join-key kind (b) as an accepted referent of this same field — cite the id, not a re-quote of the item's wording, when the brief declares one. How identifiers are formed, assigned, retired, and which brief sections carry them is owned by [`../../brainstorming/references/handoff-brief-format.md`](../../brainstorming/references/handoff-brief-format.md) §Brief item identifiers; read the rules there. This file settles only that the id is a legal referent here — a second copy of the id rules would drift from the schema that owns them.

**Referent kind (d): a `REQ-<n>` id declared by an id-mode spec file's header, or the id-form join key `<change-id> / REQ-<n> / Scenario: <name>`.** A bare `REQ-<n>` (no `/ Scenario:` suffix) covers every scenario under that requirement (OQ-3, option A). The packaged [`requirement-identifiers.md`](requirement-identifiers.md) contract owns the identifier grammar; this file settles only that the id is a legal referent here.

**The no-requirement value.** `none — <reason>` is legal because a task that delivers no brief outcome — release administration, a version bump, a manifest mirror — must not be forced into a false citation: a citation naming an item the task does not deliver reads as satisfied to every downstream reader and to the coverage checker, which makes it worse than no citation at all. The reason is mandatory, and that is what keeps the value from becoming a silent opt-out — a bare `none`, an empty reason, or a whitespace-only reason is invalid. Task 9 of `docs/loom/plans/2026-08-13-brief-item-addressability.md` is this rule's own worked instance: the release-administration task that introduced the value uses it.

**Tie-break — one primary referent per task.** When a task plausibly delivers two brief items, the primary referent is the item the task's RED test asserts. The RED test is this repo's definition of done, so it is the least arbitrary anchor available; the rejected alternative — the item most of `Files touched` serves — tracks effort rather than outcome, and a task can spend most of its edits on the item it does not actually deliver.

### Stated facts — the pointer-not-copy rule (v0.39.0+)

A plan is a technical SSOT that nothing validates: every downstream station judges the artifact **against the plan**, so a fact the plan states wrongly is implemented faithfully, reviewed as conformant, and typically surfaces only at close-out — the most expensive point to catch it. This rule makes the copy unnecessary — it is not extra ceremony on top of it.

**Any verifiable technical assertion in a plan carries an anchor citation — the verbatim string or stable heading that locates it in the source.** A *verifiable technical assertion* is a sentence whose truth some existing artifact already settles: a number, a formula, a field list, a count, or a claim about existing behaviour (*"the helper already normalizes the ticker"*). Design intent, a preference, or an instruction to the implementer is **not** one and needs no citation. Cite the anchor that resolves — the verbatim string or stable heading; a line number is optional precision, written as `file:line`, required only when the anchor alone is ambiguous (the string occurs more than once in the file). Line numbers rot in flight — plan text rides dispatch packets (SDD hands Descriptions to implementers verbatim), and the anchor survives the rot a `file:line` does not (`../../subagent-driven-development/references/dispatch-hygiene-notes.md` §Dispatch-packet context rule (a): "Anchor by string, never by line number alone").

**Every citation pairs a source path plus an anchor.** Select the anchor by artifact type: prose uses a stable heading or distinctive phrase; code uses a function, class, or method signature, a constant, or a distinctive message; config/data uses a key path plus a distinctive value fragment.

The citation **replaces** the copy: point at the formula, do not retype it. A retyped formula drifts from its source while every test stays green.

**Escape — mark it, do not omit it.** An assertion whose source you have not opened is written as an explicit **unverified assumption**: a statement the author has *not checked* against any artifact, labelled inline so a reader never mistakes it for an established fact. Write it as `(unverified assumption — <what would settle it>)`. An unmarked guess reads identically to a verified fact; the label is the whole remedy.

**No citable source → produce the source first, as a task.** When the fact is load-bearing and nothing in the repo settles it, the source has to be **produced** — a probe, a measurement, a test. That is a **task in this plan, not a sentence in it**: give it its own task block with its own RED / GREEN, and have the tasks that rely on the fact declare `Dependencies` on it.

### Optional sections

```markdown
## Parent-child decomposition (only present if this plan is a BLOCKED fallback)

Parent task: <original task that returned BLOCKED>
Implementer's unblock_step: <quote>
Child tasks: 1, 2, 3 (listed above)
Parent declared DONE when all children DONE.

## Notes

(Free-form notes to SDD orchestrator — e.g. "Tasks 2+3 can run parallel after Task 1; Task 4 needs Task 2 only, not Task 3")
```

#### `Decision Log` plan section (v0.29.0+, optional)

Unlike `## Notes` (free-form, author-written), `## Decision Log` is
**runtime content**: `writing-plans` never authors it — a fresh plan has
no `## Decision Log` section — `subagent-driven-development` **appends to
it** during execution whenever an agent decides an engineering choice with
product stakes, and `plan-document-reviewer` **accepts and ignores it**,
mirroring the per-task `Status` field's reviewer-ignores contract (see
§Progress ledger above). The precise when-to-append trigger — the
two-axis test that adjudicates "product stakes" — is owned by
`subagent-driven-development`'s Decision Log maintenance clause; this
section only defines the record shape, not the trigger. This section's
jurisdiction is decisions, not open forks: an unresolved question does
not belong here — it belongs in `## Open Questions` instead.

One entry per agent-decided choice: one conceptual record format
(single-line, reason-bearing, cost-aware) shared with `product-principles`'
Deviation Ledger, but the two views use different marker idioms — the
Deviation Ledger's `— reason:`/`— principle:` vs this section's
`— cost-of-change:` (design SSOT:
`docs/loom/design/2026-07-10-designer-pm-loop-architecture.md:228`). Each
entry is a **single physical line — do not soft-wrap** (same reason as the
Deviation Ledger: a wrapped entry breaks downstream parsing).

```markdown
## Decision Log

N. chose <X> because <Y> — cost-of-change: the day you want <Z>, this choice costs <W>
```

Product language, no jargon — this is the record a non-engineer PM reads,
not a technical rationale. Worked example:

```markdown
## Decision Log

1. chose in-memory caching because it needs no new infra — cost-of-change: the day you want multi-instance sync, this choice costs a full cache-layer rewrite
```

**Placement rationale** (brief §Alternatives): plan-embedded, not a
standalone `docs/loom/decisions/` directory — the decision lives next to
the reasoning that produced it, and the plan is already the per-arc
artifact the user reads. **Reversal conditions** (recorded, user-approved):
switch to standalone `docs/loom/decisions/` if (a) >15-20 entries
accumulate in one arc, or (b) a cross-arc lookup need emerges ("did we
already decide this?").

Commit trailers remain the engineer-facing greppable index — this section
is the product-language narrative, not a replacement for trailers (two
views of one record format, not two competing records).

## Worked example

The canonical CSV-export plan below must stay the FIRST fenced markdown code block in this section — the plan-format test suite extracts it by taking the first such fence between this heading and the next `###`-level heading, so a subsection inserted ahead of it (e.g. a shorter example) breaks that extraction. Add new subsections after it, not before.

For a brief at `docs/loom/specs/2026-05-16-csv-export.md` whose Smallest End State is *"add `?format=csv` query param to the existing `/reports/<id>` endpoint":*

```markdown
# Plan: CSV export query param

**Source brief**: docs/loom/specs/2026-05-16-csv-export.md
Goal: users can export the orders list as CSV with the same filters the list view applies
Stage: planning
Steps:
  1. Understand the CSV request and produce the file format
  2. Connect them so the download actually happens
**Total tasks**: 3
**Critical-path depth**: 2 (≤5 ✓)
**Execution order**: sequential
**Plan-document-reviewer verdict**: PASS (2026-05-16 10:42)

## Task-flow diagram

<!-- mermaid flowchart LR of the Task 1 → Task 2 → Task 3 dependency DAG -->

## Open Questions

N/A — no unresolved question: brief left nothing undecided at plan time.

## Task 1 — Add format query param parsing to /reports handler

- **Description**: Accept `format=csv` query param in `GET /reports/:id`; default to `format=json` if absent or unrecognized.
- **Module**: `src/routes/reports.ts`
- **Files touched**: `src/routes/reports.ts`, `tests/routes/reports.test.ts`
- **Context paths**:
  - `/Users/kouko/proj/src/routes/reports.ts`
  - `/Users/kouko/proj/tests/routes/reports.test.ts`
- **Acceptance**:
  - **RED**: `reports.test.ts > GET /reports/:id?format=csv returns 200`
  - **GREEN**: query param parsed; passed to renderer; existing JSON path unchanged
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "minimum shippable change: `?format=csv` query param to existing report URL (no UI work)"
- **Status**: pending
- **Gloss**: The report URL starts understanding a CSV request — until it does, no export can be asked for at all.

## Task 2 — Implement CSV renderer for report payload

- **Description**: Convert the existing `ReportPayload` JSON shape to RFC 4180 CSV. Use `papaparse` (already in deps).
- **Module**: `src/renderers/csv.ts` (new file)
- **Files touched**: `src/renderers/csv.ts`, `src/renderers/csv.test.ts`
- **Context paths**:
  - `/Users/kouko/proj/src/types/ReportPayload.ts`
  - `/Users/kouko/proj/node_modules/papaparse/README.md` (API ref)
- **Acceptance**:
  - **RED**: `renderers/csv.test.ts > renderCSV produces RFC 4180-compliant output with quoted fields containing commas`
  - **GREEN**: CSV string matches RFC 4180 fixture; passes existing fuzz tests
- **Dependencies**: none
- **Independent**: true
- **Brief item covered**: "minimum shippable change: CSV output that downstream pipeline can ingest"
- **Status**: pending
- **Gloss**: Report data turns into a spreadsheet-ready file other tools can ingest — the thing the export exists to hand over.

## Task 3 — Wire renderer into handler + set Content-Type

- **Description**: When `format=csv`, call `renderCSV(payload)`, return with `Content-Type: text/csv; charset=utf-8`.
- **Module**: `src/routes/reports.ts`
- **Files touched**: `src/routes/reports.ts`, `tests/routes/reports.test.ts`
- **Context paths**:
  - `/Users/kouko/proj/src/routes/reports.ts` (modified by Task 1)
  - `/Users/kouko/proj/src/renderers/csv.ts` (produced by Task 2)
- **Acceptance**:
  - **RED**: `reports.test.ts > GET /reports/:id?format=csv returns text/csv body matching renderer output`
  - **GREEN**: end-to-end request returns valid CSV; Content-Type header correct
- **Dependencies**: Tasks 1, 2 complete first
- **Independent**: false  # touches files Task 1 also touches; must run after Task 1
- **Brief item covered**: "minimum shippable change: end-to-end CSV download path"
- **Status**: pending
- **Gloss**: Asking for CSV now actually downloads one — the moment the goal's export works end to end for a user.

## Notes

Tasks 1 + 2 are independent (disjoint `Files touched`) and can run parallel in `dispatching-parallel-agents`. Task 3 joins them sequentially because its `Files touched` overlaps Task 1's.
```

### Field-value grammar — before/after

Before, under the retired judgment-shaped wording — one unbroken line
that reads as "one assertion" to its own author, but its first line
runs to 312 characters, past the 300-character ceiling:

```markdown
- **Description**: Add rate limiting to the /export endpoint using a token-bucket algorithm keyed on user id, with a 429 response and a Retry-After header when the bucket is empty, matching the limiter already used on /reports so behavior stays consistent across endpoints, and update the OpenAPI spec to document the new 429 case.
```

After, under the positional rule — first line stays within the
300-character ceiling, the rest routes into nested bullets, each of
which stays within the same ceiling too:

```markdown
- **Description**: Add rate limiting to the `/export` endpoint.
  - Use the token-bucket limiter already used on `/reports`, keyed on
    user id, so behavior stays consistent across endpoints.
  - Return `429` with a `Retry-After` header when the bucket is empty.
  - Update the OpenAPI spec to document the new `429` case.
```

Moving the overflow into a nested bullet is not on its own enough — the
ceiling governs each bullet too, so a single long caveat rewrites the
same violation one level down:

```markdown
- **Description**: Add rate limiting to the `/export` endpoint.
  - Use the token-bucket limiter already used on `/reports`, keyed on user id rather than on IP because the export path is authenticated and shared NAT egress would otherwise starve whole offices, and note that the limiter's existing burst allowance was tuned for `/reports`' traffic shape so the export path may need its own bucket size once real usage lands.
```

That bullet's folded text runs past 300 characters and is rejected, even
though the field's first line is short. Split it the same way the first
line was split — one bullet per idea, a table when three or more items
share axes.

### Wide-but-shallow example — 8 tasks, critical-path depth 2

A high `Total tasks` count is **not** a discovery failure when the tasks fan out wide instead of chaining deep. Consider a brief whose Smallest End State is *"add a one-line module docstring to each of the 6 renderer files, then run the lint gate, then update the index":*

```markdown
# Plan: backfill renderer module docstrings

**Source brief**: docs/loom/specs/2026-05-20-renderer-docstrings.md
Goal: every renderer file carries a one-line module docstring so the lint gate stops flagging them
Stage: planning
**Total tasks**: 8
**Critical-path depth**: 2 (≤5 ✓)
**Execution order**: parallel-where-possible

## Task-flow diagram

<!-- mermaid flowchart LR of the Task 1-6 → Task 7 → Task 8 dependency DAG -->

## Open Questions

N/A — no unresolved question: brief left nothing undecided at plan time.

## Task 1 — Docstring for csv renderer   (Independent: true, Dependencies: none)
## Task 2 — Docstring for json renderer  (Independent: true, Dependencies: none)
## Task 3 — Docstring for xml renderer   (Independent: true, Dependencies: none)
## Task 4 — Docstring for yaml renderer  (Independent: true, Dependencies: none)
## Task 5 — Docstring for toml renderer  (Independent: true, Dependencies: none)
## Task 6 — Docstring for html renderer  (Independent: true, Dependencies: none)
## Task 7 — Run lint gate over all renderers (Dependencies: Tasks 1, 2, 3, 4, 5, 6 complete first)
## Task 8 — Regenerate renderer index doc   (Dependencies: Task 7 completes first)
```

Tasks 1-6 are **6 disjoint `Independent: true` leaves at one dependency level** — they count as **one level**, not six. The longest chain of tasks linked by `Dependencies` is `(any of 1-6) → 7 → 8`, so the **critical-path depth is 2**. Eight tasks, depth 2: a wide-but-shallow plan that validates cleanly and is **NOT** a discovery failure. It parallelizes the 6 leaves and joins them at Task 7. (Each per-task block above is abbreviated to one line for the depth illustration; a real plan expands every task to the full per-task schema.)

### `Review-weight: mechanical` example — 3 sibling tasks, identical one-line edit

Consider a brief whose Smallest End State is *"bump the copyright year string in each of 3 module headers from `2025` to `2026`, verbatim, no other changes":*

```markdown
## Task 1 — Bump copyright year in csv.ts header
- **Description**: In `src/renderers/csv.ts` line 1, replace the exact literal `// Copyright 2025` with the exact literal `// Copyright 2026`. No other changes.
- **Module**: `src/renderers/csv.ts`
- **Files touched**: `src/renderers/csv.ts`
- **Acceptance**:
  - **RED**: `csv.test.ts > header contains Copyright 2026` fails
  - **GREEN**: header line reads `// Copyright 2026`
- **Dependencies**: none
- **Independent**: true
- **Review-weight**: mechanical

## Task 2 — Bump copyright year in json.ts header
- **Description**: In `src/renderers/json.ts` line 1, replace the exact literal `// Copyright 2025` with the exact literal `// Copyright 2026`. No other changes.
- **Module**: `src/renderers/json.ts`
- **Files touched**: `src/renderers/json.ts`
- **Acceptance**:
  - **RED**: `json.test.ts > header contains Copyright 2026` fails
  - **GREEN**: header line reads `// Copyright 2026`
- **Dependencies**: none
- **Independent**: true
- **Review-weight**: mechanical

## Task 3 — Bump copyright year in xml.ts header
- **Description**: In `src/renderers/xml.ts` line 1, replace the exact literal `// Copyright 2025` with the exact literal `// Copyright 2026`. No other changes.
- **Module**: `src/renderers/xml.ts`
- **Files touched**: `src/renderers/xml.ts`
- **Acceptance**:
  - **RED**: `xml.test.ts > header contains Copyright 2026` fails
  - **GREEN**: header line reads `// Copyright 2026`
- **Dependencies**: none
- **Independent**: true
- **Review-weight**: mechanical
```

Each task is an identical one-line edit (same exact-spec literal-string replacement, different file) — the reproducible-from-exact-spec bar `Review-weight: mechanical` requires. Contrast with Task 3 in the CSV-export example above (`Wire renderer into handler + set Content-Type`): that task branches on `format=csv` and touches request-handling logic, so it must NOT declare `Review-weight: mechanical` even though it is a small task — logic changes always take the full triad.

**"Near-identical" — one bounded per-file substitution, not free-form variation.** The marker also covers tasks that are the *same template with one literal swapped per file from a fixed, plan-declared list* — e.g. three sibling tasks each inserting the identical pointer sentence `"See \`family-relay.md §Family relay discipline\`."` into a different skill's `SKILL.md`, where only the surrounding one-line anchor phrase differs per file (still a verbatim literal named IN the task, not left to the implementer's judgment). This is *not* license to mark a task mechanical because it merely "feels similar" to a sibling — "add error handling similar to how Task 2 does it" is NOT reproducible-from-exact-spec (the implementer must judge what "similar" means) and must NOT declare `Review-weight: mechanical`, even though it superficially resembles a batch edit.

### `Review-weight: mechanical` example — deterministic sync-script output

Consider a brief whose Smallest End State is *"re-sync `deep-read`'s functional copy of `prompts.py` from the `deep-deep-research` SSOT after a fix landed there, and mirror the plugin's version bump into its Codex manifest":*

```markdown
## Task 1 — Re-sync deep-read's prompts.py from SSOT
- **Description**: SSOT is `research-toolkit/skills/deep-deep-research/scripts/prompts.py`. Run `research-toolkit/scripts/sync-primitives.sh deep-read` (which copies that SSOT into `deep-read`'s own `scripts/`) and commit the result unmodified. No hand-written edits to the output.
- **Module**: `research-toolkit/skills/deep-read/scripts/prompts.py`
- **Files touched**: `research-toolkit/skills/deep-read/scripts/prompts.py`
- **Acceptance**:
  - **RED**: MD5 of `research-toolkit/skills/deep-read/scripts/prompts.py` differs from `research-toolkit/skills/deep-deep-research/scripts/prompts.py`
  - **GREEN**: MD5s match; `check-script-sync` CI job (or its local equivalent) passes
- **Dependencies**: none
- **Independent**: true
- **Review-weight**: mechanical

## Task 2 — Mirror plugin.json version bump into the Codex manifest
- **Description**: SSOT is `research-toolkit/.claude-plugin/plugin.json`. Run `python3 scripts/sync_codex_manifests.py research-toolkit` (which mirrors that SSOT's shared fields into the Codex manifest) and commit the result unmodified. No hand-written edits to the output.
- **Module**: `research-toolkit/.codex-plugin/plugin.json`
- **Files touched**: `research-toolkit/.codex-plugin/plugin.json`
- **Acceptance**:
  - **RED**: `test_check_codex_manifest_drift.py::test_real_batch_a_plugin_in_sync` fails (drift detected)
  - **GREEN**: same test passes
- **Dependencies**: none
- **Independent**: true
- **Review-weight**: mechanical
```

Both tasks' entire output is computed by a deterministic script from a named SSOT — there is no literal string to pre-quote in the Description the way the copyright-year example does, so the RED/GREEN pair names the **verification method** (a checksum comparison or the project's own paired drift-detection test) instead of a literal diff. That verification method is exactly what `subagent-driven-development/SKILL.md`'s mechanical self-check runs for this category — see its **Content match** step. For a straight-copy script like Task 1's, "diff the two existing files" and "re-run the script, diff its output" are the same check by construction (the script's only job is that copy); a script with side effects beyond a straight copy (e.g. one that also reformats or merges) would need the "re-run, diff output" framing specifically — the two framings are not interchangeable in general, only for this shape.

## Anti-patterns

- ❌ **Vague task descriptions.** *"Add CSV support"* is not actionable. *"Add `format=csv` query param parsing to `GET /reports/:id` handler"* is.
- ❌ **Multi-module task.** If `Module:` lists 2+ files, split. The implementer subagent's per-task scope is one module.
- ❌ **Missing acceptance.** A task with no RED test name has no done-condition. tdd-iron-law cannot fire on it. Always name the failing test.
- ❌ **Implicit dependencies.** If a task says *"also remember to update the OpenAPI spec,"* that update is a missing task. Declare it.
- ❌ **Tasks not traceable to brief.** Every task must cite a brief item — a quote, a change-folder join key, a `BI-<n>` id, or a `REQ-<n>` id. Orphan tasks are scope creep. The one exception is the declared `none — <reason>` value (see §`Brief item covered`); a bare `none` is an orphan task with a hat on.
- ❌ **Critical-path depth >5 with no fallback decision.** If the longest chain of tasks linked by `Dependencies` exceeds depth 5, route back to brainstorming OR split into multiple briefs. A deep chain is a discovery failure. Do not silently produce a deep sequential chain. (A wide-but-shallow plan — many `Independent: true` leaves, shallow depth — is fine; the ceiling counts depth, NOT total task count.)
- ❌ **Skipping plan-document-reviewer self-review.** `Plan-document-reviewer verdict: PENDING` means SDD blocks. Do not pass an unreviewed plan to SDD.
- ❌ **Claiming `Independent: true` with overlapping `Files touched`.** Independence requires disjoint write sets. If two tasks both declare `Independent: true` AND share any file in `Files touched`, the claim is wrong — fix the plan, not the dispatch. `dispatching-parallel-agents` will refuse to dispatch overlapping tasks regardless of the marker.

## See also

- [`../SKILL.md`](../SKILL.md) — the splitting framework + BLOCKED fallback flow.
- [`plan-document-reviewer-prompt.md`](plan-document-reviewer-prompt.md) — the evaluator subagent that PASSes / NEEDS_REVISIONs this schema.
- [`../../brainstorming/references/handoff-brief-format.md`](../../brainstorming/references/handoff-brief-format.md) — upstream brief schema.
- [`../../subagent-driven-development/SKILL.md`](../../subagent-driven-development/SKILL.md) — downstream consumer.
