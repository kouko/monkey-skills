# Spec red-team — 2026-09-03-loom-post-merge-seams (round 5, v6)

Scope: docs/loom/2026-09-03-loom-post-merge-seams/spec.md (v6, commit 20d5bad0).
Verified against loom-code/scripts/loom_checker.py and loom-code/scripts/codex_scaffold.py
at HEAD (4e25360c — the checker itself is unbuilt for this change; v6 is a design spec,
so "verify against code" means: does the current code's actual behavior support the
claims v6 makes about it, and is the proposed mechanism internally sound against that code).

## 1. Round-4 findings under v6

**(a) "not widened" wording.** HOLDS — fixed, honestly reworded. spec.md:6:
"The gap exists today for every commit made after a branch-end pass; this change does
not change its shape but it does institutionalise it — every shipped change now makes
exactly one such commit, so the exposure moves from occasional to once per ship." This
is exactly the requested rewrite (frequency disclosed, not "not widened").

**(b) closed reaches trunk by direct admin push.** HOLDS — fixed. spec.md (Design
decision 1): "the closed line lands on the trunk with the squash and nowhere else, so a
`closed` on the trunk is the proof of the merge **on the assumption that the trunk
receives only merges** — loom does not verify the PR number and does not check who can
push to the trunk; this repo's own branch protection leaves `enforce_admins` off with
zero required approvals, so an admin pushing `closed` straight to `main` is not caught by
anything here (stated assumption, not a property; out of scope with the other multi-user
cheating cases)." The unconditional-property framing round 4 objected to is gone.

**(c) trunk resolution absent / @{upstream}.** HOLDS — fixed. spec.md:8: case (ii)'s
`<trunk>` is now explicitly "the first of `origin/main`, `main`, `origin/master`,
`master` that resolves — **not** `@{upstream}`, which `TRUNK_CANDIDATES` keeps for
`branch_base` but which may name the change branch's own remote copy; when none of the
four resolves, case (ii) is absent, not stale, and the checker prints that it is absent."
Verified `TRUNK_CANDIDATES = ("origin/main", "main", "origin/master", "master",
"@{upstream}")` at loom_checker.py:376 — v6 correctly identifies `@{upstream}` as the
fifth, dropped candidate and correctly distinguishes "absent" from "stale." All three
sub-escapes of round-4 (c) are closed: no-trunk-resolves is now explicitly "absent, not
stale"; `@{upstream}` degeneracy is closed by exclusion; the compose-with-2a case was
already disclosed in v5 ("a clone with no trunk ref at all... has neither check live")
and remains disclosed in v6, still spec.md:8.

**(d) contract-package offset vs the Codex scaffold layout.** HOLDS — fixed. spec.md:21
(Design decision 3): "a contract package in the place its own layout puts it —
`../contract/manifest.yaml` for a plugin checkout or this repo (`scripts/` beside
`contract/`), while the Codex scaffold writes `contract/` inside `.codex/hooks/` itself
(`codex_scaffold.CONTRACT_COPY`, the source of truth for that layout)." Verified against
codex_scaffold.py:94-96: `CONTRACT_COPY = f"{HOOK_DIR}/contract"` = `.codex/hooks/contract`,
a sibling of `.codex/hooks/loom_checker.py`, matching the disk layout
(`.codex/hooks/loom_checker.py` + `.codex/hooks/contract/manifest.yaml` both confirmed
present). v6 now states two layouts, cites the source of truth for each, rather than one
relative-path formula for both hosts.

**§3 (reviewer-claim vs prose-only-gate tension).** HOLDS — fixed. spec.md:6, REQ-1
residual (2): "this sits in tension with PRINCIPLES.md's Won't-do line on prose-only
gates and Non-negotiable 3, and is chosen over a 28th rule for Non-negotiable 4's budget
and the Constraint — the same trade-off every reviewed commit in this system already
rests on, named here rather than assumed." This explicitly names both PRINCIPLES.md
lines round 4 found un-cited, alongside the other two residuals, matching the "same
honest treatment" fix round 4 asked for.

