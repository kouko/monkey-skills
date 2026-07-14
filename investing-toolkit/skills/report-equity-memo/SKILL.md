---
name: report-equity-memo
description: |
  Layer-3 orchestrator for a full equity investment memo (Markdown). Routes by ticker to data-markets memo-fetch (market auto-detected), runs analysis-dcf + macro-regime, then delegates the memo protocol + gates to domain-teams:investing-team. Pure orchestration.
---

# report-equity-memo

Layer 3 orchestrator in the v2.0.0 three-layer architecture
(Data → Analysis → Report). This skill owns **pipeline assembly only** — it
does not fetch data, compute indicators, or render verdicts inline. All
fetching is delegated to Layer 1 (`data-markets`), all numerical compute
to Layer 2 (`analysis-*`), and all analytical judgement + gates to
`domain-teams:investing-team` per the Cross-Plugin Delegation Contract.

> **Migration note (v2.0.0)**: This skill replaces the v1.x
> `investment-memo-writer`, which was deleted in v2.0.0. The slash command
> `/report-equity-memo` continues to route here.

---

## Inputs

| Parameter | Required | Default | Notes |
|-----------|----------|---------|-------|
| `ticker` | yes | — | e.g. `AAPL`, `7203` (or `7203.T`), `2330.TW`, `005930.KS`, `600519.SS` |
| `scope` | no | `deep` | `deep` = full memo; `quick` = summary snapshot (skips Phase 2 regime fan-out + Phase 2.5 comps + Phase 2.6 xval + Phase 3 DCF; uses snapshot data only). investing-team protocol routing decides depth from this value. |
| `output_language` | no | auto-detect | `.TW` / `.TWO` → `zh-TW`; `.T` / `.TO` / 4-digit JP → `ja`; `.KS` / `.KQ` → `ko`; `.SS` / `.SZ` / `.HK` → `zh-CN`; otherwise infer from user message |
| `peers` | no | auto-discovery via runtime research agent | Comma-separated peer list (e.g., `MSFT,GOOGL,META,AMZN`); skips runtime peer-discovery if provided. |
| `--interactive` | no | `false` (auto mode) | When `true`, peer-discovery agent's output is presented for user confirmation before Comps fetch + analysis. |

### Country detection

Ticker suffix → market code (preserves v1.x convention). `data-markets/scripts/pack.py`
auto-detects this from the ticker; pass `--market <cc>` explicitly to override
(required for `--pack regime-pack`, which has no ticker dimension):

| Suffix / pattern | Country | market code | yfinance ticker rewrite |
|---|---|---|---|
| `.TW`, `.TWO` | Taiwan | `tw` | unchanged (e.g. `2330.TW`) |
| `.T`, `.TO`, bare 4-digit (e.g. `7203`) | Japan | `jp` | auto-append `.T` (handled inside `data-markets/scripts/pack_jp.py`) |
| `.KS`, `.KQ` | Korea | `kr` | unchanged |
| `.SS`, `.SZ`, `.HK` | China / HK | `cn` | unchanged |
| anything else (e.g. `AAPL`, `NVDA`) | US | `us` | unchanged |

Set `${COUNTRY}` accordingly for the rest of the pipeline (used as the
`--market` override where a pack type has no ticker dimension, e.g. Phase 2).

---

## Pipeline

> **MUST — no narration-only completion.** A phase is done only when its
> artifact exists on disk, confirmed by `ls`. Never tell the user the memo
> (or any phase) is complete without citing the artifact path(s) `ls`
> confirmed. If a phase produced no artifact (blocked, skipped, errored),
> say so explicitly — do not describe output as if it were saved.

### Phase 0 — Recall Prior Verdicts

> Runs **before** Phase 1. Pure grep + read — no judgment call, weak-model-safe.

**Resolve a search root** (best-effort; no error if none resolves):

```bash
if [ -d .obsidian ] || [ -n "${VAULT_PATH:-}" ]; then
  SEARCH_ROOT="${VAULT_PATH:-.}"          # cwd is a vault, or user named one
elif ls /tmp/*-memo.md >/dev/null 2>&1; then
  SEARCH_ROOT=/tmp                        # prior memo output from this session
else
  SEARCH_ROOT=""                          # nothing resolved
fi
```

**No root resolved**: silent skip — no error, proceed straight to Phase 1. Note
the skip in the memo's Limitations section (Phase 4).

