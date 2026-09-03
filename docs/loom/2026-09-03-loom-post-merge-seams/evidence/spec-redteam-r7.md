# Spec red-team — 2026-09-03-loom-post-merge-seams (round 7, spec v8)

Scope: docs/loom/2026-09-03-loom-post-merge-seams/spec.md (v8). Verified against
loom-code/scripts/loom_checker.py at HEAD (923fb84a): `check_review_only_head` :1557,
`check_reviewed_sha` :1670, `scored_verdicts`/`check_verdicts` :2265/:2278,
`latest_round` :293. Also verified `loom-code/scripts/codex_scaffold.py`
(`plugin_version`/`PLUGIN_ROOT` :100-145) and `loom-code/skills/ship/SKILL.md` (push is
invoked exactly once per branch: "the only station that exercises the deterministic push
gate," :11) and `loom-code/skills/review/SKILL.md` (:302-306, review-only commit shape;
:317-323, the wave-end-that-is-also-branch-end exemption). The checker code itself is
still unchanged by this branch — v8 is a design spec for a future implementation.

## 1. Round-6 findings under v8

**spec-R21 (scope-label exemption → sha on every latest-round verdict, no exemption).**
HOLDS. spec.md REQ-1: "There is no exemption by `scope`: a scope label is a claim, not a
recompute (round 6 spec-R21), so a mixed round with one untied verdict fails, and a
spec-only round — which records `spec_sha` for `intake.spec-pass` and vouches for a blob,
not a commit — is simply never a round a push can ride on." The mislabeling attack round 6
found (a `scope: spec` verdict exempted from the sha tie by string alone) is gone: v8's
rule text no longer keys the exemption off `scope` at all — every verdict of the latest
round, unconditionally, must carry a resolving `sha`. Traced against `latest_round` (:293,
global max by `round` number, not scoped): as long as round numbers strictly increase
across the whole `review.json` (true for every station-driven flow — a spec round always
precedes the first code checkpoint that push actually rides on), a spec round is never
"the latest round" at push time, so it never needs to satisfy the tie and never gets a free
pass either. Traced legitimate flows for breakage (task item a): a spec-only round before
build never reaches push (push runs once, at ship, after at least one code checkpoint —
`loom-code/skills/ship/SKILL.md:11` "only station that exercises the deterministic push
gate"); the first push of a branch is not special-cased anywhere in the text and needs no
exemption; the wave-end-that-is-also-branch-end round (`review/SKILL.md:317-323`) still
produces the same review-only commit via the same `git commit` step (:302-306) regardless
of which scope string is recorded, so its verdicts still carry `sha` the same as a plain
`branch-end` round — no break. HOLDS.

**spec-R22 (two-commit dodge → HEAD^^ must be a checkpoint whose reviewed_sha resolves to
its own parent).** HOLDS for the literal round-6 attack. spec.md REQ-1: "its parent
`HEAD^^` must itself be a checkpoint, i.e. a commit that touches only `review.json` and
whose `review.json` records a `reviewed_sha` resolving to `HEAD^^^`... so no commit can sit
between the last checkpoint and the close commit without a checkpoint of its own." Traced
the exact round-6 shape (`R1 → A → C → R2`, task item b "can two close commits chain" and
"the two-commit dodge"): at push time `HEAD^^` = the commit immediately before the close
commit. If that commit is anything other than a bare review-only commit (an interposed
content commit `A`, or a second close commit `C1` with no review-only wrapper of its own),
`check_review_only_head`'s shape test on `HEAD^^` fails (`A` or `C1` touches paths other
than `review.json`), closing exactly the escape round 6 named. Traced the legitimate
double-close case (this change's own diff closes both `2026-09-02-simple-loom-flow` and
itself) — REQ-1's own text: "The already-merged intent ... is closed the same way inside
this change's own diff," meaning it needs its own close-commit + review-only pair; chaining
`R0 → C1 → R1 → C2 → R2` satisfies the new rule at each push exactly because each close
commit gets its own review-only wrapper. HOLDS for the literal round-6 dodge, and does not
break the legitimate double-close flow. **A narrower, new escape in what this same
recompute detects (not the round-6 dodge) is reported in §2(b) below — it does not reopen
spec-R22 as stated, but it is the same category of gap the tightening exists to close, via
a different trigger (a merge commit rather than an interposed content commit).**

