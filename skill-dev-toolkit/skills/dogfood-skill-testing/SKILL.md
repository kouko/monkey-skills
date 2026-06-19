---
name: dogfood-skill-testing
description: |
  Blind behavioral test of a drafted SKILL.md: does it fire when expected (not over-fire), and does its workflow meet its contract on real input? Use for 'dogfood this skill' or 'will it fire before I ship'. For static scoring use skill-judge.
version: 0.1.0
---

# Dogfood Skill Testing

## Overview

**A bad SKILL.md doesn't throw an error — it just never gets invoked.**
A skill defect is rarely a crash; the dominant failure mode is *silent*.
The skill never fires, fires for the wrong request, or produces
valid-looking output that is domain-wrong — and a green grader or a
passing structural check sees PASS while the skill is broken in practice.

This skill fills the **black-box exploratory behavioral** gap that its
siblings leave open. `skill-judge` scores a SKILL.md *statically* (reads
the file, never runs it). `skill-creator-advance` runs a *white-box*
conformance eval against the author's own known prompts. `distill-sessions`
mines *past* session logs for activation telemetry. None of them unleashes
a fresh agent that does **not** know the author's intent and actively
probes a skill-in-development to surface the unanticipated defects no
author-written test prompt covers.

The dogfood tests **two co-equal dimensions**:

- **Triggering** — does the skill fire when it should (no `trigger-miss`)
  and *not* fire when it shouldn't (no `over-trigger`), measured against a
  distractor set.
- **Output quality** — does the workflow, run end-to-end on real /
  realistic input, produce an artifact that meets the skill's **own
  declared contract** plus a domain bar (catching `workflow-drift`,
  `gate-bypass`, and `valid-but-wrong` output).

**Input** — a path to a skill-under-test directory in the working tree
(an un-installed, raw `SKILL.md` + its bundle). **Output** — a
fix-actionable findings report written to disk: each finding localizes the
defect to a SKILL.md section / bundled file, cites the probe prompt + the
subagent transcript that proves it, and names a suggested edit class. The
user reviews the surfaced raw test outputs (the human is the final
calibrator), then hands the report to the main agent to apply the fix —
this skill discovers and points; it does not auto-fix.

## Bundled resources

Both files resolve relative to this skill directory (one level deep,
flat-folder convention):

- `references/defect-taxonomy.md` — the severity (Critical / High /
  Medium / Low) × category (Trigger-miss / Over-trigger / Cold-start /
  Workflow-drift / Gate-bypass / Jargon-leak / Convention-violation /
  Progressive-disclosure / Output-quality) classification, each category
  annotated with the measured community frequency where known so the
  dogfood agent probes the high-base-rate defects first.
- `templates/dogfood-report-template.md` — the output report structure:
  metadata header → severity summary table → per-finding blocks (probe /
  expected / actual / transcript evidence / root cause / location /
  suggested fix) → Raw outputs appendix.
- `trigger-eval.json` — a ready-made trigger corpus (`query` +
  `should_trigger` pairs, zh-TW/ja/en). It is this skill's own self-dogfood
  corpus **and** the format + starter for Probe A's corpus — extend it for
  the target rather than building one from scratch.
- `NOTICE` — upstream-inspiration provenance (the `agent-browser` dogfood
  pattern, Apache-2.0; no code copied).

## Workflow

Six phases — a substrate-swapped port of the `agent-browser` dogfood
**pattern** (`agent-browser` = Vercel Labs' web-app exploratory-QA tool
whose `dogfood` skill explores an app to find bugs; here the substrate is a
skill-under-test, not a web app; no code copied — see this skill's
`NOTICE`). The target is a **raw working-tree skill**, never installed.
Run the three probes (below) inside Phase 4; append findings as you go.

1. **Initialize.** Locate the skill-under-test directory in the working
   tree (the `<skill-dir>` the user names). Read its `SKILL.md` and
   **split frontmatter from body**: the `description:` field is the
   *blind context* (all the router sees), the body is the *informed
   context*. Enumerate every bundled file (`references/`, `templates/`,
   `scripts/`, `assets/`, …). Create the output dir
   `docs/skill-dogfood/<date>-<skill>/` and copy
   `templates/dogfood-report-template.md` into it as `report.md`.
2. **Build probe contexts.** Assemble two firewalled context bundles:
   *blind* = the `description` only, plus a **distractor menu** (defined
   next). *informed* = the full body + every bundled file.

   **Distractor set** — 3–6 *sibling* skills whose descriptions claim the
   most **adjacent** jobs to the target (the ones a router is most likely
   to confuse it with). Not a global constant: **select per target** by
   nearest-neighbour on the description — same plugin first, and the
   siblings the target's own "Do NOT use for" clause already names are
   prime picks. Over-trigger only exists *relative to the alternatives
   present*, so without distractors it is undetectable. *Worked example* —
   to dogfood **this** skill, the set is its five nearest siblings:
   `skill-judge`, `skill-creator-advance`, `distill-sessions`,
   `skill-refactor`, `skill-tuning`.
