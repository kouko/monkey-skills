# Spec red-team — 2026-09-03-loom-post-merge-seams (round 4, v5)

## 1. Round-3 escapes under v5

**Fatal — user reads PR diff.** HOLDS (fixed). REQ-1's residual no longer names
user diff-reading as the catch. v5 replaces it with a machine round: "the
review station runs one more round over `<reviewed_sha>..<close commit>`...
two fresh-context reviewers read it under the docs + user-judgment-leak
lenses" and explicitly "the user reads no diff at any point" (spec.md:6).
Not hidden, not re-introduced anywhere else in v5 (grepped for
"smuggl|reads no diff|user is the merge gate" — only the one closing
sentence and the N/A UI-flows line remain). See §3 below for a narrower,
related tension this fix creates.

**2a reopen via branch/rebase.** HOLDS in the case v5 actually defends (case
(ii), the trunk copy, backstops case (i) when a local rebase drops the close
commit): REQ-2 "the boundary is stated exactly: case (i) holds while the
commit that introduced `closed` is in the branch's ancestry... only rewritten
ancestry does" — this is the honestly-stated bounded gap round 3 asked for,
not a silent hole. **But it ESCAPES again** when combined with new attack
§2 item (c) below: case (ii)'s trunk resolution can itself degenerate to the
attacker's own branch (via `@{upstream}`) or be skipped entirely (no trunk
resolves), at which point 2a's rebase attack has no backstop left. Not a new
instance of the *same* escape — a new escape that reopens 2a's door.

