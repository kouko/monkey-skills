# Spec red-team — 2026-09-03-loom-post-merge-seams (round 6, spec v7)

Scope: docs/loom/2026-09-03-loom-post-merge-seams/spec.md (v7). Verified against
loom-code/scripts/loom_checker.py at HEAD (923fb84a) and
loom-code/contract/manifest.yaml:120 (verdict grammar). Note: the checker code itself is
UNCHANGED by this branch yet — v7 is still a design spec describing a future
implementation, so "verify against code" means: is the mechanism v7 prescribes buildable,
unambiguous, and actually closed against the current code's real shape (not "does the
tightening already exist").

## 1. Round-5 findings under v7

**spec-C11 (prose-enforced close round → tightened rules).** HOLDS. v7 REQ-1 spells out
both tightenings verbatim: "`push.reviewed-sha` also requires every verdict of the latest
round whose `scope` is not `spec` to carry `sha`, and every such `sha` must resolve to the
same object as `reviewed_sha`... `push.review-only-head` also recomputes the reviewed
commit's shape when it introduces a `closed` status: ... that commit must touch exactly
that one file and its diff must change exactly that one line." This is option A, the exact
remedy Codex's round-5 fatal demanded ("fold a verdict-to-reviewed_sha comparison and the
required close-commit diff-shape recomputation into an existing checker rule"). Closes the
literal attack round 5 named (moving `reviewed_sha` by hand while verdicts describe an
older commit) — see §2 for a narrower attack the *wording* of the fix leaves open.

**spec-R19 (fabricated trunk ref → stated residual).** HOLDS. REQ-2: "a ref of the right
name that was never fetched at all — created locally (`git branch main <old sha>`,
`git update-ref refs/remotes/origin/main …`) — is indistinguishable from a real one,
because case (ii) trusts whatever local ref resolves under those four names and verifies
no fetch provenance (single-user shaping their own gate, same class as the downgraded
plugin)." Verbatim disclosure, same class-naming pattern as the round-4/5 residuals.

**spec-R20 (symlink resolve → invoked path, symlink never exempt).** HOLDS, and
strengthened past what R20 asked. Design decision 3: "it identifies itself by the path it
was **invoked** as — `Path(__file__)` without `.resolve()`... never the symlink-resolved
real path, because a symlinked `.codex/hooks/loom_checker.py` pointing at a genuine
canonical would otherwise resolve outside `.codex/hooks/` and classify itself as canonical
(round 5 spec-R20)"; and separately "a plumbing path that is a symlink at the commit (mode
`120000`) is never exempt — it is gate work whatever it points at." Both the
self-classification fix and the target-file-is-a-symlink case are covered.

**Unnamed-list nit → REOPEN_TRUNK_CANDIDATES.** HOLDS. REQ-2 names it explicitly:
"`REOPEN_TRUNK_CANDIDATES = ("origin/main", "main", "origin/master", "master")` — a
second, named constant, **not** `TRUNK_CANDIDATES`, whose trailing `@{upstream}`
`branch_base` keeps but which may name the change branch's own remote copy." An
implementer can no longer collapse the two lists by convenience.

**Cold-read mode-only gap.** HOLDS. Design decision 3: "the comparison is blob **and**
mode (`git show --raw` reports both, so a mode-only change fails like a content change)."

All five round-5 items close cleanly under v7's actual wording.

## 2. Attacks on the two tightenings

### (a) `push.reviewed-sha` verdict-sha tie

Verified against `check_reviewed_sha` (loom_checker.py:1670), `check_verdicts` /
`scored_verdicts` / `latest_round` (:2278, :2265, and the `latest_round` helper they call),
and `check_review_only_head` (:1557). Key fact confirmed in code: `check_verdicts` counts
distinct reviewers and requires all of the latest round's verdicts to carry a passing
`verdict` — it does **not** branch on `scope` at all today (:2278-2300), and nothing in
`loom_checker.py` validates the *value* of a verdict's `scope` field against what the round
actually reviewed; `scope` is free text compared only by prefix-match for the spec lens
(`spec_scoped_verdicts`, :1162-1188). Same for the review-level `review["scope"]` field.

