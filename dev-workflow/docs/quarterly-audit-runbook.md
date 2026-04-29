# Quarterly Skill Audit Runbook

Operational runbook for quarterly review of dev-workflow's skill
ecosystem. Companion to `skill-governance.md`.

**Cadence**: every 3 months (Jan / Apr / Jul / Oct), or on demand
when significant change events occur (major skill release,
external dependency update, framework migration).

**Time budget**: ~1-2 hours per audit when ecosystem is stable;
more if findings require investigation.

**Output**: a brief audit report committed to
`dev-workflow/docs/audit-reports/YYYY-Qn-audit.md` recording what
was checked, what was found, and what action items resulted.

---

## When to run

### Scheduled

Quarterly:
- Q1: end of January
- Q2: end of April
- Q3: end of July
- Q4: end of October

### On demand

Whenever any of these happen:
- Major skill release (new skill, breaking change, version major bump)
- External dependency update (upstream MIT skill modified, Anthropic
  Skills API contract change)
- User-reported regression that suggests systemic drift
- Validation gate from architecture doc §6 has been completed and
  needs reflection in governance docs
- Cross-plugin contract violation discovered

---

## Pre-audit checklist

- [ ] Last audit report read and any open action items reviewed
- [ ] Current git status clean (no in-flight branches that block
      file inspection)
- [ ] `gh` CLI authenticated; can read PRs
- [ ] Python 3.11+ available for running CI scripts locally

---

## The audit checklist

### 1. SSOT registry verification

Goal: ensure governance doc's SSOT Registry matches reality.

```bash
# Run the convention drift CI locally
python3 scripts/check-shared-conventions-drift.py

# Check ownership tables in skill-governance.md vs actual LICENSE
# files in each skill directory
for skill in dev-workflow/skills/*/; do
    name=$(basename "$skill")
    echo "=== $name ==="
    head -5 "$skill/LICENSE" 2>/dev/null | grep -i copyright || echo "  (no LICENSE or no copyright line)"
done
```

Action items:
- [ ] All conventions in registry pass drift check
- [ ] Each skill's LICENSE matches stated owner in governance doc
- [ ] Any new shared convention added since last audit is in registry

### 2. Skill lifecycle state review

Goal: confirm each skill's state matches its activity level.

For each Active skill, check:
- Last commit date (`git log --oneline -1 -- "dev-workflow/skills/<skill>/"`)
- Recent invocation patterns (informally; if telemetry available, use it)
- Open issues / known regressions

For each Deprecated skill:
- Has 3 months passed? If yes, eligible for Retired transition
- Has a replacement skill matured? If yes, expedite retirement
- Is anyone still using it? If usage signal present, postpone retirement

Action items:
- [ ] No Active skill has been untouched for >12 months without
      recent invocation evidence (suggests it should be Deprecated)
- [ ] All Deprecated >3 months reviewed for Retired transition
- [ ] Lifecycle table in governance doc updated if states changed

### 3. Convention drift inspection

Goal: catch any drift not caught by CI (e.g., conceptual drift
between skill behavior and convention documentation).

For each shared convention:
- Read the canonical version
- Verify the skills that depend on it still implement the
  documented behavior (sample-based; spot-check a few skills)
- If drift discovered: file an action item to either align skill
  with convention or update convention to reflect skill reality

Action items:
- [ ] All 3 shared conventions (golden-anchor / test-prompts /
      constitution) spot-checked against consuming skills
- [ ] Cross-plugin conventions (mindsets in code-team) verified
      consistent with dev-workflow:complexity-critique consumption

### 4. External dependency audit

Goal: ensure upstream MIT chains are intact and attribution is
current.

For each skill with NOTICE file:
- Verify upstream URL still resolves
- Verify upstream skill / project still exists at stated path
- Check upstream license is still MIT (or compatible)
- Note any upstream updates that would warrant local sync

