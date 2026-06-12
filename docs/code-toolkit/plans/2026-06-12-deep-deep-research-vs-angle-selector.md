# Plan: deep-deep-research Verbalized-Sampling angle selector (+ skill rename)

**Source brief**: `~/kouko-obsidian-vault/projects/2026-06-12 deep-research 角度選擇器（Verbalized Sampling）實作 brief.md` (external vault brief = brainstorming output; status ready-to-implement)
**Total tasks**: 12
**Critical-path depth**: 4 (≤5 ✓) — longest chain `Task 1 → Task 6 → Task 7 → Task 12`
**Execution order**: parallel-where-possible
**Plan-document-reviewer verdict**: PASS (2026-06-12, round 2)

## Scope notes (read before the tasks)

- **Two requirements bundled.** (a) The brief's VS angle-selector feature; (b) the user's explicit session instruction (2026-06-12): rename the editable skill `deep-research` → `deep-deep-research` to stop it colliding with Claude Code's built-in `deep-research` at activation time. Tasks 1–5 trace to (b); Tasks 6–12 trace to (a). User instructions are a first-class scope source (CLAUDE.md instruction priority), so Tasks 1–5 are **not** orphan tasks.
- **SSOT-isolation refinement (deviation from brief §四 table).** The brief says add `SCOPE_VS_SCHEMA` to `schemas.py` and `scope_vs_prompt()` to `prompts.py`. Those two files are the **byte-identical-synced SSOT primitives** (`research-toolkit/scripts/sync-primitives.sh` copies them into `fact-check`/`cite-check`/`deep-read`, enforced by `.github/workflows/check-script-sync.yml` MD5 groups). Adding VS code there would either drift the siblings or push dead code into them (the sync script forbids: *"a skill must not carry code it never invokes"*). **Refinement: house ALL VS additions in new, non-synced modules** (`scope_vs.py`, `select.py`, `metric_novelty.py`). This honors the brief's faithful-copy hard-constraint *more* strongly — the synced primitives are touched **zero** times. (User has veto on this deviation at plan review.)
- **Faithful-copy contract preserved by construction.** No task edits `schemas.py`, `prompts.py`, `dedup.py`, or `rank.py`. `scope_prompt` / `SCOPE_SCHEMA` remain byte-identical. `select.py` and `metric_novelty.py` *import* `norm_url` from `dedup.py` (read-only reuse) but do not modify it.
- **All paths below use the post-rename directory** `research-toolkit/skills/deep-deep-research/`. Task 1 establishes it first; every other task depends on Task 1 so new files are created at their final tracked location (avoids the git-mv-untracked-file problem).
- **Out of this plan** (brief §七 task 6): the 5–8-question two-arm face-validity + target-metric eval run. It needs real LLM + WebSearch and is the user-confirmed stop point after the build. `metric_novelty.py` (Tasks 10–11) is the *tooling* for that run; running it is not in scope here.
- **External surfaces**: none. Every task is pure-Python stdlib (`json`, `sys`, `difflib`, `itertools`, `urllib.parse`) + internal sibling imports + repo config edits. The `External surfaces` field is omitted on all tasks per `plan-format.md` §External surfaces (pure internal logic).

---

## Task 1 — Rename skill directory + SKILL.md identity

