# Plan: close-out privacy gate

Source brief: docs/loom/specs/2026-07-19-closeout-privacy-gate.md
Total tasks: 10
Critical-path depth: 4 (≤5)
Execution order: parallel-where-possible
Plan-document-reviewer verdict: PASS (2026-07-19, round 2, 14/14)

## Notes

**PINNED gate wording (SSOT for T3 + T4 — transcribe VERBATIM, never re-derive).**
Both compose-commit.md and compose-pr.md must carry the same privacy-gate mandate.
Per docs/loom/memory/pin-shared-wording-in-plan-copies-transcribe-from-pin.md, the
canonical text is pinned here; each task transcribes from THIS block, not from each
other. Canonical mandate (prose, adapt only the carrier noun commit-text / PR-body-text):

> **Privacy gate (fail-closed).** After composing the {CARRIER}, run the two-layer
> privacy check before it is used:
> 1. **Layer 1 — deterministic scan.** Run
>    `scripts/privacy-scan.py --text-file <composed>` (exit 0 = clean; exit 3 =
>    secrets/deny-list findings printed as JSON).
> 2. **Layer 2 — fresh-context judge.** Dispatch a fresh-context agent over the same
>    composed text per `protocols/privacy-judge-spec.md` (the judge SSOT: the
>    categories it inspects, its `PASS | BLOCK` output schema, and its fail-closed
>    contract). Do NOT inline the judge's full rubric here — point at the spec.
> 3. **Verdict.** Any layer-1 finding OR a layer-2 BLOCK → the carrier is BLOCKED:
>    surface findings, do not proceed, escalate to the human.
> 4. **Fail-closed (explicit).** A layer-1 script error, a layer-2 dispatch failure,
>    or a non-conforming judge output → treat as BLOCK (never as PASS). This is an
>    explicit branch, not an emergent default.

compose-commit.md ADDITIONALLY requests the quality advisory (T3 only, not T4):

> **Quality advisory (non-blocking).** In the commit carrier, the layer-2 judge also
> returns the optional `quality_note` defined in `protocols/privacy-judge-spec.md`
> (compose-commit anti-patterns: restates the diff / lists files / restates subject /
> body is what-not-why). ADVISORY ONLY — it never blocks and never escalates; carry
> it into the close-out report as a note.

**Judge-spec SSOT (T10).** The layer-2 judge's actual rubric — the categories
(names / companies / internal codenames / contextual leaks), the `PASS | BLOCK`
output schema, the `quality_note` field, and the fail-closed contract — lives in ONE
file, `protocols/privacy-judge-spec.md` (T10). Both compose-* protocols POINT at it;
neither duplicates it (per docs/loom/memory/pin-shared-wording-in-plan-copies-transcribe-from-pin.md,
extended to the shipped artifact: two copies of a judge contract drift).

**Language convention (repo):** all committed artifacts (scripts, SKILL/protocol
prose, CHANGELOG, commit messages) stay in English per repo convention; only the
user-facing chat narration is Traditional Chinese.

**Kickoff decisions (fork harvest — all two-way-door, none escalated; grep key for SDD):**
Kickoff decision: layer-1 secrets pattern set → core gitleaks default-ruleset classes (AWS access key, GitHub `ghp_`/`gho_`, Slack token/webhook, PEM private-key header, generic high-entropy `KEY=`/`TOKEN=`); extend later by editing the regex list (two-way).
Kickoff decision: layer-2 judge model tier → sonnet default (structured detection with a fixed rubric, runs every close-out → cost-conscious), privacy-judge-spec.md notes opus escalation is available if real-name misses recur (matches brief conditional reversal); two-way, late-vetoable.
Kickoff decision: deny-list mount path → gitignored repo-local default, overridable via `--denylist <path>`; exact default filename fixed in T2 (two-way).
Kickoff decision: privacy-scan.py language → Python (pytest-able, matches distill-sessions/recap-state convention) (two-way).

**Amendment (post-PASS, schema-safe — re-review skipped per writing-plans §Amending a PASS plan):**
T6/T7 test carrier corrected from bash `loom-code/tests/test-*.sh` → Python pytest
`loom-code/scripts/test_finishing_*.py`. Reason: execution-time CI recon found loom-code
CI does NOT glob `loom-code/tests/*.sh` (runs only 3 explicitly-named integration .sh);
finishing-SKILL prose pins already use pytest under loom-code/scripts/ (precedent:
test_finishing_merge_path_guidance.py). A bash test there would silently never run in CI.
WHERE-only change: all required fields intact, DAG/deps/Independent flags unchanged.
(dev-workflow bash tests T3/T4/T5/T10 are unaffected — dev-workflow CI DOES glob
`dev-workflow/tests/test-*.sh`.)

