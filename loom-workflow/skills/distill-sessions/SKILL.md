---
name: distill-sessions
description: |
  Mine past Claude Code and Codex session transcripts + /insights for friction patterns → a per-skill improvement-proposals doc. Use to audit skill-activation telemetry, or gather evidence before a refactor. For creating a skill use skill-creator-advance.
version: 0.5.2
---

# distill-sessions

Mine completed Claude Code and Codex sessions, join Claude `/insights`
facets when available, rank friction by existing Skill, and produce reviewable
SKILL.md proposals. The default target preset is `loom-code:*`; use
`--target-skill-pattern` for another scope. This is post-hoc evidence mining,
not real-time coaching or new-skill discovery.

## When to use

Use this skill after several changes to a skill family, before a skill
refactor, when recurring missed activations need evidence, or when MEMORY.md
has crossed its 24.4 KB soft cap and needs evidence-backed graduation
candidates. Typical requests include “mine my skill logs for loom-code,”
「最近の loom-code ログを掘って改善提案を出して」, and
「挖一下最近 loom-code 的 session log」.

Do not use it for:

- real-time coaching;
- a single-session reflection already served by `/insights`;
- discovering or creating new skills;
- taste-driven output tuning; or
- token-only refactors where output equivalence, rather than session evidence,
  is the objective.

## Bare invocation — preview, then confirm

When the user names no target, run only the local Stage 1 preview:

```bash
python scripts/main.py --target-skill-pattern 'loom-code:*'
```

Show the stderr summary (top skills and per-session friction) verbatim. Then
pause and confirm which subset to send to Step 2: the highest-friction skill,
top three, all, another target, or stop after preview. Do not infer approval
from invoking the skill: Step 2 sends session-derived text to paid subagents.
That approval necessarily occurs before Stage 3, which only collects results.

If any serialized dispatch input is projected above the 1M-token context
window (`len(json.dumps(payload.input)) // 4 > 1_000_000`), skip that
trajectory, warn the user, and recommend narrowing the filter before Step 2.
The observed maximum was 559K tokens, but that history does not waive the
check.

When the prompt already names a target, execute that scoped flow directly;
the explicit scope replaces the preview pause, not later approval or privacy
gates.

## Privacy and evidence boundaries

Local-only stages read `~/.claude/projects/**/*.jsonl`,
`~/.codex/sessions/**/*.jsonl`, and available
`~/.claude/usage-data/facets/*.json`. No network calls occur in `main.py`,
`propose.py`, or `apply.py`. Step 2 and the optional advisory report are the
only subagent dispatch steps, so their cost and data movement must remain
visible to the user.

For Codex, retain only observable user/assistant text, tool calls, and tool
outputs. Exclude reasoning records and encrypted reasoning content. A
`policy_stops[]` record requires both an observable user-facing stop/ask and a
policy reason; never infer a stop from hidden reasoning, generic risk language,
or a quoted rule. Claude events without a matching `/insights` facet still
participate through the friction heuristic.

## Workflow

### 1. Ingest, detect, and rank

```bash
python scripts/main.py \
  --target-skill-pattern 'loom-code:*' \
  [--config path/to/override.json] \
  [--top-n 5] \
  [--max-trajectories-per-skill 5] \
  > top.json
```

`main.py` joins available facets, detects interrupt-after-brainstorm,
tool-error clusters, NEEDS_REVISION streaks, and re-dispatch concentration,
then ranks skills by frequency, time cost, cross-project occurrence, and
recency. It emits `top_skills[]` plus per-trajectory `subagent_payload[]`.
Trajectory ids are deterministic UUID5 values over skill, session, and kind.

A high-friction session whose facet says success creates both failure- and
success-analysis dispatches. Therefore `--max-trajectories-per-skill` counts
dispatches, not sessions.

### 2. Dispatch per trajectory

After the bare-invocation confirmation (or with explicit initial scope), read
`top.json` and dispatch one independent subagent per payload. Use
`agents/prompt-failure-analysis.md` or
`agents/prompt-success-analysis.md` according to `kind`, include the target
SKILL.md body and observable session events, and use the current Sonnet
generation. Fan out only disjoint trajectories.