- **Forged sha entries making a round "latest":** out of scope by the system's own stated
  convention ("§0 is explicit that a FORGED record is out of scope", loom_checker.py:2312,
  echoed for `dispatch[]`) and v7 does not rely on trusting a forged sha — it says the sha
  must **resolve** (`git rev-parse --verify`), mirroring `reviewed_id`'s own resolution.
  Abbreviated shas resolve the same way `reviewed_sha` already does; a garbage or
  non-existent sha fails to resolve and the check fails, symmetrically with the existing
  `reviewed_id is None` path. HOLDS — no escape here, and not a new attack surface.

- **`scope: spec` on a code/intent delta — FATAL, unaddressed.** Anchor: spec.md:6
  ("`push.reviewed-sha` also requires every verdict of the latest round whose `scope` is
  not `spec` to carry `sha`") and spec.md:19 ("`verdicts[].sha` is required only on
  non-`spec` scopes because a spec round reviews a blob (`spec_sha`), not a commit"). This
  exemption is keyed on the verdict's self-reported `scope` string, and nothing in the spec
  — or in the checker code it's building on — recomputes that a verdict actually was a
  `spec` review (e.g. by requiring `spec_sha` to be present and to match the spec blob, or
  by refusing `scope: spec` when the reviewed round in fact carries a `sha`-shaped commit
  delta). A round reviewing the *close commit itself* — exactly the delta this whole
  tightening exists to police — can have both its verdicts labeled `scope: spec`. Under
  v7's own rule text those verdicts then owe no `sha` at all: `push.reviewed-sha`'s new
  clause never fires, `check_verdicts` still passes (it only counts reviewers and verdict
  outcome, never scope), and `push.review-only-head`'s close-commit shape recompute (which
  only inspects the commit's own diff, not the round's paperwork) has nothing to say about
  it either. This is not a forgery of a fact the checker recomputes — `scope: spec` is a
  legitimate grammar value the manifest itself defines — so it sits outside the "forged
  record is out of scope" carve-out; it is a real gap in what the tightening actually
  binds. It exactly reopens the class of attack spec-C11 was written to close: a round that
  reviewed nothing tying to `reviewed_sha` can still vouch for it, so long as it lies about
  what kind of round it was. **Fix**: require `scope: spec` verdicts to also carry
  `spec_sha` equal to the current spec's blob (already computable — `check_confirmed_behavior`
  / `check_spec_freshness` already do this comparison elsewhere in the file), and refuse
  `scope: spec` on a round whose `reviewed_sha` names a commit rather than the spec is
  N/A — or, simpler and in the spirit of "one recompute, no waiver": drop the `scope`
  string as the sha-exemption trigger entirely and instead exempt a verdict from the `sha`
  tie only when the review record's own artifact-type recompute (the same `artifact_types()`
  the trailer rule already uses) says the reviewed delta is spec-only.

- **Mixed-scope round — same finding, sharper form.** A single round can satisfy
  `push.verdicts-ge-2` (two distinct reviewers, both passing) with reviewer A labeled
  `scope: branch-end` carrying a correct `sha` tie, and reviewer B labeled `scope: spec`
  carrying none. `check_verdicts` (:2278) never partitions by scope when counting
  reviewers, so the round "has two reviewers" for push purposes even though only one of
  them was mechanically bound to `reviewed_sha`. The design's own prose ("a round that
  reviewed an older delta cannot vouch for a newer `reviewed_sha`") is defeated by a single
  mislabeled verdict, not a wholesale forged round. Same fix as above closes this too.

- **Mixed-scope on a code delta ("wrong artifact type" dodge):** since `scope` is free
  text and not cross-checked against `artifact_types()` of the actual delta, an agent could
  label a round reviewing a genuine *code* delta as `scope: spec` for the same reason — the
  exemption doesn't distinguish "reviews the close-intent commit" from "reviews a code
  commit"; it only distinguishes the string `spec` from everything else. Same fix.

