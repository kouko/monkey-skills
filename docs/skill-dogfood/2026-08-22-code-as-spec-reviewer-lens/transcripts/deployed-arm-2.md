# Deployed arm 2 — `loom-code:code-reviewer`, sonnet, 2026-08-22

Dispatched as the registered agent type, after `plugin update` to 0.93.0.
8 tool calls.

## Verdict block (verbatim)

```
standards_version: "0.93.0"

verdict: NEEDS_REVISION

dimension_scores:
  security: PASS
  architecture: PASS
  correctness: NEEDS_REVISION
  naming: PASS
  tests: PASS
  refactoring: PASS
  cross-task-coherence: PASS
  external-surface-grounding: PASS
  principles-conformance: N/A
  deliberate-simplification: PASS
  deletion-first: PASS_WITH_NOTES

findings:
  - severity: 🔴 fatal
    dimension: correctness
    where: mod.py:42-44
    source: rubrics/quality-gate.md §Correctness & Logic
    note: >
      The added sentence "A record whose `label` disagrees with its filename really does
      surface here under the filename stem, so the stem is the string a scheduler must
      match against" is factually wrong. `display_label` returns `header.get("label",
      record.stem)` — the stem fallback fires only when the `label` key is ABSENT, not
      when it disagrees with the filename. Verified by execution: a record at
      `bar.txt` with header `label: foo` returns `"foo"`, not `"bar"`. A caller who reads
      this docstring and matches a scheduler against the filename stem in the
      "disagrees" case will match the wrong string — the sentence tells a reader to do
      the wrong thing, meeting the 🔴 bar (`arch-gate.md` §D10's correctness route:
      "🔴 fatal when a caller acting on the sentence would do the wrong thing").
    origin: none
    evidence_needed: craft

  - severity: 🟡 should-fix
    dimension: correctness
    where: mod.py:51-53
    source: rubrics/quality-gate.md §Correctness & Logic
    note: >
      "Negative values are rejected rather than clamped" is misleading for the only
      reachable path. `_RETRY_RE = re.compile(r"^retries:\s*(\d+)\s*$")` requires
      `\d+` right after the colon, so a header line like `retries: -5` never matches —
      the key is simply absent from `parse_header`'s output, and `retry_budget` falls
      through to `DEFAULT_RETRIES` (3), silently. Verified by execution: a record file
      containing `retries: -5` returns `retry_budget() == 3`, no `ValueError` raised.
      The `raise ValueError` branch this docstring describes is reachable only by
      handing `retry_budget`'s internals a pre-built dict with a negative string
      directly — not via the file-parsing path a reader of this docstring would assume.
      Not 🔴 because no caller currently branches on the exception; 🟡 because a reader
      or a future test could reasonably assume file input `-5` raises, and it silently
      doesn't.
    origin: none
    evidence_needed: craft

  - severity: 🟡 should-fix
    dimension: deletion-first
    where: mod.py:40
    source: rubrics/arch-gate.md §Deletion-First Scoring
    note: >
      "Read the record, parse its header, and return the `label` key." is pure
      mechanism the two-line function body already shows (`parse_header(...)` then
      `.get("label", ...)`). Per the Code-as-spec lens this is a stale-claim-waiting-
      to-happen and should be deleted; the smaller shape is simply dropping this first
      sentence and keeping the docstring focused on the (corrected) label/filename
      behavior.
    origin: none

  - severity: 🟡 should-fix
    dimension: deletion-first
    where: mod.py:26-27
    source: rubrics/arch-gate.md §Deletion-First Scoring
    note: >
      "Keys absent from the text are absent from the result" is mechanism the code
      already shows (`if m: out[key] = ...`, nothing written when the regex doesn't
      match) — flag only this clause for deletion. The trailing reason clause,
      "since a missing key and an empty one mean different things to `retry_budget`",
      is not deletable (it is the non-obvious *why*, not a restatement of *what*) and
      must survive the edit; after deletion the sentence should read "...since a
      missing key and an empty one mean different things to `retry_budget`" with a
      new lead-in, or be merged into the paragraph above it so it isn't left stranded
      without a subject.
    origin: none
```

(The `summary:` block is omitted here; its content is reflected in the
grading note below.)

## Contract-source follow-up (verbatim, second turn)

Asked which absolute paths it opened, and to quote its own contract:

> **(a) My own role contract / agent definition** — I did not open it via a
> file Read tool call — it was not fetched from disk during this session. The
> full text (the `code-reviewer` subagent definition, including the
> baseline/reviewer-discipline/rule-sheet injected blocks) was already present
> in my system prompt when the task began.

> **"Code-as-spec" — verbatim check.** Yes, my role contract contains this
> phrase, in two places: Role-contract item 7 — *"Read §D10's Code-as-spec
> lens before flagging — jurisdiction, two filing routes, a second half, two
> reversing cases, and a duty to run what survives."* — and the §D10
> subsection header itself.
>
> The one sentence that tells me when a prose sentence must be deleted, quoted
> verbatim from role-contract item 7:
>
> > "For every changed sentence describing a mechanism, ask: can the code show
> > this? When it can, flag it for deletion — a mechanism sentence the code
> > already proves is a stale claim waiting to happen."

Rubrics it opened: `~/.claude/plugins/marketplaces/monkey-skills/loom-code/`
(the marketplace clone, `6e0a835` = PR #722's squash, `plugin.json` version
`0.93.0`) — `skills/subagent-driven-development/rubrics/{quality-gate,arch-gate}.md`
and `checklists/security-checklist.md`.

**This is the deployment evidence.** The quoted item-7 sentence occurs 1× in
0.93.0's `agents/code-reviewer.md` and 0× in 0.92.0's — and the agent read it
from its injected system prompt, not from disk. The dispatch layer delivered
the new contract.

## Grading note

Caught both surplus-class plants (`a` and `d`), and on `d` preserved the
reason clause exactly as the lens's second half requires — including naming
the stranding risk the deletion would create. This is the behaviour the lens
was written for. Arm 1, same contract, same model, same diff, filed none.
