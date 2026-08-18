# On-ramp explicit-choice gate — fire-rate baseline

**Date**: 2026-08-18
**Subject**: `loom-code/scripts/check_onramp_choice.py` (as of `4260a489`) run
over every historical spec and plan→brief pair, as a pre-ship ceremony
baseline for BI-7 of `docs/loom/specs/2026-08-18-onramp-explicit-choice-gate.md`.
**Scope note, stated up front**: the commit-time gate this arc ships
(Task 8, `git-guard.py`) only fires on `git commit` for a **newly added**
`docs/loom/plans/*.md` (`--diff-filter=A`). None of the historical
files scanned below were added today — **none of them is, or will be,
blocked by the shipped gate**. This audit answers a different question:
if the checker's strict grammar were applied to the existing corpus,
how often would it call something unresolved — i.e. how loud would the
gate be once it starts firing on *new* plans going forward.

## Method

1. Ran `check_onramp_choice.py <file> --repo-root .` over every file
   under `docs/loom/specs/*.md` (207 files) directly — each spec file
   itself carries (or lacks) a `## Design-side on-ramp` / inline
   `Design-side on-ramp:` line, so the spec file *is* the "brief" the
   checker parses.
2. For every file under `docs/loom/plans/*.md` (220 files), located the
   `**Source brief**:` / `Source brief:` header line (bold and
   non-bold forms both occur in the corpus), extracted its path
   (handling three observed spellings: bare path, backtick-wrapped
   path, and `[text](path)` markdown-link form), resolved it against
   the repo root, and ran the same checker against that resolved path.
   A bash `for`-loop with `sed`'s `\s` class could not reliably strip
   the three header spellings (`\s` is not honored by macOS/BSD `sed`
   in extended mode), so this half of the run used a small Python
   script instead of a one-line shell loop — its source is reproduced
   under §Commands below, next to the specs' shell loop.
3. Bucketed by exit code (0/1/2) and, for exit 0, by the checker's own
   stdout wording (`resolved (not_fired)` vs `resolved (resolved)`) —
   the checker's `print()` at `check_onramp_choice.py` `main()` always
   includes the literal string `not_fired` or `resolved` from
   `Result.status`, so a substring match on stdout distinguishes them
   without re-implementing the grammar.
4. Read `docs/loom/DIRECTION.md` at run time for the
   `## On-ramp standing choices` section state (§DIRECTION.md state
   below).

## Counts — specs (`docs/loom/specs/*.md`, 207 files)

| Outcome | Count |
|---|---|
| exit 0, not-fired | 1 |
| exit 0, resolved (fired + explicit choice) | 0 |
| exit 2, unresolved | 206 |
| exit 1, brief file missing | 0 |
| **Total** | **207** |

The single exit-0/not-fired file is this arc's own brief
(`docs/loom/specs/2026-08-18-onramp-explicit-choice-gate.md`), whose
inline line — `> Design-side on-ramp: not fired — ...` — was authored
against the canonical grammar this arc is introducing. Every other
spec (206 of 207) is unresolved under the strict checker, including
the 87 specs that *do* carry some form of a `Design-side on-ramp`
line (`grep -l "Design-side on-ramp" docs/loom/specs/*.md | wc -l` →
87) — none of their existing wording (`N/A — ...`, `not offered — ...`,
`not applicable — ...`, etc.) matches the checker's literal
`^not fired — <reason>$` form, so all 87 fall into the same
`unresolved` bucket as specs with no line at all. This is expected and
by design (`section-gate-must-flag-entry-lookalikes-not-just-matches.md`
— lookalike wording never resolves the gate); it also means the
checker's `unresolved` count is not a proxy for "the on-ramp actually
fired" on this historical corpus — see §Disagreement with the brief's
pre-measurement below.

## Counts — plans → brief (`docs/loom/plans/*.md`, 220 files)

| Outcome | Count |
|---|---|
| no `Source brief` line at all | 8 |
| exit 0, not-fired | 1 |
| exit 0, resolved (fired + explicit choice) | 0 |
| exit 2, unresolved | 200 |
| exit 1, brief file missing | 11 |
| **Total** | **220** |

The exit-1 "brief file missing" plans are pre-existing path drift, not
a gate defect — mostly old `code-toolkit`/`spec-toolkit` paths from
before the loom- rename, two paths that never existed under
`docs/loom/plans/*.md` naming (`implicit`, see below), one path
pointing outside the repo (an Obsidian vault path), and one
change-folder-style spec path. Full list under §Blocked pairs.

The 8 "no `Source brief` line" plans are older plans predating the
`**Source brief**:` header convention (`plan-format.md:31`); the
checker was never run against them because there is no path to
resolve.

## Combined total

207 (specs) + 220 (plans) = **427** files scanned, matching the sum of
the two counts tables above.

## Plan→brief pairs that would be blocked if newly added today

