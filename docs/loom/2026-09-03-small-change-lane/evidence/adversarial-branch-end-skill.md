# Adversarial pass — branch-end skill (small-change-lane, HEAD e8d99de4)

Sandbox setup used for every probe below (a clean checkout of the reviewed
tree, so nothing here touches the shared worktree):

```
mkdir -p /tmp/adv-sandbox && cd /tmp/adv-sandbox && git init -q \
  && git config user.email a@a.com && git config user.name a
git -C <this-repo> archive e8d99de4 | tar -x -C /tmp/adv-sandbox
cd /tmp/adv-sandbox && git add -A && git commit -q -m base && git branch -M main
```

Six catalogue classes (`loom-code/skills/review/references/attack-catalogue.md`),
one attempt each, plus the five named attacks (a)-(e).

## Class: forge an artifact the gate trusts

**Attack**: write a `review.json` claiming a full-lane change was reviewed
and `second-vendor: ask` was honoured with `second_vendor: "none"`, with no
`questions[]` entry recording that the user was ever asked.

```
cd /tmp/adv-sandbox && git checkout -q -b vendor-attack2
printf '# KICKOFF defaults\n\n- second-vendor: ask — user decides per change (2026-09-04)\n' \
  > docs/loom/KICKOFF-DEFAULTS.md
mkdir -p docs/loom/vendorchange2
cat > docs/loom/vendorchange2/review.json <<'EOF'
{"reviewed_sha": "PLACEHOLDER", "scope": "branch-end", "second_vendor": "none",
 "verdicts": [{"round":1,"scope":"branch-end","reviewer":"rev-a","vendor":"anthropic",
   "model":"sonnet","lens":"skill","verdict":"PASS"}],
 "probes": [], "dispatch": [], "questions": []}
EOF
echo "# real skill change" >> loom-code/skills/build/SKILL.md
git add -A && git commit -q -m "forge: full-lane change, second_vendor:none, no questions[] entry"
python3 - <<'PY'
import sys, json; sys.path.insert(0, "loom-code/scripts")
import loom_checker as lc; from pathlib import Path
repo = Path("."); review = json.loads(Path("docs/loom/vendorchange2/review.json").read_text())
print("lane:", lc.change_lane_detail(repo, None))
print("check_second_vendor_honoured:", lc.check_second_vendor_honoured(repo, review, None))
PY
```

Output: `lane: ('full', 'loom-code/skills/build/SKILL.md is skill-typed')`,
`check_second_vendor_honoured: []` — **zero failures**.

**Stopped?** No. **Finding F3** (important) — see below.

## Class: bypass a gate by editing its input

**Attack (a)**: move a real production `.py` file into a `tests/`
directory to force the small lane's name-based test detection.

```
cd /tmp/adv-sandbox && git checkout -q main && git checkout -q -b small-attack
mkdir -p loom-code/scripts/tests
cat > loom-code/scripts/tests/evil_prod_logic.py <<'EOF'
"""Not a test. Production logic smuggled under tests/."""
def deploy_to_prod():
    import os; os.system("echo pretend-deploy")
EOF
git add -A && git commit -q -m "attack(a): smuggle non-test code under tests/"
python3 - <<'PY'
import sys; sys.path.insert(0, "loom-code/scripts")
import loom_checker as lc; from pathlib import Path
print(lc.change_lane_detail(Path("."), None))
PY
```

Output: `('small', 'every changed path ... is docs/memory/evidence/intent/'
'plan/standing, a test file, or CI/config, in at most one plugin '
'directory.')`

**Stopped?** No — `deploy_to_prod()` gets the small lane (one reviewer, no
blind run, no second-vendor question). **Finding F4** (important).

**Attack (a, second form)**: declare a KICKOFF `artifact-types:` override
reclassifying `loom-code/skills/**` as `docs`, on a diff that edits a real
skill file.

```
cd /tmp/adv-sandbox && git checkout -q main && git checkout -q -b artifact-types-attack
mkdir -p docs/loom
printf -- '- artifact-types: loom-code/skills/**=docs — dodge skill classification (2026-09-04)\n' \
  > docs/loom/KICKOFF-DEFAULTS.md
git add docs/loom/KICKOFF-DEFAULTS.md
echo "# evil edit to a gate-typed skill file" >> loom-code/skills/build/SKILL.md
git add loom-code/skills/build/SKILL.md
git commit -q -m "attack(a2): declare artifact-types override"
python3 - <<'PY'
import sys; sys.path.insert(0, "loom-code/scripts")
import loom_checker as lc; from pathlib import Path
repo = Path(".")
manifest = lc.load_manifest()
print("kickoff line:", lc.kickoff_defaults(repo).get("artifact-types"))
print("checker's computed type:", lc.artifact_types(manifest, ["loom-code/skills/build/SKILL.md"]))
print(lc.change_lane_detail(repo, None))
PY
```

