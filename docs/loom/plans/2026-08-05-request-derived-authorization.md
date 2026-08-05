# Plan: request-derived authorization (B-full, reshaped) + ask-triage SSOT

Source brief: docs/loom/specs/2026-08-05-request-derived-authorization.md
Total tasks: 6
Critical-path depth: 3 (≤5)
Execution order: parallel-where-possible (Wave 1 = T1+T2+T3+T4, disjoint files; T5 after Wave 1; T6 after T5)
Plan-document-reviewer verdict: PASS (2026-08-05, round 3 — rounds 1-2
NEEDS_REVISION fixed and fix-verified; round-2's finding was new, not
persistence, so round 3 ran as delta verification within the
fix-and-rerun budget)
Endpoint named: yes → continuous (user: 「凍結 brief 開跑」; the arc
runs to PR-open; merge stays with the user)

## Task 1 — router + doctrine: endpoint recognition

- Description: Add the recognition block (pinned verbatim in ## Notes
  N1) to `using-loom-code/SKILL.md` §Continuous mode (after the entry
  precondition sentence) and the doctrine paragraph (N2) to
  `references/continuous-mode.md` §Entry; sweep the router-rule-5
  parenthetical (using-loom-code/SKILL.md:21 "always confirm
  outward/irreversible actions") to carry the once-clause pointer
  "(asked once — see §Continuous mode's request-recognition block)"
  so it stops contradicting the new block; create `loom-code/scripts/test_request_derived_authorization.py`
  pinning: recognition-sentence lead, the non-trigger sentence, the
  escape hatch 「一站一站來」, the plan-header recording format
  "endpoint named:", and the doctrine paragraph's closing
  "never auto-merge" restatement — whitespace-normalized contiguous
  matches, plus a positive-fact control per file.
- Module: loom-code/skills/using-loom-code
- Files touched: loom-code/skills/using-loom-code/SKILL.md, loom-code/skills/using-loom-code/references/continuous-mode.md, loom-code/scripts/test_request_derived_authorization.py
- Context paths:
  - loom-code/scripts/test_continuous_mode_router.py (existing phrase pins — must stay green)
- Acceptance:
  - RED: the new test file fails against unedited files (controls pass).
  - GREEN: new test + test_continuous_mode_router.py both pass.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State 1-2 (Partition A)

## Task 2 — finishing: delete the Step 11 ask + entry-confirm note + neighbor sweep + SSOT pointer

- Description: Rewrite Step 11 per pinned text N3 (ask deleted,
  auto-open + loud report; the trailing `- If no: stop after push`
  line absorbed and deleted); add the §When to use entry-confirm note
  N4 to the "I'm done here, what's next?" row; insert the SSOT pointer
  sentence N9a into the §ASK rationale paragraph while sweeping it;
  sweep ALL neighbors restating the old ask:
  (a) §ASK rationale paragraph (~:330) — Steps 11-12 wording → Step 12
  only + Step 11 reports loudly;
  (b) delegation-table row 6 (:89 "user must opt in") →
  request-derived wording;
  (c) Phase-6 diagram line (:50) — already opt-out-shaped, verify and
  align terminology only if it names an ask;
  (d) §What this skill does NOT do (:338 "or auto-create PRs /
  auto-remove worktrees — each needs explicit user authorization") →
  worktree-removal keeps the ask, PR-open authorization arrives with
  the request;
  (e) the :95 bullet "Force the merge or auto-create PRs without user
  opt-in" → merge stays; PR-open rewritten to request-derived.
  Pin rewrites in test_finishing_step7_privacy_gate.py: slice marker
  :79 and `test_guard_step11_pr_open_ask_intact` (:170-176) →
  rewritten to assert the y/N ask is ABSENT from Step 11 and the N3
  lead is present; `test_step11_invokes_pr_body_privacy_gate` (:178)
  stays as-is. test_finishing_merge_path_guidance.py:61 slice marker →
  new Step 11 lead. New assertions: N4 entry note present; N9a pointer
  present; :338 old absolute absent.
- Module: loom-code/skills/finishing-a-development-branch
- Files touched: loom-code/skills/finishing-a-development-branch/SKILL.md, loom-code/scripts/test_finishing_step7_privacy_gate.py, loom-code/scripts/test_finishing_merge_path_guidance.py
- Context paths:
  - loom-code/scripts/test_finishing_attached_head_check.py (sibling conventions)
- Acceptance:
  - RED: rewritten step-11 assertions fail against unedited SKILL.md.
  - GREEN: all finishing test files pass; SKILL.md word count ≤4500.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State 3 + item 6's finishing pointer half

## Task 3 — rcr: push-trigger steps 4/6 + neighbor sweep + SSOT pointer

- Description: Rewrite Push-as-trigger steps 4 and 6 per pinned text
  N5 and append the SSOT pointer sentence N9b after step 6; sweep the
  neighbors restating the old ask:
  (a) the sync-marker'd 1-row §When to use summary (keep in sync per
  the marker comment);
  (b) rcr SKILL.md:18 "push/PR/merge actions always confirm first" →
  "merge always confirms; push/PR confirm once — at the request that
  names them";
  (c) references/relay-phrasing.md:13 — replace its closing clause
  per pinned text N9c.
  Create `loom-code/scripts/test_rcr_push_trigger_authorization.py`
  pinning: step-4 "the push WAS the request" lead + absence of
  "want me to push now", step-6 carry-findings wording + absence of
  the "push anyway" ask, N9b pointer present, N9c's lead phrase
  present in relay-phrasing.md — plus a positive-fact control. Net SKILL.md word
  delta budgeted ≤ +30 (headroom 112, ceiling 3900 pinned in
  test_rcr_extraction_pointers.py:151).
- Module: loom-code/skills/requesting-code-review
- Files touched: loom-code/skills/requesting-code-review/SKILL.md, loom-code/skills/requesting-code-review/references/relay-phrasing.md, loom-code/scripts/test_rcr_push_trigger_authorization.py
- Context paths:
  - loom-code/scripts/test_rcr_extraction_pointers.py (ceiling pin — must stay green)
- Acceptance:
  - RED: new test file fails against unedited files (controls pass).
  - GREEN: new test + test_rcr_extraction_pointers.py pass; wc ≤3900.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State 4 + item 6's rcr pointer half

## Task 4 — SDD: gate ① once-clause + triage SSOT marker

- Description: Edit gate ①'s "always confirm" row per pinned text N6
  (asked-ONCE clause; merge/deploy/delete/paid always confirm); append
  the SSOT marker N7 to the three-way triage bullet; create
  `loom-code/scripts/test_sdd_gate_once_clause.py` pinning both (plus
  a positive-fact control). Net delta budgeted ≈ +64 words by
  `len(split())` (3824 + 64 = 3888 ≤ 3900 ceiling pinned in
  test_sdd_extraction_pointers.py:81) — the pinned texts are VERBATIM;
  never trim them to a budget.
- Module: loom-code/skills/subagent-driven-development
- Files touched: loom-code/skills/subagent-driven-development/SKILL.md, loom-code/scripts/test_sdd_gate_once_clause.py
- Context paths:
  - loom-code/scripts/test_sdd_extraction_pointers.py (ceiling pin — must stay green)
- Acceptance:
  - RED: new test file fails against unedited SKILL.md (control passes).
  - GREEN: new test + test_sdd_extraction_pointers.py pass; wc ≤3900.
- Dependencies: none
- Independent: true
- Brief item covered: Smallest End State 5-6 (gate ① clause + SSOT marker; the pointer halves of item 6 are produced by T2 (N9a) and T3 (N9b))

## Task 5 — bump 0.58.0

- Description: Both manifests → 0.58.0; CHANGELOG entry per pinned
  text N8; test_docs_review_blocking_class.py version pin rewritten
  0.57.0 → 0.58.0 (name, docstring, both assertions and messages).
- Module: loom-code (manifests + changelog)
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md, loom-code/scripts/test_docs_review_blocking_class.py
- Context paths:
  - loom-code/CHANGELOG.md ([0.57.0] head)
- Acceptance:
  - RED: rewritten version-pin test fails pre-bump.
  - GREEN: full `pytest loom-code/scripts/` passes.
- Dependencies: Tasks 1, 2, 3, 4 complete first
- Independent: false
- Review-weight: mechanical
- Brief item covered: Smallest End State 7

## Task 6 — five-leg haiku probes + dogfood report

- Description: Dispatch five haiku cold-read probes per brief item 8
  (a-e legs, by-path prompts against the edited working tree); write
  docs/loom/dogfood/2026-08-05-request-derived-authorization-probe.md
  summarizing each leg with verbatim key quotes and CLEAN/FAIL.
- Module: docs/loom/dogfood
- Files touched: docs/loom/dogfood/2026-08-05-request-derived-authorization-probe.md
- Context paths:
  - docs/loom/dogfood/2026-08-05-extraction-batch-cold-read-probe.md (report shape)
- Acceptance:
  - RED: a probe leg answering with the OLD behavior (asks where it
    should proceed, proceeds where it should ask, or auto-merges) is
    the failure signal — any FAIL blocks close-out until the wording
    is fixed and the leg re-probed.
  - GREEN: the report exists at the named path with all five legs
    marked CLEAN, each carrying a verbatim supporting quote.
- Dependencies: Task 5 completes first
- Independent: false
- Review-weight: prose
- Brief item covered: Smallest End State 8

## Notes

Kickoff decisions: no one-way doors — all edits additive/deletive prose
with escape hatches; below-threshold decisions log here.
Counting convention: `len(text.split())`.

**Pinned canonical texts — transcribe VERBATIM**:

N1 — router recognition block (after the entry-precondition sentence in
§Continuous mode):

```markdown
**Opt-in is also recognized from the request itself**: a kickoff
request that names a publish endpoint — "finish this branch", "ship
it", "開 PR", "run to PR" — is an explicit continuous opt-in (the
anchor phrases are examples; the operative test is whether the request
names a publish endpoint). Record the recognition in one line in the
plan header ("endpoint named: yes → continuous"); downstream stations
read the recording, never re-judge the request. A request naming no
endpoint never triggers this; saying 「一站一站來」 (stage-by-stage)
restores human-pumped mode from that point, and the recording flips.
```

N2 — continuous-mode.md §Entry addition (doctrine register; ends
restating the invariant):

```markdown
Entry opt-in is also satisfied by the request itself: a kickoff
request naming a publish endpoint ("finish this branch", "ship it",
"開 PR", "run to PR") is an explicit opt-in — judged once at kickoff
against the operative test "does the request name a publish
endpoint?", recorded in the plan header ("endpoint named: yes →
continuous"), and flipped by a mid-arc 「一站一站來」. A request
naming no endpoint keeps the human-pumped default. The STOP contract
below is unchanged by this recognition, and the merge invariant is
untouched: **never auto-merge**.
```

N3 — finishing Step 11 lead (replaces `11. ASK user: "Open a PR?
(y/N)" — only if gh CLI configured`):

```markdown
11. Open the PR — no ask: the authorization arrived with the request
    (every §When to use trigger names the close-out endpoint; the one
    ambiguous row confirmed at entry). Skip only if gh CLI is
    unconfigured or the user opted out up front — then stop after
    push and say so.
```

(sub-bullets — privacy gate, PR-carrier check, both merge paths —
unchanged; the trailing `- If no: stop after push` line is absorbed by
the lead's opt-out sentence and deleted.)

N4 — §When to use entry note (rides the "I'm done here, what's next?"
row):

```markdown
✅ Yes — the one endpoint-unnamed trigger: confirm the close-out
intent at entry ("closing out = review → verify → commit → push →
PR — proceeding?"), then never re-ask downstream.
```

N5 — rcr Push-as-trigger steps 4/6 (replace the three-line block;
step 5 transcribed unchanged to keep it contiguous):

```markdown
4. **After PASS**: the push WAS the request — execute it (branch-
   qualified form) and report loudly what was pushed. Do not re-ask.
5. **After NEEDS_REVISION**: surface findings; do NOT push; let user remediate.
6. **After PASS_WITH_NOTES**: push, carrying every finding verbatim
   into the report (and the PR body if one follows) — consistent with
   `finishing-a-development-branch` Step 3's auto-proceed. Do NOT fix
   findings inline silently.
```

N6 — SDD gate ① "always confirm" row clause (appended to the row,
before the parenthetical):

```markdown
The confirm is asked ONCE: a kickoff request that already names the
endpoint ("finish the branch", "ship it", "開 PR") IS that ask —
stations then report loudly instead of re-asking. `gh pr merge`,
deploy, delete, and paid runs always confirm regardless.
```

N7 — triage SSOT marker (appended to the three-way triage bullet):

```markdown
This three-way triage is the cross-skill SSOT for ask-vs-resolve
decisions — sibling skills point here by heading text, never copy it.
```

N9a — finishing SSOT pointer (inserted into the §ASK rationale
paragraph during T2's sweep):

```markdown
For any remaining question, run the ask-vs-resolve triage at
`subagent-driven-development` §Asking the user, gate ① (the
cross-skill SSOT) before asking.
```

N9b — rcr SSOT pointer (appended after Push-as-trigger step 6):

```markdown
Any further question this flow surfaces runs the ask-vs-resolve
triage at `subagent-driven-development` §Asking the user, gate ①
(the cross-skill SSOT) before it reaches the user.
```

N9c — relay-phrasing.md:13 replacement (the bullet's closing clause,
from "The push-as-trigger actions" to the end of the line, becomes):

```markdown
The push-as-trigger actions publish to teammates / CI / production —
`gh pr merge` always confirms first and is never auto-run; `git push`
/ `gh pr create` confirm ONCE, at the request that names them
(request-derived authorization) — a naming request executes with a
loud report, an unnamed one still asks.
```

N8 — CHANGELOG entry:

```markdown
## [0.58.0] — 2026-08-05 — authorization arrives with the request

### Changed

- **A request that names a publish endpoint is a continuous-mode
  opt-in.** The router and doctrine recognize "finish this branch" /
  "ship it" / "開 PR" as the explicit opt-in continuous mode always
  required — judged once at kickoff, recorded in the plan header,
  reversible mid-arc with 「一站一站來」. Measured basis: 6-project
  pump-phrase mining, PR/review-context stops ≈10:1 over
  limit-recovery stops.
- **Stations stop re-asking for what the request already authorized.**
  finishing Step 11's `Open a PR? (y/N)` is deleted (every trigger
  names the endpoint; the ambiguous "done" row confirms at entry);
  requesting-code-review's push-trigger PASS re-ask and
  PASS_WITH_NOTES push-anyway ask are replaced by loud reports
  carrying findings; SDD gate ① states the confirm is asked once.
  Merge, deploy, delete, and paid runs still always confirm; hard
  gates (NEEDS_REVISION, privacy BLOCK, one-way doors, UI acceptance)
  unchanged.
- **Gate ①'s three-way triage is marked the cross-skill SSOT** for
  ask-vs-resolve decisions; sibling ask-moments point at it by stable
  heading text instead of restating fragments.
```

## Decision Log

- 2026-08-05: SSOT pointers anchor stable heading text, never section
  numbers (cross-file-§refs Shotgun-Surgery memory).
- 2026-08-05: T6 probe legs run by-path against the edited working
  tree (contracts unreachable in-session otherwise).
- 2026-08-05 (round-1 fixes): shared test file split per skill
  (T1/T3/T4 now disjoint — depth 5 → 3); T6 gains a GREEN; T2 cites
  the real pin test `test_guard_step11_pr_open_ask_intact`; item 6's
  pointer halves became executable pinned texts N9a/N9b in T2/T3;
  neighbor sweep extended (finishing :338+:95, rcr :18,
  relay-phrasing.md:13, router rule-5 parenthetical rides T1); T4
  budget corrected to ≈ +64 (verbatim pins never trimmed to budget).
- 2026-08-05 (round-2 fix): T1's pointer literal re-anchored to the
  shipped artifact ("§Continuous mode's request-recognition block" —
  plan-internal label N1 removed from shipping text);
  relay-phrasing.md:13 replacement pinned as N9c (deterministic
  RED/GREEN). Round-2's five fix-verifications all confirmed; round 3
  is a delta verification of these two edits only.