Skills with NOTICE files (as of v1.7.0):
- skill-creator-advance (Anthropic → AllanYiin → kouko)
- skill-judge (Leonardo Flores → kouko)
- complexity-critique (joshuadavidthomas → softaworks → kouko)
- skill-refactor (original; design influence from darwin-skill)
- skill-tuning (original; design influence from darwin-skill)

Action items:
- [ ] All upstream URLs resolve
- [ ] All upstream licenses confirmed still MIT
- [ ] Significant upstream updates noted for follow-up sync

### 5. Validation gate status

Goal: track outstanding validation gates from architecture doc §6.

```bash
# Search for OUTSTANDING markers in CHANGELOG
grep -A 2 "OUTSTANDING" dev-workflow/CHANGELOG.md
```

For each outstanding gate:
- Determine if validation has been performed since last audit
- If yes: update CHANGELOG / governance doc to reflect completion
- If no: assess whether outstanding for >2 quarters; if so, decide
  to either schedule validation or formally accept the risk

Currently outstanding (as of v1.7.0):
- skill-refactor: dry-run on ≥2 existing skills; ≥90% equivalence-
  check agreement with manual review
- skill-tuning: 1 real-skill walkthrough verifying A/B flow
  produces meaningful preference signal

Action items:
- [ ] All outstanding validation gates inventoried
- [ ] Each gate >2 quarters outstanding has explicit accept-risk
      or schedule-validation decision

### 6. Skill-judge score history (if data available)

Goal: detect drift in skills that have been using
`scripts/score_history.py` for evaluation tracking.

For each skill with a `.skill-judge-history.jsonl` file:

```bash
python3 dev-workflow/skills/skill-judge/scripts/score_history.py \
    drift <skill>/.skill-judge-history.jsonl
```

If drift flagged: investigate (refactor introduced subtle
regression? tuning moved skill in unintended direction?). Recommend
running skill-tuning to capture human preference signal before
deciding action.

Action items:
- [ ] Drift detection run on all skills with history
- [ ] Flagged drift findings noted for investigation

### 7. Documentation freshness

Goal: catch stale documentation.

- [ ] Plugin README version line matches plugin.json version
- [ ] Plugin README skills table matches actual skills directory
- [ ] CHANGELOG.md most recent entry is for the current version
- [ ] Governance doc SSOT Registry has no orphaned entries
- [ ] Architecture doc §10 acceptance criteria still reflect
      reality (skills that have shipped should not still appear
      as "to be implemented")

---

## Audit report template

Save to `dev-workflow/docs/audit-reports/YYYY-Qn-audit.md`:

```markdown
# YYYY-Qn Quarterly Audit

**Date**: YYYY-MM-DD
**Auditor**: <name>
**Plugin version at audit**: vX.Y.Z

## Findings summary

- N skills active, M deprecated, K retired
- Drift CI: PASS / FAIL (details if FAIL)
- Outstanding validation gates: N (list)
- Score-history drift findings: N (list)

## Action items

- [ ] Item 1
- [ ] Item 2
...

## Notes

Any observations that don't fit elsewhere.
```

Commit the audit report. The next quarterly audit references the
prior one's open action items.

---

## What to do with findings

| Finding type | Action |
|---|---|
| Convention drift in CI | Block merging until same-PR drift rule honored |
| Skill should be Deprecated | Open PR adding deprecation marker + not-trigger; minor bump |
| Skill should be Retired | Wait for 3-month deprecation; then PR removing skill; major bump |
| Validation gate complete | Update CHANGELOG / governance doc; close gate |
| Validation gate >2 quarters outstanding | Decision: schedule validation (one-shot PR) OR formally accept-risk (note in governance doc) |
| External upstream broken | Investigate; if upstream gone, update NOTICE; if MIT changed, follow license terms |
| Score-history drift | Investigate; possibly run skill-tuning; possibly accept (taste evolved with intent) |

---

## When to extend this runbook

This runbook is itself a living document. Extend it when:

- A new class of governance check becomes routinely needed
- A finding type recurs across audits without a clear response policy
- A new skill class enters the family (e.g., agent-team skills)
  with its own audit needs

The plugin owner maintains this runbook as part of governance
responsibility.
