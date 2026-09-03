# Investment-Analysis AI-Agent Projects — Prior-Art Survey

Research date: 2026-07-19. Method: focused research agent reading actual project
repos/docs (WebSearch + WebFetch), grounding-focused. Purpose: see how popular
open-source investment-analysis agent projects structure their pipeline and output,
and where a source-anchored longitudinal design differs.

## Bottom line

Almost all popular projects are **trading-signal bots** that emit a buy/hold/sell
decision, not a cited research document. Genuine mechanical source-grounding exists
in only a few (FinRobot, TradingAgents, OpenBB agents), and **none** does
verbatim-quote anchoring, per-number citation back to a filing line, or a maintained
multi-year per-company coverage file. **That triad is our differentiator.**

## Comparison

| Project (stars, 2026-07-19) | Pipeline | Output | Source-grounding | Horizon |
|---|---|---|---|---|
| virattt/ai-hedge-fund (~62k) | 13 investor personas + 4 analyst agents → Risk → PM | per-ticker signal + order | ❌ fetch-then-pass, no cite/verify | mixed |
| TauricResearch/TradingAgents (~93k) | analysts → Bull/Bear debate → trader → risk → PM | trade decision + analyst reports + memory | ✅ verified data snapshot, anti-fabrication guards | short-lean |
| **AI4Finance/FinRobot (~7.6k)** | orchestrator → data→analysis→model→synthesis→report + Bull/Bear/Judge | **multi-page equity research report + IC memo** | ✅ **strongest**: numbers code-computed, narratives LLM, provenance-tracked* | **long/fundamental** |
| AI4Finance/FinGPT (~21k) | finance-tuned LLMs (model library, not a report pipeline) | sentiment / forecast / NER | ❌ pure-LLM (RAG in one variant) | short |
| FinMem (~0.9k) / FinAgent (~75) | memory/reflection single-name bots | trade action | ❌ not documented, pure-LLM | short |
| OpenBB agents (~1.3k / ~355) | tool-calling loop / Workspace examples | Q&A / charts+tables + **citations**/PDF | ✅ tool-fetched figures; Workspace ships first-class citation | fundamental |
| CrewAI stock_analysis (~6k, archived) | analyst → research → 10-K/Q → advisor (sequential) | accreting Markdown report + reco | ⚠️ weak: LLM narration over filing text | fundamental/reco |
| **edinetdb/dexter-jp (~285, JP)** | single agentic loop: plan→tool→exec→validate | Markdown report: metric tables + narrative + conclusions | ⚠️ tool-grounded but **uncited**; EDINET/TDnet/J-Quants, DCF w/ JGB WACC | long/fundamental |

*FinRobot's granular provenance is README-stated, not fully verified — treat as
"designed for grounding," not confirmed.

## Common patterns

- **Pipeline convergence:** data-fetch → parallel analyst agents (fundamental /
  sentiment / news / technical) → (optional Bull-Bear debate) → risk → PM/decision.
  TradingAgents + FinRobot add the debate/judge stage; the rest fan-in flat.
  (Our shipped investing-team already resembles this.)
- **Output convergence:** dominant artifact is a *trade signal*, not a document.
  Only FinRobot / CrewAI / dexter-jp emit a prose research artifact.
- **Grounding is the exception:** most inject real fetched numbers but let the LLM
  narrate freely; mechanical grounding only in FinRobot / TradingAgents / OpenBB.
- **Citation almost absent:** only OpenBB Workspace ships first-class citations;
  none quotes verbatim or links a number to a filing line.
- **No longitudinal company memory:** memory modules are per-run trading state /
  portfolio memory — none maintains a multi-year per-company evidence file that
  accretes across filings.

## Gap = our differentiator (none of them does this)

1. **Verbatim-anchored quotes + per-number provenance** — every project at best
   fetches numbers; none pins a value or a management quote to the exact source
   filing location and forbids LLM invention. Our "values+quotes are mechanically
   anchored, never LLM-invented" rule has no equivalent here.
2. **Maintained multi-year per-company coverage file** — all are one-shot; none
   keeps a longitudinal, updated coverage document that survives across quarters.
3. **Human-confirm trust gate + primary-source discipline** — none has a
   ratify-before-trust gate separating machine-verified data from LLM narration,
   with refusal on unanchored claims.

**Our shipped Route B already leads the field on grounding** (values+coords
mechanical / LLM only labels / human confirm). FinRobot (same philosophy: numbers
code-computed, narratives LLM, provenance-tracked) is the closest study target;
dexter-jp is the only credible JP-market OSS analogue.

## Sources (repos read directly; EN unless marked)

github.com/virattt/ai-hedge-fund · github.com/TauricResearch/TradingAgents (arXiv:2412.20138) ·
github.com/AI4Finance-Foundation/FinRobot · /FinGPT ·
github.com/pipiku915/FinMem-LLM-StockTrading (arXiv:2311.13743) ·
github.com/DVampire/FinAgent (arXiv:2402.18485) ·
github.com/OpenBB-finance/agents-for-openbb · docs.openbb.co ·
github.com/crewAIInc/crewAI-examples (crews/stock_analysis) ·
**[JP]** github.com/edinetdb/dexter-jp · github.com/SakanaAI/EDINET-Bench.
