---
name: verified-gate-pytest-suite-misses-skill-structure-word-cap
description: The finishing-a-development-branch `verified` gate marker runs the pytest suite, which does NOT collect scripts/check-skill-structure.py (it is check-*.py, not test_*.py) — a SKILL.md word-cap breach (CHK-SKL-010, >4500 words / ~6000 tokens) passes the verified gate AND the local .claude/hooks/validate-skill-folder-structure.sh (structure-only), but fails CI's separate skill-structure job; run check-skill-structure.py <plugin> in the verify command for any branch that edits SKILL.md files
type: gotcha
origin: 2026-08-15 plain-relay-contract arc — the plain-relay N/A-consolidation paragraph tipped loom-code/skills/finishing-a-development-branch/SKILL.md to 4600 words; the close-out `verified` marker (full 2488-test pytest suite) minted green at HEAD, the local skill-folder hook passed, but CI's `skill-structure` job failed CHK-SKL-010 after the PR opened
---

The repo has TWO skill-structure enforcement surfaces that are easy to
conflate:

1. `.claude/hooks/validate-skill-folder-structure.sh` (PostToolUse on
   Write|Edit) — checks ONLY the flat-folder convention (no nested
   subfolders under a skill's subfolders). It does NOT check word count.
2. `scripts/check-skill-structure.py`, run by `.github/workflows/skill-structure.yml`
   as a SEPARATE CI job — checks structure AND the CHK-SKL-010 word cap
   (≤4500 words / ~6000 tokens). It is `check-*.py`, so `pytest scripts/`
   does NOT collect it.

The finishing-a-development-branch `verified` gate marker (Step 9c) runs
the pytest suite through `loom_gate_markers.py verified --run "<pytest…>"`.
That suite is green on a word-cap breach — so the marker mints, the
git-guard lets the push through, and the failure surfaces only when CI's
skill-structure job runs on the PR. Complements
[[ci-skill-structure-scan-gap-obsidian]] (CI blind spot for unscanned
plugins); this entry is the LOCAL blind spot for scanned plugins — the
dev's own verify command never runs the check CI will run.

**Why:** "tests passed" and "SKILL.md is under the word cap" are enforced
by different tools in different jobs; a verify command that covers only
the pytest suite has a hole exactly where CI checks next.

**How to apply:** for any branch that edits a SKILL.md under a scanned
plugin (domain-teams, loom-*), include `python3 scripts/check-skill-structure.py <plugin>`
in the `verified` marker's `--run` command (chain it with the pytest
suite), OR run it as a standalone close-out sub-check before minting —
same discipline as [[a-branch-suite-must-cover-every-touched-plugin-scripts-dir]]
extending the suite to every touched plugin dir. A future arc may fold
this into Step 5/9c of finishing-a-development-branch explicitly (note:
that SKILL.md is already near the cap, so the instruction must stay
terse). `wc -w` and `len(text.split())` can differ by 1 — see
[[name-the-word-count-convention-when-citing-a-count]]; the pin
convention is `len(text.split())` per check-skill-structure.py.