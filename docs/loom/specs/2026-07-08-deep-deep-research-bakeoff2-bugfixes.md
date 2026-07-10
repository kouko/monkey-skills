# deep-deep-research: fix 4 bugs found in 2026-07-08 bake-off round 2

## Problem

`research-toolkit:deep-deep-research` produces incorrect or incomplete
output in ways a user would not notice from the rendered report alone.
Round 2 of the bake-off (n=3 questions, 3 concurrent arms in one session)
independently reproduced 4 defects — two of them (field-name mismatch,
evidence-drop) hit **every single run**, not just concurrent ones:

1. **Concurrency collision** — the `work/` intermediate-file tree defaults
   to a fixed path under the invocation cwd (SKILL.md's own instruction),
   not namespaced per run. Two concurrent invocations in the same cwd
   overwrite each other's intermediate files.
2. **Directory-merge contamination** — `rank.py --claims-dir` merges every
   `*.json` file in the given directory (by design — see Current State
   Evidence). This is only a defect *because* of #1: once the work dir is
   namespaced per run, this "merge everything in the dir" behavior becomes
   correct again, since the directory will only ever hold the current run's
   files.
3. **Field-name mismatch (KeyError)** — `verify_prompt()` in `prompts.py`
   hard-indexes `claim["sourceUrl"]`, but nothing in the pipeline's
   documented schema or instructions tells the Stage-3 extraction step to
   use that literal key name — so an agent extracting claims has no way to
   know it must write `sourceUrl` rather than `url`. All 3 independent
   bake-off arms wrote `url` and hit a KeyError at verify time.
4. **Evidence silently dropped / caveats type fragility** — the final
   markdown renderer (`_render_markdown` in `synthesis.py`) never reads
   `finding["evidence"]` even though the report schema requires it per
   finding, so it never reaches the report the user reads. Separately, the
   renderer assumes `report["caveats"]` is always a string; if the
   synthesizing LLM emits a list instead (an easy drift for a field whose
   own prompt asks it to "note caveats" — plural, list-shaped, in a
   schema that says `{"type": "string"}`), `"\n".join(lines)` raises a
   `TypeError` and the whole render step dies.

The job: a user or agent running `deep-deep-research` — solo or as one of
several concurrent invocations — gets a correct, complete rendered report
every time, without needing to hand-invent workarounds mid-run (which is
what all 3 bake-off arms did this round).

## Users

Anyone invoking `research-toolkit:deep-deep-research` — this repo's own
maintainers dogfooding it (as in this bake-off), and any external user of
the `research-toolkit` marketplace plugin. No special persona split; the
defects are correctness bugs, not UX/audience-specific issues.

## Smallest End State

Three independent, disjoint-file fixes. No pipeline redesign, no new
opt-in stage, no schema shape change:

- **Fix A (SKILL.md prose only, resolves bugs #1 and #2)** — change the
  File-carrier rule's `work/` directory instruction from a fixed path to
  a run-scoped one: pick a unique directory name once at Stage-1 start
  (default `work/` for the common single-run case; a distinguishing
  suffix, e.g. `work-<short-id>/`, when the agent knows it is one of
  several concurrent invocations in the same session) and use that same
  chosen directory consistently for every stage reference below. No
  script changes — `rank.py --claims-dir <dir>`'s "merge everything in
  the directory" behavior is correct once the directory is properly
  scoped, so bug #2 needs no separate code fix.
- **Fix B (`prompts.py`, resolves bug #3)** — `verify_prompt()` reads the
  source URL via `claim.get("sourceUrl") or claim.get("url", "")` instead
  of a hard `claim["sourceUrl"]` index, mirroring the `.get(...)`
  tolerance `synthesis.py` already uses. Add one doc sentence to
  SKILL.md's Stage 3 step 3 naming the literal key (`sourceUrl`) claims
  must carry, so extraction gets it right from the start and the fallback
  rarely needs to fire.
- **Fix C (`synthesis.py`, resolves bug #4)** — `_render_markdown()`:
  (a) coerce `caveats` to a string if the report emits a list (join with
  newlines) before appending, instead of assuming schema compliance; (b)
  render each finding's `evidence` field (it is already read/available on
  the finding dict, just never emitted).

Each fix ships with a failing-test-first (RED → GREEN) pair in the
existing `test_prompts.py` / `test_synthesis.py` files, following their
established conventions (flat imports, subprocess CLI tests where
relevant). Fix A has no code to test; verify it via a fresh-context
cold-read of the edited SKILL.md section (per `judgment-rubrics.md` §5
quality floor for prompt/skill/rule text) rather than pytest.

## Current State Evidence

- **Forward** (where these paths are invoked): `SKILL.md:352`
  (`rank.py --claims-dir work/claims`), `SKILL.md:378-379` (`prompts.py
  verify --claim '<claim JSON>' ...`), `SKILL.md:641-648` (`synthesis.py
  report --key report=work/report.json ...`). The orchestrating agent
  (not any Python entry point) is the sole caller of all of these — there
  is no wrapper script.
- **Reverse** (who defines the shapes consumed above): `schemas.py:71-91`
  `EXTRACT_SCHEMA` — the `claims` array items require only `claim`,
  `quote`, `importance`; **no URL-carrying field is defined at all**,
  confirming bug #3's root cause is a schema/doc gap, not a typo.
  `schemas.py:104-126` `REPORT_SCHEMA` declares `"caveats": {"type":
  "string"}` (schema says string; nothing enforces the synthesizing LLM
  actually complies) and each finding requires `evidence` — the schema
  already demands the field bug #4 drops.
- **Error path** (current failure behavior): `prompts.py:106`
  `source_url = claim["sourceUrl"]` — hard `KeyError` on a `url`-keyed
  claim, no `.get()` fallback (contrast with `synthesis.py:68,82,96`,
  which already do `claim.get('sourceUrl', '')` everywhere claims are
  read). `synthesis.py:149-152` `_render_markdown`'s caveats branch does
  `lines.append(caveats)` with no type check, so a non-string caveats
  value survives until `"\n".join(lines)` at line 166 raises `TypeError`.
- **Data path**: `synthesis.py:141-147` findings-render loop reads
  `confidence`, `claim`, `sources` off each finding dict but never calls
  `f.get("evidence")` — the field is present on the dict (it flows in via
  `report.json`, schema-required) and is simply never read in this loop.
- **Boundary**: `test_prompts.py:99-114` and `test_synthesis.py` never
  construct a claim/report missing `sourceUrl` or with non-string
  `caveats` — every existing fixture is schema-compliant by hand, which
  is exactly why these bugs shipped unnoticed; the new tests must cover
  the missing/malformed-input boundary specifically.

Evidence paths: `research-toolkit/skills/deep-deep-research/SKILL.md`,
`research-toolkit/skills/deep-deep-research/scripts/{schemas,prompts,synthesis,test_prompts,test_synthesis}.py`.

## Decision

Ship all 3 fixes (A/B/C above) in one branch, TDD-first for B and C,
cold-read-verified for A. No change to `rank.py`, `dedup.py`, `schemas.py`
struct shapes, or any opt-in Stage-1/6 lever (VS mode, framework-audit,
meta-mode, purpose-fit, calibration) — those are out of scope and
untouched by these defects.

## Out of Scope

- Redesigning the file-carrier convention itself (e.g. a formal run-ID
  system, a manifest file) — the minimal per-run directory-name fix is
  sufficient for the confirmed defects.
- Hardening `rank.py` independently against directory contamination —
  superseded by Fix A; adding a second independent guard here would be
  defending against a risk Fix A already eliminates (redundant surface).
- Rendering the optional `finding.vote` field in the markdown — not one
  of the 4 confirmed defects; out of scope to avoid scope creep on an
  adjacent-but-unreported field.
- Any change to the opt-in Stage 6 levers (meta-mode / purpose-fit /
  calibration) — they wrap the base prompt and are untouched by this bug
  set.
- Updating `docs/loom/BACKLOG.md` / dogfood mirror — folded into the same
  branch's commit per the repo's "memory travels with the PR" convention,
  not a separate task here.

## Alternatives Considered

Narrow design space — all 3 fixes are standard, textbook patterns with no
real competing approach worth an industry search:

- Fix A: per-run-scoped scratch directories (vs. a formal run-ID/manifest
  system, or requiring the caller to pass `--work-dir` explicitly). The
  scoped-directory-name convention is the standard, minimal pattern (same
  shape as `mktemp -d` in spirit) and matches what all 3 bake-off arms
  independently improvised under pressure — evidence the lightweight fix
  is the natural one, not an invented alternative.
- Fix B: defensive `.get()` fallback (vs. renaming the schema field to
  `url` everywhere, which would be a bigger, backward-incompatible
  change touching more call sites for no added correctness).
- Fix C: type-coerce + read the existing field (vs. tightening the LLM
  prompt to forbid list-shaped caveats, which doesn't eliminate the
  renderer's fragility — an LLM can still drift under a different
  phrasing later; defensive rendering is the fix that actually holds).

## What Becomes Obsolete

The three ad-hoc workarounds each bake-off arm hand-invented this session
(manual `work-q{1,2,3}/` isolation + selective file-copying before
ranking, inline `sourceUrl` aliasing inside verifier dispatch prompts,
hand-composing markdown from the raw report object instead of trusting
`synthesis.py report`) all become unnecessary once these fixes ship —
future runs get correct behavior from the skill itself, not from an agent
improvising around it mid-pipeline.

## Open Questions

None — all 3 fixes are fully specified above; no user input needed before
`writing-plans`.
