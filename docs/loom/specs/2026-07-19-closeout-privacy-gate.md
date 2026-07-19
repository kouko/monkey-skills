# Brief: Close-out privacy gate — replace human confirmation with automated privacy check

Date: 2026-07-19
Status: draft (awaiting user sign-off before writing-plans)

## Design-side on-ramp

Offered — user chose direct (change is a process-skill increment with enumerable
states; loom-spec detour declined by default, consistent with prior skill-change arcs).

## Problem

When kouko closes out a branch, the flow stops for human confirmation at two
points (finishing Step 7 commit-message approval; Step 3 PASS_WITH_NOTES ask),
and the Step-7 human eyeball is currently the ONLY privacy defense for
outward-facing prose (commit message, memory trailers, PR body) — no mechanized
check exists anywhere in the chain (verified: compose-commit.md / compose-pr.md
have no scrub step; git-memory SKILL.md:208-210 is declarative only; review's
CHK-SEC-001 covers the code diff, not prose carriers).

Job story: When I finish a branch, I want close-out to run without stopping for
my approval, so that shipping is fast — while leaked secrets / personal names /
company or internal-project names in commit/PR text are still caught before push.

## Users

- kouko (solo, Traditional Chinese conversation, ships from this machine).
- Any future plugin user (汎用化 requirement — the gate must work with ZERO
  per-repo/per-user configuration; no shipped deny-list of someone's sensitive words).
- Weak-model orchestrators executing finishing headlessly (prose-only duties die
  on weak tiers — enforcement must be deterministic carriers, not prose;
  see docs/loom/memory/prose-only-enforcement-dies-on-weak-executors.md).

## Smallest End State

1. **git-memory (dev-workflow) — the SSOT for the check**:
   - New script `scripts/privacy-scan.*`: deterministic secrets regex over
     composed TEXT (commit subject+body+trailers; PR title+body). Core
     gitleaks-style pattern set (AWS/GitHub/Slack/private-key/high-entropy
     token classes). Exit 0 = clean, exit 3 = findings (machine-readable list).
     TDD-able, zero config.
   - Optional deny-list mount: if a configured local file exists (gitignored
     repo-local or `~/.config/` path — exact path decided at plan time), its
     literals are also grepped; absent → one-line "denylist: not configured"
     note, never blocking. Ships zero-config by default (汎用性).
   - New protocol step in BOTH compose-commit.md and compose-pr.md: after
     composing, run privacy gate = script (layer 1) + fresh-context LLM judge
     (layer 2: names / companies / internal codenames / contextual leaks;
     structured verdict PASS | BLOCK + findings). Judge prompt spec lives here (SSOT).
   - **Quality advisory (non-blocking), same judge dispatch**: the layer-2 judge
     ALSO returns an optional `quality_note` field flagging compose-commit
     anti-patterns (restates the diff / lists files / restates subject / body is
     what-not-why). This is ADVISORY ONLY — it NEVER blocks, never escalates to a
     human; it is carried into the final close-out report as a note. Rationale:
     semantic message quality is taste-heavy (judgment-rubrics §6 — never a hard
     gate); the message is already composed TO the compose-commit standard, so
     this is a cheap second look folded into a dispatch we already pay for, not a
     new gate. Privacy verdict and quality_note are INDEPENDENT: a BLOCK on
     privacy stops; a quality_note never does.
   - **Fail-closed, explicit guard**: script error, judge dispatch failure, or
     judge non-conforming output → treated as BLOCK (falls back to human ask —
     the pre-change behavior). Explicit branch, not emergent
     (docs/loom/memory/fail-closed-default-must-be-enforced-not-emergent.md).
2. **finishing-a-development-branch (loom-code)**:
   - Step 3: PASS_WITH_NOTES no longer asks — auto-proceed, carry the 🟡 into
     the PR body and final report. (NEEDS_REVISION STOP unchanged.)
   - Step 7: "show + ASK approval" replaced by "run privacy gate (via
     git-memory SSOT)": gate PASS → proceed silently; gate BLOCK → surface
     findings + ask user (exception-based escalation — human returns only on
     failure). Step 9's "only after user approval at Step 7" wording updated.
   - Step 11: PR body passes the same gate (compose-pr path) before `gh pr create`.
     The "Open a PR? (y/N)" ask itself is RETAINED (outward-facing action).
   - §"ASK = stop and wait" rationale paragraph rewritten to the
     exception-based model.
