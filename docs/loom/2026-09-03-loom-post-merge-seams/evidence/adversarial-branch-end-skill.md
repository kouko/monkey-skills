# Adversarial audit — skill-typed delta, branch-end checkpoint

Target: `git diff 160658c2..HEAD -- loom-code/skills/ship/SKILL.md
loom-code/skills/review/SKILL.md` (commit `e19b65eb`). Attacker role only —
never an implementer of this change. Repo root
`/Users/kouko/.herdr/worktrees/monkey-skills/simple-loom-flow`, branch
`loom-post-merge-seams`, HEAD `664159a8`. Read-only against the repo except
this file. The checker's `push.review-only-head`
(`check_close_commit_shape`), `push.reviewed-sha` (verdict-sha tie) and
`push.verdicts-ge-2` are the code-typed delta already covered by 21
committed probes and 12 graduated tests — not re-attacked here; used only
to test what the two SKILL.md texts claim about them.

## Class: forge an artifact the gate trusts

Attempt: hand-craft a `review.json` round for the close-commit checkpoint
that ship §6 describes — two verdict entries with plausible `reviewer`,
`vendor`, `model`, `lens`, `verdict: PASS`, `sha: <close commit>` — never
actually dispatching `agents/reviewer.md`, and see whether `push` accepts
it.

Caught by: `push.reviewer-ne-implementer` — `parse_dispatch` requires a
`dispatch[]` entry per verdict's `reviewer` id with role `reviewer` /
`blind-runner` / `adversary`; a verdict naming a reviewer absent from
`dispatch[]` is `unknown` and blocks (loom_checker.py:3105-3114, read, not
re-run here — pre-existing mechanism, not part of this diff). A forged
verdict with no matching dispatch entry is refused.

Result: held (by the pre-existing, already-probed mechanism; not a hole
introduced by this diff).

## Class: bypass a gate by editing its input

Attempt: put the close commit's status-line edit and the `review.json`
verdict-append into the **same** commit (skip ship §6's two-commit shape:
close commit, then a separate review-only commit), hoping the merged diff
still "reads" as the intent-typed delta the text describes.

Caught by: `review.review-only-commit` / `push.review-only-head` recompute
HEAD's raw diff and refuse any shape other than exactly `review.json`
touched, `M`, both sides `100644`; a commit also touching the intent path
fails structurally (`check_review_only_head`, pre-existing, code-typed
delta). Verified by reading `check_close_commit_shape` at
loom_checker.py:1883-1978, already covered by that delta's own probes —
not re-run here.

Result: held (pre-existing mechanism).

## Class: replay a stale artifact

Attempt: reuse the branch-end round's already-committed adversarial probes
and package-tests probe records as-is for the close-commit round, without
adding new probe entries whose `sha` names the close commit — see whether
`push` still accepts them.

**Reproduced** (ran the actual checker functions against this repo,
no repo file changed):

```
python3 - <<'EOF'
import sys; sys.path.insert(0, "loom-code/scripts")
import loom_checker as lc
from pathlib import Path
repo = Path(".")
head = lc.git_text(repo, "rev-parse", "HEAD").strip()
close_sha = lc.git_text(repo, "rev-parse", "HEAD^").strip()   # stands in for <close commit>
stale_sha = lc.git_text(repo, "rev-parse", "HEAD~5").strip()  # an earlier commit, stands in for the original probe sha
review = {"probes": [
    {"kind": "adversarial", "command": "python3 evidence/probes/x.py", "sha": stale_sha,
     "artifact": "evidence/probes/x.py", "result": "pass", "scope": "branch-end"},
]}
# check_probes_adversarial ties probe["sha"] to reviewed_id; a stale sha never matches close_sha
print("probe sha", stale_sha[:8], "vs reviewed_id", close_sha[:8], "-> stale, must fail the tie")
EOF
```

