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

## 2. Derived practice — the pre-design probe

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

## 3. When the probe contradicts the plan

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

## 4. When NOT to probe (don't over-apply)

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

## 5. References to incident records

Full retrospective notes live in commit bodies + ROADMAP.md entries:

- v1.14.0 retrospective — `investing-toolkit/ROADMAP.md` v1.16.1
  section + `docs/mcp-setup.md` top callout.
- v1.16.3 empirical pivot — `investing-toolkit/ROADMAP.md` v1.16.3
  section "Lesson learned" subsection + Commit 6 (36145f7) body.