**spec-C12 (merge-proof sentence qualified).** HOLDS. Round 6's codex fatal named exactly
this contradiction: REQ-1 (spec.md:6) unconditionally claimed "`closed` reaches the trunk
only by the merge" while the Design decision (spec.md:19) already conceded an admin can
push `closed` straight to `main`. v8's REQ-1 now reads: "under the stated assumption that
the trunk receives only merges (Design decision 1), `closed` reaches the trunk only by the
merge" — the same qualifying clause codex asked for, verbatim at the point of the claim,
consistent with Design decision 1's own wording ("so a `closed` on the trunk is the proof
of the merge **on the assumption that the trunk receives only merges** — loom does not
verify the PR number and does not check who can push to the trunk"). Both places now agree.
HOLDS.

## 2. Attacks on v8

### (a) The sha tie with no scope exemption

Verified `check_verdicts` (:2278-2300) does not branch on `scope` today and `scored_verdicts`
→ `latest_round` (:293) picks strictly the max `round` number, global across the array — a
fact v8's rule text relies on and that holds under every traced flow (see §1 above; no
repeat here). No break of the spec-round-only case, the first push of a branch, or the
wave-end-that-is-also-branch-end exemption in the review station.

**Does a round that reviewed an older delta still vouch?** Only by forging the `sha` field
itself (writing the correct-looking git object id of the current `HEAD^` in a verdict that
did not actually review that tree). `git rev-parse --verify` resolution (mirroring
`check_reviewed_sha`'s own existing pattern) defeats a garbage or non-existent sha, and a
literal forged-but-correct sha is squarely inside the system's own declared boundary
(loom_checker.py §0: "a forged record is out of scope," echoed for `dispatch[]`) — the same
boundary every review round has always rested on (a reviewer's honesty that it actually read
the diff is never machine-verified beyond identity/dispatch checks). Not a new gap; not
reported as a finding.

### (b) The checkpoint-parent chain

**Merge commit as `HEAD^` — new, unaddressed detection gap (important).** Anchor:
spec.md REQ-1, the new shape recompute: "if `git show --raw --no-renames HEAD^` touches an
intent file whose `status:` line changes to `closed …`, that commit must touch exactly that
one file [and] its diff ... must consist of exactly one removed and one added line." `git
show` on a merge commit prints **no diff at all** by default (no `-m`/`-c`/`--cc`/
`--first-parent` flag is specified anywhere in the spec's recompute), so if `HEAD^` is a
merge commit whose resulting tree happens to carry a `closed`-transition on an intent file
(e.g. a conflict resolved by keeping the side that already had `status: closed …`, or a
merge deliberately crafted to introduce it), `git show --raw --no-renames HEAD^` returns an
**empty** listing. The detector's own trigger condition ("touches an intent file whose
status line changes to closed") therefore never fires — not because the commit is safe, but
because the tool used to look never reports merge diffs by default. When the trigger does
not fire, nothing else in the recompute (or in `check_review_only_head`/`check_reviewed_sha`,
which never inspect `HEAD^`'s shape at all in the ordinary case) imposes any file-count or
line-count restriction on `HEAD^`. A merge commit at that position could therefore introduce
`closed` while touching arbitrary other files and lines, entirely invisible to the
recompute this tightening exists to provide — exactly the class of gap spec-R22 was written
to close (an unreviewed transition of the status line riding to `reviewed_sha` unchecked),
reached through a different vector (a merge, not a plain interposed commit) than the one
round 6 named. Nothing in the Constraints, Design decision, or Alternatives sections
forbids or disclaims a mid-branch merge commit (the single disclosed assumption, "the trunk
receives only merges," is about the *final* PR merge onto the trunk, not about merge
commits appearing mid-branch during feature work — a realistic operation on a long-lived
branch, e.g. `git merge main` to pick up upstream fixes). **Fix**: either (i) require the
recompute to run `git show --raw --no-renames -m --first-parent HEAD^` (or check
`git rev-list --parents -1 HEAD^` has exactly one parent) and refuse `HEAD^` outright when
it is a merge commit, or (ii) state as a residual, with the same honesty pattern as spec-S8/
spec-R19, that a merge commit at `HEAD^` is not shape-checked and therefore this recompute
does not defend against one.

**Two close commits chaining directly (no review-only wrapper between them) — attempted,
does not break.** Traced above in §1; `check_review_only_head` on the interposed commit
fails structurally. Recorded as a pass, not a finding.

**Stale/forged `review.json` on the ancestor checkpoint — attempted, does not break, and is
not new to v8.** The new rule checks only the ancestor's *shape* ("the two shapes this rule
and `push.reviewed-sha` already demand of HEAD," spec.md REQ-1 — explicitly shapes, not
verdict content) rather than re-running `check_verdicts`/the sha tie on that ancestor round.
Traced whether this reopens anything: `loom_checker.py push` is invoked exactly once per
branch, at ship (`ship/SKILL.md:11`), and REQ-1's own prescribed sequence is two separate
pushes — one right after the branch-end round passes (at which point the branch-end round
*is* the latest round and gets the full `check_verdicts` + sha-tie treatment), and a second
after the close-commit round. So the ancestor checkpoint the chain rule inspects was, in the
ordinary sequence, already fully content-checked at its own, earlier push. An agent that
skips the first push entirely and does everything in one shot at the end reduces to
forging the ancestor round's verdicts wholesale — which is, again, squarely the declared
"forged record is out of scope" boundary, identical to the pre-existing trust model for
every earlier wave-end round in the current (pre-v8) architecture (only the latest round has
ever been content-checked by push; earlier rounds have never been re-verified). Not a new
v8-introduced gap; not reported as a finding.

**Close commit as the first commit after a "wave-end that is also branch-end" round —
attempted, does not break.** That round still produces the ordinary `git commit -m
"chore(loom): checkpoint review — <scope> <verdict>"` review-only wrapper regardless of the
`scope: branch-end` relabeling (`review/SKILL.md:302-306`, `:317-323`), so `HEAD^^` for the
close commit is still a genuine review-only commit either way. No break.

### (c) The `-U0` one-removed-one-added diff shape

**CRLF / BOM introduction alongside the status change — attempted, fails safe, not an
escape.** If a commit also flips line endings (or inserts a BOM) across the file, every
line's bytes differ, so `git diff -U0` reports far more than one removed/added line and the
shape check correctly rejects. This is a false-negative-shaped robustness risk (a
legitimate close commit made under a different EOL convention might be wrongly rejected),
not a bypass, so not reported as a finding.

**Second `status:`-matching line elsewhere in the file — attempted, does not break.** The
count is "exactly one removed and one added line" for the **whole file's** diff, not
anchored to the frontmatter block specifically. In principle a decoy pair (remove one
stray status-matching line elsewhere, add one status-matching line elsewhere) could satisfy
the shape test without the real frontmatter `status:` field ever changing — but that
decoy pair *consumes* the entire "exactly one removed, one added" budget, leaving no room
for the real frontmatter line to also change in the same commit. So an attacker can have
the decoy-shape-check-satisfying pair, or the real frontmatter transition, but not both in
one commit — and a decoy-only commit doesn't achieve anything (the file's real `status:`
field, read by `intake.confirmed`/`parse_document`, stays `confirmed`, so nothing is
actually closed). No exploitable asymmetry found; not reported as a finding.

### (d) The `-G` pattern and STATUS regex text

`git log --format=%H -G'^status:[[:space:]]*closed '` is anchored at line start and shares
the `closed` alternative's literal text with the frontmatter-parsing regex ("the pattern
cannot drift from the grammar because it is derived from it," spec.md REQ-2). Checked for a
legitimate `closed` line the pattern would miss: none found — the anchor and whitespace
class match `_FRONTMATTER_LINE`'s own tolerance. Checked for a non-closed line the pattern
would false-positive on: a commented-out or fenced-code-block instance
(`# status: closed …` or inside a ``` block) does not match `^status:` at all (the `# `
prefix breaks the anchor), so no false positive there. `-G`'s pickaxe semantics (match-count
delta between parent and child blob) also correctly catches both the introduction *and* a
later removal of a closed line, and the very first commit of a file (no parent) is handled
the same way pickaxe always is. No escape found.