Each subagent returns the strict-markdown Memory Item shape defined by its
prompt. Do not ask it for JSON. Claude Code dispatch uses the harness alias
`sonnet`; the literal `claude-sonnet-4-6` is metadata and fails Claude Code's
dispatch enum. Codex uses its host-specific dispatch mechanism.

### 3. Collect `merged.json`

Mechanically convert each returned Memory Item into `memory_items[]`, carrying
the source `session_id` and `target_skill_path`. Every item needs `title`,
`description`, `content`, `kind`, and a non-blank `section_anchor` that names a
real target heading. `requires_new_reference_file` is optional and defaults to
false.

Do not silently default a missing anchor to `Examples`. Invalid anchors must
remain visible for review. The canonical schema, conversion procedure, and
host-specific dispatch forms are conditional runtime details: read
[references/runtime-protocol.md](references/runtime-protocol.md) when
performing Stage 2, converting Memory Items, running the advisory report,
changing configuration thresholds, or diagnosing folder/runtime failures.

### 4. Render proposals

```bash
python scripts/propose.py \
  --input merged.json \
  --target-skill /path/to/target/SKILL.md \
  --output docs/skill-mining/<date>-<target>-proposals.md
```

Before rendering, `propose.py` clusters normalized title plus section anchor.
Items supported by at least two sessions become proposed additions or
modifications. Single-session evidence remains under “Cross-session evidence
pending.” Dead anchors appear under “Anchor mismatch — needs review,” and
items requiring a new reference file remain visibly deferred. None of these
buckets may be silently discarded.

The proposal is the required per-target artifact. It is review material, not
authorization to edit a Skill.

### 5. Human review and approval-gated application

The user must complete a Human review of each proposed addition and
modification. Only after explicit approval run:

```bash
python scripts/apply.py \
  --proposal docs/skill-mining/<date>-<target>-proposals.md \
  --target-skill /path/to/target/SKILL.md \
  --approved
```

`apply.py` must refuse without `--approved`, refuse writes under
`references/`, and require exact section-anchor plus contiguous old-text
matches. It writes atomic updates using a temporary file, `fsync`, and replace;
failure must leave the target unchanged. Approval is an intent gate even for
an empty proposal, not an environment override.

Final verification requires confirming all expected `top.json`,
`merged.json`, and proposal artifacts exist, reviewing the proposal rather
than trusting exit status, and running the relevant tests before claiming the
workflow complete. Stop rather than bypass any approval, anchor, privacy,
overflow, or write-boundary refusal.

## Optional advisory report

After `merged.json` exists, a cross-target report can complement per-target
proposals:

```bash
python scripts/report.py \
  --input merged.json \
  --lang zh-TW \
  [--output docs/skill-mining/<date>-advisory-report.md] \
  > dispatch_payload.json
```

`--lang` is mandatory and accepts `zh-TW`, `en`, or `ja`. The command creates
a dispatch payload; it does not write the analyst's prose. Read the advisory
prompt, dispatch one current-Sonnet subagent with
`dispatch_payload.input`, then write its returned markdown verbatim to the
reported `output_path`. Do not add a preamble or edit the response. Skip this
surface when only per-target proposals are needed.

## Configuration and operating invariants

`--config` accepts a partial JSON object merged over six defaults:
`interrupt_window_sec=600`, `needs_revision_threshold=2`,
`redispatch_threshold=2`, `tool_error_proximity_events=10`,
`min_session_count=3`, and `cross_project_count=2`. Use JSON; the scripts are
stdlib-only. Read the runtime protocol before interpreting or changing these
thresholds.

Preserve these invariants:

- When several target skills occur in one session, attribute a Memory Item to
  the highest signal-severity pair; alphabetic order is only the tie-break.
- Single-session items are pending evidence, not errors. Leave them reviewable
  until another run supplies corroboration.
