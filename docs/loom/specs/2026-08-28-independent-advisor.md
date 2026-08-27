# Brief: independent-advisor — cross-executor second opinion

Author: kouko (session 2026-08-28)
Change-folder: `docs/loom/2026-08-28-independent-advisor/`

## Design-side on-ramp

fired: rows 3 — user chose detour

## Queue relation

unqueued — arc opened directly from the 2026-08-28 session; no live `bet` entry claims it

## Problem

When I have just settled on a plan or an architectural decision, I want a second
opinion produced by a DIFFERENT executor — a stronger model, a higher effort
level, or another vendor — so I can find the flaw my own reasoning chain is
blind to before I spend real time building it.

## Users

kouko, working in Claude Code or Codex CLI on this machine, at two moments:
before committing to an approach (the solution space is still open), and before
shipping (the work exists and the question is whether it will break). Both
`codex` and `claude` CLIs are installed and authenticated here; a consuming repo
may have neither, one, or both.

## Smallest End State

One skill at `loom-workflow/skills/independent-advisor/` that runs the core loop
end to end on this machine:

1. routes to `explore` (three roles) or `audit` (single leg), from a citable
   fact, with the basis stated in one line and user override honoured;
2. detects candidate executors statically (free), and never offers one that
   failed the static check;
3. presents ONE checkpoint carrying leg count, executors, estimated cost, and
   the egress disclosure — that the packet is what was inspected and the
   executor's readable range is larger;
4. live-probes only an executor the user selected, judging success on the
   executor's self-reported model/effort rather than a pipeline exit code, and
   failing loud rather than silently downgrading a `frontier` request;
5. dispatches the legs, holding Leg A blind to the incumbent, normalising both
   proposals to one template, and running the blind judge under BOTH card
   orders;
6. returns a report led by divergences, disclosing degraded or failed legs,
   actual cost, and the standing limitation that agreement between legs reading
   one sample measures the sample, not the world.

## Current State Evidence

- Forward — `loom-workflow/.claude-plugin/plugin.json` is at `"version": "1.0.2"`
  with nine skills under `loom-workflow/skills/`; each has a matching
  `loom-workflow/scripts/test_<skill>_compaction.py`.
- Reverse — `scripts/sync_codex_manifests.py` docstring: "the Claude manifest
  (``<plugin>/.claude-plugin/plugin.json``) is the single source of truth for the
  shared plugin metadata." Codex manifests are derived, never hand-edited.
- Error — `loom-code/skills/using-loom-code/references/dispatch-profile.md`: "A
  `frontier` request must not silently downgrade. If the host cannot provide a
  same-tier model, fail loud and surface the unavailable capability."
- Data — `loom-code/scripts/loom_firing_harness.py` `host_argv_for_root()` builds
  both host invocations; the Codex leg passes `--model` before the query while the
  Claude leg appends it, and Codex has no `--plugin-dir` equivalent.
- Boundary — repo `CLAUDE.md` §Contract Citations: a runtime prose contract under
  the loom skill and agent trees "must not cite one of this repository's
  development records under `docs/`", so the skill body cannot cite this brief or
  the change-folder.

## Decision

Build the core consultation loop as one skill in `loom-workflow`, whose stated
difference from the sibling critique skills is that the EXECUTOR changes rather
than the critique lens.

- The privacy guarantee covers the dispatch packet only. The honest fix is a
  disclosure obligation at the checkpoint, not a stronger scan: passing paths
  rather than content is this repo's convention, and inlining only vetted
  content would remove the skill's usefulness.
- Enterprise and operational hardening — persistence, retention, org-level
  policy declarations, billing-identity records, spend ceilings with numeric
  thresholds — is specified in the change-folder but NOT built in this arc.

## Out of Scope

- Persistence, retention, deletion, and crash recovery of requests and reports.
- Organisation- or repo-level policy declarations and vendor allowlists.
- Numeric thresholds of any kind (timeouts, spend ceilings, retry caps): the
  spec requires a declared bound, this arc does not pick the numbers.
- Leg-to-leg untrusted-text marking (the report path is in scope, the
  proposer→normalizer→judge path is not).
- Qualifying the proposer leg's blindness claim against `scope_boundary`.
- Any change to sibling skills' triggering, and any merge or deploy step.

## What Becomes Obsolete

The ad-hoc habit of typing "請用 fable 模型開 subagent 做一次獨立評估": it raises
the model but silently inherits the session's effort level, and it hands the
advisor the author's own framing. Nothing in the repo is deleted by this arc.

## Alternatives Considered

My take: recommend a single skill wrapping headless CLIs, with the blind-judge
counterbalance built in.

- **codex-review** (EN, github.com/shimo4228/codex-review) — a Claude Code skill
  thinly wrapping `codex review` read-only, treating the output as untrusted
  input. Rejected as the whole design: it is review-only, with no independent
  generation and no bias control.
- **crossmodel-review** (EN, github.com/ktundwal/crossmodel-review) — fans out to
  several vendors via Copilot CLI and reports agreements and divergences.
  Divergence-first reporting is adopted; the subscription dependency is not.
- **adversarial-review** (EN, basicmachines-co) — two model families review
  independently then rebut each other. Independent-generation-then-compare is
  adopted; the symmetric rebuttal is replaced by a blind judge, because the
  challenger is always younger than the incumbent and asymmetric attack favours
  the status quo.
- **ai-utils** (JA, zenn.dev/trknhr) — runs four CLIs in parallel on a `git diff`,
  deliberately on subscriptions rather than metered APIs. The cost framing is
  adopted into the checkpoint; diff-only input is rejected as too thin.

EN/JA divergence, itself a finding: English sources frame this as bias
engineering (decorrelation, swap, anonymisation) while Japanese sources frame it
as cost engineering (subscription vs metered) and additionally warn that
ensembling and order-reversal only treat variance inside the panel, never a bias
the whole population shares. Both framings are carried into the design.

## Open Questions

N/A — no unresolved question: every open item is recorded in the change-folder's
`## Blind spots — needs human/field input` section with a named source type, and
none of them blocks the Smallest End State above.
