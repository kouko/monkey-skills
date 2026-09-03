# Spec red-team — 2026-09-03-loom-post-merge-seams (round 8, spec v9)

Scope: docs/loom/2026-09-03-loom-post-merge-seams/spec.md (v9). Verified against
loom-code/scripts/loom_checker.py at HEAD (923fb84a): `latest_round` :293,
`scored_verdicts`/`check_verdicts` :2265/:2278, `check_reviewed_sha` :1670,
`HOST_PLUMBING_FILES`/`_is_host_plumbing` :382-397. Also verified
`loom-code/scripts/codex_scaffold.py` (`plugin_version`/`PLUGIN_ROOT`/`PLUGIN_JSON` :98-145)
against both this repo's layout (`loom-code/.claude-plugin/plugin.json`,
`loom-code/scripts/codex_scaffold.py`) and the installed plugin cache
(`~/.claude/plugins/cache/monkey-skills/loom-code/1.0.0/.claude-plugin/plugin.json`,
`.../1.0.0/scripts/`), and PRINCIPLES.md (ratified 2026-09-03). The checker code is
still unchanged by this branch — v9 remains a design spec for a future implementation
(no `sha`-handling on `verdicts[]` anywhere in `loom_checker.py`, no
`codex_scaffold` import in `loom_checker.py` yet).

## 1. Round-7 findings under v9

