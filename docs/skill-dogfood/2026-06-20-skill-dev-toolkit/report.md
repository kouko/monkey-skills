# Dogfood report — `skill-dev-toolkit` (5 skills, post-extraction second pass)

> **Findings are ADVISORY.** This was the second-pass QA on the merged
> `skill-dev-toolkit` extraction (#430): the canonical blind-subagent
> behavioral dogfood + a fresh dispatched whole-skill code review, run
> once the subagent weekly-limit reset. The first pass (inline, at merge
> time) covered structural/behavioral *integrity* only; this pass covers
> blind triggering + workflow-contract + an independent second opinion.

## Metadata

| Field | Value |
|---|---|
| Skill path | `skill-dev-toolkit/skills/{skill-creator-advance,skill-judge,skill-refactor,skill-tuning,dogfood-skill-testing}/` |
| Plugin version | `0.1.0` |
| Date | 2026-06-20 |
| Passes run | activation (real-harness) · executor+blind-auditor · cold-reader · fresh dispatched code-review |
| Model pinned | claude-opus-4-8 (orchestrator + subagents); activation via `claude -p` 2.1.183 |
| Activation fidelity | **real-harness sandbox** (`claude -p --max-turns 1 --allowedTools Skill --output-format stream-json --verbose`, live menu, ≥2 runs/query) |

## Severity summary (behavioral findings)

| Severity | Count |
|---|---|
| Critical | 0 |
| High | 0 |
| Medium (🟡) | 5 (all extraction-introduced; all FIXED on `fix/skill-dev-toolkit-dogfood`) |
| Low (🟢) | 1 noted (sca NOTICE provenance — folded into F-5) + pre-existing set (mention-only) |
| Trigger flag | 1 (skill-tuning, see TRIG-1) |

## Probe A — Activation harness (real-harness sandbox)

Corpus: 8 should-fire (≥1 per skill, 2 priority skills ×2) + 3 should-NOT
(external distractors), 2 runs each. Routing is non-deterministic — read
per-skill, averaged.

| Query | Expected | run1 | run2 |
|---|---|---|---|
| build me a new skill that wraps our deploy checklist | creator-advance | ✅ | ✅ |
| create a slash command skill for generating release notes | creator-advance | ✅ | ✅ |
| is this SKILL.md well-designed? score its quality | judge | ✗ | ✅ |
| review the design quality of this skill package and grade it | judge | ✗ | ✅ |
| shorten this skill, it has too many tokens — cut the SKILL.md down | refactor | ✗ | ✅ |
| 縮減這個 SKILL.md 的 token 數但保留行為 | refactor | ✗ | ✅ |
| A/B test the output quality of this skill on the same prompts | **tuning** | **✗** | **✗** |
| dogfood this skill before I ship it — will it fire correctly? | dogfood | ✅ | ✅ |
| review my pull request diff for correctness bugs | (none) | ✗ | ✗ |
| refactor this Python data-pipeline module to reduce its size | (none) | ✗ | ✗ |
| debug why this pytest case fails intermittently | (none) | ✗ | ✗ |

- **TNR = 100%** — no over-trigger: the 3 external distractors fired none
  of the 5 skills. The severing/genericization did NOT make the family
  greedy.
- **TPR** — creator-advance & dogfood 2/2; judge & refactor fired on run2,
  missed run1 (routing variance in the bare one-shot harness).
- **TRIG-1 (RESOLVED — variance, not a real miss):** `skill-tuning`
  missed both runs for "A/B test the output quality of this skill" in the
  first batch, but a focused re-test (4 phrasings × 3 runs) fired
  skill-tuning **3/3** on that exact phrase and 3/3 on "tune output
  voice/tone". The original 0/2 was high-variance noise in the bare
  one-shot harness (the "never conclude from a single run" rule). **No
  description change made** — the baseline already triggers reliably.

## Probe B — Executor + blind auditor (workflow contract)

Two priority skills run end-to-end on real input; a firewalled blind
auditor judged each artifact against the skill's OWN declared contract.

- **skill-judge — PASS (auditor: STRONG).** Ran the full 8-dim rubric on
  a real external target (`ascii-graph` SKILL.md) → 105/120, Grade B, per-
  dimension scores + justifications + top-3 improvements. Blind audit:
  arithmetic sums to 105 exactly, grade band correct, every cited feature
  verified present in the target, no fabrication. The genericized
  "domain-team adaptation" appendix correctly **no-op'd** (target isn't a
  domain-team skill) — confirming the genericization residue is confined
  to that optional section, not the core workflow.
- **skill-creator-advance — PASS (auditor: ADEQUATE).** The INLINED
  worth-it gate correctly **REJECTED** a thin proposal (`git-status-helper`,
  a wrapper over `git status`/`git diff --stat`) via Gate-2 (smallest end
  state = 0 functions). Verdict domain-correct; one loosely-worded
  "additive = fail" framing noted. **The extraction did not break the
  inlined gate** (the core concern of the second pass).
- Neither artifact was "valid-looking but domain-wrong."

## Probe C — Blind cold-reader (zero-context first-time reader)

Two fresh zero-context subagents read skill-judge + skill-creator-advance
SKILL.md as first-time users. Surfaced the genericization residue that a
green structural check sees as PASS (see F-2..F-4). Also surfaced the
pre-existing set (mention-only): skill-creator "skill-creator directory"
vs actual `skill-creator-advance`, `CHK-SKL-013`, scripts/ not in the
reference index, "retasted" typo, score_history `...` placeholder.