3. **Orient.** Derive the **probe matrix** from the skill itself, before
   probing: its intended triggers (should-fire), near-miss requests that
   should NOT fire, its workflow steps, its declared gates, and its stated
   conventions. This matrix is what each probe asserts against.
4. **Run the three probes** (Probe A / B / C below) via fresh `Agent`
   subagents and Bash. Each probe is context-firewalled from the others.
5. **Document.** Append each finding to `report.md` **immediately**, with
   transcript evidence — the probe prompt + the subagent's actual reply
   excerpt that proves the defect. Never batch findings to the end (you
   lose the evidence and drift toward asserting from memory).
6. **Wrap up.** Tally severity counts into the summary table, write the
   Raw outputs appendix, finalize the report. Do not stamp any pass
   verdict (see Method → floor-not-ceiling).

## The three probes

### Probe A — Activation harness (does it trigger?)

Measures trigger precision against a distractor set. Catches
`Trigger-miss` and `Over-trigger`.

**PRIMARY — real-harness sandbox.** Copy the working-tree skill plus the
**distractor set** (defined in Phase 2) into a temp
`.claude/skills/`. For each corpus query, run the router for one turn and
parse the JSONL stream for `Skill()` tool_use events to decide fired /
didn't-fire:

```bash
claude -p "$QUERY" --max-turns 1 \
  --allowedTools Skill --output-format stream-json | tee run.jsonl
# fired? — any Skill tool_use appears in the stream:
grep -q '"name":"Skill"' run.jsonl && echo FIRED || echo "did not fire"
# which skill did it route to? — pull the Skill tool_use input:
jq -rc 'select(.type=="assistant") | .message.content[]?
        | select(.type=="tool_use" and .name=="Skill") | .input' run.jsonl
# (exact JSON path can vary by CLI version; the object you want is a
#  tool_use block whose name is "Skill" — its input names the routed skill.)
```

Corpus shape: **≈20 should-fire + ≥5 should-NOT-fire** queries, **≥2 runs
each** — routing is non-deterministic, so *average across runs; never
conclude from a single run*. Start from the shipped `trigger-eval.json`
format (the should-NOT entries should map to the distractor skills) and
extend it for the target. Compute the **true-positive rate** (1 −
miss) and **true-negative rate** (1 − over-trigger). A should-fire query
that routes to a distractor, or a should-NOT query that fires the target,
is a finding.

**FALLBACK** (no `claude` CLI / no API key): inject the `description`
into a fresh subagent's synthetic skill-menu alongside the distractor
descriptions and ask which one it routes to. Mark every finding from this
path `fidelity:approximate` — it approximates, it does not equal, the
live harness.

### Probe B — Executor + blind auditor (is the output good?)

Output quality is a **first-class peer of triggering**, not an
afterthought. Two firewalled subagents. Catches `Workflow-drift`,
`Gate-bypass`, `Convention-violation`, `Output-quality` (valid-but-wrong),
and integration crashes.

- **executor (informed):** given the full SKILL.md body + bundle, runs
  the skill **end-to-end on real / realistic input**. *Derive that input
  from the skill itself* — take a representative task from its own
  description or one of its should-fire trigger phrases. If realistic input
  is a **bulky external artifact** (an EPUB, a warehouse schema, a 500-row
  dataset), use a **minimal real fixture** — a 1–2 page / ~10-row slice of a
  genuine artifact (redact if sensitive), never a fabricated one: sample
  *fidelity* matters more than size, and a fabricated input hides the
  valid-but-wrong bugs you are hunting. Told explicitly: *"the user has NOT
  installed this plugin — execute as if invoked."* If the skill has a config / setup
  concept, **force its cold-start / fallback branch** (no config present) —
  highest bug density, least exercised; skip this step for skills that have
  no config concept.
- **auditor (blind):** given **only the executor's produced output** plus
  a domain-expert persona. Told: *"you have NO context about how this was
  produced."* Its rubric = **the skill's OWN declared contract** (the
  success criteria / gates / output format the skill claims) **plus a
  domain standard** (factual correctness, no fabrication, no leakage). So
  it catches BOTH *"failed its own declared bar"* AND *"met its bar but is
  domain-wrong."*

