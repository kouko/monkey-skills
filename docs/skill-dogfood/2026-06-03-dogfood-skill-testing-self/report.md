# Dogfood report — dogfood-skill-testing (self-dogfood)

| field | value |
|---|---|
| Skill under test | `dev-workflow/skills/dogfood-skill-testing` |
| Skill version | 0.1.0 |
| Date | 2026-06-03 |
| Passes run | Probe A (activation, injection-fallback method) · Probe C (cold-reader) |
| Passes deferred | Probe B (executor+auditor) — nested self-execution, deferred |
| Method | fresh blind `Agent` subagents (no conversation context); meta-dogfood bias controlled by the firewall |
| Fidelity | activation = `fidelity:approximate` (injection fallback — no `ANTHROPIC_API_KEY` in env, real `claude -p` path not exercised) |

## Severity summary

| Critical | High | Medium | Low | Total |
|---|---|---|---|---|
| 0 | 1 | 3 | 1 | 5 |

Static structural tests (8) + whole-branch review (PASS_WITH_NOTES) all passed. Every
finding below is something those could NOT catch — behavioral/usability gaps.

---

### FINDING-001: "distractor sibling skills" set is load-bearing but never defined
- severity: **High** · category: Workflow-drift / Progressive-disclosure · pass: cold-reader
- probe prompt: "Could you run Probe A's PRIMARY path as written?"
- expected: a cold reader can execute Probe A
- actual: "A cold first-timer literally cannot run Probe A's PRIMARY path." The distractor
  set is referenced 3× as "a small **fixed** set/menu of distractor sibling skills" (SKILL.md
  L105, L130, L142) and the skill states "over-trigger is undetectable without distractors"
  (L105) — yet the set is never enumerated, sized, or pointed to a file.
- root cause: a load-bearing input is named "fixed" but left to the runtime agent to invent.
- why static review missed it: structural tests check the file EXISTS and contains tokens;
  they cannot detect that an instruction references a resource that is never supplied.
