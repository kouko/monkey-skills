# Dogfood Report — brief-before-asking (Mode D + Mode A-default change)

- **Skill under test:** `dev-workflow/skills/brief-before-asking/` (branch `fix/brief-before-asking-stakes-first-and-real-examples`)
- **Scope:** the CHANGED behavior — Mode A → default; new Mode D (stakes didn't land); repeated-confusion guard; description triggers.
- **Probes:** A (activation, fallback synthetic — `fidelity:approximate`), B (executor + blind auditor), C (blind cold-reader).
- **Distractor set:** complexity-critique, proposal-critique, recap-state, handoff, git-memory.

## Severity summary

| Severity | Count | Status |
|---|---|---|
| Critical | 0 | — |
| High | 0 | — |
| Medium | 1 | FIXED (F1) |
| Low | 2 | FIXED (F2, F3) |
| Pre-existing (out of scope) | 3 | noted, not fixed |

Probe A: 0 trigger-miss, 0 over-trigger (15-query corpus × 2 runs, no disagreement). Probe B: 3/3 scenarios PASS (blind auditor), 1 WEAK flag → F3. Probe C: clarity gaps → F1, F2.

## Findings (all tied to this change, all fixed)

### F1 — Medium · Mode-routing conflict (Trigger / Cold-start) · `SKILL.md:§Mode Detection Heuristics`
A Mode-D trigger phrase ("為什麼要選" / "why does this matter") arriving right after a long jargon explanation hits both the Mode-D row (→D) and the "confusion after dense explanation" rows (→C), with no tiebreak. Cold-reader (Probe C) could not tell which wins.
- **Fix applied:** added a "phrase content beats turn position" tiebreak note after the heuristics table — stakes-naming phrasing → D even after a dense turn; can't-follow phrasing → C; position only breaks ties on neutral phrases.

### F2 — Low · Progressive-disclosure · `SKILL.md:§Mode D`
Mode D had no pointer to a worked example (only Mode C did, line 61), yet a worked Mode-D example now exists in EXAMPLES.md. First-timer couldn't find it.
- **Fix applied:** added a "Mode D example — optional load" note pointing to §Real-World Cases Real Case 2 (text-to-SQL) + Real Case 1.

### F3 — Low · Output-quality (jargon-leak) · `SKILL.md:§Mode D`
Blind auditor (Probe B) passed all 3 executor outputs but flagged the Mode-D one for carrying raw internal labels (`thin/thick-slice`, `git-ref`, `WARN`, `D`/`E`) *alongside* the plain framing — stakes recoverable from the analogy, but the skill's own "define jargon on first use" mandate not fully honored.
- **Fix applied:** added Mode-D output step 4 — drop or define internal labels; replace with analogy + plain outcome words, do not ride them alongside.

## Pre-existing (NOT introduced by this change — left for a separate pass)
- `references/DESIGN.md` holds the non-trivial *upper* escalation boundary but is marked do-NOT-load-at-runtime → the "Mode A is the default / skipping is a violation" contract is strict while its gate is fuzzy.
- Undefined in-file terms: `Minto SCQA`, `two-way door / one-way door`, `AskUserQuestion` (assumed host tool).

## Raw outputs
Probe transcripts (executor 3 scenarios, blind auditor 3 verdicts, cold-reader Q1–6, activation 15×2) live in the session log; key excerpts cited inline above. Probe A is `fidelity:approximate` (synthetic routing, no live `claude -p` harness).

## Verdict
No Critical/High. The three surfaced findings were all in newly-added content and are fixed. Per floor-not-ceiling: this is a behavioral pass on the changed surface, not a blanket skill-quality stamp — see skill-judge for static design scoring.