## Decision Log

- privacy-scan.py in Python not bash — pytest convention (memory-grep.sh is bash but
  is a git-plumbing wrapper; a regex scanner with unit tests fits the repo's Python
  test dirs). Two-way, no product consequence.
- Layer-2 judge tier = sonnet (see Kickoff decision above). Two-way, product-consequence
  (judge strength ↔ leak recall) → late-vetoable in the final report.
- Optional deny-list layer is fail-OPEN (absent file → continue), while the secrets
  layer is fail-CLOSED (mandatory). Rationale: a zero-config default must not always
  block; the optional layer only adds coverage when configured. Two-way.
- T1 gets a bash CLI test (dev-workflow/tests/test-privacy-scan.sh) IN ADDITION to the
  pytest. Discovered at execution: dev-workflow CI is bash-only (globs
  dev-workflow/tests/test-*.sh) — no pytest job covers dev-workflow/skills/, so
  test_privacy_scan.py alone would never gate in CI (same dark-test class as the
  loom-code tests/*.sh finding). The bash test exercises the real CLI (exit 0/3 +
  redaction) so the scanner's contract has CI regression protection; pytest stays as
  richer dev-time coverage. Two-way door, product consequence (a gate that can't
  regress-fail is worth little) → agent-decided, late-vetoable. (Pre-existing dark
  pytest in distill-sessions is NOT fixed here — surgical scope.)

**Testing split:** Python capability (privacy-scan.py) → pytest `test_privacy_scan.py`.
Prose contract changes (protocols, SKILL.md) → bash grep-pin tests under
dev-workflow/tests/ and loom-code/tests/ (structural pin that the mandate wording
exists), consistent with existing test-git-memory-*.sh. The layer-2 judge behavior
itself is prose (not pytest-able — docs/loom/memory: Claude-prose policies can't
pytest); its behavioral proof is the branch-level cold-reader dogfood in the brief's
Verification plan, run at finishing, NOT a per-task unit test.

**Step 11 PR-body coverage (transitive, verified).** No task edits finishing Step 11
directly. The brief's Step-11 item ("PR body passes the same gate before gh pr create")
is satisfied transitively: finishing Step 11 / Phase 6 composes the PR body via
git-memory's compose-pr.md convention (finishing SKILL.md :238 references
"compose-pr.md Step 4"), so the gate added to compose-pr.md in T4 fires whenever
finishing reaches Step 11. This is intended, not a coverage gap.

## Task 1 — privacy-scan.py: layer-1 secrets scan
- Description: Create `privacy-scan.py` that scans a text blob for hardcoded secrets
  using a core gitleaks-style pattern set (AWS access key, GitHub token `ghp_`/`gho_`,
  Slack token/webhook, private-key PEM header, generic high-entropy `KEY=`/`TOKEN=`
  assignment). Reads `--text-file <path>` (or stdin); prints findings as a JSON list
  (each: pattern-name, matched-span-redacted, line); exit 0 = clean, exit 3 = findings.
  Zero configuration.
- Module: dev-workflow/skills/git-memory/scripts
- Files touched: dev-workflow/skills/git-memory/scripts/privacy-scan.py, dev-workflow/skills/git-memory/scripts/test_privacy_scan.py, dev-workflow/skills/git-memory/scripts/conftest.py, dev-workflow/skills/git-memory/scripts/pytest.ini, dev-workflow/tests/test-privacy-scan.sh
- Context paths:
  - dev-workflow/skills/git-memory/scripts/memory-grep.sh
  - dev-workflow/skills/distill-sessions/scripts/test_propose.py
  - dev-workflow/skills/distill-sessions/scripts/conftest.py
  - dev-workflow/tests/test-git-memory-carrier-doctrine.sh
  - loom-code/skills/subagent-driven-development/checklists/security-checklist.md
- Acceptance:
  - RED: test_privacy_scan.py — a planted AWS key / GitHub token / PEM header each
    yields exit 3 + a JSON finding; a clean paragraph yields exit 0 + empty list.
  - GREEN: pytest test_privacy_scan.py passes; new script runs via
    `python3 dev-workflow/skills/git-memory/scripts/privacy-scan.py --text-file <f>`
    (runnable capability declared — verified to run).
- External surfaces: filesystem read (stdlib `pathlib`/`argparse` only; no non-stdlib deps —
  regex via stdlib `re`). No network.
- Dependencies: none
- Independent: true
- Brief item covered: "New script `scripts/privacy-scan.*`: deterministic secrets regex
  over composed TEXT … Exit 0 = clean, exit 3 = findings"

## Task 2 — privacy-scan.py: optional deny-list mount
- Description: Extend privacy-scan.py with an OPTIONAL deny-list: if a configured local
  file exists (path via `--denylist <path>` or a documented default env/path — decided
  in this task, gitignored repo-local), its literal terms are also matched and reported
  (finding type `denylist`). Absent/unconfigured → no block, emit a one-line
  `denylist: not configured` note to stderr and continue (zero-config default intact).
- Module: dev-workflow/skills/git-memory/scripts
- Files touched: dev-workflow/skills/git-memory/scripts/privacy-scan.py, dev-workflow/skills/git-memory/scripts/test_privacy_scan.py
- Context paths:
  - dev-workflow/skills/git-memory/scripts/privacy-scan.py (from Task 1)
- Acceptance:
  - RED: test — a term in a provided deny-list file yields exit 3 + a `denylist`
    finding; a MISSING deny-list path yields exit 0 (clean text) + the not-configured
    note, never a block.
  - GREEN: pytest passes both cases; zero-config path unchanged (Task 1 tests still green).
- External surfaces: filesystem read of an optional user-supplied file (stdlib only);
  absent-file is a normal non-error branch (fail-open for the OPTIONAL layer only —
  the secrets layer stays mandatory).
- Dependencies: Task 1 completes first
- Independent: false
- Brief item covered: "Optional deny-list mount: if a configured local file exists …
  its literals are also grepped; absent → one-line 'denylist: not configured' note,
  never blocking"

## Task 3 — compose-commit.md: privacy gate + quality advisory
- Description: Add the privacy-gate protocol step to compose-commit.md (transcribe the
  PINNED gate wording from §Notes, CARRIER = commit-text) PLUS the quality-advisory
  block (compose-commit only). The layer-2 bullet POINTS at protocols/privacy-judge-spec.md
  (T10) — do not inline the judge rubric. Places the gate AFTER composition (Step 3
  trailers), BEFORE the message is used.
- Module: dev-workflow/skills/git-memory/protocols
- Files touched: dev-workflow/skills/git-memory/protocols/compose-commit.md, dev-workflow/tests/test-privacy-gate-compose-commit.sh
- Context paths:
  - dev-workflow/skills/git-memory/protocols/compose-commit.md
  - dev-workflow/tests/test-git-memory-raw-footer-mandate.sh
  - docs/loom/specs/2026-07-19-closeout-privacy-gate.md (judge spec SSOT)
- Acceptance:
  - RED: test-privacy-gate-compose-commit.sh greps compose-commit.md and fails until it
    finds the gate mandate (layer-1 script invocation + layer-2 judge pointing at
    privacy-judge-spec.md + fail-closed branch + quality_note advisory).
  - GREEN: the grep-pin test passes; wording matches the §Notes pin.
- External surfaces: none (prose protocol).
- Dependencies: Tasks 1, 10 complete first
- Independent: true
- Brief item covered: "New protocol step in BOTH compose-commit.md and compose-pr.md …
  run privacy gate = script (layer 1) + fresh-context LLM judge (layer 2) …" +
  "Quality advisory (non-blocking), same judge dispatch … `quality_note` field"

## Task 4 — compose-pr.md: privacy gate (PR-body carrier)
- Description: Add the privacy-gate protocol step to compose-pr.md (transcribe the
  PINNED gate wording from §Notes, CARRIER = PR-body-text). The layer-2 bullet POINTS
  at protocols/privacy-judge-spec.md (T10) — do not inline the judge rubric. No
  quality-advisory block (that is commit-only). Gate runs after the PR body is composed,
  before `gh pr create`.
- Module: dev-workflow/skills/git-memory/protocols
- Files touched: dev-workflow/skills/git-memory/protocols/compose-pr.md, dev-workflow/tests/test-privacy-gate-compose-pr.sh
- Context paths:
  - dev-workflow/skills/git-memory/protocols/compose-pr.md
  - dev-workflow/tests/test-git-memory-raw-footer-mandate.sh
- Acceptance:
  - RED: test-privacy-gate-compose-pr.sh greps compose-pr.md and fails until it finds
    the gate mandate (layer-1 + layer-2 pointing at privacy-judge-spec.md + fail-closed).
  - GREEN: the grep-pin test passes; wording matches the §Notes pin.
- External surfaces: none (prose protocol).
- Dependencies: Tasks 1, 10 complete first
- Independent: true
- Brief item covered: "New protocol step in BOTH compose-commit.md and compose-pr.md"
  + "Step 11: PR body passes the same gate (compose-pr path) before `gh pr create`"

## Task 5 — git-memory SKILL.md: operationalize the secrets line
- Description: Rewrite git-memory SKILL.md's declarative "The skill refuses to embed
  secrets in commit trailers" line (~:208-210) to point at the operationalized privacy
  gate (the compose-* protocol step), so the SKILL text and the enforced mechanism agree.
- Module: dev-workflow/skills/git-memory
- Files touched: dev-workflow/skills/git-memory/SKILL.md, dev-workflow/tests/test-git-memory-privacy-gate-ref.sh
- Context paths:
  - dev-workflow/skills/git-memory/SKILL.md
- Acceptance:
  - RED: test-git-memory-privacy-gate-ref.sh greps SKILL.md and fails until the secrets
    line references the privacy gate / compose-protocol step (not a bare declarative claim).
  - GREEN: grep-pin test passes.
- External surfaces: none (prose).
- Dependencies: Task 3 completes first
- Independent: false
- Brief item covered: "git-memory SKILL.md:208-210 declarative 'refuses to embed
  secrets' line — superseded by the operationalized gate; rewritten to point at it"

## Task 6 — finishing Step 3: PASS_WITH_NOTES auto-proceed
- Description: Rewrite finishing-a-development-branch SKILL.md Step 3 so PASS_WITH_NOTES
  (exactly 1 🟡) no longer ASKS — it auto-proceeds and carries the 🟡 finding into the
  PR body + final report. NEEDS_REVISION STOP and PASS-silent branches unchanged.
- Module: loom-code/skills/finishing-a-development-branch
- Files touched: loom-code/skills/finishing-a-development-branch/SKILL.md, loom-code/scripts/test_finishing_step3_autoproceed.py
- Context paths:
  - loom-code/skills/finishing-a-development-branch/SKILL.md
  - loom-code/skills/requesting-code-review/SKILL.md
  - loom-code/scripts/test_finishing_merge_path_guidance.py
- Acceptance:
  - RED: test_finishing_step3_autoproceed.py (pytest, neighborhood-scoped grep over
    Step 3's slice, mirroring test_finishing_merge_path_guidance.py) fails until Step 3's
    PASS_WITH_NOTES branch states auto-proceed + carry-🟡-into-PR-body, and no longer
    says "ASK user to proceed or remediate".
  - GREEN: `python3 -m pytest loom-code/scripts/test_finishing_step3_autoproceed.py`
    passes (asserts auto-proceed present AND the old ask string absent).
- External surfaces: none (prose).
- Dependencies: none
- Independent: true
- Brief item covered: "Step 3: PASS_WITH_NOTES no longer asks — auto-proceed, carry the
  🟡 into the PR body and final report. (NEEDS_REVISION STOP unchanged.)"

## Task 7 — finishing Step 7/9: gate replaces approval ask
- Description: Rewrite finishing SKILL.md Step 7 to REPLACE the "show + ASK approval"
  with "run the privacy gate (via git-memory compose SSOT)": gate PASS → proceed
  silently; gate BLOCK → surface findings + ask the user (exception-based escalation).
  Update Step 9's "only after user approval at Step 7" dependency wording, and rewrite
  the §"ASK = stop and wait" rationale paragraph to the exception-based model (asks
  retained only for outward-facing actions: Step 11 PR-open, Step 12 worktree).
- Module: loom-code/skills/finishing-a-development-branch
- Files touched: loom-code/skills/finishing-a-development-branch/SKILL.md, loom-code/scripts/test_finishing_step7_privacy_gate.py
- Context paths:
  - loom-code/skills/finishing-a-development-branch/SKILL.md
  - dev-workflow/skills/git-memory/protocols/compose-commit.md (the gate it invokes)
  - loom-code/scripts/test_finishing_merge_path_guidance.py
- Acceptance:
  - RED: test_finishing_step7_privacy_gate.py (pytest, neighborhood-scoped grep over the
    Step 7 / Step 9 / ASK-rationale slices) fails until Step 7 invokes the privacy gate +
    defines PASS-silent / BLOCK-ask, Step 9 no longer requires "user approval at Step 7",
    and the rationale paragraph reflects exception-based escalation.
  - GREEN: `python3 -m pytest loom-code/scripts/test_finishing_step7_privacy_gate.py`
    passes (gate-invocation + BLOCK-ask present; old approval-ask string absent).
- External surfaces: none (prose).
- Dependencies: Tasks 3, 6 complete first
- Independent: false
- Brief item covered: "Step 7: 'show + ASK approval' replaced by 'run privacy gate' …
  gate PASS → proceed silently; gate BLOCK → surface findings + ask user … Step 9's
  'only after user approval at Step 7' wording updated" + "§'ASK = stop and wait'
  rationale paragraph rewritten"

## Task 8 — dev-workflow: version bump + CHANGELOG + Codex sync
- Description: Bump dev-workflow plugin version (2.23.0 → next minor), add a CHANGELOG
  entry naming the privacy gate, and re-sync the Codex manifest via
  scripts/sync_codex_manifests.py so .codex-plugin/plugin.json matches.
- Module: dev-workflow/.claude-plugin
- Files touched: dev-workflow/.claude-plugin/plugin.json, dev-workflow/.codex-plugin/plugin.json, dev-workflow/CHANGELOG.md
- Context paths:
  - dev-workflow/.claude-plugin/plugin.json
  - dev-workflow/CHANGELOG.md
  - scripts/sync_codex_manifests.py
  - dev-workflow/.claude-plugin/test_plugin_manifest.py
- Acceptance:
  - RED: python3 dev-workflow/.claude-plugin/test_plugin_manifest.py fails on version
    mismatch (claude vs codex manifest) until re-synced; CHANGELOG lacks the entry.
  - GREEN: manifest test passes (versions synced); CHANGELOG names the version + gate;
    `python3 scripts/sync_codex_manifests.py` reports clean.
- External surfaces: none.
- Dependencies: Tasks 1, 2, 3, 4, 5, 10 complete first
- Independent: true
- Brief item covered: "Version bumps + CHANGELOGs for dev-workflow AND loom-code;
  marketplace/Codex manifest sync per repo convention"

## Task 9 — loom-code: version bump + CHANGELOG + Codex sync
- Description: Bump loom-code plugin version (0.34.0 → next minor), add a CHANGELOG
  entry naming the Step 3 + Step 7 close-out change, and re-sync the Codex manifest via
  scripts/sync_codex_manifests.py.
- Module: loom-code/.claude-plugin
- Files touched: loom-code/.claude-plugin/plugin.json, loom-code/.codex-plugin/plugin.json, loom-code/CHANGELOG.md
- Context paths:
  - loom-code/.claude-plugin/plugin.json
  - loom-code/CHANGELOG.md
  - scripts/sync_codex_manifests.py
- Acceptance:
  - RED: manifest sync check fails on claude-vs-codex version mismatch until re-synced;
    CHANGELOG lacks the entry.
  - GREEN: versions synced; CHANGELOG names the version + close-out change;
    `python3 scripts/sync_codex_manifests.py` reports clean.
- External surfaces: none.
- Dependencies: Tasks 6, 7 complete first
- Independent: true
- Brief item covered: "Version bumps + CHANGELOGs for dev-workflow AND loom-code;
  marketplace/Codex manifest sync per repo convention"

## Task 10 — privacy-judge-spec.md: the layer-2 judge SSOT
- Description: Author `protocols/privacy-judge-spec.md` in git-memory — the single
  source of truth for the layer-2 judge: the fresh-context dispatch instruction, the
  categories it inspects (names / companies / internal codenames / contextual leaks),
  the structured `PASS | BLOCK` + findings output schema, the optional `quality_note`
  field (commit-carrier only, non-blocking), and the fail-closed contract (dispatch
  failure or non-conforming output → BLOCK). Both compose-commit.md (T3) and
  compose-pr.md (T4) POINT at this file; it is authored once here.
- Module: dev-workflow/skills/git-memory/protocols
- Files touched: dev-workflow/skills/git-memory/protocols/privacy-judge-spec.md, dev-workflow/tests/test-privacy-judge-spec.sh
- Context paths:
  - dev-workflow/skills/git-memory/protocols/compose-commit.md
  - docs/loom/specs/2026-07-19-closeout-privacy-gate.md
  - docs/loom/memory/prose-only-enforcement-dies-on-weak-executors.md
  - docs/loom/memory/fail-closed-default-must-be-enforced-not-emergent.md
- Acceptance:
  - RED: test-privacy-judge-spec.sh greps privacy-judge-spec.md and fails until it
    carries all five parts (dispatch instruction, category list, PASS|BLOCK output
    schema, quality_note field, explicit fail-closed→BLOCK contract).
  - GREEN: the grep-pin test passes; the spec names each of the five parts.
- External surfaces: none (prose spec).
- Dependencies: none
- Independent: true
- Brief item covered: "structured verdict PASS | BLOCK + findings). Judge prompt spec
  lives here (SSOT)" + "fresh-context LLM judge (layer 2: names / companies / internal
  codenames / contextual leaks …)" + "Fail-closed … Explicit branch, not emergent"