- **Description**: `git mv research-toolkit/skills/deep-research research-toolkit/skills/deep-deep-research`. In the moved `SKILL.md`, change frontmatter `name: deep-research` → `name: deep-deep-research`, the `# deep-research` H1 header → `# deep-deep-research`, and any self-referential "this skill is `deep-research`" prose. Leave provenance prose that cites the *upstream CC built-in* `deep-research` (it is a faithful port of that) unchanged. Do **not** edit the synced primitives or the Stage-1 body (that is Task 12).
- **Module**: `research-toolkit/skills/deep-deep-research/SKILL.md`
- **Files touched**: `research-toolkit/skills/deep-deep-research/SKILL.md` (+ `git mv` of the whole directory)
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/deep-research-r2/research-toolkit/skills/deep-research/SKILL.md`
- **Acceptance**:
  - **RED**: `test -d research-toolkit/skills/deep-deep-research` fails (dir not yet moved); `grep -q '^name: deep-deep-research' .../SKILL.md` fails.
  - **GREEN**: new dir exists, old `skills/deep-research/` gone; `grep '^name: deep-deep-research'` matches; `cd research-toolkit/skills/deep-deep-research/scripts && python -m pytest -q` still 44 green at the new location; sibling skills' pytest (`fact-check`/`cite-check`/`deep-read`) still green (sentinel drift tests are path-agnostic, so they must be unaffected).
- **Dependencies**: none
- **Independent**: false  # root of the dependency DAG
- **Brief item covered**: User session instruction (2026-06-12): "換一個 skill 名稱避免跟內建的重複 就叫做 deep-deep-research"

## Task 2 — Re-point SSOT path in sync-primitives.sh

- **Description**: Update `research-toolkit/scripts/sync-primitives.sh`: `SSOT_DIR="$SKILLS_DIR/deep-research/scripts"` → `"$SKILLS_DIR/deep-deep-research/scripts"`, plus the `deep-research`-naming header comments in that file. No primitive file contents change, so byte-identity of copies is unaffected.
- **Module**: `research-toolkit/scripts/sync-primitives.sh`
- **Files touched**: `research-toolkit/scripts/sync-primitives.sh`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/deep-research-r2/research-toolkit/scripts/sync-primitives.sh`
- **Acceptance**:
  - **RED**: `grep -n 'deep-research/scripts' research-toolkit/scripts/sync-primitives.sh` still returns the stale `SSOT_DIR` line.
  - **GREEN**: that grep returns nothing; `bash research-toolkit/scripts/sync-primitives.sh fact-check cite-check deep-read` exits 0 and the copies remain byte-identical (`for f in schemas rank prompts dedup; do diff` empty against the new SSOT).
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: User rename instruction — keep the SSOT sync working after the directory move.

## Task 3 — Re-point SSOT path in check-script-sync.yml (CI)

- **Description**: Update `.github/workflows/check-script-sync.yml`: the `rt_reference = rt_skills / "deep-research" / "scripts" / primitive` line (~135) → `"deep-deep-research"`, plus the `deep-research`-naming comments (lines ~19/22/127/141). Contents of the synced primitives are unchanged, so the MD5 groups still pass once the reference path is corrected.
- **Module**: `.github/workflows/check-script-sync.yml`
- **Files touched**: `.github/workflows/check-script-sync.yml`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/deep-research-r2/.github/workflows/check-script-sync.yml`
- **Acceptance**:
  - **RED**: `grep -n '"deep-research"' .github/workflows/check-script-sync.yml` still returns the stale `rt_reference` path component.
  - **GREEN**: that grep returns nothing; the file is valid YAML (`python -c 'import yaml,sys; yaml.safe_load(open(sys.argv[1]))' .github/workflows/check-script-sync.yml` exits 0); `rt_reference` now points at `deep-deep-research`.
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: User rename instruction — keep the CI MD5 sync-group check working after the directory move.

## Task 4 — Update plugin.json prose to new skill name

- **Description**: Update `research-toolkit/.claude-plugin/plugin.json` `description` ("…Ships the deep-research skill…") to name `deep-deep-research`. Leave the `deep-research` topic keyword in `keywords` (still an accurate topic tag).
- **Module**: `research-toolkit/.claude-plugin/plugin.json`
- **Files touched**: `research-toolkit/.claude-plugin/plugin.json`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/deep-research-r2/research-toolkit/.claude-plugin/plugin.json`
- **Acceptance**:
  - **RED**: `grep -c 'deep-deep-research' research-toolkit/.claude-plugin/plugin.json` returns 0.
  - **GREEN**: the `description` names `deep-deep-research`; file remains valid JSON (`python -m json.tool research-toolkit/.claude-plugin/plugin.json` exits 0).
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: User rename instruction — keep plugin metadata honest after rename.

## Task 5 — Update marketplace.json prose to new skill name