- location: SKILL.md §Workflow Probe A (L105 / L130 / L142)
- suggested fix: ship the distractor set as a bundled file (e.g. `assets/distractor-skills.md`)
  with a concrete list + one-line selection rule ("the N siblings whose descriptions are
  nearest-neighbour to the target"); reference it from Phase 2 + Probe A.

### FINDING-002: the jargon-leak detector leaks its own jargon
- severity: **Medium** · category: Jargon-leak · pass: cold-reader
- actual: terms used as established but unglossed: `fidelity:approximate` (tag, no schema),
  `pass[blind|informed]`, "meta-dogfood familiarity bias", "green grader", axis "grain",
  "agent-browser dogfood pattern" (first-timer has no idea what agent-browser is),
  "distractor set". (Some — oracle problem, bias accumulation — ARE glossed; several are not.)
- root cause: author-context vocabulary written as baseline (the exact bias the cold-reader
  pass exists to defeat — surfaced here against the skill itself).
- why static review missed it: no structural check models a first-time reader's vocabulary.
- location: SKILL.md L91, L153, L214, L222, L237, L240
- suggested fix: inline-gloss on first use, or a one-line glossary; especially `distractor set`
  + `fidelity:approximate` + `grain`.

### FINDING-003: Probe B "run the skill end-to-end on real/realistic input" — what input?
- severity: **Medium** · category: Workflow-drift (underspecified) · pass: cold-reader
- actual: "the vaguest single instruction in the file." For a skill-under-test the executor
  has never seen, what counts as "realistic input" is left entirely to the agent with no
  guidance or worked example. "Force the cold-start/fallback path (no config folder present)"
  also assumes the target HAS a config-folder concept — many skills don't.
- why static review missed it: a grep for "executor"/"auditor" passes regardless of whether
  the executor's task is actionable.
- location: SKILL.md §Workflow Probe B (L164–165)
- suggested fix: add one worked example of manufacturing realistic input for an arbitrary
  skill (e.g. "derive a representative task from the skill's own description / its trigger-eval
  should-fire queries"); make the cold-start-path step conditional on the target having config.

### FINDING-004: over-trigger seam — "test my skill" collides with skill-creator-advance
- severity: **Medium** · category: Over-trigger · pass: activation (12/13 routed correctly)
- actual: of 13 corpus queries, 12 route correctly with high confidence. The ONE collision:
  Query 1 ("dogfood test this skill … does it trigger and behave right?"). `skill-creator-advance`'s
  description explicitly claims the trigger phrase **"test my skill"**; a router could fire it
  on the bare word "test". dogfood-skill-testing wins on specificity, but the shared token is a
  real seam. (Partly external — lives in skill-creator-advance's description.)
- why static review missed it: trigger-eval.json schema-validates; it does not run a router
  against sibling descriptions to detect cross-claims.
- location: dogfood-skill-testing description vs `skill-creator-advance/SKILL.md` description ("test my skill")
- suggested fix: add an explicit "(for behavioral testing of an existing draft — not creating
  or white-box eval, see skill-creator-advance)" disambiguator near dogfood's trigger phrases;
  optionally propose trimming "test my skill" from skill-creator-advance (separate change).

### FINDING-005: dangling `NOTICE` reference
- severity: **Low** · category: Convention-violation · pass: cold-reader
- actual: L92 says "see this skill's `NOTICE`" but NOTICE is not listed in §Bundled resources.
- location: SKILL.md L92 vs §Bundled resources
- suggested fix: add `NOTICE` to the bundled-resources list, or drop the inline pointer.

## What worked (positive evidence)
- **Trigger precision is strong**: 12/13 corpus queries routed to the correct skill at high
  confidence; the mutual "Do NOT use for" cross-references across siblings actively suppress
  secondary candidates (genuine discrimination, not strawman).
- **Probe C (cold-reader) is the cleanest probe** — fully runnable as written (per the cold
  reader itself, ironically running on the skill).
- No Critical findings; no trigger-miss.

## Raw outputs appendix
- **Probe A transcript** (blind router, description-only): routing table 13/13 + ambiguities —
  agent `a5a7d93666d0fccd3`. Key line: "skill-creator-advance's description explicitly claims
  'test my skill' as a trigger phrase … a real router could fire creator-advance on the bare
  word 'test'."
- **Probe C transcript** (blind cold-reader): 5-question audit — agent `a5649ce4c189c788b`.
  Key line: "A cold first-timer literally cannot run Probe A's PRIMARY path [distractor set
  undefined]."
- Corpus: `dev-workflow/skills/dogfood-skill-testing/trigger-eval.json` (8 should-fire / 5 should-NOT).

> Findings are **advisory** — they localize + point; apply via normal conversation with the
> main agent. The auditor/cold-reader verdicts are drafts the user confirms or rejects.

## Remediation (2026-06-03, same session)

All five findings fixed in SKILL.md; **re-dogfood (fresh cold-reader) confirmed**:

| Finding | Fix | Re-dogfood verdict |
|---|---|---|
| F1 distractor undefined | Phase 2 now defines the set (count 3–6 + nearest-neighbour rule + worked example); Probe A points back to it | "distractor set IS now defined … Probe A runnable as written" |
| F2 jargon leak | inline glosses: agent-browser, meta-dogfood, green grader, data grain, pass[blind\|informed] | "most are now glossed … no load-bearing term left fully undefined" |
| F3 Probe B input | "derive input from the skill's own description / should-fire phrases"; cold-start step made conditional | "input manufacture IS addressed … runnable for self-contained skills" |
| F4 over-trigger "test my skill" | description disambiguator added (behavioral/blind vs white-box eval) | n/a (description-level) |
| F5 dangling NOTICE | NOTICE added to Bundled resources | resolved |

**Re-dogfood found a NEW (2nd-order) finding → also fixed**: `trigger-eval.json` shipped in the
bundle but was undocumented + unreferenced — the skill made the reader rebuild a corpus it already
ships. Fixed: listed in Bundled resources + referenced as Probe A's corpus starter; added a
`test_skill_md_refs` assertion to prevent regression. Remaining minor (v0.1.1): JSONL-parse filter
in Probe A is directional not concrete; realistic-input sourcing thin for bulky-external-input skills.

Loop status: **converged** (1st round 5 findings → fixed → 2nd round confirmed + 1 new → fixed).
Structural tests 8/8, package-level 137/137 green throughout.