## Independent fresh code review (code-toolkit:code-reviewer)

Verdict on the merged extraction: **PASS_WITH_NOTES.** Confirmed by
execution (not memory): 0 cross-plugin `plugin:skill` IDs (all file types),
manifests valid (dev-workflow 2.18.0 / 8 skills), marketplace==plugin.json
verbatim, both CI gates green, flat-skill structure intact, cross-task
coherence clean (frozen dated docs correctly retain old IDs). Headline
should-fix = the move-introduced broken-link family (F-1) the cold-readers
partially missed.

## Findings (all extraction-introduced; all FIXED)

| # | sev | category | location | finding | fix (applied on `fix/skill-dev-toolkit-dogfood`) |
|---|---|---|---|---|---|
| F-1 | 🟡 | dangling-ref | skill-refactor + skill-tuning READMEs (6 md-links) + both NOTICE files + `references/self-trained-judge-pipeline.md` | All point to `dev-workflow/docs/skill-evolution-architecture.md`, which stayed in dev-workflow → broken links / cross-plugin leak after the move. Root cause: relative `../../docs/` pointer valid pre-move, dead post-move. | Removed the supplementary "see … §1" links (rationale already stated inline) + genericized the NOTICE/reference prose to drop the cross-plugin path. 0 refs remain. Commit `cb0f97f1`. |
| F-2 | 🟡 | convention/residue | skill-judge `SKILL.md:819-820` (+ :814) | Genericization produced "above what domain-team structural gates / **gates** already check" (line-break-split doubled "gates") + sentence-initial lowercase "the". | Rewrote to "above what the structural convention gates already check" + capitalized. Commit `0c3e60a4`. |
| F-3 | 🟡 | self-containment | skill-judge `SKILL.md:877` | Cross-plugin path `dev-workflow/docs/quarterly-audit-runbook.md` (a bare path, so the plugin:skill grep-guard never caught it). | Dropped the path → "a periodic quality audit". Commit `0c3e60a4`. |
| F-4 | 🟡 | dangling-ref | skill-creator-advance `SKILL.md` Gate-1 | After `dev-workflow:proposal-critique` ID was severed (#430), Gate-1 still said "The triage matrix … the full 5-step flow" with definite articles but no matrix/flow defined in-file → dangling for ≥2-skill proposals. | Inlined the triage criteria (KEEP/DEFER/DROP on evidence grounding + YAGNI); Gate-2 unchanged. Commit `ae54970f`. |
| F-5 | 🟢 | provenance | skill-creator-advance `NOTICE:28,34` | Stale `Path: dev-workflow/skills/...` + `dev-workflow/CHANGELOG.md` pointer after the move. | Repointed Path to `skill-dev-toolkit/`; folded the changelog pointer into the inline per-version summary. Commit `ae54970f`. |

## Follow-up applied (newly surfaced → FIXED same branch, commit `44244e34`)

- **F-6 — stale `dev-workflow` framing** beyond the architecture-doc family
  (same root cause as F-1): two SKILL.md "runtime self-contained —
  `dev-workflow` is the only plugin needed" statements (factually wrong
  post-move), NOTICE "runs with `dev-workflow` alone", 6 README "Where in
  dev-workflow does this fit?" family diagrams (EN/ja/zh ×2), "Parallel to
  **other** dev-workflow critique skills", LICENSE/NOTICE/README
  provenance, and plugin-conventions examples — all repointed to
  `skill-dev-toolkit`. Accurate references kept (the general critique gates
  `proposal-critique`/`complexity-critique` genuinely stay in dev-workflow).

## Out of scope (NOT fixed — pre-existing)

- **Pre-existing (origin/main; surgical-edits → mention-only):** "retasted"
  typo, "skill-coherence" ref, score_history `...` placeholder,
  `skill-creator directory` wording, `CHK-SKL-013`, scripts/ not indexed,
  README `../../../../LICENSE` extra `../`, `__pycache__` not in
  `.gitignore`, CHK-SKL-012 "unexpected top-level file" for
  LICENSE/NOTICE/test-prompts.json (a check-allowlist gap, not a defect).

## Verification (post-fix, on branch)

- 0 `skill-evolution-architecture` / `quarterly-audit-runbook` / "triage
  matrix"/"5-step flow" / doubled-"gates" / dev-workflow-path-in-sca-NOTICE.
- Self-containment: 0 cross-plugin `plugin:skill` IDs.
- CI gates: description-standard 11 passed · drift "in sync" · dogfood
  structure 7 passed · marketplace-sync OK · plugin-coherence OK.
- 3 conventional `fix(skill-dev-toolkit):` commits; no files added (all
  modifications); red-line token scrub clean.

## Method notes

- Activation harness initially returned all-no-fire — a harness bug
  (`--output-format stream-json` requires `--verbose`), NOT a real
  trigger-miss; fixed and re-run. (Floor-not-ceiling: a green automated
  check that *looked* like "nothing fires" was a tooling artifact.)
- Dispatched agents pinned to reasoning class (general-purpose /
  code-toolkit:code-reviewer), never search — per the known lesson that
  search agents silently refuse critique roles.
- Human (kouko) is the final calibrator: raw subagent outputs are in the
  session transcript; this report is the conversational handoff artifact.