**Sonnet's downgraded-plugin residual.** HOLDS — fixed. spec.md:21 (Design decision 3):
"Stated residual (round 4 spec-S8): a loaded plugin that is itself a deliberately older
version is its own, older canonical — loom checks no freshness against the newest cached
version or the trunk's `plugin.json`; on a single-user machine this is the user
downgrading their own gate, and it goes to the same follow-up intent as the Codex
scaffold-commit seam." v6 no longer asserts "not ambiguous" — it discloses the gap with
the same shape as the R9/S7 residuals sonnet asked for.

## 2. New attacks on v6

**(1) — important — fabricated/foreign local ref satisfies case (ii) without being
trunk data at all.** Anchor: spec.md:8 ("the trunk's copy of the file parses as
`closed`... `<trunk>` being the first of `origin/main`, `main`, `origin/master`,
`master` that resolves"). v6 correctly drops `@{upstream}` so the *name* resolved can no
longer be the attacker's own branch by tracking-config accident (round-4 (c)). It does
not address a stronger version of the same problem: any of the four remaining candidate
*names* is itself just a ref lookup by string, and nothing about "resolves" implies "was
populated by a real fetch of the real trunk." Verified against the existing resolution
pattern this design explicitly reuses (`branch_base`, loom_checker.py:410-447): it calls
`git merge-base HEAD <candidate>` / (by extension for case (ii)) `git show
<candidate>:<path>` on whatever ref by that name exists in the local repo, with zero
check that it came from a real `git fetch origin`. A repo owner can create a local
branch `main` (`git branch main <arbitrary-old-sha>`) or a synthetic remote-tracking ref
(`git update-ref refs/remotes/origin/main <arbitrary-old-sha>`) that was never fetched
from anywhere, entirely locally, without touching a network. Case (ii) then "resolves" —
prints no diagnostic, reports a confident non-closed result — against data the checker
never verified came from trunk at all. This differs materially from the two residuals v6
already states ("a stale trunk ref... gives partial protection" and "a clone with no
trunk ref at all... has neither check live"): those two describe honest degrees of
staleness or honest absence (and the absent case now prints that it is absent, per fix
(c)). A fabricated-but-present ref is a third case v6 does not name: it looks identical
to a genuinely fresh, correct check from the outside (no diagnostic, a definite verdict)
while checking nothing real. Fix: state this third case as a residual alongside the
other two — "case (ii) trusts whatever local ref resolves under these names; it does not
verify the ref was populated by a real fetch, so a locally-fabricated or stale-and-never-
refreshed ref of the right name is indistinguishable from a genuine one" — or (mechanism
change, follow-up intent per the Constraint) have case (ii) additionally record and print
the resolved ref's commit date/reflog provenance so a human can sanity-check it.

**(2) — important — a symlinked `.codex/hooks/loom_checker.py` flips the checker's own
self-classification from "is the copy" to "is the canonical."** Anchor: spec.md:21
("the checker doing the push is the file the host hook invokes... and it identifies
itself by `Path(__file__).resolve()`... The order of the test matters: a checker under
the repo's `.codex/hooks/` is the copy and is excluded first"). `Path.resolve()` follows
symlinks to their real target by construction — that is its documented purpose. If a
user (single-machine, has both Codex and a monkey-skills plugin checkout or this repo
present) replaces the scaffolded `.codex/hooks/loom_checker.py` with a symlink to the
genuine canonical (`~/.claude/plugins/cache/monkey-skills/loom-code/<v>/scripts/
loom_checker.py`, or this repo's `loom-code/scripts/loom_checker.py`), the *same file*
Codex's shim invokes (`SHIM_TEMPLATE`: `exec python3 {checker} push --hook`, checker =
`.codex/hooks/loom_checker.py`, codex_scaffold.py:126) resolves, via `.resolve()`, to a
path *outside* `.codex/hooks/`. Under the stated classification rule ("a checker under
the repo's `.codex/hooks/` is the copy and is excluded first"), this checker no longer
tests as "under .codex/hooks/" — it falls through to the canonical branch, finds a
genuine `../contract/manifest.yaml` beside its resolved location (because it really is
sitting inside a genuine plugin/repo checkout), and grants itself an exemption for
plumbing-path edits — exactly the outcome REQ-3's closing sentence says must not happen
("When the checker doing the push is the copy (Codex in an adopting repo) there is no
canonical to compare against and no exemption applies — every plumbing edit keeps
trailer duty, exactly as today"). Installing the symlink itself is one trailer-carrying
commit (a mode/content change under `.codex/hooks/`, per REQ-3's own "altered... or
mode-changed entry... counts as gate work"), but every *subsequent* refresh of
`.codex/hooks/contract/*` on that machine is then classified as canonical-comparable and
exempt — a one-time trailer buys a standing exemption the design says Codex must never
have. This is not round-4's 2e (a decoy elsewhere) or 2f (an old checker run by hand): it
is the actual hook-invoked file, genuinely executed by Codex's trusted shim, whose
*self-report of its own location* the design's own chosen primitive (`.resolve()`)
falsifies. Fix: classify "is the copy" by the *invoked* path (`sys.argv[0]` / the shim's
literal `{checker}` argument, or `Path(__file__)` without `.resolve()`, i.e. the path
Codex actually ran) rather than the symlink-resolved real path, or explicitly reject a
non-regular-file (symlink) at `CHECKER_COPY`/`SIBLING_MODULES` paths as itself always
gate work regardless of blob content.

**(3) — nit — two same-purpose candidate lists risk drift.** Anchor: spec.md:8. The v6
fix for (c) defines a second, unnamed four-item trunk-candidate list (a subset of
`TRUNK_CANDIDATES` minus `@{upstream}`) alongside the existing `TRUNK_CANDIDATES` used
by `branch_base` (loom_checker.py:376). Nothing in the spec names this second list or
says it must not simply reuse `TRUNK_CANDIDATES` by reference — an implementer following
"which `TRUNK_CANDIDATES` keeps for `branch_base`" literally could reasonably reuse the
same constant for case (ii) rather than defining a second one, silently reintroducing
round-4 (c)'s `@{upstream}` escape at build time. Fix: name the second list explicitly
(e.g. `REOPEN_TRUNK_CANDIDATES`) in the Design decision so a build-time implementer
cannot collapse it back into `TRUNK_CANDIDATES` by convenience.

**REQ-3 deleted-entry clause, REQ-6 moot record — no new escape.** Verified: `commit_paths`
(loom_checker.py:2085-2092) uses `git show --raw --no-renames`, whose raw lines include
deletions (mode `000000` on the new side, status `D`) with the path still in field [1], so
v6's claim "a deleted entry is in `commit_paths()` with no blob at the commit" is accurate
and the comparison-fails-for-deletions design is sound. REQ-6's "moot" claim for R28-O2 is
confirmed: no `wc` subprocess or `check=True` skip-guard remains in
test_check_mechanisms.py (grep clean); the R30-O1/O2/O3 current-state descriptions
(recompute-not-pinned oracle at :662-669, no `inspect.getsource` guard yet) match the file
as it stands. No vacuous satisfaction found.

## 3. Principles

No sentence in v6 assigns the user a quality-catching role. "the user reads no diff at
any point" (spec.md:6) stands unqualified; the one user-facing action left (pressing
merge) is a consequence-form one-way-door choice permitted by Non-negotiable 1, not a
quality read. No prose-only gate is presented as a guarantee: the two remaining
prose-trusted claims (the close-commit reviewers' "delta is one line" statement, and now
also new finding (1)'s ref-provenance trust and finding (2)'s self-identification trust)
are either explicitly named as residuals with their PRINCIPLES.md tension stated (REQ-1
residual (2), Design decision 3's spec-S8 residual) or, for the two new findings this
round, not yet named at all — which is the substance of findings (1) and (2) above, not a
restatement of a still-open round-4 item. Non-negotiable 3 ("no gate trusts a claim
written by the agent it checked") is the same principle both new findings ultimately
sharpen: case (ii)'s ref resolution and Design decision 3's self-identification are both
facts the checker computes about *its own environment*, which the same single user who
controls that environment can also shape — a narrower, filesystem-level version of the
claim-trust concern, not a new class of violation the spec fails to acknowledge as a
category (Design decision 1 and 3 already name the single-user-shapes-their-own-gate
class explicitly) — it is missing only these two specific instances of it.

Verdict: NEEDS_REVISION — fatal: 0, important: 2, nit: 1