Output: `kickoff line: loom-code/skills/**=docs`, `checker's computed type:
{'skill'}`, lane stays `full` — the override has **zero effect**: the
checker never reads it.

**Stopped?** The lane result itself held here (accidentally, because
ignoring the override happened to be the safe direction), but the text's
promise did not — the checker computes the type as if the KICKOFF line
did not exist. **Finding F2** (important).

## Class: replay a stale artifact

**Attack**: land an unreviewed commit, then re-submit a checkpoint whose
verdict `sha` still names the pre-existing (stale) commit while
`reviewed_sha` is bumped to the new one.

```
cd /tmp/adv-sandbox && git checkout -q main && git checkout -q -b replay-attack3
mkdir -p docs/loom/replaychange3 && echo x > docs/loom/replaychange3/a.md
git add -A && git commit -q -m "first pass content"
STALE_SHA=$(git rev-parse HEAD)
echo "def helper(): pass  # unreviewed" >> loom-code/scripts/git_exec.py
git add loom-code/scripts/git_exec.py
git commit -q -m "feat(loom-code): unreviewed change landed after the stale review"
NEW_PARENT=$(git rev-parse HEAD)
cat > docs/loom/replaychange3/review.json <<EOF
{"reviewed_sha": "$NEW_PARENT", "scope": "branch-end",
 "verdicts": [{"round":1,"scope":"branch-end","reviewer":"rev-a","vendor":"anthropic",
   "model":"sonnet","lens":"docs","verdict":"PASS","sha":"$STALE_SHA"}],
 "probes": [], "dispatch": []}
EOF
git add docs/loom/replaychange3/review.json
git commit -q -m "chore(loom): checkpoint review — branch-end PASS (replayed stale verdict sha)"
python3 loom-code/scripts/loom_checker.py push --head HEAD
```

Output includes: `BLOCK push.reviewed-sha: rev-a's verdict sha resolves to
44fb672e, not reviewed_sha 6e31eeff.`

**Stopped?** Yes — `held`. `check_reviewed_sha` ties every verdict's own
`sha` to the current `reviewed_sha`/`HEAD^`, so a replayed stale verdict is
refused.

## Class: cross a trust boundary (repo / worktree / process)

**Attempt**: this branch's changed text (review/ship/build/write-plan/
capture-intent SKILL.md prose) introduces no new worktree- or
process-crossing mechanism of its own — the worktree integration rule
(`git merge --no-ff`, never a rebase) is pre-existing `build` text
untouched by this diff, and the checker's `repo_root(Path.cwd())` /
`branch_base()` machinery it relies on is likewise unchanged here.

**Verdict**: `not-applicable` to this delta — the mechanism the class
targets belongs to prior, unchanged text, not to what this branch added.

## Class: self-exempt via a prose condition

**Attack (b)**: a fix-round reader "notices" and raises a finding outside
the fix delta, and **attack (e)**: a third round on the same checkpoint
never gets escalated to a design re-look.

```
grep -n "round\b" loom-code/scripts/loom_checker.py | grep -vi "^.*#" | grep -c "round"
grep -n "delta\|anchor" loom-code/scripts/loom_checker.py | grep -i "finding" 
```

Manual audit of every `push.*` rule in `loom_checker.py --list-rules`
(15 rules) against `fix-rounds.md`'s two claims: no rule reads a finding's
`anchor` against the fix delta, no rule counts rounds toward a
third-round cap, and no rule verifies a higher-tier agent was dispatched
before a fourth round on the same checkpoint. The checker's own comment on
`dispatch[]` confirms the pattern is deliberate elsewhere too:
`"fresh_context" is a record field, not a recomputable condition`
(`loom_checker.py:3277`).

**Stopped?** No — both (b) and (e) are pure prose, entirely
self-policing; nothing in `push` can catch a resumed reader that raises an
unrelated finding, or an orchestrator that iterates a fourth round without
ever dispatching the design re-look. **Finding F5** (nit — the text never
claims the checker enforces this, so it is not a contradiction, but it is
the textbook instance of this catalogue class and worth a named caveat).

**Attack (d)**: `second-vendor: ask` in the small lane — can the answer be
skipped and later claimed? Re-used the forge-class probe above (F3) for
the full-lane form; for the small lane itself:

```
cd /tmp/adv-sandbox && git checkout -q main && git checkout -q -b vendor-attack
printf '# KICKOFF defaults\n\n- second-vendor: ask — user decides per change (2026-09-04)\n' \
  > docs/loom/KICKOFF-DEFAULTS.md
mkdir -p docs/loom/vendorchange
cat > docs/loom/vendorchange/review.json <<'EOF'
{"reviewed_sha": "PLACEHOLDER", "scope": "branch-end",
 "verdicts": [{"round":1,"scope":"branch-end","reviewer":"rev-a","vendor":"anthropic",
   "model":"sonnet","lens":"docs","verdict":"PASS"}],
 "probes": [], "dispatch": []}
EOF
echo "small change" > docs/loom/vendorchange/note.md
git add -A && git commit -q -m "attack(d): small lane, ask never answered, no second_vendor field"
python3 - <<'PY'
import sys, json; sys.path.insert(0, "loom-code/scripts")
import loom_checker as lc; from pathlib import Path
repo = Path("."); review = json.loads(Path("docs/loom/vendorchange/review.json").read_text())
print(lc.change_lane_detail(repo, None))
print(lc.check_second_vendor_honoured(repo, review, None))
PY
```

Output: lane `small`, `check_second_vendor_honoured: []`. **Held for the
small lane** — this matches the text exactly (intent point 1: "小改動車道
只有一位讀者，這題不問"), so silently skipping the question here is the
documented design, not an evasion. The exploitable form is the **full**
lane one above (F3), where nothing ties the claimed answer to evidence the
question was actually asked.

## Class: race a concurrent writer

**Attack**: two dispatch-record writers append to the same `review.json`
`dispatch[]` array (as §2's "each in its own message so the two run
concurrently" invites) without any serialization; a lost-update drops one
record.

```
cd /tmp/adv-sandbox && git checkout -q main && git checkout -q -b race-attack
mkdir -p docs/loom/racechange
printf '{"reviewed_sha":"x","scope":"branch-end","verdicts":[],"probes":[],"dispatch":[]}' \
  > docs/loom/racechange/review.json
git add -A && git commit -q -m "seed review.json for race test"
python3 - <<'PY'
import json
path = "docs/loom/racechange/review.json"
a = json.load(open(path))          # writer A (adversary dispatch) reads
b = json.load(open(path))          # writer B (blind-runner dispatch) reads the same snapshot
b["dispatch"].append({"task": "branch-end", "role": "blind-runner", "agent_id": "blind-1"})
json.dump(b, open(path, "w"))      # B writes first
a["dispatch"].append({"task": "branch-end", "role": "adversary", "agent_id": "adv-1"})
json.dump(a, open(path, "w"))      # A writes second, from its stale snapshot
final = json.load(open(path))
print("final dispatch entries:", [e["role"] for e in final["dispatch"]])
PY
```

Output: `final dispatch entries: ['adversary']` — the `blind-runner` record
is silently lost.

**Stopped?** No. **Finding F6** (important) — a lost record breaks
`push.reviewer-ne-implementer` / `push.dismissed-by-reviewer`'s ground
truth, since `dispatch[]` is the only evidence separating reviewer from
implementer.

## Attacks (c): nit-batch commit sneaking a code change

```
cd /tmp/adv-sandbox && git checkout -q main && git checkout -q -b nitbatch-attack
mkdir -p docs/loom/attackchange
printf '{"reviewed_sha":"PLACEHOLDER","scope":"branch-end","verdicts":[],"probes":[],"dispatch":[]}' \
  > docs/loom/attackchange/review.json
git add -A && git commit -q -m "chore(loom): checkpoint review — branch-end PASS"
echo "def backdoor(): return 'sneaked in the nit batch'" >> loom-code/scripts/loom_checker.py
git add loom-code/scripts/loom_checker.py
git commit -q -m "docs(loom): nit batch — wording fixes"
python3 loom-code/scripts/loom_checker.py push --head HEAD
```

Output: `BLOCK push.review-only-head: HEAD must touch only
docs/loom/<change-id>/review.json; it touches
loom-code/scripts/loom_checker.py.` — exit 1.

**Stopped?** Yes, but for the *wrong* reason: `ship/SKILL.md` §3.5
literally instructs "the push follows the nit-batch commit as usual",
i.e. the nit-batch commit becomes `HEAD` and the push gate runs against
it directly. As written, following that instruction verbatim always
trips `push.review-only-head`, because a nit-batch commit necessarily
touches something other than `review.json` (that is the whole point of
a nit batch — it fixes wording in the SKILL/docs files the findings were
about). The gate does hold against a code change hiding in the batch, but
it holds against **every** nit batch, including an honest wording-only
one. **Finding F1** (important — the procedure as written cannot reach
push without an undocumented extra step).

## Findings

| id | severity | anchor | text | fix |
|---|---|---|---|---|
| F1 | important | `loom-code/skills/ship/SKILL.md` §3.5 ("The push follows the nit-batch commit as usual") | The nit-batch commit becomes `HEAD` and touches non-`review.json` files by design, but `push.review-only-head` (run by the very next step, §4) requires `HEAD` to touch only `review.json`; reproduced with the real `push --head HEAD` CLI (`BLOCK push.review-only-head`). Every checkpoint that has any nit finding — likely most of them — cannot reach push as §3.5 is written. | State the missing step explicitly: either fold the nit-batch commit into the review-only commit *before* it is finalized (i.e. do the nit batch before review step 7 sets `reviewed_sha`), or add a second review-only-shaped commit after the nit batch that re-sets `reviewed_sha` to the nit-batch commit, so `HEAD` is review-only again at push time. |
| F2 | important | `loom-code/skills/review/SKILL.md:100-102` ("a `KICKOFF-DEFAULTS.md` line `artifact-types: <glob>=<type>` overrides it") | The override is declared in the manifest's KICKOFF field schema and the template, but no function in `loom_checker.py` (`artifact_types`, `_artifact_type_for`, `change_lane_detail`, `check_probes_adversarial`, …) ever reads `kickoff_defaults(repo).get("artifact-types")`. Reproduced: a declared override had zero effect on the checker's computed type. This sentence is pre-existing but is now load-bearing for the new Lane feature that reads "the same classified delta". | Either implement the override (merge it into the effective type-mapping table before every `artifact_types` call), or strike the sentence from `SKILL.md` and the manifest's KICKOFF field list. |
| F3 | important | `loom-code/skills/write-plan/references/second-vendor-ask-and-docs-lint.md` §"`second-vendor: ask`"; `loom_checker.py` `check_second_vendor_honoured` / `_resolve_second_vendor_ask` | Nothing ties the recorded `second_vendor` answer to evidence the question was actually asked at decision point ① — a forged `second_vendor: "none"` with an empty `questions[]` passes with zero failures, on a full-lane change. Reproduced (see forge-class probe). Intent Acceptance #7 explicitly requires the question to land in the plan's `Questions asked` section. | `check_second_vendor_honoured` should also require a `questions[]` entry (`decision_point: 1`) matching the standing question whenever `second-vendor: ask` is declared and `second_vendor` is present. |
| F4 | important | `loom-code/skills/review/SKILL.md:119-128` (the Lane paragraph) | Small-lane "test file" classification is purely name/location-based (`tests` anywhere in the path); a non-test `.py` file placed under a `tests/` directory is accepted as small-lane-safe with no content check. Reproduced: a file with a `deploy_to_prod()` function under `loom-code/scripts/tests/` classified as `small`. The checker's own source comment calls this intentional, but the station text never discloses the name-only rule to its reader. | Add one clause to the Lane paragraph: "test" here means name/location only (`test_*.py`, `*_test.py`, or any `tests/` path segment) — not verified by content — so a reviewer/adversary knows to check what such a path actually contains. |
| F5 | nit | `loom-code/skills/review/references/fix-rounds.md` (whole file, new this branch) | "No finding outside the fix delta" and "third round triggers a design re-look" are entirely prose-trusted — no `push` rule checks a finding's anchor against the delta, counts rounds, or verifies a higher-tier dispatch. Not a contradiction (the text never claims mechanical enforcement), but it is the textbook "self-exempt via a prose condition" instance and worth a named caveat next to the rule. | Add one line acknowledging these two rules are reader-trusted, not checker-enforced — parallel to how `dispatch[]`'s `fresh_context` field is already documented as trusted, not recomputed. |
| F6 | important | `loom-code/skills/review/SKILL.md:138-140` ("each in its own message so the two run concurrently") | Dispatching the adversary and blind-runner "each in its own message" invites two independent read-modify-write cycles against the same `review.json` `dispatch[]` array with no serialization; reproduced a lost-update dropping one dispatch record. A lost record breaks `push.reviewer-ne-implementer` / `push.dismissed-by-reviewer`'s ground truth. | State explicitly that the two dispatch-record appends (and their commits) are sequential even though the two dispatched AGENTS then run concurrently — the concurrency is for the review work, not for the writes to `review.json`. |
