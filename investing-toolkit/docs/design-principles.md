# investing-toolkit Design Principles

Meta-conventions for architecting this plugin. Not prescriptive rules;
lessons earned the hard way through shipped-then-corrected PRs.

---

## 1. Empirical-first design (coined v1.16.3)

**Rule**: Before designing any new source / router / multi-path
architecture, empirically probe the actual behavior. Do not design
around hypotheses alone.

**Why the rule exists**: Two shipped PRs in 2026-04-19 failed the
"hypothesis survives contact with reality" test:

### Incident 1 — v1.14.0 "MCP bypasses Cowork sandbox"

- **Hypothesis** (Phase 1 Explore report): Claude Desktop Cowork runs
  plugin-installed stdio MCP servers as child processes **outside** the
  sandbox, with the user's shell env + unrestricted network.
- **Reality** (confirmed in Cowork empirically, v1.16.1): plugin-MCP
  runs **inside** the same sandbox as plugin-subprocess. URL allowlist
  applies equally. Anthropic's own plugins all use remote `type: http`
  MCP for exactly this reason — a signal we misread as "they prefer
  remote" rather than "local stdio is sandboxed".
- **Cost**: ~1,300 LOC of MCP infrastructure (servers/ bootstrap +
  wrapper + setup + mcp_server) shipped under a false pretense. Kept
  the code (still works in Code CLI + preserves optionality) but had
  to ship v1.16.1 correcting all 9 SKILL.md blockquotes +
  docs/mcp-setup.md with a retrospective.

### Incident 2 — v1.16.3 ".TW needs TWSE /rwd/ Tier A because yfinance is patchy"

- **Hypothesis**: yfinance TW coverage uneven → need TWSE `/rwd/` +
  FinMind as primary/fallback for `.TW`/`.TWO` tickers.
- **Reality** (empirical probe 2026-04-19 mid-PR): yfinance actually
  handles 2330.TW / 2317.TW / 3105.TWO / 6488.TWO cleanly with full
  info + sufficient history for SMA-200. Better still, yfinance
  returns **split-adjusted** prices which are the TA industry standard.
- **Cost**: 5 commits designed around the wrong hypothesis. Commit 6
  flipped Phase 1 back to yfinance-primary. TWSE `/rwd/` action kept
  (useful for memo primary-source citation) but demoted from "default
  router target" to "explicit-request advanced mode".

---

## 2. Three-layer architecture (Data / Analysis / Report) — codified v2.0.0

**Rule**: Every skill belongs to exactly one of three layers
(`data-*` / `analysis-*` / `report-*`) with strict layer-responsibility
separation.

**Why the rule exists**: Through v1.x the toolkit grew to 15 skills
with overlapping concerns. Two structural problems became blocking:

- **Mixed concerns inside a single skill** — `us-stock-snapshot`,
  `japan-stock-snapshot`, `taiwan-stock-snapshot`, `dcf-valuation`,
  `stock-screener`, `invest-portfolio`, `investment-memo-writer` all
  bundled fetch + compute + format. When TWSE OpenAPI added `/rwd/`
  in v1.16.3, edits had to be replayed across several skills with
  subtle drift.
- **50+ duplicate client files** — `yfinance_client.py` in 11 skills,
  `fred_client.py` in 7, `ta_client.py` in 3, each silently drifting
  between PRs because there was no CI gate enforcing sync.

### Layer responsibilities

| Layer | Owns | Forbidden | Cross-skill calls |
|---|---|---|---|
| **Data** (`data-*`) | Network I/O, tier routing, cache, batch dispatch. Country-bundled (1 skill = 1 country = all clients for that country). | Computing indicators, ranking, formatting Markdown | **none** — leaf nodes |
| **Analysis** (`analysis-*`) | Pure functions: input JSON → output JSON. RSI/MACD/BB, DCF, comps multiples, screener filter+score+rank, portfolio P&L, IC+GIP regime. | Network I/O, file fetch, sub-agent dispatch — **zero exceptions** | none |
| **Report** (`report-*`) | Orchestration, country routing (ticker suffix → which `data-{country}`), Markdown formatting. May delegate to `domain-teams:investing-team` / `domain-teams:docs-team`. | Re-implementing a multiple, hand-rolling RSI inline, calling yfinance directly | yes (cross-plugin via plugin-name path) |

### Cross-skill data passing

**Main agent + temp file** is the canonical pattern (NOT sub-agent
dispatch). The orchestrating `report-*` skill calls Bash to run
`data-X/scripts/pack.py > /tmp/data.json`, then Bash again to run
`analysis-Y/scripts/compute.py --in /tmp/data.json > /tmp/result.json`,
then formats. Same shape as the Cross-Plugin Delegation Contract
(pass paths, not content). Sub-agent dispatch is reserved for
autonomy-required work (`investing-team` Worker / Evaluator), not
layer-to-layer hand-off — subprocess+temp-file is deterministic,
debuggable, replayable, and round-trip lossless.