**Search** (when a root resolved) for the ticker's frontmatter, per
`references/vault-frontmatter.md`'s `ticker` field:

```bash
grep -rl "^ticker: ${TICKER}$" "$SEARCH_ROOT" --include="*.md" 2>/dev/null
# NOTE: escape regex dots in suffixed tickers first, e.g. TICKER_RE=${TICKER//./\\.}
# and grep for "^ticker: ${TICKER_RE}$" — a bare . would match any character.
```

**No hits**: silent skip — mirrors Phase 5b's graceful-skip shape (see its closing artifact-gate paragraph).
No error, proceed to Phase 1. Note in the memo's Limitations section that no
prior verdict was found.

**Hits found**: read the most recent match's frontmatter (highest `date`),
extract `verdict`, `date`, `price_at_analysis`. Surface before Phase 1 starts:

> Prior verdict for {ticker}: {verdict} @ {date}, price_at_analysis {price}.

After Phase 1's fetch completes, compute delta = current `fetch.json`
`current_price` − prior `price_at_analysis` (value and %) and surface it too.
Carry {prior verdict, date, price_at_analysis, delta} into the Phase 4 seed
context so the new memo's Limitations section discloses the recall outcome
(hit-and-cited / no-hits / skipped) — exactly one of these three, never
silent about which.

### Phase 1 — Data Fetch

> **`scope=quick` note**: quick mode runs Phase 1 only (snapshot data) and skips Phase 2 (regime) + Phase 2.5 (comps) + Phase 2.6 (xval) + Phase 3 DCF. The pipeline jumps straight to Phase 4 with snapshot-only inputs; investing-team protocol routing handles the lighter analysis depth.

Single subprocess call per ticker. The merged `data-markets/scripts/pack.py --pack memo-fetch`
facade auto-detects the market from the ticker and composes all required clients
(e.g. SEC EDGAR + yfinance + FRED for US; EDINET + TDnet + yfinance for JP with
Tier-A / Tier-2 routing on `EDINET_API_KEY`; MOPS + TWSE OpenAPI + FinMind
gap-fill for TW; FDR for KR; NBS + akshare for CN).

```bash
uv run ${CLAUDE_PLUGIN_ROOT}/skills/data-markets/scripts/pack.py \
    --ticker ${TICKER} --pack memo-fetch \
    > /tmp/${TICKER_SAFE}-fetch.json
```

`${TICKER_SAFE}` strips the suffix (`AAPL`, `7203`, `2330`, `005930`, `600519`) for filesystem safety.

**Artifact gate**: Phase 1 is not complete until `/tmp/${TICKER_SAFE}-fetch.json` exists — verify with `ls /tmp/${TICKER_SAFE}-fetch.json` before proceeding.

The data layer owns Tier-A / Tier-2 routing; this skill never decides which
client to call — `pack.py` returns a single normalised JSON regardless of
underlying source mix. Provenance labels (e.g. `_provenance.tier_label`) ride
along on the payload and surface in the final memo.

### Phase 2 — Macro Regime

Fetch the macro regime-pack(s) relevant to the ticker.

**Deterministic default rule:**

> Default: fetch home country only. When `scope=deep`, also fetch US (for any
> non-US ticker, since US rates dominate global liquidity). Cross-listed
> exposure or sector-specific macro flags can be handled by the orchestrator's
> main agent — but the canonical default is home + (US if non-US ticker AND
> deep).

```bash
# Per relevant country (always at minimum the ticker's home country)
uv run ${CLAUDE_PLUGIN_ROOT}/skills/data-markets/scripts/pack.py \
    --pack regime-pack --market ${COUNTRY} \
    > /tmp/${COUNTRY}-regime.json
# (repeat for additional countries as needed: us / jp / tw / kr / cn)

# Compose into a regime card
uv run ${CLAUDE_PLUGIN_ROOT}/skills/analysis-macro-regime/scripts/regime_compose.py \
  --input ${COUNTRY}=/tmp/${COUNTRY}-regime.json[,us=/tmp/us-regime.json,...] \
  > /tmp/regime-card.json
```

`analysis-macro-regime` accepts any subset of `us/jp/tw/kr/cn` so the cross-country
list scales with the memo's scope.

**Artifact gate**: Phase 2 is not complete until `/tmp/regime-card.json` exists — verify with `ls /tmp/regime-card.json` before proceeding.