3. Version bumps + CHANGELOGs for dev-workflow AND loom-code; marketplace/Codex
   manifest sync per repo convention.

## Current State Evidence

- **Forward**: finishing SKILL.md:142-144 (Step 7 ASK), :96-114 (Step 3 verdict
  routing incl. PASS_WITH_NOTES ask at :102), :132-141 (Step 6 git-memory
  invocation returning trailer set), :196 (Step 9 depends on Step-7 approval),
  :226-247 (push / PR create / PR-carrier check).
- **Reverse (SSOT ownership)**: finishing delegates ALL trailer/message logic to
  dev-workflow:git-memory (P3-D, SKILL.md:83, §Cross-skill contract:89-92 —
  "does NOT duplicate git-memory's logic"). New check follows the same
  direction: logic in git-memory, finishing invokes. git-memory files are
  dev-workflow-owned; NOT part of loom-code's distribute.py sync surface.
- **Error**: current error paths — NEEDS_REVISION STOP (:100), test-failure STOP
  (:121), budget-fallback B2 self-review (:104-110), commit-carrier verify STOP
  (:197-210). No privacy failure path exists — that is the gap. New gate adds
  one, shaped like the existing STOPs.
- **Data**: diff + recent commits → git-memory → trailer set + commit body
  (compose-commit.md Steps 1-3); PR body composed per compose-pr.md with raw
  trailer footer (finishing :229-239). The gate's scan input = these composed
  texts, nothing else.
- **Boundary**: hooks/git-guard.py blocks push/PR without gate markers at HEAD
  (finishing :211-225) — an existing enforcement idiom available if marker-level
  enforcement is added later (out of scope for v1). Codex host mirror exists for
  dev-workflow manifests (sync script). Weak-model executors are a boundary
  audience (see Users).

Evidence paths: loom-code/skills/finishing-a-development-branch/SKILL.md;
dev-workflow/skills/git-memory/SKILL.md;
dev-workflow/skills/git-memory/protocols/compose-commit.md;
dev-workflow/skills/git-memory/protocols/compose-pr.md;
loom-code/skills/subagent-driven-development/checklists/security-checklist.md (CHK-SEC-001);
docs/loom/memory/{prose-only-enforcement-dies-on-weak-executors,fail-closed-default-must-be-enforced-not-emergent,process-mechanism-dogfood-via-coldreader-real-commits,cold-read-and-adversarial-review-catch-different-failures,pipeline-enforced-gates-beat-drafter-instructions}.md

## Alternatives Considered

Researched EN + JA (2026-07-19); EN/JA agree, no divergence finding.

1. **Deterministic-only (regex + deny-list)** — gitleaks-style. Rejected as sole
   mechanism: names/companies have no format; deny-list contradicts 汎用化
   (per-user dictionary maintenance). Sources: [EN] appsecsanta.com
   gitleaks-vs-trufflehog benchmarks; github.com/trufflesecurity/trufflehog;
   [JA] dev.classmethod.jp/articles/gitleaks-commands/;
   tech.makeshop.co.jp/entry/2026/05/15/101006 (pre-commit + allowlist 運用).
2. **LLM-judge-only** — rejected as sole mechanism: hands the deterministic
   secrets class to a nondeterministic checker; industry treats format-matchable
   secrets as regex territory (both languages agree).
3. **External dependency (Presidio NER / vendored gitleaks binary)** — rejected
   for v1: Python+spaCy model weight (Presidio) / binary distribution burden
   (gitleaks) inside a plugin; Presidio's own docs state no detection guarantee,
   recommending hybrid pipelines anyway. Sources: github.com/microsoft/presidio;
   explainx.ai Presidio guide 2026; [JA] zenn.dev/okamyuji multi-layer defense.
