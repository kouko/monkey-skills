# Brief: requesting-code-review SKILL.md extraction pilot (E-1(b))

Date: 2026-08-05
Source: E-1 decision（user：「E1 選 b」→ 分割地圖簡報 → 受眾錯置補充 →「go」）.
Recon: read-only sweep of the file + all 8 pinning test files, 2026-08-05
(this brief transcribes the partition — the recon lives nowhere else).
Status: FROZEN.

## Problem

`loom-code/skills/requesting-code-review/SKILL.md` sits at 4498/4500
words (CHK-SKL-010 hard cap). Every contract fix now pays a net-zero
word surgery first (twice already: the union-recompute edit, the E-3
pointer). Goal: ≥600 words of durable headroom with zero behavior
change, as the pilot whose partition recipe the two other ceiling-bound
files (requesting-docs-review 4490, SDD SKILL.md 4482) will batch later
via `code-toolkit-skill-refactor-sweep`.

## Method (user-ratified composition)

loom-code flow orchestrates; `skill-dev-toolkit:skill-refactor`'s
invariant set is adopted as the acceptance bar rather than invoking that
skill's own orchestration: (a) ≥10% word cut, (b) output behavior
preserved — here operationalized as ALL existing prose-pin tests green
untouched, every pointer resolving, and cold-read probes passing, (c)
no load-bearing rule leaves the SKILL.md body (repo memory
`feedback_extract_to_reference_load_bearing_rule` governs).

## The partition (recon result, FROZEN — implementers transcribe from here)

Move — all verified zero-pin across the 8 pinning test files:

1. §"When this is different from SDD's per-task reviewer" (123 w) →
   `references/scope-comparison.md`. Inline residue: one sentence
   keeping the load-bearing distinction ("same rubrics, different diff
   scope — branch-cumulative, not per-task") + pointer.
2. §"Cross-skill contract" (159 w) → `references/cross-skill-map.md`.
   Inline residue: one line naming the delegation convention (paths not
   content) + pointer.
3. The "wrong-default rationalizations" table embedded in
   §Push-as-trigger (209 w; the section's PROCEDURE stays — only the
   table moves) → `references/push-trigger-rationalizations.md`.
   Inline residue: one line ("push-intent excuses and their refusals:
   see the reference") + pointer.
4. §"Red Flags — refuse these rationalizations" (233 w) →
   `references/red-flags.md`, following the finishing-a-development-branch
   house shape: inline residue is a one-line distillation listing the
   refusal posture + pointer. **Probe-gated**: the cold-read probe
   (below) must show a weak model still refuses under pressure; probe
   FAIL → move this section back and ship #1-3 only (recorded exit
   clause of this brief).
5. Audience-misplaced (maintainer-facing) fragments →
   `references/design-evidence.md`, whose header states it is
   author-facing and not for runtime loading (house precedent:
   brief-before-asking's "Author-only — do NOT load at runtime"):
   - the **Exit clause** paragraph (line ~198, ~30 w);
   - the §Panel union "Evidence: G4 A/B — …" sentence tail incl. the
     dogfood path (line ~196, ~45 w) — the RULE sentence ("each arm's
     own verdict: is advisory only — the gate verdict is produced by
     applying the aggregation rule … never by picking one arm's
     verdict") STAYS, it is pinned;
   - the Step-2 G4 calibration parenthetical ("and G4's evidence was
     measured on exactly the inherit configuration … extrapolating
     across tiers or diff types", line ~106, ~25 w) — the rule it
     qualifies ("Do not pin a model on either dispatch — reviewers
     inherit the session model by design: that keeps the panel's tier
     matched…") STAYS;
   - the Step-3 union-evidence parenthetical ("zero false positives
     measured across G4's 4 arms, report §Scorecard, plus the two
     same-day panel deployments recorded in PR #503/#504", line ~108)
     — the rule ("no cross-arm adjudication layer is needed") STAYS;
   - the §See-also version tag "(v0.6.0+ / P15-12 Phase 2)" (carried 🟢
     from the 0.52.0 arc) — deleted, not moved (pure archaeology).

MUST NOT MOVE:
- §Pinned refusal contract and §Pinned pass-down contract (transcribed-
  verbatim mirrors, lines ~98/~105) and the findings/simplification_ledger
  schema fence (~134-169);
- anything in §Process or §Verdict structure beyond the #5 fragments
  named above (25+/12+ pins);
- the pinned E-3 anchor fragment "a single-arm verdict is degraded
  evidence — G4 measured why" (test_rcr_capacity_pointer.py pins it) —
  its G4 mention stays inline even though it is evidence-flavored;
- the trivia tables in §When to use / §When NOT to use (row-pinned).

## Pin inventory the implementer must keep green (from recon; verify
locations before editing, lines drift)

8 test files pin this SKILL.md:
test_review_scope_stations.py (verbatim contract blocks + review_scope.py
call sites), test_docs_review_mode.py (Step-1 routing + Step-3 mixed-mint
phrases + When-to-use rows), test_docs_review_blocking_class.py
(§Verdict structure headings/phrases incl. "each arm's own `verdict:` is
advisory only" and the §Asking-the-user machine-precise sentence),
test_finding_origin_attribution.py (origin: field lines),
test_rcr_capacity_pointer.py (capacity pointer + trimmed tag + word cap),
test_code_reviewer_principles_derivation.py (self-derive/override),
test_asking_user_briefing_escalation.py (brief-before-asking triple),
test_reviewer_dispatch_role_anchor.py ("You ARE the reviewer").
None of these pins lands in move-sets #1-#4; #5 splices around pins as
itemized above. The full suite green (unmodified pin tests) is the
equivalence gate's core evidence.

## Smallest End State

1. SKILL.md ≤ 3900 words (net cut ≥ 598, ≥13%); all five destination
   files exist; every moved passage present in its destination
   (verbatim, minus purely connective rewording at splice points);
   inline residue sentences + pointers as itemized.
2. Full suite green with the 8 pin-test files UNTOUCHED (any pin-test
   edit means the partition was violated — stop and re-plan, do not
   adapt pins).
3. A new pointer-pin pytest guards the refactor itself: five pointer
   lines present, moved section headings absent from SKILL.md, present
   in destinations; word count ≤ 3900.
4. Cold-read probes CLEAN (red-flags pressure probe + a slim-file
   execution probe), recorded in a dogfood file; probe (red-flags) FAIL
   → #4 reverts per the exit clause.
5. loom-code 0.53.0 → 0.54.0, four bump deliverables; suite green
   post-commit.

## Out of scope

- requesting-docs-review and SDD SKILL.md (batch phase, later arc, via
  code-toolkit-skill-refactor-sweep).
- Any wording change to rules that stay (pure move, no rewrites beyond
  splice connectives and the itemized inline residues).
- gate-markers-spec.md / relay-phrasing.md (existing references,
  untouched).