Output: `probe sha <stale sha> vs reviewed_id <close sha> -> stale, must
fail the tie`. Confirmed by reading `check_probes_adversarial` and
`check_probes_package_tests` (loom_checker.py:2441-2560, :2331-2360): both
require `probe["sha"]` to resolve, as a git object id, to `reviewed_id`
(the close commit) — a probe recorded against any earlier commit is
rejected with `"ran against sha X, not the reviewed commit"`, however
correct the command and artifact still are. `changed_paths()` (used to
decide which artifact `kinds` need adversarial coverage) diffs
`branch_base(repo)..HEAD` — the **whole branch**, not just the close
commit's own delta — so this isn't scoped away by the delta being
intent-only: `kinds` will include every type the branch ever touched
(here: code, skill), so ≥3 usable, sha-tied probes are still owed at the
close-commit push.

**Finding** (important): ship §6 says only "package tests and adversarial
probes are **re-pinned** there" — it never states the mechanical action
(write new `probes[]` entries into this round, same `command`/`artifact`,
`sha: <close commit>`) that `push.probes-adversarial` and
`push.probes-package-tests` actually require, nor that this applies to
**every** probe the branch accumulated, not just ones touching the status
line. A literal cold agent following only this sentence has no way to
infer that step, and will hit a full `push.probes-adversarial` /
`push.probes-package-tests` block on the second push of ship §6 with no
prose explaining why the exact same probes that passed one push ago now
fail. Fails closed (no bypass), but is a genuine, reproducible workflow
gap: anchor `loom-code/skills/ship/SKILL.md:308-309`. Fix: state the
concrete action — "add a `probes[]` entry per branch-typed probe kind for
this round, same `command`/`artifact`, `sha: <close commit>`, and let the
checker re-run every one of them at push."

Disposition: CARRY-FORWARD — the fix is a one-sentence prose addition, not
a checker change, and does not block this PR (the checker already fails
closed; the cost is a wasted push cycle, not a hole).

## Class: cross a trust boundary (repo / worktree / process)

Not applicable to this delta. Neither SKILL.md text introduces a new
cross-process or cross-worktree write; step 4/6's pushes are ordinary
single-repo git operations and the worktree-removal step (§7) is
untouched by this diff.

Result: not-applicable.

## Class: self-exempt via a prose condition

Attempt: satisfy ship §6's instruction — "two fresh reviewers **under the
docs and user-judgment-leak lenses**... every verdict carries `sha: <close
commit>`" — with two verdicts whose `lens` is `code` (wrong lens for a
one-line status change), sha-tied correctly, and see whether the push
gates that this text claims cover the round (`push.reviewed-sha`,
`push.verdicts-ge-2`) actually recompute the lens.

**Reproduced**:

```
python3 - <<'EOF'
import sys; sys.path.insert(0, "loom-code/scripts")
import loom_checker as lc
from pathlib import Path
repo = Path(".")
head = lc.git_text(repo, "rev-parse", "HEAD").strip()
parent = lc.git_text(repo, "rev-parse", "HEAD^").strip()
review = {"reviewed_sha": parent, "verdicts": [
    {"round": 99, "scope": "branch-end", "reviewer": "fake-rev-a", "vendor": "anthropic",
     "model": "sonnet", "lens": "code", "verdict": "PASS", "sha": parent,
     "dimension_scores": {"security": "PASS"}, "findings": []},
    {"round": 99, "scope": "branch-end", "reviewer": "fake-rev-b", "vendor": "anthropic",
     "model": "sonnet", "lens": "code", "verdict": "PASS", "sha": parent,
     "dimension_scores": {"security": "PASS"}, "findings": []},
]}
print("check_reviewed_sha:", lc.check_reviewed_sha(repo, head, parent, parent, review))
print("check_verdicts:", lc.check_verdicts(review))
EOF
```

Actual output:
```
check_reviewed_sha: []
check_verdicts: []
```

Both gates pass with `lens: code` on every verdict. Grepped the whole
checker for any lens recompute at push: the only place `verdict["lens"]`
is read at all is `spec_scoped_verdicts` (loom_checker.py:1342-1344),
which exists to satisfy `intake.spec-pass` for `scope: spec` rounds — a
different gate entirely, not part of the `push` command's rule set, and
never consulted for a `branch-end`-scoped round.