### Phase 2.5 — Peer Discovery + Comps Multiples

**If `--peers` provided** (manual override): skip discovery, use the list verbatim. (Manual-override mode: provenance shows `source: user-provided` for each peer; no rationale required.)

**Else** spawn research agent for peer-discovery at runtime:

Dispatch a general-reasoning subagent with this prompt template. (For
the concrete per-host dispatch call and agent-type mapping — `general-purpose`
on Claude Code, `default` on Codex — see `references/claude-code-tools.md`
/ `references/codex-tools.md`.)

> Find 5–8 publicly-traded competitor tickers for {anchor_ticker} ({company_name}).
>
> Selection criteria (in order):
> 1. Direct business-line competitor (same products/services)
> 2. Comparable scale tier (market cap within 0.3x–3x range)
> 3. Same primary geography or comparable geographic mix
> 4. Listed on major exchanges (US/JP/TW/KR/CN/HK/Europe)
>
> For each peer, provide:
> - Ticker symbol (with exchange suffix if non-US: .T, .TW, .KS, etc.)
> - 1-line rationale explaining why it's a comp
> - Source URL (corporate disclosure, industry report, or competitor analysis)
>
> Output as JSON:
> {"peers": [{"ticker": "MSFT", "rationale": "...", "source": "https://..."}]}
>
> Cap: 250 words total. No industry-rollup commentary — just the peer list.

**Mode switch**: if `--interactive=false` (default, pipeline mode), the orchestrator
proceeds directly from agent JSON to anchor/peer fetch. If `--interactive=true`,
present the agent's JSON list + rationales, wait for user `/proceed` or edits, then fetch.

**Default behavior** (configurable):

| Context | Discovery flow |
|---|---|
| Pipeline mode (called by orchestrator / memo automation) | **Auto** — agent finds peers → analysis runs immediately → peer list + rationale visible in process logs and final report |
| CLI mode (`--interactive`) | **Interactive** — agent finds peers → presents list + rationale → user `/proceed` confirms or edits → analysis runs |

**Provenance transparency requirement** (per Spec §5.6 — peer list visible at three points):

1. **During execution**: main agent logs `Using peers: X (reason), Y (reason), Z (reason)` before fetch starts
2. **In analysis JSON**: `_provenance.peer_data_sources` lists each peer + how it was selected
3. **In final memo**: Comps section header explicitly lists peers + 1-line rationale per peer

The reader never wonders "Comps against whom?"

**Then fetch + analyze**:

```bash
# 0. Persist the peer-discovery agent's JSON output (or the --peers manual list
#    converted to {"peers": [{"ticker", "rationale": null, "source": null}]})
#    as /tmp/peer-rationales.json — analysis-comps reads this for provenance.

# 1. Fetch anchor multiples
uv run ${CLAUDE_PLUGIN_ROOT}/skills/data-markets/scripts/pack.py \
    --ticker ${TICKER} --pack comps-multiples \
    > /tmp/${TICKER_SAFE}-anchor-comps.json

# 2. Fetch peer multiples (group peers by country, run per-country batch)
# Per peer country group:
uv run ${CLAUDE_PLUGIN_ROOT}/skills/data-markets/scripts/pack.py \
    --tickers ${PEERS_FOR_COUNTRY} --pack comps-multiples \
    > /tmp/${COUNTRY}-peers-comps.json
# Repeat for each country present in the peer list.

# 3. Run analysis-comps in compute mode (v2.2.0-b+; sector-aware since v2.2.0-c)
# anchor memo-fetch already pre-fetched in Phase 1: /tmp/${TICKER_SAFE}-fetch.json
# Compute mode emits multiples_direct + multiples_compute + divergence + indicators
# (v2.2.0-c) in one JSON. Sector classification is automatic from
# info.sector + info.industry on the anchor pack — no flag needed.
# Override available via --sector-override <id> (debug only) when yfinance
# misroutes a holdco / multi-segment issuer not yet captured in
# analysis-comps/references/sector-overrides.yaml.
uv run ${CLAUDE_PLUGIN_ROOT}/skills/analysis-comps/scripts/comps_compute.py \
  --mode compute \
  --anchor       /tmp/${TICKER_SAFE}-anchor-comps.json \
  --anchor-base  /tmp/${TICKER_SAFE}-fetch.json \
  --peers        /tmp/<peer1>-comps.json,/tmp/<peer2>-comps.json,... \
  --rationale-map /tmp/peer-rationales.json \
  > /tmp/${TICKER_SAFE}-comps.json
```