- Claude `/insights` facets may disappear after the configured retention
  period (commonly 30 days). Mine what is present; this skill does not archive
  facets or claim absent facets existed.
- `/insights` is interactive-only. Sessions without facets remain eligible via
  observable friction signals.
- The per-trajectory model is locked by `scripts/main.py`; an operator may
  choose a different model only at the confirmed orchestration boundary.
- `main.py`, `propose.py`, and `apply.py` remain local and deterministic. LLM
  judgment belongs only in the declared subagent stages.
- Proposal application changes SKILL.md only. It must not turn a mined idea
  into a new reference file or another agent-instruction surface.

Run Python tests with bytecode disabled so the skill-folder structure stays
valid:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest \
  loom-workflow/skills/distill-sessions/scripts/ -v
```

If `__pycache__` appears, use the non-destructive two-pass `find -delete`
procedure in the runtime protocol; do not use recursive removal shortcuts.

## Artifact contract

Treat the three intermediate files as a chain of evidence, not interchangeable
scratch output. `top.json` records what the deterministic miner observed and
which trajectories it proposed for dispatch. Keep its stdout separate from the
human preview on stderr; mixing them makes the dispatch input invalid.
`merged.json` records what the approved subagents returned after the mechanical
markdown conversion. It must retain each source session id and target path so
cross-session support can be audited. The per-target proposal records the
promotion decision and is the only input `apply.py` may use for Skill changes.

Before leaving each stage, verify its output can be parsed by the next stage.
An empty but valid result is different from a missing or malformed artifact:
report the former as “no qualifying evidence” and stop cleanly; report the
latter as a failure that needs repair. Never manufacture placeholder Memory
Items to keep the pipeline moving. Preserve run-local artifacts until the user
has reviewed the proposal or chosen to stop, because they are the evidence for
why an edit was suggested.

The proposal must expose all four outcomes: supported additions, supported
modifications, anchor mismatches, and single-session evidence pending. The
deferred-reference bucket is also required whenever an item requests a new
file. A zero-count section may remain explicit; deleting a non-empty bucket is
behavior loss because the user can no longer audit excluded evidence.

## Signal interpretation

Signals identify review candidates; they do not prove that a Skill is wrong.
An interrupt after brainstorming may reflect a changed user priority. A tool
error cluster may belong to the environment. A NEEDS_REVISION streak may
indicate a difficult task rather than weak instructions. Preserve the source
events and let cross-session recurrence raise confidence instead of converting
one event directly into policy.

Use the four-axis rank only to decide review order. Frequency asks how often a
pattern recurs; time cost estimates its practical drag; cross-project spread
reduces the chance of a repository-specific explanation; recency keeps old,
already-fixed behavior from dominating. Do not reinterpret the score as
severity, probability, or authorization to edit. When two target skills share
a session, the signal weights choose attribution so one Memory Item is not
duplicated across every invoked Skill.

Success trajectories matter alongside failures. A high-friction successful
session is deliberately analyzed twice: the failure prompt asks what caused
avoidable work, while the success prompt asks what existing instruction helped
recovery. Keep both dispatches and distinct trajectory ids. Merging them before
analysis would erase the difference between a guardrail worth preserving and a
friction source worth changing.

Policy-stop extraction is deliberately conservative. Accept only an assistant
message that visibly asks or states a stop and also gives the policy reason.
Do not classify explanatory discussion, quoted instructions, generic mentions
of privacy, or tool internals. This protects the privacy analysis from relying
on records an operator could not inspect.

## Dispatch and collection discipline

Dispatch only after the Step 2 scope is approved. The preview choice controls
which trajectories leave the local-only portion of the workflow; it does not
authorize broader logs, a different target pattern, or later write-back. If a
chosen trajectory would exceed the context estimate, omit it from the fan-out
and identify it in the user-facing summary. Do not truncate the trajectory
silently, because a partial session can invert the apparent cause of friction.

Give every analysis subagent only its own payload, the matching analysis
prompt, and the current target SKILL.md. Do not add the desired conclusion,
suspected change, or other trajectories’ results. Independent inputs keep the
fan-out parallel and prevent one analysis from anchoring another. A subagent is
an analyst here: it returns Memory Items and does not edit repository files,
issue verdicts, or invoke `apply.py`.

At collection time, parse the prompt-defined headings literally and reject an
incomplete item. Copy title, description, and content without rewriting them;
attach `kind` from the selected prompt rather than guessing it from prose.
Resolve `section_anchor` against the current target headings. If an anchor is
wrong, retain it for the mismatch report instead of silently choosing the
nearest heading. These rules make `merged.json` reproducible from the visible
subagent returns.

When the same session produced failure and success items, keep both records.
When repeated items support the same normalized title and anchor, clustering
may promote them; it must still preserve their session support. A single
session cannot satisfy the cross-session threshold by producing two similar
items.

## Proposal review discipline

Review proposals as evidence-backed hypotheses. For each addition, verify the
target heading exists and the text changes a future agent’s decision. For each
modification, compare the exact old lines with the current file and check that
the replacement does not broaden authorization or remove an important
boundary. For pending items, decide whether more sessions are needed; do not
promote them merely because they sound plausible. For anchor mismatches,
re-route manually only after identifying the intended section.

No proposal may directly modify `references/`, agent instructions, global
rules, or another Skill. A Memory Item requesting such scope remains in the
deferred bucket for a separately authorized task. Likewise, the optional
advisory report is explanatory output. Its cross-target recommendations are
not an approval token for `apply.py`.

Before running `apply.py`, show or otherwise establish the exact proposal the
user approved. If the target changed after review, exact-match validation must
refuse rather than rebasing the suggestion automatically. Re-render or review
again against the new target. After a successful atomic replacement, inspect
the resulting section and run the relevant Skill and plugin tests. “Command
returned zero” is insufficient if the approved change is absent, misplaced, or
causes a reference failure.

## Completion evidence

A complete run reports the selected target and trajectory count, which inputs
had facets, which overflow or validation exclusions occurred, and the paths to
`top.json`, `merged.json`, and every proposal. If the advisory report was
requested, also report its locale and output path. Do not claim a full run when
the user stopped at preview; call that outcome “preview complete, dispatch not
approved.”

For an applied proposal, final verification includes the approval gate, exact
anchor/diff match, atomic write, and relevant tests with no failures or skips.
For a review-only run, completion means the proposal is renderable and all
pending, mismatch, and deferred evidence remains visible. In either mode,
state excluded trajectories and unavailable facets rather than treating them
as analyzed. This keeps the result bounded by observable data and the scope the
user actually approved.

## Stop conditions

Stop and surface the reason when:

- the target is absent or ambiguous after preview;
- the user declines Step 2 dispatch or proposal application;
- a trajectory exceeds the 1M-token estimate;
- input would include hidden or encrypted reasoning rather than observable
  records;
- a required prompt, target SKILL.md, `top.json`, or `merged.json` is missing;
- a Memory Item lacks required fields or has an unresolved anchor;
- `apply.py` refuses approval, path, anchor, or diff validation; or
- any relevant test fails or is skipped.

Do not convert a refusal into a best-effort write. Preserve partial artifacts
for inspection and state what the user must decide or repair next.

## References

- [Runtime protocol](references/runtime-protocol.md) — Read it when performing
  dispatch, markdown-to-JSON conversion, advisory rendering, threshold
  interpretation, or runtime cleanup. It contains conditional schemas,
  per-host mechanics, history, and troubleshooting rather than default-path
  policy.
- `agents/prompt-{failure,success}-analysis.md` — strict Memory Item output
  contract.
- `agents/prompt-advisory-analyst.md` — advisory report role and template.
- `scripts/propose.py:32-49` and
  `scripts/fixture_subagent_results.json` — executable schema SSOT.
- `docs/loom/specs/2026-05-22-distill-sessions-v0.1-brief.md` — original
  decisions and empirical threshold derivation.
