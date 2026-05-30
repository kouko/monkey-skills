# distill-sessions v0.5 — brainstorming brief

> **Status**: 5-axis exploration complete. **Surfaces 3 candidate architectures (A / B / C); recommends A.** Reverses v0.1 stdlib-only constraint as anticipated by v0.5 placeholder language in current code. Bundles output-format changes (code-block wrapping + language enforcement) per user 2026-05-27 ask.
>
> **Author**: kouko + Claude session, 2026-05-27.
>
> **Consumes**:
> - v0.4.1 first-dogfood evidence (5 sec / 0 $ run with /tmp/v0.4-dispatch/merged.json):
>   - Anti-pattern section: 1 cluster swallowed 31/33 items via "axis" keyword transitive union-find
>   - CLAUDE.md candidates section: 21 entries, ~19 are surface-word noise (`all`, `from`, `open`, `start`, `clarify`, `code`, `branch`...)
>   - User feedback: "離可用還有距離" — heuristic quality is ~30-40% of hand-curated
> - [`distill-sessions-v0-4-first-dogfood`](../../../.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_distill_sessions_v0_4_first_dogfood.md) memory — first cluster N≥2 fire = 0 evidence
> - [`distill-sessions-v0-4-1-shipped`](../../../.claude/projects/-Users-kouko-GitHub-monkey-skills/memory/project_distill_sessions_v0_4_1_shipped.md) memory — v0.4.1 heuristic limits known at ship-time
> - User 2026-05-27 dialogue: "我可以改輸出格式嗎？我想明確用 code block 來寫建議修改或是可以複製貼上的地方，其他說明部分則強制使用 user 使用的語言"

---

## Problem

**JTBD (Klement format)**: *When I run distill-sessions and get the advisory report, I want it to actually surface **distinct** anti-patterns (not 1 cluster containing 31 unrelated items merged by surface-word coincidence) AND list CLAUDE.md candidates that are **real cross-skill rules** (not 21 generic-keyword noise entries) — and I want the suggested edits in code blocks so I can copy-paste them straight into the target SKILL.md / CLAUDE.md without reformatting, with explanatory prose in my working language so I'm not parsing English mid-skim.*

v0.4.1 productized the report shape but kept v0.1 Q1 stdlib-only lock → heuristic clustering. Two real-data dogfood cycles (v0.4 first-dogfood and v0.4.1 first-dogfood) both confirmed:
- N≥2 exact-match cluster fires 0 times on diverse Memory Items
- Loose token-overlap cluster transitive-merges via shared common words (1 dominant cluster swallowing >90% of items)
- CLAUDE.md keyword-shared-across-targets heuristic produces noise ~10× higher than real candidates

The friction is **algorithmic, not template**. Template (v0.4.1) is good enough; clustering needs semantic understanding.

## Users

Primary: **kouko after a distill-sessions dogfood run**, wanting <60-second triage with actionable copy-pasteable output in zh-TW (working language).

New v0.5-specific user constraint surfaced today: user wants 「明確用 code block 來寫建議修改或是可以複製貼上的地方，其他說明部分則強制使用 user 使用的語言」 — output ergonomics matter as much as analysis quality. Plain "your skill needs to say X" prose loses to "copy this code block".

Secondary (other monkey-skills users at v1.0+) inherit unchanged. Tertiary user (cross-runtime at v1.0+) still parked at [[distill-sessions-v0-6-cross-runtime-parking]].

## Smallest End State

**One paragraph**: After v0.5 ships, running `python scripts/report.py --input merged.json` invokes a single **Sonnet-tier "advisory analyst" subagent** that consumes the same merged.json + renders the advisory report directly. The subagent does the clustering, narrative generation, code-block wrapping, AND language rendering in one LLM call. Output: same 7-section advisory at `docs/skill-mining/<date>-advisory-report.md`, but with (a) semantically-clustered anti-patterns (3-5 distinct, not 1 noise-merged), (b) ≤5 real CLAUDE.md candidates (semantic dedup of surface-word noise), (c) code blocks around copy-pasteable text, (d) prose in user's working language (`--lang zh-TW|en|ja`, default zh-TW). v0.4.1 heuristic `cluster_by_title_keyword` + `extract_claude_md_candidates` + heuristic Python rendering all become obsolete; replaced by `agents/prompt-advisory-analyst.md` (the dispatched prompt) + thin `report.py` (just dispatches subagent + writes output to file).