**Artifact gate**: Phase 2.5 is not complete until `/tmp/${TICKER_SAFE}-comps.json` exists — verify with `ls /tmp/${TICKER_SAFE}-comps.json` before proceeding.

Pass `/tmp/${TICKER_SAFE}-comps.json` to investing-team in Phase 4 alongside `dcf.json` / `regime.json`.

**Sector-aware shape (v2.2.0-c+)**: the comps JSON now carries
`anchor.schema_id` (one of `default / bank / insurance / asset-manager
/ reit / tech-saas / tech-semis / energy / utilities`) and
`anchor.indicators` (operating-context metrics like ROE / Rule-of-40
/ FCF-yield, sector-dependent). `multiples_compute` keys are
schema-driven — non-default schemas omit irrelevant multiples (e.g. a
bank anchor has no `evEbitda` because it's undefined for banks; a REIT
anchor uses `priceToFFO + evEbitdare` instead of `trailingPE +
evEbitda`). Phase 4 investing-team consumes this shape transparently —
relative-valuation gates iterate the schema's multiple set rather than
assuming a fixed-5 schema.

### Phase 2.6 — xval Cross-Validation (US tickers only)

**US tickers only.** `xval_source_a` / `xval_source_b` are SEC-specific keys
`data-markets/scripts/pack_us.py::pack_memo_fetch` emits — non-US fetch packs
never carry them. For a non-US ticker, skip this phase silently (no error,
no `xval.json`) and note in the memo's Limitations section that xval
cross-validation is US-only.

**Layer discipline**: the COMPUTE runs **here** (this analysis phase), not
in the data-markets pack layer — `pack_memo_fetch` only fetches + wraps the
two source packs (`xval_source_a` doc-table cells, `xval_source_b`
companyfacts), it never runs `xval_compute.py` itself. This mirrors the
Phase 2.5 / Phase 3 split (comps/DCF compute in the analysis phase, not in
`pack.py`), NOT `sec_narrative`'s eager-in-pack pattern.