**211 pairs** (200 exit-2 unresolved + 11 exit-1 brief-missing) would
be blocked by the checker if the corresponding plan were *newly added*
today and staged in `git commit` — restated: **none of them actually
is**, per the scope note at the top of this file. The full list (plan
path → resolved brief path → reason) is reproducible via the commands
in §Commands; a representative sample of the exit-1 (brief-missing)
subset — the more actionable half, since exit-2 is expected corpus-wide
per the grammar-mismatch finding above — is:

| Plan | Resolved brief path | Reason |
|---|---|---|
| `docs/loom/plans/2026-05-25-distill-sessions-v2.6.1-known-bugs-hotfix.md` | `implicit` | exit 1: not a real path (header reads literally "implicit") |
| `docs/loom/plans/2026-05-25-distill-sessions-v2.7.1-propose-target-filter.md` | `implicit` | exit 1: same |
| `docs/loom/plans/2026-06-02-dbt-wiki-nl2sql-skill-part1-A.md` | `docs/code-toolkit/specs/2026-06-02-dbt-wiki-nl2sql-skill.md` | exit 1: pre-rename `code-toolkit` path |
| `docs/loom/plans/2026-06-12-completeness-critic-diverse-panel.md` | `docs/spec-toolkit/specs/2026-06-12-completeness-critic-diverse-panel.md` | exit 1: pre-rename `spec-toolkit` path |
| `docs/loom/plans/2026-06-12-deep-deep-research-vs-angle-selector.md` | `~/kouko-obsidian-vault/projects/...` | exit 1: brief lives outside this repo |
| `docs/loom/plans/2026-07-16-operational-kpi-quarterly.md` | `docs/loom/2026-07-16-operational-kpi-quarterly/specs/operational-kpi-quarterly/spec.md` | exit 1: loom-spec change-folder path, not under `docs/loom/specs/` |
| `docs/loom/plans/2026-08-16-loom-design-merge-plan.md` | `docs/loom/research/2026-08-15-loom-plugin-consolidation.md` | exit 1: research doc, not a spec |

The remaining 200 exit-2 pairs are the historical specs/plans whose
on-ramp wording predates the canonical grammar (see previous section) —
listing all 200 individually adds no new information beyond "the
grammar is new and stricter than prior ad hoc wording"; they are all
reproducible via the loop in §Commands.

## DIRECTION.md standing-choice state at run time

`docs/loom/DIRECTION.md`'s `## On-ramp standing choices` section is
**present** at run time (2026-08-18, commit `6186d710` + an uncommitted
working-tree diff of `+7` lines on this branch — i.e. this arc's own
Task 5, observed in-flight while this task ran, not yet committed):

```
## On-ramp standing choices

<!-- Repo-level on-ramp decisions read by check_onramp_choice.py; grammar
owned by loom-code/hooks/family-reception.md §On-ramp standing choices. -->

- row 1 (product-principles): standing direct — monkey-skills deliberately keeps no docs/loom/PRINCIPLES.md; loom-family arcs go direct to a brief (2026-08-18)
```

`load_standing(repo_root)` therefore resolves `{1: "direct"}` at run
time. This state does not change any count above — none of the 427
scanned files used the `fired: rows <n> — standing <detour|direct>
(DIRECTION.md)` form (that form did not exist in the corpus before
this arc), so `load_standing`'s output was consulted but never matched
during this run.

## Disagreement with the brief's 2026-08-18 pre-measurement

The brief's §Problem states a pre-measurement over the 86 specs that
carry a `## Design-side on-ramp` line, classified by wording family:
**71 not-fired, 8 fired-and-agent-defaulted-direct, 3
fired-with-an-explicit-user-choice, 4 other** (86 total).

This run's checker-based count over the same corpus (87 specs contain
some form of the line — one more than the brief's 86, see note below):
**0 not-fired, 0 resolved, 87 unresolved** (of the 207 specs scanned;
the other 120 specs carry no on-ramp line at all and are also
`unresolved`).

**These disagree, and the disagreement is expected, not a bug**: the
brief's 71/8/3/4 was a human/LLM classification by *wording family*
(loose, semantic — "N/A", "not offered", "not applicable" all read as
"not fired" to a human) done *before* BI-1's canonical grammar existed.
The checker implements BI-1's strict grammar literally: exactly
`not fired — <reason>` or `fired: rows <n> — user chose <detour|direct>`
or `fired: rows <n> — standing <detour|direct> (DIRECTION.md)` — every
other spelling, including "N/A — ..." and "not offered — ...", is
`unresolved` by design (the lookalike-wording rule the checker's own
docstring cites). So the pre-measurement's "71 not-fired" bucket is
real *evidence that the on-ramp mostly does not fire*, but none of
those 71 specs would pass the checker unmodified — they would all need
their wording rewritten to the canonical `not fired — <reason>` form to
resolve. The 8 fired-agent-defaulted and 3 explicit-choice specs are
likewise 0-for-0 against the checker for the same reason: none of the
historical corpus was ever written in the new canonical grammar (this
arc's own brief, `2026-08-18-onramp-explicit-choice-gate.md`, is the
first).