### What v0.5 does NOT touch

- **Stage 1+2 (main.py)** — unchanged
- **Stage 3 per-trajectory Trace2Skill subagents** — unchanged (still 11 subagents producing Memory Items)
- **Stage 4 (cluster.py)** — unchanged (still title+anchor exact-match for §pending bucket promotion; this is `apply.py`'s gate, separate from advisory report)
- **propose.py** — unchanged (still the proposals-for-apply.py path)
- **apply.py** — unchanged
- **Cross-runtime portability** — still [[distill-sessions-v0-6-cross-runtime-parking]]
- **New-skill candidate LLM detection** — included AS A SECTION the analyst produces (since it's free with the analyst pass), but the SECTION renders "目前無" if analyst finds nothing — same UX as v0.4.1, just driven by LLM judgment now
- **Manual application of v0.4 / v0.4.1 KEEP items** — separate operator task; v0.5 ship doesn't trigger
- **Embedding-based clustering as a building block** — eliminated in Axis 4 (Sonnet analyst is simpler at this scale)
- **EN-language advisory output** — `--lang en` accepted but default still zh-TW (single-user repo)

## Current State Evidence

Verified 2026-05-27 against `main` (commit `28b4954d`, post-v0.4.1 merge).

| Dimension | Path / file:line | What's there |
|---|---|---|
| **Forward** (target to replace) | [`scripts/report.py:122-188`](../../../dev-workflow/skills/distill-sessions/scripts/report.py#L122-L188) `cluster_by_title_keyword` (~66 LOC; loose heuristic) | Gets replaced by subagent dispatch; function deleted |
| **Forward** (target to replace) | [`scripts/report.py:191-247`](../../../dev-workflow/skills/distill-sessions/scripts/report.py#L191-L247) `extract_claude_md_candidates` (~57 LOC; cross-target keyword heuristic) | Gets replaced by subagent dispatch; function deleted |
| **Forward** (target to replace) | [`scripts/report.py:271-460`](../../../dev-workflow/skills/distill-sessions/scripts/report.py#L271-L460) all 7 `_render_*` helpers + `render_advisory_markdown` (~190 LOC; pure-Python template) | Most deleted; thin shell remains that dispatches subagent + writes output |
| **Forward** (target to keep) | [`scripts/report.py:464-490`](../../../dev-workflow/skills/distill-sessions/scripts/report.py#L464-L490) `main()` argparse | Kept; add `--lang` flag |
| **Forward** (new file) | `dev-workflow/skills/distill-sessions/agents/prompt-advisory-analyst.md` (NEW) | Sonnet subagent prompt; defines analyst role + input/output contracts + code-block formatting rules + language enforcement |
| **Reverse** (sibling Trace2Skill prompts as pattern) | [`agents/prompt-failure-analysis.md`](../../../dev-workflow/skills/distill-sessions/agents/prompt-failure-analysis.md) + [`agents/prompt-success-analysis.md`](../../../dev-workflow/skills/distill-sessions/agents/prompt-success-analysis.md) | Existing per-trajectory subagent prompts; v0.5 analyst prompt mirrors their YAML-frontmatter + role+input+output structure |
| **Reverse** (test infrastructure) | [`scripts/test_report.py`](../../../dev-workflow/skills/distill-sessions/scripts/test_report.py) (8 tests, all on heuristic logic) | All 8 tests get rewritten; new tests check subagent dispatch contract + output structure, not heuristic correctness |
| **Reverse** (fixture) | [`scripts/fixture_report_merged.json`](../../../dev-workflow/skills/distill-sessions/scripts/fixture_report_merged.json) | Preserved; same input contract for subagent |
| **Error** (skill version + plugin version) | [`SKILL.md:25`](../../../dev-workflow/skills/distill-sessions/SKILL.md#L25) `version: 0.4.1`; [`plugin.json:3`](../../../dev-workflow/.claude-plugin/plugin.json#L3) `"version": "2.8.1"` | Both bump: skill 0.4.1 → 0.5.0; plugin 2.8.1 → 2.9.0 (minor — new architecture) |
| **Error** (v0.1 stdlib-only constraint reference) | [v0.1 brief Q-decisions](2026-05-22-skill-log-mining-v0.1-brief.md) inline stdlib-only references (e.g. "stdlib-lean per plan-time Decision 1") + [v0.4.1 brief §Decision](2026-05-27-distill-sessions-v0.4.1-brief.md) explicit "preserves v0.1 Q1 stdlib-only lock" | v0.5 brief MUST explicitly reverse this for the `report.py` dispatch path (Stage 5c). Other scripts (main.py / propose.py / apply.py / cluster.py / aggregate.py / friction_signals.py / ingest.py / event.py / facets.py) remain stdlib-only |
| **Data** (input contract preserved) | `merged.json` shape from Stage 4: `list[{session_id, trajectory_id, kind, target_skill_path, memory_items}]` | v0.5 subagent reads same shape; no upstream changes needed |
| **Boundary** (output location) | `docs/skill-mining/<date>-advisory-report.md` per v0.4.1 convention | Unchanged |
| **Boundary** (subagent dispatch shape) | v0.4 + v0.4.1 use Claude Code `Agent` tool with `subagent_type: general-purpose` and `model: claude-sonnet-4-6` | v0.5 dispatches same way; orchestrator (Claude Code session) issues `Agent` call; report.py outputs payload-for-dispatch the way `main.py` does for Stage 3 |

**Evidence paths appendix**:
- `dev-workflow/skills/distill-sessions/scripts/report.py` (current 520 LOC; v0.5 strips to ~100 LOC dispatcher + writer)
- `dev-workflow/skills/distill-sessions/scripts/test_report.py` (8 tests; v0.5 rewrites mostly)
- `dev-workflow/skills/distill-sessions/scripts/fixture_report_merged.json` (preserved fixture)
- `dev-workflow/skills/distill-sessions/agents/prompt-{failure,success}-analysis.md` (template pattern for new advisory-analyst prompt)
- `dev-workflow/skills/distill-sessions/SKILL.md` (Stage 5c block needs prose update)

## Decision

**Build `dev-workflow:distill-sessions` v0.5** with **Architecture A — Sonnet-tier "advisory analyst" subagent replaces the entire heuristic clustering + rendering layer in v0.4.1's `report.py`**. Pipeline becomes:

```
Stage 4 merged.json
    ↓
Stage 5c report.py (now thin):
    1. Read merged.json
    2. Construct subagent prompt with:
       - Memory Items inline (all 33 fit easily — ~50K tokens)
       - Output template (7 sections, exact headings, language locale)
       - Code-block wrapping rules for copy-pasteable content
       - Language enforcement instruction (--lang zh-TW|en|ja)
    3. Caller (Claude Code session) dispatches Sonnet 4.6 subagent
    4. Subagent returns rendered markdown
    5. report.py writes to docs/skill-mining/<date>-advisory-report.md
```

**The subagent does**: semantic clustering of Memory Items into 3-5 distinct anti-patterns, identification of ≤5 real cross-skill CLAUDE.md candidates (semantic dedup vs surface-word noise), per-target SKILL.md modification list with code-block-wrapped suggested edits, new-skill-candidate detection (free with the LLM pass — section renders "0 candidates" if nothing found), summary numbers, action steps. All in user's working language for prose; code blocks stay English (target SKILL.md / CLAUDE.md is English).

**Cost estimate**: 1 Sonnet 4.6 call per run × ~50K input tokens + ~5K output tokens × $3/$15 per MTok = **~$0.23 per run**. At 2-5 runs/week locked cadence = ~$2-5/month. Negligible compared to v0.4 dogfood's $3-8/run (which has 11 subagent dispatches; v0.5 advisory is 1).

**Net LOC** (Q3=A reduces vs original brief estimate): ~+80 LOC net (~200 added for new dispatcher + new prompt + tests; ~120 deleted as heuristic functions are removed entirely, not preserved-under-flag).

**Lock**: Architecture A. Reverses v0.1 stdlib-only constraint scope to **report.py only** (other scripts preserved). All other locked v0.1/v0.4/v0.4.1 Q-decisions preserved.

### Q-locked decisions for v0.5

**Q-v0.5-1 — Architecture: Sonnet analyst / embedding+algorithm / hybrid?**

| # | Approach | Cost/run | Determinism | Effort | Verdict |
|---|---|---|---|---|---|
| **A** | **Sonnet 4.6 advisory analyst (chosen)** | **~$0.23** | Non-det but seed-stable | **~150 LOC + new agent prompt** | **✅ Lock** |
| B | Voyage-4-lite embedding + agglomerative clustering + Python rendering | ~$0.001 | Deterministic | ~300 LOC + voyageai SDK + scipy/scikit-learn | Eliminated — algorithm complexity not worth $0.001 savings; doesn't solve narrative-render quality (still needs template prose) |
| C | Embedding for clustering + Sonnet for narrative naming | ~$0.05 | Mixed | ~400 LOC + both stacks | Eliminated — over-engineered for 33-item dataset |

**Why A**: Smaller code surface; solves all three v0.5 goals (semantic clustering + code-block wrapping + language enforcement) in one architectural move. At 33 Memory Items / ~50K input tokens, Sonnet 4.6 is small enough to handle in one call (well within 1M context). Non-determinism acceptable for advisory output (read once per dogfood cycle; not a build artifact).

**Q-v0.5-2 — `--lang` flag default + detection?**

- A. `--lang zh-TW` hardcoded default; explicit `--lang en|ja` override
- B. `--lang zh-TW` hardcoded default + emit warning if `~/.claude/CLAUDE.md` "Working languages" field disagrees
- **C. `--lang` strict (no default; flag is mandatory; pick zh-TW / en / ja explicitly each run) (chosen 2026-05-27 dialogue)** — explicit > implicit; user works in 3 languages, no single sensible default
- D. Auto-detect from `~/.claude/CLAUDE.md` parsing; no flag

**Why C** (user lock 2026-05-27): user's CLAUDE.md states "Traditional Chinese / Japanese / English (match my message language)" — no single language is dominant enough to be a sensible silent default. Explicit-each-time avoids the "wrong-language render lurking under default" failure mode. Cost: must type `--lang zh-TW` every invocation (~10 chars extra). Acceptable for one operator running 2-5×/week.

**Q-v0.5-3 — Keep heuristic fallback when subagent dispatch fails / no Sonnet access?**

- **A. No fallback — fail-fast with clear error (chosen 2026-05-27 dialogue)** — clean break from v0.4.1; ~120 LOC of heuristic code deleted entirely (not preserved under `--mode heuristic` flag)
- B. Heuristic fallback retained for offline / no-Sonnet-access scenarios
- C. Always run heuristic, then Sonnet pass on top (double cost)

**Why A** (user lock 2026-05-27): v0.4.1 first-dogfood demonstrated heuristic quality is "離可用還有距離" (not actionable); keeping it as fallback is preserving known-low-quality output as a "safety net." User is single-operator with Anthropic API access — offline / no-key scenarios essentially never fire. If the scenario ever materializes, `git cherry-pick 28b4954d` revives v0.4.1 heuristic from history. Two code paths + flag branches + double docs is dead weight; A is honest commitment to the new architecture.

**Q-v0.5-4 — New-skill candidate detection: include in v0.5 or defer?**

- A. Defer to v1.0 broad-scope sibling (status quo: v0.4.1 placeholder "0")
- **B. Include in v0.5 (chosen)** — the Sonnet analyst is doing whole-dataset reasoning anyway; new-skill-candidate detection is a free byproduct of the same prompt; section renders "0 candidates" if analyst finds none (same UX as v0.4.1 placeholder)

**Why B**: marginal effort (one prompt section); LLM analyst is qualitatively better at recognizing "this friction has no SKILL.md home" than rule-based heuristics; doesn't expand scope appreciably (same subagent call, one more instruction). v1.0 broad-scope sibling still does broader new-skill-discovery work that's outside this scope.

**Q-v0.5-5 — Apply v0.4 + v0.4.1 KEEP items (manually) AS PART OF v0.5 PR?**

- A. Bundle — v0.5 PR ALSO commits the 13 KEEP items + 2 CLAUDE.md candidates from v0.4 dogfood
- **B. Separate (chosen)** — v0.5 = architectural change only; manual application of insights is a separate session (operator runs `/distill-sessions` after v0.5 ship, gets the NEW improved output, then decides what to apply)
- C. Defer indefinitely

**Why B**: cleaner PR scope; v0.5 ship should be a self-contained architectural change; bundling manual insight-application would inflate PR review surface; user can manually edit any time without blocking v0.5.

## Out of Scope

- Embedding-based clustering as building block (eliminated in Q-v0.5-1)
- Cross-runtime portability (still parked [[distill-sessions-v0-6-cross-runtime-parking]])
- Stage 4 (cluster.py) modification — v0.5 leaves the propose.py / apply.py cluster path untouched; the §pending bucket promotion logic remains exact-match for safety (apply.py writes to SKILL.md; high-confidence-only is correct disposition)
- Stage 1+2 ingest / friction signals — unchanged
- Stage 3 per-trajectory Trace2Skill subagents — unchanged (still 11 subagents producing Memory Items; cost ~$3-8 per full pipeline run)
- Manual application of v0.4 / v0.4.1 KEEP items (separate operator workflow)
- Auto-applying advisory items into SKILL.md (manual edit remains the path; preserves v0.1 Q4 "no silent writes")
- EN-language output default (still zh-TW per Q-v0.5-2)
- Output path arg customization beyond v0.4.1's `--output` flag
- Prompt caching for advisory subagent (single call per run; no caching benefit at this scale)
- Batch API for advisory subagent (single call → async batch is over-engineering)

## Alternatives Considered (research-grounded — 2026-05-27 WebSearch EN + JA)

### Embedding model alternatives (eliminated by Q-v0.5-1)

| # | Model | Pricing | Strengths | Verdict |
|---|---|---|---|---|
| 1 | OpenAI text-embedding-3-small | $0.02/MTok | Industry default, cheapest, multilingual | Eliminated (no embedding path in v0.5 — see Q-v0.5-1) |
| 2 | Voyage-4-lite | $0.02/MTok | Anthropic-recommended partner, shared embedding space, 32K context | Eliminated (ditto) |
| 3 | Voyage-3-large | $0.13/MTok | Domain-specialized (code/legal/medical), 14% RTEB lead | Eliminated (ditto) |
| 4 | Cohere embed-v4 | $0.10/MTok | Strong multilingual | Eliminated (ditto) |
| 5 | BGE-M3 (local, sentence-transformers) | $0 | Free, offline, 100+ languages, 8192 token context | Eliminated — adds ~2GB torch + sentence-transformers deps; v0.1 stdlib-only goal lost more aggressively than Sonnet SDK |
| 6 | ruri-v3-30m (local, JA-focused) | $0 | 37M params, JMTEB SOTA for Japanese | Eliminated — Memory Item titles are English |

### Clustering algorithm alternatives (eliminated)

| # | Algorithm | Strengths | Verdict |
|---|---|---|---|
| 1 | HDBSCAN | Density-based, no k needed, industry standard | Eliminated — "tends to underperform K-Means and GMM, identifying too few clusters and flagging many points as noise" (Encord 2026 guide); also adds scikit-learn or hdbscan dep |
| 2 | K-Means / GMM | Better at finding distinct clusters | Eliminated — requires `k`; tuning per-dataset; algorithm-not-subagent path eliminated |
| 3 | Agglomerative + distance threshold | Deterministic, no k | Eliminated — algorithm-not-subagent path eliminated |
| 4 | BERTopic (UMAP + HDBSCAN + topic representation) | Full topic-modeling pipeline | Eliminated — full pipeline overkill for 33 items |
| 5 | LLM-driven clustering ("Sonnet analyst") | Captures semantic nuance; one-shot reasoning | **✅ Chosen as Architecture A** (Q-v0.5-1) |

### Architecture-level alternatives (the real Axis 4)

| # | Architecture | Pros | Cons | Verdict |
|---|---|---|---|---|
| **A** | **Sonnet-tier advisory analyst subagent (chosen)** | One-shot; solves clustering + narrative + code-block + language in one move; ~$0.23/run; ~150 LOC | Non-deterministic; new agent prompt to maintain | ✅ Lock |
| B | Embedding (Voyage/OpenAI) + Python clustering algorithm + heuristic template (v0.4.1 shape upgraded) | Deterministic; cheap (~$0.001/run); reusable embedding building block | Doesn't solve template-prose narrative (still need to render the output somewhere); 2× the surface (embedding + clustering + render) | Eliminated |
| C | Hybrid: embedding for clustering, Sonnet for cluster-naming and narrative | Best determinism + quality | ~$0.05/run; most code surface; over-engineering for 33-item dataset | Eliminated |

**My take**: Architecture A wins on simplicity. At 33 items × ~50K tokens, semantic clustering is a trivial Sonnet call. Embedding + algorithm path is the "right way at scale" but kouko isn't operating at scale. The narrative-render quality (code-block wrapping, language-enforced prose) is the hard part — and LLM does that natively. Algorithm path forces a separate render template that still has the v0.4.1 noise problem. **One LLM call replaces both.**

**Sources cited** (Axis 4 research — 2026-05-27):
- [Complete Guide to Embeddings in 2026 — Encord](https://encord.com/blog/complete-guide-to-embeddings-in-2026/) (EN) — embedding model landscape; HDBSCAN limitations
- [OpenAI Embeddings vs Cohere Embed vs Voyage AI: 2026 — Index.dev](https://www.index.dev/skill-vs-skill/ai-openai-embed-vs-cohere-vs-voyage) (EN) — vendor comparison
- [Text Embedding Models 2026 — TokenMix](https://tokenmix.ai/blog/text-embedding-models-comparison) (EN) — pricing matrix
- [Voyage 3.5 vs OpenAI vs Cohere 2026 — buildmvpfast](https://www.buildmvpfast.com/blog/best-embedding-model-comparison-voyage-openai-cohere-2026) (EN) — Anthropic-Voyage partnership confirmation
- [Improving HDBSCAN on Short Text Clustering — IEEE 2023](https://ieeexplore.ieee.org/document/9640285/) (EN) — HDBSCAN + UMAP + Word Embeddings for short text
- [Embeddingモデル徹底比較2026 — renue Inc](https://renue.co.jp/posts/embedding-model-comparison-openai-voyage-cohere-ruri-2026) (JA) — JA embedding model landscape; ruri-v3 JMTEB SOTA; caching + dimensionality best practices
- [Best Open-Source Embedding Models 2026 — BentoML](https://www.bentoml.com/blog/a-guide-to-open-source-embedding-models) (EN) — BGE-M3, mxbai, sentence-transformers landscape
- [Human-interpretable clustering of short text using LLMs — arxiv 2405.07278](https://arxiv.org/pdf/2405.07278) (EN) — confirms LLM-driven clustering produces more interpretable groupings than embedding+algorithm for short text

## What Becomes Obsolete

**Same-PR removal on v0.5 ship**:

- `scripts/report.py:43-119` `_STOP_WORDS` frozenset + `_tokenize_title` helper → deleted (heuristic-only); preserved only under `--mode heuristic` opt-in path (Q-v0.5-3)
- `scripts/report.py:122-188` `cluster_by_title_keyword` → deleted from default path; preserved under `--mode heuristic`
- `scripts/report.py:191-247` `extract_claude_md_candidates` → same
- `scripts/report.py:271-456` 7 `_render_*` helpers → deleted from default path; preserved under `--mode heuristic`
- `scripts/test_report.py` heuristic-specific tests (5/8 tests) → rewritten to test subagent dispatch contract + output structure
- `dev-workflow/skills/distill-sessions/SKILL.md` §Stage 5c prose → updated to describe Sonnet analyst architecture; `--mode` flag documented; `--lang` flag documented
- `dev-workflow/.claude-plugin/plugin.json` `"version": "2.8.1"` → `"2.9.0"` (minor — new architecture)
- `dev-workflow/skills/distill-sessions/SKILL.md` `version: 0.4.1` → `0.5.0`
- v0.1 brief "stdlib-only" constraint scoped DOWN — was "all distill-sessions scripts"; becomes "all scripts EXCEPT report.py" (report.py becomes the orchestrator-dispatched-subagent surface, mirroring how main.py is orchestrator-dispatched-subagent surface for Stage 3)
- `agents/prompt-failure-analysis.md` + `agents/prompt-success-analysis.md` → unchanged content but the §"How the orchestrator dispatches" block gets updated to note the new sibling advisory-analyst prompt at the Stage 5c boundary

**New on v0.5 ship**:
- `dev-workflow/skills/distill-sessions/agents/prompt-advisory-analyst.md` (NEW) — Sonnet subagent prompt mirroring failure/success prompts' YAML-frontmatter shape
- `scripts/test_report.py` rewritten with structural assertions on dispatch shape + analyst-output schema

**Not obsoleted (intentional)**:
- All other distill-sessions scripts (main.py / propose.py / apply.py / cluster.py / aggregate.py / friction_signals.py / ingest.py / event.py / facets.py) — unchanged
- Stage 4 cluster.py exact-match clustering for propose.py / apply.py path — unchanged (high-confidence-only is correct disposition for SKILL.md write-back)
- v0.4 SUBAGENT_MODEL_ID + T5 cost-estimate preview — unchanged
- v0.4.1 fixture at `scripts/fixture_report_merged.json` — preserved
- Stage 3 per-trajectory Trace2Skill subagent prompts — unchanged
- v0.1 Q3/Q4/Q5/Q6 + v0.4 Q-v0.4-2 (SUBAGENT_MODEL_ID rename) + all v0.4.1 Q-decisions — preserved

## Open Questions

1. **Subagent prompt-caching for repeated runs**: if user re-runs report.py on same merged.json, can Anthropic prompt cache save the input tokens? Defer — first verify single-run quality.
2. **Output-format A/B testing**: v0.5 ship is a one-shot architectural change. Future v0.5.1+ could A/B different analyst-prompt phrasings to optimize quality; deferred until v0.5 ship runs ≥2 real dogfoods.
3. **Cross-vendor model fallback**: if user has OPENAI_API_KEY but not Anthropic, could v0.5 fall back to GPT-5 / GPT-4.5? Adds vendor matrix; defer unless [[distill-sessions-v0-6-cross-runtime-parking]] unparks.
4. **--lang detection error mode**: if `~/.claude/CLAUDE.md` Working-languages field disagrees with `--lang` arg, what's the behavior? Q-v0.5-2 lock chose warning-not-fail; verify the warning is actionable + non-noisy.
5. **Analyst-output schema validation**: should `report.py` schema-check the subagent's markdown output (e.g. assert 7 section headings present) before writing? Adds ~30 LOC + a parse step. Lean: ship without; surface in dogfood if subagent output frequently malformed.

## Handoff to writing-plans

Input ready for [`code-toolkit:writing-plans`](../../../code-toolkit/skills/writing-plans/SKILL.md):

- **Brief**: this file (`docs/code-toolkit/specs/2026-05-27-distill-sessions-v0.5-brief.md`)
- **Predecessor briefs**: v0.4.1 + v0.4 + v0.3 + v0.1
- **Touch points verified**: report.py + test_report.py + agents/prompt-advisory-analyst.md (NEW) + SKILL.md + plugin.json
- **Sibling prompt models**: agents/prompt-failure-analysis.md + agents/prompt-success-analysis.md (existing patterns to mirror)
- **Fixture preserved**: scripts/fixture_report_merged.json

`writing-plans` should produce **~4-5 atomic tasks**:

| Task (preview) | Scope |
|---|---|
| T1 | NEW: `agents/prompt-advisory-analyst.md` — Sonnet subagent prompt; YAML frontmatter (role / model / input_contract / output_contract / hard_constraints / language) + role-play body + 7-section output template with code-block-wrapping rules + language-enforcement rule. Pure markdown — no test infrastructure |
| T2 | `scripts/report.py` rewrite — strip heuristic functions to `_heuristic_*` namespace under `--mode heuristic`; default `--mode analyst` constructs subagent dispatch payload + writes the subagent's returned markdown to output file. Add `--lang zh-TW\|en\|ja` flag (default zh-TW; warning if CLAUDE.md mismatch). Add `--mode analyst\|heuristic` flag (default analyst). TDD: failing test on dispatch shape + lang flag + mode flag behavior |
| T3 | `scripts/test_report.py` rewrite — drop 5 heuristic-specific tests; add structural assertions on dispatch payload shape + analyst-output schema + mode flag + lang flag. ~6-8 new tests |
| T4 | SKILL.md updates: §Stage 5c prose describes analyst architecture; flag documentation; pipeline ASCII updated (Stage 5c now dispatches subagent like Stage 3 does); version 0.4.1 → 0.5.0 |
| T5 | plugin.json version 2.8.1 → 2.9.0 |

T1 + T2 + T3 form a tight cluster (T2 needs T1's prompt file existing for tests in T3 to assert dispatch payload references it correctly). T4 + T5 are docs/version (independent, dispatch-parallel after T2+T3). Probably plan executes:
- Wave 1: T1 (prompt file; sets up subagent contract)
- Wave 2: T2 (rewrite report.py against T1's contract)
- Wave 3 (parallel): T3 + T4 + T5

Actually T1+T2 might merge into one task if the prompt-file-write is tight enough; tradeoff for `writing-plans` to decide.

---

**Brief complete.** Next step: invoke [`code-toolkit:writing-plans`](../../../code-toolkit/skills/writing-plans/SKILL.md).