**LLM-as-judge guardrails (load-bearing):** judge against the rubric, NOT
against intent re-inferred from the artifact (the *oracle problem* — a
judge that reads the buggy output infers the buggy intent). Run the
auditor **≥2×** and **pin the model version** — treat a single run as
variance, not verdict. Judge the **trajectory** (the executor's steps),
not only the final output — correct output can mask broken reasoning. Use
**coarse score buckets**, not fine scales.

### Probe C — Blind cold-reader (can a first-timer read it?)

A fresh **zero-context** subagent reads the `SKILL.md` as a first-time
user. This is the single highest-yield technique — it defeats **bias
accumulation** (the in-session dev agent treats its own jargon as
baseline; the cold-reader cannot). Catches `Cold-start` and `Jargon-leak`.

Fixed question set: *Is it self-contained (could you act without asking
the author)? Which requests would trigger it — name 2 you're unsure
about? Is each mode's procedure executable as written? Which terms are
undefined?* Every "I don't know / undefined / I'd have to ask" is a
finding.

## Method

Load-bearing one-liners — codified from real dogfood practice, kept inline:

- **Firewall.** The executor is informed; the auditor is blind to how the
  output was produced. Self-grading is blind to its own blind spots — a
  fabricated citation passes a format-only self-check; only a blind
  auditor catches it.
- **Floor, not ceiling.** A structural / green-grader (an automated
  PASS/FAIL check) pass is necessary, never sufficient. **NEVER stamp "dogfood-pass" when a behavioral probe
  was skipped or deferred** — that is the exact anti-pattern this skill
  exists to refuse.
- **Real data, then execute.** Synthetic + static-pass gives false
  confidence; the dangerous bugs (valid-but-wrong numbers, integration
  crashes) only surface when the real workflow runs on real input and the
  artifact is judged.
- **Axis-sweep: predict-then-execute.** Each round, name the
  highest-risk *untested* axis (input shape / language / data grain
  [row-level vs aggregated] / semantics / cold-start), **predict the
  failure before running**, then
  execute to confirm. Rotate to a fresh axis when one is exhausted.
- **Force the fallback path.** Run with no config folder present —
  highest bug density, least exercised.
- **Environment guards.** Pin to `origin/main` (a worktree inherits stale
  branch state — a subagent once recommended a deleted skill). Post-run,
  `grep` any recommended skill slug against the current skill folder.
  Flag **meta-dogfood** familiarity bias (dogfooding a skill you authored
  yourself inflates confidence) and triangulate against an external skill.
- **Human is the final calibrator.** The auditor's verdict is a draft,
  not gospel — LLM judges share the agent's blind spots. Surface the raw
  outputs so the user can judge for themselves.

## Output

Write the report to `docs/skill-dogfood/<date>-<skill>/report.md`,
structured per `templates/dogfood-report-template.md`. Classify every
finding by severity × category via `references/defect-taxonomy.md` (probe
the high-base-rate defects first).

Every finding is **fix-actionable** and **advisory** — dogfood discovers
and points; the main agent decides and applies the edit. Each finding
carries: severity · category · pass[blind|informed] (which context bundle
surfaced it) · probe prompt ·
expected · actual · **transcript evidence** (the excerpt that proves it) ·
**root cause** · **why static review missed it** (what a structural /
self-grade check sees as PASS while this is broken — the floor-not-ceiling
signal) · **location** (`SKILL.md:§section` or `references/<file>`) ·
**suggested fix direction** (the edit class — e.g. "add trigger token 'X'
to the description's first line"; "§Workflow step 3 says 'verify' but not
how → spell out the check") · repro.

**Surface the raw outputs.** The report appendix collects every executor
artifact, every probe transcript excerpt, and each activation run's
query → fired/didn't — so the user reviews what the auditor actually
judged. **No embedded feedback form**: the report is a conversational
handoff artifact. The user reads the surfaced outputs, then talks to the
main agent directly to drive the fix.

## When NOT to use

- **Static design scoring** of a SKILL.md → `skill-dev-toolkit:skill-judge`
  (reads the file, does not run it).
- **Author-conformance eval** against the author's own known prompts, or
  creating/redesigning a skill → `skill-dev-toolkit:skill-creator-advance`.
- **Retrospective activation telemetry** from past session logs → a
  session-log mining tool (out of scope for this behavioral dogfood).

## Red flags

Refuse these rationalizations — they defeat the purpose of a behavioral
dogfood:

- *"The structural tests pass, so the skill is fine."* — Floor, not
  ceiling. Structural pass ≠ behavioral pass.
- *"I'll just read the SKILL.md and judge it."* — That is `skill-judge`
  (static). A dogfood **runs** the skill through blind subagents; reading
  it yourself re-introduces the bias accumulation the cold-reader exists
  to defeat.