### (e) `codex_scaffold.plugin_version()` — the running checker's tree root

**Nit — the "running checker's own version" attribution is imprecise, though currently
harmless.** spec.md Design decision 3 ("Content-bound plumbing exemption") says the copy's
stamp line is compared against "the running checker's own version — `codex_scaffold.
plugin_version()`, read from the `.claude-plugin/plugin.json` of the tree the checker runs
from." But `plugin_version()` (`codex_scaffold.py:144-145`) reads `PLUGIN_JSON`, computed at
module scope from `codex_scaffold.py`'s **own** `__file__` (`PLUGIN_ROOT = Path(os.path.
abspath(__file__)).parent.parent`, :100) — not from `loom_checker.py`'s invoked path (the
actual "running checker" `Path(__file__)` the design decision uses elsewhere for
self-classification). This resolves to the correct tree only because `codex_scaffold.py` and
`loom_checker.py` are always committed as siblings in the same `scripts/` directory in both
layouts checked (this repo: `loom-code/scripts/{loom_checker.py,codex_scaffold.py}` next to
`loom-code/.claude-plugin/plugin.json`; the plugin cache:
`.../loom-code/1.0.1/scripts/{...}` next to `.../loom-code/1.0.1/.claude-plugin/
plugin.json`) — verified both resolve correctly today. But nothing in the spec states this
sibling-colocation as an invariant the checker asserts or a test pins, so a future refactor
that separates the two files (or vendors `codex_scaffold.py` into a different location while
`loom_checker.py` stays put) would silently read the wrong `plugin.json` with no failure
surfaced anywhere. **Fix**: either say explicitly that `plugin_version()`'s correctness for
this comparison depends on `codex_scaffold.py` and `loom_checker.py` remaining siblings (and
that this is asserted somewhere, e.g. a test), or have the exemption check pass the
checker's own invoked directory into the version lookup instead of relying on
`codex_scaffold.py`'s independent computation of its own tree root.

## 3. Principles

No sentence in v8 assigns the user a quality-catching role, and the merge-proof sentence
that round 6 flagged as an unqualified guarantee is now qualified at both points it appears
(§1, spec-C12). The already-disclosed residuals (single-user gate-shaping, stale/fabricated
trunk ref, CI not running the push gate, the Codex trailer-duty follow-up) each carry the
same honest framing as prior rounds.

The one new gap this round found that is genuinely in the same category as those residuals
— the merge-commit detection hole in §2(b) — is **not** disclosed anywhere in v8, and unlike
the pre-existing residuals it is newly-introduced surface area created by this specific
tightening's wording (an artifact of using `git show`'s default, non-merge-aware diff mode
as the detector), not an inherited trade-off the whole architecture already rests on. This
is the same shape of gap Non-negotiable 3 ("no gate trusts a claim written by the agent it
checks") and the Won't-do line ("Add prose-only gates; a rule that must block lives in the
checker") exist to prevent — here the checker doesn't even reach the point of trusting a
claim, because its own detection step silently no-ops on a merge commit. Recommend either
closing it mechanically (§2(b) fix i) or disclosing it as a named residual with the same
honesty pattern as spec-S8/spec-R19 (§2(b) fix ii) before this ships.

Verdict: PASS_WITH_NOTES — fatal: 0, important: 1, nit: 1