**2c whitespace-lenient grammar vs literal pickaxe.** HOLDS (fixed). REQ-2:
"`<pattern>` is rendered from the status regex's own `closed` alternative
(same whitespace tolerance), so the history search and the grammar cannot
disagree on a hand-edited line" — closes exactly the fix round 3 asked for
(derive `-G` from the grammar regex, don't hand-type a second string).

**2e symlink/copy outside `.codex/hooks/`.** HOLDS (fixed, and correctly
scoped now). Design decision: "What an agent runs by hand is not the gate —
only the hook-invoked checker's verdict is — so a copy or symlink placed
elsewhere buys nothing on Codex (red team 2e)." The absolute "on Codex... no
exemption applies" claim from v4 is gone; v5 states the invocation-path
condition explicitly instead.

**2f stale weaker cached canonical.** HOLDS (fixed). Design decision adds the
missing ordering: "after the stamp's version has been compared with the
running checker's own version, so a copy that matches a superseded release
fails before any blob is read... a copy stamped with another version simply
fails the comparison and owes a trailer." An attacker who deliberately
invokes an old cached checker by hand is covered by the same "what an agent
runs by hand is not the gate" sentence that closes 2e.

## 2. New attacks on v5

**(a) Does v5 widen the pre-existing verdicts/reviewed_sha gap?** Verified
against the actual checker: `check_verdicts` (loom_checker.py:2278) calls
`scored_verdicts` → `latest_round(usable)` (:2265), which picks the highest
round number in `review["verdicts"]` and requires ≥2 distinct reviewers, all
`PASSING_VERDICTS` — it never reads or compares any per-verdict `sha` field
to `reviewed_sha`. `check_reviewed_sha` (:1670) only compares the scalar
`reviewed_sha` string to `HEAD^`. So today, for *any* post-branch-end-pass
commit, an agent can hand-edit `reviewed_sha` to `HEAD^` and add/keep a
`verdicts` round with 2 PASSing entries that reviewed something else
entirely — REQ-1's residual states this accurately as pre-existing.

Where the "not widened" claim is too strong: this spec turns what was
previously an edge case (an occasional commit landing after a branch-end
pass) into a **mandatory, once-per-ship step** — every single shipped change
now creates exactly this kind of commit (the close commit) by design, with
the review round it needs enforced only by the ship-station's prose text,
never by a rule (the spec itself says so: "stopped by the ship station's
text, not by a rule"). The rule's *shape* is unchanged, but the *frequency*
at which the pre-existing gap is exercised in the guaranteed critical path
goes from occasional to 100% of ships. Rewrite the residual to say
"institutionalizes an existing gap into the standard flow" rather than "not
widened" — the reader should know this exact skip-and-forge move is now the
single most-repeated place in the whole ship flow where it could be tried.
No fix requiring a rule-shape change is available under the stated
Constraint; the ask is honesty about exposure, matching how the CI residual
is already phrased two sentences later.

**(b) Can a `closed` line reach the trunk without a merge of a reviewed
branch?** Yes. REQ-1's Design decision states as fact: "the closed line
lands on the trunk with the squash and nowhere else, so a `closed` on the
trunk is itself the proof of the merge — no PR-number verification is needed
and none is done." Verified against this repo's actual GitHub branch
protection (`gh api repos/kouko/monkey-skills/branches/main/protection`):
`"enforce_admins":{"enabled":false}` and
`"required_pull_request_reviews":{"required_approving_review_count":0}`.
The repo owner (the same person running the agent) can
`git push origin HEAD:main` directly, writing a `closed` status straight
onto the trunk with zero PR, zero merge, zero review round — branch
protection does not stop an admin, and CI checks run on push to `main` too
(they don't gate who can push, only what merges via a status check UI
that an admin can also bypass by pushing directly). The design's "no
PR-number verification is needed and none is done" is stated as an
unconditional security property of the mechanism; it is actually an
unstated assumption about GitHub configuration the checker does not enforce
and this repo does not currently have. Fix: state this as a residual
("assumes admins do not push directly to trunk; not enforced by
`enforce_admins`, not checked by loom") rather than asserting it flatly, or
note that `enforce_admins` would need to flip to `true` for the claim to
hold.

**(c) Reopen check (`intake.confirmed` case (ii), the trunk copy) — three
sub-escapes, verified against `TRUNK_CANDIDATES` and `branch_base` (loom_checker.py:376, 410-447):**

- *No trunk resolves at all.* REQ-2 says case (ii) is "skipped when none
  does" — this is not merely staleness, it is total absence of the backstop.
  In a shallow / single-branch clone that never fetched `origin/main` or
  `main` and has no upstream configured, case (ii) contributes nothing, and
  combined with 2a's local rebase, case (i) is also empty — a reopen is
  clean with *zero* of the two stated defenses live. The stated residual
  ("case (ii) is as current as the last fetch of the trunk ref — no network
  is touched, and a never-fetched trunk ref is the stated residual") reads
  as describing staleness, not this stronger "there is no trunk ref at all"
  case; the two should be distinguished, because "stale" implies partial
  protection and "skipped" implies none.
- *`@{upstream}` resolving to the attacker's own branch.* `TRUNK_CANDIDATES
  = ("origin/main", "main", "origin/master", "master", "@{upstream}")` — the
  last candidate is not guaranteed to be trunk at all. In the same clone
  shape as above (no local `main`/`origin/main`), if the change branch has
  been pushed once and tracks its own remote copy, `@{upstream}` resolves to
  `origin/<change-branch>`, i.e. a copy the attacker fully controls and can
  force-push without the close commit — the "second, independent" defense
  degenerates to re-checking the attacker's own branch against itself.
  REQ-2's residual language ("as current as the last fetch") implicitly
  assumes the resolved candidate genuinely names trunk; it does not
  distinguish "trunk data is stale" from "the resolved ref is not trunk at
  all." Fix: drop `@{upstream}` from the candidate list used for this
  specific check (it is fine for `branch_base`'s diff-recomputation purpose,
  where the failure mode is merely "no diff to test," but wrong for a
  security backstop whose whole job is to check something the attacker does
  not control), or require the resolved candidate be one of `origin/main` /
  `main` / `origin/master` / `master` specifically for case (ii).
- Both of the above compose with round-3's 2a (branch/rebase reopen): a
  determined attacker who prepares the clone shape above gets a clean
  reopen with no defense engaged at all, not merely a "bounded, accepted"
  gap.

**(d) Plumbing exemption self-identification path is inconsistent with the
scaffold's actual layout, verified against `codex_scaffold.py` and the
`.codex/hooks/` tree actually checked into this repo:**
`CONTRACT_COPY = f"{HOOK_DIR}/contract"` = `.codex/hooks/contract`
(codex_scaffold.py:94), i.e. the copied contract package is a **sibling
inside the same directory** as `.codex/hooks/loom_checker.py` — confirmed on
disk: `.codex/hooks/loom_checker.py` and `.codex/hooks/contract/manifest.yaml`
both exist directly under `.codex/hooks/`. But the Design decision's
self-identification rule is stated as a single fixed offset: "it identifies
itself by `Path(__file__).resolve()` **plus** a contract package beside it
(`../contract/manifest.yaml` relative to its own directory)." That offset is
correct for the plugin-checkout / this-repo layout (`loom-code/scripts/` and
`loom-code/contract/` are siblings of `loom-code/`, so `../contract/` from
`scripts/` is right) — but it is the *wrong* offset for the Codex scaffold's
own layout, where the sibling contract sits one level *lower*
(`./contract/`), not one level up. As written today this happens not to
create an escape (the Codex branch is excluded first, by the explicit
"under `.codex/hooks/`" path check, so the offset is never actually
evaluated for that case) — but the prose describes a single relative rule
serving two structurally different layouts, and an implementer following it
literally for, say, a third host with a different scaffold shape could
misclassify a genuine canonical as absent, or (if the explicit
"`.codex/hooks/`" exclusion is ever refactored away in favor of relying on
"has no contract package beside it" alone) misclassify a decoy. Fix: state
the contract-package location as "wherever the scaffold puts it for that
host" and cite `CONTRACT_COPY`/`codex_scaffold.py` as the source of truth for
Codex, rather than giving one relative-path formula for both hosts.

**(e) REQ-4/5/6 vacuous-satisfaction check.** No new escape found beyond
round 3's conclusion. REQ-4's "one line of recommendation" could in
principle be a content-free "no change recommended," but that is the
Design decision's own explicit intent ("Recommendation only — the decision
is deferred"), not a smuggled gap. REQ-5's acceptance is checkable by
literally running the named commands; nothing lets it pass without the
plugin actually being updated. REQ-6 is five `file:line`-pinned nits with a
green package command — fully falsifiable.

## 3. Principles

The fatal from round 3 (user as the merge-quality gate) is fixed and not
reintroduced. One narrower, related tension remains, not squarely
acknowledged:

REQ-1's close-commit round requires "each [reviewer] must state that the
delta is that one status line and nothing else" — this is the *only*
mechanism catching a docs-typed file smuggled into the close commit. The
"Alternatives considered" section explicitly names and rejects the
mechanical version of this exact check: "A checker rule asserting the close
commit's diff shape (round-3 fix proposal) — rejected: a 28th rule against
the Constraint and PRINCIPLES.md principle 4's budget." That is a real,
stated trade-off — but PRINCIPLES.md's Won't-do line reads flatly "Add
prose-only gates; a rule that must block lives in the checker," and Non-
negotiable #3 reads "no gate trusts a claim written by the agent it checks."
A reviewer's own verdict stating "the delta is one line" is exactly a claim
written by the agent being trusted, on a fact (`git show --stat <sha>`) that
is trivially machine-recomputable and was in fact already designed once
(round 1) before being dropped for budget reasons. Because fresh-context
review is elsewhere in this same constitution treated as one of the three
sanctioned "machine" actions (Non-negotiable #2 names it explicitly), this
is defensible as *consistent with existing system-wide practice* rather than
a new violation — every other reviewed commit in this whole system relies on
the same unverified reviewer-stated claim. But the spec's own alternatives
section frames the rejection purely as a *mechanism-budget* trade-off
(Non-negotiable #4) and never states the tension against Won't-do's literal
"prose-only gate" wording or Non-negotiable #3's "no gate trusts a claim"
wording — the residual paragraph in REQ-1 lists two other residuals
explicitly but omits this one. Fix: add one clause to the stated residuals
naming this trade-off explicitly (budget vs. the Won't-do line), the same
honest treatment already given to the verdict-sha gap and the CI gap two
sentences later.

## Verdict
NEEDS_REVISION — fatal: 0, important: 5 (a: "not widened" residual undersells frequency increase — verdicts/reviewed_sha gap now on the guaranteed critical path of every ship; b: "no PR-number verification is needed" overstates a property this repo's own branch protection does not enforce — enforce_admins:false, required_approving_review_count:0, verified via `gh api`; c: case (ii) trunk backstop can be skipped entirely or degenerate to the attacker's own branch via `@{upstream}`/no-trunk-resolves, reopening 2a's combined attack; d: the stated `../contract/manifest.yaml` self-ID offset does not match the Codex scaffold's actual `.codex/hooks/contract/` sibling-in-same-dir layout, verified against codex_scaffold.py:94 and the repo's own `.codex/hooks/` tree; §3: the close-commit shape check is a prose-only reviewer claim whose tension with PRINCIPLES.md's Won't-do line is not named among REQ-1's stated residuals), nit: 0.