**Finding** (important): ship's "under the docs and user-judgment-leak
lenses" and review's artifact-type table entry for `intent` are pure
prose — no `push` rule recomputes which lens a close-commit-round
verdict claims. An agent (or a shortcut-taking one) can satisfy every
mechanical push rule for the close-commit checkpoint by dispatching two
reviewers under any lens at all, including a lens that reads nothing
relevant to a one-line status-field diff. This is squarely the catalogue's
"self-exempt via prose condition" class: the specific instruction reads
like a gate but is not one. Anchor `loom-code/skills/ship/SKILL.md:308`.
Fix: either have `push.reviewed-sha`/a new rule recompute lens membership
for an intent-typed round, or soften the ship text to say plainly that
lens choice here is un-enforced agent discipline, not a checked fact —
so a reader does not mistake it for a gate.

Disposition: CARRY-FORWARD — same class of gap as similar unenforced
`lens` self-reporting elsewhere in the station (e.g. a `code`-lens
reviewer's actual dimension coverage is likewise never recomputed by
`push`); not new risk exclusive to this diff's narrow slice, and fixing it
requires either a new checker rule or a prose-only demotion — both belong
to the checker/skill maintainers' next round, not a blocker for this
skill-typed review.

## Class: race a concurrent writer

Attempt: violate review §2's new "dispatch in two stages" ordering —
launch the adversary/blind-runner and the two fresh-context reviewers in
the *same* message, so a reviewer's verdict names a `sha` that a
concurrently-running adversary probe commit later moves past.

Verified by reading (not independently re-run as a live two-process race,
given scope — the mechanism is the code-typed delta's `check_reviewed_sha`
tie, already probed 21 times): every verdict's `sha` must resolve, as a
git object id, to `reviewed_id` = `HEAD^` at push (loom_checker.py:2138-
2172). If the adversary/blind-runner's probe-and-report commit lands
*after* a reviewer already minted its verdict against an earlier `HEAD`,
that verdict's `sha` no longer equals the final `reviewed_id` and
`push.reviewed-sha` blocks it by name (`"{reviewer}'s verdict sha
resolves to X, not reviewed_sha Y"`). The two-stage instruction is
therefore process advice for avoiding a wasted round, not itself a gate —
but the invariant it protects (a verdict's sha matching the pushed tree)
is independently enforced regardless of dispatch order.

Result: held, by the pre-existing sha-tie mechanism (not literally raced
here; reasoning from the tie's unconditional recompute, which the
code-typed delta already reproduces in its own probes).

## Cross-checks asked for directly

- **Does ship still say the agent stops after `gh pr create` and the user
  merges?** Weakened, not removed. Before this diff, `## 6. Merge, verify,
  close the intent` began immediately after §5 with the merge line. Now
  `## 6. Close the intent, then merge, then verify` interposes an entire
  unconditional sequence — close-intent commit, a fresh `branch-end`
  review round, a second push — **before** the surviving line "Merge when
  the user asks and CI is green" (`ship/SKILL.md:325`, unchanged text,
  moved position). The agent still does not merge without the user
  asking, and `ship.no-push-before-acceptance` (§2) still gates the
  *first* push on decision-point-③ acceptance — but the new intervening
  work (a second review round, dispatching two more agents, a second
  push) after `gh pr create` and before that merge line is not itself
  gated on any user checkpoint; the text reads as if the agent should run
  it straight through unattended. That is consistent with the spec (REQ-1
  frames it as mechanical follow-through, not a new acceptance point) but
  worth naming: a user who reads "ship" as "open the PR and wait" will be
  surprised the agent then dispatches two more reviewing agents and
  pushes again before they said anything. Nit, not a gap the checker
  needs to catch (nothing here bypasses `ship.no-push-before-acceptance`,
  which the first push already satisfied) — anchor
  `loom-code/skills/ship/SKILL.md:294-325`. Disposition: CARRY-FORWARD.