### (b) `push.review-only-head` close-commit shape recompute

Verified against `check_review_only_head` (:1557-1583, operates on `head_sha` — the commit
actually being pushed) and `check_dispatch_covers_tasks` (:2095-2160, walks
`branch_base(repo)..reviewed_id` and requires a `Task:` trailer on every commit in that
whole range whose touched paths recompute to `{code, skill, gate}` via `TRAILER_DUTY_TYPES`,
:1940).

- **Detection of "introduces a closed status":** spec.md:6 says the check reads
  `git show --raw --no-renames HEAD^`, finds an intent file whose `status:` line now
  matches the shared `closed` regex, and then requires that commit to touch exactly one
  file and change exactly one line. This is buildable and precise (same `--raw --no-renames`
  primitive `check_review_only_head` already uses for its own file-count logic, so an
  implementer has a worked pattern to copy).

- **Two intent files' status lines in one commit:** blocked structurally — "that commit
  must touch exactly that one file" fails the moment a second path appears in the `--raw`
  listing, regardless of which line in it changed. HOLDS.

- **Rename:** blocked — `--no-renames` reports a rename as a delete of the old path plus an
  add of the new one, two distinct paths in the touched set, failing "exactly that one
  file." HOLDS (this is the exact mechanism `check_review_only_head`'s own docstring already
  explains for the analogous rename-into-`review.json` case, so it is a proven pattern, not
  a hopeful one).

- **Same file's other lines changing alongside the status line:** blocked by "its diff must
  change exactly that one line" — a second changed line (even a formatting/whitespace
  change elsewhere in the file) fails the count. HOLDS, no vacuous satisfaction.