- **Description**: Update `.claude-plugin/marketplace.json` — the research-toolkit `description` line (~104) "…Ships the deep-research skill…" → name `deep-deep-research`.
- **Module**: `.claude-plugin/marketplace.json`
- **Files touched**: `.claude-plugin/marketplace.json`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/deep-research-r2/.claude-plugin/marketplace.json`
- **Acceptance**:
  - **RED**: `grep -c 'deep-deep-research' .claude-plugin/marketplace.json` returns 0.
  - **GREEN**: the research-toolkit description names `deep-deep-research`; file remains valid JSON (`python -m json.tool .claude-plugin/marketplace.json` exits 0).
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: User rename instruction — keep marketplace metadata honest after rename.

## Task 6 — `scope_vs.py`: SCOPE_VS_SCHEMA + constants + `schema` CLI

- **Description**: Create `scripts/scope_vs.py` holding the VS-scope schema and tuning constants. `SCOPE_VS_SCHEMA`: object `{question, summary, candidates}` where `candidates` is an array `minItems: 10`, each item `{label, query, rationale, relevance(enum high|medium|low), typicality_tier(enum most-obvious|mid|least-obvious)}` (`label`, `query`, `relevance`, `typicality_tier` required). Constants: `HEAD_K=3`, `TAIL_K=2`, `CANDIDATE_COUNT=12`, `SELF_CONSISTENCY_RUNS=2`, `RELEVANCE_FLOOR="medium"` (cut `low`). CLI: `python scope_vs.py schema` prints `SCOPE_VS_SCHEMA` as JSON to stdout. Mirror `schemas.py` style (stdlib only, `from __future__ import annotations`).
- **Module**: `research-toolkit/skills/deep-deep-research/scripts/scope_vs.py`
- **Files touched**: `research-toolkit/skills/deep-deep-research/scripts/scope_vs.py`, `research-toolkit/skills/deep-deep-research/scripts/test_scope_vs.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/deep-research-r2/research-toolkit/skills/deep-research/scripts/schemas.py` (shape + CLI style to mirror)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/deep-research-r2/research-toolkit/skills/deep-research/scripts/test_schemas.py` (test style)
- **Acceptance**:
  - **RED**: `test_scope_vs.py::test_schema_shape` fails (module absent) — asserts `SCOPE_VS_SCHEMA["properties"]["candidates"]["minItems"] == 10`, the `relevance`/`typicality_tier` enums, and that `python scope_vs.py schema` prints parseable JSON equal to `SCOPE_VS_SCHEMA`.
  - **GREEN**: test passes; `python scripts/scope_vs.py schema` prints valid JSON; constants importable.
  - CLI surface (`scope_vs.py schema`) is documented in the skill command surface by Task 12 (SKILL.md).
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: Brief §四 "新增 `SCOPE_VS_SCHEMA` ＋常數"; §七 task 2 (housed in `scope_vs.py` per SSOT-isolation refinement, not `schemas.py`).

## Task 7 — `scope_vs.py`: `scope_vs_prompt()` + `prompt` CLI

- **Description**: Add `scope_vs_prompt(question: str) -> str` to `scope_vs.py`. The prompt instructs the model to: generate `CANDIDATE_COUNT` (~12) candidate angles; **first rank them, then bucket into three tiers** (`most-obvious` / `mid` / `least-obvious`) scored **relatively within this one call** (not absolute floats); rate each `relevance`; and emit JSON conforming to `SCOPE_VS_SCHEMA`. Include the blind/decoupled-scoring instruction (score typicality independent of authorship) per brief §6.3. Add CLI `python scope_vs.py prompt --question Q` printing the assembled prompt.
- **Module**: `research-toolkit/skills/deep-deep-research/scripts/scope_vs.py`
- **Files touched**: `research-toolkit/skills/deep-deep-research/scripts/scope_vs.py`, `research-toolkit/skills/deep-deep-research/scripts/test_scope_vs.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/deep-research-r2/research-toolkit/skills/deep-research/scripts/prompts.py` (`scope_prompt` style)
- **Acceptance**:
  - **RED**: `test_scope_vs.py::test_prompt_instructions` fails — asserts the returned prompt string contains the candidate-count (`12`), all three tier names, a "rank … then" relative-ranking instruction, and a blind/decoupled-scoring cue.
  - **GREEN**: test passes; `python scripts/scope_vs.py prompt --question "x"` prints the prompt with the question interpolated.