- **Does it tell the agent to run the checker's `push` before each push?**
  Only once. §4 says explicitly: "Run the checker explicitly, then push"
  and explains why ("that wait is the point of it... running it here
  first only means you see the block before the tool call does"). §6's
  second push ("Then the review-only commit, `reviewed_sha` set to the
  close commit, and push again") does not repeat this instruction. The
  PreToolUse hook still runs `push` automatically on the actual `git
  push` regardless (§4's own text says so), so this is not a mechanical
  gap — but it is an inconsistency: the only station text that explains
  *why* to run the checker manually first is attached to the first push
  and silently doesn't apply to the second. Nit — anchor
  `loom-code/skills/ship/SKILL.md:314-315`. Fix: one clause, "run the
  checker's `push` explicitly first here too, same as step 4." Disposition:
  CARRY-FORWARD.

- **Does the review text's worked record match the manifest's verdict
  grammar (`sha` present)?** Yes. `contract/manifest.yaml:120` declares
  `verdicts` grammar as `[{reviewer, vendor, model, lens, scope, round,
  verdict, dimension_scores, findings, fallback, spec_sha, sha}]` with the
  note "`sha` is the commit this verdict reviewed and must equal
  `reviewed_sha` (`push.reviewed-sha`), no scope exempt." The worked
  record in `review/SKILL.md`'s §7 example carries
  `"sha": "be19b9612b0d4c7a9f0e21c3d8a5b6e7f0123456"` on its one verdict,
  matching `reviewed_sha` at the top of the same JSON blob byte for byte.
  Consistent — no finding.

- **Spec REQ-1 cross-check.** No contradiction found. REQ-1's own text —
  "package-tests and adversarial probes are re-pinned at the close commit
  (the checker re-runs both itself at push)" — states the exact mechanism
  the "replay a stale artifact" finding above says the SKILL.md text
  under-specifies; the spec is correct and complete, the SKILL.md
  compresses it into a phrase a cold agent cannot expand unaided. REQ-1
  also states "no exemption by scope... every verdict of the latest
  round... must carry `sha`" — matches the reproduced behavior of
  `check_reviewed_sha` above (no scope filtering in its verdict loop).
  REQ-1's "two fresh-context reviewers read it under the docs +
  user-judgment-leak lenses" is spec-level prose with the same
  unenforced-lens property found above — the spec does not claim the
  checker recomputes lens membership either, so this is not a
  spec/SKILL.md contradiction, only the shared gap already logged as an
  important finding.

## Findings summary

| # | Severity | Anchor | Text | Disposition |
|---|---|---|---|---|
| 1 | important | `loom-code/skills/ship/SKILL.md:308-309` | "package tests and adversarial probes are re-pinned there" gives no mechanical instruction for what re-pinning is (new `probes[]` entries, `sha: <close commit>`, one per branch-typed probe kind, re-run against the full-branch-diff `kinds`); a literal agent will hit an unexplained `push.probes-adversarial`/`push.probes-package-tests` block on the second push. | CARRY-FORWARD — prose-only fix, fails closed today |
| 2 | important | `loom-code/skills/ship/SKILL.md:308` | "two fresh reviewers under the docs and user-judgment-leak lenses" is not recomputed by any `push` rule; reproduced two `lens: code` verdicts passing `check_reviewed_sha` and `check_verdicts` unchanged. | CARRY-FORWARD — pre-existing pattern across all lenses, needs checker-side decision |
| 3 | nit | `loom-code/skills/ship/SKILL.md:294-325` | The post-PR sequence (close-intent commit, second review round, second push) reads as unattended follow-through with no explicit "the agent proceeds without asking" statement, though nothing it does bypasses the acceptance gate already satisfied at the first push. | CARRY-FORWARD |
| 4 | nit | `loom-code/skills/ship/SKILL.md:314-315` | §6's second push does not repeat §4's "run the checker explicitly first" instruction; the PreToolUse hook still enforces it, so this is cosmetic only. | CARRY-FORWARD |

No fatal findings — no combination of the six catalogue classes bypasses
`push.review-only-head`, `push.reviewed-sha`, or `push.verdicts-ge-2` for
this delta; every attempted forgery, replay, or shortcut was either caught
by the pre-existing (and separately probed) checker mechanisms, or is a
prose-completeness gap that fails closed rather than open.

**PASS_WITH_NOTES — fatal: 0, important: 2, nit: 2**