**spec-C13 (stale scope-exemption sentence in Design decision 1) — HOLDS.**
review.json's open_findings records spec-C13 as: "Design decision 1 still says
`verdicts[].sha` is required only on non-spec scopes, contradicting REQ-1's
no-exemption rule (stale sentence from v7)." v9's Design decision 1 now reads:
"the verdict grammar gains `sha` — additive, contract stays 1.0 — and
`verdicts[].sha` is required on every verdict of the latest round regardless of
its `scope` (no scope exemption, round 6 spec-R21)" (spec.md:19). This is the
same no-exemption rule REQ-1 states ("There is no exemption by `scope`: a scope
label is a claim, not a recompute (round 6 spec-R21)," spec.md:6). The two
sections now agree; no stale sentence survives. HOLDS.

**spec-R23 (merge commit at HEAD^ → first-parent diff) — HOLDS.**
v9's REQ-1 rewrites the recompute: "`push.review-only-head` also recomputes the
reviewed commit's shape when it introduces a `closed` status, reading the
commit as a diff against its first parent — `git diff --raw --no-renames
HEAD^^ HEAD^` — never `git show`, which prints nothing for a merge commit and
would let a merge at `HEAD^` carry the transition unseen (round 7 spec-R23)"
(spec.md:6). `git diff <A> <B>` is a plain two-tree comparison — it does not
special-case either tree as a merge result, so it correctly reports every path
that differs between `HEAD^^`'s tree and `HEAD^`'s tree regardless of how many
parents `HEAD^` has. This closes the exact hole spec-R23 named (`git show`'s
default no-diff-for-merge-commits behavior). HOLDS — verified further in §2(a)
below with the specific "second-parent carries the transition" attack the task
asked me to re-derive.

**plugin_version() attribution nit — HOLDS (fixed, disclosed rather than
silently left).** R7's nit (`spec-redteam-r7.md` §2e) was that
`codex_scaffold.plugin_version()` reads `PLUGIN_JSON`, computed from
`codex_scaffold.py`'s *own* `__file__`, not from the invoked
`loom_checker.py`'s path — correct only because the two files are always
siblings, an assumption the v8 text never stated. v9's REQ-3 now states it
explicitly: "`codex_scaffold.plugin_version()`, which reads the
`.claude-plugin/plugin.json` **two levels above `codex_scaffold.py`'s own
file**, so the checker imports that module **from its own `scripts/`
directory (the sibling import it already uses)** and the version is that of
the tree the checker runs from" (spec.md REQ-3). This is R7's fix option (i)
(state the sibling dependency explicitly) rather than option (ii) (pass the
invoked directory in) — an acceptable choice since REQ-3 says nothing forbids
it and Design decision 3 doesn't contradict it.
  - Verified "two levels above" is literally correct for both layouts:
    `PLUGIN_ROOT = Path(os.path.abspath(__file__)).parent.parent`
    (codex_scaffold.py:99) is two `.parent` hops from the file — this repo:
    `loom-code/scripts/codex_scaffold.py` → `loom-code/scripts` →
    `loom-code/`, then `PLUGIN_JSON = PLUGIN_ROOT/".claude-plugin"/"plugin.json"`
    = `loom-code/.claude-plugin/plugin.json` ✓. Plugin cache: confirmed on
    disk `~/.claude/plugins/cache/monkey-skills/loom-code/1.0.0/.claude-plugin/plugin.json`
    exists alongside `.../1.0.0/scripts/` ✓ — same two-hop relationship.
  - Verified "the sibling import it already uses" is an accurate reference to
    an existing pattern, not a fabricated one: `loom_checker.py:41` already
    does `from git_exec import run_git  # sibling module (no __init__.py, no
    conftest)` — the same directory-relative import idiom REQ-3 says will be
    reused for `codex_scaffold`. Not misleading.
  HOLDS.

## 2. Attacks on v9

### (a) First-parent diff for the close-commit trigger and shape

**Does a merge commit whose SECOND parent carries the closed transition
escape?** No — traced and confirmed. `git diff --raw --no-renames HEAD^^
HEAD^` compares the *tree* of `HEAD^^` against the *tree* of `HEAD^`
(the merge result), not either parent's diff in isolation. If the merge
brings the second parent's `closed`-transitioned intent file into the
resulting tree (a fast-forward-shaped merge via `-X theirs`, or a normal
three-way merge that resolves to the second parent's version), that file's
content necessarily differs from `HEAD^^`'s tree (which still has
`confirmed`), so the diff **does** report it, and the trigger ("touches an
intent file whose `status:` line changes to `closed …`") fires as intended.
Confirmed the reasoning holds; not an escape.

**Does the checkpoint-parent requirement (`HEAD^^` a review-only commit)
interact badly with `HEAD^` being a merge?** `HEAD^^` unambiguously resolves
to the first parent of `HEAD^` under git's own revision syntax, merge or not
— this is not spec-defined behavior that could drift, it's `^` applied twice.
So the checkpoint-shape test (`HEAD^^` touches only `review.json`, its
`reviewed_sha` resolves to `HEAD^^^`) is well-defined and fully recomputed
regardless of whether `HEAD^` has one parent or several. Traced the two ways
this could go wrong and found neither exploitable:
  - *Attacker tries to smuggle extra content via the second parent while
    keeping the file-count/line-count shape check satisfied.* Since the diff
    is tree-vs-tree (not per-parent), anything the second parent contributes
    that differs from `HEAD^^`'s tree shows up in the same diff and blows the
    "exactly one file, one line" budget — caught, not an escape.
  - *Attacker makes `HEAD^` a merge whose first parent is the trunk (or any
    ref other than the real checkpoint), hoping `HEAD^^`'s checkpoint check is
    skipped for merges.* It is not skipped — the same recompute runs on
    `HEAD^^` unconditionally, and the trunk (built from squash merges of
    review-only-wrapped commits, not itself a review-only commit touching
    only `review.json` with a self-resolving `reviewed_sha`) fails that shape
    test and is refused. Fails safe.
  - Octopus merges (>2 parents) don't change this: `HEAD^^` is still `(HEAD^)^`,
    the first-listed parent, and the tree-diff argument above is parent-count
    agnostic.
  Not reported as a finding (matches the honesty-preserving precedent in
  spec-redteam-r7.md §2(c) for the CRLF case: at worst this is a
  false-negative-shaped *robustness* concern — a legitimate mid-branch
  `git merge main` immediately before the close commit would also fail the
  checkpoint-parent check, since `HEAD^^` would then be the merged-in commit,
  not the real checkpoint — never a bypass). See nit below.

### (b) Zero-verdict edge wording

v9 adds: "The tie reports only when the round has at least one usable verdict
— an empty round is already `push.verdicts-ge-2`'s report" (spec.md REQ-1).
Verified against the live code: `scored_verdicts()` (loom_checker.py:2265)
filters `verdicts[]` to entries with a non-empty `reviewer` and `verdict`
string ("usable"); `latest_round([])` (loom_checker.py:293) returns `(0, [])`
for an empty list; `check_verdicts()` (loom_checker.py:2278) then computes
`reviewers = set()`, `len(reviewers) < 2` is true, and appends a
`push.verdicts-ge-2` failure reading "review round 0 carries 0 distinct
reviewer(s) with a readable verdict; two fresh contexts are required." This
is exactly the report the spec sentence claims already exists — no gap, and
no double-reporting collision with the (as-yet-unimplemented) sha-tie rule,
since the sha-tie text is explicitly scoped to rounds with ≥1 usable verdict.
Accurate; not a finding.

### (c) Checkpoint definition for the cost table

REQ-4: "one checkpoint = one review-only commit, i.e. a commit touching only
`review.json`, taken from `git log`; a round = one `round` number in
`verdicts[]`." Attempted to game this to make the table look artificially
cheap: an implementer could bundle multiple review rounds' worth of verdicts
into fewer review-only commits, reducing the counted checkpoint number without
reducing actual review work. But the table is produced by "the blind-runner at
branch end from `git log` and `review.json`, so the numbers are recomputed by
someone who did not produce them" (Design decision, "Checkpoint-cost table")
— an independent fresh-context recompute from the actual repository state, not
a self-report — and REQ-4 itself states "no coefficient is changed" and the
Design decision states "Recommendation only — the decision is deferred to the
second and third real change." So (i) gaming the *count* would require
actually doing less review work (a real behavior change, not a fabricated
number — self-defeating for anyone trying to look cheap while still shipping
correctly reviewed work), and (ii) even a genuinely lower number changes
nothing mechanically this round — no gate, no coefficient, no acceptance
criterion reads this table. Confirmed it doesn't matter for this change.
Not reported as a finding.

### (d) `plugin_version()` attribution for both layouts

Covered in full under §1 above (the round-7 nit). Re-verified independently
here against the actual installed plugin cache directory listing (not just
the spec's own claim) — see §1. Both layouts check out. No new finding.

## 3. Principles and REQ/Design consistency

No sentence in v9 assigns the user a quality-catching role or presents a
prose-only mechanism as a guarantee — "The user reads no diff at any point"
(REQ-1) is consistent with Non-negotiable 1; the merge-proof sentence stays
qualified at both points it appears (Design decision 1's "on the assumption
that the trunk receives only merges" and REQ-1's identical clause), so
spec-C12's fix (round 6) has not regressed. `loom_checker.py --list-rules`
was run against HEAD and reports exactly 27 rules with 12 `push.*` ids,
matching the Boundary line's "rule count stays 27" and "two push rules
tightened" — no drift between the spec's claimed rule inventory and the live
checker.

Read every REQ against its corresponding Design-decision paragraph side by
side (REQ-1↔Design decision 1, REQ-2↔"`intake.confirmed` on a closed intent",
REQ-3↔"Content-bound plumbing exemption", REQ-4↔"Checkpoint-cost table",
REQ-5↔plugin bump text, REQ-6↔"Test nits"). No contradiction found in any
pair — the two sections restate the same mechanism from different angles
(user-facing sequence vs. implementation rationale) without diverging on any
concrete detail (message text, constant names, file paths, rule ids, or
counts).

**Nit — merge-at-`HEAD^` robustness is not disclosed, only its safety is
implicit.** §2(a) found that a genuine, non-malicious mid-branch
`git merge main` performed as (or immediately before) the close commit would
be refused by the checkpoint-parent check even though nothing malicious
occurred, because `HEAD^^` would then resolve to the merged-in commit rather
than the real last checkpoint. This mirrors the CRLF case round 7 already
chose not to report as a finding (a false-negative-shaped rejection, not a
bypass), and the ship-station text prescribes a specific linear sequence
(push → PR → close commit → review → review-only commit → push) that leaves no
natural place for a mid-branch merge in the first place, so the residual is
low-consequence. Fix (optional, cosmetic): a one-clause note in REQ-1 or
Design decision 1 that the close-commit sequence assumes no merge commit
lands between the last checkpoint and the close commit, and that one landing
there is rejected (fails closed) rather than silently accepted.

Verdict: PASS — fatal: 0, important: 0, nit: 1