- **Dependencies**: Task 6 completes first
- **Independent**: false  # shares scope_vs.py / test_scope_vs.py with its Independent:true producer Task 6
- **Brief item covered**: Brief §四 "新增 `scope_vs_prompt()`"; §七 task 3; §6.3 (序位三檔 + 同呼叫相對評分 + 盲評).

## Task 8 — `select.py`: core selection (relevance floor → tier sort → head/tail → cap)

- **Description**: Create `scripts/select.py` — deterministic, stdlib-only, no network. Reads stdin JSON `{candidates, head_k, tail_k}` (defaults from `scope_vs` constants when absent) and writes stdout `{angles}`. Logic: ① drop candidates below `RELEVANCE_FLOOR` (relevance `low`); ② order survivors by `typicality_tier` (most-obvious → least-obvious); ③ `head` = top `head_k` most-typical, `tail` = bottom `tail_k` least-typical **from the relevance-passing pool only** (never low-relevance); ④ cap total ≤ 6; ⑤ output each angle **stripped to `{label, query, rationale}`** so it feeds the unchanged Stage 2 `SCOPE_SCHEMA` angle shape. (Dedup + tail mutual-exclusion are Task 9.)
- **Module**: `research-toolkit/skills/deep-deep-research/scripts/select.py`
- **Files touched**: `research-toolkit/skills/deep-deep-research/scripts/select.py`, `research-toolkit/skills/deep-deep-research/scripts/test_select.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/deep-research-r2/research-toolkit/skills/deep-research/scripts/dedup.py` (stdin/stdout CLI pattern to mirror)
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/deep-research-r2/research-toolkit/skills/deep-research/scripts/test_dedup.py` (test style)
- **Acceptance**:
  - **RED**: `test_select.py::test_floor_head_tail_cap` fails (module absent) — given a fixture of scored candidates, asserts low-relevance dropped, `head` = the `head_k` most-typical, `tail` = the `tail_k` least-typical relevance-passing ones, total ≤ 6, and output angles carry only `{label, query, rationale}`.
  - **GREEN**: test passes; `echo '{"candidates":[...],"head_k":3,"tail_k":2}' | python scripts/select.py` emits `{"angles":[...]}`; stdlib-only, zero network.
  - CLI surface (`select.py`) documented in SKILL.md by Task 12.
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: Brief §四 "`select.py`（核心決定論邏輯）… ① 過相關地板 ② 依 tier 排序 ③ 取 top HEAD_K…＋bottom TAIL_K… ⑥ cap ≤6"; §七 task 1; §6.2.

## Task 9 — `select.py`: dedup + tail lexical mutual-exclusion

- **Description**: Extend `select.py` selection with ④ `normURL`/label de-duplication (collapse candidates with the same case-folded `label` or the same normalized `query` key — reuse `norm_url` from `dedup.py` for URL-shaped queries) **before** head/tail picking, and ⑤ tail mutual-exclusion: when two tail candidates are lexically near-duplicate (`difflib.SequenceMatcher` ratio over `label`+`query` ≥ a module threshold), keep one and pull the next-least-typical relevance-passing candidate, so the two "surprise" tail slots aren't redundant.
- **Module**: `research-toolkit/skills/deep-deep-research/scripts/select.py`
- **Files touched**: `research-toolkit/skills/deep-deep-research/scripts/select.py`, `research-toolkit/skills/deep-deep-research/scripts/test_select.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/deep-research-r2/research-toolkit/skills/deep-research/scripts/dedup.py` (`norm_url`)
- **Acceptance**:
  - **RED**: `test_select.py::test_dedup_and_tail_exclusion` fails — asserts duplicate-label candidates collapse to one, and that two near-identical least-typical candidates do not both land in `tail` (the second is replaced by the next distinct one).
  - **GREEN**: test passes; full `test_select.py` green; still stdlib-only.
- **Dependencies**: Task 8 completes first
- **Independent**: false  # shares select.py / test_select.py with its Independent:true producer Task 8
- **Brief item covered**: Brief §四 "④ `normURL`/label 去重 ⑤ 詞彙距離守 tail 互斥"; §七 task 1; §6.3 #4 (詞彙距離交叉驗證).

## Task 10 — `metric_novelty.py`: novelty set-diff + contribution rate + direction count

- **Description**: Create `scripts/metric_novelty.py` (eval tooling, stdlib only, no network). Input: two arms' per-question data — each arm has its fetched-source set (norm_url keys, reusing `dedup.norm_url`) and its `confirmed` findings (each finding with `sources: [url]`). Compute, per question: a VS confirmed finding is **novel** iff ≥1 of its sources' `norm_url` ∉ the baseline arm's fetched set; **contribution rate** = novel_VS_confirmed / total_VS_confirmed; and the **direction** for that question = VS wins iff (≥1 novel-confirmed finding) AND (VS confirmed count ≥ baseline confirmed count). Output per-question metrics + the aggregate direction count ("VS wins k/N"). CLI over stdin/stdout JSON. (Permutation test is Task 11.)
- **Module**: `research-toolkit/skills/deep-deep-research/scripts/metric_novelty.py`
- **Files touched**: `research-toolkit/skills/deep-deep-research/scripts/metric_novelty.py`, `research-toolkit/skills/deep-deep-research/scripts/test_metric_novelty.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/deep-research-r2/research-toolkit/skills/deep-research/scripts/dedup.py` (`norm_url` reuse)
- **Acceptance**:
  - **RED**: `test_metric_novelty.py::test_novelty_and_direction` fails (module absent) — given synthetic two-arm data, asserts which VS confirmed findings are flagged novel vs the baseline fetched set, the per-question contribution rate, and the aggregate direction count.
  - **GREEN**: test passes; CLI runs over a sample stdin payload; stdlib-only.
  - CLI surface documented in SKILL.md by Task 12.
- **Dependencies**: Task 1 completes first
- **Independent**: true
- **Brief item covered**: Brief §四 "`metric_novelty.py` … novel-AND-confirmed 貢獻率＋方向數"; §七 task 4; §6.1 (目標指標 + S-recall 風格).

## Task 11 — `metric_novelty.py`: exact paired permutation test

- **Description**: Add an exact paired permutation test to `metric_novelty.py`. Given the per-question paired differences `d_i = metric_VS(q_i) − metric_baseline(q_i)` over N questions, enumerate all `2^N` sign-flips (`itertools.product([1,-1], repeat=N)`), use a sum/mean statistic, and return the one-sided exact p = fraction of sign-flip arrangements with statistic ≥ observed, plus the **minimum achievable p at this N** (`1/2^N`). Pure stdlib `itertools`.
- **Module**: `research-toolkit/skills/deep-deep-research/scripts/metric_novelty.py`
- **Files touched**: `research-toolkit/skills/deep-deep-research/scripts/metric_novelty.py`, `research-toolkit/skills/deep-deep-research/scripts/test_metric_novelty.py`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/deep-research-r2/research-toolkit/skills/deep-research/scripts/rank.py` (stdlib-only pure-function style)
- **Acceptance**:
  - **RED**: `test_metric_novelty.py::test_exact_permutation_p` fails — for an all-positive `d` vector with N=3 asserts one-sided p == 1/8 (0.125), and that the reported minimum-achievable-p == 1/2^N.
  - **GREEN**: test passes; full `test_metric_novelty.py` green; stdlib-only.