**Depth-1 status check** (mirrors the DCF/comps artifact-gate discipline):
read `/tmp/${TICKER_SAFE}-fetch.json`'s `xval_source_a._status` and
`xval_source_b._status`. If either key is **absent** or its `_status` is
`"failed"`, this is a **loud skip** — do not run `xval_compute.py`, do not
write `xval.json`, and note in the memo's Limitations section which side
failed (e.g. "xval skipped: xval_source_b._status=failed,
error=cik_unresolved"). Never fabricate an empty-but-present `xval.json` to
paper over a failed/absent source. A `_status: "partial"` `xval_source_a`
(some of the 4 primary statements failed, `failed_items` populated) still
proceeds — the cells that did succeed are cross-validated; the memo's
Limitations section separately discloses the partial per-statement gap from
`failed_items`.

**Else, extract + run:**

```bash
# 1. Extract the two xval source packs from the memo-fetch JSON.
#    xval_source_a wraps FOUR per-statement envelopes under "statements"
#    (BalanceSheet/IncomeStatement/CashFlowStatement/StatementOfEquity);
#    xval_compute.py's --source-a expects ONE flat pack with a top-level
#    "cells" list (mirrors the declared Source-A cell schema, whose own
#    per-cell citation.statement_name already preserves which statement a
#    cell came from) -- so flatten the 4 statements' cells into one list,
#    same combine-then-single-call pattern report-screener-list uses for
#    multi-country screener packs (SKILL.md's Step 3).
#    xval_source_b is already the flat {cik, facts, ...} shape
#    build_source_b_index expects -- pass it through as-is.
python3 -c "
import json, sys
from pathlib import Path
fetch = json.loads(Path(sys.argv[1]).read_text())
src_a = fetch.get('xval_source_a', {})
cells = [cell for stmt in src_a.get('statements', []) for cell in stmt.get('cells', [])]
combined_a = {'accession': next((s['accession'] for s in src_a.get('statements', [])), None),
              'statement_name': 'combined-primary-statements', 'cells': cells}
print(json.dumps(combined_a))
" /tmp/${TICKER_SAFE}-fetch.json > /tmp/${TICKER_SAFE}-xval-source-a.json

python3 -c "
import json, sys
from pathlib import Path
fetch = json.loads(Path(sys.argv[1]).read_text())
print(json.dumps(fetch.get('xval_source_b', {})))
" /tmp/${TICKER_SAFE}-fetch.json > /tmp/${TICKER_SAFE}-xval-source-b.json

# 2. Run analysis-xval in compute mode
uv run ${CLAUDE_PLUGIN_ROOT}/skills/analysis-xval/scripts/xval_compute.py \
  --source-a /tmp/${TICKER_SAFE}-xval-source-a.json \
  --source-b /tmp/${TICKER_SAFE}-xval-source-b.json \
  > /tmp/${TICKER_SAFE}-xval.json
```

**Artifact gate**: when this phase runs (non-US tickers and loud-skip cases
are exempt), Phase 2.6 is not complete until `/tmp/${TICKER_SAFE}-xval.json`
exists — verify with `ls /tmp/${TICKER_SAFE}-xval.json` before proceeding.

Pass `/tmp/${TICKER_SAFE}-xval.json` to investing-team in Phase 4 alongside
`dcf.json` / `comps.json` / `regime.json` (omit it from the Resource Paths
list when this phase was skipped, and say so in the seed context instead).

### Phase 3 — Analysis

Run pure-compute analysis skills on the Phase 1 fetch JSON.

```bash
# DCF — 3-stage Damodaran with 3×3 sensitivity
uv run ${CLAUDE_PLUGIN_ROOT}/skills/analysis-dcf/scripts/dcf_compute.py \
  --input /tmp/${TICKER_SAFE}-fetch.json \
  > /tmp/${TICKER_SAFE}-dcf.json
```

**Artifact gate**: Phase 3 is not complete until `/tmp/${TICKER_SAFE}-dcf.json` exists — verify with `ls /tmp/${TICKER_SAFE}-dcf.json` before proceeding.

> **Comps note**: relative valuation is computed in **Phase 2.5** (peer
> discovery + `analysis-comps`). The resulting `/tmp/${TICKER_SAFE}-comps.json`
> is passed to investing-team in Phase 4 alongside the DCF and regime JSONs,
> so Phase 4's relative-valuation gates run on the structured comps JSON, not
> prose.

Each analysis skill called from Phase 3 is pure compute (Layer 2 contract).
They emit a JSON-only payload — no Markdown, no verdict prose. That is
investing-team's job.

### Phase 4 — Delegate to `domain-teams:investing-team`

Launch `domain-teams:investing-team` with the **Deep Equity Research Memo** protocol
(`protocols/deep-equity-research-memo.md`) and the canonical gate stack.

**Per Cross-Plugin Delegation Contract (CLAUDE.md §Cross-Plugin Delegation Contract):**

1. Pass **paths** to the Phase 1 / 2 / 2.5 / 2.6 / 3 JSONs as `### Resource Paths` — never file content. Specifically: `fetch.json` (Phase 1), `regime-card.json` (Phase 2), `comps.json` (Phase 2.5), `xval.json` (Phase 2.6 — US tickers only; omit + state the skip reason when Phase 2.6 was skipped), `dcf.json` (Phase 3).
2. Pass the ticker, scope, output_language, country code as `### Input` seed
   context — plus Phase 0's recall outcome (prior verdict/date/price/delta,
   or the no-hits/skipped fact) so investing-team can disclose it in the
   memo's Limitations section
2b. The seed context MUST also carry the six verdict-layer defense elements
   — `rule_verdict` (binding-or-gated), the pack-section inventory (generate
   via `scripts/pack_inventory.py`), date-anchoring rule, the
   verbatim-disclosure pass bar, the `sec_narrative` read-before-cite
   rule (US tickers: `text_path` is a path, not text — open it before
   citing), and the `xval` read-before-cite rule (US tickers with an xval
   report: check `high_alerts` before citing a statement-table number) —
   per
   `references/phase4-seed-contract.md`, which also defines the
   orchestrator's acceptance greps on the returned memo
3. The investing-team worker self-loads its standards / protocols / rubrics and runs the full gate stack — relative-valuation gates consume the structured `comps.json`, not prose
4. Gate verdicts (PASS / NEEDS_REVISION) flow back from investing-team's evaluators — this skill does not produce verdicts
5. Visibility Convention: include the skill-team TaskUpdate cadence clause (phase transitions / milestones / heartbeat ≤60s) so the user sees progress during the multi-minute investing-team run