4. **Chosen: two-layer hybrid, zero-dependency** — layer 1 regex script (secrets,
   deterministic, TDD-pinned) + layer 2 fresh-context LLM judge (names/PII,
   generalizes without dictionaries), exception-based human escalation,
   fail-closed. Matches the industry hybrid consensus while staying
   dependency-free inside the plugin.

My take — Recommend: alternative 4. Why: only combination that is
deterministic where formats exist, dictionary-free where they don't, and
enforceable on weak tiers (script + structured verdict, not prose). Conditional
reversal: if live use shows the judge misses real names repeatedly, add the
gate-marker (git-guard.py) enforcement layer and/or promote the optional
deny-list to a documented first-class config.

## Decision

Build the two-layer privacy gate as git-memory compose-SSOT (script + judge
spec + protocol steps in both carriers), rewire finishing Step 3 (auto-proceed
on PASS_WITH_NOTES) and Step 7 (gate replaces approval ask; BLOCK → human), keep
Step 11/12 asks, fail-closed throughout. We will NOT build: diff scanning (owned
by review CHK-SEC-001), auto-rewrite/anonymization of flagged text (gate blocks,
never rewrites — machine rewrites risk semantic damage), gate-marker/hook
enforcement (deferred, conditional reversal above), Presidio/gitleaks
dependencies, any shipped deny-list content.

## Out of Scope

- Step 11 "Open a PR?" and Step 12 worktree-removal asks (outward-facing;
  user only requested removing Step 7 + Step 3 confirmations).
- Diff-content secret scanning (CHK-SEC-001 owns it at review).
- Automatic redaction/rewriting of flagged text.
- git-guard.py marker-level enforcement of the privacy gate (v2 candidate).
- Backfilling scans over historical commits/PRs.
- Codex-host behavioral parity beyond manifest sync (loom-code Codex shim
  handles skill routing; judge dispatch on Codex verified separately if needed).

## What Becomes Obsolete

- finishing Step 7 ASK + Step 9 approval dependency wording + §"ASK = stop and
  wait" rationale paragraph — rewritten in same PR.
- Step 3 PASS_WITH_NOTES ask branch — rewritten in same PR.
- git-memory SKILL.md:208-210 declarative "refuses to embed secrets" line —
  superseded by the operationalized gate; rewritten to point at it (same PR).
- No test files or reference files pin "Step 7"/"Step 3" literals (grepped
  references/ + test-prompts.json + tests/ — no hits), so no external sweep.

## Open Questions (plan-time, non-blocking)

- Judge model tier: sonnet default per model-dispatch §2 vs opus (verdict
  role). Recommend sonnet with ladder escalation.
- Exact secrets pattern set for layer 1 (core ~10-15 classes vs broader).
- Deny-list mount path convention (repo-local gitignored vs ~/.config).
- Whether finishing shows the composed message read-only (no ask) on PASS,
  for transparency in the final report.
- Mechanical commit-format pre-push check (conventional-commits type/scope, 72-col
  wrap, trailer validity): largely overlaps with this repo's CI (type whitelist +
  mandatory scope) + finishing Step 9b `memory-grep --verify`. Add a pre-push
  deterministic check (catch format issues before push, not after CI) or rely on
  existing CI? Lean: rely on CI for v1 (avoid duplicate-surface drift); revisit if
  post-push CI-red round-trips become a friction.

## Verification plan (acceptance shape)

- Layer-1 script: pytest RED→GREEN per pattern class + clean-text negative.
- Process-rule behavior: cold-reader dogfood per
  docs/loom/memory/process-mechanism-dogfood-via-coldreader-real-commits.md —
  real sandbox commits: (a) clean close-out → no ask, (b) planted secret →
  BLOCK, (c) planted company/person name in trailer → judge BLOCK,
  (d) judge dispatch failure → fail-closed ask.
- Gate-mechanism change ⇒ BOTH cold-read AND adversarial review
  (docs/loom/memory/cold-read-and-adversarial-review-catch-different-failures.md).