### Canonical client scripts (single copy, no sync)

The 5 country data skills were merged into one `data-markets` skill
(ADR-0009), so client scripts collapsed from N per-country copies to a
single canonical copy each, imported by the market-specific
`pack_{market}.py` modules that live in the same `scripts/` directory:

| File | Copies | Consumers |
|---|---|---|
| `yfinance_client.py` | 1 | `pack_us`, `pack_jp`, `pack_tw`, `pack_kr`, `pack_cn` |
| `fred_client.py` | 1 | `pack_us`, `pack_cn` |
| `nbs_client.py` | 1 | `pack_cn` |
| `akshare_client.py` | 1 | `pack_cn` |
| `ta_client.py` | canonical only | `analysis-technical` (no second consumer yet) |

Cache handling is likewise one shared `cache_util.py` in
`skills/data-markets/scripts/`, imported by every client in that same
skill directory — same-skill imports were always fine under the
Anthropic skill-self-containment convention; what changed is the
skill count (5 skills each needing a copy → 1 skill needing exactly
one). See ADR-0009 for the full rationale.

### What this prevents

- Mixed fetch+compute+format in a single skill (the v1.x lesson).
- Cross-skill orchestration via sub-agent dispatch (token cost +
  serialization-layer waste for pure-function compute).
- Duplication drift — there is exactly one copy of each client and of
  `cache_util.py`, so there is no second copy left to drift from (the
  MD5-sync CI guard this used to require is retired along with the
  duplication it guarded — ADR-0009).

### What this enables

- New skills follow the prefix convention (`data-*` / `analysis-*` /
  `report-*`) — placement is mechanical, not a judgement call.
- Layer 2 skills are pure compute → trivially testable with synthetic
  JSON fixtures (see `tests/analysis/`); no network mocks required.
- Country-bundled data layer hides tier-routing complexity from the
  analysis layer — `analysis-dcf` does not know whether
  `data-jp` used EDINET or yfinance.

**Pointer**: Full architectural details, alternatives considered,
slash-command rename map, and PR sequencing in
`docs/adr/0001-data-analysis-report-layers.md` (ADR-0001).

---

## 3. Derived practice — the pre-design probe

Before opening a design plan file, spend 5-30 minutes on any of these
that apply:

| Probe type | When to use |
|---|---|
| `curl` / `uv run` direct HTTP probe | Before committing to a new endpoint integration |
| Cross-country ticker smoke test | Before adding suffix-based source router |
| MCP handshake timeout probe | Before shipping MCP bootstrap strategy (did this in v1.14.0 P3 — caught the 60s cliff correctly; should do more like this) |
| `git log`+`grep` prior-art walk | Before designing a new skill — check what exists that can be reused |
| Read a competing/reference plugin's source | Before adopting an architecture pattern — Anthropic's knowledge-work-plugins + financial-services-plugins should have told us Cowork MCP sandboxing in v1.14.0 |

All probes are cheap relative to the cost of 1,300 LOC in the wrong
direction.

---

## 4. When the probe contradicts the plan

1. **Stop. Don't ship the original plan.** (Counter-example: v1.16.3
   shipped Commits 1-5 on the wrong hypothesis, then Commit 6
   corrected. Extra round trip could have been avoided.)
2. Update the plan file with the new data.
3. Re-check which commits still have value under the revised design.
   Not all of them will — but some will (v1.16.3 Commits 1 + 2 still
   shipped even after the pivot because the TWSE action + ta_client
   robustness are independently useful).
4. Document the pivot in the PR / ROADMAP with a "Lesson learned"
   paragraph. Over time the pattern of these paragraphs builds a
   personal heuristic library for what classes of claim need
   empirical verification.

---

## 5. When NOT to probe (don't over-apply)

Skip empirical probing when:

- The change is a pure refactor / code-movement (no new source or
  architecture claim involved).
- The claim is about a system whose contract is already known and
  stable (e.g. FRED CSV endpoint behavior — probed in v1.0.0, stable
  since).
- The probe itself would cost more than the expected loss from a
  failed hypothesis (rare — usually probes are cheap).

Use judgement. The rule is "probe when claiming behavior across a
boundary you haven't recently verified", not "probe everything".

---

## 6. References to incident records

Full retrospective notes live in commit bodies + ROADMAP.md entries:

- v1.14.0 retrospective — `investing-toolkit/ROADMAP.md` v1.16.1
  section + `docs/mcp-setup.md` top callout.
- v1.16.3 empirical pivot — `investing-toolkit/ROADMAP.md` v1.16.3
  section "Lesson learned" subsection + Commit 6 (36145f7) body.