**Gates that run** (investing-team canonical stack):

| Gate | Level | Source |
|------|-------|--------|
| Primary-Source Citation Compliance | **MUST** | `checklists/primary-source-citation-compliance.md` |
| Investment Thesis Soundness | **MUST** | `checklists/investment-thesis-soundness-checklist.md` |
| Scenario Stress-Test | SHOULD | `rubrics/scenario-stress-test-gate.md` |
| Position-Sizing Rationale | SHOULD | `rubrics/position-sizing-rationale-gate.md` |
| Market-Regime Consistency | SHOULD | `rubrics/market-regime-consistency-gate.md` |
| Signal Quality (ISQ) | SHOULD | `rubrics/signal-quality-assessment-gate.md` |
| Taiwan Local Rigor | MAY | `rubrics/taiwan-local-rigor-gate.md` (auto-triggered for `.TW` / `.TWO`) |

**Comps divergence (v2.2.0-b+)**: when `comps.json` has `anchor.divergence[*].alert == "high"`, the Comps section MUST surface the divergence source — e.g. "yfinance trailingPE 28.5x vs SEC raw recompute 36.7x — Yahoo's adjusted EPS differs from FY GAAP". Cite the relevant SEC accession from `compute_provenance[*].accession_basis`. Medium alerts may be mentioned briefly; low alerts are upstream-rounding noise and stay silent.

**Sector-aware Comps narrative (v2.2.0-c+)**: lead the Comps section with `anchor.schema_id` context — e.g. "JPM (bank schema): P/B 1.81x, ROE 16.2%; sector peers ..." — because the multiples Phase 4 sees depend on schema. For non-default schemas, REIT P/FFO and EV/EBITDAre are NAREIT approximations (gains_on_sale / impairment not available in standard XBRL); the per-multiple `compute_provenance.note` discloses this — surface it in the memo when the multiple is load-bearing for the verdict. Indicators (`anchor.indicators`) are sector-specific operating-context metrics rendered as `pct` units (e.g. `{"ROE": {"value": 16.2, "unit": "pct"}}`); cite them alongside multiples to give the reader a profitability anchor that the multiple alone doesn't convey.

For non-US tickers (.T / .TW / .KS / .KQ / .HK / .SS / .SZ), substitute the `data-markets/scripts/pack.py --pack memo-fetch` output (market auto-detected from the ticker) for `--anchor-base`. Compute-mode US-first; non-US compute mode lands in per-country PRs (until then, falls back to direct with stderr warning).

The investing-team output is the memo body (Markdown). Before persisting,
prepend the toolkit frontmatter block (schema SSOT:
`references/vault-frontmatter.md`) — the 8 fields (`type`, `ticker`,
`market`, `date`, `verdict`, `confidence`, `price_at_analysis`,
`intrinsic_mid`; `confidence` is omitted when the memo reports none — see
the schema SSOT), values sourced from this run (verdict/confidence from
the memo's §一 執行摘要, `price_at_analysis` from Phase 1 `fetch.json`
`current_price`, `intrinsic_mid` from Phase 3 `dcf.json` `mid`) — so the
file is `---\n<8 fields>\n---\n` followed by the memo body. This emission
is unconditional, regardless of destination (Phase 5a/5b optional or
skipped). Persist the result to `/tmp/${TICKER_SAFE}-memo.md` before
replying to the user.

**Artifact gate**: Phase 4 — and the memo overall — is not complete until
`/tmp/${TICKER_SAFE}-memo.md` exists AND starts with the frontmatter
block — verify with `ls /tmp/${TICKER_SAFE}-memo.md` and
`head -1 /tmp/${TICKER_SAFE}-memo.md` (must print `---`). Do not tell the
user the memo is ready until both checks have been run and the path cited
in the reply.

### Phase 5a — Format (optional, `domain-teams:docs-team`)

If the user requests polished document output (PDF-ready memo, formatted
report, vault-ready note), pass the Phase 4 memo as input to
`domain-teams:docs-team`. Skip this phase for in-conversation analysis or
when the memo is already in a target-ready shape.

### Phase 5b — Obsidian vault delivery (optional, `obsidian:obsidian-markdown`)

For Obsidian vault delivery (`output=obsidian` or natural-language intent),
call `obsidian:obsidian-markdown` after docs-team formatting to write to
the resolved vault path. If Phase 5a is skipped, 5b reads the Phase 4
memo directly.