The off-by-one (87 vs 86 specs carrying the line) is not investigated
further here — it is a one-file discrepancy against a pre-measurement
whose own method (§Problem, brief) is not reproduced in this repo, and
does not change any conclusion above.

## Fired-rate implication for future arcs

Going forward, only *newly written* briefs are graded against the
canonical grammar (this run's 0/0/87 bucket is a snapshot of the old,
pre-canonical corpus — it says nothing about how often future briefs
will resolve cleanly). The brief's own pre-measurement is still the
best available estimate of the underlying fire rate: **on the order of
8–11% of briefs (8 agent-defaulted + 3 explicit, of 86) have the
on-ramp actually fire**, i.e. roughly 1 in 10 arcs. Under BI-5's new
rule (recommend as a standalone ask, write `pending` until answered),
that is the rate at which a future arc will see the standalone
on-ramp ask at all — the other ~90% ("not fired") pay no added
ceremony, since `not_fired` and `resolved` both exit 0 and the
`writing-plans`/`git-guard.py` gates only block on `unresolved`
(`pending`, malformed, or fired-with-no-recorded-choice). The
ceremony this arc adds is therefore bounded to roughly 1 extra
standalone question per 10 arcs, not a per-arc tax.

## Commands

Specs loop (bash; exact commands run):

```bash
cd /Users/kouko/GitHub/monkey-skills
total=0; not_fired=0; resolved=0; unresolved=0; missing=0
for f in docs/loom/specs/*.md; do
  total=$((total+1))
  out=$(python3 loom-code/scripts/check_onramp_choice.py "$f" --repo-root . 2>&1)
  code=$?
  if [ $code -eq 1 ]; then missing=$((missing+1))
  elif [ $code -eq 2 ]; then unresolved=$((unresolved+1))
  elif [ $code -eq 0 ]; then
    if echo "$out" | grep -q "not_fired"; then not_fired=$((not_fired+1))
    else resolved=$((resolved+1)); fi
  fi
done
echo "SPECS total=$total not_fired=$not_fired resolved=$resolved unresolved=$unresolved missing=$missing"
```

Output reproduced: `SPECS total=207 not_fired=1 resolved=0 unresolved=206 missing=0`

Plans loop (Python; needed because plan headers use three different
`Source brief` spellings that a portable `sed`/`grep` one-liner could
not reliably normalize — see §Method step 2):

```python
#!/usr/bin/env python3
import re, subprocess, sys
from pathlib import Path

REPO_ROOT = Path("/Users/kouko/GitHub/monkey-skills")
PLANS_DIR = REPO_ROOT / "docs" / "loom" / "plans"
LINE_RE = re.compile(r"^\**Source brief\**:\s*(?P<rest>.+)$")
MD_LINK_RE = re.compile(r"^\[[^\]]*\]\((?P<path>[^)]+)\)")
BACKTICK_RE = re.compile(r"^`(?P<path>[^`]+)`")

def extract_path(rest: str) -> str:
    rest = rest.strip()
    m = MD_LINK_RE.match(rest)
    if m: return m.group("path")
    m = BACKTICK_RE.match(rest)
    if m: return m.group("path")
    m = re.match(r"^[A-Za-z0-9._/\-]+", rest)
    return m.group(0) if m else rest

def main():
    plans = sorted(PLANS_DIR.glob("*.md"))
    total = len(plans)
    no_source_line = not_fired = resolved = unresolved = missing = 0
    for plan in plans:
        text = plan.read_text(encoding="utf-8")
        brief_rel = None
        for line in text.splitlines():
            m = LINE_RE.match(line.strip())
            if m:
                brief_rel = extract_path(m.group("rest"))
                break
        if brief_rel is None:
            no_source_line += 1
            continue
        brief_path = REPO_ROOT / brief_rel.lstrip("./")
        if not brief_path.exists() and brief_rel.startswith(".."):
            brief_path = (PLANS_DIR / brief_rel).resolve()
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "loom-code/scripts/check_onramp_choice.py"),
             str(brief_path), "--repo-root", str(REPO_ROOT)],
            capture_output=True, text=True)
        code = result.returncode
        if code == 1: missing += 1
        elif code == 2: unresolved += 1
        elif code == 0:
            if "not_fired" in result.stdout: not_fired += 1
            else: resolved += 1
    print(f"PLANS total={total} no_source_brief_line={no_source_line} "
          f"not_fired={not_fired} resolved={resolved} unresolved={unresolved} "
          f"brief_file_missing={missing}")

if __name__ == "__main__":
    main()
```

Output reproduced: `PLANS total=220 no_source_brief_line=8 not_fired=1 resolved=0 unresolved=200 brief_file_missing=11`

Re-running both commands against the same repo state (branch
`onramp-explicit-choice-gate`, DIRECTION.md state as recorded above)
reproduces these exact numbers.
