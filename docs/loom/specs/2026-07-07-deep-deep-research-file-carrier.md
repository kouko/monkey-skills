# Brief: deep-deep-research file-carrier fix + heavyweight trigger (2026-07-07)

## Problem

deep-deep-research reproducibly dies unattended at the claims-consolidation
boundary: SKILL.md instructs the orchestrator to `echo` the **entire claims
pool inline** (`echo '[<all claims>]' | rank.py`, and again for
`synthesis.py blocks` / `report` with `all_claims`). At real scale (bake-off:
88 claims from 47 sources) that giant single response was cut by
"Server error mid-response" **twice at the same stage** (2/2 unattended
failures); the run survived only via operator `--resume` with a
"write payloads to files incrementally" hint. The job to be done: an
unattended (headless / another-session) heavyweight research run must complete
without an operator rescue. Secondary job: heavyweight asks (徹底研究/多輪)
should have a semantic hook to route here (bake-off verdict: this skill BEAT
built-in deep-research 2/2 blind judges at ~1/4 cost — evidence:
docs/loom/dogfood/2026-07-07-research-bakeoff-vs-builtin.md, added in this
change).

## Users

kouko dispatching research from other Claude Code sessions or headless
(`claude -p`), on this machine and on Codex hosts (key-free pipeline is the
Codex path). Failure mode hits exactly when nobody is watching.

## Smallest End State

1. Bulk data between pipeline stages travels **by file path, never inline**:
   - Stage 3 fetch subagents WRITE their extraction to
     `work/claims/<angle>-<idx>.json`, return `{path, count}` only.
   - `rank.py` accepts `--claims-dir DIR` (merge all `*.json` arrays,
     deterministic filename sort) → orchestrator runs
     `rank.py --claims-dir work/claims > work/ranked.json`.
   - Stage 5 verdicts land in `work/verdicts/claim-<i>.json` (small per-claim
     writes); vote booleans accumulate in `work/votes.json` (tiny).
   - `synthesis.py` `blocks`/`report` accept per-key file flags
     (`--key name=FILE`, `--key-dir name=DIR` for array-merge) instead of the
     monolithic stdin object; stdin stays for backward compat (tests, small
     payloads like `rank.py quorum`).
   - SKILL.md gains one explicit file-carrier rule beside the fan-out
     convention: never emit the full claims pool inline in a command or a
     single response.
2. Description trigger: swap the one CJK trigger from 想調整研究流程 to
   **徹底研究** (higher-frequency heavyweight ask; house standard caps at ONE
   CJK trigger — #426/#428 A/B refuted stuffing); pipeline-tweak intent stays
   as an EN clause. Router `using-research-toolkit` deep-deep-research row
   adds 徹底研究／多輪深挖 (router table rows carry both languages; no
   description-budget cap applies to body text).
3. Bake-off evidence mirrored to the repo: dogfood report file + a loom memory
   store entry (file-carrier practice); machine-side auto-memory already
   written.
4. research-toolkit 0.3.0 → 0.3.1 in `.claude-plugin` + `.codex-plugin`
   (sync script) — a no-bump sweep never reaches version-pinned caches
   (PR #508 lesson).

## Current State Evidence

- **Forward**: SKILL.md:336 `echo '[<all claims>]' | python scripts/rank.py`;
  SKILL.md:397-399 blocks echo; SKILL.md:606-609 report echo with
  `all_claims`; SKILL.md:322-324 "Collect every extracted claim … into one
  pool".
- **Reverse**: `rank.py:84-85` reads `sys.stdin` only (subcommand `quorum` via
  argv); `synthesis.py:191-202` reads `sys.stdin` only (`blocks`/`report`
  argv). Tool-matrix table rows SKILL.md:662,672 document the stdin shapes.
- **Error**: degradation section SKILL.md:619-635 (empty stages → partial
  report) — unaffected by carrier change; abstention semantics rank.py quorum
  unchanged.
- **Data**: claim/extraction/verdict shapes owned by `scripts/schemas.py`
  (`extract`, `verdict`); rank is an L1 leaf (no schemas import) — keep it so.
- **Boundary**: `scripts/` is flat (Anthropic skill convention, hook-enforced);
  tests exist per module (`test_rank.py` 102 lines, `test_synthesis.py` 207
  lines); pytest.ini pins rootdir. Description surface: SKILL.md frontmatter
  (195 chars, one CJK trigger); router row in
  `../using-research-toolkit/SKILL.md`.

Evidence paths: research-toolkit/skills/deep-deep-research/{SKILL.md,
scripts/rank.py, scripts/synthesis.py, scripts/schemas.py},
research-toolkit/skills/using-research-toolkit/SKILL.md.

## Alternatives Considered

- **Compress/truncate claims to shrink the inline payload** — lossy (drops
  quotes/evidence that verification needs); rejected.
- **Cap claims earlier (lower MAX before rank)** — changes research recall,
  not the carrier; the pool before rank is unbounded by design; rejected.
- **Keep stdin, build the payload file via repeated `>>` appends** — is
  file-carrier with worse ergonomics and shell-quoting risk; dir-merge
  dominates it.
- Grounding: not web-researched — the fix pattern was **proven live in this
  session** (the failed run completed only after the resume hint "write large
  payloads to files incrementally"); design space is internal data plumbing,
  not a tech-stack choice.

## Decision

Build: file-carrier hand-off (rank `--claims-dir`, synthesis `--key/--key-dir`,
SKILL.md stage rewrites + file-carrier rule + tool-matrix row updates),
trigger swap + router row, evidence mirror, 0.3.1 bump + codex sync.
NOT build: any new module (payload assembly lives inside synthesis.py's CLI);
no change to quorum semantics, ranking order, schemas, or prompts; no change
to the other 4 research-toolkit skills; built-in deep-research stays enabled
(n=1 evidence — revisit after real usage).

## What Becomes Obsolete

The monolithic-echo instructions at SKILL.md:336/397-399/606-609 are REPLACED
(not kept as alternate path). Scripts keep stdin for tests/small payloads —
documented as such, so no dead code.

## Out of Scope

- Disabling built-in deep-research via skillOverrides (user decision, config
  not repo).
- Learning built-in's stricter survey-refusal behavior (separate improvement).
- deep-read inline-answering residual miss (single-run observation, parked).
- Machine-side cache refresh (post-merge operational step).

## Design-side on-ramp

N/A — bug fix + incremental text changes (Axis 0 negative guard).

## Open Questions

None blocking. Trigger-swap reversal path: if 想調整研究流程-type asks stop
firing after the swap, restore it as the router-row trigger only (router body
has no cap).