- **Dodging by closing in two commits — FATAL, unaddressed.** The shape recompute as
  specified inspects only **`HEAD^`'s own diff against its own parent** — it never re-derives
  or bounds the *range* being vouched for by the round (station-level text puts that range
  at `<reviewed_sha>..<close commit>`, but that range is nowhere recomputed by a checker
  rule; it is only what the ship-station *asks* reviewers to look at). Concretely: insert an
  ordinary content commit **A** between the previous push's review-only commit **R1** and
  the close commit **C** (`R1 → A → C → R2(review-only)`). At push time `head_sha = R2`;
  `check_review_only_head(R2)` still passes (R2 touches only `review.json`);
  `check_reviewed_sha` ties `reviewed_sha = C` to `R2^ = C`, correctly, because C is
  literally R2's parent; the new shape recompute reads `git show HEAD^` = **C's diff against
  its own parent A** — which is still exactly one file, one line, because C's own edit is
  genuinely just the status line, *regardless of what A changed*. Nothing in the recompute
  as specified ever diffs against R1 (the last point actually pinned by a prior push) or
  walks `R1..C`. If A touches a path that is not `{code, skill, gate}` in the `artifact_types()`
  table — e.g. a plain doc, a note under `docs/`, `README.md`, an evidence file — then
  `check_dispatch_covers_tasks` (which does walk the fuller `branch_base..reviewed_id`
  range) imposes **no** trailer duty on it either (`TRAILER_DUTY_TYPES = {code, skill,
  gate}`, :1940), so A is mechanically invisible to *every* push rule: not shape-checked
  (it isn't the close commit), not trailer-checked (it isn't a trailer-duty type), and its
  content is covered only by the two close-commit reviewers' prose claim that "the delta is
  that one status line and nothing else" — the exact claim REQ-1 says is "recomputed by
  `push.review-only-head`, not taken from the reviewers." That recompute, as specified, does
  not actually cover the range the claim is about; it covers only the tip commit. This is
  precisely the class Non-negotiable 3 forbids, and it directly contradicts REQ-1's own
  closing sentence: "an agent that skips the close-commit round and moves `reviewed_sha` by
  hand is now refused by `push.reviewed-sha`... **for every commit made after a branch-end
  pass and not only the close commit**" — that claim is true only if every such commit is
  independently pushed with its own review-only wrapper; it is false, as specified, for a
  content commit smuggled into the *same* push as the close commit. **Fix**: state the
  recompute's diffed range as `<the reviewed_sha recorded by the review-only commit that
  most recently PASSED push>..HEAD^` (or, simpler, require the close commit's parent to
  BE the prior review-only commit — i.e. add "and `HEAD^^` must itself be a commit that
  touches only `review.json`" to the close-commit shape rule) rather than `HEAD^`'s own diff
  alone, so an interposed content commit cannot exist between the last verified checkpoint
  and the close commit at all.

- **Conflict with the review-only commit itself being HEAD:** none — the shape recompute
  targets `HEAD^` (the close commit), a different commit than `check_review_only_head`'s own
  target (`HEAD`, the review-only commit). The two checks compose without contradiction.
  HOLDS.

### (c) Does either tightening loosen anything, waive, or change the rule count?

No loosening and no waiver in the text: both changes only ADD conditions to existing rule
ids (`push.reviewed-sha`, `push.review-only-head`); Boundary (spec.md:43) states "two push
rules tightened... none added, none loosened, rule count stays 27" and nothing in REQ-1/2/3
contradicts that arithmetic claim — no new rule id appears, no `--waive`/config escape is
introduced. However, per (a) and (b) above, the tightening as **specified** does not close
the gap it claims to close in full: it closes the literal "move `reviewed_sha` by hand"
attack round 5 named, but leaves two adjacent, unaddressed escapes (`scope: spec`
mislabeling; a non-trailer-duty content commit interposed before the close commit) that
defeat the same Non-negotiable the tightening exists to satisfy. That is a correctness gap
in the mechanism's *coverage*, not a change to the rule count or an added waiver — but it
means the REQ-1 sentence claiming the gap is now "closed... for every commit made after a
branch-end pass and not only the close commit" is not accurate as specified.

## 3. Principles

No sentence in v7 assigns the user a quality-catching role, or presents an *already-named*
prose-only gate as a guarantee — the two prose-trusted claims this design still carries
(the close-commit reviewers' "delta is one line" statement, and the single-user-shapes-
their-own-gate class) are each explicitly named as residuals with their tension stated
(REQ-1 residual, Design decision 3's spec-S8 residual, REQ-2's stated three residuals).

But the two findings in §2 are new instances of exactly the same category, and v7 does not
name them: `scope: spec` mislabeling and the interposed-non-trailer-duty-commit both let
`push.reviewed-sha`/`push.review-only-head` "pass" while a claim written by the reviewing
agent (what the round actually covered) is the only thing standing behind the gap — the
literal shape of Non-negotiable 3 ("no gate trusts a claim written by the agent it
checks") and the Won't-do line ("Add prose-only gates; a rule that must block lives in the
checker"). Unlike the already-disclosed residuals, these two are not "the same trade-off
every reviewed commit already rests on" (spec-S8's own framing) — they are specific,
newly-introduced surface area created by *this* tightening's exact wording (the `scope`
string as an untied exemption trigger; `HEAD^`-only as the shape-check's diff range), not
inherited from the pre-existing architecture. REQ-1's own closing sentence overclaims
("for every commit made after a branch-end pass and not only the close commit") in a way
the two round-5-reviewed vendors did not have the chance to catch (they reviewed v6, before
this specific tightening language existed). Recommend the spec either disclose both as
named residuals with the same honesty pattern as spec-S8/R19, or close them mechanically
per the fixes in §2 before shipping — given they defeat the literal purpose kouko's
2026-09-03 option-A decision was made to buy (closing spec-C11), disclosure alone would be
a materially weaker remedy than for the other residuals, which are genuinely orthogonal to
this change's own point.

Verdict: NEEDS_REVISION — fatal: 2, important: 0, nit: 0