**Field ownership**: the frontmatter fields are already present — Phase 4
prepended them per the toolkit schema SSOT (`references/vault-frontmatter.md`).
obsidian-markdown MUST respect these fields as-is and MUST NOT re-invent
or overwrite them; it owns placement, wikilinks, callouts, and vault
conventions only. Default vault folder: `investing/memos/` — a
default-unless-user-says-otherwise convention, not a hard requirement;
follow a user-named or vault-configured path when given one. Filename:
`YYYY-MM-DD {ticker} Equity Memo.md` (e.g. `2026-07-12 2330.TW Equity
Memo.md`) per the naming section of `references/vault-frontmatter.md` —
ticker as-is including its dot suffix; same-day re-analysis updates the
existing note instead of minting a sibling.

> **Cross-Plugin Contract recap (Phase 5b)**: Pass the docs-team Markdown
> output **path** (not content) as input to obsidian-markdown — same
> paths-not-content discipline as Phase 4.

**Artifact gate**: if Phase 5a or 5b runs, the same rule applies — confirm
the resulting file exists (`ls` the docs-team output / vault path) before
citing it as done; if it was skipped, tell the user `/tmp/${TICKER_SAFE}-memo.md`
(Phase 4) is the final artifact.

---

## Cross-Plugin Delegation Contract (recap)

This skill is the canonical example of the contract codified in CLAUDE.md:

- **Data layer stays in toolkit, analysis layer stays in domain-teams** —
  `report-equity-memo` only orchestrates data fetch + pipeline; gate logic
  belongs to `domain-teams:investing-team`.
- **Delegation = pass paths + structured seed context** — never file content,
  never inlined analysis.
- **Gate verdicts flow back** — `PASS` / `NEEDS_REVISION` from investing-team
  evaluators are surfaced in the final memo "Gate Results" section, not
  swallowed by this skill.

---

## Limitations

- yfinance is an unofficial scraper (Tier 2). Tier A primary-source paths
  are used per market defaults (SEC EDGAR for US; EDINET for
  JP when `EDINET_API_KEY` set; MOPS + TWSE OpenAPI for TW always; FDR /
  BOK ECOS-KEYSTAT for KR; NBS new-SPA + akshare for CN). See
  `data-markets/references/market-{us,jp,tw,kr,cn}.md` for the per-country tier matrix.
- Analyst consensus + forward guidance are not in scope (philosophy:
  primary-source equity research). If consensus context is needed, surface
  the data gap in the memo's "Limitations" rather than mocking it.
- `data-markets/scripts/pack.py --pack memo-fetch` is single-ticker by design
  (heavy SEC / EDINET / MOPS calls). Batch memo runs over many tickers
  must be sequenced at the user level.

---

## i18n footer

- 日本語: 株式投資メモの編成層（Layer 3）。ticker から market を自動判定し、
  `data-markets` の memo-fetch / regime-pack を呼び出したうえで、
  `analysis-dcf` + `analysis-macro-regime` + `analysis-comps` + `analysis-xval`（US のみ）を pure compute で走らせ、Deep
  Equity Research Memo protocol（2 MUST + 4 SHOULD + 1 MAY gate）の実行を
  `domain-teams:investing-team` に委譲。最終整形は任意で
  `domain-teams:docs-team`。
- 繁體中文: 權益投資備忘錄編排層（Layer 3）。依 ticker 自動判定市場，呼叫
  `data-markets` 的 memo-fetch / regime-pack，於
  `analysis-dcf` + `analysis-macro-regime` + `analysis-comps` + `analysis-xval`（僅美股）進行純計算，再將 Deep Equity
  Research Memo protocol（2 MUST + 4 SHOULD + 1 MAY 閘）委派給
  `domain-teams:investing-team`。最終排版可選 `domain-teams:docs-team`。
- English: Layer 3 orchestrator for equity investment memos. Auto-detects
  the market from the ticker and calls `data-markets` memo-fetch / regime-pack,
  runs `analysis-dcf` + `analysis-macro-regime` + `analysis-comps` + `analysis-xval`
  (pure compute; xval is US-only), delegates
  the Deep Equity Research Memo protocol (2 MUST + 4 SHOULD + 1 MAY gates)
  to `domain-teams:investing-team`, optional final formatting via
  `domain-teams:docs-team`.