- **Dependencies**: Task 10 completes first
- **Independent**: false  # shares metric_novelty.py / test_metric_novelty.py with its Independent:true producer Task 10
- **Brief item covered**: Brief §四 "純 stdlib 精確配對置換檢定"; §七 task 4; §6.1 小樣本統計設計 callout (2^N 翻號, 標此 N 最小可達 p).

## Task 12 — SKILL.md: Stage 1 opt-in "VS scope mode" branch

- **Description**: In the renamed `SKILL.md`, **append** an opt-in subsection under Stage 1 — e.g. `### Opt-in: Verbalized Sampling (VS) scope mode` — documenting: (1) `python scripts/scope_vs.py prompt --question Q` → reason → emit ~12 candidates conforming to `python scripts/scope_vs.py schema`; (2) self-consistency: re-run the scope reasoning `SELF_CONSISTENCY_RUNS` times (text-only, no fetch), keep tier-stable candidates; (3) `echo '{candidates,...}' | python scripts/select.py` → `{angles}` → feed the **unchanged** Stage 2; (4) a face-validity log step (print candidates+tier, eyeball the least-obvious ones per brief Risk #1); plus a one-line pointer that `scripts/metric_novelty.py` is the two-arm eval tool. **Do not alter** the existing default Stage 1 steps (current lines ~60–81) — VS mode is explicitly opt-in and additive.
- **Module**: `research-toolkit/skills/deep-deep-research/SKILL.md`
- **Files touched**: `research-toolkit/skills/deep-deep-research/SKILL.md`
- **Context paths**:
  - `/Users/kouko/GitHub/monkey-skills/.claude/worktrees/deep-research-r2/research-toolkit/skills/deep-research/SKILL.md` (Stage 1 region to extend, not edit)
- **Acceptance**:
  - **RED**: `grep -q 'Verbalized Sampling' SKILL.md` fails and `grep -q 'scope_vs.py' SKILL.md` fails (section not yet added).
  - **GREEN**: SKILL.md contains the VS-mode section naming `scope_vs.py`, `select.py`, `metric_novelty.py`, "opt-in", and self-consistency; the original default Stage-1 step text is unchanged (`git diff` shows only additive lines in the Stage-1 region); the three new script CLIs are now declared in the skill's command surface (this is the command-surface accretion point for Tasks 6/8/10).
- **Dependencies**: Tasks 1, 7, 9, 11 complete first
- **Independent**: false  # convergence task; shares SKILL.md with Task 1 and documents Tasks 6–11
- **Brief item covered**: Brief §四 "`SKILL.md` 追加 Stage 1 的 opt-in 分支"; §七 task 5; §九 (既定經路不動, VS 為明確 opt-in).

## Notes

- **Parallel waves for `dispatching-parallel-agents`**:
  - **Wave A (after Task 1)**: Tasks **2, 3, 4, 5, 6, 8, 10** — all `Independent: true`, pairwise-disjoint `Files touched`, depend only on Task 1. 7-wide.
  - **Wave B (after their Wave-A producers)**: Tasks **7, 9, 11** — marked `Independent: false` because each shares its module file with its `Independent: true` producer (7↔6 `scope_vs.py`, 9↔8 `select.py`, 11↔10 `metric_novelty.py`); the single global `Independent` boolean cannot encode "independent of my Wave-B siblings but not of my producer." **These three touch mutually-disjoint files**, so the orchestrator MAY still dispatch them concurrently once their producers finish — `Dependencies` permits it — but the plan does not *claim* parallelism via the flag (which would violate the global-disjointness contract vs the producers). This is the intended reason for the expected plan-document-reviewer **Check-15 advisory note** on Tasks 7/9/11; it is advisory only, never a NEEDS_REVISION.
  - Task 12 joins last (depends on 1, 7, 9, 11).
- **Faithful-copy guard at review time**: the whole-branch `requesting-code-review` + `verification-before-completion` must confirm `git diff` shows **no changes** to `schemas.py`/`prompts.py`/`dedup.py`/`rank.py` contents, and that `bash research-toolkit/scripts/sync-primitives.sh` keeps the sibling copies byte-identical (CI MD5 groups green).
- **Verification suite**: package-level `cd research-toolkit/skills/deep-deep-research/scripts && python -m pytest -q` (expect 44 baseline + new test_scope_vs/test_select/test_metric_novelty cases all green), plus sibling pytest for `fact-check`/`cite-check`/`deep-read` unaffected.
